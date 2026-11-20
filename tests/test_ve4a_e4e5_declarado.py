"""
tests/test_ve4a_e4e5_declarado.py
=================================
VE-4a: E4 y E5 (estabilidad global del muro y del talud del cabezal) como
RESULTADO DECLARADO del EMS o del analisis externo (ficha T7B-07, decision
del dueño).

El programa NO calcula E4 ni E5: el proyectista declara, por punto y por
cabezal, el factor de seguridad que le entrega el geotecnista
(`estabilidad_global_declarada` de `--datos-externos`, con el documento, la
fecha y el metodo), y el ensamble lo CONTRASTA en los dos marcos que no se
cruzan:

    ASD   FS_declarado >= FS de E.050 (39.13.6 b para E4, Art. 30.3 para
          E5), aplicada por analogia [N→]: 1.50 / 1.25.
    LRFD  FS_declarado >= 1/phi, con phi de AASHTO 11.6.3.7 en la condicion
          estatica (0.75 o 0.65 segun el EMS: la fila es el criterio [A]
          'fila_phi_estabilidad_global', sin valor) y de 11.5.8 bajo sismo
          (0.9); el puente FS = 1/phi es el comentario C11.6.3.7.

Sin el dato declarado nada cambia: E4 y E5 siguen «diferidas al expediente
con el EMS», con su paso F9.GLOBAL y su aviso.
"""

import json
from dataclasses import replace

import pytest

import cli
from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src import servicio
from src.modelos import (CondicionAnalisis, DatoInvalidoError,
                         MARCO_RIGE_ASD, TipoDeVeredicto)
from src.modulos import M9_cabezal as M9
from src.normativa.registro import construir
from tests.apoyo.aproximacion import ABS_CERO
from tests.test_t7b_cabezal_estabilidad import (  # noqa: F401  (fixture)
    _correr_de_prueba, _externos, tanteo)

EST = CondicionAnalisis.ESTATICO
SIS = CondicionAnalisis.SISMICO

# DE PRUEBA: ningun factor de seguridad de este archivo es del proyecto.
TRAZA = {"documento": "EMS de prueba, anexo de estabilidad (no es del "
                      "proyecto)",
         "fecha": "2026-11-20", "metodo": "Spencer",
         "programa": "programa de equilibrio limite de prueba"}
FS_AMBOS = {"E4": {"estatico": 1.80, "sismico": 1.40},
            "E5": {"estatico": 1.70, "sismico": 1.35}}


def _declarado(**por_extremo):
    """El bloque de UN extremo, ya normalizado como lo deja la puerta."""
    bloque = dict(TRAZA)
    bloque.update(por_extremo)
    return bloque


def _filas(e):
    return {v.codigo: v for v in e.globales}


# ===========================================================================
# 1. LA PUERTA DEL DATO
# ===========================================================================

def test_la_puerta_normaliza_a_entrada_y_salida_con_la_traza_comun():
    valor = dict(TRAZA, entrada={"E4": {"estatico": 1.8, "sismico": 1.4}},
                 salida={"E5": {"estatico": 1.6, "sismico": 1.3},
                         "documento": "otro documento de prueba"})
    norm = M9.validar_estabilidad_global_declarada(valor)
    assert set(norm) == {"entrada", "salida"}
    assert norm["entrada"]["E4"] == {"estatico": 1.8, "sismico": 1.4}
    assert "E5" not in norm["entrada"]
    assert norm["entrada"]["documento"] == TRAZA["documento"]
    assert norm["salida"]["documento"] == "otro documento de prueba"
    assert norm["salida"]["metodo"] == "Spencer"
    assert norm["salida"]["programa"] == TRAZA["programa"]


def test_un_extremo_sin_factores_queda_vacio_y_sin_traza():
    norm = M9.validar_estabilidad_global_declarada(
        dict(TRAZA, salida={"E4": {"estatico": 1.8, "sismico": 1.4}}))
    assert norm["entrada"] == {}
    assert norm["salida"]["E4"]["sismico"] == pytest.approx(1.4, abs=ABS_CERO)


