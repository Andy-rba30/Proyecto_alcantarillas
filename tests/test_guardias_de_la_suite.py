"""
tests/test_guardias_de_la_suite.py
==================================
Guardias sobre LA PROPIA SUITE: reglas de CLAUDE.md que hablan de como se
escriben los tests, no de como se calcula.

`tests/test_sin_literales.py` vigila el codigo de produccion. Este archivo
vigila el codigo de prueba, que hasta la sesion S16 no vigilaba nadie -- y esa
es exactamente la forma del cluster C09: la suite estaba verde y no habria
detectado los hallazgos de las tres auditorias.
"""

import ast
import re
import io
import tokenize
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
TESTS = RAIZ / "tests"
CONFTEST = RAIZ / "conftest.py"

# Los directorios de la suite. `conftest.py` entra porque declara los
# criterios de la corrida y podria comparar floats igual que un test.
# TODO el arbol de la suite, no solo los `test_*.py`. Dejar fuera
# `tests/fixtures/casos_patron.py` era el peor de los huecos posibles: es el
# archivo que CLAUDE.md hace obligatorio para todo modulo de calculo ("Todo
# modulo de calculo se contrasta contra tests/fixtures/casos_patron.py") y el
# objeto de la fila 7 de la hoja `Conflictos`. Sus asserts de autoverificacion
# no los miraba este guardian, y sus `approx` no entraban en el censo, de modo
# que los cupos subcontaban. `tests/apoyo/` estaba fuera por lo mismo.
ARCHIVOS_DE_PRUEBA = sorted(
    ruta for ruta in TESTS.rglob("*.py")
    if "__pycache__" not in ruta.parts
) + [CONFTEST]

MARCA_APPROX = "approx"


# ---------------------------------------------------------------------------
# SIS-F-16 - ningun assert compara floats con igualdad exacta
# ---------------------------------------------------------------------------

MARCA_EXACTO = "# float-exacto"


def _operandos_de_igualdad(nodo_assert: ast.Assert):
    """
    Las comparaciones de IGUALDAD de un assert, con los operandos donde puede
    haber un float escrito.

    `==` y `!=` miran los dos lados. `in` y `not in` miran SOLO el contenedor:
    en `assert nota(espesor=0.30) in texto` el 0.30 es un argumento, no un
    valor comparado, y contarlo seria un falso positivo. En
    `assert fila["Ks"] in (-0.5, 0.7)` el par SI es el conjunto de valores
    contra el que se compara, y ahi la igualdad exacta esta escondida en la
    pertenencia.
    """
    for comparacion in ast.walk(nodo_assert.test):
        if not isinstance(comparacion, ast.Compare):
            continue
        ops = comparacion.ops
        if any(isinstance(op, (ast.Eq, ast.NotEq)) for op in ops):
            yield comparacion, [comparacion.left] + list(comparacion.comparators)
        elif any(isinstance(op, (ast.In, ast.NotIn)) for op in ops):
            yield comparacion, list(comparacion.comparators)


# Llamadas que TRANSPORTAN el literal en vez de consumirlo: el valor que se
# compara sigue siendo el que esta escrito dentro.
LLAMADAS_QUE_TRANSPORTAN = {
    "float", "int", "complex", "Decimal", "Fraction", "abs", "round",
    "min", "max", "sum", "list", "tuple", "set", "frozenset", "dict",
    "sorted", "reversed",
}


def _aritmetica_de_literales(nodo):
    """
    El valor de una expresion aritmetica hecha SOLO de literales, o None.

    `ast.literal_eval` no sirve: admite `+` y `-` unicamente para reconstruir
    complejos, de modo que `9 / 2` --- un 4.5 escrito en dos trozos --- le
    devuelve ValueError y quedaba invisible.
    """
    if isinstance(nodo, ast.Constant):
        return nodo.value if isinstance(nodo.value, (int, float)) and not isinstance(nodo.value, bool) else None
    if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.USub, ast.UAdd)):
        valor = _aritmetica_de_literales(nodo.operand)
        if valor is None:
            return None
        return -valor if isinstance(nodo.op, ast.USub) else valor
    if not isinstance(nodo, ast.BinOp):
        return None
    izq = _aritmetica_de_literales(nodo.left)
    der = _aritmetica_de_literales(nodo.right)
    if izq is None or der is None:
        return None
    try:
        if isinstance(nodo.op, ast.Add):
            return izq + der
        if isinstance(nodo.op, ast.Sub):
            return izq - der
        if isinstance(nodo.op, ast.Mult):
            return izq * der
        if isinstance(nodo.op, ast.Div):
            return izq / der
        if isinstance(nodo.op, ast.Pow):
            return izq ** der
    except (ZeroDivisionError, OverflowError, ValueError):
        return None
    return None


def _nombre_de_llamada(nodo: ast.Call):
    """`f(...)` -> 'f'; `a.b(...)` -> 'b'."""
    f = nodo.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _floats_escritos(nodo):
    """
    Los float ESCRITOS COMO LITERAL en el operando, a cualquier profundidad de
    tupla, lista, conjunto o diccionario, y con el signo delante.

    Dos precisiones que costaron sendos falsos negativos y un falso positivo:

      * `-0.5` NO es un `ast.Constant`: es `UnaryOp(USub, Constant(0.5))`, de
        modo que mirar solo Constant deja pasar todos los literales negativos.
      * NO se desciende dentro de una LLAMADA. Un float que viaja como
        argumento -- `nota_temperatura_dos_caras(espesor=0.30)` -- no es un
        valor comparado: es una entrada. Contarlo convertiria en falta cada
        test que pase un numero a la funcion que prueba.

    Esa tercera regla abria un falso NEGATIVO que la primera version no
    declaraba: envolver el literal en cualquier llamada lo hacia invisible.
    `== float(4.5)`, `== abs(-0.5)`, `== max(0.5, 0.2)`, `== list((0.5, 0.7))`
    y `== dict(maximo=1.25)` comparaban exacto y el guardian no los veia. Se
    cierra distinguiendo la llamada que TRANSPORTA el literal --- un conversor
    o un constructor de contenedor, donde el valor comparado sigue siendo el
    literal --- de la que lo CONSUME, que es la que se exime. Y un `BinOp` de
    literales (`== 9 / 2`) es un literal escrito en dos trozos.
    """
    if isinstance(nodo, ast.Call):
        if _nombre_de_llamada(nodo) in LLAMADAS_QUE_TRANSPORTAN:
            for hijo in list(nodo.args) + [k.value for k in nodo.keywords]:
                yield from _floats_escritos(hijo)
        return
    if isinstance(nodo, ast.BinOp):
        valor = _aritmetica_de_literales(nodo)
        if isinstance(valor, float) and not isinstance(valor, bool):
            yield valor
            return
        # No era aritmetica cerrada de literales (`4.5 + tolerancia`): se
        # sigue descendiendo, o se perderia el 4.5 que si esta escrito.
    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, float) and not isinstance(nodo.value, bool):
            yield nodo.value
        return
    if (isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, ast.USub)
            and isinstance(nodo.operand, ast.Constant)
            and isinstance(nodo.operand.value, float)):
        yield -nodo.operand.value
        return
    for hijo in ast.iter_child_nodes(nodo):
        yield from _floats_escritos(hijo)


def _es_approx(nodo) -> bool:
    """
    El operando ES, en su primer nivel, un `pytest.approx(...)`.

    Se mira el primer nivel y no el subarbol: un `approx` ENTERRADO dentro de
    una tupla -- `assert par() == (approx(1.0), 2.5)` -- desactivaba el
    detector para toda la comparacion, y el 2.5 seguia comparandose exacto.
    """
    if not isinstance(nodo, ast.Call):
        return False
    f = nodo.func
    nombre = f.id if isinstance(f, ast.Name) else (
        f.attr if isinstance(f, ast.Attribute) else None)
    return nombre == MARCA_APPROX


def _lineas_compuestas(codigo: str) -> set:
    """Lineas con un `;` fuera de un string: dos sentencias, una sola marca."""
    lineas = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(codigo).readline):
            if tok.type == tokenize.OP and tok.string == ";":
                lineas.add(tok.start[0])
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return lineas


