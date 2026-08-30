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


# Los ids de las tres auditorias -- `NOR-HDS-04`, `MAT-D3`, `SIS-B-10` -- van
# entre backticks como cualquier simbolo y NO lo son. Sin este filtro, el
# primer identificador de `NOR-E060-02` es `NOR`, que no existe en ningun
# archivo de src/ y por eso no llegaba a resolver nada; el daño no era ese,
# sino que la fila CONTABA como "cita un identificador" y la comprobacion de
# mencion la daba por buena en cuanto el bloque de destino nombrara cualquier
# otra ficha. Es la diferencia entre una guardia que verifica y una que se
# satisface sola (SIS-G-03).
ID_DE_FICHA = re.compile(r"^(?:NOR|MAT|SIS)-")


def _simbolos_citados(fila: str) -> List[str]:
    """
    Identificadores entre backticks en esa fila del manifiesto.

    SE DEVUELVE TAMBIEN LA COLA DE UN NOMBRE PUNTEADO, y no es un detalle de
    forma: el manifiesto escribe `M9.cuantia_de_diseno` o `M11.seccion_eg2013`
    para decir "esta funcion, de este modulo", y quedarse con el primer
    identificador convertia esa cita en `M9` -- un alias de archivo que no es
    simbolo de nada --. La fila perdia su ancla y caia al saco de prosa, donde
    lo unico que se comprueba es que la linea no este en blanco. Cuatro
    referencias estaban desviadas justo asi, y las cuatro salieron a la luz al
    devolver la cola (SIS-G-03).
    """
    simbolos: List[str] = []
    for trozo in re.findall(r"`([^`]+)`", fila):
        limpio = trozo.strip().lstrip("↳↻⚠~✚⟳ ")
        if ID_DE_FICHA.match(limpio):
            continue
        m = re.match(r"^([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", limpio)
        if not m:
            continue
        # `constantes_normativas.py` es una RUTA, no un nombre punteado: su
        # cola es `py`, que casa con cualquier bloque que nombre cualquier
        # archivo del proyecto.
        partes = m.group(1).removesuffix(".py").split(".")
        for candidato in (partes[0], partes[-1]):
            if candidato not in simbolos:
                simbolos.append(candidato)
    return simbolos


_CACHE_SIMBOLOS: List[set] = []


def _SIMBOLOS_DEL_PROYECTO() -> set:
    """
    Todo nombre que `src/` define en alguna parte.

    Sirve para separar un SIMBOLO de un token que solo lo parece. El
    manifiesto escribe formulas y rutas entre backticks, y de ahi salian
    `max`, `Ks`, `q`, `t` y --- el peor --- `py`, cola de
    `constantes_normativas.py`, que casa con cualquier bloque que nombre
    cualquier archivo del proyecto. Un comodin en una comprobacion es una
    comprobacion que se satisface sola, que es el defecto que el filtro
    `ID_DE_FICHA` ya cerro para los ids de auditoria y este cierra para el
    resto.
    """
    if not _CACHE_SIMBOLOS:
        nombres: set = set()
        campo = re.compile(r"^\s+([a-z_]\w*)\s*:\s*[A-Za-z\"']")
        for ruta in sorted((RAIZ / "src").rglob("*.py")):
            if "__pycache__" in ruta.parts:
                continue
            rel = str(ruta.relative_to(RAIZ))
            nombres |= set(_bloques(rel))
            # Los campos anotados de una dataclass (`seccion_eg2013: str`) son
            # simbolos del proyecto y `_bloques` no los ve: no abren bloque,
            # pero una fila del manifiesto los cita y el codigo los usa.
            nombres |= {m.group(1) for l in _lineas(rel)
                        for m in [campo.match(l)] if m}
        _CACHE_SIMBOLOS.append(nombres)
    return _CACHE_SIMBOLOS[0]


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
        return _linea_por_mencion(rel, simbolos, linea_actual)
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


def _linea_por_mencion(rel: str, simbolos: List[str],
                       linea_actual: int) -> Optional[int]:
    """
    Cuando el archivo USA el simbolo sin definirlo.

    Es el caso legitimo que SIS-G-03 saco del saco de prosa: `M5` consume
    `V_MIN`, que vive en `constantes_normativas.py`, y una fila que cita
    `V_MIN` y apunta a M5 esta apuntando a un USO. No hay bloque del simbolo
    al que anclar, pero si hay algo que derivar del nombre: LA LINEA QUE LO
    NOMBRA, la mas cercana a la que el manifiesto ya declara.

    LA PRIMERA VERSION ANCLABA AL BLOQUE, Y ERA DEMASIADO FLOJA. Bastaba con
    que cualquier bloque del archivo nombrara el simbolo en cualquier parte:
    una referencia sabotada a 2900 lineas de su uso pasaba en verde, y la
    regla «si sigue cayendo en un bloque que lo menciona, no se mueve»
    remataba el agujero impidiendo que el regenerador la devolviera a su
    sitio. Un bloque de `criterios_adoptados.py` tiene noventa lineas: decir
    que el destino «habla del simbolo» porque su bloque lo nombra noventa
    lineas mas abajo no es una comprobacion.

    Ahora se ancla al RENGLON. Se descartan las lineas de `import`, que
    nombran el simbolo sin decir nada de el, y se descartan los tokens que no
    son simbolos del proyecto --- `py` sacado de un backtick
    `constantes_normativas.py`, o el `max` de una formula ---, que hacian de
    comodin. Sin menciones reales, `None`: es prosa de verdad y el cupo la
    cuenta.
    """
    lineas = _lineas(rel)
    reales = [s for s in simbolos if s in _SIMBOLOS_DEL_PROYECTO()]
    if not reales:
        return None
    menciones = [
        n for n, linea in enumerate(lineas, 1)
        if not linea.lstrip().startswith(("import ", "from "))
        and any(re.search(r"\b" + re.escape(s) + r"\b", linea) for s in reales)
    ]
    if not menciones:
        return None
    return min(menciones, key=lambda n: abs(n - linea_actual))


