"""
tests/apoyo/sensibilidad.py
===========================
El BARRIDO DE SENSIBILIDAD de T-11 (punto 3 del prompt): cada criterio [A]
o [C] que gobierna el diametro o el cabezal se barre sobre SU ventana con
`src/barrido.py` (PF-3: una clave a la vez, la misma puerta que la pestaña 2,
ninguna corrida hereda de la anterior, la comparacion es la del comparador
de E-B) sobre el JUEGO DE DATOS DE PRUEBA de la validacion integral
(`tests/fixtures/juego_validacion_integral.py`), y GENERA
`docs/validacion_sensibilidad.md`. `tests/test_t11_sensibilidad.py` lo
regenera a memoria y lo compara, de modo que el anexo no se puede
desincronizar del programa.

Regenerar::

    python -m tests.apoyo.sensibilidad --escribir

LOS JUICIOS, ESCRITOS AQUI PARA QUE SE PUEDAN AUDITAR
-----------------------------------------------------
1. QUE SE BARRE. Desde las correcciones de T-11 (H3 de su auditoria) la
   lista SE DERIVA DEL CENSO: `BARRIDOS` = los escritos a mano
   (`BARRIDOS_A_MANO`: los de PRECISIONES_T-11 y los que necesitan valores
   propios --la seccion del receptor, un opcional sin valor, un valor
   intermedio, una ventana en prosa--) MAS todo criterio con valor efectivo
   en el juego y ventana legible por maquina (`barribles_del_censo`: una
   categoria cerrada o dos extremos numericos). Lo que queda fuera esta en
   `NO_BARRIBLES` con su razon, POR NOMBRE, y un test exige que la particion
   sea exacta: ningun criterio queda sin decir si se barrio o por que no.
2. CON QUE VALORES. El PRIMER valor es el EFECTIVO en el juego (el que el
   juego declara o, si no declara nada, el del archivo): la corrida del
   primer valor ES la corrida completa de la validacion integral, y cada
   otra se compara con ella. Los demas son los extremos de la ventana
   (`Criterio.sensibilidad`): para una ventana numerica, sus dos extremos;
   para una categoria, las demas opciones; para la seccion del receptor, la
   seccion mas estrecha y lenta y la mas ancha y rapida que la ventana
   admite. Un criterio OPCIONAL sin valor (`v_max_concreto_eleccion`) no
   tiene «efectivo»: se barren sus dos extremos y el primero es la
   referencia, y se dice.
3. QUE ES «MOVER». Por (valor, punto), contra el primer valor: «mueve el
   diseño» si cambia el material o la seccion, o si el punto deja de
   dimensionar o empieza a hacerlo; «mueve veredictos» si cambia el
   veredicto de alguna verificacion (conducto, cabezal y Fase 10: la
   columna del comparador, que cuenta tambien la que aparece o desaparece);
   «mueve el HW» si solo cambia la carga que gobierna en mas de
   `TOL_HW_SENSIBILIDAD_M` (antes con `!=` exacto: una longitud que movia
   el HW en 3e-6 m lo «movia»). «Leido, sin efecto medible» quiere decir
   eso y NADA MAS: no compara las otras magnitudes (la hoya de socavacion,
   el espesor de la proteccion, las longitudes, los margenes, el armado),
   que pueden cambiar. «No lo lee la corrida» si la clave no esta
   entre los criterios usados de NINGUNA de sus corridas: entonces barrerla
   no puede mover nada, y la razon de que no se lea esta escrita en
   `NO_LEIDO_PORQUE` --- un test exige que esa lista coincida con la medida,
   en los dos sentidos.

Lo que este modulo NO hace: no calcula (lee los volcados del barrido), no
escribe en `src/` y no deja nada declarado: cada barrido parte del estado
vacio de declaraciones y lo repone al salir.
"""

from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cli
from src import barrido
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import servicio
from tests.apoyo import validacion_integral as V
from tests.fixtures import juego_validacion_integral as J

RAIZ = Path(__file__).resolve().parents[2]
DOCUMENTO = RAIZ / "docs" / "validacion_sensibilidad.md"

NOTA = ("barrido de sensibilidad de la validacion integral de T-11 sobre DATOS "
        "DE PRUEBA, NO DEL PROYECTO: el valor recorre la ventana del criterio")

GRUPO_CONDUCTO = "conducto"
GRUPO_CABEZAL = "cabezal"
GRUPO_PROTECCION = "protección"
GRUPO_CUNETA = "cuneta"
GRUPO_HIDROLOGIA = "hidrología"
GRUPO_SIN_CONSUMIDOR = "sin consumidor"

# La carga que gobierna «se mueve» si cambia en mas de esto: media unidad de
# la cuarta cifra decimal con que el anexo la imprime. Precision de lectura,
# no un valor de proyecto (correcciones de T-11, H3: con `!=` exacto,
# `metodo_longitud_conducto` «movia» el HW de C-01 en 3e-6 m).
TOL_HW_SENSIBILIDAD_M = 5e-5

# La seccion del receptor mas estrecha y lenta y la mas ancha y rapida que la
# ventana de `seccion_receptor` admite (cada campo en su extremo).
SECCION_ESTRECHA = {"b_m": 1.5, "z_HV": 1.0, "S": 0.0005, "n": 0.035,
                    "altura_total_m": 1.2}
SECCION_ANCHA = {"b_m": 3.0, "z_HV": 2.0, "S": 0.0015, "n": 0.025,
                 "altura_total_m": 2.5}

