"""
MD.py
=====
Orquestador del bucle de diseño: la Fase 4 y la Fase 5 recorridas en el orden
que fija la guia de sesiones (Sec. 2), para un punto critico.

    para cada material candidato de M2 (Sec. 3.4)
        para cada diametro del catalogo, en orden ascendente (Sec. 3.2)
            M3  tirante normal por Manning          (Sec. 4.1)
            M4  control de entrada y de salida      (Sec. 4.2 / 4.3)
            M5  verificaciones                      (Fase 5)
            si TODAS cumplen -> ese es el diseño del punto
        si se agoto el catalogo -> "material descartado por diametro requerido"
    si ningun material llego a cumplir -> DisenoNoFactibleError

`disenar_lote(puntos, ...)` corre `disenar_punto` sobre cada fila del CSV,
captura los fallos por-punto como `ResultadoPunto(aceptado=False)` y devuelve
la lista completa en el orden de la entrada: M11 puede listar aceptados y
fallidos sin haber perdido ninguno.

Devuelve el primer `ResultadoPunto` aceptado: el diametro MAS CHICO del
material MAS ALTO en la lista de candidatos de M2 que pasa la Fase 5 entera.
No compara materiales entre si ni busca "el mejor" -- la eleccion final de
material combina defendibilidad, durabilidad (Sec. 3.3) y estructural
(Fase 8), y Sec. 3.4 no la reduce a un orden de preferencia. Este bucle
entrega el primero que cumple; quien quiera los tres para compararlos llama a
`disenar_material()` una vez por material.

Lo que MD NO hace
-----------------
- No verifica nada por su cuenta. Lee `Verificacion.cumple` y no reinterpreta
  ninguna: si una verificacion es incorrecta, se corrige en M5.
- No calcula L ni TW. La longitud del conducto (ancho de plataforma +
  proyeccion de taludes, afectada por el esviaje) es Fase 7 / 7.B, y el TW es
  el criterio pendiente 'TW_receptor' (Tablero 3.1) o su calculo por Manning
  en el receptor. MD los EXIGE como argumentos en vez de derivarlos: la hoja
  de ruta no da la regla de taludes ni el TW, y rellenar ese vacio en silencio
  aqui contaminaria todo el bucle. Ambos llegan en metros, SI.
- No calcula el delta de rasante. `DisenoNoFactibleError.delta_rasante_m` sale
  vacio a proposito: "no factible -> subir rasante X cm" es el tamizado de
  7.A, que fija la rasante ANTES del bucle y no desde dentro (el acoplamiento
  circular rasante -> subrasante -> CBR -> resguardo -> V4 -> rasante se corta
  ahi, Sec. 7.A). MD reporta el motivo; el delta lo pone
  `modulos.M7_geometria.tamizado_rasante`, que lo devuelve en
  `TamizadoRasante.delta_rasante_cm` sin necesidad de excepcion.
- No fabrica la Verificacion V9 (disponibilidad de diametro). El descarte por
  tope de CATALOGO y V9 son el MISMO hecho, y quien lo declare como
  `Verificacion` con su criterio es M5, que ya recibe D y `material.D_max`.
  MD lo reporta como texto en el motivo de descarte, no como verificacion.
  Ese tope NO es normativo: sale del criterio 'D_max_catalogo' [A] y las
  normas de producto a las que se le atribuia no lo sostienen (NOR-PRO-01,
  NOR-PRO-02). El motivo de descarte lo dice con esas palabras.
- No itera puntos. El bucle exterior "para cada punto" no esta aqui porque
  cada punto entra con su L y su TW propios (arriba) y porque la hoja de ruta
  no declara que hacer con el lote cuando UN punto sale no factible: si aborta
  el expediente o si continua y lo lista aparte es una decision de la GUI y de
  M11, no un default que este modulo pueda inventar.

Interfaz con M5 -- supuesto de arquitectura, no valor de proyecto
------------------------------------------------------------------
ESTE PARRAFO ABRIA CON "M5 todavia no existe en el repositorio" Y ESA PREMISA
CADUCO (SIS-A-08): `src/modulos/M5_verificaciones.py` existe desde hace varias
sesiones y esta cubierto por su propia suite. El Protocol y la importacion
perezosa de abajo SIGUEN siendo la forma correcta, pero por otra razon, y
decirla importa porque la razon vieja invitaba a borrarlos en cuanto M5
apareciera:

    MD no depende de M5 porque M5 falte, sino porque MD es el ORQUESTADOR y no
    debe conocer la implementacion de lo que orquesta. La inyeccion por
    argumento es lo que permite a un test pasarle un doble, a la GUI pasarle
    una version instrumentada y a una sesion futura sustituir M5 sin tocar
    este archivo. La importacion perezosa evita ademas un ciclo de importacion
    en el arranque.

Lo que MD fija es la unica pieza que un orquestador esta obligado a fijar: la
FIRMA con la que llama a M5.

    verificar(punto=..., material=..., D=..., resultado=...) -> Sequence[Verificacion]

Se pasa siempre por palabra clave, para que M5 pueda ampliar la firma sin
romper este archivo. La funcion se toma del argumento `verificar`; si no se
pasa, MD la importa de `modulos.M5_verificaciones.verificar`, y si esa
importacion fallara la ausencia sale como ImportError -- un fallo de programa, no
del expediente, y por eso fuera de ErrorProyecto (misma regla que
FileNotFoundError). Que M5 devuelva CERO verificaciones no es un diseño
aceptado: es ValueError, porque un punto aceptado sin verificaciones no es
defendible en la memoria.

Ninguno de estos nombres es un valor de proyecto: MD no lee
`criterios_adoptados` ni `constantes_normativas` en ninguna linea. Todo numero
del bucle -- el 0.90 inicial, el paso de 0.15, los topes por material -- entra
por M2 desde el criterio 'diametros_normalizados'.

El mensaje de descarte
----------------------
`MENSAJE_DIAMETRO_SUPERADO` es textual y no se parafrasea: la hoja de ruta lo
fija en el Anexo B ("Superado el tope: devolver 'material descartado por
diametro requerido'") y M2 ya documenta que ese es el sentido de su
`siguiente_diametro() -> None`. MD es quien lo emite.

Excepciones
-----------
    DisenoNoFactibleError   ningun material candidato cumple, con el motivo
                            del ultimo fallo de CADA material; o M2 no ofrece
                            candidatos (Familia C, Sec. 2.3).
    DatoFaltanteError       el punto no trae Q ni S y no se pasaron como
                            argumento (llega desde `PuntoCritico.exigir`).
    DatoInvalidoError       llega desde M3 / M4: un dato que no puede ser.
    CriterioPendienteError  llega desde M2 o M4: un criterio [A] sin valor.

Uso
---
    from modulos.MD import disenar_punto

    resultado = disenar_punto(punto, L=24.0, TW=0.30)
    resultado.material.nombre, resultado.D, resultado.verificaciones
"""

