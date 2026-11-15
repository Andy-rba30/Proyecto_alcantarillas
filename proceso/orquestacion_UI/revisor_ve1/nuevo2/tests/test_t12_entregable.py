"""
tests/test_t12_entregable.py
============================
La aceptacion de T-12 de la cadena T, «repositorio listo para la
sustentacion», en lo que toca al ENTREGABLE (la parte de proceso que T-12
movio vive en `proceso/` con sus propios tests). T-12 NO CAMBIA CALCULO: lo
que aqui se comprueba es formato, empaquetado y lo que el repositorio dice de
si mismo.

  1. La memoria en DOS VISTAS de la MISMA corrida (decision del dueño del
     2026-11-13): la RESUMIDA para imprimir (`M11.memoria_resumida_html`) y
     la COMPLETA de siempre como anexo digital. La resumida sale del mismo
     informe --las mismas huellas y la misma hora de corrida--, no tiene
     formateadores propios para los numeros y NO PUBLICA NINGUN NUMERO QUE LA
     COMPLETA NO TENGA (medido sobre el texto de las dos, en total y por
     punto, en las tres corridas de referencia y en el juego de T-11). La
     CLI escribe las dos en una invocacion (`--html` y `--html-resumida`).
  2. T11-09 (aprobado por el dueño el 2026-11-13): la fila «Control
     gobernante» de la memoria --de las dos vistas-- ya no publica como
     «salida» la aproximacion que el perfil descarto cuando su remanso no
     alcanza la entrada; dice «salida no se forma: el perfil no alcanza la
     entrada», con la MISMA regla que la CLI y el JSON, que desde T-12 vive
     en el dato (`ResultadoHidraulico.salida_no_se_forma`).

ROJO MEDIDO, NO ESCRITO PRIMERO. Se escribio con el codigo y el rojo se midio
corriendo este archivo contra el arbol base (`f77c5d4`, exportado con
`git archive`): el numero esta en el informe de la FASE A de T-12.
"""

from __future__ import annotations

import html as _html
import re
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import indice_formulas as ind
from src.modelos import ALCANCE_PERFIL
from src.modulos import M11_reporte as M11
from tests.apoyo import validacion_integral as V

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"


# ===========================================================================
# Apoyo: el texto visible de una memoria y sus numeros
# ===========================================================================

# Un numero tal como la memoria lo imprime: entero o decimal con punto, con
# signo opcional. No se parte un identificador («A-01», «V2b», un sha1): el
# numero no puede ir pegado a una letra, a un digito ni a un punto anterior.
_NUMERO = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w])")


def _texto_visible(fragmento: str) -> str:
    """Sin estilos, comentarios ni etiquetas, con las entidades resueltas."""
    sin_estilo = re.sub(r"<style.*?</style>", " ", fragmento, flags=re.S)
    sin_comentarios = re.sub(r"<!--.*?-->", " ", sin_estilo, flags=re.S)
    return _html.unescape(re.sub(r"<[^>]+>", " ", sin_comentarios))


def _numeros(fragmento: str) -> set:
    return set(_NUMERO.findall(_texto_visible(fragmento)))


def _bloque_por_id(html: str, ancla: str) -> str:
    """El `<div ... id="ancla">` de un punto hasta el siguiente punto o h2."""
    ini = html.index(f'id="{ancla}"')
    ini = html.rindex("<div", 0, ini)
    candidatos = [html.find(marca, ini + 1)
                  for marca in ('<div class="punto', "<h2", '<h3 id="')]
    fin = min(c for c in candidatos if c > 0)
    return html[ini:fin]


def _vistas(informe):
    plantilla = cli.plantilla_por_alcance(informe.alcance)
    completa = M11.memoria_html(informe, proyecto="T-12",
                                ruta_plantilla=plantilla)
    resumida = M11.memoria_resumida_html(informe, proyecto="T-12",
                                         nombre_completa="completa.html")
    return completa, resumida


@pytest.fixture(scope="module",
                params=[c.nombre for c in ind.CORRIDAS_DE_REFERENCIA] + ["juego_T11"])
def corrida(request):
    if request.param == "juego_T11":
        informe = V.correr_juego()
    else:
        referencia = next(c for c in ind.CORRIDAS_DE_REFERENCIA
                          if c.nombre == request.param)
        informe = ind.correr_referencia(referencia)
    completa, resumida = _vistas(informe)
    return request.param, informe, completa, resumida


@pytest.fixture(scope="module")
def juego():
    """El juego de T-11: A-02 y B-01 tienen la salida que no se forma."""
    return V.correr_juego()


# ===========================================================================
# 1. La memoria resumida: misma corrida, ningun numero propio
# ===========================================================================

def test_la_resumida_no_publica_ningun_numero_que_la_completa_no_tenga(corrida):
    """
    LA PROPIEDAD QUE LA DECISION DEL DUEÑO PIDE. Todo numero visible de la
    resumida esta, escrito igual, en el texto visible de la completa de la
    MISMA corrida. Se mide sobre las tres corridas de referencia del indice
    de formulas (perfil, expediente con cabezal, hidrologia calculada) y
    sobre el juego de la validacion integral de T-11.
    """
    nombre, _informe, completa, resumida = corrida
    sobran = _numeros(resumida) - _numeros(completa)
    assert not sobran, (nombre, sorted(sobran))
    # Y no es vacuo: la resumida publica numeros (los del cuadro, los HW...).
    assert len(_numeros(resumida)) > 20, nombre


