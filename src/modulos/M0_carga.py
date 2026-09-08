"""
M0_carga.py
===========
Carga y validacion del CSV de entrada. Fase 1 de la hoja de ruta: encabezado
de Sec. 1.2, significado y unidad de cada dato en Sec. 1.1, y validaciones
cruzadas guiadas por la tabla de "datos que se confunden" de Sec. 1.5.

Que valida M0 y que no
----------------------
M0 valida ESTRUCTURA: que esten las columnas de Sec. 1.2, que cada valor sea
del tipo que dice ser, que caiga dentro del rango fisicamente posible y que no
contradiga a otro dato de su propia fila.

M0 NO valida COMPLETITUD de lo que depende de terceros. Una fila de Familia C
sin Q_m3s, sin area_ha y sin S_cauce no es una fila invalida: es una fila cuyo
caudal Y CUYA PENDIENTE los fija el canal (ANA / Junta de Usuarios del Bajo
Piura, Tablero 3.1), datos que a la fecha no han llegado. Eran «el caudal» y
«el dato», en singular, hasta que C6 midio que la pendiente del canal tambien
hace falta -- V2b la compara contra la del barril -- y que sale del mismo
tablero. Se carga con esos campos en None y con la
columna anotada en `pendientes_externos`. Lo mismo vale para cota_TW y
Q_receptor_m3s, que estan bloqueadas para TODAS las familias por el mismo
tablero. Rechazar esas filas aqui equivaldria a decidir en el modulo de lectura
algo que corresponde decidir mas adelante, cuando se sepa si el dato hace falta.

Excepciones
-----------
    DatoFaltanteError   falta una columna de Sec. 1.2, o una celda obligatoria
                        vacia. Lleva siempre el nombre de la columna.
    DatoInvalidoError   la celda esta pero no puede ser: no es numero, cae
                        fuera del rango fisico, o contradice a otro dato de la
                        fila (Sec. 1.5).
    FileNotFoundError   no hay archivo. Es un problema de E/S, no del
                        expediente, y por eso no entra en ErrorProyecto.

Uso
---
    from modulos.M0_carga import cargar_puntos

    puntos = cargar_puntos("tests/ejemplo_puntos.csv")
    pendientes = [p for p in puntos if p.pendiente_dato_externo]
"""

from __future__ import annotations

import csv
import math
from dataclasses import fields
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dominios import (CBR_MAX_FISICO, ESVIAJE_MAX, METROS_POR_KM, S_CAUCE_MAX)
from modelos import (DatoFaltanteError, DatoInvalidoError, Familia,
                     PuntoCritico)
from tolerancias import TOL_UMBRAL_NORMATIVO


# ---------------------------------------------------------------------------
# Encabezado de Sec. 1.2
# ---------------------------------------------------------------------------
# Se deriva de PuntoCritico en vez de reescribirse, para que columna y campo no
# puedan divergir. Los campos derivados no son columnas: M0 los construye.

CAMPOS_DERIVADOS = ("progresiva_display", "pendientes_externos")

COLUMNAS: Tuple[str, ...] = tuple(
    f.name for f in fields(PuntoCritico) if f.name not in CAMPOS_DERIVADOS
)

# Columnas numericas, en el orden de Sec. 1.2. Las TRES ultimas no vienen de
# ese encabezado y cierran la lista por eso: `NF_profundidad_m` se agrego al
# reclasificar el nivel freatico como dato de sitio [S] medido en cada cruce,
# `cota_fondo_entrada` al abrir la via del invert MEDIDO, y
# `cota_coronacion_canal` al implementar VC1 (ver `PuntoCritico`).
# El orden importa y esta fijado por test: tiene que ser el de los campos del
# tipo, y un campo con valor por defecto solo puede ir al final.
_NUMERICAS: Tuple[str, ...] = (
    "Q_m3s", "area_ha", "S_cauce", "cota_terreno", "cota_rasante",
    "cota_subrasante", "cbr_subrasante", "esviaje_grados", "ancho_plataforma",
    "cota_fondo_receptor", "Q_receptor_m3s", "cota_TW",
    "NF_profundidad_m", "cota_fondo_entrada", "cota_coronacion_canal",
)

# Vacios admitidos por tablero, no por comodidad.
_VACIAS_TODA_FAMILIA = ("Q_receptor_m3s", "cota_TW")        # Tablero 3.1

