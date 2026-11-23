"""
M11_reporte (subpaquete)
========================
Fase 11 - Memoria de calculo. FORMATEA la traza que el calculo emitio y la
convierte en el documento que se entrega. No calcula nada.

Que cambio en S18, y por que importa (Sec. 4.4 del plan v12)
------------------------------------------------------------
Este modulo RECONSTRUIA la memoria: leia los resultados y volvia a armar el
relato. Para armarlo tenia que calcular, y lo hacia --- `y_normal / D` en dos
sitios --- contra este mismo docstring, que ya decia "sin calcular nada nuevo"
(SIS-A-07). Un reporte que recalcula es un segundo motor de calculo sin tests,
y lo que imprime puede divergir de lo que el pipeline verifico sin que nada
avise.

Ahora cada funcion de calculo emite un `PasoDeMemoria` (`modelos.py`) con los
ocho campos de la §4.4 --- que, por que, formula, sustitucion, resultado,
umbral, veredicto, citas textuales --- y este modulo elige etiquetas y clases
de CSS. La frase "sin calcular nada nuevo" pasa de ser una intencion escrita a
ser una propiedad comprobada: `test_memoria_sustentada.test_M11_no_calcula_y_
sobre_D` barre el AST de este archivo.

Tres cosas que este modulo imprime SEPARADAS, y que no son estilo
-----------------------------------------------------------------
    .fuente          lo que el documento DICE. Entrecomillado, con su numeral.
    .interpretacion  lo que el PROYECTO lee en el documento.
    texto normal     lo que el proyecto HACE con ello.

Pegadas, las tres se leen como norma. El caso testigo es NOR-HID-04: «el rango
recorre la calidad del revestimiento» no esta en el Manual --- nada dice por
que hay dos numeros --- y se imprimia dentro del mismo parrafo que la cita.

Estructura del documento (Sec. "Fase 11 - Entregables")
-------------------------------------------------------
    0. Encabezado de trazabilidad   version de la hoja de ruta, fecha, SHA-1
                                    del CSV de entrada y version de
                                    criterios_adoptados. Sin esto dos memorias
                                    no se distinguen y ninguna es auditable
    1. Memoria por punto            entregable 1: datos CON SU FUENTE,
                                    iteraciones del diseño y cada verificacion
                                    como cumple / no cumple JUNTO A SU NUMERAL
    2. Tabla resumen                entregable 3, con sus doce columnas
    3. Criterios adoptados          entregable 2: los criterios que el calculo
                                    invoco, con etiqueta, justificacion y fuente
    4. Pendientes                   Tableros 1, 2 y 3 EN BLOQUE APARTE

Por que el bloque 4 va aparte
-----------------------------
El bloque 3 lista criterios CERRADOS: tienen valor, fuente y justificacion, y
sostienen los numeros de la memoria. El bloque 4 lista lo que NO esta resuelto.
Mezclarlos daria a entender que el expediente esta mas cerrado de lo que esta.
La hoja de ruta segrego los pendientes en tres tableros precisamente para no
leerlos como una lista homogenea, y la memoria respeta esa separacion.

De donde sale cada cosa
-----------------------
EL ESTADO DE LA CORRIDA SALE DEL INFORME, NO DEL PROCESO (EXT-4, EXT-A-01).
Todo lo que es estado --- que criterios y datos de sitio se invocaron, con que
valor efectivo gobernaron, cuales se declararon o pisaron en caliente y con que
procedencia, el SHA-1 del CSV --- lo trae `Informe.contexto`, un
`ContextoCorrida` congelado que `servicio.correr` fotografia al salir. Hasta EXT-4
este modulo lo leia del registro vivo de `criterios_adoptados`, `datos_sitio`
y `declaracion` en 24 sitios, y una memoria renderizada despues de otra
corrida, o despues de una declaracion, describia un estado que no era el suyo.
De los dos catalogos solo se leen ahora LECTURAS ESTATICAS --- lo que dice el
archivo: concepto, fuente, justificacion, etiqueta --- y
`tests/test_ext4_contexto_corrida.py` barre el AST para que siga siendo asi.

Los tableros NO se transcriben aqui: se leen de la hoja de ruta en cada
corrida. Una copia en Python seria una segunda fuente de verdad que envejece
en silencio en cuanto la hoja pase a v8, que es el error que este proyecto
persigue. Si la hoja cambia de forma y el bloque no se puede leer, M11 se
detiene con ValueError en vez de emitir una memoria con un bloque vacio.

La plantilla
------------
Vive en `src/plantillas/memoria_alcantarillas.html` y se procesa con
`string.Template` y delimitador "%%", el mismo patron de `legacy/Tc.py`. Se
sustituye con `substitute`, no con `safe_substitute`: un marcador sin valor
tiene que reventar en la generacion, no imprimirse en la memoria.

PDF
---
La misma via que ya usa Tc.py, sin dependencia nueva: `weasyprint` si esta
instalado y, si no, se escribe el HTML y se abre en el navegador para
"Imprimir -> Guardar como PDF" (la hoja ya esta configurada en A4).
`exportar_pdf` declara en su resultado cual de las dos vias se uso: nunca
devuelve un PDF que no escribio.

Excepciones
-----------
M11 no produce `ErrorProyecto`: no evalua el expediente, lo transcribe. Un
expediente incompleto es contenido normal de la memoria -- se imprime con sus
bloqueos y sus pendientes -- y no una excepcion. Lo que si falla es la falta de
las piezas del propio reporte (plantilla o hoja de ruta ausentes,
FileNotFoundError; hoja de ruta ilegible, ValueError), que son fallos de
instalacion del script y no del expediente.

Como esta partido (D3 del plan de mantenibilidad)
-------------------------------------------------
Este modulo fue un solo archivo de 6069 lineas hasta D3 y hoy es un
subpaquete; `from src.modulos import M11_reporte as M11` y `from
src.modulos.M11_reporte import X` siguen sirviendo, con los mismos nombres
(privados incluidos), porque este `__init__` los reexporta todos. Los bloques,
en el orden en que se importan unos a otros (ninguno importa de uno posterior):

    _base             rutas, formatos de texto, PlantillaHTML y MARCADORES
    trazabilidad      encabezado de trazabilidad, hoja de ruta, hidrologia
    tableros          Tableros 1-2-3 de la hoja de ruta y bloqueantes
    trazas            titulos y `traza_*` de cada fase
    tablas_diseno     tablas de datos, de diseño y de bloqueos
    anclas            anclas, enlaces e indice de la memoria
    pasos             un `PasoDeMemoria` hecho HTML y la tabla de verificaciones
    cabezal           Fase 9: cabezal, armado, solicitaciones
    metrados          Fase 11: metrados y compatibilidad rasante-alcantarilla
    fases_finales     Fases 6, 8, 9 y 10 del punto
    bloques_punto     `memoria_de_punto` y los bloques que la arman
    proyecto          cabezal del proyecto, resumen del punto y CSV resumen
    sitio_criterios   datos de sitio, discrepancias y criterios adoptados
    pendientes        pendientes (Tableros) y acotaciones
    umbrales_anexos   umbrales, anexos de referencias y de sensibilidad
    memoria           plantilla, alcance y `memoria_html`
    resumida          memoria resumida
    exportadores      HTML, PDF, CSV y la sonda de weasyprint

Dos reglas del paquete: (1) lo que un test reasigna con monkeypatch
(`M11.memoria_de_punto`, `M11.verificaciones_publicadas`, ...) se propaga a
los submodulos que llevan ese nombre (`_PaqueteM11`), y el estado de la sonda
de weasyprint (`WeasyHTML`, `FALLO_WEASYPRINT`, `WEASYPRINT_AUSENTE`,
`_WEASYPRINT_SONDEADO`) vive SOLO en `exportadores` y el paquete lo lee y lo
escribe alli; (2) las guardias por AST barren todos los archivos del paquete
(`M11_reporte/*.py`), no solo este.

Uso
---
    from src.modulos.M11_reporte import memoria_html, exportar_html, exportar_pdf

    html_texto = memoria_html(informe, proyecto="Via de evitamiento - La Union")
    exportar_html(informe, Path("Memoria.html"))
"""

