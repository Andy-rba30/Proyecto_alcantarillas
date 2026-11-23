"""
src/modelos/hidrologia.py
=========================
Fase 1-bis: entradas y salida de MH_hidrologia.

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional, Tuple


if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.memoria import PasoDeMemoria

# ===========================================================================
# --- T-1 --- Fase 1-bis - Hidrologia (entradas y salida de MH_hidrologia)
# ===========================================================================
# Las dos ENTRADAS del proyecto que el calculo hidrologico consume --la cuenca
# de cada obra y la serie de la estacion-- y lo que devuelve: el caudal de
# diseño de un punto con su origen y su memoria. Fluyen entre
# `modulos/MH_hidrologia.py`, `servicio.py`, `M11_reporte.py` y `cli.py`, y
# por eso viven aqui. Ninguna trae valores por defecto de proyecto: los
# `None` de `Cuenca` son columnas OPCIONALES del CSV, y lo que cada una
# habilita cuando falta esta escrito en su campo.

# Los dos origenes del caudal de un punto de Familia A o B. Son rotulos de la
# memoria y del JSON, no valores de proyecto.
ORIGEN_CAUDAL_DECLARADO = "declarado"
ORIGEN_CAUDAL_CALCULADO = "calculado"
# La frase que la memoria imprime cuando `Q_m3s` viene lleno (T-1, punto 2).
LEYENDA_CAUDAL_DECLARADO = "Q declarado por el estudio hidrológico"
LEYENDA_CAUDAL_CALCULADO = ("Q calculado por el programa (MH_hidrologia) con "
                            "la cuenca y la estación declaradas")


@dataclass(frozen=True)
class Cuenca:
    """
    La cuenca aportante de UNA obra: una fila del CSV de cuencas (--cuencas).

    Es una entrada del estudio hidrologico (docs/contrato_entradas.md): el
    programa la valida y no la corrige. Para una alcantarilla de alivio
    (Familia B) la «cuenca» es el area tributaria de la cuneta --plataforma y
    talud--, `L_cauce_m` su longitud y `S_cauce_cuenca` su pendiente
    longitudinal: el calculo es el mismo (num. 4.1.2.1 b del Manual).
    """

    id: str                     # el id de la obra en el CSV de puntos
    area_km2: float             # km2
    L_cauce_m: float            # m: longitud del cauce principal (o cuneta)
    # m/m: pendiente media del cauce principal (o de la cuneta). Es la S de
    # la formula del tiempo de concentracion, y las dos fuentes no la llaman
    # igual: la Tabla N 05 escribe «pendiente promedio de la cuenca» en la
    # fila de Kirpich y la ecuacion (30) «Pendiente promedio del cauce mayor».
    # El CSV trae UNA, la del cauce, que es la que acompaña a `L_cauce_m`.
    S_cauce_cuenca: float
    cobertura: str              # clave de cobertura de la Tabla N 08
    suelo: str                  # clave de tipo de suelo de la Tabla N 08
    estacion: str               # nombre de la estacion del CSV de --estacion
    metodo_tc: str              # clave del metodo de tiempo de concentracion
    # m/m. OBLIGATORIA desde la auditoria de T-1: pendiente media del TERRENO
    # de la cuenca, que es con la que la Tabla N 08 elige columna. Era
    # opcional y, vacia, la tabla se leia con `S_cauce_cuenca`: un dato
    # rellenado con otro, y por el lado no conservador. Es tambien la
    # «pendiente promedio de la cuenca» de la ecuacion de retardo.
    S_terreno: float
    # OPCIONAL, y obligatoria solo con el metodo de California: desnivel
    # entre la divisoria y la salida, m. No se deduce de S·L.
    H_desnivel_m: Optional[float] = None
    # Clave del ajuste de Kirpich por tipo de superficie (Tabla N 05,
    # observaciones). OBLIGATORIA cuando `metodo_tc` es Kirpich --«ninguno»
    # es una clave y hay que escribirla: una celda vacia no elige fila--; con
    # cualquier otro metodo va vacia.
    ajuste_kirpich: Optional[str] = None
    # OPCIONAL, y obligatoria solo con la ecuacion de retardo: numero de
    # curva de la cuenca. Lo entrega el estudio hidrologico; el programa no
    # tiene tabla de la que leerlo.
    CN: Optional[float] = None
    origen: str = ""            # archivo y fila, para la memoria
    # --- VE-5 (mh, ficha T1-07) --- OPCIONALES, y obligatorias solo con su
    # metodo (van despues de `origen` para no mover el orden posicional):
    # el coeficiente de retardo de Izzard (adimensional; la Tabla N 05 lo
    # describe de 0.0070 en pavimento muy liso a 0.06 en pasto denso) y el n
    # de Manning del flujo superficial de la onda cinematica. Datos del
    # estudio hidrologico: el programa no los elige ni los lee de una tabla.
    c_retardo_izzard: Optional[float] = None
    n_manning_superficial: Optional[float] = None
    # --- VE-7 lote B, B10 (ficha VE5-MH-01; dictamen Fable, decision 1) ---
    # OPCIONAL: las subareas de la cuenca con distinta cobertura, tuplas
    # (cobertura, suelo, S o None, area en ha) de la columna `subareas`
    # («cobertura/suelo[/S_terreno]:area_ha;...», o «cobertura:area_ha» en
    # una superficie vial, con suelo ""). Cada C sale de su tabla, nunca
    # tecleado; C = ΣC·A/ΣA (`MH._paso_c`). Con ella, `cobertura` y `suelo`
    # de la fila van vacios.
    subareas: Tuple[Tuple[str, str, Optional[float], float], ...] = ()


@dataclass(frozen=True)
class RegistroDeLluvia:
    """Un año de la serie: precipitacion maxima en 24 h y si fue año FEN."""

    anio: int
    p24_mm: float
    fen: bool


@dataclass(frozen=True)
class SerieDeEstacion:
    """
    La serie de precipitacion maxima en 24 horas de una estacion (--estacion).

    `fen` de cada registro es un HECHO que declara quien entrega la serie
    (que años son del fenomeno El Niño); que se hace con esos años es el
    criterio 'homogeneidad_serie_fen'.
    """

    estacion: str
    registros: Tuple[RegistroDeLluvia, ...]
    origen: str = ""

    @property
    def anios_fen(self) -> Tuple[int, ...]:
        return tuple(r.anio for r in self.registros if r.fen)


@dataclass(frozen=True)
class EntradaHidrologica:
    """
    Las dos entradas de la Fase 1-bis, ya cargadas y validadas.

    `cuencas_sha1` y `estacion_sha1` (UI-1, ficha T1-04): el SHA-1 de los
    MISMOS bytes que el cargador parseo, como `ContextoCorrida.csv_sha1` es
    el de los bytes que M0 leyo (PC-09). Los pone `servicio.cargar_hidrologia`,
    que lee cada archivo una sola vez y le pasa esos bytes al cargador; una
    entrada armada por otra via los deja en None. `servicio.correr` los copia
    al contexto de la corrida, que es de donde los leen la memoria y el JSON.
    """

    cuencas: Dict[str, Cuenca]
    estaciones: Dict[str, SerieDeEstacion]
    origen_cuencas: str = ""
    origen_estacion: str = ""
    cuencas_sha1: Optional[str] = None
    estacion_sha1: Optional[str] = None

    def cuenca_de(self, id_punto: str) -> Optional[Cuenca]:
        return self.cuencas.get(id_punto)

    def ids_calculables(self) -> frozenset:
        """
        Los ids cuyo caudal se PUEDE intentar calcular: tienen cuenca y la
        estacion que su cuenca nombra esta en el archivo de la estacion. Es
        lo que M0 consulta para admitir `Q_m3s` vacio en las Familias A y B.
        """
        return frozenset(id_ for id_, c in self.cuencas.items()
                         if c.estacion in self.estaciones)


@dataclass(frozen=True)
class AjusteDeDistribucion:
    """Una distribucion ajustada a la serie, con su prueba de bondad."""

    distribucion: str
    parametros: Tuple[Tuple[str, float], ...]
    n: int
    D: float                    # estadistico de Kolmogorov-Smirnov
    d_critico: float
    alfa: float
    acepta: bool                # D < d_critico (desigualdad estricta)
    P_TR_mm: float              # cuantil del periodo de retorno


@dataclass(frozen=True)
class CaudalDeDiseno:
    """
    El caudal de diseño de un punto de Familia A o B, con su ORIGEN.

    `pasos` es la memoria hidrologica del punto: los nueve pasos de la Fase
    1-bis cuando el caudal se calculo, o solo el del caudal especifico cuando
    entro declarado. `avisos` son textos que la memoria imprime tal cual y
    que no detienen nada. `tratamiento_fen` es SIEMPRE None en un caudal
    declarado: el criterio rige el caudal que el programa calcula, y del
    declarado el programa no sabe que se hizo con los años FEN.
    """

    Q_m3s: float
    origen: str                 # ORIGEN_CAUDAL_DECLARADO / _CALCULADO
    leyenda: str
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    de_donde: str = ""          # la columna, el dato externo o el calculo
    TR_anios: Optional[int] = None
    area_km2: Optional[float] = None
    tc_min: Optional[float] = None
    I_mm_h: Optional[float] = None
    C: Optional[float] = None
    P24_TR_mm: Optional[float] = None
    distribucion: Optional[str] = None
    tratamiento_fen: Optional[str] = None
    q_especifico_m3s_km2: Optional[float] = None
    lamina_equivalente_mm_h: Optional[float] = None
    ajustes: Tuple[AjusteDeDistribucion, ...] = ()
    # Lo que la auditoria de T-1 pidio que viaje y no solo se imprima. La
    # duracion de la lluvia de diseño NO siempre es `tc_min`: por debajo de
    # 'duracion_minima_lluvia_min' se adopta el minimo. `K_uniformidad` es el
    # coeficiente de la ecuacion (31) cuando el caudal lo lleva; None cuando
    # no (otro metodo de tc, o 'coeficiente_uniformidad_temez' = no_aplicar).
    metodo_tc: Optional[str] = None
    duracion_min: Optional[float] = None
    K_uniformidad: Optional[float] = None

    @property
    def calculado(self) -> bool:
        return self.origen == ORIGEN_CAUDAL_CALCULADO
