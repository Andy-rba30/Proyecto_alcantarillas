"""
tests/test_cli.py
=================
Pruebas del orquestador de linea de comandos: que corra el pipeline completo,
que registre cada bloqueo con su causa y que no rellene ningun vacio.

Dos cosas que estas pruebas fijan a proposito:

1. Con los criterios como estan hoy, NINGUN punto se dimensiona: V5 y V8 de la
   Fase 5 son vacios declarados y la Fase 5 no puede completarse. El informe de
   un punto dimensionado se prueba sustituyendo `MD.disenar_punto` -- lo que se
   verifica ahi es la capa de reporte (material, D, control gobernante,
   verificaciones con numeral), no el bucle de MD, que tiene sus propias
   pruebas en tests/test_MD.py.

2. Un criterio se declara con `monkeypatch.setitem` sobre `ca.CRITERIOS`, el
   mismo patron de tests/test_M5_verificaciones.py: la prueba no toca el
   archivo de criterios, solo simula que el Tablero 3 se cerro.
"""

import json
from pathlib import Path

import pytest

import cli
import criterios_adoptados as ca
from modelos import (ControlGobernante, DatoInvalidoError,
                     ResultadoHidraulico, ResultadoPunto, TipoMaterial,
                     Verificacion)
from modulos.M0_carga import cargar_puntos
from modulos.M2_material import catalogo

CSV = Path(__file__).resolve().parent / "ejemplo_puntos.csv"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _declarar(monkeypatch, **valores):
    """Le da valor a criterios hoy vacios, sin tocar criterios_adoptados.py."""
    for clave, valor in valores.items():
        original = ca.CRITERIOS[clave]
        monkeypatch.setitem(
            ca.CRITERIOS, clave,
            original.__class__(**{**original.__dict__, "valor": valor}),
        )


def _externos(**globales):
    return cli.cargar_datos_externos(None, dict(globales))


def _informe(**globales):
    return cli.correr(CSV, _externos(**globales))


def _informe_por_punto(globales, por_punto):
    """Como `_informe`, con datos declarados punto por punto."""
    externos = cli.DatosExternos(
        {k: cli.DatoDeclarado(k, v, "prueba") for k, v in globales.items()},
        {id_punto: {k: cli.DatoDeclarado(k, v, "prueba")
                    for k, v in campos.items()}
         for id_punto, campos in por_punto.items()})
    return cli.correr(CSV, externos)


def _punto(informe, id_punto):
    return next(i for i in informe.puntos if i.punto.id == id_punto)


def _claves_bloqueantes(informe_punto):
    return {b.criterio for b in informe_punto.bloqueos if b.criterio}


# ---------------------------------------------------------------------------
# Datos externos: lo que no es columna de Sec. 1.2
# ---------------------------------------------------------------------------

def test_clave_desconocida_es_dato_invalido(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps({"globales": {"luz": 2.0}}), encoding="utf-8")
    with pytest.raises(DatoInvalidoError) as excinfo:
        cli.cargar_datos_externos(ruta, {})
    assert "luz" in str(excinfo.value)


def test_seccion_desconocida_es_dato_invalido(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps({"puntos_criticos": {}}), encoding="utf-8")
    with pytest.raises(DatoInvalidoError):
        cli.cargar_datos_externos(ruta, {})


def test_tw_cero_se_admite_porque_es_salida_libre():
    externos = _externos(TW_m=0.0)
    assert externos.valor("A-01", "TW_m") == 0.0


def test_longitud_cero_o_negativa_es_dato_invalido():
    for valor in (0.0, -3.0):
        with pytest.raises(DatoInvalidoError):
            _externos(longitud_m=valor)


def test_dato_por_punto_pisa_al_global(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps({"globales": {"luz_m": 2.0},
                                "puntos": {"A-01": {"luz_m": 4.0}}}),
                    encoding="utf-8")
    externos = cli.cargar_datos_externos(ruta, {})
    assert externos.valor("A-01", "luz_m") == 4.0
    assert externos.valor("A-02", "luz_m") == 2.0


