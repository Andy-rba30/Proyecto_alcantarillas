# -*- coding: utf-8 -*-
"""
editores.py
===========
EL CONTENIDO de los editores tipados de la pestaña 2 (E-B, E10): que campos
tiene el editor de cada criterio, de que tipo, con que ventana, que filas de
la tabla se ofrecen y que valor propone cada una, como se ARMA el valor
entero desde los campos y como se DESCOMPONE para pintarlo, y por que puerta
de `declaracion.py` entra. Todo derivado de la ficha (`Criterio.forma` de
EXT-5, `sensibilidad`, `campos_obligatorios`, `resolucion`) y del registro
normativo; nada escrito aqui a mano.

Por que esta en src/ y no en gui/
---------------------------------
El mismo reparto que `anticipo.py`, `ayuda_entrada.py` y `traza_punto.py`:
`gui/` importa `tkinter`, que no esta en toda imagen donde corre la suite, y
lo que un editor AFIRMA --- que `seccion_receptor` tiene cinco campos y que
`n` se mueve entre 0.025 y 0.035; que elegir la fila
`concreto_headwall_square_edge` de la Tabla C.2 pone 0.5 --- tiene que
poder comprobarse sin escritorio. `gui/editores.py` pinta esto sobre
`CampoValidable` y no sabe nada mas.

Las tres reglas del prompt, y donde vive cada una
-------------------------------------------------
1. **Una seleccion normativa OBTIENE el valor de la tabla.** Cada
   `OpcionDeTabla` trae `valor_propuesto`: la celda de la fila que el calculo
   usa cuando el criterio declara un numero (o un par), y la CLAVE de la fila
   cuando declara un texto. Es lo mismo que `declaracion.valor_propuesto`
   propone en la ventana emergente, leido de las columnas que el registro
   marca como usadas.
2. **Una adopcion distinta EXIGE procedencia.** `declarar` enruta por el
   modo de resolucion a la puerta que corresponde de `declaracion.py`: con
   fila, `declarar_desde_tabla` (que rechaza sin `nota` un numero que
   DIFIERE de la celda, EXT-V-02); sin fila, en un criterio que se lee de una
   tabla, hace falta la nota, o no entra. Teclear la CLAVE de una fila es
   elegir esa fila (`fila_implicita`), que es el camino del raton de EXT-5;
   un numero que coincide con VARIAS celdas no nombra ninguna --- adivinar
   la fila seria inventar la procedencia.
3. **Aplicar es ATOMICO.** El valor se arma ENTERO (`armar_valor`), pasa la
   MISMA guardia que el archivo en seco (`verificar`, que es
   `ca.verificar_declaracion`) y entra por una sola llamada a `declaracion`,
   que a su vez verifica antes de escribir y registra la procedencia solo
   despues. Si un campo falla, no entra nada: ni el valor ni la procedencia.

Lo que NO inventa: un dict cuyos campos no se pueden derivar de la ficha
--- un dict de dicts como `cobertura_minima_aashto`, o uno vacio sin
ventana ni campos obligatorios --- cae al editor LITERAL (el campo de texto
de siempre, con el mismo parser) en vez de recibir campos que la ficha no
declara.
"""

from __future__ import annotations

import math
import numbers
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src import criterios_adoptados as _ca
from src import declaracion as _dec
from src import variables_entrada as _ve
from src import ventana_normativa as _vn
from src.declaracion import Estado, ResultadoValidacion
from src.modelos import DeCatalogo, DeEnsayo, Derivada, DeTabla, EnRango, Libre
from src.normativa import registro as _registro
from src.tolerancias import TOL_UMBRAL_NORMATIVO

# Los seis editores. `LITERAL` es el campo de texto de siempre: el editor
# «sin campos» para lo que la ficha no permite descomponer.
ESCALAR = "escalar"
PAR = "par"
SERIE_DE_PARES = "serie_de_pares"
DICT = "dict"
SERIE_DE_CLAVES = "serie_de_claves"
LITERAL = "literal"
TIPOS_DE_EDITOR = (ESCALAR, PAR, SERIE_DE_PARES, DICT, SERIE_DE_CLAVES, LITERAL)

# Los tipos de un CAMPO del editor. `libre` es «lo que el parser devuelva»
# (numero o texto): la union `k_v` y los campos de un dict sin ventana.
TIPO_ENTERO = _ca.FORMA_INT
TIPO_REAL = _ca.FORMA_FLOAT
TIPO_TEXTO = _ca.FORMA_STR
TIPO_CATEGORIA = _ca.FORMA_CATEGORIA
TIPO_LIBRE = "libre"

