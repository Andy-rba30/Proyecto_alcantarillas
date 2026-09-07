"""
M2_material.py
===============
Fase 3 de la hoja de ruta: catalogo de diametros normalizado (Sec. 3.2) y
matriz de decision de material (Sec. 3.4).

Lo que M2 NO hace
-----------------
M2 no selecciona el material del punto. Esa decision -- que combina
hidraulica (Fase 4), verificaciones de aceptacion (Fase 5) y el argumento de
defensibilidad de Sec. 3.4 -- no le corresponde a este modulo. M2 hace dos
cosas mas chicas y anteriores a esa decision:

    1. FILTRA CANDIDATOS: de los tres materiales de TipoMaterial, cuales
       tienen sentido para el punto antes de intentar dimensionarlos.
    2. PROVEE EL CATALOGO: para cada material candidato, junta en un
       `Material` los datos que la Fase 4 y la Fase 5 van a necesitar
       (n de Manning, tope de diametro, HDS-5, velocidad maxima, relleno
       minimo, seccion EG-2013), leidos de una sola fuente cada uno.

De donde sale cada dato del catalogo
-------------------------------------
constantes_normativas.py adelanta esta ADVERTENCIA DE DOBLE DEFINICION: tres
bloques del Anexo B tienen homologo en criterios_adoptados.py porque la hoja
de ruta los incluyo alli aun siendo [C], y la fuente unica para el CALCULO es
siempre el criterio adoptado:

    D_INICIO / D_PASO           -> criterio 'diametros_normalizados'
    HDS5_INLET (fila HDPE)      -> criterio 'hds5_embocadura_hdpe'

Este modulo respeta esa regla: la progresion de diametros sale siempre de
'diametros_normalizados'; la fila HDS-5 de concreto y de TMC sale de
HDS5_INLET (no tienen homologo -- son lectura directa de la Tabla A.1),
mientras que la fila de HDPE sale del criterio.

Dos datos del catalogo cambiaron de sitio y de naturaleza (cluster C01):

    D_max            ya NO sale de `constantes_normativas.D_MAX`, que se
                     retiro de alli: los topes no salen de las normas de
                     producto a las que se les atribuian (A760 tabula hasta
                     3600 mm, M 170M tambien -- NOR-PRO-01, NOR-PRO-02,
                     MAT-O8). Salen del criterio 'D_max_catalogo' [A], que
                     ademas trae en `de_catalogo` el rotulo con que hay que
                     imprimirlos. `Material.D_max_de_catalogo` lo transporta
                     para que la memoria no vuelva a llamarlos normativos.
    h_relleno_min    ya NO existe como campo. El recubrimiento minimo dejo de
                     ser un escalar por material: se CALCULA en
                     `M7_geometria.altura_recubrimiento` como el mayor entre
                     el minimo de EG-2013 -- que solo existe para HDPE, y que
                     el catalogo transporta en `h_relleno_min_eg2013` -- y la
                     cobertura minima de la Tabla 12.6.6.3-1 de AASHTO LRFD,
                     que depende del diametro EXTERIOR y de la condicion de
                     pavimento (NOR-VAC-01).

Y uno es nuevo:

    espesor_pared    m, el t que separa el diametro interior del exterior.
                     Sale del criterio 'espesor_pared_conducto' [A], hoy SIN
                     VALOR. Es lo que le faltaba al catalogo para que la clave
                     fisica y el volumen desplazado no se calculasen con el
                     diametro interior (MAT-D3, MAT-D4).

Campos que el catalogo puede dejar en None, a proposito
--------------------------------------------------------
Cuatro criterios alimentan campos que `Material` declara `Optional`:
'n_manning_hdpe', 'v_max_tmc', 'v_max_hdpe' y 'espesor_pared_conducto'.

ESTADO HOY: los tres primeros tienen valor y el cuarto no.
'v_max_tmc' = 'v_max_hdpe' = 4.572 m/s [C] (WSDOT, Tabla 8-4: 15 ft/s);
'n_manning_hdpe' = la fila del concreto de la Tabla N 09 [N->];
'espesor_pared_conducto' = SIN VALOR [A], y bloquea en su punto de uso
(`diametro_exterior` de este mismo modulo, que llaman
`M5_verificaciones.cota_clave` y `M8_estructural`/V7).

El cuarto criterio de esta lista era antes 'h_relleno_min_concreto_tmc', con
valor 0.30 m: se RETIRO al cerrarse NOR-VAC-01 -- el vacio que cubria no era
un vacio, la Tabla 12.6.6.3-1 de AASHTO LRFD lo tabula, y el numero adoptado
quedaba por debajo de su piso. Su hueco en la lista lo ocupa el espesor de
pared, que es un vacio de la misma familia (norma de producto) y esta vez sin
valor de verdad.

Este bloque decia ademas "Dos de los criterios ... siguen sin valor" y a
continuacion enumeraba tres, y otros siete docstrings del proyecto repetian
ese estado ya superado (SIS-A-03).

EL MECANISMO. La regla general del proyecto es que un criterio sin valor
DETIENE el calculo apenas se invoca (`criterios_adoptados.valor` lanza
CriterioPendienteError). Pero un catalogo que no se puede ni listar porque un
dato pendiente de extraer bloquea la construccion del objeto no es un
catalogo, es un candado. Por eso `catalogo()` lee esos cuatro con
`_valor_si_declarado()` -- que delega en `ca.valor_si_declarado`, no en
`ca.criterio(...)` como decia este texto -- y traslada el None al `Material`
tal cual. No es rellenar el vacio: es reportarlo con fidelidad, y el bloqueo
salta despues, en el punto de uso (`diametro_exterior` de este modulo para el
espesor de pared, M5:`v3_velocidad_maxima` para las velocidades), donde el
revisor puede saber que verificacion se detuvo.

LA EXCEPCION, escrita porque no la cubre el parrafo anterior:
'n_manning_hdpe' NO tiene punto de uso que lo detenga. Su None se
desempaqueta aqui mismo en `n_min, n_max` y saldria como `TypeError` -- un
fallo de programa -- en vez de como `CriterioPendienteError` del expediente.
No es alcanzable hoy (el criterio tiene valor, y una declaracion en caliente
a None se rechaza en `establecer_valor_dinamico`): solo lo seria vaciando el
archivo a mano. Queda dicho para quien lo vacie: antes de hacerlo, hay que
darle un punto de uso que bloquee, como tienen los otros tres.

Sec. 3.2 - Catalogo de diametros
---------------------------------
Progresion 0.90 m + pasos de 0.15 m, topada por material. El 0.90 sale del
num. 4.1.1.3.4 a) y NO es un piso incondicional: el numeral lo escribe "en
carreteras de alto volumen de transito" -- condicion que este proyecto no puede
afirmar, porque la clase de via depende del IMDA -- y exceptua expresamente los
cruces de canal de riego, que es la Familia C (ver "Familia C queda sin
candidatos", mas abajo, y `constantes_normativas.DIAMETRO_MIN_AMBITO`).
Aplicarlo igual a las Familias A y B es una adopcion declarada, y su direccion
NO es uniformemente conservadora: mas diametro da mas borde libre (favorable a
V1) y menos velocidad (desfavorable al piso de V2). Los dos numeros de la progresion viven en el criterio
'diametros_normalizados' [C]; los tres topes, en 'D_max_catalogo' [A]. Estan
separados porque no son la misma clase de dato: el paso se verifica contra la
serie de diametros nominales de las normas de producto y los topes NO salen de
ninguna norma -- son de catalogo, y como tales descartan material por
DISPONIBILIDAD, no por exigencia (NOR-PRO-01, NOR-PRO-02). Que no se usen
catalogos de proveedor para la PROGRESION es lo que preserva la neutralidad
comercial en obra publica; el tope, en cambio, es inevitablemente una decision
sobre lo que se consigue, y por eso va declarado como adopcion.

    NOTA DE CONSERVADURISMO (declarar en la memoria): 0.90 m redondo
    subestima el equivalente exacto de 36" (0.9144 m) en aproximadamente
    3 %. El error va del lado de la seguridad -- una seccion mas chica que
    la real exige mas resguardo del que hace falta -- y por eso se acepta
    sin ajustar la progresion a la pulgada.

`siguiente_diametro(material, D)` devuelve el siguiente diametro de la
progresion para ese material, o None cuando D ya esta en el ultimo escalon
posible (o lo supera): "material descartado por diametro requerido" es la
lectura que la Fase 4 le da a ese None, nunca un numero que no existe como
producto.

Sec. 3.4 - Matriz de decision de material
-------------------------------------------
Concreto reforzado es el unico material sin vacio normativo propio: su n
sale de la Tabla N 09 (MANNING['concreto_tubo_recto']) y su velocidad maxima
de la Tabla N 10 (V_MAX['concreto']), ambas [N] en constantes_normativas.py.
TMC tiene su propia subfila en la Tabla N 09
(MANNING['metal_corrugado_dren_aguas_lluvias'] -- ver `_MANNING_CLAVE`, que
declara por que esa y no la de sub-dren) pero no tiene fila en la Tabla N 10:
su velocidad maxima es el criterio 'v_max_tmc'. HDPE no esta en ninguna de las
dos tablas del Manual MTC: su n sale del criterio 'n_manning_hdpe' (la subfila
completa del concreto por analogia, [N->]) y su velocidad maxima del criterio
'v_max_hdpe'.

El marco de la Familia C -- ANTES "sin candidatos", y ya no
-------------------------------------------------------------
ESTE EPIGRAFE DESCRIBIA UN ESTADO QUE C5 TERMINO, y se reescribe entero en vez
de anotarse: un docstring que describe un estado superado es peor que no
haberlo escrito, y este proyecto ya se tropezo dos veces con eso (SIS-A-03).
Lo que decia: que `materiales_candidatos()` devolvia la tupla vacia para la
Familia C por dos razones acumuladas -- el catalogo era solo de conductos
circulares, y el num. 4.1.1.3.4 a) exceptua a los cruces de canal del piso de
0.90 m --. La primera dejo de ser cierta; la segunda sigue, y ahora es lo que
SOSTIENE el candidato en vez de excluirlo.

LO QUE HAY HOY. `materiales_candidatos()` devuelve UN candidato para la
Familia C: el marco de concreto reforzado, con `FormaSeccion.RECTANGULAR`.
Uno y no tres, porque el TMC y el HDPE son productos de seccion circular y no
hay catalogo de marco en ninguno de los dos. La asignacion del tipo la hace la
Sec. 2.3 de la hoja de ruta, y tiene respaldo en la fuente primaria: el num.
4.1.1.3.4 a) nombra al marco de concreto el PRIMERO entre los tipos comunmente
utilizados, cuenta la seccion rectangular entre las mas usuales y permite
ubicarlo a la cota que se requiera; y la Lamina N 03 lo DIBUJA para este caso
exacto, un marco de concreto en cruce de canal de riego.

Y LO QUE PASA AL PEDIRLO: se detiene. Los cuatro criterios del cajon estan sin
valor por mandato -- el numeral remite la seccion a "cada diseno particular",
de modo que el proyecto no puede escribirla --, y `catalogo()` levanta
`CriterioPendienteError` en el primero que falte. La detencion CAMBIO DE
NATURALEZA y eso es lo que importa: antes el programa afirmaba algo sobre el
CATALOGO ("no hay material candidato para esta familia"), y ahora afirma algo
sobre el EXPEDIENTE ("falta declarar la embocadura del marco"). La primera no
se podia resolver declarando nada; la segunda es una lista de trabajo.

EL PISO DE 0.90 m NO SE HEREDA, y ahora se ve en el codigo y no solo en el
comentario: la progresion del marco no sale de 'diametros_normalizados' sino
de 'secciones_cajon_normalizadas', que es un criterio distinto y sin valor. El
literal del numeral y su ambito siguen en
`constantes_normativas.DIAMETRO_MIN_TEXTO` y `DIAMETRO_MIN_AMBITO`; no se
transcriben aqui.

Excepciones
-----------
    DatoInvalidoError   el 'material' pasado no es uno de TipoMaterial, o el
                        'D' pasado a siguiente_diametro() no pertenece a la
                        progresion de ese material.
    CriterioPendienteError   solo puede llegar desde 'diametros_normalizados'
                        (tiene valor, no deberia dispararse hoy) o si algun
                        dia alguno de los tres vacios documentados arriba
                        se reclasificara a un `valor()` directo.

Uso
---
    from modulos.M2_material import (catalogo, materiales_candidatos,
                                     siguiente_seccion)

    candidatos = materiales_candidatos(punto)   # el marco, en Familia C
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                     forma=FormaSeccion.RECTANGULAR)     # bloquea sin declarar
    seccion = siguiente_seccion(concreto)                # Ø 0.90 m
    seccion = siguiente_seccion(concreto, seccion)       # Ø 1.05 m
"""

