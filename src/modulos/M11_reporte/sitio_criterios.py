# -*- coding: utf-8 -*-
"""
M11_reporte.sitio_criterios
===========================
Submodulo de Fase 11 (`M11_reporte`): bloque `sitio_criterios` (D3).
"""

from __future__ import annotations

from dataclasses import replace
from typing import (
    Any,
    List,
    Tuple,
)
from src import (
    criterios_adoptados as ca,
    datos_sitio as ds,
)
from src.modelos import ContextoCorrida

from src.modulos.M11_reporte._base import (
    _esc,
    _etiqueta_html,
    _orden_etiqueta,
    _reg_M11,
    _valor_legible,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
)
from src.modulos.M11_reporte.trazas import (
    traza_durabilidad,
    traza_espaciamiento,
    traza_geometria,
    traza_hidrologia,
    traza_licuefaccion,
)
from src.modulos.M11_reporte.anclas import (
    _cita_como_texto,
    ancla_de_criterio,
    ancla_de_discrepancia,
)
from src.modulos.M11_reporte.pasos import (
    citas_en_que_descansa,
)
from src.modulos.M11_reporte.cabezal import (
    traza_cabezal,
)
from src.modulos.M11_reporte.fases_finales import (
    traza_proteccion,
)
from src.modulos.M11_reporte.metrados import (
    traza_metrado,
)

# ===========================================================================
# 3. Declaracion de criterios adoptados (entregable 2)
# ===========================================================================

def _cabecera_de_corredor(contexto: Any, proyecto: str) -> str:
    """
    La linea del corredor de los datos de sitio de ESTA corrida (con su
    origen) y, si el proyecto no coincide con el, la advertencia de corredor
    (`datos_sitio.advertencia_de_corredor`, EXT-V-01). La llevan las DOS
    vistas de la memoria (T-12, H3 de su auditoria): la resumida es la que se
    imprime, y es justo donde la advertencia no puede desaparecer.
    """
    corredor = contexto.dato_efectivo("corredor_del_proyecto")
    partes = ['<p class="corredor">Corredor de los datos de sitio: '
              f"<b>{_esc(str(corredor.valor))}</b> (origen: "
              f"<code>{_esc(corredor.origen)}</code>)</p>"]
    advertencia = ds.advertencia_de_corredor(proyecto, str(corredor.valor),
                                             corredor.origen)
    if advertencia:
        partes.append(f'<div class="aviso"><p><b>{_esc(advertencia)}</b></p></div>')
    return "".join(partes)


def _declaracion_en_sesion(d: Any, efectivo: Any) -> str:
    """Lo que dice un [S] declarado por sesion: fecha, origen y el archivo."""
    del_archivo = ("el archivo no lo tenia leido" if d.valor is None
                   else f"el archivo dice {_valor_legible(d.valor)}")
    return (f"el {_esc(efectivo.fecha)}, desde "
            f"<code>{_esc(efectivo.origen)}</code>; {del_archivo} "
            f"(<code>{_esc(ds.ORIGEN_ARCHIVO)}</code>)")


def datos_sitio_resumidos(contexto: Any, *, proyecto: str = "") -> str:
    """
    --- T-12 (H3 de su auditoria) --- Los [S] de la corrida en la memoria
    RESUMIDA: el corredor y su advertencia (los mismos de la completa) y una
    tabla con el valor efectivo y DE QUE ARCHIVO salio cada uno (regla (3) de
    EXT-10). El procedimiento, la fuente y la trazabilidad completos estan en
    la seccion 3.1 de la memoria completa.
    """
    partes = [_cabecera_de_corredor(contexto, proyecto)]
    claves = sorted(contexto.datos_usados)
    if not claves:
        partes.append("<p>Esta corrida no invoco ningun dato de sitio.</p>")
        return "".join(partes)
    filas = [_fila(["<th>Dato de sitio</th>", "<th>Valor</th>",
                    "<th>Origen</th>"])]
    for clave in claves:
        d = ds.dato(clave)
        efectivo = contexto.dato_efectivo(clave)
        origen = f"<code>{_esc(efectivo.origen)}</code>"
        if efectivo.declarado_en_caliente:
            origen += ("<br><b>declarado (sesion)</b> "
                       + _declaracion_en_sesion(d, efectivo))
        filas.append(_fila([
            _td(f"{_etiqueta_html(d.etiqueta)} <code>{_esc(clave)}</code>"),
            _td(_valor_legible(efectivo.valor)), _td(origen)]))
    partes.append('<table class="compacta">' + "".join(filas) + "</table>")
    return "".join(partes)


