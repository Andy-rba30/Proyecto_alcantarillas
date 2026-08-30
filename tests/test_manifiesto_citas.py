"""
tests/test_manifiesto_citas.py
==============================
El manifiesto de citas existe para que un revisor pueda ir del valor al
codigo que lo declara. Una referencia `archivo:linea` que no lleva a lo que
dice llevar no es media cita: es una cita que no se puede verificar, que es
justo lo que el documento existe para permitir.

Por que este test. En una auditoria se encontro que 195 de las 209
referencias verificables estaban desfasadas -- hasta +397 lineas -- y nadie
lo habia notado. No fue descuido de nadie en particular: los enlaces apuntan
a numeros de linea y CUALQUIER insercion en un archivo citado desplaza todos
los de abajo, en silencio. Sin este test, la correccion se degrada sola con
el proximo commit que mueva lineas.

Como verifica. Para cada referencia se toma el simbolo citado en su propia
fila del manifiesto, se calcula el BLOQUE que ese simbolo ocupa en el archivo
(de su definicion a la siguiente) y se comprueba que la linea referenciada
caiga dentro. Apuntar DENTRO del bloque es legitimo y frecuente: muchas filas
citan el cuerpo de un criterio -- su `fuente`, su `verificacion_pendiente` --
y no su cabecera. Solo cuenta como desfase salir del bloque.
"""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MANIFIESTO = RAIZ / "docs" / "manifiesto_citas.md"

REFERENCIA = re.compile(
    r"\[([A-Za-z0-9_.]+):(\d+)(?:,\s*\d+)?(-\d+)?\]\((src/[^)]+?):(\d+)\)")

# Definiciones que abren bloque: def/class a cualquier indentacion, constantes
# y funciones de modulo, y las entradas de los diccionarios grandes
# (CRITERIOS, MANNING, V_MAX...), que se citan fila por fila.
DEFINICION = re.compile(
    r"^(?:(\s*)(?:def|class)\s+([A-Za-z_]\w*)"          # def/class, a cualquier indentacion
    r"|([A-Z_][A-Z0-9_]*)\s*[:=]"                        # CONSTANTE = ... (nivel de modulo)
    r"|    \"([A-Za-z_]\w*)\"\s*:"                       # entrada de dict citada fila a fila
    r"|([a-z_]\w*)\s*=(?!=))")                           # funcion/variable de modulo, columna 0

# La ultima alternativa exige COLUMNA 0 a proposito. Sin eso, cada `valor=...`
# dentro de un `Criterio(` contaba como definicion de un simbolo `valor` y
# truncaba el bloque del criterio en su primera linea, de modo que una
# referencia a su `fuente` o a su `justificacion` -- el caso legitimo que este
# test dice admitir -- quedaba fuera del bloque y se reportaba como rota.