def test_bandera_pisa_al_global_del_archivo(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps({"globales": {"luz_m": 2.0}}), encoding="utf-8")
    externos = cli.cargar_datos_externos(ruta, {"luz_m": 5.0})
    dato = externos.dato("A-01", "luz_m")
    assert dato.valor == 5.0
    assert "linea de comandos" in dato.origen


def test_categoria_tr_viaja_como_texto():
    externos = _externos(categoria_tr="quebrada_menor")
    assert externos.valor("A-01", "categoria_tr") == "quebrada_menor"


def test_categoria_tr_numerica_es_dato_invalido():
    with pytest.raises(DatoInvalidoError):
        _externos(categoria_tr=71)


def test_origen_del_dato_queda_registrado():
    dato = _externos(longitud_m=12.0).dato("A-01", "longitud_m")
    assert dato.origen == "linea de comandos (--longitud_m)"


# ---------------------------------------------------------------------------
# Fase 2: sin luz no hay pipeline
# ---------------------------------------------------------------------------

def test_sin_luz_ningun_punto_se_dimensiona():
    informe = _informe()
    assert informe.dimensionados == 0
    for punto in informe.puntos:
        faltantes = [b for b in punto.bloqueos if b.campo == "luz_m"]
        assert faltantes, f"{punto.punto.id} deberia reclamar la luz"
        assert punto.clasificacion is None


def test_luz_declarada_clasifica_y_trae_la_verificacion_de_la_luz():
    informe = _informe(luz_m=2.0)
    b01 = _punto(informe, "B-01")
    assert b01.clasificacion.en_alcance
    assert b01.clasificacion.periodo_retorno.anios == 35
    numerales = [v.numeral for _, v in b01.verificaciones()]
    assert numerales, "la luz tiene que aparecer como verificacion con numeral"


def test_familia_a_se_detiene_en_el_umbral_de_quebrada_sin_categoria():
    informe = _informe(luz_m=2.0)
    assert "umbral_area_quebrada_importante_ha" in _claves_bloqueantes(
        _punto(informe, "A-01"))


def test_categoria_declarada_desbloquea_el_tr_de_la_familia_a():
    informe = _informe(luz_m=2.0, categoria_tr="quebrada_importante")
    a01 = _punto(informe, "A-01")
    assert a01.clasificacion.periodo_retorno.anios == 71
    assert "umbral_area_quebrada_importante_ha" not in _claves_bloqueantes(a01)


def test_luz_de_puente_deja_el_punto_fuera_de_alcance():
    informe = _informe(luz_m=6.0, categoria_tr="quebrada_menor")
    a01 = _punto(informe, "A-01")
    assert not a01.clasificacion.en_alcance
    assert not a01.dimensionado
    assert any(b.tipo == "DisenoNoFactibleError" for b in a01.bloqueos)


# ---------------------------------------------------------------------------
# Fases 3-5: los vacios que hoy detienen el dimensionamiento
# ---------------------------------------------------------------------------

def test_sin_tw_ni_longitud_se_bloquean_los_dos_insumos_de_md():
    informe = _informe(luz_m=2.0, categoria_tr="quebrada_menor")
    claves = _claves_bloqueantes(_punto(informe, "A-01"))
    assert {"TW_receptor", "talud_terraplen"} <= claves


def test_con_tw_y_longitud_el_bucle_de_md_llega_a_la_fase_5():
    """
    El siguiente vacio esta dentro de la Fase 5, no en un insumo que falte:
    MD ya corrio. Es V7 ('peso_especifico_relleno_kn_m3') y no V5, porque V5
    dejo de detener la secuencia: se difiere al expediente con cumple=None.
    """
    informe = _informe(luz_m=2.0, categoria_tr="quebrada_menor",
                       TW_m=0.0, longitud_m=12.0)
    a01 = _punto(informe, "A-01")
    assert "peso_especifico_relleno_kn_m3" in _claves_bloqueantes(a01)
    assert "remanso_derecho_via" not in _claves_bloqueantes(a01)
    assert not a01.dimensionado


