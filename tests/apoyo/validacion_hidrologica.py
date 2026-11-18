"""
tests/apoyo/validacion_hidrologica.py
=====================================
La VALIDACION HIDROLOGICA de `src/modulos/MH_hidrologia.py` (Fase 1-bis)
contra seis CASOS REALES PUBLICADOS, generada en
`docs/validacion_hidrologica.md`. `tests/test_validacion_hidrologica.py` lo
regenera a memoria y lo compara, de modo que el documento no se puede
desincronizar del programa sin que la suite lo diga.

Regenerar::

    python -m tests.apoyo.validacion_hidrologica --escribir

DE DONDE SALE
-------------
El material es de una verificacion INDEPENDIENTE (dossier
`proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/hidrologia/
hidrologia_casos_reales.md`, 2026-11-18): el verificador transcribio los
seis documentos con su pagina, hizo el calculo a mano sin importar `src/`,
lo congelo con sha1 ANTES de correr el programa y despues comparo. Aqui no
se repite su calculo a mano: se toman

  * las ENTRADAS, en `tests/fixtures/hidrologia_casos_reales/<caso>/`
    (rotuladas «DATOS DE CASO REAL PUBLICADO — no son datos de este
    proyecto»; lo que el documento no publica va rotulado como vehiculo o
    declaracion del verificador);
  * los NUMEROS PUBLICADOS, transcritos abajo con documento, pagina y tabla
    (los del dossier, contrastados contra la capa de texto de cada PDF del
    repositorio de normas, `ejemplos_resueltos/casos_reales/`);
  * las TOLERANCIAS del dossier, nombradas (`TOLERANCIAS`), cada una con su
    razon;
  * para los caudales, que ningun documento calcula como MH, el resultado
    del calculo a mano del verificador (`salida_esperada.json` de cada caso,
    sellado), con la tolerancia de la misma aritmetica.

QUE SE COMPARA
--------------
Por cada pieza: lo PUBLICADO por un tercero y lo que da el PROGRAMA con las
entradas del caso, la diferencia y la tolerancia. El juicio es uno de
cuatro: COINCIDE; DIFIERE POR METODO (declarado: el documento usa otro
metodo y se dice cual); EL PROGRAMA SE DETIENE (declarado y esperado: es el
caso adversarial); y DEFECTO (ninguno de los anteriores: la suite exige
cero).

Lo que este modulo NO hace: no lee ningun PDF (las cifras estan transcritas),
no corrige el programa ni la tolerancia para que un contraste pase, y no
valida el caudal de punta a punta contra ningun tercero, porque ninguno de
los seis lo calcula con el metodo de MH.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from src import criterios_adoptados as ca
from src.dominios import METROS_POR_KM, MINUTOS_POR_HORA
from src.modelos import ErrorProyecto
from src.modulos import MH_hidrologia as MH
from tests.apoyo.criterios import declarados, sin_valor

RAIZ = Path(__file__).resolve().parents[2]
DOCUMENTO = RAIZ / "docs" / "validacion_hidrologica.md"
CASOS = RAIZ / "tests" / "fixtures" / "hidrologia_casos_reales"
DOSSIER = ("proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/"
           "hidrologia/hidrologia_casos_reales.md")

INDECI = "INDECI Piura"
TUMBES = "UNTumbes TU-107"
UNSAAC = "UNSAAC Roquepata"
UPAO = "UPAO La Jalca"
UPEU = "UPeU Colpahuayco"
ESPOL = "ESPOL Intervalles"

FEN = MH.CRITERIO_FEN
DIST = MH.CRITERIO_DISTRIBUCION
COMPLETA = MH.FEN_SERIE_COMPLETA
LN, NORMAL, GUMBEL = "lognormal_2p", "normal", "gumbel"

# ===========================================================================
# Los seis documentos y su clasificacion (dossier §0 y §1.3)
# ===========================================================================

ORACULO = "oráculo numérico de piezas"
CONTRASTE = "contraste de método"
ADVERSARIAL = "adversarial (y oráculo de la estadística)"
DESCARTABLE = "descartable para el caudal; contraste de método del K-S"


@dataclass(frozen=True)
class Caso:
    nombre: str
    carpeta: str
    documento: str
    clasificacion: str
    razon: str
    no_valida: str


CASOS_REALES: Tuple[Caso, ...] = (
    Caso(INDECI, "indeci_piura",
         "INDECI-OEA, «Mapa de peligros de la ciudad de Piura», jun. 2009, "
         "Vol. I (`mapa_peligros_vol1.pdf`; impresa = PDF − 16) y Vol. II "
         "anexos (`mapa_peligros_vol2_anexos.pdf`; se cita la página del "
         "PDF). Estación Miraflores 1971-2008",
         ORACULO,
         "publica la P24(TR) de Normal, Log Normal y Gumbel por momentos (su "
         "«Gumbel modificado») con y sin años FEN, y el Δ de K-S calculado "
         "con la misma ecuación (13) del Manual. Es el mejor caso del "
         "conjunto, y el único que nombra sus años FEN",
         "el caudal: no publica longitud ni pendiente de ninguna cuenca, y "
         "su intensidad es P24/6 h"),
    Caso(TUMBES, "untumbes_tu107",
         "Ramos Estrada, tesis UNTumbes, 2025, carretera Bocapán–Tamarindo "
         "(`tesis.pdf`; impresa = PDF). Estación Cañaveral, 40 años",
         ADVERSARIAL,
         "su estadística (media, s, Δ de Normal, LN2 y Gumbel, P24 LN2) y "
         "los 41 Témez reproducen a la cifra impresa, pero la serie no es "
         "creíble: filas mensuales copiadas entre años, lluvias de 24 h de "
         "hasta 729 mm, sin años FEN declarados. Lo que vale es qué hace el "
         "programa con esa entrada",
         "el caudal: IDF propia ajustada a la Tabla N.º 04 y extrapolada a "
         "minutos, y hidrograma triangular sobre 10 km²; la serie misma es "
         "inverosímil"),
    Caso(UNSAAC, "unsaac_42tmc",
         "Bermejo Colque y Cruz Huamán, tesis UNSAAC, 2019, camino vecinal "
         "Emp. CU112–Roquepata (`tesis.pdf`; impresa = PDF − 12). Estación "
         "Colquepata 1990-2014",
         ORACULO,
         "Gumbel por momentos (10 TR), Dick-Peschke (48 celdas) y Témez (15 "
         "microcuencas) con números de terceros; el caudal es contraste de "
         "método",
         "el caudal: tc promediado con Bransby-Williams e IDF de regresión; "
         "la serie es inhomogénea (quiebre en 1998)"),
    Caso(UPAO, "upao_la_jalca",
         "Campos Muñoz e Inga Yopan, tesis UPAO, 2016, La Jalca–Nueva "
         "Esperanza (`tesis.pdf`; impresa = PDF − 20). Estación Chachapoyas, "
         "dos series discordantes (A y B)",
         ORACULO,
         "serie A: Δ y P24 de Normal, LN y Gumbel; serie B: Gumbel por "
         "momentos (siete TR). Segundo oráculo completo de estimadores y K-S, "
         "independiente del de Piura",
         "el caudal: IDF ajustada a la Tabla N.º 04 y evaluada a 14 min, y "
         "elige Log Pearson III, que MH no ajusta"),
    Caso(UPEU, "upeu_colpahuayco",
         "Huamán Guerra y Marrujo Carpio, UPeU, 2023, carretera "
         "Colpahuayco–Langui (`doc.pdf`; impresa = PDF). Estación Sicuani "
         "1993-2020",
         CONTRASTE,
         "es el único que aplica el racional modificado de Témez con sus "
         "pasos, pero su P24 sale de Pearson III y su C de un CN que no "
         "imprime; sólo el K se contrasta, y no en todas las filas",
         "la P24, el C y el caudal"),
    Caso(ESPOL, "espol_intervalles",
         "Luna Chalán, tesis ESPOL, 2023, vía Intervalles, Loja, Ecuador "
         "(`tesis.pdf`; impresa = PDF − 5). Cuatro estaciones INAMHI",
         DESCARTABLE,
         "la hidrología es ecuatoriana (IDF del INAMHI, fórmula del MTOP); "
         "lo que aporta son cuatro series reales con el Dmax de K-S de "
         "Hydrognomon, que coincide en Normal y Gumbel en tres estaciones",
         "toda la hidrología de MH; el cajón con HY-8 es de M3/M4"),
)

# ===========================================================================
# Las tolerancias, nombradas: las del dossier, con su razon
# ===========================================================================


@dataclass(frozen=True)
class Tolerancia:
    nombre: str
    valor: float
    relativa: bool
    unidad: str
    porque: str

    def admite(self, programa: float, publicado: float) -> bool:
        dif = abs(programa - publicado)
        if self.relativa:
            return dif <= self.valor * abs(publicado)
        return dif <= self.valor

    def texto(self) -> str:
        if self.relativa:
            if self.valor < TOL_REL_SIN_PORCENTAJE:
                return f"±{self.valor:g} (relativa)"
            return f"±{self.valor * 100:g} %"
        return f"±{self.valor:g}{(' ' + self.unidad) if self.unidad else ''}"


# Por debajo de esto una tolerancia relativa no se escribe en %: «±1e-07 %»
# no se lee; «±1e-09 (relativa)» si.
TOL_REL_SIN_PORCENTAJE = 1e-6


def _t(nombre, valor, relativa, unidad, porque) -> Tolerancia:
    return Tolerancia(nombre, valor, relativa, unidad, porque)


TOLERANCIAS: Dict[str, Tolerancia] = {t.nombre: t for t in (
    _t("TOL_P24_INDECI", 1e-3, True, "",
       "dossier §2.5: el estudio redondea z y los logaritmos a 3 decimales "
       "(medido: 0.05 %)"),
    _t("TOL_D_INDECI", 5e-4, False, "",
       "dossier §2.5: el Δ se imprime a 3 decimales"),
    _t("TOL_P24_UNTUMBES", 5e-4, True, "",
       "dossier §3.5: redondeo de z en HidroEsta (medido: 0.04 %)"),
    _t("TOL_D_UNTUMBES", 5e-5, False, "",
       "dossier §3.5: el Δ se imprime a 4 decimales"),
    _t("TOL_TC_UNTUMBES", 0.007, False, "h",
       "dossier §3.2 y §3.5: desvío máximo medido contra la columna TÉMEZ, "
       "con la pendiente derivada de las cotas"),
    _t("TOL_P24_UNSAAC", 1e-4, True, "",
       "dossier §4.5 (medido: 0.004 %)"),
    _t("TOL_I_UNSAAC", 0.02, False, "mm/h",
       "dossier §4.5: la P24 de la Tabla 6.8 está a 2 decimales (medido: "
       "0.013 mm/h)"),
    _t("TOL_TC_UNSAAC", 0.005, False, "min",
       "dossier §4.5: el tc se imprime a 2 decimales"),
    _t("TOL_D_UPAO", 5e-5, False, "",
       "dossier §5.5: el Δ se imprime a 4 decimales"),
    _t("TOL_P24_UPAO_A", 0.02, False, "mm",
       "dossier §5.5: las 15 lluvias de la serie A"),
    _t("TOL_XT_UPAO_B", 5e-5, True, "",
       "dossier §5.5: XT' de la serie B (medido: 0.003 %)"),
    _t("TOL_K_UPEU", 0.006, False, "",
       "dossier §6.5: el K se imprime a 2 decimales"),
    _t("TOL_D_ESPOL", 1e-4, False, "",
       "dossier §7: Dmax de Hydrognomon en Normal y Gumbel"),
    _t("TOL_REL_A_MANO", 1e-9, True, "",
       "dossier §2.5: programa contra el cálculo a mano del verificador, la "
       "misma aritmética"),
)}


def _medio_ultimo_digito(impreso: str) -> Tolerancia:
    """La tolerancia de un estadistico impreso: medio ultimo digito."""
    decimales = len(impreso.split(".")[1]) if "." in impreso else 0
    return Tolerancia("medio último dígito impreso", 0.5 * 10.0 ** -decimales,
                      False, "", "el estadístico se imprime a "
                      f"{decimales} decimales")


# ===========================================================================
# El contraste
# ===========================================================================

JUICIO_COINCIDE = "coincide"
JUICIO_METODO = "difiere por método (declarado)"
JUICIO_DETIENE = "el programa se detiene (esperado)"
JUICIO_EXPLICADO = "fuera de la tolerancia del dossier (explicado)"
JUICIO_DEFECTO = "DEFECTO"


@dataclass(frozen=True)
class Contraste:
    caso: str
    pieza: str
    que: str
    unidad: str
    publicado: float
    programa: Optional[float]
    tolerancia: Tolerancia
    cita: str
    metodo: str = ""          # por que el documento difiere (declarado)
    detencion: str = ""       # la excepcion del programa (esperada)
    fuera: str = ""           # por que queda fuera de la tolerancia

    def diferencia(self) -> Optional[float]:
        if self.programa is None:
            return None
        if self.tolerancia.relativa:
            return (self.programa - self.publicado) / self.publicado
        return self.programa - self.publicado

    @property
    def coincide(self) -> bool:
        return (self.programa is not None
                and self.tolerancia.admite(self.programa, self.publicado))

    @property
    def juicio(self) -> str:
        if self.programa is None:
            return JUICIO_DETIENE if self.detencion else JUICIO_DEFECTO
        if self.coincide:
            return JUICIO_COINCIDE
        if self.metodo:
            return JUICIO_METODO
        return JUICIO_EXPLICADO if self.fuera else JUICIO_DEFECTO


def _serie(carpeta: str, archivo: str, estacion: str):
    return MH.cargar_estacion(CASOS / carpeta / archivo)[estacion]


def _cuencas(carpeta: str):
    return MH.cargar_cuencas(CASOS / carpeta / "cuencas.csv")


def _ajustes(serie, TR: float) -> Dict[str, object]:
    """Los tres ajustes que MH evalua, por la puerta publica."""
    with declarados({FEN: COMPLETA, DIST: MH.MEJOR_AJUSTE_KS}):
        _, evaluados, *_ = MH.precipitacion_de_diseno(serie, TR)
    return {a.distribucion: a for a in evaluados}


def _parametro(ajuste, nombre: str) -> float:
    return dict(ajuste.parametros)[nombre]


def _sin_fen(serie):
    """La serie sin sus años FEN, como serie propia (la del Anexo 07.1)."""
    return replace(serie, registros=tuple(r for r in serie.registros
                                          if not r.fen))


def _intenta(f: Callable[[], object]) -> Tuple[object, Optional[ErrorProyecto]]:
    try:
        return f(), None
    except ErrorProyecto as error:
        return None, error


# ===========================================================================
# 1. INDECI Piura (dossier §2)
# ===========================================================================

PIURA_NORMAL = {
    "con": {2: 30.49, 5: 64.73, 10: 82.64, 20: 97.43, 25: 101.73, 50: 114.06,
            100: 125.15, 200: 135.30, 500: 147.60, 1000: 156.23},
    "sin": {2: 18.63, 5: 36.86, 10: 46.39, 20: 54.27, 25: 56.56, 50: 63.12,
            100: 69.03, 200: 74.43, 500: 80.98, 1000: 85.57}}
PIURA_LN = {
    "con": {2: 14.81, 5: 42.34, 10: 73.37, 20: 115.50, 25: 131.82, 50: 192.46,
            100: 270.49, 200: 369.33, 500: 538.65, 1000: 701.89},
    "sin": {2: 10.90, 5: 26.93, 10: 43.23, 20: 63.90, 25: 71.61, 50: 99.19,
            100: 132.98, 200: 173.89, 500: 240.67, 1000: 302.29}}
PIURA_GUMBEL_MOD = {
    "con": {5: 59.77, 10: 83.57, 20: 106.40, 25: 113.65, 50: 135.96,
            100: 158.11, 200: 180.18, 500: 209.29, 1000: 231.29},
    "sin": {5: 34.22, 10: 46.89, 20: 59.04, 25: 62.90, 50: 74.78, 100: 86.57,
            200: 98.32, 500: 113.82, 1000: 125.53}}
PIURA_DELTA = {"con": {NORMAL: 0.245, LN: 0.059, GUMBEL: 0.222},
               "sin": {NORMAL: 0.236, LN: 0.080, GUMBEL: 0.184}}
PIURA_ESTADISTICOS = {"con": ("30.5", "40.68", "1.170", "0.542"),
                      "sin": ("18.6", "21.66", "1.037", "0.467")}
PIURA_CITA_P24 = {"con": "Vol. II, Anexo 07.2, PDF 347",
                  "sin": "Vol. II, Anexo 07.1, PDF 339"}
PIURA_CITA_EST = {"con": "Vol. II, Anexo 07.2, PDF 346",
                  "sin": "Vol. II, Anexo 07.1, PDF 338"}
PIURA_CITA_DELTA = {"con": "Vol. I, Cuadro N.º 22, PDF 128 (imp. 112)",
                    "sin": "Vol. I, Cuadro N.º 21, PDF 127 (imp. 111)"}
PIURA_ROTULO = {"con": "con FEN (n = 38)", "sin": "sin FEN (n = 32)"}


def _piura():
    serie = _serie("indeci_piura", "estacion.csv", "Miraflores")
    return {"con": serie, "sin": _sin_fen(serie)}


def contrastes_indeci() -> Tuple[Contraste, ...]:
    filas: List[Contraste] = []
    tol_p, tol_d = TOLERANCIAS["TOL_P24_INDECI"], TOLERANCIAS["TOL_D_INDECI"]
    for clave, serie in _piura().items():
        rot = PIURA_ROTULO[clave]
        a = _ajustes(serie, 25)
        mu, s, ml, sl = PIURA_ESTADISTICOS[clave]
        for que, impreso, valor in (
                ("media μ", mu, _parametro(a[NORMAL], "mu")),
                ("desviación σ (n − 1)", s, _parametro(a[NORMAL], "S")),
                ("media de log10 P", ml, _parametro(a[LN], "Y") / math.log(10)),
                ("desviación de log10 P", sl,
                 _parametro(a[LN], "Sy") / math.log(10))):
            filas.append(Contraste(INDECI, f"estadísticos, {rot}", que, "mm"
                                   if "log" not in que else "",
                                   float(impreso), valor,
                                   _medio_ultimo_digito(impreso),
                                   PIURA_CITA_EST[clave]))
        for dist, nombre in ((NORMAL, "Normal"), (LN, "Log Normal"),
                             (GUMBEL, "Gumbel por momentos («Gumbel "
                                      "modificado»)")):
            filas.append(Contraste(
                INDECI, f"Δ de K-S, ec. (13), {rot}", nombre, "",
                PIURA_DELTA[clave][dist], a[dist].D, tol_d,
                PIURA_CITA_DELTA[clave]))
        for dist, nombre, tabla in ((NORMAL, "Normal", PIURA_NORMAL),
                                    (LN, "Log Normal", PIURA_LN),
                                    (GUMBEL, "Gumbel por momentos",
                                     PIURA_GUMBEL_MOD)):
            for TR, publicado in tabla[clave].items():
                filas.append(Contraste(
                    INDECI, f"P24(TR) {nombre}, {rot}", f"TR {TR}", "mm",
                    publicado, _ajustes(serie, TR)[dist].P_TR_mm, tol_p,
                    PIURA_CITA_P24[clave]))
    return tuple(filas)


# ===========================================================================
# 2. UNTumbes TU-107 (dossier §3)
# ===========================================================================

TUMBES_LN2 = {5: 278.23, 10: 412.70, 20: 571.46, 25: 628.29, 50: 824.21,
              70: 930.62, 100: 1052.08, 140: 1175.25, 200: 1315.40,
              500: 1724.28}                     # Tabla 47, p. 80 (XT', sin 1.13)
TUMBES_DELTA = {NORMAL: 0.1618, LN: 0.0535, GUMBEL: 0.1074}   # Tabla 36, p. 74
# Tabla 27, p. 65, columna TÉMEZ (h)
TUMBES_TEMEZ_H = {
    "C-1": 0.46, "C-2": 1.02, "C-3": 0.84, "C-4": 0.51, "C-5": 1.05,
    "C-6": 7.17, "C-7": 3.25, "C-8": 0.28, "C-9": 0.82, "C-10": 0.52,
    "C-11": 0.43, "C-12": 0.67, "C-13": 4.66, "C-14": 0.59, "C-15": 0.76,
    "C-16": 3.77, "C-17": 3.15, "C-18": 0.56, "C-19": 0.32, "C-20": 0.20,
    "C-21": 0.65, "C-22": 1.03, "C-23": 0.54, "C-24": 1.53, "C-25": 0.77,
    "C-26": 0.49, "C-27": 0.25, "C-28": 0.87, "C-29": 0.35, "C-30": 0.38,
    "C-31": 0.38, "C-32": 0.45, "C-33": 0.26, "C-34": 1.68, "C-35": 2.49,
    "C-36": 0.91, "C-37": 0.48, "C-38": 0.68, "C-39": 0.29, "C-40": 0.90,
    "C-41": 0.58}
TUMBES_ESTADISTICOS = (("media", "188.6725", "mu", "Tabla 28, p. 66"),
                       ("desviación (n − 1)", "169.5565", "S", "Tabla 28, p. 66"),
                       ("media de ln P", "4.8750", "Y", "Tabla 29, p. 67"),
                       ("desviación de ln P", "0.8955", "Sy", "Tabla 29, p. 67"))
# La unica fila de las 41 que excede la tolerancia del dossier, y por que.
TUMBES_TEMEZ_FUERA = {
    "C-13": ("la tesis imprime 4.66 h; con la longitud y las cotas de su "
             "Tabla 26 la ec. (30) da 4.6527 h, que es tambien el calculo a "
             "mano del verificador (4.652699 h en su `salida_esperada.json`). "
             "El ±0.007 h del dossier es su desvio maximo redondeado a tres "
             "decimales, y esta es la fila de ese maximo (0.0073 h, 0.16 %). "
             "La tolerancia no se ensancha para que pase"),
}
TEMEZ_BAJO_EL_RANGO = ("Témez da un Tc bajo 0.25 h y el Manual la acota a "
                       "0.25-24 h (núm. 3.12.2.1)")


def _tumbes():
    return _serie("untumbes_tu107",
                  "estacion_fen_declarado_por_el_verificador.csv", "Cañaveral")


def _temez_h(cuenca) -> Tuple[Optional[float], str]:
    tc, error = _intenta(lambda: MH.tc_temez_h(
        L_km=cuenca.L_cauce_m / METROS_POR_KM, S=cuenca.S_cauce_cuenca,
        area_km2=cuenca.area_km2))
    return tc, (type(error).__name__ if error else "")


def contrastes_tumbes() -> Tuple[Contraste, ...]:
    filas: List[Contraste] = []
    serie = _tumbes()
    a = _ajustes(serie, 70)
    for que, impreso, param, cita in TUMBES_ESTADISTICOS:
        dist = LN if param in ("Y", "Sy") else NORMAL
        filas.append(Contraste(TUMBES, "estadísticos", que,
                               "" if dist == LN else "mm", float(impreso),
                               _parametro(a[dist], param),
                               _medio_ultimo_digito(impreso), cita))
    for dist, nombre in ((NORMAL, "Normal"), (LN, "Log Normal 2P"),
                         (GUMBEL, "Gumbel")):
        filas.append(Contraste(TUMBES, "Δ de K-S, ec. (13)", nombre, "",
                               TUMBES_DELTA[dist], a[dist].D,
                               TOLERANCIAS["TOL_D_UNTUMBES"],
                               "Tabla 36, p. 74"))
    for TR, publicado in TUMBES_LN2.items():
        filas.append(Contraste(TUMBES, "P24(TR) Log Normal 2P", f"TR {TR}",
                               "mm", publicado, _ajustes(serie, TR)[LN].P_TR_mm,
                               TOLERANCIAS["TOL_P24_UNTUMBES"],
                               "Tabla 47, p. 80 (XT', antes del 1.13)"))
    for id_, cuenca in _cuencas("untumbes_tu107").items():
        tc, error = _temez_h(cuenca)
        filas.append(Contraste(TUMBES, "Témez, ec. (30)", id_, "h",
                               TUMBES_TEMEZ_H[id_], tc,
                               TOLERANCIAS["TOL_TC_UNTUMBES"],
                               "Tabla 27, p. 65", detencion=(
                                   f"{error}: {TEMEZ_BAJO_EL_RANGO}"
                                   if error else ""),
                               fuera=TUMBES_TEMEZ_FUERA.get(id_, "")))
    return tuple(filas)


# ===========================================================================
# 3. UNSAAC Roquepata (dossier §4)
# ===========================================================================

UNSAAC_GUMBEL = {10: 40.5334, 30: 52.1259, 35: 53.7268, 70: 60.8874,
                 100: 64.5560, 150: 68.7183, 200: 71.6680, 250: 73.9544,
                 500: 81.0509, 1000: 88.1423}   # Tabla 6.7, PDF 104 (imp. 92)
# Tabla 6.8, PDF 106 (imp. 94): TR -> (P24 impresa, I para d = 5..40 min)
UNSAAC_DP_D = (5, 10, 15, 20, 25, 30, 35, 40)
UNSAAC_DP = {
    10: (40.53, (118.07, 70.21, 51.80, 41.74, 35.31, 30.80, 27.44, 24.82)),
    30: (52.13, (151.84, 90.28, 66.61, 53.68, 45.41, 39.61, 35.28, 31.92)),
    35: (53.73, (156.50, 93.06, 68.66, 55.33, 46.81, 40.82, 36.37, 32.90)),
    70: (60.89, (177.36, 105.46, 77.81, 62.71, 53.04, 46.26, 41.21, 37.29)),
    100: (64.56, (188.05, 111.81, 82.50, 66.49, 56.24, 49.05, 43.70, 39.53)),
    1000: (88.14, (256.75, 152.67, 112.64, 90.78, 76.79, 66.97, 59.66, 53.98))}
# Tabla 6.5, PDF 99-100 (imp. 87-88), columna Témez (min)
UNSAAC_TEMEZ_MIN = {"A1": 24.18, "A2": 22.19, "A3": 17.93, "A4": 21.07,
                    "A5": 17.26, "A6": 15.95, "A7": 15.57, "A8": 12.44,
                    "A9": 12.74, "A10": 9.02, "A11": 7.81, "A12": 8.48,
                    "A13": 13.63, "A14": 16.23, "A15": 11.51}
UNSAAC_ESTADISTICOS = (("media", "23.43", "mu"), ("desviación (n − 1)",
                                                  "13.11", "S"))


def _colquepata():
    return _serie("unsaac_42tmc", "estacion.csv", "Colquepata")


def contrastes_unsaac() -> Tuple[Contraste, ...]:
    filas: List[Contraste] = []
    serie = _colquepata()
    a = _ajustes(serie, 35)
    for que, impreso, param in UNSAAC_ESTADISTICOS:
        filas.append(Contraste(UNSAAC, "estadísticos", que, "mm",
                               float(impreso), _parametro(a[NORMAL], param),
                               _medio_ultimo_digito(impreso),
                               "Tabla 6.6, PDF 102 (imp. 90)"))
    for TR, publicado in UNSAAC_GUMBEL.items():
        filas.append(Contraste(UNSAAC, "P24(TR) Gumbel por momentos",
                               f"TR {TR}", "mm", publicado,
                               _ajustes(serie, TR)[GUMBEL].P_TR_mm,
                               TOLERANCIAS["TOL_P24_UNSAAC"],
                               "Tabla 6.7, PDF 104 (imp. 92)"))
    for TR, (P24, intensidades) in UNSAAC_DP.items():
        for d, publicado in zip(UNSAAC_DP_D, intensidades):
            _, I = MH._intensidad(P24_mm=P24, d_min=d,
                                  relacion=MH.RELACION_DICK_PESCHKE)
            filas.append(Contraste(
                UNSAAC, "Dick-Peschke, ec. (16), con la P24 impresa",
                f"TR {TR}, d = {d} min", "mm/h", publicado, I,
                TOLERANCIAS["TOL_I_UNSAAC"], "Tabla 6.8, PDF 106 (imp. 94)"))
    for id_, cuenca in _cuencas("unsaac_42tmc").items():
        tc, error = _temez_h(cuenca)
        filas.append(Contraste(
            UNSAAC, "Témez, ec. (30)", id_, "min", UNSAAC_TEMEZ_MIN[id_],
            None if tc is None else tc * MINUTOS_POR_HORA,
            TOLERANCIAS["TOL_TC_UNSAAC"], "Tabla 6.5, PDF 99-100 (imp. 87-88)",
            detencion=f"{error}: {TEMEZ_BAJO_EL_RANGO}" if error else ""))
    return tuple(filas)


# ===========================================================================
# 4. UPAO La Jalca (dossier §5)
# ===========================================================================

UPAO_A = {NORMAL: (0.1591, {10: 59.72, 50: 71.56, 100: 75.74, 175: 78.85,
                            500: 84.19}),
          LN: (0.1149, {10: 56.90, 50: 72.52, 100: 79.00, 175: 84.20,
                        500: 93.94}),
          GUMBEL: (0.1032, {10: 60.07, 50: 79.81, 100: 88.15, 175: 94.86,
                            500: 107.43})}     # Cuadro N.º 19, PDF 93 (imp. 73)
UPAO_B_XT = {2: 35.5133, 5: 42.4672, 10: 47.0712, 25: 52.8885, 50: 57.2041,
             100: 61.4878, 500: 71.3868}       # PDF 115 (imp. 95)
UPAO_B_ESTADISTICOS = (("media", "36.81", "mu"),
                       ("desviación (n − 1)", "7.87", "S"))
NOMBRE_DIST = {NORMAL: "Normal", LN: "Log Normal", GUMBEL: "Gumbel"}


def contrastes_upao() -> Tuple[Contraste, ...]:
    filas: List[Contraste] = []
    serie_a = _serie("upao_la_jalca", "estacion.csv", "Chachapoyas-A")
    a = _ajustes(serie_a, 50)
    cita_a = "Cuadro N.º 19, PDF 93 (imp. 73)"
    for dist, (delta, lluvias) in UPAO_A.items():
        filas.append(Contraste(UPAO, "serie A: Δ de K-S, ec. (13)",
                               NOMBRE_DIST[dist], "", delta, a[dist].D,
                               TOLERANCIAS["TOL_D_UPAO"], cita_a))
        for TR, publicado in lluvias.items():
            filas.append(Contraste(
                UPAO, f"serie A: P24(TR) {NOMBRE_DIST[dist]}", f"TR {TR}",
                "mm", publicado, _ajustes(serie_a, TR)[dist].P_TR_mm,
                TOLERANCIAS["TOL_P24_UPAO_A"], cita_a))
    serie_b = _serie("upao_la_jalca", "estacion.csv", "Chachapoyas-B")
    b = _ajustes(serie_b, 50)
    for que, impreso, param in UPAO_B_ESTADISTICOS:
        filas.append(Contraste(UPAO, "serie B: estadísticos", que, "mm",
                               float(impreso), _parametro(b[NORMAL], param),
                               _medio_ultimo_digito(impreso),
                               "PDF 114 (imp. 94)"))
    for TR, publicado in UPAO_B_XT.items():
        filas.append(Contraste(UPAO, "serie B: XT' Gumbel por momentos",
                               f"TR {TR}", "mm", publicado,
                               _ajustes(serie_b, TR)[GUMBEL].P_TR_mm,
                               TOLERANCIAS["TOL_XT_UPAO_B"],
                               "PDF 115 (imp. 95)"))
    return tuple(filas)


# ===========================================================================
# 5. UPeU Colpahuayco (dossier §6)
# ===========================================================================

# Tabla 8, p. 20: el K impreso de las 12 alcantarillas de paso < 10 km2
UPEU_K = {"MC-01": 1.04, "MC-02": 1.03, "MC-03": 1.05, "MC-04": 1.06,
          "MC-05": 1.05, "MC-06": 1.06, "MC-08": 1.08, "MC-09": 1.05,
          "MC-10": 1.02, "MC-11": 1.02, "MC-12": 1.04, "MC-13": 1.02}
UPEU_K_METODO = ("el documento calculó Témez con la pendiente de la "
                 "microcuenca (fila «S» de su Tabla 6), no con la del cauce "
                 "mayor que la ec. (30) pide (fila «s»): con «S» el K "
                 "coincide (dossier §6.2)")


def _k_temez(cuenca, S: float) -> float:
    tc_h = MH.tc_temez_h(L_km=cuenca.L_cauce_m / METROS_POR_KM, S=S,
                         area_km2=cuenca.area_km2)
    return MH.coeficiente_de_uniformidad(tc_h)


def contrastes_upeu() -> Tuple[Contraste, ...]:
    filas: List[Contraste] = []
    cuencas = _cuencas("upeu_colpahuayco")
    for id_, publicado in UPEU_K.items():
        c = cuencas[id_]
        filas.append(Contraste(
            UPEU, "K de Témez, ec. (31), con la «s» del cauce (entrada de MH)",
            id_, "", publicado, _k_temez(c, c.S_cauce_cuenca),
            TOLERANCIAS["TOL_K_UPEU"], "Tabla 8, p. 20; L y s de la Tabla 6, "
            "p. 18", metodo=UPEU_K_METODO))
    for id_, publicado in UPEU_K.items():
        c = cuencas[id_]
        filas.append(Contraste(
            UPEU, "K de Témez con la «S» de la microcuenca (la que usó el "
            "documento)", id_, "", publicado, _k_temez(c, c.S_terreno),
            TOLERANCIAS["TOL_K_UPEU"], "Tabla 8, p. 20; S de la Tabla 6, "
            "p. 18"))
    return tuple(filas)


# ===========================================================================
# 6. ESPOL Intervalles (dossier §7)
# ===========================================================================

# Anexos 3 a 6, PDF 96-98: Dmax de Hydrognomon
ESPOL_DMAX = {"La Argelia": {LN: 0.07205, NORMAL: 0.10209, GUMBEL: 0.0896},
              "Gonzanama": {LN: 0.06859, NORMAL: 0.09365, GUMBEL: 0.06861},
              "Malacatos": {LN: 0.07291, NORMAL: 0.08111, GUMBEL: 0.08131},
              "Catamayo": {LN: 0.15415, NORMAL: 0.23595, GUMBEL: 0.16758}}
ESPOL_LN_METODO = ("Hydrognomon estima la Log Normal de otra forma que el "
                   "núm. 3.7.1.2 (logaritmos, n − 1)")
ESPOL_MALACATOS_METODO = ("con las otras tres estaciones cuadrando, la serie "
                          "impresa en el Anexo 2 no es exactamente la que "
                          "entró a Hydrognomon (dossier §7)")


def contrastes_espol() -> Tuple[Contraste, ...]:
    filas: List[Contraste] = []
    for estacion, dmax in ESPOL_DMAX.items():
        a = _ajustes(_serie("espol_intervalles", "estacion.csv", estacion), 50)
        for dist in (NORMAL, GUMBEL, LN):
            metodo = (ESPOL_MALACATOS_METODO if estacion == "Malacatos" else
                      ESPOL_LN_METODO if dist == LN else "")
            filas.append(Contraste(
                ESPOL, f"Dmax de K-S, {estacion}", NOMBRE_DIST[dist], "",
                dmax[dist], a[dist].D, TOLERANCIAS["TOL_D_ESPOL"],
                "Anexos 3 a 6, PDF 96-98", metodo=metodo))
    return tuple(filas)


def contrastes() -> Tuple[Contraste, ...]:
    return (contrastes_indeci() + contrastes_tumbes() + contrastes_unsaac()
            + contrastes_upao() + contrastes_upeu() + contrastes_espol())


# ===========================================================================
# Las detenciones (los casos adversariales de cada documento)
# ===========================================================================

@dataclass(frozen=True)
class Detencion:
    caso: str
    entrada: str
    esperada: str
    campo_esperado: str
    obtenida: str
    campo_obtenido: str
    por_que: str

    @property
    def como_se_espera(self) -> bool:
        return (self.obtenida == self.esperada
                and self.campo_obtenido == self.campo_esperado)


def _detencion(caso, entrada, esperada, campo, f, por_que) -> Detencion:
    _, error = _intenta(f)
    return Detencion(caso, entrada, esperada, campo,
                     type(error).__name__ if error else "no se detiene",
                     (getattr(error, "campo", "") or "") if error else "",
                     por_que)


def _con_anio_repetido() -> bytes:
    """La serie de Tumbes con la fila de 2002 rotulada 1989: la misma
    etiqueta de año dos veces."""
    ruta = CASOS / "untumbes_tu107" / \
        "estacion_fen_declarado_por_el_verificador.csv"
    texto = ruta.read_text(encoding="utf-8")
    assert "Cañaveral,2002," in texto
    return texto.replace("Cañaveral,2002,", "Cañaveral,1989,").encode("utf-8")


def detenciones() -> Tuple[Detencion, ...]:
    piura = _piura()["con"]
    piura5 = _serie("indeci_piura", "estacion_fen_5_sin_1973.csv",
                    "Miraflores")
    ruta_tumbes = CASOS / "untumbes_tu107" / \
        "estacion_fen_declarado_por_el_verificador.csv"
    MNE, DF, DI, CP = ("MetodoNoEvaluableError", "DatoFaltanteError",
                       "DatoInvalidoError", "CriterioPendienteError")
    salida: List[Detencion] = []

    def lluvia(serie, TR, valores):
        def f():
            with declarados(valores):
                return MH.precipitacion_de_diseno(serie, TR)
        return f

    def sin_declarar():
        with sin_valor(FEN):
            return MH.precipitacion_de_diseno(piura, 25)

    salida += [
        _detencion(INDECI, "`serie_sin_fen`, TR 25", MNE, "",
                   lluvia(piura, 25, {FEN: MH.FEN_SERIE_SIN_FEN}),
                   "sin FEN da menos lluvia que la serie completa: la hoja de "
                   "ruta manda adoptar la más conservadora (ficha T1-09); "
                   "INDECI tomó la serie con FEN «por criterio conservador»"),
        _detencion(INDECI, "variante con los 5 años FEN del Anexo 07.3, "
                   "`serie_sin_fen`", MNE, "",
                   lluvia(piura5, 25, {FEN: MH.FEN_SERIE_SIN_FEN}),
                   "la declaración de años FEN mueve la lluvia sin FEN, no "
                   "la adoptada"),
        _detencion(INDECI, "`dos_poblaciones`", MNE, "",
                   lluvia(piura, 25, {FEN: MH.FEN_DOS_POBLACIONES}),
                   "ninguna fuente da el procedimiento de población mixta"),
        _detencion(INDECI, "sin declarar `homogeneidad_serie_fen`", CP, "",
                   sin_declarar, "sin decidir qué se hace con los años FEN no "
                   "hay serie que ajustar"),
        _detencion(INDECI, "`normal` declarada", MNE, "",
                   lluvia(piura, 25, {FEN: COMPLETA, DIST: NORMAL}),
                   "no pasa K-S: D ≥ d crítico (0.2154, cuantil exacto n = "
                   "38)"),
        _detencion(INDECI, "`gumbel` declarada", MNE, "",
                   lluvia(piura, 25, {FEN: COMPLETA, DIST: GUMBEL}),
                   "no pasa K-S: D ≥ d crítico"),
        _detencion(TUMBES, "la serie como se publica (`fen` vacío)", DF, "fen",
                   lambda: MH.cargar_estacion(
                       CASOS / "untumbes_tu107"
                       / "estacion_como_se_publica_fen_vacio.csv"),
                   "la tesis no declara años FEN, y una celda vacía no se lee "
                   "como «no»: es la guardia que de verdad protege aquí"),
        _detencion(TUMBES, "la fila de 2002 rotulada 1989 (la misma etiqueta "
                   "de año dos veces)", DI, "anio",
                   lambda: MH.cargar_estacion(ruta_tumbes,
                                              datos=_con_anio_repetido()),
                   "un máximo anual por año: el dato está y contradice a otro"),
        _detencion(UNSAAC, "`lognormal_2p` declarada", MNE, "",
                   lluvia(_colquepata(), 35, {FEN: COMPLETA, DIST: LN}),
                   "no pasa K-S: D ≥ 0.26 (Tabla N.º 03, n = 25)"),
    ]
    alc = _cuencas("upao_la_jalca")["ALC-19"]
    serie_b = _serie("upao_la_jalca", "estacion.csv", "Chachapoyas-B")

    def alc19():
        with declarados({FEN: COMPLETA}):
            return MH.caudal_de_diseno(alc, serie_b, 50)

    salida.append(_detencion(
        UPAO, "ALC-19 con Kirpich, por omisión", MNE, "", alc19,
        "S = 21.1 %, fuera de la población de Kirpich (3 a 10 %, Tabla N.º "
        "05); la salida es otra fórmula, `indicador_con_aviso` o el caudal "
        "declarado"))
    cuencas_upeu = _cuencas("upeu_colpahuayco")
    sicuani = _serie("upeu_colpahuayco", "estacion.csv", "Sicuani")
    for id_ in ("MC-07", "MC-14"):
        def q(c=cuencas_upeu[id_]):
            with declarados({FEN: COMPLETA}):
                return MH.caudal_de_diseno(c, sicuani, 70)
        salida.append(_detencion(
            UPEU, f"{id_} (≥ 10 km², racional modificado)", DF, "CN", q,
            "el documento no publica el CN; va vacío a propósito"))
    return tuple(salida)


# ===========================================================================
# Caudales: contraste de método contra el documento, y el calculo a mano
# ===========================================================================

@dataclass(frozen=True)
class Caudal:
    caso: str
    cuenca: str
    TR: int
    magnitud: str
    unidad: str
    documento: Optional[float]
    cita_documento: str
    programa: float
    a_mano: float
    por_que_difiere: str

    @property
    def coincide_a_mano(self) -> bool:
        return TOLERANCIAS["TOL_REL_A_MANO"].admite(self.programa, self.a_mano)


def _caudal(carpeta, estacion, archivo_estacion, id_, TR, valores=None):
    cuenca = _cuencas(carpeta)[id_]
    serie = _serie(carpeta, archivo_estacion, estacion)
    with declarados({FEN: COMPLETA, **(valores or {})}):
        return MH.caudal_de_diseno(cuenca, serie, TR)


# El calculo a mano del verificador: `salida_esperada.json` de cada caso del
# dossier (sellado con sha1 antes de correr el programa).
A_MANO = {
    ("UNTumbes", "C-1", 35): {"tc_min": 27.665677053246043,
                              "I_mm_h": 580.8167236384426,
                              "Q_m3s": 6.215005166910939},
    ("UNTumbes", "C-6", 70): {"Q_m3s": 3751.9553113914935,
                              "C": 0.9158030149147586},
    ("UNTumbes", "C-7", 70): {"Q_m3s": 734.2562208143954},
    ("UNTumbes", "C-13", 70): {"Q_m3s": 835.2300802643985},
    ("UNTumbes", "C-16", 70): {"Q_m3s": 1131.1800583403792},
    ("UNTumbes", "C-17", 70): {"Q_m3s": 771.4236038606273},
    ("UNSAAC", "A1", 35): {"tc_min": 24.177516489703283,
                           "I_mm_h": 47.99638131668232,
                           "Q_m3s": 5.675265092915667},
    ("UPAO", "ALC-19", 50): {"tc_min": 14.27064831727966,
                             "I_mm_h": 75.8864874070169,
                             "Q_m3s": 9.22969403087843},
    ("UPeU", "MC-01", 70): {"tc_min": 37.77320713416002,
                            "I_mm_h": 28.591145027912653,
                            "Q_m3s": 2.402045489446021},
}
MAGNITUD = {"tc_min": ("tc", "min"), "I_mm_h": ("I", "mm/h"),
            "Q_m3s": ("Q", "m³/s"), "C": ("C", "")}


def caudales() -> Tuple[Caudal, ...]:
    """
    Lo que el programa entrega donde el documento calcula un caudal, contra
    el documento (sin tolerancia: es otro metodo) y contra el calculo a mano
    del verificador (`TOL_REL_A_MANO`).
    """
    filas: List[Caudal] = []
    tumbes_est = "estacion_fen_declarado_por_el_verificador.csv"
    doc_tumbes = {
        ("C-1", 35, "I_mm_h"): (280.28, "Tabla 66, p. 92"),
        ("C-1", 35, "Q_m3s"): (2.86, "Tabla 66, p. 92"),
        ("C-1", 35, "tc_min"): (26.81, "Tabla 27, p. 65 (promedio con "
                                       "Bransby-Williams)"),
        ("C-6", 70, "Q_m3s"): (1827.93, "Tabla 67, p. 93 (hidrograma "
                                        "triangular, CN 62)"),
        ("C-7", 70, "Q_m3s"): (345.23, "Tabla 67, p. 93"),
        ("C-13", 70, "Q_m3s"): (372.98, "Tabla 67, p. 93"),
        ("C-16", 70, "Q_m3s"): (534.64, "Tabla 67, p. 93"),
        ("C-17", 70, "Q_m3s"): (345.99, "Tabla 67, p. 93"),
    }
    razones = {
        "UNTumbes": ("IDF propia ajustada a la Tabla N.º 04 (1 a 24 h) y "
                     "extrapolada a minutos, con el factor 1.13; tc promedio "
                     "de Témez y Bransby-Williams; sobre 10 km² hidrograma "
                     "triangular. MH: Dick-Peschke bajo 1 h, Témez solo, "
                     "racional modificado desde 10 km²"),
        "UNSAAC": ("tc promedio de Témez y Bransby-Williams e IDF de "
                   "regresión sobre Dick-Peschke; MH: Témez solo, "
                   "Dick-Peschke en tc y K (`gumbel` declarada como en la "
                   "tesis)"),
        "UPAO": ("IDF ajustada a la Tabla N.º 04 y evaluada a 14 min; MH: "
                 "Dick-Peschke, que el núm. 3.8.1 manda bajo 1 h (Kirpich "
                 "fuera de su población, con `indicador_con_aviso`)"),
        "UPeU": ("P24 de Pearson III, I de la ec. (34) y C de un CN no "
                 "publicado; MH: racional (ec. 28) con Dick-Peschke y el C "
                 "del vehículo (0.30)"),
    }
    for (caso, id_, TR), valores in A_MANO.items():
        if caso == "UNTumbes":
            q = _caudal("untumbes_tu107", "Cañaveral", tumbes_est, id_, TR)
            documento = {k: doc_tumbes.get((id_, TR, k)) for k in valores}
        elif caso == "UNSAAC":
            q = _caudal("unsaac_42tmc", "Colquepata", "estacion.csv", id_, TR,
                        {DIST: GUMBEL})
            documento = {"tc_min": (22.51, "Tabla 6.5, PDF 99 (promedio)"),
                         "I_mm_h": None,
                         "Q_m3s": (5.20, "Tabla 6.13, PDF 111 (imp. 99)")}
        elif caso == "UPAO":
            q = _caudal("upao_la_jalca", "Chachapoyas-B", "estacion.csv", id_,
                        TR, {MH.CRITERIO_POBLACION_TC: "indicador_con_aviso"})
            documento = {"tc_min": (14.27, "PDF 139 (imp. 119)"),
                         "I_mm_h": (32.72327, "PDF 139 (imp. 119)"),
                         "Q_m3s": (3.99, "PDF 140 (imp. 120)")}
        else:
            q = _caudal("upeu_colpahuayco", "Sicuani", "estacion.csv", id_, TR)
            documento = {"tc_min": None,
                         "I_mm_h": (27.10, "Tabla 8, p. 20"),
                         "Q_m3s": (2.41, "Tabla 8, p. 20")}
        programa = {"tc_min": q.tc_min, "I_mm_h": q.I_mm_h, "Q_m3s": q.Q_m3s,
                    "C": q.C}
        for clave, a_mano in valores.items():
            doc = documento.get(clave)
            simbolo, unidad = MAGNITUD[clave]
            filas.append(Caudal(caso, id_, TR, simbolo, unidad,
                                doc[0] if doc else None,
                                doc[1] if doc else "no publicado",
                                programa[clave], a_mano, razones[caso]))
    return tuple(filas)


# ===========================================================================
# Los hallazgos del dossier sobre MH, como contrastes de metodo (§8)
# ===========================================================================

# El d critico que usa cada documento: 1.36/√n, impreso.
CRITICOS_PUBLICADOS = (
    (INDECI, "Miraflores sin FEN", 32, 0.24, "Vol. I, Cuadro N.º 21"),
    (INDECI, "Miraflores con FEN", 38, 0.22, "Vol. I, Cuadro N.º 22"),
    (TUMBES, "Cañaveral", 40, 0.2150, "Tabla 36, p. 74 («1.36/√N»)"),
    (UPAO, "Chachapoyas-A", 17, 0.3298, "Cuadro N.º 19, PDF 93"),
    (UPEU, "Sicuani", 28, 0.2570, "p. 19"),
)


def criticos() -> Tuple[Tuple[str, str, int, float, str, float, str], ...]:
    salida = []
    for caso, serie, n, publicado, cita in CRITICOS_PUBLICADOS:
        alfa = ca.valor(MH.CRITERIO_ALFA)
        d, origen = MH.valor_critico_ks(n, alfa)
        salida.append((caso, serie, n, publicado, cita, d, origen))
    return tuple(salida)


@dataclass(frozen=True)
class Medidas:
    """Los numeros de los hallazgos H3 a H9, medidos con el programa."""
    piura_normal_sin_fen_D: float
    piura_d_sin_fen: float
    piura_ln25_con: float
    piura_ln25_sin: float
    piura_ln25_sin_1971: float
    tumbes_c6_q70: float
    tumbes_c6_avisos: Tuple[str, ...]
    tumbes_consistencia: str
    tumbes_p24_70: float
    unsaac_normal_35: float
    colquepata_maximo: float
    unsaac_razones_q: Tuple[float, float]
    unsaac_temez_detenidas: int
    unsaac_kirpich_fuera: int
    tumbes_temez_detenidas: int


# Tabla 6.13, PDF 111 (imp. 99): Q a 35 años de las ocho microcuencas que
# Temez deja evaluar.
UNSAAC_Q35 = {"A1": 5.20, "A2": 9.37, "A3": 2.88, "A4": 1.91, "A5": 3.30,
              "A6": 3.37, "A7": 2.95, "A14": 3.34}


def medidas() -> Medidas:
    piura = _piura()
    a_sin = _ajustes(piura["sin"], 25)
    sin_1971 = replace(piura["con"], registros=tuple(
        r for r in piura["con"].registros if r.anio != min(
            x.anio for x in piura["con"].registros)))
    c6 = _caudal("untumbes_tu107", "Cañaveral",
                 "estacion_fen_declarado_por_el_verificador.csv", "C-6", 70)
    with declarados({FEN: COMPLETA}):
        *_, pasos, _ = MH.precipitacion_de_diseno(_tumbes(), 70)
    (consistencia,) = [p for p in pasos if p.codigo == MH.CODIGO_CONSISTENCIA]
    razones = tuple(
        _caudal("unsaac_42tmc", "Colquepata", "estacion.csv", id_, 35,
                {DIST: GUMBEL}).Q_m3s / q for id_, q in UNSAAC_Q35.items())
    cuencas_unsaac = _cuencas("unsaac_42tmc").values()
    kirpich_fuera = sum(
        1 for c in cuencas_unsaac
        if not MH.poblacion_del_metodo(MH.TC_METODO_KIRPICH,
                                       pendiente=c.S_cauce_cuenca)[0])
    return Medidas(
        piura_normal_sin_fen_D=a_sin[NORMAL].D,
        piura_d_sin_fen=a_sin[NORMAL].d_critico,
        piura_ln25_con=_ajustes(piura["con"], 25)[LN].P_TR_mm,
        piura_ln25_sin=a_sin[LN].P_TR_mm,
        piura_ln25_sin_1971=_ajustes(sin_1971, 25)[LN].P_TR_mm,
        tumbes_c6_q70=c6.Q_m3s, tumbes_c6_avisos=c6.avisos,
        tumbes_consistencia=consistencia.nota_del_proyecto,
        tumbes_p24_70=_ajustes(_tumbes(), 70)[LN].P_TR_mm,
        unsaac_normal_35=_ajustes(_colquepata(), 35)[NORMAL].P_TR_mm,
        colquepata_maximo=max(r.p24_mm for r in _colquepata().registros),
        unsaac_razones_q=(min(razones), max(razones)),
        unsaac_temez_detenidas=sum(1 for c in contrastes_unsaac()
                                   if c.pieza.startswith("Témez")
                                   and c.programa is None),
        unsaac_kirpich_fuera=kirpich_fuera,
        tumbes_temez_detenidas=sum(1 for c in contrastes_tumbes()
                                   if c.pieza.startswith("Témez")
                                   and c.programa is None))


# ===========================================================================
# Las erratas de los documentos que el dossier señala (§2.4, 3.3, 4.4, 5.4,
# 6.3). Ninguna afecta a los numeros que se usan de oraculo.
# ===========================================================================

ERRATAS: Dict[str, Tuple[str, ...]] = {
    INDECI: (
        "Cuadro 13, fila «Prom. S/Niños», ANUAL: imprime 42.5; la media sin "
        "Niños es 18.6 (su propio Anexo 07.1).",
        "Cuadro 13, fila «MAX S/Niños», ANUAL: imprime 107.1, que es 1992, año "
        "que el estudio trata como FEN; sería 103.5 (2002).",
        "Anexos 07.1 y 07.3: 1973 sale de «sin FEN» y no entra en «sólo FEN» "
        "(el estudio escribe «72/73» como un evento).",
        "Cuadro 22: Normal (0.245), Gumbel (0.254) y Gumbel modificado "
        "(0.222) superan el Δ tabular 0.22 y el texto no lo comenta.",
        "Vol. I PDF 125 (imp. 109), ítem e): repite «sin considerar los "
        "fenómenos El Niño»; por el Anexo 07.5 es «considerando».",
        "Figura 26, PDF 133: eje rotulado «Caudal m3/s» sobre curvas de "
        "precipitación.",
        "Cuadro 13, 1971: año parcial (abril a diciembre, máximo 1.6 mm) que "
        "entra en las dos series.",
        "La serie «sin FEN» conserva 1997 (54.0 mm, diciembre, inicio del FEN "
        "97-98) y 2002 (103.5 mm)."),
    TUMBES: (
        "Tabla 23, p. 60: filas copiadas; 2002 = 1989 en los 12 meses y 2001 "
        "= 1996 en 11 de 12 (mayo: 11.00 frente a 11.10).",
        "Tabla 23: 14 celdas mensuales de 300 mm o más en 24 h (1983, 1987, "
        "1991, 1992, 1997, 2000, 2017, 2023); el máximo de Miraflores en 38 "
        "años es 173.6 mm.",
        "El evento de 1998 aparece en «1997» (502 a 729 mm de enero a abril; "
        "«1998», 150 mm).",
        "No menciona El Niño, con 1983 y 1997-98 en la serie; faltan 1988 y "
        "2022 (Tabla 22).",
        "Tabla 27: promedia Témez con Bransby-Williams y usa Témez bajo 0.25 "
        "h (C-20: 0.20 h; C-27: 0.25 h impreso, 0.246 h recalculado).",
        "Tablas 48 y 65: IDF ajustada a los coeficientes de la Tabla N.º 04 (1 "
        "a 24 h) y aplicada a duraciones de 11 a 60 min."),
    UNSAAC: (
        "Tabla 6.7, título: dice «distribución normal»; el contenido es "
        "Gumbel.",
        "Tabla 6.13, encabezado: «T= 35 AÑOS» dos veces; la tercera columna es "
        "70 años.",
        "PDF 100-101: dice 28 registros de 1990 a 2017; la serie llega a 2014 "
        "(25 años).",
        "Serie inhomogénea: 1990-1997 de 4.4 a 9.3 mm (media 6.54); 1998-2014 "
        "de 20.1 a 48.2 mm (media 31.38).",
        "PDF 103: afirma que el mejor ajuste es Gumbel; con el K-S del Manual "
        "es la Normal, y el anexo no se publicó."),
    UPAO: (
        "Series A y B, 1973: 25.5 mm en la A y 27.0 en la B; en la tabla "
        "mensual 25.50 es junio y 27.00 abril: el máximo es 27.0.",
        "PDF 139 (imp. 119): escribe Kirpich con L^0.76; los 14.27 min "
        "impresos salen con 0.77, el exponente del Manual.",
        "PDF 115 (imp. 95), lluvia de 18 h a 25 años: 47.21 mm; sería 0.90 · "
        "59.76 = 53.79, y contamina la regresión de TR 25.",
        "PDF 90 (imp. 70): anuncia «tres estaciones» y registros hasta 2003; "
        "hay una estación y la serie acaba en 2001.",
        "Alcantarilla 19: Kirpich con S = 21.1 %, fuera de la población de 3 "
        "a 10 %."),
    UPEU: (
        "Tablas 6 y 8: las áreas no coinciden (0.97 km² frente a 113.89 ha; "
        "0.20 frente a 25.57; 3.70 frente a 403.16).",
        "Tabla 8, columna Q: el K no entra en el caudal impreso (0.278·C·I·A "
        "sin K reproduce las filas 1, 9, 10, 11 y 13).",
        "Témez con la pendiente de la microcuenca, no la del cauce mayor "
        "(sección 7 de este documento).",
        "Ec. (1), p. 13: «R = 1 − (1 − T)^n»; es 1 − (1 − 1/T)^n.",
        "p. 15: «P0 = [(500/CN) – 50]»; el Manual escribe 5000/CN (ec. 35).",
        "Tabla 4, p. 14: Kirpich con 3.98 y unidad «h»; ese coeficiente da "
        "minutos.",
        "Tabla 8: C a 2 decimales (±1.7 %), lo que impide separar la fila 2 "
        "con K y sin K."),
    ESPOL: (
        "Malacatos: el Dmax de Hydrognomon no corresponde a la serie impresa "
        "en el Anexo 2 (las otras tres estaciones cuadran).",),
}


# ===========================================================================
# El documento
# ===========================================================================

def _celda(texto) -> str:
    return str(texto).replace("|", "\\|").replace("\n", " ")


def _num(x: Optional[float]) -> str:
    """Un numero del programa: siete cifras significativas."""
    if x is None:
        return "—"
    return f"{x:.7g}"


def _impreso(x: Optional[float]) -> str:
    """Un numero publicado, con las cifras con que se transcribio."""
    return "—" if x is None else repr(x)


# Lo que «+0.000 %» ya no distingue de cero: medio milesimo de punto.
MEDIO_MILESIMO_DE_PUNTO = 5e-6


def _dif(c: Contraste) -> str:
    d = c.diferencia()
    if d is None:
        return "—"
    if c.tolerancia.relativa:
        return ("0.000 %" if abs(d) < MEDIO_MILESIMO_DE_PUNTO
                else f"{d * 100:+.3f} %")
    return f"{d:+.2g}"


def _seccion_contrastes(A, filas: Sequence[Contraste]) -> None:
    A("| Pieza | Qué | Publicado | Programa | Diferencia | Tolerancia | "
      "Juicio | Cita |")
    A("|---|---|---|---|---|---|---|---|")
    for c in filas:
        tol = (c.tolerancia.texto() if c.tolerancia.nombre.startswith("medio")
               else f"`{c.tolerancia.nombre}` {c.tolerancia.texto()}")
        A("| " + " | ".join(_celda(x) for x in (
            c.pieza, c.que, _impreso(c.publicado),
            _num(c.programa) if c.programa is not None else c.detencion,
            _dif(c), tol, c.juicio, c.cita)) + " |")
    A("")
    notas = sorted({c.metodo for c in filas
                    if c.juicio == JUICIO_METODO and c.metodo})
    if notas:
        A("Diferencias de método declaradas:")
        A("")
        for n in notas:
            quien = ", ".join(f"{c.pieza.split(',')[-1].strip()} {c.que}"
                              if c.caso == ESPOL else c.que
                              for c in filas if c.metodo == n
                              and c.juicio == JUICIO_METODO)
            A(f"- *{quien}*: {n}.")
        A("")
    for c in filas:
        if c.juicio == JUICIO_EXPLICADO:
            A(f"Fuera de la tolerancia del dossier, *{c.que}*: {c.fuera}.")
            A("")


def _cuenta(filas: Sequence[Contraste]) -> str:
    cuenta = {j: sum(1 for c in filas if c.juicio == j)
              for j in (JUICIO_COINCIDE, JUICIO_METODO, JUICIO_EXPLICADO,
                        JUICIO_DETIENE, JUICIO_DEFECTO)}
    return "; ".join(f"{v} «{k}»" for k, v in cuenta.items())


def generar() -> str:
    L: List[str] = []
    A = L.append
    todos = contrastes()
    por_caso = {c.nombre: [x for x in todos if x.caso == c.nombre]
                for c in CASOS_REALES}
    A("# Validación hidrológica de MH con casos reales publicados")
    A("")
    A("> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe "
      "`python -m tests.apoyo.validacion_hidrologica --escribir` y "
      "`tests/test_validacion_hidrologica.py` lo regenera y lo compara. Las "
      "cifras publicadas están transcritas con su documento, página y tabla "
      "en `tests/apoyo/validacion_hidrologica.py`; las entradas, en "
      "`tests/fixtures/hidrologia_casos_reales/` (DATOS DE CASO REAL "
      "PUBLICADO — no son datos de este proyecto); la cuenta es la de las "
      "funciones de `src/modulos/MH_hidrologia.py`. Los PDF están en el "
      "repositorio de normas, `ejemplos_resueltos/casos_reales/`.")
    A("")
    A("## 1. Qué es, de dónde sale y qué no valida")
    A("")
    A(f"El material es de una verificación independiente (dossier `{DOSSIER}`): "
      "el verificador transcribió los seis documentos, hizo el cálculo a "
      "mano sin importar `src/`, lo congeló con sha1 antes de correr el "
      "programa y después comparó. Este documento rehace la comparación con "
      "el programa en cada corrida de la suite.")
    A("")
    A("**Lo que ningún caso valida: el caudal de punta a punta.** Ninguno de "
      "los seis documentos calcula el caudal con el método de MH (P24 por "
      "ajuste con K-S, tc de la Tabla N.º 05 o de Témez, Dick-Peschke bajo "
      "1 h, C de la Tabla N.º 08, racional o racional modificado): todos "
      "usan otra relación intensidad-duración, otro tc o un C que la Tabla "
      "N.º 08 no puede dar. Lo que se valida con números de terceros son "
      "PIEZAS: el estadístico K-S de la ecuación (13), los tres estimadores "
      "(Normal, Log Normal 2P, Gumbel por momentos), Dick-Peschke, Témez y "
      "el K de Témez. El caudal se compara sólo contra el cálculo a mano del "
      "verificador (sección 10).")
    A("")
    A("Tampoco se validan: el C (ningún documento publica `cobertura`, "
      "`suelo` ni `S_terreno`; en los CSV son VEHÍCULO DEL VERIFICADOR que "
      "lleva a la Tabla N.º 08 al C declarado), el CN del racional "
      "modificado (ninguno lo publica con su caudal), la Log Pearson III y "
      "las demás distribuciones sin estimador impreso (MH no las ajusta), y "
      "el pipeline completo por la CLI (no hay CSV de puntos publicable sin "
      "inventar columnas).")
    A("")
    A("| Caso | Documento | Clasificación | Por qué | Qué NO valida |")
    A("|---|---|---|---|---|")
    for c in CASOS_REALES:
        A(f"| {_celda(c.nombre)} | {_celda(c.documento)} | "
          f"**{_celda(c.clasificacion)}** | {_celda(c.razon)} | "
          f"{_celda(c.no_valida)} |")
    A("")
    A("## 2. Tolerancias y regla de juicio")
    A("")
    A("| Nombre | Valor | Por qué |")
    A("|---|---|---|")
    for t in TOLERANCIAS.values():
        A(f"| `{t.nombre}` | {t.texto()} | {_celda(t.porque)} |")
    A("| medio último dígito impreso | 0.5·10^−k | los estadísticos (media, "
      "desviación) impresos a k decimales |")
    A("")
    A(f"Juicios: «{JUICIO_COINCIDE}» (dentro de la tolerancia), "
      f"«{JUICIO_METODO}» (fuera, con la diferencia de método escrita), "
      f"«{JUICIO_EXPLICADO}» (fuera por menos que el redondeo de la propia "
      "tolerancia, con el programa igual al cálculo a mano y la razón "
      "escrita), "
      f"«{JUICIO_DETIENE}» (el caso adversarial: la excepción del programa es "
      f"la esperada) y «{JUICIO_DEFECTO}» (ninguno de los anteriores). La "
      "suite exige cero defectos. En una tolerancia relativa la diferencia "
      "es relativa; en una absoluta, absoluta.")
    A("")
    titulos = {
        INDECI: "INDECI Piura — oráculo numérico, con y sin años FEN",
        TUMBES: "UNTumbes TU-107 — adversarial; su estadística es oráculo",
        UNSAAC: "UNSAAC Roquepata — oráculo de Gumbel, Dick-Peschke y Témez",
        UPAO: "UPAO La Jalca — oráculo de la estadística (series A y B)",
        UPEU: "UPeU Colpahuayco — contraste de método (el K de Témez)",
        ESPOL: "ESPOL Intervalles — contraste de método del K-S",
    }
    for numero, caso in enumerate(CASOS_REALES, start=3):
        A(f"## {numero}. {titulos[caso.nombre]}")
        A("")
        _seccion_contrastes(A, por_caso[caso.nombre])
    A("## 9. Las detenciones: qué hace el programa con la entrada defectuosa")
    A("")
    A("| Caso | Entrada | Esperada | Obtenida | Por qué |")
    A("|---|---|---|---|---|")
    for d in detenciones():
        esp = d.esperada + (f" (`{d.campo_esperado}`)" if d.campo_esperado
                            else "")
        obt = d.obtenida + (f" (`{d.campo_obtenido}`)" if d.campo_obtenido
                            else "")
        A("| " + " | ".join(_celda(x) for x in (
            d.caso, d.entrada, esp,
            obt if d.como_se_espera else f"**{obt}**", d.por_que)) + " |")
    A("")
    A("## 10. Caudales: el documento (otro método) y el cálculo a mano")
    A("")
    A("El caudal **no** se juzga contra el documento: es otro método (columna "
      "«por qué difiere»). Se juzga contra el cálculo a mano del verificador "
      "(`salida_esperada.json` de cada caso, sellado antes de correr el "
      "programa) con `TOL_REL_A_MANO`.")
    A("")
    A("| Caso | Cuenca | TR | Magnitud | Documento | Programa | Programa / "
      "documento | A mano | ¿Coincide a mano? | Cita del documento |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for q in caudales():
        razon = (f"{q.programa / q.documento:.3g}" if q.documento else "—")
        A("| " + " | ".join(_celda(x) for x in (
            q.caso, q.cuenca, q.TR, f"{q.magnitud} ({q.unidad})"
            if q.unidad else q.magnitud, _impreso(q.documento),
            _num(q.programa),
            razon, _num(q.a_mano), "sí" if q.coincide_a_mano else "**NO**",
            q.cita_documento)) + " |")
    A("")
    A("Por qué el documento da otro caudal:")
    A("")
    for caso in ("UNTumbes", "UNSAAC", "UPAO", "UPeU"):
        (razon,) = {q.por_que_difiere for q in caudales() if q.caso == caso}
        A(f"- **{caso}.** {razon}.")
    A("")
    m = medidas()
    A("## 11. Hallazgos sobre MH: contrastes de método, sin cambiar el cálculo")
    A("")
    A("Ninguno es un error numérico (dossier §8). Salvo H1, que desde la "
      "ficha VE3-19 de `docs/decisiones_diferidas.md` es un renglón del "
      "aviso de consistencia, quedan documentados aquí y el cálculo no "
      "cambia.")
    A("")
    A("**H1. Filas copiadas entre años (UNTumbes).** Con un máximo por año "
      "la copia no es demostrable y dos máximos iguales son normales. Desde "
      "VE3-19 el aviso de consistencia sin umbral (paso 1b.3c) lista los "
      "máximos repetidos con sus años, sin detener, quitar ni juzgar. Para "
      "Cañaveral el programa imprime:")
    A("")
    renglon = m.tumbes_consistencia[m.tumbes_consistencia.index("Maximos "
                                                                "anuales"):]
    A(f"> {renglon}")
    A("")
    A("Y la misma etiqueta de año dos veces sigue siendo `DatoInvalidoError` "
      "(sección 9).")
    A("")
    A("**H2. La guardia que protege en Tumbes es la celda `fen` "
      "obligatoria.** La serie como se publica no carga (sección 9). Una vez "
      "que alguien escribe «no» en toda la columna, sólo queda el aviso de "
      "que la serie no declara ningún año FEN.")
    A("")
    A("**H3. Con la serie de Tumbes el programa entrega caudal, con aviso.** "
      f"P24(70) = {m.tumbes_p24_70:.1f} mm (Log Normal 2P) y, en la "
      f"quebrada Sapotal (C-6, 102.71 km²), Q70 = {m.tumbes_c6_q70:.0f} "
      "m³/s por el racional modificado. No se detiene: no hay umbral que "
      "inventar. Los avisos que acompañan a ese caudal:")
    A("")
    for aviso in m.tumbes_c6_avisos:
        A(f"- {_celda(aviso)}")
    A("")
    A("La defensa real es que el proyectista lea la memoria: un revisor "
      "externo esperará una detención.")
    A("")
    A("**H4. El valor crítico de K-S no es 1.36/√n.** Los cuatro documentos "
      "peruanos usan 1.36/√n; MH usa la celda de la Tabla N.º 03 cuando n es "
      "fila y, si no, el cuantil exacto del mismo estadístico, que es más "
      "estricto. Conviene que la memoria lo diga, porque es lo que el "
      "revisor recalculará.")
    A("")
    A("| Caso | Serie | n | d del documento | Cita | d del programa | De dónde "
      "sale |")
    A("|---|---|---|---|---|---|---|")
    for caso, serie, n, pub, cita, d, origen in criticos():
        A(f"| {caso} | {serie} | {n} | {pub:g} | {cita} | {d:.4f} | "
          f"{_celda(origen)} |")
    A("")
    A("Cambia un veredicto de los revisados: la Normal de Miraflores sin FEN "
      f"(D = {m.piura_normal_sin_fen_D:.4f}) pasa con 0.24 y no pasa con "
      f"{m.piura_d_sin_fen:.4f}.")
    A("")
    upao = [q for q in caudales() if q.caso == "UPAO" and q.magnitud == "I"]
    tum = [q for q in caudales() if q.caso == "UNTumbes" and q.cuenca == "C-1"
           and q.magnitud == "I"]
    A("**H5. Dick-Peschke frente a la Tabla N.º 04 extrapolada bajo 1 h.** "
      "Para tc < 1 h MH da una intensidad del orden del doble que las tesis "
      "que extrapolan los coeficientes de la Tabla N.º 04 (válidos de 1 a 24 "
      f"h): {upao[0].programa / upao[0].documento:.2f} veces en UPAO "
      f"(ALC-19) y {tum[0].programa / tum[0].documento:.2f} en UNTumbes "
      "(C-1, y la tesis lleva además el factor 1.13). MH aplica lo que el "
      "núm. 3.8.1 manda para duraciones menores de 1 hora, y el criterio "
      "`relacion_intensidad_duracion` ya lo declara. Donde la tesis usa "
      "Dick-Peschke (UNSAAC), el caudal de MH queda entre "
      f"{(m.unsaac_razones_q[0] - 1) * 100:+.1f} % y "
      f"{(m.unsaac_razones_q[1] - 1) * 100:+.1f} % sobre el impreso en las "
      "ocho microcuencas que Témez deja evaluar (Tabla 6.13, PDF 111).")
    A("")
    A("**H6. Las microcuencas pequeñas y empinadas no tienen, por omisión, "
      f"fórmula de tc evaluable.** En UNSAAC {m.unsaac_temez_detenidas} de 15 "
      "dan Témez bajo 0.25 h y "
      f"{m.unsaac_kirpich_fuera} de 15 están fuera de la población de "
      f"Kirpich; en UNTumbes, {m.tumbes_temez_detenidas} de 41. El programa "
      "se detiene con `MetodoNoEvaluableError` y ofrece la salida (otra "
      "fórmula, `indicador_con_aviso` o el caudal declarado). Es la letra del "
      "Manual; en sierra es una limitación práctica que la guía de uso "
      "conviene que anticipe.")
    A("")
    A("**H7. `serie_sin_fen` no es adoptable en costa norte.** En Miraflores "
      f"la Log Normal a 25 años da {m.piura_ln25_sin:.1f} mm sin FEN y "
      f"{m.piura_ln25_con:.1f} mm con FEN (razón "
      f"{m.piura_ln25_con / m.piura_ln25_sin:.2f}): `serie_sin_fen` se "
      "detiene con las dos declaraciones de años FEN (sección 9), que es la "
      "regla de la ficha T1-09 y la decisión de INDECI. En una estación con "
      "FEN extraordinario el criterio tiene un solo valor utilizable.")
    A("")
    A("**H8. `mejor_ajuste_ks` puede elegir la Normal en una serie con "
      "quiebre.** Colquepata: la Normal da P24(35) = "
      f"{m.unsaac_normal_35:.2f} mm, apenas sobre el máximo registrado "
      f"({m.colquepata_maximo:.1f} mm). El defecto es de la serie "
      "(inhomogénea), no de la regla; el aviso de consistencia deja a la "
      "vista el mínimo y el máximo.")
    A("")
    A("**H9. El contrato no marca un año incompleto.** 1971 en Miraflores "
      "trae nueve meses y entra con 1.6 mm; quitarlo mueve la Log Normal a 25 "
      f"años de {m.piura_ln25_con:.1f} a {m.piura_ln25_sin_1971:.1f} mm "
      f"({(m.piura_ln25_sin_1971 / m.piura_ln25_con - 1) * 100:+.1f} %). "
      "Menor.")
    A("")
    A("## 12. Erratas de los documentos (dossier)")
    A("")
    A("Ninguna afecta a los números que se usan de oráculo.")
    A("")
    for caso, erratas in ERRATAS.items():
        A(f"**{caso}.**")
        A("")
        for e in erratas:
            A(f"- {e}")
        A("")
    A("## 13. Resumen")
    A("")
    for caso in CASOS_REALES:
        A(f"- **{caso.nombre}** ({caso.clasificacion}): "
          f"{len(por_caso[caso.nombre])} contrastes — "
          f"{_cuenta(por_caso[caso.nombre])}.")
    dets = detenciones()
    A(f"- **Detenciones:** {sum(d.como_se_espera for d in dets)} de "
      f"{len(dets)} con la excepción esperada.")
    qs = caudales()
    A(f"- **Caudales contra el cálculo a mano:** "
      f"{sum(q.coincide_a_mano for q in qs)} de {len(qs)} dentro de "
      "`TOL_REL_A_MANO`.")
    defectos = [c for c in todos if c.juicio == JUICIO_DEFECTO]
    A(f"- **Defectos del programa: {len(defectos)}.** Ningún caso valida el "
      "caudal de punta a punta.")
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