from __future__ import annotations

from importlib import import_module
from typing import (Callable, List, Optional, Protocol, Sequence, Tuple,
                    Iterable)

from modelos import (CriterioPendienteError, DisenoNoFactibleError,
                     ErrorProyecto, Familia, Material,
                     PasoDiseno, PuntoCritico, ResultadoHidraulico,
                     ResultadoPunto, Verificacion)
from modulos.M2_material import materiales_candidatos, siguiente_diametro
from modulos.M3_hidraulica import resolver_manning
from modulos.M4_control import resolver_control

NUMERAL_BUCLE = "Sec. 2 de la guia de sesiones (Fases 4 y 5)"

MENSAJE_DIAMETRO_SUPERADO = "material descartado por diámetro requerido"

MODULO_VERIFICACIONES = "modulos.M5_verificaciones"
FUNCION_VERIFICACIONES = "verificar"


class Verificador(Protocol):
    """
    Firma con la que MD llama a la Fase 5. Ver "Interfaz con M5" en el
    docstring del modulo: es un supuesto de arquitectura declarado, no un
    valor de proyecto.
    """

    def __call__(self, *, punto: PuntoCritico, material: Material, D: float,
                 resultado: ResultadoHidraulico) -> Sequence[Verificacion]:
        ...


# Observador opcional del bucle: recibe un PasoDiseno por escalon probado.
# No participa del diseño -- no puede cambiar el resultado ni detenerlo -- y
# existe solo para que M11 publique las iteraciones (Fase 11, entregable 1).
# Sin observador, MD se comporta exactamente igual que antes.
Registrador = Callable[[PasoDiseno], None]