def bloque_datos_sitio(contexto: Any, solo_usados: bool = True, *,
                       proyecto: str = "") -> str:
    """
    Los datos de sitio [S] que el calculo invoco --- leidos del
    `ContextoCorrida` del informe, no del registro vivo (EXT-4) ---, cada uno
    con el procedimiento que lo produjo, la trazabilidad que permite
    repetirlo y, desde EXT-10, DE QUE ARCHIVO SALIO: `datos_sitio.py` (la
    obra del repositorio) o el `sitio.json` / la sesion de otra obra. Un [S]
    declarado por sesion que PISA un valor del archivo se imprime con lo que
    el archivo dice al lado, como los criterios pisados en caliente: tantear
    no es falsear, y la memoria tiene que dejar ver las dos cosas.

    Abre con el corredor para el que se leyeron los datos de sitio de ESTA
    corrida y, si el nombre del proyecto no coincide con el, con la
    advertencia de corredor (EXT-V-01). El texto lo pone
    `datos_sitio.advertencia_de_corredor`, una funcion pura sin estado;
    aqui no se normaliza ni se compara nada, solo se formatea.

    Va delante de los criterios y no mezclado con ellos: un [S] no se defiende
    con un rango de sensibilidad -- no hay nada que elegir -- sino diciendo
    donde se leyo. Mezclarlos daria a entender que el PGA del mapa y la
    eleccion de F_pga son la misma clase de afirmacion, y son lo contrario:
    uno es un hecho del sitio y el otro una decision del proyectista.
    """
    partes: List[str] = [_cabecera_de_corredor(contexto, proyecto)]

    claves = sorted(contexto.datos_usados if solo_usados else ds.DATOS_SITIO)
    if not claves:
        partes.append('<div class="aviso"><p>Esta corrida no invoco ningun dato '
                      "de sitio.</p></div>")
        return "".join(partes)

    for clave in claves:
        d = ds.dato(clave)
        efectivo = contexto.dato_efectivo(clave)
        campos = [
            f"<dt>Concepto</dt><dd>{_esc(d.concepto)}</dd>",
            f"<dt>Valor</dt><dd>{_valor_legible(efectivo.valor)}</dd>",
            f"<dt>Procedimiento</dt><dd>{_esc(d.procedimiento)}</dd>",
            f"<dt>Fuente</dt><dd>{_esc(d.fuente)}</dd>",
            f"<dt>Trazabilidad</dt><dd>{_esc(efectivo.trazabilidad)}</dd>",
            f"<dt>Ambito</dt><dd>{_esc(d.ambito)}</dd>",
            f"<dt>Origen</dt><dd><code>{_esc(efectivo.origen)}</code></dd>",
        ]
        if efectivo.declarado_en_caliente:
            campos.append(
                '<dt class="pendiente">declarado (sesion)</dt>'
                f'<dd class="pendiente">{_declaracion_en_sesion(d, efectivo)}'
                "</dd>")
        if d.reemplazado_por:
            campos.append("<dt>Lo sustituye</dt>"
                          f"<dd>{_esc(d.reemplazado_por)}</dd>")
        if d.verificacion_pendiente:
            campos.append('<dt class="pendiente">Verificar</dt>'
                          f'<dd class="pendiente">'
                          f"{_esc(d.verificacion_pendiente)}</dd>")
        partes.append(
            '<div class="criterio">'
            f'<p class="clave">{_etiqueta_html(d.etiqueta)} '
            f"<code>{_esc(clave)}</code></p><dl>" + "".join(campos)
            + "</dl></div>")

    con_pendiente = [k for k in claves if ds.dato(k).verificacion_pendiente]
    if con_pendiente:
        lista = ", ".join(f"<code>{_esc(k)}</code>" for k in con_pendiente)
        partes.append(
            '<div class="aviso"><p><b>Advertencia.</b> Los datos de sitio '
            f"{lista} tienen la trazabilidad incompleta: el valor esta leido, "
            "pero la memoria todavia no dice sobre que punto exacto se leyo y "
            "un revisor no puede reproducir la lectura.</p></div>")
    return "".join(partes)


