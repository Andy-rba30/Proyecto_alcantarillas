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

import csv
import json
from pathlib import Path

import pytest

import cli
import criterios_adoptados as ca
from modulos.M11_reporte import PlantillaHTML
from modelos import (CriterioPendienteError,
                     ControlGobernante, DatoInvalidoError,
                     ResultadoHidraulico, ResultadoPunto, TipoMaterial,
                     Verificacion)
from modulos.M0_carga import cargar_puntos
from modulos.M2_material import catalogo
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from modulos import M11_reporte as M11

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
    assert externos.valor("A-01", "TW_m") == pytest.approx(0.0, abs=ABS_CERO)


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
    assert externos.valor("A-01", "luz_m") == pytest.approx(4.0, rel=REL_TRANSPORTE)
    assert externos.valor("A-02", "luz_m") == pytest.approx(2.0, rel=REL_TRANSPORTE)


def test_bandera_pisa_al_global_del_archivo(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps({"globales": {"luz_m": 2.0}}), encoding="utf-8")
    externos = cli.cargar_datos_externos(ruta, {"luz_m": 5.0})
    dato = externos.dato("A-01", "luz_m")
    assert dato.valor == pytest.approx(5.0, rel=REL_TRANSPORTE)
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
    """El siguiente vacio es V5, no un insumo que falte: MD ya corrio."""
    informe = _informe(luz_m=2.0, categoria_tr="quebrada_menor",
                       TW_m=0.0, longitud_m=12.0)
    a01 = _punto(informe, "A-01")
    assert "remanso_derecho_via" in _claves_bloqueantes(a01)
    assert not a01.dimensionado


def test_la_longitud_declarada_se_registra_con_su_origen():
    informe = _informe(luz_m=2.0, TW_m=0.0, longitud_m=12.0)
    b01 = _punto(informe, "B-01")
    assert b01.longitud.valor == pytest.approx(12.0, rel=REL_TRANSPORTE)
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
    assert _punto(informe, "B-01").espaciamiento.espaciamiento_max == pytest.approx(180.0, rel=REL_TRANSPORTE)
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
    remanso = bloqueantes["remanso_derecho_via"]
    assert set(remanso.puntos) == {"A-01", "A-02", "B-01"}
    assert remanso.etiqueta == "A"
    assert remanso.concepto and remanso.fuente


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

def _resultado_hdpe(punto, S=None, **_):
    """
    Un `ResultadoPunto` aceptado, con material y hidraulica coherentes, para
    probar la capa de reporte. HDPE por costumbre de este archivo, no por
    necesidad: desde C01 los tres materiales corren el tamizado de 7.A con la
    misma tabla (AASHTO LRFD 12.6.6.3) y ninguno depende ya de un criterio de
    recubrimiento propio.
    """
    material = catalogo(TipoMaterial.HDPE)
    S = punto.exigir("S_cauce") if S is None else S
    hidraulica = ResultadoHidraulico(
        y_normal=0.30, y_critico=0.25,
        V_erosion=2.50, V_sedimentacion=1.92, Q=punto.Q_m3s or 1.0,
        # La S del diseño, resuelta como la resuelve `MD.disenar_punto`: la
        # que declare el llamador y, si no hay, `punto.exigir("S_cauce")`,
        # que lanza DatoFaltanteError cuando la columna viene vacia. Sin
        # `or` ni default: ese es justamente el defecto que MAT-D9 cierra.
        S=S,
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
                        lambda punto, **kwargs: _resultado_hdpe(punto, **kwargs))
    return _informe(luz_m=2.0, categoria_tr="quebrada_menor", TW_m=0.0,
                    longitud_m=12.0)


def test_el_cuadro_resumen_csv_lleva_el_contenido_del_punto_dimensionado(
        informe_dimensionado, tmp_path):
    """
    SIS-F-09. La rama `if informe.dimensionado:` de `M11.exportar_csv` -- la
    que ESCRIBE las celdas -- no se ejecutaba nunca: el unico test corria
    sobre una corrida sin ningun punto dimensionado y comprobaba la cabecera y
    el numero de filas, de modo que un cuadro entero de celdas vacias lo
    pasaba igual. Aqui se asserta el CONTENIDO.
    """
    destino = tmp_path / "resumen.csv"
    M11.exportar_csv(informe_dimensionado, destino)
    filas = list(csv.DictReader(destino.read_text(encoding="utf-8").splitlines()))

    por_id = {fila["id"]: fila for fila in filas}
    assert set(por_id) == {"A-01", "A-02", "B-01", "C-01"}

    a01 = por_id["A-01"]
    assert a01["familia"] == "A"
    assert a01["material"], "el material del punto dimensionado quedo vacio"
    assert a01["D_m"] == "0.60"
    assert a01["control_gobernante"] == "entrada"
    assert a01["V_erosion_ms"] and a01["V_sedimentacion_ms"]
    assert a01["V_erosion_ms"] != a01["V_sedimentacion_ms"], (
        "la doble n de Sec. 4.1.1 tiene que dar dos velocidades distintas")

    # Y el contraste que hace util al cuadro: C-01 es Familia C, no se
    # dimensiona, y sus celdas de diseño quedan vacias en vez de traer un
    # numero inventado.
    c01 = por_id["C-01"]
    assert c01["familia"] == "C"
    assert c01["material"] == ""
    assert c01["D_m"] == ""


