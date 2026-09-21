"""
tests/test_ext10_multiobra.py
=============================
La aceptacion de EXT-10: MULTI-OBRA COMO REQUISITO DE PRODUCTO (EXT-V-01) y la
fase E04 del plan de evolucion (sesion formato 3 con identidad, huella del CSV,
corridas embebidas y escritura atomica).

Escrita PRIMERO, en rojo, como manda la cadena EXT: `xfail(strict=True)` a
nivel de modulo, medida antes de tocar codigo y liberada al corregir. Los
simbolos nuevos se leen por atributo dentro de cada test y no al importar,
para que el rojo sea un fallo del test y no un error de coleccion.

Que se vigila, y por que cada cosa
----------------------------------
(a) `DatoSitio.nivel`, medido por corridas y en las dos direcciones, como
    `Criterio.nivel` (S21): la corrida de perfil no lee ningun [S] y la de
    expediente solo `PGA_roca_B`. Lo que ninguna corrida invoca se censa,
    para que el grupo no crezca en silencio.
(b) `datos_sitio.establecer_dato_dinamico`: la UNICA puerta por la que un [S]
    de otra obra entra al proceso. Pasa por `_verificar_dato` (via
    `dataclasses.replace`), exige trazabilidad no vacia y fecha, y rechaza un
    dato `Derivada`. Nunca escribe `datos_sitio.py`.
(c) DOS OBRAS DISTINTAS por la CLI (`--datos-sitio`) y por el servicio: la
    cadena sismica cambia con el PGA declarado, el JSON y la memoria dicen de
    que archivo salio cada [S], y el archivo del repositorio no se toca.
(d) UNA OBRA VACIA: `sesion.sesion_vacia()` es como se crea un proyecto
    nuevo, y aplicarla retira lo declarado sin vaciar ningun archivo.
(e) ABRIR B TRAS A: sustituye, en seco, y no hereda ni valor ni fecha.
(f) SESION FORMATO 3: migracion explicita v1/v2 -> v3, `id`, `csv_sha1`,
    `informe_json` embebido por corrida, escritura temporal + `os.replace`,
    y la CLI que compara su corrida con la embebida.
(g) La ADVERTENCIA de corredor: pura, textual, no bloquea, no va al JSON.
(h) Guardias: el contexto congelado con los campos nuevos; la GUI por AST.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import declaracion as dec
from src import sesion as ses
from src import servicio
from src import variables_entrada as ve
from src.modulos import M11_reporte as M11
from tests.apoyo.aproximacion import REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
ARCHIVO_SITIO = RAIZ / "src" / "datos_sitio.py"
GUI = RAIZ / "gui" / "app.py"
M11_ARCHIVO = RAIZ / "src" / "modulos" / "M11_reporte.py"

# Nacio con `xfail(strict=True)` en cada test que describia el estado nuevo:
# medido en rojo ANTES de tocar codigo, 63 xfailed y 0 XPASS, y liberado al
# corregir. Dos guardias nunca lo llevaron porque valen antes y despues
# (medido: XPASS en la primera corrida en rojo, y por eso se les quito):
# `criterios_bloqueantes` ya resolvia un [S] pendiente por `ca.declaracion_de`
# (SIS-A-05), y `errores_de_sesion` ya aceptaba `sitio: null` y una lista bien
# formada porque ignora las claves que no conoce.

# Las banderas de la linea base de la Familia C a alcance expediente: es la
# unica corrida de la suite que llega a la Fase 9 y por tanto la unica que
# invoca un [S]. Se leen del mismo archivo que `regenerar.sh`.
BANDERAS_EXPEDIENTE = {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
                       "L_hidraulico_m": None, "categoria_tr": None}

# Los [S] que ninguna corrida invoca --- SEIS de los nueve, medidos con
# `variables_entrada.consumido_por` ---. Su `nivel` es un ARGUMENTO escrito
# junto al campo, no una medida: `corredor_del_proyecto` no gobierna ningun
# calculo (es el ambito de los demas), la zona y el Z de E.030 son solo
# referencia (Sec. 0.4 de la hoja de ruta), y los tres del programa de
# calicatas los pide el Manual de Suelos a nivel de perfil sin que ningun
# modulo los consuma todavia. Mismo recurso que
# `test_nivel_medido.SIN_CONSUMIDOR_Y_SIN_MEDIDA`.
DATOS_SIN_CONSUMIDOR_Y_SIN_MEDIDA = ("ZONA_SISMICA_LA_UNION", "Z_E030",
                                     "corredor_del_proyecto", "carriles_por_sentido",
                                     "clase_de_via", "existe_informacion_secundaria_tramo")

FECHA = "2026-09-21"
TRAZ_A = "lectura del mapa A3 sobre la coordenada X de la obra A"
TRAZ_B = "lectura del mapa A3 sobre la coordenada Y de la obra B"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _sha1(ruta: Path) -> str:
    return hashlib.sha1(ruta.read_bytes()).hexdigest()


def _sitio(pga: float, corredor: str, trazabilidad: str) -> dict:
    return {
        "PGA_roca_B": {"valor": pga, "trazabilidad": trazabilidad, "fecha": FECHA},
        "corredor_del_proyecto": {"valor": corredor,
                                  "trazabilidad": f"expediente vial de {corredor}",
                                  "fecha": FECHA},
    }


def _escribir(tmp_path: Path, nombre: str, datos: dict) -> Path:
    ruta = tmp_path / nombre
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    return ruta


def _externos_expediente():
    return cli.cargar_datos_externos(EXTERNOS_AMPLIADOS, dict(BANDERAS_EXPEDIENTE))


def _cli(*args: str, timeout: float = 600.0) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(RAIZ / "cli.py"), *args],
                          cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def _cli_expediente(tmp_path: Path, rotulo: str, *extra: str) -> tuple:
    salida = tmp_path / f"{rotulo}.informe.json"
    hecho = _cli(str(CSV_EJEMPLO), "--luz", "2.75", "--alcance", cli.ALCANCE_EXPEDIENTE,
                 "--datos-externos", str(EXTERNOS_AMPLIADOS), "--json", str(salida),
                 *extra)
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    return hecho, json.loads(salida.read_text(encoding="utf-8"))


def _sin_marca(datos: dict) -> dict:
    copia = json.loads(json.dumps(datos))
    copia.pop("generado", None)
    copia.get("expediente", {}).pop("generado_utc", None)
    return copia


def _usado(datos: dict, clave: str) -> dict:
    return next(d for d in datos["datos_sitio"]["usados"] if d["clave"] == clave)


def _funcion(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"'{nombre}' ya no existe: el test quedo obsoleto")


def _llamadas(funcion):
    """[(nombre de la llamada, linea)] en orden de aparicion."""
    salida = []
    for nodo in ast.walk(funcion):
        if isinstance(nodo, ast.Call):
            salida.append((ast.unparse(nodo.func), nodo.lineno))
    return sorted(salida, key=lambda par: par[1])


def _primera(llamadas, sufijo):
    for nombre, linea in llamadas:
        if nombre == sufijo or nombre.endswith("." + sufijo):
            return linea
    raise AssertionError(f"ninguna llamada a {sufijo}")


@pytest.fixture(autouse=True)
def _sin_datos_de_sitio_declarados():
    """Cada test arranca y termina con el archivo gobernando."""
    limpiar = getattr(ds, "limpiar_datos_dinamicos", lambda: None)
    limpiar()
    yield
    limpiar()


# ===========================================================================
# (a) DatoSitio.nivel, medido
# ===========================================================================

def test_a_todo_dato_de_sitio_declara_nivel():
    from src.modelos import NIVELES
    for clave, dato in ds.DATOS_SITIO.items():
        assert dato.nivel in NIVELES, f"{clave} no declara nivel"


def test_a_la_guardia_rechaza_un_nivel_desconocido():
    with pytest.raises(ValueError, match="nivel"):
        replace(ds.dato("PGA_roca_B"), nivel="borrador")


def test_a_los_niveles_viven_en_modelos_y_criterios_los_reexporta():
    from src import modelos
    assert ca.NIVEL_PERFIL is modelos.NIVEL_PERFIL
    assert ca.NIVEL_EXPEDIENTE is modelos.NIVEL_EXPEDIENTE
    assert ca.NIVELES == modelos.NIVELES


def test_a_el_nivel_se_mide_en_las_dos_direcciones():
    from src.modelos import NIVEL_EXPEDIENTE, NIVEL_PERFIL
    perfil = cli.correr(CSV_EJEMPLO, _externos_expediente(), alcance=cli.ALCANCE_PERFIL)
    expediente = cli.correr(CSV_EJEMPLO, _externos_expediente(),
                            alcance=cli.ALCANCE_EXPEDIENTE)
    usados_perfil = set(perfil.contexto.datos_usados)
    usados_expediente = set(expediente.contexto.datos_usados)
    # El radio medido por el dictamen, comprobado y no copiado.
    assert usados_perfil == set()
    assert usados_expediente == {"PGA_roca_B"}
    # marcado PERFIL -> la corrida de perfil TIENE que invocarlo, salvo lo que
    # ninguna corrida puede invocar (sin consumidor: nivel argumentado).
    for clave, dato in ds.DATOS_SITIO.items():
        if dato.nivel == NIVEL_PERFIL and clave not in DATOS_SIN_CONSUMIDOR_Y_SIN_MEDIDA:
            assert clave in usados_perfil, f"{clave} dice perfil y perfil no lo invoca"
    # marcado EXPEDIENTE -> la corrida de perfil NO puede invocarlo.
    for clave in usados_perfil:
        assert ds.dato(clave).nivel == NIVEL_PERFIL
    for clave in usados_expediente - usados_perfil:
        assert ds.dato(clave).nivel == NIVEL_EXPEDIENTE


def test_a_el_censo_de_lo_que_no_se_puede_medir_no_crece_en_silencio():
    # M11 no es un modulo de calculo: lee `corredor_del_proyecto` del
    # contexto para IMPRIMIRLO, y `variables_entrada` lo cuenta como
    # consumidor por la cadena literal. Lo que mide el nivel es quien lo
    # invoca por `valor()`, y eso solo lo hace un modulo de calculo.
    sin_consumidor = tuple(sorted(
        clave for clave in ds.DATOS_SITIO
        if not set(ve.variable(clave).consumido_por) - {"M11_reporte"}))
    assert sin_consumidor == tuple(sorted(DATOS_SIN_CONSUMIDOR_Y_SIN_MEDIDA))


# ===========================================================================
# (b) establecer_dato_dinamico: la unica puerta
# ===========================================================================

def test_b_un_dato_declarado_gobierna_y_registra_su_uso():
    huella = _sha1(ARCHIVO_SITIO)
    ds.reiniciar_usos()
    ds.establecer_dato_dinamico("PGA_roca_B", 0.30, TRAZ_B, FECHA, origen="sitio_B.json")
    assert ds.valor("PGA_roca_B") == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert ds.datos_usados() == ["PGA_roca_B"]
    efectivo = ds.dato_efectivo("PGA_roca_B")
    assert efectivo.valor == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert efectivo.trazabilidad == TRAZ_B
    assert efectivo.concepto == ds.dato("PGA_roca_B").concepto
    assert ds.origen_de("PGA_roca_B") == "sitio_B.json"
    assert ds.origen_de("Z_E030") == ds.ORIGEN_ARCHIVO
    # El archivo dice lo mismo que antes, y su huella tambien.
    assert ds.dato("PGA_roca_B").valor == pytest.approx(0.50, rel=REL_TRANSPORTE)
    assert _sha1(ARCHIVO_SITIO) == huella


@pytest.mark.parametrize("clave,valor,trazabilidad,fecha,excepcion,texto", [
    ("PGA_roca_B", 0.30, "", FECHA, ValueError, "trazabilidad"),
    ("PGA_roca_B", 0.30, "   ", FECHA, ValueError, "trazabilidad"),
    ("PGA_roca_B", None, TRAZ_B, FECHA, ValueError, "None"),
    ("PGA_roca_B", 0.30, TRAZ_B, "", ValueError, "fecha"),
    ("PGA_roca_B", float("inf"), TRAZ_B, FECHA, ValueError, "infinito"),
    ("Z_E030", 0.35, TRAZ_B, FECHA, ValueError, "ZONA_SISMICA_LA_UNION"),
    ("dato_que_no_existe", 1.0, TRAZ_B, FECHA, KeyError, "datos_sitio.py"),
])
def test_b_la_puerta_rechaza_lo_que_el_archivo_rechazaria(clave, valor, trazabilidad,
                                                          fecha, excepcion, texto):
    with pytest.raises(excepcion, match=texto):
        ds.establecer_dato_dinamico(clave, valor, trazabilidad, fecha, origen="prueba")
    assert ds.datos_dinamicos() == {}, "un rechazo no deja nada escrito"


def test_b_quitar_y_limpiar_devuelven_el_archivo():
    ds.establecer_dato_dinamico("PGA_roca_B", 0.30, TRAZ_B, FECHA, origen="p")
    ds.establecer_dato_dinamico("carriles_por_sentido", 2, "plano de secciones", FECHA,
                                origen="p")
    assert ds.datos_declarados_en_caliente() == ["PGA_roca_B", "carriles_por_sentido"]
    # Pisar un valor del archivo no es lo mismo que rellenar un vacio.
    assert ds.datos_pisados_en_caliente() == ["PGA_roca_B"]
    assert "carriles_por_sentido" not in ds.datos_sin_valor()
    ds.quitar_dato_dinamico("PGA_roca_B")
    assert ds.valor("PGA_roca_B") == pytest.approx(0.50, rel=REL_TRANSPORTE)
    ds.limpiar_datos_dinamicos()
    assert "carriles_por_sentido" in ds.datos_sin_valor()
    assert ds.datos_dinamicos() == {}


def test_b_el_reporte_de_texto_dice_de_donde_salio_cada_dato():
    ds.establecer_dato_dinamico("PGA_roca_B", 0.30, TRAZ_B, FECHA, origen="sitio_B.json")
    informe = cli.correr(CSV_EJEMPLO, _externos_expediente())
    texto = cli.volcar(informe, con_criterios=True)
    assert "sitio_B.json" in texto
    assert TRAZ_B in texto
    assert "0.3" in texto


# ===========================================================================
# (c) Dos obras distintas
# ===========================================================================

def test_c_dos_obras_por_la_cli_dan_dos_cadenas_sismicas_y_dicen_su_origen(tmp_path):
    huella = _sha1(ARCHIVO_SITIO)
    sitio_a = _escribir(tmp_path, "sitio_A.json", _sitio(0.40, "Obra A, km 0-4", TRAZ_A))
    sitio_b = _escribir(tmp_path, "sitio_B.json", _sitio(0.30, "Obra B, km 10-12", TRAZ_B))
    _, json_a = _cli_expediente(tmp_path, "A", "--datos-sitio", str(sitio_a))
    _, json_b = _cli_expediente(tmp_path, "B", "--datos-sitio", str(sitio_b))
    _, json_repo = _cli_expediente(tmp_path, "repo")

    cadena = lambda d: d["cabezal"]["cadena_sismica"]  # noqa: E731
    assert cadena(json_a)["PGA"] == pytest.approx(0.40, rel=REL_TRANSPORTE)
    assert cadena(json_b)["PGA"] == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert cadena(json_repo)["PGA"] == pytest.approx(0.50, rel=REL_TRANSPORTE)
    assert cadena(json_a)["A_s"] != pytest.approx(cadena(json_b)["A_s"], rel=REL_TRANSPORTE)

    assert _usado(json_a, "PGA_roca_B")["origen"].endswith("sitio_A.json")
    assert _usado(json_a, "PGA_roca_B")["trazabilidad"] == TRAZ_A
    assert _usado(json_a, "PGA_roca_B")["fecha"] == FECHA
    assert _usado(json_a, "PGA_roca_B")["declarado_en_caliente"] is True
    assert _usado(json_repo, "PGA_roca_B")["origen"] == ds.ORIGEN_ARCHIVO
    assert _usado(json_repo, "PGA_roca_B")["declarado_en_caliente"] is False
    assert json_b["expediente"]["corredor_del_proyecto"] == {
        "valor": "Obra B, km 10-12", "origen": str(sitio_b)}
    assert json_repo["expediente"]["corredor_del_proyecto"]["valor"] == ds.CORREDOR_DEL_PROYECTO
    assert json_a["datos_sitio"]["declarados_en_caliente"] == ["PGA_roca_B",
                                                              "corredor_del_proyecto"]
    assert _sha1(ARCHIVO_SITIO) == huella


def test_c_la_memoria_imprime_el_origen_y_el_corredor_de_cada_obra(tmp_path):
    sitio_b = _escribir(tmp_path, "sitio_B.json", _sitio(0.30, "Obra B, km 10-12", TRAZ_B))
    html = tmp_path / "B.html"
    hecho, _ = _cli_expediente(tmp_path, "B", "--datos-sitio", str(sitio_b),
                               "--proyecto", "Obra B", "--html", str(html))
    memoria = html.read_text(encoding="utf-8")
    assert "sitio_B.json" in memoria
    assert TRAZ_B in memoria
    assert "Obra B, km 10-12" in memoria
    assert "declarado (sesi" in memoria          # rotulo del [S] pisado
    assert "0.50" in memoria or "0.5" in memoria  # lo que el archivo dice, al lado
    assert "Advertencia de corredor" not in memoria


def _sesion_con(tmp_path: Path, nombre: str, **campos) -> Path:
    """
    Una sesion v3 con los criterios que la corrida de pruebas tiene
    declarados (`conftest`), para que el subproceso de la CLI calcule la
    MISMA obra que este proceso: es lo que `test_ext8` hace con
    `dec.estado_de_sesion()`, y sin ello las dos puertas no son comparables.
    """
    sesion = ses.sesion_vacia("1.0")
    sesion.update({"csv": str(CSV_EJEMPLO), "datos_externos": str(EXTERNOS_AMPLIADOS),
                   "externos": {"luz_m": "2,75"}, "alcance": cli.ALCANCE_EXPEDIENTE,
                   "criterios": dec.estado_de_sesion()})
    sesion.update(campos)
    return _escribir(tmp_path, nombre, sesion)


def test_c_las_dos_puertas_producen_el_mismo_json_con_sitio(tmp_path):
    sitio_a = _escribir(tmp_path, "sitio_A.json", _sitio(0.40, "Obra A, km 0-4", TRAZ_A))
    ruta_sesion = _sesion_con(tmp_path, "sesion_A.json")
    salida = tmp_path / "A.json"
    hecho = _cli("--sesion", str(ruta_sesion), "--datos-sitio", str(sitio_a),
                 "--json", str(salida))
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    por_cli = json.loads(salida.read_text(encoding="utf-8"))
    resultado = servicio.cargar_datos_sitio(sitio_a)
    assert set(resultado.restaurados) == {"PGA_roca_B", "corredor_del_proyecto"}
    assert not resultado.rechazados
    por_servicio = cli.informe_json(servicio.correr(CSV_EJEMPLO, _externos_expediente()))
    assert _sin_marca(json.loads(json.dumps(por_servicio))) == _sin_marca(por_cli)


def test_c_un_sitio_json_con_una_clave_mala_se_rechaza_entero_y_sin_traza(tmp_path):
    malo = _sitio(0.40, "Obra A", TRAZ_A)
    malo["PGA_rocaB"] = malo.pop("PGA_roca_B")          # clave mal escrita
    ruta = _escribir(tmp_path, "malo.json", malo)
    hecho = _cli(str(CSV_EJEMPLO), "--luz", "2.75", "--datos-sitio", str(ruta),
                 "--json", str(tmp_path / "x.json"))
    assert hecho.returncode == 2
    assert "Traceback" not in hecho.stderr
    assert "PGA_rocaB" in hecho.stderr
    assert not (tmp_path / "x.json").exists()
    # Y en proceso: nada queda a medias, ni la clave buena.
    with pytest.raises(ValueError, match="PGA_rocaB"):
        servicio.cargar_datos_sitio(ruta)
    assert ds.datos_dinamicos() == {}


@pytest.mark.parametrize("defecto,texto", [
    ({"PGA_roca_B": {"valor": 0.4, "fecha": FECHA}}, "trazabilidad"),
    ({"PGA_roca_B": {"valor": 0.4, "trazabilidad": TRAZ_A}}, "fecha"),
    ({"Z_E030": {"valor": 0.4, "trazabilidad": TRAZ_A, "fecha": FECHA}}, "deriva"),
    ({"PGA_roca_B": 0.4}, "objeto"),
    ([1, 2], "objeto"),
])
def test_c_la_forma_del_sitio_json_se_exige_entera(tmp_path, defecto, texto):
    ruta = _escribir(tmp_path, "sitio.json", defecto)
    with pytest.raises(ValueError, match=texto):
        servicio.cargar_datos_sitio(ruta)
    assert ds.datos_dinamicos() == {}


# ===========================================================================
# (d) Una obra vacia
# ===========================================================================

def test_d_la_sesion_vacia_es_una_sesion_v3_valida_con_identidad():
    vacia = ses.sesion_vacia("1.0")
    assert ses.errores_de_sesion(vacia) == []
    assert vacia["formato_version"] == ses.FORMATO_SESION == 3
    assert vacia["id"] and vacia["id"] != ses.sesion_vacia("1.0")["id"]
    assert vacia["proyecto"] == vacia["csv"] == vacia["datos_externos"] == ""
    assert vacia["datos_sitio"] == ""
    assert vacia["sitio"] == {"valores": {}}
    assert vacia["criterios"] == {"valores": {}, "procedencias": {}}
    assert vacia["corridas"] == [] and vacia["csv_sha1"] == ""
    assert vacia["alcance"] == cli.ALCANCE_EXPEDIENTE
    assert ses.migrar_a_actual(vacia) == (vacia, [])


def test_d_abrir_la_obra_vacia_retira_lo_declarado_sin_vaciar_el_archivo():
    huella = _sha1(ARCHIVO_SITIO)
    ds.establecer_dato_dinamico("PGA_roca_B", 0.40, TRAZ_A, FECHA, origen="A")
    ds.establecer_dato_dinamico("corredor_del_proyecto", "Obra A", "expediente A", FECHA,
                                origen="A")
    vacia = ses.sesion_vacia("1.0")
    resultado = dec.restaurar_datos_de_sitio(vacia["sitio"], sustituir=True,
                                             origen="sesion vacia")
    assert resultado.restaurados == ()
    assert set(resultado.retirados) == {"PGA_roca_B", "corredor_del_proyecto"}
    assert ds.datos_dinamicos() == {}
    assert dec.estado_de_sitio_de_sesion() == {"valores": {}}
    informe = cli.correr(CSV_EJEMPLO, _externos_expediente())
    assert informe.contexto.datos_efectivos["PGA_roca_B"].origen == ds.ORIGEN_ARCHIVO
    assert informe.contexto.datos_efectivos["PGA_roca_B"].valor == pytest.approx(0.50, rel=REL_TRANSPORTE)
    assert _sha1(ARCHIVO_SITIO) == huella


# ===========================================================================
# (e) Abrir B tras A
# ===========================================================================

def test_e_abrir_B_tras_A_sustituye_y_no_hereda():
    bloque_a = {"valores": _sitio(0.40, "Obra A", TRAZ_A)}
    bloque_b = {"valores": {"PGA_roca_B": {"valor": 0.30, "trazabilidad": TRAZ_B,
                                           "fecha": "2026-09-22"}}}
    dec.restaurar_datos_de_sitio(bloque_a, sustituir=True, origen="sesion A")
    assert ds.origen_de("corredor_del_proyecto") == "sesion A"
    resultado = dec.restaurar_datos_de_sitio(bloque_b, sustituir=True, origen="sesion B")
    assert resultado.restaurados == ("PGA_roca_B",)
    assert resultado.retirados == ("corredor_del_proyecto",)
    assert not resultado.rechazados
    assert ds.valor("PGA_roca_B") == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert ds.dato_efectivo("PGA_roca_B").trazabilidad == TRAZ_B
    assert ds.datos_dinamicos()["PGA_roca_B"].fecha == "2026-09-22"
    assert ds.origen_de("PGA_roca_B") == "sesion B"
    # El corredor volvio al archivo: B no lo trae, y el de A no se hereda.
    assert ds.origen_de("corredor_del_proyecto") == ds.ORIGEN_ARCHIVO
    assert ds.valor("corredor_del_proyecto") == ds.CORREDOR_DEL_PROYECTO


def test_e_un_candidato_rechazado_no_deja_la_sesion_a_medias():
    dec.restaurar_datos_de_sitio({"valores": _sitio(0.40, "Obra A", TRAZ_A)},
                                 sustituir=True, origen="sesion A")
    bloque_b = {"valores": {
        "PGA_roca_B": {"valor": 0.30, "trazabilidad": TRAZ_B, "fecha": FECHA},
        "Z_E030": {"valor": 0.35, "trazabilidad": "x", "fecha": FECHA},   # Derivada
        "corredor_del_proyecto": {"valor": "Obra B", "trazabilidad": "y"},  # sin fecha
    }}
    resultado = dec.restaurar_datos_de_sitio(bloque_b, sustituir=True, origen="sesion B")
    assert resultado.restaurados == ("PGA_roca_B",)
    assert {clave for clave, _ in resultado.rechazados} == {"Z_E030", "corredor_del_proyecto"}
    assert all(motivo for _, motivo in resultado.rechazados)
    # Lo rechazado no entra, y lo que A traia y B no acepta se retira: la
    # fecha de A no sobrevive en una clave que B trae sin fecha.
    assert set(ds.datos_dinamicos()) == {"PGA_roca_B"}
    assert "corredor_del_proyecto" in resultado.retirados


def test_e_un_bloque_deformado_se_rechaza_antes_de_tocar_nada():
    dec.restaurar_datos_de_sitio({"valores": _sitio(0.40, "Obra A", TRAZ_A)},
                                 sustituir=True, origen="sesion A")
    for malo in ([1], {"valores": [1]}, "texto"):
        with pytest.raises(ValueError, match="objeto"):
            dec.restaurar_datos_de_sitio(malo, sustituir=True, origen="B")
    assert set(ds.datos_dinamicos()) == {"PGA_roca_B", "corredor_del_proyecto"}


# ===========================================================================
# (f) Sesion formato 3
# ===========================================================================

def test_f_el_esquema_v3_tiene_las_claves_de_E04():
    for clave, tipo in (("id", str), ("datos_sitio", str), ("sitio", dict),
                        ("csv_sha1", str), ("corridas", list)):
        assert ses.ESQUEMA_SESION[clave] is tipo
    assert ses.errores_de_sesion({}) == []


@pytest.mark.parametrize("sesion_vieja,version", [
    ({"proyecto": "obra v1", "csv": "x.csv"}, 1),
    ({"formato_version": 2, "proyecto": "obra v2", "csv": "x.csv", "alcance": "perfil",
      "criterios": {"valores": {}, "procedencias": {}}}, 2),
])
def test_f_la_migracion_es_explicita_y_completa_lo_que_falta(sesion_vieja, version):
    migrada, avisos = ses.migrar_a_actual(sesion_vieja)
    assert migrada is not sesion_vieja and "id" not in sesion_vieja
    assert migrada["formato_version"] == 3
    assert migrada["proyecto"] == sesion_vieja["proyecto"]
    assert migrada["id"] and migrada["sitio"] == {"valores": {}}
    assert migrada["datos_sitio"] == "" and migrada["corridas"] == []
    assert migrada["csv_sha1"] == ""
    if version == 1:
        assert migrada["alcance"] == cli.ALCANCE_EXPEDIENTE
        assert migrada["criterios"] == {"valores": {}, "procedencias": {}}
    assert avisos and any(f"v{version}" in aviso for aviso in avisos)
    assert any("id" in aviso for aviso in avisos)
    assert ses.errores_de_sesion(migrada) == []


def test_f_una_sesion_v3_completa_no_se_toca_y_una_incompleta_se_completa():
    completa = ses.sesion_vacia("1.0")
    assert ses.migrar_a_actual(completa) == (completa, [])
    incompleta = {"formato_version": 3, "proyecto": "x"}
    migrada, avisos = ses.migrar_a_actual(incompleta)
    assert migrada["id"] and migrada["sitio"] == {"valores": {}} and avisos


@pytest.mark.parametrize("datos", [{"formato_version": "2"}, {"formato_version": 4},
                                   {"formato_version": True}, [1, 2]])
def test_f_una_version_que_no_se_puede_migrar_es_ValueError(datos):
    with pytest.raises(ValueError):
        ses.migrar_a_actual(datos)


@pytest.mark.parametrize("data", [
    {"sitio": []},
    {"sitio": {"valores": None}},
    {"sitio": {"valores": {"PGA_roca_B": 0.4}}},
    {"sitio": {"valores": {"PGA_roca_B": {"valor": 0.4}}}},
    {"corridas": {}},
    {"corridas": [1]},
    {"corridas": [{"informe_json": 3}]},
    {"id": 7},
    {"csv_sha1": None},
])
def test_f_el_esquema_valida_el_interior_de_sitio_y_corridas(data):
    assert ses.errores_de_sesion(data)


def test_f_sitio_nulo_y_corridas_bien_formadas_pasan():
    assert ses.errores_de_sesion({"sitio": None}) == []
    assert ses.errores_de_sesion({
        "sitio": {"valores": {"PGA_roca_B": {"valor": 0.4, "trazabilidad": "t",
                                             "fecha": FECHA}}},
        "corridas": [{"generado_utc": "x", "alcance": "perfil", "csv_sha1": "a",
                      "criterios_sha1": "b", "informe_json": {}}]}) == []


def test_f_la_escritura_es_atomica(tmp_path, monkeypatch):
    destino = tmp_path / "sesion.json"
    ses.escribir_json_atomico(destino, {"a": 1})
    assert json.loads(destino.read_text(encoding="utf-8")) == {"a": 1}
    original = destino.read_bytes()

    def _revienta(*a, **k):
        raise OSError("disco lleno a mitad de la escritura")

    monkeypatch.setattr(ses.json, "dump", _revienta)
    with pytest.raises(OSError):
        ses.escribir_json_atomico(destino, {"a": 2})
    assert destino.read_bytes() == original, "el archivo anterior no se toco"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["sesion.json"], (
        "no queda ningun temporal")


def test_f_la_sesion_de_la_gui_lleva_id_huella_sitio_y_corridas(tmp_path):
    from tests.test_gui_contrato import _con_doble_de_tkinter
    app = _con_doble_de_tkinter()
    import gui.exportacion_pdf as expdf

    ds.establecer_dato_dinamico("PGA_roca_B", 0.30, TRAZ_B, FECHA, origen="sitio_B.json")
    informe = cli.correr(CSV_EJEMPLO, _externos_expediente())
    volcado = cli.informe_json(informe)
    corrida = ses.corrida_para_sesion(informe, volcado)
    assert corrida["csv_sha1"] == informe.contexto.csv_sha1
    assert corrida["criterios_sha1"] == informe.contexto.criterios_sha1
    assert corrida["alcance"] == informe.alcance
    assert corrida["generado_utc"] == informe.generado
    assert corrida["informe_json"] == volcado

    sesion = expdf.sesion_de_la_corrida(
        informe, proyecto="Obra B", csv=str(CSV_EJEMPLO), datos_externos="",
        datos_sitio="sitio_B.json", externos={"luz_m": "2,75"},
        alcance=cli.ALCANCE_EXPEDIENTE, formato_version=ses.FORMATO_SESION,
        app_version="1.0", id_sesion="abc")
    assert ses.errores_de_sesion(json.loads(json.dumps(sesion))) == []
    assert sesion["id"] == "abc"
    assert sesion["csv_sha1"] == informe.contexto.csv_sha1
    assert sesion["datos_sitio"] == "sitio_B.json"
    pga = sesion["sitio"]["valores"]["PGA_roca_B"]
    assert pga["valor"] == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert (pga["trazabilidad"], pga["fecha"]) == (TRAZ_B, FECHA)
    assert sesion["corridas"] == []
    # La ventana arma el MISMO conjunto de claves (leido de su AST).
    arbol = ast.parse(GUI.read_text(encoding="utf-8-sig"))
    funcion = _funcion(arbol, "_datos_de_sesion")
    claves_gui = None
    for nodo in ast.walk(funcion):
        if (isinstance(nodo, ast.Assign) and isinstance(nodo.targets[0], ast.Name)
                and nodo.targets[0].id == "data" and isinstance(nodo.value, ast.Dict)):
            claves_gui = {c.value for c in nodo.value.keys if isinstance(c, ast.Constant)}
    assert claves_gui == set(sesion) == set(ses.ESQUEMA_SESION)
    assert app.FORMATO_SESION == 3


def test_f_la_cli_repone_el_sitio_de_la_sesion_y_la_bandera_escrita_gana(tmp_path):
    sesion = ses.sesion_vacia("1.0")
    sesion.update({"proyecto": "Obra B", "csv": str(CSV_EJEMPLO),
                   "datos_externos": str(EXTERNOS_AMPLIADOS),
                   "externos": {"luz_m": "2,75"}, "alcance": cli.ALCANCE_EXPEDIENTE,
                   "sitio": {"valores": _sitio(0.30, "Obra B", TRAZ_B)}})
    ruta_sesion = _escribir(tmp_path, "sesion_B.json", sesion)
    salida = tmp_path / "b.json"
    hecho = _cli("--sesion", str(ruta_sesion), "--json", str(salida))
    assert hecho.returncode in (0, 1), hecho.stderr
    datos = json.loads(salida.read_text(encoding="utf-8"))
    assert datos["cabezal"]["cadena_sismica"]["PGA"] == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert "sesion_B.json" in _usado(datos, "PGA_roca_B")["origen"]
    assert "PGA_roca_B" in hecho.stdout and "datos_sitio.py no se modifico" in hecho.stdout
    # La bandera escrita gana al bloque de la sesion.
    sitio_c = _escribir(tmp_path, "sitio_C.json", _sitio(0.20, "Obra C", "traz C"))
    hecho = _cli("--sesion", str(ruta_sesion), "--datos-sitio", str(sitio_c),
                 "--json", str(salida))
    assert hecho.returncode in (0, 1), hecho.stderr
    datos = json.loads(salida.read_text(encoding="utf-8"))
    assert datos["cabezal"]["cadena_sismica"]["PGA"] == pytest.approx(0.20, rel=REL_TRANSPORTE)
    assert _usado(datos, "PGA_roca_B")["origen"].endswith("sitio_C.json")


def test_f_la_cli_compara_su_corrida_con_la_embebida_en_la_sesion(tmp_path):
    informe = cli.correr(CSV_EJEMPLO, _externos_expediente())
    volcado = json.loads(json.dumps(cli.informe_json(informe), allow_nan=False))
    corridas = [ses.corrida_para_sesion(informe, volcado)]
    ruta = _sesion_con(tmp_path, "sesion.json", csv_sha1=informe.contexto.csv_sha1,
                       corridas=corridas)
    hecho = _cli("--sesion", str(ruta), "--json", str(tmp_path / "a.json"))
    assert hecho.returncode in (0, 1), hecho.stderr
    assert "Esta corrida REPRODUCE" in hecho.stdout
    assert "Esta corrida DIFIERE" not in hecho.stdout
    # Mutar la corrida guardada: la CLI lo dice, y no se detiene.
    corridas[0]["informe_json"]["expediente"]["dimensionados"] = 99
    ruta = _sesion_con(tmp_path, "sesion_mutada.json", csv_sha1=informe.contexto.csv_sha1,
                       corridas=corridas)
    hecho = _cli("--sesion", str(ruta), "--json", str(tmp_path / "b.json"))
    assert hecho.returncode in (0, 1), hecho.stderr
    assert "Esta corrida DIFIERE" in hecho.stdout


def test_f_la_cli_avisa_de_la_migracion_y_conserva_el_id(tmp_path):
    sesion_v2 = {"formato_version": 2, "app_version": "1.0", "proyecto": "obra v2",
                 "csv": str(CSV_EJEMPLO), "datos_externos": str(EXTERNOS_AMPLIADOS),
                 "externos": {"luz_m": "2,75"}, "alcance": cli.ALCANCE_PERFIL,
                 "criterios": {"valores": {}, "procedencias": {}}}
    ruta = _escribir(tmp_path, "v2.json", sesion_v2)
    cargada = cli.cargar_sesion_serializada(ruta)
    assert cargada.formato_version == 3
    assert cargada.id and cargada.avisos and any("v2" in a for a in cargada.avisos)
    assert cargada.sitio == {"valores": {}} and cargada.datos_sitio is None
    v3 = ses.sesion_vacia("1.0")
    v3.update({"csv": str(CSV_EJEMPLO), "id": "id-fijo"})
    cargada = cli.cargar_sesion_serializada(_escribir(tmp_path, "v3.json", v3))
    assert cargada.id == "id-fijo" and cargada.avisos == ()


def test_f_el_hijo_del_pdf_reproduce_la_corrida_con_el_sitio_de_la_sesion(tmp_path):
    if not M11.weasyprint_disponible():
        pytest.skip("weasyprint no esta operativo en este interprete")
    import gui.exportacion_pdf as expdf
    from tests.test_ext8_rendimiento_gui import _csv_de_un_punto, _esperar

    csv = _csv_de_un_punto(tmp_path)
    sesion = ses.sesion_vacia("1.0")
    sesion.update({"proyecto": "Obra B", "csv": str(csv),
                   "datos_externos": str(EXTERNOS_AMPLIADOS),
                   "externos": {"luz_m": "2,75"}, "alcance": cli.ALCANCE_EXPEDIENTE,
                   "criterios": dec.estado_de_sesion(),
                   "sitio": {"valores": _sitio(0.30, "Obra B", TRAZ_B)}})
    dec.restaurar_datos_de_sitio(sesion["sitio"], sustituir=True, origen="sesion")
    propio = cli.informe_json(cli.correr(csv, _externos_expediente()))
    ds.limpiar_datos_dinamicos()
    proceso = expdf.ProcesoPdf(sesion=sesion, destino=tmp_path / "m.pdf",
                               plantilla=cli.plantilla_por_alcance(cli.ALCANCE_EXPEDIENTE),
                               directorio_trabajo=tmp_path / "trabajo",
                               interprete=sys.executable, raiz=RAIZ)
    proceso.iniciar()
    assert _esperar(proceso) is expdf.EstadoPdf.TERMINADO, proceso.detalle
    ajeno = json.loads(proceso.ruta_json.read_text(encoding="utf-8"))
    propio_json = json.loads(json.dumps(propio, ensure_ascii=False, allow_nan=False))
    assert ajeno["cabezal"]["cadena_sismica"]["PGA"] == pytest.approx(0.30, rel=REL_TRANSPORTE)
    # El origen es lo unico que difiere: el hijo lo lee de SU sesion.
    for volcado in (propio_json, ajeno):
        for usado in volcado["datos_sitio"]["usados"]:
            usado["origen"] = "<origen>"
        volcado["expediente"]["corredor_del_proyecto"]["origen"] = "<origen>"
    assert expdf.sin_marca_de_tiempo(propio_json) == expdf.sin_marca_de_tiempo(ajeno)


# ===========================================================================
# (g) La advertencia de corredor
# ===========================================================================

@pytest.mark.parametrize("proyecto,corredor", [
    ("", "terraplen de ~5 km"),
    ("Obra B", "Obra B, km 10-12"),
    ("Vía de evitamiento - tramo 2", "VIA DE EVITAMIENTO"),
    ("  obra   b ", "corredor de la OBRA B"),
])
def test_g_no_advierte_sin_proyecto_ni_cuando_uno_contiene_al_otro(proyecto, corredor):
    assert ds.advertencia_de_corredor(proyecto, corredor, "archivo") is None


def test_g_advierte_cuando_no_coinciden_y_dice_de_donde_salio_el_corredor():
    texto = ds.advertencia_de_corredor("Via de evitamiento", "terraplen de ~5 km", "sitio.json")
    assert texto and "Via de evitamiento" in texto and "terraplen de ~5 km" in texto
    assert "sitio.json" in texto and "--datos-sitio" in texto
    assert texto == ds.advertencia_de_corredor("Via de evitamiento", "terraplen de ~5 km",
                                               "sitio.json")


def test_g_la_advertencia_llega_a_la_consola_y_a_la_memoria_pero_no_al_json(tmp_path):
    html = tmp_path / "x.html"
    hecho, datos = _cli_expediente(tmp_path, "x", "--proyecto", "Otra obra",
                                   "--html", str(html))
    assert "Otra obra" in hecho.stdout and ds.CORREDOR_DEL_PROYECTO in hecho.stdout
    memoria = html.read_text(encoding="utf-8")
    assert "Advertencia de corredor" in memoria
    assert "advertencia" not in json.dumps(datos).lower()
    hecho, _ = _cli_expediente(tmp_path, "y")
    assert "Advertencia de corredor" not in hecho.stdout


def test_g_M11_formatea_la_advertencia_y_no_la_calcula():
    fuente = M11_ARCHIVO.read_text(encoding="utf-8-sig")
    arbol = ast.parse(fuente)
    nombres = {ast.unparse(n.func) for n in ast.walk(arbol) if isinstance(n, ast.Call)}
    assert not any(n.endswith(".casefold") or n.endswith(".lower") and "corredor" in n
                   for n in nombres)
    assert "unicodedata" not in fuente
    assert "ds.advertencia_de_corredor" in nombres


# ===========================================================================
# (h) Guardias
# ===========================================================================

def test_h_el_contexto_lleva_los_datos_de_sitio_efectivos_y_esta_congelado():
    from dataclasses import FrozenInstanceError

    from src.modelos import DatoEfectivoDeSitio

    ds.establecer_dato_dinamico("PGA_roca_B", 0.30, TRAZ_B, FECHA, origen="sitio_B.json")
    informe = cli.correr(CSV_EJEMPLO, _externos_expediente())
    contexto = informe.contexto
    assert set(contexto.datos_efectivos) == set(ds.DATOS_SITIO)
    efectivo = contexto.datos_efectivos["PGA_roca_B"]
    assert isinstance(efectivo, DatoEfectivoDeSitio)
    assert efectivo.valor == pytest.approx(0.30, rel=REL_TRANSPORTE) and efectivo.origen == "sitio_B.json"
    assert efectivo.fecha == FECHA and efectivo.declarado_en_caliente is True
    assert contexto.datos_declarados_en_caliente == ("PGA_roca_B",)
    assert contexto.datos_pisados_en_caliente == ("PGA_roca_B",)
    assert set(contexto.datos_sin_valor) == set(ds.datos_sin_valor())
    assert contexto.dato_efectivo("Z_E030").origen == ds.ORIGEN_ARCHIVO
    with pytest.raises(TypeError):
        contexto.datos_efectivos["PGA_roca_B"] = None
    with pytest.raises(FrozenInstanceError):
        efectivo.valor = 1.0
    # Declarar DESPUES de correr no mueve la foto ni el JSON.
    antes = json.dumps(cli.informe_json(informe), sort_keys=True)
    ds.establecer_dato_dinamico("PGA_roca_B", 0.25, "otra", FECHA, origen="z")
    assert json.dumps(cli.informe_json(informe), sort_keys=True) == antes
    assert contexto.datos_efectivos["PGA_roca_B"].valor == pytest.approx(0.30, rel=REL_TRANSPORTE)


def test_h_el_json_lee_los_sin_valor_de_la_foto_y_no_del_estado_vivo():
    ds.establecer_dato_dinamico("carriles_por_sentido", 2, "plano", FECHA, origen="s")
    informe = cli.correr(CSV_EJEMPLO, _externos_expediente())
    assert "carriles_por_sentido" not in cli.informe_json(informe)["datos_sitio"][
        "sin_valor_declarados"]
    ds.limpiar_datos_dinamicos()
    assert "carriles_por_sentido" not in cli.informe_json(informe)["datos_sitio"][
        "sin_valor_declarados"], "la foto no cambia con el estado vivo"


def test_h_criterios_bloqueantes_resuelve_tambien_un_dato_de_sitio_pendiente(monkeypatch):
    monkeypatch.setitem(ds.DATOS_SITIO, "PGA_roca_B",
                        replace(ds.DATOS_SITIO["PGA_roca_B"], valor=None))
    informe = cli.correr(CSV_EJEMPLO, _externos_expediente())
    claves = {c.clave for c in M11.criterios_bloqueantes(informe)}
    assert "PGA_roca_B" in claves
    bloqueante = next(c for c in M11.criterios_bloqueantes(informe) if c.clave == "PGA_roca_B")
    assert bloqueante.etiqueta == "S" and bloqueante.fuente


def test_h_la_gui_carga_declara_y_guarda_por_las_puertas_nuevas():
    arbol = ast.parse(GUI.read_text(encoding="utf-8-sig"))
    ejecutar = _llamadas(_funcion(arbol, "ejecutar_pipeline"))
    assert _primera(ejecutar, "_declarar_datos_de_sitio") < _primera(ejecutar, "correr")
    declarar = _llamadas(_funcion(arbol, "_declarar_datos_de_sitio"))
    assert any(n.endswith("cargar_datos_sitio") for n, _ in declarar)
    cargar = _llamadas(_funcion(arbol, "cargar_sesion"))
    errores = _primera(cargar, "errores_de_sesion")
    migrar = _primera(cargar, "migrar_a_actual")
    primer_set = _primera(cargar, "set")
    assert errores < migrar < primer_set
    assert any(n.endswith("_aplicar_bloques_de_sesion") for n, _ in cargar)
    guardar = _llamadas(_funcion(arbol, "guardar_sesion"))
    assert any(n.endswith("escribir_json_atomico") for n, _ in guardar)
    assert not any(n == "open" for n, _ in guardar)
    nuevo = _llamadas(_funcion(arbol, "nuevo_proyecto"))
    assert any(n.endswith("sesion_vacia") for n, _ in nuevo)
    assert any(n.endswith("_aplicar_bloques_de_sesion") for n, _ in nuevo)
    bloques = _llamadas(_funcion(arbol, "_aplicar_bloques_de_sesion"))
    assert any(n.endswith("restaurar_datos_de_sitio") for n, _ in bloques)
    fuente = GUI.read_text(encoding="utf-8-sig")
    assert "Nuevo proyecto" in fuente and "datos_sitio_var" in fuente


def test_h_la_cli_reexporta_el_cargador_del_servicio():
    assert cli.cargar_datos_sitio is servicio.cargar_datos_sitio
    assert ses.sin_marca_de_tiempo is __import__("gui.exportacion_pdf",
                                                 fromlist=["x"]).sin_marca_de_tiempo
