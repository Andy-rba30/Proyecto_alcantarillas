# -*- coding: utf-8 -*-
"""
M11_reporte.resumida
====================
Submodulo de Fase 11 (`M11_reporte`): bloque `resumida` (D3).
"""

from __future__ import annotations

from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)
from src.modelos import ContextoCorrida

from src.modulos.M11_reporte._base import (
    DIR_PLANTILLAS,
    VACIO,
    _esc,
    _etiqueta_html,
    _valor_legible,
)
from src.modulos.M11_reporte.trazabilidad import (
    filas_hidrologia,
    trazabilidad,
)
from src.modulos.M11_reporte.tableros import (
    criterios_bloqueantes,
)
from src.modulos.M11_reporte.tablas_diseno import (
    AVISO_SIN_DIMENSIONAR,
    _fila,
    _filas_combinacion_adoptada,
    _tabla_bloqueos,
    _td,
)
from src.modulos.M11_reporte.trazas import (
    verificaciones_publicadas,
)
from src.modulos.M11_reporte.anclas import (
    ancla_de_punto,
)
from src.modulos.M11_reporte.pasos import (
    SIN_VERIFICACIONES,
    _filas_verificaciones,
)
from src.modulos.M11_reporte.proyecto import (
    fila_resumen,
)
from src.modulos.M11_reporte.sitio_criterios import (
    _criterio_efectivo,
    datos_sitio_resumidos,
)
from src.modulos.M11_reporte.umbrales_anexos import (
    criterios_A_por_punto,
)
from src.modulos.M11_reporte.memoria import (
    _exigir_que_la_plantilla_no_pierda_contenido,
    _resumen_expediente,
    bloque_alcance,
    cargar_plantilla,
    estado_del_expediente,
)

# ===========================================================================
# --- T-12 --- La memoria RESUMIDA: la vista para imprimir
# ===========================================================================
# DOS VISTAS DE LA MISMA CORRIDA (decision del dueño del 2026-11-13, ficha
# T12-04 de docs/decisiones_diferidas.md). La memoria COMPLETA de arriba es el
# anexo digital: cada paso con su formula, su sustitucion, su cita y su
# veredicto, y por punto mas de cien KB (techos de `test_ext8`). La RESUMIDA
# es lo que se imprime: por punto, el resultado, los veredictos, los avisos,
# los criterios [A] que nombra y lo que lo detuvo; para el proyecto, el
# encabezado de trazabilidad, el alcance, el cuadro resumen y los criterios
# pendientes. Las dos reglas que la hacen defendible:
#
#   1. SALE DEL MISMO `Informe`, y por eso del mismo `ContextoCorrida`: las
#      mismas huellas (CSV, criterios, hoja de ruta) y la misma hora de
#      corrida que la completa, que la resumida imprime en su encabezado. La
#      CLI escribe las dos en la MISMA invocacion (`--html` y
#      `--html-resumida`).
#   2. NO TIENE FORMATEADORES PROPIOS PARA LOS NUMEROS: cada fila numerica es
#      la de la completa (`_filas_combinacion_adoptada`,
#      `_filas_verificaciones`, `fila_resumen`, `_tabla_bloqueos`,
#      `bloque_alcance`, `_resumen_expediente`, `_valor_legible` sobre el
#      valor efectivo del contexto), de modo que no puede publicar un numero
#      que la completa no tenga. `tests/test_t12_entregable.py` lo comprueba
#      sobre el texto de las dos, por punto y en total. Sin aritmetica: es
#      una SELECCION de lo que la completa ya imprime.
NOMBRE_PLANTILLA_RESUMIDA = "memoria_resumida.html"
MARCADORES_RESUMIDA: Tuple[str, ...] = (
    "proyecto", "subtitulo",
    "version_hoja_ruta", "hoja_ruta_archivo", "hoja_ruta_sha1",
    "csv_ruta", "csv_sha1",
    "filas_hidrologia",
    "criterios_version", "criterios_fecha", "criterios_sha1",
    "generado_local", "generado_utc",
    "estado_expediente", "resumen_expediente", "bloque_alcance",
    "datos_sitio_resumidos",
    "filas_resumen", "resumenes_punto", "pendientes_resumidos",
    "memoria_completa",
)
PREFIJO_ANCLA_RESUMEN = "resumen-"
TITULO_RESUMEN_RESULTADO = "Resultado: la combinacion adoptada"
TITULO_RESUMEN_VERIFICACIONES = "Verificaciones y su veredicto"
TITULO_RESUMEN_AVISOS = "Avisos del punto"
TITULO_RESUMEN_CRITERIOS = "Criterios [A] que nombra este punto"
SIN_AVISOS = "Sin avisos."


