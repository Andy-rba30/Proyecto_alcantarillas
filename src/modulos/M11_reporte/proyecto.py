# -*- coding: utf-8 -*-
"""
M11_reporte.proyecto
====================
Submodulo de Fase 11 (`M11_reporte`): bloque `proyecto` (D3).
"""

from __future__ import annotations

from typing import (
    Any,
    List,
    Optional,
)
from src.constantes_normativas import RECUBRIMIENTO_MP_PISO_MM

from src.modulos.M11_reporte._base import (
    FMT_2,
    FMT_4,
    VACIO,
    _esc,
    _etiqueta_html,
    _num,
    rotulo_norma_producto,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _tabla_bloqueos,
    _td,
)
from src.modulos.M11_reporte.pasos import (
    bloque_paso,
)

TITULO_CABEZAL_PROYECTO = ("Fase 9 del proyecto: cadena sismica, empuje "
                           "sismico, recubrimientos y notas")
ANCLA_CABEZAL_PROYECTO = "fase-9-proyecto"


def bloque_cabezal_proyecto(informe: Any) -> str:
    """
    --- T-10 --- Lo que la Fase 9 deja en el PROYECTO (`InformeCabezal`) y
    que la CLI (`cli._lineas_cabezal`) y el JSON (`cli._cabezal_json`)
    imprimian desde hace tiempo y la memoria no: la cadena sismica eslabon
    por eslabon --- con la etiqueta, el origen, el criterio y la CONDICION
    de cada uno, que es lo que la hace revisable ---, el K_AE y el K_A de
    Mononobe-Okabe, los cabezales por punto, los recubrimientos con la
    cadena de su lado AASHTO y su paso, las cuantias minimas, las notas del
    proyecto y sus bloqueos. Una fuente (el objeto), tres vistas. Formato:
    los numeros vienen del objeto que M9 emitio.

    Vacio si la corrida no llego a la Fase 9 del proyecto (perfil): lo dice
    entonces el bloque de alcance.
    """
    c = getattr(informe, "cabezal", None)
    if c is None or not (c.cadena is not None or c.mononobe_okabe is not None
                         or c.por_punto or c.recubrimientos or c.cuantias
                         or c.notas or c.bloqueos):
        return ""
    partes: List[str] = [
        f'<h3 id="{ANCLA_CABEZAL_PROYECTO}">{_esc(TITULO_CABEZAL_PROYECTO)}'
        "</h3>"]
    # --- T-10 (correcciones, H1) --- cada dato en una FILA con su clave en
    # la primera columna, para que el censo lo localice por clave y no por
    # texto libre.
    if c.por_punto:
        filas = [_fila(["<th>Punto</th>", "<th>Entrada</th>",
                        "<th>Salida</th>", "<th>H_c entrada (m)</th>",
                        "<th>H_c salida (m)</th>"])]
        for x in c.por_punto:
            filas.append(_fila([
                _td(_esc(x.id_punto)), _td(_esc(x.entrada.tipo)),
                _td(_esc(x.salida.tipo)),
                _td(_num(x.entrada.altura_total), "num"),
                _td(_num(x.salida.altura_total), "num")]))
        partes.append("<p>Cabezales por punto (la geometria de cada uno va "
                      "con su punto):</p>"
                      '<table class="compacta">' + "".join(filas) + "</table>")
    k = c.cadena
    if k is not None:
        filas = [_fila(["<th>Eslabon</th>", "<th>Valor</th>",
                        "<th>Etiqueta</th>", "<th>Concepto</th>",
                        "<th>Origen</th>", "<th>Condicion de su fuente</th>"])]
        for e in k.pasos:
            criterio = (f" (<code>{_esc(e.criterio)}</code>)"
                        if getattr(e, "criterio", None) else "")
            filas.append(_fila([
                _td(f"<b>{_esc(e.simbolo)}</b>"),
                _td(_num(e.valor), "num"),
                _td(_etiqueta_html(e.etiqueta)),
                _td(_esc(e.concepto)),
                _td(_esc(e.origen) + criterio),
                _td(_esc(e.condicion) if e.condicion else VACIO)]))
        partes.append(
            f"<p><b>Cadena sismica</b> (num. {_esc(k.numeral)}): PGA "
            f"{_num(k.PGA, FMT_2)} g &rarr; F_pga {_num(k.F_pga, FMT_2)} "
            f"&rarr; A_s {_num(k.A_s, FMT_2)} g &rarr; k_h0 "
            f"{_num(k.k_h0, FMT_2)} &rarr; factor del muro "
            f"{_num(k.factor_muro, FMT_2)} &rarr; k_h {_num(k.k_h, FMT_2)}; "
            f"k_v {_num(k.k_v, FMT_2)}. Filas de sitio leidas: "
            f"{_esc(', '.join(k.clases_de_sitio))}; cimentacion en roca: "
            f"{'si' if k.cimentacion_en_roca else 'no'}.</p>"
            '<table class="compacta">' + "".join(filas) + "</table>")
    mo = c.mononobe_okabe
    if mo is not None:
        partes.append(
            "<p>Mononobe-Okabe del proyecto:</p>"
            '<table class="compacta">'
            + _fila(["<th>Coeficiente</th>", "<th>Valor</th>"])
            + _fila([_td("K_AE"), _td(_num(mo.K_AE), "num")])
            + _fila([_td("K_A"), _td(_num(mo.K_A), "num")]) + "</table>")
    if c.recubrimientos:
        filas = [_fila(["<th>Condicion</th>", "<th>Adoptado (mm)</th>",
                        "<th>Gobierna</th>", "<th>E.060 (mm)</th>",
                        "<th>AASHTO (mm)</th>", "<th>Fila AASHTO</th>",
                        "<th>Categoria de acero</th>",
                        "<th>De tabla (mm) &times; factor a/c</th>",
                        "<th>Factor por a/c, de donde</th>"])]
        for r in c.recubrimientos:
            piso = (f" (piso de {_num(RECUBRIMIENTO_MP_PISO_MM, FMT_2)} mm "
                    "aplicado)" if r.piso_aplicado else "")
            filas.append(_fila([
                _td(_esc(r.condicion)), _td(_num(r.adoptado_mm, FMT_2), "num"),
                _td(f"{_esc(r.origen)} ({_esc(r.numeral)})"),
                _td(_num(r.e060_mm, FMT_2), "num"),
                _td(_num(r.aashto_mm, FMT_2) + piso, "num"),
                _td(_esc(r.situacion)), _td(_esc(r.categoria)),
                _td(f"{_num(r.tabulado_mm, FMT_2)} &times; "
                    f"{_num(r.factor_ac, FMT_2)}", "num"),
                _td(_esc(r.origen_factor))]))
        partes.append("<p>Recubrimientos de diseño (rige el mayor de AASHTO y "
                      "E.060):</p>"
                      '<table class="compacta">' + "".join(filas) + "</table>")
        for r in c.recubrimientos:
            if r.requisitos is not None:
                q = r.requisitos
                partes.append(
                    f"<p>Durabilidad del concreto ({_esc(r.condicion)}): a/c "
                    f"maxima {_esc(q.a_c_max)} (gobierna "
                    f"{_esc(q.gobierna_a_c)}), f'c minimo "
                    f"{_esc(q.fc_min_MPa)} MPa (gobierna {_esc(q.gobierna_fc)}); "
                    f"exposicion a sulfatos «{_esc(q.clase_sulfatos)}»; "
                    f"{_esc(r.corpus_tabla)}.</p>")
            if getattr(r, "paso", None) is not None:
                partes.append(bloque_paso(r.paso))
    if c.cuantias:
        partes.append(
            "<p>Cuantias minimas del muro:</p>"
            '<table class="compacta">'
            + _fila(["<th>Direccion</th>", "<th>Cuantia minima</th>"])
            + "".join(_fila([_td(_esc(d)), _td(_num(q, FMT_4), "num")])
                      for d, q in c.cuantias.items()) + "</table>")
    if c.notas:
        partes.append('<div class="nota">'
                      + "".join(f"<p>{_esc(n)}</p>" for n in c.notas)
                      + "</div>")
    partes.append(_tabla_bloqueos(c.bloqueos))
    return "".join(partes)