# ---------------------------------------------------------------------------
# Excepcion declarada: las referencias de PROSA
# ---------------------------------------------------------------------------
# Hay filas del manifiesto que no citan un simbolo sino una afirmacion --
# sobre todo las "Afirmacion negativa", que registran que una norma NO dice
# algo, y las notas al pie. No tienen identificador que anclar, de modo que
# este test no puede verificarlas y NO las cuenta como fallo.
#
# Es una limitacion real y se declara aqui en vez de disimularse: una
# referencia de prosa puede quedar desfasada sin que nada avise. Lo que si se
# verifica de ellas es lo unico verificable sin simbolo -- que la linea exista
# y no este vacia -- porque aterrizar en una linea en blanco es prueba directa
# de que el enlace se movio.
#
# EL CUPO ES UN TRINQUETE, no un tope: SOLO PUEDE BAJAR. Si crece, es que se
# estan anadiendo citas sin identificador, y eso es lo que produjo NOR-MAN-04.
#
# LA META ES CERO (T9 del diseño del registro normativo) y hoy no se puede
# cumplir, por una razon concreta y no por dejadez: una fila que no cita
# ningun simbolo no tiene a que anclarse. Lo que la hace cumplible es que la
# fila nazca de un OBJETO con id estable, y eso exige que el registro
# normativo contenga el corpus entero. Hoy contiene las citas de C11, C12 y
# C02 y las tablas que esos tres tocan; el resto sigue en prosa.
#
# Mientras tanto, lo que SI cambio es que las referencias con simbolo ya no se
# mantienen a mano: las genera `src/normativa/manifiesto.py` desde el nombre
# del simbolo, y el test de abajo regenera y compara. El numero de linea deja
# de ser un dato que mantener y pasa a ser una comodidad regenerable.
#
# EL SACO DE PROSA NO ERA UNO, ERAN DOS (SIS-G-03)
# ------------------------------------------------
# Hasta S19 «de prosa» significaba, literalmente, «la fila no cita ningun
# simbolo QUE ESTE DEFINIDO EN EL ARCHIVO DE DESTINO». Eso mete en el mismo
# saco dos cosas que no se parecen:
#
#   (a) la fila no cita NINGUN identificador -- la afirmacion negativa, la
#       nota al pie. No hay nada que anclar y no lo habra: es el hueco real.
#
#   (b) la fila SI cita un identificador, y el archivo al que apunta no lo
#       define porque lo USA (M5 consume `V_MIN`, que vive en
#       constantes_normativas.py). Ahi si hay algo que comprobar: que la
#       linea de destino HABLE del simbolo que la fila nombra.
#
# Meter (b) en el saco de (a) es lo que dejaba pasar en verde una referencia
# aterrizada en cualquier parte. Al separarlos aparecieron VEINTE
# referencias desviadas -- entre ellas `e2_volteo()` y `empuje_flotacion()`,
# nombres que el codigo ya no tiene, y `ESPACIAMIENTO_MAX_VECES_ESPESOR`
# apuntando al bloque de `n_s_zapata_en_talud`, a 950 lineas de su uso --,
# ninguna de las cuales se estaba buscando. La ficha decia que la tasa entre
# las no ancladas era DESCONOCIDA; medida con la regla de hoy sobre el arbol
# anterior (f56360c), era 20 de 64. Y de las 39 que ni siquiera nombraban un
# simbolo del proyecto, 27 tampoco llevaban a donde decian: se anclaron una a
# una, leyendo la linea de destino.
#
# Las de (b) las vigila `test_toda_fila_que_cita_un_identificador_lo_nombra_
# en_su_destino`, SIN CUPO: no son una excepcion declarada, son referencias
# verificables que hasta ahora nadie verificaba.
MAX_REFERENCIAS_DE_PROSA = 26

# El hueco de verdad -- el caso (a) --, con su propio trinquete. Se separa del
# anterior para que bajar el total a base de anclar por USO no disimule que
# las filas sin identificador siguen ahi. Esta es la que T9 quiere en cero.
#
# ESTUVO EN 2 UNAS HORAS Y SUBE A 4, y hay que decir por que porque un
# trinquete que sube sin explicacion deja de serlo. No entraron dos filas
# nuevas: la REGLA se estrecho. Al exigir que el token citado sea un simbolo
# que `src/` define de verdad --- para que `py`, `max` o `Ks` dejaran de hacer
# de comodin ---, las dos referencias de la fila de `FS_flotacion` pasaron de
# «verificables por mencion» a «sin identificador», que es lo que son:
# `FS_flotacion` se RETIRO del proyecto y la fila lo nombra justamente para
# decirlo. Una fila que cita un simbolo que ya no existe no tiene a que
# anclarse, y contarla como verificada era el mismo autoengaño en pequeño.
MAX_REFERENCIAS_SIN_IDENTIFICADOR = 4


def _codigo(rel: str) -> list:
    return (RAIZ / rel).read_text(encoding="utf-8").split("\n")


def _bloques(rel: str) -> dict:
    """{simbolo: [(primera_linea, ultima_linea), ...]} de un archivo."""
    lineas, definiciones = _codigo(rel), []
    for numero, linea in enumerate(lineas, 1):
        m = DEFINICION.match(linea)
        if m:
            nombre = next((g for g in m.groups()[1:] if g), None)
            if nombre:
                definiciones.append((numero, nombre))
    bloques = {}
    for i, (inicio, nombre) in enumerate(definiciones):
        fin = definiciones[i + 1][0] - 1 if i + 1 < len(definiciones) else len(lineas)
        bloques.setdefault(nombre, []).append((inicio, fin))
    return bloques


