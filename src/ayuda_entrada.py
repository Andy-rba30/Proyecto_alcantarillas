"""
ayuda_entrada.py
================
EL CONTENIDO de las tres ayudas de la ventana de ayuda: que columnas tiene que
traer el CSV de Sec. 1.2, que claves acepta el JSON de `--datos-externos`, y
--- desde G5 --- los CONCEPTOS con que el programa habla: familias, etiquetas,
estados de un criterio y el glosario del censo.

Que es esto, y por que no esta en gui/
--------------------------------------
El mismo reparto que `ventana_normativa.py`, y por las mismas dos razones:
`gui/` importa `tkinter`, que no esta en toda imagen donde corre la suite, y
lo que la ventana AFIRMA tiene que poder compararse campo a campo sin
escritorio. Aqui el contenido es un DATO; `gui/ayuda_entrada.py` lo pinta y no
sabe nada mas.

NINGUNA LISTA DE ESTAS AYUDAS ESTA ESCRITA AQUI
-----------------------------------------------
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
    las tres familias             `M1_clasificacion.PERFILES`, por `modelos.Familia`
    las cinco etiquetas           `criterios_adoptados.ETIQUETAS_VALIDAS`
    los estados de un criterio    el AST de `gui/app.py::_estado_criterio`
                                  + `Criterio.vacio_verificado`
                                  + `modelos.TipoDeVeredicto.DIFERIDO`
    el glosario                   `variables_entrada.VARIABLES` entero

LOS PARRAFOS DE LA AYUDA DE CONCEPTOS SI SON TEXTO ESCRITO A MANO, y la
distincion es deliberada y hay que conservarla al tocarlos: una LISTA (que
etiquetas existen, que estados tiene un criterio) envejece sola y por eso se
deriva; un PARRAFO explicativo en lenguaje llano es texto estable que ninguna
declaracion del codigo contiene, y se escribe aqui --- junto a una GUARDIA que
falla si la lista derivada gana o pierde una entrada sin que su parrafo la
siga (`fichas_de_etiquetas`, `fichas_de_estados`). Un parrafo sin guardia
seria una tabla paralela; una guardia sin parrafo seria una ayuda que enumera
sin explicar.

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

import ast
import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Dict, Optional, Tuple

import variables_entrada as ve
import ventana_normativa as vn
from modelos import (Familia, Libre, TipoDeVeredicto, VacioAdmitido,
                     VariableDeEntrada)
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
    # `VariableDeEntrada.nota`, QUE LA AYUDA DE S22 SE DEJABA. Existia,
    # `reporte_variables` la imprimia y dos columnas la llevan --- la de
    # `NF_profundidad_m` explica por que no viene del encabezado de Sec. 1.2, y
    # la de `sucs_fundacion` dice que se escribe en la celda ---, y aun asi no
    # llegaba a la pantalla. Una ayuda derivada que descarta un campo de su
    # fuente es una ayuda derivada a medias.
    nota: str = ""

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
        nota=v.nota,
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


# ===========================================================================
# La ayuda de conceptos (G5): familias, etiquetas, estados y glosario
# ===========================================================================

# ---------------------------------------------------------------------------
# 1. Las tres familias
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FichaDeFamilia:
    """
    Una familia de Sec. 2.3 con lo que su perfil declara: como se llama y de
    donde sale su caudal. Todo sale de `M1_clasificacion.PERFILES`, que es la
    unica huella en el codigo de esa seccion de la hoja de ruta.
    """

    familia: Familia
    nombre: str
    origen_del_caudal: str
    numeral: str
    notas: Tuple[str, ...] = ()

    @property
    def rotulo(self) -> str:
        return f"Familia {self.familia.value} - {self.nombre}"


def fichas_de_familias() -> Tuple[FichaDeFamilia, ...]:
    """
    Las familias EN EL ORDEN DEL ENUM `modelos.Familia`, cada una con su
    perfil de `M1_clasificacion.PERFILES`.

    Se recorre el ENUM y no el dict, y esa eleccion es la guardia: una familia
    nueva sin perfil detiene la ayuda con KeyError en vez de omitirse --- que
    es como una lista escrita a mano se quedaria callada. `M1_clasificacion`
    se importa dentro de la funcion por la misma razon que `cli` mas arriba:
    la GUI y los tests de contenido no tienen por que arrastrar un modulo de
    calculo para pintar tres rotulos.
    """
    from modulos import M1_clasificacion as m1

    fichas = []
    for familia in Familia:
        if familia not in m1.PERFILES:
            raise KeyError(
                f"la Familia {familia.value} no tiene perfil en "
                "M1_clasificacion.PERFILES: la ayuda de conceptos no la puede "
                "describir sin inventarla. Declarar el perfil primero.")
        perfil = m1.PERFILES[familia]
        fichas.append(FichaDeFamilia(
            familia=familia, nombre=perfil.nombre,
            origen_del_caudal=perfil.origen_del_caudal,
            numeral=perfil.numeral, notas=perfil.notas))
    return tuple(fichas)


# ---------------------------------------------------------------------------
# 2. Las cinco etiquetas
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FichaDeEtiqueta:
    """Una etiqueta de la taxonomia, con su parrafo llano y donde vive."""

    etiqueta: str
    nombre: str
    explicacion: str
    archivo: str

    @property
    def rotulo(self) -> str:
        return f"[{self.etiqueta}]"


# LOS PARRAFOS SON TEXTO ESTABLE ESCRITO A MANO, declarado asi a proposito
# (ver el docstring del modulo): ninguna declaracion del codigo contiene la
# explicacion llana de una etiqueta, de modo que no hay de donde derivarla.
# Lo que SI se deriva es la LISTA: `fichas_de_etiquetas` recorre
# `criterios_adoptados.ETIQUETAS_VALIDAS` y falla si a una etiqueta le falta
# su fila aqui, o si aqui sobra una fila que la taxonomia ya no tiene.
# El `archivo` de cada fila es el de la regla de arquitectura de CLAUDE.md
# (que literal vive donde), y un test comprueba que cada uno exista en src/.
_EXPLICACIONES_DE_ETIQUETAS: Dict[str, Tuple[str, str, str]] = {
    "N": ("Exigencia normativa",
          "Lo exige una norma peruana vigente, con numeral verificado: el "
          "mismo numero en cualquier obra del pais. Nadie lo eligio.",
          "constantes_normativas.py"),
    "N->": ("Valor normativo por analogia",
            "El numero es de una norma, pero aplicado a un caso que esa norma "
            "no cubre. La analogia se declara expresamente: sin declaracion, "
            "pareceria una exigencia directa y no lo es.",
            "criterios_adoptados.py"),
    "S": ("Dato de sitio",
          "Un hecho de ESTE lugar, leido con un procedimiento real (mapa, "
          "ensayo, medicion). Cambia al mover la obra de sitio, no al cambiar "
          "de proyectista; se defiende con la trazabilidad de la lectura, no "
          "con un rango.",
          "datos_sitio.py"),
    "C": ("Vacio cubierto con fuente tecnica",
          "La norma peruana calla y el valor sale de una fuente tecnica "
          "reconocida (FHWA, AASHTO), citada.",
          "criterios_adoptados.py"),
    "A": ("Adopcion del proyectista",
          "Sin norma ni fuente unica: alguien ELIGIO este valor y lo declara, "
          "con su rango de sensibilidad. Es la unica etiqueta que se defiende "
          "mostrando cuanto cambiaria el resultado con otro valor.",
          "criterios_adoptados.py"),
}


def fichas_de_etiquetas() -> Tuple[FichaDeEtiqueta, ...]:
    """
    Las etiquetas EN EL ORDEN DE `criterios_adoptados.ETIQUETAS_VALIDAS`, que
    es la declaracion que la guardia de los criterios aplica de verdad.

    LA GUARDIA VA EN LAS DOS DIRECCIONES: una etiqueta nueva sin parrafo
    detiene la ayuda (no se enumera sin explicar), y un parrafo cuya etiqueta
    ya no existe tambien (una fila muerta aqui es la tabla paralela que este
    archivo se prohibe).
    """
    import criterios_adoptados as ca

    sobrantes = set(_EXPLICACIONES_DE_ETIQUETAS) - set(ca.ETIQUETAS_VALIDAS)
    if sobrantes:
        raise KeyError(
            "la ayuda de conceptos explica etiquetas que la taxonomia ya no "
            f"tiene: {sorted(sobrantes)}. Retirar sus filas de "
            "_EXPLICACIONES_DE_ETIQUETAS.")
    fichas = []
    for etiqueta in ca.ETIQUETAS_VALIDAS:
        if etiqueta not in _EXPLICACIONES_DE_ETIQUETAS:
            raise KeyError(
                f"la etiqueta '{etiqueta}' entro en ETIQUETAS_VALIDAS y no "
                "tiene fila en _EXPLICACIONES_DE_ETIQUETAS: escribir su "
                "parrafo llano y su archivo de residencia antes de que la "
                "ayuda la muestre.")
        nombre, explicacion, archivo = _EXPLICACIONES_DE_ETIQUETAS[etiqueta]
        fichas.append(FichaDeEtiqueta(etiqueta=etiqueta, nombre=nombre,
                                      explicacion=explicacion,
                                      archivo=archivo))
    return tuple(fichas)


# ---------------------------------------------------------------------------
# 3. Los estados de un criterio
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FichaDeEstado:
    """Un estado con su rotulo tal como la pestana 2 lo pinta, y su parrafo."""

    tag: str
    rotulo: str
    explicacion: str
    origen: str


# El archivo donde viven los cuatro estados de la tabla de criterios. Se
# PARSEA su arbol y no se importa, por dos razones que ya estan pagadas en
# este repositorio: `gui/` arrastra tkinter, que no esta en toda imagen donde
# corre la suite, y el precedente de leer el AST en vez de duplicar la lista
# es `variables_entrada._consumo_por_modulo`.
_RUTA_GUI_APP = Path(__file__).resolve().parent.parent / "gui" / "app.py"

# Igual que los parrafos de las etiquetas: texto estable escrito a mano,
# guardado por `fichas_de_estados` en las dos direcciones contra la lista
# derivada del AST de `gui/app.py::_estado_criterio`.
_EXPLICACIONES_DE_ESTADOS: Dict[str, str] = {
    "pendiente": (
        "El criterio no tiene valor y nadie lo declaro en esta corrida. Si "
        "una etapa lo invoca, esa etapa se detiene y aparece como bloqueo en "
        "la pestana 4; declararlo (en la pestana 2) lo destraba."),
    "declarado_corrida": (
        "El archivo lo tiene vacio y se le dio un valor SOLO para esta "
        "corrida: rellena el vacio sin tocar el expediente, y se pierde al "
        "cerrar el programa. Escribirlo en el archivo es una accion aparte."),
    "pisado_corrida": (
        "El archivo YA tiene un valor y esta corrida usa otro por encima. No "
        "es lo mismo que declarar sobre un vacio: el expediente sigue "
        "diciendo otra cosa, y por eso la tabla lo marca distinto."),
    "resuelto": (
        "El valor esta transcrito en criterios_adoptados.py, con su "
        "etiqueta, su fuente y su justificacion. Es el unico estado que "
        "sobrevive a cerrar el programa."),
}

_EXPLICACION_VACIO_VERIFICADO = (
    "No es un estado de la tabla sino una marca del criterio: el vacio que "
    "este valor cubre SE BUSCO fuente por fuente y quedo registrado (el "
    "campo lleva el ancla al registro). Distingue el hueco que nadie busco "
    "del hueco agotado, que es el unico defendible en una memoria.")

_EXPLICACION_DIFERIDO = (
    "Estado de una VERIFICACION, no de un criterio: existe, tiene umbral, y "
    "el alcance de la corrida la dejo fuera (a --alcance perfil se difieren "
    "las etapas de expediente). Imprimirla como cumple o no cumple seria "
    "mentir; se imprime diferida, con su motivo.")


def _estados_de_la_tabla(ruta_gui=None) -> Tuple[Tuple[str, str], ...]:
    """
    Los pares (tag, rotulo) de la tabla de criterios, leidos del arbol de
    `gui/app.py`: los tags y su orden salen de `FILTROS_DE_ESTADO`, y el
    rotulo de cada uno del `return` de `_estado_criterio` que lo devuelve.

    Las dos declaraciones prometen ser la misma (el comentario de
    `FILTROS_DE_ESTADO` lo dice con palabras); aqui esa promesa se EXIGE: un
    tag que este en una y no en la otra detiene la ayuda en vez de mostrarse
    a medias.
    """
    arbol = ast.parse(Path(ruta_gui or _RUTA_GUI_APP).read_text(
        encoding="utf-8"))

    filtros = None
    rotulos: Dict[str, str] = {}
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "FILTROS_DE_ESTADO"
                for t in nodo.targets):
            filtros = ast.literal_eval(nodo.value)
        if isinstance(nodo, ast.FunctionDef) and nodo.name == "_estado_criterio":
            for r in ast.walk(nodo):
                if isinstance(r, ast.Return):
                    rotulo, tag = ast.literal_eval(r.value)
                    rotulos[tag] = rotulo
    if filtros is None or not rotulos:
        raise KeyError(
            "gui/app.py ya no declara FILTROS_DE_ESTADO o _estado_criterio: "
            "la ayuda de conceptos no tiene de donde derivar los estados.")

    tags_filtro = [tag for _rotulo, tag in filtros if tag is not None]
    if set(tags_filtro) != set(rotulos):
        raise KeyError(
            "FILTROS_DE_ESTADO y _estado_criterio dejaron de declarar los "
            f"mismos estados: filtro={sorted(tags_filtro)}, "
            f"retornos={sorted(rotulos)}. Son la misma lista o la tabla y su "
            "filtro dicen cosas distintas de la misma fila.")
    return tuple((tag, rotulos[tag]) for tag in tags_filtro)


def fichas_de_estados(ruta_gui=None) -> Tuple[FichaDeEstado, ...]:
    """
    Los estados de un criterio: primero los de la tabla de la pestana 2 (en
    el orden de su filtro), y despues los dos conceptos del pipeline que se
    les parecen y no son estados de la tabla --- el vacio verificado y el
    diferido ---, cada uno anclado al simbolo del que sale, de modo que si el
    simbolo desaparece la fila no se puede construir.
    """
    import criterios_adoptados as ca

    derivados = _estados_de_la_tabla(ruta_gui)
    tags = {tag for tag, _rotulo in derivados}
    sobrantes = set(_EXPLICACIONES_DE_ESTADOS) - tags
    if sobrantes:
        raise KeyError(
            "la ayuda de conceptos explica estados que la tabla de criterios "
            f"ya no tiene: {sorted(sobrantes)}. Retirar sus filas de "
            "_EXPLICACIONES_DE_ESTADOS.")
    fichas = []
    for tag, rotulo in derivados:
        if tag not in _EXPLICACIONES_DE_ESTADOS:
            raise KeyError(
                f"el estado '{tag}' aparecio en gui/app.py y no tiene fila "
                "en _EXPLICACIONES_DE_ESTADOS: escribir su parrafo llano "
                "antes de que la ayuda lo muestre.")
        fichas.append(FichaDeEstado(
            tag=tag, rotulo=rotulo,
            explicacion=_EXPLICACIONES_DE_ESTADOS[tag],
            origen="gui/app.py::_estado_criterio"))

    if "vacio_verificado" not in {f.name for f in fields(ca.Criterio)}:
        raise KeyError(
            "Criterio.vacio_verificado ya no existe: retirar su fila de la "
            "ayuda de conceptos en vez de mostrar un concepto muerto.")
    fichas.append(FichaDeEstado(
        tag="vacio_verificado", rotulo="vacio verificado",
        explicacion=_EXPLICACION_VACIO_VERIFICADO,
        origen="criterios_adoptados.Criterio.vacio_verificado"))

    fichas.append(FichaDeEstado(
        tag=TipoDeVeredicto.DIFERIDO.value,
        rotulo=TipoDeVeredicto.DIFERIDO.value,
        explicacion=_EXPLICACION_DIFERIDO,
        origen="modelos.TipoDeVeredicto.DIFERIDO"))
    return tuple(fichas)


# ---------------------------------------------------------------------------
# 4. El glosario de simbolos y unidades
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FichaDeGlosario:
    """Una variable del censo, con lo que un lector nuevo necesita ubicarla."""

    clave: str
    concepto: str
    unidad: str
    fase: str
    poblacion: str


# El rotulo llano de cada poblacion del censo. La LISTA de poblaciones es el
# enum `modelos.Poblacion`; estos tres rotulos son presentacion (el valor del
# enum, 'columna_csv', no es una frase) y la guardia de `fichas_de_glosario`
# exige que ningun miembro del enum se quede sin rotulo.
_ROTULOS_DE_POBLACION: Dict[str, str] = {
    "columna_csv": "columna del CSV",
    "dato_sitio": "dato de sitio",
    "criterio": "criterio adoptado",
}


def fichas_de_glosario() -> Tuple[FichaDeGlosario, ...]:
    """
    Las variables del censo ENTERO, en orden alfabetico de clave.

    Alfabetico y no por fase, al reves que las columnas del CSV: un glosario
    se consulta buscando un nombre que se acaba de leer, no llenando un
    archivo de izquierda a derecha. La fase va en la ficha para quien quiera
    el otro orden.
    """
    fichas = []
    for clave in sorted(ve.VARIABLES, key=str.lower):
        v = ve.variable(clave)
        poblacion = v.poblacion.value
        if poblacion not in _ROTULOS_DE_POBLACION:
            raise KeyError(
                f"la poblacion '{poblacion}' del censo no tiene rotulo llano "
                "en _ROTULOS_DE_POBLACION: escribirlo antes de que el "
                "glosario la muestre.")
        fichas.append(FichaDeGlosario(
            clave=clave, concepto=v.concepto, unidad=v.unidad, fase=v.fase,
            poblacion=_ROTULOS_DE_POBLACION[poblacion]))
    return tuple(fichas)
