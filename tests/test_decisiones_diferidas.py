"""
tests/test_decisiones_diferidas.py
==================================
La guardia de `docs/decisiones_diferidas.md`, el registro unico de las
decisiones que el proyecto tomo a conciencia y no habia escrito en ningun
sitio donde un revisor las buscara.

POR QUE UN TEST Y NO SOLO UN DOCUMENTO. El plan pedia ese registro desde S14 y
en S19 se escribio; un documento que nadie verifica es una afirmacion, no un
registro. Lo que aqui se comprueba es lo unico que puede envejecer solo:

  1. que estan LAS VEINTIDOS, con la lista DERIVADA del propio informe de
     auditoria --- las fichas cuya linea `**Clasificacion**` dice «deliberado
     sin documentar» --- y no transcrita a mano. Si la auditoria nombrara una
     mas, este test lo diria; una lista copiada, no.
  2. que cada ficha trae sus CUATRO campos. Tres de cuatro es media decision:
     la que dice que se difirio y no que haria falta para cerrarlo deja al
     lector sin la unica parte accionable.
  3. que el SIMBOLO que cada ficha nombra SIGUE EXISTIENDO. Es la regla 4 de
     CLAUDE.md --- anclar por nombre de simbolo, nunca por linea --- aplicada
     al documento que la invoca. Si alguien renombra `mensaje_gui`, el
     registro se pone en rojo en vez de quedarse apuntando a un nombre muerto.

Lo que NO comprueba, dicho para que no se lea de mas: que la razon escrita sea
CIERTA. Eso no lo puede hacer un test; lo hace la revision. Lo que el test
impide es que el registro quede huerfano, incompleto o desanclado.
"""

import ast
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
REGISTRO = RAIZ / "docs" / "decisiones_diferidas.md"
AUDITORIA = RAIZ / "docs" / "auditorias" / "auditoria_sistema.md"

# Los cuatro campos, cada uno con las etiquetas que valen para el.
#
# Las dos primeras admiten un par alternativo, y no es laxitud: una ficha de
# la Parte I describe una DECISION («qué se difirió / por qué»), y una de la
# Parte III describe un PARCIAL, donde lo mismo se dice mejor como «qué está
# cerrado / qué sigue abierto». Forzar la primera redaccion sobre la segunda
# produciria un parrafo torcido para satisfacer a un test, que es la forma de
# que el registro empiece a escribirse para el test y no para el revisor.
# Los dos ultimos campos NO tienen alternativa: son los que hacen accionable
# la ficha.
CAMPOS = (
    ("**Qué se difirió:**", "**Cerrado"),
    ("**Por qué", "**Abierto"),
    ("**Qué haría falta",),
    ("**Dónde vive:**",),
)


def _ids_deliberados() -> list:
    """
    Los IDs que la auditoria de sistema clasifico «deliberado sin documentar»,
    leidos del informe. La lista NO se escribe aqui a proposito: derivarla es
    lo que hace que el registro no pueda quedarse corto en silencio.
    """
    lineas = AUDITORIA.read_text(encoding="utf-8").split("\n")
    ids = []
    for i, linea in enumerate(lineas):
        if "**Clasificacion** deliberado sin documentar" not in linea:
            continue
        for j in range(i, max(-1, i - 12), -1):
            m = re.match(r"^###\s+([A-G]-\d+)\s", lineas[j])
            if m:
                ids.append("SIS-" + m.group(1))
                break
    return ids


def _fichas() -> dict:
    """{id: cuerpo} de cada ficha `## SIS-x-nn · titulo` del registro."""
    texto = REGISTRO.read_text(encoding="utf-8")
    fichas, actual, cuerpo = {}, None, []
    for linea in texto.split("\n"):
        # TODA ficha, no solo las tituladas con un ID. Las de las Partes II y
        # IV llevan titulo en prosa («`M9.combinaciones()` prometia un
        # consumidor...») y escapaban al chequeo de los cuatro campos: una de
        # ellas, de hecho, no los tenia.
        m = re.match(r"^##\s+(.+?)\s*$", linea)
        if m and not linea.startswith("## Qué") and not linea.startswith("## Cómo"):
            if actual:
                fichas[actual] = "\n".join(cuerpo)
            titulo = m.group(1)
            # La clave es el ID cuando el titulo empieza por uno, para que
            # `test_estan_las_veintidos_...` pueda buscarlo; el titulo entero
            # cuando la ficha no lleva ID (Partes II y IV).
            con_id = re.match(r"^((?:SIS|NOR|MAT)-[A-Z0-9]+-\d+)\s", titulo)
            actual, cuerpo = (con_id.group(1) if con_id else titulo), []
            continue
        if re.match(r"^#\s", linea) and actual:
            fichas[actual] = "\n".join(cuerpo)
            actual, cuerpo = None, []
        if actual:
            cuerpo.append(linea)
    if actual:
        fichas[actual] = "\n".join(cuerpo)
    return fichas


def _simbolos_declarados() -> list:
    """(id_o_titulo, ruta, simbolo) de cada campo «Dónde vive»."""
    salida = []
    seccion = "(cabecera)"
    for linea in REGISTRO.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^##\s+(.+)$", linea)
        if m:
            seccion = m.group(1).strip()
        m = re.search(r"\*\*Dónde vive:\*\*\s+`([^`]+)`", linea)
        if m:
            ruta, _, simbolo = m.group(1).partition("::")
            salida.append((seccion, ruta, simbolo))
    return salida