def _procedencia(clave: str, contexto: Any) -> str:
    """
    De donde salio el valor que gobierna el calculo: el archivo, o una
    declaracion hecha para esta corrida. Lo dice el `ContextoCorrida`.

    Se imprime en TODOS los criterios y no solo en los declarados en caliente.
    Una marca que aparece solo a veces se lee como una nota al pie; la misma
    fila en todas las fichas convierte la procedencia en parte del contrato de
    la memoria, que es lo que es: el SHA-1 del encabezado identifica el
    ARCHIVO, y un valor que no esta en el archivo no queda identificado por el
    SHA-1 de nadie.
    """
    if not contexto.declarado_en_caliente(clave):
        return ("<dt>Procedencia</dt><dd>transcrita en "
                "<code>criterios_adoptados.py</code>, la version que el "
                "encabezado identifica por SHA-1</dd>")
    del_archivo = ca.criterio(clave).valor
    dice_el_archivo = (
        "el archivo lo declara <b>sin valor</b>" if del_archivo is None else
        f"el archivo declara {_valor_legible(del_archivo)}")
    return ('<dt class="pendiente">Procedencia</dt>'
            f'<dd class="pendiente"><b>DECLARADO PARA ESTA CORRIDA</b> '
            f"&mdash; {dice_el_archivo}. El valor de arriba lo declaro quien "
            "corrio el calculo (GUI o CLI) y NO esta en "
            "<code>criterios_adoptados.py</code>: no es un valor transcrito "
            "de una norma y reproducir esta memoria exige repetir la "
            "declaracion.</dd>" + _de_donde_salio(clave, contexto))


def _de_donde_salio(clave: str, contexto: Any) -> str:
    """
    La PROCEDENCIA de la ventana: de que fila de que tabla salio el valor, con
    su cita, sus alternativas descartadas y la fecha.

    Es la mitad que la regla R1 del plan v12 exige y que `_procedencia` sola
    no puede dar: aquella dice que el valor no esta en el archivo, y esta dice
    de donde SI esta. Sin ella, «6.0 m/s» y «6.0 m/s porque es la fila
    Concreto de la Tabla N 10, descartando 3.0» son la misma linea en la
    pagina y no son la misma decision.

    Devuelve cadena vacia cuando el valor entro por otro camino
    (`--declarar`, `conftest`): no toda declaracion en caliente pasa por la
    ventana, y fingir una procedencia que nadie registro seria peor que no
    imprimir ninguna.
    """
    procedencia = contexto.procedencia_de(clave)
    if procedencia is None:
        return ""
    filas = []
    if procedencia.filas and procedencia.difiere_de_la_celda():
        # PROCEDENCIA VERAZ (EXT-V-02): el valor declarado NO es el de la
        # celda, y la memoria no puede decir que «proviene» de ella. Se
        # imprime la celda al lado, para que el revisor vea los dos numeros.
        filas.append('<dt class="pendiente">Proviene de</dt>'
                     '<dd class="pendiente">fila <code>'
                     + "</code>, <code>".join(_esc(f) for f in procedencia.filas)
                     + f"</code> de la tabla <code>{_esc(procedencia.tabla_id)}"
                     f"</code> &mdash; {_esc(procedencia.titulo_de_la_tabla)}"
                     f"<br><b>DIFIERE de la celda "
                     f"({_esc(procedencia.valor_de_la_celda)})</b>: el valor "
                     "de arriba NO es el que la tabla imprime en esa fila; "
                     "es una adopcion del proyectista que la nota de la "
                     "declaracion tiene que defender.</dd>")
    elif procedencia.filas:
        filas.append("<dt>Proviene de</dt><dd>fila <code>"
                     + "</code>, <code>".join(_esc(f) for f in procedencia.filas)
                     + f"</code> de la tabla <code>{_esc(procedencia.tabla_id)}"
                     f"</code> &mdash; {_esc(procedencia.titulo_de_la_tabla)}"
                     "<br>LA TABLA ES NORMATIVA; LA ELECCION DE FILA NO LO ES: "
                     "el valor de arriba es una adopcion del proyectista que "
                     "PROVIENE de esa fila.</dd>")
    elif procedencia.columnas:
        filas.append("<dt>Proviene de</dt><dd>columna <code>"
                     + "</code>, <code>".join(_esc(c)
                                              for c in procedencia.columnas)
                     + f"</code> de la tabla <code>{_esc(procedencia.tabla_id)}"
                     f"</code> &mdash; {_esc(procedencia.titulo_de_la_tabla)}</dd>")
    elif procedencia.catalogo_id:
        filas.append("<dt>Proviene de</dt><dd>el catalogo <code>"
                     f"{_esc(procedencia.catalogo_id)}</code>. "
                     "<b>NO es una norma</b> y no tiene numeral.</dd>")
    if procedencia.frase_del_rango:
        filas.append(f"<dt>Rango de la fuente</dt><dd>{_esc(procedencia.rotulo_del_rango)}"
                     f" {_esc(procedencia.frase_del_rango)} "
                     f"[{_esc(procedencia.semantica)}]</dd>")
    if procedencia.cita:
        filas.append(f"<dt>Cita</dt><dd>{_esc(procedencia.cita)}</dd>")
    if procedencia.alternativas_descartadas:
        descartadas = "; ".join(
            f"<code>{_esc(a.id)}</code> ({_esc(a.valor)}) &mdash; {_esc(a.motivo)}"
            for a in procedencia.alternativas_descartadas)
        filas.append(f"<dt>Alternativas descartadas</dt><dd>{descartadas}</dd>")
    if procedencia.aviso:
        filas.append('<dt class="pendiente">Aviso</dt>'
                     f'<dd class="pendiente">{_esc(procedencia.aviso)}</dd>')
    filas.append(f"<dt>Declarado el</dt><dd>{_esc(procedencia.fecha)}</dd>")
    return "".join(filas)


