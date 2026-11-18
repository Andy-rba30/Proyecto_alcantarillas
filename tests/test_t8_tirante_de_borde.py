"""
tests/test_t8_tirante_de_borde.py
=================================
Aceptacion del cierre de las fichas T8-08 y T8-09 de
`docs/decisiones_diferidas.md` (trabajo posterior a la cadena T, README §8):

  * T8-08 · las Figuras 3.3 (rectangular) y 3.4 (circular) de HEC-14
    (num. 3.1.3, pags. impresas 3-5 y 3-6, PDF 36 y 37) transcritas como
    tablas del registro normativo, leidas POR IMAGEN con una tolerancia de
    lectura nombrada, y `M4.tirante_de_borde` sustituyendo al tirante critico
    en la primera viñeta de `M4.velocidad_de_salida` (control de salida con
    el TW bajo el critico) para las dos formas que las figuras cubren.
  * T8-09 · en la banda en que la rama de n maximo da flujo subcritico y la
    de n minimo lo daria supercritico, la velocidad de salida es la MAYOR de
    la de borde (o la critica) y `V_erosion` (decision del dueño: la regla
    del maximo).

ROJO PRIMERO: este archivo se escribio y se corrio contra el arbol de
partida (`6b08e4b`) antes de tocar el codigo, y fallo entero en la
coleccion (`ImportError`: no existia `tolerancias.TOL_LECTURA_FIGURA_HEC14`,
ni `M4.tirante_de_borde`, ni las tablas `HEC14.F3_3` / `HEC14.F3_4` con sus
vistas de calculo). Despues de implementar, sin tocar sus oraculos, se
corrigieron dos erratas del propio test: `Magnitud.simbolo` (no `.nombre`)
y la aritmetica a mano de A-02 (A/D² = 0.2844, no 0.2849).

DE DONDE SALE CADA ORACULO, porque ninguno es la salida del codigo:

  * LOS ANCLAJES DE LA FICHA T8-08, leidos por imagen de la Figura 3.4 por
    otra sesion (la que escribio `_aviso_tirante_de_borde` en T-8) ANTES de
    esta digitalizacion: en descarga libre (TW/D -> 0), las curvas
    KuQ/D^2.5 = 1.0, 2.0 y 3.0 dan yo/D = 0.323, 0.467 y 0.572.
  * EL EJEMPLO RESUELTO IMPRESO de HEC-14, pag. impresa 3-4 (PDF 35): Q =
    1.7 m3/s, TW = 0.610 m, cuatro diametros; la fuente imprime KuQ/D^2.5,
    TW/D, yo/D, A/D² y V = Q/A.
  * LA ARITMETICA A MANO de cada docstring sobre la figura renderizada
    (`pdftoppm -r 200 -f 37 -l 37`), con la interpolacion escrita paso por
    paso.
  * LA FRASE DE LA FUENTE «Since critical depth is larger than brink depth»
    (num. 3.1.3, pag. impresa 3-3): toda curva de trazo continuo tiene que
    quedar bajo el tirante critico mientras el TW este bajo el.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src import servicio
from src import constantes_normativas as CN
from src.modelos import (ControlGobernante, Magnitud, SeccionCircular,
                         SeccionRectangular, TipoMaterial)
from src.modulos import M4_control as M4
from src.modulos import M6_proteccion as M6
from src.modulos.M2_material import catalogo
from src.modulos.M3_hidraulica import resolver_manning
from src.normativa import registro as _registro
from src.normativa.esquema import CeldaSinValor, MetodoDeVerificacion
from src.tolerancias import TOL_LECTURA_FIGURA_HEC14

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_ANCHOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"

# Tolerancias de este archivo, nombradas (CLAUDE.md).
REL_FORMULA = 1e-9            # una formula recomputada en el test
# El ejemplo impreso de la pag. 3-4 da yo/D con DOS cifras: media unidad de
# la ultima, sumada a la tolerancia de lectura de la figura.
ABS_YO_IMPRESO = 5e-3 + TOL_LECTURA_FIGURA_HEC14
# El ejemplo impreso da KuQ/D^2.5, TW/D y V con dos cifras decimales: media
# unidad de la ultima.
ABS_IMPRESO_2_DECIMALES = 5e-3
# A/D² se imprime con cuatro cifras, pero sale de un yo/D de DOS: la
# geometria del programa con ese yo/D reproduce las cuatro cifras a menos de
# 5e-4 (medio centesimo de la tercera).
ABS_AREA_IMPRESA = 5e-4
# Bilineal recomputada a mano con las celdas de la tabla: solo el redondeo.
ABS_INTERPOLACION = 1e-6
# V = Q/A(y_o) con el area por la via canonica (Brent sobre el llenado,
# xtol 1e-10): el recomputo con la formula cerrada del test difiere menos.
REL_AREA_CANONICA = 1e-6
# La aritmetica a mano de un docstring, con la tabla a tres cifras y
# redondeos intermedios: la velocidad a ±0.06 m/s y el d50 a ±0.012 m (con
# V² el error relativo se dobla). No es la incertidumbre de la lectura de la
# figura, que es TOL_LECTURA_FIGURA_HEC14 sobre yo/D.
ABS_V_A_MANO = 0.06
ABS_D50_A_MANO = 0.012
KU_SI = 1.811                 # «Ku = 1.811 for SI», impreso en las dos figuras


# ---------------------------------------------------------------------------
# Apoyo
# ---------------------------------------------------------------------------

def _caudal_circular(q: float, D: float) -> float:
    """El Q (m3/s) que da KuQ/D^2.5 = q."""
    return q * D ** 2.5 / KU_SI


def _caudal_rectangular(q: float, B: float, D: float) -> float:
    """El Q (m3/s) que da KuQ/(B·D^1.5) = q."""
    return q * B * D ** 1.5 / KU_SI


def _borde(Q, seccion, TW):
    critico = M4.tirante_critico(Q, seccion)
    return M4.tirante_de_borde(Q_celda=Q, seccion=seccion, TW=TW,
                               y_c=critico.y_c)


def _area_circular_sobre_D2(y_sobre_D: float) -> float:
    """A/D² de la seccion circular, (θ - sen θ)/8 con θ = 2·acos(1 - 2y/D)."""
    theta = 2 * math.acos(1 - 2 * y_sobre_D)
    return (theta - math.sin(theta)) / 8


def _externos(tmp_path, contenido, **banderas):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, banderas)


def _correr_ancho(tmp_path, extra=None):
    """La corrida ancha de la linea base, con lo que el test le sume."""
    base = json.loads(EXTERNOS_ANCHOS.read_text(encoding="utf-8"))
    for seccion, por_clave in (extra or {}).items():
        base.setdefault("puntos", {}).setdefault(seccion, {}).update(por_clave)
    return servicio.correr(CSV, _externos(tmp_path, base, luz_m=2.75), "perfil")


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


# ===========================================================================
# 1. La transcripcion: dos tablas del registro, leidas por imagen
# ===========================================================================

@pytest.mark.parametrize("id_tabla, figura, pagina_pdf", [
    ("HEC14.F3_3", "Figure 3.3", 36),
    ("HEC14.F3_4", "Figure 3.4", 37),
])
def test_las_figuras_son_tablas_del_registro_leidas_por_imagen(
        id_tabla, figura, pagina_pdf):
    reg = _registro.construir()
    tabla = reg.tabla(id_tabla)
    cita = reg.cita(tabla.cita_id)
    assert cita.fuente_id == "HEC14"
    assert cita.pagina_pdf == pagina_pdf
    assert figura in tabla.titulo_literal
    assert cita.verificado is not None
    assert cita.verificado.metodo is MetodoDeVerificacion.IMAGEN
    # La lectura por imagen se DECLARA, con su tolerancia, en la nota.
    assert "por imagen" in cita.nota.lower()
    assert f"{TOL_LECTURA_FIGURA_HEC14:g}" in cita.nota


def test_la_figura_3_4_tiene_sus_trece_curvas_y_la_3_3_las_suyas():
    """
    Figura 3.4: 0.0 a 6.0 de 0.5 en 0.5 (trece). Figura 3.3: 0.0 a 4.0 de
    0.5 en 0.5 y 5.0, 6.0, 7.0 y 8.0 (trece: no tiene 4.5).
    """
    assert tuple(CN.HEC14_BORDE_CIRCULAR) == pytest.approx(tuple(
        x / 2 for x in range(13)), rel=REL_FORMULA)
    assert tuple(CN.HEC14_BORDE_RECTANGULAR) == pytest.approx(
        tuple(x / 2 for x in range(9)) + tuple(float(x) for x in range(5, 9)),
        rel=REL_FORMULA)
    assert CN.HEC14_BORDE_TW_SOBRE_D == pytest.approx(
        tuple(x / 10 for x in range(11)), rel=REL_FORMULA)


def test_las_vistas_de_calculo_se_derivan_de_la_transcripcion():
    reg = _registro.construir()
    for id_tabla, vista in (("HEC14.F3_3", CN.HEC14_BORDE_RECTANGULAR),
                            ("HEC14.F3_4", CN.HEC14_BORDE_CIRCULAR)):
        tabla = reg.tabla(id_tabla)
        columnas = [c for c in tabla.columnas if c.id.startswith("tw_")]
        for fila in tabla.filas:
            q = fila.valores["curva"]
            esperado = tuple(
                None if isinstance(fila.valores[c.id], CeldaSinValor)
                else fila.valores[c.id] for c in columnas)
            assert vista[q] == esperado, (id_tabla, q)


@pytest.mark.parametrize("q, anclaje", [(1.0, 0.323), (2.0, 0.467),
                                        (3.0, 0.572)])
def test_la_figura_3_4_reproduce_los_anclajes_de_descarga_libre(q, anclaje):
    """
    Los tres anclajes de la ficha T8-08, leidos por OTRA sesion antes de esta
    digitalizacion: en TW/D = 0 la tabla tiene que dar el mismo yo/D dentro
    de la tolerancia de lectura.
    """
    assert CN.HEC14_BORDE_CIRCULAR[q][0] == pytest.approx(
        anclaje, abs=TOL_LECTURA_FIGURA_HEC14)
    D = 1.0
    borde = _borde(_caudal_circular(q, D), SeccionCircular(D), 0.0)
    assert borde.figura == "3.4"
    assert borde.caudal_adimensional == pytest.approx(q, rel=REL_FORMULA)
    assert borde.y_o / D == pytest.approx(anclaje, abs=TOL_LECTURA_FIGURA_HEC14)


# El ejemplo resuelto de la pag. impresa 3-4 (PDF 35), tal como lo imprime:
# (D m, KuQ/D^2.5, TW/D, yo/D, A/D², V m/s).
EJEMPLO_3_4 = (
    (1.050, 2.73, 0.58, 0.64, 0.5308, 2.90),
    (1.200, 1.95, 0.51, 0.55, 0.4426, 2.67),
    (1.350, 1.45, 0.45, 0.47, 0.3627, 2.57),
    (1.500, 1.12, 0.41, 0.42, 0.3130, 2.41),
)


@pytest.mark.parametrize("D, q_impreso, tw_d, yo_d, a_d2, V", EJEMPLO_3_4)
def test_la_figura_3_4_reproduce_el_ejemplo_resuelto_de_la_pag_3_4(
        D, q_impreso, tw_d, yo_d, a_d2, V):
    """
    Q = 1.7 m3/s y TW = 0.610 m. A mano, para la primera fila (D = 1.050):
    KuQ/D^2.5 = 1.811·1.7/1.050^2.5 = 3.0787/1.12972 = 2.725; TW/D = 0.581.
    Columna 0.5: curva 2.5 -> 0.585, 3.0 -> 0.627; columna 0.6: 0.628 y
    0.666. En TW/D = 0.581: 0.6193 y 0.6577; en q = 2.725: 0.6193 + 0.45·
    0.0384 = 0.637, contra 0.64 impreso. Las otras tres: 0.547 (0.55), 0.476
    (0.47) y 0.424 (0.42).
    """
    Q, TW = 1.7, 0.610
    borde = _borde(Q, SeccionCircular(D), TW)
    assert borde.caudal_adimensional == pytest.approx(q_impreso, abs=ABS_IMPRESO_2_DECIMALES)
    assert borde.TW_sobre_D == pytest.approx(tw_d, abs=ABS_IMPRESO_2_DECIMALES)
    assert borde.y_o / D == pytest.approx(yo_d, abs=ABS_YO_IMPRESO)
    # La geometria con que la fuente pasa de yo/D a la velocidad es la misma
    # del programa: con el yo/D IMPRESO, A/D² y V salen como los imprime.
    assert _area_circular_sobre_D2(yo_d) == pytest.approx(a_d2, abs=ABS_AREA_IMPRESA)
    assert Q / (a_d2 * D ** 2) == pytest.approx(V, abs=ABS_IMPRESO_2_DECIMALES)


@pytest.mark.parametrize("q, tw_d, esperado", [
    (2.0, 0.0, 0.382),   # celda leida: curva 2.0, TW/D = 0
    (1.0, 0.1, 0.248),   # celda leida: la curva 1.0 corre sobre la linea 0.25
    (3.5, 0.3, 0.577),
    # Interpolada a mano entre celdas: q = 2.25, TW/D = 0.15.
    # Columna 0.1: 2.0 -> 0.389, 2.5 -> 0.447 -> 0.418; columna 0.2: 0.396 y
    # 0.457 -> 0.4265; en 0.15: 0.42225.
    (2.25, 0.15, 0.42225),
])
def test_la_figura_3_3_da_el_borde_del_marco(q, tw_d, esperado):
    """KuQ/(B·D^1.5): con B = 2.0 m y D = 1.2 m el grupo no es KuQ/D^2.5."""
    B, D = 2.0, 1.2
    seccion = SeccionRectangular(B=B, H=D)
    borde = _borde(_caudal_rectangular(q, B, D), seccion, tw_d * D)
    assert borde.figura == "3.3"
    assert borde.caudal_adimensional == pytest.approx(q, rel=REL_FORMULA)
    assert borde.y_o / D == pytest.approx(esperado, abs=ABS_INTERPOLACION)


@pytest.mark.parametrize("vista, forma", [
    (CN.HEC14_BORDE_CIRCULAR, "circular"),
    (CN.HEC14_BORDE_RECTANGULAR, "rectangular"),
])
def test_las_curvas_de_trazo_continuo_quedan_bajo_el_critico(vista, forma):
    """
    «Since critical depth is larger than brink depth» (num. 3.1.3): toda
    celda de una curva de TRAZO CONTINUO (hasta 3.5 en la circular, hasta 4.0
    en la rectangular) con el TW bajo el critico da yo < yc. Es una prueba de
    la LECTURA: una celda mal leida hacia arriba la rompe. (Las de trazo
    discontinuo no la cumplen en toda la figura, y por eso el codigo las
    contrasta con yc y no las usa por encima.)
    """
    D = 1.0
    techo = 3.5 if forma == "circular" else 4.0
    for q, celdas in vista.items():
        if not 0.0 < q <= techo:
            continue
        if forma == "circular":
            seccion = SeccionCircular(D)
            Q = _caudal_circular(q, D)
        else:
            seccion = SeccionRectangular(B=D, H=D)
            Q = _caudal_rectangular(q, D, D)
        yc = M4.tirante_critico(Q, seccion).y_c
        for tw_d, yo_d in zip(CN.HEC14_BORDE_TW_SOBRE_D, celdas):
            if yo_d is None or not tw_d < yc / D:
                continue
            assert yo_d < yc / D, (forma, q, tw_d, yo_d, yc / D)


def test_cada_celda_crece_con_el_caudal_y_con_el_tw():
    """Las familias no se cruzan: monotonas en q y en TW/D."""
    for vista in (CN.HEC14_BORDE_CIRCULAR, CN.HEC14_BORDE_RECTANGULAR):
        curvas = list(vista.items())
        for (q0, a), (q1, b) in zip(curvas, curvas[1:]):
            for x, y in zip(a, b):
                if x is not None and y is not None:
                    assert y >= x, (q0, q1)
        for q, celdas in curvas:
            leidas = [c for c in celdas if c is not None]
            assert leidas == sorted(leidas), q


# ===========================================================================
# 2. Fuera del dominio de la figura no se extrapola en silencio
# ===========================================================================

def test_por_encima_de_la_ultima_curva_no_hay_lectura():
    """KuQ/D^2.5 = 6.5 > 6.0: la Figura 3.4 no lo cubre."""
    D = 1.0
    seccion = SeccionCircular(D)
    Q = _caudal_circular(6.5, D)
    borde = M4.tirante_de_borde(Q_celda=Q, seccion=seccion, TW=0.1,
                                y_c=0.99 * D)
    assert borde.y_o is None
    assert "6" in borde.motivo and "Figura 3.4" in borde.motivo


def test_un_borde_leido_sobre_el_critico_no_se_usa():
    """
    Curva 6.0 (trazo discontinuo) en TW/D = 0: yo/D = 0.973, y el tirante
    critico de ese caudal es yc/D ≈ 0.955 (Q/(g^0.5·D^2.5) = 6/1.811/3.1321 =
    1.058). La figura da un borde SOBRE el critico, contra la frase de la
    fuente: no hay lectura, y la velocidad se queda en la critica.
    """
    D = 1.0
    borde = _borde(_caudal_circular(6.0, D), SeccionCircular(D), 0.0)
    assert borde.y_o is None
    assert "critico" in borde.motivo


# ===========================================================================
# 3. M4.velocidad_de_salida: el borde en la primera viñeta (T8-08)
# ===========================================================================

def test_a02_horizontal_sale_con_la_velocidad_de_borde(tmp_path):
    """
    El caso del auditor (H2 de la segunda auditoria de T-8): A-02 con el
    barril horizontal, D = 0.90 m, Q = 0.48 m3/s, TW = 0.30 m, sobre
    «Material graduado: grava» con flujo permanente (1.80 m/s).

    A mano: KuQ/D^2.5 = 1.811·0.48/0.76843 = 1.1312; TW/D = 0.3333.
    Columna 0.3: 1.0 -> 0.3605, 1.5 -> 0.4245 -> 0.3773; columna 0.4: 0.404
    y 0.455 -> 0.4174; en TW/D = 0.333: yo/D = 0.3907. A/D² = 0.2844 (θ =
    2·acos(0.2186) = 2.7008), A = 0.2304 m2, V = 2.084 m/s > 1.80: el
    contraste CONCLUYE (antes, 1.739 m/s al critico, no concluia).
    """
    informe = _correr_ancho(tmp_path, {"A-02": {
        "S_conducto": 0, "tipo_terreno_receptor": "graduado_grava",
        "regimen_flujo_descarga": "permanente"}})
    a02 = _punto(informe, "A-02")
    h = a02.resultado.resultado_hidraulico
    D = a02.resultado.seccion.altura
    assert h.control_gobernante is ControlGobernante.SALIDA
    assert h.borde is not None and h.borde.figura == "3.4"
    assert h.borde.y_o / D == pytest.approx(0.3907, abs=TOL_LECTURA_FIGURA_HEC14)
    assert h.borde.y_o < h.y_critico
    A = _area_circular_sobre_D2(h.borde.y_o / D) * D ** 2
    assert h.V_salida.valor == pytest.approx(h.Q_celda_m3s / A, rel=REL_AREA_CANONICA)
    assert h.V_salida.valor == pytest.approx(2.084, abs=ABS_V_A_MANO)
    assert h.V_salida_cota_inferior is False
    assert "Figura 3.4" in h.V_salida.procedencia
    # El tirante de REGISTRO no cambia: sigue siendo el critico.
    assert h.y_salida_m == pytest.approx(h.y_critico, rel=REL_FORMULA)
    p = a02.proteccion
    assert p.velocidad_admisible.concluyente is True
    assert p.velocidad_admisible.supera is True
    assert p.requerida is True
    assert not any("no concluye" in x for x in a02.avisos())
    assert not any("cota inferior" in x for x in a02.avisos())


def test_el_paso_4_3b_imprime_el_borde_y_su_figura(tmp_path):
    informe = _correr_ancho(tmp_path, {"A-02": {"S_conducto": 0}})
    a02 = _punto(informe, "A-02")
    paso = next(x for x in a02.resultado.resultado_hidraulico.pasos
                if x.fundamento_id == "F4.REGIMEN")
    nombres = {m.simbolo for m in paso.sustitucion}
    assert {"y_o", "KuQ/D^2.5", "TW/D"} <= nombres
    assert "HEC14.F3.4" in paso.citas_textuales


# ===========================================================================
# 4. La regla del maximo en la banda de regimen (T8-09)
# ===========================================================================

def test_a01_con_s_0_0056_toma_la_mayor_de_borde_y_erosion(tmp_path):
    """
    El caso medido de la ficha T8-09: A-01 con S = 0.0056, control de salida
    con el TW (0.30 m) bajo el critico; con n_min el tirante normal es
    supercritico. ANTES: V_salida = V_c = 2.412 m/s y d50 de Laushey 0.191 m.
    La ficha escribio «0.191 -> 0.319» con V_erosion = 3.114 m/s, que era la
    de n_min sobre el tirante de n_max; desde VE-2 V_erosion es la de SU
    tirante, 2.960 m/s, y el maximo con la critica daria d50 = 2.960²/30.38
    = 0.288 m.

    CON EL BORDE, que es lo que esta pasada añade, gana el borde. A mano:
    KuQ/D^2.5 = 1.811·1.167/0.76843 = 2.750; TW/D = 0.333. Columna 0.3:
    2.5 -> 0.542, 3.0 -> 0.589 -> 0.5655; columna 0.4: 0.559 y 0.6035 ->
    0.5813; en 0.333: yo/D = 0.5708. A/D² = 0.4633, A = 0.3752 m2, V_borde
    = 3.110 m/s > 2.960: d50 = 3.110²/30.38 = 0.318 m (el 0.319 de la
    ficha, por otro camino).
    """
    informe = _correr_ancho(tmp_path, {"A-01": {"S_conducto": 0.0056}})
    a01 = _punto(informe, "A-01")
    h = a01.resultado.resultado_hidraulico
    assert h.control_gobernante is ControlGobernante.SALIDA
    assert h.V_erosion > h.V_critica_m_s           # la banda
    assert h.V_salida.valor >= h.V_erosion - REL_FORMULA
    assert h.V_salida.valor == pytest.approx(3.110, abs=ABS_V_A_MANO)
    d50 = a01.proteccion.d50_laushey
    assert d50 == pytest.approx(h.V_salida.valor ** 2 / (3.1 * 9.8),
                                rel=REL_FORMULA)
    assert d50 > 0.288 and d50 == pytest.approx(0.318, abs=ABS_D50_A_MANO)
    # El aviso de la banda (T-8) ya no existe: M4 lo resolvio.
    assert not any("n minimo de la regla de doble n" in x
                   for x in a01.avisos())


def _a01_directo(*, S, TW):
    """`velocidad_de_salida` con los objetos de M3/M4 del tubo de A-01."""
    seccion = SeccionCircular(0.9)
    Q = 1.167
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    critico = M4.tirante_critico(Q, seccion)
    normal = resolver_manning(seccion, Q, S, material)
    return M4.velocidad_de_salida(
        Q_celda=Q, seccion=seccion, TW=TW, critico=critico, normal=normal,
        control=ControlGobernante.SALIDA), critico, normal


def test_en_la_banda_gana_v_erosion_cuando_el_borde_es_menor():
    """
    Mismo tubo con TW = 0.55 m (TW/D = 0.611 < yc/D = 0.711): el borde sube
    hacia el TW y su velocidad baja. A mano: columna 0.6: 2.5 -> 0.628, 3.0
    -> 0.6655 -> 0.6468; columna 0.7: 0.690 y 0.711 -> 0.7005; en 0.611:
    0.6527. A/D² = 0.5431, A = 0.4399 m2, V_borde = 2.653 < V_erosion =
    2.960: rige V_erosion, y lo dice.
    """
    salida, critico, normal = _a01_directo(S=0.0056, TW=0.55)
    assert normal.geometria.y > critico.y_c          # n_max: subcritico
    assert normal.geometria_erosion.y < critico.y_c  # n_min: supercritico
    assert salida.V_salida.valor == pytest.approx(normal.V_erosion,
                                                  rel=REL_FORMULA)
    assert salida.borde.y_o is not None
    assert salida.cota_inferior is False
    assert "V_erosion" in salida.V_salida.procedencia
    assert "mayor" in salida.V_salida.procedencia.lower()


def test_con_pendiente_pronunciada_en_n_max_la_figura_no_aplica():
    """
    S = 0.02 con el control de salida forzado: con n_max el tirante normal ya
    queda bajo el critico, y la Figura 3.4 es «on Horizontal and Mild
    Slopes». No se lee; la critica queda bajo V_erosion y rige V_erosion.
    """
    salida, critico, normal = _a01_directo(S=0.02, TW=0.30)
    assert normal.geometria.y < critico.y_c
    assert salida.borde.y_o is None
    assert "Mild Slopes" in salida.borde.motivo
    assert salida.V_salida.valor == pytest.approx(normal.V_erosion,
                                                  rel=REL_FORMULA)
    assert salida.cota_inferior is False


# ===========================================================================
# 5. M6: el contraste vuelve a concluir donde hay numero
# ===========================================================================

def test_los_avisos_de_t8_ya_no_existen_como_estaban():
    """`_aviso_banda_de_regimen` se retira: M4 aplica la regla del maximo."""
    assert not hasattr(M6, "_aviso_banda_de_regimen")


def test_con_la_cota_inferior_declarada_por_m4_el_contraste_no_concluye():
    """
    Lo que queda de T8-08: fuera del dominio de la figura M4 conserva la
    critica y lo DICE (`V_salida_cota_inferior`); M6 no concluye y avisa con
    el motivo de M4.
    """
    from dataclasses import replace
    from src.modelos import ResultadoHidraulico, TiranteDeBorde
    base = ResultadoHidraulico(
        y_normal=0.5, y_critico=0.6, V_erosion=1.0, V_sedimentacion=0.8,
        Q=1.0, S=0.001, HW_entrada=1.0, HW_salida=1.2,
        control_gobernante=ControlGobernante.SALIDA, TW_m=0.1,
        y_salida_m=0.6,
        V_salida=Magnitud("V_salida", 1.0, "m/s", "Q / A(y_c) (dato del test)"))
    sin_lectura = replace(
        base, V_salida_cota_inferior=True,
        borde=TiranteDeBorde(figura="3.4", caudal_adimensional=6.5,
                             TW_sobre_D=0.11, y_o=None,
                             motivo="fuera de la Figura 3.4 (dato del test)"))
    p = M6.proteccion_salida(V=sin_lectura.V_salida, resultado=sin_lectura,
                             seccion=SeccionCircular(1.0),
                             tipo_terreno="grava_fina",
                             regimen_flujo="intermitente")
    assert p.velocidad_admisible.concluyente is False
    assert any("fuera de la Figura 3.4 (dato del test)" in x
               for x in p.avisos)
    con_borde = M6.proteccion_salida(V=base.V_salida, resultado=base,
                                     seccion=SeccionCircular(1.0),
                                     tipo_terreno="grava_fina",
                                     regimen_flujo="intermitente")
    assert con_borde.velocidad_admisible.concluyente is True
