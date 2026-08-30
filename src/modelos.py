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
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple, Union

from dominios import CENTIMETROS_POR_METRO


# ===========================================================================
# Taxonomia de excepciones
# ---------------------------------------------------------------------------
# Prohibido usar Exception generica en logica de negocio. Toda excepcion del
# calculo desciende de ErrorProyecto, para que la GUI pueda distinguir un
# problema del expediente de un fallo del programa.
#
# SON CINCO, NO CUATRO, desde S16.5. La quinta -- LimiteNumericoError -- no se
# anade porque las otras cuatro fueran insuficientes en teoria, sino porque el
# proyecto YA la estaba usando sin nombrarla: ver la nota de MAT-D13 en su
# docstring.
# ===========================================================================

class ErrorProyecto(Exception):
    """
    Raiz de la taxonomia. La GUI la trata como aviso, no como crash.

    `verificaciones_completadas` es lo que la Fase 5 ALCANZO A VERIFICAR antes
    de detenerse. No es un dato de la excepcion --- la excepcion sigue
    significando lo mismo --- sino la parte del trabajo que ya estaba hecha
    cuando el vacio aparecio, y que sin esto se tiraba.

    Hace falta porque en este expediente ninguna combinacion pasa de V5:
    `v5_remanso` se detiene siempre en `ancho_derecho_via_m`, que ningun
    tablero aporta todavia. V1 a V4b SI se evaluaron, con su tirante, su
    velocidad y su margen, y ese calculo no llegaba a la memoria --- ni el
    veredicto ni el desarrollo ---, de modo que el revisor veia «no
    dimensionado» sin ver nada de lo que si se comprobo. Es la misma trampa
    que NOR-MEM-01: cierto sobre el codigo y falso sobre el producto.

    Vacia por defecto, y solo la rellena `M5.verificar`. Ninguna otra
    excepcion de la taxonomia la usa hoy.
    """

    verificaciones_completadas: Tuple["Verificacion", ...] = ()


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
        """
        La redaccion MINIMA que CLAUDE.md fija para esta excepcion, sin jerga
        de programa. Se conserva sin consumidor de produccion, y esa es la
        decision (SIS-B-07): ver `docs/decisiones_diferidas.md`, ficha
        SIS-B-07.

        NO ES POR AQUI POR DONDE LA GUI MUESTRA UN PENDIENTE, y el docstring
        anterior --- «Texto que la GUI muestra al usuario» --- lo afirmaba. La
        GUI llega por `cli._etapa` -> `cli._bloqueo` -> `Bloqueo` ->
        `M11.criterios_bloqueantes` -> `gui/app.py::_llenar_resumen`, y pinta
        SEIS columnas: clave, etiqueta, concepto, fuente, fases y puntos.
        Cablear esta propiedad ahi cambiaria ese tablero por un solo dato.

        Y no es que sea la via mas rica de dos: es la UNICA. Comprobado
        vaciando el `valor` de los 46 criterios y de todos los datos de sitio:
        `cli.correr` devuelve su informe sin levantar nada, con los bloqueos
        archivados. Los tres unicos sitios que levantan
        `CriterioPendienteError` --- `criterios_adoptados.valor`,
        `datos_sitio.valor` y `GeometriaCabezal.exigir_ancho_talon` --- cuelgan
        todos de etapas envueltas por `_etapa`, de modo que ninguno alcanza el
        `except ErrorProyecto` de la ventana. (Si corre otro codigo fuera de
        `_etapa` --- `correr_cabezal` llama a `condicion_normativa_cabezal`, y
        varias fases piden `externos.valor` ---: decir «lo unico que corre
        fuera de `_etapa` es `cargar_puntos`» era describir mal el archivo,
        aunque la conclusion se sostenga.) No hay consumidor honesto que
        anadir.
        """
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


class LimiteNumericoError(ErrorProyecto):
    """
    El dato individual CUMPLE su rango declarado en dominios.py, y es la
    ARITMETICA que lo combina con otro dato o con una operacion la que no lo
    puede representar en doble precision: o desborda a +-inf, o colapsa el
    denominador de una division antes de que exista resultado.

    NO ES una version mas de DatoInvalidoError, y tampoco es que
    DatoInvalidoError sea la clase equivocada por definicion. La distincion es
    de DONDE esta el problema:

        DatoInvalidoError    el dato no puede ser: cae fuera del rango fisico
                             de dominios.py, no es del tipo esperado, o
                             contradice a otro dato de su fila.
        LimiteNumericoError  cada dato, por separado, es perfectamente sano.
                             Es la COMBINACION la que no cabe en un double.

    POR QUE HACIA FALTA NOMBRARLA. Sin esta clase, un desbordamiento salia por
    uno de dos caminos, y los dos son malos. O bien el calculo seguia con un
    `inf` dentro y la memoria imprimia un diagnostico entero construido sobre
    un numero que no lo es -- eso es SIS-G-01, medido en
    `M7.proyeccion_taludes` --, o bien Python lanzaba `ZeroDivisionError` /
    `OverflowError` en crudo, fuera de ErrorProyecto, y la GUI no sabia si eso
    era un problema del expediente o un fallo del programa: son SIS-G-02 y la
    mitad alcanzable de MAT-O18, las dos en `M4.tirante_critico`.

    EL PRECEDENTE, dicho para que quien lea esta taxonomia no encuentre la
    misma inconsistencia sin explicar: MAT-D13 cerro un caso IDENTICO a este
    -- `M1_clasificacion.tr_desde_riesgo`, donde (1-R)^(1/n) redondea a 1 y el
    denominador se anula con una R que esta DENTRO de su rango declarado --
    bajo DatoInvalidoError, porque esta clase no existia todavia. No se migra
    aqui: es codigo verde y su guarda funciona. Se deja escrito para que la
    inconsistencia sea deliberada y visible, no un descuido.

    De MAT-D13 se hereda, eso si, la FORMA de la guarda, que es lo que vale:
    umbral MEDIDO en vez de un `!= 0` generico, condicion escrita EN POSITIVO
    y negada (`not A > 0` y no `A <= 0`, porque un NaN es falso frente a las
    dos y se colaria por la segunda), y mensaje que nombra al PAR culpable en
    vez de acusar a un solo dato cuando la degeneracion es de la combinacion.

    Desciende de ErrorProyecto y no de otra raiz aunque el diagnostico sea
    aritmetico: lo que el revisor tiene delante es corregible desde el
    expediente -- una cota absurda, un caudal absurdo --, y la GUI lo tiene que
    mostrar como aviso y no como traza, que es justo el contrato de
    ErrorProyecto. La firma es la de DatoInvalidoError a proposito: `motivo`
    separa los casos igual que ya los separa ahi, sin un atributo nuevo.
    """

    def __init__(self, campo: str,
                 valor: Any = None,
                 id_punto: Optional[str] = None,
                 motivo: Optional[str] = None) -> None:
        self.campo = campo
        self.valor = valor
        self.id_punto = id_punto
        self.motivo = motivo
        texto = f"Limite de la aritmetica en '{campo}'"
        if id_punto:
            texto += f" del punto {id_punto}"
        if motivo:
            texto += f": {motivo}"
        if valor is not None:
            texto += f" (valor calculado: {valor!r})"
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



