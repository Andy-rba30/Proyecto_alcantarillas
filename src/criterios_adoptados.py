"""
criterios_adoptados.py
======================
Fuente unica de verdad para todo parametro que NO sea una exigencia normativa
verificada. Ningun otro modulo del script debe declarar estos valores.

Regla de uso
------------
    from src.criterios_adoptados import valor, reporte_criterios

    Fpga = valor("F_pga")          # registra el uso automaticamente
    ...
    print(reporte_criterios())     # M11 lo imprime al final del reporte

Un criterio con valor None lanza CriterioPendienteError (modelos.py) y detiene
el calculo. Nunca devuelve un default. Para saber que falta ANTES de correr,
sin provocar la excepcion, se consulta criterios_sin_valor().

La UNICA excepcion son los criterios marcados `opcional=True`: no cubren un
vacio, refinan un valor que la norma ya fija. Sin declarar, el consumidor
aplica el valor normativo por defecto y el calculo sigue. Se leen con
valor_si_declarado(), nunca con valor(), y se listan con
criterios_opcionales_sin_declarar(), no con criterios_sin_valor().

Todo valor que entre por cualquiera de los tres caminos de declaracion -- el
archivo al importarse, establecer_valor_dinamico() y escribir_valor_en_archivo()
-- pasa por _verificar_criterio(). Si el criterio declara un rango de
sensibilidad numerico, el valor tiene que caer dentro: el rango y el valor se
defienden juntos en la memoria y no pueden contradecirse.

Al cambiar un criterio (por ejemplo, cuando llegue el SPT), se modifica UNA
linea de este archivo y todos los modulos se recalculan sin contradicciones.

Etiquetas
---------
    N    Exigencia normativa peruana vigente, numeral verificado
    N->  Valor normativo aplicado POR ANALOGIA. Requiere declaracion expresa
    S    Dato de sitio. Obtenido mediante un procedimiento normativo real
         (mapa, ensayo, medicion de campo) aplicado a las coordenadas o
         condiciones de ESTE proyecto. No es eleccion del proyectista ni
         analogia: es un hecho determinado, no portable a otro proyecto. En
         vez de sensibilidad declara TRAZABILIDAD obligatoria: el
         procedimiento exacto, la fuente, y si el dato aplica a todo el
         corredor o varia punto a punto
    C    Vacio normativo cubierto con fuente tecnica reconocida (FHWA, AASHTO)
    A    Sin norma ni fuente unica. Adopcion declarada + sensibilidad obligatoria

Las cinco se leen de mas determinado a mas elegido. [S] se lee entre [N->] y
[C] por lo mismo: el procedimiento que lo produce es normativo y propio (no
prestado, no ajeno), y lo unico local es la lectura.

Donde vive cada [S]
-------------------
Un dato de sitio unico para todo el corredor vive en `datos_sitio.py`
(PGA_roca_B, la zonificacion de E.030). Uno que varia punto a punto es una
columna del CSV (NF_profundidad_m, cbr_subrasante). Aqui solo quedan los [S]
que ademas siguen sujetos a un ensayo pendiente y por eso comparten tablero
con los criterios adoptados.
"""

import ast
import math
import numbers
import re
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from src.constantes_normativas import (
    CUNETA_DIMENSIONES_MINIMAS_T34,
    CUNETA_FILA_TRAPEZOIDAL_T34,
    MANNING_CAJON_IN_SITU_HDS5,
    NUMERAL_MANNING_CAJON_IN_SITU_HDS5,
)
from src.modelos import (
    ALCANCE_EXPEDIENTE,
    ALCANCE_PERFIL,
    CriterioPendienteError,
    DeCatalogo,
    DeEnsayo,
    DeTabla,
    Derivada,
    EnRango,
    Libre,
    ModoDeResolucion,
    Resolucion,
    modo_de,
)
from src.normativa import esquema as _esquema, registro as _registro_normativo
from src.criterios import (
    ARCHIVOS_DE_FICHAS,
    CRITERIOS_DE_FICHAS,
    ORIGEN_POR_CLAVE,
)
from src.criterios._base import (
    NIVEL_PERFIL,
    NIVEL_EXPEDIENTE,
    NIVELES,
    ETIQUETAS_DE_ELECCION,
    FORMA_INT,
    FORMA_FLOAT,
    FORMA_STR,
    FORMA_PAR_ORDENADO,
    FORMA_SERIE_DE_PARES,
    FORMA_DICT_CON_CAMPOS,
    FORMA_CATEGORIA,
    FORMA_SERIE_DE_CLAVES,
    FORMAS,
    Criterio,
    _tabla_recubrimiento_aashto_mm,
    _TABLA_RECUBRIMIENTO_AASHTO_MM,
    _n_manning_hdpe_hds5,
    _N_MANNING_HDPE_HDS5,
    N_MANNING_PARED_LISA_HDS5,
    _espesor_hdpe_de_aashto,
    _DECIMALES_DE_ESPESOR,
    _ESPESOR_HDPE_AASHTO,
    _topes_de_la_norma_de_producto,
    _TOPES_DE_LA_NORMA_DE_PRODUCTO,
    _CLAVES_DE_PLANCHA_TMC,
    _SIMBOLOS_SUCS_E050,
    SUPERFICIES_VIALES_WSDOT,
    _coeficientes_de_superficies_viales,
    _COEFICIENTES_VIALES_WSDOT,
    _VENTANA_KE_C2,
    REVESTIMIENTOS_CUNETA,
    _FIGURA_3_11_C_R_LEIDA,
    _FIGURA_3_11_C_R_EN_SI,
)
_RAIZ_PROYECTO = Path(__file__).resolve().parents[1]


def archivos_de_criterios() -> Tuple[Path, ...]:
    """Todos los archivos Fuente de los criterios (`criterios_adoptados.py` + `src/criterios/*.py`)."""
    return (Path(__file__).resolve(), *ARCHIVOS_DE_FICHAS)


def archivo_de_criterio(clave: str) -> Path:
    """Archivo exacto de `src/criterios/` donde esta definida la ficha `clave`."""
    if clave not in ORIGEN_POR_CLAVE:
        raise KeyError(f"'{clave}' no esta declarado en criterios_adoptados.py.")
    return ORIGEN_POR_CLAVE[clave]


def sha1_criterios() -> str:
    """
    Huella SHA-1 determinista del conjunto de criterios: mecanismo (`criterios_adoptados.py`)
    y todas las fichas y definiciones base (`src/criterios/*.py`), ordenadas por ruta POSIX.
    """
    import hashlib

    h = hashlib.sha1()
    pares = sorted(
        (ruta.resolve().relative_to(_RAIZ_PROYECTO).as_posix(), ruta.read_bytes())
        for ruta in archivos_de_criterios()
    )
    for rel_posix, datos in pares:
        h.update(rel_posix.encode("utf-8"))
        h.update(b"\0")
        h.update(datos)
        h.update(b"\0")
    return h.hexdigest()


CRITERIOS: Dict[str, Criterio] = dict(CRITERIOS_DE_FICHAS)

_USADOS: Set[str] = set()

# ---------------------------------------------------------------------------
# Declaracion en caliente (solo para la corrida actual)
# ---------------------------------------------------------------------------
# La GUI (pestana "Criterios") permite declarar un valor para un criterio con
# valor=None SIN tocar este archivo. El override vive solo en memoria de
# proceso: se pierde al cerrar la GUI y nunca se confunde con un valor [N]/[C]
# transcrito de una norma. Reescribir este archivo es una accion aparte,
# explicita, ver `escribir_valor_en_archivo`.
_OVERRIDES: Dict[str, Any] = {}


def establecer_valor_dinamico(clave: str, valor_nuevo: Any) -> None:
    """
    Declara, solo para esta corrida, el valor de un criterio.

    DE CUALQUIER CRITERIO QUE SE ELIJA, TAMBIEN DE UNO QUE YA TIENE VALOR EN
    EL ARCHIVO. Esta funcion nunca lo impidio --- no hay ni hubo comprobacion
    de `valor is None` aqui ---; quien lo impedia era la GUI, con un
    `puede_declarar` en `_al_seleccionar_criterio`.

    Esa asimetria dejaba al proyectista sin forma de TANTEAR: para probar un
    espesor distinto en seis cruces habia que reescribir
    `criterios_adoptados.py`, o sea cambiar el expediente para hacer un
    ensayo. Reescribirlo permanentemente si estaba permitido, lo que dejaba
    la puerta ancha abierta y la estrecha cerrada.

    LA UNICA EXCEPCION ES EL CRITERIO QUE NO SE ELIGE: el de resolucion
    `Derivada` (EXT-V-04). Su valor lo calcula el programa desde otras
    variables ya declaradas -- la tabla de recubrimiento AASHTO sale del
    registro normativo, no de quien corre el calculo -- y pisarlo por esta
    via ponia en la memoria una tabla que la fuente no imprime: medido en el
    dictamen de la auditoria externa, con la tabla pisada a 1.0 el
    recubrimiento de M9 baja de 40.64 a 25.4 mm. La ventana emergente ya lo
    protegia (`contenido_de_campo` devuelve `editable=False`); la pestaña 2
    de la GUI, `--declarar` y `declaracion.declarar_valor` entran por aqui,
    de modo que la guardia va aqui y cubre a los tres. Se rechaza con
    `ValueError`, como todo rechazo en la puerta de declaracion (SIS-E-05),
    y el mensaje dice de que se deriva y que hay que editar en su lugar.

    Pisar un valor de archivo NO es lo mismo que rellenar un vacio, y el
    proyecto lo distingue en los tres sitios donde se ve: `criterios_pisados_en_caliente`
    los separa, la memoria les da su propio bloque con lo que el archivo dice
    al lado, y la GUI los rotula «pisado (corrida)» y no «declarado (corrida)».
    Sin esas tres, permitir el tanteo seria permitir falsearlo en silencio.

    Pasa por la MISMA guardia que el archivo: se arma el Criterio que
    resultaria de esta declaracion y se somete a `_verificar_criterio`. Un
    valor fuera del rango de sensibilidad que el propio criterio declara se
    rechaza aqui, en el momento de declararlo, y no mas tarde durante el
    calculo.

    `valor_nuevo=None` se rechaza. No es una forma de retirar la
    declaracion -- para eso esta `quitar_valor_dinamico` -- y aceptarlo abria
    un default silencioso: `valor()` consulta `_OVERRIDES` ANTES de mirar si
    el valor es None, de modo que un override a None devolvia None en vez de
    lanzar `CriterioPendienteError`, que es justo lo que este archivo existe
    para impedir.

    POR QUE EL RECHAZO SALE COMO `ValueError` Y NO COMO `DatoInvalidoError`
    (SIS-E-05). La pregunta es legitima: CLAUDE.md define DatoInvalidoError
    como "el dato esta pero no puede ser", y un valor fuera del rango de
    sensibilidad encaja en esa frase. La respuesta es que lo que se rechaza
    aqui NO es un dato del expediente: es una DECLARACION que el proyectista
    acaba de teclear, y el rango contra el que se compara lo declara el
    propio criterio, en este archivo. `_verificar_criterio` es la misma
    guardia que corre AL IMPORTAR, donde un fallo significa que el archivo
    fuente esta mal escrito y ninguna corrida deberia empezar -- ahi
    `ValueError` es exactamente lo que corresponde --, y hacerla lanzar dos
    excepciones distintas segun por cual de sus tres caminos entre convertiria
    la guardia en dos guardias.
    Lo que la taxonomia persigue -- que la GUI distinga un problema del
    expediente de un fallo del programa -- se cumple igual y esta comprobado:
    los tres llamadores (`cli.main`, `gui/app.py::_aplicar_valor_corrida` y
    `::_guardar_valor_en_archivo`) capturan `(ValueError, KeyError)` a tres
    lineas y muestran el mensaje; ninguno deja escapar una traza. El contrato
    esta fijado por test en tests/test_criterios_adoptados.py.
    """
    verificar_declaracion(clave, valor_nuevo)
    _OVERRIDES[clave] = valor_nuevo


