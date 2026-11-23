"""
src/modelos/cabezal.py
======================
Fase 9: cabezal y aletas, su estabilidad (E1 a E3) y su armado.

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from src.modelos.errores import (
    DatoFaltanteError, DatoInvalidoError, LimiteNumericoError
)
from src.modelos.memoria import Verificacion

if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.base import CondicionAnalisis
    from src.modelos.memoria import PasoDeMemoria

# ===========================================================================
# Fase 9 - Cabezal y aletas (salida de M9)
# ===========================================================================

@dataclass(frozen=True)
class PasoSismico:
    """
    Una fila de la tabla "Cadena sismica - desagregada" de Sec. 9.2.

    La hoja de ruta la escribe desagregada a proposito: PGA, F_pga, A_s,
    k_h0, factor de muro y k_h son SEIS cosas distintas con tres etiquetas
    distintas ([N] el mapa y el numeral 2.8.1.1.14.2, [A] la eleccion de
    F_pga), y hoy coinciden todas en 0.50 solo porque F_pga y el factor de
    muro valen 1.0. Un reporte que imprima "k_h = 0.50" y nada mas no permite
    ver que la unica pieza discutible de la cadena es F_pga, ni recalcularla
    cuando llegue el SPT.

    `criterio` es la clave de `criterios_adoptados.py` cuando el paso LEE un
    valor declarado, y None cuando el paso lo CALCULA a partir de los
    anteriores (A_s y k_h): esos dos no se declaran en ningun sitio, salen de
    una multiplicacion, y por eso su `etiqueta` es "-" y no [N] ni [A].
    """

    simbolo: str                          # "PGA", "F_pga", "A_s", ...
    valor: float
    concepto: str
    etiqueta: str                         # "N", "A", "-" (calculado)
    origen: str                           # numeral o "Calculado"
    criterio: Optional[str] = None        # clave en criterios_adoptados.py
    # La CONDICION bajo la que el paso vale: de que filas de la tabla sale
    # F_pga, en que rama de k_h0 cae la cimentacion, que caso de k_v rige.
    # Tres de los siete pasos llevaban esa condicion implicita en el numero,
    # que es como se pierde: el numero se revisa, el supuesto no se ve. Los
    # pasos CALCULADOS (A_s, k_h) no llevan condicion propia -- heredan la de
    # sus insumos -- y por eso el campo es opcional.
    condicion: Optional[str] = None


@dataclass(frozen=True)
class CadenaSismica:
    """
    Cadena sismica completa de Sec. 9.2, con los seis pasos horizontales mas
    k_v, que va aparte porque NO deriva de la cadena: lo fija su propio
    numeral ([N] condicionado, num. 2.8.1.1.14.2.1).

        A_s  = F_pga * PGA
        k_h0 = A_s                        (Manual de Puentes, 2.8.1.1.14.2.1)
        k_h0 = 1.2 * F_pga * PGA          (idem, cimentacion en Clase A o B)
        k_h  = factor_muro * k_h0

    `pasos` reproduce la tabla de la hoja de ruta fila por fila para que el
    informe la imprima entera -- con su condicion por eslabon, que es lo que
    la hace revisable. Los campos escalares existen para que el calculo no
    tenga que buscar dentro de la tupla.
    """

    PGA: float                            # g - roca Clase B, Tr = 1000 anios
    F_pga: float                          # adimensional - factor de sitio
    A_s: float                            # g - F_pga * PGA
    k_h0: float                           # adimensional - A_s, o 1.2*F_pga*PGA en roca
    factor_muro: float                    # adimensional - 1.0 = sin reduccion
    k_h: float                            # adimensional - factor_muro * k_h0
    k_v: float                            # adimensional - vertical, [N] aparte
    pasos: Tuple[PasoSismico, ...]
    numeral: str = "Sec. 9.2"
    # Las filas de la Tabla 2.4.3.11.2.1.2-1 sobre las que se leyo F_pga, y
    # en que rama de k_h0 cayo la cimentacion. Viajan con la cadena porque el
    # numero no se puede revisar sin ellas: un F_pga de 1.0 leido sobre C/D/E
    # y uno leido sobre A/B son dos afirmaciones distintas, y la segunda
    # ademas cambia la formula de k_h0.
    clases_de_sitio: Tuple[str, ...] = ()
    cimentacion_en_roca: bool = False


@dataclass(frozen=True)
class GeometriaCabezal:
    """
    Predimensionamiento del cabezal, en metros. NO sale del CSV: Sec. 1.2 no
    trae ninguna columna de geometria del cabezal y Sec. 9 no lo dimensiona.
    Desde T-7a la PROPONE `M9.predimensionar_cabezal` para cada extremo de
    cada punto dimensionado, con las reglas declaradas del criterio
    'predimensionamiento_cabezal' [A], y el proyectista puede pisar cualquier
    dimension por `--datos-externos` (clave `cabezal_declarado`); o la arma
    el llamador de M9 en un tanteo, con los ocho campos de siempre.

    `beta_grados` es la inclinacion del PARAMENTO INTERIOR (trasdos) respecto
    de la vertical, con el signo de Mononobe-Okabe: positiva cuando el muro se
    inclina alejandose del relleno. Un muro de paramento vertical es 0.
    """

    H: float                              # m - altura del muro sobre la zapata
    B: float                              # m - ancho de la zapata
    D_f: float                            # m - profundidad de desplante
    espesor_corona: float                 # m - espesor del muro en la corona
    espesor_base_muro: float              # m - espesor del muro en su arranque
    espesor_zapata: float                 # m
    beta_grados: float = 0.0              # grados desde la vertical
    # Ancho del TALON, la parte de la zapata que queda del lado del relleno.
    # Entra aqui porque el num. 2.8.1.1.14.1 define W_s como "el peso del
    # suelo que esta inmediatamente encima del muro, INCLUYENDO EL TALON": sin
    # esa medida no hay W_s y sin W_s no hay P_IR. Es opcional en la
    # dataclase y NO por comodidad -- un default numerico seria inventar
    # geometria --, sino para que las funciones que no lo necesitan sigan
    # aceptando una geometria de tanteo sin el; quien lo necesita lo pide con
    # `exigir_ancho_talon`, que se detiene si falta.
    ancho_talon: Optional[float] = None   # m
    # --- T-7a --- EL CABEZAL POR PUNTO (INF-4.2, INF-5.1.15). Todos con
    # default None / vacio: una geometria de TANTEO -- la de los tests de M9
    # y la que T-7b iterara -- sigue armandose con los ocho campos de arriba,
    # y la que propone `M9.predimensionar_cabezal` lleva ademas DE QUE PUNTO
    # y DE QUE EXTREMO es, su longitud, sus cotas, su tipo, sus aleros, la
    # losa de entrega y, dimension por dimension, si salio de una regla o la
    # declaro el proyectista (`dimensiones`). `H` sigue siendo la altura del
    # muro SOBRE la zapata; `altura_total` (H + zapata) es la H_c del prompt.
    longitud: Optional[float] = None      # m - L_c, normal al eje del conducto
    tipo: Optional[str] = None            # 'voladizo_armado' | 'gravedad_ciclopeo'
    id_punto: Optional[str] = None
    extremo: Optional[str] = None         # 'entrada' | 'salida'
    cota_coronacion: Optional[float] = None   # msnm
    cota_desplante: Optional[float] = None    # msnm - base de la zapata
    ancho_punta: Optional[float] = None   # m - zapata del lado libre (punta)
    aleros: Optional["Aleros"] = None
    losa: Optional["LosaDeEntrega"] = None
    dimensiones: Tuple["DimensionDeCabezal", ...] = ()
    # --- VE-6 (ficha T7B-11, VE6M9-04) --- la orientacion del trasdos frente
    # al trafico y la distancia del borde de calzada al trasdos que el PUNTO
    # declara para este cabezal (`--datos-externos`, claves
    # `orientacion_muro_del_punto` y `distancia_borde_calzada_del_punto_m`).
    # None: rige el [S] de corredor de `datos_sitio`. No son dimensiones: son
    # la planta del cruce, que viaja con la geometria del cabezal.
    orientacion_trafico: Optional[str] = None
    distancia_borde_calzada_m: Optional[float] = None

    def exigir_ancho_talon(self) -> float:
        """
        El ancho del talon, o `DatoFaltanteError` si la geometria no lo trae.

        Desde T-7a ya no es `CriterioPendienteError` sobre
        'predimensionamiento_cabezal': ese criterio TIENE valor (las reglas
        del predimensionamiento) y la geometria que propone
        `M9.predimensionar_cabezal` lleva el talon siempre. Una geometria sin
        el solo puede venir de un TANTEO armado a mano, y lo que le falta es
        un dato que el que tantea tiene que AÑADIR (regla de CLAUDE.md:
        Faltante). Devolver 0 en su lugar anularia W_s y con el la mitad de
        P_IR, en la direccion no conservadora.
        """
        if self.ancho_talon is None:
            raise DatoFaltanteError(
                "ancho_talon",
                detalle="El num. 2.8.1.1.14.1 define W_s como el peso del suelo "
                "inmediatamente encima del muro, incluyendo el talon: sin el "
                "ancho del talon de la geometria del cabezal no hay W_s ni "
                "P_IR. `M9.predimensionar_cabezal` lo propone; una geometria "
                "de tanteo tiene que traerlo",
            )
        return self.ancho_talon

    @property
    def altura_total(self) -> float:
        """
        H + espesor de zapata, en m: la altura del plano vertical contra el
        que actua el relleno. No es lo mismo que `H`, que mide solo el muro
        sobre la zapata, y confundirlas subestima el empuje en el espesor de
        la zapata entero.
        """
        return self.H + self.espesor_zapata


# ===========================================================================
# --- T-7a --- El cabezal POR PUNTO: aleros, losa de entrega, embocadura
# ===========================================================================

ORIGEN_DIMENSION_REGLA = "propuesta por regla"
ORIGEN_DIMENSION_DECLARADA = "declarada"
# --- T-7a, correcciones (H9) --- La dimension que la regla CALCULA a partir de
# otra que el proyectista declaro (el talon con B declarado, la zapata con la
# altura total declarada, los aleros con la altura...): no es «propuesta por
# regla» -- su valor no lo eligio la regla -- ni «declarada» -- nadie la
# tecleo --. Imprimirla con uno de los dos rotulos mentia sobre su origen.
ORIGEN_DIMENSION_DERIVADA = "derivada de dimensiones declaradas"
# --- VE-3.5 --- La dimension que el programa hizo CRECER hasta que la
# estabilidad cumple (`M9.dimensionar_zapata_por_estabilidad`): el ancho de
# la zapata y, con el, el talon. No la eligio la regla ni la declaro nadie.
ORIGEN_DIMENSION_ESTABILIDAD = "dimensionada por estabilidad"
# --- VE-3.9 --- El peralte de la zapata que el programa hizo CRECER hasta que
# el armado de la zapata (punta y talon) cumple
# (`M9.dimensionar_peralte_por_armado`). Tampoco lo eligio la regla.
ORIGEN_DIMENSION_ARMADO = "dimensionada por armado"
# --- VE-3.14 (H-3 de los ensayos de diseño del cabezal) --- El ancho que
# el dimensionamiento hizo crecer con la estabilidad EVALUABLE cuando una
# condicion no se pudo evaluar (su `Bloqueo` lo dice): rotularlo
# «dimensionada por estabilidad» decia que la estabilidad entera estaba
# cubierta.
ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA = ("dimensionada con la estabilidad "
                                           "evaluable (falta una condicion)")
ORIGENES_DE_DIMENSION = (ORIGEN_DIMENSION_REGLA, ORIGEN_DIMENSION_DECLARADA,
                         ORIGEN_DIMENSION_DERIVADA,
                         ORIGEN_DIMENSION_ESTABILIDAD,
                         ORIGEN_DIMENSION_ARMADO,
                         ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA)


@dataclass(frozen=True)
class DimensionDeCabezal:
    """
    --- T-7a --- Una fila de la tabla de geometria del cabezal: la dimension,
    su valor y DE DONDE SALIO --«propuesta por regla» (con la regla escrita y
    el criterio que la declara) o «declarada» por el proyectista en
    `--datos-externos`--. Es la tabla que el prompt pide imprimir en la
    memoria de cada punto, y viaja con la geometria para que M11 la formatee
    sin reconstruirla.
    """

    nombre: str
    valor: Any
    unidad: str
    origen: str                     # uno de ORIGENES_DE_DIMENSION
    regla: str                      # la regla, o «dato externo del punto»
    criterio: str = ""              # clave del criterio que la gobierna

    def __post_init__(self) -> None:
        if self.origen not in ORIGENES_DE_DIMENSION:
            raise ValueError(
                f"DimensionDeCabezal «{self.nombre}»: origen {self.origen!r}; "
                "se espera uno de " + ", ".join(
                    f"«{o}»" for o in ORIGENES_DE_DIMENSION))
        if not str(self.regla).strip():
            raise ValueError(
                f"DimensionDeCabezal «{self.nombre}» sin regla: una dimension "
                "sin decir de donde salio es la que obliga a abrir el codigo")


@dataclass(frozen=True)
class Aleros:
    """
    --- T-7a --- Los dos aleros (aletas) de UN cabezal (INF-4.3).

    `angulo_grados` es alfa, el angulo de cada alero CON LA PROLONGACION DE
    LA PARED DEL BARRIL: la definicion de ΘW del HDS-5 («Flare angle of
    wingwalls with respect to extension of culvert side wall», List of
    Symbols, pag. impresa xix; cita HDS5_3ED.SIMBOLOS#THETA_W), la de los
    rotulos de su Tabla C.2 («to barrel») y la del INFORME §4.3: 0 son aleros
    paralelos al barril y 90 aleros en el plano del muro, que es un cabezal
    recto.

    CON ESVIAJE LOS DOS ALEROS NO SON IGUALES (correcciones de T-7a, H1). El
    talud del terraplen baja PERPENDICULAR A LA VIA -- es como lo modela
    `M7.longitud_conducto` --, y el eje del conducto forma con esa direccion
    el esviaje theta. El cabezal es normal al eje, de modo que un alero forma
    alfa - theta con la bajada del talud y el otro alfa + theta, y cada uno
    tiene que recorrer, hasta que el talud baje de h0 a H_f, lo que el talud
    avanza en planta ((h0 - H_f)·talud) dividido por el coseno de SU angulo:

        L_corto = (h0 - H_f)·talud / cos(alfa - theta)
        L_largo = (h0 - H_f)·talud / cos(alfa_largo + theta)

    con theta en valor absoluto (con theta = 0 son la misma) y alfa_largo =
    alfa salvo que el punto declare uno menor de ese lado. El CSV trae la
    MAGNITUD del esviaje y no su sentido de giro, de modo que no se sabe cual
    de los dos lados (izquierdo o derecho, aguas arriba o aguas abajo del
    cruce) es el largo: lo fija la planta del cruce, y los dos se llaman
    «corto» y «largo».

    Las dos alturas son VISIBLES, sobre el terreno al pie
    (`ExtremoDelConducto.cota_pie`): la inicial es la del cabezal en el
    arranque (coronacion menos pie) y la final la de la punta. La zapata del
    alero se desplanta a la misma cota que la del cabezal.
    """

    angulo_grados: float            # alfa, grados con la pared del barril
    # --- T-7a, integracion --- el alfa del alero LARGO: el mismo alfa salvo
    # que el punto declare uno menor de ese lado (`cabezal_declarado.
    # angulo_alero_largo_grados`, aleros asimetricos), que es el remedio que
    # el dueño aprobo para el alero largo de un cruce esviado.
    angulo_largo_grados: float      # grados con la pared del barril
    esviaje_grados: float           # theta, magnitud del esviaje del cruce
    longitud_corto: float           # m - el alero que forma alfa - theta
    longitud_largo: float           # m - el alero que forma alfa + theta
    altura_inicial: float           # m - sobre el pie, en el arranque
    altura_final: float             # m - sobre el pie, en la punta (H_f)
    espesor: float                  # m
    ancho_zapata: float             # m
    espesor_zapata: float           # m

    @property
    def longitudes(self) -> Tuple[float, float]:
        """(corto, largo), m."""
        return (self.longitud_corto, self.longitud_largo)


@dataclass(frozen=True)
class LosaDeEntrega:
    """
    --- T-7a --- La losa (zampeado) delante del cabezal y el dentellon en su
    borde libre: GEOMETRIA DECLARADA (T-7a punto 5, ficha T8-03). Su
    verificacion hidraulica es de la Fase 6; aqui solo se dimensiona.

    `profundidad_dentellon` SE MIDE DESDE EL TERRENO al borde de la losa
    (`cota_terreno`) hasta la base del dentellon (`cota_base_dentellon`),
    como la cota «0.80 min.» de la Lamina Nº 04, que arranca en la superficie
    del terreno natural junto al dentellon -- alli, la cara inferior del
    paquete losa + relleno granular -- y no en la cara superior de la losa
    (correcciones de T-7a, H3). El terreno es el MISMO del desplante del
    cabezal de ese extremo (`ExtremoDelConducto.cota_pie`): una referencia
    por extremo para el desplante, la losa y el dentellon. La cota de la cara
    superior de la losa no la fija este predimensionamiento.
    """

    longitud: float                 # m - normal al cabezal, hacia el cauce
    espesor: float                  # m
    profundidad_dentellon: float    # m - desde el terreno hasta su base
    ancho_dentellon: float          # m
    cota_terreno: float             # msnm - el pie del muro de ese extremo
    cota_base_dentellon: float      # msnm - cota_terreno - profundidad


@dataclass(frozen=True)
class ExtremoDelConducto:
    """
    --- T-7a --- Lo que el cabezal de UN extremo necesita saber del conducto
    y del cruce, ya resuelto por las fases anteriores (4, 6 y 7.B) y con su
    procedencia. Es la entrada de `M9.predimensionar_cabezal`, que asi no
    lee el `InformePunto` ni decide nada que ya se haya decidido.

        cota_solera          fondo interior del conducto en ese extremo (la
                             de entrada de 7.B, medida o adoptada; la de
                             salida, entrada - S·L)
        cota_pie             terreno AL PIE del muro: la referencia del
                             desplante (E.050 Art. 26.1 lo mide desde la
                             superficie del terreno) y de la altura de los
                             aleros. Ver `origen_cota_pie`
        cota_clave_exterior  la clave FISICA (M5.cota_clave: altura interior
                             + pared), trasladada al extremo
        cota_agua            el nivel de agua de diseño contra el muro: en la
                             entrada, solera + HW de diseño (M4); en la
                             salida, solera + max(TW, tirante de salida)
        ancho_exterior       ancho exterior del conducto en planta, con
                             todas sus celdas (N·B + (N+1)·t en un marco)
        cota_fondo_hoya      fondo de la hoya de socavacion (Fase 6, T-8);
                             solo en la salida y solo si se estimo o declaro
    """

    extremo: str
    cota_solera: float
    cota_pie: float
    origen_cota_pie: str
    cota_clave_exterior: float
    cota_agua: float
    origen_cota_agua: str
    ancho_exterior: float
    altura_interior: float
    cota_fondo_hoya: Optional[float] = None
    origen_socavacion: str = ""


@dataclass(frozen=True)
class EmbocaduraDelPunto:
    """
    --- T-7a --- La embocadura de un punto: si el cabezal lleva aleros y con
    que angulo, resuelta ANTES de la Fase 4 porque es una entrada de la
    hidraulica (fila de ke de la Tabla C.2 y carta de la Tabla A.1) y de la
    proteccion de entrada (Fase 6), no solo de la geometria de la Fase 9.

    `angulo_aletas` es None sin aleros. `regla` dice que rama de
    'angulo_aletas' dio el angulo (por defecto, o por esviaje mayor que el
    umbral). Que hace la fuente con esa embocadura lo dice
    `M9.filas_hds5_del_cajon`: con tubo, nada (la Tabla C.2 agrupa «Headwall
    or headwall and wingwalls» y las Cartas 1 a 3 no separan aleros); con
    cajon, elige la banda de filas de las Tablas A.1 y C.2.
    """

    tipo: str                       # 'cabezal_con_aleros' | 'cabezal_recto'
    angulo_aletas: Optional[float]  # grados con la pared del barril
    regla: str
    esviaje_grados: float
    criterio_tipo: str
    criterio_angulo: str
    # --- T-7a, correcciones (decision 3 del dueño) --- lo que la embocadura
    # del punto no puede representar y la corrida tiene que AVISAR (la caja
    # receptora de un alivio de cuneta, Familia B). Sale por
    # `InformePunto.avisos()`.
    avisos: Tuple[str, ...] = ()
    # --- VE-6 (ficha T7A-03) --- La ORIENTACION del muro de cabecera:
    # 'normal_al_eje' (la de archivo en las tres familias) o
    # 'paralelo_a_la_via' (solo el marco, cuando 'embocadura_cajon' declara
    # una fila de la Carta 11 del HDS-5: cabezal esviado respecto del barril,
    # sin aletas). Ver `M9.embocadura_del_punto`.
    orientacion: str = "normal_al_eje"


@dataclass(frozen=True)
class CabezalDelPunto:
    """
    --- T-7a --- La Fase 9 de UN punto: los dos cabezales (entrada y salida)
    con su geometria completa, las verificaciones de compatibilidad con el
    conducto y de los minimos con numero (CB1 a CB7), la longitud entre
    cabezales que el relleno retenido cierra (ficha T6-01) y la de metrado,
    los pasos de memoria y los avisos. La estabilidad (E1-E6) y el armado no
    estan aqui: son T-7b y T-7c.
    """

    id_punto: str
    embocadura: EmbocaduraDelPunto
    entrada: GeometriaCabezal
    salida: GeometriaCabezal
    verificaciones: Tuple["Verificacion", ...]
    longitud_entre_cabezales: Optional[float] = None   # m, entre trasdos
    # --- T-7a, correcciones (H6) --- el barril completo, que atraviesa los
    # dos muros normales al eje: L_cab + los dos espesores.
    longitud_metrado: Optional[float] = None           # m
    motivo_sin_longitud: str = ""
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    # --- T-7b --- El ensamble de estabilidad de cada cabezal, por condicion
    # (`EstabilidadDelCabezal`): hasta cuatro, entrada y salida x estatica y
    # sismica. Sus verificaciones E1 a E3 viajan TAMBIEN en `verificaciones`
    # (la via por la que `InformePunto` cuenta incumplidas e indicadores), y
    # sus avisos en `avisos`. Vacio = la estabilidad no se evaluo (su etapa
    # se bloqueo y el punto lleva el `Bloqueo` con el motivo).
    estabilidad: Tuple["EstabilidadDelCabezal", ...] = ()
    # --- T-7c --- El armado de cada cabezal (`ArmadoDelCabezal`), o las
    # verificaciones de su alternativa ciclopea: hasta dos, entrada y
    # salida. Sus verificaciones A* / C* viajan TAMBIEN en `verificaciones`
    # y sus avisos en `avisos`. Vacio = el armado no se evaluo (su etapa se
    # bloqueo y el punto lleva el `Bloqueo` con el motivo).
    armado: Tuple["ArmadoDelCabezal", ...] = ()
    # --- VE-3.5 --- Los anchos de zapata que el dimensionamiento por
    # estabilidad PROBO, en orden, por extremo: el primero es el de la regla
    # y el ultimo el adoptado. Vacio = no se dimensiono (la regla cumplio,
    # el ancho se declaro o el criterio del paso y el tope esta sin valor).
    intentos_de_zapata: Tuple["IntentoDeZapata", ...] = ()
    # --- VE-3.9 --- Los peraltes de zapata que el dimensionamiento por
    # armado PROBO, en orden, por extremo: el primero es el de la regla (o el
    # de su piso) y el ultimo el adoptado. Vacio = no se dimensiono (el
    # armado de la zapata cumplio, el peralte se declaro, el cabezal es de
    # gravedad o el armado no se pudo evaluar).
    intentos_de_peralte: Tuple["IntentoDePeralte", ...] = ()
    # --- VE-3.14 --- Los espesores de pantalla que el dimensionamiento por
    # armado de la pantalla y de los aleros PROBO, uno por extremo
    # dimensionado («extremo: e_0: no cumplen ... -> e_1: cumple»). Vacio =
    # no se dimensiono (el armado cumplio con la regla, el espesor se
    # declaro, el cabezal es de gravedad o el armado no se pudo evaluar).
    intentos_de_pantalla: Tuple[str, ...] = ()
    # --- VE-7 (ficha VE7-01, cierre de T7C-04) --- La estabilidad de los
    # ALEROS de cada cabezal de voladizo, como muro en voladizo con su
    # zapata (la franja del arranque, `M9.estabilidad_del_alero`): hasta
    # cuatro, como la del cabezal. Van aparte de `estabilidad` para que lo
    # que itera el cabezal no las mezcle; sus filas E1 a E3 viajan TAMBIEN
    # en `verificaciones`. Vacio = no hay aleros de voladizo, o su etapa se
    # bloqueo (el punto lleva el `Bloqueo`).
    estabilidad_aleros: Tuple["EstabilidadDelCabezal", ...] = ()
    # Los anchos de la zapata de los aleros que su dimensionamiento por
    # estabilidad PROBO (el primero, el de partida: el de la zapata del
    # cabezal). Vacio = no se dimensiono.
    intentos_de_zapata_aleros: Tuple["IntentoDeZapata", ...] = ()

    @property
    def geometrias(self) -> Tuple[GeometriaCabezal, GeometriaCabezal]:
        return (self.entrada, self.salida)

    @property
    def verificaciones_incumplidas(self) -> Tuple["Verificacion", ...]:
        return tuple(v for v in self.verificaciones if not v.cumple)


@dataclass(frozen=True)
class IntentoDeZapata:
    """
    --- VE-3.5 --- Un intento del dimensionamiento de la zapata de UN
    cabezal (`M9.dimensionar_zapata_por_estabilidad`): el ancho probado, las
    condiciones de estabilidad que se pudieron evaluar con el, las filas que
    DECIDEN y no cumplieron y si el intento cumple (todas las evaluadas
    cumplen). Es la traza que la memoria imprime: que se probo y por que se
    siguio.
    """

    extremo: str
    B: float                                  # m
    condiciones: Tuple[str, ...]
    incumplidas: Tuple[str, ...]
    al_tope: bool = False
    # --- VE-3.14 (H-5, H-12 de los ensayos de diseño del cabezal) --- La
    # punta del intento cuando crecio la punta (el pase de la punta), y si
    # el intento es de la re-optimizacion del ancho tras el peralte.
    punta: Optional[float] = None
    reoptimizado: bool = False

    @property
    def cumple(self) -> bool:
        return bool(self.condiciones) and not self.incumplidas


@dataclass(frozen=True)
class IntentoDePeralte:
    """
    --- VE-3.9 --- Un intento del dimensionamiento del PERALTE de la zapata
    de UN cabezal (`M9.dimensionar_peralte_por_armado`): el peralte probado,
    el ancho con que se armo (el de la estabilidad, que se re-verifica con
    cada peralte y puede volver a crecer), las filas del armado de la zapata
    que no cumplieron y si el ancho tuvo que crecer otra vez con este
    peralte. Cumple cuando ninguna fila del armado de la zapata falla.
    """

    extremo: str
    espesor_zapata: float                     # m
    B: float                                  # m
    incumplidas: Tuple[str, ...]
    ancho_redimensionado: bool = False
    al_tope: bool = False

    @property
    def cumple(self) -> bool:
        return not self.incumplidas


@dataclass(frozen=True)
class EmpujeMononobeOkabe:
    """
    Coeficiente de empuje activo sismico K_AE por Mononobe-Okabe (Sec. 9.2) y
    todos los angulos con que se obtuvo, porque sin ellos el numero no es
    revisable: K_AE depende de cuatro angulos ademas de la cadena sismica y
    tres de los cuatro (i, beta, delta) son adopciones del proyectista.

    `K_A` es el coeficiente estatico de la MISMA formulacion (la de Coulomb
    que resulta de hacer k_h = k_v = 0), no el de Rankine: el incremento
    sismico solo tiene sentido restando dos coeficientes homogeneos. Con
    i = beta = delta = 0 ambos coinciden con tan^2(45 - phi/2), y M9 lo
    comprueba en un test.
    """

    K_AE: float                           # adimensional
    K_A: float                            # adimensional - misma formulacion, k=0
    psi_grados: float                     # arctan(k_h / (1 - k_v))
    phi_grados: float                     # friccion interna del relleno
    i_grados: float                       # pendiente del relleno
    beta_grados: float                    # inclinacion del muro
    delta_grados: float                   # friccion muro-suelo
    k_h: float
    k_v: float
    numeral: str = "Sec. 9.2 (Mononobe-Okabe)"

    @property
    def incremento(self) -> float:
        """K_AE - K_A: la parte sismica del coeficiente, siempre >= 0."""
        return self.K_AE - self.K_A


@dataclass(frozen=True)
class EmpujesTrasdos:
    """
    Las cargas horizontales sobre el trasdos del cabezal en UNA condicion
    (Sec. 9.2), cada una con su brazo sobre la base, mas la subpresion.

    Cada empuje viaja con su brazo y no con un momento ya sumado, porque los
    factores gamma de la combinacion (Manual de Puentes, Tablas 2.4.5.3.1-1 y
    -2; la fila de gamma_p que aplica a cada estructura la declara
    'factores_carga_aashto') se aplican POR TIPO DE CARGA -- EH, LS, WA, EQ
    llevan factores distintos y algunos son dobles. Un momento total sumado
    sin factorizar no se puede combinar despues.

    `incremento_sismico` y `z_incremento` son None en condicion estatica. La
    subpresion no lleva brazo: es vertical y su efecto es reducir la normal
    en la base, no volcar.
    """

    condicion: CondicionAnalisis
    altura_empuje: float                  # m - altura del plano de empuje
    gamma_relleno: float                  # kN/m3
    E_activo: float                       # kN/m - carga EH
    z_activo: float                       # m sobre la base (H/3)
    E_sobrecarga: float                   # kN/m - carga LS
    z_sobrecarga: float                   # m sobre la base (H/2)
    E_hidrostatico: float                 # kN/m - carga WA
    z_hidrostatico: float                 # m sobre la base
    U_subpresion: float                   # kN/m - carga WA, vertical
    K_A: float
    incremento_sismico: Optional[float] = None   # kN/m - carga EQ
    z_incremento: Optional[float] = None         # m sobre la base
    mononobe_okabe: Optional[EmpujeMononobeOkabe] = None
    numeral: str = "Sec. 9.2"
    # LA CADENA DE LA SOBRECARGA VIVA, que salia del modulo sin dejar rastro.
    # `E_sobrecarga` es un numero y hasta esta sesion era el unico testigo de
    # una decision con tres eslabones: la altura del muro CON zapata, la
    # orientacion respecto al trafico -- que decide CUAL de las dos tablas de
    # AASHTO aplica -- y el h_eq que sale de ellas. Sin estos tres campos la
    # memoria imprimia un empuje que puede valer 1.87 veces el del expediente
    # anterior citando solo un numeral peruano que dice 0.60 m.
    h_eq_sobrecarga: Optional[float] = None      # m - altura de suelo equivalente
    orientacion_muro: Optional[str] = None       # respecto al trafico
    numeral_sobrecarga: str = ""                 # las DOS fuentes que la sostienen
    # DE DONDE SALE `K_A` (EXT-M-06): el Ka de Coulomb del Manual de Puentes
    # (num. 2.4.4.1.5.3), el mismo que resta el incremento sismico. Hasta
    # EXT-7 era el de Rankine y el objeto no decia cual: dos coeficientes
    # sobre el mismo muro y ningun campo que lo delatara.
    numeral_k_a: str = ""

    def __post_init__(self) -> None:
        """
        La carga EQ va ENTERA o no va: el empuje y su brazo son un solo dato.

        Los dos campos son Optional e independientes, y con solo uno de ellos
        el objeto quedaba en un estado medio que NADIE podia detectar y que es
        NO CONSERVADOR: `empuje_horizontal_total` suma el incremento sismico
        con la guarda `incremento_sismico is not None`, y `momento_volcante`
        lo suma con `incremento_sismico is not None AND z_incremento is not
        None`. Con `incremento_sismico = 9.7` y `z_incremento = None` la carga
        EQ contaba en la FUERZA y desaparecia en silencio del VOLTEO -- que es
        justo la direccion en la que un error no avisa, porque el FS de volteo
        sale mas alto de lo que corresponde.

        Hoy `M9_cabezal.empujes_trasdos` pone los dos juntos dentro del mismo
        `if condicion is SISMICO`, de modo que el estado medio es inalcanzable
        DESDE ESE CAMINO. Pero `EmpujesTrasdos` es una dataclass publica con
        los dos campos sueltos: la guarda va en el tipo, que es donde el
        estado imposible se hace imposible, y no en el llamador de turno.

        POR QUE `ValueError` Y NO `DatoInvalidoError`. La primera version usaba
        la taxonomia del expediente, y contradecia la frontera que este mismo
        trabajo escribio en `M9_cabezal.py` (SIS-E-02): `DatoInvalidoError` es
        para un argumento que ES una clave de tabla normativa, con el mensaje
        enumerando las filas admisibles; para un estado interno no lo es. Y
        este estado no es un dato del expediente que el proyectista pueda
        corregir --- el docstring de arriba dice que es INALCANZABLE desde el
        unico camino de produccion ---, de modo que presentarlo en la GUI como
        "el expediente no se puede cargar" mandaria al revisor a buscar en el
        CSV un defecto que esta en el codigo. Fuera de `ErrorProyecto`, cae en
        el brazo de programa de la GUI y sale con traza, que es lo que un
        invariante roto merece. Es la misma lectura que
        `criterios_adoptados.establecer_valor_dinamico` (SIS-E-05).
        """
        completo = (self.incremento_sismico is not None
                    and self.z_incremento is not None)
        vacio = self.incremento_sismico is None and self.z_incremento is None
        if not (completo or vacio):
            raise ValueError(
                "EmpujesTrasdos: la carga EQ va con su brazo o no va. Se "
                f"recibio incremento_sismico={self.incremento_sismico!r} y "
                f"z_incremento={self.z_incremento!r}: el empuje horizontal lo "
                "sumaria y el momento volcante no, de modo que el volteo "
                "saldria mas seguro de lo que es. Es un invariante del tipo, "
                "no un dato del expediente: si esto se levanta, el defecto "
                "esta en quien construyo el objeto."
            )

    @property
    def empuje_horizontal_total(self) -> float:
        """
        Suma SIN FACTORAR de los empujes horizontales, kN/m. Es la demanda de
        servicio: para Resistencia I o Evento Extremo I hay que factorar cada
        componente por separado con `M9_cabezal.factores_de_carga`.
        """
        total = self.E_activo + self.E_sobrecarga + self.E_hidrostatico
        if self.incremento_sismico is not None:
            total += self.incremento_sismico
        return total

    @property
    def momento_volcante(self) -> float:
        """
        Momento volcante SIN FACTORAR respecto del pie de la zapata, kN*m/m:
        cada empuje por su brazo. Misma advertencia que
        `empuje_horizontal_total` sobre los factores.
        """
        momento = (self.E_activo * self.z_activo
                   + self.E_sobrecarga * self.z_sobrecarga
                   + self.E_hidrostatico * self.z_hidrostatico)
        if self.incremento_sismico is not None and self.z_incremento is not None:
            momento += self.incremento_sismico * self.z_incremento
        return momento


@dataclass(frozen=True)
class FuerzaInerciaMuro:
    """
    P_IR, la fuerza de inercia de la masa del muro bajo sismo (Manual de
    Puentes num. 2.8.1.1.14.1, ec. 2.8.1.1.14.1-1 = AASHTO 11.6.5.1-1).

    Este objeto no existia y el termino tampoco: la cadena sismica del
    proyecto terminaba en k_h y K_AE, y el ensamble de empujes sumaba
    EH + LS + WA + el incremento de Mononobe-Okabe sin ninguna linea de
    inercia del muro (MAT-D6, MAT-X7). La MISMA seccion de la que la hoja de
    ruta toma k_h0 exige combinar las dos.

    Los dos pesos viajan separados y no sumados porque la fuente los define
    aparte y son mas estrechos de lo que "peso del muro" sugiere: W_s es el
    suelo que esta INMEDIATAMENTE ENCIMA del muro, incluido el talon, no el
    relleno del trasdos entero.
    """

    P_IR: float                           # kN/m - k_h * (W_w + W_s)
    W_w: float                            # kN/m - peso de la pared
    W_s: float                            # kN/m - suelo sobre el muro y el talon
    k_h: float                            # adimensional
    numeral: str


@dataclass(frozen=True)
class CasoDemandaSismica:
    """
    Uno de los dos casos que el num. 2.8.1.1.14.1 manda investigar. No son dos
    formas de decir lo mismo: la fuente advierte expresamente que los efectos
    de P_AE y P_IR NO son simultaneos, y por eso reparte los porcentajes.
    """

    nombre: str                           # "100% P_AE + 50% P_IR", ...
    fraccion_P_AE: float
    fraccion_P_IR: float
    P_AE_aplicado: float                  # kN/m - ya con su fraccion y su piso
    P_IR_aplicado: float                  # kN/m - ya con su fraccion
    total: float                          # kN/m
    piso_estatico_activo: bool            # si el piso de P_A levanto la fraccion


@dataclass(frozen=True)
class DemandaSismicaCabezal:
    """
    P_seis: la demanda sismica del cabezal, como la define el num.
    2.8.1.1.14.1 -- los dos casos y el mas desfavorable de los dos.

    `P_AE` es el empuje TOTAL de Mononobe-Okabe (estatico mas dinamico) y no
    su incremento: el comentario del articulo es explicito en que P_AE ya
    incluye el empuje estatico y que el Ka estatico NO debe sumarsele. `P_A`
    viaja aparte porque es el PISO del segundo caso, no un sumando.
    """

    casos: Tuple[CasoDemandaSismica, ...]
    P_AE: float                           # kN/m - Mononobe-Okabe total
    P_A: float                            # kN/m - empuje activo estatico
    inercia: FuerzaInerciaMuro
    numeral: str

    def mas_desfavorable(self, efectos: Dict[str, float]) -> CasoDemandaSismica:
        """
        El caso que gobierna, comparando el EFECTO que el llamador midio en
        cada uno: `{nombre_del_caso: efecto}`, con el efecto orientado de modo
        que mayor sea peor (momento volcante, fuerza actuante, 1/FS...).

        POR QUE NO HAY UN `gobernante` QUE COMPARE LAS SUMAS. Porque la fuente
        no manda comparar fuerzas, manda comparar ANALISIS: "el resultado mas
        conservador de estos dos ANALISIS se usara para el diseno del muro"
        (Manual 2.8.1.1.14.1; "the most conservative result from these two
        analyses", AASHTO 11.6.5.1). P_AE y P_IR actuan a alturas distintas
        -- el empuje en el tercio inferior, la inercia en el centroide de la
        masa del muro y su relleno --, de modo que el orden por fuerza
        resultante NO es el orden por momento volcante. Ejemplo con brazos
        corrientes: P_AE = 100 kN/m a 1.20 m y P_IR = 80 kN/m a 2.00 m dan
        140 kN/m y 200.0 kN*m/m en el primer caso, y 130 kN/m y 220.0 kN*m/m
        en el segundo: la suma senala el primero y el volteo lo gobierna el
        segundo, un 10 % mas. Un `gobernante` que ordenara por `total`
        devolveria el caso equivocado justo en la verificacion -- el volteo --
        donde equivocarse es no conservador.

        La comparacion por fuerza sigue disponible para quien de verdad la
        necesite (deslizamiento con los dos empujes al mismo nivel), pero
        tiene que pedirla nombrandola: `mas_desfavorable({c.nombre: c.total
        for c in demanda.casos})`.
        """
        nombres = {c.nombre for c in self.casos}
        faltan = nombres - set(efectos)
        if faltan:
            raise DatoInvalidoError(
                campo="efectos", valor=sorted(efectos),
                motivo=f"el numeral manda comparar los dos analisis y faltan "
                       f"los de {sorted(faltan)}: sin el efecto de cada caso "
                       f"no hay cual sea 'el resultado mas conservador'",
            )
        return max(self.casos, key=lambda c: efectos[c.nombre])


@dataclass(frozen=True)
class PresionContactoBase:
    """
    La presion de contacto bajo la zapata y la excentricidad que la produce
    (Manual de Puentes num. 2.8.1.1.14.1 para el limite sismico; distribucion
    lineal de Navier para las presiones).

    Era el UNICO eslabon de la cadena de estabilidad sin procedimiento ni
    vacio declarado: `verificar_capacidad_portante` exige `q_actuante` ya
    resuelto y en el repositorio no habia con que producirlo (MAT-O16).

    `distribucion` dice QUE RAMA del numeral se aplico, porque son dos y la
    fuente las reparte por terreno de fundacion: presion uniforme sobre el
    ancho efectivo B - 2e si el muro se apoya en suelo, y distribucion lineal
    sobre B si se apoya en roca. Aplicar la de roca a una cimentacion en
    suelo sobrestima el pico -- es conservador -- pero es la rama equivocada,
    y sin este campo la eleccion no se veria en ningun sitio.

    `dentro_del_nucleo` no es lo mismo que `cumple`, y solo cambia la formula
    en la rama de ROCA: el nucleo central (e <= B/6) es la condicion para que
    la distribucion lineal completa tenga sentido -- fuera de el la zapata
    levanta y q_min saldria negativo --, mientras que el limite SISMICO
    depende de gamma_EQ y llega hasta 0.4*B. Se informa en las dos ramas
    porque es una propiedad de la resultante, no de la formula.
    """

    N: float                              # kN/m - normal neta en la base
    B: float                              # m - ancho de zapata
    e: float                              # m - excentricidad respecto del centro
    q_max: float                          # kPa
    q_min: float                          # kPa
    ancho_efectivo: float                 # m - B - 2e
    dentro_del_nucleo: bool
    distribucion: str                     # que rama del numeral se aplico
    numeral: str


@dataclass(frozen=True)
class CombinacionCarga:
    """
    Una de las tres combinaciones de Sec. 9.2 (AASHTO LRFD Sec. 3.4.1, via
    Manual de Puentes num. 2.4.5.3): Resistencia I, Servicio I o Evento
    Extremo I.

    `componentes` nombra que cargas entran; `criterio_factores` apunta al
    criterio de `criterios_adoptados.py` donde se declara QUE FILA de la
    tabla de gamma_p describe a cada estructura. Este objeto describe la
    combinacion y no la evalua.

    Deciamos aqui que "la hoja de ruta NOMBRA las combinaciones pero no
    transcribe la Tabla 3.4.1-1". Lo primero sigue siendo cierto y lo segundo
    dejo de importar: las dos tablas del numeral 2.4.5.3.1 SI estan en el
    corpus peruano -- Manual de Puentes, pag. impresa 143 -- y desde
    NOR-PUE-04 estan transcritas como [N] en `constantes_normativas`. Pedir
    los factores ya no detiene el calculo por falta de tabla; lo unico que
    puede detenerlo es que falte la ELECCION de fila.
    """

    nombre: str                           # "Resistencia I", ...
    numeral: str
    componentes: Tuple[str, ...]
    criterio_factores: str


@dataclass(frozen=True)
class RequisitosDurabilidad:
    """
    Relacion a/c maxima y f'c minimo que la agresividad quimica del sitio
    impone al concreto, ya combinadas las Tablas 4.2 y 4.4 de E.060 por la
    nota al pie que las dos llevan: "se debe utilizar la MENOR relacion
    maxima agua-material cementante aplicable y el MAYOR f'c minimo".

    Las dos tablas se cruzan en un solo punto del calculo -- este -- y el
    resultado no es un numero suelto: es un par de exigencias con la fila que
    produjo cada una. Sin `gobierna_a_c` y `gobierna_fc` la memoria no puede
    decir POR QUE el concreto lleva esa relacion, que es justo lo que el
    revisor va a preguntar cuando vea que la a/c de sulfatos y la de cloruros
    no coinciden.

    `a_c_max` puede ser None: significa que ninguna de las dos tablas impone
    limite (exposicion insignificante y sin cloruros). No es un vacio del
    expediente, es una exigencia que la norma no formula, y el consumidor
    tiene que tratarlo como tal -- ver `M9.factor_recubrimiento_por_ac`.
    """

    a_c_max: Optional[float]              # relacion agua-material cementante
    fc_min_MPa: Optional[float]
    clase_sulfatos: str                   # fila de la Tabla 4.4 que aplica
    gobierna_a_c: str                     # "Tabla 4.2" / "Tabla 4.4" / "-"
    gobierna_fc: str
    cementos_admisibles: Tuple[str, ...]  # Tabla 4.4, por clase de sulfatos
    numeral: str


@dataclass(frozen=True)
class RecubrimientoDiseno:
    """
    Recubrimiento adoptado en mm y de donde sale, con los DOS operandos que la
    regla de conflicto de Sec. 0.2 obliga a comparar: "rige el recubrimiento
    mayor entre AASHTO y E.060".

    Unico dato del proyecto en milimetros, coherente con
    `constantes_normativas.RECUBRIMIENTO` (Art. 7.7.1 esta escrito en mm y
    reescribirlo en metros solo introduciria ceros). No entra en ninguna
    formula de equilibrio: es una especificacion de detalle para plano.

    POR QUE EL LADO AASHTO LLEVA SIETE CAMPOS Y NO UNO. Ese lado ya no es un
    valor declarado: es el resultado de una cadena -- fila de la tabla,
    columna por categoria de acero, modificador por relacion a/c, piso
    absoluto de 1.0 in -- y cada eslabon puede invertir quien gobierna. Un
    solo numero obligaria al revisor a rehacer la cadena para saber si el
    resultado es defendible, que es exactamente lo que paso con los 75 mm que
    este objeto transportaba antes: el numero se leia bien y no habia forma de
    ver que le faltaban una columna y un modificador.

    LOS DOS ULTIMOS CAMPOS EXISTEN PORQUE UN FACTOR NO SE EXPLICA SOLO. El
    `factor_ac` es un numero de una tabla de tres entradas, y del numero no se
    deduce por que se eligio: 1.2 puede ser "la a/c maxima es 0.50 o mas" o
    puede ser "no hay ninguna a/c contra la que evaluarlo y se toma el factor
    mas exigente". Son dos situaciones distintas del expediente y la segunda
    hay que poder leerla en la memoria, no solo en el codigo. `origen_factor`
    la trae, y `requisitos` trae la exigencia de durabilidad entera -- con
    que tabla gobierna cada mitad -- de la que el factor cuelga.
    """

    condicion: str                        # clave de RECUBRIMIENTO (Art. 7.7.1)
    e060_mm: float
    aashto_mm: float
    adoptado_mm: float                    # max(e060, aashto) - Sec. 0.2
    origen: str                           # "E.060" o "AASHTO"
    criterio_aashto: str                  # clave en criterios_adoptados.py
    numeral: str = "E.060 Art. 7.7.1 / Sec. 0.2 (regla del mayor)"
    situacion: str = ""                   # fila de la tabla de AASHTO / MP
    categoria: str = ""                   # columna: "A", "B" o "C"
    tabulado_mm: float = 0.0              # valor de tabla, antes del factor
    factor_ac: float = 1.0                # modificador por relacion a/c
    piso_aplicado: bool = False           # True si mando el piso de 1.0 in
    corpus_tabla: str = ""                # "[N] Manual de Puentes" / "[C] AASHTO LRFD"
    origen_factor: str = ""               # por que ese factor por a/c
    requisitos: Optional["RequisitosDurabilidad"] = None
    paso: Optional["PasoDeMemoria"] = None


@dataclass(frozen=True)
class CuantiaRefuerzo:
    """
    Cuantia de refuerzo ADOPTADA para una direccion de un muro, con las dos
    candidatas que la produjeron: la calculada por el diseno estructural y el
    minimo normativo. El minimo de E.060 Art. 14.3.1 es un PISO OBLIGATORIO,
    no una nota informativa, y por eso el resultado es
    `max(cuantia_calculada, cuantia_minima)` -- una regla del maximo cuyo
    resultado se guarda junto a `gobierna`, para que la memoria diga cual de
    los dos mando y no obligue al revisor a rehacer la comparacion.

    Sin `gobierna` el objeto no serviria: dos cuantias adoptadas iguales
    pueden venir una de un calculo justo y otra de un calculo muy por debajo
    del minimo, y son dos situaciones distintas de revisar.
    """

    direccion: str                        # "horizontal" / "vertical"
    cuantia_calculada: float              # la que sale del diseno estructural
    cuantia_minima: float                 # Art. 14.3.1 (o el escalon aplicable)
    cuantia_adoptada: float               # max de las dos
    gobierna: str                         # "calculo" o "minimo_normativo"
    numeral: str
    # La clave del PISO que se leyo bajo el regimen de 11.10.10 (horizontal o
    # vertical); vacia cuando el minimo es el del 14.3.1, sea porque no hubo
    # cortante alto o porque el regimen declarado es perpendicular al plano.
    criterio_cortante_alto: str           # clave en criterios_adoptados.py, o ""
    # EL PLANO DEL CORTANTE, que decide si el regimen de 11.10.10 rige
    # (EXT-M-05). `None` cuando quien llama no afirmo cortante alto: la ficha
    # ni se abrio. Con cortante alto lleva la categoria declarada en
    # `criterio_regimen_cortante` (en el plano / perpendicular), porque el
    # minimo aplicado no se puede defender sin decir en que plano actua la
    # demanda que lo dispara.
    regimen_cortante: Optional[str] = None
    criterio_regimen_cortante: str = ""


@dataclass(frozen=True)
class EstabilidadCabezal:
    """
    Expediente de estabilidad del cabezal en UNA condicion (Sec. 9.3). Las
    cinco verificaciones de la tabla llevan codigo E1..E5 para no confundirse
    con las V1-V9 de la Fase 5 ni con las G1/G2 de la Fase 7.

    El mismo cabezal se verifica dos veces, una por `CondicionAnalisis`: el
    resultado estatico y el sismico son dos objetos, no dos campos de uno,
    porque cambian a la vez las fuerzas y los umbrales.

    LO QUE `estable` SIGNIFICA, y lo que significaba (EXT-M-07). Hasta EXT-7
    `estable` era `not verificaciones_incumplidas`: True con E1-E3 solas --
    la particion E1-E3 / E4-E5 es deliberada, porque E4 y E5 salen de un
    analisis de taludes que este software no hace -- y True tambien con el
    conjunto VACIO. Un docstring que prometia cinco verificaciones sobre una
    propiedad que se conformaba con cero. Hoy el objeto lleva `exigidas`, las
    filas que la tabla de Sec. 9.3 pide (derivadas de
    `constantes_normativas.FS_CODIGO`, no escritas aqui), y las tres
    preguntas se contestan por separado:

        estabilidad_interna_cumple   las que SI se resolvieron cumplen todas
        pendientes                   las exigidas que nadie resolvio
        estable                      todas las exigidas presentes Y cumplidas

    El invariante va en el tipo y no en el llamador: ni un expediente vacio
    ni una verificacion con un codigo que la tabla no exige se pueden
    construir (`ValueError`, por la misma razon que `EmpujesTrasdos`: es un
    estado imposible del programa, no un dato del expediente).

    `motivos_pendientes` dice POR QUE falta cada pendiente -- la clave del
    criterio que la bloquea --, para que la memoria imprima «E4: pendiente
    de 'metodo_estabilidad_global'» y no una fila en blanco. Solo puede
    hablar de codigos que de verdad falten.
    """

    condicion: CondicionAnalisis
    geometria: GeometriaCabezal
    verificaciones: Tuple[Verificacion, ...]
    exigidas: Tuple[str, ...]
    numeral: str = "Sec. 9.3 (E.050)"
    motivos_pendientes: Tuple[Tuple[str, str], ...] = ()   # (codigo, clave)

    def __post_init__(self) -> None:
        if not self.exigidas:
            raise ValueError(
                "EstabilidadCabezal: `exigidas` esta vacio. Sin la lista de "
                "filas que la tabla de Sec. 9.3 pide, `estable` no tiene "
                "contra que medirse; es un invariante del tipo, no un dato "
                "del expediente")
        if len(set(self.exigidas)) != len(self.exigidas):
            raise ValueError(
                "EstabilidadCabezal: `exigidas` repite un codigo: "
                f"{self.exigidas}")
        if not self.verificaciones:
            raise ValueError(
                "EstabilidadCabezal: el conjunto de verificaciones esta "
                "vacio. Un expediente sin ninguna fila resuelta no es "
                "«estable»: hasta EXT-7 lo era, porque `estable` solo "
                "miraba que no hubiera incumplidas")
        codigos = [v.codigo for v in self.verificaciones]
        fuera = [c for c in codigos if c not in self.exigidas]
        if fuera:
            raise ValueError(
                "EstabilidadCabezal: verificaciones con un codigo que la "
                f"tabla de Sec. 9.3 no exige: {fuera}. Las exigidas son "
                f"{self.exigidas}")
        if len(set(codigos)) != len(codigos):
            raise ValueError(
                f"EstabilidadCabezal: codigo repetido en las verificaciones: "
                f"{codigos}")
        presentes = set(codigos)
        motivos_fuera = [c for c, _ in self.motivos_pendientes
                         if c in presentes or c not in self.exigidas]
        if motivos_fuera:
            raise ValueError(
                "EstabilidadCabezal: `motivos_pendientes` habla de codigos "
                f"que no estan pendientes: {motivos_fuera}")

    @property
    def verificaciones_incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las que M11 debe destacar en la memoria del cabezal."""
        return tuple(v for v in self.verificaciones if not v.cumple)

    @property
    def pendientes(self) -> Tuple[str, ...]:
        """Las exigidas que nadie resolvio, en el orden de la tabla."""
        presentes = {v.codigo for v in self.verificaciones}
        return tuple(c for c in self.exigidas if c not in presentes)

    @property
    def estabilidad_interna_cumple(self) -> bool:
        """
        True si TODAS las verificaciones resueltas cumplen. No dice nada de
        las pendientes: es lo que `estable` afirmaba hasta EXT-7, con su
        nombre verdadero.
        """
        return not self.verificaciones_incumplidas

    @property
    def estable(self) -> bool:
        """True solo con las exigidas TODAS presentes y TODAS cumplidas."""
        return not self.pendientes and not self.verificaciones_incumplidas


# ---------------------------------------------------------------------------
# El ensamble de estabilidad del cabezal (Fase 9, Sec. 9.2 y 9.3)
# ---------------------------------------------------------------------------

MARCO_LRFD = "LRFD"
MARCO_ASD = "ASD"
MARCOS_DE_ESTABILIDAD = (MARCO_LRFD, MARCO_ASD)

# Las tres opciones del criterio 'marco_estabilidad_cabezal': cual marco
# RIGE (sus verificaciones deciden) y que se hace con el otro (informa).
MARCO_RIGE_LRFD = "lrfd_rige_asd_informa"
MARCO_RIGE_ASD = "asd_rige_lrfd_informa"
MARCO_ENVOLVENTE = "envolvente_de_los_dos"
REGLAS_DE_MARCO = (MARCO_RIGE_LRFD, MARCO_RIGE_ASD, MARCO_ENVOLVENTE)

# Tipos de carga del ensamble, con la nomenclatura de AASHTO 3.3.2.
CARGA_DC = "DC"
CARGA_EV = "EV"
CARGA_EH = "EH"
CARGA_LS = "LS"
CARGA_WA = "WA"
CARGA_EQ = "EQ"
TIPOS_DE_CARGA_DEL_CABEZAL = (CARGA_DC, CARGA_EV, CARGA_EH, CARGA_LS,
                              CARGA_WA, CARGA_EQ)

ELEMENTO_PANTALLA = "pantalla"
ELEMENTO_ZAPATA = "zapata"
ELEMENTO_ALEROS = "aleros"
# --- VE-7 (ficha VE7-01, cierre de T7C-04) --- la zapata de los aleros: su
# talon se arma con el procedimiento de la zapata del cabezal, sobre la
# franja del arranque del alero.
ELEMENTO_ZAPATA_ALEROS = "zapata de los aleros"
ELEMENTOS_DEL_CABEZAL = (ELEMENTO_PANTALLA, ELEMENTO_ZAPATA, ELEMENTO_ALEROS,
                         ELEMENTO_ZAPATA_ALEROS)

# --- VE-7 --- De que muro es un ensamble de estabilidad: el cabezal, o la
# franja del arranque de sus aleros verificada como muro en voladizo.
MURO_CABEZAL = "cabezal"
MURO_ALERO = "alero"


@dataclass(frozen=True)
class CargaDeCabezal:
    """
    --- T-7b --- UNA carga del ensamble, por metro de muro, SIN FACTORAR
    (valor nominal de servicio), con su brazo.

    Convencion de signos, una para todo el ensamble: el origen esta en la
    arista inferior de la PUNTA (lado del cauce); `x` crece hacia el relleno
    y `z` hacia arriba desde la base de la zapata. `V` es positiva hacia
    abajo y `H` positiva hacia la punta (empuja el muro hacia el cauce). El
    momento respecto de la punta es `V·x - H·z`, positivo si estabiliza: la
    subpresion entra con `V` negativa.

    `sobre` dice a que elemento le llega la carga (pantalla o zapata), que es
    lo que T-7c necesita para sacar las solicitaciones de cada uno.
    """

    codigo: str             # 'DC.pantalla', 'EV.talon', 'EH.h', 'LS.v', ...
    tipo: str               # uno de TIPOS_DE_CARGA_DEL_CABEZAL
    descripcion: str
    V: float = 0.0          # kN/m
    H: float = 0.0          # kN/m
    x: float = 0.0          # m, brazo de V desde la punta
    z: float = 0.0          # m, brazo de H sobre la base de la zapata
    sobre: str = ELEMENTO_ZAPATA
    procedencia: str = ""

    def __post_init__(self) -> None:
        if self.tipo not in TIPOS_DE_CARGA_DEL_CABEZAL:
            raise ValueError(f"CargaDeCabezal «{self.codigo}»: tipo "
                             f"{self.tipo!r} desconocido")
        for nombre in ("V", "H", "x", "z"):
            valor = getattr(self, nombre)
            if not (isinstance(valor, (int, float)) and math.isfinite(valor)):
                raise LimiteNumericoError(
                    f"CargaDeCabezal.{nombre}", valor=valor,
                    motivo=f"la carga «{self.codigo}» del ensamble de "
                           "estabilidad no es un numero finito")

    @property
    def momento(self) -> float:
        """Momento respecto de la punta, kN·m/m, positivo si estabiliza."""
        return self.V * self.x - self.H * self.z


@dataclass(frozen=True)
class CombinacionDeEstabilidad:
    """
    --- T-7b --- Las cargas del ensamble combinadas con SUS factores para
    UNA verificacion: marco (LRFD o ASD), condicion (estatica o sismica),
    nombre (Resistencia I con gamma maximos, Evento Extremo I caso 1...) y
    las resultantes. `factores` es la tupla (codigo de la carga, factor): en
    el marco ASD todos valen 1 (cargas de servicio, E.050 Art. 17.1) y los
    de las cargas que la combinacion no incluye valen 0.
    """

    nombre: str
    marco: str
    condicion: CondicionAnalisis
    factores: Tuple[Tuple[str, float], ...]
    N: float                # kN/m, suma de verticales factoradas (hacia abajo)
    H: float                # kN/m, suma de horizontales factoradas
    M_estabilizante: float  # kN·m/m respecto de la punta
    M_volcante: float       # kN·m/m respecto de la punta
    B: float                # m
    para: str = ""          # que verificacion la usa

    @property
    def momento_neto(self) -> float:
        return self.M_estabilizante - self.M_volcante

    @property
    def x_resultante(self) -> float:
        """Posicion de la resultante vertical desde la punta, m."""
        return self.momento_neto / self.N

    @property
    def excentricidad(self) -> float:
        """e = B/2 - x_resultante, m (positiva hacia la punta)."""
        return self.B / 2 - self.x_resultante

    # --- T-10 (correcciones, H7) ---
    @property
    def excentricidad_publicable(self) -> Optional[float]:
        """
        La excentricidad que las vistas imprimen, o None SIN carga vertical
        hacia abajo (N <= 0: no hay resultante que excentrar). La regla vive
        aqui, en el dato, y no repetida en el JSON y en la memoria.
        """
        return self.excentricidad if self.N > 0 else None

    def factor_de(self, codigo: str) -> float:
        return dict(self.factores).get(codigo, 0.0)


@dataclass(frozen=True)
class SolicitacionDeElemento:
    """
    --- T-7b --- La solicitacion FACTORADA de un elemento del cabezal en su
    seccion critica, por metro de muro, para una combinacion del marco LRFD:
    lo que T-7c necesita para armar. `seccion` dice donde se mide (arranque
    de la pantalla, cara de la pantalla en la punta o en el talon).
    """

    elemento: str           # uno de ELEMENTOS_DEL_CABEZAL
    seccion: str
    combinacion: str
    V_u: float              # kN/m
    M_u: float              # kN·m/m
    nota: str = ""
    # --- correcciones de T-7b (H7) --- CON QUE EMPUJE SALE, dicho en la
    # interfaz para que T-7c no lo herede sin saberlo: el regimen del
    # cabezal ('regimen_cabezal' [A]), el nombre y el valor del coeficiente
    # con que se calcularon los empujes de esta solicitacion, y el K0 de
    # AASHTO 3.11.5.2 con su cociente, que es el factor por el que crecerian
    # los empujes de la pantalla si se juzgara que no cede (C11.6.5.4).
    regimen: str = ""
    coeficiente_de_empuje: str = ""     # 'K_A' (estatica) o 'K_AE' (sismica)
    K_empuje: Optional[float] = None
    K0: Optional[float] = None
    K0_sobre_K_A: Optional[float] = None


@dataclass(frozen=True)
class EntornoDelCabezal:
    """
    --- T-7b --- Lo que el ensamble de estabilidad necesita de UN cabezal
    ademas de su geometria, ya resuelto por las fases anteriores: hasta
    donde llega el relleno que retiene, como sube el terreno detras de el,
    donde esta el agua y que suelo lo soporta. Lo arma
    `M9.datos_del_cabezal_del_punto`; el ensamble no lee el informe.

        cota_relleno           coronacion menos bordillo: la superficie del
                               relleno retenido contra el trasdos
        cota_borde_plataforma  borde de la plataforma del lado de ese
                               extremo (7.B), donde el talud se quiebra
        talud                  H:V del terraplen
        cota_freatico          COTA del nivel freatico, msnm: la columna
                               NF_profundidad_m medida desde el terreno
                               natural del cruce (`cota_terreno`), que es la
                               convencion de M8, del censo y del contrato de
                               entradas; None si la columna va vacia
        origen_freatico        de donde sale esa cota (texto del paso)
        cota_pie               terreno delante del muro (el de T-7a)
        cota_fondo_hoya        fondo de la hoya de socavacion, si la hay
        suelo                  parametros del suelo de fundacion DEL PUNTO
                               (dato externo validado), o None: rige el
                               criterio de corredor
        cota_agua_diseno       nivel del agua de diseño contra ese cabezal
                               (en la entrada solera + HW de M4; en la
                               salida solera + tirante de salida), si se
                               conoce: solo informa el aviso del desembalse
                               rapido con el relleno drenado

    LA COTA Y NO LA PROFUNDIDAD (correcciones de T-7b, H1). Hasta la
    auditoria el entorno llevaba la profundidad del freatico y el ensamble la
    restaba de la profundidad de desplante de CADA cabezal, es decir, la leia
    bajo el pie del muro; el resto del repositorio la lee bajo el terreno del
    cruce. En la salida de A-01 eso dejaba el agua 0.80 m mas baja (bajo la
    zapata en vez de 0.20 m sobre la base), del lado inseguro. Con la cota no
    hay datum que elegir en el ensamble.
    """

    id_punto: str
    extremo: str
    geometria: GeometriaCabezal
    cota_relleno: float
    cota_borde_plataforma: float
    origen_cota_borde: str
    talud: float
    esviaje_grados: float
    cota_freatico: Optional[float]
    cota_pie: float
    cota_fondo_hoya: Optional[float] = None
    suelo: Optional[dict] = None
    origen_freatico: str = ""
    cota_agua_diseno: Optional[float] = None
    # --- VE-4a --- El resultado DECLARADO de E4 y E5 para ESTE cabezal, del
    # dato externo `estabilidad_global_declarada` ya validado y normalizado
    # (`M9.validar_estabilidad_global_declarada`): {"E4": {"estatico": FS,
    # "sismico": FS}, "E5": {...}, "documento", "fecha", "metodo" y, si
    # viene, "programa"}. None (o vacio): E4 y E5 siguen diferidas.
    estabilidad_global: Optional[dict] = None
    # --- VE-7 (lote A, A5) --- El empuje sismico DECLARADO de ESTE cabezal,
    # del dato externo `empuje_sismico_declarado` validado
    # (`M9.validar_empuje_sismico_declarado`): {"P_AE_kn_m",
    # "altura_aplicacion_m", "incluye_hidrodinamica", "documento", "fecha",
    # "metodo"}. Solo se consume donde el programa no calcula el empuje.
    empuje_sismico: Optional[dict] = None
    # --- VE-7 (lote A, A6 y dictamen Fable (iii)) --- El terreno de delante
    # de ESTE cabezal declarado por punto (`talud_delante_del_cabezal_del_
    # punto`): la geometria del talud, {"H_s_m", "beta_grados", "b_m"}, o el
    # texto "horizontal". None: rige el corredor.
    talud_delante: Optional[Any] = None
    # --- VE-7 (lote A, A7) --- el muro de cabecera es PARALELO A LA VIA
    # (`EmbocaduraDelPunto.orientacion`, una fila de la Carta 11): es
    # paralelo al trafico, y la sobrecarga viva lo lee.
    paralelo_a_la_via: bool = False


@dataclass(frozen=True)
class EstabilidadDelCabezal:
    """
    --- T-7b --- El ensamble de estabilidad de UN cabezal (un extremo de un
    punto) en UNA condicion: las cargas sin factorar con sus brazos, las
    combinaciones de los dos marcos, las verificaciones E1 a E3 de cada
    marco (las del marco que rige deciden; las del otro informan), las
    solicitaciones factoradas por elemento y los pasos de memoria.

    `pendientes` son las filas que NO se evaluaron con su motivo (E4 y E5,
    la estabilidad global y la del talud, diferidas al expediente con el
    EMS): se imprimen, no se callan y no cuentan como cumplidas.

    --- VE-4a --- `globales` son las filas E4 y E5 de los dos marcos cuando
    el FS se DECLARO (`EntornoDelCabezal.estabilidad_global`): el programa
    no lo calcula, lo contrasta. Van aparte de `verificaciones` a proposito:
    `cumple` -- lo que el dimensionamiento de la zapata itera -- es de E1 a
    E3, y el ancho de la zapata no mueve un FS que el programa no calcula.
    `M9.integrar_estabilidad` las suma a las del cabezal, que es la via por
    la que el informe cuenta incumplidas e indicadores. Lo declarado sale de
    `pendientes`.
    """

    id_punto: str
    extremo: str
    condicion: CondicionAnalisis
    regla_de_marco: str
    cargas: Tuple[CargaDeCabezal, ...]
    combinaciones: Tuple[CombinacionDeEstabilidad, ...]
    verificaciones: Tuple["Verificacion", ...]
    solicitaciones: Tuple[SolicitacionDeElemento, ...] = ()
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    pendientes: Tuple[Tuple[str, str], ...] = ()
    # Lo que identifica al calculo sin abrir los pasos.
    K_A: Optional[float] = None
    K_AE: Optional[float] = None
    i_grados: Optional[float] = None
    delta_grados: Optional[float] = None
    altura_empuje: Optional[float] = None
    h_eq: Optional[float] = None
    k_h: Optional[float] = None
    # --- correcciones de T-7b --- como se calculo el empuje (cuña de tanteo
    # o formula cerrada), los coeficientes de la formula cerrada que quedan
    # como CONTRASTE (None donde no es evaluable), el regimen del cabezal y
    # el K0 de referencia.
    metodo_empuje: str = ""
    K_A_contraste: Optional[float] = None
    K_AE_contraste: Optional[float] = None
    regimen: str = ""
    K0: Optional[float] = None
    globales: Tuple["Verificacion", ...] = ()
    # --- VE-5 fixve4 --- (codigo, clave del criterio) de las filas E4/E5
    # DECLARADAS cuyo veredicto depende de un criterio sin valor (la fila de
    # phi de 11.6.3.7 con el FS entre 1/0.75 y 1/0.65): no van en
    # `globales`, vuelven a `pendientes` con su motivo y el servicio las
    # lleva como `Bloqueo` del punto (`servicio._estabilidades`).
    pendientes_por_criterio: Tuple[Tuple[str, str], ...] = ()
    # --- VE-7 (ficha VE7-01) --- `MURO_CABEZAL`, o `MURO_ALERO` si es la
    # franja del arranque de los aleros verificada como muro en voladizo
    # (`M9.estabilidad_del_alero`): sus codigos llevan el sufijo `.alero`.
    muro: str = MURO_CABEZAL
    # --- VE-7 (dictamen Fable, abierto (a)) --- con `MURO_ALERO`, la
    # fraccion de la longitud del alero de la franja verificada (0 el
    # arranque, 1 la punta); None en el cabezal.
    fraccion_alero: Optional[float] = None

    def del_marco(self, marco: str) -> Tuple["Verificacion", ...]:
        return tuple(v for v in self.verificaciones
                     if f"-{marco}." in (v.codigo or ""))

    @property
    def cumple(self) -> bool:
        """Todas las verificaciones que DECIDEN cumplen (las que informan no)."""
        return all(v.cumple for v in self.verificaciones)


# ===========================================================================
# --- T-7c --- (cadena T) · el armado del cabezal y la alternativa ciclopea
# ===========================================================================
# Lo que `M9.armado_del_cabezal` entrega por cabezal: el armado de cada
# seccion critica (pantalla en su arranque, punta y talon de la zapata en la
# cara de la pantalla, alero en su arranque), el acero de reparto de cada
# elemento, y la TABLA de armado que la memoria imprime -- emitida aqui como
# datos y como `PasoDeMemoria`: M11 la formatea, no la calcula --. Para el
# cabezal de gravedad en ciclopeo no hay armado: van sus verificaciones de
# traccion y de material.

# Las dos opciones de 'regimen_resistencia_elementos_cabezal' [A].
REGIMEN_RESISTENCIA_K0 = "no_cedente_k0"
REGIMEN_RESISTENCIA_CEDENTE = "cedente"
REGIMENES_DE_RESISTENCIA = (REGIMEN_RESISTENCIA_K0,
                            REGIMEN_RESISTENCIA_CEDENTE)

# Las dos opciones de 'regla_minimos_constructivos_cabezal' [A].
MINIMOS_MAS_EXIGENTE = "mas_exigente_aashto_e060"
MINIMOS_SOLO_AASHTO = "solo_aashto"
REGLAS_DE_MINIMOS = (MINIMOS_MAS_EXIGENTE, MINIMOS_SOLO_AASHTO)

# Las dos opciones de 'criterio_traccion_cabezal_ciclopeo' [A].
TRACCION_NULA = "tracciones_nulas"
TRACCION_ADMISIBLE_E060 = "traccion_admisible_e060"
CRITERIOS_DE_TRACCION_CICLOPEO = (TRACCION_NULA, TRACCION_ADMISIBLE_E060)

# --- correcciones de T-7c (H3) --- Las dos clases de exposicion de AASHTO
# 5.6.7 (gamma_e = 1.00 y 0.75), opciones de 'clase_exposicion_fisuracion_
# cabezal' [A], que NO tiene valor de archivo: la declara el Propietario.
CLASE_EXPOSICION_1 = "clase_1"
CLASE_EXPOSICION_2 = "clase_2"
CLASES_DE_EXPOSICION = (CLASE_EXPOSICION_1, CLASE_EXPOSICION_2)

# El marco de las combinaciones del CONTRASTE con E.060 (9.2.5): un tercer
# rotulo junto a MARCO_LRFD y MARCO_ASD, para que `M9.solicitaciones_por_
# elemento` pueda entregar las solicitaciones de ESE marco sin que nadie las
# confunda con las que rigen.
MARCO_E060 = "E060"

# El rotulo de `MetodoNoEvaluableError` cuando lo que no se puede evaluar es
# el cortante de una seccion fuera de las condiciones del procedimiento
# simplificado de AASHTO 5.7.3.4.1 (el general, 5.7.3.4.2, no se implementa).
MOTIVO_METODO_NO_EVALUABLE_ARMADO = (
    "método no evaluable (AASHTO LRFD 5.7.3.4, cortante del cabezal)")

# Claves de las secciones criticas del cabezal armado.
SECCION_PANTALLA = "pantalla"
SECCION_PUNTA = "punta"
SECCION_TALON = "talon"
SECCION_ALERO = "alero"
# --- VE-6 (ficha VE6M9-03) --- la segunda seccion del alero, la de la mitad
# de su longitud: arma el tramo de L/2 a L (la del arranque, el de 0 a L/2).
SECCION_ALERO_MITAD = "alero_mitad"
# --- VE-7 (ficha VE7-01) --- el talon de la zapata de los aleros, en la cara
# del alero (la franja del arranque no tiene punta).
SECCION_TALON_ALERO = "talon_alero"
SECCIONES_DEL_ARMADO = (SECCION_PANTALLA, SECCION_PUNTA, SECCION_TALON,
                        SECCION_ALERO, SECCION_ALERO_MITAD,
                        SECCION_TALON_ALERO)


@dataclass(frozen=True)
class BarraPropuesta:
    """
    --- T-7c --- La barra y el espaciamiento que el programa PROPONE para
    una cara, tomados del catalogo [A] 'catalogo_barras_refuerzo_cabezal'.
    Es una propuesta: lo que el plano lleve tiene que dar al menos el acero
    adoptado con un espaciamiento no mayor que el maximo.
    """

    designacion: str        # '1/2', '5/8', ... (pulgadas, como en el catalogo)
    diametro_mm: float
    area_mm2: float
    espaciamiento: float    # m, entre ejes
    As_provisto: float      # mm2/m

    @property
    def texto(self) -> str:
        return f"Ø {self.designacion}\" @ {self.espaciamiento:.3f} m"


@dataclass(frozen=True)
class SolicitacionDeArmado:
    """
    --- T-7c --- El momento y el cortante FACTORADOS de una seccion para UNA
    combinacion, con el factor de resistencia que le corresponde y con que
    empuje salieron. `M_u_reposo` / `M_u_cedente` (y los de cortante) son los
    dos valores que el regimen compara: rige el de `M_u` / `V_u`.
    """

    combinacion: str
    condicion: CondicionAnalisis
    M_u: float                      # kN·m/m, el que rige (no negativo)
    V_u: float                      # kN/m, el que rige (no negativo)
    phi_flexion: float
    phi_corte: float
    M_u_cedente: float
    V_u_cedente: float
    M_u_reposo: Optional[float] = None
    V_u_reposo: Optional[float] = None
    nota: str = ""


@dataclass(frozen=True)
class ArmadoDeSeccion:
    """
    --- T-7c --- El armado de UNA seccion critica del cabezal, por metro de
    muro: las solicitaciones que la gobiernan, el acero que la flexion pide,
    los dos minimos, el adoptado, la barra propuesta y la resistencia que
    resulta, con las verificaciones A1 a A5 (las del marco que rige, AASHTO
    LRFD Seccion 5) y las de contraste con E.060, que informan.
    """

    elemento: str                   # uno de ELEMENTOS_DEL_CABEZAL
    clave: str                      # una de SECCIONES_DEL_ARMADO
    seccion: str                    # donde se mide
    cara: str                       # la cara en traccion
    espesor: float                  # m
    recubrimiento_mm: float
    origen_recubrimiento: str
    d: float                        # m, con la barra propuesta
    regimen: str
    solicitaciones: Tuple[SolicitacionDeArmado, ...]
    rige_flexion: SolicitacionDeArmado
    rige_cortante: SolicitacionDeArmado
    As_resistencia: float           # mm2/m, el que pide el momento que rige
    As_minimo_flexion: float        # mm2/m, AASHTO 5.6.3.3
    As_minimo_constructivo: float   # mm2/m, retraccion / cuantia minima
    origen_minimo: str
    As_adoptado: float              # mm2/m, el mayor de los tres
    gobierna: str                   # 'resistencia' | 'minimo de flexion' | ...
    s_max: float                    # m
    origen_s_max: str
    barra: Optional[BarraPropuesta]
    M_r: Optional[float]            # kN·m/m con la barra propuesta
    epsilon_t: Optional[float]
    d_v: Optional[float]            # m
    V_c: Optional[float]            # kN/m nominal
    V_r: Optional[float]            # kN/m factorado
    # Contraste con E.060 (solo condicion estatica), o None.
    M_u_e060: Optional[float] = None
    V_u_e060: Optional[float] = None
    As_e060: Optional[float] = None
    V_r_e060: Optional[float] = None
    # --- correcciones de T-7c --- La fisuracion de AASHTO 5.6.7 en Servicio
    # I (H3): el momento de servicio, si 5.6.7 aplica (traccion bruta sobre
    # 0.8·f_r), la tension del acero y el espaciamiento maximo de cada clase
    # de exposicion ({'clase_1': s, 'clase_2': s}, m); None sin momento de
    # servicio. Y el peralte de cortante de la letra de 5.7.2.8 cuando el
    # adoptado se acota al peralte efectivo (H8).
    M_servicio: Optional[float] = None
    fisuracion_aplica: Optional[bool] = None
    f_ss: Optional[float] = None
    s_fisuracion: Optional[dict] = None
    clase_exposicion: Optional[str] = None
    d_v_letra: Optional[float] = None
    verificaciones: Tuple["Verificacion", ...] = ()
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class FilaDeArmado:
    """
    --- T-7c --- Una fila de la tabla de armado del cabezal (T-7c punto 4):
    el acero requerido por resistencia, el minimo, el adoptado y la barra
    propuesta, de UNA posicion (cara y direccion) de UN elemento. `gobierna`
    dice cual de los dos mando.
    """

    elemento: str
    posicion: str
    As_requerido: float             # mm2/m (0 en el acero de reparto)
    As_minimo: float                # mm2/m
    origen_minimo: str
    As_adoptado: float              # mm2/m
    gobierna: str
    s_max: float                    # m
    barra: Optional[BarraPropuesta]

    @property
    def cumple(self) -> bool:
        """Hay barra en el catalogo que da el acero adoptado."""
        return self.barra is not None


@dataclass(frozen=True)
class ArmadoDelCabezal:
    """
    --- T-7c --- El armado de UN cabezal (un extremo de un punto), o las
    verificaciones de su alternativa en concreto ciclopeo.

        tipo        'voladizo_armado' o 'gravedad_ciclopeo' (el de T-7a)
        regimen     el de 'regimen_resistencia_elementos_cabezal'
        secciones   las secciones criticas armadas (vacio en el ciclopeo)
        tabla       la tabla de armado por elemento, para la memoria
        sismico     si el Evento Extremo I entro al armado; cuando no, el
                    motivo esta en `avisos` y el armado sale solo de
                    Resistencia I
    """

    id_punto: str
    extremo: str
    tipo: str
    regimen: str
    fc_mpa: float
    fy_mpa: Optional[float]
    secciones: Tuple[ArmadoDeSeccion, ...] = ()
    tabla: Tuple[FilaDeArmado, ...] = ()
    verificaciones: Tuple["Verificacion", ...] = ()
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    sismico: bool = False
    K0: Optional[float] = None
    K_A: Optional[float] = None

    def seccion(self, clave: str) -> ArmadoDeSeccion:
        return next(s for s in self.secciones if s.clave == clave)

    @property
    def cumple(self) -> bool:
        """Todas las verificaciones que DECIDEN cumplen."""
        return all(v.cumple for v in self.verificaciones)
