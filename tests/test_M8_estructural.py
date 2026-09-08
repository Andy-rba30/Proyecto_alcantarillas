"""
tests/test_M8_estructural.py
=============================
Fase 8 (M8_estructural.py):

    seleccionar_clase_calibre()      CriterioPendienteError:
                                      'clases_producto_por_relleno' vacio.
    empuje_flotacion_kn_m()          U = gamma_agua * (pi/4) * D^2, siempre
                                      calculable: la hipotesis es sumersion
                                      completa y por eso NO usa el valor del
                                      NF del punto.
    peso_relleno_kn_m()              CriterioPendienteError:
                                      'peso_especifico_relleno_kn_m3' vacio;
                                      calculo directo con el criterio declarado.
    factores_carga_flotacion()       las dos tablas del num. 2.4.5.3.1 son
                                      [N] y 'factores_carga_aashto' es [A]
                                      (la fila de gamma_p por estructura):
                                      calcula directo sobre la fila
                                      'Resistencia I'. DatoInvalidoError si
                                      la eleccion no cubre el material,
                                      nombra una fila que no esta en la
                                      tabla, o nombra una cuyo extremo la
                                      fuente marca N/A. V7 dejo de ser un FS
                                      global: es el equilibrio de factores de
                                      carga LRFD.
    cama_apoyo_relleno_lateral()     tabla 8.1, [N] literal, sin vacio.
    verificacion_diferida_estructural()  tupla de avisos, nunca calcula.
"""

import math
from dataclasses import fields
from pathlib import Path

import pytest

import criterios_adoptados as ca
from modelos import SeccionCircular, SeccionRectangular
from tests.apoyo.criterios import declarados, sin_valor
from constantes_fisicas import GAMMA_AGUA_KN_M3
import modulos.M8_estructural as M8
from modelos import (CamaApoyoRelleno, CriterioPendienteError,
                     DatoInvalidoError, PuntoCritico, TipoMaterial)
from modulos.M2_material import catalogo
from modulos.M8_estructural import (cama_apoyo_relleno_lateral,
                                    empuje_flotacion_kn_m,
                                    factores_carga_flotacion,
                                    peso_relleno_kn_m,
                                    seleccionar_clase_calibre,
                                    verificacion_diferida_estructural)
from tests.apoyo import estructura
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures.casos_patron import CP10_FLOTACION_MARCO


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


@pytest.fixture
def hdpe():
    return catalogo(TipoMaterial.HDPE)


# ===========================================================================
# Items 1-2 - Seleccion de clase/calibre
# ===========================================================================

def test_seleccionar_clase_calibre_lanza_pendiente(concreto):
    with pytest.raises(CriterioPendienteError) as excinfo:
        seleccionar_clase_calibre(material=concreto, altura_relleno=1.0)
    assert excinfo.value.clave == "clases_producto_por_relleno"


def test_clases_producto_por_relleno_esta_declarado_vacio():
    assert "clases_producto_por_relleno" in ca.criterios_sin_valor()


# ===========================================================================
# Item 3 - Piezas de V7
# ===========================================================================

def test_empuje_flotacion_no_depende_del_NF_medido_del_punto():
    """
    U no depende del NF: la hipotesis es sumersion completa. SI depende del
    espesor de pared, porque se calcula sobre el volumen DESPLAZADO -- el
    diametro exterior, num. 2.4.3.8.2 (MAT-D3).
    """
    U = empuje_flotacion_kn_m(seccion=SeccionCircular(D=0.90), espesor=0.10)
    assert U == pytest.approx(GAMMA_AGUA_KN_M3 * (math.pi / 4) * 1.10 ** 2)


def test_empuje_flotacion_crece_con_el_diametro():
    assert (empuje_flotacion_kn_m(seccion=SeccionCircular(D=1.00), espesor=0.10)
            > empuje_flotacion_kn_m(seccion=SeccionCircular(D=0.70), espesor=0.10))


