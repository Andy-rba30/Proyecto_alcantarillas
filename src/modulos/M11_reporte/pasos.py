# -*- coding: utf-8 -*-
"""
M11_reporte.pasos
=================
Submodulo de Fase 11 (`M11_reporte`): bloque `pasos` (D3).
"""

from __future__ import annotations

import contextvars
import hashlib
import math
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
)
from src import criterios_adoptados as ca
from src.modulos.M5_verificaciones import verificaciones_no_evaluadas
from src.modelos import (
    EstadoDeVerificacion,
    TipoDeVeredicto,
)

from src.modulos.M11_reporte._base import (
    CLASE_INDICADOR,
    MARCA_CUMPLE,
    MARCA_INDICADOR,
    MARCA_NO_APLICA,
    _es_indicador,
    _esc,
    _etiqueta_html,
    _marca_de_verificacion,
    _num,
    _reg_M11,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
    sin_fundamento_por_codigo,
)
from src.modulos.M11_reporte.trazas import (
    TITULO_TRAZA_VERIFICACIONES,
    traza_clasificacion,
    verificaciones_publicadas,
)
from src.modulos.M11_reporte.anclas import (
    _cita_como_texto,
    _donde,
    _enlace,
    ancla_de_cita,
    ancla_de_criterio,
    ancla_de_discrepancia,
    ancla_de_fundamento,
    ancla_de_umbral,
)

class _YaImpreso:
    """
    --- T-10 --- Lo que la memoria de los PUNTOS ya imprimio entero en ESTE
    documento, por huella de contenido: pasos completos, elecciones y notas
    del proyecto. La primera aparicion se imprime entera y con un `id`; las
    siguientes, IDENTICAS, se imprimen como una linea con su enlace a la
    primera. Es la deduplicacion que EXT-8 hizo con las citas, los
    fundamentos y los umbrales (al anexo), aplicada a lo que se repetia de
    punto a punto: medido sobre la corrida de la linea base a expediente,
    el paso 2.1 identico en los cuatro puntos, las elecciones de los
    criterios de corredor (pendientes, regimen de V2b, metodo de longitud)
    y las notas del proyecto que no dependen del punto.

    Vive SOLO mientras `memoria_html_por_partes` arma los puntos
    (`_IMPRESOS`, una `ContextVar`): un paso o un punto renderizados sueltos
    --- la traza de la GUI, un test --- salen enteros, sin referencias que no
    tendrian a donde apuntar. No es estado del calculo: es de presentacion,
    y nace y muere con el documento.
    """

    def __init__(self) -> None:
        self.anclas: Dict[str, str] = {}      # huella -> punto donde salio
        self.punto = ""

    def ver(self, prefijo: str, contenido: str) -> Tuple[str, Optional[str]]:
        """(ancla, punto de la primera aparicion o None si es la primera)."""
        huella = hashlib.sha1(contenido.encode("utf-8")).hexdigest()
        ancla = f"{prefijo}-{huella[:12]}"  # literal-ok: largo de la huella corta del ancla
        if ancla in self.anclas:
            return ancla, self.anclas[ancla]
        self.anclas[ancla] = self.punto
        return ancla, None


_IMPRESOS: "contextvars.ContextVar[Optional[_YaImpreso]]" = \
    contextvars.ContextVar("M11_ya_impreso", default=None)


def _citas_del_paso(paso: Any) -> str:
    """
    Las citas del paso: el NUMERAL de cada una en linea y la transcripcion
    UNA vez, en el anexo, por enlace (EXT-8, PC-12).

    Hasta EXT-8 cada paso transcribia entera cada cita que entrecomillaba:
    medido, la frase del umbral de 6.0 m salia 80 veces en 40 puntos. El
    numeral, el titulo y la pagina --- que es lo que la Fase 11 de la hoja de
    ruta exige junto a cada verificacion --- siguen aqui; la frase literal
    esta a un enlace, en `anexo_referencias`, y sigue saliendo del registro.
    """
    if not paso.citas_textuales:
        return ""
    partes = [
        f"<li>{_enlace(ancla_de_cita(cita_id), _esc(_cita_como_texto(cita_id)))}</li>"
        for cita_id in paso.citas_textuales]
    return ('<dt>Lo que dice la fuente</dt><dd><ul class="citas">'
            + "".join(partes) + "</ul>"
            '<span class="procedencia-cita">texto literal en el anexo de '
            "referencias</span></dd>")


