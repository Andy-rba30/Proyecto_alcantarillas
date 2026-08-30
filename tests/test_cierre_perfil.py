"""
tests/test_cierre_perfil.py
===========================
El cierre del nivel de PERFIL, comprobado sobre el producto y no sobre el
codigo.

Tres cosas que ningun otro archivo de la suite comprueba, y las tres son el
criterio de salida de S20:

    1. `--alcance perfil` corre DE PUNTA A PUNTA sobre un CSV con todos los
       datos externos presentes. Hasta S20 la corrida se detenia en la Fase 2
       por falta de `luz_m`, y la auditoria normativa lo dejo escrito como
       limitacion de su propio bloque G (`R48-041`): «lo que solo se imprime
       en Fase 5 no esta cubierto por esta auditoria». Aqui esta cubierto.
    2. La memoria contra un CASO RESUELTO A MANO. Los numeros de abajo se
       calcularon con aritmetica independiente --- brentq sobre las formulas
       escritas de nuevo, sin llamar a M3, M4 ni M7 --- y despues se
       contrastaron contra el HTML generado. Un test que llama a la misma
       funcion que quiere verificar no verifica nada.
    3. Ningun [A] de perfil sin valor, sin sensibilidad y sin procedencia, y
       la clasificacion perfil/expediente contrastada contra lo que la corrida
       INVOCA de verdad, no contra una lista escrita a mano.

POR QUE EL CSV ES OTRO. `tests/ejemplo_puntos.csv` trae `Q_receptor_m3s` y
`cota_TW` vacias en las cuatro filas, que es el estado del expediente cuando
esas dos columnas no existian para nadie (SIS-B-04). Ese archivo se conserva
tal cual: es el que sostiene los tests de bloqueo. El de aqui,
`ejemplo_puntos_perfil.csv`, es el mismo corredor con los datos externos que
el nivel de perfil si tiene, y es el unico con el que se puede ejercitar la
Sec. 1.3 entera.
"""

import math
import re
import sys
from pathlib import Path

import pytest
from scipy.optimize import brentq

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import cli                                                        # noqa: E402
import criterios_adoptados as ca                                  # noqa: E402
from modelos import SeccionReceptor, ViaDelTW                     # noqa: E402
from modulos import M11_reporte as M11                            # noqa: E402
from modulos import M3_hidraulica as M3                           # noqa: E402
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE     # noqa: E402
from tests.apoyo.criterios import sin_valor                       # noqa: E402

CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"

# Tolerancias de contraste contra el caso a mano. La de longitud y cotas es
# el milimetro; la de velocidades y tirantes, la decima de milimetro. No son
# tolerancias de convergencia --- esas viven en `tolerancias.py` --- sino de
# COMPARACION entre dos calculos independientes de la misma magnitud, y se
# eligen en el orden de la cifra que la memoria imprime.
TOL_COTA = 1e-3
TOL_FINA = 1e-4

# Los datos externos del corredor que no son columna de Sec. 1.2. La luz de
# 3.0 m sale del ancho del cauce en el cruce y es lo que separa alcantarilla
# de puente (num. 4.1.1.3.1); el caudal y la pendiente de C-01 son los del
# CANAL, no los de una quebrada (Sec. 2.3, Familia C).
EXTERNOS_GLOBALES = dict(luz_m=3.0, L_hidraulico_m=120.0, TW_m=None,
                         longitud_m=None, categoria_tr=None)
EXTERNOS_POR_PUNTO = {"C-01": {"Q_m3s": 0.65, "S_conducto": 0.004}}


# Los criterios que ESTA corrida invoco. `criterios_adoptados` acumula los
# usos en un registro global -- que es lo correcto: la memoria imprime lo que
# el calculo consumio a lo largo de la corrida entera --, y en una suite ese
# registro lleva ademas lo que invocaron los tests anteriores. Los dos tests
# de clasificacion de mas abajo miden lo que la corrida DE PERFIL invoca, no
# lo que la suite acumulo, y por eso se toma la foto aqui: se vacia, se corre,
# se lee, y se devuelve la union para no dejar sin sus usos a lo que venga
# despues.
USADOS_POR_LA_CORRIDA: set = set()


