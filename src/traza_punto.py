"""
traza_punto.py
==============
EL CONTENIDO del detalle «¿De donde sale este numero?» de la pestaña 3 de la
GUI: los `PasoDeMemoria` de un punto, en el orden en que M11 los imprime,
servidos como DATO para que `gui/app.py` solo pinte.

Que es esto, y por que no esta en gui/
--------------------------------------
El mismo reparto que `src/ventana_normativa.py` frente a
`gui/ventana_normativa.py`, y por las mismas dos razones:

1. `gui/` importa `tkinter`, que no esta en toda imagen donde corre la suite.
   Aqui el contenido es un dato: se compara campo a campo, sin ventana y sin
   escritorio (`tests/test_traza_punto.py`).
2. Lo que la GUI cuenta de un paso tiene que ser LO MISMO que la memoria
   imprime. Por eso este modulo no decide que pasos se publican ni en que
   orden: consume la MISMA seleccion que M11 (`traza_clasificacion`,
   `traza_tw`, `traza_hidraulica`, `verificaciones_publicadas`,
   `citas_en_que_descansa`, `sin_fundamento_por_codigo`), extraida de M11 en
   G4 justamente para que hubiera un solo sitio que la escribiera.

EL MISMO CONTRATO QUE M11: este modulo elige textos y orden, y NO HACE
ARITMETICA SOBRE MAGNITUDES. Todos los numeros llegan ya formados en el
`PasoDeMemoria` que el calculo emitio (`Magnitud.texto` los escribe con la
unidad SI en que el paso los guarda); la conversion a unidades de
presentacion, si algun dia hace falta, ocurre aqui y nunca en el calculo. Un
test barre el AST de este archivo con la misma guardia que barre M11
(SIS-A-07: un reporte que recalcula es un segundo motor de calculo sin tests).

Los tres registros, separados (NOR-HID-04)
------------------------------------------
Cada `LineaDeTraza` declara a cual de los tres registros pertenece, y la GUI
los pinta con estilos distintos igual que la memoria HTML los separa con las
clases CSS `.fuente` / `.interpretacion` / texto normal:

    REGISTRO_FUENTE           lo que el documento DICE (citas textuales)
    REGISTRO_INTERPRETACION   lo que el PROYECTO lee (discrepancias, notas)
    REGISTRO_PROYECTO         lo que el proyecto HACE

Pegados, los tres se leen como norma: es exactamente NOR-HID-04.

Las verificaciones sin paso NO se saltan ni se inventan: las censadas en
`normativa.fundamentos.SIN_FUNDAMENTO` (V4b, V5, V6, V8, V9) llegan como
`HuecoDeVerificacion`, con la razon de por que no pueden tener fundamento
normativo hoy y que haria falta para traerlo -- el mismo hueco declarado que
M11 imprime con `_paso_ausente`, nunca una fila en blanco.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, Union

import criterios_adoptados as _ca
from modelos import TipoDeVeredicto
from modulos import M11_reporte as _M11
from normativa import registro as _registro

# Los tres registros tipograficos de la §4.4. Son contenido, no estilo: la
# GUI mapea cada uno a un formato visual distinto y un test comprueba que no
# se fundan.
REGISTRO_FUENTE = "fuente"
REGISTRO_INTERPRETACION = "interpretacion"
REGISTRO_PROYECTO = "proyecto"

# Rotulos del detalle. Se declaran aqui --- no en la GUI --- para que la
# pantalla no pueda decir una cosa distinta de la que este modulo eligio.
ROTULO_POR_QUE = "Por que se hace"
ROTULO_FORMULA = "Formula"
ROTULO_CITA_FORMULA = "Cita de la formula"
ROTULO_SUSTITUCION = "Con que valores"
ROTULO_RESULTADO = "Resultado"
ROTULO_UMBRAL = "Contra que se compara"
ROTULO_CARACTER = "Caracter en la fuente"
ROTULO_APLICACION = "Que hace el proyecto con el"
ROTULO_CRITERIO_UMBRAL = "El umbral pasa por el criterio adoptado"
ROTULO_VEREDICTO = "Veredicto"
ROTULO_FUENTE = "Lo que dice la fuente"
ROTULO_DISCREPANCIA = "Discrepancia declarada que toca este paso"
ROTULO_ELECCION = "Que se eligio, entre que y por que"
ROTULO_NOTA = "Lo que pone el proyecto"

TITULO_HUECO = "sin fundamento normativo declarado"
ROTULO_HUECO_POR_QUE = "Por que no lo tiene"
ROTULO_HUECO_FALTA = "Que haria falta para traerlo"


@dataclass(frozen=True)
class LineaDeTraza:
    """Una linea del detalle: a que registro pertenece, su rotulo y su texto."""

    registro: str
    rotulo: str
    texto: str


@dataclass(frozen=True)
class DetalleDePaso:
    """
    Un `PasoDeMemoria` ya convertido en lineas pintables.

    `paso` viaja para que los tests contrasten el contenido contra el objeto
    emitido; la GUI no lo lee (compara por lineas, no por paso).
    """

    codigo: str
    titulo: str
    lineas: Tuple[LineaDeTraza, ...]
    paso: Any = field(compare=False, default=None)


@dataclass(frozen=True)
class HuecoDeVerificacion:
    """
    El hueco DECLARADO de una verificacion sin `PasoDeMemoria`: la razon
    censada en `SIN_FUNDAMENTO` de por que no puede tener fundamento
    normativo hoy, y que haria falta para traerlo. Nunca una fila en blanco.
    """

    codigo: str
    titulo: str
    lineas: Tuple[LineaDeTraza, ...]
    por_que: str = ""
    que_haria_falta: str = ""


EntradaDeTraza = Union[DetalleDePaso, HuecoDeVerificacion]


@dataclass(frozen=True)
class SeccionDeTraza:
    """Una serie de entradas bajo el MISMO titulo con que M11 las imprime."""

    titulo: str
    entradas: Tuple[EntradaDeTraza, ...]
    aviso: str = ""


@dataclass(frozen=True)
class TrazaDelPunto:
    """El detalle completo de un punto, en el orden de la memoria."""

    id_punto: str
    titulo: str
    secciones: Tuple[SeccionDeTraza, ...]


# ---------------------------------------------------------------------------
# De un PasoDeMemoria a sus lineas
# ---------------------------------------------------------------------------

def _margen_texto(veredicto: Any) -> str:
    """El margen como lo imprime M11: solo si es un float finito."""
    m = veredicto.margen
    if m is None or not isinstance(m, float) or not math.isfinite(m):
        return ""
    return f" - margen {_M11.FMT_3.format(m)} {veredicto.unidad}".rstrip()


def _lineas_del_paso(paso: Any, reg: Any) -> Tuple[LineaDeTraza, ...]:
    """
    Las lineas de un paso, en el orden en que `M11.bloque_paso` las escribe:
    por que, formula, sustitucion, resultado, umbral, veredicto, citas,
    discrepancias, elecciones y nota.
    """
    lineas: List[LineaDeTraza] = []

    # 1. POR QUE, con el verbo del Fundamento tal como lo sostiene el
    # caracter de sus citas (invariante T11 del registro: un fundamento cuyo
    # verbo no este sostenido no se construye, asi que aqui solo se LEE).
    rotulo_por_que = ROTULO_POR_QUE
    if paso.fundamento_id:
        verbo = reg.fundamento(paso.fundamento_id).verbo.value
        rotulo_por_que = f"{ROTULO_POR_QUE} - el fundamento {verbo}"
    lineas.append(LineaDeTraza(REGISTRO_PROYECTO, rotulo_por_que,
                               paso.por_que))

    # 2. Formula, con su cita (numeral + pagina, via `Cita.como_texto`).
    lineas.append(LineaDeTraza(REGISTRO_PROYECTO, ROTULO_FORMULA,
                               paso.formula))
    if paso.formula_cita_id:
        lineas.append(LineaDeTraza(
            REGISTRO_PROYECTO, ROTULO_CITA_FORMULA,
            reg.cita(paso.formula_cita_id).como_texto()))

    # 3. Sustitucion: cada valor con su PROCEDENCIA (etiqueta, criterio o
    # dato de sitio del que sale), que `Magnitud` trae obligatoria.
    if paso.sustitucion:
        lineas.append(LineaDeTraza(
            REGISTRO_PROYECTO, ROTULO_SUSTITUCION,
            "\n".join(f"{m.simbolo} = {m.texto}  [{m.procedencia}]"
                      for m in paso.sustitucion)))

    # 4. Resultado, con su procedencia. `Magnitud.texto` escribe el valor en
    # la unidad SI en que el paso lo guarda.
    r = paso.resultado
    lineas.append(LineaDeTraza(
        REGISTRO_PROYECTO, ROTULO_RESULTADO,
        f"{r.simbolo} = {r.texto}  [{r.procedencia}]"))

    # 5. Umbral: valor, CARACTER en la fuente y aplicacion, separados igual
    # que en M11 --- fundirlos es como se fabrica una exigencia que la norma
    # no escribio (NOR-MEM-01).
    u = paso.umbral
    if u is not None:
        valor = f"{u.valor} {u.unidad}".strip()
        lineas.append(LineaDeTraza(REGISTRO_PROYECTO, ROTULO_UMBRAL,
                                   f"{u.descripcion} = {valor}"))
        lineas.append(LineaDeTraza(REGISTRO_PROYECTO, ROTULO_CARACTER,
                                   u.caracter))
        lineas.append(LineaDeTraza(REGISTRO_PROYECTO, ROTULO_APLICACION,
                                   u.aplicacion))
        if u.criterio_aplicado:
            declarado = _ca.CRITERIOS.get(u.criterio_aplicado)
            etiqueta = (f"[{declarado.etiqueta}] "
                        if declarado is not None else "")
            lineas.append(LineaDeTraza(
                REGISTRO_PROYECTO, ROTULO_CRITERIO_UMBRAL,
                f"{etiqueta}{u.criterio_aplicado}"))

    # 6. Veredicto, con el margen.
    v = paso.veredicto
    if v is not None:
        if v.tipo is TipoDeVeredicto.CUMPLE:
            marca = _M11.MARCA_CUMPLE
        elif v.tipo is TipoDeVeredicto.NO_CUMPLE:
            marca = _M11.MARCA_INCUMPLE
        else:
            marca = v.tipo.value
        texto = marca + _margen_texto(v)
        if v.explicacion:
            texto += f"\n{v.explicacion}"
        lineas.append(LineaDeTraza(REGISTRO_PROYECTO, ROTULO_VEREDICTO,
                                   texto))

    # 7. Lo que dice la FUENTE: las transcripciones literales, cada una con
    # su cita. El texto sale del registro (`Registro.cita`), nunca se
    # transcribe aqui: una segunda transcripcion diverge sin que nada avise.
    for cita_id in paso.citas_textuales:
        c = reg.cita(cita_id)
        literal = getattr(c.texto_literal, "texto", "")
        lineas.append(LineaDeTraza(
            REGISTRO_FUENTE, ROTULO_FUENTE,
            f"«{literal}»  [{c.como_texto()}]"))

    # 8. Las discrepancias que tocan este paso, por la MISMA vista que M11
    # consume: `Registro.discrepancias_que_tocan` sobre las cuatro puertas de
    # `citas_en_que_descansa` mas las declaradas por valor. Es interpretacion
    # del proyecto, no fuente: pegarla a la cita seria NOR-HID-04.
    tocadas = reg.discrepancias_que_tocan(
        _M11.citas_en_que_descansa(paso), getattr(paso, "discrepancias", ()))
    for d in tocadas:
        lineas.append(LineaDeTraza(
            REGISTRO_INTERPRETACION, ROTULO_DISCREPANCIA,
            f"{d.id} - {d.objeto}. Gana {d.gana}."))

    # 9. Las elecciones, con su procedencia (regla R1). `EleccionDeProyecto.
    # texto` compone la frase en modelos.py, una sola vez.
    for e in paso.elecciones:
        texto = e.texto
        if e.cita_id:
            texto += f"  [{reg.cita(e.cita_id).como_texto()}]"
        lineas.append(LineaDeTraza(REGISTRO_PROYECTO, ROTULO_ELECCION, texto))

    # 10. La nota del proyecto: interpretacion, nunca pegada a la fuente.
    if paso.nota_del_proyecto:
        lineas.append(LineaDeTraza(REGISTRO_INTERPRETACION, ROTULO_NOTA,
                                   paso.nota_del_proyecto))

    return tuple(lineas)


def _detalle(paso: Any, reg: Any) -> DetalleDePaso:
    return DetalleDePaso(codigo=paso.codigo, titulo=paso.que,
                         lineas=_lineas_del_paso(paso, reg), paso=paso)


def _hueco(codigo: str, censo: Tuple[str, str]) -> HuecoDeVerificacion:
    por_que, que_haria_falta = censo
    return HuecoDeVerificacion(
        codigo=codigo,
        titulo=TITULO_HUECO,
        lineas=(LineaDeTraza(REGISTRO_PROYECTO, ROTULO_HUECO_POR_QUE,
                             por_que),
                LineaDeTraza(REGISTRO_PROYECTO, ROTULO_HUECO_FALTA,
                             que_haria_falta)),
        por_que=por_que,
        que_haria_falta=que_haria_falta)


# ---------------------------------------------------------------------------
# La traza completa de un punto
# ---------------------------------------------------------------------------

def traza_del_punto(informe_punto: Any) -> TrazaDelPunto:
    """
    El detalle de procedencia de un punto: los pasos que M11 publica para el,
    en el orden en que la memoria los imprime --- clasificacion (Fase 2), TW
    (Sec. 1.3), hidraulica (Fases 3 y 4) y el desarrollo de cada verificacion
    de la Fase 5 ---, con los huecos declarados donde no hay paso.

    La seleccion es LA DE M11, funcion por funcion; aqui solo se convierte en
    lineas. Si una seccion no tiene pasos, no aparece: igual que
    `bloque_pasos` no imprime un encabezado vacio.
    """
    reg = _registro.construir()
    punto = informe_punto.punto
    secciones: List[SeccionDeTraza] = []

    pasos_fase2 = _M11.traza_clasificacion(informe_punto)
    if pasos_fase2:
        secciones.append(SeccionDeTraza(
            _M11.TITULO_TRAZA_CLASIFICACION,
            tuple(_detalle(p, reg) for p in pasos_fase2)))

    paso_tw = _M11.traza_tw(informe_punto)
    if paso_tw is not None:
        secciones.append(SeccionDeTraza(
            _M11.TITULO_TRAZA_TW, (_detalle(paso_tw, reg),)))

    pasos_hidraulicos, ultimo = _M11.traza_hidraulica(informe_punto)
    if pasos_hidraulicos:
        if ultimo is None:
            titulo, aviso = _M11.TITULO_TRAZA_HIDRAULICA, ""
        else:
            # El MISMO aviso de fondo que M11 imprime sobre este desarrollo:
            # no es el de un diseño adoptado, y callarlo seria publicar
            # calculo descartado como si fuera el del punto.
            titulo = _M11.TITULO_TRAZA_HIDRAULICA_ULTIMO
            aviso = (f"Este desarrollo es el del ultimo escalon evaluado "
                     f"({ultimo.material}, {ultimo.seccion.etiqueta()}), no "
                     "el de un diseño adoptado: el punto no se dimensiono. "
                     "Se publica porque es calculo que el pipeline hizo de "
                     "verdad; el motivo del descarte esta en la tabla de "
                     "iteraciones de la memoria.")
        secciones.append(SeccionDeTraza(
            titulo, tuple(_detalle(p, reg) for p in pasos_hidraulicos),
            aviso=aviso))

    # Verificaciones: paso donde lo hay, HUECO DECLARADO donde el censo lo
    # explica, y nada donde M11 tampoco imprime nada --- inventar un texto
    # para una verificacion sin paso ni censo seria peor que el hueco.
    censo = _M11.sin_fundamento_por_codigo()
    entradas: List[EntradaDeTraza] = []
    for _fase, v in _M11.verificaciones_publicadas(informe_punto):
        if v.paso is not None:
            entradas.append(_detalle(v.paso, reg))
        elif v.codigo and v.codigo in censo:
            entradas.append(_hueco(v.codigo, censo[v.codigo]))
    if entradas:
        secciones.append(SeccionDeTraza(
            _M11.TITULO_TRAZA_VERIFICACIONES, tuple(entradas)))

    estado = ("dimensionado" if informe_punto.dimensionado
              else "sin dimensionar")
    titulo = (f"{punto.id} | progresiva {punto.progresiva_display} | "
              f"Familia {punto.familia.value} | {estado}")
    return TrazaDelPunto(id_punto=punto.id, titulo=titulo,
                         secciones=tuple(secciones))
