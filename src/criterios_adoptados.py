"""
criterios_adoptados.py
======================
Fuente unica de verdad para todo parametro que NO sea una exigencia normativa
verificada. Ningun otro modulo del script debe declarar estos valores.

Regla de uso
------------
    from criterios_adoptados import valor, reporte_criterios

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

import numbers
import re
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, Tuple, Dict, List, Set

from constantes_normativas import MANNING
from modelos import CriterioPendienteError

# `MANNING` es la unica importacion de constantes normativas que hace este
# archivo, y entra por una razon concreta: 'n_manning_hdpe' es un [N->] --
# una fila de esa tabla aplicada por analogia a un material que la tabla no
# lista -- y su valor tiene que SER esa fila, no una copia que puede quedar
# desincronizada. Un [N->] que duplica el literal de su origen no es una
# analogia declarada: son dos numeros iguales por casualidad hasta que uno
# cambie. No abre la puerta a mas: aqui no se transcribe ninguna constante
# normativa, se referencia la que ya esta transcrita en su archivo.


# ---------------------------------------------------------------------------
# Estructura
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Criterio:
    valor: Any
    etiqueta: str                              # "N", "N->", "S", "C", "A"
    concepto: str                              # que es
    justificacion: str                         # por que este valor
    fuente: str                                # de donde sale
    reemplazado_por: Optional[str] = None      # ensayo/dato que lo sustituye
    sensibilidad: Optional[Tuple] = None       # rango declarado -- [A] y [C]; nunca [S]
    trazabilidad: Optional[str] = None         # como reproducir la lectura -- SOLO [S]
    verificacion_pendiente: Optional[str] = None   # lo que falta confirmar
    provisional: bool = False                  # valor de PRUEBA, no verificado
    opcional: bool = False                     # valor=None NO bloquea: hay defecto normativo
    vacio_verificado: str = ""                 # ancla al vacio registrado que este valor cubre
    sin_consumidor: str = ""                   # por que NINGUN modulo lo invoca
    de_catalogo: str = ""                      # rotulo: el valor es de CATALOGO, no de norma

    # `de_catalogo` marca el valor que se PARECE a una exigencia normativa y
    # no lo es: un tope de proveedor, una disponibilidad de mercado. Lleva el
    # rotulo con que hay que imprimirlo -- de que catalogo sale y que norma de
    # producto NO lo sostiene -- para que la memoria no le invente una cita.
    #
    # Nace de NOR-PRO-01 y NOR-PRO-02: los topes D_MAX (2.70 / 2.10 / 1.50 m)
    # vivian en constantes_normativas.py atribuidos a AASHTO M170 y ASTM A760,
    # y esas normas tabulan hasta 3600 mm. Un tope de catalogo impreso como
    # tope normativo es una cita falsa que ademas descarta materiales en
    # silencio. El campo existe para que la distincion viaje con el dato y no
    # dependa de que alguien lea la justificacion entera.

    # `sin_consumidor` es la razon escrita de que ninguna etapa de produccion
    # llame a este criterio. Existe porque un criterio sin consumidor tiene
    # dos lecturas opuestas -- se olvido cablearlo, o su consumidor esta
    # declarado fuera de alcance -- y desde fuera del archivo no se
    # distinguen: `criterios_usados()` devuelve lo mismo en los dos casos.
    #
    # Sin el campo, un criterio CON valor y sin invocacion no cae en ninguno
    # de los tres bloques de M11 (no esta usado, no esta vacio, no es
    # opcional) y desaparece de la memoria sin dejar rastro. Con el, M11 lo
    # imprime en su propio bloque con la razon delante.

    # `vacio_verificado` distingue dos cosas que se parecen y no son iguales:
    # un valor que cubre un hueco que NADIE busco, y uno que cubre un hueco
    # que alguien AGOTO -- fuente por fuente, con cita -- y dejo registrado.
    # Solo lo segundo se puede defender en una memoria, y solo lo segundo
    # entra en el bloque de acotaciones que M11 imprime.
    #
    # No es un booleano a proposito: lleva el ANCLA al registro
    # ("manifiesto_citas.md Sec. 14.a"), de modo que la memoria puede decirle
    # al revisor donde ir a leer la busqueda completa en vez de pedirle que
    # confie. `_verificar_criterio` comprueba al importar que esa seccion
    # existe de verdad: un ancla rota falla, no pasa en silencio.

    # `opcional=True` cambia el significado de `valor=None`, que sin el
    # significa una sola cosa: vacio que detiene el calculo. Un criterio
    # opcional REFINA un valor que la norma ya fija, en vez de cubrir un
    # vacio que la norma deje abierto; sin declarar, el consumidor aplica el
    # valor normativo por defecto y el calculo sigue. Se lee con
    # `valor_si_declarado()`, nunca con `valor()`.
    #
    # La distincion vivia solo en que funcion usaba el llamador, mas prosa en
    # la justificacion. Eso dejaba a `criterios_sin_valor()` -- y con el, al
    # bloque "VACIOS SIN VALOR" de la memoria y al aviso de la GUI --
    # anunciando como vacio bloqueante lo que es un refinamiento que nadie
    # tiene obligacion de declarar. Ahora la distincion esta en el dato.

    # `provisional=True` marca un valor cargado para una corrida de prueba
    # integral: destraba el pipeline para ver que puntos completan diseno,
    # pero NO esta verificado contra norma ni ensayo y no puede ir a una
    # memoria de calculo. Existe para que ese valor NUNCA pueda pasar
    # inadvertido: reporte_criterios() y M11 lo imprimen con marca visible.
    # Ningun criterio del expediente lo lleva puesto -- si alguno aparece
    # con provisional=True en una revision, es que quedo residuo de una
    # prueba sin limpiar.

    # sensibilidad y trazabilidad no son dos nombres para lo mismo y no se
    # mezclan: un [A] se defiende mostrando cuanto cambiaria el resultado con
    # el otro extremo del rango, y un [S] no tiene rango que elegir -- se
    # defiende diciendo donde se leyo, para que el revisor repita la lectura.
    # `_verificar_criterio()` lo verifica al importar el modulo.


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
    Declara, solo para esta corrida, el valor de un criterio pendiente.

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
    _verificar_criterio(clave, replace(CRITERIOS[clave], valor=valor_nuevo))
    _OVERRIDES[clave] = valor_nuevo


def quitar_valor_dinamico(clave: str) -> None:
    """Retira la declaracion en caliente de un criterio (vuelve a bloquear)."""
    _OVERRIDES.pop(clave, None)


def limpiar_valores_dinamicos() -> None:
    """Retira todas las declaraciones en caliente de la corrida."""
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
    Reescribe, EN EL ARCHIVO FUENTE, el ``valor=None`` del criterio `clave`
    por `valor_nuevo`. Accion permanente y distinta de
    `establecer_valor_dinamico`: se usa solo cuando el usuario confirma de
    forma explicita que quiere dejar de tratar el criterio como pendiente
    (la GUI pide confirmacion aparte antes de llamarla). No toca ningun otro
    campo del Criterio (etiqueta, justificacion, fuente, sensibilidad): esos
    se revisan y editan a mano, porque describen POR QUE se adopto el valor.
    """
    import re

    if clave not in CRITERIOS:
        raise KeyError(f"'{clave}' no esta declarado en criterios_adoptados.py.")

    # La misma guardia que el archivo y que la declaracion en caliente, y
    # ANTES de tocar el disco: un valor que la guardia rechaza no llega a
    # escribirse, para que el archivo fuente nunca quede en un estado que su
    # propio import rechazaria.
    _verificar_criterio(clave, replace(CRITERIOS[clave], valor=valor_nuevo))

    ruta_archivo = ruta or __file__
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
    Path(ruta_archivo).write_text(texto_nuevo, encoding="utf-8")

    # El archivo ya quedo escrito; se refleja tambien en memoria para que el
    # resto de esta sesion (GUI o CLI en curso) vea el valor definitivo sin
    # tener que reiniciar el proceso, y se retira el override en caliente:
    # ya no hace falta, el valor "real" es ahora este.
    CRITERIOS[clave] = replace(CRITERIOS[clave], valor=valor_nuevo)
    _OVERRIDES.pop(clave, None)


def criterios_usados() -> List[str]:
    """
    Claves que el calculo invoco, en orden alfabetico. Es la misma informacion
    que `reporte_criterios(solo_usados=True)` imprime como texto, expuesta como
    lista para el consumidor que arma su propio bloque (cli.py la vuelca al
    JSON). Existe para que nadie tenga que leer `_USADOS` desde fuera.
    """
    return sorted(_USADOS)


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
# CRITERIOS ADOPTADOS
# ---------------------------------------------------------------------------