# ---------------------------------------------------------------------------
# Las constantes NUMERAL_* de modulo que ningun lector de produccion consume
# ---------------------------------------------------------------------------
# SIS-B-09: ocho constantes `NUMERAL_*` estan declaradas en sus modulos y no
# las lee nadie. Estaba decidido y no estaba escrito, que es el defecto: sin
# esta nota, un mantenedor no puede distinguir "todavia no cableada" de "no le
# corresponde cablearse", y las dos se ven igual leyendo el archivo.
#
# La razon se escribe AQUI, una sola vez, y aqui y no en cada modulo porque
# las ocho son la MISMA cosa y esta es la clase que la define:
# `ReferenciaNormativa` existe justamente para separar la coordenada interna
# de la hoja de ruta -- `seccion_hoja_ruta` -- de la cita verificable --
# `numeral_norma` --, y las ocho son de la primera clase.
#
# POR QUE NO SE BORRAN. Son la unica marca en el codigo de que apartado de la
# hoja de ruta implementa cada modulo, y esa navegacion se usa en cada
# revision: se lee el modulo y se va al apartado. Borrarlas ahorraria ocho
# lineas y costaria el mapa.
#
# POR QUE NO SE IMPRIMEN. Porque no son citas. Meter "4.1" o "Fase 5, V5" en
# una memoria como si fueran numerales es exactamente el defecto que
# `ReferenciaNormativa` existe para impedir -- una verificacion externa salio
# a buscar una "Sec. 9.1" en el EG-2013, que no existe --. El numeral REAL de
# cada calculo viaja por su propia via: `Verificacion.numeral`, las constantes
# de `constantes_normativas` y el registro de `src/normativa/`.
#
# Dos de las ocho tienen ademas una segunda razon, y es un bloqueo ya
# declarado: `NUMERAL_V5` y `NUMERAL_V8` anotan las dos verificaciones de la
# Fase 5 que se detienen antes de devolver una `Verificacion` -- V5 por falta
# del perfil de remanso y del ancho de derecho de via, V8 porque su logica no
# esta escrita --, de modo que su numeral no llega a la memoria porque no hay
# fila que anotar. Cuando esas dos se resuelvan, sus constantes se leeran
# solas y saldran de esta lista.
#
# Si alguna se cablea o se borra, sale de aqui EN EL MISMO COMMIT. La guardia
# que lo vigile es trabajo de la fase de tests (S16), no de esta: escribir
# hoy un test contra el estado actual congelaria los defectos que las fases de
# correccion todavia estan cerrando.
NUMERALES_DE_SECCION_SIN_LECTOR = (
    "modulos.M2_material.NUMERAL_MATERIAL",       # "Sec. 3.4"
    "modulos.M3_hidraulica.NUMERAL_MANNING",      # "4.1"
    "modulos.M4_control.NUMERAL_SALIDA",          # "4.3"
    "modulos.M5_verificaciones.NUMERAL_V5",       # bloqueo declarado
    "modulos.M5_verificaciones.NUMERAL_V8",       # bloqueo declarado
    "modulos.M8_estructural.NUMERAL_8_1_2",       # "Fase 8, items 1-2"
    "modulos.M8_estructural.NUMERAL_8_1",         # encabezado del bloque
    "modulos.MD.NUMERAL_BUCLE",                   # "Sec. 2 de la guia"
)


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
                             cota entrada + HW + resguardo(CBR) + e_paq )

    No es una etiqueta cosmetica: dice que hay que mover para bajar la rasante
    minima. Si gobierna RECUBRIMIENTO, el que manda es el conducto (bajar el
    invert, reducir el diametro o cambiar de material, porque h_rec depende
    del material); si gobierna RESGUARDO, manda la hidraulica (bajar el HW) o
    el CBR de la subrasante. Con la condicion equivocada en la memoria, el
    proyectista corrige la variable que no gobierna.
    """
    RECUBRIMIENTO = "recubrimiento"   # cota clave + h_rec + e_paq
    RESGUARDO = "resguardo"           # cota entrada + HW + resguardo + e_paq


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
    para velocidad MAXIMA y socavacion. Se expone con TRES propiedades -- no
    dos -- para que ningun modulo tenga que recordar cual es cual: la
    velocidad tiene dos umbrales, un techo y un piso, y cada uno se calcula
    con el n del extremo contrario. `n_para_velocidad_minima` devuelve el
    mismo numero que `n_para_capacidad`, y tiene nombre propio porque el
    motivo es otro: alli n_max da mas tirante, aqui da menos velocidad.

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
    norma_producto: str                     # designacion METRICA de la norma
                                            # de producto: "AASHTO M 170M-04 /
                                            # ASTM C 76M-02 (metrica)",
                                            # "AASHTO M 36 / ASTM A760/A760M-10",
                                            # "AASHTO M294". Las imperiales
                                            # (C76, M170) nombran documentos
                                            # que este expediente no tiene y
                                            # cuyas tablas van en pulgadas
                                            # (NOR-PRO-05)
    hds5: ConstantesHDS5                    # carta adoptada en Sec. 4.2
    fila_manning: str                       # fila LITERAL de la Tabla N 09
    # Los dos techos de velocidad, separados porque son dos cosas distintas y
    # un solo campo las confundia (SIS-A-06): el campo anotado
    # `Optional[Tuple[float, float]]` transportaba el par de la Tabla N 10 para
    # el concreto y un ESCALAR para TMC y HDPE, de modo que el contrato que se
    # consulta aqui decia lo que el dato no era.
    v_max_tabla10: Optional[Tuple[float, ...]]   # m/s - fila de la Tabla N 10,
                                            # tal cual: dos valores para el
                                            # concreto, uno para la
                                            # mamposteria. None = el material
                                            # NO tiene fila en esa tabla
    v_max_adoptado: Optional[float]         # m/s - techo escalar de un criterio
                                            # [C] (TMC, HDPE). None = el techo
                                            # sale de la tabla, o falta declararlo
    h_relleno_min_eg2013: Optional[float]   # m sobre la clave; None = EG-2013 no lo fija
    espesor_pared: Optional[float]          # m - t; None = criterio sin declarar
    seccion_eg2013: str                     # 505 / 506 / 507 / 508 (Capitulo V)

    @property
    def n_para_capacidad(self) -> float:
        """n maximo: conservador del lado de la inundacion (Sec. 4.1)."""
        return self.n_max

    @property
    def n_para_velocidad_maxima(self) -> float:
        """
        n minimo: conservador del lado de la erosion (Sec. 4.1), o sea contra
        los TECHOS de velocidad -- V3 y el d50 de Laushey. Es la estimacion
        ALTA de velocidad.

        El nombre reproduce el de la hoja de ruta (Sec. 4.1: n minimo para
        "velocidad maxima y socavacion"). Se llamaba `n_para_velocidad`, sin
        el "maxima", y ese nombre era la mitad del defecto MAT-D1: leido desde
        V2 -- que es tambien una verificacion de velocidad -- parecia el n que
        le tocaba, y no lo es.
        """
        return self.n_min

    @property
    def n_para_velocidad_minima(self) -> float:
        """
        n maximo: el que da la estimacion BAJA de velocidad sobre la geometria
        de diseño, y por lo tanto el conservador contra un PISO de velocidad
        (V2, autolimpieza, Sec. 4.1.1.3.6).

        Devuelve el mismo numero que `n_para_capacidad` y existe aparte porque
        la razon es distinta: en capacidad n_max se usa porque exige mas area,
        y aqui porque entrega menos velocidad. Si algun dia el proyecto tomara
        el n de dos tablas distintas para las dos cosas, esta propiedad es la
        que cambiaria sin tocar la otra.
        """
        return self.n_max

    @property
    def v_max_definida(self) -> bool:
        """
        True si el material tiene un techo de velocidad aplicable: fila en la
        Tabla N 10, o techo escalar declarado en su criterio.

        HOY DEVUELVE True PARA LOS TRES, y el docstring anterior decia lo
        contrario -- "False para TMC y HDPE mientras el Tablero 1.3 siga
        abierto" (SIS-A-06). La frase no era falsa cuando se escribio: era
        condicional, y su condicion se cerro al declararse 'v_max_tmc' y
        'v_max_hdpe' con la fuente WSDOT. Vuelve a False para TMC o HDPE si
        alguien vacia esos criterios, que es justo lo que este campo tiene que
        poder decir.
        """
        return self.v_max_tabla10 is not None or self.v_max_adoptado is not None


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
    inundacion fija el theta real de diseño. Sobre esa MISMA geometria (mismo
    theta, mismo R) se calculan las DOS velocidades de la regla de doble n,
    porque un umbral de velocidad no tiene un extremo conservador sino dos, y
    son opuestos:

        `V_erosion`        con n_min: la estimacion ALTA. Es la que hay que
                           usar contra un TECHO -- V3 (velocidad maxima
                           admisible) y el d50 de Laushey (Fase 6) --, porque
                           el riesgo esta en que la velocidad real sea mayor
                           que la calculada.
        `V_sedimentacion`  con n_max: la estimacion BAJA. Es la que hay que
                           usar contra un PISO -- V2 (velocidad minima de
                           autolimpieza) --, porque ahi el riesgo es el
                           contrario: que la velocidad real sea MENOR que la
                           calculada y el conducto sedimente.

    POR QUE HAY DOS Y NO UNA (MAT-D1). Este tipo llevaba un solo campo `V`,
    calculado con n_min, y V2 lo consumia: un piso verificado con la
    estimacion alta de velocidad, o sea el conservadurismo invertido. La
    Sec. 4.1 de la hoja de ruta asigna n minimo a "velocidad MAXIMA y
    socavacion" y no nombra a V2; el fixture CP-3 modela el umbral de V2 con
    n = 0.013, que es n_max. El repositorio se contradecia a si mismo, y la
    ventana permisiva era real: con D = 0.90 m, y/D = 0.75 y S = 5e-5, la
    velocidad de la rama n_max es 0.228 m/s -- por debajo del piso de
    0.25 m/s -- mientras que la de la rama n_min da 0.297 m/s y el punto salia
    "cumple".

    `V_erosion * geometria.A != Q` en general: Q es el caudal de diseño que
    define el theta (con n_max), mientras que esa velocidad asume una
    rugosidad menor sobre la misma seccion (ver el fixture CP-2,
    tests/fixtures/casos_patron.py, y `modulos.M3_hidraulica.resolver_manning`).
    `V_sedimentacion`, en cambio, SI cumple `V * A = Q`, y no por casualidad:
    es la velocidad media del mismo n con que se resolvio la geometria.

    Eso la convierte ademas en el minimo REAL de la velocidad sobre todo el
    rango de n de la Tabla N 09, no solo en "la de la geometria de diseño":
    resolviendo Manning con un n menor, el tirante normal baja, el area baja y
    la velocidad media Q/A sube. La cadena vale mientras theta este en la RAMA
    CRECIENTE de la curva de capacidad de la seccion circular -- Q(theta) no
    es monotona: alcanza su maximo cerca de y/D = 0.94 y decae hasta la
    seccion llena --, y ahi esta siempre el diseño de este proyecto, porque V1
    lo acota en y/D <= 0.75 (num. 4.1.1.3.7 b). Se dice y no se da por
    supuesto: por encima de ese maximo la relacion theta(n) deja de ser
    creciente y el argumento no aplicaria.
    """

    geometria: Geometria      # con n_max
    V_erosion: float          # m/s, con n_min  - estimacion ALTA (techos)
    V_sedimentacion: float    # m/s, con n_max  - estimacion BAJA (pisos)


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
    multiplicar por D.

    `HW_sobre_D` NO LO LEE NINGUNA RUTA DE PRODUCCION, y este docstring ha
    dicho dos cosas falsas sobre el, las dos de la misma familia: predecir un
    consumidor que no existia.

    Primero decia que era "lo que compara V4b (HW/D <= 1.5)" (SIS-B-02,
    SIS-A-02), cuando M5 ni siquiera implementaba V4b. Corregido eso, decia
    que "sera el argumento del chequeo el dia que se cablee". El chequeo se
    cableo en S14 y el argumento NO es este campo: `M5.v4b_relacion_hw_d`
    divide entre D el HW del control GOBERNANTE, porque lo que la fuente
    acota es el embalse que la obra produce, y este campo es el HWi/D del
    control de ENTRADA, valido solo cuando ese control gobierna. Usarlo daria
    un numero menor que el embalse real siempre que gobierne el de salida,
    que es la direccion insegura.

    El campo se conserva por lo que SI es -- la salida literal de las
    ecuaciones de la Tabla A.1, la magnitud con la que HDS-5 razona, y
    multiplicarla por D para volver a dividirla despues seria perderla y
    recomponerla -- y lo que se dice de el es lo unico que se puede sostener:
    que hoy solo lo leen los tests. Sin consumidor y con la razon escrita, no
    sin consumidor y con un consumidor prometido.
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

    Y SE IMPRIME (SIS-B-18). La ficha lo señalaba como el unico de cinco
    campos escritos y nunca leidos que ademas no viajaba ni al JSON ni al
    HTML: una rama que el codigo distingue y el revisor no ve. Dejo de serlo
    en S18 sin que nadie lo buscara --- `M4._pasos_hidraulicos` lo lee para
    redactar la procedencia de h_o en su `PasoDeMemoria`, «(manda TW: la
    salida esta ahogada)» frente a «(manda la aproximacion geometrica)» ---,
    de modo que hoy la rama llega a la memoria como texto y con su razon.
    Lo fija `tests/test_M4_control.py`.

    AL JSON NO LLEGA, y la otra mitad de la ficha sigue viva. Tampoco llega
    ninguna otra pieza del bloque h_o --- ni `h_o`, ni `TW`, ni los dos flags
    de condicion de uso ---, de modo que la ausencia es del bloque entero y no
    un olvido de este campo. Publicar la etiqueta de la rama sin los dos
    numeros que la producen seria menos revisable que no publicarla: abrir el
    JSON al bloque completo es una decision propia.

    `h_o_fuera_de_rango` y `h_o_requiere_cautela` son las DOS condiciones de
    uso que HDS-5 pone a esa aproximacion y que el proyecto puede evaluar
    (NOR-HDS-05, num. 3.3.3, pag. impresa 3.24): por debajo de HW/D = 0.75 la
    fuente dice que la aproximacion no debe usarse, y por debajo de 1.2 pide
    cautela porque el barril puede fluir parcialmente lleno. Son banderas y no
    excepciones a proposito: la fuente no prohibe calcular, dice que el numero
    no es de fiar, y quien decide que hacer con un punto asi es el revisor.
    Viajan a `ResultadoHidraulico` -- ya filtradas por si el control de salida
    gobierna, que es la condicion con que la fuente las escribe -- y de ahi a
    la memoria del punto.

    La tercera condicion de la fuente -- que el barril fluya lleno en la mayor
    parte de su longitud -- NO tiene bandera porque no se puede evaluar sin un
    perfil de la lamina de agua. Queda declarada en
    `constantes_normativas.H_O_CONDICION_APLICACION`.
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
    HW_sobre_D: float = 0.0       # adimensional - HW/D, lo que acotan las dos
                                  # condiciones de uso de h_o
    h_o_fuera_de_rango: bool = False      # HW/D < 0.75 (num. 3.3.3)
    h_o_requiere_cautela: bool = False    # HW/D < 1.2  (num. 3.3.3)
    numeral: str = "Sec. 4.3"