def verificar_declaracion(clave: str, valor_nuevo: Any) -> None:
    """
    La guardia de `establecer_valor_dinamico`, EN SECO: las mismas tres
    comprobaciones --- clave declarada, valor no None, criterio no derivado
    --- y la misma `_verificar_criterio`, sin escribir nada. Lanza
    `KeyError` o `ValueError` exactamente como la declaracion.

    Existe desde EXT-4 para `declaracion.restaurar_sesion(sustituir=True)`
    (EXT-A-02): abrir una sesion tiene que validar TODO el candidato antes de
    vaciar lo declarado, o un archivo con una clave mala dejaria el proceso
    a medias --- ni la obra anterior ni la nueva ---. No es un segundo camino
    de escritura: no toca `_OVERRIDES`, y `establecer_valor_dinamico` la
    llama para que las dos no puedan divergir.
    """
    if clave not in CRITERIOS:
        raise KeyError(
            f"'{clave}' no esta declarado en criterios_adoptados.py. "
            "Ningun parametro no normativo puede usarse sin declararse aqui."
        )
    if valor_nuevo is None:
        raise ValueError(
            f"No se puede declarar '{clave}' con valor None: una declaracion "
            "en caliente aporta un valor, no lo retira. Para retirarla, usa "
            "`quitar_valor_dinamico`; el criterio vuelve a bloquear el calculo"
        )
    resolucion = CRITERIOS[clave].resolucion
    if isinstance(resolucion, Derivada):
        raise ValueError(
            f"'{clave}' no se declara: se deriva de "
            f"{', '.join(resolucion.de)}; edite sus entradas. Un criterio de "
            "resolucion `Derivada` lo calcula el programa desde otras "
            "variables ya declaradas, y pisarlo en caliente pondria en la "
            f"memoria un valor que ninguna fuente sostiene ({resolucion.regla})"
        )
    _verificar_criterio(clave, replace(CRITERIOS[clave], valor=valor_nuevo))


def quitar_valor_dinamico(clave: str) -> None:
    """Retira la declaracion en caliente de un criterio (vuelve a bloquear)."""
    _OVERRIDES.pop(clave, None)


def limpiar_valores_dinamicos() -> None:
    """
    Retira todas las declaraciones en caliente de la corrida.

    TIENE UN LLAMADOR DE PRODUCCION DESDE EXT-4, y es abrir una sesion
    (SIS-B-22, reabierta en EXT-0 y cerrada aqui). Este docstring decia lo
    contrario --- «no tiene llamador de produccion, y es deliberado» --- con
    una premisa de S16.5 que S17 dejo atras al crear la sesion JSON: que la
    CLI es un proceso de un solo uso y que la GUI solo retira UNA clave. La
    sesion JSON es justamente el caso en que la GUI necesita retirar TODAS:
    abrir la sesion de la obra B tras declarar en la obra A dejaba las claves
    de A vivas, `estado_de_sesion()` de B las persistia y una clave de B sin
    procedencia heredaba la de A (EXT-A-02). El consumidor es
    `declaracion.restaurar_sesion(sustituir=True)`, que valida el candidato en
    seco, llama a esta funcion junto con el vaciado del libro de procedencias
    y vuelca solo lo aceptado. `sustituir=False` --- «Importar decisiones» ---
    no la llama, y esa es la diferencia entre abrir e importar.

    Sigue siendo tambien utilidad de banco de pruebas: la fixture autouse de
    `conftest.py` fotografia y repone el estado de cada test, y es el unico
    sitio de la suite que toca los registros privados.
    """
    _OVERRIDES.clear()


def valores_dinamicos() -> Dict[str, Any]:
    """Claves declaradas en caliente en esta corrida, sin registrar uso."""
    return dict(_OVERRIDES)


def valor(clave: str) -> Any:
    """Devuelve el valor del criterio y registra que fue usado."""
    if clave not in CRITERIOS:
        raise KeyError(
            f"'{clave}' no esta declarado en criterios_adoptados.py. "
            "Ningun parametro no normativo puede usarse sin declararse aqui."
        )
    _USADOS.add(clave)
    if clave in _OVERRIDES:
        return _OVERRIDES[clave]
    c = CRITERIOS[clave]
    if c.valor is None:
        # Detiene el calculo. NUNCA se devuelve un default silencioso: la GUI
        # muestra "falta declarar: <clave>" y el usuario resuelve el vacio.
        raise CriterioPendienteError(clave, concepto=c.concepto, fuente=c.fuente)
    return c.valor


def valor_si_declarado(clave: str) -> Optional[Any]:
    """
    El valor del criterio, o None si sigue sin declarar. NO lanza
    CriterioPendienteError.

    Es la lectura para los criterios OPCIONALES: los que refinan un valor que
    la norma ya fija, en vez de cubrir un vacio. Un criterio de vacio se lee
    con `valor()` y detiene el calculo mientras este vacio; uno opcional se
    lee con esta, y quien la llama aplica el valor normativo por defecto.
    Confundirlas en cualquiera de los dos sentidos es grave: `valor()` sobre
    un opcional bloquea un calculo que la norma sabe resolver, y esta sobre
    uno de vacio rellena el vacio en silencio, que es el peor error del
    proyecto.

    Un criterio sin valor no se registra como usado: no se aplico a nada y no
    hay uso que declarar en M11. En cuanto reciba valor -- en el archivo o en
    caliente -- empieza a devolverlo Y a registrarse.
    """
    if clave not in CRITERIOS:
        raise KeyError(
            f"'{clave}' no esta declarado en criterios_adoptados.py. "
            "Ningun parametro no normativo puede usarse sin declararse aqui."
        )
    if clave in _OVERRIDES:
        _USADOS.add(clave)
        return _OVERRIDES[clave]
    if CRITERIOS[clave].valor is None:
        return None
    return valor(clave)


def criterio(clave: str) -> Criterio:
    """Devuelve el objeto completo, sin registrar uso (para reportes)."""
    return CRITERIOS[clave]


def criterios_sin_valor() -> List[str]:
    """
    Claves cuyo valor es None y sin declaracion en caliente: vacios que
    detienen el calculo si se invocan. M11 los imprime en bloque aparte
    (Sec. 0.7) y la GUI los usa para avisar antes de correr, no despues de
    la excepcion.

    Los criterios OPCIONALES quedan FUERA: su `valor=None` no detiene nada
    -- el consumidor aplica el valor normativo por defecto -- y anunciarlos
    como vacios bloqueantes le decia al revisor de la memoria que un
    refinamiento que nadie tiene obligacion de declarar era un hueco del
    expediente. Se listan aparte, en `criterios_opcionales_sin_declarar`.
    """
    return sorted(
        k for k, c in CRITERIOS.items()
        if c.valor is None and not c.opcional and k not in _OVERRIDES
    )


def criterios_opcionales_sin_declarar() -> List[str]:
    """
    Criterios opcionales que nadie declaro: el calculo corre con el valor
    normativo por defecto. NO son vacios y no bloquean nada; se informan
    para que la memoria diga que el refinamiento estaba disponible y no se
    adopto, que es distinto de no haberlo mirado.
    """
    return sorted(
        k for k, c in CRITERIOS.items()
        if c.opcional and c.valor is None and k not in _OVERRIDES
    )


def escribir_valor_en_archivo(clave: str, valor_nuevo: Any,
                              ruta: Optional[str] = None) -> None:
    """
    Reescribe, EN EL ARCHIVO FUENTE, el ``valor=`` del criterio `clave` por
    `valor_nuevo`. Accion permanente y distinta de
    `establecer_valor_dinamico`: se usa solo cuando el usuario confirma de
    forma explicita que quiere dejar de tratar el criterio como pendiente
    (la GUI pide confirmacion aparte antes de llamarla).

    REESCRIBE CUALQUIER VALOR, NO SOLO `None` (SIS-A-14). El docstring decia
    «el ``valor=None``» y el patron es `valor=)([^,\\n]*)(,)`, que casa con lo
    que haya: un criterio YA declarado se puede volver a escribir por esta
    misma via, y el boton de la GUI esta disponible para toda fila, no solo
    para las pendientes. Es deliberado --- corregir un valor adoptado es tan
    legitimo como declararlo por primera vez, y obligar a editar el archivo a
    mano para eso empujaria a saltarse la guardia --- y lo que faltaba era
    decirlo. Se declara aqui porque la frase anterior describia una funcion
    mas estrecha que la que existe, y quien la leyera creeria tener una
    proteccion contra la sobreescritura que el codigo no da.

    PERO NO REESCRIBE CUALQUIER FORMA DE VALOR, y esto es un limite del
    patron, no una decision: `valor=)([^,\n]*)(,)` se corta en la PRIMERA
    coma. Un valor cuyo literal lleve comas --- la tupla de `F_pga`, el dict
    de `hds5_embocadura_hdpe` --- no cabe en esa mordida, y hasta S19 el
    intento DESTRUIA el archivo y volvia sin excepcion. Ahora se rechaza con
    `ValueError` y el archivo no se toca: la comprobacion es `ast.parse` sobre
    el texto resultante, ANTES de escribir. Esos criterios se editan a mano.

    LO QUE NO TOCA, y ahi si es estrecha a proposito: ningun otro campo del
    Criterio (etiqueta, justificacion, fuente, sensibilidad, resolucion). Esos
    describen POR QUE se adopto el valor y se revisan a mano; reescribir el
    numero y dejar la justificacion del anterior es la forma de que el archivo
    afirme una cosa y valga otra. La GUI advierte de los TRES primeros en su
    confirmacion (`gui/app.py::_guardar_valor_en_archivo`), y es advertencia,
    no impedimento: el revisor decide.
    """
    import re

    if clave not in CRITERIOS:
        raise KeyError(f"'{clave}' no esta declarado en criterios_adoptados.py.")
    if isinstance(CRITERIOS[clave].resolucion, Derivada):
        # El mismo rasero que `establecer_valor_dinamico` (EXT-V-04): una
        # tabla derivada del registro no se edita escribiendo un numero en
        # su lugar, ni en caliente ni en el archivo.
        raise ValueError(
            f"'{clave}' no se escribe: se deriva de "
            f"{', '.join(CRITERIOS[clave].resolucion.de)}; edite sus entradas")

    # La misma guardia que el archivo y que la declaracion en caliente, y
    # ANTES de tocar el disco: un valor que la guardia rechaza no llega a
    # escribirse, para que el archivo fuente nunca quede en un estado que su
    # propio import rechazaria.
    _verificar_criterio(clave, replace(CRITERIOS[clave], valor=valor_nuevo))

    ruta_archivo = ruta or str(archivo_de_criterio(clave))
    texto = Path(ruta_archivo).read_text(encoding="utf-8")

    patron = re.compile(
        r'("' + re.escape(clave) + r'":\s*Criterio\(\s*\n\s*valor=)([^,\n]*)(,)'
    )
    texto_nuevo, n = patron.subn(
        lambda m: m.group(1) + repr(valor_nuevo) + m.group(3), texto, count=1,
    )
    if n == 0:
        raise ValueError(
            f"No se encontro el bloque 'valor=' de '{clave}' en {ruta_archivo}. "
            "No se modifico el archivo."
        )

    # EL ARCHIVO RESULTANTE TIENE QUE SEGUIR SIENDO PYTHON. Sin esta guardia
    # la funcion DESTRUIA el archivo y volvia sin excepcion, que es la peor
    # combinacion posible: el patron `valor=)([^,\n]*)(,)` se corta en la
    # PRIMERA coma, de modo que un valor de UNA LINEA que lleve comas
    # --- `("C", "D", "E")` de `F_pga`, o el dict de `hds5_embocadura_hdpe` ---
    # quedaba partido, con el resto del literal colgando, y
    # `criterios_adoptados.py` dejaba de importar. La GUI, que solo mira si
    # hubo excepcion, pintaba «escrito» en verde; y como despues se refresca
    # `CRITERIOS` en memoria, la sesion en curso seguia funcionando y la
    # corrupcion no aparecia hasta el siguiente arranque.
    #
    # El proyecto YA conocia este modo de fallo: SIS-F-19 lo describe con
    # estas palabras --- «lo dejaria a medias y con el resto del literal
    # colgando» --- y su ValueError solo cubria los valores MULTILINEA. Los de
    # una linea con comas caian justo en el hueco. Encontrado al refutar el
    # cierre de SIS-A-14, que habia declarado «reescribe cualquier valor» sin
    # comprobar este limite.
    try:
        ast.parse(texto_nuevo, filename=str(ruta_archivo))
    except SyntaxError as exc:
        raise ValueError(
            f"Reescribir 'valor=' de '{clave}' dejaria {ruta_archivo} sin "
            f"poder importarse ({exc.msg}, linea {exc.lineno}). El valor "
            "actual ocupa mas de lo que el patron alcanza a ver --- una tupla "
            "o un dict con comas --- y hay que editarlo a mano. NO se "
            "modifico el archivo."
        ) from exc

    Path(ruta_archivo).write_text(texto_nuevo, encoding="utf-8")

    # El archivo ya quedo escrito; se refleja tambien en memoria para que el
    # resto de esta sesion (GUI o CLI en curso) vea el valor definitivo sin
    # tener que reiniciar el proceso, y se retira el override en caliente:
    # ya no hace falta, el valor "real" es ahora este.
    CRITERIOS[clave] = replace(CRITERIOS[clave], valor=valor_nuevo)
    _OVERRIDES.pop(clave, None)


