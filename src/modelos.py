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
transporta pulgadas, pies ni kg/cm2.

Unica salvedad, y es de presentacion, no de calculo: `TamizadoRasante` expone
`delta_rasante_cm` junto al `delta_rasante_m` que almacena, porque Sec. 7.B
redacta su salida en centimetros ("no factible -> subir rasante X cm"). El
factor sale de `dominios.CENTIMETROS_POR_METRO` -- una definicion de unidad,
no un valor de proyecto -- y ningun campo almacenado esta en centimetros.

Dos campos conservan la unidad de su encabezado normativo porque son
localizadores o clasificadores y no entran en ningun calculo hidraulico ni
estructural (Sec. 1.1):

    progresiva_km : km  - progresiva del cruce
    area_ha       : ha  - area de cuenca, "solo clasificador"

Referencias de numeral: docs/hoja_de_ruta_alcantarillas_v8.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from dominios import CENTIMETROS_POR_METRO


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
# Citas: la seccion interna y el numeral de la norma, separados
# ===========================================================================

class ReferenciaNormativa(str):
    """
    Cita partida en sus DOS mitades, que hasta ahora viajaban pegadas en un
    solo string y se confundian entre si:

        seccion_hoja_ruta   navegacion INTERNA de docs/hoja_de_ruta_*.md.
                            "Sec. 9.1", "5.1", "Fase 10". No es una cita: son
                            las coordenadas del apartado que trata el tema
                            dentro del documento propio del proyecto.
        numeral_norma       la CITA real y verificable, la que un revisor
                            busca en el documento normativo: "EG-2013,
                            Seccion 503, num. 503.01, pag. 905".

    Por que hizo falta separarlas. Constantes como
    `NUMERAL_9_1 = "Sec. 9.1 (EG-2013 num. 503.01, pag. 905)"` mezclaban las
    dos cosas en una linea, y una verificacion externa leyo el string entero
    como si fuese la cita -- salio a buscar una "Sec. 9.1" en el EG-2013, que
    no existe. En `NUMERAL_8_1` el efecto fue peor: citaba una "Seccion 500"
    del EG-2013 que tampoco existe (los conductos son las Secciones 505 a 508
    del Capitulo V), un error de simplificacion arrastrado desde una version
    temprana de la hoja de ruta. El defecto no era de una constante suelta:
    era del formato, y por eso la solucion es un tipo y no cuatro parches.

    Es una subclase de `str` a proposito. El valor sigue siendo el texto que
    la memoria imprime, de modo que todo lo que ya consumia estos numerales
    -- `Verificacion.numeral`, el escapado de M11, las pruebas que hacen
    `numeral in memoria` -- sigue funcionando sin cambios, y ademas se puede
    pedir cualquiera de las dos mitades por separado cuando el reporte quiera
    imprimir solo la cita verificable.

    El texto se compone con el NUMERAL DELANTE y la seccion propia detras y
    etiquetada: quien lea de corrido encuentra primero lo que puede
    verificar.
    """

    seccion_hoja_ruta: str
    numeral_norma: str

    def __new__(cls, *, seccion_hoja_ruta: str, numeral_norma: str):
        obj = super().__new__(
            cls, f"{numeral_norma} [hoja de ruta: {seccion_hoja_ruta}]")
        obj.seccion_hoja_ruta = seccion_hoja_ruta
        obj.numeral_norma = numeral_norma
        return obj

    def __repr__(self) -> str:
        return (f"ReferenciaNormativa(seccion_hoja_ruta="
                f"{self.seccion_hoja_ruta!r}, numeral_norma="
                f"{self.numeral_norma!r})")


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
    clave usada en `constantes_normativas.H_RELLENO_MIN` y `SECCION_EG2013`, y
    con la de los criterios que se indexan por material ('D_max_catalogo',
    'espesor_pared_conducto', 'cobertura_minima_aashto'). La correspondencia
    con las claves de la Tabla N 09 (`MANNING`) la resuelve M2, no este
    modulo.
    """
    CONCRETO_REFORZADO = "concreto_reforzado"
    TMC = "tmc"
    HDPE = "hdpe"


class ControlGobernante(str, Enum):
    """Cual de los dos controles fija la carga a la entrada."""
    ENTRADA = "entrada"   # Sec. 4.2, HDS-5
    SALIDA = "salida"     # Sec. 4.3, HW = H + ho - S*L


class CondicionRasante(str, Enum):
    """
    Cual de las dos condiciones de Sec. 7.A fija la cota de rasante minima:

        cota rasante >= max( cota clave + h_rec + e_paq ,
                             HW + resguardo(CBR) + e_paq )

    No es una etiqueta cosmetica: dice que hay que mover para bajar la rasante
    minima. Si gobierna RECUBRIMIENTO, el que manda es el conducto (bajar el
    invert, reducir el diametro o cambiar de material, porque h_rec depende
    del material); si gobierna RESGUARDO, manda la hidraulica (bajar el HW) o
    el CBR de la subrasante. Con la condicion equivocada en la memoria, el
    proyectista corrige la variable que no gobierna.
    """
    RECUBRIMIENTO = "recubrimiento"   # cota clave + h_rec + e_paq
    RESGUARDO = "resguardo"           # HW + resguardo(CBR) + e_paq


class CondicionAnalisis(str, Enum):
    """
    Las dos columnas de la tabla de factores de seguridad de Sec. 9.3: cada
    verificacion de estabilidad del cabezal tiene un FS estatico y otro
    sismico, y no son la misma verificacion con otro numero -- cambian las
    fuerzas actuantes (aparece el incremento de Mononobe-Okabe) y cambia el
    umbral (3.00 -> 2.50, 1.50 -> 1.25).

    Los valores reproducen las claves de `constantes_normativas.FS`: quien
    lea el FS de la tabla lo indexa con este enum, no con un string suelto.
    """
    ESTATICO = "estatico"
    SISMICO = "sismico"


class GobiernaEspaciamiento(str, Enum):
    """
    Cual de los dos limites de Fase 10 fija el espaciamiento maximo entre
    alcantarillas de alivio (Familia B): el limite normativo de longitud de
    cuneta por regimen, o la longitud a la que la cuneta agota su capacidad
    hidraulica admisible frente al caudal aportante. No es cosmetico: si
    gobierna NORMATIVO el remedio de un espaciamiento insuficiente es
    replantear puntos de alivio adicionales por norma; si gobierna
    HIDRAULICO, el remedio esta en la cuneta (seccion, pendiente) o en el
    area tributaria, no en el limite de 4.1.2.1 d).
    """
    NORMATIVO = "normativo"     # num. 4.1.2.1 d) -- long_max_cuneta
    HIDRAULICO = "hidraulico"   # capacidad admisible de la cuneta


class RegimenEntrada(str, Enum):
    """
    Rama de la formulacion de control de entrada de HDS-5 (Sec. 4.2). No es
    una clasificacion cualitativa del flujo: es LA ECUACION que se aplico, y
    por eso viaja en el resultado. Una memoria que dice "HW = 0.87 m" sin
    decir con que rama se obtuvo no es revisable.

    El umbral es el caudal adimensional q* = Ku*Q/(A*D^0.5), con los limites
    [N] `Q_LIM_NO_SUMERGIDO` (3.5) y `Q_LIM_SUMERGIDO` (4.0).
    """
    NO_SUMERGIDO = "no_sumergido"   # q* <= 3.5 -> Forma 1, con H_c
    TRANSICION = "transicion"       # 3.5 < q* < 4.0 -> interpolacion lineal
    SUMERGIDO = "sumergido"         # q* >= 4.0 -> forma cuadratica en q*


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

    `sucs_fundacion` es obligatoria y NINGUN modulo la lee, y las dos cosas
    son correctas a la vez. La obligatoriedad no la inventa el codigo: la
    hoja de ruta la lista en Sec. 1.1 con etiqueta [N] E.050 y la incluye en
    el encabezado literal de Sec. 1.2, o sea que una fila sin ella es un
    expediente incompleto y M0 tiene que decirlo. Su consumidor previsto es
    el criterio 'c_phi_fundacion' -- correlacion de resistencia desde la
    clasificacion SUCS --, que esta declarado vacio y cuyo ensamblaje (E1-E5
    de Sec. 9.3) esta fuera del alcance de esta CLI. Se carga, se valida y se
    imprime en la memoria; el dia que E1-E5 se ensamblen, el dato ya esta.

    `NF_profundidad_m` es la unica columna que NO viene del encabezado de
    Sec. 1.2: se agrego al reclasificar el nivel freatico como dato de sitio
    [S]. Era un criterio unico de proyecto (1.4 m, la caracterizacion de la
    llanura del Bajo Piura) y su propia verificacion pendiente ya avisaba de
    que podia variar punto a punto. Un dato que se MIDE en cada cruce es una
    columna, no un criterio: el nivel freatico de un cruce en la llanura y el
    de otro a tres kilometros son dos mediciones distintas, y declararlos con
    un solo numero fingiria una uniformidad que ningun estudio del expediente
    respalda. Viene vacio mientras el estudio geotecnico no de el valor de
    cada punto, y entonces lo que se detiene es la verificacion que lo
    necesite -- V7 en M8/M5, la subpresion del cabezal en M9 -- no la carga
    del CSV.
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
    NF_profundidad_m: Optional[float]  # m - profundidad del nivel freatico

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

    Dos campos que se leen mal si no se dice de que son:

    `D_max` NO es un tope normativo. Es el tope de CATALOGO que el proyecto
    adopta ('D_max_catalogo', [A]), y `D_max_de_catalogo` trae el rotulo con
    que hay que imprimirlo. `norma_producto` es la norma que rige el producto
    -- materiales, fabricacion, aceptacion -- y NO la que topa el diametro:
    A760 tabula hasta 3600 mm y M 170M tambien (NOR-PRO-01, NOR-PRO-02).

    `h_relleno_min_eg2013` es SOLO el minimo de EG-2013, que existe unicamente
    para HDPE (Subseccion 508.07, pag. 984). No es el recubrimiento minimo del
    material: ese lo calcula `M7_geometria.altura_recubrimiento` como el mayor
    entre este y la cobertura minima de AASHTO (Tabla 12.6.6.3-1), y depende
    del diametro exterior. Un None aqui significa "EG-2013 no lo fija para
    este material", no "falta el dato".
    """

    tipo: TipoMaterial
    nombre: str                             # etiqueta para el reporte
    n_min: float                            # Tabla N 09 (o criterio adoptado)
    n_max: float
    D_max: float                            # m - tope de CATALOGO adoptado (V9)
    D_max_de_catalogo: str                  # rotulo obligatorio de ese tope
    norma_producto: str                     # ASTM C76 / AASHTO M36 / M294 ...
    hds5: ConstantesHDS5                    # carta adoptada en Sec. 4.2
    v_max_rango: Optional[Tuple[float, float]]   # m/s - Tabla N 10; None = vacio
    h_relleno_min_eg2013: Optional[float]   # m sobre la clave; None = EG-2013 no lo fija
    espesor_pared: Optional[float]          # m - t; None = criterio sin declarar
    seccion_eg2013: str                     # 505 / 506 / 507 / 508 (Capitulo V)

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


