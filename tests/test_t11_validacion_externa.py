"""
tests/test_t11_validacion_externa.py
====================================
Punto 2 de T-11 (validacion externa): `docs/validacion_hds5.md` y
`docs/validacion_hy8.md` se GENERAN (`tests/apoyo/validacion_externa.py`) y
este archivo los regenera a memoria y los compara; cada juicio que el
documento imprime se fija aqui; y cada cifra publicada de los ejemplos de
HEC-14 que T-8 uso como oraculo se busca en el TEXTO DE SU PAGINA (marca
`pdf`: HEC-14 vive solo en el repositorio de normas, `NORMAS_DIR`).

NO SE ESCRIBIO EN ROJO PRIMERO, y se dice: los casos son los de T-2 y T-8,
que ya pasaban; lo nuevo es el documento y la verificacion por pagina de
las cifras de HEC-14, cuyo rojo se midio contra la base `14f6138` (el modulo
de apoyo no existia: rojo de recoleccion). Ningun numero del motor se toca.
"""

from __future__ import annotations

import pytest

from src.normativa import fuentes as fu
from src.normativa.extraccion import (PDF_NO_DISPONIBLE, pymupdf_disponible,
                                      texto_de_pagina)
from tests.apoyo import validacion_externa as VE
from tests.apoyo import validacion_integral as V
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures.casos_patron import CP_HDS5_DG1

# 1 - 1/sqrt(1 + S^2) frente a su primer termino de Taylor, S^2/2: con S =
# 0.010 difieren en el orden de S^2 (relativo), 1e-4.
REL_TAYLOR = 1e-3


@pytest.fixture(scope="module")
def juego():
    return V.correr_juego()


# ===========================================================================
# Sincronia
# ===========================================================================

def test_validacion_hds5_esta_sincronizado():
    assert VE.DOCUMENTO.read_text(encoding="utf-8") == VE.generar(), (
        "docs/validacion_hds5.md no esta sincronizado: "
        "python -m tests.apoyo.validacion_externa --escribir")


def test_validacion_hy8_esta_sincronizado(juego):
    assert VE.DOCUMENTO_HY8.read_text(encoding="utf-8") == \
        VE.generar_hy8(juego), (
        "docs/validacion_hy8.md no esta sincronizado: "
        "python -m tests.apoyo.validacion_externa --escribir")


# ===========================================================================
# HDS-5: el censo dice la verdad
# ===========================================================================

def test_las_cifras_de_hds5_fuera_de_la_lectura_son_las_censadas():
    lectura = CP_HDS5_DG1["tolerancia_de_lectura"]
    filas = [f for f in VE.filas_hds5() if f.diferencia is not None]
    fuera = {(f.fila, f.magnitud) for f in filas
             if not VE.dentro_de(f.diferencia, lectura)}
    assert fuera == set(CP_HDS5_DG1["fuera_de_tolerancia"])
    controles = [f for f in VE.filas_hds5() if f.diferencia is None]
    assert controles and all(f.publicado == f.calculado for f in controles)


def test_la_causa_censada_dice_la_diferencia_que_el_motor_da():
    """
    Correcciones de T-11 (H12): la causa de cada casilla censada empieza por
    la diferencia MEDIDA con dos decimales, y el documento la imprime con dos
    decimales (con uno, «−3.0 %» salia al lado de «fuera del 3 %» y la causa
    decia «−3.1 %»).
    """
    for f in VE.filas_hds5():
        if not f.censada:
            continue
        impresa = f.censada.split("%")[0].strip().replace("−", "-")
        assert impresa == f"{f.diferencia * 100:+.2f}", (f.fila, f.magnitud)
        assert VE._pct(f.diferencia) == f"{f.diferencia:+.2%}"


def test_la_frontera_de_una_banda_se_compara_con_tolerancia_nombrada():
    """
    H12: 0.495 / 0.50 - 1 es el -1 % EXACTO en decimal y en coma flotante da
    -0.010000000000000009; con la tolerancia de frontera nombrada cae dentro
    del 1 %, y el censo de HEC-14 queda vacio.
    """
    assert 0.495 / 0.50 - 1 < -VE.TOLERANCIA_EJEMPLO_IMPRESO
    assert VE.dentro_de(0.495 / 0.50 - 1, VE.TOLERANCIA_EJEMPLO_IMPRESO)
    assert VE.CENSO_HEC14 == {}
    texto = VE.DOCUMENTO.read_text(encoding="utf-8")
    assert "SIN CENSAR" not in texto and "censada:" not in texto


