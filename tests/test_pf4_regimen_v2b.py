# -*- coding: utf-8 -*-
"""
tests/test_pf4_regimen_v2b.py
=============================
La aceptacion de PF-4 (`docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md`):
V2b deja de aplicar el indicador de HDS-5 3.a ed. num. 5.3.3 «Sedimentation»
(pag. impresa 5.11, PDF 147) como umbral duro «por decision conservadora del
proyecto» --un [A] cableado y sin ficha-- y pasa a leer el REGIMEN de un
criterio declarado, `regimen_v2b`, con dos opciones cerradas:

    umbral_duro          la conducta de S20: el indicador disparado detiene el
                         punto (`Verificacion.cumple = False`). Es el valor del
                         ARCHIVO, y por eso ningun numero de la linea base se
                         mueve.
    indicador_con_aviso  V2b se evalua igual, la memoria imprime el texto
                         literal de la fuente y el veredicto INDICADOR, y el
                         diametro NO se descarta (`cumple = True`).

LA FUENTE, VERIFICADA EN ESTA SESION contra `normas/hif12026.pdf` (sha1 del
registro): la 5.11 nombra DOS «key indicators of potential problems» y no
escribe ninguna cifra ni un «shall»/«should»; el `caracter` de la cita
`HDS5_3ED.5.3.3#INDICADORES` es DEFINICION, y el unico verbo que lo sostiene
es DEFINE (`VERBO_COMPATIBLE_CON`). Por eso el `Fundamento` del regimen
DEFINE y no obliga (NOR-MEM-01).

EL VEREDICTO INDICADOR ES UN VALOR NUEVO DE `TipoDeVeredicto`, NO UNA CUARTA
CAPA (PC-27, «Cerrado parcial»): `Verificacion.cumple` sigue siendo bool,
`Bloqueo` no se toca, y lo que cambia es que la capa del veredicto puede decir
«el indicador se disparo y el punto no se detiene», que ninguno de los cuatro
valores anteriores podia decir sin mentir (CUMPLE), sin divergir del pipeline
(NO_CUMPLE, SIS-A-07), sin fingir que no se evaluo (DIFERIDO) o que no se
juzgo (SIN_VEREDICTO). La ficha PF-4-01 de `docs/decisiones_diferidas.md`
lleva el argumento entero.

LA LINEA BASE NO MUEVE UN NUMERO, y se mide con el comparador de E-B y no con
un diff de bytes: el JSON lleva `criterios_sha1` (cambia con cualquier
criterio nuevo) y la memoria imprime los criterios USADOS (`regimen_v2b` lo
invoca toda corrida de perfil), de modo que los bytes cambian por FORMATO y
el diff se lee y se declara en el README de la linea base, como en PF-1.

Escritos primero EN ROJO con `xfail(strict=True)` por test (marcador `ROJO`)
sobre el invariante, nunca sobre la salida actual; medidos antes de tocar
codigo y liberados al corregir. Los que valen antes y despues lo dicen en su
docstring y no llevan el marcador.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import barrido
from src import comparador
from src import criterios_adoptados as ca
from src import editores as ed
from src.modelos import (CriterioPendienteError, DatoInvalidoError, Magnitud,
                         PasoDeMemoria, TipoDeVeredicto, Umbral, Veredicto)
from src.modulos import M11_reporte as M11
from src.modulos import M5_verificaciones as M5
from src.normativa.registro import construir
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, sin_valor
from tests.test_M5_verificaciones import _punto, _resultado
from tests.test_canal_discrepancias import DECLARACIONES_DEL_CAJON

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
DIR_LINEA_BASE = RAIZ / "tests" / "linea_base_familia_c"
EXTERNOS_AMPLIADOS = DIR_LINEA_BASE / "entradas_ampliadas.json"
INFORME_ANCHO = DIR_LINEA_BASE / "informe_perfil_ancho.json"

# El marcador de rojo se retiro al corregir; la constancia de la medida queda
# arriba (25 items: 19 xfailed, 0 XPASS, 2 passed y un teardown del fixture
# `_limpio` que fallaba en el arbol viejo por no existir la clave).

CLAVE = "regimen_v2b"
UMBRAL_DURO = "umbral_duro"
INDICADOR_CON_AVISO = "indicador_con_aviso"
CITA_INDICADORES = "HDS5_3ED.5.3.3#INDICADORES"
# La luz de la linea base ancha: es el `--luz 2.75` de `regenerar.sh`.
LUZ_LINEA_BASE = 2.75


@pytest.fixture
def _limpio():
    """El criterio queda como en el archivo al salir, declare lo que declare el test."""
    yield
    if ca.declarado_en_caliente(CLAVE):
        ca.quitar_valor_dinamico(CLAVE)


def _v2b(regimen, S):
    """V2b con `regimen` declarado en caliente y el conducto a pendiente S."""
    punto = _punto()                       # S_cauce = 0.006
    ca.establecer_valor_dinamico(CLAVE, regimen)
    return punto, M5.v2b_sedimentacion(punto=punto, resultado=_resultado(S=S))


def _declaraciones_cli(*extra, cajon):
    """Las banderas `--declarar`: los siete del cajon si `cajon`, mas `extra`."""
    banderas = []
    if cajon:
        for clave, valor in DECLARACIONES_DEL_CAJON.items():
            banderas += ["--declarar", f"{clave}={valor!r}"]
    for texto in extra:
        banderas += ["--declarar", texto]
    return banderas


def _correr_cli(tmp_path, *declaraciones, cajon=False, csv=CSV_EJEMPLO):
    """
    La corrida de perfil de la linea base ancha, con las declaraciones dadas
    (y los siete del cajon si `cajon`, que la linea base NO declara).

    EN SUBPROCESO, como `regenerar.sh`, y no por `cli.main` en este proceso:
    `conftest.py` declara en caliente tres criterios de prueba para toda la
    suite (el espesor de pared del TMC y del HDPE entre ellos), y una corrida
    en proceso no es la corrida que produce la linea base --B-01 recorre 22
    escalones en vez de 10--. Lo que se mide aqui es la CLI real.
    """
    json_ = tmp_path / "informe.json"
    html = tmp_path / "memoria.html"
    r = subprocess.run(
        [sys.executable, "cli.py", str(csv), "--luz", str(LUZ_LINEA_BASE),
         "--alcance", "perfil", "--datos-externos", str(EXTERNOS_AMPLIADOS),
         "--json", str(json_), "--html", str(html)]
        + _declaraciones_cli(*declaraciones, cajon=cajon),
        cwd=RAIZ, capture_output=True, text=True)
    assert json_.exists(), r.stderr
    return r.stdout, json.loads(json_.read_text(encoding="utf-8")), \
        html.read_text(encoding="utf-8")


def _punto_json(informe, id_punto):
    return next(p for p in informe["puntos"] if p["id"] == id_punto)


def _bloque_del_punto(html, id_punto):
    """El trozo de la memoria que va de `id="punto-X"` al siguiente bloque."""
    marca = f'id="punto-{id_punto}"'
    assert marca in html, f"la memoria no trae el bloque de {id_punto}"
    desde = html.index(marca)
    siguiente = html.find('<div class="punto', desde + 1)
    return html[desde:siguiente if siguiente != -1 else len(html)]


# La coronacion del canal en C-01, que `tests/ejemplo_puntos.csv` deja vacia
# y sin la cual VC1 detiene el punto antes de que V2b pueda decidir nada. Es
# geometria del fixture (calado de 1.20 m sobre el fondo del cruce, el mismo
# par que usa `test_M5_verificaciones`), no un valor de proyecto.
CORONACION_CANAL_C01 = 38.30
FILA_C01 = "C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,"


@pytest.fixture
def csv_con_coronacion(tmp_path):
    """`ejemplo_puntos.csv` con la coronacion del canal en C-01; lo demas igual."""
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    assert FILA_C01 + "\n" in texto, "la fila C-01 del CSV de ejemplo cambio"
    ruta = tmp_path / "puntos_c01_coronacion.csv"
    ruta.write_text(texto.replace(FILA_C01 + "\n",
                                  f"{FILA_C01}{CORONACION_CANAL_C01}\n"),
                    encoding="utf-8")
    return ruta


# ===========================================================================
# 1 - La ficha: un [A] de perfil con dos opciones cerradas y valor de archivo
# ===========================================================================


def test_pf4_la_ficha_es_una_categoria_de_perfil_con_valor_umbral_duro():
    c = ca.criterio(CLAVE)
    assert c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_PERFIL
    assert c.forma == ca.FORMA_CATEGORIA
    assert c.sensibilidad == (UMBRAL_DURO, INDICADOR_CON_AVISO)
    # NO VACIO: dejarlo vacio detendria los cuatro puntos de toda corrida de
    # perfil, y esta sesion no mueve ningun numero de la linea base.
    assert c.valor == UMBRAL_DURO
    assert c.resolucion is not None, "[A] de perfil sin procedencia"
    # La segunda mitad del indicador (n de Manning del cauce natural) sigue
    # pendiente como hoy: la ficha lo dice, no lo inventa.
    assert "cauce" in (c.verificacion_pendiente or "").lower()
    assert "5.3.3" in c.fuente


@pytest.mark.parametrize("malo", ["aviso", 1, "1", True, "UMBRAL_DURO", ""])
def test_pf4_la_guardia_de_forma_rechaza_lo_que_no_es_una_de_las_dos_opciones(malo, _limpio):
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE, malo)
    assert not ca.declarado_en_caliente(CLAVE)


@pytest.mark.parametrize("bueno", [UMBRAL_DURO, INDICADOR_CON_AVISO])
def test_pf4_la_guardia_de_forma_acepta_las_dos_opciones(bueno, _limpio):
    ca.establecer_valor_dinamico(CLAVE, bueno)
    assert ca.valor(CLAVE) == bueno


# ===========================================================================
# 2 - El veredicto INDICADOR y su sitio en modelos.py
# ===========================================================================


def test_pf4_indicador_es_un_tipo_de_veredicto_y_no_una_cuarta_capa():
    assert TipoDeVeredicto.INDICADOR.value == "indicador"
    # Los cuatro de antes siguen: no se sustituye ninguno.
    assert {t.name for t in TipoDeVeredicto} == {
        "CUMPLE", "NO_CUMPLE", "DIFERIDO", "SIN_VEREDICTO", "INDICADOR"}
    # `Veredicto.cumple` sigue diciendo solo CUMPLE: un indicador disparado
    # no «cumple», aunque el punto no se detenga.
    assert not Veredicto(tipo=TipoDeVeredicto.INDICADOR).cumple


def _paso_minimo(**kw):
    """Un `PasoDeMemoria` con lo obligatorio, para probar sus guardias."""
    base = dict(que="x", por_que="y", formula="a >= b",
                sustitucion=(Magnitud("a", 1.0, "m/m", "a"),),
                resultado=Magnitud("a - b", 0.0, "m/m", "a - b"))
    base.update(kw)
    return PasoDeMemoria(**base)


def test_pf4_un_paso_con_veredicto_indicador_exige_umbral():
    """Decir que un indicador se disparo sin decir contra que es indefendible."""
    with pytest.raises(ValueError, match="sin umbral"):
        _paso_minimo(veredicto=Veredicto(tipo=TipoDeVeredicto.INDICADOR))


def test_pf4_m11_pinta_el_indicador_como_aviso_y_no_como_incumple_ni_diferido():
    umbral = Umbral(descripcion="d", valor=1.0, unidad="m/m",
                    cita_id=CITA_INDICADORES, caracter="definicion",
                    aplicacion="a")
    paso = _paso_minimo(
        umbral=umbral, citas_textuales=(CITA_INDICADORES,),
        veredicto=Veredicto(tipo=TipoDeVeredicto.INDICADOR, margen=-0.002,
                            unidad="m/m", explicacion="se disparo"))
    html = M11._veredicto_del_paso(paso)
    assert f'class="{M11.CLASE_INDICADOR}"' in html
    assert M11.MARCA_INDICADOR in html
    assert 'class="incumple"' not in html and "diferido" not in html.lower()


# ===========================================================================
# 3 - V2b bajo los dos regimenes (unidad, con el doble de M5)
# ===========================================================================


def test_pf4_bajo_umbral_duro_el_indicador_disparado_sigue_deteniendo(_limpio):
    """
    Vale ANTES y DESPUES: es la conducta de S20, que el valor del archivo
    conserva. Se escribe para que el regimen nuevo no la mueva por accidente.
    """
    punto = _punto()
    v = M5.v2b_sedimentacion(punto=punto, resultado=_resultado(S=punto.S_cauce / 2))
    assert not v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE


def test_pf4_bajo_umbral_duro_declarado_la_conducta_es_la_misma(_limpio):
    punto, v = _v2b(UMBRAL_DURO, 0.003)
    assert not v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE


def test_pf4_bajo_indicador_con_aviso_el_indicador_disparado_no_detiene(_limpio):
    punto, v = _v2b(INDICADOR_CON_AVISO, 0.003)
    assert v.cumple, "el diametro no se descarta bajo indicador_con_aviso"
    assert v.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    # El margen sigue siendo el de la comparacion: V2b se evaluo IGUAL.
    assert v.paso.veredicto.margen == pytest.approx(0.003 - punto.S_cauce, rel=REL_TRANSPORTE)
    assert v.valor_obtenido == pytest.approx(0.003, rel=REL_TRANSPORTE)
    assert v.valor_admisible == pytest.approx(punto.S_cauce, rel=REL_TRANSPORTE)
    assert "no se detiene" in v.paso.veredicto.explicacion.lower()


def test_pf4_bajo_indicador_con_aviso_sin_disparo_el_veredicto_es_cumple(_limpio):
    punto, v = _v2b(INDICADOR_CON_AVISO, _punto().S_cauce)
    assert v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE


@pytest.mark.parametrize("regimen", [UMBRAL_DURO, INDICADOR_CON_AVISO])
def test_pf4_el_paso_de_v2b_declara_el_regimen_como_eleccion_con_fundamento(regimen, _limpio):
    """La ficha que faltaba se imprime SIEMPRE, tambien bajo el valor del archivo."""
    _, v = _v2b(regimen, 0.003)
    eleccion = next(e for e in v.paso.elecciones if e.clave_criterio == CLAVE)
    assert eleccion.valor == regimen
    assert set(eleccion.entre) == {UMBRAL_DURO, INDICADOR_CON_AVISO}
    assert eleccion.fundamento_id, "la eleccion del regimen lleva Fundamento"
    fundamento = construir().fundamento(eleccion.fundamento_id)
    # Sostenido por el caracter DEFINICION de la cita: DEFINE, no obliga.
    assert fundamento.verbo.value == "define"
    assert CITA_INDICADORES in fundamento.citas
    assert CITA_INDICADORES in v.paso.citas_textuales
    # El regimen queda REGISTRADO como usado: es lo que M11 imprime.
    assert CLAVE in ca.criterios_usados()


def test_pf4_v2b_se_detiene_si_el_regimen_esta_vacio():
    with sin_valor(CLAVE):
        with pytest.raises(CriterioPendienteError) as exc:
            M5.v2b_sedimentacion(punto=_punto(), resultado=_resultado())
    assert exc.value.clave == CLAVE


def test_pf4_el_consumidor_rechaza_un_regimen_que_burla_la_puerta():
    """Segunda linea de guardia (ficha EXT-5-02), en forma MAT-D13."""
    with con_valor(CLAVE, "aviso", motivo="probar la guardia del consumidor"):
        with pytest.raises(DatoInvalidoError, match=CLAVE):
            M5.v2b_sedimentacion(punto=_punto(), resultado=_resultado())


# ===========================================================================
# 4 - La linea base no mueve un numero, y la corrida de perfil invoca el
#     criterio
# ===========================================================================


def test_pf4_con_el_valor_del_archivo_la_linea_base_ancha_no_mueve_un_numero(tmp_path):
    """
    La corrida de la linea base ancha por la CLI real contra el JSON
    comprometido: el comparador de E-B dice IGUALES punto a punto
    (diametros, HW, verificaciones, bloqueos, iteraciones), y `regimen_v2b`
    figura entre los criterios USADOS con el valor del archivo. Lo que
    difiere en bytes respecto de la linea base ANTERIOR a PF-4
    (`criterios_sha1`, `hoja_ruta_sha1`, la fila nueva de usados, la clave
    `veredicto`, el texto de `NUMERAL_V2B`) es formato: se midio con este
    mismo comparador sobre el JSON de `a96bbec` y esta declarado en el README
    de la linea base.
    """
    _, generado, _ = _correr_cli(tmp_path)
    comprometido = json.loads(INFORME_ANCHO.read_text(encoding="utf-8"))
    resultado = comparador.comparar(comprometido, generado)
    assert resultado.iguales, "\n".join(resultado.lineas())
    usados = {u["clave"]: u for u in generado["criterios"]["usados"]}
    assert CLAVE in usados
    assert usados[CLAVE]["valor"] == UMBRAL_DURO
    assert usados[CLAVE]["declarado_en_caliente"] is False
    assert ca.CRITERIOS[CLAVE].nivel == ca.NIVEL_PERFIL


def test_pf4_la_corrida_de_perfil_invoca_el_regimen_y_por_eso_es_de_perfil():
    """La misma medida que `test_cierre_perfil`: se lee del contexto de la corrida."""
    externos = cli.cargar_datos_externos(EXTERNOS_AMPLIADOS, {"luz_m": LUZ_LINEA_BASE})
    informe = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
    assert CLAVE in informe.contexto.criterios_usados
    assert ca.CRITERIOS[CLAVE].nivel == ca.NIVEL_PERFIL


# ===========================================================================
# 5 - Por la CLI: C-01 con S_conducto = 0.004 dimensiona bajo aviso
# ===========================================================================


def test_pf4_sin_declarar_c01_no_dimensiona_y_el_motivo_nombra_v2b(tmp_path, csv_con_coronacion):
    """
    Vale ANTES y DESPUES: con el valor del archivo (umbral duro) los tres
    marcos de la progresion de C-01 se descartan por V2b, que es la evidencia
    de la revision de E-B que motivo PF-4 (0.004 frente a 0.006).
    """
    _, informe, _ = _correr_cli(tmp_path, cajon=True, csv=csv_con_coronacion)
    c01 = _punto_json(informe, "C-01")
    assert not c01["dimensionado"]
    assert c01["iteraciones"] and all(
        "V2b" in it["incumplidas"] for it in c01["iteraciones"])


def test_pf4_declarando_indicador_con_aviso_c01_dimensiona_y_la_memoria_avisa(
        tmp_path, csv_con_coronacion):
    _, informe, html = _correr_cli(
        tmp_path, f"{CLAVE}={INDICADOR_CON_AVISO}", cajon=True,
        csv=csv_con_coronacion)
    c01 = _punto_json(informe, "C-01")
    assert c01["dimensionado"], c01.get("bloqueos")
    v2b = next(v for v in c01["verificaciones"] if v["codigo"] == "V2b")
    assert v2b["cumple"] is True
    assert v2b["veredicto"] == TipoDeVeredicto.INDICADOR.value
    assert v2b["valor_obtenido"] == pytest.approx(0.004, rel=REL_TRANSPORTE)
    assert v2b["valor_admisible"] == pytest.approx(0.006, rel=REL_TRANSPORTE)
    # El texto literal de la fuente sale del registro, no de una segunda
    # transcripcion: la frase esta en `Registro.textos_literales()`. Y se
    # busca DENTRO del bloque de C-01, no en cualquier parte del HTML: el
    # literal ya se imprimia en los bloques de A-01 y A-02 antes de PF-4, de
    # modo que un `in html` a secas pasaria sin que C-01 hubiera llegado
    # nunca a la Fase 5.
    literal = construir().cita(CITA_INDICADORES).texto_literal.texto
    assert literal in construir().textos_literales()
    bloque = _bloque_del_punto(html, "C-01")
    assert M11._esc(literal) in bloque
    assert M11.MARCA_INDICADOR in bloque
    # Y la FILA de V2b en la tabla de verificaciones lleva la clase del
    # aviso, no la del incumplimiento: es lo que distingue «se disparo y el
    # punto sigue» de «no cumple».
    fila = re.search(r'<tr class="([^"]*)">\s*<td>V2b</td>', bloque)
    assert fila is not None and "fila-indicador" in fila.group(1), bloque[:400]
    # Y el criterio declarado en caliente viaja con la corrida.
    declarados = {u["clave"]: u for u in informe["criterios"]["usados"]}
    assert declarados[CLAVE]["valor"] == INDICADOR_CON_AVISO


def test_pf4_la_cli_marca_el_aviso_y_no_lo_cuenta_como_incumplida(
        tmp_path, csv_con_coronacion):
    salida, informe, _ = _correr_cli(
        tmp_path, f"{CLAVE}={INDICADOR_CON_AVISO}", cajon=True,
        csv=csv_con_coronacion)
    assert cli.MARCA_INDICADOR in salida
    c01 = _punto_json(informe, "C-01")
    aceptada = next(it for it in c01["iteraciones"] if it["aceptado"])
    assert "V2b" not in aceptada["incumplidas"]


# ===========================================================================
# 6 - El barrido de PF-3 ve el cambio de veredicto, que ya no es solo `cumple`
# ===========================================================================


def test_pf4_el_barrido_del_regimen_ve_que_v2b_cambia_de_veredicto(csv_con_coronacion):
    """
    `regimen_v2b` es un [A] de perfil con ventana, o sea barrible, y su
    barrido es el caso que destapa el hueco: hasta PF-4 `barrido` leia el
    veredicto SOLO de `.cumple` (`_CAMPOS_DE_VEREDICTO`), de modo que un
    CUMPLE que pasa a INDICADOR con `cumple` en True las dos veces no
    contaba como cambio. Aqui `cumple` tambien se mueve --- el punto pasa
    de no dimensionar a dimensionar ---, y lo que el test fija es que V2b
    figure UNA vez entre las que cambian, en las dos corridas.
    """
    externos = cli.cargar_datos_externos(
        EXTERNOS_AMPLIADOS, {"luz_m": LUZ_LINEA_BASE})
    resultado = barrido.barrer(
        csv_con_coronacion, externos, cli.ALCANCE_PERFIL, CLAVE,
        [UMBRAL_DURO, INDICADOR_CON_AVISO],
        declaraciones_base=DECLARACIONES_DEL_CAJON,
        volcar=cli.informe_json)
    filas = {(f.valor, f.id_punto): f for f in resultado.filas}
    assert not filas[(UMBRAL_DURO, "C-01")].dimensionado
    assert filas[(INDICADOR_CON_AVISO, "C-01")].dimensionado
    cambian = filas[(INDICADOR_CON_AVISO, "C-01")].verificaciones_que_cambian
    assert cambian.count("V2b") == 1, cambian
    # Y el otro sentido: los puntos que no tocan el indicador no cambian.
    assert not filas[(INDICADOR_CON_AVISO, "A-01")].verificaciones_que_cambian


# ===========================================================================
# 7 - La pestaña 2 deriva el editor de categoria de la ficha
# ===========================================================================


def test_pf4_la_pestana_2_ofrece_el_editor_de_categoria_con_las_dos_opciones():
    esquema = ed.esquema_de(CLAVE)
    assert len(esquema.campos) == 1
    campo = esquema.campos[0]
    assert campo.tipo == ed.TIPO_CATEGORIA
    assert set(campo.opciones) == {UMBRAL_DURO, INDICADOR_CON_AVISO}
    # Y el filtro de alcance de la pestaña 2 lo muestra a perfil.
    assert CLAVE in ca.criterios_del_alcance(cli.ALCANCE_PERFIL)