# Ids de ficha de auditoria (`NOR-HDS-04`, `MAT-D3`, `SIS-B-10`): van entre
# backticks y no son simbolos. Ver la nota homologa en
# src/normativa/manifiesto.py, donde esto vive duplicado a proposito.
ID_DE_FICHA = re.compile(r"^(?:NOR|MAT|SIS)-")


def _simbolos_citados(fila: str) -> list:
    """
    Identificadores entre backticks en esa fila del manifiesto.

    Devuelve el modulo Y la cola de un nombre punteado: `M9.cuantia_de_diseno`
    aporta `M9` y `cuantia_de_diseno`. Quedarse con el primero dejaba la fila
    anclada a un alias de archivo que no es simbolo de nada, y la mandaba al
    saco de prosa -- donde lo unico que se comprueba es que la linea exista y
    no este en blanco. Cuatro referencias llevaban asi, desviadas, desde antes
    de S16.5 (SIS-G-03).
    """
    simbolos = []
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


def _referencias():
    """(n_linea_md, fila, texto_ref, archivo, linea_citada) de cada enlace."""
    for numero, fila in enumerate(MANIFIESTO.read_text(encoding="utf-8").split("\n"), 1):
        for m in REFERENCIA.finditer(fila):
            yield numero, fila, m.group(0), m.group(4), int(m.group(5))


def _clasificadas():
    """Reparte las referencias en (verificables_por_simbolo, de_prosa)."""
    por_simbolo, prosa = [], []
    for n_md, fila, ref, rel, n in _referencias():
        bloques = _bloques(rel)
        candidatos = [s for s in _simbolos_citados(fila) if s in bloques]
        destino = por_simbolo if candidatos else prosa
        destino.append((n_md, ref, rel, n, candidatos))
    return por_simbolo, prosa


def _bloque_que_contiene(rel: str, n: int):
    """(simbolo, inicio, fin) del bloque en el que cae la linea n, o None."""
    for simbolo, tramos in _bloques(rel).items():
        for inicio, fin in tramos:
            if inicio <= n <= fin:
                return simbolo, inicio, fin
    return None


def _tramo_de_verificacion(rel: str, n: int):
    """
    El TRAMO contra el que se comprueba una mencion: EL PARRAFO DE LLEGADA.

    Es decir, la linea referenciada y las contiguas no vacias a su alrededor.
    Nada mas.

    LA PRIMERA VERSION TOMABA EL BLOQUE, Y ERA UNA GUARDIA QUE SE SATISFACIA
    SOLA. Un bloque de `criterios_adoptados.py` tiene noventa lineas y uno de
    `constantes_normativas.py` puede tener quinientas: aceptar que el destino
    «habla del simbolo» porque su bloque lo nombra setenta y cinco lineas mas
    abajo no comprueba nada. Medido: seis referencias saboteadas a otro
    archivo, o a 2900 lineas de su uso, pasaban con la suite entera en verde.

    El parrafo es el tramo que un lector ve al abrir el enlace, y esa es
    exactamente la propiedad que la referencia promete.
    """
    lineas = _codigo(rel)
    if not (1 <= n <= len(lineas)):
        return "(fuera del archivo)", n, n
    inicio = n
    while inicio > 1 and lineas[inicio - 2].strip():
        inicio -= 1
    fin = n
    while fin < len(lineas) and lineas[fin].strip():
        fin += 1
    tramo = _bloque_que_contiene(rel, n)
    return (tramo[0] if tramo else "(cabecera del modulo)"), inicio, fin


_CACHE_SIMBOLOS = []


