"""
tests/test_cierre_c05.py
========================
Aceptacion del CIERRE del cluster C05 --- lo que EXT-0 y EXT-6 dejaron
abierto de PC-24 y R48-030 ---, escrita PRIMERO EN ROJO y liberada al
corregir.

PC-24 (ficha EXT-3-01): la v8 §4.1 ya dice que en V1 y V2 «el deber de
verificar es [N]» y «el valor aplicado como umbral duro es [A]», porque las
dos cifras llegan con «se recomienda» (pags. impresas 77 y 79). El codigo
seguia aplicando `Y_SOBRE_D_MAX` y `V_MIN` como [N] puros, con
`criterio_aplicado=None`. Lo que cierra: dos criterios [A] de PERFIL con
valor --- el valor por defecto es el que la fuente recomienda, y la tabla y
la eleccion se separan como manda CLAUDE.md: la cifra sigue en
`constantes_normativas.py` como [N] (la escribe el Manual) y la ADOPCION en
`criterios_adoptados.py` ---, leidos por M5 con el mismo contrato que
'riesgo_admisible_propietario': solo se pueden ENDURECER. Un y/D maximo por
encima de 0.75 o un piso de velocidad por debajo de 0.25 m/s se rechazan en
el consumidor con DatoInvalidoError, porque relajar una recomendacion no es
ejercer una adopcion: es salirse de lo que la fuente concede.

R48-030: la v8 seguia escribiendo «PPI/FHWA, valor por extraer» en seis
sitios (§0.1, §0.3, Tablero 2.x del TMC, fila V3 de la Fase 5, Tablero 1.3
y Anexo A) mientras 'v_max_tmc' y 'v_max_hdpe' llevaban 4.572 m/s de WSDOT
M 23-03.12 Tabla 8-4 y declaraban «DISCREPANCIA ABIERTA CON LA HOJA DE
RUTA». Lo que cierra: la hoja de ruta enmendada en los seis sitios (con
«Corregido desde») y la ficha de los dos criterios sin la discrepancia.
"""

import ast
from pathlib import Path

import pytest

from src import criterios_adoptados as ca
from src.constantes_normativas import (UMBRALES_POR_CODIGO, V_MIN,
                                       Y_SOBRE_D_MAX)
from src.modelos import DatoInvalidoError, Familia, TipoMaterial
from src.modulos import M5_verificaciones as M5
from src.modulos import M11_reporte as M11
from src.modulos.M2_material import catalogo
from src.tolerancias import TOL_UMBRAL_NORMATIVO
from tests.apoyo.aproximacion import REL_TRANSPORTE

from tests.test_M5_verificaciones import _punto, _resultado

RAIZ = Path(__file__).resolve().parents[1]
CLAVE_V1 = "borde_libre_y_sobre_d_max"
CLAVE_V2 = "velocidad_minima_autolimpieza_m_s"


@pytest.fixture
def limpio():
    ca.limpiar_valores_dinamicos()
    yield
    ca.limpiar_valores_dinamicos()


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


# ===========================================================================
# PC-24: los dos [A] existen, son de perfil, y valen lo que la fuente recomienda
# ===========================================================================

@pytest.mark.parametrize("clave,constante,unidad", [
    (CLAVE_V1, Y_SOBRE_D_MAX, "-"),
    (CLAVE_V2, V_MIN, "m/s"),
])
def test_pc24_el_criterio_existe_es_A_de_perfil_y_vale_lo_recomendado(clave, constante, unidad):
    c = ca.CRITERIOS[clave]
    assert c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_PERFIL
    assert c.forma == ca.FORMA_FLOAT
    assert c.valor == pytest.approx(constante, rel=REL_TRANSPORTE)
    assert c.sensibilidad is not None and c.resolucion is not None
    assert not c.opcional
    # La FUENTE de la ficha dice que la cifra es una recomendacion.
    assert "recomienda" in (c.fuente + c.justificacion).lower()


