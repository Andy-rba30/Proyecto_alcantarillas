"""
tests/apoyo/validacion_cabezal.py
=================================
La VALIDACION EXTERNA de M9 (VE-3.3): las funciones del cabezal contra los
EJEMPLOS RESUELTOS que publican dos departamentos de transporte de EE. UU.,
generada en `docs/validacion_cabezal.md`. `tests/test_validacion_cabezal.py`
lo regenera a memoria y lo compara, de modo que el documento no se puede
desincronizar del programa sin que la suite lo diga.

Regenerar::

    python -m tests.apoyo.validacion_cabezal --escribir

LAS DOS FUENTES (fuera del repositorio: llevan su propia licencia y los PDF
del proyecto viven en el repositorio de normas; aqui solo estan las CIFRAS
transcritas, cada una con su pagina o su celda)
------------------------------------------------------------------------
1. Caltrans, *Bridge Design Practice*, Cap. 11.2 «Earth Retaining Systems»,
   oct. 2022, §11.2.2 «Reinforced Concrete Retaining Wall Design Example»
   (AASHTO-CA BDS-8, es decir AASHTO LRFD 8.a ed. con las enmiendas de
   California), pags. impresas 11.2-13 a 11.2-60. Muro en voladizo de 23 ft
   sobre zapata de 19 ft, relleno con talud, sismo con k_h = 0.28.
2. Colorado DOT, *Bridge Design Manual*, Example 11 «Cast-in-Place Concrete
   Cantilever Retaining Wall», hoja de calculo de feb. 2023, hoja «Ex.11».
   Muro de 15 ft sobre zapata de 10 ft, relleno horizontal, Coulomb. La hoja
   calcula «as displayed» (lo dice su celda AF1): cada intermedio se redondea
   a lo que muestra, y eso explica las diferencias de la tercera cifra.
   Su Example 8 (aleta en voladizo de un estribo integral) no se contrasta:
   ver `NO_CONTRASTABLE`.

QUE SE COMPARA CON QUE
----------------------
Por cada cifra hay TRES numeros:
  * PUBLICADO    lo que imprime la fuente;
  * RECALCULADO  lo que da la PROPIA formula de la fuente, en sus unidades
                 (in, ft, kip, ksi), escrita aqui de nuevo y sin pasar por M9.
                 Si difiere de lo publicado, la fuente tiene una ERRATA y se
                 compara contra lo recalculado, no contra lo impreso;
  * MOTOR        lo que devuelve la funcion de M9 con las mismas entradas
                 convertidas a SI, devuelto a las unidades de la fuente.
El juicio es uno de cuatro: COINCIDE, ERRATA DE LA FUENTE (el motor coincide
con lo recalculado), DIFIERE POR METODO (declarado, con la diferencia de
formula) y DEFECTO DEL MOTOR (ninguno declarado: el test exige cero).

LA TOLERANCIA es la de un ejemplo impreso, `TOLERANCIA_EJEMPLO_IMPRESO` de
`tests/apoyo/validacion_externa.py` (1 %): las dos fuentes imprimen tres o
cuatro cifras y redondean los intermedios. Una diferencia mayor sin errata ni
metodo declarados es un DEFECTO.

Lo que este modulo NO hace: no corrige el motor ni la tolerancia para que un
contraste pase, y no lee ningun PDF ni hoja de calculo en la suite (las
cifras estan transcritas con su cita).
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple, Union

from src import datos_sitio as ds
from src.constantes_fisicas import (KIP_EN_KN, KSI_EN_MPA, PIE_EN_METROS,
                                    PULGADA_EN_MM)
from src.constantes_normativas import (ORIENTACION_PARALELO_AL_TRAFICO)
from src.modelos import CombinacionDeEstabilidad, CondicionAnalisis
from src.modulos import M9_cabezal as M9
from tests.apoyo.validacion_conducto import TOL_REL_MOTOR
from tests.apoyo.validacion_externa import (TOLERANCIA_EJEMPLO_IMPRESO,
                                            dentro_de)

RAIZ = Path(__file__).resolve().parents[2]
DOCUMENTO = RAIZ / "docs" / "validacion_cabezal.md"

# --- Unidades: factores exactos, de `constantes_fisicas` ------------------
FT = PIE_EN_METROS                       # ft -> m
IN = PULGADA_EN_MM / 1000.0              # in -> m
KIP = KIP_EN_KN                          # kip -> kN
KLF = KIP / FT                           # kip/ft -> kN/m
KIPFT_POR_FT = KIP                       # (kip·ft)/ft -> (kN·m)/m
KSF = KIP / FT ** 2                      # ksf -> kPa
KCF = KIP / FT ** 3                      # kcf -> kN/m3
KSI = KSI_EN_MPA                         # ksi -> MPa
IN2_POR_FT = IN ** 2 / FT * 1.0e6        # in2/ft -> mm2/m
B_FRANJA_IN = 12.0                       # la franja de 1 ft de las dos fuentes

CALTRANS = "Caltrans BDP 11.2.2"
CDOT = "CDOT Ex. 11"
FUENTES = {
    CALTRANS: ("Caltrans, *Bridge Design Practice*, Cap. 11.2, oct. 2022, "
               "§11.2.2 «Reinforced Concrete Retaining Wall Design Example» "
               "(AASHTO-CA BDS-8). Citas: «p. 11.2-xx» es la pagina impresa; "
               "la del PDF del capitulo es la misma cifra xx."),
    CDOT: ("Colorado DOT, *Bridge Design Manual*, Example 11 «Cast-in-Place "
           "Concrete Cantilever Retaining Wall», hoja de calculo feb. 2023, "
           "hoja «Ex.11». Citas: celda de esa hoja. La hoja calcula «as "
           "displayed» (celda AF1)."),
}

JUICIO_COINCIDE = "coincide"
JUICIO_ERRATA = "errata de la fuente; el motor coincide con lo recalculado"
JUICIO_METODO = "difiere por método (declarado)"
JUICIO_DEFECTO = "DEFECTO DEL MOTOR"

Numero = Union[float, bool]


@dataclass(frozen=True)
class Contraste:
    ejemplo: str
    paso: str
    unidad: str
    publicado: Numero
    recalculado: Numero
    motor: Numero
    cita: str
    funcion: str
    metodo: str = ""      # por que el motor difiere de lo recalculado
    errata: str = ""      # por que la fuente difiere de su propia cuenta
    # LA REFERENCIA PROPIA DEL MOTOR (correcciones de la revision Fable,
    # M-1): en una fila con `metodo`, lo que el motor TIENE que dar con SU
    # metodo, escrito aqui aparte (sin llamar a M9). Sin ella, cualquier
    # valor del motor fuera del 1 % pasaba por «difiere por metodo»: un Ec
    # un 4 a 10 % distinto sobrevivia. Con ella, el motor que no la sigue
    # (fuera de `TOL_REL_MOTOR`) es un DEFECTO, cuadre o no con la fuente.
    referencia: Optional[Numero] = None

    def diferencia_fuente(self) -> Optional[float]:
        return _rel(self.publicado, self.recalculado)

    def diferencia_motor(self) -> Optional[float]:
        return _rel(self.motor, self.recalculado)

    def fuente_cuadra(self) -> bool:
        return _igual(self.publicado, self.recalculado)

    def motor_cuadra(self) -> bool:
        return _igual(self.motor, self.recalculado)

    def motor_sigue_su_referencia(self) -> bool:
        return (self.referencia is not None
                and dentro_de(self.motor / self.referencia - 1.0,
                              TOL_REL_MOTOR))

    @property
    def juicio(self) -> str:
        if self.referencia is not None and not self.motor_sigue_su_referencia():
            return JUICIO_DEFECTO
        if not self.motor_cuadra():
            return (JUICIO_METODO if self.metodo
                    and self.motor_sigue_su_referencia() else JUICIO_DEFECTO)
        if self.errata:
            return JUICIO_ERRATA
        return JUICIO_COINCIDE if self.fuente_cuadra() else JUICIO_DEFECTO


def _rel(a: Numero, b: Numero) -> Optional[float]:
    if isinstance(a, bool) or isinstance(b, bool):
        return None
    return a / b - 1.0


def _igual(a: Numero, b: Numero) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    return dentro_de(a / b - 1.0, TOLERANCIA_EJEMPLO_IMPRESO)


# ===========================================================================
# Las formulas DE LA FUENTE, en sus unidades (script propio, sin M9)
# ===========================================================================

def ka_coulomb_aashto(*, phi: float, delta: float, theta: float,
                      beta: float) -> float:
    """
    AASHTO LRFD ec. 3.11.5.3-1 (la que CDOT escribe en su celda AQ19), con
    theta el angulo del trasdos sobre la horizontal y beta el talud del
    relleno: Ka = sen²(θ+φ) / [Γ·sen²θ·sen(θ−δ)].
    """
    r = math.radians
    gamma = (1 + math.sqrt(math.sin(r(phi + delta)) * math.sin(r(phi - beta))
                           / (math.sin(r(theta - delta))
                              * math.sin(r(theta + beta))))) ** 2
    return math.sin(r(theta + phi)) ** 2 / (
        gamma * math.sin(r(theta)) ** 2 * math.sin(r(theta - delta)))


def flexion_us(*, As: float, d: float, fc: float, fy: float, beta_1: float
               ) -> dict:
    """AASHTO 5.6.3.1.1-4 y 5.6.3.2.2-1, por pie: in2, in, ksi -> kip-ft."""
    a = As * fy / (0.85 * fc * B_FRANJA_IN)        # literal-ok: alfa_1 de 5.6.2.2
    c = a / beta_1
    Mn = As * fy * (d - a / 2) / 12.0              # kip-in -> kip-ft
    return {"a": a, "c": c, "Mn": Mn, "eps_t": 0.003 * (d - c) / c}


def acero_para_momento_us(*, Mu: float, phi: float, d: float, fc: float,
                          fy: float) -> float:
    """El As (in2/ft) con phi·Mn = Mu: la cuadratica de la seccion simple."""
    R = 2 * Mu * 12.0 / (phi * 0.85 * fc * B_FRANJA_IN * d ** 2)
    return 0.85 * fc / fy * (1 - math.sqrt(1 - R)) * B_FRANJA_IN * d


def mcr_us(*, h: float, fc: float, gamma_3: float) -> float:
    """AASHTO 5.6.3.3-1 sin presfuerzo: γ3·γ1·fr·S, fr = 0.24√f'c (ksi)."""
    S = B_FRANJA_IN * h ** 2 / 6
    return gamma_3 * 1.6 * 0.24 * math.sqrt(fc) * S / 12.0


