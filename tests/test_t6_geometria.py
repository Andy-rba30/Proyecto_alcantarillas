"""
tests/test_t6_geometria.py
==========================
Aceptacion de T-6 de la cadena T (geometria): INF-5.1.18, INF-3.3.3 y la
parte de M7 de INF-3.2.7.

Los numeros esperados NO salen de la salida del programa: salen de la
geometria hecha a mano sobre el punto A-01 del fixture (ancho 9.60 m, rasante
44.20, terreno 42.10, esviaje 15 grados, S = 0.006, talud 2.0 H:V) y de lo
que cada fuente dice, leido contra su pagina:

  1. Fondo de entrada. La columna `cota_fondo_entrada` gana cuando viene;
     cuando falta rige el terreno adoptado, y entonces la memoria avisa con la
     frase de la cadena y 7.A marca su delta como provisional.
  2. Longitud por extremo (HDS-5 3a ed., num. 2.2.4 b. y Figura 2.4, pag.
     impresa 2.8): cada talud baja hasta el fondo del conducto en SU extremo,
     y la salida queda S*L mas baja. La formula anterior se conserva como
     caso particular y la memoria dice cual se uso. Pasos con formula
     sustituida para la pendiente, el factor, L, la caida y la cota de
     salida, el encaje a la clave (HDS-5 num. 3.3.5) y G2.
  3. G2 con desnivel minimo de entrega, criterio [A] con ventana (0, 0.30).
  4. `esviaje_max_grados` con valor (45, ventana 45-60) y como AVISO.
  5. La pendiente adoptada con sus tres origenes.

MEDIDO EN ROJO: este archivo se corrio contra el arbol anterior a T-6
(`87d1ce7`, el commit de T-0) antes de darlo por aceptacion; el recuento esta
en el informe de la sesion. Los tests que valen antes y despues se nombran
`..._invariante`.
"""
from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import servicio
from src.modelos import (DatoFaltanteError, DatoInvalidoError, Familia,
                         PuntoCritico, TipoDeVeredicto, TipoMaterial)
from src import modelos
from src.modulos import M7_geometria as M7
from src.modulos import M11_reporte as M11
from src.modulos.M0_carga import cargar_puntos
from src.modulos.M2_material import catalogo, espesor_pared
from src.normativa import registro
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures.casos_patron import CP_T6_LONGITUD_POR_EXTREMO as CP
from tests.apoyo.criterios import con_valor

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"

# Los datos de A-01, escritos aqui para que la cuenta se pueda rehacer.
ANCHO, RASANTE, TERRENO = 9.60, 44.20, 42.10
TALUD, S_A01, ESVIAJE_A01 = 2.0, 0.006, 15.0
COS15 = math.cos(math.radians(ESVIAJE_A01))
H_EJE = RASANTE - TERRENO                     # 2.10 m
# L = [9.60 + 2.0 * (2.10 + 2.10)] / (cos 15 - 2.0 * 0.006) = 18.0 / 0.95393
L_POR_EXTREMO = (ANCHO + TALUD * 2 * H_EJE) / (COS15 - TALUD * S_A01)
# L = (9.60 + 2 * 2.0 * 2.10) / cos 15 = 18.0 / 0.96593: la formula anterior
L_SIMETRICA = (ANCHO + 2 * TALUD * H_EJE) / COS15
# Tolerancias con nombre. ABS: la cuenta a mano y el programa hacen la misma
# aritmetica en doble precision y difieren, a lo sumo, en el orden de las
# operaciones. TOL_CUENTA: el redondeo a cuatro decimales con que la cuenta
# se escribe en el docstring (18.8694).
ABS = 1e-9
TOL_CUENTA = 1e-4
TOL_ROTULO = 5e-3        # un numero escrito con dos o tres decimales en un texto


def _igual(valor):
    """Un valor que solo se transporta (dato, criterio): sin aritmetica."""
    return pytest.approx(valor, rel=REL_TRANSPORTE, abs=REL_TRANSPORTE)
AVISO = ("fondo de entrada adoptado igual al terreno de plataforma: medir en "
         "el cauce")

CLAVE_METODO = "metodo_longitud_conducto"
CLAVE_DESNIVEL = "desnivel_minimo_entrega_m"
CLAVE_ESVIAJE = "esviaje_max_grados"
CLAVES_DE_T2 = ("pendiente_minima_conducto", "pendiente_maxima_conducto")


@pytest.fixture(autouse=True)
def _limpio():
    """Ningun test deja una declaracion en caliente de sus tres criterios."""
    yield
    for clave in (CLAVE_METODO, CLAVE_DESNIVEL, CLAVE_ESVIAJE):
        if clave in ca.CRITERIOS:
            ca.quitar_valor_dinamico(clave)


def _punto(**cambios) -> PuntoCritico:
    base = dict(
        id="A-01", progresiva_km=0.380, progresiva_display="0+380",
        familia=Familia.A, Q_m3s=1.167, area_ha=850.0, S_cauce=S_A01,
        cota_terreno=TERRENO, cota_rasante=RASANTE, cota_subrasante=44.05,
        cbr_subrasante=8.5, esviaje_grados=ESVIAJE_A01,
        ancho_plataforma=ANCHO, cota_fondo_receptor=41.30,
        Q_receptor_m3s=None, cota_TW=None, sucs_fundacion="SM",
        NF_profundidad_m=None)
    base.update(cambios)
    return PuntoCritico(**base)


def _resultado(S=S_A01, HW=1.0):
    from src.modelos import ControlGobernante, ResultadoHidraulico
    return ResultadoHidraulico(
        y_normal=0.60, y_critico=0.40, V_erosion=1.5, V_sedimentacion=1.2,
        Q=1.0, S=S, HW_entrada=HW, HW_salida=0.20,
        control_gobernante=ControlGobernante.ENTRADA)


def _geometria(punto=None, **kw):
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    from src.modelos import SeccionCircular
    punto = punto or _punto()
    return M7.compatibilidad_geometrica(
        punto=punto, material=concreto, seccion=SeccionCircular(D=0.90),
        resultado=kw.pop("resultado", _resultado()), **kw)


def _correr(alcance=cli.ALCANCE_PERFIL, externos=EXTERNOS):
    ext = cli.cargar_datos_externos(
        externos, {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
                   "L_hidraulico_m": None, "categoria_tr": None})
    return servicio.correr(CSV, ext, alcance=alcance)


def _valor(paso, simbolo):
    for m in paso.sustitucion:
        if m.simbolo == simbolo:
            return m.valor
    raise AssertionError(f"el paso {paso.codigo} no sustituye «{simbolo}»: "
                         f"{[m.simbolo for m in paso.sustitucion]}")


# ===========================================================================
# 1. Fondo de entrada: el dato medido gana; el adoptado avisa (INF-5.1.18)
# ===========================================================================

def test_el_fondo_medido_gana_y_no_avisa():
    """Con la columna llena: cota MEDIDA, sin aviso y 7.A sin «provisional»."""
    geo = _geometria(_punto(cota_fondo_entrada=41.60))
    assert geo.cota_entrada.medida and geo.cota_entrada.valor == _igual(41.60)
    assert geo.cota_entrada.aviso == ""
    assert geo.tamizado.provisional is False
    assert "PROVISIONAL" not in geo.tamizado.mensaje
    assert AVISO not in geo.avisos


def test_el_fondo_adoptado_igual_al_terreno_avisa_con_la_frase_de_la_cadena():
    geo = _geometria()
    assert not geo.cota_entrada.medida
    assert geo.cota_entrada.valor == _igual(TERRENO)  # la regla sigue
    assert geo.cota_entrada.aviso == AVISO
    assert AVISO in geo.avisos


def test_7A_marca_el_delta_de_rasante_como_provisional():
    """Factible o no, el mensaje de 7.A dice que el numero es provisional."""
    geo = _geometria()
    assert geo.tamizado.provisional is True
    assert "PROVISIONAL" in geo.tamizado.mensaje and AVISO in geo.tamizado.mensaje
    corto = _geometria(_punto(cota_rasante=43.30, cota_subrasante=43.15))
    assert not corto.tamizado.factible and corto.tamizado.delta_rasante_m > 0
    assert "no factible -> subir rasante" in corto.tamizado.mensaje
    assert "PROVISIONAL" in corto.tamizado.mensaje
    g1 = corto.verificaciones[0]
    assert g1.codigo == "G1" and AVISO in g1.paso.nota_del_proyecto


def test_el_fondo_medido_bajo_el_terreno_baja_la_rasante_minima_lo_mismo():
    """
    INF-5.1.18: con el fondo real 0.60 m bajo el terreno, las dos condiciones
    de 7.A bajan 0.60 m. Es lo que hace «provisional» al delta adoptado.
    """
    adoptado = _geometria().tamizado
    medido = _geometria(_punto(cota_fondo_entrada=TERRENO - 0.60)).tamizado
    assert adoptado.cota_rasante_min - medido.cota_rasante_min == pytest.approx(
        0.60, abs=ABS)


def test_el_aviso_llega_a_la_memoria_al_json_y_al_volcado():
    informe = _correr()
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert a01.geometria is not None
    volcado = cli.informe_json(informe)
    g = next(p for p in volcado["puntos"] if p["id"] == "A-01")["geometria"]
    assert AVISO in g["avisos"] and g["tamizado"]["provisional"] is True
    html = M11.memoria_de_punto(a01)
    assert AVISO in html
    assert "PROVISIONAL" in html


def test_la_memoria_no_llama_adoptada_a_una_cota_medida(tmp_path):
    """El parrafo de la Fase 7 decia «adoptada ... no es cota medida» siempre."""
    texto = CSV.read_text(encoding="utf-8").splitlines()
    cabecera = texto[0].split(",")
    fila = texto[1].split(",")
    fila[cabecera.index("cota_fondo_entrada")] = "41.60"
    csv = tmp_path / "puntos.csv"
    csv.write_text("\n".join([texto[0], ",".join(fila)]) + "\n", encoding="utf-8")
    ext = cli.cargar_datos_externos(
        None, {"luz_m": 2.75, "TW_m": 0.3, "longitud_m": None,
               "L_hidraulico_m": None, "categoria_tr": None})
    informe = servicio.correr(csv, ext, alcance=cli.ALCANCE_PERFIL)
    a01 = informe.puntos[0]
    assert a01.geometria is not None and a01.geometria.cota_entrada.medida
    html = M11.memoria_de_punto(a01)
    assert "<b>medida</b>" in html
    assert "no es cota medida" not in html
    assert AVISO not in html


# ===========================================================================
# 2. Longitud por extremo y pasos de memoria (INF-3.3.3)
# ===========================================================================

def test_el_criterio_del_metodo_es_A_de_perfil_con_la_ventana_de_los_dos():
    c = ca.CRITERIOS[CLAVE_METODO]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.forma == ca.FORMA_CATEGORIA
    assert set(c.sensibilidad) == {"terraplen_simetrico", "por_extremo"}
    assert c.valor in c.sensibilidad
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE_METODO, "a_ojo")