def test_peso_relleno_lanza_pendiente():
    """Sin el peso del relleno declarado, V7 se detiene y no supone ninguno."""
    with sin_valor("peso_especifico_relleno_kn_m3"):
        with pytest.raises(CriterioPendienteError) as excinfo:
            peso_relleno_kn_m(seccion=SeccionCircular(D=0.70), espesor=0.10,
                              altura_relleno=1.0)
        assert excinfo.value.clave == "peso_especifico_relleno_kn_m3"


def test_peso_relleno_calcula_con_el_criterio_declarado(monkeypatch):
    original = ca.CRITERIOS["peso_especifico_relleno_kn_m3"]
    monkeypatch.setitem(
        ca.CRITERIOS, "peso_especifico_relleno_kn_m3",
        original.__class__(**{**original.__dict__, "valor": 18.0}),
    )
    W = peso_relleno_kn_m(seccion=SeccionCircular(D=0.90), espesor=0.10,
                      altura_relleno=1.05)
    assert W == pytest.approx(18.0 * 1.10 * 1.05)


def _declarar(monkeypatch, clave, valor):
    original = ca.CRITERIOS[clave]
    monkeypatch.setitem(ca.CRITERIOS, clave,
                        original.__class__(**{**original.__dict__, "valor": valor}))


# La ELECCION de fila por estructura, que es lo que hoy declara el criterio.
# Esta declara para el concreto la fila del CABEZAL -- muro de retencion,
# minimo 1.00 -- para poder distinguir en un test que el gamma_EV sale de la
# fila elegida y no de un par fijo. No es la eleccion del proyecto: la del
# proyecto pone al conducto de concreto en "Estructura rigida enterrada".
ELECCION_DEMO = {"concreto_reforzado": {"EV": "EV_muros_y_estribos_de_retencion"}}


def test_el_traslado_de_la_geometria_a_la_seccion_movio_un_ULP_y_esta_declarado():
    """
    EL UNICO NUMERO DE CALCULO QUE C7 MOVIO, fijado aqui para que no vuelva a
    moverse en silencio.

    C7 declaro «ningun numero se movio» y era falso por 1 ULP: la auditoria
    adversarial lo encontro comparando la linea base byte a byte. Al pasar
    `GAMMA * (pi/4) * D_ext**2` -- que Python asocia `(GAMMA*(pi/4)) *
    D_ext**2` -- a `GAMMA * seccion.area_exterior(t)` = `GAMMA * (pi*d**2/4)`,
    la asociacion cambia y el ultimo bit con ella.

    DE LOS CUATRO D_ext QUE LA LINEA BASE IMPRIME, SOLO UNO CAMBIA, y esa
    dispersion es la firma de una reasociacion y no de un error de formula:
    una formula equivocada movería los cuatro. 3.6e-15 kN/m es fisicamente
    nulo; lo que no es nulo es haberlo dicho.

    NO SE «ARREGLA» reordenando: escribir `area_exterior` como `(pi/4)*d**2`
    da el mismo float que la forma actual, porque la diferencia nace de la
    asociacion a traves del `GAMMA *`. Recuperarla exigiria darle a `Seccion`
    el peso especifico del agua.
    """
    import math
    from constantes_fisicas import GAMMA_AGUA_KN_M3

    for D_ext, se_mueve in ((1.100, False), (1.976, True),
                            (2.276, False), (2.876, False)):
        antes = GAMMA_AGUA_KN_M3 * (math.pi / 4) * D_ext ** 2
        ahora = GAMMA_AGUA_KN_M3 * (math.pi * D_ext ** 2 / 4)
        assert (antes != ahora) is se_mueve, (
            f"D_ext = {D_ext}: el censo de cuales se mueven cambio. Si se "
            "mueve otro, algo mas que la asociacion cambio de sitio")
        # Y en cualquier caso la diferencia es del orden del ultimo bit.
        assert abs(antes - ahora) <= abs(antes) * 1e-15