def fisuracion_us(*, Ms: float, As: float, d: float, h: float, dc: float,
                  n: float, gamma_e: float) -> dict:
    """
    AASHTO 5.6.7 con la seccion fisurada elastica, como la escriben las dos
    fuentes: k = √(2ρn+(ρn)²) − ρn, j = 1 − k/3, f_ss = M/(As·j·d);
    β_s = 1 + dc/[0.7(h − dc)]; s = 700γe/(β_s·f_ss) − 2dc.
    """
    rho_n = As / (B_FRANJA_IN * d) * n
    k = math.sqrt(2 * rho_n + rho_n ** 2) - rho_n
    j = 1 - k / 3
    fss = Ms * 12.0 / (As * j * d)
    beta_s = 1 + dc / (0.7 * (h - dc))
    return {"k": k, "j": j, "fss": fss, "beta_s": beta_s,
            "s_max": 700 * gamma_e / (beta_s * fss) - 2 * dc}


def fss_por_inercia_us(*, Ms: float, As: float, d: float, n: float) -> float:
    """La f_ss de Caltrans (p. 11.2-36): x, I_cr y n·M·(d − x)/I_cr."""
    B_ = n * As / B_FRANJA_IN
    C_ = 2 * n * d * As / B_FRANJA_IN
    x = math.sqrt(B_ ** 2 + C_) - B_
    I = B_FRANJA_IN * x ** 3 / 3 + n * As * (d - x) ** 2
    return n * Ms * 12.0 * (d - x) / I


def n_aashto_us(*, fc: float) -> float:
    """
    n = Es/Ec con el Ec del comentario C5.4.2.4-1 de AASHTO LRFD 9.a ed.
    (pag. 5-20, PDF 379: «For normal weight concrete with wc = 0.145 kcf, Ec
    may be taken as 2,500 f'c^0.33»), Es = 29 000 ksi (5.4.3.2). Es el metodo
    de M9, escrito aqui sin llamarlo: la REFERENCIA de las filas de metodo.
    """
    return 29000.0 / (2500.0 * fc ** 0.33)


def vc_us(*, beta: float, fc: float, dv: float) -> float:
    """AASHTO 5.7.3.3-3: Vc = 0.0316·β·√f'c·b·dv (kip por pie)."""
    return 0.0316 * beta * math.sqrt(fc) * B_FRANJA_IN * dv


def dv_us(*, de: float, a: float, h: float) -> float:
    """AASHTO 5.7.2.8: dv = max(de − a/2, 0.9·de, 0.72·h)."""
    return max(de - a / 2, 0.9 * de, 0.72 * h)


def temperatura_ec_us(*, b: float, h: float, fy: float) -> float:
    """AASHTO 5.10.6-1 SIN acotar, como la celda Y455 de CDOT (in2/ft)."""
    return 1.30 * b * h / (2 * (b + h) * fy)


def temperatura_us(*, b: float, h: float, fy: float) -> float:
    """AASHTO 5.10.6-1 con el tope de 5.10.6-2 (0.11 a 0.60 in2/ft)."""
    return min(max(temperatura_ec_us(b=b, h=h, fy=fy), 0.11), 0.60)


# La ec. 5.10.6-1 es lineal en 1/f_y. Para que el piso de 5.10.6-2 (0.11
# in2/ft) no tape la ecuacion del motor --los tres casos de CDOT dan de 0.072
# a 0.083--, el motor se llama con f_y / ESCALA_FY_TEMPERATURA (el resultado
# cae dentro de la banda 0.11-0.60) y se divide entre la misma escala. Una
# potencia de dos: la division es exacta en coma flotante.
ESCALA_FY_TEMPERATURA = 2.0


def _temperatura_ec_motor(*, b_in: float, h_in: float, fy_ksi: float) -> float:
    """La ec. 5.10.6-1 de M9 (in2/ft), leida por la escala de f_y."""
    return (M9.acero_de_temperatura_aashto(
        ancho=b_in * IN, espesor=h_in * IN,
        fy=fy_ksi / ESCALA_FY_TEMPERATURA * KSI)
        / IN2_POR_FT / ESCALA_FY_TEMPERATURA)


def presion_uniforme_us(*, V: float, M_punta: float, B: float) -> dict:
    """AASHTO 11.6.3.2 en suelo: x = ΣM/V, e = B/2 − x, q = V/(B − 2e)."""
    x = M_punta / V
    e = B / 2 - x
    return {"x": x, "e": e, "Bp": B - 2 * e, "q": V / (B - 2 * e)}


def presion_lineal_us(*, V: float, M_punta: float, B: float) -> dict:
    """AASHTO 10.6.5: trapecio V/B(1 ± 6e/B) o triangulo 2V/(3x)."""
    x = M_punta / V
    e = B / 2 - x
    if abs(e) <= B / 6:
        return {"q_punta": V / B * (1 + 6 * e / B),
                "q_talon": V / B * (1 - 6 * e / B)}
    return {"q_punta": 2 * V / (3 * x), "q_talon": 0.0}