def citas_en_que_descansa(paso: Any) -> frozenset:
    """
    TODAS las citas sobre las que un paso descansa, no solo las que entrecomilla.

    UN PASO CARGA NUMERALES POR CUATRO PUERTAS Y EL CANAL LEIA UNA. Es el
    hueco que la auditoria adversarial de C8 encontro, y no es teorico: la
    memoria de C-01 nombra la **Tabla A.1 del HDS-5 cinco veces** --- es de
    donde salen los coeficientes K, M, c, Y y Ks del control de entrada, que
    producen el unico HW que C-01 publica --- y la discrepancia sobre el
    TITULO de esa tabla (`DIS-HDS5-APENDICE-G`: remite a un «Appendix G» que
    la 3.a edicion no tiene) no llegaba. La cita entra al paso por el
    `Fundamento`, y `discrepancias_que_tocan` recibia solo `citas_textuales`.

    Las cuatro puertas, y por que las cuatro cuentan:

        `citas_textuales`   se imprimen entrecomilladas, bajo «Lo que dice la
                            fuente». Es la puerta obvia.
        `formula_cita_id`   se imprime como procedencia de la formula, al lado
                            de la formula misma.
        `umbral.cita_id`    el `__post_init__` de `PasoDeMemoria` ya obliga a
                            que este en `citas_textuales`; se incluye por
                            completitud, no porque anada nada hoy.
        `Fundamento.citas`  son los numerales que sostienen el `por_que`, y el
                            `por_que` SE IMPRIME. Un paso cuyo «por que se
                            hace» descansa en un numeral esta mandando al
                            revisor a ese numeral igual que si lo citara.

    El criterio, dicho de una vez: llega la discrepancia sobre un numeral en
    el que la memoria APOYA algo, no solo sobre el que ENTRECOMILLA. Medido
    sobre la corrida del entregable en C8: 13 citas llegaban por las puertas
    indirectas, y cruzarlas contra las 23 discrepancias de entonces anadia
    EXACTAMENTE una viva --- la del titulo de la Tabla A.1 --- y ninguna de
    las etapas diferidas. De I3 a D9 fueron 24 declaradas y las puertas
    indirectas anadian DOS: la misma del titulo y `DIS-HR-FORMAS-HDS5`, que
    ancla su parte en TA.1 y ademas llegaba DECLARADA por el paso `de_forma`
    (via 2). D9 la resolvio al corregir la v8, y desde entonces las puertas
    indirectas vuelven a anadir EXACTAMENTE una, la del titulo;
    `test_la_discrepancia_llega_por_la_cita_del_FUNDAMENTO` lo fija.
    """
    citas = set(paso.citas_textuales)
    if paso.formula_cita_id:
        citas.add(paso.formula_cita_id)
    if paso.umbral is not None and paso.umbral.cita_id:
        citas.add(paso.umbral.cita_id)
    if paso.fundamento_id:
        citas.update(_reg_M11.fundamento(paso.fundamento_id).citas)
    return frozenset(citas)


def _discrepancias_que_toca(paso: Any) -> Tuple[Any, ...]:
    """
    Las discrepancias VIVAS que este paso toca, por sus citas o por su valor.

    El cruce lo hace el registro (`discrepancias_que_tocan`); aqui solo se le
    pasa lo que el paso trae. Ni una condicion ni un id cableado en esta capa:
    M11 formatea.
    """
    return _reg_M11.discrepancias_que_tocan(
        citas_en_que_descansa(paso), getattr(paso, "discrepancias", ()))