def _de_donde_sale_el_valor(clave: str, contexto: Any) -> str:
    """
    La PROCEDENCIA de un criterio transcrito en el archivo (regla R1): de que
    tabla, de que rango, de que catalogo o de que ensayo sale su valor.

    ES LA OTRA MITAD DE `_de_donde_salio`, y hacia falta. Aquella solo dispara
    para los valores declarados EN CALIENTE por la ventana emergente ---
    `declaracion.procedencia_de` no registra nada de lo que esta escrito en
    `criterios_adoptados.py` ---, de modo que los 40 y pico criterios del
    archivo, que son la inmensa mayoria de los que gobiernan una corrida, se
    imprimian sin decir de donde salen. Esta funcion lee `Criterio.resolucion`,
    que es el objeto que S15 puso justamente para eso y que la memoria no
    consumia.

    El MODO ES EL TIPO de la resolucion (Sec. 4.3): no hay dos campos que
    puedan contradecirse.
    """
    c = ca.CRITERIOS.get(clave)
    r = getattr(c, "resolucion", None) if c is not None else None
    if r is None:
        return ""
    # CUIDADO CON EL VALOR EN CALIENTE. `resolucion` describe como el ARCHIVO
    # resuelve este criterio. Si el valor en vigor se declaro al lanzar la
    # corrida y NO paso por la ventana --- `--declarar`, la GUI sin ventana ---
    # entonces no salio por ese camino, y decirlo sin mas convertiria esta
    # ficha en la procedencia inventada que `_de_donde_salio` existe para no
    # fingir. Se imprime igual, porque el revisor necesita saber que camino
    # deberia haber seguido, y con la advertencia delante.
    en_caliente = (contexto.declarado_en_caliente(clave)
                   and contexto.procedencia_de(clave) is None)
    aviso = (
        '<br><b class="pendiente">El valor en vigor NO salio por este '
        "camino:</b> se declaro al lanzar la corrida y nadie registro de "
        "donde. Lo de arriba es como <code>criterios_adoptados.py</code> "
        "resuelve este criterio, no de donde vino el numero que gobierna "
        "esta memoria." if en_caliente else "")
    nombre = type(r).__name__
    if nombre == "DeTabla":
        tablas = ", ".join(f"<code>{_esc(t)}</code>" for t in r.tablas)
        detalle = f"tabla(s) {tablas} del registro normativo; elige "
        detalle += _esc(r.que_elige)
        if r.fila_id:
            detalle += f", fila <code>{_esc(r.fila_id)}</code>"
        if r.columna_id:
            detalle += f", columna <code>{_esc(r.columna_id)}</code>"
        if r.laguna:
            detalle += ("<br><b>No es una fila, es una REGLA DE LECTURA que "
                        f"la tabla no resuelve:</b> {_esc(r.laguna)}")
        if r.elegido_por:
            detalle += (f"<br>La fila la elige <code>{_esc(r.elegido_por)}"
                        "</code>, no este criterio.")
        return ("<dt>De donde sale (R1)</dt><dd><b>De tabla.</b> "
                + detalle + aviso + "</dd>")
    if nombre == "EnRango":
        return ("<dt>De donde sale (R1)</dt><dd><b>De un rango de la "
                f"fuente.</b> Acota {_esc(r.que_acota)}; el rango vive en la "
                f"tabla <code>{_esc(r.tabla_id)}</code>, fila "
                f"<code>{_esc(r.fila_id)}</code>, columna "
                f"<code>{_esc(r.columna_id)}</code> del registro. "
                "El valor NO se copia aqui: se referencia, para que la "
                "memoria no pueda imprimir como «minimo» el primero de dos "
                "maximos (NOR-HID-04)." + aviso + "</dd>")
    if nombre == "DeCatalogo":
        return ('<dt class="pendiente">De donde sale (R1)</dt>'
                '<dd class="pendiente"><b>De CATALOGO, no de norma.</b> '
                f"Catalogo <code>{_esc(r.catalogo_id)}</code>; elige "
                f"{_esc(r.que_elige)}.<br><b>Advertencia obligatoria:</b> "
                f"{_esc(r.advertencia)}" + aviso + "</dd>")
    if nombre == "DeEnsayo":
        return ("<dt>De donde sale (R1)</dt><dd><b>De un ensayo.</b> "
                f"{_esc(r.ensayo)}.<br><b>Trazabilidad exigida:</b> "
                f"{_esc(r.trazabilidad_exigida)}" + aviso + "</dd>")
    if nombre == "Derivada":
        de = ", ".join(f"<code>{_esc(x)}</code>" for x in r.de)
        return ("<dt>De donde sale (R1)</dt><dd><b>Derivada.</b> No es "
                f"editable: se calcula desde {de} con la regla "
                f"{_esc(r.regla)}." + aviso + "</dd>")
    # Libre
    pendiente = (f"<br><b>Tabla pendiente de transcribir:</b> "
                 f"{_esc(r.tabla_pendiente)}" if r.tabla_pendiente else "")
    dominio = f"<br>Dominio fisico: {_esc(r.dominio)}" if r.dominio else ""
    opciones = ("<br>Valores admisibles: "
                + ", ".join(f"<i>{_esc(o)}</i>" for o in r.opciones)
                if r.opciones else "")
    return ("<dt>De donde sale (R1)</dt><dd><b>Libre.</b> Ninguna tabla, "
            "ningun rango de fuente y ninguna medicion lo determinan: el "
            f"numero lo pone {_esc(r.que_lo_fija)}."
            + dominio + opciones + pendiente + aviso + "</dd>")


