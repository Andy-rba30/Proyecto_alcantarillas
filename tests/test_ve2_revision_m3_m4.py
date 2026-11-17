"""
tests/test_ve2_revision_m3_m4.py
================================
Correcciones de la revision independiente de VE-2 (REVISION_FABLE.md), los
dos hallazgos MEDIOS que el dueño mando corregir sobre la flotacion (V7).

M3 · EL PESO SATURADO DEL RELLENO ES DE PERFIL. Con 'nivel_agua_diseno_v7' =
     «nf_del_punto» y el nivel sobre la clave, V7 (Fase 5, perfil) lee
     'peso_especifico_saturado_relleno_kn_m3'
     (`M8.peso_relleno_bajo_el_nivel_kn_m`), y el criterio estaba marcado
     de EXPEDIENTE: una corrida `--alcance perfil` se detenia en un vacio
     que el filtro de la pestaña 2 (`criterios_del_alcance`) escondia de
     quien lo tiene que declarar. Medido por la revision y aqui abajo: el
     bloqueo sale con `diferido_por_alcance` = False. El nivel de un
     criterio es el de la etapa que lo consume (CLAUDE.md, «Nivel de
     entrega»), y V7 es de perfil.

     La tension que VE-2 dejo escrita (ficha VE2-C, comentario de
     `tests/test_nivel_medido.py`) era real y se resuelve sin inventar
     ventana: el criterio es un DATO DE ENSAYO (`DeEnsayo`), y la guardia
     prohibe la `sensibilidad` a un `de_ensayo` («un dato determinado por un
     procedimiento no tiene rango que elegir») mientras `_verificar_nivel`
     se la exigia a todo [A] de perfil. Las dos reglas juntas hacian
     imposible un [A] de perfil de ensayo. Se exime al `de_ensayo` de la
     ventana en la regla 3 de `_verificar_nivel` --- su «ventana» es la
     trazabilidad que `DeEnsayo.trazabilidad_exigida` exige al declararlo
     (E-B: un dato de ensayo exige la nota) ---, y sigue exigiendo
     `resolucion`. Inventar un rango de pesos saturados para cumplir la
     regla habria sido rellenar un vacio; pasarlo a `Libre` con una ventana
     de texto habria quitado la exigencia de trazabilidad al declararlo.

M4 · EL MARGEN ESTACIONAL NO ENTRA NEGATIVO POR LA PUERTA.
     'margen_estacional_nf_v7_m' ([A] de perfil, `float`, ventana de texto
     porque su extremo de arriba depende del punto) admitia un negativo por
     los tres caminos y solo lo rechazaba su consumidor
     (`M8.cota_nivel_agua_v7_del_nf`, `DatoInvalidoError`). Se suma a
     `Criterio` el mismo campo de signo que `datos_sitio.DatoSitio` ya
     tiene, `no_negativo`, comprobado en `_verificar_criterio` (los tres
     caminos) con la condicion en positivo y negada (forma MAT-D13). No se
     inventa un tope: la ventana sigue siendo la de la ficha. La guardia del
     consumidor se queda como segunda linea.

N2 · (verificacion Fable de estas correcciones, decision del dueño) EL PESO
     SATURADO ES [S], Y LA EXENCION DE ARRIBA SE RETIRA. La verificacion
     observo que la exencion se justificaba con la definicion de [S] de la
     propia taxonomia (CLAUDE.md: «un [S] no tiene rango que elegir y se
     defiende con la trazabilidad de la lectura»), y que un dato de ensayo
     del relleno es, por esa regla, un [S] pendiente de ensayo. El dueño
     eligio reetiquetarlo: `peso_especifico_saturado_relleno_kn_m3` es [S]
     con su `trazabilidad`, sigue de perfil (medido) y la regla 3 de
     `_verificar_nivel` vuelve a exigir ventana a TODO [A] de perfil, sin
     excepcion (CLAUDE.md, al texto de d9b59f9). Y como observo tambien que
     la puerta aceptaba 0 y negativos, `Criterio.positivo` (el mismo campo
     que `DatoSitio.positivo`) los rechaza por los tres caminos.

Escrita PRIMERO, en rojo: los tests de abajo fallaban por su motivo antes de
tocar `criterios_adoptados.py` (medido con el archivo de d9b59f9: 13 fallos
de los 23; los diez que pasaban fijan lo que no debe cambiar --- el cero y el
positivo aceptados, el NaN rechazado, la ventana prohibida al dato de
ensayo, la segunda linea del consumidor y los cuatro [A] de perfil de otros
modos que siguen sin poder quedarse sin ventana ---). Mutantes medidos: no
llamar a `_verificar_signo` muere en seis tests; eximir
de la ventana a todo lo que no sea `Libre` muere en tres.
"""

