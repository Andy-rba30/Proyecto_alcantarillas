"""
tests/test_t10_memoria.py
=========================
La aceptacion de T-10 de la cadena T (memoria M11 completa; INF-3.4.7,
INF-4.7, INF-5.1.10 --- el prompt lo llama INF-5.1.9 ---).

Se mide sobre las DOS corridas de referencia del indice de formulas
(`src/indice_formulas.CORRIDAS_DE_REFERENCIA`, datos de PRUEBA que ya
estaban en el repositorio): la de la guia de perfil, que dimensiona los
cuatro puntos, y la de punta a punta de T-7b/T-7c, que lleva a A-01 hasta
la Fase 9 entera. Son las corridas del censo de T-10.

Lo que fija:

  1. EL CENSO, por clave: todo NUMERO que el JSON publica de un punto
     dimensionado aparece en su bloque de la memoria (o en el paso, la
     eleccion o la nota identicos a los que ese bloque enlaza); los TEXTOS
     tambien, salvo los tres censados con su razon en
     `TEXTOS_CON_OTRA_VISTA`.
  2. Los avisos de `InformePunto.avisos()`, en las tres vistas.
  3. La Fase 9 del proyecto (la cadena sismica) y el armado en tabla.
  4. V4b, V6, V9 y el reparto 7.B.3b con paso y formula sustituida, la
     sustitucion rehecha a mano.
  5. Ningun paso dos veces en el documento, y toda remision resuelve.
  6. El alcance declarado del dueño, en las tres vistas.
  7. El anexo de sensibilidad: todo [A] con valor tiene ventana y sale en
     el anexo de la corrida que lo usa.
  8. El indice de formulas sobre corridas que dimensionan, y los datos de
     esas corridas iguales a los de la guia y a los de T-7b/T-7c.

ESCRITOS DESPUES DEL CODIGO, y se dice: el rojo se midio contra la base
(`2b13dc1`) con este archivo, y esta en el informe de la FASE A.
"""

from __future__ import annotations

import ast
import html as _html
import json
import re
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import indice_formulas as ind
from src.modelos import ALCANCE_DECLARADO, TipoDeBloqueo
from src.modulos import M11_reporte as M11
from src.normativa import fundamentos as F

RAIZ = Path(__file__).resolve().parents[1]
DECISIONES = RAIZ / "docs" / "decisiones_diferidas.md"
GUIA = RAIZ / "docs" / "guia_perfil.md"
TEST_T7C = RAIZ / "tests" / "test_t7c_cabezal_armado.py"
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"

ABS = 1e-9


# ===========================================================================
# Las dos corridas, sus tres vistas
# ===========================================================================

def _vistas(nombre: str):
    corrida = next(c for c in ind.CORRIDAS_DE_REFERENCIA if c.nombre == nombre)
    informe = ind.correr_referencia(corrida)
    html = M11.memoria_html(informe, proyecto="T-10",
                            ruta_plantilla=cli.plantilla_por_alcance(
                                informe.alcance))
    return informe, cli.informe_json(informe), cli.volcar(informe), html


@pytest.fixture(scope="module")
def perfil():
    return _vistas("perfil_guia")


@pytest.fixture(scope="module")
def expediente():
    return _vistas("expediente_cabezal")


@pytest.fixture(scope="module", params=("perfil_guia", "expediente_cabezal"))
def corrida(request, perfil, expediente):
    return perfil if request.param == "perfil_guia" else expediente


# ===========================================================================
# Apoyo: el bloque de un punto, con lo que enlaza
# ===========================================================================

_INICIO_PUNTO = re.compile(r'<div class="punto[^"]*" id="punto-([^"]+)">')
_REMISION = re.compile(r'href="#((?:paso|eleccion|nota)-[0-9a-f]{12})"')


def _bloques(html: str) -> dict:
    marcas = [(m.start(), m.group(1)) for m in _INICIO_PUNTO.finditer(html)]
    salida = {}
    for i, (ini, pid) in enumerate(marcas):
        fin = marcas[i + 1][0] if i + 1 < len(marcas) else html.index(
            '<h3 id="' + M11.ANCLA_CABEZAL_PROYECTO, ini) \
            if ('id="' + M11.ANCLA_CABEZAL_PROYECTO) in html[ini:] \
            else html.index("<h2", ini)
        salida[pid] = html[ini:fin]
    return salida


