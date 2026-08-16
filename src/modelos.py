"""
modelos.py
==========
Tipos que fluyen entre modulos y taxonomia de excepciones del proyecto.

Regla de arquitectura: ningun modulo define dicts ad-hoc para lo que ya existe
aqui. Este archivo declara TIPOS, nunca valores: no contiene un solo literal
numerico de proyecto. Los valores [N] estan en `constantes_normativas.py`
(Anexo B) y los [N->], [C] y [A] en `criterios_adoptados.py` (Anexo A).

Unidades
--------
SI estricto: m, m2, m3/s, m/s, rad, Pa, kN. Ninguna estructura de este archivo
transporta pulgadas, pies ni kg/cm2; la conversion a unidades de presentacion
ocurre solo en M11.

Dos campos conservan la unidad de su encabezado normativo porque son
localizadores o clasificadores y no entran en ningun calculo hidraulico ni
estructural (Sec. 1.1):

    progresiva_km : km  - progresiva del cruce
    area_ha       : ha  - area de cuenca, "solo clasificador"

Referencias de numeral: docs/hoja_de_ruta_alcantarillas_v7.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Dict, Optional, Tuple


# ===========================================================================
# Taxonomia de excepciones
# ---------------------------------------------------------------------------
# Prohibido usar Exception generica en logica de negocio. Toda excepcion del
# calculo desciende de ErrorProyecto, para que la GUI pueda distinguir un
# problema del expediente de un fallo del programa.
# ===========================================================================

class ErrorProyecto(Exception):
    """Raiz de la taxonomia. La GUI la trata como aviso, no como crash."""


class CriterioPendienteError(ErrorProyecto):
    """
    Se invoco un criterio declarado en `criterios_adoptados.py` cuyo valor es
    None (vacio normativo sin resolver).

    Un criterio sin valor DETIENE el calculo; nunca se sustituye por un
    default silencioso (Sec. 0.7). La GUI lo muestra como
    "falta declarar: <clave>".
    """

    def __init__(self, clave: str,
                 concepto: Optional[str] = None,
                 fuente: Optional[str] = None) -> None:
        self.clave = clave
        self.concepto = concepto
        self.fuente = fuente
        texto = f"'{clave}' es un VACIO sin valor asignado"
        if concepto:
            texto += f" ({concepto})"
        texto += ". Debe resolverse antes de continuar"
        if fuente:
            texto += f": {fuente}"
        super().__init__(texto)

    @property
    def mensaje_gui(self) -> str:
        """Texto que la GUI muestra al usuario, sin jerga de programa."""
        return f"falta declarar: {self.clave}"


class DisenoNoFactibleError(ErrorProyecto):
    """
    Ninguna combinacion material/diametro cumple las verificaciones del punto.

    Lleva siempre el motivo y, cuando la salida del tamizado 7.A lo permite,
    el delta de rasante requerido: el chequeo devuelve "no factible -> subir
    rasante X cm", nunca un resultado silencioso (Sec. 7.B).
    """

    def __init__(self, motivo: str,
                 delta_rasante_m: Optional[float] = None,
                 id_punto: Optional[str] = None) -> None:
        self.motivo = motivo
        self.delta_rasante_m = delta_rasante_m
        self.id_punto = id_punto
        texto = "Diseno no factible"
        if id_punto:
            texto += f" en el punto {id_punto}"
        texto += f": {motivo}"
        if delta_rasante_m is not None:
            texto += f". Subir la rasante {delta_rasante_m:.2f} m"
        super().__init__(texto)


class DatoFaltanteError(ErrorProyecto):
    """Falta un dato de entrada del CSV (Sec. 1.2) o de un tablero externo."""

    def __init__(self, campo: str,
                 id_punto: Optional[str] = None,
                 detalle: Optional[str] = None) -> None:
        self.campo = campo
        self.id_punto = id_punto
        self.detalle = detalle
        texto = f"Falta el dato '{campo}'"
        if id_punto:
            texto += f" en el punto {id_punto}"
        if detalle:
            texto += f". {detalle}"
        super().__init__(texto)


class DatoInvalidoError(ErrorProyecto):
    """
    El dato esta, pero no puede ser: no es del tipo esperado, cae fuera del
    rango fisico posible, o contradice a otro dato de la misma fila (Sec. 1.5).

    Es hermano de DatoFaltanteError y no el mismo: "falta la columna" y "la
    columna trae un CBR de 250 %" son dos problemas distintos del expediente y
    se corrigen de forma distinta. Ambos descienden de ErrorProyecto, de modo
    que la GUI puede atrapar los dos con un solo except.
    """

    def __init__(self, campo: str,
                 valor: Any = None,
                 id_punto: Optional[str] = None,
                 motivo: Optional[str] = None) -> None:
        self.campo = campo
        self.valor = valor
        self.id_punto = id_punto
        self.motivo = motivo
        texto = f"Dato invalido en '{campo}'"
        if id_punto:
            texto += f" del punto {id_punto}"
        if motivo:
            texto += f": {motivo}"
        if valor is not None:
            texto += f" (valor leido: {valor!r})"
        super().__init__(texto)


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
    clave usada en `constantes_normativas.D_MAX`, `H_RELLENO_MIN` y
    `SUBSECCION`. La correspondencia con las claves de la Tabla N 09
    (`MANNING`) la resuelve M2, no este modulo.
    """
    CONCRETO_REFORZADO = "concreto_reforzado"
    TMC = "tmc"
    HDPE = "hdpe"