# REVISADA COLUMNA POR COLUMNA EN C6, y no ha cambiado. La lista se escribio
# cuando la Familia C NO se dimensionaba -- M2 no le ofrecia candidato -- y
# desde C5 si lo hace, de modo que habia que volver a mirarla con el criterio
# correcto: NO es si el bloqueo incomoda, es si el dato es EXIGIBLE a quien
# escribe el CSV. Las tres siguen sin serlo, y la razon es la misma para las
# tres: la Sec. 2.3 de la hoja de ruta dice de esta familia «Bloqueada por
# falta del dato de ANA -- ver Tablero 3», y el Tablero 3.1 cubre «la Familia
# C completa». Quien llena el CSV es el proyectista vial, no la Junta.
#
#   Q_m3s     el caudal de un cruce de canal NO es el hidrologico de la
#             cuenca: es el de diseno del canal (Sec. 2.3). Poner el de la
#             cuenca seria dimensionar con el caudal equivocado. Sin el se
#             detiene `MD.disenar_punto`, que lo exige antes de pedir
#             candidatos. Vehiculo: clave `Q_m3s` de `cli.CLAVES_EXTERNAS`.
#   area_ha   Sec. 1.1 la llama «solo clasificador» y su unico lector es
#             `M1._categoria_por_area`, que sirve a la Familia A para elegir
#             fila de la Tabla N 02. La Familia C no tiene TR --su caudal no
#             es hidrologico-- y por tanto NUNCA llega a ese lector: medido,
#             `PERFILES[Familia.C].categoria_tr` es None. No se detiene nada
#             sin ella, y por eso tampoco tiene vehiculo: darselo seria
#             pedir un dato para no usarlo.
#   S_cauce   la pendiente del canal la da el mismo tablero. SI se detiene
#             algo sin ella, y desde C5: `M5.v2b_sedimentacion` compara la
#             pendiente del barril contra la del cauce (indicador del num.
#             5.3.3 del HDS-5) y el material entero queda no evaluable. Lo
#             que C6 corrigio NO fue la lista sino la AUSENCIA DE VEHICULO:
#             la columna podia ir vacia y no habia por donde entregarla
#             cuando el tablero la diera. Hoy la clave `S_cauce` existe y
#             `PERFILES[Familia.C].campos_requeridos` la reclama.
_VACIAS_FAMILIA_C = ("Q_m3s", "area_ha", "S_cauce")          # Tablero 3.1

# Vacio admitido por el estudio geotecnico, que es otro tablero y no el 3.1: el
# NF de cada cruce lo da ese estudio. Mientras no llegue, la fila se carga
# marcada y quien se detiene es la verificacion que necesite el dato (V7 de
# flotacion, subpresion del cabezal), no la carga del CSV. Rellenarlo con el
# 1.4 m de la caracterizacion general de la llanura seria inventar una
# medicion por punto que nadie hizo.
_VACIAS_ESTUDIO_GEOTECNICO = ("NF_profundidad_m",)

# Vacio admitido por el LEVANTAMIENTO DE LOS CRUCES, que es un tercer tablero:
# el topografico. Mismo mecanismo que el geotecnico y por la misma razon --- la
# fila se carga marcada y quien se detiene es la verificacion que necesite el
# dato, no la carga --- y por eso la columna no lleva grupo propio de
# comportamiento sino de PROCEDENCIA: quien la debe es otro.
#
#   cota_coronacion_canal   cota del labio del canal en el cruce, del
#                           levantamiento propio de los seis cruces del
#                           corredor. Sin ella VC1 se detiene, y no hay regla
#                           que la sustituya: ninguna columna existente la
#                           implica --- ni el terreno natural ni la rasante son
#                           el labio del canal --- de modo que rellenarla seria
#                           inventar una medicion.
#
# ESTA EVALUADO, NO ASUMIDO, QUE AQUI NO VALE LA EXCLUSION DE
# `_VACIAS_CON_REGLA_DECLARADA`. La razon por la que `cota_fondo_entrada` no se
# marca como pendiente es que el proyecto TIENE una regla declarada para su
# ausencia, de modo que la celda vacia no espera a nadie. `cota_coronacion_canal`
# no tiene ninguna: vacia, espera al levantamiento. Marcarla es exacto y no
# marcarla pintaria una fila completa que no lo esta.
_VACIAS_LEVANTAMIENTO_DEL_CRUCE = ("cota_coronacion_canal",)

