"""
tests/apoyo/mutacion.py
=======================
Arnes de MUTACION del proyecto (EXT-11, propuesta 4 del dictamen): genera
mutantes por AST de los modulos de calculo, corre contra cada uno un conjunto
de tests OBJETIVO en un subproceso, y reporta el mutation score y la lista
de supervivientes. No es `mutmut`: el prompt de EXT-11 mandaba consultar esa
dependencia de TEST y sin respuesta no se suma nada (ficha EXT-11-01). Es
suficiente para lo que la sesion tiene que medir -- que las propiedades de
`tests/test_ext11_propiedades.py` MATAN mutantes que la linea base dejaba
vivos -- y cabe en un archivo que se lee entero.

Como se usa
-----------

    python3 -m tests.apoyo.mutacion                     # la corrida de EXT-11
    python3 -m tests.apoyo.mutacion --modulo M3_hidraulica --funcion tirante_normal
    python3 -m tests.apoyo.mutacion --informe salida.json --trabajadores 4

Se ejecuta desde la raiz del repositorio. Copia el arbol de trabajo (los
archivos que `git ls-files` conoce mas los no rastreados que no ignora) a
un directorio temporal POR TRABAJADOR, sustituye alli el modulo mutado y
corre `pytest` sobre los objetivos. El arbol real no se toca nunca.

Que es un mutante
-----------------
Un cambio de UN nodo del AST dentro de una funcion, de los operadores de
`OPERADORES`. Se generan solo sobre el codigo, nunca sobre docstrings ni
sobre cadenas: las constantes que se mutan son numericas, y por eso un
`# literal-ok` (formula transcrita) TAMBIEN se muta -- es exactamente el
numero que un test de propiedad tiene que defender. Dos operadores son del
DOMINIO y no de la sintaxis: el intercambio del par (n_min, n_max) por
cualquiera de sus tres nombres (`n_min`, `n_max`, `n_para_*`), y el
intercambio de las dos velocidades de la regla de doble n
(`V_erosion`, `V_sedimentacion`).

Veredicto por mutante
---------------------
    muerto        pytest devolvio distinto de 0 (fallo, error o excepcion al
                  importar) o supero el tiempo limite;
    sobrevive     pytest en verde: ningun test objetivo nota el cambio.

El score es muertos / total. Un superviviente NO es automaticamente un
hueco: puede ser un mutante EQUIVALENTE (produce el mismo programa) o uno
cuya diferencia solo se ve en un camino que ningun test objetivo recorre.
Cada superviviente aceptado se censa con su razon en
`tests/test_ext11_mutacion.py::SUPERVIVIENTES_CON_RAZON`, y ese test exige
que el censo siga anclado al codigo.
"""

from __future__ import annotations

import argparse
import ast
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, List, Optional, Sequence

RAIZ = Path(__file__).resolve().parents[2]

# Los modulos que EXT-11 mide (M3-M5/MD) y el par (n_min, n_max): donde nace
# (M2) y donde se lee (las tres propiedades de `Material` en modelos.py).
MODULOS_DE_EXT11 = {
    "src/modulos/M3_hidraulica.py": None,
    "src/modulos/M4_control.py": None,
    "src/modulos/M5_verificaciones.py": None,
    "src/modulos/MD.py": None,
    "src/modulos/M2_material.py": ("_par_de_manning", "numero_de_celdas",
                                   "catalogo", "n_manning_hdpe",
                                   "_fila_manning_de_cajon"),
    "src/modelos.py": ("n_para_capacidad", "n_para_velocidad_maxima",
                       "n_para_velocidad_minima"),
}

# Los tests OBJETIVO: los unitarios del motor, los de aceptacion de EXT-2 y
# EXT-3 y las propiedades de EXT-11. Corren en ~1.5 s; la linea base y la
# CLI quedan para la SEGUNDA vuelta, solo sobre los supervivientes.
OBJETIVOS = (
    "tests/test_ext11_propiedades.py",
    "tests/test_M2_material.py",
    "tests/test_M3_hidraulica.py",
    "tests/test_M4_control.py",
    "tests/test_M5_verificaciones.py",
    "tests/test_MD.py",
    "tests/test_seccion_rectangular.py",
    "tests/test_ext1_entradas.py",      # el bloque de TW de la Sec. 1.3 (M3)
    "tests/test_ext2_multicelda_transicion.py",
    "tests/test_ext3_regimen_barril.py",
    "tests/test_ea_perfil_lamina.py",   # E-A: el perfil de la lamina (M4/M5)
)
SEGUNDA_VUELTA = (
    "tests/test_linea_base.py",
    "tests/test_cierre_perfil.py",
    "tests/test_cli.py",
)
TIEMPO_LIMITE_S = 120