def _sensibilidad_declarada(clave: str, criterio: Any) -> str:
    """
    El rango de sensibilidad de un criterio, IMPRESO COMO ANALISIS y no como
    un par de numeros sueltos.

    SIS-B-05: `criterios_adoptados.parametros_sensibilizables()` existia y solo
    la consumian los tests, mientras la plantilla anunciaba «con analisis de
    sensibilidad obligatorio». El insumo llegaba al documento --- el rango se
    imprimia --- pero sin decir que era ni para que servia, de modo que nadie
    podia leerlo como un analisis. Aqui se dice: que se adopto, dentro de que
    margen se movio la eleccion, y que un barrido tendria que recorrer.

    Los rangos NO NUMERICOS --- una sensibilidad expresada en funcion de otro
    criterio, o un conjunto de opciones --- se imprimen igual y se marcan como
    no recorribles: `parametros_sensibilizables` los excluye de su barrido a
    proposito, porque hacerles `float()` los falsearia.
    """
    rango = criterio.sensibilidad
    if not rango:
        return ""
    recorribles = ca.parametros_sensibilizables(solo_numericos=True)
    if clave in recorribles:
        nota = ("Rango numerico: un barrido de sensibilidad lo recorre "
                "entero. Es lo que hay que mover para saber si el resultado "
                "de esta memoria depende de la adopcion o no.")
    else:
        nota = ("Rango NO numerico o simbolico: se declara y se imprime, pero "
                "un barrido no lo puede recorrer sin resolver antes la "
                "variable de la que depende. Forzarlo a numero lo falsearia.")
    return ("<dt>Sensibilidad declarada</dt><dd>"
            f"Valor adoptado <b>{_valor_legible(criterio.valor)}</b> dentro "
            f"de <b>{_valor_legible(rango)}</b>.<br>"
            f'<span class="interpretacion">{_esc(nota)}</span></dd>')


def pasos_del_informe(informe: Any) -> Tuple[Any, ...]:
    """
    Todos los `PasoDeMemoria` que ESTA corrida emitio, de donde sea.

    Existe porque `bloque_discrepancias` tiene que saber que citas imprimio la
    memoria para saber que discrepancias toca, y eso no se puede preguntar
    bloque a bloque: un paso hidraulico vive en `ResultadoHidraulico.pasos`,
    uno de verificacion cuelga de su `Verificacion`, y los de la traza cuelgan
    de escalones que ni siquiera se adoptaron.

    `tests/test_memoria_sustentada._pasos_de` hace el mismo recorrido y NO se
    borra a cambio de este: un test que consuma la funcion que audita deja de
    auditarla. Lo que hay es un test que compara los dos recorridos, de modo
    que si uno se olvida de una rama nueva del informe, el otro lo dice.
    """
    vistos: List[Any] = []
    for punto in informe.puntos:
        vistos.extend(pasos_del_punto(punto))
    for recubrimiento in informe.cabezal.recubrimientos:
        if getattr(recubrimiento, "paso", None) is not None:
            vistos.append(recubrimiento.paso)
    return tuple(vistos)


