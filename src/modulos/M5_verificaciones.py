"""
M5_verificaciones.py
=====================
Fase 5 de la hoja de ruta: las ONCE verificaciones de la tabla principal
(V1 a V9), cada una como funcion propia que devuelve un `Verificacion` (nunca
un bool desnudo), mas `verificar()`, el agregado que MD.py llama con la firma
que declara su Protocol `Verificador`.

    V1  Borde libre               y/D <= 0.75                    [N] 4.1.1.3.7 b)
                                  (RECOMENDACION aplicada como umbral duro)
    V2  Velocidad minima          V >= 0.25 m/s                   [N] 4.1.1.3.6
                                  (RECOMENDACION aplicada como umbral duro;
                                  se evalua con la rama n_max, la estimacion
                                  BAJA de velocidad -- ver `v2_velocidad_minima`)
    V2b Sedimentacion/colmatacion S_conducto >= S_cauce   [C] HDS-5 num. 5.3.3
                                  + acceso de mantenimiento    [A]
                                  (INDICADOR aplicado como umbral duro; el
                                  segundo indicador del numeral queda
                                  declarado pendiente -- ver
                                  `v2b_sedimentacion`)
    V3  Velocidad maxima          concreto: fila de la Tabla N 10 [N]
                                  TMC / HDPE: 'v_max_tmc' / 'v_max_hdpe',
                                  CERRADOS con valor 4.572 m/s     [C]
    V4  Carga a la entrada HW     cota entrada + HW <= cota subrasante
                                  - resguardo(CBR)                       [N->]
    V5  Remanso aguas arriba      sin metodo declarado -> pendiente       [A]
    V6  Material solido de arrastre  seccion unica (cumple por construccion)
    V7  Flotacion del conducto    equilibrio LRFD de factores de carga
                                  (Fase 8, M8_estructural); pendiente en
                                  'factores_carga_aashto' o
                                  'peso_especifico_relleno_kn_m3'              [A]
    V8  Evento extremo (FEN)      sin TR mayor ni umbral -> pendiente      [A]
    V9  Disponibilidad de diametro  D <= tope de M2                        [C]

Por que ya son ONCE funciones para las ONCE filas de la tabla de Fase 5
----------------------------------------------------------------------
La tabla de Fase 5 de la hoja de ruta lista once verificaciones -- V1, V2,
**V2b**, V3, V4, **V4b**, V5, V6, V7, V8, V9 -- y este modulo implementa las
ONCE. Las dos que faltaban se cablearon en sesiones distintas y por la misma
regla: cuando se pudo sostener el umbral con su fuente, no antes.

**V2b - sedimentacion / colmatacion. IMPLEMENTADA desde S20**
(`v2b_sedimentacion`, en `verificar()`). Hasta entonces no existia en ninguna
linea de codigo (SIS-A-13, MAT-O15) y en su lugar habia una CONSTANCIA de
diferimiento: un parrafo que la memoria imprimia y que nadie tenia que
responder. Lo que la desbloqueo fue encontrar la fuente que este repositorio
ya tenia y no habia leido: el **HDS-5 3.a ed., num. 5.3.3 «Sedimentation»,
pag. impresa 5.11**, que nombra los indicadores de colmatacion en terminos de
dos numeros que el calculo ya tiene -- la pendiente del barril frente a la
del cauce natural --. La fila es [N] + [A] en la hoja de ruta y esa
estructura se conserva entera: el indicador de pendiente es la mitad
evaluable y el ACCESO DE MANTENIMIENTO es la mitad [A], que entra por el
criterio 'acceso_mantenimiento_v2b' y **detiene la corrida mientras siga
vacio**. Ya no es un parrafo: es una pregunta que el expediente tiene que
contestar.

De los dos indicadores del numeral se evalua UNO. El segundo -- «roughness
greater than the channel» -- exige el n de Manning del CAUCE NATURAL, que no
es columna de Sec. 1.2; queda declarado en la `verificacion_pendiente` del
criterio y la memoria lo imprime en la propia fila. Ver el docstring de la
funcion.

**V4b - relacion HW/D. IMPLEMENTADA desde S14** (`v4b_relacion_hw_d`, en
`verificar()`). Se cableo cuando se pudo y no antes: el conflicto #1 de la
matriz de auditorias lo prohibia expresamente mientras la ETIQUETA del
criterio siguiera abierta, porque implementar el chequeo sin saber de donde
salia el 1.5 habria convertido una cita mal leida en un umbral que rechaza
diametros. Lo que estaba abierto se cerro contra el PDF (C06): el rango
1.0-1.5 no es un criterio que el HDS-5 fije, sino la practica que su
Sec. 2.2.5 d) "Agency Constraints" DESCRIBE de las agencias viales
estadounidenses, y 1.5 es su extremo superior, el menos restrictivo. Por eso
el criterio dejo de ser [C] -- vacio cubierto por fuente tecnica -- y paso a
[A]: es una adopcion del proyectista sobre una banda de practica ajena, con
su rango de sensibilidad. Ver `criterios_adoptados.CRITERIOS['HW_D_max']`,
que lleva la cita y el texto literal.

Es un cambio de COMPORTAMIENTO -- un punto que hoy pasa puede dejar de
pasar -- y por eso se hizo aparte de la reetiquetacion y no en el mismo paso.
El HW que se divide entre D es el del control GOBERNANTE, no el del control
de entrada: lo que la fuente acota es el embalse que la obra produce. La
razon completa esta en el docstring de la funcion.

Los dos docstrings que afirmaban que M5 ya ejecutaba V4b -- en
`modulos.M4_control` y en `modelos.ControlEntrada` -- se habian corregido
junto con la reetiquetacion, cuando la afirmacion era falsa. Hoy vuelven a
poder decir que la verificacion existe, y lo dicen con la precision que
entonces faltaba: cual es el HW que compara.

Se dice con los dos numeros -- once filas, diez funciones -- porque la
diferencia importa: contarla mal (decir "las once") tapa justamente la que
sigue abierta.
Es la misma via documental que Fase 8 ya usa para el item 5 (rigidez de
anillo, pandeo y costura): se declara diferido con su motivo, no se calcula
un numero que nadie pidio.

Lo que NO se rellena en silencio
---------------------------------
V5 y V8 enuncian un REQUISITO en la hoja de ruta pero no entregan la formula,
el metodo o el dato con que evaluarlo (ver el detalle en cada funcion).
Rellenarlos con un supuesto no declarado es exactamente lo que CLAUDE.md
prohibe como "el peor error posible en este proyecto": cada uno se detiene
con `CriterioPendienteError` desde un criterio nuevo en
`criterios_adoptados.py` ('remanso_derecho_via', 'TR_evento_extremo'), con su
justificacion y lo que falta para resolverlo.

TW -- Sec. 1.3 ("TW se calcula, no se mide"), diferido y declarado
------------------------------------------------------------------
El TW que consume la Fase 4 entra por el criterio 'TW_receptor' (Tablero
3.1), NO por el procedimiento de tres pasos de Sec. 1.3 (Q del receptor de
ANA/Junta -> Manning en la seccion del receptor -> cota de agua). Ese
procedimiento no esta implementado en ningun modulo, y la consecuencia hay
que decirla porque no se adivina: **un CSV que traiga 'Q_receptor_m3s' y
'cota_TW' llenos sigue exigiendo el TW declarado** (`--tw` en la CLI o el
criterio), porque ningun modulo lee esas dos columnas -- viajan a la memoria
como datos del expediente y nada mas. Lo que falta no es una conversion sino
el paso 2 entero: la seccion transversal del receptor, que no es columna de
Sec. 1.2. Mientras tanto el bloqueo es ruidoso (`CriterioPendienteError`
sobre 'TW_receptor'), nunca un relleno silencioso.

V7 SI tiene formula y metodo -- Fase 8, item 3 de la hoja de ruta, y
`modulos.M8_estructural` la implementa completa ("tuberia vacia, NF en su cota
mas alta"). Ya NO como un factor de seguridad global ΣW >= FS*U, sino como el
equilibrio de factores de carga que corresponde al marco LRFD de Sec. 0.2:

    gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

Lo que sigue pendiente son dos DATOS puntuales del procedimiento, no el
procedimiento: el peso especifico del relleno
('peso_especifico_relleno_kn_m3') y la eleccion de fila de gamma_p
('factores_carga_aashto', el mismo criterio del que come M9; los gamma en si
son [N] y estan en constantes_normativas). Ver el docstring de `v7_flotacion`
mas abajo.

Consecuencia practica: mientras 'remanso_derecho_via', 'TR_evento_extremo',
'acceso_mantenimiento_v2b' y los dos criterios de V7 sigan vacios,
`verificar()` (y por lo tanto `MD.disenar_punto` / `MD.disenar_lote`) se
detiene con `CriterioPendienteError` para CUALQUIER punto. No es un defecto
de este modulo: es la misma regla que ya aplica a 'TW_receptor' o
'v_max_tmc' -- un vacio real bloquea el calculo, no lo esconde. Las once
funciones individuales (v1_borde_libre, ..., v9_disponibilidad_diametro) SI
son utilizables una por una hoy mismo; es el AGREGADO el que hereda el
bloqueo de las pendientes.

V4 -- la cota de entrada es un CRITERIO DECLARADO, no un supuesto del codigo
----------------------------------------------------------------------------
`modelos.ResultadoHidraulico` documenta que HW es una carga en metros SOBRE
EL FONDO DE LA ENTRADA, y que la conversion a cota (msnm) exige la cota de esa
entrada. `PuntoCritico` no trae una columna de cota de fondo de entrada (a
diferencia de `cota_fondo_receptor`, que si la trae para la salida).

V4 no puede existir sin esa cota. Este modulo NO la elige: la elige el
proyectista, en el criterio 'origen_cota_fondo_entrada'
(`criterios_adoptados.py`), y mientras nadie lo declare V4, V7 y el tamizado
7.A se detienen con `CriterioPendienteError` como cualquier otro vacio. La
regla admisible implementada hoy es 'cota_terreno' -- adoptar el terreno
natural del cruce, el unico campo de Sec. 1.1 que describe la elevacion del
cauce antes de la obra --, y su alcance, su direccion de conservadurismo y lo
que la sustituye estan escritos en la justificacion del criterio.

QUE CAMBIO Y POR QUE: hasta la correccion de SIS-A-01/SIS-A-04 este modulo
adoptaba `punto.cota_terreno` por su cuenta, con la eleccion explicada solo
aqui -- sin entrada en `criterios_adoptados.py`, sin fila en el Anexo A y sin
que la memoria marcara el numero como adoptado. Un docstring no es una
declaracion: no lo lee el revisor de la memoria, no entra en
`criterios_usados()` y no se puede cambiar sin tocar el codigo. La eleccion
gobierna V4, V7 y la rasante de 7.A/M7-M8, o sea el resultado de la obra, y
por eso vive donde vive el resto de lo que el proyectista decide.

La lectura vive en `cota_entrada_supuesta()`, publica, porque M7 (tamizado de
7.A) convierte el MISMO HW a cota para fijar la rasante minima: las dos
tienen que leer la misma referencia o el acoplamiento circular que 7.A dice
cortar sigue abierto. Lo mismo vale para `resguardo_por_cbr()`, que es la
segunda condicion del tamizado.

Excepciones
-----------
    CriterioPendienteError   V4, V7 y todo consumidor de
                             `cota_entrada_supuesta`
                             ('origen_cota_fondo_entrada'); V5
                             ('remanso_derecho_via'); V7
                             ('peso_especifico_relleno_kn_m3' o
                             'factores_carga_aashto'); V8
                             ('TR_evento_extremo'). V3 en TMC/HDPE ya NO:
                             'v_max_tmc' y 'v_max_hdpe' tienen valor.
    DatoInvalidoError        el 'material' de V3 no es de TipoMaterial (no
                             deberia llegar aqui: M2 ya lo valido antes); en
                             V7, la clave del conducto queda a nivel de la
                             subrasante o por encima (no hay relleno que
                             pesar); la regla declarada en
                             'origen_cota_fondo_entrada' no es una de las
                             implementadas.

Uso
---
    from modulos.M5_verificaciones import verificar

    verificaciones = verificar(punto=punto, material=material, D=D,
                               resultado=resultado_hidraulico)
"""