from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import servicio
from src.modelos import (CriterioPendienteError, DatoInvalidoError,
                         DeEnsayo)
from tests.apoyo.criterios import con_valor, declarados
from tests.test_ve2_flotacion import (CLAVE_MARGEN, CLAVE_NIVEL,
                                      CLAVE_SATURADO, _punto, _v7)

RAIZ = Path(__file__).resolve().parents[1]


# ===========================================================================
# M3 · el peso saturado del relleno es de perfil
# ===========================================================================

def test_m3_el_peso_saturado_es_de_perfil_y_sigue_siendo_de_ensayo():
    """
    N2: es [S] pendiente de ensayo (antes [A] con la exencion de la regla
    3), con su trazabilidad; el nivel sigue siendo el medido, perfil.
    """
    c = ca.CRITERIOS[CLAVE_SATURADO]
    assert c.nivel == ca.NIVEL_PERFIL
    assert (c.etiqueta, c.forma, c.valor) == ("S", ca.FORMA_FLOAT, None)
    assert c.trazabilidad and "ensayo" in c.trazabilidad
    assert isinstance(c.resolucion, DeEnsayo)
    assert c.sensibilidad is None          # un [S] no tiene rango


def test_m3_el_filtro_de_perfil_lo_muestra():
    """Lo que la corrida de perfil puede necesitar, la pestaña 2 lo enseña."""
    assert CLAVE_SATURADO in ca.criterios_del_alcance(cli.ALCANCE_PERFIL)
    assert CLAVE_SATURADO in ca.criterios_de_perfil_sin_valor()


def _como_a(c):
    """La misma ficha rotulada [A], como estaba antes de N2."""
    return replace(c, etiqueta="A", trazabilidad=None)


def test_m3_la_guardia_vuelve_a_exigir_ventana_al_a_de_perfil_de_ensayo():
    """
    CAMBIADO EN N2 (verificacion Fable; se llamaba «…admite un [A] de perfil
    de ensayo sin ventana»): la exencion de la regla 3 se retira con la
    decision del dueño de reetiquetar el peso saturado a [S]. Un [A] de
    perfil que se resuelve por ensayo vuelve a no poder quedarse sin
    ventana; el que no tiene rango que elegir es [S].
    """
    c = _como_a(ca.CRITERIOS[CLAVE_SATURADO])
    assert isinstance(c.resolucion, DeEnsayo) and c.sensibilidad is None
    with pytest.raises(ValueError, match="sensibilidad"):
        ca._verificar_nivel(CLAVE_SATURADO, c)


def test_n2_ningun_a_de_perfil_queda_sin_ventana():
    """El invariante de salida del perfil, sobre el archivo entero."""
    sin_ventana = sorted(
        k for k, c in ca.CRITERIOS.items()
        if c.nivel == ca.NIVEL_PERFIL and c.etiqueta == "A"
        and c.sensibilidad is None)
    assert sin_ventana == []


