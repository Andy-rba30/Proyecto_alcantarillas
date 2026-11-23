# -*- coding: utf-8 -*-
"""
M11_reporte.memoria
===================
Submodulo de Fase 11 (`M11_reporte`): bloque `memoria` (D3).
"""

from __future__ import annotations

from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    Optional,
)
from src.constantes_normativas import HOMONIMIAS
from src.modelos import (
    ALCANCE_DECLARADO,
    ContextoCorrida,
)

from src.modulos.M11_reporte._base import (
    DIR_PLANTILLAS,
    ETAPA_BLOQUES,
    ETAPA_PUNTO,
    MARCADORES,
    MARCADOR_ANEXO,
    MARCADOR_INDICE,
    NOMBRE_PLANTILLA,
    PlantillaHTML,
    _esc,
    _etiqueta_html,
)
from src.modulos.M11_reporte.trazabilidad import (
    filas_hidrologia,
    trazabilidad,
)
from src.modulos.M11_reporte.tableros import (
    criterios_bloqueantes,
    tableros_pendientes,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
)
from src.modulos.M11_reporte.anclas import (
    indice_de_la_memoria,
)
from src.modulos.M11_reporte.pasos import (
    _IMPRESOS,
    _YaImpreso,
)
from src.modulos.M11_reporte.metrados import (
    bloque_metrados_proyecto,
)
from src.modulos.M11_reporte.bloques_punto import (
    memoria_de_punto,
)
from src.modulos.M11_reporte.proyecto import (
    bloque_cabezal_proyecto,
    fila_resumen,
)
from src.modulos.M11_reporte.sitio_criterios import (
    bloque_criterios,
    bloque_datos_sitio,
    bloque_discrepancias,
)
from src.modulos.M11_reporte.pendientes import (
    bloque_acotaciones,
    bloque_pendientes,
)
from src.modulos.M11_reporte.umbrales_anexos import (
    anexo_referencias,
    bloque_umbrales,
)

# ===========================================================================
# Ensamblado del documento
# ===========================================================================

def bloque_homonimias() -> str:
    """
    Glosario de las palabras que en este expediente significan dos o tres
    cosas distintas y sin relacion, con los dos sentidos llegando a ESTA
    misma memoria.

    No es una nota de estilo. Los cuatro terminos -- «Clase F»,
    «recubrimiento», «TW»/«cota_TW» y «luz»/«diametro» -- se leen mal sin
    ruido: nadie ve un error, se ve un numero plausible en la unidad
    equivocada. El caso extremo es `cota_TW`, que difiere de `TW` en la cota
    de fondo de la salida entera, centenares de metros en este corredor
    (NOR-VOC-01, NOR-VOC-02, NOR-VOC-03, NOR-VOC-04).

    El texto se lee de `constantes_normativas.HOMONIMIAS`, que es donde vive
    una sola vez. La de «Clase F» la imprime ademas M9, pegada a la cadena
    sismica -- que es donde el lector se encuentra el termino --, leyendo la
    MISMA declaracion por `homonimia_como_texto`.
    """
    partes = ['<div class="nota"><p>Cuatro palabras de este expediente '
              "designan mas de una cosa, y en cada caso <b>los dos sentidos "
              "llegan a esta memoria</b>. Leer uno con la definicion del otro "
              "no produce un numero absurdo: produce un numero plausible y "
              "equivocado, que es lo que hace falta declararlo.</p></div>"]
    for termino, sentidos, lectura in HOMONIMIAS:
        partes.append(f"<h3>{_esc(termino)}</h3><ul>")
        partes.extend(f"<li>{_esc(s)}</li>" for s in sentidos)
        partes.append(f"</ul><p><b>Como se resuelve:</b> {_esc(lectura)}</p>")
    return "".join(partes)


# ---------------------------------------------------------------------------
# Alcance de la corrida
# ---------------------------------------------------------------------------

