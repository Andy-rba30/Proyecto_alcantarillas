"""
tests/test_ve2_flotacion.py
===========================
VE-2, decision (c) de la ficha VE1-02: la flotacion del conducto (V7).

(c1) LA JUSTIFICACION, bloque 2 de VE-2. La sumersion completa y DC = 0 se
     justificaban en `M8_estructural` y en el `por_que` de F5.V7 con el NF
     somero del Bajo Piura: un argumento de SITIO que la norma no usa. Lo que
     la norma dice, verificado contra los PDF del repositorio de normas:

       * Manual de Puentes num. 2.4.3.8.1, pag. impresa 113 (PDF 114): «Los
         niveles de agua de diseño para los diferentes estados límites serán
         los especificados y/o aprobados por el Propietario.» (AASHTO LRFD
         9.a ed. 3.7.1, pag. 3-45, PDF 99, lo dice igual: «Design water
         levels for various limit states shall be as specified and/or
         approved by the Owner.»)
       * num. 2.4.3.8.2, misma pagina: la subpresion actua sobre lo que esta
         «debajo del nivel de agua de diseño».
       * AASHTO 12.6.1 (pag. 12-14, PDF 1652) y 12.6.2.3 (pag. 12-19, PDF
         1657): evaluar la flotacion con el invert bajo el freatico, y el
         levantamiento bajo «the highest anticipated groundwater level».
       * Manual de Puentes 2.4.5.3.1 (pag. 142) y Tabla 2.4.5.3.1-2 (pag.
         143): «DC: Componentes y Auxiliares» 1.25 / 0.90, y la carga
         permanente que estabiliza se investiga con su MINIMO. C12.6.2.3:
         «the dead load on the crown of the structure should exceed the
         buoyancy of the culvert».

     Por eso el nivel en la clave (sumersion completa) es una ADOPCION [A]
     conservadora del proyecto en el sitio de una decision del Propietario,
     y DC = 0 queda del lado seguro frente al 0.90·DC que la tabla
     admitiria. Y la equivalencia que la ficha VE1-02 (c) escribia, «unas
     0.45 veces el diametro exterior», es la de pesos SIN factorar: con el
     gamma_EV = 0.90 que V7 aplica sale 0.50 (medido abajo con el codigo).

Escrita PRIMERO, en rojo (§1 regla 4 de la cadena): los tests de (c1) con
`xfail(strict=True)` fallaban por su motivo antes de tocar los textos; se
liberaron al corregir. Los mutantes se anotan junto a cada test.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

from src import criterios_adoptados as ca
from src.constantes_fisicas import GAMMA_AGUA_KN_M3
from src.modelos import SeccionCircular, TipoMaterial
from src.modulos import M5_verificaciones as M5
from src.modulos import M8_estructural as M8
from src.modulos.M2_material import catalogo, espesor_pared
from src.normativa import fuentes
from src.normativa.esquema import Caracter
from src.normativa.fundamentos import FUNDAMENTOS
from src.normativa.registro import construir
from tests.apoyo.aproximacion import REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parents[1]
REGISTRO = RAIZ / "docs" / "decisiones_diferidas.md"

# LAS TOLERANCIAS DE ESTE ARCHIVO, NOMBRADAS (tests/apoyo/aproximacion.py).
# REL_TRANSPORTE para lo que el codigo transporta o calcula por la misma
# asociacion de operaciones que el test; REL_RECALCULADO para lo que el test
# recalcula A MANO por otra asociacion de las mismas pocas operaciones (una
# raiz, un arcocoseno, una resta de cotas): el ruido es de unos pocos ulp, y
# 1e-9 relativo queda siete ordenes por encima sin tapar un error de formula
# (el mas pequeño que estos tests distinguen, restar o no el peso del agua,
# es de un 50 %). MEDIA_CENTESIMA: la equivalencia de la ficha se escribe con
# dos decimales.
REL_RECALCULADO = 1e-9
MEDIA_CENTESIMA = 0.005

CITA_NIVEL_MP = "MP.2.4.3.8.1#NIVEL_DE_DISENO"
CITA_NIVEL_AASHTO = "AASHTO_LRFD_9.3.7.1#NIVEL_DE_DISENO"


def _seccion_del_docstring(doc: str, titulo: str) -> str:
    """El apartado `titulo` (subrayado con guiones) de un docstring de
    modulo, hasta el apartado siguiente, con los espacios normalizados."""
    resto = doc.split(titulo + "\n", 1)[1]
    cuerpo = resto.split("\n", 1)[1]                  # la linea de guiones
    cuerpo = re.split(r"\n[^\n]+\n-{4,}\n", cuerpo, maxsplit=1)[0]
    return " ".join(cuerpo.split())


def _plano(texto: str) -> str:
    return " ".join(texto.split())


def _ficha(nombre: str) -> str:
    texto = REGISTRO.read_text(encoding="utf-8")
    inicio = texto.index(f"\n## {nombre} · ")
    fin = texto.find("\n## ", inicio + 1)
    return texto[inicio:fin if fin != -1 else len(texto)]


# ===========================================================================
# (c1) · la justificacion de V7 es la de la norma, no la del sitio
# ===========================================================================

# Mutante medido: devolver al `por_que` la frase «En el Bajo Piura, con NF
# somero y arenas saturadas, no es un caso de laboratorio.» -> muere aqui.
def test_c1_el_por_que_de_v7_no_se_apoya_en_el_sitio():
    por_que = _plano(FUNDAMENTOS["F5.V7"].por_que)
    assert "Bajo Piura" not in por_que and "NF somero" not in por_que
    for necesario in ("Propietario", "2.4.3.8.1", "[A]", "conservadora",
                      "0.90"):
        assert necesario in por_que, necesario


# Mutante medido: quitar `CITA_NIVEL_MP` de las citas de F5.V7 -> muere aqui
# (y el registro la declara huerfana).
def test_c1_el_fundamento_de_v7_cita_el_nivel_de_diseno_del_propietario():
    reg = construir()
    assert CITA_NIVEL_MP in FUNDAMENTOS["F5.V7"].citas
    c = reg.cita(CITA_NIVEL_MP)
    assert c.numeral == "2.4.3.8.1"
    assert (c.pagina_impresa, c.pagina_pdf) == ("113", 114)
    assert c.caracter is Caracter.EXIGENCIA
    assert c.texto_literal.texto == (
        "Los niveles de agua de diseño para los diferentes estados límites "
        "serán los especificados y/o aprobados por el Propietario.")
    gemela = reg.cita(CITA_NIVEL_AASHTO)
    assert (gemela.numeral, gemela.pagina_impresa, gemela.pagina_pdf) == (
        "3.7.1", "3-45", 99)
    assert gemela.texto_literal.texto == (
        "Design water levels for various limit states shall be as "
        "specified and/or approved by the Owner.")
    assert CITA_NIVEL_AASHTO in c.corresponde_en
    assert not reg.problemas_de_integridad()


@pytest.mark.pdf
@pytest.mark.parametrize("cita_id", [CITA_NIVEL_MP, CITA_NIVEL_AASHTO])
def test_c1_el_literal_del_nivel_de_diseno_esta_en_su_pagina(cita_id):
    """Cada literal, leido otra vez en su pagina del PDF (sin espacios)."""
    import fitz
    c = construir().cita(cita_id)
    ruta = fuentes.ruta_pdf(fuentes.FUENTES[c.fuente_id])
    if not ruta.exists():
        pytest.skip(f"no esta el PDF de {c.fuente_id}")
    texto = fitz.open(str(ruta))[c.pagina_pdf - 1].get_text()
    plano = lambda t: "".join(t.split())                    # noqa: E731
    assert plano(c.texto_literal.texto) in plano(texto)


# Mutante medido: devolver al apartado la frase del NF somero de la llanura
# del Bajo Piura -> muere aqui.
def test_c1_m8_justifica_la_sumersion_completa_con_la_norma():
    apartado = _seccion_del_docstring(M8.__doc__,
                                      "Por que U asume sumersion completa")
    # La justificacion va ANTES del parrafo que cuenta lo que se reemplazo,
    # y es ese parrafo el unico que puede nombrar el argumento de sitio.
    justificacion, historia = apartado.split("HASTA VE-2", 1)
    assert "Bajo Piura" not in justificacion and "somero" not in justificacion
    assert "Bajo Piura" in historia and "no es portable" in historia
    for necesario in ("2.4.3.8.1", "Propietario", "[A]", "conservadora",
                      "12.6.2.3", "highest anticipated groundwater level"):
        assert necesario in justificacion, necesario


def test_c1_m8_dice_que_dc_cero_esta_del_lado_seguro_frente_al_0_90():
    apartado = _seccion_del_docstring(
        M8.__doc__, "Por que el peso propio del conducto no entra en V7")
    for necesario in ("Tabla 2.4.5.3.1-2", "0.90", "2.4.5.3.1",
                      "C12.6.2.3", "lado seguro"):
        assert necesario in apartado, necesario


def test_c1_v7_y_el_empuje_nombran_al_propietario():
    for doc in (M5.v7_flotacion.__doc__, M8.empuje_flotacion_kn_m.__doc__):
        texto = _plano(doc)
        assert "Bajo Piura" not in texto
        assert "2.4.3.8.1" in texto and "Propietario" in texto


# --- la equivalencia de VE1-02 (c), medida con el codigo -------------------

def _relleno_que_equilibra(gamma_ev: float) -> float:
    """
    La altura de relleno sobre la clave con la que V7 queda en el limite,
    gamma_EV · gamma_r · Bc · H = gamma_WA · U, para el tubo de concreto de
    0.90 m con su espesor de archivo, en multiplos del diametro exterior.
    Las piezas son las de produccion: `M8.empuje_flotacion_kn_m`, el ancho
    exterior de la seccion y el gamma_WA de `factores_carga_flotacion`.
    """
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    seccion = SeccionCircular(D=0.90)
    t = espesor_pared(material, seccion.altura)
    U = M8.empuje_flotacion_kn_m(seccion=seccion, espesor=t)
    g = M8.factores_carga_flotacion(material=material)
    gamma_r = ca.CRITERIOS["peso_especifico_relleno_kn_m3"].valor
    Bc = seccion.ancho_exterior(t)
    H = g.gamma_WA * U / (gamma_ev * gamma_r * Bc)
    return H / Bc


def test_c1_la_equivalencia_de_v7_es_0_50_d_ext_con_el_gamma_de_v7():
    """
    Con el gamma_EV que V7 aplica (0.90, el minimo de la fila del conducto)
    el relleno que equilibra la subpresion es 0.50 veces el diametro
    exterior; 0.45 sale con gamma_EV = 1.00, o sea con pesos sin factorar.
    Las dos, en forma cerrada: gamma_WA·gamma_agua·pi / (4·gamma_EV·gamma_r).
    """
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    g = M8.factores_carga_flotacion(material=material)
    assert g.gamma_EV == pytest.approx(0.90, rel=REL_TRANSPORTE)
    assert g.gamma_WA == pytest.approx(1.0, rel=REL_TRANSPORTE)
    gamma_r = ca.CRITERIOS["peso_especifico_relleno_kn_m3"].valor
    cerrada = lambda gev: (g.gamma_WA * GAMMA_AGUA_KN_M3 * math.pi    # noqa: E731
                           / (4 * gev * gamma_r))
    assert _relleno_que_equilibra(g.gamma_EV) == pytest.approx(
        cerrada(0.90), rel=REL_RECALCULADO)
    assert _relleno_que_equilibra(g.gamma_EV) == pytest.approx(
        0.50, abs=MEDIA_CENTESIMA)
    assert _relleno_que_equilibra(1.00) == pytest.approx(
        0.45, abs=MEDIA_CENTESIMA)


# Mutante medido: devolver a la ficha «equivalen a un relleno de unas 0.45
# veces el diámetro exterior» sin el gamma -> muere aqui.
def test_c1_la_ficha_ve1_02_c_dice_0_50_con_gamma_ev_0_90():
    ficha = _ficha("VE1-02")
    c = ficha.split("(c)", 1)[1].split("(d)", 1)[0]
    assert "unas 0.45 veces el diámetro exterior." not in _plano(c)
    assert "0.50 veces el diámetro exterior con γ_EV = 0.90" in _plano(c)
    assert "0.45" in c and "γ_EV = 1.00" in c
    # El inciso propio, cerrado en una linea.
    assert re.search(r"^- \*\*Cerrado \(VE-2\), \(c1\):\*\*", ficha, re.M)


def test_c1_la_ficha_ve2_c_existe_y_cita_lo_verificado():
    ficha = _plano(_ficha("VE2-C"))
    assert "V7: el nivel de agua de diseño es una elección [A] del Propietario" \
        in ficha
    for necesario in ("2.4.3.8.1", "pág. impresa 113", "3.7.1", "12.6.1",
                      "12.6.2.3", "C12.6.2.3", "Tabla 2.4.5.3.1-2",
                      "0.50", "Bajo Piura"):
        assert necesario in ficha, necesario


# ===========================================================================
# (c2) · el nivel de agua de diseño de V7, criterio [A] declarable
# ===========================================================================
# Bloque 4 de VE-2. El nivel lo fija el Propietario (MP 2.4.3.8.1), y el
# proyecto lo ADOPTA en la clave: 'nivel_agua_diseno_v7' = 'en_la_clave', que
# es exactamente lo que V7 calculaba (la linea base no se mueve). La
# alternativa 'nf_del_punto' lee la columna NF_profundidad_m del punto, le
# suma el ascenso estacional 'margen_estacional_nf_v7_m' ([A] SIN valor: la
# lectura de campo no es el nivel mas alto previsto de AASHTO 12.6.2.3, y
# rellenar el margen con 0 seria inventarlo) y evalua V7 solo si el fondo del
# conducto queda bajo ese nivel (AASHTO 12.6.1); si no, «no aplica» con su
# motivo. El relleno bajo el nivel pesa sumergido, gamma' = gamma_sat -
# gamma_agua, por analogia [N->] con el Manual de Puentes 2.4.4.1.3; gamma_sat
# es el criterio de ensayo 'peso_especifico_saturado_relleno_kn_m3', que sin
# valor detiene (nunca un default).

from src.modelos import (CriterioPendienteError, DatoFaltanteError,      # noqa: E402
                         DatoInvalidoError, EstadoDeVerificacion, Familia,
                         Libre, PuntoCritico, SeccionRectangular)
from src.tolerancias import TOL_UMBRAL_NORMATIVO                          # noqa: E402
from tests.apoyo.criterios import declarados                              # noqa: E402

CLAVE_NIVEL = "nivel_agua_diseno_v7"
CLAVE_MARGEN = "margen_estacional_nf_v7_m"
CLAVE_SATURADO = "peso_especifico_saturado_relleno_kn_m3"
CONCRETO = TipoMaterial.CONCRETO_REFORZADO
CITA_SUMERGIDO = "MP.2.4.4.1.3#SUMERGIDO"


def _punto(**cambios) -> PuntoCritico:
    """
    El cruce A-01 del fixture del repositorio. Con la regla de archivo
    'origen_cota_fondo_entrada' = 'cota_terreno' el invert interior queda en
    42.10; con D = 0.90 y la pared de archivo t = 0.10 m, la clave fisica en
    43.10 y el fondo EXTERIOR en 42.00, y sobre la clave 0.95 m de relleno
    hasta la subrasante (44.05). DATOS DE PRUEBA.
    """
    base = dict(
        id="A-01", progresiva_km=0.380, progresiva_display="0+380",
        familia=Familia.A, Q_m3s=1.1673, area_ha=850.0, S_cauce=0.006,
        cota_terreno=42.10, cota_rasante=44.20, cota_subrasante=44.05,
        cbr_subrasante=8.5, esviaje_grados=15.0, ancho_plataforma=9.60,
        cota_fondo_receptor=41.30, Q_receptor_m3s=None, cota_TW=None,
        sucs_fundacion="SM", NF_profundidad_m=None)
    base.update(cambios)
    return PuntoCritico(**base)


def _v7(punto, seccion=None, material=None):
    return M5.v7_flotacion(punto=punto,
                           material=material or catalogo(CONCRETO),
                           seccion=seccion or SeccionCircular(D=0.90),
                           resultado=None)


def _segmento(D: float, h: float) -> float:
    """Area de un circulo de diametro D bajo una cuerda a altura h."""
    theta = 2 * math.acos(1 - 2 * h / D)
    return (D ** 2 / 8) * (theta - math.sin(theta))


GAMMA_R = 17.0          # 'peso_especifico_relleno_kn_m3' de archivo
BC = 1.10               # D + 2t, el tubo de 0.90 con t = 0.10
H_REL = 44.05 - 43.10   # relleno sobre la clave fisica


# --- las dos fichas --------------------------------------------------------

def test_c2_el_nivel_de_agua_de_diseno_es_un_criterio_a_de_perfil():
    c = ca.CRITERIOS[CLAVE_NIVEL]
    assert c.valor == "en_la_clave"
    assert (c.etiqueta, c.forma, c.nivel) == ("A", ca.FORMA_CATEGORIA,
                                              ca.NIVEL_PERFIL)
    assert "en_la_clave" in c.sensibilidad and "nf_del_punto" in c.sensibilidad
    assert isinstance(c.resolucion, Libre)
    assert "Propietario" in c.resolucion.que_lo_fija
    for necesario in ("2.4.3.8.1", "12.6.1", "2.4.4.1.3"):
        assert necesario in c.fuente, necesario
    # La categoria es cerrada: un nivel que no es de la ventana no entra.
    with pytest.raises(ValueError):
        ca.verificar_declaracion(CLAVE_NIVEL, "en_el_terreno")


def test_c2_el_margen_estacional_es_un_a_de_perfil_sin_valor():
    c = ca.CRITERIOS[CLAVE_MARGEN]
    assert c.valor is None and not c.opcional
    assert (c.etiqueta, c.forma, c.nivel) == ("A", ca.FORMA_FLOAT,
                                              ca.NIVEL_PERFIL)
    assert c.sensibilidad is not None and c.resolucion is not None
    assert CLAVE_MARGEN in ca.criterios_de_perfil_sin_valor()
    assert "12.6.2.3" in c.fuente or "12.6.2.3" in c.justificacion


# --- con el valor de archivo, V7 es la de siempre --------------------------

def test_c2_con_el_valor_de_archivo_v7_no_lee_el_nf_y_registra_el_criterio():
    ca.reiniciar_usos()
    v = {nf: _v7(_punto(NF_profundidad_m=nf)) for nf in (None, 0.05, 10.0)}
    assert len({(x.valor_obtenido, x.valor_admisible) for x in v.values()}) == 1
    x = v[None]
    assert x.valor_admisible == pytest.approx(M8.empuje_flotacion_kn_m(
        seccion=SeccionCircular(D=0.90), espesor=0.10), rel=REL_TRANSPORTE)
    assert x.valor_obtenido == pytest.approx(0.90 * GAMMA_R * BC * H_REL,
                                             rel=REL_RECALCULADO)
    assert CLAVE_NIVEL in ca.criterios_usados()
    assert CLAVE_MARGEN not in ca.criterios_usados()
    eleccion = [e for e in x.paso.elecciones if e.clave_criterio == CLAVE_NIVEL]
    assert len(eleccion) == 1 and "en_la_clave" in eleccion[0].valor
    assert eleccion[0].cita_id == CITA_NIVEL_MP


# --- la alternativa: lee el NF del punto ------------------------------------

def test_c2_con_nf_del_punto_sin_nf_es_dato_faltante():
    with declarados({CLAVE_NIVEL: "nf_del_punto"}):
        with pytest.raises(DatoFaltanteError) as exc:
            _v7(_punto(NF_profundidad_m=None))
    assert exc.value.campo == "NF_profundidad_m"


def test_c2_con_nf_del_punto_sin_margen_es_criterio_pendiente():
    with declarados({CLAVE_NIVEL: "nf_del_punto"}):
        with pytest.raises(CriterioPendienteError) as exc:
            _v7(_punto(NF_profundidad_m=0.50))
    assert exc.value.clave == CLAVE_MARGEN


# Mutante medido: comparar el nivel con la CLAVE en vez del fondo exterior
# (o devolver un «cumple» en vez de NO_APLICA) -> muere aqui.
def test_c2_con_el_nivel_bajo_el_fondo_v7_no_aplica_y_lo_dice():
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 0.0}):
        v = _v7(_punto(NF_profundidad_m=0.50))        # nivel 41.60 < 42.00
    assert v.estado is EstadoDeVerificacion.NO_APLICA
    assert v.codigo == "V7" and v.cumple
    for necesario in ("12.6.1", "41.600", "42.000", "nf_del_punto",
                      "inverts below the water table"):
        assert necesario in v.motivo_no_aplica, necesario


def test_c2_sumersion_parcial_empuja_solo_lo_que_queda_bajo_el_nivel():
    """Nivel 42.05: 5 cm sobre el fondo exterior. U es el segmento."""
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 0.0}):
        v = _v7(_punto(NF_profundidad_m=0.05))
    h = (42.10 - 0.05) - 42.00
    assert v.estado is not EstadoDeVerificacion.NO_APLICA
    assert v.valor_admisible == pytest.approx(
        1.00 * GAMMA_AGUA_KN_M3 * _segmento(BC, h), rel=REL_RECALCULADO)
    assert v.valor_admisible < 0.05 * M8.empuje_flotacion_kn_m(
        seccion=SeccionCircular(D=0.90), espesor=0.10)
    # El relleno queda entero en seco: no hace falta el saturado (sin valor).
    assert v.valor_obtenido == pytest.approx(0.90 * GAMMA_R * BC * H_REL,
                                             rel=REL_RECALCULADO)


def test_c2_con_el_nivel_sobre_la_clave_sin_saturado_es_criterio_pendiente():
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 1.50}):
        with pytest.raises(CriterioPendienteError) as exc:
            _v7(_punto(NF_profundidad_m=0.10))       # nivel 43.50
    assert exc.value.clave == CLAVE_SATURADO


# Mutante medido: pesar el relleno sumergido con gamma_sat en vez de
# gamma_sat - gamma_agua -> muere aqui.
def test_c2_el_relleno_bajo_el_nivel_pesa_sumergido():
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 1.50,
                     CLAVE_SATURADO: 20.0}):
        v = _v7(_punto(NF_profundidad_m=0.10))       # nivel 43.50
    h_sum = 43.50 - 43.10
    EV = BC * (GAMMA_R * (H_REL - h_sum) + (20.0 - GAMMA_AGUA_KN_M3) * h_sum)
    assert v.valor_obtenido == pytest.approx(0.90 * EV, rel=REL_RECALCULADO)
    assert v.valor_admisible == pytest.approx(M8.empuje_flotacion_kn_m(
        seccion=SeccionCircular(D=0.90), espesor=0.10), rel=REL_TRANSPORTE)
    assert CITA_SUMERGIDO in v.paso.citas_textuales


def test_c2_sobre_la_subrasante_todo_el_relleno_va_sumergido():
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 3.0,
                     CLAVE_SATURADO: 20.0}):
        v = _v7(_punto(NF_profundidad_m=0.10))       # nivel 45.00 > 44.05
    EV = BC * (20.0 - GAMMA_AGUA_KN_M3) * H_REL
    assert v.valor_obtenido == pytest.approx(0.90 * EV, rel=REL_RECALCULADO)


def test_c2_con_el_nivel_en_la_clave_las_dos_reglas_coinciden():
    """
    nf_del_punto con el nivel justo en la clave (42.10 - 0.10 + 1.10) es la
    misma hipotesis que 'en_la_clave': mismo U, mismo EV, y el ruido
    flotante de la cota no obliga a declarar el saturado.
    """
    archivo = _v7(_punto(NF_profundidad_m=0.10))
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 1.10}):
        nf = _v7(_punto(NF_profundidad_m=0.10))
    assert nf.valor_admisible == pytest.approx(archivo.valor_admisible,
                                               rel=REL_RECALCULADO)
    assert nf.valor_obtenido == pytest.approx(archivo.valor_obtenido,
                                              rel=REL_RECALCULADO)


def test_c2_en_un_marco_el_volumen_bajo_el_nivel_es_un_rectangulo():
    seccion = SeccionRectangular(B=2.00, H=1.50)
    t = 0.20
    for h in (0.05, 0.80):
        assert M8.empuje_flotacion_bajo_el_nivel_kn_m(
            seccion=seccion, espesor=t, altura_agua=h) == pytest.approx(
                GAMMA_AGUA_KN_M3 * seccion.ancho_exterior(t) * h,
                rel=REL_RECALCULADO)
    # Sobre el canto exterior, el empuje es el del conducto entero.
    assert M8.empuje_flotacion_bajo_el_nivel_kn_m(
        seccion=seccion, espesor=t, altura_agua=10.0) == pytest.approx(
            M8.empuje_flotacion_kn_m(seccion=seccion, espesor=t),
            rel=REL_TRANSPORTE)
    # Y en una circular, el segmento.
    circ = SeccionCircular(D=0.90)
    assert M8.empuje_flotacion_bajo_el_nivel_kn_m(
        seccion=circ, espesor=0.10, altura_agua=0.30) == pytest.approx(
            GAMMA_AGUA_KN_M3 * _segmento(1.10, 0.30), rel=REL_RECALCULADO)


def test_c2_las_piezas_publicas_de_m8_por_su_nombre():
    """
    Las cuatro funciones publicas que V7 compone, llamadas por su nombre (la
    guardia de la suite exige que un test las nombre): la regla leida y
    registrada, la pregunta del pre-vuelo que no registra, la cota del nivel
    con sus dos lecturas, y el relleno bajo el nivel en sus dos ramas.
    """
    ca.reiniciar_usos()
    assert M8.v7_lee_el_nivel_freatico() is False
    assert CLAVE_NIVEL not in ca.criterios_usados()
    assert M8.regla_nivel_agua_v7() == "en_la_clave"
    assert CLAVE_NIVEL in ca.criterios_usados()
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 0.25}):
        assert M8.v7_lee_el_nivel_freatico() is True
        cota, nf, margen = M8.cota_nivel_agua_v7_del_nf(
            punto=_punto(NF_profundidad_m=0.80))
    assert (nf, margen) == (pytest.approx(0.80, rel=REL_TRANSPORTE),
                            pytest.approx(0.25, rel=REL_TRANSPORTE))
    assert cota == pytest.approx(42.10 - 0.80 + 0.25, rel=REL_RECALCULADO)
    seco, sin_saturado = M8.peso_relleno_bajo_el_nivel_kn_m(
        seccion=SeccionCircular(D=0.90), espesor=0.10, altura_relleno=H_REL,
        altura_sumergida=0.0)
    assert sin_saturado is None
    assert seco == pytest.approx(M8.peso_relleno_kn_m(
        seccion=SeccionCircular(D=0.90), espesor=0.10, altura_relleno=H_REL),
        rel=REL_TRANSPORTE)
    with declarados({CLAVE_SATURADO: 21.0}):
        mojado, saturado = M8.peso_relleno_bajo_el_nivel_kn_m(
            seccion=SeccionCircular(D=0.90), espesor=0.10,
            altura_relleno=H_REL, altura_sumergida=10.0)
    assert saturado == pytest.approx(21.0, rel=REL_TRANSPORTE)
    assert mojado == pytest.approx(BC * (21.0 - GAMMA_AGUA_KN_M3) * H_REL,
                                   rel=REL_RECALCULADO)


def test_c2_un_margen_negativo_es_dato_invalido():
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: -0.10}):
        with pytest.raises(DatoInvalidoError) as exc:
            _v7(_punto(NF_profundidad_m=0.50))
    assert exc.value.campo == CLAVE_MARGEN


def test_c2_un_saturado_que_no_supera_al_agua_es_dato_invalido():
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 1.50,
                     CLAVE_SATURADO: 9.0}):
        with pytest.raises(DatoInvalidoError) as exc:
            _v7(_punto(NF_profundidad_m=0.10))
    assert exc.value.campo == CLAVE_SATURADO


def test_c2_el_paso_dice_de_donde_sale_el_nivel():
    with declarados({CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 0.0}):
        v = _v7(_punto(NF_profundidad_m=0.05))
    eleccion = [e for e in v.paso.elecciones if e.clave_criterio == CLAVE_NIVEL]
    assert len(eleccion) == 1
    assert "nf_del_punto" in eleccion[0].valor and "42.050" in eleccion[0].valor
    nombres = {m.simbolo for m in v.paso.sustitucion}
    assert {"cota_nivel_agua", "NF", "margen_estacional"} <= nombres


def test_c2_el_fundamento_de_la_eleccion_se_sostiene_y_cita_la_analogia():
    reg = construir()
    f = FUNDAMENTOS["F5.V7_NIVEL"]
    assert CITA_NIVEL_MP in f.citas and CITA_SUMERGIDO in f.citas
    assert "ANALOGIA" in f.por_que
    c = reg.cita(CITA_SUMERGIDO)
    assert (c.numeral, c.pagina_impresa, c.pagina_pdf) == ("2.4.4.1.3", "133",
                                                           134)
    assert c.texto_literal.texto == (
        "Para determinar el empuje lateral del suelo debajo del nivel "
        "freático se deberán utilizar las densidades del suelo sumergido.")
    assert not reg.problemas_de_integridad()


@pytest.mark.pdf
def test_c2_el_literal_del_suelo_sumergido_esta_en_su_pagina():
    test_c1_el_literal_del_nivel_de_diseno_esta_en_su_pagina(CITA_SUMERGIDO)


# --- quien lee la columna, con y sin la alternativa -------------------------

def test_c2_el_censo_le_encuentra_a_v7_como_consumidor_del_nf():
    from src import variables_entrada as ve
    consumidores = set(ve.variable("NF_profundidad_m").consumido_por)
    assert {"M5_verificaciones", "M8_estructural", "M9_cabezal"} <= consumidores
    concepto = ve.variable("NF_profundidad_m").concepto
    assert len(concepto) <= 250, len(concepto)
    for necesario in ("nf_del_punto", "V7", "archivo", "VE2-C"):
        assert necesario in concepto, necesario


def _prevuelo_del_nf(alcance):
    import cli
    from src import anticipo as antc
    externos = cli.cargar_datos_externos(
        RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json",
        dict(luz_m=2.75, TW_m=None, longitud_m=None, L_hidraulico_m=None,
             categoria_tr=None))
    estimado = antc.datos_faltantes_por_punto(
        RAIZ / "tests" / "ejemplo_puntos.csv", externos, alcance)
    return [e for e in estimado if e.dato == "NF_profundidad_m"]


# Mutante medido: que el pre-vuelo ignore el consumo condicional y cuente a
# V7 siempre (o nunca) -> muere aqui, en una de las dos mitades.
def test_c2_el_prevuelo_dice_que_v7_la_exige_solo_con_la_alternativa():
    import cli
    sin = _prevuelo_del_nf(cli.ALCANCE_PERFIL)
    assert sin and all(not e.detiene for e in sin)
    with declarados({CLAVE_NIVEL: "nf_del_punto"}):
        con = _prevuelo_del_nf(cli.ALCANCE_PERFIL)
    assert con and all(e.detiene for e in con)
    assert all("M5_verificaciones" in e.etapa for e in con)


def test_c2_la_fila_del_contrato_dice_las_dos_cosas():
    contrato = (RAIZ / "docs" / "contrato_entradas.md").read_text(
        encoding="utf-8")
    fila = next(l for l in contrato.split("\n")
                if l.startswith("| `NF_profundidad_m` |"))
    for necesario in ("nivel_agua_diseno_v7", "nf_del_punto", "en_la_clave",
                      "V7 no la lee", "margen_estacional_nf_v7_m",
                      "VE2-C"):
        assert necesario in fila, necesario


def test_c2_la_ficha_ve2_c_cierra_c2_y_dice_lo_diferido():
    ficha = _plano(_ficha("VE2-C"))
    assert "Cerrado (VE-2), (c2)" in ficha
    for necesario in ("nivel_agua_diseno_v7", "margen_estacional_nf_v7_m",
                      "12.6.1", "2.4.4.1.3", "[N→]",
                      "peso_especifico_saturado_relleno_kn_m3"):
        assert necesario in ficha, necesario
    ve1_02 = _ficha("VE1-02")
    assert re.search(r"^- \*\*Cerrado \(VE-2\), \(c2\):\*\*", ve1_02, re.M)


# --- de punta a punta -------------------------------------------------------

def _corrida_de_perfil(tmp_path, nf: str, declaraciones: dict):
    import json as _json
    import cli
    from src import servicio
    csv = tmp_path / f"p1_{nf or 'sin_nf'}.csv"
    csv.write_text(
        "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,"
        "cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,"
        "ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,"
        "sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,"
        "cota_coronacion_canal\n"
        f"P1,0+100,A,1.0,50,0.005,100.0,104.0,103.85,10,0,9.0,99.5,,,SM,"
        f"{nf},,\n", encoding="utf-8")
    ext = tmp_path / "externos.json"
    ext.write_text(_json.dumps({"globales": {"luz_m": 3.0, "TW_m": 0.3}}),
                   encoding="utf-8")
    externos = cli.cargar_datos_externos(
        ext, {"luz_m": None, "TW_m": None, "longitud_m": None,
              "L_hidraulico_m": None, "categoria_tr": None})
    with declarados(declaraciones):
        informe = servicio.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
    return cli.informe_json(informe)


def _v7_del_volcado(volcado):
    (p,) = volcado["puntos"]
    v7 = [v for v in p["verificaciones"] if v["codigo"] == "V7"]
    return p, (v7[0] if v7 else None)


def test_c2_de_punta_a_punta_la_alternativa_no_aplica_o_detiene(tmp_path):
    """
    P1 (el cruce sintetico de Familia A de VE-1, DATOS DE PRUEBA) lleva el
    invert en el terreno natural (regla de archivo 'cota_terreno'): con el
    NF a 1.40 m y sin margen, el nivel de diseño queda 1.30 m bajo el fondo
    exterior y V7 «no aplica»; sin NF, la alternativa detiene el punto con
    «dato faltante». Con el valor de archivo, V7 es la de siempre.
    """
    _p, v7 = _v7_del_volcado(_corrida_de_perfil(tmp_path, "1.40", {}))
    assert v7 is not None and v7["estado"] == "cumple"
    _p, v7 = _v7_del_volcado(_corrida_de_perfil(
        tmp_path, "1.40", {CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 0.0}))
    assert v7 is not None and v7["estado"] == "no aplica", v7
    p, _v = _v7_del_volcado(_corrida_de_perfil(
        tmp_path, "", {CLAVE_NIVEL: "nf_del_punto", CLAVE_MARGEN: 0.0}))
    assert not p["dimensionado"]
    assert "NF_profundidad_m" in str(p["bloqueos"])