def test_cada_punto_de_la_resumida_publica_solo_numeros_de_su_bloque_completo(corrida):
    """
    La misma propiedad, POR PUNTO: los numeros del bloque de un punto en la
    resumida estan en el bloque de ESE punto en la completa, salvo los de la
    tabla de criterios [A], cuyo valor y ventana la completa imprime en su
    anexo A.4 (una vez para todo el proyecto), que entra en el universo.
    """
    nombre, informe, completa, resumida = corrida
    anexo = completa[completa.index(M11.TITULO_ANEXO_SENSIBILIDAD):] \
        if M11.TITULO_ANEXO_SENSIBILIDAD in completa else ""
    for p in informe.puntos:
        ancla = M11.ancla_de_punto(p.punto.id)
        del_resumen = _bloque_por_id(resumida, M11.PREFIJO_ANCLA_RESUMEN + ancla)
        del_completo = _bloque_por_id(completa, ancla)
        sobran = _numeros(del_resumen) - _numeros(del_completo) - _numeros(anexo)
        assert not sobran, (nombre, p.punto.id, sorted(sobran))


def test_las_dos_vistas_llevan_el_mismo_encabezado_de_trazabilidad(corrida):
    """
    «Las dos de la MISMA corrida»: la resumida imprime las huellas del CSV,
    de los criterios y de la hoja de ruta, y la hora de la corrida, que son
    las del `ContextoCorrida` del informe y las mismas de la completa.
    """
    nombre, informe, completa, resumida = corrida
    contexto = cli.ContextoCorrida.de(informe)
    for huella in (contexto.csv_sha1, contexto.criterios_sha1, informe.generado):
        assert huella in resumida and huella in completa, (nombre, huella)
    traza = M11.trazabilidad(Path(informe.csv), contexto,
                             generado_utc=informe.generado)
    assert traza.hoja_ruta_sha1 in resumida and traza.hoja_ruta_sha1 in completa


def test_la_resumida_lleva_por_punto_veredictos_avisos_bloqueos_y_criterios(corrida):
    """
    Lo que la decision del dueño enumera, por punto: resultado, veredictos,
    avisos, criterios adoptados y pendientes. Cada verificacion publicada,
    cada aviso de `InformePunto.avisos()` y cada bloqueo del punto estan en
    su bloque de la resumida.
    """
    nombre, informe, _completa, resumida = corrida
    por_punto = M11.criterios_A_por_punto(informe)
    for p in informe.puntos:
        bloque = _bloque_por_id(
            resumida, M11.PREFIJO_ANCLA_RESUMEN + M11.ancla_de_punto(p.punto.id))
        for _fase, v in M11.verificaciones_publicadas(p):
            assert M11._marca_de_verificacion(v) in bloque, (nombre, p.punto.id)
        for aviso in p.avisos():
            assert M11._esc(aviso) in bloque, (nombre, p.punto.id, aviso[:60])
        for b in p.bloqueos:
            assert M11._esc(b.etapa) in bloque, (nombre, p.punto.id, b.etapa)
        for clave, puntos in por_punto.items():
            if p.punto.id in puntos:
                assert f"<code>{clave}</code>" in bloque, (nombre, clave)
    for c in M11.criterios_bloqueantes(informe):
        assert f"<code>{c.clave}</code>" in resumida, (nombre, c.clave)


def test_la_resumida_es_mas_corta_que_la_completa(corrida):
    """Es la vista para imprimir: medido, entre un 5 y un 20 % de la completa."""
    nombre, _informe, completa, resumida = corrida
    assert len(resumida) < len(completa) / 3, (nombre, len(resumida), len(completa))


def test_la_plantilla_resumida_pide_exactamente_los_marcadores_del_contrato():
    plantilla = M11.cargar_plantilla(M11.DIR_PLANTILLAS / M11.NOMBRE_PLANTILLA_RESUMIDA)
    pedidos = {m.group("named") or m.group("braced")
               for m in plantilla.pattern.finditer(plantilla.template)}
    assert pedidos == set(M11.MARCADORES_RESUMIDA)


def test_la_resumida_no_enlaza_a_anclas_que_no_tiene(corrida):
    """La remision al bloque 0-bis se queda en la completa: aqui no hay ese bloque."""
    nombre, _informe, _completa, resumida = corrida
    ids = set(re.findall(r'id="([^"]+)"', resumida))
    rotos = {h for h in re.findall(r'href="#([^"]+)"', resumida) if h not in ids}
    assert not rotos, (nombre, sorted(rotos))


def test_la_cli_escribe_las_dos_vistas_de_una_corrida(tmp_path):
    """
    `--html` y `--html-resumida` en la MISMA invocacion: la resumida nombra el
    archivo de la completa y lleva su mismo encabezado de trazabilidad.
    """
    completa, resumida = tmp_path / "completa.html", tmp_path / "resumida.html"
    hecho = subprocess.run(
        [sys.executable, "cli.py", str(CSV_EJEMPLO), "--luz", "2.75",
         "--alcance", "expediente", "--datos-externos", str(EXTERNOS_AMPLIADOS),
         "--json", str(tmp_path / "informe.json"), "--html", str(completa),
         "--html-resumida", str(resumida)],
        cwd=RAIZ, capture_output=True, text=True)
    assert hecho.returncode in (0, 1), hecho.stderr
    assert "Memoria resumida (HTML)" in hecho.stdout
    texto_c = completa.read_text(encoding="utf-8")
    texto_r = resumida.read_text(encoding="utf-8")
    assert "<code>completa.html</code>" in texto_r
    utc = re.search(r"corrida UTC: ([^)]+)\)", texto_c).group(1).strip()
    assert f"corrida UTC: {utc}" in texto_r
    for etiqueta in ("SHA-1 del CSV de entrada", "SHA-1 de criterios_adoptados.py"):
        patron = re.escape(etiqueta) + r'</th>\s*<td class="mono">([0-9a-f]{40})'
        assert re.search(patron, texto_c).group(1) == re.search(patron, texto_r).group(1)
    assert not (_numeros(texto_r) - _numeros(texto_c))


