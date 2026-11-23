# -*- coding: utf-8 -*-
"""
M11_reporte._base
=================
Submodulo de Fase 11 (`M11_reporte`): bloque `_base` (D3).
"""

from __future__ import annotations

import html
import math
import re
from pathlib import Path
from string import Template
from typing import (
    Any,
    Dict,
    Tuple,
)
from src.normativa import registro as _registro_M11
from src.modelos import (
    EstadoDeVerificacion,
    TipoDeVeredicto,
)


_reg_M11 = _registro_M11.construir()


def rotulo_norma_producto(material: Any) -> str:
    """
    Como se nombra la norma de producto de un material en la memoria y en el
    cuadro resumen. Para la seccion circular es «norma de producto <X>»;
    para el marco, que NO tiene norma de producto (EXT-N-03), el rotulo de
    M2 ya empieza por «sin norma de producto: ...» y anteponerle «norma de
    producto» habria impreso «norma de producto sin norma de producto». Es
    eleccion de etiqueta, no aritmetica: M11 sigue sin calcular nada.
    """
    rotulo = material.norma_producto
    if rotulo.startswith("sin norma de producto"):
        return rotulo
    return f"norma de producto {rotulo}"



# ---------------------------------------------------------------------------
# Rutas del reporte. Ninguna es un valor de proyecto: son la ubicacion de los
# archivos del propio script.
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parents[3]      # src/modulos/M11_reporte/_base.py -> M11_reporte -> modulos -> src -> raiz
SRC = RAIZ / "src"
DIR_PLANTILLAS = SRC / "plantillas"
NOMBRE_PLANTILLA = "memoria_alcantarillas.html"
# Segunda plantilla, para corridas a nivel de perfil: misma estetica y
# mismo contrato de marcadores, pero sin el volcado de Tableros 1-2-3 y
# con el bloque de alcance en su lugar. Ver `cargar_plantilla`.
NOMBRE_PLANTILLA_PERFIL = "memoria_perfil.html"
ARCHIVO_CRITERIOS = SRC / "criterios_adoptados.py"

DIR_DOCS = RAIZ / "docs"
# Con comodin de version: cuando la hoja pase a v8 el reporte la encuentra sin
# tocar este archivo, y la version que imprime sale del propio documento.
PATRON_HOJA_RUTA = "hoja_de_ruta_alcantarillas_v*.md"

# Presentacion. Son formatos de texto, no magnitudes: cambiar un decimal no
# mueve ningun resultado del calculo.
FMT_2 = "{:.2f}"
FMT_3 = "{:.3f}"
# Cuatro decimales para la PENDIENTE del diseño: con tres, una S de 0.0006
# se imprime 0.001 y la caida S*L de la Fase 7 deja de recomputarse desde la
# memoria, que es justo lo que esa fila existe para permitir (MAT-D9).
FMT_4 = "{:.4f}"
VACIO = "&ndash;"
MARCA_CUMPLE = "cumple"
MARCA_INCUMPLE = "NO cumple"
# El AVISO de PF-4: un indicador que se disparo bajo `regimen_v2b` =
# indicador_con_aviso. Ni incumple (el punto no se detiene) ni diferido (se
# evaluo): tiene su marca y su clase, y la tabla de verificaciones lo lee del
# `paso.veredicto` de la propia `Verificacion`, no de `cumple`.
MARCA_INDICADOR = "INDICADOR (aviso)"
CLASE_INDICADOR = "indicador"
# La fila que existe en la tabla de la Fase 5 y en este punto no dice nada
# (PC-27, cierre): V5 en la Familia C, sustituida por VC1. Se imprime con
# el motivo al lado, en vez de no imprimirse.
MARCA_NO_APLICA = "no aplica"
CLASE_NO_APLICA = "no-aplica"

