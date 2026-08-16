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
caudal lo fija el canal (ANA / Junta de Usuarios del Bajo Piura, Tablero 3.1),
dato que a la fecha no ha llegado. Se carga con esos campos en None y con la
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

# Columnas numericas, en el orden de Sec. 1.2.
_NUMERICAS: Tuple[str, ...] = (
    "Q_m3s", "area_ha", "S_cauce", "cota_terreno", "cota_rasante",
    "cota_subrasante", "cbr_subrasante", "esviaje_grados", "ancho_plataforma",
    "cota_fondo_receptor", "Q_receptor_m3s", "cota_TW",
)

# Vacios admitidos por tablero, no por comodidad.
_VACIAS_TODA_FAMILIA = ("Q_receptor_m3s", "cota_TW")        # Tablero 3.1
_VACIAS_FAMILIA_C = ("Q_m3s", "area_ha", "S_cauce")          # Tablero 3.1

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

    admiten_vacio = set(_VACIAS_TODA_FAMILIA)
    if familia is Familia.C:
        admiten_vacio.update(_VACIAS_FAMILIA_C)

    valores: Dict[str, Optional[float]] = {}
    pendientes: List[str] = []
    for columna in _NUMERICAS:
        bruto = _celda(fila, columna, id_punto, numero)
        if bruto == "":
            if columna in admiten_vacio:
                valores[columna] = None
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
    try:
        return float(bruto)
    except ValueError:
        raise DatoInvalidoError(
            columna, valor=bruto, id_punto=id_punto,
            motivo="no es un numero (el separador decimal es el punto)",
        ) from None


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

    # Sec. 1.5: la cota TW es el nivel del agua EN EL RECEPTOR durante la
    # avenida, no un nivel dentro de la alcantarilla. No puede estar bajo el
    # fondo del propio receptor.
    if v["cota_TW"] is not None:
        _exige(v["cota_TW"] - v["cota_fondo_receptor"] >= -TOL_UMBRAL_NORMATIVO,
               "cota_TW", v["cota_TW"], id_punto,
               f"el nivel de agua del receptor ({v['cota_TW']}) no puede quedar "
               f"bajo su propio fondo ({v['cota_fondo_receptor']})")
