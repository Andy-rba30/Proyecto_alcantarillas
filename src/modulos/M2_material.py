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
                     retiro de alli: los topes de 2.70 / 2.10 / 1.50 m no
                     salian de las normas de producto a las que se les
                     atribuian (A760 tabula hasta 3600 mm, M 170M tambien --
                     NOR-PRO-01, NOR-PRO-02, MAT-O8). DESDE T-4 (INF-3.3.1)
                     el tope es el de la norma de producto
                     ('D_max_norma_producto' [C]: 2.70 / 3.60 / 1.50 m; en
                     el concreto, el mayor diametro con DISEÑO ESTANDAR de
                     M 170M --su serie sigue hasta 3600 mm como diseño
                     especial, sin pared tabulada--; en el TMC, acotado a
                     los diametros en que la corrugacion adoptada es
                     estandar), y la disponibilidad de mercado
                     ('D_max_catalogo' [A], opcional y sin valor) solo puede
                     BAJARLO. Lo resuelve `tope_de_diametro`, y
                     `Material.D_max_criterio` dice de cual de los dos salio
                     para que la memoria no llame «de catalogo» a un tope de
                     norma ni al reves.
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
                     Es lo que le faltaba al catalogo para que la clave
                     fisica y el volumen desplazado no se calculasen con el
                     diametro interior (MAT-D3, MAT-D4). DESDE T-4
                     (INF-5.1.17) los TRES materiales lo tienen: el concreto
                     y el HDPE del criterio 'espesor_pared_conducto' [A]
                     (pared B de M 170M; diametro exterior maximo de AASHTO
                     LRFD Table A12-11) y el TMC DERIVADO de
                     'corrugacion_y_espesor_tmc' [A] por
                     `espesor_pared_de_tmc` (profundidad de corrugacion mas
                     espesor de plancha). Hasta T-4 solo lo tenia el
                     concreto, y los otros dos se descartaban antes de 7.A y
                     de V7.

Campos que el catalogo puede dejar en None, a proposito
--------------------------------------------------------
Cuatro criterios alimentan campos que `Material` declara `Optional`:
'n_manning_hdpe', 'v_max_tmc', 'v_max_hdpe' y 'espesor_pared_conducto'.

ESTADO HOY (T-4): los cuatro tienen valor. 'v_max_tmc' = 4.572 m/s [A] y
'v_max_hdpe' = 4.572 m/s [C] (el corte de 15 ft/s entre los niveles de
abrasion moderado y severo de la Tabla 8-4 de WSDOT; para el termoplastico
el §8-3.3 lo prohibe en el nivel severo, para el metal ninguna fuente fija
techo); 'n_manning_hdpe' = (0.009, 0.015) [C], la fila del polietileno de
interior liso de la Table B.1 del HDS-5; 'espesor_pared_conducto' = la pared
B del concreto y el t del HDPE [A]. El mecanismo de abajo se conserva para
quien vacie alguno: el bloqueo salta en el punto de uso
(`M5_verificaciones.cota_clave` y V7 para el espesor).
ESTE BLOQUE DECIA «los tres primeros tienen valor y el cuarto no» y que el
n del HDPE era «la fila del concreto de la Tabla N 09 [N->]».

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
salta despues, en el punto de uso (`Seccion.ancho_exterior` para el
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
Progresion 0.90 m + pasos de 0.15 m, topada por material (desde T-4, por
la serie de la norma de producto: ver `tope_de_diametro`). El 0.90 sale del
num. 4.1.1.3.4 a) y NO es un piso incondicional: el numeral lo escribe "en
carreteras de alto volumen de transito" -- condicion que este proyecto no puede
afirmar, porque la clase de via depende del IMDA -- y exceptua expresamente los
cruces de canal de riego, que es la Familia C (ver "Familia C queda sin
candidatos", mas abajo, y `constantes_normativas.DIAMETRO_MIN_AMBITO`).
Aplicarlo igual a las Familias A y B es una adopcion declarada, y su direccion
NO es uniformemente conservadora: mas diametro da mas borde libre (favorable a
V1) y menos velocidad (desfavorable al piso de V2). Los dos numeros de la progresion viven en el criterio
'diametros_normalizados' [C]; los tres topes, en 'D_max_norma_producto' [C]
desde T-4. ESTE PARRAFO DECIA que los topes vivian en 'D_max_catalogo' [A] y
que «NO salen de ninguna norma»: era cierto de los 2.70 / 2.10 / 1.50 m que
el proyecto aplicaba (NOR-PRO-01, NOR-PRO-02) y deja de serlo al sustituirlos
por el ultimo diametro que cada norma de producto cubre con un producto
definido (en concreto, 2.70 m: el ultimo con diseño estandar). Que no
se usen catalogos de proveedor para la PROGRESION ni para el tope es lo que
preserva la neutralidad comercial en obra publica; lo que se consigue en el
mercado es otra pregunta, la contesta el proyectista en 'D_max_catalogo'
[A] -- opcional, y solo para BAJAR el tope -- y el descarte que produzca se
imprime como de disponibilidad, no como exigencia.

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
su velocidad maxima es el criterio 'v_max_tmc' [A]. HDPE no esta en ninguna de
las dos tablas del Manual MTC: su n sale del criterio 'n_manning_hdpe' ([C],
la fila del polietileno de interior liso de la Table B.1 del HDS-5; hasta T-4
era la subfila del concreto por analogia) y su velocidad maxima del criterio
'v_max_hdpe' [C].

LA MATRIZ DE DURABILIDAD ES UN FILTRO REAL DESDE T-4 (INF-3.3.1; v8 §3.3).
`matriz_durabilidad(punto, ensayos)` recibe los ensayos del punto --pH,
resistividad, sulfatos, cloruros y nivel de abrasion: datos del EMS y del
estudio de campo, todos opcionales y sin valor por defecto-- y devuelve un
`DictamenDurabilidad` con lo que cada uno hace a cada material: EXCLUYE (el
TMC fuera del intervalo de pH o bajo el piso de resistividad; el HDPE en
abrasion severa), EXIGE (cemento y relacion a/c del concreto por sulfatos;
proteccion del TMC con agua de pH menor de 5.8) o AVISA (cloruros, abrasion
del metal y del concreto, suelo de fundacion deficiente).
`materiales_candidatos(punto, durabilidad=...)` retira los excluidos. SIN
ENSAYOS LA MATRIZ NO ACTUA: los candidatos son los de la familia y el
dictamen lo dice (`modelos.DURABILIDAD_SIN_ENSAYOS`). Lo que M2 SIGUE sin
hacer es elegir: el orden de los candidatos no cambia y MD adopta el primero
que cierra.

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
    from src.modulos.M2_material import (catalogo, materiales_candidatos,
                                     siguiente_seccion)

    candidatos = materiales_candidatos(punto)   # el marco, en Familia C
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                     forma=FormaSeccion.RECTANGULAR)     # bloquea sin declarar
    seccion = siguiente_seccion(concreto)                # Ø 0.90 m
    seccion = siguiente_seccion(concreto, seccion)       # Ø 1.05 m
