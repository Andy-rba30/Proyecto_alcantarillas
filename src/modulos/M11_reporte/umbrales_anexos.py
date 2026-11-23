# -*- coding: utf-8 -*-
"""
M11_reporte.umbrales_anexos
===========================
Submodulo de Fase 11 (`M11_reporte`): bloque `umbrales_anexos` (D3).
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
)
from src import criterios_adoptados as ca
from src.constantes_normativas import (
    UMBRALES_DE_VERIFICACION,
    caracter_del_umbral,
    fundamento_del_umbral,
    literales_del_umbral,
    numeral_del_umbral,
)
from src.modelos import (
    ContextoCorrida,
    modo_de,
)

from src.modulos.M11_reporte._base import (
    VACIO,
    _esc,
    _reg_M11,
    _valor_legible,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
)
from src.modulos.M11_reporte.trazas import (
    traza_clasificacion,
    traza_durabilidad,
    traza_espaciamiento,
    traza_geometria,
    traza_hidraulica,
    traza_hidrologia,
    traza_licuefaccion,
    traza_tw,
    verificaciones_publicadas,
)
from src.modulos.M11_reporte.anclas import (
    _cita_como_texto,
    _clave_de_umbral,
    _enlace,
    ancla_de_cita,
    ancla_de_criterio,
    ancla_de_fundamento,
    ancla_de_umbral,
)
from src.modulos.M11_reporte.pasos import (
    NoAplica,
    desarrollo_de_verificaciones,
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
from src.modulos.M11_reporte.sitio_criterios import (
    _criterio_efectivo,
    pasos_del_punto,
)

# ---------------------------------------------------------------------------
# Umbrales normativos y su caracter
# ---------------------------------------------------------------------------

def _interpretacion_tabla_10() -> str:
    """
    La lectura del proyectista sobre la Tabla Nº 10, impresa APARTE y marcada
    como interpretacion, con los hechos que juegan EN CONTRA delante.

    Es NOR-HID-04 y es el caso testigo de la regla tipografica: «el rango
    recorre la calidad del revestimiento» no esta en el Manual -- nada dice
    por que hay dos numeros --, y se imprimia pegada a la cita, dentro del
    mismo parrafo, como si fuera norma. El texto sale ahora del registro
    (`TablaNormativa.interpretacion`, del tipo `Interpretacion`), que es el
    unico objeto del proyecto que EXIGE declarar lo que juega en contra: una
    lectura que no encuentra nada en contra no se ha buscado a si misma.
    """
    interp = _reg_M11.tabla("MC_HHD.T10").interpretacion
    contra = "".join(f"<li>{_esc(x)}</li>" for x in interp.en_contra)
    favor = "".join(f"<li>{_esc(x)}</li>" for x in interp.a_favor)
    return (
        '<div class="aviso interpretacion">'
        "<p><b>Interpretacion del proyectista sobre la Tabla N&deg; 10 "
        "&mdash; esto NO lo dice el Manual.</b></p>"
        f"<p>{_esc(interp.texto)}</p>"
        f"<p><b>Lo que juega EN CONTRA de esta lectura:</b></p><ul>{contra}"
        "</ul>"
        f"<p><b>Lo que juega a favor:</b></p><ul>{favor}</ul></div>")


def bloque_umbrales() -> str:
    """
    Los umbrales normativos que el proyecto verifica -- y las CONDICIONES DE
    USO de las formulas que adopta --, cada uno con el texto literal que lo
    fija, su CARACTER en la fuente (recomendacion, exigencia o condicion de
    aplicacion) y lo que el proyecto hace con el.

    La entrada 'h_o' no es un umbral y esta aqui a proposito (NOR-HDS-05): la
    condicion que HDS-5 impone a h_o = (dc + D)/2 tiene que llegar a la
    memoria SIEMPRE, y el criterio que la declara ('geometria_control_salida')
    solo se imprime si la corrida llega a invocarlo -- o sea si llega a M4,
    que en la corrida por defecto de este expediente no ocurre: se detiene
    antes en 'talud_terraplen'. Con `--longitud` declarada M4 si corre y la
    ficha del criterio se imprime; la diferencia es justamente el problema, y
    es el mecanismo por el que NOR-MEM-01 dejo el matiz de V2 fuera de la
    memoria generada. La solucion es la misma: un bloque que no depende de
    ningun resultado.

    Lo que este bloque NO puede decir es que un punto CONCRETO esta fuera de
    rango, porque no mira resultados. Eso se dice en la memoria del punto, en
    `_tabla_diseno`, leyendo `ResultadoHidraulico.h_o_fuera_de_rango`.

    POR QUE ES UN BLOQUE PROPIO Y NO UNA COLUMNA DE LA TABLA DE
    VERIFICACIONES (NOR-MEM-01). El matiz "el numeral recomienda, no prohibe"
    viajaba unicamente dentro de `M5.NUMERAL_V2`, o sea dentro de la tabla de
    verificaciones de cada punto. Esa tabla solo se imprime si el punto llego
    a evaluarse, y en la corrida de referencia de entonces no llegaba -- se
    detenia antes, en un criterio sin declarar --, de modo que la palabra
    "recomend" aparecia CERO veces en la memoria generada mientras el
    repositorio afirmaba que era "lo unico que la memoria imprime de V2". La
    afirmacion era cierta sobre el codigo y falsa sobre el producto. (Hasta
    T-0 este parrafo atribuia la detencion a un criterio de hidrologia que
    ningun modulo lee, INF-5.1.1; la razon del bloque no dependia de eso.)

    Este bloque no depende de ningun resultado: declara el marco normativo con
    que se verifica, se imprima o no una sola fila de verificacion. Un umbral
    aplicado como exigencia cuando la fuente lo escribe como recomendacion es
    una decision del proyecto y se declara; al reves -- imprimir "exigencia"
    donde la fuente recomienda -- es una cita falsa, que la Sec. 0.5 de la
    hoja de ruta llama la clase de defecto mas grave.

    No calcula nada: formatea `constantes_normativas.UMBRALES_DE_VERIFICACION`.
    """
    partes = [
        '<div class="nota"><p>De cada umbral se dicen <b>cuatro</b> cosas, y '
        "cada una con su tipografia, porque confundirlas es lo que convierte "
        "una recomendacion en una exigencia inventada: la "
        "<span class=\'fuente\'>frase literal de la fuente</span>, "
        "entrecomillada y con su numeral; el <b>caracter</b> que esa fuente le "
        "da, leido de la cita y no redactado aqui; la "
        "<span class=\'interpretacion\'>lectura del proyectista</span> "
        "cuando la hay; y lo que el <b>proyecto</b> hace con el.</p>"
        "<p>Las tres primeras son distintas entre si. Una cita es lo que el "
        "documento dice. Una interpretacion es lo que este proyecto lee en "
        "ella, y va marcada como tal aunque sea razonable: es lo que permite "
        "a un revisor discutirla sin discutir la norma "
        "(<code>NOR-HID-04</code>). Y lo que el proyecto HACE con el umbral "
        "no es ninguna de las dos.</p></div>"]
    for u in UMBRALES_DE_VERIFICACION:
        # Cada cita, entre comillas, por separado y CON SU PROCEDENCIA. Los
        # textos se leen del registro (`literales_del_umbral`), no de una
        # segunda transcripcion escrita en este archivo: hasta S18 cada
        # umbral llevaba su `texto` copiado a mano y de-acentuado, o sea
        # imposible de encontrar en el PDF con el buscador de un lector.
        citas = "".join(
            f'<p class="fuente">&laquo;{_esc(texto)}&raquo;'
            f'<span class="procedencia-cita">{_esc(rotulo)}</span></p>'
            for rotulo, texto in literales_del_umbral(u))
        f = fundamento_del_umbral(u)
        campos = [
            f"<dt>Por que se hace</dt><dd>{_esc(f.por_que)}<br>"
            f"<b>Si no se hace:</b> {_esc(f.que_pasa_si_no_se_hace)}</dd>",
            f"<dt>Numeral y pagina</dt><dd>{_esc(numeral_del_umbral(u))}</dd>",
            f"<dt>Caracter en la fuente</dt>"
            f"<dd><b>{_esc(caracter_del_umbral(u))}</b></dd>",
            f"<dt>Texto literal de la fuente</dt><dd>{citas}</dd>",
        ]
        if u.get("matiz"):
            campos.append(
                '<dt class="interpretacion">Como lo lee el proyecto</dt>'
                f'<dd class="interpretacion">{_esc(u["matiz"])}</dd>')
        if u.get("transcripcion"):
            campos.append("<dt>Transcripcion (NO es cita: es del proyecto)"
                          "</dt>"
                          f"<dd>{_esc(u['transcripcion'])}</dd>")
        campos.append("<dt>Que hace el proyecto con el</dt>"
                      f"<dd>{_esc(u['aplicacion'])}</dd>")
        partes.append(
            f'<h3><code>{_esc(u["codigo"])}</code> &mdash; '
            f'{_esc(u["que"])}</h3>'
            f'<dl class="acotacion">' + "".join(campos) + "</dl>")
    partes.append(_interpretacion_tabla_10())
    return "".join(partes)


# ===========================================================================
# El anexo de referencias (EXT-8, PC-12)
# ===========================================================================

def pasos_impresos(informe: Any) -> Tuple[Any, ...]:
    """
    Los `PasoDeMemoria` que la memoria IMPRIME como bloque de paso, punto por
    punto y en su orden: la Fase 2, el TW, la hidraulica (la adoptada o la del
    ultimo escalon) y el desarrollo de las verificaciones.

    No es `pasos_del_informe`: aquel recorre TODO lo que la corrida emitio
    --- los escalones descartados, los recubrimientos del cabezal --- porque
    el bloque de discrepancias necesita saber en que citas se apoyo el
    calculo. El anexo, en cambio, existe para lo que los puntos ENLAZAN, y
    una ficha sin ningun enlace que lleve a ella seria una referencia que
    nadie cita.
    """
    vistos: List[Any] = []
    for punto in informe.puntos:
        vistos.extend(traza_clasificacion(punto))
        vistos.extend(traza_licuefaccion(punto))          # --- VE-7 (C4) ---
        vistos.extend(traza_hidrologia(punto))
        vistos.extend(traza_durabilidad(punto))
        tw = traza_tw(punto)
        if tw is not None:
            vistos.append(tw)
        pasos, _ultimo = traza_hidraulica(punto)
        vistos.extend(pasos)
        vistos.extend(p for _c, p in desarrollo_de_verificaciones(punto)
                      if p is not None and not isinstance(p, NoAplica))
        vistos.extend(traza_geometria(punto)[0])          # --- T-6 ---
        # --- T-8 --- la Fase 6 imprime sus pasos como bloque desde T-8.
        vistos.extend(traza_proteccion(punto))
        vistos.extend(traza_cabezal(punto))               # --- T-7a ---
        # --- T-10 --- los de la Fase 8 (`_bloque_estructural`) y los de la
        # Fase 10 tambien se imprimen como bloque, y faltaban aqui: sus
        # enlaces a citas y fundamentos apuntaban a fichas que el anexo no
        # escribia (medido en las corridas de referencia de T-10: 17 anclas
        # rotas, de T-5 y de T-9).
        estructural = getattr(punto, "estructural", None)
        if estructural is not None:
            vistos.extend(estructural.pasos)
        vistos.extend(traza_espaciamiento(punto))
        vistos.extend(traza_metrado(punto))               # --- VE-5 met ---
    for recubrimiento in informe.cabezal.recubrimientos:     # --- T-10 ---
        if getattr(recubrimiento, "paso", None) is not None:
            vistos.append(recubrimiento.paso)
    return tuple(vistos)


# --- T-10 (correcciones, H5) --- El rotulo de la frase que acompaña a un
# umbral en el anexo sigue al CARACTER de su cita: una DEFINICION describe el
# numero, no lo fija; una RECOMENDACION lo recomienda. Decia «Frase que lo
# fija» para todas, y la de V4b describe la practica de agencias ajenas.
ROTULO_DE_LA_FRASE_POR_CARACTER: Dict[str, str] = {
    "exigencia": "Frase que lo fija",
    "recomendacion": "Frase que lo recomienda",
    "permiso": "Frase que lo permite",
    "definicion": "Frase que lo describe",
    "aproximacion": "Frase que lo da como aproximacion",
}


def _rotulo_de_la_frase(cita_id: str) -> str:
    caracter = _reg_M11.cita(cita_id).caracter.value
    return ROTULO_DE_LA_FRASE_POR_CARACTER.get(caracter, "Frase de la fuente")


def _umbrales_del_informe(informe: Any) -> Tuple[Any, ...]:
    """Los umbrales distintos que los pasos impresos de esta corrida contrastan."""
    vistos: Dict[Tuple[Any, ...], Any] = {}
    for paso in pasos_impresos(informe):
        if paso.umbral is not None:
            vistos.setdefault(_clave_de_umbral(paso.umbral), paso.umbral)
    return tuple(vistos[k] for k in sorted(vistos))


def _exigir_anclas_inyectivas(ids: Sequence[str], ancla) -> None:
    por_ancla: Dict[str, str] = {}
    for id_ in ids:
        a = ancla(id_)
        if a in por_ancla and por_ancla[a] != id_:
            raise ValueError(
                f"dos ids distintos comparten el ancla «{a}»: {por_ancla[a]!r} "
                f"y {id_!r}. Un enlace del anexo llevaria al texto equivocado")
        por_ancla[a] = id_


def anexo_referencias(informe: Any) -> str:
    """
    EL ANEXO UNICO de fundamentos, citas y umbrales al que cada paso enlaza.

    Es la decision que el dictamen (PC-12) pidio tomar EXPLICITAMENTE, porque
    tensiona el criterio de salida de la §4.4 del plan v12 --- «la memoria de
    un punto se lee de arriba abajo y se entiende sin abrir el codigo» ---.
    Lo que se decide, y por que:

    - Lo que es DEL PUNTO se queda en el punto: que se calcula, con que
      valores, que sale, contra que valor se compara y el veredicto. Es lo
      que cambia de un punto a otro y lo que el revisor contrasta.
    - Lo que es DEL REGISTRO se imprime UNA vez, aqui, y el punto lo enlaza
      con su numeral en la linea: el argumento del fundamento
      (`Fundamento.por_que`, hasta 2.3 KB), la transcripcion literal de cada
      cita, y el caracter en la fuente y la aplicacion de cada umbral. Medido
      antes de EXT-8, esos tres eran el 44 % de los bytes de la memoria y
      salian repetidos hasta 80 veces en 40 puntos; con el PDF de 200 puntos
      en 6 minutos y 5.7 GB, la repeticion no era gratis.
    - «Sin abrir el codigo» se conserva: todo esta en el MISMO documento, y
      en la salida impresa el enlace es una remision a un anexo, que es la
      forma en que una memoria de calculo cita desde siempre. Lo que NO se
      conserva es «de arriba abajo» en sentido estricto: el revisor que
      quiera la frase literal pasa la pagina. La ficha EXT-8-01 de
      `docs/decisiones_diferidas.md` lo deja escrito.

    Los textos siguen saliendo del registro: `Registro.textos_literales()`
    los verifica contra su pagina, y `test_ninguna_cita_textual_de_la_memoria_
    esta_fuera_del_registro` barre este anexo como barria los pasos. No se
    transcribe nada a mano.

    Se construye a partir de `pasos_impresos`: lo que ESTA memoria imprime
    y enlaza, no el catalogo entero (que para los umbrales ya imprime el
    bloque 0-ter) ni todo lo que la corrida emitio (`pasos_del_informe`,
    que es la base del bloque de discrepancias). Las anclas se comprueban
    inyectivas antes de escribir.
    """
    pasos = pasos_impresos(informe)
    fundamentos = sorted({p.fundamento_id for p in pasos if p.fundamento_id})
    umbrales = _umbrales_del_informe(informe)
    # TODA cita que este anexo enlaza tiene ficha en A.2: las entrecomilladas
    # por los pasos, las que sostienen cada fundamento (A.1 las enlaza) y la
    # que fija cada umbral (A.3 la enlaza). Un `href` sin `id` es un enlace
    # roto que weasyprint reporta y el lector no puede seguir.
    ids_de_citas = {c for p in pasos for c in p.citas_textuales}
    for fid in fundamentos:
        ids_de_citas.update(_reg_M11.fundamento(fid).citas)
    ids_de_citas.update(u.cita_id for u in umbrales)
    # --- T-10 --- las citas del requisito de filtro de la Fase 6, que la
    # memoria enlaza desde el parrafo del filtro (`_fase_6_ampliada`).
    for punto in informe.puntos:
        filtro = getattr(getattr(punto, "proteccion", None), "filtro", None)
        if filtro is not None:
            ids_de_citas.update(getattr(filtro, "citas", ()))
    citas = sorted(ids_de_citas)
    _exigir_anclas_inyectivas(fundamentos, ancla_de_fundamento)
    _exigir_anclas_inyectivas(citas, ancla_de_cita)
    if not (fundamentos or citas or umbrales):
        return ('<div class="nota"><p>Esta corrida no emitio ningun paso con '
                "fundamento, cita o umbral: no hay referencias que anexar."
                "</p></div>")

    partes: List[str] = [
        '<div class="nota"><p>Lo que cada paso de la memoria de un punto '
        "ENLAZA en vez de repetir: el argumento de su fundamento, la frase "
        "literal de cada cita y el caracter de cada umbral. Cada ficha esta "
        "UNA vez; los puntos remiten aqui con su numeral en la linea. Los "
        "textos entrecomillados son literales del registro normativo, "
        "verificados contra su pagina.</p></div>"]

    partes.append("<h3>A.1 Fundamentos</h3>")
    for fid in fundamentos:
        f = _reg_M11.fundamento(fid)
        enlaces = "; ".join(
            _enlace(ancla_de_cita(c), _esc(_cita_como_texto(c))) for c in f.citas)
        partes.append(
            f'<div class="acotacion" id="{_esc(ancla_de_fundamento(fid))}">'
            f"<h4><code>{_esc(fid)}</code> &mdash; {_esc(f.que_paso)}</h4>"
            f"<dl><dt>Por que se hace</dt><dd>{_esc(f.por_que)}</dd>"
            f"<dt>Si no se hace</dt><dd>{_esc(f.que_pasa_si_no_se_hace)}</dd>"
            f"<dt>Verbo y citas</dt><dd><b>{_esc(f.verbo.value)}</b>"
            f"{' &mdash; ' + enlaces if enlaces else ''}</dd></dl></div>")

    partes.append("<h3>A.2 Citas textuales</h3>")
    for cita_id in citas:
        c = _reg_M11.cita(cita_id)
        texto = getattr(c.texto_literal, "texto", "")
        partes.append(
            f'<div class="acotacion" id="{_esc(ancla_de_cita(cita_id))}">'
            f"<h4><code>{_esc(cita_id)}</code></h4>"
            f'<p class="fuente">&laquo;{_esc(texto)}&raquo;'
            f'<span class="procedencia-cita">{_esc(c.como_texto())}</span></p>'
            "</div>")

    if umbrales:
        partes.append("<h3>A.3 Umbrales contrastados</h3>")
    for u in umbrales:
        valor = f"{u.valor} {u.unidad}".strip()
        criterio = ""
        if u.criterio_aplicado:
            criterio = ("<dt>Pasa por el criterio adoptado</dt><dd>"
                        + _enlace(ancla_de_criterio(u.criterio_aplicado),
                                  f"<code>{_esc(u.criterio_aplicado)}</code>")
                        + "</dd>")
        partes.append(
            f'<div class="acotacion" id="{_esc(ancla_de_umbral(u))}">'
            f"<h4>{_esc(u.descripcion)} = {_esc(valor)}</h4>"
            f"<dl><dt>Caracter en la fuente</dt><dd><b>{_esc(u.caracter)}</b></dd>"
            f"<dt>Que hace el proyecto con el</dt><dd>{_esc(u.aplicacion)}</dd>"
            f"<dt>{_esc(_rotulo_de_la_frase(u.cita_id))}</dt><dd>"
            + _enlace(ancla_de_cita(u.cita_id), _esc(_cita_como_texto(u.cita_id)))
            + f"</dd>{criterio}</dl></div>")
    partes.append(anexo_sensibilidad(informe))
    return "".join(partes)


TITULO_ANEXO_SENSIBILIDAD = ("A.4 Criterios [A] adoptados y su sensibilidad, "
                             "por punto")


def criterios_A_por_punto(informe: Any) -> Dict[str, Tuple[str, ...]]:
    """
    --- T-10 --- {clave [A]: (puntos cuyo calculo la nombra, ...)}, leido de
    lo que cada punto emitio: el `criterio_aplicado` de sus verificaciones y
    de los umbrales de sus pasos, y la `clave_criterio` de sus elecciones.
    Es una SELECCION de lo emitido, no una cuenta nueva: el contexto de la
    corrida registra los usos del proceso entero, no por punto.
    """
    por_clave: Dict[str, List[str]] = {}

    def _anota(clave: Optional[str], id_punto: str) -> None:
        if not clave:
            return
        declarado = ca.CRITERIOS.get(clave)
        if declarado is None or declarado.etiqueta != "A":
            return
        puntos = por_clave.setdefault(clave, [])
        if id_punto not in puntos:
            puntos.append(id_punto)

    for p in informe.puntos:
        id_punto = p.punto.id
        for _fase, v in verificaciones_publicadas(p):
            _anota(getattr(v, "criterio_aplicado", None), id_punto)
    for p in informe.puntos:
        id_punto = p.punto.id
        for paso in pasos_del_punto(p):
            umbral = getattr(paso, "umbral", None)
            if umbral is not None:
                _anota(umbral.criterio_aplicado, id_punto)
            for e in getattr(paso, "elecciones", ()):
                _anota(e.clave_criterio, id_punto)
    return {k: tuple(v) for k, v in sorted(por_clave.items())}


def anexo_sensibilidad(informe: Any) -> str:
    """
    --- T-10 --- El anexo de los criterios [A] que la corrida USO, con su
    valor efectivo, su ventana (`sensibilidad`), su modo de resolucion y los
    puntos que lo nombran (T-10 punto 4). NO RECALCULA NADA: la ventana es la
    que la ficha declara, y el barrido que la recorre es PF-3
    (`cli.py --barrido CLAVE=v1,v2`), que no corre dentro de la memoria. La
    ficha entera de cada criterio esta en el bloque 3, enlazada.
    """
    contexto = ContextoCorrida.de(informe)
    usados = [k for k in sorted(contexto.criterios_usados)
              if ca.CRITERIOS.get(k) is not None
              and ca.CRITERIOS[k].etiqueta == "A"]
    if not usados:
        return ""
    por_punto = criterios_A_por_punto(informe)
    recorribles = ca.parametros_sensibilizables(solo_numericos=True)
    filas = [_fila(["<th>Criterio [A]</th>", "<th>Valor efectivo</th>",
                    "<th>Ventana (sensibilidad)</th>", "<th>Resolucion</th>",
                    "<th>Puntos que lo nombran</th>"])]
    for clave in usados:
        c = _criterio_efectivo(clave, contexto)
        ventana = (_valor_legible(c.sensibilidad) if c.sensibilidad else
                   '<span class="pendiente">sin ventana declarada</span>')
        if clave in recorribles:
            ventana += " <small>(barrible: <code>--barrido</code>)</small>"
        filas.append(_fila([
            _td(_enlace(ancla_de_criterio(clave), f"<code>{_esc(clave)}</code>")),
            _td(_valor_legible(c.valor)),
            _td(ventana),
            _td(_esc(modo_de(c.resolucion).value) if c.resolucion is not None
                else VACIO),
            _td(", ".join(_esc(x) for x in por_punto.get(clave, ()))
                or "<i>del proyecto</i>")]))
    return (f"<h3>{_esc(TITULO_ANEXO_SENSIBILIDAD)}</h3>"
            "<p>Las adopciones del proyectista que esta corrida invoco, con la "
            "ventana dentro de la que se eligieron. Se imprime la ventana; el "
            "barrido que la recorre es aparte (PF-3) y no se ejecuta aqui.</p>"
            '<table class="compacta">' + "".join(filas) + "</table>")