def test_longitud_por_extremo_de_A01_contra_la_cuenta_a_mano():
    """18.0 / (cos 15 - 0.012) = 18.869 m."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    lc = M7.longitud_del_conducto(_punto())
    assert lc.metodo is modelos.MetodoLongitud.POR_EXTREMO
    assert L_POR_EXTREMO == pytest.approx(18.8694, abs=TOL_CUENTA)   # la cuenta
    assert lc.longitud == pytest.approx(L_POR_EXTREMO, abs=ABS)
    assert M7.longitud_conducto(_punto()) == pytest.approx(L_POR_EXTREMO, abs=ABS)


def test_la_geometria_por_extremo_cierra_sobre_la_seccion_del_cruce():
    """
    La identidad que DEFINE el metodo: L*cos(esviaje) = ancho + la proyeccion
    de cada talud, cada una con SU altura, y la salida S*L bajo la entrada.
    """
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    lc = M7.longitud_del_conducto(_punto())
    caida = S_A01 * lc.longitud
    assert lc.cota_referencia_entrada == _igual(TERRENO)
    assert lc.cota_referencia_salida == pytest.approx(TERRENO - caida, abs=ABS)
    assert lc.altura_entrada == pytest.approx(H_EJE, abs=ABS)
    assert lc.altura_salida == pytest.approx(H_EJE + caida, abs=ABS)   # mas alta
    assert lc.proyeccion_entrada == pytest.approx(TALUD * H_EJE, abs=ABS)
    assert lc.proyeccion_salida == pytest.approx(TALUD * (H_EJE + caida), abs=ABS)
    assert lc.longitud * COS15 == pytest.approx(
        ANCHO + lc.proyeccion_entrada + lc.proyeccion_salida, abs=ABS)
    assert lc.semilongitud_entrada + lc.semilongitud_salida == pytest.approx(
        lc.longitud, abs=ABS)
    assert lc.semilongitud_salida > lc.semilongitud_entrada


def test_el_terraplen_simetrico_es_la_formula_anterior():
    """(9.60 + 2*2.0*2.10)/cos 15 = 18.635 m: la L de A-01 antes de T-6."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "terraplen_simetrico")
    lc = M7.longitud_del_conducto(_punto())
    assert lc.metodo is modelos.MetodoLongitud.TERRAPLEN_SIMETRICO
    assert L_SIMETRICA == pytest.approx(18.6350, abs=TOL_CUENTA)
    assert lc.longitud == pytest.approx(L_SIMETRICA, abs=ABS)
    assert lc.altura_entrada == pytest.approx(H_EJE, abs=ABS)
    assert lc.altura_salida == pytest.approx(H_EJE, abs=ABS)
    # No lee la pendiente: un punto sin S_cauce tambien la calcula.
    assert M7.longitud_conducto(_punto(S_cauce=None)) == pytest.approx(
        L_SIMETRICA, abs=ABS)


def test_el_simetrico_es_el_caso_particular_del_por_extremo():
    """Sin caida (S = 0), fondo en el terreno y sin bombeo, las dos coinciden."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    horizontal = modelos.PendienteAdoptada(
        valor=0.0, origen=modelos.OrigenPendiente.DECLARADA, S_cauce=S_A01,
        S_declarada=0.0, S_minima=None, S_maxima=None,
        procedencia="prueba: conducto horizontal")
    lc = M7.longitud_del_conducto(_punto(), pendiente=horizontal)
    assert lc.longitud == pytest.approx(L_SIMETRICA, abs=ABS)


def test_el_por_extremo_ve_el_fondo_medido_y_el_simetrico_no():
    """
    Con el cauce 0.60 m bajo el terreno, cada talud baja 0.60 m mas:
    L crece en talud*2*0.60/(cos - talud*S). El metodo anterior no lo veia.
    """
    hondo = _punto(cota_fondo_entrada=TERRENO - 0.60)
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    esperado = (ANCHO + TALUD * 2 * (H_EJE + 0.60)) / (COS15 - TALUD * S_A01)
    assert M7.longitud_conducto(hondo) == pytest.approx(esperado, abs=ABS)
    assert esperado - L_POR_EXTREMO == pytest.approx(
        TALUD * 2 * 0.60 / (COS15 - TALUD * S_A01), abs=ABS)
    ca.establecer_valor_dinamico(CLAVE_METODO, "terraplen_simetrico")
    assert M7.longitud_conducto(hondo) == pytest.approx(L_SIMETRICA, abs=ABS)


def test_el_bombeo_baja_los_dos_bordes_y_acorta_la_longitud():
    """Bombeo 2 % sobre medio ancho: 0.096 m por borde, 2*2.0*0.096 = 0.384 m."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    lc = M7.longitud_del_conducto(_punto(), bombeo=0.02)
    assert lc.cota_borde_entrada == pytest.approx(RASANTE - 0.096, abs=ABS)
    assert lc.cota_borde_salida == pytest.approx(RASANTE - 0.096, abs=ABS)
    esperado = (ANCHO + TALUD * 2 * (H_EJE - 0.096)) / (COS15 - TALUD * S_A01)
    assert lc.longitud == pytest.approx(esperado, abs=ABS)
    assert L_POR_EXTREMO - lc.longitud == pytest.approx(
        0.384 / (COS15 - TALUD * S_A01), abs=ABS)
    simbolos = [m.simbolo for m in lc.pasos[-1].sustitucion]
    assert "bombeo" in simbolos and "peralte" not in simbolos


def test_el_peralte_no_cambia_la_longitud_y_si_cada_extremo():
    """Giro alrededor del eje: sube un borde lo que baja el otro."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    plano = M7.longitud_del_conducto(_punto())
    lc = M7.longitud_del_conducto(_punto(), peralte=0.04)
    assert lc.longitud == pytest.approx(plano.longitud, abs=ABS)
    assert lc.cota_borde_entrada == pytest.approx(RASANTE + 0.192, abs=ABS)
    assert lc.cota_borde_salida == pytest.approx(RASANTE - 0.192, abs=ABS)
    assert lc.altura_entrada - plano.altura_entrada == pytest.approx(0.192, abs=ABS)
    assert lc.altura_salida - plano.altura_salida == pytest.approx(-0.192, abs=ABS)
    assert lc.semilongitud_entrada > plano.semilongitud_entrada
    # con signo contrario, el borde alto es el de la salida
    al_reves = M7.longitud_del_conducto(_punto(), peralte=-0.04)
    assert al_reves.cota_borde_salida == pytest.approx(RASANTE + 0.192, abs=ABS)


def test_la_pendiente_que_alcanza_al_talud_no_tiene_longitud():
    """talud*S >= cos(esviaje): el talud de salida no alcanza al conducto."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    # La pendiente tiene que venir DECLARADA: la del cauce ya llega acotada a
    # la banda adoptada (0.10 de archivo), y con ella 2.0*0.10 < cos 15.
    punto = _punto()
    with pytest.raises(DatoInvalidoError) as exc:
        M7.longitud_del_conducto(                          # 2.0*0.60 > cos 15
            punto, pendiente=M7.pendiente_adoptada(punto, S_declarada=0.60))
    assert "talud" in exc.value.motivo and "0.6" in exc.value.motivo
    # justo por debajo sigue habiendo longitud, enorme y finita: se VE
    assert M7.longitud_conducto(
        punto, pendiente=M7.pendiente_adoptada(punto, S_declarada=0.45)) > 100


def test_un_borde_de_plataforma_bajo_el_fondo_es_dato_invalido():
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    with pytest.raises(DatoInvalidoError) as exc:
        M7.longitud_del_conducto(_punto(), bombeo=0.5)     # baja 2.40 m > 2.10
    assert "borde de la plataforma" in exc.value.motivo


# ---------------------------------------------------------------------------
# Lo que dejo el auditor adversarial de T-6
# ---------------------------------------------------------------------------

def test_dorado_a_mano_de_la_longitud_por_extremo():
    """
    CP-T6 (tests/fixtures/casos_patron.py): la aritmetica esta escrita alli.
    Aqui se rehace SIN la formula cerrada -- por la iteracion de punto fijo
    de la identidad geometrica -- y se compara el modulo contra el dorado.
    """
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    tol = CP["tolerancia"]
    # la iteracion: L <- (ancho + proy_entrada + talud*(H + S*L)) / cos
    H = CP["cota_rasante"] - CP["cota_terreno"]
    L = CP["longitud_formula_anterior"]
    for _ in range(12):
        L = (CP["ancho_plataforma"] + CP["talud"] * H
             + CP["talud"] * (H + CP["S"] * L)) / CP["cos_esviaje"]
    assert L == pytest.approx(CP["longitud_esperada"], abs=tol)
    lc = M7.longitud_del_conducto(_punto())
    assert lc.longitud == pytest.approx(CP["longitud_esperada"], abs=tol)
    assert lc.proyeccion_entrada == pytest.approx(
        CP["proyeccion_entrada_esperada"], abs=tol)
    assert lc.proyeccion_salida == pytest.approx(
        CP["proyeccion_salida_esperada"], abs=tol)
    geo = _geometria()
    assert geo.caida == pytest.approx(CP["caida_esperada"], abs=tol)
    assert geo.cota_salida == pytest.approx(CP["cota_salida_esperada"], abs=tol)
    # la formula anterior queda a 0.234 m: el dorado la separa
    assert abs(CP["longitud_formula_anterior"] - lc.longitud) > 0.2


def test_dorado_a_mano_con_peralte_con_fondo_medido_y_con_bombeo():
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    tol = CP["tolerancia"]
    peraltado = M7.longitud_del_conducto(_punto(), peralte=CP["peralte"])
    assert peraltado.longitud == pytest.approx(
        CP["longitud_con_peralte_esperada"], abs=tol)
    assert peraltado.cota_borde_entrada == pytest.approx(
        CP["cota_borde_entrada_con_peralte"], abs=tol)
    assert peraltado.cota_borde_salida == pytest.approx(
        CP["cota_borde_salida_con_peralte"], abs=tol)
    assert peraltado.semilongitud_entrada == pytest.approx(
        CP["semilongitud_entrada_con_peralte"], abs=tol)
    assert peraltado.semilongitud_salida == pytest.approx(
        CP["semilongitud_salida_con_peralte"], abs=tol)
    medido = _geometria(_punto(
        cota_fondo_entrada=CP["cota_fondo_entrada_medida"]))
    assert medido.longitud == pytest.approx(
        CP["longitud_con_fondo_medido_esperada"], abs=tol)
    assert medido.cota_salida == pytest.approx(
        CP["cota_salida_con_fondo_medido_esperada"], abs=tol)
    bombeado = M7.longitud_del_conducto(_punto(), bombeo=CP["bombeo"])
    assert bombeado.longitud == pytest.approx(
        CP["longitud_con_bombeo_esperada"], abs=tol)


def test_bombeo_y_peralte_a_la_vez_son_dato_invalido_y_nombran_el_par():
    """
    Auditor de T-6: se SUMABAN (A-01 con 0.02 y 0.04 daba 18.467 m). Una
    seccion tiene bombeo o peralte: DG-2018 304.05 y 304.06.
    """
    for metodo in ("por_extremo", "terraplen_simetrico"):
        ca.establecer_valor_dinamico(CLAVE_METODO, metodo)
        with pytest.raises(DatoInvalidoError) as exc:
            M7.longitud_del_conducto(_punto(), bombeo=0.02, peralte=0.04)
        assert "bombeo" in exc.value.campo and "peralte" in exc.value.campo
        assert "304.05" in exc.value.motivo and "304.06" in exc.value.motivo
    with pytest.raises(DatoInvalidoError):
        M7.longitud_declarada(_punto(), 20.0, bombeo=0.02, peralte=-0.04)
    # un cero declarado NO cuenta: es como se anula el bombeo en una curva
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    solo_peralte = M7.longitud_del_conducto(_punto(), peralte=0.04)
    con_cero = M7.longitud_del_conducto(_punto(), bombeo=0.0, peralte=0.04)
    assert con_cero.longitud == pytest.approx(solo_peralte.longitud, abs=ABS)
    assert con_cero.longitud == pytest.approx(L_POR_EXTREMO, abs=ABS)