def _elemento_con_id(html: str, ancla: str) -> str:
    """El elemento entero que lleva `id="ancla"` (paso, eleccion o nota)."""
    i = html.index(f'id="{ancla}"')
    if ancla.startswith("paso-"):
        ini = html.rindex("<div", 0, i)
        return html[ini:html.index("</dl></div>", i) + len("</dl></div>")]
    if ancla.startswith("eleccion-"):
        return html[i:html.index("</li>", i)]
    return html[i:html.index("</dd>", i)]


def _plano(fragmento: str) -> str:
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", " ", fragmento)).split())


def _texto_del_punto(html: str, pid: str) -> str:
    """El bloque del punto MAS los pasos, elecciones y notas que enlaza."""
    bloque = _bloques(html)[pid]
    piezas = [bloque]
    vistos = set()
    pendientes = _REMISION.findall(bloque)
    while pendientes:
        ancla = pendientes.pop()
        if ancla in vistos:
            continue
        vistos.add(ancla)
        elemento = _elemento_con_id(html, ancla)
        piezas.append(elemento)
        pendientes.extend(_REMISION.findall(elemento))
    return _plano(" ".join(piezas))


def _hojas(objeto, ruta=""):
    if isinstance(objeto, dict):
        for k, v in objeto.items():
            yield from _hojas(v, f"{ruta}.{k}" if ruta else k)
    elif isinstance(objeto, list):
        for v in objeto:
            yield from _hojas(v, f"{ruta}[]")
    else:
        yield ruta, objeto


def _formatos(x: float) -> set:
    if float(x).is_integer() and abs(x) >= 1:
        return {str(int(x)), f"{x:.1f}", f"{x:.2f}", f"{x:.3f}"}
    return {f"{x:.2f}", f"{x:.3f}", f"{x:.4f}"}


# ===========================================================================
# 1. EL CENSO: lo que el JSON publica de un punto dimensionado esta en su
#    bloque de la memoria, por clave
# ===========================================================================

# Las TRES claves de texto del JSON que la memoria imprime de otra forma, con
# la razon. Nada mas: un texto nuevo del JSON que la memoria no lleve rompe
# el test por su clave.
TEXTOS_CON_OTRA_VISTA = {
    "bloqueos[].mensaje": (
        "en un bloqueo por criterio pendiente la memoria imprime sus partes "
        "--- la clave, la etiqueta, el concepto y la fuente --- y no la frase "
        "que las une"),
    "verificaciones[].fase": (
        "el rotulo de fase del JSON; la memoria agrupa las verificaciones en "
        "su tabla y su desarrollo y no repite el rotulo en cada fila"),
    "proteccion_salida.filtro.citas[]": (
        "ids del registro: la memoria imprime de cada una el numeral, el "
        "titulo y la pagina (`Cita.como_texto`), y el test lo comprueba"),
}


def test_todo_numero_del_json_de_un_punto_dimensionado_esta_en_su_bloque(corrida):
    informe, js, _cli, html = corrida
    faltan = []
    for p in js["puntos"]:
        if not p["dimensionado"]:
            continue
        texto = _texto_del_punto(html, p["id"])
        for ruta, v in _hojas(p):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v == 0:
                continue
            if not any(f in texto for f in _formatos(float(v))):
                faltan.append((p["id"], ruta, v))
    assert not faltan, faltan[:20]


def test_todo_texto_del_json_de_un_punto_dimensionado_esta_en_su_bloque(corrida):
    informe, js, _cli, html = corrida
    reg = M11._reg_M11
    faltan = []
    for p in js["puntos"]:
        if not p["dimensionado"]:
            continue
        texto = _texto_del_punto(html, p["id"])
        for ruta, v in _hojas(p):
            if not isinstance(v, str) or not v.strip():
                continue
            if ruta == "proteccion_salida.filtro.citas[]":
                assert _plano(reg.cita(v).como_texto()) in texto, (p["id"], v)
                continue
            if ruta in TEXTOS_CON_OTRA_VISTA:
                continue
            if " ".join(v.split()) not in texto:
                faltan.append((p["id"], ruta, v[:80]))
    assert not faltan, faltan[:20]


def test_el_censo_de_textos_con_otra_vista_dice_su_razon():
    assert len(TEXTOS_CON_OTRA_VISTA) == 3
    for clave, razon in TEXTOS_CON_OTRA_VISTA.items():
        assert razon.strip(), clave


# ===========================================================================
# 2. Los avisos del punto, en las tres vistas
# ===========================================================================

