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

Lo que el piloto ENCONTRO, y que este archivo REPORTA sin corregir
------------------------------------------------------------------
La regla del prompt es explicita: «reporta, no corrijas: cualquier
inconsistencia es un candidato a Discrepancia o a hallazgo, y su correccion
es sesion aparte (tocaria el motor validado --- regla: test que falle
antes)». Por eso los hallazgos viven en dos censos ---
`INHOMOGENEIDADES_CENSADAS` y `UMBRALES_INCONMENSURABLES_CENSADOS` --- y el
test exige que el conjunto medido sea EXACTAMENTE el censado: una
inconsistencia nueva falla, y una que alguien corrija sin retirarla del
censo tambien falla, para que el censo no se quede diciendo lo que ya no es.
La decision de no corregir aqui y de no extender el barrido esta en
`docs/decisiones_diferidas.md` (ficha I4-01).

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
imprime no puede verificarse «en la sustitucion» de nada.
"""

from __future__ import annotations

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
    # M4 --- Q = (1/n) * A * R^(2/3) * S^(1/2), con A ~ D^2 y R ~ D del paso
    # anterior. La segunda relacion es la que NO cierra: ver el censo.
    "F4.MANNING@4.1": (
        ("y_normal~D", "r", "v['D']"),
        ("Q=(1/n)·A·R^(2/3)·S^(1/2)", "v['Q']",
         "v['D'] ** 2 * v['D'] ** F(2, 3) * v['S'] ** F(1, 2) / v['n_max']"),
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
    # M4 --- HW/D = H_c/D + K*(q*)^M + Ks*S. El resultado es HW_entrada [m] y
    # la sustitucion trae q* y Ks, adimensionales: NO cierra sin D. Censado.
    "F4.CONTROL@4.2": (
        ("HW_entrada~q*·Ks", "r", "v['q*'] * v['Ks']"),
    ),
    # M4 --- HW = H + h_o - S*L, con h_o = max(TW, (y_c + D)/2).
    "F4.HO@4.3": (
        ("HW=H+h_o-S·L", "r", "v['H'] + v['h_o'] - v['S*L']"),
        ("h_o~TW", "v['h_o']", "v['TW']"),
        ("h_o~(y_c+D)/2", "v['h_o']", "v['(y_c + D)/2']"),
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
# entre lo medido y esto.
INHOMOGENEIDADES_CENSADAS: Dict[str, str] = {
    "F4.MANNING@4.1:Q=(1/n)·A·R^(2/3)·S^(1/2)": (
        "Manning es una formula empirica NO homogenea: con n adimensional, "
        "A·R^(2/3)·S^(1/2) tiene dimension L^(8/3) y Q tiene L^3/T. La "
        "diferencia, L^(1/3)/T, la absorbe el coeficiente de unidades k_n "
        "(1.0 m^(1/3)/s en SI; 1.486 ft^(1/3)/s en el sistema ingles), que la "
        "formula de la Sec. 4.1 escribe como «1/n» y `M3._caudal_manning` "
        "aplica como (1/n) sin declarar. Es una constante empirica "
        "dependiente de unidades sin nombre `_SI` ni comentario imperial: "
        "candidato a hallazgo contra la regla de unidades de CLAUDE.md, no "
        "un error de calculo (el 1.0 esta implicito y es el correcto en SI)."),
    "F4.CONTROL@4.2:HW_entrada~q*·Ks": (
        "El paso 4.2 imprime HW/D = ... y devuelve HW_entrada en metros con "
        "una sustitucion que solo trae q* y Ks, adimensionales: el D que "
        "convierte HW/D en HW --- y H_c/D, K, M y S en la Forma 1 --- estan "
        "en los pasos 4.1 y 4.2 anteriores, no en este. La sustitucion no "
        "cierra dimensionalmente por si sola. Candidato a hallazgo de "
        "presentacion de la memoria (la aritmetica de M4 es correcta)."),
}

# Umbrales cuya unidad no es la del resultado contra el que el paso dice
# compararlo, con la razon.
UMBRALES_INCONMENSURABLES_CENSADOS: Dict[str, str] = {
    "F4.HO@4.3": (
        "El resultado del paso es HW_salida [m] y su umbral es el HW/D "
        "minimo de validez de h_o, adimensional (0.75): el veredicto y su "
        "margen se calculan sobre HW/D (`salida.HW_sobre_D`), que no es el "
        "resultado impreso. Candidato a hallazgo de presentacion: el umbral "
        "juzga una magnitud derivada que el paso no imprime como resultado."),
}


# ===========================================================================
# Las constantes _SI
# ===========================================================================

# 1 ft = 0.3048 m, exacto por definicion (acuerdo internacional de 1959).
M_POR_FT = 0.3048
# HDS-5 trabaja con g = 32.2 ft/s^2 y phi = 1.486 (coeficiente de Manning en
# el sistema ingles); K = 2g/phi^2 es la relacion que el propio comentario de
# `K_FRICCION_SI` establece y verifica contra la 3a ed.
G_FT_S2 = 32.2
PHI_MANNING_INGLES = 1.486
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
    "K_FRICCION_SI": ConstanteSI(
        dimension=L ** F(1, 3),
        formula="c * v['n'] ** 2 * v['L'] / v['R'] ** F(4, 3)",
        simbolos={"n": ADIM, "L": L, "R": L},
        cierra_a=ADIM,
        imperial_en_comentario=r"OJO:\s*([0-9.]+) es el valor ingles",
        huella_en_los_pasos=r"K_FRICCION_SI|K_friccion|19\.63",
        cierra_desde_el_comentario=False,
        la_nombra_algun_paso=False,
        nota="K = 2g/phi^2 lleva m^(1/3) si n es adimensional. Desde el «29» "
             "del comentario --- que es 29.164 redondeado --- la conversion "
             "da 19.51, un 0.6 % por debajo del 19.63 transcrito; desde "
             "2·32.2/1.486^2 = 29.164 da 19.62, que cierra. Y ningun paso de "
             "la corrida transcribe la formula de H en que entra: el paso 4.3 "
             "recibe H como numero con la procedencia «perdida de carga en el "
             "barril». Candidato a hallazgo de presentacion, no de valor."),
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


def test_manning_no_cierra_por_L_un_tercio_sobre_T():
    """
    La diferencia dimensional de Manning es exactamente L^(1/3)/T, que es
    la dimension del coeficiente k_n. Se comprueba el NUMERO, no solo que
    no cierre: es lo que permite decir que el hallazgo es el coeficiente de
    unidades y no otra cosa.
    """
    v = {"Q": UNIDADES["m3/s"], "S": ADIM, "D": L, "n_max": ADIM}
    _, izq, der = RELACIONES["F4.MANNING@4.1"][1]
    assert _evaluar(izq, v, L) / _evaluar(der, v, L) == L ** F(1, 3) / T


def test_los_umbrales_son_conmensurables_con_su_resultado_salvo_los_censados(
        pasos_del_piloto):
    medidos = {}
    for paso in pasos_del_piloto:
        if paso.umbral is None:
            continue
        r, u = _dim(paso.resultado.unidad), _dim(paso.umbral.unidad)
        if r != u:
            medidos[_clave(paso)] = f"resultado {r} vs umbral {u}"
    nuevos = sorted(set(medidos) - set(UMBRALES_INCONMENSURABLES_CENSADOS))
    assert not nuevos, {k: medidos[k] for k in nuevos}
    resueltos = sorted(set(UMBRALES_INCONMENSURABLES_CENSADOS) - set(medidos))
    assert not resueltos, resueltos


def test_cada_hallazgo_censado_lleva_su_razon_escrita():
    for censo in (INHOMOGENEIDADES_CENSADAS, UMBRALES_INCONMENSURABLES_CENSADOS):
        for id_, razon in censo.items():
            assert razon.strip() and "andidato a hallazgo" in razon, id_


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
    El numero: 2·32.2/1.486^2 = 29.164 ft^(1/3) -> 19.62 m^(1/3), a menos
    de un 0.1 % del 19.63 transcrito; el «29» impreso -> 19.51, un 0.6 %
    por debajo. Es lo que el comentario de la constante ya explica, medido.
    """
    exacto = 2 * G_FT_S2 / PHI_MANNING_INGLES ** 2
    desde_exacto = exacto * M_POR_FT ** (1 / 3)
    assert abs(desde_exacto - cn.K_FRICCION_SI) / cn.K_FRICCION_SI \
        < REL_CIERRE_DIMENSIONAL
    imperial = float(re.search(CONSTANTES_SI["K_FRICCION_SI"].imperial_en_comentario,
                               _comentario_de("K_FRICCION_SI")).group(1))
    desde_redondeado = imperial * M_POR_FT ** (1 / 3)
    assert abs(desde_redondeado - cn.K_FRICCION_SI) / cn.K_FRICCION_SI \
        > REL_CIERRE_DIMENSIONAL


@pytest.mark.parametrize("nombre", sorted(CONSTANTES_SI))
def test_si_algun_paso_de_la_corrida_nombra_la_constante_SI(nombre,
                                                              pasos_del_piloto):
    """
    Una constante que ningun paso imprime no se puede verificar «en la
    sustitucion» de nada: KU_SI aparece en la procedencia de q*;
    K_FRICCION_SI no aparece en ninguna, porque el paso 4.3 recibe H ya
    calculado. El censo lo dice y este test lo mide.
    """
    c = CONSTANTES_SI[nombre]
    nombrada = any(re.search(c.huella_en_los_pasos, _texto_del_paso(p))
                   for p in pasos_del_piloto)
    assert nombrada == c.la_nombra_algun_paso, (
        f"{nombre}: {'ya la nombra' if nombrada else 'no la nombra'} algun "
        "paso; actualiza el censo")