# ===========================================================================
# 2. T11-09: «salida no se forma» tambien en la memoria
# ===========================================================================

def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


def test_la_regla_vive_en_el_dato_y_la_cli_la_delega(juego):
    """
    La condicion de `cli.salida_no_se_forma` (T-11, H9) es desde T-12 una
    propiedad del dato, la MISMA en que `PerfilLamina.HW_efectivo_m` es None.
    """
    vistos = set()
    for p in juego.puntos:
        if not p.dimensionado:
            continue
        h = p.resultado.resultado_hidraulico
        assert h.salida_no_se_forma is cli.salida_no_se_forma(h)
        assert h.salida_no_se_forma is (h.perfil is not None
                                        and h.perfil.HW_efectivo_m is None)
        vistos.add(h.salida_no_se_forma)
    assert vistos == {True, False}, "el juego tiene que ejercitar los dos casos"


def test_la_fila_control_gobernante_dice_que_la_salida_no_se_forma(juego):
    """
    A-02 y B-01 del juego de T-11: la fila «Control gobernante» de la
    memoria COMPLETA y de la RESUMIDA dice «salida no se forma: el perfil no
    alcanza la entrada» --la redaccion de la linea «Control» de la CLI-- y no
    imprime la aproximacion descartada como «salida X». La aproximacion sigue
    impresa en la fila del perfil, rotulada HW_aprox. A-01 (la aproximacion
    se usa) y C-01 (el remanso alcanza la entrada) siguen con su numero.
    """
    completa, resumida = _vistas(juego)
    for id_punto in ("A-02", "B-01"):
        p = _punto(juego, id_punto)
        h = p.resultado.resultado_hidraulico
        assert h.salida_no_se_forma
        celda = M11._celda_control_gobernante(h)
        assert M11.SALIDA_NO_SE_FORMA in celda
        assert f"salida {M11._num(h.HW_salida)}" not in celda
        for vista in (completa, resumida):
            assert celda in vista, id_punto
        # El HW que gobierna y el de entrada no se tocan.
        assert f"HW = {M11._num(h.HW)} m (entrada {M11._num(h.HW_entrada)}" in celda
        linea_cli = next(l for l in cli._lineas_punto(p) if "Control  :" in l)
        assert M11.SALIDA_NO_SE_FORMA.split(": ", 1)[1] in linea_cli
        # La aproximacion descartada sigue rotulada como tal en el perfil.
        assert (f"HW<sub>aprox</sub> = {M11._num(h.perfil.HW_aproximado_m)} m"
                in _bloque_por_id(completa, M11.ancla_de_punto(id_punto)))
    for id_punto in ("A-01", "C-01"):
        h = _punto(juego, id_punto).resultado.resultado_hidraulico
        assert not h.salida_no_se_forma
        celda = M11._celda_control_gobernante(h)
        assert f"salida {M11._num(h.HW_salida)})" in celda
        assert M11.SALIDA_NO_SE_FORMA not in celda


def test_T11_09_no_mueve_ningun_numero_del_punto(juego):
    """
    Es formato: el cuadro resumen (HW que gobierna, control, seccion,
    material) es el mismo con y sin la regla; lo unico que la fila deja de
    imprimir es el numero DESCARTADO, que sigue en la fila del perfil.
    """
    for id_punto in ("A-02", "B-01"):
        p = _punto(juego, id_punto)
        h = p.resultado.resultado_hidraulico
        fila = M11.fila_resumen(p)
        assert M11._num(h.HW, M11.FMT_2) in fila
        assert h.control_gobernante.value in fila
        # El JSON y la memoria dicen lo mismo de la salida.
        d = next(x for x in cli.informe_json(juego)["puntos"] if x["id"] == id_punto)
        assert d["diseno"]["HW_salida_m"] is None


def test_una_corrida_de_perfil_tambien_lo_dice(tmp_path):
    """
    La corrida ancha de la linea base (perfil, entradas ampliadas): A-02 es
    el punto donde la salida no se forma, y su memoria lo dice.
    """
    externos = cli.cargar_datos_externos(EXTERNOS_AMPLIADOS, {"luz_m": 2.75})
    informe = cli.correr(CSV_EJEMPLO, externos, alcance=ALCANCE_PERFIL)
    p = _punto(informe, "A-02")
    assert p.resultado.resultado_hidraulico.salida_no_se_forma
    completa, resumida = _vistas(informe)
    for vista in (completa, resumida):
        assert M11.SALIDA_NO_SE_FORMA in vista


# ===========================================================================
# 1-bis. Las puertas de la resumida, una por una
# ===========================================================================

def test_resumen_de_punto_es_el_bloque_que_la_memoria_resumida_imprime(corrida):
    """`resumen_de_punto` es la pieza: la memoria resumida es su concatenacion."""
    _nombre, informe, _completa, resumida = corrida
    contexto = cli.ContextoCorrida.de(informe)
    por_punto = M11.criterios_A_por_punto(informe)
    for p in informe.puntos:
        assert M11.resumen_de_punto(p, por_punto, contexto) in resumida


def test_pendientes_resumidos_lista_cada_criterio_bloqueante_y_si_detiene(corrida):
    _nombre, informe, _completa, resumida = corrida
    tabla = M11.pendientes_resumidos(informe)
    assert tabla in resumida
    for c in M11.criterios_bloqueantes(informe):
        fila = tabla[tabla.index(f"<code>{c.clave}</code>"):]
        fila = fila[:fila.index("</tr>")]
        assert ("diferido por alcance" in fila) is c.diferido