from __future__ import annotations

from typing import Tuple

import criterios_adoptados as ca
from constantes_normativas import (RESGUARDO_NAPA_SUBRASANTE,
                                   UMBRALES_POR_CODIGO, V_MIN,
                                   Y_SOBRE_D_MAX, caracter_del_umbral)
from modelos import (CIFRAS_FACTOR, CIFRAS_FINA, CIFRAS_MAGNITUD,
                     CIFRAS_PORCENTAJE,
                     DatoFaltanteError, DatoInvalidoError, EleccionDeProyecto,
                     ErrorProyecto,
                     Magnitud, Material,
                     PuntoCritico, ReferenciaNormativa, ResultadoHidraulico,
                     TipoMaterial, TipoDeVeredicto, Umbral, Veredicto,
                     Verificacion, paso)
from modulos.M2_material import (CRITERIO_D_MAX_CATALOGO, CRITERIO_V_MAX,
                                 diametro_exterior, espesor_pared)
from modulos.M8_estructural import (CRITERIO_FACTORES_CARGA,
                                    empuje_flotacion_kn_m,
                                    factores_carga_flotacion,
                                    peso_relleno_kn_m)
from tolerancias import TOL_UMBRAL_NORMATIVO

# Los TRES numerales de las verificaciones hidraulicas se escriben largos, y
# por el mismo motivo: son lo UNICO que la memoria imprime de cada
# verificacion (M11 los vuelca en la columna "numeral"), de modo que el
# sustento tiene que viajar aqui dentro o el revisor no lo ve. El titulo de la
# tabla, la pagina y el CARACTER de la frase vivian solo en el comentario de
# constantes_normativas y en docs/manifiesto_citas.md, que no van al
# expediente.
#
# V1 iba pelado -- "4.1.1.3.7 b)" -- y eso era un trato asimetrico sin
# fundamento (MAT-O13, NOR-HID-10): el 0.75 de V1 y el 0.25 de V2 salen del
# MISMO tipo de frase ("se recomienda") del mismo apartado 4.1.1.3, y solo V2
# llevaba el matiz. Un revisor que viera "recomienda, no prohibe" en V2 y un
# numeral desnudo en V1 leeria que el borde libre es exigencia y el piso de
# velocidad no, cuando la fuente los escribe igual.
NUMERAL_V1 = ('MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.7 b) "Borde libre", '
              'pag. impresa 79. El numeral RECOMIENDA este borde libre ("Se '
              'recomienda que el diseño hidraulico considere como minimo el '
              '25 % de la altura, diametro o flecha de la estructura"), no lo '
              'prohibe: aqui se aplica como umbral duro por decision '
              'conservadora del proyecto, igual que el piso de V2')
# V2 y V3 salen ademas del MISMO numeral -- 4.1.1.3.6 -- y de paginas
# contiguas: la Tabla Nº 10 esta en la 76 y el parrafo que la sigue termina en
# la 77. Lo que separa un piso de un techo no es el numero: es el titulo de la
# tabla y ese parrafo.
NUMERAL_V2 = ('MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.6, parrafo '
              'inmediatamente posterior a la Tabla Nº 10: arranca en la pag. '
              'impresa 76 y el valor se imprime en la 77. El numeral '
              'RECOMIENDA este minimo ("recomendandose que la velocidad '
              'minima sea igual a 0.25 m/s"), no lo prohibe: aqui se aplica '
              'como umbral duro por decision conservadora del proyecto. Se '
              'evalua con la velocidad de la rama de n MAXIMO -- la '
              'estimacion baja --, que es el extremo conservador para un piso')
NUMERAL_V3 = ('MC-HHD (RD 20-2011-MTC/14), Tabla Nº 10 "Velocidades maximas '
              'admisibles (m/s) en conductos revestidos", num. 4.1.1.3.6, '
              'pag. impresa 76; fuente de la tabla: HCANALES, Maximo Villon B. '
              'Los DOS numeros de cada fila son MAXIMOS -- lo dice el titulo --, '
              'de modo que se verifica solo el superior y el piso lo pone V2. '
              'Que el rango recorra la calidad del revestimiento es '
              'INTERPRETACION DEL PROYECTISTA y no del Manual: se declara '
              'aparte, en el bloque "Umbrales normativos y su caracter" de '
              'esta memoria. Se '
              'evalua con la velocidad de la rama de n MINIMO -- la estimacion '
              'alta --, que es el extremo conservador para un techo')
NUMERAL_V4 = ReferenciaNormativa(
    seccion_hoja_ruta="Sec. 5.1",
    numeral_norma="Manual de Suelos, Geologia, Geotecnia y Pavimentos (MTC), "
                  "num. 4.5.4 y 9.1(3)",
)
# V4b NO tiene numeral normativo, y el rotulo lo dice: el HDS-5 describe la
# banda de practica de las agencias de EE. UU., no la prescribe, y el MTC no
# fija HW/D alguno (NOR-HDS-02). Escribir aqui "HDS-5 num. 2.2.5 d)" a secas
# haria pasar por exigencia lo que la memoria tiene que presentar como
# adopcion del proyectista.
NUMERAL_V4B = ("Fase 5, V4b -- adopcion del proyectista ('HW_D_max' [A]). "
               "NO es exigencia: el HDS-5, num. 2.2.5 d) 'Agency "
               "Constraints', pag. impresa 2.10, DESCRIBE la banda 1.0-1.5 "
               "que imponen las agencias viales de EE. UU., y el MTC no fija "
               "HW/D alguno")

# V2b lleva numeral y pagina porque la mitad evaluable SI los tiene desde
# S20 -- el HDS-5 3.a ed. num. 5.3.3 --, y lleva ademas el matiz por la misma
# razon que V1 y V2: la fuente nombra un INDICADOR y el proyecto lo aplica
# como umbral duro. Un numeral pelado haria pasar por exigencia lo que la
# fuente escribe como sintoma.
NUMERAL_V2B = ('HDS-5 3.a ed. (FHWA-HIF-12-026), num. 5.3.3 "Sedimentation", '
               'pag. impresa 5.11. El numeral NO fija un umbral: nombra dos '
               'INDICADORES ("barrel slope less than the natural channel and '
               'roughness greater than the channel are key indicators of '
               'potential problems"). Aqui se evalua el PRIMERO como umbral '
               'duro, por decision conservadora del proyecto; el segundo '
               'exige el n de Manning del cauce natural, que no es columna de '
               'Sec. 1.2, y queda declarado pendiente. La otra mitad de la '
               'fila V2b de la hoja de ruta -- el acceso de mantenimiento en '
               'planos -- entra por el criterio '
               "'acceso_mantenimiento_v2b' [A]")
NUMERAL_V5 = "Fase 5, V5 (DG-2018 + Ley 29338)"
NUMERAL_V6 = "3.1"
NUMERAL_V7 = ("Fase 5, V7 (subpresion: Manual de Puentes num. 2.4.3.8.2; "
              "equilibrio de factores de carga: Manual de Puentes Tablas "
              "2.4.5.3.1-1 y 2.4.5.3.1-2, pag. impresa 143, con la fila de "
              "gamma_p elegida por estructura en 'factores_carga_aashto'; "
              "procedimiento: Fase 8, item 3)")
NUMERAL_V8 = "Fase 5, V8"
NUMERAL_V9 = "Sec. 3.2 (V9, nuevo en v7)"

CRITERIO_RESGUARDO = "resguardo_HW_subrasante"
CRITERIO_REMANSO = "remanso_derecho_via"
CRITERIO_EVENTO_EXTREMO = "TR_evento_extremo"
# La mitad [A] de la fila V2b: el acceso de mantenimiento en planos.
CRITERIO_ACCESO_MANTENIMIENTO = "acceso_mantenimiento_v2b"
# La regla con la que se obtiene la cota de fondo de entrada (V4, V7 y 7.A).
CRITERIO_ORIGEN_COTA_ENTRADA = "origen_cota_fondo_entrada"
# Reglas IMPLEMENTADAS: clave = valor que el proyectista declara en el
# criterio, valor = campo de `PuntoCritico` del que sale la cota. No hay
# aritmetica ninguna aqui -- cada regla es la lectura de una columna que el
# CSV ya trae -- y por eso la tabla no contiene ningun valor de proyecto:
# contiene el nombre de la columna que la declaracion elige.
ORIGENES_COTA_ENTRADA = {"cota_terreno": "cota_terreno"}
# Techo OPCIONAL del concreto. Se lee con `valor_si_declarado`, no con
# `valor`: sin declarar no bloquea nada y V3 usa el maximo [N] de la tabla.
CRITERIO_V_MAX_CONCRETO = "v_max_concreto_eleccion"


# ---------------------------------------------------------------------------
# Filas de Fase 5 que este modulo no evalua: desde S20, ninguna
# ---------------------------------------------------------------------------

CLAVE_HW_D_MAX = "HW_D_max"


def verificaciones_no_evaluadas() -> Tuple[str, ...]:
    """
    Las filas de la tabla de Fase 5 que este modulo NO implementa como
    verificacion. Desde S20 la tupla esta VACIA: las once se evaluan.

    Misma forma y mismo proposito que
    `M8_estructural.verificacion_diferida_estructural`: lo que queda fuera del
    alcance del script no se calcula ni se aproxima, se declara con su
    fundamento para que la memoria lo imprima. Un requisito que desaparece sin
    dejar rastro es lo que este proyecto persigue.

    POR QUE SIGUE EXISTIENDO UNA FUNCION QUE HOY DEVUELVE (). Porque su forma
    es la del CONJUNTO de filas diferidas, no la de la fila que en un momento
    dado lo este. Ya paso dos veces: contenia dos constancias (V2b y V4b),
    quedo con una al cablearse V4b en S14, y quedo con ninguna al cablearse
    V2b en S20. El dia que otra se difiera entra aqui sin tocar a ningun
    llamador, y mientras tanto M11 imprime la afirmacion positiva -- que
    ninguna queda sin evaluar --, que es informacion y no un hueco.

    QUE PASO CON LA CONSTANCIA DE V2b, para que nadie la busque. No se
    BORRO: se CONVIRTIO. Su mitad evaluable es hoy `v2b_sedimentacion`, con
    el numeral 5.3.3 del HDS-5 que la sostiene; su mitad de expediente -- el
    acceso de mantenimiento en planos -- es hoy el criterio
    'acceso_mantenimiento_v2b', que DETIENE la corrida mientras siga vacio en
    vez de imprimir un parrafo que nadie tiene que contestar. La obligacion
    no se relajo: se endurecio.

    El nombre era `verificacion_diferida_v2b` y se renombro al incorporar la
    de V4b: una funcion que devolvia dos constancias no podia llamarse por una
    sola de ellas. El nombre plural se conserva por lo mismo que la tupla.
    """
    return ()


