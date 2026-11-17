"""
tests/apoyo/validacion_conducto.py
==================================
La VALIDACION EXTERNA de M8 (estructura del conducto) contra EJEMPLOS
RESUELTOS PUBLICADOS por terceros, generada en `docs/validacion_conducto.md`.
`tests/test_validacion_conducto.py` lo regenera a memoria y lo compara, de
modo que el documento no se puede desincronizar del programa sin que la
suite lo diga.

Regenerar::

    python -m tests.apoyo.validacion_conducto --escribir

QUE SE COMPARA CON QUE, Y COMO SE JUZGA
---------------------------------------
Cada CONTRASTE lleva cuatro cifras, todas en la UNIDAD DE LA FUENTE:

  publicado     lo que el ejemplo imprime, con su pagina impresa;
  recalculado   la cuenta del EJEMPLO rehecha aqui con SUS formulas y SUS
                datos (los intermedios redondeados que el ejemplo imprime se
                usan tal cual): si difiere de lo publicado, la fuente tiene
                una ERRATA, y lo que rige es lo recalculado;
  referencia    la cuenta del METODO QUE M8 IMPLEMENTA (AASHTO LRFD 9.a ed.,
                Manual de Puentes, ASTM A796-13), escrita aqui A MANO, en
                otra unidad y sin llamar a M8, con los datos del ejemplo;
  motor         lo que M8 devuelve con los datos del ejemplo en SI,
                convertido a la unidad de la fuente.

y se clasifica asi, en este orden:

  DEFECTO     el motor no reproduce su propio metodo (motor frente a
              referencia, fuera de `TOL_REL_MOTOR`). Seria un defecto de M8;
  SIN FUENTE  no hay cifra publicada: el caso existe para ejercitar una rama
              del motor que ningun ejemplo alcanza (hoy, l_w < B_c);
  COINCIDE    el metodo de M8 da lo mismo que el ejemplo (referencia frente
              a recalculado, dentro de `TOL_REL_CIFRA_IMPRESA`);
  METODO      el ejemplo usa otra edicion u otro metodo: la diferencia se
              explica, partida por causa, en el contraste.

DOS CATEGORIAS, y no se suman (correcciones de la revision Fable, A-1): solo
COINCIDE es «CONTRASTADO CON LA FUENTE». METODO y SIN FUENTE dicen que el
motor «REPRODUCE SU PROPIO METODO» (la lectura de la edicion vigente que el
arnes escribe a mano): prueban que M8 esta bien programado segun esa
lectura, no que la lectura este validada por un tercero.

Ademas, una ERRATA DE LA FUENTE (publicado frente a recalculado, fuera de
`TOL_REL_CIFRA_IMPRESA`) se registra aparte, sin cambiar la clase.

LAS FUENTES NO SE VERSIONAN: son documentos publicos de ACPA y del USACE
(URL en `FUENTES`), con copyright, y este repositorio no versiona ningun PDF
(CLAUDE.md). Las cifras se transcribieron leyendo la pagina, la imagen
cuando la capa de texto era dudosa (USACE, escaneado), con la pagina impresa
de cada una.

Lo que este modulo NO hace: no corrige el motor ni ajusta una tolerancia
para que un contraste pase. Un DEFECTO se imprime como tal.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from src import constantes_normativas as CN
from src.constantes_fisicas import (GAMMA_AGUA_KN_M3, LIBRA_FUERZA_EN_N,
                                    N_POR_KN, PCF_EN_KN_M3, PIE_EN_METROS,
                                    PULGADA_EN_MM)
from src.modelos import SeccionCircular, TipoMaterial
from src.modulos import M8_estructural as M8
from src.modulos.M2_material import catalogo
from tests.apoyo.criterios import con_valor, declarados

RAIZ = Path(__file__).resolve().parents[2]
DOCUMENTO = RAIZ / "docs" / "validacion_conducto.md"

# ---------------------------------------------------------------------------
# Tolerancias, con nombre y con su clase de igualdad
# ---------------------------------------------------------------------------
# El motor frente a la MISMA ecuacion escrita aqui a mano en otra unidad (pies
# y libras, o SI con las constantes del motor): solo el redondeo de la
# aritmetica y de los factores de conversion exactos.
TOL_REL_MOTOR = 1e-9
# Una cifra IMPRESA frente a la recalculada: las fuentes imprimen 3 o 4
# cifras significativas, redondean los intermedios (DD 1 toma A = 24.9 ft2
# por 24.95; DD 22 lee los pesos de tabla a la libra; USACE escribe f_c con
# tres cifras) y escriben el agua a 62.4 pcf (9.802 kN/m3) donde el motor usa
# 9.81 kN/m3, un 0.08 %. Medio por ciento cubre todo eso con margen y queda
# un orden por debajo de cualquier diferencia de metodo de este documento
# (la menor, el agua del tubo en la D-load, pesa un 2.9 %).
TOL_REL_CIFRA_IMPRESA = 5e-3

COINCIDE = "COINCIDE"
METODO = "METODO"
SIN_FUENTE = "SIN FUENTE"
DEFECTO = "DEFECTO"
# Las dos categorias del resumen (A-1 de la revision Fable).
CONTRASTADO_CON_LA_FUENTE = (COINCIDE,)
REPRODUCE_SU_METODO = (METODO, SIN_FUENTE)

# ---------------------------------------------------------------------------
# Unidades de las fuentes (EE. UU.), con los factores exactos del motor
# ---------------------------------------------------------------------------
PLF_EN_KN_M = LIBRA_FUERZA_EN_N / N_POR_KN / PIE_EN_METROS      # lb/ft -> kN/m
# D-load: libras por pie lineal y por pie de diametro -> N/m por mm.
DLOAD_EN_N_M_MM = LIBRA_FUERZA_EN_N / PIE_EN_METROS / (
    PIE_EN_METROS * 1000.0)                                     # literal-ok: mm por m
PULG = PULGADA_EN_MM / 1000.0                                   # literal-ok: m por mm
AGUA_PCF_MOTOR = GAMMA_AGUA_KN_M3 / PCF_EN_KN_M3                # 62.45 pcf


def _cerca(a: float, b: float, rel: float) -> bool:
    return abs(a - b) <= rel * max(abs(a), abs(b))


def _interpolar_a_mano(x: float, xs: Sequence[float],
                       ys: Sequence[float]) -> float:
    """
    Interpolacion lineal con los extremos de la tabla como tope, escrita
    AQUI (correcciones de la revision Fable, A-2: la referencia usaba
    `M8._interpolar`, la funcion del motor, y dejaba de ser independiente).
    """
    if x <= xs[0]:
        return ys[0]
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return ys[-1]


# ===========================================================================
# Las fuentes
# ===========================================================================

FUENTES = {
    "DD1": ("ACPA, Design Data 1 «Highway Live Loads on Concrete Pipe», "
            "DD 1 (07/09), 2009",
            "https://old.concretepipe.org/wp-content/uploads/DD_1.pdf"),
    "DD22": ("ACPA, Design Data 22 «Flotation of Circular Concrete Pipe», "
             "DD 22 (11/12)",
             "https://old.concretepipe.org/wp-content/uploads/2014/09/"
             "DD_22.pdf"),
    "CPDM": ("ACPA, Concrete Pipe Design Manual, Cap. 4 «Loads and "
             "Supporting Strengths» (ed. 2000; copia de un curso del NJIT)",
             "https://web.njit.edu/~washd/cim305/download/notes/CHAPTERS/"
             "CH%204.pdf"),
    "USACE": ("US Army Corps of Engineers, EM 1110-2-2902 «Conduits, "
              "Culverts and Pipes», Apendice B «Design Examples», 1997 "
              "(Change 1, 1998)",
              "https://damtoolbox.org/images/3/37/EM_1110-2-2902.pdf"),
    "PPI": ("Plastics Pipe Institute, Drainage Handbook — Structural Design "
            "Guide (Draft Rev 1), 2019",
            "https://clvr.imiscloud.com/common/Uploaded%20files/1-PPI/"
            "Manuals-Design%20Guides/Drainage%20Handbook/1st%20Edition/"
            "Design%20Guide%20Rev1%20.pdf"),
}


@dataclass(frozen=True)
class Contraste:
    id: str
    fuente: str
    pagina: str
    que: str
    unidad: str
    publicado: Optional[float]
    recalculado: float
    referencia: float
    motor: float
    explicacion: str
    errata: str = ""

    @property
    def clase(self) -> str:
        if not _cerca(self.motor, self.referencia, TOL_REL_MOTOR):
            return DEFECTO
        if self.publicado is None:
            return SIN_FUENTE
        if _cerca(self.referencia, self.recalculado, TOL_REL_CIFRA_IMPRESA):
            return COINCIDE
        return METODO

    @property
    def errata_de_la_fuente(self) -> bool:
        return (self.publicado is not None and not _cerca(
            self.publicado, self.recalculado, TOL_REL_CIFRA_IMPRESA)) \
            or bool(self.errata)

    @property
    def diferencia_pct(self) -> float:
        """El motor frente a lo recalculado del ejemplo, en %."""
        return 100.0 * (self.motor - self.recalculado) / self.recalculado  # literal-ok: porcentaje


# ===========================================================================
# 1. Carga viva a traves del relleno (ACPA DD 1) y su IM
# ===========================================================================

def _lldf_9a(D_i_ft: float, concreto: bool) -> float:
    """Tabla 3.6.1.2.6a-1 (9.a ed.), a mano: 1.15 a 1.75 entre 2 y 8 ft."""
    if not concreto:
        return 1.15                                    # literal-ok: Tabla 3.6.1.2.6a-1
    x = min(max(D_i_ft, 2.0), 8.0)                     # literal-ok: 2 y 8 ft de la tabla
    return 1.15 + 0.60 * (x - 2.0) / 6.0               # literal-ok: interpolacion de la tabla


def _hl93_a_mano(H_ft: float, D_i_ft: float, B_c_ft: float,
                 D_E_ft: Optional[float] = None) -> Tuple[float, float, str]:
    """
    W_L = P_L min(l_w, B_c) en lb/ft del VEHICULO DE MAYOR W_L, por
    AASHTO LRFD 9.a ed. 3.6.1.2.6b con el HL-93 del Manual de Puentes (32 y
    25 kip, m = 1.20), escrito en kip y pies SIN llamar a M8. Devuelve
    (W_L, IM %, vehiculo).
    """
    d = hl93_detalle(H_ft, D_i_ft, B_c_ft, D_E_ft)
    return d["W_L"], d["IM"], d["vehiculo"]


def hl93_detalle(H_ft: float, D_i_ft: float, B_c_ft: float,
                 D_E_ft: Optional[float] = None) -> Dict[str, object]:
    """
    Lo mismo que `_hl93_a_mano`, con el detalle del vehiculo que gobierna:
    W_L (lb/ft), P_L (lb/ft2), l_w (ft), IM (%) y el vehiculo. Lo leen la
    descomposicion del §8 y el test de la rama l_w < B_c.
    """
    D_E_ft = H_ft if D_E_ft is None else D_E_ft
    LLDF = _lldf_9a(D_i_ft, concreto=True)
    IM = max(0.0, 33.0 * (1.0 - 0.125 * D_E_ft))     # literal-ok: 2.4.3.3.2
    wt, lt, sw = 20 / 12, 10 / 12, 6.0                 # literal-ok: neumatico 20 x 10 in, ruedas a 6 ft
    mejor: Dict[str, object] = {"W_L": -1.0}
    for nombre, eje, sa in (("camion", 32.0, 14.0), ("tandem", 25.0, 4.0)):  # literal-ok: HL-93
        luz = 0.06 * D_i_ft                            # literal-ok: Eq. 3.6.1.2.6b-1
        if H_ft < (sw - wt - luz) / LLDF:
            ww, P = wt + LLDF * H_ft + luz, eje / 2
        else:
            ww, P = wt + sw + LLDF * H_ft + luz, eje
        if H_ft < (sa - lt) / LLDF:
            lw = lt + LLDF * H_ft
        else:
            lw, P = lt + sa + LLDF * H_ft, 2 * P
        PL_ksf = P * (1 + IM / 100) * 1.20 / (lw * ww)  # literal-ok: m = 1.20, Eq. 3.6.1.2.6b-7
        WL = PL_ksf * min(lw, B_c_ft) * 1000.0         # literal-ok: lb por kip
        if WL > mejor["W_L"]:
            mejor = {"W_L": WL, "IM": IM, "vehiculo": nombre,
                     "P_L_psf": PL_ksf * 1000.0, "l_w": lw}  # literal-ok: lb por kip
    return mejor


def _dd1_a_mano(*, P_lb: float, a_ft: float, b_ft: float, H_ft: float,
                Do_ft: float, Ro_ft: float, perpendicular: bool,
                A_impresa: Optional[float] = None) -> float:
    """
    La cuenta de DD 1 (ecs. 1 a 5), con SUS datos: w = P (1 + IM)/A,
    W_T = w L S_L, L_e = L + 1.75 (3/4 R_o), W_L = W_T / L_e, en lb/ft.
    `a_ft` y `b_ft` son los lados del area ya extendida a la profundidad H;
    `A_impresa`, el area que el ejemplo redondea e imprime.
    """
    IM = 33 * (1.0 - 0.125 * H_ft) / 100               # literal-ok: Eq. 1 de DD 1
    A = A_impresa if A_impresa is not None else a_ft * b_ft
    w = P_lb * (1 + IM) / A
    L, otro = (a_ft, b_ft) if perpendicular else (b_ft, a_ft)
    S_L = min(Do_ft, otro)
    W_T = w * L * S_L
    L_e = L + 1.75 * (0.75 * Ro_ft)                    # literal-ok: Eq. 2 de DD 1
    return W_T / L_e


def _contrastes_dd1() -> List[Contraste]:
    out: List[Contraste] = []
    # --- IM de componentes enterrados: 33 (1 - 0.125 D_E), D_E en pies ----
    for H_ft, publicado, pag in ((2.0, 24.75, "7"), (6.0, 8.25, "9")):
        recalc = 33 * (1.0 - 0.125 * H_ft)             # literal-ok: Eq. 1 de DD 1
        motor = M8.incremento_dinamico_enterrado(H_ft * PIE_EN_METROS)
        out.append(Contraste(
            id=f"DD1-IM-{H_ft:g}ft", fuente="DD1", pagina=pag,
            que=f"IM de componentes enterrados con {H_ft:g} ft de cubierta",
            unidad="%", publicado=publicado, recalculado=recalc,
            referencia=recalc, motor=motor,
            explicacion=("La misma ecuacion: DD 1 Eq. 1 y Manual de Puentes "
                         "2.4.3.3.2 (`M8.incremento_dinamico_enterrado`).")))
    # --- W_L del tubo de 30 in pared B (Do = 37 in) ------------------------
    D_i, Do = 30 * PULG, 37 * PULG
    Do_ft, Di_ft = 37 / 12, 30 / 12
    casos = (
        # (id, H, P, a, b, perpendicular, A impresa, publicado, pagina, carga)
        ("DD1-EJ1", 2.0, 32000.0, 1.67 + 4 + 1.15 * 2, 0.83 + 1.15 * 2,  # literal-ok: Ej. 1 de DD 1
         True, 24.9, 3272.0, "7",                                        # literal-ok: Ej. 1 de DD 1
         "dos ruedas duales HS 20 en paso, 32 000 lb"),
        ("DD1-EJ4", 6.0, 50000.0, 1.67 + 4 + 1.15 * 6, 0.83 + 4 + 1.15 * 6,  # literal-ok: Ej. 4 de DD 1
         True, 147.45, 855.0, "8-9",                                     # literal-ok: Ej. 4 de DD 1
         "dos ruedas de dos cargas alternativas (Alternate Load) en paso, "
         "50 000 lb"),
    )
    for id_, H_ft, P, a, b, perp, A_imp, publicado, pag, carga in casos:
        recalc = _dd1_a_mano(P_lb=P, a_ft=a, b_ft=b, H_ft=H_ft, Do_ft=Do_ft,
                             Ro_ft=3.08, perpendicular=perp, A_impresa=A_imp)  # literal-ok: R_o que imprime DD 1
        ref, IM, vehiculo = _hl93_a_mano(H_ft, Di_ft, Do_ft)
        # LA RUTA REAL (correcciones de la revision Fable, A-2): el W_L que
        # `M8.verificar_concreto` sustituye en la D-load, y no el de
        # `M8.carga_viva_enterrada` con una formula de W_L que le pasaba el
        # arnes: asi la linea W_L = P_L min(l_w, B_c) del motor se contrasta.
        _D, sust = _verificar_concreto_del_motor(
            D_in=30.0, pared_in=3.5, H_ft=H_ft, tipo="tipo_2")  # literal-ok: Ø 30 in pared B de DD 1
        motor = sust["W_L"]
        out.append(Contraste(
            id=id_, fuente="DD1", pagina=pag,
            que=(f"Carga viva por pie de tubo, Ø 30 in pared B, {H_ft:g} ft "
                 "de relleno, trafico perpendicular al tubo"),
            unidad="lb/ft", publicado=publicado, recalculado=recalc,
            referencia=ref, motor=motor,
            explicacion=(
                f"DD 1 (2009) aplica la distribucion ANTERIOR a 2013 ({carga}, "
                "sin presencia multiple), LLDF 1.15 fijo, sin "
                "el termino 0.06 D_i, y reparte la carga a lo largo del tubo "
                "con la longitud efectiva L_e = L + 1.75 (3/4 R_o), donde R_o "
                "es la ALTURA exterior del tubo (= D_o en un circular; la "
                "Fig. 7 de DD 1 escribe 3/4 B_c), no el radio. M8 aplica "
                "AASHTO LRFD 9.a ed. 3.6.1.2.6b: HL-93 (gobierna el "
                f"{vehiculo}), m = 1.20, LLDF {_lldf_9a(Di_ft, True):.3f} "
                "interpolado por diametro (Tabla 3.6.1.2.6a-1), 0.06 D_i en el "
                "ancho y W_L = P_L min(l_w, B_c), sin L_e. El IM es el mismo "
                f"({IM:.2f} %, contraste DD1-IM). No es un defecto, y casi "
                "toda la diferencia es la L_e (ver la descomposicion del "
                "§8). El W_L del motor es el que `M8.verificar_concreto` "
                "sustituye en la D-load.")))
    # --- La rama l_w < B_c, que ningun ejemplo alcanza (A-2) --------------
    # Ø 72 in pared B (7 in; B_c = 86 in = 7.17 ft, el tubo de DD 22) con 2 ft:
    # el ancho cargado l_w (~3.2 ft) es MENOR que B_c y gobierna el min.
    # SIN cifra publicada: prueba que el motor sigue su metodo en esa rama.
    det = hl93_detalle(2.0, 6.0, 86.0 / 12)            # literal-ok: Ø 72 in pared B, 2 ft
    _D, sust = _verificar_concreto_del_motor(
        D_in=72.0, pared_in=7.0, H_ft=2.0, tipo="tipo_2")  # literal-ok: Ø 72 in pared B, 2 ft
    out.append(Contraste(
        id="M8-LW-72", fuente="M8", pagina="—",
        que=("Carga viva por pie de tubo, Ø 72 in pared B, 2 ft de relleno: "
             "la rama l_w < B_c de W_L = P_L min(l_w, B_c)"),
        unidad="lb/ft", publicado=None, recalculado=det["W_L"],
        referencia=det["W_L"], motor=sust["W_L"],
        explicacion=(
            f"Sin ejemplo publicado: l_w = {det['l_w']:.2f} ft < B_c = "
            f"{86.0 / 12:.2f} ft, la rama que ningun ejemplo de esta "
            "validacion alcanza (en DD 1 y en el CPDM l_w >= B_c). Solo prueba "
            "que la linea del motor sigue el metodo escrito a mano.")))
    return out


# ===========================================================================
# 2. Tablas del metodo indirecto (ACPA CPDM, Ilustraciones 4.19 y 4.21;
#    VAF bajo la Ec. 4)
# ===========================================================================

# Ilustracion 4.19 del CPDM (pag. impresa 52): B_fe por diametro y tipo.
CPDM_BFE = {12: (4.4, 3.2, 2.5, 1.7), 24: (4.2, 3.0, 2.4, 1.7),   # literal-ok: Ilustracion 4.19 del CPDM
            36: (4.0, 2.9, 2.3, 1.7), 72: (3.8, 2.8, 2.2, 1.7),   # literal-ok: Ilustracion 4.19 del CPDM
            144: (3.6, 2.8, 2.2, 1.7)}                            # literal-ok: Ilustracion 4.19 del CPDM
# VAF de las cuatro instalaciones estandar, bajo la Ec. 4 del CPDM (pag. 38).
CPDM_VAF = (1.35, 1.40, 1.40, 1.45)                               # literal-ok: VAF del CPDM, Ec. 4
# Ilustracion 4.21 del CPDM (pag. impresa 55), fila de 2.0 ft de relleno.
CPDM_BFLL_2FT = {12: 2.2, 24: 2.2, 36: 2.2, 48: 2.0}              # literal-ok: Ilustracion 4.21 del CPDM
TIPOS = ("tipo_1", "tipo_2", "tipo_3", "tipo_4")


def _contrastes_tablas() -> List[Contraste]:
    out: List[Contraste] = []
    for i, tipo in enumerate(TIPOS):
        out.append(Contraste(
            id=f"CPDM-VAF-{i + 1}", fuente="CPDM", pagina="38",
            que=f"VAF de la instalacion estandar Tipo {i + 1}", unidad="",
            publicado=CPDM_VAF[i], recalculado=CPDM_VAF[i],
            referencia=CPDM_VAF[i], motor=CN.VAF_INSTALACION_ESTANDAR[tipo],
            explicacion="Tabla 12.10.2.1-3 de AASHTO LRFD 9.a ed.: la misma."))
    for D_pulg, fila in CPDM_BFE.items():
        for i, tipo in enumerate(TIPOS):
            motor = M8._interpolar(D_pulg, CN.BFE_DIAMETROS_PULG,
                                   CN.BFE_POR_TIPO[tipo])
            out.append(Contraste(
                id=f"CPDM-BFE-{D_pulg}-{i + 1}", fuente="CPDM", pagina="52",
                que=f"B_FE, Ø {D_pulg} in, Tipo {i + 1}", unidad="",
                publicado=fila[i], recalculado=fila[i], referencia=fila[i],
                motor=motor,
                explicacion=("Tabla 12.10.4.3.2a-1 de AASHTO LRFD 9.a ed.: "
                             "la misma.")))
    # B_fe de 48 in, Tipo 1, que el CPDM PUBLICA en el Ej. 4-2 (interpolado
    # entre 36 y 72 in de su Ilustracion 4.19): el unico B_fe fuera de los
    # nodos de la tabla (A-2 de la revision Fable).
    xs = tuple(float(x) for x in sorted(CPDM_BFE))
    ref_48 = _interpolar_a_mano(48.0, xs, tuple(CPDM_BFE[int(x)][0] for x in xs))  # literal-ok: Ø 48 in del Ej. 4-2
    out.append(Contraste(
        id="CPDM-BFE-48-1", fuente="CPDM", pagina="60-62",
        que="B_FE, Ø 48 in, Tipo 1 (interpolado; publicado en el Ej. 4-2)",
        unidad="", publicado=3.93, recalculado=ref_48, referencia=ref_48,  # literal-ok: B_fe del Ej. 4-2
        motor=M8._interpolar(48.0, CN.BFE_DIAMETROS_PULG,           # literal-ok: Ø 48 in del Ej. 4-2
                             CN.BFE_POR_TIPO["tipo_1"]),
        explicacion=("Tabla 12.10.4.3.2a-1 de AASHTO LRFD 9.a ed. (la misma "
                     "que la Ilustracion 4.19 del CPDM) interpolada a 48 in, "
                     "como hace el Ej. 4-2.")))
    for D_pulg, publicado in CPDM_BFLL_2FT.items():
        ref = _interpolar_a_mano(D_pulg, (12.0, 18.0, 24.0, 30.0),   # literal-ok: Tabla 12.10.4.3.2c-1
                                 (2.4, 2.4, 2.4, 2.2))               # literal-ok: Tabla 12.10.4.3.2c-1
        motor = M8._interpolar(D_pulg, CN.BFLL_DIAMETROS_PULG,
                               CN.BFLL_RELLENO_DESDE_2_PIES)
        if _cerca(ref, publicado, TOL_REL_CIFRA_IMPRESA):
            out.append(Contraste(
                id=f"CPDM-BFLL-{D_pulg}", fuente="CPDM", pagina="55",
                que=f"B_FLL, Ø {D_pulg} in, 2.0 ft de relleno", unidad="",
                publicado=publicado, recalculado=publicado, referencia=ref,
                motor=motor,
                explicacion=(f"Ø {D_pulg} in con 2.0 ft: {publicado} en las "
                             "dos ediciones (Tabla 12.10.4.3.2c-1, «30 and "
                             "larger»).")))
            continue
        out.append(Contraste(
            id=f"CPDM-BFLL-{D_pulg}", fuente="CPDM", pagina="55",
            que=f"B_FLL, Ø {D_pulg} in, 2.0 ft de relleno", unidad="",
            publicado=publicado, recalculado=publicado, referencia=ref,
            motor=motor,
            explicacion=(
                "El CPDM (2000) tabula B_fLL para el HS 20 por diametro y por "
                "relleno de 0.5 a 6.5 ft; AASHTO LRFD 9.a ed. (Tabla "
                "12.10.4.3.2c-1, pag. 12-66) la reduce a dos columnas (< 2.0 y "
                ">= 2.0 ft) y la ajusta por la distribucion longitudinal de la "
                "carga en los tubos pequeños (C12.10.4.3.2c). El CPDM manda "
                "ademas usar B_fe si es menor que B_fLL; la 9.a ed. no lo "
                "dice. M8 sigue la 9.a ed.")))
    return out


# ===========================================================================
# 3. D-load requerida por el metodo indirecto (ACPA CPDM, Ejs. 4-2, 4-5, 4-7)
# ===========================================================================

@dataclass(frozen=True)
class EjemploDload:
    id: str
    pagina: str
    D_in: float
    pared_in: float
    H_ft: float
    tipo: str
    W_E_cpdm: float          # lb/ft, con el termino de los riñones (Ec. 4)
    B_fe: float
    W_L_cpdm: float          # lb/ft, de la Tabla 42 del CPDM (HS 20, con IM)
    B_fLL: float
    publicado: float         # lb/ft/ft
    errata: str = ""


EJEMPLOS_DLOAD = (
    EjemploDload("CPDM-4-2", "60-62", 48, 5, 35.0, "tipo_1",      # literal-ok: Ej. 4-2 del CPDM
                 27791.0, 3.93, 0.0, 1.0, 1768.0),               # literal-ok: Ej. 4-2 del CPDM
    EjemploDload("CPDM-4-5", "67-69", 24, 3, 10.0, "tipo_4",      # literal-ok: Ej. 4-5 del CPDM
                 4466.0, 1.7, 0.0, 1.0, 1314.0),                 # literal-ok: Ej. 4-5 del CPDM
    EjemploDload("CPDM-4-7", "71-73", 24, 3, 2.0, "tipo_2",       # literal-ok: Ej. 4-7 del CPDM
                 952.0, 3.0, 1780.0, 2.2, 563.2,                 # literal-ok: Ej. 4-7 del CPDM
                 errata=("la Ec. 28 imprime el intermedio «D0.01 = 597.3» y "
                         "la respuesta «563.2»: rehecha con los datos que el "
                         "propio ejemplo escribe ((952/3 + 1780/2.2)/2) da "
                         "563.2, de modo que la errata es el intermedio, no "
                         "la respuesta. El paso 1 escribe ademas «H = 10» y "
                         "calcula con H = 2 ft (PL = 680 lb/ft).")),
)

# El intermedio que la Ec. 28 del Ej. 4-7 imprime (pag. 73) y que la cuenta
# no da: la errata del ejemplo.
CPDM_INTERMEDIO_4_7 = 597.3                                       # literal-ok: Ej. 4-7 del CPDM

# Las clases que el arnes ofrece a M8 para que la D-load requerida quede a la
# vista: II y V de ASTM C76M, 50 y 140 N/m/mm, como las imprime USACE EM
# 1110-2-2902 pag. B-7. NO es una transcripcion de M 170M al archivo: solo
# evita que la falta de las Clases III a V detenga la cuenta (la clase que M8
# elija aqui no se juzga).
CLASES_DEL_ARNES = {"concreto_reforzado": {"II": 50.0, "V": 140.0}}   # literal-ok: USACE pag. B-7


def _dload_aashto_a_mano(e: EjemploDload, W_L_plf: float) -> Tuple[float, Dict[str, float]]:
    """
    La D-load por AASHTO LRFD 9.a ed. 12.10.4.3.1 escrita A MANO en lb y
    pies, con los datos del ejemplo: W_E = VAF w B_c H (Ec. 12.10.2.1-1, sin
    termino de riñones), W_F = gamma_w pi D^2/4 (12.10.2.2, con el agua del
    motor), D = [(W_E + W_F)/B_FE + W_L/B_FLL]/S_i x 1.10 en el Tipo 1. El
    VAF y el B_FE son los del CPDM transcritos aqui (Ec. 4 e Ilustracion
    4.19), que son los de las Tablas 12.10.2.1-3 y 12.10.4.3.2a-1 de la 9.a
    ed. (lo comprobo la revision Fable); el B_FLL, el de la Tabla
    12.10.4.3.2c-1. Interpolados A MANO (`_interpolar_a_mano`), sin la
    funcion del motor.
    """
    VAF = dict(zip(TIPOS, CPDM_VAF))[e.tipo]
    i = TIPOS.index(e.tipo)
    xs = sorted(CPDM_BFE)
    B_FE = _interpolar_a_mano(e.D_in, tuple(float(x) for x in xs),
                              tuple(CPDM_BFE[x][i] for x in xs))
    B_FLL = _interpolar_a_mano(e.D_in, (12.0, 18.0, 24.0, 30.0),   # literal-ok: Tabla 12.10.4.3.2c-1
                               (2.4, 2.4, 2.4, 2.2))               # literal-ok: Tabla 12.10.4.3.2c-1
    B_c = (e.D_in + 2 * e.pared_in) / 12
    D_ft = e.D_in / 12
    W_E = VAF * 120.0 * B_c * e.H_ft                               # literal-ok: 120 pcf del ejemplo
    W_F = AGUA_PCF_MOTOR * math.pi * D_ft ** 2 / 4
    factor = 1.10 if e.tipo == "tipo_1" else 1.0                   # literal-ok: 12.10.4.3.1
    D = factor * ((W_E + W_F) / B_FE + W_L_plf / B_FLL) / D_ft
    return D, {"W_E": W_E, "W_F": W_F, "W_L": W_L_plf, "B_FE": B_FE,
               "B_FLL": B_FLL, "factor": factor}


def _dload_cpdm(e: EjemploDload) -> float:
    """La Ec. 28 del CPDM con los datos que el ejemplo imprime (F.S. 1.0)."""
    return (e.W_E_cpdm / e.B_fe + e.W_L_cpdm / e.B_fLL) / (e.D_in / 12)


def dload_del_motor(e: EjemploDload) -> Tuple[float, Dict[str, float]]:
    """
    `M8.verificar_concreto` con los datos del ejemplo en SI: relleno de 120
    pcf (el que M8 toma, 0.120 kcf del Manual de Puentes), sin paquete, la
    instalacion del ejemplo, la carga viva despreciada cuando el relleno pasa
    de 8 ft y de la luz (los dos primeros ejemplos la desprecian), y el
    diametro y la pared B de ASTM C76 del ejemplo. Devuelve (D en lb/ft/ft,
    los terminos de la sustitucion en lb/ft).
    """
    return _verificar_concreto_del_motor(
        D_in=e.D_in, pared_in=e.pared_in, H_ft=e.H_ft, tipo=e.tipo,
        conservar_carga_viva=bool(e.W_L_cpdm))


def _verificar_concreto_del_motor(*, D_in: float, pared_in: float,
                                  H_ft: float, tipo: str,
                                  conservar_carga_viva: bool = True
                                  ) -> Tuple[float, Dict[str, float]]:
    """La ruta real de M8 (`verificar_concreto`) para un tubo de concreto."""
    from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP
    D = D_in * PULG
    t = pared_in * PULG
    punto = CP["punto_A01"]()
    punto = replace(punto, cota_rasante=punto.cota_subrasante)
    material = replace(catalogo(TipoMaterial.CONCRETO_REFORZADO),
                       espesor_pared={round(D * 1000.0): t})       # literal-ok: mm por m
    carga_viva = ("conservar" if conservar_carga_viva
                  else "despreciar_3_6_1_2_6a")
    with declarados({"instalacion_estandar_concreto": tipo,
                     "carga_viva_bajo_relleno_alto": carga_viva}), \
            con_valor("clases_producto_por_relleno", CLASES_DEL_ARNES,
                      motivo="arnes de la validacion externa de M8: ofrece "
                             "las Clases II y V de USACE pag. B-7 para que la "
                             "D-load requerida quede a la vista"):
        r = M8.verificar_concreto(punto=punto, material=material,
                                  seccion=SeccionCircular(D),
                                  altura_relleno=H_ft * PIE_EN_METROS)
    (v,) = r.verificaciones
    sust = {m.simbolo: m.valor for m in v.paso.sustitucion}
    return (v.valor_obtenido / DLOAD_EN_N_M_MM,
            {"W_E": sust["W_E"] / PLF_EN_KN_M, "W_F": sust["W_F"] / PLF_EN_KN_M,
             "W_L": sust["W_L"] / PLF_EN_KN_M, "B_FE": sust["B_FE"],
             "B_FLL": sust["B_FLL"]})


def _contrastes_dload() -> List[Contraste]:
    out: List[Contraste] = []
    for e in EJEMPLOS_DLOAD:
        W_L = 0.0
        if e.W_L_cpdm:
            W_L, _IM, _veh = _hl93_a_mano(e.H_ft, e.D_in / 12,
                                          (e.D_in + 2 * e.pared_in) / 12)
        ref, t = _dload_aashto_a_mano(e, W_L)
        motor, _sust = dload_del_motor(e)
        recalc = _dload_cpdm(e)
        B_c = (e.D_in + 2 * e.pared_in) / 12
        rinones = 120.0 * B_c * B_c * (4 - math.pi) / 8            # literal-ok: Ec. 4 del CPDM
        partes = [
            f"W_E sin el termino de los riñones de la Ec. 4 del CPDM "
            f"(AASHTO 9.a ed. Ec. 12.10.2.1-1: W_E = F_e w B_c H): "
            f"{t['W_E']:,.0f} lb/ft contra {e.W_E_cpdm:,.0f}",
            f"el agua del tubo W_F = {t['W_F']:,.0f} lb/ft, que AASHTO "
            "12.10.4.3.1 suma a la tierra y el CPDM no",
        ]
        if t["factor"] != 1.0:
            partes.append("el factor 1.10 del Tipo 1 (12.10.4.3.1), que el "
                          "CPDM (2000) no aplica")
        if e.W_L_cpdm:
            partes.append(
                f"la carga viva HL-93 por 3.6.1.2.6b: W_L = {W_L:,.0f} lb/ft "
                f"contra {e.W_L_cpdm:,.0f} de la Tabla 42 del CPDM (HS 20), "
                f"con B_FLL = {t['B_FLL']:.2f} (Tabla 12.10.4.3.2c-1) contra "
                f"{e.B_fLL:.2f} (Ilustracion 4.21)")
        out.append(Contraste(
            id=e.id, fuente="CPDM", pagina=e.pagina,
            que=(f"D-load a 0.01 in, Ø {e.D_in:g} in pared B, {e.H_ft:g} ft "
                 f"de relleno de 120 pcf, Tipo {TIPOS.index(e.tipo) + 1}"),
            unidad="lb/ft/ft", publicado=e.publicado, recalculado=recalc,
            referencia=ref, motor=motor, errata=e.errata,
            explicacion=(
                "El ejemplo (CPDM 2000) y M8 (AASHTO LRFD 9.a ed.) difieren "
                "en: " + "; ".join(partes) + ". Lo comun —la Ec. 28 del CPDM "
                "y la 12.10.4.3.1-1, el VAF y el B_FE— coincide (contrastes "
                f"CPDM-VAF y CPDM-BFE). El termino de los riñones vale "
                f"{rinones:,.0f} lb/ft.")))
    return out


# ===========================================================================
# 4. Flotacion: empuje y relleno sumergido (ACPA DD 22, Ejemplo 1)
# ===========================================================================

def _contrastes_dd22() -> List[Contraste]:
    out: List[Contraste] = []
    D_in, pared_in, H_ft = 72.0, 7.0, 8.0                          # literal-ok: Ej. 1 de DD 22
    B_c_ft = (D_in + 2 * pared_in) / 12
    seccion = SeccionCircular(D_in * PULG)
    t = pared_in * PULG
    # --- empuje: el agua desplazada por el tubo (Ec. 2 de DD 22) -----------
    recalc_U = math.pi * B_c_ft ** 2 / 4 * 62.4                    # literal-ok: Ec. 2 de DD 22, 62.4 pcf
    ref_U = math.pi * B_c_ft ** 2 / 4 * AGUA_PCF_MOTOR
    motor_U = M8.empuje_flotacion_kn_m(seccion=seccion, espesor=t) / PLF_EN_KN_M
    out.append(Contraste(
        id="DD22-U", fuente="DD22", pagina="4",
        que="Empuje: agua desplazada por el tubo de 72 in pared B (B_c = 86 in)",
        unidad="lb/ft", publicado=2519.0, recalculado=recalc_U,     # literal-ok: Tabla 4 de DD 22
        referencia=ref_U, motor=motor_U,
        explicacion=("La misma ecuacion (gamma_w pi B_c^2/4, `M8."
                     "empuje_flotacion_kn_m`); el ejemplo lee 2519 de su "
                     "Tabla 4 y la Ec. 2 da 2517 con 62.4 pcf, el motor 2519 "
                     "con 9.81 kN/m3.")))
    # --- relleno sumergido sobre el tubo (Ecs. 4 y 5 de DD 22) -------------
    w_seco, SG = 110.0, 2.65                                       # literal-ok: Ej. 1 de DD 22
    w_sumergido = w_seco * (1 - 1 / SG)                            # Ec. 4 de DD 22
    recalc_W = 68.0 * (0.1073 * 7.17 ** 2 + H_ft * 7.17)           # literal-ok: Ec. 5 con los redondeos que imprime DD 22
    ref_W = w_sumergido * B_c_ft * H_ft
    gamma_sat = w_sumergido * PCF_EN_KN_M3 + GAMMA_AGUA_KN_M3
    with con_valor("peso_especifico_saturado_relleno_kn_m3", gamma_sat,
                   motivo="arnes de la validacion externa de M8: el saturado "
                          "de la arena de DD 22 (110 pcf seca, SG 2.65)"):
        W, _g = M8.peso_relleno_bajo_el_nivel_kn_m(
            seccion=seccion, espesor=t, altura_relleno=H_ft * PIE_EN_METROS,
            altura_sumergida=H_ft * PIE_EN_METROS)
    motor_W = W / PLF_EN_KN_M
    rinones = w_sumergido * 0.1073 * B_c_ft ** 2                   # literal-ok: Ec. 5 de DD 22
    out.append(Contraste(
        id="DD22-WI", fuente="DD22", pagina="4-5",
        que=("Peso del relleno sumergido sobre el tubo, 8 ft bajo el nivel "
             "de agua (arena de 110 pcf, SG 2.65)"),
        unidad="lb/ft", publicado=4276.0, recalculado=recalc_W,    # literal-ok: Ej. 1 de DD 22
        referencia=ref_W, motor=motor_W,
        errata=("el paso 4 escribe «WB = +4267 + 0 = +4276»: el sumando "
                "4267 es una transposicion de 4276, que es lo que da la Ec. 5 "
                "y lo que el ejemplo usa despues."),
        explicacion=(
            "El peso sumergido por unidad de volumen es el mismo: DD 22 Ec. 4, "
            f"w (1 - 1/SG) = {w_sumergido:.2f} pcf, y M8 gamma_sat - gamma_w "
            "(`M8.peso_relleno_bajo_el_nivel_kn_m`, con el saturado de esa "
            "arena). Difiere el VOLUMEN: DD 22 suma el relleno sobre los "
            f"riñones, 0.1073 B_c^2 ({rinones:,.0f} lb/ft), y M8 toma el "
            "prisma B_c H sobre la clave, la convencion declarada del "
            "proyecto (docstring de `M8.peso_relleno_kn_m`), que sujeta menos: "
            "del lado seguro en la flotacion. DD 22 redondea ademas w_I a 68 "
            "pcf y B_c a 7.17 ft.")))
    # --- el veredicto de V7 sobre el mismo caso, con los factores de M8 ----
    f = M8.factores_carga_flotacion(material=catalogo(TipoMaterial.CONCRETO_REFORZADO))
    margen_motor = f.gamma_EV * motor_W - f.gamma_WA * motor_U
    margen_mano = f.gamma_EV * ref_W - f.gamma_WA * ref_U
    # DD 22 paso 6: (WP + WW) + WB/FS = (1811 - 2519) + 4276/1.25.
    margen_dd22 = (1811.0 - 2519.0) + recalc_W / 1.25                 # literal-ok: pasos 1 a 6 de DD 22
    out.append(Contraste(
        id="DD22-V7", fuente="DD22", pagina="5",
        que=("Fuerza neta hacia abajo del tubo vacio con el relleno completo "
             "(signo + = no flota)"),
        unidad="lb/ft", publicado=2713.0, recalculado=margen_dd22,      # literal-ok: paso 6 de DD 22
        referencia=margen_mano, motor=margen_motor,
        explicacion=(
            "DD 22 (ASD) suma el peso del tubo (1 811 lb/ft) y divide el "
            "relleno entre un factor de seguridad de 1.25; V7 de M8 (LRFD, "
            f"Resistencia I) desprecia el peso propio (DC = 0, conservador) y "
            f"hace gamma_EV EV - gamma_WA U con gamma_EV = {f.gamma_EV:.2f} y "
            f"gamma_WA = {f.gamma_WA:.2f} (`M8.factores_carga_flotacion`), "
            "sobre el EV sin riñones de DD22-WI. Los dos metodos dan el mismo "
            "veredicto: el tubo no flota.")))
    return out


# ===========================================================================
# 5. TMC por tensiones admisibles de ASTM A796 (USACE EM 1110-2-2902, Cap. 4)
# ===========================================================================
# Pags. B-9 y B-10 (PDF 73 y 74, escaneadas: leidas en la imagen).
USACE_P_KPA = 94.850         # literal-ok: P = EL + LL, pag. B-9
USACE_S_M = 1.2              # literal-ok: S de la pag. B-10 (thrust)
USACE_S_PANDEO_MM = 1220.0   # literal-ok: s de la pag. B-10 (pandeo)
USACE_R_MM = 4.3713          # literal-ok: r, pag. B-10
USACE_FY = 227.53            # literal-ok: f_y = 33 000 psi, pag. B-10
USACE_FU = 310.0             # literal-ok: f_u, pag. B-10
USACE_E = 200000.0           # literal-ok: E = 2e11 N/m2, pag. B-10
USACE_K = 0.22               # literal-ok: k, pag. B-10
USACE_SF = 2.0               # literal-ok: SF, pag. B-10


def _fc_a_mano(S_mm: float) -> float:
    """f_c de A796 (ecs. 5 y 6) como la escribe USACE pag. B-10, MPa."""
    esb = USACE_K * S_mm / USACE_R_MM
    if S_mm < (USACE_R_MM / USACE_K) * math.sqrt(24 * USACE_E / USACE_FU):  # literal-ok: A796 ec. 5
        return USACE_FU - USACE_FU ** 2 / (48 * USACE_E) * esb ** 2           # literal-ok: A796 ec. 5
    return 12 * USACE_E / esb ** 2                                            # literal-ok: A796 ec. 6


def _contrastes_usace() -> List[Contraste]:
    T, f, A = M8.area_requerida_asd_a796(
        S_m=USACE_S_M, P_kPa=USACE_P_KPA, r_mm=USACE_R_MM, f_y=USACE_FY,
        f_u=USACE_FU, E=USACE_E, k=USACE_K, SF=USACE_SF)
    T_mano = USACE_P_KPA * USACE_S_M / 2
    A_mano = T_mano * USACE_SF / min(USACE_FY, _fc_a_mano(USACE_S_M * 1000.0))  # literal-ok: mm por m
    fc_motor = M8.tension_critica_de_pandeo(
        S_mm=USACE_S_PANDEO_MM, r_mm=USACE_R_MM, E=USACE_E, F_u=USACE_FU,
        k=USACE_K)
    fc_mano = _fc_a_mano(USACE_S_PANDEO_MM)
    nota_fuente = ("La pag. B-9 tiene dos inconsistencias propias que no tocan "
                   "esta cuenta: escribe EL = 56 550 N/m2 «(1,220 psf)» por "
                   "1 200 (10 ft x 120 pcf), y LL = 38 200 N/m2 cuando la suma "
                   "P = 94 850 usa 38 300, el valor de su tabla para 0.6 m "
                   "(2 ft) de cubierta, aunque el ejemplo tiene 3 m (10 ft). "
                   "El contraste parte de P = 94 850 N/m2, como el ejemplo.")
    return [
        Contraste(
            id="USACE-T", fuente="USACE", pagina="B-10",
            que="Empuje en la pared, T = P S/2", unidad="kN/m",
            publicado=56.910, recalculado=T_mano, referencia=T_mano, motor=T,  # literal-ok: pag. B-10
            explicacion="ASTM A796 ec. 3, `M8.area_requerida_asd_a796`. "
                        + nota_fuente),
        Contraste(
            id="USACE-A", fuente="USACE", pagina="B-10",
            que="Area requerida de pared, A = T SF / f_y", unidad="mm2/mm",
            publicado=0.5002, recalculado=A_mano, referencia=A_mano, motor=A,  # literal-ok: pag. B-10
            explicacion=("ASTM A796 num. 8, con el f_y de 33 000 psi del "
                         "ejemplo (M8 trae por defecto los 225 MPa de "
                         "A796-13; aqui se le pasa el del ejemplo).")),
        Contraste(
            id="USACE-FC", fuente="USACE", pagina="B-10",
            que="Tension critica de pandeo f_c, s = 1220 mm", unidad="MPa",
            publicado=272.0, recalculado=fc_mano, referencia=fc_mano,  # literal-ok: 2.72e8 N/m2, pag. B-10
            motor=fc_motor,
            explicacion=("ASTM A796 ecs. 5 y 6 = AASHTO 12.7.2.4 "
                         "(`M8.tension_critica_de_pandeo`); el ejemplo imprime "
                         "2.72e8 N/m2 (39 523 psi). Usa S = 1.2 m para el empuje "
                         "y s = 1 220 mm (48 in) para el pandeo: se respeta.")),
    ]


def _contrastes_clases() -> List[Contraste]:
    from src import criterios_adoptados as ca
    archivo = ca.CRITERIOS["clases_producto_por_relleno"].valor
    return [Contraste(
        id="USACE-CLASE-II", fuente="USACE", pagina="B-7",
        que="D-load a 0.01 in de la Clase II de ASTM C76M", unidad="N/m/mm",
        publicado=50.0, recalculado=50.0, referencia=50.0,       # literal-ok: pag. B-7
        motor=archivo["concreto_reforzado"]["II"],
        explicacion=("La unica clase transcrita en 'clases_producto_por_relleno' "
                     "(AASHTO M 170M). USACE imprime ademas I 40, III 65, IV 100 "
                     "y V 140 N/m/mm (ASTM C76M de su edicion); M8 no las "
                     "transcribe (ficha de DIFERIDO_CLASES_M170M) y este "
                     "documento no las usa como fuente: solo el arnes de la "
                     "D-load ofrece II y V para dejar la cuenta a la vista."))]


# ===========================================================================
# El conjunto, y lo que no se contrasto
# ===========================================================================

def contrastes() -> List[Contraste]:
    return (_contrastes_dd1() + _contrastes_tablas() + _contrastes_dload()
            + _contrastes_dd22() + _contrastes_usace() + _contrastes_clases())


# Los datos de DD 1 que la descomposicion usa (Ejs. 1 y 4, pags. 7 a 9): el
# area de reparto que el ejemplo imprime, la carga, la cubierta, el lado L
# (spread a, transito perpendicular) y R_o = D_o, la altura exterior.
DD1_DESCOMPOSICION = (
    # (id, H ft, P lb, A impresa ft2, L ft)
    ("DD1-EJ1", 2.0, 32000.0, 24.9, 1.67 + 4 + 1.15 * 2),      # literal-ok: Ej. 1 de DD 1
    ("DD1-EJ4", 6.0, 50000.0, 147.45, 1.67 + 4 + 1.15 * 6),    # literal-ok: Ej. 4 de DD 1
)
DD1_RO_FT = 3.08                                               # literal-ok: R_o que imprime DD 1


def descomposicion_dd1(cs: Sequence[Contraste]) -> List[Dict[str, float]]:
    """
    Cuanto del exceso de M8 sobre DD 1 es la PRESION en la clave (la edicion:
    HL-93, m = 1.20, LLDF por diametro, 0.06 D_i) y cuanto la LONGITUD
    EFECTIVA (DD 1 divide W_T entre L_e = L + 1.75 (3/4 R_o); M8 no reparte).
    Con S_L = B_c en los dos (en los dos ejemplos l_w >= B_c), el cociente
    motor/recalculado es exactamente (P_L / w) x (L_e / L): el test lo
    comprueba. Correcciones de la revision Fable (M-3: el §8 no lo
    cuantificaba).
    """
    por_id = {c.id: c for c in cs}
    out = []
    for id_, H_ft, P_lb, A, L in DD1_DESCOMPOSICION:
        c = por_id[id_]
        det = hl93_detalle(H_ft, 30 / 12, 37 / 12)            # literal-ok: Ø 30 in pared B de DD 1
        w = P_lb * (1 + 33 * (1.0 - 0.125 * H_ft) / 100) / A  # literal-ok: Eqs. 1 y 3 de DD 1
        L_e = L + 1.75 * (0.75 * DD1_RO_FT)                    # literal-ok: Eq. 2 de DD 1
        out.append({"id": id_, "H_ft": H_ft, "P_L": det["P_L_psf"], "w": w,
                    "presion": det["P_L_psf"] / w, "L": L, "L_e": L_e,
                    "longitud": L_e / L, "total": c.motor / c.recalculado,
                    "l_w": det["l_w"]})
    return out


def observacion_carga_viva(cs: Sequence[Contraste]) -> str:
    """La observacion del §8, con las cifras LEIDAS de los contrastes."""
    por_id = {c.id: c for c in cs}
    ej1, cp47 = por_id["DD1-EJ1"], por_id["CPDM-4-7"]
    d1, d4 = descomposicion_dd1(cs)
    return (
    "No es un defecto —el motor reproduce su metodo en todos los "
    "contrastes—, pero es la diferencia mayor de este documento y conviene "
    "que la juzgue un ingeniero: con poco relleno, la carga viva de M8 sobre "
    "un tubo de concreto pequeño sale bastante por encima de la de ACPA "
    f"(2000 y 2009): {ej1.diferencia_pct:+.0f} % en DD1-EJ1 (30 in, 2 ft) y "
    f"la D-load {cp47.diferencia_pct:+.0f} % en CPDM-4-7 (24 in, 2 ft), casi "
    "toda por la carga viva. CASI TODO ES LA LONGITUD EFECTIVA, no la "
    f"edicion (tabla de abajo): en DD1-EJ1 la presion en la clave pesa "
    f"{d1['presion'] - 1:+.1%} y no repartir con L_e {d1['longitud'] - 1:+.1%}; "
    f"en DD1-EJ4 la presion {d4['presion'] - 1:+.1%} (la edicion es ahi "
    f"FAVORABLE) y la L_e {d4['longitud'] - 1:+.1%}. Y no repartir con L_e NO "
    "es una lectura libre de M8: es lo que la 9.a ed. escribe. 12.10.2.3 "
    "(pag. 12-54, PDF 1692): «Live loads shall be as specified in Article "
    "3.6 and shall be distributed through the earth cover as specified in "
    "Article 3.6.1.2.6. For standard installations, the live load on the "
    "pipe shall be assumed to have a uniform vertical distribution across "
    "the top of the pipe», sin longitud efectiva; y C12.10.4.3.2c (pag. "
    "12-66, PDF 1704): «The bedding factor has been adjusted in Table "
    "12.10.4.3.2c-1 to account for this higher distribution length», de "
    "modo que sumar ademas la L_e de ACPA contaria dos veces el reparto "
    "longitudinal. La revision Fable lo dictamino como la lectura literal de "
    "la 9.a ed. y no un defecto, con una reserva que sigue en pie: ninguna "
    "de estas fuentes resuelve un ejemplo con la edicion 2013 o posterior, y "
    "solo uno asi cerraria W_L con un numero de terceros.")


NO_CONTRASTADO = (
    ("PPI, Ejemplos 1 y 2 (HDPE y PP)",
     "El Ejemplo 2 (HDPE de 48 in, 2 ft de relleno) usa un vehiculo de obra "
     "(45 kip en 18 x 18 in, IM = 1.0) que M8 no admite —su carga viva es el "
     "HL-93 fijo— y un M_s por combinacion de suelos de la Tabla 7.3-6 del PPI "
     "(S_c = 0.53 sobre M_sb = 3 500 psi) donde M8 interpola la Tabla "
     "12.12.3.5-1 de AASHTO por la presion; el Ejemplo 1 es de polipropileno, "
     "que M8 no trae. Las ECUACIONES coinciden en forma (P_sp con 0.11 D_o, "
     "S_H, VAF, F_2, la distribucion con 0.06 D_i y LLDF 1.15), pero ningun "
     "numero del ejemplo se puede reproducir con las entradas de M8. (El "
     "ejemplo tiene ademas una errata de transcripcion: su VAF escribe "
     "«27.98 + 2.92» por 7.98 + 2.92, y el resultado, 0.32, es el de 7.98.)"),
    ("USACE, costura y factor de flexibilidad del TMC (pag. B-11)",
     "M8 verifica la costura y el FF por AASHTO LRFD 12.7.2 dentro de "
     "`M8.verificar_tmc`, sin funcion publica para el contraste ASD; y la "
     "pagina escaneada da I = «39,198 mm4/mm (2.392 in.4/ft)», que no es una "
     "conversion consistente (2.392 in4/ft son 3 266 mm4/mm; 39 198 es "
     "2.392 x 16 387, el factor de in3 a mm3), con FF = 0.00019 mm/N "
     "calculado sobre ese I. No se usa como oraculo."),
    ("USACE, Cap. 3 (tubo de concreto por Marston-Spangler)",
     "D = (W_l + W_e) H_f /(B_f S_i) = 57 N/m/mm (pag. B-8) con el factor de "
     "carga de Spangler (cama de cuna de concreto, B_f = 6.098): es el metodo "
     "de las camas historicas, que AASHTO 12.10.2.1 sustituye por las "
     "instalaciones estandar. Solo su tabla de clases se contrasta "
     "(USACE-CLASE-II)."),
)


# ===========================================================================
# El documento
# ===========================================================================

def _cifra(x: Optional[float], unidad: str) -> str:
    if x is None:
        return "—"
    if unidad in ("", "mm2/mm"):
        return f"{x:.4g}" if unidad == "" else f"{x:.4f}"
    if abs(x) >= 1000:
        return f"{x:,.0f}".replace(",", " ")
    return f"{x:.4g}"


def generar() -> str:
    cs = contrastes()
    n = {c: sum(1 for x in cs if x.clase == c)
         for c in (COINCIDE, METODO, SIN_FUENTE, DEFECTO)}
    erratas = [x for x in cs if x.errata_de_la_fuente]
    lineas: List[str] = [
        "# Validación externa de M8: el conducto contra ejemplos publicados",
        "",
        "> **Este documento se GENERA.** No se edita a mano: lo produce "
        "`tests/apoyo/validacion_conducto.py` y "
        "`tests/test_validacion_conducto.py` lo regenera a memoria y lo "
        "compara. Regenerar: `python -m tests.apoyo.validacion_conducto "
        "--escribir`.",
        "",
        "## 1. Qué se juzga, y con qué regla",
        "",
        "Cada contraste lleva cuatro cifras en la unidad de la fuente: lo "
        "**publicado** (con su página impresa), lo **recalculado** con las "
        "fórmulas y los datos del propio ejemplo, la **referencia** —el "
        "método que M8 implementa, escrito a mano en otra unidad y sin llamar "
        "a M8— y lo que da el **motor**. La clase se decide en este orden:",
        "",
        f"- **DEFECTO**: el motor no reproduce su propio método (motor frente "
        f"a referencia, fuera de `TOL_REL_MOTOR` = {TOL_REL_MOTOR:g}).",
        f"- **COINCIDE**: el método de M8 da lo mismo que el ejemplo "
        f"(referencia frente a recalculado, dentro de "
        f"`TOL_REL_CIFRA_IMPRESA` = {TOL_REL_CIFRA_IMPRESA:g}).",
        "- **METODO**: el ejemplo usa otra edición u otro método; la "
        "diferencia se explica por causa.",
        "- **SIN FUENTE**: no hay cifra publicada; el caso ejercita una rama "
        "del motor que ningún ejemplo alcanza.",
        "",
        "**Dos categorías que no se suman** (corrección de la revisión Fable, "
        "A-1): sólo **COINCIDE** es *contrastado con la fuente*. **METODO** y "
        "**SIN FUENTE** dicen que el motor *reproduce su propio método* —la "
        "lectura de la edición vigente que el arnés escribe a mano—: prueban "
        "que M8 está bien programado según esa lectura, no que un tercero la "
        "valide.",
        "",
        "Una **errata de la fuente** (publicado frente a recalculado) se "
        "anota aparte: lo que rige es lo recalculado.",
        "",
        "## 2. Fuentes",
        "",
        "| Clave | Documento | URL |",
        "|---|---|---|",
    ]
    for k, (t, u) in FUENTES.items():
        lineas.append(f"| {k} | {t} | {u} |")
    lineas += [
        "",
        "Los PDF no se versionan (copyright; CLAUDE.md). Las cifras se "
        "transcribieron leyendo cada página; las del USACE, escaneadas, en la "
        "imagen.",
        "",
        "## 3. Resultado",
        "",
        f"**{len(cs)} contrastes. Contrastados con la fuente: {n[COINCIDE]} "
        f"(coinciden). El motor reproduce su propio método: "
        f"{n[METODO] + n[SIN_FUENTE]} ({n[METODO]} difieren de la fuente por "
        f"edición o método, {n[SIN_FUENTE]} sin cifra publicada). Defectos "
        f"del motor: {n[DEFECTO]}.** {len(erratas)} con errata de la fuente. "
        "Ninguna cifra de W_L ni de D-load de M8 está contrastada con una "
        "fuente: todas son de la segunda categoría.",
        "",
        "| Id | Fuente, pág. | Qué | Unidad | Publicado | Recalculado | "
        "Referencia (método de M8) | Motor | Motor − recalculado | Clase |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for c in cs:
        lineas.append(
            f"| {c.id} | {c.fuente}, {c.pagina} | {c.que} | {c.unidad} | "
            f"{_cifra(c.publicado, c.unidad)} | {_cifra(c.recalculado, c.unidad)} "
            f"| {_cifra(c.referencia, c.unidad)} | {_cifra(c.motor, c.unidad)} | "
            f"{c.diferencia_pct:+.2f} % | {c.clase}"
            f"{' (errata de la fuente)' if c.errata_de_la_fuente else ''} |")
    lineas += ["", "## 4. Por qué difiere cada contraste de método, y los "
               "casos sin fuente", ""]
    vistos = set()
    for c in cs:
        if c.clase not in REPRODUCE_SU_METODO or c.explicacion in vistos:
            continue
        vistos.add(c.explicacion)
        lineas.append(f"- **{c.id}** — {c.explicacion}")
    lineas += ["", "## 5. Lo que coincide", ""]
    vistos = set()
    for c in cs:
        if c.clase != COINCIDE or c.explicacion in vistos:
            continue
        vistos.add(c.explicacion)
        lineas.append(f"- **{c.id}** — {c.explicacion}")
    lineas += ["", "## 6. Erratas de las fuentes", ""]
    for c in erratas:
        texto = c.errata or (f"publicado {_cifra(c.publicado, c.unidad)} "
                             f"frente a {_cifra(c.recalculado, c.unidad)} "
                             "recalculado")
        lineas.append(f"- **{c.id}** — {texto}")
    lineas += ["", "## 7. Lo que no se contrastó, y por qué", ""]
    for titulo, texto in NO_CONTRASTADO:
        lineas.append(f"- **{titulo}.** {texto}")
    lineas += [
        "",
        "## 8. Observación para el dueño: la carga viva sobre tubos pequeños",
        "",
        observacion_carga_viva(cs),
        "",
        "| Contraste | Relleno | P_L de M8 (lb/ft²) | w de DD 1 (lb/ft²) | "
        "Presión: P_L / w | L (ft) | L_e (ft) | Longitud: L_e / L | Total: "
        "motor / recalculado |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for d in descomposicion_dd1(cs):
        lineas.append(
            f"| {d['id']} | {d['H_ft']:g} ft | {d['P_L']:,.0f} | "
            f"{d['w']:,.0f} | {d['presion'] - 1:+.1%} | {d['L']:.2f} | "
            f"{d['L_e']:.2f} | {d['longitud'] - 1:+.1%} | "
            f"{d['total'] - 1:+.1%} |")
    lineas += [
        "",
        "El total es el producto de los dos factores porque en los dos "
        "ejemplos l_w ≥ B_c (M8 toma W_L = P_L·B_c) y DD 1 toma S_L = B_c.",
        "",
        "## 9. Defectos del motor",
        "",
        ("Ninguno: en todos los contrastes el motor reproduce su propio "
         "método, y donde el ejemplo usa la misma edición, el mismo número. "
         "Eso no valida la lectura de la carga viva ni la D-load (ver §3 y "
         "§8)."
         if n[DEFECTO] == 0 else
         "Ver la tabla del §3: las filas DEFECTO."),
        "",
    ]
    return "\n".join(lineas)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    texto = generar()
    if "--escribir" in args:
        DOCUMENTO.write_text(texto, encoding="utf-8")
        print(f"escrito {DOCUMENTO}")
        return 0
    actual = DOCUMENTO.read_text(encoding="utf-8") if DOCUMENTO.exists() else ""
    print("sincronizado" if actual == texto else "DESINCRONIZADO")
    return 0 if actual == texto else 1


if __name__ == "__main__":
    raise SystemExit(main())