def test_exigir_transversales_compatibles_solo_rechaza_el_par_no_nulo():
    """La regla sola, que comparten M7 y la carga de datos externos."""
    for par in ((None, None), (0.02, None), (None, -0.04), (0.0, 0.04),
                (0.02, 0.0), (0.0, 0.0)):
        M7.exigir_transversales_compatibles(*par, "A-01")      # no lanza
    for par in ((0.02, 0.04), (0.02, -0.04), (0.001, 0.001)):
        with pytest.raises(DatoInvalidoError) as exc:
            M7.exigir_transversales_compatibles(*par, "A-01")
        assert exc.value.id_punto == "A-01"


@pytest.mark.parametrize("contenido", [
    {"globales": {"bombeo": 0.02, "peralte": 0.04}},
    {"puntos": {"A-01": {"bombeo": 0.02, "peralte": 0.04}}},
    {"globales": {"bombeo": 0.02}, "puntos": {"A-02": {"peralte": -0.04}}},
    {"globales": {"peralte": 0.04}, "puntos": {"A-02": {"bombeo": 0.02}}},
])
def test_el_par_bombeo_peralte_se_rechaza_al_cargar_tambien_por_globales(
        tmp_path, contenido):
    ruta = tmp_path / "ext.json"
    ruta.write_text(json.dumps(contenido))
    with pytest.raises(DatoInvalidoError) as exc:
        cli.cargar_datos_externos(ruta, {"luz_m": 2.75})
    assert "bombeo" in exc.value.campo and "peralte" in exc.value.campo


def test_el_punto_en_curva_anula_el_bombeo_global_con_cero(tmp_path):
    ruta = tmp_path / "ext.json"
    ruta.write_text(json.dumps({
        "globales": {"bombeo": 0.02, "TW_m": 0.3},
        "puntos": {"A-02": {"bombeo": 0.0, "peralte": 0.04}}}))
    informe = _correr(externos=ruta)
    a01, a02 = informe.puntos[0], informe.puntos[1]
    assert a01.longitud_calculada.bombeo == _igual(0.02)
    assert a01.longitud_calculada.peralte is None
    assert a02.longitud_calculada.peralte == _igual(0.04)
    assert a02.longitud_calculada.cota_borde_entrada > \
        a02.longitud_calculada.cota_borde_salida


@pytest.mark.parametrize("clave, valor", [
    ("bombeo", -0.5), ("bombeo", -0.02), ("bombeo", 2.0), ("peralte", 4.0),
    ("peralte", -4.0), ("bombeo", float("nan")), ("peralte", float("inf")),
    ("bombeo", True), ("peralte", "0.04"),
])
def test_la_segunda_linea_de_M7_rechaza_la_transversal_invalida(clave, valor):
    """Auditor de T-6: bombeo = -0.5 llamado directo daba 28.93 m."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    with pytest.raises(DatoInvalidoError) as exc:
        M7.longitud_del_conducto(_punto(), **{clave: valor})
    assert exc.value.campo == clave


def test_la_plataforma_horizontal_se_avisa_con_su_sensibilidad():
    """
    Sin bombeo ni peralte la plataforma se toma horizontal, y eso se dice:
    cada 1 % de bombeo acorta talud*ancho/(cos - talud*S) centimetros
    (2.0 * 9.60 / 0.953926 = 20.1 en A-01; un 2 % son 0.40 m).
    """
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    lc = M7.longitud_del_conducto(_punto())
    # dos avisos: el fondo ADOPTADO, que la longitud por extremo consume, y
    # la plataforma horizontal
    assert lc.avisos[0] == AVISO and len(lc.avisos) == 2
    assert "plataforma tomada horizontal" in lc.avisos[1]
    assert "20.1 cm" in lc.avisos[1]
    con_2 = M7.longitud_del_conducto(_punto(), bombeo=0.02)
    assert lc.longitud - con_2.longitud == pytest.approx(
        2 * 20.1 / 100, abs=TOL_ROTULO)
    assert con_2.avisos == (AVISO,)
    assert M7.longitud_del_conducto(_punto(), peralte=0.04).avisos == (AVISO,)
    # con el fondo MEDIDO y el bombeo declarado no queda nada que avisar
    medido = _punto(cota_fondo_entrada=TERRENO - 0.50)
    assert M7.longitud_del_conducto(medido, bombeo=0.02).avisos == ()
    # llega a 7.B (una sola vez cada uno), a la nota del paso, al JSON y a
    # la memoria
    geo = _geometria()
    assert geo.avisos == lc.avisos
    assert "plataforma tomada horizontal" in geo.pasos[2].nota_del_proyecto
    informe = _correr()
    volcado = cli.informe_json(informe)
    g = next(p for p in volcado["puntos"] if p["id"] == "A-01")["geometria"]
    assert any("plataforma tomada horizontal" in a for a in g["avisos"])
    b01 = next(p for p in informe.puntos if p.punto.id == "B-01")
    assert "plataforma tomada horizontal" in M11.memoria_de_punto(b01)


def test_una_transversal_declarada_que_se_descarta_lo_dice():
    """Con el metodo simetrico o con la longitud declarada, no en silencio."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "terraplen_simetrico")
    lc = M7.longitud_del_conducto(_punto(), bombeo=0.02)
    assert lc.longitud == pytest.approx(L_SIMETRICA, abs=ABS)
    assert len(lc.avisos) == 1 and "NO aplicada" in lc.avisos[0]
    assert "bombeo = 0.02" in lc.avisos[0]
    assert "NO aplicada" in lc.pasos[-1].nota_del_proyecto
    assert M7.longitud_del_conducto(_punto()).avisos == ()
    declarada = _geometria(longitud=14.0, peralte=0.04)
    assert any("NO aplicada" in a and "peralte = 0.04" in a
               for a in declarada.avisos)
    assert "NO aplicada" in declarada.pasos[2].nota_del_proyecto


def test_una_transversal_con_longitud_declarada_se_avisa_en_la_corrida(tmp_path):
    ruta = tmp_path / "ext.json"
    ruta.write_text(json.dumps({
        "globales": {"TW_m": 0.3},
        "puntos": {"A-01": {"longitud_m": 18.0, "bombeo": 0.02}}}))
    informe = _correr(externos=ruta)
    a01 = informe.puntos[0]
    assert a01.geometria is not None
    assert a01.geometria.longitud == _igual(18.0)
    assert any("NO aplicada" in a for a in a01.geometria.avisos)


def test_el_fondo_adoptado_declara_el_sesgo_del_eje_en_el_paso_de_la_longitud():
    """
    'cota_terreno' es el terreno EN EL EJE. Con el fondo adoptado, el metodo
    ancla ahi la entrada; para un lecho de pendiente S que pasara por esa
    cota en el eje:
        aguas arriba  (4.80 + 2.0*2.10) / (cos 15 + 0.012) = 9.2031 m
        aguas abajo   (4.80 + 2.0*2.10) / (cos 15 - 0.012) = 9.4347 m
        L = 18.638 m, 0.232 m menos que los 18.869 del metodo.
    """
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    L_eje = (4.80 + TALUD * H_EJE) / (COS15 + TALUD * S_A01) \
        + (4.80 + TALUD * H_EJE) / (COS15 - TALUD * S_A01)
    assert L_eje == pytest.approx(18.638, abs=TOL_ROTULO)
    nota = M7.longitud_del_conducto(_punto()).pasos[-1].nota_del_proyecto
    assert "18.638 m" in nota and "+0.232 m" in nota
    assert "EJE" in nota and "cota_fondo_entrada" in nota
    # con el fondo MEDIDO no hay sesgo que declarar
    medido = M7.longitud_del_conducto(_punto(cota_fondo_entrada=41.50))
    assert "EJE de la via" not in medido.pasos[-1].nota_del_proyecto


@pytest.mark.parametrize("grados", [-10.0, -89.0, -0.001, float("nan")])
def test_un_esviaje_negativo_llamado_directo_es_dato_invalido(grados):
    """
    Auditor de T-6: -89 grados daba factor 57.3, 3301 m de conducto y G3 en
    «cumple». El dominio de M7 es el de M0, [0, 90).
    """
    punto = _punto(esviaje_grados=grados)
    for llamada in (M7.factor_esviaje, M7.g3_esviaje,
                    M7.longitud_del_conducto):
        with pytest.raises(DatoInvalidoError) as exc:
            llamada(punto)
        assert exc.value.campo == "esviaje_grados"
    assert M7.factor_esviaje(_punto(esviaje_grados=0.0)) == _igual(1.0)


def test_el_error_del_denominador_nombra_el_par_esviaje_pendiente():
    """cos(60) = 0.5 = 2.0 * 0.25: el mismo S tiene longitud con menos esviaje."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    punto = _punto(esviaje_grados=60.0)
    declarada = M7.pendiente_adoptada(punto, S_declarada=0.26)
    with pytest.raises(DatoInvalidoError) as exc:
        M7.longitud_del_conducto(punto, pendiente=declarada)
    assert "esviaje_grados" in exc.value.campo
    assert "S_conducto" in exc.value.campo
    assert "esviaje" in exc.value.motivo and "pendiente" in exc.value.motivo
    assert M7.longitud_conducto(replace(punto, esviaje_grados=15.0),
                                pendiente=declarada) > 0


def test_la_longitud_a_la_clave_es_cota_superior_de_la_de_entre_cabezales():
    """
    Auditor de T-6: el docstring decia «cota inferior». Un cabezal 0.30 m
    sobre la clave acorta 2*2.0*0.30/0.953926 = 1.258 m MAS: 13.42 < 14.68.
    """
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    geo = _geometria()
    con_cabezal_mas_alto = geo.longitud_a_la_clave \
        - 2 * TALUD * 0.30 / (COS15 - TALUD * S_A01)
    assert geo.longitud_a_la_clave == pytest.approx(14.68, abs=TOL_ROTULO)
    assert con_cabezal_mas_alto == pytest.approx(13.42, abs=TOL_ROTULO)
    assert con_cabezal_mas_alto < geo.longitud_a_la_clave < geo.longitud
    doc = M7.longitud_a_la_clave.__doc__
    assert "COTA SUPERIOR" in doc and "COTA INFERIOR" not in doc


def test_los_textos_no_atribuyen_a_la_fuente_la_eleccion_del_proyecto():
    """Medir al fondo es del proyecto; la cita sostiene la superposicion."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    eleccion = M7.longitud_del_conducto(_punto()).pasos[-1].elecciones[0]
    assert "eleccion del proyecto" in eleccion.por_que
    assert "cota superior" in eleccion.por_que
    nota = registro.construir().cita("HDS5_3ED.2.2.4#LONGITUD").nota
    assert "Pavement Elevation" in nota
    assert "CARA SUPERIOR DEL BARRIL" in nota
    ficha = ca.CRITERIOS[CLAVE_METODO]
    assert "no de la fuente" in ficha.justificacion
    assert "0.9925" in ficha.justificacion and "1.0002" in ficha.justificacion
    fundamento = registro.construir().fundamento("F7.ESVIAJE_MAX")
    assert "no gira" in fundamento.por_que
    assert "no se elige" not in registro.construir().fundamento(
        "F7.LONGITUD").por_que
    assert "inventar un valor normativo" in M7.factor_esviaje.__doc__   # citado
    assert "adopcion declarada" in M7.factor_esviaje.__doc__