def _lineas_exentas(codigo: str) -> set:
    """
    Lineas con la marca `# float-exacto: <razon>`, como COMENTARIO.

    Mismo mecanismo y misma exigencia de razon que la marca `# literal-ok` del
    barrido de literales: la exencion es visible en revision y dice por que.
    Se usa donde la igualdad exacta ES lo que se prueba -- los autotests de
    los propios detectores comparan la lista de literales que encontraron
    contra los mismos dobles que parsearon, y aproximarla la vaciaria de
    sentido.

    Y NO VALE EN UNA LINEA COMPUESTA. Un `;` pone dos asserts bajo un solo
    comentario --- `assert a() == 1.5; assert b() == 2.5  # float-exacto: solo
    el primero` --- y la marca eximiria el segundo con la razon del primero.
    Es el mismo problema que `# literal-ok` tiene en
    tests/test_sin_literales.py, y se cierra igual: la linea compuesta se
    rechaza entera.
    """
    exentas = set()
    compuestas = _lineas_compuestas(codigo)
    try:
        for tok in tokenize.generate_tokens(io.StringIO(codigo).readline):
            if tok.type != tokenize.COMMENT:
                continue
            if tok.start[0] in compuestas:
                continue           # la marca explica UNA sentencia, no dos
            texto = tok.string.strip()
            if texto.startswith(MARCA_EXACTO + ":") and texto[len(MARCA_EXACTO) + 1:].strip():
                exentas.add(tok.start[0])
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return exentas


def asserts_de_float_con_igualdad(codigo: str, nombre: str = "<memoria>"):
    """
    [(linea, valor literal), ...] de los asserts que comparan un float escrito
    con `==`, `!=`, `in` o `not in` sin `pytest.approx` y sin la marca
    `# float-exacto: <razon>`.

    LIMITES DECLARADOS del detector. Reconoce el float ESCRITO en el assert, y
    hay dos formas que no puede ver porque no son decidibles mirando el arbol.
    Las dos se barrieron A MANO en S16, y quedan escritas aqui para que quien
    escriba el test siguiente sepa que el guardian no lo cubre:

      * NOMBRE contra NOMBRE -- `tmc.v_max_adoptado == ca.valor("v_max_tmc")`,
        que la propia ficha SIS-F-16 añade a su lista con un `(+ test_M2)` y
        que hubo que encontrar leyendo, no detectando;
      * el idioma de MONOTONIA `lista == sorted(lista)`, que compara floats con
        igualdad -- aunque sea contra una permutacion de si misma -- y que
        ademas afirma menos de lo que se quiere decir. Los cinco casos del
        arbol se reescribieron como
        `all(a <= b for a, b in zip(lista, lista[1:]))`.

    Lo que SI cubre es la forma en que aparecieron los quince asserts del grep
    de la ficha -- un valor calculado contra un numero escrito a mano --, que
    es la que se copia al escribir el test siguiente.
    """
    arbol = ast.parse(codigo, filename=nombre)
    exentas = _lineas_exentas(codigo)
    hallazgos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Assert):
            continue
        for comparacion, operandos in _operandos_de_igualdad(nodo):
            if comparacion.lineno in exentas:
                continue
            for operando in operandos:
                if _es_approx(operando):
                    continue
                for valor in _floats_escritos(operando):
                    hallazgos.append((comparacion.lineno, valor))
    return sorted(set(hallazgos))


def test_ningun_assert_compara_floats_con_igualdad_exacta():
    """
    SIS-F-16. CLAUDE.md: "No comparar floats con ==. Tolerancias explicitas y
    nombradas." La regla no exime a los tests, y la auditoria encontro quince
    asserts que la incumplian -- todos exactos por construccion, de modo que
    ninguno fallaba: el defecto era que la suite congelaba el patron y lo
    extendia a cada test nuevo que lo copiara.

    Las dos tolerancias con que se sustituyeron viven, con nombre y con la
    razon de cada una, en `tests/apoyo/aproximacion.py`.
    """
    faltas = {}
    for ruta in ARCHIVOS_DE_PRUEBA:
        hallazgos = asserts_de_float_con_igualdad(
            ruta.read_text(encoding="utf-8-sig"), ruta.name)
        if hallazgos:
            faltas[str(ruta.relative_to(RAIZ))] = hallazgos
    detalle = "\n".join(
        f"  {archivo}: " + ", ".join(f"linea {n} -> {v!r}" for n, v in sitios)
        for archivo, sitios in faltas.items())
    assert not faltas, (
        "Asserts que comparan un float con igualdad exacta:\n" + detalle +
        "\n\nUsa pytest.approx con una tolerancia NOMBRADA: REL_TRANSPORTE si "
        "el valor solo se transporta, ABS_CERO si la comparacion es contra "
        "cero (tests/apoyo/aproximacion.py), o la tolerancia que declare el "
        "caso patron si el valor se calculo."
    )


# --- el detector probandose a si mismo -------------------------------------

def test_el_detector_ve_la_igualdad_de_float():
    codigo = "def test_x():\n    assert medir() == 4.5\n"
    assert [v for _, v in asserts_de_float_con_igualdad(codigo)] == [4.5]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_el_detector_ve_la_desigualdad_de_float():
    codigo = "def test_x():\n    assert medir() != 0.75\n"
    assert [v for _, v in asserts_de_float_con_igualdad(codigo)] == [0.75]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_el_detector_acepta_pytest_approx():
    codigo = ("def test_x():\n"
              "    assert medir() == pytest.approx(4.5, rel=REL_TRANSPORTE)\n")
    assert asserts_de_float_con_igualdad(codigo) == []


def test_el_detector_no_molesta_a_enteros_ni_a_textos():
    codigo = ("def test_x():\n"
              "    assert contar() == 3\n"
              "    assert nombre() == 'A-01'\n"
              "    assert bandera() is True\n"
              "    assert falta() is None\n")
    assert asserts_de_float_con_igualdad(codigo) == []


def test_el_detector_no_molesta_a_las_comparaciones_de_orden():
    """`>` y `<` sobre floats son legitimas: no afirman igualdad."""
    codigo = "def test_x():\n    assert medir() > 4.5\n    assert medir() <= 9.0\n"
    assert asserts_de_float_con_igualdad(codigo) == []


@pytest.mark.parametrize("codigo, esperado", [
    # (a) el literal dentro de una TUPLA
    ('def t():\n    assert par() == (0.90, 1.00)\n', [0.90, 1.00]),
    # (b) dentro de un DICT
    ('def t():\n    assert d() == {"max": 1.25, "min": 0.90}\n', [0.90, 1.25]),
    # (c) dentro de una LISTA
    ('def t():\n    assert [medir()] == [4.5]\n', [4.5]),
    # (d) la PERTENENCIA, que es una igualdad contra varios a la vez
    ('def t():\n    assert medir() in (4.5, 9.0)\n', [4.5, 9.0]),
    # (e) el literal NEGATIVO: en el arbol no es Constant, es UnaryOp
    ('def t():\n    assert ks() == -0.5\n', [-0.5]),
    # (f) el approx ENTERRADO, que desactivaba el detector para toda la
    #     comparacion y dejaba pasar al hermano de al lado
    ('def t():\n    assert par() == (pytest.approx(1.0), 2.5)\n', [2.5]),
])
def test_las_seis_evasiones_del_detector_estan_cerradas(codigo, esperado):
    """
    Las seis formas con que un assert de float con igualdad se escapaba del
    guardian, cada una construida y corrida. No son hipoteticas: cinco de las
    seis aparecen en la suite real (test_M5, test_M8, test_M9, test_MD y
    test_M4 respectivamente), y por eso el detector estrecho daba por cerrado
    SIS-F-16 con dieciseis asserts todavia en pie.
    """
    assert sorted(v for _, v in asserts_de_float_con_igualdad(codigo)) == sorted(esperado)


def test_el_detector_no_confunde_un_argumento_con_un_valor_comparado():
    """
    El falso positivo simetrico: en `nota(espesor=0.30) in texto` el 0.30 es
    una ENTRADA, no un valor comparado. Contarlo convertiria en falta cada
    test que pase un numero a la funcion que prueba.
    """
    codigo = 'def t():\n    assert "AMBAS caras" in nota(espesor=0.30)\n'
    assert asserts_de_float_con_igualdad(codigo) == []


def test_la_marca_float_exacto_exime_y_exige_su_razon():
    """
    Donde la igualdad exacta ES lo que se prueba -- los autotests de los
    propios detectores comparan la lista de literales encontrados contra los
    mismos dobles que parsearon -- se declara con la marca, igual que el
    barrido de literales declara sus formulas. Sin razon, no exime.
    """
    con_razon = ('def t():\n    assert f(c) == [4.5]'
                 '  # float-exacto: el detector devuelve el mismo double\n')
    sin_razon = 'def t():\n    assert f(c) == [4.5]  # float-exacto\n'
    assert asserts_de_float_con_igualdad(con_razon) == []
    assert [v for _, v in asserts_de_float_con_igualdad(sin_razon)] == [4.5]  # float-exacto: el detector devuelve el mismo double que parseo