def declaracion_de(clave: str):
    """
    El objeto DECLARADO de `clave`, venga de este archivo o de datos_sitio.py.

    SIS-A-05. `servicio._bloqueo` y `M11.criterios_bloqueantes` resolvian toda
    clave con `criterio()`, y `CriterioPendienteError` no la levanta solo este
    archivo: `datos_sitio.valor` levanta LA MISMA excepcion cuando un [S] de
    corredor todavia no se ha leido -- deliberadamente, porque el error que se
    evita es el mismo. Con un [S] pendiente, los dos consumidores salian por
    `KeyError`: un fallo de PROGRAMA en el codigo que existe justamente para
    convertir un problema del expediente en una fila del informe.

    Hoy es inalcanzable porque los datos de sitio de corredor tienen valor,
    pero eso es una propiedad del expediente de este mes, no del codigo: el
    dia que se añada un [S] pendiente -- y el proyecto tiene el mecanismo para
    ello -- la corrida moriria con traza en vez de listar el bloqueo.

    Los dos tipos declaran los mismos campos que el informe necesita
    (`etiqueta`, `concepto`, `fuente`, `reemplazado_por`), de modo que el
    consumidor no tiene que saber de cual de los dos archivos vino.
    """
    if clave in CRITERIOS:
        return criterio(clave)
    from src import datos_sitio as ds

    if clave in ds.DATOS_SITIO:
        return ds.dato(clave)
    raise KeyError(
        f"'{clave}' no esta declarado ni en criterios_adoptados.py ni en "
        "datos_sitio.py. Ningun valor no normativo puede usarse sin "
        "declararse en uno de los dos."
    )


# QUE NIVELES NECESITA DECLARADOS CADA ALCANCE DE CORRIDA.
#
# La correspondencia es 1:1 con el nombre y aun asi se escribe, porque son dos
# cosas distintas y el proyecto ya lo tiene dicho: el NIVEL es propiedad del
# CRITERIO y el ALCANCE lo es de la CORRIDA. Escribir el diccionario deja el
# puente a la vista en vez de esconderlo en una comparacion de cadenas que
# parece una coincidencia de nombres.
#
# EL "" ESTA EN LAS DOS FILAS A PROPOSITO. Hoy no hay ningun criterio sin
# nivel --- los trece que quedaban se midieron en S21 ---, pero uno nuevo
# puede nacer sin clasificar, y entonces el filtro tiene que MOSTRARLO. Un
# filtro que oculta lo que no sabe clasificar es la unica forma de fallo que
# no se puede permitir: esconde un criterio sin que nadie se entere, que es
# exactamente lo contrario de lo que hace el resto del programa.
NIVELES_DEL_ALCANCE: Dict[str, Tuple[str, ...]] = {
    ALCANCE_PERFIL: (NIVEL_PERFIL, ""),
    ALCANCE_EXPEDIENTE: (NIVEL_PERFIL, NIVEL_EXPEDIENTE, ""),
}


def criterios_del_alcance(alcance: str) -> Tuple[str, ...]:
    """
    Los criterios que una corrida de ese alcance PUEDE necesitar declarados.

    Es el filtro de alcance de la pestana de criterios, y no calcula nada: lee
    `Criterio.nivel`, que es el campo que ya responde a esta pregunta y que
    `tests/test_nivel_medido.py` contrasta contra corridas reales en las dos
    direcciones. Deducirlo aqui de los consumidores --- la otra via
    disponible --- seria una segunda clasificacion que puede contradecir a la
    primera, y ademas la peor de las dos: la derivacion estatica de
    `variables_entrada` es una ESTIMACION y tuvo dos falsos negativos medidos
    (ver `_consumo_por_modulo`).

    NO ES UN PERMISO NI UNA PODA. Lo que queda fuera sigue existiendo, sigue
    contando en el recuento de la pestana y se puede declarar igual: el
    alcance de perfil no prohibe declarar un criterio del expediente, solo
    dice que esta corrida no lo va a invocar.
    """
    if alcance not in NIVELES_DEL_ALCANCE:
        raise ValueError(
            f"alcance desconocido: '{alcance}'. Los declarados son "
            + ", ".join(sorted(NIVELES_DEL_ALCANCE))
        )
    niveles = NIVELES_DEL_ALCANCE[alcance]
    return tuple(clave for clave in sorted(CRITERIOS)
                 if CRITERIOS[clave].nivel in niveles)


def criterios_usados() -> List[str]:
    """
    Claves que el calculo invoco, en orden alfabetico. Es la misma informacion
    que `reporte_criterios(solo_usados=True)` imprime como texto, expuesta como
    lista para el consumidor que arma su propio bloque (cli.py la vuelca al
    JSON). Existe para que nadie tenga que leer `_USADOS` desde fuera.

    DESDE EXT-4 ES EL REGISTRO DE LA CORRIDA EN CURSO, no del proceso:
    `servicio.correr` lo vacia al entrar (`reiniciar_usos`) y lo fotografia al
    salir en `Informe.contexto`. Los exportadores leen la foto, no esto.
    """
    return sorted(_USADOS)


def reiniciar_usos() -> None:
    """
    Vacia el registro de usos. Lo llama `servicio.correr` AL ENTRAR, y es lo que
    cierra PC-09: el registro era de proceso y nunca se vaciaba, de modo que
    en la GUI --- o en cualquier consumidor que corra dos veces --- la
    memoria de la segunda corrida imprimia como usados los criterios de la
    primera (medido: una memoria de perfil tras una corrida de expediente
    listaba seis criterios de Fase 9 como usados con la Fase 9 diferida).

    Es publica para que la suite tampoco tenga que tocar `_USADOS`: hasta
    EXT-4 nueve archivos de tests lo vaciaban y reponian a mano, 27 veces.
    """
    _USADOS.clear()


def declarado_en_caliente(clave: str) -> bool:
    """
    True si el valor que GOBIERNA el calculo entro por
    `establecer_valor_dinamico` y no esta en el archivo.

    Es la mitad que faltaba de `criterio_efectivo`: el valor efectivo dice
    QUE numero se uso y esta dice DE DONDE vino. Separadas porque la memoria
    tiene que imprimir las dos cosas -- un override no es un valor
    transcrito, y una memoria que no distinga las dos procedencias declara
    como cerrado lo que solo vale para esa corrida.
    """
    if clave not in CRITERIOS:
        raise KeyError(
            f"'{clave}' no esta declarado en criterios_adoptados.py."
        )
    return clave in _OVERRIDES


def criterios_declarados_en_caliente() -> List[str]:
    """
    Claves con valor declarado SOLO para esta corrida, en orden alfabetico.

    No son vacios (`criterios_sin_valor` las excluye, y con razon: el calculo
    tiene valor con que correr) y tampoco son valores del archivo. Sin esta
    lista se caian entre las dos sillas: la memoria las imprimia como
    pendientes y el bloque de pendientes no las mostraba.
    """
    return sorted(_OVERRIDES)


def criterios_pisados_en_caliente() -> List[str]:
    """
    Los declarados en caliente que PISAN un valor del archivo, no un vacio.

    Subconjunto de `criterios_declarados_en_caliente`, y la distincion no es
    de matiz: rellenar un vacio deja el expediente donde estaba --- faltaba un
    numero y se puso --- mientras que pisar sustituye una decision ya tomada y
    transcrita, que sigue en el archivo diciendo otra cosa. Un lector de la
    memoria tiene que poder ver esa segunda, con los DOS valores delante; si
    no, tantear y falsear se imprimen igual.
    """
    return sorted(c for c in _OVERRIDES if CRITERIOS[c].valor is not None)


def criterio_efectivo(clave: str) -> Criterio:
    """
    El Criterio TAL COMO GOBIERNA el calculo: con el valor declarado en
    caliente si lo hay, y con el del archivo si no. No registra uso.

    `criterio()` devuelve lo que dice el ARCHIVO y por eso no sirve para
    declarar en la memoria lo que el calculo hizo: un criterio declarado en
    caliente se imprimia como "sin valor declarado" mientras su override
    gobernaba los numeros de esa misma pagina. Todo reporte lee de aqui;
    `criterio()` queda para quien necesite exactamente el texto del archivo
    (por ejemplo, para contrastarlo con el override).
    """
    c = criterio(clave)
    if clave in _OVERRIDES:
        return replace(c, valor=_OVERRIDES[clave])
    return c


def criterios_con_verificacion_pendiente() -> List[str]:
    """
    Los que tienen valor pero una verificacion documental abierta: hermano de
    `datos_sitio.datos_con_verificacion_pendiente()`.

    Las dos dataclases comparten el campo `verificacion_pendiente` y solo una
    exponia la consulta, de modo que un consumidor del JSON veia que datos de
    sitio quedaban sin cerrar documentalmente y no veia que criterios. El
    valor efectivo cuenta: un criterio declarado en caliente sobre un
    criterio con verificacion abierta sigue teniendola abierta.
    """
    return sorted(
        k for k in CRITERIOS
        if criterio_efectivo(k).valor is not None
        and CRITERIOS[k].verificacion_pendiente
    )


def criterios_sin_consumidor() -> List[str]:
    """
    Los que declaran por que ningun modulo de produccion los invoca.

    La razon se escribe UNA vez, en el campo `sin_consumidor` del propio
    criterio, y de ahi la leen la memoria y quien audite el archivo. Antes
    vivia repartida entre la auditoria v9, el manifiesto y los docstrings de
    los modulos que NO los llaman, que es el peor sitio para buscarla.
    """
    return sorted(k for k, c in CRITERIOS.items() if c.sin_consumidor)



# ---------------------------------------------------------------------------
# Coherencia de las etiquetas
# ---------------------------------------------------------------------------

ETIQUETAS_VALIDAS = ("N", "N->", "S", "C", "A")

# Salida que todo mensaje de rango debe ofrecer. El error no es "tu numero
# esta mal": es que el numero y el rango se contradicen, y quien declaro el
# rango puede haber sido el equivocado.
_SALIDA_RANGO = (
    "si el rango ya no es el correcto, corrigelo en criterios_adoptados.py; "
    "el rango y el valor se defienden juntos en la memoria"
)


# Un ancla es "<archivo>.md Sec. <n>", relativo a docs/.
_ANCLA = re.compile(r"^(?P<doc>[\w.\-]+\.md)\s+Sec\.\s+(?P<sec>[\w.\-]+)$")
_DOCS = Path(__file__).resolve().parents[1] / "docs"


@lru_cache(maxsize=None)
def _secciones_de(documento: str) -> frozenset:
    """
    Titulos de seccion de un documento de docs/, como anclas ("14.a", "9").

    Se cachea porque la guardia corre en cada declaracion en caliente y el
    documento no cambia dentro de una corrida. Si el archivo no existe
    devuelve None, y quien llama lo distingue de "existe pero no tiene esa
    seccion": son dos errores distintos y el mensaje lo dice.
    """
    ruta = _DOCS / documento
    if not ruta.is_file():
        return None
    return frozenset(
        m.group(1) for m in re.finditer(
            r"^#{2,4}\s+([\w.\-]+?)\.?\s",
            ruta.read_text(encoding="utf-8"), re.MULTILINE)
    )


def _verificar_ancla_de_vacio(clave: str, ancla: str) -> None:
    """
    El ancla tiene que RESOLVER, no solo estar bien escrita.

    Un valor que dice cubrir un vacio verificado y apunta a un registro que no
    existe es peor que uno que no dice nada: afirma una diligencia que nadie
    hizo. Se comprueba al importar, igual que el test de referencias comprueba
    los archivo:linea del manifiesto.
    """
    m = _ANCLA.match(ancla.strip())
    if not m:
        raise ValueError(
            f"'{clave}' declara vacio_verificado={ancla!r}, que no tiene la "
            "forma '<documento>.md Sec. <n>' (por ejemplo "
            "'manifiesto_citas.md Sec. 14.a'). El ancla existe para que la "
            "memoria pueda mandar al revisor al registro: si no resuelve, no "
            "sirve"
        )
    documento, seccion = m.group("doc"), m.group("sec")
    secciones = _secciones_de(documento)
    if secciones is None:
        raise ValueError(
            f"'{clave}' declara vacio_verificado={ancla!r} pero "
            f"docs/{documento} no existe"
        )
    if seccion not in secciones:
        raise ValueError(
            f"'{clave}' declara vacio_verificado={ancla!r} pero "
            f"docs/{documento} no tiene una Sec. {seccion}. El vacio que este "
            "valor dice cubrir no esta registrado: o se registra, o el campo "
            "no se declara"
        )


# ---------------------------------------------------------------------------
# El modo de resolucion (Sec. 4.3 del plan v12)
# ---------------------------------------------------------------------------

# Los cinco rangos de `normativa/esquema.py` §7. Se importan por NOMBRE y no
# por el alias `RangoNormativo` porque `isinstance` no acepta un `Union`, y
# porque la lista explicita hace visible en revision que la familia es cerrada.
_RANGOS_NORMATIVOS = (_esquema.IntervaloAdmisible, _esquema.TechoUnico,
                      _esquema.PisoUnico, _esquema.ConjuntoDeMaximos,
                      _esquema.BandaDeInterpolacion)