CRITERIOS: Dict[str, Criterio] = {

    # ----------------------- SISMO: cadena unica -------------------------
    # Se define UNA vez y se propaga a toda verificacion de estabilidad.

    # 'PGA_roca_B' ya no vive aqui: es un dato de sitio [S] -- la lectura de un
    # mapa normativo sobre las coordenadas de esta obra, unica para todo el
    # corredor -- y vive en `datos_sitio.py`. No se declara en dos sitios: la
    # cadena sismica de M9 lo lee de alla.

    "PERFIL_SUELO_PRESUNTO": Criterio(
        valor="S5",
        etiqueta="S",
        concepto="Perfil de suelo de E.030 presunto para el sitio (S0-S5)",
        justificacion="El Art. 14.6 de E.030 define el ESQUEMA de perfiles "
                      "S0-S5 y sus umbrales; que letra le toca a este sitio es "
                      "el resultado de aplicar ese esquema a las condiciones "
                      "de la llanura del Bajo Piura (arenas saturadas, NF "
                      "somero, suelos potencialmente licuables), no una "
                      "exigencia normativa con valor fijo. En otra via con "
                      "otro suelo el mismo articulo da otra letra. El nombre "
                      "de la variable lo venia admitiendo desde el principio: "
                      "PRESUNTO es una presuncion de expediente",
        fuente="E.030 (RM 183-2026-VIVIENDA), Art. 14.6 - suelos "
               "potencialmente licuables",
        reemplazado_por="Ensayo SPT DE LICUEFACCION: perforaciones de al menos "
                        "15 m de profundidad con ensayo cada 1.00 m (E.050 "
                        "Art. 38). Es la profundidad que cierra ESTE criterio "
                        "-- la presuncion de suelo licuable del Art. 14.6 -- y "
                        "no la del criterio 'clase_sitio', que necesita 30 m",
        trazabilidad="Clasificacion del Art. 14.6 de E.030 aplicada a la "
                     "caracterizacion geotecnica disponible del corredor "
                     "(llanura del Bajo Piura, distrito de La Union), sin "
                     "ensayo que la cierre. Ambito: todo el corredor mientras "
                     "sea presuncion; con SPT pasa a ser dato por calicata y "
                     "entonces le corresponde una columna del CSV, no esta "
                     "entrada. REFERENCIA MUERTA HOY: ningun modulo de "
                     "src/modulos/ lo invoca -- la clase de sitio que si entra "
                     "en el calculo es la de AASHTO, criterio 'clase_sitio'. "
                     "Se conserva declarado, y no borrado, porque es la "
                     "presuncion geotecnica sobre la que se apoyan tanto "
                     "'clase_sitio' como la hipotesis de licuefaccion de "
                     "Sec. 0.5",
        verificacion_pendiente="Al llegar el SPT, confirmar el perfil y "
                               "decidir si es unico para el tramo o varia por "
                               "calicata; si varia, no se corrige el valor: se "
                               "convierte en columna del CSV",
        sin_consumidor="Referencia declarada, no calculo: la clasificacion "
                       "sismica del sitio se declara aparte, en el criterio "
                       "'clase_sitio', y la evaluacion de licuefaccion que "
                       "usaria este perfil esta declarada fuera del alcance "
                       "del script (Sec. 0.5). Se conserva declarado, y no "
                       "borrado, para que el ensayo que lo cerraria siga "
                       "pedido; que papel juega respecto de 'clase_sitio' "
                       "esta en su trazabilidad y es materia de la revision "
                       "de la cadena sismica, no de este campo",
    ),

    "clase_sitio": Criterio(
        valor="F_con_factores_tabulados_por_adopcion",
        etiqueta="A",
        concepto="Clase de sitio sismica AASHTO y base sobre la que se toman "
                 "los factores de sitio de la cadena sismica",
        justificacion="El sitio es Clase F por susceptibilidad a licuefaccion "
                      "(arenas saturadas, NF a 1.4 m); esa parte no cambia. "
                      "LO QUE CAMBIA ES QUE LA DISPENSA POR PERIODO CORTO NO "
                      "EXISTE. Se verifico contra AASHTO LRFD Bridge Design "
                      "Specifications, 9a edicion (2020): no esta en el "
                      "Art. 3.10.3.1, no esta en su comentario C3.10.3.1, y "
                      "no esta en ninguna tabla ni nota de tabla de clases de "
                      "sitio. AASHTO exige, de forma incondicional, un estudio de "
                      "respuesta de sitio especifico para la Clase F. La "
                      "redaccion anterior de este criterio y de Sec. 0.5 "
                      "atribuia a AASHTO una dispensa por periodo "
                      "fundamental T <= 0.5 s que AASHTO no concede: no fue "
                      "un vacio rellenado en silencio, fue una autorizacion "
                      "normativa inventada, que es peor, porque un vacio se "
                      "ve y una cita falsa se cree. "
                      "CONSECUENCIA SOBRE LA ETIQUETA: deja de ser [C]. Un "
                      "[C] es un vacio normativo CUBIERTO con fuente tecnica "
                      "reconocida, y aqui no hay fuente que cubra nada -- la "
                      "que se citaba no dice lo que se le hacia decir. Pasa a "
                      "[A]: seguir el calculo con los factores de sitio "
                      "tabulados, mientras no exista el estudio de respuesta "
                      "de sitio, es una ADOPCION DECLARADA DEL PROYECTISTA y "
                      "no un permiso de la norma. La memoria lo dice con esas "
                      "palabras; no hay forma honesta de escribirlo mas "
                      "corto. "
                      "ALCANCE, ahora sin coartada: los factores tabulados "
                      "permiten DIMENSIONAR el elemento; no evaluan el riesgo "
                      "de licuefaccion (Fase 0-bis), y los efectos de la "
                      "licuefaccion -- asentamiento, desplazamiento lateral, "
                      "perdida de capacidad portante -- quedan fuera del "
                      "alcance del script y remitidos al estudio geotecnico "
                      "del expediente. Un analisis de respuesta especifica de "
                      "sitio puede arrojar valores MAYORES que los tabulados: "
                      "la adopcion no es conservadora por construccion, y por "
                      "eso es [A] y no [N->]",
        fuente="NINGUNA autoriza la adopcion. AASHTO LRFD 9a ed. (2020), "
               "Art. 3.10.3.1 y C3.10.3.1: la Clase F exige estudio de "
               "respuesta de sitio especifico, sin dispensa alguna por periodo "
               "corto. El Manual de Puentes tampoco tipifica dispensas "
               "para Clase F en su Tabla 2.4.3.11.2.1.2-1. La adopcion es "
               "del proyectista y se declara como tal",
        reemplazado_por="CARACTERIZACION DE SITIO SOBRE LOS 30 m SUPERIORES: "
                        "Vs30, o N_barra promediado en esos 30 m, con el que "
                        "se lee la clase de sitio. Los 30 m son parte de la "
                        "DEFINICION de la clase (AASHTO LRFD Art. 3.10.3.1, "
                        "coherente con el perfil de E.030): una clase de sitio "
                        "leida sobre menos profundidad no es la misma "
                        "variable. "
                        "NO LO CIERRA el SPT de 15 m de E.050 Art. 38: ese "
                        "ensayo responde a la pregunta de licuefaccion "
                        "(criterio PERFIL_SUELO_PRESUNTO) y se detiene a mitad "
                        "de la columna que esta clase necesita. Este criterio "
                        "decia antes '>= 15 m -> N_barra o Vs30', que mezclaba "
                        "las dos profundidades y daba por cerrada con 15 m una "
                        "lectura que exige 30. Son dos requisitos de campana "
                        "distintos y conviene pedirlos juntos al programar la "
                        "campana geotecnica",
        verificacion_pendiente="La verificacion que este campo pedia -- si la "
                               "dispensa estaba en articulado o en comentario "
                               "-- YA SE HIZO y la respuesta fue que no esta "
                               "en ninguno de los dos. Lo que queda pendiente "
                               "es otra cosa: mientras la adopcion siga en "
                               "pie, la memoria debe declararla como decision "
                               "del proyectista contra una exigencia expresa "
                               "de AASHTO, y el expediente debe programar el "
                               "estudio de respuesta de sitio especifico. No "
                               "se cita AASHTO como respaldo de la adopcion. "
                               "POR QUE NO DECLARA SENSIBILIDAD, siendo el "
                               "unico [A] con valor que no la declara: un "
                               "rango de sensibilidad dice entre que dos "
                               "valores pudo moverse la ELECCION, y aqui la "
                               "eleccion no esta cerrada por arriba porque "
                               "la PREMISA -- que el sitio es Clase F por "
                               "licuefaccion -- esta bajo REVISION ABIERTA "
                               "del expediente, no resuelta ni en un sentido "
                               "ni en el otro. Hasta que esa revision "
                               "termine, declarar un rango de clases "
                               "alternativas seria fijar la respuesta antes "
                               "de resolver la pregunta, y la memoria "
                               "imprimiria como acotada una adopcion que "
                               "todavia no lo esta. El rango se declara "
                               "cuando la premisa se cierre, y no antes; "
                               "hasta entonces lo que la memoria dice es lo "
                               "unico defendible hoy: que no hay norma que "
                               "respalde la adopcion",
    ),

    "F_pga": Criterio(
        valor=1.0,
        etiqueta="A",
        concepto="Factor de sitio para la aceleracion pico",
        justificacion="Sin SPT no hay clase de sitio definitiva. Para PGA >= 0.50 "
                      "los factores convergen: 1.0 para clases C y D, 0.9 para E. "
                      "Se adopta 1.0 por ser conservador o exacto frente a las "
                      "tres clases plausibles; incertidumbre asociada <= 10%",
        fuente="Tabla 2.4.3.11.2.1.2-1 del Manual de Puentes (valores [N]: C=1.0, D=1.0, E=0.9 para PGA>=0.50). La ELECCION es [A]",
        reemplazado_por="Clase de sitio definitiva desde SPT",
        sensibilidad=(0.9, 1.0),
    ),

    "factor_muro_eleccion": Criterio(
        valor=1.0,
        etiqueta="A",
        concepto="Factor de reduccion del coeficiente sismico por "
                 "desplazamiento: fila elegida de la tabla del numeral",
        justificacion="El cabezal esta empotrado en el terraplen y no tiene "
                      "desplazamiento lateral admisible garantizado de 25-50 mm. "
                      "Se adopta el caso de muro rigido, sin reduccion",
        fuente="Tabla FACTOR_MURO_TABLA del Manual de Puentes num. 2.8.1.1.14.2 "
               "(valores [N]: rigido = 1.0, desplazable = 0.5). La ELECCION de "
               "la fila es [A]",
        reemplazado_por="Diseno de detalle del cabezal que garantice (o "
                        "descarte) un desplazamiento admisible de 25-50 mm",
        sensibilidad=(0.5, 1.0),
    ),

    "k_v": Criterio(
        valor=0.0,
        etiqueta="A",
        concepto="Coeficiente sismico vertical para Mononobe-Okabe",
        justificacion="Adopcion habitual en analisis pseudo-estatico de muros de "
                      "contencion de baja altura",
        fuente="Practica corriente; no fijado por el Manual de Puentes",
        sensibilidad=(0.0, 0.5),   # 0.5*k_h como escenario alterno
    ),

    # Los cuatro angulos que Sec. 9.2 exige ADEMAS de la cadena sismica para
    # cerrar Mononobe-Okabe: "se requieren ademas phi del relleno, pendiente
    # del relleno (i), inclinacion del muro (beta) y friccion muro-suelo
    # (delta)". El primero ya esta declarado abajo como 'phi_relleno_trasdos'
    # (bloque GEOTECNIA), porque no es solo del sismo: gobierna tambien el Ka
    # estatico. Los otros tres viven aqui.

    "pendiente_relleno_trasdos_i": Criterio(
        valor=None,                 # VACIO: bloquea K_AE y el Ka de Coulomb
        etiqueta="A",
        concepto="Inclinacion de la superficie del relleno del trasdos sobre "
                 "la horizontal (i), en grados, para Mononobe-Okabe",
        justificacion="Sec. 9.2 la exige por su nombre y no la entrega, y "
                      "Sec. 1.2 no trae ninguna columna de geometria del "
                      "cabezal ni del terraplen sobre el trasdos. No se "
                      "puede deducir del CSV: la altura de terraplen del "
                      "punto (cota_rasante - cota_terreno) es un desnivel, "
                      "no la pendiente de la superficie contra el muro. "
                      "Adoptar i = 0 en silencio parece inocuo y no lo es: "
                      "en Mononobe-Okabe i entra en sen(phi - psi - i), y "
                      "con psi = 26.6 grados (k_h = 0.50) el radicando se "
                      "anula para phi - i cerca de psi -- es decir, unos "
                      "pocos grados de relleno inclinado pueden llevar el "
                      "empuje sismico al infinito. Es el parametro con la "
                      "sensibilidad mas violenta de toda la Fase 9",
        fuente="PENDIENTE - seccion tipica del expediente vial sobre el "
               "cabezal (DG-2018) o el detalle de coronacion del terraplen",
        reemplazado_por="Geometria medida sobre la seccion transversal del "
                        "punto de cruce",
        sensibilidad=(0.0, 10.0),   # grados; horizontal frente a talud suave
        verificacion_pendiente="Declarar si el relleno corona horizontal "
                               "contra el muro (i = 0) o continua con el "
                               "talud del terraplen: son dos detalles "
                               "constructivos distintos, no un matiz",
    ),

    "inclinacion_muro_beta": Criterio(
        valor=None,                 # VACIO: bloquea K_AE y el Ka de Coulomb
        etiqueta="A",
        concepto="Inclinacion del paramento interior (trasdos) del cabezal "
                 "respecto de la VERTICAL (beta), en grados, positiva cuando "
                 "el muro se aleja del relleno",
        justificacion="Es geometria del cabezal, y Sec. 9 no lo dimensiona: "
                      "la hoja de ruta fija el detalle de EMBOCADURA (tubo a "
                      "ras del muro, square edge, Sec. 9.1 y Tablero 2.3) "
                      "pero no el talud del paramento. Un cabezal de "
                      "paramento vertical (beta = 0) y uno con talud de "
                      "1:10 dan K_AE distintos, y el signo de beta se presta "
                      "a error: se declara con la convencion de "
                      "Mononobe-Okabe, no con la del plano",
        fuente="PENDIENTE - predimensionamiento del cabezal; ver el criterio "
               "'predimensionamiento_cabezal', del que este angulo es parte",
        reemplazado_por="Plano de encofrado del cabezal del expediente",
        sensibilidad=(0.0, 10.0),   # grados
    ),

    "friccion_muro_suelo_delta": Criterio(
        valor=None,                 # VACIO: bloquea K_AE y el Ka de Coulomb
        etiqueta="A",
        concepto="Angulo de friccion entre el paramento del muro y el relleno "
                 "(delta), en grados, para Mononobe-Okabe",
        justificacion="Sec. 9.2 lo exige por su nombre y no lo entrega. La "
                      "practica corriente lo liga a phi del relleno (del "
                      "orden de phi/2 a 2*phi/3 en concreto contra suelo "
                      "granular), pero la hoja de ruta no fija esa fraccion "
                      "y adoptarla en silencio moveria a la vez el empuje "
                      "estatico y el sismico. Ademas no es conservador por "
                      "un lado solo: un delta alto reduce K_AE (favorable "
                      "para el empuje) y a la vez inclina la resultante, "
                      "cambiando el reparto entre deslizamiento y volteo",
        fuente="PENDIENTE - se declara como fraccion de 'phi_relleno_trasdos' "
               "con la fuente tecnica que la sostenga, o se mide",
        reemplazado_por="Ensayo de interfase concreto-relleno, o adopcion "
                        "declarada como fraccion de phi con su fuente",
        sensibilidad=(0.0, 22.7),   # grados; delta=0 (conservador) a 2*phi/3 con phi=34
        verificacion_pendiente="Declararlo como FRACCION de phi y no como "
                               "angulo suelto, para que al ajustar "
                               "'phi_relleno_trasdos' no queden incoherentes",
    ),

    "punto_aplicacion_incremento_sismico": Criterio(
        valor=None,                 # VACIO: bloquea el momento de volteo sismico
        etiqueta="A",
        concepto="Altura de aplicacion del incremento sismico de empuje "
                 "(P_AE - P_A), como fraccion de la altura H del muro",
        justificacion="Mononobe-Okabe entrega el empuje TOTAL, no su punto de "
                      "aplicacion. El empuje estatico si lo tiene sin "
                      "adoptar nada: su distribucion es triangular y la "
                      "resultante cae en H/3, que es el centroide del "
                      "triangulo, no un criterio. El INCREMENTO sismico no es "
                      "triangular y su altura de aplicacion es una convencion "
                      "de la literatura (Seed-Whitman la sitea del orden de "
                      "0.6H); la hoja de ruta no la fija. Sin ella no hay "
                      "brazo, y sin brazo no hay momento de volteo sismico: "
                      "la fila 'volteo / sismico' de la tabla de Sec. 9.3 no "
                      "se puede evaluar",
        fuente="PENDIENTE - Sec. 9.2 entrega K_AE y se detiene ahi. "
               "Seed-Whitman (0.6H) o AASHTO LRFD Sec. 11, declarado con su "
               "fuente en la memoria",
        reemplazado_por="Convencion adoptada y escrita en la memoria de calculo",
        sensibilidad=(0.333, 0.6),   # H/3 (empuje total en el centroide) a 0.6H
    ),

    # ----------------------- HIDROLOGIA -----------------------------------

    "homogeneidad_serie_fen": Criterio(
        valor=None,                 # VACIO: bloquea el Q de diseno de TODOS los puntos
        etiqueta="A",
        concepto="Tratamiento de la poblacion mixta de la serie de precipitacion "
                 "maxima anual (anios FEN frente a anios neutros)",
        justificacion="La serie de Piura no es de poblacion unica: 1983, 1998 y "
                      "2017 no pertenecen estadisticamente a la misma poblacion "
                      "que los anios neutros. Si la serie los CONTIENE, el ajuste "
                      "K-S puede estar dominado por dos o tres outliers y hay que "
                      "reportar el ajuste con y sin ellos y adoptar el mas "
                      "conservador. Si NO los contiene, el Q de diseno esta "
                      "subestimado de forma grave y es una limitacion central",
        fuente="PENDIENTE - Fase 1-bis de la hoja de ruta. Requiere la serie "
               "SENAMHI con su longitud de registro, estacion y anios faltantes",
        reemplazado_por="Analisis de homogeneidad sobre la serie SENAMHI completa",
        verificacion_pendiente="Tablero 3.2: verificar si la serie contiene 1983, "
                               "1998 y 2017. Va ANTES de la Fase 4. "
                               "COMO BLOQUEA, que no es como los demas y "
                               "conviene saberlo (SIS-B-11): ningun modulo "
                               "llama a `valor('homogeneidad_serie_fen')`. El "
                               "bloqueo es INDIRECTO -- el hidrologo no "
                               "entrega Q hasta cerrar la homogeneidad, la "
                               "columna 'Q_m3s' llega vacia y salta "
                               "DatoFaltanteError -- y esta escrito en el "
                               "docstring de `MD.disenar_lote`. La "
                               "consecuencia: si el CSV trae 'Q_m3s' LLENO, "
                               "nada obliga a declarar como se trato la "
                               "poblacion mixta, y este criterio saldra en el "
                               "bloque de pendientes de la memoria sin haber "
                               "detenido nada. Quien reciba un CSV con Q ya "
                               "calculado tiene que exigir, aparte, el "
                               "analisis de homogeneidad que lo respalda",
    ),

    "umbral_area_quebrada_importante_ha": Criterio(
        valor=None,                 # VACIO: bloquea el TR de toda la Familia A
        etiqueta="A",
        concepto="Area de cuenca a partir de la cual el cauce de un punto de "
                 "Familia A se clasifica como 'quebrada importante' (TR 71) en "
                 "vez de 'quebrada menor' (TR 35) en la Tabla N 02",
        justificacion="FORMALIZADO COMO [A] TRAS VERIFICACION EXTERNA DEL "
                      "MANUAL. Lo que la Tabla N 02 (num. 3.6) del Manual de "
                      "Hidrologia entrega son las dos filas con su riesgo "
                      "admisible R y su vida util n, y de ahi sale el TR de "
                      "cada categoria. Lo que NO entrega -- ni esa tabla ni "
                      "ningun otro apartado del Manual -- es una REGLA DE "
                      "ASIGNACION FISICA que diga cuando un cauce cae en una "
                      "categoria o en la otra: no hay umbral de area, ni de "
                      "caudal, ni de longitud, ni de orden de cauce. El "
                      "Manual nombra las categorias y las tarifa; no las "
                      "define. Sec. 2.3 de la hoja de ruta hereda el hueco y "
                      "se limita a decir que la Familia A lleva 'TR 71 o 35 "
                      "anios'. "
                      "Por eso es [A] y no [C]: un [C] necesitaria una fuente "
                      "tecnica reconocida que SI fije el criterio, y aqui no "
                      "la hay -- el vacio esta en la norma y no se cubre "
                      "prestandolo de otra. Y no es menor: entre una fila y "
                      "la otra el TR se duplica, y con el suben la intensidad "
                      "de la IDF y el Q de diseno de todos los puntos de "
                      "paso. "
                      "Se elige el AREA DE CUENCA como descriptor porque es "
                      "el unico dato del CSV que Sec. 1.1 califica "
                      "expresamente de 'solo clasificador': no entra en "
                      "ninguna formula y existe justamente para esto. Elegir "
                      "el descriptor tambien es parte de la adopcion -- el "
                      "Manual tampoco dice que haya que clasificar por area. "
                      "Lo que falta es el umbral. "
                      "ALTERNATIVA sin este criterio: clasificar cauce por "
                      "cauce y pasar la categoria explicita a M1, que la "
                      "acepta como argumento; entonces la eleccion se "
                      "documenta punto por punto en la memoria en vez de por "
                      "regla",
        fuente="PENDIENTE - Manual de Hidrologia, Hidraulica y Drenaje (MTC), "
               "Tabla N 02 (num. 3.6): da R y n por categoria de cauce y NO "
               "define 'quebrada importante' ni 'quebrada menor' por umbral "
               "de area, longitud ni caudal. Verificado contra el texto",
        reemplazado_por="Clasificacion del cauce documentada punto por punto "
                        "(categoria explicita a M1), o umbral tomado de un "
                        "estudio hidrologico de la cuenca del Bajo Piura",
        verificacion_pendiente="Si se adopta un umbral, declarar en la memoria "
                               "que puntos quedan a cada lado y correr la "
                               "sensibilidad del Q con TR 71 y TR 35: es la "
                               "misma alcantarilla con dos caudales de diseno",
    ),

    # ----------------------- HIDRAULICA: vacios ---------------------------

    "hds5_embocadura_hdpe": Criterio(
        valor={"K": 0.0098, "M": 2.00, "c": 0.0398, "Y": 0.67, "Ks": -0.5},
        etiqueta="C",
        concepto="Constantes de control de entrada HDS-5 para tuberia HDPE",
        justificacion="La Tabla A.1 se organiza en cartas por forma/material y, "
                      "dentro de cada carta, por configuracion de borde: la misma "
                      "'square edge w/headwall' tiene K=0.0098 en concreto y "
                      "K=0.0078 en metal corrugado. Esa diferencia responde al "
                      "PERFIL DE PARED EN LA BOCA (lisa vs corrugada), no a la "
                      "friccion del barril. El HDPE de interior liso cortado a ras "
                      "del muro presenta en la boca pared lisa y borde cuadrado: "
                      "misma condicion de entrada que el concreto",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Apendice A, Tabla A.1, "
               "pag. A.8, fila 'Circular Concrete / Square edge w/headwall'. "
               "Los cinco valores confirman contra esa fila y la pagina es la "
               "correcta (verificado por la auditoria normativa, NOR-ANA-03)",
        sensibilidad=("Tabla A.1, fila 'Circular Concrete / Square edge "
                      "w/headwall' (la adoptada): K=0.0098, c=0.0398, Y=0.67",
                      "Tabla A.1, fila 'Circular CM / Headwall' (la "
                      "alternativa): K=0.0078, c=0.0379, Y=0.69"),
        verificacion_pendiente="LA ANALOGIA NO ES CONSERVADORA, Y HAY QUE "
                               "DECLARARLO EN LA MEMORIA (NOR-ANA-03). En la "
                               "rama sumergida HW_i/D = c*q*^2 + Y + Ks*S, la "
                               "fila del concreto adoptada da un HW MENOR que "
                               "la fila del metal corrugado en todo el rango "
                               "de q* de interes (c y Y son ambos menores: "
                               "0.0398 vs 0.0379 con Y 0.67 vs 0.69 -- el "
                               "termino independiente pesa mas). Un HW mas bajo "
                               "es la direccion INSEGURA para V1, para V4 y "
                               "para el resguardo de 7.A. La adopcion se "
                               "sostiene en el argumento fisico de arriba -- el "
                               "perfil de pared EN LA BOCA, no la friccion del "
                               "barril -- y no en un margen de seguridad: son "
                               "dos cosas distintas y el criterio declaraba "
                               "solo la primera. Lo que cierra el punto no es "
                               "cambiar de fila (la de metal seria otra "
                               "analogia, elegida por su resultado y no por su "
                               "fundamento) sino el detalle constructivo: "
                               "confirmar que el tubo enrasa en la cara del "
                               "cabezal con pared interior lisa. Si aloja "
                               "campana, sobresale o el HDPE es de interior "
                               "corrugado, corresponde otra fila y la "
                               "alternativa de la sensibilidad pasa a ser la "
                               "adoptada",
    ),

    "metodo_transicion_hds5": Criterio(
        valor="interpolacion_lineal_entre_extremos",
        etiqueta="C",
        concepto="Metodo con que se cubre la zona de transicion del control de "
                 "entrada de HDS-5, 3.5 < q* < 4.0",
        justificacion="Sec. 4.2 de la hoja de ruta resuelve la transicion con "
                      "'interpolar linealmente', y eso es lo que M4 implementa: "
                      "una recta entre la forma NO SUMERGIDA evaluada en "
                      "q* = 3.5 y la SUMERGIDA evaluada en q* = 4.0. Lo que se "
                      "declara aqui es que ESO NO ES EL METODO DEL HDS-5. "
                      "HDS-5 no interpola linealmente: en la zona de transicion "
                      "traza a mano una curva TANGENTE a las dos ramas, un "
                      "empalme empirico ajustado sobre los datos de laboratorio "
                      "del que no publica ecuacion cerrada. La recta es una "
                      "SIMPLIFICACION ADOPTADA de ese empalme, no una "
                      "transcripcion de la fuente primaria, y por eso es [C] y "
                      "no [N]: la fuente tecnica reconocida existe (HDS-5) pero "
                      "el procedimiento programable no sale de ella. "
                      "Que la recta empalme continua en los dos extremos "
                      "(coincide con cada rama en su borde de validez) hace el "
                      "error acotado y del orden del espesor de la propia "
                      "curva de HDS-5, no lo convierte en el metodo del HDS-5. "
                      "ALCANCE: solo afecta a los puntos cuyo q* cae dentro de "
                      "la ventana 3.5-4.0; fuera de ella rigen las dos "
                      "ecuaciones tal cual las escribe la tabla",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Cap. IV y Apendice A "
               "(curva de transicion tangente, sin ecuacion publicada). La "
               "interpolacion lineal la prescribe Sec. 4.2 de la hoja de ruta, "
               "no HDS-5",
        reemplazado_por="Lectura directa de la carta de HDS-5 en la zona de "
                        "transicion, o el procedimiento tangente si el "
                        "expediente exige reproducir la curva original",
        verificacion_pendiente="Declarar en la memoria que puntos del corredor "
                               "caen con q* entre 3.5 y 4.0: si ninguno lo hace, "
                               "esta simplificacion no toca ningun resultado y "
                               "basta con dejarla enunciada",
    ),

    "n_manning_hdpe": Criterio(
        # El valor NO se escribe: se LEE de la tabla normativa de la que sale
        # por analogia. Escrito a mano era el mismo par (0.010, 0.013) copiado
        # del concreto, sin nada que ligara las dos copias: si alguien
        # corrigiera la Tabla N 09, esta seguiria con el valor viejo y la
        # "analogia" habria dejado de serlo en silencio (SIS-D-11).
        valor=MANNING["concreto_recto"],   # RANGO (n_min, n_max), no puntual
        etiqueta="N->",             # analogia normativa declarada, no adopcion
        concepto="Coeficiente de rugosidad de Manning para HDPE de interior liso",
        justificacion="La Tabla N 09 del Manual MTC no lista HDPE. Se adopta el "
                      "RANGO COMPLETO del concreto por analogia. Un valor puntual "
                      "(p.ej. 0.012) romperia la regla de doble n: n_max para "
                      "capacidad y n_min para velocidad y socavacion. Con un solo "
                      "numero, una de las dos verificaciones deja de ser conservadora. "
                      "ETIQUETA: es [N->] y no [A]. La regla de coherencia de la "
                      "hoja de ruta (num. 40) lo dice literal -- un criterio "
                      "justificado invocando una disposicion normativa no puede "
                      "etiquetarse [A] -- y aqui la justificacion ES una fila de "
                      "una tabla normativa aplicada por analogia a un material que "
                      "esa tabla no lista, que es la definicion de [N->]. Los dos "
                      "casos gemelos del archivo ('resguardo_HW_subrasante' y "
                      "'h_relleno_min_concreto_tmc', hoy retirado) ya llevaban "
                      "[N->] por lo mismo. La hoja de ruta se contradice a si misma al escribir "
                      "[A] para este criterio en su Anexo A: manda su propia regla "
                      "de coherencia, no la fila del indice",
        fuente="Analogia a Tabla N 09 (concreto, tubo recto), num. 4.1.1.3.5, "
               "transcrita en constantes_normativas.MANNING",
        reemplazado_por="Ficha tecnica del producto seleccionado",
        sensibilidad=MANNING["concreto_recto"],
        verificacion_pendiente="Confirmar que el HDPE especificado es de INTERIOR "
                               "LISO. El de interior corrugado tiene n del orden de "
                               "0.018-0.025 y la analogia seria gruesamente insegura",
    ),

    "v_max_hdpe": Criterio(
        valor=4.6,
        etiqueta="C",               # Anexo A y Sec. 0.1: la fuente (WSDOT)
                                    # es tecnica reconocida, no una adopcion libre
        concepto="Velocidad maxima admisible en HDPE",
        justificacion="La Tabla N 10 del Manual MTC no cubre materiales flexibles",
        fuente="WSDOT Hydraulics Manual M 23-03.12 (abril 2026), Cap. 8, S8-6, "
               "Tabla 8-4 'Pipe Abrasion Levels', pp. 8-27/8-28. Techo duro: "
               "por encima de 15 ft/s el termoplastico no puede reforzarse "
               "estructuralmente y su uso queda prohibido por la propia tabla.",
        reemplazado_por="Ficha tecnica del producto seleccionado o "
                        "especificacion del fabricante con su propio techo de "
                        "velocidad; y, para el expediente, la transcripcion "
                        "de la Tabla 8-4 al repositorio de normas",
        # POR QUE NO LLEVA `vacio_verificado`, siendo una afirmacion negativa
        # sobre la Tabla N 10 (SIS-D-12): el campo es para el valor que cubre
        # un vacio AGOTADO -- una busqueda cerrada fuente por fuente que
        # termino sin encontrar nada. El ejemplo que este comentario citaba
        # -- 'h_relleno_min_concreto_tmc' en Sec. 14.a -- ya no sirve como
        # ejemplo de nada: aquel vacio se declaro agotado sin haber mirado
        # AASHTO LRFD Art. 12.6.6.3, que lo cerraba, y el criterio se retiro
        # (NOR-VAC-01). Aqui no hubo vacio que agotar: la busqueda ENCONTRO
        # una fuente tecnica reconocida y el valor sale de ella. Es una cita
        # cerrada, que el manifiesto registra en su Sec. 10-bis, y por eso
        # este criterio es [C] con fuente y no una adopcion sobre un hueco.
        # Marcarlo como vacio verificado lo imprimiria en el bloque de
        # acotaciones de la memoria, que dice "el proyectista adopto esto
        # donde la norma no dice nada": seria falso.
    ),

    "v_max_tmc": Criterio(
        valor=4.6,
        etiqueta="C",               # idem v_max_hdpe: Anexo A lo etiqueta [C]
        concepto="Velocidad maxima admisible en TMC",
        justificacion="La Tabla N 10 del Manual MTC no cubre materiales flexibles",
        fuente="WSDOT Hydraulics Manual M 23-03.12 (abril 2026), Cap. 8, S8-6, "
               "Tabla 8-4 'Pipe Abrasion Levels', pp. 8-27/8-28. La fuente NO "
               "fija techo absoluto para metal -- por encima de este valor "
               "exige mayor calibre o revestimiento, no prohibe el material. "
               "Se adopta 4.6 m/s como limite de diseno conservador porque el "
               "catalogo de M2 no modela proteccion adicional por calibre.",
        reemplazado_por="Ficha tecnica del producto seleccionado, o el "
                        "modelado del calibre y el revestimiento en el "
                        "catalogo de M2 (que es lo que la fuente pide en vez "
                        "de un techo unico); y, para el expediente, la "
                        "transcripcion de la Tabla 8-4 al repositorio de "
                        "normas",
        # Mismo motivo que en 'v_max_hdpe' para no llevar `vacio_verificado`:
        # cita cerrada sobre fuente tecnica (Sec. 10-bis del manifiesto), no
        # dossier de vacio agotado (SIS-D-12).
    ),

    "v_max_concreto_eleccion": Criterio(
        valor=None,                 # OPCIONAL: sin valor, V3 usa el techo [N]
        etiqueta="A",
        concepto="Techo de velocidad adoptado para el concreto, mas "
                 "conservador que el maximo normativo de 6.0 m/s",
        justificacion="OPCIONAL, no un vacio: sin valor el calculo NO se "
                      "detiene, V3 aplica el techo normativo de 6.0 m/s y la "
                      "memoria no declara este criterio. Es el unico "
                      "`opcional=True` del archivo, y por eso el unico que se "
                      "lee con `valor_si_declarado()` PORQUE ES OPCIONAL. "
                      "CORRIGE la redaccion anterior, que decia 'la unica "
                      "entrada que se lee con valor_si_declarado()': no lo "
                      "es. M2 lee asi otras cuatro claves NO opcionales "
                      "('n_manning_hdpe', 'espesor_pared_conducto', "
                      "'v_max_tmc', 'v_max_hdpe') para poder armar el "
                      "catalogo con campos vacios y que el bloqueo salte en "
                      "el punto de uso; la diferencia es que aquellas SI "
                      "detienen el calculo mas tarde y esta no detiene nada "
                      "nunca. Confundir las dos cosas es lo que la palabra "
                      "'unica' hacia. "
                      "La Tabla N 10 se titula 'Velocidades maximas "
                      "admisibles en conductos revestidos' (num. 4.1.1.3.6, "
                      "pag. 76): sus dos numeros son MAXIMOS segun la calidad "
                      "del revestimiento, y 6.0 m/s es el techo del acabado "
                      "de mejor calidad. Un concreto de acabado corriente "
                      "admite menos, y bajar el techo hasta 3.0 m/s -- el "
                      "maximo del acabado mas pobre -- es una decision "
                      "defendible del proyectista sobre las condiciones de "
                      "ESTA obra, no una exigencia del numeral: por eso [A]. "
                      "CORRIGE la redaccion anterior, que lo planteaba como "
                      "'elegir un valor dentro del rango' dando por hecho que "
                      "3.0 era un PISO a decidir. No lo es: el piso de "
                      "velocidad es V2 (0.25 m/s, misma pagina) y vale para "
                      "todos los materiales. Con aquella lectura, V3 rechazaba "
                      "conductos de concreto perfectamente admisibles",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, "
               "RD 20-2011-MTC/14), Tabla N 10 'Velocidades maximas "
               "admisibles en conductos revestidos', num. 4.1.1.3.6, "
               "pag. 76. "
               "DE DONDE SALE EL DEFECTO: los dos numeros de la fila del "
               "concreto, 3.0 y 6.0 m/s, son ambos MAXIMOS -- el rango "
               "recorre la calidad del revestimiento, no un piso y un techo. "
               "6.0 m/s es el maximo del acabado de mejor calidad, y es el "
               "valor [N] que V3 aplica cuando este criterio no se declara. "
               "3.0 m/s es el maximo del acabado mas pobre, y por eso es el "
               "otro extremo del rango de sensibilidad: entre 3.0 y 6.0 esta "
               "todo lo que el proyectista puede adoptar sin salirse de la "
               "tabla. Bajar el techo dentro de ese rango, por las "
               "condiciones de acabado de ESTA obra, no lo normaliza ningun "
               "numeral: es adopcion declarada, y por eso [A] y no [N]. "
               "El piso de velocidad NO sale de esta tabla: es V2, 0.25 m/s "
               "de la misma pagina, y vale para todos los materiales",
        sensibilidad=(3.0, 6.0),
        opcional=True,      # sin declarar, V3 aplica el techo [N] de 6.0 m/s
    ),

    "ke_entrada": Criterio(
        valor=0.5,
        etiqueta="C",
        concepto="Coeficiente de perdida de carga en la embocadura (ke)",
        justificacion="La ecuacion de control de salida de la hoja de ruta, "
                      "H = (1 + ke + 19.63*n^2*L/R^(4/3))*V^2/(2g), contiene ke "
                      "pero ningun apartado de la hoja le asigna valor. El "
                      "Manual MTC no desarrolla el control de salida, de modo "
                      "que el dato sale de HDS-5, en la fila que corresponde a "
                      "la embocadura ya adoptada por diseno: tubo a ras del "
                      "muro (square edge with headwall). "
                      "TRAZABILIDAD: este 0.5 ya estaba en uso como dato fijo "
                      "en el caso patron CP-8 de tests/fixtures/casos_patron.py "
                      "('ke': 0.5), donde entra en el calculo de H sin declarar "
                      "de donde salia. Queda trazado aqui: el fixture y el "
                      "calculo leen ahora el mismo origen, y si el valor cambia, "
                      "cambia en un solo sitio",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Apendice C, Tabla C.2, "
               "pag. C.2 - coeficientes de perdida de entrada; fila 'square "
               "edge with headwall', ke = 0.5. CITA CERRADA por verificacion "
               "externa contra el documento: antes se citaba el manual sin "
               "apendice, tabla ni pagina, y lo que quedaba pendiente era "
               "exactamente eso",
        reemplazado_por="Fila de HDS-5 que corresponda si cambia el detalle de "
                        "embocadura del cabezal (Tablero 2.3). La Tabla C.2 "
                        "trae las demas configuraciones de borde",
    ),

    "geometria_control_salida": Criterio(
        valor="seccion_llena",
        etiqueta="C",
        concepto="Seccion de referencia de la que se toman V y R en la ecuacion "
                 "de control de salida H = (1 + ke + 19.63*n^2*L/R^(4/3))*V^2/(2g)",
        justificacion="Sec. 4.3 escribe la ecuacion pero NO dice a que seccion "
                      "pertenecen V y R, y la eleccion no es cosmetica: con la "
                      "seccion llena de un tubo de 0.90 m, R = D/4 = 0.225 m; con "
                      "el tirante normal de y/D = 0.75, R = 0.2715 m. La misma "
                      "formula da dos H distintas. Se adopta la SECCION LLENA "
                      "(A = pi*D^2/4, R = D/4, V = Q/A) porque es la seccion para "
                      "la que HDS-5 deriva esa expresion: los tres sumandos "
                      "(1 = carga de velocidad, ke = perdida de entrada, "
                      "19.63*n^2*L/R^(4/3) = perdida por friccion) son las "
                      "perdidas de un barril trabajando LLENO, que es el caso de "
                      "control de salida por definicion. Aplicarla sobre la "
                      "geometria del tirante normal mezcla dos regimenes. "
                      "TRAZABILIDAD: el caso patron CP-8 de "
                      "tests/fixtures/casos_patron.py alimenta la formula con "
                      "R = 0.27152 y V = 2.2807, que son los de la seccion "
                      "parcialmente llena de CP-2. CP-8 no contradice esto: es un "
                      "caso patron de la CONSTANTE SI (19.63) frente al 29 imperial, "
                      "y "
                      "para eso da V y R como datos sueltos, no como la geometria "
                      "de un control de salida real",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Cap. III - control de salida a "
               "seccion llena. Sec. 4.3 de la hoja de ruta cita la ecuacion sin "
               "definir la seccion",
        reemplazado_por="Procedimiento de barril parcialmente lleno de HDS-5 "
                        "(longitud de la seccion llena, Cap. III) si el "
                        "expediente lo exige",
        verificacion_pendiente="Con TW bajo y pendiente pronunciada el barril "
                               "puede no llegar a llenarse y el control de salida "
                               "no gobierna igualmente; verificar que el punto "
                               "donde el control de salida GOBIERNE sea uno donde "
                               "la hipotesis de seccion llena tenga sentido fisico",
    ),

    "HW_D_max": Criterio(
        valor=1.5,
        etiqueta="C",
        concepto="Relacion maxima de carga a la entrada sobre diametro",
        justificacion="El Manual MTC no define HW/D. Se adopta el extremo "
                      "superior del rango que HDS-5 da para el diseno "
                      "corriente, 1.0-1.5. El control gobernante del embalse "
                      "sigue siendo la verificacion V5 (remanso dentro del "
                      "derecho de via). "
                      "SOBRE LA SENSIBILIDAD: la banda declarada es "
                      "(1.2, 1.5), no el rango completo (1.0, 1.5) de la "
                      "fuente. Se conserva a proposito -- es la banda que el "
                      "proyecto considera defendible para este corredor -- y "
                      "se deja dicho que es un SUBRANGO, para que nadie la "
                      "confunda con lo que dice HDS-5",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Sec. 2.2.5, pag. 2.14 - "
               "rango de HW/D de 1.0 a 1.5 para el diseno corriente. CITA "
               "CERRADA por verificacion externa contra el documento: antes "
               "decia solo 'practica corriente', sin seccion ni pagina",
        sensibilidad=(1.2, 1.5),
    ),

    "resguardo_HW_subrasante": Criterio(
        valor="segun_CBR",          # 0.60 / 0.80 / 1.00 / 1.20 m
        etiqueta="N->",
        concepto="Resguardo entre nivel de agua a la entrada y subrasante",
        justificacion="El numeral 4.5.4 regula la separacion frente al NIVEL "
                      "FREATICO, no frente a un nivel transitorio de avenida. Se "
                      "aplica POR ANALOGIA por ser el unico parametro normativo "
                      "nacional que protege la subrasante de la saturacion, y la "
                      "analogia debe declararse en la memoria. "
                      "QUE LA ANALOGIA QUEDE DEL LADO SEGURO ES PLAUSIBLE, NO "
                      "DEMOSTRADO (NOR-ANA-02). Este campo decia 'la analogia es "
                      "conservadora' como si fuera un hecho establecido, y no lo "
                      "es: el resguardo del 4.5.4 protege la subrasante del "
                      "ASCENSO CAPILAR CONTINUO de un freatico permanente, "
                      "mientras que un HW de avenida moja el terreno durante "
                      "horas, por un mecanismo distinto, y puede subir por encima "
                      "del freatico. Que el resguardo dimensionado para el primer "
                      "mecanismo baste para el segundo no se deduce del numeral "
                      "ni de ningun otro del Manual de Suelos. Se conserva la "
                      "adopcion -- no hay parametro nacional que la sustituya -- "
                      "y se retira la afirmacion de conservadurismo, que era la "
                      "unica parte que la fuente no sostenia. La auditoria "
                      "normativa confirmo lo demas: el numeral regula lo que se "
                      "le atribuye, la tabla es la que el codigo transcribe y la "
                      "etiqueta [N->] es la correcta",
        fuente="Manual de Suelos MTC, numeral 4.5.4 (pags. 41-42) y 9.1(3) "
               "(pags. 89-90), que repite la tabla en el capitulo de "
               "estabilizacion",
        verificacion_pendiente="La equivalencia entre saturacion permanente "
                               "(el mecanismo del 4.5.4) y mojado transitorio "
                               "por avenida (el de V4) queda sin demostrar. "
                               "Cerrarla exige una fuente que trate el "
                               "remanso de avenida sobre la subrasante, no una "
                               "lectura mas del mismo numeral",
    ),

    "TW_receptor": Criterio(
        valor=None,                 # VACIO hasta obtener Q del receptor
        etiqueta="A",
        concepto="Nivel de agua en el cuerpo receptor durante la avenida",
        justificacion="No se mide: se calcula con Manning en el receptor usando "
                      "su propio caudal de diseno. Sin ese dato se adoptan dos "
                      "escenarios acotados (salida libre / seccion llena)",
        fuente="PENDIENTE: ANA / Junta de Usuarios del Bajo Piura",
        reemplazado_por="Caudal de diseno documentado del dren o canal receptor",
    ),

    "long_max_cuneta": Criterio(
        valor=200.0,
        etiqueta="A",
        concepto="Longitud maxima de cuneta -> espaciamiento de alcantarillas de alivio",
        justificacion="El Manual fija 250 m para region seca y 200 m para region "
                      "muy lluviosa. El regimen normal de Piura es arido, pero el "
                      "evento de diseno relevante es el FEN, durante el cual la "
                      "zona se comporta como region muy lluviosa. Se adopta 200 m",
        fuente="Manual MTC, numeral 4.1.2.1 d), pag. 178",
        sensibilidad=(200.0, 250.0),
    ),

    # ----------------------- FASE 5: VACIOS DE VERIFICACION ---------------
    # Tres filas de la tabla de Fase 5 (V5, V7, V8) enuncian el REQUISITO
    # pero no entregan la formula ni el dato con que M5 pueda evaluarlo.
    # Cada uno se detiene aqui, no en M5, para que quede escrito por que
    # falta y que lo resolveria -- nunca un valor supuesto en silencio.
    #
    # V7 ya NO es de esta clase: Fase 8 (M8_estructural.py) implementa el
    # procedimiento completo, y desde la correccion del marco LRFD es un
    # equilibrio de factores de carga, no un FS global. Lo que sigue faltando
    # son dos datos puntuales del procedimiento -- 'peso_especifico_relleno_kn_m3'
    # (mas abajo, seccion de Fase 8) y 'factores_carga_aashto' (seccion de
    # Fase 9, compartido con M9) -- no la formula ni el metodo, que ya estan
    # escritos.

    "origen_cota_fondo_entrada": Criterio(
        valor=None,                 # VACIO: bloquea V4, V7 y el tamizado 7.A
        etiqueta="A",
        concepto="Regla con la que se obtiene la cota del FONDO DE LA ENTRADA "
                 "(invert) de cada punto, msnm, mientras el expediente no la "
                 "entregue medida",
        justificacion="HW es una carga en metros SOBRE EL FONDO DE LA ENTRADA "
                      "(Sec. 4.2/4.3, `modelos.ResultadoHidraulico`), y "
                      "convertirla a cota -- que es lo que hacen V4, V7 y las "
                      "dos condiciones del tamizado 7.A -- exige esa cota. El "
                      "CSV de Sec. 1.2 NO trae columna de cota de fondo de "
                      "entrada: trae 'cota_terreno' (terreno natural, DEM), "
                      "'cota_rasante', 'cota_subrasante' y "
                      "'cota_fondo_receptor' (la del receptor, o sea la "
                      "SALIDA). La hoja de ruta tampoco fija la regla: Sec. "
                      "7.B pide las cotas de entrada y salida 'amarradas al "
                      "perfil del cauce y a la cota de fondo del receptor', "
                      "sin decir cual de las dos lecturas gobierna. "
                      "QUE ESTABA MAL: M5 adoptaba `punto.cota_terreno` "
                      "dentro del codigo, sin criterio, sin Anexo A y sin que "
                      "la memoria marcara el numero como supuesto (SIS-A-04). "
                      "Era la eleccion del proyectista escrita como si fuera "
                      "un dato, y es exactamente lo que este archivo existe "
                      "para impedir. "
                      "QUE SE HACE AHORA: la eleccion se declara aqui y no la "
                      "toma el programa. Valor admisible implementado hoy: "
                      "'cota_terreno' -- adoptar el terreno natural del cruce "
                      "como fondo de la entrada, que es la lectura mas "
                      "defendible a nivel de PERFIL con las columnas que el "
                      "CSV si trae y la que hace coincidir V4 con la segunda "
                      "condicion de 7.A. NO es conservadora por "
                      "construccion: si el invert real queda por debajo del "
                      "terreno (entrada excavada), la cota de HW calculada "
                      "es MAYOR que la real y V4 se vuelve exigente de mas; "
                      "si queda por encima (entrada elevada sobre relleno), "
                      "V4 se vuelve permisiva. Por eso es adopcion "
                      "declarada [A] y no analogia normativa",
        fuente="PENDIENTE - NINGUNA norma fija esta regla: no la da el Manual "
               "de Hidrologia (Sec. 4.2/4.3 define HW sobre el fondo, no como "
               "obtener el fondo), no la da la hoja de ruta (Sec. 7.B enuncia "
               "el amarre sin regla de calculo) y no es columna de Sec. 1.2. "
               "Es una decision del proyectista sobre ESTE expediente",
        reemplazado_por="Cota de fondo de entrada MEDIDA por punto "
                        "(nivelacion del perfil longitudinal del cauce en el "
                        "cruce), como columna propia del CSV. El dia que el "
                        "expediente la entregue, este criterio deja de "
                        "aplicarse: un dato medido no se sustituye por una "
                        "regla adoptada",
        verificacion_pendiente="Declarar en la memoria, punto por punto, si "
                               "la entrada proyectada queda excavada o "
                               "elevada respecto del terreno natural: es la "
                               "diferencia entre esta adopcion y el invert "
                               "real, y es la que decide si V4 y 7.A quedaron "
                               "del lado seguro en ese punto",
    ),

    "remanso_derecho_via": Criterio(
        valor=None,                 # VACIO: bloquea V5 para todo punto
        etiqueta="A",
        concepto="Extension del remanso aguas arriba de la alcantarilla y "
                 "ancho de derecho de via disponible en el punto, para V5 "
                 "(embalse dentro del derecho de via, sin afectar terceros "
                 "ni la faja marginal)",
        justificacion="Sec. 4.2 y el DG-2018 exigen la condicion pero no dan "
                      "metodo: la hoja de ruta no entrega un procedimiento de "
                      "perfil de remanso (curva de remanso aguas arriba del "
                      "embalse) ni el dato de ancho de derecho de via por "
                      "punto -- este ultimo tampoco es columna del CSV "
                      "(Sec. 1.2). Sin el metodo Y el dato, V5 no tiene con "
                      "que comparar el HW calculado por M4",
        fuente="PENDIENTE - Manual de Diseño Geometrico DG-2018 + Ley 29338 "
               "(Fase 5, V5). Requiere perfil de remanso (paso a paso o "
               "HEC-RAS) y el ancho de derecho de via del expediente vial",
        reemplazado_por="Perfil de remanso calculado aguas arriba del punto "
                        "y ancho de derecho de via declarado por punto",
        verificacion_pendiente="Definir si el ancho de derecho de via es un "
                               "dato por punto (nueva columna del CSV) o un "
                               "criterio unico del tramo",
    ),

    "TR_evento_extremo": Criterio(
        valor=None,                 # VACIO: bloquea V8 para todo punto
        etiqueta="A",
        concepto="Periodo de retorno del evento extremo de V8 y el umbral "
                 "que define 'la via no colapsa aunque desborde'",
        justificacion="Sec. 5 (V8) exige verificar el punto a un TR MAYOR "
                      "que el de diseno y confirmar que la via no colapsa "
                      "aunque desborde, pero la hoja de ruta no fija ese TR "
                      "mayor ni un umbral cuantitativo de 'colapso' (p.ej. "
                      "HW sobre la corona del terraplen). Sin el TR no hay "
                      "Q que correr por M3/M4 aparte del Q de diseno, y sin "
                      "el umbral no hay con que comparar el HW resultante",
        fuente="PENDIENTE - Fase 5, V8 de la hoja de ruta: '[N] verificacion, "
               "no diseño', sin numeral que fije el TR ni el umbral",
        reemplazado_por="TR del evento extremo (p.ej. el de la serie FEN de "
                        "la Fase 1-bis) y definicion tecnica de colapso de "
                        "la via, ambos declarados en la memoria",
    ),

    # ----------------------- GEOTECNIA -----------------------------------

    "phi_relleno_trasdos": Criterio(
        valor=None,                 # completar
        etiqueta="A",
        concepto="Angulo de friccion interna del material de cantera del trasdos",
        justificacion="Estimado por correlacion desde granulometria y grado de "
                      "compactacion especificado",
        fuente="PENDIENTE",
        reemplazado_por="Ensayo de corte directo sobre el material de cantera",
        sensibilidad=(30.0, 38.0),
    ),

    "c_phi_fundacion": Criterio(
        valor=None,                 # completar
        etiqueta="A",
        concepto="Parametros de resistencia del suelo de fundacion",
        justificacion="Correlacion desde clasificacion SUCS de calicatas. E.050 "
                      "Art. 20 obliga a usar solo uno: phi=0 en cohesivos, "
                      "c=0 en friccionantes",
        fuente="PENDIENTE",
        reemplazado_por="Corte directo o SPT",
        sin_consumidor="Su consumidor son las verificaciones de estabilidad "
                       "del cabezal E1-E5 (Sec. 9.3), que esta CLI declara "
                       "no ensamblar: ver la nota de alcance que la propia "
                       "corrida imprime. Se declara igual, y vacio, para que "
                       "el bloque de pendientes lo pida al expediente en vez "
                       "de que aparezca el dia del ensamblaje",
    ),

    "capacidad_portante_adm": Criterio(
        valor=None,                 # completar
        etiqueta="A",
        concepto="Capacidad portante admisible del terreno de fundacion",
        justificacion="Derivada de c_phi_fundacion, que es a su vez adoptado",
        fuente="PENDIENTE",
        reemplazado_por="EMS conforme a E.050",
        sin_consumidor="Mismo motivo que 'c_phi_fundacion', del que deriva: "
                       "lo consumen E1-E5 (Sec. 9.3), no ensambladas en esta "
                       "CLI",
    ),

    "Mw_licuefaccion": Criterio(
        valor=None,                 # VACIO: bloquea la evaluacion de licuefaccion
        etiqueta="A",
        concepto="Magnitud sismica para el factor de escala de magnitud (MSF)",
        justificacion="El procedimiento simplificado de evaluacion de licuefaccion "
                      "no se alimenta solo de a_max: requiere Mw para el MSF. El "
                      "mapa de PGA no la entrega",
        fuente="PENDIENTE: desagregacion del peligro sismico o adopcion justificada "
               "del sismo de diseno de la subduccion del norte peruano",
        reemplazado_por="Estudio de peligro sismico especifico",
        sin_consumidor="La evaluacion de licuefaccion esta declarada FUERA "
                       "del alcance del script (Sec. 0.5): el script no "
                       "calcula el factor de seguridad a licuefaccion, de "
                       "modo que nada invoca el MSF ni su Mw. Se declara "
                       "vacio para que el expediente lo programe, no porque "
                       "falte cablearlo",
    ),

    "demanda_sismica_licuefaccion": Criterio(
        valor=1000,                 # anios
        etiqueta="A",
        concepto="Periodo de retorno para la evaluacion de licuefaccion",
        justificacion="Se descarta el sismo de 475 anios de E.030. Al tratarse de "
                      "infraestructura vial regida por el Manual de Puentes, se "
                      "exige al suelo la misma demanda que a la estructura que "
                      "soporta. Un terreno evaluado a 475 anios bajo una estructura "
                      "disenada a 1000 es incoherencia de niveles de seguridad",
        fuente="Coherencia con el marco del Manual de Puentes",
        sensibilidad=(475, 1000),
        sin_consumidor="Igual que 'Mw_licuefaccion': la evaluacion de "
                       "licuefaccion esta fuera del alcance del script "
                       "(Sec. 0.5) y nada la invoca. Es uno de los dos "
                       "criterios CON valor y sin invocacion -- el otro es "
                       "'PERFIL_SUELO_PRESUNTO', en esta misma tabla -- y por "
                       "eso no caia en ninguno de los "
                       "bloques de la memoria: ni usado, ni vacio, ni "
                       "opcional. Desaparecia del HTML. La adopcion "
                       "(Tr = 1000 anios, §0.6 de la hoja de ruta, "
                       "descartando el sismo de 475 anios de E.030) tiene que "
                       "estar en la memoria aunque este calculo no corra: es "
                       "la que fija la demanda que el estudio geotecnico del "
                       "expediente debe exigirle al suelo",
    ),

    "diametros_normalizados": Criterio(
        valor={"inicio": 0.90, "paso": 0.15},
        etiqueta="C",
        concepto="Progresion de diametros normalizados (inicio y paso)",
        justificacion="Neutralidad comercial exigible en obra publica: no se usan "
                      "catalogos de proveedor. El paso de 0.15 m reproduce las "
                      "series de 6 pulgadas (ASTM/AASHTO: 6 in = 0.1524 m) y de "
                      "150 mm (M294) con error despreciable. Usar 0.90 en vez de "
                      "0.9144 (36 in) subestima el area ~3%, del lado de la "
                      "seguridad. "
                      "LOS TOPES YA NO ESTAN AQUI. Este criterio declaraba "
                      "tambien 'max' -- 2.70 / 2.10 / 1.50 m -- como si fuera la "
                      "misma clase de dato que el paso, y no lo es: el paso se "
                      "verifica contra la serie de la norma de producto y los "
                      "topes NO salen de ninguna norma (NOR-PRO-01, NOR-PRO-02, "
                      "MAT-O8). Viven ahora en 'D_max_catalogo', rotulados como "
                      "topes de catalogo",
        fuente="Series de diametro nominal de las normas de producto: ASTM "
               "A760/A760M-10, Tabla 1 'Tamaños de tuberia' (150 a 3600 mm, en "
               "escalones de 150 mm a partir de 900 mm); AASHTO M 170M-04, "
               "Tablas 1 a 5 (300 a 3600 mm); AASHTO M294 (serie de 150 mm). El "
               "piso de 0.90 m no sale de ellas sino del minimo normativo "
               "peruano: Manual de Hidrologia num. 4.1.1.3.4 a) "
               "(constantes_normativas.DIAMETRO_MIN)",
    ),

    "D_max_catalogo": Criterio(
        valor={"concreto_reforzado": 2.70, "tmc": 2.10, "hdpe": 1.50},
        etiqueta="A",
        concepto="Diametro maximo que el proyecto admite por material, como "
                 "tope de DISPONIBILIDAD (catalogo), no como tope normativo",
        de_catalogo="TOPE DE CATALOGO, NO DE NORMA. Imprimir siempre asi: "
                    "'diametro maximo adoptado por disponibilidad de mercado'. "
                    "Las normas de producto que el proyecto cita para cada "
                    "material NO topan el diametro donde este criterio lo topa "
                    "-- A760/A760M-10 tabula hasta 3600 mm y M 170M-04 tambien "
                    "--, de modo que atribuirles el tope seria una cita falsa. "
                    "Es tambien el aviso de que superar el tope NO significa "
                    "'material inexistente': significa 'fuera del catalogo "
                    "adoptado', y se levanta declarando otro tope",
        justificacion="ADOPCION DEL PROYECTISTA SOBRE UNA DISPONIBILIDAD, no "
                      "sobre un vacio normativo. El tope existe por una razon "
                      "de calculo real -- sin el, el solver de la Fase 4 "
                      "converge a un diametro que nadie fabrica ni transporta a "
                      "la obra -- pero el NUMERO es una decision de proyecto "
                      "sobre lo que se consigue en el mercado local, no una "
                      "exigencia. "
                      "QUE CAMBIA RESPECTO DE LA VERSION ANTERIOR: nada del "
                      "valor, todo de la etiqueta y de la cita. Los tres numeros "
                      "son los mismos que traia 'diametros_normalizados'; lo que "
                      "se retira es la atribucion a ASTM C76 / AASHTO M170, "
                      "AASHTO M36 / ASTM A760 y AASHTO M294, que no los "
                      "sostienen (NOR-PRO-01, NOR-PRO-02) y que el propio codigo "
                      "marcaba 'VERIFICAR' sin numeral (MAT-O8). "
                      "POR QUE NO SE SUBEN A 3600 mm: porque eso seria cambiar "
                      "una adopcion no declarada por otra. Lo que la fuente "
                      "sostiene es que la norma no topa donde el proyecto topa, "
                      "no cual es el tope que a esta obra le conviene. Elegir el "
                      "tope real es del expediente -- ver `reemplazado_por` --, "
                      "y mientras tanto los tres valores se conservan porque son "
                      "los que la Fase 4 ya venia usando y son los CONSERVADORES "
                      "en su unico efecto: descartan material antes, nunca "
                      "despues. Un tope mas alto solo puede ampliar el conjunto "
                      "de disenos admisibles. "
                      "CONSECUENCIA QUE HAY QUE DECLARAR EN LA MEMORIA: V9 "
                      "(`M5_verificaciones.v9_disponibilidad_diametro`) y "
                      "`M2_material.siguiente_diametro` descartan material "
                      "contra este tope, y ese descarte es ADOPTADO. Un punto "
                      "que salga 'no factible por diametro' con 2.10 m de TMC no "
                      "es un punto que la norma prohiba resolver con TMC",
        fuente="NINGUNA NORMA. Verificado en contra por lectura directa del "
               "PDF: ASTM A760/A760M-10, Tabla 1 'Tamaños de tuberia', pag. 3, "
               "tabula diametros nominales de 100 mm (4 in) a 3600 mm (144 in) "
               "-- 2100 mm es una fila mas de la serie, no un maximo. AASHTO M "
               "170M-04, Tablas 1 a 5 (Clases I a V), tabula de 300 a 3600 mm y "
               "su Seccion 7.2 preve ademas 'special designs for sizes and loads "
               "beyond those shown in Tables 1 to 5'. AASHTO M294 no esta en "
               "normas/ y su tope de 1.50 m no se pudo contrastar con ninguna "
               "fuente del repositorio",
        sensibilidad=("topes adoptados: concreto 2.70 / TMC 2.10 / HDPE "
                      "1.50 m (los que el proyecto aplica hoy)",
                      "topes de la serie tabulada: 3.60 m en concreto y en "
                      "TMC (M 170M-04 Tablas 1-5 y A760 Tabla 1); en HDPE no "
                      "hay extremo que declarar porque M294 no esta en "
                      "normas/. Entre los dos extremos, lo unico que cambia "
                      "es CUANTOS puntos salen 'no factible por diametro': el "
                      "tope no entra en ninguna formula de dimensionamiento"),
        reemplazado_por="Disponibilidad real de mercado para el corredor, "
                        "declarada en el expediente con su respaldo (consulta a "
                        "fabricantes, o el tope de la serie tabulada de cada "
                        "norma de producto si el proyecto decide no acotar). "
                        "Mientras no se declare, el descarte por diametro se "
                        "imprime como adoptado",
        verificacion_pendiente="Los tres topes siguen sin respaldo documental. "
                               "El de HDPE (1.50 m) es el mas restrictivo y es "
                               "el unico cuya norma de producto (AASHTO M294) ni "
                               "siquiera esta en normas/ para poder contrastarlo",
    ),

    # 'h_relleno_min_concreto_tmc' SE RETIRO. Declaraba 0.30 m [N->] para
    # concreto y TMC "por analogia sobre un vacio verificado": el HDPE es el
    # material menos tolerante a cobertura reducida, luego exigirle a los
    # otros dos su mismo recubrimiento no podia quedar del lado inseguro.
    #
    # Las dos mitades del argumento cayeron a la vez.
    #
    # (1) EL VACIO NO ERA UN VACIO (NOR-VAC-01). La busqueda se declaro
    #     cerrada tras agotar tres fuentes -- normas de producto, Manual de
    #     Puentes y EG-2013 -- y falto la cuarta, que ademas esta en el propio
    #     repositorio y es la que Sec. 0.2 adopta de extremo a extremo: AASHTO
    #     LRFD 9a ed. (2020), Art. 12.6.6.3 "Minimum Cover" y su
    #     Tabla 12.6.6.3-1, pag. 12-22, tabulan la cobertura minima por tipo
    #     de conducto. Vive ahora en 'cobertura_minima_aashto'.
    # (2) EL NUMERO ERA CORTO. Esa tabla pone un PISO de 12.0 in = 0.3048 m
    #     para concreto y metal, de modo que 0.30 m quedaba 5 mm por debajo;
    #     y lo que gobierna en diametros grandes no es el piso sino Bc/8, que
    #     para un tubo de 2.40 m de concreto (Bc ~ 2.9 m) da ~0.36 m, un 20 %
    #     mas que lo adoptado.
    #
    # Se retira en vez de corregirle el numero porque ya no queda vacio que
    # cubrir: el recubrimiento minimo pasa a CALCULARSE
    # (`M7_geometria.altura_recubrimiento`) como el mayor entre el minimo de
    # EG-2013 -- que solo existe para HDPE -- y la cobertura minima de AASHTO,
    # que depende del diametro EXTERIOR y de la condicion de pavimento. Un
    # escalar unico para dos materiales no puede expresar eso.
    #
    # Cae con el la referencia a WSDOT M 23-03.12 Tabla 8-6 (NOR-ANA-01): era
    # la unica cita que la memoria ofrecia para sostener "el concreto tolera
    # mas", y no esta en el repositorio. La Tabla 12.6.6.3-1 confirma la
    # DIRECCION de aquel argumento -- bajo pavimento el termoplastico pide
    # ID/2 >= 24 in, el valor mas alto de la tabla -- y desmiente su MAGNITUD:
    # la analogia era conservadora en el orden de los materiales y no en el
    # numero. Con la tabla cableada, ni la direccion ni la magnitud dependen
    # ya de una fuente ausente.

    "cobertura_minima_aashto": Criterio(
        valor={
            # Tabla 12.6.6.3-1, transcrita a SI. Por material del catalogo y
            # por condicion de pavimento. Cada fila:
            #   divisor   el D se divide por el (None: la fila es un valor
            #             fijo, sin termino proporcional al diametro)
            #   sobre     que diametro entra en el divisor, con la nomenclatura
            #             del propio Art. 12.6.6.3: "exterior" para Bc
            #             ("outside diameter or width of the structure"),
            #             "interior" para ID ("inside diameter"), "nominal"
            #             para S ("diameter of pipe")
            #   piso_m    el ">" de la tabla: minimo absoluto, en metros
            #   raiz_pies rama "or sqrt(Bc)/8, whichever is greater" -- solo
            #             la fila del concreto la tiene, y no es homogenea:
            #             la tabla escribe Bc en PIES y por eso se evalua en
            #             pies y se devuelve a metros (ver "pie_a_metro")
            "concreto_reforzado": {
                # "Reinforced Concrete Pipe / Under unpaved areas or top of
                # flexible pavement -- Bc/8 or sqrt(Bc)/8, whichever is
                # greater, > 12.0 in."
                "no_pavimentado": {"divisor": 8.0, "sobre": "exterior",
                                   "piso_m": 0.3048, "raiz_pies": True},
                "flexible": {"divisor": 8.0, "sobre": "exterior",
                             "piso_m": 0.3048, "raiz_pies": True},
                # "Under bottom of rigid pavement -- 9.0 in."
                "rigido": {"divisor": None, "sobre": "exterior",
                           "piso_m": 0.2286, "raiz_pies": False},
            },
            "tmc": {
                # "Corrugated Metal Pipe / -- / S/8 > 12.0 in." Fila unica:
                # la tabla no distingue condicion de pavimento para el metal
                # corrugado, y por eso las tres condiciones repiten la misma
                # fila en vez de inventarle dos que la tabla no trae.
                "no_pavimentado": {"divisor": 8.0, "sobre": "nominal",
                                   "piso_m": 0.3048, "raiz_pies": False},
                "flexible": {"divisor": 8.0, "sobre": "nominal",
                             "piso_m": 0.3048, "raiz_pies": False},
                "rigido": {"divisor": 8.0, "sobre": "nominal",
                           "piso_m": 0.3048, "raiz_pies": False},
            },
            "hdpe": {
                # "Thermoplastic Pipe / Under unpaved areas -- ID/8 > 12.0 in.
                #                     / Under paved roads  -- ID/2 > 24.0 in."
                # Las dos condiciones pavimentadas caen en la MISMA fila: la
                # tabla dice "paved roads" sin separar flexible de rigido.
                "no_pavimentado": {"divisor": 8.0, "sobre": "interior",
                                   "piso_m": 0.3048, "raiz_pies": False},
                "flexible": {"divisor": 2.0, "sobre": "interior",
                             "piso_m": 0.6096, "raiz_pies": False},
                "rigido": {"divisor": 2.0, "sobre": "interior",
                           "piso_m": 0.6096, "raiz_pies": False},
            },
            # Definicion exacta de la unidad (NIST): 1 ft = 0.3048 m. No es un
            # valor de proyecto ni una constante fisica: esta aqui, dentro de
            # la transcripcion, porque la rama sqrt(Bc)/8 NO es homogenea y
            # solo tiene sentido con Bc en pies. Sin ella la fila del concreto
            # no se puede pasar a SI sin inventar un coeficiente.
            "pie_a_metro": 0.3048,
        },
        etiqueta="C",
        concepto="Cobertura minima sobre la clave del conducto, por material y "
                 "condicion de pavimento (Tabla 12.6.6.3-1 de AASHTO LRFD)",
        justificacion="VACIO NORMATIVO PERUANO CUBIERTO CON LA FUENTE QUE EL "
                      "PROPIO PROYECTO YA ADOPTO. EG-2013 fija la altura "
                      "minima de relleno solo para HDPE (Subseccion 508.07, "
                      "pag. impresa 984) y el Manual de Puentes no incorporo "
                      "la Sec. 12 de AASHTO LRFD, de modo que para concreto y "
                      "TMC el corpus peruano no da numero. AASHTO LRFD si, y "
                      "Sec. 0.2 de la hoja de ruta adopta la Via 1 -- AASHTO "
                      "LRFD de extremo a extremo -- lo que hace de esta tabla "
                      "la fuente natural y no una analogia. Es [C] y no [N] "
                      "porque AASHTO no es norma peruana vigente: es la fuente "
                      "tecnica reconocida con que se cubre el vacio. "
                      "REGLA DE CONFLICTO, la misma que Sec. 0.2 ya aplica al "
                      "recubrimiento de concreto (AASHTO frente a E.060): rige "
                      "el MAYOR de los dos minimos. Para HDPE conviven el "
                      "0.30 m de EG-2013 [N] y esta tabla, y se aplica el "
                      "mayor; para concreto y TMC solo existe esta. "
                      "SIMPLIFICACION CONSERVADORA DECLARADA -- el datum. La "
                      "nota al pie de la Tabla 12.6.6.3-1 dice que la "
                      "cobertura se mide 'from top of rigid pavement or bottom "
                      "of flexible pavement', mientras que 7.A mide h_rec de "
                      "la clave a la SUBRASANTE. La cobertura de AASHTO es "
                      "entonces h_rec MAS el paquete que quede por encima de "
                      "la subrasante (base, subbase y, con pavimento rigido, "
                      "la losa), o sea siempre >= h_rec. Exigir el minimo de "
                      "AASHTO a h_rec solo -- que es lo que hace 7.A -- pide "
                      "de mas, nunca de menos. Se declara porque es una "
                      "eleccion de encuadre, aunque su direccion sea segura: "
                      "cerrarla de verdad exige el desglose del paquete "
                      "estructural, que Sec. 1.2 no trae como columna. "
                      "TENSION INTERNA DE LA PROPIA TABLA, anotada para que "
                      "nadie la lea como un descuido: la fila del concreto "
                      "describe su condicion como 'under unpaved areas or TOP "
                      "of flexible pavement' mientras la nota al pie dice que "
                      "la cobertura se mide desde el 'BOTTOM of flexible "
                      "pavement'. Cualquiera de las dos lecturas situa el "
                      "datum a nivel de subrasante o POR ENCIMA, de modo que "
                      "exigir el minimo sobre h_rec -- que llega solo hasta la "
                      "subrasante -- es conservador con las dos. Por eso la "
                      "tension no se resuelve aqui: no cambia el resultado, y "
                      "resolverla sin el desglose del paquete seria elegir "
                      "una lectura sin dato que la sostenga. "
                      "POR QUE 'S' ES EL DIAMETRO INTERIOR EN LA FILA DEL "
                      "METAL: el Art. 12.6.6.3 define S como 'diameter of "
                      "pipe' y define Bc e ID aparte, de modo que S es el "
                      "diametro NOMINAL. En la serie del producto ese nominal "
                      "es el interior: la Tabla 1 de ASTM A760/A760M-10 titula "
                      "su primera columna 'Nominal Inside Diameter'. En TMC la "
                      "distincion es ademas de milimetros -- la pared es una "
                      "plancha mas la corrugacion -- mientras que la cota de "
                      "clave si la necesita entera. "
                      "QUE FILA APLICA la decide 'condicion_pavimento', que es "
                      "un vacio aparte y bloquea: la tabla es [C] y elegir su "
                      "fila es [A], el mismo reparto que F_PGA_TABLA / 'F_pga' "
                      "y FACTOR_MURO_TABLA / 'factor_muro_eleccion'",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed. (2020), "
               "Seccion 12 'Buried Structures and Tunnel Liners', "
               "Art. 12.6.6.3 'Minimum Cover' y Tabla 12.6.6.3-1, pag. "
               "impresa 12-22 (PDF 1660 de "
               "normas/AASHTO.LRFD.Bridge.Design.Specifications_9th.Edition."
               "2020.pdf). Nomenclatura del propio articulo: 'S = diameter of "
               "pipe (in.)', 'Bc = outside diameter or width of the structure "
               "(ft)', 'ID = inside diameter (in.)'. Filas transcritas, "
               "literales: Corrugated Metal Pipe 'S/8 > 12.0 in.'; "
               "Thermoplastic Pipe 'Under unpaved areas ID/8 > 12.0 in.' y "
               "'Under paved roads ID/2 > 24.0 in.'; Reinforced Concrete Pipe "
               "'Under unpaved areas or top of flexible pavement: Bc/8 or "
               "sqrt(Bc)/8, whichever is greater, > 12.0 in.' y 'Under bottom "
               "of rigid pavement: 9.0 in.'. Nota al pie: 'Minimum cover taken "
               "from top of rigid pavement or bottom of flexible pavement'. "
               "Conversiones a SI: 12.0 in = 0.3048 m, 9.0 in = 0.2286 m, "
               "24.0 in = 0.6096 m (1 in = 0.0254 m exacto). "
               "BUSQUEDA EN EL CORPUS PERUANO, agotada fuente por fuente y "
               "registrada en docs/manifiesto_citas.md Sec. 14.a: EG-2013 "
               "Cap. V fija la altura minima de relleno SOLO para HDPE "
               "(Subseccion 508.07, pag. impresa 984, verificada leyendo el "
               "PDF); las Secciones 505, 506 y 507 regulan colocacion y "
               "compactacion y remiten a la Seccion 502, que tampoco fija "
               "altura minima de diseño. El Manual de Puentes (RD "
               "041-2016-MTC/14) no incorporo un capitulo equivalente a la "
               "Seccion 12 de AASHTO LRFD y no fija altura minima de relleno "
               "para ningun material: trata estructuras enterradas en al "
               "menos cinco numerales (2.4.3.3.2 pag. 109; Tabla 2.4.5.3.1-2 "
               "pag. 143; 2.8.1.3A.6.2 pag. 280; 2.9.1.4.6.4.6 pag. 362; "
               "2.4.3.11.1 pag. 121) y los cinco SUPONEN conocida la "
               "cobertura. Las normas de producto tampoco: AASHTO M 170M-04 "
               "lo excluye en su Nota 1 ('manufacturing and purchase "
               "specification only'), AASHTO M 36 en su §1.3 y ASTM "
               "A760/A760M-10 en su §1.4 -- la atribucion anterior ponia la "
               "misma 'Nota 1' en las tres y era falsa en dos (NOR-PRO-03). "
               "TRAMPA DE VOCABULARIO, anotada para que nadie la vuelva a "
               "pisar: el Manual de Puentes SI usa la palabra 'recubrimiento' "
               "para alcantarillas en la Tabla 2.9.1.5.5.3-1 (pag. 378, 2.0 "
               "in / 50 mm), pero ahi significa el recubrimiento de CONCRETO "
               "SOBRE EL ACERO DE REFUERZO, no la altura de relleno de "
               "tierra. Son dos conceptos que comparten palabra en espaniol y "
               "no tienen ninguna relacion; el numero de esa tabla NO sirve "
               "aqui. "
               "LA EVIDENCIA DE INDICE QUE SE RETIRO, por falsa (NOR-PUE-06): "
               "se sostenia que 'el indice del Manual salta de 2.11 (Muros de "
               "Contencion y Estribos) a 2.12'. El 2.11 del Manual es 'DISEÑO "
               "DE BARRERAS DE SONIDO' (15 AASHTO), pag. 505, y el 2.12 "
               "'Disposiciones Constructivas', pag. 513; los muros y estribos "
               "viven dentro de 2.8 Cimentaciones, de donde este mismo "
               "expediente saca 2.8.1.1.14.2. Ademas la numeracion del Manual "
               "no sigue la de AASHTO (2.8 <-> 10, 2.10 <-> 14.6, 2.11 <-> "
               "15), de modo que 'entre 2.11 y 2.12 deberia estar la Sec. 12' "
               "no era una inferencia valida. La conclusion -- que el Manual "
               "no incorporo la Sec. 12 -- no cambia; el argumento con que se "
               "sostenia, si",
        reemplazado_por="Una disposicion PERUANA que fije la cobertura minima "
                        "para concreto y TMC: hoy no existe, y por eso se "
                        "aplica AASHTO LRFD. La cerraria que el MTC "
                        "incorporase la Sec. 12 de AASHTO LRFD al Manual de "
                        "Puentes, o una version del EG-2013 que extendiese el "
                        "508.07 a los otros dos materiales. Queda ademas "
                        "abierto el DATUM: la tabla mide la cobertura desde "
                        "el fondo del pavimento flexible o el techo del "
                        "rigido, y 7.A la exige sobre la subrasante -- la "
                        "simplificacion es conservadora y se cierra con el "
                        "desglose del paquete estructural, que Sec. 1.2 no "
                        "trae como columna",
        vacio_verificado="manifiesto_citas.md Sec. 14.a",
        verificacion_pendiente="Las filas que el catalogo de este proyecto NO "
                               "usa quedaron fuera de la transcripcion "
                               "(Spiral Rib, Structural Plate, Fiberglass, "
                               "Steel-Reinforced Thermoplastic, Long-Span, "
                               "Box y Deep Corrugated). Si algun dia el "
                               "catalogo de Sec. 3.2 admite otra forma, hay "
                               "que traerlas: hoy no estan porque no aplican, "
                               "no porque no existan. Falta ademas cerrar el "
                               "datum -- ver la SIMPLIFICACION CONSERVADORA de "
                               "la justificacion --, que necesita el desglose "
                               "del paquete estructural",
    ),

    "condicion_pavimento": Criterio(
        valor=None,                 # VACIO: bloquea 7.A -- que fila de la tabla
        etiqueta="A",
        concepto="Condicion de la superficie de rodadura sobre el cruce, para "
                 "elegir la fila de la Tabla 12.6.6.3-1: 'no_pavimentado', "
                 "'flexible' o 'rigido'",
        justificacion="LA TABLA ES [C] Y ELEGIR SU FILA ES [A]: mismo reparto "
                      "que F_PGA_TABLA / 'F_pga' y FACTOR_MURO_TABLA / "
                      "'factor_muro_eleccion'. La Tabla 12.6.6.3-1 separa 'under "
                      "unpaved areas', 'top of flexible pavement' y 'under "
                      "bottom of rigid pavement', y cual de las tres es esta via "
                      "no lo dice ninguna norma: lo dice la seccion tipica del "
                      "expediente vial. "
                      "POR QUE NO SE DEDUCE DE LO QUE YA HAY: el CSV (Sec. 1.2) "
                      "trae cota de rasante y cota de subrasante, y su "
                      "diferencia -- el paquete estructural e_paq -- es positiva "
                      "tambien en un afirmado. Un paquete no dice si hay carpeta "
                      "asfaltica ni si es losa de concreto. "
                      "POR QUE NO SE ADOPTA EL EXTREMO CONSERVADOR EN SILENCIO: "
                      "porque cambia el resultado, y mucho. En HDPE la fila "
                      "pavimentada pide ID/2 >= 24 in -- 0.75 m para un tubo de "
                      "1.50 m -- frente a 0.30 m de la fila no pavimentada: "
                      "2.5 veces. Elegir la mas exigente 'por si acaso' subiria "
                      "la rasante de todos los puntos sin que nadie pueda "
                      "rastrear de donde salio, que es exactamente lo que "
                      "CLAUDE.md prohibe. En concreto el efecto es el contrario "
                      "y por eso tampoco hay un extremo 'seguro' unico: la fila "
                      "de pavimento RIGIDO pide 9.0 in fijos, MENOS que las "
                      "otras dos",
        fuente="PENDIENTE - seccion tipica del expediente vial (Manual de "
               "Diseño Geometrico DG-2018 y el estudio de pavimentos), que fija "
               "el tipo de superficie de rodadura del corredor. Misma "
               "procedencia que 'talud_terraplen'",
        reemplazado_por="Tipo de pavimento de la seccion tipica del proyecto "
                        "vial, o una columna por punto si el corredor cambia de "
                        "superficie a lo largo de sus 5 km",
        sensibilidad=("no_pavimentado", "flexible", "rigido"),
        verificacion_pendiente="Declarar si la condicion es unica para el "
                               "corredor o varia por punto. Se declara como "
                               "criterio de corredor porque la seccion tipica "
                               "lo es; si el expediente trae tramos con "
                               "superficie distinta, pasa a ser columna del CSV",
    ),

    "espesor_pared_conducto": Criterio(
        valor=None,                 # VACIO: bloquea la clave fisica y el empuje de V7
        etiqueta="A",
        concepto="Espesor de pared del conducto por material, en metros: la "
                 "distancia entre la superficie interior y la exterior que "
                 "separa el diametro hidraulico D del diametro exterior "
                 "D_ext = D + 2*t",
        justificacion="EL CATALOGO DE Sec. 3.2 MODELA EL TUBO CON UN SOLO "
                      "DIAMETRO, el interior, y hay dos sitios donde el que "
                      "hace falta es el exterior: "
                      "(1) LA CLAVE FISICA (MAT-D4). EG-2013 Subseccion 508.07 "
                      "mide el relleno minimo 'desde la clave de la tuberia', "
                      "que es la superficie EXTERIOR; 7.A la calculaba como "
                      "cota de entrada + D, sin espesor. Con la clave corta en "
                      "t, la rasante minima sale corta en t: una rasante fijada "
                      "en ese minimo deja ~0.20 m reales de recubrimiento donde "
                      "EG-2013 exige 0.30 (deficit del 33 % para D = 0.90 m de "
                      "concreto). "
                      "(2) EL EMPUJE DE FLOTACION (MAT-D3). El num. 2.4.3.8.2 "
                      "del Manual de Puentes define la subpresion sobre el "
                      "VOLUMEN DESPLAZADO, que es el exterior. V7 usaba "
                      "U = gamma_w*(pi/4)*D^2 con D interior y su docstring lo "
                      "declaraba conservador: es al reves. Subestimar el volumen "
                      "desplazado subestima la carga DESestabilizante, y el "
                      "conservadurismo declarado apunta al lado contrario del "
                      "real (-31.6 % en U para D = 0.90 m de concreto). "
                      "POR QUE NO TIENE VALOR Y BLOQUEA: porque el espesor no "
                      "es un dato unico por material, es una CONSECUENCIA de la "
                      "clase o calibre que se especifique, y esa seleccion es "
                      "el vacio que 'clases_producto_por_relleno' ya declara "
                      "abierto para la Fase 8, items 1-2. En concreto, AASHTO M "
                      "170M-04 tabula TRES espesores por diametro (Wall A, B y "
                      "C, Tablas 1 a 5) y elegir cual se usa es del proyectista; "
                      "en TMC el espesor util es la altura de corrugacion mas el "
                      "calibre de la plancha, y la corrugacion admisible por "
                      "diametro esta en la Tabla 1 de A760 mientras el calibre "
                      "sigue abierto en 'clases_producto_por_relleno'; en HDPE "
                      "es la altura del perfil corrugado, y AASHTO M294 no esta "
                      "en normas/. Con una fuente que exige elegir, otra que "
                      "depende de un vacio ya declarado y una tercera ausente, "
                      "no hay transcripcion que hacer: hay una adopcion que "
                      "declarar, y por eso [A] y no [C]. "
                      "POR QUE NO SE APROXIMA A CERO 'del lado seguro': porque "
                      "no hay un lado seguro unico. En 7.A un t mayor sube la "
                      "clave y exige mas rasante (t = 0 es INSEGURO); en V7 un t "
                      "mayor sube el empuje U (t = 0 tambien es inseguro). Las "
                      "dos apuntan en la misma direccion aqui, y aun asi "
                      "adoptar un numero sin declararlo seria rellenar el vacio "
                      "en silencio",
        fuente="PENDIENTE - por material: AASHTO M 170M-04, Tablas 1 a 5, "
               "columna 'Wall Thickness' de las paredes A, B y C por diametro "
               "designado (concreto reforzado, con la eleccion de pared por "
               "declarar); ASTM A760/A760M-10 Tabla 1 (tamaños de corrugacion "
               "admisibles por diametro nominal) junto con el calibre de la "
               "plancha que fije la Fase 8 (TMC); AASHTO M294 (HDPE), que NO "
               "esta en normas/",
        reemplazado_por="El espesor de pared de la clase, calibre o perfil "
                        "efectivamente especificado en el expediente. Se cierra "
                        "junto con 'clases_producto_por_relleno': son el mismo "
                        "vacio de norma de producto visto desde dos fases -- "
                        "alli la clase por altura de relleno, aqui el espesor "
                        "que esa clase implica",
        verificacion_pendiente="El espesor real NO es constante por material: "
                               "crece con el diametro. Este criterio lo declara "
                               "como un escalar por material, que es lo que el "
                               "nivel de perfil (Sec. 1.4) admite; el "
                               "expediente lo sustituye por la tabla espesor x "
                               "diametro x clase. Mientras sea escalar hay que "
                               "declararlo para el diametro MAYOR que el "
                               "material vaya a usar, que es donde el espesor "
                               "es mayor y la clave queda mas alta",
    ),

    # ----------------------- FASE 8: ESTRUCTURAL DEL CONDUCTO -------------
    # Seleccion de clase/calibre por norma de producto (items 1-2) y V7 -
    # flotacion (item 3). El resto de Fase 8 (item 5: rigidez de anillo,
    # pandeo, costura) NO se calcula por decision expresa de la hoja de
    # ruta -- se difiere al expediente tecnico, ver
    # M8_estructural.verificacion_diferida_estructural().

    # 'NF_profundidad_m' ya no vive aqui: es un dato de sitio [S] que se mide
    # en cada cruce, no una exigencia normativa, y por eso es COLUMNA DEL CSV
    # (ver modelos.PuntoCritico y M0_carga.COLUMNAS). El 1.4 m que este
    # criterio declaraba era la caracterizacion general de la llanura del Bajo
    # Piura, y su propia `verificacion_pendiente` ya avisaba de que podia no
    # ser uniforme dentro del tramo; repetirlo en las cuatro filas del CSV
    # habria fingido cuatro mediciones donde hubo una descripcion de zona.

    "clases_producto_por_relleno": Criterio(
        valor=None,                 # VACIO: bloquea la seleccion de Fase 8, items 1-2
        etiqueta="C",
        concepto="Tabla de clase (concreto, AASHTO M 170M-04, Clases I a V) o "
                 "calibre (TMC, ASTM A796/A796M) admisible segun la altura de "
                 "relleno sobre la clave, para Fase 8 items 1-2: seleccionar "
                 "la clase/calibre por altura real y verificar que esa "
                 "altura cae en el rango admisible de la clase elegida",
        justificacion="Ninguna de las dos tablas (AASHTO M 170M-04 clases I-V "
                      "por diametro y altura de relleno; ASTM A796/A796M "
                      "calibre por altura de cobertura) esta transcrita en la "
                      "hoja de ruta. HDPE (AASHTO M294) no tiene tabla de "
                      "clase por altura: su seleccion depende de un calculo de "
                      "rigidez de anillo que Fase 8, item 5, difiere "
                      "expresamente al expediente tecnico. "
                      "LA NORMA DEL TMC NO ES A-807 (NOR-PRO-04). Este "
                      "criterio atribuia el calibre por altura y la relacion "
                      "luz/corrugacion a 'ASTM A-807', y esa designacion no "
                      "aparece NI UNA VEZ en M 170M, M 36 ni A760. Lo que si "
                      "aparece: A760 §1.4 remite el procedimiento de "
                      "instalacion a ASTM A798/A798M, y tanto A760 como la "
                      "lista de normas de M 36 citan ASTM A796/A796M "
                      "('Practice for Structural Design of Corrugated Steel "
                      "Pipe'), que es la que lleva el calibre por altura de "
                      "cobertura. De donde venia el error: EG-2013 "
                      "Subsecciones 507.05, 507.06 y 507.08 (pags. 969-970) SI "
                      "remiten a A-807 -- esa cita del expediente es correcta "
                      "y no se toca -- pero remiten para MATERIALES Y "
                      "FABRICACION, no para la tabla de calibre por altura. "
                      "PARTE DEL PENDIENTE YA SE PUEDE CERRAR: la relacion "
                      "luz/corrugacion no hay que buscarla fuera, esta en la "
                      "Tabla 1 de A760 (una 'X' por cada tamaño de corrugacion "
                      "estandar para cada diametro nominal) y en la Tabla 6 de "
                      "M 36, las dos adjuntas en normas/. Lo que sigue fuera "
                      "del repositorio es A796",
        fuente="PENDIENTE - AASHTO M 170M-04, Tablas 1 a 5 (clases I a V por "
              "diametro, concreto); ASTM A796/A796M (calibre por altura de "
              "cobertura, TMC), que NO esta en normas/. Falta EXTRAER la "
              "tabla completa (clase o calibre x diametro x rango de altura "
              "de relleno). La relacion luz/corrugacion, en cambio, si esta "
              "disponible: ASTM A760/A760M-10 Tabla 1 y AASHTO M 36 Tabla 6",
        reemplazado_por="Tabla de clase/calibre por altura de relleno de la "
                        "norma de producto, extraida y transcrita con su "
                        "numeral. Cierra ademas 'espesor_pared_conducto': el "
                        "espesor de pared es una consecuencia de la clase, el "
                        "calibre o el perfil que aqui se seleccione",
        verificacion_pendiente="POR QUE ES [C] Y NO [A], que es la unica "
                               "combinacion de este archivo (un [C] sin "
                               "valor): la etiqueta la fija DE DONDE saldra "
                               "el valor, no si ya lo tiene. Aqui la fuente "
                               "tecnica existe, esta identificada y es "
                               "reconocida (AASHTO M 170M-04, ASTM A796/A796M): "
                               "lo que falta es TRANSCRIBIRLA, no elegir. Un "
                               "[A] seria lo contrario: no hay fuente y decide "
                               "el proyectista -- que es justo el caso de "
                               "'espesor_pared_conducto', su gemelo por la "
                               "otra punta: alli M 170M ofrece TRES paredes "
                               "por diametro y hay que elegir una. El "
                               "precedente interno es 'v_max_tmc' / "
                               "'v_max_hdpe', que fueron [C] sin valor por la "
                               "misma razon y hoy valen 4.6 sin haber cambiado "
                               "de etiqueta",
    ),

    # 'FS_flotacion' SE RETIRO. Declaraba el factor de seguridad global de
    # ΣW >= FS*U, que es lenguaje de TENSION ADMISIBLE, y V7 se reescribio
    # como el equilibrio de factores de carga que corresponde al marco LRFD
    # que adopta Sec. 0.2:
    #
    #     gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U
    #
    # No se le redefinio el contenido porque en LRFD no queda nada que
    # represente: el margen entre estabilizante y desestabilizante lo hacen
    # ahora los propios gamma, y conservar ademas un FS seria contar dos veces
    # el mismo margen. Los gamma NO son un criterio nuevo: salen de
    # 'factores_carga_aashto', mas abajo, el mismo del que come M9 (Sec. 9.2).
    # Que Fase 8 y Fase 9 lean la misma declaracion es lo que impide que el
    # expediente termine con dos juegos de factores de carga distintos.

    "peso_especifico_relleno_kn_m3": Criterio(
        valor=None,                 # VACIO: bloquea el termino Sigma W de V7
        etiqueta="A",
        concepto="Peso especifico del material de relleno sobre la clave, "
                 "para el termino ΣW de V7 (peso del prisma de relleno que "
                 "se opone a la flotacion)",
        justificacion="Ni la hoja de ruta ni el CSV (Sec. 1.2) traen el "
                      "peso especifico del material de relleno: depende de "
                      "la cantera que finalmente se especifique. V7 lo "
                      "necesita para pesar el prisma de relleno sobre la "
                      "clave (ancho D, altura la del punto -- ver "
                      "M8_estructural.peso_relleno_kn_m). El peso propio del "
                      "conducto NO se suma: omitirlo es conservador (reduce "
                      "ΣW) y evita depender del espesor de pared que "
                      "'clases_producto_por_relleno' todavia no resuelve",
        fuente="PENDIENTE - ensayo de peso especifico del material de "
              "cantera propuesto, o valor de practica corriente declarado "
              "con su fuente en la memoria",
        reemplazado_por="Peso especifico medido del material de relleno "
                        "efectivamente especificado en el proyecto",
        sensibilidad=(17.0, 20.0),   # kN/m3, rango corriente de rellenos compactados
    ),

    # ----------------------- FASE 7: COMPATIBILIDAD GEOMETRICA ------------
    # 7.A ya NO queda resuelto con lo declarado: pide tres cosas que estan
    # mas arriba en este archivo -- 'cobertura_minima_aashto' (la tabla),
    # 'condicion_pavimento' (que fila) y 'espesor_pared_conducto' (donde esta
    # la clave fisica) --, y las dos ultimas bloquean. 'resguardo_HW_subrasante'
    # sigue cubriendo la otra condicion del maximo, la de la carga a la
    # entrada. Lo que 7.B abre aparte es la LONGITUD del conducto.

    "talud_terraplen": Criterio(
        valor=None,                 # VACIO: bloquea la longitud del conducto en 7.B
        etiqueta="A",
        concepto="Inclinacion del talud del terraplen en el punto de cruce, "
                 "como proyeccion horizontal por unidad de altura (H:V), para "
                 "la 'proyeccion de taludes' que Sec. 7.B suma al ancho de "
                 "plataforma al calcular la longitud del conducto",
        justificacion="Sec. 7.B define la longitud como 'ancho de plataforma + "
                      "proyeccion de taludes, afectada por esviaje', pero no "
                      "entrega la inclinacion del talud ni una regla para "
                      "deducirla, y Sec. 1.2 no la trae como columna: el unico "
                      "dato de seccion transversal que llega por punto es el "
                      "ancho de plataforma. El vacio no se puede tapar con lo "
                      "que ya esta en el CSV -- la altura de terraplen del "
                      "punto (cota_rasante - cota_terreno) da el BRAZO "
                      "VERTICAL del talud, no su inclinacion -- y sin longitud "
                      "no hay caida S*L ni cota de salida que amarrar al fondo "
                      "del receptor, que es la otra mitad de 7.B. Adoptar en "
                      "silencio un 1.5:1 de practica corriente moveria la "
                      "longitud, la caida y la cota de salida de todos los "
                      "puntos sin que nadie pueda rastrear de donde salio",
        fuente="PENDIENTE - Manual de Diseño Geometrico DG-2018 y la seccion "
               "tipica del proyecto, que fijan el talud del terraplen segun su "
               "altura y el material del cuerpo",
        reemplazado_por="Talud de la seccion tipica del expediente vial, o la "
                        "longitud medida directamente sobre la seccion "
                        "transversal de cada punto",
        verificacion_pendiente="Declarar si el talud es unico para el tramo o "
                               "varia por punto con la altura de terraplen. M7 "
                               "lo aplica hoy a los DOS taludes con la misma "
                               "altura (terraplen simetrico sobre el terreno "
                               "natural del cruce), que es lo unico que el CSV "
                               "permite calcular: si la seccion es asimetrica, "
                               "la longitud se mide y no se deduce",
    ),

    # ----------------------- PROTECCION Y DETALLE -------------------------

    "espesor_proteccion_salida": Criterio(
        valor=1.75,                 # multiplicador de d50
        etiqueta="A",
        concepto="Espesor de la capa de proteccion, como multiplo de d50",
        justificacion="El Manual solo entrega d50 (Laushey). El espesor, la "
                      "longitud y la granulometria completa no estan normados. "
                      "Se adopta el rango corriente 1.5-2.0 d50",
        fuente="Practica corriente de diseno de enrocado",
        sensibilidad=(1.5, 2.0),
    ),

    "longitud_proteccion_salida": Criterio(
        valor=None,                 # VACIO: completa el diseno de la Fase 6
        etiqueta="A",
        concepto="Longitud de la proteccion aguas abajo de la salida",
        justificacion="Laushey (num. 4.1.1.3.7 c) entrega d50 y nada mas. La "
                      "hoja de ruta declara expresamente que el espesor, la "
                      "LONGITUD aguas abajo, la granulometria completa y el "
                      "filtro quedan fuera de la norma. Sin filtro el enrocado "
                      "se socava por debajo y falla: la longitud sola no basta, "
                      "pero sin ella no hay pieza que dimensionar",
        fuente="PENDIENTE - Sec. 6 de la hoja de ruta la marca [A] sin valor. "
               "Practica corriente de diseno de enrocado o HEC-14",
        reemplazado_por="Diseno de disipador o transicion del expediente",
        verificacion_pendiente="Con pendientes bajas los d50 son de 3-13 cm y lo "
                               "probable es que gobierne el emboquillado de piedra "
                               "por razones constructivas, no el enrocado",
    ),

    "angulo_aletas": Criterio(
        valor=None,                 # completar segun esviaje
        etiqueta="A",
        concepto="Angulo de las aletas del cabezal",
        justificacion="Ajustado al esviaje del cauce en cada punto",
        fuente="PENDIENTE - Practica corriente de diseno de cabezales; ni el "
               "Manual de Hidrologia ni el Manual de Puentes fijan el angulo "
               "de las aletas. No hay numeral que extraer: hay una geometria "
               "que el proyectista define punto por punto",
        reemplazado_por="Geometria de aletas del expediente: angulo por punto, "
                        "definido con el esviaje medido del cauce "
                        "('esviaje_grados' de Sec. 1.2) y el plano tipo de "
                        "cabezal adoptado",
        sin_consumidor="Ningun modulo lo invoca porque el script no dibuja la "
                       "geometria de las aletas: dimensiona el cabezal "
                       "(Fase 9) y remite el despiece al plano del "
                       "expediente. Se declara para que el vacio se pida, no "
                       "para que se calcule aqui",
    ),

    # ----------------------- FASE 9: CABEZAL Y ALETAS ---------------------
    # Sec. 9.2 nombra las combinaciones y la cadena sismica; Sec. 9.3 da los
    # FS; Sec. 9.4 remite el diseno a AASHTO LRFD Sec. 5. Lo que NO transcribe
    # son las tablas numericas de esas tres remisiones. Cada vacio se declara
    # aqui en vez de rellenarse con el valor "de siempre".

    "factores_carga_aashto": Criterio(
        valor={
            "Resistencia I": {
                "DC": {"max": 1.25, "min": 0.90},
                "EV": {"max": 1.35, "min": 0.90},
                "EH": {"max": 1.50, "min": 0.90},        # empuje ACTIVO -- caso de diseno del proyecto
                "EH_en_reposo": {"max": 1.35},           # informativo: el proyecto disena con empuje activo, no en reposo
                "LS": 1.75,
                "WA": {"max": 1.00, "min": 1.00},
            },
            "Servicio I": {
                "DC": {"max": 1.00, "min": 1.00},
                "EV": {"max": 1.00, "min": 1.00},
                "EH": {"max": 1.00, "min": 1.00},
                "LS": 1.00,
                "WA": {"max": 1.00, "min": 1.00},
            },
            "Evento Extremo I": {
                "DC": {"max": 1.00, "min": 1.00},
                "EV": {"max": 1.00, "min": 1.00},
                "EH": {"max": 1.00, "min": 1.00},
                "LS": "gamma_EQ",   # 0.50 o 0.00 -- a criterio del propietario, ver verificacion_pendiente
                "WA": {"max": 1.00, "min": 1.00},
                "EQ": {"max": 1.00, "min": 1.00},
            },
        },
        etiqueta="C",
        concepto="Factores gamma de las tres combinaciones de Sec. 9.2 "
                 "(Resistencia I, Servicio I, Evento Extremo I) por tipo de "
                 "carga: DC, EV, EH, LS, WA, EQ, con sus maximos y minimos",
        justificacion="Sec. 9.2 NOMBRA las tres combinaciones con numeral "
                      "(2.4.5.3, AASHTO LRFD Sec. 3.4.1) pero no transcribia "
                      "la Tabla 3.4.1-1 ni la 3.4.1-2. Sin los factores, una "
                      "combinacion es una lista de cargas, no una demanda. "
                      "CERRADO por verificacion externa contra la fuente: "
                      "los factores de EH y EV son DOBLES (gamma maximo y "
                      "minimo) y cual de los dos gobierna depende de si la "
                      "carga estabiliza o desestabiliza cada verificacion -- "
                      "escribir 1.35 para el empuje de tierras en todas las "
                      "filas habria sido el error clasico y da del lado "
                      "inseguro en volteo; la tabla fuente da EV minimo "
                      "0.90, no 1.00. La Tabla 3.4.1-2 ademas distingue EH "
                      "activo (1.50/0.90) de EH en reposo (1.35, sin minimo "
                      "declarado por la fuente): el proyecto disena con "
                      "empuje ACTIVO (Mononobe-Okabe/Coulomb, ver "
                      "'inclinacion_muro_beta' y companeros), asi que 'EH' "
                      "es el activo y 'EH_en_reposo' queda solo como dato "
                      "informativo de la tabla. Evento Extremo I lleva "
                      "gamma_EQ en la carga LS, que la propia AASHTO deja a "
                      "criterio del propietario (0.50 o 0.00): no se fija "
                      "aqui un numero, se declara la eleccion pendiente",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., Tablas "
               "3.4.1-1 (pag. 3-14) y 3.4.1-2 (pag. 3-18); transcritas "
               "tambien en Manual de Puentes MTC, pags. 143 y 146",
        verificacion_pendiente="gamma_EQ (carga LS de Evento Extremo I) "
                               "queda a criterio del propietario del "
                               "proyecto (0.50 o 0.00, AASHTO LRFD "
                               "C3.4.1): declarar en la memoria cual se "
                               "adopta y por que, antes de evaluar esa "
                               "combinacion",
    ),

    "peso_especifico_concreto_kn_m3": Criterio(
        valor=23.56,                # kN/m3, concreto armado (0.150 kcf)
        etiqueta="C",
        concepto="Peso especifico del concreto armado del cabezal, kN/m3",
        justificacion="Es el peso propio (carga DC) que resiste el volteo y "
                      "el deslizamiento de Sec. 9.3: sin el no hay momento "
                      "estabilizante ni fuerza normal en la base. CERRADO "
                      "por verificacion externa: AASHTO LRFD Tabla 3.5.1-1 "
                      "+ Comentario C3.5.1 dan 0.150 kcf (concreto normal "
                      "armado) = 23.56 kN/m3. El valor cae dentro del rango "
                      "de practica corriente (23.5-24.5 kN/m3) que este "
                      "criterio manejaba antes de tener cita directa, pero "
                      "no se adopta el redondeo regional de 24.0: ese numero "
                      "no tiene fuente propia y 23.56 si la tiene",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., Tabla "
               "3.5.1-1 + Comentario C3.5.1, pag. 3-21 (0.150 kcf, concreto "
               "normal armado)",
    ),

    "predimensionamiento_cabezal": Criterio(
        valor=None,                 # VACIO: bloquea la estabilidad automatica
        etiqueta="A",
        concepto="Geometria del cabezal (altura H sobre zapata, ancho de "
                 "zapata B, profundidad de desplante D_f, espesor de la "
                 "pantalla en corona y en su arranque, espesor de zapata e "
                 "inclinacion beta del trasdos), en m",
        justificacion="Sec. 9.1 fija QUE es el cabezal (Sec. 503, concreto "
                      "estructural) y COMO es su embocadura (tubo a ras, "
                      "square edge, amarrada a las constantes HDS-5 de "
                      "Sec. 4.2), pero no lo dimensiona, y Sec. 1.2 no trae "
                      "ninguna columna con su geometria. Sin H no hay empuje, "
                      "sin B no hay momento estabilizante ni presion de "
                      "contacto, sin D_f no hay confinamiento. Las funciones "
                      "de M9 aceptan la geometria como argumento explicito "
                      "para poder tantear; lo que este vacio bloquea es que "
                      "el cabezal se dimensione SOLO, sin que nadie declare "
                      "de donde salieron las dimensiones",
        fuente="PENDIENTE - predimensionamiento del proyectista, o plano tipo "
               "de cabezal del expediente vial",
        reemplazado_por="Plano de encofrado del cabezal, acotado",
        verificacion_pendiente="La geometria tiene que ser COMPATIBLE con el "
                               "diametro adoptado en la Fase 4 y con la "
                               "altura de terraplen de la Fase 7: un cabezal "
                               "declarado aparte del conducto que remata es "
                               "una incoherencia de expediente",
    ),

    "N_cq_N_gammaq_meyerhof": Criterio(
        valor=None,                 # VACIO: bloquea la capacidad portante en talud
        etiqueta="A",
        concepto="Factores de capacidad de carga N_cq y N_gamma_q para zapata "
                 "proxima a talud (Meyerhof 1957), leidos de las figuras "
                 "2.8.1.3.1.2c-1 y -2 del Manual de Puentes",
        justificacion="Sec. 9.3 es taxativa en que el cabezal se apoya en el "
                      "BORDE DEL TERRAPLEN y no en terreno horizontal, y en "
                      "que la penalizacion es severa por perdida de "
                      "confinamiento: N_q = 0.0 (eso si es un numero y esta "
                      "en constantes_normativas), y N_c y N_gamma se "
                      "REEMPLAZAN por N_cq y N_gamma_q. Pero esos dos salen "
                      "de FIGURAS, no de una formula ni de una tabla: "
                      "dependen de la distancia de la zapata al borde, de la "
                      "altura del talud y de su inclinacion, y no hay forma "
                      "de transcribirlos sin leer los abacos para la "
                      "geometria concreta de cada punto. Usar N_c y N_gamma "
                      "de terreno horizontal aqui seria exactamente la "
                      "sobrestimacion que la hoja de ruta advierte",
        fuente="PENDIENTE - Manual de Puentes num. 2.8.1.3.1.2c, figuras "
               "2.8.1.3.1.2c-1 y 2.8.1.3.1.2c-2 (Meyerhof 1957), pags. 272-273",
        reemplazado_por="Lectura de los abacos para la geometria real de cada "
                        "cabezal, adjuntada a la memoria",
        verificacion_pendiente="E.050 Art. 30.1-30.2 exige ADEMAS la "
                               "verificacion por inclinacion de la superficie "
                               "y de la base, y el analisis de estabilidad "
                               "global del talud con la estructura "
                               "cargandolo: son dos comprobaciones, no una "
                               "(Sec. 9.3, 'doble verificacion')",
    ),

    "metodo_estabilidad_global": Criterio(
        valor=None,                 # VACIO: bloquea las filas E4 y E5 de Sec. 9.3
        etiqueta="A",
        concepto="Metodo de analisis de estabilidad global del muro y del "
                 "talud que lo soporta (equilibrio limite: Bishop "
                 "simplificado, Spencer, Morgenstern-Price...)",
        justificacion="La tabla de Sec. 9.3 exige FS = 1.50 estatico y 1.25 "
                      "sismico para la estabilidad global del muro "
                      "(39.13.6 b) y para la del talud (Art. 30.3), pero un "
                      "FS de estabilidad global no se calcula con una "
                      "formula cerrada: sale de un analisis de superficies "
                      "de falla que exige el perfil estratigrafico completo, "
                      "la geometria del terraplen y un metodo declarado. "
                      "Ninguna de las tres cosas esta en el alcance del CSV "
                      "de Sec. 1.2. El FS existe y esta transcrito; lo que "
                      "falta es con que producir el valor a comparar",
        fuente="PENDIENTE - E.050 Art. 30.3 y num. 39.13.6 b) fijan el "
               "umbral, no el metodo. El analisis es del EMS del expediente",
        reemplazado_por="Analisis de estabilidad de taludes del estudio "
                        "geotecnico, con su metodo y sus superficies criticas",
    ),

    "recubrimiento_aashto_mm": Criterio(
        valor={"contra_suelo": 75.0, "suelo_intemperie_ge_3_4": 75.0,
              "suelo_intemperie_le_5_8": 75.0},
        etiqueta="C",
        concepto="Recubrimiento minimo del refuerzo exigido por AASHTO LRFD, "
                 "en mm, por condicion de exposicion, para compararlo con el "
                 "de E.060 Art. 7.7.1",
        justificacion="Sec. 0.2 fija la regla de conflicto: 'rige el "
                      "recubrimiento MAYOR entre AASHTO y E.060'. CERRADO "
                      "por verificacion externa: AASHTO LRFD Tabla 5.10.1-1 "
                      "no organiza el recubrimiento por diametro de barra "
                      "como E.060 (>= 3/4\" / <= 5/8\") -- lo organiza por "
                      "severidad de EXPOSICION. La Union (Piura) es corredor "
                      "costero, y la categoria de exposicion aplicable de "
                      "AASHTO es 'ambiente costero' = 75 mm, uniforme sin "
                      "importar el diametro de barra. Como 75 > 70 "
                      "(contra_suelo de E.060) y 75 > 50 y 75 > 40 (los dos "
                      "casos de intemperie de E.060), AASHTO gobierna en los "
                      "tres casos por la regla del mayor: no son tres "
                      "lecturas distintas de AASHTO, es el mismo valor de "
                      "exposicion costera aplicado a los tres casos de "
                      "E.060, declarado explicito en las tres claves para "
                      "que la memoria muestre la comparacion caso por caso",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., Tabla "
               "5.10.1-1, pag. 5-169, categoria de exposicion 'ambiente "
               "costero'",
        verificacion_pendiente="Con NF a 1.4 m y suelos salinos, E.060 "
                               "Art. 7.7.5.1 (ambiente corrosivo, 'aumentar "
                               "adecuadamente') es directamente invocable "
                               "(Sec. 3.3): el aumento se declara aparte, "
                               "porque el articulo no fija cuanto",
    ),

    "cortante_alto_muro_e060_art_11_10_10_2": Criterio(
        valor=None,                 # VACIO: bloquea el escalon de rho a 0.0025
        etiqueta="A",
        concepto="Si el muro del cabezal esta en la condicion de CORTANTE "
                 "ALTO de E.060 Art. 11.10.10.2, que escalona la cuantia "
                 "horizontal minima de 0.0020 a 0.0025",
        justificacion="E.060 no tiene un solo minimo de cuantia horizontal "
                      "de muro: tiene dos. El Art. 14.3.1 fija 0.0020, y el "
                      "Art. 11.10.10.2 lo sube a 0.0025 cuando la demanda de "
                      "cortante supera el umbral que ese articulo define "
                      "(del orden de Vu > 0.5*phi*Vc). Aplicar solo el "
                      "0.0020 sin comprobar el otro es quedarse con el "
                      "minimo mas bajo de los dos por omision. "
                      "POR QUE NO SE RESUELVE AQUI Y NO SE RELLENA: el "
                      "disparador es una DEMANDA DE CORTANTE, y M9 no "
                      "calcula cortante -- el diseno por flexion y corte "
                      "esta bloqueado entero en "
                      "'procedimiento_flexion_corte_aashto_sec5', que es de "
                      "AASHTO LRFD Sec. 5 por la Via 1 de Sec. 0.2. Sin Vu "
                      "no hay forma de contestar si el muro esta o no en esa "
                      "condicion, y contestar 'no' por defecto seria elegir "
                      "el minimo mas bajo en silencio, que es exactamente el "
                      "error que este archivo existe para impedir. "
                      "Se declara VACIO y `M9.cuantia_de_diseno` lo exige a "
                      "quien la llame: o se declara aqui, o el calculo se "
                      "detiene. "
                      "NOTA DE TAXONOMIA: el 0.0025 en si es [N] "
                      "-- articulo peruano vigente -- y su sitio natural "
                      "seria constantes_normativas.py. No esta alli porque "
                      "la hoja de ruta no transcribe el Art. 11.10.10.2: "
                      "solo cita el 14.3.1. Mientras la hoja de ruta no lo "
                      "recoja, el numero viaja en esta justificacion y no "
                      "como constante [N], para no crear una cita normativa "
                      "que la fuente de verdad del proyecto no respalda. "
                      "Ademas, la Via 1 de Sec. 0.2 abre una pregunta previa "
                      "que tambien hay que contestar en la memoria: si el "
                      "diseno estructural es de AASHTO, cual de los dos "
                      "minimos de E.060 se importa y con que argumento",
        fuente="PENDIENTE - E.060 Art. 11.10.10.2 (cuantia horizontal "
               "minima en muros con cortante alto). Verificar numeral y "
               "pagina contra el texto de E.060 antes de darle valor, y "
               "recoger el articulo en la hoja de ruta",
        reemplazado_por="Demanda de cortante Vu del cabezal, salida del "
                        "diseno de 'procedimiento_flexion_corte_aashto_sec5', "
                        "contrastada contra el umbral del Art. 11.10.10.2",
        verificacion_pendiente="Al cerrarlo, declarar en la memoria las dos "
                               "cosas por separado: el valor de Vu con que se "
                               "decidio, y si el minimo aplicado es el 0.0020 "
                               "del Art. 14.3.1 o el 0.0025 del "
                               "Art. 11.10.10.2",
    ),

    "procedimiento_flexion_corte_aashto_sec5": Criterio(
        valor={
            "phi_flexion": 0.90,
            "phi_corte": 0.90,
            "modelo_corte": "MCFT_seccional_directo_no_iterativo "
                            "(AASHTO LRFD 9a ed., 2020)",
            "beta": "4.8 / (1 + 750*epsilon_s)",
            "theta_grados": "29 + 3500*epsilon_s",
            "Vc_kN": "0.0316*beta*lambda*raiz(f_c_prima)*bv*dv",
            "Vs_kN": "(Vu/phi) - Vc - Vp",
            "espaciamiento_s_m": "Av*fy*dv*cot(theta) / Vs",
            "dv_m": "max(de - a/2, 0.9*de, 0.72*h)",
        },
        etiqueta="C",
        concepto="Procedimiento de diseno por flexion y corte de AASHTO LRFD "
                 "Seccion 5: factores de resistencia phi, limites de refuerzo "
                 "y modelo de corte (MCFT / beta-theta) aplicables",
        justificacion="Sec. 9.4 remite el diseno a 'AASHTO LRFD Seccion 5' y "
                      "no transcribia nada de esa seccion, en coherencia con "
                      "la Via 1 de Sec. 0.2 (AASHTO de extremo a extremo, "
                      "E.060 solo para durabilidad y recubrimientos). "
                      "Mezclarlo con las expresiones de E.060 -- que si "
                      "estan a mano y que muchos usarian por costumbre -- "
                      "romperia justamente la consistencia carga-resistencia "
                      "que Sec. 0.2 declara RESUELTA: no se pueden combinar "
                      "demandas mayoradas por AASHTO con resistencias "
                      "reducidas por E.060. CERRADO por verificacion "
                      "externa: Art. 5.5.4.2 da phi = 0.90 para flexion y "
                      "para corte; Arts. 5.7.3.4.2, 5.7.3.3 y 5.7.2.8 dan el "
                      "Modelo Seccional MCFT en su procedimiento directo no "
                      "iterativo de la 9a ed. (2020), con beta, theta, Vc, "
                      "Vs y dv en forma cerrada. Las cuantias minimas de "
                      "E.060 Art. 14.3.1 que M9 aplica son un PISO "
                      "OBLIGATORIO sobre el resultado de este procedimiento "
                      "-- rho_diseno = max(rho_calculado, rho_minimo) -- no "
                      "una nota de referencia: el rho que salga de AASHTO "
                      "entra por `M9.cuantia_de_diseno` y el minimo lo "
                      "levanta si hace falta. Cerrar este dato declara el "
                      "PROCEDIMIENTO citado y disponible; el ENSAMBLE "
                      "completo (iterar epsilon_s, resolver Vs y el "
                      "espaciamiento para un momento y un cortante dados) "
                      "sigue sin implementarse en `M9.diseno_flexion_corte` "
                      "-- es una tarea de implementacion aparte, mas grande "
                      "que transcribir un dato, y no se acomete aqui",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., "
               "Arts. 5.5.4.2 (pag. 5-32) y 5.7.3.4.2 / 5.7.3.3 / 5.7.2.8 "
               "(pags. 5-70 a 5-243)",
    ),
}


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
    """Forma del rango, orden de sus extremos, y el valor dentro de el."""
    s = c.sensibilidad
    if s is None:
        return
    if not s:
        raise ValueError(
            f"'{clave}' declara una sensibilidad vacia ({s!r}). O declara el "
            f"rango que se pudo elegir, o no declares el campo"
        )

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
    candidatos = c.valor if isinstance(c.valor, (tuple, list)) else (c.valor,)
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


