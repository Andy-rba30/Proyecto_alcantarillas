"""
tests/test_ext2_multicelda_transicion.py
========================================
Tests de aceptacion de EXT-2: el cluster hidraulico A del dictamen de la
auditoria externa del 2026-09-19
(`docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md`, paso 2;
prompt EXT-2 de `docs/planes_mejora/07_CADENA_PROMPTS_EXT.md`).

Se escribieron primero EN ROJO (`xfail(strict=True)`) con la expectativa del
invariante o de la fuente -- nunca con la salida vigente como oraculo -- y el
xfail se retiro al corregir.

Lo que se comprueba, por ID:

    EXT-M-03  Un marco de N celdas resuelve M4 con Q/N (regla vinculante #3
              de `ruta_familia_c.md` §6). `ResultadoHidraulico` lleva el Q
              total del punto y, aparte, `Q_celda_m3s` y `numero_celdas`. El
              paso de Manning imprime el caudal con que M3 resolvio de
              verdad, y el reparto tiene su propio `PasoDeMemoria` colgado
              de F3.CELDAS. HDS-5 num. 5.4.3 (PDF 151) entra al registro
              como sosten del reparto.
    EXT-M-04  El extremo inferior de la recta de transicion (Forma 1) se
              evalua en q* = 3.5 con el H_c del caudal que corresponde a
              q* = 3.5, `H_c(Q_lo)`, y no con el del caudal real: la recta
              es una recta (segundas diferencias nulas) y el punto medio es
              la media exacta de los extremos (CP-5T, 1.107921425 m).
    PC-19     El oraculo del test de la recta (`test_M4_control`) deja de
              fijar el extremo movil; aqui se fija la lectura de la fuente.
    PC-06     `tirante_normal` devuelve None cuando Q >= Q_lleno, en las dos
              formas: el marco 2.00 x 1.50 con Q = 8.0 m3/s (banda 7.70-9.64
              donde el conducto va a presion) ya no publica un «tirante
              normal» de y/H = 0.86.
"""
import math

import pytest

from src.constantes_normativas import (KU_SI, K_MANNING_SI, Q_LIM_NO_SUMERGIDO,
                                   Q_LIM_SUMERGIDO)
from src.modelos import (ControlGobernante, FormaSeccion, RegimenEntrada,
                     SeccionCircular, SeccionRectangular, TipoMaterial)
from src.modulos import M4_control as M4
from src.modulos import MD
from src.modulos.M2_material import catalogo
from src.modulos.M3_hidraulica import resolver_manning, tirante_normal
from src.modulos.M4_control import (control_entrada, resolver_control,
                                tirante_critico)
from src.modulos.M5_verificaciones import v6_material_solido_arrastre
from src.normativa import registro as rn
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import (CP2_GEOMETRIA_MANNING, CP5D_FORMA2,
                                         CP5T_PUNTO_MEDIO_TRANSICION)
from tests.test_MD import _punto, _todo_cumple

# El marco de la aceptacion, con TRES celdas. Es el caso que la auditoria
# externa midio (M-03): Q = 9 m3/s, S = 0.004, L = 24 m, TW = 0.
CAJON_N3 = {
    "embocadura_cajon": "cajon_concreto_aletas_30_75",
    "n_manning_cajon": "concreto_afinado",
    "n_celdas_cajon": 3,
    "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
    "secciones_cajon_normalizadas": ((2.00, 1.50),),
}
Q_TOTAL = 9.0          # m3/s, del punto
Q_CELDA = 3.0          # m3/s, Q/N con N = 3
S_MARCO = 0.004        # m/m
L_MARCO = 24.0         # m
TW_LIBRE = 0.0         # m
HW_SALIDA_MULTICELDA = 1.045982117    # m, el numero del dictamen (M-03)
TOL_DORADO = 1e-9                     # los dorados llevan 9 decimales
# El Q_lleno del dictamen esta escrito con dos decimales (7.70 m3/s): la
# tolerancia es la del redondeo con que se cita, no una precision de calculo.
TOL_Q_LLENO_CITADO = 0.01             # m3/s
# Continuidad en los bordes de la ventana: la misma tolerancia con que
# `test_M4_control` la fijaba antes de EXT-2 (epsilon de 1e-7 en q*).
TOL_CONTINUIDAD = 1e-6                # m
CITA_REPARTO = "HDS5_3ED.5.4.3#REPARTO"
PDF_REPARTO = 151
CP5T = CP5T_PUNTO_MEDIO_TRANSICION


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


@pytest.fixture
def hds5(concreto):
    """Carta 'circular concreto, square edge w/headwall' de la Tabla A.1."""
    return concreto.hds5