# Los nombres de los campos de un par y de una serie de pares: la ficha
# declara «(minimo, maximo)» para el par (regla de doble n, Sec. 4.1) y no
# nombra las dos columnas de la serie --- su `dominio` las describe ---.
CAMPOS_DEL_PAR = ("minimo", "maximo")
CAMPOS_DE_LA_SERIE = ("primero", "segundo")
CAMPO_UNICO = "valor"
CAMPO_CLAVES = "claves"


@dataclass(frozen=True)
class CampoDelEditor:
    """Un campo: nombre, tipo, ventana (si la ficha la da) y opciones (si es cerrado)."""
    nombre: str
    tipo: str
    rango: Optional[Tuple[float, float]] = None
    opciones: Tuple[str, ...] = ()
    obligatorio: bool = True
    ayuda: str = ""


@dataclass(frozen=True)
class OpcionDeTabla:
    """Una fila de la tabla, con lo que PROPONE al elegirla."""
    fila: str                       # la clave corta, que es lo que `declaracion` acepta
    etiqueta: str
    valor_propuesto: Any            # celda (o par de celdas), clave de la fila, o None
    celdas: str                     # las celdas escritas, para leer la fila
    elegible: bool
    motivo: str = ""


@dataclass(frozen=True)
class EsquemaDeEditor:
    clave: str
    forma: Tuple[str, ...]
    tipo_de_editor: str
    campos: Tuple[CampoDelEditor, ...]
    modo: str
    editable: bool
    motivo_no_editable: str = ""
    tabla_id: str = ""
    opciones_de_tabla: Tuple[OpcionDeTabla, ...] = ()
    exige_fila: bool = False
    dominio: str = ""
    valor_actual: Any = None

    def campo(self, nombre: str) -> CampoDelEditor:
        for c in self.campos:
            if c.nombre == nombre:
                return c
        raise KeyError(f"el editor de '{self.clave}' no tiene el campo «{nombre}»")


# ===========================================================================
# El esquema, derivado de la ficha
# ===========================================================================

def _es_real(x: Any) -> bool:
    return isinstance(x, numbers.Real) and not isinstance(x, bool)


def _formas_de(c: Any) -> Tuple[str, ...]:
    return c.forma if isinstance(c.forma, tuple) else (c.forma,)


def _rango_de(c: Any) -> Optional[Tuple[float, float]]:
    rango = _ca._rango_numerico(c.sensibilidad)
    if rango is None or len(rango) != 2:
        return None
    return (rango[0], rango[1])


def _opciones_cerradas(c: Any) -> Tuple[str, ...]:
    s = c.sensibilidad
    if isinstance(s, tuple) and s and all(isinstance(x, str) for x in s):
        return tuple(s)
    return ()


def _dominio_de(r: Any) -> str:
    if isinstance(r, Libre):
        return r.dominio
    if isinstance(r, (DeTabla, DeCatalogo)):
        return r.que_elige
    if isinstance(r, EnRango):
        return r.que_acota
    if isinstance(r, DeEnsayo):
        return f"{r.ensayo} · {r.trazabilidad_exigida}"
    if isinstance(r, Derivada):
        return r.regla
    return ""


def _celdas_usadas(contenido: _vn.ContenidoDeTabla, fila: _vn.FilaMostrada) -> List[Any]:
    """
    Los valores CRUDOS de la fila en las columnas que el calculo usa (no
    atenuadas y con `usada_por`), que son reales. Es la lectura de
    `declaracion._celda_escalar` extendida al par: una celda numerica es un
    escalar; dos, un par (minimo, maximo).
    """
    tabla = _registro.construir().tabla(contenido.tabla_id)
    valores = tabla.fila(fila.id).valores
    salida = []
    for columna in contenido.columnas:
        if columna.atenuada or not columna.usada_por:
            continue
        x = valores.get(columna.id)
        if _es_real(x):
            salida.append(x)
    return salida


def _opciones_de_tabla(clave: str, r: DeTabla, tipo_de_editor: str,
                       formas: Tuple[str, ...]) -> Tuple[str, Tuple[OpcionDeTabla, ...]]:
    contenido = _vn.contenido_de_tabla(r.tablas[0], clave)
    numerico = tipo_de_editor in (ESCALAR, PAR) and not (
        {TIPO_TEXTO, TIPO_CATEGORIA} & set(formas))
    opciones = []
    for f in contenido.filas:
        if numerico:
            celdas = _celdas_usadas(contenido, f)
            if tipo_de_editor == ESCALAR and len(celdas) == 1:
                propuesto: Any = float(celdas[0])
            elif tipo_de_editor == PAR and len(celdas) == 2:
                propuesto = (float(celdas[0]), float(celdas[1]))
            else:
                propuesto = None
        elif tipo_de_editor in (DICT, LITERAL):
            propuesto = None
        else:
            propuesto = f.clave_corta
        opciones.append(OpcionDeTabla(
            fila=f.clave_corta, etiqueta=f.etiqueta_legible, valor_propuesto=propuesto,
            celdas=" / ".join(f"{k}={v}" for k, v in f.celdas.items()),
            elegible=f.elegible,
            motivo="" if f.elegible else _dec._motivo_de(f.disponibilidad)))
    return contenido.tabla_id, tuple(opciones)


