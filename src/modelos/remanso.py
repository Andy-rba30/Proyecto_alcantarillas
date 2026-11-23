"""
src/modelos/remanso.py
======================
Geometria del marco, remanso del canal, V5 y V8 con metodo, derecho de via y evento extremo.

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Tuple


if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.base import ControlGobernante
    from src.modelos.hidraulica import SeccionReceptor
    from src.modelos.memoria import PasoDeMemoria

# ===========================================================================
# --- T-3 --- (cadena T, INF-0.4) La geometria del marco y el remanso del
# canal. Viven aqui por la regla de la casa: fluyen de M7 al servicio, a la
# CLI, al JSON y a M11. Integrado T-3 detras de T-5, `GeometriaMarco` no
# tiene consumidor en M8 -- `M8.demanda_marco` lee la `Seccion`,
# `espesor_pared` y la misma `M5.cota_clave`, con los mismos numeros -- y
# queda para la demanda de la losa y el cabezal por punto (T-7a) cuando se
# toquen (ficha T3-06).
# ===========================================================================

@dataclass(frozen=True)
class GeometriaMarco:
    """
    La geometria del marco adoptado, en SI y en cotas msnm (Sec. 7.A/7.B).

    UN SOLO ESPESOR para paredes, losas y tabique: el criterio
    'espesor_pared_cajon' [A] es uno, y separarlo en tres seria inventar dos
    adopciones que nadie declaro. Con N celdas el marco es MONOLITICO --
    vaciado in situ, §14.1 de docs/ruta_familia_c.md --: las celdas
    comparten tabique y entre ellas no hay relleno, de modo que el ancho
    exterior es N*B + (N-1)*t + 2*t.

    Las cotas se apilan sobre el fondo INTERIOR de la entrada (el invert, la
    superficie por donde corre el agua): la clave interior a H, la exterior a
    H + t -- que es la MISMA que `M5.cota_clave` le da a V7 y a 7.A --, y la
    base exterior a t por debajo. `relleno_sobre_losa_m` es la subrasante
    menos la clave exterior, la altura de relleno que la Fase 8 carga.
    """
    B_m: float
    H_m: float
    celdas: int
    espesor_m: float
    tabique_m: float                 # 0.0 con una sola celda
    ancho_exterior_m: float
    canto_exterior_m: float
    cota_fondo_interior_msnm: float
    cota_clave_interior_msnm: float
    cota_clave_exterior_msnm: float
    cota_base_exterior_msnm: float
    cota_subrasante_msnm: float
    relleno_sobre_losa_m: float
    paso: Optional["PasoDeMemoria"] = None


@dataclass(frozen=True)
class RemansoCanal:
    """
    La sobreelevacion de la lamina del canal en el cruce y la longitud
    MINIMA del remanso aguas arriba (Familia C). Es un AVISO: ninguna fuente
    de normas/ fija un umbral, y no hay verificacion que lo juzgue.

    `evaluado` es False cuando falta la seccion medida del canal: entonces
    no hay numeros y `aviso` dice que falta. Con ella:

      y_normal_canal_m    tirante normal del canal en el cruce (Manning en
                          la seccion medida, con el caudal del canal)
      y_critico_canal_m   --- T-3 (auditoria, H2) --- tirante critico del
                          canal en la misma seccion (Q^2 T = g A^3)
      sobreelevacion_m    HW - y_normal: cuanto levanta la obra la lamina
                          sobre la que el canal tendria sin ella. Negativa o
                          nula, la obra no la levanta.
      longitud_minima_m   sobreelevacion / S_canal: la distancia aguas arriba
                          a la que la lamina horizontal del embalse corta la
                          lamina normal. Es una COTA INFERIOR solo en un
                          canal SUAVE (y_normal > y_critico): el perfil M1
                          real queda por encima de esa horizontal y se
                          extiende mas alla, asintotico al normal.

    --- T-3 (auditoria adversarial, H2 y H3) --- `concluye` es False, con la
    razon en `motivo_no_concluye` y en `aviso`, en dos casos en que la cuenta
    de arriba NO dice lo que parece, y entonces `longitud_minima_m` va en
    None -- ninguna cifra se presenta como cota --:
      - canal de pendiente FUERTE (y_normal <= y_critico): el remanso es una
        S1 que termina en resalto aguas arriba, y la horizontal no lo acota
        (puede ser mas corto que sobreelevacion / S). La sobreelevacion en
        el cruce si se publica: es HW - y_normal, un hecho de la seccion.
      - VC2 fuera de tolerancia: el HW de la obra sale de una descarga en
        caida libre a la salida, que el canal no tiene porque el empalme no
        cierra; ni la sobreelevacion ni la longitud se publican.
    """
    evaluado: bool
    aviso: str
    seccion_origen: str = ""
    Q_canal_m3s: Optional[float] = None
    S_canal: Optional[float] = None
    y_normal_canal_m: Optional[float] = None
    HW_m: Optional[float] = None
    cota_lamina_entrada_msnm: Optional[float] = None
    sobreelevacion_m: Optional[float] = None
    longitud_minima_m: Optional[float] = None
    paso: Optional["PasoDeMemoria"] = None
    concluye: bool = False
    y_critico_canal_m: Optional[float] = None
    motivo_no_concluye: str = ""
    # --- VE-3.7 --- La longitud del remanso por el PERFIL (paso directo,
    # `M3.perfil_remanso_trapecial`) y como se obtuvo: en un canal fuerte,
    # la S1 hasta el resalto (el conjugado del tirante normal); en uno
    # suave, la M1 hasta (1 + fraccion) y_n si el criterio
    # 'fraccion_fin_remanso_canal' esta declarado. None si no se calculo.
    longitud_remanso_m: Optional[float] = None
    metodo_longitud: str = ""
    y_conjugado_canal_m: Optional[float] = None


# ===========================================================================
# --- T-7b --- (cadena T) · V5 y V8 con metodo, y el ensamble de estabilidad
# ===========================================================================

# Los rotulos de `MetodoNoEvaluableError` de T-7b: cada uno nombra SU fuente
# (leccion de T-1 y T-8: encabezarlo con «HDS-5 3.24» seria una cita falsa).
MOTIVO_METODO_NO_EVALUABLE_REMANSO = (
    "método no evaluable (V5, embalse a nivel aguas arriba)")
MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO = (
    "método no evaluable (V8, evento extremo)")
MOTIVO_METODO_NO_EVALUABLE_CABEZAL = (
    "método no evaluable (AASHTO LRFD 11.6, estabilidad del cabezal)")

# Las opciones del criterio 'remanso_derecho_via' (V5), que desde T-7b elige
# el METODO. Las tres estan implementadas: «embalse_a_nivel» (T-7b),
# «cota_de_afectacion» (cierre de T-7b) y el perfil de remanso paso a paso
# (VE-4c, ficha T7B-01).
METODO_REMANSO_EMBALSE_A_NIVEL = "embalse_a_nivel"
# --- correcciones de T-7b (H2) --- el criterio de COTA que el HDS-5 num.
# 2.2.5 si sostiene: la cota del embalse de diseño contra la cota de
# afectacion aguas arriba (dato externo por punto).
METODO_REMANSO_COTA_AFECTACION = "cota_de_afectacion"
METODO_REMANSO_PERFIL_PASO_A_PASO = "perfil_de_remanso_paso_a_paso"
METODOS_DE_REMANSO = (METODO_REMANSO_EMBALSE_A_NIVEL,
                      METODO_REMANSO_COTA_AFECTACION,
                      METODO_REMANSO_PERFIL_PASO_A_PASO)

# Las opciones del criterio 'umbral_no_colapso_evento_extremo' (V8).
UMBRAL_V8_SIN_DESBORDE = "sin_desborde_de_la_plataforma"
UMBRAL_V8_DESBORDE_ADMITIDO = "desborde_admitido_con_terraplen_protegido"
UMBRALES_V8 = (UMBRAL_V8_SIN_DESBORDE, UMBRAL_V8_DESBORDE_ADMITIDO)


@dataclass(frozen=True)
class DerechoDeViaDelPunto:
    """
    --- T-7b --- Lo que V5 necesita del punto ademas del resultado
    hidraulico: el ancho del derecho de via declarado para ese cruce (dato
    externo `ancho_derecho_via_m`, None si no se declaro) y donde queda la
    boca de entrada respecto del eje de la via, medido a lo largo del eje
    del conducto (la semilongitud de entrada de 7.B, o L/2 si la longitud se
    declaro). Lo arma el servicio; V5 no lee el informe.
    """

    ancho_m: Optional[float]
    origen_ancho: str
    semilongitud_entrada_m: Optional[float]
    origen_semilongitud: str
    # El piso del DG-2018 (Tabla 304.09 por clase de via), si la clase de via
    # esta declarada: es un CONTRASTE del dato, no lo sustituye.
    piso_dg2018_m: Optional[float] = None
    origen_piso: str = ""
    # --- correcciones de T-7b (H2) --- la cota del terreno o del bien a
    # proteger en el limite del derecho de via aguas arriba (dato externo
    # `cota_afectacion_aguas_arriba_msnm`, None si no se declaro): la lee el
    # metodo «cota_de_afectacion».
    cota_afectacion_msnm: Optional[float] = None
    origen_cota_afectacion: str = ""
    # --- VE-4c --- (ficha T7B-01) la seccion del cauce de APROXIMACION
    # (dato externo `seccion_cauce_aproximacion`, None si no se declaro), que
    # lee el metodo «perfil_de_remanso_paso_a_paso», y la funcion con que el
    # servicio calcula su remanso (`M3.remanso_aguas_arriba`: M3, que M5 no
    # importa, como el `resolver` de V8).
    seccion_cauce: Optional["SeccionReceptor"] = None
    origen_seccion_cauce: str = ""
    remanso_aguas_arriba: Optional[Any] = None   # (Q, seccion, HW, Δ) -> RemansoAguasArriba


# --- VE-4c --- EL REMANSO DEL CAUCE DE APROXIMACION (V5 por el perfil).
# El rotulo propio: el del embalse a nivel nombra OTRO metodo.
MOTIVO_METODO_NO_EVALUABLE_REMANSO_PERFIL = (
    "método no evaluable (V5, perfil de remanso aguas arriba)")
# Que rama del perfil remansa el cauce: la M1 de un cauce suave, la S1 de uno
# fuerte (hasta el resalto) o ninguna (la carga no supera lo que el cauce ya
# lleva mas la sobreelevacion admisible, o el resalto queda en la boca).
RAMA_REMANSO_M1 = "M1"
RAMA_REMANSO_S1 = "S1"
RAMA_REMANSO_NINGUNA = "sin remanso sobre el admisible"


@dataclass(frozen=True)
class RemansoAguasArriba:
    """
    --- VE-4c --- El remanso que la obra forma en el cauce de aproximacion,
    por paso directo desde la boca (`M3.remanso_aguas_arriba`): hasta donde
    la lamina queda MAS de una sobreelevacion admisible por encima del
    tirante natural del cauce (el normal de Manning en su seccion).

    `longitud_m` es la distancia aguas arriba de la boca, sobre el eje del
    cauce, en que el perfil baja a `y_fin_m`; 0 si la obra no remansa por
    encima del admisible; None si el perfil es ASINTOTICO (M1 con
    sobreelevacion admisible nula) y no tiene final: `asintotico` lo dice.
    """

    y_normal_m: float
    y_critico_m: float
    suave: bool
    rama: str
    y_conjugado_m: Optional[float]
    y_fin_m: Optional[float]
    longitud_m: Optional[float]
    asintotico: bool = False
    estaciones: Tuple[Tuple[float, float], ...] = ()


@dataclass(frozen=True)
class EventoExtremoDelPunto:
    """
    --- T-7b --- Lo que V8 necesita ademas del resultado de diseño: el caudal
    y el tirante del receptor del evento extremo (datos externos, None si no
    se declararon), la cota a la que la plataforma desborda (el borde de la
    plataforma del lado de la entrada, de 7.B, o la rasante) y la funcion con
    que el servicio resuelve la hidraulica de la seccion adoptada para ese
    caudal (M3 y M4, que M5 no importa).
    """

    Q_m3s: Optional[float]
    TW_m: Optional[float]
    origen: str
    cota_desborde: Optional[float]
    origen_cota_desborde: str
    # (seccion, material, Q=None) -> HidraulicaDelEventoExtremo: la carga de
    # la seccion con el caudal Q (el del evento si Q es None).
    resolver: Optional[Any] = None
    # --- VE-4d --- El umbral «desborde_admitido_con_terraplen_protegido»:
    # la longitud de la cresta del vertedero que forma la plataforma (dato
    # externo `longitud_cresta_desborde_m`, None si no se declaro), y la
    # funcion con que el servicio REPARTE el caudal del evento entre el
    # conducto y la plataforma (`M4.repartir_caudal_con_desborde`, que M5 no
    # importa): (seccion, material, superficie, coeficientes, HW_minimo,
    # Q_minimo) -> RepartoDelDesborde.
    longitud_cresta_m: Optional[float] = None
    origen_longitud_cresta: str = ""
    repartir: Optional[Any] = None


# Los dos regimenes con que V8 resuelve el caudal del evento extremo
# (correcciones de T-7b, H3).
REGIMEN_EVENTO_LAMINA_LIBRE = "lamina libre"
REGIMEN_EVENTO_A_PRESION = "barril a presion"


@dataclass(frozen=True)
class HidraulicaDelEventoExtremo:
    """
    --- correcciones de T-7b (H3) --- La carga del caudal del evento extremo
    por la seccion candidata, y COMO se obtuvo: en lamina libre, con la
    hidraulica completa de M4 (`resolver_control`); o, cuando M3 no le
    encuentra tirante normal porque el caudal no cabe en lamina libre, con
    el barril trabajando A PRESION, con las MISMAS piezas de M4 que no
    necesitan tirante normal: el control de entrada (la ec. A.3 sumergida,
    o la que corresponda a su q*) y el de salida a barril lleno (HW = H +
    h_o - S·L), gobernando la mayor (`M4.hw_gobernante`). Ninguna ecuacion
    nueva.

    --- verificacion de T-7 (punto 3) --- «sin perfil» ERA EL DEFECTO: la
    aproximacion de barril lleno competia sin las dos reglas que el mismo M4
    aplica en lamina libre (HDS-5 num. 3.3.3, pag. 3.24), y un caudal MAYOR
    podia dar MENOS carga que el de diseño. Ahora compite con el perfil de
    la lamina (`M4.perfil_lamina`, que no necesita tirante normal):
    `HW_salida` es la carga EFECTIVA de salida y `avisos` dice cuando la
    aproximacion estuvo en la banda de cautela o no se uso. Salen por
    `Verificacion.avisos` de V8 y de ahi por `InformePunto.avisos()`.
    """

    HW: float
    control_gobernante: "ControlGobernante"
    regimen: str
    HW_entrada: float
    HW_salida: float
    nota: str = ""
    avisos: Tuple[str, ...] = ()


# --- VE-4d --- Las dos superficies de la cresta que la Figura 3.11 del HDS-5
# distingue («Paved» y «Gravel»): las claves de las curvas en el criterio
# 'coeficientes_desborde_plataforma'.
SUPERFICIE_CRESTA_PAVIMENTADA = "pavimentada"
SUPERFICIE_CRESTA_GRAVA = "grava"
SUPERFICIES_CRESTA = (SUPERFICIE_CRESTA_PAVIMENTADA, SUPERFICIE_CRESTA_GRAVA)
# Los dos paneles de la Figura 3.11 que dan C_r: A) HW_r/L_r > 0.15
# (desborde profundo) y B) HW_r/L_r <= 0.15 (somero).
PANEL_DESBORDE_PROFUNDO = "A (HW_r/L_r > limite)"
PANEL_DESBORDE_SOMERO = "B (HW_r/L_r <= limite)"


@dataclass(frozen=True)
class RepartoDelDesborde:
    """
    --- VE-4d --- El reparto del caudal del evento extremo entre el conducto
    y la plataforma (HDS-5 num. 3.1.5, Ec. 3.9), a la cota del agua comun a
    los dos: Q_total = Q_conducto + Q_plataforma. Lo calcula
    `M4.repartir_caudal_con_desborde` por tanteo sobre el caudal del
    conducto, como manda la fuente («A trial and error process is
    necessary»).

    `desborda` es False cuando el embalse con TODO el caudal por el conducto
    no alcanza la cresta: entonces Q_plataforma = 0 y los coeficientes del
    vertedero no se leen (None). Las alturas se miden desde la cresta (HW_r)
    y la cota del agua de aguas abajo sobre ella (h_t, 0 si no la alcanza).
    """

    Q_total: float
    Q_conducto: float
    Q_plataforma: float
    cota_embalse: float
    HW_conducto: float                  # m sobre la solera de entrada
    hidraulica: "HidraulicaDelEventoExtremo"
    desborda: bool
    cota_cresta: float
    longitud_cresta: float              # L de la Ec. 3.9, m
    ancho_cresta: float                 # L_r de la Figura 3.11, m
    HW_r: float = 0.0
    h_t: float = 0.0
    panel: str = ""
    # --- VE-5 fixve4 --- C_r EN SI (m^0.5/s), como lo usa la Ec. 3.9; hasta
    # aqui viajaba en ft^0.5/s, la unidad de la figura.
    C_r_si: Optional[float] = None
    k_t: Optional[float] = None
    C_d_si: Optional[float] = None      # = k_t * C_r_si, m^0.5/s
    q_unitario: float = 0.0             # Q_plataforma / L, m2/s
    avisos: Tuple[str, ...] = ()

    @property
    def C_r_figura(self) -> Optional[float]:
        """
        El C_r como lo lee la Figura 3.11 del HDS-5, en ft^0.5/s:
        C_r_si / 0.552 (constantes_normativas.K_CD_DESBORDE_SI). Es
        conversion de PRESENTACION, para que la memoria muestre la lectura
        de la figura: el calculo entero sigue en SI (como
        `TamizadoRasante.delta_rasante_cm`).
        """
        if self.C_r_si is None:
            return None
        from src.constantes_normativas import K_CD_DESBORDE_SI
        return self.C_r_si / K_CD_DESBORDE_SI


@dataclass(frozen=True)
class DatosDeExpediente:
    """--- T-7b --- Los datos de expediente que la Fase 5 recibe del servicio."""

    derecho_de_via: Optional[DerechoDeViaDelPunto] = None
    evento_extremo: Optional[EventoExtremoDelPunto] = None
    # --- VE-3.6 --- VC3 (Familia C): el desnivel F que el perfil del canal
    # provee en el cruce (`desnivel_perfil_canal_m` de --datos-externos).
    desnivel_perfil_canal_m: Optional[float] = None
    # --- VE-5 (item 18, fichas EXT-2-01 y T3-05) --- V6: si el cauce del
    # punto arrastra palizada, troncos o material de cauce
    # (`arrastre_de_solidos` de --datos-externos, booleano, [S] por punto de
    # la inspeccion del cauce), con su origen. None si no se declaro.
    arrastre_de_solidos: Optional[bool] = None
    origen_arrastre: str = ""
