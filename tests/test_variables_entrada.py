"""
tests/test_variables_entrada.py
===============================
El criterio de salida de la Sec. 4.3 del plan v12, hecho suite:

    ninguna variable de entrada sin modo
    ningun modo=de_tabla sin tabla existente en el registro
    ningun modo=en_rango sin rango con semantica declarada

Los tres se comprueban DOS VECES y a proposito: sobre el censo real -- que es
lo que el expediente publica -- y contra un caso construido para violarlos,
que es lo unico que demuestra que la guardia esta viva. Una guardia que solo
se prueba con datos que la pasan no se ha probado.
"""

import pytest

import criterios_adoptados as ca
import datos_sitio as ds
import variables_entrada as ve
from modelos import (DeCatalogo, DeEnsayo, Derivada, DeTabla, EnRango, Libre,
                     ModoDeResolucion, Poblacion, VariableDeEntrada, modo_de)
from modulos.M0_carga import COLUMNAS
from normativa import esquema as E
from normativa import registro as rn


# ===========================================================================
# El censo cubre las tres poblaciones, enteras
# ===========================================================================

def test_las_tres_poblaciones_estan_censadas_completas():
    """
    Lo que el usuario ve como una sola cosa -- "los datos que hay que llenar"
    -- son tres poblaciones que el repositorio mantiene separadas. El censo no
    las junta: las mira juntas.
    """
    grupos = ve.por_poblacion()

    def claves(poblacion):
        return {v.clave for v in grupos[poblacion]}

    assert claves(Poblacion.COLUMNA_CSV) == set(COLUMNAS)
    assert claves(Poblacion.DATO_SITIO) == set(ds.DATOS_SITIO)
    assert claves(Poblacion.CRITERIO) == set(ca.CRITERIOS)
    assert len(ve.VARIABLES) == (len(COLUMNAS) + len(ds.DATOS_SITIO)
                                 + len(ca.CRITERIOS))


def test_ninguna_variable_de_entrada_se_queda_sin_modo():
    """Criterio de salida, primer punto."""
    for clave, v in ve.VARIABLES.items():
        assert v.resolucion is not None, clave
        assert isinstance(v.modo, ModoDeResolucion), clave
        assert v.modo is modo_de(v.resolucion), clave


def test_el_modo_es_el_tipo_y_no_un_campo_que_pueda_mentir():
    """
    La §4.2 del registro normativo lo resolvio asi para los rangos y aqui se
    hace igual: no hay un `modo: str` que alguien pueda escribir mal, porque
    declarar la resolucion y declarar el modo son el mismo acto.
    """
    assert not hasattr(VariableDeEntrada, "modo_declarado")
    assert modo_de(Libre(que_lo_fija="x")) is ModoDeResolucion.LIBRE
    with pytest.raises(TypeError, match="familia cerrada"):
        modo_de("de_tabla")


def test_toda_variable_declara_concepto_unidad_y_fase():
    for clave, v in ve.VARIABLES.items():
        assert v.concepto.strip(), clave
        assert v.unidad.strip(), clave
        assert v.fase.strip(), clave


# ===========================================================================
# de_tabla: la tabla existe, y la fila y la columna tambien
# ===========================================================================

def test_todo_de_tabla_apunta_a_una_tabla_del_registro():
    """Criterio de salida, segundo punto."""
    registro = rn.construir()
    ids = {t.id for t in registro.tablas}
    hubo = False
    for clave, v in ve.VARIABLES.items():
        if v.modo is not ModoDeResolucion.DE_TABLA:
            continue
        hubo = True
        for tabla_id in v.resolucion.tablas:
            assert tabla_id in ids, f"{clave} -> {tabla_id}"
        r = v.resolucion
        if r.fila_id:
            registro.tabla(r.tablas[0]).fila(r.fila_id)
        if r.columna_id:
            registro.tabla(r.tablas[0]).columna(r.columna_id)
    assert hubo, "el censo no tiene ninguna variable `de_tabla`"