def _campos_del_dict(c: Any) -> Tuple[CampoDelEditor, ...]:
    """
    Los campos de un `dict_con_campos`, en este orden de preferencia y SIN
    inventar: la ventana por campo (`sensibilidad` dict), los campos
    obligatorios de la ficha, o las claves de un valor del archivo cuyos
    valores sean escalares. Un dict de dicts, o uno sin ninguna de las tres,
    no tiene campos derivables: `()`, y el editor es el literal.
    """
    s = c.sensibilidad
    if isinstance(s, dict):
        return tuple(CampoDelEditor(nombre=str(k), tipo=TIPO_REAL,
                                    rango=(float(v[0]), float(v[1])))
                     for k, v in s.items())
    if c.campos_obligatorios:
        cerradas = _opciones_cerradas(c)
        campos = []
        for nombre in c.campos_obligatorios:
            if nombre == "opcion" and cerradas:
                campos.append(CampoDelEditor(nombre, TIPO_CATEGORIA, opciones=cerradas))
            else:
                campos.append(CampoDelEditor(nombre, TIPO_TEXTO))
        return tuple(campos)
    if isinstance(c.valor, dict) and c.valor and not any(
            isinstance(v, (dict, list, tuple)) for v in c.valor.values()):
        campos = []
        for k, v in c.valor.items():
            if isinstance(v, bool) or not isinstance(v, (int, float, str)):
                tipo = TIPO_LIBRE
            elif isinstance(v, int):
                tipo = TIPO_ENTERO
            elif isinstance(v, float):
                tipo = TIPO_REAL
            else:
                tipo = TIPO_TEXTO
            campos.append(CampoDelEditor(str(k), tipo))
        return tuple(campos)
    return ()


def esquema_de(clave: str) -> EsquemaDeEditor:
    """El editor de un criterio, derivado de su ficha y del registro."""
    c = _ca.criterio(clave)
    v = _ve.variable(clave)
    r = c.resolucion
    formas = _formas_de(c)
    rango = _rango_de(c)
    cerradas = _opciones_cerradas(c)

    if len(formas) > 1:
        tipo_de_editor = ESCALAR
        campos: Tuple[CampoDelEditor, ...] = (
            CampoDelEditor(CAMPO_UNICO, TIPO_LIBRE, rango=rango, opciones=cerradas),)
    elif formas[0] in (TIPO_ENTERO, TIPO_REAL, TIPO_TEXTO):
        tipo_de_editor = ESCALAR
        campos = (CampoDelEditor(CAMPO_UNICO, formas[0], rango=rango,
                                 opciones=cerradas if formas[0] == TIPO_TEXTO else ()),)
    elif formas[0] == TIPO_CATEGORIA:
        tipo_de_editor = ESCALAR
        campos = (CampoDelEditor(CAMPO_UNICO, TIPO_CATEGORIA, opciones=cerradas),)
    elif formas[0] == _ca.FORMA_PAR_ORDENADO:
        tipo_de_editor = PAR
        campos = tuple(CampoDelEditor(n, TIPO_REAL, rango=rango) for n in CAMPOS_DEL_PAR)
    elif formas[0] == _ca.FORMA_SERIE_DE_PARES:
        tipo_de_editor = SERIE_DE_PARES
        campos = tuple(CampoDelEditor(n, TIPO_REAL) for n in CAMPOS_DE_LA_SERIE)
    elif formas[0] == _ca.FORMA_SERIE_DE_CLAVES and isinstance(r, DeTabla):
        tipo_de_editor = SERIE_DE_CLAVES
        campos = (CampoDelEditor(CAMPO_CLAVES, TIPO_TEXTO),)
    elif formas[0] == _ca.FORMA_DICT_CON_CAMPOS:
        campos = _campos_del_dict(c)
        tipo_de_editor = DICT if campos else LITERAL
    else:
        tipo_de_editor, campos = LITERAL, ()

    tabla_id, opciones = "", ()
    if isinstance(r, DeTabla):
        tabla_id, opciones = _opciones_de_tabla(clave, r, tipo_de_editor, formas)

    editable = not isinstance(r, Derivada)
    motivo = ("" if editable else
              f"se deriva de {', '.join(r.de)}; edite sus entradas (regla: {r.regla})")
    return EsquemaDeEditor(
        clave=clave, forma=formas, tipo_de_editor=tipo_de_editor, campos=campos,
        modo=v.modo.value, editable=editable, motivo_no_editable=motivo,
        tabla_id=tabla_id, opciones_de_tabla=opciones,
        exige_fila=(isinstance(r, DeTabla) and tipo_de_editor in (ESCALAR, PAR)
                    and TIPO_CATEGORIA not in formas),
        dominio=_dominio_de(r), valor_actual=_ca.criterio_efectivo(clave).valor)