def pasos_del_punto(punto: Any) -> Tuple[Any, ...]:
    """
    Los pasos de UN punto, en el orden de `pasos_del_informe` (que desde
    T-10 es esta travesia punto a punto, mas los recubrimientos del
    proyecto). La usa tambien el anexo de sensibilidad por punto.
    """
    vistos: List[Any] = []

    def _anota(paso: Any) -> None:
        if paso is not None:
            vistos.append(paso)

    if punto.clasificacion is not None:
        _anota(getattr(punto.clasificacion.verificacion_luz, "paso", None))
        _anota(getattr(punto.clasificacion.periodo_retorno, "paso", None))
    vistos.extend(traza_hidrologia(punto))      # Fase 1-bis (T-1)
    vistos.extend(traza_licuefaccion(punto))    # Fase 0-bis (VE-7, C4)
    for _fase, v in punto.verificaciones():
        _anota(getattr(v, "paso", None))
    for escalon in punto.traza:
        for v in escalon.verificaciones:
            _anota(getattr(v, "paso", None))
        hidraulico = getattr(escalon, "resultado_hidraulico", None)
        if hidraulico is not None:
            vistos.extend(hidraulico.pasos)
    if punto.resultado is not None and \
            punto.resultado.resultado_hidraulico is not None:
        vistos.extend(punto.resultado.resultado_hidraulico.pasos)
    if punto.resultado is not None and \
            getattr(punto.resultado, "gobierno_por_receptor", None) is not None:
        _anota(punto.resultado.gobierno_por_receptor.paso)     # VE-3.13
    if getattr(punto, "tw_sec13", None) is not None:
        _anota(getattr(punto.tw_sec13, "paso", None))
    vistos.extend(traza_durabilidad(punto))
    # --- T-8 --- todos los pasos de la Fase 6, no solo el de Laushey.
    vistos.extend(traza_proteccion(punto))
    vistos.extend(traza_espaciamiento(punto))         # --- T-9 ---
    vistos.extend(traza_geometria(punto)[0])          # --- T-6 ---
    vistos.extend(traza_cabezal(punto))               # --- T-7a ---
    vistos.extend(traza_metrado(punto))               # --- VE-5 met ---
    return tuple(vistos)


def _ancla_de_parte(parte: Any) -> str:
    """
    La cita de una parte de la discrepancia, o EL AVISO de que se anuncia y no
    esta transcrita.

    Nueve de las 38 `Parte.cita_id` del registro nombran citas que nadie
    transcribio (`Registro.partes_sin_cita_transcrita`). Imprimir el id pelado
    mandaria al revisor a buscar en el registro algo que no esta; callarlo
    dejaria la afirmacion de la parte sin ancla y sin decir que le falta. Se
    dice lo que hay: el id anunciado y que la transcripcion falta.
    """
    if not parte.cita_id:
        return ""
    try:
        texto = _cita_como_texto(parte.cita_id)
    except KeyError:
        return ('<span class="pendiente"> [cita anunciada y NO transcrita al '
                f"registro: <code>{_esc(parte.cita_id)}</code>; la afirmacion "
                "de esta parte no se puede contrastar contra su pagina hasta "
                "que se transcriba]</span>")
    return f'<span class="procedencia-cita">{_esc(texto)}</span>'


