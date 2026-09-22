# -*- coding: utf-8 -*-
"""
gui/app.py
==========
Interfaz grafica del expediente de alcantarillas. Reutiliza el patron de
`legacy/Tc.py`: Tkinter + ttkbootstrap, Notebook por pestanas, MarcoScroll y
Tooltip, los dos por `gui/componentes.py`, que desde el rediseño visual es
tambien el unico sitio donde vive el tema (paleta, tipografia y estilos con
nombre; ver mas abajo).

Que NO reutiliza este archivo, dicho porque el encabezado lo afirmaba (SIS-A-12)
---------------------------------------------------------------------------
El **campo validable** de `legacy/Tc.py` (`_campo_validable` + `_marcar`)
existe en el proyecto, pero no lo importa este archivo: vive en
`gui/componentes.CampoValidable` y lo usan la ventana emergente,
`gui/ventana_normativa.py`, que es donde la Sec. 4.3 pide validar AL
ESCRIBIR, y desde E-B los EDITORES TIPADOS de la pestaña 2,
`gui/editores.py` (E10): un editor por forma de `Criterio.forma` ---
escalar, par, serie de pares, dict con campos, serie de claves --- cuyos
campos son `CampoValidable` y cuyo contenido (que campos, con que ventana,
que filas de la tabla y que celda propone cada una) lo deriva
`src/editores.py` de la ficha. Los editores NO abren un segundo camino de
declaracion: COMPONEN el campo literal «Valor nuevo», que sigue siendo la
unica fuente del valor, y «Aplicar» lo arma entero y lo declara en UNA
llamada por `src.editores.declarar` --- que enruta a `declaracion.py` y
registra la procedencia: la fila elegida, o la nota que una adopcion
distinta exige ---, o no declara nada. Los campos de la pestaña 1 siguen
siendo `ttk.Entry` desnudos que se validan al pulsar EJECUTAR. De aquel
componente quedaba ademas un resto muerto --- `self.color_borde_ok`, el
color de fondo neutro que `_campo_validable` pintaba ---: se calculaba en
`_crear_interfaz` y no lo leia nadie. Retirado; el color neutro que el
componente necesita se lo pide hoy `CampoValidable` a su llamador.

No reimplementa el pipeline: llama a las mismas funciones que usa `cli.py`
(`cargar_datos_externos`, `correr`, `informe_json`, `exportar_html`,
`exportar_pdf`) para que la GUI y la linea de comandos vean siempre el mismo
expediente.

El tema (rediseño visual, bloque 1)
-----------------------------------
Como se ve la ventana se decide en UN sitio, `gui/componentes.py`: la
paleta con nombre (`FONDO`, `SUPERFICIE`, `AZUL`, `VERDE`, `AMBAR`, `ROJO` y
sus fondos suaves), la tipografia resuelta contra las fuentes instaladas
(`Tipografia`, IBM Plex si esta y la del sistema si no; monoespaciada para
numeros y claves) y los estilos ttk con nombre que `aplicar_tema` configura
antes de construir el primer widget. Este archivo pide estilos por su nombre
(`Fondo.TFrame`, `Titulo.TLabel`, `Res.TLabel`...) y componentes por su
clase --- `Panel` (plano, sin borde, titulo en mayusculas pequeñas),
`Insignia` (estado con TEXTO sobre fondo suave: el color acompaña, nunca
sustituye) y `TituloDeVista` («PASO n / 4», titulo y subtitulo, leidos de
`VISTAS`) --- y no escribe un solo color ni cuerpo de letra. Lo que Tk no
da y el estilo de referencia pide, se declara y no se simula: no hay radios
de 6-8 px ni sombras, porque un `tk.Button` y un `ttk.Frame` no los tienen.
La barra superior lleva el nombre del proyecto y las acciones principales,
y va EMPAQUETADA ANTES que el Notebook: hasta el bloque 1 iba despues, y en
la geometria por defecto (1100x800) el alto natural del Notebook la dejaba
fuera de la pantalla con el boton de EJECUTAR dentro.

Pestanas -- son CUATRO, y esta lista decia tres (SIS-A-10)
-----------------------------------------------------------
    1. Datos de entrada    CSV de Sec. 1.2 (M0) + datos declarados que no son
                            columna (los equivalentes de las banderas de
                            `cli.py`, AGRUPADOS por las familias que los usan
                            y anotados) + ALCANCE de la corrida + el panel
                            «Anticipo antes de correr» (G3, ver mas abajo) +
                            boton de ejecucion. Los dos campos de archivo
                            llevan su icono «i», que abre la AYUDA DERIVADA
                            (ver mas abajo).
    2. Criterios           Los criterios adoptados y su estado, con FILTRO
                            (por estado, por AMBITO, por FASE y por texto) y RECUENTO de
                            pendientes; la ventana normativa de cada variable
                            (Sec. 4.2/4.3 del plan); y el unico sitio de la
                            interfaz que REESCRIBE `criterios_adoptados.py`
                            --- accion permanente, aparte y con confirmacion
                            propia, que es justo la pestana que esta lista
                            omitia.
    3. Resultados por punto  Un Treeview con el resumen de cada punto y, al
                            seleccionar una fila, el detalle de verificaciones
                            y bloqueos de ese punto.
    4. Resumen             Estado del expediente, criterios pendientes que
                            bloquearon una etapa --- con QUIEN los resuelve y
                            con que EVIDENCIA, derivados de la ficha (E-B,
                            E13 reducido) ---, lo diferido por alcance,
                            exportacion (JSON/HTML/PDF/CSV) y la comparacion
                            de la corrida con otro `informe_json` (E14).

El alcance de la corrida (SIS-A-17)
-----------------------------------
`cli.py` acepta `--alcance perfil|expediente` desde hace tiempo y la ventana
no lo exponia: corria SIEMPRE «expediente», de modo que `memoria_perfil.html`
--- una de las dos plantillas del proyecto --- era inalcanzable desde la
interfaz y el nivel de perfil solo existia para quien usara la linea de
comandos. El selector de la pestana 1 lo expone, y la exportacion elige la
plantilla con `cli.plantilla_por_alcance`, que es la MISMA funcion que usa
`cli.main`: dos reglas para elegir plantilla serian dos memorias distintas
para la misma corrida.

Lo que se pone entre el proyectista y los 69 criterios
------------------------------------------------------
La pestana 2 lista los 69 criterios del archivo, 33 de ellos PENDIENTES. Tres
cosas la hacian dificil de usar, y las tres tienen la misma forma: informacion
que el programa TIENE y que no llegaba a la pantalla.

- **La fuente no cabia y no habia donde leerla.** Es el campo que dice de donde
  sale un valor --- la pregunta que la taxonomia de CLAUDE.md pone en el centro
  ---, tiene 280 caracteres de mediana y 4900 en el peor caso, y vivia en una
  columna de 300 px. Ninguna anchura arregla eso. El panel de detalle si podia,
  y tampoco: era un `Text` de `height=6` SIN barra de scroll, de modo que del
  criterio mas largo se veian 6 de sus 83 lineas y las otras 77 no eran
  alcanzables. Ahora la fuente encabeza el detalle, el detalle tiene scroll, y
  el reparto entre tabla y detalle es un `PanedWindow` que mueve el usuario.
- **No habia con que buscar.** 69 filas y ningun filtro: encontrar los
  pendientes era recorrerlas a ojo. Hay filtro por estado --- por el MISMO tag
  que devuelve `_estado_criterio`, no por un nombre paralelo --- y busqueda por
  clave o concepto, y arriba el recuento, que se calcula en el mismo recorrido
  que pinta las filas.
- **El programa pedia declarar lo que ya sabia que esta corrida no iba a
  invocar.** De los 33 pendientes, 22 son de Fase 8 y Fase 9 --- cabezal,
  licuefaccion, capacidad portante, aletas ---, que `--alcance perfil` ni
  ejecuta. El filtro de AMBITO los aparta, y sus dos ejes son DERIVADOS:
  «este alcance» es el que la pestana 1 ya declaro (`Criterio.nivel`, via
  `ca.criterios_del_alcance`), y «esta corrida» es el bloque «Criterios
  pendientes que bloquearon una etapa» del informe
  (`M11.criterios_bloqueantes`). Ninguno se elige a mano aqui, y ninguno
  calcula su propia respuesta. A perfil, la tabla pasa de 69 filas a 36 y los
  pendientes visibles de 33 a 11.
  FILTRAR NO ES OCULTAR: el recuento sigue contando los pendientes sobre los
  69 del archivo y dice ademas cuantas filas esconde el filtro. Un criterio
  que no se ve es un criterio que el proyectista no sabe que existe.
- **No se podia mirar la tabla en el orden en que se disena.** La fase es el
  orden mental del proyectista --- primero el periodo de retorno, despues la
  hidraulica, al final el cabezal --- y la tabla solo se dejaba recorrer por
  clave alfabetica. El filtro de FASE (G2) la corta por ese eje, y sus
  opciones son DERIVADAS: salen de `variables_entrada.variable(clave).fase`
  para las claves de `ca.CRITERIOS` (`_fases_del_censo`), nunca de una lista
  escrita aqui. Se compone con los otros tres filtros (Y logico) y el
  recuento sigue con la misma base: pendientes sobre el archivo entero,
  escondidos del filtro COMBINADO.
  Por fase y NO POR FAMILIA, y el orden de las dos decisiones importa: no
  existe hoy ninguna fuente derivable de que criterios aplica cada familia
  (los criterios no declaran familia), y una lista a mano criterio->familia
  seria la clase de clasificacion escrita que `Criterio.nivel` vino a
  erradicar. Si algun dia se quiere, se hace como se hizo `nivel`: midiendo
  corridas por familia (el molde es `tests/test_nivel_medido.py`). La razon
  completa esta en `docs/planes_mejora/01_PLAN_GUI.md`, seccion G2.
- **Un boton apagado no decia por que.** Ver `gui/componentes.BotonAccion`.

Que tiene que traer cada archivo: la ayuda DERIVADA (pestana 1)
---------------------------------------------------------------
El icono «i» de cada campo de archivo abre `gui/ayuda_entrada.py`: las 19
columnas del CSV con su concepto, su unidad, si pueden ir vacias y de donde
sale el dato; y las 8 claves que el JSON admite.

NINGUNA LINEA DE ESA AYUDA ESTA ESCRITA. Sale de `src/ayuda_entrada.py`, que
la deriva de `M0_carga.COLUMNAS` (que sale de los campos de `PuntoCritico`),
de `variables_entrada.VARIABLES`, de `M0_carga.VACIOS_ADMITIDOS` y de
`cli.CLAVES_EXTERNAS`. Una tabla de columnas escrita a mano no falla el dia
que se escribe: falla seis meses despues, cuando alguien anade una columna y
el proyectista llena su archivo siguiendo una ayuda que el propio programa ya
no cumple. `tests/test_ayuda_entrada.py` lo comprueba ANADIENDO una columna al
censo y viendo que la ayuda la recoge sola.

La ayuda del JSON esta a medias Y LO DICE: seis de las ocho claves no son
columna, ni dato de sitio, ni criterio --- no estan en ninguna de las tres
poblaciones del censo --- y su descripcion vive en prosa, en el docstring de
`cli.py`. Esa prosa no se parsea: un docstring no es una interfaz y se
reformatea sin que nada avise. De las seis se da lo que si es dato (el nombre
exacto y las familias que las usan) y se declara el hueco.

Los campos que este expediente no va a usar (pestana 1)
-------------------------------------------------------
La ventana pedia los cinco datos declarados a la vez, sin decir que dos de
ellos solo sirven para una familia --- eso estaba escrito, pero como PROSA en
un tooltip, que es la forma en que el programa no lo puede leer ---. Al cargar
el CSV, `cli.familias_del_csv` dice que familias trae el expediente y
`cli.familias_que_usan` que familias necesitan cada dato; los que no aplican
quedan ANOTADOS al lado.

Anotados, no deshabilitados, y no es un matiz de widget: el proyectista puede
estar preparando el dato de un punto que todavia no metio en el CSV, y un
campo apagado se lo impide mientras le dice que se equivoco. «No aplica»
tampoco quiere decir «es inerte»: en la Familia B, declarar `categoria_tr`
cambia el fundamento que la memoria imprime aunque el TR no se mueva, y por
eso esa familia SI figura entre las que lo usan --- lo dijo la medida, no la
lectura del codigo (`tests/test_familias_del_csv.py`).

Y desde G1 los campos ademas se AGRUPAN por esas mismas familias: «Comunes a
todas las familias» y una seccion por cada grupo de familias con campos
propios, con el conteo de puntos de cada familia en el encabezado. NINGUNA
asignacion campo->seccion esta escrita aqui: `_secciones_de_campos` la deriva
de `cli.familias_que_usan` --- la MISMA fuente que la anotacion ---, de modo
que mover una fila en `cli.FAMILIAS_QUE_USAN` mueve el campo de seccion sin
tocar esta ventana. Los rotulos visibles hablan en lenguaje de proyectista:
ninguna bandera de la CLI ni codigo de modulo (M0, M11) en una etiqueta ---
esa equivalencia vive en el tooltip de cada campo, y los codigos de modulo en
la barra de estado.

El anticipo antes de correr (pestana 1, G3)
-------------------------------------------
Hasta G3, los bloqueos solo se conocian DESPUES de ejecutar: el tablero de la
pestana 4 (`M11.criterios_bloqueantes`) se puebla post-corrida, y el filtro de
bloqueantes de la pestana 2 espera a que haya corrida. Ese diseño SE CONSERVA
--- es la verdad medida ---; lo que el panel «Anticipo antes de correr» ahorra
es el ciclo «correr para descubrir», con tres bloques que se refrescan al
cargar CSV y al cambiar el alcance, todos DERIVADOS por `src/anticipo.py`
(aqui solo se pintan): los criterios vacios que el alcance elegido puede
invocar (clic lleva a su fila en la pestana 2), el contraste de la cabecera
del CSV contra Sec. 1.2 --- solo cabecera y conteo de celdas vacias, por
`M0_carga.leer_cabecera`: la GUI no parsea el CSV por su cuenta ---, y lo que
el alcance difiere, leido de los dos diccionarios de `cli` que la propia
corrida consulta.

ES UNA ESTIMACION Y EL PANEL LO DICE, con su linea fija
(`anticipo.AVISO_DEL_ANTICIPO`): la invocacion real de un criterio depende de
la ruta que tome cada punto. Por eso el boton de EJECUTAR NUNCA se
deshabilita por el anticipo --- correr siempre se puede; el pipeline
convierte cada falta en un Bloqueo declarado ---.

Los criterios en la sesion (SIS-A-18)
-------------------------------------
La sesion JSON guardaba el proyecto, el CSV y las cinco banderas, y NO las
declaraciones de la corrida. Quien declaraba cinco criterios y volvia al dia
siguiente recuperaba el nombre del archivo y perdia las cinco decisiones sin
un aviso. Ahora se guardan y se restauran los valores Y SU PROCEDENCIA, por
`declaracion.restaurar_sesion`, que repone por el mismo camino con guardia que
usan la ventana y la CLI. Lo que la guardia rechace se muestra: una sesion es
un archivo que alguien pudo editar a mano.

ABRIR UNA SESION SUSTITUYE; IMPORTAR SUMA (EXT-4, EXT-A-02). «Cargar sesion»
llama a `restaurar_sesion(sustituir=True)`: vacia todo lo declarado en el
proceso --- la obra anterior --- y vuelca solo lo que la sesion trae y la
guardia acepta, diciendo que se retiro. Hasta EXT-4 era aditiva, y abrir la
obra B tras declarar en la obra A dejaba las claves de A vivas y las guardaba
en la sesion de B. «Importar decisiones» es el otro boton, con
`sustituir=False`. Y la sesion se VALIDA ENTERA antes de tocar un solo
`StringVar` (`errores_de_sesion`, PC-16): un archivo con `"externos": null`
reventaba con `AttributeError` fuera del manejador, con proyecto y CSV ya
pisados. Un externo que la sesion no trae se repone a la cadena vacia, no se
queda con el de la sesion anterior.

El informe es de SU corrida (EXT-4, PC-15)
-------------------------------------------
`self.informe` describe la corrida que lo produjo, con su `ContextoCorrida`
dentro; lo que se declare, se quite o se cargue DESPUES no lo cambia --- y por
eso mismo el informe deja de describir el estado de la ventana ---.
`_invalidar_informe` lo retira y apaga los cuatro exportadores diciendo por
que, y lo llaman los cuatro gestos que cambian el estado (declarar, quitar,
escribir en archivo, cargar sesion) y el propio EJECUTAR antes de correr: una
corrida fallida no deja el informe anterior como vigente en las pestañas 3 y
4 ni en la barra. El nombre del proyecto se lee AL CORRER, no al exportar, por
la misma razon. Y `root.report_callback_exception` convierte en dialogo lo
que Tk mandaba a stderr con la ventana como si nada.
"""

from __future__ import annotations

import ast
import tempfile
import traceback
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

RAIZ = Path(__file__).resolve().parent.parent
# La ventana se lanza desde la raiz con `python -m gui.app` (README), que es
# lo que pone la raiz en el path: desde EXT-9 no hay `sys.path.insert` y los
# modulos del calculador se importan del paquete `src` (PC-08).
import json

from src import anticipo as antc
import cli
from src import criterios_adoptados as ca
from src import comparador as compa
from src import declaracion as dec
from src import editores as sed
from src import variables_entrada as ve
from src.modelos import Derivada, ErrorProyecto, Familia
# Solo para PREGUNTARLE si weasyprint cargo (`_ayuda_del_pdf`). No se le pide
# ningun calculo: la exportacion sigue pasando por `cli.exportar_pdf`, que es
# la misma puerta que usa la linea de comandos.
from src.modulos import M11_reporte as M11
# La traza de procedencia por punto (G4). El CONTENIDO lo produce
# `src/traza_punto.py` --- que pasos, en que orden, con que rotulos y en cual
# de los tres registros tipograficos va cada linea ---; aqui solo se pinta.
# Mismo reparto que `ventana_normativa`, y por las mismas razones.
from src import traza_punto as tp

# `ayuda_ent` y no `ayuda`: `ayuda` es el nombre de la variable de bucle de
# CAMPOS_EXTERNOS, en `_construir_tab_datos`, que es la MISMA funcion donde
# se crean los dos iconos. Con el alias corto, Python trata `ayuda` como
# local de esa funcion y la lambda del icono acabaria pidiendole
# `.PESTANA_CSV` a la ultima cadena de tooltip del bucle --- un
# AttributeError al pulsar, no al arrancar. Lo encontro `pyflakes`.
from src import sesion as ses
from gui import ayuda_entrada as ayuda_ent  # noqa: E402
from gui import editores as ged  # noqa: E402
from gui import exportacion_pdf as expdf  # noqa: E402
from gui import ventana_normativa as ventana_norma  # noqa: E402
from gui import componentes as comp  # noqa: E402
from gui.componentes import (COLOR_AVISO, COLOR_ERROR,  # noqa: E402
                             COLOR_OK, BotonAccion, BotonAyuda, Insignia,
                             MarcoScroll, Panel, TituloDeVista, Tooltip,
                             interpretar_texto_declarado)

try:
    import ttkbootstrap as tb
except ImportError:
    tb = None

APP_VERSION = "1.0"
# EL FORMATO DE LA SESION VIVE EN `src/sesion.py` DESDE EXT-8 (PC-11): la
# CLI lo lee (`--sesion`) para escribir el PDF en un subproceso, y dos
# esquemas --- uno por puerta --- divergirian. Aqui se reexportan con los
# nombres de siempre, que son los que la suite y `tests/apoyo/` usan.
FORMATO_SESION = ses.FORMATO_SESION
ESQUEMA_SESION = ses.ESQUEMA_SESION
errores_de_sesion = ses.errores_de_sesion

# Los motivos por los que un boton esta apagado. Son DATO y no cadenas sueltas
# en el sitio donde se apaga cada uno: un motivo escrito junto a su condicion
# se copia mal la segunda vez que hace falta, y el usuario acaba leyendo dos
# explicaciones distintas del mismo bloqueo. `BotonAccion` los exige --- el
# motivo no es opcional --- por la misma razon por la que un criterio [A] sin
# valor lanza excepcion en vez de tomar un defecto: un bloqueo se declara.
MOTIVO_SIN_CRITERIO = "no hay ningun criterio seleccionado en la tabla"
MOTIVO_NO_DECLARADO = "el criterio no esta declarado para esta corrida"
# El criterio que NO SE ELIGE (EXT-V-04, la mitad de la pestaña 2): su valor
# lo deriva el programa de otras variables ya declaradas, y pisarlo por aqui
# pondria en la memoria una tabla que la fuente no imprime. La ventana
# normativa lo rotula «NO EDITABLE» y el nucleo lo rechaza con ValueError;
# esta pestaña, hasta EXT-5, encendia los dos botones que escriben y pedia
# confirmar una escritura permanente que no iba a ocurrir. El motivo se arma
# con `_motivo_derivado` para nombrar de que se deriva.
MOTIVO_DERIVADO = "se deriva de {de}; edite sus entradas (regla: {regla})"
MOTIVO_SIN_CORRIDA = "todavia no se ejecuto el pipeline: no hay informe que exportar"
# El PDF sale en un proceso aparte (EXT-8, PC-11): mientras corre, el boton
# esta apagado y lo dice --- y el progreso se ve en el rotulo de al lado ---.
MOTIVO_EXPORTANDO_PDF = "el PDF se esta escribiendo en un proceso aparte"
# Cada cuanto se sondea el proceso hijo, en ms. Es cadencia de interfaz, no
# un valor del expediente: mas corto no acelera nada, mas largo retrasa lo
# que el usuario ve.
CADENCIA_SONDEO_PDF_MS = 250   # literal-ok: cadencia del sondeo del subproceso, ms
MOTIVO_EJECUTANDO = "la corrida esta en marcha"
MOTIVO_SIN_PUNTO = "seleccione un punto en la tabla de arriba"
# Los dos motivos con que un informe deja de estar vigente (EXT-4, PC-15).
# El primero es el de los cuatro gestos que cambian el estado declarado; el
# segundo, el de una corrida que no llego a producir informe.
MOTIVO_INFORME_DESACTUALIZADO = (
    "el informe de la ultima corrida ya no describe el estado actual: se "
    "declaro, se quito o se cargo una sesion despues de correr. Vuelva a "
    "ejecutar el calculo")
MOTIVO_CORRIDA_FALLIDA = (
    "la ultima corrida no produjo informe: corrija la entrada y vuelva a "
    "ejecutar el calculo")

