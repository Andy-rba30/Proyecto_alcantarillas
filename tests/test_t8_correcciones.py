"""
tests/test_t8_correcciones.py
=============================
Aceptacion de la PASADA DE CORRECCIONES de la segunda auditoria adversarial
de T-8 (proteccion de entrada y salida, Fase 6) y de las SEIS DECISIONES que
el dueño tomo sobre ella el 2026-11-12. Un bloque por hallazgo, con su ID (H1
a H15) y la decision que toca (D1 a D6).

QUE CAMBIA DE NUMERO, porque esta pasada SI mueve la linea base y el dueño lo
aprobo (ningun diametro ni material: eso no):

  * D1 · 'regla_espesor_longitud_proteccion_salida' vale «envolvente_hec14»:
    piedra = el mayor de Laushey y de la Ec. (10.4) de HEC-14; espesor y
    longitud = los mayores de lo adoptado y de la Tabla 10.1. En A-01 y A-02
    el d50 no se mueve (rige Laushey: 0.338 y 0.274 m), el espesor pasa de
    0.592 y 0.479 m a 0.770 m, y la longitud de 5.00 a 5.40 m. «manual» da
    exactamente los numeros de antes, y un test lo fija.
  * D3 · la duracion por criterio pasa de 30 min [C] a 360 min [A].
  * D6 · «sin enrocado» deja de existir: el d50 lleva siempre numero.

ROJO: SE ESCRIBIO PRIMERO, Y DESPUES SE REMIDIO, y se declara asi. Los tests
de H1 a H15 se escribieron con `xfail(strict=True)` antes de tocar el codigo.
Las decisiones del dueño llegaron con la pasada a medias y cambiaron lo que
varios debian afirmar (H1, H2, H11, D3): esos se reescribieron con el codigo
ya en marcha. El rojo que vale es por eso el MEDIDO sobre `df1b23c` (el arbol
de T-8 en `origin/main`), con el archivo final: el recuento esta en la ficha
T8-12 de `docs/decisiones_diferidas.md`. Los tests que alli salen verdes son
GUARDIAS que valen antes y despues --los bordes inclusivos que el codigo ya
resolvia bien y ningun test fijaba (los mutantes de banda de tolerancia de la
ficha T8-06) y la transcripcion entera de las tablas--.

DE DONDE SALE CADA ORACULO, porque ninguno es la salida del codigo:

  * el PDF, releido por quien escribio el test: HEC-14 (pags. impresas 1-2,
    3-3, 3-4, 3-6, 5-2, 5-3, 5-7, 10-1, 10-17 a 10-19; PDF 15, 34, 35, 37, 55,
    56, 60, 202, 218 a 220), el Manual de Hidrologia (Tabla Nº 11, pag.
    impresa 77, PDF 80) y EG-2013 (Tablas 511-02 y 511-06, pags. impresas
    1011 y 1015, PDF 1019 y 1023);
  * la ARITMETICA ESCRITA en el docstring de cada test, paso por paso.
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import servicio
from src.constantes_normativas import (
    HEC14_APRON_ALTURA_MAX_M, HEC14_SOCAVACION_CH, HEC14_SOCAVACION_COHESIVO,
    HEC14_SOCAVACION_CS, HEC14_SOCAVACION_NO_COHESIVO, V_MAX_NO_REVESTIDOS)
from src.modelos import (
    ControlGobernante, DatoInvalidoError, LimiteNumericoError, Magnitud,
    MaterialLecho, MetodoNoEvaluableError, SeccionCircular, TipoDeVeredicto)
from src.modulos import M11_reporte as M11
from src.modulos import M6_proteccion as M6
from src.normativa import fuentes as _fuentes
from src.normativa import registro as _registro
from tests.apoyo.aproximacion import REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_ANCHOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"

# Tolerancias de este archivo, nombradas (CLAUDE.md).
REL_EJEMPLO_IMPRESO = 1e-2   # la fuente imprime 2-3 cifras
REL_FORMULA = 1e-9           # una formula recomputada en el test
REL_ARITMETICA = 1e-3        # la aritmetica escrita con cuatro cifras
# La linea base imprime el d50 con tres decimales (0.338 / 0.274 m): media
# unidad del ultimo digito impreso.
ABS_IMPRESO_3_DECIMALES = 5e-4

M_POR_FT = 0.3048            # exacto por definicion
M_POR_IN = 0.0254            # exacto por definicion
FT3_POR_M3 = 1 / M_POR_FT ** 3

CRITERIO_REGLA = "regla_espesor_longitud_proteccion_salida"

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


def _con_regla(regla, funcion):
    """Ejecuta `funcion()` con la regla declarada en caliente, y la repone."""
    ca.establecer_valor_dinamico(CRITERIO_REGLA, regla)
    try:
        return funcion()
    finally:
        ca.quitar_valor_dinamico(CRITERIO_REGLA)


@pytest.fixture(scope="module")
def corrida_base(tmp_path_factory):
    """La corrida ancha SIN ningun dato de T-8, con la regla del archivo."""
    return _correr_ancho(tmp_path_factory.mktemp("base"))


@pytest.fixture(scope="module")
def corrida_manual(tmp_path_factory):
    """La misma corrida con la regla «manual»: los numeros de antes."""
    return _con_regla("manual",
                      lambda: _correr_ancho(tmp_path_factory.mktemp("manual")))


@pytest.fixture(scope="module")
def resultado_a01(corrida_base):
    return _punto(corrida_base, "A-01").resultado.resultado_hidraulico


def _tubo_lleno(resultado_a01, *, D, Q, TW, V=None):
    """
    Un resultado de descarga a seccion LLENA (y_salida = y_critico = D, sin
    ajuste de la Ec. 10.5), armado sobre el de A-01: el caso del auditor.
    """
    area = math.pi * D ** 2 / 4
    velocidad = Q / area if V is None else V
    return replace(resultado_a01, Q=Q, Q_celda_m3s=Q, TW_m=TW, y_salida_m=D,
                   y_critico=D, numero_celdas=1,
                   control_gobernante=ControlGobernante.ENTRADA,
                   V_salida=Magnitud("V_salida", velocidad, "m/s",
                                     "seccion llena, Q/A (dato del test)"))


def _por_la_salida_al_critico(resultado_a01, V):
    """Control de SALIDA con el TW bajo el critico: y_salida = y_c."""
    return replace(resultado_a01, control_gobernante=ControlGobernante.SALIDA,
                   y_salida_m=resultado_a01.y_critico, TW_m=0.10,
                   V_salida=Magnitud("V_salida", V, "m/s",
                                     "Q / A(y_c) (dato del test)"))


# ===========================================================================
# H1 (ALTA) · D1 · rige la envolvente, y alcanza al tamaño de la piedra
# ===========================================================================

def test_h1_con_la_envolvente_rige_la_piedra_de_hec14_cuando_pide_mas(
        resultado_a01):
    """
    El caso del auditor: tubo Ø 0.90 m a seccion llena, Q = 1.15 m3/s, TW =
    0.36 m (= 0.4·D justo: no se acota). A mano:

        A = π·0.9²/4 = 0.63617 m2;  V = 1.15/0.63617 = 1.8077 m/s
        Laushey: d50 = 1.8077²/(3.1·9.8) = 3.2678/30.38 = 0.10756 m
        HEC-14:  0.9^2.5 = 0.768433;  Q/(g^0.5·D^2.5) = 1.15/(3.13209·
                 0.768433) = 0.47781;  ^(4/3) = 0.37354
                 D50 = 0.2·0.9·0.37354·(0.9/0.36) = 0.16809 m  -> clase 3
        clase 3: L = 5·0.9 = 4.50 m, e = 2.4·0.25 = 0.60 m
        adoptado: e = 1.75·0.10756 = 0.18823 m, L = 5.00 m

    HEC-14 pide un 56 % mas de piedra que Laushey. Con la regla del archivo
    («envolvente_hec14») RIGE la de HEC-14: d50 = 0.168 m, espesor = max(
    1.75·0.16809 = 0.294, 0.60) = 0.60 m, longitud = max(5.00, 4.50) = 5.00
    m. El d50 de Laushey se sigue publicando.
    """
    r = _tubo_lleno(resultado_a01, D=0.9, Q=1.15, TW=0.36)
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(0.9))
    assert ca.valor(CRITERIO_REGLA) == "envolvente_hec14"
    assert p.rige_la_envolvente
    assert p.d50_laushey == pytest.approx(0.10756, rel=REL_ARITMETICA)
    assert p.apron.D50_requerido == pytest.approx(0.16809, rel=REL_ARITMETICA)
    assert p.d50 == pytest.approx(0.16809, rel=REL_ARITMETICA)
    assert p.clase_de_la_piedra.clase == 3 and p.apron.clase == 3
    assert p.espesor == pytest.approx(2.4 * 0.25, rel=REL_FORMULA)
    assert p.longitud == pytest.approx(5.0, rel=REL_FORMULA)
    assert p.espesor_adoptado == pytest.approx(0.18823, rel=REL_ARITMETICA)
    aviso = next(x for x in p.avisos if "rige la envolvente" in x)
    assert "0.108 -> 0.168" in aviso and "rige la Ec. (10.4)" in aviso
    assert "0.188 -> 0.600" in aviso
    # Con lo que rige ya no queda nada por debajo de HEC-14: no hay aviso de
    # piedra, de espesor ni de longitud cortos, ni del piso de 2·D50.
    assert not any("pide una piedra mayor" in x or "es menor que" in x
                   or "bajo el piso" in x for x in p.avisos)
    assert p.advertencias == M6.ADVERTENCIAS_PROTECCION_SALIDA_ENVOLVENTE
    # El paso 6.1 sigue siendo Laushey, y el 6.6c dice lo que rige.
    assert p.paso.resultado.valor == pytest.approx(0.10756, rel=REL_ARITMETICA)
    paso_regla = next(x for x in p.pasos if x.codigo == "6.6c")
    assert paso_regla.resultado.valor == pytest.approx(0.60, rel=REL_FORMULA)


def test_h1_con_manual_la_piedra_que_hec14_pide_de_mas_se_avisa(
        resultado_a01):
    """
    Mismo caso con la regla «manual»: rigen Laushey (0.108 m) y lo adoptado
    (0.188 m, 5.00 m), y los avisos del contraste dicen lo que HEC-14 pide de
    mas: la piedra (0.168 m), y el espesor (0.600 m, clase 3).
    """
    r = _tubo_lleno(resultado_a01, D=0.9, Q=1.15, TW=0.36)
    p = _con_regla("manual", lambda: M6.proteccion_salida(
        V=r.V_salida, resultado=r, seccion=SeccionCircular(0.9)))
    assert not p.rige_la_envolvente
    assert p.d50 == pytest.approx(0.10756, rel=REL_ARITMETICA)
    assert p.d50 == pytest.approx(p.d50_laushey, rel=REL_FORMULA)
    assert p.espesor == pytest.approx(0.18823, rel=REL_ARITMETICA)
    assert p.longitud == pytest.approx(5.0, rel=REL_FORMULA)
    assert any("pide una piedra mayor que Laushey" in x and "0.168" in x
               and "0.108" in x for x in p.avisos), p.avisos
    assert any("espesor adoptado (0.188 m" in x and "0.600 m" in x
               for x in p.avisos)
    assert p.advertencias == M6.ADVERTENCIAS_PROTECCION_SALIDA


def test_h1_cuando_laushey_pide_mas_rige_laushey_con_la_clase_de_su_piedra(
        corrida_base):
    """
    A-01 de la linea base: Laushey 3.206²/30.38 = 0.3383 m; la Ec. (10.4)
    pide 0.2516 m. Rige Laushey, que es de la clase 4 (0.35 m) de la Tabla
    10.1: espesor 2.2·0.35 = 0.770 m y longitud 6·0.9 = 5.40 m.
    """
    p = _punto(corrida_base, "A-01").proteccion
    assert p.rige_la_envolvente
    assert p.d50 == pytest.approx(p.d50_laushey, rel=REL_FORMULA)
    assert p.apron.D50_requerido < p.d50
    assert p.clase_de_la_piedra.clase == 4
    assert p.espesor == pytest.approx(2.2 * 0.35, rel=REL_FORMULA)
    assert p.longitud == pytest.approx(6 * 0.9, rel=REL_FORMULA)
    aviso = next(x for x in p.avisos if "rige la envolvente" in x)
    assert "rige Laushey" in aviso and "0.592 -> 0.770" in aviso
    assert "5.00 -> 5.40" in aviso


@pytest.mark.parametrize("regla", ["manual", "envolvente_hec14"])
def test_h1_fuera_de_la_tabla_10_1_se_pide_el_disipador_con_las_dos_reglas(
        resultado_a01, regla):
    """
    Segundo caso del auditor: Ø 1.00 m, Q = 6.0 m3/s, V = 2.0 m/s, TW = 0.4 m
    (= 0.4·D), sin ajuste de la Ec. 10.5 (y = yc):

        Q/(g^0.5·D^2.5) = 6.0/3.13209 = 1.91566;  ^(4/3) = 2.3791
        D50 = 0.2·1.0·2.3791·(1.0/0.4) = 1.1896 m  >  0.55 m (clase 6)

    La Ec. (10.4) pide una piedra que no cabe en la Tabla 10.1. Con las dos
    reglas se avisa que la salida pide un disipador: con «envolvente_hec14»
    T-8 lo callaba.
    """
    r = _tubo_lleno(resultado_a01, D=1.0, Q=6.0, TW=0.4, V=2.0)
    p = _con_regla(regla, lambda: M6.proteccion_salida(
        V=r.V_salida, resultado=r, seccion=SeccionCircular(1.0)))
    assert p.apron.D50_requerido == pytest.approx(1.1896, rel=REL_ARITMETICA)
    assert p.apron.clase is None
    assert any("pide un disipador" in x for x in p.avisos), p.avisos


def test_h1_fuera_de_la_tabla_la_envolvente_da_cotas_inferiores_y_lo_dice(
        resultado_a01):
    """
    Mismo caso con la envolvente. La piedra que rige es la de la Ec. (10.4),
    1.1896 m (Laushey: 4/30.38 = 0.13167 m), que no cabe en la Tabla 10.1: la
    tabla no le da profundidad ni longitud. Lectura del proyecto, declarada:
    cotas inferiores con el limite que la fuente escribe para las piedras
    mayores, 2.0·D50 = 2.3792 m, y la longitud de su ultima clase, 8·D = 8.0
    m. Y el aviso dice que eso no es un diseño.
    """
    r = _tubo_lleno(resultado_a01, D=1.0, Q=6.0, TW=0.4, V=2.0)
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(1.0))
    assert p.d50_laushey == pytest.approx(0.13167, rel=REL_ARITMETICA)
    assert p.d50 == pytest.approx(1.1896, rel=REL_ARITMETICA)
    assert p.clase_de_la_piedra.clase is None
    assert p.espesor == pytest.approx(2.0 * p.d50, rel=REL_FORMULA)
    assert p.longitud == pytest.approx(8.0, rel=REL_FORMULA)
    assert any("COTAS INFERIORES" in x and "no un diseño" in x
               for x in p.avisos)


def test_h1_donde_hec14_no_es_evaluable_rige_laushey_y_se_avisa(
        resultado_a01):
    """
    Un TW sobre la clave deja la Ec. (10.4) fuera de su rango: con la
    envolvente declarada rigen Laushey y lo adoptado, y se dice. Tambien en
    una llamada que solo trae la velocidad.
    """
    r = _tubo_lleno(resultado_a01, D=0.9, Q=1.15, TW=1.2)
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(0.9))
    assert p.apron is None and not p.rige_la_envolvente
    assert p.d50 == pytest.approx(p.d50_laushey, rel=REL_FORMULA)
    assert p.espesor == pytest.approx(1.75 * p.d50, rel=REL_FORMULA)
    assert p.longitud == pytest.approx(5.0, rel=REL_FORMULA)
    assert any("apron de HEC-14 NO se evaluo" in x for x in p.avisos)
    assert any("no es evaluable en este punto" in x and "Laushey" in x
               for x in p.avisos)
    assert p.advertencias == M6.ADVERTENCIAS_PROTECCION_SALIDA
    solo_v = M6.proteccion_salida(V=_V(2.0))
    assert solo_v.d50 == pytest.approx(4.0 / (3.1 * 9.8), rel=REL_FORMULA)
    assert any("no es evaluable en este punto" in x for x in solo_v.avisos)


def test_h1_la_linea_de_la_cli_bajo_manual_es_la_de_antes(corrida_manual):
    """La regla «manual» reproduce la linea de la linea base anterior."""
    texto = cli.volcar(corrida_manual)
    assert ("Fase 6  d50 = 0.338 m, espesor 0.592 m, longitud 5.000 m "
            "(num. 4.1.1.3.7 c))") in texto
    assert ("Fase 6  d50 = 0.274 m, espesor 0.479 m, longitud 5.000 m "
            "(num. 4.1.1.3.7 c))") in texto


def test_h1_la_linea_de_la_cli_bajo_envolvente_separa_los_origenes(
        corrida_base):
    """
    Con la envolvente, A-01 pasa a espesor 0.770 m y longitud 5.400 m, que
    salen de la Tabla 10.1 de HEC-14 y no del num. 4.1.1.3.7 c) del Manual:
    la linea atribuye el numeral al d50 de Laushey y HEC-14 a lo que rige.
    """
    linea = next(x for x in cli.volcar(corrida_base).splitlines()
                 if "Fase 6  d50 = 0.338 m" in x)
    antes, _, despues = linea.partition("(num. 4.1.1.3.7 c))")
    assert "espesor" not in antes and "longitud" not in antes
    assert "espesor 0.770 m" in despues and "longitud 5.400 m" in despues
    assert "HEC-14" in despues
    # La memoria tampoco atribuye el espesor al criterio a secas.
    html = M11.memoria_de_punto(_punto(corrida_base, "A-01"))
    assert "rige la ENVOLVENTE del Manual y de HEC-14" in html


# ===========================================================================
# H2 (ALTA) · D2 · «sin enrocado» no se concluye con una velocidad que es
# cota inferior (control de salida con el TW bajo el critico)
# ===========================================================================

def test_h2_con_la_velocidad_al_critico_no_se_concluye_sin_enrocado(
        resultado_a01):
    """
    V = 1.0 m/s al tirante critico, sobre grava fina con flujo intermitente
    (1.50 m/s, Tabla Nº 11). No la supera, pero la velocidad REAL en el borde
    es mayor (HEC-14 num. 3.1.3): el contraste NO concluye, la proteccion se
    mantiene y se dimensiona. Laushey: 1.0²/(3.1·9.8) = 0.032916 m.
    """
    r = _por_la_salida_al_critico(resultado_a01, 1.0)
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(0.9),
                             tipo_terreno="grava_fina",
                             regimen_flujo="intermitente")
    assert p.requerida is None
    assert p.d50_laushey == pytest.approx(1.0 / (3.1 * 9.8), rel=REL_FORMULA)
    assert p.d50 is not None and p.espesor is not None
    assert len(p.advertencias) == 3
    assert p.velocidad_admisible.supera is False
    assert p.velocidad_admisible.concluyente is False
    veredicto = p.velocidad_admisible.paso.veredicto
    assert veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert "cota inferior" in veredicto.explicacion
    assert any("no concluye" in x and "cota inferior" in x for x in p.avisos)
    assert not any("el terreno la resistiria" in x for x in p.avisos)


def test_h2_y_d6_sin_la_condicion_de_borde_el_contraste_informa(
        resultado_a01):
    """
    Bajo control de ENTRADA la velocidad no es cota inferior y el contraste
    concluye: el terreno la resistiria segun la tabla (`requerida` False).
    Decision 6 del dueño: eso INFORMA y no suprime nada. La proteccion se
    calcula y se mantiene, y suprimirla queda sujeto a inspeccion de campo,
    dicho en el aviso (con la frase del HDS-5) y en el paso 6.4.
    """
    p = M6.proteccion_salida(V=_V(1.0), resultado=resultado_a01,
                             seccion=SeccionCircular(0.9),
                             tipo_terreno="grava_fina",
                             regimen_flujo="intermitente")
    assert p.requerida is False
    assert p.velocidad_admisible.concluyente is True
    assert p.d50_laushey == pytest.approx(1.0 / (3.1 * 9.8), rel=REL_FORMULA)
    assert p.d50 is not None and p.espesor is not None
    literal = _registro.construir().cita(
        "HDS5_3ED.5.3.2#PRACTICA").texto_literal.texto
    aviso = next(x for x in p.avisos if "se MANTIENE" in x)
    assert "inspeccion de campo" in aviso and literal in aviso
    paso = p.velocidad_admisible.paso
    assert paso.veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert "inspeccion de campo" in paso.veredicto.explicacion
    assert "calcula y mantiene la proteccion" in paso.umbral.aplicacion
    assert not any("SIN enrocado" in x for x in p.avisos)


def test_d6_sin_el_terreno_declarado_la_conducta_no_cambia():
    """Sin `tipo_terreno_receptor`: se dimensiona y se avisa, como antes."""
    p = M6.proteccion_salida(V=_V(2.0))
    assert p.requerida is None and p.velocidad_admisible is None
    assert p.d50 == pytest.approx(4.0 / (3.1 * 9.8), rel=REL_FORMULA)
    aviso = next(x for x in p.avisos if "tipo_terreno_receptor" in x)
    assert "el enrocado se dimensiona igual" in aviso


def test_h2_el_aviso_de_borde_da_la_magnitud_y_nombra_el_d50(resultado_a01):
    """
    El aviso da la cota, leida por imagen de la Figura 3.4 de HEC-14 (pag.
    impresa 3-6, PDF 37) para descarga libre (TW/D -> 0). Curvas KuQ/D^2.5 =
    1.0, 2.0 y 3.0: yo/D = 0.323, 0.467 y 0.572. El tirante critico de esas
    tres descargas (Q²·T/(g·A³) = 1 con Q/(g^0.5·D^2.5) = Ku·…/1.811/g^0.5):
    yc/D = 0.420, 0.604 y 0.743. Razon de areas A(yc)/A(yo) = V_borde/V_c:
    1.43, 1.38 y 1.35, y al cuadrado (d50 de Laushey): 2.03, 1.90 y 1.81.
    Y el ejemplo IMPRESO de la pag. 3-4 (TW/D de 0.41 a 0.58): A/D² al borde
    0.5308 … 0.3130 contra 0.5829 … 0.3395 al critico, de +8 % a +13 %.
    """
    r = _por_la_salida_al_critico(resultado_a01, 3.0)
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(0.9))
    aviso = next(x for x in p.avisos if "tirante critico" in x)
    assert "cota inferior" in aviso and "Figura 3.4" in aviso
    assert "1.35 a 1.43" in aviso          # V_borde / V_c en descarga libre
    assert "1.8 a 2.0" in aviso            # el d50 de Laushey, con V²
    assert "d50" in aviso


def test_h2_por_el_pipeline_el_punto_conserva_la_proteccion(tmp_path):
    """
    El caso del auditor: A-02 con el barril horizontal (S = 0), sobre
    «Material graduado: grava» con flujo permanente (1.80 m/s). M4 toma la
    velocidad al critico, 1.739 m/s < 1.80: el programa decia «sin enrocado».
    Con la Figura 3.4 (KuQ/D^2.5 = 1.13, TW/D = 0.33 -> yo/D ≈ 0.38) la
    velocidad de borde es ≈ 2.13 m/s > 1.80.
    """
    informe = _correr_ancho(tmp_path, {"A-02": {
        "S_conducto": 0, "tipo_terreno_receptor": "graduado_grava",
        "regimen_flujo_descarga": "permanente"}})
    a02 = _punto(informe, "A-02")
    p = a02.proteccion
    assert p.velocidad_admisible.V_admisible == pytest.approx(
        1.80, rel=REL_TRANSPORTE)
    assert p.V < 1.80
    assert p.requerida is None and p.d50 is not None
    assert p.d50_laushey == pytest.approx(p.V ** 2 / (3.1 * 9.8),
                                          rel=REL_FORMULA)
    avisos = a02.avisos()
    assert any("no concluye" in x for x in avisos)
    texto = cli.volcar(informe)
    assert "sin enrocado" not in texto
    volcado = {x["id"]: x for x in cli.informe_json(informe)["puntos"]}["A-02"]
    assert volcado["proteccion_salida"]["requerida"] is None
    assert volcado["proteccion_salida"]["d50_m"] is not None
    admisible = volcado["proteccion_salida"]["velocidad_admisible"]
    assert admisible["supera"] is False and admisible["concluyente"] is False
    assert any("no concluye" in x for x in volcado["avisos"])
    assert "no concluye" in M11.memoria_de_punto(a02)
    # El indicador cuenta en el RESUMEN con las verificaciones con aviso.
    assert any(x.codigo == "6.4" for x in a02.indicadores_de_proteccion())


def test_h2_la_hoya_cohesiva_con_la_velocidad_al_critico_tambien_avisa(
        resultado_a01):
    """
    En suelo cohesivo la hoya va con (ρV²/τc)^β, β = 0.18: hs ∝ V^0.36. Con
    la velocidad de borde hasta 1.43 veces la critica, 1.43^0.36 = 1.137.
    """
    r = _por_la_salida_al_critico(resultado_a01, 2.0)
    s = M6.socavacion_salida(
        resultado=r, seccion=SeccionCircular(0.9), altura_caida_m=0.0,
        material=MaterialLecho(tipo="cohesivo", IP=12.0, Sv_Pa=24000.0))
    assert any("cota inferior" in x and "V^0.36" in x for x in s.avisos)
    sin_borde = M6.socavacion_salida(
        resultado=resultado_a01, seccion=SeccionCircular(0.9),
        altura_caida_m=0.0,
        material=MaterialLecho(tipo="cohesivo", IP=12.0, Sv_Pa=24000.0))
    assert not any("V^0.36" in x for x in sin_borde.avisos)


# ===========================================================================
# H3 (MEDIA) · el fundamento del Froude dice lo que el paso hace
# ===========================================================================

def test_h3_el_fundamento_del_froude_no_clasifica_el_regimen():
    f = _registro.construir().fundamento("F6.FROUDE")
    assert "dice en que regimen" not in f.por_que
    assert "por debajo de 1" not in f.por_que
    assert "no clasifica el regimen" in f.por_que
    # «la fuente pide un disipador» no lo dice HEC-14: la Tabla 1.1 da al
    # apron Froude «na».
    assert "pide un disipador" not in f.que_pasa_si_no_se_hace
    assert "HEC14.1#T1_1_APRON" in f.citas


def test_h3_la_memoria_no_imprime_que_el_froude_dice_el_regimen(corrida_base):
    """El `por_que` va en el anexo de fundamentos de la memoria entera."""
    html = M11.memoria_html(corrida_base)
    assert "dice en que regimen entrega" not in html
    assert "no clasifica el regimen del flujo" in html
    assert "la fuente pide un disipador" not in html


def test_h3_ningun_fundamento_de_la_fase_6_atribuye_a_la_fuente_la_inversa():
    """
    Revision de TODOS los `F6.*` con el mismo ojo (resolucion c): lo que el
    proyecto lee no se imprime como si lo dijera la fuente.
    """
    reg = _registro.construir()
    admisible = reg.fundamento("F6.V_ADMISIBLE").por_que
    assert "el Manual recomienda proteger el cauce, y es entonces" \
        not in admisible
    assert "«alta»" in admisible and "lectura del proyecto" in admisible
    apron = reg.fundamento("F6.APRON").por_que
    assert "se ajusto sobre conductos circulares" not in apron
    geometria = reg.fundamento("F6.APRON_GEOMETRIA").por_que
    assert "lectura del proyecto" in geometria


# ===========================================================================
# H4 (MEDIA) · D4 · la nota (5) b de la Tabla 511-06 solo en la columna «>50»
# ===========================================================================

@pytest.mark.parametrize("pasa, IP, abertura", [
    (60.0, 10.0, 0.30),     # «>50»: la celda lleva la llamada (5)
    (60.0, 5.0, 0.22),      # IP <= 7: la celda
    (60.0, 7.0, 0.22),      # «mayor a 7»: el 7 justo no
    (30.0, 10.0, 0.25),     # «15-50»: la nota NO relaja la celda
    (10.0, 10.0, 0.43),     # «<15»: la celda
])
def test_h4_la_nota_5b_vale_en_la_columna_que_lleva_la_llamada(pasa, IP,
                                                              abertura):
    """
    Tabla 511-06 (pag. impresa 1015, PDF 1023): el rotulo dice «Tamaño de
    Abertura Aparente (3) (4) (5)» y la celda de «>50», «0,22(5)»; hay DOS
    notas, (5) a y (5) b. La Tabla 511-02 de la misma Seccion (pag. impresa
    1011, PDF 1019) trae las MISMAS dos notas con numeros distintos: el
    rotulo lleva «(3) (4)» --la (4) es el diseño especifico-- y solo la celda
    «0,22 (5)» lleva la de los suelos cohesivos. Lectura del proyecto: el
    rotulo llama a la (5) a y la celda a la (5) b.
    """
    f = M6.requisito_de_filtro(pasa_200_pct=pasa, indice_plasticidad=IP,
                               tipo_lecho="cohesivo")
    assert f.abertura_aparente_max_mm == pytest.approx(abertura,
                                                       rel=REL_TRANSPORTE)


def test_h4_la_lectura_de_la_nota_5_es_una_interpretacion_declarada():
    reg = _registro.construir()
    interpretacion = reg.cita("EG2013.511.08#T511_06").interpretacion
    assert interpretacion is not None and interpretacion.en_contra
    hermana = reg.cita("EG2013.511.05#T511_02_NOTA_5")
    assert hermana.pagina_impresa == "1011" and hermana.pagina_pdf == 1019
    # El paso imprime la lectura en la cara del proyecto, no como procedencia.
    f = M6.requisito_de_filtro(pasa_200_pct=30.0, indice_plasticidad=10.0,
                               tipo_lecho="cohesivo")
    assert interpretacion.texto in f.paso.nota_del_proyecto
    assert "EG2013.511.05#T511_02_NOTA_5" in f.paso.citas_textuales
    abertura = next(m for m in f.paso.sustitucion
                    if m.simbolo == "abertura aparente maxima")
    assert "vale en las tres columnas" not in abertura.procedencia


def test_h4_en_la_columna_baja_se_avisa_la_otra_lectura():
    """
    Del lado seguro (resolucion d): en «<15» la lectura adoptada deja 0.43 mm
    y la otra daria 0.30 mm, mas cerrada. Se avisa. En «15-50» la adoptada ya
    es la mas cerrada (0.25 contra 0.30) y no hay nada que avisar.
    """
    baja = M6.requisito_de_filtro(pasa_200_pct=10.0, indice_plasticidad=10.0,
                                  tipo_lecho="cohesivo")
    assert any("0.30 mm" in x and "nota (5)" in x for x in baja.avisos)
    media = M6.requisito_de_filtro(pasa_200_pct=30.0, indice_plasticidad=10.0,
                                   tipo_lecho="cohesivo")
    assert not media.avisos


@pytest.mark.pdf
def test_h4_las_dos_tablas_de_eg2013_llevan_las_llamadas_donde_se_dice():
    """
    El hecho de la fuente, sobre el PDF: en la Tabla 511-02 el rotulo de la
    fila lleva «(3) (4)» y la celda «0,22 (5)»; en la 511-06 el rotulo lleva
    «(3)» y «(4) (5)» y la celda «0,22(5)», con las notas «(5)  a.» y «b.».
    """
    fitz = pytest.importorskip("fitz")
    ruta = _fuentes.ruta_pdf(_registro.construir().fuente("EG2013"))
    if not ruta.is_file():
        pytest.skip(f"falta el PDF de EG-2013 ({ruta.name})")
    with fitz.open(ruta) as documento:
        t02 = " ".join(documento[1018].get_text().split())
        t06 = " ".join(documento[1022].get_text().split())
    assert "Tabla 511-02" in t02 and "Tabla 511-06" in t06
    assert "Tamaño de Abertura Aparente (3) (4) ASTM D 4751" in t02
    assert "0,22 (5)" in t02
    assert ("(5) Para los suelos cohesivos con un índice de plasticidad "
            "mayor a 7") in t02
    assert "Tamaño de Abertura Aparente (3) (4) (5) ASTM D 4751" in t06
    assert "0,22(5)" in t06
    assert ("(5) b. Para los suelos cohesivos con un índice de plasticidad "
            "mayor a 7") in t06


# ===========================================================================
# H5 (MEDIA) · D5 · el limite del apron deja entrar el ejemplo de la fuente
# ===========================================================================

def test_h5_el_limite_del_apron_es_60_pulgadas():
    """
    Nota 8 de la Tabla 1.1 (pag. impresa 1-2, PDF 15): «Culvert rise less
    than or equal to 1500 mm (60 in)». La fuente da las DOS cifras y su
    ejemplo resuelto en unidades inglesas (pag. 10-19) usa D = 5.0 ft = 60 in
    = 1.524 m: rige la que deja evaluar el ejemplo de la propia fuente.
    """
    assert HEC14_APRON_ALTURA_MAX_M == pytest.approx(60 * M_POR_IN,
                                                     rel=REL_FORMULA)
    literal = _registro.construir().cita("HEC14.1#T1_1_APRON").texto_literal
    assert "1500 mm (60 in)" in literal.texto


def test_h5_el_ejemplo_ingles_de_hec14_entra_a_su_escala_real():
    """
    Pag. impresa 10-19 (PDF 220): Q = 85 ft3/s, D = 5.0 ft, TW = 1.6 ft.
    TW/D = 0.32 < 0.4 -> TW = 2.0 ft. En unidades inglesas, a mano:

        Q/(g^0.5·D^2.5) = 85/(5.67450·55.9017) = 85/317.215 = 0.267957
        0.267957^(4/3) = 0.172751
        D50 = 0.2·5.0·0.172751·(5.0/2.0) = 0.43188 ft   (la fuente: 0.43 ft)

    Clase 2: L = 4D = 20 ft = 6.096 m; ancho = 3D + (2/3)L = 28.33 ft =
    8.636 m (la fuente: 28.3 ft). Profundidad: 3.3 veces el D50 de la clase.
    """
    a = M6.apron_hec14(Q_celda=85 / FT3_POR_M3,
                       seccion=SeccionCircular(5.0 * M_POR_FT),
                       TW=1.6 * M_POR_FT, y_salida=5.0 * M_POR_FT,
                       y_critico=1.0)
    assert a.TW_acotado
    assert a.TW_de_calculo == pytest.approx(2.0 * M_POR_FT, rel=REL_FORMULA)
    assert a.D50_requerido / M_POR_FT == pytest.approx(0.43188,
                                                       rel=REL_ARITMETICA)
    assert a.D50_requerido / M_POR_FT == pytest.approx(0.43,
                                                       rel=REL_EJEMPLO_IMPRESO)
    assert a.clase == 2
    assert a.longitud / M_POR_FT == pytest.approx(20.0, rel=REL_FORMULA)
    assert a.ancho_final / M_POR_FT == pytest.approx(28.3,
                                                     rel=REL_EJEMPLO_IMPRESO)
    assert a.espesor == pytest.approx(3.3 * 0.15, rel=REL_FORMULA)


def test_h5_por_encima_de_60_pulgadas_el_apron_no_se_evalua():
    for D in (1.53, 1.65, 1.8):
        with pytest.raises(MetodoNoEvaluableError, match="60 in") as error:
            M6.apron_hec14(Q_celda=2.0, seccion=SeccionCircular(D), TW=0.8,
                           y_salida=D, y_critico=0.7)
        assert "1500 mm" in error.value.motivo
    # El diametro normalizado de 1.50 m sigue entrando, como antes.
    assert M6.apron_hec14(Q_celda=2.0, seccion=SeccionCircular(1.5), TW=0.8,
                          y_salida=1.5, y_critico=0.7).clase is not None


# ===========================================================================
# H6 (MEDIA) · lo que el proyecto lee no se imprime como la fuente
# ===========================================================================

@pytest.mark.parametrize("cita_id", [
    "HEC14.10.2#TW",                    # los limites del TW con D'
    "MC_HHD.4.1.1.3.7c#PROTECCION",     # «alta» = mayor que la Tabla Nº 11
    "EG2013.511.08#T511_06",            # la nota (5) b
])
def test_h6_cada_lectura_del_proyecto_tiene_su_interpretacion(cita_id):
    interpretacion = _registro.construir().cita(cita_id).interpretacion
    assert interpretacion is not None
    assert interpretacion.en_contra and interpretacion.a_favor


def test_h6_bajo_la_admisible_el_veredicto_habla_en_nombre_del_proyecto():
    v = M6.velocidad_admisible_del_cauce(
        V=_V(1.0), tipo_terreno="grava_fina", regimen_flujo="intermitente")
    assert v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert "la Tabla Nº 11 no pide" not in v.paso.veredicto.explicacion
    assert "el proyecto" in v.paso.veredicto.explicacion
    # La lectura viaja en la cara del proyecto, leida del registro.
    lectura = _registro.construir().cita(
        "MC_HHD.4.1.1.3.7c#PROTECCION").interpretacion.texto
    assert lectura in v.paso.nota_del_proyecto
    assert "MC_HHD.4.1.1.3.7c#PROTECCION" in v.paso.citas_textuales


def test_h6_el_aviso_de_la_hoya_sin_revestir_no_atribuye_a_la_tabla(
        resultado_a01):
    s = M6.socavacion_salida(
        resultado=resultado_a01, seccion=SeccionCircular(0.9),
        altura_caida_m=0.3,
        material=MaterialLecho(tipo="no_cohesivo", D84_m=0.02, D16_m=0.002),
        proteccion_requerida=False)
    aviso = next(x for x in s.avisos if "5.1.3" in x)
    assert "la Tabla Nº 11 no pide" not in aviso
    assert "el terreno resistiria" in aviso
    assert "inspeccion de campo" in aviso


def test_h6_los_documentos_no_dicen_que_el_manual_no_pide_proteger():
    for ruta in ("docs/contrato_entradas.md",
                 "docs/hoja_de_ruta_alcantarillas_v8.md",
                 "src/modulos/M6_proteccion.py", "src/modelos.py", "cli.py",
                 "src/modulos/M11_reporte.py"):
        texto = (RAIZ / ruta).read_text(encoding="utf-8")
        assert "el Manual no pide proteger" not in texto, ruta
        assert "la Tabla Nº 11 no pide proteger" not in texto, ruta
        assert "la Tabla Nº 11 no pide revestir" not in texto, ruta


def test_h6_y_h10a_el_limite_del_tw_con_el_diametro_ajustado_se_llama_D_prima():
    """
    A-01 de la linea base (D = 0.90 m, y_n = 0.627 m supercritico): D' =
    (0.9 + 0.627)/2 = 0.7635 m. Con TW = 0.80 m --menor que D-- el apron sale
    no evaluable porque el proyecto aplica el limite a D' (lectura declarada):
    el mensaje dice D', no D.
    """
    with pytest.raises(MetodoNoEvaluableError) as error:
        M6.apron_hec14(Q_celda=1.167, seccion=SeccionCircular(0.9), TW=0.80,
                       y_salida=0.627, y_critico=0.640)
    assert "D' = 0.76" in error.value.motivo
    assert "1·D = 0.76" not in error.value.motivo
    # Y el paso, cuando si se evalua, lleva la lectura en la cara del proyecto.
    a = M6.apron_hec14(Q_celda=1.167, seccion=SeccionCircular(0.9), TW=0.30,
                       y_salida=0.627, y_critico=0.640)
    lectura = _registro.construir().cita("HEC14.10.2#TW").interpretacion.texto
    assert lectura in a.pasos[0].nota_del_proyecto


# ===========================================================================
# H7 · guardias de segunda linea: un tipo que no es texto es dato invalido
# ===========================================================================

def test_h7_un_terreno_o_una_embocadura_que_no_son_texto_son_dato_invalido(
        resultado_a01):
    for malo in (["grava_fina"], {"a": 1}, 3, None):
        with pytest.raises(DatoInvalidoError):
            M6.velocidad_admisible_del_cauce(
                V=_V(1.0), tipo_terreno=malo, regimen_flujo="intermitente")
    with pytest.raises(DatoInvalidoError):
        M6.velocidad_admisible_del_cauce(
            V=_V(1.0), tipo_terreno="grava_fina", regimen_flujo=["x"])
    with pytest.raises(DatoInvalidoError):
        M6.velocidad_admisible_del_cauce(
            V=_V(1.0), tipo_terreno="grava_fina",
            regimen_flujo="intermitente", donde=["salida"])
    for malo in (["x"], {"a": 1}, 3):
        with pytest.raises(DatoInvalidoError):
            M6.proteccion_entrada(resultado=resultado_a01,
                                  tipo_embocadura=malo)


# ===========================================================================
# H8 · D3 · una recomendacion no «manda»; y lo que la fuente dice de los 30 min
# ===========================================================================

def test_h8_los_30_minutos_se_recomiendan_no_se_mandan(resultado_a01):
    s = M6.socavacion_salida(
        resultado=resultado_a01, seccion=SeccionCircular(0.9),
        altura_caida_m=0.3,
        material=MaterialLecho(tipo="no_cohesivo", D84_m=0.02, D16_m=0.002))
    aviso = next(x for x in s.avisos if "duracion" in x)
    assert "manda" not in aviso and "recomienda" in aviso
    assert "manda" not in s.estimada.origen_duracion
    reg = _registro.construir()
    assert reg.cita("HEC14.5.1.2#T30").caracter.value == "recomendacion"
    # D3: la fuente dice cuanto de la hoya maxima se alcanza a los 30 min, y
    # el aviso lo cita del registro.
    literal = reg.cita("HEC14.5.1.2#DOS_TERCIOS").texto_literal.texto
    assert "2/3 to 3/4 of the maximum scour depth" in literal
    assert literal in aviso


def test_d3_sin_hidrograma_la_hoya_se_estima_con_360_minutos(resultado_a01):
    """
    Decision 3 del dueño: el criterio 'duracion_caudal_pico_socavacion_min'
    pasa de [C] = 30 min a una ELECCION [A] = 360 min en la ventana 30-360,
    con 30 --lo que la fuente recomienda-- como alternativa barrible.
    Aritmetica: hs ∝ (t/316)^θ con θ = 0.06 (Tabla 5.1). De 30 a 360 min:
    (360/30)^0.06 = 12^0.06 = exp(0.06·2.48491) = 1.16078.
    """
    ficha = ca.CRITERIOS["duracion_caudal_pico_socavacion_min"]
    assert ficha.etiqueta == "A"
    assert ficha.valor == pytest.approx(360.0, rel=REL_FORMULA)
    assert ficha.sensibilidad == pytest.approx((30.0, 360.0), rel=REL_FORMULA)
    assert "HEC14.5.1.2#DOS_TERCIOS" in ficha.justificacion
    # Lo que la fuente NO dice se dice: el techo no sale de HEC-14.
    assert "no sale de HEC-14" in ficha.justificacion
    lecho = MaterialLecho(tipo="no_cohesivo", D84_m=0.02, D16_m=0.002)
    comunes = dict(resultado=resultado_a01, seccion=SeccionCircular(0.9),
                   altura_caida_m=0.3, material=lecho)
    por_criterio = M6.socavacion_salida(**comunes).estimada
    a30 = M6.socavacion_salida(duracion_pico_min=30.0, **comunes).estimada
    assert por_criterio.duracion_por_criterio
    assert por_criterio.duracion_min == pytest.approx(360.0, rel=REL_FORMULA)
    assert por_criterio.profundidad / a30.profundidad == pytest.approx(
        1.16078, rel=REL_ARITMETICA)
    assert por_criterio.duracion_alternativa_min == pytest.approx(
        30.0, rel=REL_FORMULA)
    assert por_criterio.profundidad_alternativa == pytest.approx(
        a30.profundidad, rel=REL_FORMULA)
    # Declarando 30 en caliente (el barrido), la sensibilidad se da contra
    # el techo: la otra punta de la ventana.
    ca.establecer_valor_dinamico("duracion_caudal_pico_socavacion_min", 30.0)
    try:
        barrida = M6.socavacion_salida(**comunes).estimada
    finally:
        ca.quitar_valor_dinamico("duracion_caudal_pico_socavacion_min")
    assert barrida.profundidad == pytest.approx(a30.profundidad,
                                                rel=REL_FORMULA)
    assert barrida.duracion_alternativa_min == pytest.approx(360.0,
                                                             rel=REL_FORMULA)
    assert barrida.profundidad_alternativa == pytest.approx(
        por_criterio.profundidad, rel=REL_FORMULA)


# ===========================================================================
# H9 · la cita que sostiene «hs desde la solera» es la que lo dice
# ===========================================================================

def test_h9_la_referencia_de_la_figura_10_1_se_apoya_en_su_propia_cita(
        resultado_a01):
    reg = _registro.construir()
    cita = reg.cita("HEC14.10.1#HS")
    assert cita.pagina_impresa == "10-1" and cita.pagina_pdf == 202
    assert "at the approximate depth of scour, hs" in cita.texto_literal.texto
    s = M6.socavacion_salida(resultado=resultado_a01,
                             seccion=SeccionCircular(0.9), declarada_m=1.0,
                             cota_fondo_receptor=41.30,
                             cota_solera_salida=41.99)
    paso = s.pasos[-1]
    assert paso.codigo == "6.14"
    assert "HEC14.10.1#HS" in paso.citas_textuales
    assert "HEC14.10.1#DOS_D50" not in paso.citas_textuales
    ficha = ca.CRITERIOS["referencia_profundidad_socavacion"]
    assert "HEC14.10.1#HS" in ficha.justificacion
    assert "HEC14.10.1#DOS_D50" not in ficha.justificacion


# ===========================================================================
# H10 · mensajes que dicen otra cosa
# ===========================================================================

def test_h10b_el_limite_numerico_de_la_hoya_nombra_al_par_culpable(
        resultado_a01):
    """D84/D16 = 1e300/1e-300 desborda sigma: el par culpable es ese."""
    lecho = MaterialLecho(tipo="no_cohesivo", D84_m=1e300, D16_m=1e-300)
    with pytest.raises(LimiteNumericoError) as error:
        M6.hoya_de_socavacion_hec14(
            Q_celda=1.0, seccion=SeccionCircular(0.9), S=0.01, V=_V(2.0),
            altura_caida_m=0.0, material=lecho)
    assert "D84" in str(error.value) and "D16" in str(error.value)


def test_h10c_la_duracion_del_pico_se_pide_en_minutos():
    with pytest.raises(DatoInvalidoError) as error:
        servicio._numero_externo("duracion_caudal_pico_min", "treinta", "test")
    assert "minutos" in str(error.value)
    assert "metros o m3/s" not in str(error.value)
    # Las demas claves siguen con su texto.
    with pytest.raises(DatoInvalidoError, match="metros o m3/s"):
        servicio._numero_externo("TW_m", "x", "test")


def test_h10d_y_e_los_comentarios_ya_no_dicen_lo_contrario_que_el_codigo():
    constantes = (RAIZ / "src" / "constantes_normativas.py").read_text(
        encoding="utf-8")
    assert "es en\n# esa columna donde el proyecto la aplica" not in constantes
    modelos = (RAIZ / "src" / "modelos.py").read_text(encoding="utf-8")
    assert "que se calculo el d50: siempre" not in modelos


# ===========================================================================
# H11 · D6 · el CSV de resumen no confunde «no hace falta» con «no se calculo»
# ===========================================================================

def test_h11_las_celdas_de_la_proteccion_solo_van_vacias_sin_fase_6(tmp_path):
    """
    T-8 dejaba las tres celdas vacias cuando la velocidad no superaba la
    admisible («sin enrocado»), iguales a las de una Fase 6 que no corrio.
    Desde la decision 6 del dueño la proteccion lleva siempre numero: una
    celda vacia quiere decir, sin ambiguedad, que la fase no corrio.
    """
    informe = _correr_ancho(tmp_path, {
        "A-01": {"tipo_terreno_receptor": "graduado_grava_gruesa",
                 "regimen_flujo_descarga": "intermitente"},
        "A-02": {"tipo_terreno_receptor": "graduado_grava_a_piedras_mayor_20cm",
                 "regimen_flujo_descarga": "intermitente"}})
    columnas = [M11.COLUMNAS_RESUMEN_CSV.index(c) for c in (
        "proteccion_d50_m", "proteccion_espesor_m", "proteccion_longitud_m")]
    filas = {p.punto.id: M11._fila_resumen_csv(p, "cabezal")
             for p in informe.puntos}
    assert _punto(informe, "A-01").proteccion.requerida is True
    assert _punto(informe, "A-02").proteccion.requerida is False
    for id_punto in ("A-01", "A-02"):
        assert all(filas[id_punto][c] != "" for c in columnas), id_punto
    # B-01 no dimensiona: su Fase 6 no corrio, y esas son las celdas vacias.
    assert _punto(informe, "B-01").proteccion is None
    assert all(filas["B-01"][c] == "" for c in columnas)
    # Las columnas del resumen no cambian: ninguna se añade.
    assert "proteccion_requerida" not in M11.COLUMNAS_RESUMEN_CSV


# ===========================================================================
# H13 · la transcripcion entera, celda a celda, releida del PDF
# ===========================================================================

TABLA_11_DEL_PDF = {       # Manual, pag. impresa 77 (PDF 80): intermitente, permanente
    "arena_fina_no_coloidal": (0.75, 0.75),
    "arcilla_arenosa_no_coloidal": (0.75, 0.75),
    "arcilla_limosa_no_coloidal": (0.90, 0.90),
    "arcilla_fina": (1.00, 1.00),
    "ceniza_volcanica": (1.20, 1.00),
    "grava_fina": (1.50, 1.20),
    "arcilla_dura_coloidal": (1.80, 1.40),
    "graduado_arcilla_a_grava": (2.00, 1.50),
    "graduado_limo_a_grava": (2.10, 1.70),
    "graduado_grava": (2.30, 1.80),
    "graduado_grava_gruesa": (2.40, 2.00),
    "graduado_grava_a_piedras_menor_15cm": (2.70, 2.10),
    "graduado_grava_a_piedras_mayor_20cm": (3.00, 2.40),
}


def test_h13_las_trece_filas_de_la_tabla_11_son_las_del_pdf():
    assert list(V_MAX_NO_REVESTIDOS) == list(TABLA_11_DEL_PDF)
    for fila, (intermitente, permanente) in TABLA_11_DEL_PDF.items():
        assert V_MAX_NO_REVESTIDOS[fila]["intermitente"] == pytest.approx(
            intermitente, rel=REL_FORMULA), fila
        assert V_MAX_NO_REVESTIDOS[fila]["permanente"] == pytest.approx(
            permanente, rel=REL_FORMULA), fila


DIMENSIONES = ("profundidad", "ancho", "longitud", "volumen")


def test_h13_las_tablas_5_2_y_5_3_de_hec14_enteras():
    """Pag. impresa 5-3 (PDF 56): 16 celdas cada una, en el orden impreso."""
    ch = {0.0: (1.00, 1.00, 1.00, 1.00), 1.0: (1.22, 1.51, 0.73, 1.28),
          2.0: (1.26, 1.54, 0.73, 1.47), 4.0: (1.34, 1.66, 0.73, 1.55)}
    cs = {0.0: (1.00, 1.00, 1.00, 1.00), 2.0: (1.03, 1.28, 1.17, 1.30),
          5.0: (1.08, 1.28, 1.17, 1.30), 7.0: (1.12, 1.28, 1.17, 1.30)}
    for tabla, del_pdf in ((HEC14_SOCAVACION_CH, ch), (HEC14_SOCAVACION_CS, cs)):
        assert [abscisa for abscisa, _ in tabla] == pytest.approx(
            list(del_pdf), rel=REL_FORMULA)
        for abscisa, valores in tabla:
            assert [valores[d] for d in DIMENSIONES] == pytest.approx(
                list(del_pdf[abscisa]), rel=REL_FORMULA), abscisa


def test_h13_las_tablas_5_1_y_5_4_de_hec14_enteras():
    """Pags. impresas 5-2 y 5-7 (PDF 55 y 60): α, β, θ (y αe)."""
    t51 = {"profundidad": (2.27, 0.39, 0.06), "ancho": (6.94, 0.53, 0.08),
           "longitud": (17.10, 0.47, 0.10), "volumen": (127.08, 1.24, 0.18)}
    t54 = {"profundidad": (0.86, 0.18, 0.10, 1.37),
           "ancho": (3.55, 0.17, 0.07, 5.63),
           "longitud": (2.82, 0.33, 0.09, 4.48),
           "volumen": (0.62, 0.93, 0.23, 2.48)}
    for d in DIMENSIONES:
        assert HEC14_SOCAVACION_NO_COHESIVO[d] == pytest.approx(
            t51[d], rel=REL_FORMULA), d
        assert HEC14_SOCAVACION_COHESIVO[d] == pytest.approx(
            t54[d], rel=REL_FORMULA), d
    # «αe = α/0.63 for hs, Ws, and Ls» (pag. 5-7), con el redondeo impreso.
    for d in ("profundidad", "ancho", "longitud"):
        alfa, _, _, alfa_e = t54[d]
        assert alfa / 0.63 == pytest.approx(alfa_e, rel=REL_EJEMPLO_IMPRESO)


# ===========================================================================
# Los seis bordes INCLUSIVOS de la fuente (mutantes de banda de tolerancia)
# ===========================================================================

@pytest.mark.parametrize("IP, entra", [(5.0, True), (16.0, True),
                                       (4.999, False), (16.001, False)])
def test_borde_el_indice_de_plasticidad_de_5_a_16_incluye_los_extremos(IP,
                                                                      entra):
    """«a plasticity index of 5 to 16» (pag. impresa 5-7)."""
    if entra:
        assert M6.tension_tractiva_critica(Sv_Pa=24000.0, IP=IP) > 0
    else:
        with pytest.raises(MetodoNoEvaluableError):
            M6.tension_tractiva_critica(Sv_Pa=24000.0, IP=IP)


def test_borde_la_caida_de_cuatro_alturas_esta_en_la_tabla(resultado_a01):
    """Tabla 5.2: la ultima fila es Hd = 4, con Ch = 1.34 de profundidad."""
    lecho = MaterialLecho(tipo="no_cohesivo", D84_m=0.02, D16_m=0.002)
    comunes = dict(Q_celda=1.0, seccion=SeccionCircular(1.0), S=0.0,
                   V=_V(2.0), material=lecho)
    hoya = M6.hoya_de_socavacion_hec14(altura_caida_m=4.0, **comunes)
    assert hoya.Ch == pytest.approx(1.34, rel=REL_FORMULA)
    with pytest.raises(MetodoNoEvaluableError):
        M6.hoya_de_socavacion_hec14(altura_caida_m=4.001, **comunes)


def test_borde_el_tw_igual_a_la_altura_se_evalua_y_el_de_04_no_se_acota():
    """«between 0.4D and 1.0D» (pag. impresa 10-17): los dos extremos entran."""
    seccion = SeccionCircular(1.0)
    alto = M6.apron_hec14(Q_celda=1.0, seccion=seccion, TW=1.0, y_salida=1.0,
                          y_critico=0.6)
    assert not alto.TW_acotado
    bajo = M6.apron_hec14(Q_celda=1.0, seccion=seccion, TW=0.4, y_salida=1.0,
                          y_critico=0.6)
    assert not bajo.TW_acotado
    assert M6.apron_hec14(Q_celda=1.0, seccion=seccion, TW=0.399,
                          y_salida=1.0, y_critico=0.6).TW_acotado
    with pytest.raises(MetodoNoEvaluableError):
        M6.apron_hec14(Q_celda=1.0, seccion=seccion, TW=1.001, y_salida=1.0,
                       y_critico=0.6)


def test_borde_el_espesor_de_dos_d50_justos_no_avisa():
    """«to a limit of 2.0D50» (pag. impresa 10-18): 2.0 alcanza el piso."""
    assert M6._aviso_espesor_bajo_el_piso(2.0 * 0.35, 0.35) == ()
    assert M6._aviso_espesor_bajo_el_piso(1.999 * 0.35, 0.35)
    # Y es el techo de la ventana del criterio: declarandolo, deja de salir.
    assert ca.CRITERIOS["espesor_proteccion_salida"].sensibilidad[-1] == \
        pytest.approx(2.0, rel=REL_FORMULA)


def test_borde_la_clase_es_la_de_d50_mayor_o_igual():
    """«a D50 greater than or equal to the required size» (pag. 10-17)."""
    assert M6.clase_hec14_de_la_piedra(d50=0.125, D=0.9).clase == 1
    assert M6.clase_hec14_de_la_piedra(d50=0.1251, D=0.9).clase == 2
    assert M6.clase_hec14_de_la_piedra(d50=0.55, D=0.9).clase == 6
    assert M6.clase_hec14_de_la_piedra(d50=0.5501, D=0.9).clase is None


def test_borde_la_velocidad_igual_a_la_admisible_no_la_supera():
    """La Tabla Nº 11 da MAXIMAS admisibles: la igualdad se admite."""
    igual = M6.velocidad_admisible_del_cauce(
        V=_V(1.50), tipo_terreno="grava_fina", regimen_flujo="intermitente")
    assert not igual.supera
    assert M6.velocidad_admisible_del_cauce(
        V=_V(1.501), tipo_terreno="grava_fina",
        regimen_flujo="intermitente").supera


# ===========================================================================
# H15 · dos `None` que se resolvian en silencio
# ===========================================================================

def test_h15_sin_tirante_de_salida_el_apron_dice_que_no_sabe_el_regimen(
        resultado_a01):
    """
    A-01 sin `y_salida_m`: la Ec. (10.5) no se puede decidir. Hasta ahora
    `bool(None)` lo resolvia como «no supercritico» y el D50 salia de la clase
    3 en vez de la 4, sin decirlo.
    """
    a = M6.apron_hec14(Q_celda=1.167, seccion=SeccionCircular(0.9), TW=0.30,
                       y_salida=None, y_critico=0.640)
    assert a.regimen_determinado is False
    assert not a.ajustado_por_supercritico
    sin_tirante = replace(resultado_a01, y_salida_m=None)
    p = M6.proteccion_salida(V=sin_tirante.V_salida, resultado=sin_tirante,
                             seccion=SeccionCircular(0.9))
    assert any("regimen no determinado" in x and "10.5" in x
               for x in p.avisos), p.avisos
    # Con el tirante, como siempre: determinado y sin ese aviso.
    con = M6.proteccion_salida(V=resultado_a01.V_salida,
                               resultado=resultado_a01,
                               seccion=SeccionCircular(0.9))
    assert con.apron.regimen_determinado is True
    assert not any("regimen no determinado" in x and "10.5" in x
                   for x in con.avisos)


@pytest.mark.parametrize("campo", ["TW_m", "y_critico"])
def test_h15_un_resultado_sin_tw_o_sin_critico_no_deja_al_punto_sin_d50(
        resultado_a01, campo):
    """
    El docstring del modulo: «lo que falta en una pieza no debe dejar al punto
    sin las demas». Sin TW o sin tirante critico el apron de CONTRASTE no se
    puede evaluar; el d50 de Laushey, que solo pide V, se conserva.
    """
    r = replace(resultado_a01, **{campo: None})
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(0.9))
    assert p.d50 == pytest.approx(r.V_salida.valor ** 2 / (3.1 * 9.8),
                                  rel=REL_FORMULA)
    assert p.apron is None
    assert any("apron de HEC-14 NO se evaluo" in x for x in p.avisos)


# ===========================================================================
# H14 (M4, fuera del diff) · la banda y_n(n_max) > y_c > y_n(n_min): se avisa
# ===========================================================================

def test_h14_en_la_banda_de_regimen_la_fase_6_avisa_la_velocidad_alta(
        resultado_a01):
    """
    Control de SALIDA con la velocidad al critico, y la rama de n MINIMO
    (V_erosion) por encima de ella: con n minimo el tirante normal seria
    supercritico y la estimacion ALTA de la velocidad es V_erosion, no la
    critica. M6 no cambia el numero (es de M4): lo avisa con el d50 que daria.
    V_salida = 2.412, V_erosion = 3.160 -> d50 0.1915 m contra 0.3287 m:
        2.412²/30.38 = 5.8177/30.38 = 0.19150;  3.160²/30.38 = 0.32869
    """
    r = replace(_por_la_salida_al_critico(resultado_a01, 2.412),
                V_erosion=3.160)
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(0.9))
    assert p.d50 == pytest.approx(0.19150, rel=REL_ARITMETICA)
    aviso = next(x for x in p.avisos if "n minimo" in x)
    assert "3.16" in aviso and "0.329" in aviso
    # Fuera de la banda (V_erosion por debajo de la critica) no se avisa.
    fuera = replace(r, V_erosion=1.2)
    q = M6.proteccion_salida(V=fuera.V_salida, resultado=fuera,
                             seccion=SeccionCircular(0.9))
    assert not any("n minimo" in x for x in q.avisos)


# ===========================================================================
# Lo que se mueve y lo que no: los numeros de la linea base
# ===========================================================================

LINEA_BASE_ANTERIOR = {     # id: (d50, espesor, longitud), en m: T-8, `df1b23c`
    "A-01": (0.338, 0.592, 5.00),
    "A-02": (0.274, 0.479, 5.00),
}
LINEA_BASE_NUEVA = {        # con la envolvente: rige Laushey, clase 4
    "A-01": (0.338, 0.770, 5.40),
    "A-02": (0.274, 0.770, 5.40),
}


def test_manual_sigue_dando_exactamente_los_numeros_de_antes(corrida_manual):
    """
    La regla «manual» es la conducta de T-8, numero por numero. A-01: V =
    3.206 m/s -> 3.206²/(3.1·9.8) = 10.278/30.38 = 0.3383 m; espesor
    1.75·0.3383 = 0.592 m. A-02: 0.2736 m y 0.479 m. Longitud 5.00 m.
    """
    for id_punto, (d50, espesor, longitud) in LINEA_BASE_ANTERIOR.items():
        p = _punto(corrida_manual, id_punto).proteccion
        assert p.d50 == pytest.approx(d50, abs=ABS_IMPRESO_3_DECIMALES)
        assert p.d50 == pytest.approx(p.V ** 2 / (3.1 * 9.8), rel=REL_FORMULA)
        assert p.espesor == pytest.approx(espesor, abs=ABS_IMPRESO_3_DECIMALES)
        assert p.espesor == pytest.approx(1.75 * p.d50, rel=REL_FORMULA)
        assert p.longitud == pytest.approx(longitud, rel=REL_FORMULA)
        assert not p.rige_la_envolvente and p.requerida is None


def test_con_la_envolvente_se_mueven_espesor_y_longitud_y_no_el_d50(
        corrida_base):
    """
    LO QUE EL DUEÑO APROBO MOVER (2026-11-12), punto por punto. En los dos
    la piedra de Laushey es mayor que la que pide la Ec. (10.4) (A-01: 0.338
    contra 0.252 m; A-02: 0.274 contra la clase 1) y cae en la clase 4 (0.35
    m) de la Tabla 10.1: espesor 2.2·0.35 = 0.770 m y longitud 6·0.90 = 5.40
    m. El d50 NO se mueve.
    """
    for id_punto, (d50, espesor, longitud) in LINEA_BASE_NUEVA.items():
        p = _punto(corrida_base, id_punto).proteccion
        assert p.d50 == pytest.approx(d50, abs=ABS_IMPRESO_3_DECIMALES)
        assert p.d50 == pytest.approx(
            LINEA_BASE_ANTERIOR[id_punto][0], abs=ABS_IMPRESO_3_DECIMALES)
        assert p.espesor == pytest.approx(espesor, abs=ABS_IMPRESO_3_DECIMALES)
        assert p.longitud == pytest.approx(longitud, rel=REL_FORMULA)
        assert p.rige_la_envolvente


def test_ningun_diametro_ni_material_se_mueve_con_la_regla(corrida_base,
                                                           corrida_manual):
    """La Fase 6 corre DESPUES del dimensionado: lo que NO se aprobo mover."""
    for nueva, anterior in zip(corrida_base.puntos, corrida_manual.puntos):
        assert nueva.dimensionado == anterior.dimensionado
        if nueva.dimensionado:
            assert nueva.resultado.seccion == anterior.resultado.seccion
            assert nueva.resultado.material == anterior.resultado.material
    for id_punto in ("A-01", "A-02"):
        assert _punto(corrida_base, id_punto).resultado.seccion == \
            SeccionCircular(0.9)
