"""
tests/test_ve5_catlic.py
========================
VE-5, lote «catlic»: catalogo, Fase 10 y licuefaccion.

  * T4-06 (v8 Sec. 3.1): la rama de selva alta del catalogo del TMC, con el
    caracter de RECOMENDACION de su cita (Manual 4.1.1.3.7 a), PDF 82).
"""

import pytest

from src import datos_sitio as ds
from src.constantes_normativas import DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO
from src.modelos import NIVEL_PERFIL, TipoMaterial
from src.modulos import M2_material as M2
from src.normativa import registro as _registro
from src.normativa.esquema import Caracter, Verbo
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE

FECHA = "2026-11-20"
TRAZ_SELVA = ("prueba: corredor ficticio en selva alta, cauces con las cuatro "
              "caracteristicas del num. 4.1.1.3.7 a)")


@pytest.fixture
def selva_alta():
    ds.establecer_dato_dinamico("region_natural", ds.REGION_SELVA_ALTA,
                                TRAZ_SELVA, FECHA, origen="prueba")
    try:
        yield
    finally:
        ds.quitar_dato_dinamico("region_natural")


# ===========================================================================
# T4-06 - la rama de selva alta
# ===========================================================================

def test_t406_la_obra_del_repositorio_es_de_costa_y_la_rama_no_actua():
    assert ds.dato("region_natural").valor == ds.REGION_COSTA
    assert ds.dato("region_natural").nivel == NIVEL_PERFIL
    assert M2.piso_de_selva_alta(TipoMaterial.TMC) is None
    assert M2.siguiente_diametro(TipoMaterial.TMC) == pytest.approx(
        M2._progresion()["inicio"], rel=REL_TRANSPORTE)
    assert M2.catalogo(TipoMaterial.TMC).pasos == ()


def test_t406_la_rama_mira_la_region_siempre_que_el_material_es_tmc():
    ds.reiniciar_usos()
    M2.siguiente_diametro(TipoMaterial.TMC)
    assert "region_natural" in ds.datos_usados()
    ds.reiniciar_usos()
    M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO)
    M2.siguiente_diametro(TipoMaterial.HDPE)
    assert "region_natural" not in ds.datos_usados()


def test_t406_en_selva_alta_el_tmc_arranca_en_el_primer_escalon_de_48_in(selva_alta):
    piso = M2.piso_de_selva_alta(TipoMaterial.TMC)
    assert piso == pytest.approx(DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO,
                                 rel=REL_TRANSPORTE)
    primero = M2.siguiente_diametro(TipoMaterial.TMC)
    # 0.90 + 0.15 k: 1.20 queda por debajo de 48 in (1.2192 m); el primero
    # que no baja es 1.35 m (designado de AASHTO M 36).
    assert primero == pytest.approx(1.35, rel=REL_TRANSPORTE)
    assert primero >= piso
    # El concreto y el HDPE no reciben piso: la recomendacion es solo TMC.
    assert M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO) == \
        pytest.approx(M2._progresion()["inicio"], rel=REL_TRANSPORTE)
    assert M2.piso_de_selva_alta(TipoMaterial.HDPE) is None


def test_t406_la_memoria_dice_recomienda_y_no_obliga(selva_alta):
    pasos = M2.catalogo(TipoMaterial.TMC).pasos
    assert len(pasos) == 1
    p = pasos[0]
    assert p.fundamento_id == M2.FUNDAMENTO_SELVA_ALTA
    assert M2.CITA_SELVA_ALTA in p.citas_textuales
    reg = _registro.construir()
    assert reg.fundamento(M2.FUNDAMENTO_SELVA_ALTA).verbo is Verbo.RECOMIENDA
    assert reg.cita(M2.CITA_SELVA_ALTA).caracter is Caracter.RECOMENDACION
    assert "RECOMIENDA" in p.nota_del_proyecto
    assert p.resultado.valor == pytest.approx(1.35, rel=REL_TRANSPORTE)


def test_t406_la_region_es_un_conjunto_cerrado():
    with pytest.raises(ValueError):
        ds.verificar_declaracion_de_sitio("region_natural", "selva", TRAZ_SELVA)


# ===========================================================================
# T9-01 - la cuneta trapezoidal de la Tabla Nº 34 (> 3000 mm/año)
# ===========================================================================

