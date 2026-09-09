"""
ayuda_entrada.py
================
EL CONTENIDO de las dos ayudas de la pestana 1: que columnas tiene que traer
el CSV de Sec. 1.2, y que claves acepta el JSON de `--datos-externos`.

Que es esto, y por que no esta en gui/
--------------------------------------
El mismo reparto que `ventana_normativa.py`, y por las mismas dos razones:
`gui/` importa `tkinter`, que no esta en toda imagen donde corre la suite, y
lo que la ventana AFIRMA tiene que poder compararse campo a campo sin
escritorio. Aqui el contenido es un DATO; `gui/ayuda_entrada.py` lo pinta y no
sabe nada mas.

NINGUNA LINEA DE ESTAS DOS AYUDAS ESTA ESCRITA AQUI
---------------------------------------------------
Es la regla entera de este archivo, y no es celo: una tabla de columnas
escrita a mano envejece EN SILENCIO en cuanto alguien anade una columna a
`PuntoCritico`, y entonces la ayuda que el proyectista lee antes de llenar su
archivo es la que miente. Todo sale de donde ya vive:

    el encabezado y su orden      `M0_carga.COLUMNAS`, derivado de PuntoCritico
    concepto, unidad, resolucion  `variables_entrada.VARIABLES`
    de donde sale el dato         `variables_entrada.como_se_lee`
    el limite fisico de la celda  `ventana_normativa.dominio_mostrado`
    que puede ir vacio, y en que
      familia, y quien lo debe    `M0_carga.VACIOS_ADMITIDOS`
    las claves del JSON           `cli.CLAVES_EXTERNAS`
    que familias usan cada clave  `cli.FAMILIAS_QUE_USAN`

`tests/test_ayuda_entrada.py` lo comprueba de la unica forma que sirve: no
comparando textos, sino AÑADIENDO una columna al censo y viendo que la ayuda
la recoge sola.

Las dos ayudas no son la misma, y la segunda es mas pobre a proposito
---------------------------------------------------------------------
La del CSV esta completa: las 19 columnas tienen concepto, unidad y
`resolucion` en el censo, porque las columnas son una de sus tres poblaciones.

La del JSON no puede estarlo, y conviene decir por que en vez de disimularlo:
de las OCHO claves de `cli.CLAVES_EXTERNAS`, solo DOS --- `Q_m3s` y `S_cauce`
--- estan en el censo, porque son ademas columnas del CSV. Las otras seis
(`luz_m`, `TW_m`, `longitud_m`, `S_conducto`, `L_hidraulico_m`,
`categoria_tr`) no son columna, ni dato de sitio, ni criterio: no pertenecen a
ninguna de las tres poblaciones, y su documentacion vive en PROSA, en el
docstring de `cli.py`.

Esa prosa NO se parsea. Un docstring no es una interfaz: se reformatea sin que
nada avise, y una ayuda que lo lea se rompe callada --- que es exactamente el
defecto que este archivo existe para no cometer. De las seis se da lo que SI
es dato (el nombre exacto de la clave, y que familias la usan) y se dice donde
esta lo demas. La ayuda queda a medias y lo declara; el arreglo de fondo no es
parsear prosa, es que esas seis entren en el censo.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Tuple

import variables_entrada as ve
import ventana_normativa as vn
from modelos import Familia, Libre, VacioAdmitido, VariableDeEntrada
# POR EL MODULO Y NO POR EL VALOR (`from ... import COLUMNAS`), y no es
# estilo: un `from` copia la tupla en este espacio de nombres al importar, y
# entonces la ayuda deja de leer la declaracion y pasa a leer una foto suya.
# Que la foto no se pueda mover es justo lo que hace indetectable el defecto
# que este archivo existe para evitar --- y ademas impide comprobarlo:
# `tests/test_ayuda_entrada.py` AÑADE una columna al censo y mira si la
# ayuda la recoge, y con la foto ese test seria imposible de escribir.
from modulos import M0_carga as m0

# El separador del CSV. No es un valor de proyecto: es el formato del archivo
# que `csv.DictReader` lee con su dialecto por defecto.
SEPARADOR_CSV = ","

# Lo que se escribe en la celda de un ejemplo para decir «aqui va tu dato».
# Un ejemplo con numeros de verdad seria peor: alguien lo pegaria tal cual.
MARCA_DE_HUECO = "..."


# ===========================================================================
# La ayuda del CSV
# ===========================================================================

@dataclass(frozen=True)
class FichaDeColumna:
    """Una columna del encabezado de Sec. 1.2, con todo lo que hay que saber."""

    clave: str
    concepto: str
    unidad: str
    de_donde_sale: str
    # Los grupos de `M0_carga.VACIOS_ADMITIDOS` que admiten vacia esta celda.
    # Vacio = la columna es obligatoria en las tres familias.
    vacios: Tuple[VacioAdmitido, ...] = ()
    # Lo que la `resolucion` dice del rango admisible de la celda, en palabras
    # de quien la declaro. Solo lo tienen las `Libre`: un `de_ensayo` no acota
    # un rango, exige una trazabilidad, y esa ya va en `de_donde_sale`.
    dominio_declarado: str = ""
    # El limite de `dominios.py`, por NOMBRE y con su valor. Se pide a
    # `ventana_normativa.dominio_mostrado`, que es la misma funcion que usa la
    # ventana emergente: un dominio pintado de dos formas distintas en dos
    # pantallas del mismo programa es un dominio en el que no se puede confiar.
    limite_fisico: Optional[vn.RangoMostrado] = None

    @property
    def obligatoria(self) -> bool:
        """Si la celda NO puede ir vacia en ninguna familia."""
        return not self.vacios

    @property
    def familias_que_admiten_vacio(self) -> Tuple[Familia, ...]:
        """
        Las familias en las que la celda puede ir vacia.

        Las tres cuando algun grupo no declara familias: ese es el significado
        de `VacioAdmitido.familias` vacio, y traducirlo aqui es lo que permite
        que la ayuda diga «en Familia C» en vez de «a veces».
        """
        familias: list = []
        for vacio in self.vacios:
            for familia in (vacio.familias or tuple(Familia)):
                if familia not in familias:
                    familias.append(familia)
        return tuple(f for f in Familia if f in familias)

    def resumen_de_obligatoriedad(self) -> str:
        """La celda de la columna «obligatoria», en una linea."""
        if self.obligatoria:
            return "SI, en las tres familias"
        familias = self.familias_que_admiten_vacio
        if len(familias) == len(tuple(Familia)):
            return "puede ir vacia"
        cuales = ", ".join(f"Familia {f.value}" for f in familias)
        return f"puede ir vacia solo en {cuales}"


def _dominio_declarado(v: VariableDeEntrada) -> str:
    r = v.resolucion
    return r.dominio if isinstance(r, Libre) else ""


def _vacios_de(clave: str) -> Tuple[VacioAdmitido, ...]:
    return tuple(vacio for vacio in m0.VACIOS_ADMITIDOS
                 if clave in vacio.columnas)


def ficha_de_columna(clave: str) -> FichaDeColumna:
    """La ficha de UNA columna del encabezado, armada de sus cuatro fuentes."""
    if clave not in m0.COLUMNAS:
        raise KeyError(
            f"'{clave}' no es columna del encabezado de Sec. 1.2. Las "
            f"{len(m0.COLUMNAS)} son: " + ", ".join(m0.COLUMNAS))
    v = ve.variable(clave)
    return FichaDeColumna(
        clave=clave,
        concepto=v.concepto,
        unidad=v.unidad,
        de_donde_sale=ve.como_se_lee(v),
        vacios=_vacios_de(clave),
        dominio_declarado=_dominio_declarado(v),
        limite_fisico=vn.dominio_mostrado(v.dominio),
    )


def fichas_de_columnas() -> Tuple[FichaDeColumna, ...]:
    """
    Las 19 columnas EN EL ORDEN DEL ENCABEZADO, que es el que el CSV tiene que
    traer. El orden sale de `COLUMNAS`, que sale de los campos de
    `PuntoCritico`: ordenarlas aqui por otro criterio --- alfabetico, por
    ejemplo --- daria una ayuda que no se puede seguir de izquierda a derecha
    mientras se mira el archivo.
    """
    return tuple(ficha_de_columna(c) for c in m0.COLUMNAS)


def cabecera_csv() -> str:
    """
    La primera linea del CSV, exacta y copiable.

    Es lo que se pega en una hoja vacia para empezar. Sale de `COLUMNAS`, de
    modo que una columna nueva aparece aqui sola --- que es justo lo que una
    cabecera transcrita a mano no hace.
    """
    return SEPARADOR_CSV.join(m0.COLUMNAS)


def fila_de_ejemplo() -> str:
    """
    Una fila de huecos, con tantas celdas como columnas.

    Va debajo de la cabecera para que se vea CUANTAS comas lleva la fila, que
    es el error de formato que `_punto_desde_fila` reporta como «la fila trae
    mas celdas que columnas el encabezado». No lleva numeros a proposito: un
    ejemplo con datos plausibles acaba pegado en un expediente.
    """
    return SEPARADOR_CSV.join(MARCA_DE_HUECO for _ in m0.COLUMNAS)


def vacios_por_quien_lo_debe() -> Tuple[Tuple[str, Tuple[str, ...], Tuple[Familia, ...]], ...]:
    """
    Los grupos de celdas que pueden ir vacias, agrupados por QUIEN DEBE el dato.

    Es la mitad de la ayuda que la lista de columnas no da: leyendo fila por
    fila se ve que `Q_m3s` puede ir vacia, y no se ve que las tres columnas de
    un cruce de canal las debe el mismo tablero y llegan juntas.
    """
    return tuple((vacio.quien_lo_debe, tuple(vacio.columnas),
                  vacio.familias or tuple(Familia))
                 for vacio in m0.VACIOS_ADMITIDOS)


# ===========================================================================
# La ayuda del JSON de datos externos
# ===========================================================================

@dataclass(frozen=True)
class FichaDeClaveExterna:
    """
    Una clave de `cli.CLAVES_EXTERNAS`, con lo que de ella se puede DERIVAR.

    `en_el_censo` es False para las seis que no son columna, ni dato de sitio,
    ni criterio. Para esas, `concepto`, `unidad` y `de_donde_sale` van vacios y
    la ventana lo dice: prefiere un hueco declarado a una frase inventada o
    sacada de un docstring que puede reformatearse manana.
    """

    clave: str
    familias: Tuple[Familia, ...]
    en_el_censo: bool
    concepto: str = ""
    unidad: str = ""
    de_donde_sale: str = ""

    @property
    def resumen_de_familias(self) -> str:
        if len(self.familias) == len(tuple(Familia)):
            return "las tres familias"
        return ", ".join(f"Familia {f.value}" for f in self.familias)


def fichas_de_datos_externos() -> Tuple[FichaDeClaveExterna, ...]:
    """
    Las ocho claves del JSON, en el orden en que `cli` las declara.

    Se importa `cli` DENTRO de la funcion y no arriba: `cli` importa los once
    modulos de calculo y este modulo lo importan la GUI y los tests de
    contenido, que no tienen por que arrastrar el pipeline entero para pintar
    una lista de ocho nombres.
    """
    import cli

    fichas = []
    for clave in cli.CLAVES_EXTERNAS:
        familias = cli.familias_que_usan(clave)
        if clave in ve.VARIABLES:
            v = ve.variable(clave)
            fichas.append(FichaDeClaveExterna(
                clave=clave, familias=familias, en_el_censo=True,
                concepto=v.concepto, unidad=v.unidad,
                de_donde_sale=ve.como_se_lee(v)))
        else:
            fichas.append(FichaDeClaveExterna(
                clave=clave, familias=familias, en_el_censo=False))
    return tuple(fichas)


# El id de ejemplo del esqueleto. Va entre angulos para que se vea que hay que
# sustituirlo; si alguien lo deja tal cual, la corrida no se rompe --- lo avisa
# `cli._avisar_ids_desconocidos`, que es exactamente lo que tiene que pasar.
ID_DE_EJEMPLO = "<id del CSV>"


def esqueleto_json() -> str:
    """
    La FORMA del archivo: las dos secciones y donde va el id del punto.

    LAS OCHO CLAVES NO VAN DENTRO, y el primer intento si las metia --- con
    `null` de valor, que parecia el «no declarado» natural ---. No lo es:
    `cli._dato_externo` exige un numero (o la cadena de `categoria_tr`), de
    modo que aquel esqueleto no se podia pegar y correr, que es lo unico que
    un esqueleto tiene que saber hacer. Las claves se leen de la tabla de
    arriba, que para eso esta, y aqui queda la forma que SI carga.

    Las dos secciones son opcionales y van vacias a proposito: pegado tal
    cual, el archivo es valido y no declara nada. `tests/test_ayuda_entrada.py`
    lo comprueba pasandoselo a `cargar_datos_externos`, que es la unica forma
    de que esta promesa no se rompa en silencio.
    """
    return json.dumps({"globales": {}, "puntos": {ID_DE_EJEMPLO: {}}},
                      indent=2, ensure_ascii=False)


def claves_admitidas() -> str:
    """Las ocho claves en una linea, para la ayuda y para el mensaje de error."""
    import cli

    return ", ".join(cli.CLAVES_EXTERNAS)
