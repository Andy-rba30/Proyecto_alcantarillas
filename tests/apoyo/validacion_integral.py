"""
tests/apoyo/validacion_integral.py
==================================
La VALIDACION INTEGRAL de las tres familias (T-11 de la cadena T): corre el
juego de datos de prueba de `tests/fixtures/juego_validacion_integral.py`
de punta a punta a `--alcance expediente`, corre el fixture SIN juego,
quita del juego una entrada a la vez y corre cada variante, y con todo eso
GENERA `docs/validacion_integral.md`. `tests/test_t11_validacion_integral.py`
lo regenera a memoria y lo compara con el archivo (como la guia de perfil y
los cuatro documentos generados de `docs/`), de modo que el documento no se
puede desincronizar del programa sin que la suite lo diga.

Regenerar::

    python -m tests.apoyo.validacion_integral --escribir

LOS JUICIOS, ESCRITOS AQUI PARA QUE SE PUEDAN AUDITAR
-----------------------------------------------------
1. «LLEGA A LA FASE 11 CON DISEÑO» quiere decir, y nada mas: el punto salio
   DIMENSIONADO (MD acepto un material y una seccion: `InformePunto.
   dimensionado`) y la memoria de la Fase 11 que la corrida emite
   (`M11.memoria_html`) lleva su bloque (`M11.ancla_de_punto`) y el cuadro
   resumen su fila. NO quiere decir que el cabezal cumpla: las filas E y A
   del cabezal son RESULTADOS de la Fase 9 y se imprimen como tales (el
   dueño decidio no iterar la zapata, ficha T7B-09).
2. «LLEGA CON UN BLOQUEO» quiere decir que la corrida termino (ninguna
   excepcion salio de `servicio.correr`: solo se capturan las de
   `ErrorProyecto`) y que el bloqueo del punto se CLASIFICA en una de las
   tres clases de PRECISIONES_T-11 (`clasificar`): entrada del proyecto que
   falta, criterio que el Propietario o el proyectista debe declarar, o
   metodo diferido con ficha. Un bloqueo que no cae en ninguna es un fallo
   del test, no una cuarta clase.
3. «LA LISTA EXACTA DE LO QUE SIGUE REQUIRIENDO ENTRADA» no se escribe a
   mano: es lo que la corrida por defecto bloquea MAS lo que, quitado de a
   uno, hace aparecer un bloqueo en CUALQUIERA DE LAS DOS BASES --el juego
   completo (`quitar_una`) y el juego con las decisiones de archivo
   (`quitar_una_en_la_titular`; correcciones de T-11, H1)--. Es la lista
   ADEMAS de las columnas obligatorias del CSV, y lo que ninguna de las dos
   bases dispara se nombra como «condicional no medida»
   (`CONDICIONALES_NO_MEDIDAS`). Una entrada cuya ausencia solo cambia
   avisos o veredictos no es «requerida»: es una entrada que el resultado
   necesita para ser del sitio, y el documento la lista aparte, con su
   efecto medido.
4. LA CORRIDA TITULAR es la del juego con las decisiones de ARCHIVO
   (variante `decisiones_de_archivo`, H2): el juego pisa dos criterios con
   valor de archivo (`J.PISA_EL_ARCHIVO_PORQUE`) y eso es una variante, no
   el resultado que el documento presenta primero.

Lo que este modulo NO hace: no calcula (lee el `Informe`, el volcado JSON
de `cli.informe_json` y la memoria), no escribe en `src/` y no declara nada
fuera de la corrida: cada corrida parte del estado vacio de declaraciones y
lo repone al salir, como `indice_formulas.correr_referencia`.
"""

from __future__ import annotations

import copy
import csv
import io
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cli
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import servicio
from src.modelos import TipoDeBloqueo
from src.modulos import M11_reporte as M11
from tests.fixtures import juego_validacion_integral as J

RAIZ = Path(__file__).resolve().parents[2]
DOCUMENTO = RAIZ / "docs" / "validacion_integral.md"
CSV_FIXTURE = RAIZ / "tests" / "ejemplo_puntos.csv"
DECISIONES = RAIZ / "docs" / "decisiones_diferidas.md"
CONTRATO = RAIZ / "docs" / "contrato_entradas.md"

ALCANCE = servicio.ALCANCE_EXPEDIENTE

# ---------------------------------------------------------------------------
# Las tres clases de bloqueo (PRECISIONES_T-11, punto 1)
# ---------------------------------------------------------------------------
CLASE_ENTRADA = "entrada del proyecto que falta"
CLASE_CRITERIO = "criterio que el Propietario o el proyectista debe declarar"
CLASE_METODO = "metodo diferido con ficha"
# La cuarta salida, que NO es una clase de bloqueo de la corrida por defecto
# ni de la completa (el test lo exige): un punto al que, con una entrada
# quitada, ninguna seccion le cumple. Es un RESULTADO del calculo con la
# regla que rige sin el dato (`DisenoNoFactibleError` lleva el motivo), y
# solo puede salir en §4 y §5.
CLASE_NO_FACTIBLE = "resultado: ningun material ni seccion cumple"

# Los criterios sin valor de archivo que son, en el fondo, un DATO del
# proyecto (un ensayo, una lectura) y no una eleccion: los que el registro
# marca como pendientes de ensayo ([S] o `DeEnsayo`) mas los que el contrato
# de entradas atribuye a un estudio aunque se declaren como [A] con ventana:
# el angulo de friccion del relleno (EMS) y el nivel del receptor
# (`TW_receptor`, ANA / Junta de Usuarios: H11 de la auditoria de T-11, que
# lo veia clasificado como «decision»).
CRITERIOS_QUE_SON_DATO_POR_CONTRATO: Dict[str, str] = {
    "phi_relleno_trasdos": "ensayo",
    "TW_receptor": "dato del receptor (ANA / Junta)",
}

# Cada bloqueo de «metodo no evaluable» o «diferido por alcance» se nombra
# por su ficha. La tabla es de este modulo y el test exige que (a) todo
# bloqueo de esas dos clases que cualquier corrida de la validacion produzca
# case con una fila y (b) la ficha exista en `docs/decisiones_diferidas.md`:
# una forma nueva de no evaluar no entra en silencio.
FICHA_DEL_METODO: Tuple[Tuple[str, str, str], ...] = (
    # (texto que el mensaje o la etapa contiene, ficha, que falta). El orden
    # importa: gana la primera que case.
    ("'drenaje_trasdos' = 'sin_drenaje'", "T7B-05",
     "condicion sismica con el trasdos sin drenaje (relleno saturado): "
     "equilibrio limite generalizado (GLE) con el agua del relleno"),
    ("agua en el plano de empuje", "T7B-06",
     "empuje sismico con el relleno saturado: equilibrio limite "
     "generalizado (GLE) con el agua del relleno"),
    ("procedimiento simplificado", "T7C-03",
     "procedimiento general de cortante de AASHTO 5.7.3.4.2"),
    ("ALCANCE DEL REQUISITO DE LA SEC. 2.3", "VC1-01",
     "la alteracion de la rasante hidraulica del canal (Familia C)"),
)


@dataclass(frozen=True)
class BloqueoClasificado:
    punto: str
    clase: str
    tipo: str
    etapa: str
    que: str          # el campo, el criterio o la ficha
    destraba: str     # lo que lo resuelve, en una linea


def _origen_del_criterio(clave: str) -> str:
    if clave in ds.DATOS_SITIO:
        return "dato de sitio [S]"
    c = ca.CRITERIOS.get(clave)
    if c is None:
        return "?"
    if clave in CRITERIOS_QUE_SON_DATO_POR_CONTRATO:
        return CRITERIOS_QUE_SON_DATO_POR_CONTRATO[clave]
    if c.etiqueta == "S" or type(c.resolucion).__name__ == "DeEnsayo":
        return "ensayo"
    return "decision"


