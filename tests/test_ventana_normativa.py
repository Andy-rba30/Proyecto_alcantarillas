"""
tests/test_ventana_normativa.py
===============================
El CONTENIDO de la ventana emergente de las Sec. 4.2 y 4.3 del plan v12.

Que se prueba aqui y que no
---------------------------
Aqui se prueba TODO lo que la ventana afirma: el titulo con sus unidades, el
numeral con la pagina impresa, que la tabla este entera, que las columnas que
el calculo no usa se vean atenuadas Y con su razon, que la condicion de cada
fila se resuelva contra el estado real del expediente, que las notas al pie
esten integras, que los modificadores traigan SU cita, y que los tres
«rangos» de la Sec. 4.2 no se mezclen nunca.

No se prueba el pintado. `gui/ventana_normativa.py` solo cablea widgets, y
probar widgets con un doble de tkinter es un espejismo --- lo dice el
encabezado de `tests/test_gui_contrato.py` y sigue valiendo. Lo que si se
comprueba de la ventana pintada, alli, es que recorra el ORDEN VISUAL que este
modulo declara como dato.

Los hallazgos que este archivo vigila
-------------------------------------
    NOR-HID-06  el titulo de la Tabla N 10 se citaba sin «(m/s)», y esa unidad
                es lo unico que decide que sus dos numeros sean maximos.
    NOR-HID-04  los dos numeros de la fila del concreto son AMBOS MAXIMOS. Una
                ventana que dijera «entre 3.0 y 6.0» ensenaria a leer 3.0 como
                minimo. Ninguna frase compuesta por esta ventana puede decir
                «entre» sobre un `ConjuntoDeMaximos`.
    NOR-PRO-01  los topes de diametro son de CATALOGO. La cara que los muestra
    NOR-PRO-02  no tiene numeral y lo dice.
    NOR-SUE-01  las filas del Cuadro 4.1 que dependen de los carriles por
                sentido no se pueden elegir: la ventana BLOQUEA.
    NOR-AAS-01  la categoria de acero: la ventana PIDE.
    NOR-AAS-05  el modificador por relacion a/c: la ventana PIDE, y ademas
                pinta la laguna de la banda intermedia.
    SIS-F-01    la GUI tenia 584 sentencias y cero tests. Esta es la mitad del
                contenido, que es la que se puede probar de verdad.
"""

import pytest

import criterios_adoptados as ca
import datos_sitio as ds
import variables_entrada as ve
import ventana_normativa as vn
from modelos import ModoDeResolucion, Poblacion
from normativa import registro as registro_normativo
from normativa.esquema import (ConjuntoDeMaximos, Efecto, NoUsada,
                               PendienteDeCondicion, Usada)

REGISTRO = registro_normativo.construir()


# ===========================================================================
# La carcasa: cuatro caras, seis modos, 83 variables
# ===========================================================================

def test_los_seis_modos_tienen_cara():
    """
    Un modo sin cara es una variable que la GUI no sabe pintar. La escalera de
    la Sec. 4.3 es cerrada y el mapeo tambien tiene que serlo.
    """
    for modo in ModoDeResolucion:
        assert vn.cara_de(modo) in vn.Cara


def test_las_caras_son_cuatro_y_ninguna_sobra():
    """
    Cuatro caras, no seis ni siete: cada una tiene al menos un modo que la
    usa. Una cara sin modo seria un cuerpo que nadie pinta.
    """
    usadas = {vn.cara_de(modo) for modo in ModoDeResolucion}
    assert usadas == set(vn.Cara)


def test_las_83_variables_producen_ventana_con_cuerpo():
    """
    El criterio de salida de la sesion empieza aqui: no hay variable de
    entrada sin ventana. `cuerpo` falla si la cara declarada no trae
    contenido, de modo que este test recorre las cuatro caras enteras.
    """
    for clave in ve.VARIABLES:
        ventana = vn.ventana(clave)
        assert ventana.cuerpo is not None, clave
        assert ventana.cara is vn.cara_de(ve.variable(clave).modo)


def test_una_clave_que_no_es_variable_no_abre_ventana():
    with pytest.raises(KeyError, match="no es una variable de entrada"):
        vn.ventana("no_existe_esta_clave")


