"""
tests/test_M12_metrados.py
==========================
VE-5 (lote «met», item 8 del censo): Fase 11 de la v8, entregables 8 y 9.

    8. Metrados referidos a las partidas del EG-2013 (`M12_metrados`).
    9. Cuadro de compatibilidad rasante-alcantarilla (la salida de 7.A).

EL CASO PATRON ESTA CALCULADO A MANO EN EL TEST, no con las funciones del
modulo: cada numero esperado se escribe con la aritmetica de la regla de
medicion de su Seccion (EG-2013 501.09, 503.12, 504.10, 506.14, 506.06,
506.07, 511.13) sobre una geometria de cabezal de numeros redondos. La
geometria es un TANTEO de prueba (los objetos de la Fase 9 armados a mano),
no la de ningun proyecto.

Y una corrida de punta a punta (la de referencia `expediente_cabezal`) fija
que el servicio arma el metrado detras de la Fase 9, que lo que no se puede
medir es un `Bloqueo` con su criterio, y que declarar el criterio libera el
renglon.
"""

import json
import math
from types import SimpleNamespace

import pytest

from src import criterios_adoptados as ca
from src.constantes_normativas import PESO_BARRA_KG_M_EG2013
from src.modelos import (CriterioPendienteError, DatoFaltanteError,
                         ESTADO_RASANTE_COMPATIBLE, ESTADO_RASANTE_SIN_TAMIZADO,
                         ESTADO_RASANTE_SUBIR, FormaSeccion,
                         MetodoNoEvaluableError, MetradoDelPunto,
                         RUBROS_DE_METRADO, SeccionCircular, TipoDeBloqueo,
                         TipoMaterial)
from src.modulos import M12_metrados as M12
from src.modulos.M9_cabezal import TIPO_GRAVEDAD, TIPO_VOLADIZO
from tests.fixtures.casos_patron import CP_M12_METRADOS as CP

TOL = 1e-6
TOL_CP = 1e-5          # las cifras del caso patron van a seis decimales


# ===========================================================================
# El caso patron: la geometria de prueba
# ===========================================================================

D, T = 1.0, 0.10                      # tubo de concreto reforzado, pared
BC = D + 2 * T                        # 1.20 m, diametro exterior
A_EXT = math.pi * BC ** 2 / 4         # 1.130973 m2, el vano
L_MET, S = 12.0, 0.01                 # longitud de metrado, pendiente
SOLERA_E, SOLERA_S = 99.90, 99.78     # fondo del conducto en los extremos
NF = 0.10                             # profundidad del freatico


def _losa():
    return SimpleNamespace(longitud=1.5, espesor=0.30,
                           profundidad_dentellon=0.80, ancho_dentellon=0.40)


def _aleros_45():
    return SimpleNamespace(angulo_grados=45.0, angulo_largo_grados=45.0,
                           longitud_corto=2.0, longitud_largo=2.0,
                           altura_inicial=2.0, altura_final=0.4,
                           espesor=0.30, ancho_zapata=3.0,
                           espesor_zapata=0.40)


def _geometria(extremo, *, desplante, aleros=None, tipo=TIPO_VOLADIZO):
    return SimpleNamespace(
        extremo=extremo, tipo=tipo, H=2.0, B=3.0, D_f=1.0,
        espesor_corona=0.30, espesor_base_muro=0.30, espesor_zapata=0.40,
        ancho_talon=1.5, longitud=1.8, cota_desplante=desplante,
        aleros=aleros, losa=_losa())


def _barra(designacion, s):
    return SimpleNamespace(designacion=designacion, espaciamiento=s,
                           texto=f"Ø {designacion}\" @ {s:.3f} m")


def _armado(extremo):
    fila = SimpleNamespace
    return SimpleNamespace(extremo=extremo, fc_mpa=21.0, fy_mpa=420.0,
                           tabla=(
        fila(elemento="pantalla",
             posicion="pantalla: trasdos (contra el relleno), armadura "
                      "vertical", barra=_barra("1/2", 0.20)),
        fila(elemento="pantalla",
             posicion="pantalla: armadura horizontal, cada cara",
             barra=_barra("3/8", 0.25)),
        fila(elemento="zapata",
             posicion="punta: inferior (contra el terreno), armadura "
                      "transversal", barra=_barra("1/2", 0.25))))


