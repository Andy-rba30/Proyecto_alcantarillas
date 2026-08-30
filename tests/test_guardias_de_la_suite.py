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
import io
import tokenize
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
TESTS = RAIZ / "tests"
CONFTEST = RAIZ / "conftest.py"

# Los directorios de la suite. `conftest.py` entra porque declara los
# criterios de la corrida y podria comparar floats igual que un test.
ARCHIVOS_DE_PRUEBA = sorted(TESTS.rglob("test_*.py")) + [CONFTEST]

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
    """
    if isinstance(nodo, ast.Call):
        return
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


def _lineas_exentas(codigo: str) -> set:
    """
    Lineas con la marca `# float-exacto: <razon>`, como COMENTARIO.

    Mismo mecanismo y misma exigencia de razon que la marca `# literal-ok` del
    barrido de literales: la exencion es visible en revision y dice por que.
    Se usa donde la igualdad exacta ES lo que se prueba -- los autotests de
    los propios detectores comparan la lista de literales que encontraron
    contra los mismos dobles que parsearon, y aproximarla la vaciaria de
    sentido.
    """
    exentas = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(codigo).readline):
            if tok.type != tokenize.COMMENT:
                continue
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
    import criterios_adoptados as ca

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
    import criterios_adoptados as ca

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
    esperados = {
        "M5_verificaciones.py::v8_evento_extremo":
            ("src/modulos/M5_verificaciones.py", "v8_evento_extremo"),
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
    from modelos import Material

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
CUPO_APPROX_CON_TOLERANCIA_LITERAL = 101


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
        elif all(isinstance(kw.value, ast.Name) for kw in tolerancias):
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