def test_el_detector_ve_el_float_a_la_izquierda():
    codigo = "def test_x():\n    assert 4.5 == medir()\n"
    assert [v for _, v in asserts_de_float_con_igualdad(codigo)] == [4.5]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


# ---------------------------------------------------------------------------
# La suite no puede volver a comparar sin tolerancia nombrada
# ---------------------------------------------------------------------------

def test_las_tolerancias_de_prueba_estan_nombradas_y_documentadas():
    """
    CLAUDE.md pide tolerancias "explicitas y NOMBRADAS": un
    `pytest.approx(x)` a secas cumple la letra (es tolerante) y no el fondo
    (nadie sabe que igualdad se esta afirmando). Las dos que usa la suite
    viven en un solo sitio, con su razon escrita.
    """
    from tests.apoyo import aproximacion

    assert aproximacion.REL_TRANSPORTE > 0
    assert aproximacion.ABS_CERO > 0
    assert aproximacion.__doc__ and "SIS-F-16" in aproximacion.__doc__, (
        "el modulo de tolerancias de prueba tiene que decir de donde sale")


# ---------------------------------------------------------------------------
# SIS-F-15 - los dos .md de fixtures no pueden volver a mentir sobre el codigo
# ---------------------------------------------------------------------------
# Los dos documentos de `tests/fixtures/` describen el estado del codigo, y ese
# estado cambia con cada sesion de correccion. Cuando la auditoria los reviso,
# afirmaban cinco cosas ya falsas. Corregir el texto y no dejar guardia
# repetiria la historia: en dos sesiones vuelven a estar caducos y nadie se
# entera, porque un .md no falla.
#
# Esto no vigila la prosa: vigila las AFIRMACIONES COMPROBABLES que la prosa
# hace. Cada assert de aqui corresponde a una frase concreta del documento.

FIXTURES = RAIZ / "tests" / "fixtures"
REFERENCIAL = FIXTURES / "datos_referenciales_prueba.md"
NO_APLICADOS = FIXTURES / "datos_referenciales_prueba.NO_APLICADOS.md"

_PARRAFO_VACIOS = "Del resto de la lista, lo que sigue vacio hoy:"


def _claves_declaradas_vacias():
    """Las claves que el .md afirma que siguen sin valor, leidas del propio .md."""
    import re

    texto = REFERENCIAL.read_text(encoding="utf-8")
    inicio = texto.index(_PARRAFO_VACIOS)
    fin = texto.index("\n\n", inicio)
    return re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", texto[inicio:fin])


def test_el_fixture_referencial_dice_la_verdad_sobre_los_criterios_vacios():
    """
    El documento enumera los criterios que "siguen vacios". Si alguno se
    cierra y nadie toca el .md, el documento pasa a mentir en silencio -- que
    es exactamente lo que paso con v_max_hdpe y v_max_tmc.
    """
    from src import criterios_adoptados as ca

    claves = _claves_declaradas_vacias()
    assert claves, "el parrafo de criterios vacios desaparecio del fixture"
    con_valor = {clave: ca.CRITERIOS[clave].valor for clave in claves
                 if clave in ca.CRITERIOS and ca.CRITERIOS[clave].valor is not None}
    assert not con_valor, (
        f"el fixture dice que estos criterios siguen vacios y ya tienen valor: "
        f"{con_valor}. Actualiza tests/fixtures/datos_referenciales_prueba.md")
    inexistentes = [clave for clave in claves if clave not in ca.CRITERIOS]
    assert not inexistentes, (
        f"el fixture nombra criterios que ya no existen: {inexistentes}")


def test_los_dos_v_max_cerrados_no_pueden_volver_al_vacio_en_silencio():
    """
    La otra mitad de la misma frase: el .md declara que v_max_hdpe y
    v_max_tmc estan CERRADOS con 4.572 m/s y fuente WSDOT. Si alguien los
    devuelve a None, el documento vuelve a mentir en la direccion contraria.
    """
    from src import criterios_adoptados as ca

    for clave in ("v_max_hdpe", "v_max_tmc"):
        criterio = ca.CRITERIOS[clave]
        assert criterio.valor is not None, (
            f"'{clave}' volvio al vacio: el .md de fixtures lo declara cerrado")
        assert criterio.etiqueta == "C"
        assert "WSDOT" in (criterio.fuente or ""), (
            f"'{clave}' cambio de fuente: el .md cita WSDOT Tabla 8-4")
    assert "4.572" in REFERENCIAL.read_text(encoding="utf-8")


def test_los_simbolos_que_el_fixture_nombra_existen_de_verdad():
    """
    El .md lista los sitios de `AssertionError` que hacen inaplicable un
    criterio. Los nombraba por `archivo:linea` -- un ancla que se rompe sola,
    y que ya estaba rota en las cinco -- y ahora los nombra por SIMBOLO. Este
    test comprueba que los simbolos existen y que siguen levantando
    AssertionError, que es lo que hace cierta la afirmacion.
    """
    texto = NO_APLICADOS.read_text(encoding="utf-8")
    # DOS SITIOS SALIERON DE LA LISTA EN S20, y el test los vigila desde el
    # otro lado, mas abajo: `v8_evento_extremo` y `espesor_pared` levantan
    # hoy `DatoFaltanteError`, que SI es `ErrorProyecto`, de modo que
    # declarar su criterio ya no tumba la corrida. Es el mismo movimiento que
    # S16 hizo con `v5_remanso`.
    esperados = {
        "M8_estructural.py::seleccionar_clase_calibre":
            ("src/modulos/M8_estructural.py", "seleccionar_clase_calibre"),
        "M9_cabezal.py::verificar_estabilidad_global":
            ("src/modulos/M9_cabezal.py", "verificar_estabilidad_global"),
    }
    for rotulo, (archivo, funcion) in esperados.items():
        assert rotulo in texto, f"el fixture dejo de nombrar {rotulo}"
        arbol = ast.parse((RAIZ / archivo).read_text(encoding="utf-8-sig"))
        nodo = next((n for n in ast.walk(arbol)
                     if isinstance(n, ast.FunctionDef) and n.name == funcion), None)
        assert nodo is not None, f"'{funcion}' ya no existe en {archivo}"
        levanta = [r for r in ast.walk(nodo)
                   if isinstance(r, ast.Raise) and r.exc is not None
                   and _nombre_de_excepcion(r.exc) == "AssertionError"]
        assert levanta, (
            f"'{funcion}' ya no levanta AssertionError: el fixture quedo caduco, "
            "como paso con remanso_derecho_via")

    # Y LOS DOS QUE SALIERON, comprobados por lo contrario: si alguno volviera
    # a levantar `AssertionError`, el .md tendria que volver a nombrarlo.
    for archivo, funcion in (
            ("src/modulos/M5_verificaciones.py", "v8_evento_extremo"),
            ("src/modulos/M2_material.py", "espesor_pared")):
        arbol = ast.parse((RAIZ / archivo).read_text(encoding="utf-8-sig"))
        nodo = next((n for n in ast.walk(arbol)
                     if isinstance(n, ast.FunctionDef) and n.name == funcion), None)
        assert nodo is not None, f"'{funcion}' ya no existe en {archivo}"
        assert not [r for r in ast.walk(nodo)
                    if isinstance(r, ast.Raise) and r.exc is not None
                    and _nombre_de_excepcion(r.exc) == "AssertionError"], (
            f"'{funcion}' volvio a levantar AssertionError: si es a proposito, "
            "vuelve a nombrarlo en el .md de no aplicados; si no, es la mina "
            "que S20 desactivo")


def _nombre_de_excepcion(nodo):
    if isinstance(nodo, ast.Call):
        f = nodo.func
        return f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) else None)
    return nodo.id if isinstance(nodo, ast.Name) else None


def test_el_fixture_no_nombra_simbolos_retirados():
    """
    `Material.v_max_rango` se retiro al cerrar SIS-A-06, y el .md siguio
    describiendo el codigo en sus terminos. Los dos campos que lo
    sustituyeron son los que tienen que aparecer.
    """
    from src.modelos import Material

    campos = set(Material.__dataclass_fields__)
    assert "v_max_rango" not in campos
    assert {"v_max_tabla10", "v_max_adoptado"} <= campos

    texto = NO_APLICADOS.read_text(encoding="utf-8")
    assert "v_max_adoptado" in texto and "v_max_tabla10" in texto


