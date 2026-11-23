"""
src/modelos/rasante_espaciamiento.py
====================================
Fase 7 (compatibilidad geometrica, longitud y pendiente de 7.B) y Fase 10 (espaciamiento y cuneta).

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple

from src.dominios import CENTIMETROS_POR_METRO
from src.dominios import METROS_POR_KM                     # --- T-9 ---

from src.modelos.errores import DisenoNoFactibleError
from src.modelos.base import CondicionRasante, ReferenciaNormativa
from src.modelos.memoria import Verificacion

if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.base import (
        CotaDeEntrada, Familia, GobiernaEspaciamiento, PuntoCritico
    )
    from src.modelos.conducto import Seccion
    from src.modelos.hidrologia import CaudalDeDiseno
    from src.modelos.memoria import PasoDeMemoria
    from src.modelos.remanso import GeometriaMarco, RemansoCanal

# ===========================================================================
# Fase 7 - Compatibilidad geometrica (salida de M7)
# ===========================================================================

@dataclass(frozen=True)
class TamizadoRasante:
    """
    Salida del tamizado previo de Sec. 7.A: la cota de rasante minima que el
    punto admite, como MAXIMO de las dos condiciones, y cuanto le falta a la
    rasante actual para alcanzarla.

        cota rasante >= max( cota clave + h_rec + e_paq ,
                             cota entrada + HW + resguardo(CBR) + e_paq )

    Se guardan las DOS cotas por separado, no solo el maximo, porque la
    memoria tiene que poder mostrar por cuanto quedo descartada la condicion
    que no gobierna: una diferencia de 2 cm entre ambas significa que
    cualquier ajuste de diametro cambia cual manda.

    `delta_rasante_m` y `factible` los calcula M7 con la tolerancia de
    `tolerancias.py` y viajan como campos, no como propiedades derivadas, para
    que el objeto no vuelva a comparar floats por su cuenta. Son coherentes
    con `cota_rasante_min` y `cota_rasante_actual` por construccion.

    `criterio_recubrimiento` es hoy siempre 'cobertura_minima_aashto': el
    recubrimiento minimo ya no es un escalar leido por material sino el mayor
    entre el minimo de EG-2013 (que solo existe para HDPE) y la cobertura
    minima de la Tabla 12.6.6.3-1 de AASHTO LRFD, y esa tabla entra en los
    TRES materiales. Antes era None en HDPE -- donde el 0.30 m se leia como
    [N] puro -- y 'h_relleno_min_concreto_tmc' en los otros dos; el campo
    sigue siendo Optional porque un h_rec que algun dia vuelva a salir solo de
    EG-2013 no tendria criterio que declarar.

    `criterio_resguardo` es siempre 'resguardo_HW_subrasante', [N->] por
    analogia declarada (Sec. 5.1).

    LA CLAVE ES LA FISICA, no la hidraulica: `cota_clave` = cota de entrada +
    altura interior + espesor de pared. EG-2013 508.07 mide el relleno minimo
    "desde la clave de la tuberia", que es la superficie exterior (MAT-D4).

    LOS DOS CAMPOS DE GEOMETRIA SE LLAMABAN `D_supuesto` Y `D_exterior`, y en
    C7 dejaron de poder llamarse asi. No es cosmetica: eran dos nombres de
    DIAMETRO para dos cosas que en un marco no son un diametro y ademas NO SON
    LA MISMA DIMENSION.

      `altura_supuesta`  es la INTERIOR y VERTICAL: el D de un tubo, la H de
          una celda de marco. Es la que se apila sobre la cota de entrada para
          dar la clave, y la que entra en Manning.
      `ancho_exterior`   es el Bc del Art. 12.6.6.3 de AASHTO, "outside
          diameter or WIDTH of the structure": HORIZONTAL. En un circulo
          coincide con altura + 2t y por eso un solo campo bastaba; en un
          marco son B + 2t y H + 2t, dos numeros distintos, y el nombre viejo
          obligaba a elegir uno de los dos sin decir cual. Esa es exactamente
          la confusion que dejaba a un marco recibiendo la cobertura de la
          fila del tubo calculada sobre B'c.
    """

    cota_rasante_min: float               # msnm - el maximo de las dos
    cota_rasante_actual: float            # msnm - la del CSV (Sec. 1.1)
    cota_por_recubrimiento: float         # msnm - cota clave + h_rec + e_paq
    cota_por_resguardo: float             # msnm - cota entrada + HW
                                          #        + resguardo(CBR) + e_paq
    condicion_gobernante: CondicionRasante
    cota_entrada: float                   # msnm - fondo de la entrada
    cota_clave: float                     # msnm - cota entrada + D + espesor de pared
    altura_supuesta: float                # m  - altura INTERIOR del tamizado (Sec. 7.A)
    espesor_pared: float                  # m  - t; separa el interior del exterior
    ancho_exterior: float                 # m  - el Bc de AASHTO Art. 12.6.6.3
    HW: float                             # m  - carga sobre el fondo de la entrada
    h_recubrimiento: float                # m  - relleno minimo sobre la clave
    espesor_paquete: float                # m  - cota rasante - cota subrasante
    resguardo: float                      # m  - tabla de Sec. 5.1 segun CBR
    factible: bool                        # la rasante actual ya alcanza
    delta_rasante_m: float                # m  - 0.0 si es factible
    criterio_recubrimiento: Optional[str]
    # EL NUMERAL QUE LA FILA G1 IMPRIME, resuelto donde se conoce la forma.
    # Viaja aqui por la misma razon que `criterio_recubrimiento`: G1 recibe
    # solo el tamizado, y con una constante unica atribuia a todo material la
    # Tabla 12.6.6.3-1 de AASHTO -- que no tiene fila de cajon de concreto --.
    numeral_g1: str
    # CUAL de los dos minimos gano la regla del mayor. No es derivable de los
    # campos de aqui -- h_rec es el maximo y no dice de donde salio --, y sin
    # el la memoria enuncia la regla sin publicar el resultado de aplicarla.
    # Sus dos valores son `M7.MINIMO_EG2013` y `M7.MINIMO_AASHTO`.
    minimo_que_gobierna: str
    criterio_resguardo: str
    id_punto: Optional[str] = None
    numeral: str = "Sec. 7.A"
    # --- T-6 --- (INF-5.1.18). `provisional` es True cuando la cota de
    # entrada sobre la que se levantan las DOS condiciones es adoptada igual
    # al terreno y no medida en el cauce: la rasante minima y su delta valen
    # lo que valga esa adopcion, y `aviso` lleva la frase que lo dice. Con la
    # columna `cota_fondo_entrada` llena los dos quedan en False y "".
    provisional: bool = False
    aviso: str = ""
    # --- T-3 (auditoria adversarial, H5) --- LA COBERTURA DEL MARCO AVISA Y
    # NO BLOQUEA. Su valor, 0.3048 m, es [A] por analogia con la fila del
    # TUBO de la Tabla 12.6.6.3-1, y es MAS RESTRICTIVO que la fuente: el
    # Manual admite la rasante a nivel de la losa (num. 4.1.1.3.4 a)), la
    # Lamina N 03 dibuja el marco en cruce de canal sin relleno acotado y
    # AASHTO LRFD 12.6.6.3 admite el cajon sin cobertura con la losa
    # diseñada para la carga vehicular directa. Con `cobertura_como_aviso`
    # (solo un marco) la condicion de recubrimiento que BLOQUEA es la clave
    # bajo la subrasante -- cobertura cero, `cota_por_cobertura_exigible` =
    # clave + e_paq --, y `cota_rasante_min`, `factible` y el delta se
    # calculan con ella y con el resguardo; la cobertura adoptada queda en
    # `cota_por_recubrimiento` y `alcanza_cobertura_adoptada` dice si la
    # rasante la alcanza: si no, G1 sale como INDICADOR. En un tubo los dos
    # campos quedan en False/None y nada cambia.
    cobertura_como_aviso: bool = False
    cota_por_cobertura_exigible: Optional[float] = None
    alcanza_cobertura_adoptada: bool = True

    @property
    def delta_rasante_cm(self) -> float:
        """
        El mismo delta en centimetros, que es la unidad en que Sec. 7.B
        redacta la salida ("no factible -> subir rasante X cm"). Es conversion
        de presentacion: el calculo entero sigue en metros (SI).
        """
        return self.delta_rasante_m * CENTIMETROS_POR_METRO

    @property
    def criterio_gobernante(self) -> Optional[str]:
        """Clave del criterio adoptado de la condicion que fija la rasante."""
        if self.condicion_gobernante is CondicionRasante.RESGUARDO:
            return self.criterio_resguardo
        return self.criterio_recubrimiento

    @property
    def mensaje(self) -> str:
        """
        La frase que Sec. 7.B exige devolver, en centimetros. Nunca un
        resultado silencioso: cuando el punto es factible tambien lo dice.
        """
        # --- T-6 --- el delta (o su ausencia) es PROVISIONAL mientras el
        # fondo de entrada sea el terreno adoptado: se dice en la misma frase.
        cola = f" -- PROVISIONAL: {self.aviso}" if self.provisional else ""
        # --- T-3 (auditoria, H5) --- la cobertura adoptada del marco, que
        # avisa y no bloquea, se dice en la misma frase.
        if self.cobertura_como_aviso and not self.alcanza_cobertura_adoptada:
            cola = (f" -- AVISO: no alcanza la cobertura adoptada por "
                    f"analogia ({self.h_recubrimiento:.4f} m sobre la clave, "
                    f"rasante {self.cota_por_recubrimiento:.3f} msnm)" + cola)
        if self.factible:
            return (f"factible: la rasante {self.cota_rasante_actual:.3f} msnm "
                    f"alcanza la minima de 7.A ({self.cota_rasante_min:.3f} "
                    f"msnm, gobierna {self.condicion_gobernante.value})"
                    + cola)
        return (f"no factible -> subir rasante {self.delta_rasante_cm:.1f} cm "
                f"(de {self.cota_rasante_actual:.3f} a "
                f"{self.cota_rasante_min:.3f} msnm; gobierna la condicion de "
                f"{self.condicion_gobernante.value})" + cola)

    def exigir_factible(self) -> None:
        """
        Lanza `DisenoNoFactibleError` con el delta si la rasante no alcanza.

        Existe para el consumidor que necesita la excepcion (un bucle que debe
        abortar el punto) sin perder el numero: el delta viaja SIEMPRE en
        `delta_rasante_m`, nunca como un mensaje suelto ni como una excepcion
        generica. Quien prefiera el resultado sin excepcion lee `factible` y
        `delta_rasante_cm`, que es la forma en que M7 lo devuelve por defecto.
        """
        if self.factible:
            return
        raise DisenoNoFactibleError(
            motivo=self.mensaje,
            delta_rasante_m=self.delta_rasante_m,
            id_punto=self.id_punto,
        )


# --- T-9 --- Los dos limites de la capacidad de una cuneta (num. 4.1.2.1 a)
# del Manual de Hidrologia: «Caudal que transita con la cuneta llena» y
# «Caudal que produce la velocidad máxima admisible»). Rotulos, no valores.
CAPACIDAD_CUNETA_LLENA = "cuneta llena"
CAPACIDAD_VELOCIDAD_LIMITE = "velocidad limite admisible"
ORIGEN_L_DECLARADO = "declarado"
ORIGEN_L_CALCULADO = "calculado"
# El codigo de la verificacion del espaciamiento por tramo (Familia B). Es la
# hermana de VC1 (la verificacion propia de la Familia C): «VB1».
CODIGO_VB1 = "VB1"
# --- T-9 (correcciones de la auditoria, H1) --- La condicion LITERAL del
# Manual (num. 4.1.2.1 a), pag. impresa 177): «Q manning > Q de aporte». Es
# la segunda verificacion de la Fase 10 y no necesita el tramo: el caudal de
# aporte del alivio contra la capacidad admisible de la cuneta.
CODIGO_VB2 = "VB2"
# Como se reparte el aporte por metro de cuneta para la longitud por
# capacidad (H1): con el TRAMO conocido, el caudal del alivio entre su
# longitud; sin el, la escorrentia especifica por el ancho tributario.
METODO_APORTE_TRAMO = "caudal del alivio repartido en su tramo (q' = Q / s)"
METODO_APORTE_AREA = ("escorrentia especifica por el ancho tributario "
                      "(q' = q · b)")


@dataclass(frozen=True)
class Espaciamiento:
    """
    Salida de Fase 10: espaciamiento maximo entre alcantarillas de alivio
    (Familia B), el MINIMO de dos limites independientes:

        espaciamiento_max = min(L_normativo, L_hidraulico)

    `L_normativo` es el limite de num. 4.1.2.1 d) (longitud maxima de cuneta
    segun regimen), leido del criterio adoptado 'long_max_cuneta' -- 200 m,
    adoptado por el regimen FEN (Sec. 10, Anexo A).

    `L_hidraulico` es la longitud a la que la cuneta agota su capacidad
    admisible frente al caudal aportante por metro lineal. Hasta T-9 llegaba
    siempre declarada (`L_hidraulico_m`); desde T-9 la DECLARADA sigue
    ganando y, si no viene, M10 la calcula (`LongitudHidraulica`): la
    seccion y el revestimiento de la cuneta son criterios [A]
    ('seccion_cuneta', con el minimo muy lluvioso de la Tabla Nº 34 desde
    las correcciones; 'revestimiento_cuneta'), su pendiente y el ancho
    tributario son datos del trazo, y el aporte es el caudal del punto,
    repartido en su tramo (Q / s) o por el ancho tributario (q · b).
    `origen_L_hidraulico` dice cual de las dos fue.

    ESTE OBJETO NO VERIFICA NADA (INF-5.1.12): es el espaciamiento MAXIMO.
    Lo que se verifica es el espaciamiento ADOPTADO entre dos alivios, por
    tramo (`TramoDeAlivio`, verificacion VB1). Hasta T-9 su paso decia
    «cumple» comparando el minimo de dos limites con uno de ellos, que no
    podia fallar.

    Se guardan los DOS limites por separado, no solo el minimo, porque la
    memoria tiene que poder mostrar por cuanto quedo descartado el que no
    gobierna.
    """
    L_normativo: float           # m
    L_hidraulico: float          # m
    espaciamiento_max: float     # m - el minimo de los dos
    gobierna: GobiernaEspaciamiento
    criterio_normativo: str = "long_max_cuneta"
    # La pagina impresa es la de la cita del registro (MC_HHD_CUNETA, 179):
    # se repite aqui como texto porque `modelos` no importa del registro, y
    # un test la compara con `MC_HHD_CUNETA.pagina_impresa` (PC-30).
    numeral: str = ReferenciaNormativa(
        seccion_hoja_ruta="Fase 10",
        numeral_norma="Manual de Hidrologia, Hidraulica y Drenaje (MTC), "
                      "num. 4.1.2.1 d), pag. 179",
    )
    paso: Optional["PasoDeMemoria"] = None
    # --- T-9 --- DE DONDE SALIO `L_hidraulico`: declarado (dato externo
    # `L_hidraulico_m`, que sigue ganando) o calculado por M10 con la cuneta
    # (`longitud_hidraulica`, con sus pasos y avisos). Con la longitud
    # declarada `longitud_hidraulica` es None.
    origen_L_hidraulico: str = ORIGEN_L_DECLARADO
    longitud_hidraulica: Optional["LongitudHidraulica"] = None

    @property
    def pasos(self) -> Tuple["PasoDeMemoria", ...]:
        """
        --- T-9 --- Todos los pasos de la Fase 10 del punto, en el orden del
        calculo: los de la longitud por capacidad (si se calculo) y el del
        espaciamiento maximo.
        """
        previos = (() if self.longitud_hidraulica is None
                   else self.longitud_hidraulica.pasos)
        return tuple(previos) + (() if self.paso is None else (self.paso,))

    @property
    def avisos(self) -> Tuple[str, ...]:
        """--- T-9 --- Los avisos de la longitud por capacidad, si la hubo."""
        if self.longitud_hidraulica is None:
            return ()
        return tuple(self.longitud_hidraulica.avisos)


@dataclass(frozen=True)
class CapacidadCuneta:
    """
    --- T-9 --- La capacidad admisible de la cuneta triangular de la Fase 10
    (Manual de Hidrologia, num. 4.1.2.1 a), pag. impresa 174): el MENOR de
    dos caudales, el de la cuneta llena (hasta `tirante_util_m`, la
    profundidad menos el borde libre) y el que produce la velocidad limite
    admisible de la Tabla Nº 33. Los dos van por separado porque el remedio
    no es el mismo: si gobierna la cuneta llena falta seccion; si gobierna la
    velocidad, falta revestimiento.
    """
    profundidad_m: float
    ancho_m: float
    talud_interior_HV: float      # Z1 = ancho / profundidad (Figura Nº 27)
    talud_exterior_HV: float      # Z2
    borde_libre_m: float
    tirante_util_m: float
    revestimiento: str
    n: float                      # 1/K de la Tabla Nº 32
    v_limite_m_s: float           # extremo leido de la Tabla Nº 33
    S: float                      # pendiente longitudinal de la cuneta, m/m
    area_llena_m2: float
    radio_llena_m: float
    Q_llena_m3s: float
    V_llena_m_s: float
    Q_velocidad_m3s: float        # caudal a la velocidad limite
    Q_admisible_m3s: float
    gobierna: str                 # CAPACIDAD_CUNETA_LLENA | ..._VELOCIDAD_LIMITE
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    # --- VE-5 (catlic, T9-01) --- fondo de la seccion: 0 = triangular;
    # > 0 = la trapezoidal de la Tabla Nº 34 (fila «>3000 mm/año», nota «*»).
    ancho_fondo_m: float = 0.0


@dataclass(frozen=True)
class LongitudHidraulica:
    """
    --- T-9 --- La longitud por capacidad de la cuneta (Sec. 10 punto 2 de la
    hoja de ruta): la capacidad admisible dividida por el caudal aportante
    por metro de cuneta,

        q' = q · b / 10^6        [m3/s por m; q en m3/s por km2, b en m]
        L_hidraulico = Q_admisible / q'

    DESDE LAS CORRECCIONES DE LA AUDITORIA DE T-9 (H1) el aporte por metro
    se reparte de DOS maneras, y `metodo_aporte` dice cual:

      * TRAMO conocido (`METODO_APORTE_TRAMO`): q' = Q / s, el caudal de
        aporte del alivio repartido uniformemente en su tramo real de
        longitud s, y L_hidraulico = Q_adm · s / Q. Es la condicion literal
        del Manual escrita como longitud: L_hidraulico >= s si y solo si
        Q_adm >= Q. `escorrentia_m3s_km2` y `ancho_tributario_m` son None.
      * TRAMO desconocido (`METODO_APORTE_AREA`): q' = q · b / 10^6, con q la
        escorrentia especifica del area tributaria (Q / A) y b el ancho
        tributario. Se publica la longitud que ese par implica, s_impl =
        A · 10^6 / b (`s_implicita_m`), y si supera la longitud maxima
        normativa del tramo se avisa: el area declarada no es la faja b x
        tramo, y la longitud calculada no es fiable.

    `caudal_de_aporte` es el `CaudalDeDiseno` de la Fase 1-bis cuando el
    caudal se calculo (el mismo objeto del punto: no se recalcula, H11), o
    None.
    """
    capacidad: CapacidadCuneta
    escorrentia_m3s_km2: Optional[float]
    origen_escorrentia: str
    ancho_tributario_m: Optional[float]
    q_por_metro_m3s_m: float
    L_hidraulico: float
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    caudal_de_aporte: Optional["CaudalDeDiseno"] = None
    metodo_aporte: str = METODO_APORTE_AREA
    Q_aporte_m3s: Optional[float] = None
    longitud_tramo_m: Optional[float] = None
    s_implicita_m: Optional[float] = None


@dataclass(frozen=True)
class AporteDelAlivio:
    """
    --- T-9 (correcciones de la auditoria, H1) --- VB2: el caudal de aporte
    del alivio contra la capacidad admisible de la cuneta (Manual de
    Hidrologia, num. 4.1.2.1 a), pag. impresa 177: «Q manning > Q de aporte,
    Entonces el diseño está terminado»). En la Familia B el caudal del punto
    es, por contrato, el de la cuneta que descarga en el alivio.

    `capacidad` es None cuando no se pudo calcular --falta la pendiente de la
    cuneta-- y entonces `verificacion` tambien, y `aviso` dice que VB2 no se
    evaluo y por que. Con `L_hidraulico_m` declarado no se exige el dato: el
    aviso basta (quien declara la longitud declara que la cuneta conduce su
    aporte hasta ella).
    """
    Q_aporte_m3s: float
    origen_aporte: str
    capacidad: Optional[CapacidadCuneta]
    verificacion: Optional["Verificacion"] = None
    aviso: str = ""

    @property
    def pasos(self) -> Tuple["PasoDeMemoria", ...]:
        """Los pasos de la capacidad de la cuneta, si se calculo."""
        return () if self.capacidad is None else tuple(self.capacidad.pasos)


@dataclass(frozen=True)
class ExtremoDeTramo:
    """
    --- T-9 (correcciones de la auditoria, H3 y decision C) --- Donde empieza
    el tramo de cuneta que VB1 mide para una alcantarilla de alivio: el lado
    de PROGRESIVAS MENORES del alivio (el sentido del flujo no es dato y el
    texto no lo presupone).

    El extremo es, por orden: el inicio declarado (`inicio_tramo_cuneta_km`,
    que no puede ser posterior a la obra); si no, la obra anterior en
    progresiva que cierre el tramo --de Familia B siempre, de Familia A si el
    criterio 'obras_familia_a_extremo_de_cuneta' vale «si»--; si no hay
    ninguna, None, y VB1 no se puede evaluar.

    `avisos` son los HUECOS que VB1 no mira: la cuneta entre la obra anterior
    y un inicio declarado posterior a ella, y la del lado de progresivas
    mayores del alivio cuando la obra siguiente no es otro alivio que la
    verifique.
    """
    id_punto: str
    progresiva_km: float
    extremo: Optional[str]
    progresiva_extremo_km: Optional[float]
    origen_extremo: str
    familia_extremo: Optional["Familia"] = None
    avisos: Tuple[str, ...] = ()

    @property
    def longitud_m(self) -> Optional[float]:
        """|progresiva − progresiva_extremo| en metros, o None sin extremo."""
        if self.progresiva_extremo_km is None:
            return None
        return abs(self.progresiva_km - self.progresiva_extremo_km) * METROS_POR_KM


@dataclass(frozen=True)
class TramoDeAlivio:
    """
    --- T-9 --- El tramo de cuneta que descarga en una alcantarilla de alivio
    (Familia B), entre ella y su extremo aguas arriba, y la verificacion VB1
    de su longitud contra el espaciamiento maximo de la Fase 10.

    EL EXTREMO es la obra B anterior en progresiva, o el inicio del tramo que
    el punto declara (`inicio_tramo_cuneta_km`: punto alto de la rasante,
    inicio del corte, otra obra de drenaje transversal). Sin ninguno de los
    dos no hay tramo que medir: `verificacion` es None, `longitud_m` tambien,
    y `aviso` lo dice. Con el espaciamiento maximo de algun extremo sin
    conocer, se verifica contra el limite normativo SOLO si el tramo ya lo
    excede (el maximo nunca lo supera); si no, tampoco hay verificacion y el
    aviso nombra lo que falta.
    """
    id_punto: str
    progresiva_km: float
    extremo: Optional[str]
    progresiva_extremo_km: Optional[float]
    origen_extremo: str
    longitud_m: Optional[float]
    verificacion: Optional["Verificacion"] = None
    aviso: str = ""
    # --- T-9 (correcciones de la auditoria, H2 y H3) --- `falta` es el dato
    # que destraba VB1 cuando no se evaluo (`inicio_tramo_cuneta_km` sin
    # extremo, `L_hidraulico_m` con el maximo de un extremo desconocido): el
    # servicio lo registra como `Bloqueo` del punto, porque una verificacion
    # de la aceptacion de la Familia B que no se evaluo no puede dejar el
    # expediente cerrado. `avisos` son los huecos de cuneta que VB1 no mira.
    falta: str = ""
    avisos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class CompatibilidadGeometrica:
    """
    Salida de la verificacion final por punto de Sec. 7.B: la geometria del
    conducto ya amarrada al perfil (longitud, esviaje, pendiente, cotas de
    entrada y salida) y el expediente de verificaciones que la sostiene.

    `longitud` = (ancho de plataforma + proyeccion de taludes) * factor de
    esviaje, en metros. `caida` = S * longitud, y `cota_salida` = cota de
    entrada - caida.
    Como se obtuvo la proyeccion -- por extremo, con el terraplen simetrico,
    o despejada de una longitud declarada -- lo dice `longitud_calculada`
    (T-6); `proyeccion_taludes` es siempre la suma de los dos lados.

    Las verificaciones llevan codigo G1/G2 para no confundirse con las V1-V9
    de la Fase 5: son de otra fase y de otro modulo. La lista es corta a
    proposito -- ver "Por que 7.B trae dos verificaciones con umbral y un
    aviso" en el docstring de M7. Desde T-6 hay una tercera fila, G3, que es
    el AVISO de esviaje: `cumple` es True siempre y por eso no entra en
    `verificaciones_incumplidas` ni cambia `factible`.

    `S_conducto` es la pendiente CON LA QUE CORRIO EL DISENO
    (`ResultadoHidraulico.S`), no una que esta fase vuelva a elegir. Sec. 7.B
    dice que la pendiente de la alcantarilla es la del cauce, y esa sigue
    siendo la regla; lo que ya no puede pasar es que el punto que declara la
    suya la use en el HW y no en la cota de salida (MAT-D9).
    """

    punto: PuntoCritico
    # LA SECCION ADOPTADA EN LA FASE 4, y no el escalar `D` que este campo
    # llevaba hasta C8. Misma razon que en `ResultadoPunto`: un `0.90` no dice
    # si el marco era de 1.20 o de 2.00 m de luz, y la Fase 7 es la que
    # publica la geometria amarrada al perfil.
    seccion: Seccion
    tamizado: TamizadoRasante             # el de 7.A, recalculado con ella
    longitud: float                       # m
    proyeccion_taludes: float             # m - suma de los dos taludes
    factor_esviaje: float                 # adimensional - 1/cos(esviaje)
    altura_terraplen: float               # m - cota rasante - cota terreno
    S_conducto: float                     # m/m - la del diseno hidraulico
                                          # (`ResultadoHidraulico.S`), que es
                                          # la del cauce salvo declaracion
    # LA COTA DE ENTRADA CON SU PROCEDENCIA, y no un `float` con un booleano
    # al lado. Dos campos paralelos --- el numero y "si fue medido" --- son
    # dos cosas que pueden divergir sin que nadie lo note, que es la leccion
    # que `ResultadoPunto.D` frente a `seccion` dejo en C7 y C8. Aqui viajan
    # pegados porque son el mismo hecho: el valor y de donde salio.
    #
    # Lo consume el volcado de texto, que marca la cota como MEDIDA o
    # ADOPTADA: un numero en msnm sin marca se lee como cota levantada en
    # campo, que es SIS-A-04.
    cota_entrada: CotaDeEntrada           # msnm, con su procedencia
    cota_salida: float                    # msnm - cota entrada - S*L
    caida: float                          # m  - S*L
    verificaciones: Tuple[Verificacion, ...]
    numeral: str = "Sec. 7.B"
    # --- T-6 --- Lo que 7.B CALCULA, con sus pasos. Todos con valor por
    # defecto: un consumidor anterior a T-6 que construya este objeto sin
    # ellos sigue funcionando, y M11 no imprime lo que no viene.
    #   pasos                los `PasoDeMemoria` de 7.B en orden: pendiente
    #                        adoptada, factor de esviaje, longitud, caida y
    #                        cota de salida, encaje (G1, G2 y G3 llevan el
    #                        suyo dentro de su `Verificacion`).
    #   longitud_calculada   como salio L: metodo, altura del borde de la
    #                        plataforma sobre el fondo EN CADA EXTREMO y la
    #                        proyeccion de cada talud. Es lo que T-7a lee
    #                        para la altura del cabezal y el largo del alero.
    #   pendiente            la S del diseno CON SU ORIGEN (cauce, declarada,
    #                        minima o maxima).
    #   longitud_a_la_clave  longitud entre cabezales con el talud muriendo
    #                        en la clave exterior de la seccion ADOPTADA
    #                        (HDS-5 3.3.5); None cuando L es declarada o el
    #                        metodo es el del terraplen simetrico.
    #   desnivel_entrega     cota de salida - cota de fondo del receptor, m.
    #   avisos               frases que la memoria imprime como aviso (fondo
    #                        de entrada adoptado, esviaje sobre el maximo).
    pasos: Tuple["PasoDeMemoria", ...] = ()
    longitud_calculada: Optional["LongitudConducto"] = None
    pendiente: Optional["PendienteAdoptada"] = None
    longitud_a_la_clave: Optional[float] = None
    desnivel_entrega: Optional[float] = None
    avisos: Tuple[str, ...] = ()
    # --- T-3 --- Lo que 7.B publica de un MARCO y de un paso de canal, los
    # dos con valor por defecto para los constructores anteriores:
    #   geometria_marco   la geometria del marco adoptado (B, H, celdas,
    #                     espesor, dimensiones exteriores y cotas de fondo y
    #                     de clave). None si la seccion es circular. Queda
    #                     para quien la necesite (la demanda de la losa del
    #                     marco, el cabezal por punto) sin volver a
    #                     calcularla; hoy M8 no la lee (ficha T3-06).
    #   remanso_canal     la sobreelevacion de la lamina del canal en el
    #                     cruce y la longitud minima del remanso aguas arriba
    #                     (Familia C). Es un AVISO, no una verificacion.
    geometria_marco: Optional["GeometriaMarco"] = None
    remanso_canal: Optional["RemansoCanal"] = None

    @property
    def verificaciones_incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las que M11 debe destacar en la memoria del punto."""
        return tuple(v for v in self.verificaciones if not v.cumple)

    @property
    def factible(self) -> bool:
        """True si las verificaciones de 7.B cumplen todas."""
        return not self.verificaciones_incumplidas

    @property
    def delta_rasante_cm(self) -> Optional[float]:
        """
        Cuanto hay que subir la rasante, en centimetros, o None cuando subirla
        no es el remedio.

        Es el delta del TAMIZADO, o sea el de G1, y solo existe cuando G1 es
        la que falla. Si la rasante alcanza y lo que incumple es G2 -- la cota
        de salida contra el fondo del receptor --, subir la rasante NO lo
        arregla: G2 se corrige con la pendiente, con la longitud o con la cota
        del receptor. Por eso aqui va None y no 0.0, que es la misma regla que
        `exigir_factible` ya aplicaba al construir la excepcion.

        Devolvia 0.0 SIEMPRE, y eso hacia que `M11_reporte` escribiera
        "Requiere subir la rasante 0.00 cm" en el punto cuya salida queda
        enterrada bajo el receptor -- una instruccion vacia en el sitio donde
        el revisor busca el remedio. El caso era inalcanzable mientras 7.B
        corriese con la pendiente del cauce en vez de la del diseño (MAT-D9);
        al cerrarse ese hallazgo dejo de serlo.
        """
        if self.tamizado.factible:
            return None
        return self.tamizado.delta_rasante_cm

    def exigir_factible(self) -> None:
        """
        Lanza `DisenoNoFactibleError` si 7.B no cumple, con el delta de
        rasante cuando el incumplimiento es el de la rasante congelada (G1).
        Si el que falla es otro (G2, cota de salida contra el receptor), el
        delta va en None porque subir la rasante NO lo resuelve: sale de la
        pendiente y de la cota del receptor, no del tamizado.
        """
        incumplidas = self.verificaciones_incumplidas
        if not incumplidas:
            return
        if not self.tamizado.factible:
            self.tamizado.exigir_factible()
        raise DisenoNoFactibleError(
            motivo="7.B incumple " + "; ".join(
                f"{v.codigo or 'sin codigo'} ({v.numeral}): obtenido "
                f"{v.valor_obtenido!r} frente a {v.valor_admisible!r}"
                for v in incumplidas
            ),
            id_punto=self.punto.id,
        )


