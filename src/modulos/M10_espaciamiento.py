"""
M10_espaciamiento.py
=====================
Fase 10 de la hoja de ruta: espaciamiento entre alcantarillas de alivio
(Familia B). Desde T-9 de la cadena T, y desde sus correcciones (auditoria
adversarial de T-9, 2026-11-13), cinco piezas:

    1. La CAPACIDAD admisible de la cuneta (Manual de Hidrologia num.
       4.1.2.1 a)): el menor del caudal con la cuneta llena y del que
       produce la velocidad limite de su revestimiento.

    2. VB2, la condicion LITERAL del Manual («Q manning > Q de aporte,
       Entonces el diseño está terminado», pag. impresa 177): el caudal de
       aporte del alivio contra esa capacidad. PUEDE FALLAR y no necesita el
       tramo (H1 de la auditoria: sin ella, VB1 cumplia con un aporte un
       82 % mayor que la capacidad).

    3. La longitud por capacidad de la cuneta (L_hidraulico), CALCULADA
       cuando no se declara (Sec. 10 punto 2):

           con el TRAMO conocido:   L_hidraulico = Q_adm · s / Q
           sin el tramo:            L_hidraulico = Q_adm / (q · b / 10^6)

       La primera es la condicion de VB2 escrita como longitud; la segunda
       conserva la escorrentia especifica del area tributaria por el ancho
       tributario, y AVISA cuando el area declarada no es la faja de un tramo
       (la longitud que el par implica supera el recorrido maximo).

    4. El espaciamiento MAXIMO (Sec. 10):

           espaciamiento_max = min(L_normativo, L_hidraulico)

    5. VB1, por TRAMO: el espaciamiento ADOPTADO -- la distancia entre el
       alivio y el extremo de su tramo de cuneta, de las progresivas del
       CSV -- contra el maximo. Hasta T-9 el paso 10.1 decia «cumple»
       comparando min(L_normativo, L_hidraulico) con L_normativo, que no
       podia fallar (INF-5.1.12). El extremo lo resuelve `extremo_del_tramo`:
       el inicio declarado, o la obra anterior en progresiva -- de Familia B,
       y de Familia A por el criterio 'obras_familia_a_extremo_de_cuneta'
       (decision C del dueño) --; los huecos que VB1 no mira se avisan.

L_normativo es el limite de num. 4.1.2.1 d), pag. 179: longitud maxima de
cuneta segun el regimen pluviometrico. La hoja de ruta lo ADOPTA en 200 m
-- el regimen normal de Piura es arido (250 m), pero el evento de diseno
relevante es el FEN, durante el cual la zona se comporta como region muy
lluviosa (Sec. 10, sensibilidad declarada (200, 250)) -- y ese valor vive en
`criterios_adoptados.valor('long_max_cuneta')`, nunca repetido aqui.

Lo que este modulo NO decide
----------------------------
* La SECCION de la cuneta: es el criterio 'seccion_cuneta' [A], con el minimo
  de la Tabla Nº 34 para la region muy lluviosa como valor de archivo
  (decision A del dueño) y el talud exterior como eleccion declarada.
* El CAUDAL de aporte: es el del punto (declarado, o calculado por la Fase
  1-bis) y llega de `servicio._fase_10`, que es el puente con la
  hidrologia: este modulo no importa `MH_hidrologia` (lo importa solo
  `servicio.py`, fijado por AST).
* La pendiente de la cuneta y el ancho tributario: datos del trazo
  (`S_cuneta`, `ancho_tributario_m`), que el CSV no trae.
* La seccion trapezoidal (fila «>3000 mm/año» de la Tabla Nº 34) ni la
  rectangular: solo la triangular, que el num. 4.1.2.1 prefiere.
* El sentido del flujo en la cuneta: no es dato, y ningun texto lo supone.

Cual gobierna
-------------
El espaciamiento de diseno es el MENOR de los dos limites: cada uno es una
restriccion independiente y la que exige mas alivio es la que manda.
`Espaciamiento` lleva los dos por separado y la etiqueta de cual gobierna:
si es el normativo, el remedio es replantear alivios; si es el hidraulico,
esta en la cuneta (seccion, revestimiento, pendiente) o en el aporte.

Excepciones
-----------
    CriterioPendienteError   un criterio de la cuneta o 'long_max_cuneta'
                             dejado sin valor.
    DatoInvalidoError        una longitud, una pendiente, un ancho, un
                             caudal o una escorrentia que no es un numero
                             finito positivo; una seccion o un revestimiento
                             que burlan la puerta del criterio; un talud
                             interior mas empinado que el que admite la
                             Tabla 304.12; un inicio de tramo posterior a la
                             obra.
    LimiteNumericoError      la capacidad o el caudal por metro no son
                             positivos y finitos aunque cada dato lo sea.

Uso
---
    from src.modulos.M10_espaciamiento import espaciamiento_alivio

    espaciamiento = espaciamiento_alivio(L_hidraulico=180.0)
    espaciamiento.espaciamiento_max, espaciamiento.gobierna
"""

from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple

from src import criterios_adoptados as ca
from src.constantes_normativas import (CUNETA_STRICKLER_T32,
                                       CUNETA_T32_ROTULO, CUNETA_T33_ROTULO,
                                       CUNETA_T33_MUY_CORTA_DURACION,
                                       CUNETA_VELOCIDAD_LIMITE_T33,
                                       CUNETA_Z1_MIN_T304_12,
                                       K_MANNING_SI,
                                       NUMERAL_PENDIENTE_DRENAJE_LONGITUDINAL,
                                       PENDIENTE_DRENAJE_LONGITUDINAL,
                                       PENDIENTE_MIN_CUNETA_DG2018)
from src.dominios import METROS_POR_KM
from src.modelos import (CAPACIDAD_CUNETA_LLENA, CAPACIDAD_VELOCIDAD_LIMITE,
                         CIFRAS_FACTOR, CIFRAS_FINA, CIFRAS_MAGNITUD,
                         CODIGO_VB1, ORIGEN_L_CALCULADO, ORIGEN_L_DECLARADO,
                         CapacidadCuneta, CaudalDeDiseno, DatoInvalidoError,
                         EleccionDeProyecto, Espaciamiento,
                         LimiteNumericoError, LongitudHidraulica, Magnitud,
                         TipoDeVeredicto, TramoDeAlivio, Umbral, Verificacion,
                         Veredicto, paso,
                         GobiernaEspaciamiento, ReferenciaNormativa)
from src.modelos import (CODIGO_VB2, METODO_APORTE_AREA,   # --- T-9 (correcciones) ---
                         METODO_APORTE_TRAMO, AporteDelAlivio, ExtremoDeTramo,
                         Familia)
from src.normativa.citas import MC_HHD_CUNETA as _cita_cuneta
from src.tolerancias import TOL_UMBRAL_NORMATIVO

# LA PAGINA SE LEE DEL REGISTRO, no se repite: NOR-HID-02 se cerro en S12
# corrigiendo la cita (MC_HHD_CUNETA, pag. impresa 179) y este texto -- el
# que la memoria IMPRIME -- siguio en 178 hasta EXT-6 (PC-30). Un test lo
# compara con `MC_HHD_CUNETA.pagina_impresa` para que no vuelva a pasar.
NUMERAL_FASE_10 = ReferenciaNormativa(
    seccion_hoja_ruta="Fase 10",
    numeral_norma="Manual de Hidrologia, Hidraulica y Drenaje (MTC), "
                  f"num. 4.1.2.1 d), pag. {_cita_cuneta.pagina_impresa}",
)

# --- T-9 (correcciones, H1) --- el de VB2: la condicion del apartado a).
NUMERAL_FASE_10_CAPACIDAD = ReferenciaNormativa(
    seccion_hoja_ruta="Fase 10",
    numeral_norma="Manual de Hidrologia, Hidraulica y Drenaje (MTC), "
                  "num. 4.1.2.1 a), pag. 177",
)

CRITERIO_LONG_MAX_CUNETA = "long_max_cuneta"
# --- T-9 --- Los tres criterios de la cuneta. Se escriben aqui con su clave
# literal: `variables_entrada` atribuye el consumo de un criterio al modulo
# que escribe su clave, y este es el que la invoca.
CRITERIO_SECCION_CUNETA = "seccion_cuneta"
CRITERIO_REVESTIMIENTO_CUNETA = "revestimiento_cuneta"
CRITERIO_LECTURA_VELOCIDAD = "lectura_velocidad_limite_cuneta"
LECTURA_EXTREMO_INFERIOR = "extremo_inferior"
LECTURA_EXTREMO_SUPERIOR = "extremo_superior"

# --- T-9 (correcciones; decision C del dueño) --- si una obra de Familia A
# cierra el tramo de cuneta del alivio siguiente.
CRITERIO_OBRA_A_EXTREMO = "obras_familia_a_extremo_de_cuneta"
OBRA_A_ES_EXTREMO = "si"
OBRA_A_NO_ES_EXTREMO = "no"

CODIGO_CAPACIDAD = "10.2"
CODIGO_APORTE = "10.3"
CODIGO_L_HIDRAULICO = "10.4"
CODIGO_ESPACIAMIENTO = "10.1"
CODIGO_TRAMO = "10.5"
CODIGO_APORTE_CAPACIDAD = "10.6"      # VB2 (correcciones de T-9, H1)