from __future__ import annotations

import numbers
from typing import Any, Optional, Tuple, Union

import criterios_adoptados as ca
from constantes_normativas import (CARTAS_CAJON_TA1,
                                   FILAS_MANNING_CONCRETO,HDS5_INLET, H_RELLENO_MIN, MANNING,
                                   SECCION_EG2013, TABLA_09_FILAS, V_MAX)
from dominios import MILIMETROS_POR_METRO
from modelos import (CIFRAS_FACTOR, CIFRAS_FINA, ConstantesHDS5,
                     DatoFaltanteError, DatoInvalidoError,
                     EleccionDeProyecto, Familia, FormaSeccion, Magnitud,
                     Material, PasoDeMemoria, PuntoCritico, Seccion,
                     SeccionCircular, SeccionRectangular, TipoDeVeredicto,
                     TipoMaterial, Veredicto, paso)
from tolerancias import TOL_UMBRAL_NORMATIVO

NUMERAL_CATALOGO = "Sec. 3.2"     # nuevo en v7, sin numeral MTC propio
NUMERAL_MATERIAL = "Sec. 3.4"

CRITERIO_DIAMETROS = "diametros_normalizados"
CRITERIO_D_MAX_CATALOGO = "D_max_catalogo"
CRITERIO_ESPESOR_PARED = "espesor_pared_conducto"
CRITERIO_N_MANNING_HDPE = "n_manning_hdpe"
CRITERIO_HDS5_HDPE = "hds5_embocadura_hdpe"
# Los cinco del cajon (C5). Los cuatro primeros los lee ESTE modulo; el quinto
# lo lee M4 cuando llega al control de salida, y aqui solo viaja su CLAVE
# dentro del `Material`.
CRITERIO_SECCIONES_CAJON = "secciones_cajon_normalizadas"
CRITERIO_N_MANNING_CAJON = "n_manning_cajon"
CRITERIO_EMBOCADURA_CAJON = "embocadura_cajon"
CRITERIO_N_CELDAS_CAJON = "n_celdas_cajon"
# LAS DOS CLAVES DEL ke NO ESTAN AQUI, y no es un olvido: `variables_entrada`
# deduce el consumidor de una variable de los LITERALES de cada modulo, de
# modo que nombrarlas aqui haria figurar a M2 como consumidor de un criterio
# que M2 no lee nunca -- y `consumido_por` es lo que la memoria imprime bajo
# «de donde sale este dato» --. Quien las lee es M4, en el control de salida,
# y por eso viven en `M4_control` con el resto de sus claves.
CRITERIO_V_MAX = {
    TipoMaterial.TMC: "v_max_tmc",
    TipoMaterial.HDPE: "v_max_hdpe",
}

MaterialLike = Union[TipoMaterial, str]

