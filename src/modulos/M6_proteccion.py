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
                            CONSERVA tal cual: mismos numeros que antes de
                            T-8 para todo punto que no declare el terreno.
    espesor y longitud      criterios [A] 'espesor_proteccion_salida' y
                            'longitud_proteccion_salida', sin cambio.
    Froude de la salida     HEC-14 num. 10.1.1: Fr = V / (g·ye)^0.5.
    velocidad admisible     Manual MTC, Tabla Nº 11, por el tipo de terreno
                            del cauce receptor, que es un DATO DE SITIO por
                            punto (`tipo_terreno_receptor` y
                            `regimen_flujo_descarga`, datos externos). Si la
                            velocidad de salida NO la supera, el Manual no
                            pide proteger y la piedra NO se dimensiona; si la
                            supera, se avisa y se dimensiona; si el dato
                            falta, se dimensiona como antes y se avisa.
    apron de HEC-14         Sec. 10.2: D50 por la Ec. (10.4) en funcion de Q,
                            D y TW, y clase, longitud, profundidad y ancho
                            por la Tabla 10.1. AL LADO de Laushey, como
                            contraste: no sustituye a lo adoptado.
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

LO QUE ESTE MODULO NO HACE, dicho para que no se lea de mas: no dimensiona
la poza de enrocado de HEC-14 Sec. 10.1 (pide elegir el D50 entre las piedras
disponibles en la zona, que es dato del proyecto), ni los disipadores
internos de su Capitulo 7, ni el aliviadero escalonado de la Lámina Nº 04 del
Manual (la medida que el num. 4.1.1.3.7 c) da para REDUCIR la velocidad); no
digitaliza la Figura 10.3 (atenuacion de la velocidad con el TW sobre la
clave), no diseña el filtro granular (HEC 11 no esta en el repositorio de
normas) y no da dimensiones al revestimiento de la entrada, porque ninguna
fuente de normas/ las da. Cada uno tiene su ficha en
`docs/decisiones_diferidas.md`.

DIVERGENCIA DECLARADA ENTRE LAS DOS FUENTES (MAT-X6)
---------------------------------------------------
    Manual MTC, num. 4.1.1.3.7 c): d50 = V^2/(3.1*g). Funcion de UNA sola
        variable, la velocidad de salida.

    HDS-5 3a ed. (FHWA-HIF-12-026), Sec. 5.3.2 "Scour at Outlets", pag.
        impresa 5.11: remite el apron de enrocado a HEC-14 Sec. 10.2, que lo
        dimensiona en funcion de Q, D y TW.

Hasta T-8 se calculaba solo el primero, porque HEC-14 no estaba en normas/.
Hoy esta y se calculan los DOS. Sigue rigiendo el del Manual --norma peruana
vigente [N]--, que es el que llena `ProteccionSalida.d50`; el de HEC-14 [C]
se imprime al lado y, cuando pide mas piedra, mas espesor o mas longitud que
lo adoptado, la corrida lo AVISA. No hay contradiccion que resolver: son dos
metodos empiricos con variables distintas, y la memoria deja ver los dos.

Y HAY UNA RAZON TECNICA PARA CALCULAR LOS DOS, que es lectura del proyecto
y no de ninguna de las fuentes: la ec. (49) dimensiona con la velocidad sola
(d50 = V^2/(3.1·9.8) = 0.0329·V^2), como las dos relaciones del Apendice D de
HEC-14 que la fuente NO recomienda «because they do not consider tailwater
effects» (D.2 de Berry, 0.0413·V^2; D.3 de Searcy, 0.0214·V^2 con S = 2.65;
cita HEC14.D#SOLO_VELOCIDAD). HEC-14 no nombra a Laushey; el coeficiente de
la ec. (49) cae entre los de esas dos. La que HEC-14 retiene, Fletcher y
Grace, es la Ec. (10.4) que se calcula al lado.

Excepciones
-----------
Las funciones PUBLICAS de pieza (`apron_hec14`, `hoya_de_socavacion_hec14`,
`velocidad_admisible_del_cauce`) lanzan la excepcion que corresponde:
`DatoInvalidoError` (un dato que no puede ser), `DatoFaltanteError` (falta un
dato del EMS), `MetodoNoEvaluableError` (la ecuacion no cubre el caso: marco,
TW sobre la clave, conducto de mas de 1500 mm, caida mayor que la tabla,
indice de plasticidad fuera de rango). Las tres funciones de FASE
(`proteccion_salida`, `proteccion_entrada`, `socavacion_salida`) recogen las
de METODO y de dato FALTANTE y las convierten en AVISO, porque lo que falta o
no se puede evaluar en una pieza no debe dejar al punto sin las demas: un
punto sin lecho declarado conserva su d50. Un dato INVALIDO no se recoge.

QUE VELOCIDAD ENTRA (regla de doble n, Sec. 4.1)
-------------------------------------------------
La de SALIDA de HDS-5 3.1.6 que M4 emite (`ResultadoHidraulico.V_salida`),
con su procedencia. Bajo control de entrada es `V_erosion`, la rama de n
MINIMO -- la estimacion ALTA --; bajo control de salida y con el barril
horizontal (S = 0, donde no hay tirante normal) es Q entre el area al tirante
de salida. El Froude se forma con ESA velocidad y con el area que la
continuidad le asigna, Q_celda / V, no con el tirante normal.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

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
    REGIMENES_DE_FLUJO_T11, TERRENO_T11_ROTULO, V_MAX_NO_REVESTIDOS)