@dataclass(frozen=True)
class TiranteNormal:
    """
    Salida de M3 (Sec. 4.1): tirante normal resuelto por Manning + Brent con
    la regla de doble n.

    `geometria` es la UNICA solucion de Brent, con n_max (rama de capacidad y
    tirante: V1 borde libre) -- el n mas conservador del lado de la
    inundacion fija el theta real de diseño. `V` reusa esa MISMA geometria
    (mismo theta, mismo R) pero recalcula la velocidad de Manning con n_min
    (rama de velocidad y socavacion: V2, V3, Laushey): el mismo canal visto
    con la rugosidad mas baja, conservador del lado de la erosion. No es una
    segunda resolucion de Brent para un theta distinto.

    Por eso, en general, `V * geometria.A != Q`: Q es el caudal de diseño que
    define el theta (con n_max), mientras que V asume una rugosidad menor
    sobre esa misma seccion (ver el fixture CP-2,
    tests/fixtures/casos_patron.py, y `modulos.M3_hidraulica.resolver_manning`).
    """

    geometria: Geometria      # con n_max
    V: float                  # m/s, con n_min


@dataclass(frozen=True)
class TiranteCritico:
    """
    Salida del primer solver de M4 (Sec. 4.2.1): tirante critico de la seccion
    circular, raiz de Q^2*T/(g*A^3) = 1, resuelta con Brent sobre theta.

    `geometria` es la seccion en estado critico (de ella salen y_c, A_c y T_c);
    `V` = Q/A_c es la velocidad critica, y `H_c` = y_c + V^2/(2g) la energia
    especifica critica que exige la Forma 1 del control de entrada.

    A diferencia de `TiranteNormal`, aqui V SI es Q/A: el tirante critico no
    depende de la rugosidad -- no interviene n en Q^2*T/(g*A^3) = 1 -- y por
    lo tanto la regla de doble n (Sec. 4.1) no le aplica. Es la unica
    velocidad del proyecto que se obtiene dividiendo Q entre A, y lo es porque
    la ecuacion que la define no tiene rama de capacidad ni rama de erosion.
    """

    geometria: Geometria      # seccion en estado critico
    V: float                  # m/s - velocidad critica, Q/A_c
    H_c: float                # m  - energia especifica critica, y_c + V^2/(2g)

    @property
    def y_c(self) -> float:
        """Tirante critico, m."""
        return self.geometria.y