@lru_cache(maxsize=1)
def _registro():
    """
    El registro normativo, armado una sola vez. La guardia lo necesita para
    comprobar que una tabla citada por una `resolucion` EXISTE: un
    `DeTabla` que apunta a una tabla que nadie transcribio prometeria una
    ventana que no se puede pintar.
    """
    return _registro_normativo.construir()


def verificar_resolucion(clave: str, r: Resolucion) -> ModoDeResolucion:
    """
    Forma de la resolucion y, cuando apunta al registro, que lo apuntado
    exista. Es el criterio de salida de la Sec. 4.3 hecho guardia:

        ninguna variable sin modo
        ningun `DeTabla` sin tabla existente en el registro
        ningun `EnRango` sin rango con semantica declarada

    El tercero se comprueba por TIPO: la celda del registro tiene que ser uno
    de los cinco rangos de `normativa/esquema.py` §7, donde la semantica ES el
    tipo. Un float suelto no es un rango, y un rango sin semantica no existe.

    ES PUBLICA Y VIVE AQUI, aunque no sea exclusiva de los criterios, por dos
    razones: aqui esta la poblacion mas grande de las tres (59 de las 83
    variables de entrada) y aqui ya esta el registro, del que este archivo
    depende por `constantes_normativas`. `variables_entrada.py` la reutiliza
    para las 17 columnas del CSV en vez de escribir una segunda copia que
    pudiera divergir. Las reglas que valen SOLO para un criterio -- que
    `Libre.opciones` este vacio, que un `de_ensayo` no lleve sensibilidad, que
    el rotulo `de_catalogo` y el modo digan lo mismo -- no estan aqui sino en
    `_verificar_criterio`.

    Devuelve el modo, para que quien llame no tenga que volver a deducirlo.
    """
    modo = modo_de(r)          # levanta TypeError si no es de la familia

    if isinstance(r, Libre):
        if not r.que_lo_fija:
            raise ValueError(
                f"'{clave}' se resuelve `libre` y no dice QUIEN pone el "
                "numero. Sin eso la ventana ofrece un campo vacio y la "
                "memoria no puede escribir su procedencia"
            )

    elif isinstance(r, DeTabla):
        if not r.tablas:
            raise ValueError(f"'{clave}' se resuelve `de_tabla` y no cita "
                             "ninguna tabla")
        if not r.que_elige:
            raise ValueError(f"'{clave}' se resuelve `de_tabla` y no dice "
                             "QUE se elige sobre la tabla")
        if (r.fila_id or r.columna_id) and len(r.tablas) != 1:
            raise ValueError(
                f"'{clave}' fija fila o columna y cita {len(r.tablas)} "
                "tablas: no se sabe de cual. La fila y la columna solo "
                "tienen sentido con una tabla"
            )
        for tabla_id in r.tablas:
            tabla = _tabla_del_registro(clave, tabla_id)
            if r.fila_id:
                try:
                    tabla.fila(r.fila_id)
                except KeyError:
                    raise ValueError(
                        f"'{clave}' apunta a la fila '{r.fila_id}' de "
                        f"'{tabla_id}', que la tabla no tiene"
                    ) from None
            if r.columna_id:
                try:
                    tabla.columna(r.columna_id)
                except KeyError:
                    raise ValueError(
                        f"'{clave}' apunta a la columna '{r.columna_id}' de "
                        f"'{tabla_id}', que la tabla no tiene"
                    ) from None
        if r.elegido_por and r.elegido_por not in CRITERIOS:
            raise ValueError(
                f"'{clave}' dice que la fila la elige '{r.elegido_por}', que "
                "no es un criterio declarado"
            )

    elif isinstance(r, EnRango):
        tabla = _tabla_del_registro(clave, r.tabla_id)
        try:
            celda = tabla.fila(r.fila_id).valores[r.columna_id]
        except KeyError:
            raise ValueError(
                f"'{clave}' apunta a la celda "
                f"({r.fila_id}, {r.columna_id}) de '{r.tabla_id}', que la "
                "tabla no tiene"
            ) from None
        if not isinstance(celda, _RANGOS_NORMATIVOS):
            raise ValueError(
                f"'{clave}' se resuelve `en_rango` y la celda "
                f"({r.fila_id}, {r.columna_id}) de '{r.tabla_id}' es "
                f"{type(celda).__name__}, no un rango. Un `en_rango` sin "
                "rango con SEMANTICA declarada es lo que deja a la ventana "
                "pintar como minimo el primero de dos maximos (NOR-HID-04)"
            )
        if not r.que_acota:
            raise ValueError(f"'{clave}' se resuelve `en_rango` y no dice "
                             "QUE acota el rango")

    elif isinstance(r, Derivada):
        if not r.de or not r.regla:
            raise ValueError(
                f"'{clave}' se resuelve `derivada` y no declara de que se "
                "deriva o con que regla. La ventana no lo deja editar: si no "
                "dice de donde sale, el usuario se queda sin nada que leer"
            )

    elif isinstance(r, DeEnsayo):
        if not r.ensayo or not r.trazabilidad_exigida:
            raise ValueError(
                f"'{clave}' se resuelve `de_ensayo` y no declara el "
                "procedimiento o la trazabilidad que hay que exigir. Un dato "
                "determinado se defiende con la lectura que lo reproduce"
            )

    elif isinstance(r, DeCatalogo):
        if not r.advertencia:
            raise ValueError(
                f"'{clave}' se resuelve `de_catalogo` y no lleva "
                "advertencia. El rotulo es todo el punto del modo: sin el, "
                "un tope de proveedor se lee como exigencia normativa "
                "(NOR-PRO-01, NOR-PRO-02)"
            )
        if r.catalogo_id not in _ids_de_catalogo():
            raise ValueError(
                f"'{clave}' cita el catalogo '{r.catalogo_id}', que no esta "
                f"en el registro (hay: {sorted(_ids_de_catalogo())})"
            )

    return modo


def _tabla_del_registro(clave: str, tabla_id: str):
    try:
        return _registro().tabla(tabla_id)
    except KeyError:
        raise ValueError(
            f"'{clave}' declara que su valor sale de la tabla '{tabla_id}', "
            "que no esta en el registro normativo. Una tabla que no esta "
            "transcrita no se puede mostrar entera, que es lo que el modo "
            "`de_tabla` promete"
        ) from None


def _ids_de_catalogo() -> frozenset:
    return frozenset(c.id for c in _registro().catalogos)


def _es_real(x: Any) -> bool:
    """
    Un numero real de verdad. `bool` queda fuera a proposito: en Python es
    subclase de `int`, y sin esta exclusion `True` pasaria por un 1.0 valido
    dentro de cualquier rango que contenga al 1.
    """
    return isinstance(x, numbers.Real) and not isinstance(x, bool)


def _rango_numerico(sensibilidad: Any) -> Optional[Tuple]:
    """
    La sensibilidad si es un rango numerico validable; None si es SIMBOLICA.

    La discriminacion es por FORMA, nunca por nombre de criterio: una
    2-tupla de reales se valida entera, y cualquier otra cosa no vacia -- una
    cadena como "2*phi_relleno_trasdos/3", un invocable, una tupla con un
    extremo simbolico -- se acepta tal cual y no se toca. No se hace `float()`
    sobre ella, no se coacciona a un formato que no tiene y no se descarta en
    silencio: se declara, se imprime en el reporte como esta escrita, y el
    analisis de sensibilidad la pide aparte.
    """
    if isinstance(sensibilidad, tuple) and all(_es_real(x) for x in sensibilidad):
        return sensibilidad
    return None


def _verificar_sensibilidad(clave: str, c: Criterio) -> None:
    """
    Forma del rango, orden de sus extremos, y el valor dentro de el.

    TRES FORMAS DE VENTANA, y la tercera llego en EXT-1 (EXT-V-05):

      * un par numerico (min, max): se valida entero, y el valor -- escalar o
        PAR -- tiene que caer dentro;
      * una ventana SIMBOLICA (una cadena, una tupla con un extremo
        simbolico): se declara, se imprime y no se evalua;
      * un dict {campo: (min, max)} para los criterios cuyo valor es un dict
        ('seccion_receptor' es el primero). Hasta EXT-1 su ventana estaba
        escrita EN PROSA -- «n: 0.025 a 0.035» -- y por eso caia en la forma
        simbolica: `n='0.03'` llegaba a M3 como texto y salia TypeError,
        `n=True` valia 1, un tirante x5 pasaba y una clave desconocida se
        ignoraba. La ventana por campo se evalua en `_verificar_dict`.

    Y UN PAR ES UN PAR (PC-01): cuando el valor es una tupla o una lista bajo
    un rango numerico, se exige que tenga DOS extremos y que esten en orden.
    `n_manning_hdpe = (0.013, 0.010)` pasaba -- cada extremo cae en la
    ventana -- y movia todas las velocidades de M3->M5->M6 al lado no
    conservador: con Q = 1.167 m3/s y S = 0.020 el par nominal descarta el
    HDPE por V3 y el invertido aprueba 0.90 m. El «no validamos el orden» de
    `progresion_de_cajon` es un argumento de dos dimensiones que no se
    traslada a un par escalar que la hoja de ruta (Sec. 4.1) presupone
    ordenado: n_max para capacidad, n_min para velocidad.
    """
    s = c.sensibilidad
    if s is None:
        return
    if not s:
        raise ValueError(
            f"'{clave}' declara una sensibilidad vacia ({s!r}). O declara el "
            f"rango que se pudo elegir, o no declares el campo"
        )

    if isinstance(s, dict):
        _verificar_dict(clave, c)
        return

    rango = _rango_numerico(s)
    if rango is None:
        return              # simbolica: declarada, respetada, no evaluada

    if len(rango) != 2:
        raise ValueError(
            f"'{clave}' declara una sensibilidad de {len(rango)} extremos "
            f"({s!r}). Un rango numerico tiene dos: minimo y maximo"
        )
    minimo, maximo = rango
    if minimo > maximo:
        raise ValueError(
            f"'{clave}' tiene el rango de sensibilidad invertido ({s!r}): "
            f"el minimo {minimo!r} es mayor que el maximo {maximo!r}"
        )

    if c.valor is None:
        return              # sin valor no hay nada que contrastar

    # El valor puede ser un escalar o una tupla (la regla de doble n de
    # Sec. 4.1.1: `n_manning_hdpe` es un par, no un numero). En los dos casos
    # se exige que CADA numero caiga dentro del rango declarado.
    es_par = isinstance(c.valor, (tuple, list))
    candidatos = tuple(c.valor) if es_par else (c.valor,)
    if es_par and len(candidatos) != 2:
        raise ValueError(
            f"'{clave}' declara {c.valor!r}, de {len(candidatos)} elementos, "
            f"bajo un rango de sensibilidad numerico {s!r}. Un valor en forma "
            f"de secuencia es un PAR (minimo, maximo) -- la regla de doble n "
            f"de la Sec. 4.1 -- y tiene exactamente dos extremos"
        )
    for x in candidatos:
        if not _es_real(x):
            raise ValueError(
                f"'{clave}' declara un rango de sensibilidad numerico {s!r} "
                f"pero su valor es {c.valor!r}, que no es un numero. "
                f"Un rango numerico no puede defender un valor que no lo es: "
                f"{_SALIDA_RANGO}"
            )
        if not minimo <= x <= maximo:
            raise ValueError(
                f"'{clave}' tiene el valor {c.valor!r} fuera del rango de "
                f"sensibilidad que el mismo declara, {s!r} "
                f"(el extremo infractor es {x!r}). {_SALIDA_RANGO}"
            )
    if es_par and not candidatos[0] <= candidatos[1]:
        raise ValueError(
            f"'{clave}' declara el par {c.valor!r} INVERTIDO: el primer "
            f"extremo es el minimo y el segundo el maximo (regla de doble n, "
            f"Sec. 4.1: n_max para capacidad, n_min para velocidad). Con el "
            f"par al reves todas las velocidades salen del lado no "
            f"conservador sin que ninguna verificacion lo note"
        )


# --- VE-7 lote B, B11 (ficha VE5-CAT-02; decision del consultor Fable,
# triaje VE-7, 2026-11-20) --- El PISO de un campo de la ventana que baja
# cuando otro campo del mismo valor lo dice: {clave: {campo: (campo que lo
# condiciona, piso)}}. Hoy uno: la profundidad de 'seccion_cuneta' baja a
# 0.30 con fondo, el minimo de la trapezoidal de la fila de mas de 3000
# mm/año de la Tabla Nº 34 (nota «*»). Las esquinas de la ventana siguen
# siendo valores validos: el piso propio del campo no cambia.
_PISO_CONDICIONADO = {
    "seccion_cuneta": {
        "profundidad_m": ("ancho_fondo_m", CUNETA_DIMENSIONES_MINIMAS_T34[
            CUNETA_FILA_TRAPEZOIDAL_T34][0]),
    },
}