def test_reporta_material_diametro_y_control_gobernante(informe_dimensionado):
    a01 = _punto(informe_dimensionado, "A-01")
    assert a01.dimensionado
    assert a01.resultado.material.tipo is TipoMaterial.HDPE
    assert a01.resultado.D == pytest.approx(0.60, rel=REL_TRANSPORTE)
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
    assert a01.geometria.longitud == pytest.approx(12.0, rel=REL_TRANSPORTE)
    assert a01.cama_apoyo is not None


def test_la_fase_7_usa_la_misma_longitud_que_la_fase_4(informe_dimensionado):
    a01 = _punto(informe_dimensionado, "A-01")
    assert a01.geometria.longitud == a01.longitud.valor


def test_la_clase_de_producto_sigue_bloqueada(informe_dimensionado):
    claves = _claves_bloqueantes(_punto(informe_dimensionado, "A-01"))
    assert "clases_producto_por_relleno" in claves


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
    # Seis listas desde la correccion de C08: a las tres originales se
    # sumaron `declarados_en_caliente` (SIS-A-01: un valor que gobierna el
    # calculo y no esta en el archivo), `verificacion_pendiente` (SIS-D-07:
    # el hermano de `trazabilidad_incompleta` de los datos de sitio) y
    # `sin_consumidor` (SIS-B-15/B-19).
    assert set(datos["criterios"]) == {
        "usados", "sin_valor_declarados", "bloquearon",
        "declarados_en_caliente", "verificacion_pendiente", "sin_consumidor"}
    # Cada criterio usado dice de donde salio su valor, no solo cual es.
    assert all("declarado_en_caliente" in c for c in datos["criterios"]["usados"])
    a01 = next(p for p in datos["puntos"] if p["id"] == "A-01")
    assert a01["diseno"]["control_gobernante"] == "entrada"
    assert a01["diseno"]["D_m"] == pytest.approx(0.60, rel=REL_TRANSPORTE)
    assert all(v["numeral"] for v in a01["verificaciones"])


def test_el_volcado_no_revienta_con_un_criterio_aplicado_desconocido(
        informe_dimensionado):
    """
    `_resultado_hdpe` aplica el umbral "Y_sobre_D_max", que NO es clave de
    CRITERIOS. El acceso directo `ca.criterio(...)` lanzaba KeyError y se caia
    el volcado entero del expediente por un desajuste de nombre en la capa de
    reporte. La consulta tolerante imprime la clave tal cual, sin etiqueta.
    """
    assert "Y_sobre_D_max" not in ca.CRITERIOS
    texto = cli.volcar(informe_dimensionado)
    assert "umbral del criterio 'Y_sobre_D_max'" in texto
    # Sin etiqueta inventada: la linea termina en la clave, no en "[algo]".
    linea = next(l for l in texto.splitlines() if "Y_sobre_D_max" in l)
    assert linea.rstrip().endswith("'Y_sobre_D_max'")


def test_el_texto_nombra_el_material_el_control_y_los_bloqueos():
    informe = _informe(luz_m=2.0, TW_m=0.0, longitud_m=12.0,
                       categoria_tr="quebrada_menor")
    texto = cli.volcar(informe)
    assert "CRITERIOS PENDIENTES QUE BLOQUEARON UNA ETAPA" in texto
    assert "remanso_derecho_via" in texto
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


# ---------------------------------------------------------------------------
# Alcance de la corrida: bifurcacion perfil / expediente
# ---------------------------------------------------------------------------
#
# La bandera --alcance separa dos corridas del MISMO pipeline: "expediente"
# (defecto) lo corre entero, como siempre; "perfil" difiere V5, V8, la Fase 8
# y la Fase 9 al expediente, dejando constancia con fundamento. Nada se borra:
# lo diferido deja de contar solo para `Informe.cerrado`.
#
# Los criterios que aqui se declaran con `_declarar` son los que una corrida
# de perfil real necesita cerrados (los detecto la propia corrida): el peso
# especifico del relleno (V7 es obligatoria tambien en perfil), las
# velocidades maximas de TMC/HDPE (V3) y la longitud de proteccion (Fase 6).
# Son valores de PRUEBA via monkeypatch, el patron de todo este archivo: no
# tocan criterios_adoptados.py.

CRITERIOS_CORRIDA_PERFIL = dict(
    peso_especifico_relleno_kn_m3=18.0,
    v_max_tmc=4.5,
    v_max_hdpe=6.0,
    longitud_proteccion_salida=3.0,
)

EXTERNOS_PERFIL = dict(luz_m=2.0, categoria_tr="quebrada_menor", TW_m=0.0,
                       longitud_m=12.0, L_hidraulico_m=180.0)


def _informe_alcance(alcance, **globales):
    return cli.correr(CSV, _externos(**globales), alcance=alcance)


def test_el_alcance_por_defecto_es_expediente():
    """Quien no pasa la bandera corre exactamente lo de siempre."""
    assert cli._parser().parse_args(["x.csv"]).alcance == cli.ALCANCE_EXPEDIENTE
    informe = _informe(luz_m=2.0)
    assert informe.alcance == cli.ALCANCE_EXPEDIENTE
    assert informe.diferidos() == ()