@dataclass(frozen=True)
class ControlEntrada:
    """
    Salida del control de entrada HDS-5 (Sec. 4.2). Ademas del HW lleva el
    q* y la rama aplicada: son lo que hace revisable el numero en la memoria.

    `HW` es carga sobre el fondo de la entrada, en metros. `HW_sobre_D` es el
    HWi/D adimensional que devuelven las ecuaciones de la Tabla A.1, antes de
    multiplicar por D -- y es tambien lo que compara V4b (HW/D <= 1.5).
    """

    HW: float                     # m  - HWi
    HW_sobre_D: float             # adimensional - HWi/D
    q_estrella: float             # adimensional - Ku*Q/(A_llena*D^0.5)
    regimen: RegimenEntrada
    critico: TiranteCritico
    constantes: ConstantesHDS5
    numeral: str = "HDS-5 Ap. A, Tabla A.1 (Sec. 4.2)"


@dataclass(frozen=True)
class ControlSalida:
    """
    Salida del control de salida (Sec. 4.3): HW = H + h_o - S*L.

    Se guardan los tres sumandos por separado porque cada uno responde a una
    pregunta distinta del revisor: `H` es la perdida total en el barril
    (entrada + friccion + carga de velocidad), `h_o` es el nivel de agua a la
    salida que la manda aguas arriba, y `S*L` es la caida del conducto.

    `ahogado_por_TW` distingue las dos ramas de h_o = max(TW, (y_c + D)/2): si
    es True, el que gobierna el remanso es el nivel del cuerpo receptor y no
    la geometria del conducto. Es la situacion que Sec. 4.3 advierte
    expresamente para descargas a drenes con nivel propio.
    """

    HW: float                     # m  - carga sobre el fondo de la entrada
    H: float                      # m  - perdida total en el barril
    h_o: float                    # m  - max(TW, (y_c + D)/2)
    TW: float                     # m  - tirante en el cuerpo receptor
    caida: float                  # m  - S*L
    V: float                      # m/s - velocidad de referencia del barril
    R: float                      # m  - radio hidraulico de referencia
    ahogado_por_TW: bool
    critico: TiranteCritico
    numeral: str = "Sec. 4.3"


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
class ProteccionSalida:
    """
    Salida de M6 (Fase 6): d50 de Laushey y las dos piezas complementarias que
    la hoja de ruta deja como criterio adoptado (espesor y longitud).

    `d50` es la unica magnitud con formula normativa (num. 4.1.1.3.7 c). NO es
    un diseño de enrocado: la hoja de ruta (Sec. 6) dice expresamente que
    faltan la granulometria completa y el filtro, y que sin filtro el
    enrocado se socava por debajo y falla. `advertencias` transporta ese
    aviso para que ningun consumidor de este resultado lo omita.
    """

    d50: float                            # m - num. 4.1.1.3.7 c)
    espesor: float                        # m - multiplo de d50, criterio adoptado
    longitud: float                       # m - criterio adoptado
    V: float                              # m/s - velocidad de salida usada
    criterio_espesor: str                 # clave en criterios_adoptados.py
    criterio_longitud: str                # clave en criterios_adoptados.py
    advertencias: Tuple[str, ...]
    numeral: str = "4.1.1.3.7 c)"


