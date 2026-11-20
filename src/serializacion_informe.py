"""
src/serializacion_informe.py
============================
EL `Informe` CON IDA Y VUELTA (VE-5, fichas EXT-8-02, EXT-10-04 y UI5-01 b;
decision del dueño ya adoptada: el hijo del PDF lee la CORRIDA EMBEBIDA en
vez de recalcular).

Hasta VE-5 el proceso hijo que escribe el PDF de la ventana VOLVIA A CORRER
la obra con la sesion de la corrida: releia el CSV, el JSON de datos
externos y las dos entradas de la hidrologia, y su memoria llevaba la hora
de ESA corrida y las huellas de los archivos tal como estuvieran al
exportar. Un encabezado igual no probaba la misma corrida (ficha UI5-01 b),
y la razon por la que se recalculaba era una sola: `Informe` no tenia forma
de ida y vuelta --- `cli.informe_json` es un volcado de SALIDA, con perdida,
y M11 formatea objetos, no dicts (ficha EXT-10-04) ---.

Aqui esta esa forma. `informe_a_dict` escribe el arbol entero del informe
--- dataclasses, enums, tuplas, dicts, los `mappingproxy` congelados de
`ContextoCorrida`, rutas y reales no finitos --- como JSON ETIQUETADO, y
`informe_desde_dict` lo reconstruye. No es `pickle`, a proposito: una sesion
es un archivo que se guarda, se copia y se manda, y cargar un `pickle` es
ejecutar lo que traiga. Aqui no se ejecuta nada: el cargador solo construye
clases que son DATACLASSES o ENUMS de un modulo del paquete `src`, por su
nombre calificado, y rechaza cualquier otra cosa con `ValueError`. Una
dataclass se repone sin llamar a su `__init__` ni a su `__post_init__` (como
lo hace `pickle`): el objeto ya paso sus guardias cuando se construyo en la
corrida, y los campos `init=False` tambien vuelven. Un campo que el archivo
trae y la clase ya no tiene, o al reves, es `ValueError`: un informe de otra
version del programa no se formatea a medias.

LA IDENTIDAD SE CONSERVA. La memoria no imprime dos veces el mismo paso:
lo reconoce por IDENTIDAD (`id(paso)`, `M11._pasos_de_fase` y la traza del
punto), y un paso que la corrida comparte entre dos sitios es el MISMO
objeto. Una serializacion que lo duplicara daria otra memoria --- medido en
`expediente_cabezal`: un paso «repetido» de mas en el armado ---. Por eso
cada contenedor lleva su numero de orden (`__n__`, en el orden en que
termina de escribirse) y su segunda aparicion se escribe como
`{"__ref__": n}`: a la vuelta es el mismo objeto.

La garantia de que lo cargado ES la corrida la da quien lo carga, no este
modulo: la CLI compara el volcado del informe cargado con el `informe_json`
de la misma corrida embebida, y si difieren no formatea
(`cli._informe_de_la_corrida_embebida`).
"""

from __future__ import annotations

import dataclasses
import enum
import importlib
import math
import types
from pathlib import Path, PurePath
from typing import Any, Dict, List

# La version de ESTA forma. Sube si cambia la codificacion, no si cambia el
# informe: un campo nuevo del informe lo detecta el cargador por si solo.
FORMATO_INFORME_SERIALIZADO = 1

# El unico paquete cuyas clases el cargador construye.
PAQUETE_PERMITIDO = "src"

_CLASE, _CAMPOS = "__dc__", "campos"
_ENUM, _MIEMBRO = "__enum__", "miembro"
_TUPLA, _LISTA, _DICT, _MAPA, _CONJ = ("__tupla__", "__lista__", "__dict__",
                                        "__mapa__", "__conj__")
_RUTA, _REAL, _REF, _N = "__ruta__", "__real__", "__ref__", "__n__"
_ETIQUETAS = (_CLASE, _ENUM, _TUPLA, _LISTA, _DICT, _MAPA, _CONJ, _RUTA,
              _REAL, _REF)


