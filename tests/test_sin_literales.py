"""
tests/test_sin_literales.py
===========================
Guardia automatica de la regla de arquitectura: ningun modulo declara valores.

Todo literal numerico bajo src/ -- incluido src/modulos/, donde aterrizaran
M0 a M11 -- es un defecto, salvo en los cuatro archivos exentos:

    constantes_normativas.py   valores [N] con numeral verificado
    criterios_adoptados.py     valores [N->], [C] y [A] declarados
    tolerancias.py             precision numerica, no valores de proyecto
    dominios.py                limites de dominio del dato de entrada

Excepciones dentro de un modulo vigilado:

    0, 1 y 2            (y sus equivalentes float)
    indices y rebanadas x[3], x[1:5]
    pi                  no es literal: es math.pi, un nombre
    lineas marcadas     con el comentario `# literal-ok: <razon>`

La ultima merece explicacion. Las formulas de la hoja de ruta traen numeros
que NO son valores de proyecto sino parte de la expresion matematica: el 8 de
A = (D^2/8)(theta - sen theta), el exponente 2/3 de Manning, el 4/3 del radio
hidraulico en el control de salida. Moverlos a constantes_normativas.py como
`OCHO = 8` no defiende nada y empeora la lectura. La marca los permite dejando
constancia visible en la revision: un literal exento es un literal declarado,
nunca un literal silencioso. Si prefieres cero valvulas de escape, borra el
soporte de la marca y esos numeros tendran que salir de un archivo exento.

El barrido esta parametrizado por directorio para poder probarse a si mismo
sobre un arbol sintetico: un test que solo recorre un directorio vacio no
prueba nada.
"""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
MODULOS = SRC / "modulos"

EXENTOS = {"constantes_normativas.py", "criterios_adoptados.py",
           "tolerancias.py", "dominios.py"}
NUMEROS_PERMITIDOS = {0, 1, 2}
MARCA = "# literal-ok"


# ---------------------------------------------------------------------------
# El detector
# ---------------------------------------------------------------------------

def _nodos_de_indice(arbol: ast.AST) -> set:
    """Constantes enteras que son indice o limite de rebanada: x[3], x[1:5]."""
    exentos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Subscript):
            for hijo in ast.walk(nodo.slice):
                if isinstance(hijo, ast.Constant) and isinstance(hijo.value, int):
                    exentos.add(id(hijo))
    return exentos


def _marcado(lineas, numero_de_linea: int) -> bool:
    """La marca vale en la propia linea o en la anterior (expresiones partidas)."""
    for indice in (numero_de_linea - 1, numero_de_linea - 2):
        if 0 <= indice < len(lineas) and MARCA in lineas[indice]:
            return True
    return False


def literales_numericos(codigo: str, nombre: str = "<memoria>"):
    """
    Todos los literales numericos, sin aplicar ninguna exencion. Sirve para
    comprobar que un archivo exento declara valores de verdad: en dominios.py
    los numeros llevan la marca `# literal-ok` y `literales_prohibidos` los
    dejaria pasar, con lo que el archivo pareceria vacio de valores.
    """
    arbol = ast.parse(codigo, filename=nombre)
    hallazgos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Constant):
            continue
        valor = nodo.value
        if isinstance(valor, bool) or not isinstance(valor, (int, float, complex)):
            continue                      # los strings y None no son literales numericos
        hallazgos.append((nodo.lineno, valor))
    return sorted(hallazgos)


def literales_prohibidos(codigo: str, nombre: str = "<memoria>"):
    """Devuelve [(linea, valor), ...] de los literales numericos no permitidos."""
    arbol = ast.parse(codigo, filename=nombre)
    lineas = codigo.splitlines()
    de_indice = _nodos_de_indice(arbol)
    # Se recorre el arbol otra vez para poder identificar los nodos por id():
    # literales_numericos devuelve valores, no nodos.
    hallazgos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Constant):
            continue
        valor = nodo.value
        if isinstance(valor, bool) or not isinstance(valor, (int, float, complex)):
            continue
        if id(nodo) in de_indice:
            continue
        if valor in NUMEROS_PERMITIDOS:   # 2 y 2.0 entran por igual
            continue
        if _marcado(lineas, nodo.lineno):
            continue
        hallazgos.append((nodo.lineno, valor))
    return sorted(hallazgos)


def barrido(raiz: Path) -> dict:
    """Recorre un arbol .py y devuelve {ruta relativa: [(linea, valor), ...]}."""
    faltas = {}
    for ruta in sorted(raiz.rglob("*.py")):
        if ruta.name in EXENTOS:
            continue
        # utf-8-sig y no utf-8: un editor de Windows puede dejar BOM y el
        # interprete de Python lo acepta. El barrido tiene que leer lo mismo
        # que ejecuta el programa, o falla por sintaxis en vez de reportar.
        hallazgos = literales_prohibidos(ruta.read_text(encoding="utf-8-sig"), ruta.name)
        if hallazgos:
            faltas[str(ruta.relative_to(raiz))] = hallazgos
    return faltas


# ---------------------------------------------------------------------------
# La guardia sobre el codigo real
# ---------------------------------------------------------------------------

def test_ningun_modulo_declara_literales_numericos():
    faltas = barrido(SRC)
    detalle = "\n".join(
        f"  {archivo}: " + ", ".join(f"linea {n} -> {v!r}" for n, v in hallazgos)
        for archivo, hallazgos in faltas.items()
    )
    assert not faltas, (
        "Literales numericos fuera de los archivos exentos:\n" + detalle +
        "\n\nUn valor de proyecto va a constantes_normativas.py (si es [N] con "
        "numeral) o a criterios_adoptados.py (si es [N->], [C] o [A]). Una "
        "tolerancia va a tolerancias.py. Si es parte de una formula, marca la "
        f"linea con '{MARCA}: <razon>'."
    )