# Vacio admitido EN TODA FAMILIA, y por una razon distinta de las de arriba: no
# es que el dato dependa de un tablero que todavia no respondio, es que el
# proyecto TIENE una regla declarada para cuando no esta.
#
#   cota_fondo_entrada   nivelacion del fondo del cauce -- del CANAL, en un
#                        paso de canal -- en el cruce. Cuando viene, MANDA: un
#                        dato medido no se sustituye por una regla adoptada, y
#                        eso lo dice el `reemplazado_por` del propio criterio
#                        'origen_cota_fondo_entrada'. Cuando falta, rige ese
#                        criterio, y si el criterio tampoco esta declarado la
#                        etapa se detiene como se detenia antes: NO hay valor
#                        por defecto en ninguno de los dos escalones.
#
# La columna SI tiene que estar en el encabezado aunque la celda vaya vacia,
# igual que 'cota_TW' o 'NF_profundidad_m': un encabezado sin ella es una fila
# truncada, y `_celda` la rechaza como tal.
_VACIAS_CON_REGLA_DECLARADA = ("cota_fondo_entrada",)

_SOBRANTES = "__sobrantes__"       # restkey de csv.DictReader


# Los limites de dominio del dato de entrada (CBR_MAX_FISICO, ESVIAJE_MAX,
# S_CAUCE_MAX, METROS_POR_KM) viven en dominios.py con su justificacion. M0 los
# usa, no los declara.


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def cargar_puntos(ruta: Any) -> List[PuntoCritico]:
    """
    Lee el CSV de puntos criticos y devuelve la lista de PuntoCritico.

    Sec. 1.1 (significado y unidad de cada dato), Sec. 1.2 (encabezado) y
    Sec. 1.5 (validaciones cruzadas).
    """
    ruta = Path(ruta)
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo, restkey=_SOBRANTES, restval=None)
        if not lector.fieldnames:
            raise DatoFaltanteError(
                COLUMNAS[0],
                detalle=f"'{ruta.name}' esta vacio: no tiene ni encabezado "
                        f"(se esperan las {len(COLUMNAS)} columnas de Sec. 1.2)",
            )
        _valida_encabezado(lector.fieldnames, ruta)
        # La fila 1 es el encabezado: la primera fila de datos es la 2.
        puntos = [_punto_desde_fila(fila, numero)
                  for numero, fila in enumerate(lector, start=2)]

    if not puntos:
        raise DatoFaltanteError(
            "id",
            detalle=f"'{ruta.name}' trae el encabezado pero ninguna fila de datos",
        )
    _valida_ids_unicos(puntos)
    return puntos


# ---------------------------------------------------------------------------
# Estructura
# ---------------------------------------------------------------------------

def _valida_encabezado(encabezado: List[str], ruta: Path) -> None:
    """Todas las columnas de Sec. 1.2 tienen que estar. El orden no importa."""
    vistas = [c.strip() for c in encabezado if c]
    faltan = [c for c in COLUMNAS if c not in vistas]
    if not faltan:
        return

    detalle = (f"El encabezado de '{ruta.name}' no trae {len(faltan)} columna(s) "
               f"de Sec. 1.2: {', '.join(faltan)}")
    sobran = [c for c in vistas if c not in COLUMNAS]
    if sobran:
        detalle += (f". Columnas no reconocidas: {', '.join(sobran)} "
                    "- revisa si alguna esta mal escrita")
    raise DatoFaltanteError(faltan[0], detalle=detalle)


def _valida_ids_unicos(puntos: List[PuntoCritico]) -> None:
    vistos: Dict[str, int] = {}
    for orden, punto in enumerate(puntos, start=2):
        if punto.id in vistos:
            raise DatoInvalidoError(
                "id", valor=punto.id, id_punto=punto.id,
                motivo=f"identificador repetido (filas {vistos[punto.id]} y {orden}); "
                       "la memoria de calculo se ordena por punto y no puede "
                       "tener dos con el mismo nombre",
            )
        vistos[punto.id] = orden


# ---------------------------------------------------------------------------
# Una fila
# ---------------------------------------------------------------------------