TITULO_AVISOS_DEL_PUNTO = "Avisos del punto que no salieron junto a su fase"


def _avisos_que_faltan(informe: Any, cuerpo: str) -> str:
    """
    --- T-10 --- Los avisos de `InformePunto.avisos()` --- la MISMA lista,
    con el mismo texto, que imprimen la CLI y el JSON --- que el bloque del
    punto todavia no imprimio. Cada fase pinta los suyos junto a su tabla
    (el TW, la Fase 6, la 7, la 8, la 10); los que no tienen fase en la
    memoria --- los indicadores del cabezal (E*, A2), los del armado, los de
    la embocadura --- quedaban fuera, y el censo de T-10 midio 40 de 47
    avisos de A-01 a expediente que el HTML no llevaba. Aqui salen todos los
    que falten, una vez: se comparan TEXTOS (el aviso escapado contra el
    cuerpo ya armado), no magnitudes.
    """
    avisos = getattr(informe, "avisos", None)
    if avisos is None:
        return ""
    faltan = []
    for aviso in avisos():
        texto = _esc(aviso)
        if texto not in cuerpo and texto not in faltan:
            faltan.append(texto)
    if not faltan:
        return ""
    return (f"<h4>{_esc(TITULO_AVISOS_DEL_PUNTO)}</h4>"
            + "".join(f'<div class="aviso"><p>{t}</p></div>' for t in faltan))


