"""
tests/test_ve7_lote_c_licuefaccion.py
=====================================
VE-7, lote C, item C4 (VE5-CAT-03, «Qué haría falta»: una sección propia de
la memoria y del JSON para la Fase 0-bis; decision del consultor Fable,
triaje VE-7, 2026-11-20).

Hasta VE-7 la Fase 0-bis viajaba como `InformePunto.licuefaccion`, su paso
y sus avisos, y ninguna de las dos vistas la mostraba como fase: el JSON no
la publicaba y la memoria solo pintaba sus avisos entre los «que faltan».
Desde VE-7:

  * el JSON del punto lleva la clave `licuefaccion` (None si la fase no
    corrio: perfil, punto sin clasificar o etapa bloqueada; si no, el
    estado de la `Verificacion`, el resultado, lo exigido y los avisos);
  * la memoria del punto lleva la seccion «Fase 0-bis» con esos mismos
    textos y el paso `F0.LICUEFACCION` desarrollado una vez;
  * con la etapa bloqueada a expediente, la seccion lo dice y remite a la
    tabla de bloqueos; a perfil (diferida) no hay seccion.

Las guardias de T-10 se respetan: todo texto del JSON del punto esta en su
bloque de la memoria (`tests/test_t10_memoria.py`).
"""

import html as _html
import json
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.modelos import EstadoDeVerificacion
from src.modulos import M11_reporte as M11
from src.modulos import ML_licuefaccion as ML
from tests.test_t10_memoria import _bloques, _hojas, _texto_del_punto

RAIZ = Path(__file__).resolve().parents[1]
CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
FECHA = "2026-11-20"
TRAZ_ZONA = "prueba: lectura ficticia de S_D1 para una obra en otra zona"
MW_ADOPTADA = 8.0          # escenario de PRUEBA, no del proyecto

EMS_LICUA = {"resultado": "licua", "Mw": 8.0, "periodo_retorno_anios": 1000,
             "documento": "EMS de PRUEBA, informe 07", "fecha": "2026-11-20",
             "metodo": "procedimiento simplificado (NCEER), PRUEBA",
             "mitigacion": "columnas de grava de PRUEBA bajo el cabezal"}


def _externos(tmp_path, contenido):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    return cli.cargar_datos_externos(ruta, {"luz_m": 3.0})


def _vistas(informe):
    html = M11.memoria_html(informe, proyecto="VE-7 C4",
                            ruta_plantilla=cli.plantilla_por_alcance(
                                informe.alcance))
    js = json.loads(json.dumps(cli.informe_json(informe), ensure_ascii=False,
                               default=str))
    return js, html


@pytest.fixture(scope="module")
def declarada(tmp_path_factory):
    """A expediente, con el EMS declarado (licua, con mitigacion) y M_w."""
    ca.establecer_valor_dinamico("Mw_licuefaccion", MW_ADOPTADA)
    try:
        externos = _externos(tmp_path_factory.mktemp("c4"),
                             {"globales": {"licuefaccion_ems": EMS_LICUA}})
        informe = cli.correr(CSV_PERFIL, externos,
                             alcance=cli.ALCANCE_EXPEDIENTE)
        return (informe, *_vistas(informe))
    finally:
        ca.quitar_valor_dinamico("Mw_licuefaccion")


@pytest.fixture(scope="module")
def no_aplica(tmp_path_factory):
    """A expediente en zona sismica 1: 10.5.4.2 no exige la evaluacion."""
    ds.establecer_dato_dinamico("zona_sismica_aashto", 1, TRAZ_ZONA, FECHA,
                                origen="prueba")
    try:
        externos = _externos(tmp_path_factory.mktemp("c4na"), {})
        informe = cli.correr(CSV_PERFIL, externos,
                             alcance=cli.ALCANCE_EXPEDIENTE)
        return (informe, *_vistas(informe))
    finally:
        ds.quitar_dato_dinamico("zona_sismica_aashto")


def _con_fase(informe):
    return [p for p in informe.puntos if p.licuefaccion is not None]