def _piso_condicionado(clave: str, campo: str, valor: dict,
                       minimo: float) -> float:
    """El piso del campo con `_PISO_CONDICIONADO`: el alternativo si el
    campo que lo condiciona es un real positivo, el de la ventana si no."""
    regla = _PISO_CONDICIONADO.get(clave, {}).get(campo)
    if regla is None:
        return minimo
    condicion, piso = regla
    x = valor.get(condicion)
    return piso if _es_real(x) and x > 0 else minimo


def _verificar_dict(clave: str, c: Criterio) -> None:
    """
    La ventana ESTRUCTURADA {campo: (min, max)} de un criterio de valor dict
    (EXT-V-05).

    Se exige que la ventana misma este bien formada -- cada campo un par
    numerico ordenado -- y, si hay valor, que el valor sea un dict con
    EXACTAMENTE los campos de la ventana: una clave desconocida es una errata
    que antes se ignoraba, y una clave que falta es un campo que M3 iba a
    pedir con KeyError. Cada campo se contrasta con `_es_real` -- un texto o
    un bool no son numeros -- y con su propio rango.
    """
    s = c.sensibilidad
    for campo, rango in s.items():
        par = _rango_numerico(rango)
        if par is None or len(par) != 2:
            raise ValueError(
                f"'{clave}' declara para el campo {campo!r} la ventana "
                f"{rango!r}, que no es un par numerico (minimo, maximo). Una "
                f"sensibilidad estructurada lleva un par por campo"
            )
        if par[0] > par[1]:
            raise ValueError(
                f"'{clave}' tiene invertida la ventana del campo {campo!r} "
                f"({rango!r}): el minimo es mayor que el maximo"
            )
    if c.valor is None:
        return
    if not isinstance(c.valor, dict):
        raise ValueError(
            f"'{clave}' declara una sensibilidad por campo ({sorted(s)}) y su "
            f"valor es {c.valor!r}, que no es un dict con esos campos. "
            f"{_SALIDA_RANGO}"
        )
    desconocidas = sorted(set(c.valor) - set(s))
    faltantes = sorted(set(s) - set(c.valor))
    if desconocidas or faltantes:
        raise ValueError(
            f"'{clave}' declara los campos {sorted(c.valor)} y su ventana "
            f"conoce {sorted(s)}: desconocidos {desconocidas}, faltantes "
            f"{faltantes}. Un campo que la ventana no conoce es una errata "
            f"que antes se ignoraba en silencio; uno que falta es el que el "
            f"consumidor iba a pedir y no iba a encontrar"
        )
    for campo, rango in s.items():
        x = c.valor[campo]
        minimo, maximo = rango
        minimo = _piso_condicionado(clave, campo, c.valor, minimo)
        if not _es_real(x):
            raise ValueError(
                f"'{clave}' declara {campo!r} = {x!r}, que no es un numero, "
                f"bajo la ventana numerica {rango!r}. Un texto o un bool no "
                f"se defienden con un rango: {_SALIDA_RANGO}"
            )
        if not minimo <= x <= maximo:
            raise ValueError(
                f"'{clave}' declara {campo!r} = {x!r} fuera de la ventana "
                f"que el mismo declara para ese campo, {rango!r}. "
                f"{_SALIDA_RANGO}"
            )


def _numeros_de(valor: Any):
    """
    Todos los numeros reales que hay DENTRO de un valor de criterio, sea un
    escalar, una tupla (la doble n de Sec. 4.1.1), una lista o un dict (el
    predimensionamiento del cabezal, la exposicion quimica del EMS).

    Existe para que la guardia de finitud no dependa de la FORMA del valor:
    un `inf` escondido dentro de un dict entra al calculo igual que uno
    escrito como escalar.
    """
    if isinstance(valor, dict):
        for v in valor.values():
            yield from _numeros_de(v)
    elif isinstance(valor, (tuple, list, set, frozenset)):
        for v in valor:
            yield from _numeros_de(v)
    elif isinstance(valor, str):
        # UN TEXTO QUE SE LEE COMO NUMERO CUENTA COMO NUMERO. No es celo: es
        # la puerta que quedaba abierta despues de cerrar `--declarar
        # CLAVE=nan`. Con comillas -- `--declarar "CLAVE='nan'"` --
        # `ast.literal_eval` tiene EXITO y devuelve la cadena 'nan', de modo
        # que el respaldo a texto de `cli.py` no se ejecuta y su guardia no
        # llega a mirar. El criterio queda con la cadena 'nan' guardada, y el
        # primer consumidor que haga `float()` sobre el -- `M9_cabezal.
        # cuantia_de_diseno` es el caso medido -- lo devuelve al calculo
        # convertido en el mismo NaN que se rechazo, con la memoria
        # imprimiendo `cuantia_adoptada = nan`.
        #
        # Solo cae el texto que se LEE como numero no finito. Un criterio
        # categorico ('Bishop_Simplificado', 'cota_terreno', 'flexible') no
        # se lee como numero y pasa intacto, que es para lo que el respaldo a
        # texto existe.
        try:
            leido = float(valor)
        except (TypeError, ValueError, OverflowError):
            return
        if not math.isfinite(leido):
            yield leido
    elif _es_real(valor):
        yield valor


def _verificar_finitud(clave: str, c: Criterio) -> None:
    """
    Ningun numero de un criterio puede ser infinito ni NaN, tenga o no rango
    de sensibilidad declarado.

    Por que hace falta aparte del rango (MAT-D14, criterio de salida de S16:
    "ningun dato no finito entra al pipeline como diagnostico falso"): el
    rango solo defiende a los criterios que declaran uno. Un criterio [A] con
    `sensibilidad=None` -- 'talud_terraplen' es el caso vivo -- aceptaba
    `inf` y `nan` por los tres caminos de declaracion. Y el camino existe de
    verdad: `cli.py::declarar_criterios` resuelve el texto de `--declarar`
    con `ast.literal_eval`, y `ast.literal_eval("1e999")` devuelve `inf` sin
    error. Con `talud_terraplen = inf`, `M7.proyeccion_taludes` devuelve
    `inf`, `longitud_conducto` devuelve `inf` y `cota_salida` devuelve
    `-inf`: la memoria imprime un diagnostico entero construido sobre un
    numero que no lo es.

    `nan` es peor que `inf` y por eso no basta con acotar por rango: `nan`
    es FALSO frente a `<=` y frente a `>=` a la vez, de modo que atraviesa
    tanto una comprobacion escrita como "esta dentro del rango" como una
    escrita como "no esta fuera".

    LA GUARDIA ES AQUI Y NO EN `cli.py` porque aqui es el cuello: pasan por
    `_verificar_criterio` las tres vias de declaracion --- el `--declarar` de
    la CLI, el boton de la GUI y la escritura permanente ---, y una guardia
    puesta en una sola de ellas deja las otras dos. La primera version de
    este cierre puso la del texto en `cli.py`, en el brazo `except` de
    `ast.literal_eval`, y una revision adversarial la esquivo con comillas:
    `--declarar "CLAVE='nan'"` hace que `literal_eval` tenga exito, el brazo
    `except` no se ejecute, y la cadena 'nan' entre entera. La de `cli.py` se
    conserva porque da un mensaje mejor en su caso; la que cierra la clase es
    esta.

    HASTA DONDE LLEGA ESTA GUARDIA, dicho para que no se sobreentienda. Cierra
    la PUERTA: ningun no-finito ENTRA. No cierra el OVERFLOW ARITMETICO, que
    es otro defecto: con `talud_terraplen = 1e308` --- finito, y sin rango de
    sensibilidad que lo acote --- `M7.proyeccion_taludes` multiplica y
    devuelve `inf`, y el informe sale con `"longitud_m": {"valor": "inf"}`. Se
    alcanza tambien sin criterio absurdo, solo desde el CSV: una
    `cota_rasante = 1e308` pasa `_a_float`, `_valida_rangos` y
    `_valida_cruzadas`, porque NINGUNA cota tiene techo en dominios.py, y
    ponerle uno seria inventar un valor de proyecto, que es lo que CLAUDE.md
    prohibe expresamente.

    ESO YA NO ESTA ABIERTO. Cuando se escribio este parrafo el defecto no
    tenia ID de auditoria y quedaba declarado aqui sin cerrar; S16.5 lo dio de
    alta como SIS-G-01 y lo cerro donde corresponde, que NO es este archivo:
    la guardia esta a la SALIDA de M7 (`M7_geometria._exigir_finito`), porque
    un resultado no finito nacido de entradas finitas no es un dato mal
    declarado del expediente sino el limite de la aritmetica, y por eso
    tampoco sale como `DatoInvalidoError` sino con la clase que S16.5 anadio a
    la taxonomia para nombrarlo, `modelos.LimiteNumericoError`. La misma
    sesion cerro con esa clase sus dos hermanos de M4 --- SIS-G-02 (el area se
    anula despues del solver) y la mitad alcanzable de MAT-O18 (`Q ** 2`
    desborda) ---, que reventaban en crudo con ZeroDivisionError y
    OverflowError. La division del trabajo se mantiene: aqui la ENTRADA, alla
    la SALIDA.

    Y no todo `inf` que llega a la memoria es ese defecto. SON DOS LOS
    LEGITIMOS, no uno --- este parrafo nombraba solo el primero ---:
    `M9.verificar_volteo` y `M9.verificar_deslizamiento` devuelven `math.inf`
    A PROPOSITO como FS cuando la solicitacion es nula --- "no vuelca" no es
    un numero grande, es la ausencia del momento volcante ---, y `cli._num`
    los renderiza como texto para que el JSON siga siendo valido. Un barrido
    que prohibiera todo no-finito en la SALIDA de todo el calculo romperia los
    dos, y por eso la guardia de S16.5 vive solo en M7 y el censo de los dos
    esta fijado en un test
    (`test_los_dos_unicos_inf_deliberados_del_repositorio_siguen_ahi`).
    """
    for x in _numeros_de(c.valor):
        try:
            finito = math.isfinite(float(x))
        except OverflowError:
            # Un `int` de Python no tiene tope, y uno de 401 cifras no cabe en
            # un double: `float(x)` lanza OverflowError, que no es ValueError
            # ni KeyError y que ni `cli.main` ni la GUI atrapan. Entra por la
            # misma puerta que el infinito y sale por el mismo mensaje, no por
            # una traza: para el calculo son el mismo problema.
            finito = False
        if not finito:
            raise ValueError(
                f"'{clave}' recibe el valor {c.valor!r}, que contiene "
                f"{x!r}: un criterio no puede declararse con un numero "
                "infinito, con NaN ni con un entero que no quepa en doble "
                "precision. No es un valor grande, es un valor que no existe, "
                "y el calculo lo propagaria hasta la memoria sin detenerse en "
                "ningun sitio"
            )


def _formas_de(c: Criterio) -> Tuple[str, ...]:
    """La forma como tupla, sea una o la union de varias."""
    return c.forma if isinstance(c.forma, tuple) else (c.forma,)


def _es_par_de_reales(x: Any) -> bool:
    return (isinstance(x, (tuple, list)) and len(x) == 2
            and all(_es_real(e) for e in x))