ORIGEN_EXTREMO_OBRA_B = "la obra de Familia B anterior en progresiva (CSV)"
ORIGEN_EXTREMO_OBRA_A = (
    "la obra de Familia A anterior en progresiva (CSV), que cierra el tramo "
    f"por el criterio '{CRITERIO_OBRA_A_EXTREMO}'")
ORIGEN_EXTREMO_DECLARADO = ("el inicio del tramo declarado para el punto "
                            "(dato externo `inicio_tramo_cuneta_km`)")
ORIGEN_EXTREMO_NINGUNO = "ninguno"
EXTREMO_DECLARADO = "inicio declarado"
# Los datos que destraban VB1 cuando no se evaluo (H2): el servicio los
# registra como `Bloqueo` del punto.
FALTA_EXTREMO = "inicio_tramo_cuneta_km"
FALTA_MAXIMO = "L_hidraulico_m"

# Sin presuponer el sentido del flujo (H3): VB1 mide, de cada alivio, el
# tramo del lado de PROGRESIVAS MENORES.
AVISO_TRAMO_SIN_EXTREMO = (
    "VB1 (espaciamiento entre alivios) NO SE EVALUO: el tramo de cuneta del "
    "lado de progresivas menores de esta alcantarilla de alivio no tiene "
    "extremo -- ninguna obra anterior en progresiva que lo cierre (de "
    "Familia B, o de Familia A con el criterio "
    f"'{CRITERIO_OBRA_A_EXTREMO}' = {OBRA_A_ES_EXTREMO}) ni "
    "`inicio_tramo_cuneta_km` declarado --, y la longitud del tramo no se "
    "supone. Declararlo en --datos-externos para verificarlo")
AVISO_VB2_SIN_PENDIENTE = (
    "VB2 (caudal de aporte frente a la capacidad de la cuneta) NO SE "
    "EVALUO: falta la pendiente de la cuneta (`S_cuneta`, por "
    "--datos-externos), sin la que la capacidad no se calcula. La longitud "
    "por capacidad se declaro (`L_hidraulico_m`) y no se exige el dato: "
    "quien la declara declara que la cuneta conduce su aporte hasta ella")
AVISO_VB2_SIN_PENDIENTE_NI_LONGITUD = (
    "VB2 (caudal de aporte frente a la capacidad de la cuneta) NO SE "
    "EVALUO: falta la pendiente de la cuneta (`S_cuneta`, por "
    "--datos-externos), sin la que la capacidad no se calcula; por la misma "
    "falta la Fase 10 del punto se detiene (ver su bloqueo)")


def _lectura(cita_id: str) -> str:
    """
    El texto de la `Interpretacion` que cuelga de una cita, LEIDO DEL
    REGISTRO (el patron de M6 y de MH): lo que el proyecto lee en la fuente
    se imprime en la cara del proyecto con las palabras con que el registro
    lo declara, y no se redacta por segunda vez aqui.
    """
    from src.normativa import registro as _registro    # perezoso: ciclo
    return ("LECTURA DEL PROYECTO, no texto de la fuente. "
            + _registro.construir().cita(cita_id).interpretacion.texto)


def _nota_al_pie_t33(marca: str) -> str:
    """La nota al pie de la Tabla Nº 33 con esa marca, leida del registro."""
    from src.normativa import registro as _registro    # perezoso: ciclo
    for nota in _registro.construir().tabla("MC_HHD.T33").notas_al_pie:
        if nota.marca == marca:
            return nota.texto.texto
    return ""