def test_C4_la_etapa_de_M11_es_la_del_modulo():
    assert M11.ETAPA_LICUEFACCION == ML.ETAPA_LICUEFACCION


def test_C4_el_json_del_punto_lleva_la_clave_licuefaccion(declarada):
    informe, js, _html_ = declarada
    con = _con_fase(informe)
    assert con, "la corrida de prueba no llego a la Fase 0-bis"
    for p, pj in zip(informe.puntos, js["puntos"]):
        assert "licuefaccion" in pj
        if p.licuefaccion is None:
            assert pj["licuefaccion"] is None
            continue
        lj = pj["licuefaccion"]
        v = p.licuefaccion
        assert lj["codigo"] == ML.CODIGO_LICUEFACCION == v.codigo
        assert lj["estado"] == v.estado.value == EstadoDeVerificacion.CUMPLE.value
        assert lj["cumple"] is True
        assert lj["valor_obtenido"] == "licua"
        assert lj["valor_admisible"] == v.valor_admisible
        assert lj["criterio_aplicado"] == "Mw_licuefaccion"
        assert lj["avisos"] == list(v.avisos) and lj["avisos"]
        assert lj["motivo_no_aplica"] is None


def test_C4_la_memoria_tiene_la_seccion_con_los_textos_del_json(declarada):
    informe, js, html = declarada
    bloques = _bloques(html)
    for p, pj in zip(informe.puntos, js["puntos"]):
        bloque = bloques[p.punto.id]
        if p.licuefaccion is None:
            assert M11.TITULO_LICUEFACCION not in bloque
            continue
        assert _html.escape(M11.TITULO_LICUEFACCION) in bloque
        texto = _texto_del_punto(html, p.punto.id)
        for ruta, valor in _hojas(pj["licuefaccion"]):
            if isinstance(valor, str) and valor.strip():
                assert " ".join(valor.split()) in texto, (p.punto.id, ruta)


def test_C4_el_paso_de_la_fase_0_bis_se_desarrolla_una_vez(declarada):
    informe, _js, html = declarada
    for p in _con_fase(informe):
        paso = p.licuefaccion.paso
        assert paso is not None and paso.fundamento_id == "F0.LICUEFACCION"
        assert paso in M11.pasos_del_punto(p)
        assert paso in M11.pasos_impresos(informe)
        assert M11.traza_licuefaccion(p) == (paso,)
    encabezado = (f"<code>{_html.escape(ML.CODIGO_LICUEFACCION)}</code> "
                  "&mdash; ")
    # un paso por punto que llego a la fase, y ninguno repetido
    assert html.count(encabezado) == len(_con_fase(informe))


def test_C4_no_aplica_imprime_el_motivo(no_aplica):
    informe, js, html = no_aplica
    con = _con_fase(informe)
    assert con
    for p, pj in zip(informe.puntos, js["puntos"]):
        if p.licuefaccion is None:
            continue
        assert p.licuefaccion.estado is EstadoDeVerificacion.NO_APLICA
        lj = pj["licuefaccion"]
        assert lj["estado"] == EstadoDeVerificacion.NO_APLICA.value
        assert lj["motivo_no_aplica"] == p.licuefaccion.motivo_no_aplica
        assert lj["valor_obtenido"] is None
        assert _html.escape(lj["motivo_no_aplica"]) in _bloques(html)[p.punto.id]


def test_C4_con_la_etapa_bloqueada_la_seccion_remite_a_los_bloqueos(tmp_path):
    informe = cli.correr(CSV_PERFIL, _externos(tmp_path, {}),
                         alcance=cli.ALCANCE_EXPEDIENTE)
    js, html = _vistas(informe)
    bloques = _bloques(html)
    bloqueados = [p for p in informe.puntos
                  if any(b.etapa == ML.ETAPA_LICUEFACCION
                         and not b.diferido_por_alcance for b in p.bloqueos)]
    assert bloqueados
    for p in bloqueados:
        assert p.licuefaccion is None
        pj = next(x for x in js["puntos"] if x["id"] == p.punto.id)
        assert pj["licuefaccion"] is None
        bloque = bloques[p.punto.id]
        assert _html.escape(M11.TITULO_LICUEFACCION) in bloque
        assert _html.escape(M11.TEXTO_LICUEFACCION_BLOQUEADA) in bloque


