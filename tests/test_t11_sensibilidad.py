"""
tests/test_t11_sensibilidad.py
==============================
Punto 3 de T-11 (sensibilidad): `docs/validacion_sensibilidad.md` se GENERA
con `tests/apoyo/sensibilidad.py` (un barrido de `src/barrido.py` por clave,
sobre el juego de DATOS DE PRUEBA de la validacion integral) y este archivo
lo regenera a memoria y lo compara. Fija ademas los JUICIOS que el anexo
imprime --- que clave mueve el diseño, cual solo veredictos, cual la corrida
no lee y por que ---, para que un cambio del programa que los mueva no pase
en silencio.

LA MARCA `lento` SE RETIRO en las correcciones de T-11 (H13): la convencion
del `conftest` la reserva a un SUBPROCESO pesado, y aqui no hay ninguno (la
fixture `medidas` corre unas doscientas corridas en proceso: ~60 s).

NO SE ESCRIBIO EN ROJO PRIMERO, y se dice: T-11 mide lo que el programa ya
hace; el rojo es de recoleccion contra la base `14f6138` (el modulo de apoyo
no existia). Ningun valor de archivo cambia: cada barrido declara su valor
para su corrida y deja el proceso como estaba (`barrido.barrer`).
"""

from __future__ import annotations

import pytest

from src import criterios_adoptados as ca
from tests.apoyo import sensibilidad as S


@pytest.fixture(scope="module")
def medidas():
    estado = ca.valores_dinamicos()
    salida = S.medir_todos()
    # Ningun barrido deja nada declarado.
    assert ca.valores_dinamicos() == estado
    return salida


def _por_efecto(medidas):
    salida = {}
    for m in medidas:
        clave = m.barrido.clave + ("" if m.barrido.base == "juego"
                                   else f"@{m.barrido.base}")
        salida.setdefault(m.efecto, set()).add(clave)
    return salida


def test_el_anexo_de_sensibilidad_esta_sincronizado(medidas):
    assert S.DOCUMENTO.read_text(encoding="utf-8") == S.generar(medidas), (
        "docs/validacion_sensibilidad.md no esta sincronizado: "
        "python -m tests.apoyo.sensibilidad --escribir")


def test_cada_barrido_recorre_la_ventana_de_su_criterio():
    """
    El primer valor es el del juego (salvo un opcional sin valor), y TODOS
    los valores estan DENTRO de la ventana del criterio cuando la ventana es
    legible por maquina (correcciones de T-11, H13: el test no lo miraba).
    """
    for b in S.BARRIDOS:
        c = ca.criterio(b.clave)
        assert c.sensibilidad, b.clave
        assert c.etiqueta in ("A", "C"), b.clave
        valores = S.valores_de(b)
        assert len(valores) >= 2 and len(set(map(repr, valores))) == len(valores)
        efectivo = S.J.DECLARACIONES.get(b.clave, c.valor)
        if efectivo is not None:
            assert valores[0] == efectivo, b.clave
        ventana = c.sensibilidad
        if c.forma == "categoria":
            assert set(valores) <= set(ventana), b.clave
        elif isinstance(ventana, tuple) and len(ventana) == 2 and all(
                isinstance(x, (int, float)) for x in ventana):
            lo, hi = ventana
            assert all(lo <= v <= hi for v in valores), (b.clave, valores)
        elif isinstance(ventana, dict):
            for v in valores:
                for campo, (lo, hi) in ventana.items():
                    assert lo <= v[campo] <= hi, (b.clave, campo, v[campo])


