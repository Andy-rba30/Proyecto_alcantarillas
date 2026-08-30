"""
tests/test_modelos.py
=====================
Los tipos que fluyen entre modulos. Se verifica lo que otros modulos van a dar
por supuesto: que PuntoCritico reproduce el encabezado de Sec. 1.2, que la
geometria circular es coherente, que Verificacion nunca degenera en un bool
desnudo y que la taxonomia de excepciones esta completa.

Valores de referencia: tests/fixtures/casos_patron.py.
"""

import csv
import dataclasses
import math
from pathlib import Path

import pytest

import constantes_normativas as CN
import criterios_adoptados as ca
from modelos import (CasoDemandaSismica, CondicionAnalisis, ConstantesHDS5,
                     ControlGobernante, CriterioPendienteError,
                     DatoFaltanteError, DatoInvalidoError,
                     DemandaSismicaCabezal, DisenoNoFactibleError,
                     EmpujesTrasdos, ErrorProyecto, Familia,
                     LimiteNumericoError,
                     FuerzaInerciaMuro, Geometria, Material, PasoDiseno,
                     PuntoCritico, ReferenciaNormativa, ResultadoHidraulico,
                     ResultadoPunto, TipoMaterial, Verificacion)
from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING, CP8_CONTROL_SALIDA

DIRECTORIO_TESTS = Path(__file__).resolve().parent
CSV_VALIDO = DIRECTORIO_TESTS / "ejemplo_puntos.csv"
CSV_INVALIDO = DIRECTORIO_TESTS / "ejemplo_puntos_invalido.csv"

# Campos de PuntoCritico que M0 deriva y que no son columnas del CSV (Sec. 1.2):
# la notacion vial de la progresiva y la marca de datos pendientes de terceros.
DERIVADOS = {"progresiva_display", "pendientes_externos"}


def _encabezado(ruta: Path):
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f))


def _punto(**cambios) -> PuntoCritico:
    """Punto de prueba con la fila A-01 del CSV de ejemplo como base."""
    base = dict(
        id="A-01",
        progresiva_km=0.380,
        progresiva_display="0+380",
        familia=Familia.A,
        Q_m3s=CP2_GEOMETRIA_MANNING["Q_con_n_max_esperado"],
        area_ha=850.0,
        S_cauce=0.006,
        cota_terreno=42.10,
        cota_rasante=44.20,
        cota_subrasante=44.05,
        cbr_subrasante=8.5,
        esviaje_grados=15.0,
        ancho_plataforma=9.60,
        cota_fondo_receptor=41.30,
        Q_receptor_m3s=None,       # Tablero 3.1
        cota_TW=None,              # Tablero 3.1
        sucs_fundacion="SM",
        NF_profundidad_m=None,     # lo da el estudio geotecnico, por punto
    )
    base.update(cambios)
    return PuntoCritico(**base)


def _geometria_CP2() -> Geometria:
    c = CP2_GEOMETRIA_MANNING
    return Geometria(
        D=c["D"],
        theta=c["theta_esperado"],
        A=c["A_esperado"],
        P=c["P_esperado"],
        R=c["R_esperado"],
        y=c["y_sobre_D"] * c["D"],
    )


# ---------------------------------------------------------------------------
# PuntoCritico: el contrato con el CSV
# ---------------------------------------------------------------------------

def test_los_campos_reproducen_el_encabezado_de_la_seccion_1_2():
    """
    Mismo nombre y mismo orden: M0 no renombra columnas. El unico campo que no
    es columna del CSV es progresiva_display, que M0 deriva del mismo string
    de entrada que progresiva_km.
    """
    campos = [f.name for f in dataclasses.fields(PuntoCritico)]
    assert [c for c in campos if c not in DERIVADOS] == _encabezado(CSV_VALIDO)


def test_la_progresiva_vial_acompana_a_la_numerica():
    """
    '0+380' y 0.380 salen del mismo dato de entrada y deben viajar juntas: la
    memoria se cita en progresivas, no en kilometros decimales.
    """
    campos = [f.name for f in dataclasses.fields(PuntoCritico)]
    assert campos.index("progresiva_display") == campos.index("progresiva_km") + 1

    punto = _punto()
    assert punto.progresiva_display == "0+380"
    assert punto.progresiva_km == pytest.approx(0.380)
    assert str(punto.progresiva_km) not in punto.progresiva_display


def test_el_csv_invalido_es_el_que_omite_una_columna_obligatoria():
    """Documenta para que sirve el fixture de M0: le falta cota_subrasante."""
    columnas = {f.name for f in dataclasses.fields(PuntoCritico)} - DERIVADOS
    faltantes = columnas - set(_encabezado(CSV_INVALIDO))
    assert faltantes == {"cota_subrasante"}


def test_exigir_lanza_dato_faltante_en_vez_de_asumir_un_valor():
    punto = _punto()
    with pytest.raises(DatoFaltanteError) as exc:
        punto.exigir("cota_TW")
    assert exc.value.campo == "cota_TW"
    assert exc.value.id_punto == punto.id