@pytest.mark.parametrize("valor", [
    None, [], "1.5", {},
    # sin ningun factor
    dict(TRAZA),
    # un factor fuera de un extremo: es de la seccion de UN cabezal
    dict(TRAZA, E4={"estatico": 1.8, "sismico": 1.4}),
    # clave desconocida, arriba y dentro
    dict(TRAZA, autor="x", entrada={"E4": {"estatico": 1.8, "sismico": 1.4}}),
    dict(TRAZA, entrada={"E6": {"estatico": 1.8, "sismico": 1.4}}),
    # medio analisis no es un analisis: las dos condiciones
    dict(TRAZA, entrada={"E4": {"estatico": 1.8}}),
    dict(TRAZA, entrada={"E4": {"estatico": 1.8, "sismico": 1.4,
                                "dinamico": 1.1}}),
    # un FS que no es un numero positivo y finito
    dict(TRAZA, entrada={"E4": {"estatico": 0.0, "sismico": 1.4}}),
    dict(TRAZA, entrada={"E4": {"estatico": -1.0, "sismico": 1.4}}),
    dict(TRAZA, entrada={"E4": {"estatico": "1.8", "sismico": 1.4}}),
    dict(TRAZA, entrada={"E4": {"estatico": True, "sismico": 1.4}}),
    dict(TRAZA, entrada={"E4": {"estatico": float("inf"), "sismico": 1.4}}),
    # sin la traza del documento: un FS sin fuente no entra
    {"entrada": {"E4": {"estatico": 1.8, "sismico": 1.4}}},
    dict({k: v for k, v in TRAZA.items() if k != "fecha"},
         entrada={"E4": {"estatico": 1.8, "sismico": 1.4}}),
    dict(TRAZA, documento="  ",
         entrada={"E4": {"estatico": 1.8, "sismico": 1.4}}),
    dict(TRAZA, metodo=3, entrada={"E4": {"estatico": 1.8, "sismico": 1.4}}),
])
def test_la_puerta_rechaza_lo_que_no_es_un_resultado_trazable(valor):
    with pytest.raises(DatoInvalidoError):
        M9.validar_estabilidad_global_declarada(valor)


def test_la_clave_es_del_cabezal_opcional_y_no_una_falta(tmp_path):
    clave = servicio.CLAVE_ESTABILIDAD_GLOBAL_DECLARADA
    assert clave == "estabilidad_global_declarada"
    assert clave in servicio.CLAVES_DE_CABEZAL
    assert clave not in servicio.CLAVES_EXTERNAS
    externos = _externos(tmp_path, puntos={"A-01": {clave: dict(
        TRAZA, entrada={"E4": {"estatico": 1.8, "sismico": 1.4}})}})
    valor = externos.valor("A-01", clave)
    assert valor["entrada"]["E4"]["estatico"] == pytest.approx(1.8,
                                                              abs=ABS_CERO)
    assert externos.valor("A-02", clave) is None


def test_un_factor_de_seguridad_no_se_declara_para_todos_los_puntos(tmp_path):
    clave = servicio.CLAVE_ESTABILIDAD_GLOBAL_DECLARADA
    with pytest.raises(DatoInvalidoError) as e:
        _externos(tmp_path, globales={clave: dict(
            TRAZA, entrada={"E4": {"estatico": 1.8, "sismico": 1.4}})})
    assert "por punto" in str(e.value)


# ===========================================================================
# 2. SIN EL DATO NADA CAMBIA
# ===========================================================================

def test_sin_dato_declarado_E4_y_E5_siguen_diferidas(tanteo):
    for condicion in (EST, SIS):
        e = M9.ensamble_estabilidad(tanteo, condicion)
        assert [p[0] for p in e.pendientes] == ["E4", "E5"]
        assert e.pendientes == M9.PENDIENTES_E4_E5
        assert e.globales == ()
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert "9.3.g.e" in [p.codigo for p in e.pasos]
    assert any("E4 y E5" in a and "NO se evaluan" in a for a in e.avisos)


