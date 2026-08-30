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
from tests.apoyo import estructura


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
        # SIS-C-02. La version anterior preguntaba `clave in <texto fuente>`,
        # y eso falla en las dos direcciones: un comentario que solo MENCIONE
        # la clave tumba el test en falso, y una invocacion con la clave
        # partida (`ds.valor("Z" + "_E030")`) lo deja verde. Se pregunta al
        # arbol: que nombres LEE el modulo y que claves de texto pasa como
        # argumento o como indice.
        invocan = [ruta.name for ruta in (raiz / "src" / "modulos").glob("*.py")
                   if clave in estructura.nombres_usados(ruta)
                   or clave in estructura.textos_de_llamada_o_indice(ruta)]
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


# ===========================================================================
# La guardia al importar (SIS-D-09)
# ===========================================================================
# El hallazgo: `criterios_adoptados._verificar_criterio` rechazaba al importar
# un [S] sin trazabilidad, y aqui el mismo objeto se construia sin una queja.
# La regla estaba escrita con las mismas palabras en los dos archivos y se
# hacia cumplir en uno solo, sin que ninguna nota declarara la asimetria.
#
# La guardia va en `__post_init__` y no solo en un barrido al importar porque
# este archivo NO tiene API de escritura: el unico camino para meter un dato
# invalido es construir un `DatoSitio`, que es exactamente lo que el hallazgo
# hace.

def _dato_valido(**campos):
    base = dict(valor=1.0, concepto="c", procedimiento="p", fuente="f",
                trazabilidad="t",
                resolucion=ds.DeEnsayo(ensayo="e", trazabilidad_exigida="te"))
    base.update(campos)
    return DatoSitio(**base)


def test_la_guardia_rechaza_el_caso_exacto_del_hallazgo():
    """`DatoSitio(trazabilidad='', etiqueta='A')` -- SIS-D-09, literal."""
    with pytest.raises(ValueError, match="etiqueta"):
        _dato_valido(trazabilidad="", etiqueta="A")


def test_la_guardia_rechaza_un_dato_de_sitio_sin_trazabilidad():
    """Es la misma regla que `criterios_adoptados` ya hacia cumplir."""
    with pytest.raises(ValueError, match="trazabilidad"):
        _dato_valido(trazabilidad="")
    with pytest.raises(ValueError, match="trazabilidad"):
        _dato_valido(trazabilidad="   ")


@pytest.mark.parametrize("campo",
                         ["concepto", "procedimiento", "fuente", "ambito"])
def test_la_guardia_exige_los_campos_con_que_un_S_se_reproduce(campo):
    with pytest.raises(ValueError, match=campo):
        _dato_valido(**{campo: ""})


def test_la_guardia_rechaza_un_dato_sin_modo_de_resolucion():
    """Sec. 4.3: ninguna variable de entrada se queda sin modo."""
    with pytest.raises(ValueError, match="resolucion"):
        _dato_valido(resolucion=None)


def test_un_dato_de_sitio_no_se_elige_ni_se_compra():
    """
    `libre` seria un dato de sitio que alguien DECIDE -- y entonces es un
    criterio [A] -- y `de_catalogo` un hecho del terreno comprado a un
    proveedor. Los dos modos estan cerrados para esta poblacion.
    """
    with pytest.raises(ValueError, match="libre"):
        _dato_valido(resolucion=ds.Libre(que_lo_fija="alguien"))
    with pytest.raises(ValueError, match="de_catalogo"):
        _dato_valido(resolucion=ds.DeCatalogo(catalogo_id="X", que_elige="y",
                                              advertencia="z"))


def test_el_barrido_al_importar_da_el_mensaje_con_la_clave(monkeypatch):
    """
    `__post_init__` no puede conocer la clave del diccionario -- a esa altura
    la entrada todavia no tiene nombre --, y el barrido si. Por eso los dos
    existen y no sobra ninguno.
    """
    malo = DatoSitio.__new__(DatoSitio)      # sin pasar por __post_init__
    object.__setattr__(malo, "valor", 1.0)
    for campo, v in (("concepto", "c"), ("procedimiento", "p"),
                     ("fuente", "f"), ("trazabilidad", ""),
                     ("ambito", ds.AMBITO_CORREDOR), ("etiqueta", "S"),
                     ("reemplazado_por", None), ("verificacion_pendiente", None),
                     ("resolucion", None)):
        object.__setattr__(malo, campo, v)
    monkeypatch.setitem(DATOS_SITIO, "dato_de_prueba", malo)
    with pytest.raises(ValueError, match="dato_de_prueba"):
        ds._coherencia_de_datos_sitio()


