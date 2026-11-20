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

import copy
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.modelos import ALCANCE_EXPEDIENTE

# v2: la sesion guarda tambien el alcance de la corrida y los criterios
# declarados con su procedencia (SIS-A-17, SIS-A-18).
# v3 (EXT-10, fase E04 del plan de evolucion): la sesion es EL UNICO LUGAR
# DEL «PROYECTO ACTUAL». Gana `id` (identidad, uuid4), `datos_sitio` (la
# ruta del sitio.json, hermana de `datos_externos`), `sitio` (los datos de
# sitio [S] declarados POR SESION, con valor, trazabilidad y fecha, que es
# como otra obra entra sin editar `datos_sitio.py`: EXT-V-01), `csv_sha1`
# (la huella del CSV de la ultima corrida guardada) y `corridas` (cada
# corrida con su `informe_json` embebido: las REVISIONES del expediente).
# La migracion es EXPLICITA (`migrar_a_actual`), no por defectos silenciosos:
# una sesion v1 o v2 se completa y la puerta que la abre dice que se
# completo.
# v4 (UI-1, ficha T1-04): `cuencas` y `estacion`, las rutas de las dos
# entradas de la hidrologia (las de `--cuencas` y `--estacion`), guardadas y
# resueltas con la MISMA convencion que el CSV: el texto tal como esta en el
# campo al guardar, y `ruta_de_campo(texto)` al leerla, en las dos puertas. Una sesion v3 no conocia la hidrologia y
# se completa con las dos vacias --que es exactamente lo que significaba: el
# caudal entra por `Q_m3s`--; no hay nada que avisar, porque nada cambia, y
# al guardarla se escribe en v4.
FORMATO_SESION = 4  # literal-ok: version del formato de sesion, no una magnitud
# El escalon anterior, con nombre: `migrar_a_actual` sube de v3 a v4 y una
# sesion v3 incompleta se completa con el escalon de v2 -> v3.
FORMATO_V3 = 3  # literal-ok: version del formato de sesion (EXT-10), no una magnitud

# EL ESQUEMA DE LA SESION, como dato (PC-16): que tipo tiene que traer cada
# clave. `errores_de_sesion` lo contrasta ENTERO antes de que nadie toque un
# solo campo. `criterios` y `sitio` admiten ademas `None` --- una sesion sin
# bloque --- y `externos` es un objeto de cadenas. Toda clave es OPCIONAL en
# la validacion (`{}` es una sesion valida y vacia, fijado por test): lo que
# falte lo completa `migrar_a_actual`, diciendo que lo completo.
ESQUEMA_SESION = {
    "formato_version": int,
    "app_version": str,
    "id": str,
    "proyecto": str,
    "csv": str,
    "datos_externos": str,
    "datos_sitio": str,
    "cuencas": str,
    "estacion": str,
    "externos": dict,
    "alcance": str,
    "criterios": dict,
    "sitio": dict,
    "csv_sha1": str,
    "corridas": list,
}

# Lo que cada entrada de `sitio.valores` tiene que traer: el valor de la
# lectura, como reproducirla y cuando se hizo. Es el contrato de
# `datos_sitio.establecer_dato_dinamico`, escrito una vez.
CAMPOS_DE_UN_DATO_DE_SITIO = ("valor", "trazabilidad", "fecha")

# Lo que cada corrida embebida trae: la marca de la corrida, su alcance, las
# dos huellas y el volcado entero de `cli.informe_json`.
CAMPOS_DE_UNA_CORRIDA = ("generado_utc", "alcance", "csv_sha1",
                         "criterios_sha1", "informe_json")
# Y uno OPCIONAL (VE-5, fichas EXT-10-04 y UI5-01 b): el informe entero con
# ida y vuelta (`src/serializacion_informe.py`), que la ventana embebe en la
# sesion de trabajo del hijo del PDF para que este FORMATEE la corrida en vez
# de recalcularla (`cli.py --corrida-embebida`). «Guardar sesion» no lo
# escribe: pesa megabytes y una sesion guardada se compara, no se formatea.
CAMPO_INFORME_SERIALIZADO = "informe_serializado"

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
    # --- VE-5 (ficha T6-04) --- la pendiente del barril y la pendiente
    # transversal de la plataforma (bombeo en tangente, peralte en curva),
    # que hasta VE-5 solo entraban por el JSON de datos externos. Una sesion
    # de un formato anterior no las trae, y un campo que la sesion no trae es
    # un campo vacio (`banderas_de_externos`): la sesion vieja abre igual.
    "S_conducto": "S_conducto",
    "bombeo": "bombeo",
    "peralte": "peralte",
}