def _discrepancias_del_paso(paso: Any) -> str:
    """
    EL AVISO, en el punto de uso: que esta linea de la memoria descansa sobre
    una lectura del proyecto y no sobre la letra de la fuente.

    Una linea por discrepancia, con su id, su objeto y quien gana. EL TEXTO
    ENTERO NO VA AQUI: va una sola vez en `bloque_discrepancias`, porque
    repetir los cuatro campos en cada paso que toca la misma discrepancia es
    la segunda transcripcion que la §4.5 prohibe --- y ademas ilegible: la
    Tabla N 09 la tocan cinco pasos.

    `class="interpretacion"`: una discrepancia es lo que el proyecto LEE en
    sus fuentes cuando dicen cosas distintas. Pegarla a `class="fuente"`
    seria NOR-HID-04 en su forma mas cruda --- presentar como norma lo que es
    una eleccion entre dos normas.
    """
    tocadas = _discrepancias_que_toca(paso)
    if not tocadas:
        return ""
    # EL PUNTERO ES UN ENLACE, NO UNA FRASE (EXT-8, PC-12): «el detalle esta
    # en el bloque de discrepancias de esta memoria» se repetia 90 veces en
    # 40 puntos. El id enlaza a la ficha del bloque de discrepancias, que
    # lleva su ancla (`ancla_de_discrepancia`).
    filas = "".join(
        f"<li>{_enlace(ancla_de_discrepancia(d.id), f'<code>{_esc(d.id)}</code>')}"
        f" &mdash; {_esc(d.objeto)}. <b>Gana {_esc(d.gana)}.</b></li>"
        for d in tocadas)
    return ('<dt class="interpretacion">Discrepancia declarada que toca este '
            f'paso</dt><dd class="interpretacion"><ul>{filas}</ul></dd>')


def _sustitucion_del_paso(paso: Any) -> str:
    """
    Los valores que entran, cada uno con unidad y PROCEDENCIA.

    La procedencia no es un adorno: es la mitad que hace que la memoria se
    lea "sin abrir el codigo", que es el criterio de salida de la §4.4. Un
    numero sin origen obliga al revisor a buscar quien lo produjo.
    """
    if not paso.sustitucion:
        return ""
    filas = "".join(
        f"<li><code>{_esc(m.simbolo)}</code> = <b>{_esc(m.texto)}</b>"
        f'<span class="procedencia-cita">{_esc(m.procedencia)}</span></li>'
        for m in paso.sustitucion)
    return f"<dt>Con que valores</dt><dd><ul class=\"sustitucion\">{filas}</ul></dd>"


def _umbral_del_paso(paso: Any) -> str:
    """Contra que se compara: valor, CARACTER de la fuente y aplicacion."""
    u = paso.umbral
    if u is None:
        return ""
    # EL VALOR SE QUEDA EN LA LINEA; el caracter en la fuente y lo que el
    # proyecto hace con el --- que son los mismos para cada aparicion del
    # mismo umbral, y salian 29 veces en 4 puntos --- estan UNA vez en la
    # ficha del anexo, enlazada (EXT-8, PC-12). El criterio adoptado enlaza
    # a su ficha del bloque 3 en vez de decir en prosa que esta alli.
    criterio = ""
    if u.criterio_aplicado:
        declarado = ca.CRITERIOS.get(u.criterio_aplicado)
        etiqueta = (_etiqueta_html(declarado.etiqueta) + " "
                    if declarado is not None else "")
        criterio = (f"<br>Pasa por el criterio adoptado {etiqueta}"
                    + _enlace(ancla_de_criterio(u.criterio_aplicado),
                              f"<code>{_esc(u.criterio_aplicado)}</code>"))
    valor = f"{u.valor} {u.unidad}".strip()
    return (
        "<dt>Contra que se compara</dt><dd>"
        f"<b>{_esc(u.descripcion)} = {_esc(valor)}</b> &mdash; "
        + _enlace(ancla_de_umbral(u), "caracter en la fuente y aplicacion")
        + f"{criterio}</dd>")