import math                                                     # noqa: E402

from src import criterios_adoptados as ca                       # noqa: E402
from src.constantes_normativas import (                         # noqa: E402
    CUNETA_DIMENSIONES_MINIMAS_T34, CUNETA_FONDO_MIN_TRAPEZOIDAL_T34,
    K_MANNING_SI)
from src.modelos import DatoInvalidoError                       # noqa: E402
from src.modulos import M10_espaciamiento as M10                # noqa: E402

S_PRUEBA = 0.01
REL_FORMULA = 1e-9     # una formula de Manning recomputada en el test
REL_BRENT = 1e-8       # un tirante resuelto por brentq (xtol = TOL_BRENT)


@pytest.fixture
def seccion():
    """Declara una seccion de cuneta y la retira al salir."""
    def declarar(**campos):
        v = dict(ca.CRITERIOS["seccion_cuneta"].valor)
        v.update(campos)
        ca.establecer_valor_dinamico("seccion_cuneta", v)
        return v
    try:
        yield declarar
    finally:
        ca.quitar_valor_dinamico("seccion_cuneta")


def test_t901_el_minimo_de_la_nota_es_el_del_pdf():
    # PDF 181, pag. impresa 178: «* Sección Trapezoidal con un ancho mínimo
    # de fondo de 0.30»; fila «Muy lluviosa (>3000 mm/año)» 0.30* x 1.20.
    assert CUNETA_FONDO_MIN_TRAPEZOIDAL_T34 == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert CUNETA_DIMENSIONES_MINIMAS_T34["muy_lluviosa_mas_de_3000"] == \
        pytest.approx((0.30, 1.20), rel=REL_TRANSPORTE)


def test_t901_el_archivo_sigue_siendo_triangular_y_no_mueve_la_capacidad(seccion):
    base = M10.capacidad_cuneta(S_cuneta=S_PRUEBA)
    assert base.ancho_fondo_m == pytest.approx(0.0, abs=ABS_CERO)
    # Sin el campo no se le supone una seccion: M10 lo rechaza.
    v = dict(ca.CRITERIOS["seccion_cuneta"].valor)
    del v["ancho_fondo_m"]
    from tests.apoyo.criterios import con_valor
    with con_valor("seccion_cuneta", v,
                   motivo="la seccion sin el campo del fondo, para la "
                          "guardia de segunda linea de M10"):
        with pytest.raises(DatoInvalidoError):
            M10.capacidad_cuneta(S_cuneta=S_PRUEBA)

def test_t901_la_capacidad_trapezoidal_contra_el_calculo_a_mano(seccion):
    d, a, b, Z2 = 0.40, 1.20, 0.30, 1.0
    seccion(profundidad_m=d, ancho_m=a, ancho_fondo_m=b, talud_exterior_HV=Z2)
    c = M10.capacidad_cuneta(S_cuneta=S_PRUEBA)
    Z1 = (a - b) / d
    A = b * d + (Z1 + Z2) * d ** 2 / 2
    P = b + d * (math.sqrt(1 + Z1 ** 2) + math.sqrt(1 + Z2 ** 2))
    n = c.n          # 1/K de la Tabla Nº 32, contrastado en test_t9_*
    Q = (K_MANNING_SI / n) * A * (A / P) ** (2 / 3) * S_PRUEBA ** 0.5
    assert c.talud_interior_HV == pytest.approx(Z1, rel=REL_TRANSPORTE)
    assert c.area_llena_m2 == pytest.approx(A, rel=REL_TRANSPORTE)
    assert c.Q_llena_m3s == pytest.approx(Q, rel=REL_FORMULA)
    assert c.ancho_fondo_m == pytest.approx(b, rel=REL_TRANSPORTE)
    assert c.pasos[0].sustitucion[2].simbolo == "b"