from src.modelos import (
    CIFRAS_FACTOR, CIFRAS_FINA, CIFRAS_MAGNITUD, ApronHEC14, ClaseHEC14,
    ControlGobernante, TIPO_LECHO_COHESIVO,
    DatoFaltanteError, DatoInvalidoError, EleccionDeProyecto, FroudeSalida,
    HoyaDeSocavacion, LimiteNumericoError, Magnitud, MaterialLecho,
    MetodoNoEvaluableError, MOTIVO_METODO_NO_EVALUABLE_HEC14,
    ORIGEN_SOCAVACION_DECLARADA,
    ORIGEN_SOCAVACION_ESTIMADA, ORIGEN_SOCAVACION_SIN_DATO, PasoDeMemoria,
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
ADVERTENCIAS_PROTECCION_SALIDA: Tuple[str, ...] = (
    ADVERTENCIA_NO_ES_DISENO,
    ADVERTENCIA_FALTA_FILTRO,
    ADVERTENCIA_ALCANCE_HDS5,
)

# ---------------------------------------------------------------------------
# Tipos de embocadura que la proteccion de entrada distingue
# ---------------------------------------------------------------------------
# La asignacion «que se protege segun la embocadura» es LECTURA DEL PROYECTO
# sobre la enumeracion del HDS-5 num. 5.3.1 (revestimiento del talud y del
# cauce, cabezal, aleros, dentellon), que la fuente da sin repartir. Hoy el
# pipeline pasa `EMBOCADURA_CABEZAL_RECTO`, que es la adoptada (HDS-5 «square
# edge w/ headwall»); T-7a pasara la de cada punto por el mismo argumento.
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
            que_se_adopto="regla del espesor y la longitud que rigen",
            valor=regla,
            entre=tuple(ca.CRITERIOS[CRITERIO_REGLA].sensibilidad),
            de_donde=f"el criterio adoptado '{CRITERIO_REGLA}' [A]",
            por_que="con «manual» rigen el espesor y la longitud de este "
                    "paso; con «envolvente_hec14», el mayor de estos y de "
                    "HEC-14 (paso 6.6c). La decision es del dueño del "
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
    tirante normal: bajo control de entrada `V` es la rama de n minimo sobre
    la geometria de n maximo y V·A(y_n) != Q; con el area de continuidad el
    numero es el de la velocidad que de verdad entra a la proteccion, del
    lado ALTO. `y_salida` (el tirante con que M4 midio esa velocidad) y
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
                                  donde: str = DONDE_SALIDA
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
    Superar la admisible NO es un incumplimiento del diseño: es lo que
    dispara la proteccion, y por eso el veredicto es INDICADOR (aviso).
    """
    _exigir_velocidad(V, "velocidad_admisible_del_cauce")
    if donde not in (DONDE_SALIDA, DONDE_ENTRADA):
        raise ValueError(f"`donde` es '{DONDE_SALIDA}' o '{DONDE_ENTRADA}', "
                         f"no {donde!r}")
    dato = DATO_TERRENO_RECEPTOR if donde == DONDE_SALIDA else DATO_TERRENO_ENTRADA
    if tipo_terreno not in V_MAX_NO_REVESTIDOS:
        raise DatoInvalidoError(
            dato, valor=tipo_terreno,
            motivo="no es una fila de la Tabla Nº 11 del Manual. Las filas "
                   "son: " + ", ".join(V_MAX_NO_REVESTIDOS))
    if regimen_flujo not in REGIMENES_DE_FLUJO_T11:
        raise DatoInvalidoError(
            DATO_REGIMEN_FLUJO, valor=regimen_flujo,
            motivo="no es una columna de la Tabla Nº 11 del Manual: "
                   + " o ".join(REGIMENES_DE_FLUJO_T11))
    V_adm = V_MAX_NO_REVESTIDOS[tipo_terreno][regimen_flujo]
    supera = V.valor > V_adm + TOL_UMBRAL_NORMATIVO
    rotulo = TERRENO_T11_ROTULO[tipo_terreno]
    if donde == DONDE_SALIDA:
        codigo, lugar = "6.4", "a la salida"
        aplicacion = ("si la velocidad de salida la supera, el proyecto "
                      "protege el cauce y dimensiona la piedra (pasos 6.1, "
                      "6.5 y 6.6); si no la supera, no reviste. No descarta "
                      "el diametro: el techo de velocidad DENTRO del conducto "
                      "es V3")
        citas = ("MC_HHD.4.1.1.3.6#T11", "MC_HHD.4.1.1.3.6#V_SALIDA")
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
    else:
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.CUMPLE, margen=margen, unidad="m/s",
            explicacion=f"la velocidad {lugar} no supera la maxima admisible "
                        f"del terreno «{rotulo}» con flujo {regimen_flujo}: "
                        "el terreno natural la resiste y la Tabla Nº 11 no "
                        "pide proteger")
    return VelocidadAdmisible(
        donde=donde, tipo_terreno=tipo_terreno, regimen_flujo=regimen_flujo,
        V=V.valor, V_admisible=V_adm, supera=supera,
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
            veredicto=veredicto))


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
        encima la fuente manda a la Figura 10.3, que no esta digitalizada:
        `MetodoNoEvaluableError`.
      * Conducto de hasta 1500 mm de alto: la nota 8 de la Tabla 1.1
        «Energy Dissipators and Limitations» lo pone como LIMITE del apron
        («Culvert rise less than or equal to 1500 mm»), y la Sec. 10.2 lo
        repite como poblacion. Se trata como los otros limites: por encima,
        `MetodoNoEvaluableError` (hallazgo 9 de la auditoria de T-8; hasta
        entonces era un aviso).

    «SUPERCRITICO EN EL CONDUCTO» se decide con `flujo_supercritico`, la
    MISMA regla que rotula el Froude, sobre `y_salida`: el tirante con que M4
    midio la velocidad de salida. Bajo control de entrada es el normal de
    registro (rama de n maximo); bajo control de salida y con el barril
    horizontal es max(TW, y_c), que nunca queda bajo el critico, y no hay
    ajuste. D' = (D + y)/2 entra en la Ec. (10.4) y en los limites del TW; la
    longitud de la Tabla 10.1 usa D, la altura real del conducto («D is the
    culvert rise»).

    EL yn ES EL DE REGISTRO, Y NO ES EL LADO ALTO DEL D50, dicho para que no
    se lea de mas: la regla de doble n (Sec. 4.1) resuelve los TIRANTES con
    n_max, y este es el que M3 publica. Con n_min el tirante supercritico
    seria menor, D' tambien, y como D50 va con D'^(-4/3) la piedra saldria
    algo mayor. El apron es CONTRASTE [C] salvo que el dueño elija la
    envolvente ('regla_espesor_longitud_proteccion_salida'), y el paso lo
    declara en la procedencia de D'.
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
            procedimiento="un disipador o una proteccion dimensionados para "
                          "seccion rectangular (HEC-14, Sec. 10.1 o 10.3), "
                          "que este programa no implementa",
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
            procedimiento="un disipador diseñado por HEC-14 (Caps. 7 a 10), "
                          "que este programa no implementa",
            motivo=f"el conducto mide {D:.2f} m de alto y la Tabla 1.1 de "
                   "HEC-14 limita el apron de enrocado a conductos de hasta "
                   f"{HEC14_APRON_ALTURA_MAX_M:.2f} m (nota 8)",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    supercritico = bool(flujo_supercritico(y_salida, y_critico))
    D_calc = (D + y_salida) / 2 if supercritico else D
    tw_min = HEC14_APRON_TW_SOBRE_D_MIN * D_calc
    tw_max = HEC14_APRON_TW_SOBRE_D_MAX * D_calc
    if TW > tw_max + TOL_UMBRAL_NORMATIVO:
        raise MetodoNoEvaluableError(
            que,
            procedimiento="la Figura 10.3 de HEC-14 (atenuacion de la "
                          "velocidad aguas abajo) con la Sec. 10.3, que este "
                          "programa no tiene digitalizada",
            motivo=f"el tirante del receptor (TW = {TW:.3f} m) supera el "
                   f"rango aceptable de la ecuacion, TW <= "
                   f"{HEC14_APRON_TW_SOBRE_D_MAX:g}·D = {tw_max:.3f} m",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)
    acotado = TW < tw_min - TOL_UMBRAL_NORMATIVO
    TW_calc = tw_min if acotado else TW
    adimensional = Q_celda / (
        math.sqrt(G) * D_calc ** HEC14_EXPONENTE_LONGITUD_DEL_CAUDAL_ADIMENSIONAL)
    D50 = (HEC14_APRON_COEFICIENTE * D_calc
           * adimensional ** HEC14_APRON_EXPONENTE * (D_calc / TW_calc))

    procedencia_D = ("diametro interior del conducto" if not supercritico else
                     f"D' = (D + yn)/2 de la Ec. (10.5), con D = {D:.3f} m e "
                     f"yn = {y_salida:.3f} m: el flujo es supercritico "
                     f"(y < yc = {y_critico:.3f} m, la misma regla del paso "
                     "6.3). yn es el tirante normal de registro (n maximo, "
                     "Sec. 4.1); con n minimo seria menor y el D50, algo "
                     "mayor")
    procedencia_TW = (
        "tirante del cuerpo receptor del punto (Sec. 1.3)" if not acotado else
        f"el del punto es {TW:.3f} m, menor que 0.4·D = {tw_min:.3f} m: se "
        "usa 0.4·D, como el ejemplo resuelto de la fuente (pag. impresa "
        "10-18), que es ademas lo que manda cuando el TW no se conoce")
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
            explicacion="dimensionamiento de contraste [C]: no sustituye al "
                        "d50 de Laushey, que es el del Manual"),
    )

    clase = D50_clase = k_long = k_esp = None
    for n_clase, d50_clase, k_l, k_e in HEC14_TABLA_10_1:
        if not d50_clase < D50 - TOL_UMBRAL_NORMATIVO:
            clase, D50_clase, k_long, k_esp = n_clase, d50_clase, k_l, k_e
            break
    comunes = dict(D50_requerido=D50, D=D, D_de_calculo=D_calc,
                   ajustado_por_supercritico=supercritico, TW=TW,
                   TW_de_calculo=TW_calc, TW_acotado=acotado)
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
                        "estandar de proyecto): se imprime como contraste de "
                        "lo adoptado en el paso 6.2"),
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

    LA NOTA (5) LA LLEVA LA FILA ENTERA: el rotulo «Tamaño de Abertura
    Aparente (3) (4) (5)» y, ademas, la celda «0,22(5)» (PDF 1023; la
    primera lectura de T-8 la aplicaba solo a esa columna y el auditor la
    refuto). Asi:
      * (5) b, «para los suelos cohesivos con un índice de plasticidad mayor
        a 7, el valor máximo promedio por rollo es de 0.30 mm»: con un lecho
        COHESIVO declarado (`indice_plasticidad`, que solo se pasa si el
        tipo del lecho es cohesivo) e IP > 7, la abertura es 0.30 mm en
        cualquiera de las tres columnas.
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
    por_nota_5b = (indice_plasticidad is not None
                   and indice_plasticidad > GEOTEXTIL_EROSION_IP_COHESIVO)
    if por_nota_5b:
        abertura = GEOTEXTIL_EROSION_TAA_COHESIVO_MM
        procedencia_abertura = (
            f"nota (5) b de la Tabla 511-06: suelo cohesivo con indice de "
            f"plasticidad {indice_plasticidad:g} > "
            f"{GEOTEXTIL_EROSION_IP_COHESIVO:g} (dato del EMS). La llamada "
            "(5) la lleva el rotulo de la fila: vale en las tres columnas")
    else:
        procedencia_abertura = (
            "celda de la Tabla 511-06 (valor maximo promedio por rollo). "
            "Su nota (5) b la lleva a 0.30 mm si el suelo es cohesivo con "
            "indice de plasticidad mayor que 7, y el lecho no lo declara")
    avisos_filtro: List[str] = []
    if (tipo_lecho == TIPO_LECHO_NO_COHESIVO
            and pasa_200_pct > PORCENTAJE_POR_UNIDAD / 2):
        avisos_filtro.append(
            f"Filtro: el lecho declarado es NO cohesivo con {pasa_200_pct:g} "
            "% pasando el tamiz N.º 200 --un limo, en la clasificacion SUCS--"
            ", y la nota (5) a de la Tabla 511-06 de EG-2013 pide para "
            "«" + _literal("EG2013.511.08#NOTA_5A") + "» un diseño del "
            "geotextil para el sitio especifico: los valores de la tabla son "
            "por omision y no bastan")
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
            citas_textuales=CITAS_DEL_FILTRO + ("EG2013.511.08#NOTA_5A",),
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


def clase_hec14_de_la_piedra(*, d50: float, D: float) -> ClaseHEC14:
    """
    La regla de clase de la Tabla 10.1 de HEC-14 aplicada a la piedra que el
    PROYECTO pone (el d50 de Laushey), no a la que pide la Ec. (10.4): la
    clase es la primera con D50 mayor o igual («The class of riprap to be
    specified is that which has a D50 greater than or equal to the required
    size», pag. impresa 10-17), y la tabla le da longitud kL·D, profundidad
    ke·D50 de la clase y ancho final 3·D + (2/3)·L. Hallazgo 5 (ii) de la
    auditoria de T-8: en A-02 la Ec. (10.4) pide la clase 1 y la piedra que
    se pone, 0.274 m, es de la clase 4, que pide 5.4 m y 0.77 m.
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
                Magnitud("d50", d50, "m", "Laushey, paso 6.1",
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
                Magnitud("d50", d50, "m", "Laushey, paso 6.1: la piedra que "
                         "el proyecto pone", cifras=CIFRAS_MAGNITUD),
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
                explicacion="guia de la fuente aplicada a la piedra adoptada: "
                            "contraste de lo adoptado en el paso 6.2")))


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