def test_el_fixture_ya_no_afirma_un_conteo_de_tests_congelado():
    """
    El .md daba "653 passed" como baseline. Un numero absoluto de tests
    caduca con el commit siguiente: lo que puede afirmarse es de donde se lee,
    no cuanto vale.
    """
    texto = NO_APLICADOS.read_text(encoding="utf-8")
    assert "origin/main" in texto, (
        "el fixture tiene que decir DONDE se lee el conteo, no cual es")
    assert "collected" in texto, (
        "y tiene que distinguir passed de collected, que es de donde sale la "
        "confusion historica de numeros")


# ---------------------------------------------------------------------------
# La OTRA mitad de la regla: "Tolerancias explicitas y NOMBRADAS"
# ---------------------------------------------------------------------------
# El guardian de arriba vigila la primera mitad de la frase de CLAUDE.md. La
# segunda -- que la tolerancia se declare con un nombre -- no la vigila nadie,
# y `pytest.approx(x)` a secas la incumple dos veces: no dice cuanta tolerancia
# aplica (usa rel=1e-6, que es tres ordenes mas floja que las de este proyecto)
# y no dice QUE clase de igualdad afirma.
#
# Cerrarla entera hoy exigiria tocar 309 llamadas en dieciseis archivos, que es
# una sesion propia y no cabe en el commit de C09/C10. Lo que SI cabe, y es lo
# que el proyecto ya hace con `MAX_REFERENCIAS_DE_PROSA` en
# `src/normativa/manifiesto.py`, es declarar el cupo: escribir el numero, decir
# que es deuda y no meta, y que no pueda crecer sin que alguien lo suba a mano.
#
# Si al bajar uno de los dos numeros el test falla, es una buena noticia mal
# contada: baja el cupo y sigue.

CUPO_APPROX_SIN_TOLERANCIA = 208

# BAJA DE 101 A 72 EN S19, y no porque se hayan reescrito treinta llamadas:
# porque el clasificador estaba contando como «literal» la forma que el propio
# `tests/apoyo/aproximacion.py` manda usar --- `abs=c3["tolerancia_V"]`, la
# tolerancia que DECLARA el caso patron ---, de modo que el cupo empujaba a
# escribir `abs=1e-3` a mano al lado del caso que ya lo dice. El numero no
# medía lo que decía medir. Ver `_es_tolerancia_nombrada`.
CUPO_APPROX_CON_TOLERANCIA_LITERAL = 72


def _es_tolerancia_nombrada(nodo) -> bool:
    """
    Una tolerancia esta NOMBRADA si se la puede leer sin adivinar de que clase
    de igualdad habla. Dos formas valen:

      `REL_TRANSPORTE`      un nombre de tests/apoyo/aproximacion.py;
      `c3["tolerancia_V"]`  la que DECLARA el caso patron.

    La segunda faltaba, y es la que el propio `aproximacion.py` manda usar con
    todas las letras: «un test que contrasta un valor CALCULADO contra un caso
    patron usa la tolerancia que el propio caso patron declara, no estas dos».
    Contarla como literal empujaba a lo contrario --- a escribir `abs=1e-3` a
    mano al lado del caso que ya lo dice ---, que es exactamente la
    duplicacion que el cupo existe para frenar (S19).
    """
    if isinstance(nodo, ast.Name):
        return True
    return (isinstance(nodo, ast.Subscript)
            and isinstance(nodo.slice, ast.Constant)
            and isinstance(nodo.slice.value, str)
            and "toleranc" in nodo.slice.value.lower())


def _llamadas_a_approx(codigo: str, nombre: str = "<memoria>"):
    """[(linea, 'sin'|'literal'|'nombrada'), ...] por cada pytest.approx."""
    arbol = ast.parse(codigo, filename=nombre)
    clasificadas = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call) or not _es_approx(nodo):
            continue
        tolerancias = [kw for kw in nodo.keywords if kw.arg in ("rel", "abs")]
        if not tolerancias:
            clase = "sin"
        elif all(_es_tolerancia_nombrada(kw.value) for kw in tolerancias):
            clase = "nombrada"
        else:
            clase = "literal"
        clasificadas.append((nodo.lineno, clase))
    return clasificadas


def _censo_de_approx():
    censo = {"sin": [], "literal": [], "nombrada": []}
    for ruta in ARCHIVOS_DE_PRUEBA:
        for linea, clase in _llamadas_a_approx(
                ruta.read_text(encoding="utf-8-sig"), ruta.name):
            censo[clase].append(f"{ruta.relative_to(RAIZ)}:{linea}")
    return censo


def test_el_cupo_de_approx_sin_tolerancia_no_crece():
    """
    `pytest.approx(x)` sin tolerancia usa rel=1e-6 por defecto: tres ordenes
    mas floja que las tolerancias que este proyecto declara, y sin decirlo.
    El cupo es DEUDA DECLARADA, no una meta: lo que este test impide es que
    crezca sin que nadie lo note.
    """
    censo = _censo_de_approx()
    assert len(censo["sin"]) <= CUPO_APPROX_SIN_TOLERANCIA, (
        f"las llamadas a pytest.approx sin tolerancia subieron de "
        f"{CUPO_APPROX_SIN_TOLERANCIA} a {len(censo['sin'])}. Las nuevas "
        "tienen que declarar su tolerancia, y con nombre: mira "
        "tests/apoyo/aproximacion.py o la que declare el caso patron.\n"
        + "\n".join(f"  {sitio}" for sitio in censo["sin"][-15:]))


def test_el_cupo_de_approx_con_tolerancia_escrita_a_mano_no_crece():
    """
    Una tolerancia literal (`rel=1e-9`) es explicita pero no NOMBRADA: dice
    cuanto y no dice de que clase de igualdad se trata. Mismo cupo, misma
    razon.
    """
    censo = _censo_de_approx()
    assert len(censo["literal"]) <= CUPO_APPROX_CON_TOLERANCIA_LITERAL, (
        f"las tolerancias literales subieron de "
        f"{CUPO_APPROX_CON_TOLERANCIA_LITERAL} a {len(censo['literal'])}\n"
        + "\n".join(f"  {sitio}" for sitio in censo["literal"][-15:]))


def test_el_cupo_esta_escrito_con_su_razon_y_no_es_una_meta():
    """
    Un cupo sin razon escrita es un numero magico que nadie se atreve a bajar.
    Este test comprueba que el comentario que lo explica sigue ahi, igual que
    `MAX_REFERENCIAS_DE_PROSA` lleva el suyo en src/normativa/manifiesto.py.
    """
    fuente = Path(__file__).read_text(encoding="utf-8")
    assert "es deuda y no meta" in fuente
    assert "MAX_REFERENCIAS_DE_PROSA" in fuente, (
        "el cupo tiene que remitir al precedente del proyecto")
    censo = _censo_de_approx()
    assert censo["nombrada"], "ninguna tolerancia nombrada: el patron se perdio"