def _punto_desde_fila(fila: Dict[str, Any], numero: int) -> PuntoCritico:
    sobrantes = fila.pop(_SOBRANTES, None)
    id_punto = _texto(fila, "id", f"(fila {numero})", numero)

    if sobrantes:
        raise DatoInvalidoError(
            "(fila completa)", valor=sobrantes, id_punto=id_punto,
            motivo=f"la fila {numero} trae mas celdas que columnas el "
                   "encabezado; suele ser una coma sin comillas dentro de un texto",
        )

    progresiva_km, progresiva_display = _progresiva(fila, id_punto, numero)
    familia = _familia(fila, id_punto, numero)

    admiten_vacio = (set(_VACIAS_TODA_FAMILIA) | set(_VACIAS_ESTUDIO_GEOTECNICO)
                     | set(_VACIAS_CON_REGLA_DECLARADA)
                     | set(_VACIAS_LEVANTAMIENTO_DEL_CRUCE))
    if familia is Familia.C:
        admiten_vacio.update(_VACIAS_FAMILIA_C)

    valores: Dict[str, Optional[float]] = {}
    pendientes: List[str] = []
    for columna in _NUMERICAS:
        bruto = _celda(fila, columna, id_punto, numero)
        if bruto == "":
            if columna in admiten_vacio:
                valores[columna] = None
                # `pendientes_externos` significa «la fila espera un dato de
                # TERCEROS», y eso es lo que la GUI y el JSON leen de ella.
                # Una `cota_fondo_entrada` vacia NO espera a nadie: el
                # proyecto tiene una regla declarada para ese caso, y meterla
                # aqui pintaria un pendiente que no existe --- justo el tipo
                # de afirmacion falsa que este repositorio persigue.
                if columna not in _VACIAS_CON_REGLA_DECLARADA:
                    pendientes.append(columna)
                continue
            raise DatoFaltanteError(
                columna, id_punto=id_punto,
                detalle=f"la fila {numero} la deja vacia y no es de las que "
                        "dependen de un tablero externo",
            )
        valores[columna] = _a_float(bruto, columna, id_punto)

    _valida_rangos(valores, id_punto)
    _valida_cruzadas(valores, id_punto)

    return PuntoCritico(
        id=id_punto,
        progresiva_km=progresiva_km,
        progresiva_display=progresiva_display,
        familia=familia,
        sucs_fundacion=_texto(fila, "sucs_fundacion", id_punto, numero),
        pendientes_externos=tuple(pendientes),
        **valores,
    )


def _celda(fila: Dict[str, Any], columna: str, id_punto: str, numero: int) -> str:
    """
    Devuelve la celda ya recortada. None significa fila truncada: DictReader
    rellena con restval las columnas que la fila no alcanzo a traer.
    """
    bruto = fila.get(columna)
    if bruto is None:
        raise DatoFaltanteError(
            columna, id_punto=id_punto,
            detalle=f"la fila {numero} tiene menos celdas que el encabezado y "
                    "se corta antes de esta columna",
        )
    return bruto.strip()


def _texto(fila: Dict[str, Any], columna: str, id_punto: str, numero: int) -> str:
    valor = _celda(fila, columna, id_punto, numero)
    if not valor:
        raise DatoFaltanteError(
            columna, id_punto=id_punto, detalle=f"la fila {numero} la deja vacia")
    return valor


def _a_float(bruto: str, columna: str, id_punto: str) -> float:
    """
    La celda como float, EXIGIENDO QUE SEA FINITO (MAT-D14).

    `float()` acepta los literales 'inf', '-inf', 'Infinity' y 'nan', y
    ninguna validacion posterior los atrapa:

      * `inf` FUGABA de verdad, y no solo por las columnas con piso: medido
        sobre el codigo anterior, entraban `Q_m3s`, `area_ha`, `cota_rasante`,
        `ancho_plataforma`, `Q_receptor_m3s`, `cota_TW`, `NF_profundidad_m` y
        `cota_fondo_receptor` (esta ultima con `-inf`). `inf > 0` es cierto y
        ninguna de esas columnas tiene techo.
      * `nan` NO fugaba hoy, y conviene decirlo con precision en vez de
        exagerarlo: `_valida_rangos` esta escrita en forma positiva
        (`_exige(0 <= x < MAX)`) y `nan` es falso frente a `<=` y frente a
        `>=` a la vez, de modo que las FALLA todas -- las catorce columnas lo
        rechazan. Pero lo rechazan por casualidad de redaccion: basta con que
        una sola se reescriba como "no esta fuera"
        (`_exige(not (x < 0 or x > MAX))`) para que `nan` la atraviese. La
        finitud se exige AQUI, en la conversion, para que esa proteccion no
        dependa de como este redactado cada rango.

    Un dato asi no detiene el pipeline: lo recorre y sale por el otro extremo
    como una memoria con numeros que no son numeros -- un diagnostico falso,
    que es peor que un fallo. Es exactamente el caso que CLAUDE.md llama
    DatoInvalidoError: el dato ESTA pero no puede ser.

    `cli.py::_numero_externo` ya lo exigia para los datos externos. Esta era
    la mitad que faltaba, y la asimetria entre las dos puertas de entrada del
    mismo pipeline es lo que delato el hueco.
    """
    try:
        valor = float(bruto)
    except ValueError:
        raise DatoInvalidoError(
            columna, valor=bruto, id_punto=id_punto,
            motivo="no es un numero (el separador decimal es el punto)",
        ) from None
    if not math.isfinite(valor):
        raise DatoInvalidoError(
            columna, valor=bruto, id_punto=id_punto,
            motivo="no es un numero finito: 'inf' y 'nan' son literales que "
                   "float() acepta y que ninguna validacion de rango atrapa, "
                   "de modo que entrarian al calculo y saldrian como una "
                   "memoria con numeros que no lo son",
        )
    return valor


