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
MAX_REFERENCIAS_DE_PROSA = 82


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


def _simbolos_citados(fila: str) -> list:
    """Identificadores entre backticks en esa fila del manifiesto."""
    simbolos = []
    for trozo in re.findall(r"`([^`]+)`", fila):
        m = re.match(r"^([A-Za-z_]\w*)", trozo.strip().lstrip("↳↻⚠~ "))
        if m and m.group(1) not in simbolos:
            simbolos.append(m.group(1))
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
    assert len(por_simbolo) / total >= 0.65, (
        f"solo {len(por_simbolo)}/{total} referencias son verificables por "
        "simbolo: el manifiesto se esta llenando de citas sin identificador")