def test_solo_los_criterios_se_declaran_desde_la_ventana():
    """
    R4 aplicado a la variable entera. Una columna del CSV vale para UN punto y
    un dato de sitio se determina con un procedimiento: ninguno de los dos se
    elige en una ventana, y la ventana lo dice en vez de ofrecer un campo que
    no lleva a ninguna parte.
    """
    for clave, v in ve.VARIABLES.items():
        ventana = vn.ventana(clave)
        assert ventana.declarable_aqui is (v.poblacion is Poblacion.CRITERIO)
        if not ventana.declarable_aqui:
            assert ventana.por_que_no_declarable.strip(), clave


# ===========================================================================
# La cara TABLA
# ===========================================================================

def test_el_titulo_de_la_tabla_10_lleva_sus_unidades():
    """
    NOR-HID-06. El titulo se cita entero, con «(m/s)». Es lo unico que decide
    que los dos numeros de la fila del concreto sean maximos: sin la unidad,
    el titulo se lee como un rotulo cualquiera.
    """
    contenido = vn.contenido_de_tabla("MC_HHD.T10")
    assert "(m/s)" in contenido.titulo_literal
    assert contenido.titulo_literal == REGISTRO.tabla("MC_HHD.T10").titulo_literal


def test_la_linea_de_cita_trae_numeral_norma_edicion_y_pagina_impresa():
    """El orden que pide el plan, y los cuatro trozos presentes."""
    contenido = vn.contenido_de_tabla("MC_HHD.T10")
    cita = REGISTRO.cita(contenido.cita.id)
    fuente = REGISTRO.fuente(cita.fuente_id)
    linea = contenido.linea_de_cita
    assert linea.startswith(f"num. {cita.numeral}")
    assert fuente.titulo in linea
    assert fuente.edicion in linea
    assert f"pag. impresa {cita.pagina_impresa}" in linea
    assert linea.index(cita.numeral) < linea.index(fuente.titulo)
    assert linea.index(fuente.titulo) < linea.index(cita.pagina_impresa)


def test_el_orden_visual_es_el_que_el_plan_pide():
    """
    El orden esta declarado como DATO y no como una secuencia de llamadas: la
    ventana lo recorre, y cambiarlo obliga a cambiar esto.
    """
    assert vn.ORDEN_VISUAL_TABLA == (
        "titulo_literal", "linea_de_cita", "tabla_completa",
        "condiciones_de_fila", "notas_al_pie", "modificadores",
        "cita_textual")


def test_la_tabla_se_muestra_completa_en_todas_las_tablas_del_registro():
    """
    Ni una fila ni una columna se pierden por el camino. «La tabla COMPLETA»
    del plan es una afirmacion comprobable: los conteos tienen que coincidir
    con los del registro, tabla por tabla.
    """
    for tabla in REGISTRO.tablas:
        contenido = vn.contenido_de_tabla(tabla.id)
        assert len(contenido.columnas) == len(tabla.columnas), tabla.id
        assert len(contenido.filas) == len(tabla.filas), tabla.id
        assert {c.id for c in contenido.columnas} == {c.id for c in tabla.columnas}
        assert {f.id for f in contenido.filas} == {f.id for f in tabla.filas}


def test_las_columnas_que_el_calculo_no_usa_estan_visibles_y_atenuadas():
    """
    Visibles y atenuadas, no ocultas: una tabla podada no es la tabla. Y con
    la RAZON, que es lo que contesta la pregunta que nace al verla apagada.
    """
    contenido = vn.contenido_de_tabla("MC_HHD.T09")
    normal = next(c for c in contenido.columnas if c.id == "normal")
    assert normal.atenuada
    assert normal.motivo.strip()
    assert normal.motivo == REGISTRO.tabla("MC_HHD.T09").columna("normal").uso.por_que_no


def test_toda_columna_y_fila_atenuada_trae_su_razon():
    """La regla, en todo el registro y no solo en el ejemplo."""
    for tabla in REGISTRO.tablas:
        contenido = vn.contenido_de_tabla(tabla.id)
        for elemento in (*contenido.columnas, *contenido.filas):
            if elemento.atenuada:
                assert elemento.motivo.strip(), f"{tabla.id}:{elemento.id}"


