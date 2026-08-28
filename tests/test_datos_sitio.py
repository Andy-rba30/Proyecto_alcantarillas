"""
tests/test_datos_sitio.py
=========================
Guardia de la quinta etiqueta, [S] (dato de sitio).

Lo que este archivo defiende no es un numero: es una frontera. Un dato de
sitio se parece a una constante normativa (tiene numeral, sale de un
procedimiento normativo) y se parece a un criterio adoptado (no es portable a
otra obra), y por parecerse a las dos cosas es el que se clasifica mal. Los
tests de aqui fijan las tres propiedades que lo distinguen:

    1. Se defiende con TRAZABILIDAD, no con sensibilidad: no hay rango que
       elegir, hay una lectura que reproducir.
    2. Declara su AMBITO. Lo que vale para todo el corredor vive aqui; lo que
       varia punto a punto es columna del CSV.
    3. Un dato sin leer DETIENE el calculo, igual que un criterio pendiente:
       nunca devuelve un default.

Valores de referencia: tests/fixtures/casos_patron.py (no se recalculan aqui).
"""

import pytest

import criterios_adoptados as ca
import datos_sitio as ds
from datos_sitio import (DATOS_SITIO, DatoSitio, dato, datos_sin_valor,
                         datos_usados, reporte_datos_sitio, valor)
from modelos import CriterioPendienteError, ErrorProyecto
from tests.fixtures.casos_patron import CP7_CADENA_SISMICA


@pytest.fixture(autouse=True)
def _aisla_registro_de_uso():
    """El registro de invocaciones es estado global del modulo."""
    previo = set(ds._USADOS)
    ds._USADOS.clear()
    yield
    ds._USADOS.clear()
    ds._USADOS.update(previo)


# ---------------------------------------------------------------------------
# Lo que define la etiqueta
# ---------------------------------------------------------------------------

def test_todos_los_datos_declarados_llevan_la_etiqueta_S():
    for clave, d in DATOS_SITIO.items():
        assert d.etiqueta == "S", f"'{clave}' no es un dato de sitio"


def test_cada_dato_declara_procedimiento_fuente_trazabilidad_y_ambito():
    """
    Las cuatro piezas sin las cuales un [S] no es reproducible. La
    trazabilidad es la que reemplaza a la sensibilidad de un [A]: un revisor
    tiene que poder repetir la lectura y llegar al mismo numero.
    """
    for clave, d in DATOS_SITIO.items():
        assert d.procedimiento, f"'{clave}' no dice como se obtuvo"
        assert d.fuente, f"'{clave}' no dice de donde sale el procedimiento"
        assert d.trazabilidad, f"'{clave}' no dice como reproducir la lectura"
        assert d.ambito, f"'{clave}' no dice para que parte del proyecto vale"


def test_ningun_dato_de_sitio_declara_sensibilidad():
    """
    Un [S] no tiene rango que elegir. Si alguna vez uno lo necesitara, no
    seria un dato de sitio: seria una adopcion [A] disfrazada.
    """
    assert not hasattr(DatoSitio, "sensibilidad")
    assert "sensibilidad" not in {c for c in DatoSitio.__dataclass_fields__}


def test_lo_que_vive_aqui_es_de_corredor_y_no_de_punto():
    """
    La frontera con el CSV: si un dato variara punto a punto, no se ajusta su
    valor -- se muda a una columna. Hoy los tres son unicos para el tramo y su
    ambito lo dice.
    """
    for clave, d in DATOS_SITIO.items():
        assert d.ambito == ds.AMBITO_CORREDOR, (
            f"'{clave}' declara un ambito que no es el corredor: si varia "
            "punto a punto le toca ser columna del CSV")


# ---------------------------------------------------------------------------
# La regla de siempre: un vacio detiene el calculo
# ---------------------------------------------------------------------------

def test_un_dato_sin_leer_lanza_y_no_devuelve_un_default(monkeypatch):
    original = DATOS_SITIO["PGA_roca_B"]
    monkeypatch.setitem(
        DATOS_SITIO, "PGA_roca_B",
        original.__class__(**{**original.__dict__, "valor": None}))

    with pytest.raises(CriterioPendienteError) as excinfo:
        valor("PGA_roca_B")

    assert excinfo.value.clave == "PGA_roca_B"
    assert excinfo.value.mensaje_gui == "falta declarar: PGA_roca_B"
    assert isinstance(excinfo.value, ErrorProyecto)
    assert "PGA_roca_B" in datos_sin_valor()


def test_una_clave_no_declarada_no_se_inventa():
    with pytest.raises(KeyError):
        valor("PGA_de_otra_provincia")


def test_el_uso_queda_registrado_para_M11():
    valor("PGA_roca_B")
    assert datos_usados() == ["PGA_roca_B"]
    assert set(datos_usados()) <= set(DATOS_SITIO)