# ---------------------------------------------------------------------------
# La traza de la memoria: como este modulo la emite
# ---------------------------------------------------------------------------
# Cada verificacion devuelve su `Verificacion` COMO SIEMPRE y ademas el
# `PasoDeMemoria` que la explica. No es informacion nueva: es la que la
# funcion ya tenia delante -- de donde salio cada numero, contra que se
# compara, con que margen -- y que hasta S18 se perdia al devolver solo el
# veredicto, obligando a M11 a reconstruirla desde los resultados (SIS-A-07).
#
# `_umbral_de` arma el `Umbral` desde `UMBRALES_DE_VERIFICACION`, que es donde
# viven el caracter de la fuente y lo que el proyecto hace con el. NO se
# escriben aqui: la memoria y el codigo tienen que citar el mismo objeto o
# divergen, que es literalmente NOR-MEM-01.

# codigo de verificacion -> id de la cita del registro que fija SU umbral. Es
# la cita que lleva el NUMERO, que no siempre es la primera del bloque: la de
# V2 es la segunda mitad del parrafo ("recomendandose que la velocidad minima
# sea igual a 0.25 m/s"), porque la primera obliga a verificar y no dice
# cuanto.
CITA_DEL_UMBRAL = {
    "V1": "MC_HHD.4.1.1.3.7b",
    "V2": "MC_HHD.4.1.1.3.6#VMIN",
    # V2b: la cita que lleva la COMPARACION, no la que da la contracara.
    "V2b": "HDS5_3ED.5.3.3#INDICADORES",
    "V3": "MC_HHD.4.1.1.3.6#T10",
    "V4": "MS.4.5.4",
    "V7": "MP.T2.4.5.3.1-2",
}


def _umbral_de(codigo: str, *, valor, unidad: str,
               descripcion: str, criterio: str = None) -> Umbral:
    """
    El `Umbral` de una verificacion, con su caracter y su aplicacion leidos de
    `UMBRALES_DE_VERIFICACION` y no reescritos aqui.
    """
    u = UMBRALES_POR_CODIGO[codigo]
    return Umbral(descripcion=descripcion, valor=valor, unidad=unidad,
                  cita_id=CITA_DEL_UMBRAL[codigo],
                  caracter=caracter_del_umbral(u),
                  aplicacion=u["aplicacion"],
                  criterio_aplicado=criterio)


def _veredicto(cumple: bool, margen: float, unidad: str,
               explicacion: str) -> Veredicto:
    return Veredicto(
        tipo=TipoDeVeredicto.CUMPLE if cumple else TipoDeVeredicto.NO_CUMPLE,
        margen=margen, unidad=unidad, explicacion=explicacion)


# ---------------------------------------------------------------------------
# V1 - Borde libre (Sec. 4.1.1.3.7 b)
# ---------------------------------------------------------------------------

def v1_borde_libre(*, D: float, resultado: ResultadoHidraulico) -> Verificacion:
    """
    y/D <= 0.75: minimo 25 % de borde libre sobre el tirante normal.

    Texto que lo sustenta, literal (MC-HHD, RD 20-2011-MTC/14,
    num. 4.1.1.3.7 b) "Borde libre", pag. impresa 79):

        "Se recomienda que el diseño hidráulico considere como mínimo el 25 %
        de la altura, diámetro o flecha de la estructura."

    ES UNA RECOMENDACION, IGUAL QUE EL PISO DE V2, y esta funcion la aplica
    igualmente como umbral duro (`y/D <= 0.75` decide `cumple`), que es la
    lectura conservadora y la que el proyecto adopta. El matiz viaja en
    `NUMERAL_V1`, que es lo unico que la memoria imprime de V1. Hasta esta
    correccion `NUMERAL_V1` era el numeral desnudo mientras `NUMERAL_V2` si
    llevaba el matiz: dos frases del mismo apartado presentadas con distinta
    fuerza normativa, sin nada en la fuente que lo justificara (MAT-O13,
    NOR-HID-10).

    El tirante que se compara es `y_normal`, resuelto con n_max (rama de
    capacidad): mas rugosidad da mas tirante para el mismo Q, o sea el extremo
    conservador para una verificacion de borde libre.
    """
    y_sobre_D = resultado.y_normal / D
    cumple = y_sobre_D <= Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO
    umbral = _umbral_de(
        "V1", valor=Y_SOBRE_D_MAX, unidad="",
        descripcion="y/D maximo admisible (borde libre >= 25 % de D)")
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V1,
        valor_obtenido=y_sobre_D,
        valor_admisible=Y_SOBRE_D_MAX,
        criterio_aplicado=None,          # [N] puro, sin criterio adoptado
        codigo="V1",
        paso=paso(
            "F5.V1",
            codigo="V1",
            que="Borde libre: relacion de llenado del conducto",
            formula="y/D <= 0.75, donde 0.75 = 1 - 0.25 (el 25 % que el "
                    "numeral escribe como borde libre minimo)",
            formula_cita_id="MC_HHD.4.1.1.3.7b",
            sustitucion=(
                Magnitud("y_normal", resultado.y_normal, "m",
                         "M3, tirante normal por Manning con la rama de n "
                         "MAXIMO (mas rugosidad da mas tirante para el mismo "
                         "Q: el extremo conservador para un borde libre)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("D", D, "m",
                         "diametro adoptado por el bucle de diseño (MD), de "
                         "la serie normalizada", cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("y/D", y_sobre_D, "",
                               "y_normal / D, calculado en esta verificacion",
                               cifras=CIFRAS_MAGNITUD),
            umbral=umbral,
            veredicto=_veredicto(
                cumple, Y_SOBRE_D_MAX - y_sobre_D, "",
                "margen de borde libre por encima del 25 % exigido"
                if cumple else
                "el conducto trabaja con menos borde libre del recomendado"),
            nota_del_proyecto=(
                "El numeral RECOMIENDA este borde libre; aqui se aplica como "
                "umbral duro por decision conservadora del proyecto. La "
                "fuente no escribe el 0.75 ni la razon y/D: escribe «el 25 % "
                "de la altura, diametro o flecha de la estructura»."),
        ),
    )


# ---------------------------------------------------------------------------
# V2 - Velocidad minima (Sec. 4.1.1.3.6)
# ---------------------------------------------------------------------------

def v2_velocidad_minima(*, resultado: ResultadoHidraulico) -> Verificacion:
    """
    V >= 0.25 m/s. Sec. 5.2 de la hoja de ruta ya advierte que este piso casi
    nunca gobierna (se necesitaria una pendiente ~0.00006 para violarlo); la
    verificacion se calcula igual, sin dar por hecho el resultado.

    Texto que lo sustenta, literal (MC-HHD, RD 20-2011-MTC/14, num. 4.1.1.3.6,
    pag. 76, parrafo inmediatamente posterior a la Tabla Nº 10):

        "Se deberá verificar que la velocidad mínima del flujo dentro del
        conducto no produzca sedimentación que pueda incidir en una reducción
        de su capacidad hidráulica, recomendándose que la velocidad mínima sea
        igual a 0.25 m/s."

    DOS COSAS QUE ESE TEXTO FIJA Y QUE HAY QUE LEER JUNTAS:

    (1) El 0.25 es una RECOMENDACION, no una prohibicion -- el numeral dice
        "recomendandose". Esta funcion lo aplica igualmente como umbral duro
        (`V >= V_MIN` decide `cumple`), que es la lectura conservadora y es la
        que el proyecto adopta. Pero el matiz no puede quedarse en el codigo:
        `NUMERAL_V2` lo lleva escrito, de modo que la memoria lo imprime junto
        al resultado y un revisor que vea un punto rechazado por V2 sepa que
        esta ante una recomendacion incumplida y no ante una infraccion. Y no
        viaja solo por ahi: `constantes_normativas.UMBRALES_DE_VERIFICACION`
        lo lleva al bloque que M11 imprime SIEMPRE, tambien cuando ningun
        punto llego a evaluarse (NOR-MEM-01).

    (2) La RAZON del minimo es la sedimentacion que reduce la capacidad
        hidraulica, no el desgaste. Es lo que separa a V2 de V3: el piso lo
        pone la sedimentacion y vale para todos los materiales por igual; el
        techo lo pone la abrasion del revestimiento y cambia con el material.
        Por eso los dos numeros de la Tabla Nº 10 son maximos y ninguno es
        este piso (ver `v3_velocidad_maxima`).

    QUE VELOCIDAD SE COMPARA, Y POR QUE NO ES LA MISMA QUE EN V3 (MAT-D1)
    ---------------------------------------------------------------------
    `resultado.V_sedimentacion`: la de la rama de n MAXIMO, que es la
    estimacion BAJA de velocidad. No `V_erosion`, que es la alta y la que
    consume V3.

    La regla de doble n (Sec. 4.1 de la hoja de ruta) asigna n minimo a
    "velocidad MAXIMA y socavacion". V2 no esta en esa lista, y no por olvido:
    un piso y un techo tienen extremos conservadores OPUESTOS. Contra un techo
    hay que suponer la velocidad mas alta que el rango de n admite; contra un
    piso, la mas baja. Verificar el piso con la estimacion alta es declarar
    "cumple" en el caso en que el conducto sedimenta.

    Hasta esta correccion V2 leia la rama n_min y el defecto era medible: con
    D = 0.90 m, y/D = 0.75 y S = 5e-5, la rama n_max da 0.228 m/s -- por
    debajo del piso -- y la n_min 0.297 m/s, de modo que el punto pasaba. La
    ventana permisiva completa es S entre 3.55e-5 y 6.01e-5, por debajo de
    cualquier pendiente constructiva, asi que ningun diseño real quedo
    afectado; lo que estaba invertido era el conservadurismo. El fixture CP-3
    ya modelaba el umbral de V2 con n = 0.013 (n_max): el repositorio se
    contradecia a si mismo.
    """
    cumple = resultado.V_sedimentacion >= V_MIN - TOL_UMBRAL_NORMATIVO
    umbral = _umbral_de("V2", valor=V_MIN, unidad="m/s",
                        descripcion="velocidad minima de autolimpieza")
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V2,
        valor_obtenido=resultado.V_sedimentacion,
        valor_admisible=V_MIN,
        criterio_aplicado=None,
        codigo="V2",
        paso=paso(
            "F5.V2",
            codigo="V2",
            que="Velocidad minima: comprobacion de autolimpieza",
            formula="V >= 0.25 m/s",
            formula_cita_id="MC_HHD.4.1.1.3.6#VMIN",
            # LAS DOS MITADES DEL PARRAFO, y en este orden: primero la que
            # obliga a verificar, despues la que recomienda el valor. Leida
            # sola, la segunda hace parecer opcional lo que el Manual manda.
            citas_textuales=("MC_HHD.4.1.1.3.6#VMIN_INICIO",),
            sustitucion=(
                Magnitud("V_sedimentacion", resultado.V_sedimentacion, "m/s",
                         "M3, velocidad de la rama de n MAXIMO -- la "
                         "estimacion BAJA de velocidad, que es el extremo "
                         "conservador contra un PISO. No es la de V3, que "
                         "verifica un techo y usa la rama opuesta (MAT-D1)",
                         cifras=CIFRAS_MAGNITUD),),
            resultado=Magnitud("V_sedimentacion", resultado.V_sedimentacion,
                               "m/s", "la misma velocidad, contrastada contra "
                               "el piso", cifras=CIFRAS_MAGNITUD),
            umbral=umbral,
            veredicto=_veredicto(
                cumple, resultado.V_sedimentacion - V_MIN, "m/s",
                "por encima del piso de autolimpieza" if cumple else
                "por debajo del piso: el conducto puede sedimentar y perder "
                "capacidad hidraulica"),
            nota_del_proyecto=(
                "La oracion del Manual dice dos cosas con fuerza distinta: "
                "«se debera verificar» (EXIGENCIA de comprobar) y "
                "«recomendandose que la velocidad minima sea igual a 0.25 "
                "m/s» (RECOMENDACION sobre el valor). El proyecto cumple la "
                "primera y aplica la segunda como umbral duro, por decision "
                "conservadora propia."),
        ),
    )