def test_todo_aviso_del_punto_sale_en_las_tres_vistas(corrida):
    informe, js, texto_cli, html = corrida
    bloques = _bloques(html)
    for p, pj in zip(informe.puntos, js["puntos"]):
        assert pj["avisos"] == list(p.avisos())
        for aviso in p.avisos():
            assert _html.escape(aviso) in bloques[p.punto.id], (
                p.punto.id, aviso[:80])
            assert f"aviso: {aviso}" in texto_cli, (p.punto.id, aviso[:80])


def test_un_bloqueo_dice_en_palabras_lo_que_es():
    """«Espera un dato» y «metodo no evaluable» no son NO CUMPLE."""
    for tipo in TipoDeBloqueo:
        assert M11.ROTULO_TIPO_DE_BLOQUEO.get(tipo.value, "").strip(), tipo


def test_el_bloqueo_de_un_dato_que_falta_lleva_su_rotulo(expediente):
    _informe, _js, _cli, html = expediente
    assert M11.ROTULO_TIPO_DE_BLOQUEO["DatoFaltanteError"] in html


# ===========================================================================
# 3. La Fase 9 del proyecto y el armado en tabla
# ===========================================================================

def test_la_cadena_sismica_sale_en_las_tres_vistas(expediente):
    informe, js, texto_cli, html = expediente
    cadena = informe.cabezal.cadena
    assert cadena is not None
    i = html.index(f'id="{M11.ANCLA_CABEZAL_PROYECTO}"')
    bloque = _plano(html[i:html.index("<h2", i)])
    assert js["cabezal"]["cadena_sismica"]["k_h"] == cadena.k_h
    assert "Cadena sismica" in texto_cli
    for e in cadena.pasos:
        assert e.simbolo in bloque
        assert f"{e.valor:.3f}" in bloque, e.simbolo
        if e.condicion:
            assert _plano(_html.escape(e.condicion)) in bloque, e.simbolo
            assert e.condicion in texto_cli
    for nota in informe.cabezal.notas:
        assert _plano(_html.escape(nota)) in bloque


def test_el_armado_va_en_tabla_con_los_numeros_de_M9(expediente):
    informe, _js, _cli, html = expediente
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    texto = _texto_del_punto(html, "A-01")
    assert a01.cabezal.armado
    for armado in a01.cabezal.armado:
        assert M11.TITULO_ARMADO.format(extremo=armado.extremo,
                                        tipo=armado.tipo) in texto
        for f in armado.tabla:
            assert f"{f.As_adoptado:.2f}" in texto
            assert f"{f.As_minimo:.2f}" in texto
            if f.barra is not None:
                assert f"{f.barra.diametro_mm:.2f}" in texto
        for s in armado.secciones:
            assert f"{s.As_resistencia:.2f}" in texto
            assert f"{s.recubrimiento_mm:.2f}" in texto


def test_la_traza_de_la_fase_9_no_repite_los_pasos_del_armado(expediente):
    """
    Los pasos A1..A8 cuelgan de su `Verificacion` y del `ArmadoDelCabezal`:
    hasta T-10 salian dos veces en el bloque del punto (50 pasos, 161 KB en
    A-01). Ahora una, y la traza de la Fase 9 remite.
    """
    informe, _js, _cli, html = expediente
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    bloque = _bloques(html)["A-01"]
    ya = {id(paso) for _c, paso in M11.desarrollo_de_verificaciones(a01)
          if paso is not None and not isinstance(paso, M11.NoAplica)}
    repetidos = [p for p in M11.traza_cabezal(a01) if id(p) in ya]
    assert repetidos
    for paso in repetidos:
        assert bloque.count(f"<code>{_html.escape(paso.codigo)}</code> &mdash; "
                            f"{_html.escape(paso.que)}</h5>") == 1, paso.codigo
    assert "se desarrollan una sola vez" in bloque


# ===========================================================================
# 4. V4b, V6, V9 y 7.B.3b: paso con formula sustituida, rehecha a mano
# ===========================================================================

def _valor(paso, simbolo):
    return next(m.valor for m in paso.sustitucion if m.simbolo == simbolo)


def _verificacion(punto, codigo):
    return next(v for _f, v in punto.verificaciones() if v.codigo == codigo)


def test_V4b_V6_V9_tienen_paso_en_los_cuatro_puntos(perfil):
    informe = perfil[0]
    for p in informe.puntos:
        for codigo in ("V4b", "V6", "V9"):
            v = _verificacion(p, codigo)
            assert v.paso is not None, (p.punto.id, codigo)
            assert v.paso.fundamento_id == f"F5.{codigo}"
    assert F.SIN_FUNDAMENTO == ()