"""

from __future__ import annotations

import math
import numbers
from typing import Any, Optional, Tuple, Union

from src import criterios_adoptados as ca
from src.constantes_normativas import (ALCANCE_NORMA_PRODUCTO, CARTAS_CAJON_TA1,
                                   FILAS_MANNING_CONCRETO,HDS5_INLET, H_RELLENO_MIN, MANNING,
                                   SECCION_EG2013,
                                   SECCION_EG2013_CAJON,
                                   TABLA_09_FILAS, V_MAX)
# --- T-4 --- las vistas del TMC, de la abrasion y del SUCS, y el [N] del pH.
from src.constantes_normativas import (DIAMETROS_ESTANDAR_TMC,
                                   EXPOSICION_ESPECIAL,
                                   NIVEL_DE_ABRASION_SEVERO,
                                   NIVELES_DE_ABRASION,
                                   NUMERAL_PH_MIN_TMC,
                                   PH_MIN_AGUA_TMC_SIN_PROTECCION,
                                   SIMBOLOS_SUCS, SULFATOS,
                                   TMC_PLANCHA_CORRUGADA)
from src.dominios import MILIMETROS_POR_METRO, PPM_POR_PORCIENTO
from src.modelos import (CIFRAS_FACTOR, CIFRAS_FINA, ConstantesHDS5,
                     DatoFaltanteError, DatoInvalidoError,
                     DictamenDurabilidad, EfectoDeDurabilidad,
                     EleccionDeProyecto, EnsayosDurabilidad,
                     Familia, FormaSeccion, Magnitud,
                     Material, PasoDeMemoria, PuntoCritico,
                     ReglaDeDurabilidad, Seccion,
                     SeccionCircular, SeccionRectangular, TipoDeVeredicto,
                     TipoMaterial, Umbral, Veredicto, paso)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

NUMERAL_CATALOGO = "Sec. 3.2"     # nuevo en v7, sin numeral MTC propio
NUMERAL_MATERIAL = "Sec. 3.4"

CRITERIO_DIAMETROS = "diametros_normalizados"
CRITERIO_D_MAX_CATALOGO = "D_max_catalogo"
CRITERIO_ESPESOR_PARED = "espesor_pared_conducto"
# --- T-4 --- los cuatro criterios que T-4 abre y que lee este modulo.
CRITERIO_D_MAX_NORMA = "D_max_norma_producto"
CRITERIO_CALIBRE_TMC = "corrugacion_y_espesor_tmc"
CRITERIO_DURABILIDAD_TMC = "durabilidad_tmc_umbrales"
CRITERIO_SUCS_DEFICIENTE = "sucs_fundacion_deficiente"
# El del MARCO es otro criterio y no una entrada mas del de arriba: aquel
# es una TABLA por diametro designado de tuberia y este un ESCALAR
# adoptado. Meterlos en el mismo dict obligaria a que el marco tuviera un
# "diametro designado", que es justo lo que no tiene.
CRITERIO_ESPESOR_PARED_CAJON = "espesor_pared_cajon"
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
#
# La de HDPE lleva la edicion que el ejemplar de normas/ declara (M 294-11)
# Y SU NATURALEZA: lo que hay en el repositorio es una TRADUCCION NO OFICIAL
# (N2; `normativa.fuentes.AASHTO_M294_TRAD`, con el original en ingles todavia
# en el censo de ausentes). La regla de esa fuente es que las palabras
# «traduccion no oficial» acompañen a toda cita suya, y este rotulo llega a
# la memoria como norma de producto del material: es una cita.
_NORMA_PRODUCTO = {
    TipoMaterial.CONCRETO_REFORZADO: "AASHTO M 170M-04 / ASTM C 76M-02 (metrica)",
    TipoMaterial.TMC: "AASHTO M 36 / ASTM A760/A760M-10",
    TipoMaterial.HDPE: "AASHTO M 294-11 (en normas/: traduccion no oficial)",
}

# Y VA POR (MATERIAL, FORMA) DESDE EXT-6, no solo por material (EXT-N-03).
# Las tres de arriba cubren TUBERIA: lo dice la clausula de alcance de cada
# una (M 170M 1.1 «reinforced concrete pipe»; M 36 1.1 y A760 1.1 «corrugated
# steel pipe»; M 294 1.1.1), transcrita en el registro desde EXT-6. Un marco
# rectangular vaciado in situ no es tuberia, y hasta EXT-6 salia rotulado
# con AASHTO M 170M-04 --- en la memoria, en el JSON, en el CSV de resumen y
# en el motivo de descarte cuando agotaba su serie ---. La norma de producto
# del cajon PREFABRICADO seria AASHTO M 259 / M 273 (AASHTO LRFD 12.4.2.4,
# pag. 12-8; 12.11.1, pag. 12-68), ausentes de normas/, y el proyecto decidio
# el marco vaciado in situ justamente por eso (docs/ruta_familia_c.md §14.1):
# se DISEÑA por AASHTO LRFD Seccion 5 y Art. 12.11 y se CONSTRUYE por EG-2013
# Secciones 503 (concreto estructural) y 504 (acero de refuerzo). El rotulo
# lo dice con esas palabras en vez de dejar la casilla vacia o poner la norma
# de otro producto.
_NORMA_PRODUCTO_MARCO = (
    "sin norma de producto: marco vaciado in situ (ruta_familia_c §14.1); "
    "diseño AASHTO LRFD Sec. 5 y Art. 12.11; construccion EG-2013 503+504; "
    "M 259/M 273 ausentes")

# El ALCANCE de cada rotulo, anclado en el registro: las citas que dicen que
# cubre cada norma, y para el marco las dos de AASHTO LRFD que dicen por que
# no la hay. `test_ext6_registro_normativo` exige que existan.
CITA_ALCANCE_NORMA_PRODUCTO = {
    (TipoMaterial.CONCRETO_REFORZADO, FormaSeccion.CIRCULAR):
        ("AASHTO_M170M.1.1", "AASHTO_M170M.1.1#NOTA1"),
    (TipoMaterial.TMC, FormaSeccion.CIRCULAR):
        ("AASHTO_M36.1.1", "ASTM_A760.1.1"),
    (TipoMaterial.HDPE, FormaSeccion.CIRCULAR):
        ("AASHTO_M294_TRAD.1.1.1",),
    (TipoMaterial.CONCRETO_REFORZADO, FormaSeccion.RECTANGULAR):
        ("AASHTO_LRFD_9.12.4.2.4", "AASHTO_LRFD_9.12.11.1"),
}


def norma_producto_de(tipo: TipoMaterial, forma: FormaSeccion) -> str:
    """
    El rotulo de norma de producto de un (material, forma): la norma del
    tubo para la seccion circular; para la rectangular, la constancia
    explicita de que no la hay (EXT-N-03). Un marco de TMC o de HDPE no
    existe en el catalogo (`materiales_candidatos`), y por eso la unica
    combinacion rectangular es la del concreto.
    """
    if forma is FormaSeccion.RECTANGULAR:
        if tipo is not TipoMaterial.CONCRETO_REFORZADO:
            raise DatoInvalidoError(
                "forma", tipo.value,
                detalle=("el catalogo de la Sec. 3.2 no ofrece marco "
                         "rectangular de ese material: el marco es de "
                         "concreto reforzado (Lamina N 03)"))
        return _NORMA_PRODUCTO_MARCO
    return _NORMA_PRODUCTO[tipo]


def alcance_norma_producto_de(tipo: TipoMaterial, forma: FormaSeccion) -> str:
    """
    El alcance de la norma de producto, como texto del registro
    (`constantes_normativas.ALCANCE_NORMA_PRODUCTO`): lo que cada norma dice
    cubrir en su clausula 1.1, o por que el marco no tiene norma. Lo exporta
    `cli._diseno_json` como `alcance_norma_producto`.
    """
    clave = "marco" if forma is FormaSeccion.RECTANGULAR else tipo.value
    return ALCANCE_NORMA_PRODUCTO[clave]

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


# --- T-4 --- El rotulo con que se imprime el tope cuando sale de la SERIE
# de la norma de producto. Es lo contrario del rotulo de `de_catalogo`: aqui
# el tope SI es el de la norma, y decirlo importa tanto como importaba no
# decirlo cuando no lo era (NOR-PRO-01, NOR-PRO-02).
ROTULO_TOPE_DE_SERIE = (
    "TOPE DE LA NORMA DE PRODUCTO: mayor diametro que la norma de producto "
    "cubre para este material (criterio "
    f"'{CRITERIO_D_MAX_NORMA}' [C]); en tuberia de concreto, el mayor con "
    "diseño estandar tabulado: por encima es diseño especial del "
    "fabricante. No es un dato de mercado: que el "
    "producto se consiga en la obra se declara aparte, en "
    f"'{CRITERIO_D_MAX_CATALOGO}' [A], y solo puede bajarlo")
ROTULO_TOPE_DE_CORRUGACION = (
    "TOPE DE LA CORRUGACION ADOPTADA: mayor diametro en que la corrugacion "
    f"de '{CRITERIO_CALIBRE_TMC}' [A] es estandar en la Table 6 de AASHTO "
    "M 36 (igual a la Tabla 1 de ASTM A760). La serie de la norma llega mas "
    "lejos con las corrugaciones de 25 mm de profundidad: superarlo se "
    "resuelve declarando otra corrugacion, no otro material. ES EL TOPE DE "
    "LA CORRUGACION Y NO EL DE LA PLANCHA: que el espesor adoptado resista "
    "y cumpla el factor de flexibilidad de ASTM A796 en cada diametro lo "
    "verifica la Fase 8, no este catalogo")


def tope_de_diametro(material: MaterialLike) -> Tuple[float, str, str]:
    """
    El diametro maximo que el catalogo recorre para ese material, m, con la
    CLAVE del criterio que lo fija y el ROTULO con que hay que imprimirlo
    (Sec. 3.2; INF-3.3.1).

        tope = min( serie de la norma de producto ,
                    [TMC] mayor diametro estandar de la corrugacion adoptada ,
                    [si se declara] disponibilidad de mercado )

    DE DONDE SALE CADA TERMINO:

      * la norma: 'D_max_norma_producto' [C]. En TMC y HDPE, la ultima fila
        de AASHTO M 36 Table 6 (3600 mm) y de AASHTO M 294-11 num. 7.2.2
        (1500 mm, traduccion no oficial). En CONCRETO, 2700 mm: el mayor
        diametro con diseño estandar de AASHTO M 170M-04 (Tablas 1 y 3). Su
        serie sigue hasta 3600 mm, pero esas filas llevan rayas y remiten a
        la Seccion 7.2: son diseños especiales cuya pared da el fabricante
        (`constantes_normativas.DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM`);
      * la corrugacion: AASHTO M 36 Table 6 marca con «X» en que diametros es
        estandar cada una; con la de 68 por 13 mm el ultimo es 2100 mm
        (`constantes_normativas.DIAMETROS_ESTANDAR_TMC`);
      * la disponibilidad: 'D_max_catalogo' [A], OPCIONAL y sin valor. Solo
        puede BAJAR el tope: un valor por encima del de la serie se rechaza
        con `DatoInvalidoError`, porque un diametro que la norma de producto
        no tabula no es un producto que un catalogo pueda ofrecer bajo ella.

    HASTA T-4 el tope eran 2.70 / 2.10 / 1.50 m de 'D_max_catalogo', [A] sin
    respaldo en concreto y TMC. El 2.10 m del TMC y el 1.50 m del HDPE NO se
    mueven --ahora tienen de donde salir--. El del concreto TAMPOCO: una
    primera version de T-4 lo llevo a 3.60 m, la ultima fila de la serie, y
    la auditoria lo refuto contra la fuente (H2): por encima de 2700 mm la
    norma no tabula pared ni acero. Sigue en 2.70 m, ahora con fuente y
    pagina.

    Y EL TOPE NO DICE QUE EL PRODUCTO SIRVA ESTRUCTURALMENTE HASTA AHI. El
    2.10 m del TMC es el de la CORRUGACION (Table 6 de M 36), no el de la
    plancha: con 68 por 13 mm y 2.01 mm el factor de flexibilidad de ASTM
    A796 deja de cumplirse mucho antes. Eso lo comprueba la Fase 8, no este
    catalogo (ver el rotulo `ROTULO_TOPE_DE_CORRUGACION`).
    """
    tipo = _tipo_material(material)
    serie = ca.valor(CRITERIO_D_MAX_NORMA)
    if not isinstance(serie, dict) or tipo.value not in serie:
        raise DatoInvalidoError(
            campo=CRITERIO_D_MAX_NORMA, valor=serie,
            motivo=f"el criterio no trae el tope de la serie de "
                   f"«{tipo.value}». Es un dict por material con el diametro "
                   "maximo en METROS")
    tope = _espesor_valido(CRITERIO_D_MAX_NORMA, serie[tipo.value],
                           que_es=f"el tope de la serie de «{tipo.value}» es "
                                  "un diametro en METROS")
    clave, rotulo = CRITERIO_D_MAX_NORMA, ROTULO_TOPE_DE_SERIE

    if tipo is TipoMaterial.TMC:
        estandar = max(_diametros_estandar_de_la_corrugacion()) \
            / MILIMETROS_POR_METRO
        if estandar < tope - TOL_UMBRAL_NORMATIVO:
            tope, clave, rotulo = (estandar, CRITERIO_CALIBRE_TMC,
                                   ROTULO_TOPE_DE_CORRUGACION)

    local = _valor_si_declarado(CRITERIO_D_MAX_CATALOGO)
    if local is not None:
        if not isinstance(local, dict):
            raise DatoInvalidoError(
                campo=CRITERIO_D_MAX_CATALOGO, valor=local,
                motivo="la disponibilidad de mercado se declara como un dict "
                       "por material, con el diametro maximo en METROS: "
                       "{'concreto_reforzado': 2.40, 'tmc': 1.80}")
        if tipo.value in local:
            disponible = _espesor_valido(
                CRITERIO_D_MAX_CATALOGO, local[tipo.value],
                que_es=f"el tope de disponibilidad de «{tipo.value}» es un "
                       "diametro en METROS")
            if disponible > tope + TOL_UMBRAL_NORMATIVO:
                raise DatoInvalidoError(
                    campo=CRITERIO_D_MAX_CATALOGO, valor=disponible,
                    motivo=f"la disponibilidad de mercado declarada para "
                           f"«{tipo.value}» ({disponible} m) supera el tope "
                           f"que la norma de producto da ({tope} m, criterio "
                           f"'{clave}'). Este criterio solo puede BAJAR el "
                           "tope: un diametro que la norma no tabula no es "
                           "un producto de catalogo bajo esa norma")
            if disponible < tope - TOL_UMBRAL_NORMATIVO:
                tope, clave = disponible, CRITERIO_D_MAX_CATALOGO
                rotulo = ca.criterio(CRITERIO_D_MAX_CATALOGO).de_catalogo
    return tope, clave, rotulo


def _calibre_de_tmc() -> dict:
    """
    La fila de `TMC_PLANCHA_CORRUGADA` que 'corrugacion_y_espesor_tmc' elige.
    Una clave que no es fila de la vista es `DatoInvalidoError`: la puerta de
    declaracion ya la rechaza (forma `categoria`), y esta es la segunda linea
    para quien la esquive.
    """
    clave = ca.valor(CRITERIO_CALIBRE_TMC)
    if clave not in TMC_PLANCHA_CORRUGADA:
        raise DatoInvalidoError(
            campo=CRITERIO_CALIBRE_TMC, valor=clave,
            motivo="tiene que ser una de las claves 'corrugacion/espesor' de "
                   "las Tablas 5, 7 y 9 de ASTM A796: "
                   f"{', '.join(TMC_PLANCHA_CORRUGADA)}")
    return TMC_PLANCHA_CORRUGADA[clave]


def _diametros_estandar_de_la_corrugacion() -> Tuple[int, ...]:
    """Los diametros (mm) en que la corrugacion adoptada es estandar."""
    return DIAMETROS_ESTANDAR_TMC[_calibre_de_tmc()["corrugacion"]]


def espesor_pared_de_tmc() -> dict:
    """
    El «espesor de pared» de la tuberia metalica corrugada, por diametro
    designado: {mm: t en metros}, con

        t = profundidad nominal de la corrugacion + espesor de la plancha

    para los diametros en que la corrugacion adoptada es ESTANDAR (AASHTO
    M 36 Table 6). Es lo que separa el diametro interior del exterior:
    D_ext = D + 2t.

    POR QUE ES UNA SUMA, que la norma no escribe: AASHTO M 36 num. 8.1.1 mide
    el diametro nominal en la cresta INTERIOR de las corrugaciones (cita
    AASHTO_M36.8.1.1) y la nota b de su Table 1 define la profundidad de
    cresta a valle sobre una misma cara de la plancha (cita AASHTO_M36.T1),
    de modo que la cresta exterior queda a profundidad + espesor de la
    interior. Es geometria del proyecto sobre dos definiciones de la fuente,
    declarada como `Interpretacion` de la tabla AASHTO_M36.T1.

    Con la adopcion de perfil (68 por 13 mm, plancha de 2.01 mm) da
    0.013 + 0.00201 = 0.01501 m en todo diametro de 300 a 2100 mm. El
    espesor NO depende del diametro; lo que depende es EN CUALES existe.

    Un diametro fuera de los estandar no lleva fila, y `espesor_pared`
    detiene ahi el material con `DatoFaltanteError`.
    """
    calibre = _calibre_de_tmc()
    t = calibre["profundidad_m"] + calibre["espesor_m"]
    return {mm: t for mm in DIAMETROS_ESTANDAR_TMC[calibre["corrugacion"]]}


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
      concreto sale de una tabla que esta en `normas/` y el del HDPE no lo
      trae su norma de producto -- AASHTO M 294-11, en normas/ desde N2 como
      traduccion no oficial, tabula el espesor minimo de la pared interior y
      no la altura del perfil --. El revisor tiene que AÑADIR la entrada de ese
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
    la pared del tubo de 1500 mm, y con ella la geometria exterior daba a V7
    un cilindro de 1.80 m. Medido sobre esa seccion: la subpresion real de un
    prisma es 40.6 kN/m y la del cilindro 25.0 kN/m -- un 63 % menos --,
    mientras el peso de relleno cae solo un 28 %, de modo que V7 SOBREESTIMA
    la seguridad del marco alrededor de un 27 %. Es la direccion insegura, y
    es MAT-D3 reintroducido para el cajon.

    El docstring de `M5.v7_flotacion` que C5 escribio decia que «un marco
    vaciado in situ no tiene fila ahi». La frase era verdadera sobre la NORMA
    y falsa sobre el DICT, que es lo que el codigo lee, y una declaracion en
    un docstring no detiene ningun calculo. Por eso la deteccion esta aqui.

    Y EL QUINTO VACIO CAMBIA DE EXCEPCION EN C7, que no es un detalle de
    forma. C5 lo detuvo con `DatoFaltanteError` -- «hay que CONSEGUIR el
    dato» -- y era la lectura correcta mientras el proyecto no tuviera donde
    ponerlo. Ahora lo tiene: `espesor_pared_cajon`, [A] de nivel perfil. Con
    eso el revisor ya no tiene que CONSEGUIR nada, tiene que DECIDIR, y esa es
    exactamente la frontera que CLAUDE.md fija entre las dos excepciones. La
    detencion pasa a `CriterioPendienteError`, que es la que la GUI muestra
    como pendiente declarable con su ventana y su procedencia -- y este
    criterio tiene una ventana que hay que leer, porque su sensibilidad va en
    el sentido contrario al que todo el mundo supone.

    LO QUE NO CAMBIA es que se detiene, ni por que: leerle al marco la fila
    del tubo de la misma altura da un cilindro, y V7 sobreestima la seguridad
    alrededor de un 27 % sobre un marco de 2.00 x 1.50 m. La coincidencia de
    series -- 900 + 150k mm -- sigue siendo la trampa.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        # `ca.valor` levanta CriterioPendienteError mientras siga sin valor, y
        # ese es el camino normal hoy. Si se declara, devuelve el espesor
        # adoptado: un escalar en metros, no una tabla por diametro -- un
        # marco vaciado in situ no tiene serie de producto que indexar.
        return _espesor_valido(
            CRITERIO_ESPESOR_PARED_CAJON, ca.valor(CRITERIO_ESPESOR_PARED_CAJON),
            que_es="el espesor de pared de un marco es UN escalar en metros, "
                   "no una tabla por diametro: un marco vaciado in situ no "
                   "tiene serie de producto que indexar")
    if material.espesor_pared is None:
        ca.valor(CRITERIO_ESPESOR_PARED)      # CriterioPendienteError si esta vacio
        raise DatoFaltanteError(
            f"{CRITERIO_ESPESOR_PARED}[{material.tipo.value}]",
            detalle=(
                f"el criterio '{CRITERIO_ESPESOR_PARED}' esta declarado, pero "
                f"no trae entrada para «{material.tipo.value}». Es un dict "
                "por material y cada entrada necesita su propia fuente: la "
                "del concreto es la columna 'Wall Thickness' de las Tablas 1 "
                "a 5 de AASHTO M 170M-04, la del HDPE el diametro exterior "
                "maximo de la Table A12-11 de AASHTO LRFD (su norma de "
                "producto, AASHTO M 294-11 -- en normas/ como traduccion no "
                "oficial --, no fija el diametro exterior) y la del TMC se "
                f"deriva de '{CRITERIO_CALIBRE_TMC}' cuando no se declara. "
                "Sin espesor no hay diametro exterior, y sin diametro "
                "exterior no hay clave fisica (7.A) ni volumen desplazado "
                "(V7)"
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
                f"{sorted(por_diametro)}. Falta esa fila en su fuente "
                f"({_FUENTE_DEL_ESPESOR[material.tipo]}): no se "
                "interpola ni se toma la fila vecina, porque el espesor "
                "gobierna la clave fisica (7.A) y el volumen desplazado de V7 "
                "y los dos quedan del lado inseguro si se estima por lo bajo"
            ),
        )
    return _espesor_valido(
        CRITERIO_ESPESOR_PARED, por_diametro[designado],
        que_es=f"el espesor declarado para '{material.tipo.value}' en el "
               f"diametro {designado} mm es una celda de la columna 'Wall "
               f"Thickness', en METROS")


# --- T-4 --- De donde sale la tabla de espesores de cada material, para el
# mensaje de la fila que falta. Hasta T-4 el mensaje decia «la columna 'Wall
# Thickness' de la norma de producto» para los tres, que solo es cierto del
# concreto.
_FUENTE_DEL_ESPESOR = {
    TipoMaterial.CONCRETO_REFORZADO: (
        "columna 'Wall Thickness' de la pared B de AASHTO M 170M-04, de "
        "900 a 2700 mm, que es el ultimo diametro con diseño estandar: por "
        "encima la norma no tabula pared (diseño especial, Seccion 7.2) y "
        "la da el fabricante"),
    TipoMaterial.TMC: (
        f"'{CRITERIO_CALIBRE_TMC}': la corrugacion adoptada no es estandar "
        "en ese diametro segun la Table 6 de AASHTO M 36; se resuelve "
        "declarando otra corrugacion"),
    TipoMaterial.HDPE: (
        "columna 'Max. OD' de la Table A12-11 de AASHTO LRFD, que termina "
        "en 48 in (1200 mm); para 1350 y 1500 mm hace falta el diametro "
        "exterior de la ficha del fabricante"),
}


def procedencia_del_espesor(material: Material) -> Tuple[str, str, str]:
    """
    De donde sale el espesor de pared de ese material: (texto para la
    memoria, id de la cita del registro o cadena vacia, clave del criterio).

    Existe para que V7 --que es donde el espesor entra en un numero que se
    juzga-- pueda decir en su paso de donde salio t, en vez de dejar al
    revisor buscandolo en la ficha de un criterio que es un dict de dicts.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        return ("espesor de pared del marco, escalar declarado por el "
                "proyectista", "", CRITERIO_ESPESOR_PARED_CAJON)
    declarados = _valor_si_declarado(CRITERIO_ESPESOR_PARED) or {}
    if material.tipo is TipoMaterial.TMC and \
            material.tipo.value not in declarados:
        calibre = ca.valor(CRITERIO_CALIBRE_TMC)
        return (f"profundidad de la corrugacion mas espesor de la plancha "
                f"de la fila '{calibre}' (AASHTO M 36 Table 1 y num. 8.1.1; "
                f"ASTM A796)", "AASHTO_M36.T1", CRITERIO_CALIBRE_TMC)
    if material.tipo is TipoMaterial.HDPE:
        return ("el t que lleva el diametro designado hasta el diametro "
                "exterior maximo de la Table A12-11 de AASHTO LRFD, o el "
                "que el proyectista declare en su lugar",
                "AASHTO_LRFD_9.TA12-11", CRITERIO_ESPESOR_PARED)
    return (f"tabla declarada en '{CRITERIO_ESPESOR_PARED}' para "
            f"'{material.tipo.value}' (concreto: pared B de AASHTO "
            "M 170M-04)", "", CRITERIO_ESPESOR_PARED)


