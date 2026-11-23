# -*- coding: utf-8 -*-
"""
M11_reporte.fases_finales
=========================
Submodulo de Fase 11 (`M11_reporte`): bloque `fases_finales` (D3).
"""

from __future__ import annotations

from typing import (
    Any,
    List,
    Tuple,
)
from src.modulos.M5_verificaciones import CRITERIO_ORIGEN_COTA_ENTRADA
from src.modulos.M8_estructural import verificacion_diferida_estructural

from src.modulos.M11_reporte._base import (
    FMT_2,
    FMT_4,
    _esc,
    _num,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
)
from src.modulos.M11_reporte.trazas import (
    TITULO_TRAZA_ESPACIAMIENTO,
    TITULO_TRAZA_GEOMETRIA,
    TITULO_TRAZA_GEOMETRIA_PREVIA,
    traza_espaciamiento,
    traza_geometria,
)
from src.modulos.M11_reporte.anclas import (
    _cita_como_texto,
    _enlace,
    ancla_de_cita,
)
from src.modulos.M11_reporte.pasos import (
    bloque_pasos,
)
from src.modulos.M11_reporte.cabezal import (
    _bloque_cabezal,
)
from src.modulos.M11_reporte.metrados import (
    _bloque_compatibilidad_punto,
    _bloque_metrado,
)

def traza_proteccion(informe: Any) -> Tuple[Any, ...]:
    """
    --- T-8 --- Los `PasoDeMemoria` de la Fase 6 de un punto, en su orden de
    lectura: la proteccion de salida (Laushey, lo adoptado, Froude,
    velocidad admisible, apron de HEC-14, filtro), la de entrada y la
    socavacion. M6 los emite; aqui solo se enumeran.
    """
    pasos: List[Any] = []
    for pieza in (getattr(informe, "proteccion", None),
                  getattr(informe, "proteccion_entrada", None),
                  getattr(informe, "socavacion", None)):
        if pieza is None:
            continue
        propios = tuple(getattr(pieza, "pasos", ()) or ())
        if not propios and getattr(pieza, "paso", None) is not None:
            # Una `ProteccionSalida` armada antes de T-8: solo trae Laushey.
            propios = (pieza.paso,)
        pasos.extend(propios)
    return tuple(pasos)


TITULO_TRAZA_PROTECCION = "Desarrollo de la Fase 6"