from __future__ import annotations

import sys as _sys
import types as _types

# Modulos y nombres externos expuestos en `M11_reporte` (compatibilidad con tests y llamadores)
import contextvars
import csv
import hashlib
import html
import math
import os
import re
import tempfile
import webbrowser
from dataclasses import (
    dataclass,
    replace,
)
from datetime import datetime
from pathlib import Path
from string import Template
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
)
from src import (
    criterios_adoptados as ca,
    datos_sitio as ds,
    responsable as _responsable,
)
from src.constantes_normativas import (
    FISURACION_FRACCION_FR,
    RECUBRIMIENTO_MP_PISO_MM,
    HOMONIMIAS,
    UMBRALES_DE_VERIFICACION,
    H_O_HW_SOBRE_D_CAUTELA,
    H_O_HW_SOBRE_D_MIN,
    H_O_NUMERAL,
    caracter_del_umbral,
    fundamento_del_umbral,
    literales_del_umbral,
    numeral_del_umbral,
)
from src.normativa import (
    fundamentos as _fundamentos,
    registro as _registro_M11,
)
from src.modulos.M5_verificaciones import (
    CRITERIO_ORIGEN_COTA_ENTRADA,
    verificaciones_no_evaluadas,
)
from src.modulos.M8_estructural import verificacion_diferida_estructural
from src.modulos import M2_material as _M2
from src.modelos import (
    ALCANCE_DECLARADO,
    ALCANCE_EXPEDIENTE,
    ALCANCE_PERFIL,
    AVISO_SIN_ACCESO_DE_MANTENIMIENTO,
    ContextoCorrida,
    ControlGobernante,
    EstadoDeVerificacion,
    modo_de,
    MOTIVO_METODO_NO_EVALUABLE,
    TipoDeBloqueo,
    TipoDeVeredicto,
    ESTADO_RASANTE_COMPATIBLE,
    MURO_ALERO,
)
from src.modulos.M11_reporte import _base as _mod__base
from src.modulos.M11_reporte._base import (
    _reg_M11,
    rotulo_norma_producto,
    RAIZ,
    SRC,
    DIR_PLANTILLAS,
    NOMBRE_PLANTILLA,
    NOMBRE_PLANTILLA_PERFIL,
    ARCHIVO_CRITERIOS,
    DIR_DOCS,
    PATRON_HOJA_RUTA,
    FMT_2,
    FMT_3,
    FMT_4,
    VACIO,
    MARCA_CUMPLE,
    MARCA_INCUMPLE,
    MARCA_INDICADOR,
    CLASE_INDICADOR,
    MARCA_NO_APLICA,
    CLASE_NO_APLICA,
    ORDEN_ETIQUETAS,
    CLASE_ETIQUETA,
    ETIQUETA_HTML,
    ITEM_EMBOCADURA,
    COLUMNA_ESTADO,
    VIA_WEASYPRINT,
    VIA_NAVEGADOR,
    CAMPOS_CSV,
    DATOS_DECLARADOS,
    PlantillaHTML,
    MARCADORES,
    MARCADOR_ANEXO,
    MARCADOR_INDICE,
    ETAPA_PUNTO,
    ETAPA_BLOQUES,
    ETAPA_PDF,
    ETAPA_NAVEGADOR,
    marcadores_de_la_memoria,
    _esc,
    _num,
    _valor_legible,
    _etiqueta_html,
    _marca,
    _es_indicador,
    _marca_de_verificacion,
    _orden_etiqueta,
    _md_inline,
    _md_texto,
)
from src.modulos.M11_reporte import trazabilidad as _mod_trazabilidad
from src.modulos.M11_reporte.trazabilidad import (
    Trazabilidad,
    sha1_de_bytes,
    sha1_archivo,
    ruta_hoja_de_ruta,
    version_hoja_de_ruta,
    version_criterios,
    fecha_archivo,
    trazabilidad,
    ROTULO_CSV_CUENCAS,
    ROTULO_SHA1_CUENCAS,
    ROTULO_CSV_ESTACION,
    ROTULO_SHA1_ESTACION,
    filas_hidrologia,
)
from src.modulos.M11_reporte import tableros as _mod_tableros
from src.modulos.M11_reporte.tableros import (
    Tablero,
    _RE_TITULO_TABLERO,
    _RE_GLOSA,
    _RE_SEPARADOR,
    _celdas,
    tableros_pendientes,
    decision_embocadura,
    CriterioBloqueante,
    criterios_bloqueantes,
    DatoBloqueante,
    datos_bloqueantes,
)
from src.modulos.M11_reporte import tablas_diseno as _mod_tablas_diseno
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
    _tabla_datos,
    _tabla_clasificacion,
    _tabla_iteraciones,
    AVISO_SIN_DIMENSIONAR,
    SALIDA_NO_SE_FORMA,
    _celda_control_gobernante,
    _tabla_diseno,
    _filas_combinacion_adoptada,
    _filas_h_o,
    _tabla_diseno_con_perfil,
    sin_fundamento_por_codigo,
    ROTULO_TIPO_DE_BLOQUEO,
    _tabla_bloqueos,
)
from src.modulos.M11_reporte import trazas as _mod_trazas
from src.modulos.M11_reporte.trazas import (
    TITULO_TRAZA_CLASIFICACION,
    TITULO_CAUDAL_DE_DISENO,
    TITULO_TRAZA_HIDROLOGIA,
    TITULO_TRAZA_TW,
    TITULO_TRAZA_HIDRAULICA,
    TITULO_TRAZA_HIDRAULICA_ULTIMO,
    TITULO_TRAZA_VERIFICACIONES,
    TITULO_DURABILIDAD,
    ETAPA_DURABILIDAD,
    TITULO_TRAZA_DURABILIDAD,
    TITULO_LICUEFACCION,
    ETAPA_LICUEFACCION,
    TITULO_TRAZA_LICUEFACCION,
    TEXTO_LICUEFACCION_BLOQUEADA,
    TITULO_TRAZA_GEOMETRIA,
    TITULO_TRAZA_GEOMETRIA_PREVIA,
    TITULO_TRAZA_ESPACIAMIENTO,
    traza_clasificacion,
    traza_hidrologia,
    traza_durabilidad,
    traza_licuefaccion,
    traza_espaciamiento,
    traza_geometria,
    traza_tw,
    traza_hidraulica,
    verificaciones_publicadas,
)
from src.modulos.M11_reporte import anclas as _mod_anclas
from src.modulos.M11_reporte.anclas import (
    _cita_como_texto,
    _SLUG_NO_ADMITIDO,
    _slug,
    ancla_de_cita,
    ancla_de_fundamento,
    ancla_de_discrepancia,
    ancla_de_criterio,
    ancla_de_punto,
    _RE_H2_DE_LA_PLANTILLA,
    _RE_ETIQUETA_HTML,
    indice_de_la_memoria,
    ancla_de_umbral,
    _clave_de_umbral,
    _donde,
    _enlace,
)
from src.modulos.M11_reporte import pasos as _mod_pasos
from src.modulos.M11_reporte.pasos import (
    _YaImpreso,
    _IMPRESOS,
    _citas_del_paso,
    citas_en_que_descansa,
    _discrepancias_que_toca,
    _discrepancias_del_paso,
    _sustitucion_del_paso,
    _umbral_del_paso,
    _veredicto_del_paso,
    _elecciones_del_paso,
    _por_que_del_paso,
    bloque_paso,
    _bloque_paso_entero,
    _nota_del_proyecto,
    bloque_pasos,
    _paso_ausente,
    NoAplica,
    _no_aplica_html,
    desarrollo_de_verificaciones,
    SIN_VERIFICACIONES,
    MARCA_VACIO_VERIFICADO,
    _filas_verificaciones,
    _tabla_verificaciones,
)
from src.modulos.M11_reporte import cabezal as _mod_cabezal
from src.modulos.M11_reporte.cabezal import (
    TITULO_TRAZA_CABEZAL,
    traza_cabezal,
    _bloque_cabezal,
    _linea_embocadura,
    _tabla_solicitaciones,
    TITULO_ARMADO,
    _bloque_armado,
    _traza_cabezal_sin_repetir,
)
from src.modulos.M11_reporte import fases_finales as _mod_fases_finales
from src.modulos.M11_reporte.fases_finales import (
    traza_proteccion,
    TITULO_TRAZA_PROTECCION,
    _fase_6_ampliada,
    _bloques_fases_finales,
    _bloque_estructural,
    _tabla_portico,
)
from src.modulos.M11_reporte import metrados as _mod_metrados
from src.modulos.M11_reporte.metrados import (
    TITULO_METRADO_PUNTO,
    TITULO_TRAZA_METRADO,
    TITULO_METRADOS_PROYECTO,
    ANCLA_METRADOS_PROYECTO,
    traza_metrado,
    _tabla_renglones,
    _bloque_compatibilidad_punto,
    _bloque_metrado,
    _cota,
    bloque_metrados_proyecto,
)
from src.modulos.M11_reporte import bloques_punto as _mod_bloques_punto
from src.modulos.M11_reporte.bloques_punto import (
    _bloque_durabilidad,
    _bloque_licuefaccion,
    _pasos_de_clasificacion,
    _bloque_hidrologia,
    _paso_del_tw,
    _acceso_de_mantenimiento,
    _pasos_hidraulicos_del_punto,
    TITULO_GOBIERNO_RECEPTOR,
    _paso_gobierno_por_receptor,
    memoria_de_punto,
)
from src.modulos.M11_reporte import proyecto as _mod_proyecto
from src.modulos.M11_reporte.proyecto import (
    TITULO_CABEZAL_PROYECTO,
    ANCLA_CABEZAL_PROYECTO,
    bloque_cabezal_proyecto,
    TITULO_AVISOS_DEL_PUNTO,
    _avisos_que_faltan,
    tipo_cabezal_del_punto,
    fila_resumen,
    COLUMNAS_RESUMEN_CSV,
    _fila_resumen_csv,
)
from src.modulos.M11_reporte import sitio_criterios as _mod_sitio_criterios
from src.modulos.M11_reporte.sitio_criterios import (
    _cabecera_de_corredor,
    _declaracion_en_sesion,
    datos_sitio_resumidos,
    bloque_datos_sitio,
    _procedencia,
    _de_donde_salio,
    _de_donde_sale_el_valor,
    _sensibilidad_declarada,
    pasos_del_informe,
    pasos_del_punto,
    _ancla_de_parte,
    bloque_discrepancias,
    _criterio_efectivo,
    _valor_por_punto,
    bloque_criterios,
)
from src.modulos.M11_reporte import pendientes as _mod_pendientes
from src.modulos.M11_reporte.pendientes import (
    _tabla_tablero,
    bloque_pendientes,
    acotaciones_declaradas,
    bloque_acotaciones,
)
from src.modulos.M11_reporte import umbrales_anexos as _mod_umbrales_anexos
from src.modulos.M11_reporte.umbrales_anexos import (
    _interpretacion_tabla_10,
    bloque_umbrales,
    pasos_impresos,
    ROTULO_DE_LA_FRASE_POR_CARACTER,
    _rotulo_de_la_frase,
    _umbrales_del_informe,
    _exigir_anclas_inyectivas,
    anexo_referencias,
    TITULO_ANEXO_SENSIBILIDAD,
    criterios_A_por_punto,
    anexo_sensibilidad,
)
from src.modulos.M11_reporte import memoria as _mod_memoria
from src.modulos.M11_reporte.memoria import (
    bloque_homonimias,
    bloque_alcance,
    cargar_plantilla,
    _exigir_que_la_plantilla_no_pierda_contenido,
    _resumen_expediente,
    estado_del_expediente,
    memoria_html,
    memoria_html_por_partes,
)
from src.modulos.M11_reporte import resumida as _mod_resumida
from src.modulos.M11_reporte.resumida import (
    NOMBRE_PLANTILLA_RESUMIDA,
    MARCADORES_RESUMIDA,
    PREFIJO_ANCLA_RESUMEN,
    TITULO_RESUMEN_RESULTADO,
    TITULO_RESUMEN_VERIFICACIONES,
    TITULO_RESUMEN_AVISOS,
    TITULO_RESUMEN_CRITERIOS,
    SIN_AVISOS,
    _criterios_A_del_punto,
    resumen_de_punto,
    pendientes_resumidos,
    REMISION_COMO_COMPROBARLO,
    _remision_a_la_completa,
    memoria_resumida_html,
)
from src.modulos.M11_reporte import exportadores as _mod_exportadores
from src.modulos.M11_reporte.exportadores import (
    _importar_weasyprint,
    weasyprint_disponible,
    ResultadoExportacion,
    exportar_html,
    exportar_csv,
    exportar_html_resumida,
    exportar_pdf_resumida,
    exportar_pdf,
    _escribir_pdf,
    _por_que_no_hay_weasyprint,
    _mensaje_via_navegador,
)