# Intercambios de DOMINIO: el par de n y las dos velocidades.
PAR_N = {
    "n_min": "n_max", "n_max": "n_min",
    "n_para_capacidad": "n_para_velocidad_maxima",
    "n_para_velocidad_maxima": "n_para_capacidad",
    "n_para_velocidad_minima": "n_para_velocidad_maxima",
}
PAR_V = {"V_erosion": "V_sedimentacion", "V_sedimentacion": "V_erosion"}

OPERADORES = (
    "aritmetico",      # + <-> -, * <-> /, ** -> *
    "comparacion",     # < <-> <=, > <-> >=, == <-> !=, is <-> is not, in <-> not in
    "constante",       # numero -> numero + 1
    "booleano",        # and <-> or ; not x -> x
    "condicion",       # if c -> if not c
    "retorno_none",    # return x -> return None
    "par_n",           # n_min <-> n_max, n_para_* entre si
    "par_v",           # V_erosion <-> V_sedimentacion
)

_ARITMETICOS = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div,
                ast.Div: ast.Mult, ast.Pow: ast.Mult}
_COMPARACIONES = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE,
                  ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
                  ast.Is: ast.IsNot, ast.IsNot: ast.Is, ast.In: ast.NotIn,
                  ast.NotIn: ast.In}


@dataclass(frozen=True)
class Mutante:
    modulo: str          # ruta relativa del archivo
    funcion: str         # nombre calificado (Clase.metodo si aplica)
    operador: str
    linea: int
    original: str        # el nodo antes, `ast.unparse`
    mutado: str          # el nodo despues
    ordinal: int = 1     # k-esima mutacion IDENTICA dentro de la funcion

    @property
    def clave(self) -> str:
        """
        Identidad ESTABLE del mutante: modulo, funcion, operador, fragmento
        y ordinal. Sin el ordinal, dos sitios con el mismo fragmento en la
        misma funcion (medido: 31 pares en los modulos de EXT-11) caian en
        una sola clave y un censo cubria dos mutantes con una razon. No
        lleva la linea a proposito: CLAUDE.md ancla por simbolo, nunca por
        numero de linea, y el ordinal sobrevive a las ediciones de arriba.
        """
        base = f"{self.modulo}::{self.funcion}::{self.operador}::{self.original} -> {self.mutado}"
        return base if self.ordinal == 1 else f"{base} #{self.ordinal}"


# ---------------------------------------------------------------------------
# Generacion
# ---------------------------------------------------------------------------

def _funciones(arbol: ast.Module) -> Iterator[tuple]:
    """(nombre_calificado, nodo FunctionDef) de todo el modulo, clases incluidas."""
    def _recorrer(cuerpo, prefijo=""):
        for nodo in cuerpo:
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield prefijo + nodo.name, nodo
                yield from _recorrer(nodo.body, prefijo + nodo.name + ".")
            elif isinstance(nodo, ast.ClassDef):
                yield from _recorrer(nodo.body, prefijo + nodo.name + ".")
    yield from _recorrer(arbol.body)


def _es_docstring(nodo, padre) -> bool:
    return (isinstance(padre, ast.Expr) and isinstance(nodo, ast.Constant)
            and isinstance(nodo.value, str))


def _sitios(funcion: ast.FunctionDef) -> Iterator[tuple]:
    """(nodo, campo, indice, padre) de cada nodo mutable del cuerpo."""
    for padre in ast.walk(funcion):
        for campo, valor in ast.iter_fields(padre):
            if isinstance(valor, ast.AST):
                yield valor, campo, None, padre
            elif isinstance(valor, list):
                for i, elemento in enumerate(valor):
                    if isinstance(elemento, ast.AST):
                        yield elemento, campo, i, padre