def test_V4b_se_rehace_con_su_sustitucion(perfil):
    a01 = next(p for p in perfil[0].puntos if p.punto.id == "A-01")
    paso = _verificacion(a01, "V4b").paso
    HW, D = _valor(paso, "HW"), _valor(paso, "D")
    assert HW == a01.resultado.resultado_hidraulico.HW
    assert paso.resultado.valor == pytest.approx(HW / D, abs=ABS)
    assert paso.umbral.valor == ca.valor("HW_D_max")
    assert paso.umbral.cita_id == "HDS5_3ED.2.2.5d#AGENCIAS"
    assert paso.veredicto.margen == pytest.approx(
        paso.umbral.valor - HW / D, abs=ABS)


def test_V9_juzga_contra_la_norma_en_el_tubo_y_solo_sustituye_en_el_marco(perfil):
    informe = perfil[0]
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    tubo = _verificacion(a01, "V9").paso
    assert tubo.umbral.cita_id == "AASHTO_M170M.7.2.1"
    assert tubo.resultado.valor == pytest.approx(
        _valor(tubo, "D_max") - _valor(tubo, "D"), abs=ABS)
    c01 = next(p for p in informe.puntos if p.punto.id == "C-01")
    marco = _verificacion(c01, "V9").paso
    assert marco.umbral is None and marco.veredicto is None
    assert "NO TIENE NUMERAL" in marco.nota_del_proyecto


def test_V6_cuenta_las_celdas_con_su_procedencia(perfil):
    informe = perfil[0]
    for p in informe.puntos:
        paso = _verificacion(p, "V6").paso
        assert paso.resultado.valor == 1
        assert paso.umbral.cita_id == "MC_HHD.4.1.1.3.4a#MULTIPLES"


def test_el_reparto_7B3b_se_rehace_con_su_sustitucion(perfil):
    a01 = next(p for p in perfil[0].puntos if p.punto.id == "A-01")
    paso = next(x for x in a01.geometria.pasos if x.codigo == "7.B.3b")
    L, S = _valor(paso, "L"), _valor(paso, "S")
    H_e, H_s0 = _valor(paso, "H_entrada"), _valor(paso, "H_salida0")
    talud, semi, k = (_valor(paso, "talud"), _valor(paso, "ancho/2"),
                      _valor(paso, "k"))
    H_s = H_s0 + S * L
    assert _valor(paso, "H_salida") == pytest.approx(H_s, abs=ABS)
    assert _valor(paso, "proyeccion") == pytest.approx(
        talud * (H_e + H_s), abs=ABS)
    L_e = (semi + talud * H_e) * k
    assert _valor(paso, "L_entrada") == pytest.approx(L_e, abs=ABS)
    assert paso.resultado.valor == pytest.approx(L - L_e, abs=ABS)
    lc = a01.geometria.longitud_calculada
    assert lc.semilongitud_salida == pytest.approx(L - L_e, abs=ABS)
    assert lc.proyeccion_taludes == pytest.approx(talud * (H_e + H_s), abs=ABS)


# ===========================================================================
# 5. Ningun paso dos veces; toda remision resuelve
# ===========================================================================

def test_ningun_paso_identico_se_imprime_entero_dos_veces(corrida):
    _informe, _js, _cli, html = corrida
    enteros = re.findall(r'<div class="paso"[^>]*>.*?</dl></div>', html, re.S)
    sin_ancla = [re.sub(r' id="paso-[0-9a-f]{12}"', "", x) for x in enteros]
    repetidos = {x[:120] for x in sin_ancla if sin_ancla.count(x) > 1}
    assert not repetidos, sorted(repetidos)[:5]


def test_toda_remision_del_documento_apunta_a_un_id_que_existe(corrida):
    _informe, _js, _cli, html = corrida
    ids = set(re.findall(r'id="([^"]+)"', html))
    for ancla in set(re.findall(r'href="#([^"]+)"', html)):
        assert ancla in ids, ancla
    for ancla in re.findall(r'id="((?:paso|eleccion|nota)-[0-9a-f]{12})"', html):
        assert html.count(f'id="{ancla}"') == 1, ancla


def test_un_punto_renderizado_suelto_sale_entero(perfil):
    """Fuera del documento no hay a donde remitir: el paso sale entero."""
    informe = perfil[0]
    for p in informe.puntos:
        suelto = M11.memoria_de_punto(p)
        assert 'class="paso repetido"' not in suelto
        assert 'href="#paso-' not in suelto