def _registrar(registrador: Optional[Registrador], material: Material,
               D: float, *, aceptado: bool, motivo: str,
               verificaciones: Tuple[Verificacion, ...] = (),
               resultado: Optional[ResultadoHidraulico] = None) -> None:
    """Anota un escalon del bucle si hay observador; si no, no hace nada."""
    if registrador is None:
        return
    registrador(PasoDiseno(material=material.nombre, D=D, aceptado=aceptado,
                           motivo=motivo, verificaciones=verificaciones,
                           resultado_hidraulico=resultado))


# ---------------------------------------------------------------------------
# Resolucion de la funcion de verificacion
# ---------------------------------------------------------------------------

def _verificador_de_M5() -> Verificador:
    """
    Importa `modulos.M5_verificaciones.verificar`. Un M5 ausente o sin esa
    funcion es un fallo de PROGRAMA -- falta un modulo del script, no un dato
    del expediente -- y por eso sale como ImportError y no como ErrorProyecto:
    la GUI no debe mostrarlo como "falta declarar" ni como "no factible".
    """
    try:
        modulo = import_module(MODULO_VERIFICACIONES)
    except ImportError as exc:
        raise ImportError(
            f"'{MODULO_VERIFICACIONES}' no esta en el proyecto: MD no puede "
            "cerrar el bucle de diseño sin la Fase 5. Mientras M5 no exista, "
            "pasa la funcion de verificacion en el argumento 'verificar' de "
            f"disenar_punto() con la firma {FUNCION_VERIFICACIONES}"
            "(punto=, material=, D=, resultado=) -> Sequence[Verificacion]"
        ) from exc

    verificar = getattr(modulo, FUNCION_VERIFICACIONES, None)
    if verificar is None:
        raise ImportError(
            f"'{MODULO_VERIFICACIONES}' no expone '{FUNCION_VERIFICACIONES}': "
            "MD llama a la Fase 5 por ese nombre y con la firma "
            "(punto=, material=, D=, resultado=) -> Sequence[Verificacion]"
        )
    return verificar


# ---------------------------------------------------------------------------
# Redaccion de los motivos de fallo
# ---------------------------------------------------------------------------

def _motivo_sin_flujo_libre(D: float, Q: float, S: float,
                            material: Material) -> str:
    """
    M3 devolvio None: no hay tirante normal en (0, 2*pi) para esa D. No es un
    fallo -- es el resultado de diseño "este diametro no alcanza" (Sec. 4.1).
    """
    return (f"D = {D:.2f} m: el conducto no transporta Q = {Q:.4f} m3/s en "
            f"flujo libre con S = {S:.5f} y n = {material.n_para_capacidad} "
            "(Sec. 4.1)")


def _motivo_incumplimiento(D: float,
                           verificaciones: Sequence[Verificacion]) -> str:
    """Las verificaciones que no cumplen, con su codigo y su numeral."""
    partes = [
        f"{v.codigo or 'sin codigo'} ({v.numeral}) obtenido {v.valor_obtenido!r} "
        f"frente a {v.valor_admisible!r}"
        for v in verificaciones if not v.cumple
    ]
    return f"D = {D:.2f} m: incumple " + "; ".join(partes)


