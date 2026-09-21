# -*- coding: utf-8 -*-
"""
comparador.py
=============
Compara DOS volcados `informe_json` de dos corridas, por IDENTIDAD DE PUNTO
(E-B, E14). Es lo que un revisor necesita para saber si una memoria sigue
vigente despues de un cambio --- del CSV, de un criterio, del codigo --- sin
leer dos memorias en paralelo.

Lo que es, y lo que no
----------------------
* Lee dos `dict` (los que `cli.informe_json` escribe) y devuelve un objeto
  con las diferencias NOMBRADAS por punto y campo, lo que no se pudo
  comparar y por que, y los puntos que estan en uno solo de los dos.
* NUNCA RECALCULA. No importa el motor (`servicio`, `src/modulos`), ni los
  tres archivos de valores, ni `declaracion`: un comparador que corriera el
  pipeline «con el proyecto activo» compararia el volcado B con una tercera
  corrida hecha con el estado vivo del proceso, que es exactamente lo que
  EXT-4 saco de los exportadores. `tests/test_eb_editores_comparador.py` lo
  fija por AST.
* La NORMALIZACION es la misma que la CLI aplica a la corrida embebida en
  la sesion (EXT-10) y que `regenerar.sh` aplica a la linea base: fuera la
  marca de tiempo y fuera las RUTAS de origen de los datos de sitio, porque
  ninguna de las dos dice nada del calculo. `sesion.sin_marca_de_tiempo` y
  `sesion.sin_origen_de_los_datos_de_sitio` son las dos funciones, y por eso
  `cli._comparar_con_la_corrida_embebida` llama a `comparar` en vez de
  comparar dos dicts con `==`: UNA definicion de «la misma corrida».
* Las TOLERANCIAS tienen nombre (`tolerancias.TOL_COMPARADOR_ABS`,
  `TOL_COMPARADOR_REL`) y absorben solo el ruido de la aritmetica; ningun
  float se compara con `==` (CLAUDE.md).
* «NO COMPARABLE» para metodos distintos. Si en un punto el control
  gobernante, el regimen del barril o el tipo de perfil de la lamina
  difieren entre A y B, los numeros de su diseno salieron de FORMULAS
  distintas y compararlos uno a uno no significa nada: el comparador lo
  dice como `NoComparable` con la causa, en vez de listar veinte
  diferencias que son una sola. Lo mismo cuando un punto dimensiona en una
  corrida y en la otra no, y cuando los dos volcados son de ALCANCES
  distintos (una corrida de perfil difiere etapas que la de expediente
  ejecuta).

La comparacion de los bloques que no son un punto --- criterios usados,
datos de sitio usados, cabezal, expediente --- es por CLAVE, con la misma
regla: se emparejan por su identificador y no por su posicion.

Uso
---
    python -m src.comparador A.informe.json B.informe.json
    python cli.py --comparar A.informe.json B.informe.json

Codigo de salida 0 si son iguales, 1 si hay diferencias o no comparables,
2 si alguno de los dos no se pudo leer. Nada de esto corre el pipeline.
"""

from __future__ import annotations

import json
import math
import numbers
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src import sesion as _sesion
from src.tolerancias import TOL_COMPARADOR_ABS, TOL_COMPARADOR_REL

# Los campos del diseño de un punto que definen el METODO con que salieron
# sus numeros. Si difieren, el resto del bloque `diseno` no se compara
# numero a numero: se declara «no comparable» con la causa.
CAMPOS_DE_METODO: Tuple[str, ...] = ("control_gobernante", "regimen_barril",
                                     "perfil_tipo")

# Donde vive cada bloque del volcado que se compara por clave.
EXPEDIENTE = "expediente"
ALCANCE = "alcance"
PUNTOS = "puntos"
CABEZAL = "cabezal"
CRITERIOS = "criterios"
DATOS_SITIO = "datos_sitio"