# ===========================================================================
# Validar un campo al escribir
# ===========================================================================

def validar_campo(campo: CampoDelEditor, valor: Any) -> ResultadoValidacion:
    """
    El veredicto de UN campo con el valor ya interpretado por el parser de
    `gui/componentes.py`: tipo y ventana. Forma MAT-D13 en la ventana
    (condicion en positivo y negada, para que un NaN caiga del lado del
    rechazo). Un campo vacio es invalido si es obligatorio.
    """
    if valor is None or valor == "":
        if campo.obligatorio:
            return ResultadoValidacion(Estado.INVALIDO, f"«{campo.nombre}»: falta el valor")
        return ResultadoValidacion(Estado.VALIDO, f"«{campo.nombre}» vacio (opcional)")
    if campo.tipo == TIPO_ENTERO:
        if isinstance(valor, bool) or not isinstance(valor, int):
            return ResultadoValidacion(
                Estado.INVALIDO, f"«{campo.nombre}» tiene que ser un ENTERO (ni 1.0, ni texto)")
    elif campo.tipo == TIPO_REAL:
        if not _es_real(valor) or not math.isfinite(valor):
            return ResultadoValidacion(
                Estado.INVALIDO, f"«{campo.nombre}» tiene que ser un numero real finito")
    elif campo.tipo == TIPO_TEXTO:
        if not isinstance(valor, str) or not valor.strip():
            return ResultadoValidacion(
                Estado.INVALIDO, f"«{campo.nombre}» tiene que ser un texto no vacio")
    elif campo.tipo == TIPO_CATEGORIA:
        if not isinstance(valor, str) or valor not in campo.opciones:
            return ResultadoValidacion(
                Estado.INVALIDO,
                f"«{campo.nombre}» tiene que ser una de: {', '.join(campo.opciones)}")
    elif campo.tipo == TIPO_LIBRE:
        if _es_real(valor) and not math.isfinite(valor):
            return ResultadoValidacion(
                Estado.INVALIDO, f"«{campo.nombre}»: un numero tiene que ser finito")
    if campo.rango is not None and _es_real(valor):
        minimo, maximo = campo.rango
        numero = float(valor)
        if not minimo <= numero <= maximo:
            return ResultadoValidacion(
                Estado.INVALIDO,
                f"«{campo.nombre}» = {valor!r} cae fuera de la ventana de "
                f"sensibilidad que la ficha declara, [{minimo}, {maximo}]: la "
                "puerta de declaracion lo rechazara")
        return ResultadoValidacion(
            Estado.VALIDO, f"«{campo.nombre}» dentro de [{minimo}, {maximo}]")
    return ResultadoValidacion(Estado.VALIDO, f"«{campo.nombre}» con la forma esperada")


# ===========================================================================
# Armar y descomponer el valor entero
# ===========================================================================

def armar_valor(esquema: EsquemaDeEditor, piezas: Any) -> Any:
    """El valor ENTERO desde las piezas de los campos. Puro: no valida."""
    tipo = esquema.tipo_de_editor
    if tipo in (ESCALAR, LITERAL):
        return piezas[CAMPO_UNICO]
    if tipo == PAR:
        return tuple(piezas[n] for n in CAMPOS_DEL_PAR)
    if tipo == SERIE_DE_PARES:
        return [[a, b] for a, b in piezas]
    if tipo == DICT:
        return {c.nombre: piezas[c.nombre] for c in esquema.campos}
    if tipo == SERIE_DE_CLAVES:
        return tuple(piezas[CAMPO_CLAVES])
    raise ValueError(f"editor {tipo!r} sin regla de armado")


