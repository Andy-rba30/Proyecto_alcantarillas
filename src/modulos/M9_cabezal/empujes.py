# -*- coding: utf-8 -*-
"""
M9_cabezal.empujes
==================
Submodulo de Fase 9 (`M9_cabezal`): bloque `empujes` (D1).
"""

from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple

from src import (
    criterios_adoptados as ca,
    datos_sitio as ds,
)
from src.constantes_fisicas import (
    GAMMA_AGUA_KN_M3,
    PIE_EN_METROS,
)
from src.constantes_normativas import (
    CARGA_VIVA,
    FACTOR_MURO_CON_REDUCCION,
    FACTOR_MURO_DECLARACIONES,
    F_PGA_CLASES_EN_ROCA,
    F_PGA_EXIGE_ESTUDIO_DE_SITIO,
    F_PGA_TABLA,
    F_PGA_TABLA_PGA_COLUMNAS,
    H_EQ_BORDE_UMBRAL_M,
    H_EQ_ESTRIBO_PERPENDICULAR_FT,
    H_EQ_MURO_PARALELO_FT,
    K_H0_FACTOR_ROCA_A_B,
    K_V_CASO_RESERVADO,
    K_V_DECLARACION_PRESCRITO,
    K_V_PRESCRITO,
    LECTURAS_COLUMNA_EXTREMA,
    LECTURA_COLUMNA_EXTREMA_ESTRICTA,
    NUMERAL_FACTOR_MURO,
    NUMERAL_F_PGA_TABLA,
    NUMERAL_KA_COULOMB,
    NUMERAL_K_H0,
    NUMERAL_P_IR,
    NUMERAL_SOBRECARGA_TRASDOS,
    NUMERAL_SOBRECARGA_TRASDOS_AASHTO,
    ORIENTACIONES_TABULADAS,
    ORIENTACION_PARALELO_AL_TRAFICO,
    ORIENTACION_PERPENDICULAR_AL_TRAFICO,
    P_SEIS_COMBINACIONES,
    P_SEIS_PISO_ESTATICO,
    REDUCCION_KH_POR_DESPLAZAMIENTO,
    SOBRECARGA_TRASDOS_PISO_MP_M,
)
from src.modelos import (
    CadenaSismica,
    CasoDemandaSismica,
    CondicionAnalisis,
    DatoInvalidoError,
    DemandaSismicaCabezal,
    DisenoNoFactibleError,
    EmpujeMononobeOkabe,
    EmpujesTrasdos,
    EntornoDelCabezal,
    FuerzaInerciaMuro,
    GeometriaCabezal,
    PasoSismico,
    REGIMEN_RESISTENCIA_CEDENTE,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

from src.modulos.M9_cabezal._criterios import (
    CALCULADO,
    CRITERIO_BETA_MURO,
    CRITERIO_BRAZO_SISMICO,
    CRITERIO_DELTA_MURO,
    CRITERIO_FACTOR_MURO,
    CRITERIO_F_PGA,
    CRITERIO_F_PGA_LECTURA,
    CRITERIO_GAMMA_CONCRETO,
    CRITERIO_GAMMA_RELLENO,
    CRITERIO_H_EQ_BAJO_TABLA,
    CRITERIO_H_EQ_BANDA_BORDE,
    CRITERIO_I_RELLENO,
    CRITERIO_K_V,
    CRITERIO_PHI_RELLENO,
    CRITERIO_REGIMEN_RESISTENCIA,
    DATO_SITIO_PGA,
    ETIQUETA_CALCULADO,
    H_EQ_BAJO_TABLA_EXTRAPOLAR,
    H_EQ_BAJO_TABLA_PRIMERA_FILA,
    H_EQ_BANDA_INTERPOLA,
    H_EQ_BANDA_LEE_COLUMNA_CERO,
    NUMERAL_9_2,
    NUMERAL_F_PGA,
    NUMERAL_MO,
    NUMERAL_PGA,
    es_paralelo_a_la_via,
)

# ===========================================================================
# 9.2 - CADENA SISMICA DESAGREGADA
# Un paso, una funcion. Ver "Por que la cadena sismica va desagregada".
# ===========================================================================

def pga_roca_b() -> float:
    """
    Paso 1: PGA, aceleracion pico en roca Clase B para Tr = 1000 anios, en g.

    [S] leido del dato de sitio 'PGA_roca_B' -- vive en datos_sitio.py y no en
    constantes_normativas porque, aunque el mapa es normativo, el valor
    depende de la coordenada sobre la que se lea y esa lectura es trazabilidad
    del proyecto (Sec. 9.2, Apendice A3 del Manual de Puentes). Esa frase, que
    este docstring venia diciendo desde el principio, es exactamente la
    definicion de la etiqueta [S]; hasta la quinta etiqueta el valor figuraba
    como [N], que era la unica de las cuatro que no le corresponde.
    """
    return ds.valor(DATO_SITIO_PGA)


def clases_de_sitio_plausibles() -> Tuple[str, ...]:
    """
    Las FILAS de la Tabla 2.4.3.11.2.1.2-1 sobre las que este proyecto lee el
    factor de sitio ([A], criterio 'F_pga').

    Es el reparto R1 del proyecto -- la tabla es [N], la eleccion de fila es
    [A] -- aplicado por fin a F_pga. El criterio guardaba el RESULTADO (1.0),
    que es el mismo defecto que tenia 'factores_carga_aashto' antes de C03: un
    numero suelto no puede expresar de que filas salio ni que pasa cuando la
    campana geotecnica cierre la clase. Ahora guarda las filas, y el numero
    lo calcula `f_pga`.

    Se rechaza, con `DatoInvalidoError`:
      * una fila que no existe en la tabla;
      * una declaracion vacia;
      * la fila F, que la tabla marca con asterisco y sin factor: elegirla no
        es leer un valor, es leer una exigencia de estudio (Nota 2).
    """
    elegidas = ca.valor(CRITERIO_F_PGA)
    if isinstance(elegidas, str) or not isinstance(elegidas, (tuple, list)):
        raise DatoInvalidoError(
            campo=CRITERIO_F_PGA, valor=elegidas,
            motivo=f"la declaracion tiene que ser la tupla de filas de "
                   f"{NUMERAL_F_PGA_TABLA} sobre las que se lee el factor, "
                   f"no un factor ya resuelto",
        )
    if not elegidas:
        raise DatoInvalidoError(
            campo=CRITERIO_F_PGA, valor=elegidas,
            motivo="no declara ninguna fila: sin fila no hay factor que leer",
        )
    for clase in elegidas:
        if clase not in F_PGA_TABLA:
            raise DatoInvalidoError(
                campo=CRITERIO_F_PGA, valor=clase,
                motivo=f"no es una fila de {NUMERAL_F_PGA_TABLA}: "
                       f"{', '.join(sorted(F_PGA_TABLA))}",
            )
        if F_PGA_EXIGE_ESTUDIO_DE_SITIO in F_PGA_TABLA[clase]:
            raise DatoInvalidoError(
                campo=CRITERIO_F_PGA, valor=clase,
                motivo=f"la fila '{clase}' de {NUMERAL_F_PGA_TABLA} no trae "
                       f"factor: la fuente le pone asterisco en las cinco "
                       f"columnas y su Nota 2 exige investigaciones "
                       f"geotecnicas especificas del sitio y analisis de "
                       f"respuesta dinamica. No hay numero que leer ahi. Si "
                       f"esa es la fila que el expediente se atribuye, "
                       f"entonces lo que hay que declarar no es un factor de "
                       f"tabla sino la adopcion de seguir sin el, que es "
                       f"materia de la premisa abierta y no de este criterio",
            )
    return tuple(elegidas)


def _pga_en_rotulo_extremo(PGA: float) -> bool:
    """
    Si el PGA cae JUSTO sobre uno de los dos rotulos extremos de la tabla de
    F_pga, que son los unicos puntos donde la lectura declarada en
    'F_pga_lectura_columna_extrema' cambia algo.

    Existe para que la condicion que el informe imprime diga la verdad en los dos
    casos: con PGA = 0.50 la lectura del borde gobierna, y con un PGA
    interior no gobierna nada y decir que si seria falso.
    """
    limites = F_PGA_TABLA_PGA_COLUMNAS
    return any(math.isclose(PGA, x, abs_tol=TOL_UMBRAL_NORMATIVO)
               for x in (limites[0], limites[-1]))


def factor_sitio_desde_tabla(*, clase: str, PGA: float,
                             lectura_extremos: str) -> float:
    """
    F_pga de UNA fila de la Tabla 2.4.3.11.2.1.2-1 para un PGA dado, aplicando
    su Nota 1 ("usar linea recta de interpolacion para valores intermedios de
    PGA").

    Los cinco numeros de los rotulos -- 0.10, 0.20, 0.30, 0.40 y 0.50 -- son
    [N]: la tabla los imprime. Lo que la tabla NO resuelve es que hacer con un
    PGA que cae JUSTO en los rotulos extremos, porque los dos son
    desigualdades estrictas: "PGA < 0.10" y "PGA > 0.50". El de este proyecto
    es exactamente 0.50 y por tanto no cae en ninguna columna tabulada
    (NOR-PUE-11). Esa lectura es del proyectista y entra por argumento:

      'limite_inclusive'  las columnas extremas aplican TAMBIEN en su propio
                          limite, de modo que 0.50 lee la ultima columna. Es
                          la lectura corriente y la que este proyecto declara.
      'limite_estricto'   los rotulos se leen al pie de la letra: en 0.50 no
                          hay columna y no hay nada que interpolar, asi que el
                          calculo se DETIENE en vez de elegir una.

    Que la lectura no es neutra se ve en la fila D: con 'limite_inclusive' da
    1.0 y con la columna anterior daria 1.1. Por eso se declara.
    """
    if clase not in F_PGA_TABLA:
        raise DatoInvalidoError(
            campo="clase", valor=clase,
            motivo=f"no es una fila de {NUMERAL_F_PGA_TABLA}",
        )
    if lectura_extremos not in LECTURAS_COLUMNA_EXTREMA:
        raise DatoInvalidoError(
            campo="lectura_extremos", valor=lectura_extremos,
            motivo="la lectura de los rotulos extremos tiene que ser una de "
                   f"{LECTURAS_COLUMNA_EXTREMA}",
        )
    fila = F_PGA_TABLA[clase]
    if F_PGA_EXIGE_ESTUDIO_DE_SITIO in fila:
        # Misma excepcion que en `clases_de_sitio_plausibles` y a proposito:
        # el hecho es el mismo -- se pidio una fila que no trae factor -- y
        # dos excepciones distintas para un mismo hecho obligarian a quien
        # atrapa a saber por cual de las dos puertas entro.
        raise DatoInvalidoError(
            campo="clase", valor=clase,
            motivo=f"la fila '{clase}' de {NUMERAL_F_PGA_TABLA} no tiene "
                   f"factor tabulado: la fuente le pone asterisco en las "
                   f"cinco columnas y su Nota 2 exige estudio de respuesta "
                   f"dinamica de sitio. No hay numero que leer ahi",
        )

    limites = F_PGA_TABLA_PGA_COLUMNAS
    inferior, superior = limites[0], limites[-1]
    if lectura_extremos == LECTURA_COLUMNA_EXTREMA_ESTRICTA and (
            math.isclose(PGA, inferior, abs_tol=TOL_UMBRAL_NORMATIVO)
            or math.isclose(PGA, superior, abs_tol=TOL_UMBRAL_NORMATIVO)):
        raise DisenoNoFactibleError(
            motivo=f"PGA = {PGA:.3f} g cae justo sobre un rotulo extremo de "
                   f"{NUMERAL_F_PGA_TABLA}, y los dos son desigualdades "
                   f"estrictas ('PGA < {inferior}', 'PGA > {superior}'): con "
                   f"la lectura '{lectura_extremos}' no hay columna que leer "
                   f"ni valor entre el que interpolar"
        )

    if PGA <= inferior:
        return fila[0]
    if PGA >= superior:
        return fila[-1]
    for k in range(len(limites) - 1):
        x0, x1 = limites[k], limites[k + 1]
        if x0 <= PGA <= x1:
            y0, y1 = fila[k], fila[k + 1]
            return y0 + (y1 - y0) * (PGA - x0) / (x1 - x0)
    raise DisenoNoFactibleError(              # inalcanzable: los tramos cubren
        motivo=f"PGA = {PGA} fuera de {NUMERAL_F_PGA_TABLA}"   # todo el rango
    )


def f_pga() -> float:
    """
    Paso 2: F_pga, factor de sitio, adimensional.

    Es la ENVOLVENTE de la tabla sobre las filas que 'F_pga' declara
    plausibles: el mayor de sus factores al PGA del proyecto. Mientras la
    campana geotecnica no cierre la clase, adoptar el mayor es la lectura
    conservadora, y con las filas declaradas la memoria puede decir de cuales
    salio -- que es lo que un 1.0 escrito a mano no permitia (NOR-MEM-03).

    Lo que NO hace esta funcion, y hay que decirlo: no decide la clase del
    sitio. La premisa de la Sec. 0.5 -- que el sitio cae en la Clase F de
    AASHTO por licuefaccion -- sigue abierta en el criterio que la declara, y
    el salto de la clasificacion de E.030 a la de AASHTO no lo escribe
    ninguno de los dos documentos (NOR-AAS-02; la discrepancia entre los dos
    esquemas esta transcrita en
    `constantes_normativas.E030_S5_VS_CLASE_F`). Esta funcion lee las filas
    que el proyectista declara; no las deduce.
    """
    PGA = pga_roca_b()
    lectura = lectura_columna_extrema()
    return max(factor_sitio_desde_tabla(clase=clase, PGA=PGA,
                                        lectura_extremos=lectura)
               for clase in clases_de_sitio_plausibles())


def lectura_columna_extrema() -> str:
    """
    Como se leen los dos rotulos extremos de la tabla de F_pga, del criterio
    'F_pga_lectura_columna_extrema' ([A]). Ver `factor_sitio_desde_tabla`.
    """
    lectura = ca.valor(CRITERIO_F_PGA_LECTURA)
    if lectura not in LECTURAS_COLUMNA_EXTREMA:
        raise DatoInvalidoError(
            campo=CRITERIO_F_PGA_LECTURA, valor=lectura,
            motivo=f"tiene que ser una de {LECTURAS_COLUMNA_EXTREMA}",
        )
    return lectura


def aceleracion_ajustada_sitio(*, PGA: float, F_pga: float) -> float:
    """Paso 3: A_s = F_pga * PGA, en g (Sec. 9.2). Calculado, no declarado."""
    return F_pga * PGA


def cimentacion_en_roca() -> bool:
    """
    Si la cimentacion del cabezal cae en las filas de ROCA de la tabla de
    F_pga (Clase A o B), que es la condicion que dispara la clausula de roca
    del num. 2.8.1.1.14.2.1.

    Se resuelve con las MISMAS filas que declara 'F_pga' y no con un criterio
    nuevo: si el proyectista declara que las filas plausibles son C, D y E,
    ya esta diciendo que la cimentacion no es roca. Antes esa afirmacion
    estaba implicita en un 1.0 y la clausula no se implementaba ni se
    descartaba (MAT-O4, NOR-PUE-12); ahora se descarta de forma trazable, y
    el dia que alguien anada A o B a la declaracion la clausula se activa
    sola.

    Una declaracion MIXTA -- filas de roca y de suelo a la vez -- no se
    resuelve por mayoria ni por el lado conservador: son dos ramas distintas
    del numeral y elegir una seria decidir por el proyectista.
    """
    clases = clases_de_sitio_plausibles()
    en_roca = [c for c in clases if c in F_PGA_CLASES_EN_ROCA]
    if en_roca and len(en_roca) != len(clases):
        raise DatoInvalidoError(
            campo=CRITERIO_F_PGA, valor=clases,
            motivo=f"mezcla filas de roca {F_PGA_CLASES_EN_ROCA} con filas de "
                   f"suelo, y {NUMERAL_K_H0} da a cada grupo una expresion "
                   f"distinta de k_h0. Declarar en cual de las dos ramas cae "
                   f"la cimentacion del cabezal",
        )
    return bool(en_roca)


def coeficiente_sismico_base(*, A_s: float, F_pga: float, PGA: float,
                             cimentacion_en_roca: bool) -> float:
    """
    Paso 4: k_h0, coeficiente sismico de base (num. 2.8.1.1.14.2.1,
    `NUMERAL_K_H0`).

    DOS RAMAS, y el repositorio implementaba una sola sin decirlo:

        cimentacion en suelo   k_h0 = F_pga*PGA = A_s
        cimentacion en roca    k_h0 = 1.2 * F_pga * PGA
        (Clase de Sitio A o B)

    La igualdad de la primera rama es [N]: no es que k_h0 "se adopte" igual a
    A_s, es que el numeral la establece ("kh0=FpgaPGA = As donde kh0 es el
    coeficiente de aceleracion sismico horizontal asumiendo que el
    desplazamiento del muro sea cero").

    LA SEGUNDA RAMA SE TOMA DE LA PROSA Y NO DEL PARENTESIS. El Manual
    imprime "(es decir, 1.2 kh0=FpgaPGA)", que leido al pie de la letra daria
    k_h0 = A_s/1.2 -- una reduccion del 17 %, lo contrario de lo que la misma
    frase acaba de decir. Es errata de imprenta y esta declarada entera en
    `constantes_normativas.K_H0_ROCA_ERRATA`, con la ecuacion de AASHTO que
    la resuelve. Es la segunda de las tres erratas del Manual en esta misma
    cadena; las otras estan en `k_ae_mononobe_okabe` y en
    `excentricidad_admisible_sismica`.

    `cimentacion_en_roca` entra por argumento y no se deduce aqui: quien
    quiera la rama del proyecto usa `cimentacion_en_roca()`, que la resuelve
    con las filas declaradas en 'F_pga'.
    """
    if cimentacion_en_roca:
        return K_H0_FACTOR_ROCA_A_B * F_pga * PGA
    return A_s


def factor_muro() -> float:
    """
    Paso 5: factor por el que se multiplica k_h0 segun la deformacion lateral
    admitida al muro (num. 2.8.1.1.14.2.2, `NUMERAL_FACTOR_MURO`),
    adimensional.

    AQUI NO HAY TABLA. Este archivo declaraba `FACTOR_MURO_TABLA` con dos
    filas ("rigido" 1.0 / "desplazable" 0.5) afirmando que "las DOS filas son
    [N]: el numeral las fija". El numeral no presenta ninguna tabla -- en las
    pags. impresas 252-257 del Manual no hay una sola -- y fija UN valor, 0.5,
    de forma PERMISIVA ("kh puede ser reducido a 0.5kh0"). El 1.0 no es una
    fila tabulada: es la AUSENCIA de reduccion, que es la definicion misma de
    k_h0 (NOR-PUE-07).

    Lo que el proyectista declara, entonces, no es una fila sino si aplica o
    no la reduccion que el numeral autoriza. Y no es una decision solo
    tecnica: AASHTO, del que el numeral es traduccion, la condiciona ademas a
    que el movimiento lateral sea "acceptable to the Owner". Este cabezal va
    empotrado en el terraplen y no tiene desplazamiento admisible garantizado,
    de modo que el archivo lo declara SIN reduccion: el programa no asume la
    aceptacion del Propietario. La Sec. 9.2 (corregida, ficha VE3-20) pide
    declarar la reduccion por obra, con el detalle que permite el movimiento
    y la aceptacion escrita del Propietario.
    """
    declarado = ca.valor(CRITERIO_FACTOR_MURO)
    if declarado not in FACTOR_MURO_DECLARACIONES:
        raise DatoInvalidoError(
            CRITERIO_FACTOR_MURO, valor=declarado,
            motivo=f"la declaracion tiene que ser una de "
                   f"{FACTOR_MURO_DECLARACIONES} ({NUMERAL_FACTOR_MURO}). El "
                   f"numeral no tabula filas: autoriza una reduccion",
        )
    if declarado == FACTOR_MURO_CON_REDUCCION:
        # Un solo regimen (decision 12 del dueño, VE-3.15): la reduccion es
        # del muro que CEDE, y no se declara con el armado del que no cede
        # (C11.6.5.4 pone el estribo con aleros estructurales entre los que
        # pueden no ceder; la hoja de ruta §9.2 lo advierte).
        regimen = ca.valor(CRITERIO_REGIMEN_RESISTENCIA)
        if regimen != REGIMEN_RESISTENCIA_CEDENTE:
            raise DatoInvalidoError(
                CRITERIO_FACTOR_MURO, valor=declarado,
                motivo=(f"la reduccion de k_h por desplazamiento supone un "
                        f"muro que cede, y "
                        f"'{CRITERIO_REGIMEN_RESISTENCIA}' = '{regimen}' arma "
                        f"el cabezal como muro que no cede: un solo regimen. "
                        f"Se declaran juntos (el desplazamiento aceptado por "
                        f"el Propietario y la pantalla que cede) o ninguno"))
        return REDUCCION_KH_POR_DESPLAZAMIENTO
    return 1.0   # literal-ok: ausencia de reduccion, k_h = k_h0 por definicion


def coeficiente_sismico_horizontal(*, k_h0: float, factor_muro: float) -> float:
    """Paso 6: k_h = factor_muro * k_h0 (Sec. 9.2). Calculado, no declarado."""
    return factor_muro * k_h0


def coeficiente_sismico_vertical() -> float:
    """
    k_v, coeficiente sismico vertical, adimensional.

    ES [N] CONDICIONADO, no una adopcion. El criterio 'k_v' declaraba 0.0 con
    la fuente "practica corriente; no fijado por el Manual de Puentes", y esa
    afirmacion negativa es falsa: el MISMO numeral del que la cadena toma
    k_h0 lo fija ("El coeficiente de aceleracion sismica vertical, kv, se
    asumira cero con el proposito de calcular las presiones laterales del
    terreno, a no ser que...", `NUMERAL_K_H0`). El valor era correcto; la
    cita y
    la etiqueta, no (NOR-PUE-08, MAT-O11, MAT-X4).

    El numeral reserva dos casos -- muro significativamente afectado por
    efectos de alguna falla cercana, y aceleraciones verticales relativamente
    altas simultaneas con la horizontal -- y no cuantifica ninguno ni escribe
    un k_v alternativo para ellos. Lo que el proyecto declara en el criterio
    'k_v' es, por tanto, una de dos cosas:

        la cadena prescrita       -> k_v = K_V_PRESCRITO, que es [N]
        un numero                 -> el caso reservado se da y el proyectista
                                     aporta el valor que el Manual no da

    Cualquier otra cosa es `DatoInvalidoError`. El rango de sensibilidad
    (0.0, 0.5) que el criterio declaraba sugeria una libertad que el numeral
    no concede, y ademas su comentario ("0.5*k_h") no coincidia con su propio
    extremo: con la cadena de hoy 0.5*k_h vale 0.25, no 0.5 (SIS-D-04).
    """
    declarado = ca.valor(CRITERIO_K_V)
    if declarado == K_V_DECLARACION_PRESCRITO:
        return K_V_PRESCRITO
    if isinstance(declarado, bool) or not isinstance(declarado, (int, float)):
        raise DatoInvalidoError(
            CRITERIO_K_V, valor=declarado,
            motivo=f"o se declara '{K_V_DECLARACION_PRESCRITO}' y rige el "
                   f"cero de {NUMERAL_K_H0}, o se declara el numero que "
                   f"corresponde al caso que ese numeral reserva y que no "
                   f"cuantifica. {K_V_CASO_RESERVADO}",
        )
    return float(declarado)


def cadena_sismica() -> CadenaSismica:
    """
    Los seis pasos horizontales de Sec. 9.2 mas k_v, cada uno con su etiqueta,
    su origen y LA CONDICION QUE SU FUENTE LE PONE, en el orden de la tabla de
    la hoja de ruta.

    `pasos` es lo que el informe imprime: la cadena entera, no el resultado. La
    columna nueva es `condicion`: cada eslabon dice bajo que supuesto vale, de
    modo que un revisor pueda comprobar el supuesto y no solo el numero. Los
    tres que mas pesan -- de que filas de la tabla sale F_pga, en que rama de
    k_h0 cae la cimentacion, y que caso de k_v rige -- eran justamente los que
    viajaban implicitos.

    Todos los insumos tienen valor declarado, asi que esta funcion no se
    detiene hoy por ningun vacio.
    """
    PGA = pga_roca_b()
    clases = clases_de_sitio_plausibles()
    lectura = lectura_columna_extrema()
    Fpga = f_pga()
    A_s = aceleracion_ajustada_sitio(PGA=PGA, F_pga=Fpga)
    en_roca = cimentacion_en_roca()
    k_h0 = coeficiente_sismico_base(A_s=A_s, F_pga=Fpga, PGA=PGA,
                                    cimentacion_en_roca=en_roca)
    f_muro = factor_muro()
    k_h = coeficiente_sismico_horizontal(k_h0=k_h0, factor_muro=f_muro)
    k_v = coeficiente_sismico_vertical()
    declarado_muro = ca.valor(CRITERIO_FACTOR_MURO)
    # La etiqueta y la condicion de k_v NO se cablean: dependen de cual de
    # los dos regimenes declaro el criterio. Cableadas, un k_v puesto a mano
    # por el proyectista para el caso reservado salia de la memoria como [N]
    # "exigencia normativa con numeral verificado" y con una condicion que
    # afirmaba lo contrario de lo que acababa de pasar -- el peor error
    # posible de la taxonomia, cometido justo por la funcion que existe para
    # arreglar etiquetas.
    rige_el_cero = ca.valor(CRITERIO_K_V) == K_V_DECLARACION_PRESCRITO
    if rige_el_cero:
        etiqueta_k_v = "N"
        origen_k_v = NUMERAL_K_H0
        condicion_k_v = ("El numeral lo fija en cero salvo muro "
                         "significativamente afectado por efectos de alguna "
                         "falla cercana, o aceleraciones verticales "
                         "relativamente altas simultaneas con la horizontal. "
                         "Ninguno de los dos casos se declara para este "
                         "cabezal, de modo que rige el cero prescrito")
    else:
        etiqueta_k_v = ca.criterio(CRITERIO_K_V).etiqueta
        origen_k_v = "Declarado por el proyectista"
        condicion_k_v = ("El expediente declara que se da uno de los dos "
                         f"casos que {NUMERAL_K_H0} reserva. Para ellos el "
                         "Manual NO escribe ningun k_v, asi que este valor es "
                         "del proyectista y no de la norma")

    pasos = (
        PasoSismico(simbolo="PGA", valor=PGA,
                    concepto="Aceleracion pico en roca Clase B, Tr = 1000 anios",
                    etiqueta=ds.dato(DATO_SITIO_PGA).etiqueta,
                    origen=NUMERAL_PGA, criterio=DATO_SITIO_PGA,
                    condicion="Lectura del mapa sobre las coordenadas de esta "
                              "obra; su reproducibilidad llega hoy hasta el "
                              "distrito"),
        PasoSismico(simbolo="F_pga", valor=Fpga,
                    concepto="Factor de sitio",
                    etiqueta=ca.criterio(CRITERIO_F_PGA).etiqueta,
                    origen=NUMERAL_F_PGA, criterio=CRITERIO_F_PGA,
                    condicion=f"Envolvente de las filas {', '.join(clases)} "
                              f"de la tabla" + (
                                  f"; PGA = {PGA:.2f} g cae justo sobre un "
                                  f"rotulo extremo, que es desigualdad "
                                  f"estricta, y ese borde se lee con "
                                  f"'{lectura}'"
                                  if _pga_en_rotulo_extremo(PGA) else
                                  f"; PGA = {PGA:.2f} g cae dentro de la "
                                  f"tabla y el factor sale de la "
                                  f"interpolacion de su Nota 1")),
        PasoSismico(simbolo="A_s", valor=A_s,
                    concepto="Aceleracion ajustada por sitio (F_pga * PGA)",
                    etiqueta=ETIQUETA_CALCULADO, origen=CALCULADO),
        PasoSismico(simbolo="k_h0", valor=k_h0,
                    concepto="Coeficiente sismico de base",
                    etiqueta="N", origen=NUMERAL_K_H0,
                    condicion=("Rama de roca: k_h0 = 1.2*F_pga*PGA, "
                               "cimentacion en Clase de Sitio A o B"
                               if en_roca else
                               "Rama de suelo: k_h0 = A_s. La rama de roca "
                               "(1.2*F_pga*PGA, Clase de Sitio A o B) queda "
                               "descartada porque ninguna fila declarada en "
                               "'F_pga' es de roca")),
        PasoSismico(simbolo="factor_muro", valor=f_muro,
                    concepto="Factor por deformacion lateral admitida al muro",
                    etiqueta=ca.criterio(CRITERIO_FACTOR_MURO).etiqueta,
                    origen=NUMERAL_FACTOR_MURO, criterio=CRITERIO_FACTOR_MURO,
                    condicion=f"Declaracion '{declarado_muro}'. El numeral no "
                              f"tabula filas: autoriza reducir k_h0 a la "
                              f"mitad si el muro admite 1.0 a 2.0 in o mas de "
                              f"desplazamiento Y el propietario acepta ese "
                              f"movimiento"),
        PasoSismico(simbolo="k_h", valor=k_h,
                    concepto="Coeficiente sismico horizontal de diseno",
                    etiqueta=ETIQUETA_CALCULADO, origen=CALCULADO),
        PasoSismico(simbolo="k_v", valor=k_v,
                    concepto="Coeficiente sismico vertical",
                    etiqueta=etiqueta_k_v, origen=origen_k_v,
                    criterio=CRITERIO_K_V, condicion=condicion_k_v),
    )

    return CadenaSismica(PGA=PGA, F_pga=Fpga, A_s=A_s, k_h0=k_h0,
                         factor_muro=f_muro, k_h=k_h, k_v=k_v,
                         pasos=pasos, numeral=NUMERAL_9_2,
                         clases_de_sitio=clases, cimentacion_en_roca=en_roca)


# ===========================================================================
# 9.2 - EMPUJE ACTIVO Y MONONOBE-OKABE
# ===========================================================================

def ka_rankine(*, phi_grados: float) -> float:
    """
    Ka = tan^2(45 - phi/2), el empuje activo que Sec. 9.2 escribe de forma
    literal. Es el caso de Rankine: muro vertical, relleno horizontal y
    friccion muro-suelo nula.

    NO ES EL Ka DEL EMPUJE ESTATICO (EXT-M-06): desde EXT-7 `empujes_trasdos`
    usa el de Coulomb del Manual de Puentes (`k_a_coulomb`), que es el de la
    fuente primaria y el homogeneo con K_AE; con i = beta = delta = 0 los dos
    coinciden exactamente, y en cuanto alguno deja de ser cero difieren.
    Esta funcion se conserva como PATRON: es la forma reducida que la hoja de
    ruta escribia en su Sec. 9.2 (enmendada en EXT-0, `DIS-HR-KA-COULOMB`) y
    el caso limite contra el que se contrasta Mononobe-Okabe.
    """
    return math.tan(math.radians(45 - phi_grados / 2)) ** 2   # literal-ok: Ka = tan^2(45 - phi/2), Sec. 9.2


def angulo_inercia_sismica(*, k_h: float, k_v: float) -> float:
    """
    psi = arctan[k_h / (1 - k_v)], en GRADOS: el angulo con que la resultante
    de las fuerzas de inercia se aparta de la vertical. Es el unico punto por
    donde la cadena sismica entra en Mononobe-Okabe.

    Se usa atan2 y no una division: con k_v = 1 (aceleracion vertical igual a
    g, fisicamente absurdo pero declarable por error en un criterio) la
    division reventaria con ZeroDivisionError -- un fallo de programa, no del
    expediente. atan2 devuelve 90 grados y el caso se rechaza mas adelante,
    con un DisenoNoFactibleError que es de la taxonomia.

    POR QUE GUARDA LO RECHAZA, dicho con precision. El texto que ocupaba este
    lugar decia "cos(psi) = 0 hace degenerar el denominador de K_AE", y eso es
    falso en aritmetica de maquina: `math.cos(math.radians(90.0))` vale
    6.123233995736766e-17, que es POSITIVO, de modo que la guarda de cosenos
    no dispara por psi. Con delta = 0 el rechazo lo produce la guarda
    siguiente, la de `phi - psi - i < 0` --- 34 - 90 - 0 = -56 grados ---, y
    su mensaje manda al revisor a "reducir la pendiente del relleno o revisar
    phi" cuando el disparate esta en k_v. Con delta > 0 dispara antes la de
    cosenos, pero por `delta + beta + psi` y no por psi.

    Se deja asi --- ninguna de las dos guardas nombra k_v --- porque las dos
    son correctas para lo que verifican y anadir una tercera que mire k_v
    exigiria un techo declarado para k_v que este expediente no tiene. Lo que
    no puede quedar es el docstring afirmando un mecanismo que no ocurre.
    """
    return math.degrees(math.atan2(k_h, 1 - k_v))


def k_ae_mononobe_okabe(*, phi_grados: float, i_grados: float,
                        beta_grados: float, delta_grados: float,
                        k_h: float, k_v: float) -> float:
    """
    K_AE por Mononobe-Okabe (Sec. 9.2), adimensional.

                    cos^2(phi - psi - beta)
    K_AE = ----------------------------------------------------------
           cos(psi) cos^2(beta) cos(delta + beta + psi) [1 + R]^2

                 /  sen(phi + delta) sen(phi - psi - i)
    con   R = _ /  --------------------------------------
             V    cos(delta + beta + psi) cos(i - beta)

    Convenciones de angulo, que son la mitad del riesgo de esta formula:
        phi   friccion interna del relleno
        psi   arctan[k_h/(1-k_v)], de `angulo_inercia_sismica`
        i     pendiente del relleno sobre la HORIZONTAL
        beta  inclinacion del trasdos sobre la VERTICAL, positiva cuando el
              muro se aleja del relleno
        delta friccion muro-suelo

    Caso limite verificado en los tests: con k_h = k_v = 0 y
    i = beta = delta = 0, esta expresion devuelve exactamente
    tan^2(45 - phi/2), el Ka de Rankine que cita Sec. 9.2.

    ESE CASO LIMITE NO GARANTIZA LOS SIGNOS, y aqui decia que si (SIS-F-04,
    mitad documental). Con i = beta = delta = 0 los cuatro cosenos son PARES
    y por lo tanto insensibles al signo: de los quince mutantes de signo y
    operador de esta formula, DOCE devuelven el mismo double que el original
    en ese caso --- medido, 0.28271491971777263 para phi = 34 ---, y siete de
    ellos atravesaban la suite entera. Una comprobacion con todos los angulos
    en cero no puede ver una convencion de signo: no hay signo que ver.

    Lo que si los cubre es CP9_MONONOBE_OKABE (tests/fixtures/casos_patron.py),
    tres juegos con phi, i, beta, delta, k_h y k_v todos distintos y todos
    distintos de cero, autoverificados por recomputacion independiente. El
    caso limite se conserva porque prueba otra cosa --- la reduccion a
    Rankine, que es la que cita Sec. 9.2 --- y esa si la prueba.

    EL SIGNO DEL CORCHETE: [1 + R], Y EL MANUAL DE PUENTES IMPRIME [1 - R].
    Hay que decirlo aqui, en el punto de uso, porque un revisor que compare
    esta funcion con la letra impresa de la norma peruana va a creer que
    encontro un error de transcripcion, y "corregirla" rompe la formula.

    El Apendice A11 del Manual (num. A.11.3.1 "Metodo de Mononobe -Okabe",
    pag. impresa 586 / PDF 587) imprime el denominador con signo MENOS. Es
    ERRATA DE IMPRENTA, no una variante peruana:

      * el propio Manual declara transcribir a AASHTO, y AASHTO imprime "+"
        (Art. A11.3.1, ec. A11.3.1-1, pag. impresa 11-145 / PDF 1614);
      * con el menos, K_AE DIVERGE cuando el radicando tiende a 1, y el caso
        limite k_h = k_v = 0 deja de devolver el Ka de Coulomb -- la formula
        se rompe justo donde el Manual la manda coincidir.

    ESTE CODIGO SIGUE A AASHTO, y esa es la decision correcta. La declaracion
    completa, con las dos citas, esta en
    `constantes_normativas.K_AE_ERRATA_MANUAL`, y viaja a la memoria por
    `condicion_normativa_cabezal`. Es la primera de las TRES erratas del
    Manual en esta misma cadena sismica: las otras dos son el parentesis de
    la clausula de roca de k_h0, en `coeficiente_sismico_base`, y el "tercio
    central" del limite de excentricidad, en
    `excentricidad_admisible_sismica` -- la unica de las tres que mueve un
    numero.

    Se reporta contra la hoja de ruta: su Sec. 9.2 remite a Mononobe-Okabe
    sin escribir la formula ni advertir de la errata, de modo que quien la
    lea sin leer este codigo no tiene con que detectarla.

    Dominio de validez. La formula tiene solucion real solo si
    phi - psi - i >= 0: por debajo de ese limite la cuna activa no encuentra
    equilibrio y K_AE no existe (no es que salga grande: no existe). Con
    k_h = 0.50 es psi = 26.6 grados, de modo que un relleno inclinado se
    acerca al limite muy rapido -- esa es la razon de la sensibilidad
    violenta que declara el criterio 'pendiente_relleno_trasdos_i'. Los dos
    cosenos del denominador se comprueban aparte por la misma razon. Los tres
    casos salen como `DisenoNoFactibleError` con su motivo, nunca como un
    ValueError de math.sqrt ni como un numero enorme sin explicacion.
    """
    psi = math.radians(angulo_inercia_sismica(k_h=k_h, k_v=k_v))
    phi = math.radians(phi_grados)
    i = math.radians(i_grados)
    beta = math.radians(beta_grados)
    delta = math.radians(delta_grados)

    cos_psi = math.cos(psi)
    cos_dbp = math.cos(delta + beta + psi)
    cos_ib = math.cos(i - beta)

    if cos_psi <= 0 or cos_dbp <= 0 or cos_ib <= 0:
        raise DisenoNoFactibleError(
            motivo=(
                "Mononobe-Okabe fuera de su dominio: algun coseno del "
                f"denominador es nulo o negativo (psi = {math.degrees(psi):.2f} "
                f"grados, delta+beta+psi = {math.degrees(delta + beta + psi):.2f}, "
                f"i-beta = {math.degrees(i - beta):.2f}). Revisar los angulos "
                f"declarados y k_v ({NUMERAL_MO})"
            )
        )

    radicando_seno = phi - psi - i
    if radicando_seno < 0:
        raise DisenoNoFactibleError(
            motivo=(
                f"Mononobe-Okabe sin solucion real: phi - psi - i = "
                f"{math.degrees(radicando_seno):.2f} grados < 0 "
                f"(phi = {phi_grados:.2f}, psi = {math.degrees(psi):.2f}, "
                f"i = {i_grados:.2f}). La cuna activa no encuentra equilibrio "
                f"bajo k_h = {k_h:.3f}: no hay K_AE que calcular, hay que "
                f"reducir la pendiente del relleno o revisar phi ({NUMERAL_MO})"
            )
        )

    radicando = (math.sin(phi + delta) * math.sin(radicando_seno)
                 / (cos_dbp * cos_ib))
    R = math.sqrt(max(radicando, 0.0))   # el max solo absorbe -0.0 del producto

    numerador = math.cos(phi - psi - beta) ** 2
    denominador = cos_psi * math.cos(beta) ** 2 * cos_dbp * (1 + R) ** 2
    return numerador / denominador


def k_a_coulomb(*, phi_grados: float, i_grados: float,
                beta_grados: float, delta_grados: float) -> float:
    """
    Coeficiente activo ESTATICO de la misma formulacion de Mononobe-Okabe,
    obtenido haciendo k_h = k_v = 0 (con lo que psi = 0 y la expresion se
    reduce a Coulomb).

    Existe para que `EmpujeMononobeOkabe.incremento` reste dos coeficientes
    homogeneos. Restar K_AE (Mononobe-Okabe, con i, beta y delta) menos Ka de
    Rankine (que ignora los tres) mezclaria dos modelos y daria un incremento
    sismico que no es tal.
    """
    return k_ae_mononobe_okabe(phi_grados=phi_grados, i_grados=i_grados,
                               beta_grados=beta_grados,
                               delta_grados=delta_grados, k_h=0.0, k_v=0.0)


def empuje_mononobe_okabe(*, phi_grados: float, i_grados: float,
                          beta_grados: float, delta_grados: float,
                          k_h: float, k_v: float) -> EmpujeMononobeOkabe:
    """
    K_AE y K_A con todos los angulos que los produjeron, empaquetados para la
    memoria: sin los cuatro angulos el coeficiente no es revisable, porque
    tres de ellos son adopciones del proyectista.
    """
    return EmpujeMononobeOkabe(
        K_AE=k_ae_mononobe_okabe(phi_grados=phi_grados, i_grados=i_grados,
                                 beta_grados=beta_grados,
                                 delta_grados=delta_grados, k_h=k_h, k_v=k_v),
        K_A=k_a_coulomb(phi_grados=phi_grados, i_grados=i_grados,
                        beta_grados=beta_grados, delta_grados=delta_grados),
        psi_grados=angulo_inercia_sismica(k_h=k_h, k_v=k_v),
        phi_grados=phi_grados, i_grados=i_grados,
        beta_grados=beta_grados, delta_grados=delta_grados,
        k_h=k_h, k_v=k_v, numeral=NUMERAL_MO,
    )


def k_ae_del_proyecto() -> EmpujeMononobeOkabe:
    """
    El K_AE del proyecto: cadena sismica declarada mas los cuatro angulos de
    `criterios_adoptados`.

    Se detiene con `CriterioPendienteError` en el primero de los cuatro que
    siga vacio -- hoy los cuatro lo estan ('phi_relleno_trasdos',
    'pendiente_relleno_trasdos_i', 'inclinacion_muro_beta',
    'friccion_muro_suelo_delta'). La formula de arriba SI es utilizable con
    argumentos explicitos: lo que falta son los datos, no el procedimiento.
    """
    cadena = cadena_sismica()
    return empuje_mononobe_okabe(
        phi_grados=ca.valor(CRITERIO_PHI_RELLENO),
        i_grados=ca.valor(CRITERIO_I_RELLENO),
        beta_grados=ca.valor(CRITERIO_BETA_MURO),
        delta_grados=ca.valor(CRITERIO_DELTA_MURO),
        k_h=cadena.k_h, k_v=cadena.k_v,
    )


# ===========================================================================
# 9.2 - EMPUJES SOBRE EL TRASDOS
# ===========================================================================

def aplica_sobrecarga_trasdos(*, distancia_trafico: float, H: float) -> bool:
    """
    Regla de Sec. 9.2: la sobrecarga vertical de trasdos aplica con trafico a
    distancia horizontal <= H/2 desde la parte superior de la estructura.

    NUMERAL CORREGIDO (NOR-PUE-01, MAT-D5). Esta regla se citaba al num.
    2.1.4.3.9 del Manual de Puentes, que se titula "Aparatos de Apoyo" y va de
    la conexion entre superestructura y subestructura. El texto que la sostiene
    esta en el num. 2.4.2.2 "Cargas de Suelo: EH, ES, y DD", pag. impresa 102:
    "Cuando se prevea trafico a una distancia horizontal, medida desde la parte
    superior de la estructura, menor o igual a la mitad de su altura, las
    presiones seran incrementadas...". El numeral viejo estaba propagado a seis
    puntos del repositorio.

    La hoja de ruta anade que "en un cabezal bajo terraplen vial siempre
    aplica" -- ver `sobrecarga_trasdos_siempre_aplica`. Esta funcion existe
    para el caso en que alguien tenga la distancia medida y quiera
    comprobarlo en vez de invocar la regla general.
    """
    return distancia_trafico <= H / 2 + TOL_UMBRAL_NORMATIVO


def sobrecarga_trasdos_siempre_aplica() -> str:
    """
    Declaracion, para la memoria, de que la sobrecarga de trasdos aplica sin
    medir distancia: Sec. 9.2 cierra el punto con "en un cabezal bajo
    terraplen vial SIEMPRE aplica". No es un supuesto de este modulo.

    LA SEGUNDA MITAD DEL NUMERAL, que el expediente no declaraba: el 2.4.2.2
    EXIME expresamente del incremento "cuando se diseñe una losa de
    aproximacion soportada en un extremo del puente". Este proyecto no
    proyecta losa de aproximacion en ningun cabezal, de modo que la exencion
    no se invoca y la sobrecarga se aplica; se dice para que un revisor vea
    que la salida existe y que no se tomo.
    """
    return (
        f"Sobrecarga de trasdos: aplica siempre en un cabezal bajo terraplen "
        f"vial, con carga viva {CARGA_VIVA} ({NUMERAL_SOBRECARGA_TRASDOS}). "
        f"El numeral exime del incremento si hay losa de aproximacion; este "
        f"expediente no proyecta ninguna, de modo que la exencion no se invoca"
    )


def h_eq_sobrecarga_trasdos(*, altura_muro_total: float,
                            orientacion: Optional[str] = None,
                            borde_m: Optional[float] = None) -> float:
    """
    Altura de suelo equivalente de la sobrecarga viva de trafico, en m.

    Sec. 9.2. Numerales: Manual de Puentes num. 2.4.2.2 (pag. impresa 102) y
    AASHTO LRFD 9a ed. Art. 3.11.6.4 (pag. impresa 3-151).

    LOS DOS RIGEN A LA VEZ Y GOBIERNA EL MAYOR, que es la misma regla del
    mayor de la Sec. 0.2 que este proyecto ya aplica al recubrimiento:

        h_eq = max( piso del Manual , h_eq tabulado por AASHTO )

    El Manual escribe un PISO -- "una sobrecarga vertical NO MENOR QUE la
    equivalente a 0.60 m de altura de relleno" -- y no tabula nada: su
    traduccion de la Sec. 3.11 de AASHTO se corta en el empuje pasivo k_p y no
    tiene subnumeral LS (verificado barriendo las 673 paginas). AASHTO SI
    tabula, por altura del muro, y manda interpolar linealmente entre filas.

    POR QUE ESTA FUNCION PUEDE DETENERSE. Cual de las dos tablas de AASHTO
    aplica depende de la ORIENTACION del muro respecto del trafico, que es un
    dato de sitio de este expediente y todavia no esta declarado. Es la
    resolucion del conflicto vinculante #4 del plan de correcciones: "no hay
    contradiccion sino un dato faltante". Con el dato sin declarar se lanza
    `CriterioPendienteError` -- por la via que `datos_sitio.valor` ya usa, sin
    inventar un camino nuevo -- en vez de aplicar 0.60 m plano, que es lo que
    el expediente venia haciendo y que para un cabezal de 2.0 m con trafico
    perpendicular subestima la sobrecarga en un factor 1.87.

    `altura_muro_total` ES LA ALTURA CON ZAPATA, y no es un detalle: AASHTO lo
    escribe con un `shall` -- "The wall height shall be taken as the distance
    between the surface of the backfill and the bottom of the footing along
    the pressure surface being considered" --. Con `GeometriaCabezal` eso es
    `H + espesor_zapata`. Medirla sin la zapata subestima la altura y, como
    h_eq DECRECE con ella, sobrestima h_eq: conservador, pero es la lectura
    equivocada de la tabla.

    --- VE-6 (ficha T7B-11) --- `orientacion` y `borde_m` son los que el
    PUNTO declara para este cabezal (`GeometriaCabezal.orientacion_trafico`
    y `.distancia_borde_calzada_m`); cada uno que falte se lee del [S] de
    corredor, que solo entonces se invoca. Ninguno se deduce del esviaje:
    AASHTO no tiene tabla para el muro oblicuo.
    """
    if orientacion is None:
        orientacion = ds.valor("orientacion_muro_respecto_al_trafico")
    altura_ft = altura_muro_total / PIE_EN_METROS

    if orientacion == ORIENTACION_PERPENDICULAR_AL_TRAFICO:
        # ANALOGIA DECLARADA [N->]: la Tabla 3.11.6.4-1 es de ESTRIBOS -- su
        # variable se llama "Abutment Height" --, no de muros de contencion.
        # AASHTO no publica tabla para un muro perpendicular al trafico. La
        # analogia va del lado conservador: el propio comentario C3.11.6.4
        # dice que h_eq es MAYOR para un estribo que para un muro.
        puntos = sorted((a, h) for a, h in
                        H_EQ_ESTRIBO_PERPENDICULAR_FT.values())
    elif orientacion == ORIENTACION_PARALELO_AL_TRAFICO:
        borde = (ds.valor("distancia_borde_calzada_al_trasdos_m")
                 if borde_m is None else borde_m)
        lejos = _columna_de_borde(borde)
        puntos = sorted((f[0], f[2] if lejos else f[1])
                        for f in H_EQ_MURO_PARALELO_FT.values())
    else:
        raise DatoInvalidoError(
            f"orientacion_muro_respecto_al_trafico = {orientacion!r} no es "
            f"una de las dos que AASHTO 3.11.6.4 tabula "
            f"({', '.join(ORIENTACIONES_TABULADAS)}). La fuente no ofrece un "
            f"eje libre de orientacion: ofrece dos binomios acoplados "
            f"(estribo+perpendicular y muro+paralelo) y no hay tabla para "
            f"ningun otro caso")

    h_eq_ft = _interpolar_h_eq(altura_ft, puntos)
    h_eq_aashto = h_eq_ft * PIE_EN_METROS
    # La regla del mayor de Sec. 0.2: el piso peruano y el valor tabulado de
    # AASHTO rigen a la vez.
    return max(SOBRECARGA_TRASDOS_PISO_MP_M, h_eq_aashto)


def _embocadura_paralela_del_cabezal(cabezal) -> bool:
    """Si el cabezal del punto lleva la embocadura paralela a la via (un
    cabezal sin embocadura -- armado a mano en un banco de pruebas -- no)."""
    embocadura = getattr(cabezal, "embocadura", None)
    return embocadura is not None and es_paralelo_a_la_via(embocadura)


def envolvente_de_h_eq_paralelo(entorno: EntornoDelCabezal) -> bool:
    """
    --- VE-7 (lote A, A7; triaje VE-7 de Fable) --- Si la h_eq de este
    cabezal es la ENVOLVENTE de las dos tablas de AASHTO 3.11.6.4: el muro
    es paralelo a la via (`EntornoDelCabezal.paralelo_a_la_via`, una fila de
    la Carta 11) y por tanto paralelo al trafico, la orientacion vigente es
    la perpendicular del [S] de corredor y el punto no declara la suya.
    """
    if (not getattr(entorno, "paralelo_a_la_via", False)
            or entorno.geometria.orientacion_trafico is not None):
        return False
    return (ds.valor("orientacion_muro_respecto_al_trafico")
            == ORIENTACION_PERPENDICULAR_AL_TRAFICO)


def h_eq_del_cabezal(entorno: EntornoDelCabezal, *,
                     altura_muro_total: float) -> float:
    """
    La h_eq de la sobrecarga viva de ESTE cabezal (`h_eq_sobrecarga_trasdos`
    con la orientacion y la distancia del punto). --- VE-7 (lote A, A7) ---
    Con `envolvente_de_h_eq_paralelo`, la MAYOR de las dos tablas: la del
    estribo perpendicular (3.11.6.4-1) y la del muro paralelo (3.11.6.4-2)
    con la distancia del punto o, sin ella, la columna «0.0 ft» (la mayor:
    lado seguro, sin leer la distancia de un corredor que dice
    perpendicular). El aviso lo da `avisos_de_la_sobrecarga_del_punto`.
    """
    g = entorno.geometria
    if not envolvente_de_h_eq_paralelo(entorno):
        return h_eq_sobrecarga_trasdos(altura_muro_total=altura_muro_total,
                                       orientacion=g.orientacion_trafico,
                                       borde_m=g.distancia_borde_calzada_m)
    borde = (g.distancia_borde_calzada_m
             if g.distancia_borde_calzada_m is not None else 0.0)
    return max(
        h_eq_sobrecarga_trasdos(
            altura_muro_total=altura_muro_total,
            orientacion=ORIENTACION_PERPENDICULAR_AL_TRAFICO),
        h_eq_sobrecarga_trasdos(
            altura_muro_total=altura_muro_total,
            orientacion=ORIENTACION_PARALELO_AL_TRAFICO, borde_m=borde))


def _columna_de_borde(borde_m: float) -> bool:
    """
    Cual de las DOS columnas de la Tabla 3.11.6.4-2 aplica. True = la de
    "1.0 ft or Further".

    LA TABLA TIENE DOS COLUMNAS Y NADA EN MEDIO. Sus rotulos son "0.0 ft" y
    "1.0 ft or Further", y la unica interpolacion que AASHTO autoriza es la de
    ALTURAS ("for intermediate wall heights"), entre filas. La banda abierta
    0 < d < 1.0 ft es laguna de la fuente y la cierra un criterio [A] vacio,
    no un redondeo de este modulo: hasta que se declare, el calculo se detiene.

    LA TOLERANCIA DECIDE IGUALDAD, NO LADO SEGURO, y la distincion es el
    hallazgo que la corrigio. Antes la comparacion era
    `borde >= UMBRAL - TOL`, que redondea hacia "lejos" -- la columna de h_eq
    MENOR, o sea el lado RELAJADO --, justo la direccion que los comentarios de
    alrededor condenan. Ahora la tolerancia solo sirve para reconocer los dos
    valores que la tabla SI tabula (0.0 ft y 1.0 ft) pese a la representacion
    binaria; lo que cae de verdad entre ellos no se redondea a ninguno de los
    dos: bloquea.
    """
    if borde_m >= H_EQ_BORDE_UMBRAL_M - TOL_UMBRAL_NORMATIVO:
        return True                       # columna "1.0 ft or Further"
    if borde_m <= TOL_UMBRAL_NORMATIVO:
        if borde_m < -TOL_UMBRAL_NORMATIVO:
            raise DatoInvalidoError(
                campo="distancia_borde_calzada_al_trasdos_m", valor=borde_m,
                motivo="una distancia del trasdos al borde de calzada no "
                       "puede ser negativa")
        return False                      # columna "0.0 ft"
    # La banda abierta: la fuente calla y el criterio esta vacio.
    regla = ca.valor(CRITERIO_H_EQ_BANDA_BORDE)   # VACIO: detiene aqui
    if regla == H_EQ_BANDA_LEE_COLUMNA_CERO:
        return False
    raise DatoInvalidoError(
        campo=CRITERIO_H_EQ_BANDA_BORDE, valor=regla,
        motivo="las lecturas declaradas de la banda 0 < d < 1.0 ft son "
               f"'{H_EQ_BANDA_LEE_COLUMNA_CERO}' y "
               f"'{H_EQ_BANDA_INTERPOLA}'; interpolar entre las dos columnas "
               "exige ademas escribir la regla, que la fuente no da")


def _interpolar_h_eq(altura_ft: float,
                     puntos: Sequence[Tuple[float, float]]) -> float:
    """
    Interpolacion lineal entre filas de una tabla de h_eq, en pies.

    "Linear interpolation shall be used for intermediate wall heights"
    (AASHTO 3.11.6.4). Es EXIGENCIA, con `shall`.

    FUERA DEL RANGO TABULADO la fuente calla y esta funcion NO extrapola:
      - por encima de la ultima fila, esta se rotula ">=20.0" y su valor rige
        para toda altura mayor -- eso SI lo escribe la tabla;
      - por debajo de la primera (5.0 ft = 1.524 m) no hay fila con que
        interpolar y extrapolar no lo autoriza nadie. Es una LAGUNA de la
        fuente y la cierra un criterio [A] VACIO, no este modulo: hasta que se
        declare, el calculo se detiene. Antes se tomaba la primera fila en
        duro, con el argumento de que era el lado conservador; no lo decide
        eso, porque extrapolar el primer tramo da un h_eq AUN MAYOR y las dos
        lecturas son elegibles.
    """
    if altura_ft <= puntos[0][0]:
        if altura_ft >= puntos[0][0] - TOL_UMBRAL_NORMATIVO:
            return puntos[0][1]           # la fila existe: no hay laguna
        regla = ca.valor(CRITERIO_H_EQ_BAJO_TABLA)    # VACIO: detiene aqui
        if regla == H_EQ_BAJO_TABLA_PRIMERA_FILA:
            return puntos[0][1]
        if regla == H_EQ_BAJO_TABLA_EXTRAPOLAR:
            (a0, h0), (a1, h1) = puntos[0], puntos[1]
            return h0 + (h1 - h0) * (altura_ft - a0) / (a1 - a0)
        raise DatoInvalidoError(
            campo=CRITERIO_H_EQ_BAJO_TABLA, valor=regla,
            motivo="las lecturas declaradas por debajo de la primera fila "
                   f"son '{H_EQ_BAJO_TABLA_PRIMERA_FILA}' y "
                   f"'{H_EQ_BAJO_TABLA_EXTRAPOLAR}'")
    if altura_ft >= puntos[-1][0]:
        return puntos[-1][1]
    for (a0, h0), (a1, h1) in zip(puntos, puntos[1:]):
        if a0 <= altura_ft <= a1:
            return h0 + (h1 - h0) * (altura_ft - a0) / (a1 - a0)
    raise DatoInvalidoError(
        f"altura de muro {altura_ft} ft fuera de la tabla de h_eq")


def presion_sobrecarga_trasdos(*, gamma_relleno: float, k_a: float,
                               altura_muro_total: float) -> float:
    """
    Presion horizontal constante de la sobrecarga de trasdos, kPa:

        p = gamma * h_eq * k_a       (num. 2.4.2.2 / AASHTO 3.11.6.4)

    El h_eq ya NO es el escalar 0.60: sale de `h_eq_sobrecarga_trasdos`, que
    lo resuelve por altura y orientacion y se detiene si la orientacion no
    esta declarada.

    LA FORMA `p = gamma * h_eq * k_a` NO ESTA EN EL NUMERAL PERUANO: el
    Manual escribe la sobrecarga como "altura de relleno equivalente" y el
    paso a presion es derivacion del proyectista, correcta y declarada.
    AASHTO SI la escribe, en su ec. 3.11.6.4-1 (Dp = k*gamma_s*h_eq).

    La presion es uniforme en toda la altura porque la sobrecarga equivale a
    una altura de relleno adicional constante, no a una carga triangular.
    """
    h_eq = h_eq_sobrecarga_trasdos(altura_muro_total=altura_muro_total)
    return gamma_relleno * h_eq * k_a


def empuje_sobrecarga_trasdos(*, gamma_relleno: float, k_a: float,
                              H: float,
                              altura_muro_total: Optional[float] = None) -> float:
    """
    Empuje horizontal de la sobrecarga por metro de muro, kN/m: la presion
    uniforme de `presion_sobrecarga_trasdos` por la altura H. Su resultante
    actua a H/2, por ser un diagrama rectangular (geometria, no criterio).

    LAS DOS ALTURAS NO SON LA MISMA, y por eso son dos argumentos:
      `H`                  la altura sobre la que se integra el diagrama, que
                           es la del empuje del punto;
      `altura_muro_total`  la que ENTRA EN LA TABLA de h_eq, y que AASHTO
                           define desde la superficie del relleno hasta el
                           FONDO DE LA ZAPATA -- o sea con la zapata dentro.
    Si no se pasa la segunda se usa la primera, y eso subestima la altura de
    entrada: como h_eq decrece con ella, el resultado queda del lado
    conservador. Se admite por compatibilidad con los llamadores que solo
    tienen una altura; quien tenga la geometria completa pasa las dos.
    """
    return presion_sobrecarga_trasdos(
        gamma_relleno=gamma_relleno, k_a=k_a,
        altura_muro_total=H if altura_muro_total is None
        else altura_muro_total) * H


def empuje_activo_estatico(*, gamma_relleno: float, k_a: float,
                           H: float) -> float:
    """
    P_A = gamma * H^2 * k_a / 2, kN/m: empuje activo del relleno (Sec. 9.2).
    Diagrama triangular, resultante a H/3 -- el centroide del triangulo, que
    es geometria y no una adopcion (a diferencia del brazo del incremento
    sismico, que si lo es: 'punto_aplicacion_incremento_sismico').
    """
    return gamma_relleno * H ** 2 * k_a / 2


def empuje_activo_sismico_total(*, gamma_relleno: float, K_AE: float,
                                H: float, k_v: float) -> float:
    """
    P_AE = gamma * H^2 * (1 - k_v) * K_AE / 2, kN/m: empuje TOTAL de
    Mononobe-Okabe, estatico mas sismico (Sec. 9.2). El factor (1 - k_v)
    recoge la aceleracion vertical; con el k_v = 0 adoptado vale 1.
    """
    return gamma_relleno * H ** 2 * (1 - k_v) * K_AE / 2


def incremento_sismico(*, gamma_relleno: float, K_AE: float, K_A: float,
                       H: float, k_v: float) -> float:
    """
    Delta P_AE = P_AE - P_A, kN/m: la parte estrictamente sismica del empuje,
    que es la que se suma en la combinacion Evento Extremo I. `K_A` debe ser
    el de `k_a_coulomb` (misma formulacion), no el de Rankine.
    """
    P_AE = empuje_activo_sismico_total(gamma_relleno=gamma_relleno,
                                       K_AE=K_AE, H=H, k_v=k_v)
    P_A = empuje_activo_estatico(gamma_relleno=gamma_relleno, k_a=K_A, H=H)
    return P_AE - P_A


def brazo_incremento_sismico(*, H: float) -> float:
    """
    Altura de aplicacion del incremento sismico sobre la base, en m.

    Se detiene en 'punto_aplicacion_incremento_sismico'
    (`CriterioPendienteError`): Mononobe-Okabe entrega el empuje y NO su punto
    de aplicacion, y sin brazo no hay momento de volteo sismico. El criterio
    guarda la fraccion de H, no la altura, para que sirva a cualquier cabezal.
    """
    return ca.valor(CRITERIO_BRAZO_SISMICO) * H


def altura_agua_sobre_base(*, D_f: float, NF_profundidad_m: float) -> float:
    """
    Altura de agua sobre el nivel de fundacion, en m: la profundidad de
    desplante menos la profundidad del NF, acotada en 0 cuando la zapata queda
    por encima del freatico.

    Sec. 9.2 es explicita: "empuje hidrostatico y subpresion: con NF a 1.4 m
    NO es opcional". El NF entra por argumento porque es la columna
    'NF_profundidad_m' del CSV, medida en el cruce -- dato de sitio [S] que
    varia punto a punto -- y no un criterio unico de proyecto: dos cabezales
    del mismo tramo pueden tener el freatico a profundidades distintas y cada
    uno se calcula con la suya. Quien lo lee de la fila usa
    `punto.exigir("NF_profundidad_m")`, que se detiene con DatoFaltanteError
    si el estudio geotecnico todavia no dio el valor de ese punto.
    """
    return max(D_f - NF_profundidad_m, 0.0)


def empuje_hidrostatico(*, h_agua: float) -> float:
    """
    E_w = gamma_agua * h_agua^2 / 2, kN/m (Sec. 9.2: "empuje hidrostatico y
    subpresion: con NF a 1.4 m no es opcional"). Es hidrostatica pura, no un
    coeficiente de empuje: el agua no tiene angulo de friccion y su empuje no
    se reduce por Ka. Confundirlos (multiplicar el empuje del agua por Ka) es
    el error clasico del trasdos con freatico.
    """
    return GAMMA_AGUA_KN_M3 * h_agua ** 2 / 2


def subpresion(*, h_agua: float, B: float) -> float:
    """
    U = gamma_agua * h_agua * B, kN/m: subpresion bajo la zapata
    (num. 2.4.3.8.2, el mismo numeral de la flotacion de M8).

    Hipotesis declarada: distribucion UNIFORME de valor gamma_agua * h_agua
    en todo el ancho B, es decir, sin alivio por drenaje ni gradiente de
    filtracion bajo la zapata. Es la lectura conservadora -- una distribucion
    con gradiente daria una resultante menor -- y es la coherente con la
    hipotesis de M8 para U ("NF en su cota mas alta"). Un diseno que necesite
    la distribucion real necesita una red de flujo, que no esta en el alcance
    de la hoja de ruta.
    """
    return GAMMA_AGUA_KN_M3 * h_agua * B


def peso_especifico_relleno() -> float:
    """
    Peso especifico del relleno del trasdos, kN/m3, del criterio
    'peso_especifico_relleno_kn_m3' -- el MISMO que usa M8 para el peso sobre
    la clave en V7. Un cabezal calculado con un relleno y un conducto
    verificado con otro seria una incoherencia de expediente.

    Se detiene con `CriterioPendienteError` mientras el criterio siga vacio.
    """
    return ca.valor(CRITERIO_GAMMA_RELLENO)


def peso_propio_cabezal(*, geometria: GeometriaCabezal) -> float:
    """
    Peso propio del cabezal por metro de muro, kN/m: la carga DC de las tres
    combinaciones de Sec. 9.2. Pantalla trapecial mas zapata rectangular.

        W = gamma_c * [ (e_corona + e_base_muro)/2 * H  +  B * e_zapata ]

    Es geometria exacta, no una aproximacion: el area de un trapecio es la
    semisuma de sus bases por la altura. Por eso `GeometriaCabezal` pide los
    DOS espesores de la pantalla -- con uno solo habria que suponer que es
    rectangular, y suponer eso subestima el peso, que aqui es el
    ESTABILIZANTE de volteo y deslizamiento.

    'peso_especifico_concreto_kn_m3' es [C] (AASHTO LRFD Tabla 3.5.1-1,
    23.56 kN/m3): la funcion calcula directo, ya no se detiene aqui.
    """
    gamma_c = ca.valor(CRITERIO_GAMMA_CONCRETO)
    area_pantalla = (geometria.espesor_corona + geometria.espesor_base_muro) / 2 * geometria.H
    area_zapata = geometria.B * geometria.espesor_zapata
    return gamma_c * (area_pantalla + area_zapata)


def empujes_trasdos(*, geometria: GeometriaCabezal,
                    condicion: CondicionAnalisis,
                    altura_empuje: float,
                    NF_profundidad_m: float) -> EmpujesTrasdos:
    """
    Ensambla las cargas horizontales de Sec. 9.2 sobre el trasdos, cada una
    con su brazo sobre la base: empuje activo (EH), sobrecarga de 0.60 m
    equivalente (LS), empuje hidrostatico y subpresion (WA) y, en condicion
    sismica, el incremento de Mononobe-Okabe (EQ).

    `altura_empuje` entra por argumento y NO se deduce de la geometria a
    proposito. La eleccion corriente es `geometria.altura_total`
    (H + espesor de zapata: el relleno actua contra el plano vertical que
    incluye el canto de la zapata), y para eso existe esa propiedad -- pero
    tambien se usa el plano vertical por el talon en muros con zapata larga,
    y son dos modelos distintos con dos resultados distintos. Escoger uno
    aqui y no decirlo seria decidir por el proyectista.

    Que Ka usa el empuje estatico, y la sobrecarga: EL DE COULOMB del Manual
    de Puentes, num. 2.4.4.1.5.3 (`k_a_coulomb`, la formulacion de
    Mononobe-Okabe con k_h = k_v = 0), y no el de Rankine. Se declara aqui,
    en el punto de uso, porque la hoja de ruta decia otra cosa (EXT-M-06):
    su Sec. 9.2 escribia "Ka = tan^2(45 - phi/2)" sin decir de donde salia,
    y hasta EXT-7 esta funcion la seguia -- empuje estatico y sobrecarga con
    `ka_rankine` mientras el incremento sismico iba con Mononobe-Okabe, que
    es Coulomb con aceleracion: dos familias de coeficiente sobre el mismo
    muro, decision declarada en dos docstrings y autorizada por ninguna
    fuente. La fuente primaria del marco elegido en Sec. 9.1 escribe Coulomb
    (ecs. 2.4.4.1.5.3-1 y -2, pag. impresa 135; cita `MP.2.4.4.1.5.3`), y
    con trasdos vertical, delta = 0 y relleno horizontal se reduce
    EXACTAMENTE a la forma que la hoja escribia (diferencia medida
    -5.6e-17). EXT-0 enmendo la v8; la discrepancia queda registrada y
    resuelta como `DIS-HR-KA-COULOMB`, y la memoria la imprime por
    `condicion_normativa_cabezal`.

    Consecuencias que conviene leer antes de usarla: (1) los cuatro angulos
    de Sec. 9.2 son entrada tambien en condicion ESTATICA -- antes solo phi
    lo era -- y un vacio la detiene; (2) `K_A` y `mononobe_okabe.K_A` son
    el MISMO numero, tambien con angulos no nulos, de modo que el incremento
    K_AE - K_A resta dos coeficientes homogeneos; (3) con i = beta =
    delta = 0 ningun numero se mueve respecto de Rankine, y `ka_rankine` se
    conserva como patron del caso limite. Dentro de las ventanas declaradas
    la diferencia no es un matiz: en el bloque C de CP-9 (i = 5, beta = 5,
    delta = 17 grados) el COEFICIENTE de Coulomb da +9.7 % sobre Rankine, y
    barriendo las cuatro ventanas enteras va de -11.1 % (phi = 30, i = beta
    = 0, delta = 22.7) a +44.4 % (phi = 38, i = beta = 10, delta = 0).

    LA RESULTANTE DE COULOMB ESTA INCLINADA, Y AQUI SE TOMA ENTERA COMO
    HORIZONTAL (auditoria adversarial de EXT-7). P_A = gamma*H^2*K_A/2 es la
    resultante sobre el trasdos, que actua a delta de la normal al paramento
    (Figura 2.4.4.1.5.3-1 del Manual): delta + beta respecto de la
    horizontal. Con Rankine (delta = beta = 0) era exactamente horizontal;
    con Coulomb no, y `EmpujesTrasdos` la suma integra como carga EH
    horizontal sin descomponerla en E_h = P_A*cos(delta + beta) y
    E_v = P_A*sen(delta + beta). Lo mismo le pasa a la sobrecarga (mismo
    Ka) y le pasaba ya al incremento sismico (P_AE tambien inclinado). En el
    bloque C la sobreestimacion de la horizontal es +7.9 % (1/cos 22 - 1) y
    llega a +18.8 % en el extremo de ventana (delta = 22.7, beta = 10); la
    horizontal verdadera queda solo +1.7 % sobre Rankine. La direccion NO es
    una: CONSERVADORA para E2 y E3 (mas fuerza horizontal y mas momento
    volcante) y NO conservadora para E1 en la parte de la componente
    vertical que deja de cargar sobre la base (mas normal, mas presion de
    contacto). No se descompone en EXT-7 porque `EmpujesTrasdos` no tiene
    modelo de cargas verticales del trasdos donde llevar E_v --- el vertical
    que hoy existe es la subpresion ---; queda diferido con simbolo
    (EXT-7-04 en docs/decisiones_diferidas.md) y declarado en la memoria por
    `KA_COULOMB_DECLARACION`.

    Brazos. Los tres estaticos son geometria y no criterio: el empuje activo
    es triangular y su resultante cae en H/3, la sobrecarga es rectangular y
    cae en H/2, y el agua es triangular sobre su propia altura. El brazo del
    incremento sismico NO es geometria -- Mononobe-Okabe da el empuje y no su
    punto de aplicacion -- y sale de 'punto_aplicacion_incremento_sismico'.

    `NF_profundidad_m` entra por argumento, como `altura_empuje`, y por la
    misma razon: es un dato del punto (columna del CSV, dato de sitio [S]
    medido en el cruce), no un criterio de proyecto. Quien llama lo saca de la
    fila con `punto.exigir("NF_profundidad_m")` y se detiene con
    DatoFaltanteError si el estudio geotecnico aun no lo dio para ese punto.

    EL AGUA BAJO EL NF, hipotesis declarada y no supuesta. El empuje activo
    se calcula con el peso especifico TOTAL del relleno en toda la altura y
    se le suma la hidrostatica completa, de modo que en la zona sumergida el
    agua de poros se cuenta dos veces. AASHTO 3.11.3 "Presence of Water"
    (pag. impresa 3-118 / PDF 172) exige lo contrario, y con un `shall`:
    "Submerged unit weights of the soil shall be used to determine the
    lateral earth pressure below the groundwater table". La desviacion es
    CONSERVADORA y esta acotada. El exceso NO es constante en la zona
    sumergida: es TRIANGULAR, crece desde 0 en el nivel freatico hasta
    Ka*gamma_agua*h_agua en la base --- 1.96 kPa con Ka = 1/3 y 0.60 m de
    agua, que es el valor EN LA BASE y no una constante. (El texto que ocupaba
    este lugar decia "constante en toda la zona sumergida" y se contradecia a
    si mismo tres lineas mas abajo: con el diagrama rectangular el muro de
    0.60 m daria +68 % y no el +25 % que el propio parrafo cita.)

    En porcentaje sobre el empuje lateral total, recomputado a mano contra
    AASHTO 3.11.3 con gamma = 19.0 kN/m3, gamma_agua = 9.81 kN/m3 y Ka = 1/3:
    +25.4 % sobre un muro de 0.60 m enteramente sumergido (el caso con que lo
    calculo la ficha MAT-O3) y +4.3 % sobre uno de 2.00 m con el freatico a
    1.40 m --- no el +11 % que decia este parrafo, que corresponderia a un
    muro de ~1.06 m. Menos cuanto mas alto el muro. Se
    mantiene porque corregirla exige un peso especifico SUMERGIDO del relleno
    que este expediente todavia no tiene: aplicar AASHTO con el unico gamma
    declarado seria aliviar el empuje sin dato que lo sostenga. El texto
    completo esta en `constantes_normativas.HIPOTESIS_EMPUJE_BAJO_NF` y viaja
    a la memoria por `condicion_normativa_cabezal`; la hoja de ruta no dice
    nada del NF en el empuje y por eso el defecto se reporta contra ella.

    Se detiene con `CriterioPendienteError` en el primero de los vacios que
    toque: el peso especifico del relleno, los cuatro angulos de K_AE (solo
    en condicion sismica) o el brazo del incremento.
    """
    gamma = peso_especifico_relleno()
    # Coulomb (MP 2.4.4.1.5.3), con los cuatro angulos declarados: es el
    # mismo K_A que resta el incremento sismico. CriterioPendienteError en
    # el primero de los cuatro que siga vacio, tambien en condicion estatica.
    K_A = k_a_coulomb(phi_grados=ca.valor(CRITERIO_PHI_RELLENO),
                      i_grados=ca.valor(CRITERIO_I_RELLENO),
                      beta_grados=ca.valor(CRITERIO_BETA_MURO),
                      delta_grados=ca.valor(CRITERIO_DELTA_MURO))

    E_a = empuje_activo_estatico(gamma_relleno=gamma, k_a=K_A,
                                 H=altura_empuje)
    # AASHTO mide la altura de entrada de h_eq desde la superficie del relleno
    # hasta el FONDO DE LA ZAPATA, con un `shall`. `geometria.H` es la altura
    # del muro SOBRE la zapata, de modo que la de la tabla es la suma.
    altura_para_h_eq = geometria.H + geometria.espesor_zapata
    # h_eq SE CALCULA APARTE Y VIAJA EN EL RESULTADO. Antes solo existia dentro
    # de `empuje_sobrecarga_trasdos` y se perdia: la memoria recibia el empuje
    # y no la altura equivalente, la orientacion ni la segunda fuente.
    h_eq = h_eq_sobrecarga_trasdos(altura_muro_total=altura_para_h_eq)
    E_s = empuje_sobrecarga_trasdos(
        gamma_relleno=gamma, k_a=K_A, H=altura_empuje,
        altura_muro_total=altura_para_h_eq)
    h_agua = altura_agua_sobre_base(D_f=geometria.D_f,
                                    NF_profundidad_m=NF_profundidad_m)
    E_w = empuje_hidrostatico(h_agua=h_agua)
    U = subpresion(h_agua=h_agua, B=geometria.B)

    incremento = None
    z_incremento = None
    mo = None
    if condicion is CondicionAnalisis.SISMICO:
        mo = k_ae_del_proyecto()          # CriterioPendienteError: los 4 angulos
        incremento = incremento_sismico(gamma_relleno=gamma, K_AE=mo.K_AE,
                                        K_A=mo.K_A, H=altura_empuje, k_v=mo.k_v)
        z_incremento = brazo_incremento_sismico(H=altura_empuje)

    return EmpujesTrasdos(
        condicion=condicion,
        altura_empuje=altura_empuje,
        gamma_relleno=gamma,
        E_activo=E_a, z_activo=altura_empuje / 3,   # literal-ok: centroide del triangulo
        E_sobrecarga=E_s, z_sobrecarga=altura_empuje / 2,
        E_hidrostatico=E_w, z_hidrostatico=h_agua / 3,   # literal-ok: centroide del triangulo
        U_subpresion=U,
        K_A=K_A,
        incremento_sismico=incremento,
        z_incremento=z_incremento,
        mononobe_okabe=mo,
        numeral=NUMERAL_9_2,
        h_eq_sobrecarga=h_eq,
        orientacion_muro=ds.valor("orientacion_muro_respecto_al_trafico"),
        numeral_sobrecarga=(f"{NUMERAL_SOBRECARGA_TRASDOS} + "
                            f"{NUMERAL_SOBRECARGA_TRASDOS_AASHTO}"),
        numeral_k_a=NUMERAL_KA_COULOMB,
    )


# ===========================================================================
# 9.2 - INERCIA DEL MURO Y DEMANDA SISMICA (100/50 - 50/100)
# El tramo de la cadena que faltaba entero: MAT-D6, MAT-X7, MAT-O16.
# ===========================================================================

def peso_suelo_sobre_talon(*, ancho_talon: float, altura_suelo: float,
                           gamma_relleno: float) -> float:
    """
    W_s, peso del suelo que gravita sobre el talon de la zapata, kN/m
    (num. 2.8.1.1.14.1).

    La fuente lo define ESTRECHO y conviene no ensancharlo: "el peso del
    suelo que esta inmediatamente encima del muro, incluyendo el talon del
    muro". No es el relleno del trasdos entero -- ese ya entra por el empuje
    activo -- sino la columna de suelo que la zapata carga y que, por tanto,
    acelera con el muro.

    `altura_suelo` entra por argumento y no se deduce de la geometria por la
    misma razon que `altura_empuje` en `empujes_trasdos`: la altura de suelo
    sobre el talon depende de donde se corte el plano de calculo, y elegirlo
    aqui seria decidir por el proyectista. La eleccion corriente es la altura
    del muro sobre la cara superior de la zapata.
    """
    return gamma_relleno * ancho_talon * altura_suelo


def fuerza_inercia_muro(*, k_h: float, W_w: float,
                        W_s: float) -> FuerzaInerciaMuro:
    """
    P_IR = k_h * (W_w + W_s), kN/m: la fuerza de inercia de la masa del muro
    (num. 2.8.1.1.14.1, ec. 2.8.1.1.14.1-1 = AASHTO 11.6.5.1-1).

    ESTE TERMINO NO EXISTIA EN EL REPOSITORIO. La cadena de la hoja de ruta
    termina en k_h y K_AE, y `empujes_trasdos` sumaba EH + LS + WA + el
    incremento de Mononobe-Okabe sin ninguna linea de inercia del muro. La
    omision es NO CONSERVADORA y no marginal: con k_h = 0.50, P_IR vale la
    mitad del peso movilizado, del mismo orden que el propio incremento
    sismico del empuje, y falta en el volteo y en el deslizamiento sismicos.

    Se reporta contra la hoja de ruta, que es la que hay que corregir: su
    Sec. 9.2 desagrega la cadena, cita el num. 2.8.1.1.14.2 para k_h0 y nunca
    menciona P_IR, que esta en el num. 2.8.1.1.14.1 -- la misma seccion, un
    nivel mas arriba.
    """
    return FuerzaInerciaMuro(P_IR=k_h * (W_w + W_s), W_w=W_w, W_s=W_s,
                             k_h=k_h, numeral=NUMERAL_P_IR)


def demanda_sismica_cabezal(*, P_AE: float, P_A: float,
                            inercia: FuerzaInerciaMuro
                            ) -> DemandaSismicaCabezal:
    """
    P_seis: los dos casos que el num. 2.8.1.1.14.1 manda investigar y el mas
    desfavorable de los dos.

        caso 1   100 % P_AE  +   50 % P_IR
        caso 2    50 % P_AE  +  100 % P_IR,
                  con el 50 % de P_AE acotado por abajo en el empuje activo
                  ESTATICO: "no sea menor que la presion estatica activa del
                  terreno (F = 1/2 gf h2 k)"

    La fuente dice por que son dos y no una suma: "los efectos de la
    combinacion de P_AE y P_IR NO SON SIMULTANEOS". Sumar el 100 % de los dos
    sobrestima; tomar solo uno subestima.

    ESTA FUNCION NO ELIGE EL QUE GOBIERNA, y es deliberado. La fuente manda
    quedarse con "el resultado mas conservador de estos dos ANALISIS", no con
    la mayor de las dos fuerzas: P_AE y P_IR actuan a alturas distintas, de
    modo que el orden por fuerza resultante no coincide con el orden por
    momento volcante, y elegir por la suma devuelve el caso equivocado justo
    donde equivocarse es no conservador. Quien evalue la estabilidad pasa el
    efecto que midio a `DemandaSismicaCabezal.mas_desfavorable`.

    QUE ES `P_AE` AQUI. El empuje TOTAL de Mononobe-Okabe -- estatico mas
    dinamico --, no el incremento. AASHTO lo advierte en el comentario del
    mismo articulo: "Since P_AE is the combined lateral earth pressure force
    resulting from static earth pressure plus dynamic effects, the static
    earth pressure ... K_a, should not be added to the seismic earth
    pressure". Pasarle el incremento de `incremento_sismico` en vez del total
    de `empuje_activo_sismico_total` es el error que este parrafo existe para
    impedir.

    QUE NO ENTRA. La sobrecarga de trasdos: el comentario excluye de P_AE las
    cargas de sobrecarga permanente sobre el muro, que aportan por su cuenta
    su empuje estatico y su propia inercia k_h*W_sobrecarga. Este objeto
    devuelve la demanda del PAR P_AE / P_IR, y quien ensamble la combinacion
    Evento Extremo I tiene que anadir esos dos terminos aparte.
    """
    # El piso estatico se identifica por el NOMBRE de la combinacion a la que
    # la fuente se lo pone, y ese nombre es dato [N]. Si alguna vez dejara de
    # coincidir, el piso se aplicaria a ninguna combinacion EN SILENCIO -- que
    # es exactamente la clase de omision no conservadora que este bloque
    # existe para cerrar --, asi que se comprueba en vez de confiarse.
    nombres = [nombre for nombre, _, _ in P_SEIS_COMBINACIONES]
    if P_SEIS_PISO_ESTATICO not in nombres:
        raise DatoInvalidoError(
            campo="P_SEIS_PISO_ESTATICO", valor=P_SEIS_PISO_ESTATICO,
            motivo=f"nombra una combinacion que no esta en "
                   f"P_SEIS_COMBINACIONES ({nombres}): el piso del empuje "
                   f"activo estatico que exige {NUMERAL_P_IR} no se estaria "
                   f"aplicando a ninguna",
        )
    casos = []
    for nombre, fraccion_ae, fraccion_ir in P_SEIS_COMBINACIONES:
        ae = fraccion_ae * P_AE
        piso = nombre == P_SEIS_PISO_ESTATICO and ae < P_A
        if piso:
            ae = P_A
        ir = fraccion_ir * inercia.P_IR
        casos.append(CasoDemandaSismica(
            nombre=nombre, fraccion_P_AE=fraccion_ae,
            fraccion_P_IR=fraccion_ir, P_AE_aplicado=ae, P_IR_aplicado=ir,
            total=ae + ir, piso_estatico_activo=piso,
        ))
    return DemandaSismicaCabezal(casos=tuple(casos), P_AE=P_AE, P_A=P_A,
                                 inercia=inercia, numeral=NUMERAL_P_IR)
