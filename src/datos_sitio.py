"""
datos_sitio.py
==============
Datos de sitio `[S]`: hechos de ESTE emplazamiento, validos para TODO el
corredor, obtenidos con un procedimiento normativo real aplicado a las
coordenadas o condiciones de este proyecto.

Que es la etiqueta [S]
----------------------
    [S]  Dato de sitio. Obtenido mediante un procedimiento normativo real
         (mapa, ensayo, medicion de campo) aplicado a las coordenadas o
         condiciones de este proyecto. No es eleccion del proyectista ni
         analogia: es un hecho determinado, no portable a otro proyecto.
         En vez de sensibilidad declara TRAZABILIDAD obligatoria: el
         procedimiento exacto, la fuente, y si el dato aplica a todo el
         corredor o varia punto a punto.

Nacio porque las cuatro etiquetas anteriores no tenian casilla para esto:
`N` supone un valor que la norma fija igual para cualquier obra del pais,
`N->` supone una regla prestada de otro caso, `C` supone una fuente tecnica
ajena cubriendo un vacio, y `A` supone que alguien ELIGIO. Nadie eligio el
PGA del mapa ni la zona sismica: se leyeron.

Por que este archivo NO es tolerancias.py ni dominios.py
--------------------------------------------------------
`tolerancias.py` y `dominios.py` estan exentos de la regla "todo literal
numerico es un defecto" porque NO son valores de proyecto: una tolerancia es
el ultimo bit del float y un limite de dominio dice si una celda del CSV es
legible. Cambiarlos no mueve ninguna magnitud fisica.

Lo de aqui es exactamente lo contrario: SI son valores de proyecto, y de los
mas pesados -- el PGA gobierna toda la cadena sismica del cabezal. Este
archivo esta separado por la razon opuesta a la de aquellos dos: no porque
sus numeros no importen, sino porque importan y NO son constantes
universales. Copiar este archivo a otra obra sin releer los mapas sobre las
nuevas coordenadas es el error que la etiqueta [S] existe para impedir.

Por que este archivo NO es una columna del CSV
----------------------------------------------
Un dato de sitio y una columna del CSV son los dos datos de ESTE expediente;
la frontera es el AMBITO:

    varia punto a punto  ->  columna del CSV (`cbr_subrasante`,
                             `sucs_fundacion`, `NF_profundidad_m`): el dato
                             se mide en cada cruce y la fila lo trae.
    unico para el tramo  ->  este archivo: la lectura es una sola para los
                             ~5 km del corredor (Fase 0-bis) y repetirla en
                             cada fila fingiria cuatro mediciones donde hubo
                             una.

Si algun dia un dato de aqui deja de ser unico para el corredor -- porque el
corredor crece o porque aparece evidencia de que varia -- no se ajusta su
valor: se MUEVE a una columna del CSV. La `trazabilidad` de cada dato dice
sobre que ambito se leyo, justamente para que esa decision no dependa de la
memoria de nadie.

Por que este archivo NO es constantes_normativas.py ni criterios_adoptados.py
-----------------------------------------------------------------------------
`constantes_normativas.py` responde "que exige la norma" y solo admite [N]:
valores que serian el MISMO numero en cualquier obra del Peru. "La Union esta
en Zona 4" cita E.030 correctamente y aun asi no es eso -- es donde esta esta
via. `criterios_adoptados.py` responde "que decidio el proyectista donde la
norma calla", y aqui no hubo decision que declarar.

Regla practica: si el valor cambia al mover la obra de sitio pero NO al
cambiar de proyectista, es [S] y va aqui.

Regla de uso
------------
    import datos_sitio as ds

    PGA = ds.valor("PGA_roca_B")     # registra el uso automaticamente
    print(ds.reporte_datos_sitio())  # M11 lo imprime en la Seccion 3

Un dato con valor None lanza `CriterioPendienteError` (modelos.py) y detiene
el calculo, igual que un criterio pendiente: un dato de sitio que todavia no
se ha leido tampoco se sustituye por un default.
"""

import math
import numbers
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from modelos import (CriterioPendienteError, DeCatalogo, DeEnsayo, Derivada,
                     Libre, ModoDeResolucion, Resolucion, modo_de)


ETIQUETA_SITIO = "S"

# El corredor de ESTE expediente. Es un dato del proyecto -- cambia al mover
# la obra y no al cambiar de proyectista --, no una constante del programa, y
# por eso se declara aqui, en el archivo de los [S], y no incrustado en la
# frase que define la etiqueta. Escrito como literal dentro de
# `AMBITO_CORREDOR`, aplicar la app a otra carretera heredaba "~5 km" en
# silencio en la memoria de la obra nueva (NOR-F-01).
#
# Su entrada completa, con procedimiento y trazabilidad, es
# DATOS_SITIO["corredor_del_proyecto"]; aqui esta el texto porque el valor por
# defecto del campo `ambito` se necesita al DEFINIR la dataclass, antes de que
# el diccionario exista. Una sola escritura, dos usos.
CORREDOR_DEL_PROYECTO = ("terraplen de ~5 km de la Fase 0-bis de la hoja de "
                         "ruta, num. 150")

