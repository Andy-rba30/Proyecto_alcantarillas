"""
tests/test_ext11_mutacion.py
============================
La mutacion MEDIDA de EXT-11 (propuesta 4 del dictamen): el arnes
`tests/apoyo/mutacion.py` probandose a si mismo, y el CENSO de los mutantes
que sobreviven a toda la suite objetivo con la razon de cada uno, anclado
al codigo para que no se vuelva una lista muerta.

Como se midio (2026-09-21, sobre el arbol de EXT-11, en serie con tres
trabajadores; `python3 -m tests.apoyo.mutacion --segunda-vuelta`):

  679 mutantes en 6 modulos (M3, M4, M5, MD enteros; `_par_de_manning`,
  `numero_de_celdas`, `catalogo`, `n_manning_hdpe` y `_fila_manning_de_cajon`
  de M2; las tres propiedades del par de n de `Material`).
  PRIMERA VUELTA (los diez `OBJETIVOS`, ~2 s por mutante): 568/679 muertos,
  score 0.8365. SEGUNDA VUELTA (linea base, cierre de perfil, CLI) sobre los
  111 vivos: 65 mueren, 46 sobreviven a todo; tres mas murieron con la
  segunda tanda de «Lo que la MUTACION enseño» (remedidos funcion por
  funcion con el arnes): 43 censados abajo.
  SIN `tests/test_ext11_propiedades.py` (los otros nueve objetivos, misma
  corrida): 504/679, score 0.7423. Sesenta y cuatro mutantes mueren SOLO por
  las propiedades y sus tandas: el receptor trapecial de la Sec. 1.3 (31:
  `tirante_normal_trapecial`, `caudal_manning_trapecial`, `area_` y
  `perimetro_trapecial`, `tw_seccion_1_3`), V3 y su paso (11), la
  progresion del catalogo (`_mismo_escalon`, 4), `_regimen` (2), el par de
  Manning (2) y las guardias de entrada. Sin las propiedades ni esas tandas,
  sobre los ocho objetivos que existian antes de EXT-11, la medida inicial
  fue 489/679 (0.7202).

Que es un superviviente CON RAZON. De cada mutante que sobrevive a las dos
vueltas se dice por que, y las razones son de cinco clases:

  equivalente   el mutante produce el mismo programa: `<=` frente a `<`
                cuando la banda TOL_UMBRAL_NORMATIVO ya cubre la igualdad,
                una guardia que el codigo anterior hace inalcanzable, un
                `return None` donde solo se lee la falsedad, un argumento
                por defecto que nadie usa;
  banda         el signo o el sentido de la banda TOL_UMBRAL_NORMATIVO (1e-9):
                el mutante solo se distingue con un valor a menos de 2·TOL
                del umbral. La banda existe para que la igualdad en punto
                flotante cuente como cumplimiento; donde el umbral es un
                escalar de entrada (V1, V2, V3, V9, el CBR) el test P8 fija
                la lectura inclusiva, y donde exige cotas o pesos al pelo
                (V4, V4b, VC1, V7, el regimen del barril) no se fijo;
  borde         una desigualdad estricta de la FUENTE en su valor exacto
                (HW/D = 0.75 de HDS-5 pag. 3.24): el caso es de medida
                nula y construirlo exige invertir el control de salida;
  memoria       solo cambia el TEXTO de un paso de memoria, no un numero.
                Ninguna entrada de hoy es de esta clase: las que lo
                parecian eran numeros y se cerraron con tests;
  fuera         el camino no lo recorre ningun test ni la linea base porque
                el expediente no puede llegar a el todavia (`M5.verificar`
                entero: V5 vacia), y esta escrito donde se prueba;
  hueco         un hueco REAL de la suite: no queda ninguno, porque cada
                hueco que la mutacion encontro se cerro con un test en
                `tests/test_ext11_propiedades.py` («Lo que la MUTACION
                enseño», dos tandas) y se remidio con el arnes.

El censo se comprueba en las dos direcciones: cada entrada tiene que seguir
siendo un mutante que `generar` produce sobre el codigo de hoy (anclaje por
modulo, funcion, operador y fragmento), y NO se comprueba aqui que siga
sobreviviendo --- eso cuesta minutos y se mide con el arnes; lo que se fija
es que la lista describa codigo que existe.
"""

import ast
import textwrap
from pathlib import Path

import pytest

