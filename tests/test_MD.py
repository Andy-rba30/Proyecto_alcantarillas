"""
tests/test_MD.py
================
MD contra el bucle de diseño de Sec. 2 de la guia de sesiones:

    1. el orden del recorrido: materiales de M2 en su orden, y dentro de cada
       uno el catalogo de Sec. 3.2 ASCENDENTE, desde el minimo normativo;
    2. el corte: se devuelve el PRIMER par (material, D) que pasa la Fase 5
       entera, sin seguir subiendo;
    3. el descarte: agotado el catalogo bajo el tope de la norma de producto,
       el material sale con el mensaje textual del Anexo B, "material
       descartado por diametro requerido";
    4. la salida sin solucion: DisenoNoFactibleError con el motivo del ultimo
       fallo de CADA material, nunca un resultado silencioso;
    5. lo que MD no hace: no verifica por su cuenta (lee `Verificacion.cumple`
       y nada mas) y no acepta un diseño sin verificaciones.

M5 todavia no existe en el repositorio, de modo que la Fase 5 entra aqui como
verificador inyectado -- que es tambien como MD lo declara en su interfaz. Los
verificadores de prueba son deliberadamente triviales (V1 sola, o un si/no
constante): lo que se prueba es el BUCLE, no las verificaciones.
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

from constantes_normativas import Y_SOBRE_D_MAX
from modelos import (CriterioPendienteError, DatoFaltanteError,
                     DatoInvalidoError, DisenoNoFactibleError, ErrorProyecto,
                     Familia, PuntoCritico, TipoMaterial, Verificacion)
from modulos.M0_carga import cargar_puntos
from modulos.M2_material import catalogo
from modulos.MD import (FUNCION_VERIFICACIONES, MENSAJE_DIAMETRO_SUPERADO,
                        MODULO_VERIFICACIONES, _motivo_sin_candidatos,
                        _verificador_de_M5, disenar_lote, disenar_material,
                        disenar_punto)
from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING
from tests.apoyo.aproximacion import REL_TRANSPORTE

# Contexto geometrico del punto. Son datos de la Fase 7 (L) y del Tablero 3.1
# (TW): MD los exige como argumentos y no los deriva.
L_CONDUCTO = 24.0     # m
TW_LIBRE = 0.0        # m, salida libre


def _punto(**cambios) -> PuntoCritico:
    """Punto de prueba con la fila A-01 del CSV de ejemplo como base."""
    base = dict(
        id="A-01",
        progresiva_km=0.380,
        progresiva_display="0+380",
        familia=Familia.A,
        Q_m3s=CP2_GEOMETRIA_MANNING["Q_con_n_max_esperado"],
        area_ha=850.0,
        S_cauce=CP2_GEOMETRIA_MANNING["S"],
        cota_terreno=42.10,
        cota_rasante=44.20,
        cota_subrasante=44.05,
        cbr_subrasante=8.5,
        esviaje_grados=15.0,
        ancho_plataforma=9.60,
        cota_fondo_receptor=41.30,
        Q_receptor_m3s=None,
        cota_TW=None,
        sucs_fundacion="SM",
        NF_profundidad_m=None,     # lo da el estudio geotecnico, por punto
    )
    base.update(cambios)
    return PuntoCritico(**base)


# ---------------------------------------------------------------------------
# Verificadores de prueba (sustituyen a M5)
# ---------------------------------------------------------------------------

def _verificacion(cumple: bool, obtenido=None, admisible=None) -> Verificacion:
    return Verificacion(
        cumple=cumple,
        numeral="4.1.1.3.7 b)",
        valor_obtenido=obtenido,
        valor_admisible=admisible,
        criterio_aplicado=None,
        codigo="V1",
    )


def _todo_cumple(*, punto, material, D, resultado):
    return (_verificacion(True),)


def _nada_cumple(*, punto, material, D, resultado):
    return (_verificacion(False, obtenido="lo que sea", admisible="otra cosa"),)


def _solo_borde_libre(*, punto, material, D, resultado):
    """V1 sola: y/D <= 0.75 (num. 4.1.1.3.7 b), el unico criterio del bucle."""
    y_sobre_D = resultado.y_normal / D
    return (_verificacion(y_sobre_D <= Y_SOBRE_D_MAX,
                          obtenido=y_sobre_D, admisible=Y_SOBRE_D_MAX),)


class _Registro:
    """Verificador que anota cada llamada, para leer el orden del recorrido."""

    def __init__(self, decision):
        self.decision = decision
        self.llamadas = []

    def __call__(self, *, punto, material, D, resultado):
        self.llamadas.append((material.tipo, round(D, 2)))
        return (_verificacion(self.decision(D)),)


class _RevientaMaterial:
    """
    Verificador que lanza ErrorProyecto en los materiales indicados y deja
    cumplir a los demas. Reproduce, sin depender de M5, lo que hace V7 cuando
    la clave del conducto ya no cabe bajo la subrasante: un material se cae a
    mitad del catalogo y los siguientes tienen que poder seguir intentandose.
    """

    def __init__(self, *tipos_que_revientan, desde_D=0.0,
                 exc=DatoInvalidoError, rechazan=()):
        self.tipos = set(tipos_que_revientan)
        self.rechazan = set(rechazan)     # se evaluan de verdad y no cumplen
        self.desde_D = desde_D
        self.exc = exc
        self.llamadas = []

    def __call__(self, *, punto, material, D, resultado):
        self.llamadas.append((material.tipo, round(D, 2)))
        if material.tipo in self.tipos and D >= self.desde_D:
            if self.exc is DatoInvalidoError:
                raise DatoInvalidoError("cota_subrasante", valor=44.05,
                                        id_punto=punto.id,
                                        motivo="la clave no cabe bajo la "
                                               "subrasante a este diametro")
            raise self.exc("criterio_de_prueba")
        if material.tipo in self.rechazan:
            return (_verificacion(False, obtenido="lo que sea",
                                  admisible="otra cosa"),)
        return (_verificacion(True),)


# ===========================================================================
# 1 y 2 - El recorrido y el corte
# ===========================================================================

def test_devuelve_el_primer_material_y_el_diametro_minimo_si_todo_cumple():
    resultado = disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=_todo_cumple)

    assert resultado.aceptado
    assert resultado.coherente
    assert resultado.material.tipo is TipoMaterial.CONCRETO_REFORZADO
    assert resultado.D == pytest.approx(0.90)
    assert resultado.punto.id == "A-01"
    assert resultado.motivo_rechazo is None


def test_sube_por_el_catalogo_hasta_que_la_verificacion_cumple():
    """
    Con el Q de CP-2 sobre su misma S, D = 0.90 m da exactamente y/D = 0.75 y
    V1 esta en el filo. Con un Q mayor, el minimo normativo se pasa de borde
    libre y el bucle tiene que subir un escalon, no dos.
    """
    punto = _punto(Q_m3s=CP2_GEOMETRIA_MANNING["Q_con_n_max_esperado"] * 1.15)

    resultado = disenar_punto(punto, L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=_solo_borde_libre)

    assert resultado.D == pytest.approx(1.05)
    assert resultado.resultado_hidraulico.y_normal / resultado.D <= Y_SOBRE_D_MAX
    assert all(v.cumple for v in resultado.verificaciones)


def test_el_catalogo_se_recorre_ascendente_desde_el_minimo_normativo():
    registro = _Registro(lambda D: D >= 1.35)

    resultado = disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=registro)

    assert [D for _, D in registro.llamadas] == pytest.approx(
        [0.90, 1.05, 1.20, 1.35], rel=REL_TRANSPORTE)
    assert {tipo for tipo, _ in registro.llamadas} == {TipoMaterial.CONCRETO_REFORZADO}
    assert resultado.D == pytest.approx(1.35)


def test_no_sigue_probando_despues_de_aceptar():
    registro = _Registro(lambda D: True)

    disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE, verificar=registro)

    assert len(registro.llamadas) == 1


def test_la_hidraulica_del_resultado_es_la_del_par_aceptado():
    punto = _punto()
    resultado = disenar_punto(punto, L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=_todo_cumple)
    hidraulica = resultado.resultado_hidraulico

    assert hidraulica.Q == pytest.approx(punto.Q_m3s)
    assert hidraulica.y_normal / resultado.D == pytest.approx(Y_SOBRE_D_MAX, rel=1e-3)
    # Regla de doble n (Sec. 4.1): la velocidad de erosion sale de n_min, no
    # de Q/A -- esa ultima es justamente `V_sedimentacion`, la del piso de V2.
    assert hidraulica.V_erosion > hidraulica.Q / (hidraulica.y_normal * resultado.D)
    assert hidraulica.V_sedimentacion < hidraulica.V_erosion
    assert hidraulica.HW in (hidraulica.HW_entrada, hidraulica.HW_salida)


# ===========================================================================
# 3 - El descarte por tope de la norma de producto
# ===========================================================================

def test_agotado_el_catalogo_el_material_se_descarta_con_el_mensaje_textual():
    material = catalogo(TipoMaterial.HDPE)

    resultado, motivo = disenar_material(_punto(), material, Q=1.0,
                                         S=CP2_GEOMETRIA_MANNING["S"],
                                         L=L_CONDUCTO, TW=TW_LIBRE,
                                         verificar=_nada_cumple)

    assert resultado is None
    assert MENSAJE_DIAMETRO_SUPERADO in motivo
    assert "1.50" in motivo, "el motivo debe citar el tope del material"


def test_el_bucle_no_pasa_del_tope_de_cada_material():
    """HDPE topa en 1.50 m: el catalogo se agota en 0.90-1.05-1.20-1.35-1.50."""
    registro = _Registro(lambda D: False)
    material = catalogo(TipoMaterial.HDPE)

    disenar_material(_punto(), material, Q=1.0, S=CP2_GEOMETRIA_MANNING["S"],
                     L=L_CONDUCTO, TW=TW_LIBRE, verificar=registro)

    assert [D for _, D in registro.llamadas] == pytest.approx(
        [0.90, 1.05, 1.20, 1.35, 1.50], rel=REL_TRANSPORTE)


def test_el_mensaje_de_descarte_es_el_del_anexo_B():
    """Textual: la hoja de ruta lo fija asi y M2 lo documenta igual."""
    assert MENSAJE_DIAMETRO_SUPERADO == "material descartado por diámetro requerido"


# ===========================================================================
# 4 - Ningun material cumple
# ===========================================================================

def test_sin_material_que_cumpla_lanza_no_factible_con_los_tres_motivos():
    with pytest.raises(DisenoNoFactibleError) as excinfo:
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                      verificar=_nada_cumple)

    mensaje = str(excinfo.value)
    assert excinfo.value.id_punto == "A-01"
    assert mensaje.count(MENSAJE_DIAMETRO_SUPERADO) == len(TipoMaterial)
    for material in TipoMaterial:
        assert catalogo(material).nombre in mensaje
    # El delta de rasante es del tamizado 7.A, no de este bucle.
    assert excinfo.value.delta_rasante_m is None


def test_un_caudal_que_ningun_diametro_transporta_lo_dice_como_flujo_libre():
    """
    Q = 50 m3/s supera la capacidad del mayor conducto del catalogo: M3
    devuelve None en todos los escalones y el motivo tiene que decir eso, no
    "incumple una verificacion" -- son dos diagnosticos distintos.
    """
    with pytest.raises(DisenoNoFactibleError) as excinfo:
        disenar_punto(_punto(Q_m3s=50.0), L=L_CONDUCTO, TW=TW_LIBRE,
                      verificar=_todo_cumple)

    assert "flujo libre" in str(excinfo.value)


def test_el_motivo_cita_la_verificacion_incumplida():
    with pytest.raises(DisenoNoFactibleError) as excinfo:
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                      verificar=_nada_cumple)

    assert "V1" in str(excinfo.value)
    assert "4.1.1.3.7 b)" in str(excinfo.value)


def test_familia_C_no_es_no_factible_sino_otra_forma_de_estructura():
    """
    M2 no ofrece candidatos: Sec. 2.3 le asigna marco o multicelda y el
    catalogo es de conductos circulares. El motivo tiene que decirlo.
    """
    with pytest.raises(DisenoNoFactibleError) as excinfo:
        disenar_punto(_punto(familia=Familia.C), L=L_CONDUCTO, TW=TW_LIBRE,
                      verificar=_todo_cumple)

    assert "multicelda" in str(excinfo.value)


# ===========================================================================
# 5 - Lo que MD no hace
# ===========================================================================

def test_no_reinterpreta_las_verificaciones():
    """
    Un verificador que dice `cumple=True` con un y/D absurdo es aceptado: MD
    lee el booleano de M5 y no vuelve a juzgarlo. Si una verificacion esta
    mal, se corrige en M5, no aqui.
    """
    def cumple_pese_a_todo(*, punto, material, D, resultado):
        return (_verificacion(True, obtenido=9.99, admisible=Y_SOBRE_D_MAX),)

    resultado = disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=cumple_pese_a_todo)

    assert resultado.aceptado


def test_cero_verificaciones_no_es_un_diseño_aceptado():
    def sin_verificaciones(*, punto, material, D, resultado):
        return ()

    with pytest.raises(ValueError, match="cero verificaciones"):
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                      verificar=sin_verificaciones)


def test_el_caudal_y_la_pendiente_por_defecto_salen_del_punto():
    """Q_m3s (Sec. 1.2) y S_cauce (Sec. 7.B: la pendiente es la del cauce)."""
    punto = _punto()

    por_defecto = disenar_punto(punto, L=L_CONDUCTO, TW=TW_LIBRE,
                                verificar=_solo_borde_libre)
    explicito = disenar_punto(punto, L=L_CONDUCTO, TW=TW_LIBRE,
                              Q=punto.Q_m3s, S=punto.S_cauce,
                              verificar=_solo_borde_libre)

    assert por_defecto.D == explicito.D
    assert (por_defecto.resultado_hidraulico.y_normal
            == pytest.approx(explicito.resultado_hidraulico.y_normal))


@pytest.mark.parametrize("campo", ["Q_m3s", "S_cauce"])
def test_sin_caudal_o_sin_pendiente_es_dato_faltante(campo):
    """No se sustituyen por un valor plausible: se detiene con el nombre."""
    with pytest.raises(DatoFaltanteError) as excinfo:
        disenar_punto(_punto(**{campo: None}), L=L_CONDUCTO, TW=TW_LIBRE,
                      verificar=_todo_cumple)

    assert excinfo.value.campo == campo


@pytest.mark.skipif(importlib.util.find_spec(MODULO_VERIFICACIONES) is not None,
                    reason="M5 ya existe: el verificador por defecto lo importa")
def test_sin_M5_la_ausencia_sale_como_ImportError_y_no_como_ErrorProyecto():
    """
    Falta un modulo del script, no un dato del expediente: la GUI no debe
    mostrarlo como "no factible" ni como "falta declarar".
    """
    with pytest.raises(ImportError, match="M5_verificaciones"):
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE)


# ===========================================================================
# disenar_lote: expediente completo
# ===========================================================================

def test_el_lote_devuelve_todos_los_puntos_en_orden():
    puntos = [_punto(id="A-01"), _punto(id="A-02"), _punto(id="A-03")]

    resultados = disenar_lote(puntos, L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=_todo_cumple)

    assert [r.punto.id for r in resultados] == ["A-01", "A-02", "A-03"]


def test_el_lote_continua_despues_de_un_punto_fallido():
    """
    El punto A-02 tiene Q=50 m3/s y falla con DisenoNoFactibleError. El lote
    no aborta: A-03 se procesa y sus resultados aparecen en la lista.
    """
    puntos = [
        _punto(id="A-01"),
        _punto(id="A-02", Q_m3s=50.0),   # no factible: ningún diametro alcanza
        _punto(id="A-03"),
    ]

    resultados = disenar_lote(puntos, L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=_todo_cumple)

    assert len(resultados) == 3
    assert resultados[0].aceptado
    assert not resultados[1].aceptado
    assert resultados[2].aceptado


def test_el_punto_fallido_tiene_motivo_explicito_y_campos_en_none():
    """
    El motivo lleva el nombre del error y su mensaje: M11 distingue
    DisenoNoFactibleError de DatoFaltanteError sin releer la excepcion.
    """
    puntos = [_punto(id="A-01", Q_m3s=50.0)]

    resultados = disenar_lote(puntos, L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=_todo_cumple)

    fallido = resultados[0]
    assert not fallido.aceptado
    assert fallido.motivo_rechazo is not None
    assert "DisenoNoFactibleError" in fallido.motivo_rechazo
    assert fallido.material is None
    assert fallido.D is None
    assert fallido.resultado_hidraulico is None
    assert fallido.verificaciones == ()
    assert fallido.coherente


def test_el_lote_captura_dato_faltante_por_punto():
    """
    Un punto sin S_cauce es DatoFaltanteError: el lote lo guarda como fallido
    y sigue procesando los demas.
    """
    puntos = [_punto(id="A-01"), _punto(id="A-02", S_cauce=None)]

    resultados = disenar_lote(puntos, L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=_todo_cumple)

    assert resultados[0].aceptado
    assert not resultados[1].aceptado
    assert "DatoFaltanteError" in resultados[1].motivo_rechazo


# ===========================================================================
# 6 - Un material que revienta no se lleva el punto por delante
# ===========================================================================

def test_un_material_que_revienta_no_impide_que_otro_cierre():
    """
    El primer candidato (concreto) lanza ErrorProyecto a mitad del catalogo.
    Antes esa excepcion suba hasta el llamador y mataba el punto entero: TMC
    y HDPE no llegaban a intentarse. Ahora el material se descarta y el bucle
    sigue, de modo que el punto cierra con el siguiente candidato que cumple.
    """
    verificar = _RevientaMaterial(TipoMaterial.CONCRETO_REFORZADO)

    resultado = disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=verificar)

    assert resultado.aceptado
    assert resultado.material.tipo is TipoMaterial.TMC
    # El concreto se intento y se descarto; no se salto en silencio.
    tipos = [t for t, _ in verificar.llamadas]
    assert TipoMaterial.CONCRETO_REFORZADO in tipos
    assert TipoMaterial.TMC in tipos


def test_el_escalon_que_revienta_queda_en_la_traza():
    """
    Entregable 1: la traza de iteraciones publica lo que se INTENTO, y un
    escalon que termino en excepcion se intento igual. Sin esto, la memoria
    de un punto que no cerro perderia justo el escalon que explica por que.
    """
    verificar = _RevientaMaterial(TipoMaterial.CONCRETO_REFORZADO)
    pasos = []

    disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE, verificar=verificar,
                  registrar=pasos.append)

    concreto = [p for p in pasos if p.material == catalogo(
        TipoMaterial.CONCRETO_REFORZADO).nombre]
    assert concreto, "el escalon que revento tiene que estar en la traza"
    assert not concreto[-1].aceptado
    # El sujeto del motivo es el escalon, no el expediente.
    assert "D = 0.90 m" in concreto[-1].motivo
    assert "no se pudo evaluar" in concreto[-1].motivo
    assert "DatoInvalidoError" in concreto[-1].motivo


def test_si_todos_los_materiales_revientan_sigue_siendo_no_factible():
    """
    Con los tres candidatos cayendo, el punto no tiene diseño y eso se dice
    con DisenoNoFactibleError, como cuando se agota el catalogo. El motivo
    lleva los tres materiales, cada uno con su causa citada entera.
    """
    verificar = _RevientaMaterial(TipoMaterial.CONCRETO_REFORZADO,
                                  TipoMaterial.TMC, TipoMaterial.HDPE)

    with pytest.raises(DisenoNoFactibleError) as excinfo:
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE, verificar=verificar)

    motivo = str(excinfo.value)
    for tipo in (TipoMaterial.CONCRETO_REFORZADO, TipoMaterial.TMC,
                 TipoMaterial.HDPE):
        assert catalogo(tipo).nombre in motivo
    assert "DatoInvalidoError" in motivo
    assert "no evaluable" in motivo


def test_un_criterio_pendiente_bloquea_el_punto_aunque_otro_material_cierre():
    """
    Un criterio vacio NO es un descarte: es un material que no se evaluo.

    El concreto es el candidato mas preferente de M2 y queda bloqueado; el TMC
    cumpliria. Cerrar con TMC seria elegir material por descarte de uno que
    nadie llego a verificar, y la memoria de Sec. 3.4 no podria defender esa
    eleccion. El punto sale BLOQUEADO, con la clave que falta.
    """
    verificar = _RevientaMaterial(TipoMaterial.CONCRETO_REFORZADO,
                                  exc=CriterioPendienteError)

    with pytest.raises(CriterioPendienteError) as excinfo:
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE, verificar=verificar)

    assert excinfo.value.clave == "criterio_de_prueba"
    # El TMC llego a probarse: el bucle no se detuvo en el concreto.
    assert TipoMaterial.TMC in [t for t, _ in verificar.llamadas]


def test_el_caso_mixto_es_bloqueado_y_no_no_factible():
    """
    Caso MIXTO: un material evaluado y RECHAZADO, los otros dos bloqueados por
    criterio vacio. `DisenoNoFactibleError` afirma que ninguna combinacion
    cumple, y esa afirmacion no se sostiene sobre dos materiales que nunca se
    evaluaron. Sale CriterioPendienteError.
    """
    verificar = _RevientaMaterial(TipoMaterial.TMC, TipoMaterial.HDPE,
                                  exc=CriterioPendienteError,
                                  rechazan=(TipoMaterial.CONCRETO_REFORZADO,))

    with pytest.raises(CriterioPendienteError):
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE, verificar=verificar)


def test_evaluados_todos_y_ninguno_cumple_si_es_no_factible():
    """
    La contraparte: sin ningun bloqueo, los tres materiales se evaluaron de
    verdad y el punto es NO FACTIBLE, que es lo que DisenoNoFactibleError
    puede afirmar con fundamento.
    """
    with pytest.raises(DisenoNoFactibleError):
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                      verificar=_nada_cumple)


def test_un_fallo_de_programa_sigue_propagandose():
    """
    La captura es de ErrorProyecto y de nada mas. Un ValueError es un defecto
    del script, no un problema del expediente, y no puede quedar disfrazado
    de "material descartado".
    """
    def revienta_feo(*, punto, material, D, resultado):
        raise ValueError("defecto del programa")

    with pytest.raises(ValueError):
        disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                      verificar=revienta_feo)


def test_el_lote_vacio_devuelve_lista_vacia():
    assert disenar_lote([], L=L_CONDUCTO, TW=TW_LIBRE,
                        verificar=_todo_cumple) == []


def test_lote_con_todos_fallidos_devuelve_todos_como_no_aceptados():
    puntos = [_punto(id=f"A-{i:02d}") for i in range(3)]

    resultados = disenar_lote(puntos, L=L_CONDUCTO, TW=TW_LIBRE,
                              verificar=_nada_cumple)

    assert all(not r.aceptado for r in resultados)
    assert all(r.motivo_rechazo for r in resultados)
    assert all(r.coherente for r in resultados)


# ===========================================================================
# C09 / SIS-F-20 - las dos ramas de ImportError, y el verificador del lote
# ===========================================================================
#
# `_verificador_de_M5` tiene DOS salidas de fallo y su docstring las nombra
# las dos ("un M5 ausente O SIN ESA FUNCION"). La primera la cubre el test de
# mas arriba, que hoy queda SALTADO porque M5 ya existe -- el skip es
# deliberado y su motivo esta escrito en el `reason`; la segunda no la cubria
# nadie, y es la que se puede ejercitar sin borrar el modulo.
#
# Las dos se alcanzan aqui inyectando en `sys.modules` lo que `import_module`
# encontraria en cada caso. No se toca produccion ni se borra nada del
# arbol: `monkeypatch.setitem` repone `sys.modules` al terminar el test.
#
# El skip de arriba NO se retira: prueba la ausencia REAL del modulo -- que
# es lo que veria un repositorio sin la Fase 5 -- y eso no lo demuestra
# ninguna inyeccion. Este bloque cubre las lineas; aquel declara el caso.


def test_un_M5_sin_la_funcion_verificar_sale_como_ImportError(monkeypatch):
    """
    SIS-F-20, segunda rama. El modulo esta y no expone `verificar`: falta una
    pieza del PROGRAMA, no un dato del expediente, y por eso NO puede salir
    como ErrorProyecto -- la GUI lo mostraria como "no factible" o como
    "falta declarar" y mandaria al revisor a corregir un expediente que esta
    bien.

    Falla si alguien cambia el `getattr(...) is None` por un fallback
    silencioso (un verificador vacio, un `lambda *_: ()`): entonces MD
    aceptaria diseños sin Fase 5 y nadie se enteraria.
    """
    doble = types.ModuleType(MODULO_VERIFICACIONES)
    assert not hasattr(doble, FUNCION_VERIFICACIONES)
    monkeypatch.setitem(sys.modules, MODULO_VERIFICACIONES, doble)

    with pytest.raises(ImportError) as exc:
        _verificador_de_M5()

    mensaje = str(exc.value)
    assert not isinstance(exc.value, ErrorProyecto), (
        "un modulo incompleto es fallo de programa, no del expediente")
    assert MODULO_VERIFICACIONES in mensaje
    assert FUNCION_VERIFICACIONES in mensaje
    # El mensaje tiene que decir la FIRMA que MD espera: es lo unico que le
    # dice a quien programe la Fase 5 como se enchufa.
    assert "punto=" in mensaje and "material=" in mensaje and "D=" in mensaje


def test_un_M5_ausente_sale_como_ImportError_con_la_via_de_escape(monkeypatch):
    """
    SIS-F-20, primera rama, cubierta sin borrar el modulo: un `None` en
    `sys.modules` es lo que `import_module` trata como importacion detenida,
    igual que la ausencia real que prueba el test saltado de mas arriba.

    Falla si el mensaje deja de decir COMO seguir trabajando sin M5 (pasar el
    verificador en el argumento `verificar`): ese texto es la unica salida
    que tiene quien clone el proyecto sin la Fase 5, y es la que uso este
    mismo archivo de tests mientras M5 no existia.
    """
    monkeypatch.setitem(sys.modules, MODULO_VERIFICACIONES, None)

    with pytest.raises(ImportError) as exc:
        _verificador_de_M5()

    mensaje = str(exc.value)
    assert MODULO_VERIFICACIONES in mensaje
    assert "no esta en el proyecto" in mensaje
    assert "verificar" in mensaje


def test_el_verificador_por_defecto_es_el_de_M5():
    """
    La cara positiva de las dos anteriores: con M5 en su sitio, el
    verificador que MD resuelve es SU funcion, no un doble ni un fallback.
    """
    import modulos.M5_verificaciones as M5

    assert _verificador_de_M5() is getattr(M5, FUNCION_VERIFICACIONES)


def test_el_lote_sin_verificador_explicito_resuelve_la_Fase_5_por_su_cuenta():
    """
    SIS-F-20, segunda deuda de la ficha: `disenar_lote` resuelve el
    verificador igual que `disenar_punto`, y ese camino no lo recorria
    ninguna corrida porque todos los tests le pasaban el verificador.

    Se comprueba por el resultado y no por la identidad de la funcion: el
    punto se detiene en 'remanso_derecho_via', que es el vacio declarado de
    V5 -- una verificacion que solo existe en M5. Si el lote dejara de usar
    la Fase 5 real, este punto cerraria (o fallaria por otra causa) y el
    assert lo diria.
    """
    punto = _punto()

    resultados = disenar_lote([punto], L=L_CONDUCTO, TW=TW_LIBRE)

    assert len(resultados) == 1
    assert not resultados[0].aceptado
    assert "CriterioPendienteError" in resultados[0].motivo_rechazo
    assert "remanso_derecho_via" in resultados[0].motivo_rechazo


# ===========================================================================
# C09 / SIS-A-09 - el diagnostico de Familia C y el camino que no lo alcanza
# ===========================================================================
#
# La ficha dice que el diagnostico de Familia C que MD escribio es
# INALCANZABLE desde el CSV: `disenar_punto` exige Q y S antes de pedir
# candidatos, y una fila C del expediente los trae vacios (Tablero 3.1
# declara la Familia C entera como dato externo pendiente), de modo que el
# punto muere antes en DatoFaltanteError('Q_m3s').
#
# CIERRE ADOPTADO: la opcion (a). Se cubre la rama llamando a la funcion y se
# DECLARA que el camino desde el CSV no la alcanza, con el test que lo
# demuestra. NO se toca produccion: reordenar `disenar_punto` para pedir
# candidatos antes que Q cambiaria que excepcion sale de un punto del
# expediente -- y la que sale hoy es CIERTA (el dato de la ANA falta de
# verdad), solo menos fundamental. Ese reordenamiento es un cambio de diseño
# de la taxonomia de excepciones y no cabe en una tarea de tests.


def test_la_fila_C_del_CSV_muere_antes_de_llegar_al_diagnostico_de_familia_C():
    """
    SIS-A-09, el hecho. La fila C-01 del CSV de ejemplo trae Q_m3s, area_ha y
    S_cauce vacios, y `disenar_punto` los exige antes de pedir candidatos a
    M2: lo que sale es DatoFaltanteError('Q_m3s'), no el "es de otra forma de
    estructura".

    Este test NO pide que eso cambie -- el mensaje que sale es cierto -- : lo
    fija, para que quien lea el docstring de MD ("DisenoNoFactibleError ... o
    M2 no ofrece candidatos (Familia C)") sepa que ese camino no se recorre
    desde el expediente, y para que el dia que alguien reordene las dos
    exigencias se entere aqui y no en una obra.
    """
    csv = Path(__file__).resolve().parent / "ejemplo_puntos.csv"
    c01 = [p for p in cargar_puntos(csv) if p.familia is Familia.C][0]
    assert c01.Q_m3s is None, "la fila C dejo de venir sin caudal"

    with pytest.raises(DatoFaltanteError) as exc:
        disenar_punto(c01, L=L_CONDUCTO, TW=TW_LIBRE, verificar=_todo_cumple)

    assert exc.value.campo == "Q_m3s"
    assert exc.value.id_punto == c01.id


def test_el_diagnostico_de_familia_C_dice_que_es_otra_forma_de_estructura():
    """
    SIS-A-09, la rama. `_motivo_sin_candidatos` se llama directamente porque
    el camino desde el CSV no la alcanza (ver el test anterior); con Q y S
    puestos a mano si se alcanza, y es lo que hace
    `test_familia_C_no_es_no_factible_sino_otra_forma_de_estructura`.

    Lo que este test fija es el CONTENIDO del diagnostico, que es lo que la
    ficha llama "mas fundamental": el punto no es no-factible, es de otra
    forma de estructura. Falla si alguien lo reescribe como "no factible" --
    que mandaria al proyectista a subir la rasante para un cruce que ninguna
    rasante arregla, porque lo que hace falta es un marco.
    """
    csv = Path(__file__).resolve().parent / "ejemplo_puntos.csv"
    c01 = [p for p in cargar_puntos(csv) if p.familia is Familia.C][0]

    motivo = _motivo_sin_candidatos(c01)

    assert Familia.C.value in motivo
    assert "marco o multicelda" in motivo
    assert "no es no-factible" in motivo
    # Y dice por que el catalogo no sirve, que es la causa: es de circulares.
    assert "circulares" in motivo


def test_el_diagnostico_de_una_familia_con_candidatos_no_lleva_la_coletilla_de_C():
    """
    El contraste: la frase de marco o multicelda es de la Familia C y solo de
    ella. Falla si alguien la saca del `if` y se la cuelga a cualquier punto
    sin candidatos, que es la forma en que un diagnostico cierto se convierte
    en uno falso para el resto del expediente.
    """
    motivo = _motivo_sin_candidatos(_punto(familia=Familia.A))

    assert Familia.A.value in motivo
    assert "multicelda" not in motivo