def _fase_6_ampliada(informe: Any) -> str:
    """
    --- T-8 --- Lo que la Fase 6 añade al parrafo del d50: el filtro como
    requisito declarado, la entrada, la socavacion para el desplante, los
    avisos de la fase y el desarrollo de todos los pasos. No calcula nada:
    todos los numeros vienen de M6.
    """
    partes: List[str] = []
    p = informe.proteccion
    filtro = getattr(p, "filtro", None)
    if filtro is not None:
        # --- T-10 --- con las citas que lo sostienen, que el JSON publica
        # (`filtro.citas`) y la memoria no nombraba: numeral y pagina, con
        # el enlace a su texto en el anexo.
        citas = "; ".join(
            _enlace(ancla_de_cita(cita_id), _esc(_cita_como_texto(cita_id)))
            for cita_id in getattr(filtro, "citas", ()))
        partes.append(f'<div class="nota"><p><b>Filtro.</b> '
                      f"{_esc(filtro.texto)}"
                      + (f" Sostienen el requisito: {citas}." if citas else "")
                      + "</p></div>")
    e = getattr(informe, "proteccion_entrada", None)
    if e is not None:
        velocidad = ("sin velocidad publicada por la hidraulica"
                     if e.V_entrada is None else
                     f"V = {_num(e.V_entrada, FMT_2)} m/s en la boca")
        partes.append(
            f"<p><b>Entrada.</b> {_esc(velocidad)}; revestimiento adoptado "
            f"<b>{_esc(e.revestimiento)}</b> (criterio "
            f"<code>{_esc(e.criterio_revestimiento)}</code>); embocadura "
            f"{_esc(e.tipo_embocadura)}. Se protege: "
            f"{_esc('; '.join(e.elementos))}.</p>")
    soc = getattr(informe, "socavacion", None)
    if soc is not None:
        if soc.profundidad_para_desplante is None:
            texto = ("<b>sin dato</b>: " + _esc(soc.motivo_no_estimada))
        else:
            texto = (f"<b>{_num(soc.profundidad_para_desplante)} m</b> "
                     f"({_esc(soc.origen)}), medida desde "
                     f"{_esc(soc.referencia or '')}")
            if getattr(soc, "cota_fondo_de_la_hoya", None) is not None:
                texto += (f"; fondo de la hoya a "
                          f"<b>{_num(soc.cota_fondo_de_la_hoya)} msnm</b>")
            if soc.estimada is not None:
                h = soc.estimada
                texto += (f". Hoya estimada por {_esc(h.metodo)}: "
                          f"profundidad {_num(h.profundidad)} m, ancho "
                          f"{_num(h.ancho)} m, longitud {_num(h.longitud)} m, "
                          "con el maximo a "
                          f"{_num(h.distancia_al_maximo)} m de la salida")
        partes.append("<p><b>Socavacion a la salida, para el desplante del "
                      f"cabezal.</b> {texto}.</p>")
    # LOS AVISOS DE LA FASE, con el MISMO texto que la CLI y el JSON imprimen
    # (`InformePunto.avisos`): lo que no se comparo o no se estimo por falta
    # de un dato del sitio, y donde lo adoptado queda bajo lo que HEC-14 da.
    for pieza in (p, e, soc):
        for aviso in getattr(pieza, "avisos", ()) or ():
            partes.append(f'<div class="aviso"><p><b>Aviso.</b> '
                          f"{_esc(aviso)}</p></div>")
    partes.append(bloque_pasos(traza_proteccion(informe),
                               TITULO_TRAZA_PROTECCION))
    return "".join(partes)