def test_alcance_expediente_es_identico_al_comportamiento_actual():
    """El mismo CSV con y sin la bandera produce el mismo informe JSON."""
    con = cli.informe_json(_informe_alcance(cli.ALCANCE_EXPEDIENTE,
                                            **EXTERNOS_PERFIL))
    sin = cli.informe_json(cli.correr(CSV, _externos(**EXTERNOS_PERFIL)))
    for datos in (con, sin):
        datos["expediente"].pop("generado_utc")
    assert con == sin


def test_perfil_dimensiona_puntos_que_expediente_bloquea(monkeypatch):
    """
    El corazon de la bifurcacion: con los mismos datos, V5 (remanso) detiene
    el bucle de MD en alcance expediente, y en alcance perfil se difiere y el
    punto se dimensiona. El diferido queda registrado con clave, concepto y
    fuente -- la constancia, no un descarte silencioso.
    """
    _declarar(monkeypatch, **CRITERIOS_CORRIDA_PERFIL)

    expediente = _informe_alcance(cli.ALCANCE_EXPEDIENTE, **EXTERNOS_PERFIL)
    assert expediente.dimensionados == 0

    perfil = _informe_alcance(cli.ALCANCE_PERFIL, **EXTERNOS_PERFIL)
    assert perfil.dimensionados == 3      # A-01, A-02, B-01; C-01 es Familia C
    a01 = _punto(perfil, "A-01")
    assert a01.resultado.material.tipo is TipoMaterial.CONCRETO_REFORZADO

    diferidos = [b for b in a01.bloqueos if b.diferido_por_alcance]
    v5 = next(b for b in diferidos if b.criterio == "remanso_derecho_via")
    assert v5.tipo == "CriterioPendienteError"
    assert v5.concepto and v5.fuente
    assert "V5" in v5.etapa
    v8 = next(b for b in diferidos if b.criterio == "TR_evento_extremo")
    assert "V8" in v8.etapa


def test_perfil_intenta_v5_y_v8_pero_no_las_exige(monkeypatch):
    """
    Las OCHO obligatorias estan en la tabla del punto; V5 y V8 no.

    Eran siete hasta S14, cuando V4b se cableo: su umbral es un criterio con
    valor y no depende de ningun dato de expediente, de modo que al alcance
    de perfil corre como cualquier otra obligatoria.
    """
    _declarar(monkeypatch, **CRITERIOS_CORRIDA_PERFIL)
    perfil = _informe_alcance(cli.ALCANCE_PERFIL, **EXTERNOS_PERFIL)
    codigos = [v.codigo for _, v in _punto(perfil, "A-01").verificaciones()
               if v.codigo and v.codigo.startswith("V")]
    assert codigos == ["V1", "V2", "V3", "V4", "V4b", "V6", "V7", "V9"]


def test_perfil_no_ejecuta_fase_8_ni_cabezal(monkeypatch):
    """
    2.b: ni `_fase_8` ni `correr_cabezal` corren en perfil. El espia sobre
    `seleccionar_clase_calibre` documenta ademas la MINA de M8: esa funcion
    es una guarda deliberada (AssertionError en cuanto
    'clases_producto_por_relleno' tenga valor, porque la tabla no esta
    transcrita) y en alcance perfil NUNCA se alcanza. Que este test siga
    exigiendo "cero llamadas" es lo que mantiene visible que, antes de
    declarar ese criterio, hay que escribir el cuerpo de la funcion.
    """
    _declarar(monkeypatch, **CRITERIOS_CORRIDA_PERFIL)
    llamadas = []
    monkeypatch.setattr(cli, "seleccionar_clase_calibre",
                        lambda **kw: llamadas.append(kw))
    monkeypatch.setattr(cli, "cadena_sismica",
                        lambda: llamadas.append("cabezal"))

    perfil = _informe_alcance(cli.ALCANCE_PERFIL, **EXTERNOS_PERFIL)
    assert llamadas == []
    assert perfil.cabezal.cadena is None
    fases_8 = [b for i in perfil.puntos for b in i.bloqueos
               if b.fase == cli.FASE_ESTRUCTURAL]
    assert fases_8 and all(b.diferido_por_alcance for b in fases_8)
    assert all(b.diferido_por_alcance for b in perfil.cabezal.bloqueos)

    # En expediente, la Fase 8 y el cabezal SI corren.
    llamadas.clear()
    _informe_alcance(cli.ALCANCE_EXPEDIENTE, **EXTERNOS_PERFIL)
    assert "cabezal" in llamadas


def test_la_mina_de_v8_sigue_armada_en_perfil(monkeypatch):
    """
    MINA de M5 (no desactivar): `v8_evento_extremo` termina en
    AssertionError en cuanto 'TR_evento_extremo' tenga valor -- el criterio
    tendria dato pero la logica de V8 no esta escrita. El verificador de
    perfil captura SOLO ErrorProyecto, asi que esa AssertionError propaga y
    tumba la corrida con su traza en vez de quedar "diferida": un modulo
    incompleto no es un asunto de alcance. Antes de declarar ese criterio
    hay que escribir el cuerpo de la funcion.
    """
    _declarar(monkeypatch, TR_evento_extremo=100.0, **CRITERIOS_CORRIDA_PERFIL)
    with pytest.raises(AssertionError, match="TR_evento_extremo"):
        _informe_alcance(cli.ALCANCE_PERFIL, **EXTERNOS_PERFIL)