# Las bases sobre las que se barre: el juego completo, o el juego con un
# cambio (la forma de `J.VARIANTES`).
BASES: Dict[str, Tuple[str, Tuple[Tuple[Any, ...], ...]]] = {
    "juego": ("el juego completo", ()),
    "juego_sin_TW": ("el juego sin `TW_m` (el TW sale de la vía 4 de la Sec. "
                     "1.3, los escenarios acotados con la sección del receptor)",
                     (("externo", "globales", "TW_m", None),)),
    # Correcciones de T-11 (H6): el resultado de `v_max_concreto_eleccion`
    # con el TMC excluido por los sulfatos del juego.
    "juego_tmc_excluida": ("el juego con `suelo_agresivo_lrfd_sobre_tmc` = "
                           "'excluye' (dentro de su ventana): el TMC queda "
                           "fuera por los sulfatos del juego (500 ppm > 200)",
                           (("declarar", "suelo_agresivo_lrfd_sobre_tmc",
                             "excluye"),)),
}


@dataclass(frozen=True)
class Barrido:
    clave: str
    grupo: str
    por_que: str                      # por que esta en la lista
    base: str = "juego"
    valores: Tuple[Any, ...] = ()     # vacio: se derivan de la ventana


BARRIDOS_A_MANO: Tuple[Barrido, ...] = (
    # --- los que gobiernan el diametro (PRECISIONES_T-11) ---------------
    Barrido("HW_D_max", GRUPO_CONDUCTO, "tope de V4b (PRECISIONES)"),
    Barrido("borde_libre_bajo_tw_ahogante", GRUPO_CONDUCTO,
            "lectura de V1 cuando el receptor llena la sección (PRECISIONES)"),
    Barrido("seccion_receptor", GRUPO_CONDUCTO,
            "sección adoptada del receptor (PRECISIONES), con el TW del juego"),
    Barrido("seccion_receptor", GRUPO_CONDUCTO,
            "sección adoptada del receptor (PRECISIONES), con el TW por la "
            "vía 4", base="juego_sin_TW"),
    Barrido("v_max_tmc", GRUPO_CONDUCTO, "techo de V3 del TMC (PRECISIONES)"),
    Barrido("v_max_hdpe", GRUPO_CONDUCTO, "techo de V3 del HDPE (PRECISIONES)"),
    Barrido("v_max_concreto_eleccion", GRUPO_CONDUCTO,
            "techo de V3 del concreto, opcional (PRECISIONES)",
            valores=(3.0, 6.0)),
    Barrido("v_max_concreto_eleccion", GRUPO_CONDUCTO,
            "techo de V3 del concreto con el TMC excluido por los sulfatos "
            "(correcciones de T-11, H6: el resultado de 3.0 m/s depende de "
            "`suelo_agresivo_lrfd_sobre_tmc`)",
            base="juego_tmc_excluida", valores=(3.0, 6.0)),
    Barrido("regimen_v2b", GRUPO_CONDUCTO,
            "régimen del indicador de V2b (PRECISIONES)"),
    Barrido("hw_entrada_fuera_de_rango", GRUPO_CONDUCTO,
            "carga de entrada fuera del rango de la corrección (PRECISIONES)"),
    Barrido("n_manning_cajon", GRUPO_CONDUCTO,
            "doble n del marco (PRECISIONES). Se barre la alternativa de "
            "TABLA (n menor); el lado ALTO de la ventana, el num. B.3 del "
            "HDS-5 (0.012 a 0.022 en un cajón vaciado in situ), NO SE MIDIÓ: "
            "la ficha dice que se declara «como el par de la especificación "
            "del encofrado», y la puerta lo rechaza (la forma del criterio es "
            "`str`). C-01 lo gobierna la salida, que es donde n pesa"),
    Barrido("espesor_pared_cajon", GRUPO_CONDUCTO,
            "espesor de pared del marco (correcciones de T-11, H3); la "
            "ventana está en prosa (0.20 a 0.30 m, ficha T3-08)",
            valores=(0.20, 0.25, 0.30)),
    # --- los que T-11 añadio por gobernar una fila de la Fase 5 ---------
    Barrido("borde_libre_y_sobre_d_max", GRUPO_CONDUCTO,
            "umbral de V1, sólo endurecible (T-11). Se barre además un valor "
            "intermedio (0.6): el extremo inferior de la ventana (0.0) no lo "
            "cumple ningún conducto con caudal",
            valores=(0.75, 0.6, 0.0)),
    Barrido("ke_entrada", GRUPO_CONDUCTO,
            "pérdida de entrada del tubo en el control de salida (T-11)"),
    Barrido("embocadura_cabezal", GRUPO_CONDUCTO,
            "tipo de embocadura del punto: carta, ke y cabezal (T-11)"),
    Barrido("fraccion_llena_mayor_parte", GRUPO_CONDUCTO,
            "regla del perfil de la lámina, «la mayor parte» lleno (T-11)"),
    Barrido("instalacion_estandar_concreto", GRUPO_CONDUCTO,
            "instalación del tubo de concreto en la Fase 8 (T-11)"),
    Barrido("carga_viva_bajo_relleno_alto", GRUPO_CONDUCTO,
            "carga viva pasados 8 ft de relleno en la Fase 8 (T-11)"),
    Barrido("eta_importancia_operativa_conducto", GRUPO_CONDUCTO,
            "el η del cruce: Fase 8 y combinaciones del cabezal "
            "(PRECISIONES)"),
    # --- los del cabezal (PRECISIONES_T-11) ----------------------------
    Barrido("factor_muro_eleccion", GRUPO_CABEZAL,
            "reducción de k_h por desplazamiento (PRECISIONES)"),
    Barrido("gamma_EQ", GRUPO_CABEZAL,
            "factor de la carga viva en el Evento Extremo I (PRECISIONES)"),
    Barrido("fraccion_delta_sobre_phi_trasdos", GRUPO_CABEZAL,
            "fricción del trasdós δ/φ (PRECISIONES)"),
    Barrido("fila_phi_estabilidad_cabezal", GRUPO_CABEZAL,
            "fila de φ de la estabilidad LRFD (PRECISIONES)"),
    Barrido("factores_inclinacion_carga_portante", GRUPO_CABEZAL,
            "factores de inclinación de la capacidad portante (PRECISIONES)"),
    Barrido("regla_pendiente_relleno_trasdos", GRUPO_CABEZAL,
            "superficie del relleno para el empuje (PRECISIONES)"),
    Barrido("regimen_resistencia_elementos_cabezal", GRUPO_CABEZAL,
            "empuje con que se arman los elementos (PRECISIONES)"),
    # --- los que T-11 añadio del cabezal ---------------------------------
    Barrido("eta_ductilidad_cabezal", GRUPO_CABEZAL, "η_D del cabezal (T-11)"),
    Barrido("eta_redundancia_cabezal", GRUPO_CABEZAL,
            "η_R del cabezal (T-11)"),
    Barrido("marco_estabilidad_cabezal", GRUPO_CABEZAL,
            "cuál marco de estabilidad rige (T-11)"),
    Barrido("regimen_cabezal", GRUPO_CABEZAL,
            "muro que cede o que no cede en la estabilidad (T-11)"),
    Barrido("drenaje_trasdos", GRUPO_CABEZAL,
            "trasdós drenado o no (T-11)"),
    Barrido("fc_cabezal_mpa", GRUPO_CABEZAL,
            "resistencia del concreto del cabezal (T-11)"),
    Barrido("duracion_caudal_pico_socavacion_min", GRUPO_CABEZAL,
            "duración del pico para la hoya de socavación, que baja el "
            "desplante del cabezal de salida (T-11)"),
)