ROTULO_IGUALES = "IGUALES"
ROTULO_DIFIEREN = "DIFIEREN"
# Como se rotula la diferencia de una verificacion de un punto («verificacion
# V3», y debajo «.cumple», «.valor_obtenido»...). Es una constante y no un
# literal en `_comparar_punto` porque `barrido._filas_de` la LEE para
# reconocer sus filas: una segunda transcripcion divergiria sin aviso
# (auditor adversarial de PF-3).
ROTULO_VERIFICACION = "verificacion "
VALOR_EVALUADA = "evaluada"
VALOR_AUSENTE = "<ausente>"


@dataclass(frozen=True)
class Diferencia:
    """Un campo con dos valores distintos. `donde` es el punto o el bloque."""
    donde: str
    campo: str
    a: Any
    b: Any


@dataclass(frozen=True)
class NoComparable:
    """Algo que no se pudo comparar, y POR QUE."""
    donde: str
    por_que: str


@dataclass(frozen=True)
class ComparacionDeInformes:
    puntos_comunes: Tuple[str, ...]
    solo_en_a: Tuple[str, ...]
    solo_en_b: Tuple[str, ...]
    diferencias: Tuple[Diferencia, ...]
    no_comparables: Tuple[NoComparable, ...]

    @property
    def iguales(self) -> bool:
        """
        Iguales = mismos puntos, ningun campo distinto y nada que no se
        pudiera comparar. Un «no comparable» NO es igualdad: es una
        pregunta sin contestar, y se reporta.
        """
        return not (self.diferencias or self.no_comparables
                    or self.solo_en_a or self.solo_en_b)

    def lineas(self) -> Tuple[str, ...]:
        """El informe en texto, elegido aqui para que la CLI y la GUI impriman lo mismo."""
        if self.iguales:
            return ((f"{ROTULO_IGUALES}: los dos volcados describen la misma corrida "
                     f"({len(self.puntos_comunes)} puntos, salvo la marca de tiempo y "
                     "las rutas de origen de los datos de sitio)."),)
        salida: List[str] = [
            f"{ROTULO_DIFIEREN}: {len(self.diferencias)} diferencia(s), "
            f"{len(self.no_comparables)} no comparable(s), "
            f"{len(self.solo_en_a)} punto(s) solo en A, {len(self.solo_en_b)} solo en B."]
        if self.solo_en_a:
            salida.append("Solo en A: " + ", ".join(self.solo_en_a))
        if self.solo_en_b:
            salida.append("Solo en B: " + ", ".join(self.solo_en_b))
        for n in self.no_comparables:
            salida.append(f"NO COMPARABLE [{n.donde}]: {n.por_que}")
        for d in self.diferencias:
            salida.append(f"[{d.donde}] {d.campo}: A = {d.a!r} | B = {d.b!r}")
        return tuple(salida)


# ===========================================================================
# Comparacion generica de valores
# ===========================================================================

def _es_numero(x: Any) -> bool:
    return isinstance(x, numbers.Real) and not isinstance(x, bool)


def mismo_numero(a: float, b: float) -> bool:
    """
    Dos reales son el mismo numero si su diferencia no pasa del mayor de los
    dos umbrales nombrados: el absoluto para magnitudes pequenas, el relativo
    para las grandes. Un NaN no es el mismo numero que nada --- ni que otro
    NaN ---, y dos infinitos lo son solo con el mismo signo: `json.loads`
    acepta `NaN` e `Infinity`, y sin esta rama la forma negada de la
    tolerancia los dejaba caer del lado de «igual» (auditoria adversarial de
    E-B); con un infinito el umbral relativo se volvia infinito.
    """
    if not (math.isfinite(a) and math.isfinite(b)):
        return (math.isinf(a) and math.isinf(b) and (a > 0) == (b > 0))
    return not (abs(a - b) > max(TOL_COMPARADOR_ABS,
                                 TOL_COMPARADOR_REL * max(abs(a), abs(b))))