def test_perfil_deja_constancia_en_texto_y_json(monkeypatch):
    """2.d: el alcance usado y lo diferido, con fundamento, en ambas salidas."""
    _declarar(monkeypatch, **CRITERIOS_CORRIDA_PERFIL)
    perfil = _informe_alcance(cli.ALCANCE_PERFIL, **EXTERNOS_PERFIL)

    datos = json.loads(json.dumps(cli.informe_json(perfil),
                                  ensure_ascii=False, allow_nan=False))
    assert datos["alcance"]["nivel"] == "perfil"
    claves = {d["criterio"] for d in datos["alcance"]["diferidos"]}
    assert "remanso_derecho_via" in claves and "TR_evento_extremo" in claves
    remanso = next(d for d in datos["alcance"]["diferidos"]
                   if d["criterio"] == "remanso_derecho_via")
    assert remanso["fuente"] and remanso["punto"] == "A-01"
    fases = {d["fase"] for d in datos["alcance"]["diferidos"]}
    assert cli.FASE_ESTRUCTURAL in fases and cli.FASE_CABEZAL in fases

    texto = cli.volcar(perfil)
    assert "ALCANCE DE LA CORRIDA" in texto
    assert "Alcance declarado: perfil" in texto
    assert "remanso_derecho_via" in texto
    assert "Fase 8 completa diferida" in texto
    assert "Fase 9 completa diferida" in texto


def test_expediente_tambien_declara_su_alcance():
    informe = _informe(luz_m=2.0)
    assert cli.informe_json(informe)["alcance"] == {
        "nivel": "expediente", "diferidos": []}
    assert "Alcance declarado: expediente" in cli.volcar(informe)


def test_perfil_cerrado_devuelve_exit_cero(tmp_path, monkeypatch, capsys):
    """
    2.c: un expediente de perfil con todos sus puntos dimensionados y sin
    bloqueos REALES cierra y main devuelve 0; los diferidos por alcance no
    cuentan. Se usa B-01 solo, que cierra en concreto a V = 1.96 m/s.

    Esa velocidad es justamente la que la correccion de V3 legitimo: mientras
    V3 leia el par de la Tabla N 10 como piso y techo, 1.96 m/s se rechazaba
    por "bajo el minimo" y el concreto se descartaba en todo su catalogo. El
    piso real lo pone V2 (0.25 m/s) y esta velocidad lo cumple de sobra.

    Ya no declara 'h_relleno_min_concreto_tmc': ese criterio se retiro en C01
    y la Fase 7 no lo pide. Los dos criterios que hoy podrian bloquearla --
    'espesor_pared_conducto' y 'condicion_pavimento' -- los declara conftest
    para toda la corrida de pruebas.
    """
    _declarar(monkeypatch, **CRITERIOS_CORRIDA_PERFIL)
    lineas = CSV.read_text(encoding="utf-8").strip().splitlines()
    solo_b01 = tmp_path / "solo_b01.csv"
    solo_b01.write_text("\n".join([lineas[0]] + [
        l for l in lineas if l.startswith("B-01")]) + "\n", encoding="utf-8")
    argumentos = [str(solo_b01), "--luz", "2.0", "--tw", "0.0",
                  "--longitud", "12.0", "--l-hidraulico", "180.0",
                  "--json", str(tmp_path / "b01.json")]

    assert cli.main(argumentos + ["--alcance", "perfil"]) == 0
    salida = capsys.readouterr().out
    assert "Expediente cerrado      : si" in salida
    assert "Alcance de la corrida   : perfil" in salida

    # El MISMO expediente en alcance completo NO cierra: V5 sigue exigiendose.
    assert cli.main(argumentos + ["--alcance", "expediente"]) == 1
    capsys.readouterr()


# ---------------------------------------------------------------------------
# Seleccion de plantilla de la memoria (M11)
# ---------------------------------------------------------------------------

def test_el_alcance_elige_la_plantilla_por_defecto():
    perfil = cli.plantilla_por_alcance(cli.ALCANCE_PERFIL)
    expediente = cli.plantilla_por_alcance(cli.ALCANCE_EXPEDIENTE)
    assert perfil.name == cli.NOMBRE_PLANTILLA_PERFIL
    assert expediente.name == cli.NOMBRE_PLANTILLA
    assert perfil.is_file() and expediente.is_file()


def test_la_plantilla_forzada_gana_sobre_el_alcance(tmp_path):
    """Las dos comparten contrato: cualquiera vale para cualquier corrida."""
    forzada = tmp_path / "otra.html"
    for alcance in (cli.ALCANCE_PERFIL, cli.ALCANCE_EXPEDIENTE):
        assert cli.plantilla_por_alcance(alcance, forzada) == forzada
    assert cli._parser().parse_args(["x.csv"]).plantilla is None