def _efectivo(clave: str) -> Any:
    return J.DECLARACIONES.get(clave, ca.criterio(clave).valor)


def ventana_legible(clave: str) -> Optional[Tuple[Any, ...]]:
    """
    Los OTROS valores de la ventana de un criterio, si es legible por
    maquina: una categoria cerrada (las demas opciones) o una ventana
    numerica de dos extremos (los dos). None si no lo es.
    """
    c = ca.criterio(clave)
    s = c.sensibilidad
    efectivo = _efectivo(clave)
    if c.forma == "categoria" and isinstance(s, tuple) and s and \
            all(isinstance(x, str) for x in s):
        return tuple(v for v in s if v != efectivo)
    if c.forma in ("float", "int") and isinstance(s, tuple) and len(s) == 2 \
            and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                    for x in s):
        return tuple(type(efectivo)(v) for v in s)
    return None


def barribles_del_censo() -> Tuple[str, ...]:
    """
    Todo criterio con valor efectivo en el juego (el que el juego declara o
    el de archivo) y ventana legible por maquina, en el orden del archivo.
    """
    return tuple(k for k in ca.CRITERIOS
                 if _efectivo(k) is not None and ventana_legible(k))


def _grupo(clave: str) -> str:
    from src import variables_entrada as ve
    modulos = set(ve.variable(clave).consumido_por)
    if modulos & {"M2_material", "M3_hidraulica", "M4_control",
                  "M5_verificaciones", "M7_geometria", "M8_estructural", "MD"}:
        return GRUPO_CONDUCTO
    if "M9_cabezal" in modulos:
        return GRUPO_CABEZAL
    if "M6_proteccion" in modulos:
        return GRUPO_PROTECCION
    if "M10_espaciamiento" in modulos:
        return GRUPO_CUNETA
    if "MH_hidrologia" in modulos:
        return GRUPO_HIDROLOGIA
    return GRUPO_SIN_CONSUMIDOR


POR_QUE_DERIVADO = ("derivado del censo (valor efectivo y ventana legible "
                    "por máquina; correcciones de T-11, H3)")

BARRIDOS: Tuple[Barrido, ...] = BARRIDOS_A_MANO + tuple(
    Barrido(k, _grupo(k), POR_QUE_DERIVADO) for k in barribles_del_censo()
    if k not in {b.clave for b in BARRIDOS_A_MANO})

# LOS QUE NO SE BARREN, POR NOMBRE Y CON SU RAZON (correcciones de T-11,
# H3). El test exige que `BARRIDOS` y esta tabla partan el censo entero.
_R_SIN_VALOR = ("sin valor de archivo y el juego no lo declara: no hay "
                "valor efectivo desde el que barrer")
_R_OPCIONAL = ("[A] OPCIONAL sin valor: sin declararlo rige la regla escrita "
               "en su ficha; el juego no lo declara")
_R_ENSAYO = ("dato de ensayo o de sitio, sin ventana: se declara con su "
             "trazabilidad, no se elige")
_R_TABLA = ("su valor es una fila o un conjunto de filas de una tabla "
            "(forma estructurada) y la ventana, si la hay, va por fila o en "
            "prosa: no es legible por máquina")
_R_POR_CAMPO = ("ventana POR CAMPO de un dict: barrerlo exige elegir una "
                "esquina por campo, y no se hizo (NO SE MIDIÓ)")
_R_DERIVADA = "Derivada de otros criterios o del registro: no se declara"
_R_ANALOGIA = ("valor de una fuente ([N→] o [C]) sin ventana: no hay rango "
               "que barrer")
_R_PROSA = ("ventana en prosa (un piso o una regla, sin dos extremos): no "
            "es legible por máquina y no se barrió (NO SE MIDIÓ)")
_R_SIN_CONSUMIDOR = ("sin consumidor "
                     "(`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`)")