def bloque_discrepancias(informe: Any) -> str:
    """
    LAS DISCREPANCIAS DECLARADAS QUE ESTA CORRIDA TOCA, con sus cuatro campos.

    POR QUE ESTE BLOQUE EXISTE. El registro de discrepancias llevaba desde
    S-anteriores enumerando lo que `CLAUDE.md` obliga a declarar, y
    `Registro.discrepancias_abiertas` decia en su docstring «M11 las
    imprime». No las imprimia: M11 no importaba el modulo. De las 23
    declaradas llegaban DOS a la memoria, y las dos por accidente --- con el
    id escrito a mano dentro de la justificacion de un criterio o de la nota
    de una cita, que es la segunda transcripcion que la §4.5 prohibe. Una
    discrepancia registrada donde nadie la lee esta tan registrada como no
    registrada, que es la segunda de las dos lecciones que le costaron
    auditorias a este proyecto.

    QUE LLEGA Y QUE NO, que es la decision y no el mecanismo. El manifiesto es
    para quien AUDITA EL CODIGO y la memoria para quien SUSTENTA, y de ahi
    salen los dos filtros:

    - **Vivas.** Lo `RESUELTA` no llega (`EstadoDiscrepancia.viva`): quien
      abra hoy el PDF por donde la memoria lo manda encuentra lo que la
      memoria dice. Son cinco de las 23 y son historia del repositorio.
      Las `ERRATA_DE_IMPRENTA` SI llegan, y es la mitad menos obvia de la
      regla: el PDF sigue imprimiendo lo que imprime, de modo que el revisor
      que lea la Tabla N 09 al pie de la letra encontrara un n de Manning
      distinto del que la memoria uso.
    - **Tocadas por la corrida.** No se vuelcan las 18 vivas: llegan las que
      esta corrida toca, por las citas que sus pasos imprimieron o por el
      valor que sus pasos sustituyeron (`Registro.discrepancias_que_tocan`).
      Que una corrida `--alcance perfil` no traiga las seis del cabezal no es
      un olvido --- es que el cabezal esta diferido y la memoria no afirma
      nada sobre ellas.

    `class="interpretacion"` en todo el bloque: NOR-HID-04. Una discrepancia
    es lo que el proyecto LEE cuando dos fuentes dicen cosas distintas, y
    presentarla con la autoridad de una cita es exactamente el defecto que esa
    ficha nombra.
    """
    citas: set = set()
    declaradas: set = set()
    for paso in pasos_del_informe(informe):
        # LAS CUATRO PUERTAS, no solo `citas_textuales`: ver
        # `citas_en_que_descansa`. Leyendo solo la primera, la memoria de C-01
        # perdia la discrepancia sobre el titulo de la Tabla A.1 --- la tabla
        # que le da los coeficientes del control de entrada que gobierna.
        citas.update(citas_en_que_descansa(paso))
        declaradas.update(getattr(paso, "discrepancias", ()))
    # La tercera via: los criterios que la corrida INVOCO. `criterios_usados`
    # y no `CRITERIOS`, por lo mismo que `bloque_criterios`: la memoria
    # publica lo que este calculo uso, no el catalogo entero.
    for clave in ContextoCorrida.de(informe).criterios_usados:
        declaradas.update(ca.criterio(clave).discrepancias)
    tocadas = _reg_M11.discrepancias_que_tocan(citas, declaradas)
    if not tocadas:
        return ('<div class="aviso"><p>Esta corrida no toca ninguna '
                "discrepancia declarada viva.</p></div>")

    partes: List[str] = []
    for d in tocadas:
        filas_partes = "".join(
            f"<li><b>{_esc(p.quien)}</b>: {_esc(p.que_dice)}"
            + _ancla_de_parte(p) + "</li>" for p in d.partes)
        partes.append(
            f'<div class="acotacion interpretacion" '
            f'id="{_esc(ancla_de_discrepancia(d.id))}">'
            f"<h4><code>{_esc(d.id)}</code> &mdash; {_esc(d.objeto)}</h4>"
            f"<dl><dt>Estado</dt><dd>{_esc(d.estado.value)}</dd>"
            f"<dt>Que dice cada parte</dt><dd><ul>{filas_partes}</ul></dd>"
            f"<dt>Cual gana, y por que</dt><dd><b>{_esc(d.gana)}</b>. "
            f"{_esc(d.por_que)}</dd>"
            "<dt>Que pasaria siguiendo a la otra</dt>"
            f"<dd>{_esc(d.efecto_si_se_sigue_la_otra)}</dd></dl></div>")
    return "".join(partes)


def _criterio_efectivo(clave: str, contexto: Any):
    """
    El `Criterio` TAL COMO GOBERNO esa corrida: el texto del archivo con el
    valor efectivo que el contexto fotografio. Es `ca.criterio_efectivo`
    leido de la foto y no del registro vivo.
    """
    return replace(ca.criterio(clave), valor=contexto.valor_efectivo(clave))


def _valor_por_punto(clave: str, contexto: Any) -> str:
    """
    --- dictamen Fable (VE-7 lote A, A2) --- Lo que un criterio valio en los
    puntos que lo pisaron para si (`ContextoCorrida.criterios_por_punto`):
    «por punto (`embocadura_cajon_del_punto`): C-01 = ...». Vacio si ninguno.
    """
    por_punto = getattr(contexto, "criterios_por_punto", None) or {}
    if clave not in por_punto:
        return ""
    return ('<b class="pendiente"> [por punto (<code>'
            "embocadura_cajon_del_punto</code>): "
            + "; ".join(f"{_esc(i)} = {_valor_legible(v)}"
                        for i, v in sorted(por_punto[clave].items()))
            + "]</b>")