def _nombre_de(clase: type) -> str:
    return f"{clase.__module__}:{clase.__qualname__}"


class _Escritor:
    """Un recorrido: la pila (para los ciclos) y lo ya escrito (identidad)."""

    def __init__(self) -> None:
        self.pila: List[int] = []
        self.escritos: Dict[int, int] = {}
        # Los objetos escritos se retienen: su `id` no puede reutilizarse
        # mientras dure el recorrido.
        self.retenidos: List[Any] = []

    def escribir(self, valor: Any) -> Any:
        # El enum PRIMERO: los del proyecto son `str, Enum` (`TipoDeBloqueo`,
        # `Poblacion`...) y como cadena perderian su clase a la vuelta.
        if isinstance(valor, enum.Enum):
            return {_ENUM: _nombre_de(type(valor)), _MIEMBRO: valor.name}
        if valor is None or isinstance(valor, (bool, str, int)):
            return valor
        if isinstance(valor, float):
            return valor if math.isfinite(valor) else {_REAL: repr(valor)}
        if isinstance(valor, PurePath):
            return {_RUTA: str(valor)}
        clave = id(valor)
        if clave in self.escritos:
            return {_REF: self.escritos[clave]}
        if clave in self.pila:
            raise ValueError(f"el informe tiene un ciclo en {type(valor).__name__}: "
                             "no se puede serializar")
        self.pila.append(clave)
        try:
            salida = self._contenedor(valor)
        finally:
            self.pila.pop()
        salida[_N] = len(self.escritos)
        self.escritos[clave] = salida[_N]
        self.retenidos.append(valor)
        return salida

    def _pares(self, mapa: Any) -> List[List[Any]]:
        return [[self.escribir(k), self.escribir(v)] for k, v in mapa.items()]

    def _contenedor(self, valor: Any) -> Dict[str, Any]:
        if dataclasses.is_dataclass(valor) and not isinstance(valor, type):
            return {_CLASE: _nombre_de(type(valor)),
                    _CAMPOS: {f.name: self.escribir(getattr(valor, f.name))
                              for f in dataclasses.fields(valor)}}
        if isinstance(valor, tuple):
            return {_TUPLA: [self.escribir(v) for v in valor]}
        if isinstance(valor, list):
            return {_LISTA: [self.escribir(v) for v in valor]}
        if isinstance(valor, types.MappingProxyType):
            return {_MAPA: self._pares(valor)}
        if isinstance(valor, dict):
            return {_DICT: self._pares(valor)}
        if isinstance(valor, (set, frozenset)):
            return {_CONJ: [self.escribir(v) for v in valor],
                    "congelado": isinstance(valor, frozenset)}
        raise TypeError(f"el informe lleva un {type(valor).__module__}."
                        f"{type(valor).__qualname__}, que esta forma no sabe "
                        "escribir: hay que ensenarselo aqui antes de embeberlo")


def informe_a_dict(informe: Any) -> Dict[str, Any]:
    """El informe entero como un dict que `json.dumps` escribe sin perder nada."""
    return {"formato": FORMATO_INFORME_SERIALIZADO,
            "informe": _Escritor().escribir(informe)}


def informe_desde_dict(datos: Any) -> Any:
    """
    El informe que `informe_a_dict` escribio. `ValueError` si el dict no es
    de esta forma, si nombra una clase fuera de `src` o que no es dataclass
    ni enum, o si los campos no son los de la clase.
    """
    if not isinstance(datos, dict) or set(datos) != {"formato", "informe"}:
        raise ValueError("no es un informe serializado: faltan 'formato' e "
                         "'informe'")
    if datos["formato"] != FORMATO_INFORME_SERIALIZADO:
        raise ValueError(f"informe serializado en el formato {datos['formato']!r}; "
                         f"este programa lee el {FORMATO_INFORME_SERIALIZADO}")
    return _Lector().leer(datos["informe"])


