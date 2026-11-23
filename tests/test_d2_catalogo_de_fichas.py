# -*- coding: utf-8 -*-
"""
tests/test_d2_catalogo_de_fichas.py
===================================
Pruebas D2: `src/criterios_adoptados.py` quedo como MECANISMO y las 169
fichas viven en el paquete `src/criterios/`, una por dominio. Lo que se fija
aqui es lo que la particion no puede romper en silencio:

- que el catalogo sean TODOS los archivos del paquete, sin uno sin registrar
  (sus criterios no entrarian en `CRITERIOS` y su texto no entraria en la
  huella);
- que cada ficha este en el archivo que `archivo_de_criterio` dice, que es
  donde escribe la escritura permanente;
- que la huella `criterios_sha1` del `ContextoCorrida` sea la del CONJUNTO
  y se mueva al tocar una ficha. Hasta D2 era el SHA-1 de
  `criterios_adoptados.py` solo, y desde la particion ese archivo ya no
  cambia al cambiar una ficha: la huella habria dejado de distinguir dos
  catalogos distintos. DECLARADO: el VALOR de la huella cambio con D2 aunque
  no cambio ningun criterio.
"""
from __future__ import annotations

import ast
import shutil
from pathlib import Path

from src import criterios_adoptados as ca
from src import criterios as paquete
from tests.apoyo import estructura

RAIZ = Path(__file__).resolve().parents[1]
PAQUETE = RAIZ / "src" / "criterios"


def test_el_catalogo_son_el_mecanismo_y_todos_los_archivos_del_paquete():
    en_disco = {r.resolve() for r in PAQUETE.glob("*.py")}
    assert {r.resolve() for r in PAQUETE.rglob("*.py")
            if "__pycache__" not in r.parts} == en_disco, (
        "src/criterios/ tiene subdirectorios: el catalogo es de un nivel")
    archivos = [r.resolve() for r in ca.archivos_de_criterios()]
    assert len(archivos) == len(set(archivos))
    assert set(archivos) == en_disco | {(RAIZ / "src" / "criterios_adoptados.py").resolve()}
    registrados = {r.resolve() for r, _ in paquete.MODULOS_DE_FICHAS}
    assert registrados == en_disco - {(PAQUETE / "__init__.py").resolve(),
                                      (PAQUETE / "_base.py").resolve()}, (
        "un archivo de fichas de src/criterios/ no esta en MODULOS_DE_FICHAS: "
        "sus criterios no entran en CRITERIOS")


def test_los_criterios_son_los_de_las_fichas_en_su_orden():
    assert list(ca.CRITERIOS) == list(paquete.CRITERIOS_DE_FICHAS)
    assert set(ca.CRITERIOS) == set(paquete.ORIGEN_POR_CLAVE)
    orden = [clave for _, fichas in paquete.MODULOS_DE_FICHAS for clave in fichas]
    assert orden == list(ca.CRITERIOS)


def _claves_declaradas(ruta: Path) -> set:
    """Las claves del dict `CRITERIOS` LITERAL del archivo, por AST."""
    valor = estructura.valor_asignado(ruta, "CRITERIOS")
    if not isinstance(valor, ast.Dict):
        return set()
    return {k.value for k in valor.keys
            if isinstance(k, ast.Constant) and isinstance(k.value, str)}


def test_cada_ficha_esta_en_el_archivo_que_la_escritura_permanente_toca():
    por_archivo = {r.resolve(): _claves_declaradas(r)
                   for r in ca.archivos_de_criterios()}
    for clave in ca.CRITERIOS:
        donde = [r for r, claves in por_archivo.items() if clave in claves]
        assert donde == [ca.archivo_de_criterio(clave).resolve()], (clave, donde)
    mecanismo = RAIZ / "src" / "criterios_adoptados.py"
    assert not por_archivo[mecanismo.resolve()], (
        "el mecanismo volvio a declarar fichas en un dict CRITERIOS literal")
    construye = [n.lineno for n in ast.walk(estructura.arbol(mecanismo))
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "Criterio"]
    assert not construye, f"el mecanismo construye un Criterio en {construye}"


# Los archivos REALES del catalogo, leidos antes de que ningun test parchee
# `archivos_de_criterios`.
ARCHIVOS_REALES = ca.archivos_de_criterios()


def _huella_de_una_copia(tmp_path, monkeypatch, tocar=None) -> str:
    """`sha1_criterios()` sobre una copia del catalogo con la misma
    estructura de rutas, tocando opcionalmente un archivo."""
    copias = []
    for ruta in ARCHIVOS_REALES:
        rel = ruta.resolve().relative_to(RAIZ)
        destino = tmp_path / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ruta, destino)
        if tocar is not None and ruta.resolve() == tocar.resolve():
            destino.write_bytes(destino.read_bytes() + b"\n# tocado\n")
        copias.append(destino)
    monkeypatch.setattr(ca, "archivos_de_criterios", lambda: tuple(copias))
    monkeypatch.setattr(ca, "_RAIZ_PROYECTO", tmp_path)
    return ca.sha1_criterios()


def test_la_huella_es_la_del_conjunto_y_se_mueve_al_tocar_una_ficha(
        tmp_path, monkeypatch):
    real = ca.sha1_criterios()
    assert _huella_de_una_copia(tmp_path / "igual", monkeypatch) == real, (
        "la huella depende de algo mas que las rutas relativas y los bytes")
    ficha = ca.archivo_de_criterio("ke_entrada")
    assert _huella_de_una_copia(tmp_path / "ficha", monkeypatch,
                                tocar=ficha) != real, (
        "tocar una ficha no movio la huella")
    mecanismo = RAIZ / "src" / "criterios_adoptados.py"
    assert _huella_de_una_copia(tmp_path / "mecanismo", monkeypatch,
                                tocar=mecanismo) != real


def test_la_corrida_fotografia_la_huella_del_conjunto():
    from src import servicio

    contexto = servicio.capturar_contexto(csv_sha1="0" * 40)
    assert contexto.criterios_sha1 == ca.sha1_criterios()


def test_la_fecha_del_encabezado_es_la_del_archivo_mas_reciente_del_catalogo():
    mas_reciente = ca.archivo_de_criterios_mas_reciente()
    assert mas_reciente in ca.archivos_de_criterios()
    assert all(mas_reciente.stat().st_mtime >= r.stat().st_mtime
               for r in ca.archivos_de_criterios())


def test_ningun_archivo_del_paquete_pasa_del_tope_del_bloque_d():
    """Criterio de aceptacion del bloque D: ningun archivo de ~3 000 lineas."""
    tope = 3000
    largos = {r.name: n for r in PAQUETE.glob("*.py")
              if (n := len(r.read_text(encoding="utf-8").splitlines())) > tope}
    assert not largos, largos