from tests.apoyo import mutacion

RAIZ = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# El censo: (modulo, funcion, operador, original -> mutado): razon
# ---------------------------------------------------------------------------
SUPERVIVIENTES_CON_RAZON = {
    "src/modulos/M3_hidraulica.py::tirante_normal::booleano::f_min > 0 or f_max < 0 -> f_min > 0 and f_max < 0":
        "equivalente: la guardia del corchete es inalcanzable tras `not Q < Q_lleno` (PC-06): con 0 < Q < Q_lleno, f(min) < 0 y f(max) > 0 siempre; se conserva como defensa de Brent",
    "src/modulos/M3_hidraulica.py::tirante_normal::comparacion::f_min > 0 -> f_min >= 0":
        "equivalente: la guardia del corchete es inalcanzable tras `not Q < Q_lleno` (PC-06): con 0 < Q < Q_lleno, f(min) < 0 y f(max) > 0 siempre; se conserva como defensa de Brent",
    "src/modulos/M3_hidraulica.py::tirante_normal::comparacion::f_max < 0 -> f_max <= 0":
        "equivalente: la guardia del corchete es inalcanzable tras `not Q < Q_lleno` (PC-06): con 0 < Q < Q_lleno, f(min) < 0 y f(max) > 0 siempre; se conserva como defensa de Brent",
    "src/modulos/M3_hidraulica.py::tirante_normal::constante::0 -> 1":
        "equivalente: la guardia del corchete es inalcanzable tras `not Q < Q_lleno` (PC-06): con 0 < Q < Q_lleno, f(min) < 0 y f(max) > 0 siempre; se conserva como defensa de Brent",
    "src/modulos/M3_hidraulica.py::tirante_normal_trapecial::constante::1.0 -> 2.0":
        "equivalente: semilla y factor de duplicacion del corchete; cualquier valor > 0 encuentra la misma raiz (Brent con el mismo xtol)",
    "src/modulos/M3_hidraulica.py::tirante_normal_trapecial::comparacion::f(y_hi) > 0 -> f(y_hi) >= 0":
        "equivalente: `f(y_hi) >= 0` frente a `> 0` difiere solo si el corchete cae EXACTAMENTE en la raiz, de medida nula",
    "src/modulos/M3_hidraulica.py::tirante_normal_trapecial::constante::2 -> 3":
        "equivalente: semilla y factor de duplicacion del corchete; cualquier valor > 0 encuentra la misma raiz (Brent con el mismo xtol)",
    "src/modulos/M3_hidraulica.py::tirante_normal_trapecial::constante::0 -> 1 #2":
        "equivalente: `f(y_hi) > 1` en vez de `> 0` solo duplica el corchete una vez mas antes de Brent; la raiz es la misma",
    "src/modulos/M3_hidraulica.py::tw_seccion_1_3::aritmetico::cota_fondo_salida + gobernante -> cota_fondo_salida - gobernante #2":
        "equivalente: es el `cota_agua` que la via de escenarios pasa a `_paso_tw`, y ese argumento no llega a ningun campo del paso por esa via (la cota que si se publica, `cota_TW_msnm`, la fija test_la_cota_de_agua_del_TW...)",
    "src/modulos/M4_control.py::_exigir_hw_no_negativo::comparacion::HW_sobre_D > 0 -> HW_sobre_D >= 0":
        "equivalente: HW/D exactamente 0.0 (una lamina en el fondo) es de medida nula; el mutante solo cambia si un caudal produce ese cero exacto",
    "src/modulos/M4_control.py::control_salida::comparacion::TW > h_o_geometrico -> TW >= h_o_geometrico":
        "equivalente: con TW == h_o_geometrico las dos ramas devuelven el mismo h_o; el mutante solo cambia el rotulo `ahogado_por_TW` en la igualdad exacta",
    "src/modulos/M4_control.py::control_salida::comparacion::HW_sobre_D < H_O_HW_SOBRE_D_MIN -> HW_sobre_D <= H_O_HW_SOBRE_D_MIN":
        "borde: HW/D exactamente igual a 0.75 (o a 1.2, la cautela) de HDS-5 pag. 3.24; la lectura (0.75 usable) no se fija por test porque construir HW/D = 0.75 exacto exige invertir el control de salida, y el caso es de medida nula",
    "src/modulos/M4_control.py::control_salida::comparacion::HW_sobre_D < H_O_HW_SOBRE_D_CAUTELA -> HW_sobre_D <= H_O_HW_SOBRE_D_CAUTELA":
        "borde: HW/D exactamente igual a 0.75 (o a 1.2, la cautela) de HDS-5 pag. 3.24; la lectura (0.75 usable) no se fija por test porque construir HW/D = 0.75 exacto exige invertir el control de salida, y el caso es de medida nula",
    "src/modulos/M4_control.py::hw_gobernante::comparacion::salida.HW > entrada.HW + TOL_UMBRAL_NORMATIVO -> salida.HW >= entrada.HW + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M4_control.py::hw_gobernante::aritmetico::entrada.HW + TOL_UMBRAL_NORMATIVO -> entrada.HW - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M4_control.py::regimen_del_barril::comparacion::TW < seccion.altura - TOL_UMBRAL_NORMATIVO -> TW <= seccion.altura - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M4_control.py::velocidad_de_salida::comparacion::y_salida < D - TOL_UMBRAL_NORMATIVO -> y_salida <= D - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M4_control.py::velocidad_de_salida::comparacion::TW > critico.y_c -> TW >= critico.y_c":
        "equivalente: con TW == y_c el tirante de salida es el mismo por `min(D, max(TW, y_c))`; solo cambia el texto del caso",
    "src/modulos/M4_control.py::velocidad_de_salida::comparacion::A > 0 -> A >= 0":
        "equivalente: A = A(y_salida) con y_salida >= y_c > 0 nunca es cero; la guardia es defensiva",
    "src/modulos/M4_control.py::velocidad_de_salida::comparacion::TW < seccion.altura - TOL_UMBRAL_NORMATIVO -> TW <= seccion.altura - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M4_control.py::velocidad_de_salida::aritmetico::seccion.altura - TOL_UMBRAL_NORMATIVO -> seccion.altura + TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M4_control.py::_pasos_hidraulicos::constante::1 -> 2":
        "equivalente: el valor por defecto `celdas=1` nunca se usa, `resolver_control` pasa siempre `celdas` explicito",
    "src/modulos/M5_verificaciones.py::_exigir_regimen_evaluable::retorno_none::return False -> return None":
        "equivalente: `return None` es tan falso como `return False` para el unico lector (`if _exigir_regimen_evaluable(...)`)",
    "src/modulos/M5_verificaciones.py::v1_borde_libre::comparacion::y_sobre_D <= Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO -> y_sobre_D < Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v2_velocidad_minima::comparacion::V >= V_MIN - TOL_UMBRAL_NORMATIVO -> V > V_MIN - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v2b_sedimentacion::comparacion::resultado.S >= S_cauce - TOL_UMBRAL_NORMATIVO -> resultado.S > S_cauce - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v3_velocidad_maxima::comparacion::resultado.V_erosion <= v_max + TOL_UMBRAL_NORMATIVO -> resultado.V_erosion < v_max + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v3_velocidad_maxima::comparacion::resultado.V_erosion <= v_max + TOL_UMBRAL_NORMATIVO -> resultado.V_erosion < v_max + TOL_UMBRAL_NORMATIVO #2":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::altura_relleno_sobre_clave::comparacion::altura <= TOL_UMBRAL_NORMATIVO -> altura < TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::resguardo_por_cbr::comparacion::cbr < cbr_max -> cbr <= cbr_max":
        "equivalente: la tabla RESGUARDO_NAPA_SUBRASANTE va en orden descendente y la fila cuyo CBR_min es el borde se encuentra antes que la que lo tiene por CBR_max; `<=` en el techo nunca decide (test_el_resguardo_por_cbr... fija la lectura [min, max))",
    "src/modulos/M5_verificaciones.py::v4_carga_entrada::comparacion::HW_cota <= admisible + TOL_UMBRAL_NORMATIVO -> HW_cota < admisible + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v4_carga_entrada::aritmetico::admisible + TOL_UMBRAL_NORMATIVO -> admisible - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M5_verificaciones.py::v4b_relacion_hw_d::comparacion::HW_sobre_D <= admisible + TOL_UMBRAL_NORMATIVO -> HW_sobre_D < admisible + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v4b_relacion_hw_d::aritmetico::admisible + TOL_UMBRAL_NORMATIVO -> admisible - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M5_verificaciones.py::vc1_borde_libre_canal::comparacion::HW_cota <= admisible + TOL_UMBRAL_NORMATIVO -> HW_cota < admisible + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::vc1_borde_libre_canal::aritmetico::admisible + TOL_UMBRAL_NORMATIVO -> admisible - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M5_verificaciones.py::v7_flotacion::comparacion::estabilizante >= desestabilizante - TOL_UMBRAL_NORMATIVO -> estabilizante > desestabilizante - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v7_flotacion::aritmetico::desestabilizante - TOL_UMBRAL_NORMATIVO -> desestabilizante + TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M5_verificaciones.py::v9_disponibilidad_diametro::comparacion::D <= material.D_max + TOL_UMBRAL_NORMATIVO -> D < material.D_max + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::verificar::retorno_none::return tuple(hechas) -> return None":
        "fuera: ningun test llega al final de `M5.verificar` (la Fase 5 de expediente) porque V5 esta vacia y detiene antes; la de perfil corre por `servicio._verificador_perfil` (ficha EXT-11-04)",
    "src/modulos/MD.py::_mismo_escalon::comparacion::abs(a.altura - b.altura) > TOL_UMBRAL_NORMATIVO -> abs(a.altura - b.altura) >= TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/MD.py::_mismo_escalon::retorno_none::return False -> return None":
        "equivalente: `return None` es tan falso como `return False` para `any(...)` en `_exigir_progreso`",
    "src/modulos/MD.py::_mismo_escalon::comparacion::abs(ancho_a - ancho_b) <= TOL_UMBRAL_NORMATIVO -> abs(ancho_a - ancho_b) < TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
}