# El unico campo que NO es numero: es una FILA de la Tabla N 02, y la coma
# decimal no se le toca.
CAMPO_CATEGORICO = "categoria_tr"


def ruta_de_campo(texto: Any) -> Optional[Path]:
    """
    LA CONVENCION DE RUTAS DE LA SESION, una para las dos puertas (UI-1): el
    texto de un campo de archivo sin los espacios de los extremos, y `None`
    si queda vacio. La ventana ya lo leia asi al ejecutar (`.strip()`) y la
    CLI hacia `Path(texto)` crudo al abrir la sesion, de modo que una ruta
    tecleada con un espacio al final corria en la ventana y no existia para
    `cli.py --sesion` (revision de UI-1). La relativa se resuelve contra el
    directorio de trabajo, en las dos.
    """
    limpio = str(texto or "").strip()
    return Path(limpio) if limpio else None


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
        if clave in ("criterios", "sitio") and valor is None:
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
    # EL INTERIOR DE `sitio` Y DE `corridas` (EXT-10), por la misma razon:
    # un bloque de datos de sitio con un valor suelto en vez de un objeto
    # {valor, trazabilidad, fecha} no es un dato de sitio, es un numero sin
    # lectura, y tiene que rechazarse ANTES de vaciar lo declarado.
    sitio = data.get("sitio")
    if isinstance(sitio, dict):
        valores = sitio.get("valores")
        if "valores" in sitio and not isinstance(valores, dict):
            errores.append("'sitio.valores' tiene que ser un objeto con claves "
                           f"y trae {type(valores).__name__}")
        elif isinstance(valores, dict):
            for clave, entrada in valores.items():
                if not isinstance(entrada, dict):
                    errores.append(f"'sitio.valores.{clave}' tiene que ser un "
                                   "objeto con valor, trazabilidad y fecha y "
                                   f"trae {type(entrada).__name__}")
                    continue
                faltan = [c for c in CAMPOS_DE_UN_DATO_DE_SITIO if c not in entrada]
                if faltan:
                    errores.append(f"'sitio.valores.{clave}' no trae "
                                   f"{', '.join(faltan)}")
                if "origen" in entrada and not isinstance(entrada["origen"], str):
                    errores.append(f"'sitio.valores.{clave}.origen' tiene que "
                                   f"ser str y trae "
                                   f"{type(entrada['origen']).__name__}")
    corridas = data.get("corridas")
    if isinstance(corridas, list):
        for indice, corrida in enumerate(corridas):
            if not isinstance(corrida, dict):
                errores.append(f"'corridas[{indice}]' tiene que ser un objeto y "
                               f"trae {type(corrida).__name__}")
                continue
            if "informe_json" in corrida and not isinstance(corrida["informe_json"], dict):
                errores.append(f"'corridas[{indice}].informe_json' tiene que ser "
                               "un objeto con claves y trae "
                               f"{type(corrida['informe_json']).__name__}")
            serializado = corrida.get(CAMPO_INFORME_SERIALIZADO)
            if serializado is not None and not isinstance(serializado, dict):
                errores.append(f"'corridas[{indice}].{CAMPO_INFORME_SERIALIZADO}' "
                               "tiene que ser un objeto con claves y trae "
                               f"{type(serializado).__name__}")
    return errores


# ---------------------------------------------------------------------------
# Migracion explicita, sesion vacia, corridas y escritura atomica (EXT-10)
# ---------------------------------------------------------------------------

def _version_de(data: Any) -> int:
    if not isinstance(data, dict):
        raise ValueError(
            "una sesion es un objeto con claves, y esto trae "
            f"{type(data).__name__}")
    version = data.get("formato_version", 1)
    if isinstance(version, bool) or not isinstance(version, int):
        raise ValueError(
            f"'formato_version' tiene que ser un entero y trae {version!r}")
    if version > FORMATO_SESION:
        raise ValueError(
            f"la sesion es del formato v{version} y este programa lee hasta "
            f"v{FORMATO_SESION}: hace falta una version mas nueva del programa")
    if version < 1:
        raise ValueError(f"'formato_version' no puede ser {version}")
    return version


def _migrar_v1_a_v2(data: Dict[str, Any]) -> List[str]:
    """v1 no guardaba ni el alcance ni los criterios declarados (S17)."""
    avisos = []
    if "alcance" not in data:
        data["alcance"] = ALCANCE_EXPEDIENTE
        avisos.append("la sesion v1 no guardaba el alcance de la corrida: se "
                      f"leyo como '{ALCANCE_EXPEDIENTE}', revise antes de ejecutar")
    if not isinstance(data.get("criterios"), dict):
        data["criterios"] = {"valores": {}, "procedencias": {}}
        avisos.append("la sesion v1 no guardaba los criterios declarados: se "
                      "abre sin ninguno")
    data["formato_version"] = 2
    return avisos