def _veredicto_del_paso(paso: Any) -> str:
    v = paso.veredicto
    if v is None:
        return ""
    if v.tipo is TipoDeVeredicto.CUMPLE:
        marca = f'<span class="{MARCA_CUMPLE}">cumple</span>'
    elif v.tipo is TipoDeVeredicto.NO_CUMPLE:
        marca = f'<span class="incumple">NO cumple</span>'
    elif v.tipo is TipoDeVeredicto.INDICADOR:
        marca = f'<span class="{CLASE_INDICADOR}">{MARCA_INDICADOR}</span>'
    else:
        marca = f"<b>{_esc(v.tipo.value)}</b>"
    margen = ""
    if v.margen is not None and isinstance(v.margen, float) \
            and math.isfinite(v.margen):
        margen = (f" &mdash; margen {_num(v.margen)} "
                  f"{_esc(v.unidad)}".rstrip())
    return (f"<dt>Veredicto</dt><dd>{marca}{margen}<br>"
            f"{_esc(v.explicacion)}</dd>")


def _elecciones_del_paso(paso: Any) -> str:
    """
    La PROCEDENCIA de cada eleccion (regla R1): que se adopto, entre que, de
    donde y por que.

    Es lo que hace defendible una memoria y lo que da sentido al analisis de
    sensibilidad, que existia y solo lo consumian los tests (SIS-B-05). Sin
    las alternativas, un valor adoptado y un valor normativo se imprimen
    igual.
    """
    if not paso.elecciones:
        return ""
    impresos = _IMPRESOS.get()
    filas = []
    for e in paso.elecciones:
        entre = ("<br>Elegido entre: "
                 + "; ".join(f"<i>{_esc(x)}</i>" for x in e.entre)
                 if e.entre else "")
        de_donde = f"<br>De: {_esc(e.de_donde)}" if e.de_donde else ""
        cita = (f"<br>Cita: {_esc(_cita_como_texto(e.cita_id))}"
                if e.cita_id else "")
        clave = (f"<br>Criterio adoptado: <code>{_esc(e.clave_criterio)}"
                 "</code>" if e.clave_criterio else "")
        cabeza = f"<b>{_esc(e.que_se_adopto)}: {_esc(e.valor)}</b>"
        cuerpo = (f"{entre}{de_donde}{cita}"
                  f'<br><span class="interpretacion">Por que: '
                  f"{_esc(e.por_que)}</span>{clave}")
        if impresos is None:
            filas.append(f"<li>{cabeza}{cuerpo}</li>")
            continue
        # --- T-10 --- la eleccion IDENTICA ya impresa en este documento va
        # como su linea y un enlace: el valor adoptado se queda aqui.
        ancla, previo = impresos.ver("eleccion", cabeza + cuerpo)
        if previo is None:
            filas.append(f'<li id="{ancla}">{cabeza}{cuerpo}</li>')
        else:
            filas.append(f"<li>{cabeza} &mdash; "
                         + _enlace(ancla, "la misma eleccion, con sus "
                                   "alternativas y su porque, "
                                   f"{_donde(previo)}") + "</li>")
    return ("<dt>Que se eligio, entre que y por que</dt>"
            f"<dd><ul class=\"elecciones\">{''.join(filas)}</ul></dd>")


def _por_que_del_paso(paso: Any) -> str:
    """
    El fundamento del paso: su titulo en la linea y el argumento entero UNA
    vez, en el anexo (EXT-8, PC-12).

    El `por_que` de un paso es un parrafo del registro (`Fundamento.por_que`,
    hasta 2.3 KB) y era el mayor de los textos repetidos de la memoria: el
    mismo fundamento se transcribia en cada punto que daba ese paso. Aqui
    queda `Fundamento.que_paso` --- la frase que dice que se hace y por que,
    en una linea --- y el enlace a la ficha. Un paso SIN `fundamento_id`
    (los hay en fixtures y en pasos que no pasan por `modelos.paso`) imprime
    su `por_que` entero como antes: no hay ficha a la que mandar.
    """
    if not paso.fundamento_id:
        return _esc(paso.por_que)
    f = _reg_M11.fundamento(paso.fundamento_id)
    return (f"{_esc(f.que_paso)} "
            + _enlace(ancla_de_fundamento(f.id),
                      f"fundamento <code>{_esc(f.id)}</code> en el anexo"))


