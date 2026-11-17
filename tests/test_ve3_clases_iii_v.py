"""
tests/test_ve3_clases_iii_v.py
==============================
VE-3.12 · Decisiones 1, 6 y 7 del dueño (2026-11-17,
`proceso/planes_mejora/ve3_estado/LEEME.md`), sobre los dos informes de
verificacion de `proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/`.

1. LAS CLASES III, IV Y V DEL TUBO DE CONCRETO, como [C], desde la tabla
   «ASTM C76 Class and D0.01» del ejemplo resuelto del USACE EM 1110-2-2902
   (pag. impresa B-7, PDF 71): 65, 100 y 140 N/m/mm, los nominales de la
   norma metrica. Hasta VE-3.12 solo la Clase II (50.0) estaba transcrita y
   ningun tubo de concreto con mas de ~2.4 m de tierra sobre la clave cerraba
   (ensayos de diseño del conducto, H1).
2. CON EL TOPE DE DIAMETRO POR CLASE de M 170M (H1 del informe de las
   clases): la Clase V con pared B solo hasta 1200 mm (Tabla 5, PDF 10); de
   la Tabla 4 (Clase IV) solo se lee la fila de 300 mm, y por encima la Clase
   IV queda BLOQUEADA: un tubo que la necesite se detiene con el dato que
   falta, no recibe otra clase ni otro diametro.
3. EL CONTRASTE DE LA PRACTICA ACPA (decision 6): la carga viva sigue con la
   lectura literal de AASHTO LRFD 9.a (sin longitud efectiva); con menos de
   `relleno_max_contraste_acpa_m` hasta la rasante, el paso F8.CLASE avisa que
   clase saldria con la L_e de ACPA DD 1 (Eq. [2]), rotulado como contraste
   que NO gobierna.

Los rellenos de los casos se midieron con las cinco clases de prueba
(`CINCO_CLASES_DE_PRUEBA` de T-5) y el punto A01 del caso patron de la Fase
8: con Ø 0.90 m, H = 5.0 m pide 77.6 N/m/mm (banda de la Clase IV), H = 7.0 m
pide 104.7 (banda de la V); con Ø 1.35 m, H = 5.0 m pide 79.4 y H = 7.0 m
pide 106.9. Cada test lo vuelve a comprobar antes de usarlo.

SE ESCRIBIO EN ROJO PRIMERO, contra d78f2c4.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src.modelos import DatoFaltanteError, SeccionCircular, TipoMaterial
from src.modulos import M8_estructural as M8
from src.normativa import fuentes
from src.normativa.registro import construir as cargar_registro
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, declarados
from tests.test_t5_correcciones_auditoria import (  # noqa: F401 (fixtures)
    CINCO_CLASES_DE_PRUEBA, _mat, _por_codigo, a01, del_expediente)

CLASES_DE_ARCHIVO = {"II": 50.0, "III": 65.0, "IV": 100.0, "V": 140.0}
CLAVE_UMBRAL_ACPA = "relleno_max_contraste_acpa_m"


def _concreto(punto, D, H):
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    return M8.verificar_concreto(punto=punto, material=mat,
                                 seccion=SeccionCircular(D), altura_relleno=H)


def _pedida(punto, D, H):
    """
    La D-load que el tubo pide, medida con las cinco clases de prueba y SIN
    el bloqueo de la Clase IV (solo para medir la demanda: la seleccion que
    se prueba despues corre con el bloqueo).
    """
    with declarados({"clases_producto_por_relleno": CINCO_CLASES_DE_PRUEBA}), \
            patch.dict(CN.DIAMETRO_MAX_LEGIBLE_POR_CLASE_M170M_MM, clear=True):
        r = _concreto(punto, D, H)
    return _por_codigo(r)[M8.CODIGO_CLASE].valor_obtenido


# ---------------------------------------------------------------------------
# 1. Las clases transcritas y su fuente
# ---------------------------------------------------------------------------

def test_las_clases_III_a_V_estan_transcritas_con_su_valor_de_archivo():
    valor = ca.CRITERIOS["clases_producto_por_relleno"].valor
    assert valor == {"concreto_reforzado": CLASES_DE_ARCHIVO}
    # La Clase I NO: la norma solo la tabula desde 1500 mm y la decision 1
    # del dueño son las Clases III a V.
    assert "I" not in valor["concreto_reforzado"]


def test_la_fuente_del_usace_esta_registrada_como_secundaria():
    f = fuentes.FUENTES["USACE_EM_1110_2_2902"]
    assert f.sha1 == "cfdc3bfd1c9291d30c98de11f27b1f1fbf7a95d8"
    assert f.paginacion.pagina_pdf("B-7") == 71
    reg = cargar_registro()
    c = reg.cita("USACE_EM_1110_2_2902.B-7#C76")
    assert c.pagina_impresa == "B-7" and c.pagina_pdf == 71
    assert c.texto_literal.texto == "ASTM C76 Class and D0.01"
    assert "EJEMPLO RESUELTO" in c.nota and "NOMINALES" in c.nota
    for fila in ("III 65 (1,350)", "IV 100 (2,000)", "V 140 (3,000)"):
        assert fila in c.nota
    for cid in ("AASHTO_M170M.T5#PARED_B", "AASHTO_M170M.T4#LEGIBLE"):
        assert reg.cita(cid).fuente_id == "AASHTO_M170M"


@pytest.mark.pdf
def test_las_cifras_estan_impresas_en_la_pagina_del_usace():
    from src.normativa.extraccion.pdf import texto_de_pagina
    f = fuentes.FUENTES["USACE_EM_1110_2_2902"]
    texto = texto_de_pagina(fuentes.ruta_pdf(f), 71)
    assert "ASTM C76 Class and D0.01" in texto
    for cifra in ("40 (800)", "50 (1,000)", "65 (1,350)", "100 (2,000)",
                  "140 (3,000)"):
        assert cifra in texto


# ---------------------------------------------------------------------------
# 2. Los topes de diametro por clase
# ---------------------------------------------------------------------------

def test_los_topes_leidos_de_M170M():
    assert CN.DIAMETRO_MAX_TABULADO_PARED_B_POR_CLASE_M170M_MM == {"V": 1200}
    assert CN.DIAMETRO_MAX_LEGIBLE_POR_CLASE_M170M_MM == {"IV": 300}


def test_a_0_90_m_se_ofrecen_II_III_y_V_y_la_IV_queda_bloqueada():
    ofrecidas, faltan = M8.clases_de_concreto_para(0.90)
    assert list(ofrecidas) == ["II", "III", "V"] and faltan == ()
    assert M8.clases_bloqueadas_para(0.90) == ("IV",)


def test_a_1_35_m_la_V_no_se_ofrece_porque_no_tiene_pared_B():
    ofrecidas, faltan = M8.clases_de_concreto_para(1.35)
    assert list(ofrecidas) == ["II", "III"] and faltan == ()
    assert M8.clases_bloqueadas_para(1.35) == ("IV",)
    # A 1.20 m todavia si: es la ultima fila con pared B de la Tabla 5.
    assert "V" in M8.clases_de_concreto_para(1.20)[0]


def test_a_0_30_m_la_IV_si_se_lee_y_se_ofrece():
    assert "IV" in M8.clases_de_concreto_para(0.30)[0]
    assert M8.clases_bloqueadas_para(0.30) == ()


# ---------------------------------------------------------------------------
# 3. Lo que hace el tubo con las clases y los topes
# ---------------------------------------------------------------------------

def test_un_tubo_que_cabe_en_la_clase_III_la_recibe(del_expediente, a01):
    assert 50.0 < _pedida(a01, 0.90, 4.0) < 65.0
    assert _concreto(a01, 0.90, 4.0).seleccion == "Clase III"


def test_un_tubo_que_necesita_la_IV_bloqueada_se_detiene_con_el_dato(
        del_expediente, a01):
    """
    Ø 0.90 m con 5.0 m pide 77.6 N/m/mm: la Clase IV (100) alcanzaria, pero
    el ejemplar no deja verificar que M 170M la tabule a 900 mm. No se le da
    la V para esquivarla (decision 7 del dueño): se detiene con el dato.
    """
    assert 65.0 < _pedida(a01, 0.90, 5.0) <= 100.0
    with pytest.raises(DatoFaltanteError) as exc:
        _concreto(a01, 0.90, 5.0)
    assert exc.value.campo == "clases_producto_por_relleno"
    assert "Clase IV" in str(exc.value) and "300 mm" in str(exc.value)


def test_un_tubo_que_pide_mas_que_la_IV_recibe_la_V_donde_la_V_existe(
        del_expediente, a01):
    assert 100.0 < _pedida(a01, 0.90, 7.0) <= 140.0
    r = _concreto(a01, 0.90, 7.0)
    assert r.seleccion == "Clase V"
    v = _por_codigo(r)[M8.CODIGO_CLASE]
    assert "USACE_EM_1110_2_2902.B-7#C76" in v.paso.citas_textuales
    assert "USACE" in v.paso.umbral.descripcion


def test_por_encima_de_1200_mm_un_tubo_que_pide_mas_que_la_IV_no_cumple(
        del_expediente, a01):
    """
    Ø 1.35 m con 7.0 m pide 106.9: la IV no alcanza y la V no tiene pared B a
    ese diametro (diseño especial de la Seccion 7.2). No falta ningun dato:
    el tubo NO CUMPLE y MD prueba lo siguiente.
    """
    assert 100.0 < _pedida(a01, 1.35, 7.0) <= 140.0
    r = _concreto(a01, 1.35, 7.0)
    v = _por_codigo(r)[M8.CODIGO_CLASE]
    assert not v.cumple and r.seleccion == ""


def test_por_encima_de_1200_mm_la_banda_de_la_IV_tambien_se_detiene(
        del_expediente, a01):
    assert 65.0 < _pedida(a01, 1.35, 5.0) <= 100.0
    with pytest.raises(DatoFaltanteError):
        _concreto(a01, 1.35, 5.0)


# ---------------------------------------------------------------------------
# 4. El contraste de la practica ACPA (no gobierna)
# ---------------------------------------------------------------------------

def test_el_umbral_del_contraste_es_un_criterio_A_con_valor_del_dueño():
    c = ca.CRITERIOS[CLAVE_UMBRAL_ACPA]
    assert c.etiqueta == "A" and c.valor == pytest.approx(1.0, abs=ABS_CERO)
    assert c.sensibilidad is not None and c.resolucion is not None


def test_con_poco_relleno_el_paso_avisa_la_clase_de_ACPA_sin_cambiarla(
        del_expediente, a01):
    """0.60 m de relleno + 0.15 m de paquete = 0.75 m hasta la rasante."""
    r = _concreto(a01, 0.90, 0.60)
    v = _por_codigo(r)[M8.CODIGO_CLASE]
    avisos = " ".join(r.avisos)
    assert "ACPA" in avisos and "NO GOBIERNA" in avisos
    assert "L_e" in avisos
    assert "ACPA" in v.paso.nota_del_proyecto
    # La clase que rige es la de la lectura literal.
    assert r.seleccion == "Clase II"


def test_con_relleno_suficiente_no_hay_contraste_ACPA(del_expediente, a01):
    """1.00 m + 0.15 m = 1.15 m hasta la rasante: por encima del umbral."""
    r = _concreto(a01, 0.90, 1.00)
    assert "ACPA" not in " ".join(r.avisos)


def test_el_umbral_se_lee_del_criterio(del_expediente, a01):
    with con_valor(CLAVE_UMBRAL_ACPA, 1.2,
                   motivo="umbral subido para que 1.15 m quede por debajo"):
        r = _concreto(a01, 0.90, 1.00)
    assert "ACPA" in " ".join(r.avisos)


def test_la_carga_del_contraste_es_la_de_ACPA_DD1_ec_2(del_expediente, a01):
    """
    W_L(ACPA) = W_L · w_w / L_e, L_e = w_w + 1.75 · (3/4) · B_c: la longitud
    efectiva de ACPA DD 1 (2009), Eq. [2], aplicada sobre el reparto de la
    9.a ed. Se recalcula aqui con los numeros del paso.
    """
    r = _concreto(a01, 0.90, 0.60)
    (paso_c,) = [p for p in r.pasos if p.codigo == M8.CODIGO_CONTRASTE_ACPA]
    s = {m.simbolo: m.valor for m in paso_c.sustitucion}
    L_e = s["w_w"] + 1.75 * 0.75 * s["B_c"]
    assert paso_c.resultado.valor == pytest.approx(
        s["W_L"] * s["w_w"] / L_e, rel=REL_TRANSPORTE)