_SUBMODULOS_M11 = (
    _mod__base,
    _mod_trazabilidad,
    _mod_tableros,
    _mod_tablas_diseno,
    _mod_trazas,
    _mod_anclas,
    _mod_pasos,
    _mod_cabezal,
    _mod_fases_finales,
    _mod_metrados,
    _mod_bloques_punto,
    _mod_proyecto,
    _mod_sitio_criterios,
    _mod_pendientes,
    _mod_umbrales_anexos,
    _mod_memoria,
    _mod_resumida,
    _mod_exportadores,
)
_NOMBRES_SUBMODULOS = frozenset(('_base', 'trazabilidad', 'tableros', 'tablas_diseno', 'trazas', 'anclas', 'pasos', 'cabezal', 'fases_finales', 'metrados', 'bloques_punto', 'proyecto', 'sitio_criterios', 'pendientes', 'umbrales_anexos', 'memoria', 'resumida', 'exportadores',))


# El estado de la sonda de weasyprint vive en `exportadores` (ahi lo escribe
# `weasyprint_disponible` con `global`): el paquete no guarda copia, la lee y
# la escribe alli, para que `M11.WeasyHTML` sea siempre lo que decide la via.
_ESTADO_DE_LA_SONDA = frozenset((
    'WeasyHTML', 'FALLO_WEASYPRINT', 'WEASYPRINT_AUSENTE',
    '_WEASYPRINT_SONDEADO'))


class _PaqueteM11(_types.ModuleType):
    """Propaga reasignaciones de monkeypatch sobre `M11_reporte` a sus submodulos."""

    def __getattr__(self, nombre: str):
        if nombre in _ESTADO_DE_LA_SONDA:
            return getattr(_mod_exportadores, nombre)
        raise AttributeError(
            f"module {self.__name__!r} has no attribute {nombre!r}")

    def __setattr__(self, nombre: str, valor) -> None:
        if nombre in _ESTADO_DE_LA_SONDA:
            setattr(_mod_exportadores, nombre, valor)
            return
        super().__setattr__(nombre, valor)
        if nombre.startswith('_mod_') or nombre in _NOMBRES_SUBMODULOS:
            return
        for submod in _SUBMODULOS_M11:
            if nombre in submod.__dict__:
                setattr(submod, nombre, valor)

    def __delattr__(self, nombre: str) -> None:
        super().__delattr__(nombre)
        for submod in _SUBMODULOS_M11:
            if nombre in submod.__dict__:
                delattr(submod, nombre)


_sys.modules[__name__].__class__ = _PaqueteM11