# Ambito del dato. Hoy solo existe uno: lo que varia punto a punto no vive
# aqui, vive en el CSV. Se declara igualmente en cada entrada porque es la
# mitad de la trazabilidad que la etiqueta [S] exige ("si el dato aplica a
# todo el corredor o varia punto a punto"), y porque el dia que una lectura
# deje de valer para todo el tramo, la fila tiene que decirlo antes de
# mudarse al CSV.
AMBITO_CORREDOR = f"todo el corredor ({CORREDOR_DEL_PROYECTO})"


@dataclass(frozen=True)
class DatoSitio:
    """
    Un hecho del sitio con su procedimiento y su trazabilidad.

    `trazabilidad` ocupa el lugar que en un criterio [A] ocupa `sensibilidad`,
    y no por simetria estetica: un [A] se defiende mostrando cuanto cambiaria
    el resultado si se hubiera elegido el otro extremo del rango, y un [S] no
    se defiende asi -- no hay rango que elegir, hay una lectura que reproducir.
    Se defiende diciendo donde se leyo, para que el revisor la repita.
    """
    valor: Any
    concepto: str                              # que es
    procedimiento: str                         # como se obtuvo el valor
    fuente: str                                # de donde sale el procedimiento
    trazabilidad: str                          # como reproducir la lectura
    ambito: str = AMBITO_CORREDOR              # para que parte del proyecto vale
    etiqueta: str = ETIQUETA_SITIO
    reemplazado_por: Optional[str] = None      # ensayo/dato que lo sustituye
    verificacion_pendiente: Optional[str] = None   # lo que falta confirmar
    resolucion: Optional[Resolucion] = None    # COMO se resuelve (Sec. 4.3)

    # `resolucion` dice COMO SE LLEGA al valor, y para un dato de sitio la
    # respuesta casi siempre es la misma -- se determino con un procedimiento
    # -- pero no siempre: `Z_E030` no se lee de ningun mapa, se DERIVA de la
    # zona sismica entrando en la tabla del Art. 11.1. Sin el campo, la
    # ventana pintaria las dos cosas iguales y ofreceria editar un valor que
    # no se elige. El modo es el TIPO del objeto (`modelos.modo_de`), no un
    # texto: declarar la resolucion y declarar el modo son el mismo acto.

    def __post_init__(self) -> None:
        """
        LA GUARDIA QUE FALTABA (SIS-D-09).

        `criterios_adoptados._verificar_criterio` rechaza al importar un [S]
        sin trazabilidad; aqui `DatoSitio(trazabilidad="", etiqueta="A")` se
        construia sin una queja, de modo que la MISMA regla -- escrita con
        las mismas palabras en el encabezado de este archivo y en CLAUDE.md
        -- se hacia cumplir en un archivo y no en el otro. La asimetria no
        estaba declarada en ninguna parte: no era una decision, era un olvido.

        Va en `__post_init__` y no solo en un barrido al importar, y ahi esta
        la diferencia con el homologo: `criterios_adoptados` puede permitirse
        el barrido porque sus otros dos caminos de escritura
        (`establecer_valor_dinamico`, `escribir_valor_en_archivo`) pasan por
        la guardia a mano. Este archivo no tiene API de escritura, asi que el
        unico camino es CONSTRUIR un `DatoSitio` -- que es exactamente lo que
        el hallazgo hace --, y validar en el constructor lo cierra entero:
        el diccionario del archivo, un test, la GUI o cualquier cosa futura.
        """
        _verificar_dato(self)


# ---------------------------------------------------------------------------
# La guardia
# ---------------------------------------------------------------------------
# Vive AQUI ARRIBA, y no al final como su homologa de `criterios_adoptados`,
# porque `DatoSitio.__post_init__` la llama al construir cada entrada del
# diccionario: si se declarara despues, la primera entrada no la encontraria.

# Un dato de sitio se DETERMINA, no se elige y no se compra. `Libre` seria un
# dato de sitio que alguien decide -- y entonces es un criterio [A], no un [S]
# -- y `DeCatalogo` seria un hecho del terreno comprado a un proveedor.
_MODOS_DE_UN_DATO_DE_SITIO = (ModoDeResolucion.DE_ENSAYO,
                              ModoDeResolucion.DERIVADA,
                              ModoDeResolucion.DE_TABLA,
                              ModoDeResolucion.EN_RANGO)

_OBLIGATORIOS = ("concepto", "procedimiento", "fuente", "trazabilidad",
                 "ambito")


def _numeros_de(valor: Any):
    """
    Todos los numeros reales que hay DENTRO de un valor, sea escalar, tupla,
    lista o dict. Homologa de `criterios_adoptados._numeros_de`: la finitud no
    puede depender de la FORMA del valor.
    """
    if isinstance(valor, dict):
        for v in valor.values():
            yield from _numeros_de(v)
    elif isinstance(valor, (tuple, list, set, frozenset)):
        for v in valor:
            yield from _numeros_de(v)
    elif isinstance(valor, numbers.Real) and not isinstance(valor, bool):
        yield valor


