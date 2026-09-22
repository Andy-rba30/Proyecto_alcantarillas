"""
tests/test_cierre_c10.py
========================
Aceptacion del cierre del cluster C10 que la cadena EXT dejo abierto o parcial
(sesion de cierre del 2026-09-22): C5-02, PC-27 y PC-32. Escritos PRIMERO en
rojo con `xfail(strict=True)` y liberados al corregir.

  C5-02  `ke_entrada` (tubo) declara un NUMERO y `ke_entrada_cajon` una fila.
         Lo que reabrio la ficha --la procedencia que mentia y el -50-- lo
         cerro EXT-1; lo que quedaba era que `M4.ke_declarado` devolviera los
         tres rotulos VACIOS para el tubo, o sea una memoria que no dice de
         que fila salio el 0.5. La forma NO se migra (decision: el unico
         criterio `float` resuelto `de_tabla` es el que sostienen el editor
         de E-B, el barrido de PF-3 y `declarar_desde_tabla`); lo que cambia
         es que la FILA viaja en la resolucion (`DeTabla.fila_id`) o en la
         procedencia de la declaracion, el consumidor comprueba que el numero
         ES la celda de esa fila y la memoria imprime fila, agrupacion y
         bloque. Un numero que no es la celda se declara como tal.
  PC-27  Tres capas del estado de verificacion (`Verificacion.cumple`,
         `TipoDeVeredicto` del paso, `Bloqueo`) sin una fuente unica y sin
         «no aplica». Ahora `Verificacion.estado` (`EstadoDeVerificacion`) es
         LA fuente: `cumple` es su vista, el veredicto del paso tiene que
         decir lo mismo, el JSON lo lleva, y NO_APLICA existe con un
         productor real: V5 en la Familia C, SUSTITUIDA por VC1.
  PC-32  `factor_esviaje` no tiene cota: 89.9 grados dan 10 313 m. La cota
         es un valor de proyecto sin fuente: criterio [A] de perfil
         `esviaje_max_grados`, opcional, leido con `valor_si_declarado`; sin
         declarar nada cambia, declarado detiene con DatoInvalidoError.
"""
from __future__ import annotations

import ast
import math
import json
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import declaracion as dec
from src import servicio
from src.constantes_normativas import KE_HDS5_C2
from src import modelos
from src.modelos import (DatoInvalidoError, Familia, TipoDeVeredicto,
                         Verificacion, Veredicto)
EstadoDeVerificacion = getattr(modelos, "EstadoDeVerificacion", None)   # en rojo no existe
from src.tolerancias import TOL_COMPARADOR_REL
from src.modulos import M4_control as M4
from src.modulos import M5_verificaciones as M5
from src.modulos import M7_geometria as M7
from src.modulos import M11_reporte as M11
from tests.apoyo.aproximacion import REL_TRANSPORTE

# `pytestmark = pytest.mark.xfail(strict=True)` medido en rojo antes de tocar
# codigo: 12 xfailed y 2 XPASS (los dos invariantes). Liberado al corregir.

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"

FILA_TUBO = "concreto_headwall_square_edge"
FILA_METAL = "cm_headwall_square_edge"
FILA_CAJON = "cajon_aletas_paralelas_escuadra"
CLAVE_ESVIAJE = "esviaje_max_grados"


@pytest.fixture
def limpio():
    ca.limpiar_valores_dinamicos()
    dec.limpiar()
    yield
    ca.limpiar_valores_dinamicos()
    dec.limpiar()


# ===========================================================================
# C5-02
# ===========================================================================

def test_c502_el_ke_del_tubo_trae_su_fila_agrupacion_y_bloque():
    """El 0.5 del archivo sale de una fila, y `ke_declarado` la nombra."""
    fila, agrupacion, bloque, ke = M4.ke_declarado(M4.CRITERIO_KE)
    esperada = KE_HDS5_C2[FILA_TUBO]
    assert ke == pytest.approx(esperada["ke"], rel=REL_TRANSPORTE)
    assert (fila, agrupacion, bloque) == (
        esperada["fila"], esperada["agrupacion"], esperada["bloque"])
    assert ca.CRITERIOS[M4.CRITERIO_KE].resolucion.fila_id == FILA_TUBO


