"""
tests/test_t8_proteccion.py
===========================
Aceptacion de T-8 de la cadena T: la Fase 6 pasa a ser de verdad la
proteccion de ENTRADA y de SALIDA, con la socavacion local a la salida.
Cierra INF-3.3.7 (la cadena lo cita «INF-3.3 protección») e INF-5.1.13 (la
cadena lo cita «INF-5.1.11 (M6 sin protección de entrada)»).

DE DONDE SALE CADA ORACULO, porque ninguno es la salida del codigo:

  * los EJEMPLOS RESUELTOS de la fuente, con su pagina: el apron SI de HEC-14
    (pags. impresas 10-18 y 10-19, PDF 219 y 220) y su gemelo en unidades
    inglesas convertido a SI; la hoya en suelo no cohesivo (pags. 5-4 y 5-5,
    PDF 57 y 58) y en suelo cohesivo (pags. 5-8 y 5-9, PDF 61 y 62); el
    tirante equivalente y el Froude del ejemplo de la poza de impacto USBR
    tipo VI (pag. 9-40, PDF 197). Se comparan con `REL_EJEMPLO_IMPRESO`: la
    fuente imprime dos o tres cifras y redondea los intermedios (Rc = 0.114
    por 0.11425; (t/316) = 0.095 y, en el cohesivo, 0.09).
  * la ARITMETICA ESCRITA en el test, paso por paso, independiente de la
    formula cerrada del codigo (lecciones de las auditorias del lote 1);
  * la TRANSCRIPCION de las tablas, leida otra vez del PDF por quien escribio
    el test (Tabla Nº 11 del Manual, Tablas 5.2, 5.3 y 10.1 de HEC-14,
    Tabla 511-06 de EG-2013).

ROJO MEDIDO, NO ESCRITO PRIMERO, y se declara: este archivo se escribio
despues del codigo (el prompt se retomo a medias de otra sesion). Se midio
contra el arbol base `ad5cb97`, donde no se puede ni importar: las funciones
publicas de M6 que nombra no existian. Con marcadores para esos nombres: 57
rojos, 5 errores y 1 verde (la guardia de las tres advertencias). La mutacion
de M6 contra este archivo, con el arnes de EXT-11: 337 de 375 muertos (ficha
T8-06 de `docs/decisiones_diferidas.md`). El bloque 10 lo dejo el auditor
adversarial de T-8 (tres refutados y cinco ajustes; ver cada test).

REESCRITO A LA VERDAD NUEVA EL 2026-11-12, y se declara que cambio y por que
(segunda auditoria de T-8 y decisiones del dueño de esa fecha; la aceptacion
de la pasada esta en `tests/test_t8_correcciones.py`):

  * RIGE LA ENVOLVENTE. 'regla_espesor_longitud_proteccion_salida' vale
    «envolvente_hec14»: la piedra es el mayor de Laushey y de la Ec. (10.4),
    y el espesor y la longitud los mayores de lo adoptado y de la Tabla 10.1.
    Los tests que fijaban «espesor = 1.75·d50» y «longitud = 5.0 m» sobre la
    corrida por defecto los fijan ahora sobre `corrida_manual`, que declara
    la regla anterior y tiene que dar EXACTAMENTE aquellos numeros; sobre la
    corrida por defecto fijan lo nuevo (A-01 y A-02: 0.770 m y 5.40 m).
  * «SIN ENROCADO» NO ES UNA CONCLUSION. Bajo la admisible de la Tabla Nº 11
    la proteccion se calcula y se mantiene; los tests que esperaban `d50 is
    None` y las celdas vacias del resumen esperan el numero y el aviso.
  * LA DURACION POR CRITERIO SON 360 MIN [A], no 30 [C]. Los ejemplos
    resueltos de HEC-14 usan t = 30 min y lo DECLARAN (`duracion_pico_min`).
  * LA NOTA (5) b de la Tabla 511-06 vale solo en la columna «>50».
  * EL LIMITE DEL APRON es 1.524 m (60 in), no 1.500.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import servicio
from src.constantes_fisicas import G
from src.constantes_normativas import (
    G_LAUSHEY, HEC14_SOCAVACION_CH, HEC14_SOCAVACION_CS, HEC14_TABLA_10_1,
    LAUSHEY_K, V_MAX_NO_REVESTIDOS)
from src.modelos import (
    ControlGobernante, DatoFaltanteError, DatoInvalidoError, Magnitud,
    MOTIVO_METODO_NO_EVALUABLE, MOTIVO_METODO_NO_EVALUABLE_HEC14,
    MaterialLecho, MetodoNoEvaluableError, ORIGEN_SOCAVACION_DECLARADA,
    ORIGEN_SOCAVACION_ESTIMADA, ORIGEN_SOCAVACION_SIN_DATO, SeccionCircular,
    SeccionRectangular, TipoDeVeredicto)
from src.modulos import M11_reporte as M11
from src.modulos import M6_proteccion as M6
from src.normativa import registro as _registro
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_ANCHOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"

# Tolerancias de este archivo, nombradas (CLAUDE.md).
REL_EJEMPLO_IMPRESO = 1e-2   # la fuente imprime 2-3 cifras y redondea intermedios
REL_FORMULA = 1e-9           # una formula recomputada a mano en el test
REL_ARITMETICA = 1e-4        # la aritmetica escrita con cuatro o cinco cifras
REL_ARITMETICA_CORTA = 1e-3  # la aritmetica escrita con tres o cuatro cifras

M_POR_FT = 0.3048            # exacto por definicion
FT3_POR_M3 = 1 / M_POR_FT ** 3


def _V(valor: float) -> Magnitud:
    return Magnitud("V_salida", valor, "m/s", "dato del test")


def _externos(tmp_path, contenido, **banderas):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, banderas)


def _correr_ancho(tmp_path, extra=None):
    """La corrida ancha de la linea base, con lo que el test le sume."""
    base = json.loads(EXTERNOS_ANCHOS.read_text(encoding="utf-8"))
    for seccion, por_clave in (extra or {}).items():
        if seccion == "globales":
            base.setdefault("globales", {}).update(por_clave)
        else:
            base.setdefault("puntos", {}).setdefault(seccion, {}).update(por_clave)
    return servicio.correr(CSV, _externos(tmp_path, base, luz_m=2.75), "perfil")


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


@pytest.fixture(scope="module")
def corrida_base(tmp_path_factory):
    """La corrida ancha SIN ningun dato de T-8, con la regla del archivo."""
    return _correr_ancho(tmp_path_factory.mktemp("base"))


CRITERIO_REGLA = "regla_espesor_longitud_proteccion_salida"


def _con_regla(regla, funcion):
    """Ejecuta `funcion()` con la regla declarada en caliente, y la repone."""
    ca.establecer_valor_dinamico(CRITERIO_REGLA, regla)
    try:
        return funcion()
    finally:
        ca.quitar_valor_dinamico(CRITERIO_REGLA)


@pytest.fixture(scope="module")
def corrida_manual(tmp_path_factory):
    """
    La misma corrida con la regla «manual» declarada: la conducta de antes
    de la decision del 2026-11-12, numero por numero.
    """
    return _con_regla("manual",
                      lambda: _correr_ancho(tmp_path_factory.mktemp("manual")))


# ===========================================================================
# 0 · Las fuentes: capitulos reales de HEC-14 y la errata de la cadena
# ===========================================================================

def test_hec14_la_socavacion_es_el_capitulo_5_y_el_apron_el_10():
    """
    La cadena T dice «cap. 3 (socavacion a la salida)» y «cap. 4-5 (velocidad
    de salida y disipadores internos)». El ejemplar dice otra cosa (T-0 lo
    midio; aqui se fija sobre las citas que T-8 escribe): la hoya es el
    Capitulo 5, la velocidad de salida el 3 y el apron el 10.2.
    """
    reg = _registro.construir()
    for cita_id in ("HEC14.5.1#EC_5_1", "HEC14.5.2#EC_5_2", "HEC14.5.1.2#T30",
                    "HEC14.5.1.3#CABEZAL", "HEC14.5.1.4#T5_2"):
        c = reg.cita(cita_id)
        assert c.numeral.startswith("5") and c.pagina_impresa.startswith("5-")
    assert reg.cita("HEC14.3#CONTINUIDAD").pagina_impresa == "3-1"
    for cita_id in ("HEC14.10.2#EC_10_4", "HEC14.10.2#T10_1"):
        assert reg.cita(cita_id).numeral.startswith("10.2")
    # Paginacion por capitulo de la fuente: impresa «c-n» -> PDF base[c] + n.
    for cita_id, pdf in (("HEC14.5.1#EC_5_1", 54), ("HEC14.10.2#T10_1", 219),
                         ("HEC14.3#CONTINUIDAD", 32), ("HEC14.D#SOLO_VELOCIDAD", 281)):
        assert reg.cita(cita_id).pagina_pdf == pdf


def test_las_tablas_de_hec14_son_las_del_pdf():
    """Transcripcion releida del PDF (pags. impresas 5-3 y 10-18)."""
    # Table 5.2 (Ch) y 5.3 (Cs): filas y columna de profundidad.
    assert [f[0] for f in HEC14_SOCAVACION_CH] == \
        pytest.approx([0.0, 1.0, 2.0, 4.0], abs=ABS_CERO)
    assert [f[1]["profundidad"] for f in HEC14_SOCAVACION_CH] == \
        pytest.approx([1.00, 1.22, 1.26, 1.34], rel=REL_FORMULA)
    assert [f[1]["longitud"] for f in HEC14_SOCAVACION_CH] == \
        pytest.approx([1.00, 0.73, 0.73, 0.73], rel=REL_FORMULA)
    assert [f[0] for f in HEC14_SOCAVACION_CS] == \
        pytest.approx([0.0, 2.0, 5.0, 7.0], abs=ABS_CERO)
    assert [f[1]["profundidad"] for f in HEC14_SOCAVACION_CS] == \
        pytest.approx([1.00, 1.03, 1.08, 1.12], rel=REL_FORMULA)
    # Table 10.1: clase, D50 (m), longitud en D, profundidad en D50.
    assert [f[0] for f in HEC14_TABLA_10_1] == [1, 2, 3, 4, 5, 6]
    filas_del_pdf = ((0.125, 4.0, 3.5), (0.150, 4.0, 3.3), (0.250, 5.0, 2.4),
                     (0.350, 6.0, 2.2), (0.500, 7.0, 2.0), (0.550, 8.0, 2.0))
    for fila, del_pdf in zip(HEC14_TABLA_10_1, filas_del_pdf):
        assert fila[1:] == pytest.approx(del_pdf, rel=REL_TRANSPORTE)


def test_la_tabla_11_del_manual_es_la_del_pdf():
    """Manual de Hidrologia, Tabla Nº 11, pag. impresa 77 (PDF 80): 13 filas."""
    assert len(V_MAX_NO_REVESTIDOS) == 13
    t11 = {k: (v["intermitente"], v["permanente"])
           for k, v in V_MAX_NO_REVESTIDOS.items()}
    assert t11["arena_fina_no_coloidal"] == pytest.approx((0.75, 0.75), rel=REL_TRANSPORTE)
    assert t11["ceniza_volcanica"] == pytest.approx((1.20, 1.00), rel=REL_TRANSPORTE)
    assert t11["arcilla_dura_coloidal"] == pytest.approx((1.80, 1.40), rel=REL_TRANSPORTE)
    assert t11["graduado_grava_a_piedras_mayor_20cm"] == pytest.approx((3.00, 2.40), rel=REL_TRANSPORTE)
    # Ninguna admisible permanente supera a la intermitente.
    assert all(p <= i for i, p in t11.values())


# ===========================================================================
# 1 · Laushey se conserva: mismos numeros que antes de T-8
# ===========================================================================

def test_sin_datos_nuevos_la_salida_da_los_numeros_de_antes(corrida_manual,
                                                            corrida_base):
    """
    Con la regla «manual»: d50 = V^2/(3.1·9.8), espesor = 1.75·d50 y longitud
    5.0 m, la conducta de antes de T-8, recomputada a mano sobre la V_salida
    de cada punto. Con la regla del archivo (la envolvente) el d50 de Laushey
    es el MISMO --se publica siempre-- y en estos dos puntos es ademas el que
    rige, porque la Ec. (10.4) pide menos piedra.
    """
    for id_punto in ("A-01", "A-02"):
        p = _punto(corrida_manual, id_punto).proteccion
        d50 = p.V ** 2 / (3.1 * 9.8)
        assert p.d50 == pytest.approx(d50, rel=REL_FORMULA)
        assert p.espesor == pytest.approx(1.75 * d50, rel=REL_FORMULA)
        assert p.longitud == pytest.approx(5.0, rel=REL_FORMULA)
        assert p.requerida is None and not p.rige_la_envolvente
        q = _punto(corrida_base, id_punto).proteccion
        assert q.d50_laushey == pytest.approx(d50, rel=REL_FORMULA)
        assert q.d50 == pytest.approx(d50, rel=REL_FORMULA)
        assert q.rige_la_envolvente
    assert LAUSHEY_K == pytest.approx(3.1, rel=REL_TRANSPORTE) and G_LAUSHEY == pytest.approx(9.8, rel=REL_TRANSPORTE)


def test_las_tres_advertencias_de_siempre_viajan_con_el_d50(corrida_base,
                                                            corrida_manual):
    """
    Tres advertencias siempre. Las dos primeras no cambian; la del ALCANCE
    dice cual de las dos reglas rigio (con la envolvente, «el d50 que rige
    sale del Manual» seria falso donde HEC-14 pide mas piedra).
    """
    manual = _punto(corrida_manual, "A-01").proteccion
    assert manual.advertencias == M6.ADVERTENCIAS_PROTECCION_SALIDA
    p = _punto(corrida_base, "A-01").proteccion
    assert p.advertencias == M6.ADVERTENCIAS_PROTECCION_SALIDA_ENVOLVENTE
    assert len(p.advertencias) == 3
    assert p.advertencias[:2] == manual.advertencias[:2]
    assert "rige la ENVOLVENTE" in p.advertencias[2]


def test_proteccion_salida_solo_con_V_no_añade_pasos_de_HEC14():
    p = M6.proteccion_salida(V=_V(2.0))
    assert p.d50 == pytest.approx(4.0 / (3.1 * 9.8), rel=REL_FORMULA)
    assert p.apron is None and p.froude is None
    assert [x.codigo for x in p.pasos] == ["6.1", "6.2"]


# ===========================================================================
# 2 · Froude a la salida (HEC-14 num. 10.1.1)
# ===========================================================================

def test_froude_reproduce_el_ejemplo_de_hec14_pag_9_40():
    """
    Poza USBR tipo VI, ejemplo SI (pag. impresa 9-40, PDF 197): tubo de
    1.219 m, Q = 8.5 m3/s, Vo = 12.192 m/s -> A = Q/Vo = 0.697 m2,
    ye = (A/2)^0.5 = 0.590 m, Fr = Vo/(g·ye)^0.5 = 5.07.
    """
    f = M6.froude_salida(V=_V(12.192), Q_celda=8.5,
                         seccion=SeccionCircular(1.219))
    assert f.A == pytest.approx(0.697, rel=REL_EJEMPLO_IMPRESO)
    assert f.y_equivalente == pytest.approx(0.590, rel=REL_EJEMPLO_IMPRESO)
    assert f.Fr == pytest.approx(5.07, rel=REL_EJEMPLO_IMPRESO)
    # Sin tirante de salida ni critico el regimen NO se rotula: Fr_e es el
    # parametro de HEC-14 y no lo indica (auditoria de T-8, hallazgo 2).
    assert f.supercritico is None


def test_froude_a_mano_circular_y_rectangular():
    # Circular: Q = 1.0, V = 2.0 -> A = 0.5 m2; ye = (0.5/2)^0.5 = 0.5 m;
    # Fr = 2.0 / (9.81·0.5)^0.5 = 2.0 / 2.21472 = 0.90306.
    f = M6.froude_salida(V=_V(2.0), Q_celda=1.0, seccion=SeccionCircular(1.2))
    assert f.y_equivalente == pytest.approx(0.5, rel=REL_FORMULA)
    assert f.Fr == pytest.approx(0.90306, rel=REL_ARITMETICA)
    assert f.supercritico is None
    # Marco de B = 2.0 m: ye = yo = A/B = 0.25 m; Fr = 2/(9.81·0.25)^0.5 = 1.27713.
    r = M6.froude_salida(V=_V(2.0), Q_celda=1.0,
                         seccion=SeccionRectangular(B=2.0, H=1.5))
    assert r.y_equivalente == pytest.approx(0.25, rel=REL_FORMULA)
    assert r.Fr == pytest.approx(1.27713, rel=REL_ARITMETICA)
    assert r.paso.codigo == "6.3" and "HEC14.3#CONTINUIDAD" in r.paso.citas_textuales


def test_froude_exige_una_velocidad_con_procedencia():
    with pytest.raises(TypeError):
        M6.froude_salida(V=2.0, Q_celda=1.0, seccion=SeccionCircular(1.0))
    with pytest.raises(DatoInvalidoError):
        M6.froude_salida(V=_V(float("nan")), Q_celda=1.0,
                         seccion=SeccionCircular(1.0))


# ===========================================================================
# 3 · Apron de enrocado (HEC-14 Sec. 10.2)
# ===========================================================================

def test_apron_reproduce_el_ejemplo_SI_de_hec14():
    """
    Pags. impresas 10-18 y 10-19: Q = 2.33 m3/s, D = 1.5 m, TW = 0.5 m.
    TW/D = 0.33 < 0.4 -> TW = 0.6 m. Aritmetica escrita:
        Q/(g^0.5·D^2.5) = 2.33/(3.13209·2.75568) = 0.26996
        0.26996^(4/3) = 0.17447
        D50 = 0.2·1.5·0.17447·(1.5/0.6) = 0.13085 m  (la fuente: 0.13 m)
    Clase 2 (D50 = 0.15 m): L = 4·1.5 = 6 m, profundidad 3.3·0.15 = 0.50 m,
    ancho al final 3·1.5 + (2/3)·6 = 8.5 m.
    """
    a = M6.apron_hec14(Q_celda=2.33, seccion=SeccionCircular(1.5), TW=0.5,
                       y_salida=None, y_critico=0.8)
    assert a.TW_acotado and a.TW_de_calculo == pytest.approx(0.6, rel=REL_FORMULA)
    assert a.D50_requerido == pytest.approx(0.13085, rel=REL_ARITMETICA)
    assert a.D50_requerido == pytest.approx(0.13, rel=REL_EJEMPLO_IMPRESO)
    assert a.clase == 2 and a.D50_clase == pytest.approx(0.15, rel=REL_TRANSPORTE)
    assert a.longitud == pytest.approx(6.0, rel=REL_FORMULA)
    # La fuente imprime «3.3 (0.15) = 0.50 m»: 0.495 redondeado hacia arriba.
    assert a.espesor == pytest.approx(3.3 * 0.15, rel=REL_FORMULA)
    assert a.ancho_final == pytest.approx(8.5, rel=REL_FORMULA)
    assert not a.ajustado_por_supercritico
    assert [x.codigo for x in a.pasos] == ["6.5", "6.6"]


def test_apron_es_adimensional_el_ejemplo_ingles_da_lo_mismo_en_SI():
    """
    Ejemplo CU (pag. 10-19): Q = 85 ft3/s, D = 5 ft, TW = 1.6 ft -> 0.43 ft.
    La Ec. (10.4) es adimensional: convertido a SI (0.3048 m/ft) y llevado a
    escala geometrica λ = 0.9 (longitudes por λ, caudal por λ^2.5) el D50
    sale 0.43 ft · 0.3048 · λ. La escala hace falta porque D = 5 ft = 1.524 m
    queda justo sobre el limite de 1500 mm de la Tabla 1.1 (la fuente lo
    imprime «1500 mm (60 in)»: el SI es la conversion redondeada).
    """
    lam = 0.9
    a = M6.apron_hec14(Q_celda=85 / FT3_POR_M3 * lam ** 2.5,
                       seccion=SeccionCircular(5 * M_POR_FT * lam),
                       TW=1.6 * M_POR_FT * lam, y_salida=None, y_critico=1.0)
    assert a.D50_requerido / (M_POR_FT * lam) == pytest.approx(
        0.43, rel=REL_EJEMPLO_IMPRESO)


def test_apron_con_flujo_supercritico_ajusta_el_diametro():
    """
    Ec. (10.5): D' = (D + yn)/2. D = 1.0, yn = 0.4 < yc = 0.6 -> D' = 0.7 m;
    el TW = 0.5 m queda dentro de [0.4·0.7, 1.0·0.7] = [0.28, 0.70].
    D50 = 0.2·0.7·[1.0/(3.13209·0.7^2.5)]^(4/3)·(0.7/0.5):
        0.7^2.5 = 0.409963; 3.13209·0.409963 = 1.284043;
        1.0/1.284043 = 0.778790; 0.778790^(4/3) = 0.716518;
        D50 = 0.2·0.7·0.716518·1.4 = 0.140438 m.
    La longitud de la Tabla 10.1 usa D (la altura real), no D'.
    """
    a = M6.apron_hec14(Q_celda=1.0, seccion=SeccionCircular(1.0), TW=0.5,
                       y_salida=0.4, y_critico=0.6)
    assert a.ajustado_por_supercritico
    assert a.D_de_calculo == pytest.approx(0.7, rel=REL_FORMULA)
    assert not a.TW_acotado
    assert a.D50_requerido == pytest.approx(0.140438, rel=REL_ARITMETICA)
    # 0.140 m <= 0.150 m: clase 2, longitud 4·D = 4·1.0 m (D, no D').
    assert a.clase == 2 and a.longitud == pytest.approx(4.0 * 1.0, rel=REL_TRANSPORTE)
    assert "HEC14.10.2#EC_10_5" in a.pasos[0].citas_textuales


@pytest.mark.parametrize("seccion, TW, celdas, motivo", [
    (SeccionRectangular(B=1.5, H=1.0), 0.5, 1, "marco"),
    (SeccionCircular(1.0), 1.2, 1, "Figura 10.3"),
    (SeccionCircular(1.0), 0.5, 2, "barriles"),
])
def test_apron_fuera_de_su_rango_no_se_evalua(seccion, TW, celdas, motivo):
    """
    «recommended for circular culverts»; TW > 1.0D manda a la Figura 10.3.
    El estado se rotula con HEC-14, no con el «HDS-5 3.24» por defecto, que
    aqui seria una cita falsa (auditor de T-8, punto 7).
    """
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.apron_hec14(Q_celda=1.0, seccion=seccion, TW=TW, y_salida=None,
                       y_critico=0.5, numero_celdas=celdas)
    assert motivo in str(e.value)
    assert str(e.value).startswith(MOTIVO_METODO_NO_EVALUABLE_HEC14)
    assert MOTIVO_METODO_NO_EVALUABLE not in str(e.value)


def test_apron_que_no_cabe_en_la_tabla_lo_dice_y_nombra_la_lamina_04():
    """Un D50 mayor que 0.55 m no tiene clase: aviso, y la alternativa del Manual."""
    a = M6.apron_hec14(Q_celda=6.0, seccion=SeccionCircular(1.0), TW=0.4,
                       y_salida=None, y_critico=0.9)
    assert a.clase is None and a.longitud is None
    assert "MC_HHD.LAMINA_04" in a.pasos[1].citas_textuales
    avisos = M6._avisos_del_contraste(a, d50=0.3, espesor=0.5, longitud=5.0)
    assert any("Lámina Nº 04" in x for x in avisos)


def test_el_contraste_avisa_cuando_lo_adoptado_queda_corto(corrida_manual,
                                                           corrida_base):
    """
    A-01 del fixture: HEC-14 da clase 4 (L = 6·0.9 = 5.4 m, profundidad
    2.2·0.35 = 0.77 m). Con la regla «manual» el proyecto adopta 5.0 m y
    1.75·d50, y la corrida avisa las dos cosas, que llegan a
    `InformePunto.avisos()`. Con la envolvente (el archivo) lo que rige ya
    no queda corto, y esos dos avisos callan.
    """
    assert not any("longitud adoptada (5.00 m" in x or "espesor adoptado" in x
                   for x in _punto(corrida_base, "A-01").avisos())
    a01 = _punto(corrida_manual, "A-01")
    apron = a01.proteccion.apron
    assert apron.clase == 4
    assert apron.longitud == pytest.approx(6 * 0.9, rel=REL_FORMULA)
    assert apron.espesor == pytest.approx(2.2 * 0.35, rel=REL_FORMULA)
    avisos = a01.avisos()
    assert any("longitud adoptada (5.00 m" in x for x in avisos)
    assert any("espesor adoptado" in x for x in avisos)


def test_conducto_mayor_de_1500_mm_es_limite_del_apron():
    """
    Nota 8 de la Tabla 1.1 «Energy Dissipators and Limitations»: el apron
    vale para conductos de hasta «1500 mm (60 in)» de alto. Es un LIMITE,
    como los otros, y no un aviso (auditoria de T-8, hallazgo 9). De las dos
    cifras rige 60 in = 1.524 m (segunda auditoria, H5).
    """
    with pytest.raises(MetodoNoEvaluableError, match="60 in") as e:
        M6.apron_hec14(Q_celda=2.0, seccion=SeccionCircular(1.8), TW=0.8,
                       y_salida=None, y_critico=0.7)
    assert e.value.rotulo == MOTIVO_METODO_NO_EVALUABLE_HEC14
    a = M6.apron_hec14(Q_celda=2.0, seccion=SeccionCircular(1.5), TW=0.8,
                       y_salida=None, y_critico=0.7)
    assert a.D50_requerido > 0


# ===========================================================================
# 4 · Velocidad admisible del cauce (Manual, Tabla Nº 11)
# ===========================================================================

def test_bajo_la_admisible_la_proteccion_se_mantiene_y_se_dice():
    """
    Grava gruesa, flujo intermitente: 2.40 m/s. Con V = 2.0 el terreno la
    resistiria segun la tabla: `requerida` False y el paso 6.4 CUMPLE. Hasta
    la decision del dueño del 2026-11-12 eso dejaba la salida «sin enrocado»
    (d50 None); ahora la proteccion se calcula y se mantiene, y el aviso dice
    que suprimirla queda sujeto a inspeccion de campo. d50 = 4/30.38.
    """
    p = M6.proteccion_salida(V=_V(2.0), tipo_terreno="graduado_grava_gruesa",
                             regimen_flujo="intermitente")
    assert p.requerida is False
    assert p.d50 == pytest.approx(4.0 / (3.1 * 9.8), rel=REL_FORMULA)
    assert p.espesor is not None and p.longitud is not None
    assert len(p.advertencias) == 3
    assert any("se MANTIENE" in x and "inspeccion de campo" in x
               for x in p.avisos)
    assert p.velocidad_admisible.V_admisible == pytest.approx(2.40, rel=REL_TRANSPORTE)
    assert p.velocidad_admisible.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE


def test_sobre_la_admisible_se_avisa_y_se_dimensiona():
    p = M6.proteccion_salida(V=_V(2.0), tipo_terreno="arena_fina_no_coloidal",
                             regimen_flujo="permanente")
    assert p.requerida is True
    assert p.d50 == pytest.approx(4.0 / (3.1 * 9.8), rel=REL_FORMULA)
    assert p.velocidad_admisible.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert any("0.75 m/s" in x for x in p.avisos)


def test_sin_terreno_se_dimensiona_como_antes_y_se_avisa():
    p = M6.proteccion_salida(V=_V(2.0))
    assert p.requerida is None and p.d50 is not None
    assert any("tipo_terreno_receptor" in x for x in p.avisos)
    # La consecuencia es la de la SALIDA, no la de la entrada.
    aviso = next(x for x in p.avisos if "tipo_terreno_receptor" in x)
    assert "el enrocado se dimensiona igual" in aviso
    assert "la entrada necesita" not in aviso


def test_un_terreno_que_no_es_fila_de_la_tabla_es_invalido():
    with pytest.raises(DatoInvalidoError):
        M6.velocidad_admisible_del_cauce(V=_V(1.0), tipo_terreno="roca",
                                         regimen_flujo="intermitente")
    with pytest.raises(DatoInvalidoError):
        M6.velocidad_admisible_del_cauce(V=_V(1.0), tipo_terreno="grava_fina",
                                         regimen_flujo="estacional")


# ===========================================================================
# 5 · Filtro (EG-2013 num. 511.08, Tabla 511-06)
# ===========================================================================

@pytest.mark.parametrize("pasa, columna, permitividad, abertura", [
    (10.0, "< 15", 0.7, 0.43),
    (15.0, "15-50", 0.2, 0.25),
    (50.0, "15-50", 0.2, 0.25),
    (60.0, "> 50", 0.1, 0.22),
])
def test_el_filtro_elige_la_columna_de_la_tabla_511_06(pasa, columna,
                                                       permitividad, abertura):
    f = M6.requisito_de_filtro(pasa_200_pct=pasa)
    assert f.columna == columna
    assert f.permitividad_min_s1 == pytest.approx(permitividad, rel=REL_TRANSPORTE)
    assert f.abertura_aparente_max_mm == pytest.approx(abertura, rel=REL_TRANSPORTE)
    assert f.paso.codigo == "6.7"


def test_la_nota_5b_lleva_la_abertura_a_030_en_suelo_cohesivo_con_IP_mayor_7():
    assert M6.requisito_de_filtro(pasa_200_pct=60.0, indice_plasticidad=10.0
                                  ).abertura_aparente_max_mm == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert M6.requisito_de_filtro(pasa_200_pct=60.0, indice_plasticidad=5.0
                                  ).abertura_aparente_max_mm == pytest.approx(0.22, rel=REL_TRANSPORTE)
    # TERCERA LECTURA, y la que queda (segunda auditoria de T-8, H4; decision
    # del dueño del 2026-11-12): la primera de T-8 daba 0.25 en «15-50», el
    # primer auditor la llevo a 0.30 en las tres columnas, y el segundo midio
    # que eso RELAJA la celda. La nota (5) b vale donde la celda lleva la
    # llamada, «>50»; en las otras dos rige la celda.
    assert M6.requisito_de_filtro(pasa_200_pct=30.0, indice_plasticidad=10.0
                                  ).abertura_aparente_max_mm == pytest.approx(0.25, rel=REL_TRANSPORTE)
    assert M6.requisito_de_filtro(pasa_200_pct=10.0, indice_plasticidad=10.0
                                  ).abertura_aparente_max_mm == pytest.approx(0.43, rel=REL_TRANSPORTE)


def test_sin_el_pasante_el_filtro_se_declara_y_no_se_dimensiona():
    f = M6.requisito_de_filtro()
    assert f.columna is None and f.paso is None
    assert "pasa_200_pct" in f.texto and "Lámina Nº 05" in f.texto
    with pytest.raises(DatoInvalidoError):
        M6.requisito_de_filtro(pasa_200_pct=120.0)


# ===========================================================================
# 6 · Proteccion de la ENTRADA (INF-5.1.13)
# ===========================================================================

def test_la_fase_6_tiene_proteccion_de_entrada(corrida_base):
    """
    A-01 corre bajo control de ENTRADA: la velocidad en la boca es la critica
    del paso 4.2 (HDS-5 num. 3.1.3), Q_celda / A_c. El revestimiento es el
    del criterio [A] 'tipo_proteccion_entrada', y la embocadura, la adoptada.
    """
    a01 = _punto(corrida_base, "A-01")
    r = a01.resultado.resultado_hidraulico
    assert r.control_gobernante is ControlGobernante.ENTRADA
    e = a01.proteccion_entrada
    assert e.V_entrada == pytest.approx(r.V_critica_m_s, rel=REL_FORMULA)
    assert e.revestimiento == ca.valor("tipo_proteccion_entrada")
    assert e.tipo_embocadura == M6.EMBOCADURA_CABEZAL_RECTO
    assert e.elementos == M6.EMBOCADURAS[M6.EMBOCADURA_CABEZAL_RECTO]
    assert servicio.FASE_PROTECCION == "Fase 6 - Proteccion de entrada y salida (M6)"


def test_la_velocidad_en_la_entrada_bajo_control_de_salida_es_la_del_perfil(
        corrida_base):
    from dataclasses import replace
    r = _punto(corrida_base, "A-01").resultado.resultado_hidraulico
    # A-01 corre bajo control de entrada y su perfil S1 no llega a la boca
    # (`V_entrada_m_s` None): se arma uno que si llega, para leer la rama.
    perfil = replace(r.perfil, V_entrada_m_s=1.234, alcanza_entrada=True,
                     y_entrada_m=0.8, HW_remanso_m=1.0)
    salida = replace(r, control_gobernante=ControlGobernante.SALIDA,
                     perfil=perfil)
    V = M6.velocidad_en_la_entrada(salida)
    assert V.valor == pytest.approx(1.234, rel=REL_FORMULA)
    assert "perfil de la lamina" in V.procedencia
    # Bajo control de salida SIN perfil que llegue, la critica, y lo dice.
    sin_perfil = replace(r, control_gobernante=ControlGobernante.SALIDA)
    V = M6.velocidad_en_la_entrada(sin_perfil)
    assert V.valor == pytest.approx(r.V_critica_m_s, rel=REL_FORMULA)
    assert "no llega a la entrada" in V.procedencia
    sin_nada = replace(r, perfil=None, V_critica_m_s=None)
    assert M6.velocidad_en_la_entrada(sin_nada) is None


def test_la_entrada_compara_con_el_terreno_si_esta_declarado(corrida_base):
    r = _punto(corrida_base, "A-01").resultado.resultado_hidraulico
    e = M6.proteccion_entrada(resultado=r, tipo_terreno="arena_fina_no_coloidal",
                              regimen_flujo="intermitente")
    assert e.requerida is True and e.velocidad_admisible.donde == M6.DONDE_ENTRADA
    assert [x.codigo for x in e.pasos] == ["6.8", "6.9"]
    with pytest.raises(DatoInvalidoError):
        M6.proteccion_entrada(resultado=r, tipo_embocadura="caja_magica")


def test_el_criterio_de_entrada_es_un_A_de_perfil_con_las_tres_clases_del_manual():
    c = ca.CRITERIOS["tipo_proteccion_entrada"]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.sensibilidad == ("emboquillado_de_piedra",
                              "enchapado_de_roca_acomodada", "otro_revestimiento")
    assert "MC_HHD.LAMINA_02" in c.fuente


# ===========================================================================
# 7 · Hoya de socavacion (HEC-14 Cap. 5)
# ===========================================================================

def test_hoya_no_cohesiva_reproduce_el_ejemplo_SI_de_hec14():
    """
    Pags. impresas 5-4 y 5-5: D = 457 mm, S = 2 %, caida 0.914 m (Hd = 2),
    Q = 0.764 m3/s, σ = 1.87, t = 30 min -> hs = 1.14 m, Ws = 8.82 m,
    Ls = 7.06 m, maximo a 0.4·Ls = 2.82 m. Aritmetica escrita (Rc = D/4):
        Rc = 0.11425; Rc^2.5 = 0.0044121; Q/(g^0.5·Rc^2.5) = 55.2864
        σ^(1/3) = 1.23201; (30/316) = 0.094937
        hs = 1.03·1.26·(2.27/1.23201)·55.2864^0.39·0.094937^0.06·0.11425
           = 1.13434 m
    """
    material = MaterialLecho(tipo="no_cohesivo", D84_m=1.87 ** 2 * 0.001,
                             D16_m=0.001)
    h = M6.hoya_de_socavacion_hec14(
        Q_celda=0.764, seccion=SeccionCircular(0.457), S=0.02,
        V=_V(3.0), altura_caida_m=0.914, material=material,
        duracion_pico_min=30.0)       # el ejemplo lo da: t = 30 min
    assert h.profundidad == pytest.approx(1.13434, rel=REL_ARITMETICA)
    assert h.profundidad == pytest.approx(1.14, rel=REL_EJEMPLO_IMPRESO)
    assert h.ancho == pytest.approx(8.82, rel=REL_EJEMPLO_IMPRESO)
    assert h.longitud == pytest.approx(7.06, rel=REL_EJEMPLO_IMPRESO)
    assert h.distancia_al_maximo == pytest.approx(2.82, rel=REL_EJEMPLO_IMPRESO)
    assert h.Cs == pytest.approx(1.03, rel=REL_TRANSPORTE) and h.Ch == pytest.approx(1.26, rel=REL_TRANSPORTE)
    assert h.duracion_min == pytest.approx(30.0, rel=REL_TRANSPORTE)
    assert [p.codigo for p in h.pasos] == ["6.11", "6.12", "6.13"]


def test_hoya_cohesiva_reproduce_el_ejemplo_SI_de_hec14():
    """
    Pags. impresas 5-8 y 5-9: D = 610 mm, S = 0, sin caida, Q = 1.133 m3/s,
    PI = 12, Sv = 23 970 N/m2, V = 3.88 m/s. Aritmetica escrita:
        τc = 0.001·(23970 + 8630)·tan(30 + 1.73·12) = 32.6·tan(50.76°)
           = 32.6·1.22438 = 39.91 N/m2   (la fuente: 39.9)
        ρV²/τc = 1000·3.88²/39.91 = 377.2   (la fuente: 377.3)
        hs = 0.86·377.2^0.18·(30/316)^0.10·0.61 = 1.206 m  (la fuente: 1.2)
    La fuente escribe (0.09)^θ por (30/316)^θ = (0.0949)^θ: de ahi el medio
    por ciento de Ws (5.02) y Ls (9.81).
    """
    assert M6.tension_tractiva_critica(Sv_Pa=23970.0, IP=12.0) == \
        pytest.approx(39.9, rel=REL_EJEMPLO_IMPRESO)
    h = M6.hoya_de_socavacion_hec14(
        Q_celda=1.133, seccion=SeccionCircular(0.61), S=0.0, V=_V(3.88),
        altura_caida_m=0.0, duracion_pico_min=30.0,    # «Use 30 minutes»
        material=MaterialLecho(tipo="cohesivo", IP=12.0, Sv_Pa=23970.0))
    assert h.profundidad == pytest.approx(1.206, rel=REL_ARITMETICA_CORTA)
    assert h.profundidad == pytest.approx(1.2, rel=REL_EJEMPLO_IMPRESO)
    # Conducto circular: la columna α de la Tabla 5.4, no la αe del marco.
    assert not any("(columna alfa_e)" in m.procedencia
                   for p in h.pasos for m in p.sustitucion)
    assert h.ancho == pytest.approx(5.02, rel=REL_EJEMPLO_IMPRESO)
    assert h.longitud == pytest.approx(9.81, rel=REL_EJEMPLO_IMPRESO)
    assert [p.codigo for p in h.pasos] == ["6.10", "6.11", "6.12", "6.13"]


@pytest.mark.parametrize("cambio, error", [
    (dict(altura_caida_m=2.5), MetodoNoEvaluableError),         # Hd > 4
    (dict(numero_celdas=2), MetodoNoEvaluableError),
    (dict(material=MaterialLecho(tipo="no_cohesivo")), DatoFaltanteError),
    (dict(material=MaterialLecho(tipo="cohesivo", IP=20.0, Sv_Pa=1e4)),
     MetodoNoEvaluableError),                                   # IP fuera de 5-16
    (dict(material=MaterialLecho()), DatoFaltanteError),
])
def test_hoya_fuera_de_rango_no_se_extrapola(cambio, error):
    base = dict(Q_celda=1.0, seccion=SeccionCircular(0.5), S=0.01, V=_V(3.0),
                altura_caida_m=0.5,
                material=MaterialLecho(tipo="no_cohesivo", D84_m=0.004,
                                       D16_m=0.001))
    base.update(cambio)
    with pytest.raises(error) as e:
        M6.hoya_de_socavacion_hec14(**base)
    if error is MetodoNoEvaluableError:
        # HEC-14 Cap. 5, no «HDS-5 3.24» (auditor de T-8, punto 7).
        assert str(e.value).startswith(MOTIVO_METODO_NO_EVALUABLE_HEC14)


def test_entre_dos_filas_la_lectura_la_decide_el_criterio():
    """
    Cs de profundidad con 6 % de pendiente: entre la fila 5 (1.08) y la «>7»
    (1.12). Envolvente: 1.12. Interpolacion: 1.08 + 0.04·(6-5)/(7-5) = 1.10.
    En una fila, la fila; mas alla de la ultima, la ultima.
    """
    cs = HEC14_SOCAVACION_CS
    assert M6.coeficiente_de_tabla(cs, 6.0, "profundidad",
                                   M6.LECTURA_ENVOLVENTE) == pytest.approx(1.12, rel=REL_TRANSPORTE)
    assert M6.coeficiente_de_tabla(cs, 6.0, "profundidad",
                                   M6.LECTURA_INTERPOLADA) == pytest.approx(1.10, rel=REL_TRANSPORTE)
    assert M6.coeficiente_de_tabla(cs, 2.0, "profundidad",
                                   M6.LECTURA_ENVOLVENTE) == pytest.approx(1.03, rel=REL_TRANSPORTE)
    assert M6.coeficiente_de_tabla(cs, 12.0, "profundidad",
                                   M6.LECTURA_INTERPOLADA) == pytest.approx(1.12, rel=REL_TRANSPORTE)
    # Ch de LONGITUD baja con la caida: la envolvente toma el MAYOR (1.00).
    assert M6.coeficiente_de_tabla(HEC14_SOCAVACION_CH, 0.5, "longitud",
                                   M6.LECTURA_ENVOLVENTE) == pytest.approx(1.00, rel=REL_TRANSPORTE)
    with pytest.raises(DatoInvalidoError):
        M6.coeficiente_de_tabla(cs, 1.0, "profundidad", "a_ojo")


def test_la_declarada_gana_y_la_estimada_se_imprime_al_lado(corrida_base):
    r = _punto(corrida_base, "A-01").resultado.resultado_hidraulico
    seccion = _punto(corrida_base, "A-01").resultado.seccion
    lecho = MaterialLecho(tipo="no_cohesivo", D84_m=0.02, D16_m=0.002)
    s = M6.socavacion_salida(resultado=r, seccion=seccion, altura_caida_m=0.3,
                             material=lecho, declarada_m=0.10)
    assert s.origen == ORIGEN_SOCAVACION_DECLARADA
    assert s.profundidad_para_desplante == pytest.approx(0.10, rel=REL_TRANSPORTE)
    assert s.estimada is not None and s.estimada.profundidad > 0.10
    assert any("MENOR que la estimada" in x for x in s.avisos)
    sola = M6.socavacion_salida(resultado=r, seccion=seccion,
                                altura_caida_m=0.3, material=lecho)
    assert sola.origen == ORIGEN_SOCAVACION_ESTIMADA
    assert sola.profundidad_para_desplante == pytest.approx(sola.estimada.profundidad, rel=REL_TRANSPORTE)
    assert sola.pasos[-1].codigo == "6.14"


def test_sin_lecho_no_se_supone_un_suelo(corrida_base):
    a01 = _punto(corrida_base, "A-01")
    s = a01.socavacion
    assert s.origen == ORIGEN_SOCAVACION_SIN_DATO
    assert s.profundidad_para_desplante is None and s.estimada is None
    assert "material_lecho_salida" in s.motivo_no_estimada
    assert any("Socavacion a la salida: NO se estimo" in x for x in a01.avisos())
    # La declarada de 0 (lecho de roca) vale; una negativa, no.
    r = a01.resultado.resultado_hidraulico
    cero = M6.socavacion_salida(resultado=r, seccion=a01.resultado.seccion,
                                declarada_m=0.0)
    assert cero.profundidad_para_desplante == pytest.approx(0.0, abs=ABS_CERO)
    with pytest.raises(DatoInvalidoError):
        M6.socavacion_salida(resultado=r, seccion=a01.resultado.seccion,
                             declarada_m=-0.5)


def test_sin_revestimiento_pero_con_hoya_se_avisa_el_desplante(corrida_base):
    a01 = _punto(corrida_base, "A-01")
    s = M6.socavacion_salida(
        resultado=a01.resultado.resultado_hidraulico,
        seccion=a01.resultado.seccion, altura_caida_m=0.3,
        material=MaterialLecho(tipo="no_cohesivo", D84_m=0.02, D16_m=0.002),
        proteccion_requerida=False)
    # Segun la Tabla Nº 11 el terreno resistiria, y aun asi hay hoya: el
    # aviso lo dice en nombre del proyecto (no «la tabla no pide revestir»).
    assert any("el terreno resistiria" in x and "5.1.3" in x
               for x in s.avisos)


# ===========================================================================
# 8 · La corrida entera: datos externos, avisos y salidas
# ===========================================================================

DATOS_T8 = {
    "A-01": {"tipo_terreno_receptor": "graduado_grava_gruesa",
             "tipo_terreno_entrada": "graduado_grava_gruesa",
             "regimen_flujo_descarga": "intermitente",
             "material_lecho_salida": {"tipo": "no_cohesivo", "D84_m": 0.03,
                                       "D16_m": 0.002, "pasa_200_pct": 8},
             "duracion_caudal_pico_min": 60},
    "A-02": {"tipo_terreno_receptor": "graduado_grava_a_piedras_mayor_20cm",
             "regimen_flujo_descarga": "intermitente",
             "profundidad_socavacion_estimada_m": 0.8},
}


@pytest.fixture(scope="module")
def corrida_con_datos(tmp_path_factory):
    return _correr_ancho(tmp_path_factory.mktemp("t8"), DATOS_T8)


def test_con_los_datos_del_sitio_la_fase_6_se_completa(corrida_con_datos):
    a01 = _punto(corrida_con_datos, "A-01")
    # A-01 descarga a 3.2 m/s sobre grava gruesa (2.40 m/s): se protege.
    assert a01.proteccion.requerida is True
    assert a01.proteccion.filtro.columna == "< 15"
    assert a01.socavacion.origen == ORIGEN_SOCAVACION_ESTIMADA
    assert a01.socavacion.estimada.duracion_min == pytest.approx(60.0, rel=REL_TRANSPORTE)
    # A-02 descarga a 2.9 m/s sobre piedras > 20 cm (3.00 m/s): el terreno
    # la resistiria segun la tabla, y la proteccion se MANTIENE (decision del
    # dueño del 2026-11-12; antes quedaba «sin enrocado», con d50 None).
    a02 = _punto(corrida_con_datos, "A-02")
    assert a02.proteccion.requerida is False
    assert a02.proteccion.d50 == pytest.approx(
        a02.proteccion.V ** 2 / (3.1 * 9.8), rel=REL_FORMULA)
    assert a02.socavacion.origen == ORIGEN_SOCAVACION_DECLARADA


def test_ningun_diametro_se_mueve_con_los_datos_de_T8(corrida_base,
                                                      corrida_con_datos):
    """PARADA (c) del orquestador: la Fase 6 corre DESPUES del dimensionado."""
    for base, con in zip(corrida_base.puntos, corrida_con_datos.puntos):
        assert base.dimensionado == con.dimensionado
        if base.dimensionado:
            assert base.resultado.seccion == con.resultado.seccion


def test_los_avisos_de_la_fase_6_llegan_a_cli_json_y_memoria(corrida_base):
    a01 = _punto(corrida_base, "A-01")
    avisos = [x for x in a01.avisos() if x.startswith(("Proteccion", "Socavacion"))]
    assert avisos
    texto = cli.volcar(corrida_base)
    volcado = {p["id"]: p for p in cli.informe_json(corrida_base)["puntos"]}
    html = M11.memoria_de_punto(a01)
    for aviso in avisos:
        assert aviso in texto
        assert aviso in volcado["A-01"]["avisos"]
        assert M11._esc(aviso) in html


def test_el_json_lleva_las_tres_piezas_de_la_fase_6(corrida_con_datos):
    volcado = {p["id"]: p for p in cli.informe_json(corrida_con_datos)["puntos"]}
    a01, a02 = volcado["A-01"], volcado["A-02"]
    assert a01["proteccion_salida"]["requerida"] is True
    assert a01["proteccion_salida"]["apron_hec14"]["clase"] == 4
    assert a01["proteccion_entrada"]["revestimiento"] == "emboquillado_de_piedra"
    assert a01["socavacion_salida"]["origen"] == ORIGEN_SOCAVACION_ESTIMADA
    assert a02["proteccion_salida"]["requerida"] is False
    assert a02["proteccion_salida"]["d50_m"] is not None
    assert a02["proteccion_salida"]["d50_laushey_m"] == \
        a02["proteccion_salida"]["d50_m"]
    assert a02["socavacion_salida"]["profundidad_para_desplante_m"] == \
        pytest.approx(0.8, rel=REL_TRANSPORTE)


def test_bajo_la_admisible_el_resumen_lleva_la_proteccion(corrida_con_datos,
                                                          tmp_path):
    """
    A-02, bajo la admisible del terreno. Hasta la decision del 2026-11-12 el
    resumen decia «sin enrocado» y el CSV dejaba las tres celdas VACIAS,
    iguales a las de una Fase 6 bloqueada (H11 de la segunda auditoria). Hoy
    llevan los numeros que rigen, y nada dice «sin enrocado».
    """
    a02 = _punto(corrida_con_datos, "A-02")
    assert "sin enrocado" not in M11.fila_resumen(a02, "cabezal")
    fila = M11._fila_resumen_csv(a02, "cabezal")
    for columna in ("proteccion_d50_m", "proteccion_espesor_m",
                    "proteccion_longitud_m"):
        assert fila[M11.COLUMNAS_RESUMEN_CSV.index(columna)] != ""
    assert "sin enrocado" not in M11.memoria_de_punto(a02)
    assert "sin enrocado" not in cli.volcar(corrida_con_datos)
    assert any("se MANTIENE" in x for x in a02.avisos())


def test_la_traza_de_la_fase_6_la_imprime_la_memoria(corrida_con_datos):
    a01 = _punto(corrida_con_datos, "A-01")
    pasos = M11.traza_proteccion(a01)
    codigos = [p.codigo for p in pasos]
    for c in ("6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9",
              "6.11", "6.14"):
        assert c in codigos
    impresos = {id(p) for p in M11.pasos_impresos(corrida_con_datos)}
    assert all(id(p) in impresos for p in pasos)
    # Los diez fundamentos de la Fase 6 los emite esta corrida (los nueve
    # de T-8 estan en `sin_alcanzar` de test_memoria_sustentada porque la
    # corrida por defecto no dimensiona: aqui se mide que existen).
    a02 = _punto(corrida_con_datos, "A-02")
    emitidos = {p.fundamento_id for p in pasos + M11.traza_proteccion(a02)}
    assert emitidos == {"F6.LAUSHEY", "F6.GEOMETRIA_ADOPTADA", "F6.FROUDE",
                        "F6.V_ADMISIBLE", "F6.APRON", "F6.APRON_GEOMETRIA",
                        "F6.FILTRO", "F6.ENTRADA", "F6.SOCAVACION",
                        "F6.SOCAVACION_DESPLANTE"}


@pytest.mark.parametrize("bruto, campo, motivo", [
    ({"tipo_terreno_receptor": "roca_sana"}, "tipo_terreno_receptor",
     "Tabla Nº 11"),
    ({"regimen_flujo_descarga": "a_veces"}, "regimen_flujo_descarga",
     "Tabla Nº 11"),
    ({"material_lecho_salida": {"tipo": "no_cohesivo", "D84_m": 0.01}},
     "material_lecho_salida", "faltan ['D16_m']"),
    ({"material_lecho_salida": {"tipo": "cohesivo", "IP": 10, "Sv_Pa": 1e4,
                                "D84_m": 0.01}}, "material_lecho_salida",
     "del otro tipo"),
    ({"material_lecho_salida": {"D84_m": 0.01, "D16_m": 0.001}},
     "material_lecho_salida", "hace falta `tipo`"),
    ({"material_lecho_salida": {"pasa_200_pct": 140}}, "material_lecho_salida",
     "entre 0 y 100"),
    ({"material_lecho_salida": {"tipo": "no_cohesivo", "D84_m": 0.001,
                                "D16_m": 0.01}}, "material_lecho_salida",
     "D84 no puede ser menor que D16"),
    ({"material_lecho_salida": {"tipo": "no_cohesivo", "D84_m": True,
                                "D16_m": 0.01}}, "material_lecho_salida",
     "no es un numero finito"),
    ({"profundidad_socavacion_estimada_m": -1},
     "profundidad_socavacion_estimada_m", "positivo"),
    ({"duracion_caudal_pico_min": 0}, "duracion_caudal_pico_min", "positivo"),
])
def test_los_datos_de_T8_se_validan_en_la_carga(tmp_path, bruto, campo, motivo):
    """
    El motivo se comprueba, no solo el nombre del dato: en el arbol de antes
    de T-8 estas claves se rechazaban igual, por DESCONOCIDAS, y un test que
    solo mirara la clave habria pasado vacuo (medido).
    """
    with pytest.raises(DatoInvalidoError) as e:
        _externos(tmp_path, {"puntos": {"A-01": bruto}})
    assert campo in str(e.value) and motivo in str(e.value)


def test_los_datos_de_T8_validos_se_cargan_con_su_tipo(tmp_path):
    """El control positivo de la puerta: las tres formas del lecho y el cero."""
    ext = _externos(tmp_path, {"puntos": {
        "A-01": {"tipo_terreno_receptor": "grava_fina",
                 "regimen_flujo_descarga": "permanente",
                 "material_lecho_salida": {"tipo": "cohesivo", "IP": 12,
                                           "Sv_Pa": 23970, "pasa_200_pct": 70}},
        "A-02": {"material_lecho_salida": {"pasa_200_pct": 35},
                 "profundidad_socavacion_estimada_m": 0}}})
    lecho = ext.valor("A-01", "material_lecho_salida")
    assert isinstance(lecho, MaterialLecho)
    assert lecho.tipo == "cohesivo" and lecho.IP == pytest.approx(12.0, rel=REL_TRANSPORTE)
    assert ext.valor("A-01", "tipo_terreno_receptor") == "grava_fina"
    assert ext.valor("A-02", "material_lecho_salida").tipo is None
    assert ext.valor("A-02", "profundidad_socavacion_estimada_m") == \
        pytest.approx(0.0, abs=ABS_CERO)


def test_las_seis_claves_son_externas_opcionales_sin_valor_por_defecto():
    for clave in ("tipo_terreno_receptor", "tipo_terreno_entrada",
                  "regimen_flujo_descarga", "material_lecho_salida",
                  "duracion_caudal_pico_min",
                  "profundidad_socavacion_estimada_m"):
        assert clave in servicio.CLAVES_EXTERNAS
        assert clave in servicio.EXTERNOS_CON_VIA_ALTERNA
    assert "profundidad_socavacion_estimada_m" in servicio.CLAVES_QUE_ADMITEN_CERO


def test_los_criterios_nuevos_de_la_hoya_tienen_ficha_y_ventana():
    # Era [C] con 30 min; desde la decision del dueño del 2026-11-12 es una
    # ELECCION [A] en la ventana 30-360, con 360 de valor de archivo.
    t = ca.CRITERIOS["duracion_caudal_pico_socavacion_min"]
    assert t.etiqueta == "A" and t.valor == pytest.approx(360.0, rel=REL_TRANSPORTE)
    assert t.sensibilidad == pytest.approx((30.0, 360.0), rel=REL_TRANSPORTE)
    lectura = ca.CRITERIOS["lectura_coeficientes_socavacion_hec14"]
    assert lectura.etiqueta == "A"
    assert lectura.valor == M6.LECTURA_ENVOLVENTE
    assert set(lectura.sensibilidad) == {M6.LECTURA_ENVOLVENTE,
                                         M6.LECTURA_INTERPOLADA}


def test_con_el_barril_horizontal_la_fase_6_lee_la_velocidad_de_salida(tmp_path):
    """
    Con `S_conducto = 0` (T-2) no hay tirante normal: `y_normal` y
    `V_erosion` son None. La Fase 6 no los lee: el Froude sale de la
    velocidad de SALIDA de M4 y su area de continuidad, el apron no ajusta
    por flujo supercritico (no hay yn), y la hoya entra por la fila 0 % de la
    Tabla 5.3 (Cs = 1.00).
    """
    informe = _correr_ancho(tmp_path, {"A-01": {
        "S_conducto": 0,
        "material_lecho_salida": {"tipo": "no_cohesivo", "D84_m": 0.02,
                                  "D16_m": 0.002}}})
    a01 = _punto(informe, "A-01")
    r = a01.resultado.resultado_hidraulico
    assert r.S == pytest.approx(0.0, abs=ABS_CERO) and r.y_normal is None
    p = a01.proteccion
    assert p.froude.A == pytest.approx(r.Q_celda_m3s / r.V_salida.valor,
                                       rel=REL_FORMULA)
    assert p.d50 == pytest.approx(r.V_salida.valor ** 2 / (3.1 * 9.8),
                                  rel=REL_FORMULA)
    assert p.apron is None or not p.apron.ajustado_por_supercritico
    hoya = a01.socavacion.estimada
    assert hoya is not None and hoya.Cs == pytest.approx(1.00, rel=REL_TRANSPORTE)


# ===========================================================================
# 9 · Lo que la mutacion enseño (arnes de EXT-11 sobre M6; ficha T8-05)
# ===========================================================================

def test_hoya_cohesiva_en_un_marco_usa_el_tirante_equivalente_y_alfa_e():
    """
    Ec. (5.3), «other shaped culverts»: ye = (A/2)^0.5 con A = Q/V, y αe de la
    Tabla 5.4. Marco de 1.20 × 1.00 m, Q = 1.0 m3/s, V = 2.5 m/s, PI = 12,
    Sv = 23 970 N/m2, S = 0, caida de 1.00 m (Hd = 1: Ch = 1.22, 1.51, 0.73).
    Aritmetica escrita:
        A = 1.0/2.5 = 0.40 m2; ye = (0.40/2)^0.5 = 0.447214 m
        τc = 39.9146 N/m2; ρV²/τc = 1000·2.5²/39.9146 = 156.584
        hs = 1.00·1.22·1.37·156.584^0.18·(30/316)^0.10·0.447214
           = 1.22·1.37·2.48345·0.790212·0.447214 = 1.46688 m
        Ws = 1.51·5.63·156.584^0.17·(30/316)^0.07·0.447214 = 7.61251 m
        Ls = 0.73·4.48·156.584^0.33·(30/316)^0.09·0.447214 = 6.27122 m
    """
    h = M6.hoya_de_socavacion_hec14(
        Q_celda=1.0, seccion=SeccionRectangular(B=1.2, H=1.0), S=0.0,
        V=_V(2.5), altura_caida_m=1.0, duracion_pico_min=30.0,
        material=MaterialLecho(tipo="cohesivo", IP=12.0, Sv_Pa=23970.0))
    assert h.profundidad == pytest.approx(1.46688, rel=REL_ARITMETICA)
    assert h.ancho == pytest.approx(7.61251, rel=REL_ARITMETICA)
    assert h.longitud == pytest.approx(6.27122, rel=REL_ARITMETICA)
    assert "(5.3)" in h.metodo and "ye" in h.pasos[1].formula
    # La sustitucion dice que la fila se leyo en la columna αe.
    assert any("(columna alfa_e)" in m.procedencia
               for m in h.pasos[1].sustitucion)


def test_la_pendiente_entra_en_porcentaje_y_la_interpolacion_multiplica():
    """
    S = 0.06 m/m es el 6 %: Cs de profundidad 1.12 con la envolvente (entre
    el 5 % y el «>7»). Y la interpolacion entre filas a media distancia: Ch
    de profundidad con Hd = 0.5 vale 1.00 + 0.22·0.5 = 1.11.
    """
    h = M6.hoya_de_socavacion_hec14(
        Q_celda=0.764, seccion=SeccionCircular(0.457), S=0.06, V=_V(3.0),
        altura_caida_m=0.914,
        material=MaterialLecho(tipo="no_cohesivo", D84_m=0.0035, D16_m=0.001))
    assert h.Cs == pytest.approx(1.12, rel=REL_TRANSPORTE)
    assert M6.coeficiente_de_tabla(HEC14_SOCAVACION_CH, 0.5, "profundidad",
                                   M6.LECTURA_INTERPOLADA) == \
        pytest.approx(1.11, rel=REL_FORMULA)


@pytest.mark.parametrize("material", [
    MaterialLecho(tipo="no_cohesivo", D84_m=0.01),
    MaterialLecho(tipo="no_cohesivo", D16_m=0.01),
    MaterialLecho(tipo="cohesivo", IP=10.0),
    MaterialLecho(tipo="cohesivo", Sv_Pa=1e4),
])
def test_medio_ensayo_del_lecho_es_un_dato_que_falta(material):
    with pytest.raises(DatoFaltanteError):
        M6.hoya_de_socavacion_hec14(
            Q_celda=1.0, seccion=SeccionCircular(0.5), S=0.01, V=_V(3.0),
            altura_caida_m=0.5, material=material)


def test_un_lecho_uniforme_D84_igual_a_D16_es_valido():
    h = M6.hoya_de_socavacion_hec14(
        Q_celda=1.0, seccion=SeccionCircular(0.5), S=0.01, V=_V(3.0),
        altura_caida_m=0.0,
        material=MaterialLecho(tipo="no_cohesivo", D84_m=0.002, D16_m=0.002))
    assert h.profundidad > 0


def test_la_salida_al_nivel_del_lecho_se_estima_y_la_declarada_va_en_el_paso(
        corrida_base):
    a01 = _punto(corrida_base, "A-01")
    lecho = MaterialLecho(tipo="no_cohesivo", D84_m=0.02, D16_m=0.002)
    s = M6.socavacion_salida(resultado=a01.resultado.resultado_hidraulico,
                             seccion=a01.resultado.seccion, altura_caida_m=0.0,
                             material=lecho, declarada_m=2.0,
                             longitud_proteccion_m=1.0)
    assert s.estimada is not None and s.estimada.Ch == pytest.approx(
        1.0, rel=REL_TRANSPORTE)
    simbolos = [m.simbolo for m in s.pasos[-1].sustitucion]
    assert simbolos == ["hs declarada", "hs estimada"]
    assert any("revestimiento hasta donde" in x for x in s.avisos)
    assert not any("MENOR que la estimada" in x for x in s.avisos)


def test_el_froude_dice_si_la_salida_va_llena_y_el_umbral_es_uno():
    llena = M6.froude_salida(V=_V(2.0), Q_celda=1.0, seccion=SeccionCircular(1.0),
                             y_salida=1.0)
    parcial = M6.froude_salida(V=_V(2.0), Q_celda=1.0,
                               seccion=SeccionCircular(1.0), y_salida=0.6)
    assert llena.seccion_llena and not parcial.seccion_llena
    assert "LLENA" in llena.paso.veredicto.explicacion
    assert "LLENA" not in parcial.paso.veredicto.explicacion
    # El regimen sale del tirante contra el critico, no de Fr_e.
    assert M6.froude_salida(V=_V(2.0), Q_celda=1.0, seccion=SeccionCircular(1.0),
                            y_salida=0.3, y_critico=0.5).supercritico
    assert M6.froude_salida(V=_V(2.0), Q_celda=1.0, seccion=SeccionCircular(1.0),
                            y_salida=0.5, y_critico=0.5).supercritico is False


def test_el_margen_de_la_velocidad_admisible_es_la_holgura():
    v = M6.velocidad_admisible_del_cauce(V=_V(2.0), tipo_terreno="grava_fina",
                                         regimen_flujo="intermitente")
    assert v.paso.veredicto.margen == pytest.approx(1.50 - 2.0, rel=REL_FORMULA)
    assert v.paso.codigo == "6.4"
    with pytest.raises(DatoInvalidoError, match="tipo_terreno_entrada"):
        M6.velocidad_admisible_del_cauce(V=_V(1.0), tipo_terreno="roca",
                                         regimen_flujo="intermitente",
                                         donde=M6.DONDE_ENTRADA)


def test_el_apron_fuera_de_la_tabla_compara_con_la_clase_mayor():
    a = M6.apron_hec14(Q_celda=6.0, seccion=SeccionCircular(1.0), TW=0.4,
                       y_salida=None, y_critico=0.9)
    mayor = {m.simbolo: m for m in a.pasos[1].sustitucion}["D50 de la clase mayor"]
    assert mayor.valor == pytest.approx(0.55, rel=REL_TRANSPORTE)
    assert "clase 6" in mayor.procedencia
    # El TW de 0.4 m queda en el rango y no se acota: la procedencia lo dice.
    assert not a.TW_acotado
    assert "0.4·D" not in {m.simbolo: m for m in
                           a.pasos[0].sustitucion}["TW"].procedencia


def test_el_contraste_avisa_la_piedra_mayor_solo_cuando_hec14_la_pide(
        corrida_base):
    a01 = _punto(corrida_base, "A-01")
    # Laushey 0.338 m contra HEC-14 0.252 m: no hay aviso de piedra mayor.
    assert not any("pide una piedra mayor" in x for x in a01.avisos())
    a = M6.apron_hec14(Q_celda=2.33, seccion=SeccionCircular(1.5), TW=0.5,
                       y_salida=None, y_critico=0.8)
    avisos = M6._avisos_del_contraste(a, d50=0.05, espesor=5.0, longitud=50.0)
    assert any("pide una piedra mayor" in x for x in avisos)


@pytest.mark.parametrize("pasa, IP, abertura", [
    (0.0, None, 0.43),        # el borde inferior de la tabla es valido
    (60.0, 7.0, 0.22),        # «mayor a 7»: el 7 justo no
])
def test_los_bordes_del_filtro(pasa, IP, abertura):
    f = M6.requisito_de_filtro(pasa_200_pct=pasa, indice_plasticidad=IP)
    assert f.abertura_aparente_max_mm == pytest.approx(abertura, rel=REL_TRANSPORTE)
    procedencia = {m.simbolo: m for m in f.paso.sustitucion}[
        "abertura aparente maxima"].procedencia
    assert procedencia.startswith("nota (5) b") == (abertura == pytest.approx(
        0.30, rel=REL_TRANSPORTE))


def test_un_solo_dato_del_terreno_no_compara_y_lo_dice(corrida_base):
    p = M6.proteccion_salida(V=_V(2.0), tipo_terreno="grava_fina")
    assert p.requerida is None and p.velocidad_admisible is None
    assert any("'regimen_flujo_descarga'" in x and
               "'tipo_terreno_receptor'" not in x for x in p.avisos)
    r = _punto(corrida_base, "A-01").resultado.resultado_hidraulico
    sin_seccion = M6.proteccion_salida(V=_V(2.0), resultado=r)
    assert sin_seccion.froude is None and sin_seccion.apron is None
    e = M6.proteccion_entrada(resultado=r, regimen_flujo="intermitente")
    assert any("'tipo_terreno_entrada'" in x for x in e.avisos)
    aviso = next(x for x in e.avisos if "'tipo_terreno_entrada'" in x)
    assert "no se sabe si la entrada necesita revestimiento" in aviso
    assert "enrocado se dimensiona" not in aviso


def test_la_entrada_sin_velocidad_lo_dice_y_la_que_supera_avisa(corrida_base):
    from dataclasses import replace
    r = _punto(corrida_base, "A-01").resultado.resultado_hidraulico
    vacia = M6.proteccion_entrada(resultado=replace(r, perfil=None,
                                                    V_critica_m_s=None))
    assert vacia.V_entrada is None and vacia.pasos == ()
    assert any("no trae la velocidad en la boca" in x for x in vacia.avisos)
    resiste = M6.proteccion_entrada(
        resultado=r, tipo_terreno="graduado_grava_a_piedras_mayor_20cm",
        regimen_flujo="intermitente")
    assert resiste.requerida is False
    assert not any("supera" in x for x in resiste.avisos)


def test_una_caida_entre_dos_y_cuatro_alturas_esta_en_la_tabla():
    """La Tabla 5.2 llega a Hd = 4: con Hd = 3 la hoya se estima (Ch 1.34)."""
    h = M6.hoya_de_socavacion_hec14(
        Q_celda=0.764, seccion=SeccionCircular(0.457), S=0.02, V=_V(3.0),
        altura_caida_m=3 * 0.457,
        material=MaterialLecho(tipo="no_cohesivo", D84_m=0.0035, D16_m=0.001))
    assert h.Ch == pytest.approx(1.34, rel=REL_TRANSPORTE)


@pytest.mark.parametrize("Q", [0.0, True, float("inf")])
def test_las_guardias_de_segunda_linea_rechazan_cero_bool_e_infinito(Q):
    with pytest.raises(DatoInvalidoError):
        M6.froude_salida(V=_V(2.0), Q_celda=Q, seccion=SeccionCircular(1.0))


def test_sin_seccion_el_apron_no_se_intenta_ni_se_avisa(corrida_base):
    r = _punto(corrida_base, "A-01").resultado.resultado_hidraulico
    p = M6.proteccion_salida(V=_V(2.0), resultado=r)
    assert p.apron is None
    assert not any("apron de HEC-14 NO se evaluo" in x for x in p.avisos)


# ===========================================================================
# 10 · Las correcciones del auditor adversarial de T-8
# ===========================================================================

LECHO_ARENOSO = {"tipo": "no_cohesivo", "D84_m": 0.0005, "D16_m": 0.00008}


def test_aud1_la_duracion_por_criterio_avisa_y_da_la_sensibilidad(tmp_path):
    """
    Hallazgo 1, reescrito a la decision del 2026-11-12. Sin
    `duracion_caudal_pico_min` rige el criterio [A], que ya no son los 30 min
    que HEC-14 5.1.2 recomienda «lacking this knowledge» sino 360: la corrida
    lo AVISA y da al lado la profundidad con 30 min, la otra punta de la
    ventana. Con θ = 0.06 (no cohesivo): ×(30/360)^0.06 = 1/1.161 = ×0.861.
    """
    informe = _correr_ancho(tmp_path, {"A-01": {
        "material_lecho_salida": LECHO_ARENOSO}})
    a01 = _punto(informe, "A-01")
    hoya = a01.socavacion.estimada
    assert hoya.duracion_por_criterio and not hoya.duracion_acotada
    assert hoya.duracion_min == pytest.approx(360.0, rel=REL_TRANSPORTE)
    assert hoya.duracion_alternativa_min == pytest.approx(30.0,
                                                          rel=REL_TRANSPORTE)
    assert hoya.profundidad_alternativa == pytest.approx(
        hoya.profundidad / 12 ** 0.06, rel=REL_FORMULA)
    assert any("adopcion del proyecto" in x and "360 min" in x
               and "Con t = 30 min" in x for x in a01.avisos())
    nota = next(p for p in hoya.pasos if p.codigo == "6.11").nota_del_proyecto
    assert "SENSIBILIDAD A LA DURACION" in nota
    # El numero de la nota es el de la formula, no solo la frase.
    assert f"seria {hoya.profundidad / 12 ** 0.06:.3f} m (×0.861)" in nota


def test_aud1_una_duracion_menor_de_30_min_se_acota_y_no_deja_sin_dato(tmp_path):
    """
    Hallazgo 1 (ii): con t = 20 min el punto quedaba «sin dato» mientras que
    sin el dato salia la hoya de 30 min. Ahora se estima con 30 min como cota
    superior (la hoya crece con t) y se avisa.
    """
    con_20 = _punto(_correr_ancho(tmp_path, {"A-01": {
        "material_lecho_salida": LECHO_ARENOSO,
        "duracion_caudal_pico_min": 20}}), "A-01")
    # El termino de comparacion es la hoya de 30 min DECLARADOS: el criterio
    # por falta del dato da hoy la de 360.
    sin_dato = _punto(_correr_ancho(tmp_path, {"A-01": {
        "material_lecho_salida": LECHO_ARENOSO,
        "duracion_caudal_pico_min": 30}}), "A-01")
    hoya = con_20.socavacion.estimada
    assert hoya is not None and hoya.duracion_acotada
    assert hoya.duracion_min == pytest.approx(30.0, rel=REL_TRANSPORTE)
    assert hoya.profundidad == pytest.approx(
        sin_dato.socavacion.estimada.profundidad, rel=REL_FORMULA)
    assert any("cota superior" in x for x in con_20.avisos())


def test_aud2_el_regimen_es_uno_solo_para_el_froude_y_el_apron():
    """
    Hallazgo 2, el caso del auditor: D = 1.0 m, y = 0.25 m, Q = 0.2329 m3/s.
    y_c = 0.2686 m > y: el flujo es SUPERCRITICO (Fr con A/T = 1.15). El
    Froude con ye = (A/2)^0.5 da 0.920 y antes rotulaba «subcritico», contra
    el apron, que aplicaba la Ec. 10.5 «porque el flujo es supercritico».
    """
    D, y = 1.0, 0.25
    seccion = SeccionCircular(D)
    A = seccion.area(y)
    T = 2 * math.sqrt(y * (D - y))
    V = 1.15 * math.sqrt(G * A / T)
    Q = A * V
    y_c = 0.2686
    f = M6.froude_salida(V=_V(V), Q_celda=Q, seccion=seccion, y_salida=y,
                         y_critico=y_c)
    a = M6.apron_hec14(Q_celda=Q, seccion=seccion, TW=0.5, y_salida=y,
                       y_critico=y_c)
    assert f.Fr == pytest.approx(0.920, rel=REL_EJEMPLO_IMPRESO)
    assert f.supercritico is True and a.ajustado_por_supercritico is True
    assert "supercritico" in f.paso.veredicto.explicacion
    assert "no el que clasifica el regimen" in f.paso.veredicto.explicacion
    assert M6.flujo_supercritico(y, y_c) is True
    assert M6.flujo_supercritico(None, y_c) is None


def test_aud3_un_IP_fuera_del_rango_avisa_y_no_bloquea(tmp_path):
    """
    Hallazgo 3: la carga acepta IP = 0 y M6 lanzaba `DatoInvalidoError`, que
    nadie recogia: bloqueo nuevo de la Fase 6. Ahora es «no evaluable» con
    aviso, como IP = 0.5; un IP negativo se rechaza en la carga.
    """
    with pytest.raises(MetodoNoEvaluableError):
        M6.tension_tractiva_critica(Sv_Pa=2e4, IP=0.0)
    informe = _correr_ancho(tmp_path, {"A-01": {"material_lecho_salida": {
        "tipo": "cohesivo", "IP": 0, "Sv_Pa": 2e4}}})
    a01 = _punto(informe, "A-01")
    assert not [b for b in a01.bloqueos if "Fase 6" in str(b.fase)]
    assert a01.socavacion.estimada is None
    assert any("indice de plasticidad" in x and "NO se estimo" in x
               for x in a01.avisos())
    with pytest.raises(DatoInvalidoError, match="IP"):
        _externos(tmp_path, {"puntos": {"A-01": {"material_lecho_salida": {
            "tipo": "cohesivo", "IP": -1, "Sv_Pa": 2e4}}}})


def test_aud4_bajo_la_admisible_el_aviso_cita_la_frase_del_hds5():
    """
    Hallazgo 4 de la primera auditoria, y lo que la decision 6 del dueño
    (2026-11-12) hizo con el: «sin enrocado» no es una conclusion. El HDS-5
    5.3.2 dice que el apron es practica corriente salvo que el campo diga que
    no hace falta; el aviso lo cita (del registro), la proteccion se
    mantiene, y el fundamento no lleva OBLIGA.
    """
    from src.normativa.esquema import Verbo
    reg = _registro.construir()
    p = M6.proteccion_salida(V=_V(1.0), tipo_terreno="grava_fina",
                             regimen_flujo="intermitente")
    assert p.requerida is False and p.d50 is not None
    literal = reg.cita("HDS5_3ED.5.3.2#PRACTICA").texto_literal.texto
    assert any("inspeccion de campo" in x and literal in x for x in p.avisos)
    assert not any("SIN enrocado" in x for x in p.avisos)
    assert reg.fundamento("F6.V_ADMISIBLE").verbo is not Verbo.OBLIGA
    assert reg.cita("HDS5_3ED.5.3.2#PRACTICA").interpretacion is not None


def test_aud5_el_espesor_bajo_2_d50_se_avisa_siempre(corrida_manual,
                                                     corrida_base):
    """
    Hallazgo 5 (i): con la regla «manual», 1.75·d50 queda bajo el piso de
    HEC-14 («to a limit of 2.0D50»; «at least 2D50 thick») en TODO punto que
    dimensiona; en A-02 no se avisaba porque el espesor absoluto superaba el
    de la clase 1. Con la envolvente (el archivo) el espesor que rige es el
    de la Tabla 10.1 y el aviso calla.
    """
    for id_punto in ("A-01", "A-02"):
        avisos = _punto(corrida_manual, id_punto).avisos()
        assert any("1.75 veces el d50" in x and "to a limit of 2.0D50" in x
                   for x in avisos), id_punto
        assert not any("veces el d50" in x and "bajo el piso" in x
                       for x in _punto(corrida_base, id_punto).avisos())
    # 2.0·0.35 = 0.70 m: un espesor de 0.80 m alcanza el piso y no se avisa;
    # uno de 0.60 m (1.71 veces) se avisa.
    assert M6._aviso_espesor_bajo_el_piso(0.80, 0.35) == ()
    assert "1.71 veces el d50" in M6._aviso_espesor_bajo_el_piso(0.60, 0.35)[0]


def test_aud5_la_clase_de_la_piedra_adoptada_se_contrasta(corrida_manual):
    """
    Hallazgo 5 (ii), A-02 con la regla «manual»: la Ec. (10.4) pide la clase
    1, y la piedra que el proyecto pone (d50 = 0.274 m) es de la clase 4: L =
    6·0.9 = 5.4 m y profundidad 2.2·0.35 = 0.77 m, mas que lo adoptado (5.0 m
    y 0.479 m).
    """
    a02 = _punto(corrida_manual, "A-02")
    p = a02.proteccion
    assert p.apron.clase == 1
    c = p.clase_de_la_piedra
    assert c.clase == 4
    assert c.longitud == pytest.approx(6 * 0.9, rel=REL_FORMULA)
    assert c.espesor == pytest.approx(2.2 * 0.35, rel=REL_FORMULA)
    assert any("piedra que el proyecto pone" in x for x in a02.avisos())
    assert any("queda corto en la longitud (5.00 m contra 5.40 m) y en el "
               "espesor (0.479 m contra 0.770 m)" in x for x in a02.avisos())
    assert M6._avisos_de_la_piedra(c, espesor=0.8, longitud=6.0) == ()
    solo_espesor = M6._avisos_de_la_piedra(c, espesor=0.5, longitud=6.0)
    assert len(solo_espesor) == 1 and "la longitud" not in solo_espesor[0]
    assert "6.6b" in [x.codigo for x in p.pasos]
    directa = M6.clase_hec14_de_la_piedra(d50=p.d50, D=0.9)
    assert directa.clase == 4 and directa.ancho_final == pytest.approx(
        3 * 0.9 + 2 / 3 * 5.4, rel=REL_FORMULA)
    sin_clase = M6.clase_hec14_de_la_piedra(d50=0.6, D=0.9)
    assert sin_clase.clase is None
    # La sustitucion del paso nombra la clase MAYOR de la tabla y su D50.
    mayor = sin_clase.paso.sustitucion[1]
    assert mayor.valor == pytest.approx(0.55, rel=REL_TRANSPORTE)
    assert mayor.procedencia == "clase 6 de la Tabla 10.1"
    assert any("supera la mayor clase" in x for x in
               M6._avisos_de_la_piedra(sin_clase, espesor=1.0, longitud=5.0))
    # En A-01 la clase de la piedra es la misma del apron: no se repite.
    a01 = _punto(corrida_manual, "A-01")
    assert a01.proteccion.clase_de_la_piedra.clase == a01.proteccion.apron.clase
    assert not any("piedra que el proyecto pone" in x for x in a01.avisos())


def test_aud5_la_regla_envolvente_toma_el_mayor_y_manual_reproduce_lo_de_antes(
        corrida_base):
    """
    Hallazgo 5 (iv), y la decision del dueño del 2026-11-12: la envolvente
    es el valor de archivo y «manual» la alternativa barrible que deja lo
    adoptado, como antes. A-02: Laushey 0.274 m (clase 4), la Ec. (10.4) pide
    menos piedra (clase 1); rige Laushey, con 2.2·0.35 = 0.770 m y 6·0.9 =
    5.40 m de la clase 4.
    """
    a02 = _punto(corrida_base, "A-02")
    r, seccion = a02.resultado.resultado_hidraulico, a02.resultado.seccion
    assert ca.valor(CRITERIO_REGLA) == "envolvente_hec14"
    manual = _con_regla("manual", lambda: M6.proteccion_salida(
        V=r.V_salida, resultado=r, seccion=seccion))
    assert manual.espesor == pytest.approx(manual.espesor_adoptado,
                                           rel=REL_TRANSPORTE)
    assert manual.espesor == pytest.approx(1.75 * manual.d50, rel=REL_FORMULA)
    assert manual.longitud == pytest.approx(5.0, rel=REL_TRANSPORTE)
    assert "6.6c" not in [x.codigo for x in manual.pasos]
    env = M6.proteccion_salida(V=r.V_salida, resultado=r, seccion=seccion)
    assert env.d50 == pytest.approx(manual.d50, rel=REL_TRANSPORTE)
    assert env.d50_laushey == pytest.approx(manual.d50, rel=REL_TRANSPORTE)
    assert env.espesor == pytest.approx(2.2 * 0.35, rel=REL_FORMULA)
    assert env.longitud == pytest.approx(6 * 0.9, rel=REL_FORMULA)
    assert env.espesor_adoptado == pytest.approx(manual.espesor,
                                                 rel=REL_FORMULA)
    assert "6.6c" in [x.codigo for x in env.pasos]
    assert any("rige la envolvente" in x and "rige Laushey" in x
               for x in env.avisos)
    # Sin apron evaluable la envolvente no tiene con que comparar: rige
    # Laushey con lo adoptado y se dice.
    sin_apron = M6._regla_de_la_proteccion(
        regla="envolvente_hec14", d50_laushey=0.6, mult_espesor=1.75,
        longitud_adoptada=5.0, apron=None)
    assert sin_apron.d50 == pytest.approx(0.6, rel=REL_TRANSPORTE)
    assert sin_apron.espesor == pytest.approx(1.75 * 0.6, rel=REL_FORMULA)
    assert sin_apron.longitud == pytest.approx(5.0, rel=REL_TRANSPORTE)
    assert sin_apron.paso is None and not sin_apron.rige_la_envolvente
    assert len(sin_apron.avisos) == 1
    assert "no es evaluable" in sin_apron.avisos[0]
    with pytest.raises(DatoInvalidoError):
        M6._regla_de_la_proteccion(
            regla="la_que_sea", d50_laushey=0.3, mult_espesor=1.75,
            longitud_adoptada=5.0, apron=None)


def test_aud6_la_hoya_dice_desde_que_cota_se_mide(corrida_base):
    """
    Hallazgo 6: HEC-14 Cap. 5 no define la referencia de hs. La fija el
    criterio [A] 'referencia_profundidad_socavacion' (por defecto el fondo
    del cauce receptor) y se entrega la cota del fondo de la hoya.
    """
    a01 = _punto(corrida_base, "A-01")
    r, seccion = a01.resultado.resultado_hidraulico, a01.resultado.seccion
    s = M6.socavacion_salida(resultado=r, seccion=seccion, declarada_m=1.0,
                             cota_fondo_receptor=41.30, cota_solera_salida=41.99)
    assert s.referencia == M6.REFERENCIA_FONDO
    assert s.cota_fondo_de_la_hoya == pytest.approx(41.30 - 1.0, rel=REL_FORMULA)
    ca.establecer_valor_dinamico("referencia_profundidad_socavacion",
                                 "solera_de_salida")
    try:
        sol = M6.socavacion_salida(resultado=r, seccion=seccion, declarada_m=1.0,
                                   cota_fondo_receptor=41.30,
                                   cota_solera_salida=41.99)
    finally:
        ca.quitar_valor_dinamico("referencia_profundidad_socavacion")
    assert sol.cota_fondo_de_la_hoya == pytest.approx(41.99 - 1.0,
                                                      rel=REL_FORMULA)
    assert sol.pasos[-1].elecciones[0].clave_criterio == \
        "referencia_profundidad_socavacion"
    # El paso 6.14 nombra la referencia que se uso y su resultado es la cota.
    for s_, nombre in ((s, "el fondo del cauce receptor"),
                       (sol, "la solera de salida")):
        p614 = s_.pasos[-1]
        assert p614.codigo == "6.14"
        assert p614.resultado.simbolo == "cota del fondo de la hoya"
        assert any(nombre in m.procedencia for m in p614.sustitucion)
        assert p614.resultado.valor == pytest.approx(s_.cota_fondo_de_la_hoya,
                                                     rel=REL_FORMULA)


def test_aud8_la_nota_5a_avisa_el_limo_no_cohesivo():
    f = M6.requisito_de_filtro(pasa_200_pct=70.0, tipo_lecho="no_cohesivo")
    assert any("limos no cohesivos" in x for x in f.avisos)
    assert not M6.requisito_de_filtro(pasa_200_pct=30.0,
                                      tipo_lecho="no_cohesivo").avisos
    for pasa in (40.0, 50.0):    # la mitad exacta no es «mas de la mitad»
        assert not M6.requisito_de_filtro(pasa_200_pct=pasa,
                                          tipo_lecho="no_cohesivo").avisos, pasa
    assert not M6.requisito_de_filtro(pasa_200_pct=70.0,
                                      tipo_lecho="cohesivo").avisos


def test_aud9_el_tirante_de_borde_bajo_control_de_salida_se_avisa(corrida_base):
    """
    Hallazgo 9: con control de salida y el TW bajo el critico la velocidad se
    toma al tirante critico, y HEC-14 3.1.3 dice que en el borde es menor:
    V, Fr y d50 quedan subestimados. Se avisa.
    """
    from dataclasses import replace
    r = _punto(corrida_base, "A-01").resultado.resultado_hidraulico
    salida = replace(r, control_gobernante=ControlGobernante.SALIDA,
                     y_salida_m=r.y_critico)
    assert any("cota inferior" in x for x in M6._aviso_tirante_de_borde(salida))
    assert not M6._aviso_tirante_de_borde(r)     # control de entrada


def test_aud9_el_terreno_y_el_lecho_que_no_concuerdan_se_avisan():
    p = M6.proteccion_salida(V=_V(1.0),
                             tipo_terreno="graduado_grava_a_piedras_mayor_20cm",
                             regimen_flujo="intermitente", tipo_lecho="cohesivo")
    assert any("no concuerda con el lecho" in x for x in p.avisos)
    q = M6.proteccion_salida(V=_V(1.0), tipo_terreno="arcilla_fina",
                             regimen_flujo="intermitente", tipo_lecho="cohesivo")
    assert not any("no concuerda" in x for x in q.avisos)
    g = M6.proteccion_salida(V=_V(1.0), tipo_terreno="grava_fina",
                             regimen_flujo="intermitente",
                             tipo_lecho="no_cohesivo")
    assert not any("no concuerda" in x for x in g.avisos)
    a = M6.proteccion_salida(V=_V(1.0), tipo_terreno="arcilla_fina",
                             regimen_flujo="intermitente",
                             tipo_lecho="no_cohesivo")
    assert any("no concuerda con el lecho" in x for x in a.avisos)
