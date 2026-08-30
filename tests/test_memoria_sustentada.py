"""
La memoria SUSTENTADA (§4.4 del plan de correcciones v12).

Los tres criterios de salida que ese numeral escribe, cada uno como un test
que se puede correr:

    1. ningun `PasoDeMemoria` sin `por_que`;
    2. ningun umbral sin cita;
    3. ninguna cita textual que no este en el registro.

Y alrededor, los cuatro hallazgos que la §4.4 nombra:

    NOR-MEM-01  el matiz «recomienda, no prohibe» de V2 tiene que LLEGAR a la
                memoria generada, no solo vivir en el codigo. Se comprueba
                sobre el producto, que es donde fallaba.
    MAT-O13     lo mismo para V1: el 0.75 tiene el mismo caracter que el 0.25
                y solo V2 llevaba el matiz.
    NOR-HID-04  la interpretacion del proyectista se imprime SEPARADA de la
                cita, no pegada a ella como si fuera norma.
    SIS-B-05    el analisis de sensibilidad llega al documento, no solo a los
                tests.

POR QUE SE COMPRUEBA SOBRE EL HTML GENERADO Y NO SOBRE LOS OBJETOS. Porque el
defecto que origina esta sesion era exactamente esa diferencia: el repositorio
afirmaba que el matiz de V2 «viaja hasta la memoria» y era cierto sobre el
codigo y falso sobre el producto --- «recomend» aparecia CERO veces en la
memoria generada ---. Un test sobre los objetos habria pasado.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

from cli import cargar_datos_externos, correr                      # noqa: E402
from modelos import (Magnitud, PasoDeMemoria, TipoDeVeredicto,     # noqa: E402
                     Umbral, Veredicto)
from modulos import M11_reporte as M11                             # noqa: E402
from normativa import fundamentos as F                             # noqa: E402
from normativa.registro import construir                           # noqa: E402

CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"


@pytest.fixture(scope="module")
def reg():
    return construir()


@pytest.fixture(scope="module")
def informe():
    """
    La corrida real del CSV de ejemplo con los datos externos minimos, que es
    la misma que usa `test_M11_reporte`.
    """
    externos = cargar_datos_externos(
        None, {"luz_m": 2.0, "TW_m": 0.0, "longitud_m": 14.0,
               "L_hidraulico_m": None, "categoria_tr": None})
    return correr(CSV_EJEMPLO, externos)


@pytest.fixture(scope="module")
def memoria(informe):
    return M11.memoria_html(informe, proyecto="prueba de la memoria sustentada")


def _pasos_de(informe):
    """Todos los `PasoDeMemoria` que ESTA corrida emitio, de donde sea."""
    vistos = []

    def _anota(paso):
        if paso is not None:
            vistos.append(paso)

    for punto in informe.puntos:
        if punto.clasificacion is not None:
            _anota(getattr(punto.clasificacion.verificacion_luz, "paso", None))
            _anota(getattr(punto.clasificacion.periodo_retorno, "paso", None))
        for _fase, v in punto.verificaciones():
            _anota(getattr(v, "paso", None))
        for escalon in punto.traza:
            for v in escalon.verificaciones:
                _anota(getattr(v, "paso", None))
            hidraulico = getattr(escalon, "resultado_hidraulico", None)
            if hidraulico is not None:
                vistos.extend(hidraulico.pasos)
        if punto.resultado is not None and \
                punto.resultado.resultado_hidraulico is not None:
            vistos.extend(punto.resultado.resultado_hidraulico.pasos)
        # El TW de Sec. 1.3 tambien emite paso desde S20: es la unica traza
        # de la Fase 1 que la memoria imprime, y sin recogerla aqui el
        # fundamento F1.TW quedaria contado como "declarado y nunca usado".
        if getattr(punto, "tw_sec13", None) is not None:
            _anota(getattr(punto.tw_sec13, "paso", None))
        if punto.proteccion is not None:
            _anota(getattr(punto.proteccion, "paso", None))
        if punto.espaciamiento is not None:
            _anota(getattr(punto.espaciamiento, "paso", None))
    for recubrimiento in informe.cabezal.recubrimientos:
        _anota(getattr(recubrimiento, "paso", None))
    return vistos


# ===========================================================================
# Criterio de salida 1 - ningun PasoDeMemoria sin por_que
# ===========================================================================

def test_ningun_paso_de_memoria_sin_por_que(informe):
    """
    Sobre la corrida real. El invariante esta ademas en el `__post_init__` del
    tipo --- un paso sin `por_que` no se construye ---, y este test comprueba
    que la corrida produce pasos de verdad: un invariante que nadie ejerce no
    prueba nada.
    """
    pasos = _pasos_de(informe)
    assert pasos, ("la corrida no emitio ni un solo PasoDeMemoria: la traza "
                   "no llega, y todo lo demas de este archivo seria vacuo")
    sin_por_que = [p.que for p in pasos if not p.por_que.strip()]
    assert not sin_por_que, sin_por_que


def test_el_tipo_rechaza_un_paso_sin_por_que():
    """El invariante, ejercido directamente."""
    with pytest.raises(ValueError) as exc:
        PasoDeMemoria(que="x", por_que="  ", formula="f", sustitucion=(),
                      resultado=Magnitud("a", 1.0, "m", "de algun sitio"))
    assert "por_que" in str(exc.value)


def test_todo_paso_declara_el_fundamento_del_que_saco_su_por_que(informe, reg):
    """
    El `por_que` no se escribe suelto en el modulo de calculo: sale de un
    `Fundamento` del registro, y el paso guarda su id. Es lo que impide
    redactar «la norma obliga a...» encima de un parrafo que recomienda ---
    el `Fundamento` lleva `verbo`, y el registro comprueba que el verbo este
    sostenido por el caracter de alguna de sus citas (invariante T11).
    """
    for paso in _pasos_de(informe):
        assert paso.fundamento_id, paso.que
        fundamento = reg.fundamento(paso.fundamento_id)
        assert paso.por_que == fundamento.por_que, (
            f"{paso.que}: el por_que no es el del fundamento "
            f"{paso.fundamento_id}. Alguien lo reescribio en el modulo")


# ===========================================================================
# Criterio de salida 2 - ningun umbral sin cita
# ===========================================================================

def test_ningun_umbral_sin_cita(informe, reg):
    for paso in _pasos_de(informe):
        if paso.umbral is None:
            continue
        assert paso.umbral.cita_id, paso.que
        reg.cita(paso.umbral.cita_id)          # KeyError si no existe
        assert paso.umbral.cita_id in paso.citas_textuales, (
            f"{paso.que}: el umbral cita {paso.umbral.cita_id} y esa cita no "
            "esta entre las que el paso imprime. El numero y la frase que lo "
            "fija se imprimen juntos o el revisor lee uno sin la otra")


def test_el_tipo_rechaza_un_umbral_sin_cita():
    with pytest.raises(ValueError) as exc:
        Umbral(descripcion="x", valor=1.0, unidad="m", cita_id="",
               caracter="EXIGENCIA", aplicacion="se aplica")
    assert "cita_id" in str(exc.value)


def test_un_veredicto_de_cumplimiento_sin_umbral_no_se_construye():
    """
    Decir que algo cumple sin decir contra que es lo que hace indefendible una
    memoria. Un paso que calcula y no juzga tiene su propio veredicto ---
    `SIN_VEREDICTO` --- y no necesita inventarse un umbral.
    """
    with pytest.raises(ValueError) as exc:
        PasoDeMemoria(
            que="x", por_que="porque si", formula="f", sustitucion=(),
            resultado=Magnitud("a", 1.0, "m", "de algun sitio"),
            veredicto=Veredicto(tipo=TipoDeVeredicto.CUMPLE))
    assert "sin umbral" in str(exc.value)


def test_todo_umbral_normativo_del_bloque_fijo_lleva_su_cita(reg):
    """
    El otro sitio donde viven umbrales: `UMBRALES_DE_VERIFICACION`, que M11
    imprime SIEMPRE (se imprima o no una sola fila de verificacion). Ninguna
    de sus entradas puede quedarse sin cita del registro.
    """
    import constantes_normativas as cn

    for u in cn.UMBRALES_DE_VERIFICACION:
        anclas = tuple(u.get("citas", ())) + tuple(
            t for t, _campo in u.get("literales_de_tabla", ()))
        assert anclas, u["codigo"]
        for cita_id in u.get("citas", ()):
            reg.cita(cita_id)
        for tabla_id, _campo in u.get("literales_de_tabla", ()):
            reg.tabla(tabla_id)


# ===========================================================================
# Criterio de salida 3 - ninguna cita textual fuera del registro
# ===========================================================================

# Las comillas angulares son el rotulo de "esto es literal" en toda la memoria.
CITA_EN_LA_MEMORIA = re.compile(r"&laquo;(.+?)&raquo;", re.DOTALL)


def _desescapar(texto: str) -> str:
    import html

    return html.unescape(texto)


def test_ninguna_cita_textual_de_la_memoria_esta_fuera_del_registro(memoria,
                                                                    reg):
    """
    Todo lo que la memoria entrecomilla con &laquo;&raquo; --- que es como
    marca «esto es literal de la fuente» --- tiene que existir en el registro,
    verificado contra su pagina.

    La lista blanca es corta y cada entrada dice por que. NO son excepciones
    al criterio: son textos que la memoria entrecomilla y que NO se presentan
    como cita de una norma --- una frase del propio expediente, un rotulo de
    columna del CSV ---, y donde las comillas hacen de comillas y no de sello
    de literalidad.
    """
    literales = reg.textos_literales()
    normalizados = {" ".join(t.split()) for t in literales}
    permitidos = {
        # Transcripcion declarada como tal en el bloque de umbrales: la forma
        # con el MAXIMO de h_o, que la 3a ed. del HDS-5 no imprime como
        # igualdad y que NO puede internarse como `Cita` de la edicion de 1985
        # porque la paginacion de esa copia es `SinDeterminar` (invariante T6
        # del registro). Va rotulada «Transcripcion (NO es cita)».
        "ho = TW or (dc + D)/2 whichever is larger.",
    }
    fuera = []
    for bruto in CITA_EN_LA_MEMORIA.findall(memoria):
        texto = " ".join(_desescapar(bruto).split())
        if texto in normalizados or texto in permitidos:
            continue
        # Una cita puede imprimirse recortada por el ancho de la pagina o
        # dentro de un parrafo mayor: se admite la inclusion en los dos
        # sentidos, que sigue atando el texto a un original del registro.
        if any(texto in t or t in texto for t in normalizados):
            continue
        fuera.append(texto[:160])
    assert not fuera, (
        "la memoria entrecomilla como literal texto que el registro no "
        "sostiene:\n  " + "\n  ".join(fuera))


# ===========================================================================
# NOR-MEM-01 y MAT-O13 - el matiz de recomendacion, en el PRODUCTO
# ===========================================================================

def test_la_memoria_dice_que_V2_se_RECOMIENDA_y_el_proyecto_lo_endurece(memoria):
    """
    NOR-MEM-01, verificado donde fallaba: sobre la memoria generada. «recomend»
    aparecia CERO veces mientras el repositorio afirmaba que el matiz era «lo
    unico que la memoria imprime de V2».
    """
    assert memoria.lower().count("recomend") > 0
    assert "0.25 m/s" in memoria
    assert "sedimenta" in memoria.lower()
    assert "RECOMENDACION" in memoria
    assert "umbral DURO" in memoria


def test_la_memoria_dice_lo_MISMO_de_V1(memoria):
    """
    MAT-O13: el 0.75 de V1 nace de una frase del mismo apartado y tiene el
    mismo caracter de recomendacion; hasta la correccion solo V2 llevaba el
    matiz. Los dos numerales se presentaban con distinta fuerza normativa sin
    nada en la fuente que lo justificara.
    """
    assert "4.1.1.3.7 b)" in memoria
    assert "25 %" in memoria
    # La frase entera del numeral, tal como el registro la tiene.
    assert "Se recomienda que el dise" in memoria


def test_las_dos_mitades_del_parrafo_de_V2_llegan_por_separado(memoria):
    """
    La oracion del Manual dice DOS cosas con fuerza distinta: «se debera
    verificar» (exigencia de comprobar) y «recomendandose que la velocidad
    minima sea igual a 0.25 m/s» (recomendacion sobre el valor). Leida solo la
    segunda, «V2 es una recomendacion» se entiende como que verificar el piso
    es opcional, que no es lo que el Manual dice.
    """
    assert "Se deber" in memoria and "verificar que la velocidad m" in memoria
    assert "recomend" in memoria
    assert "EXIGENCIA + RECOMENDACION" in memoria


# ===========================================================================
# NOR-HID-04 - la interpretacion, separada de la cita
# ===========================================================================

def test_la_interpretacion_de_la_tabla_10_no_va_pegada_a_la_cita(memoria, reg):
    """
    Caso testigo de la regla tipografica. «El rango recorre la calidad del
    revestimiento» es lectura del proyectista --- el Manual no dice por que hay
    dos numeros --- y se imprimia dentro del mismo parrafo que la cita.

    Se comprueban las tres cosas: que el texto esta, que lleva su rotulo de
    interpretacion, y que NO aparece dentro de ningun bloque marcado como
    literal de la fuente.
    """
    interp = reg.tabla("MC_HHD.T10").interpretacion
    fragmento = "recorran la calidad del revestimiento"
    assert fragmento in interp.texto
    assert "NO lo dice el Manual" in memoria or "esto NO lo dice el Manual" \
        in memoria.lower() or "NO lo dice el Manual" in memoria
    assert 'class="aviso interpretacion"' in memoria
    for literal in CITA_EN_LA_MEMORIA.findall(memoria):
        assert fragmento not in _desescapar(literal), (
            "la interpretacion del proyectista se esta imprimiendo DENTRO de "
            "un bloque entrecomillado como literal de la fuente: es "
            "exactamente NOR-HID-04")


def test_la_interpretacion_lleva_lo_que_juega_en_contra(memoria, reg):
    """
    Una lectura que no encuentra nada en contra no se ha buscado a si misma:
    el tipo `Interpretacion` exige al menos un `en_contra`, y la memoria lo
    imprime. Es lo que permite a un revisor discutir la lectura sin discutir
    la norma.
    """
    interp = reg.tabla("MC_HHD.T10").interpretacion
    assert interp.en_contra
    assert "juega EN CONTRA" in memoria
    for contra in interp.en_contra:
        assert contra[:40] in memoria


# ===========================================================================
# SIS-B-05 - el analisis de sensibilidad llega al documento
# ===========================================================================

def test_la_sensibilidad_declarada_se_imprime_como_analisis(memoria):
    """
    `parametros_sensibilizables()` existia y solo la consumian los tests,
    mientras la plantilla anunciaba «con analisis de sensibilidad
    obligatorio». El rango llegaba al documento, pero sin decir que era ni
    para que servia.
    """
    import criterios_adoptados as ca

    assert "Sensibilidad declarada" in memoria
    assert "barrido de sensibilidad" in memoria
    usados_con_rango = [k for k in ca.criterios_usados()
                        if ca.criterio(k).sensibilidad]
    assert usados_con_rango, "la corrida no invoco ningun criterio con rango"
    for clave in usados_con_rango:
        assert clave in memoria


def test_la_procedencia_R1_de_cada_criterio_llega_a_la_memoria(memoria):
    """
    La regla R1: «se adopto X, elegido entre X1...Xn de la Tabla T (numeral N,
    pag. P), por la razon R». Hasta S18 solo se imprimia para los valores
    declarados por la ventana emergente; los criterios transcritos en el
    archivo --- la inmensa mayoria de los que gobiernan una corrida --- se
    imprimian sin decir de donde salen.
    """
    assert "De donde sale (R1)" in memoria


# ===========================================================================
# El censo de lo que NO tiene fundamento
# ===========================================================================

def test_todo_fundamento_declarado_lo_usa_algun_paso(informe):
    """
    Un `Fundamento` sin paso que lo imprima es una promesa que la memoria no
    cumple. Los que hoy no pueden emitir paso en esta corrida --- los de fases
    que el expediente no alcanza --- se declaran aqui, con la razon, en vez de
    quedar sueltos.
    """
    import constantes_normativas as cn

    emitidos = {p.fundamento_id for p in _pasos_de(informe)}
    # Los que llegan por la OTRA puerta: el bloque fijo de umbrales, que M11
    # imprime siempre. `F3.D_MIN` solo tiene esa: el minimo de 0.90 m no se
    # verifica sobre un resultado, es el piso de la serie de diametros
    # candidatos, y aun asi su «por que» tiene que llegar al revisor.
    del_bloque_fijo = {u["fundamento"] for u in cn.UMBRALES_DE_VERIFICACION}
    # Las fases que la corrida por defecto no alcanza, cada una por un vacio
    # del expediente y no por falta de fundamento.
    sin_alcanzar = {
        "F7.RELLENO",       # 7.A se detiene en 'espesor_pared_conducto'
        "F8.RECUBRIMIENTO",  # 9.4 se detiene en 'categoria_refuerzo_aashto'
        "F10.CUNETA",       # falta el dato 'L_hidraulico_m'
        "F6.LAUSHEY",       # Fase 6 cuelga de un punto dimensionado
    }
    declarados = set(F.FUNDAMENTOS)
    huerfanos = declarados - emitidos - del_bloque_fijo - sin_alcanzar
    assert not huerfanos, (
        f"fundamentos que ningun paso imprime y que nadie declaro como "
        f"inalcanzables en esta corrida: {sorted(huerfanos)}")


def test_el_censo_de_lo_que_no_puede_tener_fundamento_esta_completo():
    """
    Las verificaciones sin `PasoDeMemoria` no son un hueco: son un censo. Cada
    una dice por que no puede tener fundamento normativo hoy y que haria falta
    para traerlo.
    """
    codigos = {id_.split(".")[-1] for id_, _p, _q in F.SIN_FUNDAMENTO}
    assert {"V4b", "V5", "V6", "V8", "V9"} <= codigos
    for id_, por_que, que_haria_falta in F.SIN_FUNDAMENTO:
        assert por_que.strip() and que_haria_falta.strip(), id_


def test_una_verificacion_sin_paso_imprime_su_razon_en_vez_de_callarla():
    """
    Un hueco callado en una memoria se lee como un olvido. Con la razon
    delante se lee como lo que es.
    """
    for codigo in ("V4b", "V5", "V6", "V8", "V9"):
        bloque = M11._paso_ausente(codigo)
        assert "sin fundamento normativo declarado" in bloque, codigo
        assert "Que haria falta para traerlo" in bloque, codigo


# ===========================================================================
# El cambio de fondo: M11 formatea, no reconstruye
# ===========================================================================

def test_la_memoria_imprime_el_desarrollo_del_calculo(memoria):
    """
    El criterio de salida de la §4.4 leido entero: «la memoria de un punto se
    lee de arriba abajo y se entiende sin abrir el codigo; cada numero tiene
    de donde salio, contra que se comparo y la frase de la norma».
    """
    assert 'class="paso"' in memoria
    assert "Por que se hace" in memoria
    assert "Con que valores" in memoria
    assert "Contra que se compara" in memoria
    assert "Veredicto" in memoria
    assert "Lo que dice la fuente" in memoria


def test_el_desarrollo_hidraulico_llega_aunque_el_punto_no_cierre(informe,
                                                                  memoria):
    """
    En ESTE expediente ningun punto se dimensiona --- V5 se detiene siempre en
    `ancho_derecho_via_m`, que ningun tablero aporta ---, de modo que
    `ResultadoPunto.resultado_hidraulico` es None en todos. Sin el escalon de
    la traza, el desarrollo que M3 y M4 SI calcularon no llegaria jamas al
    revisor: es la misma trampa de NOR-MEM-01, cierta sobre el codigo y falsa
    sobre el producto.
    """
    assert informe.dimensionados == 0, (
        "si algun punto llegara a dimensionarse, este test deja de probar lo "
        "que dice: revisar el supuesto antes de tocarlo")
    assert any(getattr(p, "resultado_hidraulico", None) is not None
               for punto in informe.puntos for p in punto.traza)
    assert "ultimo escalon evaluado" in memoria
    assert "Tirante normal y velocidades" in memoria


def test_M11_no_calcula_y_sobre_D(informe):
    """
    SIS-A-07: M11 declaraba «sin calcular nada nuevo» y dividia `y_normal/D`
    en dos sitios. El numero vive ahora en `ResultadoPunto.y_sobre_D`, escrito
    una vez, y este test vigila que la capa de reporte no vuelva a hacerlo.
    """
    import ast

    fuente = (RAIZ / "src" / "modulos" / "M11_reporte.py").read_text(
        encoding="utf-8")
    divisiones = [n for n in ast.walk(ast.parse(fuente))
                  if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
    sospechosas = [n for n in divisiones
                   if not (isinstance(n.left, ast.Name)
                           and n.left.id in {"RAIZ", "SRC", "DIR_PLANTILLAS",
                                             "DIR_DOCS"})
                   and not isinstance(n.left, ast.Call)
                   and not isinstance(n.left, ast.Attribute)]
    assert not sospechosas, (
        "M11 volvio a hacer aritmetica sobre magnitudes: la capa de reporte "
        "formatea la traza que el calculo emitio, no la recalcula")
