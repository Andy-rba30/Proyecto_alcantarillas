# -*- coding: utf-8 -*-
"""
M11_reporte.bloques_punto
=========================
Submodulo de Fase 11 (`M11_reporte`): bloque `bloques_punto` (D3).
"""

from __future__ import annotations

from typing import Any
from src.modelos import AVISO_SIN_ACCESO_DE_MANTENIMIENTO

from src.modulos.M11_reporte._base import (
    _esc,
    _num,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _tabla_bloqueos,
    _tabla_clasificacion,
    _tabla_datos,
    _tabla_diseno,
    _tabla_iteraciones,
    _td,
)
from src.modulos.M11_reporte.trazas import (
    ETAPA_DURABILIDAD,
    ETAPA_LICUEFACCION,
    TEXTO_LICUEFACCION_BLOQUEADA,
    TITULO_CAUDAL_DE_DISENO,
    TITULO_DURABILIDAD,
    TITULO_LICUEFACCION,
    TITULO_TRAZA_CLASIFICACION,
    TITULO_TRAZA_DURABILIDAD,
    TITULO_TRAZA_HIDRAULICA,
    TITULO_TRAZA_HIDRAULICA_ULTIMO,
    TITULO_TRAZA_HIDROLOGIA,
    TITULO_TRAZA_LICUEFACCION,
    TITULO_TRAZA_TW,
    traza_clasificacion,
    traza_durabilidad,
    traza_hidraulica,
    traza_licuefaccion,
    traza_tw,
)
from src.modulos.M11_reporte.anclas import (
    ancla_de_punto,
)
from src.modulos.M11_reporte.pasos import (
    _tabla_verificaciones,
    bloque_pasos,
)
from src.modulos.M11_reporte.fases_finales import (
    _bloques_fases_finales,
)
from src.modulos.M11_reporte.proyecto import (
    _avisos_que_faltan,
)

def _bloque_durabilidad(informe: Any) -> str:
    """
    La Sec. 3.3 del punto: que hizo la matriz de durabilidad con los
    materiales candidatos (T-4; INF-3.3.1, INF-5.1.9).

    SE IMPRIME EN TODO PUNTO QUE LLEGA A LA FASE 3, con ensayos o sin
    ellos. Sin ensayos la matriz no
    actua y el bloque lo dice con el texto de `DictamenDurabilidad.resumen`;
    callarlo dejaria al lector suponiendo que los tres materiales pasaron
    una matriz que nunca corrio. M11 no decide nada aqui: el efecto de cada
    regla, su texto y sus citas vienen del dictamen que M2 emite.
    """
    dictamen = getattr(informe, "durabilidad", None)
    if dictamen is None:
        # El punto no llego a la Fase 3 (se detuvo en la Fase 2): no hay
        # bloque. Si llego y la etapa se bloqueo, se dice.
        if not any(getattr(b, "etapa", "") == ETAPA_DURABILIDAD
                   for b in getattr(informe, "bloqueos", ())):
            return ""
        return (f"<h4>{_esc(TITULO_DURABILIDAD)}</h4>"
                '<div class="nota"><p>La matriz de durabilidad no se pudo '
                "evaluar en este punto; el motivo esta en la tabla de "
                "bloqueos y el bucle de materiales no corrio.</p></div>")
    partes = [f"<h4>{_esc(TITULO_DURABILIDAD)}</h4>",
              f'<div class="nota"><p><b>{_esc(dictamen.resumen)}</b></p>'
              f"<p>{_esc(dictamen.suelo_fundacion)}</p></div>"]
    if dictamen.reglas:
        filas = [_fila(["<th>Dato</th>", "<th>Material</th>",
                        "<th>Efecto</th>", "<th>Lo que la matriz deja "
                        "escrito</th>", "<th>Citas</th>"])]
        for regla in dictamen.reglas:
            material = ("todos" if regla.material is None
                        else regla.material.value)
            filas.append(_fila([
                _td(f"<code>{_esc(regla.ensayo)}</code>"),
                _td(_esc(material)),
                _td(f"<b>{_esc(regla.efecto.value)}</b>"),
                _td(_esc(regla.texto)),
                _td("<br>".join(f"<code>{_esc(c)}</code>"
                                for c in regla.cita_ids)),
            ], "fila-incumple" if regla.efecto.value == "excluye" else ""))
        partes.append('<table class="compacta">' + "".join(filas)
                      + "</table>")
    partes.append(bloque_pasos(traza_durabilidad(informe),
                               TITULO_TRAZA_DURABILIDAD))
    return "".join(partes)