# ---------------------------------------------------------------------------
# SIS-F-13: la regla del caso patron, con guardia
# ---------------------------------------------------------------------------
# `CLAUDE.md`, seccion Tests: «Todo modulo de calculo se contrasta contra
# tests/fixtures/casos_patron.py». Hasta S19 esa regla no la ejecutaba nadie:
# vivia en la constitucion y su incumplimiento se descubrio en una AUDITORIA
# EXTERNA, no en la suite. Las exenciones tampoco estaban en ningun sitio que
# corriera --- vivian en una celda de un .xlsx y en la §15 del plan ---, de
# modo que el dia que llegara la fuente que falta nadie se enteraria de que ya
# se puede retirar la exencion.
#
# Cada exencion lleva su razon Y LO QUE HARIA FALTA para retirarla. No son
# equivalentes: M2, M8 y M10 esperaban una FUENTE que el repositorio no tenia
# (fabricarles un dorado seria inventar el valor de referencia, que es lo que
# prohibe el conflicto n.7 del plan) -- y M8 y M2 ya salieron, cada uno con
# su caso, cuando la fuente llego --; M11 no espera nada, porque es el modulo
# de reporte y un dorado numerico no tendria contra que contrastarse --- lo
# que a el se le exige es lo contrario, no calcular, y eso ya lo vigila
# `tests/test_memoria_sustentada.py::test_M11_no_calcula_y_sobre_D`.
SIN_CASO_PATRON = {
    # M2_material SALIO DE LA LISTA EN N2, y por la misma razon por la que M8
    # salio en C7: la exencion cubria de mas. Decia que faltaban las tres
    # series de diametros nominales de las normas de producto; la del TMC
    # dejo de faltar en I1 (ASTM_A760.T1 y AASHTO_M36.T6, paso 150 mm real
    # sobre 900) y la del HDPE en N2 (AASHTO_M294_TRAD.T7.2.2, transcrita de
    # la TRADUCCION NO OFICIAL de M 294-11 que entro en normas/, sin firma:
    # el original sigue ausente). Con dos de tres, `CP11_SERIES_NOMINALES`
    # contrasta `siguiente_diametro` contra las TABLAS y no contra la formula
    # (conflicto #7), y la exencion habria sobrevivido a la mitad de su
    # motivo. Lo que SIGUE sin dorado esta censado en el propio fixture
    # (`CP11_SERIES_NOMINALES['sin_dorado']`, con test): desde el cierre de
    # C09 esta vacio, porque la serie del concreto entro por imagen de la
    # Tabla 5 de M 170M (PDF 10, el unico escaneo real del ejemplar).
    # M8_estructural SALIO DE LA LISTA EN C7, y el motivo por el que estaba
    # sigue siendo cierto -- lo que cambio es que ya no cubre al modulo
    # ENTERO --. La exencion decia: «faltan AASHTO M 170M-04 Tablas 1 a 5
    # (clases D-load del concreto) y ASTM A796/A796M (calibre por altura de
    # cobertura del TMC). Son el insumo del vacio
    # 'clases_producto_por_relleno'». Eso sigue faltando y `seleccionar_clase_
    # calibre` sigue sin dorado por esa razon; pero la FLOTACION no necesitaba
    # ninguna de esas dos fuentes -- se calcula con geometria y con los gamma
    # de una tabla que si esta transcrita --, de modo que la exencion estaba
    # cubriendo de mas. C7 aporta `CP10_FLOTACION_MARCO`, con los dos numeros
    # que midio la auditoria de C5: prisma 40.61 kN/m contra cilindro 24.96.
    # Una exencion que sobrevive a su motivo es deuda inventada, y este test
    # es lo que lo hizo ruidoso en cuanto dejo de ser cierta.
    "M10_espaciamiento":
        "no lo cierra una norma sino el EXPEDIENTE VIAL: seccion de cuneta, su "
        "n de Manning, la intensidad de TR = 35 y el metodo de area "
        "tributaria. Su brazo normativo (`L_normativo`) ya es [N] y un caso "
        "patron sobre el seria tautologico; falta `L_hidraulico` (§15)",
    "M11_reporte":
        "NO es deuda: es el modulo de reporte y no le corresponde dorado "
        "numerico. Lo que se le exige es que no calcule, y lo vigila "
        "tests/test_memoria_sustentada.py::test_M11_no_calcula_y_sobre_D",
}


def test_todo_modulo_de_calculo_consume_su_caso_patron():
    """
    SIS-F-13. La lista de exentos es la que la §15 del plan declara, y este
    test la convierte en condicion que la suite defiende: si alguien anade un
    modulo de calculo sin caso patron, falla; y si trae la fuente que falta y
    conecta el caso, falla tambien --- pidiendo que se retire la exencion, que
    es la mitad que un .xlsx nunca avisa.
    """
    modulos = sorted(p.stem for p in (RAIZ / "src" / "modulos").glob("M*.py"))
    sin_fixture, exentos_que_ya_lo_usan = [], []
    for modulo in modulos:
        prueba = RAIZ / "tests" / f"test_{modulo}.py"
        if not prueba.exists():
            sin_fixture.append(f"{modulo}: no tiene tests/test_{modulo}.py")
            continue
        # POR AST, NO POR SUBCADENA. `"casos_patron" in texto` fallaba en las
        # dos direcciones: un modulo podia perder el import Y el test y quedar
        # verde mientras sobreviviera la palabra en un comentario, y un exento
        # que solo la mencionara disparaba la alarma contraria. La guardia que
        # se escribe para cerrar SIS-F-13 cometia SIS-F-17 --- test verde sobre
        # una cadena de texto --- al cerrarlo.
        arbol = ast.parse(prueba.read_text(encoding="utf-8"), filename=prueba.name)
        usa = any(
            (isinstance(n, ast.ImportFrom) and (n.module or "").endswith("casos_patron"))
            or (isinstance(n, ast.Import)
                and any(a.name.endswith("casos_patron") for a in n.names))
            for n in ast.walk(arbol))
        if usa and modulo in SIN_CASO_PATRON:
            exentos_que_ya_lo_usan.append(modulo)
        elif not usa and modulo not in SIN_CASO_PATRON:
            sin_fixture.append(
                f"{modulo}: no importa casos_patron y no esta exento. O trae "
                "su dorado, o declara la exencion con lo que haria falta")

    assert not sin_fixture, "\n  ".join([""] + sin_fixture)
    assert not exentos_que_ya_lo_usan, (
        f"{exentos_que_ya_lo_usan} YA consumen casos_patron: retira su "
        "entrada de SIN_CASO_PATRON y actualiza la §15 del plan. Una "
        "exencion que sobrevive a su motivo es deuda inventada")


def test_cada_exencion_de_caso_patron_dice_que_haria_falta():
    """
    Una exencion sin «que haria falta» es un «no se puede» sin fecha. La
    §15 del plan las escribe con su fuente concreta; este test impide que
    alguien anada una vacia.
    """
    for modulo, razon in SIN_CASO_PATRON.items():
        assert len(razon) > 80, f"{modulo}: la razon es demasiado corta"
        assert ("falta" in razon or "no le corresponde" in razon
                or "NO es deuda" in razon), (
            f"{modulo}: la razon no dice que haria falta para retirarla")


# ---------------------------------------------------------------------------
# PC-21 - lo que se afirma de un CODIGO se afirma sobre su AST, no sobre su
# texto: `getsource(...).count(...)` y `"x" in ruta_py.read_text()` cuentan
# los comentarios, y el mutante que borra el uso real sigue verde
# ---------------------------------------------------------------------------
#
# El precedente es S16, que paso al AST el `"FACTOR_MURO_TABLA = {" in fuente`
# que estaba verde sobre el comentario que explicaba la retirada del simbolo
# (CLAUDE.md). El dictamen midio que el patron volvio dos veces
# (`test_anticipo`, `test_gui_contrato`), y EXT-11 las paso al AST y dejo
# esta guardia para que no vuelva una tercera.
#
# QUE SE DETECTA. Dentro de cada funcion de la suite, un texto que sale de
# `inspect.getsource(...)` o de `<ruta>.read_text(...)` donde `<ruta>` nombra
# un archivo `.py` (directamente, o por una constante de modulo que lo
# nombra), y que se usa como contenedor de un `in` / `not in` o como receptor
# de `.count(` SIN haber pasado por `ast.parse(...)` en la misma funcion. Un
# `read_text()` de un `.md`, de un `.html` o de un `.json` no es codigo y no
# entra: lo que se persigue es la afirmacion textual sobre CODIGO.
#
# QUE NO SE PROHIBE, Y POR QUE HAY UN CENSO. Hay afirmaciones que son
# textuales A PROPOSITO y que el AST no puede hacer: (a) la AUSENCIA de una
# frase en todo el archivo, comentarios incluidos, que es mas fuerte por
# texto; (b) la presencia de un COMENTARIO, que por definicion no esta en el
# arbol; (c) un ancla de texto con la que el test REESCRIBE una copia del
# archivo; (d) un rotulo de la GUI, que es una cadena y se afirma como
# cadena; (e) que un archivo de la suite NOMBRE a otro en una tupla de datos;
# (f) el objeto medido es el TEXTO que un escritor del proyecto produjo
# (`escribir_valor_en_archivo`): se afirma la forma escrita, no un uso.
# Cada una vive en `TEXTUAL_CON_RAZON` con su razon, y el censo se comprueba
# en las dos direcciones: un sitio nuevo sin censar falla, y una entrada
# cuyo sitio ya no existe tambien, para que el censo no se vuelva una lista
# de excepciones muertas.

_LECTORES_DE_CODIGO = ("getsource", "read_text", "read_bytes")
_BUSCADORES_DE_TEXTO = ("count", "find", "rfind", "index", "rindex",
                        "startswith", "endswith")
_FUNCIONES_DE_RE = ("search", "match", "fullmatch", "findall", "finditer")
_MARCAS_DE_PYTHON = (".py",)
_EL_PROPIO_ARCHIVO = ("Path(__file__)", "Path(__file__).resolve()", "__file__")