def _clave(modulo, funcion, operador, original, mutado):
    return f"{modulo}::{funcion}::{operador}::{original} -> {mutado}"


@pytest.fixture(scope="module")
def mutantes_de_hoy():
    """{clave: Mutante} de todo lo que el arnes genera sobre el arbol actual."""
    salida = {}
    for modulo, funciones in mutacion.MODULOS_DE_EXT11.items():
        for m, _ in mutacion.generar(modulo, funciones):
            salida.setdefault(m.clave, m)
    return salida


def test_cada_superviviente_del_censo_sigue_siendo_un_mutante_del_codigo(mutantes_de_hoy):
    huerfanos = [c for c in SUPERVIVIENTES_CON_RAZON if c not in mutantes_de_hoy]
    assert not huerfanos, (
        "entradas de SUPERVIVIENTES_CON_RAZON que el arnes ya no genera "
        "(cambio el codigo que anclan): actualiza o retira estas\n  "
        + "\n  ".join(huerfanos))


def test_cada_razon_del_censo_es_de_una_de_las_clases_declaradas():
    clases = ("equivalente", "banda", "borde", "memoria", "fuera")
    for clave, razon in SUPERVIVIENTES_CON_RAZON.items():
        assert razon.split(":")[0] in clases, f"{clave}: «{razon[:60]}»"
    assert not any(r.startswith("hueco") for r in SUPERVIVIENTES_CON_RAZON.values()), (
        "un hueco real no se censa: se cierra con un test")


