"""
tests/test_dimensional_piloto.py
================================
CHEQUEO DIMENSIONAL PILOTO sobre la cadena hidraulica: M3, M4 y M5 (sesion
I4 del plan de cierre ingenieril).

Que comprueba, y sobre que
--------------------------
Sobre cada `PasoDeMemoria` que esos tres modulos EMITEN en la corrida de
referencia (`indice_formulas.corrida_de_referencia`, la misma del indice de
formulas), que las unidades declaradas en la sustitucion sean consistentes
con la unidad del resultado. Lo hace con un algebra de dimensiones minima
--- exponentes racionales de longitud, tiempo y masa --- y con un MAPA de
unidad SI a dimension que vive AQUI y no en `src/`: es una guardia de la
suite, no un valor de proyecto, y el plan lo pide asi.

Las relaciones dimensionales de cada paso se declaran en `RELACIONES`,
escritas a mano desde la formula que el paso imprime: no se parsea la prosa
de `PasoDeMemoria.formula`, porque un parser de prosa falla en silencio y una
relacion escrita se lee. El censo se comprueba en las dos direcciones: todo
paso de M3-M5 de la corrida tiene relacion declarada, y toda relacion
declarada corresponde a un paso de la corrida.

Lo que el piloto ENCONTRO en I4, y lo que PD CERRO
--------------------------------------------------
I4 midio cuatro inconsistencias, todas de PRESENTACION y ninguna de valor,
y las dejo censadas sin corregir (regla de aquella sesion: «reporta, no
corrijas; su correccion es sesion aparte porque toca el motor validado»).
PD las cerro sin mover un solo numero: (1) el coeficiente de unidades de
Manning se declaro como `K_MANNING_SI = 1.0 m^(1/3)/s` y el paso 4.1 lo
trae en su sustitucion --multiplicar por 1.0 es la identidad--; (2) el paso
4.2 trae el D con que HW/D pasa a HW_entrada; (3) el paso 4.3 imprime el D y
el HW/D sobre el que juzga su umbral; (4) el comentario de `K_FRICCION_SI`
dice la derivacion que cierra (2·32.2/1.486² = 29.164) y no la que no
cierra (el 29 redondeado). Los dos censos --- `INHOMOGENEIDADES_CENSADAS` y
`UMBRALES_INCONMENSURABLES_CENSADOS` --- quedan VACIOS y se conservan como
guardia: el test sigue exigiendo que lo medido sea EXACTAMENTE lo censado,
de modo que una inconsistencia nueva falla con nombre, y una entrada que
alguien censara sin que se mida tambien. La decision de I4 y su cierre en
PD estan en `docs/decisiones_diferidas.md` (ficha I4-01).

Las constantes con sufijo `_SI`
-------------------------------
CLAUDE.md manda que toda constante empirica dependiente de unidades lleve el
sufijo `_SI` y un comentario con el valor imperial. `CONSTANTES_SI` censa
las que `constantes_normativas.py` declara (y el test exige que sean todas),
y por cada una comprueba tres cosas: (1) que la dimension que le atribuye la
formula en que entra CIERRA esa formula; (2) que el valor SI se obtiene del
imperial del comentario convirtiendo con esa dimension --- o, si no, que el
censo lo diga y explique desde que cifra si cierra ---; (3) si alguna
sustitucion de la corrida la nombra, porque una constante que ningun paso
imprime no puede verificarse «en la sustitucion» de nada. Desde PD son
TRES --- `KU_SI`, `K_MANNING_SI` y `K_FRICCION_SI` --- y las tres cierran
desde la cifra imperial que su comentario declara.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Dict, Tuple

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import constantes_normativas as cn                                 # noqa: E402
from tests.apoyo.aproximacion import REL_TRANSPORTE                # noqa: E402
import indice_formulas as ind                                      # noqa: E402

MODULOS_DEL_PILOTO = ("M3_hidraulica", "M4_control", "M5_verificaciones")


# ===========================================================================
# El algebra de dimensiones: exponentes racionales, sin floats
# ===========================================================================

class DimensionIncompatible(Exception):
    """Suma o resta de dos dimensiones distintas."""


@dataclass(frozen=True)
class Dim:
    """Una dimension fisica como exponentes racionales de L, T y M."""

    L: F = F(0)
    T: F = F(0)
    M: F = F(0)

    def __mul__(self, otra: "Dim") -> "Dim":
        return Dim(self.L + otra.L, self.T + otra.T, self.M + otra.M)

    def __truediv__(self, otra: "Dim") -> "Dim":
        return Dim(self.L - otra.L, self.T - otra.T, self.M - otra.M)

    def __pow__(self, exponente) -> "Dim":
        e = F(exponente)
        return Dim(self.L * e, self.T * e, self.M * e)

    def __add__(self, otra: "Dim") -> "Dim":
        if self != otra:
            raise DimensionIncompatible(f"{self} + {otra}")
        return self

    __sub__ = __add__

    def __str__(self) -> str:
        partes = [f"{n}^{v}" for n, v in (("L", self.L), ("T", self.T),
                                          ("M", self.M)) if v != 0]
        return "·".join(partes) if partes else "1"


ADIM = Dim()
L = Dim(L=F(1))
T = Dim(T=F(1))
M = Dim(M=F(1))

# El MAPA de unidad SI a dimension. Vive aqui a proposito (ver docstring del
# modulo). `msnm` es una cota: una longitud sobre un origen fijo, que se suma
# con metros y se compara con otra cota. `anios` es tiempo. `%` y `H:V` son
# razones. `m/m` es la pendiente, adimensional.
UNIDADES: Dict[str, Dim] = {
    "": ADIM,
    "m": L,
    "mm": L,
    "m2": L ** 2,
    "m3": L ** 3,
    "m3/s": L ** 3 / T,
    "m/s": L / T,
    "m/s2": L / T ** 2,
    "m^(1/3)/s": L ** F(1, 3) / T,      # k_n, el coeficiente de Manning
    "m/m": ADIM,
    "msnm": L,
    "%": ADIM,
    "H:V": ADIM,
    "anios": T,
    "grados": ADIM,
    "Pa": M / (L * T ** 2),
    "kPa": M / (L * T ** 2),
    "MPa": M / (L * T ** 2),
    "kN": M * L / T ** 2,
    "kN/m": M / T ** 2,
    "kN/m2": M / (L * T ** 2),
    "kN/m3": M / (L ** 2 * T ** 2),
    "kg/m3": M / L ** 3,
}

# Constantes que las formulas usan sin ponerlas en la sustitucion: la
# gravedad entra en el tirante critico como `g` y no como `Magnitud`.
CONSTANTES_IMPLICITAS: Dict[str, Dim] = {"g": L / T ** 2}


def _dim(unidad: str) -> Dim:
    if unidad not in UNIDADES:
        raise KeyError(f"unidad sin dimension en el mapa del piloto: {unidad!r}")
    return UNIDADES[unidad]


def _evaluar(expresion: str, v: Dict[str, Dim], r: Dim) -> Dim:
    """
    Evalua una expresion dimensional escrita en Python: `v['A'] / v['P']`,
    `r`, `g`, `F(2, 3)` para exponentes racionales.
    """
    return eval(expresion, {"F": F, "ADIM": ADIM, "__builtins__": {},
                            **CONSTANTES_IMPLICITAS},
                {"v": v, "r": r})


# ===========================================================================
# Las relaciones dimensionales de cada paso de M3-M5, escritas desde su formula
# ===========================================================================
# Clave: `fundamento_id@codigo` (F4.CONTROL emite dos pasos, 4.2 y 4.4). Cada
# relacion es (id, lado_izquierdo, lado_derecho): `r` es la dimension del
# resultado y `v[...]` la de cada variable de la sustitucion.
Relacion = Tuple[str, str, str]
RELACIONES: Dict[str, Tuple[Relacion, ...]] = {
    # M3 --- TW por la via declarada: la sustitucion trae solo el TW
    # declarado y el resultado es ese mismo TW.
    "F1.TW@1.3": (
        ("TW=TW_declarado", "r", "v['TW']"),
    ),
    # M4 --- A = (D^2/8)(theta - sen theta), P = D*theta/2, R = A/P.
    "F4.SECCION@4.1": (
        ("R=A/P", "r", "v['A'] / v['P']"),
        ("A~D^2", "v['A']", "v['D'] ** 2"),
        ("P~D", "v['P']", "v['D']"),
        ("y~D", "v['y']", "v['D']"),
    ),
    # M4 --- Q = (k_n/n) * A * R^(2/3) * S^(1/2), con A ~ D^2 y R ~ D del paso
    # anterior. Cierra desde PD porque el paso trae k_n, el coeficiente de
    # unidades (L^(1/3)/T): sin el, la relacion no cerraba y estaba censada.
    "F4.MANNING@4.1": (
        ("y_normal~D", "r", "v['D']"),
        ("Q=(k_n/n)·A·R^(2/3)·S^(1/2)", "v['Q']",
         "v['k_n'] * v['D'] ** 2 * v['D'] ** F(2, 3) * v['S'] ** F(1, 2) "
         "/ v['n_max']"),
    ),
    # M4 --- Q^2/g = A^3/T, con A ~ D^2 y T ~ D.
    "F4.YC_RECT@4.2.1": (
        ("y_c~D", "r", "v['D']"),
        ("Q^2/g=A^3/T", "v['Q'] ** 2 / g", "v['D'] ** 5"),
    ),
    # M4 --- la forma de la ecuacion: todo adimensional.
    "F4.FORMA_HDS5@4.2": (
        ("forma~K", "r", "v['K']"),
        ("M adimensional", "v['M']", "ADIM"),
    ),
    # M4 --- HW/D = H_c/D + K*(q*)^M + Ks*S: el resultado es HW_entrada [m],
    # y desde PD la sustitucion trae el D que lo convierte; q* y Ks son
    # adimensionales.
    "F4.CONTROL@4.2": (
        ("HW_entrada=D·(HW/D)", "r", "v['D']"),
        ("q* adimensional", "v['q*']", "ADIM"),
        ("Ks adimensional", "v['Ks']", "ADIM"),
    ),
    # M4 --- HW = H + h_o - S*L, con h_o = max(TW, (y_c + D)/2).
    # Desde PD la sustitucion trae ademas D y HW/D, que es la magnitud sobre
    # la que el umbral del paso juzga (ver `UMBRAL_JUZGA`).
    "F4.HO@4.3": (
        ("HW=H+h_o-S·L", "r", "v['H'] + v['h_o'] - v['S*L']"),
        ("h_o~TW", "v['h_o']", "v['TW']"),
        ("h_o~(y_c+D)/2", "v['h_o']", "v['(y_c + D)/2']"),
        ("HW/D=HW_salida/D", "v['HW/D']", "r / v['D']"),
    ),
    # M4 --- regimen del barril y velocidad de salida (EXT-3, HDS-5 3.1.6):
    # y_salida = min(D, max(TW, y_c)) es una longitud, y V_salida = Q/A con
    # A ~ D^2. `regimen` y `control` son rotulos adimensionales y no entran.
    "F4.REGIMEN@4.3b": (
        ("y_salida~TW", "v['y_salida']", "v['TW']"),
        ("y_salida~y_c", "v['y_salida']", "v['y_c']"),
        ("y_salida~D", "v['y_salida']", "v['D']"),
        ("V_llena~Q_celda/D^2", "v['V_llena']", "v['Q_celda'] / v['D'] ** 2"),
        ("V_salida~V_llena", "r", "v['V_llena']"),
        ("V_salida~Q_celda/D^2", "r", "v['Q_celda'] / v['D'] ** 2"),
    ),
    # M4 --- HW = max(HW_entrada, HW_salida).
    "F4.CONTROL@4.4": (
        ("HW~HW_entrada", "r", "v['HW_entrada']"),
        ("HW~HW_salida", "r", "v['HW_salida']"),
    ),
    # M5 --- y/D <= 0.75.
    "F5.V1@V1": (
        ("y/D", "r", "v['y_normal'] / v['D']"),
    ),
    # M5 --- V >= 0.25 m/s.
    "F5.V2@V2": (
        ("V", "r", "v['V_sedimentacion']"),
    ),
    # M5 --- S_conducto >= S_cauce, resultado la diferencia.
    "F5.V2b@V2b": (
        ("S_conducto-S_cauce", "r", "v['S_conducto'] - v['S_cauce']"),
    ),
    # M5 --- V <= v_max.
    "F5.V3@V3": (
        ("V", "r", "v['V_erosion']"),
    ),
    # M5 --- cota_entrada + HW <= cota_subrasante - resguardo(CBR).
    "F5.V4@V4": (
        ("cota_entrada+HW", "r", "v['cota_entrada'] + v['HW']"),
        ("cota_subrasante-resguardo", "v['cota_subrasante']", "v['resguardo']"),
    ),
}

# Las relaciones que NO cierran, con la razon. El test exige igualdad exacta
# entre lo medido y esto. VACIO DESDE PD, y se conserva a proposito: I4 dejo
# aqui dos entradas --Manning sin su coeficiente de unidades, y el paso 4.2
# sin el D que convierte HW/D en HW_entrada-- y PD las cerro en el codigo
# (ver el docstring del modulo). Una entrada nueva aqui tiene que venir con
# su razon y con la palabra «candidato a hallazgo», como manda
# `test_cada_hallazgo_censado_lleva_su_razon_escrita`.
INHOMOGENEIDADES_CENSADAS: Dict[str, str] = {}

# Umbrales cuya unidad no es la del resultado contra el que el paso dice
# compararlo, con la razon. VACIO DESDE PD: el paso 4.3 juzgaba HW/D e
# imprimia HW_salida [m]; hoy trae HW/D en su sustitucion y lo declara en
# `UMBRAL_JUZGA`.
UMBRALES_INCONMENSURABLES_CENSADOS: Dict[str, str] = {}

# Sobre QUE magnitud juzga el umbral de un paso cuando no es el resultado.
# Por omision el umbral se compara con `paso.resultado`; los pasos de aqui
# lo comparan con una magnitud de su SUSTITUCION, que tiene que existir y
# tener la unidad del umbral. Es una declaracion escrita, no un parser de
# la prosa del umbral (misma regla que `RELACIONES`).
UMBRAL_JUZGA: Dict[str, str] = {
    "F4.HO@4.3": "HW/D",
}


# ===========================================================================
# Las constantes _SI
# ===========================================================================

# 1 ft = 0.3048 m, exacto por definicion (acuerdo internacional de 1959).
M_POR_FT = 0.3048
# HDS-5 trabaja con g = 32.2 ft/s^2 y phi = 1.486 (coeficiente de Manning en
# el sistema ingles, el mismo que `K_MANNING_SI` nombra como imperial);
# K = 2g/phi^2 es la relacion que el propio comentario de `K_FRICCION_SI`
# establece y verifica contra la 3a ed.
G_FT_S2 = 32.2
PHI_MANNING_INGLES = 1.486
# El «29» con que HDS-5 imprime K en el sistema ingles, redondeado: desde el
# NO se cierra al 19.63, y el comentario de la constante lo dice desde PD.
IMPERIAL_REDONDEADO_K_FRICCION = r"OJO:\s*([0-9.]+) es el valor ingles"
# Tolerancia relativa con que se declara que un valor SI «cierra» desde su
# imperial: 1e-3 admite el redondeo a cuatro cifras con que HDS-5 imprime
# 1.811 y 19.63, y rechaza el 0.6 % que separa 19.63 de la conversion del
# 29 redondeado. No es una tolerancia de calculo: es el criterio de este
# chequeo, y por eso vive aqui y no en `src/tolerancias.py`.
REL_CIERRE_DIMENSIONAL = 1e-3


@dataclass(frozen=True)
class ConstanteSI:
    """
    Como se verifica una constante `_SI`: la formula en que entra (con la
    dimension de cada simbolo), la dimension que le hace cerrar esa formula,
    donde esta el imperial en su comentario, y la huella con que se la busca
    en las sustituciones de la corrida.
    """

    dimension: Dim
    formula: str                       # expresion con `c` = la constante
    simbolos: Dict[str, Dim]
    cierra_a: Dim
    imperial_en_comentario: str        # regex con un grupo: la cifra imperial
    huella_en_los_pasos: str           # regex sobre formula + procedencias
    cierra_desde_el_comentario: bool   # ver `test_cada_constante_SI_...`
    la_nombra_algun_paso: bool
    nota: str


CONSTANTES_SI: Dict[str, ConstanteSI] = {
    "KU_SI": ConstanteSI(
        dimension=T / L ** F(1, 2),
        formula="c * v['Q'] / (v['A_llena'] * v['D'] ** F(1, 2))",
        simbolos={"Q": L ** 3 / T, "A_llena": L ** 2, "D": L},
        cierra_a=ADIM,
        imperial_en_comentario=r"Imperial:\s*([0-9.]+)",
        huella_en_los_pasos=r"\bKu\b",
        cierra_desde_el_comentario=True,
        la_nombra_algun_paso=True,
        nota="q* = Ku·Q/(A·D^0.5) es adimensional solo si Ku lleva s/m^0.5: "
             "1.0 s/ft^0.5 = 1.8112 s/m^0.5, que es el 1.811 de HDS-5."),
    "K_MANNING_SI": ConstanteSI(
        dimension=L ** F(1, 3) / T,
        formula="c * v['A'] * v['R'] ** F(2, 3) * v['S'] ** F(1, 2) / v['n']",
        simbolos={"A": L ** 2, "R": L, "S": ADIM, "n": ADIM},
        cierra_a=L ** 3 / T,
        imperial_en_comentario=r"Imperial:\s*([0-9.]+)",
        huella_en_los_pasos=r"K_MANNING_SI|\bk_n\b",
        cierra_desde_el_comentario=True,
        la_nombra_algun_paso=True,
        nota="Q = (k_n/n)·A·R^(2/3)·S^(1/2) tiene dimension L^3/T solo si k_n "
             "lleva L^(1/3)/T: 1.486 ft^(1/3)/s = 1.00005 m^(1/3)/s, que es el "
             "1.0 del SI (el 1.486 es 1/0.3048^(1/3) = 1.4859 redondeado). "
             "Lo declaro PD; el paso 4.1 lo trae como k_n."),
    "K_FRICCION_SI": ConstanteSI(
        dimension=L ** F(1, 3),
        formula="c * v['n'] ** 2 * v['L'] / v['R'] ** F(4, 3)",
        simbolos={"n": ADIM, "L": L, "R": L},
        cierra_a=ADIM,
        # El EXACTO que el comentario declara desde PD, no el 29 redondeado
        # (ese se mide aparte, con `IMPERIAL_REDONDEADO_K_FRICCION`).
        imperial_en_comentario=r"Exacto:\s*2\*32\.2/1\.486\^2 = ([0-9.]+)",
        huella_en_los_pasos=r"K_FRICCION_SI|K_friccion|19\.63",
        cierra_desde_el_comentario=True,
        la_nombra_algun_paso=False,
        nota="K = 2g/phi^2 lleva m^(1/3) si n es adimensional. Desde el "
             "exacto 2·32.2/1.486^2 = 29.164 la conversion da 19.627, que "
             "es el 19.63 transcrito; desde el «29» impreso "
             "--29.164 redondeado-- da 19.51, un 0.6 % por debajo, y el "
             "comentario dice desde PD cual de las dos derivaciones es la que "
             "cierra. Sigue sin nombrarla ningun paso de la corrida: el paso "
             "4.3 recibe H como numero con la procedencia «perdida de carga en "
             "el barril», y transcribir la formula de H es un paso nuevo que "
             "PD no abrio (ficha I4-01)."),
}


def _comentario_de(nombre: str) -> str:
    """La linea de asignacion y los comentarios que la siguen, sin saltos."""
    lineas = (SRC / "constantes_normativas.py").read_text(
        encoding="utf-8").split("\n")
    for i, linea in enumerate(lineas):
        if re.match(rf"^{nombre}\s*=", linea):
            bloque = [linea]
            for siguiente in lineas[i + 1:]:
                if siguiente.strip().startswith("#"):
                    bloque.append(siguiente)
                else:
                    break
            return "\n".join(bloque)
    raise KeyError(nombre)


def _nombres_SI_declarados() -> set:
    fuente = (SRC / "constantes_normativas.py").read_text(encoding="utf-8")
    # Solo las asignaciones NUMERICAS: `NUMERAL_KU_SI` es el texto de una
    # cita y lleva el sufijo por arrastre del nombre de la constante.
    return set(re.findall(r"^([A-Z0-9_]+_SI)\s*=\s*[0-9]", fuente, flags=re.M))


# ===========================================================================
# Fixtures: los pasos de M3-M5 de la corrida de referencia
# ===========================================================================

@pytest.fixture(scope="module")
def pasos_del_piloto():
    emisores = ind.emisores_por_fundamento()
    informe = ind.corrida_de_referencia()
    return tuple(p for p in ind.pasos_de_la_corrida(informe)
                 if any(m in MODULOS_DEL_PILOTO
                        for m in emisores.get(p.fundamento_id, ())))


def _clave(paso) -> str:
    return f"{paso.fundamento_id}@{paso.codigo}"


def _variables(paso) -> Dict[str, Dim]:
    return {m.simbolo: _dim(m.unidad) for m in paso.sustitucion}


def _texto_del_paso(paso) -> str:
    return " ".join([paso.formula, paso.nota_del_proyecto,
                     paso.resultado.procedencia]
                    + [m.procedencia for m in paso.sustitucion])


# ===========================================================================
# El algebra probandose a si misma
# ===========================================================================

def test_el_algebra_dimensional_multiplica_divide_y_eleva():
    assert (L ** 3 / T) / (L ** 2 * L ** F(1, 2)) == L ** F(1, 2) / T
    assert (L / T) ** 2 / (L / T ** 2) == L
    assert str(ADIM) == "1"


def test_el_algebra_rechaza_sumar_dimensiones_distintas():
    with pytest.raises(DimensionIncompatible):
        _ = L + T
    assert L + L == L


def test_el_evaluador_ve_las_variables_el_resultado_y_la_gravedad():
    v = {"Q": UNIDADES["m3/s"], "D": L}
    assert _evaluar("v['Q'] ** 2 / g", v, L) == L ** 5
    assert _evaluar("r", v, L) == L


# ===========================================================================
# El piloto
# ===========================================================================

def test_el_piloto_alcanza_los_tres_modulos(pasos_del_piloto):
    emisores = ind.emisores_por_fundamento()
    alcanzados = {m for p in pasos_del_piloto
                  for m in emisores[p.fundamento_id]}
    assert alcanzados == set(MODULOS_DEL_PILOTO), alcanzados


def test_toda_unidad_de_M3_a_M5_esta_en_el_mapa(pasos_del_piloto):
    sin_dimension = set()
    for paso in pasos_del_piloto:
        for m in paso.sustitucion + (paso.resultado,):
            if m.unidad not in UNIDADES:
                sin_dimension.add(m.unidad)
        if paso.umbral is not None and paso.umbral.unidad not in UNIDADES:
            sin_dimension.add(paso.umbral.unidad)
    assert not sin_dimension, sin_dimension


def test_todo_paso_del_piloto_tiene_relacion_declarada_y_ninguna_sobra(
        pasos_del_piloto):
    """
    Las dos direcciones: un paso nuevo de M3-M5 sin relacion falla, y una
    relacion cuyo paso ya no se emite tambien, para que el censo no se
    quede describiendo un calculo que ya no existe.
    """
    emitidos = {_clave(p) for p in pasos_del_piloto}
    assert emitidos == set(RELACIONES), (
        f"sin relacion: {sorted(emitidos - set(RELACIONES))}; "
        f"relaciones sin paso: {sorted(set(RELACIONES) - emitidos)}")


def test_toda_relacion_nombra_solo_variables_que_el_paso_sustituye(
        pasos_del_piloto):
    for paso in pasos_del_piloto:
        v = _variables(paso)
        for id_, izq, der in RELACIONES[_clave(paso)]:
            for expresion in (izq, der):
                for simbolo in re.findall(r"v\['([^']+)'\]", expresion):
                    assert simbolo in v, (_clave(paso), id_, simbolo)


def _inhomogeneidades(pasos) -> Dict[str, str]:
    """{clave:id -> 'izq vs der'} de las relaciones que no cierran."""
    medidas = {}
    for paso in pasos:
        v = _variables(paso)
        r = _dim(paso.resultado.unidad)
        for id_, izq, der in RELACIONES[_clave(paso)]:
            try:
                a = _evaluar(izq, v, r)
                b = _evaluar(der, v, r)
            except DimensionIncompatible as e:
                medidas[f"{_clave(paso)}:{id_}"] = f"suma incompatible: {e}"
                continue
            if a != b:
                medidas[f"{_clave(paso)}:{id_}"] = f"{a} vs {b}"
    return medidas


def test_las_relaciones_cierran_salvo_las_censadas(pasos_del_piloto):
    """
    REPORTA, NO CORRIGE. Lo medido tiene que ser exactamente lo censado:
    una inconsistencia nueva es un hallazgo sin declarar, y una censada que
    ya no se mide es un censo que miente.
    """
    medidas = _inhomogeneidades(pasos_del_piloto)
    nuevas = sorted(set(medidas) - set(INHOMOGENEIDADES_CENSADAS))
    assert not nuevas, {k: medidas[k] for k in nuevas}
    resueltas = sorted(set(INHOMOGENEIDADES_CENSADAS) - set(medidas))
    assert not resueltas, (
        f"censadas y ya no medidas: {resueltas}. Si se corrigio el paso, "
        "retira la entrada del censo en el mismo commit")


def test_manning_cierra_con_k_n_y_sin_k_n_le_falta_L_un_tercio_sobre_T():
    """
    La afirmacion positiva que I4 dejo en negativo: con k_n de dimension
    L^(1/3)/T en la sustitucion, Manning CIERRA. Y se conserva el numero
    que I4 midio --sin k_n le falta exactamente L^(1/3)/T--, porque es lo
    que permite decir que lo que cerro la formula fue el coeficiente de
    unidades y no otra cosa.
    """
    _, izq, der = RELACIONES["F4.MANNING@4.1"][1]
    con = {"Q": UNIDADES["m3/s"], "S": ADIM, "D": L, "n_max": ADIM,
           "k_n": UNIDADES["m^(1/3)/s"]}
    assert _evaluar(izq, con, L) == _evaluar(der, con, L)
    sin = dict(con, k_n=ADIM)
    assert _evaluar(izq, sin, L) / _evaluar(der, sin, L) == L ** F(1, 3) / T


def test_las_tres_funciones_de_manning_de_M3_multiplican_por_K_MANNING_SI():
    """
    LA GUARDIA DEL MOTOR, no solo de la memoria. El auditor de PD midio que
    revertir `M3._caudal_manning` a `(1 / n)` dejaba la suite verde: el paso
    4.1 lee `K_MANNING_SI` por su cuenta y las relaciones cerraban igual.
    Aqui se lee el AST de M3 y se exige que las tres funciones que aplican
    Manning nombren la constante --el mismo recurso que la suite usa contra
    M11--, para que «declarado» sea una propiedad del calculo y no del
    reporte.
    """
    arbol = ast.parse((SRC / "modulos" / "M3_hidraulica.py").read_text(
        encoding="utf-8"))
    funciones = {n.name: n for n in ast.walk(arbol)
                 if isinstance(n, ast.FunctionDef)}
    for nombre in ("_caudal_manning", "resolver_manning",
                   "caudal_manning_trapecial"):
        nombres = {n.id for n in ast.walk(funciones[nombre])
                   if isinstance(n, ast.Name)}
        assert "K_MANNING_SI" in nombres, (
            f"M3.{nombre} aplica Manning sin nombrar K_MANNING_SI: el "
            "coeficiente de unidades volvio a quedar implicito en (1/n)")


def test_el_paso_de_manning_trae_el_coeficiente_de_unidades_con_su_unidad(
        pasos_del_piloto):
    """El k_n de cada paso 4.1 es K_MANNING_SI, en m^(1/3)/s, y vale 1.0."""
    pasos = [p for p in pasos_del_piloto if _clave(p) == "F4.MANNING@4.1"]
    assert pasos
    for paso in pasos:
        k = {m.simbolo: m for m in paso.sustitucion}["k_n"]
        assert k.unidad == "m^(1/3)/s"
        # Se TRANSPORTA (es la constante, no un calculo), y vale 1.0 exacto:
        # la tolerancia nombrada es la de transporte.
        assert k.valor == pytest.approx(cn.K_MANNING_SI, rel=REL_TRANSPORTE)
        assert cn.K_MANNING_SI == pytest.approx(1.0, rel=REL_TRANSPORTE)
        assert "K_MANNING_SI" in k.procedencia
        assert "K_MANNING_SI" in paso.formula


def _magnitud_juzgada(paso):
    """
    La magnitud contra la que se compara el umbral: el resultado, salvo que
    `UMBRAL_JUZGA` nombre una de la sustitucion --que entonces tiene que
    estar--.
    """
    simbolo = UMBRAL_JUZGA.get(_clave(paso))
    if simbolo is None:
        return paso.resultado
    por_simbolo = {m.simbolo: m for m in paso.sustitucion}
    assert simbolo in por_simbolo, (
        f"{_clave(paso)}: UMBRAL_JUZGA nombra «{simbolo}» y el paso no lo "
        "sustituye")
    return por_simbolo[simbolo]


def test_los_umbrales_son_conmensurables_con_su_resultado_salvo_los_censados(
        pasos_del_piloto):
    medidos = {}
    for paso in pasos_del_piloto:
        if paso.umbral is None:
            continue
        r, u = _dim(_magnitud_juzgada(paso).unidad), _dim(paso.umbral.unidad)
        if r != u:
            medidos[_clave(paso)] = f"juzgada {r} vs umbral {u}"
    nuevos = sorted(set(medidos) - set(UMBRALES_INCONMENSURABLES_CENSADOS))
    assert not nuevos, {k: medidos[k] for k in nuevos}
    resueltos = sorted(set(UMBRALES_INCONMENSURABLES_CENSADOS) - set(medidos))
    assert not resueltos, resueltos


def test_cada_hallazgo_censado_lleva_su_razon_escrita():
    for censo in (INHOMOGENEIDADES_CENSADAS, UMBRALES_INCONMENSURABLES_CENSADOS):
        for id_, razon in censo.items():
            assert razon.strip() and "andidato a hallazgo" in razon, id_


def test_los_dos_censos_estan_en_cero_desde_PD():
    """
    El objetivo de PD escrito como aserto: ningun hallazgo censado. Si
    alguien vuelve a censar uno, este test lo dice antes de que el censo
    crezca en silencio, y la ficha I4-01 tiene que decir que volvio a haber.
    """
    assert INHOMOGENEIDADES_CENSADAS == {}
    assert UMBRALES_INCONMENSURABLES_CENSADOS == {}


def test_todo_umbral_juzgado_sobre_una_sustitucion_lo_imprime_con_su_unidad(
        pasos_del_piloto):
    """
    `UMBRAL_JUZGA` en las dos direcciones: cada clave es un paso con umbral
    de la corrida, y su magnitud esta en la sustitucion con la unidad del
    umbral (es lo que PD añadio al paso 4.3: el HW/D que antes se juzgaba
    sin imprimirse).
    """
    con_umbral = {_clave(p): p for p in pasos_del_piloto if p.umbral is not None}
    for clave, simbolo in UMBRAL_JUZGA.items():
        assert clave in con_umbral, clave
        m = _magnitud_juzgada(con_umbral[clave])
        assert m.simbolo == simbolo
        assert m.unidad == con_umbral[clave].umbral.unidad


# ===========================================================================
# Las constantes _SI
# ===========================================================================

def test_el_censo_de_constantes_SI_es_el_del_archivo():
    """Toda constante `_SI` de `constantes_normativas.py` se verifica aqui."""
    assert _nombres_SI_declarados() == set(CONSTANTES_SI)


@pytest.mark.parametrize("nombre", sorted(CONSTANTES_SI))
def test_la_dimension_de_cada_constante_SI_cierra_su_formula(nombre):
    c = CONSTANTES_SI[nombre]
    cerrada = eval(c.formula, {"F": F, "__builtins__": {}},
                   {"c": c.dimension, "v": c.simbolos})
    assert cerrada == c.cierra_a, f"{nombre}: {cerrada} vs {c.cierra_a}"


@pytest.mark.parametrize("nombre", sorted(CONSTANTES_SI))
def test_cada_constante_SI_cierra_o_dice_por_que_no_con_su_comentario_imperial(
        nombre):
    """
    valor_SI = valor_imperial * (0.3048 m/ft)^(exponente de longitud). Si el
    censo dice que cierra, tiene que cerrar; si dice que no, tiene que NO
    cerrar (para que el censo no siga diciendo algo que se corrigio) y la
    nota tiene que decir desde que cifra si cierra.
    """
    c = CONSTANTES_SI[nombre]
    comentario = _comentario_de(nombre)
    m = re.search(c.imperial_en_comentario, comentario)
    assert m, f"{nombre}: el comentario no trae el valor imperial"
    imperial = float(m.group(1))
    valor_si = getattr(cn, nombre)
    # Solo se convierte la longitud: el segundo es el mismo en los dos
    # sistemas, y la masa no entra en ninguna de las dos constantes.
    convertido = imperial * M_POR_FT ** float(c.dimension.L)
    desvio = abs(convertido - valor_si) / valor_si
    if c.cierra_desde_el_comentario:
        assert desvio < REL_CIERRE_DIMENSIONAL, (nombre, convertido, valor_si)
    else:
        assert desvio > REL_CIERRE_DIMENSIONAL, (
            f"{nombre}: ahora SI cierra desde el comentario ({convertido} vs "
            f"{valor_si}); actualiza el censo")
        assert c.nota.strip(), nombre


def test_K_FRICCION_SI_cierra_desde_2g_sobre_phi_cuadrado_y_no_desde_el_29():
    """
    El numero: 2·32.2/1.486^2 = 29.164 ft^(1/3) -> 19.627 m^(1/3), que es
    el 19.63 transcrito; el «29» impreso -> 19.51, un 0.6 %
    por debajo. Es lo que el comentario de la constante ya explica, medido.
    """
    exacto = 2 * G_FT_S2 / PHI_MANNING_INGLES ** 2
    desde_exacto = exacto * M_POR_FT ** (1 / 3)
    assert abs(desde_exacto - cn.K_FRICCION_SI) / cn.K_FRICCION_SI \
        < REL_CIERRE_DIMENSIONAL
    imperial = float(re.search(IMPERIAL_REDONDEADO_K_FRICCION,
                               _comentario_de("K_FRICCION_SI")).group(1))
    assert imperial == 29
    desde_redondeado = imperial * M_POR_FT ** (1 / 3)
    assert abs(desde_redondeado - cn.K_FRICCION_SI) / cn.K_FRICCION_SI \
        > REL_CIERRE_DIMENSIONAL


@pytest.mark.parametrize("nombre", sorted(CONSTANTES_SI))
def test_si_algun_paso_de_la_corrida_nombra_la_constante_SI(nombre,
                                                              pasos_del_piloto):
    """
    Una constante que ningun paso imprime no se puede verificar «en la
    sustitucion» de nada: KU_SI aparece en la procedencia de q*, y
    K_MANNING_SI, desde PD, como k_n en la sustitucion del paso 4.1;
    K_FRICCION_SI no aparece en ninguna, porque el paso 4.3 recibe H ya
    calculado. El censo lo dice y este test lo mide.
    """
    c = CONSTANTES_SI[nombre]
    nombrada = any(re.search(c.huella_en_los_pasos, _texto_del_paso(p))
                   for p in pasos_del_piloto)
    assert nombrada == c.la_nombra_algun_paso, (
        f"{nombre}: {'ya la nombra' if nombrada else 'no la nombra'} algun "
        "paso; actualiza el censo")