def _aviso_salida_sin_enrocado() -> str:
    """Hallazgo 4 de la auditoria de T-8: la inversa es lectura del proyecto."""
    return ("Proteccion de salida: SIN enrocado porque la velocidad de salida "
            "no supera la admisible del terreno (Tabla Nº 11). Que eso baste "
            "es lectura del proyecto, no texto del Manual; el HDS-5 (num. "
            "5.3.2, pag. impresa 5.11) dice: «"
            + _literal("HDS5_3ED.5.3.2#PRACTICA") + "». Hace falta esa "
            "inspeccion de campo para sostener la salida sin proteccion")


def _aviso_tirante_de_borde(resultado: ResultadoHidraulico) -> Tuple[str, ...]:
    """
    Hallazgo 9 de la auditoria de T-8: bajo control de salida con el TW bajo
    el critico, M4 toma la velocidad al tirante critico (HDS-5 3.1.6), y
    HEC-14 3.1.3 dice que el flujo pasa por el critico AGUAS ARRIBA de la
    salida: en el borde el tirante es menor y la velocidad mayor. V, el
    Froude y el d50 quedan SUBESTIMADOS. Las Figuras 3.3 y 3.4, que dan el
    borde, no estan digitalizadas: se avisa, no se corrige.
    """
    por_la_salida = (resultado.control_gobernante is ControlGobernante.SALIDA
                     or resultado.sin_tirante_normal)
    y = resultado.y_salida_m
    if not por_la_salida or y is None or \
            abs(y - resultado.y_critico) > TOL_UMBRAL_NORMATIVO:
        return ()
    return ("Proteccion de salida: la velocidad de salida se tomo con el "
            "tirante critico (HDS-5 num. 3.1.6) porque el TW queda bajo el. "
            "HEC-14 num. 3.1.3: «" + _literal("HEC14.3.1.3#BORDE") + "»; en "
            "el borde el tirante es MENOR que el critico y la velocidad "
            "MAYOR, de modo que V, el Froude y el d50 quedan subestimados (no "
            "conservador). Las Figuras 3.3 y 3.4 de HEC-14, que dan el "
            "tirante de borde, no estan digitalizadas",)