def _nombre_de_llamada_simple(nodo: ast.Call) -> str:
    f = nodo.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def _nombres_asignados(objetivo) -> list:
    if isinstance(objetivo, ast.Name):
        return [objetivo.id]
    if isinstance(objetivo, (ast.Tuple, ast.List)):
        return [n for e in objetivo.elts for n in _nombres_asignados(e)]
    return []


def _resolutor_de_rutas_python(arbol_modulo: ast.Module, fn=None):
    """
    Devuelve `es_py(expr)`: si la expresion nombra un archivo `.py`, sea en
    su texto o a traves de una constante --- de modulo o LOCAL de la funcion
    --- (hasta tres saltos). Las locales entraron con la auditoria de EXT-11:
    `ruta = RAIZ / "gui" / "app.py"; ruta.read_text()` evadia al detector.
    """
    tabla = {}
    cuerpos = [arbol_modulo.body] + ([ast.walk(fn)] if fn is not None else [])
    for cuerpo in cuerpos:
        for n in cuerpo:
            if isinstance(n, ast.Assign):
                for nombre in _nombres_asignados(n.targets[0]) if len(n.targets) == 1 else []:
                    tabla[nombre] = ast.unparse(n.value)
            elif isinstance(n, ast.AnnAssign) and n.value is not None:
                for nombre in _nombres_asignados(n.target):
                    tabla[nombre] = ast.unparse(n.value)

    def es_py(expr, profundidad=0) -> bool:
        s = ast.unparse(expr) if isinstance(expr, ast.AST) else expr
        if any(marca in s for marca in _MARCAS_DE_PYTHON) or s in _EL_PROPIO_ARCHIVO:
            return True
        if profundidad > 2:
            return False
        return any(re.search(r"\b" + re.escape(nombre) + r"\b", s)
                   and es_py(valor, profundidad + 1)
                   for nombre, valor in tabla.items())
    return es_py


def afirmaciones_textuales_sobre_codigo(codigo: str, nombre: str = "<memoria>"):
    """
    [(linea, funcion, forma, lector)] de cada afirmacion TEXTUAL sobre el
    texto de un codigo Python: `in` / `not in`, `.count(` / `.find(` /
    `.index(` / `.startswith(`, o `re.search(...)` y hermanas, sobre un texto
    que salio de `inspect.getsource(...)`, de `<ruta .py>.read_text()` /
    `.read_bytes()` o de `open(<ruta .py>).read()`.

    EL TEXTO SE SIGUE COMO UNA MANCHA (taint): todo nombre asignado desde
    una expresion que contiene el texto --- `fuente.lower()`,
    `fuente.splitlines()`, `a, b = fuente.split(...)`, la variable de una
    comprension sobre el texto --- queda marcado, y una afirmacion sobre
    cualquiera de ellos cuenta. Un `ast.parse(fuente)` NO desmarca `fuente`:
    parsear y despues preguntar por el texto es la evasion mas facil, y la
    primera version de este detector la aceptaba (auditoria de EXT-11).
    """
    arbol = ast.parse(codigo, filename=nombre)
    hallazgos = []
    for fn in ast.walk(arbol):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        es_py = _resolutor_de_rutas_python(arbol, fn)
        manchados: dict = {}      # nombre -> lector del que viene el texto
        # Alias del lector (`leer = inspect.getsource`), de modulo o locales.
        alias = set()
        for n in list(arbol.body) + list(ast.walk(fn)):
            if isinstance(n, ast.Assign) and ast.unparse(n.value).split(".")[-1] == "getsource":
                alias.update(x for o in n.targets for x in _nombres_asignados(o))

        def _lector_directo(nodo):
            """El lector si la expresion ES una lectura de codigo Python."""
            if not isinstance(nodo, ast.Call):
                return None
            lector = _nombre_de_llamada_simple(nodo)
            if lector == "getsource" or (isinstance(nodo.func, ast.Name)
                                         and nodo.func.id in alias):
                return "getsource"
            if lector in ("read_text", "read_bytes") \
                    and isinstance(nodo.func, ast.Attribute) \
                    and es_py(nodo.func.value):
                return lector
            if lector == "read" and isinstance(nodo.func, ast.Attribute) \
                    and isinstance(nodo.func.value, ast.Call) \
                    and _nombre_de_llamada_simple(nodo.func.value) == "open" \
                    and nodo.func.value.args and es_py(nodo.func.value.args[0]):
                return "open"
            return None

        def _sin_arboles(expr):
            """
            Los nodos de la expresion SIN descender en `ast.parse(...)`: lo
            que sale de un parse es un arbol, no texto, y no arrastra la
            mancha (la variable parseada, en cambio, la conserva).
            """
            pendientes = [expr]
            while pendientes:
                n = pendientes.pop()
                if isinstance(n, ast.Call) and _nombre_de_llamada_simple(n) == "parse":
                    continue
                yield n
                pendientes.extend(ast.iter_child_nodes(n))

        def _lector_de(expr):
            """El lector si la expresion contiene texto de codigo, o None."""
            for n in _sin_arboles(expr):
                directo = _lector_directo(n)
                if directo:
                    return directo
                if isinstance(n, ast.Name) and n.id in manchados:
                    return manchados[n.id]
            return None

        # Propagacion de la mancha hasta el punto fijo.
        cambio = True
        while cambio:
            cambio = False
            for n in ast.walk(fn):
                objetivos, valor = [], None
                if isinstance(n, ast.Assign):
                    objetivos = [x for o in n.targets for x in _nombres_asignados(o)]
                    valor = n.value
                elif isinstance(n, ast.AnnAssign) and n.value is not None:
                    objetivos, valor = _nombres_asignados(n.target), n.value
                elif isinstance(n, ast.NamedExpr):
                    objetivos, valor = _nombres_asignados(n.target), n.value
                elif isinstance(n, ast.comprehension):
                    objetivos, valor = _nombres_asignados(n.target), n.iter
                elif isinstance(n, ast.For):
                    objetivos, valor = _nombres_asignados(n.target), n.iter
                if valor is None:
                    continue
                lector = _lector_de(valor)
                if lector:
                    for nombre_obj in objetivos:
                        if nombre_obj not in manchados:
                            manchados[nombre_obj] = lector
                            cambio = True

        for n in ast.walk(fn):
            if isinstance(n, ast.Compare):
                for op, contenedor in zip(n.ops, n.comparators):
                    lector = _lector_de(contenedor)
                    if isinstance(op, (ast.In, ast.NotIn)) and lector:
                        hallazgos.append((n.lineno, fn.name, "in", lector))
            if isinstance(n, ast.Call):
                llamado = _nombre_de_llamada_simple(n)
                if llamado in _BUSCADORES_DE_TEXTO and isinstance(n.func, ast.Attribute):
                    lector = _lector_de(n.func.value)
                    if lector:
                        hallazgos.append((n.lineno, fn.name, llamado, lector))
                if llamado in _FUNCIONES_DE_RE and isinstance(n.func, ast.Attribute) \
                        and ast.unparse(n.func.value) == "re":
                    lector = next((_lector_de(a) for a in n.args if _lector_de(a)), None)
                    if lector:
                        hallazgos.append((n.lineno, fn.name, "re." + llamado, lector))
    return sorted(set(hallazgos))