def test_exportar_html_resumida_es_atomica_y_escribe_la_vista(tmp_path):
    informe = V.correr_juego()
    destino = tmp_path / "sub" / "resumida.html"
    ruta = M11.exportar_html_resumida(informe, destino, proyecto="T-12",
                                      nombre_completa="completa.html")
    assert ruta == destino and destino.read_text(encoding="utf-8") == \
        M11.memoria_resumida_html(informe, proyecto="T-12",
                                  nombre_completa="completa.html")
    assert not list(destino.parent.glob("*.parcial"))


def test_exportar_pdf_resumida_tiene_la_via_del_navegador(tmp_path):
    """Sin weasyprint (o forzada) deja el HTML de la resumida para Ctrl+P."""
    informe = V.correr_juego()
    salida = M11.exportar_pdf_resumida(informe, tmp_path / "resumida.pdf",
                                       abrir_navegador=False,
                                       forzar_navegador=True, proyecto="T-12")
    assert salida.via == M11.VIA_NAVEGADOR
    assert salida.ruta == tmp_path / "resumida.html"
    assert M11.TITULO_RESUMEN_VERIFICACIONES in salida.ruta.read_text(encoding="utf-8")


# ===========================================================================
# 3. Los fixtures dicen que lo son (punto 3 de T-12, INF-5.2.4)
# ===========================================================================

LINEA_BASE = RAIZ / "tests" / "linea_base_familia_c"
ROTULO_FIXTURE = "FIXTURE DE PRUEBA, NO ES UN RESULTADO DEL PROYECTO"


@pytest.mark.parametrize("nombre", sorted(p.name for p in LINEA_BASE.glob("*.html")))
def test_cada_memoria_de_la_linea_base_lleva_la_advertencia_visible(nombre):
    """
    Visible AL ABRIRLA: el rotulo esta en el texto visible del documento
    --no en un comentario-- antes que cualquier otro contenido, y en el
    `<title>` cuando la memoria lo tiene.
    """
    from tests.apoyo import rotulo_fixture as R
    texto = (LINEA_BASE / nombre).read_text(encoding="utf-8")
    visible = " ".join(_texto_visible(texto).split())
    assert R.ROTULO == ROTULO_FIXTURE
    if "<title>" in texto:
        assert f"<title>{ROTULO_FIXTURE} - " in texto
        cuerpo = texto[texto.index("<body>"):]
        assert _texto_visible(cuerpo).split()[:len(ROTULO_FIXTURE.split())] == \
            ROTULO_FIXTURE.split()
    else:
        assert texto.startswith(R.BLOQUE)
    assert ROTULO_FIXTURE in visible


def test_la_advertencia_la_pone_el_generador_y_no_el_programa():
    """
    Ninguna memoria que el programa escriba lleva el rotulo: lo pone
    `regenerar.sh` con el envoltorio declarado, y sale de la plantilla y de
    M11 solo si alguien lo mete donde no va.
    """
    script = (LINEA_BASE / "regenerar.sh").read_text(encoding="utf-8")
    assert "python3 -m tests.apoyo.rotulo_fixture" in script
    for fuente in (RAIZ / "src" / "modulos" / "M11_reporte.py", RAIZ / "cli.py",
                   *sorted((RAIZ / "src" / "plantillas").glob("*.html"))):
        assert ROTULO_FIXTURE not in fuente.read_text(encoding="utf-8"), fuente.name


@pytest.mark.parametrize("ruta", [
    RAIZ / "tests" / "fixtures" / "datos_referenciales_prueba.md",
    RAIZ / "tests" / "fixtures" / "datos_referenciales_prueba.NO_APLICADOS.md"])
def test_los_datos_referenciales_de_prueba_empiezan_por_la_advertencia(ruta):
    primera = ruta.read_text(encoding="utf-8").split("\n", 1)[0]
    assert primera.startswith(f"> **{ROTULO_FIXTURE}.**")


def test_las_entradas_ampliadas_llevan_su_advertencia_y_el_cargador_no_la_lee(tmp_path):
    import json
    from src import servicio
    from src.modelos import DatoInvalidoError
    datos = json.loads((LINEA_BASE / "entradas_ampliadas.json").read_text(encoding="utf-8"))
    assert next(iter(datos)) == servicio.CLAVE_ADVERTENCIA_EXTERNOS
    assert datos[servicio.CLAVE_ADVERTENCIA_EXTERNOS].startswith(ROTULO_FIXTURE)
    con = servicio.cargar_datos_externos(LINEA_BASE / "entradas_ampliadas.json",
                                         {"luz_m": 2.75})
    sin_ella = tmp_path / "sin.json"
    del datos[servicio.CLAVE_ADVERTENCIA_EXTERNOS]
    sin_ella.write_text(json.dumps(datos), encoding="utf-8")
    sin = servicio.cargar_datos_externos(sin_ella, {"luz_m": 2.75})
    assert con.globales.keys() == sin.globales.keys()
    for id_punto in ("C-01", "B-01"):
        for clave in ("TW_m", "Q_m3s", "S_conducto", "S_cauce"):
            assert con.valor(id_punto, clave) == sin.valor(id_punto, clave)
    # Una advertencia que no es texto, o cualquier otra seccion, se rechaza.
    malo = tmp_path / "malo.json"
    for crudo in ({servicio.CLAVE_ADVERTENCIA_EXTERNOS: 3}, {"_nota": "x"}):
        malo.write_text(json.dumps(crudo), encoding="utf-8")
        with pytest.raises(DatoInvalidoError):
            servicio.cargar_datos_externos(malo, {})


def test_la_resumida_de_la_linea_base_no_publica_numeros_que_su_completa_no_tenga():
    """Sobre los dos archivos COMPROMETIDOS de la corrida 4 (expediente)."""
    completa = (LINEA_BASE / "memoria_expediente.html").read_text(encoding="utf-8")
    resumida = (LINEA_BASE / "memoria_resumida_expediente.html").read_text(encoding="utf-8")
    assert not (_numeros(resumida) - _numeros(completa))
    assert "<code>memoria_exp.html</code>" in resumida