def test_la_lista_de_barridos_se_deriva_del_censo_y_lo_parte_entero():
    """
    H3 (MEDIA): todo criterio con valor efectivo y ventana legible por
    maquina se barre (`barribles_del_censo` esta dentro de `BARRIDOS`), y
    los que no se barren estan POR NOMBRE en `NO_BARRIBLES`, con su razon:
    las dos listas parten el archivo de criterios sin solaparse.
    """
    barridos = {b.clave for b in S.BARRIDOS}
    assert set(S.barribles_del_censo()) <= barridos
    assert not barridos & set(S.NO_BARRIBLES)
    assert barridos | set(S.NO_BARRIBLES) == set(ca.CRITERIOS)
    assert all(r.strip() for r in S.NO_BARRIBLES.values())
    # Los que el auditor midio fuera de la lista estan dentro.
    assert {"espesor_pared_cajon", "pendiente_minima_conducto",
            "remanso_derecho_via", "umbral_no_colapso_evento_extremo",
            "peso_especifico_relleno_kn_m3", "margen_zapata_bajo_socavacion_m",
            "referencia_profundidad_socavacion",
            "lectura_coeficientes_socavacion_hec14",
            "punto_aplicacion_incremento_sismico",
            "terreno_delante_del_cabezal", "F_pga_lectura_columna_extrema",
            "talud_terraplen", "metodo_longitud_conducto",
            "revestimiento_cuneta", "origen_cota_fondo_entrada"} <= barridos
    # predimensionamiento_cabezal: su campo de la zapata ya esta en el techo.
    c = ca.criterio("predimensionamiento_cabezal")
    assert c.valor["fraccion_ancho_zapata"] == \
        c.sensibilidad["fraccion_ancho_zapata"][1]
    assert "YA ES EL TECHO" in S.NO_BARRIBLES["predimensionamiento_cabezal"]


def test_lo_que_la_corrida_no_lee_es_lo_que_el_anexo_explica(medidas):
    no_leidos = {(m.barrido.clave, m.barrido.base) for m in medidas
                 if not m.leido}
    assert no_leidos == set(S.NO_LEIDO_PORQUE)


def test_los_juicios_del_anexo(medidas):
    """
    LA RESPUESTA DE T-11 A «QUE [A] MUEVEN UN DIAMETRO O UN VEREDICTO DENTRO
    DE SU VENTANA», medida sobre el juego. Si el programa cambia y una clave
    cambia de clase, este test lo dice y el anexo se regenera DECLARANDOLO.
    """
    # REESCRITO EN LAS CORRECCIONES DE T-11 (H3), declarandolo: la lista
    # paso de 31 barridos escritos a mano a 82 derivados del censo, y lo que
    # «mueve el diseño» paso de cinco a once (diez criterios: el techo del
    # concreto sobre dos bases). Antes se decia «cinco mueven el diseño».
    assert _por_efecto(medidas) == {
        "MUEVE EL DISEÑO": {
            "seccion_receptor@juego_sin_TW", "v_max_concreto_eleccion",
            "v_max_concreto_eleccion@juego_tmc_excluida",
            "regimen_v2b", "borde_libre_y_sobre_d_max", "embocadura_cabezal",
            "espesor_pared_cajon", "pendiente_minima_conducto",
            "remanso_derecho_via", "umbral_no_colapso_evento_extremo",
            "origen_cota_fondo_entrada"},
        "MUEVE VEREDICTOS": {
            "eta_importancia_operativa_conducto", "factor_muro_eleccion",
            "gamma_EQ", "fraccion_delta_sobre_phi_trasdos",
            "fila_phi_estabilidad_cabezal",
            "factores_inclinacion_carga_portante",
            "regla_pendiente_relleno_trasdos",
            "regimen_resistencia_elementos_cabezal", "eta_ductilidad_cabezal",
            "eta_redundancia_cabezal", "marco_estabilidad_cabezal",
            "regimen_cabezal", "drenaje_trasdos", "fc_cabezal_mpa",
            "F_pga_lectura_columna_extrema", "lectura_coeficientes_socavacion_hec14",
            "margen_zapata_bajo_socavacion_m", "metodo_longitud_conducto",
            "peso_especifico_relleno_kn_m3", "phi_relleno_trasdos",
            "punto_aplicacion_incremento_sismico",
            "referencia_profundidad_socavacion", "revestimiento_cuneta",
            "talud_terraplen", "terreno_delante_del_cabezal"},
        "MUEVE EL HW": {"n_manning_cajon", "ke_entrada"},
        "LEÍDO, SIN EFECTO MEDIBLE": {
            "HW_D_max", "v_max_tmc", "v_max_hdpe", "fraccion_llena_mayor_parte",
            "instalacion_estandar_concreto", "carga_viva_bajo_relleno_alto",
            "duracion_caudal_pico_socavacion_min", "acceso_mantenimiento_v2b",
            "acero_refuerzo_cabezal", "borde_libre_canal_m",
            "clase_exposicion_fisuracion_cabezal", "condicion_pavimento",
            "corrugacion_y_espesor_tmc", "desajuste_empalme_canal_m",
            "desnivel_minimo_entrega_m", "espesor_proteccion_salida",
            "esviaje_max_grados", "lectura_velocidad_limite_cuneta",
            "long_max_cuneta", "longitud_proteccion_salida",
            "obras_familia_a_extremo_de_cuneta", "pendiente_maxima_conducto",
            "regimen_cortante_muro_e060_art_11_10_2",
            "regla_espesor_longitud_proteccion_salida",
            "regla_minimos_constructivos_cabezal",
            "suelo_agresivo_lrfd_sobre_tmc", "tipo_proteccion_entrada",
            "umbral_area_quebrada_importante_ha"},
        "NO LO LEE LA CORRIDA": {
            "borde_libre_bajo_tw_ahogante", "seccion_receptor",
            "hw_entrada_fuera_de_rango", "coeficiente_uniformidad_temez",
            "criterio_traccion_cabezal_ciclopeo", "demanda_sismica_licuefaccion",
            "distribucion_precipitacion_maxima", "duracion_minima_lluvia_min",
            "fabricacion_tmc", "homogeneidad_serie_fen", "inclinacion_muro_beta",
            "junta_arranque_cabezal_ciclopeo", "nivel_significancia_ks",
            "relacion_intensidad_duracion", "relleno_estructural_hdpe",
            "tc_fuera_de_la_poblacion_del_metodo"},
    }