def descomponer_valor(esquema: EsquemaDeEditor, valor: Any) -> Any:
    """Las piezas de un valor entero, para pintarlas. `None` da piezas vacias."""
    tipo = esquema.tipo_de_editor
    if tipo in (ESCALAR, LITERAL):
        return {CAMPO_UNICO: valor}
    if tipo == PAR:
        par = tuple(valor) if isinstance(valor, (tuple, list)) and len(valor) == 2 else (None, None)
        return dict(zip(CAMPOS_DEL_PAR, par))
    if tipo == SERIE_DE_PARES:
        if not isinstance(valor, (tuple, list)):
            return []
        return [tuple(p) for p in valor if isinstance(p, (tuple, list)) and len(p) == 2]
    if tipo == DICT:
        origen = valor if isinstance(valor, dict) else {}
        return {c.nombre: origen.get(c.nombre) for c in esquema.campos}
    if tipo == SERIE_DE_CLAVES:
        return {CAMPO_CLAVES: list(valor) if isinstance(valor, (tuple, list)) else []}
    raise ValueError(f"editor {tipo!r} sin regla de descomposicion")


# ===========================================================================
# La guardia, en seco, y la declaracion
# ===========================================================================

def verificar(clave: str, valor: Any) -> None:
    """La MISMA guardia que el archivo, sin escribir nada (`ValueError`/`KeyError`)."""
    _ca.verificar_declaracion(clave, valor)


def veredicto_al_escribir(clave: str, valor: Any) -> ResultadoValidacion:
    """El veredicto de la puerta, como (estado, mensaje) para pintar al escribir."""
    try:
        verificar(clave, valor)
    except (ValueError, KeyError) as exc:
        return ResultadoValidacion(Estado.INVALIDO, str(exc))
    return ResultadoValidacion(
        Estado.VALIDO, f"'{clave}' = {valor!r} pasa la guardia de criterios_adoptados")


def fila_implicita(esquema: EsquemaDeEditor, valor: Any) -> Optional[str]:
    """
    La fila que un valor tecleado NOMBRA sin haberla elegido: la clave de una
    fila (o su id) cuando el valor es un texto; la unica fila elegible cuya
    celda propuesta es ese numero (o ese par) cuando es numerico. Con varias
    candidatas, ninguna: adivinar seria inventar la procedencia.
    """
    if not esquema.opciones_de_tabla:
        return None
    elegibles = [o for o in esquema.opciones_de_tabla if o.elegible]
    if isinstance(valor, str):
        for o in elegibles:
            if valor in (o.fila, f"{esquema.tabla_id}#{o.fila}"):
                return o.fila
        return None
    candidatas = []
    for o in elegibles:
        p = o.valor_propuesto
        if _es_real(valor) and _es_real(p) and abs(float(valor) - float(p)) <= TOL_UMBRAL_NORMATIVO:
            candidatas.append(o.fila)
        elif (isinstance(valor, (tuple, list)) and isinstance(p, tuple)
              and len(valor) == len(p) and all(_es_real(x) for x in valor)
              and all(abs(float(x) - float(y)) <= TOL_UMBRAL_NORMATIVO
                      for x, y in zip(valor, p))):
            candidatas.append(o.fila)
    return candidatas[0] if len(candidatas) == 1 else None


def declarar(clave: str, valor: Any, *, fila: str = "", nota: str = "") -> _dec.Procedencia:
    """
    Declara `valor` para la corrida por la puerta de `declaracion.py` que
    corresponde al modo del criterio, y devuelve la procedencia. ATOMICO:
    la guardia corre en seco antes; cada puerta de `declaracion` vuelve a
    verificar antes de escribir y registra la procedencia solo despues.
    """
    verificar(clave, valor)
    esquema = esquema_de(clave)
    r = _ca.criterio(clave).resolucion
    if isinstance(r, DeTabla):
        fila = (fila or "").strip() or (fila_implicita(esquema, valor) or "")
        if fila:
            return _dec.declarar_desde_tabla(clave, valor, tabla_id=esquema.tabla_id,
                                             filas=(fila,), nota=nota)
        if esquema.exige_fila and not nota.strip():
            raise ValueError(
                f"'{clave}' se lee de la tabla {esquema.tabla_id} y el valor {valor!r} "
                "no proviene de ninguna de sus filas: una adopcion distinta exige "
                "procedencia. Elija la fila en el editor, o escriba en la nota por "
                "que se adopta otro numero (la memoria lo imprimira como adoptado)")
        return _dec.declarar_valor(clave, valor, nota=nota)
    if isinstance(r, EnRango):
        return _dec.declarar_en_rango(clave, valor, nota=nota)
    return _dec.declarar_valor(clave, valor, nota=nota)