# ---------------------------------------------------------------------------
# V2b - Sedimentacion / colmatacion (HDS-5 3.a ed., num. 5.3.3)
# ---------------------------------------------------------------------------

def v2b_sedimentacion(*, punto: PuntoCritico,
                      resultado: ResultadoHidraulico) -> Verificacion:
    """
    S_conducto >= S_cauce, el indicador de sedimentacion del HDS-5, mas el
    acceso de mantenimiento declarado en 'acceso_mantenimiento_v2b'.

    POR QUE ESTA FILA EXISTE SI YA ESTA V2. Porque V2 pone un piso de
    VELOCIDAD en el caudal de DISEÑO, y la colmatacion de una alcantarilla en
    una llanura de riego no la produce la avenida: la producen los caudales
    bajos y frecuentes sobre un conducto tendido mas plano que el cauce que lo
    alimenta. Un punto puede cumplir V2 con holgura y colmatarse igual. El
    HDS-5 3.a ed. lo nombra con todas las letras (num. 5.3.3 «Sedimentation»,
    pag. impresa 5.11):

        "Therefore, barrel slope less than the natural channel and roughness
        greater than the channel are key indicators of potential problems at
        culvert sites."

    y da la contracara en la misma pagina:

        "Culverts which are located on and aligned with the natural channel
        generally do not have a sedimentation problem."

    DE LOS DOS INDICADORES SE EVALUA UNO, Y HAY QUE DECIR CUAL Y POR QUE. El
    primero -- pendiente del barril frente a la del cauce -- son dos numeros
    que este calculo ya tiene: `resultado.S` es la pendiente CON QUE CORRIO EL
    DISEÑO y `punto.S_cauce` la del cauce natural (Sec. 1.5). El segundo --
    rugosidad del barril frente a la del cauce -- exige el n de Manning del
    CAUCE NATURAL, que no es columna de Sec. 1.2 y que la hoja de ruta no
    fija: no se aproxima con el n del conducto ni con un valor de practica,
    se declara pendiente en `acceso_mantenimiento_v2b.verificacion_pendiente`
    y la memoria lo imprime en la propia fila. Media verificacion declarada es
    defendible; media verificacion callada no.

    ES UN INDICADOR APLICADO COMO UMBRAL DURO, igual que V1 y V2 aplican como
    umbral duro dos recomendaciones. La fuente escribe «are key indicators of
    potential problems», no «shall»: el matiz viaja en `NUMERAL_V2B` y en
    `UMBRALES_DE_VERIFICACION`, que es lo que M11 imprime siempre.

    POR QUE CASI NUNCA GOBIERNA EN ESTE CORREDOR, y se dice para que nadie lo
    lea como una verificacion decorativa: Sec. 7.B fija que la alcantarilla
    sigue la pendiente del cauce, de modo que `S_conducto = S_cauce` salvo que
    el punto declare `S_conducto` aparte. La fila existe para el punto que SI
    lo declara -- una entrada deprimida, un conducto tendido mas plano para
    ganar recubrimiento -- que es exactamente el caso que el HDS-5 describe
    como «built with an upstream depression» y del que dice «Sedimentation is
    the likely result».

    LA MITAD [A] DETIENE, y esa es la diferencia con lo que habia antes. Hasta
    S20 la obligacion de prever el acceso de limpieza viajaba como un texto en
    `verificaciones_no_evaluadas()`: un parrafo que la memoria imprimia y que
    nadie tenia que responder. Ahora es un criterio sin valor, de modo que la
    corrida se detiene con `CriterioPendienteError` hasta que el proyectista
    declare como se limpia cada punto (SIS-A-13, MAT-O15).
    """
    # `exigir` y no `punto.S_cauce`: sin la pendiente del cauce el indicador
    # no tiene contra que comparar, y el revisor tiene que AÑADIR el dato
    # (DatoFaltanteError, no Invalido). MD descarta el material con la causa
    # citada entera, no mata el punto.
    S_cauce = punto.exigir("S_cauce")
    acceso = ca.valor(CRITERIO_ACCESO_MANTENIMIENTO)   # CriterioPendienteError
    cumple = resultado.S >= S_cauce - TOL_UMBRAL_NORMATIVO
    umbral = _umbral_de(
        "V2b", valor=S_cauce, unidad="m/m",
        descripcion="pendiente del cauce natural: el conducto no se tiende "
                    "mas plano que ella",
        criterio=CRITERIO_ACCESO_MANTENIMIENTO)
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V2B,
        valor_obtenido=resultado.S,
        valor_admisible=S_cauce,
        criterio_aplicado=CRITERIO_ACCESO_MANTENIMIENTO,
        codigo="V2b",
        paso=paso(
            "F5.V2b",
            codigo="V2b",
            que="Sedimentacion / colmatacion: indicador de pendiente y "
                "acceso de mantenimiento",
            formula="S_conducto >= S_cauce",
            formula_cita_id="HDS5_3ED.5.3.3#INDICADORES",
            citas_textuales=("HDS5_3ED.5.3.3#INDICADORES",
                             "HDS5_3ED.5.3.3#ALINEADO"),
            sustitucion=(
                Magnitud("S_conducto", resultado.S, "m/m",
                         "pendiente CON QUE CORRIO EL DISEÑO (la del cauce, "
                         "salvo que el punto declare `S_conducto`)",
                         cifras=CIFRAS_FINA),
                Magnitud("S_cauce", S_cauce, "m/m",
                         "pendiente del CAUCE NATURAL, columna del CSV "
                         "(Sec. 1.5: no es la de la alcantarilla)",
                         cifras=CIFRAS_FINA)),
            resultado=Magnitud("S_conducto - S_cauce", resultado.S - S_cauce,
                               "m/m",
                               "diferencia de pendientes: negativa es el "
                               "indicador que el HDS-5 nombra",
                               cifras=CIFRAS_FINA),
            umbral=umbral,
            veredicto=_veredicto(
                cumple, resultado.S - S_cauce, "m/m",
                "el conducto no queda mas plano que el cauce que lo "
                "alimenta: el indicador de sedimentacion del num. 5.3.3 no "
                "se dispara" if cumple else
                "el conducto queda MAS PLANO que el cauce natural, que es el "
                "indicador de colmatacion del num. 5.3.3; el HDS-5 lo llama "
                "«built with an upstream depression» y dice que la "
                "sedimentacion es el resultado probable"),
            elecciones=(EleccionDeProyecto(
                que_se_adopto="dispositivo de acceso de mantenimiento para "
                              "limpieza del conducto",
                valor=str(acceso),
                entre=tuple(str(v) for v in
                            ca.criterio(CRITERIO_ACCESO_MANTENIMIENTO)
                              .sensibilidad),
                de_donde="el criterio 'acceso_mantenimiento_v2b' [A]: "
                         "ninguna norma de normas/ prescribe el dispositivo",
                por_que="la fila V2b de la hoja de ruta es [N] + [A], y esta "
                        "es la mitad [A]. El indicador de pendiente dice si "
                        "el punto TIENDE a colmatarse; el acceso dice si se "
                        "va a poder limpiar cuando lo haga. El diametro "
                        "minimo de 0.90 m garantiza que una persona quepa, "
                        "no que pueda entrar",
                clave_criterio=CRITERIO_ACCESO_MANTENIMIENTO),),
            nota_del_proyecto=(
                "SE EVALUA UNO DE LOS DOS INDICADORES DEL NUMERAL. El "
                "segundo -- «roughness greater than the channel» -- exige el "
                "n de Manning del cauce natural, que no es columna de "
                "Sec. 1.2 ni lo fija la hoja de ruta. No se aproxima: queda "
                "declarado como pendiente. Y el caracter de la fuente es "
                "INDICADOR («are key indicators of potential problems»), no "
                "exigencia: el proyecto lo endurece a umbral duro por "
                "decision propia, igual que hace con V1 y con V2."),
        ),
    )


# ---------------------------------------------------------------------------
# V3 - Velocidad maxima (Tabla N 10 / vacios PPI-FHWA)
# ---------------------------------------------------------------------------