# Los filtros de estado de la tabla de criterios (pestana 2). Cada entrada es
# (rotulo, tag), y el `tag` es el MISMO que devuelve `_estado_criterio`: filtrar
# por un nombre propio seria una segunda regla de estado, y dos reglas de estado
# son dos tablas que pueden decir cosas distintas de la misma fila.
FILTROS_DE_ESTADO = (
    ("Todos", None),
    ("Solo PENDIENTES", "pendiente"),
    ("Declarados en esta corrida", "declarado_corrida"),
    ("PISADOS en esta corrida", "pisado_corrida"),
    ("Resueltos en el archivo", "resuelto"),
)

# Los filtros de AMBITO de la tabla de criterios (pestana 2). Responden a una
# pregunta distinta de la del estado --- aquel dice como esta un criterio,
# este dice si ESTA CORRIDA lo puede necesitar --- y por eso son dos combos y
# no uno solo con las siete opciones mezcladas.
#
# NINGUNO DE LOS TRES SE ELIGE A MANO EN ESTA PESTANA, y ese es todo el
# diseño: el segundo lee el alcance que la pestana 1 ya declaro, y el tercero
# lee el informe de la ultima corrida. Un desplegable donde el proyectista
# eligiera "perfil" aqui mientras la pestana 1 dice "expediente" seria una
# segunda declaracion de alcance, y dos declaraciones de alcance son dos
# corridas distintas descritas como una.
#
# LOS DOS PRIMEROS ESTIMAN Y EL TERCERO MIDE, y la diferencia importa al
# leerlos: "este alcance puede invocarlo" sale de `Criterio.nivel`, que dos
# corridas comprueban en `tests/test_nivel_medido.py` pero que sigue siendo
# una clasificacion previa; "bloqueo esta corrida" sale de
# `M11.criterios_bloqueantes`, que es el registro de lo que de verdad paso.
AMBITO_TODOS = "todos"
AMBITO_ALCANCE = "alcance"
AMBITO_BLOQUEANTES = "bloqueantes"

FILTROS_DE_AMBITO = (
    ("Todos", AMBITO_TODOS),
    ("Solo los que este alcance puede invocar", AMBITO_ALCANCE),
    ("Solo los que bloquearon esta corrida", AMBITO_BLOQUEANTES),
)

MOTIVO_SIN_CORRIDA_FILTRO = (
    "todavia no se ejecuto el pipeline: no hay corrida cuyos bloqueos filtrar")

# El filtro de FASE de la tabla de criterios (pestana 2, G2). Cuarta pregunta,
# distinta de las otras tres: el estado dice como esta un criterio, el ambito
# si esta corrida lo puede necesitar, el texto donde esta --- y la fase dice
# EN QUE MOMENTO DEL DISEÑO se usa, que es el orden en que el proyectista
# piensa el expediente. La unica opcion escrita aqui es el rotulo de "sin
# filtro"; las fases mismas las da el censo (`_fases_del_censo`).
FILTRO_FASE_TODAS = "Todas"


def _fases_del_censo():
    """
    Las opciones del filtro de fase, DERIVADAS del censo: la fase de cada una
    de las claves de `criterios_adoptados.CRITERIOS` segun
    `variables_entrada.variable(clave).fase`, sin repetir y ordenadas.

    NINGUNA FASE SE ESCRIBE EN ESTE ARCHIVO, y es la misma regla que gobierna
    los dos ejes del filtro de ambito: una lista de fases escrita en la GUI
    estaria bien el dia que se escribe y mentiria el dia que el censo mueva
    una variable de fase --- que es exactamente lo que S21 midio en
    `variables_entrada._consumo_por_modulo` ---. El texto de cada opcion es la
    fase TAL COMO EL CENSO LA DICE, compuesta incluida ("Fase 3 ... · Fase 5
    ..."): partirla aqui seria una segunda regla sobre el separador, y la
    variable que dos fases consumen aparece con las dos, que es lo cierto.
    """
    return sorted({ve.variable(clave).fase for clave in ca.CRITERIOS})

# Banderas globales que acepta `cli.py` fuera del CSV (ver docstring de
# `cli.py`, seccion "Datos que NO estan en el CSV"). Cada tupla es
# (clave, etiqueta, ayuda, unidad).
#
# LA ETIQUETA NO NOMBRA BANDERAS NI FAMILIAS, y las dos ausencias son
# deliberadas (G1): la equivalencia con la bandera de la CLI es informacion
# de tooltip --- quien mira la ventana no teclea `--luz` ---, y la familia
# que usa cada dato ya no se ESCRIBE en ninguna cadena: la dice la SECCION
# donde el campo aparece, que `_secciones_de_campos` deriva de
# `cli.familias_que_usan`. La version anterior la escribia a mano y mentia:
# «Categoria TR (Familia A)» sobre un dato que la medida atribuye a las
# familias A y B (`tests/test_familias_del_csv.py`).
CAMPOS_EXTERNOS = (
    ("luz_m", "Luz del cruce:",
     "Luz del cruce, en METROS (Sec. 2.1).\n"
     "Sin ella no se puede separar alcantarilla de puente\n"
     "y el punto no se dimensiona.\n"
     "Equivale a la bandera --luz de la linea de comandos.", "[m]"),
    ("TW_m", "Tirante en el receptor (TW):",
     "Tirante en el receptor sobre el fondo de la salida, en METROS.\n"
     "Si no se declara se pide al criterio 'TW_receptor'.\n"
     "Equivale a la bandera --tw de la linea de comandos.", "[m]"),
    ("longitud_m", "Longitud del conducto:",
     "Longitud del conducto, en METROS.\n"
     "Si no se declara la calcula M7 (Sec. 7.B).\n"
     "Equivale a la bandera --longitud de la linea de comandos.", "[m]"),
    ("l_hidraulico", "L hidráulico de la cuneta:",
     "Longitud a la que la cuneta agota su capacidad, en METROS\n"
     "(Fase 10, Sec. 10).\n"
     "Equivale a la bandera --l-hidraulico de la linea de comandos.", "[m]"),
    ("categoria_tr", "Categoría del TR (Tabla N.º 02):",
     "Fila de la Tabla N 02: 'quebrada_importante' o 'quebrada_menor'\n"
     "(Sec. 2.2). Sin ella la Familia A se detiene en el umbral de area.\n"
     "Equivale a la bandera --categoria-tr de la linea de comandos.", ""),
)

# LAS CUATRO VISTAS, con el titulo y el subtitulo que encabezan cada pestaña
# («PASO n / 4», titulo, subtitulo). El numero de paso es la POSICION en esta
# tupla y el total su longitud: ninguno se escribe dos veces. El texto de la
# pestaña del Notebook es el mismo titulo, precedido del numero.
VISTAS = (
    ("Datos de entrada",
     "El CSV de puntos criticos, los datos que no son columna, el alcance de "
     "la corrida y el anticipo de lo que va a faltar."),
    ("Criterios",
     "Los criterios adoptados y su estado; aqui se declaran los pendientes, "
     "solo para esta corrida o en el archivo."),
    ("Resultados por punto",
     "Una fila por punto de la ultima corrida y, al seleccionarla, sus "
     "verificaciones y bloqueos."),
    ("Resumen",
     "El estado del expediente, los criterios que bloquearon una etapa y la "
     "exportacion de la memoria."),
)

# El texto del boton de ejecucion, UNA vez: se restaura en dos sitios despues
# de correr y una tercera copia divergiria. Sin codigos de modulo (G1): que
# la corrida ejecuta M0 a M10 lo dicen su tooltip y la barra de estado.
TEXTO_BOTON_EJECUTAR = "EJECUTAR EL CÁLCULO"