# Nombre para el reporte y norma de producto de cada material (Sec. 3.2). NO
# es "la norma que topa el diametro": esa lectura era el defecto NOR-PRO-01 /
# NOR-PRO-02 -- A760 tabula hasta 3600 mm y M 170M tambien, de modo que
# ninguna de ellas sostiene el tope que el proyecto aplica. Es la norma que
# rige el PRODUCTO (materiales, fabricacion, aceptacion), y viaja al reporte
# como tal. El tope sale del criterio 'D_max_catalogo' y se imprime con su
# propio rotulo de catalogo.
_NOMBRE = {
    TipoMaterial.CONCRETO_REFORZADO: "Concreto reforzado",
    TipoMaterial.TMC: "TMC galvanizada",
    TipoMaterial.HDPE: "HDPE",
}
# LAS DESIGNACIONES SON LAS METRICAS, QUE SON LAS QUE EL PROYECTO TIENE
# (NOR-PRO-05). Este dict escribia "ASTM C76 / AASHTO M170", que son las
# versiones EN PULGADAS, y la memoria las imprimia en un expediente que opera
# en SI de punta a punta. El documento que hay en normas/ se designa a si
# mismo "AASHTO Designation: M 170M-04 / ASTM Designation: C 76M-02", se
# titula "... [Metric]" y su num. 1.2 dice "This specification is the metric
# counterpart of M 170": no son la misma norma con otro nombre, son la
# contraparte metrica. Citar la imperial manda al revisor a un documento que
# el expediente no tiene y cuyas tablas estan en pulgadas.
#
# La de TMC lleva la designacion DUAL tal como la norma se nombra
# -- A760/A760M cubre los dos sistemas --, que es lo que el registro tiene
# catalogado (`normativa.fuentes.ASTM_A760`, edicion "A760/A760M-10"). No se
# le inventa una metrica que la norma no separa.
_NORMA_PRODUCTO = {
    TipoMaterial.CONCRETO_REFORZADO: "AASHTO M 170M-04 / ASTM C 76M-02 (metrica)",
    TipoMaterial.TMC: "AASHTO M 36 / ASTM A760/A760M-10",
    TipoMaterial.HDPE: "AASHTO M294",
}

# Claves de MANNING (Tabla N 09) y de HDS5_INLET (Tabla A.1) que si tienen
# fila normativa directa: HDPE no esta en ninguna de las dos tablas del
# Manual MTC y por eso no aparece en estos dos dicts (usa criterio adoptado).
# LA ELECCION DE SUBFILA SE DECLARA AQUI, QUE ES DONDE SE HACE (NOR-HID-11).
# La Tabla N 09 no tiene una fila por material sino un arbol de subfilas, y
# elegir una es una decision sobre QUE ES la obra, no sobre que valor conviene:
#
#   TMC     -> "Metal corrugado / dren para aguas lluvias" (0.021/0.024/0.030),
#              NO "Metal corrugado / sub - dren" (0.017/0.019/0.021). Una
#              alcantarilla evacua escorrentia superficial; un sub-dren capta
#              agua del terreno. La confusion no se detectaba mirando los
#              numeros: el par (n_min, n_max) de la subfila elegida, (0.021,
#              0.030), empieza justo donde TERMINA la otra, y el codigo la
#              guardaba bajo la clave generica 'metal_corrugado'.
#   Concreto -> "Concreto / tubo recto y libre de basuras" (0.010/0.011/0.013),
#              la primera de las siete subfilas de concreto. Es la que
#              describe el conducto de este proyecto: tramo recto, sin camaras
#              ni conexiones intermedias (esas son "tubo de alcantarillado con
#              camaras, entradas", 0.013/0.015/0.017). Si un punto llevara
#              camaras, esta clave cambiaria -- y con ella el tirante, porque
#              el n_max sube de 0.013 a 0.017.
#   HDPE    -> no esta en la tabla: criterio 'n_manning_hdpe', que aplica por
#              analogia la MISMA subfila del concreto.
_MANNING_CLAVE = {
    TipoMaterial.CONCRETO_REFORZADO: "concreto_tubo_recto",
    TipoMaterial.TMC: "metal_corrugado_dren_aguas_lluvias",
}
_HDS5_CLAVE = {
    TipoMaterial.CONCRETO_REFORZADO: "circular_concreto_square_edge_headwall",
    TipoMaterial.TMC: "circular_cmp_headwall",
}
# Tabla N 10: solo el concreto tiene fila. TMC y HDPE dependen de los vacios
# 'v_max_tmc' / 'v_max_hdpe' (CRITERIO_V_MAX), no de esta tabla.
_V_MAX_CLAVE = {
    TipoMaterial.CONCRETO_REFORZADO: "concreto",
}
# H_RELLENO_MIN usa 'concreto' donde TipoMaterial usa 'concreto_reforzado':
# la clave del dict del Anexo B no coincide con el `value` del enum en ese
# material, y solo en ese. Se mapea aqui en vez de renombrar la constante,
# que es transcripcion literal del Anexo.
_EG2013_CLAVE = {
    TipoMaterial.CONCRETO_REFORZADO: "concreto",
    TipoMaterial.TMC: "tmc",
    TipoMaterial.HDPE: "hdpe",
}


# ---------------------------------------------------------------------------
# Validacion de entrada
# ---------------------------------------------------------------------------

def _tipo_material(material: MaterialLike) -> TipoMaterial:
    try:
        return TipoMaterial(material)
    except ValueError:
        raise DatoInvalidoError(
            "material", valor=material,
            motivo="los materiales de Sec. 3.4 son "
                   f"{', '.join(m.value for m in TipoMaterial)}",
        ) from None


def _valor_si_declarado(clave: str) -> Optional[Any]:
    """
    Delega en `ca.valor_si_declarado`, la lectura tolerante publica: devuelve
    el valor del criterio, o None si sigue sin declarar, SIN lanzar
    CriterioPendienteError y sin registrarlo como usado en ese caso -- un
    criterio vacio no se aplico a nada y no hay uso que declarar en M11.

    Antes esta funcion consultaba `ca.criterio(clave).valor`, que es el valor
    DEL ARCHIVO, y devolvia None sin mirar las declaraciones en caliente. Con
    eso, un criterio vacio en el archivo y declarado desde la GUI (que usa
    `ca.establecer_valor_dinamico`) seguia llegando aqui como None: el
    catalogo no veia la declaracion. La consecuencia no era solo un dato
    perdido -- en `n_manning_hdpe` el None se desempaquetaba en (n_min, n_max)
    y reventaba con TypeError, un fallo de programa por un dato que el usuario
    SI habia declarado.

    Se conserva como envoltorio con nombre propio, en vez de llamar a `ca`
    directo en los tres sitios, porque el docstring de este modulo la cita
    como la lectura de los "vacios que el catalogo deja en None".
    """
    return ca.valor_si_declarado(clave)


# ---------------------------------------------------------------------------
# Sec. 3.2 - Catalogo de diametros
# ---------------------------------------------------------------------------

def _progresion() -> dict:
    return ca.valor(CRITERIO_DIAMETROS)


def _topes() -> dict:
    return ca.valor(CRITERIO_D_MAX_CATALOGO)


# ---------------------------------------------------------------------------
# Sec. 3.2 - Geometria fisica del conducto: espesor de pared y D exterior
# ---------------------------------------------------------------------------

