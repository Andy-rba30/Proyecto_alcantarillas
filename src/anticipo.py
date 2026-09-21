# -*- coding: utf-8 -*-
"""
anticipo.py
===========
EL CONTENIDO del panel «Anticipo antes de correr» de la pestana 1 (G3): lo
que se puede saber ANTES de ejecutar el pipeline, en tres bloques, todos
DERIVADOS.

Que es esto, y por que no esta en gui/
--------------------------------------
El mismo reparto que `ayuda_entrada.py` y `traza_punto.py`, y por las mismas
razones: `gui/` importa `tkinter`, que no esta en toda imagen donde corre la
suite, y lo que el panel AFIRMA tiene que poder compararse sin escritorio.
Aqui el contenido es un DATO; `gui/app.py` lo pinta y no sabe nada mas.

ES UNA ESTIMACION, Y ESA PALABRA NO ES OPCIONAL
-----------------------------------------------
El proyecto distingue estimaciones de medidas, y este panel esta del lado de
las estimaciones: la invocacion real de un criterio depende de la ruta que
tome cada punto, y la verdad post-corrida es el tablero de la pestana 4
(`M11.criterios_bloqueantes`, que se puebla DESPUES de ejecutar --- ese
diseño se conserva porque es la verdad medida). Por eso:

  * el aviso `AVISO_DEL_ANTICIPO` viaja con el panel y dice «estimacion»;
  * NADA de este modulo gobierna un filtro ni un boton: el boton de EJECUTAR
    no se entera de que el anticipo existe, porque correr siempre se puede
    --- el pipeline convierte cada falta en un `Bloqueo` declarado ---.

NINGUNA LISTA DE ESTE MODULO ESTA ESCRITA A MANO
------------------------------------------------
Todo sale de donde ya vive, que es la regla que S21/S22 dejaron asentada:

    criterios vacios alcanzables   ca.criterios_del_alcance (Criterio.nivel,
                                   contrastado por tests/test_nivel_medido.py)
                                   x ca.criterios_sin_valor (que ya excluye
                                   opcionales y declarados en caliente)
    columnas del CSV               M0_carga.COLUMNAS, M0_carga.VACIOS_ADMITIDOS
                                   y M0_carga.leer_cabecera --- SOLO cabecera y
                                   conteo de celdas vacias, sin ejecutar la
                                   carga completa ---
    lo que el alcance difiere      servicio.VERIFICACIONES_DIFERIDAS_POR_ALCANCE
                                   y servicio.MODULOS_DIFERIDOS_POR_ALCANCE,
                                   los dos consultados por la propia corrida
                                   (en `cli` hasta EXT-9)

Este modulo no hace aritmetica sobre magnitudes --- cuenta filas y celdas,
que es lo unico que un contraste de cabecera necesita --- y no toma ninguna
decision de diseño: elige textos y orden, igual que M11.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Any, Dict, List, Optional, Tuple

from src import criterios_adoptados as ca
from src import responsable as _responsable
from src import servicio
from src import variables_entrada as _ve
from src.modelos import Familia, VacioAdmitido
# Por el modulo y no por el valor, por la razon escrita en `ayuda_entrada.py`:
# un `from ... import COLUMNAS` copia la tupla y la deja leyendo una foto.
from src.modulos import M0_carga as m0

# La linea fija del panel (regla dura de G3). La palabra «estimacion» no es
# opcional: el proyecto distingue estimaciones de medidas y esta es una
# estimacion. Vive aqui --- y la GUI la lee --- para que el texto que la
# ventana muestra y el que los tests comprueban sean EL MISMO.
AVISO_DEL_ANTICIPO = ("Estimación derivada del alcance; la lista definitiva "
                      "la da la corrida (pestaña 4).")

# Lo que el bloque de columnas dice mientras no hay CSV legible. `None` es
# «no se sabe», no «esta mal»: el anticipo se refresca al teclear la ruta y
# la mitad de las veces el archivo aun no existe (misma decision, escrita,
# que `gui/app.py::_releer_familias`).
SIN_CSV = ("Sin CSV legible todavía: el contraste de columnas se hace al "
           "cargar uno.")


# ===========================================================================
# Bloque 1 - criterios vacios que el alcance elegido puede invocar
# ===========================================================================

@dataclass(frozen=True)
class CriterioVacio:
    """
    Una fila del bloque 1: clave y concepto, para pintar y navegar, y desde
    E-B (E13 reducido) QUIEN lo fija y CON QUE evidencia, derivados de la
    ficha por `src/responsable.py`: la misma pareja que `M11.CriterioBloqueante`
    lleva despues de correr. Con defecto vacio para que el tipo siga siendo
    construible por su par (clave, concepto).
    """

    clave: str
    concepto: str
    responsable: str = ""
    evidencia: str = ""


def criterios_vacios_alcanzables(alcance: str) -> Tuple[CriterioVacio, ...]:
    """
    Los criterios SIN VALOR, no opcionales y sin declaracion en caliente que
    una corrida de ese alcance PUEDE invocar.

    Es la INTERSECCION de dos respuestas que ya existen, no una tercera:
    `ca.criterios_del_alcance` dice que criterios puede necesitar el alcance
    (lee `Criterio.nivel`), y `ca.criterios_sin_valor` dice cuales siguen
    vacios (y ya deja fuera los opcionales --- que no bloquean nada --- y los
    declarados en caliente). Una regla propia aqui seria una segunda
    clasificacion capaz de contradecir a las dos.

    Sigue siendo una ESTIMACION: que un criterio alcanzable este vacio no
    garantiza que esta corrida lo invoque --- eso depende de la ruta de cada
    punto --- y la lista definitiva la da `M11.criterios_bloqueantes` despues
    de correr.
    """
    alcanzables = set(ca.criterios_del_alcance(alcance))
    salida = []
    for clave in ca.criterios_sin_valor():
        if clave not in alcanzables:
            continue
        criterio = ca.criterio(clave)
        quien = _responsable.responsabilidad_de(criterio)
        salida.append(CriterioVacio(clave=clave, concepto=criterio.concepto,
                                    responsable=quien.responsable,
                                    evidencia=quien.evidencia))
    return tuple(salida)


# ===========================================================================
# Bloque 2 - contraste de la cabecera del CSV, sin ejecutar el pipeline
# ===========================================================================

@dataclass(frozen=True)
class ColumnaConVacios:
    """
    Una columna del CSV cargado que trae celdas vacias.

    `grupos` son los `VacioAdmitido` de M0 que la cubren: vacio significa que
    NINGUN grupo la admite y la carga completa se detendria en esa fila con
    `DatoFaltanteError`.
    """

    columna: str
    vacias: int
    grupos: Tuple[VacioAdmitido, ...]

    @property
    def admite_vacio(self) -> bool:
        return bool(self.grupos)

    @property
    def familias_del_vacio(self) -> Tuple[Familia, ...]:
        """
        Las familias en las que el vacio se admite; las tres cuando algun
        grupo no declara familias (el significado de `VacioAdmitido.familias`
        vacio, igual que en `ayuda_entrada.FichaDeColumna`).
        """
        familias = [familia
                    for vacio in self.grupos
                    for familia in (vacio.familias or tuple(Familia))]
        return tuple(f for f in Familia if f in familias)


@dataclass(frozen=True)
class ContrasteDelCSV:
    """El bloque 2 entero: cabecera contra Sec. 1.2 y celdas vacias."""

    filas: int
    faltan: Tuple[str, ...]
    sobran: Tuple[str, ...]
    con_vacios: Tuple[ColumnaConVacios, ...]

    @property
    def cabecera_completa(self) -> bool:
        return not self.faltan and not self.sobran


def contraste_de_cabecera(ruta: Any) -> ContrasteDelCSV:
    """
    La cabecera del CSV contra `M0_carga.COLUMNAS`, y sus celdas vacias
    contra `M0_carga.VACIOS_ADMITIDOS` --- SIN ejecutar el pipeline: la
    lectura es `M0_carga.leer_cabecera`, que no valida ni lanza por el
    contenido ---.

    Los grupos de cada columna se piden a `VACIOS_ADMITIDOS`, que es el dato
    publico que `_punto_desde_fila` consulta al cargar de verdad: una regla
    propia aqui podria admitir un vacio que la carga rechaza. La lectura por
    UNION de familias (sin fijar una) es la misma que usa la ayuda de la
    pestana 1, y es parte de por que esto es una estimacion: cual familia
    trae cada fila solo lo dice la carga completa.
    """
    cabecera = m0.leer_cabecera(ruta)
    faltan = tuple(c for c in m0.COLUMNAS if c not in cabecera.columnas)
    sobran = tuple(c for c in cabecera.columnas if c not in m0.COLUMNAS)
    con_vacios = tuple(
        ColumnaConVacios(
            columna=columna, vacias=vacias,
            grupos=tuple(vacio for vacio in m0.VACIOS_ADMITIDOS
                         if columna in vacio.columnas))
        for columna, vacias in cabecera.vacias_por_columna.items() if vacias)
    return ContrasteDelCSV(filas=cabecera.filas, faltan=faltan, sobran=sobran,
                           con_vacios=con_vacios)


def _celdas(cuantas: int) -> str:
    return f"{cuantas} celda" + ("" if cuantas == 1 else "s")


def _en_que_familias(columna: ColumnaConVacios) -> str:
    familias = columna.familias_del_vacio
    if len(familias) == len(tuple(Familia)):
        return "en las tres familias"
    return "solo en " + ", ".join(f"Familia {f.value}" for f in familias)


def lineas_del_contraste(contraste: ContrasteDelCSV) -> Tuple[str, ...]:
    """
    Las lineas del bloque 2, elegidas aqui para que gui/ solo pinte (el
    reparto de `traza_punto`). El orden es el del riesgo: primero lo que
    detendria la carga, despues lo que espera a un tablero.
    """
    lineas = []
    if contraste.faltan:
        lineas.append(
            "Faltan columnas de Sec. 1.2 (la carga del CSV se detendrá): "
            + ", ".join(contraste.faltan) + ".")
    if contraste.sobran:
        lineas.append("Columnas no reconocidas: "
                      + ", ".join(contraste.sobran)
                      + " — revisa si alguna está mal escrita.")
    if contraste.cabecera_completa:
        lineas.append(
            f"Cabecera completa: las {len(m0.COLUMNAS)} columnas de "
            f"Sec. 1.2, con {contraste.filas} fila"
            + ("" if contraste.filas == 1 else "s") + " de datos.")
    for columna in contraste.con_vacios:
        if not columna.admite_vacio:
            lineas.append(
                f"{columna.columna}: {_celdas(columna.vacias)} sin dato — la "
                "columna no admite vacío y la carga del CSV se detendrá ahí.")
            continue
        quien = "; ".join(vacio.quien_lo_debe for vacio in columna.grupos)
        lineas.append(
            f"{columna.columna}: {_celdas(columna.vacias)} sin dato — vacío "
            f"admitido {_en_que_familias(columna)} (lo debe: {quien}).")
    return tuple(lineas)


# ===========================================================================
# Bloque 3 - lo que el alcance elegido difiere
# ===========================================================================

@dataclass(frozen=True)
class DiferimientosDelAlcance:
    """Lo que una corrida de ese alcance difiere, leido del servicio."""

    alcance: str
    verificaciones: Tuple[str, ...]
    modulos: Tuple[str, ...]

    @property
    def difiere_algo(self) -> bool:
        return bool(self.verificaciones or self.modulos)


def diferimientos_del_alcance(alcance: str) -> DiferimientosDelAlcance:
    """
    La lista REAL de lo que ese alcance difiere, leida del servicio de
    calculo y no escrita a mano: `VERIFICACIONES_DIFERIDAS_POR_ALCANCE` (las
    que se intentan y cuyo fallo se difiere, hoy V5 y V8 a perfil) y
    `MODULOS_DIFERIDOS_POR_ALCANCE` (los que la corrida no ejecuta). Los dos
    diccionarios los consulta la propia corrida, de modo que esta lista no
    puede divergir de lo que la corrida hace.

    Hasta EXT-9 los dos se leian de `cli`, importado DENTRO de la funcion
    para no arrastrar la capa de arriba al cargar este modulo; desde EXT-9
    viven en `src/servicio.py`, que es un modulo de esta misma capa y se
    importa arriba, como cualquier otro.
    """
    return DiferimientosDelAlcance(
        alcance=alcance,
        verificaciones=tuple(servicio.VERIFICACIONES_DIFERIDAS_POR_ALCANCE[alcance]),
        modulos=tuple(servicio.MODULOS_DIFERIDOS_POR_ALCANCE[alcance]))


def lineas_de_diferimientos(diferido: DiferimientosDelAlcance) -> Tuple[str, ...]:
    """Las lineas del bloque 3. Nada diferido tambien se dice, en positivo."""
    if not diferido.difiere_algo:
        return (f"El alcance «{diferido.alcance}» no difiere nada: corre el "
                "pipeline completo.",)
    lineas = []
    if diferido.verificaciones:
        lineas.append(
            "Verificaciones que se intentan y cuyo fallo se difiere al "
            "expediente: " + ", ".join(diferido.verificaciones) + ".")
    if diferido.modulos:
        lineas.append(
            "Módulos de cálculo que esta corrida no ejecuta: "
            + ", ".join(diferido.modulos) + ".")
    return tuple(lineas)


# ===========================================================================
# Bloque 4 - los datos que faltan, punto a punto, sin ejecutar el pipeline (PF-2)
# ===========================================================================
#
# LA EVIDENCIA QUE LO ABRIO: la corrida de perfil de la revision de E-B
# necesito CUATRO corridas para dimensionar el punto de Familia C, porque cada
# bloqueo aparecio despues del anterior --- `luz_m`, los siete criterios del
# cajon, `cota_coronacion_canal`, `S_conducto` ---: `servicio._etapa` registra
# UN bloqueo por etapa y el revisor ve el siguiente solo al corregir el
# primero. Este bloque lee de una vez lo que la corrida iria diciendo capa a
# capa, y lo lee de donde la corrida lo decide:
#
#   columnas obligatorias vacias     m0.columnas_que_admiten_vacio(familia),
#                                    que es lo que `_punto_desde_fila` consulta
#   columnas admitidas vacias        m0.VACIOS_ADMITIDOS (quien las debe y si
#                                    esperan a alguien) y el censo de
#                                    consumidores de `variables_entrada`, menos
#                                    los modulos que el alcance difiere
#                                    (servicio.MODULOS_DIFERIDOS_POR_ALCANCE)
#   la columna que exige UNA familia servicio.FAMILIAS_QUE_EXIGEN_COLUMNA
#   claves externas                  servicio.CLAVES_EXTERNAS,
#                                    servicio.familias_que_usan, y los textos
#                                    con que `_fase_2` y `_fase_10` registran la
#                                    falta (ETAPA_FALTA_*, DETALLE_FALTA_*)
#   el TW sin ninguna via            servicio.tw_sin_via_de_sec_1_3, el MISMO
#                                    predicado que `_resolver_tw`
#
# SIGUE SIENDO UNA ESTIMACION, por dos razones medidas y no supuestas
# (tests/test_pf2_prevuelo.py, la union contra la corrida real): estima de MAS
# cuando la corrida se detiene en una falta anterior del mismo punto y no llega
# a producir las siguientes, y no ve lo que solo se sabe corriendo (un
# criterio dict al que le falta una entrada, una cota que M7 exige tras
# tender el conducto). Lo que garantiza el test es la direccion que importa:
# ningun DatoFaltanteError real sobre una columna o una clave externa escapa a
# lo que aqui se estimo para ese punto.

DETIENE = "detiene"
ESPERA = "espera"
COLUMNA = "columna del CSV"
EXTERNO = "dato externo"
# Los modulos del censo que LEEN la columna sin consumirla en un calculo: la
# carga y el reporte. Que una columna admitida vacia solo los tenga a ellos
# como consumidores es lo que la vuelve «espera» y no «detiene».
_LECTORES_SIN_CALCULO = ("M0_carga", "M11_reporte")


@dataclass(frozen=True)
class DatoFaltanteEstimado:
    """
    Una falta estimada para UN punto: que dato, de que poblacion, de donde
    tendria que venir, en que etapa se sentiria, y si DETIENE esa etapa o
    solo ESPERA a un tablero (M0 la admite vacia y ningun modulo de calculo
    de este alcance la consume).
    """

    id_punto: str
    familia: Optional[Familia]
    dato: str
    poblacion: str
    de_donde: str
    etapa: str
    detiene: bool


def _filas_crudas(ruta: Any) -> List[Dict[str, str]]:
    """
    Las filas del CSV tal como estan, SIN validar: la misma lectura de
    solo-contenido que `M0_carga.leer_cabecera`, fila a fila. Una fila sin
    ningun contenido no cuenta; una celda que no alcanza a traer, vacia.
    """
    with Path(ruta).open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo, restval="")
        return [{(k or "").strip(): (v or "").strip() for k, v in fila.items() if k}
                for fila in lector
                if any((v or "").strip() for v in fila.values())]


def _familia_de(fila: Dict[str, str]) -> Optional[Familia]:
    try:
        return Familia(fila.get("familia", ""))
    except ValueError:
        return None


def _grupos_que_admiten(columna: str, familia: Optional[Familia]) -> Tuple[VacioAdmitido, ...]:
    return tuple(v for v in m0.VACIOS_ADMITIDOS
                 if columna in v.columnas and v.alcanza_a(familia))


def _consumidores_de_calculo(clave: str, alcance: str) -> Tuple[str, ...]:
    diferidos = set(servicio.MODULOS_DIFERIDOS_POR_ALCANCE.get(alcance, ()))
    return tuple(m for m in _ve.variable(clave).consumido_por
                 if m not in _LECTORES_SIN_CALCULO and m not in diferidos)


def _aplica(clave: str, familia: Optional[Familia]) -> bool:
    return familia is None or familia in servicio.familias_que_usan(clave)


def _numero_o_none(celda: str) -> Optional[float]:
    try:
        return float(celda) if celda else None
    except ValueError:
        return None


def datos_faltantes_por_punto(ruta_csv: Any, externos: Any,
                              alcance: str) -> Tuple[DatoFaltanteEstimado, ...]:
    """
    El bloque 4: lo que le falta a cada fila del CSV para que la corrida de
    ese alcance no se detenga por un dato, sin ejecutar el pipeline.

    `externos` es el `DatosExternos` que la corrida recibiria (el JSON de
    `--datos-externos` mas las banderas): una clave declarada ahi, global o
    por punto, cuenta como presente. Lee el CSV con `_filas_crudas`, que no
    valida ni lanza por el contenido, y los fallos de E/S salen como tales.
    """
    salida: List[DatoFaltanteEstimado] = []
    externas_no_columna = tuple(c for c in servicio.CLAVES_EXTERNAS
                                if c not in m0.COLUMNAS)
    for fila in _filas_crudas(ruta_csv):
        id_punto = fila.get("id", "") or "(fila sin id)"
        familia = _familia_de(fila)
        admiten = m0.columnas_que_admiten_vacio(familia)

        def anadir(dato, poblacion, de_donde, etapa, detiene):
            salida.append(DatoFaltanteEstimado(
                id_punto=id_punto, familia=familia, dato=dato,
                poblacion=poblacion, de_donde=de_donde, etapa=etapa,
                detiene=detiene))

        # --- columnas presentes en la cabecera con la celda vacia ---------
        for columna in m0.COLUMNAS:
            if columna not in fila or fila[columna]:
                continue
            concepto = _ve.variable(columna).concepto
            if columna in servicio.CLAVES_EXTERNAS and externos.dato(id_punto, columna) is not None:
                continue                      # la trae el JSON o una bandera
            if columna in servicio.COLUMNAS_DEL_TW:
                continue                      # es una via del TW: ver abajo
            if columna not in admiten:
                anadir(columna, COLUMNA, concepto, "carga del CSV (M0, Sec. 1.2)", True)
                continue
            grupos = _grupos_que_admiten(columna, familia)
            if not any(g.marca_pendiente for g in grupos):
                continue                      # regla declarada: no espera a nadie
            quien = "; ".join(g.quien_lo_debe for g in grupos)
            de_donde = f"{concepto}. Lo debe: {quien}"
            if columna == "S_cauce" and externos.dato(id_punto, "S_conducto") is None:
                de_donde += (". La via alterna del conducto (S_conducto, por "
                             "--datos-externos) tampoco esta declarada")
            exigida_por = servicio.FAMILIAS_QUE_EXIGEN_COLUMNA.get(columna)
            consumidores = _consumidores_de_calculo(columna, alcance)
            if exigida_por is not None:
                detiene = familia is None or familia in exigida_por
            else:
                detiene = bool(consumidores)
            etapa = (("la exige " + ", ".join(consumidores)) if detiene
                     else "ningun modulo de calculo de este alcance la consume")
            anadir(columna, COLUMNA, de_donde, etapa, detiene)

        # --- claves externas que no son columna -------------------------
        for clave in externas_no_columna:
            if not _aplica(clave, familia) or externos.dato(id_punto, clave) is not None:
                continue
            concepto = _ve.variable(clave).concepto
            if clave == "luz_m":
                anadir(clave, EXTERNO, f"{concepto}. {servicio.DETALLE_FALTA_LUZ}",
                       servicio.ETAPA_FALTA_LUZ, True)
            elif clave == "L_hidraulico_m":
                anadir(clave, EXTERNO,
                       f"{concepto}. {servicio.DETALLE_FALTA_L_HIDRAULICO}",
                       servicio.ETAPA_FALTA_L_HIDRAULICO, True)
            elif clave == "TW_m":
                sin_via = servicio.tw_sin_via_de_sec_1_3(
                    None, _numero_o_none(fila.get("cota_TW", "")),
                    _numero_o_none(fila.get("Q_receptor_m3s", "")))
                if sin_via:
                    anadir(clave, EXTERNO,
                           f"{concepto}. Sin TW declarado, sin cota_TW y sin "
                           "Q_receptor_m3s (o sin 'seccion_receptor' declarado), "
                           "el TW cae en la ultima puerta de Sec. 1.3, el "
                           "criterio 'TW_receptor' (bloque 1)",
                           "tirante en el receptor (TW, Sec. 1.3)", False)
            # longitud_m, categoria_tr y S_conducto tienen via alterna en el
            # codigo (7.B, la fila fija o el criterio de la Tabla N 02, y
            # S_cauce): no son faltas. S_conducto se nombra en la entrada de
            # S_cauce cuando las dos faltan.
    return tuple(salida)


def lineas_del_prevuelo(estimado: Tuple[DatoFaltanteEstimado, ...]) -> Tuple[str, ...]:
    """Las lineas del bloque 4, una por falta, con el recuento delante."""
    detienen = [e for e in estimado if e.detiene]
    esperan = [e for e in estimado if not e.detiene]
    if not estimado:
        return ("Nada falta por punto: ninguna columna obligatoria vacía, ninguna "
                "clave externa sin declarar y ningún vacío que espere a un tablero.",)
    lineas = [f"Datos que faltan: {len(detienen)} que detienen una etapa y "
              f"{len(esperan)} que esperan a un tablero (estimación por punto)."]
    for e in detienen + esperan:
        familia = "" if e.familia is None else f" (Familia {e.familia.value})"
        estado = "DETIENE" if e.detiene else "espera"
        lineas.append(f"{e.id_punto}{familia} · {e.dato} · {estado} · {e.etapa} "
                      f"· {e.poblacion}: {e.de_donde}")
    return tuple(lineas)