def test_factores_carga_flotacion_calcula_con_el_criterio_real(concreto):
    """
    Las dos tablas del num. 2.4.5.3.1 son [N] y la eleccion de fila esta
    declarada: V7 ya no se detiene aqui.

    Para el conducto de concreto la fila es "Estructura rigida enterrada"
    (1.30/0.90): DC y EV entran con su MINIMO -- 0.90 los dos, el de DC de la
    fila "DC: Componentes y Auxiliares" -- y WA con su MAXIMO (1.00, de la
    Tabla 2.4.5.3.1-1; no hay margen que tomar en esa carga).

    La fila viaja en el resultado, y ese es el punto de MAT-D8: la tabla
    desglosa EV por TIPO DE ESTRUCTURA -- el HDPE cuelga de "Alcantarillas
    termoplasticas" y el TMC de la subfila flexible "Entre otros" -- y un
    conducto no es un muro. Los tres minimos enterrados valen 0.90, de modo
    que V7 no cambia de numero; lo que cambia es que ya no se puede leer sin
    decir de que fila sale.
    """
    g = factores_carga_flotacion(material=concreto)
    assert (g.gamma_DC, g.gamma_EV, g.gamma_WA) == pytest.approx(
        (0.90, 0.90, 1.00), rel=REL_TRANSPORTE)
    assert g.criterio == "factores_carga_aashto"
    assert "Estructura rígida enterrada" in g.fila_gamma_EV


def test_fs_flotacion_ya_no_existe():
    """
    'FS_flotacion' se retiro al reescribir V7 como equilibrio LRFD. Un FS
    global es lenguaje de tension admisible y Sec. 0.2 adopta AASHTO LRFD de
    extremo a extremo; conservar ademas un FS seria contar dos veces el mismo
    margen. Este test impide que vuelva por la puerta de atras.
    """
    assert "FS_flotacion" not in ca.CRITERIOS
    assert not hasattr(M8, "fs_flotacion")


def test_los_gamma_de_v7_salen_de_la_fila_elegida_y_con_el_extremo_correcto(
        concreto, monkeypatch):
    """
    DC y EV estabilizan la flotacion: entran con su gamma MINIMO. WA (la
    subpresion) desestabiliza: entra con el MAXIMO. Tomar el maximo de EV
    seria el error clasico, y aqui daria del lado inseguro.

    Se declara para el concreto la fila del muro de retencion, cuyo minimo es
    1.00: el gamma_EV cambia con ella, que es la prueba de que sale de la
    fila declarada y no de un par escrito en el codigo.
    """
    _declarar(monkeypatch, "factores_carga_aashto", ELECCION_DEMO)
    g = factores_carga_flotacion(material=concreto)
    assert (g.gamma_DC, g.gamma_EV, g.gamma_WA) == pytest.approx(
        (0.90, 1.00, 1.00), rel=REL_TRANSPORTE)
    assert g.criterio == "factores_carga_aashto"


def test_una_eleccion_que_no_cubre_el_material_es_dato_invalido(hdpe,
                                                                monkeypatch):
    """
    Falta el HDPE en la declaracion: el problema esta en lo que el revisor
    escribio, no en el programa. Antes este hueco no se podia ni expresar --
    el criterio traia un par unico para todas las estructuras -- y esa es
    justamente la forma en que MAT-D8 pasaba inadvertido.
    """
    _declarar(monkeypatch, "factores_carga_aashto", ELECCION_DEMO)
    with pytest.raises(DatoInvalidoError) as excinfo:
        factores_carga_flotacion(material=hdpe)
    assert "hdpe" in str(excinfo.value)


def test_una_fila_que_no_es_de_la_tabla_es_dato_invalido(concreto, monkeypatch):
    """
    La eleccion nombra una fila de la Tabla 2.4.5.3.1-2, y se contrasta
    contra la tabla: ni un nombre inventado ni una fila cuyo extremo la
    fuente marca N/A pasan como gamma. Las dos son dato invalido, no
    KeyError ni None.
    """
    _declarar(monkeypatch, "factores_carga_aashto",
              {"concreto_reforzado": {"EV": "EV_fila_que_no_existe"}})
    with pytest.raises(DatoInvalidoError) as excinfo:
        factores_carga_flotacion(material=concreto)
    assert "EV_fila_que_no_existe" in str(excinfo.value)

    # Y una fila que SI existe pero cuyo minimo la fuente marca N/A:
    # "Estabilidad global" no tiene minimo, y eso no es un cero ni una
    # omision. Es la otra cara de MAT-D15 / NOR-AAS-04, donde el N/A de una
    # fila se leyo como "la fuente no declara minimo" para otra.
    _declarar(monkeypatch, "factores_carga_aashto",
              {"concreto_reforzado": {"EV": "EV_estabilidad_global"}})
    with pytest.raises(DatoInvalidoError) as excinfo:
        factores_carga_flotacion(material=concreto)
    assert "N/A" in str(excinfo.value)