def test_el_HW_de_salida_de_A01_con_la_longitud_a_la_clave_es_el_que_se_cita():
    """
    El numero que la ficha y la hoja de ruta dan para decir que la cota
    superior de L no es el lado seguro: con L al fondo 0.9925 m, con L a la
    clave 1.0002 m (7.7 mm mas), y gobierna la entrada con 1.042 m.
    """
    informe = _correr()
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    h = a01.resultado.resultado_hidraulico
    assert h.HW_salida == pytest.approx(0.9925, abs=TOL_CUENTA)
    assert h.HW_entrada == pytest.approx(1.0420, abs=TOL_CUENTA)
    # a mano: dHW/dL = friccion por metro - S, con R = D/4 y seccion llena
    V = 1.167 / (math.pi / 4 * 0.90 ** 2)
    por_metro = 19.63 * 0.013 ** 2 / (0.90 / 4) ** (4 / 3) * V ** 2 / (2 * 9.81)
    dL = a01.geometria.longitud_a_la_clave - a01.geometria.longitud
    HW_clave = h.HW_salida + (por_metro - S_A01) * dL
    assert HW_clave == pytest.approx(1.0002, abs=TOL_CUENTA)
    assert HW_clave < h.HW_entrada            # sigue gobernando la entrada


def test_un_metodo_que_burla_la_puerta_lo_rechaza_el_consumidor():
    with con_valor(CLAVE_METODO, "a_ojo", motivo="guardia de M7 tras la puerta"):
        with pytest.raises(DatoInvalidoError) as exc:
            M7.longitud_del_conducto(_punto())
    assert CLAVE_METODO in str(exc.value)


def test_7B_emite_los_cinco_pasos_con_formula_cita_y_sustitucion():
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    geo = _geometria()
    # REESCRITO EN T-10, declarandolo: entre 7.B.3 y 7.B.4 va el 7.B.3b, el
    # reparto por extremo (altura del terraplen en la salida, proyeccion de
    # los taludes y semilongitudes) que el JSON publicaba y la memoria no.
    # Los cinco de T-6 siguen, en su orden; la sustitucion del 7.B.3b se
    # rehace a mano en tests/test_t10_memoria.py.
    assert [p.codigo for p in geo.pasos] == ["7.B.1", "7.B.2", "7.B.3",
                                             "7.B.3b", "7.B.4", "7.B.5"]
    reg = registro.construir()
    for p in geo.pasos:
        assert p.formula.strip() and p.por_que.strip(), p.codigo
        assert p.sustitucion, p.codigo
        assert all(m.procedencia.strip() for m in p.sustitucion), p.codigo
        assert reg.cita(p.formula_cita_id).pagina_pdf > 0, p.codigo
        assert p.fundamento_id.startswith("F7."), p.codigo


def test_el_paso_de_la_longitud_se_rehace_con_su_propia_sustitucion():
    """«Formula sustituida»: con los numeros que el paso imprime sale su L."""
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    geo = _geometria(_punto(cota_fondo_entrada=41.70))
    p = geo.pasos[2]
    L = ((_valor(p, "ancho") + _valor(p, "talud")
          * (_valor(p, "H_entrada") + _valor(p, "H_salida0")))
         / (_valor(p, "cos(esviaje)") - _valor(p, "talud") * _valor(p, "S")))
    assert p.resultado.valor == pytest.approx(L, abs=ABS)
    assert geo.longitud == pytest.approx(L, abs=ABS)
    assert "por_extremo" in [e.valor for e in p.elecciones]
    assert p.elecciones[0].clave_criterio == CLAVE_METODO
    assert "terraplen simetrico" in p.nota_del_proyecto      # dice cuanto daria
    # el factor y la cota de salida, igual
    factor = geo.pasos[1]
    assert factor.resultado.valor == pytest.approx(
        1 / math.cos(math.radians(_valor(factor, "esviaje"))), abs=ABS)
    # REESCRITO EN T-10 (por codigo y no por posicion: entre 7.B.3 y 7.B.4
    # va ahora el 7.B.3b del reparto por extremo).
    salida = next(x for x in geo.pasos if x.codigo == "7.B.4")
    assert _valor(salida, "caida") == pytest.approx(
        _valor(salida, "S") * _valor(salida, "L"), abs=ABS)
    assert salida.resultado.valor == pytest.approx(
        _valor(salida, "cota_entrada") - _valor(salida, "caida"), abs=ABS)
    assert salida.resultado.valor == pytest.approx(geo.cota_salida, abs=ABS)
    assert geo.caida == pytest.approx(S_A01 * geo.longitud, abs=ABS)


def test_la_memoria_dice_que_metodo_se_uso_en_los_dos_casos():
    for metodo, rotulo in (("por_extremo", "por extremo"),
                           ("terraplen_simetrico", "terraplen simetrico")):
        ca.establecer_valor_dinamico(CLAVE_METODO, metodo)
        geo = _geometria()
        paso_L = geo.pasos[2]
        assert rotulo in paso_L.que
        assert paso_L.elecciones[0].valor == metodo
        assert geo.longitud_calculada.metodo.value == metodo
    # el simetrico no tiene encaje a la clave: su referencia es el terreno
    assert geo.longitud_a_la_clave is None
    assert [p.codigo for p in geo.pasos] == ["7.B.1", "7.B.2", "7.B.3", "7.B.4"]


def test_una_longitud_declarada_no_aplica_el_metodo_y_lo_dice():
    usados_antes = set(ca.criterios_usados())
    ca.reiniciar_usos()
    geo = _geometria(longitud=14.0)
    assert geo.longitud == _igual(14.0)
    assert geo.longitud_calculada.metodo is modelos.MetodoLongitud.DECLARADA
    assert geo.proyeccion_taludes == pytest.approx(14.0 * COS15 - ANCHO, abs=ABS)
    assert CLAVE_METODO not in ca.criterios_usados()
    assert "declarada" in geo.pasos[2].que
    assert geo.longitud_a_la_clave is None
    del usados_antes
    with pytest.raises(ValueError):
        _geometria(longitud=14.0,
                   longitud_calculada=M7.longitud_del_conducto(_punto()))


def test_longitud_declarada_envuelve_el_dato_sin_calcularlo():
    """`M7.longitud_declarada`: la proyeccion es la que esa L IMPLICA."""
    lc = M7.longitud_declarada(_punto(), 20.0, origen="plano de la seccion")
    assert lc.metodo is modelos.MetodoLongitud.DECLARADA
    assert lc.longitud == _igual(20.0)
    assert lc.proyeccion_taludes == pytest.approx(20.0 * COS15 - ANCHO, abs=ABS)
    assert lc.altura_entrada is None and lc.talud is None
    paso_L = lc.pasos[-1]
    assert _valor(paso_L, "longitud_m") == _igual(20.0)
    assert "plano de la seccion" in paso_L.sustitucion[0].procedencia
    assert not paso_L.elecciones           # el metodo no se aplico


def test_el_encaje_a_la_clave_contra_la_cuenta_a_mano():
    """
    HDS-5 3.3.5: elegida la seccion, se encaja. Con cabezal a la clave cada
    talud deja de bajar c = D + espesor de pared.
    """
    ca.establecer_valor_dinamico(CLAVE_METODO, "por_extremo")
    geo = _geometria()
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    c = 0.90 + espesor_pared(concreto, 0.90)
    esperado = (ANCHO + TALUD * (2 * H_EJE - 2 * c)) / (COS15 - TALUD * S_A01)
    assert geo.longitud_a_la_clave == pytest.approx(esperado, abs=ABS)
    assert geo.longitud_a_la_clave < geo.longitud
    # REESCRITO EN T-10: por codigo (el 7.B.3b corre las posiciones).
    encaje = next(x for x in geo.pasos if x.codigo == "7.B.5")
    assert encaje.formula_cita_id == "HDS5_3ED.3.3.5#ENCAJE"
    assert _valor(encaje, "c") == pytest.approx(c, abs=ABS)
    assert encaje.umbral is None and encaje.veredicto is None   # sin tolerancia
    # la longitud del diseño NO se sustituye por la de la clave
    assert geo.longitud == pytest.approx(L_POR_EXTREMO, abs=ABS)
    assert geo.cota_salida == pytest.approx(TERRENO - S_A01 * L_POR_EXTREMO, abs=ABS)


def test_la_longitud_de_7B_es_la_misma_que_uso_el_diseno():
    informe = _correr()
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert a01.longitud_calculada is not None
    assert a01.geometria.longitud_calculada is a01.longitud_calculada
    assert a01.geometria.longitud == _igual(a01.longitud.valor)
    assert a01.longitud.valor == pytest.approx(L_POR_EXTREMO, abs=ABS)
    assert "por_extremo" in a01.longitud.origen
    volcado = cli.informe_json(informe)
    g = next(p for p in volcado["puntos"] if p["id"] == "A-01")["geometria"]
    assert g["longitud_calculo"]["metodo"] == "por_extremo"
    assert g["longitud_calculo"]["altura_terraplen_salida_m"] > \
        g["longitud_calculo"]["altura_terraplen_entrada_m"]
    assert g["longitud_a_la_clave_m"] < g["longitud_m"]


def test_ningun_diametro_del_fixture_se_mueve_con_ningun_metodo():
    """PARADA (c) de la cadena: A-01 y A-02 siguen en 0.90 m, con los dos."""
    for metodo in ("por_extremo", "terraplen_simetrico"):
        ca.establecer_valor_dinamico(CLAVE_METODO, metodo)
        informe = _correr()
        adoptado = {p.punto.id: (p.resultado.seccion.etiqueta()
                                 if p.dimensionado else None)
                    for p in informe.puntos}
        assert adoptado == {"A-01": "Ø 0.90 m", "A-02": "Ø 0.90 m",
                            "B-01": None, "C-01": None}, metodo
        # REESCRITO EN LAS CORRECCIONES DE T-9 (decision C del dueño): la VB1
        # de B-01 --su tramo de cuneta desde A-02 mide 530 m-- no cumple, y
        # no tiene que ver con la longitud del conducto ni con un diametro;
        # lo que esta prueba fija es que ninguna verificacion de la seccion
        # incumpla con ninguno de los dos metodos.
        for p in informe.puntos:
            del_conducto = [v for v in p.incumplidas()
                            if v.codigo not in ("VB1", "VB2")]
            assert not del_conducto, (metodo, p.punto.id)


def test_declarar_el_metodo_anterior_reproduce_la_longitud_anterior():
    ca.establecer_valor_dinamico(CLAVE_METODO, "terraplen_simetrico")
    informe = _correr()
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert a01.longitud.valor == pytest.approx(L_SIMETRICA, abs=ABS)
    assert a01.geometria.cota_salida == pytest.approx(
        TERRENO - S_A01 * L_SIMETRICA, abs=ABS)


