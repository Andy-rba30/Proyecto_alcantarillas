"""
tests/test_t3_familia_c.py
==========================
Aceptacion de T-3 de la cadena T: «Familia C: el marco de concreto se
dimensiona» (INF-0.4, §0 del INFORME, punto 4 de «lo que falta»).

Lo que este archivo fija, por los cuatro puntos del prompt:

  1. Los siete criterios del cajon tienen VALOR DE ARCHIVO, cada uno con su
     fila nombrada por clave y su cita verificada contra la pagina:
       n_manning_cajon         'concrete_boxes' [C], HDS-5 Tabla B.1, fila
                               «Concrete Boxes / Smooth»: (0.012, 0.015).
                               Hasta la auditoria de T-3 (H1) era la fila
                               'concreto_afinado' [N->] de la Tabla N 09,
                               (0.011, 0.014), que queda como alternativa;
                               las correcciones viven en
                               tests/test_t3_correcciones_auditoria.py
       embocadura_cajon        'cajon_concreto_aletas_30_75' [A], Tabla A.1
                               Carta 8 escala 1 (Forma 1)
       ke_entrada_cajon        'cajon_aletas_30_75_escuadra' [C], Tabla C.2,
                               0.4, la MISMA embocadura
       n_celdas_cajon          1 [A] (num. 4.1.1.3.4 a) recomienda seccion
                               unica ante arrastre)
       espesor_pared_cajon     0.20 m [A], piso de la E.060 num. 14.5.3.2
                               (muros exteriores de sotanos y cimentaciones)
                               POR ANALOGIA
       cobertura_minima_cajon  0.3048 m [A], piso de la fila del TUBO de
                               concreto de la Tabla 12.6.6.3-1 POR ANALOGIA
       secciones_cajon_normalizadas
                               la progresion con que C-01 dimensiona desde C7
                               -- PARADA (c): la del prompt deja a C-01 sin
                               dimensionar, ver el informe --.
     Ninguno mueve una seccion ni un HW ya fijados: los valores de archivo son
     los que la guia de perfil y la suite declaraban en caliente, y la carga
     de aletas frente a cabezal recto se midio (0.589 contra 0.629 m) y se
     dejo la de hoy, como pide la precision del orquestador.
  2. VC2 -- la cota de salida frente al fondo del canal aguas abajo, con la
     tolerancia constructiva de EG-2013 503.11 g) --, como AVISO; y la
     sobreelevacion y el remanso aguas arriba del canal, como aviso, con la
     seccion medida del canal cuando viene y «no evaluado» cuando no.
  3. La geometria del marco (B, H, N, espesores, ancho y canto exteriores,
     cotas de fondo, de clave interior y exterior) en `modelos.GeometriaMarco`
     y en M7; y 7.A, G1 y G2 corriendo para C-01 del fixture con los datos
     del canal declarados.
  4. V6 con N > 1 publica el reparto Q/N, la separacion entre celdas y el
     ancho total, y sigue sin aceptar la multicelda (EXT-2-01).

LOS ESPERADOS SALEN DE LA FUENTE O DE LA CUENTA A MANO, no de la salida del
programa: 12.0 in * 0.0254, 200 mm de la E.060, las celdas de la Tabla A.1 y
de la C.2 leidas en el PDF, la longitud de C-01 por la formula de T-6 y el
tirante normal del canal por una biseccion escrita aqui.

ESCRITO EN ROJO: los tests de aceptacion llevaban `xfail(strict=True)` y se
midieron contra `df1b23c` antes de tocar el codigo; el recuento esta en el
informe de la sesion. Los que valen antes y despues se nombran
`..._invariante`.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import constantes_normativas as cn
from src import servicio
from src import modelos
from src.modelos import (DatoInvalidoError, EstadoDeVerificacion, Familia,
                         FormaSeccion, PuntoCritico, SeccionReceptor,
                         SeccionRectangular, TipoMaterial)
from src.modulos import M5_verificaciones as M5
from src.modulos import M7_geometria as M7
from src.modulos.M0_carga import cargar_puntos
from src.modulos.M2_material import catalogo
from src.normativa import registro
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import declarados

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"

CAJON = ("n_manning_cajon", "embocadura_cajon", "ke_entrada_cajon",
         "n_celdas_cajon", "espesor_pared_cajon", "cobertura_minima_cajon",
         "secciones_cajon_normalizadas")

# Lo que la guia de perfil y la suite declaraban EN CALIENTE hasta T-3. Los
# valores de archivo tienen que reproducirlo: es la condicion de la parada (c).
DECLARADOS_HASTA_T3 = {
    "embocadura_cajon": "cajon_concreto_aletas_30_75",
    "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
    "n_manning_cajon": "concreto_afinado",
    "n_celdas_cajon": 1,
    "secciones_cajon_normalizadas": ((1.20, 0.90), (1.50, 1.20), (2.00, 1.50)),
    "espesor_pared_cajon": 0.20,
    "cobertura_minima_cajon": 0.3048,
}

def _declarados_en_lista():
    """Las siete declaraciones en la forma en que las escribe la CLI."""
    return {k: (list(map(list, v)) if isinstance(v, tuple) else v)
            for k, v in DECLARADOS_HASTA_T3.items()}


# La fila C-01 del fixture con la coronacion que la guia de perfil le pone, y
# los datos del canal de la guia (caudal y pendiente del CANAL, Sec. 2.3).
CORONACION_GUIA = 38.30
EXTERNOS_GUIA = {"globales": {"TW_m": 0.3, "L_hidraulico_m": 120.0},
                 "puntos": {"C-01": {"Q_m3s": 0.85, "S_cauce": 0.006,
                                     "S_conducto": 0.006}}}

# La seccion MEDIDA del canal que este archivo declara para medir el remanso.
# Es una sonda, no un levantamiento: canal revestido de 1.00 m de solera,
# talud 1:1, n = 0.015.
CANAL = {"b_m": 1.00, "z_HV": 1.0, "S": 0.006, "n": 0.015,
         "altura_total_m": 1.20}

# --- La aritmetica escrita, independiente del codigo -------------------------
PULGADA_M = 0.0254
COBERTURA_TUBO_IN = 12.0                       # Tabla 12.6.6.3-1, fila del tubo
E060_MUROS_EXTERIORES_MM = 200.0               # E.060 num. 14.5.3.2
# Longitud de C-01 por la formula de T-6, a mano: ancho 9.60, H = 39.10 -
# 36.90 = 2.20 en los dos extremos (plataforma horizontal), talud 2.0,
# esviaje 30 grados, S = 0.006.
L_C01 = (9.60 + 2.0 * (2.20 + 2.20)) / (math.cos(math.radians(30.0))
                                        - 2.0 * 0.006)
SALIDA_C01 = 36.90 - 0.006 * L_C01             # 36.7707...
DESAJUSTE_C01 = SALIDA_C01 - 36.20             # +0.5707 m sobre el canal

# Tolerancias con nombre. ABS: la cuenta a mano y el programa hacen la misma
# aritmetica en doble precision y difieren, a lo sumo, en el orden de las
# operaciones. TOL_RESULTADO: un HW escrito con tres decimales. TOL_BISECCION:
# la biseccion de aqui contra el brentq de M3, que paran con criterios
# distintos; TOL_LONGITUD la propaga a dh/S (se divide por S = 0.006).
ABS = 1e-9
TOL_RESULTADO = 5e-4
TOL_BISECCION = 1e-6
TOL_LONGITUD = TOL_BISECCION / CANAL["S"]


def _tirante_normal_a_mano(Q, b, z, S, n):
    """Biseccion sobre Manning en un trapecio, escrita aqui y no en M3."""
    def q(y):
        A = (b + z * y) * y
        P = b + 2.0 * y * math.sqrt(1.0 + z * z)
        return (1.0 / n) * A * (A / P) ** (2.0 / 3.0) * math.sqrt(S)
    lo, hi = 1e-9, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if q(mid) > Q:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def _csv_con_coronacion(tmp_path, coronacion=CORONACION_GUIA):
    lineas = CSV.read_text(encoding="utf-8").splitlines()
    salida = []
    for linea in lineas:
        if linea.startswith("C-01,"):
            assert linea.endswith(",,,"), linea
            linea = linea + f"{coronacion:.2f}"
        salida.append(linea)
    ruta = tmp_path / "puntos.csv"
    ruta.write_text("\n".join(salida) + "\n", encoding="utf-8")
    return ruta


def _externos(tmp_path, extra_c01=None):
    datos = json.loads(json.dumps(EXTERNOS_GUIA))
    if extra_c01:
        datos["puntos"]["C-01"].update(extra_c01)
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, {"luz_m": 2.75})


def _c01(informe):
    return next(p for p in informe.puntos if p.punto.id == "C-01")


@pytest.fixture
def corrida_guia(tmp_path):
    """La corrida de la guia, SIN declarar nada del cajon."""
    informe = servicio.correr(_csv_con_coronacion(tmp_path),
                              _externos(tmp_path),
                              alcance=servicio.ALCANCE_PERFIL)
    return informe


# ===========================================================================
# 1 · Los siete del cajon con valor de archivo
# ===========================================================================

@pytest.mark.parametrize("clave", CAJON)
def test_los_siete_del_cajon_tienen_valor_de_archivo(clave):
    c = ca.CRITERIOS[clave]
    assert c.valor is not None
    assert c.nivel == ca.NIVEL_PERFIL
    assert c.sensibilidad, "un [A] de perfil lleva ventana"
    assert c.resolucion is not None


@pytest.mark.parametrize("clave", [c for c in CAJON
                                   if c != "n_manning_cajon"])
def test_el_valor_de_archivo_es_el_que_la_guia_declaraba(clave):
    """
    La parada (c): ningun valor de archivo mueve una SECCION ya fijada. Seis
    de los siete son lo que la guia declaraba. 'n_manning_cajon' SALIO DE
    ESTE PARAMETRIZADO en las correcciones de la auditoria (H1): su valor de
    archivo es desde entonces la fila del cajon de la Tabla B.1 del HDS-5,
    que mueve el tirante y el HW de salida de C-01 y no su seccion; lo mide
    `tests/test_t3_correcciones_auditoria.py`.
    """
    valor = ca.CRITERIOS[clave].valor
    esperado = DECLARADOS_HASTA_T3[clave]
    if clave == "secciones_cajon_normalizadas":
        assert tuple(tuple(p) for p in valor) == esperado
    elif isinstance(esperado, float):
        assert valor == pytest.approx(esperado, abs=ABS)
    else:
        assert valor == esperado


def test_ninguno_del_cajon_queda_entre_los_de_perfil_sin_valor():
    sin_valor = set(ca.criterios_de_perfil_sin_valor())
    assert not sin_valor & set(CAJON)


def test_la_fila_de_manning_es_la_de_afinado_con_el_corrimiento_corregido_invariante():
    """
    Tabla N 09, grupo A.2, a. Concreto, fila «afinado», pag. impresa 75: el
    PDF imprime la columna de valores un renglon mas arriba que sus rotulos,
    y en la linea de «afinado» se leen los de la fila siguiente (0.013 /
    0.015 / 0.017). Corrigiendo el corrimiento son 0.011 / 0.012 / 0.014: la
    evidencia es INTERNA de la pagina (el bloque A.1 alineado; la cita de
    Ven Te Chow que este docstring traia no es verificable en normas/, H10).
    Es la lectura corregida del tubo recto, y desde la auditoria de T-3 la
    ALTERNATIVA barrible del n del marco.
    """
    assert cn.MANNING["concreto_afinado"] == pytest.approx(
        (0.011, 0.014), rel=REL_TRANSPORTE)
    assert cn.MANNING["concreto_tubo_recto"] == pytest.approx(
        (0.010, 0.013), rel=REL_TRANSPORTE)


def test_la_embocadura_y_su_ke_son_la_misma_aleta_de_30_a_75_grados():
    """
    Carta 8, escala 1, «30° to 75° wingwall flares», Forma 1 (Tabla A.1, PDF
    197): K 0.026, M 1.0, c 0.0347, Y 0.81. Y la fila de la Tabla C.2 (pag.
    impresa C.6, PDF 216) «Square-edged at crown» bajo «Wingwalls at 30° to
    75° to barrel»: 0.4. La carta y el ke hablan de la MISMA embocadura.
    """
    carta = cn.HDS5_INLET[ca.CRITERIOS["embocadura_cajon"].valor]
    assert carta["forma"] == 1
    assert (carta["K"], carta["M"], carta["c"], carta["Y"]) == pytest.approx(
        (0.026, 1.0, 0.0347, 0.81), rel=REL_TRANSPORTE)
    fila = cn.KE_HDS5_C2[ca.CRITERIOS["ke_entrada_cajon"].valor]
    assert fila["ke"] == pytest.approx(0.4, rel=REL_TRANSPORTE)
    assert "30" in fila["agrupacion"] and "75" in fila["agrupacion"]
    assert fila["bloque"] == "Box, Reinforced Concrete"
    assert ca.CRITERIOS["ke_entrada_cajon"].resolucion.elegido_por \
        == "embocadura_cajon"


def test_la_cobertura_es_el_piso_de_la_fila_del_tubo_por_analogia():
    c = ca.CRITERIOS["cobertura_minima_cajon"]
    assert c.valor == pytest.approx(COBERTURA_TUBO_IN * PULGADA_M, abs=ABS)
    assert c.etiqueta == "A"
    # Lo que la fuente SI cubre para un cajon -- la losa sin cobertura -- y
    # la fila del tubo que se aplica por analogia, en el registro.
    reg = registro.construir()
    assert reg.cita("AASHTO_LRFD_9.T12.6.6.3-1")
    assert c.vacio_verificado


def test_el_espesor_es_el_piso_de_la_E060_para_muros_enterrados():
    c = ca.CRITERIOS["espesor_pared_cajon"]
    assert c.valor == pytest.approx(E060_MUROS_EXTERIORES_MM / 1000.0, abs=ABS)
    cita = registro.construir().cita("E060.14.5.3.2")
    assert cita.pagina_impresa == "134"
    assert "200" in cita.texto_literal.texto
    assert "muros" in cita.texto_literal.texto


def test_la_progresion_del_prompt_entra_por_la_puerta_y_deja_a_C01_sin_dimensionar(
        tmp_path):
    """
    PARADA (c), medida: la progresion que la cadena propone (anchos 1.00 a
    4.00 paso 0.50 por alturas 1.00 a 3.00 paso 0.25, por area creciente) no
    contiene el 1.20 x 0.90 con que C-01 dimensiona, y con ella C-01 no
    dimensiona: V7 (flotacion) incumple en los siete primeros escalones,
    porque una altura de 1.00 m o mas deja menos relleno sobre la losa, y el
    octavo (1.00 x 2.00 m) deja la clave por encima de la subrasante y
    detiene el material. Se deja como alternativa declarable, y el valor de
    archivo sigue siendo el que no mueve nada.
    """
    anchos = [1.00 + 0.50 * i for i in range(7)]
    alturas = [1.00 + 0.25 * i for i in range(9)]
    grid = sorted(((b, h) for b in anchos for h in alturas),
                  key=lambda p: (p[0] * p[1], p[1]))
    with declarados({"secciones_cajon_normalizadas": grid}):
        informe = servicio.correr(_csv_con_coronacion(tmp_path),
                                  _externos(tmp_path),
                                  alcance=servicio.ALCANCE_PERFIL)
    c01 = _c01(informe)
    assert not c01.dimensionado
    motivos = [it.motivo or "" for it in c01.traza]
    assert len(motivos) == 8, motivos
    assert sum("incumple V7" in m for m in motivos[:7]) == 7
    assert "subrasante" in motivos[7]


# ===========================================================================
# 2 · C-01 dimensiona sin declarar nada: 7.A, G1, G2, VC1, VC2
# ===========================================================================

def test_C01_dimensiona_con_los_valores_de_archivo(corrida_guia):
    c01 = _c01(corrida_guia)
    assert c01.dimensionado, [b.detalle for b in c01.bloqueos]
    seccion = c01.resultado.seccion
    assert isinstance(seccion, SeccionRectangular)
    assert (seccion.B, seccion.H) == pytest.approx((1.20, 0.90), abs=ABS)
    assert c01.resultado.resultado_hidraulico.HW == pytest.approx(
        0.589, abs=TOL_RESULTADO)
    codigos = {v.codigo for _, v in c01.verificaciones()}
    assert {"G1", "G2", "VC1", "VC2"} <= codigos
    assert c01.geometria.tamizado is not None          # 7.A con la seccion
    assert not any(b.criterio in CAJON for b in c01.bloqueos)


def test_los_valores_de_archivo_reproducen_la_corrida_declarada_en_caliente(
        tmp_path):
    """
    Mismo diseño de C-01 con el archivo que con las siete declaraciones.

    REESCRITO EN LAS CORRECCIONES DE LA AUDITORIA (H1), declarandolo: las
    siete declaraciones eran las de la guia, con 'n_manning_cajon' =
    'concreto_afinado', y el archivo vale hoy 'concrete_boxes'. Se mide lo
    mismo con el n de archivo declarado en caliente -- identico diseño --, y
    se mide aparte lo que la fila de la guia mueve: el HW de control de
    entrada, que no depende de n, no se mueve; el tirante normal si.
    """
    sin = servicio.correr(_csv_con_coronacion(tmp_path), _externos(tmp_path),
                          alcance=servicio.ALCANCE_PERFIL)
    declaradas = dict(_declarados_en_lista(), n_manning_cajon="concrete_boxes")
    with declarados(declaradas):
        con = servicio.correr(_csv_con_coronacion(tmp_path),
                              _externos(tmp_path),
                              alcance=servicio.ALCANCE_PERFIL)
    with declarados(_declarados_en_lista()):
        guia = servicio.correr(_csv_con_coronacion(tmp_path),
                               _externos(tmp_path),
                               alcance=servicio.ALCANCE_PERFIL)
    a, b, g = _c01(sin), _c01(con), _c01(guia)
    assert a.dimensionado and b.dimensionado and g.dimensionado
    ra, rb = a.resultado.resultado_hidraulico, b.resultado.resultado_hidraulico
    rg = g.resultado.resultado_hidraulico
    assert ra.HW == rb.HW and ra.y_normal == rb.y_normal
    assert a.geometria.cota_salida == b.geometria.cota_salida
    assert (a.resultado.seccion.B, a.resultado.seccion.H) == (
        g.resultado.seccion.B, g.resultado.seccion.H)
    assert ra.HW == pytest.approx(rg.HW, abs=ABS)
    assert ra.y_normal > rg.y_normal       # n_max 0.015 > 0.014


# ===========================================================================
# 2 · VC2: la cota de salida frente al fondo del canal aguas abajo
# ===========================================================================

def _punto_c01():
    return next(p for p in cargar_puntos(CSV) if p.id == "C-01")


def test_la_tolerancia_de_VC2_es_la_de_EG2013_y_es_un_A_con_ventana():
    c = ca.CRITERIOS["desajuste_empalme_canal_m"]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.valor == pytest.approx(0.010, abs=ABS)       # -10 mm a +10 mm
    assert tuple(c.sensibilidad) == pytest.approx((0.010, 0.020),
                                                  rel=REL_TRANSPORTE)
    reg = registro.construir()
    assert "10 mm" in reg.cita("EG2013.503.11g#COTAS").texto_literal.texto
    assert "2" in reg.cita("EG2013.501.07").texto_literal.texto


@pytest.mark.parametrize("cota_salida, estado", [
    (36.205, EstadoDeVerificacion.CUMPLE),       # +5 mm, dentro
    (36.195, EstadoDeVerificacion.CUMPLE),       # -5 mm, dentro
    (36.215, EstadoDeVerificacion.INDICADOR),    # +15 mm: escalon hacia arriba
    (36.185, EstadoDeVerificacion.INDICADOR),    # -15 mm: la salida enterrada
])
def test_VC2_es_una_banda_de_dos_lados_y_avisa_sin_detener(cota_salida, estado):
    v = M7.vc2_empalme_canal(punto=_punto_c01(), cota_salida_m=cota_salida)
    assert v.codigo == "VC2"
    assert v.estado is estado
    assert v.cumple                      # un aviso NUNCA descarta la seccion
    assert v.valor_obtenido == pytest.approx(cota_salida - 36.20, abs=ABS)
    assert v.paso is not None and v.paso.umbral is not None


def test_VC2_de_C01_avisa_el_desajuste_que_deja_la_cota_de_entrada_adoptada(
        corrida_guia):
    c01 = _c01(corrida_guia)
    vc2 = next(v for _, v in c01.verificaciones() if v.codigo == "VC2")
    assert vc2.estado is EstadoDeVerificacion.INDICADOR
    assert vc2.valor_obtenido == pytest.approx(DESAJUSTE_C01, abs=ABS)
    assert vc2 in c01.con_aviso()
    assert any(a.startswith("VC2") for a in c01.avisos())


def test_VC2_no_existe_fuera_de_la_familia_C_invariante(corrida_guia):
    for p in corrida_guia.puntos:
        if p.punto.familia is not Familia.C:
            assert all(v.codigo != "VC2" for _, v in p.verificaciones())


@pytest.mark.parametrize("malo", [-0.01, float("nan"), float("inf")])
def test_VC2_tiene_segunda_linea_sobre_su_tolerancia(malo):
    from tests.apoyo.criterios import con_valor
    with con_valor("desajuste_empalme_canal_m", malo,
                   motivo="segunda linea: un valor que burla la puerta"):
        with pytest.raises(DatoInvalidoError):
            M7.vc2_empalme_canal(punto=_punto_c01(), cota_salida_m=36.20)


# ===========================================================================
# 2 · El remanso aguas arriba del canal: aviso, nunca umbral
# ===========================================================================

def test_sin_la_seccion_del_canal_el_remanso_sale_no_evaluado(corrida_guia):
    c01 = _c01(corrida_guia)
    rem = c01.geometria.remanso_canal
    assert rem is not None and not rem.evaluado
    assert any("remanso" in a.lower() and "no se evalu" in a
               for a in c01.avisos())


def test_con_la_seccion_medida_el_remanso_sale_con_la_cuenta_a_mano(tmp_path):
    """
    REESCRITO EN LAS CORRECCIONES DE LA AUDITORIA (H2 y H3), declarandolo.
    Este test fijaba «AL MENOS dh/S» sobre una corrida en que la cuenta no
    concluye por DOS razones: VC2 de C-01 esta fuera de tolerancia (+0.571
    m: el HW sale de una descarga libre que el canal no tiene), y la sonda
    -- 1.00 m de solera, talud 1:1, n 0.015, S 0.006 -- es un canal de
    pendiente FUERTE (y_n = 0.33 < y_c = 0.37). Hoy el remanso sale
    evaluado, NO concluye por VC2 (la primera razon que se comprueba), y no
    presenta cifra alguna como cota; los tirantes del canal siguen
    publicandose y se comprueban a mano.
    """
    informe = servicio.correr(
        _csv_con_coronacion(tmp_path),
        _externos(tmp_path, {"seccion_receptor_medida": CANAL}),
        alcance=servicio.ALCANCE_PERFIL)
    c01 = _c01(informe)
    rem = c01.geometria.remanso_canal
    assert rem.evaluado and not rem.concluye
    y_n = _tirante_normal_a_mano(0.85, CANAL["b_m"], CANAL["z_HV"],
                                 CANAL["S"], CANAL["n"])
    assert rem.y_normal_canal_m == pytest.approx(y_n, abs=TOL_BISECCION)
    assert rem.y_critico_canal_m > rem.y_normal_canal_m     # canal fuerte
    assert rem.sobreelevacion_m is None and rem.longitud_minima_m is None
    assert rem.paso is not None
    assert any("remanso" in a.lower() and "no concluye" in a and "VC2" in a
               for a in c01.avisos())
    assert not any("AL MENOS" in a for a in c01.avisos())
    # Es un aviso: no hay verificacion que lo juzgue ni umbral.
    assert all(v.codigo != "REMANSO" for _, v in c01.verificaciones())


def test_si_la_obra_no_levanta_la_lamina_no_hay_remanso():
    canal_hondo = SeccionReceptor(b_m=0.30, z_HV=0.5, S=0.0005, n=0.030,
                                  altura_total_m=3.0)
    rem = M7.remanso_canal(punto=_punto_c01(), cota_entrada_msnm=36.90,
                           HW=0.20, Q=0.85, seccion_canal=canal_hondo)
    assert rem.evaluado
    assert rem.sobreelevacion_m < 0
    assert rem.longitud_minima_m == pytest.approx(0.0, abs=ABS_CERO)


# ===========================================================================
# 3 · La geometria del marco, disponible para quien la consuma
# ===========================================================================

def test_la_geometria_del_marco_con_la_cuenta_a_mano(corrida_guia):
    c01 = _c01(corrida_guia)
    g = c01.geometria.geometria_marco
    assert isinstance(g, modelos.GeometriaMarco)
    t = 0.20
    assert (g.B_m, g.H_m, g.celdas, g.espesor_m) == pytest.approx(
        (1.20, 0.90, 1, t), abs=ABS)
    assert g.ancho_exterior_m == pytest.approx(1.20 + 2 * t, abs=ABS)
    assert g.canto_exterior_m == pytest.approx(0.90 + 2 * t, abs=ABS)
    assert g.cota_fondo_interior_msnm == pytest.approx(36.90, abs=ABS)
    assert g.cota_clave_interior_msnm == pytest.approx(36.90 + 0.90, abs=ABS)
    assert g.cota_clave_exterior_msnm == pytest.approx(36.90 + 0.90 + t,
                                                       abs=ABS)
    assert g.cota_base_exterior_msnm == pytest.approx(36.90 - t, abs=ABS)
    assert g.relleno_sobre_losa_m == pytest.approx(38.95 - (36.90 + 0.90 + t),
                                                   abs=ABS)
    assert g.paso is not None


def test_la_clave_del_marco_es_la_misma_que_usan_V7_y_7A():
    punto = _punto_c01()
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                        forma=FormaSeccion.RECTANGULAR)
    seccion = SeccionRectangular(1.20, 0.90)
    g = M7.geometria_marco(punto=punto, material=material, seccion=seccion)
    assert g.cota_clave_exterior_msnm == M5.cota_clave(
        punto=punto, material=material, seccion=seccion)


def test_un_tubo_no_lleva_geometria_de_marco(corrida_guia):
    for p in corrida_guia.puntos:
        if p.punto.familia is not Familia.C and p.geometria is not None:
            assert p.geometria.geometria_marco is None


def test_el_volcado_lleva_la_geometria_del_marco_y_el_remanso(corrida_guia):
    datos = cli.informe_json(corrida_guia)
    c01 = next(p for p in datos["puntos"] if p["id"] == "C-01")
    marco = c01["geometria"]["geometria_marco"]
    assert marco["B_m"] == pytest.approx(1.20, abs=TOL_RESULTADO)
    assert marco["cota_clave_exterior_msnm"] == pytest.approx(
        38.00, abs=TOL_RESULTADO)
    assert c01["geometria"]["remanso_canal"]["evaluado"] is False


# ===========================================================================
# 4 · V6 con N > 1: reparto, separacion y ancho total, sin aceptar
# ===========================================================================

def _marco():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO,
                    forma=FormaSeccion.RECTANGULAR)


def test_V6_con_dos_celdas_publica_la_separacion_y_el_ancho_total():
    with declarados({**_declarados_en_lista(), "n_celdas_cajon": 2}):
        v = M5.v6_material_solido_arrastre(material=_marco(),
                                           seccion=SeccionRectangular(1.20,
                                                                      0.90),
                                           Q=0.85)
    assert not v.cumple                   # EXT-2-01: sigue sin aceptarse
    texto = str(v.valor_obtenido)
    assert "2 celda" in texto
    # Q/N = 0.425 m3/s por celda; tabique = t = 0.20; ancho total
    # 2*1.20 + 1*0.20 + 2*0.20 = 3.00 m.
    assert "0.425" in texto
    assert "3.00" in texto


def test_V6_con_una_celda_sigue_cumpliendo_invariante():
    with declarados(_declarados_en_lista()):
        v = M5.v6_material_solido_arrastre(material=_marco())
    assert v.cumple and "1 celda" in v.valor_obtenido


# ===========================================================================
# Guardias de segunda linea y la cuenta del multicelda en un solo sitio
# ===========================================================================

def test_el_remanso_rechaza_un_canal_sin_pendiente():
    """
    Segunda linea (forma MAT-D13): L = dh / S no se divide por cero.

    REESCRITO EN LAS CORRECCIONES DE LA AUDITORIA (H8): era VACUO -- seguia
    verde con la guardia mutada a `S >= 0`, porque con S = 0 la excepcion
    salia de Manning (`M3.tirante_normal_trapecial`, campo
    'seccion_receptor') y no de la guardia que dice medir --. Ahora se
    comprueba el CAMPO de la guardia del remanso.
    """
    plano = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.0, n=0.015,
                            altura_total_m=1.2)
    with pytest.raises(DatoInvalidoError) as exc:
        M7.remanso_canal(punto=_punto_c01(), cota_entrada_msnm=36.90,
                         HW=0.60, Q=0.85, seccion_canal=plano)
    assert exc.value.campo == "seccion_receptor_medida"


def test_el_ancho_del_marco_de_n_celdas_es_una_cuenta_y_vive_en_la_seccion():
    """
    N*B + (N - 1)*t + 2*t, a mano: con B = 1.20 y t = 0.20, una celda da
    1.60 m (= ancho_exterior) y dos dan 2.40 + 0.20 + 0.40 = 3.00 m.
    """
    s = SeccionRectangular(1.20, 0.90)
    assert s.ancho_exterior_de_celdas(0.20, 1) == pytest.approx(
        s.ancho_exterior(0.20), abs=ABS)
    assert s.ancho_exterior_de_celdas(0.20, 2) == pytest.approx(3.00, abs=ABS)


def test_con_dos_celdas_la_geometria_del_marco_lleva_el_tabique():
    punto = _punto_c01()
    with declarados({**_declarados_en_lista(), "n_celdas_cajon": 2}):
        material = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                            forma=FormaSeccion.RECTANGULAR)
        g = M7.geometria_marco(punto=punto, material=material,
                               seccion=SeccionRectangular(1.20, 0.90))
    assert g.celdas == 2
    assert g.tabique_m == pytest.approx(0.20, abs=ABS)
    assert g.ancho_exterior_m == pytest.approx(3.00, abs=ABS)


def test_la_geometria_del_marco_no_existe_para_un_tubo():
    from src.modelos import SeccionCircular
    with pytest.raises(DatoInvalidoError):
        M7.geometria_marco(punto=_punto_c01(),
                           material=catalogo(TipoMaterial.CONCRETO_REFORZADO),
                           seccion=SeccionCircular(0.90))