def test_los_tres_datos_de_geometria_vial_estan_sin_leer_y_bloquean():
    """
    Este test decia «hoy ninguno esta sin leer» y afirmaba `datos_sin_valor()
    == []`. Ya no es cierto, Y ESO ES LA CORRECCION, no una regresion.

    Los tres datos que faltan son los que el cluster C02 y el C12 destaparon:
    sin la orientacion del muro respecto del trafico, AASHTO no dice cual de
    sus dos tablas de h_eq aplica; sin los carriles por sentido, el Cuadro 4.1
    del Manual de Suelos no dice si son 4 calicatas o 6. Antes el codigo
    rellenaba los dos huecos en silencio -- h_eq = 0.60 m plano y 4 calicatas
    para toda autopista --, que es exactamente lo que la etiqueta [S] con
    valor None existe para impedir.

    El test se invierte: lo que hay que vigilar no es que la lista este vacia
    sino que sea EXACTAMENTE la que el expediente declara pendiente. Si
    aparece un cuarto sin que nadie lo declare, este test lo dice.
    """
    assert sorted(datos_sin_valor()) == [
        "carriles_por_sentido",
        "distancia_borde_calzada_al_trasdos_m",
        "orientacion_muro_respecto_al_trafico",
    ]
    # Y los tres tienen que decir QUE los cerraria: un vacio sin salida
    # declarada es una excusa, con salida es una deuda con direccion.
    for clave in datos_sin_valor():
        assert dato(clave).verificacion_pendiente, (
            f"'{clave}' bloquea el calculo y no dice que haria falta para "
            "desbloquearlo")


# ---------------------------------------------------------------------------
# Los tres datos de este expediente
# ---------------------------------------------------------------------------

def test_el_PGA_es_el_de_CP7_y_abre_la_cadena_sismica():
    assert valor("PGA_roca_B") == pytest.approx(CP7_CADENA_SISMICA["PGA"])
    assert "Apendice A3" in dato("PGA_roca_B").fuente


def test_el_PGA_declara_que_su_coordenada_de_lectura_no_esta_registrada():
    """
    La honestidad que la etiqueta obliga a hacer visible: el valor esta leido,
    pero el expediente no dice sobre que punto del mapa. Mientras ese
    pendiente siga abierto, la memoria no puede presentarlo como cerrado.
    """
    d = dato("PGA_roca_B")
    assert d.verificacion_pendiente
    assert "PGA_roca_B" in ds.datos_con_verificacion_pendiente()
    assert "NO ESTAN REGISTRADAS" in d.trazabilidad


def test_los_dos_valores_de_E030_siguen_siendo_solo_referencia():
    """
    Sec. 0.4 descarta el sismo de 475 anios de E.030 frente al PGA de
    Tr = 1000 anios. El cambio de [N] a [S] es de clasificacion, no de uso:
    ningun modulo de calculo los invoca ni antes ni ahora.
    """
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[1]
    for clave in ("ZONA_SISMICA_LA_UNION", "Z_E030"):
        assert clave in DATOS_SITIO
        invocan = [ruta.name for ruta in (raiz / "src" / "modulos").glob("*.py")
                   if clave in ruta.read_text(encoding="utf-8-sig")]
        assert not invocan, f"'{clave}' dejo de ser referencia: lo usa {invocan}"

    assert valor("Z_E030") != pytest.approx(CP7_CADENA_SISMICA["PGA"])


def test_ninguno_de_los_tres_sigue_declarado_en_otro_archivo():
    """Una sola declaracion por dato: la doble definicion es lo que motivo la v5."""
    import constantes_normativas as CN

    for clave in DATOS_SITIO:
        assert not hasattr(CN, clave), (
            f"'{clave}' sigue declarado en constantes_normativas.py")
        assert clave not in ca.CRITERIOS, (
            f"'{clave}' sigue declarado en criterios_adoptados.py")


# ---------------------------------------------------------------------------
# El reporte que M11 imprime
# ---------------------------------------------------------------------------

def test_el_reporte_lista_solo_los_datos_usados():
    valor("Z_E030")
    texto = reporte_datos_sitio(solo_usados=True)
    assert "Z_E030" in texto
    assert "PGA_roca_B" not in texto


def test_el_reporte_imprime_la_trazabilidad_de_cada_dato():
    texto = reporte_datos_sitio(solo_usados=False)
    for clave, d in DATOS_SITIO.items():
        assert clave in texto
    assert "Trazabilidad" in texto
    assert "Ambito" in texto
    assert "DATOS DE SITIO" in texto


def test_sin_invocaciones_el_reporte_lo_dice_en_vez_de_quedar_vacio():
    assert reporte_datos_sitio(solo_usados=True) == (
        "No se invoco ningun dato de sitio.")


def test_el_reporte_advierte_de_la_trazabilidad_incompleta():
    valor("PGA_roca_B")
    texto = reporte_datos_sitio(solo_usados=True)
    assert "ADVERTENCIA" in texto
    assert "PGA_roca_B" in texto