# ===========================================================================
# Resultados
# ===========================================================================

@dataclass(frozen=True)
class ResultadoHidraulico:
    """
    Salida de M3 + M4 para una combinacion punto / material / diametro.

    ATENCION a la regla de doble n (Sec. 4.1): `y_normal` se resuelve con
    n_max, y la velocidad viaja en DOS campos porque un umbral de velocidad
    tiene dos extremos conservadores opuestos (ver `TiranteNormal`):

        `V_erosion`        con n_min, estimacion ALTA. Contra los TECHOS: V3
                           y el d50 de la Fase 6. En general
                           `V_erosion * A != Q`, y esa discrepancia es
                           intencional.
        `V_sedimentacion`  con n_max, estimacion BAJA. Contra el PISO: V2.

    NO HAY UN CAMPO `V` A SECAS, Y ES DELIBERADO. Lo habia, valia `V_erosion`
    y V2 lo consumia para verificar un piso con la estimacion alta (MAT-D1).
    Un nombre neutro deja que cada consumidor suponga que "la velocidad" es la
    suya; con dos nombres, elegir mal es visible en la linea que lo hace. Un
    modulo que obtenga la velocidad dividiendo Q entre A esta anulando la
    regla de doble n: siempre le dara `V_sedimentacion`, tambien cuando lo que
    necesita es el techo.

    HW_entrada y HW_salida son cargas sobre el fondo de la entrada, en metros.
    La conversion a cota (msnm) la hace M7 sumando la cota de entrada.

    `Q` y `S` son LOS DATOS CON QUE CORRIO EL DISENO, no los de la fila del
    CSV, y viajan aqui por el mismo motivo: ninguno de los dos sale siempre de
    su columna. Sec. 2.3 pone el caudal de la Familia B en el drenaje
    longitudinal y el de la C en el canal, y el punto cuya rasante no sigue el
    cauce declara su pendiente aparte ('S_conducto' de la CLI). Quien
    consuma este resultado -- la Fase 6, el tamizado de 7.A, la memoria --
    tiene que poder leer con QUE numeros se resolvio, sin volver a decidirlo.

    `S` entro en el tipo al cerrarse MAT-D9: la Fase 7 la re-resolvia por su
    cuenta contra `punto.S_cauce` y caia en la pendiente del cauce aunque el
    diseno hubiera corrido con otra, de modo que un mismo punto tenia dos
    pendientes -- una en el HW y otra en la cota de salida -- sin que nada lo
    dijera. No es un dato nuevo: es el mismo que M3 y M4 ya recibieron, hecho
    visible en su salida para que no se pueda elegir dos veces.

    `h_o_fuera_de_rango` / `h_o_requiere_cautela`: HDS-5 acota el uso de
    h_o = (dc + D)/2 con dos limites sobre HW/D, y los escribe condicionados a
    que el control de salida gobierne (num. 3.3.3, pag. impresa 3.24). Aqui
    llegan ya con esa condicion aplicada, de modo que True significa "este
    punto usa la aproximacion fuera del rango que su fuente declara" y no
    "podria pasarle a alguien". M11 lo imprime junto al HW del punto.
    """

    y_normal: float                       # m  - con n_max (Sec. 4.1)
    y_critico: float                      # m  - Q^2*T/(g*A^3) = 1 (Sec. 4.2)
    V_erosion: float                      # m/s - con n_min (Sec. 4.1)
    V_sedimentacion: float                # m/s - con n_max (Sec. 4.1)
    Q: float                              # m3/s - caudal de diseno del punto
    S: float                              # m/m - pendiente con que corrio el
                                          # diseno (la del cauce salvo que el
                                          # punto declare la suya): la MISMA
                                          # que usa 7.B (MAT-D9)
    HW_entrada: float                     # m  - control de entrada (Sec. 4.2)
    HW_salida: float                      # m  - control de salida (Sec. 4.3)
    control_gobernante: ControlGobernante
    # Las dos condiciones de uso de h_o que el proyecto evalua, ya filtradas
    # por si el control de salida gobierna (NOR-HDS-05). Ver `ControlSalida`.
    h_o_fuera_de_rango: bool = False
    h_o_requiere_cautela: bool = False
    # LA TRAZA HIDRAULICA (§4.4). Los pasos que M3 y M4 emitieron al resolver
    # esta combinacion, en el orden en que se calcularon: Manning, tirante
    # critico, control de entrada, control de salida y adopcion del
    # gobernante. M11 los formatea; no los reconstruye.
    pasos: Tuple["PasoDeMemoria", ...] = ()

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
    V: float                              # m/s - la velocidad de salida con
                                          # que se calculo el d50: siempre
                                          # `ResultadoHidraulico.V_erosion`
                                          # (rama de n minimo, estimacion
                                          # ALTA), que es el lado conservador
                                          # para una proteccion contra
                                          # socavacion -- el d50 crece con V^2
    criterio_espesor: str                 # clave en criterios_adoptados.py
    criterio_longitud: str                # clave en criterios_adoptados.py
    advertencias: Tuple[str, ...]
    numeral: str = "4.1.1.3.7 c)"
    paso: Optional["PasoDeMemoria"] = None


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
    # DE DONDE SALEN LOS PORCENTAJES DE COMPACTACION que la fila imprime, y
    # es un campo y no un comentario porque la memoria tiene que poder
    # decirlo. Al verificar las cuatro fichas contra el EG-2013 (NOR-EG-03)
    # aparecio que en tres de ellas el "95 % MDS" NO es literal de la
    # subseccion citada: llega por REMISION -- 506.07 y 507.08 remiten a la
    # Subseccion 205.12(c)(1), que es la que imprime Di > 0.95 De para la
    # corona y Di > 0.90 De para base y cuerpo --, y en la ficha del concreto
    # simple el 95 % de la pagina vecina es de OTRO elemento (el terreno base
    # de 505.06). El valor es correcto; lo que faltaba era decir por que via
    # llega, que es la diferencia entre una cita y una deduccion.
    # Vacio significa "todo lo que la fila imprime es literal de su
    # subseccion", que es el caso del HDPE.
    procedencia_de_los_porcentajes: str = ""


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

    `gamma_DC` y `gamma_EV` son los MINIMOS de la Tabla 2.4.5.3.1-2: en
    flotacion el peso propio y el peso del relleno estabilizan, y en LRFD lo
    que estabiliza se minora. `gamma_WA` es el de la subpresion, que
    desestabiliza y se mayora, y sale de la Tabla 2.4.5.3.1-1.

    `fila_gamma_EV` es la fila LITERAL de la Tabla 2.4.5.3.1-2 de la que sale
    `gamma_EV`, y viaja por la misma razon que el resto: esa tabla desglosa
    el empuje vertical de tierra POR TIPO DE ESTRUCTURA -- un muro de
    retencion y un conducto enterrado no llevan el mismo par -- y un gamma_EV
    suelto no dice de cual de las seis filas salio. El par {1.35, 0.90} que
    el proyecto uso durante un tiempo no era ninguna de ellas: mezclaba el
    maximo de una con el minimo de otra (MAT-D8, NOR-PUE-03).

    HASTA DONDE LLEGA HOY ESE CAMPO, dicho con exactitud: llega a este objeto
    y ahi se queda. `M5_verificaciones.v7_flotacion` arma la `Verificacion` de
    V7 con el codigo, el numeral y la clave del criterio, y no con la fila:
    la memoria NO imprime hoy de que fila salio el gamma de V7. Lo que si
    imprime es el criterio 'factores_carga_aashto' entero en el bloque de
    criterios usados, y ese criterio nombra la fila de cada estructura, de
    modo que el dato esta en la memoria por esa via y no por esta. Llevarlo
    tambien a la fila de V7 pide un campo mas en `Verificacion` y su
    renderizado en M11, y es trabajo de la fase de reporte, no de esta.
    """
    gamma_DC: float
    gamma_EV: float
    gamma_WA: float
    criterio: str
    fila_gamma_EV: str


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
    # LA TRAZA DE LA MEMORIA, emitida por la propia funcion que verifica.
    #
    # Va aqui y no en un canal aparte porque es lo mismo que `cumple`: el
    # resultado de la verificacion. Lo que cambia es a quien se lo cuenta --
    # `cumple` al pipeline, `paso` al lector de la memoria -- y separarlos en
    # dos objetos permitiria que dijeran cosas distintas, que es exactamente
    # lo que pasaba cuando M11 reconstruia el relato leyendo resultados
    # (SIS-A-07).
    #
    # `None` NO significa "sin fundamentar": significa que esa verificacion
    # todavia no puede tener `Fundamento`, y las razones estan censadas una a
    # una en `normativa.fundamentos.SIN_FUNDAMENTO` -- V4b, V5, V6, V8 y V9,
    # cada una con lo que habria que transcribir para traerla. M11 imprime esa
    # razon en el sitio del paso ausente, en vez de dejar el hueco callado.
    paso: Optional["PasoDeMemoria"] = None


# ===========================================================================
# La traza de la memoria (Sec. 4.4 del plan de correcciones v12)
# ---------------------------------------------------------------------------
# EL CAMBIO DE FONDO. Hasta S18 la memoria se RECONSTRUIA: M11 leia los
# resultados y volvia a armar el relato -- y, para poder armarlo, volvia a
# calcular (`y/D` en dos sitios, contra su propio docstring; SIS-A-07). Un
# reporte que recalcula es un segundo motor de calculo sin tests, y lo que
# imprime puede divergir de lo que el pipeline verifico sin que nada avise.
#
# A partir de aqui el calculo EMITE la traza y M11 la FORMATEA. `PasoDeMemoria`
# es la unidad de esa traza: los ocho campos de la §4.4, y cada uno responde a
# una pregunta que un revisor hace en voz alta delante de la memoria.
#
#     que              que se esta calculando
#     por_que          por que la norma obliga o recomienda hacerlo
#     formula          la expresion como la escribe la fuente, con su cita
#     sustitucion      los valores que entran, con unidad y PROCEDENCIA
#     resultado        el numero, con unidad y cifras declaradas
#     umbral           contra que se compara, con cita y CARACTER
#     veredicto        cumple / no cumple / diferido, con el margen
#     citas_textuales  las transcripciones literales que lo sostienen
#
# TRES REGLAS ESTAN EN LOS TIPOS, no en un test que alguien puede no correr:
#
#   1. `por_que` es obligatorio y no vacio. Un paso sin fundamento no se
#      construye. (Criterio de salida de la §4.4: "ningun PasoDeMemoria sin
#      por_que".)
#   2. Un `Umbral` sin `cita_id` no se construye. ("ningun umbral sin cita".)
#   3. Un veredicto de cumplimiento sin umbral no se construye: decir "cumple"
#      sin decir contra que es lo que hace indefendible una memoria.
#
# La cuarta -- que toda cita referenciada EXISTA en el registro -- no puede
# vivir aqui: este archivo no importa `normativa`, y no debe. La comprueba
# `modelos.paso()`, que si lo consulta, y la vuelve a comprobar el test sobre
# la memoria generada.
# ===========================================================================

# DECIMALES DE PRESENTACION de la traza. Son de la misma naturaleza que los
# `FMT_*` de M11 -- cuantos decimales se imprimen -- y por eso no son valores
# de proyecto: `Magnitud` guarda el float entero y `cifras` solo dice como
# escribirlo. Viven aqui, con nombre y una sola vez, en lugar de repetirse
# como enteros sueltos en cada llamada de cada modulo de calculo: asi el
# barrido de literales tiene tres lineas que mirar y no ochenta.
CIFRAS_MAGNITUD = 3        # literal-ok: decimales de presentacion; no entra en ningun calculo
# Cuatro para la PENDIENTE y para n: con tres, una S de 0.0006 se imprime
# 0.001 y la caida S*L deja de poder recomputarse desde la memoria, que es
# justo lo que esas filas existen para permitir (MAT-D9). Es la misma razon
# por la que M11 tiene un FMT_4.
CIFRAS_FINA = 4            # literal-ok: decimales de presentacion; no entra en ningun calculo
CIFRAS_FACTOR = 2          # el 2 y el 1 no necesitan marca: la regla los exime
CIFRAS_PORCENTAJE = 1


# Alcance de la corrida. Rotulos, no valores de proyecto: con "expediente"
# (el defecto) todo corre como siempre; con "perfil" V5 y V8 se INTENTAN pero
# su fallo se difiere, y las Fases 8 y 9 no se ejecutan.
#
# VIVEN AQUI DESDE S18, y no en `cli.py`, porque dejaron de ser de la CLI:
# M11 los necesita para decidir que va dentro de `bloque_pendientes` (el
# volcado de los Tableros 1-2-3 es de la corrida de expediente), y M11 no
# puede importar `cli` --- es `cli` quien importa M11 ---. La alternativa era
# que M11 llevara su propia copia de las dos cadenas, que es como nacen las
# dos fuentes de verdad que este proyecto persigue: `bloque_acotaciones` ya
# comparaba contra un "expediente" escrito a mano.
ALCANCE_PERFIL = "perfil"
ALCANCE_EXPEDIENTE = "expediente"


class TipoDeVeredicto(str, Enum):
    """
    CUATRO estados, y el cuarto no es relleno. Un paso puede calcular sin
    juzgar --el tirante normal es un numero, no un aprobado-- y forzarlo a
    "cumple" o "no cumple" obligaria a inventarle un umbral, que es la forma
    exacta de la cita falsa que este proyecto viene retirando.

    DIFERIDO es distinto de NO_CUMPLE y de SIN_VEREDICTO: la verificacion
    existe, tiene umbral y no se evaluo porque el alcance de la corrida la
    dejo fuera (`--alcance perfil`). Imprimirla como "cumple" seria mentir y
    como "no cumple" tambien.
    """

    CUMPLE = "cumple"
    NO_CUMPLE = "no cumple"
    DIFERIDO = "diferido"
    SIN_VEREDICTO = "sin veredicto"


@dataclass(frozen=True)
class Magnitud:
    """
    Un numero de la memoria con las tres cosas que lo hacen rastreable: su
    unidad, sus cifras y DE DONDE SALIO.

    `procedencia` es obligatoria y es la mitad que faltaba. "V = 2.31 m/s" y
    "V = 2.31 m/s, de M3 por Manning con la rama de n maximo" son la misma
    linea en la pagina y no son la misma informacion: la primera obliga al
    revisor a abrir el codigo, que es justo lo que el criterio de salida de la
    §4.4 prohibe.

    `cifras` es de PRESENTACION: cuantos decimales se imprimen. No redondea el
    valor almacenado -- el calculo sigue con el float entero -- y por eso no
    es un valor de proyecto.
    """

    simbolo: str
    valor: Any
    unidad: str
    procedencia: str
    cifras: Optional[int] = None

    def __post_init__(self) -> None:
        if not str(self.simbolo).strip():
            raise ValueError("Magnitud sin simbolo: no se puede citar")
        if not str(self.procedencia).strip():
            raise ValueError(
                f"Magnitud «{self.simbolo}» sin procedencia. La §4.4 exige "
                "que la sustitucion diga de donde sale cada valor; un numero "
                "sin origen es el que obliga a abrir el codigo")

    @property
    def texto(self) -> str:
        """El valor con su unidad, como lo imprime la memoria."""
        v = self.valor
        if isinstance(v, float) and math.isfinite(v) and self.cifras is not None:
            texto = f"{v:.{self.cifras}f}"
        elif isinstance(v, float) and not math.isfinite(v):
            texto = "no finito"
        else:
            texto = str(v)
        return f"{texto} {self.unidad}".strip()


@dataclass(frozen=True)
class Umbral:
    """
    Contra que se compara un resultado, con su cita y con su CARACTER.

    `cita_id` es obligatorio: es la regla 2 de arriba y el corazon de
    NOR-MEM-01. Un umbral sin cita es un numero que la memoria presenta como
    normativo sin poder decir de donde sale.

    `caracter` y `aplicacion` van SEPARADOS a proposito. El primero es lo que
    la FUENTE hace con el numero (exigencia, recomendacion, aproximacion); el
    segundo es lo que el PROYECTO hace con el. Los dos coinciden casi siempre,
    y donde no coinciden esta lo unico que hay que declarar: el 0.25 m/s de V2
    y el 0.75 de V1 los RECOMIENDA el Manual y este proyecto los aplica como
    umbral duro por decision conservadora propia (NOR-MEM-01, MAT-O13).
    Fundirlos en un campo es como se fabrica una exigencia que la norma no
    escribio.
    """

    descripcion: str
    valor: Any
    unidad: str
    cita_id: str
    caracter: str
    aplicacion: str
    criterio_aplicado: Optional[str] = None

    def __post_init__(self) -> None:
        if not str(self.cita_id).strip():
            raise ValueError(
                f"Umbral «{self.descripcion}» sin `cita_id`. La §4.4 exige "
                "que todo umbral de aceptacion lleve la frase de la fuente "
                "que lo fija; sin id no hay frase que buscar en el registro")
        if not str(self.aplicacion).strip():
            raise ValueError(
                f"Umbral «{self.descripcion}» sin `aplicacion`: hay que decir "
                "que hace el proyecto con el, que es lo que separa una "
                "recomendacion aplicada como dura de una exigencia")


@dataclass(frozen=True)
class Veredicto:
    """
    El resultado del contraste, con el MARGEN.

    El margen es lo que convierte "cumple" en informacion: un punto que pasa
    por 0.002 y otro que pasa por 0.4 se imprimen igual sin el, y no son el
    mismo diseno.
    """

    tipo: TipoDeVeredicto
    margen: Optional[float] = None
    unidad: str = ""
    explicacion: str = ""

    @property
    def cumple(self) -> bool:
        return self.tipo is TipoDeVeredicto.CUMPLE


@dataclass(frozen=True)
class EleccionDeProyecto:
    """
    La PROCEDENCIA de una eleccion, que es la regla R1 del plan v12: «se
    adopto X, elegido entre X1...Xn de la Tabla T (numeral N, pag. P), por la
    razon R».

    `entre` no es decorado: es lo que da sentido al analisis de sensibilidad.
    Sin las alternativas, el rango declarado de un criterio [A] es un par de
    numeros sueltos al pie de una ficha -- que es como estaba, consumido solo
    por los tests (SIS-B-05).

    `de_donde` es texto legible y `cita_id` el ancla al registro. `cita_id`
    queda VACIO a proposito cuando la eleccion no sale de una norma: un tope
    de catalogo no tiene numeral, y ponerle uno seria la cita falsa que
    NOR-PRO-01 y NOR-PRO-02 retiraron. Por eso el vacio esta permitido aqui y
    prohibido en `Umbral`.
    """

    que_se_adopto: str
    valor: Any
    entre: Tuple[str, ...]
    de_donde: str
    por_que: str
    cita_id: str = ""
    clave_criterio: str = ""

    def __post_init__(self) -> None:
        if not str(self.por_que).strip():
            raise ValueError(
                f"EleccionDeProyecto «{self.que_se_adopto}» sin `por_que`. La "
                "R1 pide las tres cosas: que se eligio, entre que, y por que")

    @property
    def texto(self) -> str:
        entre = ", ".join(str(x) for x in self.entre)
        alternativas = f", elegido entre {entre}" if entre else ""
        de = f" de {self.de_donde}" if self.de_donde else ""
        return (f"se adopto {self.que_se_adopto} = {self.valor}"
                f"{alternativas}{de}, por: {self.por_que}")


@dataclass(frozen=True)
class PasoDeMemoria:
    """
    Un paso de la memoria, emitido por la funcion que lo calcula.

    No es un registro de depuracion ni una traza de ejecucion: es el parrafo
    de la memoria, con sus numeros ya atados a su fuente, escrito por quien
    tiene delante los valores. Por eso lo emite el calculo y no el reporte --
    M11 no puede saber de donde salio un numero que le llega suelto.
    """

    que: str
    por_que: str
    formula: str
    sustitucion: Tuple[Magnitud, ...]
    resultado: Magnitud
    umbral: Optional[Umbral] = None
    veredicto: Optional[Veredicto] = None
    citas_textuales: Tuple[str, ...] = ()
    fundamento_id: str = ""
    formula_cita_id: str = ""
    elecciones: Tuple[EleccionDeProyecto, ...] = ()
    fase: str = ""
    codigo: str = ""
    nota_del_proyecto: str = ""

    def __post_init__(self) -> None:
        if not str(self.que).strip():
            raise ValueError("PasoDeMemoria sin `que`")
        if not str(self.por_que).strip():
            raise ValueError(
                f"PasoDeMemoria «{self.que}» sin `por_que`. Es la regla 1 de "
                "la §4.4 y no admite excepcion: el fundamento se declara en "
                "`normativa/fundamentos.py` y se trae con `modelos.paso()`, "
                "nunca se escribe suelto en el modulo de calculo")
        if self.veredicto is not None and self.umbral is None and \
                self.veredicto.tipo in (TipoDeVeredicto.CUMPLE,
                                        TipoDeVeredicto.NO_CUMPLE):
            raise ValueError(
                f"PasoDeMemoria «{self.que}»: veredicto "
                f"«{self.veredicto.tipo.value}» sin umbral. Decir que algo "
                "cumple sin decir contra que es lo que hace indefendible una "
                "memoria")
        if self.umbral is not None and \
                self.umbral.cita_id not in self.citas_textuales:
            raise ValueError(
                f"PasoDeMemoria «{self.que}»: la cita del umbral "
                f"«{self.umbral.cita_id}» no esta en `citas_textuales`. El "
                "umbral y su frase se imprimen juntos o el revisor lee el "
                "numero sin la frase que lo fija")

    @property
    def juzga(self) -> bool:
        """True si el paso contrasta contra un umbral."""
        return self.umbral is not None


@lru_cache(maxsize=1)
def _registro_normativo():
    """
    El registro, armado una sola vez. Mismo patron y misma razon que
    `criterios_adoptados._registro`: `paso()` lo consulta en cada llamada y
    reconstruirlo por paso convertiria la traza en el cuello de botella del
    pipeline.
    """
    from normativa import registro as _rn

    return _rn.construir()


def paso(fundamento_id: str, **kw: Any) -> PasoDeMemoria:
    """
    Construye un `PasoDeMemoria` trayendo el `por_que` del registro.

    ES LA UNICA PUERTA que los modulos de calculo usan, y por eso el `por_que`
    no se puede escribir a mano en un modulo: sale del `Fundamento`, que a su
    vez esta atado a sus citas y a su verbo por la invariante T11. Escribirlo
    suelto permitiria redactar «la norma obliga» encima de un parrafo que
    recomienda, que es el defecto que NOR-MEM-01 y MAT-O13 dejaron por escrito.

    El import del registro es DIFERIDO, igual que en
    `criterios_adoptados.tabla_del_criterio`: `modelos.py` no depende de
    `normativa` en su cabecera y no debe -- es el tipo que fluye entre modulos,
    y la regla de dependencias del registro pone a `normativa` a la izquierda
    de todo.

    Comprueba ademas que toda cita referenciada EXISTA: es la unica de las
    cuatro reglas de la §4.4 que este archivo no puede poner en un
    `__post_init__`.
    """
    reg = _registro_normativo()
    f = reg.fundamento(fundamento_id)
    citas = tuple(kw.pop("citas_textuales", ()) or ())
    umbral = kw.get("umbral")
    if umbral is not None and umbral.cita_id not in citas:
        citas = (umbral.cita_id,) + citas
    for cita_id in citas:
        reg.cita(cita_id)                       # KeyError si no existe
    for eleccion in kw.get("elecciones", ()):
        if eleccion.cita_id:
            reg.cita(eleccion.cita_id)
    if kw.get("formula_cita_id"):
        reg.cita(kw["formula_cita_id"])
    kw.setdefault("fase", f.fase)
    return PasoDeMemoria(por_que=f.por_que, fundamento_id=f.id,
                         citas_textuales=citas, **kw)


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
    cota_por_resguardo: float             # msnm - cota entrada + HW
                                          #        + resguardo(CBR) + e_paq
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
    paso: Optional["PasoDeMemoria"] = None


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

    `S_conducto` es la pendiente CON LA QUE CORRIO EL DISENO
    (`ResultadoHidraulico.S`), no una que esta fase vuelva a elegir. Sec. 7.B
    dice que la pendiente de la alcantarilla es la del cauce, y esa sigue
    siendo la regla; lo que ya no puede pasar es que el punto que declara la
    suya la use en el HW y no en la cota de salida (MAT-D9).
    """

    punto: PuntoCritico
    D: float                              # m - diametro adoptado en la Fase 4
    tamizado: TamizadoRasante             # el de 7.A, recalculado con ese D
    longitud: float                       # m
    proyeccion_taludes: float             # m - suma de los dos taludes
    factor_esviaje: float                 # adimensional - 1/cos(esviaje)
    altura_terraplen: float               # m - cota rasante - cota terreno
    S_conducto: float                     # m/m - la del diseno hidraulico
                                          # (`ResultadoHidraulico.S`), que es
                                          # la del cauce salvo declaracion
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
    # Ancho del TALON, la parte de la zapata que queda del lado del relleno.
    # Entra aqui porque el num. 2.8.1.1.14.1 define W_s como "el peso del
    # suelo que esta inmediatamente encima del muro, INCLUYENDO EL TALON": sin
    # esa medida no hay W_s y sin W_s no hay P_IR. Es opcional en la
    # dataclase y NO por comodidad -- un default numerico seria inventar
    # geometria --, sino para que las funciones que no lo necesitan sigan
    # aceptando una geometria de tanteo sin el; quien lo necesita lo pide con
    # `exigir_ancho_talon`, que se detiene si falta.
    ancho_talon: Optional[float] = None   # m

    def exigir_ancho_talon(self) -> float:
        """
        El ancho del talon, o `CriterioPendienteError` si no se declaro.

        Se detiene con la misma excepcion que el criterio del que sale la
        geometria ('predimensionamiento_cabezal'), porque es lo que es: una
        dimension del cabezal que nadie ha declarado todavia. Devolver 0 en su
        lugar anularia W_s y con el la mitad de P_IR, en la direccion no
        conservadora.
        """
        if self.ancho_talon is None:
            raise CriterioPendienteError(
                "predimensionamiento_cabezal",
                concepto="ancho del talon de la zapata",
                fuente="El num. 2.8.1.1.14.1 define W_s como el peso del "
                       "suelo inmediatamente encima del muro, incluyendo el "
                       "talon: sin el ancho del talon no hay W_s ni P_IR",
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
    # El paso de memoria del TR (§4.4). `None` cuando `procede` es False: no
    # hay TR que fundar, y el motivo lo lleva `fundamento`.
    paso: Optional["PasoDeMemoria"] = None

    def exigir_anios(self) -> int:
        """
        Devuelve el TR o lanza: un TR ausente nunca se sustituye por uno
        plausible.

        HOY NO LA LLAMA NADIE, y esa es la decision (SIS-B-08): ver
        `docs/decisiones_diferidas.md`, ficha SIS-B-08. El docstring anterior
        decia «Unico acceso permitido cuando el modulo que llama NECESITA el
        numero», que es una condicion que no se cumple en ningun sitio --- la
        misma forma de prometer un consumidor que este archivo ya desterro al
        cerrar SIS-B-02 en `ControlEntrada`.

        Los CINCO accesos de produccion al TR --- `M11._tabla_clasificacion`,
        `M11.fila_resumen`, `M11._fila_resumen_csv`, `cli._clasificacion_json`
        y `cli._lineas_punto` --- leen `.anios` y tratan el `None`
        explicitamente: lo imprimen como ausente o lo propagan. Ninguno
        necesita el entero, porque el paso que si lo necesitaria --- «Tc.py +
        IDF con el TR de Fase 2», Sec. 1.1 --- ocurre fuera de este programa y
        Q entra por columna del CSV.

        Se conserva porque es la unica sentencia EJECUTABLE del invariante,
        y `anios` esta anotado `Optional[int]`: sin ella, el consumidor que
        llegue escribira `tr.anios or 35`, que es el default silencioso que
        CLAUDE.md llama el peor error posible.

        LIMITE CONOCIDO, declarado en vez de disimulado. Hay dos motivos por
        los que `anios` es None y esta guardia solo distingue bien uno:
        Familia C (el caudal es el de diseno del canal: falta el dato, y
        `DatoFaltanteError('Q_m3s')` es correcto) y punto fuera de alcance
        (es un puente: no falta nada, y lo que corresponde es
        `DisenoNoFactibleError`, como en `M1_clasificacion.exigir_alcance`).
        `PeriodoRetorno` no lleva hoy con que separarlos sin oler el texto de
        `fundamento`, y el orden que el propio M1 documenta en su bloque de
        Uso --- `exigir_alcance(...)` ANTES de leer el TR --- deja la segunda
        rama fuera del camino. Cerrarlo del todo pide un discriminante en el
        objeto, no una guardia mas: queda anotado en el registro.
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

    NADIE DESPACHA SOBRE ESTE CAMPO, Y ES DELIBERADO (SIS-B-13)
    ----------------------------------------------------------
    Lo escribe solo `M1_clasificacion.PERFILES` y lo leen solo dos asserts de
    `tests/test_M1_clasificacion.py`. Cero lectores de produccion: `M5.verificar`
    y el cierre `verificar` de `cli.py` corren la Fase 5 ENTERA sobre todo
    punto, sin mirar la familia. La razon de que asi sea, dicha aqui porque es
    lo que faltaba escrito: si algun modulo despachara sobre esta tupla, la
    frase de la Sec. 2.3 se convertiria en un FILTRO y la Familia A se quedaria
    sin V3 (velocidad maxima), V6, V7 (flotacion), V8 y V9 --- que la tabla de
    la Fase 5 no exime por familia --- y las Familias B y C se quedarian sin
    conjunto ninguno. Es la lectura no conservadora que este campo existe para
    NO habilitar. Se conserva porque es la unica huella en el codigo de una
    frase de la fuente de verdad, y el `None` carga una distincion que se
    perderia al borrarlo.

    DEFECTO CONTRA LA HOJA DE RUTA, que es la que hay que corregir (regla 7).
    La Sec. 2.3 escribe «**A — Alcantarillas de paso.** Q hidrologico propio.
    TR 71 o 35 anios. Aceptacion: V1 + V2 + V4 + V5.» --- un conjunto SOLO
    para la Familia A y en una forma que se lee exhaustiva --- mientras la
    Fase 5 tabula sus verificaciones sin calificarlas por familia, y para B y
    C no declara nada. La hoja no dice si V1+V2+V4+V5 es «el minimo que A debe
    pasar» o «las unicas que a A se le exigen». La fuente primaria no puede
    dirimirlo: la taxonomia A/B/C y las etiquetas V1..V9 son de la hoja, no
    del MTC (`M1.NUMERAL_FAMILIA = "Sec. 2.3"`, «sin numeral MTC propio»).
    MIENTRAS NO SE CORRIJA, LA HOJA SIGUE MAL: quien la lea sin leer el codigo
    disenara una alcantarilla de Familia A creyendo que no se le exige V7
    (flotacion) ni V9 (disponibilidad de diametro). El codigo toma entretanto
    la lectura conservadora --- aplicarlas todas ---, que es la unica que no
    puede dejar un punto sin verificar.
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
    # EL RESULTADO HIDRAULICO DEL ESCALON, con su traza (§4.4).
    #
    # Viaja aqui, y no solo en el `ResultadoPunto` ganador, por la MISMA razon
    # que existe `M11.bloque_umbrales`: en este expediente ningun punto llega
    # a dimensionarse --- V5 se detiene siempre en `ancho_derecho_via_m`, que
    # ningun tablero aporta todavia --- y `ResultadoPunto.resultado_hidraulico`
    # es None en los cuatro puntos. Sin este campo, el desarrollo hidraulico
    # que M3 y M4 SI calcularon no llegaria nunca al revisor, que es
    # literalmente la forma de NOR-MEM-01: cierto sobre el codigo y falso
    # sobre el producto.
    #
    # None cuando el escalon ni siquiera transporto el caudal en flujo libre
    # (M3 no hallo tirante normal) o cuando revento antes de resolver M4.
    resultado_hidraulico: Optional["ResultadoHidraulico"] = None

    @property
    def incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las verificaciones que hicieron descartar este escalon."""
        return tuple(v for v in self.verificaciones if not v.cumple)


# ===========================================================================
# Modo de resolucion de una variable de entrada (Sec. 4.3 del plan v12)
# ===========================================================================
# Cada variable de entrada declara COMO SE RESUELVE. Eso es lo que le dice a
# la GUI que ventana abrir y a M11 que imprimir, y es informacion que hoy no
# existe en ninguna parte: el usuario ve una sola cosa -- "un dato que hay que
# llenar" -- donde el repositorio tiene tres poblaciones separadas (las
# columnas del CSV, los datos de sitio de corredor y los criterios adoptados)
# y seis maneras distintas de llegar al numero.
#
# LA SEMANTICA ES EL TIPO, igual que en `normativa/esquema.py` §7. No hay un
# campo `modo: str` que alguien pueda escribir mal: el modo se LEE del tipo
# del objeto `resolucion` (`modo_de()`), de forma que declarar una resolucion
# y declarar un modo son el mismo acto y no pueden divergir.
#
# COMO SE ELIGE EL MODO. La escalera se recorre de arriba abajo y se para en
# el primer peldaño que aplica; esta escrita aqui para que la clasificacion
# de las 83 variables sea reproducible y no dependa del gusto de quien la
# hizo:
#
#   1. El valor es una fila, una columna o una regla de lectura de una tabla
#      normativa TRANSCRITA EN EL REGISTRO   ->  DeTabla
#   2. Es un numero que una fuente acota con un piso, un techo o un
#      intervalo escritos por ella                ->  EnRango
#   3. El programa lo calcula desde otras variables ya declaradas y el
#      usuario no puede editarlo                  ->  Derivada
#   4. Sale de un catalogo o de la disponibilidad del mercado, y NO de una
#      norma                                      ->  DeCatalogo
#   5. Lo DETERMINA un procedimiento real aplicado a este sitio -- ensayo,
#      medicion de campo, lectura de mapa o de plano, estudio de un tercero
#      -- y por eso se defiende con trazabilidad y no con un rango de
#      sensibilidad                               ->  DeEnsayo
#   6. En cualquier otro caso                     ->  Libre
#
# ELEGIR (peldaño 6) Y DETERMINAR (peldaño 5) NO SON LO MISMO, y es lo que
# separa `Libre` de `DeEnsayo`: un metodo de analisis lo elige el
# proyectista aunque salga del mismo EMS del que sale la capacidad portante.
# Por eso `metodo_estabilidad_global` es `Libre` y `capacidad_portante_adm`
# es `DeEnsayo`.
#
# `DeEnsayo` cubre TODA determinacion por procedimiento, no solo el ensayo de
# laboratorio: es la misma extension que CLAUDE.md le da a la etiqueta [S]
# ("mapa, ensayo, medicion de campo"). Se llama asi porque asi lo nombra la
# Sec. 4.3 del plan, y la ventana que abre es la misma en los tres casos:
# campo mas TRAZABILIDAD OBLIGATORIA.


class ModoDeResolucion(str, Enum):
    """Los seis modos de la Sec. 4.3. Familia cerrada."""
    LIBRE = "libre"
    DE_TABLA = "de_tabla"
    EN_RANGO = "en_rango"
    DERIVADA = "derivada"
    DE_ENSAYO = "de_ensayo"
    DE_CATALOGO = "de_catalogo"


@dataclass(frozen=True)
class Libre:
    """
    Campo con su dominio fisico. Ninguna tabla, ningun rango de fuente y
    ninguna medicion lo determinan: el numero lo pone quien firma.

    `opciones` es para el conjunto cerrado de valores admisibles cuando la
    variable no es numerica (la Familia de un punto). En un criterio NO se
    usa: alli el conjunto ya vive en `Criterio.sensibilidad`, y repetirlo
    aqui crearia dos listas que pueden divergir.

    `tabla_pendiente` es la lista de trabajo que este censo produce: nombra
    la tabla de la fuente que convertiria esta variable en `DeTabla` el dia
    que se transcriba al registro. No es una excusa, es un pendiente con
    nombre.
    """
    que_lo_fija: str
    dominio: str = ""
    opciones: Tuple[str, ...] = ()
    tabla_pendiente: str = ""


@dataclass(frozen=True)
class DeTabla:
    """
    El valor es una fila, una columna, o la regla con que se lee una tabla
    del registro. La ventana MUESTRA LA TABLA ENTERA -- con su numeral, su
    pagina, sus notas y sus condiciones -- y el usuario elige sobre ella.

    `tablas` es una tupla porque hay elecciones que se hacen mirando dos: la
    de estribos y la de muros de AASHTO 3.11.6.4 se leen juntas o no se
    entiende ninguna de las dos.

    `laguna` se llena cuando lo que se elige NO es una fila sino una REGLA DE
    LECTURA que la tabla no resuelve. Es la diferencia entre "elegi la fila
    de 10 ft" y "elegi que hacer con un muro de 4 ft, que la tabla no
    tabula": la memoria tiene que poder decir cual de las dos cosas paso.

    `elegido_por` dice que OTRA variable elige la fila cuando esta transcribe
    la tabla completa en vez de elegir dentro de ella.
    """
    tablas: Tuple[str, ...]
    que_elige: str
    fila_id: Optional[str] = None
    columna_id: Optional[str] = None
    elegido_por: Optional[str] = None
    laguna: str = ""


@dataclass(frozen=True)
class EnRango:
    """
    El valor tiene que caer dentro de un rango que una fuente escribe.

    NO COPIA EL RANGO: lo referencia por (tabla, fila, columna) del registro,
    donde vive como `IntervaloAdmisible`, `TechoUnico`, `PisoUnico`,
    `ConjuntoDeMaximos` o `BandaDeInterpolacion`. Copiarlo aqui pondria los
    numeros de la norma fuera de su unico sitio y, peor, dejaria que la
    ventana pintara como "minimo" el primero de dos maximos (NOR-HID-04),
    que es exactamente el error que el tipo del registro existe para impedir.
    """
    tabla_id: str
    fila_id: str
    columna_id: str
    que_acota: str


@dataclass(frozen=True)
class Derivada:
    """
    No editable: la calcula el programa desde otras variables ya declaradas.
    La ventana muestra DE QUE se deriva y la memoria escribe la regla con su
    numeral.
    """
    de: Tuple[str, ...]
    regla: str


@dataclass(frozen=True)
class DeEnsayo:
    """
    La determina un procedimiento real aplicado a este sitio. La ventana pide
    el valor Y LA TRAZABILIDAD, y la memoria escribe la trazabilidad -- nunca
    una sensibilidad: no hay rango que elegir, hay una lectura que reproducir.
    """
    ensayo: str
    trazabilidad_exigida: str


@dataclass(frozen=True)
class DeCatalogo:
    """
    Igual que `DeTabla` pero ROTULADO COMO CATALOGO, no como norma.

    Existe por `NOR-PRO-01` y `NOR-PRO-02`: los topes de diametro estaban
    atribuidos a AASHTO M170 y ASTM A760, que tabulan hasta 3600 mm.
    Mostrarlos en una ventana rotulada "norma" seria crear una cita falsa
    nueva, y por eso `advertencia` es obligatoria y dice que norma NO lo
    sostiene.
    """
    catalogo_id: str
    que_elige: str
    advertencia: str


Resolucion = Union[Libre, DeTabla, EnRango, Derivada, DeEnsayo, DeCatalogo]

_MODO_DE_TIPO: Dict[type, ModoDeResolucion] = {
    Libre: ModoDeResolucion.LIBRE,
    DeTabla: ModoDeResolucion.DE_TABLA,
    EnRango: ModoDeResolucion.EN_RANGO,
    Derivada: ModoDeResolucion.DERIVADA,
    DeEnsayo: ModoDeResolucion.DE_ENSAYO,
    DeCatalogo: ModoDeResolucion.DE_CATALOGO,
}


def modo_de(resolucion: Resolucion) -> ModoDeResolucion:
    """
    El modo de una resolucion. Es una lectura del TIPO, no de un campo: una
    variable no puede quedarse sin modo ni declarar uno que no corresponda a
    como se resuelve.
    """
    try:
        return _MODO_DE_TIPO[type(resolucion)]
    except KeyError:
        raise TypeError(
            f"{resolucion!r} no es una resolucion de la familia cerrada de "
            f"la Sec. 4.3: {tuple(t.__name__ for t in _MODO_DE_TIPO)}"
        ) from None


class Poblacion(str, Enum):
    """
    Las TRES poblaciones que el repositorio mantiene separadas y que el
    usuario ve como una sola cosa -- "los datos que hay que llenar".

    Estan separadas por buenas razones (una es del CSV y varia punto a punto,
    otra es del corredor, la tercera es lo que el proyectista decidio donde la
    norma calla) y esas razones no se tocan. Lo que faltaba era la vista
    unica: sin ella, la GUI tiene tres pestañas que no se pueden comparar y la
    memoria tres bloques que no suman.
    """
    COLUMNA_CSV = "columna_csv"
    DATO_SITIO = "dato_sitio"
    CRITERIO = "criterio"


@dataclass(frozen=True)
class VariableDeEntrada:
    """
    Una variable que el expediente tiene que traer, con todo lo que la GUI
    necesita para pintarla y M11 para imprimirla.

    `criterio_destino` es el criterio [A] que RECIBE la eleccion cuando la
    variable la alimenta sin ser ella misma un criterio: el CBR de la fila
    entra en `resguardo_HW_subrasante`, la cota TW en `TW_receptor`. Para una
    variable que ES un criterio, es su propia clave.

    `dominio` nombra el limite de `dominios.py` que acota la celda, POR
    NOMBRE y no por valor: el dominio fisico no es normativo -- fuera de el
    la celda esta mal llenada -- y la ventana tiene que rotularlo asi
    (§4.2 del plan).
    """
    clave: str
    concepto: str
    unidad: str
    poblacion: Poblacion
    resolucion: Resolucion
    fase: str
    consumido_por: Tuple[str, ...] = ()
    criterio_destino: Optional[str] = None
    dominio: Optional[str] = None
    nota: str = ""

    @property
    def modo(self) -> ModoDeResolucion:
        """El modo de la Sec. 4.3, leido del tipo de `resolucion`."""
        return modo_de(self.resolucion)
