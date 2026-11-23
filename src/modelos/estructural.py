"""
src/modelos/estructural.py
==========================
Fase 8: lo que devuelve M8 (carga viva, marco y portico).

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Tuple


if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.memoria import PasoDeMemoria, Verificacion

# ===========================================================================
# --- T-5 --- (cadena T, 2026-11-12) Fase 8: estructural del conducto
# (INF-3.3.5). Lo que M8 devuelve. Viven aqui por la regla de la casa: son
# tipos que fluyen entre M8, la Fase 5 (M5 y el verificador de perfil del
# servicio), el servicio y M11.
# ===========================================================================

@dataclass(frozen=True)
class CargaVivaEnterrada:
    """
    La carga viva HL-93 a la profundidad del conducto (AASHTO LRFD
    3.6.1.2.6, con el HL-93 y el IM del Manual de Puentes). Todo en SI.

    `vehiculo` dice cual de los dos gobernó ("camion" o "tandem"), y
    GOBIERNA EL DE MAYOR EFECTO, no el de mayor presion (auditoria de T-5):
    lo que carga al conducto es la presion por el largo del area cargada que
    cae sobre el --W_L = P_L min(l_w, B_c) en el tubo de concreto, P_L C_L
    F_1 en los flexibles--, y con poco relleno y luz grande el tandem (ejes
    a 4 ft) da menos presion sobre un area mas larga y carga mas. `efecto`
    es el valor de esa medida para el que gobierna, `efecto_descripcion`
    dice cual es, y `candidatos` trae los DOS vehiculos como tuplas
    (vehiculo, P_kN, l_w_m, w_w_m, P_L_kPa, efecto). `P_kN` es la carga de
    las ruedas que interactuan sobre el area `l_w x w_w`. `despreciada` es
    True solo cuando el criterio 'carga_viva_bajo_relleno_alto' toma el
    PERMISO de 3.6.1.2.6a (relleno de mas de 8 ft que ademas supera la luz)
    y entonces `P_L_kPa` vale 0; `en_zona_de_permiso` dice si el relleno
    esta en esa zona, se tome o no el permiso. `paso` es el desarrollo.
    """
    H_m: float
    LLDF: float
    IM_pct: float
    m: float
    vehiculo: str
    P_kN: float
    l_w_m: float
    w_w_m: float
    P_L_kPa: float
    despreciada: bool
    paso: "PasoDeMemoria"
    efecto: float = 0.0
    efecto_descripcion: str = ""
    candidatos: Tuple[Tuple[str, float, float, float, float, float], ...] = ()
    en_zona_de_permiso: bool = False
    # --- VE-4f --- True cuando el relleno hasta la rasante es MENOR de 2.0 ft
    # sobre un tubo de concreto o un marco y la carga viva se reparte en la
    # franja equivalente de AASHTO LRFD 4.6.2.10.2 (3.6.1.2.6a): `w_w_m` es
    # entonces el ancho E de la franja (a lo largo del conducto), `l_w_m` el
    # largo del area cargada a traves de el, `P_kN` la carga de UN eje y
    # `efecto` la medida del consumidor sobre los ejes que caen en el.
    relleno_somero: bool = False


@dataclass(frozen=True)
class DemandaMarco:
    """
    La demanda sobre la losa superior del marco (AASHTO LRFD 12.11) que el
    diseño de la seccion --diferido al expediente-- tiene que cubrir. Es
    una DEMANDA, no una verificacion: no hay resistencia contra que
    compararla mientras la seccion no se diseñe.
    """
    F_e: float
    w_tierra_kPa: float
    w_viva_kPa: float
    w_u_kPa: float
    luz_m: float
    M_u_referencia_kNm_m: float
    pasos: Tuple["PasoDeMemoria", ...]


# ===========================================================================
# --- VE-5 (m8), item 1 del censo --- EL PORTICO DEL MARCO (ficha T5-07)
# ===========================================================================

@dataclass(frozen=True)
class GeometriaPortico:
    """
    El marco como portico cerrado de ejes, para su analisis (AASHTO LRFD
    12.11): `n_celdas` celdas de luz libre `luz_libre_m` y altura libre
    `altura_libre_m`, con los CANTOS SEPARADOS de la losa superior, la
    inferior, las paredes exteriores y los tabiques (decision del dueño,
    censo del 2026-11-20). `cartela_m` es la cartela a 45° de las esquinas
    interiores (0 en el catalogo del proyecto, que no las lleva; el ejemplo
    resuelto de MnDOT §12.5 las tiene de 12 in): el analisis la cuenta como
    canto creciente junto a cada cara.
    """
    n_celdas: int
    luz_libre_m: float
    altura_libre_m: float
    t_losa_superior_m: float
    t_losa_inferior_m: float
    t_pared_m: float
    t_tabique_m: float
    cartela_m: float = 0.0

    def espesor_de_pared(self, j: int) -> float:
        """El canto de la pared j (0 y n_celdas son las exteriores)."""
        return (self.t_pared_m if j in (0, self.n_celdas)
                else self.t_tabique_m)

    @property
    def ejes_x_m(self) -> Tuple[float, ...]:
        """Abscisas de los ejes de las paredes, desde el eje de la izquierda."""
        x = [0.0]
        for j in range(self.n_celdas):
            x.append(x[-1] + self.luz_libre_m
                     + (self.espesor_de_pared(j)
                        + self.espesor_de_pared(j + 1)) / 2)
        return tuple(x)

    @property
    def altura_ejes_m(self) -> float:
        """Distancia entre los ejes de las losas."""
        return (self.altura_libre_m
                + (self.t_losa_superior_m + self.t_losa_inferior_m) / 2)


@dataclass(frozen=True)
class EsfuerzoDeSeccion:
    """
    Los esfuerzos de UNA seccion del portico en un caso de carga o en una
    combinacion, por metro de marco: M positivo TRACCIONA LA CARA INTERIOR
    de la celda (en un tabique, la cara que mira a la celda de su derecha),
    N positivo comprime, V en valor absoluto.
    """
    seccion: str
    miembro: str
    M_kNm_m: float
    V_kN_m: float
    N_kN_m: float


@dataclass(frozen=True)
class DisenoPortico:
    """
    El analisis y el armado del portico del marco (AASHTO LRFD 12.11 y
    Seccion 5). `envolventes` son, por combinacion, los esfuerzos factorados
    de cada seccion con la carga viva en su posicion mas desfavorable para
    cada signo; `armados`, las secciones armadas con el armado del cabezal
    (`M9.diseno_flexion_corte`); `verificaciones`, las suyas (A1 a A6 por
    seccion y cara), que cuentan en el punto como las del cabezal.
    """
    geometria: GeometriaPortico
    casos: Tuple[Tuple[str, Tuple[EsfuerzoDeSeccion, ...]], ...]
    envolventes: Tuple[Tuple[str, str, Tuple[EsfuerzoDeSeccion, ...]], ...]
    armados: Tuple[Any, ...]
    verificaciones: Tuple["Verificacion", ...]
    pasos: Tuple["PasoDeMemoria", ...]
    avisos: Tuple[str, ...] = ()
    diferido: Tuple[str, ...] = ()
    # --- VE-7 lote B, B4 (T5-07 (3)) --- las caras que ninguna combinacion
    # tracciona, con el minimo de retraccion y temperatura de AASHTO 5.10.6
    # que 12.11.5.3.1 manda (`FilaDeArmado`, la fila de reparto del cabezal).
    minimos: Tuple[Any, ...] = ()
    # --- VE-7 lote B, B5 (T5-07 (1)) --- si el portico no cumple: el menor
    # canto UNIFORME de la grilla de 'dimensionamiento_zapata_cabezal' con
    # el que cerraria (la seccion interior fija, el relleno reducido), o
    # None si ninguno hasta el tope fisico; y hasta donde se busco. No se
    # adopta: 'espesor_pared_cajon' mueve la clave, V4, V7 y G1.
    canto_que_cierra_m: Optional[float] = None
    canto_buscado_hasta_m: Optional[float] = None
    # --- VE-7, dictamen Fable (ii-b) --- el acero LONGITUDINAL minimo de
    # 5.10.6 (12.11.5.3.1), una `FilaDeArmado` por miembro y cara; y si el
    # relleno hasta la rasante es menor de 2.0 ft, la distribucion de la losa
    # superior (9.7.3.2) es obligatoria y no esta implementada.
    longitudinales: Tuple[Any, ...] = ()
    distribucion_obligatoria: bool = False

    @property
    def cumple(self) -> bool:
        return all(v.cumple for v in self.verificaciones)


@dataclass(frozen=True)
class ResultadoEstructural:
    """
    La Fase 8 de un conducto: las cargas, lo que se eligio (clase, plancha o
    perfil), las verificaciones que deciden si la combinacion EXISTE y el
    relleno maximo con que la eleccion sigue cumpliendo.

    `verificaciones` son las que la Fase 5 suma a su tabla (codigos F8.*):
    deciden, igual que V1 a V10, si el escalon se acepta. `pasos` son los de
    la carga y la seleccion, que no juzgan; `avisos` sube a
    `InformePunto.avisos()`; `diferido` lista lo que de verdad sigue fuera
    del alcance. `seleccion` es el texto de lo elegido ("Clase II",
    "68x13/2.77", ...) y vacio si nada cumple.

    `cota_inferior` es True SOLO en el resultado del HDPE calculado con el
    perfil MINIMO de la Tabla A12-11 de AASHTO LRFD por no haberse declarado
    el del fabricante: sus veredictos no son los de un producto real
    (C12.12.3.2) y por eso ese resultado no llega nunca a la tabla de la
    Fase 5 --`M8.verificar_hdpe` se detiene con `DatoFaltanteError` y lo
    lleva dentro--; se obtiene con `M8.cota_inferior_hdpe`.
    """
    material: str
    H_relleno_m: float
    e_paquete_m: float
    H_total_m: float
    seleccion: str
    relleno_maximo_m: Optional[float]
    verificaciones: Tuple["Verificacion", ...]
    pasos: Tuple["PasoDeMemoria", ...]
    avisos: Tuple[str, ...] = ()
    diferido: Tuple[str, ...] = ()
    demanda_marco: Optional[DemandaMarco] = None
    cota_inferior: bool = False
    # --- VE-5 (m8) --- El analisis y el armado del portico del marco (la
    # etapa `servicio.ETAPA_PORTICO_MARCO`, a expediente); None en los tubos.
    portico: Optional[DisenoPortico] = None

    @property
    def cumple(self) -> bool:
        return all(v.cumple for v in self.verificaciones)


# --- T-5 --- El mismo estado cuando lo que no alcanza es el metodo de la
# carga viva a traves del relleno de AASHTO LRFD 3.6.1.2.6a (relleno menor
# que el de su dominio). Mismo recurso que T-1: encabezarla con «HDS-5
# 3.24» seria una cita falsa (`MetodoNoEvaluableError.rotulo`).
MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL = (
    "método no evaluable (AASHTO LRFD 3.6.1.2.6a)")