# ===========================================================================
# 4. El material de proceso fuera del entregable (punto 2, INF-5.2.2)
# ===========================================================================

PROCESO = RAIZ / "proceso"


def test_el_material_de_proceso_ya_no_esta_en_el_entregable():
    """
    Lo que T-12 movio a `proceso/` ya no esta en su sitio anterior (movido,
    no copiado). Lo que hay DENTRO de `proceso/` lo comprueba la suite de
    proceso (`proceso/tests/test_t12_proceso.py`): este archivo no lee
    `proceso/`, porque una exportacion del entregable no lo lleva.
    """
    for antes in (RAIZ / ".claude" / "agents", RAIZ / "docs" / "planes_mejora",
                  RAIZ / "docs" / "auditorias", RAIZ / "verificar_sesion.py",
                  RAIZ / "docs" / "hoja_de_ruta_correcciones_v12.md",
                  RAIZ / "docs" / "auditoria_y_ruta_despliegue_v9.md",
                  RAIZ / "tests" / "apoyo" / "tracker.py",
                  RAIZ / "tests" / "test_ext11_cruce_temarios.py"):
        assert not antes.exists(), antes


def test_la_suite_del_entregable_es_tests_y_no_recoge_proceso():
    import tomllib
    config = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    assert config["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]


def test_ningun_test_del_entregable_lee_material_de_proceso():
    """
    La regla del censo de T-12: lo que un test del ENTREGABLE necesita se
    queda donde esta; lo que lee material de proceso se fue con el. Ningun
    archivo de `tests/` importa de `proceso` ni construye una ruta a el (se
    mira el AST: las cadenas que no son docstring). Este archivo se exime:
    es el que comprueba la separacion.
    """
    import ast as _ast
    culpables = []
    for ruta in sorted((RAIZ / "tests").rglob("*.py")):
        if ruta.name == Path(__file__).name:
            continue
        arbol = _ast.parse(ruta.read_text(encoding="utf-8"))
        docstrings = {id(n.body[0].value) for n in _ast.walk(arbol)
                      if isinstance(n, (_ast.Module, _ast.FunctionDef,
                                        _ast.ClassDef, _ast.AsyncFunctionDef))
                      and n.body and isinstance(n.body[0], _ast.Expr)
                      and isinstance(n.body[0].value, _ast.Constant)}
        for nodo in _ast.walk(arbol):
            if isinstance(nodo, (_ast.Import, _ast.ImportFrom)):
                modulos = ([a.name for a in nodo.names] if isinstance(nodo, _ast.Import)
                           else [nodo.module or ""])
                if any(m == "proceso" or m.startswith("proceso.") for m in modulos):
                    culpables.append(f"{ruta.name}: importa {modulos}")
            elif (isinstance(nodo, _ast.Constant) and isinstance(nodo.value, str)
                  and id(nodo) not in docstrings
                  # Una RUTA dentro de `proceso/`; el prefijo solo, con el que
                  # `test_decisiones_diferidas` EXCLUYE los anclajes de
                  # proceso, no lee nada.
                  and ((nodo.value.startswith("proceso/")
                        and nodo.value != "proceso/")
                       or "planes_mejora" in nodo.value
                       or "matriz_cruzada" in nodo.value
                       or "verificar_sesion" in nodo.value)):
                culpables.append(f"{ruta.name}: {nodo.value!r}")
            elif (isinstance(nodo, _ast.BinOp) and isinstance(nodo.op, _ast.Div)
                  and isinstance(nodo.right, _ast.Constant)
                  and nodo.right.value in ("proceso", "auditorias", "planes_mejora")):
                # `RAIZ / "proceso"`, `... / "auditorias"`: una ruta construida.
                culpables.append(f"{ruta.name}: / {nodo.right.value!r}")
    assert not culpables, culpables


def test_git_archive_deja_fuera_el_material_de_proceso():
    """`.gitattributes` marca `proceso/` como export-ignore."""
    import shutil
    git = shutil.which("git")
    if git is None or not (RAIZ / ".git").exists():
        pytest.skip("sin git o fuera de un checkout")
    for ruta, esperado in (("proceso/verificar_sesion.py", "set"),
                           ("proceso/tests/conftest.py", "set"),
                           ("src/servicio.py", "unspecified")):
        salida = subprocess.run([git, "check-attr", "export-ignore", ruta], cwd=RAIZ,
                                capture_output=True, text=True, check=True).stdout
        assert salida.strip().endswith(esperado), salida


def test_claude_md_conserva_las_reglas_tecnicas_y_remite_a_la_bitacora():
    """
    La bitacora de conteos e incidentes salio ENTERA (sin resumir ni
    reescribir; lo comprueba la suite de proceso contra `f77c5d4`) y la
    constitucion lleva solo reglas tecnicas mas el puntero.
    """
    constitucion = (RAIZ / "CLAUDE.md").read_text(encoding="utf-8")
    for regla in ("## Taxonomía de etiquetas", "## Arquitectura", "## Excepciones (taxonomía)",
                  "## Unidades", "## Tests", "## Dónde están los PDF de normas",
                  "## Material de proceso"):
        assert regla in constitucion, regla
    assert "## Cierre de tarea" not in constitucion
    assert "## Reglas de corrección de hallazgos de auditoría" not in constitucion
    for archivo in ("proceso/bitacora_conteos_y_entorno.md",
                    "proceso/reglas_de_correccion_de_auditorias.md"):
        assert archivo in constitucion, archivo


# ===========================================================================
# 5. Licencia, pyproject y README (punto 4, INF-5.2.7)
# ===========================================================================

_CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def test_la_licencia_reserva_los_derechos_y_no_licencia_las_normas():
    texto = (RAIZ / "LICENSE").read_text(encoding="utf-8")
    assert "TODOS LOS DERECHOS RESERVADOS" in texto
    assert "Andy-rba30" in texto and "caratula" in texto
    assert "NO SON DEL AUTOR NI SE LICENCIAN" in texto
    assert "MIT" in texto and "posterior a la sustentacion" in texto


@pytest.mark.parametrize("nombre", ["LICENSE", "pyproject.toml", "README.md"])
def test_ningun_archivo_del_entregable_escribe_un_correo(nombre):
    texto = (RAIZ / nombre).read_text(encoding="utf-8")
    assert not _CORREO.findall(texto), nombre


def _pines(ruta: Path) -> dict:
    pines = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.split("#", 1)[0].strip()
        if linea:
            nombre = re.split(r"[=<>]", linea, maxsplit=1)[0].strip()
            pines[nombre.lower()] = linea.replace(" ", "")
    return pines


def test_pyproject_fija_las_mismas_versiones_que_requirements():
    """
    Ninguna dependencia nueva y ninguna version distinta: pyproject declara
    las de `requirements.txt` y `requirements-dev.txt`, repartidas en
    obligatorias y opcionales. Sin `[build-system]`: no se instala como
    paquete.
    """
    import tomllib
    config = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    proyecto = config["project"]
    declaradas = list(proyecto["dependencies"])
    for extra in proyecto["optional-dependencies"].values():
        declaradas.extend(extra)
    en_pyproject = {re.split(r"[=<>]", d, maxsplit=1)[0].strip().lower(): d.replace(" ", "")
                    for d in declaradas}
    en_requirements = {**_pines(RAIZ / "requirements.txt"),
                       **_pines(RAIZ / "requirements-dev.txt")}
    assert en_pyproject == en_requirements
    assert set(proyecto["dependencies"]) == {_pines(RAIZ / "requirements.txt")[n]
                                             for n in ("numpy", "scipy")}
    assert "build-system" not in config
    assert proyecto["authors"] == [{"name": "Andy-rba30"}]
    assert proyecto["license"] == {"file": "LICENSE"}


def test_el_readme_de_usuario_dice_instalacion_entradas_corrida_y_salidas():
    from src.modelos import ALCANCE_DECLARADO
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    for seccion in ("## 1. Instalación", "## 2. Los PDF de las normas", "## 3. Entradas",
                    "## 4. Corrida", "## 5. Salidas", "## 6. Alcance",
                    "## 8. Trabajo posterior", "## 9. Licencia"):
        assert seccion in readme, seccion
    for remision in ("docs/contrato_entradas.md", "docs/guia_perfil.md", "NORMAS_DIR",
                     "PRIVADO", "--html-resumida", "proceso/README.md"):
        assert remision in readme, remision
    # El alcance declarado: cada entrada de `modelos.ALCANCE_DECLARADO` por su ficha.
    for alcance in ALCANCE_DECLARADO:
        assert f"ficha {alcance.ficha}" in readme, alcance.ficha
    # Lo que queda para despues de la cadena, aprobado por el dueño.
    for posterior in ("Figuras 3.3 y 3.4 de HEC-14", "max(V_c, V_erosion)",
                      "cuencas de prueba coherente", "T11-03", "n_manning_cajon"):
        assert posterior in readme, posterior


# ===========================================================================
# 6. El entregable se sostiene solo: su suite pasa sobre una EXPORTACION
#    (H1 de la auditoria de T-12)
# ===========================================================================
# Una exportacion (`git archive HEAD`, la descarga ZIP de GitHub) no lleva
# `proceso/` (`.gitattributes`) ni `.git`. El auditor de T-12 corrio la suite
# entera sobre una y midio 2 failed: la exencion de `proceso` en
# `test_sin_literales` caducaba, y el arnes de mutacion exigia `.git`. Aqui
# se fija la propiedad de dos maneras: un censo ESTATICO de lo que necesita
# git (barato, en cada corrida) y la corrida de esos tests SOBRE una
# exportacion emulada del arbol de trabajo (en subproceso, `lento`).

# Los archivos de `tests/` que invocan git, y por que pueden hacerlo: cada
# test que los usa se salta sin `.git`, diciendolo.
REQUIEREN_GIT = {
    "tests/apoyo/mutacion.py": "copia el arbol con `git ls-files`; su unico "
                               "consumidor en subproceso, el arnes de "
                               "`test_ext11_mutacion`, se salta sin .git",
    "tests/test_ext6_registro_normativo.py": "lo versionado (`git ls-files`): "
                                             "se salta fuera de un checkout",
    "tests/test_t12_entregable.py": "`git check-attr` y la exportacion "
                                    "emulada: se saltan fuera de un checkout",
}
# Los tests que una exportacion SALTA (o en los que la exencion de `proceso`
# deja de aplicar), y que la emulacion de abajo corre.
EN_LA_EXPORTACION = (
    "tests/test_sin_literales.py::test_ningun_py_fuera_de_src_se_queda_sin_declarar",
    "tests/test_ext11_mutacion.py::test_el_arnes_mata_de_verdad_un_mutante_conocido",
    "tests/test_ext6_registro_normativo.py::test_la_app_no_versiona_ningun_PDF_de_normas",
    "tests/test_t12_entregable.py::test_git_archive_deja_fuera_el_material_de_proceso",
    "tests/test_t12_entregable.py::test_ningun_test_del_entregable_lee_material_de_proceso",
    "tests/test_decisiones_diferidas.py",
)


def _invoca_git(ruta: Path) -> bool:
    import ast as _ast
    arbol = _ast.parse(ruta.read_text(encoding="utf-8"))
    return any(isinstance(n, _ast.Constant) and n.value == "git"
               for n in _ast.walk(arbol))


def test_solo_los_censados_invocan_git_y_sus_tests_se_saltan_sin_el():
    invocan = {str(r.relative_to(RAIZ)).replace("\\", "/")
               for r in (RAIZ / "tests").rglob("*.py") if _invoca_git(r)}
    assert invocan == set(REQUIEREN_GIT), sorted(invocan ^ set(REQUIEREN_GIT))
    import ast as _ast
    arnes = _ast.parse((RAIZ / "tests" / "test_ext11_mutacion.py").read_text(
        encoding="utf-8"))
    funcion = next(n for n in _ast.walk(arnes) if isinstance(n, _ast.FunctionDef)
                   and n.name == "test_el_arnes_mata_de_verdad_un_mutante_conocido")
    assert any(isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)
               and n.func.attr == "skip" and n.args
               and isinstance(n.args[0], _ast.Name) and n.args[0].id == "MOTIVO_SIN_GIT"
               for n in _ast.walk(funcion))
    for nombre in ("test_ext6_registro_normativo.py", "test_t12_entregable.py"):
        constantes = {n.value for n in _ast.walk(_ast.parse(
            (RAIZ / "tests" / nombre).read_text(encoding="utf-8")))
            if isinstance(n, _ast.Constant) and isinstance(n.value, str)}
        assert any("sin git o fuera de un checkout" in c for c in constantes), nombre