def bloque_paso(paso: Any) -> str:
    """
    Un `PasoDeMemoria` completo (ver `_bloque_paso_entero`). --- T-10 ---
    Dentro de la memoria de los puntos, un paso IDENTICO a uno ya impreso en
    el documento --- mismos numeros, mismas citas, misma nota: el 2.1 de una
    luz global, el 4.2 de una misma carta --- sale como su titulo y un
    enlace a la primera aparicion (`_YaImpreso`). Fuera de ella, entero.
    """
    impresos = _IMPRESOS.get()
    if impresos is None:
        return _bloque_paso_entero(paso).replace("{ancla}", "")
    # La huella del paso se toma SIN el registro activo: la version canonica,
    # para que dos pasos iguales den la misma aunque sus partes ya se hayan
    # impreso en otro sitio.
    token = _IMPRESOS.set(None)
    try:
        canonico = _bloque_paso_entero(paso)
    finally:
        _IMPRESOS.reset(token)
    ancla, previo = impresos.ver("paso", canonico)
    codigo = f"<code>{_esc(paso.codigo)}</code> &mdash; " if paso.codigo else ""
    if previo is not None:
        return (f'<div class="paso repetido"><h5>{codigo}{_esc(paso.que)}'
                "</h5><p>Identico, con los mismos valores, "
                + _enlace(ancla, f"al desarrollado {_donde(previo)}")
                + ".</p></div>")
    return _bloque_paso_entero(paso).replace("{ancla}", f' id="{ancla}"', 1)


def _bloque_paso_entero(paso: Any) -> str:
    """
    Un `PasoDeMemoria` completo, en el orden en que se lee de arriba abajo:
    que, por que, formula, con que valores, resultado, contra que, veredicto,
    la frase de la norma, y las elecciones con su procedencia.

    NO CALCULA NADA. Todos los numeros vienen ya formados desde el modulo que
    los produjo; esta funcion elige etiquetas y clases de CSS.
    """
    codigo = f"<code>{_esc(paso.codigo)}</code> &mdash; " if paso.codigo else ""
    formula_cita = (f'<span class="procedencia-cita">'
                    f"{_esc(_cita_como_texto(paso.formula_cita_id))}</span>"
                    if paso.formula_cita_id else "")
    campos = [
        f"<dt>Por que se hace</dt><dd>{_por_que_del_paso(paso)}</dd>",
        f"<dt>Formula</dt><dd><code>{_esc(paso.formula)}</code>"
        f"{formula_cita}</dd>",
        _sustitucion_del_paso(paso),
        f"<dt>Resultado</dt><dd><b>{_esc(paso.resultado.simbolo)} = "
        f"{_esc(paso.resultado.texto)}</b>"
        f'<span class="procedencia-cita">'
        f"{_esc(paso.resultado.procedencia)}</span></dd>",
        _umbral_del_paso(paso),
        _veredicto_del_paso(paso),
        _citas_del_paso(paso),
        _discrepancias_del_paso(paso),
        _elecciones_del_paso(paso),
    ]
    if paso.nota_del_proyecto:
        campos.append('<dt class="interpretacion">Lo que pone el proyecto'
                      "</dt>" + _nota_del_proyecto(paso.nota_del_proyecto))
    return (f'<div class="paso"{{ancla}}><h5>{codigo}{_esc(paso.que)}</h5>'
            f'<dl class="acotacion">' + "".join(campos) + "</dl></div>")


def _nota_del_proyecto(nota: str) -> str:
    """
    --- T-10 --- La nota del proyecto (lo que el proyecto LEE o HACE, en su
    clase, separada de la fuente). La IDENTICA ya impresa en este documento
    va como enlace a la primera (ver `_YaImpreso`).
    """
    impresos = _IMPRESOS.get()
    if impresos is None:
        return f'<dd class="interpretacion">{_esc(nota)}</dd>'
    ancla, previo = impresos.ver("nota", nota)
    if previo is None:
        return f'<dd class="interpretacion" id="{ancla}">{_esc(nota)}</dd>'
    return ('<dd class="interpretacion">'
            + _enlace(ancla, f"la misma nota del proyecto, {_donde(previo)}")
            + "</dd>")