def _bloques_fases_finales(informe: Any) -> str:
    """Fases 6, 7, 8 y 10 del punto, cada una con su numeral."""
    partes: List[str] = []

    if informe.proteccion is not None:
        p = informe.proteccion
        avisos = "".join(f'<div class="aviso"><p>{_esc(a)}</p></div>'
                         for a in p.advertencias)
        # La proteccion lleva SIEMPRE numero (decision del dueño del
        # 2026-11-12: «sin enrocado» no es una conclusion del programa). Lo
        # que cambia es a QUE se atribuye: con la envolvente, el espesor y
        # la longitud --y la piedra, cuando HEC-14 pide mas-- no salen del
        # numeral del Manual ni de los dos criterios a secas.
        if p.rige_la_envolvente:
            resumen = (
                f"<p>d<sub>50</sub> = {_num(p.d50)} m, espesor "
                f"{_num(p.espesor)} m y longitud {_num(p.longitud)} m: rige "
                "la ENVOLVENTE del Manual y de HEC-14 (regla "
                f"<code>{_esc(p.regla_espesor_longitud)}</code>; el "
                "desarrollo, en el paso 6.6c). El d<sub>50</sub> de Laushey "
                f"(num. {_esc(p.numeral)}) es {_num(p.d50_laushey)} m, y lo "
                f"adoptado por los criterios "
                f"<code>{_esc(p.criterio_espesor)}</code> y "
                f"<code>{_esc(p.criterio_longitud)}</code>, "
                f"{_num(p.espesor_adoptado)} m y "
                f"{_num(p.longitud_adoptada)} m. Todo con la velocidad de "
                f"SALIDA de HDS-5 3.1.6 V = {_num(p.V, FMT_2)} m/s (su "
                "procedencia, en el paso 6.1).</p>")
        else:
            resumen = (
                f"<p>d<sub>50</sub> = {_num(p.d50)} m (num. "
                f"{_esc(p.numeral)}), espesor {_num(p.espesor)} m (criterio "
                f"<code>{_esc(p.criterio_espesor)}</code>), longitud "
                f"{_num(p.longitud)} m (criterio "
                f"<code>{_esc(p.criterio_longitud)}</code>), con la "
                f"velocidad de SALIDA de HDS-5 3.1.6 V = "
                f"{_num(p.V, FMT_2)} m/s (su procedencia, en el paso "
                "6.1).</p>")
        partes.append("<h4>Fase 6 &mdash; Proteccion de entrada y salida</h4>"
                      + resumen + avisos + _fase_6_ampliada(informe))

    if informe.geometria is not None:
        g = informe.geometria
        t = g.tamizado
        # DOS estados y no uno. `g.factible` es el de 7.B ENTERA (G1 y G2) y
        # `t.factible` el del tamizado de 7.A (solo G1): rotular el primero
        # como "Tamizado 7.A" decia "el tamizado no compatible" en el punto
        # cuyo tamizado si compatible y lo que falla es la cota de salida, y
        # el revisor iba a corregir la rasante, que no es el remedio de G2.
        estado_7b = ('<span class="cumple">compatible</span>' if g.factible
                     else '<span class="incumple">no compatible</span>')
        estado_7a = ('<span class="cumple">compatible</span>' if t.factible
                     else '<span class="incumple">no compatible</span>')
        # None cuando la rasante alcanza: subirla no arregla un G2 incumplido
        # (ver `CompatibilidadGeometrica.delta_rasante_cm`).
        delta = ("" if g.delta_rasante_cm is None else
                 f" Requiere subir la rasante {_num(g.delta_rasante_cm, FMT_2)} cm.")
        # La cota de entrada NO es un dato del CSV: sale de la regla que el
        # proyectista declaro en 'origen_cota_fondo_entrada' (SIS-A-04). Se
        # imprime marcada, con la clave del criterio delante, porque un
        # numero en msnm sin marca se lee como cota levantada en campo.
        # --- T-6 --- LA MARCA DE LA COTA DE ENTRADA DICE CUAL DE LAS DOS
        # FUE. Este parrafo escribia «adoptada ... no es cota medida» SIEMPRE,
        # tambien cuando la columna `cota_fondo_entrada` traia el fondo
        # medido: el texto y el volcado de la CLI ya lo distinguian y la
        # memoria no. Los avisos (fondo adoptado, pendiente que gobierna un
        # extremo de la banda, plataforma horizontal) salen del objeto de
        # 7.B, no se redactan aqui; el de esviaje es la fila G3 de la tabla
        # de verificaciones, con veredicto de indicador.
        # --- T-10 --- la nota la escribe el objeto (`CotaDeEntrada.nota`),
        # la misma que lleva el JSON.
        if g.cota_entrada.medida:
            origen_entrada = f"<b>medida</b>: {_esc(g.cota_entrada.nota)}"
        else:
            origen_entrada = (
                "<b>adoptada</b>, criterio "
                f"<code>{_esc(CRITERIO_ORIGEN_COTA_ENTRADA)}</code>: "
                f"{_esc(g.cota_entrada.nota)}")
        avisos = "".join(f'<div class="aviso"><p><b>Aviso:</b> {_esc(a)}.'
                         "</p></div>" for a in getattr(g, "avisos", ()))
        calculada = getattr(g, "longitud_calculada", None)
        metodo = ("" if calculada is None else
                  f" (metodo <code>{_esc(calculada.metodo.value)}</code>)")
        pendiente = getattr(g, "pendiente", None)
        origen_s = ("" if pendiente is None else
                    f", pendiente {_num(g.S_conducto, FMT_4)} m/m "
                    f"(origen: {_esc(pendiente.origen.value)})")
        pasos_7b, _previa = traza_geometria(informe)
        partes.append(
            "<h4>Fase 7 &mdash; Compatibilidad geometrica</h4>"
            f"<p>L = {_num(g.longitud, FMT_2)} m{metodo}, esviaje afectando con factor "
            f"{_num(g.factor_esviaje)}{origen_s}; cota de entrada {_num(g.cota_entrada.valor)} ({_esc(g.cota_entrada.rotulo)}) "
            f"msnm ({origen_entrada}) y de salida "
            f"{_num(g.cota_salida)} msnm (caida "
            f"{_num(g.caida)} m), num. {_esc(g.numeral)}. Compatibilidad "
            f"7.B (G1 y G2): {estado_7b}. Tamizado 7.A (G1): "
            f"{estado_7a}, gobierna la condicion "
            f"<b>{_esc(t.condicion_gobernante.value)}</b> "
            f"(criterio <code>{_esc(t.criterio_gobernante)}</code>).{delta}</p>"
            + avisos
            + f'<div class="nota"><p>{_esc(t.mensaje)}</p></div>'
            + bloque_pasos(pasos_7b, TITULO_TRAZA_GEOMETRIA))
    else:
        # --- T-6 --- el punto no llego a 7.B, pero la longitud se calculo
        # ANTES de la Fase 4 y entro al control de salida de cada escalon.
        pasos_7b, previa = traza_geometria(informe)
        if pasos_7b and previa:
            partes.append(
                "<h4>Fase 7 &mdash; Longitud del conducto</h4>"
                '<div class="nota"><p>El punto no se dimensiono y la Sec. '
                "7.B no se evaluo; se publica la longitud con que corrio el "
                "diseño hidraulico de cada escalon.</p></div>"
                + "".join(
                    f'<div class="aviso"><p><b>Aviso:</b> {_esc(a)}.</p></div>'
                    for a in getattr(informe, "avisos_de_geometria",
                                     lambda: ())())
                + bloque_pasos(pasos_7b, TITULO_TRAZA_GEOMETRIA_PREVIA))

    # --- T-5 --- Lo que la Fase 8 sigue sin verificar, UNA vez por punto,
    # con su razon: desde T-5 ya no es el item 5 entero (lo implementa M8),
    # solo lo que de verdad queda fuera. Se imprime LO DEL CONDUCTO DE ESTE
    # PUNTO (`ResultadoEstructural.diferido`), no la lista de todos los
    # materiales: el bloque del tubo de concreto listaba el portico del
    # marco, la flexion del HDPE y la costura empernada del TMC (auditoria de
    # T-5). Solo el punto que trae la cama y no el conducto imprime la lista
    # entera (`verificacion_diferida_estructural`).
    estructural = getattr(informe, "estructural", None)
    diferidas = "".join(
        f'<div class="nota"><p>{_esc(t)}</p></div>'
        for t in (estructural.diferido
                  if estructural is not None and estructural.diferido
                  else verificacion_diferida_estructural()))
    if estructural is not None:
        partes.append(_bloque_estructural(estructural))
    if informe.cama_apoyo is not None:
        c = informe.cama_apoyo
        partes.append(
            "<h4>Fase 8 &mdash; Cama de apoyo y relleno lateral</h4>"
            f"<p>Cama de apoyo: {_esc(c.cama_apoyo)}. Sujecion y relleno "
            f"lateral: {_esc(c.sujecion_relleno_lateral)} "
            f"(num. {_esc(c.numeral)}).</p>")
    if estructural is not None or informe.cama_apoyo is not None:
        partes.append("<h4>Fase 8 &mdash; Lo que no se verifica</h4>"
                      + diferidas)

    # --- T-7a --- la Fase 9 del punto: embocadura y, a expediente, cabezales.
    cabezal = _bloque_cabezal(informe)
    if cabezal:
        partes.append(cabezal)

    # --- T-9 --- los avisos de la Fase 10 (pendiente de la cuneta fuera de
    # la banda del Manual, capacidad gobernada por la velocidad limite, VB1
    # sin evaluar): salen aqui y por `InformePunto.avisos()` en la CLI y el
    # JSON, con el mismo texto. Tambien cuando la Fase 10 no cerro y el
    # punto solo trae el aviso del tramo.
    tramo = getattr(informe, "tramo_alivio", None)
    aporte = getattr(informe, "aporte_alivio", None)
    avisos_10: list = []
    # --- T-9 (correcciones) --- los de la capacidad (VB2), los de la
    # longitud, VB2 sin evaluar y los huecos de cuneta que VB1 no mira. VB1
    # sin evaluar ya no es un aviso: es un bloqueo del punto (H2), y sale con
    # los bloqueos.
    if aporte is not None:
        if aporte.capacidad is not None:
            avisos_10.extend(aporte.capacidad.avisos)
        if aporte.aviso:
            avisos_10.append(aporte.aviso)
    avisos_10.extend(a for a in (getattr(informe.espaciamiento, "avisos", ())
                                 or ()) if a not in avisos_10)
    if tramo is not None:
        avisos_10.extend(a for a in tramo.avisos if a not in avisos_10)
    html_avisos_10 = "".join(
        f'<div class="aviso"><p><b>Aviso:</b> {_esc(a)}.</p></div>'
        for a in avisos_10)
    if informe.espaciamiento is None and (html_avisos_10
                                          or traza_espaciamiento(informe)):
        partes.append("<h4>Fase 10 &mdash; Espaciamiento de alcantarillas de "
                      "alivio</h4>" + html_avisos_10
                      + bloque_pasos(traza_espaciamiento(informe),
                                     TITULO_TRAZA_ESPACIAMIENTO))
    if informe.espaciamiento is not None:
        e = informe.espaciamiento
        # --- T-9 --- el origen de L_hidraulico, los pasos que la calculan y
        # el tramo de VB1 (la verificacion sale en la tabla del punto; el
        # tramo sin evaluar, en los avisos).
        texto_tramo = ""
        if tramo is not None and tramo.longitud_m is not None:
            texto_tramo = (
                f" Tramo de cuneta que descarga en esta obra (VB1): "
                f"{_num(tramo.longitud_m, FMT_2)} m desde "
                f"{_esc(tramo.extremo)} ({_esc(tramo.origen_extremo)}).")
        if aporte is not None:
            # --- T-10 --- de donde sale el caudal que VB2 compara (el JSON
            # lo publicaba como `origen_aporte`).
            texto_tramo += (f" Caudal de aporte de VB2: "
                            f"{_num(aporte.Q_aporte_m3s)} m3/s, "
                            f"{_esc(aporte.origen_aporte)}.")
        partes.append(
            "<h4>Fase 10 &mdash; Espaciamiento de alcantarillas de alivio</h4>"
            f"<p>Espaciamiento maximo {_num(e.espaciamiento_max, FMT_2)} m: "
            f"gobierna el limite <b>{_esc(e.gobierna.value)}</b> "
            f"(normativo {_num(e.L_normativo, FMT_2)} m por el criterio "
            f"<code>{_esc(e.criterio_normativo)}</code>, hidraulico "
            f"{_num(e.L_hidraulico, FMT_2)} m, "
            f"<b>{_esc(e.origen_L_hidraulico)}</b>), num. "
            f"{_esc(e.numeral)}.{texto_tramo}</p>"
            + html_avisos_10
            + bloque_pasos(traza_espaciamiento(informe),
                           TITULO_TRAZA_ESPACIAMIENTO))

    # --- VE-5 met --- Fase 11: la fila del punto en el cuadro de
    # compatibilidad (entregable 9) y su metrado (entregable 8).
    partes.append(_bloque_compatibilidad_punto(informe))
    partes.append(_bloque_metrado(informe))
    return "".join(partes)