def _cabezal():
    """Entrada: cabezal recto (sin aleros), pie a 100.0 msnm. Salida: con
    dos aleros a 45 grados de 2.0 m, pie a 99.0 msnm. Los dos armados."""
    return SimpleNamespace(
        id_punto="P-1", longitud_metrado=L_MET, motivo_sin_longitud="",
        entrada=_geometria("entrada", desplante=99.0),
        salida=_geometria("salida", desplante=98.0, aleros=_aleros_45()),
        armado=(_armado("entrada"), _armado("salida")))


def _material(tipo=TipoMaterial.CONCRETO_REFORZADO,
              forma=FormaSeccion.CIRCULAR):
    return SimpleNamespace(tipo=tipo, forma=forma)


class _Punto(SimpleNamespace):
    def exigir(self, campo):
        valor = getattr(self, campo)
        if valor is None:
            raise DatoFaltanteError(campo, id_punto=self.id)
        return valor


def _punto(**kw):
    datos = dict(id="P-1", progresiva_display="0+100",
                 familia=SimpleNamespace(value="A"), cota_rasante=102.0,
                 sucs_fundacion="SP-SM", NF_profundidad_m=NF)
    datos.update(kw)
    return _Punto(**datos)


# ===========================================================================
# Conducto (EG-2013 506.14)
# ===========================================================================

def test_conducto_entre_caras_exteriores_siguiendo_la_pendiente():
    (r,) = M12.renglones_conducto(
        material=_material(), seccion=SeccionCircular(D=D), celdas=1,
        espesor=T, cabezal=_cabezal(), S=S)
    # 12.0 · sqrt(1 + 0.01^2) = 12.00059998
    assert r.cantidad == pytest.approx(12.0 * math.sqrt(1.0001), abs=TOL)
    assert r.cantidad == pytest.approx(CP["conducto_m"], abs=TOL_CP)
    assert (r.partida, r.unidad) == ("506.A", "m")
    assert "1000 mm" in r.descripcion
    assert r.paso.formula_cita_id == "EG2013.506.14#LONGITUD"


def test_sin_longitud_de_metrado_el_conducto_no_se_mide():
    c = _cabezal()
    c.longitud_metrado = None
    c.motivo_sin_longitud = "sin coronacion"
    with pytest.raises(DatoFaltanteError, match="longitud_metrado"):
        M12.renglones_conducto(material=_material(),
                               seccion=SeccionCircular(D=D), celdas=1,
                               espesor=T, cabezal=c, S=S)


# ===========================================================================
# Excavacion (EG-2013 501.09, 506.06, 506.07, 501.04, 501.01)
# ===========================================================================

def _excavacion(**kw):
    datos = dict(punto=_punto(), material=_material(),
                 seccion=SeccionCircular(D=D), celdas=1, espesor=T,
                 cabezal=_cabezal(), cota_solera_entrada=SOLERA_E,
                 cota_solera_salida=SOLERA_S)
    datos.update(kw)
    return M12.renglones_excavacion(**datos)


def _por_elemento(renglones):
    return {r.elemento: r for r in renglones}


def test_zanja_del_conducto_a_mano():
    """
    W = Bc + 0.60 = 1.80 m (506.06); fondo = solera - t - 0.15 (506.07).
    x medido desde la cara exterior del muro de entrada sobre L = 12 m:
        terreno(x) = 100.0 - x/12          (pies 100.0 y 99.0)
        fondo(x)   = 99.65 - 0.01·x        (99.90 - 0.25 ; 99.78 - 0.25)
        d(x)       = 0.35 - (1/12 - 0.01)·x
    La zanja corre entre los talones: x_a = 0.3 + 1.5 = 1.8 y x_b = 10.2.
    """
    pendiente = 1 / 12 - 0.01
    d_a = 0.35 - pendiente * 1.8
    d_b = 0.35 - pendiente * 10.2
    L = 10.2 - 1.8
    assert d_a > 0 > d_b
    # la parte positiva es un triangulo
    corte = L * d_a / (d_a - d_b)
    V = 1.80 * d_a * corte / 2
    corte_nf = L * (d_a - NF) / ((d_a - NF) - (d_b - NF))
    V_agua = 1.80 * (d_a - NF) * corte_nf / 2
    r = _por_elemento(_excavacion())
    seco = r["zanja del conducto, en seco"]
    agua = r["zanja del conducto, bajo agua (bajo el nivel freatico)"]
    assert seco.cantidad == pytest.approx(V - V_agua, abs=TOL)
    assert agua.cantidad == pytest.approx(V_agua, abs=TOL)
    assert (seco.partida, agua.partida) == ("501.C", "501.D")
    assert V == pytest.approx(CP["zanja_m3"], abs=TOL_CP)
    assert V_agua == pytest.approx(CP["zanja_agua_m3"], abs=TOL_CP)
    assert seco.unidad == "m3"


