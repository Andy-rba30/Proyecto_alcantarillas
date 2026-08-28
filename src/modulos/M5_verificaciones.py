"""
M5_verificaciones.py
=====================
Fase 5 de la hoja de ruta: las nueve verificaciones de la tabla principal
(V1 a V9), cada una como funcion propia que devuelve un `Verificacion` (nunca
un bool desnudo), mas `verificar()`, el agregado que MD.py llama con la firma
que declara su Protocol `Verificador`.

    V1  Borde libre               y/D <= 0.75                    [N] 4.1.1.3.7 b)
                                  (RECOMENDACION aplicada como umbral duro)
    V2  Velocidad minima          V >= 0.25 m/s                   [N] 4.1.1.3.6
                                  (RECOMENDACION aplicada como umbral duro;
                                  se evalua con la rama n_max, la estimacion
                                  BAJA de velocidad -- ver `v2_velocidad_minima`)
    V3  Velocidad maxima          concreto: fila de la Tabla N 10 [N]
                                  TMC / HDPE: 'v_max_tmc' / 'v_max_hdpe',
                                  CERRADOS con valor 4.572 m/s     [C]
    V4  Carga a la entrada HW     HW <= cota subrasante - resguardo(CBR)  [N->]
    V5  Remanso aguas arriba      sin metodo declarado -> pendiente       [A]
    V6  Material solido de arrastre  seccion unica (cumple por construccion)
    V7  Flotacion del conducto    equilibrio LRFD de factores de carga
                                  (Fase 8, M8_estructural); pendiente en
                                  'factores_carga_aashto' o
                                  'peso_especifico_relleno_kn_m3'              [A]
    V8  Evento extremo (FEN)      sin TR mayor ni umbral -> pendiente      [A]
    V9  Disponibilidad de diametro  D <= tope de M2                        [C]

Por que son NUEVE funciones y la tabla de Fase 5 tiene ONCE filas
-----------------------------------------------------------------
La tabla de Fase 5 de la hoja de ruta lista once verificaciones -- V1, V2,
**V2b**, V3, V4, **V4b**, V5, V6, V7, V8, V9 -- y este modulo implementa
nueve. Las dos que faltan son V2b y V4b, y no faltan por lo mismo:

**V2b - sedimentacion / colmatacion. Diferida al expediente, con constancia.**
Lo que V2b exige no es un umbral que este software pueda evaluar, sino ACCESO
DE MANTENIMIENTO EN LOS PLANOS -- el entregable 7 de Sec. 11, que este script
no produce (no dibuja planos). La mitad [N] de esa fila -- la velocidad
minima que evita la sedimentacion -- SI esta implementada, y es V2 (0.25 m/s,
num. 4.1.1.3.6, cuyo motivo declarado en la norma es justamente la
sedimentacion). Queda una obligacion viva y de expediente que no desaparece:
prever el acceso de mantenimiento para limpieza en los planos de cada punto.
`verificaciones_no_evaluadas()` la declara, M11 la imprime pegada a la tabla de
verificaciones de cada punto -- que es donde el revisor cuenta las filas -- y
el JSON la lleva en 'verificaciones_no_evaluadas'.

**V4b - relacion HW/D. No implementada, y su tratamiento esta ABIERTO.** El
criterio existe ('HW_D_max', 1.5) y ningun modulo lo consume. NO se cablea
aqui, y no por descuido: de donde sale ese 1.5 y que etiqueta le corresponde
son objeto de una revision abierta del expediente, y cablear el chequeo antes
de cerrarla verificaria los puntos contra un umbral cuya procedencia el
proyecto todavia no puede defender. Mientras siga asi, esta fila no se evalua
y este parrafo es su constancia. Cuando esa revision cierre, V4b entra como
funcion propia y este texto se sustituye por ella.

AVISO para quien lea esto y quiera arreglarlo por su cuenta: hay dos
docstrings que hoy afirman lo CONTRARIO -- que M5 si ejecuta V4b --, en
`modulos.M4_control` y en `modelos.ControlEntrada`. Estan detectados y se
corrigen en el mismo paquete que el cableado, no antes: primero se cierra de
donde sale el umbral, despues se cablea y se corrigen las tres cosas juntas.
Corregir solo los docstrings dejaria el paquete a medias, que es exactamente
como llego este modulo a tener ocho descripciones desfasadas.

Se dice con los dos numeros -- once filas, nueve funciones -- porque la
diferencia importa: contarla mal (decir "una fila mas") tapa justamente la
que sigue abierta.
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
('peso_especifico_relleno_kn_m3') y los factores gamma
('factores_carga_aashto', el mismo criterio del que come M9). Ver el docstring
de `v7_flotacion` mas abajo.

Consecuencia practica: mientras 'remanso_derecho_via', 'TR_evento_extremo' y
los dos criterios de V7 sigan vacios, `verificar()` (y por lo tanto
`MD.disenar_punto` / `MD.disenar_lote`) se detiene con
`CriterioPendienteError` para CUALQUIER punto. No es un defecto de este
modulo: es la misma regla que ya aplica a 'TW_receptor' o 'v_max_tmc' -- un
vacio real bloquea el calculo, no lo esconde. Las nueve funciones
individuales (v1_borde_libre, ..., v9_disponibilidad_diametro) SI son
utilizables una por una hoy mismo; es el AGREGADO el que hereda el bloqueo de
las pendientes.

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
from constantes_normativas import (RESGUARDO_NAPA_SUBRASANTE, V_MIN,
                                   Y_SOBRE_D_MAX)
from modelos import (DatoFaltanteError, DatoInvalidoError, Material, PuntoCritico,
                     ReferenciaNormativa, ResultadoHidraulico, TipoMaterial,
                     Verificacion)
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
NUMERAL_V5 = "Fase 5, V5 (DG-2018 + Ley 29338)"
NUMERAL_V6 = "3.1"
NUMERAL_V7 = ("Fase 5, V7 (subpresion: Manual de Puentes num. 2.4.3.8.2; "
              "equilibrio de factores de carga: AASHTO LRFD Tablas 3.4.1-1 y "
              "3.4.1-2, via el criterio 'factores_carga_aashto'; "
              "procedimiento: Fase 8, item 3)")
NUMERAL_V8 = "Fase 5, V8"
NUMERAL_V9 = "Sec. 3.2 (V9, nuevo en v7)"

CRITERIO_RESGUARDO = "resguardo_HW_subrasante"
CRITERIO_REMANSO = "remanso_derecho_via"
CRITERIO_EVENTO_EXTREMO = "TR_evento_extremo"
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
# Las DOS filas de Fase 5 que este modulo no evalua: V2b y V4b
# ---------------------------------------------------------------------------

def verificaciones_no_evaluadas() -> Tuple[str, ...]:
    """
    Las dos filas de la tabla de Fase 5 que este modulo NO implementa como
    verificacion -- V2b y V4b -- y por que cada una.

    Misma forma y mismo proposito que
    `M8_estructural.verificacion_diferida_estructural`: lo que queda fuera del
    alcance del script no se calcula ni se aproxima, se declara con su
    fundamento para que la memoria lo imprima. Un requisito que desaparece sin
    dejar rastro es lo que este proyecto persigue; que la tabla tenga ONCE
    filas y el modulo NUEVE funciones tiene que verse en la memoria, no
    deducirse contando.

    V2b: la mitad [N] -- la velocidad minima que evita la sedimentacion -- SI
    se verifica, y es V2 (0.25 m/s, num. 4.1.1.3.6, cuyo motivo declarado en
    el propio numeral es la sedimentacion). Lo que queda fuera es la mitad
    [A], el acceso de mantenimiento para limpieza, contenido de los PLANOS
    (Sec. 11, entregable 7) que este software no produce.

    V4b: no se evalua porque su umbral esta en revision abierta (ver el
    encabezado del modulo). El nombre de esta funcion era
    `verificacion_diferida_v2b` y se renombro al incorporarla: una funcion que
    devuelve dos constancias no puede llamarse por una sola de ellas.
    """
    return (
        "V2b (sedimentacion / colmatacion): la condicion de velocidad la "
        f"verifica V2 ({NUMERAL_V2}). El acceso de mantenimiento para "
        "limpieza queda DIFERIDO al expediente: es contenido de planos "
        "(Sec. 11, entregable 7), que este software no dibuja. Ningun "
        "punto se da por conforme en V2b por el hecho de cumplir V2",
        "V4b (relacion HW/D): NO evaluada. El criterio 'HW_D_max' esta "
        "declarado y ningun modulo lo consume; el origen del umbral y su "
        "etiqueta estan en revision abierta, y verificar contra un umbral "
        "cuya procedencia no se puede defender seria peor que no "
        "verificarlo. El control real del embalse aguas arriba es V5, que "
        "esta declarada y bloquea",
    )


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
    return Verificacion(
        cumple=y_sobre_D <= Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V1,
        valor_obtenido=y_sobre_D,
        valor_admisible=Y_SOBRE_D_MAX,
        criterio_aplicado=None,          # [N] puro, sin criterio adoptado
        codigo="V1",
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
    return Verificacion(
        cumple=resultado.V_sedimentacion >= V_MIN - TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V2,
        valor_obtenido=resultado.V_sedimentacion,
        valor_admisible=V_MIN,
        criterio_aplicado=None,
        codigo="V2",
    )


# ---------------------------------------------------------------------------
# V3 - Velocidad maxima (Tabla N 10 / vacios PPI-FHWA)
# ---------------------------------------------------------------------------

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
        return Verificacion(
            cumple=resultado.V_erosion <= v_max + TOL_UMBRAL_NORMATIVO,
            numeral=NUMERAL_V3,
            valor_obtenido=resultado.V_erosion,
            valor_admisible=v_max,
            criterio_aplicado=clave,
            codigo="V3",
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

    return Verificacion(
        cumple=resultado.V_erosion <= v_max + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V3,
        valor_obtenido=resultado.V_erosion,
        valor_admisible=v_max,
        criterio_aplicado=clave,   # None = [N] puro de la Tabla N 10
        codigo="V3",
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
    return cota_entrada_supuesta(punto) + D + espesor_pared(material)


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


def v4_carga_entrada(*, punto: PuntoCritico,
                     resultado: ResultadoHidraulico) -> Verificacion:
    """
    HW <= cota de subrasante - resguardo(CBR), Sec. 5.1. El resguardo sale
    del criterio 'resguardo_HW_subrasante' [N->] (analogia declarada al nivel
    freatico, no un valor puntual: la tabla de CBR vive en
    `constantes_normativas.RESGUARDO_NAPA_SUBRASANTE`, [N] por numeral, y es
    la aplicacion de ESA tabla al HW lo que Sec. 5.1 etiqueta [N->]).

    `HW` es una carga en metros sobre el fondo de la entrada (Sec. 4.2/4.3);
    convertirla a cota exige la cota de esa entrada. Este modulo adopta
    `punto.cota_terreno` para eso -- ver "V4 -- el supuesto de la cota de
    entrada" en el docstring del modulo: es una interpretacion declarada, no
    un criterio con fuente propia, y debe citarse como tal en la memoria.
    """
    ca.valor(CRITERIO_RESGUARDO)      # registra el uso; "segun_CBR" no es numerico
    resguardo_m = resguardo_por_cbr(punto.cbr_subrasante)

    cota_entrada = cota_entrada_supuesta(punto)   # ver supuesto declarado arriba
    HW_cota = cota_entrada + resultado.HW
    admisible = punto.cota_subrasante - resguardo_m

    return Verificacion(
        cumple=HW_cota <= admisible + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V4,
        valor_obtenido=HW_cota,
        valor_admisible=admisible,
        criterio_aplicado=CRITERIO_RESGUARDO,   # su etiqueta en ca.criterio() es "N->"
        codigo="V4",
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
    3.4.1-2 -- y se mayora la subpresion, que desestabiliza (WA, Tabla
    3.4.1-1). Con los minimos de la tabla es la forma 0.90*(DC + EV) >= 1.00*U.

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
    el relleno que de verdad hay encima, no un piso admisible. Usa la misma
    `cota_clave` que el tamizado de 7.A, que a su vez usa la misma cota de
    entrada que V4 (`cota_entrada_supuesta`, la regla declarada en
    'origen_cota_fondo_entrada'), para no evaluar la flotacion contra una
    referencia distinta de la que fija la rasante. Esa clave es la FISICA:
    lleva el espesor de pared, y por eso V7 se detiene tambien en
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
    'factores_carga_aashto' (los gamma), los dos vacios que le faltan al
    procedimiento -- no en un vacio de METODO: ver el docstring del modulo.
    """
    clave = cota_clave(punto=punto, material=material, D=D)
    altura_relleno = punto.cota_subrasante - clave
    if altura_relleno <= TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            "cota_subrasante", valor=punto.cota_subrasante, id_punto=punto.id,
            motivo="la clave del conducto queda a nivel de la subrasante o "
                   "por encima: no hay relleno sobre la clave que pesar "
                   f"en V7 ({NUMERAL_V7})",
        )

    D_ext = diametro_exterior(material=material, D=D)
    U = empuje_flotacion_kn_m(D_exterior=D_ext)
    EV = peso_relleno_kn_m(D_exterior=D_ext, altura_relleno=altura_relleno)
    DC = 0.0                 # peso propio omitido, del lado conservador
    g = factores_carga_flotacion()   # CriterioPendienteError si EV no se detuvo antes

    estabilizante = g.gamma_DC * DC + g.gamma_EV * EV
    desestabilizante = g.gamma_WA * U

    return Verificacion(
        cumple=estabilizante >= desestabilizante - TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V7,
        valor_obtenido=estabilizante,
        valor_admisible=desestabilizante,
        criterio_aplicado=CRITERIO_FACTORES_CARGA,
        codigo="V7",
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
    resultante. Se detiene en el criterio 'TR_evento_extremo'.
    """
    ca.valor(CRITERIO_EVENTO_EXTREMO)   # CriterioPendienteError: sin TR ni umbral
    raise AssertionError("inalcanzable mientras 'TR_evento_extremo' este vacio")


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
    Las nueve verificaciones de la Fase 5, en el orden de la tabla. Coincide
    con la firma de `modulos.MD.Verificador`: MD la importa como
    `modulos.M5_verificaciones.verificar` cuando no se le inyecta otra.

    Se detiene -- sin devolver nada -- en la primera de V3 (TMC/HDPE), V5, V7
    o V8 que este pendiente: son excepciones, no verificaciones incumplidas,
    y el bucle de MD no debe tratarlas como un diametro rechazado sino como
    lo que son, un calculo que no puede completarse todavia.
    """
    return (
        v1_borde_libre(D=D, resultado=resultado),
        v2_velocidad_minima(resultado=resultado),
        v3_velocidad_maxima(material=material, resultado=resultado),
        v4_carga_entrada(punto=punto, resultado=resultado),
        v5_remanso(punto=punto, resultado=resultado),
        v6_material_solido_arrastre(),
        v7_flotacion(punto=punto, material=material, D=D, resultado=resultado),
        v8_evento_extremo(punto=punto, resultado=resultado),
        v9_disponibilidad_diametro(D=D, material=material),
    )
