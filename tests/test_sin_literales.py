"""
tests/test_sin_literales.py
===========================
Guardia automatica de la regla de arquitectura: ningun modulo declara valores.

Todo literal numerico bajo src/ -- incluido src/modulos/, donde aterrizan M0 a
M11 -- es un defecto, salvo en los seis archivos exentos:

    constantes_normativas.py   valores [N] con numeral verificado
    criterios_adoptados.py     valores [N->], [C], [A] y los [S] con ensayo
                               pendiente, declarados
    datos_sitio.py             valores [S] de corredor: la lectura de un mapa
                               o un ensayo sobre las coordenadas de esta obra
    tolerancias.py             precision numerica, no valores de proyecto
    dominios.py                limites de dominio del dato de entrada
    constantes_fisicas.py      constantes fisicas universales (hoy cinco
                               nombres: G, RHO_AGUA, N_POR_KN, GAMMA_AGUA,
                               GAMMA_AGUA_KN_M3), no valores de proyecto

Los tres ultimos estan exentos porque sus numeros NO son valores de proyecto.
`datos_sitio.py` esta exento por la razon contraria: los suyos si lo son -- el
PGA gobierna la cadena sismica entera -- y estan aparte porque no son
constantes universales, que es una separacion de clasificacion, no de peso.

Excepciones dentro de un modulo vigilado:

    0, 1 y 2            (y sus equivalentes float; nunca un complejo)
    indices y rebanadas x[3], x[1:5] -- pero NO una clave de tabla, ver abajo
    pi                  no es literal: es math.pi, un nombre
    lineas marcadas     con el comentario `# literal-ok: <razon>`

La ultima merece explicacion. Las formulas de la hoja de ruta traen numeros
que NO son valores de proyecto sino parte de la expresion matematica: el 8 de
A = (D^2/8)(theta - sen theta), el exponente 2/3 de Manning, el 4/3 del radio
hidraulico en el control de salida. Moverlos a constantes_normativas.py como
`OCHO = 8` no defiende nada y empeora la lectura. La marca los permite dejando
constancia visible en la revision: un literal exento es un literal declarado,
nunca un literal silencioso. Si prefieres cero valvulas de escape, borra el
soporte de la marca y esos numeros tendran que salir de un archivo exento.

Las SEIS vias de evasion que este barrido tenia (S16, cluster C09)
------------------------------------------------------------------
La auditoria de Sistema documento seis formas de meter un valor de proyecto
bajo src/ sin que este archivo lo viera, y una septima omision de alcance.
Todas estan cerradas aqui, y cada una tiene su propio test de regresion en el
bloque "El detector probandose a si mismo": si alguien reabre la puerta, cae
un test con el ID del hallazgo en el nombre.

    SIS-C-03  La marca se buscaba como SUBCADENA de la linea: valia dentro de
              un string o de un docstring. Ahora se busca con `tokenize`, como
              COMMENT token, y ademas se exige la razon (`# literal-ok: ...`
              con texto detras). Un `MARCA = "# literal-ok"` en el cuerpo de un
              modulo ya no exime nada.
    SIS-C-07  La marca en linea propia eximia todos los literales de la linea
              SIGUIENTE. Ahora vale SOLO en la linea fisica del literal. Una
              expresion partida repite la marca en cada linea que traiga un
              numero: cuesta una linea de comentario y elimina la unica via
              por la que un comentario suelto blanqueaba codigo que no leyo.
    SIS-C-04  `_nodos_de_indice` eximia TODO entero dentro de un `Subscript`,
              de modo que una clave numerica de tabla -- `CAUDAL_POR_TR[500]`,
              con el 500 en anios -- pasaba invisible. CLAUDE.md exime los
              INDICES, no las claves: un indice es una posicion en una
              secuencia, una clave de tabla es una magnitud. Se separan por el
              objeto subscrito: si es un nombre en MAYUSCULAS (una tabla
              declarada) el entero es clave y cae; en cualquier otro caso es
              indice y sigue exento.
              TAMBIEN EN EL SEGUNDO NIVEL: `TABLA[900][2500]`, el otro
              ejemplo de la ficha, se resuelve mirando la RAIZ de la cadena de
              subindices y no el nivel de arriba.
              LA HEURISTICA NO ES EXACTA, Y SE DECLARA: un indice POSICIONAL
              sobre una constante en mayusculas (`COLUMNAS[3]`) tambien cae, y
              se declara con `# literal-ok: indice posicional sobre COLUMNAS`;
              al reves, una tabla escrita en minusculas o en CamelCase se le
              escapa. Las tablas de este proyecto van en MAYUSCULAS y esa
              convencion es parte de la guardia, no un accidente.
    SIS-C-05  La lista de exentos se aplicaba por NOMBRE de archivo a
              cualquier profundidad: un `src/modulos/dominios.py` habria
              quedado exento sin que nadie lo declarara. Ahora se compara la
              RUTA RELATIVA a la raiz del barrido.
    SIS-C-08  `valor in NUMEROS_PERMITIDOS` dejaba pasar los complejos, porque
              `0j == 0` y `2+0j == 2`. Un complejo no tiene sitio en este
              calculo: cae siempre, tambien si vale 0j.
    SIS-C-09  El detector era puramente sintactico: `int("13")`, `float("4.6")`
              e `int("500")` eran invisibles. Ahora se miran las conversiones
              desde texto (`int`, `float`, `complex`, `Decimal`, `Fraction`)
              con argumento literal que parsea como numero.
    SIS-C-06  El barrido solo recorria `src/`: `cli.py` y `gui/app.py` quedaban
              sin vigilancia y ningun documento decia por que (lo mismo que
              reporta NOR-F-02). Ahora entran, con la regla estrechada de la
              capa de presentacion que se explica mas abajo.

La capa de presentacion: cli.py y gui/app.py
--------------------------------------------
Sus numeros no son valores de proyecto: son geometria de widget (padx, pady,
ancho de columna, tamaño de fuente) y formato de consola (ancho de caja,
sangria, decimales). Cambiar cualquiera de ellos no mueve ninguna magnitud
fisica -- que es exactamente el criterio con que CLAUDE.md exime a
`tolerancias.py`. Pero eximirlos EN BLOQUE haria de la GUI el mejor escondite
del repositorio, y esa es la razon por la que quedaban fuera sin declaracion.

La regla es la misma forma que ya tiene `src/normativa/`: exencion
ESTRECHADA, no exencion entera.

    * un literal ENTERO dentro de una llamada a un constructor o metodo de
      presentacion (la lista `CONSTRUCTORES_DE_PRESENTACION`) se admite;
    * un FLOAT o un COMPLEX cae SIEMPRE, este donde este. Un valor de proyecto
      -- 0.013, 4.5, 1.5, 0.75 -- es float practicamente por definicion, y un
      entero de proyecto que se colara igual tiene que estar dentro de una
      llamada a `.pack()` o a `ttk.Label()` para pasar;
    * cualquier otro literal cae salvo marca `# literal-ok: <razon>`;
    * y una CLAVE de tabla declarada no se blanquea por estar dentro de una
      llamada de presentacion -- `lbl.config(text=str(CAUDAL_POR_TR[500]))`
      seria la forma obvia de colar un entero de proyecto por este hueco.

El hueco que la regla acepta a sabiendas: un ENTERO de proyecto escrito a mano
dentro de una llamada de presentacion (`ttk.Label(text=f"D = {900} mm")`).
Se acepta porque practicamente toda magnitud de este proyecto es float, porque
la clave de tabla -- la otra forma entera de colarlo -- ya cae, y porque la
alternativa (marcar los 152 numeros de geometria de la GUI uno por uno) haria
ilegible el modulo sin defender nada mas.

Las plantillas HTML (SIS-C-11)
------------------------------
`src/plantillas/*.html` no son .py y quedaban fuera del barrido, tambien sin
declaracion. Hoy no traen ningun valor de calculo -- todas las magnitudes
entran por los marcadores `%%...%%` que rellena M11 -- y esa es la propiedad
que se vigila: fuera de los bloques `<style>`, los unicos numeros admitidos
son la NUMERACION DE SECCIONES de la memoria. Si alguien escribe un 0.75 en
una celda de la plantilla, cae `test_las_plantillas_no_traen_valores_de_calculo`.

Los asserts de subcadena (SIS-C-01, SIS-C-02)
---------------------------------------------
Veintidos asserts de la suite comprobaban el TEXTO FUENTE de un modulo en vez
de su estructura. Los de este archivo se reescribieron contra el AST, con
`tests/apoyo/estructura.py`. No es una mejora cosmetica: al portarlos se
descubrio que `test_la_tabla_del_factor_de_muro_es_normativa_y_la_eleccion_no`
llevaba tiempo VERDE SOBRE UN COMENTARIO -- `FACTOR_MURO_TABLA` se retiro de
`constantes_normativas.py` (NOR-PUE-07: el numeral no tabula dos filas) y la
cadena `FACTOR_MURO_TABLA = {` sobrevivio dentro del comentario que explica su
retirada, satisfaciendo el assert con el simbolo ya inexistente.

Lo que este barrido NO ve, dicho aqui para que no se sobreentienda
------------------------------------------------------------------
Las seis vias de evasion DOCUMENTADAS estan cerradas; el barrido no es por eso
hermetico, y conviene que quien lo lea sepa donde acaba:

  * un valor compuesto solo con los numeros permitidos: `(1 + 2*2*2) / 2` es
    4.5 y ningun literal prohibido aparece;
  * una conversion desde texto cuyo argumento sea un NOMBRE y no un literal
    (`_TR = "500"` en una linea, `int(_TR)` en otra);
  * un valor que llegue por un archivo de datos o por una variable de entorno.

Las tres exigen ofuscacion deliberada. Contra eso la guardia no es el AST: es
la revision humana, y por eso la marca `# literal-ok` existe -- para que lo
declarado se VEA -- en vez de intentar que el detector lo adivine.

El barrido esta parametrizado por directorio para poder probarse a si mismo
sobre un arbol sintetico: un test que solo recorre un directorio vacio no
prueba nada.
"""