def test_la_memoria_de_perfil_sale_con_la_plantilla_de_perfil(
        tmp_path, monkeypatch):
    """De punta a punta: --alcance perfil --html usa memoria_perfil.html."""
    _declarar(monkeypatch, **CRITERIOS_CORRIDA_PERFIL)
    destino = tmp_path / "memoria.html"
    codigo = cli.main([str(CSV), "--alcance", "perfil",
                       "--luz", "2.0", "--tw", "0.0", "--longitud", "12.0",
                       "--categoria-tr", "quebrada_menor",
                       "--l-hidraulico", "180.0",
                       "--json", str(tmp_path / "i.json"),
                       "--html", str(destino)])
    assert codigo == 1          # C-01 sigue sin Q: el expediente no cierra
    html = destino.read_text(encoding="utf-8")
    assert "nivel de perfil" in html
    assert "4. Alcance y diferimientos declarados" in html
    assert "remanso_derecho_via" in html
    # El volcado de Tableros 1-2-3 NO esta: es lo que la plantilla reemplaza.
    assert "Pendientes &mdash; Tableros 1, 2 y 3" not in html
    assert PlantillaHTML.delimiter not in html


def test_la_memoria_de_expediente_conserva_el_volcado_de_tableros(tmp_path):
    destino = tmp_path / "memoria.html"
    cli.main([str(CSV), "--luz", "2.0",
              "--json", str(tmp_path / "i.json"), "--html", str(destino)])
    html = destino.read_text(encoding="utf-8")
    assert "Pendientes &mdash; Tableros 1, 2 y 3" in html
    assert "0.1 Alcance de la corrida" in html
    assert "Ninguna etapa quedo diferida por alcance" in html


# ---------------------------------------------------------------------------
# --declarar: la via de declaracion en caliente desde la linea de comandos
# ---------------------------------------------------------------------------
# Es el mismo camino que usa la GUI (`establecer_valor_dinamico`), no un
# segundo mecanismo: pasa por la guardia del archivo y la memoria imprime el
# valor con su procedencia (SIS-A-01).

def test_declarar_pasa_por_la_guardia_del_archivo():
    try:
        with pytest.raises(ValueError, match="fuera del rango"):
            cli.declarar_criterios(["v_max_concreto_eleccion=99.0"])
        assert "v_max_concreto_eleccion" not in ca.valores_dinamicos()

        cli.declarar_criterios(["v_max_concreto_eleccion=4.0"])
        assert ca.valores_dinamicos()["v_max_concreto_eleccion"] == pytest.approx(4.0)
    finally:
        ca.quitar_valor_dinamico("v_max_concreto_eleccion")


# ---------------------------------------------------------------------------
# SIS-F-11 - las seis banderas del CLI que no ejercitaba nadie
# ---------------------------------------------------------------------------
# --criterios, --csv-resumen, --datos-externos, --pdf, --plantilla y --proyecto
# estaban definidas en el parser y ningun test las pasaba por `main`: el
# cableado bandera -> funcion no se ejercitaba, de modo que un `dest` mal
# escrito o una llamada cambiada de sitio dejaban la suite en verde. Cada test
# de aqui asserta el EFECTO de la bandera, no solo que no revienta.

def test_bandera_criterios_anade_el_bloque_de_declaracion(tmp_path, capsys):
    base = cli.main([str(CSV), "--luz", "2.0", "--json", str(tmp_path / "a.json")])
    sin = capsys.readouterr().out
    con_bandera = cli.main([str(CSV), "--luz", "2.0", "--criterios",
                            "--json", str(tmp_path / "b.json")])
    con = capsys.readouterr().out
    assert base == con_bandera
    assert len(con) > len(sin), "--criterios no anadio nada al volcado"
    assert "DATOS DE SITIO" in con.upper()
    assert "DATOS DE SITIO" not in sin.upper()


def test_bandera_csv_resumen_escribe_el_entregable_3(tmp_path, capsys):
    destino = tmp_path / "resumen.csv"
    cli.main([str(CSV), "--luz", "2.0", "--json", str(tmp_path / "a.json"),
              "--csv-resumen", str(destino)])
    salida = capsys.readouterr().out
    assert destino.is_file(), "--csv-resumen no escribio el archivo"
    assert str(destino) in salida, "el volcado no dice donde quedo el CSV"
    lineas = destino.read_text(encoding="utf-8").strip().splitlines()
    assert lineas[0] == ",".join(M11.COLUMNAS_RESUMEN_CSV)
    assert len(lineas) == 1 + 4, "una fila por punto critico del ejemplo"


def test_bandera_datos_externos_entra_por_main(tmp_path, capsys):
    """La bandera y el archivo son el mismo camino: `main` los combina."""
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps({"globales": {"luz_m": 2.0}}),
                    encoding="utf-8")
    codigo = cli.main([str(CSV), "--datos-externos", str(ruta),
                       "--json", str(tmp_path / "a.json")])
    capsys.readouterr()
    assert codigo == 1, "sin luz no se clasifica ningun punto: la bandera no llego"


def test_bandera_proyecto_encabeza_la_memoria(tmp_path, capsys):
    destino = tmp_path / "memoria.html"
    cli.main([str(CSV), "--luz", "2.0", "--json", str(tmp_path / "a.json"),
              "--html", str(destino), "--proyecto", "Via de Evitamiento X"])
    capsys.readouterr()
    assert "Via de Evitamiento X" in destino.read_text(encoding="utf-8")