def _exportacion_emulada(destino: Path) -> Path:
    """
    Los archivos del ARBOL DE TRABAJO que `git archive` llevaria: los
    versionados y los nuevos sin ignorar, menos los `export-ignore`. Se
    emula sobre el arbol de trabajo (y no sobre HEAD) para que el test mida
    lo que se va a confirmar.
    """
    archivos = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=RAIZ, capture_output=True, text=True, check=True).stdout.splitlines()
    atributos = subprocess.run(
        ["git", "check-attr", "export-ignore", "--stdin"], cwd=RAIZ,
        input="\n".join(archivos), capture_output=True, text=True,
        check=True).stdout.splitlines()
    ignorados = {linea.split(": export-ignore:")[0] for linea in atributos
                 if linea.endswith(": export-ignore: set")}
    import shutil
    for relativo in archivos:
        origen = RAIZ / relativo
        if relativo in ignorados or not origen.is_file():
            continue
        objetivo = destino / relativo
        objetivo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, objetivo)
    return destino


@pytest.mark.lento
def test_la_suite_del_entregable_pasa_sobre_una_exportacion(tmp_path):
    """
    Los tests que dependen de `.git` o de `proceso/`, corridos sobre una
    exportacion emulada: ninguno falla (los que leen lo versionado se
    saltan), la exportacion no lleva `proceso/` ni `.git`, y la suite entera
    se RECOGE sin errores. El par de la suite ENTERA sobre una exportacion
    real (`git archive HEAD`) se mide en el cierre y esta en la bitacora y en
    el README §7.
    """
    import shutil
    if shutil.which("git") is None or not (RAIZ / ".git").exists():
        pytest.skip("sin git o fuera de un checkout: no hay de donde exportar")
    arbol = _exportacion_emulada(tmp_path / "exportado")
    assert not (arbol / "proceso").exists() and not (arbol / ".git").exists()
    assert (arbol / "tests" / "test_t12_entregable.py").is_file()
    recogida = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p",
         "no:cacheprovider"], cwd=arbol, capture_output=True, text=True)
    assert recogida.returncode == 0, recogida.stdout[-2000:]
    corrida = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "--no-header", "-rs", *EN_LA_EXPORTACION],
        cwd=arbol, capture_output=True, text=True)
    assert corrida.returncode == 0, corrida.stdout[-3000:]
    assert "failed" not in corrida.stdout.splitlines()[-1]
    for motivo in ("sin .git (una exportacion del entregable)",
                   "sin git o fuera de un checkout"):
        assert motivo in corrida.stdout, motivo