@pytest.mark.parametrize("clave", [
    CLAVE_MARGEN,                      # Libre
    "riesgo_admisible_propietario",    # DeTabla
    "v_max_concreto_eleccion",         # EnRango
    "D_max_catalogo",                  # DeCatalogo
])
def test_m3_la_guardia_sigue_exigiendo_ventana_a_los_demas_a_de_perfil(clave):
    """
    La exencion es del `de_ensayo` y de nadie mas: un modo por cada otra
    resolucion que hoy tiene un [A] de perfil. Mutante medido: eximir todo lo
    que no sea `Libre` sobrevivia con un solo caso `Libre`; con estos muere.
    """
    c = ca.CRITERIOS[clave]
    assert c.nivel == ca.NIVEL_PERFIL and c.etiqueta == "A"
    assert not isinstance(c.resolucion, DeEnsayo)
    with pytest.raises(ValueError, match="sensibilidad"):
        ca._verificar_nivel(clave, replace(c, sensibilidad=None))


def test_m3_la_guardia_sigue_exigiendo_resolucion_al_a_de_perfil():
    """
    CAMBIADO EN N2 (se llamaba «…resolucion al [A] de perfil de ensayo»):
    con la regla 3 de vuelta al texto de d9b59f9, un [A] de perfil sin
    ventana se rechaza por la ventana antes de mirar la resolucion, y el
    caso del ensayo ya no existe. Lo que se sigue fijando es la otra mitad
    de la regla: con ventana y sin `resolucion`, tampoco entra.
    """
    c = replace(ca.CRITERIOS[CLAVE_MARGEN], resolucion=None)
    assert c.sensibilidad is not None
    with pytest.raises(ValueError, match="resolucion"):
        ca._verificar_nivel(CLAVE_MARGEN, c)


def test_m3_y_la_guardia_sigue_prohibiendo_la_ventana_al_de_ensayo():
    c = replace(ca.CRITERIOS[CLAVE_SATURADO], sensibilidad=(18.0, 22.0))
    # Desde N2 la rechaza primero la regla del [S] («un hecho de sitio no
    # tiene rango que elegir»); rotulado [A], la del `de_ensayo`.
    with pytest.raises(ValueError, match=r"\[S\] y declara sensibilidad"):
        ca._verificar_criterio(CLAVE_SATURADO, c)
    with pytest.raises(ValueError, match="de_ensayo"):
        ca._verificar_criterio(CLAVE_SATURADO, _como_a(c))


def _corrida_de_perfil_con_el_nivel_sobre_la_clave(tmp_path):
    """
    El cruce P1 de `test_ve2_flotacion` (DATOS DE PRUEBA): invert en el
    terreno natural (100.00), subrasante en 103.85. Con NF a 0.05 m y un
    margen de 3.00 m el nivel de diseño queda en 102.95, sobre la clave de
    cualquier escalon que la Fase 5 evalue primero (Ø 0.90 m: clave fisica
    hacia 101.0), de modo que V7 tiene que pesar relleno sumergido y lee el
    peso saturado.
    """
    import json as _json
    csv = tmp_path / "p1_nf_alto.csv"
    csv.write_text(
        "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,"
        "cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,"
        "ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,"
        "sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,"
        "cota_coronacion_canal\n"
        "P1,0+100,A,1.0,50,0.005,100.0,104.0,103.85,10,0,9.0,99.5,,,SM,"
        "0.05,,\n", encoding="utf-8")
    ext = tmp_path / "externos.json"
    ext.write_text(_json.dumps({"globales": {"luz_m": 3.0, "TW_m": 0.3}}),
                   encoding="utf-8")
    externos = cli.cargar_datos_externos(
        ext, {"luz_m": None, "TW_m": None, "longitud_m": None,
              "L_hidraulico_m": None, "categoria_tr": None})
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 3.0}):
        return servicio.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)


def test_m3_medido_la_corrida_de_perfil_lo_invoca_sin_diferir(tmp_path):
    """
    LA MEDIDA, no la opinion: la corrida `--alcance perfil` con la
    alternativa declarada invoca el criterio, y el bloqueo que deja NO esta
    diferido por el alcance. Por la segunda direccion de
    `tests/test_nivel_medido.py`, eso lo hace de perfil.
    """
    informe = _corrida_de_perfil_con_el_nivel_sobre_la_clave(tmp_path)
    assert CLAVE_SATURADO in informe.contexto.criterios_usados
    (p,) = informe.puntos
    del_saturado = [b for b in p.bloqueos if b.criterio == CLAVE_SATURADO]
    assert del_saturado, [b.criterio for b in p.bloqueos]
    assert not any(b.diferido_por_alcance for b in del_saturado)
    assert ca.CRITERIOS[CLAVE_SATURADO].nivel == ca.NIVEL_PERFIL