def _reemplazar(padre, campo, indice, nuevo):
    if indice is None:
        setattr(padre, campo, nuevo)
    else:
        getattr(padre, campo)[indice] = nuevo


def _mutaciones_de(nodo, padre) -> Iterator[tuple]:
    """(operador, nodo_mutado) para cada mutacion aplicable al nodo."""
    if isinstance(nodo, ast.BinOp) and type(nodo.op) in _ARITMETICOS:
        yield "aritmetico", ast.BinOp(left=nodo.left,
                                      op=_ARITMETICOS[type(nodo.op)](),
                                      right=nodo.right)
    if isinstance(nodo, ast.Compare) and len(nodo.ops) == 1 \
            and type(nodo.ops[0]) in _COMPARACIONES:
        yield "comparacion", ast.Compare(
            left=nodo.left, ops=[_COMPARACIONES[type(nodo.ops[0])]()],
            comparators=nodo.comparators)
    if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float) \
            and not isinstance(nodo.value, bool) \
            and not isinstance(padre, ast.JoinedStr):
        yield "constante", ast.Constant(value=nodo.value + 1)
    if isinstance(nodo, ast.BoolOp):
        yield "booleano", ast.BoolOp(
            op=ast.Or() if isinstance(nodo.op, ast.And) else ast.And(),
            values=nodo.values)
    if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, ast.Not):
        yield "booleano", nodo.operand
    if isinstance(nodo, ast.If):
        yield "condicion", ast.If(test=ast.UnaryOp(op=ast.Not(), operand=nodo.test),
                                  body=nodo.body, orelse=nodo.orelse)
    if isinstance(nodo, ast.Return) and nodo.value is not None \
            and not (isinstance(nodo.value, ast.Constant)
                     and nodo.value.value is None):
        yield "retorno_none", ast.Return(value=ast.Constant(value=None))
    if isinstance(nodo, ast.Attribute) and nodo.attr in PAR_N:
        yield "par_n", ast.Attribute(value=nodo.value, attr=PAR_N[nodo.attr],
                                     ctx=nodo.ctx)
    if isinstance(nodo, ast.Attribute) and nodo.attr in PAR_V:
        yield "par_v", ast.Attribute(value=nodo.value, attr=PAR_V[nodo.attr],
                                     ctx=nodo.ctx)
    if isinstance(nodo, ast.keyword) and nodo.arg in PAR_N:
        yield "par_n", ast.keyword(arg=PAR_N[nodo.arg], value=nodo.value)


def _fragmento(nodo) -> str:
    """El nodo como texto; un `if` o un `return` solo por su cabecera."""
    if isinstance(nodo, ast.If):
        return f"if {ast.unparse(nodo.test)}:"
    if isinstance(nodo, ast.Return):
        return f"return {ast.unparse(nodo.value)}"
    return ast.unparse(nodo)


def generar(modulo: str, funciones: Optional[Sequence[str]] = None,
            operadores: Sequence[str] = OPERADORES) -> List[tuple]:
    """
    [(Mutante, fuente_mutada)] del modulo. `funciones` limita a esos
    nombres calificados (o a los que terminan en ellos).
    """
    ruta = RAIZ / modulo
    fuente = ruta.read_text(encoding="utf-8")
    salida = []
    arbol = ast.parse(fuente)
    vistos: dict = {}
    for nombre, funcion in _funciones(arbol):
        if funciones and not any(nombre == f or nombre.endswith("." + f)
                                 for f in funciones):
            continue
        for nodo, campo, indice, padre in list(_sitios(funcion)):
            if _es_docstring(nodo, padre):
                continue
            for operador, nuevo in _mutaciones_de(nodo, padre):
                if operador not in operadores:
                    continue
                ast.copy_location(nuevo, nodo)
                ast.fix_missing_locations(nuevo)
                _reemplazar(padre, campo, indice, nuevo)
                try:
                    fuente_mutada = ast.unparse(arbol)
                finally:
                    _reemplazar(padre, campo, indice, nodo)
                identidad = (nombre, operador, _fragmento(nodo), _fragmento(nuevo))
                vistos[identidad] = vistos.get(identidad, 0) + 1
                salida.append((Mutante(
                    modulo=modulo, funcion=nombre, operador=operador,
                    linea=getattr(nodo, "lineno", 0),
                    original=_fragmento(nodo), mutado=_fragmento(nuevo),
                    ordinal=vistos[identidad]),
                    fuente_mutada))
    return salida


