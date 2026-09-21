"""
tests/apoyo/guia_perfil.py
==========================
Lo que `docs/guia_perfil.md` NO escribe a mano (PF-5): las tablas que salen
de simbolos del programa, y el lector de los bloques de la guia que la suite
ejecuta.

La guia es un documento para un tesista que no ha leido el codigo, y por eso
tiene dos clases de contenido con dos guardias distintas:

  1. BLOQUES GENERADOS. Las listas de columnas del CSV, de claves de
     `--datos-externos`, de datos de sitio declarables, de criterios [A] de
     perfil sin valor y de columnas del CSV resumen salen de los simbolos
     que las gobiernan (`M0_carga.COLUMNAS`, `servicio.CLAVES_EXTERNAS`,
     `datos_sitio.DATOS_SITIO`, `ca.criterios_de_perfil_sin_valor()`,
     `M11.COLUMNAS_RESUMEN_CSV`, `sesion.sesion_vacia`). En la guia van entre
     las marcas `<!-- generado: nombre -->` y `<!-- fin: nombre -->`, y
     `tests/test_guia_perfil.py` compara el texto entre marcas con lo que
     este modulo produce, como hacen los cuatro documentos generados de
     `docs/`. Si un criterio cambia de forma, el test lo dice. Se regeneran
     con:

         python -m tests.apoyo.guia_perfil

     que imprime cada bloque con sus marcas, listo para pegar.

  2. BLOQUES QUE CORREN. Cada bloque de comandos de la guia lleva en la linea
     de apertura de su cerca un `id=` (```sh id=perfil), y cada archivo que
     la guia muestra lleva `archivo=` (```json archivo=guia/externos.json).
     `bloques_de_la_guia` los lee, y el test los escribe y los ejecuta en
     subproceso, en el orden en que la guia los presenta, sustituyendo solo
     tres cosas: `python` por el interprete de la suite, `cli.py` por su
     ruta absoluta y las rutas `tests/...` por las del repositorio. Lo demas
     se ejecuta tal como el tesista lo teclearia.

Este modulo no importa `src.modulos` de calculo mas alla de M0 y M11 (que
declaran los simbolos) y no corre el pipeline: derivar una tabla no es
calcular nada.
"""
from __future__ import annotations

import re
import shlex
import textwrap
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import servicio
from src import sesion
from src.modelos import DeTabla, Derivada, Familia, Libre
from src.modulos import M0_carga as M0
from src.modulos import M11_reporte as M11

MARCA_INICIO = "<!-- generado: {nombre} -->"
MARCA_FIN = "<!-- fin: {nombre} -->"

# Las banderas de la CLI que escriben una clave externa, leidas del parser
# real (`cli._parser`): la clave -> la opcion larga. El diccionario
# `banderas` de `cli.main` es el que las une por `dest`, y por eso aqui se
# resuelve por `dest` y no por nombre.
_DEST_DE_CLAVE = {"luz_m": "luz", "TW_m": "TW", "longitud_m": "longitud",
                  "L_hidraulico_m": "l_hidraulico",
                  "categoria_tr": "categoria_tr"}


def _bandera_de(clave: str) -> str:
    import cli  # perezoso: el modulo se importa tambien desde el __main__
    dest = _DEST_DE_CLAVE.get(clave)
    if dest is None:
        return "—"
    for accion in cli._parser()._actions:
        if accion.dest == dest and accion.option_strings:
            return "`" + max(accion.option_strings, key=len) + "`"
    raise KeyError(f"el parser de la CLI no tiene una bandera con dest={dest!r}")


def _tabla(encabezados: Sequence[str], filas: Iterable[Sequence[str]]) -> str:
    lineas = ["| " + " | ".join(encabezados) + " |",
              "|" + "|".join("---" for _ in encabezados) + "|"]
    lineas += ["| " + " | ".join(str(c) for c in fila) + " |" for fila in filas]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 1. Las columnas del CSV, familia por familia
# ---------------------------------------------------------------------------