def test_exigir_devuelve_el_dato_cuando_existe():
    punto = _punto()
    assert punto.exigir("Q_m3s") == pytest.approx(punto.Q_m3s)


def test_exigir_rechaza_un_campo_que_no_es_del_encabezado():
    with pytest.raises(AttributeError):
        _punto().exigir("caudal")


def test_el_punto_critico_es_inmutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        _punto().cota_rasante = 0.0


# ---------------------------------------------------------------------------
# Geometria
# ---------------------------------------------------------------------------

def test_la_geometria_reproduce_CP2():
    c = CP2_GEOMETRIA_MANNING
    g = _geometria_CP2()
    tol = c["tolerancia_geometria"]
    assert g.y_sobre_D == pytest.approx(c["y_sobre_D"], rel=tol)
    # A, P y R vienen redondeados a 5 decimales en el fixture: la coherencia
    # R = A/P solo puede exigirse con tolerancia absoluta, no relativa.
    assert g.R == pytest.approx(g.A / g.P, abs=tol)


def test_el_ancho_superficial_es_consistente_con_el_tirante():
    """
    T = D*sen(theta/2) debe coincidir con la cuerda calculada desde el
    tirante, 2*sqrt(r^2 - (y-r)^2). M4 lo usa en Q^2*T/(g*A^3) = 1.
    """
    g = _geometria_CP2()
    radio = g.D / 2
    cuerda = 2 * math.sqrt(radio**2 - (g.y - radio) ** 2)
    assert g.T == pytest.approx(cuerda, rel=CP2_GEOMETRIA_MANNING["tolerancia_geometria"])


# ---------------------------------------------------------------------------
# Material: la regla de doble n
# ---------------------------------------------------------------------------

def _material_concreto() -> Material:
    n_min, n_max = CN.MANNING["concreto_tubo_recto"]
    return Material(
        tipo=TipoMaterial.CONCRETO_REFORZADO,
        nombre="Concreto reforzado",
        n_min=n_min,
        n_max=n_max,
        D_max=ca.valor("D_max_catalogo")["concreto_reforzado"],
        D_max_de_catalogo=ca.criterio("D_max_catalogo").de_catalogo,
        norma_producto="ASTM C76 / AASHTO M170",
        hds5=ConstantesHDS5.desde_dict(
            CN.HDS5_INLET["circular_concreto_square_edge_headwall"]
        ),
        fila_manning=CN.TABLA_09_FILAS["concreto_tubo_recto"]["fila"],
        v_max_tabla10=CN.V_MAX["concreto"],
        v_max_adoptado=None,
        h_relleno_min_eg2013=CN.H_RELLENO_MIN["concreto"],
        espesor_pared=ca.valor("espesor_pared_conducto")["concreto_reforzado"],
        seccion_eg2013=CN.SECCION_EG2013["concreto_reforzado"],
    )


def test_el_material_expone_las_dos_ramas_de_n():
    m = _material_concreto()
    assert m.n_para_capacidad == pytest.approx(CP2_GEOMETRIA_MANNING["n_max"])
    assert m.n_para_velocidad_maxima == pytest.approx(CP2_GEOMETRIA_MANNING["n_min"])
    assert m.n_para_velocidad_maxima < m.n_para_capacidad
    # El piso de velocidad se calcula con n_max, no con n_min (MAT-D1).
    assert m.n_para_velocidad_minima == pytest.approx(CP2_GEOMETRIA_MANNING["n_max"])


def test_la_velocidad_maxima_del_concreto_esta_tabulada():
    assert _material_concreto().v_max_definida is True


def test_las_constantes_hds5_se_construyen_desde_la_tabla_A1():
    fila = CN.HDS5_INLET["circular_concreto_square_edge_headwall"]
    constantes = ConstantesHDS5.desde_dict(fila)
    assert constantes.K == pytest.approx(fila["K"])
    assert constantes.Ks == pytest.approx(fila["Ks"])   # no se omite


# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------

def _resultado_hidraulico(control: ControlGobernante) -> ResultadoHidraulico:
    c = CP2_GEOMETRIA_MANNING
    return ResultadoHidraulico(
        y_normal=c["y_sobre_D"] * c["D"],
        y_critico=c["y_sobre_D"] * c["D"] / 2,     # valor de forma, no de calculo
        V_erosion=c["V_con_n_min_esperado"],
        V_sedimentacion=c["V_con_n_max_esperado"],
        Q=c["Q_con_n_max_esperado"],
        S=c["S"],
        HW_entrada=CP8_CONTROL_SALIDA["H_esperado_con_K_SI"],
        HW_salida=CP8_CONTROL_SALIDA["H_con_29_incorrecto"],
        control_gobernante=control,
    )


def test_HW_selecciona_el_control_que_gobierna():
    entrada = _resultado_hidraulico(ControlGobernante.ENTRADA)
    salida = _resultado_hidraulico(ControlGobernante.SALIDA)
    assert entrada.HW == pytest.approx(entrada.HW_entrada)
    assert salida.HW == pytest.approx(salida.HW_salida)