# Orden de lectura de las etiquetas, de mas normativo a mas adoptado. Reproduce
# el de `criterios_adoptados.reporte_criterios`.
ORDEN_ETIQUETAS: Tuple[str, ...] = ("N", "N->", "S", "C", "A")
CLASE_ETIQUETA: Dict[str, str] = {"N": "et-N", "N->": "et-Na", "S": "et-S",
                                  "C": "et-C", "A": "et-A"}
ETIQUETA_HTML: Dict[str, str] = {"N": "N", "N->": "N&rarr;", "S": "S",
                                 "C": "C", "A": "A"}

# Fila del Tablero 2 que declara el detalle de embocadura del cabezal. La
# columna "Tipo de cabezal" del cuadro resumen (entregable 3) sale de ahi y no
# de una constante de este modulo: es una DECISION de proyecto, y su estado
# -- cerrada o abierta -- lo lleva la hoja de ruta.
ITEM_EMBOCADURA = "2.3"
# Columna del Tablero 2 que lleva la decision adoptada. Se busca por NOMBRE de
# encabezado y no por posicion: una columna nueva en la hoja de ruta no debe
# hacer que la memoria imprima la celda equivocada en silencio.
COLUMNA_ESTADO = "estado"

VIA_WEASYPRINT = "weasyprint"
VIA_NAVEGADOR = "navegador"

# Columnas del CSV de Sec. 1.2 tal como se listan en la memoria del punto:
# (campo de PuntoCritico, rotulo, unidad). El campo es la fuente: la memoria
# cita la columna de la que salio el dato, no solo el numero.
CAMPOS_CSV: Tuple[Tuple[str, str, str], ...] = (
    ("progresiva_km", "Progresiva", "km"),
    ("familia", "Familia (Sec. 2.3)", ""),
    ("Q_m3s", "Caudal de diseño", "m3/s"),
    ("area_ha", "Area tributaria", "ha"),
    ("S_cauce", "Pendiente del cauce", "m/m"),
    ("cota_terreno", "Cota de terreno", "msnm"),
    ("cota_rasante", "Cota de rasante", "msnm"),
    ("cota_subrasante", "Cota de subrasante", "msnm"),
    ("cbr_subrasante", "CBR de subrasante", "%"),
    ("esviaje_grados", "Esviaje", "grados"),
    ("ancho_plataforma", "Ancho de plataforma", "m"),
    ("cota_fondo_receptor", "Cota de fondo del receptor", "msnm"),
    ("Q_receptor_m3s", "Caudal del receptor", "m3/s"),
    ("cota_TW", "Cota de TW", "msnm"),
    ("sucs_fundacion", "SUCS de la fundacion", ""),
    # No viene del encabezado de Sec. 1.2 -- se agrego al reclasificar el NF
    # como dato por punto -- y por eso faltaba en esta tabla. Se carga, se
    # valida y viaja en `PuntoCritico`: si no se imprime, la memoria no
    # muestra un dato del expediente que el CSV si trae, y el revisor no
    # puede ver si venia vacio (SIS-B-12).
    ("NF_profundidad_m", "Profundidad del nivel freatico", "m"),
    # --- T-10 --- Las dos columnas que T-6 y T-3 sumaron al CSV y que esta
    # tabla no imprimia (el JSON las nombraba entre los pendientes del punto
    # y la memoria no decia si venian vacias): la cota de fondo de la entrada
    # medida en el cauce y la coronacion del canal de la Familia C.
    ("cota_fondo_entrada", "Cota de fondo de la entrada (medida)", "msnm"),
    ("cota_coronacion_canal", "Cota de coronacion del canal", "msnm"),
)