def espesor_pared(material: Material, D: float) -> float:
    """
    t, espesor de pared del conducto para el diametro D, m
    ('espesor_pared_conducto', [A]).

    EL ESPESOR DEPENDE DEL DIAMETRO, y por eso esta funcion recibe D. La
    AASHTO M 170M-04 tabula la columna «Wall Thickness» por diametro
    designado, no un numero por material: entre el tubo de 0.90 m y el de
    2.70 m hay 150 mm de diferencia de pared. Mientras el criterio fue un
    escalar por material, un punto que cerrara en un diametro distinto del que
    se tuvo en mente al declararlo se calculaba con el espesor equivocado sin
    que nada avisara -- y el bucle de MD recorre el catalogo entero, de modo
    que no era un caso remoto.

    LA CLAVE DEL DICT ES EL DIAMETRO DESIGNADO EN MILIMETROS, entero, que es
    como lo imprime la norma de producto y como se pide un tubo. El D del
    calculo es un float en metros: la conversion es `round(D * 1000)`, y no
    hay comparacion de floats de por medio -- que es lo que la regla de
    CLAUDE.md prohibe -- porque el redondeo a entero de una serie que avanza
    de 150 en 150 mm no tiene ambiguedad.

    CUATRO VACIOS DISTINTOS Y CUATRO DETENCIONES DISTINTAS, ninguna un fallo
    de programa:

    - Criterio SIN valor -> `CriterioPendienteError` (la lanza `ca.valor`).
    - Criterio CON valor pero SIN ESTE MATERIAL -> `DatoFaltanteError`. El
      criterio es un dict por material y puede estar declarado para unos y no
      para otros; es el caso vivo del expediente, donde el espesor del
      concreto sale de una tabla que esta en `normas/` y el del HDPE de la
      AASHTO M294, que no esta. El revisor tiene que AÑADIR la entrada de ese
      material, y por eso es Faltante y no Invalido (CLAUDE.md). MD descarta
      el material con su causa citada entera y sigue con el siguiente
      candidato: un material sin fuente no mata el punto.
    - Material declarado pero SIN ESTE DIAMETRO -> `DatoFaltanteError`
      tambien, y es la deteccion que el modelo anterior no podia dar: dice
      exactamente que fila de la tabla falta transcribir.
    - Entrada declarada que no es un numero -> `DatoInvalidoError`.

    Hasta S20 la segunda rama era un `raise AssertionError` desnudo -- la
    misma mina que V8 tenia --: declarar el criterio para un solo material
    tumbaba la corrida entera con un fallo de programa en vez de descartar
    ese material.

    Y HAY UN QUINTO VACIO, QUE ES EL DEL MARCO, y se detiene ANTES que los
    cuatro. Lo encontro la auditoria adversarial de C5 midiendo lo que pasaba
    sin el, y no era una imprecision de texto: era un NUMERO INSEGURO. La
    tabla que este criterio declara es la columna «Wall Thickness» de una
    norma de TUBERIA, indexada por diametro designado en milimetros, y las
    alturas de marco plausibles caen sobre esa misma serie de 900 + 150k mm.
    De modo que un marco de 2.00 x 1.50 m NO se detenia: recibia t = 0.150 m,
    la pared del tubo de 1500 mm, y con ella `diametro_exterior` le daba a V7
    un cilindro de 1.80 m. Medido sobre esa seccion: la subpresion real de un
    prisma es 40.6 kN/m y la del cilindro 25.0 kN/m -- un 63 % menos --,
    mientras el peso de relleno cae solo un 28 %, de modo que V7 SOBREESTIMA
    la seguridad del marco alrededor de un 27 %. Es la direccion insegura, y
    es MAT-D3 reintroducido para el cajon.

    El docstring de `M5.v7_flotacion` que C5 escribio decia que «un marco
    vaciado in situ no tiene fila ahi». La frase era verdadera sobre la NORMA
    y falsa sobre el DICT, que es lo que el codigo lee, y una declaracion en
    un docstring no detiene ningun calculo. Por eso la deteccion esta aqui:
    `DatoFaltanteError`, porque lo que falta es un dato que hay que CONSEGUIR
    -- el espesor de pared de un marco sale de su calculo estructural, no de
    una tabla de producto --, y porque asi la Fase 5 de un marco se detiene en
    V7 en vez de publicar un margen que no es. Levantarla es de C7, que
    generaliza M8 a la seccion.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        raise DatoFaltanteError(
            f"{CRITERIO_ESPESOR_PARED}[marco]",
            detalle=(
                f"el criterio '{CRITERIO_ESPESOR_PARED}' tabula la pared por "
                "DIAMETRO DESIGNADO de una norma de tuberia (columna 'Wall "
                "Thickness' de AASHTO M 170M-04), y un marco vaciado in situ "
                "no tiene fila ahi: su espesor sale de su propio calculo "
                "estructural. NO SE PUEDE LEER LA FILA DEL TUBO DE LA MISMA "
                "ALTURA, aunque exista: la altura de un marco cae sobre la "
                "misma serie de 900 + 150k mm por coincidencia, y con esa "
                "pared el volumen desplazado se calcula como un CILINDRO -- "
                "V7 sobreestima la seguridad alrededor de un 27 % sobre un "
                "marco de 2.00 x 1.50 m, que es la direccion insegura. "
                "Mientras esto no se declare, la Fase 5 de un marco se "
                "detiene en V7 y no publica un margen que no es. Lo cierra la "
                "generalizacion de M8 a la seccion"
            ),
        )
    if material.espesor_pared is None:
        ca.valor(CRITERIO_ESPESOR_PARED)      # CriterioPendienteError si esta vacio
        raise DatoFaltanteError(
            f"{CRITERIO_ESPESOR_PARED}[{material.tipo.value}]",
            detalle=(
                f"el criterio '{CRITERIO_ESPESOR_PARED}' esta declarado, pero "
                f"no trae entrada para «{material.tipo.value}». Es un dict "
                "por material y cada entrada necesita su propia fuente: la "
                "del concreto es la columna 'Wall Thickness' de las Tablas 1 "
                "a 5 de AASHTO M 170M-04, la del TMC depende del calibre que "
                "fije la Fase 8 ('clases_producto_por_relleno') y la del "
                "HDPE sale de AASHTO M294, que NO esta en normas/. Sin "
                "espesor no hay diametro exterior, y sin diametro exterior no "
                "hay clave fisica (7.A) ni volumen desplazado (V7)"
            ),
        )
    ca.valor(CRITERIO_ESPESOR_PARED)          # registra el uso para M11
    por_diametro = material.espesor_pared
    if not isinstance(por_diametro, dict):
        raise DatoInvalidoError(
            campo=CRITERIO_ESPESOR_PARED, valor=por_diametro,
            motivo=f"el espesor declarado para '{material.tipo.value}' no es "
                   "una tabla por diametro. Este criterio se declara como un "
                   "dict de dicts: {'concreto_reforzado': {900: 0.100, 1050: "
                   "0.113, ...}}, con el diametro designado en MILIMETROS "
                   "como clave y el espesor en METROS como valor")
    designado = round(D * MILIMETROS_POR_METRO)
    if designado not in por_diametro:
        raise DatoFaltanteError(
            f"{CRITERIO_ESPESOR_PARED}[{material.tipo.value}][{designado}]",
            detalle=(
                f"el criterio '{CRITERIO_ESPESOR_PARED}' declara "
                f"«{material.tipo.value}» pero no la fila de {designado} mm. "
                f"Los diametros declarados son "
                f"{sorted(por_diametro)}. Falta transcribir esa fila de la "
                "columna 'Wall Thickness' de la norma de producto: no se "
                "interpola ni se toma la fila vecina, porque el espesor "
                "gobierna la clave fisica (7.A) y el volumen desplazado de V7 "
                "y los dos quedan del lado inseguro si se estima por lo bajo"
            ),
        )
    t = por_diametro[designado]
    if not isinstance(t, numbers.Real):
        raise DatoInvalidoError(
            campo=CRITERIO_ESPESOR_PARED, valor=t,
            motivo=f"el espesor declarado para '{material.tipo.value}' en el "
                   f"diametro {designado} mm no es un numero. Los valores de "
                   "la tabla son espesores en METROS")
    return t


def diametro_exterior(*, material: Material, D: float) -> float:
    """
    D_ext = D + 2*t, m: el diametro EXTERIOR del conducto.

    `D` es el diametro interior -- el hidraulico, el que entra en Manning y en
    `modelos.SeccionCircular` -- y `D_ext` es el que gobierna todo lo que toca al
    terreno: el Bc del Art. 12.6.6.3 de AASHTO LRFD (cobertura minima), el
    volumen desplazado de la subpresion de V7 (num. 2.4.3.8.2 del Manual de
    Puentes) y la posicion de la clave fisica. Confundirlos es MAT-D3 y
    MAT-D4: los dos quedaban del lado inseguro por el mismo motivo.

    Se detiene con `CriterioPendienteError` mientras 'espesor_pared_conducto'
    siga vacio (ver `espesor_pared`).
    """
    return D + 2 * espesor_pared(material, D)


def siguiente_diametro(material: MaterialLike,
                       D: Optional[float] = None) -> Optional[float]:
    """
    Siguiente diametro de la progresion 0.90 m + 0.15 m (Sec. 3.2) para ese
    material, o None si D ya esta en el ultimo escalon posible bajo el tope
    de la norma de producto -- la Fase 4 lee ese None como "material
    descartado por diametro requerido", nunca como un numero inexistente.

    D=None pide el primer escalon (el minimo normativo). Un D que no cae
    exacto sobre la progresion (no es inicio + n*paso) es DatoInvalidoError:
    este catalogo no reconoce diametros "de proveedor".
    """
    tipo = _tipo_material(material)
    prog = _progresion()
    inicio, paso = prog["inicio"], prog["paso"]
    tope = _topes()[tipo.value]      # tope de CATALOGO, no normativo

    if D is None:
        return inicio

    pasos = (D - inicio) / paso
    n = round(pasos)
    if abs(pasos - n) > TOL_UMBRAL_NORMATIVO or n < 0:
        raise DatoInvalidoError(
            "D", valor=D,
            motivo=f"no pertenece a la progresion de {inicio} m + {paso} m "
                   f"de {NUMERAL_CATALOGO} para '{tipo.value}'",
        )

    siguiente = round(inicio + (n + 1) * paso, 2)
    if siguiente > tope + TOL_UMBRAL_NORMATIVO:
        return None
    return siguiente


def siguiente_seccion(material: Material,
                      actual: Optional[Seccion] = None) -> Optional[Seccion]:
    """
    Siguiente escalon del catalogo COMO SECCION, o None si se agoto (Sec. 3.2).

    ES LA PUERTA QUE C5 TIENE QUE PONER, y la razon es un modo de fallo
    silencioso: hasta aqui MD pedia `siguiente_diametro(material.tipo)` y
    construia `SeccionCircular(D)` con lo que recibiera. Un material de MARCO
    tiene el mismo `TipoMaterial` que un tubo de concreto, de modo que esa
    llamada le habria devuelto 0.90, 1.05, 1.20... -- la progresion CIRCULAR
    -- y el punto se habria dimensionado como un tubo con las constantes de
    HDS-5 de un cajon. Ningun numero habria salido negativo ni infinito: solo
    equivocado. Preguntar por la SECCION y no por el diametro cierra esa
    puerta, porque la progresion la elige la forma.

    `actual` es la seccion del escalon anterior, no un numero: quien recorre
    el catalogo no tiene por que saber sobre que magnitud avanza.

    Con `FormaSeccion.RECTANGULAR` la progresion sale del criterio
    'secciones_cajon_normalizadas', que hoy esta SIN VALOR por mandato de la
    Sec. 4.1.1.3.4 a) -- el numeral exceptua a los cruces de canal del piso de
    0.90 m y los remite a "cada diseno particular" --. La llamada se detiene
    con `CriterioPendienteError`, que es lo que tiene que pasar.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        return _siguiente_seccion_cajon(actual)
    D = siguiente_diametro(material.tipo,
                           None if actual is None else actual.altura)
    return None if D is None else SeccionCircular(D)


