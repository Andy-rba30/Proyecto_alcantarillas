"""
tests/apoyo/estructura.py
=========================
Lectura ESTRUCTURAL de un modulo fuente, para los tests que hoy comprueban
subcadenas de su texto (SIS-C-01, SIS-C-02).

Por que existe
--------------
Veintidos asserts de la suite comprobaban cosas como::

    assert '"factor_muro": Criterio(' not in criterios

Eso no es una comprobacion de la declaracion: es una comprobacion del TEXTO.
Lo satisface igual un comentario, un docstring o una linea de ejemplo, y lo
evade cambiar las comillas dobles por simples -- que es exactamente el caso
que documenta SIS-C-01: una entrada ``'factor_muro': Criterio(...)`` dentro de
``CRITERIOS`` dejaba la suite entera en verde.

Las funciones de aqui responden a la misma pregunta leyendo el ARBOL: si el
nombre esta asignado, si la clave existe en el diccionario, con que
constructor se construyo su valor. Ni las comillas, ni el formato, ni un
comentario cambian la respuesta.

Todas leen el archivo con ``utf-8-sig``, igual que el barrido de literales: un
editor de Windows puede dejar BOM y el interprete de Python lo acepta.
"""

import ast
from functools import lru_cache
from pathlib import Path
from typing import Optional, Set


@lru_cache(maxsize=None)
def _arbol(ruta: str) -> ast.Module:
    return ast.parse(Path(ruta).read_text(encoding="utf-8-sig"), filename=ruta)


def arbol(ruta) -> ast.Module:
    """El AST del modulo, cacheado por ruta."""
    return _arbol(str(ruta))


def nombres_asignados(ruta) -> Set[str]:
    """
    Nombres asignados A NIVEL DE MODULO (incluida la asignacion anotada).

    Sustituye a ``f"{nombre} =" in fuente``, que un comentario satisface.
    """
    nombres = set()
    for nodo in arbol(ruta).body:
        if isinstance(nodo, ast.Assign):
            for destino in nodo.targets:
                if isinstance(destino, ast.Name):
                    nombres.add(destino.id)
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            nombres.add(nodo.target.id)
    return nombres


def valor_asignado(ruta, nombre: str) -> Optional[ast.AST]:
    """El nodo del valor asignado a `nombre` a nivel de modulo, o None."""
    for nodo in arbol(ruta).body:
        if isinstance(nodo, ast.Assign):
            for destino in nodo.targets:
                if isinstance(destino, ast.Name) and destino.id == nombre:
                    return nodo.value
        elif (isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name)
              and nodo.target.id == nombre):
            return nodo.value
    return None


def nombres_usados(ruta) -> Set[str]:
    """
    Nombres LEIDOS en el modulo (contexto Load) mas los importados.

    Sustituye a ``nombre in fuente``, que un docstring satisface.
    """
    usados = set()
    for nodo in ast.walk(arbol(ruta)):
        if isinstance(nodo, ast.Name) and isinstance(nodo.ctx, ast.Load):
            usados.add(nodo.id)
        elif isinstance(nodo, ast.Attribute):
            usados.add(nodo.attr)
        elif isinstance(nodo, ast.ImportFrom):
            usados.update(alias.asname or alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.Import):
            usados.update((alias.asname or alias.name).split(".")[0]
                          for alias in nodo.names)
    return usados


def claves_de_dict(ruta, nombre: str) -> Set[str]:
    """
    Las claves de texto del diccionario de modulo `nombre`.

    Sustituye a ``'"clave":' in fuente``: no distingue comillas simples de
    dobles porque no mira comillas (SIS-C-01).
    """
    valor = valor_asignado(ruta, nombre)
    if not isinstance(valor, ast.Dict):
        return set()
    return {clave.value for clave in valor.keys
            if isinstance(clave, ast.Constant) and isinstance(clave.value, str)}


def constructor_de_clave(ruta, nombre: str, clave: str) -> Optional[str]:
    """
    Nombre del constructor con que se construyo ``nombre[clave]``, o None si
    la clave no esta o su valor no es una llamada.

    Es la comprobacion que sustituye a ``'"PGA_roca_B": Criterio(' in fuente``:
    responde "con que se declaro esta clave", que es la pregunta real.
    """
    valor = valor_asignado(ruta, nombre)
    if not isinstance(valor, ast.Dict):
        return None
    for nodo_clave, nodo_valor in zip(valor.keys, valor.values):
        if not (isinstance(nodo_clave, ast.Constant) and nodo_clave.value == clave):
            continue
        if not isinstance(nodo_valor, ast.Call):
            return None
        f = nodo_valor.func
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute):
            return f.attr
        return None
    return None


def llamadas_a(ruta, nombre_funcion: str) -> int:
    """Cuantas veces se LLAMA a `nombre_funcion` en el modulo."""
    total = 0
    for nodo in ast.walk(arbol(ruta)):
        if not isinstance(nodo, ast.Call):
            continue
        f = nodo.func
        llamado = f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) else None)
        if llamado == nombre_funcion:
            total += 1
    return total


def argumentos_de_texto(ruta, nombre_funcion: str) -> Set[str]:
    """
    Los argumentos que son literal de texto en toda llamada a
    `nombre_funcion`, posicionales y por palabra clave.

    Sirve para preguntar "que claves consume este modulo" sin leer el texto:
    p. ej. ``argumentos_de_texto(M8, "valor")`` da las claves de criterio que
    M8 pide.
    """
    textos = set()
    for nodo in ast.walk(arbol(ruta)):
        if not isinstance(nodo, ast.Call):
            continue
        f = nodo.func
        llamado = f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) else None)
        if llamado != nombre_funcion:
            continue
        for arg in list(nodo.args) + [kw.value for kw in nodo.keywords]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                textos.add(arg.value)
    return textos


def textos_de_llamada_o_indice(ruta) -> Set[str]:
    """
    Los literales de texto que el modulo USA EN TIEMPO DE EJECUCION como
    argumento de una llamada o como clave de un subindice.

    Es la version precisa de ``clave in fuente`` (SIS-C-02): responde "este
    modulo INVOCA esta clave", que es la pregunta, en vez de "esta cadena
    aparece en el archivo", que la satisface un comentario, una linea de
    ejemplo o el mensaje de una excepcion que la nombra.

    La comparacion es por IGUALDAD del literal, no por subcadena: un motivo
    de excepcion que mencione la clave dentro de una frase no cuenta como
    invocacion, y debe no contar -- explicar por que un criterio NO se usa es
    justo lo contrario de usarlo.
    """
    textos = set()
    for nodo in ast.walk(arbol(ruta)):
        if isinstance(nodo, ast.Call):
            candidatos = list(nodo.args) + [kw.value for kw in nodo.keywords]
        elif isinstance(nodo, ast.Subscript):
            candidatos = [nodo.slice]
        else:
            continue
        for candidato in candidatos:
            if isinstance(candidato, ast.Constant) and isinstance(candidato.value, str):
                textos.add(candidato.value)
    return textos