@pytest.fixture(scope="module")
def informe_perfil():
    externos = cli.cargar_datos_externos(None, EXTERNOS_GLOBALES)
    for id_punto, datos in EXTERNOS_POR_PUNTO.items():
        externos.por_punto.setdefault(id_punto, {}).update(
            {clave: cli.DatoDeclarado(clave, valor, "datos del expediente")
             for clave, valor in datos.items()})
    previos = set(ca._USADOS)
    ca._USADOS.clear()
    try:
        informe = cli.correr(CSV_PERFIL, externos, alcance=cli.ALCANCE_PERFIL)
        USADOS_POR_LA_CORRIDA.update(ca._USADOS)
    finally:
        ca._USADOS.update(previos)
    return informe


@pytest.fixture(scope="module")
def memoria(informe_perfil):
    """
    La memoria CON LA PLANTILLA DE PERFIL, que es la que la CLI elige para
    esta corrida. No es un detalle de fixture: las dos plantillas comparten
    el contrato de marcadores pero no imprimen los mismos bloques, y usar la
    de expediente aqui mediria un documento que nadie va a emitir (SIS-B-06).
    """
    return M11.memoria_html(
        informe_perfil, proyecto="cierre del nivel de perfil",
        ruta_plantilla=M11.DIR_PLANTILLAS / M11.NOMBRE_PLANTILLA_PERFIL)


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


# ===========================================================================
# 1 - La corrida llega a la Fase 5, que es lo que R48-041 no pudo medir
# ===========================================================================

def test_la_corrida_de_perfil_pasa_de_la_fase_2_y_dimensiona(informe_perfil):
    """
    Los tres puntos de conducto circular cierran. C-01 no, y no es un fallo:
    la Familia C es marco o multicelda (Sec. 2.3) y el catalogo de Sec. 3.2
    es circular. La distincion importa y por eso se comprueba: un punto que
    no cierra por falta de dato y uno que no cierra porque es otra forma de
    estructura se corrigen de forma distinta.
    """
    dimensionados = {p.punto.id for p in informe_perfil.puntos if p.dimensionado}
    assert dimensionados == {"A-01", "A-02", "B-01"}

    c01 = _punto(informe_perfil, "C-01")
    assert not c01.dimensionado
    motivos = " ".join(b.mensaje for b in c01.bloqueos)
    assert "no es no-factible, es de otra forma de estructura" in motivos


def test_las_nueve_verificaciones_de_perfil_llegan_a_la_memoria(informe_perfil):
    """
    La limitacion `R48-041` de la auditoria normativa, cerrada: su bloque G
    se midio sobre una corrida detenida en Fase 2, donde V4 y 7.A nunca se
    ejecutan. Aqui se ejecutan las nueve obligatorias del alcance de perfil.
    """
    a01 = _punto(informe_perfil, "A-01")
    codigos = [v.codigo for _, v in a01.verificaciones() if v.codigo]
    assert codigos == ["V1", "V2", "V2b", "V3", "V4", "V4b", "V6",
                       "V7", "V9", "G1", "G2"]
    assert all(v.cumple for _, v in a01.verificaciones())


def test_lo_diferido_esta_listado_con_fundamento_en_el_bloque_de_alcance(
        informe_perfil, memoria):
    """
    Criterio de salida: «todo lo diferido aparece listado con fundamento en
    el bloque de alcance». Se comprueba sobre el HTML, que es donde el
    revisor lo lee, y no solo sobre el objeto.
    """
    diferidos = informe_perfil.diferidos()
    assert diferidos, "una corrida de perfil sin nada diferido no es de perfil"

    # Las tres familias de diferimiento del alcance de perfil, cada una con
    # su fundamento en el documento.
    etapas = {b.etapa for _id, b in diferidos}
    assert any("V5" in e for e in etapas)
    assert any("V8" in e for e in etapas)
    assert any("Fase 8" in e for e in etapas)
    assert any("Fase 9" in e for e in etapas)

    bloque = memoria.split("4. Alcance y diferimientos")[1].split("<h2")[0]
    for _id_punto, b in diferidos:
        assert b.etapa in bloque or b.mensaje[:60] in bloque, b.etapa
    # Y el fundamento, no solo el rotulo: la fuente que cerraria el criterio.
    assert "DG-2018" in bloque and "Ley 29338" in bloque