# ===========================================================================
# 6. El alcance declarado del dueño, en las tres vistas
# ===========================================================================

def test_el_alcance_declarado_sale_en_las_tres_vistas(corrida):
    _informe, js, texto_cli, html = corrida
    plano = _plano(html)
    assert [d["clave"] for d in js["alcance"]["declarado"]] == [
        a.clave for a in ALCANCE_DECLARADO]
    for a in ALCANCE_DECLARADO:
        assert a.texto in texto_cli
        assert _plano(_html.escape(a.texto)) in plano


def test_cada_alcance_declarado_nombra_una_ficha_que_existe():
    texto = DECISIONES.read_text(encoding="utf-8")
    assert {a.clave for a in ALCANCE_DECLARADO} == {
        "armado_seccion_marco", "cabezal_paralelo_a_la_via",
        "iteracion_ancho_zapata_cabezal", "flotacion_marco_sin_peso_propio",
        "tirante_de_borde_hec14"}
    for a in ALCANCE_DECLARADO:
        assert f"## {a.ficha} · " in texto, a.ficha
        modulo, simbolo = a.simbolo.split(".")
        fuente = (RAIZ / "src" / "modulos" / f"{modulo}.py").read_text(
            encoding="utf-8")
        assert f"def {simbolo}(" in fuente, a.simbolo


# ===========================================================================
# 7. El anexo de sensibilidad
# ===========================================================================

def test_todo_A_con_valor_tiene_ventana():
    sin_ventana = [k for k, c in ca.CRITERIOS.items()
                   if c.etiqueta == "A" and c.valor is not None
                   and not c.sensibilidad]
    assert not sin_ventana, sin_ventana


def test_todo_A_usado_sale_en_el_anexo_con_su_ventana(corrida):
    informe, _js, _cli, html = corrida
    i = html.index(M11.TITULO_ANEXO_SENSIBILIDAD)
    anexo = html[i:]
    usados = [k for k in informe.contexto.criterios_usados
              if ca.CRITERIOS.get(k) is not None
              and ca.CRITERIOS[k].etiqueta == "A"]
    assert usados
    for clave in usados:
        assert f'href="#{M11.ancla_de_criterio(clave)}"' in anexo, clave
    por_punto = M11.criterios_A_por_punto(informe)
    assert set(por_punto) <= set(ca.CRITERIOS)


def test_el_anexo_no_recalcula():
    """El anexo lee la ventana de la ficha; el barrido es PF-3, aparte."""
    fuente = (RAIZ / "src" / "modulos" / "M11_reporte.py").read_text(
        encoding="utf-8")
    arbol = ast.parse(fuente)
    for nombre in ("anexo_sensibilidad", "criterios_A_por_punto"):
        nodo = next(n for n in ast.walk(arbol)
                    if isinstance(n, ast.FunctionDef) and n.name == nombre)
        texto = ast.unparse(nodo)
        assert "barrer" not in texto and "correr(" not in texto, nombre
        assert not [n for n in ast.walk(nodo) if isinstance(n, ast.BinOp)
                    and isinstance(n.op, (ast.Div, ast.Mult, ast.Pow))], nombre


# ===========================================================================
# 8. El indice de formulas sobre corridas que dimensionan
# ===========================================================================

def test_la_corrida_de_perfil_dimensiona_los_cuatro_y_la_de_expediente_arma_A01(
        perfil, expediente):
    assert perfil[0].dimensionados == 4
    a01 = next(p for p in expediente[0].puntos if p.punto.id == "A-01")
    assert a01.dimensionado and a01.cabezal.armado
    # PARADA (c): las secciones del fixture no se mueven.
    secciones = {p.punto.id: p.resultado.seccion.etiqueta()
                 for p in perfil[0].puntos}
    assert secciones["A-01"] == "Ø 0.90 m" and secciones["A-02"] == "Ø 0.90 m"
    assert secciones["C-01"] == "marco 1.20 × 0.90 m"
    assert a01.resultado.seccion.etiqueta() == "Ø 0.90 m"