# ===========================================================================
# M4 · el margen estacional no entra negativo por la puerta
# ===========================================================================

def test_m4_la_ficha_del_margen_declara_su_signo():
    c = ca.CRITERIOS[CLAVE_MARGEN]
    assert c.no_negativo is True
    assert c.valor is None          # ningun valor de archivo cambia


def test_m4_ningun_otro_criterio_declara_signo():
    """El campo nace para este criterio; extenderlo es otra decision."""
    con_signo = sorted(k for k, c in ca.CRITERIOS.items() if c.no_negativo)
    assert con_signo == [CLAVE_MARGEN]


def test_m4_un_negativo_no_entra_por_el_archivo():
    c = replace(ca.CRITERIOS[CLAVE_MARGEN], valor=-0.10)
    with pytest.raises(ValueError, match="negativ"):
        ca._verificar_criterio(CLAVE_MARGEN, c)


def test_m4_un_negativo_no_entra_en_caliente():
    with pytest.raises(ValueError, match="negativ"):
        ca.verificar_declaracion(CLAVE_MARGEN, -0.10)
    with pytest.raises(ValueError, match="negativ"):
        ca.establecer_valor_dinamico(CLAVE_MARGEN, -0.10)
    assert not ca.declarado_en_caliente(CLAVE_MARGEN)


def test_m4_un_negativo_no_entra_por_la_cli():
    try:
        with pytest.raises((ValueError, SystemExit)):
            cli.declarar_criterios([f"{CLAVE_MARGEN}=-0.10"])
        assert not ca.declarado_en_caliente(CLAVE_MARGEN)
    finally:
        # Si la puerta lo dejara pasar, que no contamine los tests de despues.
        ca.quitar_valor_dinamico(CLAVE_MARGEN)


def test_m4_un_negativo_no_se_escribe_en_el_archivo(tmp_path):
    copia = tmp_path / "criterios_adoptados.py"
    original = Path(ca.__file__).read_text(encoding="utf-8")
    copia.write_text(original, encoding="utf-8")
    with pytest.raises(ValueError, match="negativ"):
        ca.escribir_valor_en_archivo(CLAVE_MARGEN, -0.10, ruta=str(copia))
    assert copia.read_text(encoding="utf-8") == original


@pytest.mark.parametrize("valor", [0, 0.0, 1.5])
def test_m4_el_cero_y_el_positivo_entran(valor):
    ca.verificar_declaracion(CLAVE_MARGEN, valor)


def test_m4_el_nan_no_entra():
    with pytest.raises(ValueError):
        ca.verificar_declaracion(CLAVE_MARGEN, math.nan)


def test_m4_el_signo_solo_se_declara_en_un_numero():
    """`no_negativo` sobre una categoria es una ficha mal escrita."""
    c = replace(ca.CRITERIOS[CLAVE_NIVEL], no_negativo=True)
    with pytest.raises(ValueError, match="no_negativo"):
        ca._verificar_criterio(CLAVE_NIVEL, c)

    # Tambien SIN VALOR (verificacion de las correcciones de VE-2, N7): la
    # ficha esta mal escrita aunque el criterio siga vacio. Un mutante que
    # cortara con `valor is None` antes de mirar la forma sobrevivia.
    vacio = replace(c, valor=None)
    with pytest.raises(ValueError, match="no_negativo"):
        ca._verificar_criterio(CLAVE_NIVEL, vacio)