def bloque_pasos(pasos: Sequence[Any], titulo: str) -> str:
    """Una serie de pasos bajo su encabezado. Vacia si no hay ninguno."""
    if not pasos:
        return ""
    return (f"<h4>{_esc(titulo)}</h4>"
            + "".join(bloque_paso(p) for p in pasos))


def _paso_ausente(codigo: str) -> str:
    """
    El hueco DECLARADO de una verificacion sin `PasoDeMemoria`.

    Ver `sin_fundamento_por_codigo`: una verificacion que no pueda tener
    fundamento normativo se censa con su razon, y aqui se imprime el hueco
    con ella. El censo esta vacio desde T-10 (V5 y V8 salieron en T-7b; V4b,
    V6 y V9 en T-10), y la maquina se conserva para la que mañana lo
    necesite. Imprimir el hueco con su razon es lo contrario de esconderlo.
    """
    censo = sin_fundamento_por_codigo().get(codigo)
    if censo is None:
        return ""
    por_que, que_haria_falta = censo
    return ('<div class="paso nota"><h5><code>' + _esc(codigo)
            + "</code> &mdash; sin fundamento normativo declarado</h5>"
            f"<p><b>Por que no lo tiene:</b> {_esc(por_que)}</p>"
            f"<p><b>Que haria falta para traerlo:</b> "
            f"{_esc(que_haria_falta)}</p></div>")


@dataclass(frozen=True)
class NoAplica:
    """
    La entrada de desarrollo de una verificacion que NO APLICA al punto
    (`EstadoDeVerificacion.NO_APLICA`, C10 / PC-27): no tiene paso porque no
    se evaluo, y el motivo dice que la sustituye. Viaja en
    `desarrollo_de_verificaciones` en el lugar del paso para que ni M11 ni
    la traza la confundan con el HUECO censado de una verificacion sin
    fundamento --- que es lo que el auditor de C10 midio en C-01: la fila
    «no aplica» de V5 imprimia el hueco del derecho de via, pidiendo al
    revisor datos que en un cruce de canal no cierran nada ---.
    """

    codigo: str
    motivo: str


def _no_aplica_html(entrada: "NoAplica") -> str:
    return ('<div class="paso nota"><h5><code>' + _esc(entrada.codigo)
            + f"</code> &mdash; {_esc(MARCA_NO_APLICA)} en este punto</h5>"
            f"<p><b>Por que no aplica:</b> {_esc(entrada.motivo)}</p></div>")


def desarrollo_de_verificaciones(informe: Any) -> Tuple[Tuple[str, Optional[Any]], ...]:
    """
    Las verificaciones cuyo DESARROLLO se imprime bajo la tabla de Fase 5,
    como `(codigo, paso)`: `paso` es el `PasoDeMemoria` de la verificacion,
    un `NoAplica` cuando la verificacion no aplica al punto (C10), o `None`
    cuando no lo tiene y el censo (`sin_fundamento_por_codigo`) explica por
    que --- ese hueco se imprime con `_paso_ausente` ---. Lo que no tiene ni
    paso ni censo no entra: inventarle texto seria peor que el hueco.

    LA MISMA SELECCION PARA M11 Y PARA LA TRAZA DE LA GUI (`traza_punto`),
    y con el paso 2.1 UNA sola vez (EXT-8, PC-12). F2.LUZ cuelga de
    `clasificacion.verificacion_luz` y ya se imprime en la traza de la Fase 2
    (`traza_clasificacion`); volver a desarrollarlo aqui era el «x2 por
    punto» que el dictamen midio. Se excluye por IDENTIDAD del objeto, no por
    codigo: es el mismo `PasoDeMemoria`, no uno parecido.
    """
    ya_impresos = {id(p) for p in traza_clasificacion(informe)}
    censo = sin_fundamento_por_codigo()
    salida: List[Tuple[str, Optional[Any]]] = []
    for _fase, v in verificaciones_publicadas(informe):
        paso = getattr(v, "paso", None)
        if getattr(v, "estado", None) is EstadoDeVerificacion.NO_APLICA:
            salida.append((v.codigo or "", NoAplica(v.codigo or "",
                                                     v.motivo_no_aplica)))
        elif paso is not None:
            if id(paso) in ya_impresos:
                continue
            salida.append((v.codigo or "", paso))
        elif v.codigo and v.codigo in censo:
            salida.append((v.codigo, None))
    return tuple(salida)