def _familia(fila: Dict[str, Any], id_punto: str, numero: int) -> Familia:
    """Familias A, B y C de Sec. 2.3."""
    bruto = _texto(fila, "familia", id_punto, numero).upper()
    try:
        return Familia(bruto)
    except ValueError:
        raise DatoInvalidoError(
            "familia", valor=bruto, id_punto=id_punto,
            motivo="las familias de Sec. 2.3 son "
                   f"{', '.join(f.value for f in Familia)}",
        ) from None


def _progresiva(fila: Dict[str, Any], id_punto: str, numero: int) -> Tuple[float, str]:
    """
    Devuelve (km numericos, notacion vial). Ambos salen del mismo string: la
    memoria y los planos se citan en progresivas ('0+380') y el orden de los
    puntos se resuelve con el numero (0.380 km).
    """
    bruto = _texto(fila, "progresiva_km", id_punto, numero)

    if "+" not in bruto:
        km = _a_float(bruto, "progresiva_km", id_punto)
        _exige(km >= 0, "progresiva_km", km, id_punto,
               "la progresiva no puede ser negativa")
        entero = int(km)
        metros = (km - entero) * METROS_POR_KM
        return km, f"{entero}+{metros:06.2f}"

    partes = bruto.split("+")
    if len(partes) != 2:
        raise DatoInvalidoError(
            "progresiva_km", valor=bruto, id_punto=id_punto,
            motivo="la notacion vial lleva un solo '+', como en '0+380'")

    kilometros = _a_float(partes[0], "progresiva_km", id_punto)
    metros = _a_float(partes[1], "progresiva_km", id_punto)
    _exige(kilometros >= 0, "progresiva_km", bruto, id_punto,
           "la progresiva no puede ser negativa")
    _exige(0 <= metros < METROS_POR_KM, "progresiva_km", bruto, id_punto,
           f"los metros de la progresiva van de 0 a {METROS_POR_KM}: pasado "
           "ese punto sube el kilometro")
    return kilometros + metros / METROS_POR_KM, bruto


# ---------------------------------------------------------------------------
# Rangos y validaciones cruzadas (Sec. 1.5)
# ---------------------------------------------------------------------------

def _exige(condicion: bool, columna: str, valor: Any, id_punto: str,
           motivo: str) -> None:
    if not condicion:
        raise DatoInvalidoError(columna, valor=valor, id_punto=id_punto,
                                motivo=motivo)