def _simbolos_del_proyecto() -> set:
    """
    Todo nombre que `src/` define. Ver la nota homologa en
    `src/normativa/manifiesto.py`: separa un SIMBOLO de un token que solo lo
    parece (`max`, `Ks`, `q`, y el peor de todos, `py`).
    """
    if not _CACHE_SIMBOLOS:
        nombres = set()
        campo = re.compile(r"^\s+([a-z_]\w*)\s*:\s*[A-Za-z\"']")
        for ruta in sorted((RAIZ / "src").rglob("*.py")):
            if "__pycache__" in ruta.parts:
                continue
            rel = str(ruta.relative_to(RAIZ))
            nombres |= set(_bloques(rel))
            # Los campos anotados de una dataclass (`seccion_eg2013: str`) son
            # simbolos del proyecto y `_bloques` no los ve: no abren bloque,
            # pero una fila del manifiesto los cita y el codigo los usa.
            nombres |= {m.group(1) for l in _codigo(rel)
                        for m in [campo.match(l)] if m}
        _CACHE_SIMBOLOS.append(nombres)
    return _CACHE_SIMBOLOS[0]


def _prosa_repartida():
    """
    Parte el saco de prosa en las dos poblaciones que no son la misma cosa.

    Devuelve (sin_identificador, por_mencion, rotas):

      sin_identificador  la fila no nombra ningun identificador. Hueco real.
      por_mencion        la fila nombra uno y la linea de destino cae en un
                         bloque que LO NOMBRA. Verificada.
      rotas              la fila nombra uno y el destino no habla de el. Es
                         una referencia que no lleva a lo que dice llevar.
    """
    sin_identificador, por_mencion, rotas = [], [], []
    for n_md, fila, ref, rel, n in _referencias():
        bloques = _bloques(rel)
        simbolos = _simbolos_citados(fila)
        if [s for s in simbolos if s in bloques]:
            continue                       # ya la cubre la via por definicion
        # Una fila que cita un simbolo RETIRADO --- `FS_flotacion`, que se
        # nombra justamente para decir que ya no existe --- no tiene nada que
        # anclar: cuenta como prosa, no como referencia rota.
        reales = [s for s in simbolos if s in _simbolos_del_proyecto()]
        if not reales:
            sin_identificador.append((n_md, ref, rel, n))
            continue
        lineas = _codigo(rel)
        nombre, inicio, fin = _tramo_de_verificacion(rel, n)
        cuerpo = "\n".join(lineas[inicio - 1:fin])
        nombrados = [s for s in reales
                     if re.search(r"\b" + re.escape(s) + r"\b", cuerpo)]
        if nombrados:
            por_mencion.append((n_md, ref, rel, n, nombrados))
        else:
            rotas.append((n_md, ref, rel, n, simbolos, nombre))
    return sin_identificador, por_mencion, rotas


# ---------------------------------------------------------------------------

def test_el_manifiesto_existe_y_tiene_referencias():
    assert MANIFIESTO.exists(), "no hay manifiesto de citas que verificar"
    assert sum(1 for _ in _referencias()) > 200, (
        "el manifiesto perdio la mayoria de sus referencias: revisa si se "
        "trunco el archivo")


def test_toda_referencia_apunta_a_un_archivo_que_existe():
    faltan = {rel for _, _, _, rel, _ in
              ((a, b, c, d, e) for a, b, c, d, e in _referencias())
              if not (RAIZ / rel).exists()}
    assert not faltan, f"referencias a archivos inexistentes: {sorted(faltan)}"


def test_ninguna_referencia_apunta_mas_alla_del_final_del_archivo():
    fuera = [f"md:{n_md} {ref} (el archivo tiene {len(_codigo(rel))} lineas)"
             for n_md, _, ref, rel, n in _referencias()
             if n > len(_codigo(rel))]
    assert not fuera, "referencias fuera de rango:\n  " + "\n  ".join(fuera)


def test_ninguna_referencia_aterriza_en_una_linea_vacia():
    """
    Vale tambien para las de prosa: una linea en blanco no es el sitio de
    ninguna cita, y es la senal mas barata de que el enlace se movio.
    """
    vacias = [f"md:{n_md} {ref} -> {rel}:{n}"
              for n_md, _, ref, rel, n in _referencias()
              if not _codigo(rel)[n - 1].strip()]
    assert not vacias, (
        "referencias que caen en una linea vacia:\n  " + "\n  ".join(vacias))