def test_la_memoria_imprime_los_pasos_de_7B_y_la_traza_de_la_gui_tambien():
    from src import traza_punto
    informe = _correr()
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    html = M11.memoria_de_punto(a01)
    assert M11.TITULO_TRAZA_GEOMETRIA in html
    assert "por_extremo" in html
    for p in a01.geometria.pasos:
        assert p.que in html, p.codigo
    traza = traza_punto.traza_del_punto(a01)
    titulos = [s.titulo for s in traza.secciones]
    assert M11.TITULO_TRAZA_GEOMETRIA in titulos
    # un punto que NO dimensiona publica igual la longitud con que corrio
    b01 = next(p for p in informe.puntos if p.punto.id == "B-01")
    assert not b01.dimensionado and b01.geometria is None
    pasos, previa = M11.traza_geometria(b01)
    assert previa and [p.codigo for p in pasos] == ["7.B.2", "7.B.3"]
    assert M11.TITULO_TRAZA_GEOMETRIA_PREVIA in M11.memoria_de_punto(b01)
    # y todos estan entre los pasos que el anexo enlaza
    impresos = {id(p) for p in M11.pasos_impresos(informe)}
    assert all(id(p) in impresos for p in a01.geometria.pasos)


@pytest.mark.parametrize("clave, bruto, valido", [
    ("bombeo", 0.02, True), ("bombeo", 0.0, True), ("bombeo", -0.02, False),
    ("bombeo", 2.0, False),                 # 2.0 es el porcentaje del DG-2018
    ("peralte", 0.04, True), ("peralte", -0.04, True), ("peralte", 0.0, True),
    ("peralte", 4.0, False), ("peralte", -4.0, False), ("peralte", True, False),
])
def test_bombeo_y_peralte_entran_como_datos_externos_con_su_dominio(
        tmp_path, clave, bruto, valido):
    ruta = tmp_path / "ext.json"
    ruta.write_text(json.dumps({"puntos": {"A-01": {clave: bruto}}}))
    banderas = {"luz_m": 2.75, "TW_m": 0.3, "longitud_m": None,
                "L_hidraulico_m": None, "categoria_tr": None}
    if not valido:
        with pytest.raises(DatoInvalidoError):
            cli.cargar_datos_externos(ruta, banderas)
        return
    ext = cli.cargar_datos_externos(ruta, banderas)
    assert ext.valor("A-01", clave) == _igual(bruto)
    assert ext.valor("A-02", clave) is None            # sin valor por defecto


def test_el_bombeo_declarado_llega_a_la_longitud_del_punto(tmp_path):
    ruta = tmp_path / "ext.json"
    ruta.write_text(json.dumps({"globales": {"TW_m": 0.3},
                                "puntos": {"A-01": {"bombeo": 0.02}}}))
    informe = _correr(externos=ruta)
    a01, a02 = informe.puntos[0], informe.puntos[1]
    esperado = (ANCHO + TALUD * 2 * (H_EJE - 0.096)) / (COS15 - TALUD * S_A01)
    assert a01.longitud.valor == pytest.approx(esperado, abs=ABS)
    assert a01.longitud_calculada.bombeo == _igual(0.02)
    assert a02.longitud_calculada.bombeo is None


# ===========================================================================
# 3. G2 con desnivel minimo de entrega
# ===========================================================================

def test_el_desnivel_de_entrega_es_A_de_perfil_con_ventana_0_a_030():
    c = ca.CRITERIOS[CLAVE_DESNIVEL]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.forma == ca.FORMA_FLOAT
    assert tuple(c.sensibilidad) == _igual((0.0, 0.30))
    assert c.sensibilidad[0] <= c.valor <= c.sensibilidad[1]
    assert "4.1.1.3.3" in c.fuente
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE_DESNIVEL, 0.50)


def test_g2_aplica_el_desnivel_declarado():
    """cota_salida >= cota_fondo_receptor + desnivel, con el margen exacto."""
    punto = _punto(cota_fondo_receptor=41.30)
    ca.establecer_valor_dinamico(CLAVE_DESNIVEL, 0.0)
    assert M7.g2_cota_salida(punto=punto, cota_salida_m=41.30).cumple
    assert not M7.g2_cota_salida(punto=punto, cota_salida_m=41.29).cumple
    ca.establecer_valor_dinamico(CLAVE_DESNIVEL, 0.30)
    assert not M7.g2_cota_salida(punto=punto, cota_salida_m=41.55).cumple
    limite = M7.g2_cota_salida(punto=punto, cota_salida_m=41.60)
    assert limite.cumple                                   # frontera inclusiva
    assert limite.valor_admisible == pytest.approx(41.60, abs=ABS)
    assert limite.criterio_aplicado == CLAVE_DESNIVEL
    assert CLAVE_DESNIVEL in ca.criterios_usados()


def test_g2_lleva_paso_con_formula_sustituida_y_umbral_sin_cifra_de_fuente():
    ca.establecer_valor_dinamico(CLAVE_DESNIVEL, 0.10)
    v = M7.g2_cota_salida(punto=_punto(), cota_salida_m=41.987)
    p = v.paso
    assert p is not None and p.codigo == "G2" and p.fundamento_id == "F7.ENTREGA"
    assert _valor(p, "desnivel_minimo") == _igual(0.10)
    assert _valor(p, "cota_fondo_receptor") == _igual(41.30)
    assert p.umbral.valor == pytest.approx(41.40, abs=ABS)
    assert p.umbral.criterio_aplicado == CLAVE_DESNIVEL
    # Auditor de T-6: el umbral es un [A] y NO toma caracter EXIGENCIA del
    # numeral de la pendiente, que no habla de la entrega. Su cita es la
    # lamina, que tipifica (DEFINICION) y no acota.
    assert p.umbral.cita_id == "MC_HHD.LAMINA_01"
    assert p.umbral.caracter == "DEFINICION"
    assert "EXIGENCIA" not in p.umbral.caracter
    assert "SIN CIFRA" in p.umbral.aplicacion
    assert "ADOPCION" in p.umbral.aplicacion
    assert p.veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert p.veredicto.margen == pytest.approx(41.987 - 41.40, abs=ABS)
    assert p.resultado.valor == pytest.approx(0.687, abs=ABS)


def test_un_desnivel_negativo_que_burla_la_puerta_se_rechaza():
    with con_valor(CLAVE_DESNIVEL, -0.10, motivo="guardia de G2 tras la puerta"):
        with pytest.raises(DatoInvalidoError):
            M7.g2_cota_salida(punto=_punto(), cota_salida_m=41.9)


def test_ningun_valor_de_la_ventana_cambia_el_veredicto_de_g2_en_el_fixture():
    """PARADA (c) en espiritu: 0.0 y 0.30 dan el mismo veredicto en A-01 y A-02."""
    extremos = ca.CRITERIOS[CLAVE_DESNIVEL].sensibilidad
    for desnivel in extremos:
        ca.establecer_valor_dinamico(CLAVE_DESNIVEL, desnivel)
        informe = _correr()
        veredicto = {
            p.punto.id: next(v.cumple for v in p.geometria.verificaciones
                             if v.codigo == "G2")
            for p in informe.puntos if p.geometria is not None}
        assert veredicto == {"A-01": True, "A-02": True}, desnivel


def test_g2_incumplida_no_pide_subir_la_rasante():
    ca.establecer_valor_dinamico(CLAVE_DESNIVEL, 0.30)
    geo = _geometria(_punto(cota_fondo_receptor=41.80))
    assert [v.codigo for v in geo.verificaciones_incumplidas] == ["G2"]
    assert geo.delta_rasante_cm is None
    assert geo.desnivel_entrega == pytest.approx(geo.cota_salida - 41.80, abs=ABS)


# ===========================================================================
# 4. Esviaje maximo: valor [A] y aviso, no bloqueo
# ===========================================================================

def test_el_esviaje_maximo_tiene_valor_A_en_la_ventana_45_60():
    c = ca.CRITERIOS[CLAVE_ESVIAJE]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert tuple(c.sensibilidad) == _igual((45.0, 60.0))
    assert c.valor is not None and 45.0 <= c.valor <= 60.0
    assert not c.opcional
    assert "5.4.2" in c.fuente and "4.1.1.3.2" in c.fuente
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE_ESVIAJE, 70.0)


def test_el_esviaje_sobre_el_maximo_es_aviso_y_el_punto_sigue():
    maximo = ca.CRITERIOS[CLAVE_ESVIAJE].valor
    punto = _punto(esviaje_grados=maximo + 5.0)
    # el factor se calcula igual: ya no hay DatoInvalidoError
    assert M7.factor_esviaje(punto) == pytest.approx(
        1 / math.cos(math.radians(maximo + 5.0)), abs=ABS)
    geo = _geometria(punto)
    g3 = geo.verificaciones[-1]
    assert g3.codigo == "G3" and g3.cumple is True
    assert g3.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert g3.estado is modelos.EstadoDeVerificacion.INDICADOR
    assert g3.criterio_aplicado == CLAVE_ESVIAJE
    assert g3.valor_admisible == _igual(maximo)
    assert geo.factible                       # G3 no cuenta como incumplida
    # El aviso NO se repite en la lista de 7.B: G3 es una verificacion con
    # veredicto INDICADOR y sale por `InformePunto.con_aviso` (ver abajo,
    # `test_el_esviaje_sobre_el_maximo_sale_una_vez_por_la_via_de_los_indicadores`)
    assert not any("esviaje" in a for a in geo.avisos)
    assert "SUPERA el maximo adoptado" in g3.paso.veredicto.explicacion
    assert g3.paso.umbral.cita_id == "HDS5_3ED.5.4.2#MAXIMO_PRACTICO"
    assert g3.paso.umbral.caracter == "RECOMENDACION"


def test_el_esviaje_dentro_del_maximo_no_avisa_y_la_frontera_es_inclusiva():
    maximo = ca.CRITERIOS[CLAVE_ESVIAJE].valor
    for grados in (0.0, 15.0, 30.0, maximo):
        geo = _geometria(_punto(esviaje_grados=grados))
        g3 = geo.verificaciones[-1]
        assert g3.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE, grados
        assert not any("esviaje" in a for a in geo.avisos)


def test_los_cuatro_esviajes_del_fixture_no_cambian_de_veredicto():
    """15, 5, 0 y 30 grados: ninguno avisa ni se detiene con el valor adoptado."""
    puntos = cargar_puntos(CSV)
    assert [p.esviaje_grados for p in puntos] == _igual([15.0, 5.0, 0.0, 30.0])
    for p in puntos:
        v = M7.g3_esviaje(p)
        assert v.cumple and v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE


def test_el_aviso_de_esviaje_se_pinta_como_indicador_en_la_memoria():
    geo = _geometria(_punto(esviaje_grados=55.0))
    g3 = geo.verificaciones[-1]
    assert M11._es_indicador(g3)
    assert M11.CLASE_INDICADOR in M11._marca_de_verificacion(g3)


def test_la_guardia_numerica_del_esviaje_sigue_invariante():
    """PC-32: cerca de 90 grados sigue siendo LimiteNumericoError."""
    from src.modelos import LimiteNumericoError
    with pytest.raises(LimiteNumericoError):
        M7.factor_esviaje(_punto(esviaje_grados=89.99999))