# ===========================================================================
# 7. Lo que la resumida no puede perder (H2, H3, H6 y H7 de la auditoria)
# ===========================================================================

_ENLACE_ACOTACION = re.compile(r' <a href="#acotaciones" class="remision"[^>]*>[^<]*</a>')


def _sin_marcas(fragmento: str) -> str:
    """El fragmento sin la remision a acotaciones (completa) ni su marca (resumida)."""
    sin_marca = fragmento.replace(
        f' <span class="remision">{M11.MARCA_VACIO_VERIFICADO}</span>', "")
    return _ENLACE_ACOTACION.sub("", sin_marca)


def _filas_de_resultado_y_veredictos(bloque: str) -> list:
    """Los `<tr>` de la combinacion adoptada y de las verificaciones del punto."""
    hasta = bloque.index(f"<h4>{M11.TITULO_RESUMEN_CRITERIOS}</h4>")
    return re.findall(r"<tr[^>]*>.*?</tr>", bloque[:hasta], flags=re.S)


def test_cada_fila_de_la_resumida_es_una_fila_de_la_completa(corrida):
    """
    H7: identidad de FILAS, no de conjuntos de numeros. Cada `<tr>` de la
    combinacion adoptada y de las verificaciones de un punto en la resumida
    esta, tal cual, en el bloque de ese punto en la completa, salvo la marca
    de vacio verificado (H2), que sustituye a la remision a acotaciones.
    Asi un intercambio de dos celdas en el formateador comun no pasa
    inadvertido por el lado de la resumida.
    """
    nombre, informe, completa, resumida = corrida
    for p in informe.puntos:
        ancla = M11.ancla_de_punto(p.punto.id)
        del_resumen = _bloque_por_id(resumida, M11.PREFIJO_ANCLA_RESUMEN + ancla)
        del_completo = _sin_marcas(_bloque_por_id(completa, ancla))
        filas = _filas_de_resultado_y_veredictos(del_resumen)
        assert filas or not p.dimensionado, (nombre, p.punto.id)
        for fila in filas:
            assert _sin_marcas(fila) in del_completo, (nombre, p.punto.id, fila[:120])