def ficha_del_metodo(texto: str) -> Optional[Tuple[str, str]]:
    for marca, ficha, falta in FICHA_DEL_METODO:
        if marca in texto:
            return ficha, falta
    return None


def clasificar(id_punto: str, b: Any) -> BloqueoClasificado:
    """
    La clase de un `Bloqueo`, por su TIPO (la taxonomia de excepciones de
    CLAUDE.md) y, para un criterio pendiente, por el origen del criterio.
    Lanza `ValueError` para un tipo que no cae en ninguna de las tres
    clases: un `DisenoNoFactibleError`, un `DatoInvalidoError` o un
    `LimiteNumericoError` en la validacion son un hallazgo, no una clase.
    """
    tipo = b.tipo
    if tipo is TipoDeBloqueo.DATO_FALTANTE:
        return BloqueoClasificado(id_punto, CLASE_ENTRADA, tipo.value, b.etapa,
                                  str(b.campo), _primera_frase(b.mensaje))
    if tipo is TipoDeBloqueo.CRITERIO_PENDIENTE:
        origen = _origen_del_criterio(str(b.criterio))
        clase = CLASE_CRITERIO if origen == "decision" else CLASE_ENTRADA
        return BloqueoClasificado(id_punto, clase, tipo.value, b.etapa,
                                  str(b.criterio), f"{origen}: "
                                  + _primera_frase(b.fuente or b.mensaje))
    if tipo in (TipoDeBloqueo.METODO_NO_EVALUABLE,
                TipoDeBloqueo.DIFERIDO_POR_ALCANCE):
        f = ficha_del_metodo(f"{b.etapa} {b.mensaje}")
        if f is None:
            raise ValueError(f"bloqueo de metodo sin ficha en {id_punto}: "
                             f"{b.etapa} -- {b.mensaje[:200]}")
        return BloqueoClasificado(id_punto, CLASE_METODO, tipo.value, b.etapa,
                                  f[0], f[1])
    if tipo is TipoDeBloqueo.DISENO_NO_FACTIBLE:
        return BloqueoClasificado(id_punto, CLASE_NO_FACTIBLE, tipo.value,
                                  b.etapa, "Fase 5", _primera_frase(b.mensaje))
    raise ValueError(f"bloqueo fuera de las tres clases en {id_punto}: "
                     f"{tipo.value} -- {b.etapa} -- {b.mensaje[:200]}")


def _primera_frase(texto: Optional[str]) -> str:
    texto = " ".join(str(texto or "").split())
    corte = texto.find(". ")
    return (texto if corte < 0 else texto[:corte + 1])[:240]


# ---------------------------------------------------------------------------
# El juego como dato mutable, y las variantes
# ---------------------------------------------------------------------------

@dataclass
class Juego:
    celdas: Dict[Tuple[str, str], str]
    externos: Dict[str, Any]
    sitio: Dict[str, Dict[str, Any]]
    declaraciones: Dict[str, Any]
    hidrologia: bool = True
    caudal_vacio: Tuple[str, ...] = ()

    def copia(self) -> "Juego":
        return copy.deepcopy(self)


def juego_completo() -> Juego:
    return Juego(dict(J.CELDAS), copy.deepcopy(J.EXTERNOS),
                 copy.deepcopy(J.SITIO), copy.deepcopy(J.DECLARACIONES))


def aplicar(juego: Juego, cambios: Sequence[Tuple[Any, ...]]) -> Juego:
    """El juego con los `cambios` de una variante (ver `J.VARIANTES`)."""
    j = juego.copia()
    for cambio in cambios:
        clase = cambio[0]
        if clase == "celda":
            _, id_punto, columna, texto = cambio
            if texto is None:
                j.celdas.pop((id_punto, columna), None)
            else:
                j.celdas[(id_punto, columna)] = texto
        elif clase == "externo":
            _, donde, clave, valor = cambio
            seccion = (j.externos["globales"] if donde == "globales"
                       else j.externos["puntos"].setdefault(donde, {}))
            if valor is None:
                seccion.pop(clave, None)
            else:
                seccion[clave] = valor
        elif clase == "declarar":
            _, clave, valor = cambio
            if valor is None:
                j.declaraciones.pop(clave, None)
            else:
                j.declaraciones[clave] = valor
        elif clase == "sitio":
            _, clave, valor = cambio
            if valor is None:
                j.sitio.pop(clave, None)
            else:
                j.sitio[clave] = valor
        elif clase == "hidrologia":
            j.hidrologia = bool(cambio[1])
        elif clase == "csv_caudal_vacio":
            j.caudal_vacio = tuple(cambio[1])
        else:
            raise ValueError(f"cambio desconocido: {cambio!r}")
    return j


# ---------------------------------------------------------------------------
# Materializar: los archivos que la CLI lee
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Entradas:
    csv: Path
    externos: Path
    sitio: Path
    cuencas: Optional[Path]
    estacion: Optional[Path]
    declaraciones: Dict[str, Any]


def materializar(juego: Juego, destino: Path) -> Entradas:
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    filas = list(csv.reader(io.StringIO(CSV_FIXTURE.read_text(encoding="utf-8"))))
    cabecera = filas[0]
    ids = {f[0] for f in filas[1:]}
    for (id_punto, columna) in juego.celdas:
        if id_punto not in ids or columna not in cabecera:
            raise ValueError(f"celda inexistente: {(id_punto, columna)}")
    for fila in filas[1:]:
        for (id_punto, columna), texto in juego.celdas.items():
            if fila[0] == id_punto:
                fila[cabecera.index(columna)] = texto
        if fila[0] in juego.caudal_vacio:
            fila[cabecera.index("Q_m3s")] = ""
    salida = io.StringIO()
    csv.writer(salida, lineterminator="\n").writerows(filas)
    ruta_csv = destino / "puntos.csv"
    ruta_csv.write_text(salida.getvalue(), encoding="utf-8")
    ruta_ext = destino / "externos.json"
    ruta_ext.write_text(json.dumps(juego.externos, indent=1, ensure_ascii=False),
                        encoding="utf-8")
    ruta_sitio = destino / "sitio.json"
    ruta_sitio.write_text(json.dumps(juego.sitio, indent=1, ensure_ascii=False),
                          encoding="utf-8")
    return Entradas(ruta_csv, ruta_ext, ruta_sitio,
                    J.CUENCAS if juego.hidrologia else None,
                    J.ESTACION if juego.hidrologia else None,
                    dict(juego.declaraciones))


# --- La tercera corrida de referencia del indice de formulas (ficha T10-02)
# es ESTE juego con la variante `caudal_calculado`, escrito en su carpeta.
# `escribir_corrida_de_referencia` la (re)escribe y el test exige que los
# archivos versionados sean exactamente su salida: no es una copia que pueda
# divergir del juego.
CORRIDA_DE_REFERENCIA = RAIZ / "tests" / "fixtures" / "corridas_de_referencia" \
    / "hidrologia_calculada"
VARIANTE_DE_REFERENCIA = "caudal_calculado"


