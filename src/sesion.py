"""
sesion.py
=========
EL FORMATO DE LA SESION DE LA VENTANA, en un modulo sin Tk (EXT-8, PC-11).

Por que existe
--------------
Hasta EXT-8 el esquema de la sesion --- `FORMATO_SESION`, `ESQUEMA_SESION`,
`errores_de_sesion` y la traduccion de los campos de la pestana 1 a las
banderas de la CLI --- vivia en `gui/app.py`. Estaba bien ahi mientras la
sesion solo la leia la ventana. EXT-8 saca la exportacion del PDF a un
SUBPROCESO que corre `cli.py --sesion <archivo>`: la CLI tiene que leer la
MISMA sesion que la ventana guarda, y no puede importar `gui/` --- `gui`
importa `cli`, y un modulo con Tk no entra en una CLI ---. Dos esquemas, uno
por puerta, serian dos formatos que divergen el dia que uno cambie. Este
modulo es el unico, y `gui/app.py` lo reexporta con los mismos nombres.

Que NO hace: no toca ningun estado. Validar (`errores_de_sesion`) y traducir
(`banderas_de_externos`) son funciones puras; reponer los criterios es
`declaracion.restaurar_sesion`, y quien aplica el resto es cada puerta
(`ExpedienteApp.cargar_sesion`, `cli.aplicar_sesion_serializada`).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# v2: la sesion guarda tambien el alcance de la corrida y los criterios
# declarados con su procedencia (SIS-A-17, SIS-A-18). Una sesion v1 se sigue
# leyendo: lo que no trae se queda en su valor por defecto y la ventana lo
# dice, que es el patron de migracion de `legacy/Tc.py`.
FORMATO_SESION = 2

# EL ESQUEMA DE LA SESION, como dato (PC-16): que tipo tiene que traer cada
# clave. `errores_de_sesion` lo contrasta ENTERO antes de que nadie toque un
# solo campo. `criterios` admite ademas `None` --- una sesion sin bloque de
# criterios --- y `externos` es un objeto de cadenas.
ESQUEMA_SESION = {
    "formato_version": int,
    "app_version": str,
    "proyecto": str,
    "csv": str,
    "datos_externos": str,
    "externos": dict,
    "alcance": str,
    "criterios": dict,
}

# La traduccion rotulo-de-ventana -> clave-de-expediente. Es UNA, y la usan
# la anotacion de familias de la pestana 1, `_leer_banderas` de la ventana y
# `banderas_de_externos` de aqui (que es lo que la CLI lee de la sesion): dos
# copias se separan el dia que aparezca un sexto campo, y entonces la ventana
# anota sobre un campo y declara sobre otro.
CLAVE_EXTERNA_DE_CAMPO = {
    "luz_m": "luz_m",
    "TW_m": "TW_m",
    "longitud_m": "longitud_m",
    "l_hidraulico": "L_hidraulico_m",
    "categoria_tr": "categoria_tr",
}

# El unico campo que NO es numero: es una FILA de la Tabla N 02, y la coma
# decimal no se le toca.
CAMPO_CATEGORICO = "categoria_tr"


def errores_de_sesion(data: Any) -> List[str]:
    """
    Los defectos de forma de una sesion, como lista de frases; vacia si la
    sesion se puede aplicar entera. No aplica nada: es la mitad que faltaba
    en `cargar_sesion`, que escribia el proyecto y el CSV en la ventana y
    reventaba despues con `"externos": null`.
    """
    errores = []
    if not isinstance(data, dict):
        return [f"una sesion es un objeto con claves, y este trae "
                f"{type(data).__name__}"]
    for clave, tipo in ESQUEMA_SESION.items():
        if clave not in data:
            continue
        valor = data[clave]
        if clave == "criterios" and valor is None:
            continue
        # `bool` es subclase de `int`: una version `true` no es una version.
        if not isinstance(valor, tipo) or isinstance(valor, bool):
            errores.append(f"'{clave}' tiene que ser {tipo.__name__} y trae "
                           f"{type(valor).__name__}")
    externos = data.get("externos")
    if isinstance(externos, dict):
        for clave, valor in externos.items():
            if not isinstance(clave, str) or not isinstance(valor, str):
                errores.append(f"'externos' tiene que ser un objeto de "
                               f"cadenas: '{clave}' trae "
                               f"{type(valor).__name__}")
    # EL INTERIOR DE `criterios` TAMBIEN, o `{"valores": null}` pasaba la
    # validacion, `cargar_sesion` pisaba proyecto, CSV y externos, y
    # `restaurar_sesion` rechazaba el bloque DESPUES: la mezcla de EXT-A-02
    # con un aviso encima (auditoria adversarial de EXT-4).
    criterios = data.get("criterios")
    if isinstance(criterios, dict):
        for clave in ("valores", "procedencias"):
            if clave in criterios and not isinstance(criterios[clave], dict):
                errores.append(f"'criterios.{clave}' tiene que ser un objeto "
                               f"con claves y trae "
                               f"{type(criterios[clave]).__name__}")
    return errores


def banderas_de_externos(externos: Dict[str, str]) -> Dict[str, Optional[str]]:
    """
    Los textos de los campos de la pestana 1, como las banderas que
    `servicio.cargar_datos_externos` espera: `None` si el campo quedo vacio, la
    coma decimal pasada a punto en los numericos, y la categoria de TR tal
    cual. Un campo que la sesion no trae es un campo vacio.
    """
    banderas: Dict[str, Optional[str]] = {}
    for campo, clave in CLAVE_EXTERNA_DE_CAMPO.items():
        texto = str(externos.get(campo, "") or "").strip()
        banderas[clave] = None
        if texto:
            banderas[clave] = (texto if campo == CAMPO_CATEGORICO
                               else texto.replace(",", "."))
    return banderas