def _misma_seccion(a: Seccion, b: Seccion) -> bool:
    """
    Dos secciones rectangulares son la misma escalon del catalogo.

    CON TOLERANCIA Y NO CON `==`, igual que `siguiente_diametro` compara su
    progresion: CLAUDE.md prohibe comparar floats con `==` sin excepcion. Hoy
    las dos secciones se reconstruyen del mismo criterio y el `==` acertaba
    siempre; deja de acertar en cuanto una llegue de otro sitio -- de un JSON
    de tablero, de la GUI, de un round-trip por texto --, y entonces el bucle
    de MD dejaria de reconocer su propio escalon y levantaria un
    `DatoInvalidoError` sobre una seccion que si esta en la serie.
    """
    return (abs(a.B - b.B) <= TOL_UMBRAL_NORMATIVO
            and abs(a.altura - b.altura) <= TOL_UMBRAL_NORMATIVO)


def _siguiente_seccion_cajon(actual: Optional[Seccion]) -> Optional[Seccion]:
    """
    Siguiente par (B, H) de la progresion declarada, en el orden en que el
    criterio la declara.

    NO SE ORDENA AQUI, y conviene decir por que: en una progresion de dos
    dimensiones "el siguiente" no es una relacion de orden que el programa
    pueda deducir -- crecer en ancho y crecer en canto no son intercambiables,
    y cual conviene depende de la rasante y del canal --. El orden es parte de
    lo que el proyectista declara, y este bucle lo respeta tal cual.
    """
    secciones = [SeccionRectangular(B, H) for B, H in progresion_de_cajon()]
    if actual is None:
        return secciones[0] if secciones else None
    for anterior, siguiente in zip(secciones, secciones[1:]):
        if _misma_seccion(anterior, actual):
            return siguiente
    if secciones and _misma_seccion(secciones[-1], actual):
        return None
    raise DatoInvalidoError(
        "seccion", valor=(actual.B, actual.H),
        motivo=f"no pertenece a la progresion declarada en "
               f"'{CRITERIO_SECCIONES_CAJON}': este catalogo no reconoce "
               f"secciones fuera de la serie que el expediente declara",
    )


# ---------------------------------------------------------------------------
# Sec. 3.4 - Catalogo de material
# ---------------------------------------------------------------------------

def _carta_de_cajon() -> str:
    """
    La clave de la carta de la Tabla A.1 que 'embocadura_cajon' declara,
    comprobada contra las CARTAS DE CAJON y no contra la tabla entera.

    LAS DOS GUARDIAS SON DE LA MISMA FAMILIA Y LAS DOS LAS PIDIO LA AUDITORIA
    ADVERSARIAL DE C5, que midio los dos agujeros:

      * `HDS5_INLET[ca.valor(...)]` a pelo acepta
        «circular_concreto_square_edge_headwall» y le da a un MARCO las
        constantes de la Carta 1 CIRCULAR -- y ademas la Forma 1, con su
        Ks*S --, mientras el paso de memoria imprime que la carta es «del
        bloque de CAJON» invocando el num. A.3, que es la regla que se estaria
        violando. Este es el unico punto del codigo donde la regla vinculante
        #5 se puede hacer cumplir.
      * y una ERRATA en la clave --«cajon_concreto_aleta_45_d04»-- sale como
        `KeyError` desnudo, que no desciende de `ErrorProyecto`: `cli._etapa`
        no lo captura, tumba la corrida entera y la GUI no lo puede distinguir
        de un fallo del programa. Es la mina que S20 desactivo tres veces.

    Es `DatoInvalidoError` y no `CriterioPendienteError` porque el criterio SI
    esta declarado: hay que CORREGIRLO, no declararlo.
    """
    clave = ca.valor(CRITERIO_EMBOCADURA_CAJON)
    if not isinstance(clave, str) or clave not in CARTAS_CAJON_TA1:
        raise DatoInvalidoError(
            CRITERIO_EMBOCADURA_CAJON, valor=clave,
            motivo="se espera la CLAVE de una carta de CAJON de la Tabla A.1 "
                   "del HDS-5. El num. A.3 prohibe expresamente cruzar "
                   "coeficientes entre geometrias -- «coefficients for "
                   "rectangular (box) shapes should not be used for "
                   "nonrectangular ... shapes and vice-versa» --, de modo que "
                   "una carta circular aqui no es un valor discutible: es "
                   "otra geometria. Claves admitidas: "
                   + ", ".join(sorted(CARTAS_CAJON_TA1)),
        )
    return clave


def _fila_manning_de_cajon() -> str:
    """
    La fila de la Tabla N 09 de la que 'n_manning_cajon' toma su analogia.

    ACOTADA AL SUBGRUPO «a. Concreto», que es lo que el criterio declara: un
    marco de concreto no puede tomar prestada la n de un metal corrugado ni la
    de unas duelas de madera, y sin esta guardia `MANNING[...]` las aceptaba
    -- y una errata en la clave salia como `KeyError` desnudo --.
    """
    clave = ca.valor(CRITERIO_N_MANNING_CAJON)
    if not isinstance(clave, str) or clave not in FILAS_MANNING_CONCRETO:
        raise DatoInvalidoError(
            CRITERIO_N_MANNING_CAJON, valor=clave,
            motivo="se espera la CLAVE de una fila del subgrupo «a. Concreto» "
                   "del grupo A de la Tabla N 09: la analogia que este "
                   "criterio declara es DENTRO del material del conducto, no "
                   "entre materiales. Claves admitidas: "
                   + ", ".join(sorted(FILAS_MANNING_CONCRETO)),
        )
    return clave