def _migrar_v2_a_v3(data: Dict[str, Any]) -> List[str]:
    """
    v2 no tenia identidad, ni datos de sitio por sesion, ni huella del CSV,
    ni corridas (EXT-4-01, E04). Se completan y se dice.
    """
    avisos = []
    if not str(data.get("id") or "").strip():
        data["id"] = uuid.uuid4().hex
        avisos.append("la sesion no tenia identidad (v2): se le asigno el id "
                      f"{data['id']}, que solo sera estable cuando la guarde")
    if "datos_sitio" not in data:
        data["datos_sitio"] = ""
    if not isinstance(data.get("sitio"), dict):
        data["sitio"] = {"valores": {}}
        avisos.append("la sesion no traia datos de sitio [S] declarados por "
                      "sesion: gobiernan los de datos_sitio.py (la obra del "
                      "repositorio) mientras no se declaren otros")
    if "csv_sha1" not in data:
        data["csv_sha1"] = ""
    if not isinstance(data.get("corridas"), list):
        data["corridas"] = []
    data["formato_version"] = FORMATO_V3
    return avisos


# Las claves que cada escalon de la migracion garantiza. Una sesion que dice
# ser de una version y no las trae (las de `tests/apoyo/` que escriben
# `FORMATO_SESION` sin traer todo) se completa con el mismo escalon.
CLAVES_DE_V3 = ("id", "datos_sitio", "sitio", "csv_sha1", "corridas")
CLAVES_DE_V4 = ("cuencas", "estacion")


def _migrar_v3_a_v4(data: Dict[str, Any]) -> List[str]:
    """
    v3 no conocia la hidrologia (UI-1): se completa con las dos rutas
    VACIAS, que es lo que una sesion v3 significaba --el caudal entra
    declarado por `Q_m3s`--. No hay aviso: nada de lo que la sesion decia
    cambia ni se supone (la diferencia con `_migrar_v2_a_v3`, que asigna
    una identidad y deja gobernar a datos_sitio.py, y lo dice).
    """
    for clave in CLAVES_DE_V4:
        if not isinstance(data.get(clave), str):
            data[clave] = ""
    data["formato_version"] = FORMATO_SESION
    return []


def migrar_a_actual(data: Any) -> Tuple[Dict[str, Any], List[str]]:
    """
    Una COPIA de la sesion llevada al formato actual, y la lista de lo que
    hubo que completar para llegar. Explicita a proposito (E04): hasta EXT-10
    la ventana leia una sesion v1 con defectos silenciosos y un texto cableado
    en `cargar_sesion`; la CLI ni miraba la version.

    Sube de escalon en escalon (v1 -> v2 -> v3 -> v4) para que cada version
    tenga escrito, en un solo sitio, que le faltaba. Una sesion de v3 o
    posterior a la que le falten las claves de v3 --- las de `tests/apoyo/`
    que escriben `FORMATO_SESION` sin traer todo --- se completa igual, y lo
    dice; las dos de v4 se completan vacias y sin aviso (`_migrar_v3_a_v4`).
    Una version que no es entera, o mayor que la actual, es `ValueError`
    (nunca un `TypeError` fuera del brazo de las puertas).
    """
    version = _version_de(data)
    migrada = copy.deepcopy(data)
    avisos: List[str] = []
    if version < 2:
        avisos.extend(f"v1 -> v2: {a}" for a in _migrar_v1_a_v2(migrada))
    if version < FORMATO_V3:
        avisos.extend(f"v2 -> v3: {a}" for a in _migrar_v2_a_v3(migrada))
    elif not all(clave in migrada for clave in CLAVES_DE_V3):
        incompleta = []
        incompleta.extend(f"v{version} incompleta: {a}"
                          for a in _migrar_v2_a_v3(migrada))
        if not incompleta:
            incompleta.append(f"v{version} incompleta: se completaron las "
                              "claves que faltaban")
        avisos.extend(incompleta)
    if version < FORMATO_SESION or not all(isinstance(migrada.get(c), str)
                                           for c in CLAVES_DE_V4):
        avisos.extend(f"v3 -> v4: {a}" for a in _migrar_v3_a_v4(migrada))
    migrada["formato_version"] = FORMATO_SESION
    return migrada, avisos