def test_ninguna_fila_de_la_fase_5_queda_sin_evaluar(memoria):
    """
    Lo que SIS-A-13 y MAT-O15 reprochaban: contar diez verificaciones donde
    la hoja de ruta lista once, y dejar la resta al lector. La memoria lo
    dice ahora en positivo.
    """
    assert "Las ONCE filas de la tabla de Fase 5" in memoria


# ===========================================================================
# 2 - La memoria contra el caso resuelto a mano (A-01)
# ===========================================================================
#
# Todo lo de abajo se calcula aqui, con las formulas escritas de nuevo. Si
# alguna coincidiera con la del modulo por copiarla, el test no valdria nada:
# se escriben desde la fuente (Manning, la seccion circular de Sec. 4.1, la
# ec. de Froude de Sec. 4.2.1, el control de salida de Sec. 4.3) y se comparan
# contra lo que el pipeline produjo.

A01 = dict(Q=1.167, S=0.006, D=0.90, n_min=0.010, n_max=0.013,
           cota_terreno=42.10, cota_rasante=44.20, cota_subrasante=44.05,
           ancho_plataforma=9.60, esviaje=15.0, cota_fondo_receptor=41.30,
           Q_receptor=2.00, talud=2.0, ke=0.5, K_friccion=19.63, G=9.81,
           receptor=dict(b=2.0, z=1.5, S=0.0008, n=0.030))


def _manning_circular(*, Q, S, D, n):
    def f(th):
        A = (D ** 2 / 8) * (th - math.sin(th))
        R = A / (D * th / 2)
        return (1 / n) * A * R ** (2 / 3) * S ** 0.5 - Q
    th = brentq(f, 1e-9, 2 * math.pi - 1e-9, xtol=1e-12)
    A = (D ** 2 / 8) * (th - math.sin(th))
    return th, A, A / (D * th / 2), (D / 2) * (1 - math.cos(th / 2))


def _manning_trapecial(*, Q, b, z, S, n):
    def f(y):
        A = (b + z * y) * y
        R = A / (b + 2 * y * math.sqrt(1 + z ** 2))
        return (1 / n) * A * R ** (2 / 3) * S ** 0.5 - Q
    return brentq(f, 1e-9, 50.0, xtol=1e-12)


def test_la_longitud_de_A01_reproduce_el_calculo_a_mano(informe_perfil):
    """
    7.B: L = (ancho de plataforma + 2*talud*altura de terraplen) / cos(esviaje)

        altura     = 44.20 - 42.10        = 2.10 m
        proyeccion = 2 * 2.0 * 2.10       = 8.40 m
        L          = 18.00 / cos(15 deg)  = 18.63497 m
    """
    d = A01
    altura = d["cota_rasante"] - d["cota_terreno"]
    L = ((d["ancho_plataforma"] + 2 * d["talud"] * altura)
         / math.cos(math.radians(d["esviaje"])))
    assert L == pytest.approx(18.63497, abs=TOL_COTA)
    assert _punto(informe_perfil, "A-01").longitud.valor == pytest.approx(
        L, abs=TOL_COTA)