def _motivo_escalon_fallido(D: float, exc: ErrorProyecto) -> str:
    """
    Un escalon que termino en ErrorProyecto en vez de en una verificacion.

    El sujeto de la frase es EL ESCALON, no el expediente: es MD quien eligio
    esta D del catalogo, de modo que "con D = 2.10 m no se pudo evaluar" es un
    hecho del bucle, y el mensaje de la excepcion queda detras como la causa
    que lo explica. Sin el prefijo, un DatoInvalidoError sobre 'cota_subrasante'
    lanzado por V7 se lee como "el dato del expediente esta mal" cuando lo que
    ocurrio es que la clave del conducto, A ESTE DIAMETRO, ya no cabe bajo la
    subrasante -- el dato no cambio, cambio la D que el bucle estaba probando.

    MD no reinterpreta la excepcion ni la reclasifica: la cita entera, con su
    tipo. Corregir el tipo o el campo de la excepcion es de M5, no de aqui.
    """
    return (f"D = {D:.2f} m: el escalon no se pudo evaluar -- "
            f"{type(exc).__name__}: {exc}")


def _motivo_material_fallido(exc: ErrorProyecto) -> str:
    """
    El material completo se cae porque uno de sus escalones lanzo. No es
    "descartado por diametro requerido" (Anexo B) -- ese mensaje es para el
    catalogo agotado bajo el tope -- ni es un incumplimiento de la Fase 5: es
    un material que no se pudo terminar de evaluar, y se declara asi.
    """
    return f"material no evaluable: {type(exc).__name__}: {exc}"


def _motivo_descarte(material: Material, ultimo_motivo: str) -> str:
    """
    El material se quedo sin catalogo: se agoto la progresion de Sec. 3.2 bajo
    el tope de CATALOGO del material. Lleva el mensaje textual del Anexo B y,
    detras, el ultimo fallo concreto -- el mensaje solo dice que no hay tubo
    mas grande; el motivo dice por que hacia falta uno.

    El tope se cita como lo que es: una adopcion del proyecto sobre la
    disponibilidad ('D_max_catalogo'), NO la norma de producto. Este mensaje
    decia "segun {norma_producto}" y esa atribucion es falsa -- A760 tabula
    hasta 3600 mm y M 170M tambien (NOR-PRO-01, NOR-PRO-02) --, de modo que
    un punto descartado aqui parecia rechazado por la norma cuando lo rechaza
    el catalogo adoptado.
    """
    return (f"{MENSAJE_DIAMETRO_SUPERADO} (tope de catalogo adoptado "
            f"{material.D_max:.2f} m, criterio 'D_max_catalogo'; NO es un "
            f"tope de {material.norma_producto}). Ultimo intento: "
            f"{ultimo_motivo}")


# ---------------------------------------------------------------------------
# Bucle interior: un material, el catalogo ascendente
# ---------------------------------------------------------------------------