def _paso_v3(*, resultado: ResultadoHidraulico, v_max: float,
             clave, cumple: bool, material: Material, de_tabla: bool):
    """
    El paso de memoria de V3, comun a sus dos ramas.

    LA ELECCION SE IMPRIME, que es la regla R1: el techo de un material de la
    Tabla Nº 10 sale de una FILA, y la fila tiene alternativas -- las otras
    filas de la tabla, y en el concreto ademas el segundo numero de la propia
    fila. Sin decir entre que se eligio, «6.0 m/s» y «6.0 m/s porque es el
    mayor de la fila Concreto, descartando 3.0» son la misma linea en la
    pagina y no son la misma decision.
    """
    elecciones = []
    if de_tabla:
        fila = ", ".join(f"{v}" for v in material.v_max_tabla10)
        elecciones.append(EleccionDeProyecto(
            que_se_adopto="techo de velocidad del revestimiento",
            valor=f"{v_max} m/s",
            entre=tuple(f"{v} m/s" for v in material.v_max_tabla10),
            de_donde=f"la fila «{material.nombre}» de la Tabla Nº 10 "
                     f"({fila} m/s)",
            por_que="los DOS numeros de la fila son MAXIMOS -- lo dice el "
                    "titulo de la tabla --, de modo que se verifica contra el "
                    "mayor y el menor NO es un piso. El piso de velocidad es "
                    "V2 y sale de otro parrafo",
            cita_id="MC_HHD.4.1.1.3.6#T10"))
        if clave is not None:
            elecciones.append(EleccionDeProyecto(
                que_se_adopto="techo mas conservador dentro de la fila",
                valor=f"{v_max} m/s",
                entre=tuple(f"{v} m/s" for v in material.v_max_tabla10),
                de_donde="el criterio adoptado 'v_max_concreto_eleccion'",
                por_que="el proyectista bajo el techo dentro de la fila del "
                        "concreto. Esa posibilidad se apoya en una "
                        "INTERPRETACION del proyectista -- que el par recorra "
                        "la calidad del acabado --, no en el Manual: se "
                        "declara aparte, en el bloque de umbrales",
                clave_criterio=clave))
    elif clave is not None:
        elecciones.append(EleccionDeProyecto(
            que_se_adopto="techo de velocidad",
            valor=f"{v_max} m/s",
            entre=(),
            de_donde=f"el criterio adoptado '{clave}' [C], con fuente WSDOT "
                     "Hydraulics Manual",
            por_que="la Tabla Nº 10 NO lista este material: no tiene fila. El "
                    "vacio esta verificado (afirmacion negativa del registro) "
                    "y se cubre con fuente tecnica reconocida, que es lo que "
                    "la etiqueta [C] declara",
            clave_criterio=clave))
    return paso(
        "F5.V3",
        codigo="V3",
        que="Velocidad maxima: comprobacion contra el techo del revestimiento",
        formula="V <= v_max del revestimiento",
        formula_cita_id="MC_HHD.4.1.1.3.6#T10",
        sustitucion=(
            Magnitud("V_erosion", resultado.V_erosion, "m/s",
                     "M3, velocidad de la rama de n MINIMO -- la estimacion "
                     "ALTA de velocidad, que es el extremo conservador contra "
                     "un TECHO. No es la de V2, que verifica un piso y usa la "
                     "rama opuesta", cifras=CIFRAS_MAGNITUD),),
        resultado=Magnitud("V_erosion", resultado.V_erosion, "m/s",
                           "la misma velocidad, contrastada contra el techo",
                           cifras=CIFRAS_MAGNITUD),
        umbral=_umbral_de("V3", valor=v_max, unidad="m/s",
                          descripcion=f"velocidad maxima admisible de "
                                      f"«{material.nombre}»",
                          criterio=clave),
        veredicto=_veredicto(
            cumple, v_max - resultado.V_erosion, "m/s",
            "por debajo del maximo admisible del revestimiento" if cumple else
            "por encima del maximo: el flujo abrasiona el revestimiento"),
        elecciones=tuple(elecciones),
    )


def v3_velocidad_maxima(*, material: Material,
                        resultado: ResultadoHidraulico) -> Verificacion:
    """
    V3 verifica UN SOLO extremo: el techo. V <= v_max.

    Materiales de la Tabla N 10 (concreto, ladrillo con concreto, mamposteria
    de piedra y concreto): M2 trae la fila literal en
    `material.v_max_tabla10`, y TODOS sus valores son velocidades MAXIMAS --
    la tabla se titula "Velocidades maximas admisibles (m/s) en conductos
    revestidos" (num. 4.1.1.3.6, pag. impresa 76), su unica columna de valores
    se rotula "VELOCIDAD (M/S)", y el piso esta aparte en el parrafo
    siguiente. El extremo inferior no es un minimo; exigirlo como tal era leer
    la tabla al reves.

    QUE DICE LA FUENTE Y QUE PONE EL PROYECTO (NOR-HID-04). Que los dos
    numeros sean maximos lo dice el titulo. Que el rango "recorra la calidad
    del revestimiento" -- el superior para el mejor acabado, el inferior para
    el mas pobre -- NO lo dice el Manual en ninguna parte: es interpretacion
    del proyectista, esta declarada como tal en
    `constantes_normativas.TABLA_10_INTERPRETACION_PROYECTO`, y es la que
    sostiene que 'v_max_concreto_eleccion' pueda bajar el techo dentro de la
    fila. Se dice aparte y no pegado a la cita porque en contra de esa lectura
    juegan dos hechos de la propia fuente: la frase que introduce la tabla
    habla de "un rango, cuyos limites se describen a continuacion", y la fila
    de mamposteria trae un solo valor.

    Ese error tenia consecuencia real: rechazaba por V3 un conducto de
    concreto a 1.5 m/s, que es una velocidad perfectamente admisible y que
    cumple de sobra el unico piso que la norma fija. Porque el piso existe y
    es otro: **V2**, autolimpieza, V >= 0.25 m/s, declarado aparte en la misma
    pagina y aplicable a todos los materiales por igual. Un segundo piso, mas
    alto y por material, no lo respalda ningun numeral.

    Se toma el valor MAYOR de la fila como admisible. Bajo la interpretacion
    del proyecto es el techo del revestimiento de mejor calidad; bajo lo que
    la fuente sostiene sin mas, es simplemente la mayor de las velocidades que
    la tabla admite para ese revestimiento, y verificar contra ella es la
    lectura minima que no inventa un piso.

    Techo mas conservador, OPCIONAL. Para el concreto, el proyectista puede
    declarar 'v_max_concreto_eleccion' y bajar ese techo -- hasta 3.0 m/s, el
    maximo del acabado mas pobre -- si las condiciones del acabado de ESTA
    obra lo ameritan. Se lee con `ca.valor_si_declarado`, NO con `ca.valor`:
    es un criterio opcional que refina un valor que la norma ya fija, no un
    vacio que la norma deje abierto. Sin declarar devuelve None, V3 aplica el
    6.0 de la tabla y el criterio no entra en la memoria. Leerlo con
    `ca.valor` bloquearia el concreto por un criterio que nadie tiene
    obligacion de declarar.

    `criterio_aplicado` distingue las dos procedencias, que es lo que un
    revisor necesita: None cuando el umbral es el [N] de la tabla, y la clave
    del criterio cuando el proyectista lo bajo.

    TMC y HDPE: la Tabla N 10 no los cubre (Tablero 1.3). El valor sale de
    `criterios_adoptados.valor('v_max_tmc' | 'v_max_hdpe')`, hoy 4.572 m/s los
    dos -- la conversion exacta de las 15 ft/s de la fuente, que antes se
    escribia redondeada a 4.6 y quedaba 0.6 % POR ENCIMA del techo declarado
    duro (MAT-O14) --, con cita de WSDOT Hydraulics Manual M 23-03.12, Cap. 8,
    Tabla 8-4 (el vacio que la hoja de ruta declaraba quedo cerrado; esa tabla
    NO esta en normas/ y la cita no es auditable contra el repositorio, lo que
    el propio criterio declara). Se leen con
    `ca.valor`, no con `ca.valor_si_declarado`: no son opcionales -- si
    alguien los vaciara, V3 debe detenerse y no caer a un techo inventado,
    porque para estos materiales no hay ningun valor normativo de respaldo
    al que volver. Son un techo escalar, de modo que esta rama no cambia.
    """
    if material.tipo in CRITERIO_V_MAX:
        clave = CRITERIO_V_MAX[material.tipo]
        v_max = ca.valor(clave)     # CriterioPendienteError mientras falte
        cumple = resultado.V_erosion <= v_max + TOL_UMBRAL_NORMATIVO
        return Verificacion(
            cumple=cumple,
            numeral=NUMERAL_V3,
            valor_obtenido=resultado.V_erosion,
            valor_admisible=v_max,
            criterio_aplicado=clave,
            codigo="V3",
            paso=_paso_v3(resultado=resultado, v_max=v_max, clave=clave,
                          cumple=cumple, material=material, de_tabla=False),
        )

    # Solo el techo: los valores de la fila de la Tabla N 10 son todos
    # MAXIMOS, no un piso y un techo (ver el docstring). Se toma el mayor; los
    # demas no se verifican. `max()` y no un desempaquetado de dos: la fila de
    # la mamposteria trae UN solo valor y escribirla como (2.0, 2.0) inventaba
    # un par que la fuente no imprime (NOR-HID-07).
    v_max = max(material.v_max_tabla10)
    clave = None

    if material.tipo is TipoMaterial.CONCRETO_REFORZADO:
        adoptado = ca.valor_si_declarado(CRITERIO_V_MAX_CONCRETO)
        if adoptado is not None:
            v_max = adoptado
            clave = CRITERIO_V_MAX_CONCRETO

    cumple = resultado.V_erosion <= v_max + TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V3,
        valor_obtenido=resultado.V_erosion,
        valor_admisible=v_max,
        criterio_aplicado=clave,   # None = [N] puro de la Tabla N 10
        codigo="V3",
        paso=_paso_v3(resultado=resultado, v_max=v_max, clave=clave,
                      cumple=cumple, material=material, de_tabla=True),
    )


# ---------------------------------------------------------------------------
# V4 - Carga a la entrada HW (Sec. 5.1, resguardo por analogia [N->])
# ---------------------------------------------------------------------------

def cota_entrada_supuesta(punto: PuntoCritico) -> float:
    """
    Cota del fondo de la entrada, msnm, segun la regla que el proyectista
    declaro en el criterio 'origen_cota_fondo_entrada' (Sec. 7.B; ver "V4 --
    la cota de entrada es un CRITERIO DECLARADO" en el docstring del modulo).

    Sin criterio declarado se detiene con `CriterioPendienteError`: la cota de
    fondo de entrada no es columna del CSV ni la fija ninguna norma, de modo
    que elegirla aqui seria rellenar un vacio en silencio.

    Es publica y con nombre propio porque V4 no es su unico consumidor: el
    tamizado de 7.A (M7) convierte el mismo HW a cota para fijar la rasante
    minima. Si cada modulo eligiera su propia cota de entrada, V4 y 7.A
    quedarian evaluando dos condiciones distintas y el acoplamiento circular
    que 7.A dice cortar seguiria abierto: la rasante se fijaria contra una
    referencia y se verificaria contra otra.
    """
    origen = ca.valor(CRITERIO_ORIGEN_COTA_ENTRADA)
    if origen not in ORIGENES_COTA_ENTRADA:
        raise DatoInvalidoError(
            CRITERIO_ORIGEN_COTA_ENTRADA, valor=origen,
            motivo="la regla declarada tiene que ser una de las "
                   f"implementadas: {sorted(ORIGENES_COTA_ENTRADA)}. Una cota "
                   "de fondo de entrada MEDIDA no se declara aqui: entra como "
                   "columna del CSV y sustituye al criterio entero",
        )
    return getattr(punto, ORIGENES_COTA_ENTRADA[origen])