# ===========================================================================
# 5. Pendiente adoptada con tres origenes (INF-3.2.7, parte de M7)
# ===========================================================================

def test_sin_declaracion_la_pendiente_es_la_del_cauce():
    p = M7.pendiente_adoptada(_punto())
    assert p.valor == _igual(S_A01) and p.origen is modelos.OrigenPendiente.CAUCE
    assert p.S_declarada is None


def test_la_pendiente_declarada_gana_y_no_se_recorta():
    p = M7.pendiente_adoptada(_punto(), S_declarada=0.004)
    assert p.valor == _igual(0.004) and p.origen is modelos.OrigenPendiente.DECLARADA
    assert p.S_cauce == _igual(S_A01)


def test_sin_cauce_ni_declaracion_falta_el_dato():
    with pytest.raises(DatoFaltanteError) as exc:
        M7.pendiente_adoptada(_punto(S_cauce=None))
    assert exc.value.campo == "S_cauce"
    assert M7.pendiente_adoptada(_punto(S_cauce=None), 0.004).valor == _igual(0.004)


@pytest.mark.parametrize("S_cauce, minimo, maximo, esperado, origen", [
    (0.006, 0.002, 0.05, 0.006, "CAUCE"),
    (0.001, 0.002, 0.05, 0.002, "MINIMA"),
    (0.080, 0.002, 0.05, 0.050, "MAXIMA"),
    (0.002, 0.002, 0.05, 0.002, "CAUCE"),       # la frontera es del cauce
    (0.050, 0.002, 0.05, 0.050, "CAUCE"),
])
def test_los_limites_gobiernan_solo_sobre_la_pendiente_del_cauce(
        monkeypatch, S_cauce, minimo, maximo, esperado, origen):
    # La banda entra por la lectura UNICA de T-2: si M7 leyera los criterios
    # por su cuenta, sustituir `limites_de_pendiente` no cambiaria nada.
    monkeypatch.setattr(M7, "limites_de_pendiente", lambda: (minimo, maximo))
    p = M7.pendiente_adoptada(_punto(S_cauce=S_cauce))
    assert p.valor == _igual(esperado)
    assert p.origen is modelos.OrigenPendiente[origen]
    assert (p.S_minima, p.S_maxima) == (minimo, maximo)
    assert bool(M7.aviso_de_pendiente(p)) == (origen != "CAUCE")
    # una pendiente DECLARADA no se recorta: la juzga la Fase 5 (V10)
    declarada = M7.pendiente_adoptada(_punto(S_cauce=S_cauce), S_declarada=0.0005)
    assert declarada.valor == _igual(0.0005)
    assert declarada.origen is modelos.OrigenPendiente.DECLARADA
    assert M7.aviso_de_pendiente(declarada) == ""


def test_M7_lee_la_banda_de_la_lectura_unica_de_T2():
    """
    `M7.limites_de_pendiente` ES `M5.limites_de_pendiente`, y las dos claves
    son las de M5: no hay segunda lectura de la banda (ni segunda guardia).
    """
    from src.modulos import M5_verificaciones as M5
    assert M7.limites_de_pendiente is M5.limites_de_pendiente
    assert M7.CRITERIO_PENDIENTE_MINIMA is M5.CRITERIO_PENDIENTE_MINIMA
    assert M7.CRITERIO_PENDIENTE_MAXIMA is M5.CRITERIO_PENDIENTE_MAXIMA
    assert (M7.CRITERIO_PENDIENTE_MINIMA,
            M7.CRITERIO_PENDIENTE_MAXIMA) == CLAVES_DE_T2
    assert not hasattr(M7, "_limite_de_pendiente")
    # con los valores de archivo (0.0 y 0.10) la banda llega al objeto
    p = M7.pendiente_adoptada(_punto())
    assert (p.S_minima, p.S_maxima) == M5.limites_de_pendiente()


