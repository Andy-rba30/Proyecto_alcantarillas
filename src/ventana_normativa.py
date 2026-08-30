"""
ventana_normativa.py
====================
EL CONTENIDO de la ventana emergente de las Sec. 4.2 y 4.3 del plan
`docs/hoja_de_ruta_correcciones_v12.md`. Un solo componente con cuatro caras.

Que es esto, y por que no esta en gui/
--------------------------------------
La ventana tiene dos mitades que no se parecen en nada: QUE MUESTRA y COMO LO
PINTA. Este modulo es la primera, y esta fuera de `gui/` por dos razones que
no son de gusto:

1. `gui/` importa `tkinter`, que no esta en toda imagen donde corre la suite.
   Un contenido que viviera alli solo se podria probar con un doble, y probar
   con un doble lo que la pantalla ensena es un espejismo -- lo dice el
   encabezado de `tests/test_gui_contrato.py` y sigue siendo verdad. Aqui el
   contenido es un DATO: se compara campo a campo, sin ventana y sin escritorio.
2. La misma frase que la ventana pinta la tiene que poder imprimir M11. Si el
   texto de «la fuente escribe DOS MAXIMOS y ningun piso» viviera en un widget,
   la memoria diria otra cosa que la pantalla, que es como nacen las dos
   versiones de una cita.

LA VENTANA NO SABE NADA DE NORMAS POR SU CUENTA. Todo lo que muestra -- el
titulo literal, el numeral, la pagina impresa, las filas, las notas al pie,
los modificadores, el parrafo que sostiene la tabla -- sale de
`src/normativa/`. Este modulo no declara ni un numero ni una cita: los LEE.
Si algo falta en la ventana, falta en el registro, y ese es el sitio donde hay
que arreglarlo.

Las cuatro caras, y por que son cuatro y no seis
------------------------------------------------
La Sec. 4.3 declara SEIS modos de resolucion. Las caras son cuatro porque dos
pares de modos comparten cuerpo entero y se distinguen solo por el rotulo, y
duplicar el cuerpo para cambiar un rotulo es la forma mas segura de que las
dos copias se separen:

    de_tabla     ->  cara TABLA      la tabla entera, con su numeral
    en_rango     ->  cara RANGO      campo + rango + SEMANTICA + cita
    de_catalogo  ->  cara CATALOGO   la tabla de un catalogo, SIN numeral y
                                     con la norma que NO lo sostiene
    libre        ->  cara CAMPO      campo + dominio fisico (no normativo)
    de_ensayo    ->  cara CAMPO      campo + TRAZABILIDAD obligatoria
    derivada     ->  cara CAMPO      no editable + de que se deriva

`de_catalogo` NO comparte cara con `de_tabla` a proposito, aunque las dos
pinten una tabla: un `Catalogo` no es una `Fuente` y no puede sostener una
cita (test T1 del registro). La cabecera de la cara TABLA es «numeral · norma
· edicion · pagina», y esa cabecera sobre un tope de proveedor seria una cita
falsa nueva -- exactamente NOR-PRO-01 y NOR-PRO-02.

Los tres «rangos» de la Sec. 4.2, que aqui NO se mezclan
--------------------------------------------------------
El pedido original -- «que diga explicitamente entre que numeros debe estar mi
valor» -- toca tres objetos distintos que el repositorio nombra igual. Este
modulo los lleva en TRES CAMPOS SEPARADOS, cada uno con su rotulo, y ninguna
cara los une:

    `rango_normativo`       lo que la fuente acota. Es del registro y su
                            SEMANTICA ES EL TIPO (`IntervaloAdmisible`,
                            `TechoUnico`, `PisoUnico`, `ConjuntoDeMaximos`,
                            `BandaDeInterpolacion`).
    `dominio_fisico`        `dominios.py`. NO es normativo: fuera de el la
                            celda esta mal llenada.
    `rango_de_sensibilidad` el `sensibilidad` del `Criterio`. Es adopcion del
                            proyectista y se defiende mostrando el resultado
                            en los extremos.

El caso testigo es `v_max_concreto_eleccion` (NOR-HID-04): su fila de la Tabla
N 10 trae DOS MAXIMOS y ningun piso. Una ventana rotulada «rango» que
imprimiera «entre 3.0 y 6.0» ensenaria a leer 3.0 como minimo, que es
justamente lo que el tipo `ConjuntoDeMaximos` existe para impedir. Por eso la
frase que se muestra la compone `frase_del_rango()` a partir del TIPO, y no un
formateo generico de dos numeros.

Regla de uso
------------
    import ventana_normativa as vn

    v = vn.ventana("n_manning_hdpe")
    v.cara                       # Cara.TABLA
    v.tabla.titulo_literal       # con «(m/s)» donde la fuente lo escribe
    v.tabla.linea_de_cita        # numeral · norma · edicion · pagina impresa
    for fila in v.tabla.filas:   # TODAS, con las atenuadas marcadas
        fila.disponibilidad      # Elegible / PideDato / BloqueaLaEleccion
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import criterios_adoptados as _ca
import datos_sitio as _ds
import dominios as _dominios
import variables_entrada as _ve
from modelos import (DeCatalogo, DeEnsayo, Derivada, DeTabla, EnRango, Libre,
                     ModoDeResolucion, Poblacion, VariableDeEntrada)
from normativa import registro as _registro
from normativa.esquema import (Acotada, AfirmacionNegativa,
                               BandaDeInterpolacion, Catalogo, Celda,
                               CeldaSinValor, CondicionAplicacion,
                               ConjuntoDeMaximos, Efecto, Interpretacion,
                               IntervaloAdmisible, Laguna, NoEvaluable,
                               NoUsada, PendienteDeCondicion, PisoUnico,
                               PorCriterio, PorDatoDeSitio, PorExpresion,
                               QuePasaFuera, ROTULOS_DE_RANGO, TechoUnico,
                               Usada, esta_por_transcribir)


# ===========================================================================
# Las cuatro caras
# ===========================================================================

class Cara(str, Enum):
    """
    El cuerpo que la ventana pinta. Familia cerrada, como los modos.

    No es el modo con otro nombre: `_CARA_DE_MODO` mapea seis modos sobre
    cuatro caras, y ese mapeo es la unica decision de diseno de la ventana.
    Vive aqui, como dato, para que un test pueda comprobar que ningun modo se
    queda sin cara.
    """
    TABLA = "tabla"
    RANGO = "rango"
    CATALOGO = "catalogo"
    CAMPO = "campo"


_CARA_DE_MODO: Dict[ModoDeResolucion, Cara] = {
    ModoDeResolucion.DE_TABLA: Cara.TABLA,
    ModoDeResolucion.EN_RANGO: Cara.RANGO,
    ModoDeResolucion.DE_CATALOGO: Cara.CATALOGO,
    ModoDeResolucion.LIBRE: Cara.CAMPO,
    ModoDeResolucion.DE_ENSAYO: Cara.CAMPO,
    ModoDeResolucion.DERIVADA: Cara.CAMPO,
}


def cara_de(modo: ModoDeResolucion) -> Cara:
    """La cara que le toca a un modo. Falla si alguien anade un modo septimo."""
    try:
        return _CARA_DE_MODO[modo]
    except KeyError:
        raise KeyError(
            f"el modo '{modo}' no tiene cara asignada en la ventana: anadir "
            "un modo obliga a decidir que cuerpo se pinta"
        ) from None


# ===========================================================================
# R4 - cuando una fila depende de un dato que el proyecto no tiene
# ===========================================================================
# La regla R4 del plan dice que la ventana PIDE o BLOQUEA, y que NUNCA elige.
# La frontera entre las dos no es de gravedad: es de QUIEN PUEDE APORTAR EL
# DATO desde donde el usuario esta parado.
#
#   PIDE     el dato que falta es un CRITERIO: se declara desde esta misma
#            ventana, y la fila queda a un clic de ser elegible. La ventana
#            nombra la clave y el concepto, para que el usuario sepa que abrir.
#   BLOQUEA  el dato que falta NO se puede aportar aqui -- un dato de sitio
#            (que se escribe en `datos_sitio.py`, con su trazabilidad), una
#            expresion que se evalua punto por punto, una condicion que la
#            fuente declara no evaluable, o una clave que no existe declarada
#            en ninguna de las dos poblaciones. La fila no se puede elegir y
#            la ventana dice que la cerraria.
#
# En los dos casos la fila SIGUE VISIBLE. Ocultarla seria elegir por omision.


@dataclass(frozen=True)
class Elegible:
    """
    La fila o la columna se puede elegir. `resuelta_por` dice con que dato, y
    esta vacio cuando la fila no cuelga de ninguna condicion.
    """
    resuelta_por: str = ""


@dataclass(frozen=True)
class PideDato:
    """
    Falta un dato que el usuario SI puede declarar desde la ventana. Lleva la
    clave y el concepto porque «falta un dato» sin nombre no se puede resolver.
    """
    condicion_id: str
    texto_de_la_condicion: str
    clave_que_falta: str
    concepto_de_lo_que_falta: str


@dataclass(frozen=True)
class BloqueaLaEleccion:
    """
    Falta un dato que NO se aporta desde aqui. `que_lo_cerraria` es
    obligatorio y no vacio, por la misma razon que en `NoEvaluable`: un «no se
    puede» sin salida escrita es una excusa.
    """
    condicion_id: str
    texto_de_la_condicion: str
    por_que: str
    que_lo_cerraria: str

    def __post_init__(self) -> None:
        if not self.que_lo_cerraria.strip():
            raise ValueError(
                f"BloqueaLaEleccion {self.condicion_id}: falta "
                "`que_lo_cerraria`. Un bloqueo sin salida declarada no se "
                "puede pintar en una ventana")


Disponibilidad = Union[Elegible, PideDato, BloqueaLaEleccion]


def _valor_efectivo_de_criterio(clave: str) -> Any:
    """El valor que gobierna hoy, sin registrar uso ni levantar excepcion."""
    return _ca.criterio_efectivo(clave).valor


def disponibilidad_de(condicion: CondicionAplicacion) -> Disponibilidad:
    """
    Resuelve UNA condicion de aplicacion contra el estado del expediente.

    Es el unico sitio donde la ventana decide si una fila se puede elegir, y
    no decide NUNCA por el usuario: cuando el dato falta devuelve `PideDato` o
    `BloqueaLaEleccion`, jamas una fila elegida por defecto.

    El `efecto_si_indeterminada` de la condicion se respeta al pie de la
    letra: `ADVIERTE` y `EXCLUYE` no detienen la eleccion -- la fuente misma
    dijo que no bloquean --, y por eso salen como `Elegible` con la razon
    escrita. Solo `BLOQUEA` -- el defecto del registro (D4) -- impide elegir.
    """
    r = condicion.resuelve
    texto = condicion.texto.texto

    if isinstance(r, PorCriterio):
        if r.clave not in _ca.CRITERIOS:
            return BloqueaLaEleccion(
                condicion_id=condicion.id, texto_de_la_condicion=texto,
                por_que=(f"la condicion se resuelve con el criterio "
                         f"'{r.clave}', que no esta declarado en "
                         "criterios_adoptados.py"),
                que_lo_cerraria=("declarar el criterio en "
                                 "criterios_adoptados.py con su etiqueta, su "
                                 "justificacion y su fuente"))
        if _valor_efectivo_de_criterio(r.clave) is not None:
            return Elegible(resuelta_por=f"criterio '{r.clave}'")
        return _indeterminada(
            condicion,
            PideDato(condicion_id=condicion.id, texto_de_la_condicion=texto,
                     clave_que_falta=r.clave,
                     concepto_de_lo_que_falta=_ca.criterio(r.clave).concepto))

    if isinstance(r, PorDatoDeSitio):
        if r.clave not in _ds.DATOS_SITIO:
            return BloqueaLaEleccion(
                condicion_id=condicion.id, texto_de_la_condicion=texto,
                por_que=(f"la condicion se resuelve con el dato de sitio "
                         f"'{r.clave}', que no esta declarado en "
                         "datos_sitio.py: no es que falte su valor, es que "
                         "falta el dato entero"),
                que_lo_cerraria=("declarar el dato en datos_sitio.py, con su "
                                 "procedimiento y su trazabilidad"))
        if _ds.dato(r.clave).valor is not None:
            return Elegible(resuelta_por=f"dato de sitio '{r.clave}'")
        return _indeterminada(
            condicion,
            BloqueaLaEleccion(
                condicion_id=condicion.id, texto_de_la_condicion=texto,
                por_que=(f"el dato de sitio '{r.clave}' "
                         f"({_ds.dato(r.clave).concepto}) esta declarado sin "
                         "valor, y un dato de sitio NO se declara desde esta "
                         "ventana: es un hecho determinado por un "
                         "procedimiento, no una eleccion"),
                que_lo_cerraria=(f"{_ds.dato(r.clave).procedimiento} -- y "
                                 "escribir el valor en datos_sitio.py con su "
                                 "trazabilidad")))

    if isinstance(r, PorExpresion):
        return _indeterminada(
            condicion,
            BloqueaLaEleccion(
                condicion_id=condicion.id, texto_de_la_condicion=texto,
                por_que=("la condicion se evalua con la expresion "
                         f"'{r.expresion}', sobre {', '.join(r.simbolos)}: "
                         "son datos de un punto del CSV y esta ventana "
                         "declara valores de proyecto, no de un punto"),
                que_lo_cerraria=("correr el pipeline: la expresion se evalua "
                                 "punto por punto y su resultado va a la "
                                 "memoria de ese punto")))

    if isinstance(r, NoEvaluable):
        return _indeterminada(
            condicion,
            BloqueaLaEleccion(
                condicion_id=condicion.id, texto_de_la_condicion=texto,
                por_que=r.por_que, que_lo_cerraria=r.que_lo_cerraria))

    raise TypeError(
        f"condicion {condicion.id}: `resuelve` es un {type(r).__name__}, que "
        "no esta en la familia cerrada del registro")


def _indeterminada(condicion: CondicionAplicacion,
                   si_bloquea: Disponibilidad) -> Disponibilidad:
    """
    Que hacer con una condicion que no se pudo resolver, segun lo que la
    propia condicion declara.

    `ADVIERTE` y `EXCLUYE` llevan `justificacion_de_no_bloquear` obligatoria
    (test T15 del registro), y esa justificacion es lo que la ventana pinta:
    la fila se puede elegir Y el usuario lee por que la condicion no la
    detiene. Fabricar aqui un bloqueo que la fuente no pone seria el error
    simetrico al de elegir por el usuario.
    """
    if condicion.efecto_si_indeterminada is Efecto.BLOQUEA:
        return si_bloquea
    return Elegible(
        resuelta_por=(f"la condicion queda indeterminada y su efecto "
                      f"declarado es '{condicion.efecto_si_indeterminada.value}': "
                      f"{condicion.justificacion_de_no_bloquear}"))


# ===========================================================================
# Los tres rangos de la Sec. 4.2, cada uno con su rotulo
# ===========================================================================

@dataclass(frozen=True)
class RangoMostrado:
    """
    Un rango, con la FRASE que lo dice y el ROTULO que dice de que clase es.

    `rotulo` no es decorado: es lo que separa «la norma acota esto» de «fuera
    de esto la celda esta mal llenada» y de «esto es lo que el proyectista
    movio para defender su adopcion». Las tres frases se parecen y no
    significan lo mismo, y esa confusion es el motivo de la Sec. 4.2.
    """
    clase: str                 # "normativo" | "dominio_fisico" | "sensibilidad"
    rotulo: str
    frase: str
    unidad: str = ""
    cita: str = ""
    que_pasa_fuera: str = ""


_QUE_PASA_FUERA: Dict[QuePasaFuera, str] = {
    QuePasaFuera.INCUMPLE_LA_NORMA:
        "el valor INCUMPLE la norma que lo acota",
    QuePasaFuera.SALE_DEL_DOMINIO:
        "el valor sale del dominio fisico del dato: la celda esta mal llenada",
    QuePasaFuera.DEJA_DE_SER_DEFENDIBLE:
        "el valor deja de ser defendible con la adopcion declarada",
    QuePasaFuera.LA_FUENTE_NO_SE_PRONUNCIA:
        "la fuente no se pronuncia: fuera de aqui no hay norma que respalde "
        "el valor, ni a favor ni en contra",
}


def _num(x: float) -> str:
    """
    Un numero como el registro lo guarda.

    `str` y no un formato con precision fija: la transcripcion escribe 3.0 y
    0.013, y un `{:g}` los convertiria en «3» y «0.013», perdiendo por el
    camino la unica forma que el revisor puede cotejar contra la pagina. Lo
    que el registro no puede devolver es la cifra significativa que la fuente
    imprime cuando es un cero final (0.030): eso se pierde al transcribir a
    float, y no lo arregla el formateo.
    """
    return str(x)


def frase_del_rango(rango: Any) -> str:
    """
    «Debe estar entre X e Y» -- pero SOLO cuando eso es lo que la fuente dice.

    La frase se compone a partir del TIPO del rango, que es donde vive la
    semantica. Un `ConjuntoDeMaximos` no produce nunca una frase con la
    palabra «entre»: sus valores son todos techos y ninguno es un piso
    (NOR-HID-04), y ese es el error concreto que esta funcion existe para no
    cometer.
    """
    if isinstance(rango, IntervaloAdmisible):
        return (f"debe estar entre {_num(rango.minimo)} y "
                f"{_num(rango.maximo)} {rango.unidad}")
    if isinstance(rango, TechoUnico):
        return f"no debe pasar de {_num(rango.maximo)} {rango.unidad}"
    if isinstance(rango, PisoUnico):
        return f"no debe bajar de {_num(rango.minimo)} {rango.unidad}"
    if isinstance(rango, ConjuntoDeMaximos):
        valores = " y ".join(_num(v) for v in rango.valores)
        return (f"la fuente escribe {valores} {rango.unidad}, y son TODOS "
                f"MAXIMOS: ninguno es un minimo. El valor no debe pasar del "
                f"mayor de ellos ({_num(max(rango.valores))} {rango.unidad})")
    if isinstance(rango, BandaDeInterpolacion):
        pares = ", ".join(f"({_num(a)} {rango.unidad_abscisa} -> {_num(b)} "
                          f"{rango.unidad})" for a, b in rango.puntos)
        return (f"la fuente manda INTERPOLAR linealmente entre {pares}: los "
                "extremos no acotan el valor, lo definen por tramos")
    raise TypeError(
        f"{type(rango).__name__} no es un rango normativo del registro: la "
        "frase de un rango se compone desde su tipo, nunca de dos numeros "
        "sueltos")


def rango_normativo_mostrado(rango: Any) -> RangoMostrado:
    """El rango del registro, listo para pintar, con su rotulo obligatorio."""
    return RangoMostrado(
        clase="normativo",
        rotulo=rango.rotulo_obligatorio,
        frase=frase_del_rango(rango),
        unidad=rango.unidad,
        cita=_linea_de_cita(rango.cita_id),
        que_pasa_fuera=_QUE_PASA_FUERA[rango.que_pasa_fuera])


def dominio_mostrado(nombre: Optional[str]) -> Optional[RangoMostrado]:
    """
    El limite de `dominios.py` que acota la celda, por NOMBRE y con su valor.

    Se rotula con `ROTULOS_DE_RANGO['dominio_fisico']`, que dice lo unico que
    hay que decir: no es normativo. Un dominio pintado como si fuera norma es
    una cita inventada barata.
    """
    if not nombre:
        return None
    limite = getattr(_dominios, nombre)
    return RangoMostrado(
        clase="dominio_fisico",
        rotulo=ROTULOS_DE_RANGO["dominio_fisico"],
        frase=f"dominios.{nombre} = {_num(limite)}",
        que_pasa_fuera=_QUE_PASA_FUERA[QuePasaFuera.SALE_DEL_DOMINIO])


def sensibilidad_mostrada(sensibilidad: Any) -> Optional[RangoMostrado]:
    """
    El `sensibilidad` del criterio. NO es un rango normativo y no se pinta
    como tal: es lo que el proyectista movio para defender su adopcion.
    """
    if not sensibilidad:
        return None
    if isinstance(sensibilidad, (tuple, list)):
        frase = " · ".join(str(s) for s in sensibilidad)
    else:
        frase = str(sensibilidad)
    return RangoMostrado(
        clase="sensibilidad",
        rotulo=ROTULOS_DE_RANGO["sensibilidad"],
        frase=frase,
        que_pasa_fuera=_QUE_PASA_FUERA[QuePasaFuera.DEJA_DE_SER_DEFENDIBLE])


# ===========================================================================
# La cita: numeral · nombre completo de la norma · edicion · pagina impresa
# ===========================================================================

def _linea_de_cita(cita_id: str) -> str:
    """
    La linea de cabecera que el plan pide, en ese orden exacto.

    La compone ESTA funcion y no un campo del registro, por la misma razon
    que `Cita.como_texto`: el « · » que une los trozos es del proyecto, y
    buscar la linea compuesta en el PDF no la encontraria. Lo que si esta en
    el PDF es cada trozo por separado.
    """
    reg = _registro.construir()
    cita = reg.cita(cita_id)
    fuente = reg.fuente(cita.fuente_id)
    trozos = [f"num. {cita.numeral}", fuente.titulo, fuente.emisor,
              f"ed. {fuente.edicion} ({fuente.anio})",
              f"pag. impresa {cita.pagina_impresa}"]
    if not esta_por_transcribir(cita.pagina_pdf):
        trozos.append(f"PDF {cita.pagina_pdf}")
    if cita.verificado is None:
        trozos.append("[cita NO verificada contra el PDF]")
    return " · ".join(trozos)


@dataclass(frozen=True)
class CitaMostrada:
    """La cita desmontada, para que la ventana la pinte en varias lineas."""
    id: str
    linea: str
    numeral: str
    titulo_numeral: str
    jerarquia: Tuple[str, ...]
    norma: str
    emisor: str
    edicion: str
    pagina_impresa: str
    caracter: str
    texto_literal: str
    verificada: bool
    interpretacion: Optional[str] = None


def cita_mostrada(cita_id: str) -> CitaMostrada:
    """La cita del registro, con lo pendiente de transcribir dicho como tal."""
    reg = _registro.construir()
    c = reg.cita(cita_id)
    f = reg.fuente(c.fuente_id)
    pendiente = "(pendiente de transcribir del PDF)"
    return CitaMostrada(
        id=c.id,
        linea=_linea_de_cita(cita_id),
        numeral=c.numeral,
        titulo_numeral=(pendiente if esta_por_transcribir(c.titulo_numeral)
                        else c.titulo_numeral),
        jerarquia=c.jerarquia_numeral,
        norma=f.titulo,
        emisor=f.emisor,
        edicion=f"{f.edicion} ({f.anio})",
        pagina_impresa=c.pagina_impresa,
        caracter=c.caracter.value,
        texto_literal=(pendiente if esta_por_transcribir(c.texto_literal)
                       else c.texto_literal.texto),
        verificada=c.verificado is not None,
        interpretacion=(c.interpretacion.texto if c.interpretacion else None))


# ===========================================================================
# La cara TABLA
# ===========================================================================

def texto_de_celda(celda: Celda) -> str:
    """
    Una celda como la ventana la escribe.

    Un `RangoNormativo` dentro de una celda se escribe con su frase, no con
    sus numeros sueltos: es la misma regla de la Sec. 4.2 aplicada dentro de
    la tabla. Un `CeldaSinValor` se escribe con su marca Y su significado,
    porque `"*"` a secas no le dice nada a quien lee la ventana.
    """
    if isinstance(celda, CeldaSinValor):
        return f"{celda.value}  ({_SIGNIFICADO_SIN_VALOR[celda]})"
    if isinstance(celda, (IntervaloAdmisible, TechoUnico, PisoUnico,
                          ConjuntoDeMaximos, BandaDeInterpolacion)):
        return frase_del_rango(celda)
    if isinstance(celda, bool):
        return str(celda)
    if isinstance(celda, (int, float)):
        return _num(celda)
    return str(celda)


_SIGNIFICADO_SIN_VALOR: Dict[CeldaSinValor, str] = {
    CeldaSinValor.EXIGE_ESTUDIO: "la fuente exige un estudio especifico",
    CeldaSinValor.NO_APLICA: "la fuente dice que no aplica",
    CeldaSinValor.NO_PARTICIPA: "no participa en esta combinacion",
    CeldaSinValor.NO_IMPRESO: "la celda esta vacia en el impreso",
    CeldaSinValor.REMITE_A_OTRA_TABLA: "remite a otra tabla",
}


@dataclass(frozen=True)
class ColumnaMostrada:
    """
    Una columna de la tabla. `atenuada` es la que el calculo NO usa: se pinta,
    apagada, con la razon al lado.

    Se pinta y no se esconde porque una tabla podada no es la tabla: el
    revisor tiene que ver lo que la fuente imprime y, aparte, que parte de eso
    entra en este calculo. `motivo` contesta la pregunta que nace al verla
    apagada, y sale de `NoUsada.por_que_no`, que el registro exige no vacio.
    """
    id: str
    etiqueta_literal: str
    unidad: str
    atenuada: bool
    motivo: str
    disponibilidad: Optional[Disponibilidad] = None
    usada_por: Tuple[str, ...] = ()


@dataclass(frozen=True)
class FilaMostrada:
    """Una fila con sus celdas ya escritas, su condicion y sus llamadas a nota."""
    id: str
    clave_corta: str
    etiqueta_literal: str
    jerarquia: Tuple[str, ...]
    etiqueta_legible: str
    celdas: Dict[str, str]
    atenuada: bool
    motivo: str
    disponibilidad: Disponibilidad
    condiciones: Tuple[str, ...] = ()
    llamadas_a_nota: Tuple[str, ...] = ()
    elegible: bool = True


@dataclass(frozen=True)
class ModificadorMostrado:
    """
    Un modificador, con SU CITA -- que no es la de la tabla -- y con el orden
    de aplicacion, que es el campo que puede invertir que norma gobierna.
    """
    id: str
    concepto: str
    texto_literal: str
    sobre_que: str
    orden: str
    cita: str
    tramos: Tuple[Tuple[str, str, Disponibilidad], ...]
    piso: str = ""
    tope: str = ""
    lagunas: Tuple[str, ...] = ()


@dataclass(frozen=True)
class NotaMostrada:
    marca: str
    texto: str


# El orden visual que pide la Sec. 4.2/4.3 del plan, escrito como DATO para
# que un test lo compruebe. Una ventana que pinte la tabla antes que su
# numeral, o las notas al pie despues de la cita, es otra ventana.
ORDEN_VISUAL_TABLA: Tuple[str, ...] = (
    "titulo_literal",
    "linea_de_cita",
    "tabla_completa",
    "condiciones_de_fila",
    "notas_al_pie",
    "modificadores",
    "cita_textual",
)


@dataclass(frozen=True)
class ContenidoDeTabla:
    """
    Todo lo que la cara TABLA muestra, en el orden en que lo muestra.

    `titulo_literal` viene del registro TAL CUAL, con las unidades que la
    fuente imprime. Es NOR-HID-06: el titulo de la Tabla N 10 se citaba sin
    «(m/s)», y esa unidad es lo unico que decide que los dos numeros de la
    fila sean maximos y no un intervalo.
    """
    tabla_id: str
    titulo_literal: str
    linea_de_cita: str
    cita: CitaMostrada
    rotulo_de_completitud: str
    alcance: str
    encabezados_superiores: Tuple[str, ...]
    columnas: Tuple[ColumnaMostrada, ...]
    filas: Tuple[FilaMostrada, ...]
    notas_al_pie: Tuple[NotaMostrada, ...]
    modificadores: Tuple[ModificadorMostrado, ...]
    cita_textual: str
    texto_previo: str = ""
    fuente_declarada_por_la_tabla: str = ""
    lagunas: Tuple[str, ...] = ()
    erratas: Tuple[str, ...] = ()
    afirmaciones_negativas: Tuple[str, ...] = ()
    interpretacion_del_proyectista: str = ""
    orden_visual: Tuple[str, ...] = ORDEN_VISUAL_TABLA

    @property
    def filas_elegibles(self) -> Tuple[FilaMostrada, ...]:
        return tuple(f for f in self.filas if f.elegible)

    def fila_por_clave(self, clave: str) -> FilaMostrada:
        """
        Una fila por su id completo o por su clave corta.

        Las dos formas, porque el registro usa las dos: el id lleva el prefijo
        de la tabla (`MC_HHD.T10#concreto`) y quien lee la ventana --- y quien
        escribe un test --- piensa en «concreto».
        """
        for f in self.filas:
            if clave in (f.id, f.clave_corta):
                return f
        raise KeyError(f"{self.tabla_id}: no hay fila «{clave}»")

    def columna_por_id(self, id_columna: str) -> ColumnaMostrada:
        for c in self.columnas:
            if c.id == id_columna:
                return c
        raise KeyError(f"{self.tabla_id}: no hay columna «{id_columna}»")


# LA ELECCION NO ES UN DATO QUE FALTE, y sin esta distincion la ventana de
# `categoria_refuerzo_aashto` seria inutilizable: sus tres columnas cuelgan de
# la condicion COND-CATEGORIA-REFUERZO, que se resuelve con ese MISMO
# criterio. Pintadas como «falta declarar categoria_refuerzo_aashto» dentro de
# la ventana que existe para declararlo, el usuario leeria que hay que
# declararlo en otro sitio -- y no hay otro sitio.
#
# La regla, escrita para que no se lea como una excepcion comoda: una
# condicion que se resuelve con la CLAVE QUE ESTA VENTANA DECLARA no es un
# dato ausente, es la eleccion misma. Cualquier otra clave que falte sigue
# siendo R4 y sigue bloqueando o pidiendo.
_ELECCION_DE_ESTA_VENTANA = ("esta condicion se resuelve con la clave que "
                             "esta ventana declara: no es un dato que falte, "
                             "es la eleccion que se esta haciendo")


def _resuelta_por_la_propia_ventana(disponibilidad: Disponibilidad,
                                    clave: str) -> Disponibilidad:
    if isinstance(disponibilidad, PideDato) and \
            disponibilidad.clave_que_falta == clave:
        return Elegible(resuelta_por=_ELECCION_DE_ESTA_VENTANA)
    return disponibilidad


def _uso_a_disponibilidad(uso: Any,
                          clave: str = "") -> Tuple[bool, str,
                                                    Optional[Disponibilidad]]:
    """(atenuada, motivo, disponibilidad) de un `UsoEnCalculo`."""
    if isinstance(uso, Usada):
        return (False, f"la usa {', '.join(uso.por)}", None)
    if isinstance(uso, NoUsada):
        return (True, uso.por_que_no, None)
    if isinstance(uso, PendienteDeCondicion):
        reg = _registro.construir()
        condicion = reg.condicion(uso.condicion_id)
        if condicion is None:
            raise KeyError(
                f"la condicion '{uso.condicion_id}' no existe en el registro")
        disponibilidad = _resuelta_por_la_propia_ventana(
            disponibilidad_de(condicion), clave)
        atenuada = not isinstance(disponibilidad, Elegible)
        return (atenuada, condicion.texto.texto, disponibilidad)
    raise TypeError(f"uso no contemplado: {type(uso).__name__}")


def _texto_de_laguna(laguna: Laguna) -> str:
    quien = (f" Lo cierra: {laguna.quien_lo_cierra}."
             if laguna.quien_lo_cierra else "")
    return (f"LA FUENTE NO CUBRE: {laguna.que_no_cubre}. Se cierra con "
            f"{laguna.con_que_regla}.{quien} Si nadie lo cierra: "
            f"{laguna.si_nadie_lo_cierra.value}.")


def _texto_de_afirmacion(a: AfirmacionNegativa) -> str:
    return f"{a.que_no_dice} (barrido: {a.ambito_barrido})"


def _texto_de_interpretacion(i: Interpretacion) -> str:
    partes = [f"INTERPRETACION DEL PROYECTISTA, no de la fuente: {i.texto}"]
    if i.en_contra:
        partes.append("En contra: " + " · ".join(i.en_contra))
    if i.a_favor:
        partes.append("A favor: " + " · ".join(i.a_favor))
    return " || ".join(partes)


def contenido_de_tabla(tabla_id: str,
                       clave_que_se_declara: str = "") -> ContenidoDeTabla:
    """
    Arma el contenido de la cara TABLA leyendo SOLO el registro.

    Todo lo que la Sec. 4.2/4.3 pide sale de un campo del registro y de
    ninguna otra parte: el titulo con sus unidades, el numeral con la pagina
    impresa, TODAS las columnas y TODAS las filas -- las que el calculo no usa
    atenuadas, con la razon --, la condicion de cada fila, las notas al pie
    integras, los modificadores con su propia cita y el parrafo que sostiene
    la tabla.
    """
    reg = _registro.construir()
    t = reg.tabla(tabla_id)
    cita = cita_mostrada(t.cita_id)

    columnas = []
    for c in t.columnas:
        atenuada, motivo, disp = _uso_a_disponibilidad(
            c.uso, clave_que_se_declara)
        columnas.append(ColumnaMostrada(
            id=c.id, etiqueta_literal=c.etiqueta_literal, unidad=c.unidad,
            atenuada=atenuada, motivo=motivo, disponibilidad=disp,
            usada_por=c.uso.por if isinstance(c.uso, Usada) else ()))

    filas = []
    for f in t.filas:
        atenuada, motivo, disp = _uso_a_disponibilidad(
            f.uso, clave_que_se_declara)
        if disp is None:
            disp = Elegible()
        # Las condiciones propias de la fila se suman a la del `uso`: una
        # fila puede colgar de dos (la de MS.C41 cuelga de la clase de via Y
        # del numero de carriles) y quedarse con la primera perderia la otra.
        propias = tuple(_resuelta_por_la_propia_ventana(
            disponibilidad_de(c), clave_que_se_declara) for c in f.condiciones)
        bloqueantes = [d for d in (disp, *propias)
                       if not isinstance(d, Elegible)]
        if bloqueantes:
            disp = bloqueantes[0]
            atenuada = True
        filas.append(FilaMostrada(
            id=f.id, clave_corta=t.clave_corta(f),
            etiqueta_literal=f.etiqueta_literal, jerarquia=f.jerarquia,
            etiqueta_legible=f.legible(),
            celdas={col.id: texto_de_celda(f.valores[col.id])
                    for col in t.columnas if col.id in f.valores},
            atenuada=atenuada, motivo=motivo, disponibilidad=disp,
            condiciones=tuple(c.texto.texto for c in f.condiciones),
            llamadas_a_nota=f.llamadas_a_nota,
            elegible=isinstance(disp, Elegible)))

    modificadores = []
    for m in t.modificadores:
        modificadores.append(ModificadorMostrado(
            id=m.id, concepto=m.concepto, texto_literal=m.texto.texto,
            sobre_que=m.sobre_que, orden=m.orden.value,
            cita=_linea_de_cita(m.cita_id),
            tramos=tuple((tr.etiqueta_literal, _num(tr.factor),
                          disponibilidad_de(tr.condicion))
                         for tr in m.tramos),
            piso=(f"{_num(m.piso[0])} · {_linea_de_cita(m.piso[1])}"
                  if m.piso else ""),
            tope=(f"{_num(m.tope[0])} · {_linea_de_cita(m.tope[1])}"
                  if m.tope else ""),
            lagunas=tuple(_texto_de_laguna(l) for l in m.lagunas)))

    alcance = ("transcripcion INTEGRA de la tabla impresa"
               if not isinstance(t.alcance, Acotada) else
               f"TRANSCRIPCION ACOTADA: {t.alcance.razon}. Queda fuera: "
               f"{t.alcance.que_queda_fuera}. Donde leerlo: "
               f"{t.alcance.donde_leerlo}")

    return ContenidoDeTabla(
        tabla_id=t.id,
        titulo_literal=t.titulo_literal,
        linea_de_cita=cita.linea,
        cita=cita,
        rotulo_de_completitud=t.rotulo_de_completitud(),
        alcance=alcance,
        encabezados_superiores=t.encabezados_superiores,
        columnas=tuple(columnas),
        filas=tuple(filas),
        notas_al_pie=tuple(NotaMostrada(marca=n.marca, texto=n.texto.texto)
                           for n in t.notas_al_pie),
        modificadores=tuple(modificadores),
        cita_textual=cita.texto_literal,
        texto_previo=t.texto_previo.texto if t.texto_previo else "",
        fuente_declarada_por_la_tabla=t.fuente_declarada_por_la_tabla,
        lagunas=tuple(_texto_de_laguna(l) for l in t.lagunas),
        erratas=tuple(_texto_de_errata(e) for e in t.erratas),
        afirmaciones_negativas=tuple(_texto_de_afirmacion(a)
                                     for a in t.afirmaciones_negativas),
        interpretacion_del_proyectista=(
            _texto_de_interpretacion(t.interpretacion)
            if t.interpretacion else ""))


def _texto_de_errata(discrepancia_id: str) -> str:
    """
    La errata de una tabla, con QUIEN GANA y que pasa si se sigue a la otra
    parte. Las tres cosas que `CLAUDE.md` obliga a decir cuando dos fuentes
    dicen cosas distintas, dichas en la ventana y no solo en un comentario.
    """
    d = _registro.construir().discrepancia(discrepancia_id)
    partes = " · ".join(f"{p.quien}: {p.que_dice}" for p in d.partes)
    return (f"{d.id} [{d.estado.value}] sobre {d.objeto}. {partes}. GANA "
            f"{d.gana}: {d.por_que}. Si se sigue la otra: "
            f"{d.efecto_si_se_sigue_la_otra}")


# ===========================================================================
# La cara RANGO
# ===========================================================================

@dataclass(frozen=True)
class ContenidoDeRango:
    """
    Campo numerico + el rango + LA SEMANTICA + la cita + la unidad + que
    significa salirse. Los tres rangos de la Sec. 4.2 van en tres campos.

    `semantica` es el NOMBRE DEL TIPO del rango del registro. No es adorno:
    es lo que le dice al lector que «3.0 y 6.0» no es «de 3.0 a 6.0».
    """
    clave: str
    que_acota: str
    semantica: str
    rango_normativo: RangoMostrado
    tabla_id: str
    fila_id: str
    columna_id: str
    titulo_de_la_tabla: str
    fila_legible: str
    dominio_fisico: Optional[RangoMostrado] = None
    rango_de_sensibilidad: Optional[RangoMostrado] = None
    interpretacion_del_proyectista: str = ""


def contenido_de_rango(clave: str) -> ContenidoDeRango:
    """El contenido de la cara RANGO, leyendo el rango del registro por tipo."""
    v = _ve.variable(clave)
    r = v.resolucion
    if not isinstance(r, EnRango):
        raise ValueError(
            f"'{clave}' se resuelve `{v.modo.value}`, no `en_rango`")
    reg = _registro.construir()
    tabla = reg.tabla(r.tabla_id)
    fila = tabla.fila(r.fila_id)
    rango = fila.valores[r.columna_id]
    sensibilidad = (_ca.criterio(clave).sensibilidad
                    if clave in _ca.CRITERIOS else None)
    return ContenidoDeRango(
        clave=clave,
        que_acota=r.que_acota,
        semantica=type(rango).__name__,
        rango_normativo=rango_normativo_mostrado(rango),
        tabla_id=tabla.id,
        fila_id=fila.id,
        columna_id=r.columna_id,
        titulo_de_la_tabla=tabla.titulo_literal,
        fila_legible=fila.legible(),
        dominio_fisico=dominio_mostrado(v.dominio),
        rango_de_sensibilidad=sensibilidad_mostrada(sensibilidad),
        interpretacion_del_proyectista=(
            _texto_de_interpretacion(tabla.interpretacion)
            if tabla.interpretacion else ""))


# ===========================================================================
# La cara CATALOGO
# ===========================================================================

@dataclass(frozen=True)
class ContenidoDeCatalogo:
    """
    Un catalogo de proveedor. SIN numeral y SIN cita, y diciendolo.

    `que_norma_NO_lo_sostiene` es obligatorio en el `Catalogo` del registro y
    se pinta arriba del todo: es el campo entero del tipo. NOR-PRO-01 y
    NOR-PRO-02 nacieron de topes de catalogo impresos como si fueran normas de
    producto que, ademas, tabulan hasta 3600 mm.
    """
    catalogo_id: str
    titulo: str
    proveedor_o_ambito: str
    que_norma_NO_lo_sostiene: str
    advertencia: str
    que_elige: str
    sin_numeral: str = ("Este valor NO tiene numeral y no puede sostener una "
                        "cita: un catalogo no es una fuente normativa.")


def contenido_de_catalogo(clave: str) -> ContenidoDeCatalogo:
    v = _ve.variable(clave)
    r = v.resolucion
    if not isinstance(r, DeCatalogo):
        raise ValueError(
            f"'{clave}' se resuelve `{v.modo.value}`, no `de_catalogo`")
    reg = _registro.construir()
    catalogo = next((c for c in reg.catalogos
                     if isinstance(c, Catalogo) and c.id == r.catalogo_id), None)
    if catalogo is None:
        raise KeyError(f"no hay catalogo «{r.catalogo_id}» en el registro")
    return ContenidoDeCatalogo(
        catalogo_id=catalogo.id, titulo=catalogo.titulo,
        proveedor_o_ambito=catalogo.proveedor_o_ambito,
        que_norma_NO_lo_sostiene=catalogo.que_norma_NO_lo_sostiene,
        advertencia=r.advertencia, que_elige=r.que_elige)


# ===========================================================================
# La cara CAMPO
# ===========================================================================

@dataclass(frozen=True)
class ContenidoDeCampo:
    """
    El campo de los tres modos que no muestran tabla ni rango de fuente.

    Los tres comparten cuerpo y NO comparten rotulo, y por eso `que_pide`
    existe: un `libre` pide un numero dentro de su dominio, un `de_ensayo`
    pide el numero Y la trazabilidad, y un `derivada` no pide nada porque no
    se edita.
    """
    clave: str
    editable: bool
    que_pide: str
    que_lo_fija: str = ""
    opciones: Tuple[str, ...] = ()
    dominio_fisico: Optional[RangoMostrado] = None
    rango_de_sensibilidad: Optional[RangoMostrado] = None
    trazabilidad_exigida: str = ""
    ensayo: str = ""
    se_deriva_de: Tuple[str, ...] = ()
    regla_de_derivacion: str = ""
    tabla_pendiente: str = ""


def contenido_de_campo(clave: str) -> ContenidoDeCampo:
    v = _ve.variable(clave)
    r = v.resolucion
    sensibilidad = (_ca.criterio(clave).sensibilidad
                    if clave in _ca.CRITERIOS else None)
    comun = dict(clave=clave,
                 dominio_fisico=dominio_mostrado(v.dominio),
                 rango_de_sensibilidad=sensibilidad_mostrada(sensibilidad))

    if isinstance(r, Libre):
        return ContenidoDeCampo(
            editable=True,
            que_pide=("un valor dentro de su dominio fisico. Ninguna tabla, "
                      "ningun rango de fuente y ninguna medicion lo "
                      "determinan: el numero lo pone quien firma"),
            que_lo_fija=r.que_lo_fija, opciones=r.opciones,
            tabla_pendiente=r.tabla_pendiente, **comun)
    if isinstance(r, DeEnsayo):
        return ContenidoDeCampo(
            editable=True,
            que_pide=("el valor Y SU TRAZABILIDAD. Un dato de sitio no se "
                      "defiende con un rango de sensibilidad -- no hay rango "
                      "que elegir --: se defiende diciendo donde se leyo, "
                      "para que el revisor repita la lectura"),
            ensayo=r.ensayo, trazabilidad_exigida=r.trazabilidad_exigida,
            **comun)
    if isinstance(r, Derivada):
        return ContenidoDeCampo(
            editable=False,
            que_pide=("nada: lo calcula el programa desde otras variables ya "
                      "declaradas y no se edita"),
            se_deriva_de=r.de, regla_de_derivacion=r.regla, **comun)
    raise ValueError(
        f"'{clave}' se resuelve `{v.modo.value}`, que no se pinta con la cara "
        "CAMPO")


# ===========================================================================
# La ventana: la carcasa comun mas la cara que toque
# ===========================================================================

# Solo un CRITERIO se declara desde la ventana, y conviene decir por que las
# otras dos poblaciones no:
#
#   una COLUMNA DEL CSV es un dato por punto: su sitio es el CSV, y declararla
#   aqui pondria el mismo numero en los 40 cruces;
#   un DATO DE SITIO es un hecho determinado por un procedimiento, y
#   `datos_sitio.py` NO TIENE API DE ESCRITURA a proposito -- el unico camino
#   es construir el `DatoSitio`, con su trazabilidad, en el archivo.
#
# En los dos casos la ventana MUESTRA todo y no deja declarar, diciendo de
# donde tiene que venir el valor. Es la misma regla R4 aplicada a la variable
# entera en vez de a una fila.
_POBLACION_DECLARABLE = Poblacion.CRITERIO

_POR_QUE_NO_DECLARABLE: Dict[Poblacion, str] = {
    Poblacion.COLUMNA_CSV:
        "es una columna del CSV de la Sec. 1.2: vale para UN punto critico y "
        "se llena en el CSV, no aqui. Declararla en la ventana pondria el "
        "mismo numero en todos los cruces",
    Poblacion.DATO_SITIO:
        "es un dato de sitio [S]: un hecho determinado por un procedimiento "
        "sobre las coordenadas de esta obra. Se escribe en datos_sitio.py con "
        "su procedimiento y su trazabilidad; el archivo no tiene API de "
        "escritura y esta ventana no la inventa",
}


@dataclass(frozen=True)
class Ventana:
    """
    La ventana emergente de una variable: carcasa comun + una sola cara.

    Exactamente uno de `tabla` / `rango` / `catalogo` / `campo` viene lleno, y
    `cara` dice cual. Es la misma disciplina que el resto del proyecto: la
    semantica es el tipo, no un campo de texto que alguien pueda escribir mal.
    """
    clave: str
    concepto: str
    unidad: str
    poblacion: str
    modo: str
    cara: Cara
    fase: str
    etiqueta: str
    valor_efectivo: Any
    declarada_en_caliente: bool
    declarable_aqui: bool
    por_que_no_declarable: str
    consumido_por: Tuple[str, ...] = ()
    criterio_destino: Optional[str] = None
    justificacion: str = ""
    fuente: str = ""
    nota: str = ""
    tabla: Optional[ContenidoDeTabla] = None
    tablas: Tuple[ContenidoDeTabla, ...] = ()
    rango: Optional[ContenidoDeRango] = None
    catalogo: Optional[ContenidoDeCatalogo] = None
    campo: Optional[ContenidoDeCampo] = None
    que_elige: str = ""
    laguna: str = ""
    elegido_por: Optional[str] = None
    fila_declarada: Optional[str] = None
    columna_declarada: Optional[str] = None

    @property
    def cuerpo(self) -> Any:
        """El unico contenido lleno. Falla si la ventana quedo sin cuerpo."""
        cuerpos = {Cara.TABLA: self.tabla, Cara.RANGO: self.rango,
                   Cara.CATALOGO: self.catalogo, Cara.CAMPO: self.campo}
        cuerpo = cuerpos[self.cara]
        if cuerpo is None:
            raise ValueError(
                f"la ventana de '{self.clave}' declara cara {self.cara.value} "
                "y no trae cuerpo")
        return cuerpo


def _datos_de_la_variable(v: VariableDeEntrada) -> Tuple[Any, bool, str, str, str]:
    """(valor efectivo, declarada en caliente, etiqueta, justificacion, fuente)."""
    if v.poblacion is Poblacion.CRITERIO:
        c = _ca.criterio_efectivo(v.clave)
        return (c.valor, _ca.declarado_en_caliente(v.clave), c.etiqueta,
                c.justificacion, c.fuente)
    if v.poblacion is Poblacion.DATO_SITIO:
        d = _ds.dato(v.clave)
        return (d.valor, False, d.etiqueta, d.procedimiento, d.fuente)
    return (None, False, "", "", "")


def ventana(clave: str) -> Ventana:
    """
    LA funcion del modulo: el contenido completo de la ventana de una variable.

    No toca el registro mas que para leer, no declara nada y no elige nada.
    Declarar es otra cosa y vive en `declaracion.py`, que es el unico camino
    y pasa por `criterios_adoptados.establecer_valor_dinamico`.
    """
    v = _ve.variable(clave)
    cara = cara_de(v.modo)
    valor, en_caliente, etiqueta, justificacion, fuente = _datos_de_la_variable(v)
    declarable = v.poblacion is _POBLACION_DECLARABLE

    comun = dict(
        clave=v.clave, concepto=v.concepto, unidad=v.unidad,
        poblacion=v.poblacion.value, modo=v.modo.value, cara=cara,
        fase=v.fase, etiqueta=etiqueta, valor_efectivo=valor,
        declarada_en_caliente=en_caliente, declarable_aqui=declarable,
        por_que_no_declarable=("" if declarable
                               else _POR_QUE_NO_DECLARABLE[v.poblacion]),
        consumido_por=v.consumido_por, criterio_destino=v.criterio_destino,
        justificacion=justificacion, fuente=fuente, nota=v.nota)

    r = v.resolucion
    if isinstance(r, DeTabla):
        tablas = tuple(contenido_de_tabla(t, clave) for t in r.tablas)
        return Ventana(tabla=tablas[0], tablas=tablas, que_elige=r.que_elige,
                       laguna=r.laguna, elegido_por=r.elegido_por,
                       fila_declarada=r.fila_id, columna_declarada=r.columna_id,
                       **comun)
    if isinstance(r, EnRango):
        return Ventana(rango=contenido_de_rango(clave),
                       que_elige=r.que_acota, **comun)
    if isinstance(r, DeCatalogo):
        return Ventana(catalogo=contenido_de_catalogo(clave),
                       que_elige=r.que_elige, **comun)
    return Ventana(campo=contenido_de_campo(clave), **comun)


# ===========================================================================
# Los cinco casos que la regla R4 nombra, censados
# ===========================================================================
# El plan identifica cinco casos de «la fila depende de un dato que el
# proyecto no tiene». TRES estan en el registro como `CondicionAplicacion` y
# los resuelve la maquinaria de arriba, fila a fila. LOS OTROS DOS NO, y
# declararlo es la unica forma honesta de decirlo: una ventana que los
# mostrara tendria que inventarse la condicion, que es exactamente lo que este
# proyecto viene retirando.
#
# El censo existe como DATO y no como prosa por la misma razon que
# `variables_entrada.DESVIACIONES_DEL_PLAN`: un pendiente que solo vive en un
# comentario no se puede enumerar ni comprobar en un test.


@dataclass(frozen=True)
class CasoR4:
    """
    Un caso de la regla R4, con su estado real frente a la ventana.

    `condicion_id` vacio significa que el registro NO declara la condicion, y
    entonces `que_lo_traeria_a_la_ventana` es obligatorio.
    """
    hallazgo: str
    de_que_depende: str
    condicion_id: str
    donde_vive_hoy: str
    que_lo_traeria_a_la_ventana: str = ""

    @property
    def cubierto_por_la_ventana(self) -> bool:
        return bool(self.condicion_id)

    def __post_init__(self) -> None:
        if not self.condicion_id and not self.que_lo_traeria_a_la_ventana:
            raise ValueError(
                f"CasoR4 {self.hallazgo}: sin condicion en el registro hay que "
                "decir que lo traeria a la ventana")


CASOS_R4: Tuple[CasoR4, ...] = (
    CasoR4(hallazgo="NOR-SUE-01",
           de_que_depende="carriles por sentido",
           condicion_id="COND-CARRILES-POR-SENTIDO",
           donde_vive_hoy="tabla MS.C41 del registro: dos filas y tres "
                          "columnas cuelgan de la condicion, y el dato de "
                          "sitio 'carriles_por_sentido' esta declarado SIN "
                          "valor. La ventana BLOQUEA: un dato de sitio no se "
                          "declara desde aqui"),
    CasoR4(hallazgo="NOR-AAS-01",
           de_que_depende="categoria de acero de refuerzo (columna A/B/C)",
           condicion_id="COND-CATEGORIA-REFUERZO",
           donde_vive_hoy="tabla AASHTO_LRFD_9.T5.10.1-1 del registro: las "
                          "tres columnas de categoria y dos filas cuelgan de "
                          "la condicion, que se resuelve con el criterio "
                          "'categoria_refuerzo_aashto'. La ventana PIDE: es "
                          "un criterio y se declara desde aqui. Es el caso "
                          "que INVIERTE que norma gobierna -- con B o C, "
                          "AASHTO baja a 2.0 in y la regla del mayor la gana "
                          "E.060 --, y esa consecuencia esta escrita en la "
                          "sensibilidad del propio criterio, que la ventana "
                          "muestra"),
    CasoR4(hallazgo="NOR-AAS-05",
           de_que_depende="relacion agua/cemento",
           condicion_id="COND-AC-BAJA",
           donde_vive_hoy="modificador MOD-RECUB-AC de la tabla MP.TRECUB: "
                          "sus dos tramos (0.8 y 1.2) cuelgan del criterio "
                          "'exposicion_quimica_ems'. La ventana PIDE, y "
                          "ademas pinta la laguna de la banda intermedia "
                          "0.40 < a/c < 0.50, que el Manual no imprime"),
    CasoR4(hallazgo="NOR-HDS-05",
           de_que_depende="que el barril fluya lleno en la mayor parte de su "
                          "longitud",
           condicion_id="",
           donde_vive_hoy="la cita HDS5_3ED.3.3.3#HO del registro trae el "
                          "texto literal de la condicion, y el enunciado "
                          "completo de las tres vive en "
                          "`constantes_normativas.H_O_CONDICION_TEXTO`. "
                          "NINGUNA VENTANA LA MUESTRA, y no por descuido: h_o "
                          "no es una variable de entrada -- no se elige, la "
                          "calcula M4 punto por punto --, de modo que no hay "
                          "variable cuya ventana abrir. La condicion tampoco "
                          "esta declarada como `CondicionAplicacion`",
           que_lo_traeria_a_la_ventana="declarar las tres condiciones del "
                          "num. 3.3.3 como `CondicionAplicacion` de la cita "
                          "HDS5_3ED.3.3.3#HO (dos `PorExpresion` sobre HW/D y "
                          "una `NoEvaluable` para el barril lleno, que exige "
                          "el procedimiento de barril parcialmente lleno del "
                          "Cap. III del HDS-5) y hacer que la memoria "
                          "sustentada de S18 las imprima con el paso que las "
                          "usa. Es trabajo del cluster C06, que sigue en "
                          "'Cerrado parcial'"),
    CasoR4(hallazgo="NOR-AAS-06",
           de_que_depende="refuerzo transversal minimo del Art. 5.7.2.5",
           condicion_id="",
           donde_vive_hoy="la condicion que habilita la primera expresion de "
                          "beta no esta en el registro: ni como "
                          "`CondicionAplicacion` ni como `Cita`. Beta tampoco "
                          "es una variable de entrada -- es una expresion de "
                          "la verificacion a cortante --, asi que hoy no hay "
                          "ventana que la muestre",
           que_lo_traeria_a_la_ventana="transcribir el Art. 5.7.3.4.2 de "
                          "AASHTO LRFD como `Cita` con su "
                          "`CondicionAplicacion`, y la de refuerzo transversal "
                          "minimo del Art. 5.7.2.5 con ella. Mientras eso no "
                          "exista, la ventana no puede mostrarla sin "
                          "inventarla"),
)


def casos_r4_cubiertos() -> Tuple[CasoR4, ...]:
    return tuple(c for c in CASOS_R4 if c.cubierto_por_la_ventana)


def casos_r4_sin_cubrir() -> Tuple[CasoR4, ...]:
    return tuple(c for c in CASOS_R4 if not c.cubierto_por_la_ventana)