@dataclass(frozen=True)
class CamaApoyoRelleno:
    """
    Fila de la tabla 8.1 (EG-2013 Capitulo V) para un material: cama de
    apoyo y sujecion / relleno lateral, con su numeral. Es informacion para
    la memoria y los planos (Sec. 11, entregable 7), no una verificacion con
    umbral: el CSV no trae una columna de compactacion realmente lograda
    contra la que comparar.
    """
    cama_apoyo: str
    sujecion_relleno_lateral: str
    numeral: str


@dataclass(frozen=True)
class FactoresFlotacion:
    """
    Los tres factores de carga gamma con que V7 evalua la flotacion del
    conducto (Fase 8, item 3), leidos de 'factores_carga_aashto' (Tablas
    3.4.1-1 y 3.4.1-2 de AASHTO LRFD).

    Existe para que los tres viajen juntos con la clave del criterio de la
    que salieron: quien lea el resultado de V7 en la memoria tiene que poder
    ver CUAL gamma se aplico a cada carga, no solo el numero final. Un
    equilibrio de factores de carga en el que no se distingue el gamma del
    estabilizante del gamma del desestabilizante es indistinguible, en el
    papel, de un factor de seguridad global -- que es justo lo que V7 dejo
    de ser.

    `gamma_DC` y `gamma_EV` son los MINIMOS de la Tabla 3.4.1-2: en flotacion
    el peso propio y el peso del relleno estabilizan, y en LRFD lo que
    estabiliza se minora. `gamma_WA` es el de la subpresion, que
    desestabiliza y se mayora.
    """
    gamma_DC: float
    gamma_EV: float
    gamma_WA: float
    criterio: str


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
# Fase 7 - Compatibilidad geometrica (salida de M7)
# ===========================================================================