def _espesor_valido(campo: str, t: Any, *, que_es: str) -> float:
    """
    UN validador para las DOS ramas de `espesor_pared` (EXT-V-03).

    Hasta EXT-1 cada rama tenia su propio `isinstance`, y divergian: la
    rectangular exigia Real-no-bool y `t > 0`; la circular solo
    `numbers.Real`. Medido por la auditoria externa sobre la rama circular:
    `True` daba una pared de 1.0 m (D_ext 2.9 m, cota de clave 44.0), `0` se
    devolvia como `int`, y -0.1 e inf entraban a la clave fisica (7.A) y al
    volumen desplazado de V7. El predicado correcto ya existia
    (`criterios_adoptados._es_real`); la duplicacion era la causa.

    Forma MAT-D13: Real y no bool, finito, y la condicion de signo escrita EN
    POSITIVO Y NEGADA (`not t > 0`), porque un NaN es falso frente a `<=`
    igual que frente a `>`. Devuelve SIEMPRE `float(t)`: el espesor entra en
    aritmetica con las cotas y un `int` disfrazado no es el mismo dato.
    """
    if not ca._es_real(t):
        raise DatoInvalidoError(
            campo=campo, valor=t,
            motivo=f"{que_es}. Lo declarado ({t!r}) no es un numero real -- "
                   "un texto, un bool o una tabla no son un espesor")
    if not math.isfinite(t):
        raise DatoInvalidoError(
            campo=campo, valor=t,
            motivo=f"{que_es}. Lo declarado ({t!r}) no es finito: un espesor "
                   "infinito o NaN no es una pared, y seguiria hasta la cota "
                   "de clave y el volumen desplazado de V7")
    if not t > 0:
        raise DatoInvalidoError(
            campo=campo, valor=t,
            motivo=f"{que_es}. El espesor de pared tiene que ser positivo; "
                   f"lo declarado es {t!r}. La condicion se escribe negada "
                   "(`not t > 0`) para que un NaN caiga del lado seguro, "
                   "como en MAT-D13")
    return float(t)