def disenar_material(punto: PuntoCritico, material: Material, *,
                     Q: float, S: float, L: float, TW: float,
                     verificar: Verificador,
                     registrar: Optional[Registrador] = None
                     ) -> Tuple[Optional[ResultadoPunto], str]:
    """
    Recorre el catalogo de Sec. 3.2 para UN material, de menor a mayor, y
    devuelve el par (resultado, motivo):

        (ResultadoPunto aceptado, "")   el primer diametro que pasa la Fase 5
        (None, motivo de descarte)      se agoto el catalogo bajo el tope

    En cada escalon llama a M3 (tirante normal, Sec. 4.1), a M4 (controles de
    entrada y salida, Sec. 4.2 y 4.3) y a M5 (Fase 5), en ese orden. El
    tirante normal se resuelve aqui y se le inyecta a M4 para no repetir
    Brent, y para poder distinguir en el motivo el escalon que ni siquiera
    transporta Q de aquel que lo transporta pero incumple una verificacion.

    Queda publica porque el bucle exterior no es el unico consumidor: correr
    los tres materiales y comparar sus diseños -- para la memoria de Sec. 3.4,
    que exige defender la eleccion -- es llamar a esta funcion tres veces.

    `registrar` es un observador opcional: recibe un `PasoDiseno` por cada
    escalon probado, en orden. Es lo que M11 necesita para publicar las
    iteraciones (Fase 11, entregable 1). No altera el diseño ni el retorno.
    """
    D = siguiente_diametro(material.tipo)     # primer escalon: minimo normativo
    ultimo_motivo = "el catalogo no ofrecio ningun diametro"

    while D is not None:
        # Fuera del `try` a proposito: si la Fase 5 revienta, el escalon que
        # revento tiene que quedar en la traza CON la hidraulica que M3 y M4
        # si alcanzaron a resolver. Es lo unico que llega a la memoria cuando
        # ningun punto cierra, que es el estado de este expediente mientras
        # V5 siga sin `ancho_derecho_via_m` (§4.4, y la leccion de
        # NOR-MEM-01: el codigo lo calcula y el producto no lo muestra).
        resultado = None
        try:
            normal = resolver_manning(D=D, Q=Q, S=S, material=material)

            if normal is None:
                ultimo_motivo = _motivo_sin_flujo_libre(D, Q, S, material)
                _registrar(registrar, material, D, aceptado=False,
                           motivo=ultimo_motivo)
            else:
                # No puede salir None: se le pasa el tirante normal ya
                # resuelto, y ese es el unico caso en que M4 devuelve None.
                resultado = resolver_control(D=D, Q=Q, S=S, L=L, TW=TW,
                                             material=material, normal=normal)
                verificaciones = tuple(verificar(punto=punto,
                                                 material=material,
                                                 D=D, resultado=resultado))
                if not verificaciones:
                    raise ValueError(
                        f"la Fase 5 devolvio cero verificaciones para "
                        f"{punto.id} con {material.nombre} D = {D:.2f} m: un "
                        "punto aceptado sin verificaciones no es defendible "
                        "en la memoria"
                    )

                if all(v.cumple for v in verificaciones):
                    _registrar(registrar, material, D, aceptado=True,
                               motivo="", verificaciones=verificaciones,
                               resultado=resultado)
                    return ResultadoPunto(
                        punto=punto,
                        material=material,
                        D=D,
                        resultado_hidraulico=resultado,
                        verificaciones=verificaciones,
                        aceptado=True,
                    ), ""

                ultimo_motivo = _motivo_incumplimiento(D, verificaciones)
                _registrar(registrar, material, D, aceptado=False,
                           motivo=ultimo_motivo,
                           verificaciones=verificaciones,
                           resultado=resultado)
        except ErrorProyecto as exc:
            # El escalon probado queda en la traza ANTES de que la excepcion
            # siga subiendo: un escalon que revento es parte de lo que se
            # intento, y la memoria de un punto que no cerro es justamente la
            # que hay que publicar entera. Solo ErrorProyecto: un ValueError o
            # un ImportError es un fallo de programa y sube sin anotarse.
            # Las verificaciones que la Fase 5 SI alcanzo a evaluar viajan
            # dentro de la excepcion. Sin ellas, un escalon que revento en V5
            # --- que en este expediente son todos --- llegaba a la memoria
            # como un motivo de una linea, tirando el desarrollo de V1 a V4b
            # que si se calculo. Ver el docstring de `M5.verificar`.
            _registrar(registrar, material, D, aceptado=False,
                       motivo=_motivo_escalon_fallido(D, exc),
                       verificaciones=getattr(
                           exc, "verificaciones_completadas", ()),
                       resultado=resultado)
            raise

        D = siguiente_diametro(material.tipo, D)

    return None, _motivo_descarte(material, ultimo_motivo)


# ---------------------------------------------------------------------------
# Bucle exterior: un punto, los materiales candidatos
# ---------------------------------------------------------------------------