# ===========================================================================
# 2. Tabla resumen (entregable 3)
# ===========================================================================

def tipo_cabezal_del_punto(informe: Any) -> Optional[str]:
    """
    --- T-11 (H8 de su auditoria) --- La celda «Tipo de cabezal» del cuadro
    resumen, leida DEL PUNTO: su embocadura (`InformePunto.embocadura`, que
    T-7a resuelve antes de la Fase 4: con o sin aleros y su angulo) y, cuando
    la Fase 9 del punto corrio, el tipo de cada uno de sus dos cabezales
    (voladizo armado o gravedad ciclopeo). Hasta T-11 la celda era la UNICA
    decision del Tablero 2.3 de la hoja de ruta («tubo a ras del muro»),
    impresa igual en los cuatro puntos, tambien en el marco de la Familia C
    (Carta 8, aletas de 30 a 75 grados). None si la embocadura no se resolvio
    (su etapa se bloqueo): la celda sale vacia declarada, nunca rellena. No
    hace aritmetica: formatea lo que el punto trae.
    """
    e = getattr(informe, "embocadura", None)
    if e is None:
        return None
    aleros = ("sin aleros" if e.angulo_aletas is None else
              f"aleros a {_num(e.angulo_aletas, FMT_2)} grados")
    texto = f"{e.tipo} ({aleros})"
    cabezal = getattr(informe, "cabezal", None)
    if cabezal is not None:
        tipos = [f"{g.extremo} {g.tipo}" for g in cabezal.geometrias if g.tipo]
        if tipos:
            texto += "; " + ", ".join(tipos)
    return texto


def fila_resumen(informe: Any) -> str:
    """
    Una fila del cuadro resumen: progresiva, familia, TR, tipo, material y
    norma de producto, diametro, V, y/D, HW, control gobernante, proteccion de
    salida y tipo de cabezal (entregable 3). El tipo de cabezal es el DEL
    PUNTO (`tipo_cabezal_del_punto`, T-11).

    Toda celda que dependa de una etapa bloqueada sale vacia declarada, nunca
    con un valor plausible.
    """
    punto = informe.punto
    celdas = [_td(_esc(punto.progresiva_display)),
              _td(_esc(punto.familia.value))]

    if informe.clasificacion is None or informe.clasificacion.periodo_retorno.anios is None:
        celdas.append(_td(VACIO, "num"))
    else:
        celdas.append(_td(str(informe.clasificacion.periodo_retorno.anios), "num"))

    if informe.dimensionado:
        resultado = informe.resultado
        material = resultado.material
        h = resultado.resultado_hidraulico
        celdas.extend([
            _td(_esc(material.tipo.value)),
            _td(f"{_esc(material.nombre)}<br>{_esc(rotulo_norma_producto(material))}"),
            _td(_esc(resultado.seccion.etiqueta())),
            _td(_num(h.V_erosion, FMT_2), "num"),
            _td(_num(h.V_sedimentacion, FMT_2), "num"),
            _td(_num(resultado.y_sobre_D, FMT_2), "num"),
            _td(_num(h.HW, FMT_2), "num"),
            _td(_esc(h.control_gobernante.value)),
        ])
    else:
        celdas.extend([_td(VACIO), _td(VACIO), _td(VACIO, "num"),
                       _td(VACIO, "num"), _td(VACIO, "num"),
                       _td(VACIO, "num"), _td(VACIO, "num"), _td(VACIO)])

    if informe.proteccion is None:
        celdas.append(_td(VACIO))
    else:
        p = informe.proteccion
        celdas.append(_td(f"d50 {_num(p.d50)} m<br>e "
                          f"{_num(p.espesor, FMT_2)} m "
                          f"&middot; L {_num(p.longitud, FMT_2)} m"))

    tipo_cabezal = tipo_cabezal_del_punto(informe)
    celdas.append(_td(VACIO) if tipo_cabezal is None else _td(_esc(tipo_cabezal)))
    clase = "" if informe.dimensionado else "fila-incumple"
    return _fila(celdas, clase)