def test_la_velocidad_no_es_el_caudal_dividido_entre_el_area():
    """
    Regla de doble n: `V_erosion` sale de n_min y Q de n_max, asi que
    V_erosion*A != Q. Si algun dia coinciden, alguien se ahorro el calculo
    doble de Sec. 4.1.

    `V_sedimentacion` SI cumple V*A = Q, y eso no es la regla ahorrada sino su
    consecuencia: es la velocidad media del mismo n con que se resolvio el
    tirante (ver `modelos.TiranteNormal`).
    """
    c = CP2_GEOMETRIA_MANNING
    r = _resultado_hidraulico(ControlGobernante.ENTRADA)
    assert r.V_erosion * c["A_esperado"] != pytest.approx(
        r.Q, rel=c["tolerancia_hidraulica"])
    assert r.V_sedimentacion * c["A_esperado"] == pytest.approx(
        r.Q, rel=c["tolerancia_hidraulica"])


def test_la_verificacion_no_es_un_bool_desnudo():
    g = _geometria_CP2()
    v = Verificacion(
        cumple=g.y_sobre_D <= CN.Y_SOBRE_D_MAX,
        numeral="4.1.1.3.7 b)",
        valor_obtenido=g.y_sobre_D,
        valor_admisible=CN.Y_SOBRE_D_MAX,
        criterio_aplicado=None,          # umbral [N] puro
        codigo="V1",
    )
    assert not isinstance(v, bool)
    assert v.numeral
    assert v.valor_admisible == pytest.approx(CN.Y_SOBRE_D_MAX)


def test_una_verificacion_incumplida_se_reporta_como_tal():
    g = _geometria_CP2()
    excedido = g.y_sobre_D + CN.Y_SOBRE_D_MAX      # muy por encima del limite
    v = Verificacion(
        cumple=excedido <= CN.Y_SOBRE_D_MAX,
        numeral="4.1.1.3.7 b)",
        valor_obtenido=excedido,
        valor_admisible=CN.Y_SOBRE_D_MAX,
        criterio_aplicado=None,
        codigo="V1",
    )
    assert v.cumple is False


def _resultado_punto(cumple: bool) -> ResultadoPunto:
    v = Verificacion(
        cumple=cumple,
        numeral="4.1.1.3.7 b)",
        valor_obtenido=CN.Y_SOBRE_D_MAX,
        valor_admisible=CN.Y_SOBRE_D_MAX,
        criterio_aplicado=None,
        codigo="V1",
    )
    return ResultadoPunto(
        punto=_punto(),
        aceptado=cumple,
        material=_material_concreto(),
        D=CN.DIAMETRO_MIN,
        resultado_hidraulico=_resultado_hidraulico(ControlGobernante.ENTRADA),
        verificaciones=(v,),
        motivo_rechazo=None if cumple else "V1: y/D por encima del maximo",
    )


def test_el_resultado_del_punto_separa_las_verificaciones_incumplidas():
    aceptado = _resultado_punto(True)
    rechazado = _resultado_punto(False)
    assert aceptado.verificaciones_incumplidas == ()
    assert len(rechazado.verificaciones_incumplidas) == 1
    assert aceptado.coherente and rechazado.coherente


def test_un_rechazo_sin_motivo_es_incoherente():
    incoherente = dataclasses.replace(_resultado_punto(False), motivo_rechazo=None)
    assert not incoherente.coherente


# ---------------------------------------------------------------------------
# Taxonomia de excepciones
# ---------------------------------------------------------------------------

def test_toda_excepcion_del_negocio_desciende_de_error_proyecto():
    for excepcion in (CriterioPendienteError, DisenoNoFactibleError,
                      DatoFaltanteError, DatoInvalidoError,
                      LimiteNumericoError):
        assert issubclass(excepcion, ErrorProyecto)


def test_la_taxonomia_son_cinco_y_limite_numerico_no_es_dato_invalido():
    """
    S16.5 anadio la quinta. Este test fija las DOS mitades de la decision.

    Que descienda de ErrorProyecto: gui/app.py importa `ErrorProyecto` y nada
    mas, de modo que un desborde aritmetico tiene que caer en ese `except` y
    mostrarse como aviso. El diagnostico es aritmetico pero el remedio esta en
    el expediente -- una cota absurda, un caudal absurdo.

    Que NO sea `DatoInvalidoError` ni descienda de el: son preguntas
    distintas. DatoInvalido dice "este dato no puede ser" (fuera del rango de
    dominios.py, del tipo equivocado, contradice a su fila). LimiteNumerico
    dice "cada dato, por separado, es sano; es la combinacion la que no cabe
    en un double". Si algun dia alguien las hace hermanas por herencia, un
    `except DatoInvalidoError` empezaria a tragarse desbordes en silencio.
    """
    assert issubclass(LimiteNumericoError, ErrorProyecto)
    assert not issubclass(LimiteNumericoError, DatoInvalidoError)
    assert not issubclass(DatoInvalidoError, LimiteNumericoError)

    # Firma igual a la de DatoInvalidoError, a proposito: `motivo` separa los
    # casos sin necesidad de un atributo nuevo.
    e = LimiteNumericoError("Q", valor=1e155, id_punto="A-01", motivo="Q^2 no cabe")
    assert (e.campo, e.id_punto) == ("Q", "A-01")
    assert e.valor == 1e155  # float-exacto: el valor solo se transporta al atributo, no se calcula
    assert "A-01" in str(e) and "Q^2 no cabe" in str(e)