def test_las_notas_al_pie_van_integras():
    """
    Integras significa verbatim: la ventana no recorta ni resume una nota al
    pie. La Nota 1 de la tabla de F_pga es la que manda interpolar, y media
    nota al pie es una regla distinta.
    """
    contenido = vn.contenido_de_tabla("MP.TFPGA")
    originales = REGISTRO.tabla("MP.TFPGA").notas_al_pie
    assert len(contenido.notas_al_pie) == len(originales)
    for mostrada, original in zip(contenido.notas_al_pie, originales):
        assert mostrada.marca == original.marca
        assert mostrada.texto == original.texto.texto


def test_el_modificador_trae_su_propia_cita_y_su_orden():
    """
    NOR-AAS-05. El modificador lleva SU PROPIA cita --- que aqui coincide con
    la de la tabla porque el Manual imprime las dos vinetas bajo el mismo
    numeral, y que en cualquier otro modificador puede no coincidir --- y su
    `orden` de aplicacion, que es el campo capaz de invertir que norma
    gobierna. La ventana toma la cita del `cita_id` DEL MODIFICADOR, no de la
    tabla, y eso es lo que se fija aqui.
    """
    contenido = vn.contenido_de_tabla("MP.TRECUB")
    modificador = contenido.modificadores[0]
    original = REGISTRO.tabla("MP.TRECUB").modificadores[0]
    assert modificador.cita == vn._linea_de_cita(original.cita_id)
    assert modificador.orden == original.orden.value
    assert modificador.texto_literal == original.texto.texto
    assert modificador.tramos
    for etiqueta, factor, _disponibilidad in modificador.tramos:
        assert etiqueta.strip() and factor.strip()


def test_el_modificador_pinta_la_laguna_de_la_banda_intermedia():
    """
    NOR-AAS-05, la mitad que la auditoria adversarial reabrio: la banda
    0.40 < a/c < 0.50 no la imprime el Manual, y es ALCANZABLE en este
    expediente. La ventana la muestra como laguna de la fuente.
    """
    contenido = vn.contenido_de_tabla("MP.TRECUB")
    lagunas = contenido.modificadores[0].lagunas
    assert lagunas
    assert any("LA FUENTE NO CUBRE" in laguna for laguna in lagunas)


def test_la_cita_textual_es_el_texto_literal_de_la_cita():
    """El parrafo que sostiene la tabla sale del registro, no se compone."""
    for tabla in REGISTRO.tablas:
        contenido = vn.contenido_de_tabla(tabla.id)
        cita = REGISTRO.cita(tabla.cita_id)
        assert contenido.cita_textual == cita.texto_literal.texto


def test_la_interpretacion_del_proyectista_se_rotula_como_tal():
    """
    NOR-HID-04. «El rango recorre la calidad del revestimiento» NO esta en el
    Manual. La ventana lo imprime separado y diciendo de quien es, con lo que
    juega en contra.
    """
    contenido = vn.contenido_de_tabla("MC_HHD.T10")
    texto = contenido.interpretacion_del_proyectista
    assert texto.startswith("INTERPRETACION DEL PROYECTISTA, no de la fuente:")
    assert "En contra:" in texto


def test_la_errata_declara_quien_gana_y_que_pasa_si_se_sigue_la_otra():
    """
    Las tres cosas que `CLAUDE.md` obliga a decir cuando dos fuentes discrepan,
    dichas en la ventana y no solo en un comentario del registro.
    """
    contenido = vn.contenido_de_tabla("MC_HHD.T09")
    assert contenido.erratas
    errata = contenido.erratas[0]
    assert "GANA" in errata
    assert "Si se sigue la otra:" in errata


def test_la_afirmacion_negativa_dice_lo_que_la_tabla_no_dice():
    contenido = vn.contenido_de_tabla("MC_HHD.T10")
    assert contenido.afirmaciones_negativas
    assert "no lista TMC ni HDPE" in contenido.afirmaciones_negativas[0]


# ===========================================================================
# La Sec. 4.2: tres rangos que no son el mismo
# ===========================================================================

