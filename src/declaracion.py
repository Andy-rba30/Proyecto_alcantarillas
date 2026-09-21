"""
declaracion.py
==============
DECLARAR desde la ventana, y dejar escrito de donde salio el valor.

La regla R1 del plan `docs/hoja_de_ruta_correcciones_v12.md`, entera
---------------------------------------------------------------------
    «La tabla es [N], la eleccion de fila es [A]. Elegir una fila NO convierte
    la eleccion en norma. La ventana escribe un criterio [A] cuyo valor
    PROVIENE DE la fila X de la tabla T.»

De ahi salen las dos mitades de este modulo, y por eso son dos y no una:

  1. EL VALOR entra al calculo por `criterios_adoptados.establecer_valor_dinamico`,
     que es el UNICO camino de declaracion en caliente y que somete lo
     declarado a `_verificar_criterio`, la misma guardia que corre al importar
     el archivo. Aqui no hay un segundo camino: este modulo no escribe en
     `_OVERRIDES`, no reasigna `CRITERIOS` y no toca el archivo fuente.
  2. LA PROCEDENCIA -- fila, valor, alternativas descartadas, cita y fecha --
     se registra APARTE, en este modulo, porque `Criterio` no tiene donde
     guardarla y porque no es parte del valor: es parte de como se llego a el.
     La memoria la imprime junto al valor; sin ella, «6.0 m/s» y «6.0 m/s
     porque es la fila Concreto de la Tabla N 10, descartando 3.0» son la
     misma linea en la pagina y no son la misma decision.

ESCRIBIR EL ARCHIVO DE CRITERIOS ES UNA ACCION APARTE Y EXPLICITA, y no esta
aqui: la hace `criterios_adoptados.escribir_valor_en_archivo`, que la GUI
llama detras de una confirmacion propia. Declarar para la corrida y fijar el
expediente son dos decisiones distintas y este modulo solo hace la primera.

Que NO se declara desde aqui
----------------------------
Solo los CRITERIOS. Una columna del CSV es un dato por punto y su sitio es el
CSV; un dato de sitio es un hecho determinado por un procedimiento y
`datos_sitio.py` no tiene API de escritura a proposito. En los dos casos la
ventana muestra todo y no deja declarar, diciendo de donde tiene que venir el
valor: es la regla R4 aplicada a la variable entera en vez de a una fila.

R4, en el camino de declaracion
-------------------------------
    «Cuando una fila depende de un dato que el proyecto no tiene, la ventana
    PIDE o BLOQUEA. Nunca elige.»

Aqui eso es un rechazo: `declarar_desde_tabla` comprueba la disponibilidad de
CADA fila y de CADA columna elegida, y si alguna no es `Elegible` no declara
nada y explica que falta. No hay «elegir igual y avisar»: un valor declarado
sobre una fila cuyo dato no existe es exactamente la eleccion en silencio que
la regla prohibe.

Regla de uso
------------
    from src import declaracion as dec

    dec.declarar_desde_tabla("ke_entrada", 0.5,
                             filas=("concreto_headwall_square_edge",))
    dec.procedencia_de("ke_entrada").alternativas_descartadas
    dec.validar_en_rango("v_max_concreto_eleccion", 7.0).estado
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src import criterios_adoptados as _ca
from src import variables_entrada as _ve
from src import ventana_normativa as _vn
from src.modelos import DeCatalogo, DeTabla, EnRango, ModoDeResolucion, Poblacion
from src.normativa import registro as _registro
from src.tolerancias import TOL_UMBRAL_NORMATIVO
from src.normativa.esquema import (BandaDeInterpolacion, ConjuntoDeMaximos,
                               IntervaloAdmisible, PisoUnico, TechoUnico)


# ===========================================================================
# La procedencia
# ===========================================================================

@dataclass(frozen=True)
class AlternativaDescartada:
    """
    Una fila (o columna) que estaba sobre la mesa y no se eligio.

    `motivo` distingue tres cosas que no son iguales: la alternativa que se
    podia elegir y no se eligio, la que el calculo no usa (y la fuente si
    imprime), y la que ni siquiera era elegible porque le falta un dato. Sin
    la distincion, una memoria que liste «alternativas descartadas» sugiere
    que las tres se compararon, y dos de ellas no se podian comparar.
    """
    id: str
    etiqueta: str
    valor: str
    motivo: str


@dataclass(frozen=True)
class Procedencia:
    """
    De donde salio un valor declarado. Lo que la Sec. 4.3 pide que la memoria
    escriba: fila elegida, valor, alternativas, cita y fecha.

    Es un objeto y no una cadena porque la memoria, el JSON de la sesion y la
    ventana lo necesitan desmontado: componer la frase en el sitio equivocado
    es como nacen dos versiones de la misma procedencia.
    """
    clave: str
    modo: str
    valor: Any
    fecha: str
    cita: str = ""
    cita_id: str = ""
    tabla_id: str = ""
    titulo_de_la_tabla: str = ""
    filas: Tuple[str, ...] = ()
    columnas: Tuple[str, ...] = ()
    filas_legibles: Tuple[str, ...] = ()
    alternativas_descartadas: Tuple[AlternativaDescartada, ...] = ()
    catalogo_id: str = ""
    semantica: str = ""
    frase_del_rango: str = ""
    rotulo_del_rango: str = ""
    aviso: str = ""
    nota: str = ""
    # LA CELDA DE LA QUE SE DICE QUE PROVIENE EL VALOR (EXT-V-02). Se guarda
    # cuando la eleccion nombra una fila y una columna con celda escalar --
    # o una fila con una sola celda numerica --, y es lo que permite que la
    # memoria distinga «proviene de la fila» de «DIFIERE de la celda»: -50
    # se declaraba con la procedencia de la fila 'Square-edge 0.5' de la
    # Tabla C.2 y nada lo desmentia. None cuando la eleccion no tiene celda
    # escalar que citar (F_pga declara filas, n_manning_hdpe un par).
    valor_de_la_celda: Optional[float] = None

    def difiere_de_la_celda(self) -> bool:
        """
        El valor declarado NO es el numero que la celda imprime. Solo puede
        ser verdadero cuando hay celda citada, y `declarar_desde_tabla` la
        cita unicamente para valores numericos: un criterio que declara la
        CLAVE de la fila nunca «difiere».
        """
        return (self.valor_de_la_celda is not None
                and not (_ca._es_real(self.valor)
                         and abs(self.valor - self.valor_de_la_celda)
                         <= TOL_UMBRAL_NORMATIVO))

    def como_texto(self) -> str:
        """
        La procedencia en una linea, como la imprime una memoria. La compone
        esta funcion y no un campo, por lo mismo que `Cita.como_texto`: los
        separadores son del proyecto.
        """
        trozos = [f"declarado el {self.fecha}"]
        if self.filas and self.difiere_de_la_celda():
            trozos.append(f"DIFIERE de la celda ({self.valor_de_la_celda}) de "
                          f"la fila {', '.join(self.filas)} de la tabla "
                          f"{self.tabla_id}: el valor declarado es "
                          f"{self.valor!r} y NO proviene de ella")
        elif self.filas:
            trozos.append(f"proviene de la fila {', '.join(self.filas)} de la "
                          f"tabla {self.tabla_id}")
        elif self.columnas:
            trozos.append(f"proviene de la columna {', '.join(self.columnas)} "
                          f"de la tabla {self.tabla_id}")
        elif self.tabla_id:
            trozos.append(f"proviene de la tabla {self.tabla_id} entera")
        elif self.catalogo_id:
            trozos.append(f"proviene del catalogo {self.catalogo_id}, que NO "
                          "es una norma")
        if self.frase_del_rango:
            trozos.append(f"{self.semantica}: {self.frase_del_rango}")
        if self.cita:
            trozos.append(self.cita)
        if self.alternativas_descartadas:
            descartadas = "; ".join(
                f"{a.id} ({a.valor}){' -- ' + a.motivo if a.motivo else ''}"
                for a in self.alternativas_descartadas)
            trozos.append(f"alternativas descartadas: {descartadas}")
        if self.aviso:
            trozos.append(f"AVISO: {self.aviso}")
        if self.nota:
            trozos.append(self.nota)
        return " · ".join(trozos)


# El libro de procedencias de la corrida. Hermano de
# `criterios_adoptados._OVERRIDES` y con su misma vida: vale para ESTA corrida
# y no viaja al archivo. Se mantiene aparte del valor porque el valor tiene
# guardia propia y la procedencia no es un valor.
_PROCEDENCIAS: Dict[str, Procedencia] = {}


def procedencia_de(clave: str) -> Optional[Procedencia]:
    """La procedencia registrada de una clave, o None si no se declaro aqui."""
    return _PROCEDENCIAS.get(clave)


def procedencias() -> Dict[str, Procedencia]:
    """Todas las procedencias de la corrida, por clave."""
    return dict(_PROCEDENCIAS)


def olvidar(clave: str) -> None:
    """
    Retira la declaracion de la corrida: el valor Y su procedencia.

    Las dos juntas y en una sola funcion, porque separarlas dejaria una
    procedencia hablando de un valor que ya no gobierna nada, que es peor que
    no tener procedencia.
    """
    _ca.quitar_valor_dinamico(clave)
    _PROCEDENCIAS.pop(clave, None)


def limpiar() -> None:
    """Retira todas las procedencias. No toca los valores: eso es `olvidar`."""
    _PROCEDENCIAS.clear()


def olvidar_procedencia(clave: str) -> None:
    """
    Retira SOLO la procedencia de una clave, dejando el valor.

    Es lo que corresponde cuando un valor entra por un camino SIN
    procedencia sobre una clave que la tenia --- el campo de texto de la
    pestaña 2, o «Importar decisiones» con una clave que la sesion trae sin
    procedencia ---: la procedencia vieja hablaria de un numero que ya no
    gobierna, con su `valor` impreso al lado del nuevo. Encontrado por la
    auditoria adversarial de EXT-4 como el defecto EXT-A-02 por otra puerta.
    """
    _PROCEDENCIAS.pop(clave, None)


def _ahora() -> str:
    """La fecha de la declaracion, en ISO 8601 hasta el segundo."""
    return datetime.now().isoformat(timespec="seconds")


# ===========================================================================
# Validacion de un valor contra un rango del registro
# ===========================================================================

class Estado(str, Enum):
    """
    Las tres respuestas posibles, y son tres a proposito.

    `AVISO` no es un `INVALIDO` blando: separa «el valor incumple lo que la
    fuente escribe» de «el valor no incumple nada y la fuente tampoco lo
    escribe». El segundo es el 4.5 m/s dentro de la fila de la Tabla N 10,
    cuyos dos numeros son maximos: 4.5 no pasa de 6.0 -- no incumple -- y no
    es ninguno de los dos valores impresos. Rechazarlo seria inventar una
    prohibicion; callarlo seria dejar que se lea como si la tabla lo dijera.
    """
    VALIDO = "valido"
    AVISO = "aviso"
    INVALIDO = "invalido"


@dataclass(frozen=True)
class ResultadoValidacion:
    """El veredicto de validar al escribir, con el mensaje que se pinta."""
    estado: Estado
    mensaje: str
    frase_del_rango: str = ""
    semantica: str = ""

    @property
    def acepta(self) -> bool:
        """Un aviso NO impide declarar: solo un invalido lo hace."""
        return self.estado is not Estado.INVALIDO


def _como_numero(valor: Any) -> Optional[float]:
    """
    Un real FINITO como float; None para todo lo demas. `bool` queda fuera
    (True pasaria por 1.0); un texto tambien, aunque se lea como numero: el
    parser de la GUI ya entrego lo que habia que entregar, y 'nan' llega
    aqui como TEXTO a proposito (ver `gui.componentes`). Un NaN o un
    infinito numerico tampoco es un numero contra el que validar: es la
    otra mitad del mismo veredicto (PC-14).
    """
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)) and math.isfinite(valor):
        return float(valor)
    return None


def validar_contra_rango(rango: Any, valor: Any) -> ResultadoValidacion:
    """
    Compara un valor con un rango del registro SEGUN SU TIPO.

    No hay una comparacion generica «minimo <= v <= maximo»: el tipo del rango
    es su semantica, y aplicar la comparacion de un intervalo a un
    `ConjuntoDeMaximos` convierte el primero de dos techos en un piso
    (NOR-HID-04). Cada rama de abajo es la lectura de UNA de las cinco formas
    que el registro declara, y la funcion falla en vez de adivinar si aparece
    una sexta.

    TODAS LAS COMPARACIONES VAN EN LA FORMA MAT-D13 (EXT-5): condicion en
    positivo y NEGADA (`not numero <= techo`), nunca en positivo. Un NaN es
    falso frente a `<=` igual que frente a `>`, y escrita en positivo la rama
    de `ConjuntoDeMaximos` lo dejaba caer en la lectura intermedia --- un
    AVISO ambar para lo que no es un numero ---. `_como_numero` lo atrapa
    antes; la forma negada es lo que impide que vuelva a pasar si algo lo
    esquiva.
    """
    frase = _vn.frase_del_rango(rango)
    semantica = type(rango).__name__
    numero = _como_numero(valor)
    if numero is None:
        return ResultadoValidacion(
            Estado.INVALIDO,
            f"'{valor}' no es un numero finito, y este valor se acota con un "
            f"rango que la fuente escribe: {frase}", frase, semantica)

    def veredicto(estado: Estado, mensaje: str) -> ResultadoValidacion:
        return ResultadoValidacion(estado, mensaje, frase, semantica)

    fuera = _vn._QUE_PASA_FUERA[rango.que_pasa_fuera]

    if isinstance(rango, IntervaloAdmisible):
        if not rango.minimo <= numero <= rango.maximo:
            return veredicto(Estado.INVALIDO,
                             f"fuera del rango. La fuente escribe: {frase}. Si se "
                             f"sale, {fuera}")
        return veredicto(Estado.VALIDO, f"dentro del rango: {frase}")
    if isinstance(rango, TechoUnico):
        if not numero <= rango.maximo:
            return veredicto(Estado.INVALIDO,
                             f"por encima del techo. La fuente escribe: {frase}. "
                             f"Si se pasa, {fuera}")
        return veredicto(Estado.VALIDO, f"por debajo del techo: {frase}")
    if isinstance(rango, PisoUnico):
        if not numero >= rango.minimo:
            return veredicto(Estado.INVALIDO,
                             f"por debajo del piso. La fuente escribe: {frase}. "
                             f"Si se baja, {fuera}")
        return veredicto(Estado.VALIDO, f"por encima del piso: {frase}")
    if isinstance(rango, ConjuntoDeMaximos):
        techo = max(rango.valores)
        if not numero <= techo:
            return veredicto(
                Estado.INVALIDO,
                f"pasa del mayor de los maximos que la fuente escribe. "
                f"{frase}. Si se pasa, {fuera}")
        if numero in rango.valores:
            return veredicto(
                Estado.VALIDO,
                f"es uno de los maximos que la fuente escribe. {frase}")
        return veredicto(
            Estado.AVISO,
            f"no pasa del mayor de los maximos, y NO es ninguno de los "
            f"valores que la fuente escribe: es una lectura intermedia del "
            f"proyectista sobre una tabla que no manda interpolar. {frase}")
    if isinstance(rango, BandaDeInterpolacion):
        ordenadas = tuple(b for _, b in rango.puntos)
        if not min(ordenadas) <= numero <= max(ordenadas):
            return veredicto(
                Estado.INVALIDO,
                f"fuera de la banda que la fuente define. {frase}. Fuera de ella, "
                f"{fuera}")
        return veredicto(
            Estado.AVISO,
            f"cae dentro de la banda, pero la fuente no acota este valor: "
            f"manda OBTENERLO por interpolacion desde su abscisa. {frase}")
    raise TypeError(
        f"{semantica} no es un rango del registro: validar un valor contra un "
        "rango se hace por su tipo, nunca comparando dos numeros sueltos")


def validar_en_rango(clave: str, valor: Any) -> ResultadoValidacion:
    """
    Valida AL ESCRIBIR el valor de una variable `en_rango`.

    Al escribir y no al calcular: es lo que pide la Sec. 4.3, y la diferencia
    es que el proyectista corrige el numero mientras lo esta pensando, en vez
    de descubrir tres pantallas mas tarde que la corrida se detuvo.
    """
    v = _ve.variable(clave)
    if not isinstance(v.resolucion, EnRango):
        raise ValueError(
            f"'{clave}' se resuelve `{v.modo.value}`, no `en_rango`: no hay "
            "rango contra el que validar")
    return validar_contra_rango(_ve.rango_de(clave), valor)


# ===========================================================================
# Declarar
# ===========================================================================

def _exigir_declarable(clave: str) -> None:
    v = _ve.variable(clave)
    if v.poblacion is not Poblacion.CRITERIO:
        raise ValueError(
            f"'{clave}' no se declara desde la ventana: "
            f"{_vn._POR_QUE_NO_DECLARABLE[v.poblacion]}")


def _tabla_unica(clave: str, tabla_id: Optional[str]) -> str:
    """
    Que tabla se esta usando. Explicita cuando la variable declara varias.

    `DeTabla.tablas` es una tupla porque hay elecciones que se hacen mirando
    dos (las de estribos y muros de AASHTO 3.11.6.4 se leen juntas). Con dos
    tablas, elegir una por el usuario seria adivinar cual miro.
    """
    v = _ve.variable(clave)
    tablas = v.resolucion.tablas
    if tabla_id is not None:
        if tabla_id not in tablas:
            raise ValueError(
                f"'{clave}' se resuelve con {tablas} y no con '{tabla_id}'")
        return tabla_id
    if len(tablas) > 1:
        raise ValueError(
            f"'{clave}' se lee sobre {len(tablas)} tablas ({', '.join(tablas)}): "
            "hay que decir sobre cual se hizo la eleccion")
    return tablas[0]


def _alternativas(contenido: _vn.ContenidoDeTabla, filas: Sequence[str],
                  columnas: Sequence[str]) -> Tuple[AlternativaDescartada, ...]:
    """
    Lo que quedo sobre la mesa. Se compone del contenido de la ventana, no de
    la tabla cruda: asi la alternativa se describe con el mismo texto que el
    usuario vio al elegir.
    """
    salida: List[AlternativaDescartada] = []
    if filas:
        elegidas = set(filas)
        for f in contenido.filas:
            if f.id in elegidas or f.clave_corta in elegidas:
                continue
            valor = " / ".join(f"{k}={v}" for k, v in f.celdas.items())
            if not f.elegible:
                motivo = f"NO era elegible: {_motivo_de(f.disponibilidad)}"
            elif f.atenuada:
                motivo = f"el calculo no la usa: {f.motivo}"
            else:
                motivo = "alternativa viva, no elegida"
            salida.append(AlternativaDescartada(
                id=f.clave_corta, etiqueta=f.etiqueta_legible, valor=valor,
                motivo=motivo))
    if columnas:
        elegidas = set(columnas)
        for c in contenido.columnas:
            if c.id in elegidas:
                continue
            if c.disponibilidad is not None and \
                    not isinstance(c.disponibilidad, _vn.Elegible):
                motivo = f"NO era elegible: {_motivo_de(c.disponibilidad)}"
            elif c.atenuada:
                motivo = f"el calculo no la usa: {c.motivo}"
            else:
                motivo = "alternativa viva, no elegida"
            salida.append(AlternativaDescartada(
                id=c.id, etiqueta=c.etiqueta_literal, valor=c.unidad,
                motivo=motivo))
    return tuple(salida)


def _motivo_de(disponibilidad: _vn.Disponibilidad) -> str:
    if isinstance(disponibilidad, _vn.PideDato):
        return (f"falta declarar '{disponibilidad.clave_que_falta}' "
                f"({disponibilidad.concepto_de_lo_que_falta})")
    if isinstance(disponibilidad, _vn.BloqueaLaEleccion):
        return (f"{disponibilidad.por_que}. Lo cerraria: "
                f"{disponibilidad.que_lo_cerraria}")
    return ""


def _exigir_elegibles(contenido: _vn.ContenidoDeTabla, filas: Sequence[str],
                      columnas: Sequence[str]) -> None:
    """
    R4 en el camino de declaracion: no se elige una fila cuya condicion no se
    puede resolver. No declara nada y dice que falta.
    """
    por_id = {}
    for f in contenido.filas:
        por_id[f.id] = f
        por_id[f.clave_corta] = f
    for fila in filas:
        if fila not in por_id:
            raise ValueError(
                f"la tabla {contenido.tabla_id} no tiene la fila '{fila}'")
        f = por_id[fila]
        if not f.elegible:
            raise ValueError(
                f"R4: la fila '{fila}' de {contenido.tabla_id} depende de un "
                f"dato que el proyecto no tiene y NO se puede elegir. "
                f"{_motivo_de(f.disponibilidad)}")
    columnas_por_id = {c.id: c for c in contenido.columnas}
    for columna in columnas:
        if columna not in columnas_por_id:
            raise ValueError(
                f"la tabla {contenido.tabla_id} no tiene la columna "
                f"'{columna}'")
        c = columnas_por_id[columna]
        if c.disponibilidad is not None and \
                not isinstance(c.disponibilidad, _vn.Elegible):
            raise ValueError(
                f"R4: la columna '{columna}' de {contenido.tabla_id} depende "
                f"de un dato que el proyecto no tiene y NO se puede elegir. "
                f"{_motivo_de(c.disponibilidad)}")


def valor_propuesto(tabla_id: str, fila_id: str,
                    columna_id: str) -> Any:
    """
    La celda que la tabla escribe en el cruce de una fila y una columna.

    Es lo que la ventana PROPONE, no lo que declara: el valor que entra al
    calculo lo confirma quien firma, porque la celda no siempre es el valor
    (`F_pga` declara las filas que se leen, no un numero; `n_manning_hdpe`
    declara el par entero de una fila). Proponer y declarar separados es lo
    que impide que la ventana elija.
    """
    tabla = _registro.construir().tabla(tabla_id)
    return tabla.fila(fila_id).valores[columna_id]


def declarar_desde_tabla(clave: str, valor: Any, *,
                         tabla_id: Optional[str] = None,
                         filas: Sequence[str] = (),
                         columnas: Sequence[str] = (),
                         nota: str = "") -> Procedencia:
    """
    Declara un criterio cuyo valor PROVIENE de una tabla del registro.

    Lo que la regla R1 exige, hecho en este orden y sin atajos:

      1. la variable tiene que resolverse `de_tabla` y ser declarable aqui;
      2. las filas y columnas elegidas tienen que ser ELEGIBLES (R4);
      3. el valor entra por `establecer_valor_dinamico`, que lo somete a la
         guardia del archivo -- si el criterio declara sensibilidad y el valor
         cae fuera, se rechaza AQUI y no mas tarde;
      4. y solo si todo lo anterior paso, se registra la procedencia.

    El orden importa: registrar la procedencia antes del paso 3 dejaria una
    procedencia de un valor que la guardia rechazo.
    """
    _exigir_declarable(clave)
    v = _ve.variable(clave)
    if not isinstance(v.resolucion, DeTabla):
        raise ValueError(
            f"'{clave}' se resuelve `{v.modo.value}`, no `de_tabla`")
    usada = _tabla_unica(clave, tabla_id)
    contenido = _vn.contenido_de_tabla(usada, clave)
    _exigir_elegibles(contenido, filas, columnas)
    # LA CELDA SOLO SE CITA CUANDO LO DECLARADO ES UN NUMERO. Hay criterios
    # que declaran la CLAVE DE LA FILA y no su coeficiente ('ke_entrada_cajon',
    # 'embocadura_cajon': «lo que se declara es la CLAVE de la fila»), y para
    # ellos el valor no es la celda ni pretende serlo: la procedencia dice
    # «fila» y basta. Lo encontro el auditor adversarial de EXT-1: la primera
    # version comparaba la clave con el 0.4 de la celda y rechazaba la
    # declaracion legitima que hace la ventana de la GUI. Un texto declarado
    # donde el criterio espera un numero lo rechaza la propia guardia del
    # criterio (`_verificar_sensibilidad`), no esta.
    celda = _celda_escalar(usada, filas, columnas) if _ca._es_real(valor) else None
    if celda is not None and not nota.strip() and not (
            abs(valor - celda) <= TOL_UMBRAL_NORMATIVO):
        # PROCEDENCIA VERAZ (EXT-V-02): si el valor no es el de la celda que
        # se nombra, o se dice por que (nota) o no se declara. Sin esto -50
        # entraba con «proviene de la fila 'Square-edge 0.5'».
        raise ValueError(
            f"'{clave}': el valor declarado {valor!r} DIFIERE de la celda "
            f"{celda!r} de la fila {', '.join(filas)} de {usada}, y no trae "
            "`nota`. Un valor que no es el de la celda no PROVIENE de ella: "
            "o se declara la celda, o se escribe en la nota por que se "
            "adopta otro numero (la memoria lo imprimira como «DIFIERE de "
            "la celda»)")

    _ca.establecer_valor_dinamico(clave, valor)

    legibles = tuple(f.etiqueta_legible for f in contenido.filas
                     if f.id in set(filas) or f.clave_corta in set(filas))
    procedencia = Procedencia(
        clave=clave, modo=v.modo.value, valor=valor, fecha=_ahora(),
        cita=contenido.linea_de_cita, cita_id=contenido.cita.id,
        tabla_id=usada, titulo_de_la_tabla=contenido.titulo_literal,
        filas=tuple(filas), columnas=tuple(columnas), filas_legibles=legibles,
        alternativas_descartadas=_alternativas(contenido, filas, columnas),
        nota=nota or v.resolucion.que_elige,
        valor_de_la_celda=celda)
    _PROCEDENCIAS[clave] = procedencia
    return procedencia


def _celda_escalar(tabla_id: str, filas: Sequence[str],
                   columnas: Sequence[str]) -> Optional[float]:
    """
    El numero que la tabla imprime en la celda elegida, o None si la eleccion
    no señala UNA celda escalar.

    Hay celda cuando se nombra exactamente una fila y una columna, o una sola
    fila que tiene UNA sola celda numerica (la Tabla C.2 tiene una columna de
    coeficientes, y la ventana de la GUI deja elegir solo la fila). Con varias
    filas, varias columnas, una celda no numerica (un rango, un texto) o una
    fila con varias celdas numericas (los tres n de la Tabla N 09) no hay
    celda que citar y se devuelve None: la procedencia dice «fila» y nada
    mas, como hasta ahora.
    """
    if len(filas) != 1 or len(columnas) > 1:
        return None
    tabla = _registro.construir().tabla(tabla_id)
    fila_id = filas[0]
    fila = next((f for f in tabla.filas
                 if f.id == fila_id or tabla.clave_corta(f) == fila_id), None)
    if fila is None:
        return None
    if columnas:
        celda = fila.valores.get(columnas[0])
        return float(celda) if _ca._es_real(celda) else None
    numericas = [x for x in fila.valores.values() if _ca._es_real(x)]
    if len(numericas) != 1:
        return None
    return float(numericas[0])


def declarar_en_rango(clave: str, valor: Any, *,
                      nota: str = "") -> Procedencia:
    """
    Declara un criterio acotado por un rango que una fuente escribe.

    La validacion es la misma que la ventana corre al escribir, y por eso se
    llama a la misma funcion: dos validaciones distintas para el mismo campo
    -- una al teclear y otra al aceptar -- es la forma de que la ventana diga
    una cosa y el valor declarado sea otra.

    Un `AVISO` no impide declarar y VIAJA en la procedencia. Es el caso de la
    Tabla N 10: 4.5 m/s no incumple nada -- no pasa del mayor de los dos
    maximos -- y tampoco lo escribe la fuente, y la memoria tiene que decirlo
    en vez de imprimirlo como si la tabla lo trajera.
    """
    _exigir_declarable(clave)
    v = _ve.variable(clave)
    if not isinstance(v.resolucion, EnRango):
        raise ValueError(
            f"'{clave}' se resuelve `{v.modo.value}`, no `en_rango`")
    resultado = validar_en_rango(clave, valor)
    if not resultado.acepta:
        raise ValueError(
            f"'{clave}' no admite el valor {valor!r}: {resultado.mensaje}")

    _ca.establecer_valor_dinamico(clave, valor)

    contenido = _vn.contenido_de_rango(clave)
    procedencia = Procedencia(
        clave=clave, modo=v.modo.value, valor=valor, fecha=_ahora(),
        cita=contenido.rango_normativo.cita,
        cita_id=_registro.construir().tabla(contenido.tabla_id).cita_id,
        tabla_id=contenido.tabla_id,
        titulo_de_la_tabla=contenido.titulo_de_la_tabla,
        filas=(contenido.fila_id,), columnas=(contenido.columna_id,),
        filas_legibles=(contenido.fila_legible,),
        semantica=resultado.semantica,
        frase_del_rango=resultado.frase_del_rango,
        rotulo_del_rango=contenido.rango_normativo.rotulo,
        aviso=resultado.mensaje if resultado.estado is Estado.AVISO else "",
        nota=nota or contenido.que_acota)
    _PROCEDENCIAS[clave] = procedencia
    return procedencia


def declarar_valor(clave: str, valor: Any, *, nota: str = "") -> Procedencia:
    """
    Declara un criterio que no se lee de una tabla ni de un rango: `libre`,
    `de_ensayo`, `derivada` o `de_catalogo`.

    Sigue registrando procedencia, y con eso se cierra el criterio de salida
    de la sesion: TODO valor que entra por la ventana deja escrito de donde
    salio, tambien cuando la respuesta es «lo puso quien firma». Una
    procedencia que solo existiera para las tablas dejaria la mitad del
    tablero sin trazar y haria creer que la otra mitad no tiene origen.
    """
    _exigir_declarable(clave)
    v = _ve.variable(clave)
    catalogo_id = ""
    aviso = ""
    if isinstance(v.resolucion, DeCatalogo):
        catalogo = _vn.contenido_de_catalogo(clave)
        catalogo_id = catalogo.catalogo_id
        aviso = catalogo.advertencia

    _ca.establecer_valor_dinamico(clave, valor)

    procedencia = Procedencia(
        clave=clave, modo=v.modo.value, valor=valor, fecha=_ahora(),
        catalogo_id=catalogo_id, aviso=aviso,
        nota=nota or _nota_por_defecto(v))
    _PROCEDENCIAS[clave] = procedencia
    return procedencia


def _nota_por_defecto(v) -> str:
    campo = _vn.contenido_de_campo(v.clave) if v.modo in (
        ModoDeResolucion.LIBRE, ModoDeResolucion.DE_ENSAYO,
        ModoDeResolucion.DERIVADA) else None
    if campo is None:
        return _vn.ventana(v.clave).que_elige
    if campo.que_lo_fija:
        return campo.que_lo_fija
    if campo.ensayo:
        return f"{campo.ensayo} · {campo.trazabilidad_exigida}"
    return campo.regla_de_derivacion


# ===========================================================================
# La sesion: guardar y restaurar lo declarado (SIS-A-18)
# ===========================================================================
# La sesion JSON guardaba el CSV, el proyecto y las cinco banderas, y NO las
# declaraciones de la corrida. Quien declaraba cinco criterios, guardaba la
# sesion y la volvia a abrir al dia siguiente recuperaba el nombre del archivo
# y perdia las cinco decisiones, sin aviso: la corrida siguiente se detenia
# en el primer `CriterioPendienteError` y nada decia que la sesion las habia
# tenido.
#
# Se guardan las dos mitades -- valor y procedencia -- porque restaurar solo
# el valor devolveria un numero sin origen, y la memoria de la corrida
# restaurada diria menos que la de la corrida original.
#
# LO QUE SIS-A-18 NO PROBO, y EXT-4 cerro (EXT-A-02, SIS-B-22): la ida y
# vuelta de UNA sesion no dice que pasa con la anterior. `restaurar_sesion`
# era aditiva, de modo que abrir la sesion de la obra B tras declarar en la
# obra A dejaba las claves de A vivas, `estado_de_sesion()` de B las guardaba,
# y una clave de B sin procedencia heredaba la procedencia de A. Desde EXT-4
# abrir SUSTITUYE (`sustituir=True`, con el candidato validado en seco antes
# de vaciar) e importar SUMA (`sustituir=False`); el resultado dice ademas
# que se retiro.


def estado_de_sesion() -> Dict[str, Any]:
    """
    Lo declarado en la corrida, listo para `json.dump`.

    Los valores salen de `criterios_adoptados.valores_dinamicos()` y no del
    libro de procedencias: una declaracion hecha por la CLI (`--declarar`) o
    por `conftest` no tiene procedencia y aun asi gobierna el calculo, y una
    sesion que solo guardara lo declarado por la ventana perderia en silencio
    lo demas.
    """
    return {
        "valores": dict(_ca.valores_dinamicos()),
        "procedencias": {clave: asdict(p)
                         for clave, p in _PROCEDENCIAS.items()},
    }


@dataclass(frozen=True)
class ResultadoDeRestauracion:
    """
    Que se pudo reponer y que no. Las dos listas, siempre.

    Una restauracion que solo dijera «5 criterios restaurados» esconderia el
    caso que importa: el criterio que la sesion traia y que hoy la guardia
    rechaza -- porque el archivo cambio de sensibilidad, o porque la clave ya
    no existe --. Ese tiene que verse, y por eso `rechazados` lleva el motivo.
    """
    restaurados: Tuple[str, ...]
    rechazados: Tuple[Tuple[str, str], ...]
    # Lo que la corrida tenia declarado y la sesion abierta NO trae: con
    # `sustituir=True` se retira, y se dice, porque una declaracion que
    # desaparece en silencio es tan grave como una que aparece en silencio.
    retirados: Tuple[str, ...] = ()

    @property
    def hubo_rechazos(self) -> bool:
        return bool(self.rechazados)


def restaurar_sesion(estado: Any, *,
                     sustituir: bool = True) -> ResultadoDeRestauracion:
    """
    Repone las declaraciones de una sesion guardada.

    Por el MISMO camino que la ventana y que la CLI:
    `establecer_valor_dinamico`, con su guardia. Un JSON de sesion es un
    archivo que alguien pudo editar a mano, y meterlo en `_OVERRIDES` sin
    guardia convertiria el formato de sesion en la puerta de atras que este
    proyecto no tiene.

    Lo que la guardia rechaza no se descarta en silencio: sale en
    `rechazados`, con el motivo, para que la ventana lo muestre.

    ABRIR UNA SESION SUSTITUYE; IMPORTAR SUMA (EXT-A-02, SIS-B-22). Hasta
    EXT-4 esta funcion era ADITIVA: abrir la sesion de la obra B tras
    declarar en la obra A dejaba las claves de A vivas, `estado_de_sesion()`
    de B las persistia, y una clave de B sin procedencia HEREDABA la
    procedencia de A --- la memoria de B afirmaba de donde salio un valor
    que salio de otra obra ---. Con `sustituir=True` (el defecto, y lo que
    «Cargar sesion» hace) se vacia TODO lo declarado y el libro de
    procedencias, y se vuelca solo lo que la sesion trae y la guardia
    acepta; `retirados` dice que se fue. Con `sustituir=False` --- «Importar
    decisiones» --- se suma a lo declarado, que es otra accion y se pide
    por otro boton.

    EL CANDIDATO SE VALIDA ENTERO, EN SECO, ANTES DE VACIAR NADA
    (`criterios_adoptados.verificar_declaracion`): lo aceptado, lo rechazado
    y lo retirado se conocen ANTES de tocar el estado, y el vaciado solo
    ocurre con esa cuenta hecha. Cada clave aceptada entra igualmente por
    `establecer_valor_dinamico`, que es el unico camino al valor; como la
    guardia es determinista y no depende de otras claves, la segunda pasada
    no puede rechazar lo que la primera acepto.
    """
    if not isinstance(estado, dict):
        raise ValueError(
            "el bloque de criterios de la sesion no es un objeto con claves: "
            f"trae {type(estado).__name__}")
    valores = estado.get("valores", {})
    if not isinstance(valores, dict):
        raise ValueError(
            "el bloque 'valores' de la sesion no es un objeto con claves: "
            f"trae {type(valores).__name__}")
    guardadas = estado.get("procedencias", {})
    if not isinstance(guardadas, dict):
        guardadas = {}

    # 1. En seco: que acepta la guardia, y con que procedencia.
    aceptados: List[Tuple[str, Any, Optional[Procedencia]]] = []
    rechazados: List[Tuple[str, str]] = []
    for clave, valor in valores.items():
        try:
            _ca.verificar_declaracion(clave, valor)
        except (ValueError, KeyError) as exc:
            rechazados.append((clave, str(exc)))
            continue
        procedencia: Optional[Procedencia] = None
        cruda = guardadas.get(clave)
        if isinstance(cruda, dict):
            try:
                procedencia = _procedencia_desde_json(cruda)
            except (TypeError, KeyError) as exc:
                rechazados.append(
                    (clave, f"el valor se restauro y su procedencia no: {exc}"))
        aceptados.append((clave, valor, procedencia))

    # 2. Vaciar, si se abre una sesion y no se importa.
    retirados: Tuple[str, ...] = ()
    if sustituir:
        previas = set(_ca.valores_dinamicos()) | set(_PROCEDENCIAS)
        _ca.limpiar_valores_dinamicos()
        _PROCEDENCIAS.clear()
        retirados = tuple(sorted(previas - {clave for clave, _, _ in aceptados}))

    # 3. Volcar solo lo aceptado, por el unico camino. Una clave que la
    # sesion trae SIN procedencia entra sin procedencia: tambien al importar
    # (`sustituir=False`), donde la clave pudo tenerla de la obra anterior y
    # heredarla seria EXT-A-02 por otra puerta.
    for clave, valor, procedencia in aceptados:
        _ca.establecer_valor_dinamico(clave, valor)
        if procedencia is not None:
            _PROCEDENCIAS[clave] = procedencia
        else:
            _PROCEDENCIAS.pop(clave, None)
    return ResultadoDeRestauracion(tuple(clave for clave, _, _ in aceptados),
                                   tuple(rechazados), retirados)


def _procedencia_desde_json(crudo: Dict[str, Any]) -> Procedencia:
    """
    Rearma una `Procedencia` del JSON, con sus tuplas.

    `asdict` convierte las tuplas en listas y las `AlternativaDescartada` en
    diccionarios; volver a montarlas aqui es lo que hace que la procedencia
    restaurada sea del mismo tipo que la original y no un dict parecido que
    la memoria tendria que tratar aparte.
    """
    datos = dict(crudo)
    for campo in ("filas", "columnas", "filas_legibles"):
        if campo in datos:
            datos[campo] = tuple(datos[campo])
    alternativas = datos.get("alternativas_descartadas", ())
    datos["alternativas_descartadas"] = tuple(
        AlternativaDescartada(**a) if isinstance(a, dict) else a
        for a in alternativas)
    return Procedencia(**datos)