def test_la_longitud_declarada_se_registra_con_su_origen():
    informe = _informe(luz_m=2.0, TW_m=0.0, longitud_m=12.0)
    b01 = _punto(informe, "B-01")
    assert b01.longitud.valor == 12.0
    assert "linea de comandos" in b01.longitud.origen
    assert b01.tw.origen == "linea de comandos (--TW_m)"


def test_familia_c_sin_caudal_reclama_la_columna():
    """Sec. 2.3: el caudal de la Familia C es el del canal y la columna va vacia."""
    informe = _informe(luz_m=2.0, TW_m=0.0, longitud_m=12.0)
    c01 = _punto(informe, "C-01")
    assert any(b.tipo == "DatoFaltanteError" and b.campo == "Q_m3s"
               for b in c01.bloqueos)


def test_familia_c_con_caudal_declarado_no_tiene_material_candidato():
    """El catalogo de Sec. 3.2 es circular; la Familia C es marco o multicelda."""
    informe = _informe_por_punto(
        {"luz_m": 2.0, "TW_m": 0.0, "longitud_m": 12.0},
        {"C-01": {"Q_m3s": 0.9, "S_conducto": 0.004}})
    c01 = _punto(informe, "C-01")
    motivos = [b.mensaje for b in c01.bloqueos
               if b.tipo == "DisenoNoFactibleError"]
    assert motivos and "Familia C" in motivos[0]


# ---------------------------------------------------------------------------
# Fase 10
# ---------------------------------------------------------------------------

def test_espaciamiento_de_alivio_solo_en_familia_b():
    informe = _informe(luz_m=2.0, L_hidraulico_m=180.0)
    assert _punto(informe, "B-01").espaciamiento.espaciamiento_max == 180.0
    for id_punto in ("A-01", "A-02", "C-01"):
        assert _punto(informe, id_punto).espaciamiento is None


def test_sin_l_hidraulico_la_fase_10_se_bloquea_por_dato_faltante():
    informe = _informe(luz_m=2.0)
    b01 = _punto(informe, "B-01")
    assert any(b.campo == "L_hidraulico_m" for b in b01.bloqueos)
    assert b01.espaciamiento is None


def test_la_fase_10_corre_aunque_el_punto_no_se_dimensione():
    """Sec. 10 no necesita el diametro: el espaciamiento no depende de la Fase 4."""
    informe = _informe(luz_m=2.0, L_hidraulico_m=180.0)
    b01 = _punto(informe, "B-01")
    assert not b01.dimensionado
    assert b01.espaciamiento is not None


# ---------------------------------------------------------------------------
# Fase 9: del proyecto, no del punto
# ---------------------------------------------------------------------------

def test_fase_9_corre_la_cadena_sismica_y_bloquea_la_geometria():
    informe = _informe(luz_m=2.0)
    cabezal = informe.cabezal
    assert cabezal.cadena is not None and cabezal.cadena.k_h > 0
    assert cabezal.cuantias, "las cuantias minimas de E.060 son [N] y salen siempre"
    claves = {b.criterio for b in cabezal.bloqueos if b.criterio}
    assert "predimensionamiento_cabezal" in claves
    assert cli.NOTA_ESTABILIDAD_CABEZAL in cabezal.notas


# ---------------------------------------------------------------------------
# Criterios pendientes que bloquearon algo
# ---------------------------------------------------------------------------

def test_los_criterios_bloqueantes_se_agrupan_con_sus_puntos():
    informe = _informe(luz_m=2.0, categoria_tr="quebrada_menor",
                       TW_m=0.0, longitud_m=12.0)
    bloqueantes = {c.clave: c for c in cli.criterios_bloqueantes(informe)}
    relleno = bloqueantes["peso_especifico_relleno_kn_m3"]
    assert set(relleno.puntos) == {"A-01", "A-02", "B-01"}
    assert relleno.etiqueta == "A"
    assert relleno.concepto and relleno.fuente
    # V5 ya no bloquea a nadie: se difiere en vez de detenerse
    assert "remanso_derecho_via" not in bloqueantes


