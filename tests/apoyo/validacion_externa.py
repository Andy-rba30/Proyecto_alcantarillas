"""
tests/apoyo/validacion_externa.py
=================================
La VALIDACION EXTERNA de T-11 (punto 2 del prompt): el motor contra los
EJEMPLOS RESUELTOS que publican las propias fuentes, generada en
`docs/validacion_hds5.md`. `tests/test_t11_validacion_externa.py` lo
regenera a memoria y lo compara, de modo que el documento no se puede
desincronizar del programa sin que la suite lo diga.

Regenerar::

    python -m tests.apoyo.validacion_externa --escribir

DE DONDE SALE CADA CIFRA, Y QUE SE COMPARA CON QUE
--------------------------------------------------
1. HDS-5, Design Guideline 1 (formularios DG 1.3.3 y DG 1.4.3). Los CASOS
   son `tests/fixtures/casos_patron.py::CP_HDS5_DG1`, los que T-2 transcribio
   y verifico contra su pagina, y la CUENTA es la del test de T-2
   (`tests/test_t2_hidraulica.py::_calcular_fila` y `_diferencia_relativa`,
   importadas, no copiadas): este modulo no tiene una segunda version de la
   comparacion. Se compara cada cifra PUBLICADA del formulario con la que da
   el motor (M3/M4) con los mismos datos convertidos a SI y devueltos en
   pies, con la tolerancia de LECTURA del 3 % y la de la FUENTE del 10 %
   («accurate to within plus or minus ten percent, in terms of headwater
   elevation», HDS-5 pag. impresa 3.1, PDF 83). Lo que cae fuera del 3 % lo
   censa el propio caso patron con su causa; aqui se imprime.
2. HEC-14, los ejemplos resueltos que T-8 uso como oraculo (apron SI y CU,
   hoya en suelo no cohesivo y cohesivo, Froude de la poza USBR VI). Las
   ENTRADAS y las cifras PUBLICADAS estan en `EJEMPLOS_HEC14`, con su pagina
   impresa y del PDF, y `tests/test_t11_validacion_externa.py` comprueba con
   PyMuPDF (marca `pdf`, con `NORMAS_DIR`) que cada cifra publicada esta
   escrita en esa pagina. La cuenta la hace M6 con las mismas llamadas que
   los tests de T-8 (`tests/test_t8_proteccion.py`, `test_t8_correcciones.py`).
   La tolerancia es la de T-8 para un ejemplo impreso (1 %: la fuente imprime
   dos o tres cifras y redondea los intermedios).

HY-8 NO esta en el entorno: el procedimiento para que el autor lo corra esta
en `docs/validacion_hy8.md`, escrito a mano y sin ningun resultado de HY-8.

Lo que este modulo NO hace: no corrige el motor ni la tolerancia para que un
caso entre, y no escribe en `src/`.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from src.modelos import Magnitud, MaterialLecho, SeccionCircular
from src.modulos import M6_proteccion as M6
from tests.fixtures.casos_patron import CP_HDS5_DG1
from tests.test_t2_hidraulica import _calcular_fila, _diferencia_relativa

RAIZ = Path(__file__).resolve().parents[2]
DOCUMENTO = RAIZ / "docs" / "validacion_hds5.md"

# La tolerancia de T-8 para un ejemplo impreso (`REL_EJEMPLO_IMPRESO` de
# `tests/test_t8_proteccion.py`): la fuente imprime dos o tres cifras.
TOLERANCIA_EJEMPLO_IMPRESO = 1e-2
M_POR_FT = 0.3048                       # exacto por definicion
# El ruido de la aritmetica en la frontera de una banda: una diferencia que
# es el 1 % o el 3 % exacto en decimal no puede caer del otro lado por 1e-17
# (H12 de la auditoria de T-11: 0.495 / 0.50 - 1 da -0.010000000000000009 y
# el documento lo censaba «fuera del 1 %»). Precision numerica, no un valor
# de proyecto: toda comparacion contra una banda de este modulo la suma.
TOL_FRONTERA_DE_BANDA = 1e-9


def dentro_de(diferencia: float, banda: float) -> bool:
    """|diferencia| <= banda, con la tolerancia de frontera nombrada."""
    return abs(diferencia) <= banda + TOL_FRONTERA_DE_BANDA


def _V(valor: float) -> Magnitud:
    return Magnitud("V_salida", valor, "m/s", "dato del ejemplo")


# ---------------------------------------------------------------------------
# 1. HDS-5
# ---------------------------------------------------------------------------

UNIDAD = {"HW_sobre_D": "—", "HW_entrada_ft": "ft", "d_c_ft": "ft",
          "h_o_ft": "ft", "H_ft": "ft", "EL_ho_ft": "ft",
          "V_salida_ft_s": "ft/s", "control": "—"}


@dataclass(frozen=True)
class FilaHDS5:
    grupo: str
    fila: str
    magnitud: str
    publicado: Any
    calculado: Any
    diferencia: Optional[float]     # relativa; None para «control»
    censada: str                    # la causa, si el caso patron la censa


def filas_hds5() -> Tuple[FilaHDS5, ...]:
    salida = []
    censo = CP_HDS5_DG1["fuera_de_tolerancia"]
    for nombre in ("circular", "cajon"):
        grupo = CP_HDS5_DG1[nombre]
        for fila in grupo["filas"]:
            calculado = _calcular_fila(grupo, fila)
            for magnitud, publicado in fila["publicado"].items():
                if magnitud == "control":
                    salida.append(FilaHDS5(nombre, fila["id"], magnitud,
                                           publicado, calculado["control"],
                                           None, ""))
                    continue
                dif = _diferencia_relativa(grupo, fila, magnitud,
                                           calculado[magnitud])
                salida.append(FilaHDS5(nombre, fila["id"], magnitud, publicado,
                                       calculado[magnitud], dif,
                                       censo.get((fila["id"], magnitud), "")))
    return tuple(salida)


@dataclass(frozen=True)
class FilaIntervalo:
    fila: str
    magnitud: str
    publicado: Any
    con_n_bajo: Any
    con_n_alto: Any
    con_n_tipico: Any


def filas_por_intervalo() -> Tuple[FilaIntervalo, ...]:
    """Las dos filas de metal corrugado, con el n acotado por la Tabla B.1."""
    grupo = CP_HDS5_DG1["circular"]
    n_lo, n_hi = grupo["n_interpretado"]["rango"]
    tipico = grupo["n_interpretado"]["tipico"]
    salida = []
    for fila in grupo["filas"]:
        if fila["n"] is not None:
            continue
        lo = _calcular_fila(grupo, fila, n=n_lo)
        hi = _calcular_fila(grupo, fila, n=n_hi)
        ti = _calcular_fila(grupo, fila, n=tipico)
        for magnitud, publicado in fila["publicado_con_n_interpretado"].items():
            clave = magnitud
            if magnitud == "V_salida_ft_s" and \
                    fila["publicado_con_n_interpretado"]["control"] == "salida":
                clave = "V_salida_por_y_c_ft_s"
            salida.append(FilaIntervalo(fila["id"], magnitud, publicado,
                                        lo[clave], hi[clave], ti[clave]))
    return tuple(salida)


def juicio_por_intervalo(f: FilaIntervalo) -> str:
    """
    El juicio de una fila de metal corrugado. Un CONTROL se juzga con el n
    tipico (el que la fuente da para diseñar) y se dice si cambia dentro del
    rango; una magnitud que no depende de n (los dos extremos dan lo mismo:
    la velocidad bajo control de salida, Q/A al critico) se juzga con la
    tolerancia de lectura, como las filas con n impreso; las demas, por el
    intervalo.
    """
    lectura = CP_HDS5_DG1["tolerancia_de_lectura"]
    if isinstance(f.publicado, str):
        tipico = "igual con el n típico" if f.publicado == f.con_n_tipico \
            else "DISTINTO con el n típico"
        if f.con_n_bajo == f.con_n_alto:
            return f"{tipico}; el mismo en todo el rango"
        return (f"{tipico}; cambia dentro del rango ({f.con_n_bajo} con el n "
                f"bajo, {f.con_n_alto} con el alto)")
    if abs(f.con_n_bajo - f.con_n_alto) <= abs(f.publicado) * 1e-12:
        dif = f.con_n_tipico / f.publicado - 1
        return (f"no depende de n: {dif:+.2%}, "
                + (f"≤ {lectura:.0%}" if dentro_de(dif, lectura)
                   else f"> {lectura:.0%}"))
    lo, hi = sorted((f.con_n_bajo, f.con_n_alto))
    return "sí" if lo <= f.publicado <= hi else "no"


# ---------------------------------------------------------------------------
# 2. HEC-14: los ejemplos resueltos que T-8 uso como oraculo
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EjemploHEC14:
    clave: str
    titulo: str
    paginas: str                     # impresas y del PDF, como se imprimen
    paginas_pdf: Tuple[int, ...]
    paginas_impresas: Tuple[str, ...]
    datos: str                       # las entradas, como la pagina las da
    # (magnitud, publicado, unidad, texto que la pagina imprime, extractor)
    cifras: Tuple[Tuple[str, float, str, str, Callable[[Any], float]], ...]
    calcular: Callable[[], Any]
    nota: str = ""


def _apron_si():
    return M6.apron_hec14(Q_celda=2.33, seccion=SeccionCircular(1.5), TW=0.5,
                          y_salida=None, y_critico=0.8)


def _apron_cu():
    return M6.apron_hec14(Q_celda=85 * M_POR_FT ** 3,
                          seccion=SeccionCircular(5.0 * M_POR_FT),
                          TW=1.6 * M_POR_FT, y_salida=5.0 * M_POR_FT,
                          y_critico=1.0)


def _hoya_no_cohesiva():
    material = MaterialLecho(tipo="no_cohesivo", D84_m=1.87 ** 2 * 0.001,
                             D16_m=0.001)
    return M6.hoya_de_socavacion_hec14(
        Q_celda=0.764, seccion=SeccionCircular(0.457), S=0.02, V=_V(3.0),
        altura_caida_m=0.914, material=material, duracion_pico_min=30.0)


def _hoya_cohesiva():
    return M6.hoya_de_socavacion_hec14(
        Q_celda=1.133, seccion=SeccionCircular(0.61), S=0.0, V=_V(3.88),
        altura_caida_m=0.0, duracion_pico_min=30.0,
        material=MaterialLecho(tipo="cohesivo", IP=12.0, Sv_Pa=23970.0))


def _froude():
    return M6.froude_salida(V=_V(12.192), Q_celda=8.5,
                            seccion=SeccionCircular(1.219))


EJEMPLOS_HEC14: Tuple[EjemploHEC14, ...] = (
    EjemploHEC14(
        "apron_si", "Design Example: Riprap Apron (SI)",
        "págs. impresas 10-18 y 10-19 (PDF 219 y 220)", (219, 220),
        ("10-18", "10-19"),
        "Q = 2.33 m³/s, D = 1.5 m, TW = 0.5 m (TW < 0.4D: se usa 0.6 m)",
        (("D50 de la Ec. (10.4)", 0.13, "m", "equals 0.13 meters",
          lambda a: a.D50_requerido),
         ("D50 de la clase (Tabla 10.1, clase 2)", 0.15, "m",
          "riprap class 2 (D50 = 0.15 m)", lambda a: a.D50_clase),
         ("longitud L = 4D", 6.0, "m", "L = 4D = 4(1.5) = 6 m",
          lambda a: a.longitud),
         ("profundidad 3.3·D50", 0.50, "m", "3.3 (0.15) = 0.50 m",
          lambda a: a.espesor),
         ("ancho al final 3D + (2/3)L", 8.5, "m", "(2/3)(6) = 8.5 m",
          lambda a: a.ancho_final)),
        _apron_si,
        "La profundidad sale −1.00 %, sobre la frontera del 1 %: es redondeo "
        "de la fuente, que imprime «3.3 (0.15) = 0.50 m» cuando 3.3 × 0.15 "
        "= 0.495 m; el motor da 0.495 m (T-8 lo fija con la fórmula, no con "
        "la cifra impresa)."),
    EjemploHEC14(
        "apron_cu", "Design Example: Riprap Apron (CU), a su escala real",
        "pág. impresa 10-19 (PDF 220)", (220,), ("10-19",),
        "Q = 85 ft³/s, D = 5.0 ft = 60 in, TW = 1.6 ft (se usa 2.0 ft)",
        (("D50 de la Ec. (10.4)", 0.43, "ft", "equals 0.43 feet",
          lambda a: a.D50_requerido / M_POR_FT),
         ("longitud L = 4D", 20.0, "ft", "L = 4D = 4(5) = 20 ft",
          lambda a: a.longitud / M_POR_FT),
         ("ancho al final 3D + (2/3)L", 28.3, "ft", "(2/3)(20) = 28.3 ft",
          lambda a: a.ancho_final / M_POR_FT)),
        _apron_cu,
        "D = 60 in es el límite de la nota 8 de la Tabla 1.1 que rige desde "
        "las correcciones de T-8 (`HEC14_APRON_ALTURA_MAX_M`); el ejemplo "
        "entra a su escala, sin la λ = 0.9 que T-8 había usado."),
    EjemploHEC14(
        "hoya_no_cohesiva",
        "Design Example: Estimating Scour Hole Geometry in a Cohesionless "
        "Soil (SI)",
        "págs. impresas 5-4 y 5-5 (PDF 57 y 58)", (57, 58), ("5-4", "5-5"),
        "D = 457 mm, S = 2 %, caída 0.914 m (Hd = 2), Q = 0.764 m³/s, "
        "σ = 1.87, t = 30 min",
        (("profundidad hs (Ec. 5.1)", 1.14, "m", "equals 1.14 meter",
          lambda h: h.profundidad),
         ("ancho Ws", 8.82, "m", "equals 8.82 meters", lambda h: h.ancho),
         ("longitud Ls", 7.06, "m", "equals 7.06 meters",
          lambda h: h.longitud),
         ("distancia al máximo 0.4·Ls", 2.82, "m", "= 2.82 m",
          lambda h: h.distancia_al_maximo)),
        _hoya_no_cohesiva,
        "La velocidad no entra en la Ec. (5.1); el test le da 3.0 m/s y no "
        "influye. El D84/D16 se elige para σ = 1.87."),
    EjemploHEC14(
        "hoya_cohesiva",
        "Design Example: Estimating Scour Hole Geometry in a Cohesive Soil "
        "(SI)",
        "págs. impresas 5-8 y 5-9 (PDF 61 y 62)", (61, 62), ("5-8", "5-9"),
        "D = 610 mm, S = 0, sin caída, Q = 1.133 m³/s, PI = 12, "
        "Sv = 23 970 N/m², V = 3.88 m/s, t = 30 min",
        (("τc (Ec. 5.4)", 39.9, "N/m²", "= 39.9 N/m2",
          lambda _h: M6.tension_tractiva_critica(Sv_Pa=23970.0, IP=12.0)),
         ("profundidad hs (Ec. 5.2)", 1.2, "m", "= 1.2 m",
          lambda h: h.profundidad),
         ("ancho Ws", 5.02, "m", "= 5.02 m", lambda h: h.ancho),
         ("longitud Ls", 9.81, "m", "= 9.81 m", lambda h: h.longitud)),
        _hoya_cohesiva,
        "La fuente escribe (0.09)^θ por (30/316)^θ = (0.0949)^θ: de ahí el "
        "medio por ciento de Ws y Ls (ficha de T-8)."),
    EjemploHEC14(
        "froude_usbr_vi",
        "Design Example: USBR Type VI Impact Basin (SI), pasos 1 y 2",
        "pág. impresa 9-40 (PDF 197)", (197,), ("9-40",),
        "D = 1.219 m, Q = 8.5 m³/s, Vo = 12.192 m/s",
        (("área A = Q/Vo", 0.697, "m²", "= 0.697 m2", lambda f: f.A),
         ("tirante equivalente ye = (A/2)^0.5", 0.590, "m", "= 0.590 m",
          lambda f: f.y_equivalente),
         ("Froude Fr = Vo/(g·ye)^0.5", 5.07, "—", "= 5.07", lambda f: f.Fr)),
        _froude),
)


# Las cifras publicadas que el motor no reproduce dentro de la tolerancia,
# con la causa MEDIDA (como `CP_HDS5_DG1["fuera_de_tolerancia"]`): no se
# ajusta ni el motor ni la tolerancia para vaciar el censo, y el test exige
# que cada censada este de verdad fuera.
#
# VACIO DESDE LAS CORRECCIONES DE T-11 (H12): la unica entrada, «profundidad
# 3.3·D50» del apron SI, estaba fuera del 1 % por 1e-17 --0.495 / 0.50 - 1
# es el -1 % EXACTO en decimal--, una comparacion de floats sin tolerancia.
# Con `TOL_FRONTERA_DE_BANDA` cae dentro; el redondeo de la fuente que la
# explicaba queda en la nota del ejemplo.
CENSO_HEC14: Dict[Tuple[str, str], str] = {}


@dataclass(frozen=True)
class FilaHEC14:
    ejemplo: str
    magnitud: str
    publicado: float
    unidad: str
    calculado: float

    @property
    def diferencia(self) -> float:
        return self.calculado / self.publicado - 1

    @property
    def censada(self) -> str:
        return CENSO_HEC14.get((self.ejemplo, self.magnitud), "")


def filas_hec14() -> Tuple[FilaHEC14, ...]:
    salida = []
    for ej in EJEMPLOS_HEC14:
        resultado = ej.calcular()
        for magnitud, publicado, unidad, _texto, extraer in ej.cifras:
            salida.append(FilaHEC14(ej.clave, magnitud, publicado, unidad,
                                    float(extraer(resultado))))
    return tuple(salida)


# ---------------------------------------------------------------------------
# El documento
# ---------------------------------------------------------------------------

def _celda(texto: Any) -> str:
    return " ".join(str(texto).split()).replace("|", "\\|")


def _num(x: Any) -> str:
    if isinstance(x, str):
        return x
    return f"{x:.3f}"


def _pct(x: Optional[float]) -> str:
    """Con DOS decimales (H12 de la auditoria de T-11: con uno, −3.05 % se
    imprimia «−3.0 %» al lado de un veredicto «fuera del 3 %»)."""
    return "—" if x is None else f"{x:+.2%}"


def generar() -> str:
    L: List[str] = []
    A = L.append
    lectura = CP_HDS5_DG1["tolerancia_de_lectura"]
    fuente = CP_HDS5_DG1["tolerancia_de_la_fuente"]
    A("# Validación externa: el motor contra los ejemplos resueltos de HDS-5 y HEC-14 (T-11)")
    A("")
    A("> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe "
      "`python -m tests.apoyo.validacion_externa --escribir` y "
      "`tests/test_t11_validacion_externa.py` lo regenera y lo compara. Los "
      "casos son los que T-2 y T-8 transcribieron y verificaron contra su "
      "página; la cuenta es la del motor (M3, M4 y M6), con las mismas "
      "llamadas que sus tests. HY-8 no está en el entorno: su procedimiento "
      "está en `docs/validacion_hy8.md`, sin ningún resultado.")
    A("")
    A("## 1. HDS-5, Design Guideline 1 (formularios de los ejemplos)")
    A("")
    A(f"Fuente: {CP_HDS5_DG1['fuente']}. Caso patrón "
      "`tests/fixtures/casos_patron.py::CP_HDS5_DG1`; comparación "
      "`tests/test_t2_hidraulica.py::_calcular_fila`.")
    A("")
    A(f"- **Tolerancia de lectura: {lectura:.0%}.** Las cifras del formulario "
      "salen de leer nomogramas; lo que cae fuera lo censa el caso patrón con "
      "su causa, medida, y no se ajusta ni el motor ni la tolerancia.")
    A(f"- **Tolerancia de la fuente: ±{fuente:.0%}**, «"
      f"{CP_HDS5_DG1['frase_tolerancia_de_la_fuente']}» (HDS-5, PDF "
      f"{CP_HDS5_DG1['pagina_pdf_tolerancia_de_la_fuente']}).")
    A("- La diferencia es (motor / publicado − 1); en `EL_ho_ft` se toma sobre "
      "la altura H + h_o y no sobre la cota, para que el 100 de la cota no la "
      "esconda.")
    A("")
    filas = filas_hds5()
    tabla = []
    for f in filas:
        if f.diferencia is None:
            veredicto = "igual" if f.publicado == f.calculado else "DISTINTO"
        elif dentro_de(f.diferencia, lectura):
            veredicto = f"≤ {lectura:.0%}"
        elif dentro_de(f.diferencia, fuente):
            veredicto = f"≤ {fuente:.0%} (fuera de la lectura)"
        else:
            veredicto = f"> {fuente:.0%}"
        tabla.append((f.grupo, f"`{f.fila}`", f"`{f.magnitud}`",
                      UNIDAD.get(f.magnitud, ""), _num(f.publicado),
                      _num(f.calculado), _pct(f.diferencia), veredicto,
                      f.censada or "—"))
    A("| Ejemplo | Fila | Magnitud | Unidad | Publicado | Motor | Diferencia "
      "| Veredicto | Causa censada (si sale del 3 %) |")
    A("|---|---|---|---|---|---|---|---|---|")
    for t in tabla:
        A("| " + " | ".join(_celda(c) for c in t) + " |")
    A("")
    dentro = sum(1 for f in filas if f.diferencia is not None
                 and dentro_de(f.diferencia, lectura))
    con_dif = sum(1 for f in filas if f.diferencia is not None)
    controles = [f for f in filas if f.diferencia is None]
    A(f"Resumen: **{dentro} de {con_dif}** cifras dentro del {lectura:.0%} de "
      f"lectura; las {con_dif - dentro} restantes son las censadas con su "
      f"causa; **{sum(1 for f in controles if f.publicado == f.calculado)} de "
      f"{len(controles)}** controles gobernantes iguales al publicado.")
    A("")
    A("### 1.1 Las dos filas de metal corrugado: el n que la fuente acota")
    A("")
    rango = CP_HDS5_DG1["circular"]["n_interpretado"]["rango"]
    tipico = CP_HDS5_DG1["circular"]["n_interpretado"]["tipico"]
    A(f"El formulario no imprime el n del metal corrugado. La fuente lo acota "
      f"en la Tabla B.1 ({rango[0]}–{rango[1]}, pág. impresa B.6, PDF "
      f"{CP_HDS5_DG1['circular']['n_interpretado']['pagina_pdf_rango']}) y da "
      f"{tipico} como típico (pág. impresa 3.8, PDF "
      f"{CP_HDS5_DG1['circular']['n_interpretado']['pagina_pdf_tipico']}). No "
      "se compara contra una cifra al 3 %: lo publicado tiene que caer en el "
      "intervalo que da el motor con los dos extremos del rango.")
    A("")
    A("| Fila | Magnitud | Publicado | Motor, n bajo | Motor, n alto | "
      "Motor, n típico | ¿Dentro del intervalo? |")
    A("|---|---|---|---|---|---|---|")
    for f in filas_por_intervalo():
        dentro_iv = juicio_por_intervalo(f)
        A("| " + " | ".join(_celda(c) for c in (
            f"`{f.fila}`", f"`{f.magnitud}`", _num(f.publicado),
            _num(f.con_n_bajo), _num(f.con_n_alto), _num(f.con_n_tipico),
            dentro_iv)) + " |")
    A("")
    A("Con el control de **salida** gobernando, la velocidad de salida no "
      "depende de n: es Q/A al tirante crítico (TW bajo el crítico), y es la "
      "que se compara.")
    A("")
    A("### 1.2 Lo que este ejemplo no valida")
    A("")
    q_lo, q_hi = CP_HDS5_DG1["q_estrella_transicion"]
    A(f"- Ninguna de las siete filas cae en la transición {q_lo} < q* < {q_hi} "
      "del control de entrada: el ejemplo valida la rama no sumergida y la "
      "sumergida, no la recta de transición, que sigue sostenida sólo por "
      "los casos patrón internos (ficha T2-05).")
    A("- No hay ejemplo publicado del perfil de la lámina de agua (E-A), de "
      "V8 a presión, de la Fase 8 ni del cabezal: esos se sostienen con "
      "dorados calculados a mano en sus casos patrón.")
    A("")
    A("## 2. HEC-14: los ejemplos resueltos que T-8 usó como oráculo")
    A("")
    A(f"Tolerancia: {TOLERANCIA_EJEMPLO_IMPRESO:.0%} (la de T-8 para un "
      "ejemplo impreso: la fuente imprime dos o tres cifras y redondea los "
      "intermedios). Cada cifra publicada está **verificada en su página** "
      "por `tests/test_t11_validacion_externa.py` (marca `pdf`, con "
      "`NORMAS_DIR`: HEC-14 vive sólo en el repositorio de normas), que "
      "busca en el texto de la página la frase de la última columna.")
    A("")
    resultados = {f"{f.ejemplo}|{f.magnitud}": f for f in filas_hec14()}
    for ej in EJEMPLOS_HEC14:
        A(f"### {ej.titulo}")
        A("")
        A(f"HEC-14, {ej.paginas}. Datos: {ej.datos}.")
        A("")
        A("| Magnitud | Unidad | Publicado | Motor | Diferencia | Veredicto "
          "| Texto en la página |")
        A("|---|---|---|---|---|---|---|")
        for magnitud, publicado, unidad, texto, _x in ej.cifras:
            f = resultados[f"{ej.clave}|{magnitud}"]
            veredicto = (f"≤ {TOLERANCIA_EJEMPLO_IMPRESO:.0%}"
                         if dentro_de(f.diferencia, TOLERANCIA_EJEMPLO_IMPRESO)
                         else f"> {TOLERANCIA_EJEMPLO_IMPRESO:.0%}, censada: "
                         + f.censada if f.censada
                         else f"> {TOLERANCIA_EJEMPLO_IMPRESO:.0%} SIN CENSAR")
            A("| " + " | ".join(_celda(c) for c in (
                magnitud, unidad, _num(publicado), _num(f.calculado),
                _pct(f.diferencia), veredicto, f"«{texto}»")) + " |")
        A("")
        if ej.nota:
            A(ej.nota)
            A("")
    return "\n".join(L) + "\n"


# ===========================================================================
# 3. HY-8: el procedimiento para que el autor lo corra (sin resultados)
# ===========================================================================
# El documento lo escribe este modulo para que la TABLA de entradas y de
# salidas a comparar salga de la corrida del juego de la validacion integral
# y no de una transcripcion a mano: si el programa cambia un HW, el documento
# cambia con el y el test de sincronia lo dice. El procedimiento es texto fijo.
# Ninguna cifra de HY-8 se escribe: HY-8 no esta en el entorno.

DOCUMENTO_HY8 = RAIZ / "docs" / "validacion_hy8.md"

# LA TOLERANCIA DE LA COMPARACION CON HY-8: CRITERIO DEL PROYECTO, NO
# NORMATIVO. T-11 la propuso y el dueño la ACEPTO el 2026-11-13 (18:25 UTC,
# `ORQ/DECISIONES_DUENO_2026-11-12.md`, «Decisiones del dueño sobre las dos
# preguntas abiertas de T-11»): hasta el 3 % coincide --la tolerancia de
# LECTURA con que se juzgan los ejemplos publicados del HDS-5 en
# `docs/validacion_hds5.md`--; del 3 % al 10 % se EXPLICA con su causa; mas
# del 10 % --el ±10 % que el HDS-5 declara para su propio procedimiento,
# pag. impresa 3.1, PDF 83-- es una DISCREPANCIA que se investiga. Se aplica
# a HW y a HW/D; si el control gobernante no coincide, el punto va a
# «explicar» sea cual sea el porcentaje; la velocidad de salida va sin
# veredicto donde el programa no la saca del mismo modo que HY-8. Ninguna
# norma fija estas cifras: no son [N] ni viven en `constantes_normativas`.
TOLERANCIA_HY8_EXPLICAR = CP_HDS5_DG1["tolerancia_de_lectura"]
TOLERANCIA_HY8_DISCREPANCIA = CP_HDS5_DG1["tolerancia_de_la_fuente"]

JUICIO_COINCIDE = "coincide"
JUICIO_EXPLICAR = "explicar"
JUICIO_DISCREPANCIA = "discrepancia"


def juicio_hy8(programa: float, hy8: float, *, control_programa: str,
               control_hy8: str) -> str:
    """
    El juicio de UNA magnitud (HW o HW/D) del programa frente a HY-8, con la
    regla que el dueño acepto. La diferencia se mide contra el programa:
    hy8 / programa - 1. Control distinto: «explicar», sea cual sea el
    porcentaje (la carga sale de otra ecuacion).
    """
    if control_programa != control_hy8:
        return JUICIO_EXPLICAR
    d = hy8 / programa - 1
    if dentro_de(d, TOLERANCIA_HY8_EXPLICAR):
        return JUICIO_COINCIDE
    if dentro_de(d, TOLERANCIA_HY8_DISCREPANCIA):
        return JUICIO_EXPLICAR
    return JUICIO_DISCREPANCIA


def _fila_de_carta(hds5) -> str:
    """La fila de la Tabla A.1 del HDS-5 cuyas constantes usa el punto."""
    from src.normativa import registro as _registro
    tabla = _registro.construir().tabla("HDS5_3ED.TA1")
    for f in tabla.filas:
        v = f.valores
        if (v["K"], v["M"], v["c"], v["Y"], v["equation_form"]) == \
                (hds5.K, hds5.M, hds5.c, hds5.Y, hds5.forma):
            return (f"Chart {v['chart_no']}, scale {v['nomograph_scale']}: "
                    f"{v['shape_and_material']}, {v['inlet_configuration']} "
                    f"(`{tabla.clave_corta(f)}`; K {v['K']}, M {v['M']}, "
                    f"c {v['c']}, Y {v['Y']}, Forma {v['equation_form']})")
    return "SIN FILA en la Tabla A.1 (revisar)"


def filas_hy8(informe: Any) -> Tuple[Dict[str, Any], ...]:
    """Lo que el autor tiene que llenar en HY-8 y lo que tiene que comparar."""
    salida = []
    for p in informe.puntos:
        r = p.resultado
        if r is None or not p.dimensionado:
            continue
        rh = r.resultado_hidraulico
        salida.append({
            "id": p.punto.id, "familia": p.punto.familia.value,
            "seccion": r.seccion.etiqueta(), "material": r.material.nombre,
            # La ALTURA interior del conducto: el D del tubo o la altura de
            # la celda del marco. Es el divisor de HW/D (decision del dueño).
            "altura": r.seccion.altura,
            "n_min": r.material.n_min, "n_max": r.material.n_max,
            "n_perfil": rh.perfil.n if rh.perfil is not None else None,
            "carta": _fila_de_carta(r.material.hds5),
            "ke": rh.perfil.ke if rh.perfil is not None else None,
            "celdas": rh.numero_celdas, "Q": rh.Q, "S": rh.S,
            "TW": rh.TW_m,
            # Roadway Data de HY-8: la cota de la cresta es la rasante del
            # punto (columna `cota_rasante` del CSV) y el ancho de la
            # plataforma es el «top width».
            "cota_rasante": p.punto.cota_rasante,
            "ancho_plataforma": p.punto.ancho_plataforma,
        })
    return tuple(salida)


def diferencia_de_longitud_horizontal(S: float) -> float:
    """
    Cuanto mas corta es la proyeccion horizontal que la longitud sobre el
    eje del barril, en fraccion: 1 - 1/sqrt(1 + S^2) (≈ S^2/2). Con S = 0.006
    es 0.0018 %; con 0.010, 0.0050 % (H5 de la auditoria de T-11: el
    documento decia «≤ 0.002 %» para todos).
    """
    return 1 - 1 / (1 + S * S) ** 0.5


def velocidad_hy8(d: Dict[str, Any]) -> Tuple[str, str]:
    """
    Como sale la velocidad de salida del programa y si lleva veredicto frente
    a HY-8 (decision del dueño del 2026-11-13: SIN veredicto donde el
    programa no la saca del mismo modo que HY-8).
    """
    if d["control_gobernante"] == "entrada":
        return ("control de entrada: V_erosión = (1/n_mín)·R^(2/3)·S^(1/2) "
                "sobre el tirante normal de n_máx (regla de doble n de la v8 "
                "§4.1, `M3.resolver_manning`; V·A ≠ Q por diseño), la "
                "estimación alta para V3 y el d50. No es la velocidad de un "
                "perfil: HY-8 la saca del perfil supercrítico del barril",
                "no")
    return ("control de salida: Q/A en la sección de salida con el tirante "
            "y_salida = " + f"{d['y_salida_m']:.3f}" + " m (HDS-5 3.1.6; el "
            "perfil de la lámina arranca ahí), sin n: la misma magnitud que "
            "HY-8 da en la salida", "sí")


def generar_hy8(informe: Any) -> str:
    from tests.apoyo import validacion_integral as V
    volcado = {p["id"]: p for p in V.volcado(informe)["puntos"]}
    explicar = f"{TOLERANCIA_HY8_EXPLICAR:.0%}"
    discrepancia = f"{TOLERANCIA_HY8_DISCREPANCIA:.0%}"
    L: List[str] = []
    A = L.append
    A("# Validación con HY-8: procedimiento para que el autor lo corra (T-11)")
    A("")
    A("> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe "
      "`python -m tests.apoyo.validacion_externa --escribir` y "
      "`tests/test_t11_validacion_externa.py` lo regenera y lo compara. "
      "**HY-8 no está en el entorno de la cadena T y este documento NO "
      "afirma ningún resultado de HY-8**: dice qué entradas de cada punto "
      "hay que cargar, qué salida comparar y con qué tolerancia. Las "
      "entradas son las de la corrida del juego de la validación integral, "
      "que son **DATOS DE PRUEBA, NO DEL PROYECTO** "
      "(`tests/fixtures/juego_validacion_integral.py`).")
    A("")
    A("## 1. Qué se valida y qué no")
    A("")
    A("HY-8 es el programa de la FHWA para el análisis hidráulico de "
      "alcantarillas, que implementa los procedimientos del HDS-5. La "
      "comparación valida la **hidráulica del conducto** de cada punto "
      "dimensionado: la carga a la entrada con control de entrada, la carga "
      "con control de salida, cuál gobierna, HW/D, los tirantes normal y "
      "crítico, y la velocidad a la salida donde los dos programas la sacan "
      "del mismo modo (§5, regla 4). No valida nada de lo que HY-8 no "
      "calcula: la clasificación, el TR, la Fase 8, el cabezal, la "
      "protección, la Fase 10, ni las verificaciones V1 a V10 como "
      "veredictos.")
    A("")
    A("## 2. Las convenciones del programa que hay que reproducir")
    A("")
    A("- **Doble n (hoja de ruta §4.1).** El programa calcula la carga, los "
      "tirantes y el control con el n **máximo** del material (la "
      "estimación alta de la pérdida). En HY-8 cada barril se corre con el n "
      "que se le carga: la corrida que se compara con veredicto es la de "
      "**n máximo** (el «Tirante normal» de §4 está calculado con él). La "
      "velocidad de erosión del programa usa el n **mínimo** sobre ese "
      "mismo tirante (§5, regla 4): una segunda corrida de HY-8 con n "
      "mínimo es opcional e informativa.")
    A("- **El TW es un tirante sobre el fondo de la salida**, no una cota: en "
      "HY-8 se carga como cota de agua constante del receptor = cota de "
      "salida + TW.")
    A("- **El cabezal es normal al eje del conducto** (alcance declarado): no "
      "se declara esviaje de la embocadura en HY-8; el esviaje del cruce ya "
      "está en la longitud del conducto.")
    A("- **Longitud.** El programa calcula la longitud por extremo (7.B) "
      "sobre el eje del barril; la proyección horizontal es más corta en "
      "1 − 1/√(1 + S²) ≈ S²/2, que §3 da por punto (del orden de "
      "milésimas de por ciento). Cargar en HY-8 la estación de salida igual "
      "a la longitud y las dos cotas de fondo de la tabla.")
    A("- **Roadway Data.** HY-8 la exige: perfil de cota constante, **cota "
      "de la cresta = la rasante del punto** y **ancho = el de la "
      "plataforma** (§3); la longitud de la cresta es la del tramo de vía "
      "sobre el cauce, que no es dato del programa (cualquiera vale si no "
      "hay desborde). Con los caudales de diseño **no debe haber desborde** "
      "(en el programa V5 y V8 lo exigen); si HY-8 reporta caudal sobre la "
      "vía, la corrida no es comparable y se dice.")
    A("")
    A("## 3. Entradas por punto (corrida del juego, `--alcance expediente`)")
    A("")
    A("| Punto | Fam. | Sección | Material | n mín. / máx. | Embocadura "
      "(HDS-5 Tabla A.1) | ke | Barriles | Q (m³/s) | Longitud (m) y su "
      "diferencia con la horizontal | Pendiente (m/m) | Cota de fondo "
      "entrada / salida (msnm) | TW (m) y cota del receptor (msnm) | Roadway "
      "Data: cota de cresta (msnm) / ancho (m) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in filas_hy8(informe):
        g = volcado[f["id"]]["geometria"]
        ce, cs = g["cota_entrada_msnm"], g["cota_salida_msnm"]
        A("| " + " | ".join(_celda(c) for c in (
            f["id"], f["familia"], f["seccion"], f["material"],
            f"{f['n_min']} / {f['n_max']}", f["carta"], f["ke"], f["celdas"],
            f"{f['Q']:.3f}",
            f"{g['longitud_m']:.3f} "
            f"({diferencia_de_longitud_horizontal(f['S']):.4%})",
            f"{f['S']:.4f}",
            f"{ce:.3f} / {cs:.3f}", f"{f['TW']:.3f} → {cs + f['TW']:.3f}",
            f"{f['cota_rasante']:.3f} / {f['ancho_plataforma']:.2f}"))
          + " |")
    A("")
    A("## 4. Salidas del programa que hay que comparar")
    A("")
    A("Las cargas son alturas sobre el fondo de la entrada (HW), en metros. "
      "En HY-8, «headwater elevation» menos la cota de fondo de la entrada. "
      "HW/D es la carga entre la ALTURA interior del conducto: el D del tubo "
      "o la altura de la celda del marco. El tirante normal es el de **n "
      "máximo**.")
    A("")
    A("| Punto | Altura D (m) | HW control de entrada (m) · HW/D | HW control "
      "de salida (m) · HW/D | HW que gobierna (m) · HW/D | Control | "
      "Tirante normal, n máx. (m) | Tirante crítico (m) | Velocidad a la "
      "salida (m/s) | Cómo sale la velocidad | ¿Lleva veredicto? | Régimen "
      "del barril |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in filas_hy8(informe):
        d = volcado[f["id"]]["diseno"]
        D = f["altura"]
        yn = d.get("y_normal_m")
        if d.get("HW_salida_m") is None:
            # H9 de la auditoria (decision del dueño): donde el perfil
            # sustituye a la aproximacion y no alcanza la entrada, el control
            # de salida no se forma y el JSON lleva `null`; la aproximacion
            # descartada sigue en `perfil_HW_aproximado_m`.
            hw_salida = (f"no se forma: el perfil {d.get('perfil_tipo')} no "
                         "alcanza la entrada (la aproximación descartada da "
                         f"{d['perfil_HW_aproximado_m']:.3f})")
        elif d.get("perfil_sustituye_aproximacion"):
            hw_salida = (f"{d['HW_salida_m']:.3f} (remanso, perfil "
                         f"{d.get('perfil_tipo')}) · "
                         f"{d['HW_salida_m'] / D:.3f}")
        else:
            hw_salida = f"{d['HW_salida_m']:.3f} · {d['HW_salida_m'] / D:.3f}"
        como, veredicto = velocidad_hy8(d)
        A("| " + " | ".join(_celda(c) for c in (
            f["id"], f"{D:.3f}",
            f"{d['HW_entrada_m']:.3f} · {d['HW_entrada_m'] / D:.3f}",
            hw_salida,
            f"{d['HW_gobernante_m']:.3f} · {d['HW_gobernante_m'] / D:.3f}",
            d["control_gobernante"],
            "—" if yn is None else f"{yn:.3f}", f"{d['y_critico_m']:.3f}",
            f"{d['V_salida_m_s']:.3f}", como, veredicto,
            d["regimen_barril"])) + " |")
    A("")
    A("## 5. Tolerancia de la comparación: criterio del proyecto, NO "
      "normativo (aceptado por el dueño el 2026-11-13)")
    A("")
    A("Ninguna norma fija estas cifras. Son un **criterio del proyecto**, "
      "propuesto por T-11 y aceptado por el dueño, coherente con la "
      f"tolerancia de lectura del {explicar} con que se juzgan los ejemplos "
      "publicados del HDS-5 (`docs/validacion_hds5.md`). La diferencia se "
      "mide contra el programa (HY-8 / programa − 1), con dos decimales.")
    A("")
    A(f"1. **Hasta {explicar}**: coincidencia. Entre {explicar} y "
      f"{discrepancia}: diferencia que hay que **explicar** con su causa "
      "antes de darla por buena (la forma de la ecuación de control de "
      "entrada, la regla del HDS-5 núm. 3.3.3 para la carga de salida entre "
      "0.75 D y 1.2 D, el perfil de la lámina, la entrada sumergida o no). "
      f"**Más de {discrepancia}** —el ±10 % en carga que el HDS-5 declara "
      "para su propio procedimiento, pág. impresa 3.1, PDF "
      f"{CP_HDS5_DG1['pagina_pdf_tolerancia_de_la_fuente']}—: "
      "**discrepancia** que se investiga y se reporta contra el programa "
      "con el caso.")
    A("2. La regla se aplica a **HW y a HW/D** (las dos columnas de §4).")
    A("3. Si el **tipo de control** (entrada o salida) de HY-8 no es el del "
      "programa, el punto va a **«explicar» sea cual sea el porcentaje**: "
      "las cargas salen de ecuaciones distintas.")
    A("4. La **velocidad de salida** se informa **sin veredicto** donde el "
      "programa no la saca del mismo modo que HY-8 (columna «¿Lleva "
      "veredicto?» de §4): bajo control de entrada el programa da la "
      "estimación alta de la regla de doble n y HY-8 la del perfil del "
      "barril. Donde sí lleva veredicto (control de salida, sección de "
      "salida con el mismo tirante) se juzga con las bandas de la regla 1, "
      "por la misma razón que HW: lectura de T-11 sobre la decisión del "
      "dueño, que nombra HW y HW/D.")
    A("5. La **versión de HY-8** y la **fecha de la corrida** son campo "
      "obligatorio del encabezado de cada tabla de §6: sin ellas la tabla no "
      "vale.")
    A("")
    A("## 6. Cómo dejar escrito el resultado")
    A("")
    A("Una tabla por punto, con este encabezado y estas filas; las columnas "
      "de HY-8, la diferencia y el juicio las llena el autor. Si un número "
      "del programa cambia, este documento cambia con él: la comparación "
      "vale para el commit cuyo sello lleve.")
    A("")
    for f in filas_hy8(informe):
        d = volcado[f["id"]]["diseno"]
        D = f["altura"]
        A(f"### {f['id']} — versión de HY-8: ______ · fecha de la corrida: "
          "______ (obligatorios)")
        A("")
        A("| Magnitud | Programa | HY-8 | Diferencia (%) | Juicio (§5) |")
        A("|---|---|---|---|---|")
        filas = [("HW que gobierna (m)", f"{d['HW_gobernante_m']:.3f}"),
                 ("HW/D que gobierna", f"{d['HW_gobernante_m'] / D:.3f}"),
                 ("Control", d["control_gobernante"]),
                 ("HW control de entrada (m)", f"{d['HW_entrada_m']:.3f}"),
                 ("HW control de salida (m)",
                  "no se forma" if d.get("HW_salida_m") is None
                  else f"{d['HW_salida_m']:.3f}")]
        _como, veredicto = velocidad_hy8(d)
        filas.append((f"Velocidad a la salida (m/s){'' if veredicto == 'sí' else ' — sin veredicto'}",
                      f"{d['V_salida_m_s']:.3f}"))
        for magnitud, valor in filas:
            A(f"| {magnitud} | {valor} | | | |")
        A("")
    return "\n".join(L) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    texto = generar()
    if "--escribir" in args:
        from tests.apoyo import validacion_integral as V
        DOCUMENTO.write_text(texto, encoding="utf-8")
        print(f"escrito {DOCUMENTO}")
        DOCUMENTO_HY8.write_text(generar_hy8(V.correr_juego()),
                                 encoding="utf-8")
        print(f"escrito {DOCUMENTO_HY8}")
    else:
        sys.stdout.write(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