def _primer_renglon_con_texto(rel: str, desde: int,
                              hasta: Optional[int]) -> int:
    lineas = (RAIZ / rel).read_text(encoding="utf-8").split("\n")
    tope = len(lineas) if hasta is None else min(hasta, len(lineas))
    for n in range(desde, tope + 1):
        if lineas[n - 1].strip():
            return n
    return desde


def _sin_rango_imposible(original: str, linea: int, sufijo: Optional[str],
                         etiqueta: str, rel: str, cambios: List[str],
                         n_md: int) -> str:
    """
    Quita el sufijo de rango cuando el rango NO PUEDE SER: `[CN:170-49]`.

    La notacion `[ETQ:a-b]` era un rango real (de la linea a a la b). Al
    resincronizar, esta funcion reescribia la `a` y conservaba la `b` vieja, de
    modo que CINCUENTA de las 57 con sufijo acabaron anunciando tramos
    imposibles --- el
    final por delante del principio ---. Un rango cuyo final no se deriva de
    nada no es informacion: es ruido con forma de dato, y ningun test lo
    miraba (SIS-G-03).

    Se quita SOLO el imposible. Un rango bien formado (`[CN:6-8]`) dice algo
    cierto y se conserva.
    """
    if not sufijo:
        return original
    fin = int(sufijo[1:])
    if fin > linea:
        return original
    cambios.append(f"md:{n_md}  {rel}:{linea}{sufijo} -> :{linea} "
                   f"(rango imposible retirado)")
    return f"[{etiqueta}:{linea}]({rel}:{linea})"


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
                return _sin_rango_imposible(m.group(0), linea, sufijo,
                                            etiqueta, rel, cambios, n_md)
            destino = _linea_del_simbolo(rel, simbolos, linea)
            if destino is None:
                prosa += 1
                return _sin_rango_imposible(m.group(0), linea, sufijo,
                                            etiqueta, rel, cambios, n_md)
            if destino == linea:
                return _sin_rango_imposible(m.group(0), linea, sufijo,
                                            etiqueta, rel, cambios, n_md)
            cambios.append(f"md:{n_md}  {rel}:{linea} -> :{destino} "
                           f"({destino - linea:+d}, simbolo "
                           f"`{simbolos[0] if simbolos else '?'}`)")
            # EL SUFIJO SE TIRA, NO SE ARRASTRA. La notacion original era un
            # rango real -- `[CN:33-39]`, de la linea 33 a la 39 -- y esta
            # funcion reescribia el inicio conservando el final viejo, de modo
            # que 50 etiquetas acabaron mostrando rangos IMPOSIBLES como
            # `[CN:170-49]`: la etiqueta que el lector ve mentia sobre el
            # tramo, y ningun test lo miraba. Un rango cuyo final no se
            # deriva de nada no es informacion, es ruido con forma de dato.
            # La linea de llegada la fija el simbolo; el tramo lo fija su
            # bloque, y quien quiera verlo abre el archivo (SIS-G-03).
            return f"[{etiqueta}:{destino}]({rel}:{destino})"

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

    # -- Fundamentos -------------------------------------------------------
    A("## 6-bis. Fundamentos: por qué se hace cada paso")
    A("")
    A("El campo `por_que` de `PasoDeMemoria` (§4.4 del plan v12) sale de aquí,")
    A("no del docstring del módulo que calcula. El `verbo` está sostenido por")
    A("el `caracter` de al menos una de sus citas — invariante T11 —, que es")
    A("lo que impide escribir «la norma obliga» sobre un párrafo que")
    A("recomienda.")
    A("")
    A("| id | Fase | Paso | Verbo | Citas |")
    A("|---|---|---|---|---|")
    for f in sorted(registro.fundamentos, key=lambda x: x.id):
        citas = ", ".join(f"`{c}`" for c in f.citas)
        A(f"| `{f.id}` | {f.fase} | {f.que_paso} | **{f.verbo.value}** | "
          f"{citas} |")
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