def _verificar_criterio(clave: str, c: Criterio) -> None:
    """
    Valida UNA entrada. No lee CRITERIOS: recibe el objeto ya armado.

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

    _verificar_sensibilidad(clave, c)


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


def reporte_criterios(solo_usados: bool = True) -> str:
    """
    Genera el bloque de declaracion de criterios para el reporte final.
    Con solo_usados=True lista unicamente los criterios que el calculo invoco.
    """
    claves = sorted(
        (_USADOS if solo_usados else set(CRITERIOS)),
        key=lambda k: (_ORDEN.get(CRITERIOS[k].etiqueta, 9), k),
    )
    if not claves:
        return "No se invoco ningun criterio adoptado."

    out = ["=" * 78,
           "DECLARACION DE CRITERIOS ADOPTADOS",
           "=" * 78, ""]

    for k in claves:
        c = criterio_efectivo(k)
        valor_efectivo = c.valor
        marca_override = ("  [declarado para esta corrida, no en archivo]"
                          if declarado_en_caliente(k) else "")
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

    sin_valor = criterios_sin_valor()
    if sin_valor:
        out.append("")
        out.append("-" * 78)
        out.append("VACIOS SIN VALOR: detienen el calculo en cuanto se invocan")
        out.append("(bloque aparte, Sec. 0.7 - no se sustituyen por defecto):")
        for k in sin_valor:
            out.append(f"  - [{CRITERIOS[k].etiqueta}] {k}: {CRITERIOS[k].concepto}")
        out.append("-" * 78)

    en_caliente = criterios_declarados_en_caliente()
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
            out.append(f"  - [{c.etiqueta}] {k} = {_OVERRIDES[k]!r}  ({dice})")
        out.append("-" * 78)

    sin_consumidor = criterios_sin_consumidor()
    if sin_consumidor:
        out.append("")
        out.append("-" * 78)
        out.append("DECLARADOS QUE NINGUNA ETAPA INVOCA - con la razon escrita")
        out.append("en el propio criterio, no deducida de su ausencia:")
        for k in sin_consumidor:
            c = criterio_efectivo(k)
            out.append(f"  - [{c.etiqueta}] {k} = {c.valor!r}")
            out.append(f"      {c.sin_consumidor}")
        out.append("-" * 78)

    opcionales = criterios_opcionales_sin_declarar()
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
    import datos_sitio as ds

    A_s = ds.valor("PGA_roca_B") * valor("F_pga")
    k_h = valor("factor_muro_eleccion") * A_s
    valor("clase_sitio")

    print(f"A_s = {A_s:.2f} g")
    print(f"k_h = {k_h:.2f}")
    print(f"k_v = {valor('k_v'):.2f}\n")
    print(reporte_criterios())