def _comparar_valor(donde: str, campo: str, a: Any, b: Any,
                    diferencias: List[Diferencia]) -> None:
    """Recorre dicts y listas; compara hojas con la regla de su tipo."""
    if _es_numero(a) and _es_numero(b):
        if not mismo_numero(a, b):
            diferencias.append(Diferencia(donde, campo, a, b))
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                diferencias.append(Diferencia(donde, f"{campo}.{k}",
                                              a.get(k, "<ausente>"), b.get(k, "<ausente>")))
                continue
            _comparar_valor(donde, f"{campo}.{k}", a[k], b[k], diferencias)
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diferencias.append(Diferencia(donde, f"{campo}[len]", len(a), len(b)))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _comparar_valor(donde, f"{campo}[{i}]", x, y, diferencias)
        return
    # Hojas no numericas (texto, bool, None) y tipos distintos: exactas.
    if a != b:
        diferencias.append(Diferencia(donde, campo, a, b))


def _por_clave(filas: Any, clave: str) -> Dict[str, Any]:
    return {str(f[clave]): f for f in (filas or []) if isinstance(f, dict) and clave in f}


def _comparar_por_clave(donde: str, a: Any, b: Any, clave: str,
                        diferencias: List[Diferencia]) -> None:
    """Listas de dicts emparejadas por `clave`, nunca por posicion."""
    ia, ib = _por_clave(a, clave), _por_clave(b, clave)
    for k in sorted(set(ia) | set(ib)):
        if k not in ia or k not in ib:
            diferencias.append(Diferencia(donde, k, "presente" if k in ia else "<ausente>",
                                          "presente" if k in ib else "<ausente>"))
            continue
        _comparar_valor(donde, k, ia[k], ib[k], diferencias)


# ===========================================================================
# Los puntos
# ===========================================================================

def _metodo(diseno: Optional[Dict[str, Any]]) -> Tuple[Any, ...]:
    return tuple((diseno or {}).get(c) for c in CAMPOS_DE_METODO)


def _comparar_punto(id_punto: str, pa: Dict[str, Any], pb: Dict[str, Any],
                    diferencias: List[Diferencia],
                    no_comparables: List[NoComparable]) -> None:
    for campo in ("familia", "progresiva", "dimensionado", "pendientes_externos",
                  "datos_declarados", "clasificacion", "proteccion_salida",
                  "geometria", "estructural", "espaciamiento_alivio",
                  "verificaciones_no_evaluadas"):
        _comparar_valor(id_punto, campo, pa.get(campo), pb.get(campo), diferencias)

    da, db = pa.get("diseno"), pb.get("diseno")
    if (da is None) != (db is None):
        no_comparables.append(NoComparable(
            id_punto, "el punto tiene diseño en " + ("A" if da else "B")
            + " y no en " + ("B" if da else "A")
            + ": no hay numeros que comparar (ver `dimensionado` y `bloqueos`)"))
    elif da is not None:
        ma, mb = _metodo(da), _metodo(db)
        if ma != mb:
            causas = ", ".join(f"{c}: {x!r} frente a {y!r}"
                               for c, x, y in zip(CAMPOS_DE_METODO, ma, mb) if x != y)
            no_comparables.append(NoComparable(
                id_punto, f"métodos distintos ({causas}): los numeros del diseño "
                          "salieron de formulas distintas y no se comparan uno a uno"))
        else:
            _comparar_valor(id_punto, "diseno", da, db, diferencias)

    # Verificaciones por (fase, codigo), con TODOS sus campos; bloqueos por
    # (etapa, tipo, criterio, diferido), con todos sus campos y contando
    # repetidos (un set escondia dos bloqueos iguales frente a uno, y el
    # `delta_rasante_m` y el `mensaje` de un DisenoNoFactibleError, que son
    # lo que CLAUDE.md exige que lleve: auditoria adversarial de E-B);
    # iteraciones enteras, en su orden, que es el de la progresion del
    # catalogo.
    va = {(v.get("fase"), v.get("codigo")): v for v in pa.get("verificaciones") or []}
    vb = {(v.get("fase"), v.get("codigo")): v for v in pb.get("verificaciones") or []}
    for k in sorted(set(va) | set(vb), key=str):
        rotulo = f"{ROTULO_VERIFICACION}{k[1] or k[0]}"
        if k not in va or k not in vb:
            diferencias.append(Diferencia(id_punto, rotulo,
                                          VALOR_EVALUADA if k in va else VALOR_AUSENTE,
                                          VALOR_EVALUADA if k in vb else VALOR_AUSENTE))
            continue
        _comparar_valor(id_punto, rotulo, va[k], vb[k], diferencias)
    ba: Dict[Tuple[Any, ...], List[Any]] = {}
    for x in pa.get("bloqueos") or []:
        ba.setdefault(_clave_de_bloqueo(x), []).append(x)
    bb: Dict[Tuple[Any, ...], List[Any]] = {}
    for x in pb.get("bloqueos") or []:
        bb.setdefault(_clave_de_bloqueo(x), []).append(x)
    for k in sorted(set(ba) | set(bb), key=str):
        etapa, tipo, criterio, diferido = k
        que = f"bloqueo {tipo} en «{etapa}»" + (f" por {criterio}" if criterio else "") \
              + (" (diferido por alcance)" if diferido else "")
        if k not in ba or k not in bb:
            diferencias.append(Diferencia(id_punto, que, "presente" if k in ba else "<ausente>",
                                          "presente" if k in bb else "<ausente>"))
            continue
        _comparar_valor(id_punto, que, ba[k], bb[k], diferencias)

    _comparar_valor(id_punto, "iteraciones", pa.get("iteraciones"), pb.get("iteraciones"),
                    diferencias)