def _verificar_finitud(nombre: str, d: "DatoSitio") -> None:
    """
    Ningun numero de un dato de sitio puede ser infinito ni NaN.

    Es la hermana que faltaba de `criterios_adoptados._verificar_finitud`, y
    la asimetria entre las dos guardias es lo que la delato: este archivo
    declara que `_verificar_dato` es "hermana de `_verificar_criterio`, y con
    el mismo caracter", y una de las dos comprobaba la finitud y la otra no.

    Aqui el argumento es ademas mas fuerte que en los criterios: un dato de
    sitio es una LECTURA -- un mapa, un ensayo, una medicion de campo -- y
    ninguna lectura devuelve un infinito. Un [S] no finito no es un valor
    extremo: es una transcripcion rota.
    """
    for x in _numeros_de(d.valor):
        try:
            finito = math.isfinite(float(x))
        except OverflowError:
            finito = False
        if not finito:
            raise ValueError(
                f"'{nombre}' declara {d.valor!r}, que contiene {x!r}. Un dato "
                "de sitio es una lectura: ningun mapa, ensayo ni medicion "
                "devuelve un infinito ni un NaN, y el calculo lo propagaria "
                "hasta la memoria sin detenerse en ningun sitio"
            )


def _verificar_dato(d: "DatoSitio") -> None:
    """
    Valida UN dato de sitio. Hermana de
    `criterios_adoptados._verificar_criterio`, y con el mismo caracter: es
    una guardia de ARQUITECTURA, no una validacion de dato de entrada. Si
    falla, el archivo esta mal escrito y ninguna corrida deberia empezar.
    """
    nombre = d.concepto.split(".")[0][:60] or "<dato sin concepto>"

    _verificar_finitud(nombre, d)

    if d.etiqueta != ETIQUETA_SITIO:
        raise ValueError(
            f"'{nombre}' esta en datos_sitio.py con la etiqueta "
            f"{d.etiqueta!r}. Este archivo es el de los [S] y solo el: un "
            "valor que el proyectista ELIGE es un criterio y va en "
            "criterios_adoptados.py, con su sensibilidad"
        )
    for campo in _OBLIGATORIOS:
        if not str(getattr(d, campo) or "").strip():
            raise ValueError(
                f"'{nombre}' no declara `{campo}`. Un dato de sitio se "
                "defiende diciendo como reproducir la lectura: sin "
                "procedimiento, fuente, trazabilidad y ambito no hay nada "
                "que reproducir"
            )
    if d.resolucion is None:
        raise ValueError(
            f"'{nombre}' no declara `resolucion`. Toda variable de entrada "
            "dice COMO se resuelve (Sec. 4.3): sin eso la GUI no sabe que "
            "ventana abrir"
        )
    # `modo_de` levanta TypeError si la resolucion no es de la familia.
    modo = modo_de(d.resolucion)
    if modo not in _MODOS_DE_UN_DATO_DE_SITIO:
        raise ValueError(
            f"'{nombre}' se resuelve `{modo.value}`, que no es una manera de "
            "llegar a un dato de sitio. Un [S] se determina (`de_ensayo`), "
            "se deriva de otro dato ya determinado (`derivada`) o se lee de "
            "una tabla; no se elige libremente ni sale de un catalogo"
        )
    if isinstance(d.resolucion, DeEnsayo) and \
            not d.resolucion.trazabilidad_exigida:
        raise ValueError(
            f"'{nombre}' se resuelve `de_ensayo` y no dice que trazabilidad "
            "hay que exigirle a la lectura"
        )
    if isinstance(d.resolucion, Derivada) and not d.resolucion.de:
        raise ValueError(
            f"'{nombre}' se resuelve `derivada` y no dice de que se deriva"
        )


_USADOS: Set[str] = set()


# ---------------------------------------------------------------------------
# Los datos de sitio de este expediente
# ---------------------------------------------------------------------------