def _criterios_A_del_punto(id_punto: str, por_punto: Dict[str, Tuple[str, ...]],
                           contexto: Any) -> str:
    """
    Los criterios [A] que el calculo de ESTE punto nombra
    (`criterios_A_por_punto`), con su valor efectivo y su ventana, leidos
    del contexto de la corrida y formateados como en el anexo A.4 de la
    completa. Un criterio que el punto nombra y la corrida no registro como
    usado (y que por eso el anexo A.4 no imprime) sale sin valor y remite a
    la completa: la resumida no publica lo que la completa no lleva.
    """
    claves = [k for k, puntos in por_punto.items() if id_punto in puntos]
    if not claves:
        return ("<p>Este punto no nombra ningun criterio [A] en sus "
                "verificaciones ni en sus pasos.</p>")
    usados = set(contexto.criterios_usados)
    filas = [_fila(["<th>Criterio [A]</th>", "<th>Valor efectivo</th>",
                    "<th>Ventana (sensibilidad)</th>"])]
    for clave in claves:
        if clave not in usados:
            filas.append(_fila([_td(f"<code>{_esc(clave)}</code>"),
                                _td("ver la memoria completa"), _td(VACIO)]))
            continue
        c = _criterio_efectivo(clave, contexto)
        ventana = (_valor_legible(c.sensibilidad) if c.sensibilidad else
                   '<span class="pendiente">sin ventana declarada</span>')
        filas.append(_fila([_td(f"<code>{_esc(clave)}</code>"),
                            _td(_valor_legible(c.valor)), _td(ventana)]))
    return '<table class="compacta">' + "".join(filas) + "</table>"


def resumen_de_punto(informe: Any, por_punto: Dict[str, Tuple[str, ...]],
                     contexto: Any) -> str:
    """
    --- T-12 --- El bloque de UN punto en la memoria resumida: su encabezado
    (el mismo de la completa), la combinacion adoptada, la tabla de
    verificaciones con su veredicto, los avisos (`InformePunto.avisos()`, la
    misma lista que la CLI y el JSON), las etapas bloqueadas y los criterios
    [A] que nombra. El desarrollo (pasos, formulas, citas, tablas del
    cabezal) esta en la memoria completa, bajo el mismo identificador del
    punto. Ningun texto fijo de este bloque lleva un numero: los numeros son
    los de la completa.
    """
    punto = informe.punto
    clase = "punto" if informe.dimensionado else "punto sin-cerrar"
    estado = "dimensionado" if informe.dimensionado else "sin dimensionar"
    partes = [
        f'<div class="{clase}" id="{PREFIJO_ANCLA_RESUMEN}'
        f'{ancla_de_punto(punto.id)}">',
        f"<h3>{_esc(punto.id)} &nbsp;|&nbsp; progresiva "
        f"{_esc(punto.progresiva_display)} &nbsp;|&nbsp; Familia "
        f"{_esc(punto.familia.value)} &nbsp;|&nbsp; {estado}</h3>",
        f"<h4>{_esc(TITULO_RESUMEN_RESULTADO)}</h4>",
    ]
    if informe.dimensionado:
        partes.append('<table class="compacta">'
                      + "".join(_filas_combinacion_adoptada(informe))
                      + "</table>")
    else:
        partes.append(AVISO_SIN_DIMENSIONAR)
    partes.append(f"<h4>{_esc(TITULO_RESUMEN_VERIFICACIONES)}</h4>")
    verificaciones = verificaciones_publicadas(informe)
    if verificaciones:
        partes.append('<table class="compacta">'
                      + "".join(_filas_verificaciones(
                          verificaciones, remision_acotacion=False))
                      + "</table>")
    else:
        partes.append(SIN_VERIFICACIONES)
    partes.append(f"<h4>{_esc(TITULO_RESUMEN_AVISOS)}</h4>")
    avisos: List[str] = []
    for aviso in informe.avisos():
        texto = _esc(aviso)
        if texto not in avisos:
            avisos.append(texto)
    partes.append("<ul>" + "".join(f"<li>{t}</li>" for t in avisos) + "</ul>"
                  if avisos else f"<p>{_esc(SIN_AVISOS)}</p>")
    partes.append(_tabla_bloqueos(informe.bloqueos))
    partes.append(f"<h4>{_esc(TITULO_RESUMEN_CRITERIOS)}</h4>")
    partes.append(_criterios_A_del_punto(punto.id, por_punto, contexto))
    partes.append(
        '<p class="lead">El desarrollo de este punto &mdash; pasos, formulas '
        "sustituidas, citas, tablas del cabezal &mdash; esta en la memoria "
        f"completa, bloque <code>{_esc(punto.id)}</code>.</p></div>")
    return "".join(partes)