# ===========================================================================
# El motor: M9 con las mismas entradas en SI
# ===========================================================================

def _combo(*, V: float, M_punta: float, B: float) -> CombinacionDeEstabilidad:
    """Una combinacion ya resuelta (V y ΣM respecto de la punta, por pie)."""
    return CombinacionDeEstabilidad(
        nombre="ejemplo", marco="LRFD", condicion=CondicionAnalisis.ESTATICO,
        factores=(), N=V * KLF, H=0.0, M_estabilizante=M_punta * KIPFT_POR_FT,
        M_volcante=0.0, B=B * FT)


def _uniforme_motor(*, V: float, M_punta: float, B: float):
    """`M9.presion_contacto_base`, rama de SUELO, con el momento al centro."""
    momento_centro = V * B / 2 - M_punta
    return M9.presion_contacto_base(N=V * KLF,
                                    momento_neto=momento_centro * KIPFT_POR_FT,
                                    B=B * FT, cimentacion_en_roca=False)


class _SitioDeLaFuente:
    """
    Los dos [S] que la tabla de h_eq de AASHTO 3.11.6.4 pide, declarados por
    la MISMA puerta que una sesion (`datos_sitio.establecer_dato_dinamico`)
    mientras dure el bloque, y retirados al salir: el muro de CDOT es
    PARALELO al trafico, a 2 ft del borde (celdas A8 y Q61).
    """

    CLAVES = {
        "orientacion_muro_respecto_al_trafico": ORIENTACION_PARALELO_AL_TRAFICO,
        "distancia_borde_calzada_al_trasdos_m": 2.0 * FT,
    }

    def __enter__(self):
        self._antes = {k: ds.datos_dinamicos().get(k) for k in self.CLAVES}
        for clave, valor in self.CLAVES.items():
            ds.establecer_dato_dinamico(
                clave, valor,
                "CDOT Example 11, hoja Ex.11, celdas A8 y Q61 (muro junto al "
                "arcen, trafico a 2 ft del trasdos): dato de un EJEMPLO "
                "publicado, no de esta obra",
                "2023-02", origen="tests/apoyo/validacion_cabezal.py")
        return self

    def __exit__(self, *exc):
        for clave, previo in self._antes.items():
            ds.quitar_dato_dinamico(clave)
            if previo is not None:
                ds.establecer_dato_dinamico(
                    clave, previo.dato.valor, previo.dato.trazabilidad,
                    previo.fecha, origen=previo.origen)
        return False


# ===========================================================================
# CDOT Example 11
# ===========================================================================

