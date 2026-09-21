# -*- coding: utf-8 -*-
"""
barrido.py
==========
El BARRIDO DE SENSIBILIDAD de un criterio [A] sobre su ventana (PF-3): el
pipeline corre una vez por valor, cada volcado se contrasta con el del
primer valor por el comparador de E-B, y sale una tabla por punto. Es lo que
una tesis tiene que mostrar de cada [A] de perfil: que pasa con el
diametro, la carga a la entrada y las verificaciones cuando el criterio
recorre la ventana que la constitucion le exige declarar.

Que es, y que no
----------------
* NUNCA RECALCULA. La aritmetica es la del pipeline (`servicio.correr`) y
  la comparacion la del comparador (`comparador.comparar`); este modulo no
  importa `src.modulos` ni `cli`, y `tests/test_pf3_barrido.py` lo fija por
  AST. La tabla se LEE de los volcados y de la comparacion: no hace una
  resta ni un cociente sobre una magnitud.
* LA MISMA PUERTA QUE UNA DECLARACION. Cada valor entra por
  `editores.declarar`, que es lo que la pestana 2 y la ventana emergente
  usan: la guardia de forma y de ventana de `criterios_adoptados`, la
  exigencia de fila o nota para un criterio de tabla, la trazabilidad de un
  dato de ensayo. Y entra ANTES de la primera corrida, para todos los
  valores: un barrido con un valor fuera de la ventana no es sensibilidad,
  es otra adopcion, y no corre nada (`ValueError`).
* NINGUNA CORRIDA HEREDA DE LA ANTERIOR, Y EL PROCESO QUEDA COMO ESTABA.
  El estado de entrada (lo declarado y su procedencia,
  `declaracion.estado_de_sesion`) se fotografia al entrar; cada corrida
  parte de el (`restaurar_sesion(sustituir=True)`), declara SU valor y
  corre; al salir --- tambien si una corrida falla --- se repone el mismo
  estado. Cada `Informe.contexto` es de su corrida (EXT-4), y el volcado
  que viaja en `CorridaDelBarrido` lo dice: el valor barrido figura entre
  los usados como declarado en caliente, con su procedencia.
* UNA CLAVE A LA VEZ. Barrer dos claves es llamar dos veces; el producto
  cartesiano no existe aqui ni en la CLI, porque una tabla de sensibilidad
  de una tesis se lee por un eje.
* NO ES PARTE DEL EXPEDIENTE. La memoria HTML no cambia: el barrido es un
  anexo de la tesis, y por eso la CLI lo escribe en su propio JSON y no
  arma ninguna memoria cuando barre.

El volcado lo hace quien llama (`volcar`, que en produccion es
`cli.informe_json`): `src/` no importa `cli` (EXT-9), y el barrido necesita
el MISMO volcado que la sesion embebe y que el comparador entiende.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from src import comparador as _comparador
from src import criterios_adoptados as _ca
from src import declaracion as _dec
from src import editores as _sed
from src import servicio
from src.modelos import CorridaDelBarrido, FilaDelBarrido, ResultadoDeBarrido

# El prefijo con que el comparador rotula la diferencia de una verificacion
# (`comparador._comparar_punto`): «verificacion V2.cumple». Se lee de ahi;
# aqui solo se reconoce.
_ROTULO_VERIFICACION = "verificacion "
_CAMPO_VEREDICTO = ".cumple"


def barrer(ruta_csv: Path, externos: Any, alcance: str, clave: str,
           valores: Sequence[Any], *, fila: str = "", nota: str = "",
           declaraciones_base: Optional[Mapping[str, Any]] = None,
           volcar: Callable[[servicio.Informe], Dict[str, Any]]) -> ResultadoDeBarrido:
    """
    Corre el pipeline una vez por cada valor de `valores` con `clave`
    declarada a ese valor, y devuelve las corridas con su volcado y la
    tabla por punto.

    `fila` y `nota` son los de una declaracion desde la pestana 2: la fila
    de la tabla de la que proviene el valor, o la nota que explica por que
    se adopta otro numero; un criterio de tabla exige uno de los dos
    (`editores.declarar`), y un dato de ensayo exige la nota.
    `declaraciones_base` son declaraciones que acompañan a TODAS las
    corridas ademas de las que el proceso ya tenia al entrar (por el mismo
    camino que `--declarar`: `establecer_valor_dinamico`, con su guardia y
    sin procedencia). `volcar` convierte cada `Informe` en el dict que el
    comparador lee (`cli.informe_json`).

    Lanza `ValueError` (o `KeyError` si la clave no existe) ANTES de la
    primera corrida si algun valor no pasa la puerta; los errores del
    expediente (`ErrorProyecto`) de una corrida salen tal cual, con el
    estado del proceso ya repuesto.
    """
    valores = tuple(valores)
    if not valores:
        raise ValueError(f"el barrido de '{clave}' no trae ningun valor")
    _ca.criterio(clave)  # KeyError si la clave no existe, antes de nada
    base = dict(declaraciones_base or {})
    entrada = _dec.estado_de_sesion()
    try:
        # 1. LA PUERTA, PARA TODOS LOS VALORES, ANTES DE LA PRIMERA CORRIDA:
        # cada valor se declara de verdad por la puerta de la pestana 2 y
        # se deshace; lo que la puerta rechaza sale de aqui sin haber
        # corrido nada.
        for k, v in base.items():
            _ca.verificar_declaracion(k, v)
        for valor in valores:
            _dec.restaurar_sesion(entrada, sustituir=True)
            _sed.declarar(clave, valor, fila=fila, nota=nota)

        # 2. UNA CORRIDA POR VALOR, cada una desde el estado de entrada.
        corridas: List[Tuple[Any, str, Dict[str, Any]]] = []
        for valor in valores:
            _dec.restaurar_sesion(entrada, sustituir=True)
            for k, v in base.items():
                _ca.establecer_valor_dinamico(k, v)
            procedencia = _sed.declarar(clave, valor, fila=fila, nota=nota)
            informe = servicio.correr(ruta_csv, externos, alcance=alcance)
            corridas.append((valor, procedencia.como_texto(), volcar(informe)))
    finally:
        _dec.restaurar_sesion(entrada, sustituir=True)

    # 3. CADA VOLCADO CONTRA EL DEL PRIMER VALOR, por el comparador.
    primero = corridas[0][2]
    salida_corridas: List[CorridaDelBarrido] = []
    filas: List[FilaDelBarrido] = []
    for valor, procedencia, volcado in corridas:
        comparacion = _comparador.comparar(primero, volcado)
        salida_corridas.append(CorridaDelBarrido(
            valor=valor, procedencia=procedencia, informe_json=volcado,
            comparacion_con_la_primera=comparacion.lineas(),
            comparable=not comparacion.no_comparables))
        filas.extend(_filas_de(valor, volcado, comparacion))
    return ResultadoDeBarrido(clave=clave, corridas=tuple(salida_corridas),
                              filas=tuple(filas))


def _filas_de(valor: Any, volcado: Dict[str, Any],
              comparacion: _comparador.ComparacionDeInformes) -> List[FilaDelBarrido]:
    """La tabla de una corrida: una fila por punto, leida del volcado y de la comparacion."""
    salida = []
    for punto in volcado.get("puntos") or []:
        id_punto = str(punto.get("id"))
        diseno = punto.get("diseno") or {}
        motivos = tuple(n.por_que for n in comparacion.no_comparables if n.donde == id_punto)
        cambian = tuple(sorted({
            d.campo[len(_ROTULO_VERIFICACION):-len(_CAMPO_VEREDICTO)]
            for d in comparacion.diferencias
            if d.donde == id_punto and d.campo.startswith(_ROTULO_VERIFICACION)
            and d.campo.endswith(_CAMPO_VEREDICTO)}))
        salida.append(FilaDelBarrido(
            valor=valor, id_punto=id_punto,
            dimensionado=bool(punto.get("dimensionado")),
            material=diseno.get("material"), seccion=diseno.get("seccion"),
            HW_gobernante_m=diseno.get("HW_gobernante_m"),
            control_gobernante=diseno.get("control_gobernante"),
            verificaciones_que_cambian=cambian,
            comparable=not motivos, motivo="; ".join(motivos)))
    return salida


# ===========================================================================
# Presentacion: el JSON y la tabla de texto, elegidos aqui para que la CLI
# y una ventana impriman lo mismo
# ===========================================================================

def volcado_del_barrido(resultado: ResultadoDeBarrido) -> Dict[str, Any]:
    """El barrido como dict listo para `json.dump`, con los volcados enteros dentro."""
    # Sin `dataclasses.asdict`: copia en profundidad cada volcado, y un
    # volcado lleva objetos del registro normativo que no se copian (los
    # serializa `escribir_json_atomico`, como al expediente). El volcado
    # entra tal cual: es el mismo dict que la sesion embebe.
    return {
        "clave": resultado.clave,
        "corridas": [{"valor": c.valor, "procedencia": c.procedencia,
                      "informe_json": c.informe_json,
                      "comparacion_con_la_primera": list(c.comparacion_con_la_primera),
                      "comparable": c.comparable} for c in resultado.corridas],
        "filas": [asdict(f) for f in resultado.filas],
    }


ENCABEZADO_DE_LA_TABLA = ("valor", "punto", "material", "seccion", "HW (m)",
                          "control", "verificaciones que cambian", "comparable")


def lineas_de_la_tabla(resultado: ResultadoDeBarrido) -> Tuple[str, ...]:
    """
    La tabla del barrido en texto, una linea por (valor, punto), con la
    comparacion de cada corrida con la primera debajo. Solo elige textos y
    orden: los numeros se imprimen como estan en el volcado.
    """
    celdas = [ENCABEZADO_DE_LA_TABLA]
    for f in resultado.filas:
        celdas.append((
            repr(f.valor), f.id_punto,
            (f.material or "—") if f.dimensionado else "no dimensionado",
            f.seccion or "—", "—" if f.HW_gobernante_m is None else repr(f.HW_gobernante_m),
            f.control_gobernante or "—",
            ", ".join(f.verificaciones_que_cambian) or "ninguna",
            "si" if f.comparable else f"NO: {f.motivo}"))
    anchos = [max(len(fila[i]) for fila in celdas) for i in range(len(ENCABEZADO_DE_LA_TABLA))]
    salida = [f"Barrido de '{resultado.clave}' sobre {len(resultado.corridas)} valor(es): "
              + ", ".join(repr(c.valor) for c in resultado.corridas)]
    for fila in celdas:
        salida.append("  ".join(celda.ljust(ancho) for celda, ancho in zip(fila, anchos)).rstrip())
    for c in resultado.corridas:
        salida.append(f"{resultado.clave} = {c.valor!r} ({c.procedencia}): "
                      + c.comparacion_con_la_primera[0])
        salida.extend("    " + linea for linea in c.comparacion_con_la_primera[1:])
    return tuple(salida)