# ===========================================================================
# --- T-6 --- Geometria de 7.B: longitud por extremo y pendiente con origen
# (INF-3.3.3, INF-5.1.18, INF-3.2.7)
# ===========================================================================


class MetodoLongitud(str, Enum):
    """
    Como se obtuvo la longitud del conducto de Sec. 7.B.

    TERRAPLEN_SIMETRICO  la formula anterior a T-6, conservada como caso
                         particular: los dos taludes bajan la MISMA altura,
                         la del eje (cota de rasante - cota de terreno).
    POR_EXTREMO          cada talud baja desde el borde de la plataforma
                         hasta el fondo del conducto EN SU EXTREMO; la salida
                         queda S*L mas baja que la entrada (HDS-5 2.2.4 b.).
    DECLARADA            `longitud_m` entro como dato externo: no se calcula.

    Los dos primeros valores son los de la ventana del criterio
    'metodo_longitud_conducto' [A].
    """
    TERRAPLEN_SIMETRICO = "terraplen_simetrico"
    POR_EXTREMO = "por_extremo"
    DECLARADA = "declarada"


class OrigenPendiente(str, Enum):
    """
    De donde sale la pendiente con que corre el diseño (T-6 punto 5).

    CAUCE      `S_cauce`: la regla de Sec. 7.B, el conducto sigue al cauce.
    DECLARADA  el dato externo `S_conducto` del punto.
    MINIMA     la del cauce queda bajo 'pendiente_minima_conducto' y gobierna
               el minimo adoptado.
    MAXIMA     la del cauce supera 'pendiente_maxima_conducto' y gobierna el
               maximo adoptado.

    Los dos ultimos se dan solo sobre la pendiente del CAUCE, contra la banda
    de T-2 (`M5.limites_de_pendiente()`): una pendiente declarada es una
    decision del expediente y el calculo no la pisa -- la juzga V10, la
    verificacion de pendiente de la Fase 5 --. Con ellos el conducto deja de
    seguir a su cauce, y `M7.aviso_de_pendiente` dice que trae consigo.
    """
    CAUCE = "S_cauce"
    DECLARADA = "S_conducto declarada"
    MINIMA = "pendiente_minima_conducto"
    MAXIMA = "pendiente_maxima_conducto"