def test_diseno_no_factible_lleva_motivo_y_delta_de_rasante():
    """Sec. 7.B: devuelve 'no factible -> subir rasante X', nunca un silencio."""
    delta = 0.35
    e = DisenoNoFactibleError(
        "HW supera la subrasante con el maximo diametro disponible",
        delta_rasante_m=delta,
        id_punto="A-01",
    )
    assert e.delta_rasante_m == pytest.approx(delta)
    assert "A-01" in str(e)
    assert "0.35" in str(e)
    assert e.motivo in str(e)


def test_diseno_no_factible_admite_no_tener_delta_de_rasante():
    e = DisenoNoFactibleError("HDPE descartado por diametro requerido")
    assert e.delta_rasante_m is None
    assert e.motivo in str(e)


def test_resultado_punto_fallido_tiene_campos_en_none_y_motivo_explicito():
    """
    Un punto no factible -- capturado por disenar_lote -- tiene aceptado=False,
    todos los campos de diseño en None y motivo_rechazo explicito. M11 lo lista
    aparte del expediente de puntos resueltos.
    """
    fallido = ResultadoPunto(
        punto=_punto(),
        aceptado=False,
        motivo_rechazo="ningun material candidato cumple la Fase 5",
    )
    assert not fallido.aceptado
    assert fallido.material is None
    assert fallido.D is None
    assert fallido.resultado_hidraulico is None
    assert fallido.verificaciones == ()
    assert fallido.coherente                   # motivo_rechazo no es None
    assert fallido.verificaciones_incumplidas == ()


# ---------------------------------------------------------------------------
# ReferenciaNormativa: la seccion propia y el numeral de la norma, separados
# ---------------------------------------------------------------------------

def test_la_referencia_normativa_separa_la_navegacion_interna_de_la_cita():
    """
    Un verificador externo leyo "Sec. 9.1 (EG-2013 num. 503.01, pag. 905)"
    como si el string entero fuese la cita, y salio a buscar una "Sec. 9.1"
    en el EG-2013. Las dos mitades tienen que poder pedirse por separado.
    """
    r = ReferenciaNormativa(
        seccion_hoja_ruta="Sec. 9.1",
        numeral_norma="EG-2013, Capitulo V, Seccion 503, num. 503.01")

    assert r.seccion_hoja_ruta == "Sec. 9.1"
    assert "Sec. 9.1" not in r.numeral_norma
    assert "503.01" in r.numeral_norma


def test_la_referencia_normativa_sigue_siendo_un_string_para_quien_la_imprime():
    """
    Es subclase de str a proposito: `Verificacion.numeral`, el escapado de
    M11 y las pruebas que hacen `numeral in memoria` no tenian que cambiar.
    """
    r = ReferenciaNormativa(seccion_hoja_ruta="Fase 10",
                            numeral_norma="num. 4.1.2.1 d), pag. 178")

    assert isinstance(r, str)
    assert "4.1.2.1" in r
    assert "hoja de ruta" in str(r)          # la mitad interna, etiquetada
    assert str(r).startswith("num. 4.1.2.1")  # la cita verificable, delante


# ---------------------------------------------------------------------------
# Fase 9: los empujes del trasdos, con VALOR y no solo con orden (SIS-F-07)
# ---------------------------------------------------------------------------
# Tolerancia de las comparaciones de valor de este archivo. Las propiedades de
# modelos.py son aritmetica pura sobre sus propios campos -- ni solver, ni
# iteracion, ni acumulacion --, de modo que el unico ruido posible es el del
# ultimo bit del double (37.4*0.8 no da 29.92 exacto). 1e-12 lo absorbe y
# queda diez ordenes de magnitud por debajo del mutante mas fino que estos
# tests tienen que matar: el menor de todos desvia el resultado un 5.4 %.
TOL_ARITMETICA = 1e-12

# Las cuatro cargas del trasdos y sus brazos. NO salen de ningun caso patron
# -- Sec. 9.2 no tiene uno -- y por eso no se presentan como valores de
# proyecto: son los numeros con que se contrasta la ARITMETICA del tipo, y
# estan elegidos para que ninguna mutacion sobreviva. Los cuatro empujes son
# distintos entre si, los cuatro brazos tambien, ninguno vale 0, 1 ni 2, y
# ninguna suma coincide con ningun producto ni con ningun cociente. Los brazos
# ademas son los de un muro de 2.40 m (H/3, H/2 y 0.6H), para que el objeto
# siga siendo leible como lo que representa.
ALTURA_EMPUJE = 2.4           # m
EMPUJE_ACTIVO = 37.4          # kN/m - carga EH
BRAZO_ACTIVO = 0.8            # m - H/3
EMPUJE_SOBRECARGA = 12.5      # kN/m - carga LS
BRAZO_SOBRECARGA = 1.2        # m - H/2
EMPUJE_HIDROSTATICO = 6.3     # kN/m - carga WA
BRAZO_HIDROSTATICO = 0.45     # m - un tercio de la columna de agua
INCREMENTO_SISMICO = 9.7      # kN/m - carga EQ
BRAZO_INCREMENTO = 1.44       # m - 0.6H
SUBPRESION = 4.2              # kN/m - vertical: no entra en ninguna de las dos

