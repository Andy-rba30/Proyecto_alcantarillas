# -*- coding: utf-8 -*-
"""
M11_reporte.trazas
==================
Submodulo de Fase 11 (`M11_reporte`): bloque `trazas` (D3).
"""

from __future__ import annotations

from typing import (
    Any,
    Optional,
    Tuple,
)


# ---------------------------------------------------------------------------
# LA SELECCION de pasos que la memoria publica por punto, separada del HTML.
#
# Existe desde G4 porque hay DOS consumidores de la misma decision: este
# modulo (que la escribe en HTML) y `src/traza_punto.py` (que la sirve a la
# GUI como dato). La decision --- que pasos de un punto se publican, en que
# orden y cual escalon se toma cuando el punto no cierra --- es UNA, y
# escribirla dos veces es como la GUI y la memoria empiezan a contar historias
# distintas. Estas funciones SELECCIONAN; no formatean ni calculan.
# ---------------------------------------------------------------------------

TITULO_TRAZA_CLASIFICACION = "Desarrollo de la clasificacion (Fase 2)"
TITULO_CAUDAL_DE_DISENO = "Caudal de diseño y su origen (Fase 1-bis)"
TITULO_TRAZA_HIDROLOGIA = "Desarrollo del calculo hidrologico (Fase 1-bis)"
TITULO_TRAZA_TW = "Obtencion del TW en el cuerpo receptor (Sec. 1.3)"
TITULO_TRAZA_HIDRAULICA = "Desarrollo del calculo hidraulico (Fases 3 y 4)"
TITULO_TRAZA_HIDRAULICA_ULTIMO = ("Desarrollo del calculo hidraulico del "
                                  "ultimo escalon evaluado (Fases 3 y 4)")
TITULO_TRAZA_VERIFICACIONES = "Desarrollo de cada verificacion"
# --- T-4 --- La matriz de durabilidad (Sec. 3.3 de la hoja de ruta).
TITULO_DURABILIDAD = "Durabilidad de los materiales (Sec. 3.3)"
# El nombre de la etapa, que es el de `servicio.ETAPA_DURABILIDAD`. Se repite
# aqui y no se importa porque M11 no importa del servicio (la capa de reporte
# no conoce la orquestacion); `tests/test_t4_materiales_durabilidad.py`
# comprueba que los dos textos sean el mismo.
ETAPA_DURABILIDAD = "matriz de durabilidad (Sec. 3.3)"
TITULO_TRAZA_DURABILIDAD = "Desarrollo de la matriz de durabilidad (Sec. 3.3)"
# --- VE-7, lote C (C4; VE5-CAT-03; decision del consultor Fable, triaje
# VE-7, 2026-11-20) --- la Fase 0-bis con seccion propia. La etapa es la de
# `ML_licuefaccion.ETAPA_LICUEFACCION` (y la de `servicio`); se repite aqui por
# la misma razon que la de durabilidad, y
# `tests/test_ve7_lote_c_licuefaccion.py` comprueba que sea el mismo texto.
TITULO_LICUEFACCION = ("Fase 0-bis: licuefaccion (AASHTO 10.5.4.2; resultado "
                       "del EMS, E.050 38.3)")
ETAPA_LICUEFACCION = ("evaluacion de licuefaccion (Fase 0-bis; AASHTO "
                      "10.5.4.2, E.050 38.3)")
TITULO_TRAZA_LICUEFACCION = "Desarrollo de la Fase 0-bis"
TEXTO_LICUEFACCION_BLOQUEADA = (
    "La Fase 0-bis no se cerro en este punto: el motivo y el dato que la "
    "destraba estan en la tabla de bloqueos. Mientras siga abierta, el "
    "expediente no cierra.")
# --- T-6 --- los pasos de 7.B (pendiente, esviaje, longitud, cota de salida
# y encaje), que hasta T-6 iban como una frase con los numeros dentro.
TITULO_TRAZA_GEOMETRIA = "Desarrollo de la geometria del conducto (Sec. 7.B)"
TITULO_TRAZA_GEOMETRIA_PREVIA = ("Longitud del conducto calculada antes del "
                                 "diseño (Sec. 7.B)")
# --- T-9 --- los pasos de la Fase 10: capacidad de la cuneta, caudal por
# metro, longitud por capacidad y espaciamiento maximo.
TITULO_TRAZA_ESPACIAMIENTO = ("Desarrollo del espaciamiento maximo entre "
                              "alivios (Fase 10)")


def traza_clasificacion(informe: Any) -> Tuple[Any, ...]:
    """Los pasos de la Fase 2 que la memoria publica: luz y periodo de retorno."""
    clasificacion = getattr(informe, "clasificacion", None)
    if clasificacion is None:
        return ()
    pasos = []
    luz = getattr(clasificacion.verificacion_luz, "paso", None)
    if luz is not None:
        pasos.append(luz)
    tr = getattr(clasificacion.periodo_retorno, "paso", None)
    if tr is not None:
        pasos.append(tr)
    return tuple(pasos)


def traza_hidrologia(informe: Any) -> Tuple[Any, ...]:
    """
    Los pasos de la Fase 1-bis que la memoria publica (T-1): los ocho de la
    memoria hidrologica cuando el caudal se calculo, o solo el del caudal
    especifico cuando entro declarado. Vacio en la Familia C y cuando el
    calculo se detuvo antes de producir un caudal.
    """
    caudal = getattr(informe, "caudal", None)
    return () if caudal is None else tuple(caudal.pasos)


