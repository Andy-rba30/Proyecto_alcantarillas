"""
tests/test_ext3_regimen_barril.py
=================================
ACEPTACION DE EXT-3: regimen del barril y dominio del metodo (cluster C06;
EXT-M-01, EXT-M-02, PC-04, PC-27 mitad compuerta, SIS-B-18 mitad JSON).

Se escribieron primero EN ROJO (`xfail(strict=True)`) con la expectativa de la
FUENTE o del invariante, nunca con la salida del codigo como oraculo, y el
xfail se retiro al corregir. Los cuatro casos del prompt, con los numeros que
la v8 enmendada en EXT-0 y el dictamen del 2026-09-19 fijan:

  (a) ahogado: D = 0.90, Q = 0.05, S = 0.005, L = 20, TW = 1.2, concreto.
      El barril fluye LLENO (TW >= D). V2 compara Q/A_llena = 0.0786 m/s <
      0.25 y NO cumple; V1 a seccion llena NO cumple (MC-HHD pag. 79, «no
      deben ser diseñadas para trabajar a seccion llena»). El punto no sale
      «dimensionado» sin bloqueo.
  (b) Q = 0.3, S = 0.005, TW = 0: control de salida con HW/D = 0.589 < 0.75.
      El metodo aproximado de h_o NO esta definido ahi (HDS-5 pag. 3.24):
      «metodo no evaluable», por la via Bloqueo -- diferible en perfil, no en
      expediente --. Nunca DisenoNoFactibleError ni Verificacion(cumple=False):
      subir D solo baja HW/D.
  (c) subcritico con salida libre: Q = 0.3, S = 0.001. La velocidad que recibe
      M6 es la de SALIDA por HDS-5 3.1.6 (area a y_c: 1.508 m/s), no
      V_erosion (1.184 m/s, regimen uniforme).
  (d) el bloque h_o entero viaja al JSON y a `cli.volcar`.

Los numeros de contraste (0.0786, 0.589, 1.508, 1.184) son los del dictamen y
de la v8 §1.3; el dorado CERRADO es el del regimen lleno (CP-12: Q/A_llena es
aritmetica de la fuente), y para (c) no hay dorado a proposito: y_c sale de
Brent (conflicto #7 de la matriz de auditorias).
"""

import json
import math
from pathlib import Path

import pytest

import cli
from src import modelos
from src.modelos import (ControlGobernante, DisenoNoFactibleError, ErrorProyecto,
                     Magnitud, SeccionCircular, TipoDeVeredicto, TipoMaterial)
from src.modulos import M4_control as M4
from src.modulos import M5_verificaciones as M5
from src.modulos import M6_proteccion as M6
from src.modulos import MD
from src.modulos.M2_material import catalogo
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP12_REGIMEN_LLENO
from tests.test_MD import _punto as _punto_md

# Tolerancia con que se contrastan los numeros que el dictamen imprime con
# tres o cuatro cifras (0.0786, 0.589, 1.508, 1.184): no son dorados, son la
# lectura del dictamen y por eso se comparan a la cifra impresa.
REL_DICTAMEN = 1e-3

# Escritos en rojo con `xfail(strict=True)` y liberados al corregir (EXT-3):
# el marcador se retiro y esta linea queda como constancia.

CSV_BASE = Path(__file__).resolve().parent / "ejemplo_puntos_perfil.csv"

# Los criterios que la corrida necesita declarados para pasar de la Fase 5,
# los mismos de `CRITERIOS_CORRIDA_PERFIL` en tests/test_cli.py.
CRITERIOS_CORRIDA = dict(peso_especifico_relleno_kn_m3=18.0, v_max_tmc=4.5,
                         v_max_hdpe=4.5)

# Datos comunes de las corridas de aceptacion: la fila B-01 del CSV de perfil
# con Q y S sustituidos, y los externos que esa corrida ya usa.
D_CASO = 0.90
L_CASO = 20.0


def _concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