import ast
import io
import re
import tokenize
from pathlib import Path

import pytest

from tests.apoyo import estructura

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
MODULOS = SRC / "modulos"
PLANTILLAS = SRC / "plantillas"

# Rutas RELATIVAS a la raiz del barrido, no nombres sueltos (SIS-C-05).
EXENTOS = {"constantes_normativas.py", "criterios_adoptados.py",
           "datos_sitio.py", "tolerancias.py", "dominios.py",
           "constantes_fisicas.py"}

# El registro normativo entra en la lista CON UNA CONDICION QUE LAS OTRAS SEIS
# NO TIENEN: todo literal numerico suyo tiene que estar DENTRO de un objeto de
# transcripcion -- una `FilaDeTabla`, un `Verbatim`, una `Cita`, una `Fuente`,
# un `RangoNormativo`, un `TramoDeModificador`... --, nunca como constante de
# modulo suelta. Sin esa condicion, `src/normativa/` seria el mejor escondite
# del repositorio: un paquete grande, exento entero, donde cualquier valor de
# proyecto podria colarse sin etiqueta.
#
# La comprueba `test_el_registro_normativo_no_esconde_constantes_sueltas`, mas
# abajo. La marca de literal permitido sigue valiendo, para los pocos numeros
# que no son transcripcion (una escala de renderizado, un tamaño de muestra).
PAQUETE_REGISTRO = "normativa"

# Los constructores del registro: un numero dentro de la llamada a uno de
# estos ES una transcripcion, y por eso se admite. Se listan por NOMBRE y no
# por importacion para que este test no dependa de que el paquete importe.
CONSTRUCTORES_DE_TRANSCRIPCION = {
    # el objeto documental
    "Fuente", "Cita", "Verbatim", "Verificado", "Ausencia", "Catalogo",
    "NotaAlPie", "CondicionAplicacion", "Discrepancia", "Parte", "Laguna",
    "Interpretacion", "AfirmacionNegativa", "Transcripcion", "Fundamento",
    # la tabla y sus partes
    "TablaNormativa", "ColumnaDeTabla", "FilaDeTabla", "Modificador",
    "TramoDeModificador", "CorrespondenciaDeTablas", "Acotada", "Integra",
    "Usada", "NoUsada", "PendienteDeCondicion",
    # los rangos
    "IntervaloAdmisible", "TechoUnico", "PisoUnico", "ConjuntoDeMaximos",
    "BandaDeInterpolacion",
    # la paginacion
    "Corrida", "PorCapitulo", "Irregular", "SinDeterminar",
    # las fabricas internas de cada modulo del paquete
    "_cita", "_tabla", "_d", "_ausente", "_firmado", "_fundamento",
}

# La capa de presentacion (SIS-C-06 / NOR-F-02). Los archivos, y los
# constructores y metodos cuyo interior admite un entero de geometria.
# Los .py que NO estan bajo src/ y que hasta S16 no vigilaba nadie. Los tres
# son capa de presentacion o herramienta: ninguno calcula.
CAPA_DE_PRESENTACION = ("cli.py", "gui/app.py", "verificar_sesion.py")

# `conftest.py` queda fuera Y SE DECLARA POR QUE, que es la mitad que faltaba
# en los hallazgos de esta familia. Sus numeros -- los espesores de pared de
# la corrida de pruebas, la exposicion quimica -- SI son valores de proyecto,
# y por eso no podrian ir a ningun archivo exento; lo que los legitima es que
# entran al calculo por `establecer_valor_dinamico`, el mismo camino que usan
# la GUI y la CLI, de modo que M11 los imprime en el bloque "DECLARADOS SOLO
# PARA ESTA CORRIDA" y nadie los confunde con el expediente. Vigilarlos aqui
# obligaria a marcarlos uno por uno sin defender nada: ya estan declarados,
# que es lo que la marca consigue.
FUERA_DEL_BARRIDO_DECLARADO = {
    "conftest.py",
}