def _valida_rangos(v: Dict[str, Optional[float]], id_punto: str) -> None:
    """Rango fisicamente posible de cada columna, una por una."""
    if v["Q_m3s"] is not None:
        _exige(v["Q_m3s"] > 0, "Q_m3s", v["Q_m3s"], id_punto,
               "el caudal de diseno es positivo")
    if v["area_ha"] is not None:
        _exige(v["area_ha"] > 0, "area_ha", v["area_ha"], id_punto,
               "el area de cuenca es positiva")
    if v["S_cauce"] is not None:
        _exige(0 < v["S_cauce"] < S_CAUCE_MAX, "S_cauce", v["S_cauce"], id_punto,
               "la pendiente del cauce va en m/m y es mayor que 0 y menor que "
               f"{S_CAUCE_MAX}; si venia en porcentaje, divide entre cien")
    if v["Q_receptor_m3s"] is not None:
        _exige(v["Q_receptor_m3s"] > 0, "Q_receptor_m3s", v["Q_receptor_m3s"],
               id_punto, "el caudal de diseno del receptor es positivo")

    # El CBR de la subrasante define el resguardo de V4 (Sec. 5.1). Su rango
    # fisico es el de una proporcion contra la piedra patron; que sea alto o
    # bajo no lo decide M0, lo decide la tabla de 5.1.
    cbr = v["cbr_subrasante"]
    _exige(cbr > 0, "cbr_subrasante", cbr, id_punto, "el CBR es positivo")
    _exige(cbr <= CBR_MAX_FISICO, "cbr_subrasante", cbr, id_punto,
           f"un CBR de subrasante por encima de {CBR_MAX_FISICO} % no es un "
           "suelo: revisa si el valor esta en otra escala")

    _exige(0 <= v["esviaje_grados"] < ESVIAJE_MAX, "esviaje_grados",
           v["esviaje_grados"], id_punto,
           f"el esviaje va de 0 (cruce perpendicular) a {ESVIAJE_MAX} grados, "
           "donde el conducto seria paralelo a la via y no habria cruce")

    _exige(v["ancho_plataforma"] > 0, "ancho_plataforma", v["ancho_plataforma"],
           id_punto, "el ancho de plataforma es positivo")

    # El NF se mide como PROFUNDIDAD bajo el terreno natural: es positivo por
    # definicion. Un cero o un negativo significa agua sobre el terreno, que no
    # es un nivel freatico sino un cauce, y una celda con signo cambiado es el
    # error de transcripcion tipico de esta columna. No se le pone tope
    # superior: cuan profundo puede estar el freatico no lo decide este modulo
    # ni hay dato en el expediente para acotarlo.
    if v["NF_profundidad_m"] is not None:
        _exige(v["NF_profundidad_m"] > 0, "NF_profundidad_m",
               v["NF_profundidad_m"], id_punto,
               "el nivel freatico se mide como profundidad bajo el terreno "
               "natural y es positivo; si el agua aflora, el dato no es un NF")