def test_el_TW_de_A01_reproduce_el_paso_2_de_la_seccion_1_3(informe_perfil):
    """
    Sec. 1.3, pasos 1 y 2, a mano:

        Q del receptor = 2.00 m3/s (columna del CSV, ANA / Junta)
        Manning trapecial (b=2.0, z=1.5, S=0.0008, n=0.030) -> y_n = 0.908237 m
        cota de agua   = 41.30 + 0.908237            = 42.20824 msnm
        cota de salida = 42.10 - 0.006 * 18.63497    = 41.98819 msnm
        TW             = 42.20824 - 41.98819         = 0.220047 m

    Y la VIA queda registrada: si algun dia el TW volviera a salir de un
    criterio declarado sin que nadie lo note, este assert lo dice.
    """
    d = A01
    y_r = _manning_trapecial(Q=d["Q_receptor"], **d["receptor"])
    assert y_r == pytest.approx(0.908237, abs=TOL_FINA)

    altura = d["cota_rasante"] - d["cota_terreno"]
    L = ((d["ancho_plataforma"] + 2 * d["talud"] * altura)
         / math.cos(math.radians(d["esviaje"])))
    cota_salida = d["cota_terreno"] - d["S"] * L
    TW = (d["cota_fondo_receptor"] + y_r) - cota_salida
    assert TW == pytest.approx(0.220047, abs=TOL_FINA)

    a01 = _punto(informe_perfil, "A-01")
    assert a01.tw.valor == pytest.approx(TW, abs=TOL_FINA)
    assert a01.tw_sec13.via is ViaDelTW.MANNING_RECEPTOR
    assert a01.tw_sec13.cota_TW_msnm == pytest.approx(42.20824, abs=TOL_COTA)


def test_la_hidraulica_de_A01_reproduce_el_calculo_a_mano(informe_perfil):
    """
    Sec. 4.1 y 4.2.1 a mano, con la regla de doble n:

        theta = 3.950696 rad   A = 0.473279 m2   R = 0.266214 m
        y_n   = 0.627123 m     y/D = 0.696803
        V con n_max = 0.013 -> 2.465774 m/s   (V2, el piso)
        V con n_min = 0.010 -> 3.205506 m/s   (V3 y Laushey, el techo)
        y_c   = 0.639970 m
    """
    d = A01
    _th, _A, R, y_n = _manning_circular(Q=d["Q"], S=d["S"], D=d["D"],
                                        n=d["n_max"])
    V_sed = (1 / d["n_max"]) * R ** (2 / 3) * d["S"] ** 0.5
    V_ero = (1 / d["n_min"]) * R ** (2 / 3) * d["S"] ** 0.5
    assert (y_n, V_sed, V_ero) == pytest.approx(
        (0.627123, 2.465774, 3.205506), abs=TOL_FINA)

    def froude(th):
        A = (d["D"] ** 2 / 8) * (th - math.sin(th))
        T = d["D"] * math.sin(th / 2)
        return d["Q"] ** 2 * T / (d["G"] * A ** 3) - 1
    thc = brentq(froude, 1e-6, 2 * math.pi - 1e-6, xtol=1e-12)
    y_c = (d["D"] / 2) * (1 - math.cos(thc / 2))
    assert y_c == pytest.approx(0.639970, abs=TOL_FINA)

    h = _punto(informe_perfil, "A-01").resultado.resultado_hidraulico
    assert h.y_normal == pytest.approx(y_n, abs=TOL_FINA)
    assert h.y_critico == pytest.approx(y_c, abs=TOL_FINA)
    assert h.V_sedimentacion == pytest.approx(V_sed, abs=TOL_FINA)
    assert h.V_erosion == pytest.approx(V_ero, abs=TOL_FINA)


def test_el_control_de_salida_de_A01_reproduce_el_calculo_a_mano(
        informe_perfil):
    """
    Sec. 4.3 a mano, con el K de 19.63 (SI) y la seccion LLENA:

        h_o = max(TW, (y_c + D)/2) = max(0.220047, 0.769985) = 0.769985 m
        V   = Q / (pi/4 * D^2)                              = 1.834408 m/s
        H   = (1 + 0.5 + 19.63*0.013^2*18.63497/(0.225)^(4/3)) * V^2/(2g)
            = 0.334746 m
        HW  = H + h_o - S*L                                 = 0.992922 m

    El h_o lo gobierna la aproximacion (y_c + D)/2 y no el TW: es el caso que
    el HDS-5 acota, y por eso la memoria imprime las tres condiciones de uso.
    """
    d = A01
    altura = d["cota_rasante"] - d["cota_terreno"]
    L = ((d["ancho_plataforma"] + 2 * d["talud"] * altura)
         / math.cos(math.radians(d["esviaje"])))

    def froude(th):
        A = (d["D"] ** 2 / 8) * (th - math.sin(th))
        T = d["D"] * math.sin(th / 2)
        return d["Q"] ** 2 * T / (d["G"] * A ** 3) - 1
    y_c = (d["D"] / 2) * (1 - math.cos(
        brentq(froude, 1e-6, 2 * math.pi - 1e-6, xtol=1e-12) / 2))

    h_o = max(0.220047, (y_c + d["D"]) / 2)
    V_llena = d["Q"] / ((math.pi / 4) * d["D"] ** 2)
    H = ((1 + d["ke"]
          + d["K_friccion"] * d["n_max"] ** 2 * L / (d["D"] / 4) ** (4 / 3))
         * V_llena ** 2 / (2 * d["G"]))
    HW_salida = H + h_o - d["S"] * L
    assert HW_salida == pytest.approx(0.992922, abs=TOL_FINA)

    h = _punto(informe_perfil, "A-01").resultado.resultado_hidraulico
    assert h.HW_salida == pytest.approx(HW_salida, abs=TOL_FINA)