def _nombres_de(ruta: Path) -> set:
    """
    Los nombres que el archivo DEFINE de verdad: funciones, clases, metodos,
    campos de dataclass, nombres de modulo y claves de los diccionarios
    grandes (`CRITERIOS`, `DATOS_SITIO`), que el registro cita una a una.

    NO recoge variables LOCALES, y la diferencia no es teorica. Con
    `ast.walk` sobre todo el arbol, un `mensaje_gui = "nada que ver"` dentro
    de cualquier metodo bastaba para que la propiedad `mensaje_gui` pudiera
    desaparecer de produccion con este test en verde. Comprobado: renombrada
    la propiedad y dejado el homonimo local, 36 passed. La afirmacion de la
    ficha SIS-B-07 --- «si alguien renombra `mensaje_gui`, el registro se
    pone en rojo» --- solo valia si nadie dejaba un homonimo detras.
    """
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
    nombres = set()

    def _definiciones(cuerpo, dentro_de_clase=False):
        for nodo in cuerpo:
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                nombres.add(nodo.name)
                # Los metodos cuentan; el interior de un metodo, no.
                if dentro_de_clase:
                    continue
                continue
            if isinstance(nodo, ast.ClassDef):
                nombres.add(nodo.name)
                _definiciones(nodo.body, dentro_de_clase=True)
                continue
            if isinstance(nodo, ast.Assign):
                for destino in nodo.targets:
                    if isinstance(destino, ast.Name):
                        nombres.add(destino.id)
            elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
                nombres.add(nodo.target.id)

    _definiciones(arbol.body)

    # Las claves de los diccionarios de NIVEL DE MODULO --- CRITERIOS,
    # DATOS_SITIO, FUNCIONES_SIN_CONSUMIDOR --- se citan fila por fila.
    for nodo in arbol.body:
        if not isinstance(nodo, (ast.Assign, ast.AnnAssign)):
            continue
        if isinstance(nodo.value, ast.Dict):
            for clave in nodo.value.keys:
                if isinstance(clave, ast.Constant) and isinstance(clave.value, str):
                    nombres.add(clave.value)
    return nombres


# ---------------------------------------------------------------------------

def test_el_registro_existe():
    assert REGISTRO.exists(), (
        "falta docs/decisiones_diferidas.md: es el «un solo lugar» que el plan "
        "pide desde S14 para las decisiones deliberadas")


def test_estan_las_veintidos_fichas_que_la_auditoria_clasifico():
    """
    La lista se deriva del informe, no se copia. Es la diferencia entre un
    registro que se queda corto en silencio y uno que lo dice.
    """
    esperados = _ids_deliberados()
    assert len(esperados) == 22, (
        f"la auditoria clasifica hoy {len(esperados)} hallazgos como "
        "«deliberado sin documentar» y el registro se escribio para 22: "
        "revisa el informe antes de tocar el registro")

    faltan = [i for i in esperados if i not in _fichas()]
    assert not faltan, (
        f"sin ficha en docs/decisiones_diferidas.md: {faltan}")


def test_cada_ficha_dice_las_cuatro_cosas():
    """
    Que se difirio, por que, que haria falta, y donde vive. Una ficha sin el
    tercero es la que mas duele: deja al lector sabiendo que hay deuda y sin
    saber como se paga.
    """
    incompletas = {}
    for clave, cuerpo in _fichas().items():
        faltan = [grupo[0] for grupo in CAMPOS
                  if not any(etq in cuerpo for etq in grupo)]
        if faltan:
            incompletas[clave] = faltan
    assert not incompletas, f"fichas incompletas: {incompletas}"


@pytest.mark.parametrize("seccion,ruta,simbolo", _simbolos_declarados())
def test_el_simbolo_que_cada_ficha_ancla_sigue_existiendo(seccion, ruta, simbolo):
    """
    Regla 4 de CLAUDE.md aplicada al documento que la invoca. Un registro que
    apunta a un nombre que ya no existe es peor que no tener registro: manda al
    revisor a buscar algo que no esta y le hace dudar de todo lo demas.
    """
    archivo = RAIZ / ruta
    assert archivo.exists(), f"{seccion}: {ruta} no existe"
    assert simbolo, f"{seccion}: la referencia no nombra ningun simbolo"
    assert simbolo in _nombres_de(archivo), (
        f"{seccion}: `{simbolo}` ya no existe en {ruta}. Si se renombro, "
        "actualiza el registro; si se retiro, la decision cambio y hay que "
        "reescribir la ficha")


def test_el_registro_no_transcribe_la_razon_dos_veces():
    """
    La razon vive donde vive el codigo; aqui se cita el simbolo. El riesgo de
    un registro asi es que alguien copie el parrafo entero y las dos copias
    diverjan --- que es NOR-MEM-01 en otro sitio.

    Lo verificable sin criterio humano es el TAMAÑO: una ficha que se alarga
    mas alla de lo que cabe en cuatro campos esta transcribiendo, no citando.
    El tope es generoso a proposito; lo que corta es el caso patologico.
    """
    largas = {c: len(b) for c, b in _fichas().items() if len(b) > 2600}
    assert not largas, (
        f"fichas demasiado largas, probablemente transcritas: {largas}. La "
        "razon va en el docstring del simbolo; aqui va la cita")