def test_tabla_de_entrega_la_tabla_entera_que_la_ventana_muestra():
    """
    La ventana de un `de_tabla` no muestra la fila elegida: muestra la TABLA,
    con su numeral, su pagina y sus notas, y el usuario elige sobre ella. Por
    eso el API entrega la `TablaNormativa` y no un valor.
    """
    tablas = ve.tabla_de("F_pga")
    assert len(tablas) == 1
    assert isinstance(tablas[0], E.TablaNormativa)
    assert tablas[0].id == "MP.TFPGA"
    assert tablas[0].rotulo_de_completitud()

    with pytest.raises(ValueError, match="no `de_tabla`"):
        ve.tabla_de("Q_m3s")


def test_una_eleccion_sobre_dos_tablas_las_cita_a_las_dos():
    """
    `h_eq_bajo_altura_tabulada` se decide mirando la tabla de estribos Y la de
    muros: AASHTO no ofrece un eje libre 'orientacion' sino dos binomios
    acoplados, y una ventana que mostrara una sola escondería la mitad del
    problema.
    """
    tablas = ve.tabla_de("h_eq_bajo_altura_tabulada")
    assert {t.id for t in tablas} == {"AASHTO_LRFD_9.T3.11.6.4-1",
                                      "AASHTO_LRFD_9.T3.11.6.4-2"}


def test_una_laguna_de_la_fuente_se_declara_como_tal():
    """
    Elegir la fila de 10 ft y elegir que hacer con un muro de 4 ft -- que la
    tabla no tabula -- no son la misma cosa, y la memoria tiene que poder
    decir cual de las dos paso.
    """
    con_laguna = {c for c, v in ve.VARIABLES.items()
                  if isinstance(v.resolucion, DeTabla) and v.resolucion.laguna}
    assert {"h_eq_bajo_altura_tabulada", "h_eq_banda_intermedia_borde",
            "F_pga_lectura_columna_extrema"} <= con_laguna


# ===========================================================================
# en_rango: el rango existe y trae su semantica
# ===========================================================================

def test_todo_en_rango_resuelve_a_un_rango_con_semantica():
    """Criterio de salida, tercer punto. LA SEMANTICA ES EL TIPO."""
    hubo = False
    for clave, v in ve.VARIABLES.items():
        if v.modo is not ModoDeResolucion.EN_RANGO:
            continue
        hubo = True
        rango = ve.rango_de(clave)
        assert isinstance(rango, (E.IntervaloAdmisible, E.TechoUnico,
                                  E.PisoUnico, E.ConjuntoDeMaximos,
                                  E.BandaDeInterpolacion)), clave
        assert rango.rotulo_obligatorio, clave
        assert rango.cita_id in {c.id for c in rn.construir().citas}, clave
    assert hubo, "el censo no tiene ninguna variable `en_rango`"


def test_el_caso_testigo_de_la_seccion_4_2_no_tiene_minimo():
    """
    NOR-HID-04. Los dos numeros de la fila del concreto de la Tabla N 10 son
    AMBOS MAXIMOS. La ventana de `v_max_concreto_eleccion` no puede ofrecer el
    3.0 como piso, y el tipo del rango es lo que se lo impide: un
    `ConjuntoDeMaximos` NO TIENE atributo `minimo`.
    """
    rango = ve.rango_de("v_max_concreto_eleccion")
    assert isinstance(rango, E.ConjuntoDeMaximos)
    assert not hasattr(rango, "minimo")
    assert "ninguno es un piso" in rango.rotulo_obligatorio


# ===========================================================================
# de_catalogo: el modo que la Sec. 4.3 pedia crear
# ===========================================================================

def test_de_catalogo_existe_y_lleva_su_advertencia():
    """
    NOR-PRO-01 y NOR-PRO-02: los topes D_MAX estaban atribuidos a AASHTO M170
    y ASTM A760, que tabulan hasta 3600 mm. El modo existe para que la ventana
    NO los rotule como norma.
    """
    catalogo = [v for v in ve.VARIABLES.values()
                if v.modo is ModoDeResolucion.DE_CATALOGO]
    assert [v.clave for v in catalogo] == ["D_max_catalogo"]
    r = catalogo[0].resolucion
    assert r.catalogo_id in {c.id for c in rn.construir().catalogos}
    assert "NINGUNA norma" in r.advertencia
    assert "3600" in r.advertencia


