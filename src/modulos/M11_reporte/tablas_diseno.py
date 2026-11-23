# -*- coding: utf-8 -*-
"""
M11_reporte.tablas_diseno
=========================
Submodulo de Fase 11 (`M11_reporte`): bloque `tablas_diseno` (D3).
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Sequence,
    Tuple,
)
from src.constantes_normativas import (
    H_O_HW_SOBRE_D_CAUTELA,
    H_O_HW_SOBRE_D_MIN,
    H_O_NUMERAL,
)
from src.normativa import fundamentos as _fundamentos
from src.modulos import M2_material as _M2
from src.modelos import (
    ControlGobernante,
    MOTIVO_METODO_NO_EVALUABLE,
)

from src.modulos.M11_reporte._base import (
    CAMPOS_CSV,
    DATOS_DECLARADOS,
    FMT_2,
    FMT_4,
    VACIO,
    _esc,
    _etiqueta_html,
    _num,
    rotulo_norma_producto,
)
from src.modulos.M11_reporte.trazas import (
    TITULO_CAUDAL_DE_DISENO,
)

# ===========================================================================
# 1. Memoria por punto
# ===========================================================================

def _fila(celdas: Sequence[str], clase: str = "") -> str:
    atributo = f' class="{clase}"' if clase else ""
    return f"<tr{atributo}>" + "".join(celdas) + "</tr>"


def _td(contenido: str, clase: str = "") -> str:
    atributo = f' class="{clase}"' if clase else ""
    return f"<td{atributo}>{contenido}</td>"


def _tabla_datos(informe: Any) -> str:
    """
    Datos de partida del punto CON SU FUENTE (entregable 1).

    La fuente no es decorativa: un dato de la columna del CSV y un dato
    declarado en el JSON de la corrida se corrigen en sitios distintos, y el
    TW puede venir ademas de un criterio adoptado. La memoria tiene que decir
    cual es cual.
    """
    punto = informe.punto
    filas = [_fila([f"<th>{_esc(punto.id)}</th>", "<th>Valor</th>",
                    "<th>Unidad</th>", "<th>Fuente</th>"])]

    for campo, rotulo, unidad in CAMPOS_CSV:
        bruto = getattr(punto, campo)
        if hasattr(bruto, "value"):                       # enumeraciones
            texto = _esc(bruto.value)
        elif isinstance(bruto, str):
            texto = _esc(bruto)
        else:
            texto = _num(bruto)
        fuente = f"CSV Sec. 1.2, columna <code>{_esc(campo)}</code>"
        if bruto is None:
            fuente = (f'<span class="pendiente">columna '
                      f'<code>{_esc(campo)}</code> vacia</span> '
                      "&mdash; dato de un tablero externo")
            caudal = getattr(informe, "caudal", None)
            if campo == "Q_m3s" and caudal is not None and caudal.calculado:
                # T-1: la celda va vacia porque el caudal lo CALCULA la Fase
                # 1-bis; decir «tablero externo» seria falso.
                fuente = (f"columna <code>{_esc(campo)}</code> vacia &mdash; "
                          f"{_esc(caudal.leyenda)}: Q = {_num(caudal.Q_m3s)} "
                          f"m³/s (ver «{_esc(TITULO_CAUDAL_DE_DISENO)}»)")
        filas.append(_fila([_td(_esc(rotulo)), _td(texto, "num"),
                            _td(_esc(unidad)), _td(fuente)]))

    for atributo, rotulo, unidad in DATOS_DECLARADOS:
        dato = getattr(informe, atributo, None)
        if dato is None:
            # "sin resolver", no "no declarado": un dato puede haberse pasado
            # en la corrida y no llegar aqui porque la etapa que lo fija quedo
            # bloqueada antes. Decir "no declarado" acusaria al expediente de
            # una falta que puede no tener.
            filas.append(_fila([
                _td(_esc(rotulo)), _td(VACIO, "num"), _td(_esc(unidad)),
                _td('<span class="pendiente">sin resolver en esta corrida'
                    "</span> &mdash; el dato no se declaro o la etapa que lo "
                    "fija quedo bloqueada (ver las etapas bloqueadas)")]))
            continue
        valor = dato.valor
        texto = _esc(valor) if isinstance(valor, str) else _num(valor)
        filas.append(_fila([_td(_esc(rotulo)), _td(texto, "num"),
                            _td(_esc(unidad)), _td(_esc(dato.origen))]))

    return '<table class="compacta">' + "".join(filas) + "</table>"


def _tabla_clasificacion(informe: Any) -> str:
    """Fase 2: denominacion por luz y periodo de retorno, con sus numerales."""
    clasificacion = informe.clasificacion
    if clasificacion is None:
        return ""
    tr = clasificacion.periodo_retorno
    if tr.anios is None:
        # --- T-10 --- con su numeral, que el JSON publica (`TR_numeral`)
        texto_tr = (f'<span class="pendiente">no procede</span> &mdash; '
                    f"{_esc(tr.fundamento)}"
                    + (f" ({_esc(tr.numeral)})" if tr.numeral else ""))
    else:
        categoria = "" if tr.categoria is None else f" ({_esc(tr.categoria.value)})"
        # Sin anteponer "num.": `NUMERAL_TR` dejo de ser un numeral desnudo
        # al cerrarse NOR-HID-08 y ya trae el suyo dentro, de modo que el
        # prefijo imprimia "num. MC-HHD (...), num. 3.6".
        texto_tr = (f"<b>{tr.anios} años</b>{categoria} &mdash; "
                    f"{_esc(tr.numeral)}. {_esc(tr.fundamento)}")

    filas = [
        _fila([_td("<b>Denominacion</b>"),
               _td(f"{_esc(clasificacion.denominacion.value)} &mdash; luz "
                   f"{_num(clasificacion.luz_m, FMT_2)} m, num. "
                   f"{_esc(clasificacion.verificacion_luz.numeral)}")]),
        _fila([_td("<b>Familia</b>"),
               _td(f"{_esc(clasificacion.perfil.nombre)} &mdash; caudal de "
                   f"{_esc(clasificacion.perfil.origen_del_caudal)} "
                   f"(num. {_esc(clasificacion.perfil.numeral)})")]),
        _fila([_td("<b>Periodo de retorno</b>"), _td(texto_tr)]),
    ]
    return "<h4>Fase 2 &mdash; Clasificacion y periodo de retorno</h4>" \
           '<table class="compacta">' + "".join(filas) + "</table>"


def _tabla_iteraciones(informe: Any) -> str:
    """
    Iteraciones del diseño (entregable 1): los escalones que MD probo, en
    orden, con el motivo de cada descarte.

    Sin traza no se imprime una tabla vacia: se dice que no se registro. Una
    tabla vacia se lee como "no hubo iteraciones", que es falso.
    """
    traza = tuple(getattr(informe, "traza", ()) or ())
    if not traza:
        return ('<div class="nota"><p>No se registro traza de iteraciones para '
                "este punto: el bucle de diseño no llego a correr (ver los "
                "bloqueos) o la corrida no la solicito.</p></div>")

    # LA COLUMNA DICE LA SECCION, NO UN DIAMETRO (C8, punto 2). Con «D (m)»
    # los tres escalones de un catalogo de marcos salian «0.90 / 1.20 / 1.50»
    # y el revisor no podia saber que luz se descarto en cada uno.
    filas = [_fila(["<th>#</th>", "<th>Material</th>", "<th>Seccion</th>",
                    "<th>Resultado</th>", "<th>Motivo del descarte</th>"])]
    for indice, paso in enumerate(traza, start=1):
        if paso.aceptado:
            resultado = '<span class="cumple">adoptado</span>'
            motivo = "pasa todas las verificaciones de la Fase 5"
        else:
            resultado = '<span class="incumple">descartado</span>'
            motivo = _esc(paso.motivo)
        clase = "fila-aceptada" if paso.aceptado else ""
        filas.append(_fila([_td(str(indice), "num"), _td(_esc(paso.material)),
                            _td(_esc(paso.seccion.etiqueta())), _td(resultado),
                            _td(motivo)], clase))
    return "<h4>Iteraciones del diseño (Fases 3-5)</h4>" \
           '<table class="compacta">' + "".join(filas) + "</table>"


AVISO_SIN_DIMENSIONAR = ('<div class="bloqueo"><p>El punto <b>no llego a '
                         "dimensionarse</b>. El motivo esta en la tabla de "
                         "bloqueos.</p></div>")

# --- T-12 (ficha T11-09) --- Lo que la fila «Control gobernante» dice de la
# salida cuando el perfil descarto la aproximacion y su remanso no alcanza la
# entrada: la MISMA redaccion que la linea «Control» de la CLI
# (`cli._lineas_punto`), sobre la MISMA condicion, leida del dato
# (`ResultadoHidraulico.salida_no_se_forma`).
SALIDA_NO_SE_FORMA = "salida no se forma: el perfil no alcanza la entrada"


def _celda_control_gobernante(hidraulica: Any) -> str:
    """
    La celda de la fila «Control gobernante», compartida por las dos vistas
    de la memoria. Formato, no calculo: el HW que gobierna y los dos
    controles salen de M4; si la salida no se forma (T11-09) no se imprime
    como «salida» la aproximacion descartada, que la fila del perfil sigue
    publicando rotulada como HW<sub>aprox</sub>.
    """
    salida = (SALIDA_NO_SE_FORMA
              if getattr(hidraulica, "salida_no_se_forma", False) is True
              else f"salida {_num(hidraulica.HW_salida)}")
    return (f"{_esc(hidraulica.control_gobernante.value)} &mdash; "
            f"HW = {_num(hidraulica.HW)} m (entrada "
            f"{_num(hidraulica.HW_entrada)} / {salida})")


def _tabla_diseno(informe: Any) -> str:
    """La combinacion adoptada: material, diametro e hidraulica gobernante."""
    if not informe.dimensionado:
        return AVISO_SIN_DIMENSIONAR
    resultado = informe.resultado
    hidraulica = resultado.resultado_hidraulico
    filas = list(_filas_combinacion_adoptada(informe))
    return _tabla_diseno_con_perfil(hidraulica, filas)


def _filas_combinacion_adoptada(informe: Any) -> Tuple[str, ...]:
    """
    --- T-12 --- Las filas de la combinacion adoptada (material, norma de
    producto, rugosidad, seccion, hidraulica y control gobernante), las
    MISMAS para la memoria completa y para la resumida: un solo formateador,
    para que la resumida no publique un numero que la completa no tenga.
    Solo para un punto dimensionado.
    """
    resultado = informe.resultado
    material, hidraulica = resultado.material, resultado.resultado_hidraulico
    filas = [
        _fila([_td("<b>Material</b>"),
               _td(f"{_esc(material.nombre)} (<code>"
                   f"{_esc(material.tipo.value)}</code>) &mdash; "
                   f"{_esc(rotulo_norma_producto(material))}, EG-2013 Seccion "
                   f"{_esc(material.seccion_eg2013)}")]),
        # --- T-10 --- Lo que la norma de producto dice cubrir (EXT-N-03): el
        # JSON lo publicaba desde EXT-6 y la memoria no. Sale de M2.
        _fila([_td("<b>Alcance de la norma de producto</b>"),
               _td(_esc(_M2.alcance_norma_producto_de(material.tipo,
                                                      material.forma)))]),
        # --- VE-5 (ficha VE2-A, abierto (2)) --- el rotulo no supone la
        # regla ni la tabla: con la columna NORMAL o el n unico del HDS-5 el
        # n no sale de la «regla de doble n», y la fila del marco es de la
        # Tabla B.1 del HDS-5 o el par del encofrado. Que regla y que fuente
        # rigen lo dice `Material.fila_manning`, que M2 escribe para cada caso.
        _fila([_td("<b>Rugosidad (n de Manning)</b>"),
               _td(f"n para capacidad y tirante = {_num(material.n_max)}; "
                   f"n para velocidad maxima y socavacion = "
                   f"{_num(material.n_min)}. Fila o fuente del n: "
                   f"{_esc(material.fila_manning)}")]),
        # EL TITULAR DICE LA SECCION, NO UN DIAMETRO. Decia «Diametro
        # adoptado D = 0.900 m» sobre un marco de 1.20 x 0.90, que es la
        # forma mas visible del defecto que C8 cierra: el escalar `D` vale la
        # ALTURA en un cajon, de modo que la linea era numericamente cierta y
        # geometricamente falsa --- y ademas perdia la luz, que es la mitad
        # que gobierna la capacidad. La etiqueta la construye la seccion
        # (`Seccion.etiqueta`), no esta capa: M11 no compone magnitudes.
        _fila([_td("<b>Seccion adoptada</b>"),
               _td(f"{_esc(resultado.seccion.etiqueta())} (interior) "
                   f"&mdash; dimension maxima de CATALOGO adoptada: "
                   f"{_num(material.D_max, FMT_2)} m &mdash; "
                   f"{_esc(material.D_max_de_catalogo)}")]),
        # Q y S son los del DISEÑO, no los de la columna del CSV: la Familia B
        # y la C traen su propio caudal (Sec. 2.3) y el punto que no sigue el
        # cauce declara su pendiente. La S iba SIN imprimir y la memoria
        # quedaba sin poder recomputar la caida ni la cota de salida de la
        # Fase 7: la unica pendiente del entregable era la columna S_cauce del
        # bloque de datos de partida, que en esos puntos NO es la del diseño
        # (MAT-D9). Va aqui, al lado de Q, por la misma razon que Q.
        # EL REPARTO ENTRE CELDAS SE DICE AQUI TAMBIEN (EXT-M-03): el y_n y las
        # velocidades de esta fila son los de UNA celda, y sin N ni Q_celda la
        # fila yuxtaponia el Q del punto con un tirante que solo transporta
        # Q/N -- el mismo defecto que el paso de Manning tenia, mudado al
        # resumen (lo señalo el auditor adversarial de EXT-2). Los dos campos
        # llegan ya calculados por M4; aqui no se divide nada.
        _fila([_td("<b>Hidraulica</b>"),
               _td(f"Q = {_num(hidraulica.Q)} m3/s"
                   + (f" del punto, repartido entre N = "
                      f"{hidraulica.numero_celdas} celdas: Q<sub>celda</sub> = "
                      f"{_num(hidraulica.Q_celda_m3s)} m3/s, y los tirantes y "
                      f"velocidades de esta fila son los de UNA celda"
                      if hidraulica.numero_celdas != 1 else "")
                   + f" &middot; S = "
                   f"{_num(hidraulica.S, FMT_4)} m/m (la del diseño: la del "
                   "cauce salvo que el punto declare la suya) &middot; "
                   + (
                       # --- T-2 --- Barril horizontal: no hay tirante normal
                       # ni velocidades de Manning, y la fila lo DICE en vez
                       # de imprimir tres celdas vacias (INF-5.1.6).
                       "<b>barril HORIZONTAL</b>: no hay tirante normal ni "
                       "velocidad uniforme (HDS-5 num. 3.3.4); el tirante y "
                       "las velocidades del conducto salen del perfil de la "
                       "lamina y de la seccion de salida (pasos 4.1, 4.3b y "
                       f"4.3c) &middot; y<sub>c</sub> = "
                       f"{_num(hidraulica.y_critico)} m"
                       if getattr(hidraulica, "sin_tirante_normal", False) else
                       f"y<sub>n</sub> = "
                       f"{_num(hidraulica.y_normal)} m &middot; y<sub>c</sub> = "
                       f"{_num(hidraulica.y_critico)} m &middot; "
                       f"V<sub>erosion</sub> = "
                       f"{_num(hidraulica.V_erosion, FMT_2)} m/s (con n minimo "
                       f"y su propio tirante normal, contra el techo de V3) "
                       f"&middot; "
                       f"V<sub>sedimentacion</sub> = "
                       f"{_num(hidraulica.V_sedimentacion, FMT_2)} m/s (con n "
                       f"maximo, contra el piso de V2)"))]),
        _fila([_td("<b>Control gobernante</b>"),
               _td(_celda_control_gobernante(hidraulica))]),
    ]
    filas.extend(_filas_h_o(hidraulica))
    return tuple(filas)


def _filas_h_o(hidraulica: Any) -> List[str]:
    """
    --- T-12 (H6 de su auditoria) --- La fila «h_o fuera de rango» del punto,
    o ninguna. Vive aparte para que la lleven las DOS vistas de la memoria
    (es una fila de `_filas_combinacion_adoptada`): NOR-HDS-05 pide decirlo
    EN EL PUNTO, y la resumida es la vista que se imprime. Formato: todo sale
    de `ResultadoHidraulico` y de su `PerfilLamina`.
    """
    filas: List[str] = []
    # La condicion de uso de h_o, dicha EN EL PUNTO donde se incumple y no
    # solo como advertencia general del bloque 0-ter (NOR-HDS-05): un aviso
    # que no señala el punto afectado deja al revisor sin saber cual de ellos
    # esta calculado fuera del rango de su fuente, que es el "nadie se entera"
    # que el hallazgo denuncia. Desde E-A la fila lee ademas el perfil de la
    # lamina: bajo 0.75 la aproximacion NO se usa y el HW es el del remanso;
    # la primera condicion --barril lleno en la mayor parte-- viene MEDIDA.
    # Aqui se dice, no se decide ni se calcula: todo sale del `PerfilLamina`.
    perfil = hidraulica.perfil
    if hidraulica.h_o_requiere_cautela or hidraulica.h_o_fuera_de_rango:
        # `HW_sobre_D_salida` es el de la APROXIMACION (paso 4.3), que es el
        # cociente que las dos condiciones juzgan. Lo que el punto hace con
        # ella lo dice el perfil (E-A): bajo 0.75 no se usa y el HW es el
        # del remanso; en la banda de cautela manda el mayor de los dos.
        sustituida = perfil is not None and perfil.sustituye_aproximacion
        limite = (H_O_HW_SOBRE_D_MIN if sustituida or hidraulica.h_o_fuera_de_rango
                  else H_O_HW_SOBRE_D_CAUTELA)
        veredicto = ("NO DEBE USARSE" if sustituida or hidraulica.h_o_fuera_de_rango
                     else "PIDE CAUTELA")
        # LO QUE HACE LA CORRIDA CON ELLO lo decide `servicio.correr_punto` o
        # `M4.resolver_control`, no este formateador: aqui se dice, no se
        # decide. Sin perfil, bajo 0.75 el punto lleva el bloqueo «metodo no
        # evaluable» (EXT-3); con perfil (E-A) la bandera no puede estar en
        # True y el HW del punto es el del remanso.
        if hidraulica.h_o_fuera_de_rango:
            consecuencia = (
                f" El punto lleva por eso el bloqueo <b>{_esc(MOTIVO_METODO_NO_EVALUABLE)}"
                "</b>, que a nivel de perfil se difiere y a "
                "nivel de expediente impide cerrar: ver la tabla de etapas "
                "bloqueadas de este punto.")
        elif sustituida and perfil.alcanza_entrada:
            consecuencia = (
                " La aproximaci&oacute;n <b>no se usa</b>: el HW de este punto "
                f"es el del remanso del paso 4.3d, {_num(perfil.HW_remanso_m)} m "
                "(HDS-5 p&aacute;g. 3.12: «backwater calculations are required»).")
        elif sustituida:
            consecuencia = (
                " La aproximaci&oacute;n <b>no se usa</b> y el remanso del paso "
                "4.3d no alcanza la entrada: el control de salida no impone "
                "carga y gobierna la entrada.")
        elif perfil is not None and perfil.comprobacion_manda:
            consecuencia = (
                " La comprobaci&oacute;n por remanso del paso 4.3d pide "
                f"<b>m&aacute;s carga</b> ({_num(perfil.HW_remanso_m)} m) que la "
                f"aproximaci&oacute;n ({_num(perfil.HW_aproximado_m)} m), y del "
                "lado de la inundaci&oacute;n manda la mayor: el HW del punto es "
                "el del remanso.")
        elif perfil is not None:
            consecuencia = (
                " El HW de este punto es el de la aproximaci&oacute;n, y la "
                "comprobaci&oacute;n por remanso del paso 4.3d "
                + ("no alcanza la entrada." if not perfil.alcanza_entrada else
                   f"({_num(perfil.HW_remanso_m)} m) no pide m&aacute;s carga."))
        else:
            consecuencia = (
                " El HW de este punto esta calculado con ella igualmente, y por "
                "eso se dice aqui.")
        filas.append(_fila([
            _td("<b>h<sub>o</sub> fuera de rango</b>"),
            _td(f"El control de SALIDA gobierna este punto y la "
                f"aproximaci&oacute;n del paso 4.3 da HW/D = "
                f"{_num(hidraulica.HW_sobre_D_salida, FMT_2)}, por debajo de "
                f"{_num(limite, FMT_2)}: para ese HW/D, {_esc(H_O_NUMERAL)} dice "
                f"que la aproximacion h<sub>o</sub> = (d<sub>c</sub> + D)/2 "
                f"<b>{veredicto}</b>.{consecuencia}")]))
    return filas


def _tabla_diseno_con_perfil(hidraulica: Any, filas: List[str]) -> str:
    """
    La tabla de la combinacion adoptada de la memoria COMPLETA: las filas
    comunes (`_filas_combinacion_adoptada`, con la de h_o) mas la del perfil
    de la lamina, que la resumida no lleva (remite a la completa).
    """
    # La fila de h_o la lleva `_filas_combinacion_adoptada` (T-12, H6), que
    # la pone detras del control gobernante, como siempre.
    perfil = hidraulica.perfil
    if perfil is not None:
        gobierna_salida = (hidraulica.control_gobernante
                           is ControlGobernante.SALIDA)
        if not perfil.alcanza_entrada:
            remanso = (f"el remanso <b>no alcanza la entrada</b>: la curva S1 "
                       f"corta el tirante critico a "
                       f"{_num(perfil.x_fin_remanso_m, FMT_2)} m de la salida "
                       f"y aguas arriba el flujo es supercritico, controlado "
                       f"por la entrada")
        else:
            remanso = (f"HW por remanso = {_num(perfil.HW_remanso_m)} m "
                       f"(y<sub>entrada</sub> = {_num(perfil.y_entrada_m)} m)")
        if perfil.sustituye_aproximacion and gobierna_salida:
            papel = (" &mdash; <b>sustituye</b> a la aproximacion "
                     f"(HW<sub>aprox</sub> = {_num(perfil.HW_aproximado_m)} m, "
                     f"HW<sub>aprox</sub>/D &lt; {_num(H_O_HW_SOBRE_D_MIN, FMT_2)}: "
                     f"{_esc(H_O_NUMERAL)} dice que no debe usarse y la pag. "
                     "3.12 manda el remanso)")
        elif perfil.sustituye_aproximacion:
            papel = (" &mdash; la aproximacion "
                     f"(HW<sub>aprox</sub> = {_num(perfil.HW_aproximado_m)} m) "
                     "esta fuera de su rango y no compite: gobierna la entrada")
        elif gobierna_salida and perfil.comprobacion_manda:
            papel = (" &mdash; <b>manda</b>: en la banda de cautela la "
                     "comprobacion pide mas carga que la aproximacion "
                     f"(HW<sub>aprox</sub> = {_num(perfil.HW_aproximado_m)} m)")
        elif gobierna_salida:
            papel = (" &mdash; comprobacion de la aproximacion del paso 4.3, "
                     "que sigue siendo la carga del punto")
        else:
            papel = " &mdash; gobierna la entrada"
        filas.append(_fila([
            _td("<b>Perfil de la l&aacute;mina</b> (paso 4.3c/4.3d)"),
            _td(f"Perfil <b>{_esc(perfil.tipo.value)}</b> por paso directo "
                f"desde la salida (HDS-5 p&aacute;g. 3.12, Secci&oacute;n 3.5). "
                f"El barril fluye a secci&oacute;n llena en "
                f"{_num(perfil.longitud_llena_m, FMT_2)} m "
                f"(fracci&oacute;n {_num(perfil.fraccion_llena, FMT_2)} de su "
                f"longitud): la primera condici&oacute;n de uso de h<sub>o</sub> "
                f"&mdash;lleno en la mayor parte&mdash; est&aacute; "
                f"<b>medida</b>, no declarada. {remanso}{papel}. "
                f"y<sub>max</sub> = {_num(perfil.y_max_m)} m y "
                f"V<sub>min</sub> = {_num(perfil.V_min_m_s, FMT_2)} m/s son lo "
                "que V1 y V2 comparan bajo control de salida.")]))
    return "<h4>Fases 3-5 &mdash; Combinacion adoptada</h4>" \
           '<table class="compacta">' + "".join(filas) + "</table>"


# ===========================================================================
# La traza: M11 FORMATEA lo que el calculo emitio
# ---------------------------------------------------------------------------
# Aqui esta el cambio de fondo de la §4.4. Hasta S18 este modulo RECONSTRUIA
# la memoria leyendo resultados, y para reconstruirla calculaba (`y/D` en dos
# sitios, contra su propio docstring de modulo: SIS-A-07). Ahora los modulos
# de calculo emiten `PasoDeMemoria` --- que ya trae de donde salio cada
# numero, contra que se compara y con que margen --- y estas funciones solo lo
# escriben en HTML.
#
# LA REGLA TIPOGRAFICA, que es lo que NOR-HID-04 pide y no una preferencia de
# estilo: tres clases distintas y nunca en el mismo parrafo.
#
#   .fuente          lo que el documento DICE, entre comillas y con su cita
#   .interpretacion  lo que el PROYECTO lee en ella
#   (texto normal)   lo que el proyecto HACE
#
# Pegadas, las tres se leen como norma. El caso testigo: «el rango recorre la
# calidad del revestimiento» no esta en el Manual --- nada dice por que hay
# dos numeros --- y se imprimia dentro del mismo parrafo que la cita.

def sin_fundamento_por_codigo() -> Dict[str, Tuple[str, str]]:
    """
    El censo de `normativa.fundamentos.SIN_FUNDAMENTO`, indexado por codigo de
    verificacion.

    Existe para que un paso AUSENTE se imprima con su razon en el sitio donde
    estaria, en vez de dejar el hueco callado. Un hueco callado en una memoria
    se lee como un olvido; con la razon delante se lee como lo que es --- una
    verificacion que hoy no puede tener fundamento normativo --- y ademas dice
    que haria falta para traerlo.

    Publico desde G4: `traza_punto` declara el mismo hueco en la GUI, y dos
    indexaciones del mismo censo son dos que pueden divergir.
    """
    salida = {}
    for id_paso, por_que, que_haria_falta in _fundamentos.SIN_FUNDAMENTO:
        salida[id_paso.split(".")[-1]] = (por_que, que_haria_falta)
    return salida


# --- T-10 --- Lo que una etapa sin completar ES, en palabras, al lado del
# tipo tecnico: «espera un dato» y «metodo no evaluable» no son NO CUMPLE ni
# CUMPLE, y la memoria tiene que distinguirlos a la vista (PRECISIONES de
# T-10). Es presentacion: el tipo lo decide `modelos.TipoDeBloqueo`.
ROTULO_TIPO_DE_BLOQUEO: Dict[str, str] = {
    "CriterioPendienteError": "espera una declaracion (criterio pendiente)",
    "DatoFaltanteError": "espera un dato que falta",
    "DatoInvalidoError": "un dato no puede ser: hay que corregirlo",
    "LimiteNumericoError": "la aritmetica no cabe con estos datos",
    "MetodoNoEvaluableError": "metodo no evaluable: hace falta otro metodo",
    "DisenoNoFactibleError": "ningun escalon cumple: diseño no factible",
    "DiferidoPorAlcance": "diferido por el alcance de la corrida",
}


def _tabla_bloqueos(bloqueos: Sequence[Any]) -> str:
    """Etapas que no se pudieron completar, con la causa del expediente."""
    if not bloqueos:
        return ""
    partes = ["<h4>Etapas bloqueadas</h4>"]
    for b in bloqueos:
        detalle = _esc(b.mensaje)
        if b.criterio:
            detalle = (f"falta declarar {_etiqueta_html(b.etiqueta or '')} "
                       f"<code>{_esc(b.criterio)}</code> &mdash; "
                       f"{_esc(b.concepto)}<br>Fuente: {_esc(b.fuente)}")
        elif b.campo:
            detalle = f"campo <code>{_esc(b.campo)}</code>: {_esc(b.mensaje)}"
        rotulo = ROTULO_TIPO_DE_BLOQUEO.get(b.tipo.value, "")
        partes.append(
            f'<div class="bloqueo"><p><b>{_esc(b.fase)}</b> &rarr; '
            f"{_esc(b.etapa)} <i>({_esc(b.tipo.value)})</i>"
            + (f' <span class="estado-etapa">{_esc(rotulo)}</span>'
               if rotulo else "")
            + f"<br>{detalle}</p></div>")
    return "".join(partes)