def disenar_punto(punto: PuntoCritico, *, L: float, TW: float,
                  Q: Optional[float] = None, S: Optional[float] = None,
                  verificar: Optional[Verificador] = None,
                  registrar: Optional[Registrador] = None) -> ResultadoPunto:
    """
    Diseño hidraulico completo de un punto critico: recorre los materiales
    candidatos de M2 (Sec. 3.4) y, dentro de cada uno, el catalogo ascendente
    de Sec. 3.2, hasta que un par (material, D) pase TODAS las verificaciones
    de la Fase 5. Devuelve ese `ResultadoPunto`.

    Argumentos
    ----------
    L   m   longitud del conducto. Es dato: la calcula la Fase 7 (7.B, ancho
            de plataforma + proyeccion de taludes, afectada por el esviaje).
    TW  m   tirante en el cuerpo receptor sobre el fondo de la SALIDA, no una
            cota. Criterio 'TW_receptor' (Tablero 3.1); quien lo pase declara
            con que escenario lo obtuvo. TW = 0 es salida libre.
    Q   m3/s  caudal de diseño. Por defecto `punto.exigir("Q_m3s")`, que lanza
            DatoFaltanteError si la fila lo trajo vacio. Se admite explicito
            porque el caudal de las Familias B y C no sale de esa columna
            (Sec. 2.3): B es el del drenaje longitudinal y C el del canal.
    S   m/m pendiente del conducto. Por defecto la del cauce,
            `punto.exigir("S_cauce")`: Sec. 7.B fija que la pendiente de la
            alcantarilla es la del cauce y que V2 nunca la restringe (Sec. 5.2).
    verificar   funcion de la Fase 5. Por defecto, la de M5 (ver el docstring
            del modulo).
    registrar   observador opcional del bucle (ver `disenar_material`). Recibe
            los escalones de TODOS los materiales recorridos, en orden, tambien
            cuando la llamada termina en DisenoNoFactibleError: la traza de un
            punto que no cerro es justamente la que hay que publicar.

    Lanza DisenoNoFactibleError si todos los materiales candidatos SE
    EVALUARON y ninguno cumple, con el motivo del ultimo fallo de cada uno --
    nunca un resultado silencioso ni un diametro fuera de catalogo.
    `delta_rasante_m` sale vacio: ese numero es del tamizado de 7.A, no de
    este bucle.

    Un material que lanza ErrorProyecto a mitad del catalogo no mata el punto:
    se descarta como material, con su causa citada entera en el motivo, y el
    bucle sigue con el siguiente candidato. Los escalones que reventaron
    quedan igualmente en la traza de `registrar`.

    Distincion entre BLOQUEADO y NO FACTIBLE
    ----------------------------------------
    Si algun candidato quedo bloqueado por un criterio vacio, sale
    `CriterioPendienteError` y no `DisenoNoFactibleError` -- incluido el caso
    mixto y el caso en que un candidato posterior si cerro. Ver
    `_exigir_criterios_declarados`, que es donde esta el fundamento.

    PENDIENTE DELIBERADO (fuera del alcance de la tarea que introdujo esto):
    cuando cada material se detiene en un criterio vacio DISTINTO, solo la
    primera clave viaja como excepcion, porque `CriterioPendienteError` lleva
    una sola `clave`. Las demas quedan en la traza de `PasoDiseno` y en las
    'iteraciones' del informe, pero no como filas estructuradas del bloque de
    pendientes de M11 ni como avisos "falta declarar" de la GUI. Exponer las
    tres exige un campo nuevo en modelos.py -- una excepcion que admita varias
    claves -- y eso toca la taxonomia de excepciones, que se decide aparte.
    """
    if verificar is None:
        verificar = _verificador_de_M5()

    Q = punto.exigir("Q_m3s") if Q is None else Q
    S = punto.exigir("S_cauce") if S is None else S

    candidatos = materiales_candidatos(punto)
    if not candidatos:
        raise DisenoNoFactibleError(
            motivo=_motivo_sin_candidatos(punto), id_punto=punto.id)

    fallos: List[str] = []
    pendientes: List[CriterioPendienteError] = []

    for material in candidatos:
        try:
            resultado, motivo = disenar_material(
                punto, material, Q=Q, S=S, L=L, TW=TW, verificar=verificar,
                registrar=registrar)
        except CriterioPendienteError as exc:
            # Bloqueo, no descarte: este material no se evaluo, y "no se
            # evaluo" no es "no cumple". Se anota aparte de `fallos` porque
            # decide que excepcion sale del punto (ver mas abajo).
            fallos.append(f"{material.nombre}: {_motivo_material_fallido(exc)}")
            pendientes.append(exc)
            continue
        except ErrorProyecto as exc:
            # Un material que revienta se descarta COMO MATERIAL y el bucle
            # sigue con el siguiente candidato. Antes la excepcion subia hasta
            # el llamador y mataba el punto entero, de modo que un fallo del
            # PRIMER candidato dejaba a los otros dos sin intentarse siquiera:
            # el punto salia "no evaluable" cuando podia tener diseño con otro
            # material. El motivo queda citado entero, con su tipo.
            fallos.append(f"{material.nombre}: {_motivo_material_fallido(exc)}")
            continue

        if resultado is not None:
            # Un candidato cerro. Si ALGUNO de los anteriores -- todos ellos
            # mas preferentes en el orden de M2 -- quedo bloqueado por un
            # criterio vacio, el punto NO esta diseñado: estaria eligiendo
            # este material por descarte de otro que nunca se llego a evaluar,
            # y la memoria no podria defender la eleccion de Sec. 3.4.
            _exigir_criterios_declarados(pendientes)
            return resultado

        fallos.append(f"{material.nombre}: {motivo}")

    # Ningun candidato cerro. Antes de declarar el punto NO FACTIBLE hay que
    # poder afirmar que todos se evaluaron de verdad: ver la funcion.
    _exigir_criterios_declarados(pendientes)

    raise DisenoNoFactibleError(
        motivo="ningun material candidato cumple la Fase 5. " + " | ".join(fallos),
        id_punto=punto.id,
    )