def test_la_guardia_es_simetrica_con_la_de_criterios():
    """
    Lo que cerraba SIS-D-09: los dos archivos declaran la misma regla y ahora
    los dos la hacen cumplir al importar. La simetria se comprueba sobre el
    MISMO objeto conceptual -- un [S] sin trazabilidad -- por los dos caminos.

    Los caminos no son identicos y no tienen por que serlo: `criterios_adoptados`
    valida en `_verificar_criterio`, al que llegan sus tres vias de escritura, y
    `datos_sitio` valida en el constructor, que es su unica via. Lo que se exige
    aqui es que el resultado sea el mismo, no que el mecanismo lo sea.
    """
    sin_trazabilidad = ca.Criterio(
        valor=1.0, etiqueta="S", concepto="c", justificacion="j", fuente="f",
        trazabilidad="",
        resolucion=ca.DeEnsayo(ensayo="e", trazabilidad_exigida="te"))
    with pytest.raises(ValueError, match="trazabilidad"):
        ca._verificar_criterio("criterio_de_prueba", sin_trazabilidad)
    with pytest.raises(ValueError, match="trazabilidad"):
        _dato_valido(trazabilidad="")


def test_cada_dato_declara_como_se_resuelve():
    """Sec. 4.3, criterio de salida: ninguna variable de entrada sin modo."""
    for clave, d in DATOS_SITIO.items():
        assert d.resolucion is not None, clave
        ds.modo_de(d.resolucion)          # levanta si no es de la familia


def test_el_unico_dato_derivado_es_el_factor_de_zona_de_E030():
    """
    `Z_E030` no se lee de ningun mapa: se DERIVA de la zona sismica entrando
    en la tabla del Art. 11.1. Sin el modo, la ventana ofreceria editarlo como
    si fuera una lectura independiente, y un Z cambiado sin cambiar la zona
    contradice la tabla.
    """
    derivados = {k: d.resolucion for k, d in DATOS_SITIO.items()
                 if isinstance(d.resolucion, ds.Derivada)}
    assert set(derivados) == {"Z_E030"}
    assert derivados["Z_E030"].de == ("ZONA_SISMICA_LA_UNION",)
    assert derivados["Z_E030"].de[0] in DATOS_SITIO


@pytest.mark.parametrize("no_finito", [float("inf"), float("-inf"), float("nan")])
def test_ningun_dato_de_sitio_admite_un_numero_no_finito(no_finito):
    """
    La hermana que faltaba de `criterios_adoptados._verificar_finitud`. La
    asimetria entre las dos guardias es lo que la delato: este archivo declara
    que `_verificar_dato` es "hermana de `_verificar_criterio`, y con el mismo
    caracter", y una comprobaba la finitud y la otra no.

    Aqui el argumento es mas fuerte que en los criterios: un dato de sitio es
    una LECTURA -- un mapa, un ensayo, una medicion --, y ninguna lectura
    devuelve un infinito. Un [S] no finito no es un valor extremo: es una
    transcripcion rota.
    """
    from dataclasses import replace

    base = ds.DATOS_SITIO["PGA_roca_B"]
    with pytest.raises(ValueError, match="infinito ni un NaN"):
        ds._verificar_dato(replace(base, valor=no_finito))


def test_la_guardia_de_finitud_del_sitio_mira_dentro_de_las_estructuras():
    """Un inf escondido en una tupla entra al calculo igual que uno suelto."""
    from dataclasses import replace

    base = ds.DATOS_SITIO["PGA_roca_B"]
    with pytest.raises(ValueError, match="infinito ni un NaN"):
        ds._verificar_dato(replace(base, valor=(0.5, float("inf"))))