def test_la_resumida_marca_la_adopcion_sobre_vacio_verificado(corrida):
    """
    H2: la resumida no tiene bloque de acotaciones; una fila cuyo criterio
    cubre un vacio normativo verificado lleva la MARCA en texto (sin
    numeros), y la completa sigue enlazando al bloque 0-bis.
    """
    nombre, informe, completa, resumida = corrida
    con_marca = 0
    for p in informe.puntos:
        bloque = _bloque_por_id(resumida, M11.PREFIJO_ANCLA_RESUMEN
                                + M11.ancla_de_punto(p.punto.id))
        for fila in _filas_de_resultado_y_veredictos(bloque):
            claves = re.findall(r"<code>([a-z_0-9]+)</code>", fila)
            if any(M11.ca.CRITERIOS.get(c) is not None
                   and M11.ca.CRITERIOS[c].vacio_verificado for c in claves):
                assert M11.MARCA_VACIO_VERIFICADO in fila, (nombre, fila[:120])
                con_marca += 1
    assert not _numeros(M11.MARCA_VACIO_VERIFICADO)
    if nombre == "juego_T11":
        assert con_marca >= 2   # G1 de B-01 y V9 de C-01, medidos por el auditor


def test_la_resumida_lleva_el_corredor_su_advertencia_y_el_origen_de_cada_S(corrida):
    """
    H3: la advertencia de corredor de la completa esta en la resumida, y la
    tabla de los [S] usados dice el valor y DE QUE ARCHIVO salio cada uno.
    """
    nombre, informe, completa, resumida = corrida
    from src import datos_sitio as ds
    contexto = cli.ContextoCorrida.de(informe)
    corredor = contexto.dato_efectivo("corredor_del_proyecto")
    advertencia = ds.advertencia_de_corredor("T-12", str(corredor.valor), corredor.origen)
    linea = (f"Corredor de los datos de sitio: <b>{M11._esc(str(corredor.valor))}</b> "
             f"(origen: <code>{M11._esc(corredor.origen)}</code>)")
    assert linea in completa and linea in resumida, nombre
    if advertencia:
        assert M11._esc(advertencia) in completa and M11._esc(advertencia) in resumida
    for clave in contexto.datos_usados:
        efectivo = contexto.dato_efectivo(clave)
        assert f"<code>{clave}</code>" in resumida, (nombre, clave)
        assert f"<code>{M11._esc(efectivo.origen)}</code>" in resumida, (nombre, clave)
        if efectivo.declarado_en_caliente:
            assert "declarado (sesion)" in resumida, (nombre, clave)
    if nombre == "juego_T11":
        assert "declarado (sesion)" in resumida


def test_la_fila_h_o_del_punto_llega_a_las_dos_vistas(corrida):
    """H6: la fila «h_o fuera de rango» (NOR-HDS-05, dicha EN EL PUNTO)."""
    nombre, informe, completa, resumida = corrida
    for p in informe.puntos:
        if not p.dimensionado:
            continue
        for fila in M11._filas_h_o(p.resultado.resultado_hidraulico):
            assert fila in completa and fila in resumida, (nombre, p.punto.id)


def test_el_estado_del_expediente_es_el_mismo_en_las_dos_vistas(corrida):
    """H7: una sola regla (`M11.estado_del_expediente`), la misma marca."""
    nombre, informe, completa, resumida = corrida
    marca = ('<span class="cumple">cerrado</span>' if informe.cerrado
             else '<span class="incumple">NO cierra</span>')
    for vista in (completa, resumida):
        # La celda que la plantilla rellena con %%estado_expediente: la de la
        # tabla de trazabilidad, la unica que lleva la marca de estado.
        assert vista.count(marca) >= 1, nombre
        contraria = ('<span class="incumple">NO cierra</span>' if informe.cerrado
                     else '<span class="cumple">cerrado</span>')
        assert contraria not in vista, nombre
    assert M11.estado_del_expediente(informe, "x").startswith(marca)


def test_la_resumida_nombra_la_completa_que_de_verdad_se_escribio(tmp_path):
    """
    H8: con `--pdf` por la via del navegador el archivo escrito es el `.html`
    de al lado, y la resumida tiene que nombrar ESE.
    """
    from src.modulos import M11_reporte
    informe = V.correr_juego()
    salida = M11_reporte.exportar_pdf(informe, tmp_path / "completa.pdf",
                                      abrir_navegador=False, forzar_navegador=True)
    assert salida.ruta.name == "completa.html"
    hecho = subprocess.run(
        [sys.executable, "cli.py", str(CSV_EJEMPLO), "--luz", "2.75",
         "--alcance", "perfil", "--json", str(tmp_path / "i.json"),
         "--html", str(tmp_path / "c.html"), "--html-resumida",
         str(tmp_path / "r.html")], cwd=RAIZ, capture_output=True, text=True)
    assert hecho.returncode in (0, 1), hecho.stderr
    assert "<code>c.html</code>" in (tmp_path / "r.html").read_text(encoding="utf-8")


def test_datos_sitio_resumidos_es_la_seccion_de_S_de_la_resumida(corrida):
    """La pieza de H3: la resumida la imprime entera, con el proyecto de la corrida."""
    _nombre, informe, _completa, resumida = corrida
    contexto = cli.ContextoCorrida.de(informe)
    assert M11.datos_sitio_resumidos(contexto, proyecto="T-12") in resumida