def contrastes_cdot() -> Tuple[Contraste, ...]:
    C: List[Contraste] = []
    add = C.append
    fc, fy = 4.5, 60.0                       # Q36, T316
    phi, delta, theta = 34.0, 22.67, 89.0    # AM19, AM22, AM21
    gamma_s = 0.13                           # Q20, kcf
    efw = 0.036                              # Q25: Ka·γs con el minimo de BDM 11.5
    H, TF, B = 15.0, 1.25, 10.0              # Q52, Q56, Q55
    h_tallo = 21.0                           # 1'-9" (Q54 = 1.75 ft)

    # --- Empuje -------------------------------------------------------------
    add(Contraste(
        CDOT, "Ka de Coulomb (φ = 34°, δ = 22.67°, θ = 89° de la hoja, "
        "que en M9 es β = 90° − θ = 1°; relleno horizontal)", "—",
        0.261, ka_coulomb_aashto(phi=phi, delta=delta, theta=theta, beta=0.0),
        M9.k_a_coulomb(phi_grados=phi, i_grados=0.0, beta_grados=90.0 - theta,
                       delta_grados=delta),
        "AQ19 (= Q23)", "M9.k_a_coulomb",
        metodo="", errata=""))
    k_eq = efw / gamma_s
    for altura, celda, paso in ((H + TF, "T138", "EHH de estabilidad, "
                                 "½·EFW·(H+TF)²·cos δ"),
                                (H, "K331", "EHH del alzado, ½·EFW·H²·cos δ")):
        P = M9.empuje_activo_estatico(gamma_relleno=gamma_s * KCF, k_a=k_eq,
                                      H=altura * FT) / KLF
        add(Contraste(
            CDOT, paso, "kip/ft", {"T138": 4.39, "K331": 3.74}[celda],
            0.5 * efw * altura ** 2 * math.cos(math.radians(delta)),
            P * math.cos(math.radians(delta)), celda,
            "M9.empuje_activo_estatico (la componente horizontal, cos δ, la "
            "toma aqui el arnes)"))
    P = M9.empuje_activo_estatico(gamma_relleno=gamma_s * KCF, k_a=k_eq,
                                  H=(H + TF) * FT) / KLF
    add(Contraste(
        CDOT, "EHV, ½·EFW·(H+TF)²·sen δ", "kip/ft", 1.83,
        0.5 * efw * (H + TF) ** 2 * math.sin(math.radians(delta)),
        P * math.sin(math.radians(delta)), "T133",
        "M9.empuje_activo_estatico (sen δ en el arnes)"))
    with _SitioDeLaFuente():
        for altura, celda in ((H + TF, "T139"), (H, "K332")):
            LS = M9.empuje_sobrecarga_trasdos(
                gamma_relleno=gamma_s * KCF, k_a=k_eq, H=altura * FT,
                altura_muro_total=(H + TF) * FT) / KLF
            add(Contraste(
                CDOT, f"LSH, EFW·h_eq·{'(H+TF)' if celda == 'T139' else 'H'} "
                "con h_eq de la Tabla 3.11.6.4-2 (paralelo, ≥ 1.0 ft)",
                "kip/ft", {"T139": 1.17, "K332": 1.08}[celda],
                efw * 2.0 * altura, LS, celda,
                "M9.empuje_sobrecarga_trasdos (h_eq de "
                "M9.h_eq_sobrecarga_trasdos)"))

    # --- Excentricidad y presion de contacto (AASHTO 11.6.3.2) -------------
    combos = (("Strength Ia", 19.86, 128.95, 52.33, "N204", None),
              ("Extreme IIa", 17.12, 101.50, 49.38, "N207", None),
              ("Strength Ib", 27.78, 179.27, 52.33, "W220", "W221"),
              ("Strength IV", 27.57, 171.34, 35.69, "W225", "W226"),
              ("Extreme IIb", 23.32, 137.87, 49.38, "W230", "W231"),
              ("Service I", 20.53, 130.18, 33.30, "R495", "R496"))
    pub_e = {"N204": 1.14, "N207": 1.96, "W220": 0.43, "W225": 0.08,
             "W230": 1.21, "R495": 0.28}
    pub_q = {"W221": 3.04, "W226": 2.80, "W231": 3.08, "R496": 2.17,
             "T298": 2.57, "T299": 2.82}
    for nombre, V, MV, MH, c_e, c_q in combos:
        M_punta = MV - MH
        rec = presion_uniforme_us(V=V, M_punta=M_punta, B=B)
        mot = _uniforme_motor(V=V, M_punta=M_punta, B=B)
        add(Contraste(CDOT, f"e, {nombre}", "ft", pub_e[c_e], rec["e"],
                      mot.e / FT, f"{c_e} (ΣV, ΣMV, ΣMH de H188-Z193)",
                      "M9.presion_contacto_base (rama de suelo)"))
        c_q = c_q or {"Strength Ia": "T298", "Extreme IIa": "T299"}[nombre]
        add(Contraste(CDOT, f"σV = ΣV/(B − 2e), {nombre}", "ksf",
                      pub_q[c_q], rec["q"], mot.q_max / KSF, c_q,
                      "M9.presion_contacto_base (rama de suelo)"))

    # --- Flexion del alzado (AASHTO 5.6.3.2) -------------------------------
    As, de = 0.62, 18.69                       # AA359, AA355 (#5 @ 6")
    rec = flexion_us(As=As, d=de, fc=fc, fy=fy, beta_1=0.825)
    mot = M9.resistencia_a_flexion(As=As * IN2_POR_FT, d=de * IN,
                                   fc=fc * KSI, fy=fy * KSI)
    add(Contraste(CDOT, "β1 (5.6.2.2, f'c = 4.5 ksi)", "—", 0.825, 0.825,
                  mot["beta_1"], "T322", "M9.beta_1_aashto"))
    add(Contraste(CDOT, "c, eje neutro", "in", 0.982, rec["c"],
                  mot["c"] / IN, "AA360", "M9.resistencia_a_flexion"))
    add(Contraste(CDOT, "a = β1·c", "in", 0.81, rec["a"], mot["a"] / IN,
                  "AA361", "M9.resistencia_a_flexion"))
    add(Contraste(CDOT, "Mn", "kip-ft/ft", 56.68, rec["Mn"],
                  mot["M_n"] / KIPFT_POR_FT, "AA362",
                  "M9.resistencia_a_flexion"))
    add(Contraste(CDOT, "As para φMn = 51.01 kip-ft (inversa)", "in²/ft",
                  0.62,
                  acero_para_momento_us(Mu=51.01, phi=0.9, d=de, fc=fc, fy=fy),
                  M9.acero_por_flexion(M_u=51.01 * KIPFT_POR_FT, d=de * IN,
                                       fc=fc * KSI, fy=fy * KSI, phi=0.9)
                  / IN2_POR_FT,
                  "AA359 y AA363", "M9.acero_por_flexion"))
    add(Contraste(CDOT, "Mcr (γ3 = 0.67, A615 G60)", "kip-ft/ft", 40.11,
                  mcr_us(h=h_tallo, fc=fc, gamma_3=0.67),
                  M9.momento_de_agrietamiento(espesor=h_tallo * IN,
                                              fc=fc * KSI, gamma_3=0.67)
                  / KIPFT_POR_FT,
                  "Q386", "M9.momento_de_agrietamiento"))

    # --- Fisuracion (AASHTO 5.6.7), clase 2 --------------------------------
    n_cdot = 29000.0 / (120000.0 * 1.0 * 0.15 ** 2 * fc ** 0.33)
    dc, Ms = 2.0 + 0.625 / 2, 26.8                # X394, Q399
    rec = fisuracion_us(Ms=Ms, As=As, d=de, h=h_tallo, dc=dc, n=n_cdot,
                        gamma_e=0.75)
    mot = M9.fisuracion_aashto(M_s=Ms * KIPFT_POR_FT, As=As * IN2_POR_FT,
                               d=de * IN, espesor=h_tallo * IN, d_c=dc * IN,
                               fc=fc * KSI, fy=fy * KSI)
    n_m9 = n_aashto_us(fc=fc)
    ref = fisuracion_us(Ms=Ms, As=As, d=de, h=h_tallo, dc=dc, n=n_m9,
                        gamma_e=0.75)
    add(Contraste(
        CDOT, "n = Es/Ec", "—", 6.54, n_cdot, mot["n"], "T321 (Ec en T320)",
        "M9.fisuracion_aashto",
        metodo=("Ec: CDOT usa la ec. 5.4.2.4-1, 120 000·K1·wc²·f'c^0.33 con "
                "wc = 0.150 kcf (4435 ksi); M9 usa la del comentario "
                "C5.4.2.4-1, 2500·f'c^0.33, que es la misma con wc = 0.145 "
                "kcf (4107 ksi). Ver la observacion O-1 (cerrada a favor de "
                "M9)."),
        referencia=n_m9))
    add(Contraste(
        CDOT, "k de la seccion fisurada", "—", 0.179, rec["k"], mot["k"],
        "Q397", "M9.fisuracion_aashto",
        metodo="el k depende de n (O-1): con el n de M9 sale 0.1790",
        errata=("la hoja calcula k con ρ = 0.003, el valor MOSTRADO de "
                "0.620/(12·18.69) = 0.002764 («as displayed», celda AF1): "
                "con ρ exacto y su n = 6.54, k = 0.1729"),
        referencia=ref["k"]))
    add(Contraste(CDOT, "f_ss = Ms/(As·j·d)", "ksi", 29.52, rec["fss"],
                  mot["f_ss"] / KSI, "AA400", "M9.fisuracion_aashto",
                  metodo="n distinto (O-1); f_ss casi no depende de n",
                  referencia=ref["fss"]))
    add(Contraste(CDOT, "β_s", "—", 1.18, rec["beta_s"], mot["beta_s"],
                  "AA401", "M9.fisuracion_aashto"))
    add(Contraste(CDOT, "s_max (γe = 0.75, clase 2)", "in", 10.45,
                  rec["s_max"], mot["s_max"]["clase_2"] / IN, "AA402",
                  "M9.fisuracion_aashto"))

    # --- Cortante (AASHTO 5.7.3.3) ------------------------------------------
    a_m = M9.resistencia_a_flexion(As=As * IN2_POR_FT, d=de * IN,
                                   fc=fc * KSI, fy=fy * KSI)["a"]
    a_in = flexion_us(As=As, d=de, fc=fc, fy=fy, beta_1=0.825)["a"]
    dv = dv_us(de=de, a=a_in, h=h_tallo)
    mot = M9.cortante_del_concreto(d=de * IN, a=a_m, espesor=h_tallo * IN,
                                   fc=fc * KSI, beta=1.81)
    add(Contraste(
        CDOT, "dv (5.7.2.8)", "in", 18.2, dv, mot["d_v"] / IN, "S411",
        "M9.cortante_del_concreto",
        errata=("la celda escribe dv = max(de − c/2, …) con c = 0.982 in "
                "(AA360), y AASHTO 5.7.2.8 resta a/2 (a = 0.81 in): "
                "18.199 frente a 18.285 in; dentro del 1 %")))
    add(Contraste(
        CDOT, "Vc con β = 1.81 (β del procedimiento general, dato de la "
        "fuente)", "kip/ft", 26.5, vc_us(beta=1.81, fc=fc, dv=dv),
        mot["V_c"] / KLF, "AA444 (β en S440)", "M9.cortante_del_concreto",
        errata=("el texto de la celda escribe «0.0316 (2)(1) …» y el "
                "valor usa β = 1.81 de S440: con β = 2 saldria 29.3 kip; "
                "el numero publicado es el de β = 1.81 con el dv de S411")))
    permitido, _ = M9.simplificado_permitido(es_zapata=False,
                                             espesor=h_tallo * IN,
                                             vuelo=None, d_v=mot["d_v"])
    add(Contraste(
        CDOT, "¿Procedimiento simplificado de 5.7.3.4.1 permitido en el "
        "alzado sin estribos (h = 21 in)?", "sí/no", False, False, permitido,
        "A413 («does not qualify for simplified procedure»)",
        "M9.simplificado_permitido"))

    # --- Acero de retraccion y temperatura (AASHTO 5.10.6) -----------------
    # CORRECCIONES DE LA REVISION FABLE (A-3): esta fila se declaraba
    # «errata de la fuente» («la hoja aplica la ec. 5.10.6-1 sin el piso de
    # 5.10.6-2») y NO lo era: la hoja calcula la 5.10.6-1 en Y455 y comprueba
    # el piso y el techo en la fila siguiente (AD456 = IF(AND(T454 >= 0.11,
    # T454 <= 0.6), ...)), como AASHTO. Y al compararla con el valor acotado,
    # el motor devolvia el piso y la ecuacion de M9 no se contrastaba (dos
    # mutantes de la ec. 5.10.6-1 sobrevivian). Hoy son dos contrastes: la
    # ECUACION, en los tres casos que la hoja calcula, leida en el motor por
    # la escala de f_y (`_temperatura_ec_motor`), y el PISO aparte.
    for celda, h_in, elemento in (("Y455", h_tallo, "alzado (h = 21 in)"),
                                  ("Y70 y Y140", TF * 12.0,
                                   "zapata: talon y punta (h = 15 in)"),
                                  ("Y210", 18.0,
                                   "llave de corte (h = 18 in)")):
        add(Contraste(
            CDOT, f"As de la ec. 5.10.6-1 sin acotar, {elemento}, b = 12 in",
            "in²/ft",
            {"Y455": 0.083, "Y70 y Y140": 0.072, "Y210": 0.078}[celda],
            temperatura_ec_us(b=B_FRANJA_IN, h=h_in, fy=fy),
            _temperatura_ec_motor(b_in=B_FRANJA_IN, h_in=h_in, fy_ksi=fy),
            celda + (" (hoja «Footing and key design»)"
                     if celda != "Y455" else ""),
            "M9.acero_de_temperatura_aashto (llamado con f_y/2, para que el "
            "piso de 5.10.6-2 no tape la ecuacion, y dividido entre 2: la "
            "ec. es lineal en 1/f_y)"))
    add(Contraste(
        CDOT, "As minima de temperatura del alzado: la ec. 5.10.6-1 (Y455) "
        "con el piso de 5.10.6-2 que la hoja comprueba en AD456", "in²/ft",
        max(0.083, 0.11), temperatura_us(b=B_FRANJA_IN, h=h_tallo, fy=fy),
        M9.acero_de_temperatura_aashto(ancho=B_FRANJA_IN * IN,
                                       espesor=h_tallo * IN, fy=fy * KSI)
        / IN2_POR_FT,
        "Y455 y AD456 (= IF(AND(T454>=0.11, T454<=0.6), «OK», «Fails»))",
        "M9.acero_de_temperatura_aashto (con su piso)"))
    return tuple(C)