# ===========================================================================
# 3. CON EL DATO: EL CONTRASTE EN LOS DOS MARCOS
# ===========================================================================

def test_con_E4_y_E5_declaradas_no_queda_nada_diferido(tanteo):
    entorno = replace(tanteo, estabilidad_global=_declarado(**FS_AMBOS))
    e = M9.ensamble_estabilidad(entorno, EST)
    assert e.pendientes == ()
    assert "9.3.g.e" not in [p.codigo for p in e.pasos]
    assert not any("NO se evaluan" in a for a in e.avisos)
    assert set(_filas(e)) == {"E4-ASD.est.e", "E4-LRFD.est.e",
                              "E5-ASD.est.e", "E5-LRFD.est.e"}
    s = M9.ensamble_estabilidad(entorno, SIS)
    assert set(_filas(s)) == {"E4-ASD.sis.e", "E4-LRFD.sis.e",
                              "E5-ASD.sis.e", "E5-LRFD.sis.e"}


def test_el_marco_ASD_contrasta_con_el_FS_de_E050(tanteo):
    entorno = replace(tanteo, estabilidad_global=_declarado(**FS_AMBOS))
    for condicion, sufijo in ((EST, "est"), (SIS, "sis")):
        filas = _filas(M9.ensamble_estabilidad(entorno, condicion))
        for codigo, clave in (("E4", "estabilidad_global"), ("E5", "talud")):
            v = filas[f"{codigo}-ASD.{sufijo}.e"]
            assert v.valor_admisible == pytest.approx(
                cn.FS[clave][condicion.value], abs=ABS_CERO)
            assert v.valor_obtenido == pytest.approx(
                FS_AMBOS[codigo][condicion.value], abs=ABS_CERO)
            assert v.cumple
            assert v.paso.umbral.cita_id == (
                "E050.39.13.6" if codigo == "E4" else "E050.30.3")


def test_el_marco_LRFD_bajo_sismo_es_el_inverso_de_phi_11_5_8(tanteo):
    entorno = replace(tanteo, estabilidad_global=_declarado(**FS_AMBOS))
    filas = _filas(M9.ensamble_estabilidad(entorno, SIS))
    phi = cn.PHI_EVENTO_EXTREMO_11_5_8["estabilidad_global"]
    for codigo in ("E4", "E5"):
        v = filas[f"{codigo}-LRFD.sis.e"]
        assert v.valor_admisible == pytest.approx(1 / phi, abs=ABS_CERO)
        assert v.paso.umbral.cita_id == "AASHTO_LRFD_9.11.5.8#GLOBAL"
        assert v.cumple


@pytest.mark.parametrize("fila", sorted(cn.PHI_ESTABILIDAD_GLOBAL_11_6_3_7))
def test_el_marco_LRFD_estatico_con_la_fila_declarada(tanteo, fila):
    ca.establecer_valor_dinamico("fila_phi_estabilidad_global", fila)
    phi = cn.PHI_ESTABILIDAD_GLOBAL_11_6_3_7[fila]
    entorno = replace(tanteo, estabilidad_global=_declarado(**FS_AMBOS))
    v = _filas(M9.ensamble_estabilidad(entorno, EST))["E4-LRFD.est.e"]
    assert v.valor_admisible == pytest.approx(1 / phi, abs=ABS_CERO)
    assert v.criterio_aplicado == "fila_phi_estabilidad_global"
    assert v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE


@pytest.mark.parametrize("fs, tipo", [
    (1.60, TipoDeVeredicto.CUMPLE),       # >= 1/0.65: cumple con las dos
    (1.40, TipoDeVeredicto.INDICADOR),    # entre 1/0.75 y 1/0.65
    (1.20, TipoDeVeredicto.NO_CUMPLE),    # < 1/0.75: ninguna fila lo salva
])
def test_sin_la_fila_de_phi_el_LRFD_estatico_solo_decide_si_no_depende_de_ella(
        tanteo, fs, tipo):
    """
    El patron de la fila A6 del armado: sin la eleccion declarada, la fila
    decide cuando las dos opciones dan lo mismo y sale INDICADOR «no
    decidida» cuando no. No se detiene ni se rellena el vacio.
    """
    assert ca.CRITERIOS["fila_phi_estabilidad_global"].valor is None
    entorno = replace(tanteo, estabilidad_global=_declarado(
        E4={"estatico": fs, "sismico": 1.40}))
    v = _filas(M9.ensamble_estabilidad(entorno, EST))["E4-LRFD.est.e"]
    assert v.paso.veredicto.tipo is tipo
    assert v.cumple is (tipo is not TipoDeVeredicto.NO_CUMPLE)
    if tipo is TipoDeVeredicto.INDICADOR:
        assert "no decidida" in v.paso.veredicto.explicacion


def test_un_FS_que_no_alcanza_el_minimo_no_cumple_y_lo_dice(tanteo):
    entorno = replace(tanteo, estabilidad_global=_declarado(
        E5={"estatico": 1.20, "sismico": 1.10}))
    filas = _filas(M9.ensamble_estabilidad(entorno, EST))
    asd = filas["E5-ASD.est.e"]
    # El marco ASD informa con la regla de archivo (rige el LRFD).
    assert asd.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert filas["E5-LRFD.est.e"].paso.veredicto.tipo is \
        TipoDeVeredicto.NO_CUMPLE
    assert not filas["E5-LRFD.est.e"].cumple


def test_con_el_marco_ASD_rigiendo_el_LRFD_informa(tanteo):
    ca.establecer_valor_dinamico("marco_estabilidad_cabezal", MARCO_RIGE_ASD)
    entorno = replace(tanteo, estabilidad_global=_declarado(
        E4={"estatico": 1.20, "sismico": 1.10}))
    filas = _filas(M9.ensamble_estabilidad(entorno, EST))
    assert filas["E4-ASD.est.e"].paso.veredicto.tipo is \
        TipoDeVeredicto.NO_CUMPLE
    assert filas["E4-LRFD.est.e"].paso.veredicto.tipo is \
        TipoDeVeredicto.INDICADOR


def test_las_filas_E4_E5_no_tocan_el_cumple_de_E1_a_E3(tanteo):
    """
    El dimensionamiento de la zapata itera sobre `EstabilidadDelCabezal.
    cumple` (E1 a E3): un FS global declarado que no alcanza no lo cambia,
    porque el ancho de la zapata no mueve un FS que no calcula el programa.
    """
    sin = M9.ensamble_estabilidad(tanteo, EST)
    entorno = replace(tanteo, estabilidad_global=_declarado(
        E4={"estatico": 1.0, "sismico": 1.0}))
    con = M9.ensamble_estabilidad(entorno, EST)
    assert [v.codigo for v in con.verificaciones] == \
        [v.codigo for v in sin.verificaciones]
    assert con.cumple is sin.cumple


def test_con_solo_E4_declarada_E5_sigue_diferida(tanteo):
    entorno = replace(tanteo, estabilidad_global=_declarado(
        E4={"estatico": 1.8, "sismico": 1.4}))
    e = M9.ensamble_estabilidad(entorno, EST)
    assert [p[0] for p in e.pendientes] == ["E5"]
    paso = next(p for p in e.pasos if p.codigo == "9.3.g.e")
    assert "E5" in paso.que and "E4" not in paso.que
    aviso = next(a for a in e.avisos if "NO se evalua" in a)
    assert "E5" in aviso and "E4 y E5" not in aviso
    assert {v.codigo.split(".")[0] for v in e.globales} == {"E4-ASD",
                                                           "E4-LRFD"}


# ===========================================================================
# 4. LA MEMORIA: EL FS ES DECLARADO, NO CALCULADO
# ===========================================================================