# Tres de los seis archivos de la corrida (el CSV de puntos y los JSON de
# datos externos y de declaraciones) no admiten la cabecera «DATOS DE PRUEBA,
# NO DEL PROYECTO»: el rotulo va en un LEEME de la carpeta (correcciones de
# T-11, H12), escrito por la misma funcion que los materializa.
LEEME_CORRIDA_DE_REFERENCIA = (
    f"# {J.ROTULO}\n\n"
    "Esta carpeta es la tercera corrida de referencia del índice de fórmulas "
    "(`src/indice_formulas.py::CORRIDAS_DE_REFERENCIA`, ficha T10-02): el "
    "juego de la validación integral de T-11 "
    "(`tests/fixtures/juego_validacion_integral.py`) con la variante "
    "`caudal_calculado`, escrito por "
    "`tests/apoyo/validacion_integral.py::escribir_corrida_de_referencia`. "
    "**Ningún valor es del proyecto**: son valores de prueba, y las cuencas "
    "y la serie son las SINTÉTICAS de T-1. El CSV de puntos y los dos JSON no "
    "admiten esta cabecera; vale para los seis archivos. No se editan a mano: "
    "un test exige que sean, byte a byte, la materialización del juego.\n")


def escribir_corrida_de_referencia(destino: Path = CORRIDA_DE_REFERENCIA) -> Path:
    """
    Los seis archivos de la corrida `hidrologia_calculada` en `destino`, y
    su `LEEME.md` rotulado.
    """
    juego = aplicar(juego_completo(), J.VARIANTES[VARIANTE_DE_REFERENCIA][1])
    e = materializar(juego, destino)
    (Path(destino) / "LEEME.md").write_text(LEEME_CORRIDA_DE_REFERENCIA,
                                            encoding="utf-8")
    (Path(destino) / "declaraciones.json").write_text(
        json.dumps(e.declaraciones, indent=1, ensure_ascii=False),
        encoding="utf-8")
    for origen, nombre in ((e.cuencas, "cuencas.csv"),
                           (e.estacion, "estacion.csv")):
        (Path(destino) / nombre).write_bytes(Path(origen).read_bytes())
    return Path(destino)


def argumentos_cli(e: Entradas, *, alcance: str = ALCANCE) -> List[str]:
    """Los argumentos de `cli.py` para correr el juego por la puerta real."""
    args = [str(e.csv), "--alcance", alcance, "--datos-externos", str(e.externos),
            "--datos-sitio", str(e.sitio)]
    if e.cuencas is not None:
        args += ["--cuencas", str(e.cuencas), "--estacion", str(e.estacion)]
    for clave, valor in e.declaraciones.items():
        args += ["--declarar", f"{clave}={valor!r}"]
    return args


# ---------------------------------------------------------------------------
# Correr, con el estado del proceso aislado
# ---------------------------------------------------------------------------

def correr(e: Optional[Entradas], *, alcance: str = ALCANCE) -> Any:
    """
    `servicio.correr` sobre las entradas `e` (o sobre el fixture desnudo, con
    `e` None), con las declaraciones en caliente y los [S] por sesion VACIOS
    al entrar y REPUESTOS al salir. Las puertas son las de la CLI:
    `cargar_datos_sitio`, `establecer_valor_dinamico` (la guardia de
    `--declarar`), `cargar_datos_externos` y `cargar_hidrologia`.
    """
    previas = ca.valores_dinamicos()
    sitio_previo = ds.datos_dinamicos()
    for clave in previas:
        ca.quitar_valor_dinamico(clave)
    ds.limpiar_datos_dinamicos()
    try:
        if e is None:
            externos = servicio.cargar_datos_externos(None, {})
            return servicio.correr(CSV_FIXTURE, externos, alcance=alcance)
        servicio.cargar_datos_sitio(e.sitio)
        for clave, valor in e.declaraciones.items():
            ca.establecer_valor_dinamico(clave, valor)
        externos = servicio.cargar_datos_externos(e.externos, {})
        hidro = servicio.cargar_hidrologia(e.cuencas, e.estacion)
        return servicio.correr(e.csv, externos, alcance=alcance,
                               hidrologia=hidro)
    finally:
        for clave in ca.valores_dinamicos():
            ca.quitar_valor_dinamico(clave)
        for clave, valor in previas.items():
            ca.establecer_valor_dinamico(clave, valor)
        ds.limpiar_datos_dinamicos()
        for clave, d in sitio_previo.items():
            ds.establecer_dato_dinamico(clave, d.dato.valor, d.dato.trazabilidad,
                                        d.fecha, origen=d.origen)


def correr_juego(juego: Optional[Juego] = None, *, alcance: str = ALCANCE) -> Any:
    with tempfile.TemporaryDirectory(prefix="t11_") as tmp:
        return correr(materializar(juego or juego_completo(), Path(tmp)),
                      alcance=alcance)


# ---------------------------------------------------------------------------
# Lo que se lee de un informe
# ---------------------------------------------------------------------------

_VOLCADOS: Dict[int, Tuple[Any, Dict[str, Any]]] = {}


def volcado(informe: Any) -> Dict[str, Any]:
    """
    `cli.informe_json(informe)`, calculado una vez por informe. Las
    verificaciones se leen de AQUI y no del objeto: el volcado reune las del
    conducto, las del cabezal y las de la Fase 10 (VB1, VB2), que viven en
    tres objetos distintos del `InformePunto`.
    """
    hit = _VOLCADOS.get(id(informe))
    if hit is None or hit[0] is not informe:
        hit = (informe, cli.informe_json(informe))
        _VOLCADOS[id(informe)] = hit
        while len(_VOLCADOS) > 8:        # los informes pesan: solo los ultimos
            del _VOLCADOS[next(iter(_VOLCADOS))]
    return hit[1]


def verificaciones_del_punto(informe: Any, id_punto: str) -> Dict[str, str]:
    """Codigo -> estado, de todas las verificaciones del punto en el volcado."""
    for p in volcado(informe)["puntos"]:
        if p["id"] == id_punto:
            return {str(v["codigo"]): str(v["estado"])
                    for v in p.get("verificaciones") or []}
    raise KeyError(id_punto)


def resumen_del_punto(informe: Any, p: Any) -> Dict[str, Any]:
    r = p.resultado
    return {
        "id": p.punto.id,
        "familia": p.punto.familia.value,
        "dimensionado": bool(p.dimensionado),
        "material": r.material.nombre if r is not None else None,
        "seccion": r.seccion.etiqueta() if r is not None else None,
        "bloqueos": tuple(clasificar(p.punto.id, b) for b in p.bloqueos),
        "verificaciones": verificaciones_del_punto(informe, p.punto.id),
    }


def bloqueos_del_proyecto(informe: Any) -> Tuple[BloqueoClasificado, ...]:
    """Los de la Fase 9 del PROYECTO (recubrimientos, cadena sismica)."""
    cab = informe.cabezal
    return tuple(clasificar("proyecto", b) for b in (cab.bloqueos if cab else ()))


def todos_los_bloqueos(informe: Any) -> Tuple[BloqueoClasificado, ...]:
    return tuple(c for p in informe.puntos
                 for c in resumen_del_punto(informe, p)["bloqueos"]) \
        + bloqueos_del_proyecto(informe)


def llega_a_la_fase_11(informe: Any) -> Dict[str, Tuple[bool, bool]]:
    """
    Por punto: (su bloque esta en la memoria de la Fase 11, su fila esta en
    el cuadro resumen). Es la definicion operativa del juicio 1.
    """
    html = M11.memoria_html(informe)
    with tempfile.TemporaryDirectory(prefix="t11_csv_") as tmp:
        ruta = M11.exportar_csv(informe, Path(tmp) / "resumen.csv")
        filas = list(csv.reader(ruta.read_text(encoding="utf-8").splitlines()))
    ids_csv = {f[0] for f in filas[1:] if f}
    return {p.punto.id: (f'id="{M11.ancla_de_punto(p.punto.id)}"' in html,
                         p.punto.id in ids_csv)
            for p in informe.puntos}