def sesion_vacia(app_version: str) -> Dict[str, Any]:
    """
    La sesion de un PROYECTO NUEVO: identidad nueva y todo lo demas vacio.
    Es como se crea otra obra sobre el mismo despliegue (EXT-V-01): cargando
    esta sesion, nunca vaciando `datos_sitio.py` ni `criterios_adoptados.py`.
    Mientras no declare sus [S], gobiernan los del archivo y la memoria lo
    dice en la fila «Origen» y en la advertencia de corredor.
    """
    return {
        "formato_version": FORMATO_SESION,
        "app_version": str(app_version),
        "id": uuid.uuid4().hex,
        "proyecto": "",
        "csv": "",
        "datos_externos": "",
        "datos_sitio": "",
        "cuencas": "",
        "estacion": "",
        "externos": {},
        "alcance": ALCANCE_EXPEDIENTE,
        "criterios": {"valores": {}, "procedencias": {}},
        "sitio": {"valores": {}},
        "csv_sha1": "",
        "corridas": [],
    }


def corrida_para_sesion(informe: Any, informe_json: Dict[str, Any], *,
                        con_informe: bool = False) -> Dict[str, Any]:
    """
    Una corrida tal como la sesion la embebe (E04): su marca, su alcance, las
    dos huellas del `ContextoCorrida` y el volcado entero. Es lo que permite
    a la CLI, al abrir la sesion, decir si su corrida REPRODUCE la guardada.

    Con `con_informe` (VE-5) lleva ademas el informe entero con ida y vuelta
    (`CAMPO_INFORME_SERIALIZADO`): es la corrida que el hijo del PDF formatea
    sin recalcular.
    """
    contexto = informe.contexto
    corrida = {
        "generado_utc": informe.generado,
        "alcance": informe.alcance,
        "csv_sha1": contexto.csv_sha1,
        "criterios_sha1": contexto.criterios_sha1,
        "informe_json": informe_json,
    }
    if con_informe:
        from src import serializacion_informe
        corrida[CAMPO_INFORME_SERIALIZADO] = serializacion_informe.informe_a_dict(informe)
    return corrida


def sin_origen_de_los_datos_de_sitio(informe_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    El JSON de un informe sin las RUTAS de origen de sus datos de sitio,
    para comparar dos corridas de la misma obra hechas en dos maquinas o
    con la sesion renombrada: el origen es una ruta absoluta o el nombre de
    un archivo de sesion, y no dice nada del calculo. La CLI compara asi su
    corrida con la embebida en la sesion (auditoria adversarial de EXT-10).
    """
    copia = json.loads(json.dumps(informe_json))
    sitio = copia.get("datos_sitio")
    if isinstance(sitio, dict):
        for usado in sitio.get("usados", []) or []:
            if isinstance(usado, dict):
                usado.pop("origen", None)
    expediente = copia.get("expediente")
    if isinstance(expediente, dict) and isinstance(expediente.get("corredor_del_proyecto"), dict):
        expediente["corredor_del_proyecto"].pop("origen", None)
    return copia


def sin_marca_de_tiempo(informe_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    El JSON de un informe sin su marca de tiempo, para comparar dos corridas
    de la MISMA obra hechas en momentos distintos. La marca de tiempo esta
    en `expediente.generado_utc` (y en `generado`, si el volcado la lleva
    arriba): es el unico campo volatil del informe, y la linea base de la
    Familia C la normaliza por la misma razon. Vivia en
    `gui/exportacion_pdf.py` (EXT-8); desde EXT-10 la CLI tambien la necesita
    y `exportacion_pdf` la reexporta.
    """
    copia = json.loads(json.dumps(informe_json))
    copia.pop("generado", None)
    if isinstance(copia.get("expediente"), dict):
        copia["expediente"].pop("generado_utc", None)
    return copia


def escribir_json_atomico(ruta: Path, data: Any) -> None:
    """
    Escribe `data` como JSON en `ruta` SIN dejar nunca un archivo a medias:
    a un temporal en el mismo directorio, `flush` + `fsync`, y `os.replace`,
    que es atomico en POSIX y en Windows sobre el mismo volumen. Si algo
    falla, el archivo anterior sigue intacto y el temporal se borra.

    Es lo que E04 pide para la sesion, y lo usan «Guardar sesion», el JSON
    del expediente que escriben la CLI y la ventana, y la sesion de trabajo
    del subproceso del PDF: cuatro escrituras, un solo camino.

    --- VE-5 (ficha UI5-01 d) --- por `escritura_atomica.escribir_atomico`,
    la de los PDF y las memorias: hasta VE-5 el temporal llevaba el nombre
    del destino (un nombre largo no cabia), no seguia un enlace simbolico y
    no conservaba el modo del archivo previo. Un dato que no es JSON (un
    NaN) o un fallo a mitad dejan el destino como estaba y ningun temporal.
    """
    from src import escritura_atomica
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    def escribir(temporal: Path) -> None:
        with Path(temporal).open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())

    escritura_atomica.escribir_atomico(ruta, escribir)


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