def test_un_conjunto_de_maximos_nunca_produce_la_palabra_entre():
    """
    NOR-HID-04, hecho regla. La frase se compone desde el TIPO, y el tipo dice
    que ninguno de los dos numeros es un piso. Si alguien reescribe
    `frase_del_rango` con un formateo generico de dos numeros, cae aqui.
    """
    contenido = vn.contenido_de_rango("v_max_concreto_eleccion")
    frase = contenido.rango_normativo.frase
    assert contenido.semantica == "ConjuntoDeMaximos"
    assert "entre" not in frase.lower()
    assert "MAXIMOS" in frase
    assert "ninguno es un minimo" in frase


def test_ninguna_frase_de_rango_del_registro_inventa_un_minimo():
    """La misma regla, barriendo TODOS los rangos que el registro declara."""
    for tabla in REGISTRO.tablas:
        for fila in tabla.filas:
            for celda in fila.valores.values():
                if isinstance(celda, ConjuntoDeMaximos):
                    frase = vn.frase_del_rango(celda)
                    assert "entre" not in frase.lower()
                    assert not hasattr(celda, "minimo")


def test_los_tres_rangos_van_separados_y_con_rotulos_distintos():
    """
    Sec. 4.2. El rango normativo, el dominio fisico y el de sensibilidad son
    tres campos, tres clases y tres rotulos. Mezclarlos ensena una lectura
    falsa de la norma, que es el motivo entero de esa seccion del plan.
    """
    contenido = vn.contenido_de_rango("v_max_concreto_eleccion")
    assert contenido.rango_normativo.clase == "normativo"
    assert contenido.rango_de_sensibilidad.clase == "sensibilidad"
    assert contenido.rango_normativo.rotulo != contenido.rango_de_sensibilidad.rotulo
    assert "NO es" in contenido.rango_de_sensibilidad.rotulo or \
        "proyectista" in contenido.rango_de_sensibilidad.rotulo


def test_el_dominio_fisico_se_rotula_como_no_normativo():
    """
    Un dominio pintado como si fuera norma es una cita inventada barata. El
    rotulo sale de `ROTULOS_DE_RANGO`, que es del registro.
    """
    campo = vn.contenido_de_campo("cbr_subrasante")
    assert campo.dominio_fisico is not None
    assert campo.dominio_fisico.clase == "dominio_fisico"
    assert "NO es" in campo.dominio_fisico.rotulo
    assert "CBR_MAX_FISICO" in campo.dominio_fisico.frase


def test_el_rango_normativo_dice_que_pasa_al_salirse():
    contenido = vn.contenido_de_rango("v_max_concreto_eleccion")
    assert "INCUMPLE" in contenido.rango_normativo.que_pasa_fuera