# Directorios enteros fuera del barrido, cada uno CON SU RAZON escrita. Un
# directorio se declara aqui, y no archivo por archivo, porque la razon es del
# directorio.
DIRECTORIOS_FUERA_DEL_BARRIDO = {
    # Codigo HEREDADO. `legacy/Tc.py` es la GUI de referencia que CLAUDE.md
    # manda leer antes de escribir interfaz ("Reutilizar el patron de
    # legacy/Tc.py"): no lo importa ningun modulo, no entra en ninguna corrida
    # y no calcula ninguna alcantarilla. Sus literales son de OTRO programa.
    # Lo que faltaba no era vigilarlo: era que su estatus estuviera ESCRITO en
    # vez de deducirse de que nadie lo mira (SIS-B-10).
    "legacy": "codigo heredado, sin importadores ni corrida (SIS-B-10)",
    # La SUITE. Los numeros de un test son datos de prueba por definicion: el
    # caso patron, el CSV sintetico, el mutante que se inyecta. Vigilarlos
    # convertiria cada test de valor en una falta. Del arbol de tests se
    # vigila OTRA cosa, en tests/test_guardias_de_la_suite.py: que ningun
    # assert compare floats con igualdad exacta.
    "tests": "datos de prueba; su guardia es test_guardias_de_la_suite.py",
}
CONSTRUCTORES_DE_PRESENTACION = {
    # widgets de tk / ttk / ttkbootstrap
    "Frame", "LabelFrame", "Label", "Button", "Entry", "Text", "Treeview",
    "Separator", "Notebook", "Canvas", "Scrollbar", "Toplevel", "Checkbutton",
    "Combobox", "Radiobutton", "Spinbox", "Progressbar", "Menu", "Style",
    "PanedWindow", "Listbox", "Scale",
    # geometria, estilo y configuracion
    "pack", "grid", "place", "configure", "config",
    "columnconfigure", "rowconfigure",
    "grid_columnconfigure", "grid_rowconfigure",
    "minsize", "maxsize", "geometry", "wm_geometry", "resizable",
    "column", "heading", "tag_configure", "create_window", "itemconfigure",
    "yview_scroll", "xview_scroll", "yview_moveto", "xview_moveto",
    "after", "bbox",
}

NUMEROS_PERMITIDOS = {0, 1, 2}
MARCA = "# literal-ok"
# Las conversiones desde texto por las que un literal se escondia (SIS-C-09).
CONVERSORES_DESDE_TEXTO = {"int", "float", "complex", "Decimal", "Fraction"}


# ---------------------------------------------------------------------------
# El detector
# ---------------------------------------------------------------------------

def _nombre_llamado(nodo: ast.Call):
    """El nombre de lo que se llama: `f(...)` -> 'f', `a.b(...)` -> 'b'."""
    f = nodo.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def lineas_marcadas(codigo: str) -> set:
    """
    Las lineas cuya MARCA es un comentario de verdad (SIS-C-03).

    Se exige ademas la razon: `# literal-ok:` con texto detras. CLAUDE.md
    escribe la marca con razon obligatoria, y una marca sin razon es
    justamente el literal silencioso que la marca existe para evitar.
    """
    marcadas = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(codigo).readline)
        for tok in tokens:
            if tok.type != tokenize.COMMENT:
                continue
            texto = tok.string.strip()
            if not texto.startswith(MARCA + ":"):
                continue
            if not texto[len(MARCA) + 1:].strip():
                continue                   # marca sin razon: no vale
            marcadas.add(tok.start[0])
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return marcadas


def _es_tabla_declarada(nodo) -> bool:
    """
    El objeto subscrito es una TABLA declarada, no una secuencia cualquiera.

    Se reconoce por la convencion del repositorio: las tablas y constantes van
    en MAYUSCULAS (`FS`, `CAUDAL_POR_TR`, `F_PGA_TABLA`, `cn.FS`). Un entero
    dentro de un subscript sobre una de ellas es una CLAVE -- una magnitud --
    y no un indice, que es lo unico que CLAUDE.md exime.
    """
    if isinstance(nodo, ast.Name):
        base = nodo.id
    elif isinstance(nodo, ast.Attribute):
        base = nodo.attr
    else:
        return False
    letras = [c for c in base if c.isalpha()]
    return bool(letras) and all(c.isupper() for c in letras)


def _base_del_subscript(nodo):
    """
    El objeto RAIZ de una cadena de subindices: en `TABLA[900][2500]` el
    subscript exterior tiene como valor otro Subscript, no el nombre, y
    preguntar solo por el nivel de arriba dejaba escapar el 2500 --- que es
    el segundo ejemplo que la propia ficha SIS-C-04 escribe.
    """
    while isinstance(nodo, ast.Subscript):
        nodo = nodo.value
    return nodo


def _nodos_de_indice(arbol: ast.AST) -> set:
    """
    Constantes enteras que son indice o limite de rebanada: x[3], x[1:5].

    NO exime la clave de una tabla declarada: `CAUDAL_POR_TR[500]` cae
    (SIS-C-04).
    """
    exentos = set()
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Subscript):
            continue
        if _es_tabla_declarada(_base_del_subscript(nodo.value)):
            continue
        for hijo in ast.walk(nodo.slice):
            if isinstance(hijo, ast.Constant) and isinstance(hijo.value, int):
                exentos.add(id(hijo))
    return exentos


def _permitido(valor) -> bool:
    """
    0, 1 y 2, y sus equivalentes float. Un COMPLEJO nunca (SIS-C-08): `0j`
    y `2+0j` son iguales a 0 y a 2 y se colaban por la comparacion de valor.
    """
    if isinstance(valor, complex):
        return False
    return valor in NUMEROS_PERMITIDOS


def _literales_escondidos_en_texto(arbol: ast.AST):
    """
    `int("13")`, `float("4.6")`, `int("500")`: un valor de proyecto escrito
    como texto y convertido (SIS-C-09). Devuelve [(linea, texto), ...].
    """
    hallazgos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call) or not nodo.args:
            continue
        if _nombre_llamado(nodo) not in CONVERSORES_DESDE_TEXTO:
            continue
        arg = nodo.args[0]
        if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
            continue
        try:
            valor = complex(arg.value.strip())
        except ValueError:
            continue                       # no era un numero: no es un literal
        if valor.imag == 0 and _permitido(valor.real):
            continue
        hallazgos.append((nodo.lineno, arg.value))
    return hallazgos


def literales_numericos(codigo: str, nombre: str = "<memoria>"):
    """
    Todos los literales numericos, sin aplicar ninguna exencion. Sirve para
    comprobar que un archivo exento declara valores de verdad: en dominios.py
    los numeros llevan la marca de literal permitido y `literales_prohibidos`
    los dejaria pasar, con lo que el archivo pareceria vacio de valores.
    """
    arbol = ast.parse(codigo, filename=nombre)
    hallazgos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Constant):
            continue
        valor = nodo.value
        if isinstance(valor, bool) or not isinstance(valor, (int, float, complex)):
            continue                      # los strings y None no son literales numericos
        hallazgos.append((nodo.lineno, valor))
    return sorted(hallazgos)