NO_BARRIBLES: Dict[str, str] = {
    "PERFIL_SUELO_PRESUNTO": _R_ENSAYO + "; " + _R_SIN_CONSUMIDOR,
    "clase_sitio": _R_SIN_VALOR + "; " + _R_ENSAYO + "; " + _R_SIN_CONSUMIDOR,
    "F_pga": _R_TABLA,
    "k_v": ("forma compuesta (categoria o numero) con la ventana en prosa: "
            + _R_PROSA),
    "pendiente_relleno_trasdos_i": _R_OPCIONAL,
    "friccion_muro_suelo_delta": _R_OPCIONAL,
    "riesgo_admisible_propietario": _R_OPCIONAL,
    "coeficiente_escorrentia_superficie_vial": _R_DERIVADA,
    "hds5_embocadura_hdpe": _R_TABLA,
    "metodo_transicion_hds5": _R_ANALOGIA,
    "n_manning_hdpe": _R_TABLA,
    "geometria_control_salida": _R_ANALOGIA,
    "velocidad_minima_autolimpieza_m_s": (
        "sólo endurecible por encima de 0.25 m/s, sin techo: " + _R_PROSA),
    "resguardo_HW_subrasante": _R_ANALOGIA,
    "TW_receptor": (_R_SIN_VALOR + "; dato del receptor (ANA / Junta), y con "
                    "la sección de archivo de `seccion_receptor` nunca se lee"),
    "seccion_cuneta": _R_POR_CAMPO,
    "TR_evento_extremo": ("el juego lo declara (500 años) pero la ficha no "
                          "tiene ventana: el TR del evento extremo lo fija el "
                          "Propietario con el estudio hidrológico"),
    "c_phi_fundacion": _R_ENSAYO,
    "capacidad_portante_adm": (_R_SIN_VALOR + "; " + _R_ENSAYO + "; "
                               + _R_SIN_CONSUMIDOR),
    "Mw_licuefaccion": (_R_SIN_VALOR + "; " + _R_ENSAYO + "; "
                        + _R_SIN_CONSUMIDOR),
    "diametros_normalizados": _R_TABLA,
    "secciones_cajon_normalizadas": _R_TABLA,
    "embocadura_cajon": _R_TABLA,
    "n_celdas_cajon": _R_PROSA,
    "ke_entrada_cajon": _R_TABLA,
    "D_max_catalogo": _R_OPCIONAL,
    "cobertura_minima_aashto": _R_TABLA,
    "cobertura_minima_cajon": _R_PROSA,
    "h_eq_bajo_altura_tabulada": (_R_SIN_VALOR + "; condicional que el juego "
                                  "no dispara (muro de menos de 1.524 m)"),
    "h_eq_banda_intermedia_borde": (_R_SIN_VALOR + "; condicional que el juego "
                                    "no dispara (trasdós a menos de 0.3048 m "
                                    "del borde)"),
    "espesor_pared_conducto": _R_TABLA,
    "D_max_norma_producto": _R_TABLA,
    "durabilidad_tmc_umbrales": _R_POR_CAMPO,
    "sucs_fundacion_deficiente": _R_TABLA,
    "suelo_agresivo_acero_lrfd": _R_TABLA,
    "clases_producto_por_relleno": _R_TABLA,
    "parametros_diseno_hdpe": _R_POR_CAMPO,
    "perfil_hdpe_fabricante": _R_OPCIONAL,
    "angulo_aletas": _R_POR_CAMPO,
    "factores_carga_aashto": _R_TABLA,
    "peso_especifico_concreto_kn_m3": _R_ANALOGIA,
    "predimensionamiento_cabezal": (
        _R_POR_CAMPO + ". El campo que la lectura del cabezal de la regla "
        "pide, `fraccion_ancho_zapata` = 0.7, YA ES EL TECHO de su ventana "
        "(0.4–0.7): dentro de la ventana la zapata sólo puede achicarse, y "
        "una zapata más ancha se declara por punto (`cabezal_declarado`, "
        "variante `zapata_declarada_3m`)"),
    "N_cq_N_gammaq_meyerhof": (_R_SIN_VALOR + "; condicional que el juego no "
                               "dispara (terreno en talud delante del cabezal)"),
    "metodo_estabilidad_global": (_R_SIN_VALOR + "; E4 y E5 no se evalúan "
                                  "(ficha T7B-07)"),
    "categoria_refuerzo_aashto": (
        "el juego lo declara ('A'), pero su ventana es la lista de filas de "
        "la tabla con su descripción y la forma es `str`: " + _R_TABLA),
    "factor_recubrimiento_banda_intermedia_ac": _R_PROSA,
    "exposicion_quimica_ems": _R_ENSAYO,
    "situacion_recubrimiento_aashto": _R_TABLA,
    "tabla_recubrimiento_aashto_mm": _R_DERIVADA,
    "cortante_alto_muro_e060_art_11_10_10_2": _R_ANALOGIA,
    "cuantia_vertical_cortante_alto_e060_art_11_10_10_3": _R_ANALOGIA,
    "procedimiento_flexion_corte_aashto_sec5": _R_TABLA,
    "dentellon_losa_entrega": _R_ANALOGIA,
    "profundidad_cimentacion_min_cabezal_m": _R_ANALOGIA,
    "peralte_min_zapata_armada_m": _R_ANALOGIA,
    "peso_especifico_saturado_relleno_kn_m3": _R_ENSAYO,
    "catalogo_barras_refuerzo_cabezal": _R_TABLA,
    "concreto_ciclopeo_cabezal": (_R_POR_CAMPO + "; ningún cabezal del juego "
                                  "es de gravedad"),
    "espesor_min_zapata_concreto_simple_m": _R_ANALOGIA,
    "edicion_que_rige_el_expediente": _R_SIN_VALOR + "; " + _R_SIN_CONSUMIDOR,
    "edicion_legal_que_rige_el_expediente": (_R_SIN_VALOR + "; "
                                             + _R_SIN_CONSUMIDOR),
}