def test_el_rotulo_de_catalogo_y_el_modo_dicen_lo_mismo():
    """Son la misma afirmacion dicha dos veces; no pueden discrepar."""
    for clave, c in ca.CRITERIOS.items():
        rotulado = bool(c.de_catalogo)
        assert rotulado == isinstance(c.resolucion, DeCatalogo), clave


def test_un_tope_de_catalogo_no_puede_llevar_etiqueta_normativa():
    for c in ca.CRITERIOS.values():
        if isinstance(c.resolucion, DeCatalogo):
            assert c.etiqueta not in ("N", "N->")


# ===========================================================================
# de_ensayo: trazabilidad, nunca sensibilidad
# ===========================================================================

def test_de_ensayo_exige_trazabilidad_y_prohibe_sensibilidad():
    """
    Sec. 4.3: "Trazabilidad, nunca sensibilidad". Un [A] se defiende mostrando
    cuanto cambiaria el resultado con el otro extremo del rango; un dato
    determinado por un procedimiento no tiene rango que elegir.
    """
    for clave, v in ve.VARIABLES.items():
        if v.modo is not ModoDeResolucion.DE_ENSAYO:
            continue
        assert v.resolucion.ensayo.strip(), clave
        assert v.resolucion.trazabilidad_exigida.strip(), clave
        if v.poblacion is Poblacion.CRITERIO:
            assert ca.CRITERIOS[clave].sensibilidad is None, clave


def test_los_datos_de_sitio_se_determinan_no_se_eligen():
    """Ninguno es `libre` ni `de_catalogo`: un [S] no lo decide nadie."""
    for v in ve.por_poblacion()[Poblacion.DATO_SITIO]:
        assert v.modo in (ModoDeResolucion.DE_ENSAYO,
                          ModoDeResolucion.DERIVADA,
                          ModoDeResolucion.DE_TABLA,
                          ModoDeResolucion.EN_RANGO), v.clave


# ===========================================================================
# derivada: de que se deriva, y que no se edite
# ===========================================================================

def test_toda_derivada_dice_de_que_se_deriva_y_resuelve():
    derivadas = {c: v.resolucion for c, v in ve.VARIABLES.items()
                 if isinstance(v.resolucion, Derivada)}
    assert derivadas, "el censo no tiene ninguna variable `derivada`"
    ids_registro = {t.id for t in rn.construir().tablas}
    for clave, r in derivadas.items():
        assert r.de and r.regla, clave
        for origen in r.de:
            assert origen in ve.VARIABLES or origen in ids_registro, \
                f"{clave} -> {origen}"


def test_la_tabla_de_recubrimiento_se_deriva_del_registro_y_no_se_copia():
    """
    El criterio `tabla_recubrimiento_aashto_mm` NO es una transcripcion a mano
    de la Tabla 5.10.1-1: la arma `_tabla_recubrimiento_aashto_mm()` leyendo el
    registro. Que su modo sea `derivada` es lo que impide que alguien la edite
    creyendo que edita un valor de proyecto.
    """
    v = ve.variable("tabla_recubrimiento_aashto_mm")
    assert v.modo is ModoDeResolucion.DERIVADA
    assert v.resolucion.de == ("AASHTO_LRFD_9.T5.10.1-1",)


# ===========================================================================
# La guardia esta viva: los casos construidos para violarla
# ===========================================================================

def _criterio(resolucion, **campos):
    base = dict(valor=1.0, etiqueta="A", concepto="c", justificacion="j",
                fuente="f", resolucion=resolucion)
    base.update(campos)
    return ca.Criterio(**base)


def test_la_guardia_rechaza_un_criterio_sin_resolucion():
    with pytest.raises(ValueError, match="resolucion"):
        ca._verificar_criterio("x", _criterio(None))


def test_la_guardia_rechaza_una_tabla_que_no_esta_en_el_registro():
    """
    Es el criterio de salida convertido en error: una tabla que nadie
    transcribio no se puede mostrar entera, que es lo que el modo promete.
    """
    with pytest.raises(ValueError, match="no esta en el registro"):
        ca._verificar_criterio("x", _criterio(
            DeTabla(tablas=("MC_HHD.T99",), que_elige="la fila")))