def _marco():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO,
                    forma=FormaSeccion.RECTANGULAR)


def _disenar_marco_n3(registrar=None):
    with declarados(CAJON_N3):
        resultado, motivo = MD.disenar_material(
            _punto(), _marco(), Q=Q_TOTAL, S=S_MARCO, L=L_MARCO,
            TW=TW_LIBRE, verificar=_todo_cumple, registrar=registrar)
    assert resultado is not None, motivo
    return resultado


def _Q_para(q_estrella, seccion):
    """El Q que produce ese q* en la seccion."""
    return q_estrella * seccion.area_llena * math.sqrt(seccion.altura) / KU_SI


# ===========================================================================
# EXT-M-03 · multicelda: Q/N entra a M4, y la memoria lo dice
# ===========================================================================

def test_el_multicelda_se_dimensiona_con_Q_sobre_N_y_publica_los_dos_caudales():
    """
    El numero del dictamen: con Q/N = 3 m3/s el marco 2.00 x 1.50 da
    HW_salida = 1.045982117 m y gobierna la SALIDA. Con el Q total (lo que el
    codigo hacia) daba +113.8 % y cambiaba el control.

    `Q` sigue siendo el caudal del PUNTO -- sus tres lectores lo imprimen
    asi -- y los dos campos nuevos dicen con que caudal se resolvio.
    """
    r = _disenar_marco_n3().resultado_hidraulico
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.HW_salida == pytest.approx(HW_SALIDA_MULTICELDA, abs=TOL_DORADO)
    assert r.Q == pytest.approx(Q_TOTAL, rel=REL_TRANSPORTE)
    assert r.Q_celda_m3s == pytest.approx(Q_CELDA, rel=REL_TRANSPORTE)
    assert r.numero_celdas == 3


def test_las_tres_piezas_de_M4_reciben_el_caudal_de_la_celda(monkeypatch):
    """
    LA MUTACION QUE EL DICTAMEN PIDE MATAR: devolver el Q total a las piezas
    de M4. Se envuelven las tres -- critico, entrada, salida -- registrando
    el Q que reciben: ninguna puede ver 9.0.
    """
    recibidos = []

    def _espia(nombre):
        original = getattr(M4, nombre)

        def envuelta(*args, **kw):
            Q = kw["Q"] if "Q" in kw else args[0]
            recibidos.append((nombre, Q))
            return original(*args, **kw)
        return envuelta

    for nombre in ("tirante_critico", "control_entrada", "control_salida"):
        monkeypatch.setattr(M4, nombre, _espia(nombre))
    _disenar_marco_n3()
    assert {n for n, _ in recibidos} == {"tirante_critico", "control_entrada",
                                         "control_salida"}
    for nombre, Q in recibidos:
        assert Q == pytest.approx(Q_CELDA, rel=REL_TRANSPORTE), (
            f"{nombre} recibio Q = {Q}: la regla vinculante #3 dice Q/N")


def test_el_camino_sin_tirante_inyectado_tambien_reparte():
    """
    `resolver_control` con `normal=None` resolvia Manning con el Q total: con
    9 m3/s el marco no tiene tirante normal y devolvia None, cuando con Q/N
    si lo tiene. El reparto vive DENTRO de M4 y cubre los dos caminos.
    """
    with declarados(CAJON_N3):
        r = resolver_control(seccion=SeccionRectangular(2.00, 1.50),
                             Q=Q_TOTAL, S=S_MARCO, L=L_MARCO, TW=TW_LIBRE,
                             material=_marco(), normal=None)
    assert r is not None
    assert r.HW_salida == pytest.approx(HW_SALIDA_MULTICELDA, abs=TOL_DORADO)
    assert r.Q_celda_m3s == pytest.approx(Q_CELDA, rel=REL_TRANSPORTE)


def test_el_paso_de_manning_imprime_el_Q_con_que_M3_resolvio():
    """
    La memoria salia IRREPRODUCIBLE: imprimia Q = 9.0 junto a un y_n que solo
    da V*A = 3.0. El paso de Manning y el del critico sustituyen el caudal
    de la celda; el del punto se lee en el paso del reparto.
    """
    pasos = _disenar_marco_n3().resultado_hidraulico.pasos
    for fundamento in ("F4.MANNING", "F4.YC_RECT"):
        p = next(p for p in pasos if p.fundamento_id == fundamento)
        Q = next(m for m in p.sustitucion if m.simbolo == "Q")
        assert Q.valor == pytest.approx(Q_CELDA, rel=REL_TRANSPORTE), fundamento