def test_bandera_plantilla_fuerza_la_plantilla_de_la_memoria(tmp_path, capsys):
    """
    La plantilla forzada gana al defecto del alcance: es lo que declara
    `plantilla_por_alcance`, y hasta ahora nadie lo ejercitaba por `main`.
    """
    forzada = cli.DIR_PLANTILLAS / cli.NOMBRE_PLANTILLA_PERFIL
    destino = tmp_path / "memoria.html"
    cli.main([str(CSV), "--luz", "2.0", "--json", str(tmp_path / "a.json"),
              "--alcance", "expediente", "--plantilla", str(forzada),
              "--html", str(destino)])
    salida = capsys.readouterr().out
    assert forzada.name in salida, (
        "el volcado tiene que decir que plantilla se uso, y ser la forzada")
    assert destino.is_file()


def test_bandera_pdf_escribe_o_deja_el_html_con_su_mensaje(tmp_path, capsys):
    """
    --pdf tiene dos finales declarados: con weasyprint escribe el PDF; sin el,
    deja el HTML y lo dice. El test acepta los dos y comprueba que el mensaje
    corresponde al que ocurrio, que es lo que la bandera promete.
    """
    destino = tmp_path / "memoria.pdf"
    cli.main([str(CSV), "--luz", "2.0", "--json", str(tmp_path / "a.json"),
              "--pdf", str(destino)])
    salida = capsys.readouterr().out
    if destino.is_file():
        assert destino.stat().st_size > 0
        assert str(destino) in salida
    else:
        alternativo = destino.with_suffix(".html")
        assert alternativo.is_file(), (
            "sin weasyprint la bandera tiene que dejar el HTML en su lugar")
        assert "html" in salida.lower()


def test_declarar_no_deja_entrar_un_infinito_por_la_notacion_cientifica():
    """
    `ast.literal_eval("1e999")` devuelve inf sin error, de modo que --declarar
    era una puerta abierta al pipeline para un numero que no existe. El
    criterio elegido no declara rango de sensibilidad: es el que quedaba sin
    defensa (MAT-D14 / criterio de salida de S16).
    """
    try:
        with pytest.raises(ValueError, match="infinito, con NaN"):
            cli.declarar_criterios(["talud_terraplen=1e999"])
        assert "talud_terraplen" not in ca.valores_dinamicos()
    finally:
        ca.quitar_valor_dinamico("talud_terraplen")


@pytest.mark.parametrize("texto", ["nan", "NaN", "inf", "-inf", "Infinity"])
def test_declarar_no_deja_entrar_un_no_numero_disfrazado_de_texto(texto):
    """
    LA PUERTA QUE QUEDABA ABIERTA. 'nan' e 'inf' no son literales de Python:
    son NOMBRES. `ast.literal_eval` los rechaza y caian al respaldo a CADENA,
    por debajo de la guardia de finitud de criterios_adoptados -- que solo
    recorre numeros. Y la cadena no se quedaba quieta: el primer consumidor
    que hiciera `float()` sobre el criterio la devolvia al calculo convertida
    en el mismo NaN que se acababa de rechazar, y la memoria salia con
    `cuantia_adoptada = nan` y un gobernante declarado. Ese es exactamente el
    "diagnostico falso" que el criterio de salida de esta sesion prohibe.

    El respaldo a texto sigue existiendo, y debe: los criterios CATEGORICOS
    ('cota_terreno', 'flexible', 'A') entran por ahi.
    """
    try:
        with pytest.raises(ValueError, match="no es un numero declarable"):
            cli.declarar_criterios([f"talud_terraplen={texto}"])
        assert "talud_terraplen" not in ca.valores_dinamicos()
    finally:
        ca.quitar_valor_dinamico("talud_terraplen")


def test_declarar_no_revienta_con_un_entero_que_no_cabe_en_un_double():
    """
    Un `int` de Python no tiene tope. Uno de 401 cifras no cabe en un double y
    `float(x)` lanza OverflowError, que no es ValueError ni KeyError y que
    `cli.main` no atrapa: la corrida moriria con traza en vez de con el
    mensaje del expediente. Entra por la misma puerta que el infinito.
    """
    enorme = "1" + "0" * 400
    try:
        with pytest.raises(ValueError, match="doble precision"):
            cli.declarar_criterios([f"talud_terraplen={enorme}"])
        assert "talud_terraplen" not in ca.valores_dinamicos()
    finally:
        ca.quitar_valor_dinamico("talud_terraplen")


def test_declarar_sigue_admitiendo_un_criterio_categorico():
    """El otro lado: el respaldo a texto existe para estos y no puede caer."""
    try:
        cli.declarar_criterios(["origen_cota_fondo_entrada=cota_terreno"])
        assert ca.valores_dinamicos()["origen_cota_fondo_entrada"] == "cota_terreno"
    finally:
        ca.establecer_valor_dinamico("origen_cota_fondo_entrada", "cota_terreno")


def test_declarar_admite_texto_y_exige_la_forma_clave_igual_valor():
    try:
        cli.declarar_criterios(["origen_cota_fondo_entrada=cota_terreno"])
        assert ca.valores_dinamicos()["origen_cota_fondo_entrada"] == "cota_terreno"

        with pytest.raises(ValueError, match="CLAVE=VALOR"):
            cli.declarar_criterios(["origen_cota_fondo_entrada"])
        with pytest.raises(KeyError):
            cli.declarar_criterios(["criterio_que_no_existe=1.0"])
    finally:
        ca.establecer_valor_dinamico("origen_cota_fondo_entrada", "cota_terreno")