# ---------------------------------------------------------------------------
# Ejecucion
# ---------------------------------------------------------------------------

def _archivos_del_arbol() -> List[str]:
    """Rastreados mas no rastreados no ignorados: el arbol de trabajo real."""
    salida = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=RAIZ, capture_output=True, text=True, check=True).stdout
    return [linea for linea in salida.splitlines()
            if linea and not linea.startswith("normas/")]


def _copiar_arbol(destino: Path) -> None:
    for relativo in _archivos_del_arbol():
        origen = RAIZ / relativo
        if not origen.is_file():
            continue
        objetivo = destino / relativo
        objetivo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, objetivo)


def correr_pytest(arbol: Path, objetivos: Sequence[str],
                  tiempo_limite: float = TIEMPO_LIMITE_S) -> tuple:
    """(codigo, segundos) de pytest sobre los objetivos en ese arbol."""
    inicio = time.monotonic()
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
             "--no-header", *objetivos],
            cwd=arbol, capture_output=True, text=True, timeout=tiempo_limite,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        codigo = r.returncode
    except subprocess.TimeoutExpired:
        codigo = -1
    return codigo, time.monotonic() - inicio


def preparar_arboles(trabajadores: int) -> List[Path]:
    """Una copia del arbol de trabajo por trabajador, tomada UNA sola vez."""
    base = Path(tempfile.mkdtemp(prefix="mutacion_"))
    arboles = []
    for i in range(trabajadores):
        arbol = base / f"t{i}"
        _copiar_arbol(arbol)
        arboles.append(arbol)
    return arboles


class LineaBaseRoja(RuntimeError):
    """Los objetivos no pasan sobre el arbol SIN mutar: no se puede medir."""


def exigir_linea_base_verde(arbol: Path, objetivos: Sequence[str]) -> float:
    """
    La corrida de REFERENCIA: los objetivos sobre el arbol sin mutar tienen
    que pasar. Sin ella, un objetivo roto por cualquier causa ajena (un test
    en rojo, un error de coleccion) mataria a TODOS los mutantes y el score
    subiria a 1.0 sin medir nada (auditoria adversarial de EXT-11).
    """
    codigo, segundos = correr_pytest(arbol, objetivos)
    if codigo != 0:
        raise LineaBaseRoja(
            f"los objetivos {list(objetivos)} devuelven {codigo} sobre el arbol "
            "sin mutar: arregla la suite antes de medir la mutacion")
    return segundos


def evaluar(mutantes: Sequence[tuple], objetivos: Sequence[str] = OBJETIVOS,
            trabajadores: int = 1, avisar=None,
            arboles: Optional[Sequence[Path]] = None,
            comprobar_referencia: bool = True) -> List[dict]:
    """
    Corre cada mutante en un arbol temporal propio del trabajador y devuelve
    [{mutante, veredicto, codigo, segundos}]. Si se pasan `arboles`, se
    reutilizan (y no se borran); si no, se copian aqui y se borran al salir.
    Antes de mutar nada, `exigir_linea_base_verde` corre los objetivos
    sobre el arbol intacto (salvo `comprobar_referencia=False`).
    """
    propios = arboles is None
    if propios:
        arboles = preparar_arboles(trabajadores)
    if comprobar_referencia:
        exigir_linea_base_verde(arboles[0], objetivos)
    libres = list(arboles)
    resultados = []

    def _uno(indice_y_mutante):
        indice, (mutante, fuente_mutada) = indice_y_mutante
        arbol = libres.pop()
        try:
            destino = arbol / mutante.modulo
            original = destino.read_text(encoding="utf-8")
            destino.write_text(fuente_mutada, encoding="utf-8")
            try:
                codigo, segundos = correr_pytest(arbol, objetivos)
            finally:
                destino.write_text(original, encoding="utf-8")
        finally:
            libres.append(arbol)
        veredicto = "sobrevive" if codigo == 0 else "muerto"
        fila = {"mutante": asdict(mutante), "veredicto": veredicto,
                "codigo": codigo, "segundos": round(segundos, 2)}
        if avisar:
            avisar(indice, len(mutantes), fila)
        return fila

    try:
        with ThreadPoolExecutor(max_workers=len(arboles)) as pool:
            resultados = list(pool.map(_uno, enumerate(mutantes)))
    finally:
        if propios:
            shutil.rmtree(arboles[0].parent, ignore_errors=True)
    return resultados