def test_cimientos_del_cabezal_recto_a_mano():
    """
    Zapata B·L_c·D_f = 3.0·1.8·1.0 = 5.40 m3; dentellon b·ancho·h =
    0.4·1.8·0.8 = 0.576 m3 (sin aleros la losa tiene el ancho del cabezal).
    Bajo el freatico (NF = 0.10): 3.0·1.8·0.9 + 0.4·1.8·0.7 = 4.86 + 0.504.
    """
    r = _por_elemento(_excavacion())
    total = 5.40 + 0.576
    agua = 4.86 + 0.504
    assert (total, agua) == pytest.approx(
        (CP["cimientos_entrada_m3"], CP["cimientos_entrada_agua_m3"]))
    assert r["cimientos del cabezal de entrada, bajo agua (bajo el nivel "
             "freatico)"].cantidad == pytest.approx(agua, abs=TOL)
    assert r["cimientos del cabezal de entrada, en seco"].cantidad == \
        pytest.approx(total - agua, abs=TOL)


def test_cimientos_del_cabezal_con_aleros_y_sobreancho_declarado():
    """
    Con s = 0.45 m (el tope de 501.04) declarado:
        zapata  (3.0 + 0.9)(1.8 + 0.9)·1.0 = 10.53
        aleros  (3.0 + 0.9)(2.0 + 0.9)·1.0 = 11.31, cada uno
        dentellon 0.4·(1.8 + 2·2·sen45)·0.8 (la losa de 1.5 m pasa el
        alcance de los aleros, 2·cos45 = 1.414 m: se abre lo que el alero)
    """
    ca.establecer_valor_dinamico("sobreancho_excavacion_estructuras_m", 0.45)
    try:
        r = _por_elemento(_excavacion(punto=_punto(NF_profundidad_m=5.0)))
    finally:
        ca.quitar_valor_dinamico("sobreancho_excavacion_estructuras_m")
    ancho_borde = 1.8 + 2 * 2.0 * math.sin(math.radians(45))
    esperado = 10.53 + 2 * 11.31 + 0.4 * ancho_borde * 0.8
    salida = r["cimientos del cabezal de salida, en seco"]
    assert salida.cantidad == pytest.approx(esperado, abs=TOL)
    assert esperado == pytest.approx(CP["cimientos_salida_s045_m3"],
                                     abs=TOL_CP)
    assert "cimientos del cabezal de salida, bajo agua (bajo el nivel " \
           "freatico)" not in r


def test_sobreancho_fuera_de_la_ventana_de_501_04_no_entra():
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("sobreancho_excavacion_estructuras_m",
                                     0.50)


def test_zanja_de_tmc_y_de_hdpe_por_veces_el_diametro():
    for tipo, factor in ((TipoMaterial.TMC, 1.5), (TipoMaterial.HDPE, 2.0)):
        r = _excavacion(material=_material(tipo=tipo),
                        punto=_punto(NF_profundidad_m=5.0))
        zanja = _por_elemento(r)["zanja del conducto, en seco"]
        assert f"{factor:g}·D" in zanja.paso.sustitucion[0].procedencia


def test_sin_nivel_freatico_la_excavacion_no_se_clasifica():
    with pytest.raises(DatoFaltanteError, match="NF_profundidad_m"):
        _excavacion(punto=_punto(NF_profundidad_m=None))


def test_un_sucs_que_no_es_suelo_no_se_toma_por_material_comun():
    with pytest.raises(DatoFaltanteError, match="sucs_fundacion"):
        _excavacion(punto=_punto(sucs_fundacion="roca andesitica"))