def _resuelto(Q, S, TW, L=L_CASO, D=D_CASO):
    return M4.resolver_control(seccion=SeccionCircular(D), Q=Q, S=S, L=L,
                               TW=TW, material=_concreto())


def _csv_b01(tmp_path, *, Q, S):
    """Un CSV con la fila B-01 del corredor de perfil, con Q y S propios."""
    lineas = CSV_BASE.read_text(encoding="utf-8").splitlines()
    cabecera = lineas[0].split(",")
    fila = next(l for l in lineas[1:] if l.startswith("B-01")).split(",")
    fila[cabecera.index("Q_m3s")] = repr(Q)
    fila[cabecera.index("S_cauce")] = repr(S)
    ruta = tmp_path / "caso.csv"
    ruta.write_text(lineas[0] + "\n" + ",".join(fila) + "\n", encoding="utf-8")
    return ruta


def _correr(tmp_path, *, Q, S, TW, alcance):
    externos = cli.cargar_datos_externos(
        None, dict(luz_m=2.0, TW_m=TW, longitud_m=L_CASO, L_hidraulico_m=180.0))
    with declarados(CRITERIOS_CORRIDA):
        return cli.correr(_csv_b01(tmp_path, Q=Q, S=S), externos,
                          alcance=alcance)


def _b01(informe):
    return next(p for p in informe.puntos if p.punto.id == "B-01")


def _no_evaluables(informe_punto):
    return [b for b in informe_punto.bloqueos
            if b.tipo == "MetodoNoEvaluableError"]


# ===========================================================================
# Lo que EXT-3 introduce como tipos, y donde viven
# ===========================================================================

def test_bloqueo_vive_en_modelos_con_tipo_enum():
    """PC-27 (mitad compuerta): el estado «bloqueado/diferido» fluye entre
    capas, asi que su tipo vive en modelos.py y `tipo` es un Enum, no un str
    libre. Los VALORES son los strings de hoy, para que la linea base no se
    mueva por esto y `b.tipo == "CriterioPendienteError"` siga valiendo."""
    Bloqueo = modelos.Bloqueo
    TipoDeBloqueo = modelos.TipoDeBloqueo
    assert cli.Bloqueo is Bloqueo
    assert TipoDeBloqueo.CRITERIO_PENDIENTE == "CriterioPendienteError"
    assert TipoDeBloqueo.DISENO_NO_FACTIBLE == "DisenoNoFactibleError"
    assert TipoDeBloqueo.DATO_FALTANTE == "DatoFaltanteError"
    assert TipoDeBloqueo.DATO_INVALIDO == "DatoInvalidoError"
    assert TipoDeBloqueo.LIMITE_NUMERICO == "LimiteNumericoError"
    assert TipoDeBloqueo.METODO_NO_EVALUABLE == "MetodoNoEvaluableError"
    assert TipoDeBloqueo.DIFERIDO_POR_ALCANCE == "DiferidoPorAlcance"
    b = Bloqueo(fase="f", etapa="e", tipo=TipoDeBloqueo.DIFERIDO_POR_ALCANCE,
                mensaje="m")
    assert b.tipo is TipoDeBloqueo.DIFERIDO_POR_ALCANCE
    with pytest.raises(TypeError):
        Bloqueo(fase="f", etapa="e", tipo="DiferidoPorAlcance", mensaje="m")


def test_metodo_no_evaluable_es_la_sexta_excepcion_del_expediente():
    exc = modelos.MetodoNoEvaluableError
    assert issubclass(exc, ErrorProyecto)
    for hermana in (modelos.CriterioPendienteError, DisenoNoFactibleError,
                    modelos.DatoFaltanteError, modelos.DatoInvalidoError,
                    modelos.LimiteNumericoError):
        assert not issubclass(exc, hermana)
        assert not issubclass(hermana, exc)
    e = exc(que="V1", procedimiento="perfil de la lamina de agua",
            motivo="control de salida con barril parcialmente lleno",
            id_punto="B-01")
    assert str(e).startswith(modelos.MOTIVO_METODO_NO_EVALUABLE)
    assert modelos.MOTIVO_METODO_NO_EVALUABLE == (
        "método no evaluable (HDS-5 3.24, Sección 3.5)")
    assert "B-01" in str(e) and "V1" in str(e)
    assert modelos.TipoDeBloqueo.de_excepcion(e) \
        is modelos.TipoDeBloqueo.METODO_NO_EVALUABLE