def test_las_filas_de_metal_corrugado_caen_en_el_intervalo_de_n():
    juicios = {(f.fila, f.magnitud): VE.juicio_por_intervalo(f)
               for f in VE.filas_por_intervalo()}
    for (fila, magnitud), juicio in juicios.items():
        if magnitud == "control":
            assert juicio.startswith("igual con el n típico"), (fila, juicio)
        elif "no depende de n" in juicio:
            assert juicio.endswith(f"≤ {CP_HDS5_DG1['tolerancia_de_lectura']:.0%}")
        else:
            assert juicio == "sí", (fila, magnitud, juicio)
    # Lo que el documento dice del control del CMP de 72 in, medido: con el
    # n tipico gobierna la entrada, como en el formulario, y dentro del rango
    # de la Tabla B.1 el control cambia.
    assert "cambia dentro del rango" in juicios[("cmp_72_bisel_45", "control")]


# ===========================================================================
# HEC-14: cada cifra, dentro o censada; y escrita en su pagina
# ===========================================================================

def test_los_ejemplos_de_hec14_reproducen_lo_publicado_o_estan_censados():
    tol = VE.TOLERANCIA_EJEMPLO_IMPRESO
    filas = VE.filas_hec14()
    assert len(filas) == sum(len(e.cifras) for e in VE.EJEMPLOS_HEC14)
    for f in filas:
        if f.censada:
            assert not VE.dentro_de(f.diferencia, tol), (f.ejemplo, f.magnitud)
        else:
            assert VE.dentro_de(f.diferencia, tol), (f.ejemplo, f.magnitud,
                                                     f.calculado, f.publicado)
    assert set(VE.CENSO_HEC14) <= {(f.ejemplo, f.magnitud) for f in filas}


def test_las_paginas_de_hec14_son_las_que_la_paginacion_predice():
    f = fu.FUENTES["HEC14"]
    for ej in VE.EJEMPLOS_HEC14:
        assert tuple(f.paginacion.pagina_pdf(i) for i in ej.paginas_impresas) \
            == ej.paginas_pdf, ej.clave


@pytest.mark.pdf
@pytest.mark.skipif(not pymupdf_disponible(), reason=PDF_NO_DISPONIBLE)
@pytest.mark.parametrize("clave", [e.clave for e in VE.EJEMPLOS_HEC14])
def test_cada_cifra_publicada_de_hec14_esta_escrita_en_su_pagina(clave):
    f = fu.FUENTES["HEC14"]
    ruta = fu.ruta_pdf(f)
    if not ruta.exists():
        pytest.skip(f"falta {f.archivo_pdf}: enlace el repositorio de normas "
                    f"con {fu.VARIABLE_NORMAS_DIR} (ver CLAUDE.md)")
    ej = next(e for e in VE.EJEMPLOS_HEC14 if e.clave == clave)
    texto = " ".join(" ".join(texto_de_pagina(ruta, n).split())
                     for n in ej.paginas_pdf)
    assert ej.titulo.split(",")[0].split(" (SI)")[0].split(" (CU)")[0] in texto
    for magnitud, _publicado, _unidad, frase, _x in ej.cifras:
        assert frase in texto, (clave, magnitud, frase)


# ===========================================================================
# HY-8: el procedimiento no afirma ningun resultado
# ===========================================================================

def test_el_procedimiento_de_hy8_no_afirma_resultados(juego):
    texto = VE.generar_hy8(juego)
    assert "NO afirma ningún resultado de HY-8" in texto
    assert "DATOS DE PRUEBA, NO DEL PROYECTO" in texto
    # Una fila de entradas y una de salidas por punto dimensionado.
    ids = [f["id"] for f in VE.filas_hy8(juego)]
    assert ids == ["A-01", "A-02", "B-01", "C-01"]
    for id_punto in ids:
        assert texto.count(f"| {id_punto} |") == 2, id_punto


# --- Las cinco reglas de la decision del dueño (2026-11-13 18:25), H5 ------
# El test ya no es tautologico (H5): fija cada regla por su efecto.