def tabla_columnas() -> str:
    """`M0_carga.COLUMNAS` en su orden, con lo que cada familia admite vacio."""
    numericas = set(M0.columnas_numericas())
    vacias = {f: M0.columnas_que_admiten_vacio(f) for f in Familia}
    filas = []
    for columna in M0.COLUMNAS:
        celdas = [f"`{columna}`", "sí" if columna in numericas else "no"]
        for f in Familia:
            celdas.append("puede ir vacía" if columna in vacias[f] else "obligatoria")
        filas.append(celdas)
    return _tabla(["Columna", "Numérica", "Familia A", "Familia B", "Familia C"], filas)


def lista_vacios_admitidos() -> str:
    """`M0_carga.VACIOS_ADMITIDOS`: quien debe cada celda que puede ir vacia."""
    lineas = []
    for vacio in M0.VACIOS_ADMITIDOS:
        columnas = ", ".join(f"`{c}`" for c in vacio.columnas)
        donde = ("en las tres familias" if not vacio.familias
                 else "sólo en Familia " + ", ".join(f.value for f in vacio.familias))
        espera = ("la corrida marca la fila como pendiente de ese tablero"
                  if vacio.marca_pendiente else "no espera a nadie")
        lineas.append(f"- {columnas} — {donde}. Lo debe: {vacio.quien_lo_debe}. "
                      f"Si va vacía, {espera}.")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 2. Las claves de --datos-externos
# ---------------------------------------------------------------------------

def tabla_externos() -> str:
    """`servicio.CLAVES_EXTERNAS`, con lo que el programa sabe de cada una."""
    filas = []
    for clave in servicio.CLAVES_EXTERNAS:
        es_columna = clave in M0.COLUMNAS
        tipo = "texto" if clave in servicio.CLAVES_TEXTO else "número"
        familias = servicio.FAMILIAS_QUE_USAN.get(clave)
        usan = ("las tres" if familias is None
                else ", ".join(f.value for f in familias))
        if clave in servicio.EXTERNOS_CON_VIA_ALTERNA:
            si_falta = "el programa la resuelve por otra vía"
        elif es_columna:
            si_falta = "vale la celda del CSV"
        else:
            si_falta = "el pre-vuelo la lista como falta"
        filas.append([f"`{clave}`", "sí" if es_columna else "no", tipo,
                      _bandera_de(clave), usan, si_falta])
    return _tabla(["Clave", "¿Columna del CSV?", "Tipo", "Bandera",
                   "Familias que la usan", "Si no se declara"], filas)


# ---------------------------------------------------------------------------
# 3. Los datos de sitio [S] que una obra declara por sesion
# ---------------------------------------------------------------------------

def tabla_sitio() -> str:
    """`datos_sitio.DATOS_SITIO`: que se puede declarar en un sitio.json y que no."""
    filas = []
    for clave, dato in ds.DATOS_SITIO.items():
        if isinstance(dato.resolucion, Derivada):
            de = ", ".join(f"`{d}`" for d in dato.resolucion.de)
            declarable = f"no: se deriva de {de}"
        else:
            declarable = "sí"
        opciones = ", ".join(f"`{o}`" for o in dato.opciones) if dato.opciones else "—"
        filas.append([f"`{clave}`", dato.forma, dato.nivel, declarable, opciones])
    return _tabla(["Clave", "Forma", "Nivel", "¿Se declara en sitio.json?",
                   "Opciones cerradas"], filas)


# ---------------------------------------------------------------------------
# 4. Los [A] de perfil sin valor, con su forma y su ventana
# ---------------------------------------------------------------------------

def ventana_de(clave: str) -> str:
    """
    La ventana de un criterio, dicha con lo que su ficha declara: las opciones
    cerradas de una `categoria` (que viven en `sensibilidad`), las tablas de
    una resolucion `DeTabla`, o el `dominio` de una `Libre`.
    """
    c = ca.CRITERIOS[clave]
    r = c.resolucion
    if c.forma == "categoria":
        return "una de: " + ", ".join(f"`{o}`" for o in c.sensibilidad)
    if isinstance(r, DeTabla):
        return "la clave de una fila de " + ", ".join(f"`{t}`" for t in r.tablas)
    if isinstance(r, Libre) and r.dominio:
        return r.dominio
    raise ValueError(f"{clave}: no se sabe escribir su ventana ({type(r).__name__})")