def _exigir_criterios_declarados(
        pendientes: Sequence[CriterioPendienteError]) -> None:
    """
    Si algun material quedo BLOQUEADO por un criterio vacio, el punto esta
    bloqueado y sale ese `CriterioPendienteError`, no `DisenoNoFactibleError`.

    Los dos son estados distintos del expediente y se corrigen de forma
    distinta: "no factible" pide mover la rasante o cambiar de estructura;
    "falta declarar <clave>" pide una decision de proyectista. Y son
    incompatibles: `DisenoNoFactibleError` afirma que NINGUNA combinacion
    material/diametro cumple, y esa afirmacion no se puede sostener sobre un
    material que nunca se llego a evaluar. Decirlo igual seria rellenar un
    vacio en silencio con la forma de un diagnostico.

    Vale tambien para el caso MIXTO -- un material evaluado y rechazado, otro
    bloqueado -- y para el caso en que un material posterior SI cerro: ese
    cierre elige por descarte de un candidato mas preferente que nadie
    verifico.

    Solo viaja la primera clave. `CriterioPendienteError` lleva UNA `clave`, de
    modo que cuando cada material se detiene en un vacio distinto las demas no
    llegan a la GUI ni al bloque de
    pendientes de M11 como filas propias. (El ejemplo que traia este parrafo
    -- "'v_max_tmc' el TMC y 'v_max_hdpe' el HDPE" -- describia un estado ya
    superado: esos dos criterios tienen valor desde hace tiempo y en el CSV de
    ejemplo los tres materiales se detienen hoy en el mismo sitio. Se retira
    el ejemplo en vez de actualizarlo: cual es el primer vacio de cada
    material depende del expediente, y un ejemplo concreto vuelve a envejecer
    en silencio.) NO se pierden: quedan en la traza de
    `PasoDiseno` que recibe `registrar`, y de ahi en las 'iteraciones' del
    informe. Publicarlas las tres como filas estructuradas exige un campo nuevo
    en modelos.py -- una excepcion que lleve varias claves -- y queda pendiente
    a proposito, fuera del alcance de esta tarea.
    """
    if pendientes:
        raise pendientes[0]