# ===========================================================================
# Caltrans BDP 11.2.2
# ===========================================================================

# Tabla 11.2.2-2 (p. 11.2-21), sismo: (parte, fuerza kip, brazo ft, momento
# impreso kip-ft), TRANSCRITOS COMO TEXTO para saber con cuantas cifras los
# imprime la fuente. Signos de la fuente: + horario respecto de O (la esquina
# inferior de la punta). Las filas «kh·n» son la inercia 0.28·W de la parte n,
# con la fuerza que la fuente imprime (unas veces calcula el momento con ella
# y otras con 0.28·W sin redondear: las dos caben en el redondeo propagado).
TABLA_SISMICA = (
    ("1", "3.23", "5.97", "19.28"), ("2", "2.48", "6.92", "17.15"),
    ("3", "7.12", "9.50", "67.69"), ("4", "0.22", "14.00", "3.15"),
    ("5", "1.82", "7.42", "13.50"), ("6", "29.37", "13.44", "394.66"),
    ("7", "1.32", "2.75", "3.63"), ("8", "4.45", "14.83", "66.06"),
    ("PAE·sen δA", "5.34", "19.0", "101.46"),
    ("PAE·cos δA", "-31.11", "10.15", "-315.77"),
    ("kh·1", "-0.91", "14.0", "-12.66"), ("kh·2", "-0.69", "10.17", "-7.06"),
    ("kh·3", "-2.00", "1.25", "-2.49"), ("kh·5", "-0.51", "17.17", "-8.75"),
    ("kh·6", "-8.22", "13.5", "-111.02"), ("kh·7", "-0.37", "3.5", "-1.29"),
    ("kh·8", "-1.25", "26.48", "-33.10"),
)
# La fila kh·4 (0.06 kip, brazo 0.38 ft, +0.02) no se revisa porque su
# momento es de la ultima cifra. Su signo es CORRECTO: la parte 4 es la llave
# de corte (0.15·0.75·2.0 = 0.22 kip, p. 11.2-55), que queda POR DEBAJO del
# punto O, y su fuerza de inercia da momento de signo contrario al de las
# demas (correcciones de la revision Fable, M-4: este comentario decia que
# el signo «contradice» al de las demas inercias).
MOMENTO_KH4_IMPRESO = 0.02
SUMA_SISMICA_IMPRESA = 194.46
# Tabla 11.2.2-3 (p. 11.2-23), servicio.
TABLA_SERVICIO = (
    ("1", "3.23", "5.97", "19.28"), ("2", "2.48", "6.92", "17.15"),
    ("3", "7.12", "9.50", "67.69"), ("4", "0.22", "14.00", "3.15"),
    ("5", "1.82", "7.42", "13.50"), ("6", "29.37", "13.44", "394.47"),
    ("7", "1.32", "2.75", "3.63"), ("8", "4.45", "14.83", "65.99"),
    ("PA·sen δA", "2.97", "19.0", "56.43"),
    ("PA·cos δA", "-17.29", "10.65", "-175.49"),
)
SUMA_SERVICIO_IMPRESA = 465.8
ERRATAS_DE_FILA = {
    ("servicio", "6"): ("29.37 × 13.44 = 394.73; la misma fila de la tabla "
                        "sismica imprime 394.66, y ninguna fuerza que se "
                        "imprima 29.37 da 394.47"),
    ("servicio", "PA·cos δA"): ("el brazo impreso «10.65» es errata de "
                               "10.15: −17.29 × 10.15 = −175.49, que es el "
                               "momento impreso (y el brazo de la tabla "
                               "sismica y de la Tabla 11.2.2-4)"),
}


def _media_unidad(texto: str) -> float:
    """Medio ultimo digito de una cifra impresa: «13.5» -> 0.05."""
    decimales = len(texto.split(".")[1]) if "." in texto else 0
    return 0.5 * 10.0 ** (-decimales)


@dataclass(frozen=True)
class RevisionDeLaFuente:
    """
    Aritmetica de la propia fuente, sin motor: fuerza·brazo contra el
    momento impreso. Cuadra si la diferencia cabe en el redondeo PROPAGADO
    de las tres cifras impresas: |F|·δb + |b|·δF + δM, con δ el medio
    ultimo digito de cada una (la fuente calcula con los valores sin
    redondear e imprime cada cifra redondeada).
    """
    tabla: str
    fila: str
    impreso: float
    recalculado: float
    margen: float
    nota: str = ""

    @property
    def cuadra(self) -> bool:
        return dentro_de(abs(self.impreso - self.recalculado), self.margen)


def revisiones_caltrans() -> Tuple[RevisionDeLaFuente, ...]:
    R: List[RevisionDeLaFuente] = []
    for nombre, tabla, filas, suma in (
            ("sismo", "11.2.2-2 (sismo, p. 11.2-21)", TABLA_SISMICA,
             SUMA_SISMICA_IMPRESA),
            ("servicio", "11.2.2-3 (servicio, p. 11.2-23)", TABLA_SERVICIO,
             SUMA_SERVICIO_IMPRESA)):
        for parte, F_t, b_t, M_t in filas:
            F, b, M = float(F_t), float(b_t), float(M_t)
            dF = _media_unidad(F_t)
            margen = abs(F) * _media_unidad(b_t) + abs(b) * dF \
                + _media_unidad(M_t)
            R.append(RevisionDeLaFuente(
                tabla, f"parte {parte}: F·brazo", M, F * b, margen,
                ERRATAS_DE_FILA.get((nombre, parte), "")))
        momentos = [float(f[3]) for f in filas]
        if nombre == "sismo":
            momentos.append(MOMENTO_KH4_IMPRESO)
        R.append(RevisionDeLaFuente(
            tabla, "ΣM_O", suma, sum(momentos),
            _media_unidad(f"{suma}"),
            "suma de los momentos IMPRESOS de la tabla"))
    partes = ("3.23", "2.48", "7.12", "0.22", "1.82", "29.37", "1.32", "4.45")
    R.append(RevisionDeLaFuente(
        "11.2.2-1 (p. 11.2-18) y p. 11.2-21", "ΣW", 50.02,
        sum(float(x) for x in partes),
        sum(_media_unidad(x) for x in partes),
        "la p. 11.2-21 escribe V = 50.02 + 5.34 y la Tabla 11.2.2-1 suma "
        "50.01: dentro del redondeo de sus ocho partes"))
    return tuple(R)