def test_el_reparto_tiene_su_paso_colgado_de_F3_CELDAS():
    """
    El paso «Numero de celdas» de M2 adopta N; el del reparto, emitido por
    M4 con el MISMO fundamento, sustituye Q y N y da Q_celda. Sin el, la
    memoria adoptaba N y nunca decia con que caudal quedo cada barril.
    """
    pasos = _disenar_marco_n3().resultado_hidraulico.pasos
    # DOS pasos cuelgan de F3.CELDAS: el de M2 (adopta N; su resultado es la
    # frase «Q / N») y el del reparto (sustituye Q y N; su resultado es el
    # numero Q_celda). Se distinguen por el simbolo del resultado.
    con_fundamento = [p for p in pasos if p.fundamento_id == "F3.CELDAS"]
    assert len(con_fundamento) == 2
    reparto = [p for p in con_fundamento if p.resultado.simbolo == "Q_celda"]
    assert len(reparto) == 1
    simbolos = {m.simbolo: m.valor for m in reparto[0].sustitucion}
    assert simbolos["Q"] == pytest.approx(Q_TOTAL, rel=REL_TRANSPORTE)
    assert simbolos["N"] == 3
    assert reparto[0].resultado.simbolo == "Q_celda"
    assert reparto[0].resultado.valor == pytest.approx(Q_CELDA,
                                                       rel=REL_TRANSPORTE)
    assert CITA_REPARTO in reparto[0].citas_textuales
    # Y va ANTES de Manning: es lo primero que hay que saber para rehacer el
    # tirante normal de la celda.
    ids = [p.fundamento_id for p in pasos]
    assert pasos.index(reparto[0]) < ids.index("F4.MANNING")


def test_la_fila_hidraulica_de_la_tabla_de_diseno_dice_N_y_Q_celda():
    """
    LO QUE EL AUDITOR ADVERSARIAL DE EXT-2 ENCONTRO: la fila «Hidraulica» de
    la tabla de diseño de M11 imprimia el Q del punto junto a un y_n que solo
    transporta Q/N -- el defecto de M-03 mudado del paso de Manning al
    resumen --. Con N > 1 la fila dice N y Q_celda; con N = 1 no cambia nada
    (la linea base lo fija).
    """
    from cli import InformePunto
    from src.modulos import M11_reporte as M11
    resultado = _disenar_marco_n3()
    informe = InformePunto(punto=resultado.punto, resultado=resultado)
    html = M11._tabla_diseno(informe)
    assert "N = 3 celdas" in html
    assert "Q<sub>celda</sub> = 3.000 m3/s" in html
    assert "Q = 9.000 m3/s" in html


def test_la_circular_no_reparte_ni_imprime_reparto(concreto):
    """
    Un tubo es UNA celda por construccion del catalogo, no por decision: no
    invoca 'n_celdas_cajon', no emite el paso del reparto y sus dos campos
    nuevos llevan el default.
    """
    c = CP2_GEOMETRIA_MANNING
    r = resolver_control(seccion=SeccionCircular(c["D"]),
                         Q=c["Q_con_n_max_esperado"], S=c["S"], L=L_MARCO,
                         TW=TW_LIBRE, material=concreto)
    assert r is not None
    assert r.numero_celdas == 1
    assert r.Q_celda_m3s == pytest.approx(r.Q, rel=REL_TRANSPORTE)
    assert "F3.CELDAS" not in [p.fundamento_id for p in r.pasos]


def test_el_registro_sostiene_el_reparto_con_HDS5_5_4_3():
    """
    HDS-5 num. 5.4.3 «Multiple Barrels», pag. impresa 5.15 (PDF 151): «For
    multiple barrels with identical hydraulic characteristics, the total
    discharge is assumed to be divided equally among the barrels». Es el
    sosten de la regla vinculante #3 y no estaba en el registro.
    """
    reg = rn.construir()
    cita = reg.cita(CITA_REPARTO)
    assert cita.pagina_pdf == PDF_REPARTO
    assert cita.numeral == "5.4.3"
    assert "divided equally among the barrels" in cita.texto_literal.texto
    assert CITA_REPARTO in reg.fundamento("F3.CELDAS").citas


def test_V6_sigue_rechazando_el_multicelda():
    """
    NO ES UNA ACEPTACION NUEVA: fija lo que EXT-2 decide NO cambiar. V6 sigue
    siendo `celdas == 1` (Sec. 3.1, el Manual RECOMIENDA seccion unica ante
    arrastre) hasta que exista un dato de sitio sobre la capacidad de
    arrastre del cauce que permita decidir otra cosa. La ficha esta en
    `docs/decisiones_diferidas.md` (EXT-2-01).
    """
    with declarados(CAJON_N3):
        v = v6_material_solido_arrastre(material=_marco())
    assert not v.cumple
    assert "3 celda(s)" in v.valor_obtenido