def test_los_numeros_del_caso_a_mano_estan_en_la_memoria(memoria):
    """
    El contraste sobre el PRODUCTO. Los numeros de arriba tienen que estar
    IMPRESOS, no solo calculados: es la diferencia entre "el codigo lo hace
    bien" y "la memoria lo dice", que es la trampa de NOR-MEM-01.
    """
    a01 = memoria.split("A-01 &nbsp;")[1].split("A-02 &nbsp;")[0]
    for numero in ("18.635",     # L de 7.B
                   "0.220",      # TW de Sec. 1.3
                   "0.627",      # y_n
                   "0.640",      # y_c
                   "2.466",      # V_sedimentacion (V2)
                   "3.206",      # V_erosion (V3, Laushey)
                   "43.142"):    # V4: cota de entrada + HW
        assert numero in a01, f"la memoria de A-01 no imprime {numero}"


# ===========================================================================
# 3 - El nivel de perfil, cerrado y comprobable
# ===========================================================================

def test_ningun_A_de_perfil_invocado_queda_sin_valor(informe_perfil):
    """
    El criterio de salida, medido sobre lo que la corrida INVOCA de verdad.

    No se lee de una lista: se lee de `criterios_usados()`, que es el registro
    que la propia memoria imprime. Un criterio que gobierna un numero de esta
    memoria y no esta declarado seria un numero sin defensa.
    """
    for clave in sorted(USADOS_POR_LA_CORRIDA):
        c = ca.criterio_efectivo(clave)
        if c.etiqueta != "A":
            continue
        if c.nivel == ca.NIVEL_EXPEDIENTE:
            continue        # V5 y V8: los difiere el alcance, con fundamento
        assert c.valor is not None, f"[A] de perfil sin valor: {clave}"
        assert c.sensibilidad is not None, f"[A] de perfil sin ventana: {clave}"
        assert c.resolucion is not None, f"[A] de perfil sin procedencia: {clave}"


def test_todo_criterio_que_la_corrida_de_perfil_invoca_esta_clasificado(
        informe_perfil):
    """
    La clasificacion perfil/expediente no puede quedar desincronizada del
    codigo, que es como se desincronizan las clasificaciones escritas a mano.

    Un criterio que una corrida de PERFIL invoca es de perfil, salvo que su
    etapa quede DIFERIDA por el alcance --- y eso no se afirma: se lee de los
    bloqueos que la propia corrida marco `diferido_por_alcance`.
    """
    diferidos = {b.criterio for _id, b in informe_perfil.diferidos()
                 if b.criterio}
    for clave in sorted(USADOS_POR_LA_CORRIDA):
        nivel = ca.CRITERIOS[clave].nivel
        assert nivel, f"'{clave}' se invoca y no declara nivel"
        if nivel == ca.NIVEL_EXPEDIENTE:
            assert clave in diferidos, (
                f"'{clave}' esta clasificado como de expediente y la corrida "
                "de perfil lo invoca sin que su etapa quede diferida")