def test_T9_el_cupo_de_referencias_de_prosa_solo_decrece():
    """
    El trinquete. Una referencia de prosa no se puede verificar contra el
    codigo: es el hueco declarado del que salieron los 66 defectos que la
    auditoria encontro, y por eso el cupo solo puede bajar.
    """
    _, prosa = _clasificadas()
    assert len(prosa) <= MAX_REFERENCIAS_DE_PROSA, (
        f"el manifiesto tiene {len(prosa)} referencias sin simbolo que anclar "
        f"y el cupo esta en {MAX_REFERENCIAS_DE_PROSA}. Ancla la fila a un "
        "simbolo (o a un id del registro) en vez de subir el cupo")


def test_T8_el_manifiesto_esta_sincronizado_con_el_codigo():
    """
    T8 DEL DISEÑO, y es la CURA de NOR-MAN-04, no su parche.

    Renumerar a mano las referencias rotas las arregla hoy y las rompe otra
    vez con la proxima insercion: es lo que ya se hizo una vez y por lo que el
    hallazgo existe. Lo que no se rompe solo es DERIVAR el numero de linea del
    NOMBRE DEL SIMBOLO, cada vez, desde el codigo.

    Este test regenera el manifiesto a memoria y compara. Si difiere, no se
    edita el test ni se renumera a mano:

        python3 -m src.normativa.manifiesto --escribir
    """
    from normativa.manifiesto import resincronizar
    texto = MANIFIESTO.read_text(encoding="utf-8")
    regenerado, cambios, _ = resincronizar(texto)
    assert regenerado == texto, (
        f"el manifiesto esta desincronizado en {len(cambios)} referencias.\n"
        "Regeneralo con:  python3 -m src.normativa.manifiesto --escribir\n  "
        + "\n  ".join(cambios[:15]))


def test_T8_el_indice_del_registro_esta_sincronizado():
    """
    El OTRO manifiesto, el que se genera entero desde los objetos. Ahi no hay
    numeros de linea que puedan romperse porque no hay lineas: hay ids.
    """
    from normativa.manifiesto import INDICE_REGISTRO, indice_del_registro
    from normativa.registro import construir
    assert INDICE_REGISTRO.exists(), (
        "falta docs/manifiesto_registro_normativo.md: generalo con "
        "python3 -m src.normativa.manifiesto --escribir")
    assert INDICE_REGISTRO.read_text(encoding="utf-8") == \
        indice_del_registro(construir()), (
            "el indice del registro esta desincronizado. NO se edita a mano: "
            "python3 -m src.normativa.manifiesto --escribir")


def test_toda_referencia_cae_dentro_del_bloque_del_simbolo_que_cita():
    """
    EL TEST QUE IMPORTA. Si falla, alguien movio lineas en un archivo citado
    y el manifiesto quedo apuntando a otra cosa.

    Para arreglarlo NO se edita este test: se corrige el numero de linea en
    docs/manifiesto_citas.md. El mensaje de fallo dice, por cada referencia
    rota, a que linea deberia apuntar.
    """
    por_simbolo, _ = _clasificadas()
    rotas = []
    for n_md, ref, rel, n, candidatos in por_simbolo:
        bloques = _bloques(rel)
        tramos = [t for s in candidatos for t in bloques[s]]
        if any(inicio <= n <= fin for inicio, fin in tramos):
            continue
        destino = min((inicio for inicio, _ in tramos), key=lambda x: abs(x - n))
        rotas.append(f"md:{n_md}  {ref}  cita `{candidatos[0]}`, "
                     f"que vive en {rel}:{destino} (desfase {destino - n:+d})")
    assert not rotas, (
        f"{len(rotas)} de {len(por_simbolo)} referencias no caen dentro del "
        "bloque que citan.\nCorrige el numero de linea en "
        "docs/manifiesto_citas.md:\n  " + "\n  ".join(rotas))