# ---------------------------------------------------------------------------
# Quitar una entrada a la vez
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Elemento:
    etiqueta: str                       # como se imprime
    puerta: str                         # por donde entra
    cambios: Tuple[Tuple[Any, ...], ...]


def elementos_del_juego(juego: Optional[Juego] = None) -> Tuple[Elemento, ...]:
    j = juego or juego_completo()
    salida: List[Elemento] = []
    for (id_punto, columna) in sorted(j.celdas):
        salida.append(Elemento(f"{columna} ({id_punto})", "celda del CSV",
                               (("celda", id_punto, columna, None),)))
    for clave in sorted(j.externos["globales"]):
        salida.append(Elemento(f"{clave} (global)", "--datos-externos",
                               (("externo", "globales", clave, None),)))
    for id_punto in sorted(j.externos["puntos"]):
        for clave in sorted(j.externos["puntos"][id_punto]):
            salida.append(Elemento(f"{clave} ({id_punto})", "--datos-externos",
                                   (("externo", id_punto, clave, None),)))
    for clave in sorted(j.sitio):
        salida.append(Elemento(clave, "--datos-sitio",
                               (("sitio", clave, None),)))
    for clave in sorted(j.declaraciones):
        salida.append(Elemento(clave, "--declarar",
                               (("declarar", clave, None),)))
    salida.append(Elemento("--cuencas y --estacion", "--cuencas / --estacion",
                           (("hidrologia", False),)))
    return tuple(salida)


@dataclass(frozen=True)
class Efecto:
    bloqueos_nuevos: Tuple[BloqueoClasificado, ...]
    dejan_de_dimensionar: Tuple[str, ...]
    cambia_seccion: Tuple[str, ...]
    veredictos: Tuple[Tuple[str, str, str, str], ...]   # punto, codigo, antes, despues
    avisos_nuevos: int

    @property
    def clase(self) -> str:
        if any(b.clase != CLASE_NO_FACTIBLE for b in self.bloqueos_nuevos):
            return "DETIENE"
        if self.bloqueos_nuevos or self.dejan_de_dimensionar:
            return "NO FACTIBLE"
        if self.cambia_seccion:
            return "CAMBIA EL DISEÑO"
        if self.veredictos:
            return "CAMBIA VEREDICTOS"
        if self.avisos_nuevos:
            return "SOLO AVISA"
        return "SIN EFECTO MEDIBLE"


def _avisos(informe: Any) -> Dict[str, set]:
    return {p.punto.id: set(p.avisos()) for p in informe.puntos}


def efecto(base: Any, otro: Any) -> Efecto:
    rb = {p.punto.id: resumen_del_punto(base, p) for p in base.puntos}
    ro = {p.punto.id: resumen_del_punto(otro, p) for p in otro.puntos}
    clave_b = lambda b: (b.punto, b.tipo, b.etapa, b.que)  # noqa: E731
    previos = {clave_b(b) for b in todos_los_bloqueos(base)}
    nuevos = tuple(b for b in todos_los_bloqueos(otro)
                   if clave_b(b) not in previos)
    dejan = tuple(i for i in rb if rb[i]["dimensionado"] and not ro[i]["dimensionado"])
    cambia = tuple(i for i in rb if ro[i]["dimensionado"] and rb[i]["dimensionado"]
                   and (rb[i]["material"], rb[i]["seccion"])
                   != (ro[i]["material"], ro[i]["seccion"]))
    veredictos = []
    for i in rb:
        if not (rb[i]["dimensionado"] and ro[i]["dimensionado"]):
            continue
        vb, vo = rb[i]["verificaciones"], ro[i]["verificaciones"]
        for codigo in sorted(set(vb) | set(vo)):
            if vb.get(codigo) != vo.get(codigo):
                veredictos.append((i, codigo, vb.get(codigo, "—"), vo.get(codigo, "—")))
    ab, ao = _avisos(base), _avisos(otro)
    avisos = sum(len(ao[i] - ab.get(i, set())) for i in ao)
    return Efecto(nuevos, dejan, cambia, tuple(veredictos), avisos)


def quitar_una(base: Optional[Any] = None, *,
               juego: Optional[Juego] = None) -> Tuple[Tuple[Elemento, Efecto], ...]:
    """
    El efecto de quitar del `juego` (por omision, el juego completo) cada
    entrada, de a una. `base` es la corrida de ese mismo juego.
    """
    completo = juego if juego is not None else juego_completo()
    base = base if base is not None else correr_juego(completo)
    return tuple((el, efecto(base, correr_juego(aplicar(completo, el.cambios))))
                 for el in elementos_del_juego(completo))


# LA SEGUNDA BASE DE LA LISTA EXACTA (correcciones de T-11, H1 de su
# auditoria, ALTA): el juego SIN las declaraciones que pisan un valor de
# archivo --`drenaje_trasdos` y `factor_muro_eleccion` vuelven a 'sin_drenaje'
# y 'sin_reduccion'--, que es la corrida TITULAR (variante
# `decisiones_de_archivo`). Medida solo sobre el juego, la lista no veia el
# peso especifico SATURADO del relleno: con el relleno drenado no se pide, y
# con el valor de archivo (sin drenaje) detiene la estabilidad y el armado de
# los dos cabezales de los cuatro puntos. La lista es la UNION de las dos.
VARIANTE_TITULAR = "decisiones_de_archivo"


def juego_titular() -> Juego:
    """El juego con las decisiones de archivo: la corrida titular (§2)."""
    return aplicar(juego_completo(), J.VARIANTES[VARIANTE_TITULAR][1])


def quitar_una_en_la_titular(titular: Optional[Any] = None
                             ) -> Tuple[Tuple[Elemento, Efecto], ...]:
    """`quitar_una` sobre la segunda base (el juego titular)."""
    return quitar_una(titular, juego=juego_titular())


def variantes(base: Optional[Any] = None) -> Tuple[Tuple[str, str, Any, Efecto], ...]:
    completo = juego_completo()
    base = base if base is not None else correr_juego(completo)
    salida = []
    for nombre, (texto, cambios) in J.VARIANTES.items():
        informe = correr_juego(aplicar(completo, cambios))
        salida.append((nombre, texto, informe, efecto(base, informe)))
    return tuple(salida)


# ---------------------------------------------------------------------------
# El documento
# ---------------------------------------------------------------------------

def _celda(texto: Any) -> str:
    return " ".join(str(texto).split()).replace("|", "\\|")


def _tabla(encabezado: Sequence[str], filas: Sequence[Sequence[Any]]) -> List[str]:
    lineas = ["| " + " | ".join(encabezado) + " |",
              "|" + "|".join("---" for _ in encabezado) + "|"]
    for f in filas:
        lineas.append("| " + " | ".join(_celda(c) for c in f) + " |")
    return lineas


def _recorta(texto: str, n: int = 400) -> str:
    texto = " ".join(str(texto).split())
    return texto if len(texto) <= n else texto[:n - 1] + "…"


def _no_cumple(verificaciones: Dict[str, str]) -> str:
    malas = [f"{c} ({e})" for c, e in verificaciones.items()
             if e not in ("cumple", "no aplica")]
    return ", ".join(malas) if malas else "todas cumplen"


# La sensibilidad de la llegada de A-01 al caudal del evento extremo, que el
# juego toma de T-7b (1.11 veces el de diseño) sin que su linea diga por que
# es plausible (correcciones de T-11, H14). Se MIDE aqui, sobre el juego, y
# el documento lo imprime: el «llega con Ø 0.90» de A-01 depende de ese dato.
FACTORES_Q_EXTREMO_A01 = (1.5, 1.71, 1.8, 2.0)