def test_la_frase_de_un_intervalo_si_dice_entre():
    """
    El contraste que hace util al test anterior: cuando la fuente SI escribe un
    piso y un techo, la ventana lo dice con esas palabras.
    """
    from normativa.esquema import (IntervaloAdmisible, PisoUnico,
                                   QuePasaFuera, TechoUnico)
    intervalo = IntervaloAdmisible(
        minimo=1.0, maximo=2.0, unidad="m", cita_id="x",
        que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    assert "entre 1.0 y 2.0 m" in vn.frase_del_rango(intervalo)
    techo = TechoUnico(maximo=2.0, unidad="m", cita_id="x",
                       que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    assert "no debe pasar de 2.0 m" in vn.frase_del_rango(techo)
    piso = PisoUnico(minimo=1.0, unidad="m", cita_id="x",
                     que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    assert "no debe bajar de 1.0 m" in vn.frase_del_rango(piso)


def test_una_frase_de_rango_sobre_algo_que_no_es_rango_falla():
    """No hay respaldo generico: un tipo desconocido no se pinta a ojo."""
    with pytest.raises(TypeError, match="no es un rango normativo"):
        vn.frase_del_rango((3.0, 6.0))


# ===========================================================================
# La cara CATALOGO
# ===========================================================================

def test_el_catalogo_no_tiene_numeral_y_lo_dice():
    """
    NOR-PRO-01 / NOR-PRO-02. Un tope de proveedor bajo una cabecera «numeral ·
    norma · pagina» seria una cita falsa nueva. Por eso el catalogo NO comparte
    cara con la tabla.
    """
    contenido = vn.contenido_de_catalogo("D_max_catalogo")
    assert "NO tiene numeral" in contenido.sin_numeral
    assert contenido.que_norma_NO_lo_sostiene.strip()
    assert contenido.advertencia.strip()
    assert vn.ventana("D_max_catalogo").cara is vn.Cara.CATALOGO


def test_el_catalogo_nombra_las_normas_que_no_lo_sostienen():
    contenido = vn.contenido_de_catalogo("D_max_catalogo")
    assert "3600 mm" in contenido.que_norma_NO_lo_sostiene


# ===========================================================================
# La cara CAMPO
# ===========================================================================

def test_un_de_ensayo_exige_trazabilidad_y_no_ofrece_sensibilidad():
    """
    Un [S] no se defiende con un rango: se defiende con la lectura que el
    revisor puede repetir. La ventana pide lo segundo.
    """
    campo = vn.contenido_de_campo("cbr_subrasante")
    assert campo.trazabilidad_exigida.strip()
    assert campo.rango_de_sensibilidad is None
    assert "TRAZABILIDAD" in campo.que_pide


def test_una_derivada_no_es_editable_y_dice_de_que_sale():
    campo = vn.contenido_de_campo("Z_E030")
    assert campo.editable is False
    assert campo.se_deriva_de
    assert campo.regla_de_derivacion.strip()


def test_una_libre_con_tabla_pendiente_la_nombra():
    """
    La lista de trabajo del censo llega a la ventana: la variable dice cual es
    la tabla que la convertiria en `de_tabla` el dia que se transcriba.
    """
    pendientes = dict(ve.variables_con_tabla_pendiente())
    assert pendientes, "el censo dejo de declarar tablas pendientes"
    clave = sorted(pendientes)[0]
    assert vn.contenido_de_campo(clave).tabla_pendiente == pendientes[clave]


# ===========================================================================
# R4: pedir o bloquear, nunca elegir
# ===========================================================================

def test_una_fila_que_depende_de_un_dato_de_sitio_vacio_bloquea():
    """
    NOR-SUE-01. `carriles_por_sentido` esta declarado SIN valor, y un dato de
    sitio no se declara desde la ventana: es un hecho determinado por un
    procedimiento. La ventana BLOQUEA y dice que lo cerraria.
    """
    assert ds.dato("carriles_por_sentido").valor is None
    contenido = vn.contenido_de_tabla("MS.C41")
    autopista = contenido.fila_por_clave("autopista")
    assert not autopista.elegible
    assert isinstance(autopista.disponibilidad, vn.BloqueaLaEleccion)
    assert autopista.disponibilidad.que_lo_cerraria.strip()


def test_una_fila_que_depende_de_un_criterio_vacio_pide_el_dato():
    """
    NOR-AAS-01. La categoria de acero SI es un criterio, y por tanto se
    declara desde la ventana: la respuesta correcta es PEDIRLO, con su clave y
    su concepto, no bloquear.
    """
    ca.quitar_valor_dinamico("categoria_refuerzo_aashto")
    contenido = vn.contenido_de_tabla("AASHTO_LRFD_9.T5.10.1-1")
    columna = next(c for c in contenido.columnas if c.id == "cat_a_mm")
    assert isinstance(columna.disponibilidad, vn.PideDato)
    assert columna.disponibilidad.clave_que_falta == "categoria_refuerzo_aashto"
    assert columna.disponibilidad.concepto_de_lo_que_falta.strip()


def test_declarado_el_criterio_la_fila_pasa_a_elegible():
    """
    La otra mitad: en cuanto el dato existe, la fila se puede elegir. Sin este
    test, «bloquea siempre» pasaria por «respeta R4».
    """
    ca.quitar_valor_dinamico("categoria_refuerzo_aashto")
    contenido = vn.contenido_de_tabla("AASHTO_LRFD_9.T5.10.1-1")
    columna = next(c for c in contenido.columnas if c.id == "cat_a_mm")
    assert isinstance(columna.disponibilidad, vn.PideDato)

    ca.establecer_valor_dinamico("categoria_refuerzo_aashto", "A")
    contenido = vn.contenido_de_tabla("AASHTO_LRFD_9.T5.10.1-1")
    columna = next(c for c in contenido.columnas if c.id == "cat_a_mm")
    assert isinstance(columna.disponibilidad, vn.Elegible)
    assert "categoria_refuerzo_aashto" in columna.disponibilidad.resuelta_por


def test_la_condicion_que_se_resuelve_con_la_propia_clave_no_es_un_dato_que_falte():
    """
    Sin esta distincion la ventana de `categoria_refuerzo_aashto` seria
    inutilizable: sus tres columnas cuelgan de la condicion que ese MISMO
    criterio resuelve, y quedarian pintadas como «falta declararlo» dentro de
    la ventana que existe para declararlo.
    """
    ca.quitar_valor_dinamico("categoria_refuerzo_aashto")
    ventana = vn.ventana("categoria_refuerzo_aashto")
    for columna in ventana.tabla.columnas:
        if columna.disponibilidad is not None:
            assert isinstance(columna.disponibilidad, vn.Elegible), columna.id
            assert "la clave que esta ventana declara" in \
                columna.disponibilidad.resuelta_por


def test_esa_excepcion_no_alcanza_a_ninguna_otra_clave():
    """
    El contrapeso del test anterior: la regla vale para LA clave que la
    ventana declara y para ninguna otra. Vista desde la ventana de otro
    criterio, la misma columna sigue pidiendo el dato.
    """
    ca.quitar_valor_dinamico("categoria_refuerzo_aashto")
    ventana = vn.ventana("situacion_recubrimiento_aashto")
    columna = next(c for c in ventana.tabla.columnas if c.id == "cat_a_mm")
    assert isinstance(columna.disponibilidad, vn.PideDato)


def test_una_condicion_que_no_bloquea_deja_elegir_con_su_justificacion():
    """
    `ADVIERTE` y `EXCLUYE` llevan `justificacion_de_no_bloquear` obligatoria, y
    la fuente misma dijo que no detienen. Fabricar aqui un bloqueo que la
    fuente no pone seria el error simetrico al de elegir por el usuario.
    """
    condicion = REGISTRO.condicion("COND-SELVA-ALTA")
    assert condicion.efecto_si_indeterminada is not Efecto.BLOQUEA
    disponibilidad = vn.disponibilidad_de(condicion)
    assert isinstance(disponibilidad, vn.Elegible)
    assert condicion.justificacion_de_no_bloquear in disponibilidad.resuelta_por


def test_una_condicion_por_expresion_bloquea_porque_es_de_un_punto():
    """
    Una expresion sobre simbolos del CSV no se resuelve en una ventana que
    declara valores de PROYECTO: se evalua punto por punto. La ventana lo dice
    en vez de evaluarla con datos que no tiene.
    """
    condicion = REGISTRO.condicion("COND-DMIN-CANAL-RIEGO")
    disponibilidad = vn.disponibilidad_de(condicion)
    assert isinstance(disponibilidad, (vn.Elegible, vn.BloqueaLaEleccion))


def test_todas_las_elecciones_pendientes_del_registro_se_resuelven():
    """
    Ninguna `PendienteDeCondicion` del registro deja a la ventana sin
    respuesta: o es elegible, o pide, o bloquea. Un cuarto estado no existe.
    """
    for ubicacion, _condicion_id in REGISTRO.elecciones_pendientes():
        tabla_id = ubicacion.split(":")[0]
        contenido = vn.contenido_de_tabla(tabla_id)
        for elemento in (*contenido.columnas, *contenido.filas):
            disponibilidad = getattr(elemento, "disponibilidad", None)
            if disponibilidad is not None:
                assert isinstance(disponibilidad, (vn.Elegible, vn.PideDato,
                                                   vn.BloqueaLaEleccion))


def test_un_bloqueo_sin_salida_declarada_no_se_puede_construir():
    """
    La misma regla que `NoEvaluable` del registro: un «no se puede» sin salida
    escrita es una excusa. Aqui es un error de construccion.
    """
    with pytest.raises(ValueError, match="que_lo_cerraria"):
        vn.BloqueaLaEleccion(condicion_id="X", texto_de_la_condicion="t",
                             por_que="porque si", que_lo_cerraria="  ")


# ===========================================================================
# El censo de los cinco casos que la regla R4 nombra
# ===========================================================================

def test_los_cinco_casos_de_r4_estan_censados():
    """
    El plan identifica cinco. Estan los cinco, y cada uno dice DONDE vive hoy
    su condicion. Un caso que se olvidara no se notaria de ninguna otra forma.
    """
    hallazgos = {caso.hallazgo for caso in vn.CASOS_R4}
    assert hallazgos == {"NOR-SUE-01", "NOR-AAS-01", "NOR-AAS-05",
                         "NOR-HDS-05", "NOR-AAS-06"}
    for caso in vn.CASOS_R4:
        assert caso.donde_vive_hoy.strip()


def test_los_casos_cubiertos_tienen_su_condicion_en_el_registro():
    """
    «Cubierto» es una afirmacion comprobable: la condicion que el caso nombra
    existe en el registro y la maquinaria de la ventana la resuelve.
    """
    cubiertos = vn.casos_r4_cubiertos()
    assert len(cubiertos) == 3
    for caso in cubiertos:
        condicion = REGISTRO.condicion(caso.condicion_id)
        assert condicion is not None, caso.hallazgo
        assert isinstance(vn.disponibilidad_de(condicion),
                          (vn.Elegible, vn.PideDato, vn.BloqueaLaEleccion))


def test_los_casos_sin_cubrir_dicen_que_los_traeria_a_la_ventana():
    """
    Los dos que faltan NO se disimulan. La ventana no puede mostrarlos sin
    inventarse la condicion --- que es lo que este proyecto viene retirando ---
    y por eso el censo dice, para cada uno, que habria que transcribir.
    """
    sin_cubrir = vn.casos_r4_sin_cubrir()
    assert {c.hallazgo for c in sin_cubrir} == {"NOR-HDS-05", "NOR-AAS-06"}
    for caso in sin_cubrir:
        assert caso.que_lo_traeria_a_la_ventana.strip()
        assert not caso.condicion_id


def test_un_caso_r4_sin_condicion_y_sin_salida_no_se_puede_declarar():
    with pytest.raises(ValueError, match="que lo traeria a la ventana"):
        vn.CasoR4(hallazgo="X", de_que_depende="algo", condicion_id="",
                  donde_vive_hoy="en ninguna parte")


# ===========================================================================
# Celdas
# ===========================================================================

def test_una_celda_sin_valor_se_escribe_con_su_significado():
    """
    `"*"` a secas no le dice nada a quien lee la ventana. El asterisco de la
    fila F de la tabla de F_pga significa «investigacion especifica del sitio».
    """
    from normativa.esquema import CeldaSinValor
    texto = vn.texto_de_celda(CeldaSinValor.EXIGE_ESTUDIO)
    assert texto.startswith("*")
    assert "estudio" in texto


def test_una_celda_que_es_un_rango_se_escribe_con_su_frase():
    """La regla de la Sec. 4.2, aplicada tambien DENTRO de la tabla."""
    contenido = vn.contenido_de_tabla("MC_HHD.T10")
    celda = contenido.fila_por_clave("concreto").celdas["velocidad"]
    assert "MAXIMOS" in celda
    assert "entre" not in celda.lower()


# ===========================================================================
# La ventana LEE: abrirla no cambia nada
# ===========================================================================

def test_abrir_una_ventana_no_registra_uso_de_nada():
    """
    M11 imprime «solo los usados», y el uso lo registran `criterios_adoptados.valor`
    y `datos_sitio.valor`. Si la ventana leyera por ahi, mirar un criterio lo
    metería en la memoria como si el calculo lo hubiera invocado --- y el
    bloque de criterios de la memoria dejaria de significar «lo que este
    calculo uso».
    """
    antes_criterios = set(ca.criterios_usados())
    antes_sitio = set(ds.datos_usados())
    for clave in ve.VARIABLES:
        vn.ventana(clave)
    assert set(ca.criterios_usados()) == antes_criterios
    assert set(ds.datos_usados()) == antes_sitio


def test_abrir_una_ventana_no_declara_ningun_valor():
    """La ventana no elige, y no elegir empieza por no escribir."""
    antes = dict(ca.valores_dinamicos())
    for clave in ve.VARIABLES:
        vn.ventana(clave)
    assert ca.valores_dinamicos() == antes