def literales_prohibidos(codigo: str, nombre: str = "<memoria>"):
    """Devuelve [(linea, valor), ...] de los literales numericos no permitidos."""
    arbol = ast.parse(codigo, filename=nombre)
    marcadas = lineas_marcadas(codigo)
    de_indice = _nodos_de_indice(arbol)
    hallazgos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Constant):
            continue
        valor = nodo.value
        if isinstance(valor, bool) or not isinstance(valor, (int, float, complex)):
            continue
        if id(nodo) in de_indice:
            continue
        if _permitido(valor):             # 2 y 2.0 entran por igual; 2+0j no
            continue
        if nodo.lineno in marcadas:       # la marca vale en SU linea, no en la siguiente
            continue
        hallazgos.append((nodo.lineno, valor))
    for linea, texto in _literales_escondidos_en_texto(arbol):
        if linea not in marcadas:
            hallazgos.append((linea, texto))
    return sorted(hallazgos, key=lambda par: (par[0], repr(par[1])))


def _nodos_dentro_de(arbol: ast.AST, constructores: set) -> set:
    """
    Los `id()` de los nodos que caen DENTRO de la llamada a uno de esos
    constructores. Se marca el subarbol entero, no solo los argumentos
    directos: una `FilaDeTabla` lleva su `valores={...}` con los numeros
    dentro de un dict, y un `ConjuntoDeMaximos` dentro de ese dict; un
    `ttk.Label(...)` lleva su `font=("Segoe UI", 9)` dentro de una tupla.
    """
    dentro = set()
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call):
            continue
        if _nombre_llamado(nodo) not in constructores:
            continue
        for hijo in ast.walk(nodo):
            dentro.add(id(hijo))
    return dentro


def literales_fuera_de_transcripcion(codigo: str, nombre: str = "<memoria>"):
    """Literales de `src/normativa/` que no son transcripcion ni estan marcados."""
    arbol = ast.parse(codigo, filename=nombre)
    marcadas = lineas_marcadas(codigo)
    dentro = _nodos_dentro_de(arbol, CONSTRUCTORES_DE_TRANSCRIPCION)
    sueltos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Constant):
            continue
        valor = nodo.value
        if isinstance(valor, bool) or not isinstance(valor, (int, float, complex)):
            continue
        if _permitido(valor) or id(nodo) in dentro or nodo.lineno in marcadas:
            continue
        sueltos.append((nodo.lineno, valor))
    return sorted(sueltos)


def _nodos_de_argumento_directo(arbol: ast.AST, constructores: set) -> set:
    """
    Los `id()` de los literales que son ARGUMENTO DIRECTO de una llamada de
    presentacion, o elemento de una tupla o lista literal que sea argumento
    (para que `font=("Segoe UI", 9)` y `padding=(10, 0)` sigan pasando).

    NO se marca el subarbol entero, como si se hace con la transcripcion del
    registro: dentro de `etiqueta.configure(text=f"D = {int(D_m * 1000)} mm")`
    el 1000 es una conversion de unidades --- un numero que SI entra en un
    calculo --- y no geometria de widget. La exencion tiene que llegar hasta
    donde llega la geometria y no mas.
    """
    directos = set()

    def marcar(nodo):
        if isinstance(nodo, ast.Constant):
            directos.add(id(nodo))
        elif isinstance(nodo, (ast.Tuple, ast.List)):
            for elemento in nodo.elts:
                marcar(elemento)
        elif (isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, ast.USub)
              and isinstance(nodo.operand, ast.Constant)):
            directos.add(id(nodo.operand))

    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call):
            continue
        if _nombre_llamado(nodo) not in constructores:
            continue
        for argumento in list(nodo.args) + [kw.value for kw in nodo.keywords]:
            marcar(argumento)
    return directos


def literales_de_presentacion_prohibidos(codigo: str, nombre: str = "<memoria>"):
    """
    La regla estrechada de la capa de presentacion (SIS-C-06 / NOR-F-02):
    un ENTERO dentro de una llamada de presentacion pasa; un float o un
    complejo cae siempre; lo demas cae salvo marca.
    """
    arbol = ast.parse(codigo, filename=nombre)
    marcadas = lineas_marcadas(codigo)
    dentro = _nodos_de_argumento_directo(arbol, CONSTRUCTORES_DE_PRESENTACION)
    # Una clave de tabla NO se blanquea por estar dentro de una llamada de
    # presentacion: `lbl.config(text=str(CAUDAL_POR_TR[500]))` seria la forma
    # obvia de colar un entero de proyecto por este hueco (misma regla que
    # SIS-C-04, aplicada aqui tambien).
    claves_de_tabla = set()
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Subscript)
                and _es_tabla_declarada(_base_del_subscript(nodo.value))):
            for hijo in ast.walk(nodo.slice):
                if isinstance(hijo, ast.Constant) and isinstance(hijo.value, int):
                    claves_de_tabla.add(id(hijo))
    hallazgos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Constant):
            continue
        valor = nodo.value
        if isinstance(valor, bool) or not isinstance(valor, (int, float, complex)):
            continue
        if _permitido(valor):
            continue
        if not isinstance(valor, int):
            # UN FLOAT O UN COMPLEJO CAE SIEMPRE, TAMBIEN CON MARCA. La marca
            # es justo la forma en que un valor de proyecto se camuflaria
            # aqui: gui/app.py lleva 27 marcas legitimas de "ancho de columna,
            # px", y una vigesimo octava que dijera lo mismo sobre un 4.5
            # pasaria inadvertida en revision. La geometria de widget es
            # entera por construccion, de modo que no se pierde nada.
            hallazgos.append((nodo.lineno, valor))
            continue
        if nodo.lineno in marcadas:
            continue
        if id(nodo) in dentro and id(nodo) not in claves_de_tabla:
            continue                      # geometria de widget: no es magnitud
        hallazgos.append((nodo.lineno, valor))
    for linea, texto in _literales_escondidos_en_texto(arbol):
        if linea not in marcadas:
            hallazgos.append((linea, texto))
    return sorted(hallazgos, key=lambda par: (par[0], repr(par[1])))


def barrido(raiz: Path) -> dict:
    """Recorre un arbol .py y devuelve {ruta relativa: [(linea, valor), ...]}."""
    faltas = {}
    for ruta in sorted(raiz.rglob("*.py")):
        relativa = ruta.relative_to(raiz)
        if str(relativa).replace("\\", "/") in EXENTOS:
            continue                       # por RUTA, no por nombre (SIS-C-05)
        if PAQUETE_REGISTRO in relativa.parts:
            # Exento del barrido general y sujeto al suyo, mas estrecho.
            continue
        # utf-8-sig y no utf-8: un editor de Windows puede dejar BOM y el
        # interprete de Python lo acepta. El barrido tiene que leer lo mismo
        # que ejecuta el programa, o falla por sintaxis en vez de reportar.
        hallazgos = literales_prohibidos(ruta.read_text(encoding="utf-8-sig"), ruta.name)
        if hallazgos:
            faltas[str(relativa)] = hallazgos
    return faltas


def _detalle(faltas: dict) -> str:
    return "\n".join(
        f"  {archivo}: " + ", ".join(f"linea {n} -> {v!r}" for n, v in hallazgos)
        for archivo, hallazgos in faltas.items()
    )