@dataclass(frozen=True)
class TamizadoRasante:
    """
    Salida del tamizado previo de Sec. 7.A: la cota de rasante minima que el
    punto admite, como MAXIMO de las dos condiciones, y cuanto le falta a la
    rasante actual para alcanzarla.

        cota rasante >= max( cota clave + h_rec + e_paq ,
                             HW + resguardo(CBR) + e_paq )

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
    D interior + espesor de pared. EG-2013 508.07 mide el relleno minimo
    "desde la clave de la tuberia", que es la superficie exterior (MAT-D4).
    `D_supuesto` sigue siendo el diametro INTERIOR -- el que entra en Manning
    y en la geometria hidraulica -- y `D_exterior` es el que entra en la
    cobertura minima de AASHTO (el Bc del Art. 12.6.6.3) y en el empuje de
    flotacion de V7.
    """

    cota_rasante_min: float               # msnm - el maximo de las dos
    cota_rasante_actual: float            # msnm - la del CSV (Sec. 1.1)
    cota_por_recubrimiento: float         # msnm - cota clave + h_rec + e_paq
    cota_por_resguardo: float             # msnm - HW + resguardo(CBR) + e_paq
    condicion_gobernante: CondicionRasante
    cota_entrada: float                   # msnm - fondo de la entrada
    cota_clave: float                     # msnm - cota entrada + D + espesor de pared
    D_supuesto: float                     # m  - diametro INTERIOR del tamizado (Sec. 7.A)
    espesor_pared: float                  # m  - t; separa el interior del exterior
    D_exterior: float                     # m  - D_supuesto + 2*t; el Bc de AASHTO
    HW: float                             # m  - carga sobre el fondo de la entrada
    h_recubrimiento: float                # m  - relleno minimo sobre la clave
    espesor_paquete: float                # m  - cota rasante - cota subrasante
    resguardo: float                      # m  - tabla de Sec. 5.1 segun CBR
    factible: bool                        # la rasante actual ya alcanza
    delta_rasante_m: float                # m  - 0.0 si es factible
    criterio_recubrimiento: Optional[str]
    criterio_resguardo: str
    id_punto: Optional[str] = None
    numeral: str = "Sec. 7.A"

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
        if self.factible:
            return (f"factible: la rasante {self.cota_rasante_actual:.3f} msnm "
                    f"alcanza la minima de 7.A ({self.cota_rasante_min:.3f} "
                    f"msnm, gobierna {self.condicion_gobernante.value})")
        return (f"no factible -> subir rasante {self.delta_rasante_cm:.1f} cm "
                f"(de {self.cota_rasante_actual:.3f} a "
                f"{self.cota_rasante_min:.3f} msnm; gobierna la condicion de "
                f"{self.condicion_gobernante.value})")

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
    admisible frente al caudal aportante por metro lineal. Este modulo no la
    calcula: Sec. 10 punto 2 describe el procedimiento (disenar la cuneta,
    capacidad admisible con borde libre, caudal aportante por area tributaria
    e intensidad de TR = 35 anios) pero no fija la seccion de la cuneta, su n
    de Manning ni la formula de intensidad -- ningun numeral de la hoja de
    ruta los trae. Rellenar esos vacios en silencio violaria la regla del
    proyecto, asi que `M10_espaciamiento` la recibe como argumento ya
    resuelto, igual que MD.py recibe L y TW en vez de derivarlos.

    Se guardan los DOS limites por separado, no solo el minimo, porque la
    memoria tiene que poder mostrar por cuanto quedo descartado el que no
    gobierna.
    """
    L_normativo: float           # m
    L_hidraulico: float          # m
    espaciamiento_max: float     # m - el minimo de los dos
    gobierna: GobiernaEspaciamiento
    criterio_normativo: str = "long_max_cuneta"
    numeral: str = ReferenciaNormativa(
        seccion_hoja_ruta="Fase 10",
        numeral_norma="Manual de Hidrologia, Hidraulica y Drenaje (MTC), "
                      "num. 4.1.2.1 d), pag. 178",
    )


@dataclass(frozen=True)
class CompatibilidadGeometrica:
    """
    Salida de la verificacion final por punto de Sec. 7.B: la geometria del
    conducto ya amarrada al perfil (longitud, esviaje, pendiente, cotas de
    entrada y salida) y el expediente de verificaciones que la sostiene.

    `longitud` = (ancho de plataforma + proyeccion de taludes) * factor de
    esviaje, en metros. `caida` = S * longitud, y `cota_salida` = cota de
    entrada - caida.

    Las verificaciones llevan codigo G1/G2 para no confundirse con las V1-V9
    de la Fase 5: son de otra fase y de otro modulo. La lista es corta a
    proposito -- ver "Por que 7.B solo trae dos verificaciones" en el
    docstring de M7.
    """

    punto: PuntoCritico
    D: float                              # m - diametro adoptado en la Fase 4
    tamizado: TamizadoRasante             # el de 7.A, recalculado con ese D
    longitud: float                       # m
    proyeccion_taludes: float             # m - suma de los dos taludes
    factor_esviaje: float                 # adimensional - 1/cos(esviaje)
    altura_terraplen: float               # m - cota rasante - cota terreno
    S_conducto: float                     # m/m - la del cauce (Sec. 7.B)
    cota_entrada: float                   # msnm
    cota_salida: float                    # msnm - cota entrada - S*L
    caida: float                          # m  - S*L
    verificaciones: Tuple[Verificacion, ...]
    numeral: str = "Sec. 7.B"

    @property
    def verificaciones_incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las que M11 debe destacar en la memoria del punto."""
        return tuple(v for v in self.verificaciones if not v.cumple)

    @property
    def factible(self) -> bool:
        """True si las verificaciones de 7.B cumplen todas."""
        return not self.verificaciones_incumplidas

    @property
    def delta_rasante_cm(self) -> float:
        """
        Cuanto hay que subir la rasante, en centimetros. 0.0 cuando la rasante
        ya alcanza: el numero existe siempre, tambien cuando el punto cumple.
        """
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