def _bloque_licuefaccion(informe: Any) -> str:
    """
    --- VE-7, lote C (C4; VE5-CAT-03) --- La Fase 0-bis del punto con
    seccion propia: el estado de la `Verificacion` que `ML_licuefaccion`
    emitio --- el resultado del EMS contrastado, o por que 10.5.4.2 no la
    exige ---, los mismos textos que el JSON publica en la clave
    `licuefaccion`, sus avisos y su paso.

    Con la etapa BLOQUEADA a expediente la seccion lo dice y remite a la
    tabla de bloqueos; diferida por el alcance (perfil) no hay seccion: la
    constancia del diferimiento ya esta en esa tabla. M11 no decide nada:
    todo viene hecho de la Fase 0-bis.
    """
    v = getattr(informe, "licuefaccion", None)
    if v is None:
        if not any(getattr(b, "etapa", "") == ETAPA_LICUEFACCION
                   and not getattr(b, "diferido_por_alcance", False)
                   for b in getattr(informe, "bloqueos", ())):
            return ""
        return (f"<h4>{_esc(TITULO_LICUEFACCION)}</h4>"
                f'<div class="nota"><p>{_esc(TEXTO_LICUEFACCION_BLOQUEADA)}'
                "</p></div>")
    filas = [_fila(["<th>Codigo</th>", "<th>Numeral</th>",
                    "<th>Estado</th>", "<th>Resultado del EMS</th>",
                    "<th>Lo que el proyecto exige</th>",
                    "<th>Criterio</th>"]),
             _fila([_td(f"<code>{_esc(v.codigo)}</code>"),
                    _td(_esc(v.numeral)),
                    _td(f"<b>{_esc(v.estado.value)}</b>"),
                    _td("&mdash;" if v.valor_obtenido is None
                        else _esc(v.valor_obtenido)),
                    _td("&mdash;" if v.valor_admisible is None
                        else _esc(v.valor_admisible)),
                    _td("&mdash;" if not v.criterio_aplicado
                        else f"<code>{_esc(v.criterio_aplicado)}</code>")])]
    partes = [f"<h4>{_esc(TITULO_LICUEFACCION)}</h4>",
              '<table class="compacta">' + "".join(filas) + "</table>"]
    if v.motivo_no_aplica:
        partes.append(f'<div class="nota"><p>{_esc(v.motivo_no_aplica)}'
                      "</p></div>")
    partes.extend(f'<div class="aviso"><p>{_esc(aviso)}</p></div>'
                  for aviso in v.avisos)
    partes.append(bloque_pasos(traza_licuefaccion(informe),
                               TITULO_TRAZA_LICUEFACCION))
    return "".join(partes)


def _pasos_de_clasificacion(informe: Any) -> str:
    """La traza de la Fase 2: denominacion por luz y periodo de retorno."""
    return bloque_pasos(traza_clasificacion(informe),
                        TITULO_TRAZA_CLASIFICACION)


def _bloque_hidrologia(informe: Any) -> str:
    """
    El caudal de diseño del punto y DE DONDE SALE (T-1): la leyenda --«Q
    declarado por el estudio hidrológico» o calculado por el programa--, los
    avisos que no detienen nada, y los pasos de la Fase 1-bis. Va despues de
    la clasificacion porque el caudal calculado usa su TR.

    Todo llega hecho en `InformePunto.caudal`: este bloque no calcula.
    """
    caudal = getattr(informe, "caudal", None)
    if caudal is None:
        return ""
    clase = "nota" if caudal.calculado else "aviso"
    partes = [
        f"<h4>{_esc(TITULO_CAUDAL_DE_DISENO)}</h4>",
        f'<div class="{clase}"><p><b>{_esc(caudal.leyenda)}</b>: Q = '
        f"{_num(caudal.Q_m3s)} m³/s &mdash; {_esc(caudal.de_donde)}.</p></div>"]
    partes.extend(f'<div class="aviso"><p>{_esc(aviso)}</p></div>'
                  for aviso in caudal.avisos)
    partes.append(bloque_pasos(caudal.pasos, TITULO_TRAZA_HIDROLOGIA))
    return "".join(partes)