def test_integral_positiva_es_exacta_en_los_tres_casos():
    assert M12.integral_positiva(1.0, 3.0, 2.0) == pytest.approx(4.0)
    assert M12.integral_positiva(-1.0, -3.0, 2.0) == 0.0
    # cruza el cero en x = 0.5: triangulo de base 0.5 y altura 1
    assert M12.integral_positiva(1.0, -1.0, 1.0) == pytest.approx(0.25)


# ===========================================================================
# Concreto (EG-2013 503.12, Tabla 503-07)
# ===========================================================================

def test_concreto_de_los_cabezales_a_mano():
    """
    Entrada: pantalla 0.3·2.0·1.8 = 1.08; zapata 3.0·0.4·1.8 = 2.16;
             vano -A_ext·0.3.
    Salida:  lo mismo mas los aleros: fuste 0.3·h_media·2.0 con h_media =
             (2.0 + 0.4)/2 + 1.0 - 0.4 = 1.8, y zapata 3.0·0.4·2.0 = 2.4,
             cada uno.
    f'c = 21 MPa -> Clase D (la de concreto reforzado de menor resistencia
    que lo alcanza).
    """
    ent, sal = M12.renglones_concreto_cabezales(
        cabezal=_cabezal(), seccion=SeccionCircular(D=D), celdas=1,
        espesor=T)
    vano = A_EXT * 0.30
    assert ent.cantidad == pytest.approx(1.08 + 2.16 - vano, abs=TOL)
    assert sal.cantidad == pytest.approx(
        1.08 + 2.16 + 2 * (0.3 * 1.8 * 2.0) + 2 * 2.4 - vano, abs=TOL)
    assert ent.partida == "503.A" and "Clase D" in ent.descripcion
    assert ent.cantidad == pytest.approx(CP["concreto_entrada_m3"], abs=TOL_CP)
    assert sal.cantidad == pytest.approx(CP["concreto_salida_m3"], abs=TOL_CP)


def test_clase_de_concreto_de_la_tabla_503_07():
    assert M12.clase_de_concreto(21.0, TIPO_VOLADIZO) == "D"
    assert M12.clase_de_concreto(25.0, TIPO_VOLADIZO) == "C"
    assert M12.clase_de_concreto(17.5, TIPO_VOLADIZO) == "E"
    assert M12.clase_de_concreto(35.0, TIPO_VOLADIZO) is None
    assert M12.clase_de_concreto(None, TIPO_GRAVEDAD) == "G"


# ===========================================================================
# Acero (EG-2013 504.10, Tabla 504-01)
# ===========================================================================

def test_el_acero_se_detiene_sin_el_incremento_del_despiece():
    with pytest.raises(CriterioPendienteError,
                       match="incremento_acero_por_despiece"):
        M12.renglones_acero_cabezales(cabezal=_cabezal())


def test_acero_de_los_cabezales_a_mano():
    """
    Cabezal de entrada (L_c = 1.8, H = 2.0, B = 3.0), pesos de la Tabla
    504-01 (1/2" = 1.00 kg/m, 3/8" = 0.56 kg/m):
        pantalla vertical      (1.8/0.20)·2.0·1.00         = 18.000
        pantalla horizontal  2·(2.0/0.25)·1.8·0.56         = 16.128
        punta transversal      (1.8/0.25)·3.0·1.00         = 21.600
    con i = 0.10:  1.10 · 55.728 = 61.3008 kg
    """
    assert PESO_BARRA_KG_M_EG2013["1/2"] == 1.00
    assert PESO_BARRA_KG_M_EG2013["3/8"] == 0.56
    ca.establecer_valor_dinamico("incremento_acero_por_despiece", 0.10)
    try:
        ent, sal = M12.renglones_acero_cabezales(cabezal=_cabezal())
    finally:
        ca.quitar_valor_dinamico("incremento_acero_por_despiece")
    assert ent.cantidad == pytest.approx(1.10 * (18.0 + 16.128 + 21.6),
                                         abs=TOL)
    assert (ent.partida, ent.unidad) == ("504.A", "kg")
    assert ent.cantidad == pytest.approx(CP["acero_cabezal_kg"], abs=TOL_CP)
    assert sal.cantidad == pytest.approx(ent.cantidad, abs=TOL)