# ---------------------------------------------------------------------------
# La guardia sobre el codigo real
# ---------------------------------------------------------------------------

def test_ningun_modulo_declara_literales_numericos():
    faltas = barrido(SRC)
    assert not faltas, (
        "Literales numericos fuera de los archivos exentos:\n" + _detalle(faltas) +
        "\n\nUn valor de proyecto va a constantes_normativas.py (si es [N] con "
        "numeral) o a criterios_adoptados.py (si es [N->], [C] o [A]). Una "
        "tolerancia va a tolerancias.py. Si es parte de una formula, marca la "
        f"linea con '{MARCA}: <razon>'."
    )


def test_el_registro_normativo_no_esconde_constantes_sueltas():
    """
    La exencion de `src/normativa/` se ESTRECHA, no se ensancha (§10.2 b del
    diseño): un numero suyo vale si es transcripcion o si esta marcado. Una
    constante de modulo suelta, no.
    """
    paquete = SRC / PAQUETE_REGISTRO
    assert paquete.is_dir(), "src/normativa/ no existe: la exencion caduco"
    faltas = {}
    for ruta in sorted(paquete.rglob("*.py")):
        sueltos = literales_fuera_de_transcripcion(
            ruta.read_text(encoding="utf-8-sig"), ruta.name)
        if sueltos:
            faltas[str(ruta.relative_to(SRC))] = sueltos
    assert not faltas, (
        "Literales numericos sueltos en src/normativa/:\n" + _detalle(faltas) +
        "\n\nEn el registro un numero vale si esta DENTRO de un objeto de "
        "transcripcion (Verbatim, Cita, Fuente, FilaDeTabla, un rango, un "
        "tramo de modificador...). Si no lo es, o va a un archivo exento o se "
        f"marca la linea con '{MARCA}: <razon>'."
    )


def test_la_capa_de_presentacion_no_declara_valores_de_proyecto():
    """
    SIS-C-06 / NOR-F-02: `cli.py` y `gui/app.py` estaban fuera del barrido sin
    que ningun documento dijera por que.

    Entran con la regla estrechada del encabezado: un entero dentro de una
    llamada de presentacion es geometria de widget y pasa; un float o un
    complejo -- la forma de casi todo valor de proyecto -- cae SIEMPRE, este
    donde este; y cualquier otro literal cae salvo marca.
    """
    faltas = {}
    for relativa in CAPA_DE_PRESENTACION:
        ruta = RAIZ / relativa
        assert ruta.is_file(), f"'{relativa}' no existe: la lista caduco"
        hallazgos = literales_de_presentacion_prohibidos(
            ruta.read_text(encoding="utf-8-sig"), ruta.name)
        if hallazgos:
            faltas[relativa] = hallazgos
    assert not faltas, (
        "Literales numericos en la capa de presentacion:\n" + _detalle(faltas) +
        "\n\nSi es geometria de widget, tiene que ir DENTRO de la llamada de "
        "presentacion (pack, grid, ttk.Label...). Si es formato de consola, "
        f"marca la linea con '{MARCA}: <razon>'. Si es un valor de proyecto, "
        "no va aqui: va a constantes_normativas.py o a criterios_adoptados.py "
        "y la capa de presentacion lo LEE."
    )


def test_ningun_py_fuera_de_src_se_queda_sin_declarar():
    """
    La forma del hallazgo SIS-C-06 -- y de NOR-F-02, y de SIS-C-11 -- no es
    "falta vigilar la GUI": es "hay archivos fuera del barrido y ningun
    documento dice por que". Este test cierra la FAMILIA entera: todo .py que
    no este bajo src/ tiene que estar, o en la lista vigilada, o en la de
    exentos CON su razon escrita al lado. Un archivo nuevo en la raiz cae aqui
    hasta que alguien decida cual de las dos cosas es.
    """
    candidatos = {
        str(ruta.relative_to(RAIZ)).replace("\\", "/")
        for ruta in RAIZ.rglob("*.py")
        if not ruta.is_relative_to(SRC)
        and not any(parte in {".git", "__pycache__", ".pytest_cache"}
                    for parte in ruta.parts)
    }
    declarados = set(CAPA_DE_PRESENTACION) | FUERA_DEL_BARRIDO_DECLARADO
    sin_declarar = {
        ruta for ruta in candidatos - declarados
        if ruta.split("/")[0] not in DIRECTORIOS_FUERA_DEL_BARRIDO
    }
    assert not sin_declarar, (
        f"archivos .py fuera de src/ que nadie vigila ni exime: "
        f"{sorted(sin_declarar)}\n\nAñadelos a CAPA_DE_PRESENTACION para "
        "vigilarlos, a FUERA_DEL_BARRIDO_DECLARADO con la razon escrita, o "
        "declara su directorio entero en DIRECTORIOS_FUERA_DEL_BARRIDO.")
    caducos = declarados - candidatos
    assert not caducos, (
        f"declarados pero inexistentes: {sorted(caducos)}: la lista caduco")
    for directorio, razon in DIRECTORIOS_FUERA_DEL_BARRIDO.items():
        assert (RAIZ / directorio).is_dir(), (
            f"'{directorio}' ya no existe: su exencion caduco")
        assert razon.strip(), f"'{directorio}' se exime sin razon escrita"


# La numeracion de secciones de la memoria: `0.`, `0-bis`, `3.1`, y los
# numeros que van detras de una de estas palabras. Todo lo demas que parezca
# numero fuera de <style> es un valor, y cae.
_PALABRAS_DE_SECCION = r"(?:secci[oó]n|Secci[oó]n|Fase|fase|Tablero|Tableros|Entregable|entregable)"


def _numeros_de_cuerpo(html: str):
    """Numeros del cuerpo de una plantilla, quitando <style> y comentarios."""
    cuerpo = re.sub(r"(?s)<style.*?</style>", "", html)
    cuerpo = re.sub(r"(?s)<!--.*?-->", "", cuerpo)
    cuerpo = re.sub(r"(?s)<h[1-6][^>]*>.*?</h[1-6]>", "", cuerpo)   # titulos
    cuerpo = re.sub(_PALABRAS_DE_SECCION + r"\s+\d+(?:\.\d+)?(?:\s*,\s*\d+)*"
                    r"(?:\s+y\s+\d+)?", "", cuerpo)
    cuerpo = re.sub(r"%%[^%]*%%", "", cuerpo)                        # marcadores
    # El signo menos entra en el patron -- un -0.75 escondido en una celda
    # es tan valor como el positivo -- pero el guion que separa palabras
    # (utf-8, 0-bis) no: por eso el lookbehind sigue excluyendo el guion
    # y el signo se admite solo cuando lo precede un espacio o el inicio.
    return re.findall(r"(?<![\w.#-])-?\d+(?:\.\d+)?", cuerpo)