# La lectura del proyecto con que se cruza el terreno declarado del receptor
# (Tabla Nº 11) con el lecho declarado del EMS: las filas de arcilla son de
# suelo cohesivo, las de arena, grava y piedra de suelo granular; la ceniza
# volcanica y los dos materiales graduados «desde arcilla» y «desde limo» no
# se cruzan. Solo alimenta un AVISO de incoherencia (hallazgo 9).
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


def _regla_espesor_longitud(*, regla: str, espesor: float, longitud: float,
                            apron: Optional[ApronHEC14],
                            clase: Optional[ClaseHEC14]
                            ) -> Tuple[float, float, Optional[PasoDeMemoria],
                                       Tuple[str, ...]]:
    """
    La regla de 'regla_espesor_longitud_proteccion_salida'. «manual» (el
    archivo): rige lo adoptado. «envolvente_hec14»: el mayor de lo adoptado,
    la clase que pide la Ec. (10.4) y la clase de la piedra adoptada, cuando
    HEC-14 es evaluable (el apron se calculo); si no lo es, rige lo adoptado
    y se dice.
    """
    if regla not in (REGLA_MANUAL, REGLA_ENVOLVENTE):
        raise DatoInvalidoError(
            CRITERIO_REGLA, valor=regla,
            motivo=f"es '{REGLA_MANUAL}' o '{REGLA_ENVOLVENTE}'")
    if regla == REGLA_MANUAL:
        return espesor, longitud, None, ()
    candidatos = [(espesor, longitud, "lo adoptado")]
    for fuente, origen in ((apron, "la clase que pide la Ec. (10.4)"),
                           (clase, "la clase de la piedra adoptada")):
        if fuente is not None and fuente.clase is not None:
            candidatos.append((fuente.espesor, fuente.longitud, origen))
    if len(candidatos) == 1:
        return espesor, longitud, None, (
            f"Proteccion de salida: la regla '{CRITERIO_REGLA}' pide la "
            "envolvente con HEC-14 y HEC-14 no es evaluable en este punto: "
            "rige lo adoptado",)
    e_rige = max(c[0] for c in candidatos)
    L_rige = max(c[1] for c in candidatos)
    sustitucion = []
    for e, L, origen in candidatos:
        sustitucion.append(Magnitud(f"e, L ({origen})", f"{e:.3f} m, {L:.2f} m",
                                    "", origen))
    paso_regla = paso(
        "F6.GEOMETRIA_ADOPTADA",
        codigo="6.6c",
        que="Espesor y longitud que rigen por la regla declarada",
        formula="e = max(e adoptado, e HEC-14);  L = max(L adoptada, L HEC-14)",
        citas_textuales=("HEC14.10.2#T10_1", "HEC14.10.2#PROFUNDIDAD"),
        sustitucion=tuple(sustitucion),
        resultado=Magnitud("e", e_rige, "m",
                           f"espesor que rige; longitud L = {L_rige:.2f} m",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="envolvente de lo adoptado y de HEC-14"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="regla del espesor y la longitud de la proteccion",
            valor=regla,
            entre=tuple(ca.CRITERIOS[CRITERIO_REGLA].sensibilidad),
            de_donde=f"el criterio adoptado '{CRITERIO_REGLA}' [A]",
            por_que="decision del dueño del proyecto entre lo adoptado y la "
                    "envolvente con HEC-14",
            clave_criterio=CRITERIO_REGLA),))
    aviso = (f"Proteccion de salida: rige la envolvente con HEC-14 "
             f"('{CRITERIO_REGLA}'): espesor {espesor:.3f} -> {e_rige:.3f} m, "
             f"longitud {longitud:.2f} -> {L_rige:.2f} m")
    return e_rige, L_rige, paso_regla, (aviso,)


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
    La proteccion de SALIDA entera: d50 de Laushey, espesor y longitud
    adoptados, y --desde T-8-- el Froude de la salida, la comparacion con la
    velocidad admisible del terreno, el apron de HEC-14 y el filtro.

    `V` ES UNA `Magnitud` CON PROCEDENCIA, y no un float, desde EXT-3 (PC-04,
    EXT-M-01): la velocidad que entra a Laushey es la de SALIDA por HDS-5
    3.1.6, que M4 emite en `ResultadoHidraulico.V_salida` --bajo control de
    salida, Q entre el area al tirante min(D, max(TW, y_c)); bajo control de
    entrada, la del tirante normal con n_min--. La procedencia la trae el
    numero, y esta funcion la imprime sin reescribirla. Con el TW bajo el
    critico y el control de salida, HEC-14 3.1.3 dice que en el borde el
    tirante es menor: esa velocidad queda corta y se AVISA.

    LLAMADA SOLO CON `V` HACE LO QUE HACIA ANTES DE T-8, numero por numero:
    d50, espesor = k·d50 con 'espesor_proteccion_salida' (1.75, ventana
    1.5-2.0) y longitud = 'longitud_proteccion_salida' (5.0 m, ventana
    3.0-8.0), los dos [A] de nivel PERFIL y los dos DECLARADOS, de modo que
    la llamada NO se detiene en ninguno; con la regla
    'regla_espesor_longitud_proteccion_salida' en «manual», el valor del
    archivo, esos son los que rigen.

    LO QUE T-8 AÑADE, y cuando:
      * `resultado` y `seccion` -> Froude de la salida (HEC-14 10.1.1), apron
        de HEC-14 (Sec. 10.2) y la clase de la Tabla 10.1 que toca a la
        piedra adoptada, con el TW, el caudal por barril y los tirantes que
        M4 publico. Si la ecuacion del apron no cubre el caso (marco, TW
        sobre la clave, conducto de mas de 1500 mm) NO se rellena: aviso.
      * `tipo_terreno` y `regimen_flujo` (datos de SITIO del punto) -> la
        velocidad de salida se compara con la admisible de la Tabla Nº 11.
        `requerida` dice el resultado: False = no la supera, y entonces NO
        se dimensiona la piedra (d50, espesor y longitud en None) y se AVISA
        que esa inversa es lectura del proyecto, con lo que dice el HDS-5;
        True = la supera, se avisa y se dimensiona. Si falta cualquiera de
        los dos, `requerida` es None, se dimensiona como antes y se AVISA.
      * `pasa_200_pct`, `indice_plasticidad_lecho` (solo si el lecho es
        cohesivo) y `tipo_lecho` (datos del EMS) -> el geotextil de filtro
        (Tabla 511-06 de EG-2013, nota (5) por fila) y el cruce del terreno
        con el lecho.

    Devuelve las TRES advertencias de siempre cuando dimensiona y ninguna
    cuando la Tabla Nº 11 no pide proteger.
    """
    _exigir_velocidad(V, "proteccion_salida")
    pasos: List[PasoDeMemoria] = []
    avisos: List[str] = []

    froude = None
    if resultado is not None and seccion is not None:
        froude = froude_salida(V=V, Q_celda=resultado.Q_celda_m3s,
                               seccion=seccion, y_salida=resultado.y_salida_m,
                               y_critico=resultado.y_critico)
        avisos.extend(_aviso_tirante_de_borde(resultado))

    admisible = None
    if tipo_terreno is not None and regimen_flujo is not None:
        admisible = velocidad_admisible_del_cauce(
            V=V, tipo_terreno=tipo_terreno, regimen_flujo=regimen_flujo,
            donde=DONDE_SALIDA)
        if admisible.supera:
            avisos.append("Proteccion de salida: "
                          + admisible.paso.veredicto.explicacion)
    else:
        avisos.append(_aviso_sin_terreno(DONDE_SALIDA, tipo_terreno,
                                         regimen_flujo))
    avisos.extend(_aviso_terreno_contra_lecho(tipo_terreno, tipo_lecho))
    requerida = None if admisible is None else admisible.supera

    if requerida is False:
        # La Tabla Nº 11 no pide proteger: no hay piedra que dimensionar. Que
        # baste es lectura del proyecto, y se avisa con lo que dice el HDS-5.
        if froude is not None:
            pasos.append(froude.paso)
        pasos.append(admisible.paso)
        avisos.append(_aviso_salida_sin_enrocado())
        return ProteccionSalida(
            d50=None, espesor=None, longitud=None, V=V.valor,
            criterio_espesor=CRITERIO_ESPESOR,
            criterio_longitud=CRITERIO_LONGITUD,
            advertencias=(), numeral=NUMERAL_LAUSHEY, paso=None,
            requerida=False, froude=froude, velocidad_admisible=admisible,
            pasos=tuple(pasos), avisos=tuple(avisos))

    d50 = laushey_d50(V=V.valor)
    mult_espesor = ca.valor(CRITERIO_ESPESOR)
    espesor_adoptado = mult_espesor * d50
    longitud_adoptada = ca.valor(CRITERIO_LONGITUD)   # [A] declarado
    regla = ca.valor(CRITERIO_REGLA)
    paso_laushey = _paso_laushey(V, d50, espesor_adoptado, mult_espesor)
    pasos.append(paso_laushey)
    pasos.append(_paso_geometria_adoptada(d50, mult_espesor, espesor_adoptado,
                                          longitud_adoptada, regla))
    if froude is not None:
        pasos.append(froude.paso)
    if admisible is not None:
        pasos.append(admisible.paso)

    apron = clase = None
    if resultado is not None and seccion is not None:
        try:
            apron = apron_hec14(
                Q_celda=resultado.Q_celda_m3s, seccion=seccion,
                TW=resultado.TW_m, y_salida=resultado.y_salida_m,
                y_critico=resultado.y_critico,
                numero_celdas=resultado.numero_celdas)
        except MetodoNoEvaluableError as error:
            avisos.append(f"Proteccion de salida: el apron de HEC-14 NO se "
                          f"evaluo -- {error.motivo}. Hace falta: "
                          f"{error.procedimiento}. Rige el d50 de Laushey")
        else:
            pasos.extend(apron.pasos)
            clase = clase_hec14_de_la_piedra(d50=d50, D=apron.D)
            pasos.append(clase.paso)
    espesor, longitud, paso_regla, avisos_regla = _regla_espesor_longitud(
        regla=regla, espesor=espesor_adoptado, longitud=longitud_adoptada,
        apron=apron, clase=clase)
    if paso_regla is not None:
        pasos.append(paso_regla)
    avisos.extend(avisos_regla)
    if regla == REGLA_MANUAL and apron is not None:
        avisos.extend(_avisos_del_contraste(
            apron, d50=d50, espesor=espesor, longitud=longitud))
        if clase.clase != apron.clase:
            # Con la misma clase el aviso del apron ya lo dijo, con las
            # mismas cifras: no se repite.
            avisos.extend(_avisos_de_la_piedra(clase, espesor=espesor,
                                               longitud=longitud))
    avisos.extend(_aviso_espesor_bajo_el_piso(espesor, d50))
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
        d50=d50,
        espesor=espesor,
        longitud=longitud,
        V=V.valor,
        criterio_espesor=CRITERIO_ESPESOR,
        criterio_longitud=CRITERIO_LONGITUD,
        advertencias=ADVERTENCIAS_PROTECCION_SALIDA,
        numeral=NUMERAL_LAUSHEY,
        requerida=requerida, froude=froude, velocidad_admisible=admisible,
        apron=apron, filtro=filtro, pasos=tuple(pasos), avisos=tuple(avisos),
        clase_de_la_piedra=clase, regla_espesor_longitud=regla,
        espesor_adoptado=espesor_adoptado, longitud_adoptada=longitud_adoptada,
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

    `tipo_embocadura` es una clave de `EMBOCADURAS`. Hoy el pipeline pasa la
    adoptada (cabezal recto); el cabezal por punto pasara la suya.
    """
    if tipo_embocadura not in EMBOCADURAS:
        raise DatoInvalidoError(
            "tipo_embocadura", valor=tipo_embocadura,
            motivo="no es un tipo de embocadura que la proteccion de entrada "
                   "conozca: " + ", ".join(EMBOCADURAS))
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
                     "tipo de embocadura del punto: hoy la adoptada para "
                     "todo el proyecto; el cabezal por punto pasara la suya"),),
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
    criterio [C] 'duracion_caudal_pico_socavacion_min' (30 minutos: lo que
    la fuente recomienda «lacking this knowledge»).

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
    t_techo = None
    if por_criterio:
        t = ca.valor(CRITERIO_DURACION_PICO)
        t_techo = ca.CRITERIOS[CRITERIO_DURACION_PICO].sensibilidad[-1]
        origen_t = (f"criterio '{CRITERIO_DURACION_PICO}' [C], por falta del "
                    "dato: lo que HEC-14 manda usar «lacking this knowledge» "
                    "(num. 5.1.2), que es el extremo NO conservador de la "
                    "ventana: la hoya crece con t")
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
                                 "HEC14.5.1.5#T5_3", "HEC14.5.1.2#T30"),
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
                    d, dims[d], theta, t, t_techo)))
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
                                 "HEC14.5.1.5#T5_3", "HEC14.5.1.2#T30"),
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
                    d, dims[d], theta, t, t_techo)))
    for d, valor in dims.items():
        if not (math.isfinite(valor) and valor > 0):
            # Forma MAT-D13: el par culpable, no un solo dato.
            raise LimiteNumericoError(
                _SIMBOLO[d], valor=valor,
                motivo=f"la {d} de la hoya (Q_celda = {Q_celda!r} m3/s, "
                       f"altura del conducto = {altura!r} m) no es un numero "
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
        profundidad_al_techo_de_la_ventana=(
            None if t_techo is None
            else dims["profundidad"] * (t_techo / t) ** theta_hs),
        duracion_techo_min=t_techo)


