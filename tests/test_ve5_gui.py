# -*- coding: utf-8 -*-
"""
Lote VE5-GUI: cuatro huecos de la interfaz que el censo del 2026-11-20 dejó
como «implementable ya» (ítems 37, 38, 40 y 42). Ficha VE5GUI-01 de
`docs/decisiones_diferidas.md`.

- **42 (UI1-02):** el editor tipado ofrece las filas de TODAS las tablas de
  un criterio que se lee sobre varias, y declara cada una con su tabla.
- **37 (EB-06, T11-10):** la ventana emergente tiene campo de nota y declara
  por la MISMA puerta que la pestaña 2 (`src.editores.declarar`).
- **40 (T6-04):** `bombeo`, `peralte` y `S_conducto` tienen campo en la
  pestaña 1, viajan en la sesión y tienen bandera en la CLI.
- **38 (UI3-01, UI4-01):** el panel de declaración de la pestaña 2 tiene
  scroll y la fila de exportación cabe a 900 px (medido en ventana real, por
  `tests/apoyo/gui_ve5_real.py`, en `tests/test_ve5_gui_ventana.py`).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src import criterios_adoptados as ca
from src import declaracion as dec
from src import editores as sed
<<<<<<< HEAD
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
=======
from tests.apoyo.aproximacion import REL_TRANSPORTE
>>>>>>> claude/ve5-fixve4

RAIZ = Path(__file__).resolve().parent.parent

N_CAJON = "n_manning_cajon"
TB1 = "HDS5_3ED.TB.1"
T09 = "MC_HHD.T09"
H_EQ = "h_eq_bajo_altura_tabulada"
H_EQ_T1 = "AASHTO_LRFD_9.T3.11.6.4-1"
H_EQ_T2 = "AASHTO_LRFD_9.T3.11.6.4-2"
KE = "ke_entrada"


# ===========================================================================
# 42 · Las filas de todas las tablas (UI1-02)
# ===========================================================================

def test_42_el_esquema_ofrece_las_filas_de_todas_las_tablas():
    e = sed.esquema_de(N_CAJON)
    assert e.tablas == (TB1, T09)
    # `tabla_id` sigue siendo la primera: lo leen los consumidores de
    # un criterio de una sola tabla y los tests de T11-10.
    assert e.tabla_id == TB1
    por_tabla = {}
    for o in e.opciones_de_tabla:
        por_tabla.setdefault(o.tabla_id, set()).add(o.fila)
    assert set(por_tabla) == {TB1, T09}
    assert "concrete_boxes" in por_tabla[TB1]
    assert "concreto_afinado" in por_tabla[T09]


def test_42_la_fila_de_la_segunda_tabla_entra_con_su_procedencia_y_sin_nota():
    # La alternativa barrible de la Tabla N 09: hasta VE5-GUI sólo entraba
    # con nota, como adopción, porque el editor no conocía esa tabla.
    p = sed.declarar(N_CAJON, "concreto_afinado")
    assert p.tabla_id == T09
    assert p.filas == ("concreto_afinado",)
    assert not ca.declarado_en_caliente(N_CAJON) or ca.valor(N_CAJON) == "concreto_afinado"
    assert ca.valor(N_CAJON) == "concreto_afinado"


def test_42_elegir_la_fila_por_su_referencia_calificada():
    # Una clave corta que no se repite entre las tablas se guarda corta (VE-5,
    # lote «gui»: `tests/test_pf6_cabos.py`), y la calificada sigue valiendo.
    e = sed.esquema_de(N_CAJON)
    o = next(o for o in e.opciones_de_tabla if o.fila == "concreto_afinado")
    assert o.referencia == "concreto_afinado"
    assert sed.declarar(N_CAJON, "concreto_afinado", fila=o.referencia).tabla_id == T09
    p = sed.declarar(N_CAJON, "concreto_afinado", fila=f"{T09}#concreto_afinado")
    assert p.tabla_id == T09


def test_42_una_fila_repetida_en_dos_tablas_exige_decir_cual():
    e = sed.esquema_de(H_EQ)
    assert e.tablas == (H_EQ_T1, H_EQ_T2)
    referencias = {o.referencia for o in e.opciones_de_tabla}
    assert f"{H_EQ_T1}#5" in referencias and f"{H_EQ_T2}#5" in referencias
    with pytest.raises(ValueError, match="dos o mas tablas|varias tablas"):
        sed.declarar(H_EQ, "primera_fila", fila="5")
    p = sed.declarar(H_EQ, "primera_fila", fila=f"{H_EQ_T2}#5")
    assert p.tabla_id == H_EQ_T2
    assert p.filas == ("5",)


def test_42_una_fila_que_no_existe_en_ninguna_tabla_se_rechaza():
    with pytest.raises(ValueError):
        sed.declarar(N_CAJON, "concrete_boxes", fila="no_existe")
    with pytest.raises(ValueError):
        sed.declarar(N_CAJON, "concreto_afinado", fila=f"{TB1}#concreto_afinado")


def test_42_el_texto_que_nombra_una_fila_de_la_segunda_tabla_es_esa_fila():
    e = sed.esquema_de(N_CAJON)
    # Claves que no se repiten entre las dos tablas: viajan cortas (VE-5).
    assert sed.fila_implicita(e, "concreto_afinado") == "concreto_afinado"
    assert sed.fila_implicita(e, "concrete_boxes") == "concrete_boxes"


def test_42_un_criterio_de_una_sola_tabla_no_cambia():
    e = sed.esquema_de(KE)
    assert e.tablas == (e.tabla_id,)
    assert all(o.referencia == o.fila for o in e.opciones_de_tabla)
    assert all(o.tabla_id == e.tabla_id for o in e.opciones_de_tabla)


# ===========================================================================
# 37 · La ventana emergente con campo de nota (EB-06, T11-10)
# ===========================================================================

KE_TC2 = "HDS5_3ED.TC2"
KE_FILA = "concreto_headwall_square_edge"
ENSAYO = "capacidad_portante_adm"
NOTA = "adoptado del plano tipo del proyecto, hoja 3"


def _id_de_fila(tabla_id, clave_corta):
    from src import ventana_normativa as vn
    contenido = vn.contenido_de_tabla(tabla_id, KE)
    return next(f.id for f in contenido.filas if f.clave_corta == clave_corta)


def test_37_un_numero_que_difiere_de_la_celda_exige_nota_y_con_ella_entra():
    fila_id = _id_de_fila(KE_TC2, KE_FILA)
    with pytest.raises(ValueError):
        sed.declarar_desde_la_ventana(KE, 0.55, tabla_id=KE_TC2, fila=fila_id)
    assert not ca.declarado_en_caliente(KE)
    p = sed.declarar_desde_la_ventana(KE, 0.55, tabla_id=KE_TC2, fila=fila_id, nota=NOTA)
    assert p.tabla_id == KE_TC2 and p.filas == (KE_FILA,)
    assert p.nota == NOTA
    assert ca.valor(KE) == pytest.approx(0.55, rel=REL_TRANSPORTE)


def test_37_la_fila_de_la_tabla_sin_nota_sigue_entrando_como_antes():
    p = sed.declarar_desde_la_ventana(KE, 0.5, tabla_id=KE_TC2,
                                      fila=_id_de_fila(KE_TC2, KE_FILA))
    assert p.filas == (KE_FILA,)


def test_37_un_criterio_de_tabla_sin_fila_entra_solo_con_nota():
    with pytest.raises(ValueError, match="fila"):
        sed.declarar_desde_la_ventana(KE, 0.55, tabla_id=KE_TC2)
    assert not ca.declarado_en_caliente(KE)
    p = sed.declarar_desde_la_ventana(KE, 0.55, tabla_id=KE_TC2, nota=NOTA)
    assert p.nota == NOTA and not p.filas


def test_37_un_dato_de_ensayo_exige_la_nota_que_es_su_trazabilidad():
    with pytest.raises(ValueError, match="TRAZABILIDAD"):
        sed.declarar_desde_la_ventana(ENSAYO, 150.0)
    assert not ca.declarado_en_caliente(ENSAYO)
    p = sed.declarar_desde_la_ventana(ENSAYO, 150.0, nota="ensayo de carga, informe EMS-03")
    assert p.nota.startswith("ensayo de carga")


def test_37_el_par_del_encofrado_de_t11_10_entra_por_la_ventana():
    par = (0.013, 0.016)
    with pytest.raises(ValueError):
        sed.declarar_desde_la_ventana(N_CAJON, par, tabla_id=TB1)
    p = sed.declarar_desde_la_ventana(
        N_CAJON, par, tabla_id=TB1, nota="encofrado metalico, especificacion E-12")
    assert tuple(ca.valor(N_CAJON)) == par
    assert p.nota


def test_37_la_ventana_declara_por_la_puerta_de_editores_y_no_por_declaracion():
    """La emergente sólo pinta: su declaración es `src.editores.declarar_desde_la_ventana`."""
    arbol = ast.parse((RAIZ / "gui" / "ventana_normativa.py").read_text(encoding="utf-8"))
    metodo = next(n for n in ast.walk(arbol)
                  if isinstance(n, ast.FunctionDef) and n.name == "_declarar_segun_cara")
    llamadas = {ast.unparse(n.func) for n in ast.walk(metodo) if isinstance(n, ast.Call)}
    assert any(l.endswith("declarar_desde_la_ventana") for l in llamadas), llamadas
    assert not any(l.startswith("dec.declarar") for l in llamadas), llamadas
<<<<<<< HEAD
    # El campo de la nota existe: un atributo `nota_var` en el arbol.
    assert any(isinstance(n, ast.Attribute) and n.attr == "nota_var"
               for n in ast.walk(arbol))
=======
    nombres = {n.attr if isinstance(n, ast.Attribute) else n.id
               for n in ast.walk(arbol)
               if isinstance(n, (ast.Attribute, ast.Name))}
    assert "nota_var" in nombres
>>>>>>> claude/ve5-fixve4


def test_37_la_puerta_de_la_ventana_es_la_de_la_pestana_2():
    """Sin columna, la ventana pasa por `declarar` con la fila calificada por su tabla."""
    fuente = ast.parse((RAIZ / "src" / "editores.py").read_text(encoding="utf-8"))
    f = next(n for n in ast.walk(fuente)
             if isinstance(n, ast.FunctionDef) and n.name == "declarar_desde_la_ventana")
    llamadas = {ast.unparse(n.func) for n in ast.walk(f) if isinstance(n, ast.Call)}
    assert "declarar" in llamadas


# ===========================================================================
# 40 · `S_conducto`, `bombeo` y `peralte` en la ventana y en la CLI (T6-04)
# ===========================================================================

TRES_DE_T6_04 = ("S_conducto", "bombeo", "peralte")


def test_40_los_tres_tienen_campo_y_viajan_con_su_clave():
    import cli
    from src import sesion as ses
    for clave in TRES_DE_T6_04:
        assert ses.CLAVE_EXTERNA_DE_CAMPO[clave] == clave
        assert clave in cli.CLAVES_EXTERNAS
    # La coma decimal y el signo del peralte, por la MISMA traduccion que la
    # CLI aplica al leer una sesion y la ventana al correr.
    banderas = ses.banderas_de_externos(
        {"S_conducto": "0,004", "bombeo": "", "peralte": "-0,02"})
    assert banderas["S_conducto"] == "0.004"
    assert banderas["bombeo"] is None
    assert banderas["peralte"] == "-0.02"


def test_40_una_sesion_de_un_formato_anterior_abre_sin_los_campos_nuevos():
    from src import sesion as ses
    vieja = {"formato_version": 3, "externos": {"luz_m": "2.0"}}
    assert ses.errores_de_sesion(vieja) == []
    migrada, _avisos = ses.migrar_a_actual(vieja)
    banderas = ses.banderas_de_externos(migrada["externos"])
    assert banderas["luz_m"] == "2.0"
    assert all(banderas[c] is None for c in TRES_DE_T6_04)


def test_40_la_cli_lleva_las_tres_banderas_a_los_datos_externos(monkeypatch, tmp_path):
    import cli
    from src.modelos import DatoInvalidoError
    vistas = {}

    def capturar(ruta, banderas):
        vistas.update(banderas)
        raise DatoInvalidoError("datos_externos", valor="sonda", motivo="sonda del test")

    monkeypatch.setattr(cli, "cargar_datos_externos", capturar)
    codigo = cli.main([str(RAIZ / "tests" / "ejemplo_puntos_perfil.csv"),
                       "--s-conducto", "0.004", "--bombeo", "0.02",
                       "--peralte", "-0.03", "--json", str(tmp_path / "i.json")])
    assert codigo == 2
    assert vistas["S_conducto"] == pytest.approx(0.004, rel=REL_TRANSPORTE)
    assert vistas["bombeo"] == pytest.approx(0.02, rel=REL_TRANSPORTE)
    assert vistas["peralte"] == pytest.approx(-0.03, rel=REL_TRANSPORTE)


def test_40_las_banderas_pisan_al_global_del_json_y_conservan_la_exclusion(tmp_path):
    import cli
    from src.modelos import DatoInvalidoError
    json_ = tmp_path / "ext.json"
    json_.write_text('{"globales": {"bombeo": 0.02}}', encoding="utf-8")
    ext = cli.cargar_datos_externos(json_, {"bombeo": 0.0, "peralte": 0.04})
    assert ext.valor("X", "bombeo") == pytest.approx(0.0, abs=ABS_CERO)
    assert ext.valor("X", "peralte") == pytest.approx(0.04, rel=REL_TRANSPORTE)
    with pytest.raises(DatoInvalidoError):
        cli.cargar_datos_externos(json_, {"peralte": 0.04})


# ===========================================================================
# 39 · Temporales únicos al exportar; el fallo de escritura sin traza (UI5-01 c, d)
# ===========================================================================

@pytest.fixture(scope="module")
def informe_de_perfil():
    from src import indice_formulas as ind
    referencia = next(r for r in ind.CORRIDAS_DE_REFERENCIA if r.nombre == "perfil_guia")
    return ind.correr_referencia(referencia)


def _exportadores_de_m11():
    from src.modulos import M11_reporte as M11
    return {"html": lambda inf, d: M11.exportar_html(inf, d),
            "html_resumida": lambda inf, d: M11.exportar_html_resumida(inf, d),
            "csv": lambda inf, d: M11.exportar_csv(inf, d)}


@pytest.mark.parametrize("via", ["html", "html_resumida", "csv"])
def test_39_no_pisa_el_archivo_del_usuario_con_nombre_de_temporal(via, informe_de_perfil, tmp_path):
    destino = tmp_path / f"memoria.{via}"
    del_usuario = destino.with_name(destino.name + ".parcial")
    del_usuario.write_text("archivo del usuario", encoding="utf-8")
    _exportadores_de_m11()[via](informe_de_perfil, destino)
    assert destino.stat().st_size > 0
    assert del_usuario.read_text(encoding="utf-8") == "archivo del usuario"
    # Y no deja restos: el temporal de `escribir_atomico` es oculto y se va.
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(
        [destino.name, del_usuario.name])


@pytest.mark.parametrize("via", ["html", "html_resumida", "csv"])
def test_39_un_destino_de_nombre_largo_se_escribe(via, informe_de_perfil, tmp_path):
    destino = tmp_path / ("m" * 245 + f".{via[:4]}")
    _exportadores_de_m11()[via](informe_de_perfil, destino)
    assert destino.stat().st_size > 0


@pytest.mark.parametrize("via", ["html", "html_resumida", "csv"])
def test_39_un_enlace_simbolico_sigue_siendo_enlace(via, informe_de_perfil, tmp_path):
    real = tmp_path / "real" / "memoria"
    real.parent.mkdir()
    real.write_text("anterior", encoding="utf-8")
    real.chmod(0o600)
    enlace = tmp_path / "enlace"
    enlace.symlink_to(real)
    _exportadores_de_m11()[via](informe_de_perfil, enlace)
    assert enlace.is_symlink()
    assert real.read_text(encoding="utf-8") != "anterior"
    assert real.stat().st_mode & 0o777 == 0o600


def test_39_la_sesion_se_escribe_por_la_misma_puerta(tmp_path):
    from src import sesion as ses
    real = tmp_path / "real.json"
    real.write_text("{}", encoding="utf-8")
    enlace = tmp_path / "sesion.json"
    enlace.symlink_to(real)
    ses.escribir_json_atomico(enlace, {"a": 1})
    assert enlace.is_symlink() and '"a": 1' in real.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        ses.escribir_json_atomico(tmp_path / "nan.json", {"x": float("nan")})
    assert not (tmp_path / "nan.json").exists()


def test_39_la_cli_que_no_puede_escribir_sale_con_su_codigo_y_sin_traza(capsys, tmp_path):
    import cli
    from gui import exportacion_pdf as expdf
    bloqueo = tmp_path / "soy_un_archivo"
    bloqueo.write_text("", encoding="utf-8")
    codigo = cli.main([str(RAIZ / "tests" / "ejemplo_puntos_perfil.csv"),
                       "--alcance", "perfil",
                       "--json", str(bloqueo / "dentro" / "i.json")])
    err = capsys.readouterr().err
    assert codigo == cli.CODIGO_ESCRITURA_FALLIDA
    assert codigo not in (0, 1, 2)
    assert "No se pudo escribir una salida" in err and "Traceback" not in err
    # El hijo del PDF de la ventana no lo cuenta como memoria escrita.
    assert codigo not in expdf.CODIGOS_DE_SALIDA_CON_MEMORIA


def test_39_el_fallo_del_pdf_en_la_cli_sale_con_su_mensaje(monkeypatch, capsys, tmp_path):
    import cli

    def disco_lleno(*_a, **_k):
        raise OSError(28, "No space left on device", str(tmp_path / "m.pdf"))

    monkeypatch.setattr(cli, "exportar_pdf", disco_lleno)
    codigo = cli.main([str(RAIZ / "tests" / "ejemplo_puntos_perfil.csv"),
                       "--alcance", "perfil", "--json", str(tmp_path / "i.json"),
                       "--pdf", str(tmp_path / "m.pdf")])
    err = capsys.readouterr().err
    assert codigo == cli.CODIGO_ESCRITURA_FALLIDA
    assert "No space left on device" in err and "Traceback" not in err
    # Lo que se escribio antes del fallo queda entero.
    assert (tmp_path / "i.json").stat().st_size > 0


# ===========================================================================
# 46 · Ids `FH.*` en el índice; la fila de rugosidad; `D` con sus decimales
# ===========================================================================

def test_46_el_indice_reconoce_los_ids_de_la_hidrologia_y_los_de_punto_interior():
    from src import indice_formulas as ind
    menciones = ind.menciones_del_fundamento()
    assert menciones.get("FH.FACTOR_P24") == ("MH_hidrologia",)
    assert "M5_verificaciones" in menciones.get("F5.V2b.REGIMEN", ())
    import re
    assert re.fullmatch(ind.PATRON_ID_DE_FUNDAMENTO, "F4.N_CONCRETO")
    assert not re.fullmatch(ind.PATRON_ID_DE_FUNDAMENTO, "FX.ALGO")


@pytest.mark.parametrize("valor, texto", [(0.9, "0.90 m"), (1.05, "1.05 m"),
                                          (1.0668, "1.0668 m"), (1.2192, "1.2192 m")])
def test_46_la_dimension_de_la_sustitucion_es_la_del_rotulo(valor, texto):
    from src import modelos as mod
    assert mod.SeccionCircular(D=valor).magnitudes_de_forma()[0].texto == texto
    assert f"{mod.texto_de_dimension(valor)} m" == texto


def test_46_la_dimension_del_marco_tambien():
    from src import modelos as mod
    b, h = mod.SeccionRectangular(B=1.2192, H=0.9).magnitudes_de_forma()
    assert (b.texto, h.texto) == ("1.2192 m", "0.90 m")


def test_46_la_fila_de_rugosidad_no_supone_la_regla_de_doble_n(informe_de_perfil, monkeypatch):
    from src.modulos import M11_reporte as M11
    html = M11.memoria_html(informe_de_perfil)
    assert "Rugosidad (regla de doble n)" not in html
    assert "<b>Rugosidad (n de Manning)</b>" in html
    assert "Fila de la Tabla N 09: ninguna" not in html


# ===========================================================================
# 49 · El hijo del PDF formatea la corrida embebida; las entradas invalidan
# ===========================================================================

def _corrida(nombre):
    from src import indice_formulas as ind
    referencia = next(r for r in ind.CORRIDAS_DE_REFERENCIA if r.nombre == nombre)
    return referencia, ind.correr_referencia(referencia)


@pytest.mark.parametrize("nombre", ["perfil_guia", "expediente_cabezal"])
def test_49_el_informe_tiene_ida_y_vuelta_y_da_la_misma_memoria(nombre):
    import json
    import cli
    from src import serializacion_informe as si
    from src.modulos import M11_reporte as M11
    _ref, informe = _corrida(nombre)
    texto = json.dumps(si.informe_a_dict(informe), ensure_ascii=False, allow_nan=False)
    vuelta = si.informe_desde_dict(json.loads(texto))
    assert cli.informe_json(vuelta) == cli.informe_json(informe)
    # La identidad de los pasos compartidos se conserva: la memoria no
    # imprime un paso «repetido» de mas (medido en expediente_cabezal).
    assert M11.memoria_html(vuelta) == M11.memoria_html(informe)
    assert M11.memoria_resumida_html(vuelta) == M11.memoria_resumida_html(informe)


@pytest.mark.parametrize("malo", [
    {"__dc__": "os:PathLike", "campos": {}, "__n__": 0},
    {"__dc__": "src.escritura_atomica:archivo_real", "campos": {}, "__n__": 0},
    {"__dc__": "src.modelos:Magnitud", "campos": {"nombre": "x"}, "__n__": 0},
    {"__enum__": "builtins:object", "miembro": "x"},
    {"__ref__": 7},
])
def test_49_el_cargador_no_construye_nada_fuera_de_las_clases_de_src(malo):
    from src import serializacion_informe as si
    with pytest.raises(ValueError):
        si.informe_desde_dict({"formato": si.FORMATO_INFORME_SERIALIZADO, "informe": malo})
    with pytest.raises(ValueError):
        si.informe_desde_dict({"formato": 99, "informe": None})


def _sesion_del_hijo(tmp_path, nombre="perfil_guia"):
    import shutil
    from src import sesion as ses
    from gui import exportacion_pdf as expdf
    referencia, informe = _corrida(nombre)
    csv = tmp_path / "puntos.csv"
    shutil.copyfile(referencia.csv, csv)
    sesion = expdf.sesion_de_la_corrida(
        informe, proyecto="DATOS DE PRUEBA", csv=str(csv), datos_externos="",
        externos={}, alcance=informe.alcance,
        formato_version=ses.FORMATO_SESION, app_version="1.0")
    return informe, sesion, csv


def test_49_la_sesion_del_hijo_trae_la_corrida_y_el_comando_la_pide(tmp_path):
    from gui import exportacion_pdf as expdf
    _informe, sesion, _csv = _sesion_del_hijo(tmp_path)
    assert expdf.trae_la_corrida_embebida(sesion)
    proceso = expdf.ProcesoPdf(sesion=sesion, destino=tmp_path / "m.pdf",
                               directorio_trabajo=tmp_path / "trabajo",
                               plantilla=Path("p.html"),
                               interprete="interprete-que-no-existe")
    proceso.iniciar()
    assert "--corrida-embebida" in proceso.comando
    assert not expdf.trae_la_corrida_embebida({"corridas": []})


def test_49_la_cli_formatea_la_corrida_sin_releer_el_csv(tmp_path, capsys):
    import json
    import cli
    from src import sesion as ses
    from src.modulos import M11_reporte as M11
    informe, sesion, csv = _sesion_del_hijo(tmp_path)
    ruta = tmp_path / "s.json"
    ses.escribir_json_atomico(ruta, sesion)
    csv.unlink()                      # el hijo no lo relee
    plantilla = cli.plantilla_por_alcance(informe.alcance)
    codigo = cli.main(["--sesion", str(ruta), "--corrida-embebida",
                       "--html", str(tmp_path / "m.html"),
                       "--json", str(tmp_path / "i.json"),
                       "--plantilla", str(plantilla)])
    salida = capsys.readouterr()
    assert codigo in (0, 1), salida.err
    assert "formateada sin recalcular" in salida.out
    html = (tmp_path / "m.html").read_text(encoding="utf-8")
    assert html == M11.memoria_html(informe, proyecto="DATOS DE PRUEBA",
                                    ruta_plantilla=plantilla)
    # Con la hora de la corrida: es la misma, no otra.
    assert json.loads((tmp_path / "i.json").read_text(encoding="utf-8")) == \
        json.loads(json.dumps(cli.informe_json(informe), ensure_ascii=False))


def test_49_un_informe_que_no_es_el_de_su_volcado_no_se_formatea(tmp_path, capsys):
    import cli
    from src import sesion as ses
    _informe, sesion, _csv = _sesion_del_hijo(tmp_path)
    sesion["corridas"][0]["informe_json"]["generado_utc"] = "1999-01-01T00:00:00Z"
    ruta = tmp_path / "s.json"
    ses.escribir_json_atomico(ruta, sesion)
    codigo = cli.main(["--sesion", str(ruta), "--corrida-embebida",
                       "--html", str(tmp_path / "m.html"),
                       "--json", str(tmp_path / "i.json")])
    assert codigo == 2
    assert "no es el de su volcado" in capsys.readouterr().err
    assert not (tmp_path / "m.html").exists() and not (tmp_path / "i.json").exists()


def test_49_sin_corrida_embebida_la_bandera_lo_dice(tmp_path, capsys):
    import cli
    from src import sesion as ses
    _informe, sesion, _csv = _sesion_del_hijo(tmp_path)
    sesion["corridas"] = []
    ruta = tmp_path / "s.json"
    ses.escribir_json_atomico(ruta, sesion)
    assert cli.main(["--sesion", str(ruta), "--corrida-embebida",
                     "--json", str(tmp_path / "i.json")]) == 2
    assert "no trae ninguna corrida con su informe entero" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        cli.main([str(RAIZ / "tests" / "ejemplo_puntos_perfil.csv"), "--corrida-embebida"])


def test_49_las_entradas_de_la_pestana_1_invalidan_y_las_sesiones_no_las_pisan():
    """
    Por el AST de la ventana (sin Tk): las trazas de los campos que la
    corrida lee llaman a `_al_cambiar_una_entrada`, y «Cargar sesion» y
    «Nuevo proyecto» escriben esos campos DESPUES de retirar el informe con
    el motivo de la sesion. La medida en ventana real esta en
    `tests/test_ve5_gui_ventana.py`.
    """
    arbol = ast.parse((RAIZ / "gui" / "app.py").read_text(encoding="utf-8"))
    funciones = {n.name: ast.unparse(n) for n in ast.walk(arbol)
                 if isinstance(n, ast.FunctionDef)}
    init = funciones["__init__"]
    for var in ("datos_externos_var", "datos_sitio_var", "alcance_var"):
        traza = next(l for l in init.splitlines() if f"self.{var}.trace_add" in l)
        assert "_al_cambiar_una_entrada" in traza or "_al_cambiar_una_entrada" in \
            init[init.index(f"self.{var}.trace_add"):][:300], var
    for nombre in ("cargar_sesion", "nuevo_proyecto"):
        cuerpo = funciones[nombre]
        bloques = cuerpo.index("self._aplicar_bloques_de_sesion(")
        for var in ("self.datos_externos_var.set(", "self.datos_sitio_var.set(",
                    "self.alcance_var.set(", "var.set("):
            assert cuerpo.index(var) > bloques, (nombre, var)


# ===========================================================================
# 48 · La integración continua corre los tests de ventana (SIS-F-01, C09-01)
# ===========================================================================

def test_48_la_integracion_continua_corre_la_suite_bajo_un_servidor_x():
    flujo = (RAIZ / ".github" / "workflows" / "pruebas.yml").read_text(encoding="utf-8")
    assert "xvfb" in flujo and "python3-tk" in flujo
    # La suite entera, y con el envoltorio con que la suite busca un Tk.
    assert "xvfb-run -a python -m pytest" in flujo
    # La sonda que la suite usa para decidir si salta las ventanas, como paso
    # propio: si el Tk no se levanta, el flujo falla en vez de saltarlas.
    assert "tkinter.Tk()" in flujo
    assert "pip install -r requirements.txt -r requirements-dev.txt" in flujo


# ===========================================================================
# 43 · Los ensayos de durabilidad en el censo, la ayuda y el pre-vuelo (T4-09)
# ===========================================================================

def test_43_los_seis_ensayos_son_la_quinta_poblacion_del_censo():
    from src import servicio
    from src import variables_entrada as ve
    from src.modelos import ENSAYOS_DE_DURABILIDAD, Poblacion
    censados = {v.clave for v in ve.VARIABLES.values()
                if v.poblacion is Poblacion.DATO_EXTERNO_OPCIONAL}
    assert censados == set(ENSAYOS_DE_DURABILIDAD) == set(servicio.CLAVES_DE_DURABILIDAD)
    # No son de CLAVES_EXTERNAS: ninguna etapa los exige.
    assert not censados & set(servicio.CLAVES_EXTERNAS)
    for clave in censados:
        v = ve.variable(clave)
        assert v.concepto and v.unidad and v.fase
        assert "M2_material" in v.consumido_por
    from src import constantes_normativas as cn
    assert ve.variable("abrasion").resolucion.opciones == tuple(cn.NIVELES_DE_ABRASION)


def test_43_la_ayuda_del_json_los_nombra_rotulados_como_opcionales():
    from src import ayuda_entrada as ay
    from src.modelos import ENSAYOS_DE_DURABILIDAD
    fichas = ay.fichas_de_ensayos_opcionales()
    assert [f.clave for f in fichas] == list(ENSAYOS_DE_DURABILIDAD)
    assert all(f.concepto and f.de_donde_sale for f in fichas)
    # La ventana de ayuda los pinta: la llamada esta en su arbol.
    arbol = ast.parse((RAIZ / "gui" / "ayuda_entrada.py").read_text(encoding="utf-8"))
    assert any(isinstance(n, ast.Call)
               and ast.unparse(n.func) == "ay.fichas_de_ensayos_opcionales"
               for n in ast.walk(arbol))


def test_43_el_prevuelo_no_los_cuenta_como_falta():
    """Sin ningun ensayo declarado, ninguno sale como dato que falta."""
    import cli
    from src import anticipo
    from src.modelos import ENSAYOS_DE_DURABILIDAD
    csv = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
    for alcance in (cli.ALCANCE_PERFIL, cli.ALCANCE_EXPEDIENTE):
        faltas = anticipo.datos_faltantes_por_punto(
            csv, cli.cargar_datos_externos(None, {}), alcance)
        texto = repr(faltas)
        for clave in ENSAYOS_DE_DURABILIDAD:
            assert f"'{clave}'" not in texto, (alcance, clave)


# ===========================================================================
# 45 · Estado del expediente: discrepancias abiertas y corridas (C8-02)
# ===========================================================================

def test_45_las_discrepancias_abiertas_tienen_consumidor_y_son_las_del_registro():
    from src import estado_del_expediente as estexp
    from src.normativa import registro
    abiertas = estexp.discrepancias_abiertas()
    assert [d.id for d in abiertas] == [d.id for d in registro.construir().discrepancias_abiertas()]
    assert abiertas, "el censo del 2026-11-20 tiene dos abiertas"
    for d in abiertas:
        assert d.id in d.linea() and d.gana in d.linea()
    arbol = ast.parse((RAIZ / "gui" / "app.py").read_text(encoding="utf-8"))
    assert any(isinstance(n, ast.Call)
               and ast.unparse(n.func) == "estexp.discrepancias_abiertas"
               for n in ast.walk(arbol))


def test_45_las_corridas_para_comparar_son_las_que_traen_volcado_y_la_ultima_primero():
    from src import estado_del_expediente as estexp
    corridas = [
        {"generado_utc": "2026-11-20T01:00:00Z", "alcance": "perfil",
         "csv_sha1": "a" * 40, "criterios_sha1": "b" * 40, "informe_json": {"x": 1}},
        {"generado_utc": "2026-11-20T02:00:00Z", "alcance": "perfil"},   # sin volcado
        "no es una corrida",
        {"generado_utc": "2026-11-20T03:00:00Z", "alcance": "expediente",
         "csv_sha1": "c" * 40, "criterios_sha1": "d" * 40, "informe_json": {"x": 2}},
    ]
    lista = estexp.corridas_para_comparar(corridas)
    assert [c.indice for c in lista] == [3, 0]
    assert lista[0].rotulo.startswith("2026-11-20T03:00:00Z · expediente · CSV cccccccc")
    assert lista[1].informe_json == {"x": 1}


# ===========================================================================
# 44 · Techos de transcripción de la Fase 6, como aviso (T8-11)
# ===========================================================================

class _Lecho:
    def __init__(self, D84_m=None, Sv_Pa=None):
        self.D84_m, self.Sv_Pa = D84_m, Sv_Pa


def test_44_sin_declarar_no_hay_aviso():
    from src.modulos import M6_proteccion as M6
    datos = {"duracion_caudal_pico_min": 1e9, "material_lecho_salida": _Lecho(D84_m=5.0)}
    assert ca.CRITERIOS["techos_de_transcripcion_fase_6"].valor is None
    assert ca.CRITERIOS["techos_de_transcripcion_fase_6"].opcional
    assert M6.avisos_de_transcripcion(datos.get) == []


def test_44_declarado_avisa_lo_que_pasa_su_techo_y_nada_mas(monkeypatch):
    from src.modulos import M6_proteccion as M6
    monkeypatch.setitem(ca._OVERRIDES, "techos_de_transcripcion_fase_6",
                        {"D84_m": 1.0, "duracion_caudal_pico_min": 1440.0})
    datos = {"duracion_caudal_pico_min": 60.0,
             "material_lecho_salida": _Lecho(D84_m=5.0, Sv_Pa=1e300)}
    avisos = M6.avisos_de_transcripcion(datos.get)
    assert len(avisos) == 1
    assert "material_lecho_salida.D84_m = 5 m" in avisos[0]
    assert "ningun resultado cambia" in avisos[0]


@pytest.mark.parametrize("malo", [{"D84": 1.0}, {"D84_m": -1.0}, {"D84_m": True},
                                  {"Sv_Pa": float("inf")}])
def test_44_un_techo_mal_declarado_no_se_ignora(malo, monkeypatch):
    from src.modulos import M6_proteccion as M6
    from src.modelos import DatoInvalidoError
    monkeypatch.setitem(ca._OVERRIDES, "techos_de_transcripcion_fase_6", malo)
    with pytest.raises(DatoInvalidoError):
        M6.avisos_de_transcripcion(lambda clave: None)