def test_los_dos_vacios_de_perfil_que_quedan_dicen_por_que(informe_perfil):
    """
    Quedan dos, y ninguno es una omision: los dos declaran por que no se
    pudieron cerrar, y ninguno lo invoca esta corrida.

    'TW_receptor'          Sec. 1.3 lo dejo como ULTIMA puerta. Con el
                           expediente aportando el caudal del receptor, la
                           corrida no llega a el.
    'homogeneidad_serie_fen'  No es una eleccion: es un hecho sobre la serie
                           SENAMHI, que no esta en el expediente. Elegir una
                           de sus dos ramas seria afirmar algo sobre un
                           archivo que nadie abrio.
    """
    assert ca.criterios_de_perfil_sin_valor() == ["TW_receptor",
                                                  "homogeneidad_serie_fen"]
    for clave in ca.criterios_de_perfil_sin_valor():
        assert clave not in USADOS_POR_LA_CORRIDA
        assert ca.CRITERIOS[clave].sensibilidad is not None, (
            f"'{clave}' esta vacio y sin ventana: la ventana es parte de la "
            "ficha, no del valor")


# ===========================================================================
# 4 - Sec. 1.3: las cuatro vias, y la que gobierna
# ===========================================================================

SECCION = SeccionReceptor(b_m=2.0, z_HV=1.5, S=0.0008, n=0.030,
                          altura_total_m=1.80)


def _punto_de_prueba(**cambios):
    from modelos import Familia, PuntoCritico
    base = dict(id="X-01", progresiva_km=0.0, progresiva_display="0+000",
                familia=Familia.A, Q_m3s=1.0, area_ha=100.0, S_cauce=0.006,
                cota_terreno=42.10, cota_rasante=44.20, cota_subrasante=44.05,
                cbr_subrasante=8.5, esviaje_grados=0.0, ancho_plataforma=9.60,
                cota_fondo_receptor=41.30, Q_receptor_m3s=None, cota_TW=None,
                sucs_fundacion="SM", NF_profundidad_m=1.40)
    base.update(cambios)
    return PuntoCritico(**base)


def test_la_via_1_es_el_TW_declarado_y_no_necesita_geometria():
    """
    Con el TW a mano no hay cota que restar. Antes de S20 esta rama exigia
    igual la cota de fondo de la salida --- y con ella la pendiente del
    cauce ---, de modo que un punto de Familia C, cuya `S_cauce` va vacia
    porque su pendiente es la del canal, se bloqueaba en el TW en vez de
    llegar al bloqueo que de verdad tiene.
    """
    tw = M3.tw_seccion_1_3(punto=_punto_de_prueba(), cota_fondo_salida=None,
                           tw_declarado=0.35)
    assert tw.valor == pytest.approx(0.35, rel=REL_TRANSPORTE)
    assert tw.via is ViaDelTW.DECLARADO
    assert tw.cota_TW_msnm is None


def test_la_via_2_convierte_la_columna_cota_TW_en_tirante():
    """
    SIS-B-04 medido: «un CSV con `cota_TW` llena sigue exigiendo --tw».
    Tablero 3.1 rotula esa columna «Calculada (1.3)»: es el paso 2 resuelto
    fuera, y lo que faltaba era la resta.
    """
    punto = _punto_de_prueba(cota_TW=42.35)
    tw = M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=42.00)
    assert tw.valor == pytest.approx(0.35, abs=TOL_FINA)
    assert tw.via is ViaDelTW.COTA_TW
    assert tw.cota_TW_msnm == pytest.approx(42.35, abs=TOL_FINA)


def test_una_cota_de_agua_bajo_el_fondo_de_la_salida_es_salida_libre():
    """
    El signo de la resta, que es donde esta el error facil: un TW negativo no
    significa nada fisico. Daria un h_o menor que el de la salida libre, que
    es imposible.
    """
    punto = _punto_de_prueba(cota_TW=41.50)
    tw = M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=42.00)
    assert tw.valor == pytest.approx(0.0, abs=ABS_CERO)


