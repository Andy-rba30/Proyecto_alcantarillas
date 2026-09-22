"""
tests/test_cierre_varios.py
===========================
Aceptacion del cierre de los tres hallazgos sueltos que quedaban abiertos o
parciales fuera de C05 y C10, escrita PRIMERO EN ROJO y liberada al corregir:

  * R48-001 (C11): M1 comparaba «la luz» con 6.0 m sin decir QUE magnitud es.
    El Manual de Hidrologia escribe «luz» sin definirla; el glosario del
    Manual de Puentes define «luz libre» (obras de arte menores < 6.00 m) y
    «luz del tramo» (entre ejes de apoyo); AASHTO 1.2, a la que el 4.1.1.5.1
    remite, escribe «opening». Ninguna es el ANCHO DEL CAUCE natural. Lo que
    cierra: las dos definiciones entran al registro como citas verificadas,
    la discrepancia `DIS-LUZ-DENOMINACION` queda declarada (viva: llega a la
    memoria por el paso F2.LUZ y por el fundamento) y `luz_m` dice lo que es.
  * PC-31 (C14): `Registro` se construia cinco veces en cuatro instancias.
    Lo que cierra: `registro.construir` devuelve UNA instancia (cache), y los
    cuatro sitios que el dictamen nombro la comparten.
  * SIS-F-13 / NOR-PRO-04, mitad concreto: la serie de M 170M Tablas 1-5 no
    se puede transcribir del ejemplar de normas/ --- la capa de texto es
    ilegible Y el render de la pagina reproduce digitos equivocados (371 por
    375, 1390 por 1350, «3tS0») ---, y la ficha de la fuente lo dice con esas
    palabras en vez de prometer que «para citar hay que renderizar la pagina».
"""

from pathlib import Path

import pytest

from src import variables_entrada as ve
from src.modulos import M1_clasificacion as M1
from src.normativa import registro
from src.normativa.esquema import EstadoDiscrepancia

RAIZ = Path(__file__).resolve().parents[1]
DIS = "DIS-LUZ-DENOMINACION"
CITAS_NUEVAS = ("MP.GLOSARIO#OBRAS_DE_ARTE_MENORES", "AASHTO_LRFD_9.1.2#BRIDGE",
                "MP.1.10#FIG_1_10A_LUZ_LIBRE", "HDS5_3ED.1.2#NBIS", "HDS5_3ED.1.2#MODELO")


# ===========================================================================
# R48-001
# ===========================================================================

@pytest.mark.parametrize("cita_id", CITAS_NUEVAS)
def test_r48001_las_definiciones_de_luz_estan_en_el_registro_y_verificadas(cita_id):
    reg = registro.construir()
    c = reg.cita(cita_id)
    assert c.verificado is not None
    assert not c.tiene_pendientes


def test_r48001_la_discrepancia_esta_declarada_viva_y_gana_aashto():
    reg = registro.construir()
    d = reg.discrepancia(DIS)
    assert d.viva
    assert d.estado is EstadoDiscrepancia.ABIERTA
    assert d.gana == "HDS5_3ED"
    assert {p.quien for p in d.partes} == {"MC_HHD", "MP", "AASHTO_LRFD_9", "HDS5_3ED"}
    assert "cauce" in d.por_que.lower()
    # La discrepancia REAL entre fuentes, no una coincidencia disfrazada:
    # la luz libre por vano (Fig. 1.10-a) contra el ancho total (NBIS), y
    # 6.0 m contra 6.096 m, con cual gana en cada cosa.
    assert "6.096" in d.por_que and "6.0 m" in d.por_que
    assert "POR VANO" in " ".join(p.que_dice for p in d.partes)
    assert "total width" in " ".join(p.que_dice for p in d.partes)


def test_r48001_el_paso_de_la_luz_declara_la_discrepancia_y_la_magnitud():
    v = M1.verificar_luz(3.0, "A-01")
    assert DIS in v.paso.discrepancias
    for cita_id in ("MP.GLOSARIO#OBRAS_DE_ARTE_MENORES", "AASHTO_LRFD_9.1.2#BRIDGE",
                    "HDS5_3ED.1.2#NBIS"):
        assert cita_id in v.paso.citas_textuales
    luz = v.paso.sustitucion[0]
    assert "cauce" in luz.procedencia.lower()
    assert "abertura" in luz.procedencia.lower()
    # Y llega por el fundamento tambien: la discrepancia toca sus citas.
    reg = registro.construir()
    tocadas = reg.discrepancias_que_tocan(reg.fundamento("F2.LUZ").citas)
    assert DIS in {d.id for d in tocadas}


def test_r48001_luz_m_dice_que_no_es_el_ancho_del_cauce():
    concepto = ve.variable("luz_m").concepto.lower()
    assert "cauce" in concepto and "abertura" in concepto


# ===========================================================================
# PC-31
# ===========================================================================

def test_pc31_el_registro_es_una_sola_instancia():
    assert registro.construir() is registro.construir()


def test_pc31_los_cuatro_sitios_del_dictamen_comparten_la_instancia():
    from src import constantes_normativas as cn
    from src import criterios_adoptados as ca
    from src import modelos
    from src.modulos import M11_reporte as M11
    unica = registro.construir()
    assert cn._reg is unica
    assert M11._reg_M11 is unica
    assert ca._registro() is unica
    assert modelos._registro_normativo() is unica


# ===========================================================================
# SIS-F-13 / NOR-PRO-04, mitad concreto
# ===========================================================================

def test_sisf13_la_fuente_m170m_dice_que_tablas_son_ocr_y_cual_es_escaneo():
    """
    Las Tablas 1 a 4 no se pueden transcribir del ejemplar (imagen OCR con
    digitos equivocados) y la Tabla 5 si (PDF 10, escaneo real): la nota lo
    dice con esas palabras, sin prometer de mas ni de menos.
    """
    f = registro.construir().fuente("AASHTO_M170M")
    nota = f.nota
    assert "Tablas 1 a 4" in nota and "NO se pueden" in nota
    assert "371" in nota and "1390" in nota
    assert "Tabla 5" in nota and "PDF 10" in nota and "AASHTO_M170M.T5" in nota


def test_sisf13_la_serie_del_concreto_esta_transcrita_por_imagen_de_la_tabla_5():
    from tests.fixtures.casos_patron import CP11_SERIES_NOMINALES
    reg = registro.construir()
    t = reg.tabla("AASHTO_M170M.T5")
    serie = tuple(sorted(int(v) for v in t.columna_como_dict("dn_mm").values()))
    assert len(serie) == 27 and serie[0] == 300 and serie[-1] == 3600
    assert serie == CP11_SERIES_NOMINALES["concreto_reforzado"]["serie_mm"]
    # Pared B solo hasta 1200 y pared C hasta 1800: donde la pagina imprime
    # raya, la fila no lleva la clave.
    b = t.columna_como_dict("wall_b_mm"); c = t.columna_como_dict("wall_c_mm")
    assert len(b) == 11 and len(c) == 15
    assert reg.cita("AASHTO_M170M.T5").verificado is not None
