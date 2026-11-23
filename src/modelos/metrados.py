"""
src/modelos/metrados.py
=======================
Fase 11, entregables 8 y 9: metrados y cuadro de compatibilidad rasante-alcantarilla.

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple


if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.memoria import PasoDeMemoria

# ===========================================================================
# --- VE-5 (lote «met», item 8 del censo) --- Fase 11, entregables 8 y 9:
# los METRADOS referidos a las partidas del EG-2013 y el CUADRO DE
# COMPATIBILIDAD RASANTE-ALCANTARILLA (la salida de 7.A). Los dos los arma
# `M12_metrados` leyendo lo que las fases anteriores ya entregaron; M11 y la
# CLI solo los formatean.
# ===========================================================================

MOTIVO_METODO_NO_EVALUABLE_METRADO = (
    "método no evaluable (metrados, Fase 11)")

# Los rubros del metrado, en el orden en que se imprimen.
RUBRO_CONDUCTO = "conducto"
RUBRO_EXCAVACION = "excavacion"
RUBRO_CONCRETO = "concreto"
RUBRO_ACERO = "acero"
RUBRO_LOSA = "losa de entrega"
RUBRO_ENROCADO = "enrocado"
RUBRO_GEOTEXTIL = "geotextil"
RUBROS_DE_METRADO = (RUBRO_CONDUCTO, RUBRO_EXCAVACION, RUBRO_CONCRETO,
                     RUBRO_ACERO, RUBRO_LOSA, RUBRO_ENROCADO,
                     RUBRO_GEOTEXTIL)

# De donde sale la partida de un renglon: del EG-2013 (su codigo es [N]) o
# del proyecto, porque el EG-2013 no tiene una (el enrocado de salida).
PARTIDA_DEL_EG2013 = "N"
PARTIDA_ESPECIAL = "A"


@dataclass(frozen=True)
class RenglonDeMetrado:
    """
    --- VE-5 met --- Un renglon del metrado de un punto: QUE se mide, con
    que partida del EG-2013, en que unidad y cuanto, con el paso de memoria
    que lo explica (la regla de medicion de la Seccion, las dimensiones de
    donde sale y su procedencia).

        rubro            uno de RUBROS_DE_METRADO
        elemento         lo que se mide, en palabras («zanja del conducto»)
        partida          codigo del EG-2013 («506.A»), o "" sin partida
        descripcion      el texto de la partida con su dato (diametro, clase)
        etiqueta_partida PARTIDA_DEL_EG2013 o PARTIDA_ESPECIAL
        desglose         (parte, cantidad) de lo que suma el renglon, en su
                         unidad: la memoria lo imprime para que el total se
                         pueda rehacer a mano
    """

    rubro: str
    elemento: str
    partida: str
    descripcion: str
    unidad: str
    cantidad: float
    paso: "PasoDeMemoria"
    etiqueta_partida: str = PARTIDA_DEL_EG2013
    desglose: Tuple[Tuple[str, float], ...] = ()
    avisos: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.rubro not in RUBROS_DE_METRADO:
            raise ValueError(
                f"RenglonDeMetrado: rubro {self.rubro!r}; se espera uno de "
                + ", ".join(RUBROS_DE_METRADO))
        if self.etiqueta_partida not in (PARTIDA_DEL_EG2013,
                                         PARTIDA_ESPECIAL):
            raise ValueError(
                f"RenglonDeMetrado «{self.elemento}»: etiqueta de partida "
                f"{self.etiqueta_partida!r}")
        if self.etiqueta_partida == PARTIDA_DEL_EG2013 and \
                not str(self.partida).strip():
            raise ValueError(
                f"RenglonDeMetrado «{self.elemento}»: una partida del "
                "EG-2013 sin codigo es una cita sin numeral")


@dataclass(frozen=True)
class MetradoDelPunto:
    """
    --- VE-5 met --- Los renglones del metrado de UN punto dimensionado con
    su cabezal (solo a expediente: la corrida de perfil difiere la Fase 9 y
    sin la longitud de metrado del barril no hay metrado). Un renglon que no
    se pudo medir no esta aqui: es un `Bloqueo` del punto con la fase de los
    metrados, que dice que falta.
    """

    id_punto: str
    renglones: Tuple[RenglonDeMetrado, ...] = ()
    avisos: Tuple[str, ...] = ()

    @property
    def pasos(self) -> Tuple["PasoDeMemoria", ...]:
        """Los pasos de los renglones, una vez cada uno: los dos renglones
        de una excavacion partida por el freatico comparten el suyo."""
        vistos: List["PasoDeMemoria"] = []
        for r in self.renglones:
            if not any(r.paso is p for p in vistos):
                vistos.append(r.paso)
        return tuple(vistos)


@dataclass(frozen=True)
class TotalDePartida:
    """
    --- VE-5 met --- La suma de UNA partida en todo el expediente: la misma
    partida con la misma descripcion (diametro, clase) y la misma unidad. La
    suma la hace `M12.totales_por_partida`, no el reporte.
    """

    partida: str
    descripcion: str
    unidad: str
    cantidad: float
    puntos: Tuple[str, ...]
    etiqueta_partida: str = PARTIDA_DEL_EG2013


ESTADO_RASANTE_COMPATIBLE = "compatible"
ESTADO_RASANTE_SUBIR = "subir rasante"
ESTADO_RASANTE_SIN_TAMIZADO = "sin tamizado"


@dataclass(frozen=True)
class FilaCompatibilidadRasante:
    """
    --- VE-5 met --- Una fila del CUADRO DE COMPATIBILIDAD RASANTE-
    ALCANTARILLA (Fase 11, entregable 9): la salida de 7.A de un punto, con
    la seccion adoptada, o lo que la impidio.

        estado     ESTADO_RASANTE_COMPATIBLE, ESTADO_RASANTE_SUBIR (con el
                   delta) o ESTADO_RASANTE_SIN_TAMIZADO (con el motivo)
        holgura_m  cota de rasante actual - cota minima de 7.A: positiva es
                   el margen, negativa lo que falta (= -delta)

    Las cotas son las de `TamizadoRasante`; ninguna se recalcula aqui salvo
    la holgura, que es su resta.
    """

    id_punto: str
    progresiva: str
    familia: str
    estado: str
    cota_rasante_actual: Optional[float] = None
    cota_rasante_min: Optional[float] = None
    cota_por_recubrimiento: Optional[float] = None
    cota_por_resguardo: Optional[float] = None
    gobierna: Optional[str] = None
    holgura_m: Optional[float] = None
    delta_rasante_m: Optional[float] = None
    cota_entrada: Optional[float] = None
    cota_clave: Optional[float] = None
    cota_salida: Optional[float] = None
    seccion: str = ""
    provisional: bool = False
    aviso: str = ""
    motivo: str = ""