def sensibilidad_q_extremo_A01(factores: Sequence[float] = FACTORES_Q_EXTREMO_A01
                               ) -> Tuple[Tuple[float, float, str, str], ...]:
    """
    (factor, Q del evento extremo, seccion de A-01, lo que incumplio el
    primer escalon) con `Q_evento_extremo_m3s` de A-01 = factor · Q de
    diseño, sobre el juego. Lee el volcado; no calcula.
    """
    q_diseno = next(float(f[3]) for f in csv.reader(
        CSV_FIXTURE.read_text(encoding="utf-8").splitlines()) if f[0] == "A-01")
    salida = []
    for k in factores:
        q = round(q_diseno * k, 3)
        informe = correr_juego(aplicar(juego_completo(), (
            ("externo", "A-01", "Q_evento_extremo_m3s", q),)))
        p = next(x for x in volcado(informe)["puntos"] if x["id"] == "A-01")
        seccion = p["diseno"]["seccion"] if p.get("diseno") else "no dimensiona"
        incumplidas = ", ".join((p.get("iteraciones") or [{}])[0].get(
            "incumplidas") or []) or "ninguna"
        salida.append((k, q, seccion, incumplidas))
    return tuple(salida)


def _filas_de_la_corrida(informe: Any) -> List[Tuple[Any, ...]]:
    fase11 = llega_a_la_fase_11(informe)
    filas = []
    for p in informe.puntos:
        r = resumen_del_punto(informe, p)
        bloqueos = "; ".join(f"{b.clase}: {b.que}" for b in r["bloqueos"]) or "ninguno"
        en_memoria, en_csv = fase11[p.punto.id]
        filas.append((r["id"], r["familia"],
                      "sí" if r["dimensionado"] else "no",
                      r["material"] or "—", r["seccion"] or "—",
                      f"{'sí' if en_memoria else 'NO'} / {'sí' if en_csv else 'NO'}",
                      bloqueos))
    return filas


ENCABEZADO_CORRIDA = ("Punto", "Familia", "Dimensiona", "Material", "Sección",
                      "Fase 11 (memoria / resumen)", "Bloqueos")

# Las filas del marco LRFD (el que rige) que la lectura de la corrida titular
# cuenta: las tres estaticas de cada cabezal.
FILAS_ESTATICAS_LRFD = ("E1-LRFD.est", "E2-LRFD.est", "E3-LRFD.est")


def filas_estaticas_que_no_pasan(informe: Any) -> Dict[str, int]:
    """Por fila estatica del marco LRFD, en cuantos cabezales no cumple."""
    cuenta = {f: 0 for f in FILAS_ESTATICAS_LRFD}
    for p in informe.puntos:
        v = verificaciones_del_punto(informe, p.punto.id)
        for f in FILAS_ESTATICAS_LRFD:
            for ext in ("e", "s"):
                if v.get(f"{f}.{ext}") == "no cumple":
                    cuenta[f] += 1
    return cuenta


def cabezales_evaluados(informe: Any) -> int:
    return sum(2 for p in informe.puntos if p.cabezal is not None)


def pisa_el_archivo() -> Tuple[Tuple[str, Any, Any, str], ...]:
    """
    (clave, valor de archivo, valor del juego, por que el juego lo cambia)
    de cada clave de `J.DECLARACIONES` cuyo criterio TIENE valor de archivo
    (correcciones de T-11, H2). Generado: si el juego pisa otra, sale aqui.
    """
    salida = []
    for clave, valor in J.DECLARACIONES.items():
        archivo = ca.CRITERIOS[clave].valor
        if archivo is None:
            continue
        salida.append((clave, archivo, valor,
                       J.PISA_EL_ARCHIVO_PORQUE.get(clave, "SIN RAZÓN ESCRITA")))
    return tuple(salida)


def _consumidor(clave: str) -> str:
    """
    «sí» si algun modulo consume el criterio (`variables_entrada`), o «no
    (censado)» si esta en el censo de los que ninguna corrida invoca
    (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`, que
    `variables_entrada` deriva del AST). Correcciones de T-11, H11.
    """
    from src import variables_entrada as ve
    return "sí" if ve.variable(clave).consumido_por else "no (censado)"