def test_las_plantillas_no_traen_valores_de_calculo():
    """
    SIS-C-11: el barrido solo miraba .py y las plantillas quedaban fuera, sin
    declaracion. Toda magnitud de una memoria entra por un marcador `%%...%%`
    que rellena M11; la plantilla solo aporta rotulos y numeracion de
    secciones. Eso es lo que se vigila: un 0.75 escrito a mano en una celda
    cae aqui.
    """
    assert PLANTILLAS.is_dir(), "src/plantillas/ no existe: la regla caduco"
    plantillas = sorted(PLANTILLAS.glob("*.html"))
    assert plantillas, "no hay plantillas que vigilar: revisa la ruta"
    faltas = {}
    for ruta in plantillas:
        numeros = _numeros_de_cuerpo(ruta.read_text(encoding="utf-8"))
        if numeros:
            faltas[ruta.name] = sorted(set(numeros))
    assert not faltas, (
        f"Numeros fuera de <style> en las plantillas: {faltas}\n\n"
        "Una plantilla no declara valores: los recibe por marcador %%...%% "
        "desde M11. Si es numeracion de seccion, va en un titulo <hN> o "
        "detras de 'seccion'/'Fase'/'Tablero'/'Entregable'."
    )


def test_los_archivos_exentos_existen_y_de_verdad_llevan_literales():
    """Si alguno se renombra, la lista de exentos queda obsoleta sin avisar."""
    for nombre in EXENTOS:
        ruta = SRC / nombre
        assert ruta.is_file(), f"'{nombre}' no existe: la lista de exentos caduco"
        assert literales_numericos(ruta.read_text(encoding="utf-8-sig"), nombre), (
            f"'{nombre}' no contiene ningun literal: revisa si sigue siendo el "
            "archivo que declara valores"
        )


def test_toda_marca_declara_su_razon():
    """
    La marca sin razon es el literal silencioso que la marca existe para
    evitar. `lineas_marcadas` ya no la acepta; este test lo dice donde el
    revisor lo lee, y nombra el archivo en vez de dejar caer el barrido con
    un numero sin contexto.
    """
    sin_razon = []
    for ruta in sorted(RAIZ.rglob("*.py")):
        if any(parte in {".git", "__pycache__", "legacy"} for parte in ruta.parts):
            continue
        codigo = ruta.read_text(encoding="utf-8-sig")
        try:
            tokens = list(tokenize.generate_tokens(io.StringIO(codigo).readline))
        except (tokenize.TokenError, IndentationError, SyntaxError):
            continue
        for tok in tokens:
            if tok.type != tokenize.COMMENT:
                continue
            texto = tok.string.strip()
            if not texto.startswith(MARCA):
                continue
            if texto.startswith(MARCA + ":") and texto[len(MARCA) + 1:].strip():
                continue
            sin_razon.append(f"{ruta.relative_to(RAIZ)}:{tok.start[0]}")
    assert not sin_razon, (
        "Marcas de literal sin razon escrita: " + ", ".join(sin_razon) +
        f"\n\nLa forma es '{MARCA}: <razon>'. Sin razon la marca no exime nada."
    )


def test_los_limites_de_dominio_salieron_de_M0():
    """
    M0 los usa pero ya no los declara: si vuelven al modulo, el barrido los
    caza igual, pero este test dice donde tienen que estar.

    Reescrito contra el AST (SIS-C-02): `f"{nombre} =" in fuente` lo satisface
    igual un comentario.
    """
    m0 = SRC / "modulos" / "M0_carga.py"
    dominios = SRC / "dominios.py"
    declarados_en_dominios = estructura.nombres_asignados(dominios)
    declarados_en_m0 = estructura.nombres_asignados(m0)
    usados_en_m0 = estructura.nombres_usados(m0)
    for nombre in ("CBR_MAX_FISICO", "ESVIAJE_MAX", "S_CAUCE_MAX", "METROS_POR_KM"):
        assert nombre in declarados_en_dominios, (
            f"'{nombre}' no se declara en dominios.py")
        assert nombre not in declarados_en_m0, (
            f"'{nombre}' volvio a declararse en M0")
        assert nombre in usados_en_m0, f"M0 dejo de usar '{nombre}'"


def test_los_datos_de_sitio_salieron_de_constantes_y_criterios():
    """
    Los tres valores que se reclasificaron como [S] no pueden volver a estar
    declarados en los archivos de los que salieron: dos declaraciones del
    mismo dato es la inconsistencia Clase D/F que motivo la v5.

    Reescrito contra el AST (SIS-C-01 y SIS-C-02): la version de subcadena se
    evadia con comillas simples y la satisfacia un comentario.
    """
    constantes = SRC / "constantes_normativas.py"
    criterios = SRC / "criterios_adoptados.py"
    sitio = SRC / "datos_sitio.py"
    declarados = estructura.nombres_asignados(constantes)

    for nombre in ("ZONA_SISMICA_LA_UNION", "Z_E030"):
        assert nombre not in declarados, (
            f"'{nombre}' volvio a declararse como constante [N]: es la lectura "
            "de un mapa sobre las coordenadas de esta obra, no una constante "
            "universal")
        assert estructura.constructor_de_clave(
            sitio, "DATOS_SITIO", nombre) == "DatoSitio", (
            f"'{nombre}' no se declara en datos_sitio.py")

    assert "PERFIL_SUELO_PRESUNTO" not in declarados
    assert estructura.constructor_de_clave(
        criterios, "CRITERIOS", "PERFIL_SUELO_PRESUNTO") == "Criterio"

    assert estructura.constructor_de_clave(
        sitio, "DATOS_SITIO", "PGA_roca_B") == "DatoSitio"
    assert estructura.constructor_de_clave(
        criterios, "CRITERIOS", "PGA_roca_B") is None, (
        "el PGA no puede estar declarado a la vez como criterio y como dato "
        "de sitio")


def test_la_reduccion_del_factor_de_muro_es_normativa_y_la_eleccion_no():
    """
    El reparto valor normativo [N] / eleccion [A], el mismo que ya tenia
    F_pga: el unico factor del num. 2.8.1.1.14.2 vive en
    constantes_normativas.py y cual declaracion aplica a este cabezal es un
    criterio adoptado.

    ESTE TEST ESTABA VERDE SOBRE UN COMENTARIO. Comprobaba
    `"FACTOR_MURO_TABLA = {" in constantes`, y `FACTOR_MURO_TABLA` se habia
    retirado del modulo (NOR-PUE-07: el numeral no tabula dos filas, el 1.0 no
    es una fila sino la AUSENCIA de reduccion). La cadena sobrevivio dentro
    del comentario que explica la retirada, de modo que el assert seguia
    pasando sobre un simbolo inexistente -- el caso exacto de SIS-C-02.
    """
    constantes = SRC / "constantes_normativas.py"
    criterios = SRC / "criterios_adoptados.py"
    declarados = estructura.nombres_asignados(constantes)

    assert "REDUCCION_KH_POR_DESPLAZAMIENTO" in declarados, (
        "el unico factor normativo del numeral no esta declarado")
    assert "FACTOR_MURO_DECLARACIONES" in declarados, (
        "las dos declaraciones admisibles del criterio no estan enumeradas "
        "en constantes_normativas.py")
    assert "FACTOR_MURO_TABLA" not in declarados, (
        "'FACTOR_MURO_TABLA' volvio: el numeral no presenta tabla alguna "
        "(NOR-PUE-07)")
    assert estructura.constructor_de_clave(
        criterios, "CRITERIOS", "factor_muro_eleccion") == "Criterio"
    assert estructura.constructor_de_clave(
        criterios, "CRITERIOS", "factor_muro") is None, (
        "'factor_muro' volvio a mezclar el valor normativo con la eleccion")