@dataclass(frozen=True)
class CadenaSismica:
    """
    Cadena sismica completa de Sec. 9.2, con los seis pasos horizontales mas
    k_v, que va aparte porque NO deriva de la cadena: es una adopcion propia
    ([A], criterio 'k_v').

        A_s  = F_pga * PGA
        k_h0 = A_s                        (Manual de Puentes, 2.8.1.1.14.2)
        k_h  = factor_muro * k_h0

    `pasos` reproduce la tabla de la hoja de ruta fila por fila para que M11
    la imprima entera. Los campos escalares existen para que el calculo no
    tenga que buscar dentro de la tupla.
    """

    PGA: float                            # g - roca Clase B, Tr = 1000 anios
    F_pga: float                          # adimensional - factor de sitio
    A_s: float                            # g - F_pga * PGA
    k_h0: float                           # adimensional - = A_s
    factor_muro: float                    # adimensional - 1.0 = muro rigido
    k_h: float                            # adimensional - factor_muro * k_h0
    k_v: float                            # adimensional - vertical, [A] aparte
    pasos: Tuple[PasoSismico, ...]
    numeral: str = "Sec. 9.2"


@dataclass(frozen=True)
class GeometriaCabezal:
    """
    Predimensionamiento del cabezal, en metros. NO sale del CSV: Sec. 1.2 no
    trae ninguna columna de geometria del cabezal y Sec. 9 no lo dimensiona.
    Lo aporta el proyectista (criterio 'predimensionamiento_cabezal') o el
    llamador de M9 en un tanteo.

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

    @property
    def altura_total(self) -> float:
        """
        H + espesor de zapata, en m: la altura del plano vertical contra el
        que actua el relleno. No es lo mismo que `H`, que mide solo el muro
        sobre la zapata, y confundirlas subestima el empuje en el espesor de
        la zapata entero.
        """
        return self.H + self.espesor_zapata


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
    factores gamma de la combinacion (AASHTO LRFD Tabla 3.4.1-1, criterio
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
class CombinacionCarga:
    """
    Una de las tres combinaciones de Sec. 9.2 (AASHTO LRFD Sec. 3.4.1, via
    Manual de Puentes num. 2.4.5.3): Resistencia I, Servicio I o Evento
    Extremo I.

    `componentes` nombra que cargas entran; `criterio_factores` apunta al
    criterio de `criterios_adoptados.py` que tiene que entregar los factores
    gamma. La hoja de ruta NOMBRA las combinaciones pero no transcribe la
    Tabla 3.4.1-1, asi que este objeto describe la combinacion y no la
    evalua: pedir los factores detiene el calculo (Sec. 0.7).
    """

    nombre: str                           # "Resistencia I", ...
    numeral: str
    componentes: Tuple[str, ...]
    criterio_factores: str


@dataclass(frozen=True)
class RecubrimientoDiseno:
    """
    Recubrimiento adoptado en mm y de donde sale, con las DOS fuentes que la
    regla de conflicto de Sec. 0.2 obliga a comparar: "rige el recubrimiento
    mayor entre AASHTO y E.060".

    Unico dato del proyecto en milimetros, coherente con
    `constantes_normativas.RECUBRIMIENTO` (Art. 7.7.1 esta escrito en mm y
    reescribirlo en metros solo introduciria ceros). No entra en ninguna
    formula de equilibrio: es una especificacion de detalle para plano.
    """

    condicion: str                        # clave de RECUBRIMIENTO (Art. 7.7.1)
    e060_mm: float
    aashto_mm: float
    adoptado_mm: float                    # max(e060, aashto) - Sec. 0.2
    origen: str                           # "E.060" o "AASHTO"
    criterio_aashto: str                  # clave en criterios_adoptados.py
    numeral: str = "E.060 Art. 7.7.1 / Sec. 0.2 (regla del mayor)"


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
    criterio_cortante_alto: str           # clave en criterios_adoptados.py


@dataclass(frozen=True)
class EstabilidadCabezal:
    """
    Expediente de estabilidad del cabezal en UNA condicion (Sec. 9.3). Las
    cinco verificaciones de la tabla llevan codigo E1..E5 para no confundirse
    con las V1-V9 de la Fase 5 ni con las G1/G2 de la Fase 7.

    El mismo cabezal se verifica dos veces, una por `CondicionAnalisis`: el
    resultado estatico y el sismico son dos objetos, no dos campos de uno,
    porque cambian a la vez las fuerzas y los umbrales.
    """

    condicion: CondicionAnalisis
    geometria: GeometriaCabezal
    verificaciones: Tuple[Verificacion, ...]
    numeral: str = "Sec. 9.3 (E.050)"

    @property
    def verificaciones_incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las que M11 debe destacar en la memoria del cabezal."""
        return tuple(v for v in self.verificaciones if not v.cumple)

    @property
    def estable(self) -> bool:
        """True si las cinco verificaciones de Sec. 9.3 cumplen."""
        return not self.verificaciones_incumplidas


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

    `aceptado` y `punto` son los dos campos siempre presentes. Los demas solo
    existen para puntos que llegaron a dimensionarse:

        aceptado=True   material, D, resultado_hidraulico y verificaciones
                        estan completos. motivo_rechazo es None.
        aceptado=False  material, D, resultado_hidraulico y verificaciones
                        son None / tupla vacia. motivo_rechazo explica por
                        que no hubo solucion. M11 los lista aparte.

    Esta separacion permite a `disenar_lote` devolver la lista completa del
    expediente -- puntos resueltos y fallidos mezclados en el orden del CSV --
    sin perder ningun punto ni forzar un aborte.
    """

    punto: PuntoCritico
    aceptado: bool
    material: Optional[Material] = None
    D: Optional[float] = None                      # m - diametro adoptado
    resultado_hidraulico: Optional[ResultadoHidraulico] = None
    verificaciones: Tuple[Verificacion, ...] = ()
    motivo_rechazo: Optional[str] = None

    @property
    def y_sobre_D(self) -> Optional[float]:
        """
        Relacion de llenado del punto dimensionado, y_normal / D, o None si el
        punto no llego a dimensionarse.

        Vive aqui, en el tipo que fluye entre modulos, y no en la capa de
        reporte: M11 la calculaba inline en dos sitios (la tabla del punto y
        la fila del cuadro resumen), contra su propio docstring de modulo
        ("sin calcular nada nuevo") y contra la regla de arquitectura. Es el
        mismo numero que V1 verifica en `M5_verificaciones.v1_borde_libre` y
        el mismo que `Geometria.y_sobre_D` define para la seccion; escrito
        una vez, no puede divergir entre la memoria y la verificacion.
        """
        if self.resultado_hidraulico is None or self.D is None:
            return None
        return self.resultado_hidraulico.y_normal / self.D

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


# ===========================================================================
# Traza del diseno (bucle de MD; entregable 1 de la Fase 11)
# ===========================================================================

@dataclass(frozen=True)
class PasoDiseno:
    """
    Un escalon del bucle de MD: el par (material, D) que se probo y como
    termino.

    Existe porque la Fase 11 exige publicar las ITERACIONES del diseño
    (entregable 1) y `ResultadoPunto` solo conserva la combinacion ganadora:
    con ella sola la memoria muestra el diametro adoptado pero no puede
    defender por que se descarto el anterior, que es justamente lo que un
    revisor pregunta. No la produce ningun calculo nuevo -- es lo que MD ya
    evaluaba y descartaba en silencio.

    `verificaciones` viene vacia cuando el escalon ni siquiera transporto el
    caudal en flujo libre (M3 no hallo tirante normal): la Fase 5 no llego a
    correr y `motivo` lo dice. En el escalon aceptado, `motivo` es "".
    """

    material: str                         # Material.nombre
    D: float                              # m - diametro probado
    aceptado: bool
    motivo: str                           # por que se descarto; "" si aceptado
    verificaciones: Tuple[Verificacion, ...] = ()

    @property
    def incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las verificaciones que hicieron descartar este escalon."""
        return tuple(v for v in self.verificaciones if not v.cumple)