def _cumple_la_forma(forma: str, valor: Any, c: Criterio) -> Optional[str]:
    """
    Por que `valor` NO tiene la forma `forma`, o None si la tiene.

    Cada rama es la lectura de UNA forma de `FORMAS`; un texto de vuelta es
    el motivo que la puerta de declaracion imprime. `bool` queda fuera de
    `int` y de `float` por lo mismo que en `_es_real`: `True` pasaria por un
    1 valido. Un `int` SI vale como `float`: los consumidores hacen
    `float()` sobre el, y quien teclea «30» para un angulo no teclea «30.0».
    """
    if forma == FORMA_INT:
        if isinstance(valor, bool) or not isinstance(valor, int):
            return "un ENTERO de Python (ni 1.0, ni True, ni '1')"
        return None
    if forma == FORMA_FLOAT:
        if not _es_real(valor):
            return "un NUMERO real (ni texto, ni bool, ni coleccion)"
        return None
    if forma == FORMA_STR:
        if not isinstance(valor, str) or not valor.strip():
            return "un TEXTO no vacio"
        return None
    if forma == FORMA_CATEGORIA:
        opciones = c.sensibilidad
        if not isinstance(valor, str) or valor not in opciones:
            return ("uno de los textos del conjunto cerrado que declara "
                    f"`sensibilidad`: {', '.join(map(repr, opciones))}")
        return None
    if forma == FORMA_PAR_ORDENADO:
        if not _es_par_de_reales(valor):
            return "un PAR (minimo, maximo) de dos numeros reales"
        if not valor[0] <= valor[1]:
            return "un PAR (minimo, maximo) en ese orden"
        return None
    if forma == FORMA_SERIE_DE_PARES:
        if isinstance(valor, (str, bytes)) or not isinstance(valor, (tuple, list)):
            return "una SERIE de pares [(B, H), ...] y no un escalar ni un texto"
        if not valor:
            return "una SERIE de pares con al menos un par"
        if not all(_es_par_de_reales(par) for par in valor):
            return "una SERIE en la que CADA elemento es un par de dos reales"
        vistos = [tuple(par) for par in valor]
        if len(set(vistos)) != len(vistos):
            return "una SERIE de pares SIN repetidos"
        return None
    if forma == FORMA_DICT_CON_CAMPOS:
        if not isinstance(valor, dict) or not valor:
            return "un DICCIONARIO no vacio con sus campos"
        if not all(isinstance(k, str) for k in valor):
            return "un DICCIONARIO cuyos campos son textos"
        # EXT-6: los campos que la ficha declara OBLIGATORIOS tienen que
        # venir, y con texto. Es lo que convierte «la opcion citada exige
        # la fecha de inicio del expediente y el acto» de una frase en una
        # puerta ('edicion_legal_que_rige_el_expediente'). Y si la ficha
        # declara un conjunto cerrado en `sensibilidad` (tupla de textos),
        # el campo `opcion` tiene que ser uno de ellos.
        faltan = [k for k in c.campos_obligatorios
                  if not (isinstance(valor.get(k), str) and valor[k].strip())]
        if faltan:
            return (f"un DICCIONARIO con los campos obligatorios {faltan} "
                    "declarados con texto")
        s = c.sensibilidad
        if "opcion" in c.campos_obligatorios and isinstance(s, tuple) \
                and all(isinstance(x, str) for x in s) \
                and valor.get("opcion") not in s:
            return ("un DICCIONARIO cuyo campo `opcion` sea una de las "
                    f"opciones de `sensibilidad`: {', '.join(map(repr, s))}")
        return None
    if forma == FORMA_SERIE_DE_CLAVES:
        if isinstance(valor, (str, bytes)) or not isinstance(valor, (tuple, list)):
            return "una TUPLA de claves de fila (textos), no un texto suelto"
        if not valor or not all(isinstance(k, str) and k.strip() for k in valor):
            return "una TUPLA no vacia de claves de fila (textos no vacios)"
        if len(set(valor)) != len(valor):
            return "una TUPLA de claves de fila SIN repetidos"
        return None
    raise ValueError(f"forma {forma!r} sin rama de comprobacion")


def _verificar_forma(clave: str, c: Criterio) -> None:
    """
    La FORMA del valor, exigida a toda entrada, tenga o no ventana numerica
    (EXT-5). Tres reglas:

    1. `forma` es obligatoria y es una de `FORMAS`, o una tupla de ellas
       (la union: `k_v`).
    2. Es COHERENTE con la ventana: una sensibilidad numerica solo defiende
       un `int`, un `float` o un `par_ordenado`; una ventana por campo, un
       `dict_con_campos`; y una `categoria` exige que `sensibilidad` sea la
       tupla de textos del conjunto cerrado --- que es donde CLAUDE.md dice
       que vive el conjunto cerrado de un criterio ---.
    3. El valor, si esta, cumple ALGUNA de las formas declaradas. Si no,
       `ValueError` con el motivo de cada forma (contrato SIS-E-05): es el
       rechazo en la puerta que hasta aqui llegaba tarde, en M2/M4, como un
       `TypeError` que tumbaba la corrida.

    Por que va aqui y no en cada consumidor: los consumidores YA validan
    (`M2.numero_de_celdas`, `M2.progresion_de_cajon`, `M9.k_v_declarado`), y
    cada uno lo hace a su manera y solo cuando le toca correr. La forma en
    la ficha es lo que permite rechazar con el mismo rasero por los tres
    caminos lo que NO TIENE LA ESTRUCTURA que el consumidor exige.

    HASTA DONDE LLEGA, dicho para que no se sobreentienda: la forma es la
    ESTRUCTURA, no el dominio. Un entero negativo para `n_celdas_cajon`, un
    par con un lado negativo en `secciones_cajon_normalizadas` o un
    `TW_receptor` de -1.0 m pasan esta guardia; los dos primeros los atrapa
    el consumidor (`DatoInvalidoError`), y el tercero hoy no lo atrapa nadie
    (medido en la auditoria adversarial de EXT-5: `cli.resolver` lo pasa
    literal a `M3.tw_seccion_1_3`). El dominio se defiende con la ventana de
    sensibilidad donde la hay, y con la guardia del consumidor donde no.
    """
    formas = _formas_de(c)
    if not c.forma or not formas or not all(f in FORMAS for f in formas):
        raise ValueError(
            f"'{clave}' declara forma={c.forma!r}, que no es ninguna de "
            f"{FORMAS} ni una tupla de ellas. Toda entrada dice que "
            "ESTRUCTURA tiene su valor: es lo que la puerta de declaracion "
            "exige antes de que el consumidor lo reviente"
        )
    s = c.sensibilidad
    if c.campos_obligatorios and FORMA_DICT_CON_CAMPOS not in formas:
        raise ValueError(
            f"'{clave}' declara campos_obligatorios={c.campos_obligatorios!r} "
            f"y forma={c.forma!r}: los campos obligatorios solo tienen "
            f"sentido en un `{FORMA_DICT_CON_CAMPOS}`"
        )
    if isinstance(s, dict) and formas != (FORMA_DICT_CON_CAMPOS,):
        raise ValueError(
            f"'{clave}' declara una ventana por campo y forma={c.forma!r}: "
            f"una ventana por campo solo defiende un `{FORMA_DICT_CON_CAMPOS}`"
        )
    if _rango_numerico(s) is not None and not set(formas) <= {
            FORMA_INT, FORMA_FLOAT, FORMA_PAR_ORDENADO}:
        raise ValueError(
            f"'{clave}' declara un rango numerico {s!r} y forma={c.forma!r}: "
            f"un rango numerico solo defiende `{FORMA_INT}`, `{FORMA_FLOAT}` "
            f"o `{FORMA_PAR_ORDENADO}`"
        )
    if FORMA_CATEGORIA in formas and not (
            isinstance(s, tuple) and s
            and all(isinstance(x, str) and x for x in s)):
        raise ValueError(
            f"'{clave}' es una `{FORMA_CATEGORIA}` y su `sensibilidad` es "
            f"{s!r}: el conjunto cerrado de una categoria es una tupla de "
            "textos en `sensibilidad`, que es donde M11 lo imprime"
        )
    if c.valor is None:
        return
    motivos = []
    for forma in formas:
        motivo = _cumple_la_forma(forma, c.valor, c)
        if motivo is None:
            return
        motivos.append(f"`{forma}`: {motivo}")
    raise ValueError(
        f"'{clave}' recibe {c.valor!r}, que no tiene la forma que el "
        f"criterio declara ({' | '.join(motivos)}). Se rechaza en la puerta "
        "de declaracion: aceptarlo dejaria que el consumidor lo reventara "
        "despues con una excepcion fuera de ErrorProyecto"
    )


# Una clave de dict que es un entero ESCRITO como texto (el `'900'` que JSON
# deja donde el archivo trae `900`): cifras ASCII con signo opcional, la
# misma lectura que `gui/componentes._ENTERO`. La usan la guardia de abajo
# (para la pista del mensaje) y la frontera del JSON de
# `declaracion.valor_desde_json` (para rearmar la clave): una definicion.
_ENTERO_ESCRITO = re.compile(r"^-?\d+$", re.ASCII)


def _son_claves_enteras(plantilla: Dict[Any, Any]) -> bool:
    """Todas las claves de `plantilla` son enteros de Python (`bool` no lo es)."""
    return all(isinstance(k, int) and not isinstance(k, bool) for k in plantilla)


def _exigir_claves(clave: str, valor: Any, plantilla: Any, donde: str) -> None:
    """
    `ValueError` si `valor` lleva, en un nivel donde las claves de
    `plantilla` son TODAS enteras, una clave que no lo es; recorre los
    niveles de abajo con la plantilla de la misma clave (o la de una hermana,
    si el valor trae una clave que el archivo no tiene).
    """
    if not isinstance(valor, dict) or not isinstance(plantilla, dict) or not plantilla:
        return
    enteras = _son_claves_enteras(plantilla)
    hermana = next(iter(plantilla.values()))
    for k, v in valor.items():
        if enteras and (not isinstance(k, int) or isinstance(k, bool)):
            ejemplo = next(iter(plantilla))
            pista = (f" Escriba {int(k)} sin comillas."
                     if isinstance(k, str) and _ENTERO_ESCRITO.match(k) else "")
            raise ValueError(
                f"'{clave}': la clave {k!r}{donde} no tiene la forma de la ficha: "
                f"en ese nivel las claves son ENTERAS (el archivo trae, p. ej., "
                f"{ejemplo!r}) y el calculo no encuentra una clave de "
                f"{type(k).__name__}.{pista}")
        _exigir_claves(clave, v, plantilla.get(k, hermana),
                       f"{donde} de {k!r}" if donde else f" de {k!r}")


def _verificar_claves_de_la_ficha(clave: str, c: Criterio) -> None:
    """
    LA FORMA DE LAS CLAVES (UI-5, decision del dueño del 2026-11-15, ficha
    UI3-03): donde las claves del valor del ARCHIVO de la ficha son enteras,
    el valor declarado tiene que traerlas enteras. La forma
    `dict_con_campos` mira la ESTRUCTURA del valor y no la de sus claves, y
    `espesor_pared_conducto` --- un dict por material con el diametro
    designado en mm, ENTERO, como clave --- aceptaba el `'900'` de un dict
    copiado de un JSON: el consumidor (`M2.espesor_pared`) ya no encontraba
    la fila y los puntos salian «no dimensionado» sin aviso.

    La plantilla es el valor de ARCHIVO de la ficha (`CRITERIOS[clave]`), y
    es lo unico que la guardia lee de `CRITERIOS`: al importar es el propio
    valor (la regla es la identidad), en los dos caminos dinamicos es el
    valor del archivo contra el que se declara. Sin valor de archivo no hay
    forma que exigir. Desde la revision de UI-3 (N1) esta regla vivia en las
    capas que llaman a la guardia (`declaracion.verificar_claves_de_la_ficha`)
    y `establecer_valor_dinamico` a pelo aceptaba el `'900'`; UI-5 la trae
    aqui, el cuello de los tres caminos, con el mismo mensaje.
    """
    ficha = CRITERIOS.get(clave)
    plantilla = c.valor if ficha is None else ficha.valor
    _exigir_claves(clave, c.valor, plantilla, "")


# --- VE-1 (hallazgo H2 de su revision) --- Los campos de la PROGRESION DE
# DIAMETROS: los dos que la aritmetica de `M2.siguiente_diametro` usa, y cual
# de ellos tiene que ser positivo. Es una tabla de la GUARDIA, no de la ficha:
# no cambia el valor, la etiqueta ni la ventana del criterio.
_CAMPOS_DE_LA_PROGRESION = {"diametros_normalizados": ("inicio", "paso")}
_CAMPOS_POSITIVOS_DE_LA_PROGRESION = {"diametros_normalizados": ("paso",)}


def _verificar_campos_de_la_progresion(clave: str, c: Criterio) -> None:
    """
    La progresion de diametros trae EXACTAMENTE sus dos campos, los dos
    numeros reales (ni texto, ni bool) y el paso positivo (VE-1, H2).

    La forma `dict_con_campos` mira la estructura y no los campos, y la
    ficha no tiene ventana por campo que los defienda (`_verificar_dict`),
    de modo que la puerta aceptaba lo que el consumidor no puede recorrer.
    Medido por la CLI antes de esta guardia: un paso 0 caia con
    `ZeroDivisionError`, un paso o un inicio de texto con `TypeError`, un
    campo ausente con `KeyError` --los cuatro fuera de `ErrorProyecto`, con
    traza y codigo 1--; un paso booleano recorria 0.90, 1.90…, uno negativo
    bajaba de 0.90 a 0.75, y un campo de mas se ignoraba en silencio. Hoy
    los tres caminos lo rechazan con `ValueError` y el motivo.

    EL INICIO NO SE ACOTA AQUI, a proposito: un inicio no positivo lo
    rechaza el consumidor, M2 (`M2._exigir_arranque_positivo`, desde VE-7
    lote B, B12: `DatoInvalidoError` sobre 'diametros_normalizados', dentro
    de `ErrorProyecto`; hasta VE-7 lo rechazaba la seccion sobre `D`), y la
    linea base lo fija como su rama de error
    (`tests/linea_base_familia_c/regenerar.sh`, corrida 3).
    """
    campos = _CAMPOS_DE_LA_PROGRESION.get(clave)
    if campos is None or not isinstance(c.valor, dict):
        return
    faltan = [k for k in campos if k not in c.valor]
    sobran = sorted(k for k in c.valor if k not in campos)
    no_reales = [k for k in campos if k in c.valor and not _es_real(c.valor[k])]
    no_positivos = [k for k in _CAMPOS_POSITIVOS_DE_LA_PROGRESION.get(clave, ())
                    if k in c.valor and _es_real(c.valor[k])
                    and not c.valor[k] > 0]
    if faltan or sobran or no_reales or no_positivos:
        raise ValueError(
            f"'{clave}' recibe {c.valor!r}, que no es una progresion que se "
            f"pueda recorrer: lleva exactamente los campos {list(campos)}, "
            f"numeros reales (ni texto ni bool), con el paso mayor que cero. "
            f"Faltan {faltan}, sobran {sobran}, no son numeros {no_reales}, "
            f"no son positivos {no_positivos}. Se rechaza en la puerta de "
            "declaracion: aceptarlo dejaria que M2 lo reventara despues fuera "
            "de ErrorProyecto, o que recorriera otra serie en silencio"
        )