EMPUJE_TOTAL_ESTATICO = 56.2      # 37.4 + 12.5 + 6.3
EMPUJE_TOTAL_SISMICO = 65.9       # + 9.7
MOMENTO_ESTATICO = 47.755         # 37.4*0.8 + 12.5*1.2 + 6.3*0.45
MOMENTO_SISMICO = 61.723          # + 9.7*1.44


def test_los_cuatro_totales_salen_de_las_ocho_componentes():
    """
    Los cuatro totales de arriba estan calculados A MANO en un comentario, y
    hasta aqui nada comprobaba que siguieran saliendo de las ocho componentes.
    Editar `EMPUJE_ACTIVO` y olvidar `MOMENTO_ESTATICO` dejaba la suite verde
    con un dorado que ya no sale de su formula --- que es exactamente el
    defecto MAT-O20 / SIS-F-03, el que hizo que los dorados de CP-1 estuvieran
    mal toda su vida.

    No van a `casos_patron.py`: no son dorados de una formula normativa sino
    numeros de sondeo de la ARITMETICA DEL TIPO, elegidos para que ninguna
    mutacion sobreviva (Sec. 9.2 no tiene caso patron, y el bloque de arriba
    lo dice). Lo que faltaba no era moverlos, era recalcularlos.
    """
    assert EMPUJE_TOTAL_ESTATICO == pytest.approx(
        EMPUJE_ACTIVO + EMPUJE_SOBRECARGA + EMPUJE_HIDROSTATICO,
        rel=TOL_ARITMETICA)
    assert EMPUJE_TOTAL_SISMICO == pytest.approx(
        EMPUJE_TOTAL_ESTATICO + INCREMENTO_SISMICO, rel=TOL_ARITMETICA)
    assert MOMENTO_ESTATICO == pytest.approx(
        EMPUJE_ACTIVO * BRAZO_ACTIVO
        + EMPUJE_SOBRECARGA * BRAZO_SOBRECARGA
        + EMPUJE_HIDROSTATICO * BRAZO_HIDROSTATICO, rel=TOL_ARITMETICA)
    assert MOMENTO_SISMICO == pytest.approx(
        MOMENTO_ESTATICO + INCREMENTO_SISMICO * BRAZO_INCREMENTO,
        rel=TOL_ARITMETICA)
    # Y los brazos siguen siendo los de un muro de 2.40 m, que es lo que hace
    # el objeto leible como lo que representa.
    assert BRAZO_ACTIVO == pytest.approx(ALTURA_EMPUJE / 3, rel=TOL_ARITMETICA)
    assert BRAZO_SOBRECARGA == pytest.approx(ALTURA_EMPUJE / 2, rel=TOL_ARITMETICA)
    assert BRAZO_INCREMENTO == pytest.approx(0.6 * ALTURA_EMPUJE,
                                             rel=TOL_ARITMETICA)


def _empujes(condicion: CondicionAnalisis) -> EmpujesTrasdos:
    """Los empujes de una condicion, con la carga EQ solo en la sismica."""
    sismico = condicion is CondicionAnalisis.SISMICO
    return EmpujesTrasdos(
        condicion=condicion,
        altura_empuje=ALTURA_EMPUJE,
        gamma_relleno=19.0,
        E_activo=EMPUJE_ACTIVO,
        z_activo=BRAZO_ACTIVO,
        E_sobrecarga=EMPUJE_SOBRECARGA,
        z_sobrecarga=BRAZO_SOBRECARGA,
        E_hidrostatico=EMPUJE_HIDROSTATICO,
        z_hidrostatico=BRAZO_HIDROSTATICO,
        U_subpresion=SUBPRESION,
        K_A=0.333,
        incremento_sismico=INCREMENTO_SISMICO if sismico else None,
        z_incremento=BRAZO_INCREMENTO if sismico else None,
    )


def test_el_empuje_horizontal_total_suma_las_cuatro_cargas_y_solo_esas():
    """
    Sec. 9.2: EH + LS + WA (+ EQ en la condicion sismica), sin factorar.

    Hasta SIS-F-07 los unicos asserts sobre esta propiedad eran dos
    comparaciones de ORDEN (`sismico > estatico`), y con ellas sobrevivian
    cambiar el signo de LS, el de WA, sumar la subpresion y hasta devolver
    solo E_activo: la suite quedaba en 895 passed con la suma rota.
    """
    estatico = _empujes(CondicionAnalisis.ESTATICO)
    sismico = _empujes(CondicionAnalisis.SISMICO)

    assert estatico.empuje_horizontal_total == pytest.approx(
        EMPUJE_TOTAL_ESTATICO, rel=TOL_ARITMETICA)
    assert sismico.empuje_horizontal_total == pytest.approx(
        EMPUJE_TOTAL_SISMICO, rel=TOL_ARITMETICA)
    # La diferencia entre las dos condiciones es EXACTAMENTE la carga EQ
    assert (sismico.empuje_horizontal_total
            - estatico.empuje_horizontal_total) == pytest.approx(
        INCREMENTO_SISMICO, rel=TOL_ARITMETICA)