def test_m4_la_segunda_linea_del_consumidor_se_queda():
    """
    Si un negativo llegara al consumidor por una via que esquiva la puerta
    (`con_valor`, la de los casos patron), M8 lo sigue rechazando.
    """
    with declarados({CLAVE_NIVEL: "nf_del_punto"}):
        with con_valor(CLAVE_MARGEN, -0.10,
                       motivo="segunda linea: esquivar la puerta a proposito"):
            with pytest.raises(DatoInvalidoError) as exc:
                _v7(_punto(NF_profundidad_m=0.50))
    assert exc.value.campo == CLAVE_MARGEN


def test_m4_con_cero_v7_sigue_evaluando_con_la_lectura():
    """El cero es la lectura misma: no detiene ni lo rechaza la puerta."""
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 0.0,
                     CLAVE_SATURADO: 20.0}):
        v = _v7(_punto(NF_profundidad_m=0.05))
    assert v is not None
    with declarados({CLAVE_NIVEL: "nf_del_punto"}):
        with pytest.raises(CriterioPendienteError):
            _v7(_punto(NF_profundidad_m=0.05))


# ===========================================================================
# N2 · el peso saturado no entra cero ni negativo por la puerta
# ===========================================================================

def test_n2_la_ficha_del_saturado_declara_su_signo():
    c = ca.CRITERIOS[CLAVE_SATURADO]
    assert c.positivo is True
    assert c.valor is None          # ningun valor de archivo cambia


def test_n2_ningun_otro_criterio_declara_positivo():
    # Desde VE-3 (ficha VE2-05) tambien la capacidad portante admisible,
    # que paso a [S] con el mismo campo: el censo crece por decision del
    # dueño, no en silencio.
    con_signo = sorted(k for k, c in ca.CRITERIOS.items() if c.positivo)
    assert con_signo == ["capacidad_portante_adm", CLAVE_SATURADO]


@pytest.mark.parametrize("valor", [0, 0.0, -20.0])
def test_n2_cero_y_negativo_no_entran_por_el_archivo(valor):
    c = replace(ca.CRITERIOS[CLAVE_SATURADO], valor=valor)
    with pytest.raises(ValueError, match="positivo"):
        ca._verificar_criterio(CLAVE_SATURADO, c)


@pytest.mark.parametrize("valor", [0, 0.0, -20.0])
def test_n2_cero_y_negativo_no_entran_en_caliente(valor):
    with pytest.raises(ValueError, match="positivo"):
        ca.verificar_declaracion(CLAVE_SATURADO, valor)
    with pytest.raises(ValueError, match="positivo"):
        ca.establecer_valor_dinamico(CLAVE_SATURADO, valor)
    assert not ca.declarado_en_caliente(CLAVE_SATURADO)


def test_n2_cero_no_entra_por_la_cli():
    try:
        with pytest.raises((ValueError, SystemExit)):
            cli.declarar_criterios([f"{CLAVE_SATURADO}=0"])
        assert not ca.declarado_en_caliente(CLAVE_SATURADO)
    finally:
        ca.quitar_valor_dinamico(CLAVE_SATURADO)


def test_n2_cero_no_se_escribe_en_el_archivo(tmp_path):
    copia = tmp_path / "criterios_adoptados.py"
    original = Path(ca.__file__).read_text(encoding="utf-8")
    copia.write_text(original, encoding="utf-8")
    with pytest.raises(ValueError, match="positivo"):
        ca.escribir_valor_en_archivo(CLAVE_SATURADO, 0.0, ruta=str(copia))
    assert copia.read_text(encoding="utf-8") == original


def test_n2_el_nan_no_entra_y_un_positivo_si():
    with pytest.raises(ValueError):
        ca.verificar_declaracion(CLAVE_SATURADO, math.nan)
    ca.verificar_declaracion(CLAVE_SATURADO, 19.5)


def test_n2_positivo_solo_se_declara_en_un_numero():
    c = replace(ca.CRITERIOS[CLAVE_NIVEL], positivo=True)
    with pytest.raises(ValueError, match="positivo"):
        ca._verificar_criterio(CLAVE_NIVEL, c)
    with pytest.raises(ValueError, match="positivo"):
        ca._verificar_criterio(CLAVE_NIVEL, replace(c, valor=None))