def bloque_alcance(informe: Any) -> str:
    """
    El alcance declarado de la corrida y TODO lo que difirio al expediente.

    Es la pieza que impide que "cerrado" se lea como "expediente completo":
    una corrida a nivel de perfil puede cerrar con etapas enteras diferidas, y
    la memoria tiene que decir cuales y por que. Cada diferimiento se imprime
    con lo que la CLI le adjunto -- clave, etiqueta, concepto y fuente cuando
    la causa es un criterio pendiente; el fundamento textual cuando es una
    fase completa -- de modo que un revisor pueda ir a buscarlo.

    En alcance de expediente el bloque no desaparece: declara que no se
    difirio nada. Que la memoria del expediente afirme "corri el pipeline
    completo" vale tanto como que la de perfil afirme lo contrario.
    """
    alcance = _esc(informe.alcance)
    diferidos = informe.diferidos()

    encabezado = _fila([_td("<b>Alcance declarado de la corrida</b>"),
                        _td(f"<code>{alcance}</code>")])
    conteo = _fila([_td("<b>Etapas diferidas al expediente</b>"),
                    _td(str(len(diferidos)), "num")])
    tabla = ('<table class="compacta">' + encabezado + conteo + "</table>")
    # --- T-10 --- lo que el EXPEDIENTE no hace por decision del dueño: la
    # misma lista que la CLI y el JSON (`modelos.ALCANCE_DECLARADO`), dicha
    # como alcance y no como omision, con su ficha y su simbolo.
    tabla += ('<div class="nota"><p><b>Fuera del alcance del expediente, por '
              "decision declarada:</b></p><ul>"
              + "".join(f"<li>{_esc(a.texto)} (ficha <code>{_esc(a.ficha)}"
                        f"</code> de <code>docs/decisiones_diferidas.md</code>;"
                        f" <code>{_esc(a.simbolo)}</code>).</li>"
                        for a in ALCANCE_DECLARADO)
              + "</ul></div>")

    if not diferidos:
        return tabla + (
            '<div class="nota"><p>Ninguna etapa quedo diferida por alcance: '
            "esta corrida ejecuto el pipeline completo, y el estado del "
            "expediente que declara el bloque 0 se lee sin reservas de "
            "alcance.</p></div>")

    filas = [_fila(["<th>Punto</th>", "<th>Fase</th>", "<th>Etapa diferida</th>",
                    "<th>Fundamento</th>"])]
    for id_punto, b in diferidos:
        donde = _esc(id_punto) if id_punto is not None else "<i>proyecto</i>"
        if b.criterio:
            fundamento = (f"{_etiqueta_html(b.etiqueta)} "
                          f"<code>{_esc(b.criterio)}</code><br>"
                          f"{_esc(b.concepto)}<br>"
                          f"<i>Fuente:</i> {_esc(b.fuente)}")
        else:
            fundamento = _esc(b.mensaje)
        filas.append(_fila([_td(donde), _td(_esc(b.fase)), _td(_esc(b.etapa)),
                            _td(fundamento)]))

    return tabla + '<table class="ancha">' + "".join(filas) + "</table>"


def cargar_plantilla(ruta: Optional[Path] = None) -> PlantillaHTML:
    """Carga la plantilla %% de la memoria."""
    destino = (DIR_PLANTILLAS / NOMBRE_PLANTILLA) if ruta is None else ruta
    if not destino.is_file():
        raise FileNotFoundError(
            f"No se encontro la plantilla «{destino.name}».\n"
            f"Debe estar en: {destino.parent}"
        )
    return PlantillaHTML(destino.read_text(encoding="utf-8"))