# Datos que no son columna del CSV y llegan declarados (ver `DatoDeclarado` de
# cli.py): el rotulo y el atributo del informe donde vive cada uno.
DATOS_DECLARADOS: Tuple[Tuple[str, str, str], ...] = (
    ("luz", "Luz del cruce", "m"),
    ("categoria_tr", "Fila de la Tabla N 02", ""),
    ("longitud", "Longitud del conducto", "m"),
    ("tw", "TW en el receptor", "m"),
    # C6: la pendiente del cauce EFECTIVA, o sea la que V2b comparo contra la
    # del barril. Entra por este mecanismo y no por la tabla de columnas
    # porque para un punto de Familia C las dos cosas son ciertas a la vez y
    # el revisor necesita las dos: la columna del CSV esta VACIA -- y su fila
    # lo sigue diciendo -- y el valor con que se calculo vino del Tablero 3.1.
    # Para los demas puntos esta fila repite el de la columna, con esa
    # procedencia: es el precio de que la fila no pueda mentir en ninguno de
    # los dos casos.
    ("s_cauce", "Pendiente del cauce (efectiva)", "m/m"),
)


class PlantillaHTML(Template):
    """string.Template con delimitador '%%', igual que en legacy/Tc.py."""
    delimiter = "%%"


# Contrato entre este modulo y la plantilla: los marcadores que M11 entrega.
# Se declara aparte para que el test pueda contrastarlo contra el archivo en
# las dos direcciones -- un marcador que la plantilla pide y M11 no entrega
# revienta la generacion, y uno que M11 calcula y la plantilla no imprime es
# contenido de la memoria que se pierde en silencio.
MARCADORES: Tuple[str, ...] = (
    "proyecto", "subtitulo",
    "version_hoja_ruta", "hoja_ruta_archivo", "hoja_ruta_sha1",
    "csv_ruta", "csv_sha1",
    # UI-1 (ficha T1-04): las rutas y las huellas de las dos entradas de la
    # hidrologia, como filas del encabezado de trazabilidad. Vacio sin
    # hidrologia: la plantilla lo lleva en la MISMA linea que la huella del
    # CSV, de modo que sin hidrologia el HTML no gana ni un byte.
    "filas_hidrologia",
    "criterios_version", "criterios_fecha", "criterios_sha1",
    "generado_local", "generado_utc",
    "estado_expediente", "resumen_expediente",
    "memorias_punto", "filas_resumen",
    "bloque_datos_sitio", "bloque_criterios", "bloque_pendientes",
    "bloque_alcance", "bloque_acotaciones", "bloque_umbrales",
    "bloque_homonimias", "bloque_discrepancias",
    # EXT-8 (PC-12): el anexo unico de fundamentos, citas y umbrales al que
    # cada paso enlaza en vez de transcribirlos. Ver `anexo_referencias`.
    "anexo_referencias",
    # E-B (E21 acotado): el indice del documento, derivado de los `<h2 id>`
    # de la propia plantilla y de los puntos del informe. Ver
    # `indice_de_la_memoria`.
    "indice",
)
MARCADOR_ANEXO = "anexo_referencias"
MARCADOR_INDICE = "indice"

# Las etapas del progreso que `memoria_html_por_partes` y `exportar_pdf`
# comunican por `progreso(etapa, hecho, total)` (EXT-8, PC-11). La CLI las
# vuelca como lineas de stdout con `--progreso`, y la GUI las lee del
# subproceso. Son texto para el usuario, no codigos.
ETAPA_PUNTO = "memoria del punto"
ETAPA_BLOQUES = "bloques generales de la memoria"
ETAPA_PDF = "escritura del PDF"
ETAPA_NAVEGADOR = "memoria HTML escrita para imprimir desde el navegador"


def marcadores_de_la_memoria() -> Tuple[str, ...]:
    """
    Los marcadores que `memoria_html` sustituye en la plantilla.

    NO TIENE LLAMADOR DE PRODUCCION, Y ES DELIBERADO (SIS-B-22). Dentro de
    este modulo el contrato se lee de `MARCADORES` directamente, y el test que
    lo contrasta contra el archivo de plantilla en las dos direcciones hace lo
    mismo: ninguno de los dos necesita pasar por una funcion.

    Existe como PUERTA PUBLICA del contrato, que es distinto de existir por si
    acaso. `MARCADORES` es una constante de modulo y leerla desde fuera ata al
    consumidor al nombre de la variable; esta funcion es lo que una plantilla
    alternativa --- o el `--plantilla` de la CLI el dia que valide la que le
    pasan --- tiene que preguntar para saber que marcadores se le van a
    sustituir, sin importar como esten guardados aqui dentro.

    Si algun dia se cablea, sale de esta declaracion en el mismo commit.
    """
    return MARCADORES