def numero_de_celdas(material: Material) -> int:
    """
    N, el numero de barriles del marco ('n_celdas_cajon'), validado.

    LA INTEGRALIDAD SE COMPRUEBA, y no es celo: la guardia anterior era
    `not celdas >= 1`, que deja pasar `2.5` -- lo midio la auditoria
    adversarial de C5: `Q/2.5` sale sin quejarse y la memoria imprimiria «2.5
    celdas» --. Un barril y medio no se construye, y el propio `dominio` del
    criterio dice «entero >= 1».

    LA GUARDIA VA ESCRITA EN POSITIVO Y NEGADA, que es la forma que MAT-D13
    dejo fijada: `not (... >= 1)` atrapa tambien un NaN, que frente a `< 1`
    seria falso y pasaria.

    VIVE EN M2 Y NO EN MD porque tiene DOS consumidores y los dos estan
    debajo del orquestador: `MD._caudal_por_barril`, que reparte el caudal, y
    `M5.v6_material_solido_arrastre`, que compara el numero contra la Sec.
    3.1. Ponerlo en MD obligaba a M5 a importar al modulo que lo orquesta.
    Leerlo dos veces con dos guardias distintas es como divergen los numeros.
    """
    celdas = ca.valor(CRITERIO_N_CELDAS_CAJON)
    entero = isinstance(celdas, int) and not isinstance(celdas, bool)
    if not entero or not celdas >= 1:
        raise DatoInvalidoError(
            CRITERIO_N_CELDAS_CAJON, valor=celdas,
            motivo="el numero de celdas del marco tiene que ser un ENTERO "
                   "mayor o igual que 1: es cuantos barriles se construyen, "
                   "y el caudal de diseño se reparte entre ellos. Un valor "
                   "fraccionario no es un numero de barriles")
    return celdas


def progresion_de_cajon() -> tuple:
    """
    La serie (B, H) que 'secciones_cajon_normalizadas' declara, validada.

    SIN ESTA GUARDIA, UN ESCALAR DECLARADO DESDE LA GUI REVIENTA CON
    `TypeError`. Es exactamente el modo de fallo que este mismo modulo ya
    tenia documentado para 'espesor_pared_conducto' --«la GUI solo sabe
    ofrecer float o str»-- y que C5 no habia replicado aqui; lo midio la
    auditoria adversarial. Se valida ademas lo que un revisor no puede ver a
    ojo en una serie de pares: que cada dimension sea un numero POSITIVO. Lo
    que NO se valida es el ORDEN, y es deliberado -- `_siguiente_seccion_cajon`
    explica por que en dos dimensiones «el siguiente» no es una relacion que
    el programa pueda deducir --.
    """
    progresion = ca.valor(CRITERIO_SECCIONES_CAJON)
    forma_mala = DatoInvalidoError(
        CRITERIO_SECCIONES_CAJON, valor=progresion,
        motivo="se espera una serie de pares (B, H) en metros -- por ejemplo "
               "((1.50, 1.20), (2.00, 1.50)) --, con B y H interiores de UNA "
               "celda y los dos POSITIVOS. No es un escalar ni un solo par: "
               "el bucle de MD recorre la serie entera, igual que recorre los "
               "diametros",
    )
    try:
        pares = tuple((float(B), float(H)) for B, H in progresion)
    except (TypeError, ValueError):
        raise forma_mala from None
    if not pares or any(B <= 0 or H <= 0 for B, H in pares):
        raise forma_mala
    return pares


def catalogo(material: MaterialLike,
             forma: FormaSeccion = FormaSeccion.CIRCULAR) -> Material:
    """
    Reune en un `Material` todo lo que la Fase 4 y la Fase 5 necesitan de ese
    material: doble n de Manning, tope de diametro (Sec. 3.2), constantes
    HDS-5 de control de entrada (Sec. 4.2), rango de velocidad maxima
    (Tabla N 10 o el vacio que la sustituye), relleno minimo sobre la clave
    (Sec. 7.A) y seccion de EG-2013 para el presupuesto.

    v_max_adoptado, espesor_pared y la doble n del HDPE pueden salir en None si
    su criterio se vacia: se leen con `_valor_si_declarado()`, no con
    `ca.valor()` ni con `ca.criterio()`. Ver "Campos que el catalogo puede
    dejar en None" en el docstring del modulo, incluida la excepcion de
    'n_manning_hdpe'.

    `h_relleno_min_eg2013` NO es de esa familia aunque tambien sea Optional:
    su None no es un vacio pendiente sino el hecho normativo de que EG-2013
    fija la altura minima de relleno solo para HDPE. Nadie lo declarara nunca.

    LA FORMA ES UN PARAMETRO DESDE C5, y no se deduce del `tipo`: un marco de
    concreto y un tubo de concreto son el mismo `TipoMaterial`, y lo que los
    separa es de que progresion sale su seccion, de que fila su n y de que
    carta sus constantes de HDS-5.

    EL CATALOGO DEL MARCO NO SE PUEDE LISTAR MIENTRAS SUS CRITERIOS ESTEN
    VACIOS, y es deliberado. La regla general de este modulo -- escrita en
    "Campos que el catalogo puede dejar en None" -- es que un catalogo que no
    se puede ni listar no es un catalogo, es un candado, y por eso los cuatro
    criterios Optional se leen con `_valor_si_declarado()`. Con el marco esa
    salida NO existe, por dos razones que se acumulan:

      * `Material.hds5` NO es Optional. Sin `embocadura_cajon` no hay carta, y
        no hay carta por defecto que poner: este repositorio tiene QUINCE
        filas de cajon de concreto transcritas de la Tabla A.1 -- Cartas 8 a
        12; la tabla trae mas, y lo que queda fuera lo censa el `Acotada` de
        `normativa/tablas.py::T_HDS5_A1` --, tres de Forma 1 y doce de Forma
        2, y elegir una por el proyectista seria exactamente lo que esta
        sesion existe para no hacer.
      * El n del marco tiene el problema que este mismo modulo dejo advertido
        para 'n_manning_hdpe': su None se desempaqueta en `n_min, n_max` y
        saldria como `TypeError` -- un fallo de PROGRAMA -- en vez de como
        `CriterioPendienteError` del expediente. El aviso decia «antes de
        vaciarlo, hay que darle un punto de uso que bloquee». El punto de uso
        que bloquea es esta lectura, y por eso el marco lee con `ca.valor()`.

    De modo que para un marco esta funcion LEVANTA `CriterioPendienteError` en
    el primer criterio sin declarar, y eso es lo correcto: el revisor tiene
    que ver que le falta antes de que el programa dimensione nada.
    """
    tipo = _tipo_material(material)

    if forma is FormaSeccion.RECTANGULAR:
        # EL ORDEN DE ESTAS DOS LECTURAS DECIDE QUE CRITERIO VE EL REVISOR
        # PRIMERO, porque `cli._etapa` registra UN bloqueo por etapa. Se lee
        # primero la embocadura y no el n: la embocadura elige la carta Y la
        # forma de ecuacion, y con ella el ke del control de salida, de modo
        # que es la que arrastra mas decisiones detras. Los otros tres
        # aparecen en cuanto este se declare.
        hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[_carta_de_cajon()])
        n_min, n_max = MANNING[_fila_manning_de_cajon()]
    elif tipo is TipoMaterial.HDPE:
        n_min, n_max = _valor_si_declarado(CRITERIO_N_MANNING_HDPE)
        hds5 = ConstantesHDS5.desde_dict(ca.valor(CRITERIO_HDS5_HDPE))
    else:
        n_min, n_max = MANNING[_MANNING_CLAVE[tipo]]
        hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[_HDS5_CLAVE[tipo]])

    # Los dos techos NO son el mismo campo (SIS-A-06): uno es la fila literal
    # de la Tabla N 10 y el otro un escalar de criterio. Cada material llena
    # uno y deja el otro en None.
    v_max_tabla10 = V_MAX.get(_V_MAX_CLAVE.get(tipo))
    v_max_adoptado = (None if tipo in _V_MAX_CLAVE
                      else _valor_si_declarado(CRITERIO_V_MAX[tipo]))

    espesores = _valor_si_declarado(CRITERIO_ESPESOR_PARED)
    if espesores is not None and not hasattr(espesores, "get"):
        # Una declaracion mal formada es problema del EXPEDIENTE, no del
        # programa: sin esta guardia un escalar declarado desde la GUI --
        # que solo sabe ofrecer float o str -- reventaba aqui con TypeError.
        raise DatoInvalidoError(
            campo=CRITERIO_ESPESOR_PARED, valor=espesores,
            motivo="se declaro un valor unico donde el criterio espera una "
                   "tabla de espesores por material: "
                   "{'concreto_reforzado': {900: 0.100, 1050: 0.113, ...}, "
                   "'tmc': ..., 'hdpe': ...}, con el diametro designado en "
                   "MILIMETROS como clave y el espesor en METROS como valor",
        )

    # EL TOPE DEL MARCO NO SALE DE 'D_max_catalogo', y no es un detalle de
    # atribucion: el valor de ese criterio es un DIAMETRO DE TUBO por material
    # -- lo que el mercado entrega en tuberia de concreto, de TMC o de HDPE --
    # y no dice nada sobre hasta donde llega una serie de marcos vaciados in
    # situ. El tope de un marco es la mayor altura interior que su propia
    # progresion declarada ofrece, y por eso se lee de ella. Un cajon con
    # `D_max` prestado del tubo habria dado a V9 un umbral verdadero en
    # numero y falso en procedencia, que es la clase de defecto que
    # NOR-PRO-01 cerro para el circular.
    if forma is FormaSeccion.RECTANGULAR:
        D_max = max(H for _, H in progresion_de_cajon())
        D_max_rotulo = (
            "TOPE DE CATALOGO, NO DE NORMA: mayor altura interior de la "
            f"progresion que el expediente declara en "
            f"'{CRITERIO_SECCIONES_CAJON}' [A]. Superarlo NO significa "
            "'seccion inexistente' -- un marco se vacia in situ en la "
            "dimension que se arme -- sino 'fuera de la serie declarada', y "
            "se levanta declarando la serie completa")
    else:
        D_max = _topes()[tipo.value]
        D_max_rotulo = ca.criterio(CRITERIO_D_MAX_CATALOGO).de_catalogo

    return Material(
        tipo=tipo,
        nombre=_NOMBRE[tipo],
        n_min=n_min,
        n_max=n_max,
        D_max=D_max,
        D_max_de_catalogo=D_max_rotulo,
        norma_producto=_NORMA_PRODUCTO[tipo],
        hds5=hds5,
        fila_manning=_fila_manning(tipo, forma),
        v_max_tabla10=v_max_tabla10,
        v_max_adoptado=v_max_adoptado,
        # [N] directo de EG-2013 508.07 y SOLO para HDPE: los otros dos
        # materiales no tienen minimo en el EG-2013, y su None significa eso.
        h_relleno_min_eg2013=H_RELLENO_MIN[_EG2013_CLAVE[tipo]],
        espesor_pared=None if espesores is None else espesores.get(tipo.value),
        seccion_eg2013=SECCION_EG2013[tipo.value],
        forma=forma,
        pasos=(_pasos_del_marco() if forma is FormaSeccion.RECTANGULAR
               else ()),
    )