def test_la_tabla_de_F_pga_es_normativa_y_la_eleccion_no():
    """El reparto tabla [N] / eleccion [A] del que sale el de arriba."""
    constantes = SRC / "constantes_normativas.py"
    criterios = SRC / "criterios_adoptados.py"
    assert "F_PGA_TABLA" in estructura.nombres_asignados(constantes)
    assert isinstance(estructura.valor_asignado(constantes, "F_PGA_TABLA"),
                      ast.Dict), "F_PGA_TABLA dejo de ser una tabla"
    assert estructura.constructor_de_clave(
        criterios, "CRITERIOS", "F_pga") == "Criterio"


def test_el_directorio_de_modulos_esta_bajo_vigilancia():
    """M0 a M11 aterrizan en src/modulos/: debe estar dentro del barrido."""
    assert MODULOS.is_dir()
    assert MODULOS.is_relative_to(SRC)


# ---------------------------------------------------------------------------
# El detector probandose a si mismo
# ---------------------------------------------------------------------------

CODIGO_CON_VALOR_DE_PROYECTO = """
def caudal(A, R, S):
    n = 0.013
    return (1 / n) * A * R ** (2 / 3) * S ** 0.5
"""

CODIGO_PERMITIDO = """
from constantes_normativas import Y_SOBRE_D_MAX
from tolerancias import TOL_UMBRAL_NORMATIVO

def cumple_borde_libre(y, D, tabla):
    referencia = tabla[3]
    del referencia
    return (y / D) <= Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO
"""

CODIGO_CON_FORMULA_MARCADA = """
import math

def area(D, theta):
    return (D ** 2 / 8) * (theta - math.sin(theta))  # literal-ok: Sec. 4.1
"""


def test_el_detector_ve_un_valor_de_proyecto():
    hallazgos = literales_prohibidos(CODIGO_CON_VALOR_DE_PROYECTO)
    valores = [v for _, v in hallazgos]
    assert 0.013 in valores, "el n de Manning tiene que caer"


def test_el_detector_deja_pasar_lo_permitido():
    assert literales_prohibidos(CODIGO_PERMITIDO) == []


def test_la_marca_exime_la_linea_de_la_formula():
    assert literales_prohibidos(CODIGO_CON_FORMULA_MARCADA) == []


def test_sin_marca_la_misma_formula_cae():
    """La exencion es de la marca, no del numero: sin declararla, el 8 cae."""
    sin_marca = CODIGO_CON_FORMULA_MARCADA.split("#")[0].rstrip() + "\n"
    assert [v for _, v in literales_prohibidos(sin_marca)] == [8]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


@pytest.mark.parametrize("codigo, esperado", [
    ("x = 0\ny = 1\nz = 2.0\n", []),                  # 0, 1, 2
    ("x = tabla[3]\n", []),                            # indice
    ("x = tabla[1:5]\n", []),                          # rebanada
    ("import math\nx = math.pi\n", []),                # pi es un nombre
    ("x = True\ny = None\nz = 'Sec. 4.1.1.3.7'\n", []),  # no son numeros
    ("x = -3.5\n", [3.5]),                             # el signo no lo salva
    ("def f(tol=1e-9):\n    return tol\n", [1e-9]),    # tolerancia sin declarar
])
def test_casos_frontera_del_detector(codigo, esperado):
    assert [v for _, v in literales_prohibidos(codigo)] == esperado


# --- Las seis vias de evasion, una por hallazgo ----------------------------

def test_sis_c_03_la_marca_dentro_de_un_string_no_exime():
    """
    La marca se buscaba como subcadena de la linea: bastaba escribirla dentro
    de un string o de un docstring para blanquear el literal de esa linea.
    """
    codigo = 'MARCA = "# literal-ok: parece una marca"; V_MAX = 4.5\n'
    assert [v for _, v in literales_prohibidos(codigo)] == [4.5]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_sis_c_03_la_marca_en_un_docstring_no_exime_su_linea():
    codigo = 'def f():\n    """# literal-ok: no es un comentario"""\n    return 4.5\n'
    assert [v for _, v in literales_prohibidos(codigo)] == [4.5]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_sis_c_07_la_marca_en_linea_propia_no_exime_la_siguiente():
    """
    La marca valia en la linea anterior 'para expresiones partidas', y eso
    permitia un comentario suelto que blanqueaba una declaracion entera.
    """
    codigo = "# literal-ok: razon que no cubre lo de abajo\nV_MAX = 4.5\n"
    assert [v for _, v in literales_prohibidos(codigo)] == [4.5]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_sis_c_07_la_marca_al_final_de_la_linea_si_exime():
    """El otro lado de la misma regla: en SU linea, la marca vale."""
    codigo = "V_MAX = 4.5  # literal-ok: razon declarada\n"
    assert literales_prohibidos(codigo) == []


def test_sis_c_04_una_clave_de_tabla_no_es_un_indice():
    """
    `_nodos_de_indice` eximia todo entero dentro de un Subscript: una clave
    numerica de tabla -- 500 anios de periodo de retorno -- pasaba invisible.
    """
    codigo = "from constantes_normativas import CAUDAL_POR_TR\nQ = CAUDAL_POR_TR[500]\n"
    assert [v for _, v in literales_prohibidos(codigo)] == [500]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_sis_c_04_la_clave_del_segundo_nivel_tampoco_es_un_indice():
    """
    `TABLA[900][2500]` es el OTRO ejemplo que la ficha SIS-C-04 escribe, y la
    primera correccion solo cazaba el 900: el subscript exterior tiene como
    valor otro Subscript, no el nombre, de modo que preguntar por el nivel de
    arriba devolvia False y eximia toda la rebanada.
    """
    codigo = "from x import TABLA\nD = TABLA[900][2500]\n"
    assert sorted(v for _, v in literales_prohibidos(codigo)) == [900, 2500]


def test_sis_c_04_el_indice_de_una_secuencia_sigue_exento():
    """CLAUDE.md exime los indices: la correccion no puede llevarselos."""
    codigo = "def f(fila):\n    return fila[3], fila[1:5]\n"
    assert literales_prohibidos(codigo) == []


def test_sis_c_05_el_exento_se_reconoce_por_ruta_y_no_por_nombre(tmp_path):
    """
    La lista se aplicaba por nombre a cualquier profundidad: un
    `src/modulos/dominios.py` habria quedado exento sin declaracion.
    """
    modulos = tmp_path / "modulos"
    modulos.mkdir()
    (modulos / "dominios.py").write_text("CBR_INVENTADO = 250\n", encoding="utf-8")
    (tmp_path / "dominios.py").write_text("CBR_MAX_FISICO = 250\n", encoding="utf-8")

    faltas = barrido(tmp_path)

    assert list(faltas) == ["modulos/dominios.py"], (
        "el exento de la raiz tiene que seguir exento y el homonimo profundo no")