# ===========================================================================
# EXT-M-04 / PC-19 · la recta de transicion, con H_c(Q_lo)
# ===========================================================================

def test_el_punto_medio_de_la_transicion_es_la_media_exacta_de_los_extremos(hds5):
    """CP-5T: en q* = 3.75 la recta vale (HW_lo + HW_hi)/2 = 1.107921425 m."""
    sec = SeccionCircular(CP5T["D"])
    r = control_entrada(Q=_Q_para(CP5T["q_estrella"], sec), seccion=sec,
                        S=CP5T["S"], hds5=hds5)
    assert r.regimen is RegimenEntrada.TRANSICION
    assert r.HW == pytest.approx(CP5T["HW_esperado"], abs=CP5T["tolerancia"])
    assert r.HW != pytest.approx(CP5T["HW_con_extremo_movil"],
                                 abs=CP5T["tolerancia"])


def test_la_recta_es_una_recta_en_toda_la_ventana(hds5):
    """
    Segundas diferencias nulas: HW(q*) es lineal entre 3.5 y 4.0. Con el
    extremo movil los incrementos iban de 20.8 a 5.6 mm por paso, y la
    memoria imprimia «recta» sobre una curva.
    """
    sec = SeccionCircular(CP5T["D"])
    paso = CP5T["paso_q_estrella"]
    n = round((Q_LIM_SUMERGIDO - Q_LIM_NO_SUMERGIDO) / paso)
    hw = [control_entrada(Q=_Q_para(Q_LIM_NO_SUMERGIDO + i * paso, sec),
                          seccion=sec, S=CP5T["S"], hds5=hds5).HW
          for i in range(n + 1)]
    segundas = [hw[i + 2] - 2 * hw[i + 1] + hw[i] for i in range(n - 1)]
    assert all(abs(d) < CP5T["tolerancia_linealidad"] for d in segundas), segundas


def test_la_continuidad_en_3_5_y_4_0_se_conserva(hds5):
    """
    La correccion mueve el interior de la ventana y NO los bordes: en 3.5 el
    caudal real ES Q_lo (H_c coincide), y en 4.0 el extremo superior no lleva
    H_c. Este test pasa antes y despues, y esta aqui para que siga pasando.
    """
    sec = SeccionCircular(CP5T["D"])
    epsilon = 1e-7
    for limite, signo in ((Q_LIM_NO_SUMERGIDO, +1), (Q_LIM_SUMERGIDO, -1)):
        dentro = control_entrada(Q=_Q_para(limite + signo * epsilon, sec),
                                 seccion=sec, S=CP5T["S"], hds5=hds5)
        borde = control_entrada(Q=_Q_para(limite, sec), seccion=sec,
                                S=CP5T["S"], hds5=hds5)
        assert dentro.regimen is RegimenEntrada.TRANSICION
        assert dentro.HW == pytest.approx(borde.HW, abs=TOL_CONTINUIDAD)


def test_el_control_de_entrada_publica_los_extremos_y_el_caudal_del_extremo(hds5):
    """
    `ControlEntrada.transicion` lleva Q_lo, H_c(Q_lo) y los dos extremos:
    sin ellos la memoria imprime un HW «por la recta» que el revisor no puede
    rehacer, porque no sabe entre que dos numeros se interpolo.
    """
    sec = SeccionCircular(CP5T["D"])
    r = control_entrada(Q=_Q_para(CP5T["q_estrella"], sec), seccion=sec,
                        S=CP5T["S"], hds5=hds5)
    t = r.transicion
    assert t is not None
    assert t.Q_lo == pytest.approx(CP5T["Q_lo_esperado"], abs=CP5T["tolerancia"])
    assert t.H_c_lo == pytest.approx(CP5T["H_c_lo_esperado"],
                                     abs=CP5T["tolerancia"])
    assert t.HW_lo == pytest.approx(CP5T["HW_lo_esperado"], abs=CP5T["tolerancia"])
    assert t.HW_hi == pytest.approx(CP5T["HW_hi_esperado"], abs=CP5T["tolerancia"])
    # Fuera de la ventana no hay recta, y el campo lo dice.
    fuera = control_entrada(Q=_Q_para(2.70, sec), seccion=sec, S=CP5T["S"],
                            hds5=hds5)
    assert fuera.transicion is None