def _motivo_sin_candidatos(punto: PuntoCritico) -> str:
    """M2 devolvio la tupla vacia. Hoy solo ocurre en Familia C (Sec. 2.3)."""
    motivo = (f"M2 (Sec. 3.4) no ofrece material candidato para la Familia "
              f"{punto.familia.value}")
    if punto.familia is Familia.C:
        motivo += (": Sec. 2.3 le asigna seccion de marco o multicelda, y el "
                   "catalogo de Sec. 3.2 es de conductos circulares. El punto "
                   "no es no-factible, es de otra forma de estructura")
    return motivo


# ---------------------------------------------------------------------------
# Lote de puntos: el bucle exterior del expediente
# ---------------------------------------------------------------------------

def _resultado_fallido(punto: PuntoCritico, exc: ErrorProyecto) -> ResultadoPunto:
    """
    Convierte una excepcion de proyecto en un ResultadoPunto no aceptado.

    El motivo lleva el tipo de excepcion y su mensaje: `DisenoNoFactibleError`
    y `DatoFaltanteError` son causas distintas del fallo y M11 debe poder
    distinguirlas en el reporte, sin tener que releer la excepcion original.
    """
    return ResultadoPunto(
        punto=punto,
        aceptado=False,
        motivo_rechazo=f"{type(exc).__name__}: {exc}",
    )


def disenar_lote(puntos: Iterable[PuntoCritico], *, L: float, TW: float,
                 Q: Optional[float] = None, S: Optional[float] = None,
                 verificar: Optional[Verificador] = None,
                 registrar: Optional[Registrador] = None,
                 ) -> List[ResultadoPunto]:
    """
    Diseño hidraulico del lote completo de un expediente: llama a
    `disenar_punto` por cada `PuntoCritico` y devuelve la lista de resultados
    en el MISMO ORDEN que la entrada, mezclando aceptados y fallidos.

    Los puntos que lanzan `ErrorProyecto` (no factible, dato faltante, dato
    invalido, criterio pendiente) se capturan y se convierten en un
    `ResultadoPunto(aceptado=False)` con el motivo explicito: el lote continua
    con el siguiente punto sin abortar. Un fallo de programa (ImportError,
    ValueError) SI se propaga, porque indica que el modulo esta incompleto.

    Cuando un criterio pendiente bloquea TODOS los puntos (p.ej. Q_m3s = None
    en toda la Familia A porque 'homogeneidad_serie_fen' esta vacio), la lista
    resultante tendra todos los puntos fallidos con CriterioPendienteError. Eso
    es informacion correcta: el bloqueo lo declara el criterio, no el lote.

    L, TW, Q, S y verificar se aplican a todos los puntos. Para puntos con
    geometria o caudal individualmente distintos -- lo habitual en la Fase 7 --
    llama a `disenar_punto` directamente, uno a uno, y ensambla la lista tu.

    `registrar` es el mismo observador de `disenar_punto` y aqui recibe los
    escalones de TODOS los puntos seguidos. Si necesitas la traza separada por
    punto -- que es lo que publica M11 -- recorre los puntos tu y dale a cada
    llamada su propio observador.

    Devuelve siempre una lista, vacia solo si `puntos` estaba vacio.
    """
    if verificar is None:
        verificar = _verificador_de_M5()

    resultados: List[ResultadoPunto] = []
    for punto in puntos:
        try:
            resultados.append(disenar_punto(punto, L=L, TW=TW, Q=Q, S=S,
                                            verificar=verificar,
                                            registrar=registrar))
        except ErrorProyecto as exc:
            resultados.append(_resultado_fallido(punto, exc))
    return resultados