DATOS_SITIO: Dict[str, DatoSitio] = {

    "PGA_roca_B": DatoSitio(
        valor=0.50,
        concepto="Aceleracion pico del terreno en roca Clase B, Tr = 1000 "
                 "anios, en g",
        procedimiento="Lectura del mapa de isoaceleraciones espectrales sobre "
                      "la ubicacion del proyecto. El mapa es normativo; el "
                      "numero que se lee en el depende de la coordenada, y por "
                      "eso el valor es [S] y no [N]: en otra provincia el MISMO "
                      "mapa da otro numero",
        fuente="Manual de Puentes MTC, Apendice A3, mapa 'Isoaceleraciones "
               "Espectrales Suelo Tipo B, AASHTO 2014 (Roca). Periodo "
               "estructural 0.0 seg (PGA)' - descartados los mapas de Ss y S1",
        trazabilidad="Lectura declarada para el distrito de La Union, Piura "
                     "(Sec. 0.4 de la hoja de ruta, num. 83). LA COORDENADA "
                     "EXACTA Y LA CURVA DE ISOACELERACION SOBRE LA QUE SE HIZO "
                     "LA LECTURA NO ESTAN REGISTRADAS todavia: es el pendiente "
                     "1.4 del tablero de la hoja de ruta, abierto. Mientras "
                     "siga abierto, la reproducibilidad de este dato llega "
                     "hasta el nombre del distrito y no hasta el punto del "
                     "mapa",
        ambito=AMBITO_CORREDOR,
        verificacion_pendiente="Registrar en la memoria las coordenadas o la "
                               "curva de isoaceleracion de la lectura "
                               "(pendiente 1.4). Al registrarlas, comprobar "
                               "sobre el mapa si la curva cambia dentro de los "
                               "~5 km del corredor: si cambiara, este dato "
                               "deja de ser unico para el tramo y pasa a ser "
                               "columna del CSV, como NF_profundidad_m",
        resolucion=DeEnsayo(
            ensayo="lectura del mapa de isoaceleraciones espectrales del "
                   "Apendice A3 del Manual de Puentes sobre la ubicacion del "
                   "proyecto (periodo estructural 0.0 s, suelo tipo B)",
            trazabilidad_exigida="la COORDENADA y la CURVA de isoaceleracion "
                                 "sobre las que se leyo. Hoy la lectura llega "
                                 "hasta el nombre del distrito y no hasta el "
                                 "punto del mapa: pendiente 1.4, abierto",
        ),
    ),

    # --------------------- E.030 - solo referencia -----------------------
    # Los dos datos que siguen NO gobiernan el diseno del cabezal, y el
    # argumento por el que no lo gobiernan CAMBIO. Se defendia solo por
    # periodo de retorno -- Sec. 0.4 de la hoja de ruta prefiere el PGA de
    # Tr = 1000 anios del Manual de Puentes al sismo de E.030 --, que es la
    # via discutible: invita a preguntar por que no aplicar las dos normas.
    # El argumento de AMBITO es anterior y cierra la pregunta, pero NO es el
    # que parecia. El Art. 4 acota E.030 a las edificaciones y un cabezal de
    # alcantarilla no lo es -- cierto --, solo que E.030 no guarda silencio
    # sobre lo que no es edificacion: su Art. 7.3 nombra puentes y
    # estructuras hidraulicas y se los ATRAE, "mientras no se cuente con
    # normas nacionales especificas". Lo que saca al cabezal de E.030, por
    # tanto, no es el silencio sino que esa condicion NO SE CUMPLE: el MTC si
    # tiene norma especifica, el Manual de Puentes. Es un fundamento positivo
    # y mas fuerte -- la propia E.030 cede el paso --, y el expediente no
    # invocaba ni uno ni otro (NOR-E030-03). Textos literales en
    # constantes_normativas.E030_AMBITO_TEXTO, E030_ART_7_3_TEXTO y
    # E030_AMBITO_LECTURA.
    #
    # Se conservan porque un revisor los va a buscar y porque su ausencia se
    # leeria como olvido, no como descarte deliberado. Vivian en
    # constantes_normativas.py como [N]; el cambio a [S] fue de
    # CLASIFICACION, no de uso: no los usaba ningun modulo antes y no los usa
    # ninguno ahora.

    "ZONA_SISMICA_LA_UNION": DatoSitio(
        valor=4,
        concepto="Zona sismica de E.030 que corresponde a la ubicacion del "
                 "proyecto",
        procedimiento="Consulta del mapa/anexo de zonificacion sismica sobre "
                      "el distrito del proyecto. E.030 define las cuatro zonas "
                      "y su reparto por distrito; que a ESTE distrito le toque "
                      "la 4 es la lectura, no la norma",
        fuente="E.030 (RM 183-2026-VIVIENDA), Anexo II - zonificacion sismica "
               "por distritos",
        trazabilidad="Anexo II de E.030, entrada del distrito de La Union "
                     "(Piura), que es la ubicacion con la que la hoja de ruta "
                     "identifica el proyecto. El expediente no registra "
                     "coordenadas: la lectura es reproducible hasta el "
                     "distrito, que es la unidad con la que el Anexo II "
                     "reparte las zonas, y no mas fino. La hoja de ruta NO "
                     "transcribe esta consulta -- solo cita el Z que de ella "
                     "resulta (num. 87) -- asi que el numeral es de E.030 y no "
                     "esta verificado contra la fuente normativa unica del "
                     "proyecto",
        ambito=AMBITO_CORREDOR,
        verificacion_pendiente="Contrastar la entrada del Anexo II de E.030 "
                               "vigente para el distrito antes de citar este "
                               "valor en la memoria. No gobierna ningun "
                               "calculo (Sec. 0.4), por lo que no bloquea",
        resolucion=DeEnsayo(
            ensayo="consulta del Anexo II de E.030 -- zonificacion sismica "
                   "por distritos -- sobre el distrito del proyecto",
            trazabilidad_exigida="el distrito consultado y la edicion del "
                                 "Anexo II. El reparto es POR DISTRITO: la "
                                 "lectura no es reproducible mas fino, y "
                                 "declarar una coordenada fingiria precision",
        ),
    ),

    "Z_E030": DatoSitio(
        valor=0.45,
        concepto="Factor de zona Z de E.030, en g: la aceleracion maxima "
                 "horizontal en suelo rigido con una probabilidad de 10 % de "
                 "ser excedida en 50 anios, que es como la define el Art. "
                 "11.1. NO 'para Tr = 475 anios': eso es una derivacion",
        procedimiento="Entrada de la Tabla N 1 de factores de zona del Art. "
                      "11.1 de E.030 con la zona leida en "
                      "'ZONA_SISMICA_LA_UNION'. La tabla es normativa; la "
                      "fila que aplica la fija la ubicacion. EL PERIODO DE "
                      "RETORNO NO SE LEE, SE DERIVA: el Art. 11.1 escribe la "
                      "probabilidad y no la cifra, y Tr = -50/ln(0.90) = "
                      "474.6 ~ 475 anios es aritmetica del proyectista. Este "
                      "campo decia 'para Tr = 475 anios' como si fuera "
                      "concepto de la norma (NOR-E030-01). La cifra si "
                      "aparece literal en E.030, pero en otro sitio y con "
                      "otro proposito: el Anexo III, pag. impresa 67, sobre "
                      "el contenido minimo de los estudios de "
                      "microzonificacion sismica",
        fuente="E.030 (RM 183-2026-VIVIENDA), Art. 11.1 y Tabla N 1, pag. "
               "impresa 9 (PDF 9): 'Este factor representa la aceleracion "
               "maxima horizontal en suelo rigido con una probabilidad de 10% "
               "de ser excedida en 50 anios' (Zona 4 -> Z = 0.45). Texto "
               "literal en constantes_normativas.E030_Z_TEXTO; la derivacion "
               "del periodo de retorno, en E030_TR_DERIVACION",
        trazabilidad="Art. 11.1 de E.030 leido con la zona que el Anexo II da "
                     "al distrito de La Union (Piura), o sea el valor que "
                     "resulta de 'ZONA_SISMICA_LA_UNION' y hereda su misma "
                     "trazabilidad. Lo que si esta en la fuente normativa "
                     "unica del proyecto es el descarte: la hoja de ruta lo "
                     "nombra en num. 87 solo para decir que NO se usa en el "
                     "calculo. El descarte tiene DOS argumentos y el "
                     "expediente usaba solo el segundo: (1) AMBITO -- el "
                     "Art. 4 aplica la norma a edificaciones y este cabezal "
                     "no lo es, pero eso solo no basta, porque el Art. 7.3 "
                     "nombra los puentes y las estructuras hidraulicas y les "
                     "aplica Z y S 'mientras no se cuente con normas "
                     "nacionales especificas'; lo que cierra la pregunta es "
                     "que esa condicion no se cumple, porque el Manual de "
                     "Puentes existe y es la norma sectorial del MTC; "
                     "(2) periodo de retorno -- el de referencia de Z, "
                     "derivado en 475 anios, difiere del adoptado (Tr = 1000 "
                     "anios del Manual de Puentes, Sec. 0.4). El (1) es el "
                     "que cierra la pregunta (NOR-E030-03)",
        ambito=AMBITO_CORREDOR,
        # Hereda la trazabilidad de 'ZONA_SISMICA_LA_UNION' -- lo dice su
        # propio campo `trazabilidad` -- y con ella hereda lo que aquella
        # tiene ABIERTO. Sin este campo, `datos_con_verificacion_pendiente()`
        # devolvia la zona y no el factor que se lee CON la zona, de modo que
        # el JSON del expediente declaraba cerrada documentalmente una
        # lectura que depende de otra que no lo esta (SIS-D-06).
        verificacion_pendiente="Hereda la verificacion abierta de "
                               "'ZONA_SISMICA_LA_UNION': el valor sale de "
                               "entrar en la tabla del Art. 11.1 con la zona "
                               "que el Anexo II de E.030 da al distrito, y "
                               "esa entrada del Anexo II todavia no se "
                               "contrasto contra la norma vigente. No "
                               "gobierna ningun calculo (Sec. 0.4), por lo "
                               "que no bloquea",
        resolucion=Derivada(
            de=("ZONA_SISMICA_LA_UNION",),
            regla="entrada en la Tabla N 1 de factores de zona del Art. 11.1 "
                  "de E.030 con la zona leida. NO SE EDITA: cambiar el Z sin "
                  "cambiar la zona seria contradecir la tabla. Y el periodo "
                  "de retorno de referencia tampoco se lee: se DERIVA de la "
                  "probabilidad que el Art. 11.1 escribe, "
                  "Tr = -50/ln(0.90) = 474.6 ~ 475 años (NOR-E030-01)",
        ),
    ),

    "corredor_del_proyecto": DatoSitio(
        valor=CORREDOR_DEL_PROYECTO,
        concepto="Tramo de via al que se aplica este expediente, y por tanto "
                 "el ambito para el que valen los demas datos de sitio",
        procedimiento="Definicion del tramo en la Fase 0-bis de la hoja de "
                      "ruta (num. 150): el terraplen sobre el que se "
                      "distribuyen los puntos criticos del CSV",
        fuente="docs/hoja_de_ruta_alcantarillas_v8.md, Fase 0-bis, num. 150",
        trazabilidad="La longitud aproximada sale de la definicion del tramo "
                     "del expediente vial, no de una medicion propia de este "
                     "estudio. NO gobierna ningun calculo: se imprime como el "
                     "ambito de cada dato de sitio, que es lo que la etiqueta "
                     "[S] obliga a declarar ('si el dato aplica a todo el "
                     "corredor o varia punto a punto'). Al aplicar el "
                     "programa a otra via, esta entrada es la que cambia; "
                     "mientras estuvo escrita dentro de `AMBITO_CORREDOR` se "
                     "heredaba sin que nadie la revisara",
        reemplazado_por="Progresiva inicial y final del tramo, del expediente "
                        "vial, cuando el proyecto declare su cabecera de "
                        "obra en vez de una longitud aproximada",
        resolucion=DeEnsayo(
            ensayo="definicion del tramo en la Fase 0-bis de la hoja de ruta "
                   "(num. 150): el terraplen sobre el que se distribuyen los "
                   "puntos criticos del CSV",
            trazabilidad_exigida="la progresiva inicial y final del tramo, "
                                 "del expediente vial. Hoy hay una longitud "
                                 "aproximada y no una cabecera de obra, y esa "
                                 "es la lectura que falta cerrar",
        ),
    ),

    # ----------------------------------------------------------------------
    # Geometria de la via y del cabezal respecto del trafico
    # ----------------------------------------------------------------------
    # LOS TRES QUE SIGUEN SON [S] Y NO [A], y la distincion decide donde
    # viven: ninguno se ELIGE. La orientacion del cabezal respecto del
    # trafico se LEE del plano de planta, los carriles por sentido salen del
    # diseño geometrico de la via y el borde de calzada se mide sobre la
    # seccion transversal. Cambian al mover la obra de sitio y NO cambian al
    # cambiar de proyectista, que es la regla de CLAUDE.md para separar [S] de
    # [A]. Los tres valen para todo el corredor mientras el trazo sea uno.
    #
    # Los tres valen None y por tanto DETIENEN el calculo. Es lo que el
    # conflicto vinculante #4 del plan de correcciones ordena: "no hay
    # contradiccion sino un dato faltante". No se sube h_eq a 1.12 m ni se
    # deja en 0.60: se declara lo que falta.

    "orientacion_muro_respecto_al_trafico": DatoSitio(
        valor=None,
        concepto="Orientacion del trasdos del cabezal respecto de la "
                 "direccion del trafico, que es lo que decide CUAL de las dos "
                 "tablas de altura de suelo equivalente de AASHTO 3.11.6.4 "
                 "aplica al empuje de sobrecarga viva (LS)",
        procedimiento="Lectura del plano de planta: angulo entre el eje del "
                      "conducto y el eje de la via. Un cabezal cuyo trasdos "
                      "corre paralelo al eje de la via es 'paralelo al "
                      "trafico'; uno enfrentado al trafico, "
                      "'perpendicular'. Valores admisibles: "
                      "'perpendicular_al_trafico' o 'paralelo_al_trafico'",
        fuente="AASHTO LRFD 9a ed., Art. 3.11.6.4 'Live Load Surcharge (LS)', "
               "pag. impresa 3-151 (PDF 205), Tablas 3.11.6.4-1 y 3.11.6.4-2",
        trazabilidad=(
            "LO QUE HAY QUE SABER ANTES DE DECLARARLO, y no es una "
            "formalidad. AASHTO NO ofrece un eje libre 'orientacion': ofrece "
            "dos BINOMIOS ACOPLADOS. La Tabla 3.11.6.4-1 es de ESTRIBOS "
            "perpendiculares al trafico -- su variable de entrada se llama "
            "literalmente 'Abutment Height (ft)' -- y la 3.11.6.4-2 de MUROS "
            "DE CONTENCION paralelos al trafico. NO HAY TABLA para 'muro "
            "perpendicular' ni para 'estribo paralelo'. "
            "De modo que declarar 'perpendicular_al_trafico' para un cabezal "
            "de alcantarilla obliga a leer la tabla de estribos, y eso es una "
            "ANALOGIA declarada [N->], no una lectura directa: el propio "
            "comentario C3.11.6.4 dice que h_eq es MAYOR para un estribo que "
            "para un muro, de modo que la analogia va del lado conservador y "
            "hay que decirlo. "
            "Y una segunda cosa que la fuente no resuelve: NO EXISTE en el "
            "articulado ninguna frase que reparta las dos tablas. El cuerpo "
            "normativo las cita juntas y sin condicionante; quien las reparte "
            "son los TITULOS de las tablas y el comentario, que no es "
            "articulado. Verificado barriendo las 1905 paginas del PDF. "
            "AMBITO: vale para todo el corredor mientras el trazo sea uno. Si "
            "algun cruce tuviera esviaje distinto del resto, este dato deja de "
            "ser unico para el tramo y pasa a columna del CSV"),
        ambito=AMBITO_CORREDOR,
        verificacion_pendiente=(
            "Declarar la orientacion sobre el plano de planta del expediente. "
            "Mientras siga en None, `M9.h_eq_sobrecarga_trasdos` se detiene y "
            "el empuje de sobrecarga viva del cabezal no se calcula"),
        resolucion=DeEnsayo(
            ensayo="lectura del plano de planta: angulo entre el eje del "
                   "conducto y el eje de la via",
            trazabilidad_exigida="la lamina y la progresiva de la lectura. Y "
                                 "el aviso de que la orientacion NO es un eje "
                                 "libre: elegir 'perpendicular' obliga a leer "
                                 "la tabla de ESTRIBOS, lo que es una "
                                 "analogia declarada [N->] y no una lectura "
                                 "directa (C3.11.6.4)",
        ),
    ),

    "distancia_borde_calzada_al_trasdos_m": DatoSitio(
        valor=None,
        concepto="Distancia horizontal del trasdos del muro al borde de la "
                 "calzada, en m. Solo la pide la Tabla 3.11.6.4-2, es decir "
                 "el caso de muro PARALELO al trafico",
        procedimiento="Medicion sobre la seccion transversal del expediente "
                      "vial, del paramento interior del cabezal al borde de "
                      "la calzada",
        fuente="AASHTO LRFD 9a ed., Tabla 3.11.6.4-2, encabezado de columna "
               "'heq (ft) Distance from wall backface to edge of traffic', "
               "pag. impresa 3-151 (PDF 205)",
        trazabilidad=(
            "EL UMBRAL DE LA FUENTE ES 1.0 ft = 0.3048 m EXACTOS, no 0.30 m. "
            "La tabla rotula su segunda columna 'ft or Further' sobre 1.0 ft, "
            "y 1 in = 25.4 mm es exacto. Redondear a 0.30 RELAJA el criterio: "
            "un trasdos con el borde de calzada a 0.30 m justos NO alcanza el "
            "umbral y le corresponde la columna de 0.0 ft, que da h_eq mayor. "
            "La banda 0.0 < d < 1.0 ft es una LAGUNA de la fuente: manda "
            "interpolar 'for intermediate wall HEIGHTS' -- entre filas -- y no "
            "autoriza interpolar entre estas dos columnas. El proyecto lee la "
            "columna de 0.0 ft para toda distancia menor, que es el lado "
            "conservador, y lo declara"),
        ambito=AMBITO_CORREDOR,
        verificacion_pendiente=(
            "Solo hace falta si la orientacion resulta 'paralelo_al_trafico'. "
            "Con 'perpendicular_al_trafico' la Tabla 3.11.6.4-1 no tiene "
            "columna de distancia y este dato no se invoca"),
        resolucion=DeEnsayo(
            ensayo="medicion sobre la seccion transversal del expediente "
                   "vial, del paramento interior del cabezal al borde de la "
                   "calzada",
            trazabilidad_exigida="la lamina y la progresiva de la seccion "
                                 "medida. El umbral de la fuente es 1.0 ft = "
                                 "0.3048 m EXACTOS, no 0.30 m: la medicion se "
                                 "compara contra ese numero",
        ),
    ),

    "carriles_por_sentido": DatoSitio(
        valor=None,
        concepto="Numero de carriles por sentido de la calzada, que es lo que "
                 "el Cuadro 4.1 del Manual de Suelos usa para fijar el numero "
                 "minimo de calicatas en autopistas y en carreteras duales o "
                 "multicarril",
        procedimiento="Lectura del diseño geometrico de la via (seccion "
                      "transversal tipo). Valores tabulados por el Cuadro "
                      "4.1: 2, 3 o 4 carriles por sentido",
        fuente="Manual de Carreteras: Suelos, Geologia, Geotecnia y "
               "Pavimentos, num. 4.2 'Caracterizacion de la sub rasante', "
               "Cuadro 4.1 'Numero de Calicatas para Exploracion de Suelos', "
               "pag. impresa 28 (PDF 29)",
        trazabilidad=(
            "EXISTE PORQUE EL REPOSITORIO AFIRMABA QUE LA NORMA NO LO PEDIA "
            "(NOR-SUE-01, MAT-D11). El comentario de `CALICATAS_POR_SENTIDO` "
            "decia que el Cuadro da el 6 'como alternativa sin decir cuando "
            "aplica cada una'. Verificado contra el PDF: el Cuadro lo "
            "condiciona por carriles por sentido, con tres viñetas explicitas "
            "-- 2 carriles/sentido: 4 calicatas x km x sentido; 3: 4; 4: 6 -- "
            "y la cadena '4 (o 6)' que el repositorio le atribuia no aparece "
            "en ninguna celda. De modo que el 6 SI es [N] y lo que faltaba no "
            "era un criterio del proyectista sino este dato. "
            "El dato lo fija el diseño geometrico, que a su vez depende del "
            "IMDA del estudio de demanda: mientras la clase de via no este "
            "cerrada, este dato tampoco. "
            "SOLO SE INVOCA en las dos filas multicarril del Cuadro; en las "
            "cuatro clases de una calzada el Cuadro da un escalar y no hace "
            "falta"),
        ambito=AMBITO_CORREDOR,
        verificacion_pendiente=(
            "Declararlo al cerrar la clase de via. El Cuadro tabula 2, 3 y 4 "
            "carriles por sentido y NO dice que hacer con 5 o mas: esa es una "
            "laguna de la fuente, declarada en el registro"),
        resolucion=DeEnsayo(
            ensayo="lectura del diseño geometrico de la via (seccion "
                   "transversal tipo)",
            trazabilidad_exigida="la lamina de la seccion tipo y la clase de "
                                 "via del estudio de demanda (IMDA) de la que "
                                 "esa seccion sale: mientras la clase de via "
                                 "no este cerrada, este dato tampoco",
        ),
    ),
}


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def valor(clave: str) -> Any:
    """
    Devuelve el dato de sitio y registra la invocacion.

    Un dato sin leer todavia (valor None) lanza `CriterioPendienteError`: la
    misma regla que en `criterios_adoptados.valor`, porque el error que se
    evita es el mismo -- rellenar en silencio lo que nadie ha determinado.
    """
    dato_ = dato(clave)
    _USADOS.add(clave)
    if dato_.valor is None:
        raise CriterioPendienteError(
            clave, concepto=dato_.concepto,
            fuente=f"dato de sitio [S] todavia sin leer - {dato_.fuente}",
        )
    return dato_.valor