def test_el_momento_volcante_es_cada_empuje_por_su_propio_brazo():
    """
    Sec. 9.2, respecto del pie de la zapata. Los cuatro brazos son distintos
    entre si a proposito: cruzarlos (E_activo con z_sobrecarga y al reves) da
    57.715 en vez de 47.755, y sin este assert de valor pasaba la suite.
    Tambien sobrevivian `*` -> `/` en EH y en LS.
    """
    estatico = _empujes(CondicionAnalisis.ESTATICO)
    sismico = _empujes(CondicionAnalisis.SISMICO)

    assert estatico.momento_volcante == pytest.approx(
        MOMENTO_ESTATICO, rel=TOL_ARITMETICA)
    assert sismico.momento_volcante == pytest.approx(
        MOMENTO_SISMICO, rel=TOL_ARITMETICA)
    # La diferencia es el incremento sismico por SU brazo, no por otro
    assert (sismico.momento_volcante
            - estatico.momento_volcante) == pytest.approx(
        INCREMENTO_SISMICO * BRAZO_INCREMENTO, rel=TOL_ARITMETICA)


def test_la_condicion_estatica_no_arrastra_la_carga_EQ():
    """`incremento_sismico` y `z_incremento` son None en estatica (Sec. 9.2)."""
    estatico = _empujes(CondicionAnalisis.ESTATICO)
    assert estatico.incremento_sismico is None
    assert estatico.z_incremento is None
    assert estatico.empuje_horizontal_total == pytest.approx(
        EMPUJE_ACTIVO + EMPUJE_SOBRECARGA + EMPUJE_HIDROSTATICO,
        rel=TOL_ARITMETICA)


def test_la_subpresion_no_entra_ni_en_el_empuje_horizontal_ni_en_el_momento():
    """
    La subpresion es VERTICAL: reduce la normal en la base, no empuja ni
    voltea (docstring de `EmpujesTrasdos`). Sumarla a cualquiera de las dos
    propiedades pasaba la suite entera.
    """
    con = _empujes(CondicionAnalisis.SISMICO)
    sin_subpresion = dataclasses.replace(con, U_subpresion=0.0)

    assert con.U_subpresion == pytest.approx(SUBPRESION, rel=TOL_ARITMETICA)
    assert con.empuje_horizontal_total == pytest.approx(
        sin_subpresion.empuje_horizontal_total, rel=TOL_ARITMETICA)
    assert con.momento_volcante == pytest.approx(
        sin_subpresion.momento_volcante, rel=TOL_ARITMETICA)


# ---------------------------------------------------------------------------
# La relacion de llenado del punto dimensionado (M11 la imprime dos veces)
# ---------------------------------------------------------------------------

def test_la_relacion_de_llenado_del_punto_usa_el_diametro_adoptado():
    """
    `ResultadoPunto.y_sobre_D` = y_normal / D. Es el numero que M11 imprime en
    la tabla del punto y en el cuadro resumen, y el mismo que V1 verifica.
    Sin assert de valor, `y_normal * D` pasaba la suite: 0.81 en vez de
    0.5625, o sea un llenado del 81 % donde el conducto va al 56 %.

    El diametro se cambia a 1.20 m a proposito, para que el resultado no pueda
    coincidir con el y/D de la geometria del fixture (0.75): asi el test
    tambien caza a quien devuelva la relacion de la seccion en vez de la del
    punto.
    """
    aceptado = dataclasses.replace(_resultado_punto(True), D=1.20)
    assert aceptado.resultado_hidraulico.y_normal == pytest.approx(
        0.675, rel=TOL_ARITMETICA)
    assert aceptado.y_sobre_D == pytest.approx(0.5625, rel=TOL_ARITMETICA)


def test_la_relacion_de_llenado_es_None_si_falta_cualquiera_de_los_dos():
    """Basta con que falte UNO de los dos: no se inventa el que quede."""
    aceptado = _resultado_punto(True)
    assert dataclasses.replace(aceptado, D=None).y_sobre_D is None
    assert dataclasses.replace(
        aceptado, resultado_hidraulico=None).y_sobre_D is None


# ---------------------------------------------------------------------------
# Coherencia del resultado y traza del bucle
# ---------------------------------------------------------------------------

def _verificacion(codigo: str, cumple: bool) -> Verificacion:
    """Una verificacion cualquiera con el codigo y el veredicto pedidos."""
    return Verificacion(
        cumple=cumple,
        numeral="4.1.1.3.7 b)",
        valor_obtenido=CN.Y_SOBRE_D_MAX,
        valor_admisible=CN.Y_SOBRE_D_MAX,
        criterio_aplicado=None,
        codigo=codigo,
    )