def test_las_referencias_de_prosa_no_crecen_sin_control():
    """
    Las de prosa son la excepcion declarada de este test: sin simbolo que
    anclar, no se pueden verificar. El cupo evita que la excepcion se ensanche
    en silencio hasta vaciar de sentido al resto.
    """
    _, prosa = _clasificadas()
    assert len(prosa) <= MAX_REFERENCIAS_DE_PROSA, (
        f"{len(prosa)} referencias sin simbolo verificable, por encima del cupo "
        f"de {MAX_REFERENCIAS_DE_PROSA}. O la fila nueva cita un identificador "
        "y hay que ponerlo entre backticks, o el cupo se sube a conciencia.")


def test_la_cobertura_verificable_no_se_degrada():
    """
    Contrapeso del anterior: que la mayoria de las referencias siga siendo
    verificable por simbolo. Si esta proporcion cae, el test de arriba pasa a
    vigilar cada vez menos cosas aunque siga en verde.
    """
    por_simbolo, prosa = _clasificadas()
    total = len(por_simbolo) + len(prosa)
    assert len(por_simbolo) / total >= 0.90, (
        f"solo {len(por_simbolo)}/{total} referencias son verificables por "
        "simbolo: el manifiesto se esta llenando de citas sin identificador")

    # El piso subio de 0.65 a 0.90 en S19 y es un trinquete como el cupo: al
    # anclar por simbolo las filas que solo lo nombraban en prosa, la
    # proporcion real paso de 262/326 a 300/326, y dejar el piso en 0.65
    # habria vuelto inofensivo a este contrapeso. Contando tambien las 22
    # verificadas por mencion, la cobertura es 322/326 = 98.8 %.
    _, por_mencion, _ = _prosa_repartida()
    assert (len(por_simbolo) + len(por_mencion)) / total >= 0.98, (
        f"solo {len(por_simbolo) + len(por_mencion)}/{total} referencias son "
        "verificables (por definicion o por mencion)")


# ---------------------------------------------------------------------------
# SIS-G-03: el hueco que quedaba entre "por simbolo" y "de prosa"
# ---------------------------------------------------------------------------

def test_toda_fila_que_cita_un_identificador_lo_nombra_en_su_destino():
    """
    LA COMPROBACION QUE FALTABA, y por la que SIS-G-03 existe.

    Una fila que cita `V_MIN` y apunta a M5 no se puede verificar por la via
    de arriba -- `V_MIN` no se DEFINE en M5, se USA --, y hasta S19 caia al
    saco de prosa, donde lo unico que se miraba era que la linea no estuviera
    en blanco. Una linea con contenido EQUIVOCADO pasaba en verde, y por eso
    las dos desviaciones que S16.5 corrigio salieron por casualidad: las
    encontro el test por el OTRO motivo, porque una insercion las habia
    movido justo a un renglon vacio.

    Lo verificable sin definicion es que el destino HABLE del simbolo: que el
    bloque en el que cae la linea lo nombre. No exige transcribir nada -- que
    seria una segunda copia divergible, prohibida por CLAUDE.md -- y no tiene
    falsos positivos: si el bloque no nombra el simbolo, la referencia no
    lleva a lo que dice llevar.

    SIN CUPO, a diferencia de las de prosa. Estas no son una excepcion
    declarada: son referencias verificables. Al medirlas por primera vez
    habia 20 rotas de 64 no ancladas, entre ellas dos nombres que el codigo
    ya no tiene (`e2_volteo`, `empuje_flotacion`) y uno que apuntaba 950
    lineas lejos de su uso (`ESPACIAMIENTO_MAX_VECES_ESPESOR`).

    Y COMPRUEBA EL PARRAFO, NO EL BLOQUE. La primera version de esta guardia
    miraba el bloque entero, y un bloque de `criterios_adoptados.py` tiene
    noventa lineas: seis referencias saboteadas --- una a OTRO ARCHIVO, otra a
    2900 lineas de su uso --- pasaban con la suite en verde. Es el mismo modo
    de fallo que la guardia dice cerrar, cometido al cerrarlo.
    """
    _, _, rotas = _prosa_repartida()
    detalle = [f"md:{n_md}  {ref}  nombra {simbolos} y cae en el bloque "
               f"`{bloque}` de {rel}:{n}, que no lo menciona"
               for n_md, ref, rel, n, simbolos, bloque in rotas]
    assert not rotas, (
        f"{len(rotas)} referencias nombran un identificador y aterrizan donde "
        "no se habla de el.\nCorrige el destino en docs/manifiesto_citas.md "
        "LEYENDO la linea de llegada (no restando el desfase):\n  "
        + "\n  ".join(detalle))