def test_el_techo_de_velocidad_del_concreto_cambia_material_y_diametro(medidas):
    """
    El hallazgo mas fuerte del anexo, fijado con sus numeros: con el techo
    del concreto en el extremo inferior de su ventana (3.0 m/s, Tabla N 10
    del Manual), A-01 deja el concreto de 0.90 m (V3: la velocidad de salida
    es 3.2 m/s) y pasa a TMC de 1.20 m. El juego no lo declara y rige la
    regla de la ficha.
    """
    m = next(x for x in medidas if x.barrido.clave == "v_max_concreto_eleccion"
             and x.barrido.base == "juego")
    f = m.filas_por_valor[repr(3.0)]["A-01"]
    assert (f.material, f.seccion) == ("TMC galvanizada", "Ø 1.20 m")
    assert S.referencia("juego")["A-01"] == "Concreto reforzado, Ø 0.90 m"


def test_el_resultado_del_techo_del_concreto_depende_del_suelo_agresivo(medidas):
    """
    H6 (MEDIA): el criterio se queda SIN valor (decision del dueño, rige el
    6.0 m/s de la Tabla N 10) y el paso a TMC con 3.0 m/s es un resultado de
    la tesis que depende de OTRO [A]: con `suelo_agresivo_lrfd_sobre_tmc` =
    'excluye' el TMC sale por los sulfatos del juego (500 ppm > 200 de AASHTO
    LRFD 11.10.6.4.2a) y A-01 se detiene en el dato del fabricante del HDPE.
    El anexo lo dice con esas palabras.
    """
    assert ca.criterio("v_max_concreto_eleccion").valor is None
    m = next(x for x in medidas if x.barrido.clave == "v_max_concreto_eleccion"
             and x.barrido.base == "juego_tmc_excluida")
    f = m.filas_por_valor[repr(3.0)]["A-01"]
    assert not f.dimensionado
    assert "perfil_hdpe_fabricante" in m.bloqueo(3.0, "A-01")
    texto = S.DOCUMENTO.read_text(encoding="utf-8")
    assert "se queda SIN valor por decisión del dueño (2026-11-13)" in texto
    assert "resultado de la tesis que no cambia el fixture" in texto
    # El dato del juego NO se cambio (su linea de plausibilidad, en el
    # juego, dice ahora «insignificante para el concreto, agresivo para el
    # acero galvanizado»), y el anexo dice las dos cosas.
    assert S.J.EXTERNOS["globales"]["sulfatos_suelo_ppm"] == 500
    assert "agresivo para el acero galvanizado" in texto
    assert "«insignificantes» por la Tabla 4.4 de E.060" in texto