def _paso_del_tw(informe: Any) -> str:
    """
    El desarrollo de Sec. 1.3: por que via salio el TW de este punto.

    Va ANTES del desarrollo hidraulico y no dentro de el, porque el TW es un
    DATO DE ENTRADA de la Fase 4, no un resultado suyo: se obtiene en la Fase
    1 y el control de salida lo consume. Imprimirlo dentro haria parecer que
    el calculo hidraulico lo produce.

    Hasta S20 no habia nada que imprimir: el TW entraba por un criterio o por
    una opcion de la linea de comandos, y la memoria lo mostraba como un
    numero en la tabla de diseño, sin procedencia (SIS-B-04).
    """
    tw = getattr(informe, "tw_sec13", None)
    paso = traza_tw(informe)
    if paso is None:
        return ""
    escenarios = ""
    if getattr(tw, "escenarios", ()):
        filas = "".join(
            _fila([_td(_esc(rotulo)), _td(_num(valor), "num")])
            for rotulo, valor in tw.escenarios)
        escenarios = (
            "<h5>Los dos escenarios acotados del paso 3</h5>"
            "<table>"
            + _fila(["<th>Escenario</th>", "<th>TW (m)</th>"])
            + filas
            + "</table>"
            + '<div class="nota"><p>La hoja de ruta pide cumplir en AMBOS. El '
              'diseño corre con el gobernante &mdash; el mayor &mdash;, y eso '
              'implica cumplir con el otro: h_o = max(TW, (y_c + D)/2) no '
              'decrece con TW, HW de salida crece con h_o, y el control que '
              'gobierna es el mayor de los dos HW; luego V4 y V4b, que son '
              'las unicas verificaciones que dependen del TW, tienen su peor '
              'caso en el TW mayor. Los dos numeros se imprimen para que se '
              'pueda comprobar en vez de creerlo.</p></div>')
    # --- T-2 --- (INF-3.2.8) CON QUE SECCION DEL RECEPTOR se obtuvo el TW,
    # cuando la via la usa: «seccion adoptada [A] por falta de levantamiento»
    # o «seccion medida», con el rotulo que M3 puso y sin redactarlo aqui; y
    # el AVISO que dispara la adoptada. El texto es el de
    # `TWDeterminado.avisos`, el mismo que imprimen la CLI y el JSON.
    de_la_seccion = ""
    if getattr(tw, "origen_seccion", ""):
        de_la_seccion = (
            '<div class="nota"><p><b>Seccion del receptor con que se obtuvo '
            f'este TW:</b> {_esc(tw.origen_seccion)}.</p></div>')
    avisos = "".join(f'<div class="aviso"><p><b>Aviso.</b> {_esc(a)}</p></div>'
                     for a in getattr(tw, "avisos", ()))
    return (bloque_pasos((paso,), TITULO_TRAZA_TW) + escenarios
            + de_la_seccion + avisos)


def _acceso_de_mantenimiento(informe: Any) -> str:
    """
    --- T-2 --- Lo que el punto declaro sobre el acceso de mantenimiento
    (`acceso_mantenimiento_previsto`, booleano opcional de --datos-externos):
    previsto, o NO previsto con su aviso. Sin declaracion no imprime nada: el
    dispositivo lo dice el criterio 'acceso_mantenimiento_v2b' en el paso de
    V2b, con la exigencia del num. 4.1.1.3.7 d) citada.
    """
    acceso = getattr(informe, "acceso_mantenimiento", None)
    if acceso is None:
        return ""
    if acceso.valor is True:
        return ('<div class="nota"><p><b>Acceso de mantenimiento:</b> el punto '
                'declara que esta PREVISTO en los planos '
                f'({_esc(acceso.origen)}). Es la exigencia del num. 4.1.1.3.7 '
                'd) del Manual; el dispositivo lo declara el criterio '
                "'acceso_mantenimiento_v2b'.</p></div>")
    return (f'<div class="aviso"><p><b>Aviso.</b> '
            f'{_esc(AVISO_SIN_ACCESO_DE_MANTENIMIENTO)} '
            f'({_esc(acceso.origen)}).</p></div>')