def test_regimen_barril_tiene_dos_estados_y_nada_mas():
    RegimenBarril = modelos.RegimenBarril
    assert {m.name for m in RegimenBarril} == {"LLENO", "PARCIALMENTE_LLENO"}


# ===========================================================================
# (a) Caso ahogado: TW = 1.2 m sobre D = 0.90 m
# ===========================================================================

def test_a_la_fuente_reproduce_el_caso_ahogado_tal_como_esta_hoy():
    """Lo que NO cambia y ancla el caso: control de salida, y_n/D = 0.135."""
    r = _resuelto(Q=0.05, S=0.005, TW=1.2)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.y_normal / D_CASO == pytest.approx(0.135, rel=REL_DICTAMEN)
    assert r.Q / SeccionCircular(D_CASO).area_llena == pytest.approx(
        CP12_REGIMEN_LLENO["V_llena_esperada"],
        rel=CP12_REGIMEN_LLENO["tolerancia"])


def test_a_el_regimen_es_lleno_y_M4_lo_emite_con_la_velocidad_llena():
    r = _resuelto(Q=0.05, S=0.005, TW=1.2)
    assert r.regimen_barril is modelos.RegimenBarril.LLENO
    assert r.V_llena_m_s == pytest.approx(CP12_REGIMEN_LLENO["V_llena_esperada"],
                                         rel=CP12_REGIMEN_LLENO["tolerancia"])
    # La velocidad de SALIDA por HDS-5 3.1.6: TW sobre la clave -> area total.
    assert isinstance(r.V_salida, Magnitud)
    assert r.V_salida.valor == pytest.approx(r.V_llena_m_s, rel=REL_TRANSPORTE)
    assert r.V_salida.procedencia
    assert r.y_salida_m == pytest.approx(D_CASO, rel=REL_TRANSPORTE)
    # El bloque h_o viaja entero en el resultado (SIS-B-18).
    assert r.h_o_m == pytest.approx(1.2, rel=REL_TRANSPORTE)
    assert r.TW_m == pytest.approx(1.2, rel=REL_TRANSPORTE)
    assert r.ahogado_por_TW is True


def test_a_V2_compara_la_velocidad_de_la_seccion_llena_y_no_cumple():
    r = _resuelto(Q=0.05, S=0.005, TW=1.2)
    v2 = M5.v2_velocidad_minima(resultado=r)
    assert not v2.cumple
    assert v2.valor_obtenido == pytest.approx(0.0786, rel=REL_DICTAMEN)
    # Y NO la velocidad uniforme de M3 (0.974 m/s), que es lo que pasaba.
    assert v2.valor_obtenido != pytest.approx(r.V_sedimentacion, rel=REL_DICTAMEN)
    assert v2.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE


def test_a_V1_a_seccion_llena_no_cumple_con_la_cita_de_la_pag_79():
    r = _resuelto(Q=0.05, S=0.005, TW=1.2)
    v1 = M5.v1_borde_libre(D=D_CASO, material=_concreto(),
                           punto=_punto_md(), resultado=r)
    assert not v1.cumple
    assert v1.valor_obtenido == pytest.approx(
        CP12_REGIMEN_LLENO["y_sobre_D_esperado"], rel=REL_TRANSPORTE)
    assert "MC_HHD.4.1.1.3.7b#LLENA" in v1.paso.citas_textuales
    assert v1.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE


def test_a_el_punto_no_sale_dimensionado_sin_bloqueo(tmp_path):
    """
    En expediente el punto no cierra: el escalon D = 0.90 va LLENO y V1 y V2
    NO cumplen en la traza --hasta EXT-3 salian [OK]--, y el bucle se detiene
    en el primer pendiente del expediente (V5, remanso) antes de subir de
    diametro. Nunca «dimensionado» limpio, nunca DisenoNoFactibleError.
    """
    informe = _correr(tmp_path, Q=0.05, S=0.005, TW=1.2,
                      alcance=cli.ALCANCE_EXPEDIENTE)
    b01 = _b01(informe)
    assert not b01.dimensionado
    assert b01.bloqueos and not informe.cerrado
    assert not [b for b in b01.bloqueos if b.tipo == "DisenoNoFactibleError"]
    escalon = next(p for p in b01.traza
                   if p.material.startswith("Concreto") and "0.90" in p.seccion.etiqueta())
    assert escalon.resultado_hidraulico.regimen_barril is modelos.RegimenBarril.LLENO
    veredictos = {v.codigo: v.cumple for v in escalon.verificaciones}
    assert veredictos["V1"] is False and veredictos["V2"] is False


def test_a_en_perfil_solo_dimensiona_por_encima_del_TW_y_con_V1_V2_diferidas(
        tmp_path):
    """
    A nivel de perfil ningun D <= TW cierra (van llenos: V1 y V2 no cumplen),
    y el primer D > TW va parcialmente lleno bajo control de salida: V1 y V2
    quedan DIFERIDAS por metodo no evaluable, no aprobadas con el tirante
    normal. El punto sale dimensionado CON esos bloqueos, nunca limpio.
    """
    informe = _correr(tmp_path, Q=0.05, S=0.005, TW=1.2,
                      alcance=cli.ALCANCE_PERFIL)
    b01 = _b01(informe)
    assert b01.dimensionado
    assert b01.resultado.seccion.altura > 1.2
    llenos = [p for p in b01.traza
              if p.resultado_hidraulico is not None
              and p.resultado_hidraulico.regimen_barril is modelos.RegimenBarril.LLENO]
    assert llenos and all(not p.aceptado for p in llenos)
    diferidos = [b for b in _no_evaluables(b01) if b.diferido_por_alcance]
    etapas = " ".join(b.etapa for b in diferidos)
    assert "V1" in etapas and "V2" in etapas
    assert not [b for b in b01.bloqueos if b.tipo == "DisenoNoFactibleError"]


# ===========================================================================
# (b) HW/D = 0.589 bajo control de salida: metodo no evaluable
# ===========================================================================

def test_b_la_fuente_reproduce_el_caso_del_dictamen_tal_como_esta_hoy():
    r = _resuelto(Q=0.3, S=0.005, TW=0.0)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.HW_sobre_D_salida == pytest.approx(0.589, rel=REL_DICTAMEN)
    assert r.h_o_fuera_de_rango is True


def test_b_el_paso_de_h_o_dice_DIFERIDO_y_no_NO_CUMPLE():
    """SIS-A-07: memoria y pipeline dicen lo mismo. El paso F4.HO no juzga
    «no cumple» un punto que el pipeline no rechaza: dice que el metodo no es
    evaluable ahi, con el motivo de la fuente."""
    r = _resuelto(Q=0.3, S=0.005, TW=0.0)
    ho = next(p for p in r.pasos if p.fundamento_id == "F4.HO")
    assert ho.veredicto.tipo is TipoDeVeredicto.DIFERIDO
    assert modelos.MOTIVO_METODO_NO_EVALUABLE in ho.veredicto.explicacion
    assert r.regimen_barril is modelos.RegimenBarril.PARCIALMENTE_LLENO