def test_sis_c_08_un_complejo_nunca_esta_permitido():
    """`0j == 0` y `2+0j == 2`: la comparacion de valor los dejaba pasar."""
    valores = [v for _, v in literales_prohibidos("a = 0j\nb = 2 + 0j\n")]
    assert valores == [0j, 2j - 2j + 2] or all(isinstance(v, complex) for v in valores)
    assert len(valores) == 2, f"los dos complejos tienen que caer: {valores}"


def test_sis_c_09_un_literal_convertido_desde_texto_no_es_invisible():
    """`int("500")`, `float("4.6")`: el detector sintactico no los veia."""
    codigo = 'TR = int("500")\nV = float("4.6")\n'
    valores = [v for _, v in literales_prohibidos(codigo)]
    assert valores == ["500", "4.6"]


def test_sis_c_09_una_conversion_que_no_es_numero_no_molesta():
    """`int(texto)` y `float("no soy un numero")` no son literales."""
    codigo = 'def f(t):\n    return int(t), str(1)\n'
    assert literales_prohibidos(codigo) == []


def test_sis_c_09_la_conversion_de_un_numero_permitido_pasa():
    assert literales_prohibidos('x = int("2")\n') == []


def test_una_marca_sin_razon_no_exime():
    """CLAUDE.md escribe la marca CON razon; sin ella no declara nada."""
    assert [v for _, v in literales_prohibidos("V = 4.5  # literal-ok\n")] == [4.5]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


# --- La capa de presentacion, probandose sobre codigo sintetico ------------

def test_la_regla_de_presentacion_admite_la_geometria_del_widget():
    codigo = (
        'import tkinter.ttk as ttk\n'
        'def construir(p):\n'
        '    ttk.Label(p, text="x", wraplength=820).grid(row=0, padx=5, pady=4)\n'
    )
    assert literales_de_presentacion_prohibidos(codigo) == []


def test_la_regla_de_presentacion_rechaza_un_float_aunque_sea_geometria():
    """
    Un valor de proyecto es float practicamente por definicion: el float cae
    tambien dentro de la llamada de presentacion, que es donde se colaria.
    """
    codigo = (
        'import tkinter.ttk as ttk\n'
        'def construir(p):\n'
        '    ttk.Label(p, text="x", wraplength=0.75).pack()\n'
    )
    assert [v for _, v in literales_de_presentacion_prohibidos(codigo)] == [0.75]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_la_regla_de_presentacion_rechaza_un_entero_fuera_de_la_llamada():
    codigo = "TR_INVENTADO = 500\n"
    assert [v for _, v in literales_de_presentacion_prohibidos(codigo)] == [500]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_la_regla_de_presentacion_rechaza_una_clave_de_tabla():
    """El entero que SI podria ser magnitud: la clave de una tabla declarada."""
    codigo = (
        'from constantes_normativas import CAUDAL_POR_TR\n'
        'def pintar(lbl):\n'
        '    lbl.configure(text=str(CAUDAL_POR_TR[500]))\n'
    )
    assert [v for _, v in literales_de_presentacion_prohibidos(codigo)] == [500]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_la_regla_de_presentacion_no_deja_que_la_marca_blanquee_un_float():
    """
    El agujero que la marca abria: `V_MAX = 4.5  # literal-ok: ancho de
    columna` pasaba, y gui/app.py acababa de recibir 27 marcas legitimas que
    dicen exactamente eso. La vigesimo octava, sobre un valor de proyecto, no
    se habria distinguido en revision. Un float cae SIEMPRE, tambien marcado.
    """
    flotante = literales_de_presentacion_prohibidos(
        "V_MAX = 4.5  # literal-ok: coartada\n")
    complejo = literales_de_presentacion_prohibidos(
        "Z = 4.5j  # literal-ok: coartada\n")
    assert [v for _, v in flotante] == [4.5]   # float-exacto: el detector devuelve el mismo double
    assert [v for _, v in complejo] == [4.5j]  # float-exacto: idem, el complejo


def test_la_regla_de_presentacion_no_exime_una_conversion_de_unidades():
    """
    La exencion llega a los argumentos DIRECTOS de la llamada, que es donde
    vive la geometria. Marcar el subarbol entero eximia tambien un numero que
    SI entra en un calculo: el 1000 de una conversion m -> mm escrita dentro
    del `configure`.
    """
    codigo = ('def pintar(etiqueta, D_m):\n'
              '    etiqueta.configure(text=f"D = {int(D_m * 1000)} mm")\n')
    assert [v for _, v in literales_de_presentacion_prohibidos(codigo)] == [1000]


def test_la_regla_de_presentacion_sigue_admitiendo_la_tupla_de_una_fuente():
    """El otro lado: `font=("Segoe UI", 9)` es argumento directo y pasa."""
    codigo = ('import tkinter.ttk as ttk\n'
              'def pintar(p):\n'
              '    ttk.Label(p, font=("Segoe UI", 9), wraplength=820).grid(\n'
              '        row=0, padx=5, pady=(10, 0))\n')
    assert literales_de_presentacion_prohibidos(codigo) == []


def test_las_plantillas_no_esconden_un_valor_detras_del_signo_menos():
    """El menos no puede ser un escondite; el guion de `utf-8` no es un menos."""
    assert _numeros_de_cuerpo("<table><td>-0.75</td></table>") == ["-0.75"]
    assert _numeros_de_cuerpo('<meta charset="utf-8">') == []


def test_la_regla_de_presentacion_admite_la_marca():
    codigo = "ANCHO = 78  # literal-ok: ancho de la caja de texto de consola\n"
    assert literales_de_presentacion_prohibidos(codigo) == []


# ---------------------------------------------------------------------------
# El barrido probandose sobre un arbol sintetico
# ---------------------------------------------------------------------------

def test_el_barrido_alcanza_los_subdirectorios(tmp_path):
    """
    Prueba de recursion: si el barrido dejara de recorrer subdirectorios, el
    barrido real seguiria en verde y M0-M11 quedarian sin vigilancia.
    """
    modulos = tmp_path / "modulos"
    modulos.mkdir()
    (modulos / "M3_hidraulica.py").write_text(
        "V_MAX_INVENTADA = 4.5\n", encoding="utf-8")

    faltas = barrido(tmp_path)

    assert len(faltas) == 1
    (archivo, hallazgos), = faltas.items()
    assert archivo.endswith("M3_hidraulica.py")
    assert [v for _, v in hallazgos] == [4.5]  # float-exacto: la igualdad exacta ES lo que se prueba: el detector devuelve el mismo double que parseo del literal


def test_el_barrido_respeta_la_lista_de_exentos(tmp_path):
    (tmp_path / "criterios_adoptados.py").write_text(
        "CRITERIOS = {'F_pga': 1.0, 'HW_D_max': 1.5}\n", encoding="utf-8")
    (tmp_path / "M2_material.py").write_text(
        "HW_D_max = 1.5\n", encoding="utf-8")

    faltas = barrido(tmp_path)

    assert list(faltas) == ["M2_material.py"]