def traza_durabilidad(informe: Any) -> Tuple[Any, ...]:
    """
    Los pasos de la matriz de durabilidad del punto (Sec. 3.3; T-4): uno por
    ensayo declarado y, si el suelo de fundacion esta en el conjunto
    declarado deficiente, el del aviso de marco. Vacia sin ensayos y sin
    aviso, y tambien cuando la etapa se bloqueo.
    """
    dictamen = getattr(informe, "durabilidad", None)
    return () if dictamen is None else tuple(dictamen.pasos)


def traza_licuefaccion(informe: Any) -> Tuple[Any, ...]:
    """
    --- VE-7, lote C (C4) --- El paso de la Fase 0-bis del punto
    (`InformePunto.licuefaccion`): vacia si la fase no corrio (perfil, punto
    sin clasificar) o si su etapa se bloqueo.
    """
    v = getattr(informe, "licuefaccion", None)
    paso = getattr(v, "paso", None)
    return () if paso is None else (paso,)


def traza_espaciamiento(informe: Any) -> Tuple[Any, ...]:
    """
    --- T-9 --- Los pasos de la Fase 10 que la memoria publica: la capacidad
    de la cuneta, los de la longitud por capacidad --si se calculo-- y el del
    espaciamiento maximo. Los de VB1 y VB2 van con las verificaciones del
    punto, y los del caudal calculado, con la Fase 1-bis (no se repiten: H11
    de la auditoria de T-9).
    """
    # --- T-9 (correcciones, H1) --- la capacidad de la cuneta tiene casa
    # propia (`aporte_alivio`, VB2) y se calcula tambien con la longitud
    # declarada: va primero, y una sola vez aunque la longitud calculada la
    # lleve tambien (el MISMO objeto).
    pasos: list = []
    aporte = getattr(informe, "aporte_alivio", None)
    if aporte is not None:
        pasos.extend(aporte.pasos)
    espaciamiento = getattr(informe, "espaciamiento", None)
    if espaciamiento is not None:
        pasos.extend(p for p in espaciamiento.pasos
                     if not any(p is q for q in pasos))
    return tuple(pasos)


def traza_geometria(informe: Any) -> Tuple[Tuple[Any, ...], bool]:
    """
    (pasos, previa): los pasos de la Sec. 7.B que la memoria publica (T-6).

    Si el punto llego a 7.B son los de `CompatibilidadGeometrica.pasos`
    --pendiente adoptada, factor de esviaje, longitud, caida y cota de
    salida, encaje-- y `previa` es False. Si NO llego (no dimensiono), la
    longitud ya se habia calculado antes de la Fase 4 y sus pasos se publican
    igual, con `previa` True para que el consumidor lo diga: es calculo que
    el pipeline hizo y que entro al control de salida de cada escalon.
    """
    geometria = getattr(informe, "geometria", None)
    if geometria is not None:
        return tuple(getattr(geometria, "pasos", ())), False
    calculada = getattr(informe, "longitud_calculada", None)
    if calculada is None:
        return (), False
    return tuple(calculada.pasos), True


def traza_tw(informe: Any) -> Optional[Any]:
    """El paso de la Sec. 1.3, o None si el TW no llego a determinarse."""
    tw = getattr(informe, "tw_sec13", None)
    return None if tw is None else getattr(tw, "paso", None)


def traza_hidraulica(informe: Any) -> Tuple[Tuple[Any, ...], Optional[Any]]:
    """
    (pasos, escalon): los pasos hidraulicos que la memoria publica, y el
    escalon del que salen cuando NO son los de un diseño adoptado.

    `escalon` es None si el punto cerro y los pasos son los de su resultado.
    Si no cerro, se toma el ULTIMO escalon del bucle que llego a resolver la
    hidraulica, y se devuelve para que el consumidor lo DIGA: publicar ese
    desarrollo sin avisar que no es el de un diseño adoptado seria la trampa
    de NOR-MEM-01 al reves.
    """
    resultado = getattr(informe, "resultado", None)
    if resultado is not None and resultado.resultado_hidraulico is not None:
        return tuple(resultado.resultado_hidraulico.pasos), None
    escalones = [p for p in getattr(informe, "traza", ())
                 if getattr(p, "resultado_hidraulico", None) is not None]
    if not escalones:
        return (), None
    ultimo = escalones[-1]
    return tuple(ultimo.resultado_hidraulico.pasos), ultimo


def verificaciones_publicadas(informe: Any) -> Tuple[Tuple[str, Any], ...]:
    """
    Las verificaciones que la memoria publica para un punto, con su fase.

    `informe.verificaciones()` solo trae las del RESULTADO ADOPTADO, y un
    punto sin dimensionar no tiene ninguno. Las de la Fase 5 que si se
    evaluaron viven en el ultimo escalon de la traza, y son justamente las que
    explican por que se descarto --- ver el comentario de `_tabla_
    verificaciones`, que es de donde esta seleccion se extrajo en G4.
    """
    verificaciones = tuple(informe.verificaciones())
    if not getattr(informe, "dimensionado", True):
        escalones = [p for p in getattr(informe, "traza", ())
                     if getattr(p, "verificaciones", ())]
        if escalones:
            ultimo = escalones[-1]
            verificaciones = verificaciones + tuple(
                (f"Fase 5 - ultimo escalon evaluado ({ultimo.material}, "
                 f"{ultimo.seccion.etiqueta()})", v)
                for v in ultimo.verificaciones)
    return verificaciones