def _pasos_del_marco() -> Tuple[PasoDeMemoria, ...]:
    """
    La traza de Fase 3 del marco: las CINCO decisiones que lo definen, cada
    una con su fundamento, su cita y la eleccion que la resolvio.

    POR QUE LA EMITE EL CATALOGO Y NO EL REPORTE. Es la regla de §4.5: la
    memoria la emite el calculo, y estas cinco se deciden aqui. Viajan en
    `Material.pasos` y `M4._pasos_hidraulicos` las antepone a las suyas, de
    modo que llegan a la memoria por el canal que ya existe -- el bloque que
    M11 titula «Fases 3 y 4» -- sin abrir uno nuevo.

    POR QUE EL TUBO NO TIENE NINGUNA. Su fila de la Tabla N 09 y su carta de
    la Tabla A.1 son LECTURA DIRECTA de una tabla normativa: no hay eleccion
    que desarrollar, y lo que hay ya sale en el bloque de criterios. El marco
    tiene cuatro criterios declarados por el proyectista y uno mas -- el ke --
    que se mueve con ellos: una memoria que no los desarrolle no los puede
    defender.
    """
    progresion = [(float(B), float(H))
                  for B, H in ca.valor(CRITERIO_SECCIONES_CAJON)]
    celdas = ca.valor(CRITERIO_N_CELDAS_CAJON)
    fila = ca.valor(CRITERIO_N_MANNING_CAJON)
    carta = ca.valor(CRITERIO_EMBOCADURA_CAJON)
    n_min, n_max = MANNING[fila]
    menor = min(progresion, key=lambda par: par[0] * par[1])

    tipo_marco = paso(
        "F3.TIPO_MARCO",
        codigo="3.1",
        que="Tipo de estructura del cruce",
        formula="Familia C (cruce de canal de riego, Sec. 2.3) -> alcantarilla "
                "tipo marco de concreto, de seccion rectangular",
        formula_cita_id="MC_HHD.4.1.1.3.4a#TIPOS",
        citas_textuales=("MC_HHD.4.1.1.3.4a#TIPOS", "MC_HHD.LAMINA_03"),
        sustitucion=(
            Magnitud("familia", Familia.C.value, "",
                     "clasificacion del punto (Sec. 2.3 de la hoja de ruta): "
                     "cruce de canal o dren de riego",
                     cifras=None),),
        resultado=Magnitud("tipo de estructura", "marco de concreto armado", "",
                           "asignado por la Sec. 2.3 y respaldado por el "
                           "numeral y por la Lamina N 03, que dibuja un marco "
                           "de concreto en cruce de canal de riego",
                           cifras=None),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="adopcion de tipologia, no verificacion"),
        nota_del_proyecto=(
            "La ASIGNACION del tipo la hace la Sec. 2.3 de la hoja de ruta, "
            "que no es fuente primaria. Lo que aportan las citas de arriba es "
            "que esa asignacion tiene respaldo en el Manual: el marco de "
            "concreto encabeza los tipos comunmente utilizados, la seccion "
            "rectangular esta entre las mas usuales, y la Lamina N 03 lo "
            "dibuja para este caso exacto."),
    )

    seccion_canal = paso(
        "F3.SECCION_CANAL",
        codigo="3.2",
        que="Progresion de secciones del marco, fuera del piso de 0.90 m",
        formula="cruce de canal de riego -> el piso de 0.90 m NO aplica; la "
                "seccion se adopta 'de acuerdo a cada diseno particular'",
        formula_cita_id="MC_HHD.4.1.1.3.4a",
        citas_textuales=("MC_HHD.4.1.1.3.4a",),
        sustitucion=(
            Magnitud("escalones", len(progresion), "",
                     f"pares (B, H) que declara el criterio "
                     f"'{CRITERIO_SECCIONES_CAJON}', en el orden en que el "
                     f"bucle de diseno los recorre", cifras=None),),
        resultado=Magnitud(
            "progresion", " ; ".join(f"{B:.2f} x {H:.2f}" for B, H in progresion),
            "m", "serie adoptada de anchos por alturas interiores de UNA "
            "celda", cifras=None),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="adopcion, no verificacion"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="la progresion de secciones normalizadas del marco",
            valor=progresion,
            entre=("cualquier serie creciente de pares (B, H) que respete la "
                   "cota inferior de mantenimiento y quepa bajo la rasante",),
            de_donde="adopcion del proyectista",
            por_que="el num. 4.1.1.3.4 a) EXCEPTUA a los cruces de canal de "
                    "riego del piso de 0.90 m y los remite a 'cada diseno "
                    "particular': el numeral no libera la seccion, la "
                    "traslada del catalogo al diseno",
            cita_id="MC_HHD.4.1.1.3.4a",
            clave_criterio=CRITERIO_SECCIONES_CAJON),),
        nota_del_proyecto=(
            "El marco NO hereda el piso de 0.90 m, y no porque el proyecto "
            "decida saltarselo: lo levanta el mismo numeral que lo fija, en "
            "la misma oracion. Por eso esta progresion es un criterio "
            "declarado y no una lectura de la norma."),
    )

    mantenimiento = paso(
        "F3.MANTENIMIENTO",
        codigo="3.2",
        que="Cota inferior de la progresion: la seccion mas chica que se "
            "puede mantener",
        formula="dimensiones que permitan el mantenimiento y la limpieza en "
                "el interior del conducto -- exigencia SIN numero",
        formula_cita_id="MC_HHD.4.1.1.3.7d",
        citas_textuales=("MC_HHD.4.1.1.3.7d",),
        sustitucion=(
            Magnitud("B_min", menor[0], "m",
                     "ancho interior del escalon mas chico de la progresion "
                     "declarada", cifras=CIFRAS_FACTOR),
            Magnitud("H_min", menor[1], "m",
                     "altura interior del mismo escalon", cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("seccion minima", f"{menor[0]:.2f} x {menor[1]:.2f}",
                           "m", "la mas chica que el proyecto admite para "
                           "este cruce", cifras=None),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="adopcion, no verificacion"),
        nota_del_proyecto=(
            "Levantar el piso de 0.90 m NO deja la seccion sin cota inferior "
            "normativa. El num. 4.1.1.3.7 d) exige, sin distinguir forma "
            "alguna, que se pueda mantener y limpiar el conducto por dentro. "
            "Es una exigencia SIN NUMERO: obliga a que exista un minimo y "
            "deja al proyecto decir cual, que es exactamente la forma de un "
            "vacio declarable."),
    )

    n_celdas = paso(
        "F3.CELDAS",
        codigo="3.3",
        que="Numero de celdas del marco",
        formula="con capacidad de arrastre del curso: seccion transversal "
                "libre mayor, SIN subdivisiones",
        formula_cita_id="MC_HHD.4.1.1.3.4a#MULTIPLES",
        citas_textuales=("MC_HHD.4.1.1.3.4a#MULTIPLES",),
        sustitucion=(
            Magnitud("N", celdas, "celdas",
                     f"adoptado en el criterio '{CRITERIO_N_CELDAS_CAJON}'",
                     cifras=None),),
        resultado=Magnitud("Q por barril", f"Q / {celdas}", "m3/s",
                           "el caudal de diseno se reparte entre las celdas: "
                           "los coeficientes de HDS-5, el radio hidraulico y "
                           "el control de entrada son POR BARRIL",
                           cifras=None),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="adopcion, no verificacion"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="el numero de celdas del marco",
            valor=celdas,
            entre=("una celda -- lo que el numeral recomienda ante arrastre "
                   "de solidos", "multicelda, admisible y no recomendada por "
                   "defecto"),
            de_donde="adopcion del proyectista",
            por_que="el Manual RECOMIENDA obras de mayor seccion libre y sin "
                    "subdivisiones ante palizada, porque cada tabique es un "
                    "punto donde el arrastre se traba. No lo prohibe: invierte "
                    "la carga de la prueba",
            cita_id="MC_HHD.4.1.1.3.4a#MULTIPLES",
            clave_criterio=CRITERIO_N_CELDAS_CAJON),),
        nota_del_proyecto=(
            "La cita RECOMIENDA y no obliga, y por eso el numero de celdas es "
            "un criterio declarado. Lo que cambia con el no es solo la "
            "geometria: V6 (material solido de arrastre) pasa a depender de "
            "esta decision escrita en vez de depender de que el programa no "
            "supiera hacer multibarril."),
    )

    n_manning = paso(
        "F4.N_CAJON",
        codigo="4.1",
        que="Coeficiente de rugosidad de Manning del marco",
        formula="analogia DENTRO del grupo A de la Tabla N 09 -- conducto "
                "cerrado con escurrimiento parcialmente lleno --, que cubre "
                "al marco por su titulo y no tiene fila de seccion "
                "rectangular",
        formula_cita_id="MC_HHD.4.1.1.3.6",
        citas_textuales=("MC_HHD.4.1.1.3.6#T09",),
        sustitucion=(
            Magnitud("n_min", n_min, "",
                     f"extremo inferior de la fila adoptada: rama de EROSION",
                     cifras=CIFRAS_FINA),
            Magnitud("n_max", n_max, "",
                     f"extremo superior de la misma fila: rama de CAPACIDAD",
                     cifras=CIFRAS_FINA)),
        resultado=Magnitud("fila adoptada", TABLA_09_FILAS[fila]["fila"], "",
                           "la fila de la Tabla N 09 que se aplica al marco "
                           "por analogia declarada", cifras=None),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="adopcion, no verificacion"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="la fila de la Tabla N 09 que se aplica al marco",
            valor=fila,
            entre=("A.2 NO METALICOS - a. Concreto - afinado",
                   "A.2 NO METALICOS - a. Concreto - tubo recto y libre de "
                   "basuras"),
            de_donde="Tabla N 09, num. 4.1.1.3.6, grupo A",
            por_que="el vacio es de FILA y no de grupo: seis de las siete "
                    "subfilas de 'a. Concreto' dicen 'tubo' y la septima, "
                    "'afinado', no dice nada de forma. La analogia se queda "
                    "DENTRO del grupo que ya cubre al conducto cerrado, y por "
                    "eso es mas estrecha que la del HDPE, que cruza material",
            cita_id="MC_HHD.4.1.1.3.6#T09",
            clave_criterio=CRITERIO_N_MANNING_CAJON),),
        nota_del_proyecto=(
            f"El rango se toma COMPLETO -- {n_min} a {n_max} -- y no un valor "
            f"corriente: la regla de doble n pide los dos extremos, porque "
            f"n_max es conservador para capacidad y tirante y n_min para "
            f"velocidad y socavacion. Y la carta de HDS-5 que acompana a esta "
            f"decision es '{carta}', del bloque de CAJON de la Tabla A.1: el "
            f"num. A.3 prohibe cruzar coeficientes entre geometrias."),
    )

    return (tipo_marco, seccion_canal, mantenimiento, n_celdas, n_manning)


