# -*- coding: utf-8 -*-
"""
M9_cabezal.ciclopeo
===================
Submodulo de Fase 9 (`M9_cabezal`): bloque `ciclopeo` (D1).
"""

from __future__ import annotations

import math
from typing import List, Sequence, Tuple

from dataclasses import replace as _reemplazar
from src import criterios_adoptados as ca
from src.constantes_fisicas import (
    GAMMA_AGUA_KN_M3,
    KPA_POR_MPA,
)
from src.constantes_normativas import (
    CICLOPEO_DOS_MINIMOS,
    CICLOPEO_FC_MATRIZ_MIN_APLICABLE,
    CICLOPEO_FRACCION_PIEDRA_MAX,
    CORTANTE_CONCRETO_SIMPLE_E060,
    E060_FACTOR_CE,
    E060_FACTOR_CM_MINIMO,
    E060_FACTOR_CV,
    EXCENTRICIDAD_MIN_MURO_CONCRETO_SIMPLE_E060,
    FC_DISENO_MAX_CICLOPEO_MPA,
    NUCLEO_CENTRAL_DIVISOR,
    NUMERAL_P_IR,
    PHI_CICLOPEO_E060,
    REDUCCION_PERALTE_CONTRA_SUELO_M,
    TRACCION_CONCRETO_SIMPLE_E060,
)
from src.modelos import (
    ArmadoDelCabezal,
    CIFRAS_FACTOR,
    CIFRAS_MAGNITUD,
    CRITERIOS_DE_TRACCION_CICLOPEO,
    CabezalDelPunto,
    CondicionAnalisis,
    DatoInvalidoError,
    EntornoDelCabezal,
    ErrorProyecto,
    LimiteNumericoError,
    MARCO_ASD,
    MOTIVO_METODO_NO_EVALUABLE_CABEZAL,
    Magnitud,
    MetodoNoEvaluableError,
    REGIMEN_RESISTENCIA_K0,
    TRACCION_NULA,
    Verificacion,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

from src.modulos.M9_cabezal._criterios import (
    CRITERIO_GAMMA_EQ,
    CRITERIO_K_V,
    ELEMENTOS_ARMADOS,
    LADOS_DEL_TRIANGULO,
    TIPO_GRAVEDAD,
    _finito,
)
from src.modulos.M9_cabezal.armado import (
    armar_elemento,
    ensamblar_armado,
)
from src.modulos.M9_cabezal.armado_secciones import (
    CRITERIO_CONCRETO_CICLOPEO,
    CRITERIO_JUNTA_CICLOPEO,
    CRITERIO_TRACCION_CICLOPEO,
    JUNTAS_DEL_ARRANQUE,
    JUNTA_DE_CONSTRUCCION,
    NUMERAL_9_4_CICLOPEO,
    _aviso_cabezal,
    _combinaciones_e060,
    _factores_por_tipo,
    _verificacion_de_armado,
    cargas_en_reposo,
    regimen_de_resistencia,
    solicitaciones_de_la_zapata,
    solicitaciones_de_resistencia,
)
from src.modulos.M9_cabezal.empujes import cadena_sismica
from src.modulos.M9_cabezal.estabilidad import (
    _incremento_sobre_el_arranque,
    diagrama_del_suelo_sobre,
)
from src.modulos.M9_cabezal.estabilidad_base import gamma_eq
from src.modulos.M9_cabezal.estabilidad_cargas import (
    C_EH_H,
    C_EQ_H,
    EMPUJE_ESTATICO_REPOSO,
    _casos_sismicos,
    _combinar,
    cargas_del_cabezal,
)

def armado_del_cabezal(entorno: EntornoDelCabezal, *,
                       alero_verificado: bool = False) -> ArmadoDelCabezal:
    """
    El armado completo de UN cabezal, de una sola llamada: sus tres
    elementos y su tabla si es de voladizo armado, o la verificacion de la
    alternativa ciclopea si es de gravedad (el tipo es el de T-7a). El
    servicio no la usa -- llama a `armar_elemento` por elemento para que
    cada fallo sea un `Bloqueo` aparte --; es la puerta de un tanteo y de
    los tests.
    """
    if entorno.geometria.tipo == TIPO_GRAVEDAD:
        return verificar_cabezal_ciclopeo(entorno)
    sol = solicitaciones_de_resistencia(entorno)
    piezas = []
    for elemento in ELEMENTOS_ARMADOS:
        piezas.extend(armar_elemento(entorno, elemento, sol))
    return ensamblar_armado(entorno, piezas, sol,
                            alero_verificado=alero_verificado)


# ---------------------------------------------------------------------------
# La alternativa ciclopea: el cabezal de gravedad
# ---------------------------------------------------------------------------

def acciones_sobre_una_seccion(entorno: EntornoDelCabezal, datos: dict, *,
                               z_seccion: float, en_reposo: bool) -> dict:
    """
    Las acciones de SERVICIO (sin factorar) que el cuerpo de un cabezal de
    gravedad transmite a una seccion horizontal a la altura `z_seccion` (m
    sobre la base de la zapata), por metro de muro:

      W     peso del concreto por encima de la seccion (trapecio de trasdos
            vertical) y su distancia `x_W` al trasdos;
      H_i   los empujes horizontales por encima de la seccion, con su brazo
            sobre ella: el del suelo -- el mismo diagrama del ensamble
            (triangular, con el peso sumergido bajo el agua), truncado a la
            altura de la seccion --, el de la sobrecarga viva y el del agua
            del relleno.

    Con `en_reposo` el coeficiente del suelo y de la sobrecarga es K0 y el
    empuje es horizontal; si no, es K_A y se toma su componente horizontal
    (la vertical, que estabiliza, se desprecia: lado seguro). No hay
    subpresion en una seccion interior del muro.
    """
    g = entorno.geometria
    e_z, H = g.espesor_zapata, g.H
    if not (_finito(z_seccion) and e_z - TOL_UMBRAL_NORMATIVO <= z_seccion
            < e_z + H):
        raise DatoInvalidoError(
            "z_seccion", valor=z_seccion, id_punto=entorno.id_punto,
            motivo="la seccion tiene que estar en el cuerpo del muro, entre "
                   "su arranque y su corona")
    y = z_seccion - e_z                      # altura sobre el arranque
    e_c, e_b = g.espesor_corona, g.espesor_base_muro
    t = e_b - (e_b - e_c) * y / H            # espesor en la seccion
    alto = H - y
    W = datos["gamma_c"] * (t + e_c) / 2 * alto
    x_W = ((t ** 2 + t * e_c + e_c ** 2) / (3 * (t + e_c))   # literal-ok: centroide del trapecio
           if t + e_c > 0 else 0.0)
    K = datos["K0"] if en_reposo else datos["K_A"]
    horizontal = 1.0 if en_reposo else math.cos(datos["inclinacion"])
    gamma, h = datos["gamma"], datos["h"]
    h_w = max(min(datos["h_w"], h) - z_seccion, 0.0)
    altura = max(h - z_seccion, 0.0)         # del diagrama sobre la seccion
    P_unitario, M_unitario = diagrama_del_suelo_sobre(datos, z_seccion)
    H_suelo = K * P_unitario * horizontal
    M_suelo = K * M_unitario * horizontal
    H_ls = K * gamma * datos["h_eq"] * altura
    M_ls = H_ls * altura / 2
    H_w = GAMMA_AGUA_KN_M3 * h_w ** 2 / 2
    M_w = H_w * h_w / 3                                       # literal-ok: centroide del triangulo
    return {"t": t, "W": W, "x_W": x_W, "K": K,
            "H_suelo": H_suelo, "M_suelo": M_suelo, "H_ls": H_ls,
            "M_ls": M_ls, "H_agua": H_w, "M_agua": M_w, "altura": altura}


def verificar_cabezal_ciclopeo(entorno: EntornoDelCabezal
                               ) -> ArmadoDelCabezal:
    """
    La alternativa en concreto CICLOPEO del cabezal de gravedad (T-7c punto
    3): no se arma; se comprueba que el muro trabaje sin traccion y que el
    material sea el que las fuentes admiten.

      C1  base: la resultante de las cargas de SERVICIO dentro del tercio
          central de la zapata, e <= B/6.
      C2  cuerpo, en su arranque sobre la zapata: e <= t/6. Con la junta de
          construccion de archivo ('junta_arranque_cabezal_ciclopeo') es la
          prohibicion de E.060 22.4.7 -- ninguna traccion a traves de la
          junta --, y se evalua con las cargas de servicio Y con las
          amplificadas de E.060 (la envolvente 0,9 CM + 1,7 CE + 1,7 CV);
          DECIDE siempre (correcciones de T-7c, H5).
      C3  cuerpo, a media altura: e <= t/6.
      C4  f'c de la matriz >= el mayor de los minimos de E.060 22.10 (10
          MPa) y de la Clase G del EG-2013 (14 MPa).
      C5  piedra desplazadora <= 30 % del volumen.
      C6  contraste con E.060 Cap. 22 (por analogia), en el arranque y a
          media altura, con SUS cargas amplificadas (9.2.5) y SU resistencia
          (phi = 0,5, f'c <= 10 MPa, peralte reducido en 50 mm): traccion
          M_u/S - P_u/A <= phi·0,42·sqrt(f'c) y cortante V_u <=
          phi·0,11·sqrt(f'c)·b·h.

    CUAL DECIDE lo declara 'criterio_traccion_cabezal_ciclopeo' [A]: con
    «tracciones_nulas» (archivo) deciden C1 y C3 y C6 informa; con
    «traccion_admisible_e060», al reves. C2 decide siempre con la junta de
    construccion; con el vaciado monolitico declarado, como C1 y C3. C4 y
    C5 deciden siempre. El umbral e <= B/6 o t/6 de C1 a C3 es criterio del
    proyecto (la `Interpretacion` de la cita E060.22.6.3#TERCIO dice por
    que esa cita no lo exige con cargas de servicio), salvo en la junta,
    donde lo sostiene 22.4.7.

      C7  (VE-6) la punta y el talon de la zapata como VOLADIZOS de
          concreto simple, cuando vuelan mas que la mitad de su peralte
          (E.060 22.10.2.2), con las cargas de E.060 9.2.5 y las
          resistencias de 22.5 (`_verificar_zapata_ciclopea`). Decide.
      C8  (VE-6) el cuerpo bajo SISMO, en el arranque y a media altura: e
          <= t/6 con el Evento Extremo I sin factorar, en los dos casos de
          AASHTO 11.6.5.1 (`_verificar_cuerpo_bajo_sismo`). Decide como C2 y
          C3.

    El empuje es el del regimen de resistencia ('regimen_resistencia_
    elementos_cabezal'): en reposo se toma, seccion por seccion, la
    excentricidad mayor de las dos. Bajo sismo la resultante en la BASE es
    la fila E2 de la estabilidad; el cuerpo, C8. Si la condicion sismica no
    es evaluable, C8 no sale y se avisa.
    """
    g = entorno.geometria
    est = CondicionAnalisis.ESTATICO
    quien = _aviso_cabezal(entorno)
    ext = entorno.extremo[0]
    regimen = regimen_de_resistencia()
    criterio = ca.valor(CRITERIO_TRACCION_CICLOPEO)
    if criterio not in CRITERIOS_DE_TRACCION_CICLOPEO:
        raise DatoInvalidoError(
            CRITERIO_TRACCION_CICLOPEO, valor=criterio,
            motivo="se espera una de: "
                   + ", ".join(CRITERIOS_DE_TRACCION_CICLOPEO))
    nulas = criterio == TRACCION_NULA
    junta = ca.valor(CRITERIO_JUNTA_CICLOPEO)
    if junta not in JUNTAS_DEL_ARRANQUE:
        raise DatoInvalidoError(
            CRITERIO_JUNTA_CICLOPEO, valor=junta,
            motivo="se espera una de: " + ", ".join(JUNTAS_DEL_ARRANQUE))
    con_junta = junta == JUNTA_DE_CONSTRUCCION
    caracter_proyecto = ("CRITERIO DEL PROYECTO (la cita no lo exige con "
                         "cargas de servicio: ver su interpretacion)")
    material = ca.valor(CRITERIO_CONCRETO_CICLOPEO)
    fc_matriz = material.get("fc_matriz_mpa") if hasattr(material, "get") \
        else None
    piedra = material.get("fraccion_piedra") if hasattr(material, "get") \
        else None
    if not (_finito(fc_matriz) and fc_matriz > 0 and _finito(piedra)
            and 0 <= piedra <= 1):
        raise DatoInvalidoError(
            CRITERIO_CONCRETO_CICLOPEO, valor=material,
            motivo="se esperan 'fc_matriz_mpa' positivo y 'fraccion_piedra' "
                   "entre 0 y 1")
    cargas, datos = cargas_del_cabezal(entorno, est)
    juegos = [("activo", cargas, False)]
    if regimen == REGIMEN_RESISTENCIA_K0:
        juegos.append(("reposo", cargas_en_reposo(cargas, datos), True))
    mag = lambda s, v, u, p, c=CIFRAS_MAGNITUD: Magnitud(s, v, u, p, cifras=c)  # noqa: E731
    verificaciones = []

    # --- C1: la base, con las cargas de servicio ----------------------------
    peor = None
    for nombre, juego, _ in juegos:
        for con_peso_ls in (True, False):
            f = _factores_por_tipo(juego, DC=1.0, EV=1.0, EH=1.0, LS=1.0,
                                   WA=1.0, **({} if con_peso_ls
                                              else {"LS_v": 0.0}))
            c = _combinar(f"Servicio ({nombre})", MARCO_ASD, est, juego, f,
                          g.B, "tracciones nulas")
            if not c.N > 0:
                raise LimiteNumericoError(
                    "N", valor=c.N,
                    motivo="la resultante vertical de servicio del cabezal "
                           "de gravedad no es de compresion")
            if peor is None or abs(c.excentricidad) > abs(peor[1].excentricidad):
                peor = (nombre, c)
    nombre_b, combo_b = peor
    e_b = abs(combo_b.excentricidad)
    limite_b = g.B / NUCLEO_CENTRAL_DIVISOR
    verificaciones.append(_verificacion_de_armado(
        fundamento="F9.CICLOPEO", codigo=f"C1.base.{ext}",
        que=f"C1, tracciones nulas en la base: cabezal de {entorno.extremo}",
        formula="e = |B/2 - (M_e - M_v)/N| <= B/6, con cargas de servicio",
        sustitucion=(
            mag("N", combo_b.N, "kN/m", f"suma de verticales, empuje "
                f"{nombre_b}"),
            mag("M_e - M_v", combo_b.momento_neto, "kN·m/m",
                "momento neto respecto de la punta"),
            mag("B", g.B, "m", "ancho de la zapata"),
        ),
        resultado=mag("e", e_b, "m", "excentricidad de la resultante"),
        descripcion_umbral="e <= B/6 (tercio central)", admisible=limite_b,
        unidad="m", cita="E060.22.6.3#TERCIO", caracter=caracter_proyecto,
        aplicacion="criterio del proyecto, mas exigente que la fuente: "
                   "E.060 admite traccion en el concreto simple "
                   f"('{CRITERIO_TRACCION_CICLOPEO}' [A])",
        criterio=CRITERIO_TRACCION_CICLOPEO,
        cumple=e_b <= limite_b + TOL_UMBRAL_NORMATIVO,
        margen=limite_b - e_b, decide=nulas, obtenido=e_b,
        nota=("La excentricidad de la estabilidad externa (fila E2) se mide "
              "con cargas factoradas y contra B/3; esta, con cargas de "
              "servicio y contra B/6, que es la condicion de que no haya "
              "traccion en el contacto."),
        explicacion_falla="la resultante cae fuera del tercio central de "
                          "la base: ampliar la zapata",
        numeral=NUMERAL_9_4_CICLOPEO))

    # --- C2, C3 y el contraste, seccion por seccion del cuerpo ---------------
    fc_dis = min(fc_matriz, FC_DISENO_MAX_CICLOPEO_MPA)
    f_t = PHI_CICLOPEO_E060 * TRACCION_CONCRETO_SIMPLE_E060 * math.sqrt(
        fc_dis) * KPA_POR_MPA                       # kPa
    uso_e060, detalle_e060 = 0.0, []
    for codigo, rotulo, z in (("C2", "arranque del cuerpo", g.espesor_zapata),
                              ("C3", "media altura del cuerpo",
                               g.espesor_zapata + g.H / 2)):
        peor_s = None
        peor_u = None           # la excentricidad amplificada de E.060
        for nombre, _, reposo in juegos:
            a = acciones_sobre_una_seccion(entorno, datos, z_seccion=z,
                                           en_reposo=reposo)
            M_h = a["M_suelo"] + a["M_ls"] + a["M_agua"]
            if not a["W"] > 0:
                raise LimiteNumericoError(
                    "W", valor=a["W"],
                    motivo="el peso del cuerpo sobre la seccion no es "
                           "positivo")
            # excentricidad hacia la cara expuesta, respecto del centro
            e = (M_h - a["W"] * (a["t"] / 2 - a["x_W"])) / a["W"]
            if peor_s is None or abs(e) > abs(peor_s[2]):
                peor_s = (nombre, a, e, M_h)
            # contraste E.060: la ENVOLVENTE de (9-6) y (9-7) que mas
            # tracciona -- el peso con 0,9 (9-7) y los empujes del suelo, del
            # agua y de la sobrecarga con 1,7 --, mas exigente que cada una.
            P_u = E060_FACTOR_CM_MINIMO * a["W"]
            M_u_centro = (E060_FACTOR_CE * (a["M_suelo"] + a["M_agua"])
                          + E060_FACTOR_CV * a["M_ls"]
                          - P_u * (a["t"] / 2 - a["x_W"]))
            e_u = M_u_centro / P_u
            if peor_u is None or abs(e_u) > abs(peor_u[1]):
                peor_u = (nombre, e_u)
            t_r = a["t"] - REDUCCION_PERALTE_CONTRA_SUELO_M
            if t_r > 0:
                # 22.6.3: excentricidad no menor de 0,10·h.
                M_u = max(abs(M_u_centro),
                          EXCENTRICIDAD_MIN_MURO_CONCRETO_SIMPLE_E060
                          * a["t"] * P_u)
                V_u = (E060_FACTOR_CE * (a["H_suelo"] + a["H_agua"])
                       + E060_FACTOR_CV * a["H_ls"])
                sigma_t = (M_u / (t_r ** 2 / NUCLEO_CENTRAL_DIVISOR)
                           - P_u / t_r)
                V_r = (PHI_CICLOPEO_E060 * CORTANTE_CONCRETO_SIMPLE_E060
                       * math.sqrt(fc_dis) * KPA_POR_MPA * t_r)
                uso = max(sigma_t / f_t, V_u / V_r)
                detalle_e060.append((rotulo, nombre, sigma_t, V_u, V_r, uso))
                uso_e060 = max(uso_e060, uso)
        nombre_s, a, e, M_h = peor_s
        limite = a["t"] / NUCLEO_CENTRAL_DIVISOR
        en_la_junta = codigo == "C2" and con_junta
        obtenido = (max(abs(e), abs(peor_u[1])) if en_la_junta else abs(e))
        verificaciones.append(_verificacion_de_armado(
            fundamento="F9.CICLOPEO", codigo=f"{codigo}.cuerpo.{ext}",
            que=f"{codigo}, tracciones nulas en el {rotulo}: cabezal de "
                f"{entorno.extremo}"
                + (" (junta de construccion, E.060 22.4.7)" if en_la_junta
                   else ""),
            formula=("e = [M_H - W·(t/2 - x_W)] / W <= t/6, con cargas de "
                     "servicio por encima de la seccion"
                     + (" y con las amplificadas de E.060 (0,9 CM; 1,7 CE "
                        "y CV): rige la mayor" if en_la_junta else "")),
            sustitucion=(
                mag("t", a["t"], "m", "espesor del cuerpo en la seccion"),
                mag("W", a["W"], "kN/m", "peso del concreto por encima"),
                mag("x_W", a["x_W"], "m", "de su centro de gravedad al "
                    "trasdos"),
                mag("M_H", M_h, "kN·m/m", f"empujes del suelo (K = "
                    f"{a['K']:.3f}, {nombre_s}), de la sobrecarga y del "
                    "agua, por encima de la seccion"),
                mag("e (servicio)", abs(e), "m", "con cargas de servicio"),
                mag("e_u (E.060)", abs(peor_u[1]), "m",
                    f"con 0,9 CM y 1,7 CE y CV ({peor_u[0]})"
                    + ("" if en_la_junta else ": informa")),
            ),
            resultado=mag("e", obtenido, "m", "excentricidad de la "
                          "resultante en la seccion"
                          + (": la mayor de las dos" if en_la_junta else "")),
            descripcion_umbral="e <= t/6 (tercio central)", admisible=limite,
            unidad="m",
            cita="E060.22.4.7#JUNTAS" if en_la_junta else "E060.22.6.3#TERCIO",
            caracter=None if en_la_junta else caracter_proyecto,
            aplicacion=("exigencia de E.060 22.4.7, por analogia: el "
                        "arranque es una junta de construccion "
                        f"('{CRITERIO_JUNTA_CICLOPEO}' = '{junta}'); decide "
                        "con cualquier criterio de traccion"
                        if en_la_junta else
                        "criterio del proyecto, mas exigente que la fuente "
                        f"('{CRITERIO_TRACCION_CICLOPEO}' [A])"),
            criterio=(CRITERIO_JUNTA_CICLOPEO if en_la_junta
                      else CRITERIO_TRACCION_CICLOPEO),
            cumple=obtenido <= limite + TOL_UMBRAL_NORMATIVO,
            margen=limite - obtenido, decide=nulas or en_la_junta,
            obtenido=obtenido,
            nota=("La componente vertical del empuje activo, que "
                  "estabiliza, no se cuenta."),
            explicacion_falla=("la junta del arranque transmitiria traccion, "
                               "que E.060 22.4.7 prohibe: aumentar el "
                               "espesor del cuerpo" if en_la_junta else
                               "hay traccion en el trasdos del cuerpo: "
                               "aumentar su espesor"),
            numeral=NUMERAL_9_4_CICLOPEO))

    # --- C4 y C5: el material -------------------------------------------------
    verificaciones.append(_verificacion_de_armado(
        fundamento="F9.CICLOPEO", codigo=f"C4.material.{ext}",
        que="C4, resistencia de la matriz del concreto ciclopeo: cabezal "
            f"de {entorno.extremo}",
        formula="f'c de la matriz >= max(10 MPa de E.060 22.10.1, 14 MPa de "
                "la Clase G del EG-2013)",
        sustitucion=(mag("f'c matriz", fc_matriz, "MPa",
                         f"'{CRITERIO_CONCRETO_CICLOPEO}' [A]", 1),),
        resultado=mag("f'c matriz", fc_matriz, "MPa", "especificado", 1),
        descripcion_umbral="f'c >= el mayor de los dos minimos",
        admisible=CICLOPEO_FC_MATRIZ_MIN_APLICABLE, unidad="MPa",
        cita="EG2013.503.04#T503_07",
        aplicacion="el mayor de los dos minimos que rigen sobre el mismo "
                   "material; el de E.060, por analogia",
        criterio=CRITERIO_CONCRETO_CICLOPEO,
        cumple=fc_matriz >= CICLOPEO_FC_MATRIZ_MIN_APLICABLE
        - TOL_UMBRAL_NORMATIVO,
        margen=fc_matriz - CICLOPEO_FC_MATRIZ_MIN_APLICABLE, decide=True,
        obtenido=fc_matriz, nota=CICLOPEO_DOS_MINIMOS,
        explicacion_falla="la matriz no alcanza la resistencia minima",
        numeral=NUMERAL_9_4_CICLOPEO))
    verificaciones.append(_verificacion_de_armado(
        fundamento="F9.CICLOPEO", codigo=f"C5.material.{ext}",
        que="C5, volumen de piedra desplazadora: cabezal de "
            f"{entorno.extremo}",
        formula="piedra desplazadora <= 30 % del volumen total",
        sustitucion=(mag("fraccion de piedra", piedra, "",
                         f"'{CRITERIO_CONCRETO_CICLOPEO}' [A]",
                         CIFRAS_FACTOR),),
        resultado=mag("fraccion de piedra", piedra, "", "especificada",
                      CIFRAS_FACTOR),
        descripcion_umbral="fraccion <= 0,30",
        admisible=CICLOPEO_FRACCION_PIEDRA_MAX, unidad="",
        cita="EG2013.503.04#T503_07",
        aplicacion="limite de la Clase G del EG-2013 y de E.060 22.10.1 b)",
        criterio=CRITERIO_CONCRETO_CICLOPEO,
        cumple=piedra <= CICLOPEO_FRACCION_PIEDRA_MAX + TOL_UMBRAL_NORMATIVO,
        margen=CICLOPEO_FRACCION_PIEDRA_MAX - piedra, decide=True,
        obtenido=piedra,
        nota="La mayor dimension de la piedra no excede la mitad de la "
             "menor dimension del elemento ni 250 mm (E.060 22.10.1 c): es "
             "de la especificacion de obra.",
        explicacion_falla="demasiada piedra desplazadora",
        numeral=NUMERAL_9_4_CICLOPEO))

    # --- C6: el contraste con E.060 -------------------------------------------
    verificaciones.append(_verificacion_de_armado(
        fundamento="F9.CICLOPEO", codigo=f"C6.cuerpo.{ext}",
        que="C6, traccion y cortante del cuerpo con E.060 Cap. 22 (por "
            f"analogia): cabezal de {entorno.extremo}",
        formula="M_u/S - P_u/A <= phi·0,42·sqrt(f'c)  y  V_u <= "
                "phi·0,11·sqrt(f'c)·b·h, con phi = 0,5, f'c <= 10 MPa y h "
                "reducido en 50 mm",
        sustitucion=tuple(
            mag(f"{rotulo} ({nombre})", uso, "",
                f"traccion {sigma:.1f} kPa frente a {f_t:.1f} kPa; cortante "
                f"{V:.1f} frente a {Vr:.1f} kN/m; cargas 0,9 CM con 1,7 CE "
                "y CV (envolvente de 9-6 y 9-7)", CIFRAS_FACTOR)
            for rotulo, nombre, sigma, V, Vr, uso in detalle_e060) or (
            mag("secciones", 0, "", "ninguna evaluable"),),
        resultado=mag("aprovechamiento", uso_e060, "",
                      "el mayor de las secciones y de los dos cocientes",
                      CIFRAS_FACTOR),
        descripcion_umbral="aprovechamiento <= 1 en el marco de E.060",
        admisible=1.0, unidad="", cita="E060.22.5.3#TRACCION",
        aplicacion="por analogia ([N→]): E.060 es norma de edificaciones",
        criterio=CRITERIO_TRACCION_CICLOPEO,
        cumple=uso_e060 <= 1 + TOL_UMBRAL_NORMATIVO,
        margen=1.0 - uso_e060, decide=not nulas, obtenido=uso_e060,
        nota=("Una traccion negativa significa que la seccion sigue "
              "comprimida. Cargas y resistencias son las dos de E.060: los "
              "marcos no se cruzan. El momento no baja de P_u·0,10·t "
              "(22.6.3). El cuerpo no se vacia contra el suelo: la "
              "reduccion de 50 mm de 22.4.8 se aplica del lado seguro. La "
              "traccion que esta fila admite en el arranque la prohibe "
              "22.4.7 en la junta: ahi decide C2."),
        explicacion_falla="la traccion o el cortante superan la "
                          "resistencia del concreto ciclopeo",
        citas=("E060.22.10.2.3#PHI", "E060.22.5.4#CORTANTE",
               "E060.22.4.8#PERALTE", "E060.9.2.5#EMPUJE",
               "E060.22.6.3#EXCENTRICIDAD", "E060.22.4.7#JUNTAS"),
        numeral=NUMERAL_9_4_CICLOPEO))

    # --- C7: la zapata como voladizo de concreto simple (VE-6, ficha
    # T7C-09 (3)) ---------------------------------------------------------
    voladizos, avisos = _verificar_zapata_ciclopea(
        entorno, juegos, datos, fc_dis=fc_dis, f_t=f_t, mag=mag, ext=ext)
    verificaciones.extend(voladizos)

    # --- C8: el cuerpo bajo SISMO (VE-6, ficha T7C-09 (2)) -----------------
    sismicas, sismico, aviso_sismo = _verificar_cuerpo_bajo_sismo(
        entorno, regimen=regimen, nulas=nulas, con_junta=con_junta,
        junta=junta, caracter_proyecto=caracter_proyecto, mag=mag, ext=ext)
    verificaciones.extend(sismicas)
    if aviso_sismo:
        avisos.append(f"{quien}: {aviso_sismo}")

    avisos[:0] = [
        f"{quien}: es de GRAVEDAD en concreto ciclopeo y no se arma. Bajo "
        "sismo la base es la fila E2 de la estabilidad y el cuerpo se "
        "verifica en C8 (Evento Extremo I sin factorar, los dos casos de "
        "AASHTO 11.6.5.1); la zapata, como voladizo de concreto simple en C7 "
        "cuando vuela mas que la mitad de su peralte (E.060 22.10.2.2), "
        "solo con las cargas estaticas de E.060 9.2.5",
        f"{quien}: decide '{criterio}' ('{CRITERIO_TRACCION_CICLOPEO}' "
        "[A]) en C1, C3 y C6; la otra verificacion de traccion informa"
        + (". C2 decide siempre: el arranque es una junta de construccion y "
           "E.060 22.4.7 prohibe transmitir traccion por ella"
           if con_junta else
           ". C2 tambien: se declaro el vaciado monolitico del arranque "
           f"('{CRITERIO_JUNTA_CICLOPEO}')"),
        f"{quien}: el vano del conducto atraviesa el cuerpo: E.060 22.6.6.5 "
        "pide dos barras de 5/8\" alrededor de las aberturas de los muros "
        "de concreto simple, que el programa no dimensiona; las secciones "
        "C2, C3 y C8 son las de un metro de muro lleno",
    ]
    for v in voladizos:
        avisos.append(
            f"{quien}: la zapata vuela mas que la mitad de su peralte "
            f"({g.espesor_zapata / 2:.2f} m): E.060 22.10.2.2 pide verificar "
            f"su flexion y su corte como voladizo, y se verifican en la fila "
            f"{v.codigo}")
    return ArmadoDelCabezal(
        id_punto=entorno.id_punto, extremo=entorno.extremo,
        tipo=TIPO_GRAVEDAD, regimen=regimen, fc_mpa=float(fc_matriz),
        fy_mpa=None, verificaciones=tuple(verificaciones),
        pasos=tuple(v.paso for v in verificaciones), avisos=tuple(avisos),
        sismico=sismico, K0=datos["K0"], K_A=datos["K_A"])


def _verificar_zapata_ciclopea(entorno: EntornoDelCabezal, juegos: list,
                               datos: dict, *, fc_dis: float, f_t: float,
                               mag, ext: str
                               ) -> Tuple[List[Verificacion], List[str]]:
    """
    --- VE-6 (ficha T7C-09 (3)) --- C7: la punta y el talon de la zapata de
    un cabezal de gravedad en ciclopeo, como VOLADIZOS de concreto simple,
    cuando vuelan mas que la mitad del peralte de la zapata: E.060 22.10.2.2
    («En elementos en voladizo con una longitud mayor a la mitad de su
    peralte, sera necesario verificar las resistencias en flexion y corte»,
    cita E060.22.10.2.2#VOLADIZO, pag. 195, firmada en VE-7 A11: es la
    cita principal de C7; E060.22.10.2#CICLOPEO la acompana).

    En la cara del cuerpo, con las solicitaciones de la zapata que el armado
    ya calcula (`solicitaciones_de_la_zapata`: presion de contacto LINEAL y
    subpresion; el talon descontando la reaccion, como en E.060 15.4.1) para
    las dos combinaciones de E.060 9.2.5 (`_combinaciones_e060`) y cada
    juego de empujes del regimen (activo; y el reposo con
    'no_cedente_k0'). Resistencias de E.060 22.5 con phi = 0,5 y f'c <= 10
    MPa (22.10.2.3), y el peralte reducido en 50 mm porque la zapata se
    vacia contra el suelo (22.4.8):

        traccion  M_u / S <= phi·0,42·sqrt(f'c),   S = b·h²/6   (22-7, P_u = 0)
        cortante  V_u <= phi·0,11·sqrt(f'c)·b·h                  (22-9)

    El aprovechamiento es el mayor de los dos cocientes. El cortante se toma
    EN LA CARA del cuerpo y no a una distancia de ella: lado seguro. Las
    cargas y la resistencia son las dos de E.060 (los marcos no se cruzan).
    Solo estatica: E.060 9.2 no combina el sismo con el empuje del suelo.
    Esta fila DECIDE: es la unica verificacion de la flexion y el corte de
    la zapata, y la pide la norma (por analogia).

    --- dictamen Fable de VE-6 --- Devuelve (filas, avisos): si alguna
    combinacion saca la resultante de la base y otras no, la fila decide con
    las evaluables y el aviso nombra las descartadas.
    """
    g = entorno.geometria
    h_r = g.espesor_zapata - REDUCCION_PERALTE_CONTRA_SUELO_M
    vuelos = (("punta", datos["punta"]), ("talon", datos["talon"]))
    salida: List[Verificacion] = []
    avisos: List[str] = []
    for rotulo, vuelo in vuelos:
        if not vuelo > g.espesor_zapata / 2 + TOL_UMBRAL_NORMATIVO:
            continue
        if not h_r > 0:
            raise LimiteNumericoError(
                "h", valor=h_r,
                motivo="el peralte de la zapata reducido en 50 mm (E.060 "
                       "22.4.8) no es positivo")
        S = h_r ** 2 / NUCLEO_CENTRAL_DIVISOR
        V_r = (PHI_CICLOPEO_E060 * CORTANTE_CONCRETO_SIMPLE_E060
               * math.sqrt(fc_dis) * KPA_POR_MPA * h_r)
        peor = None
        fuera = []
        for nombre, juego, _ in juegos:
            for combo in _combinaciones_e060(juego, g.B):
                z = solicitaciones_de_la_zapata(g, juego, combo, datos)
                if z is None:
                    fuera.append(f"{combo.nombre}, {nombre}")
                    continue
                V, M = z[rotulo]
                uso = max(abs(M) / S / f_t, abs(V) / V_r)
                if peor is None or uso > peor[0]:
                    peor = (uso, abs(M), abs(V), f"{combo.nombre}, {nombre}")
        if peor is None:
            # Como el armado de la punta (`solicitaciones_de_resistencia`):
            # sin presion de contacto no hay voladizo que verificar, y el
            # cabezal no queda callado -- la etapa del servicio lo vuelve un
            # `Bloqueo` del punto --.
            raise MetodoNoEvaluableError(
                f"C7, la {rotulo} de la zapata del cabezal de "
                f"{entorno.extremo} como voladizo de concreto simple",
                "una zapata mas ancha (la resultante tiene que caer dentro "
                "de la base para que haya presion de contacto que integrar)",
                "con las cargas de E.060 9.2.5 la resultante cae fuera de la "
                "base en todas las combinaciones (" + "; ".join(fuera)
                + "): el cabezal de gravedad vuelca con esas cargas y su "
                "zapata no tiene reaccion con que verificarse",
                entorno.id_punto, rotulo=MOTIVO_METODO_NO_EVALUABLE_CABEZAL)
        uso, M, V, de_donde = peor
        if fuera:
            avisos.append(
                f"{_aviso_cabezal(entorno)}: C7 ({rotulo} de la zapata como "
                "voladizo) se evaluo sin " + "; ".join(fuera)
                + ": con esas cargas de E.060 la resultante cae fuera de la "
                "base y no hay presion de contacto; la fila decide con las "
                "demas combinaciones, y ese cabezal vuelca con las "
                "descartadas")
        salida.append(_verificacion_de_armado(
            fundamento="F9.CICLOPEO", codigo=f"C7.{rotulo}.{ext}",
            que=f"C7, la {rotulo} de la zapata como voladizo de concreto "
                f"simple: cabezal de {entorno.extremo}",
            formula="max[(M_u/S)/(phi·0,42·sqrt(f'c)), V_u/(phi·0,11·"
                    "sqrt(f'c)·b·h)] <= 1, con S = b·h²/6, phi = 0,5, f'c <= "
                    "10 MPa y h reducido en 50 mm",
            sustitucion=(
                mag("vuelo", vuelo, "m", f"de la {rotulo}, desde la cara "
                    "del cuerpo"),
                mag("h", h_r, "m", "peralte de la zapata menos 50 mm "
                    "(E.060 22.4.8: vaciada contra el suelo)"),
                mag("M_u", M, "kN·m/m", f"en la cara del cuerpo ({de_donde})"),
                mag("V_u", V, "kN/m", "en la cara del cuerpo, misma "
                    "combinacion"),
                mag("phi·0,42·sqrt(f'c)", f_t, "kPa", "traccion admisible "
                    "(22-7, 22.10.2.3)"),
                mag("phi·0,11·sqrt(f'c)·b·h", V_r, "kN/m", "cortante "
                    "resistente (22-9)"),
            ),
            resultado=mag("aprovechamiento", uso, "", "el mayor de los dos "
                          "cocientes", CIFRAS_FACTOR),
            descripcion_umbral="aprovechamiento <= 1 en el marco de E.060",
            admisible=1.0, unidad="", cita="E060.22.5.3#TRACCION",
            aplicacion="por analogia ([N→]): E.060 22.10.2.2 manda verificar "
                       "el voladizo de concreto ciclopeo mas largo que la "
                       "mitad de su peralte, y E.060 es norma de "
                       "edificaciones",
            criterio=CRITERIO_CONCRETO_CICLOPEO,
            cumple=uso <= 1 + TOL_UMBRAL_NORMATIVO, margen=1.0 - uso,
            decide=True, obtenido=uso,
            nota=("Las solicitaciones son las del armado (presion de "
                  "contacto lineal y subpresion; el talon descuenta la "
                  "reaccion del terreno, como E.060 15.4.1). El cortante se "
                  "toma en la cara del cuerpo, del lado seguro. Solo con las "
                  "cargas estaticas: E.060 9.2 no combina el sismo con el "
                  "empuje del suelo."
                  + (" Sin presion de contacto (la resultante cae fuera de "
                     "la base) en: " + "; ".join(fuera) + "; esas "
                     "combinaciones no entran." if fuera else "")),
            explicacion_falla=f"la {rotulo} de la zapata no resiste como "
                              "voladizo de concreto simple: aumentar su "
                              "peralte o acortar su vuelo",
            citas=("E060.22.10.2.2#VOLADIZO", "E060.22.10.2#CICLOPEO",
                   "E060.22.10.2.3#PHI", "E060.22.5.4#CORTANTE",
                   "E060.22.4.8#PERALTE", "E060.9.2.5#EMPUJE"),
            numeral=NUMERAL_9_4_CICLOPEO))
    return salida, avisos


def _verificar_cuerpo_bajo_sismo(entorno: EntornoDelCabezal, *, regimen: str,
                                 nulas: bool, con_junta: bool, junta: str,
                                 caracter_proyecto: str, mag, ext: str
                                 ) -> Tuple[List[Verificacion], bool, str]:
    """
    --- VE-6 (ficha T7C-09 (2)) --- C8: las secciones del cuerpo de un
    cabezal de gravedad en ciclopeo bajo SISMO, en el arranque y a media
    altura, con la misma condicion que C2 y C3 -- la resultante en el tercio
    central del espesor, e <= t/6 -- y las cargas del Evento Extremo I SIN
    FACTORAR, que son las de C1 a C3 con el sismo:

        e = [M_H - W·(t/2 - x_W)] / W,
        M_H = f_EH·M_EH + M_LS + M_WA + f_inc·M_dPAE + f_IR·k_h·W·y_W

    M_EH, M_LS y M_WA son los de C2 y C3 (`acciones_sobre_una_seccion`: el
    diagrama del plano virtual truncado en la seccion), con el empuje
    estatico del ensamble sismico; M_dPAE, el del incremento con el diagrama
    lineal del ensamble (`_incremento_sobre_el_arranque`) por encima de la
    seccion; k_h·W·y_W es la inercia del cuerpo POR ENCIMA de la seccion
    en su centro de gravedad (y_W = alto·(t + 2·e_c)/(3·(t + e_c)), el del
    trapecio). Los factores f son los dos casos de AASHTO 11.6.5.1 (Manual
    de Puentes 2.8.1.1.14.1, `P_SEIS_COMBINACIONES`, «El resultado mas
    conservador de estos dos analisis se usara para el diseno del muro»),
    los mismos que la fila E2 (`_casos_sismicos`), y rige la mayor
    excentricidad. Con 'no_cedente_k0' el ensamble del armado va con k_h =
    1.0·k_h0 (11.6.5.4), como el Evento Extremo I de las pantallas armadas.
    --- VE-7 (lote A, A4; abierto (a) de VE6M9-01) --- CON k_v DISTINTO DE
    CERO el peso estabilizante del cuerpo va con (1 - k_v), el signo
    desfavorable (la aceleracion vertical hacia arriba lo aligera): e =
    [M_H - W·(1 - k_v)·(t/2 - x_W)] / [W·(1 - k_v)]; la inercia horizontal
    sigue con la masa entera, k_h·W. Con k_v = 0 es la formula de VE-6. El
    ensamble E1-E3 tambien aplica (1 - k_v) a los pesos desde el dictamen
    de Fable (carga `C_EQ_KV`).

    En el arranque, con la junta de construccion de archivo, la condicion es
    la de E.060 22.4.7 y DECIDE siempre. --- VE-7 (lote A, A3; abierto (b)
    de VE6M9-01) --- a media altura TAMBIEN decide con cualquier criterio
    de traccion, atribuido a 'criterio_traccion_cabezal_ciclopeo': bajo
    sismo E.060 9.2 no combina el sismo con el empuje y no hay contraste que
    lo cubra (la misma razon que el dictamen de VE-6 dio para el arranque).
    Devuelve (verificaciones, evaluado, aviso): si la condicion sismica no
    es evaluable (agua en el plano de empuje con relleno muy abierto, una
    cuña sin maximo...), no hay filas y el aviso dice por que, como el
    armado de las pantallas; evaluada, el aviso es el de k_v, o vacio.
    """
    g = entorno.geometria
    sis = CondicionAnalisis.SISMICO
    try:
        k_h_armado = (cadena_sismica().k_h0
                      if regimen == REGIMEN_RESISTENCIA_K0 else None)
        cargas_s, datos_s = cargas_del_cabezal(entorno, sis, k_h=k_h_armado)
    except ErrorProyecto as motivo:
        return [], False, (
            "el cuerpo NO se verifico bajo sismo (C8): la condicion sismica "
            f"no es evaluable -- {motivo}")
    casos = _casos_sismicos(datos_s)
    # --- dictamen Fable de VE-6 --- la sobrecarga viva con gamma_EQ, el
    # factor de la carga viva del Evento Extremo I ('gamma_EQ' [A]), como la
    # fila E2 (`combinaciones_de_estabilidad`), y no con 1.
    g_eq = gamma_eq()
    if not (_finito(g_eq) and 0 <= g_eq <= 1):
        raise DatoInvalidoError(CRITERIO_GAMMA_EQ, valor=g_eq,
                                motivo="gamma_EQ entre 0 y 1")
    e_c, e_z = g.espesor_corona, g.espesor_zapata
    # --- VE-7 (lote A, A4) --- el peso que estabiliza, con (1 - k_v).
    k_v = datos_s.get("k_v") or 0.0
    alivio_vertical = 1 - k_v
    if not (_finito(k_v) and alivio_vertical > 0):
        raise LimiteNumericoError(
            "k_v", valor=k_v, id_punto=entorno.id_punto,
            motivo="con k_v >= 1 el peso del cuerpo no estabiliza nada")
    con_k_v = abs(k_v) > TOL_UMBRAL_NORMATIVO
    salida: List[Verificacion] = []
    for codigo, rotulo, z in (("arranque", "arranque del cuerpo", e_z),
                              ("media", "media altura del cuerpo",
                               e_z + g.H / 2)):
        # El diagrama ESTATICO es el de C2 y C3 (el del plano virtual,
        # truncado en la seccion), con el empuje que el ensamble sismico
        # trae: el activo, o el reposo del muro que no cede en conjunto.
        acc = acciones_sobre_una_seccion(
            entorno, datos_s, z_seccion=z,
            en_reposo=datos_s.get("empuje_estatico")
            == EMPUJE_ESTATICO_REPOSO)
        W, t, x_W = acc["W"], acc["t"], acc["x_W"]
        if not W > 0:
            raise LimiteNumericoError(
                "W", valor=W, motivo="el peso del cuerpo sobre la seccion no "
                                     "es positivo")
        alto = g.H - (z - e_z)
        y_W = alto * (t + 2 * e_c) / (LADOS_DEL_TRIANGULO * (t + e_c))
        M_PIR = datos_s["k_h"] * W * y_W
        M_EH, M_LS, M_WA = acc["M_suelo"], acc["M_ls"], acc["M_agua"]
        por = {c.codigo: c for c in cargas_s}
        H_EH = por[C_EH_H].H if C_EH_H in por else 0.0
        H_dP = por[C_EQ_H].H if C_EQ_H in por else 0.0
        # El incremento, con el diagrama lineal del ensamble
        # (`_incremento_sobre_el_arranque`) truncado en la seccion.
        M_dP = _incremento_sobre_el_arranque(H_dP, datos_s, z,
                                             entorno.id_punto)[1]
        W_v = W * alivio_vertical
        palanca = W_v * (t / 2 - x_W)
        # Con 'no_cedente_k0', como la pantalla armada
        # (`_pantalla_con_resultante_a_media_altura`): tambien la resultante
        # del empuje TOTAL del suelo a h/2 (AASHTO C11.6.5.4), un diagrama
        # uniforme sobre h integrado por encima de la seccion; rige la mayor.
        h_s = datos_s["h"]
        encima = max(h_s - z, 0.0)
        peor = None
        for nombre, f_eh, f_inc, f_ir in casos:
            M_tierra = f_eh * M_EH + f_inc * M_dP
            posicion = "en su posicion"
            if regimen == REGIMEN_RESISTENCIA_K0 and h_s > 0:
                M_medios = ((f_eh * H_EH + f_inc * H_dP) * encima ** 2
                            / (2 * h_s))
                if M_medios > M_tierra:
                    M_tierra, posicion = M_medios, ("con la resultante del "
                                                    "empuje total a h/2 "
                                                    "(C11.6.5.4)")
            M_H = M_tierra + g_eq * M_LS + M_WA + f_ir * M_PIR
            e = (M_H - palanca) / W_v
            if peor is None or abs(e) > abs(peor[1]):
                peor = (nombre, e, M_H, f_eh, f_inc, f_ir, posicion)
        nombre, e, M_H, f_eh, f_inc, f_ir, posicion = peor
        limite = t / NUCLEO_CENTRAL_DIVISOR
        en_la_junta = codigo == "arranque" and con_junta
        # --- dictamen Fable de VE-6 --- el arranque bajo sismo DECIDE
        # siempre: sin junta y con la traccion admisible de E.060 no hay
        # contraste que lo cubra (E.060 9.2 no combina sismo con empuje), y
        # se atribuye al criterio de traccion del proyecto. --- VE-7 (lote
        # A, A3; triaje VE-7 de Fable) --- y la media altura tambien, por la
        # misma razon.
        decide = True
        salida.append(_verificacion_de_armado(
            fundamento="F9.CICLOPEO", codigo=f"C8.{codigo}.{ext}",
            que=f"C8, tracciones nulas en el {rotulo} bajo sismo: cabezal de "
                f"{entorno.extremo}"
                + (" (junta de construccion, E.060 22.4.7)" if en_la_junta
                   else ""),
            formula="e = [f_EH·M_EH + gamma_EQ·M_LS + M_WA + f_inc·M_dPAE + "
                    "f_IR·k_h·W·y_W - W·(1 - k_v)·(t/2 - x_W)] / "
                    "[W·(1 - k_v)] <= t/6, Evento "
                    "Extremo I sin factorar, el caso de AASHTO 11.6.5.1 que "
                    "mas excentrica"
                    + ("; con el muro que no cede, f_EH·M_EH + f_inc·M_dPAE "
                       "no baja del de la resultante del empuje total a h/2 "
                       "(C11.6.5.4)" if regimen == REGIMEN_RESISTENCIA_K0
                       else ""),
            sustitucion=(
                mag("t", t, "m", "espesor del cuerpo en la seccion"),
                mag("W", W, "kN/m", "peso del concreto por encima"),
                mag("x_W", x_W, "m", "de su centro de gravedad al trasdos"),
                mag("y_W", y_W, "m", "de su centro de gravedad a la seccion"),
                mag("k_h", datos_s["k_h"], "", "coeficiente sismico del "
                    "ensamble" + (" (1.0·k_h0, 11.6.5.4)" if k_h_armado
                                  is not None else ""), CIFRAS_FACTOR),
                mag("k_h·W·y_W", M_PIR, "kN·m/m", "inercia del cuerpo por "
                    "encima de la seccion, entera"),
                mag("k_v", k_v, "", f"criterio '{CRITERIO_K_V}': el peso que "
                    "estabiliza va con (1 - k_v), signo desfavorable",
                    CIFRAS_FACTOR),
                mag("M_EH", M_EH, "kN·m/m", "empuje estatico del suelo por "
                    "encima de la seccion"),
                mag("M_dPAE", M_dP, "kN·m/m", "incremento sismico del "
                    "empuje por encima de la seccion"),
                mag("gamma_EQ", g_eq, "", f"'{CRITERIO_GAMMA_EQ}' [A]: la "
                    "carga viva del Evento Extremo I, como en E2",
                    CIFRAS_FACTOR),
                mag("M_LS", M_LS, "kN·m/m", "sobrecarga viva por encima de "
                    "la seccion, sin factorar"),
                mag("M_WA", M_WA, "kN·m/m", "agua del relleno por encima de "
                    "la seccion, factor 1"),
            ),
            resultado=mag("e", abs(e), "m", "excentricidad de la resultante "
                          f"en la seccion: {nombre}, con f_EH = {f_eh:g}, "
                          f"f_inc = {f_inc:g} y f_IR = {f_ir:g}; empuje del "
                          f"suelo {posicion} (M_H = {M_H:.3f} kN·m/m)"),
            descripcion_umbral="e <= t/6 (tercio central)", admisible=limite,
            unidad="m",
            cita="E060.22.4.7#JUNTAS" if en_la_junta else "E060.22.6.3#TERCIO",
            caracter=None if en_la_junta else caracter_proyecto,
            aplicacion=("exigencia de E.060 22.4.7, por analogia: el "
                        "arranque es una junta de construccion "
                        f"('{CRITERIO_JUNTA_CICLOPEO}' = '{junta}'); decide "
                        "con cualquier criterio de traccion"
                        if en_la_junta else
                        "criterio del proyecto, mas exigente que la fuente "
                        f"('{CRITERIO_TRACCION_CICLOPEO}' [A])"
                        + ("; decide con cualquier criterio: bajo sismo "
                           "E.060 9.2 no da contraste que lo cubra"
                           if not nulas else "")),
            criterio=(CRITERIO_JUNTA_CICLOPEO if en_la_junta
                      else CRITERIO_TRACCION_CICLOPEO),
            cumple=abs(e) <= limite + TOL_UMBRAL_NORMATIVO,
            margen=limite - abs(e), decide=decide,
            obtenido=abs(e),
            nota=("Los dos casos de AASHTO 11.6.5.1 (100 % P_AE con 50 % "
                  "P_IR; 50 % P_AE, no menos que el estatico, con 100 % P_IR), "
                  "los de la fila E2, con las cargas sin factorar. La "
                  "componente vertical del empuje, que estabiliza, no se "
                  "cuenta. El peso que estabiliza va con (1 - k_v), el signo "
                  "desfavorable de la aceleracion vertical (con k_v = 0 no "
                  "cambia nada). Los dos casos son los de " + NUMERAL_P_IR
                  + "."),
            explicacion_falla=("bajo sismo la junta del arranque transmitiria "
                               "traccion, que E.060 22.4.7 prohibe: aumentar "
                               "el espesor del cuerpo" if en_la_junta else
                               "bajo sismo hay traccion en el trasdos del "
                               "cuerpo: aumentar su espesor"),
            citas=("MP.2.8.1.1.14.1#EXC", "AASHTO_LRFD_9.11.6.5.1#EXC"),
            numeral=NUMERAL_9_4_CICLOPEO))
    del con_k_v
    return salida, True, ""


def integrar_armado(cabezal: CabezalDelPunto,
                    armados: Sequence[ArmadoDelCabezal]) -> CabezalDelPunto:
    """
    El `CabezalDelPunto` con el armado de sus cabezales incorporado: las
    verificaciones A* / C* se suman a las CB y a las E (la via por la que
    `InformePunto` cuenta incumplidas e indicadores), los pasos y los avisos
    a los suyos, y los objetos enteros quedan en `armado`.
    """
    armados = tuple(armados)
    avisos = list(cabezal.avisos)
    for a in armados:
        avisos.extend(x for x in a.avisos if x not in avisos)
    return _reemplazar(
        cabezal,
        verificaciones=cabezal.verificaciones + tuple(
            v for a in armados for v in a.verificaciones),
        pasos=cabezal.pasos + tuple(p for a in armados for p in a.pasos),
        avisos=tuple(avisos), armado=armados)