SIN_VERIFICACIONES = ('<div class="nota"><p>Sin verificaciones registradas: el '
                      "punto no alcanzo la Fase 5.</p></div>")
# --- T-12 (H2 de su auditoria) --- La marca que la RESUMIDA pone, en texto,
# donde la completa enlaza al bloque de acotaciones: la adopcion se apoya en
# un vacio normativo verificado y no es una cita corriente (NOR-VAC-01).
MARCA_VACIO_VERIFICADO = ("&#9755; adopcion sobre un vacio normativo "
                          "verificado: ver el bloque de acotaciones de la "
                          "memoria completa")


def _filas_verificaciones(verificaciones: Sequence[Tuple[str, Any]], *,
                          remision_acotacion: bool = True) -> List[str]:
    """
    --- T-12 --- Las filas de la tabla de verificaciones (codigo, numeral,
    obtenido, admisible, umbral, resultado), las MISMAS en la memoria
    completa y en la resumida. `remision_acotacion` = False quita el enlace
    al bloque 0-bis, que la resumida no lleva (la completa lo conserva).
    """
    filas = [_fila(["<th>Codigo</th>", "<th>Numeral</th>", "<th>Obtenido</th>",
                    "<th>Admisible</th>", "<th>Umbral</th>",
                    "<th>Resultado</th>"])]
    for fase, v in verificaciones:
        if v.criterio_aplicado:
            # Consulta tolerante: si la clave no esta en CRITERIOS se imprime
            # sola, sin etiqueta. Inventarle una etiqueta seria peor que no
            # ponerla, y caerse seria peor todavia: la memoria no se cae por un
            # desajuste de nombre en la capa de reporte.
            declarado = ca.CRITERIOS.get(v.criterio_aplicado)
            umbral = f"<code>{_esc(v.criterio_aplicado)}</code>"
            if declarado is not None:
                umbral = f"{_etiqueta_html(declarado.etiqueta)} " + umbral
                if declarado.vacio_verificado and remision_acotacion:
                    # La fila sola engana: dice la etiqueta y la clave, y de
                    # ahi se lee una cita normativa corriente. No lo es -- el
                    # numeral que la sostiene habla de otro material o de otra
                    # situacion -- y el revisor esta mirando ESTA fila, no el
                    # bloque 0-bis. La remision es lo que conecta las dos.
                    umbral += (' <a href="#acotaciones" class="remision" '
                               'title="Adopcion sobre un vacio normativo '
                               'verificado: ver el bloque de acotaciones">'
                               "&#9755; acotacion</a>")
                elif declarado.vacio_verificado:
                    # --- T-12 (H2) --- La resumida no tiene bloque 0-bis al
                    # que enlazar, y la fila sola se leeria como cita
                    # corriente: la MARCA va en texto, sin enlace.
                    umbral += (' <span class="remision">'
                               f'{MARCA_VACIO_VERIFICADO}</span>')
        elif v.estado is EstadoDeVerificacion.NO_APLICA:
            # Una fila que no se evaluo no tiene umbral que etiquetar: decir
            # «[N] constante normativa» aqui era mentir sobre una celda vacia.
            umbral = "&ndash;"
        else:
            umbral = f"{_etiqueta_html('N')} constante normativa"
        codigo = v.codigo or fase.split(" - ")[0]
        if _es_indicador(v):
            clase = "fila-indicador"
        else:
            clase = "" if v.cumple else "fila-incumple"
        filas.append(_fila([_td(_esc(codigo)), _td(_esc(v.numeral)),
                            _td(_num(v.valor_obtenido), "num"),
                            _td(_num(v.valor_admisible), "num"),
                            _td(umbral), _td(_marca_de_verificacion(v))], clase))
    return filas