def _clase(nombre: Any) -> type:
    if not isinstance(nombre, str) or ":" not in nombre:
        raise ValueError(f"nombre de clase invalido: {nombre!r}")
    modulo, calificado = nombre.split(":", 1)
    if modulo != PAQUETE_PERMITIDO and not modulo.startswith(PAQUETE_PERMITIDO + "."):
        raise ValueError(f"la clase {nombre!r} no es del paquete "
                         f"'{PAQUETE_PERMITIDO}': no se construye")
    try:
        objeto: Any = importlib.import_module(modulo)
    except ImportError as exc:
        raise ValueError(f"la clase {nombre!r} no existe en este programa") from exc
    for parte in calificado.split("."):
        objeto = getattr(objeto, parte, None)
        if objeto is None:
            raise ValueError(f"la clase {nombre!r} no existe en este programa")
    if not isinstance(objeto, type) or not (
            dataclasses.is_dataclass(objeto) or issubclass(objeto, enum.Enum)):
        raise ValueError(f"{nombre!r} no es una dataclass ni un enum: no se construye")
    return objeto


class _Lector:
    """El recorrido inverso, con la tabla de lo ya leido por su numero."""

    def __init__(self) -> None:
        self.leidos: Dict[int, Any] = {}

    def leer(self, valor: Any) -> Any:
        if valor is None or isinstance(valor, (bool, int, float, str)):
            return valor
        if not isinstance(valor, dict):
            raise ValueError(f"valor inesperado en el informe serializado: {valor!r}")
        etiquetas = [e for e in _ETIQUETAS if e in valor]
        if len(etiquetas) != 1:
            raise ValueError(f"objeto sin etiqueta reconocible: {sorted(valor)}")
        etiqueta = etiquetas[0]
        if etiqueta == _REF:
            if valor[_REF] not in self.leidos:
                raise ValueError(f"referencia {valor[_REF]!r} a un objeto que "
                                 "no se ha leido")
            return self.leidos[valor[_REF]]
        if etiqueta == _REAL:
            return float(valor[_REAL])
        if etiqueta == _RUTA:
            return Path(valor[_RUTA])
        if etiqueta == _ENUM:
            clase = _clase(valor[_ENUM])
            if not issubclass(clase, enum.Enum):
                raise ValueError(f"{valor[_ENUM]!r} no es un enum")
            return clase[valor[_MIEMBRO]]
        objeto = self._contenedor(etiqueta, valor)
        numero = valor.get(_N)
        if not isinstance(numero, int) or numero in self.leidos:
            raise ValueError(f"numero de objeto invalido o repetido: {numero!r}")
        self.leidos[numero] = objeto
        return objeto

    def _contenedor(self, etiqueta: str, valor: Dict[str, Any]) -> Any:
        if etiqueta == _TUPLA:
            return tuple(self.leer(v) for v in valor[_TUPLA])
        if etiqueta == _LISTA:
            return [self.leer(v) for v in valor[_LISTA]]
        if etiqueta in (_DICT, _MAPA):
            salida = {self.leer(k): self.leer(v) for k, v in valor[etiqueta]}
            return types.MappingProxyType(salida) if etiqueta == _MAPA else salida
        if etiqueta == _CONJ:
            miembros = [self.leer(v) for v in valor[_CONJ]]
            return frozenset(miembros) if valor.get("congelado") else set(miembros)
        clase = _clase(valor[_CLASE])
        if not dataclasses.is_dataclass(clase):
            raise ValueError(f"{valor[_CLASE]!r} no es una dataclass")
        campos = valor.get(_CAMPOS)
        nombres = {f.name for f in dataclasses.fields(clase)}
        if not isinstance(campos, dict) or set(campos) != nombres:
            raise ValueError(
                f"los campos de {valor[_CLASE]!r} no son los de esta version del "
                f"programa (sobran {sorted(set(campos or ()) - nombres)}, faltan "
                f"{sorted(nombres - set(campos or ()))})")
        # Sin `__init__` ni `__post_init__`, como `pickle`: el objeto ya paso
        # sus guardias en la corrida, y los campos `init=False` vuelven igual.
        objeto = object.__new__(clase)
        for nombre, crudo in campos.items():
            object.__setattr__(objeto, nombre, self.leer(crudo))
        return objeto