COLUMNAS_RESUMEN_CSV = (
    "id", "progresiva", "familia", "TR_anios", "tipo_hidraulico",
    "material", "norma_producto", "seccion",
    # Dos columnas y no una: la velocidad de la rama n_min (techos: V3, d50) y
    # la de la rama n_max (piso: V2) son numeros distintos y una sola columna
    # "V_ms" obligaba al lector a adivinar cual (MAT-D1).
    "V_erosion_ms", "V_sedimentacion_ms", "y_sobre_D", "HW_m",
    "control_gobernante", "proteccion_d50_m", "proteccion_espesor_m",
    "proteccion_longitud_m", "tipo_cabezal",
)


def _fila_resumen_csv(informe: Any) -> List[Any]:
    """
    Una fila del cuadro resumen (entregable 3) en valores planos, para CSV.
    Misma fuente de datos que `fila_resumen`: toda celda que dependa de una
    etapa bloqueada sale vacia, nunca con un valor plausible.
    """
    punto = informe.punto
    fila: List[Any] = [punto.id, punto.progresiva_display, punto.familia.value]

    if informe.clasificacion is None or informe.clasificacion.periodo_retorno.anios is None:
        fila.append("")
    else:
        fila.append(informe.clasificacion.periodo_retorno.anios)

    if informe.dimensionado:
        resultado = informe.resultado
        material = resultado.material
        h = resultado.resultado_hidraulico
        # --- T-2 --- Con el barril HORIZONTAL (S = 0) no hay velocidad
        # uniforme: las dos celdas van VACIAS, como toda celda del CSV que
        # no tiene dato. `_num(None)` devuelve la marca de la memoria HTML
        # (una entidad `&ndash;`), que en un CSV es basura para quien lo abre
        # en una hoja de calculo: no se pasa por el.
        if h.sin_tirante_normal:
            velocidades = ["", ""]
        else:
            velocidades = [_num(h.V_erosion, FMT_2),
                           _num(h.V_sedimentacion, FMT_2)]
        fila.extend([
            material.tipo.value, material.nombre, material.norma_producto,
            resultado.seccion.etiqueta(), *velocidades,
            _num(resultado.y_sobre_D, FMT_2), _num(h.HW, FMT_2),
            h.control_gobernante.value,
        ])
    else:
        fila.extend(["", "", "", "", "", "", "", "", ""])

    if informe.proteccion is None:
        fila.extend(["", "", ""])
    else:
        # Las tres celdas llevan SIEMPRE numero cuando la Fase 6 corrio
        # (H11 de la segunda auditoria de T-8: «sin enrocado» las dejaba
        # vacias, iguales a las de una fase bloqueada; desde la decision del
        # dueño del 2026-11-12 la proteccion se calcula y se mantiene
        # siempre). Son las que RIGEN por la regla declarada.
        p = informe.proteccion
        fila.extend([_num(p.d50), _num(p.espesor, FMT_2), _num(p.longitud)])

    tipo_cabezal = tipo_cabezal_del_punto(informe)
    fila.append("" if tipo_cabezal is None else tipo_cabezal)
    return fila