def contrastes_caltrans() -> Tuple[Contraste, ...]:
    C: List[Contraste] = []
    add = C.append
    fc, fy, B = 4.0, 60.0, 19.0                 # p. 11.2-16; Fig. 11.2.2-1

    # --- Excentricidad y presiones (11.6.3.2 y 10.6.5) ---------------------
    casos = (("sismo (Evento Extremo)", 55.36, SUMA_SISMICA_IMPRESA,
              {"e": (5.98, "p. 11.2-21"), "Bp": (7.03, "p. 11.2-22"),
               "q": (7.87, "p. 11.2-22")}),
             ("servicio", 52.98, SUMA_SERVICIO_IMPRESA,
              {"e": (0.70, "p. 11.2-23"), "Bp": (17.59, "p. 11.2-23"),
               "q": (3.01, "p. 11.2-24")}),
             ("Resistencia Ia", 70.68, 600.48,
              {"e": (1.0, "p. 11.2-40"), "Bp": (17.00, "p. 11.2-25"),
               "q": (4.16, "p. 11.2-25")}),
             ("Resistencia Ib", 53.16, 395.62,
              {"e": (2.06, "p. 11.2-27")}))
    for nombre, V, M_O, pub in casos:
        rec = presion_uniforme_us(V=V, M_punta=M_O, B=B)
        mot = _uniforme_motor(V=V, M_punta=M_O, B=B)
        valores = {"e": (rec["e"], mot.e / FT, "ft"),
                   "Bp": (rec["Bp"], mot.ancho_efectivo / FT, "ft"),
                   "q": (rec["q"], mot.q_max / KSF, "ksf")}
        for clave, (p, cita) in pub.items():
            r, m, u = valores[clave]
            errata = ""
            if nombre == "servicio" and clave == "e":
                errata = ("la fuente escribe e = 19/2 − 8.79 = 0.70, y esa "
                          "resta da 0.71; con x = 465.8/52.98 = 8.792 "
                          "e = 0.708 (y B' = 17.584, que la fuente imprime "
                          "17.59)")
            if nombre == "sismo (Evento Extremo)" and clave == "q":
                errata = ("la fuente divide 55.35 (no 55.36) por 7.03; la "
                          "diferencia es de la cuarta cifra. En la misma "
                          "pagina escribe q_n = 32.22 ksf y luego "
                          "0.8·(33.22) = 26.58: una de las dos cifras de q_n "
                          "esta mal (no la usa el motor)")
            etiqueta = {"e": "e = B/2 − ΣM_O/V", "Bp": "B' = B − 2e",
                        "q": "q = V/B'"}[clave]
            add(Contraste(CALTRANS, f"{etiqueta}, {nombre}", u, p, r, m, cita,
                          "M9.presion_contacto_base (rama de suelo)",
                          errata=errata))
    add(Contraste(
        CALTRANS, "e admisible bajo sismo con γEQ = 0 (11.6.5.1)", "ft", 6.33,
        B / 3, M9.excentricidad_admisible_sismica(B=B * FT, gamma_EQ=0.0) / FT,
        "p. 11.2-22", "M9.excentricidad_admisible_sismica"))
    lin = presion_lineal_us(V=70.68, M_punta=600.48, B=B)
    mot = M9.presion_de_contacto_lineal(_combo(V=70.68, M_punta=600.48, B=B))
    add(Contraste(CALTRANS, "q en la punta, trapecio (Resistencia Ia)", "ksf",
                  4.895, lin["q_punta"], mot["s0"] / KSF, "p. 11.2-41",
                  "M9.presion_de_contacto_lineal (AASHTO 10.6.5)"))
    add(Contraste(CALTRANS, "q en el talon, trapecio (Resistencia Ia)", "ksf",
                  2.545, lin["q_talon"], mot["s1"] / KSF, "p. 11.2-41",
                  "M9.presion_de_contacto_lineal (AASHTO 10.6.5)"))
    lin = presion_lineal_us(V=55.36, M_punta=SUMA_SISMICA_IMPRESA, B=B)
    mot = M9.presion_de_contacto_lineal(
        _combo(V=55.36, M_punta=SUMA_SISMICA_IMPRESA, B=B))
    add(Contraste(CALTRANS, "q máx., triángulo desde la punta (sismo)", "ksf",
                  10.48, lin["q_punta"], mot["s0"] / KSF, "p. 11.2-43",
                  "M9.presion_de_contacto_lineal (AASHTO 10.6.5)"))

    # --- Flexion del alzado (#9 @ 8") --------------------------------------
    As, de, h = 1.50, 28.5 - 2.0 - 1.128 / 2, 28.5    # p. 11.2-35
    rec = flexion_us(As=As, d=de, fc=fc, fy=fy, beta_1=0.85)
    mot = M9.resistencia_a_flexion(As=As * IN2_POR_FT, d=de * IN,
                                   fc=fc * KSI, fy=fy * KSI)
    for clave, pub, u, cita, conv in (("a", 2.20, "in", "p. 11.2-35", IN),
                                      ("c", 2.59, "in", "p. 11.2-35", IN),
                                      ("Mn", 186.3, "kip-ft/ft", "p. 11.2-35",
                                       KIPFT_POR_FT)):
        motor = mot["M_n" if clave == "Mn" else clave] / conv
        add(Contraste(CALTRANS, f"{clave} del alzado", u, pub, rec[clave],
                      motor, cita, "M9.resistencia_a_flexion"))
    add(Contraste(CALTRANS, "ε_t del acero", "—", 0.027, rec["eps_t"],
                  mot["epsilon_t"], "p. 11.2-35", "M9.resistencia_a_flexion"))
    add(Contraste(CALTRANS, "As para φMn = 167.7 kip-ft (inversa)", "in²/ft",
                  1.50,
                  acero_para_momento_us(Mu=167.7, phi=0.9, d=de, fc=fc, fy=fy),
                  M9.acero_por_flexion(M_u=167.7 * KIPFT_POR_FT, d=de * IN,
                                       fc=fc * KSI, fy=fy * KSI, phi=0.9)
                  / IN2_POR_FT, "p. 11.2-35", "M9.acero_por_flexion"))
    for elemento, espesor, pub, cita in (("del alzado", 28.5, 78.0,
                                          "p. 11.2-30"),
                                         ("de la punta", 30.0, 86.4,
                                          "p. 11.2-42")):
        add(Contraste(
            CALTRANS, f"Mcr {elemento} (γ3 = 0.75, A706)", "kip-ft/ft",
            pub, mcr_us(h=espesor, fc=fc, gamma_3=0.75),
            M9.momento_de_agrietamiento(espesor=espesor * IN, fc=fc * KSI,
                                        gamma_3=0.75) / KIPFT_POR_FT,
            cita, "M9.momento_de_agrietamiento"))

    # --- Fisuracion del alzado (clase 1) ------------------------------------
    n_cal = 8.0                                     # p. 11.2-36
    dc, Ms = 2.0 + 1.128 / 2, 80.4
    rec = fisuracion_us(Ms=Ms, As=As, d=de, h=h, dc=dc, n=n_cal, gamma_e=1.0)
    fss_rec = fss_por_inercia_us(Ms=Ms, As=As, d=de, n=n_cal)
    mot = M9.fisuracion_aashto(M_s=Ms * KIPFT_POR_FT, As=As * IN2_POR_FT,
                               d=de * IN, espesor=h * IN, d_c=dc * IN,
                               fc=fc * KSI, fy=fy * KSI)
    n_m9 = n_aashto_us(fc=fc)
    add(Contraste(
        CALTRANS, "n = Es/Ec", "—", 8.0,
        29000.0 / (57.0 * math.sqrt(fc * 1000.0)), mot["n"], "p. 11.2-36",
        "M9.fisuracion_aashto",
        metodo=("Ec: Caltrans usa 57 000·√f'c (psi), la expresion de ACI "
                "318 (3605 ksi, n = 8.04, redondeado a 8); M9 la del "
                "comentario C5.4.2.4-1 de AASHTO (3950 ksi, n = 7.34). Ver "
                "O-1 (cerrada a favor de M9)."),
        referencia=n_m9))
    add(Contraste(CALTRANS, "β_s", "—", 1.14, rec["beta_s"], mot["beta_s"],
                  "p. 11.2-36", "M9.fisuracion_aashto"))
    add(Contraste(CALTRANS, "f_ss (seccion fisurada)", "ksi", 27.0, fss_rec,
                  mot["f_ss"] / KSI, "p. 11.2-37", "M9.fisuracion_aashto",
                  metodo="n distinto (O-1); f_ss casi no depende de n",
                  referencia=fisuracion_us(Ms=Ms, As=As, d=de, h=h, dc=dc,
                                           n=n_m9, gamma_e=1.0)["fss"]))
    add(Contraste(
        CALTRANS, "s_max (γe = 1.0, clase 1)", "in", 17.6,
        700 * 1.0 / (rec["beta_s"] * fss_rec) - 2 * dc,
        mot["s_max"]["clase_1"] / IN, "p. 11.2-37", "M9.fisuracion_aashto"))

    # --- Cortante del talon (sin estribos, β de la fuente) -----------------
    de_t, h_t, As_t = 30.0 - 3.0 - 1.41 / 2, 30.0, 3.0   # p. 11.2-56
    a_t = flexion_us(As=As_t, d=de_t, fc=fc, fy=fy, beta_1=0.85)["a"]
    dv = dv_us(de=de_t, a=a_t, h=h_t)
    a_m = M9.resistencia_a_flexion(As=As_t * IN2_POR_FT, d=de_t * IN,
                                   fc=fc * KSI, fy=fy * KSI)["a"]
    mot = M9.cortante_del_concreto(d=de_t * IN, a=a_m, espesor=h_t * IN,
                                   fc=fc * KSI, beta=1.57)
    add(Contraste(
        CALTRANS, "dv del talon (5.7.2.8)", "in", 24.2, dv, mot["d_v"] / IN,
        "p. 11.2-56 («calculation is not shown here»)",
        "M9.cortante_del_concreto"))
    add(Contraste(
        CALTRANS, "Vc del talon con β = 1.57 (β del Apendice B5, dato de la "
        "fuente)", "kip/ft", 28.8, vc_us(beta=1.57, fc=fc, dv=dv),
        mot["V_c"] / KLF, "p. 11.2-56", "M9.cortante_del_concreto"))
    permitido, _ = M9.simplificado_permitido(es_zapata=True, espesor=h_t * IN,
                                             vuelo=11.125 * FT,
                                             d_v=mot["d_v"])
    add(Contraste(
        CALTRANS, "¿Procedimiento simplificado permitido en el talon (vuelo "
        "11.125 ft frente a 3·dv)?", "sí/no", False, False, permitido,
        "p. 11.2-56 (usa el procedimiento general, Apendice B5)",
        "M9.simplificado_permitido"))
    return tuple(C)