def _verificar_discrepancias(clave: str, c: Criterio) -> None:
    """
    Que los ids de `Criterio.discrepancias` existan en el registro y sigan
    VIVOS.

    El import es diferido por la misma razon que en `tabla_del_criterio`: este
    archivo no depende de `normativa` en su cabecera.
    """
    if not c.discrepancias:
        return
    from src.normativa import registro as _reg
    registro = _reg.construir()
    for id_ in c.discrepancias:
        try:
            d = registro.discrepancia(id_)
        except KeyError:
            raise ValueError(
                f"'{clave}' declara la discrepancia '{id_}', que no esta en "
                "el registro. El id viaja al registro, no a la prosa: si no "
                "existe, la memoria imprimiria un ancla rota") from None
        if not d.viva:
            raise ValueError(
                f"'{clave}' declara la discrepancia '{id_}', que esta "
                f"{d.estado.value}. Lo resuelto es material del manifiesto "
                "--- para quien audita el codigo ---, no de la memoria, que "
                "es para quien sustenta")


def _verificar_criterio(clave: str, c: Criterio) -> None:
    """
    Valida UNA entrada: recibe el objeto ya armado, y de CRITERIOS lee una
    sola cosa desde UI-5, el valor del ARCHIVO de su ficha, que es la
    plantilla de la forma de las claves (`_verificar_claves_de_la_ficha`).

    Es la unica que sabe que hace valida a una declaracion, y por eso la
    atraviesan los TRES caminos por los que un criterio puede recibir valor:

        archivo (import-time)      `_coherencia_de_etiquetas()`
        declaracion en caliente    `establecer_valor_dinamico()`
        escritura permanente       `escribir_valor_en_archivo()`

    Los dos caminos dinamicos arman con `replace()` el Criterio que
    RESULTARIA de la declaracion y lo pasan por aqui antes de aceptarla. La
    logica vive una sola vez; los tres sitios son una linea y no pueden
    divergir.

    Es una guardia de arquitectura, no una validacion de dato: si falla al
    importar, el archivo esta mal escrito y ninguna corrida deberia empezar.
    Un [S] sin trazabilidad seria un hecho de sitio que el revisor no puede
    reproducir, y un [S] con sensibilidad seria un hecho al que se le ofrece
    un rango de valores alternativos, que es justo lo que un hecho no tiene.
    """
    _verificar_finitud(clave, c)
    _verificar_discrepancias(clave, c)
    if c.etiqueta not in ETIQUETAS_VALIDAS:
        raise ValueError(
            f"'{clave}' lleva la etiqueta {c.etiqueta!r}, que no es de la "
            f"convencion {ETIQUETAS_VALIDAS}"
        )
    if c.etiqueta == "S":
        if not c.trazabilidad:
            raise ValueError(
                f"'{clave}' es [S] y no declara trazabilidad. Un dato de "
                "sitio se defiende diciendo como reproducir la lectura"
            )
        if c.sensibilidad:
            raise ValueError(
                f"'{clave}' es [S] y declara sensibilidad. Un hecho de "
                "sitio no tiene rango que elegir: si lo tuviera, seria [A]"
            )
    elif c.trazabilidad:
        raise ValueError(
            f"'{clave}' no es [S] y declara trazabilidad. El campo es "
            "exclusivo de los datos de sitio"
        )

    if c.opcional:
        # Un opcional se sostiene sobre un defecto que vive FUERA de este
        # archivo: la norma que `fuente` cita. Sin ese defecto, `valor=None`
        # no significa "se aplica lo normativo", significa "no hay nada", y
        # marcarlo opcional convierte un vacio en un silencio.
        if not c.fuente or c.fuente.strip().upper().startswith("PENDIENTE"):
            raise ValueError(
                f"'{clave}' es opcional y su fuente es {c.fuente!r}. Un "
                "criterio opcional refina un valor que la norma YA fija: su "
                "fuente debe citar la norma de la que sale ese valor por "
                "defecto, no quedar pendiente"
            )
        # Un refinamiento sin limites declarados no es un refinamiento: el
        # rango dice hasta donde puede moverse el proyectista respecto del
        # valor normativo, y es lo que la memoria tiene que defender.
        if c.sensibilidad is None:
            raise ValueError(
                f"'{clave}' es opcional y no declara sensibilidad. El rango "
                "es lo que acota cuanto puede apartarse del valor normativo "
                "por defecto"
            )

    if c.de_catalogo and c.etiqueta in ("N", "N->"):
        # Un tope de catalogo no puede llevar etiqueta normativa: si la
        # llevara, la memoria lo imprimiria como exigencia y le buscaria un
        # numeral que no tiene. Es exactamente el defecto NOR-PRO-01/02.
        raise ValueError(
            f"'{clave}' se rotula `de_catalogo` y lleva etiqueta "
            f"{c.etiqueta!r}. Un valor de catalogo de proveedor no es una "
            "exigencia normativa ni una analogia normativa: es [C] o [A]"
        )

    if c.vacio_verificado:
        if c.valor is None:
            raise ValueError(
                f"'{clave}' declara vacio_verificado y no tiene valor. El "
                "campo es para el valor que CUBRE un vacio registrado; un "
                "criterio todavia vacio no cubre nada"
            )
        if not c.reemplazado_por:
            raise ValueError(
                f"'{clave}' cubre un vacio verificado y no declara "
                "`reemplazado_por`. Una adopcion sobre un vacio agotado tiene "
                "que decir que verificacion la cerraria de verdad, o se lee "
                "como si el vacio ya estuviera resuelto"
            )
        _verificar_ancla_de_vacio(clave, c.vacio_verificado)

    if c.resolucion is None:
        raise ValueError(
            f"'{clave}' no declara `resolucion`. Toda variable de entrada "
            "dice COMO se resuelve (Sec. 4.3): de que tabla, de que rango, "
            "de que ensayo, de que catalogo, de que se deriva, o que se "
            "declara libre. Sin eso la GUI no sabe que ventana abrir y la "
            "memoria no puede escribir de donde salio el valor"
        )
    modo = verificar_resolucion(clave, c.resolucion)

    if isinstance(c.resolucion, Libre) and c.resolucion.opciones:
        raise ValueError(
            f"'{clave}' declara `Libre.opciones="
            f"{c.resolucion.opciones!r}`. En un CRITERIO el conjunto cerrado "
            "de valores admisibles vive en `sensibilidad`, que es lo que M11 "
            "imprime: repetirlo aqui crea dos listas que pueden divergir. El "
            "campo es para las variables que no son criterios -- la Familia "
            "de un punto del CSV -- que no tienen `sensibilidad` donde "
            "ponerlo"
        )

    if modo is ModoDeResolucion.DE_ENSAYO and c.sensibilidad is not None:
        raise ValueError(
            f"'{clave}' se resuelve `de_ensayo` y declara sensibilidad. Un "
            "dato determinado por un procedimiento no tiene rango que "
            "elegir: se defiende con la trazabilidad de la lectura. Si "
            "hubiera rango, la resolucion no es `de_ensayo`"
        )
    if bool(c.de_catalogo) != (modo is ModoDeResolucion.DE_CATALOGO):
        raise ValueError(
            f"'{clave}' rotula `de_catalogo`={c.de_catalogo!r} y se resuelve "
            f"`{modo.value}`. El rotulo y el modo son la misma afirmacion "
            "dicha dos veces, y no pueden discrepar"
        )

    _verificar_nivel(clave, c)
    _verificar_sensibilidad(clave, c)
    # LA FORMA VA ULTIMA a proposito: las guardias de arriba dicen cosas mas
    # precisas cuando aplican (la ventana, el par, el bool), y la forma es la
    # ultima palabra sobre lo que ninguna de ellas mira. Y dentro de la forma,
    # la de las CLAVES (UI-5): la estructura del valor, primero; sus claves,
    # despues.
    _verificar_forma(clave, c)
    _verificar_par_de_encofrado(clave, c)
    _verificar_signo(clave, c)
    _verificar_claves_de_la_ficha(clave, c)
    _verificar_campos_de_la_progresion(clave, c)


# --- T11-10 --- La VENTANA DEL PAR de un criterio cuya forma es la union de
# una fila y un par: el rango que la fuente escribe para el par que no sale
# de ninguna fila. Hoy uno: 'n_manning_cajon', el par del encofrado de un
# marco vaciado in situ, acotado por el num. B.3 del HDS-5. Es una tabla de
# la GUARDIA, como `_CAMPOS_DE_LA_PROGRESION`: no cambia el valor, la
# etiqueta ni la ventana de la ficha, cuya `sensibilidad` es la tupla de las
# tres lecturas (simbolica) y no puede ademas ser un rango numerico.
_VENTANA_DEL_PAR = {
    "n_manning_cajon": (MANNING_CAJON_IN_SITU_HDS5,
                        "HDS5_3ED.B.3#CAJON_IN_SITU",
                        NUMERAL_MANNING_CAJON_IN_SITU_HDS5),
}


def _verificar_par_de_encofrado(clave: str, c: Criterio) -> None:
    """
    El PAR de un criterio de `_VENTANA_DEL_PAR` cae dentro del rango que la
    fuente escribe (T11-10). Va DESPUES de `_verificar_forma`, de modo que
    aqui un valor que no es texto ya es un par ordenado de dos reales finitos
    sin booleanos (`_cumple_la_forma`, `_verificar_finitud`); esta guardia
    solo mira los extremos.

    Para 'n_manning_cajon' el rango es el del num. B.3 del HDS-5 para el cajon
    VACIADO IN SITU (0.012 a 0.022 segun el encofrado). Un n_min por debajo
    seria un marco mas liso que el de laboratorio de la Tabla B.1, cuya fila
    del cajon empieza en el mismo 0.012; un n_max por encima, un encofrado
    que la fuente no describe. La condicion se escribe en positivo y negada
    (forma MAT-D13). Un texto no es un par: lo acota el consumidor contra las
    filas admitidas.
    """
    ventana = _VENTANA_DEL_PAR.get(clave)
    if ventana is None or c.valor is None or isinstance(c.valor, str):
        return
    (minimo, maximo), cita_id, numeral = ventana
    n_min, n_max = c.valor
    if not (minimo <= n_min and n_max <= maximo):
        raise ValueError(
            f"'{clave}' recibe el par {tuple(c.valor)!r}, fuera del rango "
            f"[{minimo}, {maximo}] que la fuente escribe para el par que no "
            f"sale de ninguna fila ({numeral}, cita {cita_id}). Se rechaza en "
            "la puerta de declaracion: un par fuera de ese rango no es la "
            "especificacion de un encofrado que la fuente describa")