def _fila_manning(tipo: TipoMaterial, forma: FormaSeccion) -> str:
    """
    La fila LITERAL de la Tabla N 09 con que se resolvio el n, para el reporte.

    Tres casos y los tres se imprimen distinto, porque son tres situaciones
    normativas distintas: el material que TIENE fila; el que no esta en la
    tabla por ninguna parte (HDPE, analogia que cruza MATERIAL); y el marco,
    que esta cubierto por el TITULO de su grupo y no tiene fila propia
    -- analogia que se queda DENTRO del grupo, y por eso es mas estrecha --.
    """
    if forma is FormaSeccion.RECTANGULAR:
        return (f"{TABLA_09_FILAS[ca.valor(CRITERIO_N_MANNING_CAJON)]['fila']} "
                f"-- aplicada al MARCO por analogia declarada en el criterio "
                f"'{CRITERIO_N_MANNING_CAJON}': el grupo A de la tabla cubre "
                f"al cajon por su titulo y ninguna de sus filas nombra la "
                f"seccion rectangular")
    if tipo in _MANNING_CLAVE:
        return TABLA_09_FILAS[_MANNING_CLAVE[tipo]]["fila"]
    return (f"no listado en la Tabla N 09; analogia declarada en el "
            f"criterio '{CRITERIO_N_MANNING_HDPE}'")


# ---------------------------------------------------------------------------
# Filtro de candidatos
# ---------------------------------------------------------------------------

def materiales_candidatos(punto: PuntoCritico) -> Tuple[Material, ...]:
    """
    Materiales candidatos para el punto, ANTES de dimensionar (Sec. 3.2 +
    Sec. 3.4). No elige uno: entrega el catalogo completo de los que tienen
    sentido para la familia del punto.

    LA FAMILIA C YA NO DEVUELVE LA TUPLA VACIA, y es el cambio que abre C5.
    Devuelve UN candidato: el marco de concreto reforzado, que es la seccion
    que la Sec. 2.3 le asigna y la que la Lamina N 03 del Manual dibuja para
    este caso exacto -- un marco de concreto en cruce de canal de riego --.
    No devuelve tres: el TMC y el HDPE son productos de seccion circular y no
    hay catalogo de marco en ninguno de los dos.

    OJO CON LO QUE ESO SIGNIFICA HOY: el candidato existe y NO se puede
    construir todavia, porque sus criterios estan sin declarar. La llamada se
    detiene con `CriterioPendienteError` en el primero que falte, que es lo
    que tiene que pasar -- y es una detencion distinta de la de antes: antes
    el programa decia "no hay material", que era una afirmacion sobre el
    CATALOGO, y ahora dice "falta declarar la embocadura del marco", que es
    una afirmacion sobre el EXPEDIENTE. Ver "El marco de la Familia C" en el
    docstring del modulo.
    """
    if punto.familia is Familia.C:
        return (catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR),)
    return tuple(catalogo(tipo) for tipo in TipoMaterial)