def test_b_V1_y_V2_quedan_pendientes_bajo_control_de_salida_parcial():
    r = _resuelto(Q=0.3, S=0.005, TW=0.0)
    with pytest.raises(modelos.MetodoNoEvaluableError) as e1:
        M5.v1_borde_libre(D=D_CASO, material=_concreto(), punto=_punto_md(),
                          resultado=r)
    with pytest.raises(modelos.MetodoNoEvaluableError) as e2:
        M5.v2_velocidad_minima(resultado=r)
    assert e1.value.que == "V1" and e2.value.que == "V2"


def test_b_MD_nunca_degrada_a_diseno_no_factible():
    """Subir de diametro solo baja HW/D (0.589 -> 0.526 medido en el
    dictamen): recorrer el catalogo hasta DisenoNoFactibleError seria
    rechazar por una condicion que ningun D puede cumplir."""
    punto = _punto_md(id="B-01", Q_m3s=0.3, S_cauce=0.005)
    with declarados(CRITERIOS_CORRIDA):
        with pytest.raises(ErrorProyecto) as exc:
            MD.disenar_punto(punto, L=L_CASO, TW=0.0)
    assert isinstance(exc.value, modelos.MetodoNoEvaluableError)
    assert not isinstance(exc.value, DisenoNoFactibleError)


def test_b_en_expediente_el_punto_no_cierra_como_si(tmp_path):
    informe = _correr(tmp_path, Q=0.3, S=0.005, TW=0.0,
                      alcance=cli.ALCANCE_EXPEDIENTE)
    b01 = _b01(informe)
    assert not informe.cerrado
    assert _no_evaluables(b01)
    assert not any(b.diferido_por_alcance for b in _no_evaluables(b01))
    assert not [b for b in b01.bloqueos if b.tipo == "DisenoNoFactibleError"]
    for _codigo, v in b01.verificaciones():
        assert v.cumple, "nunca Verificacion(cumple=False) por el dominio de h_o"


def test_b_en_perfil_queda_dimensionado_con_HW_no_evaluable_diferido(tmp_path):
    informe = _correr(tmp_path, Q=0.3, S=0.005, TW=0.0,
                      alcance=cli.ALCANCE_PERFIL)
    b01 = _b01(informe)
    assert b01.dimensionado
    diferidos = [b for b in _no_evaluables(b01) if b.diferido_por_alcance]
    assert diferidos, [b.tipo for b in b01.bloqueos]
    assert any(modelos.MOTIVO_METODO_NO_EVALUABLE in b.mensaje
               for b in diferidos)
    # Ninguno de ellos cuenta para el cierre de perfil...
    assert all(b.diferido_por_alcance for b in _no_evaluables(b01))
    # ...y V1 y V2 estan entre los diferidos, no entre las filas de la tabla.
    codigos = {c for c, _v in b01.verificaciones()}
    assert "V1" not in codigos and "V2" not in codigos
    etapas = " ".join(b.etapa for b in diferidos)
    assert "V1" in etapas and "V2" in etapas


# ===========================================================================
# (c) Subcritico con salida libre: la velocidad que recibe M6
# ===========================================================================

def test_c_la_fuente_reproduce_el_caso_subcritico_tal_como_esta_hoy():
    r = _resuelto(Q=0.3, S=0.001, TW=0.0)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.y_normal > r.y_critico
    assert r.V_erosion == pytest.approx(1.184, rel=REL_DICTAMEN)
    y_sal = min(D_CASO, max(0.0, r.y_critico))
    assert r.Q / SeccionCircular(D_CASO).area(y_sal) == pytest.approx(
        1.508, rel=REL_DICTAMEN)


def test_c_M4_emite_la_velocidad_de_salida_a_y_c_bajo_control_de_salida():
    r = _resuelto(Q=0.3, S=0.001, TW=0.0)
    assert r.V_salida.valor == pytest.approx(1.508, rel=REL_DICTAMEN)
    assert r.y_salida_m == pytest.approx(r.y_critico, rel=REL_TRANSPORTE)
    assert "3.1.6" in r.V_salida.procedencia
    regimen = next(p for p in r.pasos if p.fundamento_id == "F4.REGIMEN")
    assert regimen.resultado.valor == pytest.approx(1.508, rel=REL_DICTAMEN)