def test_la_guardia_rechaza_una_fila_que_la_tabla_no_tiene():
    with pytest.raises(ValueError, match="que la tabla no tiene"):
        ca._verificar_criterio("x", _criterio(
            DeTabla(tablas=("MC_HHD.T09",), que_elige="la fila",
                    fila_id="no_existe")))


def test_la_guardia_rechaza_un_en_rango_sobre_una_celda_que_no_es_rango():
    """
    Una celda con un float suelto NO es un rango: no trae piso, ni techo, ni
    semantica. Un `en_rango` sobre ella dejaria a la ventana inventarse cual
    de los dos es.
    """
    with pytest.raises(ValueError, match="no un rango"):
        ca._verificar_criterio("x", _criterio(
            EnRango(tabla_id="MC_HHD.T09", fila_id="concreto_tubo_recto",
                    columna_id="minimo", que_acota="n")))


def test_la_guardia_rechaza_un_de_ensayo_con_sensibilidad():
    with pytest.raises(ValueError, match="de_ensayo"):
        ca._verificar_criterio("x", _criterio(
            DeEnsayo(ensayo="e", trazabilidad_exigida="t"),
            sensibilidad=(0.0, 1.0)))


def test_la_guardia_rechaza_un_catalogo_sin_advertencia():
    with pytest.raises(ValueError, match="advertencia"):
        ca._verificar_criterio("x", _criterio(
            DeCatalogo(catalogo_id="CAT_TUBERIA_LOCAL", que_elige="q",
                       advertencia=""),
            de_catalogo="rotulo"))


def test_la_guardia_rechaza_el_rotulo_de_catalogo_sin_el_modo():
    with pytest.raises(ValueError, match="no pueden discrepar"):
        ca._verificar_criterio("x", _criterio(Libre(que_lo_fija="alguien"),
                                              de_catalogo="rotulo"))


def test_la_guardia_rechaza_opciones_en_un_criterio():
    """El conjunto cerrado de un criterio vive en `sensibilidad`, no aqui."""
    with pytest.raises(ValueError, match="opciones"):
        ca._verificar_criterio("x", _criterio(
            Libre(que_lo_fija="alguien", opciones=("a", "b")),
            sensibilidad=("a", "b")))


def test_la_guardia_del_censo_detecta_una_variable_sin_censar(monkeypatch):
    monkeypatch.setitem(ca.CRITERIOS, "criterio_sin_censar",
                        _criterio(Libre(que_lo_fija="alguien")))
    with pytest.raises(ValueError, match="criterio_sin_censar"):
        ve._verificar_censo()


# ===========================================================================
# El consumidor se averigua, no se declara
# ===========================================================================

def test_el_consumidor_sale_del_codigo_y_no_de_los_comentarios():
    """
    Varias variables se nombran en docstrings de modulos que NO las invocan:
    un `grep` -- o una lista escrita a mano a partir de un grep -- les
    atribuiria consumidores que no tienen.

    `TW_receptor` ERA EL EJEMPLO DE ESTE TEST Y DEJO DE SERLO EN S20, y el
    cambio es justamente la demostracion de que el censo se lee del codigo:
    salia en cuatro sitios de M4 y M5, todos prosa, y no lo invocaba nadie.
    Al implementarse la Sec. 1.3 gano un consumidor REAL --
    `M3.tw_seccion_1_3`, la ultima puerta del TW -- y el censo lo recogio
    solo, sin que nadie editara una lista. Se conserva aqui, con el
    consumidor que ahora tiene, porque el contraste es la prueba: los otros
    tres siguen en cero.
    """
    assert ve.variable("TW_receptor").consumido_por == ("M3_hidraulica",)
    for clave in ("angulo_aletas", "capacidad_portante_adm", "clase_sitio"):
        assert ve.variable(clave).consumido_por == (), clave
        assert clave in ve.variables_sin_consumidor()
    assert ve.variable("ke_entrada").consumido_por == ("M4_control",)


def test_una_variable_sin_consumidor_declara_a_que_fase_pertenece_el_hueco():
    """
    Es la diferencia entre "se olvido cablearlo" y "su fase esta fuera del
    alcance de esta CLI", que desde fuera no se distinguen.
    """
    for clave in ve.variables_sin_consumidor():
        assert ve.variable(clave).fase.strip(), clave