# ---------------------------------------------------------------------------
# El arnes probandose a si mismo
# ---------------------------------------------------------------------------

def _generar_sobre(codigo: str, tmp_path, funciones=None, operadores=mutacion.OPERADORES):
    ruta = tmp_path / "modulo_de_prueba.py"
    ruta.write_text(textwrap.dedent(codigo), encoding="utf-8")
    original = mutacion.RAIZ
    mutacion.RAIZ = tmp_path
    try:
        return mutacion.generar("modulo_de_prueba.py", funciones, operadores)
    finally:
        mutacion.RAIZ = original


def test_el_generador_produce_los_ocho_operadores_y_ninguno_mas(tmp_path):
    codigo = '''
        def f(material, normal, x, y):
            """docstring con 3 numeros: 1 + 2."""
            if x > 0 and not y:
                return material.n_min * normal.V_erosion + 2
            return None
    '''
    mutantes = _generar_sobre(codigo, tmp_path)
    operadores = {m.operador for m, _ in mutantes}
    assert operadores == set(mutacion.OPERADORES)
    fragmentos = {(m.operador, m.original, m.mutado) for m, _ in mutantes}
    assert ("par_n", "material.n_min", "material.n_max") in fragmentos
    assert ("par_v", "normal.V_erosion", "normal.V_sedimentacion") in fragmentos
    # Los fragmentos son texto de `ast.unparse`, y su forma exacta (los
    # parentesis de `not`) cambia entre versiones: se comparan tras la
    # misma ida y vuelta por el AST, no contra un texto escrito a mano.
    def _normal(expr):
        return ast.unparse(ast.parse(expr, mode="eval"))
    condiciones = {(m.original, m.mutado) for m, _ in mutantes if m.operador == "condicion"}
    assert {(_normal(o[3:-1]), _normal(mu[3:-1])) for o, mu in condiciones} == {
        (_normal("x > 0 and not y"), _normal("not (x > 0 and not y)"))}
    assert ("retorno_none", "return material.n_min * normal.V_erosion + 2",
            "return None") in fragmentos
    # El docstring no se muta, y `return None` no se muta a si mismo.
    assert not any("docstring" in m.original for m, _ in mutantes)
    assert not any(m.original == "return None" for m, _ in mutantes)