def test_un_criterio_con_valor_no_aparece_como_bloqueante(monkeypatch):
    _declarar(monkeypatch, talud_terraplen=1.5)
    informe = _informe(luz_m=2.0, TW_m=0.0)
    claves = {c.clave for c in cli.criterios_bloqueantes(informe)}
    assert "talud_terraplen" not in claves
    # y la longitud ahora la calcula 7.B, no la declara el operador
    assert "M7.longitud_conducto" in _punto(informe, "B-01").longitud.origen


def test_el_expediente_no_cierra_mientras_haya_bloqueos():
    informe = _informe(luz_m=2.0, TW_m=0.0, longitud_m=12.0,
                       categoria_tr="quebrada_menor", L_hidraulico_m=180.0)
    assert not informe.cerrado


# ---------------------------------------------------------------------------
# Reporte de un punto dimensionado
# ---------------------------------------------------------------------------

def _resultado_hdpe(punto):
    """
    Un `ResultadoPunto` aceptado, con material y hidraulica coherentes, para
    probar la capa de reporte. HDPE porque su recubrimiento minimo es [N]
    (EG-2013 508.07/508.08) y deja correr el tamizado de 7.A sin declarar
    'h_relleno_min_concreto_tmc'.
    """
    material = catalogo(TipoMaterial.HDPE)
    hidraulica = ResultadoHidraulico(
        y_normal=0.30, y_critico=0.25, V=2.50, Q=punto.Q_m3s or 1.0,
        HW_entrada=0.50, HW_salida=0.40,
        control_gobernante=ControlGobernante.ENTRADA)
    verificaciones = (
        Verificacion(cumple=True, numeral="4.1.1.3.7 b)", valor_obtenido=0.50,
                     valor_admisible=0.75, criterio_aplicado="Y_sobre_D_max",
                     codigo="V1"),
        Verificacion(cumple=True, numeral="4.1.1.3.7 a)", valor_obtenido=2.50,
                     valor_admisible=0.60, criterio_aplicado=None, codigo="V2"),
    )
    return ResultadoPunto(punto=punto, aceptado=True, material=material,
                          D=0.60, resultado_hidraulico=hidraulica,
                          verificaciones=verificaciones)


@pytest.fixture
def informe_dimensionado(monkeypatch):
    """A-01 dimensionado, con la Fase 6 desbloqueada y la 8 aun sin tabla."""
    _declarar(monkeypatch, longitud_proteccion_salida=3.0)
    monkeypatch.setattr(cli, "disenar_punto",
                        lambda punto, **kwargs: _resultado_hdpe(punto))
    return _informe(luz_m=2.0, categoria_tr="quebrada_menor", TW_m=0.0,
                    longitud_m=12.0)


def test_reporta_material_diametro_y_control_gobernante(informe_dimensionado):
    a01 = _punto(informe_dimensionado, "A-01")
    assert a01.dimensionado
    assert a01.resultado.material.tipo is TipoMaterial.HDPE
    assert a01.resultado.D == 0.60
    assert (a01.resultado.resultado_hidraulico.control_gobernante
            is ControlGobernante.ENTRADA)


def test_toda_verificacion_reportada_lleva_numeral(informe_dimensionado):
    filas = _punto(informe_dimensionado, "A-01").verificaciones()
    assert len(filas) >= 4          # luz + V1 + V2 + G1 + G2
    assert all(v.numeral for _, v in filas)
    codigos = {v.codigo for _, v in filas if v.codigo}
    assert {"V1", "V2", "G1", "G2"} <= codigos


def test_las_fases_6_7_y_8_corren_sobre_el_punto_dimensionado(informe_dimensionado):
    a01 = _punto(informe_dimensionado, "A-01")
    assert a01.proteccion.d50 > 0
    assert a01.proteccion.advertencias, "Sec. 6 exige el aviso de filtro"
    assert a01.geometria.longitud == 12.0
    assert a01.cama_apoyo is not None


def test_la_fase_7_usa_la_misma_longitud_que_la_fase_4(informe_dimensionado):
    a01 = _punto(informe_dimensionado, "A-01")
    assert a01.geometria.longitud == a01.longitud.valor


