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

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from modelos import CriterioPendienteError


ETIQUETA_SITIO = "S"

# Ambito del dato. Hoy solo existe uno: lo que varia punto a punto no vive
# aqui, vive en el CSV. Se declara igualmente en cada entrada porque es la
# mitad de la trazabilidad que la etiqueta [S] exige ("si el dato aplica a
# todo el corredor o varia punto a punto"), y porque el dia que una lectura
# deje de valer para todo el tramo, la fila tiene que decirlo antes de
# mudarse al CSV.
AMBITO_CORREDOR = ("todo el corredor (el terraplen de ~5 km de la Fase 0-bis de la hoja de ruta, num. 150)")


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
    ),

    # --------------------- E.030 - solo referencia -----------------------
    # Los dos datos que siguen NO gobiernan el diseno del cabezal: Sec. 0.4
    # de la hoja de ruta descarta el sismo de 475 anios de E.030 en favor del
    # PGA de Tr = 1000 anios del Manual de Puentes. Se conservan porque un
    # revisor los va a buscar y porque su ausencia se leeria como olvido, no
    # como descarte deliberado. Vivian en constantes_normativas.py como [N];
    # el cambio a [S] es de CLASIFICACION, no de uso: no los usaba ningun
    # modulo antes y no los usa ninguno ahora.

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
    ),

    "Z_E030": DatoSitio(
        valor=0.45,
        concepto="Factor de zona Z de E.030 (aceleracion maxima en suelo "
                 "rigido para Tr = 475 anios), en g",
        procedimiento="Entrada de la tabla de factor de zona del Art. 11.1 de "
                      "E.030 con la zona leida en 'ZONA_SISMICA_LA_UNION'. La "
                      "tabla es normativa; la fila que aplica la fija la "
                      "ubicacion",
        fuente="E.030 (RM 183-2026-VIVIENDA), Art. 11.1, Tabla de factores de "
               "zona (Zona 4 -> Z = 0.45)",
        trazabilidad="Art. 11.1 de E.030 leido con la zona que el Anexo II da "
                     "al distrito de La Union (Piura), o sea el valor que "
                     "resulta de 'ZONA_SISMICA_LA_UNION' y hereda su misma "
                     "trazabilidad. Lo que si esta en la fuente normativa "
                     "unica del proyecto es el descarte: la hoja de ruta lo "
                     "nombra en num. 87 solo para decir que NO se usa en el "
                     "calculo, porque su periodo de retorno de referencia "
                     "(475 anios) difiere del adoptado (Tr = 1000 anios del "
                     "Manual de Puentes, Sec. 0.4), que es el que gobierna el "
                     "cabezal",
        ambito=AMBITO_CORREDOR,
    ),

    # --------------------- Nivel de estudio del proyecto -----------------
    # No es una eleccion del proyectista sino un hecho del encargo: la
    # campana geotecnica ejecutada es la del nivel perfil del Manual de
    # Suelos, y ese nivel es el que fundamenta las verificaciones diferidas
    # al expediente definitivo (docs/encargo_verificaciones_diferidas.md).

    "nivel_estudio": DatoSitio(
        valor="perfil",
        concepto="Nivel de profundidad del estudio (perfil / expediente "
                 "definitivo)",
        procedimiento="Declarado por el proyecto: la campana geotecnica "
                      "ejecutada es de 5 calicatas en 5 km, sin SPT, corte "
                      "directo ni ensayos quimicos completos",
        fuente="Manual de Suelos MTC, num. 4.2, Cuadro 4.1 -- el mismo "
               "numeral que ya cita ESPACIAMIENTO_PERFIL_KM en "
               "constantes_normativas.py",
        trazabilidad="La densidad de investigacion ejecutada corresponde a "
                     "la que el Cuadro 4.1 exige para el nivel perfil, no a "
                     "la de expediente definitivo",
        ambito=AMBITO_CORREDOR,
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


if __name__ == "__main__":
    valor("PGA_roca_B")
    print(reporte_datos_sitio(solo_usados=False))