def dato(clave: str) -> DatoSitio:
    """El registro completo, sin registrar uso ni exigir valor."""
    if clave not in DATOS_SITIO:
        raise KeyError(
            f"'{clave}' no esta declarado en datos_sitio.py. Ningun dato de "
            "sitio puede usarse sin declararse aqui con su trazabilidad."
        )
    return DATOS_SITIO[clave]


def datos_usados() -> List[str]:
    """Las claves que el calculo invoco, ordenadas."""
    return sorted(_USADOS)


def datos_sin_valor() -> List[str]:
    """Los datos declarados pero todavia sin leer. Detienen el calculo."""
    return sorted(k for k, d in DATOS_SITIO.items() if d.valor is None)


def datos_con_verificacion_pendiente() -> List[str]:
    """Los que tienen valor pero una verificacion documental abierta."""
    return sorted(k for k, d in DATOS_SITIO.items() if d.verificacion_pendiente)


def reporte_datos_sitio(solo_usados: bool = True) -> str:
    """
    Bloque de declaracion de datos de sitio para el reporte final, hermano de
    `criterios_adoptados.reporte_criterios`.

    Con solo_usados=True lista unicamente los datos que el calculo invoco: la
    memoria declara lo que sostiene sus numeros, no el catalogo completo.
    """
    claves = sorted(_USADOS if solo_usados else set(DATOS_SITIO))
    if not claves:
        return "No se invoco ningun dato de sitio."

    out = ["=" * 78,
           "DECLARACION DE DATOS DE SITIO [S]",
           "=" * 78, ""]

    for k in claves:
        d = DATOS_SITIO[k]
        out.append(f"[{d.etiqueta}] {k} = {d.valor!r}")
        out.append(f"     Concepto      : {d.concepto}")
        out.append(f"     Procedimiento : {d.procedimiento}")
        out.append(f"     Fuente        : {d.fuente}")
        out.append(f"     Trazabilidad  : {d.trazabilidad}")
        out.append(f"     Ambito        : {d.ambito}")
        if d.reemplazado_por:
            out.append(f"     Se sustituye por: {d.reemplazado_por}")
        if d.verificacion_pendiente:
            out.append(f"     >> VERIFICAR  : {d.verificacion_pendiente}")
        out.append("")

    pendientes = [k for k in claves if DATOS_SITIO[k].verificacion_pendiente]
    if pendientes:
        out.append("-" * 78)
        out.append("ADVERTENCIA: los siguientes datos de sitio tienen la")
        out.append("trazabilidad incompleta y no deben citarse como cerrados:")
        for k in pendientes:
            out.append(f"  - {k}")
        out.append("-" * 78)

    sin_leer = datos_sin_valor()
    if sin_leer:
        out.append("")
        out.append("-" * 78)
        out.append("SIN LEER: detienen el calculo en cuanto se invocan")
        for k in sin_leer:
            out.append(f"  - {k}: {DATOS_SITIO[k].procedimiento}")
        out.append("-" * 78)

    return "\n".join(out)


def _coherencia_de_datos_sitio() -> None:
    """
    Somete TODO el archivo a la guardia al importar, igual que
    `criterios_adoptados._coherencia_de_etiquetas()`.

    Es redundante con `__post_init__` -- que ya valido cada entrada al
    construirla -- y se conserva por dos razones: deja la simetria a la vista
    de quien compare los dos archivos, y da el mensaje CON LA CLAVE del
    diccionario, que `__post_init__` no puede conocer porque a esa altura la
    entrada todavia no tiene nombre.
    """
    for clave, d in DATOS_SITIO.items():
        try:
            _verificar_dato(d)
        except ValueError as e:
            raise ValueError(f"datos_sitio['{clave}']: {e}") from None


_coherencia_de_datos_sitio()


if __name__ == "__main__":
    valor("PGA_roca_B")
    print(reporte_datos_sitio(solo_usados=False))