class ControlGobernante(str, Enum):
    """Cual de los dos controles fija la carga a la entrada."""
    ENTRADA = "entrada"   # Sec. 4.2, HDS-5
    SALIDA = "salida"     # Sec. 4.3, HW = H + ho - S*L


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
    """

    id: str                            # identificador del punto
    progresiva_km: float               # km - localizador, no entra en calculo
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


# ===========================================================================
# Material y geometria
# ===========================================================================

@dataclass(frozen=True)
class ConstantesHDS5:
    """
    Constantes de control de entrada de la Tabla A.1 de HDS-5 (Sec. 4.2).
    Los nombres de campo reproducen la notacion de la hoja de ruta.

    Ks NO figura en la Tabla A.1: proviene de la formulacion de las ecuaciones
    (-0.5 sin inglete, +0.7 con inglete). No omitirlo.
    """
    K: float
    M: float
    c: float
    Y: float
    Ks: float

    @classmethod
    def desde_dict(cls, datos: Dict[str, float]) -> "ConstantesHDS5":
        """Construye desde una fila de `HDS5_INLET` o de un criterio adoptado."""
        return cls(K=datos["K"], M=datos["M"], c=datos["c"],
                   Y=datos["Y"], Ks=datos["Ks"])


@dataclass(frozen=True)
class Material:
    """
    Material de conducto ya resuelto por M2: sus valores provienen de
    `constantes_normativas.py` y de `criterios_adoptados.py`. Este modulo solo
    declara la forma; no fija ningun numero.

    Regla de doble n (Sec. 4.1): n maximo para capacidad y tirante, n minimo
    para velocidad y socavacion. Se expone con dos propiedades para que ningun
    modulo tenga que recordar cual es cual.
    """

    tipo: TipoMaterial
    nombre: str                             # etiqueta para el reporte
    n_min: float                            # Tabla N 09 (o criterio adoptado)
    n_max: float
    D_max: float                            # m - tope de la norma de producto (V9)
    norma_producto: str                     # ASTM C76 / AASHTO M36 / M294 ...
    hds5: ConstantesHDS5                    # carta adoptada en Sec. 4.2
    v_max_rango: Optional[Tuple[float, float]]   # m/s - Tabla N 10; None = vacio
    h_relleno_min: Optional[float]          # m sobre la clave (Sec. 7.A)
    subseccion_eg2013: str                  # 505 / 506 / 507 / 508

    @property
    def n_para_capacidad(self) -> float:
        """n maximo: conservador del lado de la inundacion (Sec. 4.1)."""
        return self.n_max

    @property
    def n_para_velocidad(self) -> float:
        """n minimo: conservador del lado de la erosion (Sec. 4.1)."""
        return self.n_min

    @property
    def v_max_definida(self) -> bool:
        """False para TMC y HDPE mientras el Tablero 1.3 siga abierto."""
        return self.v_max_rango is not None


@dataclass(frozen=True)
class Geometria:
    """
    Seccion circular parcialmente llena (Sec. 4.1):

        A = (D^2/8)(theta - sen theta)      P = D*theta/2      R = A/P

    theta en radianes, sobre (0, 2*pi). Todas las longitudes en metros.
    """

    D: float          # m - diametro interior
    theta: float      # rad - angulo mojado
    A: float          # m2 - area hidraulica
    P: float          # m  - perimetro mojado
    R: float          # m  - radio hidraulico
    y: float          # m  - tirante

    @property
    def y_sobre_D(self) -> float:
        """Relacion de llenado. V1 exige y/D <= Y_SOBRE_D_MAX."""
        return self.y / self.D

    @property
    def T(self) -> float:
        """
        Ancho superficial, T = D*sen(theta/2).

        Identidad geometrica de la seccion circular, no un valor normativo:
        se deriva de y = (D/2)(1 - cos(theta/2)). La necesita M4 para el
        tirante critico, Q^2*T/(g*A^3) = 1 (Sec. 4.2).
        """
        return self.D * math.sin(self.theta / 2)


# ===========================================================================
# Resultados
# ===========================================================================

@dataclass(frozen=True)
class ResultadoHidraulico:
    """
    Salida de M3 + M4 para una combinacion punto / material / diametro.

    ATENCION a la regla de doble n (Sec. 4.1): `y_normal` se resuelve con
    n_max y `V` se calcula con n_min, de modo que en general

        V * A  !=  Q

    y esa discrepancia es intencional: Q es el caudal de diseno del punto,
    mientras que V es la velocidad conservadora del lado de la erosion, la que
    alimenta V3 y el d50 de la Fase 6. Un modulo que obtenga V dividiendo Q
    entre A esta anulando la regla.

    HW_entrada y HW_salida son cargas sobre el fondo de la entrada, en metros.
    La conversion a cota (msnm) la hace M7 sumando la cota de entrada.
    """

    y_normal: float                       # m  - con n_max (Sec. 4.1)
    y_critico: float                      # m  - Q^2*T/(g*A^3) = 1 (Sec. 4.2)
    V: float                              # m/s - con n_min (Sec. 4.1)
    Q: float                              # m3/s - caudal de diseno del punto
    HW_entrada: float                     # m  - control de entrada (Sec. 4.2)
    HW_salida: float                      # m  - control de salida (Sec. 4.3)
    control_gobernante: ControlGobernante

    @property
    def HW(self) -> float:
        """
        Carga a la entrada del control que gobierna. Es un selector sobre lo
        que M4 ya decidio, no una decision nueva.
        """
        if self.control_gobernante == ControlGobernante.ENTRADA:
            return self.HW_entrada
        return self.HW_salida


@dataclass(frozen=True)
class Verificacion:
    """
    Resultado de una verificacion de la Fase 5. Nunca se devuelve un bool
    desnudo: sin numeral, la memoria de calculo no es defendible.

    `criterio_aplicado` es la clave de `criterios_adoptados.py` cuando el
    umbral proviene de un criterio [N->], [C] o [A]; None cuando el umbral es
    [N] puro y se lee de `constantes_normativas.py`.
    """

    cumple: bool
    numeral: str                          # "4.1.1.3.7 b)", "HDS-5 Ap. A", ...
    valor_obtenido: Any
    valor_admisible: Any
    criterio_aplicado: Optional[str]
    codigo: Optional[str] = None          # "V1" .. "V9" (Fase 5)


# ===========================================================================
# Clasificacion y periodo de retorno (Fase 2, salida de M1)
# ===========================================================================

@dataclass(frozen=True)
class PeriodoRetorno:
    """
    TR de diseno de un punto y la fila de la Tabla N 02 que lo sustenta
    (Sec. 2.2). El TR no se transporta como un numero suelto: sin la fila que
    lo origina, la memoria no puede defender por que son 71 anios y no 35.

    `anios` es el valor de la columna "TR de diseno" de la tabla, redondeado
    al anio; `exacto` conserva el resultado sin redondear.

    `procede` es False en dos situaciones, y en ambas `anios` es None:
      - Familia C: su caudal es el de diseno del canal (ANA / Junta), no un
        caudal hidrologico con periodo de retorno propio (Sec. 2.3).
      - Luz >= 6.0 m: el punto es un puente y esta fuera del alcance (Sec. 2.1).
    """

    procede: bool
    categoria: Optional[CategoriaTR]
    R: Optional[float]                    # riesgo admisible de falla
    n: Optional[int]                      # vida util, anios
    exacto: Optional[float]               # TR sin redondear
    anios: Optional[int]                  # TR de diseno de la Tabla N 02
    numeral: str
    fundamento: str                       # por que esta fila y no la otra
    id_punto: Optional[str] = None

    def exigir_anios(self) -> int:
        """
        Devuelve el TR o lanza. Unico acceso permitido cuando el modulo que
        llama NECESITA el numero: un TR ausente nunca se sustituye por uno
        plausible.
        """
        if self.anios is None:
            raise DatoFaltanteError(
                "Q_m3s", id_punto=self.id_punto,
                detalle=f"este punto no tiene TR de la Tabla N 02: {self.fundamento}",
            )
        return self.anios


@dataclass(frozen=True)
class PerfilFamilia:
    """
    Lo que la familia de Sec. 2.3 implica para el resto del calculo: de donde
    sale su caudal, si la familia ya fija la fila de la Tabla N 02, que campos
    del CSV necesita y con que verificaciones se acepta.

    `verificaciones_aceptacion` es None cuando la hoja de ruta no declara un
    conjunto propio para esa familia. None significa "no declarado", no
    "ninguna": la tabla de la Fase 5 sigue aplicando punto por punto.
    """

    familia: Familia
    nombre: str
    origen_del_caudal: str
    categoria_tr: Optional[CategoriaTR]        # None: la familia no la fija
    campos_requeridos: Tuple[str, ...]         # campos de PuntoCritico
    verificaciones_aceptacion: Optional[Tuple[str, ...]]
    notas: Tuple[str, ...]
    numeral: str


@dataclass(frozen=True)
class Clasificacion:
    """
    Salida de M1 para un punto: denominacion por luz (Sec. 2.1), perfil de
    familia (Sec. 2.3) y periodo de retorno (Sec. 2.2).

    `datos_pendientes` son los campos que la familia necesita y la fila trajo
    vacios por depender de un tablero externo. Como en M0, quien decide si el
    punto se puede calcular sin ellos es el modulo que los necesite.
    """

    punto: PuntoCritico
    luz_m: float
    denominacion: Denominacion
    verificacion_luz: Verificacion
    perfil: PerfilFamilia
    periodo_retorno: PeriodoRetorno
    datos_pendientes: Tuple[str, ...] = ()

    @property
    def en_alcance(self) -> bool:
        """False si la luz lo hace puente: Manual de Puentes, otro script."""
        return self.denominacion is Denominacion.ALCANTARILLA


@dataclass(frozen=True)
class ResultadoPunto:
    """
    Resultado completo de un punto critico: la combinacion elegida y el
    expediente de verificaciones que la sostiene.

    `motivo_rechazo` se llena cuando `aceptado` es False, con el mismo texto
    que llevaria DisenoNoFactibleError si no quedara ninguna alternativa.
    """

    punto: PuntoCritico
    material: Material
    D: float                              # m - diametro adoptado
    resultado_hidraulico: ResultadoHidraulico
    verificaciones: Tuple[Verificacion, ...]
    aceptado: bool
    motivo_rechazo: Optional[str] = None

    @property
    def verificaciones_incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las que M11 debe destacar en la memoria del punto."""
        return tuple(v for v in self.verificaciones if not v.cumple)

    @property
    def coherente(self) -> bool:
        """
        True si `aceptado` concuerda con las verificaciones y con el motivo de
        rechazo. Sirve de guarda en los tests de M5 y M7.
        """
        if self.aceptado:
            return not self.verificaciones_incumplidas and self.motivo_rechazo is None
        return bool(self.motivo_rechazo)
