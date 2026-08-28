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
'v_max_tmc' = 'v_max_hdpe' = 4.6 m/s [C] (WSDOT, Tabla 8-4);
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
Progresion 0.90 m (minimo normativo MTC, num. 4.1.1.3.4 a) + pasos de 0.15 m,
topada por material. Los dos numeros de la progresion viven en el criterio
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
sale de la Tabla N 09 (MANNING['concreto_recto']) y su velocidad maxima de
la Tabla N 10 (V_MAX['concreto']), ambas [N] en constantes_normativas.py.
TMC comparte fila de Tabla N 09 (MANNING['metal_corrugado']) pero no tiene
fila en la Tabla N 10: su velocidad maxima es el vacio 'v_max_tmc'. HDPE no
esta en ninguna de las dos tablas del Manual MTC: su n sale del criterio
'n_manning_hdpe' (rango completo por analogia, [A]) y su velocidad maxima
del vacio 'v_max_hdpe'.

Familia C queda sin candidatos
-------------------------------
Sec. 2.3 (recogido en M1_clasificacion.PERFILES) dice que la Familia C usa
"seccion: marco o multicelda", no un conducto circular. El catalogo de este
modulo es exclusivamente de conductos circulares (Material.D es un diametro),
de modo que `materiales_candidatos()` devuelve la tupla vacia para un punto
de Familia C: no es que ningun material circular pase el filtro, es que la
pregunta de conducto circular no aplica a esa familia.

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
    from modulos.M2_material import catalogo, materiales_candidatos, siguiente_diametro

    candidatos = materiales_candidatos(punto)            # () en Familia C
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    D = siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO)   # 0.90
    D = siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, D)  # 1.05
