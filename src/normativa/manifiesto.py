"""
El manifiesto, GENERADO. La cura de `NOR-MAN-04`, no su parche.

EL DEFECTO, dicho como lo que es. La auditoria encontro que al menos 66 de
296 referencias `archivo:linea` del manifiesto no llevaban a lo que decian
llevar. No fue descuido de nadie: **el numero de linea es un ancla que se rompe
sola**. Cualquier insercion en un archivo citado desplaza todos los enlaces de
abajo, en silencio, y el documento se degrada con el commit siguiente. La
regla 4 de `CLAUDE.md` ya lo dice -- «ancla todo por NOMBRE DE SIMBOLO […]
nunca por numero de linea» -- y el manifiesto es el documento del repositorio
que mas la incumplia.

LA DIFERENCIA ENTRE PARCHE Y CURA, que es el fondo de este modulo. Renumerar
las 66 referencias a mano las arregla hoy y las rompe otra vez mañana: es lo
que ya se hizo una vez y por lo que el hallazgo existe. Lo que no se rompe
solo es **derivar el numero de linea del NOMBRE**, cada vez, desde el codigo:

    el manifiesto DECLARA un simbolo -> el generador CALCULA su linea

Con eso el ancla vuelve a ser el nombre -- que solo cambia si alguien lo
renombra, y entonces el generador falla ruidosamente -- y el numero de linea
pasa a ser una comodidad de navegacion regenerable, no un dato que mantener.

DOS PIEZAS, y hacen cosas distintas:

  `resincronizar`  reescribe los numeros de linea de las referencias que YA
                   citan un simbolo. Es la cura del ancla rota, y su test
                   (T8) regenera a un temporal y compara: si difieren, el
                   manifiesto esta desincronizado y el mensaje dice cuanto.

  `indice_del_registro`  genera, ENTERO y desde los objetos, el indice de lo
                   que el registro normativo ya contiene: fuentes con su
                   sha1 y su paginacion, citas con su numeral y su pagina PDF
                   verificada, tablas con su alcance y su uso, discrepancias
                   abiertas. Ahi no hay numeros de linea que puedan romperse
                   porque no hay lineas: hay ids.

LO QUE ESTE MODULO NO CIERRA TODAVIA, y conviene decirlo en vez de que se
deduzca del cupo. `MAX_REFERENCIAS_DE_PROSA == 0` -- la meta T9 -- exige que
TODA fila del manifiesto se ancle a un id del registro, y para eso el registro
tiene que contener el corpus entero. Hoy contiene las citas de los clusters
C11, C12 y C02 y las tablas que esos tres tocan; el resto sigue en prosa. El
cupo baja hasta donde el registro llega y el test lo vigila como TRINQUETE:
solo puede decrecer.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .esquema import (
    Acotada,
    Cita,
    EstadoDiscrepancia,
    NoUsada,
    PendienteDeCondicion,
    SinDeterminar,
    Usada,
    esta_por_transcribir,
)

RAIZ = Path(__file__).resolve().parents[2]
MANIFIESTO = RAIZ / "docs" / "manifiesto_citas.md"
INDICE_REGISTRO = RAIZ / "docs" / "manifiesto_registro_normativo.md"

# El formato de referencia del manifiesto: [ETIQUETA:linea](ruta:linea).
REFERENCIA = re.compile(
    r"\[([A-Za-z0-9_.]+):(\d+)(?:,\s*\d+)?(-\d+)?\]\((src/[^)]+?):(\d+)\)")

# Las mismas definiciones que reconoce `tests/test_manifiesto_citas.py`. Viven
# duplicadas A PROPOSITO y no importadas: el test es la guardia y este modulo
# el generador, y si el generador importara del test, un cambio en el
# generador cambiaria lo que el test comprueba -- que es exactamente la forma
# de que una guardia deje de guardar.
DEFINICION = re.compile(
    r"^(?:(\s*)(?:def|class)\s+([A-Za-z_]\w*)"
    r"|([A-Z_][A-Z0-9_]*)\s*[:=]"
    r"|    \"([A-Za-z_]\w*)\"\s*:"
    r"|([a-z_]\w*)\s*=(?!=))")


def _lineas(rel: str) -> List[str]:
    return (RAIZ / rel).read_text(encoding="utf-8").split("\n")


def _bloques(rel: str) -> Dict[str, List[Tuple[int, int]]]:
    """{simbolo: [(primera_linea, ultima_linea), ...]} de un archivo."""
    lineas, definiciones = _lineas(rel), []
    for numero, linea in enumerate(lineas, 1):
        m = DEFINICION.match(linea)
        if m:
            nombre = next((g for g in m.groups()[1:] if g), None)
            if nombre:
                definiciones.append((numero, nombre))
    bloques: Dict[str, List[Tuple[int, int]]] = {}
    for i, (inicio, nombre) in enumerate(definiciones):
        fin = (definiciones[i + 1][0] - 1 if i + 1 < len(definiciones)
               else len(lineas))
        bloques.setdefault(nombre, []).append((inicio, fin))
    return bloques


def _simbolos_citados(fila: str) -> List[str]:
    """Identificadores entre backticks en esa fila del manifiesto."""
    simbolos: List[str] = []
    for trozo in re.findall(r"`([^`]+)`", fila):
        m = re.match(r"^([A-Za-z_]\w*)", trozo.strip().lstrip("↳↻⚠~✚⟳ "))
        if m and m.group(1) not in simbolos:
            simbolos.append(m.group(1))
    return simbolos


def _linea_del_simbolo(rel: str, simbolos: List[str],
                       linea_actual: int) -> Optional[int]:
    """
    Donde vive HOY el simbolo que la fila cita.

    Si el simbolo tiene varios bloques -- el mismo nombre en dos sitios del
    archivo, que pasa con las claves de diccionario -- se elige el mas cercano
    a la linea que el manifiesto declara: es la unica desambiguacion que no
    exige criterio humano, y es correcta mientras el desfase sea menor que la
    distancia entre dos homonimos. Si no lo fuera, la referencia caeria fuera
    del bloque y el test T8 lo diria.
    """
    bloques = _bloques(rel)
    tramos = [t for s in simbolos for t in bloques.get(s, [])]
    if not tramos:
        return None
    for inicio, fin in tramos:
        if inicio <= linea_actual <= fin:
            # DENTRO DEL BLOQUE NO BASTA: puede ser un renglon en blanco entre
            # el comentario de cabecera y el `def`, y una referencia que
            # aterriza en el vacio no lleva a lo que dice llevar -- que es
            # NOR-MAN-04 en pequeño. Se baja al primer renglon con texto.
            return _primer_renglon_con_texto(rel, linea_actual, fin)
    return _primer_renglon_con_texto(
        rel, min((inicio for inicio, _ in tramos),
                 key=lambda x: abs(x - linea_actual)), None)


def _primer_renglon_con_texto(rel: str, desde: int,
                              hasta: Optional[int]) -> int:
    lineas = (RAIZ / rel).read_text(encoding="utf-8").split("\n")
    tope = len(lineas) if hasta is None else min(hasta, len(lineas))
    for n in range(desde, tope + 1):
        if lineas[n - 1].strip():
            return n
    return desde


def resincronizar(texto: str) -> Tuple[str, List[str], int]:
    """
    Reescribe los numeros de linea de las referencias ancladas a un simbolo.

    Devuelve (texto_nuevo, cambios, referencias_de_prosa). Las de prosa -- las
    filas que no citan ningun simbolo que exista en el archivo -- se dejan
    intactas y se CUENTAN: son el hueco declarado, y el cupo del test es lo
    que impide que crezca.
    """
    cambios: List[str] = []
    prosa = 0
    salida: List[str] = []
    for n_md, fila in enumerate(texto.split("\n"), 1):
        simbolos = _simbolos_citados(fila)

        def _reemplazo(m: re.Match) -> str:
            nonlocal prosa
            etiqueta, _, sufijo, rel, linea = m.groups()
            linea = int(linea)
            if not (RAIZ / rel).exists():
                return m.group(0)
            destino = _linea_del_simbolo(rel, simbolos, linea)
            if destino is None:
                prosa += 1
                return m.group(0)
            if destino == linea:
                return m.group(0)
            cambios.append(f"md:{n_md}  {rel}:{linea} -> :{destino} "
                           f"({destino - linea:+d}, simbolo "
                           f"`{simbolos[0] if simbolos else '?'}`)")
            nueva = f"{etiqueta}:{destino}{sufijo or ''}"
            return f"[{nueva}]({rel}:{destino})"

        salida.append(REFERENCIA.sub(_reemplazo, fila))
    return "\n".join(salida), cambios, prosa


# ===========================================================================
# El indice del registro, generado entero desde los objetos
# ===========================================================================

def _pagina(c: Cita) -> str:
    impresa = f"pág. impresa **{c.pagina_impresa}**"
    if esta_por_transcribir(c.pagina_pdf):
        return impresa + " · PDF *por transcribir*"
    return impresa + f" · PDF {c.pagina_pdf}"


def _titulo(c: Cita) -> str:
    if esta_por_transcribir(c.titulo_numeral):
        return "*por transcribir*"
    jer = " › ".join(c.jerarquia_numeral)
    return (f"{jer} › «{c.titulo_numeral}»" if jer
            else f"«{c.titulo_numeral}»")


def _verificacion(c: Cita) -> str:
    if c.verificado is None:
        return "**NO verificada**"
    return f"{c.verificado.fecha} · {c.verificado.metodo.value}"


def indice_del_registro(registro) -> str:
    """
    El manifiesto de lo que el registro contiene, generado desde los objetos.

    NO LLEVA UN SOLO NUMERO DE LINEA, y esa es toda la idea: cada fila se
    ancla al `id` de su objeto, que solo cambia si alguien lo renombra a
    proposito. Un ancla que no se rompe sola.
    """
    L: List[str] = []
    A = L.append

    A("# Manifiesto del registro normativo")
    A("")
    A("> **Este documento se GENERA.** No se edita a mano: lo produce")
    A("> `src/normativa/manifiesto.py` desde los objetos de `src/normativa/`,")
    A("> y el test `test_el_indice_del_registro_esta_sincronizado` lo")
    A("> regenera y compara. Si difieren, lo que hay que corregir es el")
    A("> registro, no este archivo.")
    A(">")
    A("> **Por qué existe, y en qué se diferencia de `manifiesto_citas.md`.**")
    A("> Aquél es un volcado de lo que el código afirma, anclado por")
    A("> `archivo:línea` — un ancla que se rompe con cualquier inserción, que")
    A("> es de lo que salió `NOR-MAN-04`. Éste se ancla por **id de objeto**,")
    A("> y por eso no puede desincronizarse en silencio: o lo regenera el")
    A("> generador, o el test falla.")
    A("")

    # -- Fuentes -----------------------------------------------------------
    A("## 1. Fuentes")
    A("")
    A("Las que están en `normas/`, con el SHA-1 exacto contra el que se")
    A("verificó cada cita y la regla de paginación MEDIDA, no supuesta.")
    A("")
    A("| id | Documento | Edición | Paginación (pdf ← impresa) | Páginas | SHA-1 | Texto extraíble |")
    A("|---|---|---|---|---|---|---|")
    for f in sorted(registro.fuentes, key=lambda x: x.id):
        p = f.paginacion
        if hasattr(p, "desfase"):
            regla = f"corrida, {p.desfase:+d}"
        elif hasattr(p, "base"):
            regla = ("por capítulo: " +
                     ", ".join(f"{k}={v}" for k, v in sorted(p.base.items())))
        elif isinstance(p, SinDeterminar):
            regla = "**sin determinar**"
        else:
            regla = "irregular"
        A(f"| `{f.id}` | {f.titulo} | {f.edicion} | {regla} | {f.paginas_pdf} "
          f"| `{f.sha1}` | {'sí' if f.texto_extraible else '**no**'} |")
    A("")

    # -- Fuentes ausentes --------------------------------------------------
    A("## 2. Fuentes que se citan y NO están en `normas/`")
    A("")
    A("Ordenadas por lo que cuesta traerlas, para que la deuda se vea sin")
    A("leer la §15 del plan. **Ninguna puede sostener un `[N]`**: la etiqueta")
    A("exige numeral verificado, y aquí no hay contra qué verificar.")
    A("")
    A("| id | Documento | Esfuerzo | Qué desbloquearía | Sustituto vigente |")
    A("|---|---|---|---|---|")
    # literal-ok: orden de presentacion de los cuatro esfuerzos, de mas
    # barato a mas caro. No es un valor de proyecto: es como se ordena una
    # tabla.
    orden = {"facil, es descarga publica": 0, "compra o suscripcion": 1,
             "gabinete": 2, "de campo": 3}   # literal-ok: orden de presentacion, no valor de proyecto
    _sin_orden = 9   # literal-ok: los que no esten en el orden, al final
    for f in sorted(registro.fuentes_ausentes,
                    key=lambda x: (orden.get(x.ausencia.esfuerzo.value,
                                            _sin_orden), x.id)):
        a = f.ausencia
        A(f"| `{f.id}` | {f.titulo} | {a.esfuerzo.value} | "
          f"{a.que_desbloquearia} | {a.sustituto_vigente or '—'} |")
    A("")

    # -- Catalogos ---------------------------------------------------------
    A("## 3. Catálogos, que NO son fuentes")
    A("")
    A("Un tope de catálogo no tiene numeral, y el registro no le deja fingir")
    A("que lo tiene: un `Catalogo` no puede ser el `fuente_id` de una cita.")
    A("")
    for c in registro.catalogos:
        A(f"- **`{c.id}` — {c.titulo}** ({c.proveedor_o_ambito}).")
        A(f"  Qué norma NO lo sostiene: {c.que_norma_NO_lo_sostiene}")
    A("")

    # -- Citas -------------------------------------------------------------
    A("## 4. Citas")
    A("")
    A("Una fila por objeto `Cita`. El `id` es el ancla: no hay número de")
    A("línea que se pueda romper.")
    A("")
    for fuente_id in sorted({c.fuente_id for c in registro.citas}):
        f = registro.fuente(fuente_id)
        A(f"### {f.titulo}  (`{f.id}`)")
        A("")
        A("| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |")
        A("|---|---|---|---|---|---|")
        for c in sorted(registro.citas_de(fuente_id), key=lambda x: x.id):
            A(f"| `{c.id}` | {c.numeral} | {_titulo(c)} | {_pagina(c)} "
              f"| {c.caracter.value} | {_verificacion(c)} |")
        A("")
        for c in sorted(registro.citas_de(fuente_id), key=lambda x: x.id):
            if c.nota:
                A(f"> **`{c.id}`** — {c.nota}")
                A("")

    # -- Tablas ------------------------------------------------------------
    A("## 5. Tablas normativas")
    A("")
    A("El rótulo de completitud **no lo escribe nadie**: lo deriva la tabla de")
    A("sus campos `alcance` y `uso`, de modo que no puede contradecirlos.")
    A("")
    for t in sorted(registro.tablas, key=lambda x: x.id):
        A(f"### `{t.id}` — {t.titulo_literal}")
        A("")
        A(f"- Cita: `{t.cita_id}`")
        A(f"- {t.rotulo_de_completitud()}")
        if t.fuente_declarada_por_la_tabla:
            A(f"- Fuente que la tabla se atribuye: "
              f"*{t.fuente_declarada_por_la_tabla}*")
        if isinstance(t.alcance, Acotada):
            A(f"- **Transcripción acotada.** Razón: {t.alcance.razon}")
            A(f"  - Qué queda fuera: {t.alcance.que_queda_fuera}")
            A(f"  - Dónde leerlo: {t.alcance.donde_leerlo}")
        for c in t.columnas:
            if isinstance(c.uso, NoUsada):
                A(f"- Columna «{c.etiqueta_literal}» transcrita y **no "
                  f"usada**: {c.uso.por_que_no}")
            elif isinstance(c.uso, PendienteDeCondicion):
                A(f"- Columna «{c.etiqueta_literal}»: **elección pendiente** "
                  f"(`{c.uso.condicion_id}`) — el cálculo se detiene")
        for fila in t.filas:
            if isinstance(fila.uso, PendienteDeCondicion):
                A(f"- Fila «{fila.legible()}»: **elección pendiente** "
                  f"(`{fila.uso.condicion_id}`)")
        for lag in t.lagunas:
            A(f"- **Laguna de la fuente**: {lag.que_no_cubre}. "
              f"Se cierra con: {lag.con_que_regla}"
              + (f" (`{lag.quien_lo_cierra}`)" if lag.quien_lo_cierra else ""))
        for a in t.afirmaciones_negativas:
            A(f"- **Afirmación negativa**: {a.que_no_dice}. "
              f"Ámbito barrido: {a.ambito_barrido}")
        if t.interpretacion:
            A(f"- **Interpretación del proyectista, no de la fuente**: "
              f"{t.interpretacion.texto}")
            for x in t.interpretacion.en_contra:
                A(f"  - En contra: {x}")
            for x in t.interpretacion.a_favor:
                A(f"  - A favor: {x}")
        for e in t.erratas:
            A(f"- **Errata declarada**: `{e}`")
        if t.vistas_de_calculo:
            A(f"- Vistas de cálculo derivadas: "
              + ", ".join(f"`{v}`" for v in t.vistas_de_calculo))
        A("")
        A("| Fila | " + " | ".join(c.etiqueta_literal for c in t.columnas)
          + " | Uso |")
        A("|---" * (len(t.columnas) + 2) + "|")
        for fila in t.filas:
            celdas = []
            for c in t.columnas:
                v = fila.valores.get(c.id, "")
                v = getattr(v, "valores", v)
                if isinstance(v, tuple):
                    v = " – ".join(str(x) for x in v)
                v = getattr(v, "value", v)
                celdas.append(str(v))
            uso = ("usada" if isinstance(fila.uso, Usada)
                   else "no usada" if isinstance(fila.uso, NoUsada)
                   else "pendiente")
            A(f"| {fila.legible()} | " + " | ".join(celdas) + f" | {uso} |")
        A("")
        for nota in t.notas_al_pie:
            A(f"> {nota.marca} {nota.texto.texto}")
            A("")

    # -- Condiciones que bloquean -----------------------------------------
    A("## 6. Condiciones que detienen el cálculo")
    A("")
    A("Lo indeterminado bloquea; lo que no bloquea lleva su justificación")
    A("escrita, y el test la exige.")
    A("")
    A("| id | Dónde | Resuelve | Efecto |")
    A("|---|---|---|---|")
    for donde, cond in sorted(registro.condiciones(), key=lambda x: x[1].id):
        r = cond.resuelve
        como = getattr(r, "clave", None) or getattr(r, "expresion", None) \
            or getattr(r, "por_que", "")
        A(f"| `{cond.id}` | {donde} | `{como}` | "
          f"{cond.efecto_si_indeterminada.value} |")
    A("")

    # -- Discrepancias -----------------------------------------------------
    A("## 7. Discrepancias declaradas")
    A("")
    A("`CLAUDE.md` obliga, cuando la fuente primaria gana a la hoja de ruta, a")
    A("declararlo en el punto de uso, a reportar el defecto contra la hoja de")
    A("ruta **y a dejar dicho que la hoja de ruta sigue mal mientras no se")
    A("corrija**. La tercera obligación vive aquí.")
    A("")
    for estado in EstadoDiscrepancia:
        deste = [d for d in registro.discrepancias if d.estado is estado]
        if not deste:
            continue
        A(f"### {estado.value}")
        A("")
        for d in sorted(deste, key=lambda x: x.id):
            A(f"- **`{d.id}` — {d.objeto}.** Gana **{d.gana}**: {d.por_que}")
            A(f"  - Si se sigue la otra: {d.efecto_si_se_sigue_la_otra}")
            for parte in d.partes:
                A(f"  - *{parte.quien}*: {parte.que_dice}")
        A("")

    # -- Pendientes --------------------------------------------------------
    A("## 8. Lo que falta por transcribir")
    A("")
    pendientes = registro.citas_con_pendientes()
    A(f"Campos `POR_TRANSCRIBIR` en el registro: **"
      f"{registro.cuenta_por_transcribir()}**, en {len(pendientes)} citas.")
    A("Este número es un **trinquete**: sólo puede decrecer, y un test lo")
    A("vigila. Una cita con cualquier campo pendiente NO puede llevar firma de")
    A("verificación.")
    A("")
    for c in sorted(pendientes, key=lambda x: x.id):
        A(f"- `{c.id}`: " + ", ".join(f"`{n}`" for n in c.campos_pendientes))
    sin_verificar = registro.citas_sin_verificar()
    A("")
    A(f"Citas sin firma de verificación: **{len(sin_verificar)}** de "
      f"{len(registro.citas)}.")
    for c in sorted(sin_verificar, key=lambda x: x.id):
        A(f"- `{c.id}`")
    A("")
    return "\n".join(L) + "\n"


def main(argv: List[str]) -> int:
    """
    `python3 -m src.normativa.manifiesto [--escribir]`

    Sin `--escribir` solo informa; con `--escribir` deja los dos documentos
    en disco.
    """
    from .registro import construir
    escribir = "--escribir" in argv

    texto = MANIFIESTO.read_text(encoding="utf-8")
    nuevo, cambios, prosa = resincronizar(texto)
    print(f"manifiesto_citas.md: {len(cambios)} referencias resincronizadas, "
          f"{prosa} de prosa (sin símbolo que anclar)")
    muestra = 20   # literal-ok: cuantos cambios se listan antes de resumir
    for c in cambios[:muestra]:
        print("   ", c)
    if len(cambios) > muestra:
        print(f"    ... y {len(cambios) - muestra} más")

    indice = indice_del_registro(construir())
    print(f"manifiesto_registro_normativo.md: {len(indice.splitlines())} líneas")

    if escribir:
        MANIFIESTO.write_text(nuevo, encoding="utf-8")
        INDICE_REGISTRO.write_text(indice, encoding="utf-8")
        print("escritos.")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv))
