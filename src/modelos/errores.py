"""
src/modelos/errores.py
======================
Taxonomia de excepciones del proyecto (todas descienden de ErrorProyecto).

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Tuple


if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.memoria import Verificacion

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
        GUI llega por `servicio._etapa` -> `servicio._bloqueo` -> `Bloqueo` ->
        `M11.criterios_bloqueantes` -> `gui/app.py::_llenar_resumen`, y pinta
        SEIS columnas: clave, etiqueta, concepto, fuente, fases y puntos.
        Cablear esta propiedad ahi cambiaria ese tablero por un solo dato.

        Y no es que sea la via mas rica de dos: es la UNICA. Comprobado
        vaciando el `valor` de los 46 criterios y de todos los datos de sitio:
        `servicio.correr` devuelve su informe sin levantar nada, con los bloqueos
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
    columna trae un CBR negativo" son dos problemas distintos del expediente y
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


# El motivo con que la v8 §4.3 (enmendada en EXT-0) nombra el estado: es la
# frase que la memoria, el JSON y la CLI imprimen junto al HW del punto, y por
# eso es UNA constante y no una redaccion por sitio.
MOTIVO_METODO_NO_EVALUABLE = "método no evaluable (HDS-5 3.24, Sección 3.5)"
# --- T-1 --- El mismo estado cuando lo que no alcanza es un metodo del
# cap. III del Manual de Hidrologia (ver `MetodoNoEvaluableError.rotulo`).
MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA = (
    "método no evaluable (Manual de Hidrología, cap. III)")
# --- T-8 --- El mismo estado cuando lo que no alcanza es un limite de HEC-14
# (apron fuera de su poblacion, TW sobre la clave, hoya fuera de sus tablas):
# encabezarlo con «HDS-5 3.24» seria una cita falsa (auditoria de T-8, ficha
# T1-06 del mismo defecto en la hidrologia).
MOTIVO_METODO_NO_EVALUABLE_HEC14 = (
    "método no evaluable (HEC-14, FHWA-NHI-06-086)")


class MetodoNoEvaluableError(ErrorProyecto):
    """
    El dato esta y es valido, el criterio esta declarado, y lo que falta es
    un PROCEDIMIENTO que este software no implementa: el metodo disponible no
    esta definido para el punto, o no alcanza a producir la magnitud que la
    verificacion compara. Sexta de la taxonomia (EXT-3; EXT-M-01, EXT-M-02,
    PC-27).

    Regla que la separa de sus hermanas, en el orden en que se pregunta:
        DatoFaltanteError        el revisor tiene que ANADIR un dato.
        DatoInvalidoError        tiene que CORREGIR un dato.
        CriterioPendienteError   tiene que DECLARAR una eleccion.
        LimiteNumericoError      la aritmetica no cabe en un double.
        MetodoNoEvaluableError   no hay nada que anadir, corregir ni declarar:
                                 hace falta OTRO METODO (hoy, el perfil de la
                                 lamina de agua de HDS-5 Section 3.5), y hasta
                                 que exista el punto no se puede cerrar.

    Los dos casos vivos, ambos bajo CONTROL DE SALIDA con el barril
    parcialmente lleno (v8 §4.1 y §4.3):
      * `que="HW"`: HW/D < 0.75, donde la fuente dice que la aproximacion de
        h_o «should not be used» (pag. impresa 3.24). No es un incumplimiento
        --subir de diametro solo baja HW/D-- ni un aviso: el HW publicado no
        es un resultado del metodo.
      * `que="V1"` / `"V2"`: el tirante y la velocidad dentro del conducto no
        se conocen sin el perfil de la lamina, y no se inventa un criterio de
        llenado para cerrarlas.

    Viaja por la via `Bloqueo` con `TipoDeBloqueo.METODO_NO_EVALUABLE`:
    DIFERIBLE a nivel de perfil (el punto sale dimensionado con HW no
    evaluable y el motivo impreso) y NO diferible a nivel de expediente,
    donde el punto no cierra. Nunca se traduce a `Verificacion(cumple=False)`
    ni a `DisenoNoFactibleError`: MD la acumula como a los criterios
    pendientes y la relanza, en vez de descartar el material.
    """

    def __init__(self, que: str, procedimiento: str, motivo: str,
                 id_punto: Optional[str] = None, *,
                 rotulo: Optional[str] = None) -> None:
        self.que = que
        self.procedimiento = procedimiento
        self.motivo = motivo
        self.id_punto = id_punto
        # `rotulo` (T-1): el encabezado del mensaje. Por defecto es el de
        # siempre, `MOTIVO_METODO_NO_EVALUABLE`, que NOMBRA A HDS-5 porque
        # los dos casos de EXT-3 son de HDS-5. La hidrologia de T-1 levanta
        # esta misma excepcion por limites del Manual de Hidrologia (Kirpich
        # fuera de su rango de pendiente, el metodo racional por encima de
        # 10 km2), y encabezarla con «HDS-5 3.24» seria una cita falsa: pasa
        # `MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA`. El `str()` sigue empezando
        # siempre por «método no evaluable (».
        self.rotulo = MOTIVO_METODO_NO_EVALUABLE if rotulo is None else rotulo
        texto = f"{self.rotulo}: {que}"
        if id_punto:
            texto += f" del punto {id_punto}"
        texto += f" -- {motivo}. Hace falta: {procedimiento}"
        super().__init__(texto)