def test_t901_el_tirante_de_la_velocidad_limite_cumple_manning(seccion):
    b, Z1, Z2, n, v = 0.30, 3.0, 1.0, 1 / 67, 1.5
    y_v, Q_v = M10.caudal_a_velocidad(v=v, n=n, S=S_PRUEBA, Z1=Z1, Z2=Z2, b=b)
    A, _P, Rh = M10.geometria_cuneta(y=y_v, Z1=Z1, Z2=Z2, b=b)
    V = (K_MANNING_SI / n) * Rh ** (2 / 3) * S_PRUEBA ** 0.5
    assert V == pytest.approx(v, rel=REL_BRENT)
    assert Q_v == pytest.approx(A * v, rel=REL_TRANSPORTE)
    # Con b = 0 es la cerrada de siempre.
    assert M10.caudal_a_velocidad(v=v, n=n, S=S_PRUEBA, Z1=Z1, Z2=Z2, b=0.0) == \
        M10.caudal_a_velocidad(v=v, n=n, S=S_PRUEBA, Z1=Z1, Z2=Z2)


@pytest.mark.parametrize("campos,culpable", [
    (dict(ancho_fondo_m=0.20), "ancho_fondo_m"),
    (dict(ancho_fondo_m=1.30), "ancho_fondo_m"),
    (dict(ancho_fondo_m=-0.1), "ancho_fondo_m"),
])
def test_t901_un_fondo_fuera_del_minimo_es_dato_invalido(seccion, campos, culpable):
    v = dict(ca.CRITERIOS["seccion_cuneta"].valor)
    v.update(campos)
    # Se pisa sin la puerta para probar la guardia de segunda linea de M10.
    from tests.apoyo.criterios import con_valor
    with con_valor("seccion_cuneta", v,
                   motivo="un fondo fuera del minimo, para la guardia de "
                          "segunda linea de M10"):
        with pytest.raises(DatoInvalidoError) as exc:
            M10.capacidad_cuneta(S_cuneta=S_PRUEBA)
    assert culpable in exc.value.campo


# ===========================================================================
# Item 6 - Fase 0-bis: licuefaccion como resultado declarado del EMS
# ===========================================================================

import json                                                      # noqa: E402
from pathlib import Path                                         # noqa: E402

import cli                                                       # noqa: E402
from src import servicio                                         # noqa: E402
from src import variables_entrada as ve                          # noqa: E402
from src.constantes_normativas import PROF_NF_LICUEFACCION_SI    # noqa: E402
from src.modelos import (CriterioPendienteError, DatoFaltanteError,  # noqa: E402
                         EstadoDeVerificacion, TipoDeBloqueo)
from src.modulos import ML_licuefaccion as ML                    # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
TRAZ_ZONA = "prueba: lectura ficticia de S_D1 para una obra en otra zona"
MW_ADOPTADA = 8.0          # escenario de PRUEBA, no del proyecto

EMS_NO_LICUA = {"resultado": "no_licua", "Mw": 8.0,
                "periodo_retorno_anios": 1000,
                "documento": "EMS de PRUEBA, informe 01", "fecha": "2026-11-20",
                "metodo": "procedimiento simplificado (NCEER), PRUEBA"}


@pytest.fixture
def zona():
    def declarar(z):
        ds.establecer_dato_dinamico("zona_sismica_aashto", z, TRAZ_ZONA, FECHA,
                                    origen="prueba")
    try:
        yield declarar
    finally:
        ds.quitar_dato_dinamico("zona_sismica_aashto")


@pytest.fixture
def mw():
    ca.establecer_valor_dinamico("Mw_licuefaccion", MW_ADOPTADA)
    try:
        yield MW_ADOPTADA
    finally:
        ca.quitar_valor_dinamico("Mw_licuefaccion")


def _declarada(**campos):
    return ML.validar_licuefaccion_declarada(dict(EMS_NO_LICUA, **campos))


def test_6_el_umbral_de_nf_es_50_ft():
    assert PROF_NF_LICUEFACCION_SI == pytest.approx(15.24, rel=REL_TRANSPORTE)


def test_6_sin_zona_leida_y_sin_resultado_el_expediente_se_detiene():
    with pytest.raises(DatoFaltanteError) as exc:
        ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=1.4,
                                declarada=None)
    assert exc.value.campo == ML.CLAVE_LICUEFACCION_EMS
    texto = str(exc.value)
    assert "10.5.4.2" in texto and "38.3" in texto and "S5" in texto
    assert "zona_sismica_aashto" in texto