def test_los_archivos_exentos_existen_y_de_verdad_llevan_literales():
    """Si alguno se renombra, la lista de exentos queda obsoleta sin avisar."""
    for nombre in EXENTOS:
        ruta = SRC / nombre
        assert ruta.is_file(), f"'{nombre}' no existe: la lista de exentos caduco"
        assert literales_numericos(ruta.read_text(encoding="utf-8-sig"), nombre), (
            f"'{nombre}' no contiene ningun literal: revisa si sigue siendo el "
            "archivo que declara valores"
        )


def test_los_limites_de_dominio_salieron_de_M0():
    """
    M0 los usa pero ya no los declara: si vuelven al modulo, el barrido los
    caza igual, pero este test dice donde tienen que estar.
    """
    m0 = (SRC / "modulos" / "M0_carga.py").read_text(encoding="utf-8-sig")
    dominios = (SRC / "dominios.py").read_text(encoding="utf-8-sig")
    for nombre in ("CBR_MAX_FISICO", "ESVIAJE_MAX", "S_CAUCE_MAX", "METROS_POR_KM"):
        assert f"{nombre} =" in dominios, f"'{nombre}' no se declara en dominios.py"
        assert f"{nombre} =" not in m0, f"'{nombre}' volvio a declararse en M0"
        assert nombre in m0, f"M0 dejo de usar '{nombre}'"


def test_el_directorio_de_modulos_esta_bajo_vigilancia():
    """M0 a M11 aterrizan en src/modulos/: debe estar dentro del barrido."""
    assert MODULOS.is_dir()
    assert MODULOS.is_relative_to(SRC)


# ---------------------------------------------------------------------------
# El detector probandose a si mismo
# ---------------------------------------------------------------------------

CODIGO_CON_VALOR_DE_PROYECTO = """
def caudal(A, R, S):
    n = 0.013
    return (1 / n) * A * R ** (2 / 3) * S ** 0.5
"""

CODIGO_PERMITIDO = """
from constantes_normativas import Y_SOBRE_D_MAX
from tolerancias import TOL_UMBRAL_NORMATIVO

def cumple_borde_libre(y, D, tabla):
    referencia = tabla[3]
    del referencia
    return (y / D) <= Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO
"""

CODIGO_CON_FORMULA_MARCADA = """
import math

def area(D, theta):
    return (D ** 2 / 8) * (theta - math.sin(theta))  # literal-ok: Sec. 4.1
"""


def test_el_detector_ve_un_valor_de_proyecto():
    hallazgos = literales_prohibidos(CODIGO_CON_VALOR_DE_PROYECTO)
    valores = [v for _, v in hallazgos]
    assert 0.013 in valores, "el n de Manning tiene que caer"


def test_el_detector_deja_pasar_lo_permitido():
    assert literales_prohibidos(CODIGO_PERMITIDO) == []


def test_la_marca_exime_la_linea_de_la_formula():
    assert literales_prohibidos(CODIGO_CON_FORMULA_MARCADA) == []


def test_sin_marca_la_misma_formula_cae():
    """La exencion es de la marca, no del numero: sin declararla, el 8 cae."""
    sin_marca = CODIGO_CON_FORMULA_MARCADA.split("#")[0].rstrip() + "\n"
    assert [v for _, v in literales_prohibidos(sin_marca)] == [8]


@pytest.mark.parametrize("codigo, esperado", [
    ("x = 0\ny = 1\nz = 2.0\n", []),                  # 0, 1, 2
    ("x = tabla[3]\n", []),                            # indice
    ("x = tabla[1:5]\n", []),                          # rebanada
    ("import math\nx = math.pi\n", []),                # pi es un nombre
    ("x = True\ny = None\nz = 'Sec. 4.1.1.3.7'\n", []),  # no son numeros
    ("x = -3.5\n", [3.5]),                             # el signo no lo salva
    ("def f(tol=1e-9):\n    return tol\n", [1e-9]),    # tolerancia sin declarar
])
def test_casos_frontera_del_detector(codigo, esperado):
    assert [v for _, v in literales_prohibidos(codigo)] == esperado


# ---------------------------------------------------------------------------
# El barrido probandose sobre un arbol sintetico
# ---------------------------------------------------------------------------

def test_el_barrido_alcanza_los_subdirectorios(tmp_path):
    """
    Prueba de recursion: hoy src/modulos/ esta vacio y el barrido real no
    demuestra nada. Aqui se le da un modulo con un literal dentro de un
    subdirectorio y tiene que encontrarlo.
    """
    modulos = tmp_path / "modulos"
    modulos.mkdir()
    (modulos / "M3_hidraulica.py").write_text(
        "V_MAX_INVENTADA = 4.5\n", encoding="utf-8")

    faltas = barrido(tmp_path)

    assert len(faltas) == 1
    (archivo, hallazgos), = faltas.items()
    assert archivo.endswith("M3_hidraulica.py")
    assert [v for _, v in hallazgos] == [4.5]


def test_el_barrido_respeta_la_lista_de_exentos(tmp_path):
    (tmp_path / "criterios_adoptados.py").write_text(
        "CRITERIOS = {'F_pga': 1.0, 'HW_D_max': 1.5}\n", encoding="utf-8")
    (tmp_path / "M2_material.py").write_text(
        "HW_D_max = 1.5\n", encoding="utf-8")

    faltas = barrido(tmp_path)

    assert list(faltas) == ["M2_material.py"]