# ===========================================================================
# Utilidades de formato
# ===========================================================================

def _esc(texto: Any) -> str:
    """Todo texto que venga de un dato se escapa antes de entrar al HTML."""
    return html.escape(str(texto))


def _num(valor: Any, fmt: str = FMT_3) -> str:
    """Un numero con decimales fijos; None es celda vacia declarada."""
    if valor is None:
        return VACIO
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return _esc(valor)
    if isinstance(valor, float) and not math.isfinite(valor):
        return _esc(repr(valor))
    return fmt.format(float(valor))


def _valor_legible(valor: Any) -> str:
    """
    Un valor de criterio como se lee en la memoria. Los rangos y los dicts se
    imprimen enteros: un criterio como el n de Manning del HDPE ES un rango, y
    reducirlo a un numero en el reporte contradiria su propia justificacion.
    """
    if valor is None:
        return '<span class="pendiente">sin valor declarado</span>'
    if isinstance(valor, dict):
        return _esc(", ".join(f"{k} = {v}" for k, v in valor.items()))
    if isinstance(valor, (tuple, list)):
        return _esc(", ".join(str(v) for v in valor))
    return _esc(valor)


def _etiqueta_html(etiqueta: str) -> str:
    clase = CLASE_ETIQUETA.get(etiqueta, "")
    texto = ETIQUETA_HTML.get(etiqueta, _esc(etiqueta))
    return f'<span class="etiqueta {clase}">{texto}</span>'


def _marca(cumple: bool) -> str:
    clase = "cumple" if cumple else "incumple"
    texto = MARCA_CUMPLE if cumple else MARCA_INCUMPLE
    return f'<span class="{clase}">{texto}</span>'


def _es_indicador(v: Any) -> bool:
    """True si la verificacion lleva veredicto INDICADOR en su paso (PF-4)."""
    paso = getattr(v, "paso", None)
    veredicto = getattr(paso, "veredicto", None)
    return veredicto is not None and \
        veredicto.tipo is TipoDeVeredicto.INDICADOR


def _marca_de_verificacion(v: Any) -> str:
    estado = getattr(v, "estado", None)
    if estado is EstadoDeVerificacion.NO_APLICA:
        motivo = _esc(getattr(v, "motivo_no_aplica", ""))
        return (f'<span class="{CLASE_NO_APLICA}" title="{motivo}">'
                f"{MARCA_NO_APLICA}</span>")
    if _es_indicador(v) or estado is EstadoDeVerificacion.INDICADOR:
        return f'<span class="{CLASE_INDICADOR}">{MARCA_INDICADOR}</span>'
    return _marca(v.cumple)


def _orden_etiqueta(etiqueta: str) -> int:
    """Posicion de la etiqueta en el orden de lectura; las raras van al final."""
    if etiqueta in ORDEN_ETIQUETAS:
        return ORDEN_ETIQUETAS.index(etiqueta)
    return len(ORDEN_ETIQUETAS)


def _md_inline(celda: str) -> str:
    """El subconjunto de Markdown que usan los tableros, convertido a HTML."""
    salida = _esc(celda.strip())
    salida = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", salida)
    salida = re.sub(r"\*(.+?)\*", r"<i>\1</i>", salida)
    salida = re.sub(r"`(.+?)`", r"<code>\1</code>", salida)
    return salida


def _md_texto(celda: str) -> str:
    """La misma celda sin marcas, para cuando va dentro de otra frase."""
    return re.sub(r"[*`]", "", celda).strip()