def _bloque_estructural(r: Any) -> str:
    """
    --- T-5 --- La Fase 8 del conducto (INF-3.3.5): lo elegido, las alturas
    con que se verifico, el relleno maximo y los pasos de carga que emitio
    M8. Las verificaciones F8.* NO se repiten aqui: estan en la tabla de la
    Fase 5, con su paso. Formatea; no calcula.
    """
    avisos = "".join(f'<div class="aviso"><p>{_esc(a)}</p></div>'
                     for a in r.avisos)
    if r.demanda_marco is not None:
        d = r.demanda_marco
        cabeza = (
            "<p>Marco: "
            + ("<b>portico analizado y armado</b> (tabla de abajo; sus "
               "verificaciones A1 a A6 estan en la tabla del punto). "
               if getattr(r, "portico", None) is not None else
               "<b>el portico no se completo</b> (ver la tabla de "
               "bloqueos). ")
            + f"Demanda de referencia de la losa superior M<sub>ref</sub> = "
            f"{_num(d.M_u_referencia_kNm_m, FMT_2)} kN&middot;m/m "
            f"(w<sub>u</sub> = {_num(d.w_u_kPa, FMT_2)} kPa, L = "
            f"{_num(d.luz_m, FMT_2)} m, F<sub>e</sub> = {_num(d.F_e)}).</p>"
            + _tabla_portico(getattr(r, "portico", None)))
    else:
        maximo = ("&mdash;" if r.relleno_maximo_m is None
                  else f"{_num(r.relleno_maximo_m, FMT_2)} m")
        cabeza = (
            f"<p>Seleccion: <b>{_esc(r.seleccion or 'ninguna cumple')}</b>. "
            f"Relleno sobre la clave {_num(r.H_relleno_m)} m mas paquete "
            f"estructural {_num(r.e_paquete_m)} m (profundidad para la carga "
            f"viva {_num(r.H_total_m)} m). Relleno maximo con lo elegido: "
            f"{maximo}.</p>")
    return ("<h4>Fase 8 &mdash; Estructural del conducto</h4>" + cabeza
            + avisos + bloque_pasos(r.pasos, "Desarrollo de la Fase 8"))