"""

from __future__ import annotations

from typing import Any, Optional, Tuple, Union

import criterios_adoptados as ca
from constantes_normativas import (HDS5_INLET, H_RELLENO_MIN, MANNING,
                                   SECCION_EG2013, V_MAX)
from modelos import (ConstantesHDS5, DatoInvalidoError, Familia, Material,
                     PuntoCritico, TipoMaterial)
from tolerancias import TOL_UMBRAL_NORMATIVO

NUMERAL_CATALOGO = "Sec. 3.2"     # nuevo en v7, sin numeral MTC propio
NUMERAL_MATERIAL = "Sec. 3.4"

CRITERIO_DIAMETROS = "diametros_normalizados"
CRITERIO_D_MAX_CATALOGO = "D_max_catalogo"
CRITERIO_ESPESOR_PARED = "espesor_pared_conducto"
CRITERIO_N_MANNING_HDPE = "n_manning_hdpe"
CRITERIO_HDS5_HDPE = "hds5_embocadura_hdpe"
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
_NORMA_PRODUCTO = {
    TipoMaterial.CONCRETO_REFORZADO: "ASTM C76 / AASHTO M170",
    TipoMaterial.TMC: "AASHTO M36 / ASTM A760",
    TipoMaterial.HDPE: "AASHTO M294",
}

# Claves de MANNING (Tabla N 09) y de HDS5_INLET (Tabla A.1) que si tienen
# fila normativa directa: HDPE no esta en ninguna de las dos tablas del
# Manual MTC y por eso no aparece en estos dos dicts (usa criterio adoptado).
_MANNING_CLAVE = {
    TipoMaterial.CONCRETO_REFORZADO: "concreto_recto",
    TipoMaterial.TMC: "metal_corrugado",
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

def espesor_pared(material: Material) -> float:
    """
    t, espesor de pared del conducto, m ('espesor_pared_conducto', [A]).

    Se detiene con `CriterioPendienteError` mientras el criterio siga vacio.
    Aqui es donde el vacio bloquea, no en `catalogo()`: el catalogo tiene que
    poder listarse aunque el espesor no este declarado (ver "Campos que el
    catalogo puede dejar en None" en el docstring del modulo), y el bloqueo
    salta en el punto donde el numero hace falta de verdad.
    """
    if material.espesor_pared is None:
        ca.valor(CRITERIO_ESPESOR_PARED)      # CriterioPendienteError
        raise AssertionError(
            f"inalcanzable mientras '{CRITERIO_ESPESOR_PARED}' este vacio"
        )
    ca.valor(CRITERIO_ESPESOR_PARED)          # registra el uso para M11
    return material.espesor_pared


def diametro_exterior(*, material: Material, D: float) -> float:
    """
    D_ext = D + 2*t, m: el diametro EXTERIOR del conducto.

    `D` es el diametro interior -- el hidraulico, el que entra en Manning y en
    `modelos.Geometria` -- y `D_ext` es el que gobierna todo lo que toca al
    terreno: el Bc del Art. 12.6.6.3 de AASHTO LRFD (cobertura minima), el
    volumen desplazado de la subpresion de V7 (num. 2.4.3.8.2 del Manual de
    Puentes) y la posicion de la clave fisica. Confundirlos es MAT-D3 y
    MAT-D4: los dos quedaban del lado inseguro por el mismo motivo.

    Se detiene con `CriterioPendienteError` mientras 'espesor_pared_conducto'
    siga vacio (ver `espesor_pared`).
    """
    return D + 2 * espesor_pared(material)


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


# ---------------------------------------------------------------------------
# Sec. 3.4 - Catalogo de material
# ---------------------------------------------------------------------------

def catalogo(material: MaterialLike) -> Material:
    """
    Reune en un `Material` todo lo que la Fase 4 y la Fase 5 necesitan de ese
    material: doble n de Manning, tope de diametro (Sec. 3.2), constantes
    HDS-5 de control de entrada (Sec. 4.2), rango de velocidad maxima
    (Tabla N 10 o el vacio que la sustituye), relleno minimo sobre la clave
    (Sec. 7.A) y seccion de EG-2013 para el presupuesto.

    v_max_rango, espesor_pared y la doble n del HDPE pueden salir en None si
    su criterio se vacia: se leen con `_valor_si_declarado()`, no con
    `ca.valor()` ni con `ca.criterio()`. Ver "Campos que el catalogo puede
    dejar en None" en el docstring del modulo, incluida la excepcion de
    'n_manning_hdpe'.

    `h_relleno_min_eg2013` NO es de esa familia aunque tambien sea Optional:
    su None no es un vacio pendiente sino el hecho normativo de que EG-2013
    fija la altura minima de relleno solo para HDPE. Nadie lo declarara nunca.
    """
    tipo = _tipo_material(material)

    if tipo is TipoMaterial.HDPE:
        n_min, n_max = _valor_si_declarado(CRITERIO_N_MANNING_HDPE)
        hds5 = ConstantesHDS5.desde_dict(ca.valor(CRITERIO_HDS5_HDPE))
    else:
        n_min, n_max = MANNING[_MANNING_CLAVE[tipo]]
        hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[_HDS5_CLAVE[tipo]])

    if tipo in _V_MAX_CLAVE:
        v_max_rango = V_MAX[_V_MAX_CLAVE[tipo]]
    else:
        v_max_rango = _valor_si_declarado(CRITERIO_V_MAX[tipo])

    espesores = _valor_si_declarado(CRITERIO_ESPESOR_PARED)

    return Material(
        tipo=tipo,
        nombre=_NOMBRE[tipo],
        n_min=n_min,
        n_max=n_max,
        D_max=_topes()[tipo.value],
        D_max_de_catalogo=ca.criterio(CRITERIO_D_MAX_CATALOGO).de_catalogo,
        norma_producto=_NORMA_PRODUCTO[tipo],
        hds5=hds5,
        v_max_rango=v_max_rango,
        # [N] directo de EG-2013 508.07 y SOLO para HDPE: los otros dos
        # materiales no tienen minimo en el EG-2013, y su None significa eso.
        h_relleno_min_eg2013=H_RELLENO_MIN[_EG2013_CLAVE[tipo]],
        espesor_pared=None if espesores is None else espesores[tipo.value],
        seccion_eg2013=SECCION_EG2013[tipo.value],
    )


# ---------------------------------------------------------------------------
# Filtro de candidatos
# ---------------------------------------------------------------------------

def materiales_candidatos(punto: PuntoCritico) -> Tuple[Material, ...]:
    """
    Materiales candidatos para el punto, ANTES de dimensionar (Sec. 3.2 +
    Sec. 3.4). No elige uno: entrega el catalogo completo de los que tienen
    sentido para la familia del punto.

    Familia C queda con la tupla vacia: su seccion es marco o multicelda
    (Sec. 2.3), no un conducto circular, y este catalogo no cubre esa forma.
    """
    if punto.familia is Familia.C:
        return ()
    return tuple(catalogo(tipo) for tipo in TipoMaterial)