def test_c502_declarado_desde_otra_fila_de_tubo_la_memoria_dice_esa_fila(limpio):
    dec.declarar_desde_tabla(M4.CRITERIO_KE, KE_HDS5_C2[FILA_METAL]["ke"],
                             filas=(FILA_METAL,))
    fila, agrupacion, bloque, ke = M4.ke_declarado(M4.CRITERIO_KE)
    assert fila == KE_HDS5_C2[FILA_METAL]["fila"]
    assert bloque == KE_HDS5_C2[FILA_METAL]["bloque"]
    assert ke == pytest.approx(0.5, rel=REL_TRANSPORTE)


def test_c502_un_numero_que_no_es_la_celda_no_hereda_los_rotulos(limpio):
    """Declarado 0.7 con nota (DIFIERE de la celda): no se atribuye a la fila."""
    dec.declarar_desde_tabla(M4.CRITERIO_KE, 0.7, filas=(FILA_TUBO,),
                             nota="adopcion mas conservadora que la celda")
    fila, agrupacion, bloque, ke = M4.ke_declarado(M4.CRITERIO_KE)
    assert ke == pytest.approx(0.7, rel=REL_TRANSPORTE)
    assert fila == "" and agrupacion == "" and bloque == ""


def test_c502_una_fila_de_cajon_no_vale_para_el_tubo(limpio):
    """La simetrica de NOR-HID-01: el tubo no puede citar una fila de marco."""
    # Dos capas. La primera ya existia: toda fila de cajon de la Tabla C.2
    # depende de 'embocadura_cajon' y R4 la hace inelegible desde la ventana
    # de declaracion. La segunda es la de C5-02: si una fila de cajon llega
    # al consumidor del tubo por cualquier otra via, el CONSUMIDOR la rechaza.
    with pytest.raises(ValueError, match="R4"):
        dec.declarar_desde_tabla(M4.CRITERIO_KE, KE_HDS5_C2[FILA_CAJON]["ke"],
                                 filas=(FILA_CAJON,))
    ca.establecer_valor_dinamico(M4.CRITERIO_KE, KE_HDS5_C2[FILA_CAJON]["ke"])
    original = M4._fila_del_ke_numerico
    M4._fila_del_ke_numerico = lambda clave: FILA_CAJON
    try:
        with pytest.raises(DatoInvalidoError) as exc:
            M4.ke_declarado(M4.CRITERIO_KE)
    finally:
        M4._fila_del_ke_numerico = original
    assert "Box" in exc.value.motivo or "cajon" in exc.value.motivo.lower()


def test_c502_la_memoria_imprime_la_fila_del_tubo():
    externos = cli.cargar_datos_externos(
        EXTERNOS_AMPLIADOS, {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
                             "L_hidraulico_m": None, "categoria_tr": None})
    informe = servicio.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_EXPEDIENTE)
    memoria = M11.memoria_html(informe, proyecto="c10")
    assert "declarado como NUMERO: la fila de la Tabla C.2" not in memoria
    assert KE_HDS5_C2[FILA_TUBO]["fila"] in memoria
    assert KE_HDS5_C2[FILA_TUBO]["agrupacion"] in memoria


# ===========================================================================
# PC-27
# ===========================================================================

def _v(cumple, estado=None, veredicto=None, **kw):
    paso = None
    if veredicto is not None:
        from src.modelos import Magnitud, PasoDeMemoria, Umbral
        umbral = Umbral(descripcion="d", valor=1.0, unidad="-",
                        cita_id="HDS5_3ED.5.3.3#INDICADORES",
                        caracter="definicion", aplicacion="a")
        paso = PasoDeMemoria(
            que="prueba", por_que="prueba", formula="x",
            sustitucion=(), resultado=Magnitud("x", 1.0, "", "prueba"),
            umbral=umbral, citas_textuales=("HDS5_3ED.5.3.3#INDICADORES",),
            veredicto=Veredicto(tipo=veredicto))
    return Verificacion(cumple=cumple, numeral="n", valor_obtenido=1.0,
                        valor_admisible=1.0, criterio_aplicado=None,
                        estado=estado, paso=paso, **kw)


def test_pc27_el_estado_es_la_fuente_y_cumple_su_vista():
    assert _v(True).estado is EstadoDeVerificacion.CUMPLE
    assert _v(False).estado is EstadoDeVerificacion.NO_CUMPLE
    v = _v(True, estado=EstadoDeVerificacion.NO_APLICA, motivo_no_aplica="VC1")
    assert v.cumple is True and v.estado.cumple is True
    with pytest.raises(ValueError, match="motivo_no_aplica"):
        _v(True, estado=EstadoDeVerificacion.NO_APLICA)   # sin decir por que
    assert EstadoDeVerificacion.NO_CUMPLE.cumple is False
    assert EstadoDeVerificacion.INDICADOR.cumple is True
    with pytest.raises(ValueError, match="estado"):
        _v(False, estado=EstadoDeVerificacion.CUMPLE)
    with pytest.raises(ValueError, match="estado"):
        _v(True, estado=EstadoDeVerificacion.NO_CUMPLE)