@pytest.mark.parametrize("z,con_aviso", [(1, False), (2, True)])
def test_6_en_zonas_1_y_2_no_se_exige(zona, z, con_aviso):
    zona(z)
    v = ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=1.4,
                                declarada=None)
    assert v.estado is EstadoDeVerificacion.NO_APLICA and v.cumple
    assert bool(v.avisos) is con_aviso
    assert v.paso.fundamento_id == "F0.LICUEFACCION"


def test_6_en_zona_4_con_nf_hondo_no_se_exige(zona):
    zona(4)
    v = ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=20.0,
                                declarada=None)
    assert v.estado is EstadoDeVerificacion.NO_APLICA
    with pytest.raises(DatoFaltanteError):
        ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=15.0,
                                declarada=None)
    # Sin NF no se puede descartar: se exige.
    with pytest.raises(DatoFaltanteError):
        ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=None,
                                declarada=None)


def test_6_una_zona_fuera_de_1_a_4_es_dato_invalido(zona):
    zona(5)
    with pytest.raises(DatoInvalidoError):
        ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=1.4,
                                declarada=None)


def test_6_el_resultado_declarado_sin_mw_adoptada_detiene_en_el_criterio():
    with pytest.raises(CriterioPendienteError) as exc:
        ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=1.4,
                                declarada=_declarada())
    assert exc.value.clave == "Mw_licuefaccion"


def test_6_no_licua_contrastado_cumple(mw):
    v = ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=1.4,
                                declarada=_declarada())
    assert v.estado is EstadoDeVerificacion.CUMPLE and not v.avisos
    assert v.valor_obtenido == ML.RESULTADO_NO_LICUA


@pytest.mark.parametrize("campos,culpable", [
    (dict(periodo_retorno_anios=475), "periodo_retorno_anios"),
    (dict(Mw=7.5), "Mw"),
])
def test_6_una_evaluacion_por_debajo_de_lo_adoptado_es_dato_invalido(mw, campos, culpable):
    with pytest.raises(DatoInvalidoError) as exc:
        ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=1.4,
                                declarada=_declarada(**campos))
    assert exc.value.campo.endswith(culpable)


def test_6_licua_sin_mitigacion_bloquea_y_con_ella_cumple_con_aviso(mw):
    with pytest.raises(DatoFaltanteError) as exc:
        ML.evaluar_licuefaccion(id_punto="A-01", NF_profundidad_m=1.4,
                                declarada=_declarada(resultado="licua"))
    assert exc.value.campo == "licuefaccion_ems.mitigacion"
    v = ML.evaluar_licuefaccion(
        id_punto="A-01", NF_profundidad_m=1.4,
        declarada=_declarada(resultado="licua",
                             mitigacion="columnas de grava bajo el terraplen"))
    assert v.cumple and "columnas de grava" in v.avisos[0]


@pytest.mark.parametrize("malo", [
    "no_licua",
    dict(EMS_NO_LICUA, resultado="quizas"),
    dict(EMS_NO_LICUA, Mw=-1.0),
    dict(EMS_NO_LICUA, periodo_retorno_anios=1000.5),
    dict(EMS_NO_LICUA, documento=""),
    dict(EMS_NO_LICUA, extra=1),
])
def test_6_la_puerta_rechaza_un_resultado_mal_formado(malo):
    with pytest.raises(DatoInvalidoError):
        ML.validar_licuefaccion_declarada(malo)


def _externos(tmp_path, contenido):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    return cli.cargar_datos_externos(ruta, {"luz_m": 3.0})


def test_6_por_punto_gana_sobre_globales(tmp_path):
    otro = dict(EMS_NO_LICUA, documento="EMS de PRUEBA del punto A-01")
    externos = _externos(tmp_path, {"globales": {"licuefaccion_ems": EMS_NO_LICUA},
                                    "puntos": {"A-01": {"licuefaccion_ems": otro}}})
    assert externos.valor("A-01", "licuefaccion_ems")["documento"] == otro["documento"]
    assert externos.valor("B-01", "licuefaccion_ems")["documento"] == \
        EMS_NO_LICUA["documento"]


def _bloqueos_de_licuefaccion(informe):
    return [(p.punto.id, b) for p in informe.puntos for b in p.bloqueos
            if b.fase == servicio.FASE_LICUEFACCION]