def test_el_hueco_sin_identificador_solo_decrece():
    """
    El trinquete del caso (a): filas que no nombran NINGUN identificador.

    Se cuenta aparte del cupo total a proposito. Bajar el total anclando por
    USO es progreso real, pero no cierra este hueco, y un solo numero dejaria
    creer que si. Esta es la cifra que T9 quiere en cero.
    """
    sin_identificador, _, _ = _prosa_repartida()
    assert len(sin_identificador) <= MAX_REFERENCIAS_SIN_IDENTIFICADOR, (
        f"{len(sin_identificador)} referencias no nombran ningun identificador, "
        f"por encima del trinquete de {MAX_REFERENCIAS_SIN_IDENTIFICADOR}. "
        "Nombra en la fila el simbolo del que habla (entre backticks) en vez "
        "de subir el numero.")


def test_las_tres_poblaciones_suman_el_total():
    """
    Que el reparto no pierda ni duplique referencias: si `_prosa_repartida`
    dejara de ver una, el test de arriba pasaria a vigilar de menos sin que
    nada avisara. Es la guardia de la guardia.
    """
    por_simbolo, prosa = _clasificadas()
    sin_identificador, por_mencion, rotas = _prosa_repartida()
    assert len(sin_identificador) + len(por_mencion) + len(rotas) == len(prosa), (
        "el reparto de las referencias de prosa no cuadra con su total")
    assert len(por_simbolo) + len(prosa) == sum(1 for _ in _referencias())


def test_ninguna_etiqueta_declara_un_rango_imposible():
    """
    La etiqueta `[CN:170-49]` anuncia un tramo que va de la 170 a la 49.

    Origen: la notacion era un rango real y `resincronizar` reescribia el
    principio conservando el final VIEJO, de modo que CINCUENTA de las 57
    etiquetas con sufijo acabaron mintiendo sobre el tramo. Es un defecto de otra especie que los
    demas de este archivo --- no es que la referencia lleve a otro sitio, es
    que la etiqueta que el lector ve es imposible --- y por eso lleva su
    propio test. Nadie lo habia mirado nunca (SIS-G-03).
    """
    texto = MANIFIESTO.read_text(encoding="utf-8")
    imposibles = [m.group(0)
                  for m in re.finditer(r"\[([A-Za-z0-9_.]+):(\d+)(-\d+)\]", texto)
                  if int(m.group(3)[1:]) <= int(m.group(2))]
    assert not imposibles, (
        f"{len(imposibles)} etiquetas anuncian un tramo imposible (el final "
        f"por delante del principio): {imposibles[:8]}. Regeneralo con "
        "python3 -m src.normativa.manifiesto --escribir")


def test_ninguna_mencion_se_verifica_contra_el_archivo_entero():
    """
    Contrapeso de la guardia por mencion: el tramo contra el que se busca el
    simbolo tiene que estar ACOTADO. Si una referencia se validara contra el
    archivo completo, «el bloque lo menciona» pasaria a significar «el archivo
    lo menciona en alguna parte», que en constantes_normativas.py --- 3350
    lineas --- no es una comprobacion.
    """
    _, por_mencion, _ = _prosa_repartida()
    holgados = []
    for n_md, ref, rel, n, _nombrados in por_mencion:
        _, inicio, fin = _tramo_de_verificacion(rel, n)
        total = len(_codigo(rel))
        if fin - inicio + 1 > total * 0.5:
            holgados.append(f"md:{n_md} {ref}: tramo de {fin - inicio + 1} "
                            f"lineas sobre {total}")
    assert not holgados, (
        "referencias verificadas contra un tramo que es casi el archivo "
        "entero:\n  " + "\n  ".join(holgados))