def test_la_memoria_declara_el_criterio_dado_en_caliente_con_su_procedencia(tmp_path):
    """
    El criterio de salida de esta correccion, extremo a extremo: se corre la
    CLI declarando un criterio en caliente y el HTML tiene que traerlo con su
    valor efectivo Y con la marca de que se declaro para la corrida.
    """
    destino = tmp_path / "memoria.html"
    try:
        cli.main([str(CSV), "--luz", "2.0", "--declarar", "TW_receptor=1.2",
                  "--json", str(tmp_path / "i.json"), "--html", str(destino)])
        html = destino.read_text(encoding="utf-8")

        assert "TW_receptor" in html
        ficha = html.split("<code>TW_receptor</code>")[1].split("</dl>")[0]
        assert "1.2" in ficha
        assert "sin valor declarado" not in ficha
        assert "DECLARADO PARA ESTA CORRIDA" in ficha
        assert "Criterios declarados solo para esta corrida" in html
    finally:
        ca.quitar_valor_dinamico("TW_receptor")


def test_el_json_lleva_el_valor_efectivo_y_la_procedencia(tmp_path):
    salida = tmp_path / "i.json"
    try:
        cli.main([str(CSV), "--luz", "2.0", "--declarar", "TW_receptor=1.2",
                  "--json", str(salida)])
        datos = json.loads(salida.read_text(encoding="utf-8"))
        usados = {c["clave"]: c for c in datos["criterios"]["usados"]}

        assert usados["TW_receptor"]["valor"] == pytest.approx(1.2)
        assert usados["TW_receptor"]["declarado_en_caliente"] is True
        assert "TW_receptor" in datos["criterios"]["declarados_en_caliente"]
        assert datos["criterios"]["verificacion_pendiente"]
    finally:
        ca.quitar_valor_dinamico("TW_receptor")


def test_un_dato_de_sitio_pendiente_sale_como_bloqueo_y_no_como_KeyError(monkeypatch):
    """
    SIS-A-05. `cli._bloqueo` resolvia TODA clave con `ca.criterio()`, y
    `CriterioPendienteError` no la levanta solo criterios_adoptados: la misma
    excepcion sale de `datos_sitio.valor` cuando un [S] de corredor todavia no
    se ha leido. Con un [S] pendiente la corrida moria con KeyError -- un
    fallo de PROGRAMA dentro de la funcion que existe para convertir un
    problema del expediente en una fila del informe.

    Hoy los tres datos de corredor tienen valor, de modo que el camino es
    inalcanzable desde el expediente; se provoca vaciando uno, que es el
    estado que el proyecto admite y para el que existe el mecanismo.
    """
    import datos_sitio as ds
    from dataclasses import replace

    clave = "PGA_roca_B"
    monkeypatch.setitem(ds.DATOS_SITIO, clave,
                        replace(ds.DATOS_SITIO[clave], valor=None))

    with pytest.raises(CriterioPendienteError) as exc:
        ds.valor(clave)

    bloqueo = cli._bloqueo("Fase 9", "cadena sismica", exc.value)

    assert bloqueo.tipo == "CriterioPendienteError"
    assert bloqueo.criterio == clave
    assert bloqueo.etiqueta == "S", (
        "la etiqueta tiene que ser la del dato de sitio, no la de un criterio")
    assert bloqueo.concepto and bloqueo.fuente
    assert bloqueo.fuente == ds.dato(clave).fuente, (
        "el informe tiene que citar la fuente del DATO DE SITIO, que es el "
        "mapa del que se lee, y no la de un criterio que no existe")


def test_el_resolvedor_comun_encuentra_las_dos_familias_y_nombra_la_que_falta():
    """La otra mitad del contrato de `ca.declaracion_de`."""
    import datos_sitio as ds

    assert ca.declaracion_de("talud_terraplen").etiqueta == "A"
    assert ca.declaracion_de("PGA_roca_B").etiqueta == "S"
    assert ca.declaracion_de("PGA_roca_B") is ds.dato("PGA_roca_B")
    with pytest.raises(KeyError, match="ni en datos_sitio.py"):
        ca.declaracion_de("clave_que_no_existe_en_ninguno")


# ---------------------------------------------------------------------------
# Las guardas de los datos externos que ninguna prueba alcanzaba (SIS-F-10)
# ---------------------------------------------------------------------------
# SIS-F-10 conto trece `raise` de la taxonomia sin cobertura; medida de nuevo
# sobre el arbol de S16 la cuenta es 51, y cuatro de ellas son de este archivo:
# los dos rechazos de `_numero_externo` y los dos de `cargar_datos_externos`.
# Que no las alcanzara nadie es exactamente la forma del cluster C09: la suite
# estaba verde y no habria detectado que cualquiera de las cuatro se borrara.
#
# Cada caso asserta las TRES cosas: la clase de la excepcion, el `campo` que
# lleva -- que es lo que la GUI usa para senalar el dato -- y un trozo del
# motivo que diga POR QUE, no solo que fallo. Un mensaje que dijera "dato
# invalido" a secas pasaria la primera y la segunda y no la tercera.

# (bruto, trozo del motivo). El motivo tiene que nombrar el sistema de
# unidades: el dato entra en SI y el error no puede limitarse a "no es un
# numero" sin decir en que se esperaba.
NO_SON_NUMEROS = [
    ("dos", "no es un numero"),
    ("", "no es un numero"),
    ([2.0], "no es un numero"),
    ({"valor": 2.0}, "no es un numero"),
]