def test_leido_sin_efecto_se_define_y_el_HW_se_compara_con_tolerancia():
    """
    H3: «LEÍDO, SIN EFECTO MEDIBLE» dice en §1 que magnitudes NO compara, y
    el HW se compara con una tolerancia nombrada, no con `!=`.
    """
    texto = S.DOCUMENTO.read_text(encoding="utf-8")
    seccion_1 = texto[texto.index("## 1."):texto.index("## 2.")]
    assert "las demás magnitudes no se comparan" in seccion_1
    assert "no la corrida titular" in seccion_1
    # Por comportamiento: un HW que cambia en 3e-6 m (lo que la longitud
    # «movia» con `!=`) no mueve nada; uno que cambia en 4e-4 m, si.
    from types import SimpleNamespace as NS

    def _medida(hw_b):
        filas = [NS(valor=v, id_punto="X", dimensionado=True, material="m",
                    seccion="s", HW_gobernante_m=hw, verificaciones_que_cambian=())
                 for v, hw in ((1.5, 0.6230), (1.2, hw_b))]
        # 1.5 es el valor efectivo de `HW_D_max`: el primero es el del juego.
        return S.Medida(S.Barrido("HW_D_max", S.GRUPO_CONDUCTO, "prueba"),
                        (1.5, 1.2), NS(filas=filas), True)

    assert _medida(0.6230 + 3e-6).efecto == "LEÍDO, SIN EFECTO MEDIBLE"
    assert _medida(0.6234).efecto == "MUEVE EL HW"


def test_el_cabezal_de_la_regla_frente_a_sus_dos_A(medidas):
    """
    PRECISIONES_T-11: el cabezal de la regla que no pasa E3 estatico ni E1
    sismico se presenta CON LA SENSIBILIDAD. Medido: omitir los factores de
    inclinacion (C10.6.3.1.2a lo permite) hace pasar E1 sismica en los dos
    extremos de los cuatro puntos; la fila de phi de muros (Tabla 11.5.7)
    hace pasar E3 estatica a la SALIDA de A-01, A-02 y C-01; ninguno de los
    dos hace pasar E3 estatica a la entrada.
    """
    por_clave = {m.barrido.clave: S.estados_del_cabezal(m) for m in medidas
                 if m.barrido.clave in S.CLAVES_DEL_CABEZAL_DE_LA_REGLA}
    puntos = ("A-01", "A-02", "B-01", "C-01")
    for estados in por_clave.values():
        for p in puntos:
            # Con el valor de archivo (el primero), las cuatro no pasan.
            assert all(estados[(p, f)][0] == "no cumple"
                       for f in S.FILAS_DEL_CABEZAL), p
            # E3 estatica de entrada no pasa con ninguno.
            assert set(estados[(p, "E3-LRFD.est.e")]) == {"no cumple"}, p
    inclinacion = por_clave["factores_inclinacion_carga_portante"]
    for p in puntos:
        assert inclinacion[(p, "E1-LRFD.sis.e")][1] == "cumple"
        assert inclinacion[(p, "E1-LRFD.sis.s")][1] == "cumple"
        assert inclinacion[(p, "E3-LRFD.est.s")][1] == "no cumple"
    phi = por_clave["fila_phi_estabilidad_cabezal"]
    assert {p for p in puntos if phi[(p, "E3-LRFD.est.s")][1] == "cumple"} == \
        {"A-01", "A-02", "C-01"}
    assert all(phi[(p, "E1-LRFD.sis.e")][1] == "no cumple" for p in puntos)