def test_el_paso_dice_de_donde_sale_el_FS_y_que_no_lo_calcula_el_programa(
        tanteo):
    entorno = replace(tanteo, estabilidad_global=_declarado(**FS_AMBOS))
    for v in M9.ensamble_estabilidad(entorno, EST).globales:
        p = v.paso
        assert p.fundamento_id == "F9.GLOBAL_DECLARADA"
        textos = " ".join([p.resultado.procedencia]
                          + [m.procedencia for m in p.sustitucion])
        assert TRAZA["documento"] in textos
        assert TRAZA["fecha"] in textos and "Spencer" in textos
        assert "no lo calcula este programa" in p.resultado.procedencia
        assert p.umbral is not None and p.veredicto is not None


def test_el_registro_sostiene_el_fundamento_y_sus_citas():
    reg = construir()
    f = reg.fundamento("F9.GLOBAL_DECLARADA")
    for cita_id in ("AASHTO_LRFD_9.11.6.3.7#PHI",
                    "AASHTO_LRFD_9.C11.6.3.7#FS",
                    "AASHTO_LRFD_9.11.5.8#GLOBAL",
                    "E050.39.13.6", "E050.30.3"):
        assert cita_id in f.citas
        reg.cita(cita_id)
    assert reg.cita("AASHTO_LRFD_9.C11.6.3.7#FS").interpretacion is not None


def test_el_criterio_de_la_fila_de_phi_es_A_de_expediente_y_sin_valor():
    c = ca.CRITERIOS["fila_phi_estabilidad_global"]
    assert c.etiqueta == "A" and c.valor is None
    assert c.nivel == ca.NIVEL_EXPEDIENTE
    assert set(c.sensibilidad) == set(cn.PHI_ESTABILIDAD_GLOBAL_11_6_3_7)


# ===========================================================================
# 5. DE PUNTA A PUNTA, POR LA PUERTA DE `--datos-externos`
# ===========================================================================

def test_A01_con_E4_E5_declaradas_las_lleva_al_informe_y_al_JSON(tmp_path):
    clave = servicio.CLAVE_ESTABILIDAD_GLOBAL_DECLARADA
    declarado = dict(TRAZA, entrada=dict(FS_AMBOS), salida=dict(FS_AMBOS))
    informe, a01 = _correr_de_prueba(tmp_path, extra_a01={clave: declarado})
    assert a01.cabezal is not None and a01.cabezal.estabilidad
    for e in a01.cabezal.estabilidad:
        assert e.pendientes == ()
        assert len(e.globales) == 4
    todas = {v.codigo for v in a01.cabezal.verificaciones}
    assert {"E4-LRFD.est.e", "E5-ASD.sis.s"} <= todas
    assert not any("E4 y E5" in a and "NO se evaluan" in a
                   for a in a01.cabezal.avisos)
    volcado = cli.informe_json(informe)
    punto = next(p for p in volcado["puntos"] if p["id"] == "A-01")
    est = punto["cabezal"]["estabilidad"][0]
    assert "E4-LRFD.est.e" in est["verificaciones"]
    assert est["pendientes"] == []
    json.dumps(volcado)


def test_la_memoria_del_punto_imprime_el_FS_declarado_con_su_documento(
        tmp_path):
    """
    La memoria HTML del punto lleva las filas E4 y E5 con el paso entero, y
    el FS sale rotulado como DECLARADO en su documento, nunca como un
    calculo del programa. Con solo E4 declarada, E5 sigue «diferida».
    """
    from src.modulos import M11_reporte as M11
    clave = servicio.CLAVE_ESTABILIDAD_GLOBAL_DECLARADA
    declarado = dict(TRAZA, entrada={"E4": FS_AMBOS["E4"]},
                     salida={"E4": FS_AMBOS["E4"]})
    _, a01 = _correr_de_prueba(tmp_path, extra_a01={clave: declarado})
    html = M11.memoria_de_punto(a01)
    for pieza in ("E4 (LRFD), estabilidad global del muro",
                  "E4 (ASD), estabilidad global del muro",
                  TRAZA["documento"], "no lo calcula este programa",
                  "E5, estabilidad del talud", "diferida al expediente"):
        assert pieza in html, pieza
    for e in a01.cabezal.estabilidad:
        assert [p[0] for p in e.pendientes] == ["E5"]