def test_la_via_4_calcula_los_dos_escenarios_y_corre_con_el_gobernante():
    """
    Paso 3 de Sec. 1.3: «dos escenarios acotados (salida libre / receptor a
    seccion llena), cumplir en ambos».

        salida libre    -> TW = 0 por definicion del escenario
        seccion llena   -> cota = 41.30 + 1.80 = 43.10; TW = 43.10 - 42.00
                           = 1.10 m

    El diseño corre con el gobernante --- el mayor --- y los DOS viajan hasta
    la memoria: cumplir con el mayor implica cumplir con el otro, y el
    revisor tiene que poder comprobarlo en vez de creerlo.
    """
    with sin_valor("TW_receptor"):
        tw = M3.tw_seccion_1_3(punto=_punto_de_prueba(),
                               cota_fondo_salida=42.00)
    assert tw.via is ViaDelTW.ESCENARIOS_ACOTADOS
    assert dict(tw.escenarios)[M3.ESCENARIO_SALIDA_LIBRE] == pytest.approx(
        0.0, abs=ABS_CERO)
    assert dict(tw.escenarios)[M3.ESCENARIO_SECCION_LLENA] == pytest.approx(
        1.10, abs=TOL_FINA)
    assert tw.valor == pytest.approx(1.10, abs=TOL_FINA)


def test_el_TW_mayor_es_el_peor_caso_y_por_eso_basta_correr_uno():
    """
    LA AFIRMACION QUE EL PASO 3 SOSTIENE, comprobada numericamente en vez de
    argumentada: h_o = max(TW, (y_c + D)/2) no decrece con TW, HW de salida
    crece con h_o, y el control gobernante es el mayor de los dos HW; luego
    HW es monotono no decreciente en TW y su peor caso es el TW mayor.

    Se barre el TW de 0 a 2 m sobre la geometria de A-01 y se exige que el HW
    gobernante nunca baje. Si algun dia el control de salida dejara de ser
    monotono en TW, «correr con el gobernante» dejaria de equivaler a
    «cumplir en ambos» y este test es el que lo dice.
    """
    from modulos.M2_material import catalogo
    from modulos.M4_control import resolver_control
    from modelos import TipoMaterial

    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    anterior = -math.inf
    for paso in range(0, 21):
        TW = paso / 10
        r = resolver_control(D=0.90, Q=1.167, S=0.006, L=18.635, TW=TW,
                             material=material)
        gobernante = max(r.HW_entrada, r.HW_salida)
        assert gobernante >= anterior - 1e-12, (
            f"el HW gobernante bajo al subir el TW a {TW} m")
        anterior = gobernante


# ===========================================================================
# 5 - Los cinco entregables de la Fase 11 estan en el documento
# ===========================================================================

def test_los_cinco_entregables_de_la_fase_11_estan_en_la_memoria(
        memoria, informe_perfil, tmp_path):
    """
    Los cinco primeros de la lista de Fase 11 de la hoja de ruta. El tercero
    es ademas un archivo aparte --- el cuadro resumen en CSV --- y se
    comprueba tambien ahi: es el que se pega en el expediente.
    """
    secciones = re.findall(r"<h2[^>]*>(.*?)</h2>", memoria, re.S)
    plano = " ".join(re.sub("<[^>]+>", "", s) for s in secciones)

    assert "Memoria de calculo por punto critico" in plano   # entregable 1
    assert "Criterios adoptados" in plano                    # entregable 2
    assert "Tabla resumen" in plano                          # entregable 3
    assert "Acotaciones" in plano                            # entregable 4
    assert "Pendientes" in plano                             # entregable 2 (cola)
    # Entregable 5: el analisis de sensibilidad, que hasta S18 solo lo
    # consumian los tests (SIS-B-05). No es una seccion: va PEGADO a cada
    # criterio adoptado, que es donde sirve --- decir de que rango salio el
    # numero, ahi mismo donde el numero esta ---, y por eso se busca su
    # rotulo y no un `<h2>`.
    assert "Sensibilidad declarada" in memoria
    assert "un barrido de sensibilidad lo recorre" in memoria

    destino = tmp_path / "resumen.csv"
    M11.exportar_csv(informe_perfil, destino)
    filas = destino.read_text(encoding="utf-8").splitlines()
    assert len(filas) == 5          # cabecera + los cuatro puntos
    assert "A-01" in filas[1] and "0.90" in filas[1]