def test_la_guardia_de_finitud_del_sitio_no_molesta_a_los_datos_reales():
    """Los datos declarados hoy la atraviesan: la guardia no cambia nada."""
    for nombre, dato in ds.DATOS_SITIO.items():
        ds._verificar_dato(dato)


# ---------------------------------------------------------------------------
# Las dos ramas de `_verificar_dato` que ninguna prueba alcanzaba (SIS-F-10)
# ---------------------------------------------------------------------------
# La guardia de este archivo tiene seis ramas y la suite alcanzaba cuatro. Las
# dos que faltaban son las que miran DENTRO de la resolucion: un `de_ensayo`
# que no dice que trazabilidad hay que exigirle a la lectura y una `derivada`
# que no dice de que se deriva. Las dos dejan un dato de sitio que parece
# declarado y no se puede reproducir, que es exactamente lo que la etiqueta
# [S] existe para impedir -- y borrarlas no rompia ninguna prueba.
#
# Van con la misma forma de tabla que las de arriba: la resolucion incompleta
# y el trozo del motivo que dice POR QUE, no solo que fallo.

@pytest.mark.parametrize("resolucion, motivo", [
    (ds.DeEnsayo(ensayo="e", trazabilidad_exigida=""),
     "no dice que trazabilidad"),
    (ds.Derivada(de=(), regla="r"),
     "no dice de que se deriva"),
])
def test_la_guardia_mira_dentro_de_la_resolucion_y_no_solo_su_tipo(
        resolucion, motivo):
    """
    Falla si la guardia se conforma con que la resolucion sea de la familia
    admitida. El modo correcto con los campos vacios es peor que no declarar
    modo: la ventana abre la pestana de ensayo sin decir que exigirle a la
    lectura, o pinta un derivado sin decir de que, y la memoria escribe una
    trazabilidad que nadie puede seguir.

    `_dato_valido` ya trae `trazabilidad` de la ENTRADA rellena, de modo que
    lo que estas dos filas aislan es la trazabilidad de la RESOLUCION, que es
    otra cosa: una dice como se leyo el valor, la otra que hay que exigirle a
    quien repita la lectura.
    """
    with pytest.raises(ValueError, match=motivo):
        _dato_valido(resolucion=resolucion)


def test_una_resolucion_completa_de_las_dos_familias_no_levanta():
    """
    La contraparte que hace de las dos filas de arriba una prueba y no una
    tautologia: con los campos llenos, los mismos dos modos se construyen sin
    una queja. Falla si alguien "arregla" la guardia rechazando el modo
    entero en vez de su campo vacio.
    """
    _dato_valido(resolucion=ds.DeEnsayo(ensayo="e", trazabilidad_exigida="te"))
    _dato_valido(resolucion=ds.Derivada(de=("ZONA_SISMICA_LA_UNION",),
                                        regla="r"))


# --- y las dos ramas de la guardia de finitud que quedaron sin recorrer ----

@pytest.mark.parametrize("valor_roto", [
    10 ** 400,                          # el entero suelto
    {"lectura": 10 ** 400},             # el mismo, dentro de un dict
])
def test_la_guardia_de_finitud_del_sitio_atrapa_el_entero_sin_tope(valor_roto):
    """
    Un `int` de Python no tiene tope y `float(x)` sobre uno de 401 cifras
    lanza OverflowError, que NO es `math.isfinite` devolviendo False: sin el
    `except`, la guardia de finitud moriria con una excepcion que no es de la
    taxonomia -- ni ValueError de arquitectura ni ErrorProyecto -- y el
    archivo dejaria de importarse con una traza en vez de con su mensaje.

    La segunda fila recorre ademas la rama de DICCIONARIO de `_numeros_de`:
    la finitud no puede depender de la FORMA del valor, y un [S] cuyo valor
    sea un mapa (una lectura por estrato, por ejemplo) tiene que mirarse
    dentro igual que una tupla.
    """
    from dataclasses import replace

    base = ds.DATOS_SITIO["PGA_roca_B"]
    with pytest.raises(ValueError, match="infinito ni un NaN"):
        ds._verificar_dato(replace(base, valor=valor_roto))