def tabla_criterios() -> str:
    """`ca.criterios_de_perfil_sin_valor()`: clave, etiqueta, forma y ventana."""
    filas = []
    for clave in ca.criterios_de_perfil_sin_valor():
        c = ca.CRITERIOS[clave]
        forma = c.forma if isinstance(c.forma, str) else " o ".join(c.forma)
        filas.append([f"`{clave}`", f"[{c.etiqueta}]", f"`{forma}`", ventana_de(clave)])
    return _tabla(["Criterio", "Etiqueta", "Forma", "Ventana"], filas)


# ---------------------------------------------------------------------------
# 5. Las salidas
# ---------------------------------------------------------------------------

def columnas_csv_resumen() -> str:
    """`M11.COLUMNAS_RESUMEN_CSV`, en su orden."""
    return ", ".join(f"`{c}`" for c in M11.COLUMNAS_RESUMEN_CSV)


def claves_de_sesion() -> str:
    """Las claves de una sesion vacia (`sesion.sesion_vacia`), formato actual."""
    claves = ", ".join(f"`{c}`" for c in sesion.sesion_vacia("guia"))
    return f"Formato {sesion.FORMATO_SESION}: {claves}."


# ---------------------------------------------------------------------------
# Todos los bloques generados, con nombre
# ---------------------------------------------------------------------------

GENERADORES = {
    "columnas": tabla_columnas,
    "vacios": lista_vacios_admitidos,
    "externos": tabla_externos,
    "sitio": tabla_sitio,
    "criterios": tabla_criterios,
    "csv_resumen": columnas_csv_resumen,
    "sesion": claves_de_sesion,
}


def bloques_generados() -> Dict[str, str]:
    return {nombre: fn() for nombre, fn in GENERADORES.items()}


def bloques_generados_en(texto: str) -> Dict[str, str]:
    """{nombre: cuerpo} de cada par de marcas de la guia, en el orden del texto."""
    patron = re.compile(r"<!-- generado: (?P<nombre>[a-z_]+) -->\n(?P<cuerpo>.*?)\n[ \t]*<!-- fin: (?P=nombre) -->",
                        re.DOTALL)
    return {m.group("nombre"): textwrap.dedent(m.group("cuerpo"))
            for m in patron.finditer(texto)}


# ---------------------------------------------------------------------------
# Los bloques que la suite escribe y ejecuta
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BloqueDeLaGuia:
    """Una cerca de codigo de la guia: su lenguaje, sus atributos y su cuerpo."""
    lenguaje: str
    atributos: Dict[str, str]
    cuerpo: str

    @property
    def id(self) -> Optional[str]:
        return self.atributos.get("id")

    @property
    def archivo(self) -> Optional[str]:
        return self.atributos.get("archivo")

    def comando(self) -> List[str]:
        """El comando de un bloque `sh`, con las continuaciones de linea unidas."""
        texto = " ".join(linea.rstrip("\\").strip()
                         for linea in self.cuerpo.splitlines() if linea.strip())
        return shlex.split(texto)


# Una cerca puede ir dentro de una viñeta (sangrada): la sangria se quita del
# cuerpo con `textwrap.dedent`, que es lo que Markdown hace al renderizarla.
_CERCA = re.compile(r"^[ \t]*```(?P<info>[^\n]*)\n(?P<cuerpo>.*?)^[ \t]*```[ \t]*$",
                    re.DOTALL | re.MULTILINE)


def bloques_de_la_guia(texto: str) -> List[BloqueDeLaGuia]:
    bloques = []
    for m in _CERCA.finditer(texto):
        partes = m.group("info").split()
        lenguaje = partes[0] if partes else ""
        atributos = dict(p.split("=", 1) for p in partes[1:] if "=" in p)
        cuerpo = textwrap.dedent(m.group("cuerpo")).rstrip("\n")
        bloques.append(BloqueDeLaGuia(lenguaje, atributos, cuerpo))
    return bloques


def imprimir_bloques() -> str:
    partes = []
    for nombre, cuerpo in bloques_generados().items():
        partes.append(MARCA_INICIO.format(nombre=nombre) + "\n" + cuerpo + "\n"
                      + MARCA_FIN.format(nombre=nombre))
    return "\n\n".join(partes)


if __name__ == "__main__":
    print(imprimir_bloques())