def test_el_NF_ya_no_es_un_criterio_de_este_modulo():
    """
    Era un criterio [N] de proyecto (1.4 m para todo el tramo). Hoy es un dato
    de sitio [S] que se mide en cada cruce, o sea una columna del CSV. Que U
    no lo lea es lo que mantiene V7 calculable en un punto cuyo estudio
    geotecnico todavia no dio el NF: la hipotesis de la fila V7 es sumersion
    completa, y sumergido del todo el conducto desplaza su volumen entero
    este el freatico donde este.
    """
    with pytest.raises(KeyError):
        ca.valor("NF_profundidad_m")
    assert "NF_profundidad_m" in {f.name for f in fields(PuntoCritico)}

    # SIS-C-02. La version anterior comprobaba dos SUBCADENAS del texto
    # fuente: `'ca.valor(CRITERIO_NF)' not in fuente` es ademas sensible al
    # FORMATO -- reindentar la llamada a dos lineas la habria evadido sin
    # cambiar nada del comportamiento. Se pregunta al arbol, que es donde
    # esta la respuesta: ni el nombre esta ligado en el modulo, ni el modulo
    # invoca la clave.
    ruta_m8 = Path(M8.__file__)
    assert "CRITERIO_NF" not in estructura.nombres_asignados(ruta_m8)
    assert "CRITERIO_NF" not in estructura.nombres_usados(ruta_m8)
    assert "NF_profundidad_m" not in estructura.textos_de_llamada_o_indice(
        ruta_m8), (
        "M8 volvio a invocar el NF del punto: la flotacion se evalua con el "
        "conducto lleno de aire, no con el freatico medido")


# ===========================================================================
# Item 4 - Cama de apoyo y relleno lateral (tabla 8.1, [N])
# ===========================================================================

def test_cama_apoyo_relleno_lateral_concreto_reforzado(concreto):
    fila = cama_apoyo_relleno_lateral(concreto)
    assert isinstance(fila, CamaApoyoRelleno)
    assert "1/6" in fila.sujecion_relleno_lateral
    assert "506" in fila.numeral


def test_cama_apoyo_relleno_lateral_hdpe(hdpe):
    fila = cama_apoyo_relleno_lateral(hdpe)
    assert "arena" in fila.cama_apoyo.lower()
    assert "508" in fila.numeral


# ===========================================================================
# Item 5 - Diferido al expediente (nunca calcula)
# ===========================================================================

def test_verificacion_diferida_no_lanza_y_devuelve_los_tres_avisos():
    avisos = verificacion_diferida_estructural()
    assert len(avisos) == 3
    conceptos = " ".join(avisos).lower()
    for palabra in ("rigidez de anillo", "pandeo", "costura"):
        assert palabra in conceptos


# ===========================================================================
# CP10 - la regresion que C5 dejo abierta y C7 cierra
# ===========================================================================