@pytest.mark.parametrize("bruto, motivo", NO_SON_NUMEROS)
def test_un_dato_externo_que_no_es_numero_dice_que_se_esperaba(bruto, motivo):
    """
    Falla si `_numero_externo` deja de convertir el bruto -- o si atrapa el
    fallo de `float()` con un default silencioso en vez de detenerse.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        _externos(luz_m=bruto)
    assert exc.value.campo == "luz_m"
    assert motivo in exc.value.motivo
    assert "SI, metros o m3/s" in exc.value.motivo
    assert "linea de comandos" in exc.value.motivo


@pytest.mark.parametrize("bruto", [float("inf"), float("-inf"), float("nan")])
def test_un_dato_externo_no_finito_no_entra_al_pipeline(bruto):
    """
    Falla si desaparece la comprobacion de finitud: un inf o un nan pasan
    `float()` sin protestar y despues salen del pipeline como diagnostico
    falso, que es lo que el criterio de salida de S16 cierra. Es el gemelo,
    por la via de los datos externos, de lo que
    `test_declarar_no_deja_entrar_un_infinito_por_la_notacion_cientifica`
    cierra por la via de --declarar.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        _externos(longitud_m=bruto)
    assert exc.value.campo == "longitud_m"
    assert "no es finito" in exc.value.motivo


@pytest.mark.parametrize("crudo", [
    [{"globales": {"luz_m": 2.0}}],      # una lista de objetos
    2.0,                                 # un numero suelto
    "globales",                          # el nombre de la seccion, no la seccion
])
def test_el_json_de_datos_externos_tiene_que_ser_un_objeto(tmp_path, crudo):
    """
    Falla si `cargar_datos_externos` deja de comprobar la forma del JSON: un
    archivo que no es un objeto se recorreria con `.get` y reventaria con un
    AttributeError -- un fallo del programa -- en vez de con el error del
    expediente que la GUI sabe mostrar.
    """
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps(crudo), encoding="utf-8")
    with pytest.raises(DatoInvalidoError) as exc:
        cli.cargar_datos_externos(ruta, {})
    assert exc.value.campo == "datos_externos"
    assert "tiene que ser un objeto JSON" in exc.value.motivo
    assert "datos.json" in exc.value.motivo
    assert exc.value.valor == type(crudo).__name__


def test_un_punto_que_no_lleva_su_objeto_de_datos_se_rechaza_con_su_id(tmp_path):
    """
    Falla si se acepta `{"puntos": {"A-01": 2.0}}` -- la forma en que alguien
    escribe el dato de un punto olvidando la clave. Sin la guarda, el bucle
    siguiente iteraria sobre el float y el punto se quedaria sin ningun dato
    declarado en silencio. El id tiene que viajar en la excepcion: es lo unico
    que dice CUAL de los puntos esta mal escrito.
    """
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps({"puntos": {"A-01": 2.0}}), encoding="utf-8")
    with pytest.raises(DatoInvalidoError) as exc:
        cli.cargar_datos_externos(ruta, {})
    assert exc.value.campo == "datos_externos"
    assert exc.value.valor == "A-01"
    assert "cada punto lleva un objeto" in exc.value.motivo


# --- La otra guarda de --declarar, que tampoco alcanzaba nadie -------------

def test_declarar_sin_valor_no_declara_la_cadena_vacia():
    """
    `ast.literal_eval("")` lanza SyntaxError, el texto cae al respaldo de
    cadena y `--declarar clave=` declararia la CADENA VACIA: un valor que
    nadie quiso declarar entrando por la puerta de una errata, y ademas por
    el camino que CLAUDE.md senala como el peor error del proyecto -- un
    vacio relleno en silencio.

    Falla si se pierde la comprobacion del texto vacio. Es la hermana de
    `test_declarar_no_deja_entrar_un_infinito_por_la_notacion_cientifica`:
    las dos cierran la misma puerta, una por el valor imposible y la otra
    por el valor ausente.
    """
    try:
        with pytest.raises(ValueError, match="no trae valor"):
            cli.declarar_criterios(["origen_cota_fondo_entrada="])
        assert ca.valores_dinamicos()["origen_cota_fondo_entrada"] != ""
    finally:
        ca.establecer_valor_dinamico("origen_cota_fondo_entrada", "cota_terreno")


def test_una_declaracion_mal_escrita_devuelve_dos_y_no_corre_el_pipeline(
        tmp_path, capsys):
    """
    El error de una declaracion no puede salir como traza de Python: `main`
    lo atrapa, lo escribe en stderr y devuelve 2, igual que hace con el CSV
    que no existe. Falla si el except desaparece -- la CLI reventaria con la
    excepcion cruda -- o si el codigo de salida pasa a ser 0, que un guion
    que encadene corridas leeria como exito.
    """
    salida_json = tmp_path / "i.json"
    assert cli.main([str(CSV), "--declarar", "origen_cota_fondo_entrada=",
                     "--json", str(salida_json)]) == 2
    err = capsys.readouterr().err
    assert "No se pudo declarar el criterio" in err
    assert "no trae valor" in err
    assert not salida_json.exists(), "no debe correr el pipeline"