def _nota_de_sensibilidad(dimension: str, valor: float, theta: float, t: float,
                          t_techo: Optional[float]) -> str:
    """
    La sensibilidad de la hoya a la duracion cuando rige el [C] de 30 min
    (hallazgo 1 de la auditoria de T-8): la dimension crece con (t/316)^θ, y
    el paso imprime cuanto daria al techo de la ventana del criterio.
    """
    if t_techo is None:
        return ""
    al_techo = valor * (t_techo / t) ** theta
    return (f"SENSIBILIDAD A LA DURACION: la {dimension} se calculo con t = "
            f"{t:g} min porque el punto no declara la duracion del caudal "
            f"pico, y ese es el extremo NO conservador de la ventana del "
            f"criterio '{CRITERIO_DURACION_PICO}': con t = {t_techo:g} min "
            f"seria {al_techo:.3f} m (×{(t_techo / t) ** theta:.3f}).")


def socavacion_salida(*, resultado: ResultadoHidraulico, seccion: Seccion,
                      altura_caida_m: Optional[float] = None,
                      material: Optional[MaterialLecho] = None,
                      duracion_pico_min: Optional[float] = None,
                      declarada_m: Optional[float] = None,
                      longitud_proteccion_m: Optional[float] = None,
                      proteccion_requerida: Optional[bool] = None,
                      cota_fondo_receptor: Optional[float] = None,
                      cota_solera_salida: Optional[float] = None
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
    --la Tabla Nº 11 dice que el terreno resiste la velocidad de salida y no
    se reviste-- y aun asi hay hoya estimada, la corrida lo AVISA: las dos
    fuentes miran cosas distintas (la velocidad media que el cauce admite y
    la hoya local del chorro en los ensayos de HEC-14), y lo que las concilia
    es que el cabezal de salida baje hasta la hoya (HEC-14 num. 5.1.3), que
    es lo que esta funcion entrega.

    DESDE QUE COTA SE MIDE (hallazgo 6 de la auditoria de T-8). HEC-14 Cap. 5
    no lo define: llama hs a la profundidad de socavacion sin figura que la
    acote, y con la salida por encima del lecho las dos lecturas difieren en
    la caida (~0.7 m en A-01). La decide el criterio [A]
    'referencia_profundidad_socavacion' --por defecto el fondo del cauce
    receptor, la lectura conservadora para el desplante--, y vale igual para
    la declarada: el estudio del cauce la da desde la misma cota. Con
    `cota_fondo_receptor` y `cota_solera_salida` la funcion entrega ademas la
    COTA del fondo de la hoya, que es lo que T-7a toma para el desplante.

    LA DURACION (hallazgo 1). Si rige el [C] de 30 min por falta del dato se
    AVISA: es lo que HEC-14 manda «lacking this knowledge» y el extremo no
    conservador de la ventana, y el aviso da la profundidad a su techo. Si el
    dato es menor de 30 min, la hoya se estima con 30 como cota superior y
    tambien se avisa.
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
            f"t = {estimada.duracion_min:g} min, lo que HEC-14 num. 5.1.2 "
            "manda usar a falta de ese dato y el extremo NO conservador de "
            f"la ventana de '{CRITERIO_DURACION_PICO}': con t = "
            f"{estimada.duracion_techo_min:g} min la profundidad seria "
            f"{estimada.profundidad_al_techo_de_la_ventana:.2f} m y no "
            f"{estimada.profundidad:.2f} m")
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
                f"Socavacion a la salida: la Tabla Nº 11 no pide revestir la "
                f"salida y HEC-14 Cap. 5 estima una hoya local de "
                f"{estimada.profundidad:.2f} m (peor caso de sus ensayos): el "
                "cabezal de salida baja hasta la profundidad de socavacion "
                "(HEC-14 num. 5.1.3), que es la que se entrega al desplante")
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
            citas_textuales=("HEC14.5.1.3#CABEZAL", "HEC14.10.1#DOS_D50"),
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
    return SocavacionSalida(
        profundidad_para_desplante=profundidad, origen=origen,
        estimada=estimada, declarada_m=declarada_m,
        motivo_no_estimada="" if estimada is not None else motivo,
        pasos=tuple(pasos), avisos=tuple(avisos), referencia=referencia,
        cota_referencia=cota_ref, cota_fondo_de_la_hoya=cota_hoya)