def test_pc27_el_veredicto_del_paso_dice_lo_mismo_que_el_estado():
    assert _v(True, veredicto=TipoDeVeredicto.INDICADOR).estado is \
        EstadoDeVerificacion.INDICADOR
    assert _v(False, veredicto=TipoDeVeredicto.NO_CUMPLE).estado is \
        EstadoDeVerificacion.NO_CUMPLE
    with pytest.raises(ValueError, match="veredicto"):
        _v(True, veredicto=TipoDeVeredicto.NO_CUMPLE)
    with pytest.raises(ValueError, match="veredicto"):
        _v(False, veredicto=TipoDeVeredicto.CUMPLE)
    assert EstadoDeVerificacion.de_veredicto(TipoDeVeredicto.CUMPLE) is \
        EstadoDeVerificacion.CUMPLE
    assert EstadoDeVerificacion.de_veredicto(TipoDeVeredicto.SIN_VEREDICTO) is None


def test_pc27_no_aplica_existe_y_tiene_productor_v5_en_familia_c():
    punto = next(p for p in servicio.cargar_puntos(CSV_PERFIL) if p.familia is Familia.C)
    v = M5.v5_no_aplica_en_canal(punto=punto)
    assert v.estado is EstadoDeVerificacion.NO_APLICA
    assert v.cumple is True and v.codigo == "V5"
    assert "VC1" in v.motivo_no_aplica
    fuente = ast.unparse(_funcion(RAIZ / "src" / "servicio.py", "_verificador_perfil")
                         ) + ast.unparse(_funcion(RAIZ / "src" / "servicio.py", "_fase_diseno"))
    assert "v5_no_aplica_en_canal" in fuente or "v5_no_aplica_en_canal" in ast.unparse(
        ast.parse((RAIZ / "src" / "servicio.py").read_text(encoding="utf-8")))


def test_pc27_el_json_y_la_memoria_llevan_el_estado():
    v = _v(True, estado=EstadoDeVerificacion.NO_APLICA, codigo="V5",
           motivo_no_aplica="sustituida por VC1")
    fila = cli._verificacion_json("Fase 5", v)
    assert fila["estado"] == "no aplica" and fila["cumple"] is True
    marca = M11._marca_de_verificacion(v)
    assert M11.MARCA_NO_APLICA in marca
    assert M11.MARCA_CUMPLE not in marca


def test_pc27_la_estabilidad_del_cabezal_no_admite_el_conjunto_vacio():
    from src.modelos import CondicionAnalisis, EstabilidadCabezal, GeometriaCabezal
    geometria = GeometriaCabezal(H=2.00, B=1.60, D_f=1.00, espesor_corona=0.25,
                                 espesor_base_muro=0.35, espesor_zapata=0.40)
    with pytest.raises(ValueError, match="vacio"):
        EstabilidadCabezal(condicion=CondicionAnalisis.ESTATICO, geometria=geometria,
                           verificaciones=(), exigidas=("E1",))


# ===========================================================================
# PC-32
# ===========================================================================

def test_pc32_el_criterio_de_esviaje_maximo_existe_como_A_de_perfil_opcional():
    c = ca.CRITERIOS[CLAVE_ESVIAJE]
    assert c.valor is None and c.opcional and c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_PERFIL and c.sensibilidad and c.resolucion is not None
    assert c.forma == ca.FORMA_FLOAT


def _punto_con_esviaje(grados):
    from dataclasses import replace
    punto = next(p for p in servicio.cargar_puntos(CSV_EJEMPLO) if p.id == "A-01")
    return replace(punto, esviaje_grados=grados)


def test_pc32_sin_declarar_nada_cambia(limpio):
    assert M7.factor_esviaje(_punto_con_esviaje(89.9)) == pytest.approx(
        1 / math.cos(math.radians(89.9)), rel=TOL_COMPARADOR_REL)