def bloque_criterios(contexto: Any, solo_usados: bool = True) -> str:
    """
    El contenido de `criterios_adoptados.reporte_criterios` como HTML: cada
    criterio invocado con su valor EFECTIVO, su procedencia, su etiqueta, su
    justificacion y su fuente. Usos, valores efectivos y procedencias salen
    del `ContextoCorrida` de la corrida (EXT-4); del catalogo, solo el texto.

    Lee los mismos objetos `Criterio` que la version en texto, en el mismo
    orden de etiqueta, para que las dos digan exactamente lo mismo.

    Valor EFECTIVO significa `ca.criterio_efectivo`, no `ca.criterio`: el
    valor que el calculo uso de verdad. Leyendo el del archivo, un criterio
    declarado en caliente -- el camino normal de la GUI, "aplicar solo a esta
    corrida" -- se imprimia como "sin valor declarado" en la misma pagina
    cuyos numeros gobernaba, y el bloque de vacios tampoco lo listaba
    (`criterios_sin_valor` lo excluye, con razon: ya no es un vacio). El
    criterio desaparecia de la memoria por partida doble. Era el unico
    hallazgo BLOQUEANTE de las tres auditorias (SIS-A-01).
    """
    claves = sorted(contexto.criterios_usados if solo_usados else ca.CRITERIOS,
                    key=lambda k: (_orden_etiqueta(ca.criterio(k).etiqueta), k))
    if not claves:
        return ('<div class="aviso"><p>Esta corrida no invoco ningun criterio '
                "adoptado.</p></div>")

    partes: List[str] = []
    for clave in claves:
        c = _criterio_efectivo(clave, contexto)
        campos = [
            f"<dt>Concepto</dt><dd>{_esc(c.concepto)}</dd>",
            f"<dt>Valor</dt><dd>{_valor_legible(c.valor)}"
            + ('<b class="pendiente"> [declarado para esta corrida, no en '
               "archivo]</b>" if contexto.declarado_en_caliente(clave) else "")
            + ('<b class="pendiente"> [PROVISIONAL: valor de prueba, '
               "NO verificado]</b>" if c.provisional else "")
            + _valor_por_punto(clave, contexto)
            + "</dd>",
            _procedencia(clave, contexto),
            _de_donde_sale_el_valor(clave, contexto),
            f"<dt>Justificacion</dt><dd>{_esc(c.justificacion)}</dd>",
            f"<dt>Fuente</dt><dd>{_esc(c.fuente)}</dd>",
        ]
        if c.reemplazado_por:
            campos.append("<dt>Lo sustituye</dt>"
                          f"<dd>{_esc(c.reemplazado_por)}</dd>")
        if c.sensibilidad:
            campos.append(_sensibilidad_declarada(clave, c))
        if c.trazabilidad:
            campos.append("<dt>Trazabilidad</dt>"
                          f"<dd>{_esc(c.trazabilidad)}</dd>")
        if c.verificacion_pendiente:
            campos.append('<dt class="pendiente">Verificar</dt>'
                          f'<dd class="pendiente">'
                          f"{_esc(c.verificacion_pendiente)}</dd>")
        if c.discrepancias:
            # El aviso EN LA FICHA, que es el punto de uso del criterio. El
            # texto entero va una sola vez, en `bloque_discrepancias`.
            enlaces = "; ".join(
                f"<code>{_esc(d.id)}</code> &mdash; {_esc(d.objeto)} "
                f"(gana {_esc(d.gana)})"
                for d in _reg_M11.discrepancias_que_tocan((), c.discrepancias))
            campos.append('<dt class="interpretacion">Discrepancia declarada'
                          f'</dt><dd class="interpretacion">{enlaces}</dd>')
        partes.append(
            f'<div class="criterio" id="{_esc(ancla_de_criterio(clave))}">'
            f'<p class="clave">{_etiqueta_html(c.etiqueta)} '
            f"<code>{_esc(clave)}</code></p><dl>" + "".join(campos)
            + "</dl></div>")

    en_caliente = [k for k in claves if contexto.declarado_en_caliente(k)]
    if en_caliente:
        lista = ", ".join(f"<code>{_esc(k)}</code>" for k in en_caliente)
        partes.append(
            '<div class="bloqueo"><p><b>DECLARADOS PARA ESTA CORRIDA.</b> '
            f"Los criterios {lista} recibieron su valor al lanzar el calculo "
            "y <b>no estan en <code>criterios_adoptados.py</code></b>. Valen "
            "para esta memoria y para ninguna otra: el encabezado identifica "
            "el archivo por SHA-1 y estos valores no viajan en el. Para que "
            "el expediente los sostenga hay que escribirlos en el archivo, "
            "con su justificacion y su fuente, y volver a correr.</p></div>")

    con_pendiente = [k for k in claves if ca.criterio(k).verificacion_pendiente]
    if con_pendiente:
        lista = ", ".join(f"<code>{_esc(k)}</code>" for k in con_pendiente)
        partes.append(
            '<div class="aviso"><p><b>Advertencia.</b> Los criterios '
            f"{lista} tienen una verificacion documental pendiente y no deben "
            "citarse como cerrados en la memoria hasta resolverla. El detalle "
            "de cada una esta en el bloque 4.</p></div>")
    return "".join(partes)