def test_la_clase_de_producto_ya_no_bloquea_la_fase_8(informe_dimensionado):
    """
    Los items 1-2 pasaron de tope a verificacion diferida: la Fase 8 corre
    entera y 'clases_producto_por_relleno' deja de figurar como criterio que
    bloqueo una etapa. El criterio sigue vacio -- lo que cambio es como se
    reporta su ausencia, no que se haya declarado.

    Ojo: `_fase_8` todavia DESCARTA el Verificacion que devuelve
    `seleccionar_clase_calibre`, asi que el diferido no llega al informe ni
    al JSON. Ensamblarlo es trabajo del paso 7 del encargo.
    """
    claves = _claves_bloqueantes(_punto(informe_dimensionado, "A-01"))
    assert "clases_producto_por_relleno" not in claves
    assert "clases_producto_por_relleno" in ca.criterios_sin_valor()


# ---------------------------------------------------------------------------
# Volcado
# ---------------------------------------------------------------------------

def test_el_json_es_serializable_y_lleva_las_tres_listas_de_criterios(
        informe_dimensionado):
    crudo = json.dumps(cli.informe_json(informe_dimensionado),
                       ensure_ascii=False, allow_nan=False)
    datos = json.loads(crudo)
    assert datos["expediente"]["puntos"] == 4
    assert datos["expediente"]["cerrado"] is False
    assert set(datos["criterios"]) == {"usados", "sin_valor_declarados",
                                       "bloquearon"}
    a01 = next(p for p in datos["puntos"] if p["id"] == "A-01")
    assert a01["diseno"]["control_gobernante"] == "entrada"
    assert a01["diseno"]["D_m"] == 0.60
    assert all(v["numeral"] for v in a01["verificaciones"])


def test_el_texto_nombra_el_material_el_control_y_los_bloqueos():
    informe = _informe(luz_m=2.0, TW_m=0.0, longitud_m=12.0,
                       categoria_tr="quebrada_menor")
    texto = cli.volcar(informe)
    assert "CRITERIOS PENDIENTES QUE BLOQUEARON UNA ETAPA" in texto
    assert "peso_especifico_relleno_kn_m3" in texto
    assert "Expediente cerrado      : no" in texto


def test_main_escribe_el_json_y_devuelve_uno(tmp_path, capsys):
    destino = tmp_path / "informe.json"
    codigo = cli.main([str(CSV), "--luz", "2.0", "--json", str(destino)])
    capsys.readouterr()
    assert codigo == 1
    datos = json.loads(destino.read_text(encoding="utf-8"))
    assert len(datos["puntos"]) == 4
    assert datos["criterios"]["bloquearon"]


def test_main_devuelve_dos_si_el_csv_no_existe(tmp_path, capsys):
    codigo = cli.main([str(tmp_path / "no_existe.csv")])
    assert codigo == 2
    assert "No se pudo leer" in capsys.readouterr().err


def test_main_devuelve_dos_si_el_csv_no_tiene_las_columnas(tmp_path, capsys):
    ruta = tmp_path / "malo.csv"
    ruta.write_text("id,progresiva_km\nA-01,0+380\n", encoding="utf-8")
    codigo = cli.main([str(ruta)])
    assert codigo == 2
    assert "no se puede cargar" in capsys.readouterr().err


def test_un_id_declarado_que_no_esta_en_el_csv_se_avisa(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps({"globales": {"luz_m": 2.0},
                                "puntos": {"Z-99": {"luz_m": 3.0}}}),
                    encoding="utf-8")
    informe = cli.correr(CSV, cli.cargar_datos_externos(ruta, {}))
    avisos = [b for b in informe.cabezal.bloqueos if b.campo == "datos_externos"]
    assert avisos and "Z-99" in avisos[0].mensaje


def test_todos_los_puntos_del_csv_aparecen_en_el_informe():
    informe = _informe(luz_m=2.0)
    assert [i.punto.id for i in informe.puntos] == [
        p.id for p in cargar_puntos(CSV)]
