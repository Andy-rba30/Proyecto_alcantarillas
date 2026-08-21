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

import pytest

from constantes_normativas import Y_SOBRE_D_MAX
from modelos import (DatoFaltanteError, DisenoNoFactibleError, Familia,
                     PuntoCritico, TipoMaterial, Verificacion)
from modulos.M2_material import catalogo
from modulos.MD import (MENSAJE_DIAMETRO_SUPERADO, MODULO_VERIFICACIONES,
                        disenar_lote, disenar_material, disenar_punto)
from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING

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

    assert [D for _, D in registro.llamadas] == [0.90, 1.05, 1.20, 1.35]
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
    # Regla de doble n (Sec. 4.1): la V del resultado sale de n_min, no de Q/A.
    assert hidraulica.V > hidraulica.Q / (hidraulica.y_normal * resultado.D)
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

    assert [D for _, D in registro.llamadas] == [0.90, 1.05, 1.20, 1.35, 1.50]


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
# Verificaciones diferidas en el bucle (sitios 1 y 2 del paso 7)
# ===========================================================================

def _diferida(codigo):
    return Verificacion(
        cumple=None, numeral=f"Fase 5, {codigo}", valor_obtenido=None,
        valor_admisible=None, criterio_aplicado=None, codigo=codigo,
        nota_diferida="diferida al expediente tecnico")


def _cumple_con_diferidas(*, punto, material, D, resultado):
    """Lo que la Fase 5 real devuelve hoy: todo cumple salvo V5/V8, diferidas."""
    return (_verificacion(True), _diferida("V5"), _diferida("V8"))


def _incumple_con_diferida(*, punto, material, D, resultado):
    return (_verificacion(False, obtenido=1.0, admisible=2.0), _diferida("V5"))


def test_un_diametro_con_v5_y_v8_diferidas_se_acepta():
    """
    Sitio 1 -- LA regresion del encargo. Un diferido no cuenta como
    incumplimiento ni como cumplimiento, y SI permite aceptar el diametro.
    Si lo impidiera, el efecto seria identico al AssertionError que los
    pasos 2-5 retiraron y ningun punto se dimensionaria jamas.
    """
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    resultado, motivo = disenar_material(
        _punto(), material, Q=1.0, S=CP2_GEOMETRIA_MANNING["S"],
        L=12.0, TW=0.0, verificar=_cumple_con_diferidas)

    assert resultado is not None and resultado.aceptado
    assert motivo == ""
    assert [v.cumple for v in resultado.verificaciones] == [True, None, None]
    # y el aceptado es coherente: las diferidas no son incumplimientos
    assert resultado.verificaciones_incumplidas == ()
    assert resultado.coherente


def test_el_motivo_de_rechazo_no_acusa_a_las_diferidas():
    """
    Sitio 2: con una False y una diferida, el motivo nombra solo la False.
    'V5 obtenido None frente a None' pareceria una comparacion real que
    nunca ocurrio.
    """
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    resultado, motivo = disenar_material(
        _punto(), material, Q=1.0, S=CP2_GEOMETRIA_MANNING["S"],
        L=12.0, TW=0.0, verificar=_incumple_con_diferida)

    assert resultado is None
    assert "V1" in motivo
    assert "V5" not in motivo
    assert "None" not in motivo