def _clave_de_bloqueo(x: Dict[str, Any]) -> Tuple[Any, ...]:
    return (x.get("etapa"), x.get("tipo"), x.get("criterio"), x.get("diferido_por_alcance"))


# ===========================================================================
# La comparacion entera
# ===========================================================================

def normalizar(volcado: Dict[str, Any]) -> Dict[str, Any]:
    """La MISMA normalizacion que la corrida embebida (EXT-10) y la linea base."""
    return _sesion.sin_origen_de_los_datos_de_sitio(_sesion.sin_marca_de_tiempo(volcado))


def comparar(a: Dict[str, Any], b: Dict[str, Any]) -> ComparacionDeInformes:
    """
    Compara dos volcados `informe_json`. No toca disco, no corre nada, no
    lee estado del proceso: dos dicts entran, un objeto sale.
    """
    a, b = normalizar(a), normalizar(b)
    diferencias: List[Diferencia] = []
    no_comparables: List[NoComparable] = []

    ea, eb = a.get(EXPEDIENTE) or {}, b.get(EXPEDIENTE) or {}
    for campo in ("csv_sha1", "criterios_sha1", "puntos", "dimensionados", "cerrado",
                  "corredor_del_proyecto"):
        _comparar_valor(EXPEDIENTE, campo, ea.get(campo), eb.get(campo), diferencias)

    aa, ab = a.get(ALCANCE) or {}, b.get(ALCANCE) or {}
    if aa.get("nivel") != ab.get("nivel"):
        no_comparables.append(NoComparable(
            EXPEDIENTE, f"alcances distintos ({aa.get('nivel')!r} frente a "
                        f"{ab.get('nivel')!r}): una corrida difiere etapas que la otra "
                        "ejecuta; los puntos se comparan igual, el cierre no"))
    else:
        _comparar_valor(ALCANCE, "diferidos[len]", len(aa.get("diferidos") or []),
                        len(ab.get("diferidos") or []), diferencias)

    pa, pb = _por_clave(a.get(PUNTOS), "id"), _por_clave(b.get(PUNTOS), "id")
    comunes = tuple(p["id"] for p in (a.get(PUNTOS) or []) if p.get("id") in pb)
    solo_a = tuple(k for k in (p["id"] for p in a.get(PUNTOS) or []) if k not in pb)
    solo_b = tuple(k for k in (p["id"] for p in b.get(PUNTOS) or []) if k not in pa)
    for id_punto in comunes:
        _comparar_punto(id_punto, pa[id_punto], pb[id_punto], diferencias, no_comparables)

    _comparar_valor(CABEZAL, "cabezal", a.get(CABEZAL), b.get(CABEZAL), diferencias)

    # Los DOS bloques de estado enteros: las listas de claves ordenadas y los
    # usados/bloqueantes por clave. Ningun subbloque se deja fuera: el
    # primer comparador ignoraba `verificacion_pendiente`, `sin_consumidor`
    # y las tres listas de los datos de sitio (auditoria adversarial de E-B).
    ca_, cb_ = a.get(CRITERIOS) or {}, b.get(CRITERIOS) or {}
    _comparar_por_clave(CRITERIOS, ca_.get("usados"), cb_.get("usados"), "clave", diferencias)
    for campo in ("sin_valor_declarados", "declarados_en_caliente",
                  "verificacion_pendiente", "sin_consumidor"):
        _comparar_valor(CRITERIOS, campo, sorted(ca_.get(campo) or [], key=str),
                        sorted(cb_.get(campo) or [], key=str), diferencias)
    _comparar_por_clave(CRITERIOS + ".bloquearon", ca_.get("bloquearon"),
                        cb_.get("bloquearon"), "clave", diferencias)
    for k in sorted(set(ca_) | set(cb_)):
        if k not in ("usados", "sin_valor_declarados", "declarados_en_caliente",
                     "verificacion_pendiente", "sin_consumidor", "bloquearon"):
            _comparar_valor(CRITERIOS, k, ca_.get(k), cb_.get(k), diferencias)

    sa, sb = a.get(DATOS_SITIO) or {}, b.get(DATOS_SITIO) or {}
    _comparar_por_clave(DATOS_SITIO, sa.get("usados"), sb.get("usados"), "clave", diferencias)
    for k in sorted(set(sa) | set(sb)):
        if k != "usados":
            _comparar_valor(DATOS_SITIO, k, sorted(sa.get(k) or [], key=str)
                            if isinstance(sa.get(k), list) else sa.get(k),
                            sorted(sb.get(k) or [], key=str)
                            if isinstance(sb.get(k), list) else sb.get(k), diferencias)

    return ComparacionDeInformes(
        puntos_comunes=comunes, solo_en_a=solo_a, solo_en_b=solo_b,
        diferencias=tuple(diferencias), no_comparables=tuple(no_comparables))


def cargar(ruta: Path) -> Dict[str, Any]:
    """Un volcado desde disco. Los fallos de lectura salen tal cual: son de E/S."""
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if not isinstance(datos, dict) or PUNTOS not in datos:
        raise ValueError(f"{ruta}: no es un volcado informe_json (sin bloque «{PUNTOS}»)")
    return datos


def comparar_archivos(ruta_a: Path, ruta_b: Path) -> ComparacionDeInformes:
    return comparar(cargar(ruta_a), cargar(ruta_b))


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("uso: python -m src.comparador A.informe.json B.informe.json", file=sys.stderr)
        return 2
    try:
        resultado = comparar_archivos(Path(args[0]), Path(args[1]))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"No se pudo comparar: {exc}", file=sys.stderr)
        return 2
    try:
        for linea in resultado.lineas():
            print(linea)
        sys.stdout.flush()
    except BrokenPipeError:
        # `| head` cerro la tuberia: el veredicto ya esta en el codigo de salida.
        pass
    return 0 if resultado.iguales else 1


if __name__ == "__main__":
    sys.exit(main())
