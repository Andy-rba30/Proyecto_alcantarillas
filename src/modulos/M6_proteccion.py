"""
M6_proteccion.py
=================
Fase 6 de la hoja de ruta: proteccion de ENTRADA y de SALIDA, y socavacion
local a la salida.

Hasta T-8 este modulo se titulaba «proteccion de entrada y salida» y solo
calculaba el d50 de Laushey para la salida (INF-5.1.13). Desde T-8 hace lo que
el titulo dice. Lo que entrega, y con que fuente cada cosa:

SALIDA (`proteccion_salida`)
    d50 de Laushey          Manual MTC, num. 4.1.1.3.7 c), ec. (49). Se
                            calcula y se imprime SIEMPRE.
    apron de HEC-14         Sec. 10.2: D50 por la Ec. (10.4) en funcion de Q,
                            D y TW, y clase, longitud, profundidad y ancho
                            por la Tabla 10.1.
    lo que RIGE             lo decide la regla [A]
                            'regla_espesor_longitud_proteccion_salida':
                            «envolvente_hec14» (el archivo): piedra = el
                            MAYOR de Laushey y de la Ec. (10.4); espesor y
                            longitud = el mayor de los adoptados y de los de
                            la Tabla 10.1 para esa piedra. «manual»: Laushey
                            y los adoptados ('espesor_proteccion_salida',
                            'longitud_proteccion_salida'), con HEC-14 al lado
                            y aviso donde pide mas. Donde HEC-14 no es
                            evaluable rige Laushey con lo adoptado, y se
                            avisa.
    Froude de la salida     HEC-14 num. 10.1.1: Fr_e = V / (g·ye)^0.5. Es un
                            parametro de diseño de esa fuente; el REGIMEN se
                            lee del tirante contra el critico.
    velocidad admisible     Manual MTC, Tabla Nº 11, por el tipo de terreno
                            del cauce receptor, que es un DATO DE SITIO por
                            punto (`tipo_terreno_receptor` y
                            `regimen_flujo_descarga`, datos externos). El
                            contraste INFORMA y no decide: la proteccion se
                            calcula y se mantiene siempre. Si la velocidad no
                            supera la admisible, se dice que el terreno la
                            resistiria segun la tabla y que suprimir la
                            proteccion queda sujeto a inspeccion de campo
                            (HDS-5 num. 5.3.2); si falta el dato, se avisa.
    filtro                  requisito DECLARADO: la Lámina Nº 05 del Manual lo
                            dibuja, HEC-14 lo pide, y EG-2013 511.08 fija lo
                            que el geotextil cumple segun el pasante del
                            tamiz N.º 200, que es dato del EMS.

ENTRADA (`proteccion_entrada`)
    velocidad en la boca    la que M4 ya resolvio: la del perfil de la lamina
                            bajo control de salida, la critica bajo control
                            de entrada (HDS-5 num. 3.1.3).
    revestimiento           criterio [A] 'tipo_proteccion_entrada', entre las
                            tres clases que el num. 4.1.1.3.7 c) enumera.
    que se protege          segun el tipo de embocadura (`EMBOCADURAS`). Hoy
                            el pipeline pasa la adoptada, cabezal recto; T-7a
                            pasara la suya por el mismo argumento.

SOCAVACION (`socavacion_salida`, `hoya_de_socavacion_hec14`)
    hoya local              HEC-14 Cap. 5 (el 5, no el 3 que cita la cadena
                            T: verificado sobre el ejemplar): Ec. (5.1) en
                            suelo no cohesivo y (5.2)/(5.3) en cohesivo.
                            Necesita el suelo del lecho, que es dato del EMS
                            (`material_lecho_salida`): sin el NO se estima.
    para el desplante       la profundidad DECLARADA
                            (`profundidad_socavacion_estimada_m`) gana si
                            viene; si no, la estimada. Es la funcion que el
                            cabezal por punto (T-7a) consumira.

POZA DE ENROCADO (`poza_de_enrocado_hec14`, desde VE-4g)
    donde el apron no llega HEC-14 Sec. 10.1: la Tabla 1.1 la da para el
                            marco y el conducto de mas de 60 in, que la Ec.
                            (10.4) no cubre. Profundidad por la Ec. (10.1)
                            con Co de la (10.2) o (10.3) (criterio [A]
                            'relacion_co_poza_enrocado_hec14'), longitud y
                            ancho de la Sec. 10.1 y velocidad a su salida
                            contra la admisible de la Tabla Nº 11. Se
                            reviste con la piedra que rige (Laushey); la
                            regla de la proteccion forma la envolvente con
                            ella. Varios barriles: ni el apron ni la poza.

LO QUE ESTE MODULO NO HACE, dicho para que no se lea de mas: no dimensiona
los disipadores internos de su Capitulo 7, ni el aliviadero escalonado de la Lámina Nº 04 del
Manual (la medida que el num. 4.1.1.3.7 c) da para REDUCIR la velocidad); no
digitaliza la Figura 10.3 (atenuacion de la velocidad con el TW sobre la
clave), no diseña el filtro granular (HEC 11 no esta en el repositorio de normas) y
no da dimensiones al revestimiento de la entrada, porque ninguna fuente de
normas/ las da. Cada uno tiene su ficha en `docs/decisiones_diferidas.md`.

LAS DOS FUENTES DEL TAMAÑO DE LA PIEDRA, Y CUAL RIGE (MAT-X6)
-------------------------------------------------------------
    Manual MTC, num. 4.1.1.3.7 c): d50 = V^2/(3.1*g). Funcion de UNA sola
        variable, la velocidad de salida.

    HDS-5 3a ed. (FHWA-HIF-12-026), Sec. 5.3.2 "Scour at Outlets", pag.
        impresa 5.11: remite el apron de enrocado a HEC-14 Sec. 10.2, que lo
        dimensiona en funcion de Q, D y TW.

Hasta T-8 se calculaba solo el primero, porque HEC-14 no estaba en normas/.
T-8 calculo los DOS y dejo rigiendo el del Manual, con el de HEC-14 al lado
como contraste. La segunda auditoria de T-8 midio lo que esa regla callaba: a
seccion llena y con TW = 0.4·D, `D50_HEC14 / d50_Laushey = 2.04·(D^2.5/Q)^
(2/3)`, mayor que 1 siempre que Q/D^2.5 < 2.9, de modo que HEC-14 pide mas
piedra que Laushey justo en la descarga lenta y caudalosa. EL DUEÑO DECIDIO
EL 2026-11-12 QUE RIGE LA ENVOLVENTE: la piedra es la MAYOR de las dos, y el
espesor y la longitud, los mayores de lo adoptado y de la Tabla 10.1 para esa
piedra. No hay contradiccion que resolver --son dos metodos empiricos con
variables distintas--, y la envolvente es el lado conservador de los dos. La
regla anterior queda como «manual», barrible, y reproduce los numeros de
antes. El d50 de Laushey se sigue publicando siempre, en
`ProteccionSalida.d50_laushey` y en el paso 6.1.

Y HAY UNA RAZON TECNICA PARA CALCULAR LOS DOS, que es lectura del proyecto
y no de ninguna de las fuentes: la ec. (49) dimensiona con la velocidad sola
(d50 = V^2/(3.1·9.8) = 0.0329·V^2), como las dos relaciones del Apendice D de
HEC-14 que la fuente NO recomienda «because they do not consider tailwater
effects» (D.2 de Berry, 0.0413·V^2; D.3 de Searcy, 0.0214·V^2 con S = 2.65;
cita HEC14.D#SOLO_VELOCIDAD). HEC-14 no nombra a Laushey; el coeficiente de
la ec. (49) cae entre los de esas dos. La que HEC-14 retiene, Fletcher y
Grace, es la Ec. (10.4).

Excepciones
-----------
Las funciones PUBLICAS de pieza (`apron_hec14`, `hoya_de_socavacion_hec14`,
`velocidad_admisible_del_cauce`) lanzan la excepcion que corresponde:
`DatoInvalidoError` (un dato que no puede ser), `DatoFaltanteError` (falta un
dato del EMS), `MetodoNoEvaluableError` (la ecuacion no cubre el caso: marco,
TW sobre la clave, conducto de mas de 60 in, caida mayor que la tabla,
indice de plasticidad fuera de rango). Las tres funciones de FASE
(`proteccion_salida`, `proteccion_entrada`, `socavacion_salida`) recogen las
de METODO y de dato FALTANTE y las convierten en AVISO, porque lo que falta o
no se puede evaluar en una pieza no debe dejar al punto sin las demas: un
punto sin lecho declarado conserva su d50, y un resultado hidraulico sin TW
o sin tirante critico pierde el apron de HEC-14 y no el d50 de Laushey. Un
dato INVALIDO no se recoge.

QUE VELOCIDAD ENTRA (regla de doble n, Sec. 4.1)
-------------------------------------------------
La de SALIDA de HDS-5 3.1.6 que M4 emite (`ResultadoHidraulico.V_salida`),
con su procedencia. Bajo control de entrada es `V_erosion`, la rama de n
MINIMO -- la estimacion ALTA --, que desde VE-2 es la velocidad del tirante
normal RESUELTO con n_min (Q_celda / A(y_n de n_min); HEC-14 num. 3.2.2);
bajo control de salida y con el barril horizontal (S = 0, donde no hay
tirante normal) es Q entre el area al tirante de salida. El Froude se forma
con ESA velocidad y con el area que la continuidad le asigna, Q_celda / V,
que bajo control de entrada es justamente el area del tirante de n_min.

DOS CASOS EN QUE ESA VELOCIDAD QUEDA CORTA, y se AVISAN sin tocar el numero,
que es de M4: (1) control de salida con el TW bajo el critico: el tirante
real en el borde es menor que el critico (HEC-14 num. 3.1.3) y la velocidad,
mayor; (2) control de salida en la banda en que el tirante normal de n maximo
es subcritico y el de n minimo seria supercritico: la estimacion alta de la
regla de doble n es `V_erosion` y no la critica. En el primero, ademas, el
contraste con la Tabla Nº 11 no concluye.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple

from scipy.optimize import brentq

from src import criterios_adoptados as ca
from src.constantes_fisicas import G, RHO_AGUA
from src.constantes_normativas import (
    G_LAUSHEY, GEOTEXTIL_EROSION_CLASE, GEOTEXTIL_EROSION_IP_COHESIVO,
    GEOTEXTIL_EROSION_T511_06, GEOTEXTIL_EROSION_TAA_COHESIVO_MM,
    HEC14_APRON_ABOCINADO_POR_LONGITUD, HEC14_APRON_ALTURA_MAX_M,
    HEC14_APRON_GRAVEDAD_ESPECIFICA_PIEDRA,
    HEC14_APRON_ANCHO_EN_LA_BOCA_EN_D, HEC14_APRON_COEFICIENTE,
    HEC14_APRON_EXPONENTE, HEC14_APRON_TW_SOBRE_D_MAX,
    HEC14_APRON_TW_SOBRE_D_MIN, HEC14_EXPONENTE_LONGITUD_DEL_CAUDAL_ADIMENSIONAL,
    HEC14_SOCAVACION_CH, HEC14_SOCAVACION_COHESIVO, HEC14_SOCAVACION_CS,
    HEC14_SOCAVACION_EXPONENTE_SIGMA, HEC14_SOCAVACION_FRACCION_LS_DEL_MAXIMO,
    HEC14_SOCAVACION_IP_MAX, HEC14_SOCAVACION_IP_MIN,
    HEC14_SOCAVACION_NO_COHESIVO, HEC14_SOCAVACION_T_MINIMO_MIN,
    HEC14_SOCAVACION_T_REFERENCIA_MIN, HEC14_TABLA_10_1, HEC14_TAU_C_ALFA_U_SI,
    HEC14_TAU_C_ANGULO_BASE_GRADOS, HEC14_TAU_C_COEFICIENTE,
    HEC14_TAU_C_GRADOS_POR_IP, LAUSHEY_K, HEC14_ESPESOR_MIN_EN_D50,
    HEC14_POZA_ABOCINADO_POR_LONGITUD, HEC14_POZA_CO,
    HEC14_POZA_COEFICIENTE_HS, HEC14_POZA_D50_SOBRE_YE_MIN,
    HEC14_POZA_ESPESOR_TALUD_EN_D50, HEC14_POZA_EXPONENTE_D50,
    HEC14_POZA_FROUDE_MAX, HEC14_POZA_HS_SOBRE_D50_MIN, HEC14_POZA_LB_EN_HS,
    HEC14_POZA_LB_MIN_EN_WO, HEC14_POZA_LS_EN_HS, HEC14_POZA_LS_MIN_EN_WO,
    HEC14_POZA_TALUD_LATERAL_Z, HEC14_POZA_TW_SOBRE_YE_ALTO,
    HEC14_POZA_TW_SOBRE_YE_BAJO,
    HEC14_POZA_TW_SOBRE_YO_SIN_PROTECCION_ADICIONAL,
    HEC14_CAIDA_APROXIMACION_EN_YC, HEC14_CAIDA_BLOQUE_ALTO_EN_YC,
    HEC14_CAIDA_BLOQUE_ANCHO_EN_YC, HEC14_CAIDA_HO_MAX_M,
    HEC14_CAIDA_HO_SOBRE_YC_MAX, HEC14_CAIDA_HO_SOBRE_YC_MIN,
    HEC14_CAIDA_L2_EN_YC, HEC14_CAIDA_L3_MIN_EN_YC, HEC14_CAIDA_LS_DENOMINADOR,
    HEC14_CAIDA_LS_NUMERADOR, HEC14_CAIDA_L_ORDENADA, HEC14_CAIDA_L_PENDIENTE,
    HEC14_CAIDA_L_RADICANDO, HEC14_CAIDA_MURO_SOBRE_TW_EN_YC,
    HEC14_CAIDA_UMBRAL_EN_YC, HEC14_CAIDA_WO_MIN_EN_YC, HEC14_CAIDA_Y3_EN_YC,
    HEC14_EC_10_6_COEFICIENTE, HEC14_FIGURA_10_3,
    REGIMENES_DE_FLUJO_T11, TERRENO_T11_ROTULO, V_MAX_NO_REVESTIDOS)
from src.modelos import (
    CIFRAS_FACTOR, CIFRAS_FINA, CIFRAS_MAGNITUD, ApronHEC14, ClaseHEC14,
    ControlGobernante, TIPO_LECHO_COHESIVO,
    DatoFaltanteError, DatoInvalidoError, EleccionDeProyecto,
    EstructuraDeCaida, FroudeSalida,
    HoyaDeSocavacion, LimiteNumericoError, Magnitud, MaterialLecho,
    MetodoNoEvaluableError, MOTIVO_METODO_NO_EVALUABLE_HEC14,
    ORIGEN_SOCAVACION_DECLARADA,
    ORIGEN_SOCAVACION_ESTIMADA, ORIGEN_SOCAVACION_SIN_DATO, PasoDeMemoria,
    PozaDeEnrocado, ProteccionTWAlto,
    ProteccionEntrada, ProteccionSalida, RequisitoDeFiltro,
    ResultadoHidraulico, Seccion, SeccionCircular, SeccionRectangular,
    SocavacionSalida, TIPO_LECHO_NO_COHESIVO, TIPOS_DE_LECHO, TipoDeVeredicto,
    Umbral, Veredicto, VelocidadAdmisible, paso)
from src.dominios import PORCENTAJE_POR_UNIDAD
from src.tolerancias import TOL_UMBRAL_NORMATIVO

NUMERAL_LAUSHEY = "4.1.1.3.7 c)"

CRITERIO_ESPESOR = "espesor_proteccion_salida"
CRITERIO_LONGITUD = "longitud_proteccion_salida"
CRITERIO_REVESTIMIENTO_ENTRADA = "tipo_proteccion_entrada"
CRITERIO_DURACION_PICO = "duracion_caudal_pico_socavacion_min"
CRITERIO_LECTURA_TABLAS = "lectura_coeficientes_socavacion_hec14"
CRITERIO_REGLA = "regla_espesor_longitud_proteccion_salida"
REGLA_MANUAL = "manual"
REGLA_ENVOLVENTE = "envolvente_hec14"
CRITERIO_REFERENCIA = "referencia_profundidad_socavacion"
REFERENCIA_FONDO = "fondo_del_cauce_receptor"
REFERENCIA_SOLERA = "solera_de_salida"
LECTURA_ENVOLVENTE = "envolvente_de_filas_vecinas"
LECTURA_INTERPOLADA = "interpolacion_lineal"

# Los datos externos que este modulo nombra en sus avisos: quien los carga y
# valida es `servicio` (CLAVES_EXTERNAS); aqui van solo los nombres, para que
# un aviso diga exactamente que hay que declarar.
DATO_TERRENO_RECEPTOR = "tipo_terreno_receptor"
DATO_TERRENO_ENTRADA = "tipo_terreno_entrada"
DATO_REGIMEN_FLUJO = "regimen_flujo_descarga"
DATO_MATERIAL_LECHO = "material_lecho_salida"
DATO_DURACION_PICO = "duracion_caudal_pico_min"
DATO_SOCAVACION_DECLARADA = "profundidad_socavacion_estimada_m"

DONDE_SALIDA = "salida"
DONDE_ENTRADA = "entrada"

ADVERTENCIA_NO_ES_DISENO = (
    "d50 no es un diseño de enrocado: falta la granulometria completa "
    f"(Sec. 6 de la hoja de ruta, {NUMERAL_LAUSHEY})"
)
ADVERTENCIA_FALTA_FILTRO = (
    "El filtro no se dimensiona: se declara como requisito. Sin filtro el "
    "enrocado se socava por debajo y falla (Sec. 6 de la hoja de ruta; "
    "Lámina Nº 05 del Manual; HEC-14 Sec. 10.2; EG-2013 num. 511.08)"
)
ADVERTENCIA_ALCANCE_HDS5 = (
    "Alcance: el d50 que rige sale del Manual MTC (num. 4.1.1.3.7 c), funcion "
    "solo de V. HDS-5 3a ed. (FHWA-HIF-12-026), Sec. 5.3.2 'Scour at "
    "Outlets', pag. 5.11, remite el apron de enrocado a HEC-14 Sec. 10.2, "
    "que lo dimensiona en funcion de Q, D y TW: se calcula AL LADO, como "
    "contraste, y la corrida avisa cuando pide mas que lo adoptado. La "
    "geometria de la proteccion se cierra en el expediente tecnico"
)
# La tercera advertencia cuando RIGE LA ENVOLVENTE (decision del dueño del
# 2026-11-12): decir «el d50 que rige sale del Manual» seria falso justo
# donde HEC-14 pide mas piedra.
ADVERTENCIA_ALCANCE_ENVOLVENTE = (
    "Alcance: rige la ENVOLVENTE de las dos fuentes. El Manual MTC (num. "
    "4.1.1.3.7 c)) da el d50 de Laushey, funcion solo de V; HDS-5 3a ed. "
    "(FHWA-HIF-12-026), Sec. 5.3.2 'Scour at Outlets', pag. 5.11, remite el "
    "apron de enrocado a HEC-14 Sec. 10.2, que lo dimensiona en funcion de "
    "Q, D y TW. La piedra es la mayor de las dos, y el espesor y la longitud "
    "los mayores de lo adoptado y de la Tabla 10.1 de HEC-14. La geometria "
    "de la proteccion se cierra en el expediente tecnico"
)
# --- VE-4g --- La tercera advertencia cuando la POZA de enrocado de HEC-14
# Sec. 10.1 entra donde el apron no llega y rige la envolvente con ella.
ADVERTENCIA_ALCANCE_POZA = (
    "Alcance: rige la ENVOLVENTE del Manual MTC (num. 4.1.1.3.7 c), d50 de "
    "Laushey) y de la POZA DE ENROCADO de HEC-14 Sec. 10.1, que la Tabla 1.1 "
    "de esa fuente da donde el apron de la Sec. 10.2 no llega (marco o "
    "conducto de mas de 60 in). La piedra es la mayor de las dos, y el "
    "espesor y la longitud los mayores de lo adoptado y de la poza; la "
    "profundidad, el ancho y la velocidad a su salida estan en los pasos "
    "6.5p y 6.6p. La geometria de la proteccion se cierra en el expediente "
    "tecnico"
)
ADVERTENCIAS_PROTECCION_SALIDA: Tuple[str, ...] = (
    ADVERTENCIA_NO_ES_DISENO,
    ADVERTENCIA_FALTA_FILTRO,
    ADVERTENCIA_ALCANCE_HDS5,
)
ADVERTENCIAS_PROTECCION_SALIDA_ENVOLVENTE: Tuple[str, ...] = (
    ADVERTENCIA_NO_ES_DISENO,
    ADVERTENCIA_FALTA_FILTRO,
    ADVERTENCIA_ALCANCE_ENVOLVENTE,
)
ADVERTENCIAS_PROTECCION_SALIDA_POZA: Tuple[str, ...] = (
    ADVERTENCIA_NO_ES_DISENO,
    ADVERTENCIA_FALTA_FILTRO,
    ADVERTENCIA_ALCANCE_POZA,
)

# ---------------------------------------------------------------------------
# Tipos de embocadura que la proteccion de entrada distingue
# ---------------------------------------------------------------------------
# La asignacion «que se protege segun la embocadura» es LECTURA DEL PROYECTO
# sobre la enumeracion del HDS-5 num. 5.3.1 (revestimiento del talud y del
# cauce, cabezal, aleros, dentellon), que la fuente da sin repartir. Desde
# T-7a el pipeline pasa la de cada punto por el mismo argumento
# (`M9.embocadura_del_punto`); las dos primeras claves son tambien el
# conjunto cerrado del criterio 'embocadura_cabezal'.
EMBOCADURA_CABEZAL_RECTO = "cabezal_recto"
EMBOCADURA_CABEZAL_CON_ALEROS = "cabezal_con_aleros"
EMBOCADURA_PROYECTANTE = "proyectante"
EMBOCADURA_A_BISEL = "a_bisel"
_CAUCE_Y_UNA = ("cauce de aproximacion, del pie del cabezal hacia aguas "
                "arriba, con su uña o dentellon al borde")
EMBOCADURAS: Dict[str, Tuple[str, ...]] = {
    EMBOCADURA_CABEZAL_RECTO: (
        _CAUCE_Y_UNA,
        "talud del terraplen a los dos lados del cabezal, donde el muro "
        "recto no lo contiene"),
    EMBOCADURA_CABEZAL_CON_ALEROS: (
        "piso entre los aleros (zampeado), con su uña o dentellon al borde",
        "talud del terraplen detras de la punta de los aleros"),
    EMBOCADURA_PROYECTANTE: (
        _CAUCE_Y_UNA,
        "talud del terraplen alrededor del tubo, que sin cabezal queda "
        "expuesto en todo el contorno de la boca"),
    EMBOCADURA_A_BISEL: (
        _CAUCE_Y_UNA,
        "talud del terraplen alrededor de la boca biselada, revestido hasta "
        "por encima de la clave"),
}


# ---------------------------------------------------------------------------
# Guardias de segunda linea (forma MAT-D13: en positivo y negada)
# ---------------------------------------------------------------------------

def _es_numero_finito(valor: object) -> bool:
    return (not isinstance(valor, bool) and isinstance(valor, (int, float))
            and math.isfinite(valor))


def _exigir_positivo(nombre: str, valor: float, de_donde: str) -> None:
    """NaN, inf, cero y negativo caen todos: `not (finito y > 0)`."""
    if not (_es_numero_finito(valor) and valor > 0):
        raise DatoInvalidoError(
            nombre, valor=valor,
            motivo=f"tiene que ser un numero finito y positivo ({de_donde})")


def _exigir_no_negativo(nombre: str, valor: float, de_donde: str) -> None:
    if not (_es_numero_finito(valor) and valor >= 0):
        raise DatoInvalidoError(
            nombre, valor=valor,
            motivo=f"tiene que ser un numero finito y no negativo ({de_donde})")


def _literal(cita_id: str) -> str:
    """
    El texto literal de una cita, LEIDO DEL REGISTRO: lo que un aviso
    entrecomilla no se transcribe por segunda vez (CLAUDE.md, «Ningún texto
    literal se transcribe dos veces»).
    """
    from src.normativa import registro as _registro    # perezoso: ciclo
    return _registro.construir().cita(cita_id).texto_literal.texto


def _lectura(cita_id: str) -> str:
    """
    El texto de la `Interpretacion` que cuelga de una cita, LEIDO DEL
    REGISTRO: lo que el proyecto lee en la fuente se imprime en la cara del
    proyecto (`nota_del_proyecto`) con las mismas palabras con que el
    registro lo declara, y no se redacta por segunda vez en el modulo.
    """
    from src.normativa import registro as _registro    # perezoso: ciclo
    return ("LECTURA DEL PROYECTO, no texto de la fuente. "
            + _registro.construir().cita(cita_id).interpretacion.texto)


def _exigir_texto_de(nombre: str, valor: object, admitidos, motivo: str) -> None:
    """
    Guardia de segunda linea de una clave de catalogo (H7 de la segunda
    auditoria de T-8): `valor in dict` con una lista levanta `TypeError`,
    que no desciende de `ErrorProyecto`. Primero el tipo, despues el juego.
    """
    if not (isinstance(valor, str) and valor in admitidos):
        raise DatoInvalidoError(nombre, valor=valor, motivo=motivo)


def _exigir_velocidad(V: Magnitud, funcion: str) -> None:
    if not isinstance(V, Magnitud):
        raise TypeError(
            f"{funcion} espera la velocidad como Magnitud con procedencia "
            f"(ResultadoHidraulico.V_salida), no {V!r}: un float suelto es "
            "una velocidad que la memoria no puede rastrear")
    _exigir_positivo("V", V.valor, "velocidad del flujo, m/s")


# ---------------------------------------------------------------------------
# d50 - Laushey (num. 4.1.1.3.7 c)
# ---------------------------------------------------------------------------

def laushey_d50(*, V: float) -> float:
    """d50 = V^2 / (LAUSHEY_K * G_LAUSHEY), sistema metrico (num. 4.1.1.3.7 c)."""
    return V ** 2 / (LAUSHEY_K * G_LAUSHEY)


def _paso_laushey(V: Magnitud, d50: float, espesor: float,
                  mult_espesor: float) -> PasoDeMemoria:
    return paso(
        "F6.LAUSHEY",
        codigo="6.1",
        que="Diametro medio del enrocado de proteccion a la salida",
        formula="d50 = V^2 / (3.1 * g)",
        formula_cita_id="MC_HHD.4.1.1.3.7c",
        citas_textuales=("MC_HHD.4.1.1.3.7c", "HEC14.D#SOLO_VELOCIDAD"),
        # AQUI VIAJO `DIS-HR-G-LAUSHEY` MIENTRAS ESTUVO VIVA, declarada
        # por su id porque el cruce por cita pasa de largo por un sufijo
        # (la discrepancia habla de `MC_HHD.4.1.1.3.7c#G`, el ancla del
        # SIMBOLO g, y este paso cita el numeral). I2 la paso a RESUELTA
        # -- la v8 ya llevaba la atribucion corregida y el registro
        # estaba atras -- y una resuelta no se declara: la guardia de
        # `paso()` lo impide. La via del campo `discrepancias` sigue
        # siendo la de las que hablan de un NUMERO y no de un texto.
        sustitucion=(
            # LA PROCEDENCIA VIENE CON EL NUMERO (EXT-3): la escribe M4
            # al elegir el area de HDS-5 3.1.6, y aqui se copia tal cual
            # bajo el simbolo de la formula. Un texto fijo aqui volveria a
            # afirmar de donde sale V sin poder desmentirse.
            Magnitud("V", V.valor, "m/s",
                     f"{V.procedencia}. Es la velocidad a la SALIDA, que "
                     "es la que socava: d50 crece con el CUADRADO de V",
                     cifras=CIFRAS_MAGNITUD),
            # LA PROCEDENCIA DICE DE DONDE SALE EL NUMERO; la historia de
            # POR QUE NO SALE DE DONDE LA HOJA DE RUTA DECIA vive en
            # `DIS-HR-G-LAUSHEY` (resuelta en I2: la v8 corrigio la
            # atribucion) y en el comentario de `G_LAUSHEY`. Estaba
            # escrita aqui entera, y era la tercera copia del mismo
            # argumento; una de las tres tiene que ser la fuente, y es la
            # del registro: es la unica enumerable.
            Magnitud("g", G_LAUSHEY, "m/s2",
                     "`constantes_normativas.G_LAUSHEY`, que el Manual de "
                     "Hidrologia escribe en sus num. 3.12.5 (pag. impresa "
                     "63) y 4.1.1.5.4 b.2.4) (pag. impresa 111)")),
        resultado=Magnitud("d50", d50, "m",
                           "diametro medio de la piedra",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="dimensionamiento, no verificacion: la fuente no "
                        "pone umbral al d50"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="espesor de la proteccion",
            valor=f"{espesor:.3f} m",
            entre=(f"multiplicador {mult_espesor} de d50",),
            de_donde=f"el criterio adoptado '{CRITERIO_ESPESOR}' [A]",
            por_que="ni el Manual de Hidrologia ni el de Puentes fijan el "
                    "espesor del enrocado: es practica corriente, y por "
                    "eso el valor es una adopcion declarada y no una cita",
            clave_criterio=CRITERIO_ESPESOR),),
        nota_del_proyecto=(
            "ESTO NO ES UN DISEÑO DE ENROCADO. La Sec. 6 de la hoja de "
            "ruta dice expresamente que faltan la granulometria completa "
            "y el FILTRO, y que sin filtro el enrocado se socava por "
            "debajo y falla. El HDS-5 dimensiona el apron por HEC-14, que "
            "es otro procedimiento: desde T-8 se calcula al lado (pasos "
            "6.5 y 6.6). LECTURA DEL PROYECTO: la ec. (49) dimensiona con la "
            "velocidad sola (d50 = 0.0329·V^2), como las dos relaciones del "
            "Apendice D de HEC-14 que esa fuente no recomienda por no "
            "considerar el tirante del receptor (Berry, 0.0413·V^2; Searcy, "
            "0.0214·V^2 con S = 2.65). HEC-14 no nombra a Laushey."),
    )


def _paso_geometria_adoptada(d50: float, mult_espesor: float, espesor: float,
                             longitud: float, regla: str) -> PasoDeMemoria:
    """El espesor como formula sustituida y la longitud como eleccion."""
    return paso(
        "F6.GEOMETRIA_ADOPTADA",
        codigo="6.2",
        que="Espesor y longitud de la proteccion de salida adoptados",
        formula="e = k * d50",
        citas_textuales=("MC_HHD.4.1.1.3.7c#REVESTIMIENTOS",),
        sustitucion=(
            Magnitud("k", mult_espesor, "-",
                     f"criterio adoptado '{CRITERIO_ESPESOR}' [A]: multiplo "
                     "del d50", cifras=CIFRAS_FACTOR),
            Magnitud("d50", d50, "m", "paso 6.1 (Laushey)",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("e", espesor, "m",
                           "espesor de la capa de proteccion",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="adopcion declarada: ninguna fuente peruana de "
                        "normas/ fija el espesor ni la longitud"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="longitud de la proteccion aguas abajo de la salida",
            valor=f"{longitud:.3f} m",
            entre=tuple(f"{x:g} m" for x in
                        ca.CRITERIOS[CRITERIO_LONGITUD].sensibilidad),
            de_donde=f"el criterio adoptado '{CRITERIO_LONGITUD}' [A]",
            por_que="el Manual pide extender el revestimiento hasta donde la "
                    "socavacion local no incida y no da la distancia: se "
                    "adopta y se contrasta con el apron de HEC-14 (paso 6.6) "
                    "y, si el lecho esta declarado, con la longitud de la "
                    "hoya de socavacion",
            clave_criterio=CRITERIO_LONGITUD),
            EleccionDeProyecto(
            que_se_adopto="regla de la piedra, el espesor y la longitud "
                          "que rigen",
            valor=regla,
            entre=tuple(ca.CRITERIOS[CRITERIO_REGLA].sensibilidad),
            de_donde=f"el criterio adoptado '{CRITERIO_REGLA}' [A]",
            por_que="con «manual» rigen el d50 de Laushey y el espesor y "
                    "la longitud de este paso; con «envolvente_hec14», en "
                    "cada magnitud el mayor de eso y de HEC-14, la piedra "
                    "incluida (paso 6.6c). La decision es del dueño del "
                    "proyecto",
            clave_criterio=CRITERIO_REGLA),),
    )


# ---------------------------------------------------------------------------
# Froude a la salida (HEC-14 num. 10.1.1)
# ---------------------------------------------------------------------------

def flujo_supercritico(y: Optional[float], y_critico: Optional[float]
                       ) -> Optional[bool]:
    """
    EL REGIMEN DEL FLUJO, con UNA sola regla para todo M6: supercritico si el
    tirante queda bajo el critico, y < y_c. `None` si falta cualquiera de los
    dos (un resultado armado sin pasar por M4): no se adivina.

    Lo usan el Froude de la salida y el apron de HEC-14 (Ec. 10.5, «whenever
    the flow is supercritical in the culvert») con el MISMO tirante, el de
    salida que M4 publico, para que el JSON no lleve dos booleanos que se
    contradigan (hallazgo 2 de la auditoria de T-8). El Froude con el tirante
    equivalente de HEC-14 NO sirve para esto: la fuente lo define «to permit
    use of the same design relationships for rectangular and circular
    culverts» (pag. impresa 10-2), no para clasificar el regimen, y en un tubo
    ye = (A/2)^0.5 no es el tirante hidraulico A/T.
    """
    if y is None or y_critico is None:
        return None
    return y < y_critico - TOL_UMBRAL_NORMATIVO


def froude_salida(*, V: Magnitud, Q_celda: float, seccion: Seccion,
                  y_salida: Optional[float] = None,
                  y_critico: Optional[float] = None) -> FroudeSalida:
    """
    Fr_e = V / (g·ye)^0.5 con el tirante EQUIVALENTE de HEC-14 num. 10.1.1
    (pag. impresa 10-2): ye = yo en un marco, ye = (A/2)^0.5 en un tubo.

    ES UN PARAMETRO DE DISEÑO DE HEC-14, NO UN RETRATO DEL REGIMEN. La fuente
    define ye para usar las mismas relaciones de diseño en las dos formas, y
    con el clasifica sus disipadores (Tabla 1.1, columna «Froude Number»). El
    REGIMEN se lee aparte, del tirante de salida contra el critico
    (`flujo_supercritico`), y es el mismo que el apron usa para la Ec. 10.5.

    `V` es la velocidad de SALIDA de HDS-5 3.1.6 y `A` el area que la
    continuidad le asigna, A = Q_celda / V (HEC-14 Cap. 3). NO se usa el
    tirante de `y_salida`: bajo control de entrada `V` es la rama de n minimo
    y, desde VE-2, la de SU tirante normal, de modo que A = Q_celda / V es el
    area de ese tirante (hasta VE-2 era la rama de n minimo sobre la geometria
    de n maximo, y la continuidad era la unica forma de darle un area); con
    el area de continuidad el numero es el de la velocidad que de verdad
    entra a la proteccion, del lado ALTO. `y_salida` (el tirante a la salida
    que M4 publica: bajo control de entrada, el normal de REGISTRO, n_max) y
    `y_critico` sirven para el regimen y para decir si la salida va a
    seccion llena; no entran en la formula.
    """
    _exigir_velocidad(V, "froude_salida")
    _exigir_positivo("Q_celda", Q_celda, "caudal de un barril, m3/s")
    A = Q_celda / V.valor
    if isinstance(seccion, SeccionRectangular):
        ye = A / seccion.B
        formula_ye = "ye = yo = A / B"
        forma_ye = Magnitud("B", seccion.B, "m", "ancho interior de la celda",
                            cifras=CIFRAS_MAGNITUD)
    else:
        ye = math.sqrt(A / 2)
        formula_ye = "ye = (A / 2)^0.5"
        forma_ye = None
    Fr = V.valor / math.sqrt(G * ye)
    llena = (y_salida is not None
             and not y_salida < seccion.altura - TOL_UMBRAL_NORMATIVO)
    supercritico = flujo_supercritico(y_salida, y_critico)
    if supercritico is None:
        regimen = ("regimen no determinado: falta el tirante de salida o el "
                   "critico. Fr_e es el parametro de HEC-14 y no lo indica")
    elif supercritico:
        regimen = (f"supercritico: el tirante de salida ({y_salida:.3f} m) "
                   f"queda bajo el critico ({y_critico:.3f} m). Fr_e es el "
                   "parametro de diseño de HEC-14, no el que clasifica el "
                   "regimen")
    else:
        regimen = (f"subcritico o critico: el tirante de salida "
                   f"({y_salida:.3f} m) no queda bajo el critico "
                   f"({y_critico:.3f} m). Fr_e es el parametro de diseño de "
                   "HEC-14, no el que clasifica el regimen")
    if llena:
        regimen += (". La seccion de salida va LLENA: el numero es el "
                    "parametro de descarga de HEC-14, no un regimen de "
                    "lamina libre")
    sustitucion: List[Magnitud] = [
        Magnitud("V", V.valor, "m/s", V.procedencia, cifras=CIFRAS_MAGNITUD),
        Magnitud("A", A, "m2",
                 "area que la continuidad asigna a esa velocidad, A = "
                 f"Q_celda / V con Q_celda = {Q_celda:.{CIFRAS_FINA}f} m3/s "
                 "(Q = A·V, HEC-14 Cap. 3)",
                 cifras=CIFRAS_FINA)]
    if forma_ye is not None:
        sustitucion.append(forma_ye)
    sustitucion += [
        Magnitud("ye", ye, "m", f"tirante equivalente de HEC-14: {formula_ye}",
                 cifras=CIFRAS_FINA),
        Magnitud("g", G, "m/s2", "`constantes_fisicas.G`, el 9.81 que HEC-14 "
                 "escribe; no es el 9.8 de Laushey", cifras=CIFRAS_FACTOR)]
    return FroudeSalida(
        Fr=Fr, V=V.valor, A=A, y_equivalente=ye, supercritico=supercritico,
        seccion_llena=llena,
        paso=paso(
            "F6.FROUDE",
            codigo="6.3",
            que="Numero de Froude de HEC-14 a la salida del conducto "
                "(parametro de diseño de sus disipadores)",
            formula=f"Fr_e = V / (g * ye)^0.5,  {formula_ye}",
            formula_cita_id="HEC14.10.1.1#YE",
            citas_textuales=("HEC14.10.1.1#YE", "HEC14.3#CONTINUIDAD"),
            sustitucion=tuple(sustitucion),
            resultado=Magnitud("Fr_e", Fr, "-",
                               "Froude con el tirante equivalente de HEC-14",
                               cifras=CIFRAS_MAGNITUD),
            veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                                explicacion=regimen)))


# ---------------------------------------------------------------------------
# Velocidad admisible del cauce (Manual MTC, Tabla Nº 11)
# ---------------------------------------------------------------------------

def velocidad_admisible_del_cauce(*, V: Magnitud, tipo_terreno: str,
                                  regimen_flujo: str,
                                  donde: str = DONDE_SALIDA,
                                  cota_inferior: bool = False
                                  ) -> VelocidadAdmisible:
    """
    Compara la velocidad del flujo con la maxima admisible del terreno, de
    la Tabla Nº 11 del Manual (num. 4.1.1.3.6, pag. impresa 77).

    El Manual exige limitar la velocidad de SALIDA para no socavar el cauce
    aguas abajo y presenta la tabla a continuacion. Aplicarla a la ENTRADA
    (`donde="entrada"`) es extension del proyecto sobre la recomendacion del
    num. 4.1.1.3.7 c), que nombra la entrada junto a la salida: el paso lo
    declara en su `aplicacion`.

    `tipo_terreno` y `regimen_flujo` son datos de SITIO: una clave de fila y
    una columna de la tabla. No tienen valor por defecto y no se deducen.

    EL CONTRASTE INFORMA, NO DECIDE (decision del dueño del 2026-11-12).
    Superar la admisible no es un incumplimiento del diseño --el veredicto
    es INDICADOR (aviso)-- y NO superarla no suprime la proteccion: dice que
    el terreno la resistiria segun la tabla. Que «alta», la palabra del num.
    4.1.1.3.7 c), sea «mayor que la Tabla Nº 11» es lectura del proyecto, y
    el paso la imprime como tal.

    `cota_inferior` (H2 de la segunda auditoria): la velocidad que se compara
    es MENOR que la real --control de salida con el TW bajo el critico, donde
    las Figuras 3.3 y 3.4 de HEC-14 no dieron el tirante de borde y M4 se
    quedo en el critico (`ResultadoHidraulico.V_salida_cota_inferior`; desde
    el cierre de T8-08, solo ahi)--. Si aun asi supera la admisible, el
    contraste vale; si no la supera, NO CONCLUYE: el resultado lleva
    `concluyente=False` y el veredicto es INDICADOR.
    """
    _exigir_velocidad(V, "velocidad_admisible_del_cauce")
    _exigir_texto_de("donde", donde, (DONDE_SALIDA, DONDE_ENTRADA),
                     f"es '{DONDE_SALIDA}' o '{DONDE_ENTRADA}'")
    dato = DATO_TERRENO_RECEPTOR if donde == DONDE_SALIDA else DATO_TERRENO_ENTRADA
    _exigir_texto_de(dato, tipo_terreno, V_MAX_NO_REVESTIDOS,
                     "no es una fila de la Tabla Nº 11 del Manual. Las filas "
                     "son: " + ", ".join(V_MAX_NO_REVESTIDOS))
    _exigir_texto_de(DATO_REGIMEN_FLUJO, regimen_flujo, REGIMENES_DE_FLUJO_T11,
                     "no es una columna de la Tabla Nº 11 del Manual: "
                     + " o ".join(REGIMENES_DE_FLUJO_T11))
    V_adm = V_MAX_NO_REVESTIDOS[tipo_terreno][regimen_flujo]
    supera = V.valor > V_adm + TOL_UMBRAL_NORMATIVO
    concluyente = supera or not cota_inferior
    rotulo = TERRENO_T11_ROTULO[tipo_terreno]
    if donde == DONDE_SALIDA:
        codigo, lugar = "6.4", "a la salida"
        aplicacion = ("el contraste INFORMA: si la velocidad de salida supera "
                      "la admisible, el terreno necesita la proteccion; si "
                      "no la supera, el terreno la resistiria segun la "
                      "tabla. En los dos casos el proyecto calcula y "
                      "mantiene la proteccion (pasos 6.1, 6.5 y 6.6). No "
                      "descarta el diametro: el techo de velocidad DENTRO "
                      "del conducto es V3")
        citas = ("MC_HHD.4.1.1.3.6#T11", "MC_HHD.4.1.1.3.6#V_SALIDA",
                 "MC_HHD.4.1.1.3.7c#PROTECCION", "HDS5_3ED.5.3.2#PRACTICA")
    else:
        codigo, lugar = "6.8", "en la boca de entrada"
        aplicacion = ("EXTENSION DEL PROYECTO: el Manual presenta la tabla al "
                      "tratar la velocidad de SALIDA, y aqui se aplica al "
                      "cauce de aproximacion, que tambien es un canal sin "
                      "revestir, por la recomendacion del num. 4.1.1.3.7 c), "
                      "que nombra la entrada. Si la supera, el cauce de "
                      "entrada se reviste")
        citas = ("MC_HHD.4.1.1.3.6#T11", "MC_HHD.4.1.1.3.7c#PROTECCION")
    margen = V_adm - V.valor
    if supera:
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.INDICADOR, margen=margen, unidad="m/s",
            explicacion=f"la velocidad {lugar} ({V.valor:.2f} m/s) supera la "
                        f"maxima admisible del terreno «{rotulo}» con flujo "
                        f"{regimen_flujo} ({V_adm:.2f} m/s, Tabla Nº 11): el "
                        "cauce se protege")
    elif not concluyente:
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.INDICADOR, margen=margen, unidad="m/s",
            explicacion=f"el contraste con la Tabla Nº 11 no concluye: la "
                        f"velocidad {lugar} ({V.valor:.2f} m/s) no supera la "
                        f"maxima admisible del terreno «{rotulo}» con flujo "
                        f"{regimen_flujo} ({V_adm:.2f} m/s), pero es una "
                        "cota inferior de la real (se tomo al tirante "
                        "critico y el de borde es menor, HEC-14 num. 3.1.3). "
                        "No se afirma que el terreno la resista")
    else:
        resto = ("la proteccion se calcula y se mantiene igual: suprimirla "
                 "queda sujeto a inspeccion de campo (HDS-5 num. 5.3.2)"
                 if donde == DONDE_SALIDA else
                 "el proyecto no pide revestir el cauce de aproximacion por "
                 "este contraste")
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.CUMPLE, margen=margen, unidad="m/s",
            explicacion=f"la velocidad {lugar} no supera la maxima admisible "
                        f"del terreno «{rotulo}» con flujo {regimen_flujo}: "
                        "segun la tabla el terreno natural la resistiria, y "
                        "asi lo lee el proyecto; " + resto)
    return VelocidadAdmisible(
        donde=donde, tipo_terreno=tipo_terreno, regimen_flujo=regimen_flujo,
        V=V.valor, V_admisible=V_adm, supera=supera, concluyente=concluyente,
        paso=paso(
            "F6.V_ADMISIBLE",
            codigo=codigo,
            que=f"Velocidad {lugar} contra la maxima admisible del terreno",
            formula="V <= V_adm(tipo de terreno, regimen del flujo)",
            formula_cita_id="MC_HHD.4.1.1.3.6#T11",
            citas_textuales=citas,
            sustitucion=(
                Magnitud("V", V.valor, "m/s", V.procedencia,
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("terreno", rotulo, "",
                         f"dato de sitio del punto, `{dato}`: fila de la "
                         "Tabla Nº 11"),
                Magnitud("flujo", regimen_flujo, "",
                         f"dato de sitio del punto, `{DATO_REGIMEN_FLUJO}`: "
                         "columna de la Tabla Nº 11")),
            resultado=Magnitud("V_adm", V_adm, "m/s",
                               "celda de la Tabla Nº 11 "
                               "(`constantes_normativas.V_MAX_NO_REVESTIDOS`)",
                               cifras=CIFRAS_FACTOR),
            umbral=Umbral(
                descripcion="velocidad maxima admisible en canales no "
                            "revestidos",
                valor=V_adm, unidad="m/s",
                cita_id="MC_HHD.4.1.1.3.6#T11",
                caracter="EXIGENCIA para la velocidad de salida («debe "
                         "limitarse»); la tabla da el maximo por tipo de "
                         "terreno",
                aplicacion=aplicacion),
            veredicto=veredicto,
            nota_del_proyecto=(
                _lectura("MC_HHD.4.1.1.3.7c#PROTECCION")
                + ("" if donde != DONDE_SALIDA else
                   " " + _lectura("HDS5_3ED.5.3.2#PRACTICA")))))


# ---------------------------------------------------------------------------
# Apron de enrocado de HEC-14 (Sec. 10.2)
# ---------------------------------------------------------------------------

def apron_hec14(*, Q_celda: float, seccion: Seccion, TW: float,
                y_salida: Optional[float], y_critico: float,
                numero_celdas: int = 1) -> ApronHEC14:
    """
    Apron de enrocado por HEC-14 Sec. 10.2 (pags. impresas 10-16 a 10-19).

        D50 = 0.2·D·[Q / (g^0.5·D^2.5)]^(4/3)·(D / TW)          Ec. (10.4)
        D'  = (D + yn) / 2     si el flujo en el conducto es supercritico
                                                                Ec. (10.5)

    y de la Tabla 10.1, con la clase de D50 mayor o igual que el requerido:
    longitud = kL·D, profundidad = ke·D50 de la clase, y ancho al final =
    3·D + (2/3)·L (ejemplo resuelto, pag. 10-19).

    RANGO DE VALIDEZ, transcrito y aplicado:
      * «recommended for CIRCULAR culverts»: un marco no se evalua
        (`MetodoNoEvaluableError`), ni un tubo de varias celdas.
      * TW entre 0.4·D y 1.0·D. Por debajo se usa 0.4·D, como hace el ejemplo
        resuelto de la fuente («use TW = 0.4D»); el resultado lo dice. Por
        encima la fuente remite a la Figura 10.3, que no esta digitalizada:
        `MetodoNoEvaluableError`.
      * Conducto de hasta 60 in de alto: la nota 8 de la Tabla 1.1
        «Energy Dissipators and Limitations» lo pone como LIMITE del apron
        («Culvert rise less than or equal to 1500 mm (60 in)»), y la Sec.
        10.2 lo repite como poblacion. Las dos cifras no coinciden (60 in =
        1.524 m) y rige 1.524 m, la que deja evaluar el ejemplo resuelto de
        la propia fuente, de D = 5.0 ft (`HEC14_APRON_ALTURA_MAX_M`). Por
        encima, `MetodoNoEvaluableError`, como los otros limites.

    «SUPERCRITICO EN EL CONDUCTO» se decide con `flujo_supercritico`, la
    MISMA regla que rotula el Froude, sobre `y_salida`: el tirante con que M4
    midio la velocidad de salida. Bajo control de entrada es el normal de
    registro (rama de n maximo); bajo control de salida y con el barril
    horizontal es max(TW, y_c), que nunca queda bajo el critico, y no hay
    ajuste. D' = (D + y)/2 entra en la Ec. (10.4) y --LECTURA DEL PROYECTO,
    `Interpretacion` de la cita HEC14.10.2#TW-- en los limites del TW; la
    longitud de la Tabla 10.1 usa D, la altura real del conducto («D is the
    culvert rise»). Sin `y_salida` el regimen NO se puede decidir: no se
    ajusta, y el resultado lo dice (`regimen_determinado` False) para que la
    fase lo avise; antes se resolvia en silencio como «no supercritico».

    EL yn ES EL DE REGISTRO, Y NO ES EL LADO ALTO DEL D50, dicho para que no
    se lea de mas: la regla de doble n (Sec. 4.1) da los TIRANTES con n_max,
    y este es el que M4 publica como tirante de salida. Con n_min el tirante
    supercritico es menor --desde VE-2 M3 lo resuelve, para la velocidad
    (`TiranteNormal.geometria_erosion`), y no viaja aqui--, D' tambien, y
    como D50 va con D'^(-4/3) la piedra saldria algo mayor. El paso lo
    declara en la procedencia de D'; pasar a ese tirante es una decision
    diferida en la ficha VE2-B. Si este D50 rige o es solo contraste lo
    decide la regla 'regla_espesor_longitud_proteccion_salida' en
    `proteccion_salida`.
    """
    _exigir_positivo("Q_celda", Q_celda, "caudal de un barril, m3/s")
    _exigir_no_negativo("TW", TW, "tirante del receptor, m")
    _exigir_positivo("y_critico", y_critico, "tirante critico, m")
    if y_salida is not None:
        _exigir_positivo("y_salida", y_salida, "tirante a la salida, m")
    que = "apron de enrocado (HEC-14 Ec. 10.4)"
    if not isinstance(seccion, SeccionCircular):
        raise MetodoNoEvaluableError(
            que,
            procedimiento="la poza de enrocado de HEC-14 (Sec. 10.1), que "
                          "vale para marcos y que la Fase 6 evalua en su "
                          "lugar (`poza_de_enrocado_hec14`)",
            motivo="la Ec. (10.4) es la que la fuente recomienda «for "
                   "circular culverts» y el conducto es un marco",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    if numero_celdas != 1:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="un diseño de la proteccion para la descarga "
                          "conjunta de los barriles",
            motivo=f"la Ec. (10.4) es para UN conducto circular y el cruce "
                   f"tiene {numero_celdas} barriles",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    D = seccion.altura
    if D > HEC14_APRON_ALTURA_MAX_M + TOL_UMBRAL_NORMATIVO:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="la poza de enrocado de HEC-14 (Sec. 10.1), sin "
                          "limite de altura en la Tabla 1.1, que la Fase 6 "
                          "evalua en su lugar (`poza_de_enrocado_hec14`)",
            motivo=f"el conducto mide {D:.3f} m de alto y la Tabla 1.1 de "
                   "HEC-14 limita el apron de enrocado a conductos de hasta "
                   f"1500 mm (60 in = {HEC14_APRON_ALTURA_MAX_M:.3f} m, que "
                   "es la cifra que rige; nota 8)",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    regimen = flujo_supercritico(y_salida, y_critico)
    regimen_determinado = regimen is not None
    supercritico = regimen is True
    D_calc = (D + y_salida) / 2 if supercritico else D
    # Con que nombre se llama al diametro de los limites del TW en un
    # mensaje: D' cuando la Ec. (10.5) lo ajusto (H10-a: decia «1·D = 0.764
    # m» de un tubo de 0.90 m).
    nombre_D = (f"D' = {D_calc:.3f} m (Ec. 10.5; el conducto mide "
                f"{D:.3f} m)" if supercritico else f"D = {D_calc:.3f} m")
    tw_min = HEC14_APRON_TW_SOBRE_D_MIN * D_calc
    tw_max = HEC14_APRON_TW_SOBRE_D_MAX * D_calc
    if TW > tw_max + TOL_UMBRAL_NORMATIVO:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="la Figura 10.3 de HEC-14 (atenuacion de la "
                          "velocidad aguas abajo) con la Ec. (10.6) de la "
                          "Sec. 10.3, que la Fase 6 evalua en su lugar "
                          "(`proteccion_tw_alto_hec14`)",
            motivo=f"el tirante del receptor (TW = {TW:.3f} m) supera el "
                   f"rango aceptable de la ecuacion, hasta "
                   f"{HEC14_APRON_TW_SOBRE_D_MAX:g} veces {nombre_D}",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    acotado = TW < tw_min - TOL_UMBRAL_NORMATIVO
    TW_calc = tw_min if acotado else TW
    adimensional = Q_celda / (
        math.sqrt(G) * D_calc ** HEC14_EXPONENTE_LONGITUD_DEL_CAUDAL_ADIMENSIONAL)
    D50 = (HEC14_APRON_COEFICIENTE * D_calc
           * adimensional ** HEC14_APRON_EXPONENTE * (D_calc / TW_calc))

    procedencia_D = (
        "diametro interior del conducto. REGIMEN NO DETERMINADO: falta el "
        "tirante de salida, la Ec. (10.5) no se aplico y, si el flujo fuera "
        "supercritico, el D50 seria mayor" if not regimen_determinado else
        "diametro interior del conducto" if not supercritico else
                     f"D' = (D + yn)/2 de la Ec. (10.5), con D = {D:.3f} m e "
                     f"yn = {y_salida:.3f} m: el flujo es supercritico "
                     f"(y < yc = {y_critico:.3f} m, la misma regla del paso "
                     "6.3). yn es el tirante normal de registro (n maximo, "
                     "Sec. 4.1); con n minimo seria menor y el D50, algo "
                     "mayor")
    procedencia_TW = (
        "tirante del cuerpo receptor del punto (Sec. 1.3)" if not acotado else
        f"el del punto es {TW:.3f} m, menor que "
        f"{HEC14_APRON_TW_SOBRE_D_MIN:g} veces {nombre_D}, o sea "
        f"{tw_min:.3f} m: se usa ese piso, como el ejemplo resuelto de la "
        "fuente (pag. impresa 10-18), que es ademas lo que indica cuando el "
        "TW no se conoce")
    paso_d50 = paso(
        "F6.APRON",
        codigo="6.5",
        que="Tamaño de piedra del apron de enrocado por HEC-14",
        formula="D50 = 0.2 * D * [Q / (g^0.5 * D^2.5)]^(4/3) * (D / TW)",
        formula_cita_id="HEC14.10.2#EC_10_4",
        citas_textuales=("HEC14.10.2#EC_10_4", "HEC14.10.2#TW",
                         "HEC14.D#SOLO_VELOCIDAD")
        + (("HEC14.10.2#EC_10_5",) if supercritico else ()),
        sustitucion=(
            Magnitud("Q", Q_celda, "m3/s", "caudal del barril, Q_celda",
                     cifras=CIFRAS_FINA),
            Magnitud("D", D_calc, "m", procedencia_D, cifras=CIFRAS_MAGNITUD),
            Magnitud("TW", TW_calc, "m", procedencia_TW,
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("g", G, "m/s2", "`constantes_fisicas.G`, el 9.81 que "
                     "HEC-14 escribe", cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("D50", D50, "m",
                           "tamaño de piedra requerido por la Ec. (10.4), "
                           "que supone una piedra de gravedad especifica "
                           f"{HEC14_APRON_GRAVEDAD_ESPECIFICA_PIEDRA:g} (si la "
                           "real difiere mucho, la fuente pide corregir el "
                           "D50 en proporcion inversa)",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="dimensionamiento [C] por la ecuacion a la que el "
                        "HDS-5 remite el apron; si rige o es contraste del "
                        "d50 de Laushey lo decide la regla declarada (paso "
                        "6.2)"),
        # Los limites del TW con D' son lectura: solo se imprime cuando la
        # Ec. (10.5) ajusto el diametro, que es cuando tiene efecto.
        nota_del_proyecto=(_lectura("HEC14.10.2#TW") if supercritico else ""),
    )

    clase = D50_clase = k_long = k_esp = None
    for n_clase, d50_clase, k_l, k_e in HEC14_TABLA_10_1:
        if not d50_clase < D50 - TOL_UMBRAL_NORMATIVO:
            clase, D50_clase, k_long, k_esp = n_clase, d50_clase, k_l, k_e
            break
    comunes = dict(D50_requerido=D50, D=D, D_de_calculo=D_calc,
                   ajustado_por_supercritico=supercritico, TW=TW,
                   TW_de_calculo=TW_calc, TW_acotado=acotado,
                   regimen_determinado=regimen_determinado)
    if clase is None:
        mayor = HEC14_TABLA_10_1[-1]
        return ApronHEC14(**comunes, pasos=(paso_d50, paso(
            "F6.APRON_GEOMETRIA",
            codigo="6.6",
            que="Clase de enrocado del apron por la Tabla 10.1 de HEC-14",
            formula="clase: la de D50 >= D50 requerido",
            formula_cita_id="HEC14.10.2#T10_1",
            citas_textuales=("HEC14.10.2#T10_1",
                             "MC_HHD.4.1.1.3.7c#ALIVIADERO",
                             "MC_HHD.LAMINA_04"),
            sustitucion=(
                Magnitud("D50", D50, "m", "requerido, paso 6.5",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("D50 de la clase mayor", mayor[1], "m",
                         f"clase {mayor[0]} de la Tabla 10.1",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("clase", "ninguna", "",
                               "el D50 requerido supera la mayor clase de "
                               "la tabla"),
            veredicto=Veredicto(
                tipo=TipoDeVeredicto.SIN_VEREDICTO,
                explicacion="fuera de la Tabla 10.1: la salida pide un "
                            "disipador diseñado por HEC-14 (HDS-5 num. "
                            "5.3.2), no un apron de catalogo"),
            nota_del_proyecto=(
                "El Manual da, para una velocidad alta, otra medida que no "
                "reviste el cauce sino que reduce la velocidad: el aliviadero "
                "escalonado de su Lámina Nº 04. Ni el disipador de HEC-14 ni "
                "el aliviadero se dimensionan en este programa."))))
    longitud = k_long * D
    espesor = k_esp * D50_clase
    ancho = (HEC14_APRON_ANCHO_EN_LA_BOCA_EN_D * D
             + HEC14_APRON_ABOCINADO_POR_LONGITUD * longitud)
    paso_geom = paso(
        "F6.APRON_GEOMETRIA",
        codigo="6.6",
        que="Clase, longitud, profundidad y ancho del apron por la Tabla "
            "10.1 de HEC-14",
        formula="L = kL * D;  e = ke * D50_clase;  W = 3 * D + (2/3) * L",
        formula_cita_id="HEC14.10.2#T10_1",
        citas_textuales=("HEC14.10.2#T10_1", "HEC14.10.2#ANCHO",
                         "MC_HHD.LAMINA_05"),
        sustitucion=(
            Magnitud("D50", D50, "m", "requerido, paso 6.5",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("clase", clase, "",
                     "la primera de la Tabla 10.1 con D50 mayor o igual que "
                     "el requerido"),
            Magnitud("D50_clase", D50_clase, "m", f"clase {clase}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("kL", k_long, "-", f"longitud del apron de la clase "
                     f"{clase}, en alturas del conducto",
                     cifras=CIFRAS_FACTOR),
            Magnitud("ke", k_esp, "-", f"profundidad del apron de la clase "
                     f"{clase}, en D50", cifras=CIFRAS_FACTOR),
            Magnitud("D", D, "m", "altura del conducto («D is the culvert "
                     "rise»): el diametro, sin el ajuste de la Ec. (10.5)",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("L", longitud, "m",
                           f"longitud del apron; profundidad e = "
                           f"{espesor:.3f} m; ancho al final W = "
                           f"{ancho:.3f} m",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="guia de la fuente (la tabla es un EJEMPLO de "
                        "estandar de proyecto): se compara con lo adoptado "
                        "en el paso 6.2"),
        nota_del_proyecto=(
            "La Lámina Nº 05 del Manual dibuja el enrocado de salida sin "
            "ninguna dimension (taludes «H:V», cotas «VARIABLE»): no hay "
            "medida peruana con que contrastar, y por eso el contraste es "
            "con HEC-14."),
    )
    return ApronHEC14(**comunes, clase=clase, D50_clase=D50_clase,
                      longitud=longitud, espesor=espesor, ancho_final=ancho,
                      pasos=(paso_d50, paso_geom))


# ---------------------------------------------------------------------------
# --- VE-5 (lote m6) --- Figura 10.3 y Ec. (10.6) de HEC-14: el TW alto
# ---------------------------------------------------------------------------

_QUE_FIGURA_10_3 = "atenuacion de la velocidad (HEC-14 Figura 10.3)"


def atenuacion_figura_10_3(L_sobre_De: float) -> float:
    """
    VL/Vo de la curva de diseño de la Figura 10.3 de HEC-14 (num. 10.1.3,
    pag. impresa 10-4) en L/De, interpolada en log-log entre los puntos de
    `HEC14_FIGURA_10_3` (leidos por imagen; los cuatro que la fuente imprime
    en sus ejemplos, tal cual). Hasta L/De = 1 vale 1. Mas alla del ultimo
    punto (L/De = 60) la figura no da nada: `MetodoNoEvaluableError`.
    """
    _exigir_no_negativo("L/De", L_sobre_De, "distancia en diametros "
                        "equivalentes")
    x0, f0 = HEC14_FIGURA_10_3[0]
    if not L_sobre_De > x0:
        return f0
    for (xa, fa), (xb, fb) in zip(HEC14_FIGURA_10_3, HEC14_FIGURA_10_3[1:]):
        if not L_sobre_De > xb + TOL_UMBRAL_NORMATIVO:
            t = math.log(L_sobre_De / xa) / math.log(xb / xa)
            return math.exp(math.log(fa) + t * math.log(fb / fa))
    x_max, f_min = HEC14_FIGURA_10_3[-1]
    raise MetodoNoEvaluableError(
        _QUE_FIGURA_10_3,
        procedimiento="una medida de la atenuacion mas alla de la figura",
        motivo=f"L/De = {L_sobre_De:.1f} queda fuera de la Figura 10.3, que "
               f"llega a L/De = {x_max:g} (VL/Vo = {f_min:g})",
        rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)


def distancia_figura_10_3(V_sobre_Vo: float) -> float:
    """
    La inversa de `atenuacion_figura_10_3`: el L/De en que la velocidad del
    eje baja a `V_sobre_Vo` veces la de salida («The calculations above
    continue until VL ≤ Vallow», pag. 10-8). Con 1 o mas, 0. Bajo el ultimo
    punto de la figura (0.10), `MetodoNoEvaluableError`.
    """
    _exigir_positivo("VL/Vo", V_sobre_Vo, "fraccion de la velocidad de salida")
    if not V_sobre_Vo < HEC14_FIGURA_10_3[0][1]:
        return 0.0
    for (xa, fa), (xb, fb) in zip(HEC14_FIGURA_10_3, HEC14_FIGURA_10_3[1:]):
        if not V_sobre_Vo < fb - TOL_UMBRAL_NORMATIVO:
            t = math.log(V_sobre_Vo / fa) / math.log(fb / fa)
            return math.exp(math.log(xa) + t * math.log(xb / xa))
    x_max, f_min = HEC14_FIGURA_10_3[-1]
    raise MetodoNoEvaluableError(
        _QUE_FIGURA_10_3,
        procedimiento="una medida de la atenuacion mas alla de la figura",
        motivo=f"la velocidad tendria que bajar a {V_sobre_Vo:.3f} veces la "
               f"de salida y la Figura 10.3 llega a {f_min:g} (L/De = "
               f"{x_max:g})",
        rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)


def d50_ec_10_6(*, V: float) -> float:
    """
    D50 = 0.692/(S - 1)·V^2/(2g), Ec. (10.6) de HEC-14 Sec. 10.3 (Searcy,
    1967), con S = 2.65 (la de la Ec. 10.4).
    """
    _exigir_positivo("V", V, "velocidad, m/s")
    return (HEC14_EC_10_6_COEFICIENTE
            / (HEC14_APRON_GRAVEDAD_ESPECIFICA_PIEDRA - 1) * V ** 2 / (2 * G))


def diametro_equivalente(area: float) -> float:
    """De = 2·(A/pi)^0.5 = (4·A/pi)^0.5: la nota de la Figura 10.3."""
    _exigir_positivo("A", area, "area de borde, m2")
    return 2 * math.sqrt(area / math.pi)


def proteccion_tw_alto_hec14(*, V: Magnitud, Q_celda: float, TW: float,
                             V_admisible: Optional[float]
                             ) -> ProteccionTWAlto:
    """
    La proteccion de salida con el tirante del receptor sobre 1.0·D, donde
    la Ec. (10.4) no vale: «Figure 10.3 should be used to determine the
    velocity downstream of the culvert. The guidance in Section 10.3 may be
    used for sizing the riprap. The apron length is determined based on the
    allowable velocity and the location at which it occurs based on Figure
    10.3» (HEC-14 Sec. 10.2, pag. impresa 10-18).

        De = (4·A/pi)^0.5,  A = Q_celda / Vo        (area de borde)
        L  = De · (L/De en que VL/Vo = Vallow/Vo)   (Figura 10.3)
        D50 = 0.692/(S - 1)·Vo^2/(2g)               (Ec. 10.6, en la boca)

    El espesor, que la Sec. 10.3 no da, es 2·D50: LECTURA DEL PROYECTO
    sobre el piso que HEC-14 pone al enrocado en la poza y en el apron
    (`HEC14_ESPESOR_MIN_EN_D50`). Sin `V_admisible` no hay longitud:
    `DatoFaltanteError` del terreno del receptor (la Fase 6 lo avisa).
    """
    _exigir_velocidad(V, "proteccion_tw_alto_hec14")
    _exigir_positivo("Q_celda", Q_celda, "caudal de un barril, m3/s")
    _exigir_no_negativo("TW", TW, "tirante del receptor, m")
    if V_admisible is None:
        raise DatoFaltanteError(
            DATO_TERRENO_RECEPTOR,
            detalle="con el tirante del receptor sobre la clave la longitud "
                    "de la proteccion es hasta donde la velocidad baja a la "
                    "admisible del cauce (HEC-14 Sec. 10.2 y Figura 10.3), y "
                    "sin el terreno del receptor (Tabla Nº 11) no hay "
                    "admisible")
    _exigir_positivo("V_admisible", V_admisible, "velocidad admisible, m/s")
    De = diametro_equivalente(Q_celda / V.valor)
    L = De * distancia_figura_10_3(V_admisible / V.valor)
    D50 = d50_ec_10_6(V=V.valor)
    espesor = HEC14_ESPESOR_MIN_EN_D50 * D50
    paso_tw = paso(
        "F6.TW_ALTO",
        codigo="6.5t",
        que="Proteccion de salida con el tirante del receptor sobre la "
            "clave (Figura 10.3 y Ec. 10.6 de HEC-14)",
        formula="De = (4 A / pi)^0.5;  L = De * (L/De)[VL/Vo = Vallow/Vo];  "
                "D50 = 0.692 / (S - 1) * Vo^2 / (2 g)",
        formula_cita_id="HEC14.10.1.3#FIGURA_10_3",
        citas_textuales=("HEC14.10.2#TW_ALTO", "HEC14.10.1.3#FIGURA_10_3",
                         "HEC14.10.3#EC_10_6", "HEC14.10.1#HASTA_VALLOW"),
        sustitucion=(
            Magnitud("Vo", V.valor, "m/s", V.procedencia,
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("A", Q_celda / V.valor, "m2", "area de borde por "
                     "continuidad, Q_celda / Vo", cifras=CIFRAS_FINA),
            Magnitud("De", De, "m", "diametro equivalente del area de borde",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("TW", TW, "m", "tirante del receptor, sobre la clave",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("Vallow", V_admisible, "m/s", "admisible del terreno "
                     "del receptor, Tabla Nº 11 del Manual",
                     cifras=CIFRAS_FACTOR),
            Magnitud("S", HEC14_APRON_GRAVEDAD_ESPECIFICA_PIEDRA, "-",
                     "gravedad especifica de la piedra, la de la Ec. (10.4)",
                     cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("L", L, "m",
                           f"longitud de la proteccion desde la boca; piedra "
                           f"D50 = {D50:.3f} m en la boca, espesor "
                           f"{espesor:.3f} m", cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="dimensionamiento [C]: la Figura 10.3 da la "
                        "atenuacion y la proteccion llega hasta VL = Vallow"),
        nota_del_proyecto=(
            "LECTURA DEL PROYECTO: el espesor, que la Sec. 10.3 no da, es "
            f"{HEC14_ESPESOR_MIN_EN_D50:g} veces el D50, el piso que HEC-14 "
            "pone al enrocado de la poza y del apron. La Figura 10.3 esta "
            "leida por imagen (tolerancia 0.015 en VL/Vo)."))
    return ProteccionTWAlto(De=De, Vo=V.valor, V_admisible=V_admisible,
                            D50=D50, longitud=L, espesor=espesor,
                            pasos=(paso_tw,))


# ---------------------------------------------------------------------------
# --- VE-4g --- Poza de enrocado de HEC-14 (Sec. 10.1)
# ---------------------------------------------------------------------------

CRITERIO_RELACION_CO = "relacion_co_poza_enrocado_hec14"


def parametro_co_poza(tw_sobre_ye: float, relacion: str) -> float:
    """
    El parametro del tirante del receptor de la Ec. (10.1) de HEC-14 (num.
    10.1.1, pag. impresa 10-3): Ec. (10.2), envolvente, o (10.3), mejor
    ajuste, por tramos de TW/ye con los bordes en 0.75 y 1.0. Las dos son
    continuas en sus bordes, de modo que el lado en que cae el borde no
    cambia el numero. CUAL rige es el criterio [A]
    'relacion_co_poza_enrocado_hec14'.
    """
    _exigir_no_negativo("TW/ye", tw_sobre_ye, "relacion del tirante del "
                        "receptor con el tirante equivalente")
    _exigir_texto_de(CRITERIO_RELACION_CO, relacion, HEC14_POZA_CO,
                     "es una de las relaciones de HEC-14: "
                     + ", ".join(HEC14_POZA_CO))
    bajo, pendiente, ordenada, alto = HEC14_POZA_CO[relacion]
    if tw_sobre_ye < HEC14_POZA_TW_SOBRE_YE_BAJO:
        return bajo
    if tw_sobre_ye > HEC14_POZA_TW_SOBRE_YE_ALTO:
        return alto
    return pendiente * tw_sobre_ye + ordenada


def salida_critica_de_la_poza(*, Q: float, ancho_fondo: float,
                              z: float = HEC14_POZA_TALUD_LATERAL_Z
                              ) -> Tuple[float, float, float]:
    """
    Paso 4 del procedimiento de la poza (HEC-14 num. 10.1.5, pag. impresa
    10-5): el tirante critico en la salida de la poza, yB = yc, por la Ec.
    (7.14) en la seccion trapecial de fondo WB y taludes z:1,

        Q^2/g = Ac^3/Tc = [yc·(WB + z·yc)]^3 / (WB + 2·z·yc)

    y la velocidad VB = Vc = Q/Ac. Devuelve (yc, Ac, Vc). El tirante de la
    seccion rectangular del mismo fondo, (q^2/g)^(1/3), es cota superior de
    yc (el trapecio tiene mas area a igual tirante) y cierra el intervalo
    de Brent.
    """
    _exigir_positivo("Q", Q, "caudal que sale de la poza, m3/s")
    _exigir_positivo("WB", ancho_fondo, "ancho de la poza en su salida, m")
    _exigir_no_negativo("z", z, "talud lateral de la poza, H:V")
    objetivo = Q ** 2 / G

    def exceso(y: float) -> float:
        area = y * (ancho_fondo + z * y)
        return area * area * area / (ancho_fondo + 2 * z * y) - objetivo

    y_rect = math.cbrt(objetivo / ancho_fondo ** 2)
    yc = brentq(exceso, y_rect * TOL_UMBRAL_NORMATIVO, y_rect)
    area = yc * (ancho_fondo + z * yc)
    return yc, area, Q / area


def _ancho_para_la_velocidad(Q: float, V_objetivo: float, ancho_desde: float,
                             z: float) -> float:
    """El ancho de salida de la poza con el que Vc = V_objetivo (paso 4)."""
    def exceso(ancho: float) -> float:
        return salida_critica_de_la_poza(Q=Q, ancho_fondo=ancho, z=z)[2] \
            - V_objetivo
    hasta = ancho_desde
    # Vc baja sin cota con el ancho (q = Q/WB -> 0): doblando se cruza el
    # objetivo en un numero finito de pasos salvo que la aritmetica desborde.
    while exceso(hasta) > 0:
        if not math.isfinite(hasta * 2):
            raise LimiteNumericoError(
                "WB", valor=hasta,
                motivo=f"no se encontro el ancho de poza en que la velocidad "
                       f"critica baja a {V_objetivo!r} m/s con Q = {Q!r} "
                       "m3/s: la pareja caudal-velocidad admisible no cabe")
        ancho_desde, hasta = hasta, hasta * 2
    return brentq(exceso, ancho_desde, hasta)


def poza_de_enrocado_hec14(*, V: Magnitud, Q_celda: float, seccion: Seccion,
                           TW: float, y_salida: Optional[float],
                           d50_piedra: float, origen_piedra: str,
                           V_admisible: Optional[float] = None,
                           numero_celdas: int = 1) -> PozaDeEnrocado:
    """
    Poza de enrocado (riprap basin) de HEC-14 Sec. 10.1, por el procedimiento
    del num. 10.1.5 (pags. impresas 10-1 a 10-5), con los cuatro ejemplos
    resueltos de las pags. 10-6 a 10-16 como oraculo.

      Paso 1  ye y Fr por continuidad con la velocidad de salida que M4 da
              (`froude_salida`: ye = A/B en un marco, (A/2)^0.5 en un tubo).
      Paso 2  Co por la Ec. (10.2) o (10.3) (criterio [A]
              'relacion_co_poza_enrocado_hec14') y
                  hs/ye = 0.86·(D50/ye)^(-0.55)·Fr - Co         Ec. (10.1)
              con hs/D50 >= 2 y D50/ye >= 0.1. Si la piedra que el proyecto
              pone (`d50_piedra`) da hs/D50 < 2, la poza se dimensiona con la
              piedra de hs/D50 = 2 EXACTO y se reviste con la que se pone
              («A basin sized for smaller riprap may be lined with larger
              riprap»). Si la piedra queda bajo 0.1·ye, se sube a 0.1·ye. Si
              ni la piedra de 0.1·ye llega a hs/D50 = 2, la ecuacion no se
              extrapola: `MetodoNoEvaluableError`.
      Paso 3  Ls = max(10·hs, 3·Wo); LB = max(15·hs, 4·Wo); LA = LB - Ls;
              WB = Wo + (2/3)·LB. Wo es el ancho del conducto en la boca: B
              en un marco, D en un tubo.
      Paso 4  yc y Vc en la salida, Ec. (7.14) con z = 2 (Figura 10.2),
              contra `V_admisible`. Si la supera, el apron se alarga con el
              mismo abocinado hasta Vc = Vallow, como el ejemplo de la fuente
              (`extendida`). Sin `V_admisible` no se contrasta, y se avisa.
      Paso 5  TW/yo > 0.75 pide proteccion aguas abajo por la Figura 10.3:
              `proteccion_adicional`, con aviso.

    Espesores (num. 10.1.4 y Figura 10.1): 2·D50 en el piso y los lados,
    3·D50 en el talud de la salida del conducto, con la piedra que reviste.

    LIMITES (`MetodoNoEvaluableError`, rotulo de HEC-14): varios barriles
    (los ensayos son de un conducto, num. 10.1.1), Froude de 3 o mas (Tabla
    1.1) y la hoya que no llega a 2·D50 con ninguna piedra del rango.
    """
    _exigir_velocidad(V, "poza_de_enrocado_hec14")
    _exigir_positivo("Q_celda", Q_celda, "caudal de un barril, m3/s")
    _exigir_no_negativo("TW", TW, "tirante del receptor, m")
    _exigir_positivo("d50_piedra", d50_piedra, "piedra de la poza, m")
    if y_salida is not None:
        _exigir_positivo("y_salida", y_salida, "tirante de borde, m")
    if V_admisible is not None:
        _exigir_positivo("V_admisible", V_admisible,
                         "velocidad admisible a la salida de la poza, m/s")
    que = "poza de enrocado (HEC-14 Sec. 10.1)"
    if numero_celdas != 1:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="un diseño de la proteccion para la descarga "
                          "conjunta de los barriles, que ninguna fuente del "
                          "repositorio de normas da",
            motivo=f"los ensayos de la poza son de UN conducto (num. "
                   f"10.1.1) y el cruce tiene {numero_celdas} barriles",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    froude = froude_salida(V=V, Q_celda=Q_celda, seccion=seccion,
                           y_salida=y_salida)
    ye, Fr = froude.y_equivalente, froude.Fr
    if not Fr < HEC14_POZA_FROUDE_MAX:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="un disipador de HEC-14 para Froude alto (Caps. 7 "
                          "a 9), fuera del alcance de este programa",
            motivo=f"el numero de Froude de la salida es {Fr:.2f} y la "
                   f"Tabla 1.1 de HEC-14 limita la poza a Fr < "
                   f"{HEC14_POZA_FROUDE_MAX:g}",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    relacion = ca.valor(CRITERIO_RELACION_CO)
    Co = parametro_co_poza(TW / ye, relacion)
    termino = HEC14_POZA_COEFICIENTE_HS * Fr

    def hs_sobre_ye(x: float) -> float:
        return termino * x ** HEC14_POZA_EXPONENTE_D50 - Co

    def holgura(x: float) -> float:
        """hs/ye - 2·D50/ye: no negativa <=> hs/D50 >= 2."""
        return hs_sobre_ye(x) - HEC14_POZA_HS_SOBRE_D50_MIN * x

    D50_minimo = HEC14_POZA_D50_SOBRE_YE_MIN * ye
    piedra_subida = d50_piedra < D50_minimo - TOL_UMBRAL_NORMATIVO
    D50_piedra = D50_minimo if piedra_subida else d50_piedra
    x_piedra = D50_piedra / ye
    dimensionada_con_menor = holgura(x_piedra) < -TOL_UMBRAL_NORMATIVO
    if not dimensionada_con_menor:
        x_dim = x_piedra
    else:
        x_min = HEC14_POZA_D50_SOBRE_YE_MIN
        if holgura(x_min) < -TOL_UMBRAL_NORMATIVO:
            raise MetodoNoEvaluableError(
                que,
                procedimiento="otra proteccion: con este tirante del receptor "
                              "y esta velocidad la Ec. (10.1) no da una poza "
                              "dentro del rango de sus ensayos",
                motivo=f"ni la piedra menor del rango de los ensayos (D50/ye "
                       f"= {HEC14_POZA_D50_SOBRE_YE_MIN:g}, D50 = "
                       f"{D50_minimo:.3f} m) deja la hoya en hs/D50 >= "
                       f"{HEC14_POZA_HS_SOBRE_D50_MIN:g} (Fr = {Fr:.2f}, TW/ye "
                       f"= {TW / ye:.2f}, Co = {Co:.2f}): la fuente descarto "
                       "los ensayos de hs/D50 < 2",
                rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
        x_dim = brentq(holgura, x_min, x_piedra)
    D50_dim = x_dim * ye
    hs = hs_sobre_ye(x_dim) * ye

    Wo = seccion.B if isinstance(seccion, SeccionRectangular) else seccion.D
    Ls = max(HEC14_POZA_LS_EN_HS * hs, HEC14_POZA_LS_MIN_EN_WO * Wo)
    LB0 = max(HEC14_POZA_LB_EN_HS * hs, HEC14_POZA_LB_MIN_EN_WO * Wo)
    WB0 = Wo + HEC14_POZA_ABOCINADO_POR_LONGITUD * LB0
    yc, Ac, Vc = salida_critica_de_la_poza(Q=Q_celda, ancho_fondo=WB0)
    avisos: List[str] = []
    LB, WB = LB0, WB0
    extendida = (V_admisible is not None
                 and Vc > V_admisible + TOL_UMBRAL_NORMATIVO)
    if extendida:
        Vc0 = Vc
        WB = _ancho_para_la_velocidad(Q_celda, V_admisible, WB0,
                                      HEC14_POZA_TALUD_LATERAL_Z)
        LB = (WB - Wo) / HEC14_POZA_ABOCINADO_POR_LONGITUD
        yc, Ac, Vc = salida_critica_de_la_poza(Q=Q_celda, ancho_fondo=WB)
        avisos.append(
            f"Poza de enrocado: con LB = {LB0:.2f} m la velocidad en la "
            f"salida ({Vc0:.2f} m/s) supera la admisible ({V_admisible:.2f} "
            f"m/s); se extiende el apron con el mismo abocinado hasta LB = "
            f"{LB:.2f} m (WB = {WB:.2f} m), como el ejemplo de la fuente: «"
            + _literal("HEC14.10.1#EXTENDER") + "»")
    elif V_admisible is None:
        avisos.append(
            f"Poza de enrocado: sin la velocidad admisible del cauce (dato "
            f"de sitio '{DATO_TERRENO_RECEPTOR}' y "
            f"'{DATO_REGIMEN_FLUJO}') el paso 4 no se contrasta: la "
            f"velocidad en la salida de la poza es {Vc:.2f} m/s y no se sabe "
            "si el cauce la resiste")
    LA = LB - Ls
    espesor = HEC14_ESPESOR_MIN_EN_D50 * D50_piedra
    espesor_talud = HEC14_POZA_ESPESOR_TALUD_EN_D50 * D50_piedra
    proteccion_adicional = (
        None if y_salida is None else
        TW / y_salida > (HEC14_POZA_TW_SOBRE_YO_SIN_PROTECCION_ADICIONAL
                         + TOL_UMBRAL_NORMATIVO))
    if piedra_subida:
        avisos.append(
            f"Poza de enrocado: la piedra ({origen_piedra}, {d50_piedra:.3f} "
            f"m) queda bajo el limite de los ensayos, D50/ye = "
            f"{HEC14_POZA_D50_SOBRE_YE_MIN:g}; la poza se reviste con "
            f"D50 = {D50_piedra:.3f} m. «" + _literal("HEC14.10.1.5#RANGO")
            + "»")
    if dimensionada_con_menor:
        avisos.append(
            f"Poza de enrocado: con la piedra que se pone ({D50_piedra:.3f} "
            f"m) la hoya no llega a hs/D50 = "
            f"{HEC14_POZA_HS_SOBRE_D50_MIN:g}; la poza se dimensiona con la "
            f"piedra de hs/D50 = {HEC14_POZA_HS_SOBRE_D50_MIN:g} "
            f"({D50_dim:.3f} m) y se reviste con la que se pone: «"
            + _literal("HEC14.10.1#MAYOR_REVISTE") + "»")
    hasta = D50_adicional = None
    if proteccion_adicional is None:
        avisos.append(
            "Poza de enrocado: sin el tirante de borde (yo) no se decide el "
            "paso 5, la proteccion adicional aguas abajo")
    elif proteccion_adicional:
        base = (f"Poza de enrocado: TW/yo = {TW / y_salida:.2f} supera "
                f"{HEC14_POZA_TW_SOBRE_YO_SIN_PROTECCION_ADICIONAL:g}: con "
                "el tirante del receptor alto la corriente atraviesa la poza "
                "y la fuente pide proteccion aguas abajo, con la atenuacion "
                "de la velocidad de su Figura 10.3")
        if V_admisible is None:
            avisos.append(base + "; sin la velocidad admisible del cauce su "
                          "extension NO se dimensiona")
        else:
            De = diametro_equivalente(Q_celda / V.valor)
            try:
                hasta = De * distancia_figura_10_3(V_admisible / V.valor)
            except MetodoNoEvaluableError as error:
                avisos.append(base + f"; su extension NO se dimensiona -- "
                              f"{error.motivo}")
            else:
                if hasta > LB + TOL_UMBRAL_NORMATIVO:
                    D50_adicional = d50_ec_10_6(
                        V=V.valor * atenuacion_figura_10_3(LB / De))
                    avisos.append(
                        base + f": la proteccion llega hasta {hasta:.2f} m "
                        f"de la boca ({hasta - LB:.2f} m pasada la poza), "
                        f"con piedra de al menos {D50_adicional:.3f} m en la "
                        "salida de la poza (Ec. 10.6)")
                else:
                    avisos.append(
                        base + f": la velocidad del eje baja a la admisible "
                        f"a {hasta:.2f} m de la boca, dentro de la poza "
                        f"({LB:.2f} m)")

    elecciones = (EleccionDeProyecto(
        que_se_adopto="relacion del parametro Co de la poza",
        valor=relacion,
        entre=tuple(ca.CRITERIOS[CRITERIO_RELACION_CO].sensibilidad),
        de_donde=f"el criterio adoptado '{CRITERIO_RELACION_CO}' [A]",
        por_que="la fuente da la envolvente y el mejor ajuste y recomienda "
                "uno u otro segun la consecuencia de la falla",
        clave_criterio=CRITERIO_RELACION_CO),)
    paso_hs = paso(
        "F6.POZA",
        codigo="6.5p",
        que="Profundidad de la poza de enrocado de HEC-14",
        formula="hs / ye = 0.86 * (D50 / ye)^-0.55 * Fr - Co",
        formula_cita_id="HEC14.10.1#EC_10_1",
        citas_textuales=("HEC14.10.1#EC_10_1", "HEC14.10.1#CO_ENVOLVENTE",
                         "HEC14.10.1.5#RANGO", "HEC14.1#T1_1_POZA",
                         "HEC14.10.1.1#ENSAYOS")
        + (("HEC14.10.1#MAYOR_REVISTE",) if dimensionada_con_menor else ()),
        sustitucion=(
            Magnitud("ye", ye, "m", "tirante equivalente de borde, paso 6.3 "
                     "(continuidad con la velocidad de salida)",
                     cifras=CIFRAS_FINA),
            Magnitud("Fr", Fr, "-", "Froude de HEC-14 en la salida, paso 6.3",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("TW", TW, "m", "tirante del cuerpo receptor del punto",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("Co", Co, "-", f"Ec. (10.2)/(10.3), relacion «{relacion}» "
                     f"con TW/ye = {TW / ye:.3f}", cifras=CIFRAS_FACTOR),
            Magnitud("D50", D50_dim, "m",
                     (f"la piedra de hs/D50 = "
                      f"{HEC14_POZA_HS_SOBRE_D50_MIN:g} exacto: la que se "
                      f"pone ({origen_piedra}, {D50_piedra:.3f} m) da una "
                      "hoya menor que dos veces su tamaño")
                     if dimensionada_con_menor else
                     f"la piedra que se pone: {origen_piedra}"
                     + (f", subida a {HEC14_POZA_D50_SOBRE_YE_MIN:g}·ye"
                        if piedra_subida else ""),
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("hs", hs, "m",
                           f"profundidad de la poza bajo la solera de salida; "
                           f"hs/D50 = {hs / D50_dim:.2f}; reviste D50 = "
                           f"{D50_piedra:.3f} m, espesor {espesor:.3f} m "
                           f"(talud {espesor_talud:.3f} m)",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="dimensionamiento [C] de la alternativa que la "
                        "Tabla 1.1 de HEC-14 da donde el apron no llega"),
        elecciones=elecciones,
        nota_del_proyecto=(
            "LECTURA DEL PROYECTO: la piedra que se pone es la que la regla "
            "de la proteccion de salida deja rigiendo (Laushey, o la que se "
            "declare). La fuente pide elegirla entre las disponibles en la "
            "zona, que no es un dato del programa."))

    sustitucion_salida = [
        Magnitud("hs", hs, "m", "paso 6.5p", cifras=CIFRAS_MAGNITUD),
        Magnitud("Wo", Wo, "m", "ancho del conducto en la boca (B del marco "
                 "o D del tubo)", cifras=CIFRAS_MAGNITUD),
        Magnitud("Ls", Ls, "m", f"max({HEC14_POZA_LS_EN_HS:g}·hs, "
                 f"{HEC14_POZA_LS_MIN_EN_WO:g}·Wo)", cifras=CIFRAS_MAGNITUD),
        Magnitud("LB", LB0, "m", f"max({HEC14_POZA_LB_EN_HS:g}·hs, "
                 f"{HEC14_POZA_LB_MIN_EN_WO:g}·Wo)", cifras=CIFRAS_MAGNITUD),
        Magnitud("WB", WB0, "m", "Wo + (2/3)·LB (abocinado 3:1)",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("z", HEC14_POZA_TALUD_LATERAL_Z, "-",
                 "talud lateral de la poza, Figura 10.2", cifras=CIFRAS_FACTOR),
        Magnitud("Q", Q_celda, "m3/s", "caudal del barril",
                 cifras=CIFRAS_FINA)]
    if extendida:
        sustitucion_salida.append(Magnitud(
            "LB extendida", LB, "m", "alargada con el mismo abocinado hasta "
            "que Vc = Vallow", cifras=CIFRAS_MAGNITUD))
    umbral = None
    if V_admisible is None:
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="sin la velocidad admisible del cauce el paso 4 no "
                        "se contrasta")
    else:
        margen = V_admisible - Vc
        cumple = not margen < -TOL_UMBRAL_NORMATIVO
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.CUMPLE if cumple else TipoDeVeredicto.INDICADOR,
            margen=margen, unidad="m/s",
            explicacion=(f"la velocidad en la salida de la poza ({Vc:.2f} m/s)"
                         f" no supera la admisible ({V_admisible:.2f} m/s)"
                         + (", con el apron extendido" if extendida else "")))
        umbral = Umbral(
            descripcion="velocidad admisible a la salida de la poza",
            valor=V_admisible, unidad="m/s",
            cita_id="HEC14.10.1.5#SALIDA",
            caracter="PERMISO: la fuente deja tomarla como la normal del "
                     "cauce o la de un criterio de estabilidad, la mayor",
            aplicacion="LECTURA DEL PROYECTO: se toma la de la Tabla Nº 11 "
                       "del Manual para el terreno declarado del receptor (un "
                       "criterio de estabilidad), sin la normal del cauce: "
                       "lado conservador")
    paso_salida = paso(
        "F6.POZA_SALIDA",
        codigo="6.6p",
        que="Longitud, ancho y velocidad a la salida de la poza de enrocado",
        formula="Ls = max(10 hs, 3 Wo);  LB = max(15 hs, 4 Wo);  "
                "WB = Wo + (2/3) LB;  Q^2/g = [yc (WB + z yc)]^3 / "
                "(WB + 2 z yc);  Vc = Q / Ac",
        formula_cita_id="HEC14.10.1#LONGITUDES",
        citas_textuales=("HEC14.10.1#LONGITUDES", "HEC14.10.1.2#ABOCINADO",
                         "HEC14.10.1.5#SALIDA", "HEC14.10.1.5#PASO_5")
        + (("HEC14.10.1#EXTENDER",) if extendida else ()),
        sustitucion=tuple(sustitucion_salida),
        resultado=Magnitud("Vc", Vc, "m/s",
                           f"velocidad en la salida de la poza; yc = "
                           f"{yc:.3f} m, Ac = {Ac:.3f} m2; longitud total LB "
                           f"= {LB:.2f} m (poza {Ls:.2f} m + apron "
                           f"{LA:.2f} m), ancho final WB = {WB:.2f} m",
                           cifras=CIFRAS_MAGNITUD),
        umbral=umbral,
        veredicto=veredicto)
    return PozaDeEnrocado(
        y_equivalente=ye, Fr=Fr, TW=TW, Co=Co, relacion_co=relacion,
        D50_minimo=D50_minimo, D50_piedra=D50_piedra,
        D50_dimensionamiento=D50_dim,
        dimensionada_con_menor=dimensionada_con_menor,
        piedra_subida=piedra_subida, hs=hs, Wo=Wo, longitud_poza=Ls,
        longitud_apron=LA, longitud_total=LB, longitud_sin_extender=LB0,
        ancho_final=WB, espesor=espesor, espesor_talud=espesor_talud,
        yc_salida=yc, V_salida_poza=Vc, V_admisible=V_admisible,
        extendida=extendida, proteccion_adicional=proteccion_adicional,
        pasos=(paso_hs, paso_salida), avisos=tuple(avisos),
        proteccion_adicional_hasta=hasta,
        D50_proteccion_adicional=D50_adicional)


# ---------------------------------------------------------------------------
# Filtro bajo el enrocado (requisito declarado; EG-2013 511.08)
# ---------------------------------------------------------------------------

CITAS_DEL_FILTRO: Tuple[str, ...] = (
    "MC_HHD.LAMINA_05", "HEC14.10.2#FILTRO", "EG2013.511.08#EROSION",
    "EG2013.511.08#T511_06")


def requisito_de_filtro(*, pasa_200_pct: Optional[float] = None,
                        indice_plasticidad: Optional[float] = None,
                        tipo_lecho: Optional[str] = None
                        ) -> RequisitoDeFiltro:
    """
    El filtro entre el enrocado y el suelo, como REQUISITO DECLARADO.

    Quien lo sostiene: la Lámina Nº 05 del Manual dibuja el enrocado de
    salida con «FILTRO» y «CAMA DE APOYO»; HEC-14 Sec. 10.2 pide «a filter
    blanket»; y EG-2013 num. 511.08 [N] fija lo que cumple el geotextil que
    va entre un enrocado y el suelo, por la Tabla 511-06.

    La tabla entra por el pasante del tamiz N.º 200 del suelo in situ, que es
    dato del EMS (`material_lecho_salida.pasa_200_pct`). Con el, se elige la
    columna y se emite el paso; sin el, el requisito se declara igual y los
    numeros de la columna quedan en `None`: no se supone un suelo.

    Los bordes de las columnas, como la tabla los escribe: «< 15», «15-50» y
    «> 50»; el 15 y el 50 justos caen en la columna central.

    LA NOTA (5), Y QUE LLAMADA LLAMA A QUE NOTA. La tabla lleva «(5)» en el
    rotulo «Tamaño de Abertura Aparente (3) (4) (5)» y en la celda «0,22(5)»
    de la columna «>50» (PDF 1023), y dos notas, (5) a y (5) b. La primera
    lectura de T-8 aplicaba la (5) b solo a esa columna, el primer auditor
    la llevo a las tres y el segundo midio que en «15-50» eso RELAJA la
    celda (0.25 -> 0.30 mm). Rige, por decision del dueño del 2026-11-12 y
    como `Interpretacion` declarada de la cita EG2013.511.08#T511_06, la
    lectura que no relaja: el rotulo llama a la (5) a y la celda a la (5) b.
    La sostiene la Tabla 511-02 de la misma Seccion, que numera las dos notas
    por separado y pone la de los suelos cohesivos solo en la celda (cita
    EG2013.511.05#T511_02_NOTA_5). Asi:
      * (5) b, «para los suelos cohesivos con un índice de plasticidad mayor
        a 7, el valor máximo promedio por rollo es de 0.30 mm»: con un lecho
        COHESIVO declarado (`indice_plasticidad`, que solo se pasa si el
        tipo del lecho es cohesivo) e IP > 7, la abertura es 0.30 mm EN LA
        COLUMNA «>50». En «15-50» y «<15» rige la celda; en «<15», donde la
        otra lectura daria una abertura mas cerrada (0.30 contra 0.43 mm),
        la corrida lo AVISA.
      * (5) a pide un diseño especifico del geotextil en suelos
        problematicos, y nombra primero «los limos no cohesivos» (cita
        EG2013.511.08#NOTA_5A): con un lecho NO cohesivo y mas de la mitad
        pasando el tamiz N.º 200 --un suelo de grano fino sin plasticidad,
        un limo en la clasificacion SUCS: lectura del proyecto-- la
        corrida lo AVISA. Es el caso probable del Bajo Piura.
    """
    if pasa_200_pct is None:
        return RequisitoDeFiltro(
            clase_geotextil=GEOTEXTIL_EROSION_CLASE, pasa_200_pct=None,
            columna=None, permitividad_min_s1=None,
            abertura_aparente_max_mm=None,
            texto=("El enrocado lleva FILTRO entre la piedra y el suelo "
                   "(Lámina Nº 05 del Manual; HEC-14 Sec. 10.2). Si es "
                   f"geotextil: {GEOTEXTIL_EROSION_CLASE}, con la "
                   "permitividad y la abertura aparente de la Tabla 511-06 "
                   "de EG-2013 (num. 511.08). NO SE DIMENSIONA: la tabla "
                   "entra por el pasante del tamiz N.º 200 del suelo, que "
                   f"es dato del EMS (`{DATO_MATERIAL_LECHO}.pasa_200_pct`)"),
            citas=CITAS_DEL_FILTRO)
    if not (_es_numero_finito(pasa_200_pct)
            and 0 <= pasa_200_pct <= PORCENTAJE_POR_UNIDAD):
        raise DatoInvalidoError(
            f"{DATO_MATERIAL_LECHO}.pasa_200_pct", valor=pasa_200_pct,
            motivo="es un porcentaje en peso: entre 0 y 100")
    (rot_bajo, techo_bajo, *fila_baja), (rot_medio, techo_medio, *fila_media), \
        (rot_alto, _sin_techo, *fila_alta) = GEOTEXTIL_EROSION_T511_06
    if pasa_200_pct < techo_bajo:
        columna, (permitividad, abertura) = rot_bajo, fila_baja
    elif not pasa_200_pct > techo_medio:
        columna, (permitividad, abertura) = rot_medio, fila_media
    else:
        columna, (permitividad, abertura) = rot_alto, fila_alta
    if indice_plasticidad is not None:
        _exigir_no_negativo("IP", indice_plasticidad,
                            "indice de plasticidad del lecho")
    cohesivo_plastico = (indice_plasticidad is not None
                         and indice_plasticidad > GEOTEXTIL_EROSION_IP_COHESIVO)
    # La columna cuya celda lleva la llamada (5): la ultima, «> 50».
    en_la_columna_de_la_llamada = columna == rot_alto
    por_nota_5b = cohesivo_plastico and en_la_columna_de_la_llamada
    avisos_filtro: List[str] = []
    if por_nota_5b:
        abertura = GEOTEXTIL_EROSION_TAA_COHESIVO_MM
        procedencia_abertura = (
            f"nota (5) b de la Tabla 511-06: suelo cohesivo con indice de "
            f"plasticidad {indice_plasticidad:g} > "
            f"{GEOTEXTIL_EROSION_IP_COHESIVO:g} (dato del EMS), en la columna "
            f"«{columna}», cuya celda lleva la llamada (5)")
    elif cohesivo_plastico:
        procedencia_abertura = (
            f"celda de la Tabla 511-06 (valor maximo promedio por rollo). El "
            f"lecho es cohesivo con indice de plasticidad "
            f"{indice_plasticidad:g} > {GEOTEXTIL_EROSION_IP_COHESIVO:g}, "
            f"pero la nota (5) b no se aplica en la columna «{columna}»: la "
            "llamada la lleva la celda de «> 50» (ver «Lo que pone el "
            "proyecto»)")
        if abertura > GEOTEXTIL_EROSION_TAA_COHESIVO_MM:
            avisos_filtro.append(
                f"Filtro: el lecho es cohesivo con indice de plasticidad "
                f"{indice_plasticidad:g} y cae en la columna «{columna}» de "
                f"la Tabla 511-06 de EG-2013, donde rige la celda "
                f"({abertura:g} mm). La nota (5) b de la tabla se lee solo "
                "para la columna «> 50»; con la otra lectura de la llamada "
                f"la abertura maxima seria "
                f"{GEOTEXTIL_EROSION_TAA_COHESIVO_MM:.2f} mm, mas cerrada. "
                "Lo decide AASHTO M 288, que no esta en normas/")
    else:
        procedencia_abertura = (
            "celda de la Tabla 511-06 (valor maximo promedio por rollo). "
            "Su nota (5) b la lleva a 0.30 mm, en la columna «> 50», si el "
            "suelo es cohesivo con indice de plasticidad mayor que 7, y el "
            "lecho no lo declara")
    if (tipo_lecho == TIPO_LECHO_NO_COHESIVO
            and pasa_200_pct > PORCENTAJE_POR_UNIDAD / 2):
        avisos_filtro.append(
            f"Filtro: el lecho declarado es NO cohesivo con {pasa_200_pct:g} "
            "% pasando el tamiz N.º 200 --un limo, en la clasificacion SUCS--"
            ", y la nota (5) a de la Tabla 511-06 de EG-2013 pide para "
            "«" + _literal("EG2013.511.08#NOTA_5A") + "» un diseño del "
            "geotextil para el sitio especifico: los valores de la tabla son "
            "por omision y no bastan")
    citas_del_paso = CITAS_DEL_FILTRO + ("EG2013.511.08#NOTA_5A",) + (
        ("EG2013.511.05#T511_02_NOTA_5",) if cohesivo_plastico else ())
    return RequisitoDeFiltro(
        clase_geotextil=GEOTEXTIL_EROSION_CLASE, pasa_200_pct=pasa_200_pct,
        columna=columna, permitividad_min_s1=permitividad,
        abertura_aparente_max_mm=abertura,
        texto=("El enrocado lleva FILTRO entre la piedra y el suelo (Lámina "
               "Nº 05 del Manual; HEC-14 Sec. 10.2). Si es geotextil: "
               f"{GEOTEXTIL_EROSION_CLASE}; con un pasante del tamiz N.º 200 "
               f"de {pasa_200_pct:g} % (columna «{columna}» de la Tabla "
               f"511-06 de EG-2013), permitividad minima {permitividad:g} "
               f"s-1 y abertura aparente maxima {abertura:g} mm. La nota (5) "
               "de la tabla pide un diseño especifico en suelos "
               "problematicos"),
        citas=CITAS_DEL_FILTRO + ("EG2013.511.08#NOTA_5A",),
        avisos=tuple(avisos_filtro),
        paso=paso(
            "F6.FILTRO",
            codigo="6.7",
            que="Requisitos del geotextil de filtro bajo el enrocado",
            formula="columna de la Tabla 511-06 por el pasante del tamiz "
                    "N.º 200",
            formula_cita_id="EG2013.511.08#T511_06",
            citas_textuales=citas_del_paso,
            # La lectura de la llamada (5) solo cuenta cuando el lecho es
            # cohesivo con IP > 7: ahi es donde decide un numero.
            nota_del_proyecto=(_lectura("EG2013.511.08#T511_06")
                               if cohesivo_plastico else ""),
            sustitucion=(
                Magnitud("pasa N.º 200", pasa_200_pct, "%",
                         f"dato del EMS, `{DATO_MATERIAL_LECHO}.pasa_200_pct`",
                         cifras=CIFRAS_FACTOR),
                Magnitud("columna", columna, "",
                         "intervalo de la Tabla 511-06 en que cae"),
                Magnitud("abertura aparente maxima", abertura, "mm",
                         procedencia_abertura, cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("permitividad minima", permitividad, "s-1",
                               "celda de la Tabla 511-06",
                               cifras=CIFRAS_FACTOR),
            veredicto=Veredicto(
                tipo=TipoDeVeredicto.SIN_VEREDICTO,
                explicacion="requisito de especificacion para quien "
                            "suministre el geotextil; no se verifica contra "
                            "un producto")))


# ---------------------------------------------------------------------------
# Proteccion de salida completa
# ---------------------------------------------------------------------------

def _aviso_sin_terreno(donde: str, tipo_terreno: Optional[str],
                       regimen_flujo: Optional[str]) -> str:
    dato = DATO_TERRENO_RECEPTOR if donde == DONDE_SALIDA else DATO_TERRENO_ENTRADA
    faltan = [d for d, v in ((dato, tipo_terreno),
                             (DATO_REGIMEN_FLUJO, regimen_flujo)) if v is None]
    consecuencia = ("el enrocado se dimensiona igual, sin saber si el "
                    "terreno lo necesita" if donde == DONDE_SALIDA else
                    "no se sabe si la entrada necesita revestimiento")
    return (f"Proteccion de {donde}: no se comparo la velocidad con la maxima "
            "admisible del terreno (Tabla Nº 11 del Manual) porque falta "
            + " y ".join(f"'{d}'" for d in faltan)
            + f" en los datos externos del punto; {consecuencia}")


def _avisos_del_contraste(apron: ApronHEC14, *, d50: float, espesor: float,
                          longitud: float) -> Tuple[str, ...]:
    """Lo adoptado contra lo que HEC-14 daria: avisa cuando lo adoptado es MENOS."""
    avisos = []
    if d50 < apron.D50_requerido - TOL_UMBRAL_NORMATIVO:
        avisos.append(
            f"Proteccion de salida: HEC-14 Ec. (10.4) pide una piedra mayor "
            f"que Laushey (D50 = {apron.D50_requerido:.3f} m contra d50 = "
            f"{d50:.3f} m)")
    if apron.clase is None:
        avisos.append(
            f"Proteccion de salida: el D50 de HEC-14 "
            f"({apron.D50_requerido:.3f} m) supera la mayor clase de la "
            "Tabla 10.1: la salida pide un disipador diseñado por HEC-14, no "
            "un apron, o el aliviadero escalonado de la Lámina Nº 04 del "
            "Manual; ninguno se dimensiona aqui")
        return tuple(avisos)
    if longitud < apron.longitud - TOL_UMBRAL_NORMATIVO:
        avisos.append(
            f"Proteccion de salida: la longitud adoptada ({longitud:.2f} m, "
            f"'{CRITERIO_LONGITUD}') es menor que la del apron de HEC-14 "
            f"({apron.longitud:.2f} m, Tabla 10.1, clase {apron.clase})")
    if espesor < apron.espesor - TOL_UMBRAL_NORMATIVO:
        avisos.append(
            f"Proteccion de salida: el espesor adoptado ({espesor:.3f} m, "
            f"'{CRITERIO_ESPESOR}') es menor que la profundidad del apron de "
            f"HEC-14 ({apron.espesor:.3f} m, Tabla 10.1, clase {apron.clase})")
    return tuple(avisos)


def clase_hec14_de_la_piedra(*, d50: float, D: float,
                             origen: str = "Laushey, paso 6.1"
                             ) -> ClaseHEC14:
    """
    La regla de clase de la Tabla 10.1 de HEC-14 aplicada a la piedra que el
    PROYECTO pone, no a la que pide la Ec. (10.4): la clase es la primera con
    D50 mayor o igual («The class of riprap to be specified is that which has
    a D50 greater than or equal to the required size», pag. impresa 10-17), y
    la tabla le da longitud kL·D, profundidad ke·D50 de la clase y ancho final
    3·D + (2/3)·L. Hallazgo 5 (ii) de la auditoria de T-8: en A-02 la Ec.
    (10.4) pide la clase 1 y la piedra que se pone, 0.274 m, es de la clase
    4, que pide 5.4 m y 0.77 m.

    `origen` dice de donde sale esa piedra, para la procedencia del paso: el
    d50 de Laushey (con «manual», y con la envolvente cuando Laushey es el
    mayor) o el de la Ec. (10.4) (con la envolvente cuando HEC-14 pide mas).
    """
    _exigir_positivo("d50", d50, "diametro medio de la piedra, m")
    _exigir_positivo("D", D, "altura del conducto, m")
    for n_clase, d50_clase, k_long, k_esp in HEC14_TABLA_10_1:
        if not d50_clase < d50 - TOL_UMBRAL_NORMATIVO:
            break
    else:
        mayor = HEC14_TABLA_10_1[-1]
        return ClaseHEC14(d50_de_partida=d50, paso=paso(
            "F6.APRON_GEOMETRIA",
            codigo="6.6b",
            que="Clase de la Tabla 10.1 de HEC-14 para la piedra adoptada",
            formula="clase: la de D50 >= d50 adoptado",
            formula_cita_id="HEC14.10.2#T10_1",
            citas_textuales=("HEC14.10.2#T10_1",),
            sustitucion=(
                Magnitud("d50", d50, "m", origen,
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("D50 de la clase mayor", mayor[1], "m",
                         f"clase {mayor[0]} de la Tabla 10.1",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("clase", "ninguna", "",
                               "la piedra adoptada supera la mayor clase"),
            veredicto=Veredicto(
                tipo=TipoDeVeredicto.SIN_VEREDICTO,
                explicacion="la tabla no tiene clase para esta piedra")))
    longitud = k_long * D
    espesor = k_esp * d50_clase
    ancho = (HEC14_APRON_ANCHO_EN_LA_BOCA_EN_D * D
             + HEC14_APRON_ABOCINADO_POR_LONGITUD * longitud)
    return ClaseHEC14(
        d50_de_partida=d50, clase=n_clase, D50_clase=d50_clase,
        longitud=longitud, espesor=espesor, ancho_final=ancho,
        paso=paso(
            "F6.APRON_GEOMETRIA",
            codigo="6.6b",
            que="Longitud y profundidad que la Tabla 10.1 de HEC-14 da a la "
                "piedra que el proyecto pone",
            formula="clase: la de D50 >= d50;  L = kL * D;  "
                    "e = ke * D50_clase;  W = 3 * D + (2/3) * L",
            formula_cita_id="HEC14.10.2#T10_1",
            citas_textuales=("HEC14.10.2#T10_1", "HEC14.10.2#PROFUNDIDAD"),
            sustitucion=(
                Magnitud("d50", d50, "m", f"{origen}: la piedra que el "
                         "proyecto pone", cifras=CIFRAS_MAGNITUD),
                Magnitud("clase", n_clase, "", "la primera de la Tabla 10.1 "
                         "con D50 mayor o igual que el d50 adoptado"),
                Magnitud("D50_clase", d50_clase, "m", f"clase {n_clase}",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("kL", k_long, "-", "longitud de la clase, en alturas "
                         "del conducto", cifras=CIFRAS_FACTOR),
                Magnitud("ke", k_esp, "-", "profundidad de la clase, en D50",
                         cifras=CIFRAS_FACTOR),
                Magnitud("D", D, "m", "altura del conducto («D is the "
                         "culvert rise»)", cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("L", longitud, "m",
                               f"longitud; profundidad e = {espesor:.3f} m; "
                               f"ancho al final W = {ancho:.3f} m",
                               cifras=CIFRAS_MAGNITUD),
            veredicto=Veredicto(
                tipo=TipoDeVeredicto.SIN_VEREDICTO,
                explicacion="guia de la fuente aplicada a la piedra que el "
                            "proyecto pone: se compara con lo adoptado en el "
                            "paso 6.2")))


def _avisos_de_la_piedra(clase: ClaseHEC14, *, espesor: float,
                         longitud: float) -> Tuple[str, ...]:
    if clase.clase is None:
        return (f"Proteccion de salida: la piedra adoptada (d50 = "
                f"{clase.d50_de_partida:.3f} m) supera la mayor clase de la "
                "Tabla 10.1 de HEC-14: la salida pide un disipador diseñado",)
    cortos = []
    if longitud < clase.longitud - TOL_UMBRAL_NORMATIVO:
        cortos.append(f"la longitud ({longitud:.2f} m contra "
                      f"{clase.longitud:.2f} m)")
    if espesor < clase.espesor - TOL_UMBRAL_NORMATIVO:
        cortos.append(f"el espesor ({espesor:.3f} m contra "
                      f"{clase.espesor:.3f} m)")
    if not cortos:
        return ()
    return (f"Proteccion de salida: con la piedra que el proyecto pone (d50 = "
            f"{clase.d50_de_partida:.3f} m, clase {clase.clase} de la Tabla "
            "10.1 de HEC-14) lo adoptado queda corto en "
            + " y en ".join(cortos),)


def _aviso_espesor_bajo_el_piso(espesor: float, d50: float) -> Tuple[str, ...]:
    """
    Hallazgo 5 (i) de la auditoria de T-8: el multiplo adoptado queda bajo el
    piso de HEC-14 SIEMPRE, no solo cuando el valor absoluto es menor que el
    de la clase que pide la Ec. (10.4) (en A-02 no se avisaba).
    """
    if not espesor < HEC14_ESPESOR_MIN_EN_D50 * d50 - TOL_UMBRAL_NORMATIVO:
        return ()
    return (f"Proteccion de salida: el espesor rige como {espesor / d50:.2f} "
            f"veces el d50 ({espesor:.3f} m), bajo el piso de "
            f"{HEC14_ESPESOR_MIN_EN_D50:g} veces de HEC-14: «"
            + _literal("HEC14.10.2#PROFUNDIDAD") + "» (Sec. 10.2) y «"
            + _literal("HEC14.10.1#DOS_D50") + "» (Sec. 10.1). Ver "
            f"'{CRITERIO_REGLA}'",)


def _aviso_el_terreno_resistiria(admisible: VelocidadAdmisible) -> str:
    """
    Decision 6 del dueño (2026-11-12): «sin enrocado» nunca es una conclusion
    del programa. Cuando la velocidad no supera la admisible, el contraste
    INFORMA y la proteccion se mantiene; suprimirla exige lo que el HDS-5
    nombra, y el aviso lo cita del registro.
    """
    return (f"Proteccion de salida: la velocidad de salida "
            f"({admisible.V:.2f} m/s) no supera la maxima admisible del "
            f"terreno ({admisible.V_admisible:.2f} m/s, Tabla Nº 11): segun "
            "la tabla el terreno la resistiria. La proteccion se calcula y "
            "se MANTIENE: suprimirla queda sujeto a inspeccion de campo, "
            "porque el HDS-5 (num. 5.3.2, pag. impresa 5.11) dice: «"
            + _literal("HDS5_3ED.5.3.2#PRACTICA") + "»")


def _aviso_el_contraste_no_concluye(admisible: VelocidadAdmisible) -> str:
    """H2 de la segunda auditoria: con una cota inferior no se concluye."""
    return (f"Proteccion de salida: el contraste con la Tabla Nº 11 no "
            f"concluye. La velocidad de salida ({admisible.V:.2f} m/s) no "
            f"supera la admisible del terreno ({admisible.V_admisible:.2f} "
            "m/s), pero es una cota inferior de la real: se tomo al tirante "
            "critico y en el borde el tirante es menor (HEC-14 num. 3.1.3). "
            "No se afirma que el terreno la resista; la proteccion se "
            "calcula y se mantiene")


def _con_la_velocidad_al_critico(resultado: ResultadoHidraulico) -> bool:
    """
    La velocidad de salida es una COTA INFERIOR de la real: control de
    salida (o barril horizontal) con el TW bajo el critico, primera viñeta
    de HDS-5 3.1.6, DONDE LAS FIGURAS 3.3 Y 3.4 DE HEC-14 NO DIERON EL
    TIRANTE DE BORDE y M4 se quedo en el critico. Lo decide M4 y lo dice en
    `ResultadoHidraulico.V_salida_cota_inferior` (cierre de T8-08); hasta
    entonces esta funcion lo infería de y_salida = y_c, que era toda la
    primera viñeta.
    """
    return bool(resultado.V_salida_cota_inferior)


def _aviso_tirante_de_borde(resultado: ResultadoHidraulico) -> Tuple[str, ...]:
    """
    Hallazgo 9 de la primera auditoria de T-8 y H2 de la segunda, CERRADOS
    por T8-08: bajo control de salida con el TW bajo el critico, M4 mide la
    velocidad al tirante de BORDE de las Figuras 3.3 y 3.4 de HEC-14
    (`M4.tirante_de_borde`). Este aviso queda para lo que la figura no
    cubre --otra forma, fuera de su familia de curvas, una lectura que no
    queda bajo el critico--, donde M4 se quedo en el critico con el permiso
    de la fuente («not conservative, but is acceptable», num. 3.1.3) y V, el
    Froude y el d50 son COTAS INFERIORES. El motivo lo da M4
    (`ResultadoHidraulico.borde.motivo`); aqui no se recalcula.
    """
    if not _con_la_velocidad_al_critico(resultado):
        return ()
    motivo = ("" if resultado.borde is None or not resultado.borde.motivo
              else f" ({resultado.borde.motivo})")
    return ("Proteccion de salida: la velocidad de salida se tomo con el "
            "tirante critico (HDS-5 num. 3.1.6) porque el TW queda bajo el y "
            "las Figuras 3.3 y 3.4 de HEC-14 no dan aqui el tirante de borde"
            + motivo + ". HEC-14 num. 3.1.3: «" + _literal("HEC14.3.1.3#BORDE")
            + "»; en el borde el tirante es MENOR que el critico y la "
            "velocidad MAYOR, de modo que V, el Froude y el d50 de Laushey "
            "son una cota inferior: «" + _literal("HEC14.3.1.3#OTRAS_FORMAS")
            + "»",)


# La lectura del proyecto con que se cruza el terreno declarado del receptor
# (Tabla Nº 11) con el lecho declarado del EMS: las filas de arcilla son de
# suelo cohesivo, las de arena, grava y piedra de suelo granular; la ceniza
# volcanica y los dos materiales graduados «desde arcilla» y «desde limo» no
# se cruzan. Solo alimenta un AVISO de incoherencia (hallazgo 9).
#
# LO QUE LA SEGUNDA AUDITORIA DEJO ABIERTO Y NO SE PUEDE CERRAR CON normas/:
# las filas «Arcilla arenosa (no coloidal)» y «Arcilla limosa (no coloidal)»
# podrian ser francos («loam») traducidos como arcilla --la tabla cita el
# «Manual de Carreteras de California», que no esta en el repositorio--, y
# entonces no serian cohesivas. La clasificacion sigue el NOMBRE impreso, y
# por eso el aviso pide revisar los dos datos y no afirma cual esta mal.
TERRENOS_COHESIVOS_T11 = ("arcilla_arenosa_no_coloidal",
                          "arcilla_limosa_no_coloidal", "arcilla_fina",
                          "arcilla_dura_coloidal")
TERRENOS_GRANULARES_T11 = ("arena_fina_no_coloidal", "grava_fina",
                           "graduado_grava", "graduado_grava_gruesa",
                           "graduado_grava_a_piedras_menor_15cm",
                           "graduado_grava_a_piedras_mayor_20cm")


def _aviso_terreno_contra_lecho(tipo_terreno: Optional[str],
                                tipo_lecho: Optional[str]) -> Tuple[str, ...]:
    if tipo_terreno is None or tipo_lecho is None:
        return ()
    granular = tipo_terreno in TERRENOS_GRANULARES_T11
    cohesivo = tipo_terreno in TERRENOS_COHESIVOS_T11
    if (tipo_lecho == TIPO_LECHO_COHESIVO and granular) or \
            (tipo_lecho == TIPO_LECHO_NO_COHESIVO and cohesivo):
        return (f"Proteccion de salida: el terreno declarado del receptor "
                f"(«{TERRENO_T11_ROTULO[tipo_terreno]}», fila de la Tabla Nº "
                f"11) no concuerda con el lecho declarado del EMS "
                f"('{tipo_lecho}'): la velocidad admisible y la hoya de "
                "socavacion se calcularon con dos suelos distintos. Revise "
                f"'{DATO_TERRENO_RECEPTOR}' y '{DATO_MATERIAL_LECHO}', que "
                "son datos de sitio y deben salir de la misma lectura",)
    return ()


class _LoQueRige(NamedTuple):
    """Lo que la regla declarada deja rigiendo en la proteccion de salida."""
    d50: float
    espesor: float
    longitud: float
    clase: Optional[ClaseHEC14]     # la de la piedra que el proyecto pone
    paso: Optional[PasoDeMemoria]   # 6.6c, solo si se formo la envolvente
    avisos: Tuple[str, ...]
    rige_la_envolvente: bool


def _avisos_de_la_poza(poza: PozaDeEnrocado, *, d50: float, espesor: float,
                       longitud: float) -> Tuple[str, ...]:
    """
    --- VE-4g --- Lo que rige contra lo que la poza de enrocado de HEC-14
    pide, con la regla «manual»: avisa donde lo adoptado es MENOS.
    """
    cortos = []
    if d50 < poza.D50_piedra - TOL_UMBRAL_NORMATIVO:
        cortos.append(f"la piedra ({d50:.3f} m contra {poza.D50_piedra:.3f} "
                      "m, el limite de los ensayos)")
    if espesor < poza.espesor - TOL_UMBRAL_NORMATIVO:
        cortos.append(f"el espesor ({espesor:.3f} m contra "
                      f"{poza.espesor:.3f} m)")
    if longitud < poza.longitud_total - TOL_UMBRAL_NORMATIVO:
        cortos.append(f"la longitud ({longitud:.2f} m contra "
                      f"{poza.longitud_total:.2f} m)")
    if not cortos:
        return ()
    return (f"Proteccion de salida: con la regla '{CRITERIO_REGLA}' en "
            f"«{REGLA_MANUAL}» lo adoptado queda corto frente a la poza de "
            "enrocado de HEC-14 (Sec. 10.1, profundidad "
            f"{poza.hs:.2f} m) en " + " y en ".join(cortos),)


def _avisos_del_tw_alto(tw: ProteccionTWAlto, *, d50: float, espesor: float,
                        longitud: float) -> Tuple[str, ...]:
    """--- VE-5 (lote m6) --- Con «manual»: avisa donde lo adoptado es menos."""
    cortos = []
    if d50 < tw.D50 - TOL_UMBRAL_NORMATIVO:
        cortos.append(f"la piedra ({d50:.3f} m contra {tw.D50:.3f} m)")
    if espesor < tw.espesor - TOL_UMBRAL_NORMATIVO:
        cortos.append(f"el espesor ({espesor:.3f} m contra "
                      f"{tw.espesor:.3f} m)")
    if longitud < tw.longitud - TOL_UMBRAL_NORMATIVO:
        cortos.append(f"la longitud ({longitud:.2f} m contra "
                      f"{tw.longitud:.2f} m)")
    if not cortos:
        return ()
    return (f"Proteccion de salida: con la regla '{CRITERIO_REGLA}' en "
            f"«{REGLA_MANUAL}» lo adoptado queda corto frente a la proteccion "
            "con el tirante del receptor alto (HEC-14 Figura 10.3 y Ec. "
            "10.6) en " + " y en ".join(cortos),)


def _regla_con_el_tw_alto(*, regla: str, d50_laushey: float,
                          mult_espesor: float, longitud_adoptada: float,
                          tw_alto: ProteccionTWAlto) -> _LoQueRige:
    """
    --- VE-5 (lote m6) --- La envolvente con la proteccion del TW alto:
    piedra = max(Laushey, Ec. 10.6); espesor = max(k·d50, 2·D50 de la Ec.
    10.6); longitud = max(adoptada, la de la Figura 10.3).
    """
    rige_hec = tw_alto.D50 > d50_laushey + TOL_UMBRAL_NORMATIVO
    d50 = tw_alto.D50 if rige_hec else d50_laushey
    e_multiplo = mult_espesor * d50
    espesor = max(e_multiplo, tw_alto.espesor)
    longitud = max(longitud_adoptada, tw_alto.longitud)
    paso_regla = paso(
        "F6.GEOMETRIA_ADOPTADA",
        codigo="6.6c",
        que="Piedra, espesor y longitud que rigen por la regla declarada "
            "(envolvente del Manual y de la proteccion con el TW alto)",
        formula="d50 = max(d50 Laushey, D50 Ec. 10.6);  e = max(k * d50, "
                "2 * D50 Ec. 10.6);  L = max(L adoptada, L Figura 10.3)",
        citas_textuales=("MC_HHD.4.1.1.3.7c", "HEC14.10.3#EC_10_6",
                         "HEC14.10.1.3#FIGURA_10_3"),
        sustitucion=(
            Magnitud("d50 Laushey", d50_laushey, "m", "paso 6.1",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("D50 Ec. 10.6", tw_alto.D50, "m", "paso 6.5t",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("k * d50", e_multiplo, "m",
                     f"criterio '{CRITERIO_ESPESOR}' [A] (k = "
                     f"{mult_espesor:g}) sobre la piedra que rige",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("e HEC-14", tw_alto.espesor, "m", "paso 6.5t",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("L adoptada", longitud_adoptada, "m",
                     f"criterio '{CRITERIO_LONGITUD}' [A]",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("L Figura 10.3", tw_alto.longitud, "m", "paso 6.5t",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("e", espesor, "m",
                           f"espesor que rige; piedra d50 = {d50:.3f} m; "
                           f"longitud L = {longitud:.2f} m",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="envolvente del Manual y de HEC-14 con el TW alto: "
                        "en cada magnitud rige el mayor"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="regla de la piedra, el espesor y la longitud de "
                          "la proteccion de salida",
            valor=regla,
            entre=tuple(ca.CRITERIOS[CRITERIO_REGLA].sensibilidad),
            de_donde=f"el criterio adoptado '{CRITERIO_REGLA}' [A]",
            por_que="decision del dueño del proyecto (2026-11-12): la "
                    "envolvente es el lado conservador",
            clave_criterio=CRITERIO_REGLA),))
    aviso = (f"Proteccion de salida: el tirante del receptor supera la "
             f"clave y rige la envolvente con HEC-14 Figura 10.3 y Ec. 10.6 "
             f"('{CRITERIO_REGLA}'): piedra d50 {d50_laushey:.3f} -> "
             f"{d50:.3f} m, espesor {mult_espesor * d50_laushey:.3f} -> "
             f"{espesor:.3f} m, longitud {longitud_adoptada:.2f} -> "
             f"{longitud:.2f} m (hasta que la velocidad del eje baja a "
             f"{tw_alto.V_admisible:.2f} m/s)")
    return _LoQueRige(d50, espesor, longitud, None, paso_regla, (aviso,), True)


def _regla_con_la_poza(*, regla: str, d50_laushey: float, mult_espesor: float,
                       longitud_adoptada: float,
                       poza: PozaDeEnrocado) -> _LoQueRige:
    """
    --- VE-4g --- La envolvente cuando el apron no es evaluable y la poza de
    enrocado de HEC-14 Sec. 10.1 si (marco, conducto de mas de 60 in):
        piedra    d50 = max(d50 de Laushey, la que reviste la poza)
        espesor   max(k·d50, 2·D50 de la poza)
        longitud  max(longitud adoptada, LB de la poza)
    La poza se reviste con la piedra de Laushey salvo que quede bajo el
    limite de los ensayos (0.1·ye), y entonces con ese limite.
    """
    rige_poza = poza.D50_piedra > d50_laushey + TOL_UMBRAL_NORMATIVO
    d50 = poza.D50_piedra if rige_poza else d50_laushey
    e_multiplo = mult_espesor * d50
    espesor = max(e_multiplo, poza.espesor)
    longitud = max(longitud_adoptada, poza.longitud_total)
    paso_regla = paso(
        "F6.GEOMETRIA_ADOPTADA",
        codigo="6.6c",
        que="Piedra, espesor y longitud que rigen por la regla declarada "
            "(envolvente del Manual y de la poza de enrocado de HEC-14)",
        formula="d50 = max(d50 Laushey, D50 poza);  e = max(k * d50, "
                "2 * D50 poza);  L = max(L adoptada, LB poza)",
        citas_textuales=("MC_HHD.4.1.1.3.7c", "HEC14.10.1#EC_10_1",
                         "HEC14.10.1#DOS_D50", "HEC14.10.1#LONGITUDES"),
        sustitucion=(
            Magnitud("d50 Laushey", d50_laushey, "m", "paso 6.1",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("D50 poza", poza.D50_piedra, "m",
                     "la que reviste la poza, paso 6.5p",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("k * d50", e_multiplo, "m",
                     f"espesor por el criterio '{CRITERIO_ESPESOR}' [A] "
                     f"(k = {mult_espesor:g}) sobre la piedra que rige",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("e poza", poza.espesor, "m",
                     f"{HEC14_ESPESOR_MIN_EN_D50:g}·D50 en el piso y los "
                     "lados de la poza (num. 10.1.4)", cifras=CIFRAS_MAGNITUD),
            Magnitud("L adoptada", longitud_adoptada, "m",
                     f"criterio '{CRITERIO_LONGITUD}' [A]",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("LB poza", poza.longitud_total, "m",
                     "longitud total de la poza, paso 6.6p",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("e", espesor, "m",
                           f"espesor que rige; piedra d50 = {d50:.3f} m; "
                           f"longitud L = {longitud:.2f} m",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="envolvente de lo que da el Manual (Laushey y lo "
                        "adoptado) y de la poza de enrocado de HEC-14: en "
                        "cada magnitud rige el mayor"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="regla de la piedra, el espesor y la longitud de "
                          "la proteccion de salida",
            valor=regla,
            entre=tuple(ca.CRITERIOS[CRITERIO_REGLA].sensibilidad),
            de_donde=f"el criterio adoptado '{CRITERIO_REGLA}' [A]",
            por_que="decision del dueño del proyecto (2026-11-12): la "
                    "envolvente es el lado conservador; donde el apron no "
                    "llega, la envolvente se forma con la poza",
            clave_criterio=CRITERIO_REGLA),),
        nota_del_proyecto=(
            f"La poza se excava {poza.hs:.2f} m bajo la solera de salida y "
            f"se abre a {poza.ancho_final:.2f} m; en el talud de la salida "
            f"del conducto el espesor sube a {poza.espesor_talud:.3f} m "
            "(num. 10.1.4)."))
    aviso = (f"Proteccion de salida: el apron de HEC-14 no llega a este "
             f"conducto y rige la envolvente con la poza de enrocado de "
             f"HEC-14 Sec. 10.1 ('{CRITERIO_REGLA}'): piedra d50 "
             f"{d50_laushey:.3f} -> {d50:.3f} m, espesor "
             f"{mult_espesor * d50_laushey:.3f} -> {espesor:.3f} m, longitud "
             f"{longitud_adoptada:.2f} -> {longitud:.2f} m; profundidad de "
             f"la poza {poza.hs:.2f} m bajo la solera de salida")
    return _LoQueRige(d50, espesor, longitud, None, paso_regla, (aviso,), True)


def _regla_de_la_proteccion(*, regla: str, d50_laushey: float,
                            mult_espesor: float, longitud_adoptada: float,
                            apron: Optional[ApronHEC14],
                            poza: Optional[PozaDeEnrocado] = None,
                            tw_alto: Optional[ProteccionTWAlto] = None
                            ) -> _LoQueRige:
    """
    La regla de 'regla_espesor_longitud_proteccion_salida': que piedra, que
    espesor y que longitud RIGEN.

    «manual»: el d50 de Laushey, el espesor k·d50 y la longitud adoptada. Son
    los numeros de antes de la decision del 2026-11-12, exactos.

    «envolvente_hec14» (el archivo), cuando el apron de HEC-14 es evaluable:
        piedra    d50 = max(d50 de Laushey, D50 de la Ec. (10.4))
        clase     la de la Tabla 10.1 para ESA piedra (D50 mayor o igual)
        espesor   max(k·d50, ke·D50 de la clase)
        longitud  max(longitud adoptada, kL·D de la clase)
    Basta la clase de la piedra que rige: esa piedra no es menor que la que
    pide la Ec. (10.4), y en la Tabla 10.1 la longitud y la profundidad
    crecen con la clase, de modo que cubre tambien la clase del apron.

    SI LA PIEDRA QUE RIGE NO CABE EN LA TABLA 10.1 (mas de 0.55 m), la tabla
    no da ni profundidad ni longitud. LECTURA DEL PROYECTO, declarada en el
    paso y en el aviso: se toman como COTAS INFERIORES el limite que la
    fuente escribe para las piedras mayores, 2.0 veces el D50 («to a limit of
    2.0D50 for the larger riprap sizes»), y la longitud de su ultima clase,
    8·D; y se avisa que la salida pide un disipador y que eso no es un diseño.

    Si HEC-14 NO es evaluable en el punto (`apron` None: marco, varios
    barriles, TW sobre la clave, conducto de mas de 60 in, falta un dato),
    rige Laushey con lo adoptado, y se avisa.
    """
    _exigir_texto_de(CRITERIO_REGLA, regla, (REGLA_MANUAL, REGLA_ENVOLVENTE),
                     f"es '{REGLA_MANUAL}' o '{REGLA_ENVOLVENTE}'")
    espesor_adoptado = mult_espesor * d50_laushey
    if regla == REGLA_MANUAL:
        clase = (None if apron is None else
                 clase_hec14_de_la_piedra(d50=d50_laushey, D=apron.D))
        avisos_poza = (() if poza is None else _avisos_de_la_poza(
            poza, d50=d50_laushey, espesor=espesor_adoptado,
            longitud=longitud_adoptada))
        avisos_tw = (() if tw_alto is None else _avisos_del_tw_alto(
            tw_alto, d50=d50_laushey, espesor=espesor_adoptado,
            longitud=longitud_adoptada))
        return _LoQueRige(d50_laushey, espesor_adoptado, longitud_adoptada,
                          clase, None, avisos_poza + avisos_tw, False)
    if apron is None and tw_alto is not None:
        return _regla_con_el_tw_alto(
            regla=regla, d50_laushey=d50_laushey, mult_espesor=mult_espesor,
            longitud_adoptada=longitud_adoptada, tw_alto=tw_alto)
    if apron is None and poza is not None:
        return _regla_con_la_poza(
            regla=regla, d50_laushey=d50_laushey, mult_espesor=mult_espesor,
            longitud_adoptada=longitud_adoptada, poza=poza)
    if apron is None:
        return _LoQueRige(
            d50_laushey, espesor_adoptado, longitud_adoptada, None, None,
            (f"Proteccion de salida: la regla '{CRITERIO_REGLA}' pide la "
             "envolvente con HEC-14 y HEC-14 no es evaluable en este punto: "
             "rige el d50 de Laushey con el espesor y la longitud "
             "adoptados",), False)
    rige_hec14 = apron.D50_requerido > d50_laushey + TOL_UMBRAL_NORMATIVO
    d50 = apron.D50_requerido if rige_hec14 else d50_laushey
    origen = ("HEC-14 Ec. (10.4), paso 6.5" if rige_hec14
              else "Laushey, paso 6.1")
    clase = clase_hec14_de_la_piedra(d50=d50, D=apron.D, origen=origen)
    e_multiplo = mult_espesor * d50
    if clase.clase is not None:
        e_tabla, L_tabla = clase.espesor, clase.longitud
        de_la_tabla = f"clase {clase.clase} de la Tabla 10.1"
        fuera = ()
    else:
        _n, _d50_mayor, kL_mayor, _ke = HEC14_TABLA_10_1[-1]
        e_tabla = HEC14_ESPESOR_MIN_EN_D50 * d50
        L_tabla = kL_mayor * apron.D
        de_la_tabla = (f"fuera de la Tabla 10.1: cotas inferiores, "
                       f"{HEC14_ESPESOR_MIN_EN_D50:g} veces el d50 y la "
                       f"longitud de la ultima clase, {kL_mayor:g}·D")
        fuera = (f"Proteccion de salida: la piedra que rige (d50 = {d50:.3f} "
                 "m) no cabe en la Tabla 10.1 de HEC-14, que no da "
                 "profundidad ni longitud para ella: el espesor y la "
                 "longitud impresos son COTAS INFERIORES, lectura del "
                 "proyecto sobre el limite de la fuente («"
                 + _literal("HEC14.10.2#PROFUNDIDAD") + "») y la longitud de "
                 "su ultima clase, y no un diseño. La salida pide un "
                 "disipador",)
    espesor = max(e_multiplo, e_tabla)
    longitud = max(longitud_adoptada, L_tabla)
    paso_regla = paso(
        "F6.GEOMETRIA_ADOPTADA",
        codigo="6.6c",
        que="Piedra, espesor y longitud que rigen por la regla declarada "
            "(envolvente del Manual y de HEC-14)",
        formula="d50 = max(d50 Laushey, D50 Ec. 10.4);  "
                "e = max(k * d50, e HEC-14);  L = max(L adoptada, L HEC-14)",
        citas_textuales=("MC_HHD.4.1.1.3.7c", "HEC14.10.2#EC_10_4",
                         "HEC14.10.2#T10_1", "HEC14.10.2#PROFUNDIDAD"),
        sustitucion=(
            Magnitud("d50 Laushey", d50_laushey, "m", "paso 6.1",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("D50 Ec. 10.4", apron.D50_requerido, "m", "paso 6.5",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("d50", d50, "m", f"el mayor de los dos: {origen}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("k * d50", e_multiplo, "m",
                     f"espesor por el criterio '{CRITERIO_ESPESOR}' [A] "
                     f"(k = {mult_espesor:g}) sobre la piedra que rige",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("e HEC-14", e_tabla, "m", de_la_tabla,
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("L adoptada", longitud_adoptada, "m",
                     f"criterio '{CRITERIO_LONGITUD}' [A]",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("L HEC-14", L_tabla, "m", de_la_tabla,
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("e", espesor, "m",
                           f"espesor que rige; piedra d50 = {d50:.3f} m; "
                           f"longitud L = {longitud:.2f} m",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="envolvente de lo que da el Manual (Laushey y lo "
                        "adoptado) y de lo que da HEC-14 (Ec. 10.4 y Tabla "
                        "10.1): en cada magnitud rige el mayor"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="regla de la piedra, el espesor y la longitud de "
                          "la proteccion de salida",
            valor=regla,
            entre=tuple(ca.CRITERIOS[CRITERIO_REGLA].sensibilidad),
            de_donde=f"el criterio adoptado '{CRITERIO_REGLA}' [A]",
            por_que="decision del dueño del proyecto (2026-11-12): ninguna "
                    "de las dos fuentes queda por debajo de la otra en todos "
                    "los casos, y la envolvente es el lado conservador",
            clave_criterio=CRITERIO_REGLA),))
    piedra = (f"piedra d50 {d50_laushey:.3f} -> {d50:.3f} m (rige la Ec. "
              "(10.4) de HEC-14, que pide mas que Laushey)" if rige_hec14 else
              f"piedra d50 = {d50:.3f} m (rige Laushey; la Ec. (10.4) de "
              f"HEC-14 pide {apron.D50_requerido:.3f} m)")
    aviso = (f"Proteccion de salida: rige la envolvente con HEC-14 "
             f"('{CRITERIO_REGLA}'): {piedra}, espesor "
             f"{espesor_adoptado:.3f} -> {espesor:.3f} m, longitud "
             f"{longitud_adoptada:.2f} -> {longitud:.2f} m ({de_la_tabla})")
    return _LoQueRige(d50, espesor, longitud, clase, paso_regla,
                      (aviso,) + fuera, True)


def _remite_a_la_poza(seccion: Seccion, resultado: ResultadoHidraulico
                      ) -> bool:
    """
    --- VE-4g --- Si el apron de la Sec. 10.2 falla por un limite para el que
    la Tabla 1.1 de HEC-14 ofrece la POZA de la Sec. 10.1: el marco (la Ec.
    10.4 es «for circular culverts»), el conducto de mas de 60 in (nota 8,
    que solo cuelga del apron) y varios barriles (que la poza tampoco cubre:
    se intenta para que el aviso lo diga). El TW sobre 1.0·D de un tubo no
    remite a la poza: la Sec. 10.2 lo manda a su Figura 10.3.
    """
    return (not isinstance(seccion, SeccionCircular)
            or seccion.altura > HEC14_APRON_ALTURA_MAX_M + TOL_UMBRAL_NORMATIVO
            or resultado.numero_celdas != 1)


def _tw_alto_de_la_fase(*, V: Magnitud, resultado: ResultadoHidraulico,
                        V_admisible: Optional[float],
                        avisos: List[str]) -> Optional[ProteccionTWAlto]:
    """
    --- VE-5 (lote m6) --- El TW sobre 1.0·D de un tubo de hasta 60 in, un
    barril: la Figura 10.3 y la Ec. (10.6), como la Sec. 10.2 manda. Lo que
    no se pueda evaluar (sin admisible, o mas alla de la figura) es AVISO, y
    rige Laushey con lo adoptado.
    """
    try:
        return proteccion_tw_alto_hec14(
            V=V, Q_celda=resultado.Q_celda_m3s, TW=resultado.TW_m,
            V_admisible=V_admisible)
    except (MetodoNoEvaluableError, DatoFaltanteError) as error:
        detalle = (f"{error.motivo}. Hace falta: {error.procedimiento}"
                   if isinstance(error, MetodoNoEvaluableError)
                   else f"falta '{error.campo}' ({error.detalle})")
        avisos.append(
            f"Proteccion de salida: la proteccion con el tirante del "
            f"receptor alto (HEC-14 Figura 10.3 y Ec. 10.6) NO se evaluo -- "
            f"{detalle}. Rige el d50 de Laushey")
        return None


def _poza_de_la_fase(*, V: Magnitud, resultado: ResultadoHidraulico,
                     seccion: Seccion, d50_laushey: float,
                     V_admisible: Optional[float],
                     avisos: List[str]) -> Optional[PozaDeEnrocado]:
    """
    --- VE-4g --- La poza de la Fase 6, revestida con la piedra de Laushey
    (la que el Manual pone). Dentro de la Fase 6 un `MetodoNoEvaluableError`
    NO viaja como `Bloqueo`: se convierte en aviso y rige Laushey con lo
    adoptado (CLAUDE.md, «Excepciones»).
    """
    try:
        return poza_de_enrocado_hec14(
            V=V, Q_celda=resultado.Q_celda_m3s, seccion=seccion,
            TW=resultado.TW_m, y_salida=resultado.y_salida_m,
            d50_piedra=d50_laushey, origen_piedra="Laushey, paso 6.1",
            V_admisible=V_admisible, numero_celdas=resultado.numero_celdas)
    except MetodoNoEvaluableError as error:
        avisos.append(
            f"Proteccion de salida: la poza de enrocado de HEC-14 (Sec. "
            f"10.1) NO se evaluo tampoco -- {error.motivo}. Hace falta: "
            f"{error.procedimiento}. Rige el d50 de Laushey")
        return None


def proteccion_salida(*, V: Magnitud,
                      resultado: Optional[ResultadoHidraulico] = None,
                      seccion: Optional[Seccion] = None,
                      tipo_terreno: Optional[str] = None,
                      regimen_flujo: Optional[str] = None,
                      pasa_200_pct: Optional[float] = None,
                      indice_plasticidad_lecho: Optional[float] = None,
                      tipo_lecho: Optional[str] = None
                      ) -> ProteccionSalida:
    """
    La proteccion de SALIDA entera: d50 de Laushey, apron de HEC-14, lo que
    rige por la regla declarada, y el Froude de la salida, el contraste con
    la velocidad admisible del terreno y el filtro.

    `V` ES UNA `Magnitud` CON PROCEDENCIA, y no un float, desde EXT-3 (PC-04,
    EXT-M-01): la velocidad que entra a Laushey es la de SALIDA por HDS-5
    3.1.6, que M4 emite en `ResultadoHidraulico.V_salida` --bajo control de
    salida, Q entre el area al tirante min(D, max(TW, y_c)); bajo control de
    entrada, la del tirante normal con n_min--. La procedencia la trae el
    numero, y esta funcion la imprime sin reescribirla. Con el TW bajo el
    critico y el control de salida, M4 la mide desde T8-08 al tirante de
    BORDE de HEC-14 (Figuras 3.3 y 3.4) y desde T8-09 toma la mayor de esa y
    `V_erosion`; solo donde la figura no da el borde se queda en el critico,
    y esa velocidad es una COTA INFERIOR (`V_salida_cota_inferior`): se
    AVISA y el contraste con la Tabla Nº 11 no concluye.

    LA PROTECCION SE CALCULA Y SE MANTIENE SIEMPRE (decision 6 del dueño,
    2026-11-12): el d50, el espesor y la longitud llevan numero en todos los
    casos. Lo que cambia es que rige:

      * regla «envolvente_hec14» (el archivo), con `resultado` y `seccion`:
        piedra = el mayor de Laushey y de la Ec. (10.4); espesor y longitud =
        el mayor de lo adoptado ('espesor_proteccion_salida',
        'longitud_proteccion_salida') y de la Tabla 10.1 para esa piedra
        (`_regla_de_la_proteccion`, paso 6.6c).
      * regla «manual»: Laushey y lo adoptado, numero por numero como antes
        de esa decision; HEC-14 se imprime al lado y se avisa donde pide mas.
      * donde HEC-14 no es evaluable (marco, TW sobre la clave, conducto de
        mas de 60 in, varios barriles, o una llamada solo con `V`): Laushey
        y lo adoptado, con aviso.

    LO QUE LOS DATOS DE SITIO AÑADEN:
      * `tipo_terreno` y `regimen_flujo` -> la velocidad de salida se compara
        con la admisible de la Tabla Nº 11. El contraste INFORMA en
        `requerida`: True = la supera; False = no la supera, y se avisa que
        el terreno la resistiria segun la tabla y que suprimir la proteccion
        queda sujeto a inspeccion de campo (HDS-5 num. 5.3.2); None = falta
        el dato, o la velocidad es una cota inferior y el contraste no
        concluye. En ninguno de los tres casos se deja de dimensionar.
      * `pasa_200_pct`, `indice_plasticidad_lecho` (solo si el lecho es
        cohesivo) y `tipo_lecho` (datos del EMS) -> el geotextil de filtro
        (Tabla 511-06 de EG-2013) y el cruce del terreno con el lecho.

    Devuelve siempre TRES advertencias: las dos de siempre y la del alcance,
    que dice cual de las dos reglas rigio.
    """
    _exigir_velocidad(V, "proteccion_salida")
    pasos: List[PasoDeMemoria] = []
    avisos: List[str] = []

    froude = None
    al_critico = False
    if resultado is not None and seccion is not None:
        froude = froude_salida(V=V, Q_celda=resultado.Q_celda_m3s,
                               seccion=seccion, y_salida=resultado.y_salida_m,
                               y_critico=resultado.y_critico)
        al_critico = _con_la_velocidad_al_critico(resultado)
        avisos.extend(_aviso_tirante_de_borde(resultado))

    admisible = None
    if tipo_terreno is not None and regimen_flujo is not None:
        admisible = velocidad_admisible_del_cauce(
            V=V, tipo_terreno=tipo_terreno, regimen_flujo=regimen_flujo,
            donde=DONDE_SALIDA, cota_inferior=al_critico)
        if admisible.supera:
            avisos.append("Proteccion de salida: "
                          + admisible.paso.veredicto.explicacion)
        elif not admisible.concluyente:
            avisos.append(_aviso_el_contraste_no_concluye(admisible))
        else:
            avisos.append(_aviso_el_terreno_resistiria(admisible))
    else:
        avisos.append(_aviso_sin_terreno(DONDE_SALIDA, tipo_terreno,
                                         regimen_flujo))
    avisos.extend(_aviso_terreno_contra_lecho(tipo_terreno, tipo_lecho))
    requerida = (None if admisible is None or not admisible.concluyente
                 else admisible.supera)

    d50_laushey = laushey_d50(V=V.valor)
    mult_espesor = ca.valor(CRITERIO_ESPESOR)
    espesor_adoptado = mult_espesor * d50_laushey
    longitud_adoptada = ca.valor(CRITERIO_LONGITUD)   # [A] declarado
    regla = ca.valor(CRITERIO_REGLA)
    paso_laushey = _paso_laushey(V, d50_laushey, espesor_adoptado,
                                 mult_espesor)
    pasos.append(paso_laushey)
    pasos.append(_paso_geometria_adoptada(
        d50_laushey, mult_espesor, espesor_adoptado, longitud_adoptada,
        regla))
    if froude is not None:
        pasos.append(froude.paso)
    if admisible is not None:
        pasos.append(admisible.paso)

    apron = poza = tw_alto = None
    if resultado is not None and seccion is not None:
        faltan = [nombre for nombre, valor in (
            ("el tirante del receptor (TW)", resultado.TW_m),
            ("el tirante critico", resultado.y_critico)) if valor is None]
        if faltan:
            # H15: un resultado armado sin pasar por M4. La pieza de HEC-14
            # no se puede evaluar; el d50 de Laushey, que solo pide V, si.
            avisos.append("Proteccion de salida: el apron de HEC-14 NO se "
                          "evaluo -- el resultado hidraulico no trae "
                          + " ni ".join(faltan) + ". Rige el d50 de Laushey")
        else:
            try:
                apron = apron_hec14(
                    Q_celda=resultado.Q_celda_m3s, seccion=seccion,
                    TW=resultado.TW_m, y_salida=resultado.y_salida_m,
                    y_critico=resultado.y_critico,
                    numero_celdas=resultado.numero_celdas)
            except MetodoNoEvaluableError as error:
                avisos.append(
                    f"Proteccion de salida: el apron de HEC-14 NO se evaluo "
                    f"-- {error.motivo}. Hace falta: {error.procedimiento}")
                if not _remite_a_la_poza(seccion, resultado):
                    tw_alto = _tw_alto_de_la_fase(
                        V=V, resultado=resultado,
                        V_admisible=(None if admisible is None
                                     else admisible.V_admisible),
                        avisos=avisos)
                else:
                    poza = _poza_de_la_fase(
                        V=V, resultado=resultado, seccion=seccion,
                        d50_laushey=laushey_d50(V=V.valor),
                        V_admisible=(None if admisible is None
                                     else admisible.V_admisible),
                        avisos=avisos)
    if apron is not None and not apron.regimen_determinado:
        avisos.append(
            "Proteccion de salida: regimen no determinado para el apron de "
            "HEC-14 -- el resultado hidraulico no trae el tirante de salida "
            "y no se pudo decidir si aplica el ajuste de la Ec. (10.5): el "
            "D50 se calculo SIN ajuste y, si el flujo fuera supercritico, "
            "seria mayor")
    rige = _regla_de_la_proteccion(
        regla=regla, d50_laushey=d50_laushey, mult_espesor=mult_espesor,
        longitud_adoptada=longitud_adoptada, apron=apron, poza=poza,
        tw_alto=tw_alto)
    if apron is not None:
        pasos.extend(apron.pasos)
    if tw_alto is not None:
        pasos.extend(tw_alto.pasos)
    if poza is not None:
        pasos.extend(poza.pasos)
        avisos.extend(poza.avisos)
    if rige.clase is not None:
        pasos.append(rige.clase.paso)
    if rige.paso is not None:
        pasos.append(rige.paso)
    avisos.extend(rige.avisos)
    # LOS AVISOS DEL CONTRASTE SALEN BAJO LAS DOS REGLAS (H1): hablan de lo
    # que RIGE contra lo que HEC-14 daria. Con la envolvente lo que rige no
    # queda por debajo y callan solos; el del disipador --el D50 de la Ec.
    # (10.4) no cabe en la Tabla 10.1-- sale siempre.
    if apron is not None:
        avisos.extend(_avisos_del_contraste(
            apron, d50=rige.d50, espesor=rige.espesor,
            longitud=rige.longitud))
        if rige.clase is not None and rige.clase.clase != apron.clase \
                and not rige.rige_la_envolvente:
            # Con la misma clase el aviso del apron ya lo dijo, con las
            # mismas cifras: no se repite. Con la envolvente, la clase de la
            # piedra que rige ya entro en el espesor y la longitud.
            avisos.extend(_avisos_de_la_piedra(
                rige.clase, espesor=rige.espesor, longitud=rige.longitud))
    avisos.extend(_aviso_espesor_bajo_el_piso(rige.espesor, rige.d50))
    # El filtro SIN el pasante del tamiz N.º 200 no añade un aviso propio: lo
    # dice ya `ADVERTENCIA_FALTA_FILTRO`, que viaja con toda proteccion
    # dimensionada, y `filtro.texto` nombra el dato que falta.
    filtro = requisito_de_filtro(pasa_200_pct=pasa_200_pct,
                                 indice_plasticidad=indice_plasticidad_lecho,
                                 tipo_lecho=tipo_lecho)
    if filtro.paso is not None:
        pasos.append(filtro.paso)
    avisos.extend(filtro.avisos)

    return ProteccionSalida(
        paso=paso_laushey,
        d50=rige.d50,
        espesor=rige.espesor,
        longitud=rige.longitud,
        V=V.valor,
        criterio_espesor=CRITERIO_ESPESOR,
        criterio_longitud=CRITERIO_LONGITUD,
        advertencias=(ADVERTENCIAS_PROTECCION_SALIDA_POZA
                      if rige.rige_la_envolvente and poza is not None
                      else ADVERTENCIAS_PROTECCION_SALIDA_ENVOLVENTE
                      if rige.rige_la_envolvente
                      else ADVERTENCIAS_PROTECCION_SALIDA),
        numeral=NUMERAL_LAUSHEY,
        requerida=requerida, froude=froude, velocidad_admisible=admisible,
        apron=apron, filtro=filtro, pasos=tuple(pasos), avisos=tuple(avisos),
        clase_de_la_piedra=rige.clase, regla_espesor_longitud=regla,
        espesor_adoptado=espesor_adoptado, longitud_adoptada=longitud_adoptada,
        d50_laushey=d50_laushey, rige_la_envolvente=rige.rige_la_envolvente,
        poza=poza, tw_alto=tw_alto,
    )


# ---------------------------------------------------------------------------
# Proteccion de la ENTRADA (INF-5.1.13)
# ---------------------------------------------------------------------------

def velocidad_en_la_entrada(resultado: ResultadoHidraulico) -> Optional[Magnitud]:
    """
    La velocidad en la boca de entrada, de lo que M4 YA resolvio; no se
    recalcula nada.

      * Bajo control de SALIDA, y siempre con el barril horizontal, el
        remanso llega a la entrada: es la velocidad de la seccion de entrada
        del perfil de la lamina (`PerfilLamina.V_entrada_m_s`).
      * Bajo control de ENTRADA: la CRITICA del paso 4.2. HDS-5 num. 3.1.3
        (pag. impresa 3.2): el flujo pasa por el tirante critico justo aguas
        abajo de la boca. Con la entrada sumergida la boca trabaja como
        orificio y la fuente no da la velocidad en ella: la critica es la de
        la seccion de control, y la procedencia lo dice.

    `None` si el resultado no trae ninguna de las dos (un resultado armado
    sin pasar por M4): no se inventa una.
    """
    perfil = resultado.perfil
    por_perfil = (resultado.control_gobernante is ControlGobernante.SALIDA
                  or resultado.sin_tirante_normal)
    if por_perfil and perfil is not None and perfil.V_entrada_m_s is not None:
        return Magnitud(
            "V_entrada", perfil.V_entrada_m_s, "m/s",
            "M4, perfil de la lamina de agua (paso 4.3c): velocidad en la "
            "seccion de ENTRADA del barril, a donde llega el remanso",
            cifras=CIFRAS_MAGNITUD)
    if resultado.V_critica_m_s is not None:
        if por_perfil:
            # El perfil no llega a la boca (o el resultado no lo trae): no
            # hay velocidad de remanso en la entrada que leer, y la critica
            # es la referencia que queda. Se dice, no se disfraza.
            procedencia = (
                "M4, paso 4.2: velocidad CRITICA, Q_celda / A_c. El control "
                "gobernante es el de SALIDA, pero el perfil de la lamina no "
                "llega a la entrada (paso 4.3c): no hay velocidad de remanso "
                "en la boca y se toma la critica como referencia")
        else:
            procedencia = (
                "M4, paso 4.2: velocidad CRITICA, Q_celda / A_c. Bajo control "
                "de entrada el flujo pasa por el tirante critico justo aguas "
                "abajo de la boca (HDS-5 num. 3.1.3, pag. impresa 3.2); con "
                "la entrada sumergida es la de la seccion de control, no la "
                "de la vena contraida")
        return Magnitud("V_entrada", resultado.V_critica_m_s, "m/s",
                        procedencia, cifras=CIFRAS_MAGNITUD)
    return None


def proteccion_entrada(*, resultado: ResultadoHidraulico,
                       tipo_embocadura: str = EMBOCADURA_CABEZAL_RECTO,
                       tipo_terreno: Optional[str] = None,
                       regimen_flujo: Optional[str] = None
                       ) -> ProteccionEntrada:
    """
    La proteccion de la ENTRADA: velocidad en la boca, revestimiento adoptado
    y lo que hay que proteger segun la embocadura (INF-5.1.13).

    Las fuentes: el Manual, num. 4.1.1.3.7 c), recomienda proteger el cauce
    cuando la velocidad en la entrada es alta y nombra tres revestimientos;
    sus Láminas 02, 02-A y 03 dibujan la entrada con piedra emboquillada y
    uña, sin dimensiones; el HDS-5 num. 5.3.1 enumera las medidas. NINGUNA da
    una formula ni una medida para la entrada, y este paso no las inventa:
    publica la velocidad, compara con la Tabla Nº 11 si el punto declara el
    terreno del cauce de aproximacion (`tipo_terreno`, `regimen_flujo`), y
    declara el revestimiento del criterio [A] 'tipo_proteccion_entrada'.

    `tipo_embocadura` es una clave de `EMBOCADURAS`. Desde T-7a el pipeline
    pasa la del punto (`M9.embocadura_del_punto`, criterio
    'embocadura_cabezal' [A]); el default de la firma sigue siendo el
    cabezal recto para quien llame a esta funcion suelta.
    """
    _exigir_texto_de("tipo_embocadura", tipo_embocadura, EMBOCADURAS,
                     "no es un tipo de embocadura que la proteccion de "
                     "entrada conozca: " + ", ".join(EMBOCADURAS))
    revestimiento = ca.valor(CRITERIO_REVESTIMIENTO_ENTRADA)
    elementos = EMBOCADURAS[tipo_embocadura]
    avisos: List[str] = []
    V = velocidad_en_la_entrada(resultado)
    if V is None:
        return ProteccionEntrada(
            tipo_embocadura=tipo_embocadura, V_entrada=None,
            revestimiento=revestimiento,
            criterio_revestimiento=CRITERIO_REVESTIMIENTO_ENTRADA,
            elementos=elementos,
            avisos=("Proteccion de entrada: el resultado hidraulico no trae "
                    "la velocidad en la boca; no se compara con la admisible "
                    "del terreno",))
    _exigir_positivo("V_entrada", V.valor, "velocidad en la boca, m/s")
    eleccion = EleccionDeProyecto(
        que_se_adopto="revestimiento de la entrada",
        valor=revestimiento,
        entre=tuple(ca.CRITERIOS[CRITERIO_REVESTIMIENTO_ENTRADA].sensibilidad),
        de_donde=f"el criterio adoptado '{CRITERIO_REVESTIMIENTO_ENTRADA}' [A]",
        por_que="el num. 4.1.1.3.7 c) del Manual enumera tres revestimientos "
                "sin preferir ninguno, y sus Láminas 02, 02-A y 03 dibujan "
                "la entrada con piedra emboquillada",
        cita_id="MC_HHD.LAMINA_02",
        clave_criterio=CRITERIO_REVESTIMIENTO_ENTRADA)
    nota = ("LO QUE SE PROTEGE CON ESTA EMBOCADURA (" + tipo_embocadura
            + "), lectura del proyecto sobre las medidas que el HDS-5 num. "
            "5.3.1 enumera: " + "; ".join(elementos) + ". Las Láminas del "
            "Manual llevan las dimensiones como letras o como «VARIABLE»: "
            "la longitud y el espesor del zampeado y el dentellon son "
            "geometria del cabezal, no de este paso.")
    admisible = None
    if tipo_terreno is not None and regimen_flujo is not None:
        admisible = velocidad_admisible_del_cauce(
            V=V, tipo_terreno=tipo_terreno, regimen_flujo=regimen_flujo,
            donde=DONDE_ENTRADA)
        if admisible.supera:
            avisos.append("Proteccion de entrada: "
                          + admisible.paso.veredicto.explicacion)
    else:
        avisos.append(_aviso_sin_terreno(DONDE_ENTRADA, tipo_terreno,
                                         regimen_flujo))
    paso_entrada = paso(
        "F6.ENTRADA",
        codigo="6.9",
        que="Proteccion de la entrada: velocidad en la boca y revestimiento "
            "adoptado",
        formula="V_entrada = velocidad en la seccion de entrada del barril",
        citas_textuales=("MC_HHD.4.1.1.3.7c#PROTECCION",
                         "MC_HHD.4.1.1.3.7c#REVESTIMIENTOS",
                         "HDS5_3ED.5.3.1#ENTRADA",
                         "HDS5_3ED.3.1.3#CRITICO_EN_LA_ENTRADA"),
        sustitucion=(
            Magnitud("embocadura", tipo_embocadura, "",
                     "tipo de embocadura del punto, del criterio "
                     "'embocadura_cabezal' [A] (T-7a: "
                     "`M9.embocadura_del_punto`)"),),
        resultado=V,
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="ninguna fuente de normas/ pone umbral ni formula a "
                        "la proteccion de la entrada; la comparacion con la "
                        "Tabla Nº 11, si el terreno esta declarado, va en el "
                        "paso 6.8"),
        elecciones=(eleccion,),
        nota_del_proyecto=nota)
    pasos = (paso_entrada,) if admisible is None else (admisible.paso,
                                                       paso_entrada)
    return ProteccionEntrada(
        tipo_embocadura=tipo_embocadura, V_entrada=V.valor,
        revestimiento=revestimiento,
        criterio_revestimiento=CRITERIO_REVESTIMIENTO_ENTRADA,
        elementos=elementos,
        requerida=None if admisible is None else admisible.supera,
        velocidad_admisible=admisible, pasos=pasos, avisos=tuple(avisos))


# ---------------------------------------------------------------------------
# Socavacion local a la salida (HEC-14, Capitulo 5)
# ---------------------------------------------------------------------------

DIMENSIONES_DE_LA_HOYA = ("profundidad", "ancho", "longitud")
_SIMBOLO = {"profundidad": "hs", "ancho": "Ws", "longitud": "Ls"}
_CODIGO = {"profundidad": "6.11", "ancho": "6.12", "longitud": "6.13"}


def coeficiente_de_tabla(tabla, x: float, dimension: str, lectura: str) -> float:
    """
    Lee Ch (Tabla 5.2) o Cs (Tabla 5.3) de HEC-14 para la abscisa `x`.

    En una fila, la fila. ENTRE dos filas, segun la lectura declarada en
    'lectura_coeficientes_socavacion_hec14': la envolvente (el mayor de los
    dos vecinos) o la interpolacion lineal. De la ultima abscisa en adelante,
    la ultima fila: en la Tabla 5.3 es la fila «>7», que vale para toda
    pendiente mayor; en la 5.2 quien llama rechaza antes lo que pase de 4.
    """
    if lectura not in (LECTURA_ENVOLVENTE, LECTURA_INTERPOLADA):
        raise DatoInvalidoError(
            CRITERIO_LECTURA_TABLAS, valor=lectura,
            motivo=f"es '{LECTURA_ENVOLVENTE}' o '{LECTURA_INTERPOLADA}'")
    _exigir_no_negativo("abscisa", x, "entrada de la tabla")
    abscisas = [fila[0] for fila in tabla]
    valores = [fila[1][dimension] for fila in tabla]
    if not x < abscisas[-1]:
        return valores[-1]
    for i in range(len(abscisas) - 1):
        x0, x1 = abscisas[i], abscisas[i + 1]
        if x0 <= x < x1:
            v0, v1 = valores[i], valores[i + 1]
            if not x > x0 + TOL_UMBRAL_NORMATIVO:
                return v0
            if lectura == LECTURA_ENVOLVENTE:
                return max(v0, v1)
            return v0 + (v1 - v0) * (x - x0) / (x1 - x0)
    raise DatoInvalidoError("abscisa", valor=x,
                            motivo="por debajo de la primera fila de la tabla")


def tension_tractiva_critica(*, Sv_Pa: float, IP: float) -> float:
    """
    τc = 0.001·(Sv + αu)·tan(30 + 1.73·PI), HEC-14 Ec. (5.4), pag. impresa
    5-7. Sv en N/m2 (Pa), αu = 8630 N/m2 (SI) y el angulo en GRADOS; τc sale
    en N/m2. La fuente limita las ecuaciones de suelo cohesivo a un indice de
    plasticidad de 5 a 16: fuera, `MetodoNoEvaluableError`.
    """
    _exigir_positivo("Sv_Pa", Sv_Pa, "resistencia al corte saturada, N/m2")
    # El MISMO dominio que la puerta de carga (`servicio`): un indice de
    # plasticidad no es negativo, y 0 es un suelo sin plasticidad. Fuera del
    # rango 5-16 de la fuente es METODO NO EVALUABLE, que la Fase 6 convierte
    # en aviso, y nunca un dato invalido que bloquee la fase (hallazgo 3 de
    # la auditoria de T-8: IP = 0 entraba por la carga y aqui bloqueaba).
    _exigir_no_negativo("IP", IP, "indice de plasticidad")
    if not (HEC14_SOCAVACION_IP_MIN - TOL_UMBRAL_NORMATIVO <= IP
            <= HEC14_SOCAVACION_IP_MAX + TOL_UMBRAL_NORMATIVO):
        raise MetodoNoEvaluableError(
            "hoya de socavacion en suelo cohesivo (HEC-14 Ec. 5.2)",
            procedimiento="un estudio de socavacion del cauce para ese "
                          "suelo, declarado como "
                          f"`{DATO_SOCAVACION_DECLARADA}`",
            motivo=f"el indice de plasticidad del lecho es {IP:g} y la fuente "
                   "limita las Ec. (5.2) y (5.3) a arcillas arenosas con "
                   f"indice de {HEC14_SOCAVACION_IP_MIN:g} a "
                   f"{HEC14_SOCAVACION_IP_MAX:g}",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    angulo = math.radians(HEC14_TAU_C_ANGULO_BASE_GRADOS
                          + HEC14_TAU_C_GRADOS_POR_IP * IP)
    return (HEC14_TAU_C_COEFICIENTE * (Sv_Pa + HEC14_TAU_C_ALFA_U_SI)
            * math.tan(angulo))


def hoya_de_socavacion_hec14(*, Q_celda: float, seccion: Seccion, S: float,
                             V: Magnitud, altura_caida_m: float,
                             material: MaterialLecho,
                             duracion_pico_min: Optional[float] = None,
                             numero_celdas: int = 1) -> HoyaDeSocavacion:
    """
    Hoya de socavacion local a la salida por HEC-14, Capitulo 5 «Estimating
    Scour at Culvert Outlets» (pags. impresas 5-1 a 5-10).

    Suelo NO cohesivo, Ec. (5.1), cualquier forma de conducto:
        [hs, Ws, Ls] / Rc = Cs·Ch·(α / σ^(1/3))·[Q / (g^0.5·Rc^2.5)]^β·(t/316)^θ
    con Rc el radio hidraulico a seccion LLENA, σ = (D84/D16)^0.5 y t en
    minutos.

    Suelo cohesivo, Ec. (5.2) circular y (5.3) otras formas:
        [hs, Ws, Ls] / D  = Cs·Ch·α ·(ρV²/τc)^β·(t/316)^θ
        [hs, Ws, Ls] / ye = Cs·Ch·αe·(ρV²/τc)^β·(t/316)^θ,  ye = (A/2)^0.5
    con V la velocidad media de salida y τc de la Ec. (5.4).

    α, β, θ (y αe) de las Tablas 5.1 y 5.4; Ch (altura de la salida sobre el
    lecho, en alturas del conducto) de la Tabla 5.2; Cs (pendiente, en %) de
    la Tabla 5.3. La profundidad maxima se da a 0.4·Ls de la salida.

    LO QUE EL METODO ES Y NO ES (num. 5, pag. 5-1): la hoya MAXIMA de los
    ensayos («worst-case»), de la socavacion LOCAL; no incluye la degradacion
    general del cauce. El tirante del receptor no entra.

    ENTRADAS QUE NO SE INVENTAN: `material` es el suelo del lecho, del EMS
    (`DatoFaltanteError` si le falta lo que su ecuacion pide). La duracion
    del caudal pico es `duracion_pico_min` si el punto la declara; si no, el
    criterio [A] 'duracion_caudal_pico_socavacion_min': 360 minutos por
    decision del dueño (2026-11-12), porque los 30 que la fuente recomienda
    «lacking this knowledge» solo alcanzan, segun la misma fuente, de 2/3 a
    3/4 de la hoya maxima. La hoya de la otra punta de la ventana, 30 min,
    viaja al lado como sensibilidad.

    FUERA DE RANGO -> `MetodoNoEvaluableError`, nunca extrapolado: caida
    mayor de 4 alturas (fin de la Tabla 5.2), indice de plasticidad fuera de
    5-16, o mas de un barril (la fuente no trata la descarga de barriles
    contiguos y el proyecto no la extiende). Una duracion menor de 30 minutos
    (los exponentes «are not applicable») NO detiene: la hoya crece con t y
    se estima con 30 min como COTA SUPERIOR, con la marca
    `duracion_acotada` (auditoria de T-8).
    """
    _exigir_positivo("Q_celda", Q_celda, "caudal de un barril, m3/s")
    _exigir_no_negativo("S", S, "pendiente del conducto, m/m")
    _exigir_no_negativo("altura_caida_m", altura_caida_m,
                        "altura del fondo de la salida sobre el lecho, m")
    _exigir_velocidad(V, "hoya_de_socavacion_hec14")
    que = "hoya de socavacion a la salida (HEC-14 Cap. 5)"
    estudio = ("un estudio de socavacion del cauce, declarado como "
               f"`{DATO_SOCAVACION_DECLARADA}`")
    if numero_celdas != 1:
        raise MetodoNoEvaluableError(
            que, procedimiento=estudio,
            motivo=f"el cruce tiene {numero_celdas} barriles; las ecuaciones "
                   "de HEC-14 Cap. 5 son para la descarga de un conducto y "
                   "el proyecto no las extiende a barriles contiguos",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    if material.tipo not in TIPOS_DE_LECHO:
        raise DatoFaltanteError(
            f"{DATO_MATERIAL_LECHO}.tipo",
            detalle="hay que decir si el lecho es '"
                    + "' o '".join(TIPOS_DE_LECHO)
                    + "': de eso depende la ecuacion de HEC-14 (dato del EMS)")
    por_criterio = duracion_pico_min is None
    acotada = False
    t_alternativa = None
    if por_criterio:
        t = ca.valor(CRITERIO_DURACION_PICO)
        # La sensibilidad se da contra la OTRA punta de la ventana del
        # criterio: los 30 min que la fuente recomienda cuando rige el
        # techo, y el techo si alguien declara un valor menor.
        piso, techo = ca.CRITERIOS[CRITERIO_DURACION_PICO].sensibilidad
        t_alternativa = (piso if not t < techo - TOL_UMBRAL_NORMATIVO
                         else techo)
        origen_t = (f"criterio '{CRITERIO_DURACION_PICO}' [A], por falta del "
                    "dato: adopcion del proyecto dentro de la ventana "
                    f"{piso:g}-{techo:g} min. HEC-14 recomienda "
                    f"{HEC14_SOCAVACION_T_MINIMO_MIN:g} min «lacking this "
                    "knowledge» (num. 5.1.2), que es el extremo NO "
                    "conservador: la hoya crece con t")
    else:
        t = duracion_pico_min
        origen_t = f"dato externo del punto, `{DATO_DURACION_PICO}`"
    _exigir_positivo("duracion", t, "duracion del caudal pico, minutos")
    if t < HEC14_SOCAVACION_T_MINIMO_MIN - TOL_UMBRAL_NORMATIVO:
        # Los exponentes de tiempo «are not applicable for the first 30
        # minutes» (5.1.2), y la hoya CRECE con t: la de 30 minutos es una
        # cota SUPERIOR de la del dato, y se estima con ella en vez de dejar
        # el punto sin estimacion (hallazgo 1 de la auditoria de T-8: con 20
        # min el punto quedaba «sin dato» y sin el dato salia la de 30).
        origen_t = (f"dato externo del punto ({t:g} min), menor que "
                    f"{HEC14_SOCAVACION_T_MINIMO_MIN:g}: los exponentes no "
                    "aplican y la hoya crece con t, de modo que se estima "
                    f"con {HEC14_SOCAVACION_T_MINIMO_MIN:g} min como COTA "
                    "SUPERIOR")
        t = HEC14_SOCAVACION_T_MINIMO_MIN
        acotada = True
    altura = seccion.altura
    Hd = altura_caida_m / altura
    Hd_max = HEC14_SOCAVACION_CH[-1][0]
    if Hd > Hd_max + TOL_UMBRAL_NORMATIVO:
        raise MetodoNoEvaluableError(
            que, procedimiento=estudio,
            motivo=f"la salida queda {altura_caida_m:.2f} m sobre el lecho "
                   f"({Hd:.2f} alturas del conducto) y la Tabla 5.2 de "
                   f"HEC-14 termina en {Hd_max:g}",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    Hd = min(Hd, Hd_max)
    lectura = ca.valor(CRITERIO_LECTURA_TABLAS)
    S_pct = S * PORCENTAJE_POR_UNIDAD
    Cs = {d: coeficiente_de_tabla(HEC14_SOCAVACION_CS, S_pct, d, lectura)
          for d in DIMENSIONES_DE_LA_HOYA}
    Ch = {d: coeficiente_de_tabla(HEC14_SOCAVACION_CH, Hd, d, lectura)
          for d in DIMENSIONES_DE_LA_HOYA}
    factor_t = t / HEC14_SOCAVACION_T_REFERENCIA_MIN
    comunes = (
        Magnitud("t", t, "min", origen_t, cifras=CIFRAS_FACTOR),
        Magnitud("S", S_pct, "%", "pendiente del conducto con que corrio el "
                 "diseño", cifras=CIFRAS_FACTOR),
        Magnitud("Hd", Hd, "-",
                 f"altura del fondo de la salida sobre el lecho "
                 f"({altura_caida_m:.3f} m: cota de salida menos cota de "
                 f"fondo del receptor) entre la altura del conducto "
                 f"({altura:.3f} m)", cifras=CIFRAS_FACTOR))
    lectura_txt = (f"lectura «{lectura}» (criterio "
                   f"'{CRITERIO_LECTURA_TABLAS}' [A]) cuando el dato cae "
                   "entre dos filas")
    veredicto = Veredicto(
        tipo=TipoDeVeredicto.SIN_VEREDICTO,
        explicacion="estimacion del peor caso de la socavacion LOCAL; no "
                    "incluye la degradacion general del cauce")
    pasos: List[PasoDeMemoria] = []
    dims: Dict[str, float] = {}

    if material.tipo == TIPO_LECHO_NO_COHESIVO:
        if material.D84_m is None or material.D16_m is None:
            raise DatoFaltanteError(
                f"{DATO_MATERIAL_LECHO}.D84_m / D16_m",
                detalle="la Ec. (5.1) de HEC-14 pide σ = (D84/D16)^0.5 del "
                        "lecho: los dos diametros salen del analisis "
                        "granulometrico del EMS")
        _exigir_positivo("D84_m", material.D84_m, "diametro D84 del lecho, m")
        _exigir_positivo("D16_m", material.D16_m, "diametro D16 del lecho, m")
        if not material.D84_m >= material.D16_m:
            raise DatoInvalidoError(
                DATO_MATERIAL_LECHO, valor=(material.D84_m, material.D16_m),
                motivo="D84 no puede ser menor que D16: son percentiles de "
                       "la misma curva granulometrica")
        sigma = math.sqrt(material.D84_m / material.D16_m)
        Rc = seccion.radio_hidraulico_lleno
        grupo = Q_celda / (
            math.sqrt(G) * Rc ** HEC14_EXPONENTE_LONGITUD_DEL_CAUDAL_ADIMENSIONAL)
        metodo = "HEC-14 Ec. (5.1), suelo no cohesivo"
        for d in DIMENSIONES_DE_LA_HOYA:
            alfa, beta, theta = HEC14_SOCAVACION_NO_COHESIVO[d]
            dims[d] = (Cs[d] * Ch[d]
                       * (alfa / sigma ** HEC14_SOCAVACION_EXPONENTE_SIGMA)
                       * grupo ** beta * factor_t ** theta * Rc)
            pasos.append(paso(
                "F6.SOCAVACION",
                codigo=_CODIGO[d],
                que=f"Hoya de socavacion a la salida: {d} "
                    "(suelo no cohesivo)",
                formula=f"{_SIMBOLO[d]} = Cs * Ch * (alfa / sigma^(1/3)) * "
                        "[Q / (g^0.5 * Rc^2.5)]^beta * (t / 316)^theta * Rc",
                formula_cita_id="HEC14.5.1#EC_5_1",
                citas_textuales=("HEC14.5.1#EC_5_1", "HEC14.5#PEOR_CASO",
                                 "HEC14.5.1.1#T5_1", "HEC14.5.1.4#T5_2",
                                 "HEC14.5.1.5#T5_3", "HEC14.5.1.2#T30",
                                 "HEC14.5.1.2#DOS_TERCIOS"),
                sustitucion=(
                    Magnitud("Q", Q_celda, "m3/s", "caudal del barril, "
                             "Q_celda", cifras=CIFRAS_FINA),
                    Magnitud("Rc", Rc, "m", "radio hidraulico del conducto a "
                             "seccion LLENA", cifras=CIFRAS_FINA),
                    Magnitud("sigma", sigma, "-",
                             f"(D84/D16)^0.5 con D84 = {material.D84_m:g} m y "
                             f"D16 = {material.D16_m:g} m, dato del EMS "
                             f"(`{DATO_MATERIAL_LECHO}`)",
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("alfa, beta, theta",
                             f"{alfa:g}, {beta:g}, {theta:g}", "",
                             f"Tabla 5.1, fila de {d}"),
                    Magnitud("Cs", Cs[d], "-", "Tabla 5.3, por la pendiente; "
                             + lectura_txt, cifras=CIFRAS_FACTOR),
                    Magnitud("Ch", Ch[d], "-", "Tabla 5.2, por la altura de "
                             "la salida sobre el lecho; " + lectura_txt,
                             cifras=CIFRAS_FACTOR),
                    Magnitud("g", G, "m/s2", "`constantes_fisicas.G`",
                             cifras=CIFRAS_FACTOR)) + comunes,
                resultado=Magnitud(_SIMBOLO[d], dims[d], "m",
                                   f"{d} de la hoya de socavacion local",
                                   cifras=CIFRAS_MAGNITUD),
                veredicto=veredicto,
                nota_del_proyecto=_nota_de_sensibilidad(
                    d, dims[d], theta, t, t_alternativa)))
    else:
        if material.IP is None or material.Sv_Pa is None:
            raise DatoFaltanteError(
                f"{DATO_MATERIAL_LECHO}.IP / Sv_Pa",
                detalle="las Ec. (5.2) a (5.4) de HEC-14 piden el indice de "
                        "plasticidad y la resistencia al corte saturada del "
                        "lecho: los dos salen de ensayos del EMS")
        tau_c = tension_tractiva_critica(Sv_Pa=material.Sv_Pa, IP=material.IP)
        numero_de_corte = RHO_AGUA * V.valor ** 2 / tau_c
        pasos.append(paso(
            "F6.SOCAVACION",
            codigo="6.10",
            que="Tension tractiva critica del lecho cohesivo",
            formula="tau_c = 0.001 * (Sv + alfa_u) * tan(30 + 1.73 * PI)",
            formula_cita_id="HEC14.5.2#EC_5_4",
            citas_textuales=("HEC14.5.2#EC_5_4", "HEC14.5.2#RANGO_IP"),
            sustitucion=(
                Magnitud("Sv", material.Sv_Pa, "N/m2",
                         "resistencia al corte saturada del lecho, dato del "
                         f"EMS (`{DATO_MATERIAL_LECHO}`)",
                         cifras=CIFRAS_FACTOR),
                Magnitud("PI", material.IP, "-",
                         "indice de plasticidad del lecho, dato del EMS",
                         cifras=CIFRAS_FACTOR),
                Magnitud("alfa_u", HEC14_TAU_C_ALFA_U_SI, "N/m2",
                         "constante de la Ec. (5.4) en SI; la fuente da "
                         "tambien 180 lb/ft2, que no se usa",
                         cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("tau_c", tau_c, "N/m2",
                               "tension tractiva critica; el angulo de la "
                               "tangente va en grados",
                               cifras=CIFRAS_MAGNITUD),
            veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                                explicacion="magnitud intermedia")))
        if isinstance(seccion, SeccionCircular):
            escala, simbolo_escala, columna = altura, "D", 0
            procedencia_escala = "diametro del conducto"
            metodo = "HEC-14 Ec. (5.2), suelo cohesivo, conducto circular"
        else:
            escala = math.sqrt(Q_celda / V.valor / 2)
            simbolo_escala, columna = "ye", len(HEC14_SOCAVACION_COHESIVO["profundidad"]) - 1
            procedencia_escala = ("tirante equivalente (A/2)^0.5, con A = "
                                  "Q_celda / V el area de flujo a la salida")
            metodo = "HEC-14 Ec. (5.3), suelo cohesivo, conducto no circular"
        for d in DIMENSIONES_DE_LA_HOYA:
            fila = HEC14_SOCAVACION_COHESIVO[d]
            alfa, beta, theta = fila[columna], fila[1], fila[2]
            dims[d] = (Cs[d] * Ch[d] * alfa * numero_de_corte ** beta
                       * factor_t ** theta * escala)
            pasos.append(paso(
                "F6.SOCAVACION",
                codigo=_CODIGO[d],
                que=f"Hoya de socavacion a la salida: {d} (suelo cohesivo)",
                formula=f"{_SIMBOLO[d]} = Cs * Ch * alfa * (rho * V^2 / "
                        f"tau_c)^beta * (t / 316)^theta * {simbolo_escala}",
                formula_cita_id="HEC14.5.2#EC_5_2",
                citas_textuales=("HEC14.5.2#EC_5_2", "HEC14.5.2#RANGO_IP",
                                 "HEC14.5#PEOR_CASO", "HEC14.5.1.4#T5_2",
                                 "HEC14.5.1.5#T5_3", "HEC14.5.1.2#T30",
                                 "HEC14.5.1.2#DOS_TERCIOS"),
                sustitucion=(
                    Magnitud("V", V.valor, "m/s", V.procedencia,
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("rho", RHO_AGUA, "kg/m3",
                             "`constantes_fisicas.RHO_AGUA`", cifras=0),
                    Magnitud("tau_c", tau_c, "N/m2", "paso 6.10",
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud(simbolo_escala, escala, "m", procedencia_escala,
                             cifras=CIFRAS_FINA),
                    Magnitud("alfa, beta, theta",
                             f"{alfa:g}, {beta:g}, {theta:g}", "",
                             f"Tabla 5.4, fila de {d}"
                             + ("" if columna == 0 else " (columna alfa_e)")),
                    Magnitud("Cs", Cs[d], "-", "Tabla 5.3, por la pendiente; "
                             + lectura_txt, cifras=CIFRAS_FACTOR),
                    Magnitud("Ch", Ch[d], "-", "Tabla 5.2, por la altura de "
                             "la salida sobre el lecho; " + lectura_txt,
                             cifras=CIFRAS_FACTOR)) + comunes,
                resultado=Magnitud(_SIMBOLO[d], dims[d], "m",
                                   f"{d} de la hoya de socavacion local",
                                   cifras=CIFRAS_MAGNITUD),
                veredicto=veredicto,
                nota_del_proyecto=_nota_de_sensibilidad(
                    d, dims[d], theta, t, t_alternativa)))
    for d, valor in dims.items():
        if not (math.isfinite(valor) and valor > 0):
            # Forma MAT-D13: el par culpable, no un solo dato. Cual es el par
            # depende de la ecuacion (H10-b: nombraba siempre el caudal y la
            # altura, tambien cuando lo que desbordaba era D84/D16).
            if material.tipo == TIPO_LECHO_NO_COHESIVO:
                culpables = (f"Q_celda = {Q_celda!r} m3/s, radio hidraulico "
                             f"lleno = {seccion.radio_hidraulico_lleno!r} m, "
                             f"y D84 = {material.D84_m!r} m con D16 = "
                             f"{material.D16_m!r} m, que forman sigma = "
                             "(D84/D16)^0.5")
            else:
                culpables = (f"V = {V.valor!r} m/s, Sv = {material.Sv_Pa!r} "
                             f"N/m2 e indice de plasticidad = "
                             f"{material.IP!r}, que forman rho·V²/tau_c")
            raise LimiteNumericoError(
                _SIMBOLO[d], valor=valor,
                motivo=f"la {d} de la hoya ({culpables}) no es un numero "
                       "positivo y finito")
    tabla = (HEC14_SOCAVACION_NO_COHESIVO
             if material.tipo == TIPO_LECHO_NO_COHESIVO
             else HEC14_SOCAVACION_COHESIVO)
    theta_hs = tabla["profundidad"][2]
    return HoyaDeSocavacion(
        metodo=metodo, profundidad=dims["profundidad"], ancho=dims["ancho"],
        longitud=dims["longitud"],
        distancia_al_maximo=(HEC14_SOCAVACION_FRACCION_LS_DEL_MAXIMO
                             * dims["longitud"]),
        duracion_min=t, origen_duracion=origen_t,
        Cs=Cs["profundidad"], Ch=Ch["profundidad"], pasos=tuple(pasos),
        duracion_por_criterio=por_criterio, duracion_acotada=acotada,
        profundidad_alternativa=(
            None if t_alternativa is None
            else dims["profundidad"] * (t_alternativa / t) ** theta_hs),
        duracion_alternativa_min=t_alternativa)


def _nota_de_sensibilidad(dimension: str, valor: float, theta: float, t: float,
                          t_alternativa: Optional[float]) -> str:
    """
    La sensibilidad de la hoya a la duracion cuando rige el criterio por
    falta del dato (hallazgo 1 de la auditoria de T-8): la dimension crece
    con (t/316)^θ, y el paso imprime cuanto daria la otra punta de la
    ventana del criterio.
    """
    if t_alternativa is None:
        return ""
    factor = (t_alternativa / t) ** theta
    return (f"SENSIBILIDAD A LA DURACION: la {dimension} se calculo con t = "
            f"{t:g} min porque el punto no declara la duracion del caudal "
            f"pico, y ese valor es adopcion del criterio "
            f"'{CRITERIO_DURACION_PICO}' [A]: con t = {t_alternativa:g} min, "
            f"la otra punta de su ventana, seria {valor * factor:.3f} m "
            f"(×{factor:.3f}).")


# ---------------------------------------------------------------------------
# --- VE-5 (lote m6) --- Estructura de caida recta de HEC-14 (num. 11.1.3)
# ---------------------------------------------------------------------------

def _longitud_de_caida(cota: float, yc: float) -> float:
    """Ec. (11.12) con `ho`, o (11.14) con `h2`: (-0.406 + (3.195 - 4.368·x/yc)^0.5)·yc."""
    return (HEC14_CAIDA_L_ORDENADA + math.sqrt(
        HEC14_CAIDA_L_RADICANDO - HEC14_CAIDA_L_PENDIENTE * cota / yc)) * yc


def caida_recta_hec14(*, Q: float, ancho_vertedero: float, desnivel_h: float,
                      tirante_aguas_abajo: float,
                      aproximacion_supercritica: bool = False,
                      yc_seccion: Optional[float] = None
                      ) -> EstructuraDeCaida:
    """
    Estructura de caida recta con estanque de bloques y umbral, HEC-14 num.
    11.1.3 (pags. impresas 11-5 a 11-8), con los dos ejemplos resueltos de
    las pags. 11-9 a 11-11 como oraculo. Las cotas se miden desde la cresta,
    negativas hacia abajo, como en la fuente.

        q  = Q / Wo;  yc = (q^2/g)^(1/3)                         Ec. (11.5)
        y3 = 2.15·yc                                             Ec. (11.7)
        h2 = -(h - yo)                                           Ec. (11.8)
        ho = h2 - y3                                             Ec. (11.9)
        Lf = (-0.406 + (3.195 - 4.368·ho/yc)^0.5)·yc             Ec. (11.12)
        Lt = (-0.406 + (3.195 - 4.368·h2/yc)^0.5)·yc             Ec. (11.14)
        Ls = (0.691 + 0.228·(Lt/yc)^2 - ho/yc)·yc
             / (0.185 + 0.456·Lt/yc)                             Ec. (11.13)
        L1 = (Lf + Ls)/2;  L2 = 0.8·yc;  L3 = 1.75·yc (el minimo)
        LB = L1 + L2 + L3                                        Ec. (11.10)

    y los bloques (0.8·yc de alto, 0.4·yc de ancho y separacion), el umbral
    (0.4·yc), el muro sobre el receptor en la salida (0.85·yc) y la
    aproximacion revestida aguas arriba de la cresta (3·yc).

    `desnivel_h` es la cresta sobre el lecho del receptor (en la salida de
    una alcantarilla, la solera de salida sobre el lecho) y
    `tirante_aguas_abajo` el tirante normal del receptor, yo.

    EL yc, por la ecuacion que la fuente da para la seccion (decision Fable,
    VE-5 lote m6): en un vertedero o un conducto RECTANGULAR, la Ec. (11.5)
    con q = Q/Wo («Critical depth in a rectangular channel or culvert is
    calculated from the unit discharge»); en una seccion de otra forma, la
    Ec. (11.6), Q^2·Tc/(g·Ac^3) = 1, que el llamador resuelve sobre su
    seccion y pasa en `yc_seccion` (en el tubo, el y_critico POR BARRIL que
    M4 publica). Con q = Q/(n·D) el yc del tubo sale MENOR que el de la Ec.
    (11.6) y el estanque, mas corto: lado inseguro. Wo sigue siendo la
    longitud de cresta de la condicion 3.

    LIMITES (`MetodoNoEvaluableError`, rotulo de HEC-14), en este orden: la
    llegada supercritica (paso 2; la rejilla del num. 11.1.2 no se
    implementa), el receptor que no queda bajo la cresta (sin lamina
    aireada), Wo de 1.5·yc o menos, |ho| de 15 ft (4.572 m) o mas, y |ho|/yc
    fuera de 1 a 15.
    """
    _exigir_positivo("Q", Q, "caudal que cae, m3/s")
    _exigir_positivo("Wo", ancho_vertedero, "ancho del vertedero, m")
    _exigir_positivo("h", desnivel_h, "desnivel de la cresta sobre el lecho, m")
    _exigir_no_negativo("yo", tirante_aguas_abajo,
                        "tirante normal del receptor, m")
    que = "estructura de caida recta (HEC-14 num. 11.1.3)"
    if aproximacion_supercritica:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="la rejilla de HEC-14 (num. 11.1.2) u otro "
                          "disipador para la llegada supercritica, fuera del "
                          "alcance de este programa",
            motivo="el flujo llega supercritico a la caida y la fuente pide "
                   "verificar condiciones subcriticas (paso 2)",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    q = Q / ancho_vertedero
    if yc_seccion is None:
        yc = math.cbrt(q * q / G)
        origen_yc = (f"Ec. (11.5), seccion rectangular: q = Q/Wo = {q:.3f} "
                     "m2/s")
    else:
        _exigir_positivo("yc", yc_seccion, "tirante critico de la seccion, m")
        yc = yc_seccion
        origen_yc = ("Ec. (11.6), Q^2·Tc/(g·Ac^3) = 1 sobre la seccion del "
                     "conducto (no rectangular), por barril: el y_critico de "
                     "M4")
    y3 = HEC14_CAIDA_Y3_EN_YC * yc
    h2 = -(desnivel_h - tirante_aguas_abajo)
    if not h2 < -TOL_UMBRAL_NORMATIVO:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="otra estructura: el receptor no deja caer la "
                          "lamina",
            motivo=f"el tirante del receptor ({tirante_aguas_abajo:.3f} m) no "
                   f"queda bajo la cresta (desnivel {desnivel_h:.3f} m): la "
                   "estructura pide la lamina aireada, con el receptor bajo "
                   "la cresta (Ec. 11.8)",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    if not ancho_vertedero > HEC14_CAIDA_WO_MIN_EN_YC * yc + TOL_UMBRAL_NORMATIVO:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="un vertedero mas ancho, con su transicion",
            motivo=f"el vertedero ({ancho_vertedero:.3f} m) no supera "
                   f"{HEC14_CAIDA_WO_MIN_EN_YC:g}·yc = "
                   f"{HEC14_CAIDA_WO_MIN_EN_YC * yc:.3f} m (num. 11.1.3, "
                   "condicion 3)",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    ho = h2 - y3
    if not -ho < HEC14_CAIDA_HO_MAX_M - TOL_UMBRAL_NORMATIVO:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="varias caidas escalonadas u otro disipador, que "
                          "este programa no dimensiona",
            motivo=f"la caida total de la cresta al piso del estanque es "
                   f"{-ho:.3f} m y la fuente limita el diseño a menos de 15 "
                   f"ft = {HEC14_CAIDA_HO_MAX_M:.3f} m (num. 11.1.3, "
                   "condicion 1)",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    relativa = -ho / yc
    if not (HEC14_CAIDA_HO_SOBRE_YC_MIN - TOL_UMBRAL_NORMATIVO < relativa
            < HEC14_CAIDA_HO_SOBRE_YC_MAX + TOL_UMBRAL_NORMATIVO):
        raise MetodoNoEvaluableError(
            que,
            procedimiento="otro disipador para esta caida relativa",
            motivo=f"la caida relativa |ho|/yc es {relativa:.2f} y la fuente "
                   f"limita el diseño a entre "
                   f"{HEC14_CAIDA_HO_SOBRE_YC_MIN:g} y "
                   f"{HEC14_CAIDA_HO_SOBRE_YC_MAX:g} (num. 11.1.3, "
                   "condicion 2)",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    depresion = -ho - desnivel_h
    Lf = _longitud_de_caida(ho, yc)
    Lt = _longitud_de_caida(h2, yc)
    a, b = HEC14_CAIDA_LS_NUMERADOR
    c, d = HEC14_CAIDA_LS_DENOMINADOR
    Ls = (a + b * (Lt / yc) ** 2 - ho / yc) * yc / (c + d * Lt / yc)
    L1 = (Lf + Ls) / 2
    L2 = HEC14_CAIDA_L2_EN_YC * yc
    L3 = HEC14_CAIDA_L3_MIN_EN_YC * yc
    LB = L1 + L2 + L3
    avisos: List[str] = []
    if depresion < -TOL_UMBRAL_NORMATIVO:
        avisos.append(
            f"Caida recta: el piso del estanque (y3 = {y3:.3f} m bajo el "
            f"nivel del receptor) queda {-depresion:.3f} m SOBRE el lecho: el "
            "receptor da mas agua que la que el estanque pide (TW > y3), el "
            "resalto se ahoga y la fuente advierte que puede hacer falta "
            "alargar el estanque")
    paso_cotas = paso(
        "F6.CAIDA",
        codigo="6.15",
        que="Cotas de la estructura de caida recta de HEC-14 (desde la "
            "cresta, negativas hacia abajo)",
        formula=("yc = (q^2/g)^(1/3)" if yc_seccion is None else
                 "Q^2 Tc / (g Ac^3) = 1")
        + ";  y3 = 2.15 yc;  h2 = -(h - yo);  ho = h2 - y3",
        formula_cita_id="HEC14.11.1.3#Y3",
        citas_textuales=("HEC14.11.1.3#Y3",
                         "HEC14.11.1.3#EC_11_5" if yc_seccion is None
                         else "HEC14.11.1.3#EC_11_6",
                         "HEC14.11.1.3#LIMITES",
                         "HEC14.11.1.3#SALIDA_COLGADA",
                         "HEC14.11.1.3#SUBCRITICO",
                         "HEC14.11.1.3#ANCHO_APROXIMACION"),
        sustitucion=(
            Magnitud("Q", Q, "m3/s", "caudal del cruce", cifras=CIFRAS_FINA),
            Magnitud("Wo", ancho_vertedero, "m",
                     "ancho del vertedero: el de los barriles en la salida "
                     "(lectura del proyecto, cita "
                     "HEC14.11.1.3#ANCHO_APROXIMACION)",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("h", desnivel_h, "m",
                     "desnivel de la cresta (solera de salida) sobre el "
                     "lecho del receptor", cifras=CIFRAS_MAGNITUD),
            Magnitud("yo", tirante_aguas_abajo, "m",
                     "tirante del receptor (Sec. 1.3)",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("yc", yc, "m", f"tirante critico sobre la cresta, "
                     f"{origen_yc}", cifras=CIFRAS_MAGNITUD),
            Magnitud("y3", y3, "m", "agua sobre el piso del estanque",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("h2", h2, "m", "nivel del receptor bajo la cresta",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("ho", ho, "m",
                           f"piso del estanque bajo la cresta; el piso baja "
                           f"{depresion:.3f} m bajo el lecho; |ho|/yc = "
                           f"{relativa:.2f}", cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="dimensionamiento [C] dentro de los limites de la "
                        "fuente: caida de menos de 15 ft, |ho|/yc entre 1 y "
                        "15 y Wo mayor que 1.5·yc"))
    paso_estanque = paso(
        "F6.CAIDA_ESTANQUE",
        codigo="6.16",
        que="Longitud, bloques, umbral, muros y aproximacion de la "
            "estructura de caida recta",
        formula="LB = (Lf + Ls)/2 + 0.8 yc + 1.75 yc;  bloques 0.8 yc x "
                "0.4 yc;  umbral 0.4 yc;  muro 0.85 yc sobre el TW;  "
                "aproximacion 3 yc",
        formula_cita_id="HEC14.11.1.3#LONGITUD",
        citas_textuales=("HEC14.11.1.3#LONGITUD", "HEC14.11.1.3#BLOQUES"),
        sustitucion=(
            Magnitud("Lf", Lf, "m", "Ec. (11.12)", cifras=CIFRAS_MAGNITUD),
            Magnitud("Lt", Lt, "m", "Ec. (11.14)", cifras=CIFRAS_MAGNITUD),
            Magnitud("Ls", Ls, "m", "Ec. (11.13)", cifras=CIFRAS_MAGNITUD),
            Magnitud("L1", L1, "m", "Ec. (11.11)", cifras=CIFRAS_MAGNITUD),
            Magnitud("L2", L2, "m", "Ec. (11.15)", cifras=CIFRAS_MAGNITUD),
            Magnitud("L3", L3, "m", "Ec. (11.16), el minimo",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud(
            "LB", LB, "m",
            f"longitud del estanque; bloques de "
            f"{HEC14_CAIDA_BLOQUE_ALTO_EN_YC * yc:.3f} m de alto y "
            f"{HEC14_CAIDA_BLOQUE_ANCHO_EN_YC * yc:.3f} m de ancho y "
            f"separacion; umbral de {HEC14_CAIDA_UMBRAL_EN_YC * yc:.3f} m; "
            f"muro {HEC14_CAIDA_MURO_SOBRE_TW_EN_YC * yc:.3f} m sobre el "
            f"receptor; aproximacion revestida "
            f"{HEC14_CAIDA_APROXIMACION_EN_YC * yc:.2f} m",
            cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="proporciones de la fuente en el tirante critico"))
    return EstructuraDeCaida(
        Q=Q, ancho_vertedero=ancho_vertedero, q=q, yc=yc,
        desnivel_h=desnivel_h, tirante_aguas_abajo=tirante_aguas_abajo,
        y3=y3, h2=h2, ho=ho, depresion_piso=depresion, Lf=Lf, Lt=Lt, Ls=Ls,
        L1=L1, L2=L2, L3=L3, longitud=LB,
        altura_bloques=HEC14_CAIDA_BLOQUE_ALTO_EN_YC * yc,
        ancho_bloques=HEC14_CAIDA_BLOQUE_ANCHO_EN_YC * yc,
        altura_umbral=HEC14_CAIDA_UMBRAL_EN_YC * yc,
        muro_sobre_tw=HEC14_CAIDA_MURO_SOBRE_TW_EN_YC * yc,
        longitud_aproximacion=HEC14_CAIDA_APROXIMACION_EN_YC * yc,
        pasos=(paso_cotas, paso_estanque), avisos=tuple(avisos))


_CAIDA = "Salida colgada, caida recta de HEC-14 (Cap. 11)"


def _caida_de_la_fase(*, resultado: ResultadoHidraulico, seccion: Seccion,
                      altura_caida_m: Optional[float],
                      pendiente_maxima_gobierna: bool,
                      avisos: List[str]) -> Optional[EstructuraDeCaida]:
    """
    --- VE-5 (lote m6) --- Si la salida queda colgada de modo que la Fase 6
    no la cierra con la hoya del Cap. 5, la estructura de caida recta del
    Cap. 11 de HEC-14 (decision del dueño: dentro del alcance). Dos
    disparadores:

      * la pendiente MAXIMA gobierna (`M7.pendiente_adoptada`, origen
        «maxima»): el conducto queda mas tendido que su cauce y el desnivel
        queda en la salida (ficha T6-02);
      * la caida pasa la ultima fila de la Tabla 5.2 (4 alturas del
        conducto), donde la hoya no se extrapola.

    El vertedero es el ancho total de los barriles en la salida (n·B o n·D,
    `Interpretacion` de la cita HEC14.11.1.3#ANCHO_APROXIMACION); yo es el TW
    del punto; la llegada es supercritica si el tirante normal del barril
    queda bajo el critico (la regla de `flujo_supercritico`). Dentro de la
    Fase 6 un `MetodoNoEvaluableError` se vuelve AVISO.
    """
    if altura_caida_m is None or not altura_caida_m > TOL_UMBRAL_NORMATIVO:
        return None
    Hd = altura_caida_m / seccion.altura
    fuera_de_tabla = Hd > HEC14_SOCAVACION_CH[-1][0] + TOL_UMBRAL_NORMATIVO
    if not (pendiente_maxima_gobierna or fuera_de_tabla):
        return None
    por_que = ("gobierna la pendiente maxima del conducto y el desnivel del "
               "cauce queda en la salida (ficha T6-02)"
               if pendiente_maxima_gobierna else
               f"la salida queda {Hd:.2f} alturas del conducto sobre el lecho "
               f"y la Tabla 5.2 de HEC-14 llega a "
               f"{HEC14_SOCAVACION_CH[-1][0]:g}")
    if resultado.TW_m is None:
        avisos.append(f"{_CAIDA}: {por_que}, y NO se evaluo -- el "
                      "resultado hidraulico no trae el tirante del receptor")
        return None
    ancho = resultado.numero_celdas * (
        seccion.B if isinstance(seccion, SeccionRectangular) else seccion.D)
    llegada_supercritica = bool(flujo_supercritico(resultado.y_normal,
                                                   resultado.y_critico))
    # Decision Fable (VE-5, lote m6): el marco con la Ec. (11.5) sobre n·B;
    # el tubo, con el yc de la Ec. (11.6) POR BARRIL, que es el y_critico que
    # M4 publica (lo resuelve con Q_celda sobre la seccion circular).
    yc_seccion = (None if isinstance(seccion, SeccionRectangular)
                  else resultado.y_critico)
    try:
        caida = caida_recta_hec14(
            Q=resultado.Q, ancho_vertedero=ancho, desnivel_h=altura_caida_m,
            tirante_aguas_abajo=resultado.TW_m,
            aproximacion_supercritica=llegada_supercritica,
            yc_seccion=yc_seccion)
    except MetodoNoEvaluableError as error:
        avisos.append(
            f"{_CAIDA}: {por_que}, y la estructura NO se evaluo -- "
            f"{error.motivo}. Hace falta: {error.procedimiento}")
        return None
    avisos.append(
        f"{_CAIDA}: {por_que}. La salida se cierra con una estructura de "
        f"caida recta de {caida.longitud:.2f} m de estanque, "
        f"con el piso {caida.depresion_piso:.2f} m bajo el lecho, bloques de "
        f"{caida.altura_bloques:.2f} m y umbral de {caida.altura_umbral:.2f} m "
        "(pasos 6.15 y 6.16)")
    avisos.extend(caida.avisos)
    return caida


def socavacion_salida(*, resultado: ResultadoHidraulico, seccion: Seccion,
                      altura_caida_m: Optional[float] = None,
                      material: Optional[MaterialLecho] = None,
                      duracion_pico_min: Optional[float] = None,
                      declarada_m: Optional[float] = None,
                      longitud_proteccion_m: Optional[float] = None,
                      proteccion_requerida: Optional[bool] = None,
                      cota_fondo_receptor: Optional[float] = None,
                      cota_solera_salida: Optional[float] = None,
                      pendiente_maxima_gobierna: bool = False
                      ) -> SocavacionSalida:
    """
    La profundidad de socavacion a la salida que la Fase 6 ENTREGA AL
    DESPLANTE DEL CABEZAL (el cabezal por punto, T-7a, la consume).

    HEC-14 num. 5.1.3: el cabezal de salida «should extend to a depth equal
    to the maximum depth of scour». Esa profundidad sale de DOS sitios, en
    este orden:

      1. `declarada_m`: el dato externo `profundidad_socavacion_estimada_m`,
         de un estudio del cauce. GANA si viene.
      2. la ESTIMADA por `hoya_de_socavacion_hec14`, si el punto declara el
         suelo del lecho (`material`) y la geometria dio la altura de caida.

    Sin ninguna de las dos, `profundidad_para_desplante` es None y
    `motivo_no_estimada` dice que dato falta: NO se supone un suelo. La
    estimada se calcula aunque haya declarada, para que las dos se impriman
    juntas. Los fuera-de-rango de la ecuacion no detienen la fase: salen
    como aviso, con el motivo de la fuente.

    `longitud_proteccion_m`, si se pasa, se contrasta con la longitud de la
    hoya: el Manual pide extender el revestimiento hasta donde la socavacion
    local no incida.

    `proteccion_requerida` es `ProteccionSalida.requerida`. Cuando es False
    --segun la Tabla Nº 11 el terreno resistiria la velocidad de salida-- y
    aun asi hay hoya estimada, la corrida lo AVISA: las dos fuentes miran
    cosas distintas (la velocidad media que el cauce admite y la hoya local
    del chorro en los ensayos de HEC-14), y es un argumento mas para no
    suprimir la proteccion sin la inspeccion de campo.

    DESDE QUE COTA SE MIDE (hallazgo 6 de la auditoria de T-8). HEC-14 Cap. 5
    no lo define: llama hs a la profundidad de socavacion sin figura que la
    acote, y con la salida por encima del lecho las dos lecturas difieren en
    la caida (~0.7 m en A-01). La decide el criterio [A]
    'referencia_profundidad_socavacion' --por defecto el fondo del cauce
    receptor, la lectura conservadora para el desplante--, y vale igual para
    la declarada: el estudio del cauce la da desde la misma cota. Con
    `cota_fondo_receptor` y `cota_solera_salida` la funcion entrega ademas la
    COTA del fondo de la hoya, que es lo que T-7a toma para el desplante.

    LA DURACION (hallazgo 1 de la primera auditoria; decision 3 del dueño,
    2026-11-12). Si rige el criterio [A] por falta del dato se AVISA: son 360
    minutos, adopcion del proyecto, y el aviso da al lado la profundidad con
    los 30 que HEC-14 recomienda «lacking this knowledge» y lo que la misma
    fuente dice de ellos (de 2/3 a 3/4 de la hoya maxima). Si el dato es
    menor de 30 min, la hoya se estima con 30 como cota superior y tambien se
    avisa.

    LA VELOCIDAD AL CRITICO (H2 de la segunda auditoria). En suelo COHESIVO
    la hoya va con (ρV²/τc)^β: si la velocidad de salida es una cota inferior
    (control de salida con el TW bajo el critico) la hoya tambien lo es, y se
    avisa con el orden de magnitud. En suelo no cohesivo la Ec. (5.1) no
    lleva la velocidad.
    """
    if declarada_m is not None:
        _exigir_no_negativo(DATO_SOCAVACION_DECLARADA, declarada_m,
                            "profundidad de socavacion declarada, m")
    estimada = None
    motivo = ""
    avisos: List[str] = []
    if material is None or material.tipo is None:
        motivo = (f"falta el suelo del lecho (`{DATO_MATERIAL_LECHO}`, dato "
                  "del EMS: tipo, y D84 y D16 si no es cohesivo o indice de "
                  "plasticidad y resistencia al corte saturada si lo es)")
    elif altura_caida_m is None:
        motivo = ("falta la altura del fondo de la salida sobre el lecho: la "
                  "Fase 7 no dio la cota de salida del punto")
    elif altura_caida_m < 0:
        motivo = (f"la salida queda {-altura_caida_m:.3f} m POR DEBAJO del "
                  "fondo del receptor (lo juzga G2, Fase 7): no hay altura de "
                  "caida con que entrar a la Tabla 5.2 de HEC-14")
    else:
        try:
            estimada = hoya_de_socavacion_hec14(
                Q_celda=resultado.Q_celda_m3s, seccion=seccion, S=resultado.S,
                V=resultado.V_salida, altura_caida_m=altura_caida_m,
                material=material, duracion_pico_min=duracion_pico_min,
                numero_celdas=resultado.numero_celdas)
        except MetodoNoEvaluableError as error:
            motivo = f"{error.motivo}. Hace falta: {error.procedimiento}"
        except DatoFaltanteError as error:
            motivo = str(error)
    pasos: List[PasoDeMemoria] = list(estimada.pasos) if estimada else []

    if declarada_m is not None:
        profundidad, origen = declarada_m, ORIGEN_SOCAVACION_DECLARADA
    elif estimada is not None:
        profundidad, origen = estimada.profundidad, ORIGEN_SOCAVACION_ESTIMADA
    else:
        profundidad, origen = None, ORIGEN_SOCAVACION_SIN_DATO

    if estimada is not None and estimada.duracion_por_criterio:
        avisos.append(
            f"Socavacion a la salida: el punto no declara la duracion del "
            f"caudal pico (`{DATO_DURACION_PICO}`) y la hoya se estimo con "
            f"t = {estimada.duracion_min:g} min, adopcion del proyecto "
            f"('{CRITERIO_DURACION_PICO}' [A]): la profundidad es "
            f"{estimada.profundidad:.2f} m. Con t = "
            f"{estimada.duracion_alternativa_min:g} min seria "
            f"{estimada.profundidad_alternativa:.2f} m. HEC-14 num. 5.1.2 "
            f"recomienda {HEC14_SOCAVACION_T_MINIMO_MIN:g} minutos a falta "
            "de ese dato, y dice de ellos: «"
            + _literal("HEC14.5.1.2#DOS_TERCIOS") + "»")
    if estimada is not None and estimada.duracion_acotada:
        avisos.append(
            f"Socavacion a la salida: la duracion declarada del caudal pico "
            f"({duracion_pico_min:g} min) es menor de "
            f"{HEC14_SOCAVACION_T_MINIMO_MIN:g} min, donde los exponentes de "
            "HEC-14 no aplican (num. 5.1.2); la hoya CRECE con t y se estimo "
            f"con {HEC14_SOCAVACION_T_MINIMO_MIN:g} min como cota superior")
    if estimada is None:
        if declarada_m is None:
            avisos.append("Socavacion a la salida: NO se estimo -- " + motivo
                          + ". El desplante del cabezal de salida queda sin "
                          "profundidad de socavacion; tambien se puede "
                          f"declarar (`{DATO_SOCAVACION_DECLARADA}`)")
    else:
        if declarada_m is not None and \
                declarada_m < estimada.profundidad - TOL_UMBRAL_NORMATIVO:
            avisos.append(
                f"Socavacion a la salida: la profundidad declarada "
                f"({declarada_m:.2f} m) es MENOR que la estimada por HEC-14 "
                f"({estimada.profundidad:.2f} m, peor caso de la socavacion "
                "local); rige la declarada")
        if proteccion_requerida is False:
            avisos.append(
                f"Socavacion a la salida: segun la Tabla Nº 11 el terreno "
                f"resistiria la velocidad de salida, y HEC-14 Cap. 5 estima "
                f"aun asi una hoya local de {estimada.profundidad:.2f} m "
                "(peor caso de sus ensayos, sin proteccion). Es un argumento "
                "mas para no suprimir la proteccion sin inspeccion de campo; "
                "el cabezal de salida baja hasta la profundidad de "
                "socavacion (HEC-14 num. 5.1.3), que es la que se entrega al "
                "desplante")
        if material.tipo == TIPO_LECHO_COHESIVO \
                and _con_la_velocidad_al_critico(resultado):
            beta = HEC14_SOCAVACION_COHESIVO["profundidad"][1]
            avisos.append(
                f"Socavacion a la salida: la hoya en suelo cohesivo va con "
                f"(rho·V²/tau_c)^{beta:g}, es decir con V^{2 * beta:g}, y la "
                "velocidad de salida se tomo al tirante critico porque las "
                "Figuras 3.3 y 3.4 de HEC-14 no dan aqui el tirante de "
                "borde: es una cota inferior (HEC-14 num. 3.1.3) y la hoya "
                "tambien. Como orden de magnitud, en la Figura 3.4 con "
                "descarga libre la velocidad de borde es de 1.35 a 1.43 "
                "veces la critica, y con ella la profundidad seria de 1.11 a "
                "1.14 veces la impresa")
        if longitud_proteccion_m is not None and \
                longitud_proteccion_m < estimada.longitud - TOL_UMBRAL_NORMATIVO:
            avisos.append(
                f"Socavacion a la salida: la hoya estimada mide "
                f"{estimada.longitud:.2f} m de largo y la proteccion adoptada "
                f"{longitud_proteccion_m:.2f} m; el Manual pide extender el "
                "revestimiento hasta donde la socavacion local no incida "
                "(num. 4.1.1.3.7 c))")
    referencia = cota_ref = cota_hoya = None
    if profundidad is not None:
        referencia = ca.valor(CRITERIO_REFERENCIA)
        if referencia not in (REFERENCIA_FONDO, REFERENCIA_SOLERA):
            raise DatoInvalidoError(
                CRITERIO_REFERENCIA, valor=referencia,
                motivo=f"es '{REFERENCIA_FONDO}' o '{REFERENCIA_SOLERA}'")
        cota_ref = (cota_fondo_receptor if referencia == REFERENCIA_FONDO
                    else cota_solera_salida)
        if cota_ref is not None:
            cota_hoya = cota_ref - profundidad
    if profundidad is not None:
        sustitucion: List[Magnitud] = []
        if declarada_m is not None:
            sustitucion.append(Magnitud(
                "hs declarada", declarada_m, "m",
                f"dato externo del punto, `{DATO_SOCAVACION_DECLARADA}`: "
                "estudio del cauce", cifras=CIFRAS_MAGNITUD))
        if estimada is not None:
            sustitucion.append(Magnitud(
                "hs estimada", estimada.profundidad, "m",
                f"paso 6.11, {estimada.metodo}", cifras=CIFRAS_MAGNITUD))
        nombre_ref = ("el fondo del cauce receptor al pie de la salida"
                      if referencia == REFERENCIA_FONDO else
                      "la solera de salida del conducto")
        if cota_ref is not None:
            sustitucion.append(Magnitud(
                "cota de referencia", cota_ref, "msnm",
                f"{nombre_ref} (criterio '{CRITERIO_REFERENCIA}' [A])",
                cifras=CIFRAS_MAGNITUD))
        resultado_paso = (
            Magnitud("cota del fondo de la hoya", cota_hoya, "msnm",
                     f"cota de referencia menos hs = {profundidad:.3f} m "
                     f"({origen})", cifras=CIFRAS_MAGNITUD)
            if cota_hoya is not None else
            Magnitud("hs", profundidad, "m", origen, cifras=CIFRAS_MAGNITUD))
        pasos.append(paso(
            "F6.SOCAVACION_DESPLANTE",
            codigo="6.14",
            que="Profundidad de socavacion para el desplante del cabezal de "
                "salida, y desde que cota se mide",
            formula=("hs = declarada, si el punto la trae; si no, la "
                     "estimada.  cota del fondo de la hoya = cota de "
                     "referencia - hs"),
            citas_textuales=("HEC14.5.1.3#CABEZAL", "HEC14.10.1#HS"),
            sustitucion=tuple(sustitucion),
            resultado=resultado_paso,
            veredicto=Veredicto(
                tipo=TipoDeVeredicto.SIN_VEREDICTO,
                explicacion="dato para el desplante del cabezal: la "
                            "profundidad de cimentacion la fija la Fase 9"),
            elecciones=(EleccionDeProyecto(
                que_se_adopto="cota desde la que se mide hs",
                valor=referencia,
                entre=tuple(ca.CRITERIOS[CRITERIO_REFERENCIA].sensibilidad),
                de_donde=f"el criterio adoptado '{CRITERIO_REFERENCIA}' [A]",
                por_que="HEC-14 Cap. 5 no define la cota desde la que se mide "
                        "hs; el fondo del cauce es la lectura conservadora "
                        "para el desplante y la Figura 10.1 de la poza, otro "
                        "metodo, la mide desde la solera de salida",
                clave_criterio=CRITERIO_REFERENCIA),)))
    caida = _caida_de_la_fase(
        resultado=resultado, seccion=seccion, altura_caida_m=altura_caida_m,
        pendiente_maxima_gobierna=pendiente_maxima_gobierna, avisos=avisos)
    if caida is not None:
        pasos.extend(caida.pasos)
    return SocavacionSalida(
        profundidad_para_desplante=profundidad, origen=origen,
        estimada=estimada, declarada_m=declarada_m,
        motivo_no_estimada="" if estimada is not None else motivo,
        pasos=tuple(pasos), avisos=tuple(avisos), referencia=referencia,
        cota_referencia=cota_ref, cota_fondo_de_la_hoya=cota_hoya,
        caida=caida)