class ExpedienteApp:
    def __init__(self, root):
        self.root = root
        # Sin «M0 a M10» en el titulo (G1): es lenguaje de modulos internos,
        # no de proyectista. El dato no se pierde: vive en la barra de estado.
        self.root.title("Expediente de Alcantarillas")
        self.root.geometry("1100x800")
        self.root.minsize(900, 620)

        self.proyecto_var = tk.StringVar()
        self.csv_var = tk.StringVar()
        self.datos_externos_var = tk.StringVar()
        # El JSON de datos de sitio [S] de la obra (EXT-10, EXT-V-01): hermano
        # del de datos externos. Vacio, gobiernan los de datos_sitio.py.
        self.datos_sitio_var = tk.StringVar()
        # LA IDENTIDAD DE LA SESION Y SUS CORRIDAS (E04): la sesion es el
        # unico lugar del «proyecto actual». El id nace con la ventana (una
        # sesion vacia) y se sustituye al cargar otra; cada corrida que
        # termina se guarda con su `informe_json` embebido.
        sesion_inicial = ses.sesion_vacia(APP_VERSION)
        self.sesion_id = sesion_inicial["id"]
        self.corridas = list(sesion_inicial["corridas"])
        # El bloque `sitio` de la sesion abierta: es lo que gobierna cuando
        # el campo «JSON de datos de sitio» esta vacio (auditoria adversarial
        # de EXT-10: borrar el campo tiene que retirar lo que la ruta trajo).
        self.sitio_de_la_sesion = dict(sesion_inicial["sitio"])
        self.externos_vars = {clave: tk.StringVar() for clave, *_r in CAMPOS_EXTERNOS}
        # El defecto es el MISMO que el de `cli.py` (`--alcance`, choices con
        # default `expediente`), y se lee de alli en vez de escribirse otra
        # vez: dos defectos que puedan divergir son dos programas.
        self.alcance_var = tk.StringVar(value=cli.ALCANCE_EXPEDIENTE)

        self.informe: Optional[cli.Informe] = None
        self.entradas_de_la_corrida = {}
        # El nombre del proyecto CON QUE SE CORRIO, leido al ejecutar y no al
        # exportar (PC-15): la memoria describe la corrida, no el campo.
        self.proyecto_de_la_corrida = ""
        # Una excepcion dentro de un callback de Tk salia a stderr y la
        # ventana seguia como si nada (PC-16). Se convierte en dialogo, con
        # la traza impresa igual para quien reporte el defecto.
        self.root.report_callback_exception = self._excepcion_en_callback
        # Las familias que el CSV cargado trae. `None` --- y no una tupla
        # vacia --- mientras no se haya podido leer: "no se sabe" y "no hay
        # ninguna" son dos cosas distintas, y anotar "no aplica" sobre la
        # segunda cuando en realidad es la primera seria decirle al
        # proyectista que un campo le sobra sin haber leido su archivo.
        self.familias_csv: Optional[tuple] = None
        # Y el conteo por familia del mismo CSV, con la misma semantica del
        # `None`: "no se sabe" no es "cero puntos".
        self.puntos_familia: Optional[dict] = None

        self._crear_interfaz()

        # El filtro de alcance de la pestana 2 no es una copia del selector de
        # la pestana 1: es el MISMO dato. Sin este `trace` la tabla se quedaba
        # filtrando por el alcance anterior hasta el proximo repintado, que es
        # justo la clase de desfase que hace desconfiar de un filtro.
        # Y el ANTICIPO se repinta con el mismo gesto (G3): sus bloques 1 y 3
        # dependen del alcance, y un anticipo que describe el alcance anterior
        # es la clase de desfase que este panel existe para evitar.
        self.alcance_var.trace_add(
            "write", lambda *_a: (self._refiltrar(), self._pintar_anticipo()))
        # Y la anotacion de la pestana 1 se rehace al cambiar el CSV, que es
        # cuando cambian las familias del expediente (el anticipo tambien:
        # `_releer_familias` termina repintandolo).
        self.csv_var.trace_add("write", lambda *_a: self._releer_familias())
        # El bloque 4 del anticipo (PF-2) depende ademas del JSON de datos
        # externos y de las banderas de esta pestaña: sin estas trazas se
        # quedaba viejo hasta tocar el CSV o el alcance (auditor de PF-2).
        self.datos_externos_var.trace_add("write", lambda *_a: self._pintar_anticipo())
        for _var in self.externos_vars.values():
            _var.trace_add("write", lambda *_a: self._pintar_anticipo())

    def _excepcion_en_callback(self, tipo, valor, tb):
        traceback.print_exception(tipo, valor, tb)
        messagebox.showerror("Error inesperado", f"{tipo.__name__}: {valor}")

    # ------------------------------------------------------------------
    # El informe vigente y su invalidacion (EXT-4, PC-15)
    # ------------------------------------------------------------------
    def _apagar_exportadores(self, motivo):
        for btn in (self.btn_json, self.btn_html, self.btn_pdf, self.btn_csv,
                    self.btn_comparar):
            btn.deshabilitar(motivo)

    def _invalidar_informe(self, motivo):
        """
        Retira el informe de la ultima corrida y apaga los exportadores
        diciendo por que. Sin informe no hay nada que invalidar.
        """
        if self.informe is None:
            return
        self.informe = None
        self._apagar_exportadores(motivo)
        self._vaciar_tablas_del_informe(motivo)

    def _vaciar_tablas_del_informe(self, motivo):
        """Las pestañas 3 y 4 y la barra dejan de mostrar la corrida anterior."""
        for arbol in (self.tree_puntos, self.tree_criterios):
            for item in arbol.get_children():
                arbol.delete(item)
        self.txt_detalle.configure(state="normal")
        self.txt_detalle.delete("1.0", "end")
        self.txt_detalle.configure(state="disabled")
        self.btn_traza.deshabilitar(MOTIVO_SIN_PUNTO)
        for lbl in self.lbl_resumen.values():
            if isinstance(lbl, Insignia):
                lbl.configurar("-", comp.INSIGNIA_NEUTRA)
            else:
                lbl.config(text="-", foreground="")
        self.lbl_estado.config(text=f"Sin informe vigente: {motivo}.")

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def _crear_interfaz(self):
        if tb is not None:
            try:
                self.style = tb.Style(theme="litera")
            except Exception:
                self.style = ttk.Style()
        else:
            self.style = ttk.Style()
            if "clam" in self.style.theme_names():
                self.style.theme_use("clam")
        # EL TEMA, UNA VEZ Y ANTES DE CUALQUIER WIDGET: `aplicar_tema` deja
        # configurados los estilos con nombre que las cuatro pestañas piden
        # (`gui/componentes.py`) y resuelve la tipografia contra las fuentes
        # instaladas, que es lo que `BotonAccion` y los `tk.Text` leen al
        # construirse. Ningun color ni cuerpo de letra se decide en este
        # archivo.
        self.tipografia = comp.aplicar_tema(self.style, self.root)

        contenedor = ttk.Frame(self.root, style="Fondo.TFrame")
        contenedor.pack(fill="both", expand=True)

        # LA BARRA SUPERIOR Y LA DE ESTADO SE EMPAQUETAN ANTES QUE EL
        # NOTEBOOK, y no es estilo: `pack` reparte el alto en orden, y la
        # barra de acciones --- con el boton de EJECUTAR --- iba DESPUES del
        # Notebook, cuyo alto natural (medido: 1002 px, el de la pestaña 2)
        # supera el de la ventana por defecto (800 px). En esa geometria la
        # barra entera quedaba fuera de la pantalla y el boton principal no
        # se veia. Empaquetadas primero, arriba y abajo, no se pueden
        # desplazar: el que cede es el Notebook, que tiene scroll.
        self._construir_barra_superior(contenedor)
        self._construir_barra_de_estado(contenedor)

        self.nb = ttk.Notebook(contenedor)
        self.nb.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        # LA PESTAÑA 2 TAMBIEN SE DESPLAZA, como la 1 y la 4, y es una medida
        # del bloque 1 del rediseño y no una eleccion: con la cabecera de la
        # vista, los cuatro paneles y el editor tipado montado, la columna
        # unica de la pestaña pide mas alto del que tiene una ventana de
        # 1000 px, y en una geometria fija el que cedia era el `PanedWindow`
        # de la tabla, que llegaba a quedarse sin una sola fila visible. El
        # bloque 2 (tabla con el detalle a la derecha) devuelve la vista a
        # una sola pantalla; hasta entonces, la tabla conserva sus filas y
        # lo que no cabe se alcanza con la rueda.
        self.tab_datos = MarcoScroll(self.nb)
        self.tab_criterios = MarcoScroll(self.nb)
        self.tab_puntos = ttk.Frame(self.nb, style="Fondo.TFrame")
        self.tab_resumen = MarcoScroll(self.nb)
        pestanas = (self.tab_datos, self.tab_criterios, self.tab_puntos,
                    self.tab_resumen)
        rotulo = {pestana: f"  {n}. {titulo}  "
                  for n, (pestana, (titulo, _sub))
                  in enumerate(zip(pestanas, VISTAS), start=1)}
        self.nb.add(self.tab_datos, text=rotulo[self.tab_datos])
        self.nb.add(self.tab_criterios, text=rotulo[self.tab_criterios])
        self.nb.add(self.tab_puntos, text=rotulo[self.tab_puntos])
        self.nb.add(self.tab_resumen, text=rotulo[self.tab_resumen])

        self._construir_tab_datos(self.tab_datos.interior)
        self._construir_tab_criterios(self.tab_criterios.interior)
        self._construir_tab_puntos(self.tab_puntos)
        self._construir_tab_resumen(self.tab_resumen.interior)

        # Control-Return ejecuta desde cualquier campo (EXT-8, PC-17): la
        # accion principal de la ventana tiene atajo, y el mismo `command`
        # del boton, para que las dos puertas hagan exactamente lo mismo.
        self.root.bind("<Control-Return>", lambda _evt: self.ejecutar_pipeline())

    def _cabecera_de_vista(self, master, pestana):
        """
        La cabecera «PASO n / 4», titulo y subtitulo de `pestana`, leida de
        `VISTAS` por la POSICION de la pestaña en el Notebook: el numero de
        paso no se escribe en ningun sitio. La devuelve sin empaquetar: cada
        pestaña la coloca segun su geometria (`pack` o `grid`).
        """
        indice = self.nb.index(pestana)
        titulo, subtitulo = VISTAS[indice]
        return TituloDeVista(master, indice + 1, len(VISTAS), titulo, subtitulo)

    def _construir_barra_superior(self, contenedor):
        """
        La barra compacta de arriba: el nombre del proyecto --- el que se
        teclea en la pestaña 1, leido de la misma variable --- y las acciones
        principales de la ventana, con EJECUTAR a la derecha.
        """
        barra = ttk.Frame(contenedor, style="Fondo.TFrame", padding=(12, 10, 12, 8))
        barra.pack(side="top", fill="x")
        self.lbl_proyecto = ttk.Label(barra, text="", style="Proyecto.TLabel")
        self.lbl_proyecto.pack(side="left", padx=(0, 16))
        self.proyecto_var.trace_add("write", lambda *_a: self._pintar_nombre_del_proyecto())
        self._pintar_nombre_del_proyecto()

        self.btn_ejecutar = BotonAccion(
            barra, TEXTO_BOTON_EJECUTAR, letra=BotonAccion.GRANDE,
            fondo=comp.AZUL, activebackground=comp.AZUL_OSCURO,
            activeforeground="white",
            command=self.ejecutar_pipeline,
            ayuda="Corre el pipeline completo (M0 -> M10) con el CSV, los\n"
                  "datos externos y el alcance elegidos en la pestaña 1.\n"
                  "Atajo: Control+Intro.",
        )
        self.btn_ejecutar.pack(side="right", padx=(8, 0), ipadx=12, ipady=4)
        # «Nuevo proyecto» es como se crea OTRA obra sobre el mismo
        # despliegue (EXT-10): se carga una sesion vacia, nunca se vacia
        # datos_sitio.py ni criterios_adoptados.py.
        for texto, comando in (("Nuevo proyecto", self.nuevo_proyecto),
                               ("Guardar sesion", self.guardar_sesion),
                               ("Cargar sesion", self.cargar_sesion),
                               ("Importar decisiones", self.importar_decisiones)):
            ttk.Button(barra, text=texto, command=comando).pack(side="left", padx=(0, 6))

    def _construir_barra_de_estado(self, contenedor):
        """
        La barra de estado, abajo. Es el sitio de los codigos de modulo (G1):
        aqui pueden leerse sin colarse en las etiquetas de los campos.
        """
        pie = ttk.Frame(contenedor, style="Fondo.TFrame", padding=(12, 4, 12, 8))
        pie.pack(side="bottom", fill="x")
        self.lbl_estado = ttk.Label(pie, text="Sin ejecutar (módulos M0 a M10).",
                                    style="Estado.TLabel")
        self.lbl_estado.pack(side="left")

    def _pintar_nombre_del_proyecto(self):
        """El nombre tecleado en la pestaña 1; sin el, el titulo de la ventana."""
        nombre = self.proyecto_var.get().strip()
        self.lbl_proyecto.config(text=nombre or self.root.title())

    # -------------------------- Pestana 1 -----------------------------
    def _construir_tab_datos(self, p):
        self._cabecera_de_vista(p, self.tab_datos).pack(anchor="w", fill="x", pady=(0, 12))
        panel_proyecto = Panel(p, "Proyecto y CSV")
        panel_proyecto.pack(fill="x", pady=(0, 10))
        f_proj = panel_proyecto.interior
        f_proj.columnconfigure(1, weight=1)

        ttk.Label(f_proj, text="Nombre del proyecto:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        ent_proy = ttk.Entry(f_proj, textvariable=self.proyecto_var)
        ent_proy.grid(row=0, column=1, sticky="we", padx=5, pady=4, columnspan=2)
        Tooltip(ent_proy, "Encabeza la memoria de calculo (M11).")

        ttk.Label(f_proj, text="CSV de puntos críticos (Sec. 1.2):").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        ent_csv = ttk.Entry(f_proj, textvariable=self.csv_var)
        ent_csv.grid(row=1, column=1, sticky="we", padx=5, pady=4)
        f_csv = ttk.Frame(f_proj)
        f_csv.grid(row=1, column=2, sticky="w", padx=5)
        ttk.Button(f_csv, text="Examinar...", command=self._elegir_csv).pack(side="left")
        # EL ICONO VA AL LADO DEL CAMPO QUE EXPLICA, no en un menu de ayuda:
        # la pregunta «que columnas lleva esto» se hace mirando el campo, y una
        # ayuda que hay que ir a buscar es una ayuda que no se lee.
        BotonAyuda(
            f_csv, lambda: self._abrir_ayuda(ayuda_ent.PESTANA_CSV),
            "Que columnas tiene que traer el CSV, con su concepto, su unidad,\n"
            "si puede ir vacia y de donde sale el dato. La lista NO esta escrita:\n"
            "se deriva de M0_carga.COLUMNAS y de variables_entrada.py, de modo\n"
            "que no puede quedarse vieja. Incluye la cabecera exacta, copiable."
        ).pack(side="left", padx=(6, 0))

        ttk.Label(f_proj, text="JSON de datos externos (opcional):").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        ent_ext = ttk.Entry(f_proj, textvariable=self.datos_externos_var)
        ent_ext.grid(row=2, column=1, sticky="we", padx=5, pady=4)
        f_ext_botones = ttk.Frame(f_proj)
        f_ext_botones.grid(row=2, column=2, sticky="w", padx=5)
        ttk.Button(f_ext_botones, text="Examinar...",
                   command=self._elegir_datos_externos).pack(side="left")
        BotonAyuda(
            f_ext_botones, lambda: self._abrir_ayuda(ayuda_ent.PESTANA_JSON),
            "Las claves que el JSON admite y la forma del archivo.\n"
            "AYUDA A MEDIAS Y LO DICE: seis de las ocho claves no estan en el\n"
            "censo de variables_entrada.py --- no son columna, ni dato de sitio,\n"
            "ni criterio --- y de ellas solo se puede derivar el nombre y las\n"
            "familias que las usan. Su descripcion sigue en el docstring de\n"
            "cli.py, y esta ventana no lo copia a proposito."
        ).pack(side="left", padx=(6, 0))
        Tooltip(ent_ext, "JSON con secciones 'globales' y/o 'puntos', igual que\n"
                         "el '--datos-externos' de cli.py. Una bandera de abajo\n"
                         "pisa al valor global de este archivo.")

        # LOS DATOS DE SITIO [S] DE OTRA OBRA (EXT-10, EXT-V-01): clon de la
        # fila del JSON de datos externos. Vacio, gobiernan los del archivo
        # datos_sitio.py --- la obra del repositorio --- y la memoria lo dice.
        ttk.Label(f_proj, text="JSON de datos de sitio (opcional):").grid(
            row=3, column=0, sticky="w", padx=5, pady=4)
        ent_sitio = ttk.Entry(f_proj, textvariable=self.datos_sitio_var)
        ent_sitio.grid(row=3, column=1, sticky="we", padx=5, pady=4)
        f_sitio_botones = ttk.Frame(f_proj)
        f_sitio_botones.grid(row=3, column=2, sticky="w", padx=5)
        ttk.Button(f_sitio_botones, text="Examinar...",
                   command=self._elegir_datos_sitio).pack(side="left")
        Tooltip(ent_sitio, "JSON con los datos de sitio [S] de ESTA obra, por clave:\n"
                           "{\"PGA_roca_B\": {\"valor\": 0.30, \"trazabilidad\": \"...\",\n"
                           "\"fecha\": \"AAAA-MM-DD\"}, ...}, igual que el\n"
                           "'--datos-sitio' de cli.py. Se declaran SOLO para la corrida,\n"
                           "por la misma guardia que datos_sitio.py (que no se toca);\n"
                           "la memoria imprime de que archivo salio cada [S]. Vacio,\n"
                           "gobiernan los del archivo: la obra del repositorio.")

        self.lbl_error_datos = ttk.Label(f_proj, text="", style="Error.TLabel",
                                         wraplength=820, justify="left")
        self.lbl_error_datos.grid(row=4, column=0, columnspan=3, sticky="w",
                                  padx=5, pady=(6, 0))

        panel_datos = Panel(p, "Datos declarados (no son columna del CSV)")
        panel_datos.pack(fill="x", pady=(0, 10))
        p = panel_datos.interior
        # El texto visible no nombra banderas de la CLI (G1): la equivalencia
        # exacta de cada campo vive en su tooltip, que es donde se lee al
        # preguntarse por ESE campo.
        ttk.Label(p, text="Se aplican a todos los puntos de la corrida; la ayuda de "
                          "cada campo dice a qué opción de la línea de comandos "
                          "equivale. Un valor por punto solo puede declararse en el "
                          "JSON de datos externos. Cada campo aparece bajo las "
                          "familias que lo usan; el de una familia que el CSV no "
                          "trae queda anotado, nunca bloqueado.",
                  style="Ayuda.TLabel", wraplength=820, justify="left").pack(anchor="w", pady=(0, 8))

        # La anotacion «no aplica» de cada campo. Es una etiqueta al lado y NO
        # un `state="disabled"`, y la diferencia es del oficio y no del
        # widget: el proyectista puede estar preparando el dato de un punto
        # que todavia no ha metido en el CSV, y un campo apagado le impide
        # hacerlo mientras le dice que se equivoco. Anotar informa; deshabilitar
        # decide por el.
        self.lbl_no_aplica = {}
        # Los encabezados de seccion de familia, para repintarles el conteo de
        # puntos al cambiar el CSV. Clave: la tupla de familias de la seccion.
        self.lbl_seccion_familia = {}
        for familias, campos in self._secciones_de_campos():
            f_titulo = ttk.Frame(p)
            f_titulo.pack(fill="x", pady=(6, 0))
            ttk.Label(f_titulo, text=self._titulo_seccion(familias),
                      style="Header.TLabel").pack(side="left")
            if familias != tuple(Familia):
                lbl = ttk.Label(f_titulo, text="— puntos", style="Ayuda.TLabel")
                lbl.pack(side="left", padx=(10, 0))
                self.lbl_seccion_familia[familias] = lbl
            f_ext = ttk.Frame(p)
            f_ext.pack(fill="x", pady=(0, 6))
            # Mismo ancho de columna de rotulos en todas las secciones: sin
            # el, cada grid alinearia sus campos a su etiqueta mas larga.
            f_ext.columnconfigure(0, minsize=240)
            for fila, (clave, etiqueta, ayuda, unidad) in enumerate(campos):
                ttk.Label(f_ext, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=5, pady=6)
                ent = ttk.Entry(f_ext, textvariable=self.externos_vars[clave], width=20, justify="right")
                ent.grid(row=fila, column=1, sticky="w", padx=5, pady=6)
                ttk.Label(f_ext, text=unidad, style="Ayuda.TLabel").grid(row=fila, column=2, sticky="w")
                Tooltip(ent, ayuda)
                self.lbl_no_aplica[clave] = ttk.Label(f_ext, text="",
                                                       style="Ayuda.TLabel")
                self.lbl_no_aplica[clave].grid(row=fila, column=3, sticky="w",
                                                padx=(12, 0))

        ttk.Label(
            p,
            text="Ningún dato de esta sección tiene valor por defecto: sin declararlo, "
                 "la etapa que lo necesita queda registrada como bloqueo en el informe "
                 "(no se sustituye por un número plausible).",
            style="Ayuda.TLabel", wraplength=820, justify="left",
        ).pack(anchor="w", padx=5, pady=(6, 0))

        # Sin «(--alcance)» en el rotulo (G1): la bandera equivalente la dicen
        # los tooltips de los dos botones de opcion.
        panel_alcance = Panel(panel_datos.master, "Alcance de la corrida")
        panel_alcance.pack(fill="x", pady=(0, 10))
        p = panel_alcance.interior
        ttk.Label(
            p,
            text="Es una bifurcación DECLARADA, no una poda. Con 'expediente' "
                 "todo corre como siempre. Con 'perfil', V5 y V8 se intentan "
                 "pero su fallo se difiere al expediente en vez de frenar el "
                 "dimensionamiento, y las Fases 8 y 9 no se ejecutan: nada de "
                 "lo diferido se pierde -- queda registrado con su fundamento "
                 "en el bloque de alcance del informe y de la memoria. El "
                 "alcance elige además la plantilla por defecto de la memoria.",
            style="Ayuda.TLabel", wraplength=820, justify="left",
        ).pack(anchor="w", pady=(0, 6))

        f_alc = ttk.Frame(p)
        f_alc.pack(fill="x", pady=4)
        for columna, (valor, etiqueta, ayuda) in enumerate((
                (cli.ALCANCE_EXPEDIENTE, "Expediente (defecto)",
                 "El pipeline completo: M0 a M10 mas la Fase 9.\n"
                 "Plantilla por defecto de la memoria: memoria_alcantarillas.html.\n"
                 "Equivale a --alcance expediente en la linea de comandos."),
                (cli.ALCANCE_PERFIL, "Perfil",
                 "V5 y V8 diferidas al expediente y Fases 8 y 9 no ejecutadas,\n"
                 "cada una con su constancia. Plantilla por defecto:\n"
                 "memoria_perfil.html, que sin este selector era INALCANZABLE\n"
                 "desde la ventana (SIS-A-17).\n"
                 "Equivale a --alcance perfil en la linea de comandos."))):
            rb = ttk.Radiobutton(f_alc, text=etiqueta, value=valor,
                                 variable=self.alcance_var)
            rb.grid(row=0, column=columna, sticky="w", padx=12, pady=4)
            Tooltip(rb, ayuda)

        # --- El anticipo de bloqueos ANTES de correr (G3) ------------------
        # Panel INFORMATIVO junto al boton de ejecutar: tres bloques, todos
        # derivados por `src/anticipo.py` (aqui solo se pinta), que se
        # refrescan al cargar CSV y al cambiar el alcance. ES UNA ESTIMACION
        # y el aviso fijo lo dice; la verdad medida sigue siendo el tablero
        # de la pestana 4, que se puebla despues de ejecutar. El boton de
        # EJECUTAR no se entera de que este panel existe: correr siempre se
        # puede, y el pipeline convierte cada falta en un Bloqueo declarado.
        panel_anticipo = Panel(panel_alcance.master, "Anticipo antes de correr")
        panel_anticipo.pack(fill="x", pady=(0, 10))
        f_ant = panel_anticipo.interior
        ttk.Label(f_ant, text=antc.AVISO_DEL_ANTICIPO, style="Ayuda.TLabel",
                  wraplength=900, justify="left").pack(anchor="w", pady=(0, 6))

        self.lbl_anticipo_criterios = ttk.Label(f_ant, text="",
                                                style="Header.TLabel")
        self.lbl_anticipo_criterios.pack(anchor="w")
        f_arbol_ant = ttk.Frame(f_ant)
        f_arbol_ant.pack(fill="x", pady=(2, 6))
        f_arbol_ant.columnconfigure(0, weight=1)
        # Con RESPONSABLE y EVIDENCIA (E-B, E13 reducido), derivados por
        # `src/responsable.py` y traidos en `CriterioVacio`; el panel sigue
        # siendo informativo (00_LEEME_DICTAMEN §3).
        self.tree_anticipo = ttk.Treeview(
            f_arbol_ant, columns=("clave", "concepto", "responsable", "evidencia"),
            show="headings", height=6)
        self.tree_anticipo.heading("clave", text="Criterio pendiente")
        self.tree_anticipo.heading("concepto", text="Concepto")
        self.tree_anticipo.heading("responsable", text="Responsable (quien lo fija)")
        self.tree_anticipo.heading("evidencia", text="Evidencia (que lo sostiene)")
        self.tree_anticipo.column("clave", width=220, anchor="w")
        self.tree_anticipo.column("concepto", width=320, anchor="w")
        self.tree_anticipo.column("responsable", width=220, anchor="w")
        self.tree_anticipo.column("evidencia", width=220, anchor="w")
        self.tree_anticipo.grid(row=0, column=0, sticky="ew")
        scroll_ant = ttk.Scrollbar(f_arbol_ant, orient="vertical",
                                   command=self.tree_anticipo.yview)
        self.tree_anticipo.configure(yscroll=scroll_ant.set)
        scroll_ant.grid(row=0, column=1, sticky="ns")
        self.tree_anticipo.bind("<<TreeviewSelect>>",
                                self._ir_al_criterio_del_anticipo)
        Tooltip(self.tree_anticipo,
                "Clic en una fila lleva a ese criterio en la pestana de\n"
                "criterios, donde se declara. La lista es la interseccion de\n"
                "lo que el alcance elegido puede invocar con los criterios\n"
                "sin valor no opcionales; los opcionales no bloquean nada y\n"
                "por eso no estan.")

        ttk.Label(f_ant, text="Columnas del CSV cargado",
                  style="Header.TLabel").pack(anchor="w")
        self.lbl_anticipo_csv = ttk.Label(f_ant, text="", style="Ayuda.TLabel",
                                          wraplength=900, justify="left")
        self.lbl_anticipo_csv.pack(anchor="w", pady=(0, 6))

        ttk.Label(f_ant, text="Lo que este alcance difiere",
                  style="Header.TLabel").pack(anchor="w")
        self.lbl_anticipo_diferido = ttk.Label(f_ant, text="",
                                               style="Ayuda.TLabel",
                                               wraplength=900, justify="left")
        self.lbl_anticipo_diferido.pack(anchor="w")

        # --- Bloque 4 (PF-2): los datos que faltan, punto a punto ----------
        # Lo produce `antc.datos_faltantes_por_punto` con el CSV, el JSON de
        # datos externos y las banderas de esta pestaña; aqui solo se pinta.
        # Como los otros tres, es una estimacion y no toca el boton.
        ttk.Label(f_ant, text="Datos que faltan, punto a punto (pre-vuelo)",
                  style="Header.TLabel").pack(anchor="w", pady=(6, 0))
        self.lbl_anticipo_prevuelo = ttk.Label(f_ant, text="", style="Ayuda.TLabel",
                                               wraplength=900, justify="left")
        self.lbl_anticipo_prevuelo.pack(anchor="w")
        f_pre = ttk.Frame(f_ant)
        f_pre.pack(fill="x", pady=(2, 6))
        f_pre.columnconfigure(0, weight=1)
        self.tree_prevuelo = ttk.Treeview(
            f_pre, columns=("punto", "dato", "estado", "etapa", "de_donde"),
            show="headings", height=5)
        self.tree_prevuelo.heading("punto", text="Punto")
        self.tree_prevuelo.heading("dato", text="Dato")
        self.tree_prevuelo.heading("estado", text="Estado")
        self.tree_prevuelo.heading("etapa", text="Etapa que lo siente")
        self.tree_prevuelo.heading("de_donde", text="De donde tendria que venir")
        self.tree_prevuelo.column("punto", width=90, anchor="w")     # literal-ok: ancho de columna en px
        self.tree_prevuelo.column("dato", width=170, anchor="w")     # literal-ok: ancho de columna en px
        self.tree_prevuelo.column("estado", width=80, anchor="w")    # literal-ok: ancho de columna en px
        self.tree_prevuelo.column("etapa", width=230, anchor="w")    # literal-ok: ancho de columna en px
        self.tree_prevuelo.column("de_donde", width=420, anchor="w") # literal-ok: ancho de columna en px
        self.tree_prevuelo.grid(row=0, column=0, sticky="ew")
        scroll_pre = ttk.Scrollbar(f_pre, orient="vertical",
                                   command=self.tree_prevuelo.yview)
        self.tree_prevuelo.configure(yscroll=scroll_pre.set)
        scroll_pre.grid(row=0, column=1, sticky="ns")

        self._pintar_anticipo()

    # LA CLAVE DE `cli` QUE LLEVA CADA CAMPO DE LA VENTANA. Los rotulos de
    # `CAMPOS_EXTERNOS` son los de la GUI (`l_hidraulico`) y las claves con las
    # que `cli` razona son las del expediente (`L_hidraulico_m`): la traduccion
    # ya existia dentro de `_leer_banderas`, enterrada en el armado del dict, y
    # aqui hace falta la MISMA para preguntar por las familias. Se escribe una
    # vez y las dos la leen.
    # La traduccion es la de `src/sesion.py`, que es la que la CLI usa al
    # leer una sesion (`--sesion`): el MISMO objeto, no una copia.
    CLAVE_EXTERNA_DE_CAMPO = ses.CLAVE_EXTERNA_DE_CAMPO

    def _secciones_de_campos(self):
        """
        Las secciones de la pestana 1, DERIVADAS: [(familias, campos), ...].

        Ninguna asignacion campo->seccion se escribe aqui: la tupla de
        familias de cada campo sale de `cli.familias_que_usan` --- la MISMA
        fuente que consulta `_pintar_no_aplica`, y la que `cli._fase_10` lee
        para decidir si esa fase corre ---, de modo que mover una fila en
        `cli.FAMILIAS_QUE_USAN` mueve el campo de seccion sin tocar la GUI.
        Un dato sin fila declarada lo usan las tres familias (la semantica
        que fija `tests/test_familias_del_csv.py`: la excepcion se declara,
        la regla no) y va en «Comunes a todas las familias», que se pinta
        primero; despues, las secciones de familia en el orden de Sec. 2.3.
        """
        secciones = {}
        for campo in CAMPOS_EXTERNOS:
            usan = cli.familias_que_usan(self.CLAVE_EXTERNA_DE_CAMPO[campo[0]])
            secciones.setdefault(usan, []).append(campo)
        todas = tuple(Familia)
        orden = {familia: indice for indice, familia in enumerate(todas)}
        return sorted(secciones.items(),
                      key=lambda par: (par[0] != todas,
                                       [orden[f] for f in par[0]]))

    def _titulo_seccion(self, familias):
        """El rotulo de una seccion, derivado de las familias que sirve."""
        if familias == tuple(Familia):
            return "Comunes a todas las familias"
        return "Solo " + " y ".join(f"Familia {f.value}" for f in familias)

    def _pintar_encabezados_familia(self):
        """
        El conteo de puntos del CSV en el encabezado de cada seccion de
        familia. `puntos_familia = None` es "no se sabe" (sin CSV legible) y
        se muestra como «— puntos», con la seccion visible. Una seccion cuyas
        familias suman 0 puntos se ATENUA --- el color de aviso, el mismo de
        la anotacion «no aplica» --- en vez de colapsarse o deshabilitarse:
        el motivo queda visible en el propio conteo y en la anotacion de cada
        campo, y los campos siguen aceptando texto por la misma razon que en
        `_pintar_no_aplica`.
        """
        for familias, lbl in self.lbl_seccion_familia.items():
            if self.puntos_familia is None:
                lbl.config(text="— puntos", foreground=comp.TEXTO_SUAVE)
                continue
            partes = []
            for familia in familias:
                n = self.puntos_familia.get(familia, 0)
                partes.append(f"Familia {familia.value}: {n} punto"
                              + ("" if n == 1 else "s"))
            texto = " · ".join(partes) + " en el CSV"
            if any(self.puntos_familia.get(f, 0) for f in familias):
                lbl.config(text=texto, foreground=comp.TEXTO_SUAVE)
            else:
                lbl.config(text=texto, foreground=COLOR_AVISO)

    def _releer_familias(self):
        """
        Relee del CSV que familias trae el expediente, y reanota la pestana 1
        --- la anotacion de cada campo y el conteo de cada encabezado ---.

        NO INTERRUMPE NI AVISA SI EL CSV NO SE PUEDE LEER, y es deliberado: se
        dispara al teclear la ruta, de modo que la mitad de las veces el
        archivo aun no existe. Un error de carga aqui es ruido; el que importa
        lo da EJECUTAR, con el mensaje entero. Lo unico que cambia es que la
        anotacion se calla: `None` es "no se sabe", no "no hay ninguna".
        """
        if not hasattr(self, "lbl_no_aplica"):
            return
        ruta = self.csv_var.get().strip()
        if not ruta:
            self.familias_csv = None
            self.puntos_familia = None
        else:
            try:
                self.familias_csv = cli.familias_del_csv(Path(ruta))
                self.puntos_familia = cli.puntos_por_familia(Path(ruta))
            except (OSError, UnicodeDecodeError, ErrorProyecto):
                self.familias_csv = None
                self.puntos_familia = None
        self._pintar_no_aplica()
        self._pintar_encabezados_familia()
        # El bloque de columnas del anticipo (G3) mira el mismo archivo:
        # cambiar el CSV es una de las dos cosas que lo refrescan.
        self._pintar_anticipo()

    def _pintar_no_aplica(self):
        """
        La anotacion de cada campo declarado, con la familia que falta.

        El conjunto de familias que usa cada dato sale de
        `cli.familias_que_usan`, que es el MISMO que consulta `cli._fase_10`
        para decidir si esa fase corre. Una regla propia de la ventana seria
        una segunda respuesta a "¿este dato sirve para algo en este
        expediente?", y podria contradecir a la del pipeline.
        """
        for campo, lbl in self.lbl_no_aplica.items():
            if self.familias_csv is None:
                lbl.config(text="")
                continue
            usan = cli.familias_que_usan(self.CLAVE_EXTERNA_DE_CAMPO[campo])
            if any(familia in usan for familia in self.familias_csv):
                lbl.config(text="")
                continue
            faltan = ", ".join(f"Familia {f.value}" for f in usan)
            lbl.config(text=f"no aplica: este CSV no trae puntos de {faltan}",
                       foreground=COLOR_AVISO)

    def _pintar_anticipo(self):
        """
        Repinta los tres bloques del anticipo (G3): al cargar CSV, al cambiar
        el alcance, y tras cada repintado de la tabla de criterios --- porque
        declarar o quitar un valor en caliente cambia que criterios siguen
        vacios, y todas esas acciones pasan por `_llenar_tabla_criterios` ---.

        TODO EL CONTENIDO LO PRODUCE `src/anticipo.py`; aqui se pinta, que es
        el mismo reparto que la ayuda de entrada y la traza de procedencia.
        La GUI no lee el CSV por su cuenta: `contraste_de_cabecera` pasa por
        `M0_carga.leer_cabecera`, que vive en src/.

        Y NO TOCA EL BOTON DE EJECUTAR, a proposito (regla dura de G3): el
        anticipo es una ESTIMACION --- la invocacion real de un criterio
        depende de la ruta que tome cada punto --- y ninguna estimacion de
        este proyecto gobierna un filtro ni un boton. Correr siempre se
        puede: el pipeline convierte cada falta en un Bloqueo declarado, y la
        verdad medida es el tablero de la pestana 4.

        El silencio ante un CSV ilegible es el MISMO de `_releer_familias`,
        y por la misma razon escrita alli: esto se dispara al teclear la
        ruta, y la mitad de las veces el archivo aun no existe.
        """
        if not hasattr(self, "tree_anticipo"):
            return
        alcance = self.alcance_var.get()

        vacios = antc.criterios_vacios_alcanzables(alcance)
        for item in self.tree_anticipo.get_children():
            self.tree_anticipo.delete(item)
        for criterio in vacios:
            self.tree_anticipo.insert("", "end", iid=criterio.clave,
                                      values=(criterio.clave,
                                              criterio.concepto,
                                              criterio.responsable,
                                              criterio.evidencia))
        self.lbl_anticipo_criterios.config(
            text=(f"Criterios vacíos que el alcance «{alcance}» puede "
                  f"invocar: {len(vacios)}"),
            foreground=COLOR_AVISO if vacios else COLOR_OK)

        ruta = self.csv_var.get().strip()
        contraste = None
        if ruta:
            try:
                contraste = antc.contraste_de_cabecera(Path(ruta))
            except (OSError, UnicodeDecodeError):
                contraste = None
        if contraste is None:
            self.lbl_anticipo_csv.config(text=antc.SIN_CSV,
                                         foreground=comp.TEXTO_SUAVE)
        else:
            self.lbl_anticipo_csv.config(
                text="\n".join(antc.lineas_del_contraste(contraste)),
                foreground=(comp.TEXTO_SUAVE if contraste.cabecera_completa
                            else COLOR_AVISO))

        diferido = antc.diferimientos_del_alcance(alcance)
        self.lbl_anticipo_diferido.config(
            text="\n".join(antc.lineas_de_diferimientos(diferido)),
            foreground=COLOR_AVISO if diferido.difiere_algo else comp.TEXTO_SUAVE)

        # Bloque 4 (PF-2). Los datos externos se arman por la MISMA puerta
        # que la corrida (`cli.cargar_datos_externos` con el JSON de la
        # pestaña y sus banderas); un JSON ilegible o una bandera mal tecleada
        # no rompen el anticipo: se dice y se sigue.
        if not hasattr(self, "tree_prevuelo"):
            return
        for item in self.tree_prevuelo.get_children():
            self.tree_prevuelo.delete(item)
        if contraste is None:
            self.lbl_anticipo_prevuelo.config(text=antc.SIN_CSV, foreground=comp.TEXTO_SUAVE)
            return
        ruta_externos = self.datos_externos_var.get().strip() or None
        try:
            externos = cli.cargar_datos_externos(
                Path(ruta_externos) if ruta_externos else None, self._leer_banderas())
            estimado = antc.datos_faltantes_por_punto(Path(ruta), externos, alcance)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            self.lbl_anticipo_prevuelo.config(
                text=f"El pre-vuelo no pudo armar los datos externos: {exc}",
                foreground=COLOR_AVISO)
            return
        lineas = antc.lineas_del_prevuelo(estimado)
        detiene = any(e.detiene for e in estimado)
        self.lbl_anticipo_prevuelo.config(
            text=lineas[0], foreground=COLOR_AVISO if detiene else comp.TEXTO_SUAVE)
        for e in estimado:
            familia = "" if e.familia is None else f" ({e.familia.value})"
            self.tree_prevuelo.insert("", "end", values=(
                f"{e.id_punto}{familia}", e.dato,
                "DETIENE" if e.detiene else "espera", e.etapa, e.de_donde))

    def _ir_al_criterio_del_anticipo(self, _evt=None):
        """
        Clic en una fila del anticipo: la MISMA fila en la pestana de
        criterios, donde se declara.

        Reutiliza la seleccion existente del arbol, por el mismo camino que
        `_tras_declarar_en_ventana` y por las mismas razones: la clave se
        adopta ANTES de repintar, para que `_pasa_el_filtro` proteja esa fila
        aunque el filtro puesto no la deje pasar, y para que `selection_set`
        encuentre algo que seleccionar.
        """
        seleccion = self.tree_anticipo.selection()
        if not seleccion:
            return
        clave = seleccion[0]
        self._clave_criterio_seleccionado = clave
        self._llenar_tabla_criterios()
        self.tree_criterios_todos.selection_set(clave)
        self.tree_criterios_todos.see(clave)
        self.nb.select(self.tab_criterios)

    def _abrir_ayuda(self, pestana):
        """
        Abre la ayuda de entrada en la pestana pedida.

        UNA SOLA VENTANA VIVA, y se reutiliza. Sin esto, cada clic en un icono
        abriria una copia mas: el usuario acabaria con cuatro ayudas apiladas y
        cerraria la de arriba creyendo que las cerro todas. Si ya esta abierta
        se le cambia la pestana y se le da el foco, que es lo que se espera al
        pulsar el icono del otro campo.
        """
        viva = getattr(self, "_ventana_ayuda", None)
        if viva is not None and viva.winfo_exists():
            viva.nb.select(viva.tab_json if pestana == ayuda_ent.PESTANA_JSON
                           else viva.tab_csv)
            viva.lift()
            viva.focus_set()
            return viva
        self._ventana_ayuda = ayuda_ent.abrir(self.root, pestana)
        return self._ventana_ayuda

    def _elegir_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar CSV de puntos criticos",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.csv_var.set(ruta)

    def _elegir_datos_externos(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar JSON de datos externos",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.datos_externos_var.set(ruta)

    def _elegir_datos_sitio(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar JSON de datos de sitio [S] de la obra",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.datos_sitio_var.set(ruta)

    # -------------------------- Pestana 2 -----------------------------
    def _construir_tab_criterios(self, p):
        p.columnconfigure(0, weight=1)
        # La fila 2 es el `PanedWindow` (tabla + detalle). La 0 es la cabecera
        # de la vista, la 1 el panel del filtro y el recuento, y la 3 el panel
        # de declaracion con su linea de estado. `p` es el interior de un
        # `MarcoScroll` (ver `_crear_interfaz`): cada fila toma su alto natural
        # y la vista se desplaza.

        self._cabecera_de_vista(p, self.tab_criterios).grid(row=0, column=0, sticky="ew",
                                           pady=(0, 8))
        panel_filtro = Panel(p, "Filtro y recuento")
        panel_filtro.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        f_cab = panel_filtro.interior
        ttk.Label(
            f_cab,
            # Las CUATRO que este archivo tiene, y solo esas (SIS-A-11).
            # [N] no aparece, y conviene decir con precision por que: NO es
            # que el codigo lo impida --- `ETIQUETAS_VALIDAS` admite 'N' y
            # `_verificar_criterio` la aceptaria ---, es que un valor
            # normativo vive en constantes_normativas.py, y lo que sostiene
            # esa separacion es el guardian
            # `test_ningun_criterio_adoptado_lleva_ya_la_etiqueta_N`.
            # Anunciar [N] aqui invitaba a leer como norma lo que es
            # adopcion. [S] SI esta -- hoy tres entradas, los datos de sitio
            # pendientes de ensayo que comparten tablero con los criterios --
            # y faltaba.
            text="Etiquetas: [N->] normativo por analogia  "
                 "[S] dato de sitio (procedimiento normativo sobre ESTE sitio: "
                 "se defiende con trazabilidad, no con sensibilidad)  "
                 "[C] fuente tecnica reconocida  [A] adopcion sin norma unica. "
                 "Ninguna fila de esta tabla es normativa: lo normativo vive "
                 "en constantes_normativas.py y no se declara desde aqui. "
                 "Las filas en rojo son criterios PENDIENTES (valor=None): bloquean "
                 "cualquier calculo que los invoque hasta que se declare un valor. "
                 "Las filas en ambar son declaradas SOLO para esta corrida, y son de "
                 "dos clases que no se confunden: «declarado (corrida)» rellena un "
                 "vacio, y «pisado (corrida)» sustituye un valor que el archivo SI "
                 "tiene y que sigue diciendo otra cosa. La memoria imprime los "
                 "pisados en su propio bloque, con el valor del archivo al lado: "
                 "sirven para TANTEAR, no para entregar.",
            style="Ayuda.TLabel", wraplength=1180, justify="left",
        ).pack(anchor="w", pady=(0, 8))

        # --- El filtro y el recuento -------------------------------------
        # Con 69 criterios --- 33 de ellos pendientes --- encontrar los que
        # hay que declarar era scroll a ojo. Y el RECUENTO va aqui, arriba de
        # la tabla, porque «cuantos me faltan» es la pregunta con que se abre
        # esta pestana y contar filas a mano es la peor forma de contestarla.
        # Los dos numeros se calculan en `_llenar_tabla_criterios`, sobre las
        # mismas filas que se pintan: un contador que se calculara aparte
        # podria decir un numero y la tabla mostrar otro.
        f_filtro = ttk.Frame(f_cab)
        f_filtro.pack(fill="x")
        f_filtro.columnconfigure(4, weight=1)

        ttk.Label(f_filtro, text="Estado:").grid(row=0, column=0, sticky="w")
        self.filtro_estado_var = tk.StringVar(value=FILTROS_DE_ESTADO[0][0])
        cmb_estado = ttk.Combobox(
            f_filtro, textvariable=self.filtro_estado_var, state="readonly",
            width=26, values=[rotulo for rotulo, _tag in FILTROS_DE_ESTADO])
        cmb_estado.grid(row=0, column=1, sticky="w", padx=(6, 16))
        Tooltip(cmb_estado,
                "PENDIENTE  = valor=None: bloquea el calculo que lo invoque.\n"
                "Declarado en esta corrida = valor puesto desde la ventana o\n"
                "  desde aqui; criterios_adoptados.py NO se modifico.\n"
                "Resuelto en el archivo = el valor viene de "
                "criterios_adoptados.py.")

        ttk.Label(f_filtro, text="Ambito:").grid(row=1, column=0, sticky="w",
                                                 pady=(6, 0))
        self.filtro_ambito_var = tk.StringVar(value=FILTROS_DE_AMBITO[0][0])
        cmb_ambito = ttk.Combobox(
            f_filtro, textvariable=self.filtro_ambito_var, state="readonly",
            width=38, values=[rotulo for rotulo, _t in FILTROS_DE_AMBITO])
        cmb_ambito.grid(row=1, column=1, sticky="w", padx=(6, 16), pady=(6, 0))
        Tooltip(cmb_ambito,
                "Ninguna de las dos opciones se elige a mano aqui:\n"
                "  - «este alcance» es el que declaraste en la pestana 1;\n"
                "  - «esta corrida» sale del informe de la ultima ejecucion.\n"
                "Las dos primeras ESTIMAN --- leen la clasificacion previa de\n"
                "cada criterio ---; la tercera MIDE: es el bloque «Criterios\n"
                "pendientes que bloquearon una etapa» del informe.\n"
                "Filtrar no es ocultar: el recuento sigue diciendo cuantos hay\n"
                "en total y cuantos esconde el filtro.")

        # El aviso del ambito («el filtro esconde N») va DEBAJO de los
        # filtros y vacio no ocupa fila: ambito y fase comparten la fila 1.
        self.lbl_ambito = ttk.Label(f_filtro, text="", style="Ayuda.TLabel")
        self.lbl_ambito.grid(row=2, column=1, columnspan=4, sticky="w")

        ttk.Label(f_filtro, text="Fase:").grid(row=1, column=2, sticky="w",
                                               pady=(6, 0))
        self.filtro_fase_var = tk.StringVar(value=FILTRO_FASE_TODAS)
        cmb_fase = ttk.Combobox(
            f_filtro, textvariable=self.filtro_fase_var, state="readonly",
            width=64, values=[FILTRO_FASE_TODAS] + _fases_del_censo())
        cmb_fase.grid(row=1, column=3, columnspan=2, sticky="w",
                      padx=(6, 16), pady=(6, 0))
        Tooltip(cmb_fase,
                "La fase del calculo en que se usa cada criterio, DERIVADA\n"
                "del censo de variables (variables_entrada): ninguna fase\n"
                "esta escrita en la ventana. Una opcion compuesta\n"
                "(«Fase 3 ... · Fase 5 ...») es una variable que consumen\n"
                "varias fases, tal como el censo la atribuye.\n"
                "Se aplica JUNTO con los otros tres filtros, no en su lugar,\n"
                "y el recuento sigue contando los pendientes sobre el archivo\n"
                "entero y diciendo cuantas filas esconde el filtro combinado.")

        ttk.Label(f_filtro, text="Buscar:").grid(row=0, column=2, sticky="w")
        self.filtro_texto_var = tk.StringVar()
        ent_buscar = ttk.Entry(f_filtro, textvariable=self.filtro_texto_var, width=28)
        ent_buscar.grid(row=0, column=3, sticky="w", padx=(6, 16))
        Tooltip(ent_buscar,
                "Busca en la CLAVE y en el CONCEPTO, sin distinguir mayusculas.\n"
                "Se aplica junto con el filtro de estado, no en su lugar.")

        # El recuento es una INSIGNIA: texto («39 de 79 pendientes») sobre el
        # fondo suave del estado, rojo mientras quede alguno y verde cuando no.
        self.lbl_recuento_criterios = Insignia(f_filtro, "", comp.INSIGNIA_NEUTRA)
        self.lbl_recuento_criterios.grid(row=0, column=4, sticky="e")

        # --- La tabla y el detalle, con el reparto en manos del usuario ----
        # `PanedWindow` y no dos filas fijas: el panel de detalle tenia
        # `height=6` y el criterio de fuente mas larga de este archivo ocupa
        # 83 lineas, de modo que 77 no se podian alcanzar de ninguna manera.
        # Con el divisor movible y su barra de scroll, el reparto lo decide
        # quien esta mirando, que es lo unico que sabe si en ese momento le
        # importa mas la lista o el texto de una fila.
        # Con alto PEDIDO: dentro del marco desplazable un `PanedWindow`
        # sin alto propio nace plano, porque su alto natural no lo dan sus
        # paneles sino este argumento. Es el area de arranque de tabla mas
        # detalle; el divisor sigue moviendose dentro de ella.
        panel = ttk.PanedWindow(p, orient="vertical", height=440)
        panel.grid(row=2, column=0, sticky="nsew")

        panel_tabla = Panel(panel, "Criterios adoptados (criterios_adoptados.py)")
        panel.add(panel_tabla, weight=2)
        f_tabla = panel_tabla.interior
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        cols = ("clave", "etiqueta", "concepto", "valor", "estado", "fuente")
        self.tree_criterios_todos = ttk.Treeview(
            f_tabla, columns=cols, show="headings", height=10)
        encabezados = [
            ("clave", "Clave", 190, "w"),  # literal-ok: ancho de columna, px
            ("etiqueta", "Etq.", 45, "center"),  # literal-ok: ancho de columna, px
            ("concepto", "Concepto", 260, "w"),  # literal-ok: ancho de columna, px
            ("valor", "Valor actual", 160, "w"),  # literal-ok: ancho de columna, px
            ("estado", "Estado", 110, "center"),  # literal-ok: ancho de columna, px
            ("fuente", "Fuente", 300, "w"),  # literal-ok: ancho de columna, px
        ]
        for col, txt, ancho, anchor in encabezados:
            self.tree_criterios_todos.heading(col, text=txt)
            self.tree_criterios_todos.column(col, width=ancho, anchor=anchor)
        self.tree_criterios_todos.grid(row=0, column=0, sticky="nsew")
        self.tree_criterios_todos.tag_configure("pendiente", background=comp.ROJO_SUAVE,
                                                 foreground=COLOR_ERROR)
        self.tree_criterios_todos.tag_configure("declarado_corrida",
                                                 background=comp.AMBAR_SUAVE,
                                                 foreground=COLOR_AVISO)
        # El pisado se pinta como AVISO y con fondo propio: no es un vacio
        # (rojo) ni un valor del archivo (verde) ni un hueco rellenado
        # (ambar claro). Es el unico estado en que la tabla y el archivo
        # discrepan, y tiene que verse de un vistazo.
        self.tree_criterios_todos.tag_configure("pisado_corrida",
                                                 background=comp.PISADO_SUAVE,
                                                 foreground=COLOR_AVISO)
        self.tree_criterios_todos.tag_configure("resuelto", foreground=COLOR_OK)
        self.tree_criterios_todos.bind("<<TreeviewSelect>>", self._al_seleccionar_criterio)
        # Doble clic = abrir la ventana normativa de ese criterio. Es el gesto
        # que el usuario ya hace sobre una tabla, y el boton de abajo repite
        # la accion para quien no lo descubra.
        self.tree_criterios_todos.bind("<Double-1>", self._abrir_ventana_normativa)

        scroll_ct = ttk.Scrollbar(f_tabla, orient="vertical",
                                   command=self.tree_criterios_todos.yview)
        self.tree_criterios_todos.configure(yscroll=scroll_ct.set)
        scroll_ct.grid(row=0, column=1, sticky="ns")

        # Barra HORIZONTAL, que no habia. Las seis columnas suman mas ancho
        # que la ventana, de modo que «Fuente» --- la ultima, y la que dice de
        # donde sale el valor --- se cortaba a media palabra sin ninguna forma
        # de llegar al resto. El texto COMPLETO vive abajo, en el detalle; esta
        # barra es para leer la tabla, no para sustituirlo.
        scroll_ch = ttk.Scrollbar(f_tabla, orient="horizontal",
                                   command=self.tree_criterios_todos.xview)
        self.tree_criterios_todos.configure(xscroll=scroll_ch.set)
        scroll_ch.grid(row=1, column=0, sticky="ew")

        panel_detalle = Panel(panel, "Detalle del criterio seleccionado")
        panel.add(panel_detalle, weight=1)
        f_detalle = panel_detalle.interior
        f_detalle.columnconfigure(0, weight=1)
        f_detalle.rowconfigure(0, weight=1)

        # `height=12` y no 6: un `PanedWindow` reparte por peso solo el espacio
        # SOBRANTE, de modo que el tamano de arranque de cada panel es el que
        # su contenido pide. Con 6 el detalle nacia en 95 px --- lo mismo que
        # tenia antes de todo esto --- y el divisor no arreglaba nada hasta
        # que alguien lo arrastrara. Doce lineas visibles de arranque, el resto
        # por la barra, y el reparto en manos del usuario a partir de ahi.
        self.txt_detalle_criterio = comp.texto_plano(f_detalle, height=7, wrap="word")
        self.txt_detalle_criterio.grid(row=0, column=0, sticky="nsew")
        scroll_det = ttk.Scrollbar(f_detalle, orient="vertical",
                                    command=self.txt_detalle_criterio.yview)
        self.txt_detalle_criterio.configure(yscrollcommand=scroll_det.set)
        scroll_det.grid(row=0, column=1, sticky="ns")
        self.txt_detalle_criterio.configure(state="disabled")

        panel_declarar = Panel(p, "Declarar valor para el criterio pendiente")
        panel_declarar.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        f_declarar = panel_declarar.interior
        f_declarar.columnconfigure(1, weight=1)

        ttk.Label(f_declarar, text="Criterio:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.lbl_criterio_seleccionado = ttk.Label(f_declarar, text="(ninguno seleccionado)",
                                                     style="Header.TLabel")
        self.lbl_criterio_seleccionado.grid(row=0, column=1, sticky="w")

        ttk.Label(f_declarar, text="Valor nuevo:").grid(row=1, column=0, sticky="w",
                                                          padx=(0, 6), pady=6)
        self.valor_declarado_var = tk.StringVar()
        # Es atributo porque `_al_seleccionar_criterio` lo APAGA cuando el
        # criterio es `Derivada`: un campo que se puede teclear y cuyo valor
        # nunca se va a aceptar es el mismo bloqueo mudo que `BotonAccion`
        # existe para impedir.
        self.ent_valor_declarado = ttk.Entry(
            f_declarar, textvariable=self.valor_declarado_var)
        self.ent_valor_declarado.grid(row=1, column=1, sticky="we", pady=6)
        Tooltip(self.ent_valor_declarado,
                "Entero ('1'), numero con punto o coma decimal ('0,20'),\n"
                "lista de pares ('[[1.20, 0.90], [1.50, 1.20]]') o texto,\n"
                "segun la FORMA que declara el criterio. Lo que no tenga esa\n"
                "forma se rechaza aqui, no en el calculo. El editor de abajo\n"
                "COMPONE este mismo campo: las dos vistas son el mismo valor.")

        # EL EDITOR TIPADO DEL CRITERIO SELECCIONADO (E-B, E10). Se monta por
        # forma al seleccionar (`_montar_editor`) y compone el literal de
        # arriba; el literal, a su vez, lo repinta. Una sola fuente del
        # valor, dos vistas, y un solo boton que declara.
        self.f_editor = ttk.Frame(f_declarar)
        self.f_editor.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 6))
        self.editor = None
        self._sincronizando_editor = False
        self._editor_refleja_literal = True
        try:
            self.color_neutro_editor = ttk.Style().lookup("TFrame", "background") \
                or "SystemButtonFace"
        except tk.TclError:
            self.color_neutro_editor = "SystemButtonFace"
        self.valor_declarado_var.trace_add("write", self._literal_cambio)

        # DOS FILAS DE BOTONES, y la segunda no es estetica: las cuatro en
        # una sola sumaban mas ancho que la ventana en su tamano por defecto
        # (1100 px) y la que se salia por el borde derecho era justamente
        # «Guardar en archivo fuente», la unica que modifica el archivo del
        # proyecto. Ahora las tres reversibles van juntas y la permanente va
        # sola, separada por una linea: la accion que no se deshace no
        # comparte fila con las que si.
        f_botones = ttk.Frame(f_declarar)
        f_botones.grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.btn_aplicar_corrida = BotonAccion(
            f_botones, "Aplicar solo a esta corrida", fondo=comp.AZUL,
            activebackground=comp.AZUL_OSCURO, activeforeground="white",
            command=self._aplicar_valor_corrida,
            motivo=MOTIVO_SIN_CRITERIO,
            ayuda="El valor se usa en la proxima ejecucion del calculo, pero\n"
                  "criterios_adoptados.py NO se modifica. Entra ENTERO y en una\n"
                  "sola llamada por declaracion.py, con su procedencia: la fila\n"
                  "elegida en el editor, o la nota que una adopcion distinta\n"
                  "exige. Si un campo falla, no entra nada.")
        self.btn_aplicar_corrida.pack(side="left", padx=(0, 8), ipadx=6, ipady=3)

        self.btn_quitar_declarado = BotonAccion(
            f_botones, "Quitar declaracion de la corrida",
            letra=BotonAccion.DISCRETA, command=self._quitar_valor_corrida, motivo=MOTIVO_SIN_CRITERIO,
            ayuda="Retira el valor declarado para esta corrida Y su\n"
                  "procedencia. Lo que queda debajo depende de lo que habia:\n"
                  "si el criterio estaba vacio vuelve a bloquear el calculo;\n"
                  "si estaba PISADO vuelve a gobernar el valor del archivo.")
        self.btn_quitar_declarado.pack(side="left", padx=8, ipadx=6, ipady=3)

        self.btn_ventana_norma = BotonAccion(
            f_botones, "Ver la norma y declarar desde la tabla...",
            fondo=comp.TEXTO_SUAVE,
            command=self._abrir_ventana_normativa, motivo=MOTIVO_SIN_CRITERIO,
            ayuda="Abre la ventana emergente de la variable: la tabla COMPLETA\n"
                  "con su numeral, su pagina impresa, sus notas al pie y sus\n"
                  "modificadores; o el rango con su semantica; o el catalogo con\n"
                  "la advertencia de que ninguna norma lo sostiene.\n"
                  "Al declarar desde alli queda registrada la procedencia: fila,\n"
                  "valor, alternativas descartadas, cita y fecha.")
        self.btn_ventana_norma.pack(side="left", padx=8, ipadx=6, ipady=3)

        ttk.Separator(f_declarar, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=8)

        f_permanente = ttk.Frame(f_declarar)
        f_permanente.grid(row=5, column=0, columnspan=2, sticky="w")

        self.btn_guardar_archivo = BotonAccion(
            f_permanente, "Guardar en archivo fuente (permanente)",
            fondo=comp.ROJO,
            command=self._guardar_valor_en_archivo, motivo=MOTIVO_SIN_CRITERIO,
            ayuda=
                  # SIS-A-14: decia 'Reescribe \'valor=None\'', y reescribe
                  # CUALQUIER valor -- tambien el de un criterio ya declarado --.
                  # El texto que lee el usuario tiene que decir lo mismo que el
                  # docstring de `escribir_valor_en_archivo`, o la correccion
                  # solo llega a quien lee el codigo.
                  "Reescribe el 'valor=' del criterio -- este declarado o no --\n"
                  "DIRECTAMENTE en criterios_adoptados.py. Pide confirmacion.\n"
                  "Etiqueta, justificacion y fuente no se tocan: revisalas a\n"
                  "mano si la razon del valor cambio.\n"
                  "No alcanza a los valores que son tabla, dict o tupla: esos\n"
                  "se rechazan y se editan a mano.")
        self.btn_guardar_archivo.pack(side="left", ipadx=6, ipady=3)

        # La linea de estado del panel, DENTRO del panel que la produce.
        self.lbl_estado_criterio = ttk.Label(f_declarar, text="", style="Ayuda.TLabel",
                                              wraplength=980, justify="left")
        self.lbl_estado_criterio.grid(row=6, column=0, columnspan=2, sticky="w",
                                      pady=(8, 0))

        self._clave_criterio_seleccionado = None
        self._seleccion_fuera_del_filtro = False
        self._claves_ambito = None
        # Refiltrar al escribir, no al pulsar: es la misma regla que la
        # Sec. 4.3 le pide al campo validable, y la que hace util un buscador.
        # La traza se engancha AQUI, al final: `_llenar_tabla_criterios` usa la
        # tabla, la etiqueta de recuento y la clave seleccionada, y engancharla
        # antes de que existan las tres deja la ventana a merced del orden en
        # que se escriban las variables.
        for var in (self.filtro_estado_var, self.filtro_texto_var,
                    self.filtro_ambito_var, self.filtro_fase_var):
            var.trace_add("write", lambda *_a: self._llenar_tabla_criterios())
        self._llenar_tabla_criterios()

    def _estado_criterio(self, clave):
        """
        (texto, tag) del estado de un criterio para la tabla y el detalle.

        CUATRO ESTADOS Y NO TRES desde que se puede PISAR un valor de archivo.
        «declarado (corrida)» y «pisado (corrida)» son los dos declarados en
        caliente y NO comparten rotulo a proposito: el primero rellena un vacio
        y deja el expediente donde estaba; el segundo sustituye una decision ya
        transcrita, que sigue en el archivo diciendo otra cosa. Reutilizar el
        mismo tag para los dos habria hecho invisible en la tabla la unica
        diferencia que importa --- la que separa tantear de falsear ---, que es
        la forma exacta que tuvo SIS-A-01.
        """
        if ca.declarado_en_caliente(clave):
            if ca.criterio(clave).valor is None:
                return "declarado (corrida)", "declarado_corrida"
            return "pisado (corrida)", "pisado_corrida"
        if ca.criterio(clave).valor is None:
            return "PENDIENTE", "pendiente"
        return "resuelto", "resuelto"

    def _refiltrar(self):
        """
        Repinta la tabla de criterios si ya existe.

        La guardia no es defensiva de mas: `alcance_var` se traza en
        `__init__`, y `set()` sobre el defecto o una sesion cargada puede
        dispararla antes de que la pestana 2 este construida.
        """
        if hasattr(self, "tree_criterios_todos"):
            self._llenar_tabla_criterios()

    def _ambito_del_filtro(self):
        """El tag de `FILTROS_DE_AMBITO` que pide el filtro."""
        rotulo = self.filtro_ambito_var.get()
        for texto, tag in FILTROS_DE_AMBITO:
            if texto == rotulo:
                return tag
        return AMBITO_TODOS

    def _claves_del_ambito(self):
        """
        Las claves que el filtro de ambito deja pasar, o None si no filtra.

        NO CALCULA NINGUNA DE LAS DOS RESPUESTAS, y eso es a proposito: la de
        alcance la da `ca.criterios_del_alcance`, que lee `Criterio.nivel`; la
        de la corrida la da `M11.criterios_bloqueantes`, que es el mismo
        bloque que la memoria imprime. Una tercera regla escrita aqui seria
        una tercera respuesta a la misma pregunta, y la pestana acabaria
        diciendo algo distinto de lo que dice el informe.

        `None` cuando el filtro de bloqueantes se pide sin corrida: sin
        informe no hay conjunto medido, y devolver el vacio dejaria la tabla a
        cero, que se lee como "no queda nada por declarar" --- la lectura mas
        peligrosa que esta pestana puede dar. Se avisa en la linea de al lado.
        """
        ambito = self._ambito_del_filtro()
        if ambito == AMBITO_ALCANCE:
            return set(ca.criterios_del_alcance(self.alcance_var.get()))
        if ambito == AMBITO_BLOQUEANTES:
            if self.informe is None:
                return None
            return {c.clave for c in M11.criterios_bloqueantes(self.informe)}
        return None

    def _pintar_aviso_de_ambito(self, escondidos):
        """La linea que dice DE DONDE sale el conjunto que el filtro aplica."""
        ambito = self._ambito_del_filtro()
        if ambito == AMBITO_ALCANCE:
            texto = (f"segun el alcance «{self.alcance_var.get()}» de la "
                     f"pestana 1 ({escondidos} fuera de alcance)")
        elif ambito == AMBITO_BLOQUEANTES:
            texto = (MOTIVO_SIN_CORRIDA_FILTRO if self.informe is None
                     else f"medido sobre la corrida de {self.informe.generado}")
        else:
            texto = ""
        self.lbl_ambito.config(
            text=texto,
            foreground=(COLOR_AVISO if ambito == AMBITO_BLOQUEANTES
                        and self.informe is None else comp.TEXTO_SUAVE))

    def _tag_del_filtro(self):
        """El tag de `_estado_criterio` que pide el filtro, o None si «Todos»."""
        rotulo = self.filtro_estado_var.get()
        for texto, tag in FILTROS_DE_ESTADO:
            if texto == rotulo:
                return tag
        return None

    def _fase_del_filtro(self):
        """
        La fase que pide el filtro, o None si «Todas».

        El rotulo ES el valor: las opciones del combo son las fases del censo
        tal cual (`_fases_del_censo`), sin tabla de traduccion en medio ---
        una tabla rotulo->fase seria una segunda copia de la lista que este
        filtro se prohibe escribir.
        """
        rotulo = self.filtro_fase_var.get()
        return None if rotulo == FILTRO_FASE_TODAS else rotulo

    def _pasa_el_filtro(self, clave, tag):
        """
        Si esta fila se pinta con el filtro puesto.

        EL CRITERIO SELECCIONADO PASA SIEMPRE, y no es una excepcion comoda:
        declarar un valor CAMBIA el estado de su fila --- de «PENDIENTE» a
        «declarado (corrida)» ---, de modo que con «Solo PENDIENTES» puesto la
        fila desapareceria en el mismo instante en que se declara. El usuario
        perderia de vista lo que acaba de hacer justo cuando quiere
        comprobarlo, y `selection_set` quedaria apuntando a una fila que ya no
        existe.
        """
        if clave == self._clave_criterio_seleccionado:
            self._seleccion_fuera_del_filtro = not self._encaja_en_el_filtro(clave, tag)
            return True
        return self._encaja_en_el_filtro(clave, tag)

    def _encaja_en_el_filtro(self, clave, tag):
        """
        Si la fila cumple los CUATRO filtros, sin la excepcion de la seleccionada.

        Los cuatro se aplican JUNTOS y no en lugar unos de otros: «solo
        PENDIENTES» de la Fase 9 dentro del alcance de expediente es la clase
        de pregunta con la que se abre esta pestana, y contestarla con dos
        pasadas obligaria a recordar cual estaba puesto.

        La fase de la fila NO se deduce aqui: la dice el censo
        (`ve.variable(clave).fase`), que es el mismo dato del que salen las
        opciones del combo. Comparar contra otra atribucion seria un filtro
        que ofrece unas fases y aplica otras.
        """
        if (self._claves_ambito is not None
                and clave not in self._claves_ambito):
            return False
        pedido = self._tag_del_filtro()
        if pedido is not None and tag != pedido:
            return False
        fase = self._fase_del_filtro()
        if fase is not None and ve.variable(clave).fase != fase:
            return False
        texto = self.filtro_texto_var.get().strip().lower()
        if not texto:
            return True
        return texto in clave.lower() or texto in ca.criterio(clave).concepto.lower()

    def _llenar_tabla_criterios(self):
        for item in self.tree_criterios_todos.get_children():
            self.tree_criterios_todos.delete(item)
        pendientes = mostrados = 0
        self._seleccion_fuera_del_filtro = False
        # UNA sola vez por repintado y no una por fila: `criterios_del_alcance`
        # recorre y ordena los 69, y `criterios_bloqueantes` recorre el informe
        # entero. Se guarda en el objeto porque `_encaja_en_el_filtro` lo lee
        # fila a fila.
        self._claves_ambito = self._claves_del_ambito()
        # El valor efectivo NO se recalcula aqui: lo da `criterio_efectivo`,
        # la misma funcion que leen M11 y el JSON. Tres copias de la regla
        # "override si lo hay, archivo si no" son tres sitios donde puede
        # divergir, y esa divergencia fue el hallazgo bloqueante SIS-A-01.
        for clave in sorted(ca.CRITERIOS):
            c = ca.criterio(clave)
            valor_efectivo = ca.criterio_efectivo(clave).valor
            estado_txt, tag = self._estado_criterio(clave)
            if tag == "pendiente":
                pendientes += 1
            if not self._pasa_el_filtro(clave, tag):
                continue
            mostrados += 1
            self.tree_criterios_todos.insert("", "end", iid=clave, values=(
                clave, c.etiqueta, c.concepto,
                "(sin declarar)" if valor_efectivo is None else repr(valor_efectivo),
                estado_txt, c.fuente,
            ), tags=(tag,))
        self._reponer_seleccion()
        self._pintar_recuento(pendientes, mostrados)
        self._pintar_aviso_de_ambito(len(ca.CRITERIOS) - len(self._claves_ambito)
                                     if self._claves_ambito is not None else 0)
        # El bloque 1 del anticipo (G3) lista los criterios que siguen
        # VACIOS, y eso cambia por este mismo repintado: declarar, pisar y
        # quitar en caliente --- desde el panel o desde la emergente ---
        # terminan todos aqui. Refrescarlo aqui es UN sitio en vez de cuatro.
        self._pintar_anticipo()

    def _reponer_seleccion(self):
        """
        Vuelve a seleccionar la fila que estaba seleccionada antes del repintado.

        ES LA RAIZ DE TRES DEFECTOS Y NO UNA COMODIDAD. `<<TreeviewSelect>>` no
        es sincrono: Tk lo ENCOLA. El `delete` de todas las filas deja la tabla
        sin seleccion, y si nadie la repone, en el siguiente giro del bucle de
        eventos `_al_seleccionar_criterio` entra con seleccion vacia y pone
        `_clave_criterio_seleccionado = None`. A partir de ahi, medido:

        - teclear en «Buscar» DESELECCIONABA el criterio --- detalle en blanco,
          botones apagados, y el mensaje de confirmacion borrado ---;
        - la promesa de `_pasa_el_filtro` («la seleccionada pasa siempre»)
          valia para UN refiltrado: al segundo, `_clave` ya era None y la fila
          desaparecia;
        - y `_tras_declarar_en_ventana` --- que declara desde la emergente, que
          NO es modal y deja tocar el filtro por debajo --- hacia
          `selection_set` sobre una fila inexistente y reventaba con
          `_tkinter.TclError`, que no desciende de `ErrorProyecto`: sale como
          traza de Tk y la GUI no la distingue de un fallo del programa, con el
          valor ya declarado y la fila fuera de la tabla.

        Reponerla aqui, en el UNICO sitio que borra e inserta filas, cierra los
        tres: la clave sobrevive al repintado, de modo que `_pasa_el_filtro`
        sigue protegiendo su fila y ningun `selection_set` posterior apunta al
        vacio. La condicion `in get_children()` no es defensiva de mas: la
        seleccion puede ser None al construir la ventana.
        """
        clave = self._clave_criterio_seleccionado
        if clave and clave in self.tree_criterios_todos.get_children():
            self.tree_criterios_todos.selection_set(clave)

    def _pintar_recuento(self, pendientes, mostrados):
        """
        «33 de 69 pendientes», y cuantas filas enseña y esconde el filtro.

        Los numeros salen del MISMO recorrido que pinta la tabla, no de un
        conteo aparte: un recuento calculado por su cuenta puede decir un
        numero mientras la tabla muestra otro, y entonces el que sobra es el
        recuento.

        LOS PENDIENTES SE CUENTAN SOBRE LOS 69, NO SOBRE LO FILTRADO, y es la
        mitad de lo que hace util este filtro. Un filtro que ademas moviera el
        recuento contestaria "te quedan 11" cuando lo cierto es "te quedan 33,
        de los que 11 los puede invocar esta corrida": la primera frase es la
        que hace que un criterio del expediente se olvide.
        """
        total = len(ca.CRITERIOS)
        texto = f"{pendientes} de {total} pendientes"
        if mostrados != total:
            # DOS NUMEROS Y NO UNO. "el filtro muestra 36" deja al lector
            # restando para saber cuantas filas dejo de ver, y esa resta es
            # justo la que hace falta para confiar en un filtro: lo que
            # esconde tiene que ser tan visible como lo que enseña. Los dos
            # salen del mismo recorrido que pinta la tabla.
            texto += (f"  |  el filtro muestra {mostrados} y esconde "
                      f"{total - mostrados}")
        # Y SE DICE CUANDO UNA DE ESAS FILAS NO ENCAJA. La seleccionada se
        # muestra siempre --- si no, se esfumaria justo al declararla ---, y
        # sin decirlo el recuento parecia equivocado: "33 pendientes, el filtro
        # muestra 34" no se entiende hasta que alguien explica cual es la de
        # mas. La frase no dice «la seleccionada» a proposito: la fila forzada
        # se queda a la vista hasta el proximo refiltrado, de modo que despues
        # de pinchar en otra sigue siendo cierto que hay una que no encaja, y
        # deja de ser cierto que sea la seleccionada.
        if self._seleccion_fuera_del_filtro:
            texto += " (incluida 1 que no encaja, para no perderla de vista)"
        self.lbl_recuento_criterios.configurar(
            texto, comp.INSIGNIA_ERROR if pendientes else comp.INSIGNIA_OK)

    def _al_seleccionar_criterio(self, _evt=None):
        seleccion = self.tree_criterios_todos.selection()
        self.txt_detalle_criterio.configure(state="normal")
        self.txt_detalle_criterio.delete("1.0", "end")
        # La linea de estado se limpia AL CAMBIAR DE FILA, y solo entonces.
        # Sin limpiarla, el "Error: ..." de un criterio se quedaba escrito
        # debajo del siguiente, que es atribuirle a una fila el problema de
        # otra. Limpiandola SIEMPRE se rompia lo contrario: declarar reselecciona
        # la misma fila --- `_aplicar_valor_corrida` hace `selection_set` para
        # que no se pierda de vista ---, ese `selection_set` vuelve a entrar
        # aqui, y el mensaje de confirmacion que se acababa de escribir se
        # borraba antes de que nadie lo leyera. La condicion es el cambio de
        # clave, no el evento.
        nueva = seleccion[0] if seleccion else None
        if nueva != self._clave_criterio_seleccionado:
            self.lbl_estado_criterio.config(text="")
        if not seleccion:
            self._clave_criterio_seleccionado = None
            self.lbl_criterio_seleccionado.config(text="(ninguno seleccionado)")
            for boton in (self.btn_aplicar_corrida, self.btn_quitar_declarado,
                          self.btn_guardar_archivo, self.btn_ventana_norma):
                boton.deshabilitar(MOTIVO_SIN_CRITERIO)
            self.txt_detalle_criterio.configure(state="disabled")
            return

        clave = seleccion[0]
        c = ca.criterio(clave)
        self._clave_criterio_seleccionado = clave
        self.lbl_criterio_seleccionado.config(text=clave)

        # LA FUENTE VA PRIMERA. Es la que dice DE DONDE sale el valor --- lo
        # que la taxonomia de CLAUDE.md convierte en la pregunta central de
        # cada fila --- y en la tabla no cabe: la mediana de este campo son 280
        # caracteres y el mas largo tiene 4900, contra los ~45 que entran en la
        # columna. Ninguna anchura de columna arregla eso; el sitio donde el
        # texto entero cabe es este panel, y por eso encabeza.
        lineas = [
            f"Fuente        : {c.fuente}",
            f"Justificacion : {c.justificacion}",
            f"Se resuelve   : {ve.variable(clave).modo.value} "
            "(doble clic abre su ventana normativa)",
        ]
        procedencia = dec.procedencia_de(clave)
        if procedencia is not None:
            lineas.append(f"Procedencia   : {procedencia.como_texto()}")
        if c.reemplazado_por:
            lineas.append(f"Se sustituye por: {c.reemplazado_por}")
        if c.sensibilidad:
            lineas.append(f"Sensibilidad  : {c.sensibilidad}")
        if c.trazabilidad:
            lineas.append(f"Trazabilidad  : {c.trazabilidad}")
        if c.verificacion_pendiente:
            lineas.append(f">> VERIFICAR  : {c.verificacion_pendiente}")
        self.txt_detalle_criterio.insert("1.0", "\n".join(lineas))
        self.txt_detalle_criterio.configure(state="disabled")

        valor_actual = ca.criterio_efectivo(clave).valor
        # El editor primero y el literal despues, bajo la misma guardia de
        # sincronizacion: `set` dispara `_literal_cambio`, que repintaria el
        # editor recien montado con lo que acaba de pintar.
        self._montar_editor(clave, valor_actual)
        self._sincronizando_editor = True
        try:
            self.valor_declarado_var.set(self._literal_de(valor_actual))
        finally:
            self._sincronizando_editor = False

        en_caliente = ca.declarado_en_caliente(clave)
        # DECLARAR EN CALIENTE YA NO DEPENDE DE QUE EL CRITERIO ESTE VACIO.
        # La condicion era `c.valor is None or en_caliente`, y con ella un
        # criterio resuelto no se podia pisar para una corrida... mientras que
        # el boton rojo de al lado SI lo reescribia permanentemente. La puerta
        # ancha abierta y la estrecha cerrada: quien queria TANTEAR un espesor
        # tenia que modificar el expediente para hacer el ensayo.
        # Lo que sostiene que ahora se pueda no es este boton: es que un pisado
        # se rotula distinto (`_estado_criterio`), se filtra aparte y sale en
        # la memoria en su propio bloque con el valor del archivo al lado.
        # CARA DE SOLO LECTURA PARA EL CRITERIO QUE NO SE ELIGE (EXT-V-04,
        # la mitad de la pestaña 2). El nucleo ya lo rechazaba; lo que faltaba
        # era que la pestaña lo DIJERA antes de que el proyectista tecleara y
        # confirmara una escritura permanente que no iba a ocurrir. Los dos
        # botones que escriben se apagan con el motivo, el campo no se
        # teclea, y la ventana normativa sigue abriendose: es donde se lee de
        # que se deriva.
        derivado = isinstance(c.resolucion, Derivada)
        if derivado:
            motivo = self._motivo_derivado(c.resolucion)
            self.btn_aplicar_corrida.deshabilitar(motivo)
            self.btn_guardar_archivo.deshabilitar(motivo)
            self.ent_valor_declarado.configure(state="disabled")
        else:
            self.btn_aplicar_corrida.habilitar()
            self.btn_guardar_archivo.habilitar()
            self.ent_valor_declarado.configure(state="normal")
        self.btn_quitar_declarado.estado(en_caliente, MOTIVO_NO_DECLARADO)
        self.btn_ventana_norma.habilitar()

    @staticmethod
    def _motivo_derivado(resolucion):
        return MOTIVO_DERIVADO.format(de=", ".join(resolucion.de),
                                      regla=resolucion.regla)

    def _abrir_ventana_normativa(self, _evt=None):
        """
        Abre la ventana emergente del criterio seleccionado.

        `al_declarar` refresca la tabla de esta pestana: la ventana declara
        por `declaracion`, que declara por `establecer_valor_dinamico`, y sin
        el refresco la fila seguiria diciendo PENDIENTE con el valor ya
        gobernando el calculo --- que es la forma que tenia SIS-A-01.
        """
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        ventana_norma.abrir(self.root, clave,
                            al_declarar=self._tras_declarar_en_ventana)

    def _tras_declarar_en_ventana(self, clave):
        # LA CLAVE SE ADOPTA ANTES DE REPINTAR. Es el unico de los cuatro
        # llamadores que recibe la clave por argumento en vez de leer la
        # seleccionada, y la emergente no es modal (`transient` sin
        # `grab_set`): entre abrirla y declarar, el usuario pudo tocar el
        # filtro por debajo y dejar `_clave_criterio_seleccionado` en otra cosa
        # --- o en None ---. Adoptarla aqui es lo que hace que
        # `_pasa_el_filtro` proteja ESTA fila y que reponer la seleccion
        # encuentre algo.
        self._clave_criterio_seleccionado = clave
        self._invalidar_informe(MOTIVO_INFORME_DESACTUALIZADO)
        self.lbl_estado_criterio.config(
            text=f"'{clave}' declarado desde su ventana normativa, SOLO para "
                 "la proxima corrida, con su procedencia registrada. "
                 "criterios_adoptados.py no se modifico.",
            foreground=COLOR_AVISO)
        self._llenar_tabla_criterios()
        self.tree_criterios_todos.selection_set(clave)

    def _interpretar_valor_declarado(self, texto):
        """
        Interpreta lo que el proyectista teclea en el campo de declaracion en
        caliente, con EL MISMO parser que la ventana emergente:
        `gui.componentes.interpretar_texto_declarado` (EXT-G-01, PC-13).
        Entero, real con coma o punto decimal, literal estructurado o texto;
        la regla entera y la politica de coma y miles estan escritas alli.

        SIS-E-04. El `ValueError` NO es de la taxonomia de `ErrorProyecto`,
        y es deliberado: un widget vacio todavia no es un dato del expediente
        -- no hay columna que añadir ni celda que corregir --, y la excepcion
        NUNCA sale de esta clase: los dos llamadores (`_aplicar_valor_corrida`
        y `_guardar_valor_en_archivo`) la atrapan tres lineas mas abajo y la
        convierten en el rotulo rojo del panel.

        DIVERGE de `cli.declarar_criterios`, y esta escrito para que se vea:
        la CLI resuelve el texto ENTERO con `ast.literal_eval` -- y asi leeria
        '1,5' como la TUPLA (1, 5), que desde EXT-1 rechaza en vez de aceptar
        en silencio -- mientras aqui se admite la coma decimal, que para
        quien teclea en la ventana es lo natural. Unificar las dos por el
        lado de la CLI convertiria '1,5' en una tupla valida en silencio, que
        es una regresion peor que la duplicacion. La divergencia esta fijada
        por un test de contrato en tests/test_gui_contrato.py; el parser
        compartido es GUI-GUI.

        Hasta EXT-5 este metodo tenia su propio cuerpo y la emergente otro, y
        los dos hacian `float()` sobre todo lo que parecia numero: '1' era
        1.0 en los dos, y `M2.numero_de_celdas` exige un entero, de modo que
        desde la ventana ningun marco pasaba de M2 (PC-13).
        """
        return interpretar_texto_declarado(texto)

    # ------------------------------------------------------------------
    # El editor tipado y su sincronizacion con el literal (E-B, E10)
    # ------------------------------------------------------------------
    @staticmethod
    def _literal_de(valor):
        """
        El texto del literal para un valor: el texto MISMO si es un texto
        (el parser no quita comillas: `repr` de una cadena las ponia y
        «Aplicar» declaraba la clave entre comillas, auditoria adversarial de
        E-B), `repr` para todo lo demas, que el parser lee entero.
        """
        if valor is None:
            return ""
        return valor if isinstance(valor, str) else repr(valor)

    def _montar_editor(self, clave, valor_actual):
        """
        El editor de la forma de `clave`, montado bajo el literal y pintado
        con el valor efectivo. Un `Derivada` no tiene editor: no se elige.
        """
        if self.editor is not None:
            self.editor.desmontar()
            self.editor = None
        if isinstance(ca.criterio(clave).resolucion, Derivada):
            return
        self.editor = ged.construir_editor(
            self.f_editor, clave, color_neutro=self.color_neutro_editor,
            al_cambiar=self._editor_cambio)
        self.editor.marco.pack(fill="x")
        self.editor.poner_valor(valor_actual)
        self._editor_refleja_literal = True

    def _editor_cambio(self):
        """Un campo del editor cambio: el literal se reescribe con el valor entero."""
        if self.editor is None or self._sincronizando_editor:
            return
        try:
            valor = self.editor.valor()
        except ValueError:
            return          # un campo a medias: el literal conserva lo anterior
        self._sincronizando_editor = True
        try:
            self.valor_declarado_var.set(self._literal_de(valor))
            self._editor_refleja_literal = True
        finally:
            self._sincronizando_editor = False

    def _literal_cambio(self, *_args):
        """
        El literal cambio (tecleado a mano): el editor se repinta con el. Si
        el literal NO cabe en los campos --- un triple en una serie de
        pares, una clave que el dict no declara --- el editor se queda como
        estaba y DEJA DE SER LA FUENTE (`_editor_refleja_literal`): la
        primera version lo repintaba recortado y «Aplicar» declaraba el
        recorte con confirmacion verde (auditoria adversarial de E-B).
        """
        if self.editor is None or self._sincronizando_editor:
            return
        try:
            valor = self._interpretar_valor_declarado(self.valor_declarado_var.get())
        except ValueError:
            self._editor_refleja_literal = False    # a medias: no representa el literal
            return
        self._sincronizando_editor = True
        try:
            self.editor.poner_valor(valor)
            self._editor_refleja_literal = True
        except ValueError:
            self._editor_refleja_literal = False
        finally:
            self._sincronizando_editor = False

    def _valor_a_declarar(self, clave):
        """
        El valor que «Aplicar» y «Guardar» declaran: el que COMPONEN los
        campos del editor montado para esta clave, o el literal cuando el
        editor es el literal (o no hay editor de esta clave).

        No se lee el literal a ciegas: un campo del editor que no arma
        --- `n` = 0.05 fuera de su ventana, pintado en rojo --- deja el
        literal en el valor ANTERIOR, y declarar ese literal seria declarar
        un numero que el proyectista no esta viendo (medido en la ventana
        real de E-B). Con el editor como fuente, el rechazo nombra el campo.
        """
        editor = self.editor
        if (editor is not None and editor.esquema.clave == clave
                and editor.esquema.tipo_de_editor != sed.LITERAL
                and self._editor_refleja_literal):
            return editor.valor()
        return self._interpretar_valor_declarado(self.valor_declarado_var.get())

    def _fila_y_nota_del_editor(self, clave):
        """
        La fila elegida y la nota del editor, SOLO si el editor es de esta
        clave: un llamador que fija `_clave_criterio_seleccionado` sin pasar
        por la seleccion (los apoyos de la suite) no hereda la fila de otro.
        """
        if self.editor is None or self.editor.esquema.clave != clave:
            return "", ""
        return self.editor.fila(), self.editor.nota()

    def _aplicar_valor_corrida(self):
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        # TODO ENTRA EN EL TRY Y EN UNA SOLA LLAMADA (E-B, E10): el literal
        # se interpreta, se arma entero y `src.editores.declarar` lo somete
        # a la guardia en seco y lo enruta a la puerta de `declaracion.py`
        # que corresponde al modo del criterio --- desde la tabla con la
        # fila elegida (o la que la clave tecleada nombra), en rango, o
        # libre ---, que registra la PROCEDENCIA. Un rechazo --- forma,
        # ventana, un numero que DIFIERE de la celda sin nota, una adopcion
        # sin fila ni nota en un criterio de tabla --- sale como ValueError
        # y aqui se pinta; nada queda declarado a medias. Hasta E-B este
        # camino llamaba a `establecer_valor_dinamico` y OLVIDABA la
        # procedencia: un valor tecleado aqui no tenia origen que la memoria
        # pudiera imprimir.
        try:
            valor_nuevo = self._valor_a_declarar(clave)
            fila, nota = self._fila_y_nota_del_editor(clave)
            procedencia = sed.declarar(clave, valor_nuevo, fila=fila, nota=nota)
        except (ValueError, KeyError) as exc:
            self.lbl_estado_criterio.config(text=f"Error: {exc}", foreground=COLOR_ERROR)
            return
        # El informe de la ultima corrida ya no describe este estado (PC-15).
        self._invalidar_informe(MOTIVO_INFORME_DESACTUALIZADO)
        self.lbl_estado_criterio.config(
            text=f"'{clave}' declarado a {valor_nuevo!r} SOLO para la proxima corrida, "
                 f"con procedencia registrada ({procedencia.como_texto()}). "
                 "criterios_adoptados.py no se modifico.",
            foreground=COLOR_AVISO)
        # Sin `selection_set` detras: lo hace `_llenar_tabla_criterios`, que es
        # quien borra las filas y por tanto quien tiene que reponerla.
        self._llenar_tabla_criterios()

    def _quitar_valor_corrida(self):
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        # `dec.olvidar` retira el valor Y su procedencia. Retirar solo el
        # valor dejaria una procedencia hablando de un numero que ya no
        # gobierna nada, que es peor que no tener procedencia.
        # QUE PASA AL QUITAR DEPENDE DE QUE HABIA DEBAJO, y hasta aqui el
        # mensaje afirmaba una sola de las dos cosas. `quitar_valor_dinamico`
        # solo saca el override, de modo que `criterio_efectivo` cae al valor
        # del ARCHIVO: si el criterio estaba vacio, vuelve a bloquear; si
        # estaba pisado, vuelve al valor transcrito y no bloquea nada. Decir
        # «vuelve a bloquear el calculo» de un pisado es exactamente el defecto
        # que este cambio tenia que no cometer: un mensaje que describe un
        # estado distinto del que el programa acaba de dejar.
        valor_archivo = ca.criterio(clave).valor
        dec.olvidar(clave)
        self._invalidar_informe(MOTIVO_INFORME_DESACTUALIZADO)
        if valor_archivo is None:
            texto = (f"Se quito la declaracion de '{clave}': el criterio "
                     "vuelve a estar PENDIENTE y bloquea el calculo que lo "
                     "invoque.")
        else:
            texto = (f"Se quito el valor pisado de '{clave}': vuelve a "
                     f"gobernar el del archivo, {valor_archivo!r}. No bloquea "
                     "nada.")
        self.lbl_estado_criterio.config(text=texto, foreground=COLOR_AVISO)
        self._llenar_tabla_criterios()

    def _guardar_valor_en_archivo(self):
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        try:
            valor_nuevo = self._valor_a_declarar(clave)
        except ValueError as exc:
            self.lbl_estado_criterio.config(text=f"Error: {exc}", foreground=COLOR_ERROR)
            return

        confirmado = messagebox.askyesno(
            "Confirmar escritura permanente",
            f"Esto reescribe 'valor=' de '{clave}' en criterios_adoptados.py "
            f"con el valor {valor_nuevo!r}.\n\n"
            "Es un cambio PERMANENTE al archivo fuente del proyecto, no solo "
            "a esta corrida. Etiqueta, justificacion y fuente del criterio "
            "no se actualizan solos: revisalas a mano si corresponde.\n\n"
            "¿Confirma que quiere escribir el archivo?",
            icon="warning",
        )
        if not confirmado:
            return
        try:
            ca.escribir_valor_en_archivo(clave, valor_nuevo)
        except (KeyError, ValueError, OSError) as exc:
            messagebox.showerror("No se pudo escribir el archivo", str(exc))
            return
        self._invalidar_informe(MOTIVO_INFORME_DESACTUALIZADO)
        self.lbl_estado_criterio.config(
            text=f"'{clave}' = {valor_nuevo!r} escrito en criterios_adoptados.py.",
            foreground=COLOR_OK)
        self._llenar_tabla_criterios()

    # -------------------------- Pestana 3 -----------------------------
    def _construir_tab_puntos(self, p):
        p.columnconfigure(0, weight=1)
        # La fila 0 es la cabecera de la vista; la 1, la tabla, y la 2 el
        # detalle: las dos ultimas crecen.
        p.rowconfigure(1, weight=1)

        self._cabecera_de_vista(p, self.tab_puntos).grid(row=0, column=0, sticky="ew",
                                           padx=14, pady=(12, 10))
        panel_tabla = Panel(p, "Resultados de la ultima corrida")
        panel_tabla.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
        f_tabla = panel_tabla.interior
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        cols = ("id", "progresiva", "familia", "dimensionado", "material",
                "seccion", "control", "HW", "V_erosion", "V_sedimentacion",
                "incumplidas", "bloqueos")
        self.tree_puntos = ttk.Treeview(f_tabla, columns=cols, show="headings", height=14)
        encabezados = [
            ("id", "Punto", 70, "w"),  # literal-ok: ancho de columna, px
            ("progresiva", "Progresiva", 90, "center"),  # literal-ok: ancho de columna, px
            ("familia", "Familia", 60, "center"),  # literal-ok: ancho de columna, px
            ("dimensionado", "Dimensionado", 105, "center"),  # literal-ok: ancho de columna, px
            ("material", "Material", 140, "w"),  # literal-ok: ancho de columna, px
            # LA COLUMNA DICE LA SECCION Y NO UN DIAMETRO (C8). Con «D (m)»,
            # un marco de 1.20 x 0.90 y otro de 2.00 x 0.90 salian los dos
            # «0.90» en el tablero, que es la mitad que no gobierna la
            # capacidad. Va mas ancha porque «marco 1.20 x 0.90 m» no cabe en
            # el ancho de un diametro.
            ("seccion", "Seccion", 130, "center"),  # literal-ok: ancho de columna, px
            ("control", "Control", 75, "center"),  # literal-ok: ancho de columna, px
            ("HW", "HW (m)", 70, "center"),  # literal-ok: ancho de columna, px
            # Dos columnas, no una: la velocidad contra los techos (V3, d50)
            # y la del piso (V2) se calculan con n distinto y no son el mismo
            # numero (MAT-D1).
            ("V_erosion", "V n min (m/s)", 90, "center"),  # literal-ok: ancho de columna, px
            ("V_sedimentacion", "V n max (m/s)", 90, "center"),  # literal-ok: ancho de columna, px
            ("incumplidas", "Verif. NO", 75, "center"),  # literal-ok: ancho de columna, px
            ("bloqueos", "Bloqueos", 75, "center"),  # literal-ok: ancho de columna, px
        ]
        for col, txt, ancho, anchor in encabezados:
            self.tree_puntos.heading(col, text=txt)
            self.tree_puntos.column(col, width=ancho, anchor=anchor)
        self.tree_puntos.grid(row=0, column=0, sticky="nsew")
        self.tree_puntos.tag_configure("no_dimensionado", background=comp.ROJO_SUAVE,
                                       foreground=COLOR_ERROR)
        self.tree_puntos.tag_configure("con_bloqueos", foreground=COLOR_AVISO)
        self.tree_puntos.bind("<<TreeviewSelect>>", self._al_seleccionar_punto)

        scroll = ttk.Scrollbar(f_tabla, orient="vertical", command=self.tree_puntos.yview)
        self.tree_puntos.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        panel_detalle = Panel(p, "Detalle del punto seleccionado")
        panel_detalle.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 12))
        p.rowconfigure(2, weight=1)
        f_encabezado = ttk.Frame(panel_detalle.interior)
        f_encabezado.pack(fill="x")
        # La traza de procedencia (G4). El contenido lo produce
        # `src/traza_punto.py`; el boton solo abre la ventana que lo pinta.
        self.btn_traza = BotonAccion(
            f_encabezado, "¿De donde sale este numero?", fondo=comp.AZUL,
            activebackground=comp.AZUL_OSCURO, activeforeground="white",
            command=self._abrir_traza_punto, motivo=MOTIVO_SIN_CORRIDA,
            letra=BotonAccion.DISCRETA,
            ayuda="Los PasoDeMemoria del punto seleccionado, en el orden en\n"
                  "que la memoria los imprime: que se calculo y por que, la\n"
                  "formula con su cita, la sustitucion con la procedencia de\n"
                  "cada valor, el umbral con su caracter y el veredicto con\n"
                  "su margen. Las verificaciones sin paso salen con su hueco\n"
                  "declarado, nunca en blanco.")
        self.btn_traza.pack(side="left", ipadx=6)

        f_detalle = ttk.Frame(panel_detalle.interior)
        f_detalle.pack(fill="both", expand=True, pady=(8, 0))
        f_detalle.columnconfigure(0, weight=1)
        f_detalle.rowconfigure(0, weight=1)

        self.txt_detalle = comp.texto_plano(f_detalle, height=12, wrap="word")
        self.txt_detalle.grid(row=0, column=0, sticky="nsew")
        self.txt_detalle.configure(state="disabled")
        scroll_det = ttk.Scrollbar(f_detalle, orient="vertical", command=self.txt_detalle.yview)
        self.txt_detalle.configure(yscroll=scroll_det.set)
        scroll_det.grid(row=0, column=1, sticky="ns")

    def _al_seleccionar_punto(self, _evt=None):
        informe_punto = self._punto_seleccionado()
        self.txt_detalle.configure(state="normal")
        self.txt_detalle.delete("1.0", "end")
        if informe_punto is not None:
            self.txt_detalle.insert("1.0", "\n".join(cli._lineas_punto(informe_punto)))
        self.txt_detalle.configure(state="disabled")
        self.btn_traza.estado(informe_punto is not None, MOTIVO_SIN_PUNTO)

    def _punto_seleccionado(self):
        """El InformePunto de la fila seleccionada, o None."""
        seleccion = self.tree_puntos.selection()
        if not seleccion or self.informe is None:
            return None
        id_punto = seleccion[0]
        return next((i for i in self.informe.puntos if i.punto.id == id_punto), None)

    def _abrir_traza_punto(self):
        """
        «¿De donde sale este numero?»: la traza de procedencia del punto.

        El CONTENIDO --- que pasos, en que orden, con que rotulos y en cual de
        los tres registros va cada linea --- lo produce
        `traza_punto.traza_del_punto`, que consume la misma seleccion que
        M11. Aqui no se decide nada de eso: se pinta.
        """
        informe_punto = self._punto_seleccionado()
        if informe_punto is None:
            return
        self._pintar_traza(tp.traza_del_punto(informe_punto))

    def _pintar_traza(self, traza):
        """
        Pinta una `TrazaDelPunto` en un Toplevel de solo lectura.

        LOS TRES REGISTROS SE PINTAN DISTINTOS, y no es estilo (NOR-HID-04):
        lo que la fuente dice va en cursiva sobre fondo neutro (la clase
        `.fuente` de la memoria HTML), lo que el proyecto lee sobre fondo
        ambar (`.interpretacion`), y lo que el proyecto hace en texto normal.
        Los tags reciben el NOMBRE del registro que declara cada
        `LineaDeTraza`: si la capa de contenido añade un registro nuevo sin
        estilo, la linea sale en texto normal en vez de perderse.
        """
        ventana = tk.Toplevel(self.root, background=comp.SUPERFICIE)
        ventana.title(f"Traza de procedencia - {traza.id_punto}")
        ventana.bind("<Escape>", lambda _evt: ventana.destroy())   # PC-17
        ventana.geometry("980x680")  # literal-ok: tamano inicial de la ventana, px
        ventana.columnconfigure(0, weight=1)
        ventana.rowconfigure(0, weight=1)

        ui = self.tipografia.ui
        texto = tk.Text(ventana, wrap="word", font=ui(comp.CUERPO_PT),
                        background=comp.SUPERFICIE, foreground=comp.TEXTO,
                        relief="flat", padx=12, pady=10)  # literal-ok: margenes del texto, px
        texto.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(ventana, orient="vertical", command=texto.yview)
        texto.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        texto.tag_configure("titulo_punto", font=ui(comp.TITULO_PT, "bold"),
                            spacing3=8)  # literal-ok: espaciado, px
        texto.tag_configure("seccion", font=ui(comp.CUERPO_PT, "bold"),
                            spacing1=12, spacing3=4,  # literal-ok: espaciado, px
                            underline=True)
        texto.tag_configure("aviso", foreground=COLOR_AVISO,
                            lmargin1=12, lmargin2=12)  # literal-ok: sangria, px
        texto.tag_configure("entrada", font=ui(comp.CUERPO_PT, "bold"),
                            spacing1=8)  # literal-ok: espaciado, px
        texto.tag_configure("hueco", foreground=COLOR_AVISO,
                            font=ui(comp.CUERPO_PT, "bold"),
                            spacing1=8)  # literal-ok: espaciado, px
        texto.tag_configure("rotulo", font=ui(comp.CUERPO_PT, "bold"),
                            lmargin1=16, lmargin2=16)  # literal-ok: sangria, px
        # Los tres registros de la §4.4, con los mismos papeles que las
        # clases CSS .fuente / .interpretacion / texto normal de la memoria.
        texto.tag_configure(tp.REGISTRO_FUENTE, font=ui(comp.CUERPO_PT, "italic"),
                            background=comp.FONDO,
                            lmargin1=28, lmargin2=28)  # literal-ok: sangria, px
        texto.tag_configure(tp.REGISTRO_INTERPRETACION, background=comp.AMBAR_SUAVE,
                            lmargin1=28, lmargin2=28)  # literal-ok: sangria, px
        texto.tag_configure(tp.REGISTRO_PROYECTO,
                            lmargin1=28, lmargin2=28)  # literal-ok: sangria, px

        texto.insert("end", traza.titulo + "\n", "titulo_punto")
        texto.insert("end",
                     "Cursiva sobre fondo gris: lo que la fuente DICE. "
                     "Fondo ambar: lo que el proyecto LEE. "
                     "Texto normal: lo que el proyecto HACE.\n", "aviso")
        for seccion in traza.secciones:
            texto.insert("end", seccion.titulo + "\n", "seccion")
            if seccion.aviso:
                texto.insert("end", seccion.aviso + "\n", "aviso")
            for entrada in seccion.entradas:
                tag = ("hueco" if entrada.titulo == tp.TITULO_HUECO
                       else "entrada")
                codigo = f"{entrada.codigo} - " if entrada.codigo else ""
                texto.insert("end", f"{codigo}{entrada.titulo}\n", tag)
                for linea in entrada.lineas:
                    texto.insert("end", f"{linea.rotulo}:\n", "rotulo")
                    texto.insert("end", linea.texto + "\n", linea.registro)
        texto.configure(state="disabled")

    # -------------------------- Pestana 4 -----------------------------
    def _construir_tab_resumen(self, p):
        self._cabecera_de_vista(p, self.tab_resumen).pack(anchor="w", fill="x", pady=(0, 12))

        panel_resumen = Panel(p, "Estado del expediente")
        panel_resumen.pack(fill="x", pady=(0, 10))
        f_res = panel_resumen.interior
        f_res.columnconfigure(1, weight=1)

        # Dos clases de fila: las que dicen un DATO (el CSV y el alcance, en
        # monoespaciada) y las que dicen un ESTADO (las seis cuentas y el
        # cierre), que son INSIGNIAS: el numero o el «si/no» como texto, y el
        # fondo suave del estado que `_llenar_resumen` les da al pintar.
        etiquetas = ["CSV", "Alcance de la corrida", "Puntos del expediente",
                     "Puntos dimensionados", "Verificaciones incumplidas",
                     "Etapas bloqueadas", "Diferidas por alcance",
                     "Expediente cerrado"]
        de_dato = {"CSV", "Alcance de la corrida"}
        self.lbl_resumen = {}
        for fila, txt in enumerate(etiquetas):
            ttk.Label(f_res, text=f"{txt}:").grid(row=fila, column=0, sticky="w", pady=3)
            if txt in de_dato:
                lbl = ttk.Label(f_res, text="-", style="Res.TLabel")
            else:
                lbl = Insignia(f_res, "-", comp.INSIGNIA_NEUTRA)
            lbl.grid(row=fila, column=1, sticky="w", padx=12, pady=3)
            self.lbl_resumen[txt] = lbl

        panel_bloqueos = Panel(p, "Criterios pendientes que bloquearon una etapa (Sec. 0.7)")
        panel_bloqueos.pack(fill="x", pady=(0, 10))
        ttk.Label(panel_bloqueos.interior,
                  text="Un criterio con valor=None cuya etapa se invoco en esta corrida. "
                       "No es un defecto silencioso: el calculo se detuvo hasta declararlo.",
                  style="Ayuda.TLabel", wraplength=820, justify="left").pack(anchor="w", pady=(0, 8))

        f_crit = ttk.Frame(panel_bloqueos.interior)
        f_crit.pack(fill="both", expand=False)
        # RESPONSABLE Y EVIDENCIA (E-B, E13 reducido): QUIEN aporta el valor
        # y CON QUE se sostiene, derivados de la ficha por `src/responsable.py`
        # y traidos en `CriterioBloqueante`. La pestaña pinta; no escribe.
        cols = ("clave", "etiqueta", "concepto", "fuente", "fases", "puntos",
                "responsable", "evidencia")
        self.tree_criterios = ttk.Treeview(f_crit, columns=cols, show="headings", height=8)
        encabezados = [
            ("clave", "Clave", 130, "w"),  # literal-ok: ancho de columna, px
            ("etiqueta", "Etiqueta", 60, "center"),  # literal-ok: ancho de columna, px
            ("concepto", "Concepto", 220, "w"),  # literal-ok: ancho de columna, px
            ("fuente", "Fuente que lo resolveria", 220, "w"),  # literal-ok: ancho de columna, px
            ("fases", "Fases", 140, "w"),  # literal-ok: ancho de columna, px
            ("puntos", "Puntos", 140, "w"),  # literal-ok: ancho de columna, px
            ("responsable", "Responsable (quien lo fija)", 220, "w"),  # literal-ok: ancho de columna, px
            ("evidencia", "Evidencia (que lo sostiene)", 220, "w"),  # literal-ok: ancho de columna, px
        ]
        for col, txt, ancho, anchor in encabezados:
            self.tree_criterios.heading(col, text=txt)
            self.tree_criterios.column(col, width=ancho, anchor=anchor)
        self.tree_criterios.pack(side="left", fill="both", expand=True)
        scroll_c = ttk.Scrollbar(f_crit, orient="vertical", command=self.tree_criterios.yview)
        self.tree_criterios.configure(yscroll=scroll_c.set)
        scroll_c.pack(side="left", fill="y")

        panel_exportacion = Panel(p, "Exportacion")
        panel_exportacion.pack(fill="x", pady=(0, 10))
        p = panel_exportacion.interior
        f_exp = ttk.Frame(p)
        f_exp.pack(fill="x")

        # LOS CUATRO NACEN APAGADOS Y DICIENDO POR QUE. El motivo es siempre
        # el mismo --- no hay informe hasta que se ejecuta el pipeline --- y
        # hasta aqui no estaba escrito en ningun sitio: los botones salian
        # grises y el usuario tenia que deducirlo. Es el bloqueo mas frecuente
        # de esta ventana y era el unico mudo.
        self.btn_json = BotonAccion(
            f_exp, "Exportar JSON", fondo=comp.VERDE,
            command=self.exportar_json, motivo=MOTIVO_SIN_CORRIDA,
            ayuda="El informe completo de la corrida en JSON.")
        self.btn_json.pack(side="left", padx=(0, 8), ipadx=8, ipady=4)

        self.btn_html = BotonAccion(
            f_exp, "Exportar memoria (HTML)", fondo=comp.AZUL,
            activebackground=comp.AZUL_OSCURO, activeforeground="white",
            command=self.exportar_html, motivo=MOTIVO_SIN_CORRIDA,
            ayuda="La memoria de calculo (M11) con la plantilla que\n"
                  "corresponde al alcance de la corrida.")
        self.btn_html.pack(side="left", padx=8, ipadx=8, ipady=4)

        self.btn_pdf = BotonAccion(
            f_exp, "Exportar memoria (PDF)", fondo=comp.AZUL_OSCURO,
            command=self.exportar_pdf, motivo=MOTIVO_SIN_CORRIDA,
            ayuda=self._ayuda_del_pdf())
        self.btn_pdf.pack(side="left", padx=8, ipadx=8, ipady=4)

        self.btn_csv = BotonAccion(
            f_exp, "Exportar cuadro resumen (CSV)", fondo=comp.VERDE,
            command=self.exportar_csv, motivo=MOTIVO_SIN_CORRIDA,
            ayuda="El cuadro resumen (entregable 3 de M11), una fila\n"
                  "por punto, en una hoja de calculo.")
        self.btn_csv.pack(side="left", padx=8, ipadx=8, ipady=4)

        # COMPARAR CON OTRO VOLCADO (E-B, E14): el `informe_json` de ESTA
        # corrida --- el mismo que se embebe en la sesion, fotografiado al
        # correr --- contra un JSON del disco, por `src/comparador.py`. Nunca
        # recalcula: compara dos volcados.
        self.btn_comparar = BotonAccion(
            f_exp, "Comparar con otro JSON...", fondo=comp.TEXTO_SUAVE,
            command=self.comparar_informe, motivo=MOTIVO_SIN_CORRIDA,
            ayuda="Compara el volcado de esta corrida con otro informe_json\n"
                  "(otra version del CSV, de los criterios o del codigo), por\n"
                  "identidad de punto y con tolerancias nombradas. Dice que\n"
                  "campo difiere en que punto, y que no se puede comparar y\n"
                  "por que (metodos distintos). No corre nada.")
        self.btn_comparar.pack(side="left", padx=8, ipadx=8, ipady=4)

        # EL MOTIVO DEL BLOQUEO, A LA VISTA (EXT-8, PC-17). Los cuatro
        # exportadores comparten motivo --- se apagan y encienden juntos ---,
        # y un solo rotulo debajo de la fila lo dice sin pasar el raton. El
        # texto lo escribe `BotonAccion`, el mismo que va al tooltip.
        self.btn_json.con_rotulo(p, style="Ayuda.TLabel", wraplength=820,  # literal-ok: ancho de ajuste del rotulo, px
                                 justify="left").pack(anchor="w", pady=(6, 0))

        # LA FILA DEL PDF EN MARCHA (EXT-8, PC-11): progreso, cancelar y el
        # estado terminal, visibles mientras y despues de exportar.
        f_pdf = ttk.Frame(p)
        f_pdf.pack(fill="x", pady=(6, 0))
        self.lbl_estado_pdf = ttk.Label(f_pdf, text="", style="Ayuda.TLabel",
                                        wraplength=700, justify="left")
        self.lbl_estado_pdf.pack(side="left", fill="x", expand=True)
        self.btn_cancelar_pdf = BotonAccion(
            f_pdf, "Cancelar PDF", letra=BotonAccion.DISCRETA,
            command=self._cancelar_pdf, motivo="no hay ninguna exportacion en marcha",
            ayuda="Termina el proceso que esta escribiendo el PDF.\n"
                  "No queda ningun archivo a medias.")
        self.btn_cancelar_pdf.pack(side="right", padx=(8, 0), ipadx=6)
        self.proceso_pdf = None

    def _ayuda_del_pdf(self):
        """
        Por que via saldra el PDF, DICHO ANTES DE PULSAR y no despues.

        `M11_reporte` intenta `from weasyprint import HTML` dentro de un
        `except Exception` --- que atrapa tanto el `ImportError` de «no esta
        instalado» como el `OSError` de «esta instalado y sus librerias
        nativas no cargan», que es el caso de Windows sin GTK ---. Si no
        cargo, la exportacion NO falla: escribe el HTML y lo abre en el
        navegador para imprimirlo con Ctrl+P. Eso funciona, y aun asi conviene
        decirlo de antemano: quien pulsa «Exportar memoria (PDF)» y ve
        aparecer un navegador cree que algo se rompio.

        Se lee `WeasyHTML` --- el MISMO simbolo que decide la via --- y no una
        comprobacion propia: dos formas de preguntar «¿hay weasyprint?» son
        dos respuestas que pueden discrepar, y la que veria el usuario seria
        la equivocada.
        """
        # La sonda carga weasyprint UNA vez por proceso (perezoso desde
        # EXT-8); despues, `WeasyHTML` sigue siendo el simbolo que decide.
        M11.weasyprint_disponible()
        limite = (f"Limite {expdf.LIMITE_MEDIDO_PDF}.\n"
                  f"Por encima de {expdf.UMBRAL_PUNTOS_PDF} puntos se ofrece la\n"
                  "via del navegador (HTML + Ctrl+P), que pagina lo mismo\n"
                  "sin que este programa pague la memoria.")
        if M11.WeasyHTML is not None:
            return ("Escribe el PDF con weasyprint EN UN PROCESO APARTE:\n"
                    "la ventana sigue viva, el progreso se ve abajo y se\n"
                    "puede cancelar. La hoja ya esta configurada en A4.\n"
                    + limite)
        return ("weasyprint no esta operativo en esta maquina: o no esta\n"
                "instalado, o esta instalado y sus librerias nativas (GTK,\n"
                "cairo, pango) no cargan --- lo corriente en Windows ---.\n"
                "NO es un bloqueo: al pulsar se escribe la memoria en HTML\n"
                "junto al destino que elijas y se abre en el navegador para\n"
                "guardarla como PDF con Ctrl+P (la hoja ya esta en A4).\n"
                + limite)

    # ------------------------------------------------------------------
    # Lectura de banderas
    # ------------------------------------------------------------------
    def _leer_banderas(self):
        """
        Los valores de texto de CAMPOS_EXTERNOS, tal como los espera
        `cargar_datos_externos`: None si el campo quedo vacio.
        """
        # La traduccion rotulo-de-ventana -> clave-de-expediente es la de
        # `CLAVE_EXTERNA_DE_CAMPO` (de `src/sesion.py`), y la regla de la
        # coma decimal tambien: `sesion.banderas_de_externos` es lo MISMO que
        # la CLI aplica al leer una sesion guardada, de modo que la corrida
        # de la ventana y la del subproceso del PDF traducen igual.
        textos = {clave: self.externos_vars[clave].get()
                  for clave in self.CLAVE_EXTERNA_DE_CAMPO}
        return ses.banderas_de_externos(textos)

    # ------------------------------------------------------------------
    # Ejecucion del pipeline
    # ------------------------------------------------------------------
    def ejecutar_pipeline(self):
        self.lbl_error_datos.config(text="")
        ruta_csv_texto = self.csv_var.get().strip()
        if not ruta_csv_texto:
            self.lbl_error_datos.config(text="Debe seleccionar el CSV de puntos críticos.")
            self.nb.select(self.tab_datos)
            return
        ruta_csv = Path(ruta_csv_texto)

        ruta_externos = None
        texto_externos = self.datos_externos_var.get().strip()
        if texto_externos:
            ruta_externos = Path(texto_externos)

        self.btn_ejecutar.deshabilitar(MOTIVO_EJECUTANDO)
        self.btn_ejecutar.config(text="Ejecutando...")
        # EL INFORME ANTERIOR DEJA DE ESTAR VIGENTE ANTES DE CORRER (PC-15):
        # si esta corrida falla, las pestañas 3 y 4, la barra y los cuatro
        # exportadores no pueden seguir presentando la corrida anterior como
        # si fuera esta. Y el nombre del proyecto se toma AHORA.
        self._invalidar_informe(MOTIVO_EJECUTANDO)
        self.proyecto_de_la_corrida = self.proyecto_var.get()
        # Y LAS ENTRADAS DE LA CORRIDA SE FOTOGRAFIAN AHORA (EXT-8): son las
        # que el subproceso del PDF recibe. Leerlas al exportar --- con el
        # radio o la luz cambiados despues de correr --- mandaria al hijo a
        # calcular otra obra (auditoria adversarial de EXT-8).
        texto_sitio = self.datos_sitio_var.get().strip()
        self.entradas_de_la_corrida = {
            "csv": ruta_csv_texto,
            "datos_externos": texto_externos,
            "datos_sitio": texto_sitio,
            "externos": {clave: var.get() for clave, var in self.externos_vars.items()},
            "alcance": self.alcance_var.get(),
        }
        self.root.update_idletasks()
        # LOS DATOS DE SITIO DE LA OBRA (EXT-10), ANTES DE CORRER: si hay
        # ruta, se declaran por sesion sustituyendo lo que otra obra hubiera
        # declarado; sin ruta se conserva lo que la sesion abierta trajo. Su
        # rechazo es el de una DECLARACION y se atrapa en su propio metodo
        # (no aqui: `ejecutar_pipeline` no captura ValueError, SIS-E-01), con
        # el mismo brazo que la CLI usa para `--datos-sitio`.
        rechazo = self._declarar_datos_de_sitio(texto_sitio)
        if rechazo is not None:
            self._mostrar_error_entrada(rechazo)
            self.btn_ejecutar.habilitar()
            self.btn_ejecutar.config(text=TEXTO_BOTON_EJECUTAR)
            return
        try:
            externos = cli.cargar_datos_externos(ruta_externos, self._leer_banderas())
            self.informe = cli.correr(ruta_csv, externos,
                                      alcance=self.alcance_var.get())
        # SIS-E-01. Este brazo capturaba (OSError, ValueError), y ValueError
        # es la excepcion mas comun de un fallo de PROGRAMA nacido dentro del
        # pipeline: cualquiera de ellos se mostraba al proyectista como "No se
        # pudo leer la entrada", que le hace revisar el CSV en vez de reportar
        # el defecto, y ademas se comia el brazo de abajo, que es el que
        # imprime la traza. La CLI ya usaba el brazo estrecho correcto
        # (cli.py::main). Las TRES formas en que la ENTRADA puede fallar al
        # LEERSE: la de E/S (OSError), la del texto que no es UTF-8
        # (UnicodeDecodeError, que es subclase de ValueError y por lo tanto no
        # entra sola) y la del JSON mal formado. La segunda no es teorica en
        # este expediente: un CSV o un JSON guardado en ANSI por Excel en
        # Windows -- con las eñes del castellano -- estrellaria la ventana con
        # una traza en vez de decir que el archivo no esta en UTF-8.
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._mostrar_error_entrada(f"No se pudo leer la entrada:\n{exc}")
            return
        except ErrorProyecto as exc:
            self._mostrar_error_entrada(f"El expediente no se puede cargar:\n{exc}")
            return
        except Exception as exc:  # fallo de programa: se muestra con traza
            traceback.print_exc()
            self._apagar_exportadores(MOTIVO_CORRIDA_FALLIDA)
            self.lbl_estado.config(
                text=f"Sin informe vigente: {MOTIVO_CORRIDA_FALLIDA}.")
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")
            return
        finally:
            self.btn_ejecutar.habilitar()
            self.btn_ejecutar.config(text=TEXTO_BOTON_EJECUTAR)

        # LA CORRIDA SE EMBEBE EN LA SESION (E04): con su `informe_json`,
        # para que quien la abra despues pueda saber si la reproduce.
        # El volcado se fotografia AQUI y el comparador de la pestaña 4 lo
        # lee de aqui (E14): compara la corrida hecha, no una nueva.
        self.volcado_de_la_corrida = cli.informe_json(self.informe)
        self.corridas.append(ses.corrida_para_sesion(
            self.informe, self.volcado_de_la_corrida))
        self._llenar_tabla_puntos()
        self._llenar_resumen()
        # La pestana 2 se repinta porque acaba de aparecer el tercer filtro:
        # sin corrida, «solo los que bloquearon esta corrida» no tiene conjunto
        # que aplicar; con ella, ya lo tiene. Repintar aqui es lo que hace que
        # el filtro exacto este disponible en el momento en que se vuelve
        # exacto.
        self._llenar_tabla_criterios()
        for btn in (self.btn_json, self.btn_html, self.btn_pdf, self.btn_csv,
                    self.btn_comparar):
            btn.habilitar()
        # La via del PDF se relee AQUI y no solo al construir la ventana: es
        # barato y evita que la ayuda hable de una maquina distinta de la que
        # acaba de correr.
        self.btn_pdf.ayuda = self._ayuda_del_pdf()
        self.btn_pdf.tooltip.texto = self.btn_pdf.ayuda
        r = self.informe.resumen()
        self.lbl_estado.config(
            text=f"Ejecutado ({self.informe.generado}). "
                 f"{r.dimensionados}/{r.puntos} puntos dimensionados. "
                 f"Expediente {'cerrado' if r.cerrado else 'NO cerrado'}.")
        self.nb.select(self.tab_puntos)

    def _declarar_datos_de_sitio(self, texto_sitio):
        """
        Que datos de sitio gobiernan la corrida, con LA MISMA regla que la
        CLI: el campo de la pestaña 1 (la ruta) gana al bloque `sitio` de la
        sesion abierta, y con el campo vacio gobierna ese bloque --- que es
        vacio en un proyecto nuevo, y entonces gobierna `datos_sitio.py` ---.
        Borrar el campo retira, por tanto, lo que la ruta trajo. Devuelve el
        motivo del rechazo, o None. El brazo es el de una declaracion
        (`(ValueError, KeyError)`, el mismo que `cli.main`) y vive aqui y no
        en `ejecutar_pipeline`, que no captura ValueError (SIS-E-01).
        """
        try:
            if texto_sitio:
                cli.cargar_datos_sitio(Path(texto_sitio))
            else:
                dec.restaurar_datos_de_sitio(self.sitio_de_la_sesion, sustituir=True,
                                             origen="sesion abierta")
        except (ValueError, KeyError) as exc:
            return f"No se pudo declarar el dato de sitio:\n{exc}"
        return None

    def _mostrar_error_entrada(self, mensaje):
        self.lbl_error_datos.config(text=mensaje)
        # Los exportadores dicen que esta corrida no dejo informe (PC-15).
        self._apagar_exportadores(MOTIVO_CORRIDA_FALLIDA)
        self.lbl_estado.config(text=f"Sin informe vigente: {MOTIVO_CORRIDA_FALLIDA}.")
        self.nb.select(self.tab_datos)
        self.btn_ejecutar.habilitar()
        self.btn_ejecutar.config(text=TEXTO_BOTON_EJECUTAR)

    # ------------------------------------------------------------------
    # Volcado a las tablas
    # ------------------------------------------------------------------
    def _llenar_tabla_puntos(self):
        for item in self.tree_puntos.get_children():
            self.tree_puntos.delete(item)
        for informe_punto in self.informe.puntos:
            punto = informe_punto.punto
            incumplidas = len(informe_punto.incumplidas())
            # Los REALES: lo diferido por alcance no es un bloqueo del punto
            # y no cuenta para el cierre (EXT-G-02).
            n_bloqueos = len(informe_punto.bloqueos_reales())
            if informe_punto.dimensionado:
                r = informe_punto.resultado
                h = r.resultado_hidraulico
                material = r.material.nombre
                seccion = r.seccion.etiqueta()
                control, HW = h.control_gobernante.value, f"{h.HW:.3f}"
                V_ero = f"{h.V_erosion:.2f}"
                V_sed = f"{h.V_sedimentacion:.2f}"
            else:
                material = seccion = control = HW = V_ero = V_sed = "-"

            tags = []
            if not informe_punto.dimensionado:
                tags.append("no_dimensionado")
            if n_bloqueos:
                tags.append("con_bloqueos")

            self.tree_puntos.insert("", "end", iid=punto.id, values=(
                punto.id, punto.progresiva_display, punto.familia.value,
                "si" if informe_punto.dimensionado else "no",
                material, seccion, control, HW, V_ero, V_sed, incumplidas,
                n_bloqueos,
            ), tags=tuple(tags))

        self.txt_detalle.configure(state="normal")
        self.txt_detalle.delete("1.0", "end")
        self.txt_detalle.configure(state="disabled")

    def _llenar_resumen(self):
        informe = self.informe
        # LAS CIFRAS LAS DA EL INFORME, NO ESTA VENTANA (EXT-G-02): la GUI
        # decia «Etapas bloqueadas: 12» y la CLI, sobre el mismo `Informe`, 1,
        # porque aqui se contaba `len(bloqueos())` con lo diferido dentro.
        # `Informe.resumen` es la unica cuenta y las tres capas la leen.
        r = informe.resumen()
        self.lbl_resumen["CSV"].config(text=str(informe.csv))
        self.lbl_resumen["Alcance de la corrida"].config(text=informe.alcance)
        # Lo diferido por alcance NO es un bloqueo y no cuenta para `cerrado`:
        # es una etapa que ESTA corrida declaro fuera de su alcance. Se
        # imprime aparte, con su fundamento, porque «cerrado a nivel de
        # perfil» no significa que el expediente este completo.
        # Cada insignia lleva el numero como TEXTO y el estado como fondo:
        # el color acompaña, no sustituye.
        self.lbl_resumen["Diferidas por alcance"].configurar(
            str(r.diferidas),
            comp.INSIGNIA_AVISO if r.diferidas else comp.INSIGNIA_OK)
        self.lbl_resumen["Puntos del expediente"].configurar(
            str(r.puntos), comp.INSIGNIA_INFO)
        self.lbl_resumen["Puntos dimensionados"].configurar(
            str(r.dimensionados),
            comp.INSIGNIA_OK if r.dimensionados == r.puntos else comp.INSIGNIA_AVISO)
        self.lbl_resumen["Verificaciones incumplidas"].configurar(
            str(r.incumplidas),
            comp.INSIGNIA_ERROR if r.incumplidas else comp.INSIGNIA_OK)
        self.lbl_resumen["Etapas bloqueadas"].configurar(
            str(r.bloqueadas),
            comp.INSIGNIA_AVISO if r.bloqueadas else comp.INSIGNIA_OK)
        self.lbl_resumen["Expediente cerrado"].configurar(
            "si" if r.cerrado else "no",
            comp.INSIGNIA_OK if r.cerrado else comp.INSIGNIA_ERROR)

        for item in self.tree_criterios.get_children():
            self.tree_criterios.delete(item)
        for c in cli.criterios_bloqueantes(informe):
            puntos = ", ".join(c.puntos) if c.puntos else "proyecto (Fase 9)"
            # Lo diferido por alcance se dice en la fila (EXT-G-02): el
            # criterio sigue pendiente y NO bloquea el cierre de esta corrida.
            fases = ", ".join(c.fases) + (
                " (diferido por alcance)" if c.diferido else "")
            self.tree_criterios.insert("", "end", values=(
                c.clave, c.etiqueta, c.concepto, c.fuente, fases, puntos,
                c.responsable, c.evidencia))

    # ------------------------------------------------------------------
    # Exportacion
    # ------------------------------------------------------------------
    def _plantilla(self):
        """
        La plantilla de la memoria, por la MISMA via que `cli.main`.

        Se lee del alcance del INFORME y no del selector: entre ejecutar y
        exportar el usuario puede haber movido el radio, y la memoria tiene
        que describir la corrida que se hizo, no la que se hara. Sin informe
        --- los botones estan deshabilitados, pero el metodo es publico ---
        manda el selector.
        """
        alcance = (self.informe.alcance if self.informe is not None
                   else self.alcance_var.get())
        return cli.plantilla_por_alcance(alcance)

    def exportar_json(self):
        if self.informe is None:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar JSON del expediente", defaultextension=".json",
            filetypes=[("Archivo JSON", "*.json")],
            initialfile=self.informe.csv.with_suffix(".informe.json").name,
        )
        if not ruta:
            return
        try:
            # Escritura atomica (E04): nunca un JSON a medias en disco.
            ses.escribir_json_atomico(Path(ruta), cli.informe_json(self.informe))
            messagebox.showinfo("JSON exportado", f"Archivo: {ruta}")
        except (OSError, ErrorProyecto) as exc:
            messagebox.showerror("Error al exportar", f"{exc}")
        except Exception as exc:  # fallo de programa: se muestra con traza
            # Son CUATRO exportadores, no tres. Este quedaba con `except
            # OSError` a secas, y su cuerpo llama a `cli.informe_json` y a
            # `json.dumps(..., allow_nan=False)`: un ErrorProyecto al armar el
            # informe, o un ValueError de json por un NaN, escapaban del
            # manejador entero y el usuario no veia NADA -- ni mensaje ni
            # traza en la ventana.
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")

    def exportar_html(self):
        if self.informe is None:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar memoria de calculo (HTML)", defaultextension=".html",
            filetypes=[("Archivo HTML", "*.html")],
        )
        if not ruta:
            return
        try:
            cli.exportar_html(self.informe, Path(ruta),
                              proyecto=self.proyecto_de_la_corrida,
                              ruta_plantilla=self._plantilla())
            messagebox.showinfo("Memoria exportada", f"Archivo: {ruta}")
        except (OSError, ErrorProyecto) as exc:
            messagebox.showerror("Error al exportar", f"{exc}")
        except Exception as exc:  # fallo de programa: se muestra con traza
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")

    def exportar_pdf(self):
        """
        El PDF, FUERA DEL HILO DE TK (EXT-8, PC-11).

        Tres caminos, decididos ANTES de tocar nada:

        1. Sin weasyprint operativo, la via del navegador de siempre, en este
           proceso: escribir el HTML cuesta ~1 s y no congela nada.
        2. Con weasyprint y mas de `UMBRAL_PUNTOS_PDF` puntos, se PREGUNTA:
           el PDF directo de 200 puntos costaba seis minutos y 5.7 GB. Quien
           elige el navegador va por el camino 1 con weasyprint apagado a
           proposito (`forzar_navegador`).
        3. Con weasyprint, un SUBPROCESO (`gui/exportacion_pdf.ProcesoPdf`)
           corre `cli.py --sesion ... --pdf` con la sesion serializada de
           esta ventana; el boton se apaga diciendo por que, el progreso se
           lee de sus lineas de stdout desde un `after` periodico, «Cancelar
           PDF» lo termina y el estado terminal queda escrito en el rotulo.
           Nunca un hilo: el estado de modulo de los tres archivos de valores
           no es seguro entre hilos, y la RAM de weasyprint solo vuelve al
           sistema cuando el proceso muere.
        """
        if self.informe is None:
            return
        if self.proceso_pdf is not None and not self.proceso_pdf.estado.terminal:
            messagebox.showinfo("PDF en marcha",
                                "Ya hay una exportacion en marcha; espere a "
                                "que termine o cancelela.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar memoria de calculo (PDF)", defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
        )
        if not ruta:
            return
        try:
            if not M11.weasyprint_disponible():
                self._exportar_pdf_por_navegador(Path(ruta), forzar=False)
                return
            n_puntos = len(self.informe.puntos)
            if n_puntos > expdf.UMBRAL_PUNTOS_PDF and not self._preguntar_via_pdf(n_puntos):
                self._exportar_pdf_por_navegador(Path(ruta), forzar=True)
                return
            self._lanzar_pdf(Path(ruta))
        except (OSError, ErrorProyecto) as exc:
            messagebox.showerror("Error al exportar", f"{exc}")
        except Exception as exc:  # fallo de programa: se muestra con traza
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")

    def _preguntar_via_pdf(self, n_puntos):
        """True si el usuario quiere el PDF directo pese al tamaño."""
        return messagebox.askyesno(
            "Memoria grande",
            f"La corrida tiene {n_puntos} puntos, por encima de los "
            f"{expdf.UMBRAL_PUNTOS_PDF} a partir de los que el PDF directo "
            f"tarda minutos ({expdf.LIMITE_MEDIDO_PDF}).\n\n"
            "¿Escribir el PDF directo en un proceso aparte de todos modos?\n"
            "«No» escribe la memoria en HTML y la abre en el navegador para "
            "guardarla como PDF con Ctrl+P, que pagina lo mismo.")

    def _exportar_pdf_por_navegador(self, ruta, *, forzar):
        resultado = cli.exportar_pdf(self.informe, ruta,
                                     proyecto=self.proyecto_de_la_corrida,
                                     ruta_plantilla=self._plantilla(),
                                     forzar_navegador=forzar)
        self.lbl_estado_pdf.config(text=resultado.mensaje.splitlines()[0])
        messagebox.showinfo("Memoria exportada", resultado.mensaje)

    def _lanzar_pdf(self, ruta):
        # El proceso hijo repone la sesion de ESTA ventana: la misma que
        # «Guardar sesion» escribe, en un archivo de trabajo aparte.
        trabajo = Path(tempfile.mkdtemp(prefix="alcantarillas_pdf_"))
        sesion = expdf.sesion_de_la_corrida(
            self.informe, proyecto=self.proyecto_de_la_corrida,
            formato_version=FORMATO_SESION, app_version=APP_VERSION,
            id_sesion=self.sesion_id, **self.entradas_de_la_corrida)
        proceso = expdf.ProcesoPdf(sesion=sesion, destino=ruta,
                                   plantilla=self._plantilla(),
                                   directorio_trabajo=trabajo)
        proceso.iniciar()
        if proceso.estado.terminal:
            # No arranco: se dice y no se deja «en marcha» nada.
            proceso.limpiar()
            raise OSError(proceso.detalle)
        self.proceso_pdf = proceso
        self.btn_pdf.deshabilitar(MOTIVO_EXPORTANDO_PDF)
        self.btn_cancelar_pdf.habilitar()
        self.lbl_estado_pdf.config(text=f"PDF en marcha: {self.proceso_pdf.progreso}")
        self.root.after(CADENCIA_SONDEO_PDF_MS, self._sondear_pdf)

    def _sondear_pdf(self):
        """Un latido del `after`: lee el progreso del hijo y se reprograma."""
        proceso = self.proceso_pdf
        if proceso is None:
            return
        estado = proceso.sondear()
        if not estado.terminal:
            self.lbl_estado_pdf.config(text=f"PDF en marcha: {proceso.progreso}")
            self.root.after(CADENCIA_SONDEO_PDF_MS, self._sondear_pdf)
            return
        self._terminar_pdf(proceso)

    def _terminar_pdf(self, proceso):
        """El estado terminal, claro y visible: escrito, cancelado o fallido."""
        self.btn_cancelar_pdf.deshabilitar("no hay ninguna exportacion en marcha")
        if self.informe is not None:
            self.btn_pdf.habilitar()
        self.lbl_estado_pdf.config(text=f"{proceso.estado.value.capitalize()}: {proceso.detalle}")
        proceso.limpiar()
        if proceso.estado is expdf.EstadoPdf.TERMINADO:
            messagebox.showinfo("Memoria exportada", proceso.detalle)
        elif proceso.estado is expdf.EstadoPdf.FALLIDO:
            messagebox.showerror("Error al exportar", proceso.detalle)

    def _cancelar_pdf(self):
        if self.proceso_pdf is not None:
            self.proceso_pdf.cancelar()
            self.lbl_estado_pdf.config(text="Cancelando la exportacion del PDF...")

    def comparar_informe(self, ruta=None):
        """
        La corrida vigente contra otro `informe_json` del disco (E-B, E14).

        Compara el VOLCADO fotografiado al correr (`volcado_de_la_corrida`)
        con el archivo elegido, por `src.comparador.comparar`: nunca corre
        el pipeline ni vuelve a armar el informe con el estado vivo. Devuelve
        el resultado (para los apoyos de la suite) y lo muestra en una
        ventana de texto; `None` si no hubo comparacion.
        """
        if self.informe is None:
            return None
        if ruta is None:
            ruta = filedialog.askopenfilename(
                title="Elegir el informe_json con el que comparar",
                filetypes=[("Archivo JSON", "*.json"), ("Todos los archivos", "*.*")])
        if not ruta:
            return None
        try:
            otro = compa.cargar(Path(ruta))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("No se pudo leer el JSON", f"{exc}")
            return None
        resultado = compa.comparar(self.volcado_de_la_corrida, otro)
        self._mostrar_comparacion(resultado, ruta)
        return resultado

    def _mostrar_comparacion(self, resultado, ruta):
        ventana = tk.Toplevel(self.root, background=comp.SUPERFICIE)
        ventana.title("Comparacion de dos informe_json")
        ventana.geometry("900x500")
        ventana.transient(self.root)
        ventana.bind("<Escape>", lambda _evt: ventana.destroy())
        ttk.Label(ventana, text=f"Esta corrida (A) frente a {ruta} (B)",
                  style="Header.TLabel", wraplength=860, justify="left").pack(
                      anchor="w", padx=10, pady=(10, 4))
        texto = comp.texto_plano(ventana, wrap="word")
        texto.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        texto.insert("1.0", "\n".join(resultado.lineas()))
        texto.configure(state="disabled")

    def exportar_csv(self):
        if self.informe is None:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar cuadro resumen (CSV)", defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            initialfile=self.informe.csv.with_suffix(".resumen.csv").name,
        )
        if not ruta:
            return
        try:
            cli.exportar_csv(self.informe, Path(ruta))
            messagebox.showinfo("CSV exportado", f"Archivo: {ruta}")
        except (OSError, ErrorProyecto) as exc:
            messagebox.showerror("Error al exportar", f"{exc}")
        except Exception as exc:  # fallo de programa: se muestra con traza
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------
    # Sesion (JSON) - patron de legacy/Tc.py
    # ------------------------------------------------------------------
    def _datos_de_sesion(self):
        """
        La sesion de ESTA ventana, lista para `json.dump`. La escriben
        «Guardar sesion» y el subproceso del PDF (EXT-8): es UNA definicion,
        y por eso el PDF del hijo describe la misma obra que la ventana.

        SIS-A-18. `criterios` y `alcance` son lo que faltaba: sin ellos, una
        sesion guardada describia DONDE estaba el expediente y no QUE se
        habia decidido sobre el, que es la parte que cuesta rehacer.

        FORMATO 3 (EXT-10, E04): `id`, `datos_sitio`, `sitio` (los [S]
        declarados por sesion, con trazabilidad y fecha), `csv_sha1` de la
        ultima corrida y `corridas` con su `informe_json` embebido. La
        sesion es el unico lugar del «proyecto actual».
        """
        data = {
            "formato_version": FORMATO_SESION,
            "app_version": APP_VERSION,
            "id": self.sesion_id,
            "proyecto": self.proyecto_var.get(),
            "csv": self.csv_var.get(),
            "datos_externos": self.datos_externos_var.get(),
            "datos_sitio": self.datos_sitio_var.get(),
            "externos": {clave: var.get() for clave, var in self.externos_vars.items()},
            "alcance": self.alcance_var.get(),
            "criterios": dec.estado_de_sesion(),
            "sitio": dec.estado_de_sitio_de_sesion(),
            "csv_sha1": (self.corridas[-1]["csv_sha1"] if self.corridas else ""),
            "corridas": list(self.corridas),
        }
        return data

    def guardar_sesion(self):
        data = self._datos_de_sesion()
        ruta = filedialog.asksaveasfilename(
            title="Guardar sesion", defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json")],
            initialfile=f"sesion_{self.proyecto_var.get() or 'expediente'}.json",
        )
        if not ruta:
            return
        try:
            # Escritura temporal + `os.replace` (E04): una sesion nunca
            # queda a medias en disco, y la anterior sigue si algo falla.
            ses.escribir_json_atomico(Path(ruta), data)
            messagebox.showinfo("Exito", "Sesion guardada correctamente.")
        except OSError as exc:
            messagebox.showerror("Error al guardar", f"No se pudo escribir el archivo:\n{exc}")

    def cargar_sesion(self):
        ruta = filedialog.askopenfilename(
            title="Cargar sesion", filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            # `UnicodeDecodeError` va aqui por la MISMA razon que en
            # `ejecutar_pipeline`, y faltaba: un JSON de sesion guardado en
            # ANSI por un editor de Windows --- con las eñes del castellano ---
            # estrellaba la ventana con una traza en vez de decir que el
            # archivo no esta en UTF-8. Es subclase de ValueError, no de
            # OSError ni de JSONDecodeError, de modo que este brazo no lo veia.
            messagebox.showerror("Error al cargar", f"No se pudo leer la sesion:\n{exc}")
            return
        # EL ESQUEMA ENTERO, ANTES DE TOCAR UN SOLO CAMPO (PC-16). Un JSON
        # valido que no sea objeto --- `[1, 2]`, `"texto"`, `3` --- o una
        # sesion con `"externos": null` pasaban `json.load` y reventaban
        # mas abajo con un `AttributeError` fuera del manejador, a stderr y
        # con proyecto y CSV ya pisados. Es un archivo mal formado, no un
        # fallo del programa, y sale por el mismo sitio que los demas.
        errores = errores_de_sesion(data)
        if errores:
            messagebox.showerror(
                "Error al cargar",
                "El archivo es JSON valido pero no es una sesion que se "
                "pueda aplicar; no se toco nada:\n- " + "\n- ".join(errores))
            return
        # LA MIGRACION ES EXPLICITA (EXT-10, E04): una sesion v1 o v2 se
        # completa aqui, en una copia, y lo completado se dice al final. Una
        # version que no se puede migrar se rechaza sin tocar nada.
        try:
            data, avisos_migracion = ses.migrar_a_actual(data)
        except ValueError as exc:
            messagebox.showerror("Error al cargar",
                                 f"La sesion no se puede migrar; no se toco nada:\n{exc}")
            return
        errores = errores_de_sesion(data)
        if errores:
            messagebox.showerror(
                "Error al cargar",
                "La sesion no se puede aplicar tras migrarla; no se toco "
                "nada:\n- " + "\n- ".join(errores))
            return

        self.proyecto_var.set(data.get("proyecto", ""))
        self.csv_var.set(data.get("csv", ""))
        self.datos_externos_var.set(data.get("datos_externos", ""))
        self.datos_sitio_var.set(data.get("datos_sitio", ""))
        # Los externos que la sesion NO trae se reponen a vacio: la ventana
        # queda como la sesion dice, no como la sesion anterior la dejo.
        externos = data.get("externos", {})
        for clave, var in self.externos_vars.items():
            var.set(externos.get(clave, ""))
        # Un alcance que la sesion no traiga (o que traiga escrito mal) NO se
        # adopta en silencio: se queda el defecto de `cli.py`, que es el mismo
        # que la ventana muestra al abrirse.
        alcance = data.get("alcance", cli.ALCANCE_EXPEDIENTE)
        if alcance not in (cli.ALCANCE_PERFIL, cli.ALCANCE_EXPEDIENTE):
            alcance = cli.ALCANCE_EXPEDIENTE
        self.alcance_var.set(alcance)

        aviso = self._aplicar_bloques_de_sesion(data, origen=f"sesion {Path(ruta).name}")

        self.lbl_error_datos.config(text="")
        self._llenar_tabla_criterios()
        self.nb.select(self.tab_datos)
        if avisos_migracion:
            aviso = ("La sesion se migro al formato v"
                     f"{FORMATO_SESION}: " + "; ".join(avisos_migracion)
                     + ". Revise antes de ejecutar. " + aviso)
        if aviso:
            messagebox.showinfo("Sesion cargada", aviso)

    def nuevo_proyecto(self):
        """
        «Nuevo proyecto»: OTRA obra sobre el mismo despliegue (EXT-10,
        EXT-V-01). Se carga una sesion vacia --- identidad nueva, campos
        vacios, sin criterios ni datos de sitio declarados --- y se sustituye
        todo lo declarado, por el mismo camino que «Cargar sesion». Nunca se
        vacia datos_sitio.py ni criterios_adoptados.py: mientras la obra
        nueva no declare sus [S], gobiernan los del archivo y la memoria lo
        dice en «Origen» y en la advertencia de corredor.
        """
        if not messagebox.askyesno(
                "Nuevo proyecto",
                "Se abre un proyecto nuevo: se retiran los criterios y los "
                "datos de sitio declarados para esta sesion y se vacian los "
                "campos. Los archivos del repositorio no se tocan. ¿Continuar?"):
            return
        data = ses.sesion_vacia(APP_VERSION)
        self.proyecto_var.set(data["proyecto"])
        self.csv_var.set(data["csv"])
        self.datos_externos_var.set(data["datos_externos"])
        self.datos_sitio_var.set(data["datos_sitio"])
        for var in self.externos_vars.values():
            var.set("")
        self.alcance_var.set(data["alcance"])
        aviso = self._aplicar_bloques_de_sesion(data, origen="proyecto nuevo")
        self.lbl_error_datos.config(text="")
        self._llenar_tabla_criterios()
        self.nb.select(self.tab_datos)
        messagebox.showinfo("Nuevo proyecto",
                            f"Proyecto nuevo (sesion {self.sesion_id}). "
                            + (aviso or "No habia nada declarado que retirar."))

    def _aplicar_bloques_de_sesion(self, data, *, origen):
        """
        La mitad de «abrir una sesion» que SUSTITUYE estado: la identidad,
        las corridas embebidas, los criterios declarados
        (`_restaurar_criterios(sustituir=True)`) y los datos de sitio [S]
        declarados por sesion (`declaracion.restaurar_datos_de_sitio`, la
        misma guardia que `datos_sitio.py`). La comparten «Cargar sesion» y
        «Nuevo proyecto» para que abrir la obra B tras la A y abrir una obra
        vacia sean el mismo camino. Devuelve el aviso para el dialogo.
        """
        self.sesion_id = data.get("id") or ses.sesion_vacia(APP_VERSION)["id"]
        self.corridas = list(data.get("corridas") or [])
        self.sitio_de_la_sesion = dict(data.get("sitio") or {"valores": {}})
        aviso = self._restaurar_criterios(data.get("criterios"), sustituir=True)
        try:
            resultado = dec.restaurar_datos_de_sitio(
                self.sitio_de_la_sesion, sustituir=True, origen=origen)
        except (ValueError, KeyError) as exc:
            return f"{aviso} No se pudieron restaurar los datos de sitio: {exc}".strip()
        partes = [aviso] if aviso else []
        if resultado.restaurados:
            partes.append(
                "Datos de sitio [S] declarados SOLO para esta sesion: "
                f"{', '.join(resultado.restaurados)}. datos_sitio.py no se modifico.")
        if resultado.retirados:
            partes.append(
                "Se RETIRARON los datos de sitio de la sesion anterior que "
                f"esta no trae: {', '.join(resultado.retirados)}.")
        if resultado.hubo_rechazos:
            detalle = "; ".join(f"{clave}: {motivo}"
                                for clave, motivo in resultado.rechazados)
            partes.append(f"NO se restauraron los datos de sitio: {detalle}")
        return " ".join(partes)

    def importar_decisiones(self):
        """
        «Importar decisiones»: SUMA los criterios declarados de otra sesion a
        los de esta, sin vaciar nada (`restaurar_sesion(sustituir=False)`).
        Es la accion aditiva que «Cargar sesion» era hasta EXT-4, con su
        propio boton y su propio nombre, porque abrir e importar son dos
        cosas y una ventana no puede hacer la segunda cuando se le pide la
        primera. No toca el proyecto, el CSV ni los externos.
        """
        ruta = filedialog.askopenfilename(
            title="Importar decisiones de otra sesion",
            filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            messagebox.showerror("Error al importar", f"No se pudo leer la sesion:\n{exc}")
            return
        errores = errores_de_sesion(data)
        if errores:
            messagebox.showerror(
                "Error al importar",
                "El archivo no es una sesion que se pueda aplicar; no se "
                "toco nada:\n- " + "\n- ".join(errores))
            return
        aviso = self._restaurar_criterios(data.get("criterios"), sustituir=False)
        self._llenar_tabla_criterios()
        messagebox.showinfo("Decisiones importadas",
                            aviso or "La sesion no traia criterios declarados.")

    def _restaurar_criterios(self, bloque, *, sustituir):
        """
        Repone los criterios declarados que la sesion traiga (SIS-A-18).

        Todo pasa por `declaracion.restaurar_sesion`, que declara por
        `establecer_valor_dinamico` -- la misma guardia que el archivo -- y
        devuelve lo restaurado, lo rechazado Y lo retirado. Un JSON de sesion
        es un archivo que alguien pudo editar a mano: aceptar sus valores sin
        guardia convertiria el formato de sesion en la puerta de atras que
        este proyecto no tiene, y descartarlos en silencio esconderia justo el
        caso que importa -- el criterio que la sesion traia y que hoy la
        guardia rechaza.

        `sustituir=True` es abrir una sesion: lo declarado en el proceso se
        retira ANTES de volcar la nueva (EXT-A-02). `False` es importar. En
        los dos casos el informe de la ultima corrida deja de estar vigente.
        """
        # Con `sustituir` se vacia aunque la sesion no traiga bloque: abrir
        # una sesion sin criterios es abrir una obra sin decisiones.
        self._invalidar_informe(MOTIVO_INFORME_DESACTUALIZADO)
        if bloque is None:
            bloque = {} if sustituir else None
        if bloque is None:
            return ""
        try:
            resultado = dec.restaurar_sesion(bloque, sustituir=sustituir)
        except (ValueError, KeyError) as exc:
            return f"No se pudieron restaurar los criterios de la sesion: {exc}"
        partes = []
        if resultado.restaurados:
            partes.append(
                f"Criterios restaurados SOLO para esta corrida: "
                f"{', '.join(resultado.restaurados)}. "
                "criterios_adoptados.py no se modifico.")
        if resultado.retirados:
            partes.append(
                "Se RETIRARON las declaraciones de la sesion anterior que "
                f"esta no trae: {', '.join(resultado.retirados)}.")
        if resultado.hubo_rechazos:
            detalle = "; ".join(f"{clave}: {motivo}"
                                for clave, motivo in resultado.rechazados)
            partes.append(f"NO se restauraron: {detalle}")
        return " ".join(partes)


def main():
    # ANTES del primer Tk, o Windows la ignora (ver `gui/componentes.py`):
    # es lo que hace que el contenido se vea nitido con la pantalla escalada.
    comp.declarar_conciencia_de_dpi()
    root = tb.Window(themename="litera") if tb is not None else tk.Tk()
    ExpedienteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