# `diametro_exterior(*, material, D) -> D + 2*t` VIVIA AQUI Y C8 LO RETIRA.
#
# Hacia lo que su nombre dice y era correcto mientras el unico conducto fuera
# un tubo. Lo que lo mato fue la Familia C: en un marco NO HAY UN "diametro
# exterior" --- hay un ancho exterior `Bc = B + 2t` y un canto exterior
# `B'c = H + 2t`, que son numeros distintos ---, y una funcion que recibe un
# escalar solo puede devolver uno de los dos. C5 la uso para el `Bc` de la
# cobertura minima y le entrego el CANTO donde iba el ANCHO, que es el defecto
# que la regla vinculante #9 arrastro dos veces (ver el docstring de
# `M7.cobertura_minima_aashto`).
#
# C7 puso en su lugar los tres miembros del protocolo `Seccion` ---
# `ancho_exterior(espesor)`, `canto_exterior(espesor)` y
# `area_exterior(espesor)` ---, que dan cada dimension por su nombre y en las
# dos formas. Desde entonces esta funcion no tenia NINGUNA llamada: medido
# sobre el AST de M7, M5, M8, MD, la CLI y este mismo modulo, y tampoco en
# tests. Seguia importada en dos modulos y citada en cinco docstrings, que es
# como un simbolo muerto sobrevive a la revision --- se lee como si alguien lo
# usara.
#
# No va a `decisiones_diferidas.md`: ahi viven los objetos que se CONSERVAN
# sin consumidor por una razon, y esta no tiene ninguna --- su contrato es
# insuficiente para la mitad de las secciones del proyecto.


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
    tope, _clave, _rotulo = tope_de_diametro(tipo)

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
        `KeyError` desnudo, que no desciende de `ErrorProyecto`: `servicio._etapa`
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
    debajo del orquestador: `M4.caudal_por_celda`, que reparte el caudal
    (desde EXT-2; `MD._caudal_por_barril` es su alias), y
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
    if not pares or any(not (B > 0 and H > 0) for B, H in pares):
        raise forma_mala
    _exigir_sin_repetidos(pares)
    return pares


def _exigir_sin_repetidos(pares: tuple) -> None:
    """
    Ningun par (B, H) puede coincidir con uno anterior dentro de
    TOL_UMBRAL_NORMATIVO (EXT-A-03).

    Con un escalon repetido `_siguiente_seccion_cajon` encuentra SIEMPRE la
    primera aparicion y devuelve el mismo siguiente, y el bucle de MD no
    termina: la auditoria externa vio «cinco visitas» porque aborto; medido
    sin abortar son 50 escalones en 0.00 s y ningun `ErrorProyecto`. Vale
    para el duplicado ADYACENTE, para el NO adyacente (ciclo de longitud 2) y
    para el CASI duplicado -- 5e-10 de diferencia --, porque la igualdad que
    el bucle usa es la de `_misma_seccion`, con tolerancia, y no `==`.

    Lo que NO se hace, y esta decidido: ni ordenar la serie (el orden lo
    declara el proyectista, ver `_siguiente_seccion_cajon`) ni cambiar la API
    por valor (tres tests la fijan). La guardia de PROGRESO de
    `MD.disenar_material` es la otra mitad: esta rechaza la serie mal
    declarada, aquella impide que cualquier regresion futura cuelgue la GUI.
    """
    for i, (B, H) in enumerate(pares):
        for B_prev, H_prev in pares[:i]:
            if (abs(B - B_prev) <= TOL_UMBRAL_NORMATIVO
                    and abs(H - H_prev) <= TOL_UMBRAL_NORMATIVO):
                raise DatoInvalidoError(
                    CRITERIO_SECCIONES_CAJON, valor=pares,
                    motivo=f"el par ({B}, {H}) en la posicion {i} REPITE un "
                           f"escalon anterior de la serie (dentro de "
                           f"TOL_UMBRAL_NORMATIVO = {TOL_UMBRAL_NORMATIVO}). "
                           "Una progresion con un escalon repetido no avanza: "
                           "el bucle de MD volveria siempre al mismo "
                           "siguiente y no terminaria. Cada par (B, H) tiene "
                           "que aparecer una sola vez",
                )