def _pasos_hidraulicos_del_punto(informe: Any) -> str:
    """
    La traza de las Fases 3 y 4: Manning, tirante critico, los dos controles y
    la adopcion del que gobierna.

    Sale de `ResultadoHidraulico.pasos`, que M4 emitio al resolver la
    combinacion adoptada. M11 no vuelve a calcular nada: hasta S18 este modulo
    obtenia `y/D` dividiendo aqui mismo, que es SIS-A-07.
    """
    # EL PUNTO PUEDE NO CERRAR, Y AUN ASI HAY CALCULO QUE PUBLICAR: la
    # seleccion --- el diseño adoptado, o el ULTIMO escalon del bucle que
    # llego a resolver la hidraulica --- vive en `traza_hidraulica`,
    # compartida con `traza_punto` desde G4. No es un premio de consolacion:
    # en este expediente NINGUN punto se dimensiona --- V5 se detiene siempre
    # en `ancho_derecho_via_m` ---, de modo que sin el ultimo escalon el
    # desarrollo que M3 y M4 si calcularon no llegaria jamas al revisor. Es
    # la misma trampa de NOR-MEM-01: cierto sobre el codigo y falso sobre el
    # producto.
    pasos, ultimo = traza_hidraulica(informe)
    if not pasos:
        return ""
    if ultimo is None:
        return bloque_pasos(pasos, TITULO_TRAZA_HIDRAULICA)
    aviso = (
        '<div class="aviso"><p><b>Este desarrollo es el del ultimo escalon '
        f"evaluado &mdash; {_esc(ultimo.material)}, "
        f"{_esc(ultimo.seccion.etiqueta())} &mdash;, no el de un diseño "
        "adoptado: "
        "el punto <b>no se dimensiono</b>. Se publica porque es calculo que "
        "el pipeline hizo de verdad y que el revisor necesita para juzgar por "
        "que se descarto ese escalon; el motivo esta en la tabla de "
        "iteraciones.</p></div>")
    return aviso + bloque_pasos(pasos, TITULO_TRAZA_HIDRAULICA_ULTIMO)


TITULO_GOBIERNO_RECEPTOR = ("Diametro gobernado por el nivel del receptor "
                            "(no por el caudal de diseño)")


def _paso_gobierno_por_receptor(informe: Any) -> str:
    """
    --- VE-3.13 (decision 8 del dueño) --- El paso que MD emitio cuando el
    diametro lo goberno el nivel del receptor
    (`ResultadoPunto.gobierno_por_receptor`), detras de la tabla de
    iteraciones que muestra los escalones descartados. Formato: el numero y
    el texto vienen del paso.
    """
    resultado = getattr(informe, "resultado", None)
    gobierno = getattr(resultado, "gobierno_por_receptor", None)
    if gobierno is None:
        return ""
    return bloque_pasos((gobierno.paso,), TITULO_GOBIERNO_RECEPTOR)


def memoria_de_punto(informe: Any) -> str:
    """Bloque completo de un punto critico (entregable 1 de la Fase 11)."""
    punto = informe.punto
    clase = "punto" if informe.dimensionado else "punto sin-cerrar"
    estado = ("dimensionado" if informe.dimensionado
              else "sin dimensionar")
    partes = [
        f'<div class="{clase}" id="{ancla_de_punto(punto.id)}">',
        f"<h3>{_esc(punto.id)} &nbsp;|&nbsp; progresiva "
        f"{_esc(punto.progresiva_display)} &nbsp;|&nbsp; Familia "
        f"{_esc(punto.familia.value)} &nbsp;|&nbsp; {estado}</h3>",
        "<h4>Datos de partida y su fuente</h4>",
        _tabla_datos(informe),
        _tabla_clasificacion(informe),
        _pasos_de_clasificacion(informe),
        _bloque_licuefaccion(informe),                # --- VE-7 (C4) ---
        _bloque_hidrologia(informe),
        _bloque_durabilidad(informe),
        _tabla_iteraciones(informe),
        _paso_gobierno_por_receptor(informe),
        _tabla_diseno(informe),
        _paso_del_tw(informe),
        _pasos_hidraulicos_del_punto(informe),
        _tabla_verificaciones(informe),
        _acceso_de_mantenimiento(informe),
        _bloques_fases_finales(informe),
    ]
    cuerpo = "".join(partes)
    return (cuerpo + _avisos_que_faltan(informe, cuerpo)
            + _tabla_bloqueos(informe.bloqueos) + "</div>")