def _valida_cruzadas(v: Dict[str, Optional[float]], id_punto: str) -> None:
    """
    Contradicciones entre datos de la misma fila. La guia es la tabla de
    Sec. 1.5: son justo los pares que se confunden al armar el CSV.
    """
    # Sec. 1.5: la rasante es la superficie de rodadura y la subrasante sale de
    # restarle el paquete estructural. Si van al reves o coinciden, estan
    # intercambiadas o el paquete quedo en cero.
    _exige(v["cota_rasante"] - v["cota_subrasante"] > TOL_UMBRAL_NORMATIVO,
           "cota_subrasante", v["cota_subrasante"], id_punto,
           f"la subrasante ({v['cota_subrasante']}) tiene que quedar bajo la "
           f"rasante ({v['cota_rasante']}): la separacion es el espesor del "
           "paquete estructural (Sec. 1.5)")

    # LAS DOS VALIDACIONES QUE NO SON FILA DE LA TABLA DE Sec. 1.5 (SIS-A-16).
    # Las dos que siguen -- altura libre terreno/subrasante positiva, y fondo
    # del receptor bajo el terreno del cruce -- NO aparecen en la hoja de
    # ruta, y conviene decir por que estan aqui en vez de dejarlo en dos
    # comentarios de linea:
    #
    #   * no son criterios de factibilidad inventados. Son comprobaciones de
    #     IMPOSIBILIDAD FISICA entre dos datos de la MISMA FILA, que es el
    #     tercer supuesto que CLAUDE.md autoriza expresamente para
    #     DatoInvalidoError ("contradice a otro dato de su misma fila");
    #   * y no invaden a M7 ni a 7.A. La frontera es la que fija
    #     `test_un_terraplen_bajo_pero_posible_lo_decide_M7_y_no_M0`: M0
    #     rechaza lo IMPOSIBLE (altura nula o negativa) y deja pasar lo
    #     POSIBLE PERO AJUSTADO, que es donde decide el tamizado con
    #     DisenoNoFactibleError y un delta de rasante.
    #
    # Diametro implicito: la altura libre entre el terreno natural y la
    # subrasante. Si no es positiva, no hay terraplen donde alojar conducto
    # alguno y el dato esta mal. Cuanto hace falta ademas para el diametro
    # elegido lo resuelve el tamizado de 7.A con DisenoNoFactibleError, no M0.
    altura = v["cota_subrasante"] - v["cota_terreno"]
    _exige(altura > TOL_UMBRAL_NORMATIVO, "cota_subrasante", v["cota_subrasante"],
           id_punto,
           f"el diametro implicito es nulo o negativo: entre el terreno "
           f"({v['cota_terreno']}) y la subrasante ({v['cota_subrasante']}) hay "
           f"{altura:+.2f} m y no cabe ningun conducto")

    # La alcantarilla entrega por gravedad: el fondo del receptor esta bajo el
    # terreno natural del cruce.
    _exige(v["cota_terreno"] - v["cota_fondo_receptor"] > TOL_UMBRAL_NORMATIVO,
           "cota_fondo_receptor", v["cota_fondo_receptor"], id_punto,
           f"el fondo del receptor ({v['cota_fondo_receptor']}) no puede estar "
           f"sobre el terreno del cruce ({v['cota_terreno']}): la entrega es "
           "por gravedad")

    # El invert MEDIDO, cuando viene, tiene que dejar sitio al conducto: si
    # queda a la subrasante o por encima, no cabe ninguno. Es la MISMA
    # comprobacion de imposibilidad fisica que la del "diametro implicito" de
    # arriba, aplicada a la cota que de verdad manda cuando esta.
    #
    # Y SOLO ESA. NO se exige que el invert quede bajo el terreno natural,
    # aunque en un paso de canal sea lo normal --- el fondo del canal esta
    # excavado respecto del terreno del cruce ---: una entrada ELEVADA sobre
    # relleno es fisicamente posible y la justificacion del propio criterio
    # 'origen_cota_fondo_entrada' la nombra. Rechazarla aqui seria convertir
    # una observacion de este corredor en una regla del programa.
    if v["cota_fondo_entrada"] is not None:
        libre = v["cota_subrasante"] - v["cota_fondo_entrada"]
        _exige(libre > TOL_UMBRAL_NORMATIVO, "cota_fondo_entrada",
               v["cota_fondo_entrada"], id_punto,
               f"el fondo de entrada medido ({v['cota_fondo_entrada']}) queda "
               f"a la subrasante ({v['cota_subrasante']}) o por encima: entre "
               f"los dos hay {libre:+.2f} m y no cabe ningun conducto")

    # La coronacion del canal esta SOBRE su propio fondo. Es la unica cruzada
    # que este dato admite, y solo cuando las dos cotas vienen medidas: si el
    # fondo lo pone la regla de 'origen_cota_fondo_entrada' en vez de la
    # nivelacion, lo que se compararia no son dos lecturas del mismo cruce.
    #
    # NO SE CRUZA CONTRA `cota_terreno` NI CONTRA `cota_rasante`, y es
    # deliberado por la misma razon que el invert no se exige bajo el terreno:
    # un canal excavado tiene la coronacion BAJO el terreno natural y uno con
    # bordos la tiene POR ENCIMA. Las dos formas existen, ninguna es un error
    # del expediente, y convertir la de este corredor en regla del programa
    # rechazaria filas correctas de otro.
    if (v["cota_coronacion_canal"] is not None
            and v["cota_fondo_entrada"] is not None):
        calado = v["cota_coronacion_canal"] - v["cota_fondo_entrada"]
        _exige(calado > TOL_UMBRAL_NORMATIVO, "cota_coronacion_canal",
               v["cota_coronacion_canal"], id_punto,
               f"la coronacion del canal ({v['cota_coronacion_canal']}) no "
               f"queda sobre su propio fondo ({v['cota_fondo_entrada']}): "
               f"entre los dos hay {calado:+.2f} m y el canal no tendria "
               "seccion")

    # Sec. 1.5: la cota TW es el nivel del agua EN EL RECEPTOR durante la
    # avenida, no un nivel dentro de la alcantarilla. No puede estar bajo el
    # fondo del propio receptor.
    if v["cota_TW"] is not None:
        _exige(v["cota_TW"] - v["cota_fondo_receptor"] >= -TOL_UMBRAL_NORMATIVO,
               "cota_TW", v["cota_TW"], id_punto,
               f"el nivel de agua del receptor ({v['cota_TW']}) no puede quedar "
               f"bajo su propio fondo ({v['cota_fondo_receptor']})")