def resumen(resultados: Sequence[dict]) -> dict:
    total = len(resultados)
    muertos = sum(1 for r in resultados if r["veredicto"] == "muerto")
    return {"total": total, "muertos": muertos, "sobreviven": total - muertos,
            "score": round(muertos / total, 4) if total else None}


def _principal(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--modulo", action="append",
                   help="ruta relativa (src/modulos/M3_hidraulica.py) o nombre "
                        "corto (M3_hidraulica); por defecto los de EXT-11")
    p.add_argument("--funcion", action="append", help="limita a estas funciones")
    p.add_argument("--operador", action="append", choices=OPERADORES)
    p.add_argument("--trabajadores", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    p.add_argument("--informe", type=Path, help="JSON con el detalle")
    p.add_argument("--segunda-vuelta", action="store_true",
                   help="reevaluar los supervivientes contra la linea base y la CLI")
    p.add_argument("--solo-generar", action="store_true")
    p.add_argument("--objetivo", action="append",
                   help="sustituye los tests objetivo de la primera vuelta "
                        "(para medir, por ejemplo, la suite SIN las propiedades)")
    args = p.parse_args(argv)
    objetivos = tuple(args.objetivo) if args.objetivo else OBJETIVOS

    modulos = dict(MODULOS_DE_EXT11)
    if args.modulo:
        modulos = {}
        for m in args.modulo:
            ruta = m if m.endswith(".py") else f"src/modulos/{m}.py"
            modulos[ruta] = MODULOS_DE_EXT11.get(ruta)
    mutantes = []
    for ruta, funciones in modulos.items():
        mutantes += generar(ruta, args.funcion or funciones,
                            args.operador or OPERADORES)
    print(f"{len(mutantes)} mutantes generados en {len(modulos)} modulos")
    if args.solo_generar:
        for m, _ in mutantes:
            print(" ", m.clave)
        return 0

    def _avisar(i, n, fila):
        m = fila["mutante"]
        print(f"[{i + 1}/{n}] {fila['veredicto']:9s} {fila['segundos']:5.1f}s "
              f"{m['modulo']}::{m['funcion']} {m['operador']} "
              f"{m['original'][:40]!r} -> {m['mutado'][:40]!r}", flush=True)

    arboles = preparar_arboles(args.trabajadores)
    try:
        resultados = evaluar(mutantes, objetivos, avisar=_avisar, arboles=arboles)
        r = resumen(resultados)
        print(f"\nPRIMERA VUELTA ({', '.join(objetivos)}): "
              f"{r['muertos']}/{r['total']} muertos, score {r['score']}")
        informe = {"objetivos": list(objetivos), "resumen": r,
                   "resultados": resultados}
        if args.segunda_vuelta:
            vivos = [(Mutante(**f["mutante"]), None) for f in resultados
                     if f["veredicto"] == "sobrevive"]
            por_clave = {m.clave: fuente for m, fuente in mutantes}
            vivos = [(m, por_clave[m.clave]) for m, _ in vivos]
            segunda = evaluar(vivos, SEGUNDA_VUELTA, avisar=_avisar,
                              arboles=arboles)
            r2 = resumen(segunda)
            print(f"\nSEGUNDA VUELTA ({', '.join(SEGUNDA_VUELTA)}) sobre los "
                  f"{r2['total']} supervivientes: {r2['muertos']} mueren, "
                  f"{r2['sobreviven']} sobreviven a todo")
            informe["segunda_vuelta"] = {"objetivos": list(SEGUNDA_VUELTA),
                                         "resumen": r2, "resultados": segunda}
    finally:
        shutil.rmtree(arboles[0].parent, ignore_errors=True)
    if args.informe:
        args.informe.write_text(json.dumps(informe, ensure_ascii=False, indent=1),
                                encoding="utf-8")
        print(f"informe en {args.informe}")
    return 0


if __name__ == "__main__":
    sys.exit(_principal())