def _exigir_que_la_plantilla_no_pierda_contenido(
        plantilla: PlantillaHTML, valores: Dict[str, str],
        ruta: Optional[Path]) -> None:
    """
    La otra mitad del contrato de marcadores, y la que faltaba (SIS-B-06).

    `substitute` ya revienta cuando la plantilla pide un marcador que M11 no
    entrega. La direccion contraria --- M11 calcula contenido y la plantilla
    no lo imprime --- no se queja de nada: `substitute` ignora los valores
    sobrantes. El comentario de contrato de este mismo modulo lo dice desde
    hace tiempo: «un marcador que M11 calcula y la plantilla no imprime es
    contenido de la memoria que se pierde en silencio». No habia guardia.

    Se comprueba sobre el contenido REAL de esta corrida, no sobre la lista de
    marcadores: un marcador cuyo valor sale vacio no es contenido perdido, es
    contenido que no habia. Asi la guardia no obliga a ninguna plantilla a
    imprimir bloques vacios, y salta exactamente cuando hay algo que decir y
    la hoja no tiene donde decirlo.

    Es `ValueError` y no un aviso impreso porque no hay donde imprimirlo: el
    problema es justamente que falta el hueco. Y no es un error del
    expediente sino de la plantilla que se le paso al script, que es la misma
    clase que la plantilla ausente.
    """
    presentes = {m.group("named") or m.group("braced")
                 for m in plantilla.pattern.finditer(plantilla.template)}
    perdidos = sorted(clave for clave, texto in valores.items()
                      if clave not in presentes and str(texto).strip())
    if not perdidos:
        return
    nombre = ruta.name if ruta is not None else NOMBRE_PLANTILLA
    detalle = ", ".join(
        f"{clave} ({len(valores[clave])} caracteres)" for clave in perdidos)
    raise ValueError(
        f"La plantilla «{nombre}» no imprime {len(perdidos)} bloque(s) que "
        f"esta corrida SI produjo: {detalle}. Eso es contenido de la memoria "
        "que se perderia en silencio, que es lo que el contrato de marcadores "
        "de este modulo prohibe (SIS-B-06). Las dos plantillas del proyecto "
        "llevan los mismos marcadores a proposito: quien decide que va dentro "
        "de cada bloque es el ALCANCE de la corrida, no la plantilla.")


def _resumen_expediente(informe: Any) -> str:
    """
    Las cifras que resumen la corrida, bajo el encabezado. Salen de
    `Informe.resumen`, la MISMA cuenta que imprimen la CLI y la GUI
    (EXT-G-02): aqui no se cuenta nada. «Etapas bloqueadas» son las reales;
    las diferidas por alcance van en su propia fila y no cuentan para el
    cierre.
    """
    r = informe.resumen()
    filas = [
        _fila([_td("<b>Puntos del expediente</b>"),
               _td(str(r.puntos), "num")]),
        _fila([_td("<b>Puntos dimensionados</b>"),
               _td(str(r.dimensionados), "num")]),
        _fila([_td("<b>Verificaciones incumplidas</b>"),
               _td(str(r.incumplidas), "num")]),
        _fila([_td("<b>Verificaciones con aviso</b> (indicador disparado; "
                   "el diseño no se detiene)"),
               _td(str(r.con_aviso), "num")]),
        _fila([_td("<b>Etapas bloqueadas</b>"),
               _td(str(r.bloqueadas), "num")]),
        _fila([_td("<b>Diferidas por alcance</b> (no cuentan para el cierre)"),
               _td(str(r.diferidas), "num")]),
    ]
    return '<table class="compacta">' + "".join(filas) + "</table>"


def estado_del_expediente(informe: Any, donde_el_detalle: str) -> str:
    """
    --- T-12 (H7 de su auditoria) --- La celda «Estado del expediente», UNA
    regla para las dos vistas de la memoria: «cerrado» o «NO cierra» sale de
    `Informe.cerrado` y nada mas; cada vista dice donde esta el detalle.
    """
    if informe.cerrado:
        return ('<span class="cumple">cerrado</span> &mdash; todos los puntos '
                "dimensionados, sin etapas bloqueadas y sin verificaciones "
                "incumplidas")
    return ('<span class="incumple">NO cierra</span> &mdash; hay etapas '
            "bloqueadas, puntos sin dimensionar o verificaciones "
            f"incumplidas; el detalle esta en {donde_el_detalle}")