def test_C4_a_perfil_no_hay_seccion_y_la_clave_es_nula(tmp_path):
    informe = cli.correr(CSV_PERFIL, _externos(tmp_path, {}),
                         alcance=cli.ALCANCE_PERFIL)
    js, html = _vistas(informe)
    assert all(pj["licuefaccion"] is None for pj in js["puntos"])
    assert _html.escape(M11.TITULO_LICUEFACCION) not in html


# ===========================================================================
# Dictamen Fable del 2026-11-20, abierto (iii): la linea del volcado de texto
# ===========================================================================

def _partes_de_la_linea(v):
    """Los textos que la linea de la CLI imprime de la Fase 0-bis."""
    partes = [v.codigo, str(v.numeral), v.estado.value]
    for x in (v.valor_obtenido, v.valor_admisible, v.criterio_aplicado,
              v.motivo_no_aplica):
        if x:
            partes.append(str(x))
    return partes


@pytest.fixture(scope="module")
def cuarta():
    from src import indice_formulas as ind
    corrida = next(c for c in ind.CORRIDAS_DE_REFERENCIA
                   if c.nombre == "materiales_y_ramas")
    informe = ind.correr_referencia(corrida)
    return (informe, *_vistas(informe))


def test_iii_la_cli_imprime_la_fase_0_bis_de_los_cuatro_puntos(cuarta):
    informe, _js, html = cuarta
    texto = cli.volcar(informe)
    bloques = _bloques(html)
    assert len(informe.puntos) == 4
    for p in informe.puntos:
        lineas = cli._lineas_licuefaccion(p)
        v = p.licuefaccion
        assert v is not None, p.punto.id
        assert lineas[0].strip().startswith(f"Fase 0-bis {v.codigo} ")
        assert " · EMS: no_licua" in lineas[0]
        for linea in lineas:
            assert linea in texto
        # guardia T-10: lo que la linea dice esta en el bloque de la memoria
        plano = _texto_del_punto(html, p.punto.id)
        assert p.punto.id in bloques
        for parte in _partes_de_la_linea(v):
            assert " ".join(parte.split()) in plano, (p.punto.id, parte)


def test_iii_la_cli_dice_la_fase_0_bis_bloqueada(tmp_path):
    informe = cli.correr(CSV_PERFIL, _externos(tmp_path, {}),
                         alcance=cli.ALCANCE_EXPEDIENTE)
    texto = cli.volcar(informe)
    bloqueados = [p for p in informe.puntos
                  if any(b.etapa == ML.ETAPA_LICUEFACCION
                         and not b.diferido_por_alcance for b in p.bloqueos)]
    assert bloqueados
    for p in bloqueados:
        assert cli._lineas_licuefaccion(p) == [
            f"{cli.SANGRIA}Fase 0-bis licuefaccion: no evaluada (ver bloqueos)"]
    assert "Fase 0-bis licuefaccion: no evaluada (ver bloqueos)" in texto


def test_iii_no_aplica_imprime_el_motivo_en_la_segunda_linea(no_aplica):
    informe, _js, html = no_aplica
    for p in informe.puntos:
        if p.licuefaccion is None:
            continue
        lineas = cli._lineas_licuefaccion(p)
        assert len(lineas) == 2
        assert lineas[1].strip() == p.licuefaccion.motivo_no_aplica
        plano = _texto_del_punto(html, p.punto.id)
        for parte in _partes_de_la_linea(p.licuefaccion):
            assert " ".join(parte.split()) in plano, (p.punto.id, parte)


def test_iii_a_perfil_no_hay_linea(tmp_path):
    informe = cli.correr(CSV_PERFIL, _externos(tmp_path, {}),
                         alcance=cli.ALCANCE_PERFIL)
    assert all(cli._lineas_licuefaccion(p) == [] for p in informe.puntos)
    texto = cli.volcar(informe)
    assert "Fase 0-bis 0B.1" not in texto
    assert "Fase 0-bis licuefaccion: no evaluada" not in texto