def test_pc32_declarado_detiene_por_encima_y_deja_pasar_por_debajo(limpio):
    ca.establecer_valor_dinamico(CLAVE_ESVIAJE, 45.0)
    assert M7.factor_esviaje(_punto_con_esviaje(30.0)) == pytest.approx(
        1 / math.cos(math.radians(30.0)), rel=TOL_COMPARADOR_REL)
    with pytest.raises(DatoInvalidoError) as exc:
        M7.factor_esviaje(_punto_con_esviaje(60.0))
    assert CLAVE_ESVIAJE in exc.value.motivo and "45" in exc.value.motivo
    assert exc.value.campo == "esviaje_grados"
    # La frontera es INCLUSIVA (`not e <= max + TOL`): el esviaje igual al
    # maximo declarado pasa. Sin este caso el mutante `not e < max`
    # sobrevivia a 701 tests (auditor adversarial de C10).
    assert M7.factor_esviaje(_punto_con_esviaje(45.0)) == pytest.approx(
        1 / math.cos(math.radians(45.0)), rel=TOL_COMPARADOR_REL)


def test_pc27_la_fila_no_aplica_no_imprime_el_hueco_del_derecho_de_via():
    """
    Auditor de C10: en C-01 dimensionado, la memoria imprimia para V5 el
    hueco censado «sin fundamento normativo declarado» (el remanso del
    derecho de via) ENCIMA de la fila «no aplica», y la traza de la GUI lo
    mismo. Lo falso: V5 no tiene paso porque no aplica, no porque le falte
    fundamento.
    """
    from src import traza_punto as tp
    punto = next(p for p in servicio.cargar_puntos(CSV_PERFIL)
                 if p.familia is Familia.C)
    v = M5.v5_no_aplica_en_canal(punto=punto)
    desarrollo = M11.desarrollo_de_verificaciones(_InformeMinimo(punto, v))
    assert [c for c, _ in desarrollo] == ["V5"]
    assert isinstance(desarrollo[0][1], M11.NoAplica)
    html = M11._no_aplica_html(desarrollo[0][1])
    assert "VC1" in html and "sin fundamento" not in html
    traza = tp.traza_del_punto(_InformeMinimo(punto, v))
    entradas = [e for sec in traza.secciones for e in sec.entradas
                if e.codigo == "V5"]
    assert len(entradas) == 1
    assert isinstance(entradas[0], tp.NoAplicaDeVerificacion)
    assert entradas[0].titulo == tp.TITULO_NO_APLICA
    assert not isinstance(entradas[0], tp.HuecoDeVerificacion)
    # Y la celda de umbral de la tabla no dice «[N] constante normativa».
    tabla = M11._tabla_verificaciones(_InformeMinimo(punto, v))
    fila_v5 = tabla[tabla.index("<td>V5</td>"):]
    fila_v5 = fila_v5[:fila_v5.index("</tr>")]
    assert "constante normativa" not in fila_v5
    assert M11.MARCA_NO_APLICA in fila_v5


def test_pc27_la_cli_de_texto_no_marca_ok_lo_que_no_aplica():
    punto = next(p for p in servicio.cargar_puntos(CSV_PERFIL)
                 if p.familia is Familia.C)
    v = M5.v5_no_aplica_en_canal(punto=punto)
    lineas = cli._lineas_verificaciones(_InformeMinimo(punto, v))
    linea_v5 = [l for l in lineas if " V5 " in l][0]
    assert cli.MARCA_NO_APLICA in linea_v5
    assert cli.MARCA_CUMPLE not in linea_v5
    assert any("VC1" in l for l in lineas)


class _InformeMinimo:
    """
    Lo minimo que M11, la traza y la CLI leen de un `InformePunto` para
    publicar UNA verificacion: el punto, `verificaciones()` y lo demas vacio.
    """

    def __init__(self, punto, verificacion):
        self.punto = punto
        self._v = verificacion
        self.dimensionado = False
        self.clasificacion = None
        self.bloqueos = ()
        self.iteraciones = ()
        self.resultado = None
        self.geometria = None

    def verificaciones(self):
        return [("Fase 5 - Verificaciones (M5)", self._v)]


def test_pc32_la_puerta_rechaza_un_maximo_fuera_del_dominio(limpio):
    for malo in (-5.0, 95.0):
        with pytest.raises(ValueError):
            ca.establecer_valor_dinamico(CLAVE_ESVIAJE, malo)


def _funcion(ruta: Path, nombre: str):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
    for n in ast.walk(arbol):
        if isinstance(n, ast.FunctionDef) and n.name == nombre:
            return n
    return ast.parse("pass")