# Por que la corrida no lee una clave. El test exige que estas sean
# EXACTAMENTE las claves (y bases) que la medida da como no leidas.
NO_LEIDO_PORQUE: Dict[Tuple[str, str], str] = {
    ("seccion_receptor", "juego"): (
        "el juego declara `TW_m` (vía 1 de la Sec. 1.3), que manda sobre las "
        "vías 3 y 4, las únicas que usan la sección del receptor"),
    ("borde_libre_bajo_tw_ahogante", "juego"): (
        "el TW del juego (0.30 m sobre el fondo de la salida; 0.41 m en C-01) "
        "no supera el llenado admisible de V1 (0.75 de la altura: 0.675 m en "
        "el Ø 0.90 y en el marco de 0.90 m): la lectura sólo se pide cuando "
        "el nivel del receptor toma el borde libre"),
    ("hw_entrada_fuera_de_rango", "juego"): (
        "ningún punto queda fuera del rango de la corrección por pendiente "
        "(la carta da carga positiva en todos los escalones evaluados)"),
    # --- los derivados del censo que la corrida no lee (correcciones de
    # T-11, H3) ---
    ("inclinacion_muro_beta", "juego"): (
        "sólo lo lee la vía de contraste de Coulomb / Mononobe-Okabe; el "
        "empuje que rige sale de la cuña de tanteo sobre el plano vertical "
        "del talón"),
    ("homogeneidad_serie_fen", "juego"): (
        "sólo lo lee el caudal CALCULADO; en el juego el caudal es el "
        "declarado del CSV (lo mide la variante `caudal_calculado_sin_fen` "
        "de `docs/validacion_integral.md`)"),
    ("distribucion_precipitacion_maxima", "juego"): (
        "hidrología: sólo la lee el caudal calculado, y en el juego el caudal "
        "es el declarado"),
    ("nivel_significancia_ks", "juego"): (
        "hidrología: sólo lo lee el caudal calculado"),
    ("relacion_intensidad_duracion", "juego"): (
        "hidrología: sólo la lee el caudal calculado"),
    ("duracion_minima_lluvia_min", "juego"): (
        "hidrología: sólo la lee el caudal calculado"),
    ("tc_fuera_de_la_poblacion_del_metodo", "juego"): (
        "hidrología: sólo la lee el caudal calculado"),
    ("coeficiente_uniformidad_temez", "juego"): (
        "hidrología: sólo la lee el caudal calculado con Témez"),
    ("demanda_sismica_licuefaccion", "juego"): (
        "sin consumidor (`SIN_CONSUMIDOR_Y_SIN_MEDIDA`): la licuefacción no "
        "se evalúa"),
    ("fabricacion_tmc", "juego"): (
        "ningún punto adopta TMC: el concreto es el primer candidato"),
    ("relleno_estructural_hdpe", "juego"): (
        "ningún punto adopta HDPE: el concreto es el primer candidato"),
    ("criterio_traccion_cabezal_ciclopeo", "juego"): (
        "ningún cabezal del juego es de gravedad: con D >= 0.90 m todos son "
        "voladizo armado (T-7a)"),
    ("junta_arranque_cabezal_ciclopeo", "juego"): (
        "ningún cabezal del juego es de gravedad"),
}


def valores_de(b: Barrido) -> Tuple[Any, ...]:
    """El efectivo en el juego primero, y despues los extremos de la ventana."""
    if b.valores:
        return b.valores
    efectivo = _efectivo(b.clave)
    if b.clave == "seccion_receptor":
        return (efectivo, SECCION_ESTRECHA, SECCION_ANCHA)
    if b.clave in ("n_manning_cajon",):
        otros: Tuple[Any, ...] = ("concreto_afinado",)
    else:
        otros = ventana_legible(b.clave) or ()
    salida: List[Any] = [efectivo]
    for v in otros:
        if v not in salida:
            salida.append(v)
    return tuple(salida)


@dataclass(frozen=True)
class Medida:
    barrido: Barrido
    valores: Tuple[Any, ...]
    resultado: Any                    # ResultadoDeBarrido
    leido: bool

    def bloqueo(self, valor: Any, id_punto: str) -> str:
        """El primer bloqueo del punto en la corrida de `valor`, abreviado."""
        corrida = next(c for c in self.resultado.corridas
                       if repr(c.valor) == repr(valor))
        p = next(x for x in corrida.informe_json["puntos"]
                 if x["id"] == id_punto)
        for b in p.get("bloqueos") or []:
            if b.get("tipo") == "DiferidoPorAlcance":
                continue
            que = b.get("criterio") or b.get("campo") or ""
            return (f"{b.get('tipo')}: {b.get('etapa')}"
                    + (f" ({que})" if que else ""))
        return ""

    @property
    def filas_por_valor(self) -> Dict[Any, Dict[str, Any]]:
        salida: Dict[Any, Dict[str, Any]] = {}
        for f in self.resultado.filas:
            salida.setdefault(repr(f.valor), {})[f.id_punto] = f
        return salida

    @property
    def primero_es_el_del_juego(self) -> bool:
        return self.valores[0] == _efectivo(self.barrido.clave)

    def movimientos(self) -> Dict[str, List[str]]:
        """
        «diseño», «veredictos» y «HW», con su detalle por (valor, punto),
        contra el primer valor. Si el primero NO es el del juego (un
        opcional sin valor), el diseño se compara ademas con la referencia
        --- el juego sin barrer --- para TODOS los valores.
        """
        filas = self.filas_por_valor
        primero = filas[repr(self.valores[0])]
        diseno, veredictos, hw = [], [], []
        if not self.primero_es_el_del_juego:
            ref = referencia(self.barrido.base)
            for v in self.valores:
                for id_punto, f in filas[repr(v)].items():
                    if _diseno(f) != ref[id_punto]:
                        diseno.append(f"{id_punto} con {_valor(v)}: "
                                      f"{ref[id_punto]} (juego) → {_diseno(f)}")
        for v in self.valores[1:]:
            for id_punto, f in filas[repr(v)].items():
                a = primero[id_punto]
                if self.primero_es_el_del_juego and \
                        (a.dimensionado, a.material, a.seccion) != \
                        (f.dimensionado, f.material, f.seccion):
                    diseno.append(f"{id_punto} con {_valor(v)}: "
                                  f"{_diseno(a)} → {_diseno(f)}")
                if f.verificaciones_que_cambian:
                    veredictos.append(f"{id_punto} con {_valor(v)}: "
                                      f"{len(f.verificaciones_que_cambian)}")
                if a.dimensionado and f.dimensionado and \
                        abs(a.HW_gobernante_m - f.HW_gobernante_m) > \
                        TOL_HW_SENSIBILIDAD_M:
                    hw.append(f"{id_punto} con {_valor(v)}: "
                              f"{a.HW_gobernante_m:.4f} → "
                              f"{f.HW_gobernante_m:.4f} m")
        return {"diseno": diseno, "veredictos": veredictos, "hw": hw}

    @property
    def efecto(self) -> str:
        if not self.leido:
            return "NO LO LEE LA CORRIDA"
        m = self.movimientos()
        if m["diseno"]:
            return "MUEVE EL DISEÑO"
        if m["veredictos"]:
            return "MUEVE VEREDICTOS"
        if m["hw"]:
            return "MUEVE EL HW"
        return "LEÍDO, SIN EFECTO MEDIBLE"