def test_la_fase_de_una_variable_cableada_sale_de_su_consumidor():
    v = ve.variable("long_max_cuneta")
    assert v.consumido_por == ("M10_espaciamiento",)
    assert v.fase == "Fase 10 - Alcantarillas de alivio"


# ===========================================================================
# Lo que este censo NO promete
# ===========================================================================

def test_las_desviaciones_del_plan_estan_declaradas_y_son_reales():
    """
    Apartarse de un ejemplo de la Sec. 4.3 en silencio seria el error que este
    proyecto persigue. Cada desviacion se declara con su razon, y la guardia
    comprueba que sigue siendo una desviacion: el dia que la variable pase a
    resolverse como el plan dice, la entrada deja de ser verdad.
    """
    assert ve.DESVIACIONES_DEL_PLAN
    for d in ve.DESVIACIONES_DEL_PLAN:
        assert d.variable in ve.VARIABLES
        assert d.por_que.strip()
        assert ve.variable(d.variable).modo.value != d.modo_del_plan.split()[0]
    ve._verificar_desviaciones()


def test_ninguna_desviacion_promete_mas_de_lo_que_la_fuente_sostiene():
    """
    Las cuatro se apartan HACIA EL MODO QUE PROMETE MENOS: ninguna inventa una
    tabla, un rango o una cita. `HW_D_max` es el caso que lo explica --
    conflicto vinculante #1 y NOR-HDS-02: el HDS-5 describe una practica ajena
    y no prescribe HW/D alguno --, y por eso es `libre` y no `en_rango`.
    """
    for d in ve.DESVIACIONES_DEL_PLAN:
        modo = ve.variable(d.variable).modo
        assert modo in (ModoDeResolucion.LIBRE, ModoDeResolucion.DE_ENSAYO), \
            f"{d.variable} se aparta hacia {modo.value}, que promete mas"
    assert ve.variable("HW_D_max").modo is ModoDeResolucion.LIBRE


def test_la_tabla_pendiente_nombra_el_trabajo_en_vez_de_excusarlo():
    """
    Un `libre` con `tabla_pendiente` no dice "no se pudo": dice cual es la
    tabla que, transcrita, convierte la variable en `de_tabla`.
    """
    pendientes = dict(ve.variables_con_tabla_pendiente())
    assert "resguardo_HW_subrasante" in pendientes
    assert "4.5.4" in pendientes["resguardo_HW_subrasante"]
    for clave, tabla in pendientes.items():
        assert tabla.strip(), clave
        assert ve.variable(clave).modo is ModoDeResolucion.LIBRE


# ===========================================================================
# El reporte que M11 va a formatear
# ===========================================================================

def test_el_reporte_imprime_el_modo_de_cada_variable():
    texto = ve.reporte_variables()
    for clave, v in ve.VARIABLES.items():
        assert clave in texto, clave
    for modo in ModoDeResolucion:
        assert f"[{modo.value}]" in texto, modo


def test_el_reporte_no_rotula_como_norma_lo_que_es_catalogo():
    texto = ve.reporte_variables(Poblacion.CRITERIO)
    linea = [l for l in texto.splitlines()
             if "D_max_catalogo" in l or "NO ES NORMA" in l]
    assert any("NO ES NORMA" in l for l in linea)


def test_el_reporte_imprime_la_semantica_del_rango_y_no_dos_numeros():
    texto = ve.reporte_variables(Poblacion.CRITERIO)
    assert "ninguno es un piso" in texto


def test_el_reporte_marca_el_dominio_fisico_como_no_normativo():
    """
    §4.2: el dominio fisico y el rango normativo son cosas distintas y la
    ventana no puede darles la misma cara. Fuera del dominio la celda esta mal
    llenada; fuera del rango normativo se incumple la norma.
    """
    texto = ve.reporte_variables(Poblacion.COLUMNA_CSV)
    assert "dominios.CBR_MAX_FISICO" in texto
    assert "no es normativo" in texto


def test_una_clave_que_no_es_variable_de_entrada_no_se_inventa():
    with pytest.raises(KeyError, match="tres poblaciones"):
        ve.variable("no_existe")