def generar(*, base: Any = None, por_defecto: Any = None,
            una: Any = None, var: Any = None, titular: Any = None,
            una_titular: Any = None, q_extremo: Any = None) -> str:
    base = base if base is not None else correr_juego()
    por_defecto = por_defecto if por_defecto is not None else correr(None)
    una = una if una is not None else quitar_una(base)
    var = var if var is not None else variantes(base)
    titular = titular if titular is not None else next(
        i for n, _t, i, _e in var if n == VARIANTE_TITULAR)
    una_titular = (una_titular if una_titular is not None
                   else quitar_una_en_la_titular(titular))
    q_extremo = q_extremo if q_extremo is not None else sensibilidad_q_extremo_A01()
    L: List[str] = []
    A = L.append
    A("# Validación integral de las tres familias (T-11)")
    A("")
    A("> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe "
      "`python -m tests.apoyo.validacion_integral --escribir` y "
      "`tests/test_t11_validacion_integral.py` lo regenera y lo compara. "
      "**Todos los datos de la corrida completa son DATOS DE PRUEBA, NO DEL "
      "PROYECTO** (`tests/fixtures/juego_validacion_integral.py`, con la "
      "línea de plausibilidad de cada valor).")
    A("")
    A("## 1. Qué se juzga, y con qué regla")
    A("")
    A("- **La corrida titular** es la del juego con las **decisiones de "
      "archivo** (§2): el juego pisa dos criterios que tienen valor de "
      "archivo y que el dueño confirmó, y eso se presenta como variante "
      "(§2.1), no como resultado.")
    A("- **Llega a la Fase 11 con diseño**: el punto sale dimensionado (MD "
      "aceptó material y sección) y la memoria de la Fase 11 lleva su bloque "
      "y el cuadro resumen su fila. Las filas E y A del cabezal son "
      "**resultados** de la Fase 9, no condición de llegada: la geometría del "
      "cabezal la propone la regla de T-7a y no se itera (alcance declarado, "
      "ficha T7B-09).")
    A("- **Llega con un bloqueo**: la corrida termina (ninguna excepción fuera "
      "de `ErrorProyecto`) y cada bloqueo cae en una de tres clases: "
      f"*{CLASE_ENTRADA}*, *{CLASE_CRITERIO}* o *{CLASE_METODO}*. Un bloqueo "
      "fuera de las tres es un fallo del test.")
    A("- **La lista exacta de lo que sigue requiriendo entrada** es lo que la "
      "corrida SIN juego bloquea (§3) más lo que, quitado de a uno, detiene "
      "una etapa en **cualquiera de las dos bases**: el juego (§4.1) y el "
      "juego con las decisiones de archivo (§4.2). Es la lista **además de "
      "las columnas obligatorias del CSV** (§2 del contrato: sin ellas M0 no "
      "carga). Las condicionales que ninguna de las dos bases dispara **no "
      "se midieron** y se nombran en §4.3.")
    A("")
    A("Reproducir la corrida completa por la CLI (los archivos los escribe "
      "`tests.apoyo.validacion_integral.materializar` en una carpeta "
      "temporal):")
    A("")
    A("```sh")
    A("python cli.py <tmp>/puntos.csv --alcance expediente \\")
    A("    --datos-externos <tmp>/externos.json --datos-sitio <tmp>/sitio.json \\")
    A("    --cuencas tests/fixtures/hidrologia/cuencas_prueba.csv \\")
    A("    --estacion tests/fixtures/hidrologia/estacion_prueba.csv \\")
    A("    " + " ".join(f"--declarar {k}=..." for k in sorted(J.DECLARACIONES)[:2])
      + " … (una por clave de `DECLARACIONES`)")
    A("```")
    A("")
    # --- 2 ---------------------------------------------------------------
    A("## 2. Corrida titular: el juego con las decisiones de archivo "
      "(`--alcance expediente`)")
    A("")
    A("El juego declara, sobre criterios que **tienen valor de archivo**, lo "
      "que esta tabla dice. La corrida titular los deja en su valor de "
      "archivo (variante `decisiones_de_archivo`) y declara el peso "
      "específico saturado del relleno que el relleno sin drenaje pide "
      "(ensayo del EMS, sin valor de archivo: 20 kN/m³ de prueba, con su "
      "línea en el juego).")
    A("")
    L += _tabla(("Criterio", "Valor de archivo", "Valor del juego",
                 "Por qué el juego lo cambia"),
                [(f"`{c}`", repr(a), repr(j), r) for c, a, j, r in pisa_el_archivo()])
    A("")
    L += _tabla(ENCABEZADO_CORRIDA, _filas_de_la_corrida(titular))
    A("")
    A("Verificaciones que no salen «cumple» (conducto y cabezal), por punto. "
      "Son RESULTADOS con los datos de prueba:")
    A("")
    L += _tabla(("Punto", "Verificaciones"),
                [(p.punto.id, _no_cumple(verificaciones_del_punto(titular, p.punto.id)))
                 for p in titular.puntos])
    A("")
    estaticas = filas_estaticas_que_no_pasan(titular)
    n_cab = cabezales_evaluados(titular)
    sismicas = sum(1 for b in todos_los_bloqueos(titular) if b.que == "T7B-05")
    A("Lectura de ingeniería (no la escribe el programa; las cifras sí): con "
      "las decisiones de archivo los cuatro puntos dimensionan igual que con "
      "el juego —el cabezal no entra al dimensionamiento del conducto—, y el "
      "cabezal de la regla de T-7a **no pasa la estabilidad estática del "
      "marco LRFD que rige**: "
      + ", ".join(f"`{f}` no cumple en {n} de {n_cab} cabezales"
                  for f, n in estaticas.items())
      + f". La condición **sísmica no se evalúa** ({sismicas} bloqueos "
      "«método no evaluable», ficha T7B-05: con el trasdós sin drenaje el "
      "relleno está saturado y el empuje sísmico con agua en el relleno pide "
      "un equilibrio límite generalizado que el programa no implementa). El "
      "**peso específico saturado del relleno** es un ensayo del EMS que esta "
      "rama necesita: sin él la estabilidad y el armado de los ocho "
      "cabezales se detienen (§4.2). Es la sensibilidad de una geometría que "
      "no se itera (ficha T7B-09), no un fallo de la validación.")
    A("")
    A("### 2.1 Variante que ejercita la cadena sísmica y el caso drenado: el "
      "juego tal como está")
    A("")
    A("El juego pisa las dos decisiones de la tabla de arriba (trasdós "
      "drenado, muro que admite desplazamiento) para que la cadena sísmica y "
      "el caso drenado se recorran. Es la base de los barridos de "
      "`docs/validacion_sensibilidad.md`, porque con los valores de archivo "
      "la sísmica no es evaluable.")
    A("")
    L += _tabla(ENCABEZADO_CORRIDA, _filas_de_la_corrida(base))
    A("")
    A("Verificaciones que no salen «cumple» (conducto y cabezal), por punto. "
      "Son RESULTADOS con los datos de prueba:")
    A("")
    L += _tabla(("Punto", "Verificaciones"),
                [(p.punto.id, _no_cumple(verificaciones_del_punto(base, p.punto.id)))
                 for p in base.puntos])
    A("")
    A("Lectura de ingeniería (no la escribe el programa): las filas E3 "
      "(deslizamiento) estática y E1 (capacidad portante) sísmica del marco "
      "LRFD no pasan con la zapata que propone la regla de T-7a en ninguno de "
      "los cuatro puntos; la variante `zapata_declarada_3m` (§5) muestra que "
      "con 3.00 m de zapata las de A-01 pasan, y el anexo de sensibilidad "
      "(`docs/validacion_sensibilidad.md` §3.1) mide los dos [A] de los que "
      "dependen: omitir los factores de inclinación hace pasar E1 sísmica en "
      "los cuatro, la fila de φ de muros hace pasar E3 estática a la salida "
      "de A-01, A-02 y C-01, y ninguno hace pasar E3 estática a la entrada. "
      "Las filas A1 de la pantalla y "
      "el alero de SALIDA no pasan donde la socavación baja el desplante (la "
      "pantalla crece y ninguna barra del catálogo alcanza); la variante "
      "`sin_socavacion_A01` muestra el otro lado. Ninguna de las dos es un "
      "fallo de la validación: son la sensibilidad de una geometría que no se "
      "itera (ficha T7B-09).")
    A("")
    c01 = {n: _c01_en_el_canal(i) for n, _t, i, _e in var
           if n == VARIANTE_C01_EN_EL_CANAL}
    c01["juego"] = _c01_en_el_canal(base)
    j, v = c01["juego"], c01[VARIANTE_C01_EN_EL_CANAL]
    A(f"**C-01 (Familia C).** Dimensiona el {j['seccion']} (HW "
      f"{j['HW']:.4f} m), pero con `VC2` «{j['VC2']}»: sin "
      "`cota_fondo_entrada`, la regla de archivo (`origen_cota_fondo_entrada` "
      f"= 'cota_terreno') pone la entrada en el terreno del cruce y la salida "
      f"queda {j['desnivel']:+.3f} m sobre el fondo del canal; el remanso "
      f"aguas arriba del canal {'concluye' if j['remanso'] else '«no concluye»'}"
      " por eso mismo (una descarga libre que el canal no tiene). La variante "
      f"`{VARIANTE_C01_EN_EL_CANAL}` (§5) pone la entrada en el canal: el "
      f"{v['seccion']} es el mismo (HW {v['HW']:.4f} m), la salida queda "
      f"{v['desnivel']:+.3f} m sobre el fondo del canal, `VC2` «{v['VC2']}», "
      f"`G2` «{v['G2']}» y el remanso "
      f"{'concluye' if v['remanso'] else '«no concluye»'}; la longitud pasa "
      f"de {j['L']:.2f} a {v['L']:.2f} m y el cabezal, más alto, cambia "
      "veredictos de su estabilidad (§5). El diseño del marco no depende de "
      "esa adopción, y la validación lo enseña.")
    A("")
    A("**El caudal del evento extremo de A-01** (1.11 veces el de diseño, "
      "tomado de T-7b) gobierna su llegada con Ø 0.90 m. Medido sobre el "
      "juego, con `Q_evento_extremo_m3s` = k · Q de diseño: "
      + "; ".join(f"k = {k} ({q:.3f} m³/s): {sec}, primer escalón incumple "
                  f"{inc}" for k, q, sec, inc in q_extremo)
      + ". El resultado de V8 es sensible a un dato del estudio hidrológico "
      "que el juego no sostiene: el «Ø 0.90» de A-01 vale para ese dato.")
    A("")
    # --- 3 ---------------------------------------------------------------
    A("## 3. Corrida por defecto (el fixture sin juego, `--alcance expediente`)")
    A("")
    filas = [(b.punto, b.clase, b.tipo, b.etapa, b.que, b.destraba)
             for b in todos_los_bloqueos(por_defecto)]
    L += _tabla(("Punto", "Clase", "Tipo", "Etapa", "Qué", "Lo destraba"), filas)
    A("")
    A("Sin juego ningún punto pasa de la Fase 2: la luz del cruce no es "
      "columna del CSV y la corrida se detiene en ella. Lo que cada etapa "
      "posterior pediría lo dice §4.")
    A("")
    # --- 4 ---------------------------------------------------------------
    A("## 4. Quitar una entrada a la vez")
    A("")
    A("Cada fila es una corrida: la base sin esa entrada. **DETIENE** = "
      "aparece un bloqueo de una de las tres clases; **NO FACTIBLE** = el "
      "punto deja de dimensionar sin un bloqueo de esas clases (ningún "
      "material ni sección cumple con la regla que rige sin el dato); "
      "**CAMBIA EL DISEÑO** = otro material o sección; **CAMBIA "
      "VEREDICTOS**; **SOLO AVISA**; **SIN EFECTO MEDIBLE**.")
    A("")
    A("### 4.1 Sobre el juego")
    A("")
    L += _tabla(("Entrada quitada", "Puerta", "Efecto", "Detalle"),
                [_fila_de_quitar(el, ef) for el, ef in una])
    A("")
    A("### 4.2 Sobre el juego con las decisiones de archivo (la titular)")
    A("")
    efecto_juego = {el.etiqueta: ef.clase for el, ef in una}
    distintas = [(el, ef) for el, ef in una_titular
                 if efecto_juego.get(el.etiqueta) != ef.clase]
    A(f"Se corrieron {len(una_titular)} entradas; las "
      f"{len(una_titular) - len(distintas)} que no salen aquí tienen el "
      "mismo efecto que en §4.1. Las que cambian de efecto:")
    A("")
    L += _tabla(("Entrada quitada", "Puerta", "Efecto", "Detalle"),
                [_fila_de_quitar(el, ef) for el, ef in distintas])
    A("")
    A("### 4.3 La lista exacta: lo que detiene una etapa si falta")
    A("")
    L += _tabla(("Qué falta", "Clase", "Dónde detiene"),
                [(f"`{n}`", c, _recorta(d))
                 for n, c, d in lista_exacta(por_defecto, una, una_titular)])
    A("")
    A("Cada una está nombrada en `docs/contrato_entradas.md` §7 (lo comprueba "
      "el test). Es la lista **además de las columnas obligatorias del CSV**. "
      "Lo que no está aquí no detuvo ninguna etapa al quitarlo de ninguna de "
      "las dos bases: el resultado deja de ser del sitio y la corrida lo "
      "avisa o adopta la regla escrita en su ficha. **Condicionales no "
      "medidas** (detienen sólo en una rama que ninguna de las dos bases "
      "recorre; el contrato §7 las nombra):")
    A("")
    for clave, cuando in CONDICIONALES_NO_MEDIDAS.items():
        A(f"- `{clave}` — {cuando}.")
    A("")
    # --- 5 ---------------------------------------------------------------
    A("## 5. Variantes: una decisión del juego, del otro lado")
    A("")
    filas = []
    for nombre, texto, informe, ef in var:
        res = []
        for p in informe.puntos:
            r = resumen_del_punto(informe, p)
            res.append(f"{r['id']}: " + (r["seccion"] if r["dimensionado"]
                                          else "no dimensiona"))
        detalle = []
        if ef.bloqueos_nuevos:
            detalle.append("; ".join(sorted({f"{b.punto}: {b.clase} — {b.que}"
                                             for b in ef.bloqueos_nuevos})))
        if ef.cambia_seccion:
            detalle.append("cambia la sección de " + ", ".join(ef.cambia_seccion))
        if ef.veredictos:
            detalle.append("; ".join(f"{i} {c}: {a} → {d}"
                                     for i, c, a, d in ef.veredictos))
        filas.append((f"`{nombre}`", texto, ef.clase, " · ".join(res),
                      " · ".join(detalle) or "—"))
    L += _tabla(("Variante", "Qué cambia", "Efecto", "Resultado", "Detalle"), filas)
    A("")
    declarados = {p.punto.id: p.punto.Q_m3s for p in base.puntos}
    for nombre, _texto, informe, _ef in var:
        calculados = [(p.punto.id, p.caudal.Q_m3s) for p in informe.puntos
                      if p.caudal is not None and p.caudal.calculado]
        if not calculados:
            continue
        A(f"Caudales que calcula la Fase 1-bis en `{nombre}`, frente a los "
          "declarados en el CSV del fixture: "
          + "; ".join(f"{i} {q:.3f} m³/s (declarado {declarados[i]:.3f})"
                      for i, q in calculados) + ".")
        A("")
    cocientes = [p.caudal.Q_m3s / declarados[p.punto.id]
                 for _n, _t, i, _e in var if _n == VARIANTE_DE_REFERENCIA
                 for p in i.puntos if p.caudal is not None and p.caudal.calculado]
    A("Lectura de ingeniería (no la escribe el programa; las cifras sí): **la "
      "cadena «caudal calculado → diseño» NO está validada con datos "
      "coherentes.** Las cuencas y la serie de `tests/fixtures/hidrologia/` "
      "son SINTÉTICAS, inventadas por T-1 para ejercitar el método racional "
      "y no para ser coherentes con los caudales del CSV; con ellas el "
      f"caudal es de {min(cocientes):.0f} a {max(cocientes):.0f} veces el "
      "declarado y ningún material ni sección "
      "cabe bajo la subrasante (no factible POR RASANTE, ficha T11-03). No "
      "se sabe cuál de los dos juegos es el irreal: lo que importa para la "
      "tesis es contrastar los caudales del fixture con el estudio "
      "hidrológico real. Queda para el lote posterior a la cadena (decisión "
      "del dueño, prioridad baja) un juego sintético de cuencas COHERENTE "
      "con el CSV —áreas, coeficientes y una serie que den caudales del "
      "orden de los declarados— para que una corrida recorra esa cadena de "
      "punta a punta con diseño.")
    A("")
    # --- 6 ---------------------------------------------------------------
    A("## 6. Criterios sin valor de archivo")
    A("")
    A("Ningún criterio se rellenó en `criterios_adoptados.py`: los que el "
      "juego necesita entran por `--declarar`. Esta es la lista entera de los "
      "que el archivo deja sin valor, con lo que los destraba y si algún "
      "módulo los consume: «no (censado)» es un criterio que ninguna corrida "
      "invoca (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`, "
      f"{len(_sin_consumidor())} en todo el archivo): declararlo no destraba "
      "ninguna etapa.")
    A("")
    filas = []
    for clave, c in ca.CRITERIOS.items():
        if c.valor is not None:
            continue
        filas.append((f"`{clave}`", f"[{c.etiqueta}]", c.nivel,
                      "opcional" if getattr(c, "opcional", False) else "—",
                      _origen_del_criterio(clave), _consumidor(clave),
                      "sí" if clave in J.DECLARACIONES else "no",
                      _primera_frase(c.fuente)))
    L += _tabla(("Criterio", "Etiqueta", "Nivel", "Opcional", "Qué es",
                 "Consumidor", "Lo declara el juego",
                 "Fuente / lo que lo destraba"), filas)
    A("")
    return "\n".join(L) + "\n"