def _valor(v: Any) -> str:
    if isinstance(v, dict):
        return ("sección estrecha" if v == SECCION_ESTRECHA else
                "sección ancha" if v == SECCION_ANCHA else "sección de archivo")
    return repr(v)


def _diseno(f: Any) -> str:
    return f"{f.material}, {f.seccion}" if f.dimensionado else "no dimensiona"


def medir(b: Barrido) -> Medida:
    """El barrido `b` sobre su base, con el estado del proceso aislado."""
    texto_base, cambios = BASES[b.base]
    juego = V.aplicar(V.juego_completo(), cambios)
    valores = valores_de(b)
    previas = ca.valores_dinamicos()
    sitio_previo = ds.datos_dinamicos()
    for clave in previas:
        ca.quitar_valor_dinamico(clave)
    ds.limpiar_datos_dinamicos()
    try:
        with tempfile.TemporaryDirectory(prefix="t11_sens_") as tmp:
            e = V.materializar(juego, Path(tmp))
            servicio.cargar_datos_sitio(e.sitio)
            externos = servicio.cargar_datos_externos(e.externos, {})
            hidro = servicio.cargar_hidrologia(e.cuencas, e.estacion)
            base = {k: v for k, v in e.declaraciones.items() if k != b.clave}
            resultado = barrido.barrer(
                e.csv, externos, V.ALCANCE, b.clave, valores, nota=NOTA,
                declaraciones_base=base, hidrologia=hidro,
                volcar=cli.informe_json)
    finally:
        for clave in ca.valores_dinamicos():
            ca.quitar_valor_dinamico(clave)
        for clave, valor in previas.items():
            ca.establecer_valor_dinamico(clave, valor)
        ds.limpiar_datos_dinamicos()
        for clave, d in sitio_previo.items():
            ds.establecer_dato_dinamico(clave, d.dato.valor, d.dato.trazabilidad,
                                        d.fecha, origen=d.origen)
    leido = any(b.clave in {u["clave"] for u in
                            c.informe_json["criterios"]["usados"]}
                for c in resultado.corridas)
    return Medida(b, valores, resultado, leido)


def medir_todos() -> Tuple[Medida, ...]:
    return tuple(medir(b) for b in BARRIDOS)


_REFERENCIAS: Dict[str, Dict[str, str]] = {}


def referencia(base: str) -> Dict[str, str]:
    """El diseño de cada punto en la base SIN barrer nada (para opcionales)."""
    if base not in _REFERENCIAS:
        informe = V.correr_juego(V.aplicar(V.juego_completo(), BASES[base][1]))
        _REFERENCIAS[base] = {
            p.punto.id: (f"{p.resultado.material.nombre}, "
                         f"{p.resultado.seccion.etiqueta()}"
                         if p.dimensionado and p.resultado is not None
                         else "no dimensiona")
            for p in informe.puntos}
    return _REFERENCIAS[base]


# El resultado del cabezal de la regla que PRECISIONES_T-11 pide presentar
# «con la sensibilidad»: las filas E3 estatica y E1 sismica del marco LRFD,
# frente a los dos [A] de los que T-7b dijo que dependen.
FILAS_DEL_CABEZAL = ("E1-LRFD.sis.e", "E1-LRFD.sis.s", "E3-LRFD.est.e",
                     "E3-LRFD.est.s")
CLAVES_DEL_CABEZAL_DE_LA_REGLA = ("fila_phi_estabilidad_cabezal",
                                  "factores_inclinacion_carga_portante")


def estados_del_cabezal(m: Medida) -> Dict[Tuple[str, str], Tuple[str, ...]]:
    """(punto, fila) -> el estado de la fila con cada valor, en su orden."""
    salida: Dict[Tuple[str, str], List[str]] = {}
    for c in m.resultado.corridas:
        for p in c.informe_json["puntos"]:
            v = {x["codigo"]: x["estado"] for x in p.get("verificaciones") or []}
            for fila in FILAS_DEL_CABEZAL:
                salida.setdefault((p["id"], fila), []).append(v.get(fila, "—"))
    return {k: tuple(v) for k, v in salida.items()}


# ---------------------------------------------------------------------------
# El documento
# ---------------------------------------------------------------------------

def _celda(texto: Any) -> str:
    return " ".join(str(texto).split()).replace("|", "\\|")


def _ventana(clave: str) -> str:
    s = ca.criterio(clave).sensibilidad
    if isinstance(s, dict):
        return "; ".join(f"{k} {a}–{b}" for k, (a, b) in s.items())
    if isinstance(s, tuple) and len(s) == 2 and all(
            isinstance(x, (int, float)) for x in s):
        return f"{s[0]}–{s[1]}"
    return " / ".join(str(x).split(" -- ")[0] for x in s)