def test_el_cabezal_de_gravedad_no_lleva_acero():
    c = _cabezal()
    c.entrada.tipo = c.salida.tipo = TIPO_GRAVEDAD
    assert M12.renglones_acero_cabezales(cabezal=c) == ()


def test_un_cabezal_armado_sin_armado_no_se_metra_en_silencio():
    c = _cabezal()
    c.armado = (_armado("entrada"),)
    with pytest.raises(MetodoNoEvaluableError, match="salida"):
        M12.renglones_acero_cabezales(cabezal=c)


# ===========================================================================
# Losa de entrega (EG-2013 503.12)
# ===========================================================================

def test_losa_de_entrega_entre_los_aleros_a_mano():
    """
    Entrada (sin aleros): 0.3·1.8·1.5 + 0.4·0.8·1.8 = 0.81 + 0.576.
    Salida: cada alero de 2.0 m a 45 grados llega a 2·cos45 = 1.4142 m del
    cabezal y se abre 2·sen45 = 1.4142 m; la losa de 1.5 m lo pasa:
        area = 1.8·1.5 + 2·[tan45·1.4142^2/2 + 1.4142·(1.5 - 1.4142)]
        dentellon = 0.4·0.8·(1.8 + 2·1.4142)
    """
    with pytest.raises(CriterioPendienteError,
                       match="clase_concreto_losa_entrega"):
        M12.renglones_losa_entrega(cabezal=_cabezal())
    ca.establecer_valor_dinamico("clase_concreto_losa_entrega", "E")
    try:
        ent, sal = M12.renglones_losa_entrega(cabezal=_cabezal())
    finally:
        ca.quitar_valor_dinamico("clase_concreto_losa_entrega")
    assert ent.cantidad == pytest.approx(0.81 + 0.576, abs=TOL)
    a = 2.0 * math.cos(math.radians(45))
    area = 1.8 * 1.5 + 2 * (a ** 2 / 2 + a * (1.5 - a))
    esperado = 0.3 * area + 0.4 * 0.8 * (1.8 + 2 * a)
    assert sal.cantidad == pytest.approx(esperado, abs=TOL)
    assert "Clase E" in sal.descripcion
    assert ent.cantidad == pytest.approx(CP["losa_entrada_m3"], abs=TOL_CP)
    assert sal.cantidad == pytest.approx(CP["losa_salida_m3"], abs=TOL_CP)


# ===========================================================================
# Enrocado y geotextil (HEC-14 10.2, EG-2013 511.13)
# ===========================================================================

def test_enrocado_y_geotextil_a_mano():
    """
    D = 1.0, L = 5.0, e = 0.6: W_0 = 3.0, W_L = 3.0 + (2/3)·5.0 = 6.3333;
    A = (3.0 + 6.3333)/2·5.0 = 23.3333 m2; V = 14.0 m3. El geotextil mide
    el area, traslapes incluidos (511.13).
    """
    prot = SimpleNamespace(longitud=5.0, espesor=0.6, d50=0.25,
                           filtro=SimpleNamespace(clase_geotextil="Clase 1"))
    enr, geo = M12.renglones_proteccion_salida(
        proteccion=prot, seccion=SeccionCircular(D=D), celdas=1)
    A = (3.0 + 3.0 + 2 / 3 * 5.0) / 2 * 5.0
    assert enr.cantidad == pytest.approx(A * 0.6, abs=TOL)
    assert enr.partida == "" and enr.etiqueta_partida == "A"
    assert (geo.partida, geo.unidad) == ("511.A", "m2")
    assert geo.cantidad == pytest.approx(A, abs=TOL)
    assert enr.cantidad == pytest.approx(CP["enrocado_m3"], abs=TOL_CP)
    assert geo.cantidad == pytest.approx(CP["geotextil_m2"], abs=TOL_CP)


def test_sin_filtro_no_hay_geotextil():
    prot = SimpleNamespace(longitud=5.0, espesor=0.6, d50=None, filtro=None)
    renglones = M12.renglones_proteccion_salida(
        proteccion=prot, seccion=SeccionCircular(D=D), celdas=1)
    assert [r.rubro for r in renglones] == ["enrocado"]