VARIANTE_C01_EN_EL_CANAL = "C01_fondo_en_el_canal"


def _c01_en_el_canal(informe: Any) -> Dict[str, Any]:
    """Lo que §2.1 dice de C-01, leido del volcado (no calcula)."""
    p = next(x for x in volcado(informe)["puntos"] if x["id"] == "C-01")
    g, d = p["geometria"], p["diseno"]
    v = verificaciones_del_punto(informe, "C-01")
    return {"seccion": d["seccion"], "HW": d["HW_gobernante_m"],
            "desnivel": g["desnivel_entrega_m"], "L": g["longitud_m"],
            "VC2": v.get("VC2", "—"), "G2": v.get("G2", "—"),
            "remanso": bool((g.get("remanso_canal") or {}).get("concluye"))}


def _sin_consumidor() -> Tuple[str, ...]:
    from src import variables_entrada as ve
    return tuple(sorted(c for c in ca.CRITERIOS
                        if not ve.variable(c).consumido_por))


def _fila_de_quitar(el: Elemento, ef: Efecto) -> Tuple[str, str, str, str]:
    detalle = []
    if ef.bloqueos_nuevos:
        detalle.append("; ".join(sorted({f"{b.punto}: {b.clase} — {b.que}"
                                         for b in ef.bloqueos_nuevos})))
    if ef.dejan_de_dimensionar:
        detalle.append("no dimensiona " + ", ".join(ef.dejan_de_dimensionar))
    if ef.cambia_seccion:
        detalle.append("cambia la sección de " + ", ".join(ef.cambia_seccion))
    if ef.veredictos:
        detalle.append(f"{len(ef.veredictos)} veredictos")
    if ef.avisos_nuevos:
        detalle.append(f"{ef.avisos_nuevos} avisos nuevos")
    return (el.etiqueta, el.puerta, ef.clase, " · ".join(detalle) or "—")