def pendientes_resumidos(informe: Any) -> str:
    """
    --- T-12 --- Los criterios sin valor que detuvieron (o difirieron) una
    etapa de esta corrida, en una tabla: los mismos `CriterioBloqueante` que
    la seccion 4 de la completa imprime en fichas.
    """
    bloqueantes = criterios_bloqueantes(informe)
    if not bloqueantes:
        return ("<p>Ninguno: ningun criterio sin valor se invoco en esta "
                "corrida.</p>")
    filas = [_fila(["<th>Criterio</th>", "<th>Concepto</th>",
                    "<th>Puntos afectados</th>", "<th>En esta corrida</th>"])]
    for c in bloqueantes:
        puntos = ", ".join(c.puntos) if c.puntos else "proyecto (Fase 9)"
        filas.append(_fila([
            _td(f"{_etiqueta_html(c.etiqueta)} <code>{_esc(c.clave)}</code>"),
            _td(_esc(c.concepto)), _td(_esc(puntos)),
            _td("diferido por alcance" if c.diferido else
                '<span class="incumple">detiene</span>')]))
    return '<table class="ancha">' + "".join(filas) + "</table>"


# --- UI-5 (decision del dueño del 2026-11-15, ficha UI2-01 b) --- LO QUE EL
# ENCABEZADO PRUEBA DE LAS DOS VISTAS, y solo eso. La resumida se escribe en
# tres contextos y la frase tiene que ser cierta en los tres: la CLI con las
# dos vistas en una invocacion (el mismo informe: el encabezado coincide), la
# resumida HTML de la ventana (el mismo informe que la completa de la
# ventana: coincide) y la resumida PDF del proceso hijo, que VUELVE A CORRER
# la obra (ficha EXT-8-02: otra hora, y las huellas de los archivos tal como
# esten al exportar): ahi no tiene por que coincidir con la completa de la
# ventana, y hasta UI-5 la memoria decia que si. Y la implicacion vale en UN
# sentido (revision de UI-5, H1): de la misma corrida, el encabezado
# coincide, y uno distinto prueba que son dos; uno IGUAL no prueba que sea la
# misma, porque la hora va al segundo y las huellas no cubren todo lo que la
# corrida leyo (lo declarado para ella, los datos externos, los de sitio):
# dos corridas con un valor declarado distinto en el mismo segundo llevan el
# mismo encabezado y dimensionan distinto. Y solo cuenta lo que el
# encabezado toma de la CORRIDA (verificacion de UI-5, N1): la hora UTC y las
# huellas del `ContextoCorrida`; la huella de la hoja de ruta y la fecha de
# generacion las lee `trazabilidad` al exportar cada vista. Los tests y la
# ventana la leen de aqui; no se transcribe dos veces.
REMISION_COMO_COMPROBARLO = (
    "Si las dos vistas salen de la MISMA corrida, coinciden en su encabezado "
    "de trazabilidad la hora UTC de la corrida y las huellas del CSV, de los "
    "criterios y, con hidrologia, de las cuencas y de la estacion. Si alguna "
    "de esas difiere, son dos corridas, y lo que dice una no se lee en la "
    "otra; que coincidan no prueba que sean la misma, porque la hora va al "
    "segundo y esas huellas no cubren todo lo que la corrida leyo (lo "
    "declarado para ella, los datos externos, los de sitio). La huella de la "
    "hoja de ruta y la fecha de generacion se leen al exportar cada vista y "
    "no cuentan para esto. De la misma corrida, ningun numero de esta vista "
    "falta en aquella.")