@dataclass(frozen=True)
class PendienteAdoptada:
    """
    La pendiente del conducto CON SU ORIGEN, m/m. La resuelve
    `M7.pendiente_adoptada` UNA vez, antes de la Fase 4, y es la que usan la
    longitud, el TW, el diseño hidraulico y 7.B (MAT-D9: la pendiente no se
    elige dos veces).

    `S_minima` y `S_maxima` son los extremos de la banda adoptada VIGENTES en
    la corrida, o None cuando la pendiente es DECLARADA (entonces la banda no
    se lee aqui: la aplica V10): se guardan para que la memoria diga contra
    que se comparo, no solo que gano.
    """
    valor: float
    origen: OrigenPendiente
    S_cauce: Optional[float]
    S_declarada: Optional[float]
    S_minima: Optional[float]
    S_maxima: Optional[float]
    procedencia: str


@dataclass(frozen=True)
class LongitudConducto:
    """
    La longitud del conducto de Sec. 7.B con todo lo que la produjo.

    Convenciones (todas en metros y msnm, sobre la seccion del cruce):

      cota_borde_*        cota del borde de la plataforma en ese lado: la
                          rasante del eje, corregida por bombeo y peralte
                          cuando se declaran.
      cota_referencia_*   cota a la que muere el talud en ese lado. En
                          POR_EXTREMO es el fondo del conducto en ese extremo
                          (la salida, S*L bajo la entrada); en
                          TERRAPLEN_SIMETRICO, el terreno del eje en los dos.
      altura_*            cota_borde - cota_referencia: la altura de
                          terraplen que el talud baja en ese lado.
      proyeccion_*        talud * altura: lo que ese talud añade, medido
                          NORMAL a la via.
      semilongitud_*      tramo de conducto, sobre su eje, entre el eje de la
                          via y ese extremo.

    Lo consume 7.B (cota de salida, encaje) y lo consumira el cabezal por
    punto (T-7a): altura de terraplen en cada extremo y largo del alero.
    `pasos` son los `PasoDeMemoria` que lo explican (factor de esviaje y
    longitud), emitidos por el calculo.
    """
    longitud: float
    metodo: MetodoLongitud
    factor_esviaje: float
    talud: Optional[float]
    S: Optional[float]
    bombeo: Optional[float]
    peralte: Optional[float]
    cota_borde_entrada: Optional[float]
    cota_borde_salida: Optional[float]
    cota_referencia_entrada: Optional[float]
    cota_referencia_salida: Optional[float]
    altura_entrada: Optional[float]
    altura_salida: Optional[float]
    proyeccion_entrada: Optional[float]
    proyeccion_salida: Optional[float]
    proyeccion_taludes: float
    semilongitud_entrada: Optional[float]
    semilongitud_salida: Optional[float]
    pasos: Tuple["PasoDeMemoria", ...] = ()
    # Avisos de la longitud (auditor de T-6): la plataforma tomada horizontal
    # por no declararse bombeo ni peralte, o una pendiente transversal
    # declarada que el metodo o una longitud declarada dejan sin aplicar.
    avisos: Tuple[str, ...] = ()
    # --- T-10 --- El paso 7.B.3b del metodo por extremo: el reparto de la
    # longitud (altura del terraplen en la salida, proyeccion de los taludes
    # y semilongitudes) que el JSON publicaba y la memoria no. Va APARTE de
    # `pasos` porque es de 7.B y no del calculo previo a la Fase 4: lo
    # imprime la geometria del punto que dimensiona (`CompatibilidadGeometrica
    # .pasos`), no la traza del que no llega a 7.B, cuyo JSON no publica esos
    # numeros. None en los otros metodos.
    paso_reparto: Optional["PasoDeMemoria"] = None
