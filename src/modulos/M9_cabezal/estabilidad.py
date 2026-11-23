# -*- coding: utf-8 -*-
"""
M9_cabezal.estabilidad
======================
Submodulo de Fase 9 (`M9_cabezal`): bloque `estabilidad` (D1).
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

from src import criterios_adoptados as ca
from src.constantes_fisicas import GAMMA_AGUA_KN_M3
from src.constantes_normativas import (
    C_DESLIZAMIENTO_10_6_3_4,
    ETA_OTROS_ESTADOS_LIMITE_AASHTO,
    ETA_PISO_GAMMA_MAXIMO_AASHTO,
    ETA_TECHO_GAMMA_MINIMO_AASHTO,
    EXCENTRICIDAD_ESTATICA_FRACCION_B,
    FS_NOMBRE_DE_LA_CONDICION,
    FS_NUMERAL,
    NUMERAL_ETA_DUCTILIDAD_AASHTO,
    NUMERAL_ETA_REDUNDANCIA_AASHTO,
    NUMERAL_MODIFICADOR_DE_CARGA_AASHTO,
    NUMERAL_PHI_ESTABILIDAD_GLOBAL,
    NUMERAL_PHI_EVENTO_EXTREMO,
    NUMERAL_PHI_MUROS,
    NUMERAL_PHI_ZAPATAS,
    PHI_ESTABILIDAD_GLOBAL_11_6_3_7,
    PHI_EVENTO_EXTREMO_11_5_8,
    PHI_MUROS_T11_5_7_1,
    PHI_ZAPATAS_T10_5_5_2_2_1,
)
from src.modelos import (
    CIFRAS_FINA,
    CIFRAS_MAGNITUD,
    CabezalDelPunto,
    CargaDeCabezal,
    CombinacionDeEstabilidad,
    CondicionAnalisis,
    CriterioPendienteError,
    DatoFaltanteError,
    DatoInvalidoError,
    DisenoNoFactibleError,
    ELEMENTO_ALEROS,
    ELEMENTO_PANTALLA,
    ELEMENTO_ZAPATA,
    EntornoDelCabezal,
    ErrorProyecto,
    EstabilidadDelCabezal,
    MARCO_ASD,
    MARCO_LRFD,
    MURO_ALERO,
    MURO_CABEZAL,
    Magnitud,
    MetodoNoEvaluableError,
    PasoDeMemoria,
    SolicitacionDeElemento,
    TipoDeVeredicto,
    Umbral,
    Veredicto,
    Verificacion,
    paso,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

from src.modulos.M9_cabezal._criterios import (
    ABREVIATURA_DE_CONDICION,
    CITAS_DE_ETA,
    CONDICIONES_DE_ESTABILIDAD,
    CRITERIO_BRAZO_SISMICO,
    CRITERIO_FACTOR_MURO,
    CRITERIO_FORMA_PROFUNDIDAD,
    CRITERIO_GAMMA_EQ,
    CRITERIO_GAMMA_RELLENO,
    CRITERIO_K_V,
    CRITERIO_PHI_RELLENO,
    CRITERIO_TALUD_TERRAPLEN,
    EXTREMO_ENTRADA,
    FORMA_CORRIDA,
    FORMA_Y_PROFUNDIDAD,
    LADOS_DEL_TRIANGULO,
    OPCIONES_FORMA_PROFUNDIDAD,
    TERRENO_TALUD,
    _caracter_de,
    _exigir_finito,
    _finito,
    _rotular_como_alero,
    sufijo_de_la_franja,
)
from src.modulos.M9_cabezal.empujes import (
    _embocadura_paralela_del_cabezal,
    cimentacion_en_roca,
    envolvente_de_h_eq_paralelo,
)
from src.modulos.M9_cabezal.estabilidad_base import (
    DATO_TALUD_DELANTE_DEL_PUNTO,
    _terreno_delante,
    capacidad_portante_zapata_en_talud,
    excentricidad_admisible_sismica,
    fs_requerido,
    gamma_eq,
    parametros_resistencia_art20,
    presion_contacto_base,
)
from src.modulos.M9_cabezal.estabilidad_cargas import (
    AGUA_SE_MUEVE_CON_EL_SUELO,
    CITAS_K_V_EN_LOS_PESOS,
    CITA_NIVEL_MEDIO,
    CLAVE_FS_DE_CODIGO,
    CODIGOS_GLOBALES,
    CRITERIO_CARGA_PANTALLA,
    CRITERIO_DRENAJE,
    CRITERIO_EMPUJE_SISMICO_NO_CEDE,
    CRITERIO_ETA_DUCTILIDAD,
    CRITERIO_ETA_IMPORTANCIA,
    CRITERIO_ETA_REDUNDANCIA,
    CRITERIO_FILA_PHI,
    CRITERIO_FILA_PHI_GLOBAL,
    CRITERIO_INCLINACION_PORTANTE,
    CRITERIO_MARCO,
    CRITERIO_NIVEL_AGUA_SISMO,
    CRITERIO_REGIMEN,
    CRITERIO_REGLA_PENDIENTE,
    C_DC_PANTALLA,
    C_DC_ZAPATA,
    C_EH_H,
    C_EH_V,
    C_EQ_H,
    C_EQ_PIR_MURO,
    C_EQ_V,
    C_EV_TALON,
    C_LS_H,
    C_LS_V,
    C_WA_H,
    C_WA_U,
    DATO_EMPUJE_SISMICO,
    DATO_ESTABILIDAD_GLOBAL,
    DRENAJE_CON,
    DRENAJE_SIN,
    EMPUJE_ESTATICO_REPOSO,
    FILAS_DE_PHI,
    FILA_PHI_MUROS,
    INCLINACION_APLICAR,
    INCLINACION_OMITIR,
    METODO_EMPUJE_CUNA,
    METODO_INCREMENTO_CUNA,
    NIVEL_MEDIO_SUPERFICIE,
    NOTA_ARMADO_CON_EMPUJE_DECLARADO,
    NO_CEDE_MAYOR_DE_REPOSO_Y_TOTAL,
    NUMERAL_9_3_ASD,
    NUMERAL_9_3_LRFD,
    PANTALLA_CUNA,
    PANTALLA_PLANO_VIRTUAL,
    REGIMEN_CEDENTE,
    REGIMEN_NO_CEDENTE,
    _citas_del_empuje_declarado,
    _decide,
    _eleccion,
    _no_evaluable,
    _nota_del_empuje_declarado,
    _regla_de_marco,
    _sesgo,
    cargas_del_cabezal,
    combinaciones_de_estabilidad,
    cuna_de_tanteo,
    modificador_de_carga,
    resistencia_portante_nominal,
    suelo_de_fundacion,
)
from src.modulos.M9_cabezal.geometria import (
    _reglas,
    _texto_de_la_sobrecarga,
    avisos_de_la_sobrecarga_del_punto,
    extremos_del_conducto,
)

# ---------------------------------------------------------------------------
# Las verificaciones E1 a E3 de cada marco
# ---------------------------------------------------------------------------

def factores_de_resistencia(condicion: CondicionAnalisis,
                            cohesivo: bool,
                            fila: Optional[str] = None) -> dict:
    """
    Los factores de resistencia phi del marco LRFD para el portante y el
    deslizamiento del cabezal, con la tabla de la que sale cada uno.

    ESTATICA (estado limite de resistencia): la fila que declara
    'fila_phi_estabilidad_cabezal' [A]. «zapatas_seccion_10», Tabla
    10.5.5.2.2-1: portante 0.45 en suelo friccionante (metodo teorico en
    arena con SPT, la menor de las de suelo) o 0.50 en cohesivo; deslizamiento
    0.80 (vaciado in situ sobre arena) u 0.85 (sobre arcilla).
    «muros_tabla_11_5_7», Tabla 11.5.7-1: 0.55 y 1.0.

    SISMICA (Evento Extremo I): sin eleccion. El Art. 11.5.8 fija 1.0 «unless
    otherwise specified» y especifica 0.8 para el portante de los muros de
    gravedad y semigravedad: NO es «phi = 1.0» a secas.
    """
    if condicion is CondicionAnalisis.SISMICO:
        return {"portante": PHI_EVENTO_EXTREMO_11_5_8[
                    "portante_gravedad_y_semigravedad"],
                "deslizamiento": PHI_EVENTO_EXTREMO_11_5_8["general"],
                "fuente": NUMERAL_PHI_EVENTO_EXTREMO, "criterio": None,
                "cita": "AASHTO_LRFD_9.11.5.8#PORTANTE"}
    if fila is None:
        fila = ca.valor(CRITERIO_FILA_PHI)
    if fila not in FILAS_DE_PHI:
        raise DatoInvalidoError(CRITERIO_FILA_PHI, valor=fila,
                                motivo="se espera una de: "
                                       + ", ".join(FILAS_DE_PHI))
    if fila == FILA_PHI_MUROS:
        return {"portante": PHI_MUROS_T11_5_7_1[
                    "portante_gravedad_y_semigravedad"],
                "deslizamiento": PHI_MUROS_T11_5_7_1["deslizamiento"],
                "fuente": NUMERAL_PHI_MUROS, "criterio": CRITERIO_FILA_PHI,
                "cita": "AASHTO_LRFD_9.11.5.7#MUROS"}
    t = PHI_ZAPATAS_T10_5_5_2_2_1
    return {"portante": (t["portante"]["teorico_arcilla"] if cohesivo
                         else t["portante"]["teorico_arena_spt"]),
            "deslizamiento": (t["deslizamiento"]["concreto_sobre_arcilla"]
                              if cohesivo else
                              t["deslizamiento"]["vaciado_in_situ_sobre_arena"]),
            "fuente": NUMERAL_PHI_ZAPATAS, "criterio": CRITERIO_FILA_PHI,
            "cita": "AASHTO_LRFD_9.10.5.5.2.2#T1"}


def _empotramiento_delante(entorno: EntornoDelCabezal, datos: dict
                           ) -> Tuple[float, float, str]:
    """
    (D_f, D_w, texto): el empotramiento que cuenta como sobrecarga DELANTE
    de la zapata y la profundidad del freatico bajo ese terreno. Con hoya de
    socavacion a la salida solo cuenta lo que queda bajo su fondo (AASHTO
    11.6.3.5 y 10.6.1.2); sin ella, la profundidad de desplante.
    """
    desplante = entorno.geometria.cota_desplante
    if entorno.cota_fondo_hoya is not None:
        terreno = min(entorno.cota_fondo_hoya, entorno.cota_pie)
        texto = ("empotramiento bajo el fondo de la hoya de socavacion de la "
                 "Fase 6")
    else:
        terreno = entorno.cota_pie
        texto = "profundidad de desplante bajo el terreno del pie"
    D_f = max(terreno - desplante, 0.0)
    # El freatico es una COTA (H1): su profundidad bajo ESE terreno.
    D_w = max(terreno - datos["cota_freatico"], 0.0)
    return D_f, D_w, texto


def _q_nominal(entorno: EntornoDelCabezal, datos: dict, suelo: dict,
               B_efectivo: float, servicio: CombinacionDeEstabilidad,
               inclinacion: Optional[str] = None
               ) -> Tuple[float, str, dict]:
    """
    La resistencia portante NOMINAL para una combinacion: la del EMS si el
    suelo trae `q_n_kpa` (gana), o la de la ecuacion de AASHTO 10.6.3.1.2a
    con el ancho efectivo. En roca, o con terreno que desciende delante de
    la zapata, la ecuacion no aplica.
    """
    if "q_n_kpa" in suelo:
        return suelo["q_n_kpa"], ("resistencia portante nominal del EMS "
                                  "(`q_n_kpa`): gana sobre la calculada"), {}
    if cimentacion_en_roca():
        raise _no_evaluable(
            f"capacidad portante del cabezal de {entorno.extremo}",
            "resistencia portante en roca (AASHTO 10.6.3.2)",
            "las filas de sitio declaradas en 'F_pga' son de roca y la "
            "ecuacion de capacidad de carga de 10.6.3.1.2a es de suelo; hace "
            "falta la resistencia nominal del EMS (`q_n_kpa`)",
            entorno.id_punto)
    # --- dictamen Fable (VE-7 lote A, (iii)) --- el terreno de delante:
    # el del punto gana (talud o «horizontal»), si no el de corredor.
    terreno, talud, origen_terreno = _terreno_delante(entorno)
    D_f, D_w, texto = _empotramiento_delante(entorno, datos)
    if inclinacion is None:
        inclinacion = ca.valor(CRITERIO_INCLINACION_PORTANTE)
    if inclinacion not in (INCLINACION_APLICAR, INCLINACION_OMITIR):
        raise DatoInvalidoError(CRITERIO_INCLINACION_PORTANTE,
                                valor=inclinacion,
                                motivo="se espera 'aplicar' u 'omitir'")
    # --- VE-5 (ficha T7B-04) --- forma y profundidad, declarables.
    forma = _eleccion(CRITERIO_FORMA_PROFUNDIDAD, OPCIONES_FORMA_PROFUNDIDAD)
    longitud = None
    if forma != FORMA_CORRIDA:
        longitud = entorno.geometria.longitud
        if longitud is None:
            raise DatoFaltanteError(
                "longitud", id_punto=entorno.id_punto,
                detalle=f"'{CRITERIO_FORMA_PROFUNDIDAD}' = '{forma}' pide la "
                        "longitud de la zapata del cabezal (L de la Tabla "
                        "10.6.3.1.2a-3), que la geometria no trae")
    profundidad = forma == FORMA_Y_PROFUNDIDAD
    # --- VE-7 (abierto (b)) --- una L infinita es la lectura de ZAPATA
    # CORRIDA de la franja del alero (`estabilidad_del_alero` la contrasta
    # con la del alero corto): s = 1, y d_q si se declaro.
    corrida_del_alero = longitud is not None and math.isinf(longitud)
    if corrida_del_alero:
        longitud = None
    texto_forma = ("zapata corrida, s = d_q = 1" if forma == FORMA_CORRIDA
                   else ("zapata corrida (L infinita), s = 1"
                         if corrida_del_alero
                         else f"factores de forma con L = {longitud:.3f} m")
                   + (" y d_q (ec. 10.6.3.1.2a-10)" if profundidad else ""))
    if terreno == TERRENO_TALUD:
        # --- VE-5 (ficha T7B-04) --- la RC_BC de AASHTO 10.6.3.1.2c sobre
        # la geometria del talud ('talud_delante_del_cabezal' [S]): hasta
        # VE-5 pedia los factores de los abacos de Meyerhof del Manual de
        # Puentes (retirados) y les pasaba H_s = 0.
        # --- VE-7 (lote A, A6; ficha VE5M9-03) --- la del PUNTO gana a la
        # de corredor ('talud_delante_del_cabezal_del_punto').
        del_punto = origen_terreno == "del punto"
        D_w_base = max(D_w - D_f, 0.0)
        q_0, det0 = resistencia_portante_nominal(
            suelo=suelo, B_efectivo=B_efectivo, D_f=0.0, D_w=D_w_base,
            H_servicio=servicio.H, V_servicio=servicio.N,
            aplicar_inclinacion=inclinacion == INCLINACION_APLICAR,
            longitud=longitud)
        c_art20, phi_art20 = parametros_resistencia_art20(
            c=suelo["c_kpa"], phi_grados=suelo["phi_grados"],
            cohesivo=suelo["cohesivo"])
        q, detalle = capacidad_portante_zapata_en_talud(
            B=B_efectivo, H_s=talud["H_s_m"], b=talud["b_m"],
            beta_grados=talud["beta_grados"], gamma=suelo["gamma_kn_m3"],
            c=c_art20, phi_grados=phi_art20, C_wgamma=det0["C_wgamma"],
            i_c=det0["i_c"], i_gamma=det0["i_gamma"], s_c=det0["s_c"],
            s_gamma=det0["s_gamma"], id_punto=entorno.id_punto)
        detalle.update(talud, inclinacion=inclinacion, forma=forma,
                       D_f=0.0, D_w=D_w_base, texto_D_f=texto)
        return q, (f"zapata {'en el' if talud['b_m'] <= 0 else 'junto al'} "
                   f"talud (AASHTO 10.6.3.1.2c): RC_BC = "
                   f"{detalle['RC_BC']:.4f} de la Tabla {detalle['tabla']} "
                   f"({detalle['columna']}, B/H_s = {detalle['B_H']:.3f}, "
                   f"beta = {talud['beta_grados']:g} grados"
                   + (f"; terreno delante: del punto, "
                      f"'{DATO_TALUD_DELANTE_DEL_PUNTO}'"
                      if del_punto else "") + ") sobre c·N_cm + "
                   "0.5·gamma·B'·N_gamma_m, sin empotramiento; "
                   + texto_forma), detalle
    q_n, detalle = resistencia_portante_nominal(
        suelo=suelo, B_efectivo=B_efectivo, D_f=D_f, D_w=D_w,
        H_servicio=servicio.H, V_servicio=servicio.N,
        aplicar_inclinacion=inclinacion == INCLINACION_APLICAR,
        longitud=longitud, profundidad=profundidad)
    detalle.update(D_f=D_f, D_w=D_w, texto_D_f=texto, inclinacion=inclinacion,
                   forma=forma)
    return q_n, ("ecuacion de AASHTO 10.6.3.1.2a con B' = B - 2e, "
                 f"D_f = {D_f:.3f} m ({texto}), factores de inclinacion "
                 f"'{inclinacion}' y {texto_forma}; terreno delante: "
                 f"{origen_terreno}"), detalle


def _resistencia_al_deslizamiento(suelo: dict, combo: CombinacionDeEstabilidad
                                  ) -> Tuple[float, str]:
    """
    R_tau, resistencia NOMINAL al deslizamiento por metro de muro, kN/m
    (AASHTO 10.6.3.4; E.050 Art. 20 para la regla de c y phi).

    Suelo friccionante: R_tau = C·V·tan(phi_f), con C = 1.0 de la zapata
    vaciada contra el suelo (ec. 10.6.3.4-2). Suelo cohesivo: la menor de la
    cohesion y la mitad del esfuerzo normal sobre el ancho efectivo, que es
    lo que la fuente admite cuando la zapata descansa sobre al menos 6.0 in
    de material granular compactado -- una condicion constructiva que el
    paso declara --.
    """
    if not suelo["cohesivo"]:
        C = C_DESLIZAMIENTO_10_6_3_4["vaciado_contra_el_suelo"]
        return (C * combo.N * math.tan(math.radians(suelo["phi_grados"])),
                f"C·V·tan(phi_f) = {C:g}·{combo.N:.3f}·tan("
                f"{suelo['phi_grados']:g}°)")
    e = abs(combo.excentricidad)
    B_ef = max(combo.B - 2 * e, 0.0)
    sigma = combo.N / B_ef if B_ef > 0 else 0.0
    q_s = min(suelo["c_kpa"], sigma / 2)
    return (q_s * B_ef,
            f"min(c, sigma_v/2)·B' = min({suelo['c_kpa']:g}, "
            f"{sigma / 2:.3f})·{B_ef:.3f} (sobre >= 6.0 in de material "
            "granular compactado)")


def _combo(combos, marco, para, peor) -> CombinacionDeEstabilidad:
    """La combinacion de ese marco y uso que da el peor efecto `peor(c)`."""
    candidatas = [c for c in combos if c.marco == marco and c.para == para]
    return max(candidatas, key=peor)


def _resultado_de_verificacion(*, fundamento: str, codigo: str, que: str,
                               formula: str, sustitucion: tuple,
                               resultado: Magnitud, descripcion_umbral: str,
                               admisible, unidad: str, cita: str,
                               aplicacion: str, criterio: Optional[str],
                               cumple: bool, margen: Optional[float],
                               decide: bool, numeral: str, obtenido,
                               nota: str, explicacion_falla: str,
                               citas: Tuple[str, ...] = ()) -> Verificacion:
    """
    Arma la `Verificacion` y su paso. Si el marco NO decide ('marco_
    estabilidad_cabezal'), un incumplimiento sale como INDICADOR: se imprime
    y se avisa, y no detiene el punto.
    """
    if cumple:
        tipo, texto = TipoDeVeredicto.CUMPLE, "cumple"
    elif decide:
        tipo, texto = TipoDeVeredicto.NO_CUMPLE, explicacion_falla
    else:
        tipo, texto = TipoDeVeredicto.INDICADOR, (
            explicacion_falla + ". Este marco NO rige "
            f"('{CRITERIO_MARCO}' [A]): se informa y no detiene el punto")
    kw = dict(codigo=codigo, que=que, formula=formula,
              sustitucion=sustitucion, resultado=resultado,
              citas_textuales=(cita,) + tuple(citas),
              umbral=Umbral(descripcion=descripcion_umbral, valor=admisible,
                            unidad=unidad, cita_id=cita,
                            caracter=_caracter_de(cita),
                            aplicacion=aplicacion,
                            criterio_aplicado=criterio),
              veredicto=Veredicto(tipo=tipo, margen=margen, unidad=unidad,
                                  explicacion=texto),
              nota_del_proyecto=nota)
    # El fundamento va LITERAL en cada rama (el indice de formulas localiza
    # al emisor por el literal).
    if fundamento == "F9.E1_LRFD":
        p = paso("F9.E1_LRFD", **kw)
    elif fundamento == "F9.E2_LRFD":
        p = paso("F9.E2_LRFD", **kw)
    elif fundamento == "F9.E3_LRFD":
        p = paso("F9.E3_LRFD", **kw)
    else:
        p = paso("F9.E_ASD", **kw)
    return Verificacion(
        cumple=tipo is not TipoDeVeredicto.NO_CUMPLE, numeral=numeral,
        valor_obtenido=obtenido, valor_admisible=admisible,
        criterio_aplicado=criterio or CRITERIO_MARCO, codigo=codigo, paso=p)


def _m(simbolo: str, valor, unidad: str, procedencia: str) -> Magnitud:
    return Magnitud(simbolo, valor, unidad, procedencia,
                    cifras=CIFRAS_MAGNITUD)


def _verificaciones_lrfd(entorno, datos, suelo, combos, condicion, decide,
                         sufijo, fila: Optional[str] = None,
                         inclinacion: Optional[str] = None
                         ) -> List[Verificacion]:
    """
    E1 a E3 del marco LRFD. `fila` e `inclinacion` sustituyen, SOLO para el
    contraste de sensibilidad del ensamble (`_avisos_de_sensibilidad`), las
    dos elecciones [A] de la ventana que mueven el veredicto: la fila de
    phi y los factores de inclinacion. Sin ellas valen las declaradas.
    """
    g = entorno.geometria
    B = g.B
    ext = entorno.extremo
    phis = factores_de_resistencia(condicion, suelo["cohesivo"], fila=fila)
    en_roca = cimentacion_en_roca()
    nota_marco = ("Marco LRFD (AASHTO LRFD 11.6): cargas factoradas contra "
                  "resistencias minoradas. El cabezal se MODELA como muro de "
                  "semigravedad en voladizo: es hipotesis del proyecto "
                  f"('{CRITERIO_MARCO}' [A]), no mandato de la fuente.")
    salida = []

    # --- E2: excentricidad (reemplaza al volteo) ---------------------------
    c2 = _combo(combos, MARCO_LRFD, "excentricidad y deslizamiento",
                lambda c: (abs(c.excentricidad) if c.N > 0 else math.inf))
    _exigir_compresion(c2, entorno)
    # En valor absoluto: la resultante tiene que quedar dentro de la franja
    # central hacia los DOS lados (con mucho peso sobre el talon cae del
    # lado del relleno, y el limite es el mismo).
    e = abs(c2.excentricidad)
    if condicion is CondicionAnalisis.SISMICO:
        g_eq = gamma_eq()
        e_max = excentricidad_admisible_sismica(B=B, gamma_EQ=g_eq)
        cita_e = "AASHTO_LRFD_9.11.6.5.1#EXC"
        desc_e = (f"limite sismico con gamma_EQ = {g_eq:g}: de los dos "
                  "tercios centrales (gamma_EQ = 0) a las ocho decimas "
                  "(gamma_EQ = 1)")
        criterio_e = CRITERIO_GAMMA_EQ
    else:
        clave = "roca" if en_roca else "suelo"
        e_max = EXCENTRICIDAD_ESTATICA_FRACCION_B[clave] * B
        cita_e = "AASHTO_LRFD_9.11.6.3.3#EXC"
        desc_e = ("resultante dentro de los dos tercios centrales de la "
                  "base, e <= B/3 (fundacion en suelo)" if not en_roca else
                  "resultante dentro de los nueve decimos centrales, e <= "
                  "0.45·B (fundacion en roca)")
        criterio_e = None
    cumple_e = e <= e_max + TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E2_LRFD", codigo=f"E2-LRFD.{sufijo}",
        que=f"E2 (LRFD), excentricidad de la resultante: cabezal de {ext}, "
            f"condicion {condicion.value}",
        formula="e = B/2 - (M_estabilizante - M_volcante) / N  <=  e_max",
        sustitucion=(
            _m("N", c2.N, "kN/m", f"suma vertical factorada, «{c2.nombre}»"),
            _m("M_estabilizante", c2.M_estabilizante, "kN·m/m",
               "momentos factorados que estabilizan, respecto de la punta"),
            _m("M_volcante", c2.M_volcante, "kN·m/m",
               "momentos factorados que vuelcan, respecto de la punta"),
            _m("B", B, "m", "ancho de la zapata")),
        resultado=_m("e", e, "m", "excentricidad respecto del centro de la "
                     "base, en valor absoluto ("
                     + ("hacia la punta" if c2.excentricidad >= 0
                        else "hacia el talon") + ")"),
        descripcion_umbral=desc_e, admisible=e_max, unidad="m", cita=cita_e,
        aplicacion="EXIGENCIA de la fuente para muros, aplicada al cabezal "
                   "por la hipotesis de modelacion",
        criterio=criterio_e, cumple=cumple_e, margen=e_max - e, decide=decide,
        numeral=NUMERAL_9_3_LRFD + f", cabezal de {ext}", obtenido=e,
        nota=nota_marco + " En este marco NO hay factor de seguridad al "
             "volteo: lo reemplaza esta excentricidad (C11.6.3.3).",
        explicacion_falla="la resultante factorada cae fuera del limite: la "
                          "base se despega en exceso; ampliar la zapata o "
                          "el talon",
        citas=("AASHTO_LRFD_9.C11.6.3.3#REEMPLAZA",)))

    # --- E3: deslizamiento ---------------------------------------------------
    c3 = _combo(combos, MARCO_LRFD, "excentricidad y deslizamiento",
                lambda c: c.H - phis["deslizamiento"]
                * _resistencia_al_deslizamiento(suelo, c)[0])
    R_tau, texto_R = _resistencia_al_deslizamiento(suelo, c3)
    R_R = phis["deslizamiento"] * R_tau
    cumple_d = c3.H <= R_R + TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E3_LRFD", codigo=f"E3-LRFD.{sufijo}",
        que=f"E3 (LRFD), deslizamiento: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula="H_u  <=  phi_tau · R_tau,  R_tau = C·V·tan(phi_f)",
        sustitucion=(
            _m("N", c3.N, "kN/m", f"suma vertical factorada, «{c3.nombre}»"),
            _m("R_tau", R_tau, "kN/m", texto_R),
            _m("phi_tau", phis["deslizamiento"], "-", phis["fuente"])),
        resultado=_m("H_u", c3.H, "kN/m", "suma horizontal factorada de la "
                     "misma combinacion"),
        descripcion_umbral="resistencia factorada al deslizamiento, "
                           "phi_tau·R_tau, sin empuje pasivo",
        admisible=R_R, unidad="kN/m",
        cita="AASHTO_LRFD_9.10.6.3.4#RESISTENCIA",
        aplicacion="EXIGENCIA de la fuente para zapatas y muros, aplicada "
                   "al cabezal por la hipotesis de modelacion",
        criterio=phis["criterio"], cumple=cumple_d, margen=R_R - c3.H,
        decide=decide, numeral=NUMERAL_9_3_LRFD + f", cabezal de {ext}",
        obtenido=c3.H,
        nota=nota_marco + " Empuje pasivo delante de la zapata: no se "
             "cuenta (AASHTO 11.6.3.5).",
        explicacion_falla="el empuje factorado supera la resistencia "
                          "factorada al deslizamiento; ampliar la zapata o "
                          "añadir un dentellon de corte",
        citas=("AASHTO_LRFD_9.11.6.3.6#DESLIZAMIENTO",
               "AASHTO_LRFD_9.11.6.3.5#PASIVA", phis["cita"])))

    # --- E1: capacidad portante ---------------------------------------------
    peor = None
    for c in (x for x in combos if x.marco == MARCO_LRFD):
        _exigir_compresion(c, entorno)
        e1 = abs(c.excentricidad)
        if e1 >= B / 2 - TOL_UMBRAL_NORMATIVO:
            peor = (math.inf, c, None, None, None, "", {})
            break
        servicio = _servicio_de(combos, c)
        presion = presion_contacto_base(N=c.N, momento_neto=c.N * e1, B=B,
                                        cimentacion_en_roca=en_roca)
        q_n, origen_q, det = _q_nominal(entorno, datos, suelo,
                                        presion.ancho_efectivo, servicio,
                                        inclinacion=inclinacion)
        q_R = phis["portante"] * q_n
        uso = presion.q_max / q_R if q_R > 0 else math.inf
        if peor is None or uso > peor[0]:
            peor = (uso, c, presion, q_n, q_R, origen_q, det)
    uso, c1, presion, q_n, q_R, origen_q, det = peor
    if presion is None:
        salida.append(_resultado_de_verificacion(
            fundamento="F9.E1_LRFD", codigo=f"E1-LRFD.{sufijo}",
            que=f"E1 (LRFD), capacidad portante: cabezal de {ext}, "
                f"condicion {condicion.value}",
            formula="sigma_v = N / (B - 2e)  <=  phi_b · q_n",
            sustitucion=(_m("N", c1.N, "kN/m", f"«{c1.nombre}»"),
                         _m("e", c1.excentricidad, "m", "excentricidad")),
            resultado=Magnitud("sigma_v", "no existe", "kPa",
                               "la resultante cae fuera de la zapata (e >= "
                               "B/2): no hay ancho efectivo"),
            descripcion_umbral="resistencia portante factorada",
            admisible=None, unidad="kPa",
            cita="AASHTO_LRFD_9.11.6.3.2#PORTANTE",
            aplicacion="EXIGENCIA de la fuente para muros",
            criterio=phis["criterio"], cumple=False, margen=None,
            decide=decide, numeral=NUMERAL_9_3_LRFD + f", cabezal de {ext}",
            obtenido=None, nota=nota_marco,
            explicacion_falla="la resultante factorada cae fuera de la "
                              "zapata: no hay presion de contacto que "
                              "equilibre el muro"))
        return salida
    cumple_q = presion.q_max <= q_R + TOL_UMBRAL_NORMATIVO
    sust = [_m("N", c1.N, "kN/m", f"suma vertical factorada, «{c1.nombre}»"),
            _m("e", abs(c1.excentricidad), "m", "excentricidad de esa "
               "combinacion"),
            _m("B'", presion.ancho_efectivo, "m", "ancho efectivo B - 2e"),
            _m("q_n", q_n, "kPa", origen_q),
            _m("phi_b", phis["portante"], "-", phis["fuente"])]
    for k in ("N_c", "N_q", "N_gamma", "i_q", "i_gamma", "C_wq", "C_wgamma"):
        if k in det:
            sust.append(_m(k, det[k], "-", "AASHTO 10.6.3.1.2a (Tablas "
                           "10.6.3.1.2a-1 y -2; ecs. -5 a -9)"))
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E1_LRFD", codigo=f"E1-LRFD.{sufijo}",
        que=f"E1 (LRFD), capacidad portante: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula=("sigma_v = N / (B - 2e)  <=  phi_b · q_n;  q_n = c·N_c·i_c "
                 "+ gamma·D_f·N_q·i_q·C_wq + 0.5·gamma·B'·N_gamma·i_gamma·"
                 "C_wgamma"),
        sustitucion=tuple(sust),
        resultado=_m("sigma_v", presion.q_max, "kPa", presion.distribucion),
        descripcion_umbral="resistencia portante factorada, phi_b·q_n",
        admisible=q_R, unidad="kPa", cita="AASHTO_LRFD_9.11.6.3.2#PORTANTE",
        aplicacion="EXIGENCIA de la fuente para muros, aplicada al cabezal "
                   "por la hipotesis de modelacion",
        criterio=phis["criterio"], cumple=cumple_q,
        margen=q_R - presion.q_max, decide=decide,
        numeral=NUMERAL_9_3_LRFD + f", cabezal de {ext}",
        obtenido=presion.q_max,
        nota=nota_marco + " Zapata tratada como corrida (factores de forma "
             "1) y sin factor de profundidad (d_q = 1). Entre filas de las "
             "Tablas 10.6.3.1.2a-1 y -2 se interpola linealmente (lectura "
             "del proyecto). Se imprime la combinacion de mayor "
             "aprovechamiento entre las del marco.",
        explicacion_falla="la presion factorada supera la resistencia "
                          "portante factorada; ampliar la zapata",
        citas=("AASHTO_LRFD_9.10.6.3.1.2a#QN", phis["cita"])))
    return salida


def _exigir_compresion(c: CombinacionDeEstabilidad,
                       entorno: EntornoDelCabezal) -> None:
    """Con N <= 0 no hay base comprimida: el problema es de flotacion."""
    if not c.N > 0:
        raise DisenoNoFactibleError(
            motivo=f"cabezal de {entorno.extremo} de {entorno.id_punto}: en "
                   f"la combinacion «{c.nombre}» la suma vertical no es de "
                   f"compresion (N = {c.N:.3f} kN/m): la subpresion iguala "
                   "o supera al peso. No es un problema de estabilidad sino "
                   "de flotacion del muro: hace falta mas peso o drenaje")


def _servicio_de(combos, c: CombinacionDeEstabilidad
                 ) -> CombinacionDeEstabilidad:
    """
    La combinacion de SERVICIO (marco ASD) hermana de una LRFD: sus cargas
    sin factorar son las que la fuente pide para los factores de inclinacion
    de la capacidad portante («unfactored»).
    """
    if c.condicion is CondicionAnalisis.ESTATICO:
        return next(x for x in combos if x.marco == MARCO_ASD
                    and x.para == "portante")
    caso = c.nombre.replace("Evento Extremo I, ", "").replace(
        " (portante)", "")
    return next(x for x in combos if x.marco == MARCO_ASD
                and x.para == "portante" and caso in x.nombre)


def _verificaciones_asd(entorno, datos, suelo, combos, condicion, decide,
                        sufijo, inclinacion: Optional[str] = None
                        ) -> List[Verificacion]:
    g = entorno.geometria
    B = g.B
    ext = entorno.extremo
    en_roca = cimentacion_en_roca()
    nota_marco = ("Marco ASD (E.050, norma de edificaciones, aplicada al "
                  "cabezal POR ANALOGIA, [N→]): TODAS las cargas de "
                  "servicio, con factor 1 (Art. 17.1), contra la "
                  "resistencia nominal dividida por el factor de seguridad. "
                  "Ningun factor de carga ni de resistencia del otro marco "
                  "entra aqui.")
    aplic = ("EXIGENCIA de E.050 para edificaciones; el proyecto la aplica "
             "al cabezal por analogia")
    salida = []

    # --- E2: volteo ----------------------------------------------------------
    c2 = _combo(combos, MARCO_ASD, "volteo y deslizamiento",
                lambda c: (c.M_volcante / c.M_estabilizante
                           if c.M_estabilizante > 0 else math.inf))
    fs_v_req = fs_requerido(verificacion="volteo", condicion=condicion)
    fs_v = (c2.M_estabilizante / c2.M_volcante
            if c2.M_volcante > TOL_UMBRAL_NORMATIVO else None)
    cumple_v = fs_v is None or fs_v >= fs_v_req - TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E_ASD", codigo=f"E2-ASD.{sufijo}",
        que=f"E2 (ASD), volteo: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula="FS = M_estabilizante / M_volcante  >=  FS minimo",
        sustitucion=(
            _m("M_estabilizante", c2.M_estabilizante, "kN·m/m",
               f"momentos de servicio que estabilizan, «{c2.nombre}»"),
            _m("M_volcante", c2.M_volcante, "kN·m/m",
               "momentos de servicio que vuelcan (empujes, inercia y "
               "subpresion)")),
        resultado=(_m("FS", fs_v, "-", "cociente de momentos respecto de "
                      "la punta") if fs_v is not None else
                   Magnitud("FS", "sin momento volcante", "-",
                            "no hay nada que vuelque el muro")),
        descripcion_umbral="factor de seguridad minimo al volteo",
        admisible=fs_v_req, unidad="-", cita="E050.39.13.6",
        aplicacion=aplic, criterio=None, cumple=cumple_v,
        margen=None if fs_v is None else fs_v - fs_v_req, decide=decide,
        numeral=NUMERAL_9_3_ASD + f", cabezal de {ext}", obtenido=fs_v,
        nota=nota_marco,
        explicacion_falla="el factor de seguridad al volteo no alcanza el "
                          "minimo de E.050",
        citas=("E050.17.1#SERVICIO",)))

    # --- E3: deslizamiento ---------------------------------------------------
    def _f_res(c):
        if suelo["cohesivo"]:
            return suelo["c_kpa"] * c.B
        return c.N * math.tan(math.radians(suelo["phi_grados"]))
    c3 = _combo(combos, MARCO_ASD, "volteo y deslizamiento",
                lambda c: (c.H / _f_res(c) if _f_res(c) > 0 else math.inf))
    _exigir_compresion(c3, entorno)
    f_res = _f_res(c3)
    fs_d_req = fs_requerido(verificacion="deslizamiento", condicion=condicion)
    fs_d = f_res / c3.H if c3.H > TOL_UMBRAL_NORMATIVO else None
    cumple_d = fs_d is None or fs_d >= fs_d_req - TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E_ASD", codigo=f"E3-ASD.{sufijo}",
        que=f"E3 (ASD), deslizamiento: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula=("FS = F_resistente / F_actuante  >=  FS minimo;  "
                 "F_resistente = N·tan(phi) (friccionante) o c·B (cohesivo)"),
        sustitucion=(
            _m("N", c3.N, "kN/m", f"suma vertical de servicio, «{c3.nombre}»"),
            _m("F_resistente", f_res, "kN/m",
               ("c·B, suelo cohesivo con phi = 0" if suelo["cohesivo"] else
                f"N·tan({suelo['phi_grados']:g}°), suelo friccionante con "
                "c = 0") + " (E.050 Art. 20)"),
            _m("F_actuante", c3.H, "kN/m", "suma horizontal de servicio")),
        resultado=(_m("FS", fs_d, "-", "cociente de fuerzas")
                   if fs_d is not None else
                   Magnitud("FS", "sin fuerza actuante", "-", "no hay empuje "
                            "horizontal")),
        descripcion_umbral="factor de seguridad minimo al deslizamiento",
        admisible=fs_d_req, unidad="-", cita="E050.39.13.6", aplicacion=aplic,
        criterio=None, cumple=cumple_d,
        margen=None if fs_d is None else fs_d - fs_d_req, decide=decide,
        numeral=NUMERAL_9_3_ASD + f", cabezal de {ext}", obtenido=fs_d,
        nota=nota_marco + " Sin empuje pasivo delante de la zapata.",
        explicacion_falla="el factor de seguridad al deslizamiento no "
                          "alcanza el minimo de E.050",
        citas=("E050.20", "E050.17.1#SERVICIO")))

    # --- E1: capacidad portante ---------------------------------------------
    fs_q_req = fs_requerido(verificacion="capacidad_portante",
                            condicion=condicion)
    peor = None
    for c in (x for x in combos if x.marco == MARCO_ASD
              and x.para == "portante"):
        _exigir_compresion(c, entorno)
        e1 = abs(c.excentricidad)
        if e1 >= B / 2 - TOL_UMBRAL_NORMATIVO:
            peor = (math.inf, c, None, None, "")
            break
        presion = presion_contacto_base(N=c.N, momento_neto=c.N * e1, B=B,
                                        cimentacion_en_roca=en_roca)
        if "q_adm_kpa" in suelo:
            q_adm, origen = suelo["q_adm_kpa"], (
                "presion admisible del EMS (`q_adm_kpa`): gana, y se usa "
                "sin aumento tambien con sismo")
        else:
            q_n, origen_q, _det = _q_nominal(entorno, datos, suelo,
                                             presion.ancho_efectivo, c,
                                             inclinacion=inclinacion)
            q_adm = q_n / fs_q_req
            origen = f"q_n / FS = {q_n:.3f} / {fs_q_req:g}; q_n: {origen_q}"
        uso = presion.q_max / q_adm if q_adm > 0 else math.inf
        if peor is None or uso > peor[0]:
            peor = (uso, c, presion, q_adm, origen)
    uso, c1, presion, q_adm, origen = peor
    if presion is None:
        salida.append(_resultado_de_verificacion(
            fundamento="F9.E_ASD", codigo=f"E1-ASD.{sufijo}",
            que=f"E1 (ASD), capacidad portante: cabezal de {ext}, "
                f"condicion {condicion.value}",
            formula="q_servicio = N / (B - 2e)  <=  q_admisible",
            sustitucion=(_m("N", c1.N, "kN/m", f"«{c1.nombre}»"),
                         _m("e", c1.excentricidad, "m", "excentricidad")),
            resultado=Magnitud("q_servicio", "no existe", "kPa",
                               "la resultante de servicio cae fuera de la "
                               "zapata (e >= B/2)"),
            descripcion_umbral="presion admisible",
            admisible=None, unidad="kPa", cita="E050.21", aplicacion=aplic,
            criterio=None, cumple=False, margen=None, decide=decide,
            numeral=NUMERAL_9_3_ASD + f", cabezal de {ext}", obtenido=None,
            nota=nota_marco,
            explicacion_falla="la resultante de servicio cae fuera de la "
                              "zapata"))
        return salida
    cumple_q = presion.q_max <= q_adm + TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E_ASD", codigo=f"E1-ASD.{sufijo}",
        que=f"E1 (ASD), capacidad portante: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula="q_servicio = N / (B - 2e)  <=  q_admisible = q_n / FS",
        sustitucion=(
            _m("N", c1.N, "kN/m", f"suma vertical de servicio, «{c1.nombre}»"),
            _m("e", abs(c1.excentricidad), "m", "excentricidad de servicio"),
            _m("B'", presion.ancho_efectivo, "m", "ancho efectivo B - 2e"),
            _m("FS", fs_q_req, "-", "E.050 Art. 21 ("
               + ("21.1, cargas estaticas"
                  if condicion is CondicionAnalisis.ESTATICO
                  else "21.2, solicitacion maxima de sismo") + ")")),
        resultado=_m("q_servicio", presion.q_max, "kPa", presion.distribucion),
        descripcion_umbral="presion admisible del terreno (" + origen + ")",
        admisible=q_adm, unidad="kPa", cita="E050.21", aplicacion=aplic,
        criterio=None, cumple=cumple_q, margen=q_adm - presion.q_max,
        decide=decide, numeral=NUMERAL_9_3_ASD + f", cabezal de {ext}",
        obtenido=presion.q_max,
        nota=nota_marco + " La excentricidad de servicio se usa solo para "
             "el ancho efectivo: su limite de B/6 no es exigencia de E.050 "
             "y B/3 es del otro marco.",
        explicacion_falla="la presion de servicio supera la admisible",
        citas=("E050.17.1#SERVICIO",)))
    return salida


# ---------------------------------------------------------------------------
# Las solicitaciones factoradas por elemento: la interfaz para T-7c
# ---------------------------------------------------------------------------

def diagrama_del_suelo_sobre(datos: dict, z: float) -> Tuple[float, float]:
    """
    --- correcciones de T-7c (H1) --- La parte del diagrama de presion del
    SUELO que queda por encima de la cota `z` (m sobre la base de la
    zapata), POR UNIDAD de coeficiente de empuje y sin la inclinacion: su
    fuerza y su momento respecto de esa cota. Es el diagrama del ensamble
    (`cargas_del_cabezal`): triangulo seco, rectangulo de su continuacion
    bajo el agua y triangulo sumergido (AASHTO 3.11.3), truncado en `z`.
    Con `z` = 0 da el diagrama entero.
    """
    gamma, h = datos["gamma"], datos["h"]
    gamma_sum = ((datos["gamma_saturado"] - GAMMA_AGUA_KN_M3)
                 if datos["gamma_saturado"] is not None else 0.0)
    h_w = max(min(datos["h_w"], h) - z, 0.0)
    altura = max(h - z, 0.0)
    seco = altura - h_w
    partes = (
        (gamma * seco ** 2 / 2, h_w + seco / LADOS_DEL_TRIANGULO),
        (gamma * seco * h_w, h_w / 2),
        (gamma_sum * h_w ** 2 / 2, h_w / LADOS_DEL_TRIANGULO),
    )
    return sum(p for p, _ in partes), sum(p * b for p, b in partes)


def _incremento_sobre_el_arranque(H: float, datos: dict, e_z: float,
                                  id_punto: Optional[str]
                                  ) -> Tuple[float, float]:
    """
    El incremento sismico del empuje (P_AE - P_A, componente horizontal `H`)
    por encima del arranque. La fuente da el PUNTO de aplicacion de su
    resultante ('punto_aplicacion_incremento_sismico', a fraccion·h) y no su
    diagrama: el proyecto lo reparte con el UNICO diagrama lineal sobre h
    que tiene la resultante en esa altura -- presion 2H/h·(2 - 3f) en la
    base y 2H/h·(3f - 1) en la corona; con f = 0.6, un trapecio cuatro veces
    mas cargado arriba que abajo -- y lo integra sobre el arranque. Por
    debajo de h/3 (el 0.333 de la ventana del criterio) se toma el
    triangulo de h/3: la resultante queda algo mas alta, del lado del mayor
    momento. Por encima de 2h/3 -- fuera de la ventana del criterio --
    ningun diagrama lineal sin traccion la tiene: se toma la resultante
    ENTERA a su altura, cota superior del cortante y, con un diagrama
    cargado hacia arriba, el momento casi entero.
    """
    h = datos["h"]
    tercio = 1.0 / LADOS_DEL_TRIANGULO
    f = datos["fraccion_brazo"]
    if not _finito(f):
        raise DatoInvalidoError(CRITERIO_BRAZO_SISMICO, valor=f,
                                id_punto=id_punto,
                                motivo="fraccion de h finita")
    if f > 2 * tercio + TOL_UMBRAL_NORMATIVO:
        return H, H * max(f * h - e_z, 0.0)
    f = max(f, tercio)
    escala = 2 * H / h
    base = escala * (2 - LADOS_DEL_TRIANGULO * f)
    corona = escala * (LADOS_DEL_TRIANGULO * f - 1)
    return _carga_lineal_sobre_un_tramo(0.0, h, base, corona, e_z, h, e_z)


def _diagrama_sobre_la_cara(K: float, gamma: float, gamma_bajo: float,
                            alto: float, mojado: float) -> Tuple[float, float]:
    """
    (P, z) del diagrama K·gamma·z sobre un plano de altura `alto` con
    `mojado` m de agua sobre su base: triangulo seco, su continuacion bajo
    el agua y triangulo con `gamma_bajo`; z desde la base del plano.
    """
    seco = alto - mojado
    partes = (
        (K * gamma * seco ** 2 / 2, mojado + seco / LADOS_DEL_TRIANGULO),
        (K * gamma * seco * mojado, mojado / 2),
        (K * gamma_bajo * mojado ** 2 / 2, mojado / LADOS_DEL_TRIANGULO),
    )
    P = sum(x for x, _ in partes)
    return P, (sum(x * z for x, z in partes) / P if P > 0 else 0.0)


def empujes_sobre_la_cara_de_la_pantalla(datos: dict, e_z: float, *,
                                         id_punto: Optional[str] = None
                                         ) -> dict:
    """
    --- VE-3.14, opcion 10 --- El empuje de una cuña de tanteo sobre la
    CARA del trasdos de la pantalla (Caltrans BDP 11.2, 11.2.2.4.1: «a trial
    wedge analysis along AB»), de altura h_p = z_rel - e_z (el relleno
    contra la pantalla), con la superficie REAL: el talud que sube desde la
    corona del relleno hasta la plataforma (`cuna_de_tanteo` con la subida
    entera). Devuelve los coeficientes equivalentes K = 2·P/h_p² (estatico)
    y, si `datos` es de la condicion sismica, K_E = 2·P_E/(h_p²·(1 - k_v));
    y los diagramas: el estatico con el suelo sumergido bajo el agua y el
    incremento con el peso total (C11.6.5.3) si hay agua.
    """
    rel, ang = datos["relleno"], datos["angulos"]
    h_p = rel["z_rel"] - e_z
    if not h_p > TOL_UMBRAL_NORMATIVO:
        return {"h_p": 0.0, "K": 0.0, "P": 0.0, "z": 0.0, "dP": 0.0,
                "K_E": None}
    gamma = datos["gamma"]
    gamma_sat = datos.get("gamma_saturado")
    gamma_sum = (gamma_sat - GAMMA_AGUA_KN_M3) if gamma_sat else 0.0
    mojado = min(max(datos["h_w"] - e_z, 0.0), h_p)
    P1, _rho = cuna_de_tanteo(h=h_p, subida=rel["subida"], talud=rel["talud"],
                              phi_grados=ang["phi"], delta_grados=ang["delta"],
                              gamma=1.0, que="empuje sobre la cara de la "
                              "pantalla", id_punto=id_punto)
    K = 2 * P1 / h_p ** 2
    P, z = _diagrama_sobre_la_cara(K, gamma, gamma_sum, h_p, mojado)
    salida = {"h_p": h_p, "K": K, "P": P, "z": z, "dP": 0.0, "K_E": None}
    if datos.get("K_AE") is not None:
        k_h, k_v = datos["k_h"], datos["k_v"]
        P1E, _ = cuna_de_tanteo(h=h_p, subida=rel["subida"],
                                talud=rel["talud"], phi_grados=ang["phi"],
                                delta_grados=ang["delta"], gamma=1.0, k_h=k_h,
                                k_v=k_v, que="empuje sismico sobre la cara de "
                                "la pantalla", id_punto=id_punto)
        K_E = 2 * P1E / (h_p ** 2 * (1.0 - k_v))
        gamma_t = gamma_sat if (gamma_sat and mojado > 0) else gamma
        G, _zt = _diagrama_sobre_la_cara(1.0, gamma, gamma_t, h_p, mojado)
        salida.update(K_E=K_E, dP=(K_E * (1.0 - k_v) - K) * G)
    return salida


def empujes_sobre_el_arranque(cargas: tuple, datos: dict, e_z: float, *,
                              id_punto: Optional[str] = None) -> dict:
    """
    --- correcciones de T-7c (H1) --- Por cada carga horizontal de la
    pantalla (sin factorar), la fuerza y el momento respecto del ARRANQUE
    (cota `e_z`) de la parte de su diagrama que esta por encima de el:

      EH.h          el diagrama del suelo (`diagrama_del_suelo_sobre`),
                    escalado a la resultante de la carga -- asi vale igual
                    para el empuje activo y para el de reposo, que conserva
                    la forma (`cargas_en_reposo`) --; brazo desde el
                    arranque.
      LS.h          uniforme sobre h: K·gamma·h_eq·(h - e_z), a
                    (h - e_z)/2.
      WA.h          triangulo hidrostatico sobre el arranque:
                    gamma_w·(h_w - e_z)²/2, a (h_w - e_z)/3.
      EQ.dPAE.h     el incremento sismico, con el diagrama lineal de
                    `_incremento_sobre_el_arranque`.
      EQ.PIR.muro   la inercia de la PANTALLA sola, k_h·W_pantalla en su
                    centro de gravedad: la de la zapata no carga la
                    pantalla.

    Devuelve {codigo: (H, M)}. Una carga de pantalla que no sea una de esas
    cinco entra con su resultante entera y su brazo desde el arranque (la
    aproximacion anterior: cota superior del cortante, NO del momento). Hoy
    no hay ninguna.
    """
    h = datos["h"]
    por_codigo = {c.codigo: c for c in cargas}
    alto = max(h - e_z, 0.0)
    salida = {}
    cara = None
    # --- dictamen Fable (VE-7 lote A, abierto (ii)) --- con el empuje
    # sismico DECLARADO el Evento Extremo I va entero con el plano virtual
    # del talon (EH, LS y EQ), que es el del analisis declarado (AASHTO
    # 11.6.5.2.2); la cuña sobre la cara no se calcula con un empuje que el
    # programa no sabe calcular. Resistencia I y Servicio no cambian.
    if datos.get("empuje_sismico_declarado"):
        pass
    elif _eleccion(CRITERIO_CARGA_PANTALLA, (PANTALLA_PLANO_VIRTUAL,
                                             PANTALLA_CUNA)) == PANTALLA_CUNA:
        # --- VE-3.14, opcion 10 --- la cuña sobre la cara de la pantalla,
        # en la misma proporcion con que cada juego (activo o reposo) escala
        # el diagrama del plano virtual.
        cara = empujes_sobre_la_cara_de_la_pantalla(datos, e_z,
                                                    id_punto=id_punto)
    for c in cargas:
        if c.sobre != ELEMENTO_PANTALLA:
            continue
        if cara is not None and c.codigo == C_EH_H:
            P_total, _ = diagrama_del_suelo_sobre(datos, 0.0)
            r = c.H / P_total if P_total > 0 else 0.0
            salida[c.codigo] = (cara["P"] * r, cara["P"] * cara["z"] * r)
        elif cara is not None and c.codigo == C_LS_H:
            proporcion = cara["K"] / datos["K_A"] if datos["K_A"] > 0 else 0.0
            H = c.H * cara["h_p"] / h * proporcion
            salida[c.codigo] = (H, H * cara["h_p"] / 2)
        elif cara is not None and c.codigo == C_EQ_H:
            H = cara["dP"] * math.cos(datos["inclinacion"])
            brazo = min(datos["fraccion_brazo"], 1.0) * cara["h_p"]
            salida[c.codigo] = (H, H * brazo)
        elif c.codigo == C_EH_H:
            P_total, _ = diagrama_del_suelo_sobre(datos, 0.0)
            P, M = diagrama_del_suelo_sobre(datos, e_z)
            r = c.H / P_total if P_total > 0 else 0.0
            salida[c.codigo] = (P * r, M * r)
        elif c.codigo == C_LS_H:
            H = c.H * alto / h
            salida[c.codigo] = (H, H * alto / 2)
        elif c.codigo == C_WA_H:
            h_w = datos["h_w"]
            mojado = max(h_w - e_z, 0.0)
            H = c.H * (mojado / h_w) ** 2 if h_w > 0 else 0.0
            salida[c.codigo] = (H, H * mojado / LADOS_DEL_TRIANGULO)
        elif c.codigo == C_EQ_H:
            salida[c.codigo] = _incremento_sobre_el_arranque(
                c.H, datos, e_z, id_punto)
        elif c.codigo == C_EQ_PIR_MURO:
            pantalla = por_codigo[C_DC_PANTALLA]
            H = datos["k_h"] * pantalla.V
            salida[c.codigo] = (H, H * max(pantalla.z - e_z, 0.0))
        else:
            salida[c.codigo] = (c.H, c.H * max(c.z - e_z, 0.0))
    return salida


def solicitaciones_por_elemento(entorno: EntornoDelCabezal, cargas: tuple,
                                combos: Tuple[CombinacionDeEstabilidad, ...],
                                datos: dict, *, marco: str = MARCO_LRFD
                                ) -> Tuple[SolicitacionDeElemento, ...]:
    """
    El cortante y el momento FACTORADOS de cada elemento del cabezal en su
    seccion critica, por metro de muro, para cada combinacion del marco LRFD
    (lo que T-7c necesita para armar; este prompt no arma nada).

      pantalla  en su arranque (cara superior de la zapata): las cargas
                horizontales que le llegan (`CargaDeCabezal.sobre` =
                pantalla), con el diagrama de cada empuje INTEGRADO POR
                ENCIMA DEL ARRANQUE (`empujes_sobre_el_arranque`): la
                fuerza y el momento respecto de la seccion son los de la
                parte del diagrama que esta sobre ella, como en una seccion
                del cuerpo de gravedad (`acciones_sobre_una_seccion`). La
                inercia es solo la de la pantalla. Hasta las correcciones de
                T-7c se tomaba la resultante ENTERA de cada empuje con su
                brazo desde el arranque, y el docstring la llamaba «del lado
                seguro»: lo era para el cortante y NO para el momento (el
                tramo del diagrama bajo el arranque entraba con brazo
                negativo; -8.5 % en el muro de tanteo, auditoria de T-7c
                H1).
      zapata    punta: la presion de contacto uniforme sobre el ancho
                efectivo (que arranca en la punta) menos el peso propio, en
                la cara delantera de la pantalla. Talon: el relleno, la
                sobrecarga, la componente vertical del empuje y el peso
                propio, menos la presion de contacto que alcance al talon y
                la subpresion, en la cara trasera de la pantalla.
      aleros    la misma seccion de la pantalla en su arranque, que es la
                altura inicial del alero; a lo largo del alero la altura
                baja y T-7c reutiliza este ensamble con la geometria de cada
                seccion.

    CON QUE EMPUJE SALEN (correcciones de T-7b, H7): toda solicitacion lleva
    el regimen del cabezal ('regimen_cabezal' [A], «cedente» de archivo),
    el coeficiente con que se calcularon sus empujes ('K_A' en la estatica,
    'K_AE' en la sismica, con su valor) y el K0 de AASHTO 3.11.5.2 con el
    cociente K0/K_A: si T-7c juzga que la pantalla no cede, la fuente pide
    para la resistencia el empuje en reposo (C11.6.5.4), y sus empujes
    crecerian en ese factor. Este prompt no lo aplica: lo marca.

    --- T-7c --- `marco` elige de que marco son las combinaciones que se
    recorren: el LRFD por defecto (lo de siempre) o `MARCO_E060`, el de las
    combinaciones del contraste con E.060 que arma `solicitaciones_de_
    resistencia`. Las formulas son las mismas; cambian los factores.
    """
    g = entorno.geometria
    e_z = g.espesor_zapata
    punta, talon = datos["punta"], datos["talon"]
    x_trasdos = datos["x_trasdos"]
    por_codigo = {c.codigo: c for c in cargas}
    salida = []
    sismica = datos["K_AE"] is not None
    reposo = datos.get("empuje_estatico") == EMPUJE_ESTATICO_REPOSO
    marca = dict(regimen=datos["regimen"],
                 coeficiente_de_empuje=(
                     "K_AE (equivalente del declarado)"
                     if sismica and datos.get("empuje_sismico_declarado")
                     else "K_AE" if sismica else
                                        "K0" if reposo else "K_A"),
                 K_empuje=(datos["K_AE"] if sismica else
                           datos["K0"] if reposo else datos["K_A"]),
                 K0=datos["K0"], K0_sobre_K_A=datos["K0"] / datos["K_A"])
    try:
        arranque = empujes_sobre_el_arranque(cargas, datos, e_z,
                                             id_punto=entorno.id_punto)
    except MetodoNoEvaluableError:
        # --- VE-3.15 (H5 de su revision) --- Con la cuña sobre la pantalla
        # (opcion 10) una cuña sin maximo no detiene la ESTABILIDAD: estas
        # filas son informativas, y el armado de la pantalla, que las
        # recalcula, la levanta como el `Bloqueo` de ese elemento.
        arranque = None
    for combo in (c for c in combos if c.marco == marco):
        f = dict(combo.factores)
        if arranque is None:
            salida.extend(_solicitaciones_de_la_zapata(
                marca, combo, f, datos, por_codigo, e_z, punta, talon,
                x_trasdos))
            continue
        V_p = sum(f[k] * H for k, (H, _) in arranque.items())
        M_p = sum(f[k] * M for k, (_, M) in arranque.items())
        salida.append(SolicitacionDeElemento(**marca,
            elemento=ELEMENTO_PANTALLA, seccion="arranque de la pantalla",
            combinacion=combo.nombre, V_u=V_p, M_u=M_p,
            nota="diagrama de cada empuje integrado por encima del "
                 "arranque; inercia de la pantalla sola"
                 + (NOTA_ARMADO_CON_EMPUJE_DECLARADO
                    if datos.get("empuje_sismico_declarado") else "")))
        salida.append(SolicitacionDeElemento(**marca, 
            elemento=ELEMENTO_ALEROS,
            seccion="arranque del alero (altura inicial, la del cabezal)",
            combinacion=combo.nombre, V_u=V_p, M_u=M_p,
            nota="la de la pantalla en su arranque: el alero empieza a la "
                 "altura del cabezal y baja con el talud"))
        salida.extend(_solicitaciones_de_la_zapata(
            marca, combo, f, datos, por_codigo, e_z, punta, talon, x_trasdos))
    return tuple(salida)


def _solicitaciones_de_la_zapata(marca, combo, f, datos, por_codigo, e_z,
                                 punta, talon, x_trasdos) -> list:
    """La punta y el talon de la zapata en la cara de la pantalla."""
    salida = []
    if not combo.N > 0:
        return salida
    e = abs(combo.excentricidad)
    B_ef = combo.B - 2 * e
    if not B_ef > 0:
        return salida
    sigma = combo.N / B_ef
    f_dc = f.get(C_DC_ZAPATA, 0.0)
    w_zap = f_dc * datos["gamma_c"] * e_z
    a = min(punta, B_ef)
    salida.append(SolicitacionDeElemento(**marca, 
        elemento=ELEMENTO_ZAPATA, seccion="punta, cara de la pantalla",
        combinacion=combo.nombre,
        V_u=sigma * a - w_zap * punta,
        M_u=sigma * a * (punta - a / 2) - w_zap * punta ** 2 / 2,
        nota="presion uniforme sobre B - 2e desde la punta, menos el "
             "peso propio; positivo = tracciona la cara inferior"))
    sobre_talon = max(B_ef - x_trasdos, 0.0)
    abajo = sum(f.get(k, 0.0) * por_codigo[k].V
                for k in (C_EV_TALON, C_LS_V, C_EH_V, C_EQ_V)
                if k in por_codigo)
    m_abajo = sum(f.get(k, 0.0) * por_codigo[k].V
                  * (por_codigo[k].x - x_trasdos)
                  for k in (C_EV_TALON, C_LS_V, C_EH_V, C_EQ_V)
                  if k in por_codigo)
    u = por_codigo.get(C_WA_U)
    sub = -f.get(C_WA_U, 0.0) * u.V * talon / combo.B if u else 0.0
    salida.append(SolicitacionDeElemento(**marca, 
        elemento=ELEMENTO_ZAPATA, seccion="talon, cara de la pantalla",
        combinacion=combo.nombre,
        V_u=abajo + w_zap * talon - sigma * sobre_talon - sub,
        M_u=(m_abajo + w_zap * talon ** 2 / 2
             - sigma * sobre_talon ** 2 / 2 - sub * talon / 2),
        nota="relleno, sobrecarga, componente vertical del empuje y "
             "peso propio, menos la presion de contacto que alcanza al "
             "talon y la subpresion (repartida uniforme); positivo = "
             "tracciona la cara superior"))
    return salida


# ---------------------------------------------------------------------------
# El ensamble de UN cabezal en UNA condicion
# ---------------------------------------------------------------------------

def _agua_del_sismo_sin_drenaje(datos: dict) -> tuple:
    """
    --- VE-4e (ficha VE3-21) --- La altura de agua de la condicion sismica
    cuando el trasdos se declara SIN drenaje, con la eleccion de la que sale.
    Con el trasdos drenado no se imprime: el agua del sismo es la del
    freatico natural, la misma del paso del agua de la estatica.
    """
    nivel = datos["nivel_agua_sismo"]
    if nivel is None:
        return ()
    return (_m("h_w", datos["h_w"], "m",
               f"agua del relleno bajo sismo con '{CRITERIO_DRENAJE}' = "
               f"'{DRENAJE_SIN}': el nivel medio en el tiempo (AASHTO "
               f"C11.6.5.3), '{CRITERIO_NIVEL_AGUA_SISMO}' [A] = '{nivel}' -- "
               + ("la superficie del relleno retenido, el agua de la "
                  "estatica" if nivel == NIVEL_MEDIO_SUPERFICIE else
                  "el freatico natural del punto, como el relleno "
                  "drenado")),)


def _nota_del_agua_del_sismo_sin_drenaje(datos: dict) -> str:
    """La frase del paso sismico que separa el agua del sismo de la estatica."""
    nivel = datos["nivel_agua_sismo"]
    if nivel is None:
        return ""
    return ("Trasdos sin drenaje: la condicion estatica llena el relleno "
            "retenido hasta su superficie (11.6.6), y esta va con el nivel "
            "medio del agua en el tiempo que recomienda C11.6.5.3; la fuente "
            "no dice cual es en un relleno que no drena, y el proyectista lo "
            f"declara ('{CRITERIO_NIVEL_AGUA_SISMO}' [A] = '{nivel}', h_w = "
            f"{datos['h_w']:.3f} m). ")


def _pasos_de_cargas(entorno, condicion, cargas, combos, datos,
                     sufijo) -> List[PasoDeMemoria]:
    ext = entorno.extremo
    ang = datos["angulos"]
    rel = datos["relleno"]
    pasos = []
    if condicion is CondicionAnalisis.ESTATICO:
        pasos.append(paso(
            "F9.EMPUJES", codigo=f"9.2.1.{sufijo}",
            que=f"Empuje activo del relleno: cabezal de {ext}",
            formula=(("K_A = 2·max_rho P_cuña(rho) / (gamma·h²), P_cuña = "
                      "W·sen(rho - phi) / cos(rho - phi - delta);  "
                      if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else "")
                     + "P_A = K_A·[gamma·h1²/2 + gamma·h1·h_w + (gamma_sat - "
                     "gamma_w)·h_w²/2];  E_h = P_A·cos(delta + beta);  E_v = "
                     "P_A·sen(delta + beta)"),
            formula_cita_id=("AASHTO_LRFD_9.3.11.5.3#CULMANN"
                             if datos["metodo_empuje"] == METODO_EMPUJE_CUNA
                             else "MP.2.4.4.1.5.3"),
            sustitucion=(
                _m("phi", ang["phi"], "grados",
                   f"criterio '{CRITERIO_PHI_RELLENO}': ensayo del relleno"),
                _m("delta", ang["delta"], "grados", ang["origen_delta"]),
                _m("i", ang["i"], "grados", rel["origen_i"]),
                _m("beta", ang["beta"], "grados", "plano de empuje: "
                   + ang["plano"]),
                _m("gamma", datos["gamma"], "kN/m3",
                   f"criterio '{CRITERIO_GAMMA_RELLENO}'"),
                _m("h", datos["h"], "m",
                   "altura del plano de empuje: de la base de la zapata al "
                   "terreno que queda sobre el extremo del talon (relleno "
                   f"retenido {rel['z_rel']:.3f} m + {rel['sobre_talon']:.3f}"
                   " m que el talud sube sobre el talon)"),
                _m("h_w", datos["h_w"], "m",
                   "altura de agua en el plano de empuje (paso del agua)"),
                _m("subida", rel["subida_sobre_plano"], "m",
                   "lo que el relleno sigue subiendo sobre el tope del "
                   f"plano, con talud 1:{rel['talud']:g}, hasta la "
                   "plataforma (superficie de la cuña)"),
                _m("K_A", datos["K_A"], "-",
                   ("EQUIVALENTE de la cuña critica de Culmann sobre la "
                    f"superficie real (rho = {datos['rho_A']:.2f} grados; "
                    "AASHTO 3.11.5.3)"
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    "Coulomb con la pendiente i, Manual de Puentes "
                    "2.4.4.1.5.3 / AASHTO 3.11.5.3")),
                _m("K_A_formula", datos["K_A_formula"], "-",
                   ("CONTRASTE: Coulomb con la pendiente equivalente i "
                    f"(regla 2H); {_sesgo(datos['K_A_formula'], datos['K_A'])}"
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    "el que rige (formula cerrada)"))),
            resultado=Magnitud(
                "E_h / E_v",
                f"{_carga(cargas, C_EH_H).H:.3f} / "
                f"{_carga(cargas, C_EH_V).V:.3f}", "kN/m",
                f"P_A = {datos['P_A']:.3f} kN/m, a {datos['z_A']:.3f} m "
                "sobre la base"),
            citas_textuales=("AASHTO_LRFD_9.C3.11.5.3#PLANO_DEL_TALON",
                             "AASHTO_LRFD_9.C3.11.5.3#DELTA",
                             "AASHTO_LRFD_9.3.11.5.8.1#CUNA",
                             "AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO",
                             # El regimen del cabezal y el K0 que la
                             # interfaz de T-7c marca (H7).
                             "AASHTO_LRFD_9.C11.6.5.4#K0",
                             "AASHTO_LRFD_9.3.11.5.2#K0"),
            nota_del_proyecto=(
                "El empuje ya no se toma entero como horizontal (ficha "
                "EXT-7-04): la componente vertical carga la base en el plano "
                "de empuje. "
                + ("METODO: la cuña de tanteo de Culmann sobre el plano "
                   "vertical del talon con la superficie REAL del relleno "
                   f"(regla '{rel['regla']}', '{CRITERIO_REGLA_PENDIENTE}' "
                   "[A]): lo que la fuente pide para un relleno que se "
                   "aparta del talud uniforme. Su coeficiente equivalente se "
                   "reparte con el diagrama triangular de Coulomb (resultante "
                   "a h/3 en seco) y, bajo el agua, con el suelo sumergido. "
                   "La pendiente equivalente 2H (Figura C3.11.5.8.1-1, de los "
                   "muros de suelo reforzado) queda como contraste y como "
                   "alternativa barrible."
                   if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                   "METODO: la formula cerrada con la pendiente i "
                   f"({rel['origen_i']}). La regla general de la fuente para "
                   "un relleno quebrado es la cuña de tanteo, que es la de "
                   "archivo; la pendiente equivalente 2H la subestima del 7 "
                   "al 11 % en los cabezales de A-01.")
                + f" Regimen del cabezal: '{datos['regimen']}' "
                f"('{CRITERIO_REGIMEN}' [A]): "
                + (("muro que NO cede (11.6.5.4 y C11.6.5.4): rige el "
                    f"empuje en REPOSO, K0 = 1 - sen(phi) = {datos['K0']:.4f} "
                    "(AASHTO 3.11.5.2-1) sobre el mismo diagrama, todo "
                    "horizontal (sin friccion muro-relleno), con el factor "
                    "de carga de la fila «En reposo» (1.35); P_0 = "
                    f"{datos['P_0']:.3f} kN/m frente al activo horizontal "
                    f"{datos['P_A'] * math.cos(datos['inclinacion']):.3f}. "
                    "K0 es de terreno horizontal: con un relleno que sube "
                    "detras es una cota inferior, y por eso rige el activo "
                    "cuando da mas.")
                   if datos["empuje_estatico"] == EMPUJE_ESTATICO_REPOSO
                   else ("muro que NO cede, pero el activo con la superficie "
                         "real da mas componente horizontal que el reposo "
                         f"de 3.11.5.2-1 (K0 = {datos['K0']:.4f}, de terreno "
                         "horizontal; P_0 = "
                         f"{datos['P_0']:.3f} kN/m): rige el activo, que un "
                         "muro que no cede no puede tener por debajo."
                         if datos["regimen"] == REGIMEN_NO_CEDENTE else
                         "empuje activo de muro que cede, la hipotesis de "
                         "la estabilidad externa (C11.6.5.4)."))
                )))
        ls = _carga(cargas, C_LS_H)
        pasos.append(paso(
            "F9.SOBRECARGA", codigo=f"9.2.2.{sufijo}",
            que=f"Sobrecarga viva de trafico: cabezal de {ext}",
            formula="LS_h = K_A·gamma·h_eq·h;  LS_v = gamma·h_eq·talon",
            formula_cita_id="AASHTO_LRFD_9.3.11.6.4",
            sustitucion=(
                _m("h_eq", datos["h_eq"], "m",
                   "max(piso del Manual de Puentes, tabla de AASHTO "
                   "3.11.6.4 por altura h y orientacion del muro: "
                   + _texto_de_la_sobrecarga(
                       entorno.geometria,
                       envolvente_de_h_eq_paralelo(entorno)) + ")"),
                _m("h", datos["h"], "m", "altura del plano de empuje, con "
                   "zapata"),
                _m("K_A", datos["K_A"], "-", "el del empuje activo")),
            resultado=Magnitud(
                "LS_h / LS_v",
                f"{ls.H:.3f} / "
                f"{(_carga(cargas, C_LS_V).V if _tiene(cargas, C_LS_V) else 0.0):.3f}",
                "kN/m", "empuje a h/2; peso sobre el talon"),
            citas_textuales=("AASHTO_LRFD_9.C11.5.6#SOBRECARGA",),
            nota_del_proyecto=(
                "Aplica siempre en un cabezal bajo terraplen vial (Sec. "
                "9.2). El cabezal es NORMAL al eje del conducto (decision "
                "del dueño): con un cruce sin esviaje su trasdos queda "
                "paralelo a la via, y con esviaje "
                f"({entorno.esviaje_grados:g} grados) forma ese angulo con "
                "ella; AASHTO solo tabula el muro paralelo y el estribo "
                "perpendicular, y se lee la tabla del dato de sitio "
                "declarado. El PESO de la sobrecarga sobre el talon entra "
                "solo en el portante.")))
        pasos.append(paso(
            "F9.AGUA", codigo=f"9.2.3.{sufijo}",
            que=f"Agua en el trasdos y subpresion: cabezal de {ext}",
            formula=("E_w = gamma_w·h_w²/2;  U = gamma_w·(h_delante + "
                     "h_w)/2·B"),
            formula_cita_id="AASHTO_LRFD_9.3.11.3",
            sustitucion=(
                _m("cota_NF", datos["cota_freatico"], "msnm",
                   entorno.origen_freatico or "cota del nivel freatico"),
                _m("cota_desplante", entorno.geometria.cota_desplante,
                   "msnm", "base de la zapata de este cabezal (T-7a)"),
                _m("D_f", datos["D_f"], "m", "profundidad de desplante"),
                _m("h_delante", datos["h_w_natural"], "m",
                   "agua sobre la base por el freatico natural: max(cota_NF "
                   "- cota_desplante, 0), no mayor que h"),
                _m("h_w", datos["h_w"], "m",
                   f"agua en el relleno con '{CRITERIO_DRENAJE}' = "
                   f"'{datos['drenaje']}': "
                   + ("hasta la superficie del relleno retenido contra el "
                      "trasdos (z_rel; el drenaje no puede darse, AASHTO "
                      "11.6.6), nunca por encima del muro"
                      if datos["drenaje"] == DRENAJE_SIN else
                      "el freatico natural (relleno drenado: filtro y "
                      "lloraderos en planos)"))),
            resultado=Magnitud(
                "E_w / U",
                f"{(_carga(cargas, C_WA_H).H if _tiene(cargas, C_WA_H) else 0.0):.3f}"
                f" / {(-_carga(cargas, C_WA_U).V if _tiene(cargas, C_WA_U) else 0.0):.3f}",
                "kN/m", "empuje hidrostatico sobre el plano de empuje / "
                "subpresion bajo la zapata"),
            citas_textuales=("AASHTO_LRFD_9.11.6.6#DRENAJE",
                             "E050.39.13.8#DRENAJE"),
            nota_del_proyecto=(
                "Bajo el nivel del agua el suelo empuja con su peso "
                "sumergido y el agua aparte: no se cuenta dos veces. "
                "El agua delante del muro no se cuenta como "
                "empuje que estabilice. El drenaje reduce el agua del "
                "relleno SOLO si se declara, y compromete un detalle que "
                "tiene que estar en los planos.")))
    else:
        pasos.append(paso(
            "F9.SISMO", codigo=f"9.2.4.{sufijo}",
            que=f"Demanda sismica: cabezal de {ext}",
            formula=("P_AE = gamma·h²·(1 - k_v)·K_AE / 2;  dP_AE = P_AE - "
                     "P_A, a f·h;  P_IR = k_h·(W_w + W_s)"),
            formula_cita_id="AASHTO_LRFD_9.A11.3.1#KAE",
            sustitucion=(
                _m("k_h", datos["k_h"], "-",
                   "cadena sismica de Sec. 9.2 (PGA, F_pga y "
                   f"'{CRITERIO_FACTOR_MURO}' = "
                   f"'{ca.valor(CRITERIO_FACTOR_MURO)}')"),
                _m("k_v", datos["k_v"], "-", f"criterio '{CRITERIO_K_V}'"),
                _m("phi", ang["phi"], "grados", "relleno"),
                _m("i", ang["i"], "grados", rel["origen_i"]),
                _m("delta", ang["delta"], "grados", ang["origen_delta"]),
                _m("K_AE", datos["K_AE"], "-",
                   ("EQUIVALENTE del empuje DECLARADO, 2·P_AE/(gamma·h²·"
                    "(1 - k_v)) (`" + DATO_EMPUJE_SISMICO + "`)"
                    if datos.get("empuje_sismico_declarado") else
                    "EQUIVALENTE de la cuña critica pseudoestatica, "
                    "2·P_AE/(gamma·h²·(1 - k_v)) (rho = "
                    f"{datos['rho_AE']:.2f} grados; AASHTO C11.6.5.3)"
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    ("(K_A + 2·(P_cuña,E - P_cuña)/h²)/(1 - k_v): el "
                     "incremento de la cuña de tanteo pseudoestatica "
                     f"(rho = {datos['rho_AE']:.2f} grados), porque "
                     "Mononobe-Okabe esta fuera de su dominio (C11.6.5.3)")
                    if datos.get("metodo_incremento") == METODO_INCREMENTO_CUNA
                    else "Mononobe-Okabe")),
                _m("K_AE_formula",
                   (datos["K_AE_formula"] if datos["K_AE_formula"]
                    is not None else "no evaluable"), "-",
                   ("CONTRASTE: Mononobe-Okabe con la pendiente equivalente "
                    "i; " + (_sesgo(datos["K_AE_formula"], datos["K_AE"])
                             if datos["K_AE_formula"] is not None else
                             f"fuera de su dominio: phi = {ang['phi']:.2f} < "
                             f"i + psi = {ang['i'] + datos['psi']:.2f} "
                             "grados (11.6.5.3)")
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    ("fuera de su dominio: phi = "
                     f"{ang['phi']:.2f} < i + psi = "
                     f"{ang['i'] + datos['psi']:.2f} grados (11.6.5.3)"
                     if datos["K_AE_formula"] is None else
                     "el que rige (formula cerrada)"))),
                _m("K_A", datos["K_A"], "-", "el estatico, misma "
                   "formulacion"),
                _m("h", datos["h"], "m", "altura del plano de empuje"),
                _m("f", datos["fraccion_brazo"], "-",
                   ("de la altura de la resultante declarada"
                    if datos.get("empuje_sismico_declarado") else
                    f"criterio '{CRITERIO_BRAZO_SISMICO}' [C]")),
                _m("W_w", datos["W_w"], "kN/m", "peso del muro"),
                _m("W_s", datos["W_s"], "kN/m", "peso del relleno sobre el "
                   "talon"))
            + _agua_del_sismo_sin_drenaje(datos),
            resultado=Magnitud(
                "P_AE / P_IR",
                f"{datos['P_AE']:.3f} / "
                f"{datos['k_h'] * (datos['W_w'] + datos['W_s']):.3f}",
                "kN/m",
                f"resultante del empuje total a {datos['z_AE']:.3f} m "
                f"sobre la base ({datos['z_AE'] / datos['h']:.2f}·h)"),
            citas_textuales=("AASHTO_LRFD_9.11.6.5.3#VALIDEZ",
                             "AASHTO_LRFD_9.C11.6.5.3#CUNA",
                             "AASHTO_LRFD_9.C11.6.5.3#RESULTANTE",
                             "AASHTO_LRFD_9.C11.6.5.4#CEDENTE",
                             "AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE")
            + (("AASHTO_LRFD_9.C11.6.5.3#AGUA_TOTAL",)
               if datos.get("tratamiento_agua_sismo")
               == AGUA_SE_MUEVE_CON_EL_SUELO else ())
            + ((CITA_NIVEL_MEDIO, "AASHTO_LRFD_9.11.6.6#DRENAJE")
               if datos["nivel_agua_sismo"] is not None else ())
            + _citas_del_empuje_declarado(datos)
            + (CITAS_K_V_EN_LOS_PESOS
               if abs(datos["k_v"]) > TOL_UMBRAL_NORMATIVO else ()),
            nota_del_proyecto=(
                _nota_del_empuje_declarado(datos)
                + _nota_del_agua_del_sismo_sin_drenaje(datos)
                + (("Con agua en el plano de empuje (h_w = "
                  f"{datos['h_w']:.3f} m) el incremento sismico va con el "
                  "peso TOTAL del suelo bajo el agua: suelo y agua se mueven "
                  "juntos en el relleno que no drena libremente (C11.6.5.3, "
                  "'agua_del_relleno_bajo_sismo' [C]); el estatico sigue "
                  "con el sumergido y la hidrostatica. "
                  if datos.get("tratamiento_agua_sismo")
                  == AGUA_SE_MUEVE_CON_EL_SUELO else "")
                 + ("Cuña de tanteo pseudoestatica (C11.6.5.3) con la "
                    "superficie real"
                    + ("" if datos.get("tratamiento_agua_sismo") else
                       ", relleno sin agua en el plano de empuje")
                    + "; Mononobe-Okabe con la pendiente equivalente queda "
                    "al lado como contraste. "
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    ("Mononobe-Okabe con la pendiente de la regla queda "
                     "FUERA de su dominio (phi = "
                     f"{ang['phi']:.2f} < i + psi = {ang['i']:.2f} + "
                     f"{datos['psi']:.2f} grados, 11.6.5.3): el incremento "
                     "sale de la cuña de tanteo pseudoestatica con la "
                     "superficie real del relleno, P_AE - P_A de la MISMA "
                     "cuña, que la fuente da para ese caso (C11.6.5.3); el "
                     "estatico sigue con la formula de la regla (VE-5). ")
                    if datos.get("metodo_incremento") == METODO_INCREMENTO_CUNA
                    else "Mononobe-Okabe dentro de su dominio: "
                    + ("" if datos.get("tratamiento_agua_sismo") else
                       "relleno sin agua en el plano de empuje y ")
                    + f"phi = {ang['phi']:.2f} >= i + psi = "
                    f"{ang['i']:.2f} + {datos['psi']:.2f} grados. "))
                + (("Regimen del cabezal CEDENTE ('regimen_cabezal' [A]): "
                    "un muro que no cede pediria k_h = 1.0·k_h0 y presiones "
                    "mayores (11.6.5.4). ")
                   if datos["regimen"] == REGIMEN_CEDENTE else
                   ("Muro que NO cede ('regimen_cabezal' [A]): k_h = "
                    f"1.0·k_h0 = {datos['k_h']:.3f}, sin la reduccion por "
                    "desplazamiento (11.6.5.4), y la resultante del estatico "
                    "mas el sismico no bajo h/2 (C11.6.5.4)"
                    + (("; sobre el reposo, el incremento es "
                        + ("lo que el total pseudoestatico supera al reposo"
                           if datos["empuje_sismico_no_cede"]
                           == NO_CEDE_MAYOR_DE_REPOSO_Y_TOTAL else
                           "el pseudoestatico P_AE - P_A, todo horizontal")
                        + f" ('{CRITERIO_EMPUJE_SISMICO_NO_CEDE}' [A]). ")
                       if datos["empuje_estatico"] == EMPUJE_ESTATICO_REPOSO
                       else ". ")))
                + "Los dos casos "
                "del 11.6.5.1 se combinan aparte: 100 % P_AE + 50 % P_IR, y "
                "50 % P_AE (no menos que el empuje estatico) + 100 % P_IR. "
                "La fraccion f se aplica al INCREMENTO; el empuje estatico "
                "sigue en su centroide.")))
    filas = tuple(
        Magnitud(c.codigo,
                 (f"V = {c.V:.3f} kN/m, x = {c.x:.3f} m" if c.V else "")
                 + (f"H = {c.H:.3f} kN/m, z = {c.z:.3f} m" if c.H else ""),
                 "", f"{c.descripcion}; {c.procedencia}")
        for c in cargas)
    resumen = "; ".join(
        f"«{c.nombre}»: N = {c.N:.2f}, H = {c.H:.2f} kN/m, M_e = "
        f"{c.M_estabilizante:.2f}, M_v = {c.M_volcante:.2f} kN·m/m"
        for c in combos)
    filas_eta, nota_eta = _eta_para_la_memoria(condicion)
    pasos.append(paso(
        "F9.COMBINACIONES", codigo=f"9.2.5.{sufijo}",
        que=f"Cargas con sus brazos y combinaciones: cabezal de {ext}, "
            f"condicion {condicion.value}",
        formula=("N = Σ eta_i·gamma·V;  H = Σ eta_i·gamma·H;  M respecto de "
                 "la punta = Σ eta_i·gamma·(V·x - H·z)"),
        sustitucion=filas + filas_eta,
        resultado=Magnitud("combinaciones", len(combos), "",
                           "de los dos marcos, cada una con SUS factores"),
        citas_textuales=("AASHTO_LRFD_9.C11.5.6#FIGURAS",
                         "E050.17.1#SERVICIO") + CITAS_DE_ETA,
        nota_del_proyecto=(
            "x se mide desde la arista de la punta hacia el relleno y z "
            "desde la base de la zapata hacia arriba; V positiva hacia "
            "abajo y H positiva hacia el cauce. " + nota_eta + " "
            + resumen + ". Factores de cada combinacion (en Resistencia I, "
            "gamma·eta_i): "
            + "; ".join(
                f"«{c.nombre}»: " + ", ".join(
                    f"{k} {v:g}" for k, v in c.factores)
                for c in combos) + ".")))
    return pasos


def _eta_para_la_memoria(condicion: CondicionAnalisis
                         ) -> Tuple[Tuple[Magnitud, ...], str]:
    """
    --- verificacion de T-7 (punto 9) --- Lo que la memoria dice del
    modificador de carga de AASHTO 1.3.2.1: las magnitudes con su
    procedencia (para la sustitucion del paso de combinaciones y del paso
    del regimen del armado) y la frase de la nota. En la condicion sismica
    no hay magnitudes: el Evento Extremo I va con eta = 1.00 y se dice.
    """
    if condicion is not CondicionAnalisis.ESTATICO:
        return (), ("Modificador de carga (AASHTO 1.3.2.1): en el Evento "
                    "Extremo I eta_D = eta_R = eta_I = "
                    f"{ETA_OTROS_ESTADOS_LIMITE_AASHTO:.2f} («For all other "
                    "limit states», 1.3.3, 1.3.4 y 1.3.5): los factores no "
                    "se modifican. El marco ASD no lleva eta.")
    eta = modificador_de_carga()
    m = lambda s, v, p: Magnitud(s, v, "", p, cifras=CIFRAS_FINA)  # noqa: E731
    filas = (
        m("eta_D", eta["eta_D"], f"'{CRITERIO_ETA_DUCTILIDAD}' [A] "
          f"({NUMERAL_ETA_DUCTILIDAD_AASHTO})"),
        m("eta_R", eta["eta_R"], f"'{CRITERIO_ETA_REDUNDANCIA}' [A] "
          f"({NUMERAL_ETA_REDUNDANCIA_AASHTO})"),
        m("eta_I", eta["eta_I"], f"'{CRITERIO_ETA_IMPORTANCIA}' [A]: la "
          "importancia operativa del cruce, la misma del conducto (AASHTO "
          "1.3.5; Manual de Puentes 2.3.2.5)"),
        m("eta_i, cargas de gamma maximo", eta["maximo"],
          "eta_D·eta_R·eta_I >= "
          f"{ETA_PISO_GAMMA_MAXIMO_AASHTO:g} (Ec. 1.3.2.1-2)"),
        m("eta_i, cargas de gamma minimo", eta["minimo"],
          "1/(eta_D·eta_R·eta_I) <= "
          f"{ETA_TECHO_GAMMA_MINIMO_AASHTO:g} (Ec. 1.3.2.1-3)"),
    )
    return filas, (
        f"Modificador de carga ({NUMERAL_MODIFICADOR_DE_CARGA_AASHTO}; Σ "
        "eta_i·gamma_i·Q_i <= phi·R_n): en Resistencia I las cargas de "
        "gamma maximo llevan "
        f"eta_i = {eta['maximo']:.4f} y las de gamma minimo (DC y EV de la "
        f"combinacion de minimos) eta_i = {eta['minimo']:.4f}; el empuje, la "
        "sobrecarga viva y el agua van con el de maximo en las dos. Es el "
        "mismo eta_I del conducto del cruce. El marco ASD (E.050) y el "
        "contraste de E.060 no llevan eta.")


def _carga(cargas: tuple, codigo: str) -> CargaDeCabezal:
    return next(c for c in cargas if c.codigo == codigo)


def _tiene(cargas: tuple, codigo: str) -> bool:
    return any(c.codigo == codigo for c in cargas)


PENDIENTES_E4_E5 = (
    ("E4", "estabilidad global del muro: analisis de equilibrio limite con "
           "la estratigrafia del EMS (AASHTO LRFD 11.6.3.7; E.050 39.13.6 "
           "b). Diferida al expediente: el programa no la evalua"),
    ("E5", "estabilidad del talud que soporta al cabezal (E.050 Art. 30.3). "
           "Diferida al expediente con el EMS: el programa no la evalua"),
)


# ---------------------------------------------------------------------------
# --- VE-4a --- E4 y E5 con el FS DECLARADO (ficha T7B-07)
# ---------------------------------------------------------------------------
# El ensamble NO calcula la estabilidad global ni la del talud: cuando el
# punto declara el resultado del analisis externo
# (`EntornoDelCabezal.estabilidad_global`), lo contrasta en los dos marcos
# que no se cruzan, y lo declarado sale de `pendientes`:
#
#   ASD   FS >= el minimo de E.050 (39.13.6 b para E4, Art. 30.3 para E5),
#         por analogia [N→]: la tabla de Sec. 9.3 de la hoja de ruta.
#   LRFD  FS >= 1/phi: phi de 11.6.3.7 en la condicion estatica (la fila es
#         'fila_phi_estabilidad_global' [A], sin valor de archivo) y 0.9 de
#         11.5.8 bajo sismo. El puente FS = 1/phi es el comentario
#         C11.6.3.7, con la lectura del proyecto declarada en su cita.
#
# Las filas van en `EstabilidadDelCabezal.globales` y no en `verificaciones`:
# el dimensionamiento de la zapata itera sobre E1 a E3 y el ancho no mueve
# un FS que el programa no calcula.
NOMBRE_DE_LA_GLOBAL = {"E4": "estabilidad global del muro",
                       "E5": "estabilidad del talud que soporta al cabezal"}


CITA_ASD_DE_LA_GLOBAL = {"E4": "E050.39.13.6", "E5": "E050.30.3"}


NUMERAL_DE_LA_GLOBAL = {"E4": "AASHTO LRFD 11.6.3.7; E.050 39.13.6 b",
                        "E5": "AASHTO LRFD 11.6.3.7; E.050 Art. 30.3"}


def fila_phi_estabilidad_global() -> Optional[str]:
    """
    La fila de phi de AASHTO 11.6.3.7 que el proyectista declaro
    ('fila_phi_estabilidad_global' [A], SIN valor de archivo), o None si no
    la declaro: la fila estatica del marco LRFD decide sin ella solo si las
    dos filas dan lo mismo; si no, espera el criterio (VE-5 fixve4:
    `_fila_global_declarada` levanta `CriterioPendienteError`). Una fila que
    no es de la tabla se rechaza.
    """
    try:
        fila = ca.valor(CRITERIO_FILA_PHI_GLOBAL)
    except CriterioPendienteError:
        return None
    if fila not in PHI_ESTABILIDAD_GLOBAL_11_6_3_7:
        raise DatoInvalidoError(
            CRITERIO_FILA_PHI_GLOBAL, valor=fila,
            motivo="se espera una de: "
                   + ", ".join(PHI_ESTABILIDAD_GLOBAL_11_6_3_7))
    return fila


def _traza_de_la_global(declarada: dict) -> str:
    """De donde sale el FS declarado, en una frase para la memoria."""
    texto = (f"«{declarada['documento']}» ({declarada['fecha']}), metodo "
             f"{declarada['metodo']}")
    if declarada.get("programa"):
        texto += f", programa {declarada['programa']}"
    return texto


def _fila_global_declarada(*, entorno: EntornoDelCabezal,
                           condicion: CondicionAnalisis, codigo: str,
                           marco: str, fs: float, traza: str, decide: bool,
                           sufijo: str) -> Verificacion:
    """
    UNA fila E4 o E5 de UN marco con el FS declarado: el paso dice de que
    documento sale el FS y que el programa no lo calcula; el umbral, de que
    numeral sale el minimo. Si el marco no decide ('marco_estabilidad_
    cabezal'), un incumplimiento sale como INDICADOR.
    """
    clave = CLAVE_FS_DE_CODIGO[codigo]
    ext = entorno.extremo
    nombre = NOMBRE_DE_LA_GLOBAL[codigo]
    procedencia = (f"DECLARADO en {traza} (dato externo "
                   f"`{DATO_ESTABILIDAD_GLOBAL}` del punto): resultado de un "
                   "analisis externo de equilibrio limite; no lo calcula "
                   "este programa")
    fs_mag = _m("FS", fs, "-", procedencia)
    nota = (f"El factor de seguridad NO lo calcula este programa: es el "
            f"resultado declarado del analisis externo ({traza}), y aqui "
            "solo se contrasta con el minimo de cada marco. ")
    no_decidida = None
    criterio = None
    if marco == MARCO_ASD:
        admisible = fs_requerido(verificacion=clave, condicion=condicion)
        cita = CITA_ASD_DE_LA_GLOBAL[codigo]
        formula = "FS_declarado  >=  FS minimo de E.050"
        sustitucion = (fs_mag,)
        descripcion = ("factor de seguridad minimo de E.050, "
                       + FS_NOMBRE_DE_LA_CONDICION[clave][condicion.value])
        aplicacion = ("EXIGENCIA de E.050 para edificaciones; el proyecto la "
                      "aplica al cabezal por analogia")
        numeral = f"{NUMERAL_9_3_ASD}; {FS_NUMERAL[clave]}"
        citas = ("AASHTO_LRFD_9.11.6.3.7#GLOBAL",)
        nota += ("Marco ASD (E.050, por analogia [N→]): la fila de la tabla "
                 "de Sec. 9.3.")
    else:
        citas = ("AASHTO_LRFD_9.C11.6.3.7#FS",
                 "AASHTO_LRFD_9.11.6.3.7#GLOBAL")
        formula = ("FS_declarado  >=  1/phi  (C11.6.3.7: phi es en esencia el "
                   "inverso del FS objetivo del programa de taludes)")
        if condicion is CondicionAnalisis.SISMICO:
            phi = PHI_EVENTO_EXTREMO_11_5_8["estabilidad_global"]
            cita = "AASHTO_LRFD_9.11.5.8#GLOBAL"
            origen_phi = (f"{NUMERAL_PHI_EVENTO_EXTREMO}: estabilidad global "
                          "del muro con sismo")
            aplicacion = ("EXIGENCIA de la fuente para muros, aplicada al "
                          "cabezal por la hipotesis de modelacion")
            numeral = f"{NUMERAL_9_3_LRFD}; {NUMERAL_PHI_EVENTO_EXTREMO}"
        else:
            fila = fila_phi_estabilidad_global()
            criterio = CRITERIO_FILA_PHI_GLOBAL
            cita = "AASHTO_LRFD_9.11.6.3.7#PHI"
            numeral = f"{NUMERAL_9_3_LRFD}; {NUMERAL_PHI_ESTABILIDAD_GLOBAL}"
            if fila is not None:
                phi = PHI_ESTABILIDAD_GLOBAL_11_6_3_7[fila]
                origen_phi = (f"{NUMERAL_PHI_ESTABILIDAD_GLOBAL}, fila "
                              f"'{fila}' ('{CRITERIO_FILA_PHI_GLOBAL}' [A])")
                aplicacion = (f"RECOMENDACION de la fuente con la fila que "
                              f"declaro el proyectista "
                              f"('{CRITERIO_FILA_PHI_GLOBAL}' = '{fila}')")
            else:
                # Sin la fila declarada se imprime la mas exigente (el
                # menor phi) y la fila solo decide si las dos dan lo mismo.
                phi = min(PHI_ESTABILIDAD_GLOBAL_11_6_3_7.values())
                phi_otra = max(PHI_ESTABILIDAD_GLOBAL_11_6_3_7.values())
                origen_phi = (f"{NUMERAL_PHI_ESTABILIDAD_GLOBAL}: fila NO "
                              f"DECIDIDA ('{CRITERIO_FILA_PHI_GLOBAL}' sin "
                              "valor); se imprime la mas exigente")
                aplicacion = (f"RECOMENDACION de la fuente con la fila NO "
                              f"DECIDIDA ('{CRITERIO_FILA_PHI_GLOBAL}' sin "
                              "valor: la declara el proyectista)")
                no_decidida = 1 / phi_otra
        admisible = 1 / phi
        sustitucion = (fs_mag, _m("phi", phi, "-", origen_phi))
        descripcion = ("inverso del factor de resistencia de la estabilidad "
                       "global, 1/phi")
        nota += ("Marco LRFD (AASHTO 11.6.3.7): el comentario C11.6.3.7 dice "
                 "que el factor de resistencia es en esencia el inverso del "
                 "FS que el programa de taludes debe alcanzar; el proyecto "
                 "toma 1/phi exacto (lectura declarada en la cita "
                 "AASHTO_LRFD_9.C11.6.3.7#FS). Que el analisis use la "
                 "combinacion de cargas que la fuente pide lo sostiene su "
                 "documento, no este programa.")
        if no_decidida is not None:
            cumple_otra = fs >= no_decidida - TOL_UMBRAL_NORMATIVO
            nota += (f" Fila de phi no decidida: con phi = {phi_otra:g} el "
                     f"minimo es {no_decidida:.3f} "
                     f"({'cumple' if cumple_otra else 'NO cumple'}); con phi "
                     f"= {phi:g}, {admisible:.3f}.")
    cumple = fs >= admisible - TOL_UMBRAL_NORMATIVO
    if (not cumple and decide and no_decidida is not None
            and fs >= no_decidida - TOL_UMBRAL_NORMATIVO):
        # --- VE-5 fixve4 (hallazgo 5 de la revision de la fusion) --- Entre
        # 1/0.75 y 1/0.65 el veredicto DEPENDE de la fila sin declarar, y el
        # marco LRFD decide: no hay fila que emitir. Hasta aqui salia
        # INDICADOR «no decidida» con `cumple` True y el codigo salia de
        # `pendientes`, que es rellenar el vacio con el lado favorable; un
        # INDICADOR es, por `EstadoDeVerificacion`, el de un [A] DECLARADO.
        # `ca.valor` levanta `CriterioPendienteError` (y registra el uso):
        # `_filas_globales_declaradas` la recoge, el codigo vuelve a
        # `pendientes` y el servicio la lleva como `Bloqueo` del punto.
        ca.valor(CRITERIO_FILA_PHI_GLOBAL)
    falla = (f"el factor de seguridad declarado no alcanza el minimo de "
             f"{nombre}")
    if cumple:
        tipo, texto = TipoDeVeredicto.CUMPLE, "cumple"
    elif not decide:
        tipo, texto = TipoDeVeredicto.INDICADOR, (
            falla + ". Este marco NO rige "
            f"('{CRITERIO_MARCO}' [A]): se informa y no detiene el punto")
    else:
        tipo, texto = TipoDeVeredicto.NO_CUMPLE, (
            falla + ": revisar el analisis con el geotecnista (geometria del "
            "terraplen, mejora del suelo o del desplante)")
    p = paso(
        "F9.GLOBAL_DECLARADA", codigo=f"{codigo}-{marco}.{sufijo}",
        que=(f"{codigo} ({marco}), {nombre}, con el FS declarado del "
             f"analisis externo: cabezal de {ext}, condicion "
             f"{condicion.value}"),
        formula=formula, sustitucion=sustitucion,
        resultado=_m("FS", fs, "-", procedencia),
        citas_textuales=(cita,) + citas,
        umbral=Umbral(descripcion=descripcion, valor=admisible, unidad="-",
                      cita_id=cita, caracter=_caracter_de(cita),
                      aplicacion=aplicacion,
                      criterio_aplicado=criterio),
        veredicto=Veredicto(tipo=tipo, margen=fs - admisible, unidad="-",
                            explicacion=texto),
        nota_del_proyecto=nota)
    return Verificacion(
        cumple=tipo is not TipoDeVeredicto.NO_CUMPLE,
        numeral=f"{numeral}, cabezal de {ext}", valor_obtenido=fs,
        valor_admisible=admisible,
        criterio_aplicado=criterio or CRITERIO_MARCO,
        codigo=f"{codigo}-{marco}.{sufijo}", paso=p)


def _filas_globales_declaradas(entorno: EntornoDelCabezal,
                               condicion: CondicionAnalisis, regla: str,
                               sufijo: str):
    """
    Las filas E4 y E5 de los dos marcos que el punto declaro, y -- VE-5
    fixve4 -- las que NO se pudieron decidir por un criterio sin valor:
    (filas, ((codigo, clave_del_criterio, motivo), ...)). Una fila que
    espera su criterio no se emite; la del otro marco, si.
    """
    declarada = entorno.estabilidad_global or {}
    filas, por_criterio = [], []
    for codigo in CODIGOS_GLOBALES:
        if codigo not in declarada:
            continue
        fs = declarada[codigo][condicion.value]
        for marco in (MARCO_LRFD, MARCO_ASD):
            try:
                filas.append(_fila_global_declarada(
                    entorno=entorno, condicion=condicion, codigo=codigo,
                    marco=marco, fs=fs,
                    traza=_traza_de_la_global(declarada),
                    decide=_decide(marco, regla), sufijo=sufijo))
            except CriterioPendienteError as exc:
                minimos = sorted(1 / phi for phi in
                                 PHI_ESTABILIDAD_GLOBAL_11_6_3_7.values())
                por_criterio.append((
                    codigo, exc.clave,
                    f"{marco}: el FS declarado ({fs:.3f}) queda entre "
                    f"{minimos[0]:.3f} (1/phi con parametros bien "
                    f"definidos) y {minimos[-1]:.3f} (1/phi con parametros "
                    "variables o limitados) de AASHTO 11.6.3.7, y el "
                    "veredicto depende de la fila de phi, sin declarar: "
                    f"declarar '{exc.clave}' con el EMS"))
    return tuple(sorted(filas, key=lambda v: v.codigo)), tuple(por_criterio)


def _paso_y_aviso_de_las_diferidas(entorno: EntornoDelCabezal,
                                   origen_suelo: str,
                                   pendientes: tuple):
    """
    El paso F9.GLOBAL y el aviso de lo que sigue diferido. Con E4 y E5
    pendientes, los textos de siempre (hasta VE-4a, los unicos); con una
    sola declarada, los de la otra.
    """
    codigos = [c for c, _ in pendientes]
    dos = len(codigos) == len(CODIGOS_GLOBALES)
    # --- VE-7 (dictamen Fable, decision 4) --- con aleros, lo diferido es
    # del cabezal Y de sus aleros (sus franjas tampoco tienen E4 ni E5).
    de_quien = ("del cabezal y de sus aleros"
                if entorno.geometria.aleros is not None else "del cabezal")
    if dos:
        que = (f"E4 y E5, estabilidad global y del talud {de_quien}: "
               f"cabezal de {entorno.extremo}")
        estado = "diferidas al expediente con el EMS"
        nota = ("No son un cumplimiento: el cabezal queda verificado en E1 "
                "a E3 y PENDIENTE en estas dos, que necesitan la "
                "estratigrafia completa y un analisis de superficies de "
                "falla.")
        aviso = (f"Cabezal de {entorno.extremo} de {entorno.id_punto}: E4 y "
                 "E5 (estabilidad global del muro y del talud) "
                 f"{de_quien} NO se "
                 "evaluan; quedan diferidas al expediente con el estudio de "
                 "suelos (AASHTO LRFD 11.6.3.7; E.050 39.13.6 b y Art. 30.3)")
    else:
        codigo = codigos[0]
        otro = next(c for c in CODIGOS_GLOBALES if c != codigo)
        que = (f"{codigo}, {NOMBRE_DE_LA_GLOBAL[codigo]} {de_quien}: "
               f"cabezal de {entorno.extremo}")
        estado = "diferida al expediente con el EMS"
        nota = (f"No es un cumplimiento: el cabezal queda verificado en E1 "
                f"a E3 y con el FS declarado en {otro}, y PENDIENTE en esta, "
                "que necesita la estratigrafia completa y un analisis de "
                "superficies de falla.")
        aviso = (f"Cabezal de {entorno.extremo} de {entorno.id_punto}: "
                 f"{codigo} ({NOMBRE_DE_LA_GLOBAL[codigo]}) {de_quien} NO "
                 "se evalua; "
                 "queda diferida al expediente con el estudio de suelos "
                 f"({NUMERAL_DE_LA_GLOBAL[codigo]}); {otro} se contrasta "
                 "con el FS declarado del analisis externo")
    p = paso(
        "F9.GLOBAL", codigo=f"9.3.g.{entorno.extremo[0]}", que=que,
        formula="FS de equilibrio limite >= FS minimo (no evaluado)",
        sustitucion=(Magnitud("suelo de fundacion", origen_suelo, "",
                              "lo que si se uso en E1 a E3"),),
        resultado=Magnitud(", ".join(codigos), estado, "",
                           "; ".join(m for _, m in pendientes)),
        nota_del_proyecto=nota)
    return p, aviso


def ensamble_estabilidad(entorno: EntornoDelCabezal,
                         condicion: CondicionAnalisis, *,
                         muro: str = MURO_CABEZAL,
                         fraccion_alero: float = 0
                         ) -> EstabilidadDelCabezal:
    """
    La estabilidad externa de UN cabezal en UNA condicion (INF-4.4, INF-4.5,
    INF-5.1.5): cargas sin factorar con sus brazos, combinaciones de los dos
    marcos, las verificaciones E1 a E3 de cada marco -- seis filas --, las
    solicitaciones factoradas por elemento y los pasos de memoria.

    DOS MARCOS QUE NO SE CRUZAN. El LRFD compara cargas factoradas con
    resistencias minoradas y la excentricidad con su limite; el ASD compara
    cargas de servicio con la resistencia nominal dividida por el factor de
    seguridad de E.050. Cual decide lo declara 'marco_estabilidad_cabezal'
    [A]: las verificaciones del marco que no decide salen como INDICADOR.

    SE DETIENE -- con `ErrorProyecto`, que el servicio registra como
    `Bloqueo` del punto -- en lo que falte: el angulo de friccion del relleno
    o los parametros del suelo de fundacion (criterios sin valor), la
    profundidad del freatico (columna vacia), la orientacion del muro frente
    al trafico ([S] sin leer) o, bajo sismo, Mononobe-Okabe fuera de su
    dominio de validez (`MetodoNoEvaluableError`).

    E4 y E5 no se CALCULAN: viajan en `pendientes`, con su motivo, salvo
    que el punto declare su factor de seguridad del analisis externo
    (`entorno.estabilidad_global`, VE-4a): entonces se contrastan en los dos
    marcos y van en `globales` (`_filas_globales_declaradas`).

    --- VE-7 (ficha VE7-01) --- Con `muro` = `MURO_ALERO` el `entorno` es la
    franja del arranque de los aleros (`estabilidad_del_alero`): las mismas
    filas, combinaciones, criterios y citas, con codigos `.alero` y rotulos
    del alero; no repite el paso de E4 y E5 diferidas ni los avisos del
    sitio, que ya dice el cabezal.
    """
    if condicion not in CONDICIONES_DE_ESTABILIDAD:
        raise DatoInvalidoError("condicion", valor=condicion,
                                motivo="estatico o sismico")
    if muro not in (MURO_CABEZAL, MURO_ALERO):
        raise DatoInvalidoError("muro", valor=muro,
                                motivo="el cabezal o la franja de su alero")
    es_alero = muro == MURO_ALERO
    g = entorno.geometria
    regla = _regla_de_marco()
    # --- VE-5 (ficha T7B-14) --- el muro que NO cede ya no se detiene aqui:
    # `cargas_del_cabezal` calcula sus presiones (11.6.5.4 y C11.6.5.4).
    suelo, origen_suelo = suelo_de_fundacion(entorno.suelo,
                                             id_punto=entorno.id_punto)
    cargas, datos = cargas_del_cabezal(entorno, condicion)
    combos = combinaciones_de_estabilidad(cargas, datos, condicion, g.B)
    sufijo = (f"{ABREVIATURA_DE_CONDICION[condicion]}.{entorno.extremo[0]}"
              + (sufijo_de_la_franja(fraccion_alero) if es_alero else ""))
    verificaciones = (
        _verificaciones_lrfd(entorno, datos, suelo, combos, condicion,
                             _decide(MARCO_LRFD, regla), sufijo)
        + _verificaciones_asd(entorno, datos, suelo, combos, condicion,
                              _decide(MARCO_ASD, regla), sufijo))
    verificaciones.sort(key=lambda v: v.codigo)
    pasos = _pasos_de_cargas(entorno, condicion, cargas, combos, datos,
                             sufijo)
    avisos = _avisos_de_sensibilidad(entorno, datos, suelo, combos,
                                     condicion, regla, sufijo,
                                     verificaciones)
    # --- VE-4a --- E4 y E5: lo DECLARADO se contrasta (`globales`) y sale
    # de `pendientes`; lo que no, sigue diferido con su paso y su aviso.
    declarada = entorno.estabilidad_global or {}
    pendientes = tuple(p for p in PENDIENTES_E4_E5 if p[0] not in declarada)
    globales, por_criterio = _filas_globales_declaradas(
        entorno, condicion, regla, sufijo)
    if condicion is CondicionAnalisis.ESTATICO and not es_alero:
        if pendientes:
            paso_global, aviso_global = _paso_y_aviso_de_las_diferidas(
                entorno, origen_suelo, pendientes)
            pasos.append(paso_global)
            avisos.append(aviso_global)
        if datos["drenaje"] == DRENAJE_SIN:
            # VE-3.16: el valor de archivo es 'drenado'; este aviso es el
            # del caso declarado. Hasta VE-3.16 decia ademas que la
            # condicion sismica no era evaluable, que dejo de ser cierto en
            # VE-3.14 (C11.6.5.3, peso total bajo el agua).
            avisos.append(
                f"Cabezal de {entorno.extremo} de {entorno.id_punto}: con el "
                f"trasdos sin drenaje ('{CRITERIO_DRENAJE}' = "
                f"'{DRENAJE_SIN}', declarado: el drenaje no puede darse), la "
                "estabilidad estatica se calcula con el relleno retenido "
                "lleno de agua hasta su superficie contra el trasdos (AASHTO "
                "11.6.6); bajo sismo el agua es la del nivel medio en el "
                "tiempo (C11.6.5.3), que la fuente no da para un relleno sin "
                "drenar y se declara en "
                f"'{CRITERIO_NIVEL_AGUA_SISMO}' [A] (la superficie del "
                "relleno o el freatico natural; sin declararla, la condicion "
                "sismica se detiene). El valor de "
                f"archivo ('{DRENAJE_CON}') lo deja en el freatico natural "
                "y compromete el filtro y los lloraderos en planos")
        else:
            avisos.append(_aviso_desembalse_rapido(entorno, datos, cargas))
        if suelo["cohesivo"]:
            avisos.append(
                f"Cabezal de {entorno.extremo} de {entorno.id_punto}: suelo "
                "de fundacion cohesivo; la resistencia al deslizamiento del "
                "marco LRFD supone al menos 6.0 in (0.15 m) de material "
                "granular compactado bajo la zapata (AASHTO 10.6.3.4), que "
                "tiene que estar en los planos")
    if not es_alero:
        avisos.extend(avisos_de_la_sobrecarga_del_punto(entorno))
        # --- dictamen Fable (VE-7 lote A, 5.7) --- el declarado que no se
        # usa (una vez por cabezal: el alero no lo repite).
        if datos.get("empuje_declarado_no_usado"):
            avisos.append(
                f"Cabezal de {entorno.extremo} de {entorno.id_punto}: "
                f"`{DATO_EMPUJE_SISMICO}` declarado y NO usado: el programa "
                "calcula el empuje (el declarado solo entra donde el ensamble "
                "no puede calcularlo; ficha VE7A-05)")
    # --- VE-5 fixve4 --- lo declarado que su criterio sin valor no deja
    # decidir VUELVE a `pendientes`, con el motivo, y viaja aparte para que
    # el servicio lo lleve como `Bloqueo` (CriterioPendienteError).
    # --- VE-7 (dictamen Fable, decision 4) --- el FS declarado de E4/E5 es
    # del cabezal: cubre los aleros solo si el analisis externo los incluyo.
    if globales and not es_alero and g.aleros is not None:
        avisos.append(
            f"Cabezal de {entorno.extremo} de {entorno.id_punto}: el FS "
            "declarado de E4/E5 cubre los aleros solo si el analisis externo "
            "incluyo su seccion; el programa no lo comprueba")
    for codigo, clave, motivo in por_criterio:
        pendientes += ((codigo, motivo),)
        avisos.append(
            f"Cabezal de {entorno.extremo} de {entorno.id_punto}: {codigo} "
            f"({NOMBRE_DE_LA_GLOBAL[codigo]}), condicion {condicion.value}, "
            f"queda PENDIENTE de '{clave}' [A]: {motivo}")
    estabilidad = EstabilidadDelCabezal(
        id_punto=entorno.id_punto, extremo=entorno.extremo,
        condicion=condicion, regla_de_marco=regla, cargas=cargas,
        combinaciones=combos, verificaciones=tuple(verificaciones),
        solicitaciones=solicitaciones_por_elemento(entorno, cargas, combos,
                                                   datos),
        pasos=tuple(pasos), avisos=tuple(avisos),
        pendientes=pendientes, K_A=datos["K_A"], K_AE=datos["K_AE"],
        i_grados=datos["angulos"]["i"], delta_grados=datos["angulos"]["delta"],
        altura_empuje=datos["h"], h_eq=datos["h_eq"], k_h=datos["k_h"],
        metodo_empuje=datos["metodo_empuje"],
        K_A_contraste=(datos["K_A_formula"] if datos["metodo_empuje"]
                       == METODO_EMPUJE_CUNA else None),
        K_AE_contraste=(datos["K_AE_formula"] if datos["metodo_empuje"]
                        == METODO_EMPUJE_CUNA else None),
        regimen=datos["regimen"], K0=datos["K0"], globales=globales,
        pendientes_por_criterio=tuple((codigo, clave)
                                      for codigo, clave, _ in por_criterio))
    return (_rotular_como_alero(estabilidad, fraccion_alero) if es_alero
            else estabilidad)


def _sin_parar(calculo):
    """
    El contraste de sensibilidad no detiene el ensamble: si con la otra
    opcion algo no se puede evaluar, ese contraste se omite (devuelve None).
    """
    try:
        return calculo()
    except ErrorProyecto:
        return None


def _aviso_desembalse_rapido(entorno: EntornoDelCabezal, datos: dict,
                             cargas: tuple) -> str:
    """
    El aviso que acompaña al drenaje DECLARADO (correcciones de T-7b, H6):
    el modelo toma el agua del relleno en el freatico natural y NO el
    desembalse rapido tras la avenida -- el relleno mojado hasta la cota del
    agua de diseño con el cauce ya vacio --, que el comentario C11.6.6 hace
    plausible al advertir que los lloraderos no aseguran el drenaje. Con el
    nivel de diseño conocido da el orden de magnitud: la hidrostatica que
    ese relleno mojado ejerceria contra la componente horizontal del empuje.
    """
    base = (f"Cabezal de {entorno.extremo} de {entorno.id_punto}: con el "
            f"drenaje del trasdos declarado ('{CRITERIO_DRENAJE}' = "
            f"'{DRENAJE_CON}') el agua del relleno se toma en el freatico "
            "natural; el modelo NO contempla el desembalse rapido -- el "
            "relleno mojado por la avenida con el cauce ya vacio -- y la "
            "fuente advierte que los lloraderos solos no aseguran el drenaje "
            "(AASHTO C11.6.6)")
    if datos["cota_agua_diseno"] is None:
        return base
    h_av = min(max(datos["cota_agua_diseno"]
                   - entorno.geometria.cota_desplante, 0.0), datos["z_rel"])
    E_av = GAMMA_AGUA_KN_M3 * h_av ** 2 / 2
    EH = sum(c.H for c in cargas if c.codigo == C_EH_H)
    return (base + f". Orden de magnitud: con el relleno mojado hasta la "
            f"cota del agua de diseño ({datos['cota_agua_diseno']:.2f} msnm, "
            f"{h_av:.2f} m sobre la base) la hidrostatica seria del orden de "
            f"gamma_w·h²/2 = {E_av:.1f} kN/m, frente a {EH:.1f} kN/m de la "
            "componente horizontal del empuje del suelo")


def _avisos_de_sensibilidad(entorno, datos, suelo, combos, condicion, regla,
                            sufijo, verificaciones) -> List[str]:
    """
    Las filas cuyo VEREDICTO cambia entre las opciones de la ventana de las
    dos elecciones [A] que mas mueven la estabilidad (correcciones de T-7b,
    H5): la fila de phi ('fila_phi_estabilidad_cabezal', solo en la
    estatica: bajo sismo phi es del 11.5.8 y no se elige) y los factores de
    inclinacion de la carga en el portante
    ('factores_inclinacion_carga_portante', en las dos condiciones y en los
    dos marcos). Cada aviso dice la fila, las dos opciones y las dos cifras:
    un incumplimiento que se invierte dentro de la ventana es SENSIBLE a una
    eleccion, no un hecho del cabezal.
    """
    actual = {v.codigo: v for v in verificaciones}
    fila_actual = ca.valor(CRITERIO_FILA_PHI)
    inclinacion_actual = ca.valor(CRITERIO_INCLINACION_PORTANTE)
    contrastes = []
    if condicion is CondicionAnalisis.ESTATICO:
        for fila in FILAS_DE_PHI:
            if fila != fila_actual:
                contrastes.append((CRITERIO_FILA_PHI, fila_actual, fila,
                                   _sin_parar(lambda f=fila: _verificaciones_lrfd(
                                       entorno, datos, suelo, combos,
                                       condicion, _decide(MARCO_LRFD, regla),
                                       sufijo, fila=f))))
    for opcion in (INCLINACION_APLICAR, INCLINACION_OMITIR):
        if opcion != inclinacion_actual:
            contrastes.append((CRITERIO_INCLINACION_PORTANTE,
                               inclinacion_actual, opcion,
                               _sin_parar(lambda o=opcion: _verificaciones_lrfd(
                                   entorno, datos, suelo, combos, condicion,
                                   _decide(MARCO_LRFD, regla), sufijo,
                                   inclinacion=o)
                                   + _verificaciones_asd(
                                   entorno, datos, suelo, combos, condicion,
                                   _decide(MARCO_ASD, regla), sufijo,
                                   inclinacion=o))))

    def cifra(v) -> str:
        if v.valor_obtenido is None or v.valor_admisible is None:
            return "sin cifra"
        return (f"{v.valor_obtenido:.2f} contra {v.valor_admisible:.2f} "
                f"({'cumple' if v.cumple else 'no cumple'})")

    avisos = []
    for criterio, de_archivo, otra, alternativas in contrastes:
        if alternativas is None:
            continue
        for v in alternativas:
            base = actual.get(v.codigo)
            if base is None or base.cumple == v.cumple:
                continue
            avisos.append(
                f"Cabezal de {entorno.extremo} de {entorno.id_punto}, "
                f"condicion {condicion.value}: {v.codigo} CAMBIA DE "
                f"VEREDICTO dentro de la ventana de '{criterio}' [A]: con "
                f"'{de_archivo}' {cifra(base)}; con '{otra}' {cifra(v)}. El "
                "veredicto es sensible a esa eleccion")
    return avisos


def datos_del_cabezal_del_punto(*, punto, cabezal: CabezalDelPunto,
                                geometria, socavacion=None,
                                suelo_del_punto: Optional[dict] = None,
                                resultado=None,
                                estabilidad_global: Optional[dict] = None,
                                empuje_sismico: Optional[dict] = None,
                                talud_delante: Optional[dict] = None
                                ) -> Tuple[EntornoDelCabezal, EntornoDelCabezal]:
    """
    Los dos `EntornoDelCabezal` de un punto (entrada y salida), leidos de lo
    que la Fase 9 de T-7a ya resolvio y de 7.B, sin decidir nada otra vez:
    el relleno retenido llega a la coronacion menos el bordillo; el talud y
    el borde de la plataforma de cada lado son los de la longitud por
    extremo de 7.B (o, si la longitud se declaro, el criterio
    'talud_terraplen' y la rasante en el eje); el freatico, la columna del
    CSV; el terreno del pie, el de la geometria del cabezal; y la hoya de
    socavacion, la que la Fase 6 entrego para la salida (`socavacion`, la
    misma que `extremos_del_conducto` leyo para el desplante).

    EL FREATICO VIAJA COMO COTA (correcciones de T-7b, H1): la columna
    NF_profundidad_m se mide bajo el terreno natural del CRUCE
    (`punto.cota_terreno`), como en M8, en el censo de `variables_entrada` y
    en el contrato de entradas, y la cota es la misma para los dos cabezales.
    La FASE A la medía bajo el pie de cada cabezal, y en la salida de A-01
    dejaba el agua 0.80 m mas baja que donde esta.

    Con `resultado` (el `ResultadoPunto` de la Fase 4) el entorno lleva
    tambien el nivel del agua de diseño contra cada cabezal, el mismo de
    `extremos_del_conducto`: solo lo lee el aviso del desembalse rapido.
    --- VE-4a --- Con `estabilidad_global` (el dato externo
    `estabilidad_global_declarada` del punto, ya validado y normalizado) cada
    entorno lleva el bloque de SU extremo: el FS declarado de E4 y E5 que el
    ensamble contrasta. Sin el, E4 y E5 siguen diferidas.
    """
    reglas = _reglas()
    nf = punto.NF_profundidad_m
    if nf is None:
        cota_freatico, origen_nf = None, ""
    else:
        _exigir_finito("NF_profundidad_m", nf, "profundidad del nivel "
                       "freatico", punto.id)
        _exigir_finito("cota_terreno", punto.cota_terreno, "terreno del "
                       "cruce", punto.id)
        cota_freatico = punto.cota_terreno - nf
        origen_nf = (f"cota_terreno - NF_profundidad_m = "
                     f"{punto.cota_terreno:.3f} - {nf:.3f}: el freatico se "
                     "mide bajo el terreno natural del cruce (columna del "
                     "CSV, del EMS), la misma cota para los dos cabezales")
    agua_de = {}
    if resultado is not None:
        for x in extremos_del_conducto(punto=punto, resultado=resultado,
                                       geometria=geometria,
                                       socavacion=socavacion):
            agua_de[x.extremo] = x.cota_agua
    bordillo = reglas["bordillo_m"]
    calculada = geometria.longitud_calculada
    talud = (calculada.talud if calculada is not None
             and calculada.talud is not None
             else ca.valor(CRITERIO_TALUD_TERRAPLEN))
    entornos = []
    for g in cabezal.geometrias:
        es_entrada = g.extremo == EXTREMO_ENTRADA
        borde = None
        if calculada is not None:
            borde = (calculada.cota_borde_entrada if es_entrada
                     else calculada.cota_borde_salida)
        if borde is not None:
            origen = "borde de la plataforma de ese lado, de 7.B"
        else:
            borde = punto.cota_rasante
            origen = ("rasante en el eje (columna cota_rasante): 7.B no "
                      "calculo el borde de la plataforma")
        entornos.append(EntornoDelCabezal(
            id_punto=punto.id, extremo=g.extremo, geometria=g,
            cota_relleno=g.cota_coronacion - bordillo,
            cota_borde_plataforma=borde, origen_cota_borde=origen,
            talud=talud, esviaje_grados=punto.esviaje_grados,
            cota_freatico=cota_freatico, origen_freatico=origen_nf,
            cota_pie=g.losa.cota_terreno if g.losa is not None
            else g.cota_desplante + g.D_f,
            cota_fondo_hoya=(None if es_entrada or socavacion is None
                             else socavacion.cota_fondo_de_la_hoya),
            suelo=suelo_del_punto,
            cota_agua_diseno=agua_de.get(g.extremo),
            estabilidad_global=(estabilidad_global or {}).get(g.extremo)
            or None,
            # --- VE-7 (lote A, A5) --- el P_AE declarado de ESTE cabezal.
            empuje_sismico=(empuje_sismico or {}).get(g.extremo) or None,
            # --- VE-7 (lote A, A6) --- el talud de delante de ESTE cabezal.
            talud_delante=(talud_delante or {}).get(g.extremo) or None,
            # --- VE-7 (lote A, A7) --- el muro paralelo a la via (Carta 11)
            # es paralelo al trafico: lo lee la sobrecarga viva.
            paralelo_a_la_via=_embocadura_paralela_del_cabezal(cabezal)))
    return tuple(entornos)


def integrar_estabilidad(cabezal: CabezalDelPunto,
                         estabilidades: Sequence[EstabilidadDelCabezal]
                         ) -> CabezalDelPunto:
    """
    El `CabezalDelPunto` con la estabilidad de sus cabezales incorporada:
    las verificaciones E1 a E3 -- y las E4 y E5 con FS declarado (VE-4a,
    `EstabilidadDelCabezal.globales`) -- se suman a las CB (la via por la que
    `InformePunto` cuenta incumplidas e indicadores), los pasos y los avisos
    a los suyos, y los objetos enteros quedan en `estabilidad`.
    """
    from dataclasses import replace as _replace
    estabilidades = tuple(estabilidades)
    avisos = list(cabezal.avisos)
    for e in estabilidades:
        avisos.extend(a for a in e.avisos if a not in avisos)
    # --- correcciones de T-7b (H8) --- un cabezal con SOLO UNA de las dos
    # condiciones evaluadas se avisa: la otra quedo como `Bloqueo` del punto
    # y la tabla del cabezal no puede leerse como completa.
    for g in cabezal.geometrias:
        evaluadas = [e.condicion for e in estabilidades
                     if e.extremo == g.extremo]
        if len(evaluadas) == 1:
            falta = next(c for c in CONDICIONES_DE_ESTABILIDAD
                         if c not in evaluadas)
            avisos.append(
                f"Cabezal de {g.extremo} de {cabezal.id_punto}: su "
                f"estabilidad se evaluo SOLO en la condicion "
                f"{evaluadas[0].value}; la {falta.value} quedo sin evaluar "
                "(ver «Etapas bloqueadas»): E1 a E3 de ese cabezal no estan "
                "completas")
    return _replace(
        cabezal,
        verificaciones=cabezal.verificaciones + tuple(
            v for e in estabilidades for v in e.verificaciones + e.globales),
        pasos=cabezal.pasos + tuple(p for e in estabilidades
                                    for p in e.pasos),
        avisos=tuple(avisos), estabilidad=estabilidades)


def _carga_lineal_sobre_un_tramo(x0: float, x1: float, s0: float, s1: float,
                                 a: float, b: float, x_ref: float
                                 ) -> Tuple[float, float]:
    """
    La resultante de una carga repartida LINEAL -- s0 en x0, s1 en x1 -- sobre
    el tramo [a, b] (recortado a [x0, x1]), y su momento respecto de x_ref
    (resultante por la distancia de su centro de gravedad a x_ref).
    """
    p, q = max(a, x0), min(b, x1)
    if not q > p or not x1 > x0:
        return 0.0, 0.0
    k = (s1 - s0) / (x1 - x0)
    sp, sq = s0 + k * (p - x0), s0 + k * (q - x0)
    F = (sp + sq) / 2 * (q - p)
    if not F > 0:
        return 0.0, 0.0
    x_c = p + (q - p) * (sp + 2 * sq) / (LADOS_DEL_TRIANGULO * (sp + sq))
    return F, F * abs(x_c - x_ref)