def test_c_bajo_control_de_entrada_la_velocidad_de_salida_es_la_normal():
    """La otra mitad de HDS-5 3.1.6 (pag. 3.24): bajo control de entrada la
    velocidad a la salida es la del tirante normal. Se conserva la rama n_min
    (techo conservador para d50), con su procedencia."""
    r = _resuelto(Q=1.167, S=0.006, TW=0.22)      # A-01 del corredor
    assert r.control_gobernante is ControlGobernante.ENTRADA
    assert r.V_salida.valor == pytest.approx(r.V_erosion, rel=REL_TRANSPORTE)


def test_c_M6_recibe_la_velocidad_de_salida_y_no_V_erosion(tmp_path):
    informe = _correr(tmp_path, Q=0.3, S=0.001, TW=0.0,
                      alcance=cli.ALCANCE_PERFIL)
    b01 = _b01(informe)
    assert b01.dimensionado and b01.proteccion is not None
    assert b01.proteccion.V == pytest.approx(1.508, rel=REL_DICTAMEN)
    assert b01.proteccion.V != pytest.approx(1.184, rel=REL_DICTAMEN)
    # d50 crece con V^2: la piedra que sale es la de la velocidad real.
    assert b01.proteccion.d50 == pytest.approx(
        M6.laushey_d50(V=b01.proteccion.V), rel=REL_TRANSPORTE)


def test_c_M6_exige_una_magnitud_con_procedencia():
    v = Magnitud("V_salida", 2.0, "m/s", "prueba: velocidad explicita")
    with declarados(dict(longitud_proteccion_salida=3.0)):
        p = M6.proteccion_salida(V=v)
    assert p.V == pytest.approx(2.0, rel=REL_TRANSPORTE)
    sustitucion = {m.simbolo: m for m in p.paso.sustitucion}
    assert "prueba: velocidad explicita" in sustitucion["V"].procedencia


# ===========================================================================
# (d) El bloque h_o entero llega al JSON y a cli.volcar
# ===========================================================================

CLAVES_H_O = ("HW_sobre_D_salida", "h_o_m", "TW_m", "ahogado_por_TW",
              "h_o_fuera_de_rango", "h_o_requiere_cautela")
CLAVES_REGIMEN = ("regimen_barril", "V_salida_m_s", "V_salida_procedencia",
                  "y_salida_m", "V_llena_m_s", "Q_celda_m3s", "numero_celdas")


def test_d_el_bloque_h_o_llega_al_json(tmp_path):
    informe = _correr(tmp_path, Q=0.3, S=0.005, TW=0.0,
                      alcance=cli.ALCANCE_PERFIL)
    diseno = cli.informe_json(informe)["puntos"][0]["diseno"]
    for clave in CLAVES_H_O + CLAVES_REGIMEN:
        assert clave in diseno, clave
    assert diseno["h_o_fuera_de_rango"] is True
    assert diseno["ahogado_por_TW"] is False
    assert diseno["HW_sobre_D_salida"] == pytest.approx(0.589, rel=REL_DICTAMEN)
    assert diseno["regimen_barril"] == "parcialmente lleno"
    assert diseno["numero_celdas"] == 1
    json.dumps(cli.informe_json(informe))      # serializable entero


def test_d_el_bloque_h_o_llega_a_volcar(tmp_path):
    informe = _correr(tmp_path, Q=0.05, S=0.005, TW=1.2,
                      alcance=cli.ALCANCE_PERFIL)
    texto = cli.volcar(informe)
    assert "h_o" in texto and "HW/D" in texto
    assert "manda TW" in texto or "ahogad" in texto
    assert "lleno" in texto