def _tabla_verificaciones(informe: Any) -> str:
    """
    Cada verificacion como cumple / no cumple JUNTO A SU NUMERAL (entregable 1).

    Cuando el umbral proviene de un criterio adoptado se imprime la clave y su
    etiqueta: un revisor tiene que poder distinguir de un vistazo lo que se
    contrasto contra la norma de lo que se contrasto contra una adopcion.
    """
    # EL PUNTO NO CERRO Y AUN ASI HAY FASE 5 QUE PUBLICAR: la seleccion ---
    # con `getattr` y no acceso directo, porque esta funcion se prueba tambien
    # con un informe minimo que solo expone `verificaciones()` --- vive en
    # `verificaciones_publicadas`, compartida con `traza_punto` desde G4.
    # No es un caso de borde: en este expediente NINGUN punto se dimensiona
    # --- V5 se detiene siempre en `ancho_derecho_via_m` ---, de modo que sin
    # el ultimo escalon la memoria no llevaria una sola verificacion
    # hidraulica de ningun punto. Es la misma trampa de NOR-MEM-01.
    verificaciones = verificaciones_publicadas(informe)
    if not verificaciones:
        return SIN_VERIFICACIONES
    filas = _filas_verificaciones(verificaciones)
    # La tabla de Fase 5 de la hoja de ruta trae ONCE filas y este software
    # evalua las once desde S20. Se dice aqui, pegado a la tabla de
    # verificaciones, y no en una nota lejana: es donde el revisor cuenta.
    # V4b se cableo en S14 y V2b en S20; las dos llegan hoy por la via normal
    # -- su fila en la tabla y su criterio en `criterios_usados()` --, no como
    # una constancia de ausencia.
    #
    # LA AFIRMACION POSITIVA SE IMPRIME IGUAL, y por la misma razon por la que
    # se imprimian las constancias: el revisor que cuenta filas necesita saber
    # si el numero que ve es el numero completo. Un bloque vacio le deja la
    # resta a el, que es lo que SIS-A-13 y MAT-O15 reprochan.
    diferidas = "".join(
        f'<div class="nota"><p>{_esc(t)}</p></div>'
        for t in verificaciones_no_evaluadas()) or (
        '<div class="nota"><p>Las ONCE filas de la tabla de Fase 5 de la '
        'hoja de ruta (V1, V2, V2b, V3, V4, V4b, V5, V6, V7, V8, V9) se '
        'evaluan: ninguna queda diferida por falta de metodo. Lo que una '
        'corrida concreta no alcance a evaluar aparece como bloqueo de ese '
        'punto, con su causa, no como una fila que no existe.</p></div>')
    # EL DESARROLLO DE CADA VERIFICACION, debajo de la tabla-resumen. La tabla
    # dice el veredicto de un vistazo; el desarrollo dice de donde sale cada
    # numero, contra que se compara y con que frase de la norma. Sin el, la
    # memoria se lee solo con el codigo al lado, que es lo que el criterio de
    # salida de la §4.4 prohibe.
    #
    # Las que no traen paso NO se saltan: se imprimen con la razon censada de
    # por que no pueden tener fundamento normativo hoy (`_paso_ausente`).
    desarrollo = []
    for codigo, paso in desarrollo_de_verificaciones(informe):
        if isinstance(paso, NoAplica):
            desarrollo.append(_no_aplica_html(paso))
        else:
            desarrollo.append(bloque_paso(paso) if paso is not None
                              else _paso_ausente(codigo))
    detalle = (f"<h4>{_esc(TITULO_TRAZA_VERIFICACIONES)}</h4>"
               + "".join(desarrollo)) if any(desarrollo) else ""
    return "<h4>Verificaciones</h4>" \
           '<table class="compacta">' + "".join(filas) + "</table>" \
           + diferidas + detalle