def cota_clave(*, punto: PuntoCritico, material: Material, D: float) -> float:
    """
    Cota de la clave FISICA del conducto, msnm (Sec. 7.A):

        cota clave = cota de fondo de la entrada + D interior + espesor de pared

    El espesor de pared entra UNA vez y no dos: la cota de entrada es el
    invert INTERIOR -- la superficie por donde corre el agua -- de modo que la
    superficie exterior superior queda a D_int + t sobre ella, no a D_ext.

    POR QUE NO ES cota_entrada + D, que es lo que este proyecto calculaba
    (MAT-D4): EG-2013 Subseccion 508.07 (pag. impresa 984) mide el relleno
    minimo "desde la clave de la tuberia hasta el nivel de la subrasante", y
    la clave de la tuberia es su superficie EXTERIOR. Con la clave calculada
    sobre el diametro interior, la rasante minima de 7.A sale corta justo en
    t: una rasante fijada en ese minimo deja ~0.20 m reales de recubrimiento
    donde EG-2013 exige 0.30 (deficit del 33 % para D = 0.90 m de concreto).

    Es publica y vive AQUI, junto a `cota_entrada_supuesta`, por la misma
    razon que ella: la usan V7 (para pesar el relleno real sobre la clave) y
    el tamizado de 7.A (para fijar la rasante), y si cada modulo la
    recalculase por su cuenta las dos condiciones se separarian. Estaba
    duplicada -- M7.cota_clave y una linea suelta dentro de `v7_flotacion` --
    y las dos copias tenian el mismo error.

    Se detiene con `CriterioPendienteError` en 'origen_cota_fondo_entrada'
    (la cota de entrada) o en 'espesor_pared_conducto' (el espesor).
    """
    return cota_entrada_supuesta(punto) + D + espesor_pared(material, D)


def altura_relleno_sobre_clave(*, punto: PuntoCritico, material: Material,
                               D: float) -> float:
    """
    Altura REAL de relleno sobre la clave fisica del conducto, m:

        altura = cota de subrasante - cota de clave

    Es el relleno que de verdad hay encima -- no el minimo de Sec. 7.A, que es
    un piso admisible y otra cosa --, y lo consumen dos etapas distintas: V7,
    que lo pesa como EV para la flotacion, y la Fase 8, que con el entra a la
    tabla de clases o calibres de la norma de producto (items 1-2).

    LA GUARDA ES PARTE DE LA MAGNITUD, y por eso vive aqui y no en cada
    consumidor. Una altura nula o negativa significa que la clave queda a
    nivel de la subrasante o por encima: no es un relleno pequeño sino un
    punto cuyas cotas no se sostienen, y el numero que saldria de restarlas no
    tiene sentido fisico en ninguna de las dos etapas. Sale como
    `DatoInvalidoError` sobre 'cota_subrasante' -- el revisor tiene que
    CORREGIR una cota, no añadir un dato (CLAUDE.md) --, que es la excepcion
    que la Fase 5 ya lanzaba.

    POR QUE SE EXTRAJO (SIS-A-21). La resta estaba escrita dos veces: dentro
    de `v7_flotacion`, con la guarda, y en `cli._fase_8`, sin ella. La segunda
    copia no hacia daño HOY -- la Fase 8 se detiene antes, en el tope de
    'clases_producto_por_relleno' -- y esa es exactamente la forma en que una
    guarda desaparece sin que nadie lo note: el dia en que ese criterio se
    declare y la tabla se transcriba, la Fase 8 entraria a la norma de
    producto con una altura negativa y elegiria una clase contra un numero sin
    sentido. Escrita una vez, la guarda no se puede olvidar en una de las dos.

    Se detiene con `CriterioPendienteError` en lo mismo que `cota_clave`:
    'origen_cota_fondo_entrada' y 'espesor_pared_conducto'.
    """
    clave = cota_clave(punto=punto, material=material, D=D)
    altura = punto.cota_subrasante - clave
    if altura <= TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            "cota_subrasante", valor=punto.cota_subrasante, id_punto=punto.id,
            # El motivo NO cita numeral de fase: la misma magnitud la
            # consumen V7 (Fase 5) y la norma de producto (Fase 8), y una
            # excepcion que nombrase una sola mandaria al revisor a la etapa
            # equivocada la mitad de las veces. Quien la atrapa ya sabe en que
            # etapa esta -- `cli._etapa` la anota con su fase.
            motivo="la clave del conducto queda a nivel de la subrasante o "
                   f"por encima ({altura:+.3f} m de relleno): no hay relleno "
                   "sobre la clave que pesar ni con que entrar a la tabla de "
                   "la norma de producto",
        )
    return altura


def resguardo_por_cbr(cbr: float) -> float:
    """
    Resguardo de Sec. 5.1 segun el CBR de subrasante (Manual de Suelos, num.
    4.5.4): busca en `RESGUARDO_NAPA_SUBRASANTE` [N] la fila cuyo rango
    [CBR_min, CBR_max) contiene el dato, con los extremos None como
    ilimitados. Recorre las cuatro filas de la tabla, exhaustivas por
    construccion (cubren todo el dominio fisico del CBR).

    Publica por el mismo motivo que `cota_entrada_supuesta`: la segunda
    condicion del tamizado de 7.A (M7) es la misma tabla aplicada al mismo
    CBR, y duplicarla alli seria abrir la puerta a que las dos se separen.
    """
    for cbr_min, cbr_max, resguardo in RESGUARDO_NAPA_SUBRASANTE:
        piso = cbr_min is None or cbr >= cbr_min
        techo = cbr_max is None or cbr < cbr_max
        if piso and techo:
            return resguardo
    raise ValueError(
        f"CBR = {cbr} no cae en ninguna fila de RESGUARDO_NAPA_SUBRASANTE: "
        "la tabla deberia ser exhaustiva sobre el dominio fisico del dato"
    )


def _banda(inf, sup) -> str:
    """La fila de la tabla de resguardo, escrita como la lee un revisor."""
    if inf is None:
        return f"< {sup} %"
    if sup is None:
        return f">= {inf} %"
    return f"{inf}-{sup} %"