def test_el_indice_muestra_las_formulas_que_antes_no_alcanzaba():
    texto = ind.INDICE_FORMULAS.read_text(encoding="utf-8")
    cuerpo = texto.split("## 2. ")[1].split("## 3. ")[0]
    for fundamento in ("F5.V7", "F5.VC1", "F6.LAUSHEY", "F5.V4b", "F5.V9",
                       "F8.CLASE", "F9.ARM_FLEXION", "F10.TRAMO"):
        assert f"`{fundamento}`" in cuerpo, fundamento
    # INF-5.1.10: el paso «cual control gobierna» con la cita correcta (la
    # del HDS-5 3.3.5, no la A.2 de las ecuaciones de entrada).
    fila = next(l for l in cuerpo.splitlines() if "| `4.4` |" in l)
    assert "num. 3.3.5" in fila and "num. A.2" not in fila


def test_los_datos_de_la_corrida_de_perfil_son_los_de_la_guia():
    from tests.apoyo import guia_perfil as gp
    bloques = {b.archivo: b for b in gp.bloques_de_la_guia(
        GUIA.read_text(encoding="utf-8")) if b.archivo}
    ids = {b.id: b for b in gp.bloques_de_la_guia(
        GUIA.read_text(encoding="utf-8")) if b.id}
    carpeta = ind.DIR_CORRIDAS_DE_REFERENCIA.joinpath("perfil_guia")
    externos = json.loads(carpeta.joinpath("externos.json").read_text())
    de_la_guia = json.loads(bloques["guia/externos.json"].cuerpo)
    # La luz que la guia pasa por la bandera `--luz` va como global del JSON.
    comando = ids["perfil"].comando()
    luz = float(comando[comando.index("--luz") + 1])
    assert externos["globales"].pop("luz_m") == luz
    assert externos == de_la_guia
    assert json.loads(carpeta.joinpath("sitio.json").read_text()) == \
        json.loads(bloques["guia/sitio.json"].cuerpo)
    original = CSV_EJEMPLO.read_text(encoding="utf-8").splitlines()
    fila_c01 = ids["fila_c01"].cuerpo
    esperado = [fila_c01 if l.startswith("C-01,") else l for l in original]
    assert carpeta.joinpath("puntos.csv").read_text(
        encoding="utf-8").splitlines() == esperado


def test_los_datos_de_la_corrida_de_expediente_son_los_de_T7b_y_T7c():
    from tests import test_t7c_cabezal_armado as t7c
    carpeta = ind.DIR_CORRIDAS_DE_REFERENCIA.joinpath("expediente_cabezal")
    declaradas = json.loads(carpeta.joinpath("declaraciones.json").read_text())
    assert declaradas.pop("remanso_derecho_via") == "cota_de_afectacion"
    assert declaradas == t7c.DECLARACIONES_DE_PRUEBA
    externos = json.loads(carpeta.joinpath("externos.json").read_text())
    # Lo que `_correr_de_prueba` escribe en su JSON, leido de su AST.
    arbol = ast.parse(TEST_T7C.read_text(encoding="utf-8"))
    funcion = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)
                   and n.name == "_correr_de_prueba")
    a01 = next(n.value for n in ast.walk(funcion) if isinstance(n, ast.Assign)
               and getattr(n.targets[0], "id", "") == "a01")
    a01 = ast.literal_eval(ast.unparse(a01).replace(
        "COTA_AFECTACION_DE_PRUEBA", repr(t7c.COTA_AFECTACION_DE_PRUEBA)))
    a01["cota_afectacion_aguas_arriba_msnm"] = t7c.COTA_AFECTACION_DE_PRUEBA
    globales = next(ast.literal_eval(k.value) for n in ast.walk(funcion)
                    if isinstance(n, ast.Call)
                    for k in n.keywords if k.arg == "globales")
    assert externos == {"globales": globales, "puntos": {"A-01": a01}}
    filas = carpeta.joinpath("puntos.csv").read_text(encoding="utf-8")
    assert t7c.FILA_A01.replace(",SM,,,", f",SM,{t7c.NF_DE_PRUEBA},,") in filas
    sitio = json.loads(carpeta.joinpath("sitio.json").read_text())
    declarar = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)
                    and n.name == "_declarar_sitio")
    de_t7c = {ast.literal_eval(c.args[0]): (ast.literal_eval(c.args[1]),
                                             ast.literal_eval(c.args[2]),
                                             ast.literal_eval(c.args[3]))
              for c in ast.walk(declarar) if isinstance(c, ast.Call)
              and ast.unparse(c.func).endswith("establecer_dato_dinamico")}
    assert {k: (d["valor"], d["trazabilidad"], d["fecha"])
            for k, d in sitio.items()} == de_t7c