# ===========================================================================
# Totales y cuadro de compatibilidad
# ===========================================================================

def test_los_totales_suman_la_misma_partida_de_puntos_distintos():
    (r,) = M12.renglones_conducto(
        material=_material(), seccion=SeccionCircular(D=D), celdas=1,
        espesor=T, cabezal=_cabezal(), S=S)
    totales = M12.totales_por_partida(
        (MetradoDelPunto("P-1", (r,)), MetradoDelPunto("P-2", (r, r))))
    (t,) = totales
    assert t.cantidad == pytest.approx(3 * r.cantidad, abs=TOL)
    assert t.puntos == ("P-1", "P-2")


def _tamizado(*, factible, actual=102.0, minima=101.5):
    from src.modelos import CondicionRasante
    return SimpleNamespace(
        cota_rasante_actual=actual, cota_rasante_min=minima,
        cota_por_recubrimiento=minima - 0.2, cota_por_resguardo=minima,
        condicion_gobernante=CondicionRasante.RESGUARDO, factible=factible,
        delta_rasante_m=0.0 if factible else minima - actual,
        cota_entrada=99.9, cota_clave=101.0, provisional=False, aviso="")


def test_cuadro_de_compatibilidad_tres_estados():
    ok = M12.fila_compatibilidad(punto=_punto(),
                                 tamizado=_tamizado(factible=True),
                                 cota_salida=99.78)
    assert ok.estado == ESTADO_RASANTE_COMPATIBLE
    assert ok.holgura_m == pytest.approx(0.5) and ok.delta_rasante_m is None
    mal = M12.fila_compatibilidad(punto=_punto(), tamizado=_tamizado(
        factible=False, actual=101.0, minima=101.3))
    assert mal.estado == ESTADO_RASANTE_SUBIR
    assert mal.delta_rasante_m == pytest.approx(0.3)
    assert mal.holgura_m == pytest.approx(-0.3)
    sin = M12.fila_compatibilidad(punto=_punto(), motivo="detenido")
    assert sin.estado == ESTADO_RASANTE_SIN_TAMIZADO and sin.motivo
    nf = M12.fila_compatibilidad(punto=_punto(), delta_no_factible=0.4)
    assert nf.estado == ESTADO_RASANTE_SUBIR and nf.delta_rasante_m == 0.4


# ===========================================================================
# De punta a punta: la corrida de referencia `expediente_cabezal`
# ===========================================================================

@pytest.fixture(scope="module")
def corrida():
    from src import indice_formulas as idx
    ref = next(c for c in idx.CORRIDAS_DE_REFERENCIA
               if c.nombre == "expediente_cabezal")
    return idx.correr_referencia(ref)


def test_el_servicio_metra_el_punto_con_cabezal(corrida):
    a01 = next(p for p in corrida.puntos if p.punto.id == "A-01")
    rubros = {r.rubro for r in a01.metrado.renglones}
    assert {"conducto", "excavacion", "concreto", "enrocado",
            "geotextil"} <= rubros
    assert rubros <= set(RUBROS_DE_METRADO)
    (conducto,) = [r for r in a01.metrado.renglones if r.rubro == "conducto"]
    assert conducto.cantidad == pytest.approx(
        a01.cabezal.longitud_metrado
        * math.sqrt(1 + a01.geometria.S_conducto ** 2), abs=TOL)
    # Lo que no se puede medir es un Bloqueo de la Fase 11 con su criterio.
    pendientes = {b.criterio for b in a01.bloqueos
                  if b.fase.startswith("Fase 11")
                  and b.tipo is TipoDeBloqueo.CRITERIO_PENDIENTE}
    assert pendientes == {"incremento_acero_por_despiece",
                          "clase_concreto_losa_entrega"}
    # Los puntos sin cabezal no se metran, y todos tienen fila del cuadro.
    for p in corrida.puntos:
        assert p.compatibilidad_rasante is not None
        if p.cabezal is None:
            assert p.metrado is None
    assert a01.compatibilidad_rasante.estado == ESTADO_RASANTE_COMPATIBLE