def v4_carga_entrada(*, punto: PuntoCritico,
                     resultado: ResultadoHidraulico) -> Verificacion:
    """
    cota de entrada + HW <= cota de subrasante - resguardo(CBR), Sec. 5.1.

    LOS DOS TERMINOS SON NIVELES, y por eso la desigualdad lleva el sumando
    `cota de entrada` que la hoja de ruta v8 omitia (MAT-O5): HW es una carga
    en metros sobre el fondo de la entrada, no una cota, y compararla con una
    cota msnm sin ese sumando se cumple siempre. El codigo nunca lo omitio
    -- ver `HW_cota` mas abajo --; era la hoja la que estaba mal, y se
    corrigio alli. El numeral tambien compara niveles: "El nivel superior de
    la sub rasante debe quedar encima del nivel de la napa freatica como
    minimo a 0.60 m ..." (Manual de Suelos, num. 4.5.4, pag. impresa 42).

    El resguardo sale
    del criterio 'resguardo_HW_subrasante' [N->] (analogia declarada al nivel
    freatico, no un valor puntual: la tabla de CBR vive en
    `constantes_normativas.RESGUARDO_NAPA_SUBRASANTE`, [N] por numeral, y es
    la aplicacion de ESA tabla al HW lo que Sec. 5.1 etiqueta [N->]).

    `HW` es una carga en metros sobre el fondo de la entrada (Sec. 4.2/4.3);
    convertirla a cota exige la cota de esa entrada. Este modulo NO la elige:
    la pide a `cota_entrada_supuesta`, que aplica la regla que el proyectista
    declaro en 'origen_cota_fondo_entrada' [A] -- ver "V4 -- la cota de
    entrada es un CRITERIO DECLARADO, no un supuesto del codigo" en el
    docstring del modulo. Este parrafo decia "este modulo adopta
    `punto.cota_terreno`", que es lo que hacia ANTES de SIS-A-01/SIS-A-04 y
    dejo de ser cierto entonces: 'cota_terreno' es hoy una de las reglas
    admisibles del criterio, no una eleccion del codigo.
    """
    ca.valor(CRITERIO_RESGUARDO)      # registra el uso; "segun_CBR" no es numerico
    resguardo_m = resguardo_por_cbr(punto.cbr_subrasante)

    cota_entrada = cota_entrada_supuesta(punto)   # ver supuesto declarado arriba
    HW_cota = cota_entrada + resultado.HW
    admisible = punto.cota_subrasante - resguardo_m

    cumple = HW_cota <= admisible + TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V4,
        valor_obtenido=HW_cota,
        valor_admisible=admisible,
        criterio_aplicado=CRITERIO_RESGUARDO,   # su etiqueta en ca.criterio() es "N->"
        codigo="V4",
        paso=paso(
            "F5.V4",
            codigo="V4",
            que="Carga a la entrada: el agua embalsada frente a la subrasante",
            formula="cota_entrada + HW <= cota_subrasante - resguardo(CBR)",
            formula_cita_id="MS.4.5.4",
            sustitucion=(
                Magnitud("cota_entrada", cota_entrada, "msnm",
                         "regla declarada en el criterio "
                         "'origen_cota_fondo_entrada' [A]; el codigo NO la "
                         "elige", cifras=CIFRAS_MAGNITUD),
                Magnitud("HW", resultado.HW, "m",
                         "M4, carga a la entrada del control que GOBIERNA "
                         "(entrada o salida, el mayor de los dos)", cifras=CIFRAS_MAGNITUD),
                Magnitud("cota_subrasante", punto.cota_subrasante, "msnm",
                         "columna cota_subrasante del CSV (Sec. 1.2)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("CBR", punto.cbr_subrasante, "%",
                         "columna cbr_subrasante del CSV (Sec. 1.2)",
                         cifras=CIFRAS_PORCENTAJE),
                Magnitud("resguardo", resguardo_m, "m",
                         "tabla del num. 4.5.4 del Manual de Suelos, entrando "
                         "con el CBR de la fila", cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("cota alcanzada por el agua", HW_cota, "msnm",
                               "cota_entrada + HW", cifras=CIFRAS_MAGNITUD),
            umbral=_umbral_de(
                "V4", valor=admisible, unidad="msnm",
                descripcion="cota maxima que el agua puede alcanzar "
                            "(subrasante menos resguardo)",
                criterio=CRITERIO_RESGUARDO),
            veredicto=_veredicto(
                cumple, admisible - HW_cota, "m",
                "el agua queda por debajo de la subrasante con su resguardo"
                if cumple else
                "el agua embalsada invade el resguardo bajo la subrasante"),
            elecciones=(EleccionDeProyecto(
                que_se_adopto="resguardo bajo la subrasante",
                valor=f"{resguardo_m} m",
                entre=tuple(f"{resguardo} m (CBR {_banda(inf, sup)})"
                            for inf, sup, resguardo in
                            RESGUARDO_NAPA_SUBRASANTE),
                de_donde="la tabla de resguardo por CBR del num. 4.5.4 del "
                         "Manual de Suelos",
                por_que=f"es la fila que corresponde al CBR "
                        f"{punto.cbr_subrasante} % de ESTE punto. La tabla es "
                        "normativa; extenderla del nivel freatico a la carga "
                        "de una avenida es la ANALOGIA que el criterio "
                        "'resguardo_HW_subrasante' declara como [N->]",
                cita_id="MS.4.5.4",
                clave_criterio=CRITERIO_RESGUARDO),),
        ),
    )


# ---------------------------------------------------------------------------
# V4b - Relacion HW/D (adopcion del proyectista sobre la banda del HDS-5)
# ---------------------------------------------------------------------------

def v4b_relacion_hw_d(*, D: float,
                      resultado: ResultadoHidraulico) -> Verificacion:
    """
    HW/D <= 'HW_D_max', Fase 5 fila V4b.

    CUAL HW SE DIVIDE ENTRE D, que es la unica decision de esta funcion y la
    que decide si el chequeo sirve. Se usa `resultado.HW` -- la carga del
    control que GOBIERNA --, no el HWi/D del control de entrada. Lo que la
    fuente acota es "the headwater produced by a culvert": el embalse real
    aguas arriba, que es el mayor de los dos controles. Tomar el de entrada
    cuando gobierna el de salida daria un numero menor que el embalse que la
    obra produce, y un umbral que se relaja solo cuando el agua sube mas es
    la direccion insegura exacta que este proyecto persigue.

    Es una consecuencia que hay que dejar escrita porque contradice una
    prediccion del propio repositorio: el docstring de
    `modelos.ControlEntrada.HW_sobre_D` decia que ese campo "sera el
    argumento del chequeo el dia que se cablee" (SIS-B-02). No lo es, por lo
    anterior, y ese docstring se corrigio en la misma pasada.

    DE DONDE SALE EL UMBRAL, y por que es [A] y no [N] ni [C]. El HDS-5 no
    prescribe HW/D alguno: su num. 2.2.5 d) "Agency Constraints" (pag.
    impresa 2.10) DESCRIBE lo que imponen las agencias viales
    estadounidenses -- "The allowable HW/D ratio varies throughout the
    country, but commonly ranges from 1.0 to 1.5" -- y en el Peru la agencia
    es el MTC, que no fija ninguno (NOR-HDS-02). Elegir un numero dentro de
    esa banda ajena es adopcion del proyectista, y por eso el criterio lleva
    su rango de sensibilidad y esta funcion lo declara en
    `criterio_aplicado`.

    POR QUE SE CABLEA AHORA Y NO ANTES. El conflicto #1 de la matriz de
    auditorias lo prohibia expresamente mientras la ETIQUETA del criterio
    estuviese abierta: implementar el chequeo antes de saber de donde sale el
    1.5 habria convertido una cita mal leida en un umbral que rechaza
    diametros. Cerrada la procedencia (C06), el cableado es lo que quedaba
    (MAT-D2, SIS-A-02, SIS-B-02).

    NO SUSTITUYE A V5. El control real del embalse aguas arriba es V5
    -- remanso dentro del derecho de via --, que es la que protege a
    terceros y que sigue deteniendose por falta de dato. V4b es un tope de
    practica, mas laxo, y cumplirlo no dice nada sobre V5.
    """
    HW_sobre_D = resultado.HW / D
    admisible = ca.valor(CLAVE_HW_D_MAX)
    return Verificacion(
        cumple=HW_sobre_D <= admisible + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V4B,
        valor_obtenido=HW_sobre_D,
        valor_admisible=admisible,
        criterio_aplicado=CLAVE_HW_D_MAX,
        codigo="V4b",
    )


# ---------------------------------------------------------------------------
# V5 - Remanso aguas arriba (DG-2018 + Ley 29338)
# ---------------------------------------------------------------------------

def v5_remanso(*, punto: PuntoCritico,
              resultado: ResultadoHidraulico) -> Verificacion:
    """
    Embalse dentro del derecho de via, sin afectar terceros ni la faja
    marginal. La hoja de ruta fija el REQUISITO pero no un metodo de perfil
    de remanso ni el ancho de derecho de via por punto (no es columna del
    CSV, Sec. 1.2): sin los dos, V5 no tiene con que comparar el HW de M4.

    Se detiene en el criterio 'remanso_derecho_via' -- vacio a proposito, ver
    su justificacion en criterios_adoptados.py -- en vez de aproximar con el
    ancho de plataforma (`punto.ancho_plataforma`), que es la seccion vial
    construida y NO el derecho de via legal: usarlo seria inventar un dato
    que el expediente no declaro.

    Los dos vacios se detienen por separado, y ninguno con un fallo de
    programa:

    - Criterio SIN valor -> `CriterioPendienteError` (la lanza `ca.valor`).
    - Criterio CON valor -> `DatoFaltanteError`. Declarar el criterio no
      cierra V5: sigue faltando el ancho de derecho de via del punto y el
      perfil de remanso con que comparar el HW de M4. El revisor tiene que
      ANADIR esos dos, y por eso es Faltante y no Invalido (CLAUDE.md).

    Antes esta segunda rama era un `raise AssertionError` desnudo: no
    descendia de `ErrorProyecto`, de modo que `cli._etapa` no lo capturaba y
    una corrida con el criterio declarado abortaba entera, con todos sus
    puntos, en vez de anotar el bloqueo y seguir.
    """
    ca.valor(CRITERIO_REMANSO)        # CriterioPendienteError: sin metodo ni dato
    raise DatoFaltanteError(
        "ancho_derecho_via_m",
        id_punto=punto.id,
        detalle=(
            f"el criterio '{CRITERIO_REMANSO}' esta declarado, pero V5 sigue "
            "sin poder resolverse: falta el ancho de derecho de via del punto "
            "(no es columna de Sec. 1.2) y el perfil de remanso aguas arriba "
            "con que comparar el HW de M4. La hoja de ruta fija el requisito "
            "y no el metodo: mientras no exista, V5 no se declara cumplida"
        ),
    )


# ---------------------------------------------------------------------------
# V6 - Material solido de arrastre (Sec. 3.1)
# ---------------------------------------------------------------------------

def v6_material_solido_arrastre() -> Verificacion:
    """
    Con palizada: seccion unica mayor, nunca multiple (Sec. 3.1). El
    catalogo de M2 (Sec. 3.2) y el bucle de MD solo ofrecen conductos
    circulares de UNA seccion -- el diseño multiceldular es Familia C
    (marco/multicelda, Sec. 2.3) y queda fuera del alcance de M2/MD. Por
    construccion del pipeline, esta verificacion nunca puede fallar hoy: si
    el proyecto alguna vez agrega diseño multibarril, esta funcion deja de
    ser trivial y hay que darle logica real.
    """
    return Verificacion(
        cumple=True,
        numeral=NUMERAL_V6,
        valor_obtenido="sección única (M2/MD no ofrecen diseño multibarril)",
        valor_admisible="sección única con palizada",
        criterio_aplicado=None,
        codigo="V6",
    )


# ---------------------------------------------------------------------------
# V7 - Flotacion del conducto (Manual de Puentes num. 2.4.3.8.2 + Fase 8.3)
# ---------------------------------------------------------------------------

def v7_flotacion(*, punto: PuntoCritico, material: Material, D: float,
                 resultado: ResultadoHidraulico) -> Verificacion:
    """
    Flotacion del conducto por EQUILIBRIO DE FACTORES DE CARGA LRFD, tuberia
    vacia y NF en su cota mas alta (Fase 5, fila V7):

        gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

    Se minoran las cargas que estabilizan -- peso propio del conducto (DC) y
    peso del relleno sobre la clave (EV), con sus gamma MINIMOS de la Tabla
    2.4.5.3.1-2 -- y se mayora la subpresion, que desestabiliza (WA, Tabla
    2.4.5.3.1-1). Para un conducto enterrado es la forma
    0.90*(DC + EV) >= 1.00*U.

    EL gamma DE EV DEPENDE DEL MATERIAL, y por eso esta funcion le pasa el
    suyo a `factores_carga_flotacion`. La Tabla 2.4.5.3.1-2 desglosa el
    empuje vertical de tierra por TIPO DE ESTRUCTURA: el tubo de concreto es
    "Estructura rigida enterrada", el HDPE una "Alcantarilla termoplastica" y
    el TMC una estructura flexible de la subfila "Entre otros". Los tres
    minimos valen 0.90 y el numero de V7 no cambia por esto; lo que cambia es
    que la fila de la que sale queda dicha, en vez de heredarse de un par
    unico que no era ninguna fila de la tabla (MAT-D8, NOR-PUE-03).

    NO es un FS global. La fila V7 de la hoja de ruta lo enuncia como
    ΣW >= FS*U, que es lenguaje de tension admisible; Sec. 0.2 adopta AASHTO
    LRFD de extremo a extremo, y verificar una demanda LRFD contra un FS
    clasico es la misma incoherencia carga-resistencia que esa seccion declara
    resuelta. El criterio 'FS_flotacion' que sostenia el umbral se retiro: en
    LRFD el margen lo hacen los propios gamma, y conservar ademas un FS seria
    contar dos veces el mismo margen. Ver "Por que V7 ya no usa un factor de
    seguridad global" en el docstring de `modulos.M8_estructural`.

    El procedimiento esta completo en `modulos.M8_estructural` (Fase 8, item
    3); esta funcion solo arma la altura de relleno del punto y ensambla el
    resultado.

    La altura de relleno sobre la clave es la REAL del punto -- cota de
    subrasante menos la cota de la clave -- no el minimo de Sec. 7.A: V7 pesa
    el relleno que de verdad hay encima, no un piso admisible. No la resta
    aqui: la pide a `altura_relleno_sobre_clave`, que es la misma que consume
    la Fase 8 y trae la guarda de cotas incoherentes con ella (SIS-A-21). Esa
    funcion usa la misma `cota_clave` que el tamizado de 7.A, que a su vez usa
    la misma cota de entrada que V4 (`cota_entrada_supuesta`, la regla
    declarada en 'origen_cota_fondo_entrada'), para no evaluar la flotacion
    contra una referencia distinta de la que fija la rasante. Esa clave es la
    FISICA: lleva el espesor de pared, y por eso V7 se detiene tambien en
    'espesor_pared_conducto' (MAT-D4).

    U y EV se calculan sobre el diametro EXTERIOR, no sobre el interior. El
    num. 2.4.3.8.2 define la subpresion sobre el volumen desplazado, que es el
    exterior; con t = 0.100 m en un tubo de concreto de D = 0.90 m
    (D_ext = 1.10 m) usar el interior la subestimaba un 33.1 %, y el docstring
    de M8 declaraba esa aproximacion "del lado conservador" cuando es
    exactamente la contraria (MAT-D3).

    DC = 0: no suma el peso propio del conducto (ver "Por que el peso propio
    del conducto no entra en V7" en el docstring de M8_estructural). Omitirlo
    es conservador, reduce el lado estabilizante en vez de inflarlo.

    Se detiene en 'peso_especifico_relleno_kn_m3' (el termino EV) o en
    'factores_carga_aashto' (la eleccion de fila de gamma_p), los dos vacios
    que le faltan al procedimiento -- no en un vacio de METODO: ver el
    docstring del modulo.
    """
    altura_relleno = altura_relleno_sobre_clave(punto=punto, material=material,
                                                D=D)

    D_ext = diametro_exterior(material=material, D=D)
    U = empuje_flotacion_kn_m(D_exterior=D_ext)
    EV = peso_relleno_kn_m(D_exterior=D_ext, altura_relleno=altura_relleno)
    DC = 0.0                 # peso propio omitido, del lado conservador
    g = factores_carga_flotacion(material=material)   # CriterioPendienteError si EV no se detuvo antes

    estabilizante = g.gamma_DC * DC + g.gamma_EV * EV
    desestabilizante = g.gamma_WA * U

    cumple = estabilizante >= desestabilizante - TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V7,
        valor_obtenido=estabilizante,
        valor_admisible=desestabilizante,
        criterio_aplicado=CRITERIO_FACTORES_CARGA,
        codigo="V7",
        paso=paso(
            "F5.V7",
            codigo="V7",
            que="Flotacion: equilibrio del conducto vacio bajo el freatico",
            formula="gamma_DC_min*DC + gamma_EV_min*EV >= gamma_WA*U",
            formula_cita_id="MP.T2.4.5.3.1-2",
            sustitucion=(
                Magnitud("D_ext", D_ext, "m",
                         "M2, diametro EXTERIOR = D + 2*espesor de pared. La "
                         "subpresion actua sobre el volumen desplazado, que "
                         "es el exterior, no el interior (MAT-D3)", cifras=CIFRAS_MAGNITUD),
                Magnitud("altura_relleno", altura_relleno, "m",
                         "cota de subrasante menos cota de clave FISICA del "
                         "punto: el relleno que de verdad hay encima, no el "
                         "minimo admisible de 7.A", cifras=CIFRAS_MAGNITUD),
                Magnitud("U", U, "kN/m",
                         "subpresion sobre el conducto vacio "
                         "(num. 2.4.3.8.2 del Manual de Puentes)", cifras=CIFRAS_MAGNITUD),
                Magnitud("EV", EV, "kN/m",
                         "peso del relleno sobre la clave", cifras=CIFRAS_MAGNITUD),
                Magnitud("DC", DC, "kN/m",
                         "peso propio del conducto, OMITIDO a proposito: "
                         "reduce el lado estabilizante y es del lado "
                         "conservador", cifras=CIFRAS_MAGNITUD),
                Magnitud("gamma_EV_min", g.gamma_EV, "",
                         "minimo de la fila de gamma_p que describe a este "
                         "material en la Tabla 2.4.5.3.1-2", cifras=CIFRAS_FACTOR),
                Magnitud("gamma_WA", g.gamma_WA, "",
                         "factor de la carga de agua, Tabla 2.4.5.3.1-1",
                         cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("accion estabilizante", estabilizante, "kN/m",
                               "gamma_DC*DC + gamma_EV*EV", cifras=CIFRAS_MAGNITUD),
            umbral=_umbral_de(
                "V7", valor=desestabilizante, unidad="kN/m",
                descripcion="accion desestabilizante mayorada (gamma_WA*U)",
                criterio=CRITERIO_FACTORES_CARGA),
            veredicto=_veredicto(
                cumple, estabilizante - desestabilizante, "kN/m",
                "el conducto vacio no flota" if cumple else
                "la subpresion supera lo que lo sujeta: el conducto flota"),
            elecciones=(EleccionDeProyecto(
                que_se_adopto="fila de gamma_p que describe a esta estructura",
                valor=f"gamma_EV min = {g.gamma_EV}",
                entre=("Estructura rigida enterrada",
                       "Alcantarillas termoplasticas",
                       "Estructuras flexibles, entre otros",
                       "Muros y estribos de retencion"),
                de_donde="la Tabla 2.4.5.3.1-2 del Manual de Puentes "
                         "(= 3.4.1-2 de AASHTO LRFD), pag. impresa 143",
                por_que=f"el conducto es de «{material.nombre}». LA TABLA ES "
                        "NORMATIVA; QUE FILA DESCRIBE A ESTA OBRA NO LO ES: "
                        "es la eleccion que el criterio "
                        "'factores_carga_aashto' declara. La fila de muros y "
                        "estribos -- que es la del cabezal de la Fase 9 -- "
                        "tiene otro minimo y no vale aqui",
                cita_id="MP.T2.4.5.3.1-2",
                clave_criterio=CRITERIO_FACTORES_CARGA),),
        ),
    )


# ---------------------------------------------------------------------------
# V8 - Evento extremo / FEN (Fase 5, V8)
# ---------------------------------------------------------------------------

def v8_evento_extremo(*, punto: PuntoCritico,
                      resultado: ResultadoHidraulico) -> Verificacion:
    """
    A un TR mayor que el de diseño, la via no colapsa aunque desborde. La
    hoja de ruta no fija ese TR mayor ni un umbral cuantitativo de colapso
    (p.ej. HW sobre la corona del terraplen): sin el TR no hay Q que correr
    aparte del de diseño, y sin el umbral no hay con que comparar el HW
    resultante.

    LOS DOS VACIOS SE DETIENEN POR SEPARADO, y ninguno con un fallo de
    programa -- misma forma que `v5_remanso`, y por la misma razon:

    - Criterio SIN valor -> `CriterioPendienteError` (la lanza `ca.valor`).
    - Criterio CON valor -> `DatoFaltanteError`. Declarar el TR del evento
      extremo NO cierra V8: sigue faltando el CAUDAL que a ese TR le
      corresponde. Este software no hace hidrologia -- el Q de diseño entra
      como columna del CSV, calculado aparte (Sec. 1.2, `legacy/Tc.py`) --,
      de modo que un TR de 500 años sin su Q es un numero sin nada que
      correr por M3/M4. El revisor tiene que AÑADIR ese caudal, y por eso es
      Faltante y no Invalido (CLAUDE.md).

    Hasta S20 esta segunda rama era un `raise AssertionError` desnudo, y
    estaba declarada como «mina deliberada» en `cli._verificador_perfil`. La
    mina avisaba de algo cierto -- la logica de V8 no esta escrita -- por el
    medio equivocado: `AssertionError` no desciende de `ErrorProyecto`, de
    modo que `cli._etapa` no lo capturaba y una corrida con el criterio
    declarado abortaba entera, con todos sus puntos, en vez de anotar el
    bloqueo y seguir. Es palabra por palabra el defecto que V5 ya habia
    tenido y que se corrigio antes; V8 se quedo con el.
    """
    ca.valor(CRITERIO_EVENTO_EXTREMO)   # CriterioPendienteError: sin TR ni umbral
    raise DatoFaltanteError(
        "Q_evento_extremo_m3s",
        id_punto=punto.id,
        detalle=(
            f"el criterio '{CRITERIO_EVENTO_EXTREMO}' esta declarado, pero V8 "
            "sigue sin poder resolverse: falta el CAUDAL correspondiente a "
            "ese periodo de retorno mayor. Este software no calcula "
            "hidrologia -- el Q de diseño entra como columna del CSV "
            "(Sec. 1.2) --, de modo que sin ese segundo caudal no hay nada "
            "que correr por M3/M4 ni HW que comparar contra la corona del "
            "terraplen. La hoja de ruta fija el requisito y no el metodo: "
            "mientras no exista, V8 no se declara cumplida"
        ),
    )


# ---------------------------------------------------------------------------
# V9 - Disponibilidad de diametro (Sec. 3.2, nuevo en v7)
# ---------------------------------------------------------------------------

def v9_disponibilidad_diametro(*, D: float, material: Material) -> Verificacion:
    """
    D requerido <= tope de CATALOGO del material. El tope es `material.D_max`,
    que M2 resuelve desde el criterio 'D_max_catalogo' -- V9 solo lo consulta,
    no lo recalcula.

    NO ES UN UMBRAL NORMATIVO (NOR-PRO-01, NOR-PRO-02, MAT-O8). El tope se
    atribuia a ASTM C76/AASHTO M170, AASHTO M36/ASTM A760 y AASHTO M294, y
    ninguna de las tres lo sostiene: A760 tabula diametros nominales hasta
    3600 mm y M 170M igual. Es una adopcion del proyecto sobre la
    disponibilidad de mercado, y por eso `criterio_aplicado` apunta ahora a
    'D_max_catalogo': un punto rechazado por V9 no lo rechaza la norma.
    """
    return Verificacion(
        cumple=D <= material.D_max + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V9,
        valor_obtenido=D,
        valor_admisible=material.D_max,
        criterio_aplicado=CRITERIO_D_MAX_CATALOGO,
        codigo="V9",
    )


# ---------------------------------------------------------------------------
# Agregado: la firma que llama MD.py
# ---------------------------------------------------------------------------

def verificar(*, punto: PuntoCritico, material: Material, D: float,
             resultado: ResultadoHidraulico) -> Tuple[Verificacion, ...]:
    """
    Las diez verificaciones de la Fase 5, en el orden de la tabla. Coincide
    con la firma de `modulos.MD.Verificador`: MD la importa como
    `modulos.M5_verificaciones.verificar` cuando no se le inyecta otra.

    Se detiene -- sin devolver nada -- en la primera de V3 (TMC/HDPE), V5, V7
    o V8 que este pendiente: son excepciones, no verificaciones incumplidas,
    y el bucle de MD no debe tratarlas como un diametro rechazado sino como
    lo que son, un calculo que no puede completarse todavia.

    PERO LO QUE YA SE VERIFICO NO SE TIRA. Al detenerse, la excepcion se lleva
    en `verificaciones_completadas` las que si se evaluaron, con su veredicto y
    con su `PasoDeMemoria`. En ESTE expediente eso no es un detalle: ninguna
    combinacion pasa de V5 --- `v5_remanso` se detiene siempre en
    `ancho_derecho_via_m` ---, de modo que sin esto el desarrollo de V1 a V4b,
    que si se calculo entero, no llegaba nunca a la memoria y el revisor solo
    veia «no dimensionado». Es la misma trampa de NOR-MEM-01: cierto sobre el
    codigo y falso sobre el producto. Escribirlo como una lista y no como una
    tupla literal es lo que permite conservarlas.
    """
    hechas: list = []
    piezas = (
        lambda: v1_borde_libre(D=D, resultado=resultado),
        lambda: v2_velocidad_minima(resultado=resultado),
        lambda: v2b_sedimentacion(punto=punto, resultado=resultado),
        lambda: v3_velocidad_maxima(material=material, resultado=resultado),
        lambda: v4_carga_entrada(punto=punto, resultado=resultado),
        lambda: v4b_relacion_hw_d(D=D, resultado=resultado),
        lambda: v5_remanso(punto=punto, resultado=resultado),
        lambda: v6_material_solido_arrastre(),
        lambda: v7_flotacion(punto=punto, material=material, D=D,
                             resultado=resultado),
        lambda: v8_evento_extremo(punto=punto, resultado=resultado),
        lambda: v9_disponibilidad_diametro(D=D, material=material),
    )
    for pieza in piezas:
        try:
            hechas.append(pieza())
        except ErrorProyecto as exc:
            exc.verificaciones_completadas = tuple(hechas)
            raise
    return tuple(hechas)