def test_bajo_forma_2_no_hay_H_c_del_extremo_y_la_recta_no_se_mueve():
    """
    Solo la Forma 1 lleva H_c: la ec. (A.2) no lo tiene, de modo que el
    extremo inferior de la Forma 2 no cambia y `H_c_lo` queda vacio. El
    numero es el de CP-5D, fijado a mano en C3.
    """
    d = CP5D_FORMA2
    carta = M4.ConstantesHDS5(K=d["K"], M=d["M"], c=d["c"], Y=d["Y"],
                              Ks=d["Ks"], forma=d["forma"])
    sec = SeccionCircular(0.90)
    t = d["transicion"]
    r = control_entrada(Q=_Q_para(t["q_estrella"], sec), seccion=sec,
                        S=t["S"], hds5=carta)
    assert r.HW_sobre_D == pytest.approx(t["hw_sobre_D_esperado"],
                                         abs=t["tolerancia"])
    assert r.transicion is not None
    assert r.transicion.H_c_lo is None


def test_el_paso_F4_CONTROL_sustituye_los_extremos_en_la_transicion(hds5):
    """La sustitucion del paso 4.2 lleva Q_lo, H_c_lo, HW_lo y HW_hi."""
    import dataclasses
    sec = SeccionCircular(CP5T["D"])
    Q = _Q_para(CP5T["q_estrella"], sec)
    material = dataclasses.replace(catalogo(TipoMaterial.CONCRETO_REFORZADO),
                                   hds5=hds5)
    r = resolver_control(seccion=sec, Q=Q, S=CP5T["S"], L=L_MARCO,
                         TW=TW_LIBRE, material=material)
    de_entrada = next(p for p in r.pasos
                      if p.fundamento_id == "F4.CONTROL" and p.codigo == "4.2")
    simbolos = {m.simbolo: m.valor for m in de_entrada.sustitucion}
    for simbolo in ("Q_lo", "H_c_lo", "HW_lo", "HW_hi"):
        assert simbolo in simbolos, simbolo
    assert simbolos["HW_lo"] == pytest.approx(CP5T["HW_lo_esperado"],
                                              abs=CP5T["tolerancia"])


# ===========================================================================
# PC-06 · el tirante normal no existe cuando el conducto va a presion
# ===========================================================================

def _Q_lleno(seccion, n, S):
    return (K_MANNING_SI / n) * seccion.area_llena \
        * seccion.radio_hidraulico_lleno ** (2 / 3) * S ** 0.5


def test_el_marco_a_presion_no_tiene_tirante_normal():
    """
    Marco 2.00 x 1.50, n = 0.014, S = 0.004: Q_lleno = 7.70 m3/s y el Manning
    de lamina libre en y = H da 9.64. En la banda (7.70, 9.64) el bracket
    (0, H) encontraba una raiz y `tirante_normal` publicaba y/H = 0.86 para
    un conducto que fisicamente va a presion. Con Q = 8.0 la respuesta es
    None; con Q por debajo de Q_lleno, un tirante.
    """
    with declarados(CAJON_N3):
        marco = _marco()
    sec = SeccionRectangular(2.00, 1.50)
    n = marco.n_para_capacidad
    Q_lleno = _Q_lleno(sec, n, S_MARCO)
    assert Q_lleno == pytest.approx(7.70, abs=TOL_Q_LLENO_CITADO)
    assert tirante_normal(sec, 8.0, S_MARCO, n) is None
    assert tirante_normal(sec, Q_lleno, S_MARCO, n) is None      # el borde
    g = tirante_normal(sec, 0.9 * Q_lleno, S_MARCO, n)
    assert g is not None and g.y < sec.H


def test_la_circular_conserva_su_contrato_y_gana_el_mismo_techo(concreto):
    """
    En la circular el techo ya lo ponia el bracket: Q(theta_max) es el caudal
    a seccion llena. El caso patron CP-2 no se mueve, y el borde exacto
    Q = Q_lleno devuelve None en las dos formas por la misma guardia.
    """
    c = CP2_GEOMETRIA_MANNING
    sec = SeccionCircular(c["D"])
    g = tirante_normal(sec, c["Q_con_n_max_esperado"], c["S"], c["n_max"])
    assert g is not None
    assert g.y_sobre_D == pytest.approx(c["y_sobre_D"], abs=c["tolerancia_hidraulica"])
    Q_lleno = _Q_lleno(sec, c["n_max"], c["S"])
    assert tirante_normal(sec, Q_lleno, c["S"], c["n_max"]) is None
    assert tirante_normal(sec, 2 * Q_lleno, c["S"], c["n_max"]) is None