def test_los_totales_del_expediente_y_las_tres_vistas(corrida):
    import cli
    from src.modulos import M11_reporte as M11
    assert corrida.totales_metrado
    datos = json.loads(json.dumps(cli.informe_json(corrida)))
    partidas = {t["partida"] for t in datos["metrados"]}
    assert {"506.A", "501.C", "503.A", "511.A"} <= partidas
    a01 = next(p for p in datos["puntos"] if p["id"] == "A-01")
    assert a01["metrado"]["renglones"]
    assert a01["compatibilidad_rasante"]["estado"] == "compatible"
    texto = "\n".join(cli._lineas_metrados(corrida))
    assert "506.A" in texto and "COMPATIBILIDAD" in texto
    html = M11.bloque_metrados_proyecto(corrida)
    assert "Cuadro de compatibilidad" in html and "506.A" in html
    punto = next(p for p in corrida.puntos if p.punto.id == "A-01")
    assert "Metrados del punto" in M11._bloque_metrado(punto)
    # Los pasos del metrado entran a la memoria (anexo, discrepancias).
    assert any(p.fundamento_id.startswith("F11.")
               for p in M11.pasos_del_punto(punto))


def test_declarar_los_dos_criterios_libera_acero_y_losa():
    """La misma corrida de referencia con los dos criterios declarados: la
    referencia retira y repone las declaraciones de la suite, y estas dos
    entran como las de su carpeta."""
    from src import indice_formulas as idx
    ref = next(c for c in idx.CORRIDAS_DE_REFERENCIA
               if c.nombre == "expediente_cabezal")

    class _ConDeclaraciones(type(ref)):
        @property
        def declaraciones(self):
            return dict(super().declaraciones,
                        incremento_acero_por_despiece=0.10,
                        clase_concreto_losa_entrega="D")

    informe = idx.correr_referencia(
        _ConDeclaraciones(ref.nombre, ref.alcance, ref.rotulo))
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    rubros = {r.rubro for r in a01.metrado.renglones}
    assert {"acero", "losa de entrega"} <= rubros
    assert not [b for b in a01.bloqueos if b.fase.startswith("Fase 11")]
    acero = [r for r in a01.metrado.renglones if r.rubro == "acero"]
    assert all(r.cantidad > 0 and r.partida == "504.A" for r in acero)


def test_a_perfil_no_hay_metrado_y_si_cuadro():
    from src import indice_formulas as idx
    ref = next(c for c in idx.CORRIDAS_DE_REFERENCIA
               if c.nombre == "perfil_guia")
    informe = idx.correr_referencia(ref)
    assert all(p.metrado is None for p in informe.puntos)
    assert informe.totales_metrado == ()
    assert all(p.compatibilidad_rasante is not None for p in informe.puntos)
    assert not [b for p in informe.puntos for b in p.bloqueos
                if b.fase.startswith("Fase 11")]


def test_las_piezas_de_geometria_que_suman_los_renglones():
    """Las funciones de geometria del metrado, una por una, contra la mano:
    el vano del tubo, el ancho de la losa en el cabezal y en su borde, el
    area de la losa recta, y las partes del cabezal recto."""
    from src.modulos import M11_reporte as M11
    assert M12.area_exterior_del_conducto(SeccionCircular(D=D), T, 1) == \
        pytest.approx(A_EXT, abs=TOL)
    c = _cabezal()
    assert M12.ancho_losa(c.salida, 0.0) == pytest.approx(1.8, abs=TOL)
    assert M12.ancho_losa(c.salida, 1.5) == pytest.approx(
        1.8 + 2 * 2.0 * math.sin(math.radians(45)), abs=TOL)
    assert M12.area_losa(c.entrada) == pytest.approx(1.8 * 1.5, abs=TOL)
    partes = dict(M12.volumen_cabezal(c.entrada, A_EXT))
    assert partes["pantalla"] == pytest.approx(1.08, abs=TOL)
    assert partes["zapata"] == pytest.approx(2.16, abs=TOL)
    assert partes["vano del conducto (se descuenta)"] == pytest.approx(
        -A_EXT * 0.30, abs=TOL)
    # Y la memoria toma los pasos del metrado sin repetir el de una
    # excavacion partida en dos renglones.
    renglones = _excavacion()
    punto = SimpleNamespace(metrado=MetradoDelPunto("P-1", renglones))
    pasos = M11.traza_metrado(punto)
    assert len(pasos) == len({id(p) for p in pasos}) < len(renglones)
