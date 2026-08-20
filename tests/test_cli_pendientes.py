"""
tests/test_cli_pendientes.py
============================
Pruebas del flag --pendientes de cli.py: la consulta informativa que imprime
TODOS los criterios sin valor agrupados por via de cierre y termina, sin
correr el pipeline y sin exigir el CSV.

Solo presentacion: estas pruebas no declaran ningun valor ni tocan el archivo
de criterios. Cuando hace falta un criterio de mentira, se inyecta con
`monkeypatch.setitem` sobre `ca.CRITERIOS`, el mismo patron de
tests/test_cli.py, y desaparece al terminar la prueba.
"""

import re

import pytest

import cli
import criterios_adoptados as ca

CLAVE_PRUEBA = "criterio_de_prueba_pendientes"


def _correr_pendientes(capsys):
    codigo = cli.main(["--pendientes"])
    return codigo, capsys.readouterr()


def _criterio_falso(fuente):
    return ca.Criterio(valor=None, etiqueta="A",
                       concepto="criterio de prueba del tablero de pendientes",
                       justificacion="existe solo dentro de esta prueba",
                       fuente=fuente)


def _conteo_del_grupo(texto, via):
    m = re.search(re.escape(via) + r": (\d+)$", texto, re.M)
    assert m, f"falta el encabezado del grupo: {via}"
    return int(m.group(1))


# ---------------------------------------------------------------------------
# Contrato basico: sin CSV, codigo 0, sin pipeline
# ---------------------------------------------------------------------------

def test_pendientes_no_requiere_csv_y_devuelve_cero(capsys):
    codigo, salida = _correr_pendientes(capsys)
    assert codigo == 0
    assert salida.err == ""
    assert "CRITERIOS PENDIENTES (SIN VALOR)" in salida.out


def test_pendientes_no_corre_el_pipeline_aunque_haya_csv(tmp_path, capsys):
    """Con --pendientes el CSV se ignora: uno ilegible no puede fallar."""
    codigo = cli.main(["--pendientes", str(tmp_path / "no_existe.csv")])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "No se pudo leer" not in salida.err
    assert "JSON del expediente" not in salida.out


def test_sin_csv_y_sin_pendientes_sigue_siendo_error_de_uso(capsys):
    """El CSV se volvio opcional SOLO para --pendientes, no para el pipeline."""
    with pytest.raises(SystemExit) as excinfo:
        cli.main([])
    assert excinfo.value.code == 2
    assert "falta el CSV" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Cobertura: lista los 26 vacios, cada uno con nombre, etiqueta,
# descripcion corta y fuente
# ---------------------------------------------------------------------------

def test_pendientes_lista_los_26_criterios_sin_valor(capsys):
    sin_valor = ca.criterios_sin_valor()
    assert len(sin_valor) == 26   # el tablero de hoy; si un vacio se cierra,
    #                               esta cifra baja y la prueba avisa
    _, salida = _correr_pendientes(capsys)
    assert f"CRITERIOS PENDIENTES (SIN VALOR): {len(sin_valor)}" in salida.out
    for clave in sin_valor:
        assert clave in salida.out, f"falta {clave} en el tablero"


def test_cada_pendiente_lleva_etiqueta_concepto_y_fuente(capsys):
    _, salida = _correr_pendientes(capsys)
    for clave in ca.criterios_sin_valor():
        c = ca.criterio(clave)
        assert f"[{c.etiqueta}] {clave}" in salida.out
        assert c.concepto in salida.out
        assert c.fuente in salida.out


def test_un_criterio_con_valor_no_aparece_en_el_tablero(capsys):
    _, salida = _correr_pendientes(capsys)
    assert "ke_entrada" not in salida.out        # [C] con valor 0.5
    assert "long_max_cuneta" not in salida.out   # [A] con valor 200.0


# ---------------------------------------------------------------------------
# Agrupacion por via de cierre
# ---------------------------------------------------------------------------

