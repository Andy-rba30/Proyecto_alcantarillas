# -*- coding: utf-8 -*-
"""
tests/test_pf1_hw_fuera_de_rango.py
===================================
La aceptacion de PF-1 (`docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md`),
que cierra PC-03: la carga a la entrada que la correccion por pendiente
Ks*S deja en cero o bajo cero (MAT-D10) deja de ser un descarte DEFINITIVO
del material y pasa a ser un VACIO DECLARABLE de perfil.

La clase de excepcion, argumentada en la ficha PF-1-01 de
`docs/decisiones_diferidas.md`: `CriterioPendienteError` sobre el criterio
[A] `hw_entrada_fuera_de_rango`, y no `MetodoNoEvaluableError`. La regla de
CLAUDE.md para un vacio de la hoja de ruta es exactamente esta --- entrada
con valor=None, etiqueta [A], y detener el calculo con excepcion ---, y lo
que distingue este caso de V1/V2 bajo control de salida (EXT-3) es que aqui
SI hay una adopcion que el proyectista puede tomar sentado: la energia
especifica critica H_c, un numero que el propio paso 4.2.1 ya calculo, como
piso cuando la ecuacion no entrega carga. Un metodo «no evaluable» es el que
no se resuelve declarando nada; este se resuelve declarando. EL PISO ACOTA
EL SIGNO: por debajo de S* la ecuacion sigue entregando su carga aunque sea
menor que H_c (lo midio el auditor adversarial: 0.035 m frente a 0.169 m a
S = 0.30), y el test de abajo lo fija para que la ficha no prometa mas.

LA MONOTONIA EN D NO ABRE OTRO DIAMETRO BAJO FORMA 1, y conviene decirlo
porque el prompt PF-1 lo escribio al reves: HWi/D DECRECE con D (bajan
H_c/D y q* a la vez, con Ks*S fijo), de modo que si la carta se cae en el
diametro minimo del catalogo ninguno mayor la levanta. Bajo Forma 2 no es
general (S* pasa a None cuando la rama cae en la (A.2)), y lo que acota el
alcance es `S_CAUCE_MAX`: con S <= 1.0 solo la Forma 1 no sumergida puede
dispararse; los dos tests del bloque 3 lo fijan. El descarte del material
entero era correcto en su alcance; lo que no era correcto es que fuera
definitivo y mudo (`Bloqueo.criterio = None`, invisible en la pestaña 4).
El test de la propiedad lo fija, y la ficha PF-1-01 deja la correccion.

Escritos primero EN ROJO con `xfail(strict=True)` por test (marcador
`rojo`) sobre el invariante, nunca sobre la salida actual; medidos antes de
tocar codigo y liberados al corregir.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src.constantes_normativas import KU_SI
from src.dominios import S_CAUCE_MAX
from src.modelos import (ConstantesHDS5, CriterioPendienteError,
                         DisenoNoFactibleError, SeccionCircular, TipoDeBloqueo,
                         TipoMaterial)
from src.modulos import M4_control as M4
from src.modulos.M2_material import catalogo
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures.casos_patron import CP5D_FORMA2

RAIZ = Path(__file__).resolve().parents[1]
# El marcador de rojo: se retira al corregir y la constancia queda arriba.
ROJO = pytest.mark.xfail(strict=True, reason="PF-1 (PC-03) todavia no ejecutado")
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"

CLAVE = "hw_entrada_fuera_de_rango"
ENERGIA_CRITICA = "energia_critica"
DESCARTAR = "descartar"

# EL CASO DE LA FICHA PC-03: D = 0.90 m (el minimo del catalogo, num.
# 4.1.1.3.4 a)), Q = 0.05 m3/s y S = 0.40 m/m, que supera el umbral
# analitico S* = 2*(H_c/D + K*(q*)^M) = 0.3770624 de la carta de concreto
# (docstring de `M4_control`, MAT-D10). La pendiente esta DENTRO del dominio
# fisico del dato: el punto de la ficha es que ningun dato esta mal.
D_MINIMO = 0.90
CASOS_DE_LA_FICHA = ((0.05, 0.40), (0.10, 0.55))

# Cuanto por encima de S* se pisa para que HWi/D quede bajo cero sin ruido
# de punto flotante, y cuanto por debajo para que quede sobre cero. Es un
# escalon de pendiente, no un valor de proyecto.
ESCALON_S = 1e-3
# Cuanto baja el fondo del receptor respecto del terreno en el CSV del caso:
# es geometria del fixture (un cruce empinado con salida libre), no un valor
# de proyecto, y medido: con 8 m el punto llega a MD y dimensiona.
CAIDA_RECEPTOR_M = 8.0
TW_DEL_CASO_M = 0.10


@pytest.fixture
def hds5():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO).hds5


@pytest.fixture
def _limpio():
    """El criterio queda como en el archivo al salir, declare lo que declare el test."""
    yield
    if ca.declarado_en_caliente(CLAVE):
        ca.quitar_valor_dinamico(CLAVE)


def _s_limite_forma_1(Q, D, hds5):
    """S* = 2*(H_c/D + K*(q*)^M), la formula del docstring, calculada aparte."""
    seccion = SeccionCircular(D)
    critico = M4.tirante_critico(Q, seccion)
    q_estrella = KU_SI * Q / (seccion.area_llena * math.sqrt(D))
    return (critico.H_c / D + hds5.K * q_estrella ** hds5.M) / (-hds5.Ks)


# ===========================================================================
# 1 - La clase: un vacio declarable, visible, con el par culpable
# ===========================================================================


@pytest.mark.parametrize("Q, S", CASOS_DE_LA_FICHA)
def test_pf1_la_carta_fuera_de_rango_es_un_vacio_declarable(hds5, Q, S, _limpio):
    assert 0 < S < S_CAUCE_MAX
    assert S > _s_limite_forma_1(Q, D_MINIMO, hds5), "el caso dejo de estar fuera de rango"
    with pytest.raises(CriterioPendienteError) as exc:
        M4.control_entrada(Q=Q, seccion=SeccionCircular(D_MINIMO), S=S, hds5=hds5)
    assert exc.value.clave == CLAVE
    assert not ca.declarado_en_caliente(CLAVE)
    texto = str(exc.value)
    # El par culpable y el limite, con la forma MAT-D13: quien lea el bloqueo
    # tiene que poder rehacer el caso y saber cuanto sobra de pendiente.
    assert f"Q={Q}" in texto and f"S={S}" in texto and f"D={D_MINIMO}" in texto
    assert "S*=" in texto



def test_pf1_el_limite_de_signo_es_el_analitico_y_control_entrada_lo_publica(hds5):
    Q = CASOS_DE_LA_FICHA[0][0]
    seccion = SeccionCircular(D_MINIMO)
    esperado = _s_limite_forma_1(Q, D_MINIMO, hds5)
    limite = M4.pendiente_limite_de_signo(Q=Q, seccion=seccion, hds5=hds5)
    assert limite == pytest.approx(esperado, rel=REL_TRANSPORTE)
    # Un escalon por debajo la carta entrega carga; uno por encima, no.
    entrada = M4.control_entrada(Q=Q, seccion=seccion, S=limite - ESCALON_S, hds5=hds5)
    assert entrada.HW > 0 and entrada.piso is None
    with pytest.raises(CriterioPendienteError):
        M4.control_entrada(Q=Q, seccion=seccion, S=limite + ESCALON_S, hds5=hds5)



def test_pf1_declarado_energia_critica_adopta_H_c_y_lo_publica(hds5, _limpio):
    Q, S = CASOS_DE_LA_FICHA[0]
    seccion = SeccionCircular(D_MINIMO)
    ca.establecer_valor_dinamico(CLAVE, ENERGIA_CRITICA)
    entrada = M4.control_entrada(Q=Q, seccion=seccion, S=S, hds5=hds5)
    assert entrada.HW == pytest.approx(entrada.critico.H_c, rel=REL_TRANSPORTE)
    assert entrada.HW_sobre_D == pytest.approx(entrada.critico.H_c / D_MINIMO,
                                               rel=REL_TRANSPORTE)
    piso = entrada.piso
    assert piso is not None
    assert piso.criterio == CLAVE and piso.adoptado == ENERGIA_CRITICA
    assert not piso.HW_sobre_D_formula > 0        # lo que la formula devolvia
    assert piso.S_limite == pytest.approx(_s_limite_forma_1(Q, D_MINIMO, hds5),
                                          rel=REL_TRANSPORTE)
    assert CLAVE in ca.criterios_usados()



def test_pf1_declarado_descartar_es_no_factible_con_el_par_y_el_limite(hds5, _limpio):
    Q, S = CASOS_DE_LA_FICHA[0]
    ca.establecer_valor_dinamico(CLAVE, DESCARTAR)
    with pytest.raises(DisenoNoFactibleError) as exc:
        M4.control_entrada(Q=Q, seccion=SeccionCircular(D_MINIMO), S=S, hds5=hds5)
    texto = str(exc.value)
    assert f"Q={Q}" in texto and f"S={S}" in texto and "S*=" in texto
    assert "Ks" in texto and str(hds5.Ks) in texto



def test_pf1_la_ficha_del_criterio_es_de_perfil_categorica_y_con_ventana():
    c = ca.CRITERIOS[CLAVE]
    assert c.valor is None and c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_PERFIL
    assert c.forma == ca.FORMA_CATEGORIA
    assert c.sensibilidad == (ENERGIA_CRITICA, DESCARTAR)
    assert c.resolucion is not None
    # La guardia de forma rechaza lo que no es del conjunto cerrado.
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE, "cero")
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE, 0.0)


# ===========================================================================
# 2 - Por el pipeline: el bloqueo se ve donde el revisor mira
# ===========================================================================

def _csv_de_un_punto(tmp_path, Q, S):
    """El punto A-02 del CSV de ejemplo con el (Q, S) de la ficha."""
    filas = list(csv.DictReader(CSV_EJEMPLO.open(encoding="utf-8")))
    fila = next(f for f in filas if f["id"] == "A-02")
    fila["id"], fila["Q_m3s"], fila["S_cauce"] = "PC-03", str(Q), str(S)
    # Con S = 0.40 el conducto cae varios metros entre sus dos bocas y M7 lo
    # tiende desde la SALIDA: con el fondo del receptor de A-02 (0.75 m bajo
    # el terreno) la clave de la entrada quedaba por encima de la subrasante
    # y el punto se detenia en la geometria, que no es lo que este archivo
    # mide. Se baja el receptor (`CAIDA_RECEPTOR_M`) y se declara un TW
    # chico, como en cualquier cruce empinado con salida libre.
    fila["cota_fondo_receptor"] = f"{float(fila['cota_terreno']) - CAIDA_RECEPTOR_M:.2f}"
    ruta = tmp_path / "pc03.csv"
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fila))
        w.writeheader()
        w.writerow(fila)
    return ruta


def _correr(ruta):
    externos = cli.cargar_datos_externos(None, dict(luz_m=2.75, TW_m=TW_DEL_CASO_M))
    return cli.correr(ruta, externos, alcance=cli.ALCANCE_PERFIL)



def test_pf1_el_bloqueo_viaja_con_criterio_y_la_pestana_4_lo_pinta(tmp_path, _limpio):
    Q, S = CASOS_DE_LA_FICHA[0]
    informe = _correr(_csv_de_un_punto(tmp_path, Q, S))
    punto = informe.puntos[0]
    assert not punto.dimensionado
    bloqueos = [b for b in punto.bloqueos if b.tipo is TipoDeBloqueo.CRITERIO_PENDIENTE
                and b.criterio == CLAVE]
    assert bloqueos, [(b.tipo, b.etapa) for b in punto.bloqueos]
    assert not bloqueos[0].diferido_por_alcance
    assert "S*=" in bloqueos[0].mensaje
    # Lo que la pestaña 4 y el bloque «criterios pendientes» de la CLI leen.
    tablero = {c.clave: c for c in cli.criterios_bloqueantes(informe)}
    assert CLAVE in tablero and "PC-03" in tablero[CLAVE].puntos
    assert not tablero[CLAVE].diferido
    volcado = cli.informe_json(informe)
    assert CLAVE in [c["clave"] for c in volcado["criterios"]["bloquearon"]]
    # No es un DisenoNoFactibleError: ningun material se descarto sin evaluar.
    assert not [b for b in punto.bloqueos if b.tipo is TipoDeBloqueo.DISENO_NO_FACTIBLE]



def test_pf1_declarado_en_caliente_el_punto_dimensiona_y_la_memoria_lo_declara(tmp_path, _limpio):
    Q, S = CASOS_DE_LA_FICHA[0]
    ca.establecer_valor_dinamico(CLAVE, ENERGIA_CRITICA)
    informe = _correr(_csv_de_un_punto(tmp_path, Q, S))
    punto = informe.puntos[0]
    assert punto.dimensionado, [(b.tipo, b.mensaje[:120]) for b in punto.bloqueos]
    assert CLAVE in informe.contexto.criterios_usados
    html = cli.memoria_html(informe, ruta_plantilla=cli.plantilla_por_alcance(cli.ALCANCE_PERFIL))
    assert CLAVE in html and ENERGIA_CRITICA in html
    assert "S*" in html
    # Y el JSON por punto distingue el piso de la ecuacion (auditor de PF-1):
    # HW_entrada_m = H_c no se puede leer como si lo hubiera dado la carta.
    diseno = cli.informe_json(informe)["puntos"][0]["diseno"]
    assert diseno["hw_entrada_piso"] == ENERGIA_CRITICA
    assert not diseno["hw_entrada_HW_sobre_D_formula"] > 0
    assert diseno["hw_entrada_S_limite_m_m"] > 0
    assert punto.resultado.resultado_hidraulico.piso_hw_entrada is not None


def test_pf1_bajo_el_limite_la_ecuacion_manda_aunque_de_menos_que_H_c(hds5, _limpio):
    """
    El piso acota el SIGNO y no impone H_c como minimo: por debajo de S* la
    carga es la de la ecuacion aunque sea menor que H_c, y el criterio no se
    invoca. Sin este test la ficha podia prometer un minimo que el codigo no
    aplica (auditor adversarial de PF-1, punto 2).
    """
    Q = CASOS_DE_LA_FICHA[0][0]
    seccion = SeccionCircular(D_MINIMO)
    limite = M4.pendiente_limite_de_signo(Q=Q, seccion=seccion, hds5=hds5)
    ca.establecer_valor_dinamico(CLAVE, ENERGIA_CRITICA)
    entrada = M4.control_entrada(Q=Q, seccion=seccion, S=limite * 0.8, hds5=hds5)
    assert entrada.piso is None
    assert 0 < entrada.HW < entrada.critico.H_c
    assert CLAVE not in ca.criterios_usados()


# ===========================================================================
# 3 - La correccion del prompt: HWi/D decrece con D
# ===========================================================================


@pytest.mark.parametrize("Q", [0.05, 0.10, 0.30])
def test_pf1_el_limite_de_signo_no_crece_con_D_y_por_eso_el_descarte_es_del_material(hds5, Q):
    """
    Si la carta se cae en el D minimo, ninguno mayor la levanta: S*(D) no
    crece con D. Es lo que hace correcto el descarte del material entero
    bajo «descartar», y lo que el prompt PF-1 tenia al reves.
    """
    limites = [M4.pendiente_limite_de_signo(Q=Q, seccion=SeccionCircular(D), hds5=hds5)
               for D in (0.90, 1.20, 1.50, 2.00, 2.40)]
    for menor, mayor in zip(limites, limites[1:]):
        assert mayor <= menor + REL_TRANSPORTE * menor


def test_pf1_bajo_forma_2_el_limite_no_es_monotono_y_no_alcanza_el_dominio():
    """
    La excepcion que el auditor adversarial midio: con una carta de Forma 2
    un D mayor puede llevar la rama a la (A.2), sin Ks*S, y S* deja de
    existir (None). Y el alcance real de todo el bloque: dentro del dominio
    del dato (S <= S_CAUCE_MAX) esa carta nunca se cae, porque en la rama
    sumergida y en la transicion S* queda muy por encima.
    """
    carta = ConstantesHDS5(**{k: CP5D_FORMA2[k] for k in ("K", "M", "c", "Y", "Ks", "forma")})
    Q = 2.0
    limites = [M4.pendiente_limite_de_signo(Q=Q, seccion=SeccionCircular(D), hds5=carta)
               for D in (0.90, 1.20, 1.50, 2.00, 2.40)]
    assert None in limites and any(x is not None for x in limites)
    for D in (0.90, 1.20, 1.50, 2.00, 2.40):
        for Q_i in (0.05, 0.10, 0.30, 1.0, 2.0, 3.5):
            limite = M4.pendiente_limite_de_signo(Q=Q_i, seccion=SeccionCircular(D), hds5=carta)
            assert limite is None or limite > S_CAUCE_MAX