ROTULO_BASE_TITULAR = " (con las decisiones de archivo)"


def lista_exacta(por_defecto: Any,
                 una: Sequence[Tuple[Elemento, Efecto]],
                 una_titular: Sequence[Tuple[Elemento, Efecto]] = ()
                 ) -> Tuple[Tuple[str, str, str], ...]:
    """
    LA LISTA EXACTA de lo que sigue requiriendo entrada (juicio 3), como
    (nombre, clase, donde detiene): lo que bloquea la corrida por defecto
    (salvo los metodos diferidos, que no son una entrada) mas lo que,
    quitado de CUALQUIERA DE LAS DOS BASES --el juego (`una`) y el juego con
    las decisiones de archivo (`una_titular`, correcciones de T-11, H1)--,
    DETIENE algo. Para un quitado que detiene se nombran la entrada quitada Y
    lo que el bloqueo pide: quitar `S_cuneta` hace faltar `L_hidraulico_m`,
    y es esa la que el mensaje nombra. La clase de una entrada quitada es la
    del bloqueo que provoca: quitar `drenaje_trasdos` no deja un dato
    faltante sino un metodo sin evaluar (ficha T7B-05), y la lista lo dice
    asi. Es la lista ADEMAS de las columnas obligatorias del CSV (sin ellas
    M0 no carga) y SIN las condicionales que ninguna de las dos bases
    dispara (`CONDICIONALES_NO_MEDIDAS`).
    """
    filas: Dict[str, Tuple[set, set]] = {}

    def _anota(nombre: str, clase: str, donde: str) -> None:
        clases, dondes = filas.setdefault(nombre, (set(), set()))
        clases.add(clase)
        dondes.add(donde)

    for b in todos_los_bloqueos(por_defecto):
        if b.clase in (CLASE_ENTRADA, CLASE_CRITERIO):
            _anota(b.que, b.clase, f"{b.punto}: {b.etapa} (sin juego)")
    for pares, rotulo in ((una, ""), (una_titular, ROTULO_BASE_TITULAR)):
        for el, ef in pares:
            if ef.clase != "DETIENE":
                continue
            for b in ef.bloqueos_nuevos:
                if b.clase == CLASE_NO_FACTIBLE:
                    continue
                donde = f"{b.punto}: {b.etapa}{rotulo}"
                _anota(_raiz_de(el.etiqueta), b.clase, donde)
                if b.clase in (CLASE_ENTRADA, CLASE_CRITERIO):
                    _anota(b.que, b.clase, donde)
    return tuple((nombre, " / ".join(sorted(clases)),
                  "; ".join(sorted(dondes)))
                 for nombre, (clases, dondes) in sorted(filas.items()))


# LAS CONDICIONALES QUE NINGUNA DE LAS DOS BASES DISPARA: detienen una etapa
# si falta su dato, pero solo en una rama que el juego no recorre, y por eso
# no salen de la medida (correcciones de T-11, H1). Se nombran aqui --y el
# test exige que la §7 del contrato las nombre-- en vez de callarlas: la
# lista exacta es la medida, y lo que la medida no alcanza se dice.
CONDICIONALES_NO_MEDIDAS: Dict[str, str] = {
    "homogeneidad_serie_fen": (
        "solo con el caudal CALCULADO (celda `Q_m3s` vacia y `--cuencas` / "
        "`--estacion`): la mide la variante `caudal_calculado_sin_fen`"),
    "perfil_hdpe_fabricante": (
        "solo si un punto no tiene otra solucion que el HDPE (T-5)"),
    "clases_producto_por_relleno": (
        "la D-load de las Clases I, III, IV y V de AASHTO M 170M: solo si un "
        "tubo de concreto pide mas que la Clase II (T-5)"),
    "resistencia_costura_empernada_tmc": (
        "solo si se adopta un TMC con `fabricacion_tmc` = 'anular_empernada' "
        "(T-5): ninguna fuente del repositorio tabula esa costura"),
    "ancho_tributario_m": (
        "solo cuando el tramo del alivio no se conoce o el caudal se calcula "
        "(T-9)"),
    "ancho_derecho_via_m": (
        "solo con `remanso_derecho_via` = 'embalse_a_nivel' (T-7b)"),
    "TW_receptor": (
        "solo si ninguna via de la Sec. 1.3 es recorrible: sin TW declarado, "
        "sin `cota_TW`, sin `Q_receptor_m3s`, sin seccion medida y con "
        "`seccion_receptor` vacio (`servicio.tw_sin_via_de_sec_1_3`); con la "
        "seccion de archivo de `seccion_receptor` nunca se lee"),
    "h_eq_banda_intermedia_borde": (
        "solo con el trasdos a menos de 1.0 ft (0.3048 m) del borde de la "
        "calzada, la banda intermedia de AASHTO 3.11.6.4 "
        "(`M9.CRITERIO_H_EQ_BANDA_BORDE`)"),
    "h_eq_bajo_altura_tabulada": (
        "solo con un muro de menos de 5.0 ft (1.524 m), bajo la primera fila "
        "de la tabla de h_eq de AASHTO 3.11.6.4 (`M9._interpolar_h_eq`)"),
    "N_cq_N_gammaq_meyerhof": (
        "solo con `terreno_delante_del_cabezal` = 'talud_descendente': la "
        "zapata en talud del Manual de Puentes 2.8.1.3.1.2c"),
    "q_n_kpa": (
        "la resistencia portante nominal del EMS (`suelo_fundacion`): solo "
        "con la cimentacion en ROCA (filas A o B declaradas en 'F_pga'), "
        "donde la ecuacion de 10.6.3.1.2a no aplica y sin el dato la "
        "capacidad portante es «metodo no evaluable»"),
}


def _raiz_de(etiqueta: str) -> str:
    """`clave (A-01)` -> `clave`; `--cuencas y --estacion` tal cual."""
    return etiqueta.split(" (")[0]


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    texto = generar()
    if "--escribir" in args:
        DOCUMENTO.write_text(texto, encoding="utf-8")
        print(f"escrito {DOCUMENTO}")
        print(f"escrita {escribir_corrida_de_referencia()}")
    else:
        sys.stdout.write(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