def test_el_generador_no_toca_cadenas_ni_numeros_dentro_de_f_strings(tmp_path):
    codigo = '''
        def f(v):
            return f"{v:.3f} m/s (2 decimales)"
    '''
    mutantes = _generar_sobre(codigo, tmp_path, operadores=("constante",))
    assert mutantes == []


def test_cada_fuente_mutada_es_python_valido_y_difiere_del_original(tmp_path):
    codigo = '''
        def g(a, b):
            if a <= b:
                return (a + b) / 2
            return a ** 2
    '''
    mutantes = _generar_sobre(codigo, tmp_path)
    assert len(mutantes) >= 8
    original = ast.unparse(ast.parse(textwrap.dedent(codigo)))
    for m, fuente in mutantes:
        ast.parse(fuente)
        assert fuente != original, m.clave


def test_el_arnes_mata_de_verdad_un_mutante_conocido(tmp_path):
    """
    De punta a punta y en subproceso: el par de n intercambiado en
    `resolver_manning` muere contra las propiedades. Es el unico test de
    aqui que corre pytest dentro de pytest; cuesta unos segundos.
    """
    mutantes = [(m, f) for m, f in mutacion.generar(
        "src/modulos/M3_hidraulica.py", ("resolver_manning",), ("par_n",))]
    assert mutantes, "resolver_manning dejo de leer el par de n"
    resultados = mutacion.evaluar(mutantes[:1], ("tests/test_ext11_propiedades.py",),
                                  trabajadores=1)
    assert resultados[0]["veredicto"] == "muerto", resultados[0]


def test_el_arnes_se_niega_a_medir_sobre_una_linea_base_roja(tmp_path):
    """
    Un objetivo roto mataria a todos los mutantes y el score seria 1.0 sin
    medir nada: la corrida de referencia lo impide (auditoria de EXT-11).
    """
    roto = tmp_path / "test_roto.py"
    roto.write_text("def test_x():\n    assert False\n", encoding="utf-8")
    with pytest.raises(mutacion.LineaBaseRoja):
        mutacion.exigir_linea_base_verde(mutacion.RAIZ, (str(roto),))


def test_dos_mutaciones_identicas_en_la_misma_funcion_tienen_claves_distintas(mutantes_de_hoy):
    claves = set()
    repetidos = 0
    for modulo, funciones in mutacion.MODULOS_DE_EXT11.items():
        for m, _ in mutacion.generar(modulo, funciones):
            assert m.clave not in claves, m.clave
            claves.add(m.clave)
            repetidos += m.ordinal > 1
    assert repetidos > 0, "el ordinal existe porque hay fragmentos repetidos; hoy no hay ninguno"


def test_los_modulos_medidos_son_M3_M5_MD_y_el_par_de_n():
    modulos = set(mutacion.MODULOS_DE_EXT11)
    assert {"src/modulos/M3_hidraulica.py", "src/modulos/M4_control.py",
            "src/modulos/M5_verificaciones.py", "src/modulos/MD.py"} <= modulos
    assert set(mutacion.MODULOS_DE_EXT11["src/modelos.py"]) == {
        "n_para_capacidad", "n_para_velocidad_maxima", "n_para_velocidad_minima"}
    assert "_par_de_manning" in mutacion.MODULOS_DE_EXT11["src/modulos/M2_material.py"]
    assert "tests/test_ext11_propiedades.py" in mutacion.OBJETIVOS