# El censo: (archivo, funcion) -> razon por la que la afirmacion es textual a
# proposito. Las letras remiten a las cinco razones admitidas de arriba.
TEXTUAL_CON_RAZON = {
    ("test_ayuda_entrada.py", "test_un_estado_nuevo_exige_su_parrafo_y_con_el_aparece_solo"):
        "(c) las dos anclas son el texto con el que el test REESCRIBE una "
        "copia de gui/app.py con un estado mas; el texto es la herramienta",
    ("test_ext10_multiobra.py", "test_h_la_gui_carga_declara_y_guarda_por_las_puertas_nuevas"):
        "(d) «Nuevo proyecto» es el rotulo del boton: una cadena afirmada "
        "como cadena; la variable de Tk del mismo test va por AST",
    ("test_criterios_adoptados.py", "test_la_escritura_permanente_reescribe_el_valor_en_el_archivo"):
        "(f) afirma el TEXTO que `escribir_valor_en_archivo` escribio en la "
        "copia: la forma escrita del bloque es lo que se mide",
    ("test_criterios_adoptados.py", "test_la_escritura_permanente_si_alcanza_a_un_valor_escalar"):
        "(f) afirma el TEXTO que `escribir_valor_en_archivo` escribio en la "
        "copia, tras comprobar por ast.parse que sigue siendo Python",
    ("test_dimensional_piloto.py", "_comentario_de"):
        "(b) recoge el COMENTARIO que sigue a una constante, que por "
        "definicion no esta en el AST; es lo que el chequeo dimensional lee",
    ("test_estilo_criterios.py", "_siglas_derivadas"):
        "(b) busca la explicacion de cada sigla en TODO el texto, "
        "comentarios y docstrings incluidos: es donde las siglas se explican",
    ("test_ext5_forma_gui.py", "test_la_gui_de_ayuda_ya_no_anuncia_claves_sin_ficha"):
        "(a) afirma la AUSENCIA de dos frases en todo gui/ayuda_entrada.py, "
        "comentarios incluidos",
    ("test_ext7_cabezal.py", "test_M05_el_docstring_ya_no_afirma_lo_contrario_de_la_norma"):
        "(a) afirma la AUSENCIA de la frase falsa de R95-031 en todo "
        "M9_cabezal.py, docstring y comentarios incluidos",
    ("test_ext8_rendimiento_gui.py", "test_pc11_la_gui_exporta_el_pdf_sin_bloquear_el_hilo_de_tk"):
        "(a) afirma la AUSENCIA de `threading`, `.wait(` y `.communicate(` "
        "en gui/app.py; las presencias del mismo test van por AST",
    ("test_ext8_rendimiento_gui.py", "test_ext8_el_modulo_de_exportacion_esta_vigilado"):
        "(e) afirma que test_sin_literales NOMBRA al modulo nuevo en su tupla "
        "de rutas; el nombre es un dato, no un uso (test_gui_contrato se "
        "consulta por su dato ARBOLES_DE_LA_GUI)",
    ("test_guardias_de_la_suite.py", "test_el_cupo_esta_escrito_con_su_razon_y_no_es_una_meta"):
        "(b) afirma la presencia de un COMENTARIO --- la razon del cupo ---, "
        "que por definicion no esta en el AST",
}


def _censo_textual():
    hallados = {}
    for ruta in ARCHIVOS_DE_PRUEBA:
        for linea, funcion, forma, lector in afirmaciones_textuales_sobre_codigo(
                ruta.read_text(encoding="utf-8"), ruta.name):
            hallados.setdefault((ruta.name, funcion), []).append(
                f"{ruta.name}:{linea} {forma} sobre {lector}()")
    return hallados


def test_ninguna_afirmacion_sobre_codigo_es_textual_sin_censar():
    hallados = _censo_textual()
    sin_censar = {sitio: usos for sitio, usos in hallados.items()
                  if sitio not in TEXTUAL_CON_RAZON}
    assert not sin_censar, (
        "afirmaciones textuales sobre CODIGO (`in read_text()` de un .py o "
        "`getsource(...).count(`) sin pasar por ast.parse. O se pasan al AST "
        "(precedente S16, PC-21) o entran en TEXTUAL_CON_RAZON con una de "
        "las cinco razones admitidas:\n  "
        + "\n  ".join(f"{a}::{f}: {', '.join(u)}"
                      for (a, f), u in sorted(sin_censar.items())))


def test_el_censo_textual_no_conserva_sitios_que_ya_no_existen():
    hallados = _censo_textual()
    muertos = sorted(set(TEXTUAL_CON_RAZON) - set(hallados))
    assert not muertos, (
        f"entradas de TEXTUAL_CON_RAZON cuyo sitio ya no afirma nada por "
        f"texto: {muertos}. Retiralas: un censo con muertos deja de vigilar.")
    for razon in TEXTUAL_CON_RAZON.values():
        assert razon[:3] in ("(a)", "(b)", "(c)", "(d)", "(e)", "(f)"), razon


# --- el detector probandose a si mismo -------------------------------------

def test_el_detector_textual_ve_getsource_count():
    codigo = ("import inspect\n"
              "def test_x():\n"
              "    fuente = inspect.getsource(f)\n"
              "    assert fuente.count('X') >= 2\n")
    assert [(4, "test_x", "count", "getsource")] == \
        afirmaciones_textuales_sobre_codigo(codigo)


def test_el_detector_textual_ve_in_sobre_read_text_de_un_py():
    codigo = ("from pathlib import Path\n"
              "RAIZ = Path('.')\n"
              "GUI = RAIZ / 'gui' / 'app.py'\n"
              "def test_x():\n"
              "    fuente = GUI.read_text()\n"
              "    assert 'trace_add' in fuente\n"
              "def test_y():\n"
              "    assert 'z' not in (RAIZ / 'src' / 'm.py').read_text()\n")
    assert [(6, "test_x", "in", "read_text"), (8, "test_y", "in", "read_text")] == \
        afirmaciones_textuales_sobre_codigo(codigo)


def test_el_detector_textual_no_molesta_a_lo_que_no_es_codigo():
    codigo = ("from pathlib import Path\n"
              "DOC = Path('docs') / 'x.md'\n"
              "def test_x():\n"
              "    assert 'frase' in DOC.read_text()\n"
              "    html = (Path('a') / 'memoria.html').read_text()\n"
              "    assert 'marca' in html and html.count('x') == 1\n")
    assert afirmaciones_textuales_sobre_codigo(codigo) == []


def test_un_ast_parse_decorativo_no_exime_a_la_afirmacion_textual():
    codigo = ("import ast, inspect\n"
              "def test_x():\n"
              "    fuente = inspect.getsource(f)\n"
              "    arbol = ast.parse(fuente)\n"
              "    assert 'X' in fuente\n")
    assert [(5, "test_x", "in", "getsource")] == \
        afirmaciones_textuales_sobre_codigo(codigo)


@pytest.mark.parametrize("cuerpo,esperado", [
    # ruta LOCAL, no una constante de modulo
    ("    ruta = RAIZ / 'gui' / 'app.py'\n    fuente = ruta.read_text()\n"
     "    assert 'x' in fuente\n", "in"),
    # variable intermedia derivada del texto
    ("    fuente = GUI.read_text()\n    texto = fuente.lower()\n"
     "    assert 'x' in texto\n", "in"),
    # .find / .index / .startswith
    ("    fuente = GUI.read_text()\n    assert fuente.find('x') >= 0\n", "find"),
    ("    fuente = GUI.read_text()\n    assert fuente.index('x')\n", "index"),
    # re.search sobre el texto
    ("    fuente = GUI.read_text()\n    assert re.search('x', fuente)\n", "re.search"),
    # alias del lector
    ("    leer = inspect.getsource\n    fuente = leer(f)\n"
     "    assert 'x' in fuente\n", "in"),
    # comprension sobre las lineas del texto
    ("    fuente = GUI.read_text()\n"
     "    assert any('x' in l for l in fuente.splitlines())\n", "in"),
    # read_bytes y open().read()
    ("    assert b'x' in GUI.read_bytes()\n", "in"),
    ("    assert 'x' in open(RAIZ / 'a.py').read()\n", "in"),
    # asignacion por tupla y anotada
    ("    a, b = GUI.read_text().split('#', 1)\n    assert 'x' in b\n", "in"),
    ("    fuente: str = GUI.read_text()\n    assert 'x' in fuente\n", "in"),
])
def test_el_detector_textual_ve_las_evasiones_que_el_auditor_probo(cuerpo, esperado):
    codigo = ("import re, inspect\nfrom pathlib import Path\n"
              "RAIZ = Path('.')\nGUI = RAIZ / 'gui' / 'app.py'\n"
              "def test_x():\n" + cuerpo)
    formas = [forma for _, _, forma, _ in afirmaciones_textuales_sobre_codigo(codigo)]
    assert esperado in formas, formas


# ---------------------------------------------------------------------------
# PC-22 - las funciones PUBLICAS de src/modulos que ningun test nombra, en un
# censo fijado con la razon de cada una
# ---------------------------------------------------------------------------
#
# El dictamen conto 16 sobre 5196dd2; hoy son 23, y el numero nunca se habia
# fijado, de modo que podia crecer en silencio. Que un test no NOMBRE una
# funcion no significa que no la ejercite: casi todas tienen consumidor de
# produccion y se prueban a traves de el (la memoria HTML, el servicio, la
# CLI). El censo dice cual es ese consumidor, medido por AST sobre `src/`,
# `gui/` y `cli.py`, y se comprueba en las dos direcciones: una funcion
# publica nueva sin test y sin censo falla, y una entrada del censo que un
# test ya nombra tambien, para que el censo se achique cuando la suite crece.
# La unica sin consumidor de produccion (el peso del suelo sobre el talon) ya
# estaba censada con su razon en `M9_cabezal.FUNCIONES_SIN_CONSUMIDOR`.

MODULOS_DE_CALCULO = sorted((RAIZ / "src" / "modulos").glob("*.py"))