def contrastes() -> Tuple[Contraste, ...]:
    return contrastes_caltrans() + contrastes_cdot()


# ===========================================================================
# Lo que no se contrasta, y por que
# ===========================================================================

NO_CONTRASTABLE = (
    (CALTRANS, "P_A y P_AE por cuña de tanteo (17.54 y 31.56 kip)",
     "la superficie del relleno (talud y tramo horizontal) solo esta en la "
     "Fig. 11.2.2-1, sin cotas suficientes para reconstruir AB = 30.44 ft; "
     "contrastar `M9.cuna_de_tanteo` exige esa geometria"),
    (CALTRANS, "k_PE y k_P de las cartas de AASHTO (Fig. A11.4-2 y "
     "3.11.5.4-1)", "M9 no calcula el empuje pasivo de espiral logaritmica; "
     "el cabezal no cuenta con el pasivo frente a la punta"),
    (CALTRANS, "Desplazamiento sismico de Anderson (A11.5.2, 5.4 in)",
     "M9 no implementa Newmark ni sus correlaciones"),
    (CALTRANS, "q_n de las Fig. 11.2.2-3 y -4", "son lecturas de graficas "
     "del sitio del ejemplo"),
    (CALTRANS, "Cortante de interfaz (5.7.4) y corte de barras (5.10.8)",
     "M9 no los verifica"),
    (CALTRANS, "θ y β por el procedimiento general (Apendice B5)",
     "M9 no implementa el procedimiento general: fuera del simplificado "
     "levanta `MetodoNoEvaluableError` (T-7c). Se contrasta Vc con el β de "
     "la fuente y la decision de no usar el simplificado"),
    (CALTRANS, "Acero de temperatura 0.0018·b·h (C5.10.6)",
     "la fuente usa la regla del comentario; M9 la ec. 5.10.6-1 con el ancho "
     "real del elemento (en un muro largo las dos dan ~0.31 in²/ft por cara "
     "en 28.5 in, pero el ejemplo no da la longitud del muro)"),
    (CDOT, "Llave de corte por bloque inerte (BDM 11.5.1, R1, R2, Rep)",
     "regla de la agencia; el cabezal de M9 no lleva llave"),
    (CDOT, "Carga de colision CT y combinaciones Extreme II",
     "el cabezal de una alcantarilla no recibe la baranda del ejemplo"),
    (CDOT, "EFW minimo de 36 pcf (BDM 11.5)", "regla de la agencia: se "
     "contrasta el empuje con el EFW que la hoja usa, no se valida el minimo"),
    (CDOT, "Example 8 (aleta en voladizo de un estribo integral)",
     "la aleta del ejemplo vuela HORIZONTALMENTE desde el estribo, con la "
     "presion trapezoidal de una ayuda de diseño de Caltrans; el alero de M9 "
     "es un voladizo vertical sobre su zapata. Lo unico comun, K0 = 1 − sen φ "
     "= 0.4408 (celda E78), M9 lo calcula dentro de `cargas_del_cabezal`, "
     "sin funcion publica que llamar"),
    ("ambas", "Contraste E.060 (fila A5 del armado)",
     "las dos fuentes son AASHTO; no hay ejemplo E.060 que contrastar"),
)

OBSERVACIONES = (
    ("O-1", "El modulo de elasticidad del concreto — CERRADA a favor de M9 "
     "(correcciones de la revision Fable, M-5). M9 toma n con la expresion "
     "del comentario C5.4.2.4-1 de AASHTO LRFD 9.a ed. (pag. 5-20, PDF 379: "
     "«For normal weight concrete with wc = 0.145 kcf, Ec may be taken as "
     "2,500 f'c^0.33»). La Tabla 3.5.1-1 da 0.145 kcf al concreto de peso "
     "normal con f'c ≤ 5.0 ksi, y C3.5.1 (pag. 3-21, PDF 75) dice que los "
     "0.005 kcf de mas del concreto ARMADO son para las cargas muertas, no "
     "para el Ec. CDOT mete 0.150 kcf en la ec. 5.4.2.4-1 (n = 6.54 frente a "
     "7.06) y Caltrans usa 57 000·√f'c, que no es de AASHTO: M9 es el que "
     "sigue la letra. En f_ss la diferencia es menor del 0.5 % en los dos "
     "ejemplos. Las filas de metodo exigen ademas que el motor de el n de esa "
     "formula, calculado aparte (`n_aashto_us`)."),
    ("O-2", "El «b» del acero de temperatura. CDOT toma b = 12 in (la franja "
     "de calculo); M9 pasa el ancho real del elemento, que es lo que AASHTO "
     "5.10.6 llama «least width of component section». Con el ancho real el "
     "minimo es mayor en un muro largo. En los tres casos de CDOT la ec. "
     "5.10.6-1 con b = 12 in queda bajo el piso de 0.11 in²/ft, de modo que "
     "ahi el b no cambia el acero minimo; los contrastes de la ecuacion usan "
     "el b de la fuente."),
)