# ===========================================================================
# La compuerta, llamada directamente: los dos alcances (auditoria de EXT-3)
# ===========================================================================
# A nivel de expediente ningun punto llega hoy dimensionado con HW/D < 0.75
# (V1/V2 bloquean antes), asi que la rama «no diferible» de la compuerta no se
# ejerce por el pipeline. Se fija aqui llamandola sobre un punto dimensionado
# a mano: una mutacion que la difiriera siempre pasaba 277 tests.

def _informe_dimensionado_con(resultado_hidraulico):
    from src.modelos import ResultadoPunto
    punto = _punto_md(id="B-01")
    informe = cli.InformePunto(punto=punto)
    informe.resultado = ResultadoPunto(
        punto=punto, aceptado=True, material=_concreto(),
        seccion=SeccionCircular(D_CASO), resultado_hidraulico=resultado_hidraulico,
        verificaciones=())
    return informe


def test_la_compuerta_no_difiere_en_expediente_y_si_en_perfil():
    r = _resuelto(Q=0.3, S=0.005, TW=0.0)          # HW/D = 0.589, fuera de rango
    assert r.h_o_fuera_de_rango
    exp = _informe_dimensionado_con(r)
    cli._compuerta_metodo_h_o(exp, cli.ALCANCE_EXPEDIENTE)
    [b] = _no_evaluables(exp)
    assert b.diferido_por_alcance is False
    assert "carga HW" in b.etapa and modelos.MOTIVO_METODO_NO_EVALUABLE in b.mensaje
    perfil = _informe_dimensionado_con(r)
    cli._compuerta_metodo_h_o(perfil, cli.ALCANCE_PERFIL)
    [b] = _no_evaluables(perfil)
    assert b.diferido_por_alcance is True


def test_la_compuerta_no_marca_un_punto_dentro_de_rango():
    r = _resuelto(Q=1.167, S=0.006, TW=0.22)       # A-01: control de entrada
    assert not r.h_o_fuera_de_rango
    for alcance in (cli.ALCANCE_EXPEDIENTE, cli.ALCANCE_PERFIL):
        informe = _informe_dimensionado_con(r)
        cli._compuerta_metodo_h_o(informe, alcance)
        assert not informe.bloqueos


# ===========================================================================
# La celda y/D del cuadro resumen sigue al regimen, como V1 (auditoria de EXT-3)
# ===========================================================================

def test_y_sobre_D_del_punto_sigue_al_regimen_del_barril():
    from src.modelos import ResultadoPunto

    def punto_con(r):
        return ResultadoPunto(punto=_punto_md(), aceptado=True,
                              material=_concreto(), seccion=SeccionCircular(D_CASO),
                              resultado_hidraulico=r, verificaciones=())
    lleno = punto_con(_resuelto(Q=0.05, S=0.005, TW=1.2))
    assert lleno.y_sobre_D == pytest.approx(1, rel=REL_TRANSPORTE)
    salida_parcial = punto_con(_resuelto(Q=0.3, S=0.005, TW=0.0))
    assert salida_parcial.y_sobre_D is None, (
        "bajo control de salida parcialmente lleno V1 queda pendiente: "
        "publicar y_normal/D en el resumen es la divergencia de SIS-A-07")
    entrada = punto_con(_resuelto(Q=1.167, S=0.006, TW=0.22))
    assert entrada.y_sobre_D == pytest.approx(
        entrada.resultado_hidraulico.y_normal / D_CASO, rel=REL_TRANSPORTE)


# ===========================================================================
# El dorado cerrado del regimen lleno (CP-12)
# ===========================================================================

def test_cp12_es_aritmetica_de_la_fuente():
    """Q/A_llena, con A_llena = pi*D^2/4: se rehace a mano en una linea."""
    c = CP12_REGIMEN_LLENO
    A = math.pi * c["D"] ** 2 / 4
    assert A == pytest.approx(c["A_llena_esperada"], rel=c["tolerancia"])
    assert c["Q"] / A == pytest.approx(c["V_llena_esperada"], rel=c["tolerancia"])
    assert c["TW"] >= c["D"]
    assert c["y_sobre_D_esperado"] == 1