def _verificar_signo(clave: str, c: Criterio) -> None:
    """
    `Criterio.no_negativo` (revision de VE-2, M4) y `Criterio.positivo`
    (verificacion de sus correcciones, N2): el valor, si esta, no es menor
    que cero, o es mayor que cero. Va DESPUES de `_verificar_forma`, de modo
    que aqui el valor ya es un numero real finito (`_verificar_finitud` dejo
    fuera el NaN y el infinito). La condicion se escribe en positivo y
    negada (forma MAT-D13), como en `datos_sitio._verificar_dato`.

    Los campos solo se declaran en un `int` o un `float`: en otra forma no
    hay un signo que comprobar, y declararlos seria una ficha mal escrita
    --- tambien con el criterio vacio, por eso la forma se mira antes que el
    valor ---.
    """
    for campo in ("no_negativo", "positivo"):
        if not getattr(c, campo):
            continue
        formas = _formas_de(c)
        if not formas or not set(formas) <= {FORMA_INT, FORMA_FLOAT}:
            raise ValueError(
                f"'{clave}' declara {campo} con forma={c.forma!r}: el signo "
                f"solo se declara en un numero escalar (`{FORMA_INT}` o "
                f"`{FORMA_FLOAT}`)")
    if c.valor is None:
        return
    if c.no_negativo and not c.valor >= 0:
        raise ValueError(
            f"'{clave}' no admite un valor negativo y recibe {c.valor!r}: su "
            "ficha declara `no_negativo`. Se rechaza en la puerta de "
            "declaracion, por los tres caminos, y no en el consumidor")
    if c.positivo and not c.valor > 0:
        raise ValueError(
            f"'{clave}' tiene que ser positivo (mayor que cero) y recibe "
            f"{c.valor!r}: su ficha declara `positivo`. Se rechaza en la "
            "puerta de declaracion, por los tres caminos, y no en el "
            "consumidor")


def _verificar_nivel(clave: str, c: Criterio) -> None:
    """
    Las tres reglas del `nivel`, y las tres nacen del cierre del nivel de
    perfil (S20):

    1. El valor, si esta, es uno de los dos NIVELES.
    2. Un criterio SIN VALOR tiene que declarar nivel. Un vacio que no dice a
       que entrega pertenece no se puede planificar: no se sabe si bloquea el
       perfil o si lo difiere el alcance.
    3. Un criterio DE PERFIL con etiqueta [A] tiene que llevar `sensibilidad`
       Y `resolucion`. Es el criterio de salida del nivel de perfil escrito
       como invariante: "ningun [A] de perfil sin valor, sin sensibilidad y
       sin procedencia". Las otras cuatro etiquetas quedan fuera por lo que
       dice `ETIQUETAS_DE_ELECCION`.

       LA REGLA NO MIRA SI HAY VALOR, y esa fue una correccion dentro de la
       propia S20. Mirandolo, un criterio [A] de perfil sin declarar podia
       quedarse sin ventana -- y entonces la GUI o la CLI no lo podian
       declarar en caliente, porque el valor aparecia y la ventana seguia sin
       estar --. La ventana es parte de la FICHA, no del valor: dice dentro de
       que se va a poder elegir, y eso se sabe antes de elegir. Los dos que la
       sesion no pudo cerrar ('TW_receptor' y 'homogeneidad_serie_fen') tienen
       hoy su ventana escrita precisamente por esto.
    """
    if c.nivel and c.nivel not in NIVELES:
        raise ValueError(
            f"'{clave}' declara nivel={c.nivel!r}, que no es ninguno de "
            f"{NIVELES}")
    if c.valor is None and not c.opcional and not c.nivel:
        raise ValueError(
            f"'{clave}' esta sin valor y no declara `nivel`. Un vacio que no "
            "dice a que entrega pertenece no se puede planificar: no se sabe "
            f"si bloquea el nivel de perfil o si `--alcance {NIVEL_PERFIL}` "
            "difiere su etapa al expediente")
    if c.nivel == NIVEL_PERFIL and c.etiqueta in ETIQUETAS_DE_ELECCION:
        if c.sensibilidad is None:
            raise ValueError(
                f"'{clave}' es de nivel {NIVEL_PERFIL} y esta declarado con "
                f"etiqueta [{c.etiqueta}], pero no lleva `sensibilidad`. El "
                "criterio de salida del nivel de perfil no admite un valor "
                "elegido sin la ventana dentro de la que se eligio: sin ella "
                "la memoria imprime un numero y el revisor no puede saber si "
                "moverlo cambia el diseño")
        if c.resolucion is None:
            raise ValueError(
                f"'{clave}' es de nivel {NIVEL_PERFIL} y esta declarado con "
                f"etiqueta [{c.etiqueta}], pero no lleva `resolucion`. Un "
                "valor sin procedencia no se puede defender: la memoria tiene "
                "que poder escribir de que tabla, de que rango o de que "
                "ensayo salio")


def criterios_por_nivel(nivel: str) -> List[str]:
    """Las claves de un nivel de entrega, en orden alfabetico."""
    if nivel not in NIVELES:
        raise ValueError(f"nivel {nivel!r} desconocido; hay {NIVELES}")
    return sorted(k for k, c in CRITERIOS.items() if c.nivel == nivel)


def criterios_de_perfil_sin_valor() -> List[str]:
    """
    Los criterios de PERFIL que siguen vacios: lo que le falta al nivel de
    perfil para cerrar, sin mezclarlo con lo que es del expediente.

    Es el corte que la lista plana de `criterios_sin_valor()` no hace y que
    obligaba a leer los 24 vacios uno por uno para saber cuales frenaban esta
    entrega.
    """
    return [k for k in criterios_por_nivel(NIVEL_PERFIL)
            if CRITERIOS[k].valor is None and not CRITERIOS[k].opcional]


def _coherencia_de_etiquetas() -> None:
    """Somete TODO el archivo a la guardia, al importar el modulo."""
    for clave, c in CRITERIOS.items():
        _verificar_criterio(clave, c)


_coherencia_de_etiquetas()


# ---------------------------------------------------------------------------
# Reporte para el modulo M11
# ---------------------------------------------------------------------------

# Orden de lectura, de mas determinado a mas elegido. [S] va entre [N->] y
# [C]: su procedimiento es normativo y propio del sitio, no prestado ni ajeno.
_ORDEN = {"N": 0, "N->": 1, "S": 2, "C": 3, "A": 4}


def reporte_criterios(solo_usados: bool = True, *,
                      contexto: Optional[Any] = None) -> str:
    """
    Genera el bloque de declaracion de criterios para el reporte final.
    Con solo_usados=True lista unicamente los criterios que el calculo invoco.

    Con `contexto` --- el `ContextoCorrida` del informe --- lee la FOTO de
    esa corrida (usos, valores efectivos, declarados, vacios) y no el estado
    vivo del proceso; es lo que `cli.volcar` le pasa desde EXT-4 (EXT-A-01).
    Sin el, describe el estado de ahora mismo, que es lo que quiere quien lo
    invoca desde la consola de este modulo.
    """
    if contexto is None:
        usados = set(_USADOS)
        efectivo = lambda k: criterio_efectivo(k).valor           # noqa: E731
        en_caliente_de = declarado_en_caliente
        sin_valor = criterios_sin_valor()
        en_caliente = criterios_declarados_en_caliente()
        opcionales = criterios_opcionales_sin_declarar()
    else:
        usados = set(contexto.criterios_usados)
        efectivo = contexto.valor_efectivo
        en_caliente_de = contexto.declarado_en_caliente
        sin_valor = list(contexto.criterios_sin_valor)
        en_caliente = list(contexto.declarados_en_caliente)
        opcionales = list(contexto.criterios_opcionales_sin_declarar)
    claves = sorted(
        (usados if solo_usados else set(CRITERIOS)),
        key=lambda k: (_ORDEN.get(CRITERIOS[k].etiqueta, 9), k),
    )
    if not claves:
        return "No se invoco ningun criterio adoptado."

    out = ["=" * 78,
           "DECLARACION DE CRITERIOS ADOPTADOS",
           "=" * 78, ""]

    for k in claves:
        c = replace(CRITERIOS[k], valor=efectivo(k))
        valor_efectivo = c.valor
        marca_override = ("  [declarado para esta corrida, no en archivo]"
                          if en_caliente_de(k) else "")
        marca_prov = "  [PROVISIONAL: valor de prueba, NO verificado]" if c.provisional else ""
        marca_opc = "  [refinamiento opcional]" if c.opcional else ""
        out.append(
            f"[{c.etiqueta}] {k} = {valor_efectivo!r}"
            f"{marca_override}{marca_prov}{marca_opc}")
        out.append(f"     Concepto      : {c.concepto}")
        if c.de_catalogo:
            out.append(f"     DE CATALOGO   : {c.de_catalogo}")
        out.append(f"     Justificacion : {c.justificacion}")
        out.append(f"     Fuente        : {c.fuente}")
        if c.reemplazado_por:
            out.append(f"     Se sustituye por: {c.reemplazado_por}")
        if c.sensibilidad:
            out.append(f"     Sensibilidad  : {c.sensibilidad}")
        if c.trazabilidad:
            out.append(f"     Trazabilidad  : {c.trazabilidad}")
        if c.verificacion_pendiente:
            out.append(f"     >> VERIFICAR  : {c.verificacion_pendiente}")
        out.append("")

    pendientes = [k for k in claves if CRITERIOS[k].verificacion_pendiente]
    if pendientes:
        out.append("-" * 78)
        out.append("ADVERTENCIA: los siguientes criterios tienen verificaciones")
        out.append("pendientes y no deben citarse en la memoria hasta resolverlas:")
        for k in pendientes:
            out.append(f"  - {k}")
        out.append("-" * 78)

    if sin_valor:
        out.append("")
        out.append("-" * 78)
        out.append("VACIOS SIN VALOR: detienen el calculo en cuanto se invocan")
        out.append("(bloque aparte, Sec. 0.7 - no se sustituyen por defecto):")
        for k in sin_valor:
            out.append(f"  - [{CRITERIOS[k].etiqueta}] {k}: {CRITERIOS[k].concepto}")
        out.append("-" * 78)

    if en_caliente:
        # Ni vacios (tienen valor) ni valores del archivo (no estan en el):
        # sin este bloque se caian de las dos listas a la vez.
        out.append("")
        out.append("-" * 78)
        out.append("DECLARADOS SOLO PARA ESTA CORRIDA - no estan en este")
        out.append("archivo ni en el SHA-1 que la memoria imprime. Valen para")
        out.append("esta corrida y para ninguna otra:")
        for k in en_caliente:
            c = CRITERIOS[k]
            dice = ("el archivo lo declara sin valor" if c.valor is None
                    else f"el archivo declara {c.valor!r}")
            out.append(f"  - [{c.etiqueta}] {k} = {efectivo(k)!r}  ({dice})")
        out.append("-" * 78)

    sin_consumidor = criterios_sin_consumidor()
    if sin_consumidor:
        out.append("")
        out.append("-" * 78)
        out.append("DECLARADOS QUE NINGUNA ETAPA INVOCA - con la razon escrita")
        out.append("en el propio criterio, no deducida de su ausencia:")
        for k in sin_consumidor:
            c = replace(CRITERIOS[k], valor=efectivo(k))
            out.append(f"  - [{c.etiqueta}] {k} = {c.valor!r}")
            out.append(f"      {c.sin_consumidor}")
        out.append("-" * 78)

    if opcionales:
        out.append("")
        out.append("-" * 78)
        out.append("REFINAMIENTO OPCIONAL NO ADOPTADO - se aplica el valor")
        out.append("normativo por defecto. NO son vacios: el calculo corre y")
        out.append("nadie tiene obligacion de declararlos:")
        for k in opcionales:
            c = CRITERIOS[k]
            out.append(f"  - [{c.etiqueta}] {k}: {c.concepto}")
            out.append(f"      Norma que aporta el defecto: {c.fuente}")
        out.append("-" * 78)

    return "\n".join(out)


def parametros_sensibilizables(solo_numericos: bool = True) -> Dict[str, Tuple]:
    """
    Los criterios con rango declarado, para el analisis de sensibilidad.

    Con `solo_numericos=True` (por defecto) devuelve unicamente los rangos
    que un barrido puede recorrer: 2-tuplas de reales. Una sensibilidad
    SIMBOLICA -- expresada en funcion de otro criterio -- se declara y se
    imprime en la memoria, pero no se puede recorrer sin resolver antes la
    variable de la que depende, y hacer `float()` sobre ella la falsearia.
    Con `solo_numericos=False` salen todas, tal como estan declaradas.
    """
    return {
        k: c.sensibilidad for k, c in CRITERIOS.items()
        if c.sensibilidad
        and (not solo_numericos or _rango_numerico(c.sensibilidad) is not None)
    }


if __name__ == "__main__":
    # Demostracion: cadena sismica completa desde una sola fuente. El PGA es
    # un dato de sitio [S] y entra desde datos_sitio.py, no desde aqui.
    from src import datos_sitio as ds

    A_s = ds.valor("PGA_roca_B") * valor("F_pga")
    k_h = valor("factor_muro_eleccion") * A_s

    # 'clase_sitio' NO se invoca, aqui tampoco. Es un [S] sin valor y lo que
    # la cadena consume es el factor: invocarlo lanzaria
    # CriterioPendienteError y esta demostracion dejaria de correr por un
    # dato que la cadena no necesita. Aparece en el reporte de abajo por
    # `criterios_sin_valor()`, que es su puerta.

    print(f"A_s = {A_s:.2f} g")
    print(f"k_h = {k_h:.2f}")
    print(f"k_v = {valor('k_v'):.2f}\n")
    print(reporte_criterios())