def _tabla_portico(portico: Any) -> str:
    """
    --- VE-5 (m8) --- Las secciones armadas del portico del marco, con los
    numeros que `M8.disenar_portico` emitio (cada una es un
    `ArmadoDeSeccion` del armado del cabezal). Formatea; no calcula.
    """
    if portico is None or not portico.armados:
        return ""
    filas = [_fila(["<th>Seccion</th>", "<th>Cara</th>",
                    "<th>Espesor / d (m)</th>", "<th>Rige la flexion</th>",
                    "<th>M_u (kN&middot;m/m); V_u (kN/m)</th>",
                    "<th>As adoptado (mm&sup2;/m), gobierna</th>",
                    "<th>Barra</th>",
                    "<th>M_r, V_r (kN&middot;m/m, kN/m)</th>",
                    "<th>Cumple</th>"])]
    for a in portico.armados:
        filas.append(_fila([
            _td(_esc(a.seccion)), _td(_esc(a.cara)),
            _td(f"{_num(a.espesor)} / {_num(a.d)}", "num"),
            _td(_esc(a.rige_flexion.combinacion)),
            _td(f"{_num(a.rige_flexion.M_u, FMT_2)}; "
                f"{_num(a.rige_cortante.V_u, FMT_2)}", "num"),
            _td(f"{_num(a.As_adoptado, FMT_2)}, {_esc(a.gobierna)}"),
            _td(_esc(a.barra.texto) if a.barra is not None
                else "sin barra del catalogo"),
            _td(f"{_num(a.M_r, FMT_2)}, {_num(a.V_r, FMT_2)}", "num"),
            _td("si" if all(v.cumple for v in a.verificaciones) else "NO")]))
    g = portico.geometria
    return (f"<p>Portico de {g.n_celdas} celda(s) de "
            f"{_num(g.luz_libre_m, FMT_2)} x {_num(g.altura_libre_m, FMT_2)} "
            f"m, canto {_num(g.t_losa_superior_m)} m (AASHTO LRFD 12.11):</p>"
            '<table class="compacta">' + "".join(filas) + "</table>"
            + "".join(f'<div class="nota"><p>{_esc(t)}</p></div>'
                      for t in portico.diferido))