@pytest.mark.parametrize("S_cauce", [float("nan"), float("inf"), 0.0, -0.01])
def test_una_pendiente_de_cauce_que_no_es_un_positivo_finito_no_se_adopta(S_cauce):
    """
    Segunda linea (M0 ya lo exige): un NaN es falso frente a `>=` y frente a
    `<=`, y sin esta guardia `S_cauce = nan` salia con origen «minima» y
    valor 0.0, que es rellenar un dato roto con un extremo de la banda.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        M7.pendiente_adoptada(_punto(S_cauce=S_cauce))
    assert exc.value.campo == "S_cauce"


@pytest.mark.parametrize("S", [float("nan"), float("inf"), -0.001])
def test_una_pendiente_declarada_negativa_o_no_finita_no_se_adopta(S):
    with pytest.raises(DatoInvalidoError) as exc:
        M7.pendiente_adoptada(_punto(), S_declarada=S)
    assert exc.value.campo == "S_conducto"
    # el cero si: es el barril horizontal que T-2 admite
    assert M7.pendiente_adoptada(_punto(), S_declarada=0.0).valor == _igual(0.0)


def test_el_desnivel_frente_al_cauce_tiene_signo_y_puede_no_existir():
    """Positivo: conducto mas tendido que el cauce. Sin cauce, no hay numero."""
    tendido = M7.pendiente_adoptada(_punto(S_cauce=0.010), S_declarada=0.004)
    assert M7.desnivel_frente_al_cauce(tendido, 20.0) == pytest.approx(
        0.12, abs=ABS)                                   # (0.010 - 0.004) * 20
    empinado = M7.pendiente_adoptada(_punto(S_cauce=0.002), S_declarada=0.004)
    assert M7.desnivel_frente_al_cauce(empinado, 20.0) == pytest.approx(
        -0.04, abs=ABS)
    sin_cauce = M7.pendiente_adoptada(_punto(S_cauce=None), S_declarada=0.004)
    assert M7.desnivel_frente_al_cauce(sin_cauce, 20.0) is None
    # y sin longitud el aviso lleva la expresion, no un numero
    with_max = M7.PendienteAdoptada(
        valor=0.02, origen=modelos.OrigenPendiente.MAXIMA, S_cauce=0.03,
        S_declarada=None, S_minima=0.0, S_maxima=0.02, procedencia="prueba")
    assert "(S_cauce - S_conducto) x L" in M7.aviso_de_pendiente(with_max)
    assert "0.20 m en este punto" in M7.aviso_de_pendiente(with_max, 20.0)


def test_el_limite_que_gobierna_llega_al_diseno_al_TW_y_a_7B():
    """
    De punta a punta, con el minimo por ENCIMA de la pendiente del cauce de
    A-01 (0.006): la Fase 4 corre con 0.007, 7.B cae 0.007*L y la memoria
    dice que gobierna el minimo. La pendiente no se elige dos veces (MAT-D9):
    si el limite se quedara en M7 y MD siguiera con la del cauce, el HW y la
    cota de salida saldrian de dos pendientes distintas.
    """
    with con_valor(CLAVES_DE_T2[0], 0.007,
                   motivo="T-6: un minimo sobre el cauce de A-01 y bajo el de "
                          "A-02, fuera de la ventana (0, 0.005) a proposito"):
        informe = _correr()
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert a01.pendiente.origen is modelos.OrigenPendiente.MINIMA
    assert a01.resultado.resultado_hidraulico.S == _igual(0.007)
    geo = a01.geometria
    assert geo.S_conducto == _igual(0.007)
    assert geo.pendiente.origen is modelos.OrigenPendiente.MINIMA
    L = (ANCHO + TALUD * 2 * H_EJE) / (COS15 - TALUD * 0.007)
    assert geo.longitud == pytest.approx(L, abs=ABS)
    assert geo.caida == pytest.approx(0.007 * L, abs=ABS)
    assert geo.cota_salida == pytest.approx(TERRENO - 0.007 * L, abs=ABS)
    # A-02 (0.008) queda por encima del minimo: sigue con la del cauce
    a02 = next(p for p in informe.puntos if p.punto.id == "A-02")
    assert a02.pendiente.origen is modelos.OrigenPendiente.CAUCE
    assert a02.resultado.resultado_hidraulico.S == _igual(0.008)
    # C-01 la DECLARA (0.004 < 0.007) y el limite no la pisa
    c01 = next(p for p in informe.puntos if p.punto.id == "C-01")
    assert c01.pendiente.origen is modelos.OrigenPendiente.DECLARADA
    assert c01.pendiente.valor == _igual(0.004)


def test_dos_limites_cruzados_son_dato_invalido():
    """La banda vacia la rechaza la lectura unica de T-2, tambien desde M7."""
    with con_valor(CLAVES_DE_T2[0], 0.05, motivo="T-6: minimo sobre el maximo"), \
            con_valor(CLAVES_DE_T2[1], 0.002, motivo="T-6: maximo bajo el minimo"):
        with pytest.raises(DatoInvalidoError):
            M7.pendiente_adoptada(_punto())


def test_con_los_criterios_de_T2_la_pendiente_del_cauce_se_acota_de_verdad():
    """
    Con las claves REALES, sin `monkeypatch`. Era un `skipif` mientras T-6
    corrio en paralelo con T-2; se libero al integrar.
    """
    with con_valor(CLAVES_DE_T2[0], 0.004, motivo="T-6: minimo sobre el cauce"), \
            con_valor(CLAVES_DE_T2[1], 0.05, motivo="T-6: maximo holgado"):
        bajo = M7.pendiente_adoptada(_punto(S_cauce=0.001))
        assert bajo.valor == _igual(0.004)
        assert bajo.origen is modelos.OrigenPendiente.MINIMA
        dentro = M7.pendiente_adoptada(_punto())
        assert dentro.origen is modelos.OrigenPendiente.CAUCE
        assert dentro.S_minima == _igual(0.004)
        assert dentro.S_maxima == _igual(0.05)
    # Y EL FIXTURE NO SE MUEVE con los valores de archivo de T-2 (0.0 y
    # 0.10): ninguna pendiente de cauce de los cuatro puntos queda fuera.
    for punto in cargar_puntos(CSV):
        if punto.S_cauce is not None:
            adoptada = M7.pendiente_adoptada(punto)
            assert adoptada.origen is modelos.OrigenPendiente.CAUCE, punto.id
            assert M7.aviso_de_pendiente(adoptada) == ""


# ---------------------------------------------------------------------------
# El reparto con V10 (auditor de T-6, punto 2): M7 acota la pendiente del
# CAUCE y lo avisa; V10 juzga la que quedo y solo falla con una DECLARADA.
# ---------------------------------------------------------------------------

def _csv_con(tmp_path, id_punto, **celdas):
    """Una copia del CSV de ejemplo con las celdas de un punto cambiadas."""
    lineas = CSV.read_text(encoding="utf-8").splitlines()
    cabecera = lineas[0].split(",")
    salida = [lineas[0]]
    for linea in lineas[1:]:
        fila = linea.split(",")
        if fila[0] == id_punto:
            for columna, valor in celdas.items():
                fila[cabecera.index(columna)] = valor
        salida.append(",".join(fila))
    ruta = tmp_path / "puntos.csv"
    ruta.write_text("\n".join(salida) + "\n", encoding="utf-8")
    return ruta


def _correr_csv(csv, tmp_path, por_punto=None):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps({"globales": {"TW_m": 0.3},
                                "puntos": por_punto or {}}))
    ext = cli.cargar_datos_externos(
        ruta, {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
               "L_hidraulico_m": None, "categoria_tr": None})
    return servicio.correr(csv, ext, alcance=cli.ALCANCE_PERFIL)


def _verificacion(informe_punto, codigo):
    return next(v for _, v in informe_punto.verificaciones()
                if v.codigo == codigo)


@pytest.fixture
def _banda_limpia():
    yield
    for clave in (*CLAVES_DE_T2, "regimen_v2b"):
        ca.quitar_valor_dinamico(clave)


def test_el_maximo_gobierna_y_el_punto_dimensiona_con_V2b_como_indicador(
        tmp_path, _banda_limpia):
    """
    Un cauce al 3 % con el maximo declarado en 2 % (dentro de su ventana,
    0.02 a 0.10, por la puerta): el diseño corre con 0.02, V10 CUMPLE --la
    pendiente que juzga ya es el extremo--, y con el regimen de archivo
    (`indicador_con_aviso`) V2b se dispara como indicador y el punto
    dimensiona. El aviso de la pendiente dice que trae consigo y sale UNA vez
    por `InformePunto.avisos()`, con el desnivel en metros.
    """
    ca.establecer_valor_dinamico(CLAVES_DE_T2[1], 0.02)
    assert ca.valor("regimen_v2b") == "indicador_con_aviso"
    informe = _correr_csv(_csv_con(tmp_path, "A-01", S_cauce="0.030"), tmp_path)
    a01 = informe.puntos[0]
    assert a01.dimensionado
    assert a01.pendiente.origen is modelos.OrigenPendiente.MAXIMA
    assert a01.resultado.resultado_hidraulico.S == _igual(0.02)
    assert _verificacion(a01, "V10").cumple
    v2b = _verificacion(a01, "V2b")
    assert v2b.estado is modelos.EstadoDeVerificacion.INDICADOR
    geo = a01.geometria
    desnivel = (0.030 - 0.02) * geo.longitud
    assert M7.desnivel_frente_al_cauce(geo.pendiente, geo.longitud) == \
        pytest.approx(desnivel, abs=ABS)
    (aviso,) = [a for a in a01.avisos() if "maximo adoptado" in a]
    assert "estructura de caida o de disipacion" in aviso
    assert "regimen_v2b" in aviso and "0.03 m/m" in aviso
    assert f"{desnivel:.2f} m en este punto" in aviso
    assert aviso in geo.avisos
    assert [a for a in a01.avisos() if a.startswith("V2b:")]
    # el paso 7.B.1 dice el origen y el 7.B.4 lleva el desnivel con su numero
    assert "S_maxima" in geo.pasos[0].formula
    assert "AVISO" in geo.pasos[0].nota_del_proyecto
    paso_salida = next(p for p in geo.pasos if p.codigo == "7.B.4")
    assert _valor(paso_salida, "(S_cauce - S) * L") == pytest.approx(
        desnivel, abs=ABS)
    # una vez en el volcado de texto, y en el JSON del punto
    texto = cli.volcar(informe)
    assert texto.count("limitada al maximo adoptado") == 1
    volcado = cli.informe_json(informe)["puntos"][0]
    assert volcado["avisos"].count(aviso) == 1
    assert volcado["geometria"]["S_conducto_origen"]["origen"] == \
        modelos.OrigenPendiente.MAXIMA.value
    assert "limitada al maximo adoptado" in M11.memoria_de_punto(a01)


def test_el_maximo_gobierna_y_con_umbral_duro_el_punto_no_dimensiona_por_V2b(
        tmp_path, _banda_limpia):
    """
    El mismo cauce con `regimen_v2b` = umbral_duro: V2b incumple en todos los
    escalones --el conducto queda mas tendido que el cauce por decision de la
    banda-- y el punto NO dimensiona, con V2b nombrada en el motivo. V10 no
    es quien lo detiene. Y el aviso de la pendiente sale igual, aunque el
    punto no llegue a 7.B.
    """
    ca.establecer_valor_dinamico(CLAVES_DE_T2[1], 0.02)
    ca.establecer_valor_dinamico("regimen_v2b", "umbral_duro")
    informe = _correr_csv(_csv_con(tmp_path, "A-01", S_cauce="0.030"), tmp_path)
    a01 = informe.puntos[0]
    assert not a01.dimensionado and a01.geometria is None
    assert a01.pendiente.origen is modelos.OrigenPendiente.MAXIMA
    assert a01.traza, "MD tuvo que probar escalones"
    evaluados = [e for e in a01.traza if e.incumplidas]
    assert evaluados and not any(e.aceptado for e in a01.traza)
    for escalon in evaluados:      # los demas no transportan Q en flujo libre
        codigos = [v.codigo for v in escalon.incumplidas]
        assert "V2b" in codigos, escalon.motivo
        assert "V10" not in codigos, escalon.motivo
    motivos = " ".join(b.mensaje for b in a01.bloqueos)
    assert "V2b" in motivos
    (aviso,) = [a for a in a01.avisos() if "maximo adoptado" in a]
    assert "estructura de caida o de disipacion" in aviso
    assert f"{(0.030 - 0.02) * a01.longitud.valor:.2f} m en este punto" in aviso
    assert cli.volcar(informe).count("limitada al maximo adoptado") == 1
    assert "limitada al maximo adoptado" in M11.memoria_de_punto(a01)


def test_el_minimo_gobierna_el_punto_dimensiona_y_G2_juzga_la_salida(
        tmp_path, _banda_limpia):
    """
    Un cauce al 0.4 % con el minimo declarado en 0.5 % (el tope de su
    ventana): el conducto cae mas que el cauce, la salida queda
    (0.005 - 0.004)*L bajo el cauce natural y G2 se evalua con esa cota.
    V2b no se dispara (el conducto no queda mas plano) y V10 cumple.
    """
    ca.establecer_valor_dinamico(CLAVES_DE_T2[0], 0.005)
    informe = _correr_csv(_csv_con(tmp_path, "A-01", S_cauce="0.004"), tmp_path)
    a01 = informe.puntos[0]
    assert a01.dimensionado
    assert a01.pendiente.origen is modelos.OrigenPendiente.MINIMA
    geo = a01.geometria
    assert geo.S_conducto == _igual(0.005)
    assert _verificacion(a01, "V10").cumple
    assert _verificacion(a01, "V2b").estado is modelos.EstadoDeVerificacion.CUMPLE
    g2 = _verificacion(a01, "G2")
    assert g2.cumple
    assert g2.valor_obtenido == pytest.approx(TERRENO - 0.005 * geo.longitud,
                                              abs=ABS)
    bajo_el_cauce = (0.005 - 0.004) * geo.longitud
    (aviso,) = [a for a in a01.avisos() if "minimo adoptado" in a]
    assert "por debajo del cauce natural" in aviso and "G2" in aviso
    assert f"{bajo_el_cauce:.2f} m en este punto" in aviso
    paso_salida = next(p for p in geo.pasos if p.codigo == "7.B.4")
    assert _valor(paso_salida, "(S_cauce - S) * L") == pytest.approx(
        -bajo_el_cauce, abs=ABS)


def test_V10_solo_se_incumple_con_una_pendiente_declarada(tmp_path):
    """
    El reparto, por el otro lado: la pendiente DECLARADA no la acota M7, y
    fuera de la banda (0.15 > 0.10) es V10 quien la rechaza en todos los
    escalones. No hay aviso de pendiente: el origen es la declaracion.
    """
    informe = _correr_csv(CSV, tmp_path, {"A-01": {"S_conducto": 0.15}})
    a01 = informe.puntos[0]
    assert a01.pendiente.origen is modelos.OrigenPendiente.DECLARADA
    assert not a01.dimensionado
    evaluados = [e for e in a01.traza if e.incumplidas]
    assert evaluados and not any(e.aceptado for e in a01.traza)
    for escalon in evaluados:
        assert "V10" in [v.codigo for v in escalon.incumplidas], escalon.motivo
    assert not [a for a in a01.avisos() if "adoptado (" in a]
    # y los otros puntos, con la pendiente de su cauce dentro de la banda, no
    assert _verificacion(informe.puntos[1], "V10").cumple


# ---------------------------------------------------------------------------
# Lo que dejo el cierre de la integracion (2026-11-12). Medidos en ROJO
# contra el arbol de los commits `wip(T-6)` (`315d491`) antes de corregir:
# los diez items fallaban alli, cada uno por su razon (la banda vacia salia
# de `correr_punto` como DatoInvalidoError; `InformePunto` no tenia
# `cota_entrada`; G3 aceptaba el maximo malo; las fichas de T-2 decian solo
# «la aplica V10»).
# ---------------------------------------------------------------------------

def test_la_banda_vacia_bloquea_el_punto_y_no_tumba_la_corrida():
    """
    `M7.pendiente_adoptada` corre FUERA de `_etapa` (antes de la Fase 4), y
    la banda vacia que levanta `M5.limites_de_pendiente` salia de
    `correr_punto` y tumbaba la corrida entera; antes de T-6 la misma banda
    la levantaba V10 dentro del bucle de MD y quedaba como bloqueo del
    punto. Ahora es un bloqueo de la etapa 7.B.1, con el dato nombrado, y
    los demas puntos siguen.
    """
    with con_valor(CLAVES_DE_T2[0], 0.05, motivo="T-6: minimo sobre el maximo"), \
            con_valor(CLAVES_DE_T2[1], 0.002, motivo="T-6: maximo bajo el minimo"):
        informe = _correr()
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    (bloqueo,) = [b for b in a01.bloqueos
                  if b.etapa == servicio.ETAPA_PENDIENTE]
    assert bloqueo.fase == servicio.FASE_GEOMETRIA
    assert bloqueo.tipo is modelos.TipoDeBloqueo.DATO_INVALIDO
    assert a01.pendiente is None and a01.longitud is None
    assert not a01.dimensionado
    # C-01 DECLARA su pendiente: M7 no lee la banda para ella, y no se
    # detiene en 7.B.1 (si V10 la juzga, es V10 quien dice la banda vacia)
    c01 = next(p for p in informe.puntos if p.punto.id == "C-01")
    assert c01.pendiente.origen is modelos.OrigenPendiente.DECLARADA
    assert not [b for b in c01.bloqueos if b.etapa == servicio.ETAPA_PENDIENTE]
    # y la corrida se puede volcar entera
    assert cli.informe_json(informe)["puntos"][0]["id"] == "A-01"


def _externos_con(tmp_path, id_punto, **claves):
    """Las entradas ampliadas de la linea base con claves por punto."""
    datos = json.loads(EXTERNOS.read_text(encoding="utf-8"))
    datos.setdefault("puntos", {}).setdefault(id_punto, {}).update(claves)
    ruta = tmp_path / "externos_ampliados.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def test_el_fondo_adoptado_se_avisa_con_el_metodo_simetrico_en_el_punto_que_no_dimensiona():
    """
    B-01 no dimensiona en la corrida ancha. Con el metodo SIMETRICO su
    longitud no lleva el aviso de fondo adoptado --ese metodo no lee la cota
    de entrada--, pero V4 y 7.A, dentro de MD, si la usaron: el aviso tiene
    que salir igual por `InformePunto.avisos()`, una vez y primero entre los
    de la geometria, como en 7.B.
    """
    ca.establecer_valor_dinamico(CLAVE_METODO, "terraplen_simetrico")
    informe = _correr()
    b01 = next(p for p in informe.puntos if p.punto.id == "B-01")
    assert b01.geometria is None and b01.longitud_calculada is not None
    assert b01.longitud_calculada.metodo is modelos.MetodoLongitud.TERRAPLEN_SIMETRICO
    assert AVISO not in b01.longitud_calculada.avisos
    assert b01.cota_entrada is not None and not b01.cota_entrada.medida
    assert b01.avisos().count(AVISO) == 1
    assert b01.avisos_de_geometria()[0] == AVISO
    volcado = {p["id"]: p for p in cli.informe_json(informe)["puntos"]}
    assert volcado["B-01"]["avisos"].count(AVISO) == 1
    assert cli.volcar(informe).count(f"aviso: {AVISO}") == len(informe.puntos)


def test_el_fondo_adoptado_se_avisa_con_la_longitud_declarada_en_el_punto_que_no_dimensiona(
        tmp_path):
    """
    Lo mismo con la longitud DECLARADA (`longitud_m`): no hay
    `longitud_calculada` de donde leer el aviso, y la cota de entrada que V4
    uso sigue siendo la adoptada.
    """
    ext = cli.cargar_datos_externos(
        _externos_con(tmp_path, "B-01", longitud_m=18.40),
        {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
         "L_hidraulico_m": None, "categoria_tr": None})
    informe = servicio.correr(CSV, ext, alcance=cli.ALCANCE_PERFIL)
    b01 = next(p for p in informe.puntos if p.punto.id == "B-01")
    assert b01.geometria is None and b01.longitud_calculada is None
    assert b01.longitud.valor == _igual(18.40)
    assert b01.avisos().count(AVISO) == 1
    # una cota MEDIDA no avisa, tampoco por esta via
    medido = replace(b01.cota_entrada, medida=True, regla=None)
    assert medido.aviso == ""


@pytest.mark.parametrize("malo", [float("nan"), float("inf"), -5.0, 0.0, True,
                                  "45"])
def test_g3_rechaza_un_maximo_que_burla_la_puerta(malo):
    """
    Segunda linea de G3 (forma MAT-D13): con un NaN el aviso salia en todo
    punto (`esviaje <= nan` es falso), con un infinito no salia en ninguno.
    """
    with con_valor(CLAVE_ESVIAJE, malo, motivo="guardia de G3 tras la puerta"):
        with pytest.raises(DatoInvalidoError) as exc:
            M7.g3_esviaje(_punto())
    assert exc.value.campo == CLAVE_ESVIAJE


def test_las_fichas_de_la_banda_dicen_el_reparto_con_M7():
    """
    Las fichas de T-2 decian «la aplica V10» y nada mas. Desde T-6 la banda
    la leen dos piezas y cada ficha lo dice: M7 acota la pendiente del CAUCE
    (eleva a la minima, limita a la maxima) y V10 juzga la DECLARADA.
    """
    for clave, verbo in ((CLAVES_DE_T2[0], "eleva"), (CLAVES_DE_T2[1], "limita")):
        ficha = ca.CRITERIOS[clave]
        assert f"M7 {verbo} a ella la del cauce" in ficha.concepto, clave
        assert "V10 juzga con ella la declarada" in ficha.concepto, clave
        assert "V10 solo rechaza una pendiente declarada" in \
            ficha.justificacion, clave
    assert "G2 la juzga" in ca.CRITERIOS[CLAVES_DE_T2[0]].justificacion
    maxima = ca.CRITERIOS[CLAVES_DE_T2[1]].justificacion
    assert "estructura de caida o de disipacion" in maxima
    assert "regimen_v2b" in maxima


def test_el_esviaje_sobre_el_maximo_sale_una_vez_por_la_via_de_los_indicadores(
        tmp_path):
    """
    G3 disparada llega a `InformePunto.avisos()` como los demas indicadores
    (`con_aviso`), cuenta en el RESUMEN y se imprime UNA vez; los avisos de
    texto de 7.B (fondo adoptado, plataforma horizontal) tambien una vez.
    """
    informe = _correr_csv(_csv_con(tmp_path, "A-01", esviaje_grados="50"),
                          tmp_path)
    a01 = informe.puntos[0]
    assert a01.dimensionado
    assert [v.codigo for v in a01.con_aviso()] == ["G3"]
    (de_g3,) = [a for a in a01.avisos() if a.startswith("G3:")]
    assert "indicador disparado" in de_g3
    assert "SUPERA el maximo adoptado" in de_g3
    assert a01.avisos().count(AVISO) == 1
    assert sum("plataforma tomada horizontal" in a for a in a01.avisos()) == 1
    assert set(a01.avisos_de_geometria()) <= set(a01.avisos())
    base = _correr_csv(CSV, tmp_path)
    assert informe.resumen().con_aviso == base.resumen().con_aviso + 1
    texto = cli.volcar(informe)
    assert texto.count("G3: indicador disparado") == 1
    assert texto.count(f"aviso: {AVISO}") == len(informe.puntos) - 1  # C-01 no
    volcado = cli.informe_json(informe)["puntos"][0]
    assert volcado["avisos"] == list(a01.avisos())


def test_el_punto_que_no_dimensiona_lleva_los_avisos_de_su_longitud():
    """
    B-01 no dimensiona en la corrida ancha y su longitud SI se calculo, con
    el fondo adoptado y la plataforma horizontal: los dos avisos salen por
    `InformePunto.avisos()` aunque el punto no llegue a 7.B.
    """
    informe = _correr()
    b01 = next(p for p in informe.puntos if p.punto.id == "B-01")
    assert b01.geometria is None and b01.longitud_calculada is not None
    assert b01.avisos_de_geometria() == b01.longitud_calculada.avisos
    assert AVISO in b01.avisos()
    assert any("plataforma tomada horizontal" in a for a in b01.avisos())
    texto = "\n".join(cli._lineas_punto(b01)) if hasattr(cli, "_lineas_punto") \
        else cli.volcar(informe)
    assert f"aviso: {AVISO}" in texto


def test_el_paso_de_la_pendiente_dice_el_origen():
    geo = _geometria()
    p = geo.pasos[0]
    assert p.codigo == "7.B.1" and p.fundamento_id == "F7.PENDIENTE"
    assert p.resultado.valor == _igual(S_A01)
    assert p.elecciones[0].valor == modelos.OrigenPendiente.CAUCE.value
    assert geo.pendiente.origen is modelos.OrigenPendiente.CAUCE
    declarada = _geometria(resultado=_resultado(S=0.004))
    assert declarada.pendiente.origen is modelos.OrigenPendiente.DECLARADA
    assert declarada.pasos[0].elecciones[0].valor == \
        modelos.OrigenPendiente.DECLARADA.value
    assert "declarada" in declarada.pasos[0].formula


def test_paso_pendiente_imprime_los_limites_cuando_gobiernan(monkeypatch):
    """`M7.paso_pendiente` con el minimo gobernando: formula, limites y origen."""
    monkeypatch.setattr(M7, "limites_de_pendiente", lambda: (0.002, 0.05))
    p = M7.paso_pendiente(M7.pendiente_adoptada(_punto(S_cauce=0.001)))
    assert "S_minima" in p.formula
    assert _valor(p, "S_minima") == _igual(0.002)
    assert _valor(p, "S_maxima") == _igual(0.05)
    assert _valor(p, "S_cauce") == _igual(0.001)
    assert p.resultado.valor == _igual(0.002)
    assert p.elecciones[0].valor == modelos.OrigenPendiente.MINIMA.value


def test_la_pendiente_de_7B_no_puede_ser_otra_que_la_del_diseno():
    """MAT-D9: un `PendienteAdoptada` que no vale `resultado.S` es un fallo."""
    otra = M7.pendiente_adoptada(_punto(), S_declarada=0.010)
    with pytest.raises(ValueError):
        _geometria(pendiente=otra)


def test_la_pendiente_declarada_del_punto_llega_con_su_origen_al_json():
    informe = _correr()
    volcado = cli.informe_json(informe)
    por_id = {p["id"]: p for p in volcado["puntos"]}
    origen = por_id["A-01"]["geometria"]["S_conducto_origen"]
    assert origen["origen"] == modelos.OrigenPendiente.CAUCE.value
    assert origen["S_cauce"] == _igual(S_A01)
    c01 = next(p for p in informe.puntos if p.punto.id == "C-01")
    assert c01.pendiente.origen is modelos.OrigenPendiente.DECLARADA
    assert c01.pendiente.valor == _igual(0.004)
    assert c01.pendiente.S_cauce == _igual(0.006)


# ===========================================================================
# Las fuentes: que cada cita diga lo que se le atribuye
# ===========================================================================

@pytest.mark.parametrize("cita_id, pagina_impresa, pagina_pdf, fragmento", [
    ("MC_HHD.4.1.1.3.2", "71", 74, "sigue la dirección de la corriente"),
    ("MC_HHD.4.1.1.3.3", "71", 74, "erosión y sedimentación"),
    ("MC_HHD.LAMINA_01", "206", 209, "SALIDA SOBRE LA PENDIENTE NATURAL"),
    ("HDS5_3ED.2.2.4#LONGITUD", "2.8", 70, "culvert length are approximate"),
    ("HDS5_3ED.3.1.4#LONGITUD", "3.9", 91, "approximation of barrel length"),
    ("HDS5_3ED.3.3.5#ENCAJE", "3.25", 107, "fitted into the roadway cross section"),
    ("HDS5_3ED.5.4.1#ESVIAJE", "5.12", 148, "line normal to the highway"),
    ("HDS5_3ED.5.4.2#MAXIMO_PRACTICO", "5.13", 149, "about 45-degrees"),
    ("DG2018.304.05#BOMBEO", "195", 196, "denominada bombeo"),
    ("DG2018.304.06#PERALTE", "196", 197, "fuerza centrífuga"),
])
def test_las_diez_citas_de_T6_estan_en_el_registro_con_su_pagina(
        cita_id, pagina_impresa, pagina_pdf, fragmento):
    c = registro.construir().cita(cita_id)
    assert c.pagina_impresa == pagina_impresa and c.pagina_pdf == pagina_pdf
    assert fragmento in c.texto_literal.texto
    assert c.verificado is not None


def test_ninguna_cita_de_T6_queda_huerfana_y_los_verbos_se_sostienen():
    reg = registro.construir()
    assert reg.problemas_de_integridad() == ()
    referenciadas = reg.citas_referenciadas()
    for cita_id in ("MC_HHD.4.1.1.3.2", "MC_HHD.4.1.1.3.3", "MC_HHD.LAMINA_01",
                    "HDS5_3ED.2.2.4#LONGITUD", "HDS5_3ED.3.1.4#LONGITUD",
                    "HDS5_3ED.3.3.5#ENCAJE", "HDS5_3ED.5.4.1#ESVIAJE",
                    "HDS5_3ED.5.4.2#MAXIMO_PRACTICO", "DG2018.304.05#BOMBEO",
                    "DG2018.304.06#PERALTE"):
        assert cita_id in referenciadas, cita_id
    # el tope de esviaje se funda en un «practical maximum», no en un «shall»
    assert reg.fundamento("F7.ESVIAJE_MAX").verbo.value == "recomienda"
    assert reg.cita("HDS5_3ED.5.4.2#MAXIMO_PRACTICO").caracter.value == \
        "recomendacion"