def test_6_la_corrida_de_expediente_se_detiene_y_la_de_perfil_no(tmp_path):
    externos = _externos(tmp_path, {})
    expediente = cli.correr(CSV_PERFIL, externos, alcance=cli.ALCANCE_EXPEDIENTE)
    bloqueos = _bloqueos_de_licuefaccion(expediente)
    assert {i for i, _ in bloqueos} == {p.punto.id for p in expediente.puntos
                                        if p.fase_2_cerrada}
    assert all(b.tipo is TipoDeBloqueo.DATO_FALTANTE
               and b.campo == "licuefaccion_ems" for _, b in bloqueos)
    perfil = cli.correr(CSV_PERFIL, externos, alcance=cli.ALCANCE_PERFIL)
    # A perfil solo queda la constancia del diferimiento, nunca una falta.
    diferidos = _bloqueos_de_licuefaccion(perfil)
    assert diferidos and all(b.diferido_por_alcance
                             and b.tipo is TipoDeBloqueo.DIFERIDO_POR_ALCANCE
                             for _, b in diferidos)
    assert "ML_licuefaccion" in servicio.MODULOS_DIFERIDOS_POR_ALCANCE[
        cli.ALCANCE_PERFIL]


def test_6_con_el_resultado_declarado_el_bloqueo_desaparece(tmp_path, mw):
    externos = _externos(tmp_path, {"globales": {"licuefaccion_ems": EMS_NO_LICUA}})
    informe = cli.correr(CSV_PERFIL, externos, alcance=cli.ALCANCE_EXPEDIENTE)
    assert not _bloqueos_de_licuefaccion(informe)
    cerrados = [p for p in informe.puntos if p.fase_2_cerrada]
    assert cerrados and all(p.licuefaccion.cumple for p in cerrados)
    usados = set(informe.contexto.criterios_usados)
    assert {"Mw_licuefaccion", "demanda_sismica_licuefaccion"} <= usados


def test_6_los_tres_criterios_de_la_fase_0_bis_tienen_consumidor():
    for clave in ("Mw_licuefaccion", "demanda_sismica_licuefaccion",
                  "PERFIL_SUELO_PRESUNTO"):
        assert set(ve.variable(clave).consumido_por) == {"ML_licuefaccion"}, clave
        assert not ca.CRITERIOS[clave].sin_consumidor
        assert ca.CRITERIOS[clave].nivel == ca.NIVEL_EXPEDIENTE
    assert set(ve.variable("zona_sismica_aashto").consumido_por) == {"ML_licuefaccion"}


# ===========================================================================
# Censo Sec. 5, item 5: la clase de sitio MEDIDA frente a las filas de F_pga
# ===========================================================================

from src.modelos import MetodoNoEvaluableError                   # noqa: E402


@pytest.fixture
def clase():
    def declarar(c):
        ca.establecer_valor_dinamico("clase_sitio", c)
    try:
        yield declarar
    finally:
        ca.quitar_valor_dinamico("clase_sitio")


def test_5_sin_clase_no_hace_nada():
    assert ML.contrastar_clase_sitio() == ()


def test_5_clase_dentro_de_las_filas_avisa_con_el_factor_medido(clase):
    clase("E")
    avisos = ML.contrastar_clase_sitio()
    assert len(avisos) == 1
    assert "0.90" in avisos[0] and "1.00" in avisos[0]   # fila E y envolvente C/D/E


def test_5_clase_fuera_de_las_filas_invalida_F_pga(clase):
    clase("B")
    with pytest.raises(DatoInvalidoError) as exc:
        ML.contrastar_clase_sitio()
    assert exc.value.campo == "F_pga"


def test_5_la_fila_F_exige_el_procedimiento_de_sitio(clase):
    clase("F")
    with pytest.raises(MetodoNoEvaluableError) as exc:
        ML.contrastar_clase_sitio()
    assert "3.10.2" in str(exc.value)


def test_5_con_F_pga_de_una_fila_igual_a_la_clase_no_avisa(clase):
    clase("D")
    ca.establecer_valor_dinamico("F_pga", ("D",))
    try:
        assert ML.contrastar_clase_sitio() == ()
    finally:
        ca.quitar_valor_dinamico("F_pga")