# ===========================================================================
# El documento
# ===========================================================================

def _celda(texto: Any) -> str:
    return str(texto).replace("|", "\\|").replace("\n", " ")


def _num(x: Numero) -> str:
    if isinstance(x, bool):
        return "sí" if x else "no"
    return f"{x:.4g}"


def _pct(x: Optional[float]) -> str:
    if x is None:
        return "—"
    return "0.00%" if abs(x) < MEDIO_CENTESIMO_DE_PUNTO else f"{x:+.2%}"


# Lo que «+0.00%» ya no distingue de cero: medio centesimo de punto.
MEDIO_CENTESIMO_DE_PUNTO = 5e-5


def generar() -> str:
    L: List[str] = []
    A = L.append
    todos = contrastes()
    A("# Validación externa de M9: el cabezal contra ejemplos resueltos "
      "(VE-3.3)")
    A("")
    A("> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe "
      "`python -m tests.apoyo.validacion_cabezal --escribir` y "
      "`tests/test_validacion_cabezal.py` lo regenera y lo compara. Las "
      "cifras de las fuentes están transcritas con su página o su celda en "
      "`tests/apoyo/validacion_cabezal.py`; la cuenta es la de las funciones "
      "de M9. Las fuentes no están en el repositorio.")
    A("")
    A("## 1. Fuentes, tolerancia y regla de juicio")
    A("")
    for nombre, texto in FUENTES.items():
        A(f"- **{nombre}.** {texto}")
    A("")
    A(f"- **Tolerancia: {TOLERANCIA_EJEMPLO_IMPRESO:.0%}**, la de un ejemplo "
      "impreso (`TOLERANCIA_EJEMPLO_IMPRESO` de "
      "`tests/apoyo/validacion_externa.py`): las fuentes imprimen tres o "
      "cuatro cifras y redondean los intermedios.")
    A("- Por cada cifra: **publicado** (la fuente), **recalculado** (la "
      "fórmula de la propia fuente, en sus unidades, sin M9) y **motor** (M9 "
      "en SI, devuelto a las unidades de la fuente). El motor se juzga "
      "contra lo recalculado; si la fuente no cuadra con su propia cuenta es "
      "una **errata de la fuente**, declarada con su causa.")
    A(f"- Juicios: «{JUICIO_COINCIDE}», «{JUICIO_ERRATA}», «{JUICIO_METODO}» "
      f"y «{JUICIO_DEFECTO}». La suite exige cero defectos.")
    A("- En una fila con **método** declarado, el motor tiene además que dar "
      "la **referencia de su propio método**, calculada aparte en el arnés "
      "sin llamar a M9 (hoy, el n = Es/Ec del comentario C5.4.2.4-1 y lo que "
      f"depende de él), con `TOL_REL_MOTOR` = {TOL_REL_MOTOR:g}; si no la da, "
      "es un **defecto**, cuadre o no con la fuente (correcciones de la "
      "revisión Fable, M-1).")
    A("")
    for numero, ejemplo, filas in ((2, CALTRANS, contrastes_caltrans()),
                                   (3, CDOT, contrastes_cdot())):
        A(f"## {numero}. {ejemplo}")
        A("")
        A("| Paso | Unidad | Publicado | Recalculado | Motor | Motor − rec. "
          "| Juicio | Cita | Función de M9 |")
        A("|---|---|---|---|---|---|---|---|---|")
        for c in filas:
            A("| " + " | ".join(_celda(x) for x in (
                c.paso, c.unidad, _num(c.publicado), _num(c.recalculado),
                _num(c.motor), _pct(c.diferencia_motor()), c.juicio, c.cita,
                f"`{c.funcion}`")) + " |")
        A("")
        notas = [c for c in filas if c.errata or c.metodo]
        if notas:
            A("Erratas de la fuente y diferencias de método:")
            A("")
            for c in notas:
                if c.errata:
                    A(f"- *{c.paso}* — **errata:** {c.errata}.")
                if c.metodo:
                    A(f"- *{c.paso}* — **método:** {c.metodo} Referencia del "
                      f"motor con su método: {_num(c.referencia)}; motor: "
                      f"{_num(c.motor)}.")
            A("")
    A("## 4. La aritmética de la propia fuente (Caltrans, tablas de momentos)")
    A("")
    A("Sin motor: cada momento impreso contra su fuerza por su brazo, con el "
      "redondeo propagado de las tres cifras impresas como margen "
      "(|F|·δb + |b|·δF + δM, δ = medio último dígito), y cada suma contra "
      "la suma de las filas impresas.")
    A("")
    A("| Tabla | Fila | Impreso | Recalculado | Margen | ¿Cuadra? | Nota |")
    A("|---|---|---|---|---|---|---|")
    for r in revisiones_caltrans():
        A("| " + " | ".join(_celda(x) for x in (
            r.tabla, r.fila, f"{r.impreso:.2f}", f"{r.recalculado:.3f}",
            f"{r.margen:.3f}", "sí" if r.cuadra else "**NO**",
            r.nota or "—")) + " |")
    A("")
    A("Las filas que no cuadran son erratas de la fuente. La de la parte 6 de "
      "servicio deja la suma 0.26 kip-ft corta (0.06 %, sin efecto en x ni en "
      "e a dos cifras); la del brazo de PA·cos δA es solo de la cifra del "
      "brazo, porque el momento impreso es el correcto. Los contrastes de las "
      "secciones 2 y 3 usan las sumas IMPRESAS.")
    A("")
    A("## 5. Lo que no se contrasta, y por qué")
    A("")
    A("| Fuente | Qué | Por qué |")
    A("|---|---|---|")
    for fuente, que, por_que in NO_CONTRASTABLE:
        A(f"| {_celda(fuente)} | {_celda(que)} | {_celda(por_que)} |")
    A("")
    A("## 6. Observaciones para el dueño (no son defectos)")
    A("")
    for codigo, texto in OBSERVACIONES:
        A(f"- **{codigo}.** {texto}")
    A("")
    A("## 7. Resumen")
    A("")
    for ejemplo, filas in ((CALTRANS, contrastes_caltrans()),
                           (CDOT, contrastes_cdot())):
        cuenta = {j: sum(1 for c in filas if c.juicio == j)
                  for j in (JUICIO_COINCIDE, JUICIO_ERRATA, JUICIO_METODO,
                            JUICIO_DEFECTO)}
        A(f"- **{ejemplo}:** {len(filas)} contrastes — "
          + "; ".join(f"{v} «{k}»" for k, v in cuenta.items()) + ".")
    no_cuadran = sum(1 for r in revisiones_caltrans() if not r.cuadra)
    A(f"- **Aritmética de Caltrans:** {no_cuadran} filas que no cuadran, de "
      f"{len(revisiones_caltrans())}.")
    defectos = [c for c in todos if c.juicio == JUICIO_DEFECTO]
    A(f"- **Defectos del motor: {len(defectos)}.**")
    A("")
    return "\n".join(L)


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