def test_los_grupos_salen_con_su_conteo_y_suman_el_total(capsys):
    _, salida = _correr_pendientes(capsys)
    grupos = cli.criterios_pendientes_por_via()
    suma = 0
    for via in (cli.VIA_DECISION, cli.VIA_DOCUMENTO, cli.VIA_ENSAYO):
        conteo = _conteo_del_grupo(salida.out, via)
        assert conteo == len(grupos[via])
        suma += conteo
    if grupos[cli.VIA_SIN_CLASIFICAR]:
        suma += _conteo_del_grupo(salida.out, cli.VIA_SIN_CLASIFICAR)
    assert suma == len(ca.criterios_sin_valor())


def test_la_agrupacion_reparte_todas_las_claves_sin_repetir():
    grupos = cli.criterios_pendientes_por_via()
    repartidas = [clave for claves in grupos.values() for clave in claves]
    assert sorted(repartidas) == ca.criterios_sin_valor()


def test_las_anclas_de_cada_via_estan_en_su_grupo():
    """Las instituciones que el propio tablero usa de ejemplo, en su sitio."""
    grupos = cli.criterios_pendientes_por_via()
    assert "TW_receptor" in grupos[cli.VIA_ENSAYO]              # fuente: ANA
    assert "homogeneidad_serie_fen" in grupos[cli.VIA_ENSAYO]   # SENAMHI
    assert "metodo_estabilidad_global" in grupos[cli.VIA_ENSAYO]  # EMS
    assert "v_max_hdpe" in grupos[cli.VIA_DOCUMENTO]            # PPI/FHWA
    assert "h_relleno_min_concreto_tmc" in grupos[cli.VIA_DOCUMENTO]  # M-170M
    assert "predimensionamiento_cabezal" in grupos[cli.VIA_DECISION]


def test_el_grupo_sin_clasificar_se_declara_no_se_esconde(capsys):
    grupos = cli.criterios_pendientes_por_via()
    sin_clasificar = grupos[cli.VIA_SIN_CLASIFICAR]
    assert sin_clasificar, ("hoy hay fuentes que no nombran su via de cierre "
                            "(p.ej. las que dicen solo 'PENDIENTE')")
    _, salida = _correr_pendientes(capsys)
    assert f"{cli.VIA_SIN_CLASIFICAR}: {len(sin_clasificar)}" in salida.out


# ---------------------------------------------------------------------------
# La via se lee del campo `fuente`, no de una lista aparte de claves
# ---------------------------------------------------------------------------

def test_si_cambia_la_fuente_el_grupo_la_sigue_solo(monkeypatch):
    monkeypatch.setitem(ca.CRITERIOS, CLAVE_PRUEBA,
                        _criterio_falso("PENDIENTE - serie SENAMHI completa"))
    assert CLAVE_PRUEBA in cli.criterios_pendientes_por_via()[cli.VIA_ENSAYO]

    monkeypatch.setitem(ca.CRITERIOS, CLAVE_PRUEBA,
                        _criterio_falso("PENDIENTE - eleccion del proyectista"))
    assert CLAVE_PRUEBA in cli.criterios_pendientes_por_via()[cli.VIA_DECISION]


def test_fuente_sin_marca_cae_en_sin_clasificar_no_se_fuerza(monkeypatch):
    monkeypatch.setitem(ca.CRITERIOS, CLAVE_PRUEBA,
                        _criterio_falso("PENDIENTE"))
    grupos = cli.criterios_pendientes_por_via()
    assert CLAVE_PRUEBA in grupos[cli.VIA_SIN_CLASIFICAR]


def test_con_varias_vias_nombradas_gana_la_mas_determinada():
    """Ensayo > documento > decision, como el orden N > N-> > S > C > A."""
    assert cli.via_de_cierre(
        "ensayo de corte, o tabla AASHTO, o adopcion declarada"
    ) == cli.VIA_ENSAYO
    assert cli.via_de_cierre(
        "tabla AASHTO, o adopcion declarada") == cli.VIA_DOCUMENTO


def test_una_sigla_se_busca_como_palabra_exacta_no_como_subcadena():
    # 'peruana' contiene 'ana' pero no es la ANA: no debe leerse como ensayo
    assert cli.via_de_cierre(
        "valor adoptado para la costa peruana") == cli.VIA_SIN_CLASIFICAR
    assert cli.via_de_cierre(
        "PENDIENTE: ANA / Junta de Usuarios") == cli.VIA_ENSAYO