def _par_de_manning(clave: str, par: Any) -> Tuple[Optional[float],
                                                  Optional[float]]:
    """
    El par (n_min, n_max) de un criterio de doble n, o (None, None) si el
    criterio sigue sin valor (la excepcion documentada de 'n_manning_hdpe').

    LA FORMA MALA ES DEL EXPEDIENTE, NO DEL PROGRAMA (PC-01). Hasta EXT-1 un
    escalar declarado -- `--declarar n_manning_hdpe=0.012`, o `[0.012]` -- se
    desempaquetaba aqui con `TypeError`/`ValueError`, y no reventaba solo en
    el punto HDPE: tumbaba la corrida ENTERA de la CLI con traza, para todos
    los puntos, porque `materiales_candidatos` construye el catalogo de los
    tres materiales de una vez; la GUI lo mostraba como fallo de programa.
    Se exige secuencia de DOS reales finitos, no bool, en orden. El orden
    tambien lo exige `Material.__post_init__`, que es la red de abajo para
    cualquier constructor que no pase por aqui.
    """
    if par is None:
        return None, None
    forma_mala = DatoInvalidoError(
        clave, valor=par,
        motivo="se espera el PAR (n_min, n_max) de la regla de doble n de la "
               "Sec. 4.1 -- por ejemplo (0.010, 0.013) --: dos numeros reales "
               "finitos, el minimo primero. Un escalar, una lista de otro "
               "largo o un texto no son un par, y un par invertido mueve "
               "todas las velocidades de M3->M5->M6 al lado no conservador",
    )
    if isinstance(par, (str, bytes)) or not isinstance(par, (tuple, list)):
        raise forma_mala
    if len(par) != 2 or not all(ca._es_real(x) and math.isfinite(x)
                                for x in par):
        raise forma_mala
    n_min, n_max = par
    if not n_min <= n_max:
        raise forma_mala
    return float(n_min), float(n_max)


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
        no hay carta por defecto que poner: este repositorio tiene DIECIOCHO
        filas de cajon de concreto transcritas de la Tabla A.1 -- Cartas 8 a
        13 (quince hasta T-2, que sumo la Carta 13); la tabla trae mas, y lo
        que queda fuera lo censa el `Acotada` de
        `normativa/tablas.py::T_HDS5_A1` --, tres de Forma 1 y quince de Forma
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
        # PRIMERO, porque `servicio._etapa` registra UN bloqueo por etapa. Se lee
        # primero la embocadura y no el n: la embocadura elige la carta Y la
        # forma de ecuacion, y con ella el ke del control de salida, de modo
        # que es la que arrastra mas decisiones detras. Los otros tres
        # aparecen en cuanto este se declare.
        hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[_carta_de_cajon()])
        n_min, n_max = MANNING[_fila_manning_de_cajon()]
    elif tipo is TipoMaterial.HDPE:
        n_min, n_max = _par_de_manning(CRITERIO_N_MANNING_HDPE,
                                       _valor_si_declarado(CRITERIO_N_MANNING_HDPE))
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
        D_max_criterio = CRITERIO_SECCIONES_CAJON
    else:
        D_max, D_max_criterio, D_max_rotulo = tope_de_diametro(tipo)

    # --- T-4 --- EL TMC NO SE DECLARA EN 'espesor_pared_conducto': su t se
    # DERIVA de la corrugacion y la plancha adoptadas. Una entrada «tmc»
    # declarada alli MANDA sobre la derivada --es el espesor de un producto
    # ya especificado, y un dato del producto no se sustituye por una
    # regla--; sin ella, se deriva. Si el criterio entero esta vacio no se
    # deriva nada: `espesor_pared` bloquea para los tres materiales, como
    # antes.
    espesor_del_material = (None if espesores is None
                            else espesores.get(tipo.value))
    if espesores is not None and espesor_del_material is None \
            and tipo is TipoMaterial.TMC \
            and forma is not FormaSeccion.RECTANGULAR:
        espesor_del_material = espesor_pared_de_tmc()

    return Material(
        tipo=tipo,
        nombre=_NOMBRE[tipo],
        n_min=n_min,
        n_max=n_max,
        D_max=D_max,
        D_max_de_catalogo=D_max_rotulo,
        norma_producto=norma_producto_de(tipo, forma),
        hds5=hds5,
        fila_manning=_fila_manning(tipo, forma),
        v_max_tabla10=v_max_tabla10,
        v_max_adoptado=v_max_adoptado,
        # [N] directo de EG-2013 508.07 y SOLO para HDPE: los otros dos
        # materiales no tienen minimo en el EG-2013, y su None significa eso.
        h_relleno_min_eg2013=H_RELLENO_MIN[_EG2013_CLAVE[tipo]],
        espesor_pared=espesor_del_material,
        # LA SECCION DEL EG-2013 NO SALE DEL MATERIAL SOLO, y hasta C7 si:
        # las cuatro entradas de `SECCION_EG2013` son de TUBERIA -- los cuatro
        # titulos impresos empiezan por esa palabra --, de modo que un marco
        # de concreto reforzado heredaba la 506, cuyo 506.01 alcanza «la
        # instalacion de tubos». Un marco vaciado in situ se construye bajo la
        # Seccion 503 (num. 503.10 h): «Placa superior en alcantarillas de
        # cajon: 14 dias»), con el acero por la 504.
        seccion_eg2013=(SECCION_EG2013_CAJON
                        if forma is FormaSeccion.RECTANGULAR
                        else SECCION_EG2013[tipo.value]),
        forma=forma,
        pasos=(_pasos_del_marco() if forma is FormaSeccion.RECTANGULAR
               else ()),
        D_max_criterio=D_max_criterio,
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

def tipos_candidatos(punto: PuntoCritico) -> Tuple[TipoMaterial, ...]:
    """
    Los TIPOS de material que la familia del punto admite (Sec. 2.3 y 3.4),
    sin construir su catalogo: el marco de concreto en la Familia C; los tres
    en las otras dos. Lo comparten `materiales_candidatos` y
    `matriz_durabilidad`, que necesita saber a que materiales les aplica una
    regla sin exigir antes los criterios del cajon.
    """
    if punto.familia is Familia.C:
        return (TipoMaterial.CONCRETO_REFORZADO,)
    return tuple(TipoMaterial)


def materiales_candidatos(
        punto: PuntoCritico,
        durabilidad: Optional[DictamenDurabilidad] = None,
) -> Tuple[Material, ...]:
    """
    Materiales candidatos para el punto, ANTES de dimensionar (Sec. 3.2 +
    Sec. 3.4). No elige uno: entrega el catalogo completo de los que tienen
    sentido para la familia del punto.

    DESDE T-4 LA MATRIZ DE DURABILIDAD LOS FILTRA (INF-3.3.1). `durabilidad`
    es el dictamen de `matriz_durabilidad` para este punto: los materiales
    que excluye no entran en la tupla, y el ORDEN de los que quedan no
    cambia. Sin dictamen, o con uno «no aplicado» (el punto no trae
    ensayos), devuelve lo mismo que antes. Puede devolver la tupla VACIA
    --todos los candidatos de la familia excluidos--: MD lo convierte en
    `DisenoNoFactibleError` con las exclusiones citadas.

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
    excluidos = () if durabilidad is None else durabilidad.excluidos
    forma = (FormaSeccion.RECTANGULAR if punto.familia is Familia.C
             else FormaSeccion.CIRCULAR)
    return tuple(catalogo(tipo, forma=forma)
                 for tipo in tipos_candidatos(punto)
                 if tipo not in excluidos)


# ---------------------------------------------------------------------------
# --- T-4 --- Sec. 3.3 - La matriz de durabilidad
# ---------------------------------------------------------------------------

CODIGO_DURABILIDAD = "DUR"
# Auditoria de T-4 (H3): los criterios de suelo agresivo para acero
# galvanizado enterrado (AASHTO LRFD, por analogia) y su efecto sobre el TMC.
CRITERIO_SUELO_AGRESIVO = "suelo_agresivo_acero_lrfd"
CRITERIO_EFECTO_SUELO_AGRESIVO = "suelo_agresivo_lrfd_sobre_tmc"
EFECTO_AVISO, EFECTO_EXCLUYE = "aviso", "excluye"
# El [S] del EMS que M9 lee para el recubrimiento del cabezal: el mismo
# ensayo de sulfatos por otra puerta (H8). Aqui solo se CONTRASTA.
CRITERIO_EXPOSICION_EMS = "exposicion_quimica_ems"


def _avisos_fijos_del_metal(punto: PuntoCritico) -> Tuple[ReglaDeDurabilidad, ...]:
    """
    El aviso que NO depende de ningun ensayo (H6 de la auditoria de T-4).

    El Manual de Hidrologia (num. 4.1.1.3.7 f y g, pags. impresas 81 a 83) no
    recomienda la alcantarilla metalica en condiciones muy agresivas --aguas
    salinas o acidas, suelos alcalinos, suelos con turba-- y pide proteccion
    para cualquier material cerca del mar. Es texto cualitativo: no hay
    ensayo que lo dispare ni umbral que comparar, de modo que se imprime
    SIEMPRE que la TMC es candidata, para que el proyectista compruebe la
    condicion del sitio. No excluye ni exige: avisa.

    Con turba en la clasificacion del suelo de fundacion (`PT`) hay ademas
    un segundo aviso, este si ligado a un dato: es una de las condiciones
    que el inciso g) nombra.
    """
    if TipoMaterial.TMC not in tipos_candidatos(punto):
        return ()
    reglas = [ReglaDeDurabilidad(
        ensayo="condicion_del_sitio", material=TipoMaterial.TMC,
        efecto=EfectoDeDurabilidad.AVISA,
        texto=("aviso fijo, sin ensayo que lo dispare: el Manual de "
               "Hidrologia no recomienda alcantarillas metalicas en "
               "condiciones muy agresivas --aguas salinas o acidas, suelos "
               "alcalinos o con turba-- y pide proteccion para cualquier "
               "material en zonas costeras cercanas al mar. Antes de adoptar "
               "TMC hay que verificar la condicion del sitio"),
        cita_ids=("MC_HHD.4.1.1.3.7f#COSTA", "MC_HHD.4.1.1.3.7g#AGRESIVAS"))]
    if "PT" in componentes_sucs(punto.sucs_fundacion):
        reglas.append(ReglaDeDurabilidad(
            ensayo="sucs_fundacion", material=TipoMaterial.TMC,
            efecto=EfectoDeDurabilidad.AVISA,
            texto=(f"suelo de fundacion {punto.sucs_fundacion}: con turba, "
                   "el Manual de Hidrologia no recomienda alcantarillas "
                   "metalicas"),
            cita_ids=("MC_HHD.4.1.1.3.7g#AGRESIVAS",)))
    return tuple(reglas)


def _valor_sin_registrar_uso(clave: str) -> Any:
    """
    El valor efectivo de un criterio SIN registrarlo como usado: para
    CONTRASTAR un dato con otro, no para calcular con el. `ca.valor` lo
    anotaria entre los criterios que la corrida uso, y un criterio de
    expediente contrastado desde la Fase 3 apareceria como invocado a nivel
    de perfil sin que ningun numero dependa de el.
    """
    return ca.valores_dinamicos().get(clave, ca.CRITERIOS[clave].valor)


def _umbral_de_cita(*, descripcion: str, valor: Any, unidad: str,
                    cita_id: str, aplicacion: str,
                    criterio: Optional[str] = None) -> Umbral:
    """
    Un `Umbral` cuyo CARACTER se lee de su cita y no se escribe aqui: es lo
    que impide rotular «exigencia» lo que la fuente recomienda (NOR-MEM-01).
    """
    from src.modelos import _registro_normativo
    caracter = _registro_normativo().cita(cita_id).caracter.value.upper()
    return Umbral(descripcion=descripcion, valor=valor, unidad=unidad,
                  cita_id=cita_id, caracter=caracter, aplicacion=aplicacion,
                  criterio_aplicado=criterio)


def _umbrales_de_durabilidad_tmc() -> dict:
    """
    Los tres umbrales de 'durabilidad_tmc_umbrales' [C], comprobados antes de
    usarlos: un dict con los tres campos, cada uno un numero finito, y el
    intervalo de pH en orden. La puerta de declaracion ya exige la ventana
    por campo; esto es la segunda linea, como en `_par_de_manning`.
    """
    u = ca.valor(CRITERIO_DURABILIDAD_TMC)
    campos = ("pH_min", "pH_max", "resistividad_min_ohm_cm")
    if not isinstance(u, dict) or any(c not in u for c in campos):
        raise DatoInvalidoError(
            campo=CRITERIO_DURABILIDAD_TMC, valor=u,
            motivo=f"tiene que ser un dict con los campos {campos}")
    for c in campos:
        if not ca._es_real(u[c]) or not math.isfinite(u[c]):
            raise DatoInvalidoError(
                campo=CRITERIO_DURABILIDAD_TMC, valor=u[c],
                motivo=f"el campo '{c}' tiene que ser un numero finito")
    if not u["pH_min"] <= u["pH_max"]:
        raise DatoInvalidoError(
            campo=CRITERIO_DURABILIDAD_TMC, valor=(u["pH_min"], u["pH_max"]),
            motivo="el intervalo de pH esta invertido: pH_min tiene que ser "
                   "<= pH_max")
    return u


def componentes_sucs(sucs: str) -> Tuple[str, ...]:
    """
    Los simbolos SUCS de una clasificacion, en MAYUSCULAS: uno para un suelo
    de grupo simple («SM»), dos para uno de frontera («SP-SM», «CL-ML»).
    """
    return tuple(parte.strip().upper()
                 for parte in str(sucs).replace("/", "-").split("-")
                 if parte.strip())


def _regla_del_suelo_de_fundacion(punto: PuntoCritico):
    """
    El aviso «suelo de fundacion deficiente -> marco» (v8 §3.1; num.
    4.1.1.3.4 a) del Manual de Hidrologia), que es el consumidor de la
    columna `sucs_fundacion` (INF-5.1.9).

    Devuelve (linea, reglas, pasos). La LINEA se devuelve siempre: dice que
    se leyo y contra que conjunto. La regla y su paso, solo si alguno de los
    simbolos del punto esta en 'sucs_fundacion_deficiente' [A] y el punto NO
    es ya un marco (Familia C): ahi la recomendacion ya esta cumplida.

    ES UN AVISO Y NO UN FILTRO: no cambia el material ni la seccion. El
    Manual RECOMIENDA el marco y no define «mala calidad»; que simbolos
    cuentan lo declara el proyecto, apoyado en E.050 Art. 24.
    """
    declarado = ca.valor(CRITERIO_SUCS_DEFICIENTE)
    # La guardia del CONSUMIDOR, que aqui es la primera linea y no la
    # segunda: la puerta de una serie de claves comprueba la forma, no que
    # cada clave sea un simbolo de la tabla. Un simbolo que no existe en la
    # Figura 3 de la E.050 nunca coincidiria con ningun suelo y el aviso
    # quedaria apagado sin que nadie lo notara.
    if not isinstance(declarado, (tuple, list)) or any(
            not isinstance(x, str) or x.upper() not in SIMBOLOS_SUCS
            for x in declarado):
        raise DatoInvalidoError(
            campo=CRITERIO_SUCS_DEFICIENTE, valor=declarado,
            motivo="el conjunto de suelos de fundacion deficientes se "
                   "declara como una serie de simbolos SUCS de la Figura 3 "
                   f"de la E.050: {', '.join(SIMBOLOS_SUCS)}")
    deficientes = tuple(x.upper() for x in declarado)
    simbolos = componentes_sucs(punto.sucs_fundacion)
    conjunto = ", ".join(deficientes)
    desconocidos = tuple(x for x in simbolos if x not in SIMBOLOS_SUCS)
    if not simbolos or desconocidos:
        return ((f"suelo de fundacion '{punto.sucs_fundacion}': no es una "
                 "clasificacion SUCS de la Figura 3 de la E.050 y no se pudo "
                 f"contrastar con el conjunto declarado deficiente "
                 f"({conjunto}; criterio '{CRITERIO_SUCS_DEFICIENTE}' [A])"),
                (), ())
    malos = tuple(x for x in simbolos if x in deficientes)
    if not malos:
        # NO ES UNA CALIFICACION DE APTITUD (H9 de la auditoria de T-4). La
        # linea decia solo «no esta entre los grupos deficientes», que para
        # una arena limosa bajo la napa se lee como «apto» y no lo es: la
        # E.050 manda evaluar la licuacion de los suelos granulares. No se
        # decide aqui que simbolos son licuables --seria inventar el mapeo--:
        # se remite al articulo para todo suelo que no este en el conjunto.
        return ((f"suelo de fundacion {punto.sucs_fundacion}: no esta entre "
                 f"los grupos SUCS declarados deficientes ({conjunto}; "
                 f"criterio '{CRITERIO_SUCS_DEFICIENTE}' [A]). Eso no lo "
                 "califica como apto: este aviso no evalua capacidad "
                 "portante, asentamientos ni licuacion; bajo el nivel "
                 "freatico, la E.050 (Art. 38, pag. 51) manda evaluar la "
                 "licuacion de los suelos granulares y de algunos con finos"),
                (), ())
    if punto.familia is Familia.C:
        return ((f"suelo de fundacion {punto.sucs_fundacion}: grupo "
                 f"declarado deficiente ({conjunto}; criterio "
                 f"'{CRITERIO_SUCS_DEFICIENTE}' [A]); la obra ya es un marco "
                 "de concreto, que es lo que el Manual recomienda en ese "
                 "caso"), (), ())
    texto = (f"suelo de fundacion {punto.sucs_fundacion}: grupo declarado "
             f"deficiente ({conjunto}; criterio "
             f"'{CRITERIO_SUCS_DEFICIENTE}' [A]). La E.050 (Art. 24) no "
             "permite cimentar sobre turba ni suelo organico y manda "
             "removerlos en la totalidad del terreno y reemplazarlos por "
             "relleno controlado; el Manual recomienda ademas, con suelo de "
             "fundacion de mala calidad, la alcantarilla tipo marco de "
             "concreto. El calculo NO cambia el tipo ni el material por "
             "este aviso: lo decide el proyectista con el estudio de suelos")
    regla = ReglaDeDurabilidad(
        ensayo="sucs_fundacion", material=None,
        efecto=EfectoDeDurabilidad.AVISA, texto=texto,
        cita_ids=("MC_HHD.4.1.1.3.4a#MARCO", "E050.24", "E050.24#REMOVER"),
        criterio=CRITERIO_SUCS_DEFICIENTE)
    paso_ = paso(
        "F3.DUR.SUELO_FUNDACION", codigo=CODIGO_DURABILIDAD,
        que="Suelo de fundacion: grupo SUCS frente al conjunto declarado "
            "deficiente",
        formula="grupo SUCS del punto en el conjunto declarado deficiente",
        citas_textuales=("MC_HHD.4.1.1.3.4a#MARCO", "E050.24",
                         "E050.24#REMOVER"),
        sustitucion=(
            Magnitud("SUCS", punto.sucs_fundacion, "",
                     "columna sucs_fundacion del CSV (Sec. 1.2): "
                     "clasificacion de la calicata del punto"),
            Magnitud("conjunto deficiente", conjunto, "",
                     f"criterio '{CRITERIO_SUCS_DEFICIENTE}' [A]")),
        resultado=Magnitud("grupos deficientes del punto", ", ".join(malos),
                           "", "interseccion de los dos anteriores"),
        nota_del_proyecto=texto)
    return texto, (regla,), (paso_,)


def matriz_durabilidad(
        punto: PuntoCritico,
        ensayos: Optional[EnsayosDurabilidad] = None) -> DictamenDurabilidad:
    """
    La matriz de durabilidad de la Sec. 3.3 de la hoja de ruta, aplicada a UN
    punto: que hace cada ensayo declarado con cada material candidato.

    ENTRADAS: los seis ensayos de `EnsayosDurabilidad`, TODOS opcionales y
    sin valor por defecto --son del EMS y del estudio de campo
    (docs/contrato_entradas.md)--, y la columna `sucs_fundacion` del CSV.
    SIN ENSAYOS LA MATRIZ NO ACTUA: devuelve un dictamen con
    `aplicada=False`, sin reglas de ensayo ni pasos, y la memoria imprime
    `modelos.DURABILIDAD_SIN_ENSAYOS`. No se supone un ambiente «benigno» ni
    uno «agresivo»: no hay dato.

    LAS REGLAS, cada una con la fuente que la sostiene y solo con ella:

    pH (suelo o agua)
        fuera de [pH_min, pH_max] de 'durabilidad_tmc_umbrales' [C] (5.0 a
        8.5: WSDOT §8-5.1)                -> TMC EXCLUIDA
        dentro, y menor de 5.8 ([N], EG-2013 507.10)
                                          -> TMC sigue, EXIGE proteccion
        (EG-2013 escribe ese 5.8 para el AGUA que conduce el tubo; hay una
        sola clave `pH`, y se le aplica sea del agua o del suelo: es el
        lado seguro, y la regla lo deja dicho)
        concreto y HDPE: el pH no los excluye (WSDOT §8-3.1, §8-3.3, §8-4.3)
    resistividad (suelo o agua)
        menor de resistividad_min_ohm_cm (1000: WSDOT §8-5.2)
                                          -> TMC EXCLUIDA
    abrasion (nivel del sitio, WSDOT Table 8-4)
        severa   -> HDPE EXCLUIDO (WSDOT §8-3.3); TMC y concreto, AVISO: la
                    fuente pide mas espesor o solera de concreto
        moderada -> TMC y concreto, AVISO
    sulfatos (suelo en ppm -> % en peso; o agua en ppm): fila de la Tabla
        4.4 de E.060 -> concreto EXIGE el cemento, la a/c maxima y el f'c
        minimo de la fila. NUNCA excluye: la norma no prohibe el concreto en
        ninguna exposicion.
    cloruros -> AVISO: E.060 4.4.2 exige la fila de cloruros de la Tabla 4.2
        y el recubrimiento del 7.7 cuando el concreto reforzado queda
        expuesto a cloruros de sal, agua salobre o agua de mar, y NO fija
        un umbral en ppm; el Manual de Hidrologia advierte del acero en agua
        salina, tambien sin numero. El ensayo no decide solo.
    suelo de fundacion (columna `sucs_fundacion`) -> AVISO de marco si el
        grupo esta en 'sucs_fundacion_deficiente' [A]. No es un ensayo de
        durabilidad y se evalua siempre.

    LO QUE AÑADIO LA AUDITORIA ADVERSARIAL DE T-4:

    suelo agresivo para el acero (pH, resistividad, cloruros o sulfatos del
        suelo fuera de 'suelo_agresivo_acero_lrfd' [C]: AASHTO LRFD
        11.10.6.4.2a y 11.12.8, criterios de refuerzos enterrados aplicados
        POR ANALOGIA) -> TMC con AVISO, o EXCLUIDA si
        'suelo_agresivo_lrfd_sobre_tmc' [A] vale «excluye» (vale «aviso»)
    suelos circundantes agresivos (ese suelo agresivo, o sulfatos sobre la
        exposicion insignificante de E.060 T4.4) -> TMC EXIGE proteccion
        ([N], la segunda mitad de EG-2013 507.10)
    aviso FIJO del Manual (4.1.1.3.7 f y g), sin ensayo: toda TMC candidata;
        y contra el metal si el suelo de fundacion trae turba (PT)
    dos entradas del mismo ensayo de sulfatos que se contradicen (estas
        claves y el [S] 'exposicion_quimica_ems') -> AVISO de incoherencia

    Las reglas de un material que no es candidato en la familia del punto
    (TMC y HDPE en la Familia C) no se emiten: no hay nada que excluir.

    NO ELIGE MATERIAL. Devuelve un dictamen; quien filtra es
    `materiales_candidatos` y quien adopta, MD.
    """
    linea_suelo, reglas_suelo, pasos_suelo = \
        _regla_del_suelo_de_fundacion(punto)
    # Los avisos que no dependen de ningun ensayo (H6): van con ensayos o
    # sin ellos, despues de las reglas de ensayo y antes de la del suelo.
    reglas_suelo = _avisos_fijos_del_metal(punto) + reglas_suelo
    if ensayos is None or not ensayos.hay_ensayos:
        return DictamenDurabilidad(aplicada=False, reglas=reglas_suelo,
                                   pasos=pasos_suelo, ensayos=ensayos,
                                   suelo_fundacion=linea_suelo)

    candidatos = tipos_candidatos(punto)
    reglas: list = []
    pasos: list = []

    def regla(ensayo, material, efecto, texto, citas, criterio=""):
        if material is None or material in candidatos:
            reglas.append(ReglaDeDurabilidad(
                ensayo=ensayo, material=material, efecto=efecto, texto=texto,
                cita_ids=tuple(citas), criterio=criterio))

    tmc, hdpe, concreto = (TipoMaterial.TMC, TipoMaterial.HDPE,
                           TipoMaterial.CONCRETO_REFORZADO)

    # ---- pH -----------------------------------------------------------------
    if ensayos.pH is not None:
        u = _umbrales_de_durabilidad_tmc()
        pH, pH_min, pH_max = ensayos.pH, u["pH_min"], u["pH_max"]
        dentro = pH_min - TOL_UMBRAL_NORMATIVO <= pH <= pH_max + TOL_UMBRAL_NORMATIVO
        exige = dentro and pH < PH_MIN_AGUA_TMC_SIN_PROTECCION - TOL_UMBRAL_NORMATIVO
        if not dentro:
            regla("pH", tmc, EfectoDeDurabilidad.EXCLUYE,
                  f"pH = {pH:g} fuera del intervalo {pH_min:g} a {pH_max:g} "
                  f"en que la fuente tecnica admite tuberia de acero "
                  f"(criterio '{CRITERIO_DURABILIDAD_TMC}' [C]): la TMC "
                  "galvanizada no es candidata en este punto",
                  ("WSDOT_HM.8-5.1#PH", "WSDOT_HM.8-4.3#ZONA_III"),
                  CRITERIO_DURABILIDAD_TMC)
        elif exige:
            regla("pH", tmc, EfectoDeDurabilidad.EXIGE,
                  f"pH = {pH:g} menor de "
                  f"{PH_MIN_AGUA_TMC_SIN_PROTECCION:g}: la TMC sigue "
                  "candidata y la especificacion tiene que incluir la "
                  f"proteccion de la tuberia ({NUMERAL_PH_MIN_TMC}); el "
                  "producto y el procedimiento son del proyecto. La norma "
                  "lo escribe para el agua que conduce el tubo; aqui se "
                  "aplica al pH declarado, sea del agua o del suelo, que "
                  "es el lado seguro",
                  ("EG2013.507.10",))
        margen = min(pH - pH_min, pH_max - pH)
        pasos.append(paso(
            "F3.DUR.PH", codigo=CODIGO_DURABILIDAD,
            que="Durabilidad: pH del sitio frente al intervalo en que se "
                "admite tuberia de acero corrugado",
            formula="pH_min <= pH <= pH_max",
            citas_textuales=("WSDOT_HM.8-5.1#PH", "EG2013.507.10",
                             "WSDOT_HM.8-4.3#ZONA_III"),
            sustitucion=(
                Magnitud("pH", pH, "", ensayos.origen_de("pH"),
                         cifras=CIFRAS_FACTOR),
                Magnitud("pH_min", pH_min, "",
                         f"criterio '{CRITERIO_DURABILIDAD_TMC}' [C]",
                         cifras=CIFRAS_FACTOR),
                Magnitud("pH_max", pH_max, "",
                         f"criterio '{CRITERIO_DURABILIDAD_TMC}' [C]",
                         cifras=CIFRAS_FACTOR),
                Magnitud("pH de proteccion", PH_MIN_AGUA_TMC_SIN_PROTECCION,
                         "", f"[N] {NUMERAL_PH_MIN_TMC}",
                         cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("pH", pH, "", "el ensayo, contrastado contra "
                               "el intervalo", cifras=CIFRAS_FACTOR),
            umbral=_umbral_de_cita(
                descripcion="intervalo de pH del suelo o del agua en que la "
                            "fuente admite tuberia de acero",
                valor=f"{pH_min:g} a {pH_max:g}", unidad="",
                cita_id="WSDOT_HM.8-5.1#PH",
                aplicacion="fuera del intervalo la TMC galvanizada sale de "
                           "los materiales candidatos del punto; el "
                           "concreto y el HDPE no se excluyen por pH",
                criterio=CRITERIO_DURABILIDAD_TMC),
            veredicto=Veredicto(
                tipo=(TipoDeVeredicto.CUMPLE if dentro
                      else TipoDeVeredicto.NO_CUMPLE),
                margen=margen, unidad="",
                explicacion=(
                    "la TMC sigue candidata, con la proteccion que exige "
                    "EG-2013 507.10" if exige else
                    "la TMC sigue candidata por pH" if dentro else
                    "la TMC galvanizada queda fuera de los candidatos")),
        ))

    # ---- resistividad -------------------------------------------------------
    if ensayos.resistividad_ohm_cm is not None:
        u = _umbrales_de_durabilidad_tmc()
        rho, rho_min = ensayos.resistividad_ohm_cm, u["resistividad_min_ohm_cm"]
        basta = rho >= rho_min - TOL_UMBRAL_NORMATIVO
        if not basta:
            regla("resistividad_ohm_cm", tmc, EfectoDeDurabilidad.EXCLUYE,
                  f"resistividad = {rho:g} ohm-cm menor de {rho_min:g} "
                  f"ohm-cm (criterio '{CRITERIO_DURABILIDAD_TMC}' [C]): la "
                  "TMC galvanizada no es candidata en este punto",
                  ("WSDOT_HM.8-5.2#RESISTIVIDAD", "WSDOT_HM.8-4.3#ZONA_III"),
                  CRITERIO_DURABILIDAD_TMC)
        pasos.append(paso(
            "F3.DUR.RESISTIVIDAD", codigo=CODIGO_DURABILIDAD,
            que="Durabilidad: resistividad del sitio frente al minimo con "
                "que se admite tuberia de acero corrugado",
            formula="resistividad >= resistividad_min",
            citas_textuales=("WSDOT_HM.8-5.2#RESISTIVIDAD",
                             "WSDOT_HM.8-4.3#ZONA_III"),
            sustitucion=(
                Magnitud("resistividad", rho, "ohm-cm",
                         ensayos.origen_de("resistividad_ohm_cm"),
                         cifras=CIFRAS_FACTOR),
                Magnitud("resistividad_min", rho_min, "ohm-cm",
                         f"criterio '{CRITERIO_DURABILIDAD_TMC}' [C]",
                         cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("resistividad", rho, "ohm-cm",
                               "el ensayo, contrastado contra el minimo",
                               cifras=CIFRAS_FACTOR),
            umbral=_umbral_de_cita(
                descripcion="resistividad minima del suelo o del agua con "
                            "que la fuente admite tuberia de acero",
                valor=rho_min, unidad="ohm-cm",
                cita_id="WSDOT_HM.8-5.2#RESISTIVIDAD",
                aplicacion="por debajo la TMC galvanizada sale de los "
                           "materiales candidatos del punto",
                criterio=CRITERIO_DURABILIDAD_TMC),
            veredicto=Veredicto(
                tipo=(TipoDeVeredicto.CUMPLE if basta
                      else TipoDeVeredicto.NO_CUMPLE),
                margen=rho - rho_min, unidad="ohm-cm",
                explicacion=("la TMC sigue candidata por resistividad"
                             if basta else
                             "la TMC galvanizada queda fuera de los "
                             "candidatos")),
        ))

    # ---- abrasion -----------------------------------------------------------
    if ensayos.abrasion is not None:
        nivel = ensayos.abrasion
        if nivel not in NIVELES_DE_ABRASION:
            raise DatoInvalidoError(
                "abrasion", valor=nivel, id_punto=punto.id,
                motivo="el nivel de abrasion del sitio tiene que ser uno de "
                       "los cuatro de la Table 8-4 del WSDOT Hydraulics "
                       f"Manual: {', '.join(NIVELES_DE_ABRASION)}")
        indice = NIVELES_DE_ABRASION.index(nivel)
        severo = nivel == NIVEL_DE_ABRASION_SEVERO
        moderado_o_mas = indice >= NIVELES_DE_ABRASION.index(
            NIVEL_DE_ABRASION_SEVERO) - 1
        if severo:
            regla("abrasion", hdpe, EfectoDeDurabilidad.EXCLUYE,
                  f"nivel de abrasion '{nivel}': la fuente no admite el "
                  "termoplastico en ese nivel porque no se puede reforzar; "
                  "el HDPE no es candidato en este punto",
                  ("WSDOT_HM.8-3.3#SEVERA", "WSDOT_HM.T8-4"))
        if moderado_o_mas:
            regla("abrasion", tmc, EfectoDeDurabilidad.AVISA,
                  f"nivel de abrasion '{nivel}': para el metal la Table 8-4 "
                  "de WSDOT pide aumentar el espesor de plancha "
                  + ("al menos dos calibres o revestir la solera con "
                     "concreto" if severo else "uno o dos calibres")
                  + f" (el del catalogo es el de '{CRITERIO_CALIBRE_TMC}'); "
                  "con condiciones muy agresivas el Manual de Hidrologia no "
                  "recomienda la alcantarilla metalica. V3 no sustituye esa "
                  "proteccion",
                  ("WSDOT_HM.T8-4", "MC_HHD.4.1.1.3.7g#AGRESIVAS"),
                  CRITERIO_CALIBRE_TMC)
            regla("abrasion", concreto, EfectoDeDurabilidad.AVISA,
                  f"nivel de abrasion '{nivel}': para el concreto la Table "
                  "8-4 de WSDOT pide especificar mas espesor de pared o mas "
                  "resistencia a compresion",
                  ("WSDOT_HM.T8-4",))
        pasos.append(paso(
            "F3.DUR.ABRASION", codigo=CODIGO_DURABILIDAD,
            que="Durabilidad: nivel de abrasion del sitio frente al nivel "
                "en que la fuente no admite termoplastico",
            formula="nivel de abrasion del sitio < nivel severo",
            citas_textuales=("WSDOT_HM.8-3.3#SEVERA", "WSDOT_HM.T8-4",
                             "MC_HHD.4.1.1.3.7e"),
            sustitucion=(
                Magnitud("nivel de abrasion", nivel, "",
                         ensayos.origen_de("abrasion")),),
            resultado=Magnitud("nivel de abrasion", nivel, "",
                               "dato de campo del sitio: no se deduce de la "
                               "velocidad"),
            umbral=_umbral_de_cita(
                descripcion="nivel de abrasion en que la fuente no admite "
                            "tuberia termoplastica",
                valor=NIVEL_DE_ABRASION_SEVERO, unidad="",
                cita_id="WSDOT_HM.8-3.3#SEVERA",
                aplicacion="en el nivel severo el HDPE sale de los "
                           "materiales candidatos del punto; el metal y el "
                           "concreto siguen, con el aviso de la proteccion "
                           "que la tabla pide"),
            veredicto=Veredicto(
                tipo=(TipoDeVeredicto.NO_CUMPLE if severo
                      else TipoDeVeredicto.CUMPLE),
                explicacion=("el HDPE queda fuera de los candidatos"
                             if severo else
                             "el HDPE sigue candidato por abrasion")),
        ))

    # ---- sulfatos -----------------------------------------------------------
    exposicion_sulfatos = None
    if ensayos.sulfatos_suelo_ppm is not None \
            or ensayos.sulfatos_agua_ppm is not None:
        suelo_pct = (None if ensayos.sulfatos_suelo_ppm is None
                     else ensayos.sulfatos_suelo_ppm / PPM_POR_PORCIENTO)
        fila = _fila_de_sulfatos(suelo_pct, ensayos.sulfatos_agua_ppm)
        exposicion = exposicion_sulfatos = fila["exposicion"]
        # EL MISMO ENSAYO DEL EMS POR DOS PUERTAS (H8): estas dos claves y el
        # dato de sitio 'exposicion_quimica_ems', que M9 lee para el
        # recubrimiento del cabezal. Si las dos estan declaradas y dan
        # exposiciones distintas, se avisa: el programa no decide cual vale.
        ems = _valor_sin_registrar_uso(CRITERIO_EXPOSICION_EMS)
        if isinstance(ems, dict) and (ems.get("so4_suelo_pct") is not None
                                      or ems.get("so4_agua_ppm") is not None):
            del_ems = _fila_de_sulfatos(ems.get("so4_suelo_pct"),
                                        ems.get("so4_agua_ppm"))["exposicion"]
            if del_ems != exposicion:
                regla("sulfatos", None, EfectoDeDurabilidad.AVISA,
                      f"INCOHERENCIA ENTRE DOS ENTRADAS DEL MISMO ENSAYO: "
                      f"los sulfatos declarados para esta matriz dan "
                      f"exposicion '{exposicion}' y el dato de sitio "
                      f"'{CRITERIO_EXPOSICION_EMS}', que fija el "
                      f"recubrimiento del cabezal, da '{del_ems}'. Son el "
                      "mismo ensayo del estudio de suelos por dos puertas: "
                      "hay que corregir la que este mal antes de entregar",
                      ("E060.T4.4",), CRITERIO_EXPOSICION_EMS)
        if fila["a_c_max"] is not None:
            regla("sulfatos", concreto, EfectoDeDurabilidad.EXIGE,
                  f"exposicion a sulfatos '{exposicion}' (E.060 Tabla 4.4): "
                  f"el concreto sigue candidato y su especificacion exige "
                  f"cemento {' o '.join(fila['cementos'])}, relacion "
                  f"agua-material cementante maxima {fila['a_c_max']} y f'c "
                  f"minimo {fila['fc_min_MPa']} MPa",
                  ("E060.T4.4",))
        sustitucion = []
        if ensayos.sulfatos_suelo_ppm is not None:
            sustitucion.append(Magnitud(
                "SO4 en el suelo", ensayos.sulfatos_suelo_ppm, "ppm",
                ensayos.origen_de("sulfatos_suelo_ppm"), cifras=CIFRAS_FACTOR))
            sustitucion.append(Magnitud(
                "SO4 en el suelo", suelo_pct, "% en peso",
                "el mismo dato en la unidad de la Tabla 4.4: 1 % = 10 000 "
                "ppm", cifras=CIFRAS_FINA))
        if ensayos.sulfatos_agua_ppm is not None:
            sustitucion.append(Magnitud(
                "SO4 en el agua", ensayos.sulfatos_agua_ppm, "ppm",
                ensayos.origen_de("sulfatos_agua_ppm"), cifras=CIFRAS_FACTOR))
        pasos.append(paso(
            "F3.DUR.SULFATOS", codigo=CODIGO_DURABILIDAD,
            que="Durabilidad: exposicion del concreto a sulfatos",
            formula="fila de la Tabla 4.4 de E.060 que alcanza el ensayo; "
                    "con las dos escalas, la mas exigente",
            formula_cita_id="E060.T4.4",
            citas_textuales=("E060.T4.4",),
            sustitucion=tuple(sustitucion),
            resultado=Magnitud("exposicion a sulfatos", exposicion, "",
                               "fila de la Tabla 4.4 de E.060"),
            nota_del_proyecto=(
                "El concreto no se excluye por sulfatos en ninguna "
                "exposicion: la norma le exige cemento, relacion "
                "agua-material cementante y resistencia. La exposicion "
                "insignificante no exige nada."),
        ))

    # ---- cloruros -----------------------------------------------------------
    if ensayos.cloruros_ppm is not None:
        fila_cl = EXPOSICION_ESPECIAL["cloruros"]
        regla("cloruros_ppm", concreto, EfectoDeDurabilidad.AVISA,
              f"cloruros = {ensayos.cloruros_ppm:g} ppm declarados: si el "
              "proyectista determina que el concreto reforzado queda "
              "expuesto a cloruros de sal, agua salobre o agua de mar, "
              "E.060 4.4.2 exige relacion agua-material cementante maxima "
              f"{fila_cl['a_c_max']}, f'c minimo {fila_cl['fc_min_MPa']} MPa "
              "y el recubrimiento minimo del 7.7. La norma define la "
              "exposicion por el origen del cloruro y no por un umbral en "
              "ppm: el ensayo no decide solo",
              ("E060.4.4.2", "E060.T4.2"))
        # El aviso del TMC por cloruros «sin umbral» salio en la auditoria
        # de T-4 (H3): para el acero galvanizado enterrado AASHTO LRFD si
        # da umbral, y lo aplica el bloque de suelo agresivo, mas abajo.
        pasos.append(paso(
            "F3.DUR.CLORUROS", codigo=CODIGO_DURABILIDAD,
            que="Durabilidad: cloruros declarados y proteccion del acero "
                "del concreto reforzado",
            formula="para el concreto, sin umbral numerico en la fuente: "
                    "la exposicion se define por el origen del cloruro",
            citas_textuales=("E060.4.4.2", "MC_HHD.4.1.1.3.7f#SALINIDAD"),
            sustitucion=(
                Magnitud("cloruros", ensayos.cloruros_ppm, "ppm",
                         ensayos.origen_de("cloruros_ppm"),
                         cifras=CIFRAS_FACTOR),),
            resultado=Magnitud("cloruros", ensayos.cloruros_ppm, "ppm",
                               "el ensayo, sin umbral contra el que "
                               "contrastarlo", cifras=CIFRAS_FACTOR),
            nota_del_proyecto=(
                "El concreto no se excluye por este dato. Queda escrito "
                "el requisito que E.060 impone al concreto reforzado si la "
                "exposicion aplica, y quien lo decide. Para la tuberia "
                "metalica los cloruros SI tienen umbral, por analogia: ver "
                "el paso de suelo agresivo."),
        ))

    # ---- suelo agresivo para el acero galvanizado (H3 y H5) -------------------
    # Los criterios electroquimicos de AASHTO LRFD para refuerzos de acero
    # enterrados, aplicados POR ANALOGIA. El efecto sobre el TMC es una
    # eleccion declarada ('suelo_agresivo_lrfd_sobre_tmc' [A]): por defecto
    # AVISA; «excluye» es la lectura estricta, para la sensibilidad.
    medidas = (("pH", ensayos.pH, "pH", ""),
               ("resistividad_ohm_cm", ensayos.resistividad_ohm_cm,
                "resistividad", "ohm-cm"),
               ("cloruros_ppm", ensayos.cloruros_ppm, "cloruros", "ppm"),
               ("sulfatos_suelo_ppm", ensayos.sulfatos_suelo_ppm,
                "sulfatos en el suelo", "ppm"))
    motivos_lrfd: list = []
    if tmc in candidatos and any(v is not None for _c, v, _n, _u in medidas):
        u = ca.valor(CRITERIO_SUELO_AGRESIVO)
        campos = ("pH_min", "pH_max", "resistividad_min_ohm_cm",
                  "cloruros_max_ppm", "sulfatos_max_ppm")
        if not isinstance(u, dict) or any(
                c not in u or not ca._es_real(u[c]) or not math.isfinite(u[c])
                for c in campos):
            raise DatoInvalidoError(
                campo=CRITERIO_SUELO_AGRESIVO, valor=u,
                motivo=f"tiene que ser un dict con los campos {campos}, "
                       "cada uno un numero finito")
        tol = TOL_UMBRAL_NORMATIVO
        if ensayos.pH is not None and not (
                u["pH_min"] - tol <= ensayos.pH <= u["pH_max"] + tol):
            motivos_lrfd.append(f"pH = {ensayos.pH:g} fuera de "
                                f"{u['pH_min']:g} a {u['pH_max']:g}")
        if ensayos.resistividad_ohm_cm is not None and not (
                ensayos.resistividad_ohm_cm
                >= u["resistividad_min_ohm_cm"] - tol):
            motivos_lrfd.append(
                f"resistividad = {ensayos.resistividad_ohm_cm:g} ohm-cm "
                f"menor de {u['resistividad_min_ohm_cm']:g} ohm-cm")
        if ensayos.cloruros_ppm is not None and not (
                ensayos.cloruros_ppm <= u["cloruros_max_ppm"] + tol):
            motivos_lrfd.append(
                f"cloruros = {ensayos.cloruros_ppm:g} ppm mayor de "
                f"{u['cloruros_max_ppm']:g} ppm")
        if ensayos.sulfatos_suelo_ppm is not None and not (
                ensayos.sulfatos_suelo_ppm <= u["sulfatos_max_ppm"] + tol):
            motivos_lrfd.append(
                f"sulfatos en el suelo = {ensayos.sulfatos_suelo_ppm:g} ppm "
                f"mayor de {u['sulfatos_max_ppm']:g} ppm")
        agresivo = bool(motivos_lrfd)
        efecto_lrfd = EFECTO_AVISO
        if agresivo:
            efecto_lrfd = ca.valor(CRITERIO_EFECTO_SUELO_AGRESIVO)
            if efecto_lrfd not in (EFECTO_AVISO, EFECTO_EXCLUYE):
                raise DatoInvalidoError(
                    campo=CRITERIO_EFECTO_SUELO_AGRESIVO, valor=efecto_lrfd,
                    motivo=f"tiene que ser '{EFECTO_AVISO}' o "
                           f"'{EFECTO_EXCLUYE}'")
            regla("suelo_agresivo", tmc,
                  (EfectoDeDurabilidad.EXCLUYE
                   if efecto_lrfd == EFECTO_EXCLUYE
                   else EfectoDeDurabilidad.AVISA),
                  "suelo agresivo segun AASHTO LRFD 11.10.6.4.2a (criterio "
                  "de refuerzos de acero galvanizado enterrados, aplicado "
                  "por analogia): " + "; ".join(motivos_lrfd)
                  + (". La TMC galvanizada no es candidata en este punto "
                     f"(criterio '{CRITERIO_EFECTO_SUELO_AGRESIVO}' [A] = "
                     f"'{EFECTO_EXCLUYE}')" if efecto_lrfd == EFECTO_EXCLUYE
                     else ". La TMC sigue candidata: la analogia avisa y no "
                          f"excluye (criterio "
                          f"'{CRITERIO_EFECTO_SUELO_AGRESIVO}' [A] = "
                          f"'{EFECTO_AVISO}')"),
                  ("AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO",
                   "AASHTO_LRFD_9.11.12.8#AGRESIVO",
                   "AASHTO_LRFD_9.10.7.5#INDICATIVOS"),
                  CRITERIO_SUELO_AGRESIVO)
        pasos.append(paso(
            "F3.DUR.SUELO_AGRESIVO", codigo=CODIGO_DURABILIDAD,
            que="Durabilidad: agresividad del suelo para el acero "
                "galvanizado, por analogia con los refuerzos enterrados",
            formula="pH en el intervalo, resistividad sobre el minimo, "
                    "cloruros y sulfatos bajo el maximo; basta incumplir "
                    "uno",
            citas_textuales=("AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO",
                             "AASHTO_LRFD_9.11.12.8#AGRESIVO",
                             "AASHTO_LRFD_9.10.7.5#INDICATIVOS",
                             "EG2013.507.10"),
            sustitucion=tuple(
                Magnitud(nombre, valor, unidad, ensayos.origen_de(clave),
                         cifras=CIFRAS_FACTOR)
                for clave, valor, nombre, unidad in medidas
                if valor is not None),
            resultado=Magnitud(
                "criterios incumplidos",
                "; ".join(motivos_lrfd) or "ninguno", "",
                f"contraste con el criterio '{CRITERIO_SUELO_AGRESIVO}' [C]"),
            umbral=_umbral_de_cita(
                descripcion="suelo no agresivo para acero galvanizado "
                            "enterrado",
                valor=(f"pH {u['pH_min']:g} a {u['pH_max']:g}; resistividad "
                       f">= {u['resistividad_min_ohm_cm']:g} ohm-cm; "
                       f"cloruros <= {u['cloruros_max_ppm']:g} ppm; "
                       f"sulfatos <= {u['sulfatos_max_ppm']:g} ppm"),
                unidad="", cita_id="AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO",
                aplicacion="la fuente lo escribe para refuerzos de muros de "
                           "suelo reforzado; aqui se aplica por analogia al "
                           "tubo de acero corrugado galvanizado, y su "
                           "efecto lo fija el criterio "
                           f"'{CRITERIO_EFECTO_SUELO_AGRESIVO}' [A]",
                criterio=CRITERIO_SUELO_AGRESIVO),
            veredicto=Veredicto(
                tipo=(TipoDeVeredicto.NO_CUMPLE if agresivo
                      else TipoDeVeredicto.CUMPLE),
                explicacion=(
                    "suelo no agresivo para el acero galvanizado segun el "
                    "criterio adoptado" if not agresivo else
                    "suelo agresivo: la TMC galvanizada queda fuera de los "
                    "candidatos" if efecto_lrfd == EFECTO_EXCLUYE else
                    "suelo agresivo: la TMC sigue candidata, con aviso y "
                    "con la proteccion que exige EG-2013 507.10")),
        ))

    # ---- EG-2013 507.10, la mitad de los SUELOS (H5) --------------------------
    # La clausula tiene dos disparadores: el pH del agua (arriba) y «que los
    # suelos circundantes presenten sustancias agresivas», que la norma no
    # cuantifica. LECTURA DEL PROYECTO, declarada en el texto de la regla y
    # en el fundamento F3.DUR.SUELO_AGRESIVO: cuentan como tales los
    # sulfatos por encima de la exposicion insignificante de E.060 Tabla
    # 4.4 y un suelo agresivo segun los criterios de arriba.
    con_sulfatos = (exposicion_sulfatos is not None
                    and exposicion_sulfatos != SULFATOS[0]["exposicion"])
    if tmc in candidatos and (con_sulfatos or motivos_lrfd):
        causas = []
        if con_sulfatos:
            causas.append(f"exposicion a sulfatos '{exposicion_sulfatos}' "
                          "(E.060 Tabla 4.4)")
        if motivos_lrfd:
            causas.append("suelo agresivo segun los criterios de AASHTO "
                          "LRFD 11.10.6.4.2a adoptados por analogia")
        regla("suelo_agresivo", tmc, EfectoDeDurabilidad.EXIGE,
              "suelos circundantes con sustancias agresivas ("
              + "; ".join(causas) + "): la especificacion de la TMC tiene "
              f"que incluir la proteccion de la tuberia "
              f"({NUMERAL_PH_MIN_TMC}); el producto y el procedimiento son "
              "del proyecto. LECTURA DEL PROYECTO: la norma no dice que "
              "sustancias ni en que cantidad; se leen como agresivas las "
              "dos escalas numericas disponibles",
              ("EG2013.507.10",))

    return DictamenDurabilidad(
        aplicada=True, reglas=tuple(reglas) + reglas_suelo,
        pasos=tuple(pasos) + pasos_suelo, ensayos=ensayos,
        suelo_fundacion=linea_suelo)


def _fila_de_sulfatos(so4_suelo_pct: Optional[float],
                      so4_agua_ppm: Optional[float]) -> dict:
    """
    La fila de la Tabla 4.4 de E.060 (`constantes_normativas.SULFATOS`) que
    alcanza el ensayo; con las dos escalas, la MAS exigente.

    ES LA MISMA REGLA que `M9.clase_exposicion_sulfatos` aplica al dato de
    sitio 'exposicion_quimica_ems' para el recubrimiento del cabezal, escrita
    sobre la MISMA tabla y con el MISMO campo `limite_inferior_estricto` que
    cierra el borde de 2,0 %. No se importa de M9 para no hacer depender el
    catalogo de la Fase 3 del modulo de la Fase 9; `tests/
    test_t4_materiales_durabilidad.py` contrasta las dos sobre una malla para
    que no diverjan.
    """
    indice = 0
    for posicion, fila in enumerate(SULFATOS):
        estricto = fila["limite_inferior_estricto"]
        for medida, clave in ((so4_suelo_pct, "so4_suelo_pct"),
                              (so4_agua_ppm, "so4_agua_ppm")):
            if medida is None:
                continue
            minimo = fila[clave][0]
            if (medida > minimo) if estricto else (medida >= minimo):
                indice = max(indice, posicion)
    return SULFATOS[indice]
