"""
variables_entrada.py
====================
El censo de TODO lo que el expediente tiene que traer, con el modo en que cada
cosa se resuelve. Sec. 4.3 del plan `docs/hoja_de_ruta_correcciones_v12.md`.

El problema que resuelve
------------------------
El repositorio mantiene TRES POBLACIONES separadas, y las separa bien:

    17  columnas del CSV        `modelos.PuntoCritico` / `M0_carga.COLUMNAS`
     7  datos de sitio          `datos_sitio.DATOS_SITIO`
    59  criterios adoptados     `criterios_adoptados.CRITERIOS`
    --
    83  variables de entrada

La frontera entre ellas es real y no se toca: una varia punto a punto, otra
vale para todo el corredor, la tercera es lo que el proyectista decidio donde
la norma calla. Lo que faltaba era la VISTA UNICA, porque quien llena el
expediente no ve tres poblaciones: ve "los datos que hay que llenar". Sin
ella la GUI tiene tres pestañas que no se pueden comparar y la memoria tres
bloques que no suman.

Y faltaba, sobre todo, el MODO DE RESOLUCION: como se llega al numero. Es lo
que le dice a la GUI QUE VENTANA ABRIR y a M11 QUE IMPRIMIR. Un campo
numerico con su dominio, una tabla entera con su numeral para elegir fila, un
rango con su semantica, un valor no editable con su derivacion, un campo con
trazabilidad obligatoria, o un catalogo de proveedor con su advertencia: son
seis ventanas distintas y hoy se pintaban todas igual.

Donde vive cada cosa
--------------------
El modo NO se declara aqui para las dos poblaciones que ya tienen archivo
propio: `Criterio.resolucion` y `DatoSitio.resolucion` lo llevan, junto al
valor que explican, y sus guardias lo exigen al importar. Este modulo declara
la resolucion SOLO de las 17 columnas del CSV, que no tienen otro sitio donde
vivir, y aporta lo que ninguna de las tres poblaciones tenia: unidad, fase
que la consume, dominio fisico y criterio que recibe la eleccion.

    resolucion (criterios)   ->  criterios_adoptados.py
    resolucion (sitio)       ->  datos_sitio.py
    resolucion (CSV)         ->  aqui
    unidad / fase / dominio  ->  aqui, para las tres

Los seis modos y como se elige uno estan documentados en `modelos.py`, junto
a los tipos. Aqui solo se aplica la escalera.

El reparto que resulta
----------------------
    libre        48    de_ensayo    18    de_tabla     13
    derivada      2    en_rango      1    de_catalogo   1

TRES LECTURAS DE ESE REPARTO, y ninguna es cosmetica:

1. `de_tabla` son 13 de 83 y podrian ser mas. Lo que lo impide no es el
   criterio de nadie: es que la tabla de la fuente NO ESTA TRANSCRITA en
   `src/normativa/`. El campo `Libre.tabla_pendiente` nombra, variable por
   variable, cual falta -- `variables_con_tabla_pendiente()` las lista --, de
   modo que el censo produce una lista de trabajo en vez de una excusa.

2. `en_rango` es UNO SOLO, y es el caso testigo de la §4.2 del plan:
   `v_max_concreto_eleccion`, cuya fila de la Tabla N 10 trae DOS MAXIMOS y
   ningun piso (NOR-HID-04). Que sea el unico no es un descuido: es que el
   registro tiene hoy rangos con semantica declarada en una sola tabla, y
   inventar los demas seria fabricar la cita que este proyecto viene
   retirando.

3. `de_catalogo` es UNO SOLO -- `D_max_catalogo` -- y ese es el modo que la
   §4.3 pedia crear (NOR-PRO-01, NOR-PRO-02).

Donde este censo se aparta de los EJEMPLOS de la Sec. 4.3
---------------------------------------------------------
El plan ilustra cada modo con ejemplos. Cuatro de ellos no sobreviven al
contraste con el repositorio y con las fuentes, y apartarse en silencio seria
el error que este proyecto persigue. Estan declarados uno a uno, con su
razon, en `DESVIACIONES_DEL_PLAN`, y ademas en el `que_lo_fija` de cada
variable, que es su punto de uso. Los cuatro se apartan SIEMPRE hacia el modo
que promete menos: ninguno inventa una tabla, un rango o una cita.

Regla de uso
------------
    import variables_entrada as ve

    v = ve.variable("cbr_subrasante")
    v.modo                       # ModoDeResolucion.DE_ENSAYO
    ve.por_modo()[ve.ModoDeResolucion.DE_TABLA]     # que ventana abrir
    ve.tabla_de("F_pga")         # la TablaNormativa que la ventana muestra
    ve.rango_de("v_max_concreto_eleccion")          # con su semantica
    print(ve.reporte_variables())
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import criterios_adoptados as _ca
import datos_sitio as _ds
import dominios as _dominios
from criterios_adoptados import verificar_resolucion
from modelos import (DeCatalogo, DeEnsayo, Derivada, DeTabla, EnRango, Libre,
                     ModoDeResolucion, Poblacion, Resolucion,
                     VariableDeEntrada)
from modulos.M0_carga import COLUMNAS
from normativa import registro as _registro_normativo


# ---------------------------------------------------------------------------
# La fase que consume cada modulo
# ---------------------------------------------------------------------------
# Los numeros salen de los titulos de `docs/hoja_de_ruta_alcantarillas_v8.md`,
# no de la numeracion de los modulos: coinciden porque M0 implementa la Fase 1
# y de ahi en adelante van corridos en uno, pero la fuente es la hoja de ruta.

_FASE_DE_MODULO: Dict[str, str] = {
    "M0_carga": "Fase 1 - Datos de entrada",
    "M1_clasificacion": "Fase 2 - Clasificacion y periodo de retorno",
    "M2_material": "Fase 3 - Tipo, material y durabilidad",
    "M3_hidraulica": "Fase 4 - Dimensionamiento hidraulico",
    "M4_control": "Fase 4 - Dimensionamiento hidraulico",
    "M5_verificaciones": "Fase 5 - Verificaciones",
    "M6_proteccion": "Fase 6 - Proteccion de entrada y salida",
    "M7_geometria": "Fase 7 - Compatibilidad geometrica",
    "M8_estructural": "Fase 8 - Verificacion estructural del conducto",
    "M9_cabezal": "Fase 9 - Cabezal y aletas",
    "M10_espaciamiento": "Fase 10 - Alcantarillas de alivio",
    "M11_reporte": "Fase 11 - Entregables",
    "MD": "Bucle de diseño (Fases 3 a 8)",
}

_MODULOS = Path(__file__).resolve().parent / "modulos"


# El ambito al que se atribuye una cadena dentro de un modulo: el nombre de la
# funcion o de la clase de primer nivel que la contiene, y "" para el cuerpo
# del modulo, que es donde viven las constantes CRITERIO_*. No es un detalle
# de implementacion: sin ambitos no hay grafo de llamadas, y sin grafo de
# llamadas el censo atribuye el consumo a quien ESCRIBE la cadena en vez de a
# quien la EJECUTA -- que es el falso negativo que esta pieza vino a cerrar.
_AMBITO_MODULO = ""


@dataclass(frozen=True)
class _Analisis:
    """Lo que hace falta saber de un modulo para seguir una clave a traves de el."""

    literales: Dict[str, Set[str]]                 # ambito -> cadenas escritas ahi
    llamadas: Dict[str, Set[Tuple[str, str]]]      # ambito -> (modulo, ambito) llamados
    constantes: Dict[str, str]                     # NOMBRE de nivel de modulo -> cadena
    importado: Dict[str, Tuple[str, str]]          # nombre local -> (modulo, nombre)


def _docstrings(arbol: ast.Module) -> Set[str]:
    docs: Set[str] = set()
    for n in ast.walk(arbol):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                          ast.ClassDef)):
            d = ast.get_docstring(n, clean=False)
            if d is not None:
                docs.add(d)
    return docs


def _analizar(ruta: Path) -> _Analisis:
    """
    Un modulo partido en ambitos, con sus cadenas y sus llamadas resueltas.

    Resuelve TRES formas de llamada y ninguna mas, porque son las tres que
    este repositorio usa: `f(...)` a una funcion del propio modulo, `f(...)` a
    una traida con `from modulos.MX import f`, y `M8.f(...)` sobre el alias de
    un modulo importado. Lo que no encaja en esas tres se ignora a proposito:
    un grafo incompleto deja consumidores sin ver --- defecto conocido y
    acotado, que se paga en falsos negativos --- mientras que uno que adivine
    los atribuiria mal, que es el defecto que esta funcion existe para evitar.

    Los metodos de una clase se agrupan bajo el nombre de la clase: una
    llamada a un metodo llega por una instancia y no se puede resolver por
    nombre, de modo que separarlos daria una precision que el grafo no puede
    sostener.
    """
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    docs = _docstrings(arbol)

    alias_modulo: Dict[str, str] = {}
    importado: Dict[str, Tuple[str, str]] = {}
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom) and nodo.module:
            partes = nodo.module.split(".")
            if partes[-1] == "modulos":
                for a in nodo.names:                    # from modulos import M8 as X
                    if a.name.startswith("M"):
                        alias_modulo[a.asname or a.name] = a.name
            elif "modulos" in partes and partes[-1].startswith("M"):
                for a in nodo.names:                    # from modulos.M8 import f
                    importado[a.asname or a.name] = (partes[-1], a.name)
        elif isinstance(nodo, ast.Import):
            for a in nodo.names:                        # import modulos.M8 as M8
                partes = a.name.split(".")
                if "modulos" in partes and partes[-1].startswith("M"):
                    alias_modulo[a.asname or partes[-1]] = partes[-1]

    cuerpos: Dict[str, List[ast.AST]] = {_AMBITO_MODULO: []}
    for nodo in arbol.body:
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            cuerpos.setdefault(nodo.name, []).append(nodo)
        else:
            cuerpos[_AMBITO_MODULO].append(nodo)
    propias = {n for n in cuerpos if n != _AMBITO_MODULO}

    # Las constantes del cuerpo del modulo se resuelven ANTES de recorrer los
    # ambitos: `ca.valor(CRITERIO_PESO_RELLENO)` no escribe ninguna cadena
    # dentro de la funcion, escribe un nombre, y sin este paso la clave se
    # queda en el ambito del modulo mientras el consumo esta en la funcion --
    # que es donde el grafo de llamadas la tiene que encontrar.
    constantes: Dict[str, str] = {
        destino.id: nodo.value.value
        for nodo in cuerpos[_AMBITO_MODULO]
        if isinstance(nodo, ast.Assign) and isinstance(nodo.value, ast.Constant)
        and isinstance(nodo.value.value, str)
        for destino in nodo.targets if isinstance(destino, ast.Name)
    }

    literales: Dict[str, Set[str]] = {}
    llamadas: Dict[str, Set[Tuple[str, str]]] = {}
    for ambito, cuerpo in cuerpos.items():
        cadenas: Set[str] = set()
        llamados: Set[Tuple[str, str]] = set()
        for raiz in cuerpo:
            for n in ast.walk(raiz):
                if isinstance(n, ast.Constant) and isinstance(n.value, str) \
                        and n.value not in docs:
                    cadenas.add(n.value)
                elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                        and n.value.id in alias_modulo:
                    llamados.add((alias_modulo[n.value.id], n.attr))
                elif isinstance(n, ast.Name):
                    if n.id in constantes:
                        cadenas.add(constantes[n.id])
                    if n.id in propias:
                        llamados.add((ruta.stem, n.id))
                    elif n.id in importado:
                        llamados.add(importado[n.id])
        literales[ambito] = cadenas
        llamadas[ambito] = llamados

    return _Analisis(literales=literales, llamadas=llamadas,
                     constantes=constantes, importado=importado)


@lru_cache(maxsize=1)
def _analisis() -> Dict[str, _Analisis]:
    return {ruta.stem: _analizar(ruta)
            for ruta in sorted(_MODULOS.glob("M*.py"))}


@lru_cache(maxsize=1)
def _consumo_por_modulo() -> Dict[str, frozenset]:
    """
    Las cadenas que cada modulo de calculo EJECUTA, no solo las que escribe.

    Es como se averigua quien consume una variable, y se AVERIGUA en vez de
    declararse a mano por una razon medida: nueve criterios se nombran en
    comentarios o docstrings de modulos que no los invocan (`TW_receptor` sale
    en cuatro), de modo que un `grep` -- o una lista escrita a mano a partir
    de un grep -- atribuye consumidores que no existen. Los docstrings se
    descartan explicitamente; los comentarios no son nodos del arbol y ya
    quedan fuera.

    EL SEGUNDO PASO LLEGO EN S21, Y LLEGO POR UN FALSO NEGATIVO MEDIDO. Hasta
    entonces esto era un solo paso --- las cadenas literales de cada modulo ---
    y esa atribucion se equivoca justo cuando el modulo que ESCRIBE la cadena
    no es el que la EJECUTA. Contrastado contra dos corridas reales del
    pipeline:

        'factores_carga_aashto'          decia   Fase 8 - Fase 9
        'peso_especifico_relleno_kn_m3'  decia   Fase 8 - Fase 9

    y a las dos las invoca V7 (flotacion), que es FASE 5 y corre en el alcance
    de perfil: `M5_verificaciones` importa de `M8_estructural` la constante
    `CRITERIO_FACTORES_CARGA` y la funcion `peso_relleno_kn_m`, y las dos
    cadenas viven en M8. Un filtro de alcance montado sobre la derivacion
    vieja habria ocultado dos criterios que la corrida de perfil SI invoca ---
    el error en la direccion peligrosa, que es la de esconder.

    Las dos vias por las que una clave cruza de modulo, y las dos se cierran
    aqui:

        CONSTANTE REEXPORTADA   `from modulos.M8_estructural import
                                CRITERIO_FACTORES_CARGA` --- la cadena esta
                                alli, el uso esta aqui.
        FUNCION REEXPORTADA     `from modulos.M8_estructural import
                                peso_relleno_kn_m`, que dentro llama a
                                `ca.valor(CRITERIO_PESO_RELLENO)`.

    La segunda se resuelve con un punto fijo sobre el grafo de llamadas: el
    consumo de un ambito incluye el de todo lo que llama, transitivamente.

    LO QUE ESTA DERIVACION NO ES: una prueba. Sigue siendo una ESTIMACION
    estatica, y por eso NO es ella la que gobierna el filtro de alcance de la
    GUI. Eso lo hace `Criterio.nivel`, que dos corridas reales comprueban en
    `tests/test_nivel_medido.py`. El papel de esta derivacion es decir a que
    FASE pertenece cada variable, y clasificar lo unico que ninguna corrida
    puede medir: lo que ninguna de las dos llega a invocar.
    """
    analisis = _analisis()

    consumo: Dict[Tuple[str, str], Set[str]] = {}
    for modulo, a in analisis.items():
        for ambito, cadenas in a.literales.items():
            consumo[(modulo, ambito)] = set(cadenas)

    # Una CONSTANTE reexportada no tiene cuerpo que recorrer: el nodo
    # (modulo, nombre) al que apunta la arista no existe, y sin esta linea la
    # clave se perderia. Se le da uno, con la cadena que su modulo de origen
    # le asigno, y el punto fijo la propaga a quien la referencie.
    for modulo, a in analisis.items():
        for origen, real in a.importado.values():
            if origen in analisis and real in analisis[origen].constantes:
                consumo.setdefault((origen, real), set()).add(
                    analisis[origen].constantes[real])

    aristas = {(modulo, ambito): llamados
               for modulo, a in analisis.items()
               for ambito, llamados in a.llamadas.items()}

    cambio = True
    while cambio:
        cambio = False
        for nodo, llamados in aristas.items():
            antes = len(consumo[nodo])
            for destino in llamados:
                consumo[nodo] |= consumo.get(destino, set())
            if len(consumo[nodo]) != antes:
                cambio = True

    salida: Dict[str, Set[str]] = {m: set() for m in analisis}
    for (modulo, _ambito), claves in consumo.items():
        salida[modulo] |= claves
    return {m: frozenset(claves) for m, claves in salida.items()}


def _consumidores(clave: str) -> Tuple[str, ...]:
    return tuple(sorted(m for m, claves in _consumo_por_modulo().items()
                        if clave in claves))


# ---------------------------------------------------------------------------
# Lo que este modulo aporta a cada variable
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _Meta:
    """
    Unidad, dominio y destino de una variable. Lo que NO esta ni en
    `Criterio` ni en `DatoSitio` ni en `PuntoCritico`.

    `fase_declarada` solo se llena cuando ningun modulo de calculo consume la
    variable: entonces la fase no se puede deducir del consumidor y hay que
    decir a que fase pertenece el hueco. Cuando hay consumidor, la fase se
    DEDUCE de el y no se escribe, para que no puedan divergir.
    """
    unidad: str
    dominio: Optional[str] = None
    criterio_destino: Optional[str] = None
    fase_declarada: str = ""
    nota: str = ""


@dataclass(frozen=True)
class Desviacion:
    """
    Un ejemplo de la Sec. 4.3 del plan que este censo NO sigue, con la razon.

    Existe como dato y no como prosa por la misma razon que
    `normativa.Discrepancia`: una desviacion que solo vive en un comentario no
    se puede enumerar, ni imprimir en la memoria, ni comprobar en un test.
    """
    variable: str
    modo_del_plan: str
    modo_adoptado: str
    por_que: str


DESVIACIONES_DEL_PLAN: Tuple[Desviacion, ...] = (
    Desviacion(
        variable="HW_D_max",
        modo_del_plan="en_rango",
        modo_adoptado="libre",
        por_que="El num. 2.2.5 d) del HDS-5 DESCRIBE lo que imponen las "
                "agencias viales de EE.UU. y no prescribe HW/D alguno "
                "(NOR-HDS-02). El conflicto vinculante #1 del plan ordena "
                "declarar de donde sale el 1.5 antes de cablearlo, y de ahi "
                "salio la reetiqueta de [C] a [A]. Pintarlo como rango con "
                "cita normativa devolveria la cita que ese hallazgo retiro.",
    ),
    Desviacion(
        variable="factor_muro_eleccion",
        modo_del_plan="de_tabla",
        modo_adoptado="libre",
        por_que="El num. 2.8.1.1.14.2.2 NO TABULA NADA: autoriza una "
                "reduccion ('kh puede ser reducido a 0.5kh0'). El 1.0 "
                "adoptado no es una fila, es la AUSENCIA de reduccion, que es "
                "la definicion misma de k_h0. Una ventana que mostrara una "
                "tabla inventaria filas que el numeral no tiene.",
    ),
    Desviacion(
        variable="resguardo_HW_subrasante",
        modo_del_plan="de_tabla (el plan lo escribe `resguardo(CBR)`)",
        modo_adoptado="libre, con `tabla_pendiente`",
        por_que="La tabla de resguardo por CBR del Manual de Suelos num. "
                "4.5.4 existe y es [N], pero vive como escalares en "
                "`constantes_normativas.py` y NO esta transcrita como "
                "`TablaNormativa` en el registro. El criterio de salida de la "
                "Sec. 4.3 prohibe un `de_tabla` sin tabla en el registro, asi "
                "que la variable queda `libre` y la tabla queda nombrada como "
                "pendiente: transcribirla la convierte en `de_tabla` sin "
                "tocar nada mas.",
    ),
    Desviacion(
        variable="diametros_normalizados",
        modo_del_plan="de_catalogo",
        modo_adoptado="libre, con `tabla_pendiente`",
        por_que="El ejemplo del plan apunta al 'max' que este criterio TENIA "
                "cuando el plan se escribio. La sesion S4 mudo esos topes a "
                "`D_max_catalogo` al cerrar NOR-PRO-01 y NOR-PRO-02, y ese "
                "criterio SI es `de_catalogo`. Lo que queda aqui es el inicio "
                "y el paso de la serie, verificados contra la Tabla 1 de ASTM "
                "A760: rotularlos 'catalogo de proveedor' contradiria la "
                "neutralidad comercial que la propia justificacion del "
                "criterio invoca.",
    ),
)


# ---------------------------------------------------------------------------
# Poblacion 1 - las 17 columnas del CSV
# ---------------------------------------------------------------------------
# Es la unica poblacion cuya resolucion se declara aqui: `PuntoCritico` es un
# tipo y no un catalogo de declaraciones, y una columna no tiene ficha propia
# donde ponerla. El concepto se escribe aqui por lo mismo.

@dataclass(frozen=True)
class _Columna:
    concepto: str
    unidad: str
    resolucion: Resolucion
    dominio: Optional[str] = None
    criterio_destino: Optional[str] = None
    nota: str = ""


_COLUMNAS: Dict[str, _Columna] = {

    "id": _Columna(
        concepto="Identificador del punto critico, con el que la memoria y "
                 "los planos lo nombran",
        unidad="-",
        resolucion=Libre(
            que_lo_fija="el expediente: es el nombre del cruce en planos y "
                        "en la memoria",
            dominio="texto no vacio, unico en el CSV",
        ),
    ),

    "progresiva_km": _Columna(
        concepto="Progresiva del cruce sobre el eje de la via. Localizador: "
                 "no entra en ningun calculo. Se escribe en NOTACION VIAL "
                 "('0+380') o en kilometros decimales ('0.380'): M0 acepta "
                 "las dos y la memoria imprime siempre la notacion vial",
        unidad="km",
        resolucion=Libre(
            que_lo_fija="el trazo del expediente vial",
            # LAS DOS FORMAS, Y ESTABAN SIN DECLARAR (S23). El dominio decia
            # solo «km >= 0», y `M0._progresiva` acepta ademas la notacion
            # vial con '+' --- que es la que usan los DOS CSV del repositorio
            # y la que la memoria y los planos imprimen ---. Quien leyera la
            # ayuda derivada de este campo escribiria '0.380' creyendo que es
            # la unica forma admitida: funciona, y aun asi la ayuda le estaba
            # escondiendo la mitad del contrato.
            #
            # El tope de los metros no se escribe como numero: se NOMBRA
            # (`METROS_POR_KM`), igual que `S_cauce` nombra `S_CAUCE_MAX`, de
            # modo que la ayuda no pueda decir un limite distinto del que
            # `_progresiva` aplica.
            dominio="km >= 0, dentro del corredor del proyecto. DOS "
                    "NOTACIONES ADMITIDAS: la vial '0+380' (kilometro, '+', "
                    "metros de 0 a METROS_POR_KM sin alcanzarlo) y los "
                    "kilometros decimales '0.380'. Un solo '+' por celda",
        ),
    ),

    "familia": _Columna(
        concepto="Familia del cruce (Sec. 2.3), que decide el periodo de "
                 "retorno y que datos son exigibles en la fila",
        unidad="-",
        resolucion=Libre(
            que_lo_fija="Sec. 2.3 de la hoja de ruta, aplicada al cruce por "
                        "quien arma el CSV",
            dominio="una de las familias declaradas",
            opciones=("A", "B", "C"),
        ),
    ),

    "Q_m3s": _Columna(
        concepto="Caudal de diseño del cruce para el periodo de retorno de su "
                 "familia",
        unidad="m3/s",
        resolucion=Libre(
            que_lo_fija="el estudio hidrologico (Fase 1-bis); en Familia C lo "
                        "fija el canal, via ANA / Junta de Usuarios",
            dominio="m3/s > 0 y finito",
        ),
    ),

    "area_ha": _Columna(
        concepto="Area de la cuenca aportante. Solo clasificador (Sec. 1.1): "
                 "no entra en el dimensionamiento",
        unidad="ha",
        resolucion=Libre(
            que_lo_fija="la delimitacion de cuenca del estudio hidrologico",
            dominio="ha > 0",
        ),
        criterio_destino="umbral_area_quebrada_importante_ha",
    ),

    "S_cauce": _Columna(
        concepto="Pendiente del CAUCE en el cruce -- no la del conducto, que "
                 "es otra cosa y se confunden (Sec. 1.5). En un cruce de "
                 "canal el «cauce» es el canal",
        unidad="m/m",
        resolucion=Libre(
            que_lo_fija="el perfil del cauce del levantamiento topografico. "
                        "EN LA FAMILIA C NO, y es el matiz que C6 tuvo que "
                        "escribir: en un cruce de canal el cauce es el canal, "
                        "su perfil no lo levanta el proyectista vial y la "
                        "columna va vacia por el Tablero 3.1 (ANA / Junta de "
                        "Usuarios del Bajo Piura). Para esos puntos el valor "
                        "entra por la clave `S_cauce` de "
                        "`cli.CLAVES_EXTERNAS`, y la memoria lo imprime con "
                        "esa procedencia en vez de con la de la columna",
            dominio="m/m, 0 < S < S_CAUCE_MAX; un valor >= 1 delata una celda "
                    "cargada en porcentaje",
        ),
        dominio="S_CAUCE_MAX",
    ),

    "cota_terreno": _Columna(
        concepto="Cota del terreno natural en el cruce",
        unidad="msnm",
        resolucion=Libre(
            que_lo_fija="el levantamiento topografico del expediente",
            dominio="msnm",
        ),
    ),

    "cota_fondo_entrada": _Columna(
        concepto="Cota del fondo de la ENTRADA (invert) medida en el cruce. "
                 "Admite vacio: cuando falta, la pone la regla declarada en "
                 "el criterio 'origen_cota_fondo_entrada'",
        unidad="msnm",
        resolucion=DeEnsayo(
            ensayo="nivelacion del fondo del cauce -- del CANAL, en un paso "
                   "de canal -- en la seccion del cruce",
            trazabilidad_exigida="la libreta de nivelacion o el perfil "
                                 "longitudinal del cauce, con la progresiva "
                                 "de la seccion levantada y el BM de "
                                 "referencia. Se MIDE en cada cruce: por eso "
                                 "es columna y no dato de corredor",
        ),
        criterio_destino="origen_cota_fondo_entrada",
    ),

    # SIN `criterio_destino`, y no es un olvido: ese campo dice a que criterio
    # va a parar la columna cuando el proyectista tiene que ELEGIR como
    # obtenerla, y aqui no hay eleccion que hacer. La coronacion de un canal
    # se mide o no se tiene: no hay regla declarada que la sustituya --- al
    # reves que `cota_fondo_entrada`, que si la tiene ---. Vacia, lo que se
    # detiene es VC1 con `DatoFaltanteError`, que es lo que corresponde cuando
    # el revisor tiene que CONSEGUIR algo y no que decidirlo.
    "cota_coronacion_canal": _Columna(
        concepto="Cota de la coronacion (labio) del canal en el cruce, "
                 "contra la que VC1 verifica el borde libre. Admite vacio: "
                 "sin ella VC1 se detiene, y no hay regla que la sustituya",
        unidad="msnm",
        resolucion=DeEnsayo(
            ensayo="levantamiento topografico del cruce: seccion transversal "
                   "del canal con su fondo y sus dos coronaciones",
            trazabilidad_exigida="la libreta o la seccion transversal "
                                 "levantada, con la progresiva del cruce y el "
                                 "BM de referencia, y cual de las dos "
                                 "margenes se transcribio si no estan a la "
                                 "misma cota --- que es la pregunta que un "
                                 "solo numero por punto deja abierta: la "
                                 "columna admite UNA cota y lo conservador es "
                                 "la MENOR de las dos, porque es por ahi por "
                                 "donde desborda primero",
        ),
    ),

    "cota_rasante": _Columna(
        concepto="Cota de la superficie de rodadura sobre el cruce",
        unidad="msnm",
        resolucion=Libre(
            que_lo_fija="el diseño geometrico del expediente vial (DG-2018)",
            dominio="msnm, por encima de la cota de subrasante",
        ),
    ),

    "cota_subrasante": _Columna(
        concepto="Cota de la subrasante sobre el cruce, contra la que se "
                 "verifica el resguardo de V4",
        unidad="msnm",
        resolucion=Libre(
            que_lo_fija="el diseño de pavimento del expediente vial",
            dominio="msnm, por debajo de la cota de rasante",
        ),
    ),

    "cbr_subrasante": _Columna(
        concepto="CBR de la subrasante en el cruce, que decide el resguardo "
                 "exigible entre el nivel de agua a la entrada y la "
                 "subrasante",
        unidad="%",
        resolucion=DeEnsayo(
            ensayo="ensayo CBR de laboratorio sobre la muestra de la calicata "
                   "del cruce",
            trazabilidad_exigida="calicata, profundidad de muestreo, "
                                 "laboratorio, fecha e informe de ensayo. Se "
                                 "MIDE en cada cruce: por eso es columna y no "
                                 "dato de corredor",
        ),
        dominio="CBR_MAX_FISICO",
        criterio_destino="resguardo_HW_subrasante",
    ),

    "esviaje_grados": _Columna(
        concepto="Angulo entre el eje del conducto y la perpendicular al eje "
                 "de la via. A 0 grados el cruce es perpendicular",
        unidad="grados",
        resolucion=Libre(
            que_lo_fija="el plano de planta del expediente vial",
            dominio="grados, 0 <= esviaje < ESVIAJE_MAX; a 90 el conducto "
                    "seria paralelo a la via y no habria cruce",
        ),
        dominio="ESVIAJE_MAX",
    ),

    "ancho_plataforma": _Columna(
        concepto="Ancho de la plataforma de la via sobre el cruce, que fija "
                 "la longitud minima del conducto",
        unidad="m",
        resolucion=Libre(
            que_lo_fija="la seccion transversal tipo del expediente vial",
            dominio="m > 0",
        ),
    ),

    "cota_fondo_receptor": _Columna(
        concepto="Cota del fondo del cuerpo receptor en el punto de entrega",
        unidad="msnm",
        resolucion=Libre(
            que_lo_fija="el levantamiento topografico del cuerpo receptor",
            dominio="msnm",
        ),
    ),

    "Q_receptor_m3s": _Columna(
        concepto="Caudal del cuerpo receptor durante la avenida, para la "
                 "verificacion de entrega",
        unidad="m3/s",
        resolucion=Libre(
            que_lo_fija="la ANA / Junta de Usuarios del Bajo Piura "
                        "(Tablero 3.1); mientras no llegue, la celda va "
                        "vacia y la fila se carga marcada",
            dominio="m3/s >= 0",
        ),
    ),

    "cota_TW": _Columna(
        concepto="Nivel de agua en el cuerpo receptor durante la avenida "
                 "(tailwater), que decide si el control es de salida",
        unidad="msnm",
        resolucion=Libre(
            que_lo_fija="Sec. 1.3, con el dato del receptor; mientras no "
                        "llegue, la celda va vacia (Tablero 3.1)",
            dominio="msnm, por encima de la cota de fondo del receptor",
        ),
        criterio_destino="TW_receptor",
    ),

    "sucs_fundacion": _Columna(
        concepto="Clasificacion SUCS del suelo de fundacion en la calicata "
                 "del cruce",
        unidad="-",
        resolucion=DeEnsayo(
            ensayo="clasificacion SUCS de la muestra de la calicata del cruce "
                   "(granulometria y limites de Atterberg)",
            trazabilidad_exigida="calicata, profundidad de muestreo, "
                                 "laboratorio y fecha. Es obligatoria en el "
                                 "encabezado de Sec. 1.2 aunque hoy ningun "
                                 "modulo la lea, y las dos cosas son "
                                 "correctas a la vez. HAY DOS CONSUMIDORES "
                                 "PLAUSIBLES Y NINGUNO ESTA CABLEADO, por "
                                 "razones distintas. (1) `c_phi_fundacion`, "
                                 "el destino declarado: es de EXPEDIENTE y lo "
                                 "consumen E1-E5 de la Sec. 9.3, que esta CLI "
                                 "no ensambla; el dia que se ensamblen, el "
                                 "dato ya esta. (2) El num. 4.1.1.3.4 a), que "
                                 "recomienda el marco segun la calidad del "
                                 "suelo de fundacion: ese NO se cablea, y EL "
                                 "VACIO ES DEL MANUAL, NO DEL PROYECTO -- la "
                                 "fuente no define «mala calidad», no da "
                                 "umbral ni clasificacion ni remision, de "
                                 "modo que el mapeo SUCS -> mala calidad "
                                 "habria que INVENTARLO --. Esta medido y "
                                 "escrito, con su literal verificado, en la "
                                 "condicion `COND-MARCO-SUELO-MALA-CALIDAD` "
                                 "de `normativa/citas.py`, que por eso la "
                                 "resuelve como `NoEvaluable` y no como un "
                                 "dato pendiente. C6 lo reviso y confirmo la "
                                 "decision; la ficha esta en "
                                 "`docs/decisiones_diferidas.md`",
        ),
        criterio_destino="c_phi_fundacion",
        # QUE SE ESCRIBE EN LA CELDA. Faltaba, y era el segundo defecto que
        # destapo la ayuda derivada de S22: la celda es texto libre, `M0._texto`
        # acepta cualquier cadena no vacia, y la ficha no decia ni que forma
        # tiene un grupo SUCS. Quien llena el CSV no tenia de donde saberlo.
        #
        # EL VOCABULARIO NO ESTA CERRADO POR NINGUNA FUENTE DE `normas/`, y esa
        # es la razon de que esto sea una NOTA y no un `opciones`. Lo medido,
        # leyendo los PDF y no de memoria:
        #
        #   - E.050, FIGURA 3, pagina impresa 31: enumera QUINCE simbolos
        #     basicos (los de abajo) y la propia norma rotula la figura como
        #     referencial. Ninguna dupla aparece ahi.
        #   - Manual de Suelos (MTC), Cuadro 4.9, pagina impresa 35: correlaciona
        #     AASHTO con SUCS y atribuye la clasificacion SUCS a ASTM D-2487.
        #     Usa trece simbolos y ninguna dupla.
        #   - Manual de Suelos (MTC), Cuadro 9.1, pagina impresa 92: USA nueve
        #     duplas como claves de fila (SP-SM, SM-SC, GW-GC...), pero es una
        #     guia de estabilizadores, no una enumeracion --- y trae ademas un
        #     desliz de transcripcion en la fuente ('SP - PC').
        #   - ASTM D-2487, que es quien define el sistema y sus duplas, NO esta
        #     en `normas/`.
        #
        # De ahi la consecuencia que decide la forma de esta declaracion:
        # `tests/ejemplo_puntos.csv` trae 'SP-SM', que NO esta entre los quince.
        # Declarar los quince como conjunto cerrado dejaria fuera un valor del
        # propio expediente, e inventar la regla de composicion de duplas seria
        # inventar norma. Se declara lo que hay y se declara el hueco.
        #
        # NO RESTRINGE LA CARGA, y esta comprobado: nada valida una celda de
        # texto contra una lista declarada --- `Libre.opciones` solo se IMPRIME
        # (M11, la ventana normativa y la ayuda) --- y `test_ayuda_entrada.py`
        # fija que M0 sigue aceptando 'SP-SM' y cualquier otra cadena. Esta nota
        # informa; no cierra ninguna puerta.
        nota="Grupo SUCS del suelo de fundacion. Los QUINCE simbolos basicos "
             "son GW, GP, GM, GC, SW, SP, SM, SC, ML, CL, OL, MH, CH, OH y Pt "
             "(E.050, FIGURA 3, pag. impresa 31; la norma rotula esa figura "
             "como referencial). La celda admite ADEMAS la forma doble de un "
             "suelo de frontera --- 'SP-SM', 'SM-SC' ---, que el expediente usa "
             "y que NINGUNA fuente de normas/ enumera: quien las define es ASTM "
             "D-2487, que no esta en el repositorio. M0 NO valida esta celda "
             "contra ninguna lista: solo exige que no este vacia.",
    ),

    "NF_profundidad_m": _Columna(
        concepto="Profundidad del nivel freatico bajo el terreno natural en "
                 "el cruce, para la flotacion (V7) y la subpresion del "
                 "cabezal",
        unidad="m",
        resolucion=DeEnsayo(
            ensayo="medicion del nivel freatico en la calicata o el "
                   "piezometro del cruce",
            trazabilidad_exigida="calicata o piezometro, FECHA Y EPOCA DEL "
                                 "AÑO de la medicion -- un NF de estiaje y "
                                 "uno de avenida no son el mismo dato -- y el "
                                 "informe geotecnico",
        ),
        nota="Es la unica columna que no viene del encabezado de Sec. 1.2: se "
             "agrego al reclasificar el nivel freatico, que era un criterio "
             "unico de proyecto (1.4 m) y se MIDE en cada cruce.",
    ),
}


# ---------------------------------------------------------------------------
# Poblacion 2 - los datos de sitio de corredor
# ---------------------------------------------------------------------------

_META_SITIO: Dict[str, _Meta] = {
    "PGA_roca_B": _Meta(unidad="g"),
    "ZONA_SISMICA_LA_UNION": _Meta(
        unidad="-",
        fase_declarada="Fase 0-bis - marco sismico (referencia declarada; "
                       "Sec. 0.4 la descarta del calculo)"),
    "Z_E030": _Meta(
        unidad="g",
        fase_declarada="Fase 0-bis - marco sismico (referencia declarada; "
                       "Sec. 0.4 la descarta del calculo)"),
    "corredor_del_proyecto": _Meta(
        unidad="-",
        fase_declarada="Fase 0-bis - definicion del tramo (num. 150); no "
                       "gobierna ningun calculo: es el ambito de los demas "
                       "datos de sitio"),
    "orientacion_muro_respecto_al_trafico": _Meta(
        unidad="-",
        nota="Es el dato que decide CUAL de las dos tablas de h_eq aplica, "
             "y por eso no tiene un criterio destino sino dos: "
             "`h_eq_bajo_altura_tabulada` y `h_eq_banda_intermedia_borde` "
             "resuelven sendas lagunas de la tabla que este dato elige."),
    "distancia_borde_calzada_al_trasdos_m": _Meta(
        unidad="m", criterio_destino="h_eq_banda_intermedia_borde"),
    "carriles_por_sentido": _Meta(
        unidad="carriles",
        fase_declarada="Fase 1 - Datos de entrada (Cuadro 4.1 del Manual de "
                       "Suelos: numero minimo de calicatas)"),
    "clase_de_via": _Meta(
        unidad="-",
        fase_declarada="Fase 1 - Datos de entrada (Cuadro 4.1 del Manual de "
                       "Suelos, y piso de seccion del num. 4.1.1.3.4 a) del "
                       "Manual de Hidrologia)",
        nota="Declarada en el triage de T2: `COND-CLASE-DE-VIA` y "
             "`COND-DMIN-ALTO-VOLUMEN` resolvian a esta clave y la clave no "
             "existia en ningun archivo."),
    "existe_informacion_secundaria_tramo": _Meta(
        unidad="-",
        fase_declarada="Fase 1 - Datos de entrada (num. 4.2 del Manual de "
                       "Suelos: espaciamiento de calicatas a nivel de "
                       "perfil)",
        nota="Declarada en el triage de T2: `COND-PERFIL-SIN-INFO-SECUNDARIA` "
             "resolvia a esta clave y la clave no existia en ningun archivo."),
}


# ---------------------------------------------------------------------------
# Poblacion 3 - los criterios adoptados
# ---------------------------------------------------------------------------

_META_CRITERIOS: Dict[str, _Meta] = {
    "D_max_catalogo": _Meta(unidad="m"),
    "F_pga": _Meta(unidad="-"),
    "F_pga_lectura_columna_extrema": _Meta(unidad="-"),
    "HW_D_max": _Meta(unidad="-"),
    "Mw_licuefaccion": _Meta(
        unidad="-", fase_declarada="Fase 0-bis - licuefaccion"),
    "N_cq_N_gammaq_meyerhof": _Meta(unidad="-"),
    "PERFIL_SUELO_PRESUNTO": _Meta(
        unidad="-", fase_declarada="Fase 0-bis - licuefaccion"),
    "TR_evento_extremo": _Meta(unidad="años"),
    "acceso_mantenimiento_v2b": _Meta(
        unidad="-",
        nota="Es la mitad [A] de la fila V2b de la Fase 5. La otra mitad -- "
             "el indicador de sedimentacion del HDS-5 num. 5.3.3 -- no "
             "necesita declaracion: se calcula comparando la pendiente del "
             "diseño con la del cauce, y las dos son datos que la corrida ya "
             "tiene."),
    "borde_libre_canal_m": _Meta(
        unidad="m",
        fase_declarada="Fase 5 - Verificaciones (VC1, cruce de canal)",
        nota="ES EL BORDE LIBRE DEL CANAL, NO EL DE V1. El de V1 es relativo "
             "y se mide DENTRO del barril (>= 25 % de su altura, num. "
             "4.1.1.3.7 b); este es absoluto y se mide bajo la CORONACION del "
             "canal. Los dos apartados del Manual se titulan «Borde libre» y "
             "no son intercambiables. Al moverse dentro de la ventana "
             "0.30-0.50 m hay que saber el signo: el valor se RESTA de la "
             "coronacion, de modo que subirlo endurece VC1."),
    "TW_receptor": _Meta(
        unidad="m sobre el fondo de la salida",
        fase_declarada="Fase 1 - Datos de entrada (Sec. 1.3, ultima puerta "
                       "del TW: `M3.tw_seccion_1_3` lo invoca solo cuando el "
                       "expediente no trae ni `cota_TW`, ni el caudal del "
                       "receptor, ni su seccion)",
        nota="LA UNIDAD ESTABA MAL Y NO ERA INOCUO. Decia «msnm», que es la "
             "unidad de `cota_TW` -- una COTA ABSOLUTA --, y este criterio "
             "declara un TIRANTE sobre el fondo de la salida. Es exactamente "
             "la homonimia que `constantes_normativas.HOMONIMIA_TW` existe "
             "para senalar, y la tenia el tablero que la senala. Confundirlas "
             "desplaza el control de salida en la magnitud entera de la cota "
             "de fondo: centenares de metros en este corredor."),
    "angulo_aletas": _Meta(
        unidad="grados", fase_declarada="Fase 9 - Cabezal y aletas"),
    "c_phi_fundacion": _Meta(
        unidad="kPa y grados",
        fase_declarada="Fase 9 - Cabezal y aletas (E1-E5 de Sec. 9.3, fuera "
                       "del alcance de esta CLI)"),
    "capacidad_portante_adm": _Meta(
        unidad="kPa",
        fase_declarada="Fase 9 - Cabezal y aletas (E1-E5 de Sec. 9.3, fuera "
                       "del alcance de esta CLI)"),
    "categoria_refuerzo_aashto": _Meta(unidad="-"),
    "clase_sitio": _Meta(
        unidad="-", fase_declarada="Fase 0-bis - licuefaccion"),
    "clases_producto_por_relleno": _Meta(unidad="-"),
    "cobertura_minima_aashto": _Meta(unidad="m"),
    "cobertura_minima_cajon": _Meta(unidad="m"),
    "condicion_pavimento": _Meta(unidad="-"),
    "cortante_alto_muro_e060_art_11_10_10_2": _Meta(unidad="-"),
    "demanda_sismica_licuefaccion": _Meta(
        unidad="años", fase_declarada="Fase 0-bis - licuefaccion"),
    "diametros_normalizados": _Meta(unidad="m"),
    "espesor_pared_conducto": _Meta(unidad="m"),
    "espesor_proteccion_salida": _Meta(unidad="- (multiplo de d50)"),
    "exposicion_quimica_ems": _Meta(unidad="ppm"),
    "factor_muro_eleccion": _Meta(unidad="-"),
    "factor_recubrimiento_banda_intermedia_ac": _Meta(unidad="-"),
    "factores_carga_aashto": _Meta(unidad="-"),
    "friccion_muro_suelo_delta": _Meta(unidad="grados"),
    "gamma_EQ": _Meta(unidad="-"),
    "geometria_control_salida": _Meta(unidad="-"),
    "h_eq_bajo_altura_tabulada": _Meta(unidad="-"),
    "h_eq_banda_intermedia_borde": _Meta(unidad="-"),
    "hds5_embocadura_hdpe": _Meta(unidad="-"),
    "homogeneidad_serie_fen": _Meta(
        unidad="-",
        fase_declarada="Fase 1-bis - Hidrologia: poblacion mixta por FEN "
                       "(ningun modulo lo invoca: la serie no ha llegado)"),
    "inclinacion_muro_beta": _Meta(unidad="grados"),
    "k_v": _Meta(unidad="-"),
    "ke_entrada": _Meta(unidad="-"),
    # ---------------- los cinco del cajon (C5) --------------------------
    # Los cinco entran SIN VALOR y con `fase_declarada` escrita donde hace
    # falta: `_fase` la deduce del consumidor cuando lo hay, y estos se
    # consumen desde M2 -- que es Fase 3 -- salvo el ke, que lo consume M4.
    # SIN `dominio`, y no por descuido: ese campo nombra un simbolo de
    # `dominios.py` -- se comprueba por nombre, justamente para que no pueda
    # apuntar a nada -- y hoy ese archivo no tiene ningun limite fisico para
    # la seccion de un marco. Ponerle uno es abrir un valor de proyecto en un
    # archivo exento del barrido de literales, y ademas es del frente F5
    # (entradas y dominios, sesion C6). Queda anotado ahi.
    "secciones_cajon_normalizadas": _Meta(
        unidad="m (pares B x H interiores de UNA celda)",
        nota="La serie se declara en el orden en que el bucle de MD tiene que "
             "recorrerla: en dos dimensiones «el siguiente escalon» no es una "
             "relacion que el programa pueda deducir, porque crecer en ancho "
             "y crecer en canto no son intercambiables."),
    "n_manning_cajon": _Meta(
        unidad="- (par n_min, n_max)",
        nota="Se declara la FILA de la Tabla N 09, no el par: el rango se lee "
             "de la fila para que la analogia y la tabla no puedan divergir, "
             "que es como ya se resuelve 'n_manning_hdpe'."),
    "embocadura_cajon": _Meta(
        unidad="-",
        nota="El valor es una de las claves 'cajon_concreto_*' de "
             "constantes_normativas.HDS5_INLET. Se mueve JUNTO con 'ke_entrada_cajon' y con el detalle de "
             "embocadura del cabezal (Sec. 9.1): las tres son la misma "
             "decision leida en tres sitios."),
    "espesor_pared_cajon": _Meta(
        unidad="m",
        nota="UN ESCALAR, no una tabla por diametro: un marco vaciado in situ "
             "no tiene serie de producto que indexar, y por eso este criterio "
             "no es una entrada mas de 'espesor_pared_conducto'. "
             "Y EL SIGNO DE SU SENSIBILIDAD ES CONTRAINTUITIVO: engrosar la "
             "pared EMPEORA la flotacion. Con DC = 0 -- V7 omite el peso "
             "propio, del lado conservador -- el espesor entra solo por la "
             "geometria exterior, y ahi la subpresion crece en dos "
             "dimensiones mientras el relleno que estabiliza crece en una. "
             "Quien lo declare va a suponer lo contrario: leer la ventana."),
    "n_celdas_cajon": _Meta(
        unidad="celdas",
        nota="Entero >= 1. El caudal de diseño se reparte entre las celdas "
             "-- `MD._caudal_por_barril` --, porque los coeficientes de HDS-5 "
             "y el radio hidraulico son POR BARRIL."),
    "ke_entrada_cajon": _Meta(
        unidad="-",
        nota="EL VALOR NO ES EL COEFICIENTE: es una de las claves "
             "'cajon_*' de constantes_normativas.KE_HDS5_C2, o sea la FILA "
             "del bloque «Box, Reinforced Concrete» de la Tabla C.2. Se "
             "declara asi porque en ese bloque el numero no identifica la "
             "fila -- el 0.2 esta en tres y el 0.5 en dos --. Lo elige "
             "'embocadura_cajon': su fila de la Tabla C.2 es la del "
             "mismo detalle de embocadura con que se lee la Tabla A.1."),
    "long_max_cuneta": _Meta(unidad="m"),
    "longitud_proteccion_salida": _Meta(unidad="m"),
    "metodo_estabilidad_global": _Meta(unidad="-"),
    "metodo_transicion_hds5": _Meta(unidad="-"),
    "n_manning_hdpe": _Meta(unidad="-"),
    "origen_cota_fondo_entrada": _Meta(unidad="-"),
    "pendiente_relleno_trasdos_i": _Meta(unidad="grados"),
    "peso_especifico_concreto_kn_m3": _Meta(unidad="kN/m3"),
    "peso_especifico_relleno_kn_m3": _Meta(unidad="kN/m3"),
    "phi_relleno_trasdos": _Meta(unidad="grados"),
    "predimensionamiento_cabezal": _Meta(unidad="m"),
    "procedimiento_flexion_corte_aashto_sec5": _Meta(unidad="-"),
    "punto_aplicacion_incremento_sismico": _Meta(unidad="- (fraccion de H)"),
    "remanso_derecho_via": _Meta(unidad="m"),
    "seccion_receptor": _Meta(
        unidad="m, H:V, m/m, -",
        fase_declarada="Fase 1 - Datos de entrada (Sec. 1.3, paso 2: Manning "
                       "en la seccion del receptor)"),
    "resguardo_HW_subrasante": _Meta(unidad="m"),
    "riesgo_admisible_propietario": _Meta(unidad="% y años"),
    "situacion_recubrimiento_aashto": _Meta(unidad="-"),
    "tabla_recubrimiento_aashto_mm": _Meta(unidad="mm"),
    "talud_terraplen": _Meta(unidad="H:V"),
    "umbral_area_quebrada_importante_ha": _Meta(unidad="ha"),
    "v_max_concreto_eleccion": _Meta(unidad="m/s"),
    "v_max_hdpe": _Meta(unidad="m/s"),
    "v_max_tmc": _Meta(unidad="m/s"),
}


# ---------------------------------------------------------------------------
# El censo
# ---------------------------------------------------------------------------

def _fase(clave: str, meta_fase: str, consumidores: Tuple[str, ...]) -> str:
    if consumidores:
        fases = []
        for m in consumidores:
            f = _FASE_DE_MODULO[m]
            if f not in fases:
                fases.append(f)
        return " · ".join(fases)
    if not meta_fase:
        raise ValueError(
            f"'{clave}' no la consume ningun modulo y no declara "
            "`fase_declarada`. Una variable sin consumidor y sin fase no se "
            "puede colocar en la memoria: o se cablea, o se dice a que fase "
            "pertenece el hueco"
        )
    return meta_fase


def _construir() -> Dict[str, VariableDeEntrada]:
    salida: Dict[str, VariableDeEntrada] = {}

    for clave in COLUMNAS:
        col = _COLUMNAS[clave]
        cons = _consumidores(clave)
        salida[clave] = VariableDeEntrada(
            clave=clave,
            concepto=col.concepto,
            unidad=col.unidad,
            poblacion=Poblacion.COLUMNA_CSV,
            resolucion=col.resolucion,
            fase=_fase(clave, "", cons),
            consumido_por=cons,
            criterio_destino=col.criterio_destino,
            dominio=col.dominio,
            nota=col.nota,
        )

    for clave, dato in _ds.DATOS_SITIO.items():
        meta = _META_SITIO[clave]
        cons = _consumidores(clave)
        salida[clave] = VariableDeEntrada(
            clave=clave,
            concepto=dato.concepto,
            unidad=meta.unidad,
            poblacion=Poblacion.DATO_SITIO,
            resolucion=dato.resolucion,
            fase=_fase(clave, meta.fase_declarada, cons),
            consumido_por=cons,
            criterio_destino=meta.criterio_destino,
            dominio=meta.dominio,
            nota=meta.nota,
        )

    for clave, crit in _ca.CRITERIOS.items():
        meta = _META_CRITERIOS[clave]
        cons = _consumidores(clave)
        salida[clave] = VariableDeEntrada(
            clave=clave,
            concepto=crit.concepto,
            unidad=meta.unidad,
            poblacion=Poblacion.CRITERIO,
            resolucion=crit.resolucion,
            # Un criterio recibe su propia eleccion: es el destino de si mismo.
            fase=_fase(clave, meta.fase_declarada, cons),
            consumido_por=cons,
            criterio_destino=clave,
            dominio=meta.dominio,
            nota=meta.nota,
        )

    return salida


VARIABLES: Dict[str, VariableDeEntrada] = _construir()


# ---------------------------------------------------------------------------
# La guardia
# ---------------------------------------------------------------------------
# El criterio de salida de la Sec. 4.3, hecho comprobacion al importar:
#
#     ninguna variable de entrada sin modo
#     ningun modo=de_tabla sin tabla existente en el registro
#     ningun modo=en_rango sin rango con semantica declarada
#
# Los dos ultimos los comprueba `criterios_adoptados.verificar_resolucion`,
# que es la MISMA funcion que corre al importar las otras dos poblaciones: se
# reutiliza en vez de escribirse otra vez, para que las tres poblaciones no
# puedan quedar sujetas a reglas distintas -- que es exactamente la asimetria
# que esta sesion vino a cerrar.

def _verificar_censo() -> None:
    esperado = {
        Poblacion.COLUMNA_CSV: set(COLUMNAS),
        Poblacion.DATO_SITIO: set(_ds.DATOS_SITIO),
        Poblacion.CRITERIO: set(_ca.CRITERIOS),
    }
    for poblacion, claves in esperado.items():
        censadas = {v.clave for v in VARIABLES.values()
                    if v.poblacion is poblacion}
        faltan = claves - censadas
        if faltan:
            raise ValueError(
                f"el censo no cubre {sorted(faltan)} de la poblacion "
                f"'{poblacion.value}'. Ninguna variable de entrada puede "
                "quedar sin modo de resolucion"
            )
        sobran = censadas - claves
        if sobran:
            raise ValueError(
                f"el censo declara {sorted(sobran)} como '{poblacion.value}' "
                "y esa poblacion no los tiene"
            )

    total = sum(len(c) for c in esperado.values())
    if len(VARIABLES) != total:
        # Solo puede pasar si una clave se repite entre poblaciones, en cuyo
        # caso una tapa a la otra en el diccionario y desaparece del censo sin
        # que ningun conteo por poblacion lo note.
        raise ValueError(
            f"el censo tiene {len(VARIABLES)} entradas y las tres poblaciones "
            f"suman {total}: hay una clave repetida entre poblaciones"
        )


def _verificar_variable(v: VariableDeEntrada) -> None:
    verificar_resolucion(v.clave, v.resolucion)

    if not v.concepto or not v.unidad:
        raise ValueError(
            f"'{v.clave}' no declara concepto o unidad. La ventana los "
            "necesita para rotular el campo y la memoria para escribirlo"
        )
    if v.dominio is not None and not hasattr(_dominios, v.dominio):
        raise ValueError(
            f"'{v.clave}' dice que su dominio fisico es '{v.dominio}', que no "
            "existe en dominios.py. El dominio se nombra POR NOMBRE y no por "
            "valor, justamente para que no pueda apuntar a nada"
        )
    if (v.criterio_destino is not None
            and v.criterio_destino not in _ca.CRITERIOS):
        raise ValueError(
            f"'{v.clave}' dice que su eleccion la recibe "
            f"'{v.criterio_destino}', que no es un criterio declarado"
        )
    if isinstance(v.resolucion, Derivada):
        for origen in v.resolucion.de:
            if origen not in VARIABLES and origen not in _ids_del_registro():
                raise ValueError(
                    f"'{v.clave}' se deriva de '{origen}', que no es ni otra "
                    "variable de entrada ni una tabla del registro"
                )
    if (isinstance(v.resolucion, Libre) and v.resolucion.opciones
            and v.poblacion is not Poblacion.COLUMNA_CSV):
        raise ValueError(
            f"'{v.clave}' declara `Libre.opciones` fuera del CSV; el conjunto "
            "cerrado de un criterio vive en su `sensibilidad`"
        )


@lru_cache(maxsize=1)
def _ids_del_registro() -> frozenset:
    reg = _registro_normativo.construir()
    return frozenset(t.id for t in reg.tablas) | frozenset(reg.ids_de_fuente())


def _verificar_desviaciones() -> None:
    """
    Una desviacion declarada tiene que ser una desviacion REAL: si alguien
    corrige la variable y el censo pasa a seguir el ejemplo del plan, la
    entrada de `DESVIACIONES_DEL_PLAN` deja de ser verdad y hay que retirarla.
    """
    for d in DESVIACIONES_DEL_PLAN:
        if d.variable not in VARIABLES:
            raise ValueError(
                f"`DESVIACIONES_DEL_PLAN` habla de '{d.variable}', que no es "
                "una variable de entrada"
            )
        if VARIABLES[d.variable].modo.value == d.modo_del_plan.split()[0]:
            raise ValueError(
                f"'{d.variable}' se declara como desviacion del plan y hoy se "
                f"resuelve como el plan dice ({d.modo_del_plan}). La "
                "desviacion ya no existe: retirala"
            )
        if not d.por_que:
            raise ValueError(
                f"la desviacion de '{d.variable}' no dice por que")


def _coherencia_del_censo() -> None:
    """Somete TODO el censo a la guardia, al importar el modulo."""
    _verificar_censo()
    for v in VARIABLES.values():
        _verificar_variable(v)
    _verificar_desviaciones()


_coherencia_del_censo()


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def variable(clave: str) -> VariableDeEntrada:
    """La variable de entrada, sea de la poblacion que sea."""
    try:
        return VARIABLES[clave]
    except KeyError:
        raise KeyError(
            f"'{clave}' no es una variable de entrada de este expediente. Las "
            f"hay en tres poblaciones: {len(COLUMNAS)} columnas del CSV, "
            f"{len(_ds.DATOS_SITIO)} datos de sitio y "
            f"{len(_ca.CRITERIOS)} criterios adoptados"
        ) from None


def por_modo() -> Dict[ModoDeResolucion, Tuple[VariableDeEntrada, ...]]:
    """
    Las variables agrupadas por el modo con que se resuelven. Es la vista que
    la GUI necesita: un grupo, una ventana.
    """
    salida: Dict[ModoDeResolucion, List[VariableDeEntrada]] = {
        m: [] for m in ModoDeResolucion}
    for v in sorted(VARIABLES.values(), key=lambda v: v.clave):
        salida[v.modo].append(v)
    return {m: tuple(vs) for m, vs in salida.items()}


def por_poblacion() -> Dict[Poblacion, Tuple[VariableDeEntrada, ...]]:
    """Las variables agrupadas por la poblacion de la que vienen."""
    salida: Dict[Poblacion, List[VariableDeEntrada]] = {
        p: [] for p in Poblacion}
    for v in sorted(VARIABLES.values(), key=lambda v: v.clave):
        salida[v.poblacion].append(v)
    return {p: tuple(vs) for p, vs in salida.items()}


def tabla_de(clave: str) -> Tuple:
    """
    Las tablas del registro que la ventana de una variable `de_tabla` tiene
    que mostrar ENTERAS, con su numeral, su pagina y sus notas.
    """
    v = variable(clave)
    if not isinstance(v.resolucion, DeTabla):
        raise ValueError(
            f"'{clave}' se resuelve `{v.modo.value}`, no `de_tabla`: no hay "
            "tabla que mostrar"
        )
    reg = _registro_normativo.construir()
    return tuple(reg.tabla(t) for t in v.resolucion.tablas)


def rango_de(clave: str):
    """
    El rango normativo de una variable `en_rango`, tal como el registro lo
    declara. LA SEMANTICA ES EL TIPO: quien lo pinte tiene que leer el tipo,
    no suponer que un par de numeros es un minimo y un maximo.
    """
    v = variable(clave)
    if not isinstance(v.resolucion, EnRango):
        raise ValueError(
            f"'{clave}' se resuelve `{v.modo.value}`, no `en_rango`: no hay "
            "rango que mostrar"
        )
    r = v.resolucion
    tabla = _registro_normativo.construir().tabla(r.tabla_id)
    return tabla.fila(r.fila_id).valores[r.columna_id]


def variables_con_tabla_pendiente() -> Tuple[Tuple[str, str], ...]:
    """
    Las variables que serian `de_tabla` el dia que su tabla se transcriba al
    registro, con el nombre de la tabla que falta. Es la lista de trabajo que
    este censo produce.
    """
    return tuple(
        (v.clave, v.resolucion.tabla_pendiente)
        for v in sorted(VARIABLES.values(), key=lambda v: v.clave)
        if isinstance(v.resolucion, Libre) and v.resolucion.tabla_pendiente
    )


def variables_sin_consumidor() -> Tuple[str, ...]:
    """
    Las que ningun modulo de calculo invoca. No es lo mismo que un vacio: una
    variable puede estar bien declarada y esperando a que su fase se ensamble.
    Lo que la lista permite es distinguir las dos cosas mirando la fase que
    cada una declara.
    """
    return tuple(v.clave for v in sorted(VARIABLES.values(),
                                         key=lambda v: v.clave)
                 if not v.consumido_por)


# Ancho de la regla de los bloques de texto del reporte. Es formato de
# salida, no un valor de proyecto: cambiarlo no mueve ninguna magnitud.
_ANCHO = 78    # literal-ok: ancho de la regla del reporte, no es magnitud


def reporte_variables(poblacion: Optional[Poblacion] = None) -> str:
    """
    Bloque de declaracion del censo, hermano de
    `criterios_adoptados.reporte_criterios` y de
    `datos_sitio.reporte_datos_sitio`.

    A diferencia de esos dos, este NO imprime valores: imprime como se
    resuelve cada variable. Es lo que M11 necesita para decir "el valor X vino
    de la fila R de la tabla T" y lo que la GUI necesita para saber que
    ventana abrir.
    """
    grupos = por_poblacion()
    if poblacion is not None:
        grupos = {poblacion: grupos[poblacion]}

    out = ["=" * _ANCHO,
           "MODO DE RESOLUCION DE LAS VARIABLES DE ENTRADA",
           "=" * _ANCHO,
           f"{len(VARIABLES)} variables en tres poblaciones.", ""]

    conteo = {m: len(vs) for m, vs in por_modo().items() if vs}
    out.append("Por modo: " + ", ".join(
        f"{m.value} {n}" for m, n in sorted(conteo.items(),
                                            key=lambda kv: -kv[1])))
    out.append("")

    for pob, variables in grupos.items():
        out.append("-" * _ANCHO)
        out.append(f"{pob.value.upper()} ({len(variables)})")
        out.append("-" * _ANCHO)
        for v in variables:
            out.append(f"[{v.modo.value}] {v.clave}  ({v.unidad})")
            out.append(f"     Concepto : {v.concepto}")
            out.append(f"     Fase     : {v.fase}")
            out.append(f"     Se lee   : {como_se_lee(v)}")
            if v.dominio:
                out.append(f"     Dominio  : dominios.{v.dominio} "
                           f"- no es normativo: fuera de el la celda esta mal "
                           f"llenada")
            if v.criterio_destino and v.criterio_destino != v.clave:
                out.append(f"     Alimenta : criterio '{v.criterio_destino}'")
            if v.nota:
                out.append(f"     Nota     : {v.nota}")
            out.append("")

    if DESVIACIONES_DEL_PLAN:
        out.append("-" * _ANCHO)
        out.append("DONDE ESTE CENSO SE APARTA DE LOS EJEMPLOS DE LA Sec. 4.3")
        out.append("-" * _ANCHO)
        for d in DESVIACIONES_DEL_PLAN:
            out.append(f"  - {d.variable}: el plan lo pone de ejemplo de "
                       f"`{d.modo_del_plan}`; aqui es `{d.modo_adoptado}`.")
            out.append(f"    {d.por_que}")
        out.append("")

    pendientes = variables_con_tabla_pendiente()
    if pendientes:
        out.append("-" * _ANCHO)
        out.append("SERIAN `de_tabla` SI SU TABLA SE TRANSCRIBIERA AL REGISTRO")
        out.append("-" * _ANCHO)
        for clave, tabla in pendientes:
            out.append(f"  - {clave}: {tabla}")
        out.append("")

    return "\n".join(out)


def como_se_lee(v: VariableDeEntrada) -> str:
    """
    Una linea que dice de donde sale el valor, segun el modo.

    ERA PRIVADA y la usaba solo `reporte_variables`. Se hizo publica en S22
    para que la ayuda del CSV de la pestana 1 la reutilice en vez de volver a
    recorrer los seis modos: dos lecturas del mismo `Resolucion` acabarian
    diciendo cosas distintas del mismo dato, y una de las dos seria la que el
    proyectista lee antes de llenar su archivo.
    """
    r = v.resolucion
    if isinstance(r, Libre):
        texto = r.que_lo_fija
        if r.opciones:
            texto += f" · opciones: {', '.join(r.opciones)}"
        return texto
    if isinstance(r, DeTabla):
        donde = ", ".join(r.tablas)
        detalle = r.que_elige
        if r.fila_id:
            detalle += f" (fila '{r.fila_id}')"
        if r.columna_id:
            detalle += f" (columna '{r.columna_id}')"
        if r.laguna:
            detalle += f" · LAGUNA DE LA FUENTE: {r.laguna}"
        return f"de la tabla {donde}: {detalle}"
    if isinstance(r, EnRango):
        rango = rango_de(v.clave)
        return (f"dentro del rango de {r.tabla_id} ({r.fila_id}, "
                f"{r.columna_id}) · {rango.rotulo_obligatorio} · "
                f"{r.que_acota}")
    if isinstance(r, Derivada):
        return f"se deriva de {', '.join(r.de)}: {r.regla}"
    if isinstance(r, DeEnsayo):
        return (f"{r.ensayo} · TRAZABILIDAD OBLIGATORIA: "
                f"{r.trazabilidad_exigida}")
    if isinstance(r, DeCatalogo):
        return (f"del catalogo {r.catalogo_id}: {r.que_elige} · "
                f"NO ES NORMA: {r.advertencia}")
    raise TypeError(f"modo no contemplado en el reporte: {type(r).__name__}")


if __name__ == "__main__":
    print(reporte_variables())