def test_CP10_la_subpresion_de_un_marco_es_la_de_un_PRISMA_y_no_la_de_un_cilindro():
    """
    EL CASO PATRON DE V7 SOBRE UN MARCO, y el unico que hay: hasta C7 no
    existia ninguno en `casos_patron.py` -- el de la circular vivia en el
    docstring de un test --.

    Lo que mata: `empuje_flotacion_kn_m` calculaba `pi/4 * D_ext^2` con un
    escalar. Un marco al que se le pasara su altura exterior salia con la
    subpresion del CILINDRO CIRCUNSCRITO, un 39 % por debajo de la real. Y el
    error no se cancela contra EV, porque EV usa solo el ANCHO exterior y cae
    un 28 %: la carga que desestabiliza baja mas que la que sujeta, de modo
    que V7 SOBREESTIMA la seguridad del marco ~27 %. Direccion insegura.
    """
    cp = CP10_FLOTACION_MARCO
    marco = SeccionRectangular(B=cp["B"], H=cp["H"])

    # La geometria exterior, con los dos nombres del Art. 12.6.6.3 separados.
    assert marco.ancho_exterior(cp["espesor"]) == pytest.approx(
        cp["Bc_esperado"], rel=REL_TRANSPORTE)
    assert marco.canto_exterior(cp["espesor"]) == pytest.approx(
        cp["Bc_prima_esperado"], rel=REL_TRANSPORTE)
    # Y NO son el mismo numero, que es toda la diferencia con la circular.
    assert marco.ancho_exterior(cp["espesor"]) != pytest.approx(
        marco.canto_exterior(cp["espesor"]), rel=REL_TRANSPORTE)

    U = empuje_flotacion_kn_m(seccion=marco, espesor=cp["espesor"])
    assert U == pytest.approx(cp["U_prisma_esperado"], rel=REL_TRANSPORTE)
    # LA MITAD QUE MATA LA REGRESION: el numero del cilindro NO es el que
    # sale. Sin este assert, una vuelta a `pi/4 * D^2` pasaria desapercibida
    # mientras el numero siguiera siendo "un numero razonable".
    assert U != pytest.approx(cp["U_cilindro_equivocado"], rel=REL_TRANSPORTE)
    assert U > cp["U_cilindro_equivocado"]

    with declarados({"peso_especifico_relleno_kn_m3": cp["gamma_relleno"]}):
        EV = peso_relleno_kn_m(seccion=marco, espesor=cp["espesor"],
                               altura_relleno=cp["altura_relleno"])
    assert EV == pytest.approx(cp["EV_esperado"], rel=REL_TRANSPORTE)


def test_CP10_una_circular_del_mismo_canto_da_el_numero_del_cilindro():
    """
    El contrapeso, y es lo que fija que la generalizacion no rompio la
    circular: una `SeccionCircular` cuyo diametro exterior sea el CANTO
    exterior del marco da exactamente el numero que el codigo viejo le daba
    al marco. O sea que el 24.96 kN/m no es un numero inventado para este
    test: es el que producia la version anterior, y aqui se ve de quien era.
    """
    cp = CP10_FLOTACION_MARCO
    D_interior = cp["H"]        # mismo canto interior que el marco
    circular = SeccionCircular(D=D_interior)
    U = empuje_flotacion_kn_m(seccion=circular, espesor=cp["espesor"])
    assert U == pytest.approx(cp["U_cilindro_equivocado"], rel=REL_TRANSPORTE)


def test_CP10_engrosar_la_pared_EMPEORA_la_flotacion():
    """
    EL SIGNO CONTRAINTUITIVO DE `espesor_pared_cajon`, fijado como test y no
    solo escrito en la sensibilidad del criterio. Con `DC = 0` el espesor
    entra solo por la geometria exterior, y por los dos lados: U crece con
    (B+2t)(H+2t) -- dos dimensiones -- y EV solo con (B+2t) -- una --. El
    margen empeora monotonamente.

    Quien declare el criterio va a suponer lo contrario, y por eso esto se
    mide en vez de confiarse a un comentario.
    """
    cp = CP10_FLOTACION_MARCO
    marco = SeccionRectangular(B=cp["B"], H=cp["H"])
    margenes = []
    with declarados({"peso_especifico_relleno_kn_m3": cp["gamma_relleno"]}):
        for t in (0.15, 0.20, 0.25):
            U = empuje_flotacion_kn_m(seccion=marco, espesor=t)
            EV = peso_relleno_kn_m(seccion=marco, espesor=t,
                                   altura_relleno=cp["altura_relleno"])
            # 0.90 es el gamma_EV minimo de las dos filas que un conducto
            # enterrado puede tomar; se escribe aqui y no se lee del criterio
            # porque lo que este test mide es el SIGNO, no el valor.
            margenes.append(0.90 * EV - U)
    assert margenes[0] > margenes[1] > margenes[2], (
        f"engrosar la pared tendria que EMPEORAR el margen de V7 y dio "
        f"{margenes}")
    assert all(m < 0 for m in margenes)