def test_regla_1_la_tolerancia_es_criterio_del_proyecto_no_normativo(juego):
    assert VE.TOLERANCIA_HY8_EXPLICAR == CP_HDS5_DG1["tolerancia_de_lectura"]
    assert VE.TOLERANCIA_HY8_DISCREPANCIA == \
        CP_HDS5_DG1["tolerancia_de_la_fuente"]
    texto = VE.generar_hy8(juego)
    seccion_5 = texto[texto.index("## 5."):texto.index("## 6.")]
    assert "criterio del proyecto" in seccion_5
    assert "NO normativo" in seccion_5
    assert "aceptado por el dueño el 2026-11-13" in seccion_5
    assert "propuesta de T-11, no normativa" not in texto
    # Las tres bandas, por el juicio (la frontera, con su tolerancia).
    j = lambda hy8: VE.juicio_hy8(1.0, hy8, control_programa="entrada",  # noqa: E731
                                  control_hy8="entrada")
    assert j(1.03) == j(0.97) == VE.JUICIO_COINCIDE
    assert j(1.0301) == j(1.10) == VE.JUICIO_EXPLICAR
    assert j(1.1001) == j(0.89) == VE.JUICIO_DISCREPANCIA


def test_regla_2_se_aplica_a_HW_y_a_HW_sobre_D(juego):
    texto = VE.generar_hy8(juego)
    seccion_4 = texto[texto.index("## 4."):texto.index("## 5.")]
    assert "HW que gobierna (m) · HW/D" in seccion_4
    volcado = {p["id"]: p for p in VE_volcado(juego)}
    for f in VE.filas_hy8(juego):
        d = volcado[f["id"]]["diseno"]
        hw_d = f"{d['HW_gobernante_m']:.3f} · {d['HW_gobernante_m'] / f['altura']:.3f}"
        fila = next(l for l in seccion_4.splitlines()
                    if l.startswith(f"| {f['id']} |"))
        assert hw_d in fila, f["id"]
    # La altura del marco es la de la celda (0.90), no el ancho.
    c01 = next(f for f in VE.filas_hy8(juego) if f["id"] == "C-01")
    assert c01["altura"] == pytest.approx(0.90, rel=REL_TRANSPORTE)


def test_regla_3_control_distinto_va_a_explicar_sea_cual_sea_el_porcentaje():
    assert VE.juicio_hy8(1.0, 1.0, control_programa="entrada",
                         control_hy8="salida") == VE.JUICIO_EXPLICAR
    assert VE.juicio_hy8(1.0, 1.5, control_programa="salida",
                         control_hy8="entrada") == VE.JUICIO_EXPLICAR


def test_regla_4_la_velocidad_va_sin_veredicto_donde_no_sale_del_mismo_modo(juego):
    volcado = {p["id"]: p for p in VE_volcado(juego)}
    veredictos = {f["id"]: VE.velocidad_hy8(volcado[f["id"]]["diseno"])[1]
                  for f in VE.filas_hy8(juego)}
    assert veredictos == {"A-01": "no", "A-02": "no", "B-01": "no", "C-01": "sí"}
    texto = VE.generar_hy8(juego)
    assert "¿Lleva veredicto?" in texto
    assert texto.count("Velocidad a la salida (m/s) — sin veredicto") == 3


def test_regla_5_version_y_fecha_de_HY8_en_el_encabezado_de_cada_tabla(juego):
    texto = VE.generar_hy8(juego)
    seccion_6 = texto[texto.index("## 6."):]
    encabezados = [l for l in seccion_6.splitlines() if l.startswith("### ")]
    assert len(encabezados) == len(VE.filas_hy8(juego))
    for l in encabezados:
        assert "versión de HY-8" in l and "fecha de la corrida" in l, l
        assert "obligatorios" in l


def test_el_procedimiento_de_hy8_es_ejecutable(juego):
    """
    H5: Roadway Data con la cota de rasante de cada punto (la cresta) y su
    ancho, el n del tirante normal dicho, y la diferencia de longitud con la
    horizontal por punto (S = 0.010 de B-01: 0.0050 %, no «≤ 0.002 %»).
    """
    texto = VE.generar_hy8(juego)
    assert "Roadway Data" in texto and "no debe haber desborde" in texto
    assert "Tirante normal, n máx." in texto
    assert "≤ 0.002 %" not in texto
    seccion_3 = texto[texto.index("## 3."):texto.index("## 4.")]
    for f in VE.filas_hy8(juego):
        fila = next(l for l in seccion_3.splitlines()
                    if l.startswith(f"| {f['id']} |"))
        assert f"{f['cota_rasante']:.3f} / {f['ancho_plataforma']:.2f}" in fila
    b01 = next(l for l in seccion_3.splitlines() if l.startswith("| B-01 |"))
    assert "(0.0050%)" in b01
    assert VE.diferencia_de_longitud_horizontal(0.010) == \
        pytest.approx(0.010 ** 2 / 2, rel=REL_TAYLOR)


def VE_volcado(informe):
    return V.volcado(informe)["puntos"]