def _remision_a_la_completa(nombre_completa: Optional[str]) -> str:
    """
    La frase que ata la resumida a SU memoria completa.

    Con `nombre_completa` (la CLI escribio las dos en la misma invocacion)
    nombra el archivo y dice que salen del MISMO informe, que ahi es cierto.
    Sin el (la resumida HTML de la ventana, la resumida PDF del proceso hijo,
    la CLI con solo `--html-resumida` o `--pdf-resumida`) no nombra ninguna
    puerta ni promete el encabezado: dice que la completa se exporta aparte.
    En los dos casos dice lo que el encabezado prueba de las dos vistas, y
    solo eso (`REMISION_COMO_COMPROBARLO`). Hasta UI-5 mandaba a `--html` o `--pdf`
    «en la MISMA invocacion» y afirmaba que el encabezado «es el mismo en las
    dos», falso entre la completa de la ventana y la resumida del hijo
    (ficha UI2-01 b).
    """
    if nombre_completa:
        donde = (f"se escribio en <code>{_esc(nombre_completa)}</code>, en la "
                 "MISMA invocacion que esta: las dos salen del MISMO informe")
    else:
        donde = "no se escribio con esta vista: se exporta aparte"
    return (
        '<div class="nota"><p><b>Esta es la memoria RESUMIDA, para imprimir.'
        "</b> La memoria COMPLETA &mdash; el anexo digital, con el desarrollo "
        "de cada paso, sus formulas sustituidas, sus citas literales, los "
        "criterios declarados con su justificacion y su fuente, las "
        "acotaciones, los umbrales y las discrepancias &mdash; "
        f"{donde}. {REMISION_COMO_COMPROBARLO}</p></div>")


def memoria_resumida_html(informe: Any, *, proyecto: str = "",
                          subtitulo: str = "",
                          nombre_completa: Optional[str] = None,
                          ruta_plantilla: Optional[Path] = None) -> str:
    """
    --- T-12 --- La memoria RESUMIDA de la corrida, como una cadena (ver el
    bloque de arriba). `nombre_completa` es el archivo de la memoria
    completa que la misma invocacion escribe, para que la resumida remita a
    el; sin el, dice que se exporta aparte (`_remision_a_la_completa`,
    UI-5). Mismo contrato de
    marcadores que la completa, en las dos direcciones: un marcador que la
    plantilla pide y aqui no se entrega revienta (`substitute`), y uno que
    aqui se entrega y la plantilla no imprime es `ValueError`.
    """
    contexto = ContextoCorrida.de(informe)
    traza = trazabilidad(Path(informe.csv), contexto,
                         generado_utc=informe.generado,
                         hidrologia=getattr(informe, "hidrologia", None))
    estado = estado_del_expediente(informe, "cada punto y en los pendientes")
    por_punto = criterios_A_por_punto(informe)
    destino = ((DIR_PLANTILLAS / NOMBRE_PLANTILLA_RESUMIDA)
               if ruta_plantilla is None else ruta_plantilla)
    plantilla = cargar_plantilla(destino)
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
        "bloque_alcance": bloque_alcance(informe),
        "datos_sitio_resumidos": datos_sitio_resumidos(contexto,
                                                       proyecto=proyecto),
        "filas_resumen": "".join(fila_resumen(p) for p in informe.puntos),
        "resumenes_punto": "".join(resumen_de_punto(p, por_punto, contexto)
                                   for p in informe.puntos),
        "pendientes_resumidos": pendientes_resumidos(informe),
        "memoria_completa": _remision_a_la_completa(nombre_completa),
    }
    if set(valores) != set(MARCADORES_RESUMIDA):
        diferencia = set(valores).symmetric_difference(MARCADORES_RESUMIDA)
        raise ValueError(
            f"El contrato de marcadores de la resumida no cuadra: "
            f"{sorted(diferencia)}")
    _exigir_que_la_plantilla_no_pierda_contenido(plantilla, valores, destino)
    return plantilla.substitute(valores)