def memoria_html(informe: Any, *, proyecto: str = "",
                 subtitulo: str = "", ruta_plantilla: Optional[Path] = None,
                 ruta_hoja: Optional[Path] = None,
                 progreso: Optional[Callable[[str, int, int], None]] = None) -> str:
    """
    El HTML completo de la memoria de calculo (Fase 11), como UNA cadena.

    `informe` es el `Informe` que produce la CLI. M11 no recalcula nada: si un
    dato no esta en el informe, la memoria lo declara ausente.

    Es `memoria_html_por_partes` unida: la construccion vive alli, por
    streaming (EXT-8, PC-12), y esta puerta existe para quien necesita la
    cadena entera --- weasyprint, los tests ---.
    """
    return "".join(memoria_html_por_partes(
        informe, proyecto=proyecto, subtitulo=subtitulo,
        ruta_plantilla=ruta_plantilla, ruta_hoja=ruta_hoja, progreso=progreso))


def memoria_html_por_partes(
        informe: Any, *, proyecto: str = "", subtitulo: str = "",
        ruta_plantilla: Optional[Path] = None, ruta_hoja: Optional[Path] = None,
        progreso: Optional[Callable[[str, int, int], None]] = None,
) -> Iterator[str]:
    """
    La memoria de calculo por TROZOS, en el orden del documento (EXT-8).

    POR QUE POR STREAMING. `memoria_html` armaba un diccionario con los
    bloques enteros --- la memoria de los puntos, unida, era uno solo --- y
    despues `Template.substitute` producia una segunda copia: medido, el pico
    de RAM al construir era 4x el tamano del documento (PC-12). Aqui la
    plantilla se recorre marcador a marcador y cada trozo se entrega en
    cuanto existe; `exportar_html` los escribe al archivo sin unirlos, y la
    memoria de cada punto se genera cuando le toca, con `progreso` avisando.

    LO QUE SI SE CALCULA ENTERO ANTES DEL PRIMER TROZO: los bloques
    generales (criterios, pendientes, acotaciones, umbrales, discrepancias y
    el anexo, que recorre los pasos de todos los puntos). Son de tamano
    acotado --- no crecen con N como la memoria de los puntos --- y la guardia
    de la plantilla (SIS-B-06) necesita saber cuales salieron vacios antes
    de empezar. Por eso `progreso` emite `ETAPA_BLOQUES` ANTES que el primer
    `ETAPA_PUNTO`: es el orden real de construccion.

    EL CONTRATO DE MARCADORES NO SE RELAJA. Los dos chequeos de siempre
    siguen: el conjunto de marcadores que este modulo entrega tiene que ser
    exactamente `MARCADORES` (o el test de la plantilla no vale), y un bloque
    que esta corrida SI produjo tiene que tener hueco en la plantilla
    (`_exigir_que_la_plantilla_no_pierda_contenido`, SIS-B-06). Para el
    segundo, la memoria de los puntos se representa por si HAY puntos, sin
    construirla: construirla dos veces es lo que se quiere evitar.

    Un marcador que la plantilla pide y este modulo no entrega revienta con
    `KeyError`, como `substitute`: nunca se imprime el marcador.
    """
    tableros = tableros_pendientes(ruta_hoja)
    bloqueantes = criterios_bloqueantes(informe)
    # La foto de la corrida: de aqui sale TODO el estado que la memoria
    # imprime (EXT-4). Un informe sin ella no se puede renderizar.
    contexto = ContextoCorrida.de(informe)
    traza = trazabilidad(Path(informe.csv), contexto,
                         generado_utc=informe.generado,
                         hidrologia=getattr(informe, "hidrologia", None))

    estado = estado_del_expediente(informe, "los bloques 1 y 4")

    n_puntos = len(informe.puntos)
    # La plantilla se carga ANTES de los valores: el indice se deriva de su
    # texto (E-B, E21), y la guardia de contenido de abajo la necesita igual.
    plantilla = cargar_plantilla(ruta_plantilla)

    def _memorias_punto() -> Iterator[str]:
        # --- T-10 --- un registro de lo ya impreso para TODO el documento
        # (`_YaImpreso`), activo solo mientras se arma cada punto.
        impresos = _YaImpreso()
        for i, p in enumerate(informe.puntos, start=1):
            impresos.punto = p.punto.id
            token = _IMPRESOS.set(impresos)
            try:
                html_punto = memoria_de_punto(p)
            finally:
                _IMPRESOS.reset(token)
            yield html_punto
            if progreso is not None:
                progreso(ETAPA_PUNTO, i, n_puntos)
        # --- T-10 --- la Fase 9 del PROYECTO, detras de los puntos y dentro
        # de la seccion 1: la cadena sismica, K_AE y los recubrimientos que
        # la CLI y el JSON imprimian y la memoria no.
        yield bloque_cabezal_proyecto(informe)
        # --- VE-5 met --- y la Fase 11 del proyecto: el cuadro de
        # compatibilidad rasante-alcantarilla y los totales por partida.
        yield bloque_metrados_proyecto(informe)

    valores = {
        "proyecto": _esc(proyecto) or "(proyecto no declarado)",
        "subtitulo": _esc(subtitulo),
        "version_hoja_ruta": _esc(traza.version_hoja_ruta),
        "hoja_ruta_archivo": _esc(traza.hoja_ruta.name),
        "hoja_ruta_sha1": _esc(traza.hoja_ruta_sha1),
        "csv_ruta": _esc(traza.csv),
        "csv_sha1": _esc(traza.csv_sha1),
        "filas_hidrologia": filas_hidrologia(traza),
        "criterios_version": _esc(traza.criterios_version),
        "criterios_fecha": _esc(traza.criterios_fecha),
        "criterios_sha1": _esc(traza.criterios_sha1),
        "generado_local": _esc(traza.generado_local),
        "generado_utc": _esc(traza.generado_utc),
        "estado_expediente": estado,
        "resumen_expediente": _resumen_expediente(informe),
        # Un TESTIGO, no el bloque: dice si hay contenido (para la guardia de
        # la plantilla) y el bloque real sale de `_memorias_punto`, por
        # trozos, cuando la plantilla llega a su marcador.
        "memorias_punto": "hay puntos" if n_puntos else "",
        "filas_resumen": "".join(fila_resumen(p)
                                 for p in informe.puntos),
        "bloque_datos_sitio": bloque_datos_sitio(contexto, solo_usados=True,
                                                 proyecto=proyecto),
        "bloque_criterios": bloque_criterios(contexto, solo_usados=True),
        "bloque_pendientes": bloque_pendientes(tableros, bloqueantes, contexto,
                                              alcance=informe.alcance),
        "bloque_alcance": bloque_alcance(informe),
        "bloque_acotaciones": bloque_acotaciones(contexto,
                                                alcance=informe.alcance),
        "bloque_umbrales": bloque_umbrales(),
        "bloque_homonimias": bloque_homonimias(),
        "bloque_discrepancias": bloque_discrepancias(informe),
        MARCADOR_ANEXO: anexo_referencias(informe),
        MARCADOR_INDICE: indice_de_la_memoria(plantilla.template, informe),
    }
    if progreso is not None:
        progreso(ETAPA_BLOQUES, 1, 1)
    if set(valores) != set(MARCADORES):
        diferencia = set(valores).symmetric_difference(MARCADORES)
        raise ValueError(
            f"El contrato de marcadores no cuadra: {sorted(diferencia)}. "
            "`MARCADORES` y el diccionario de `memoria_html` tienen que decir "
            "lo mismo, porque el test de la plantilla se apoya en esa lista."
        )
    _exigir_que_la_plantilla_no_pierda_contenido(plantilla, valores,
                                                 ruta_plantilla)
    texto = plantilla.template
    pos = 0
    for m in plantilla.pattern.finditer(texto):
        nombre = m.group("named") or m.group("braced")
        if nombre is None:
            if m.group("escaped") is not None:
                yield texto[pos:m.start()] + plantilla.delimiter
                pos = m.end()
                continue
            raise ValueError(
                f"marcador invalido en la plantilla en la posicion {m.start()}")
        yield texto[pos:m.start()]
        pos = m.end()
        if nombre == "memorias_punto":
            yield from _memorias_punto()
            continue
        if nombre not in valores:
            # Como `substitute`: lo que la plantilla pide y no existe revienta.
            raise KeyError(nombre)
        yield valores[nombre]
    yield texto[pos:]