def generar(medidas: Optional[Sequence[Medida]] = None) -> str:
    medidas = tuple(medidas) if medidas is not None else medir_todos()
    L: List[str] = []
    A = L.append
    A("# Sensibilidad de los criterios adoptados sobre el juego de prueba (T-11)")
    A("")
    A("> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe "
      "`python -m tests.apoyo.sensibilidad --escribir` y "
      "`tests/test_t11_sensibilidad.py` lo regenera y lo compara. Cada "
      "barrido es `src/barrido.py` (PF-3) sobre el juego de **DATOS DE "
      "PRUEBA, NO DEL PROYECTO** de la validación integral, a `--alcance "
      "expediente`. **Ningún valor de archivo cambia**: un barrido declara "
      "cada valor para su corrida y deja el proceso como estaba.")
    A("")
    A("## 1. Cómo leer este anexo")
    A("")
    A("- **La base de los barridos es el juego tal como está**, la variante "
      "que ejercita la cadena sísmica y el caso drenado "
      "(`docs/validacion_integral.md` §2.1), y **no la corrida titular** (§2, "
      "con las decisiones de archivo): con `drenaje_trasdos` = 'sin_drenaje' "
      "la condición sísmica del cabezal es «método no evaluable» (ficha "
      "T7B-05), y hace falta una base donde el método sea evaluable para "
      "medir los [A] del cabezal. Lo que las dos decisiones de archivo hacen "
      "se lee en sus propios barridos (`drenaje_trasdos`, "
      "`factor_muro_eleccion`).")
    A("- **Primer valor = el efectivo en el juego** (el que el juego declara "
      "o el de archivo): su corrida es la del juego, y cada otra se compara "
      "con ella por el comparador de E-B. Los demás valores son los extremos "
      "de la ventana del criterio (`Criterio.sensibilidad`), o sus otras "
      "opciones.")
    A("- **MUEVE EL DISEÑO**: algún punto cambia de material o de sección, o "
      "deja de dimensionar. **MUEVE VEREDICTOS**: cambia el veredicto de "
      "alguna verificación del conducto, del cabezal o de la Fase 10. **MUEVE "
      "EL HW**: sólo cambia la carga que gobierna, en más de "
      f"{TOL_HW_SENSIBILIDAD_M} m (media unidad de la cuarta cifra con que "
      "se imprime). **LEÍDO, SIN EFECTO MEDIBLE** quiere decir que la "
      "corrida lee el criterio y que no cambian ni el material, ni la "
      "sección, ni ningún veredicto, ni el HW que gobierna: **las demás "
      "magnitudes no se comparan** (la hoya de socavación, el espesor y la "
      "longitud de la protección, las longitudes, los márgenes, el armado), "
      "y pueden cambiar. **NO LO LEE LA CORRIDA**: la clave no está entre los "
      "criterios usados de ninguna corrida del barrido, y barrerla no mueve "
      "nada en ESTE juego (la razón, en la tabla).")
    A("- **La lista se deriva del censo**: se barre todo criterio con valor "
      "efectivo en el juego y ventana legible por máquina (una categoría "
      "cerrada o dos extremos numéricos), más los que necesitan valores "
      "propios. Los que no se barren están en §5, **por nombre y con su "
      "razón**. Un barrido mide UNA clave a la vez, sobre UN juego: no es el "
      "producto cartesiano ni dice nada de otro sitio.")
    A("")
    A("## 2. Resumen")
    A("")
    A("| Grupo | Criterio | Etiqueta | Ventana | Valores barridos | Base | "
      "Efecto | Detalle |")
    A("|---|---|---|---|---|---|---|---|")
    for m in medidas:
        c = ca.criterio(m.barrido.clave)
        mov = m.movimientos()
        if not m.leido:
            detalle = NO_LEIDO_PORQUE.get((m.barrido.clave, m.barrido.base),
                                          "SIN RAZÓN ESCRITA")
        else:
            partes = []
            if mov["diseno"]:
                partes.append("diseño: " + "; ".join(mov["diseno"]))
            if mov["veredictos"]:
                partes.append("veredictos que cambian: "
                              + "; ".join(mov["veredictos"]))
            if mov["hw"] and not mov["diseno"]:
                partes.append("HW: " + "; ".join(mov["hw"]))
            detalle = " · ".join(partes) or "—"
        A("| " + " | ".join(_celda(x) for x in (
            m.barrido.grupo, f"`{m.barrido.clave}`", f"[{c.etiqueta}]",
            _ventana(m.barrido.clave),
            ", ".join(_valor(v) for v in m.valores),
            m.barrido.base, m.efecto, detalle)) + " |")
    A("")
    A("## 3. Lo que el resumen dice, por clase")
    A("")
    for efecto in ("MUEVE EL DISEÑO", "MUEVE VEREDICTOS", "MUEVE EL HW",
                   "LEÍDO, SIN EFECTO MEDIBLE", "NO LO LEE LA CORRIDA"):
        claves = [f"`{m.barrido.clave}`" + ("" if m.barrido.base == "juego"
                                            else f" ({m.barrido.base})")
                  for m in medidas if m.efecto == efecto]
        A(f"- **{efecto}** ({len(claves)}): "
          + (", ".join(claves) if claves else "ninguno") + ".")
    A("")
    A("### 3.1 El cabezal de la regla: E3 estática y E1 sísmica del marco "
      "LRFD frente a sus dos [A]")
    A("")
    A("Con la zapata que propone la regla de T-7a (que no se itera, ficha "
      "T7B-09) estas cuatro filas no pasan en la corrida del juego "
      "(`docs/validacion_integral.md` §2). Lo que cada uno de los dos [A] de "
      "los que dependen hace con ellas, medido:")
    A("")
    A("| Criterio | Valor | " + " | ".join(f"`{f}`" for f in FILAS_DEL_CABEZAL)
      + " |")
    A("|---|---|" + "---|" * len(FILAS_DEL_CABEZAL))
    for m in medidas:
        if m.barrido.clave not in CLAVES_DEL_CABEZAL_DE_LA_REGLA:
            continue
        estados = estados_del_cabezal(m)
        puntos = sorted({p for p, _f in estados})
        for i, valor in enumerate(m.valores):
            celdas = []
            for fila in FILAS_DEL_CABEZAL:
                pasan = [p for p in puntos if estados[(p, fila)][i] == "cumple"]
                celdas.append("pasa en " + ", ".join(pasan) if pasan
                              else "no pasa en ninguno")
            A("| " + " | ".join(_celda(x) for x in (
                f"`{m.barrido.clave}`", _valor(valor), *celdas)) + " |")
    A("")
    A("Ninguno de los dos hace pasar E3 estática a la ENTRADA: ahí el "
      "deslizamiento de A-01 lo resuelve la zapata más ancha (variante "
      "`zapata_declarada_3m` de `docs/validacion_integral.md` §5), no la "
      "lectura de un [A].")
    A("")
    vmax = [m for m in medidas if m.barrido.clave == "v_max_concreto_eleccion"]
    if vmax:
        A("### 3.2 `v_max_concreto_eleccion`: lo que el dueño decidió y de "
          "qué depende el resultado")
        A("")
        A("El criterio **se queda SIN valor por decisión del dueño "
          "(2026-11-13)**: es opcional y V3 aplica el máximo de 6.0 m/s de "
          "la Tabla Nº 10 del Manual para el concreto. Lo que el barrido "
          "mide con el extremo inferior de esa misma fila (3.0 m/s) es un "
          "**resultado de la tesis que no cambia el fixture**:")
        A("")
        for m in vmax:
            f = m.filas_por_valor[repr(3.0)]["A-01"]
            resultado = (_diseno(f) if f.dimensionado else
                         "no dimensiona (" + m.bloqueo(3.0, "A-01") + ")")
            A(f"- base `{m.barrido.base}` ({BASES[m.barrido.base][0]}): "
              f"A-01 con 3.0 m/s → {resultado}.")
        A("")
        A("Ese resultado depende de **otro [A]**: el TMC al que A-01 pasa "
          "está en un suelo que la misma corrida califica de agresivo para el "
          "acero galvanizado (sulfatos de 500 ppm frente a los 200 ppm de "
          "AASHTO LRFD 11.10.6.4.2a que `suelo_agresivo_acero_lrfd` aplica "
          "por analogía; para el concreto son «insignificantes» por la Tabla "
          "4.4 de E.060). Con `suelo_agresivo_lrfd_sobre_tmc` = 'aviso' (el "
          "de archivo) la TMC sigue candidata con aviso; con 'excluye', "
          "dentro de su ventana, sale, y A-01 se detiene en el siguiente "
          "candidato, el HDPE, por el dato del fabricante que falta.")
        A("")
    A("Lectura de ingeniería (no la escribe el programa): un criterio que "
      "MUEVE EL DISEÑO dentro de su ventana es una decisión que el "
      "proyectista tiene que poder defender con la cita de su ficha, porque "
      "otra lectura igual de admisible da otra obra; uno que NO LO LEE ESTA "
      "CORRIDA puede gobernar en otro punto u otro sitio (otro material "
      "candidato, otro TW): este anexo no lo absuelve.")
    A("")
    A("## 4. Detalle por criterio")
    A("")
    for m in medidas:
        A(f"### `{m.barrido.clave}`" + ("" if m.barrido.base == "juego"
                                       else f" — base `{m.barrido.base}`"))
        A("")
        A(f"{m.barrido.por_que}. Base: {BASES[m.barrido.base][0]}. "
          f"Efecto: **{m.efecto}**.")
        A("")
        if not m.primero_es_el_del_juego:
            ref = referencia(m.barrido.base)
            A("El primer valor NO es el del juego (el juego no lo declara: "
              "rige " + ("la regla de su ficha" if ca.criterio(
                  m.barrido.clave).valor is None else "el valor de archivo")
              + "). Referencia, el juego sin barrer: "
              + "; ".join(f"{i} {s}" for i, s in ref.items()) + ".")
            A("")
        A("| Valor | Punto | Material y sección | HW (m) | Control | "
          "Verificaciones que cambian frente al primer valor | Incumplidas o "
          "bloqueo si no dimensiona | Comparable |")
        A("|---|---|---|---|---|---|---|---|")
        for f in m.resultado.filas:
            if f.dimensionado:
                cambian = ", ".join(f.verificaciones_que_cambian) or "ninguna"
            else:
                cambian = (f"(el punto no dimensiona: "
                           f"{len(f.verificaciones_que_cambian)} cambian o "
                           "desaparecen)" if f.verificaciones_que_cambian
                           else "ninguna")
            incumplidas = ", ".join(f.incumplidas_en_la_progresion) or (
                m.bloqueo(f.valor, f.id_punto) if not f.dimensionado else "")
            A("| " + " | ".join(_celda(x) for x in (
                _valor(f.valor), f.id_punto,
                _diseno(f),
                "—" if f.HW_gobernante_m is None else f"{f.HW_gobernante_m:.3f}",
                f.control_gobernante or "—", cambian, incumplidas or "—",
                "sí" if f.comparable else f"NO: {f.motivo}")) + " |")
        A("")
    L += _seccion_no_barribles()
    return "\n".join(L) + "\n"


def _seccion_no_barribles() -> List[str]:
    L = ["## 5. Los criterios que no se barren, por nombre", "",
         f"{len(BARRIDOS)} barridos sobre {len({b.clave for b in BARRIDOS})} "
         f"criterios; estos {len(NO_BARRIBLES)} no se barren, y la razón:", "",
         "| Criterio | Etiqueta | Por qué no se barre |", "|---|---|---|"]
    for clave, razon in NO_BARRIBLES.items():
        L.append("| " + " | ".join(_celda(x) for x in (
            f"`{clave}`", f"[{ca.criterio(clave).etiqueta}]", razon)) + " |")
    L.append("")
    return L


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    texto = generar()
    if "--escribir" in args:
        DOCUMENTO.write_text(texto, encoding="utf-8")
        print(f"escrito {DOCUMENTO}")
    else:
        sys.stdout.write(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