def test_un_aceptado_con_motivo_de_rechazo_es_incoherente():
    """
    `coherente` exige LAS DOS COSAS: ni verificaciones incumplidas ni motivo
    de rechazo. Con `and` -> `or` el objeto contradictorio pasaba por bueno.
    """
    incoherente = dataclasses.replace(
        _resultado_punto(True), motivo_rechazo="V3: velocidad de erosion")
    assert not incoherente.coherente


def test_un_aceptado_con_una_verificacion_incumplida_es_incoherente():
    """La otra mitad de la conjuncion: aceptar con una V en rojo no es coherente."""
    aceptado = _resultado_punto(True)
    incoherente = dataclasses.replace(
        aceptado,
        verificaciones=aceptado.verificaciones + (_verificacion("V3", False),))
    assert not incoherente.coherente


def test_el_paso_del_bucle_separa_las_verificaciones_que_lo_descartaron():
    """
    `PasoDiseno.incumplidas` alimenta la traza de iteraciones (entregable 1 de
    la Fase 11): `cli.py` exporta con ella la lista de codigos de cada
    escalon. Devolver las que CUMPLEN, o devolverlas todas, pasaba la suite
    entera y la memoria publicaba como motivo del descarte justo las
    verificaciones que no lo fueron.
    """
    paso = PasoDiseno(
        material="Concreto reforzado",
        D=CN.DIAMETRO_MIN,
        aceptado=False,
        motivo="V1: y/D por encima del maximo",
        verificaciones=(_verificacion("V1", False),
                        _verificacion("V2", True),
                        _verificacion("V3", False)),
    )
    assert [v.codigo for v in paso.incumplidas] == ["V1", "V3"]
    assert len(paso.verificaciones) == 3        # las filtra, no las consume

    aceptado = dataclasses.replace(
        paso, aceptado=True, motivo="",
        verificaciones=(_verificacion("V1", True),))
    assert aceptado.incumplidas == ()


# ---------------------------------------------------------------------------
# El caso sismico que gobierna: se comparan ANALISIS, no fuerzas
# ---------------------------------------------------------------------------

CASO_PAE = "100% P_AE + 50% P_IR"
CASO_PIR = "50% P_AE + 100% P_IR"


def _demanda_sismica() -> DemandaSismicaCabezal:
    """
    Los dos casos del contraejemplo que el propio docstring de
    `mas_desfavorable` escribe: P_AE = 100 kN/m con brazo 1.20 m y
    P_IR = 80 kN/m con brazo 2.00 m.
    """
    return DemandaSismicaCabezal(
        casos=(
            CasoDemandaSismica(nombre=CASO_PAE, fraccion_P_AE=1.0,
                               fraccion_P_IR=0.5, P_AE_aplicado=100.0,
                               P_IR_aplicado=40.0, total=140.0,
                               piso_estatico_activo=False),
            CasoDemandaSismica(nombre=CASO_PIR, fraccion_P_AE=0.5,
                               fraccion_P_IR=1.0, P_AE_aplicado=50.0,
                               P_IR_aplicado=80.0, total=130.0,
                               piso_estatico_activo=False),
        ),
        P_AE=100.0,
        P_A=60.0,
        inercia=FuerzaInerciaMuro(P_IR=80.0, W_w=210.0, W_s=110.0, k_h=0.25,
                                  numeral="num. 2.8.1.1.14.1"),
        numeral="num. 2.8.1.1.14.1",
    )


def test_gobierna_el_caso_del_efecto_mayor_y_no_el_de_la_fuerza_mayor():
    """
    num. 2.8.1.1.14.1: manda comparar ANALISIS, no resultantes. Con los dos
    casos del docstring el orden se INVIERTE segun que efecto se mida --
    140 > 130 en fuerza, 220 > 200 en momento volcante --, de modo que un
    `max` -> `min`, o un `casos[0]`, no pueden pasar los dos asserts a la vez.
    Hoy no los pasaba ninguno: `mas_desfavorable` no tenia un solo test.
    """
    demanda = _demanda_sismica()
    por_momento = {CASO_PAE: 200.0, CASO_PIR: 220.0}
    por_fuerza = {caso.nombre: caso.total for caso in demanda.casos}

    assert demanda.mas_desfavorable(por_momento).nombre == CASO_PIR
    assert demanda.mas_desfavorable(por_fuerza).nombre == CASO_PAE


def test_faltar_el_efecto_de_un_caso_detiene_la_comparacion():
    """
    Sin el efecto de los DOS casos no hay "el resultado mas conservador": se
    detiene con la taxonomia del proyecto, no con un KeyError ni con el unico
    caso que si vino.
    """
    demanda = _demanda_sismica()
    with pytest.raises(DatoInvalidoError) as exc:
        demanda.mas_desfavorable({CASO_PAE: 200.0})
    assert exc.value.campo == "efectos"
    assert CASO_PIR in str(exc.value)