PUBLICAS_SIN_REFERENCIA_EN_TESTS = {
    "M0_carga.leer_bytes": "la llama `correr` (servicio); la ejercita toda corrida de la CLI",
    "M0_carga.cargar_puntos_de_bytes": "la llama `correr` (servicio); la ejercita toda corrida de la CLI",
    "M11_reporte.sha1_de_bytes": "la llama `correr` (servicio, csv_sha1); la ejercita test_ext4",
    "M11_reporte.version_criterios": "la llama `trazabilidad` (M11); se ejercita con cada memoria",
    "M11_reporte.fecha_archivo": "la llama `trazabilidad` (M11); se ejercita con cada memoria",
    "M11_reporte.traza_clasificacion": "la llama `pasos_impresos` (M11) y `traza_del_punto`; se ejercita con cada memoria",
    "M11_reporte.traza_tw": "la llama `pasos_impresos` (M11); se ejercita con cada memoria",
    "M11_reporte.traza_hidraulica": "la llama `pasos_impresos` (M11); se ejercita con cada memoria",
    "M11_reporte.verificaciones_publicadas": "la llama `desarrollo_de_verificaciones` (M11); se ejercita con cada memoria",
    "M11_reporte.ancla_de_discrepancia": "la llama `bloque_discrepancias` (M11, anexo EXT-8); se ejercita con cada memoria",
    "M11_reporte.ancla_de_umbral": "la llama `anexo_referencias` (M11, anexo EXT-8); se ejercita con cada memoria",
    "M11_reporte.bloque_paso": "la llama `bloque_pasos` (M11); se ejercita con cada memoria",
    "M11_reporte.bloque_umbrales": "la llama `memoria_html_por_partes` (M11); se ejercita con cada memoria",
    "M11_reporte.bloque_homonimias": "la llama `memoria_html_por_partes` (M11); se ejercita con cada memoria",
    "M11_reporte.bloque_alcance": "la llama `memoria_html_por_partes` (M11); se ejercita con cada memoria",
    "M2_material.alcance_norma_producto_de": "la llama `_diseno_json` (cli); la ejercita test_cli por el JSON",
    "M3_hidraulica.area_trapecial": "la llama `caudal_manning_trapecial` (Sec. 1.3); la ejercita test_ext1 por el TW",
    "M3_hidraulica.perimetro_trapecial": "la llama `caudal_manning_trapecial` (Sec. 1.3); la ejercita test_ext1 por el TW",
    "M4_control.regimen_del_barril": "la llama `_regimen_y_salida` (EXT-3); la ejercita test_ext3 por resolver_control",
    "M4_control.velocidad_de_salida": "la llama `_regimen_y_salida` (EXT-3); la ejercita test_ext3 por resolver_control",
    "M5_verificaciones.pieza_del_hueco_de_V5": "la llama `_verificador_perfil` (servicio) y `verificar` (M5); la ejercita test_cierre_perfil",
    "M8_estructural.filas_ev_de_la_tabla": "la llama `v7_flotacion` (M5); la ejercita test_M5 por V7",
    "M9_cabezal.peso_suelo_sobre_talon": "SIN consumidor de produccion; censada con su razon en M9_cabezal.FUNCIONES_SIN_CONSUMIDOR",
    "M9_cabezal.gamma_eq": "SIN consumidor de produccion; censada con su razon en M9_cabezal.FUNCIONES_SIN_CONSUMIDOR",
    "M9_cabezal.factor_recubrimiento_por_ac": "la llama `_recubrimiento_aashto_detallado` (C07); la ejercita test_M9_cabezal por el recubrimiento",
    "M9_cabezal.nota_excepcion_refuerzo_minimo": "la llama `correr_cabezal` (servicio); la ejercita test_cli por el cabezal",
    "M9_cabezal.requiere_refuerzo_dos_capas": "la llama `nota_temperatura_dos_caras` (M9); la ejercita test_ext7",
    "M9_cabezal.funciones_sin_consumidor": "la llama `condicion_normativa_cabezal` (M9); la ejercita test_cli por el volcado del cabezal",
}


def _nombres_de_la_suite() -> set:
    """
    Los tokens NAME de toda la suite --- ni cadenas ni comentarios ni
    docstrings --- MENOS el propio censo de arriba. La primera version
    buscaba el nombre por regex sobre el texto crudo y se ponia verde sobre
    un comentario que lo mencionara, que es exactamente el patron PC-21 que
    este mismo archivo persigue (auditoria de EXT-11): medido, siete
    publicas pasaban por «referenciadas» gracias a un comentario, un
    docstring o una cadena.
    """
    nombres = set()
    for ruta in ARCHIVOS_DE_PRUEBA:
        texto = ruta.read_text(encoding="utf-8")
        if ruta == Path(__file__).resolve():
            lineas = texto.split("\n")
            arbol = ast.parse(texto, filename=ruta.name)
            for nodo in arbol.body:
                if isinstance(nodo, ast.Assign) and any(
                        getattr(objetivo, "id", "") == "PUBLICAS_SIN_REFERENCIA_EN_TESTS"
                        for objetivo in nodo.targets):
                    for i in range(nodo.lineno - 1, nodo.end_lineno):
                        lineas[i] = ""
            texto = "\n".join(lineas)
        for token in tokenize.generate_tokens(io.StringIO(texto).readline):
            if token.type == tokenize.NAME:
                nombres.add(token.string)
    return nombres


def _publicas_sin_referencia_en_tests() -> set:
    nombres = _nombres_de_la_suite()
    sin_referencia = set()
    for ruta in MODULOS_DE_CALCULO:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
        for nodo in arbol.body:
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and not nodo.name.startswith("_") \
                    and nodo.name not in nombres:
                sin_referencia.add(f"{ruta.stem}.{nodo.name}")
    return sin_referencia


def test_las_publicas_sin_referencia_en_tests_son_las_del_censo():
    medidas = _publicas_sin_referencia_en_tests()
    nuevas = sorted(medidas - set(PUBLICAS_SIN_REFERENCIA_EN_TESTS))
    assert not nuevas, (
        "funciones publicas de src/modulos que ningun test nombra y que no "
        f"estan en PUBLICAS_SIN_REFERENCIA_EN_TESTS: {nuevas}. O se les escribe "
        "test, o entran en el censo con su consumidor de produccion.")
    cubiertas = sorted(set(PUBLICAS_SIN_REFERENCIA_EN_TESTS) - medidas)
    assert not cubiertas, (
        f"entradas del censo que un test ya nombra: {cubiertas}. Retiralas: "
        "el censo tiene que achicarse cuando la suite crece.")


def _funciones_de_produccion_que_llaman_a(nombre: str) -> set:
    """Nombres de las funciones de src/, gui/ y cli.py que contienen una llamada a `nombre`."""
    llamadoras = set()
    for ruta in list((RAIZ / "src").rglob("*.py")) + list((RAIZ / "gui").glob("*.py")) \
            + [RAIZ / "cli.py"]:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
        for fn in ast.walk(arbol):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or fn.name == nombre:
                continue
            for nodo in ast.walk(fn):
                if isinstance(nodo, ast.Call):
                    f = nodo.func
                    llamado = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
                    if llamado == nombre:
                        llamadoras.add(fn.name)
    return llamadoras


@pytest.mark.parametrize("calificado", sorted(PUBLICAS_SIN_REFERENCIA_EN_TESTS))
def test_cada_publica_del_censo_tiene_el_consumidor_que_dice(calificado):
    """
    La razon del censo se COMPRUEBA con nombre y apellido: «la llama `X`»
    exige que la funcion X de produccion contenga la llamada (la primera
    version solo pedia «algun llamador», y cinco razones nombraban a otro:
    auditoria de EXT-11); «SIN consumidor» exige que M9 la tenga en su censo.
    """
    modulo, nombre = calificado.split(".")
    razon = PUBLICAS_SIN_REFERENCIA_EN_TESTS[calificado]
    llamadoras = _funciones_de_produccion_que_llaman_a(nombre)
    if razon.startswith("SIN consumidor"):
        from src.modulos import M9_cabezal
        assert not llamadoras, f"{calificado}: la llama {sorted(llamadoras)}"
        assert nombre in M9_cabezal.FUNCIONES_SIN_CONSUMIDOR
        return
    nombrados = re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", razon)
    assert nombrados, f"{calificado}: la razon no nombra al llamador entre acentos graves"
    for llamadora in nombrados:
        assert llamadora in llamadoras, (
            f"{calificado}: la razon dice que la llama `{llamadora}` y no la "
            f"llama; la llaman {sorted(llamadoras)}")