def _finito_positivo(campo: str, valor: float, que: str,
                     id_punto: Optional[str] = None) -> float:
    """Guardia de segunda linea con la forma de MAT-D13: en positivo y negada."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) \
            or not (math.isfinite(valor) and valor > 0):
        raise DatoInvalidoError(
            campo=campo, valor=valor, id_punto=id_punto,
            motivo=f"{que} tiene que ser un numero finito positivo (Fase 10)")
    return float(valor)


# ===========================================================================
# 1. Capacidad de la cuneta (num. 4.1.2.1 a))
# ===========================================================================

def geometria_triangular(*, y: float, Z1: float, Z2: float
                         ) -> Tuple[float, float, float]:
    """
    (A, P, Rh) de la seccion triangular de taludes 1:Z1 y 1:Z2 (V:H) con
    tirante y (Figura Nº 27 del num. 4.1.2.1):

        A  = (Z1 + Z2) · y² / 2
        P  = y · (√(1 + Z1²) + √(1 + Z2²))
        Rh = A / P

    No usa las ecuaciones (4.1), (4.3), (4.4) ni (4.6) del ejemplo del
    Manual, que no reproducen la geometria que nombran (ver la nota de la
    cita MC_HHD.4.1.2.1a#VELOCIDAD).
    """
    A = (Z1 + Z2) * y ** 2 / 2
    P = y * (math.sqrt(1 + Z1 ** 2) + math.sqrt(1 + Z2 ** 2))
    return A, P, A / P


def _seccion_declarada(id_punto: Optional[str]) -> dict:
    seccion = ca.valor(CRITERIO_SECCION_CUNETA)
    if not isinstance(seccion, dict):
        raise DatoInvalidoError(
            CRITERIO_SECCION_CUNETA, valor=seccion, id_punto=id_punto,
            motivo="la seccion de la cuneta es un dict con profundidad_m, "
                   "ancho_m, talud_exterior_HV y borde_libre_m")
    for campo in ("profundidad_m", "ancho_m", "talud_exterior_HV"):
        _finito_positivo(f"{CRITERIO_SECCION_CUNETA}.{campo}",
                         seccion.get(campo), campo, id_punto)
    borde = seccion.get("borde_libre_m")
    if isinstance(borde, bool) or not isinstance(borde, (int, float)) \
            or not (math.isfinite(borde) and borde >= 0
                    and borde < seccion["profundidad_m"]):
        raise DatoInvalidoError(
            f"{CRITERIO_SECCION_CUNETA}.borde_libre_m", valor=borde,
            id_punto=id_punto,
            motivo="el borde libre tiene que ser finito, no negativo y "
                   "menor que la profundidad de la cuneta")
    return seccion


def _revestimiento_declarado(id_punto: Optional[str]) -> Tuple[str, str, str]:
    clave = ca.valor(CRITERIO_REVESTIMIENTO_CUNETA)
    filas = ca.REVESTIMIENTOS_CUNETA.get(clave)
    if filas is None:
        raise DatoInvalidoError(
            CRITERIO_REVESTIMIENTO_CUNETA, valor=clave, id_punto=id_punto,
            motivo="los revestimientos admitidos son "
                   + ", ".join(ca.REVESTIMIENTOS_CUNETA))
    fila_32, fila_33 = filas
    return clave, fila_32, fila_33


def _lectura_declarada(id_punto: Optional[str]) -> str:
    lectura = ca.valor(CRITERIO_LECTURA_VELOCIDAD)
    if lectura not in (LECTURA_EXTREMO_INFERIOR, LECTURA_EXTREMO_SUPERIOR):
        raise DatoInvalidoError(
            CRITERIO_LECTURA_VELOCIDAD, valor=lectura, id_punto=id_punto,
            motivo=f"las lecturas admitidas son {LECTURA_EXTREMO_INFERIOR} y "
                   f"{LECTURA_EXTREMO_SUPERIOR}")
    return lectura


def caudal_a_velocidad(*, v: float, n: float, S: float, Z1: float,
                       Z2: float) -> Tuple[float, float]:
    """
    (tirante, caudal) con que la velocidad de Manning en la seccion
    triangular es `v`: ecuaciones (4.2) y (4.5) del num. 4.1.2.1 a),

        Rh_v = (n · v / (K_M · √S))^(3/2)

    y, como en el triangulo Rh = c · y con c = (Z1 + Z2) / (2 · (√(1 + Z1²) +
    √(1 + Z2²))), el tirante es Rh_v / c y el caudal A(y_v) · v.
    """
    Rh_v = (n * v / (K_MANNING_SI * math.sqrt(S))) ** (3 / 2)  # literal-ok: exponente de las ecuaciones (4.2) y (4.5) del num. 4.1.2.1 a)
    c = (Z1 + Z2) / (2 * (math.sqrt(1 + Z1 ** 2) + math.sqrt(1 + Z2 ** 2)))
    y_v = Rh_v / c
    A_v, _P, _R = geometria_triangular(y=y_v, Z1=Z1, Z2=Z2)
    return y_v, A_v * v


def aviso_de_pendiente(S: float) -> str:
    """
    El aviso de una pendiente de cuneta fuera de la banda del num. 4.1.2 c)
    del Manual (0.5 % < i < 2 %), o "" si cae dentro. No detiene nada: la
    pendiente es un dato del trazo, y el DG-2018 (num. 304.11) da otro
    minimo para la cuneta revestida (0.2 %), que el aviso nombra.
    """
    minimo, maximo = PENDIENTE_DRENAJE_LONGITUDINAL
    if minimo < S < maximo:
        return ""
    lado = ("por debajo de la condicion de autolimpieza" if not S > minimo
            else "por encima de la que produciria velocidades erosivas")
    return (f"pendiente de la cuneta S = {S:.4f} m/m {lado}: el Manual de "
            f"Hidrologia ({NUMERAL_PENDIENTE_DRENAJE_LONGITUDINAL}) pide "
            f"{minimo:.3f} < i < {maximo:.3f}; el DG-2018 (num. 304.11) da "
            f"como minimas absolutas "
            f"{PENDIENTE_MIN_CUNETA_DG2018['revestida']:.3f} para cuneta "
            f"revestida y {PENDIENTE_MIN_CUNETA_DG2018['sin_revestir']:.3f} "
            f"sin revestir. La capacidad se calculo con la pendiente "
            f"declarada")


def aviso_de_talud_interior(Z1: float, id_punto: Optional[str] = None) -> str:
    """
    --- T-9 (correcciones, H5) --- El talud interior 1:Z1 contra la Tabla
    304.12 que el num. 4.1.2.1 reproduce (pag. impresa 173): la tabla da
    inclinaciones MAXIMAS por velocidad de diseño e IMDA, que el programa no
    conoce. Un talud mas empinado que 1:2 no lo admite ninguna fila y es
    `DatoInvalidoError`; entre 1:2 y 1:3, y entre 1:3 y 1:4, vale solo para
    algunas filas y se AVISA de cuales deja fuera. "" desde 1:4.
    """
    tope = CUNETA_Z1_MIN_T304_12
    if not Z1 >= tope["casos_muy_especiales"] - TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            f"{CRITERIO_SECCION_CUNETA}.ancho_m / profundidad_m", valor=Z1,
            id_punto=id_punto,
            motivo=f"el talud interior 1:{Z1:.2f} (V:H, Z1 = a/d) es mas "
                   f"empinado que el 1:{tope['casos_muy_especiales']:g} que "
                   "la Tabla 304.12 (num. 4.1.2.1 del Manual de Hidrologia) "
                   "admite solo en casos muy especiales: ninguna fila lo "
                   "admite")
    if not Z1 >= tope["general"] - TOL_UMBRAL_NORMATIVO:
        return (f"talud interior de la cuneta 1:{Z1:.2f} (V:H): la Tabla "
                f"304.12 lo admite solo con velocidad de diseño menor de 70 "
                f"km/h e IMDA menor de 750 veh/dia, y aun asi solo en casos "
                f"muy especiales (llamada (*) de la tabla); en las demas filas "
                f"pide 1:"
                f"{tope['general']:g} o 1:{tope['vd_mas_70_imda_mas_750']:g}")
    if not Z1 >= tope["vd_mas_70_imda_mas_750"] - TOL_UMBRAL_NORMATIVO:
        return (f"talud interior de la cuneta 1:{Z1:.2f} (V:H): vale con "
                f"velocidad de diseño menor de 70 km/h o IMDA menor de 750 "
                f"veh/dia; con las dos mayores la Tabla 304.12 pide 1:"
                f"{tope['vd_mas_70_imda_mas_750']:g}. La velocidad de diseño "
                f"y el IMDA no son datos del programa")
    return ""


def capacidad_cuneta(*, S_cuneta: float,
                     id_punto: Optional[str] = None) -> CapacidadCuneta:
    """
    Capacidad admisible de la cuneta triangular, num. 4.1.2.1 a) del Manual
    de Hidrologia (pag. impresa 174): «Se rige por dos límites: Caudal que
    transita con la cuneta llena; Caudal que produce la velocidad máxima
    admisible». Con la ecuacion de Manning (117):

        y_u    = d − borde_libre
        Q_llena = (K_M / n) · A(y_u) · Rh(y_u)^(2/3) · S^(1/2)
        Q_v    = A(y_v) · v_lim,   Rh(y_v) = (n · v_lim / √S)^(3/2)
        Q_adm  = min(Q_llena, Q_v)

    n = 1/K de la Tabla Nº 32 y v_lim un extremo de la Tabla Nº 33, por los
    criterios 'revestimiento_cuneta' y 'lectura_velocidad_limite_cuneta'; la
    seccion es 'seccion_cuneta'. Como la velocidad crece con el tirante en
    el triangulo, Q_v < Q_llena exactamente cuando la cuneta llena superaria
    la velocidad limite: entonces gobierna la velocidad, y se avisa.

    Desde las correcciones de la auditoria de T-9 el talud interior Z1 = a/d
    se contrasta con la Tabla 304.12 (`aviso_de_talud_interior`), el paso
    declara que el n sale de la Tabla Nº 32 y no de la Nº 09 (que el mismo
    apartado nombra), imprime la nota «*» de la Tabla Nº 33 desde el
    registro, y dice que la cuneta del modelo es la del tramo y no la del
    cruce (las tres lecturas, como `Interpretacion` del registro).
    """
    S = _finito_positivo("S_cuneta", S_cuneta,
                         "la pendiente longitudinal de la cuneta", id_punto)
    seccion = _seccion_declarada(id_punto)
    revestimiento, fila_32, fila_33 = _revestimiento_declarado(id_punto)
    lectura = _lectura_declarada(id_punto)

    d = float(seccion["profundidad_m"])
    a = float(seccion["ancho_m"])
    Z2 = float(seccion["talud_exterior_HV"])
    borde = float(seccion["borde_libre_m"])
    Z1 = a / d
    aviso_talud = aviso_de_talud_interior(Z1, id_punto)
    y_u = d - borde
    K = CUNETA_STRICKLER_T32[fila_32]
    n = 1 / K
    v_min, v_max = (CUNETA_VELOCIDAD_LIMITE_T33[fila_33][0],
                    CUNETA_VELOCIDAD_LIMITE_T33[fila_33][-1])
    v_lim = v_min if lectura == LECTURA_EXTREMO_INFERIOR else v_max
    v_otra = v_max if lectura == LECTURA_EXTREMO_INFERIOR else v_min

    A, _P, Rh = geometria_triangular(y=y_u, Z1=Z1, Z2=Z2)
    Q_llena = (K_MANNING_SI / n) * A * Rh ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, ecuacion (117) del num. 4.1.2.1 a)
    V_llena = Q_llena / A
    y_v, Q_v = caudal_a_velocidad(v=v_lim, n=n, S=S, Z1=Z1, Z2=Z2)
    _y_otra, Q_v_otra = caudal_a_velocidad(v=v_otra, n=n, S=S, Z1=Z1, Z2=Z2)
    Q_adm = min(Q_llena, Q_v)
    Q_adm_otra = min(Q_llena, Q_v_otra)
    if not (math.isfinite(Q_adm) and Q_adm > 0):
        raise LimiteNumericoError(
            "capacidad de la cuneta", valor=Q_adm, id_punto=id_punto,
            motivo=f"la capacidad no es un caudal positivo con la seccion "
                   f"{seccion} y S = {S:g}")
    gobierna = (CAPACIDAD_VELOCIDAD_LIMITE if Q_v < Q_llena
                else CAPACIDAD_CUNETA_LLENA)

    avisos = []
    pendiente = aviso_de_pendiente(S)
    if pendiente:
        avisos.append(pendiente)
    if aviso_talud:
        avisos.append(aviso_talud)
    notas = [
        f"Talud interior Z1 = a / d = {a:g} / {d:g} = {Z1:.3f} (Figura Nº 27: "
        "el ancho se mide del borde de la rasante a la vertical del vertice).",
        "A, P y Rh salen de la geometria declarada; las ecuaciones (4.1), "
        "(4.3), (4.4) y (4.6) del ejemplo del Manual no se usan porque no "
        "reproducen la seccion que nombran.",
        _lectura("MC_HHD.4.1.2.1#UBICACION"),
    ]
    if revestimiento == "concreto":
        notas.append(
            f"La fila «{CUNETA_T32_ROTULO[fila_32]}» de la Tabla Nº 32 y la "
            f"fila «{CUNETA_T33_ROTULO[fila_33]}» de la Tabla Nº 33 nombran el "
            "mismo material.")
    else:
        notas.append(_lectura("MC_HHD.4.1.2.1#T33"))
    if borde > 0:
        notas.append(
            f"Borde libre de {borde:g} m bajo la cuneta llena: es ADOPCION del "
            "proyecto (criterio 'seccion_cuneta'); el Manual define la "
            "capacidad con la cuneta llena y no da borde libre para cunetas.")
    if fila_33 in CUNETA_T33_MUY_CORTA_DURACION:
        notas.append(
            f"La fila de la Tabla Nº 33 lleva la llamada "
            f"«{_nota_al_pie_t33('*')}»: la fuente no da otro valor para un "
            "flujo prolongado (el evento de diseño es el FEN), y el extremo "
            "inferior de la fila es la lectura conservadora.")
    if aviso_talud:
        notas.append(aviso_talud + ".")
    if gobierna == CAPACIDAD_VELOCIDAD_LIMITE:
        aviso = (f"capacidad de la cuneta gobernada por la VELOCIDAD LIMITE: "
                 f"llena alcanzaria V = {V_llena:.2f} m/s, sobre los "
                 f"{v_lim:.2f} m/s de la Tabla Nº 33 para "
                 f"«{CUNETA_T33_ROTULO[fila_33]}»; la capacidad admisible es "
                 f"el caudal a esa velocidad (tirante {y_v:.3f} m). El "
                 "apartado e) del num. 4.1.2.1 pide revestir la cuneta cuando "
                 "la velocidad supera esos limites")
        avisos.append(aviso)
        notas.append(aviso + ".")

    paso_capacidad = paso(
        "F10.CAPACIDAD", codigo=CODIGO_CAPACIDAD,
        que="Capacidad admisible de la cuneta: el menor del caudal con la "
            "cuneta llena y del que produce la velocidad limite admisible",
        formula=("y_u = d − bl ; A = (Z1 + Z2)·y²/2 ; P = y·(√(1+Z1²) + "
                 "√(1+Z2²)) ; Q_llena = (K_M/n)·A·Rh^(2/3)·S^(1/2) ; "
                 "Rh_v = (n·v_lim/√S)^(3/2) ; Q_v = A(y_v)·v_lim ; "
                 "Q_adm = min(Q_llena, Q_v)"),
        formula_cita_id="MC_HHD.4.1.2.1a#MANNING",
        citas_textuales=("MC_HHD.4.1.2.1a", "MC_HHD.4.1.2.1a#MANNING",
                         "MC_HHD.4.1.2.1a#VELOCIDAD", "MC_HHD.4.1.2.1#T32",
                         "MC_HHD.4.1.2.1#T09", "MC_HHD.4.1.2.1#T33",
                         "MC_HHD.4.1.2.1#T304_12", "MC_HHD.4.1.2.1#UBICACION",
                         "MC_HHD.4.1.2.1e"),
        sustitucion=(
            Magnitud("d", d, "m", f"criterio adoptado '{CRITERIO_SECCION_CUNETA}' "
                     "[A], profundidad", cifras=CIFRAS_MAGNITUD),
            Magnitud("a", a, "m", f"criterio adoptado '{CRITERIO_SECCION_CUNETA}' "
                     "[A], ancho", cifras=CIFRAS_MAGNITUD),
            Magnitud("Z1", Z1, "H:V", "a / d", cifras=CIFRAS_MAGNITUD),
            Magnitud("Z2", Z2, "H:V", f"criterio adoptado "
                     f"'{CRITERIO_SECCION_CUNETA}' [A], talud exterior",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("bl", borde, "m", f"criterio adoptado "
                     f"'{CRITERIO_SECCION_CUNETA}' [A], borde libre",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("y_u", y_u, "m", "d − bl", cifras=CIFRAS_MAGNITUD),
            Magnitud("n", n, "", f"1/K, K = {K:g} de la Tabla Nº 32, fila "
                     f"«{CUNETA_T32_ROTULO[fila_32]}» (criterio "
                     f"'{CRITERIO_REVESTIMIENTO_CUNETA}' = {revestimiento})",
                     cifras=CIFRAS_FINA),
            Magnitud("S", S, "m/m", "dato externo `S_cuneta` (trazo)",
                     cifras=CIFRAS_FINA),
            Magnitud("v_lim", v_lim, "m/s", f"Tabla Nº 33, fila "
                     f"«{CUNETA_T33_ROTULO[fila_33]}», {lectura} (criterio "
                     f"'{CRITERIO_LECTURA_VELOCIDAD}')", cifras=CIFRAS_FACTOR),
            Magnitud("A", A, "m2", "seccion a y_u", cifras=CIFRAS_FINA),
            Magnitud("Rh", Rh, "m", "A / P a y_u", cifras=CIFRAS_FINA),
            Magnitud("Q_llena", Q_llena, "m3/s",
                     "ecuacion (117) con la cuneta llena hasta y_u",
                     cifras=CIFRAS_FINA),
            Magnitud("V_llena", V_llena, "m/s", "Q_llena / A",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("y_v", y_v, "m", "ecuacion (4.2) despejada en el "
                     "triangulo", cifras=CIFRAS_FINA),
            Magnitud("Q_v", Q_v, "m3/s", "A(y_v) · v_lim", cifras=CIFRAS_FINA)),
        resultado=Magnitud("Q_adm", Q_adm, "m3/s",
                           f"gobierna: {gobierna}", cifras=CIFRAS_FINA),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="capacidad, no verificacion: la juzga VB2 contra el "
                        "caudal de aporte y entra a la longitud por capacidad "
                        "(paso 10.4)"),
        elecciones=(
            EleccionDeProyecto(
                que_se_adopto="revestimiento de la cuneta",
                valor=revestimiento,
                entre=tuple(ca.REVESTIMIENTOS_CUNETA),
                de_donde=f"el criterio adoptado "
                         f"'{CRITERIO_REVESTIMIENTO_CUNETA}' [A]",
                por_que="fija el n (Tabla Nº 32) y la velocidad limite (Tabla "
                        "Nº 33); el Manual recomienda el concreto (num. "
                        "4.1.2.1 e)), que para la longitud entre alivios es "
                        "la opcion menos conservadora de la ventana",
                cita_id="MC_HHD.4.1.2.1e",
                clave_criterio=CRITERIO_REVESTIMIENTO_CUNETA),
            # Dudoso 2 de la auditoria: el apartado ofrece dos tablas para el
            # n y no dice cual rige.
            EleccionDeProyecto(
                que_se_adopto="tabla de la que sale el n de la cuneta",
                valor=f"Tabla Nº 32 (K de Strickler): n = 1/{K:g}",
                entre=("Tabla Nº 32, el coeficiente de Strickler de cunetas",
                       "Tabla Nº 09, los n de Manning mas usados que el "
                       "mismo apartado nombra"),
                de_donde="el num. 4.1.2.1 a), pag. impresa 175",
                por_que="la Tabla Nº 32 es la que el numeral de cunetas "
                        "escribe para cunetas, por tipo de cuneta; la Tabla "
                        "Nº 09 es la general del Manual",
                cita_id="MC_HHD.4.1.2.1#T09"),
            EleccionDeProyecto(
                que_se_adopto="extremo de la fila de la Tabla Nº 33",
                valor=f"{lectura}: v_lim = {v_lim:.2f} m/s, Q_adm = "
                      f"{Q_adm:.4f} m3/s",
                entre=(f"{lectura}: Q_adm = {Q_adm:.4f} m3/s",
                       f"el otro extremo, {v_otra:.2f} m/s: Q_adm = "
                       f"{Q_adm_otra:.4f} m3/s"),
                de_donde=f"el criterio adoptado "
                         f"'{CRITERIO_LECTURA_VELOCIDAD}' [A]",
                por_que="la Tabla Nº 33 da un intervalo por superficie y no "
                        "dice cual de sus extremos rige; el inferior es el "
                        "conservador",
                cita_id="MC_HHD.4.1.2.1#T33",
                clave_criterio=CRITERIO_LECTURA_VELOCIDAD)),
        nota_del_proyecto=" ".join(notas))

    return CapacidadCuneta(
        profundidad_m=d, ancho_m=a, talud_interior_HV=Z1, talud_exterior_HV=Z2,
        borde_libre_m=borde, tirante_util_m=y_u, revestimiento=revestimiento,
        n=n, v_limite_m_s=v_lim, S=S, area_llena_m2=A, radio_llena_m=Rh,
        Q_llena_m3s=Q_llena, V_llena_m_s=V_llena, Q_velocidad_m3s=Q_v,
        Q_admisible_m3s=Q_adm, gobierna=gobierna, pasos=(paso_capacidad,),
        avisos=tuple(avisos))


def verificar_aporte(*, capacidad: Optional[CapacidadCuneta],
                     Q_aporte_m3s: float, origen_aporte: str,
                     id_punto: Optional[str] = None,
                     aviso_sin_capacidad: str = AVISO_VB2_SIN_PENDIENTE
                     ) -> AporteDelAlivio:
    """
    --- T-9 (correcciones de la auditoria, H1) --- VB2, la condicion literal
    del Manual (num. 4.1.2.1 a), pag. impresa 177):

        «Q manning > Q de aporte, Entonces el diseño está terminado»
        VB2:   Q_aporte <= Q_adm

    En la Familia B el caudal del punto es, por contrato, el de la cuneta
    que descarga en el alivio (declarado, o el que calculo la Fase 1-bis).
    PUEDE FALLAR, y no necesita el tramo. Sin capacidad (falta la pendiente
    de la cuneta) no hay verificacion: el resultado lleva el aviso de que no
    se evaluo y el servicio decide si eso detiene (sin la longitud declarada,
    la Fase 10 ya se detiene nombrando el dato) o solo avisa.
    """
    Q = _finito_positivo("Q_m3s", Q_aporte_m3s,
                         "el caudal de aporte del alivio", id_punto)
    if capacidad is None:
        return AporteDelAlivio(Q_aporte_m3s=Q, origen_aporte=origen_aporte,
                               capacidad=None, verificacion=None,
                               aviso=aviso_sin_capacidad)
    Q_adm = capacidad.Q_admisible_m3s
    cumple = Q <= Q_adm + TOL_UMBRAL_NORMATIVO
    paso_vb2 = paso(
        "F10.APORTE_CAPACIDAD", codigo=CODIGO_APORTE_CAPACIDAD,
        que="VB2 - Caudal de aporte del alivio frente a la capacidad "
            "admisible de la cuneta",
        formula="Q_aporte <= Q_adm",
        formula_cita_id="MC_HHD.4.1.2.1a#CONDICION",
        citas_textuales=("MC_HHD.4.1.2.1a#CONDICION", "MC_HHD.4.1.2.1b"),
        sustitucion=(
            Magnitud("Q_aporte", Q, "m3/s", origen_aporte,
                     cifras=CIFRAS_FINA),
            Magnitud("Q_adm", Q_adm, "m3/s", f"paso {CODIGO_CAPACIDAD} "
                     f"(gobierna: {capacidad.gobierna})",
                     cifras=CIFRAS_FINA)),
        resultado=Magnitud("Q_aporte", Q, "m3/s",
                           "caudal que la cuneta entrega al alivio",
                           cifras=CIFRAS_FINA),
        umbral=Umbral(
            descripcion="capacidad admisible de la cuneta",
            valor=Q_adm, unidad="m3/s", cita_id="MC_HHD.4.1.2.1a#CONDICION",
            caracter="EXIGENCIA: «Q manning > Q de aporte, Entonces el "
                     "diseño está terminado. Si ocurre lo contrario, debemos "
                     "volver al paso 2 y elegir otra altura de cuneta (H).»",
            aplicacion="Umbral duro, la condicion literal de la fuente. El "
                       "remedio de un incumplimiento es una cuneta de mas "
                       "capacidad (seccion, revestimiento, pendiente) o un "
                       "tramo mas corto, que reduce el aporte",
            criterio_aplicado=CRITERIO_SECCION_CUNETA),
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.CUMPLE if cumple
                  else TipoDeVeredicto.NO_CUMPLE),
            margen=Q_adm - Q, unidad="m3/s",
            explicacion=("la cuneta conduce el caudal de aporte" if cumple
                         else "el caudal de aporte supera la capacidad de la "
                              "cuneta: desborda sobre la via antes de llegar "
                              "al alivio")),
        nota_del_proyecto=(
            "En la Familia B el caudal del punto es, por contrato, el de la "
            "cuneta que descarga en el alivio, y es el que se compara. Si el "
            "alivio recibe cunetas de los dos lados, el caudal declarado es "
            "la suma y la comparacion queda del lado seguro."))
    verificacion = Verificacion(
        cumple=cumple, numeral=NUMERAL_FASE_10_CAPACIDAD,
        valor_obtenido=Q, valor_admisible=Q_adm,
        criterio_aplicado=CRITERIO_SECCION_CUNETA, codigo=CODIGO_VB2,
        paso=paso_vb2)
    return AporteDelAlivio(Q_aporte_m3s=Q, origen_aporte=origen_aporte,
                           capacidad=capacidad, verificacion=verificacion)


# ===========================================================================
# 2. Caudal por metro y longitud por capacidad (num. 4.1.2.1 b))
# ===========================================================================

def longitud_hidraulica(*, capacidad: CapacidadCuneta,
                        escorrentia_m3s_km2: float, origen_escorrentia: str,
                        ancho_tributario_m: float,
                        caudal_de_aporte: Optional[CaudalDeDiseno] = None,
                        area_km2: Optional[float] = None,
                        periodo_retorno: str = "",
                        id_punto: Optional[str] = None) -> LongitudHidraulica:
    """
    La longitud a partir de la cual el caudal aportante supera la capacidad
    de la cuneta (Sec. 10 punto 2 de la hoja de ruta), CUANDO EL TRAMO NO SE
    CONOCE (o el caudal lo calculo la Fase 1-bis):

        q'           = q · b / 10^6      [m3/s por m]
        L_hidraulico = Q_adm / q'

    `q` es la escorrentia especifica del area tributaria (m3/s por km2): por
    el metodo racional del num. 4.1.2.1 b), Q = C·I·A / 3.6 con A en km2, de
    modo que q = Q / A = C·I / 3.6 y el caudal de una faja de ancho b y
    longitud L es q · b · L / 10^6.

    ESE REPARTO SUPONE QUE EL AREA ES LA FAJA b x TRAMO (H1 de la auditoria
    de T-9): con `area_km2` se publica la longitud que el par implica,
    s_impl = A · 10^6 / b, y si supera el recorrido maximo normativo
    ('long_max_cuneta') se AVISA --el area declarada es la de una cuenca
    mayor y la longitud calculada no es fiable--. La comparacion es contra
    el limite normativo y no contra una tolerancia inventada. Con el tramo
    conocido y el caudal declarado, la longitud la da
    `longitud_hidraulica_por_tramo`, que no mezcla el area con el ancho.

    `periodo_retorno` es el texto con que el servicio dice de que TR sale la
    lluvia del aporte (el del punto, H4): este modulo no lo escribe.
    """
    q = _finito_positivo("escorrentia especifica", escorrentia_m3s_km2,
                         "la escorrentia especifica del area tributaria",
                         id_punto)
    b = _finito_positivo("ancho_tributario_m", ancho_tributario_m,
                         "el ancho tributario de la cuneta", id_punto)
    m2_por_km2 = METROS_POR_KM ** 2
    q_metro = q * b / m2_por_km2
    L = capacidad.Q_admisible_m3s / q_metro
    if not (math.isfinite(L) and L > 0 and q_metro > 0):
        raise LimiteNumericoError(
            "L_hidraulico", valor=L, id_punto=id_punto,
            motivo=f"la longitud por capacidad no es finita y positiva con "
                   f"Q_adm = {capacidad.Q_admisible_m3s:g} m3/s, q = {q:g} "
                   f"m3/s/km2 y b = {b:g} m")
    avisos = list(capacidad.avisos)
    s_impl: Optional[float] = None
    sustitucion_extra: Tuple[Magnitud, ...] = ()
    nota_area = ""
    if area_km2 is not None:
        A = _finito_positivo("area tributaria", area_km2,
                             "el area tributaria del alivio", id_punto)
        s_impl = A * m2_por_km2 / b
        sustitucion_extra = (
            Magnitud("A", A, "km2", "area tributaria del caudal del punto",
                     cifras=CIFRAS_FINA),
            Magnitud("s_impl", s_impl, "m", "A · 10^6 / b: la longitud de "
                     "cuneta que el area y el ancho implican",
                     cifras=CIFRAS_FACTOR))
        L_normativo = ca.valor(CRITERIO_LONG_MAX_CUNETA)
        if s_impl > L_normativo + TOL_UMBRAL_NORMATIVO:
            aviso = (f"la longitud por capacidad de la cuneta NO ES FIABLE: "
                     f"el area tributaria del punto ({A:g} km2) y el ancho "
                     f"tributario ({b:g} m) implican un tramo de "
                     f"s_impl = {s_impl:.0f} m, mas que el recorrido maximo "
                     f"de la cuneta ({L_normativo:g} m, criterio "
                     f"'{CRITERIO_LONG_MAX_CUNETA}'): el area no es la faja "
                     f"b x tramo que descarga en el alivio, y q' = q · b "
                     f"reparte el caudal de una cuenca mayor. Declarar el "
                     f"tramo (`inicio_tramo_cuneta_km` u otra obra que lo "
                     f"cierre), el area del tramo o `L_hidraulico_m`")
            avisos.append(aviso)
            nota_area = aviso + "."
    paso_aporte = paso(
        "F10.APORTE", codigo=CODIGO_APORTE,
        que="Caudal aportante por metro de cuneta",
        formula="q' = q · b / 10^6   [q en m3/s por km2, b en m, q' en m3/s "
                "por m] ; s_impl = A · 10^6 / b",
        formula_cita_id="MC_HHD.4.1.2.1b",
        citas_textuales=("MC_HHD.4.1.2.1b", "MC_HHD.4.1.2a"),
        sustitucion=(
            Magnitud("q", q, "m3/s por km2", origen_escorrentia,
                     cifras=CIFRAS_FINA),
            Magnitud("b", b, "m", "dato externo `ancho_tributario_m` "
                     "(seccion tipica de la via)", cifras=CIFRAS_MAGNITUD))
        + sustitucion_extra,
        resultado=Magnitud("q'", q_metro, "m3/s por m",
                           "caudal aportante por metro de cuneta",
                           cifras=CIFRAS_FINA + CIFRAS_FACTOR),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="caudal por metro, no verificacion"),
        nota_del_proyecto=" ".join(t for t in (
            "El tramo de cuneta del alivio no se conoce (o el caudal lo "
            "calculo la Fase 1-bis): el aporte se reparte con la escorrentia "
            "especifica del area tributaria por el ancho de la faja.",
            periodo_retorno, _lectura("MC_HHD.4.1.2a"), nota_area) if t))
    paso_L = _paso_longitud(capacidad, q_metro, L)
    return LongitudHidraulica(
        capacidad=capacidad, escorrentia_m3s_km2=q,
        origen_escorrentia=origen_escorrentia, ancho_tributario_m=b,
        q_por_metro_m3s_m=q_metro, L_hidraulico=L,
        pasos=(*capacidad.pasos, paso_aporte, paso_L), avisos=tuple(avisos),
        caudal_de_aporte=caudal_de_aporte, metodo_aporte=METODO_APORTE_AREA,
        Q_aporte_m3s=(None if caudal_de_aporte is None
                      else caudal_de_aporte.Q_m3s),
        s_implicita_m=s_impl)


def longitud_hidraulica_por_tramo(*, capacidad: CapacidadCuneta,
                                  Q_aporte_m3s: float, origen_aporte: str,
                                  longitud_tramo_m: float, extremo: str,
                                  periodo_retorno: str = "",
                                  id_punto: Optional[str] = None
                                  ) -> LongitudHidraulica:
    """
    --- T-9 (correcciones de la auditoria, H1) --- La longitud por capacidad
    con el TRAMO conocido: el caudal de aporte del alivio, que por contrato
    es el de la cuneta que descarga en el, repartido uniformemente en su
    tramo real de longitud s,

        q'           = Q / s
        L_hidraulico = Q_adm / q' = Q_adm · s / Q

    Es el equivalente EXACTO de la condicion literal del Manual (pag.
    impresa 177): L_hidraulico >= s si y solo si Q_adm >= Q. No usa el area
    tributaria ni el ancho tributario, de modo que no puede repartir el
    caudal de una cuenca mayor que la faja del tramo (el CUMPLE falso de H1).
    """
    Q = _finito_positivo("Q_m3s", Q_aporte_m3s,
                         "el caudal de aporte del alivio", id_punto)
    s = _finito_positivo("longitud del tramo", longitud_tramo_m,
                         "la longitud del tramo de cuneta", id_punto)
    q_metro = Q / s
    L = capacidad.Q_admisible_m3s / q_metro
    if not (math.isfinite(L) and L > 0 and q_metro > 0):
        raise LimiteNumericoError(
            "L_hidraulico", valor=L, id_punto=id_punto,
            motivo=f"la longitud por capacidad no es finita y positiva con "
                   f"Q_adm = {capacidad.Q_admisible_m3s:g} m3/s, Q = {Q:g} "
                   f"m3/s y s = {s:g} m")
    paso_aporte = paso(
        "F10.APORTE", codigo=CODIGO_APORTE,
        que="Caudal aportante por metro de cuneta",
        formula="q' = Q / s   [Q en m3/s, s en m, q' en m3/s por m]",
        formula_cita_id="MC_HHD.4.1.2.1b",
        citas_textuales=("MC_HHD.4.1.2.1b", "MC_HHD.4.1.2a"),
        sustitucion=(
            Magnitud("Q", Q, "m3/s", origen_aporte, cifras=CIFRAS_FINA),
            Magnitud("s", s, "m", f"tramo de cuneta desde {extremo} (paso "
                     f"{CODIGO_TRAMO})", cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("q'", q_metro, "m3/s por m",
                           "caudal aportante por metro de cuneta",
                           cifras=CIFRAS_FINA + CIFRAS_FACTOR),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="caudal por metro, no verificacion"),
        nota_del_proyecto=" ".join(t for t in (
            "El tramo de cuneta del alivio se conoce: su caudal de aporte "
            "(el del punto) se reparte uniformemente a lo largo de el, sin "
            "pasar por el area tributaria ni por el ancho de la faja. Con "
            "este reparto, la longitud por capacidad supera al tramo si y "
            "solo si la capacidad supera al aporte (VB2).",
            periodo_retorno, _lectura("MC_HHD.4.1.2a")) if t))
    paso_L = _paso_longitud(capacidad, q_metro, L)
    return LongitudHidraulica(
        capacidad=capacidad, escorrentia_m3s_km2=None,
        origen_escorrentia=origen_aporte, ancho_tributario_m=None,
        q_por_metro_m3s_m=q_metro, L_hidraulico=L,
        pasos=(*capacidad.pasos, paso_aporte, paso_L),
        avisos=tuple(capacidad.avisos), metodo_aporte=METODO_APORTE_TRAMO,
        Q_aporte_m3s=Q, longitud_tramo_m=s)


def _paso_longitud(capacidad: CapacidadCuneta, q_metro: float,
                   L: float) -> "PasoDeMemoria":
    """El paso 10.4, el mismo con los dos repartos del aporte."""
    return paso(
        "F10.L_HIDRAULICO", codigo=CODIGO_L_HIDRAULICO,
        que="Longitud por capacidad de la cuneta",
        formula="L_hidraulico = Q_adm / q'",
        formula_cita_id="MC_HHD.4.1.2.1a",
        citas_textuales=("MC_HHD.4.1.2.1a", "MC_HHD.4.1.2.1b",
                         "DG2018.304.11"),
        sustitucion=(
            Magnitud("Q_adm", capacidad.Q_admisible_m3s, "m3/s",
                     f"paso {CODIGO_CAPACIDAD} (gobierna: "
                     f"{capacidad.gobierna})", cifras=CIFRAS_FINA),
            Magnitud("q'", q_metro, "m3/s por m", f"paso {CODIGO_APORTE}",
                     cifras=CIFRAS_FINA + CIFRAS_FACTOR)),
        resultado=Magnitud("L_hidraulico", L, "m",
                           "longitud a la que el caudal aportante iguala la "
                           "capacidad admisible", cifras=CIFRAS_FACTOR),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="limite, no verificacion: entra al espaciamiento "
                        "maximo (paso 10.1) y de ahi a VB1"))


# ===========================================================================
# 3. Espaciamiento maximo (num. 4.1.2.1 d))
# ===========================================================================

def espaciamiento_alivio(L_hidraulico: float, *,
                         longitud_hidraulica: Optional[LongitudHidraulica] = None
                         ) -> Espaciamiento:
    """
    Espaciamiento maximo entre alcantarillas de alivio, Sec. 10:

        espaciamiento_max = min(L_normativo, L_hidraulico)

    `L_hidraulico` es la longitud, en metros, a la que la cuneta agota su
    capacidad admisible frente al caudal aportante: declarada (dato externo
    `L_hidraulico_m`; el programa no sabe con que caudal ni con que periodo
    de retorno la calculo quien la declara), o calculada por
    `longitud_hidraulica` o `longitud_hidraulica_por_tramo` --que entonces
    viaja en el resultado con sus pasos--.

    `L_normativo` sale de `criterios_adoptados.valor('long_max_cuneta')`
    -- 200 m adoptado por el regimen FEN -- y lanza CriterioPendienteError
    si algun dia se deja sin valor.

    ES UN LIMITE Y NO UNA VERIFICACION (INF-5.1.12): su paso no lleva
    veredicto de cumplimiento. Lo que se verifica es el espaciamiento
    ADOPTADO, por tramo, con `verificar_tramo` (VB1).
    """
    if isinstance(L_hidraulico, bool) or not isinstance(L_hidraulico, (int, float)) \
            or not math.isfinite(L_hidraulico) or L_hidraulico <= 0.0:
        raise DatoInvalidoError(
            campo="L_hidraulico",
            valor=L_hidraulico,
            motivo="la longitud por capacidad hidraulica de la cuneta debe "
                   "ser un numero finito positivo (Sec. 10, punto 2)",
        )

    L_normativo = ca.valor(CRITERIO_LONG_MAX_CUNETA)

    if L_hidraulico < L_normativo:
        gobierna = GobiernaEspaciamiento.HIDRAULICO
        espaciamiento_max = L_hidraulico
    else:
        gobierna = GobiernaEspaciamiento.NORMATIVO
        espaciamiento_max = L_normativo

    origen = (ORIGEN_L_DECLARADO if longitud_hidraulica is None
              else ORIGEN_L_CALCULADO)
    procedencia_L = (
        "dato externo `L_hidraulico_m`: longitud a la que la cuneta agota su "
        "capacidad frente a su caudal aportante, declarada (el programa no "
        "conoce el caudal ni el periodo de retorno con que se calculo)"
        if longitud_hidraulica is None else
        f"paso {CODIGO_L_HIDRAULICO}: calculada con la seccion, el "
        "revestimiento y la pendiente de la cuneta y el aporte del punto "
        f"({longitud_hidraulica.metodo_aporte})")

    return Espaciamiento(
        paso=paso(
            "F10.CUNETA",
            codigo=CODIGO_ESPACIAMIENTO,
            que="Espaciamiento maximo entre alcantarillas de alivio",
            formula="espaciamiento_max = min(L_normativo, L_hidraulico)",
            formula_cita_id="MC_HHD.4.1.2.1d",
            citas_textuales=("MC_HHD.4.1.2.1d",),
            sustitucion=(
                Magnitud("L_normativo", L_normativo, "m",
                         f"criterio adoptado '{CRITERIO_LONG_MAX_CUNETA}': el "
                         "numeral da DOS cifras con distinta fuerza y esta es "
                         "la elegida", cifras=CIFRAS_FACTOR),
                Magnitud("L_hidraulico", L_hidraulico, "m", procedencia_L,
                         cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("espaciamiento_max", espaciamiento_max, "m",
                               f"gobierna el limite {gobierna.value}",
                               cifras=CIFRAS_FACTOR),
            umbral=Umbral(
                descripcion="longitud maxima de recorrido de la cuneta",
                valor=L_normativo, unidad="m",
                cita_id="MC_HHD.4.1.2.1d",
                caracter="EXIGENCIA para el maximo de region seca ('sera de "
                         "250 m como maximo') y RECOMENDACION para el de "
                         "region muy lluviosa ('se recomienda reducir esta "
                         "longitud maxima a 200 m'). No son dos lecturas de "
                         "lo mismo: son dos cifras con distinta fuerza en la "
                         "misma frase",
                aplicacion="El proyecto adopta los 200 m -- la cifra "
                           "RECOMENDADA, no la exigida -- por el regimen FEN "
                           "del corredor, que es la lectura conservadora. La "
                           "eleccion es del proyectista y esta declarada en "
                           f"'{CRITERIO_LONG_MAX_CUNETA}'. Es el techo del "
                           "espaciamiento maximo; el espaciamiento ADOPTADO se "
                           "verifica en VB1, por tramo",
                criterio_aplicado=CRITERIO_LONG_MAX_CUNETA),
            veredicto=Veredicto(
                tipo=TipoDeVeredicto.SIN_VEREDICTO,
                margen=L_normativo - espaciamiento_max, unidad="m",
                explicacion="limite, no verificacion: el espaciamiento "
                            "adoptado entre dos alivios se juzga contra el en "
                            "VB1 (INF-5.1.12: hasta T-9 este paso decia "
                            "«cumple» por construccion)"),
            elecciones=(EleccionDeProyecto(
                que_se_adopto="longitud maxima de recorrido de la cuneta",
                valor=f"{L_normativo} m",
                entre=("250 m (region seca o poco lluviosa; «sera ... como "
                       "maximo»)",
                       "200 m (region muy lluviosa; «se recomienda reducir»)"),
                de_donde="el num. 4.1.2.1 d) «Desague de las cunetas», pag. "
                         "impresa 179",
                por_que="el corredor esta en regimen FEN: la region no es "
                        "seca en el evento que dimensiona la obra. Se adopta "
                        "la cifra menor, que es la recomendada y la "
                        "conservadora",
                cita_id="MC_HHD.4.1.2.1d",
                clave_criterio=CRITERIO_LONG_MAX_CUNETA),),
        ),
        L_normativo=L_normativo,
        L_hidraulico=L_hidraulico,
        espaciamiento_max=espaciamiento_max,
        gobierna=gobierna,
        criterio_normativo=CRITERIO_LONG_MAX_CUNETA,
        numeral=NUMERAL_FASE_10,
        origen_L_hidraulico=origen,
        longitud_hidraulica=longitud_hidraulica,
    )


# ===========================================================================
# 4. VB1: el espaciamiento adoptado, por tramo
# ===========================================================================

def _obras_A_son_extremo(id_punto: Optional[str]) -> bool:
    """El criterio de la decision C, con su guardia de segunda linea."""
    eleccion = ca.valor(CRITERIO_OBRA_A_EXTREMO)
    if eleccion not in (OBRA_A_ES_EXTREMO, OBRA_A_NO_ES_EXTREMO):
        raise DatoInvalidoError(
            CRITERIO_OBRA_A_EXTREMO, valor=eleccion, id_punto=id_punto,
            motivo=f"los valores admitidos son {OBRA_A_ES_EXTREMO} y "
                   f"{OBRA_A_NO_ES_EXTREMO}")
    return eleccion == OBRA_A_ES_EXTREMO


def _progresiva_valida(campo: str, valor: float, id_punto: str) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) \
            or not (math.isfinite(valor) and valor >= 0):
        raise DatoInvalidoError(
            campo, valor=valor, id_punto=id_punto,
            motivo="una progresiva es un numero finito no negativo, en km")
    return float(valor)


def extremo_del_tramo(*, id_punto: str, progresiva_km: float,
                      inicio_declarado_km: Optional[float],
                      obras: Sequence[Tuple[str, Familia, float]]
                      ) -> ExtremoDeTramo:
    """
    --- T-9 (correcciones de la auditoria, H3 y decision C) --- El extremo del
    tramo de cuneta que VB1 mide para la alcantarilla de alivio `id_punto`:
    el de su lado de PROGRESIVAS MENORES (el sentido del flujo no es dato).

    `obras` son todas las obras del CSV, (id, familia, progresiva_km), en el
    orden del CSV (que desempata dos obras en la misma progresiva). Por orden:

      1. `inicio_declarado_km` (dato externo `inicio_tramo_cuneta_km`), que
         GANA; no puede ser POSTERIOR a la obra (DatoInvalidoError nombrando
         el par): el dato es el extremo del lado de progresivas menores.
      2. La obra anterior en progresiva que cierre el tramo: una de Familia B
         siempre; una de Familia A si el criterio
         'obras_familia_a_extremo_de_cuneta' vale «si» (DG-2018 num. 304.11,
         `Interpretacion` del registro). Una de Familia C no: es un cruce de
         canal, no un desague de la cuneta.
      3. Ninguna: el extremo es None y VB1 no se evalua (H2: el servicio lo
         registra como bloqueo que espera `inicio_tramo_cuneta_km`).

    Y los HUECOS que VB1 no mira, como avisos (H3): la cuneta entre la obra
    anterior y un inicio declarado posterior a ella, y la del lado de
    progresivas mayores del alivio cuando la obra siguiente no es otro
    alivio (que la mediria como su propio tramo) o no hay ninguna.
    """
    prog = _progresiva_valida("progresiva_km", progresiva_km, id_punto)
    familias_extremo = ((Familia.B, Familia.A) if _obras_A_son_extremo(id_punto)
                        else (Familia.B,))
    nodos = [o for o in obras if o[0] == id_punto or o[1] in familias_extremo]
    ordenados = sorted(nodos, key=lambda o: o[2])          # estable: CSV
    pos = next(k for k, o in enumerate(ordenados) if o[0] == id_punto)
    anterior = ordenados[pos - 1] if pos > 0 else None
    siguiente = ordenados[pos + 1] if pos + 1 < len(ordenados) else None
    avisos = []

    familia_extremo: Optional[Familia] = None
    if inicio_declarado_km is not None:
        inicio = _progresiva_valida("inicio_tramo_cuneta_km",
                                    inicio_declarado_km, id_punto)
        if inicio > prog + TOL_UMBRAL_NORMATIVO:
            raise DatoInvalidoError(
                "inicio_tramo_cuneta_km / progresiva_km",
                valor=f"{inicio:g} km / {prog:g} km", id_punto=id_punto,
                motivo="el inicio declarado del tramo de cuneta es POSTERIOR "
                       "a la obra: `inicio_tramo_cuneta_km` es el extremo del "
                       "tramo del lado de progresivas menores del alivio, y "
                       "no se acepta en silencio un tramo que empieza "
                       "despues de su desague")
        extremo, prog_extremo, origen = (EXTREMO_DECLARADO, inicio,
                                         ORIGEN_EXTREMO_DECLARADO)
        if anterior is not None and \
                anterior[2] < inicio - TOL_UMBRAL_NORMATIVO:
            hueco = (inicio - anterior[2]) * METROS_POR_KM
            avisos.append(
                f"tramo de cuneta que VB1 no mira: entre {anterior[0]} (km "
                f"{anterior[2]:.3f}) y el inicio declarado del tramo de "
                f"{id_punto} (km {inicio:.3f}) quedan {hueco:.1f} m; si en "
                f"ellos hay cuneta, descarga en otra obra y ninguna "
                f"verificacion mide su longitud")
    elif anterior is not None:
        extremo, prog_extremo = anterior[0], anterior[2]
        familia_extremo = anterior[1]
        origen = (ORIGEN_EXTREMO_OBRA_B if anterior[1] is Familia.B
                  else ORIGEN_EXTREMO_OBRA_A)
    else:
        extremo, prog_extremo, origen = None, None, ORIGEN_EXTREMO_NINGUNO

    if siguiente is None:
        avisos.append(
            f"tramo de cuneta que VB1 no mira: del lado de progresivas "
            f"mayores de {id_punto} (km {prog:.3f}) no hay obra que cierre el "
            f"tramo; VB1 mide, de cada alivio, el tramo del lado de "
            f"progresivas menores, y la longitud de esa cuneta no se "
            f"verifica")
    elif siguiente[1] is not Familia.B:
        tramo_siguiente = (siguiente[2] - prog) * METROS_POR_KM
        avisos.append(
            f"tramo de cuneta que VB1 no mira: los {tramo_siguiente:.1f} m "
            f"entre {id_punto} (km {prog:.3f}) y {siguiente[0]} (km "
            f"{siguiente[2]:.3f}, Familia {siguiente[1].value}) desaguan en "
            f"una de las dos obras y ninguna verificacion mide su longitud "
            f"(VB1 mide, de cada alivio, el tramo del lado de progresivas "
            f"menores)")
    return ExtremoDeTramo(
        id_punto=id_punto, progresiva_km=prog, extremo=extremo,
        progresiva_extremo_km=prog_extremo, origen_extremo=origen,
        familia_extremo=familia_extremo, avisos=tuple(avisos))


def _criterio_que_gobierna(e: Espaciamiento) -> Optional[str]:
    """La clave del criterio que fija el maximo de ese extremo, o None."""
    if e.gobierna is GobiernaEspaciamiento.NORMATIVO:
        return e.criterio_normativo
    if e.longitud_hidraulica is not None:
        return CRITERIO_SECCION_CUNETA
    return None          # L_hidraulico declarado: es un dato, no un criterio


def verificar_tramo(*, id_punto: str, progresiva_km: float,
                    extremo: Optional[str],
                    progresiva_extremo_km: Optional[float],
                    origen_extremo: str,
                    maximos: Sequence[Tuple[str, Optional[Espaciamiento]]],
                    obra_de_familia_a: bool = False,
                    avisos: Sequence[str] = ()) -> TramoDeAlivio:
    """
    VB1: el tramo de cuneta que descarga en el alivio `id_punto`, del
    extremo de su lado de progresivas menores al punto, no puede exceder el
    espaciamiento maximo (num. 4.1.2.1 d), pag. impresa 179; hoja de ruta
    Fase 10):

        s = |progresiva − progresiva_extremo| · 1000   <=   min(maximos)

    `maximos` son los espaciamientos maximos de las alcantarillas de alivio
    que delimitan el tramo, con su id: los dos cuando el extremo es la obra
    B anterior -- el sentido del flujo entre dos alivios no es dato, y se
    toma el menor de los dos, que es el lado seguro --, o solo el del punto
    cuando el extremo es el inicio declarado o una obra de Familia A
    (`obra_de_familia_a`, que ademas pone en el paso la eleccion del
    criterio 'obras_familia_a_extremo_de_cuneta' y su lectura del DG-2018).
    Un `None` es un extremo cuya Fase 10 no cerro: entonces solo se puede
    verificar contra el limite normativo, y solo si el tramo ya lo excede
    (el maximo nunca lo supera).

    CUANDO VB1 NO SE EVALUA (H2 de la auditoria de T-9) el resultado lleva en
    `falta` el dato que la destraba --`inicio_tramo_cuneta_km` sin extremo,
    `L_hidraulico_m` con un maximo desconocido-- y el servicio lo registra
    como `Bloqueo` del punto: una verificacion de la aceptacion de la
    Familia B que no se evaluo no puede dejar el expediente cerrado.
    `avisos` son los huecos de cuneta que VB1 no mira (`extremo_del_tramo`).
    """
    avisos = tuple(avisos)
    if extremo is None or progresiva_extremo_km is None:
        return TramoDeAlivio(
            id_punto=id_punto, progresiva_km=progresiva_km, extremo=None,
            progresiva_extremo_km=None, origen_extremo=ORIGEN_EXTREMO_NINGUNO,
            longitud_m=None, verificacion=None, aviso=AVISO_TRAMO_SIN_EXTREMO,
            falta=FALTA_EXTREMO, avisos=avisos)
    _progresiva_valida("progresiva_km", progresiva_km, id_punto)
    _progresiva_valida("inicio_tramo_cuneta_km", progresiva_extremo_km,
                       id_punto)
    s = abs(progresiva_km - progresiva_extremo_km) * METROS_POR_KM
    conocidos = [(i, e) for i, e in maximos if e is not None]
    faltan = [i for i, e in maximos if e is None]
    L_normativo = ca.valor(CRITERIO_LONG_MAX_CUNETA)

    if faltan and not s > L_normativo + TOL_UMBRAL_NORMATIVO:
        return TramoDeAlivio(
            id_punto=id_punto, progresiva_km=progresiva_km, extremo=extremo,
            progresiva_extremo_km=progresiva_extremo_km,
            origen_extremo=origen_extremo, longitud_m=s, verificacion=None,
            aviso=(f"VB1 (espaciamiento entre alivios) NO SE EVALUO: el tramo "
                   f"de {s:.1f} m entre {extremo} y {id_punto} no excede el "
                   f"limite normativo ({L_normativo:g} m), pero el "
                   f"espaciamiento maximo de {', '.join(faltan)} no se conoce "
                   f"(su Fase 10 no cerro: ver sus bloqueos) y la longitud "
                   f"por capacidad podria ser menor"),
            falta=FALTA_MAXIMO, avisos=avisos)

    if faltan:
        admisible, de_quien, criterio = (L_normativo, "limite normativo",
                                         CRITERIO_LONG_MAX_CUNETA)
        nota = (f"El espaciamiento maximo de {', '.join(faltan)} no se conoce "
                f"(su Fase 10 no cerro), pero ningun espaciamiento maximo "
                f"supera el limite normativo de {L_normativo:g} m y el tramo "
                f"ya lo excede: VB1 no cumple sea cual sea la longitud por "
                f"capacidad.")
    else:
        de_quien, e_min = min(conocidos, key=lambda par: par[1].espaciamiento_max)
        admisible = e_min.espaciamiento_max
        criterio = _criterio_que_gobierna(e_min)
        nota = ""
        if len(conocidos) > 1:
            nota = ("El tramo esta entre dos alcantarillas de alivio y el "
                    "sentido del flujo en la cuneta no es dato: se toma el "
                    "MENOR de sus dos espaciamientos maximos ("
                    + ", ".join(f"{i}: {e.espaciamiento_max:.1f} m"
                                for i, e in conocidos)
                    + "), que es el lado seguro.")
    citas = ["MC_HHD.4.1.2.1d"]
    elecciones: Tuple[EleccionDeProyecto, ...] = ()
    if obra_de_familia_a:
        citas += ["DG2018.304.11#DESAGUE", "MC_HHD.4.1.2.1d#ALIVIO"]
        nota = " ".join(t for t in (nota, _lectura("DG2018.304.11#DESAGUE"))
                        if t)
        elecciones = (EleccionDeProyecto(
            que_se_adopto="obra de Familia A como extremo del tramo de cuneta",
            valor=f"{OBRA_A_ES_EXTREMO}: {extremo}",
            entre=(f"{OBRA_A_ES_EXTREMO}: la obra de Familia A anterior "
                   "cierra el tramo",
                   f"{OBRA_A_NO_ES_EXTREMO}: solo una obra de Familia B o un "
                   "inicio declarado"),
            de_donde=f"el criterio adoptado '{CRITERIO_OBRA_A_EXTREMO}' [A]",
            por_que="una alcantarilla de paso de quebrada es una obra de "
                    "drenaje transversal, y el DG-2018 conduce las cunetas "
                    "hacia ellas; el Manual nombra solo las alcantarillas de "
                    "alivio",
            cita_id="DG2018.304.11#DESAGUE",
            clave_criterio=CRITERIO_OBRA_A_EXTREMO),)
    cumple = s <= admisible + TOL_UMBRAL_NORMATIVO
    paso_tramo = paso(
        "F10.TRAMO", codigo=CODIGO_TRAMO,
        que="VB1 - Espaciamiento adoptado entre la alcantarilla de alivio y "
            "el extremo de su tramo de cuneta",
        formula="s = |progresiva − progresiva_extremo| · 1000 <= "
                "espaciamiento_max",
        formula_cita_id="MC_HHD.4.1.2.1d",
        citas_textuales=tuple(citas),
        sustitucion=(
            Magnitud("progresiva", progresiva_km, "km",
                     f"columna progresiva_km de {id_punto}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("progresiva_extremo", progresiva_extremo_km, "km",
                     f"{extremo}: {origen_extremo}", cifras=CIFRAS_MAGNITUD),
            Magnitud("s", s, "m", "longitud del tramo de cuneta",
                     cifras=CIFRAS_FACTOR),
            Magnitud("espaciamiento_max", admisible, "m",
                     f"de {de_quien} (Fase 10)", cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("s", s, "m", "espaciamiento adoptado",
                           cifras=CIFRAS_FACTOR),
        umbral=Umbral(
            descripcion="espaciamiento maximo entre alcantarillas de alivio",
            valor=admisible, unidad="m", cita_id="MC_HHD.4.1.2.1d",
            caracter="EXIGENCIA de la fuente para el recorrido maximo de la "
                     "cuneta en region seca o poco lluviosa (250 m, con "
                     "justificacion tecnica para mas) y RECOMENDACION en "
                     "region muy lluviosa (200 m); la longitud por capacidad "
                     "es la condicion del num. 4.1.2.1 a) y b)",
            aplicacion="Umbral DURO POR ADOPCION del proyecto: el tramo de "
                       "cuneta no puede exceder el menor del recorrido maximo "
                       "adoptado ('long_max_cuneta') y la longitud por "
                       "capacidad. El remedio de un incumplimiento es otro "
                       "alivio, o una cuneta de mas capacidad si gobierna el "
                       "limite hidraulico",
            criterio_aplicado=criterio),
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.CUMPLE if cumple
                  else TipoDeVeredicto.NO_CUMPLE),
            margen=admisible - s, unidad="m",
            explicacion=("el tramo de cuneta no excede el espaciamiento "
                         "maximo" if cumple else
                         "el tramo de cuneta excede el espaciamiento maximo: "
                         "hace falta otra alcantarilla de alivio entre "
                         f"{extremo} y {id_punto}, o declarar con su "
                         "procedencia donde empieza de verdad la cuneta que "
                         "descarga en el alivio (`inicio_tramo_cuneta_km`)")),
        elecciones=elecciones,
        nota_del_proyecto=nota)
    verificacion = Verificacion(
        cumple=cumple, numeral=NUMERAL_FASE_10, valor_obtenido=s,
        valor_admisible=admisible, criterio_aplicado=criterio,
        codigo=CODIGO_VB1, paso=paso_tramo)
    return TramoDeAlivio(
        id_punto=id_punto, progresiva_km=progresiva_km, extremo=extremo,
        progresiva_extremo_km=progresiva_extremo_km,
        origen_extremo=origen_extremo, longitud_m=s,
        verificacion=verificacion, aviso="", avisos=avisos)