def test_la_carga_sismica_va_con_su_brazo_o_no_va():
    """
    El estado medio que nadie podia detectar y que es NO CONSERVADOR: con el
    incremento sismico declarado y `z_incremento` en None, la carga EQ contaba
    en `empuje_horizontal_total` y desaparecia de `momento_volcante`, de modo
    que el FS de volteo salia MAS ALTO de lo que corresponde -- la direccion
    en la que un error no avisa.

    Se cierra en el tipo y no en el llamador: `M9.empujes_trasdos` pone hoy
    los dos campos juntos, pero `EmpujesTrasdos` es publica y los dos campos
    son Optional e independientes.

    SALE FUERA DE `ErrorProyecto`, y el test lo fija en los dos sentidos. El
    estado medio no es un dato del expediente que el proyectista pueda
    corregir --- es inalcanzable desde el unico camino de produccion ---, de
    modo que la taxonomia lo presentaria como "el expediente no se puede
    cargar" y mandaria al revisor a buscar en el CSV un defecto que esta en
    el codigo. Es la frontera que `M9_cabezal.py` declara para SIS-E-02 y la
    misma lectura de SIS-E-05.
    """
    base = _empujes(CondicionAnalisis.SISMICO)

    with pytest.raises(ValueError) as exc:
        dataclasses.replace(base, z_incremento=None)
    assert "volteo" in str(exc.value)
    assert not isinstance(exc.value, ErrorProyecto), (
        "un invariante roto del tipo es un fallo de programa: si sale como "
        "ErrorProyecto, la GUI lo muestra como problema del expediente")

    with pytest.raises(ValueError):
        dataclasses.replace(base, incremento_sismico=None)

    # Y los dos estados legitimos siguen construyendose.
    assert dataclasses.replace(base, incremento_sismico=None,
                               z_incremento=None).incremento_sismico is None
    assert base.z_incremento == pytest.approx(BRAZO_INCREMENTO,
                                              rel=TOL_ARITMETICA)


# ---------------------------------------------------------------------------
# El ancho del talon: la guarda de GeometriaCabezal que nadie alcanzaba
# ---------------------------------------------------------------------------
# Los dos nombres que esta seccion necesita se importan AQUI y no en la
# cabecera del archivo, con el mismo criterio con que otras pruebas de la
# suite hacen `from dataclasses import replace` dentro del test: la seccion
# queda autocontenida y se puede mover entera.
from modelos import GeometriaCabezal                             # noqa: E402
from tests.apoyo.aproximacion import REL_TRANSPORTE              # noqa: E402


# SIS-F-10 conto trece `raise` de la taxonomia sin cobertura; medido de nuevo
# sobre el arbol de S16 el recuento es mayor, y este es uno de los que quedaba
# en modelos.py. Es un metodo de un tipo que fluye entre modulos: borrarlo no
# rompia ninguna prueba y el calculo seguia, con un talon de cero.

# Geometria de tanteo, en metros. NO es del expediente: la geometria del
# cabezal la aporta el criterio 'predimensionamiento_cabezal', que sigue
# vacio. Estos numeros solo tienen que ser coherentes entre si.
ANCHO_TALON_DECLARADO = 1.10


def _geometria_cabezal(**cambios) -> GeometriaCabezal:
    base = dict(H=3.00, B=2.40, D_f=1.20, espesor_corona=0.30,
                espesor_base_muro=0.45, espesor_zapata=0.40)
    base.update(cambios)
    return GeometriaCabezal(**base)


def test_el_ancho_del_talon_sin_declarar_detiene_y_no_vale_cero():
    """
    Falla si `exigir_ancho_talon` devuelve 0.0, None o el default de la
    dataclase en vez de detenerse. El num. 2.8.1.1.14.1 define W_s como el
    peso del suelo encima del muro INCLUYENDO EL TALON: un talon de cero
    anula W_s y con el la mitad de P_IR, y lo hace en la direccion NO
    conservadora -- el numero que sale es menor que el real y nada avisa.

    Se detiene con la excepcion del CRITERIO y no con una de dato, y eso
    tambien se prueba: la geometria del cabezal no sale del CSV, sale de
    'predimensionamiento_cabezal', y la GUI tiene que poder ofrecer
    declararla en vez de mostrar un error de programa.
    """
    geometria = _geometria_cabezal()
    assert geometria.ancho_talon is None

    with pytest.raises(CriterioPendienteError) as exc:
        geometria.exigir_ancho_talon()

    assert exc.value.clave == "predimensionamiento_cabezal"
    assert "talon" in exc.value.concepto
    assert "2.8.1.1.14.1" in exc.value.fuente
    assert "W_s" in exc.value.fuente and "P_IR" in exc.value.fuente
    assert exc.value.mensaje_gui == "falta declarar: predimensionamiento_cabezal"


def test_el_ancho_del_talon_declarado_se_devuelve_tal_cual():
    """
    La otra mitad de la guarda, sin la cual la de arriba se satisface
    lanzando siempre: con el talon declarado no hay excepcion y el numero se
    transporta sin que nadie opere sobre el.
    """
    geometria = _geometria_cabezal(ancho_talon=ANCHO_TALON_DECLARADO)
    assert geometria.exigir_ancho_talon() == pytest.approx(
        ANCHO_TALON_DECLARADO, rel=REL_TRANSPORTE)