def _asignacion_de_modulo(ruta: Path, nombre: str):
    """El valor asignado a `nombre` en el nivel superior del modulo, por AST."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == nombre for t in nodo.targets):
            return nodo.value
    return None


def _nombre_del_valor_del_criterio(clave: str):
    """
    El nodo `valor=` de la entrada `clave` del dict CRITERIOS, por AST (PC-21:
    una afirmacion sobre codigo no se hace sobre texto).
    """
    ruta = RAIZ / "src" / "criterios_adoptados.py"
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Dict):
            for k, v in zip(nodo.keys, nodo.values):
                if (isinstance(k, ast.Constant) and k.value == clave
                        and isinstance(v, ast.Call)):
                    for kw in v.keywords:
                        if kw.arg == "valor":
                            return kw.value
    return None


def test_pc24_la_cifra_sigue_siendo_N_en_constantes_y_la_adopcion_A_en_criterios():
    """Tabla y eleccion separadas: el 0.75 y el 0.25 no se mueven de sitio."""
    constantes = RAIZ / "src" / "constantes_normativas.py"
    y_max = _asignacion_de_modulo(constantes, "Y_SOBRE_D_MAX")
    v_min = _asignacion_de_modulo(constantes, "V_MIN")
    assert isinstance(y_max, ast.Constant) and y_max.value == pytest.approx(
        Y_SOBRE_D_MAX, rel=REL_TRANSPORTE)
    assert isinstance(v_min, ast.Constant) and v_min.value == pytest.approx(
        V_MIN, rel=REL_TRANSPORTE)
    # El valor del criterio se toma DE la constante, no se copia el literal.
    valor_v1 = _nombre_del_valor_del_criterio(CLAVE_V1)
    valor_v2 = _nombre_del_valor_del_criterio(CLAVE_V2)
    assert isinstance(valor_v1, ast.Name) and valor_v1.id == "Y_SOBRE_D_MAX"
    assert isinstance(valor_v2, ast.Name) and valor_v2.id == "V_MIN"


# ===========================================================================
# PC-24: M5 los lee, los declara en la fila y solo se pueden endurecer
# ===========================================================================

def test_pc24_v1_declara_el_criterio_aplicado_y_su_umbral(concreto):
    v = M5.v1_borde_libre(D=0.90, material=concreto, punto=_punto(),
                          resultado=_resultado(y_normal=0.60))
    assert v.cumple
    assert v.criterio_aplicado == CLAVE_V1
    assert v.paso.umbral.criterio_aplicado == CLAVE_V1
    assert v.valor_admisible == pytest.approx(Y_SOBRE_D_MAX, rel=REL_TRANSPORTE)


def test_pc24_v2_declara_el_criterio_aplicado_y_su_umbral():
    v = M5.v2_velocidad_minima(resultado=_resultado(V=1.5))
    assert v.cumple
    assert v.criterio_aplicado == CLAVE_V2
    assert v.paso.umbral.criterio_aplicado == CLAVE_V2
    assert v.valor_admisible == pytest.approx(V_MIN, rel=REL_TRANSPORTE)


def test_pc24_endurecer_v1_cambia_el_veredicto(limpio, concreto):
    """y/D = 0.70 cumple con 0.75 y NO cumple con un 0.65 declarado."""
    resultado = _resultado(y_normal=0.63)          # y/D = 0.70 con D = 0.90
    assert M5.v1_borde_libre(D=0.90, material=concreto, punto=_punto(),
                             resultado=resultado).cumple
    ca.establecer_valor_dinamico(CLAVE_V1, 0.65)
    v = M5.v1_borde_libre(D=0.90, material=concreto, punto=_punto(),
                          resultado=resultado)
    assert not v.cumple
    assert v.valor_admisible == pytest.approx(0.65, rel=REL_TRANSPORTE)
    assert v.paso.umbral.valor == pytest.approx(0.65, rel=REL_TRANSPORTE)


def test_pc24_endurecer_v2_cambia_el_veredicto(limpio):
    """V = 0.30 m/s cumple con 0.25 y NO cumple con un 0.35 declarado."""
    assert M5.v2_velocidad_minima(resultado=_resultado(V=0.30)).cumple
    ca.establecer_valor_dinamico(CLAVE_V2, 0.35)
    v = M5.v2_velocidad_minima(resultado=_resultado(V=0.30))
    assert not v.cumple
    assert v.valor_admisible == pytest.approx(0.35, rel=REL_TRANSPORTE)


@pytest.mark.parametrize("clave,laxo", [(CLAVE_V1, 0.80), (CLAVE_V2, 0.20)])
def test_pc24_relajar_la_recomendacion_se_rechaza_en_el_consumidor(limpio, concreto, clave, laxo):
    """
    El mismo contrato que 'riesgo_admisible_propietario' en M1: la
    recomendacion es un extremo y solo se puede endurecer. Un y/D maximo
    mayor que 0.75 o un piso menor que 0.25 m/s no son una adopcion: son
    salirse de lo que la fuente concede, y el consumidor lo dice.
    """
    ca.establecer_valor_dinamico(clave, laxo)
    with pytest.raises(DatoInvalidoError) as exc:
        if clave == CLAVE_V1:
            M5.v1_borde_libre(D=0.90, material=concreto, punto=_punto(),
                              resultado=_resultado(y_normal=0.60))
        else:
            M5.v2_velocidad_minima(resultado=_resultado(V=1.5))
    assert exc.value.campo == clave
    assert "recomienda" in exc.value.motivo.lower()


def test_pc24_la_igualdad_con_la_recomendacion_pasa(limpio, concreto):
    """Declarar exactamente el valor recomendado no es relajarlo."""
    ca.establecer_valor_dinamico(CLAVE_V1, Y_SOBRE_D_MAX)
    ca.establecer_valor_dinamico(CLAVE_V2, V_MIN)
    assert M5.v1_borde_libre(D=0.90, material=concreto, punto=_punto(),
                             resultado=_resultado(y_normal=0.60)).cumple
    assert M5.v2_velocidad_minima(resultado=_resultado(V=1.5)).cumple
    # Y la banda de tolerancia va del lado que concede, no del que relaja.
    ca.establecer_valor_dinamico(CLAVE_V1, Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO / 2)
    assert M5.v1_borde_libre(D=0.90, material=concreto, punto=_punto(),
                             resultado=_resultado(y_normal=0.60)).cumple


# ===========================================================================
# PC-24: lo que la memoria y el bloque de umbrales dicen
# ===========================================================================

def test_pc24_el_bloque_de_umbrales_nombra_los_dos_criterios():
    assert CLAVE_V1 in UMBRALES_POR_CODIGO["V1"]["aplicacion"]
    assert CLAVE_V2 in UMBRALES_POR_CODIGO["V2"]["aplicacion"]


def test_pc24_la_fila_de_v1_en_la_memoria_lleva_la_etiqueta_A(concreto):
    v = M5.v1_borde_libre(D=0.90, material=concreto, punto=_punto(),
                          resultado=_resultado(y_normal=0.60))

    class _Informe:
        punto = _punto()
        dimensionado = True
        bloqueos = ()

        def verificaciones(self):
            return [("Fase 5 - Verificaciones (M5)", v)]

    tabla = M11._tabla_verificaciones(_Informe())
    fila = tabla[tabla.index("<td>V1</td>"):]
    fila = fila[:fila.index("</tr>")]
    assert CLAVE_V1 in fila
    assert "constante normativa" not in fila


# ===========================================================================
# R48-030: la hoja de ruta ya no dice «por extraer»
# ===========================================================================

def test_r48030_la_hoja_de_ruta_no_dice_por_extraer_en_ningun_sitio():
    hoja = M11.ruta_hoja_de_ruta().read_text(encoding="utf-8")
    # «por extraer» solo puede sobrevivir como cita de la redaccion vieja,
    # dentro de una nota «Corregido desde».
    for linea in hoja.splitlines():
        if "por extraer" in linea:
            assert "orregido desde" in linea, linea[:120]
            assert "R48-030" in linea, linea[:120]
    assert "PPI / FHWA |" not in hoja
    # Los seis sitios nombran la fuente real y el valor.
    assert hoja.count("M 23-03.12") >= 6
    assert hoja.count("4.572") >= 5
    assert hoja.count("R48-030") >= 6


def test_r48030_los_criterios_ya_no_declaran_la_discrepancia_abierta():
    for clave in ("v_max_tmc", "v_max_hdpe"):
        c = ca.CRITERIOS[clave]
        assert "DISCREPANCIA ABIERTA" not in c.fuente, clave
        assert "por extraer" not in c.fuente, clave
        assert "R48-030" in c.fuente or "enmendada" in c.fuente, clave
