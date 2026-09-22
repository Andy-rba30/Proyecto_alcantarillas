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
CITAS_NUEVAS = ("MP.GLOSARIO#OBRAS_DE_ARTE_MENORES", "AASHTO_LRFD_9.1.2#BRIDGE")


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
    assert d.gana == "AASHTO_LRFD_9"
    assert {p.quien for p in d.partes} == {"MC_HHD", "MP", "AASHTO_LRFD_9"}
    assert "cauce" in d.por_que.lower()


def test_r48001_el_paso_de_la_luz_declara_la_discrepancia_y_la_magnitud():
    v = M1.verificar_luz(3.0, "A-01")
    assert DIS in v.paso.discrepancias
    for cita_id in ("MP.GLOSARIO#OBRAS_DE_ARTE_MENORES", "AASHTO_LRFD_9.1.2#BRIDGE"):
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

def test_sisf13_la_fuente_m170m_dice_que_sus_tablas_no_se_pueden_transcribir():
    f = registro.construir().fuente("AASHTO_M170M")
    nota = f.nota.lower()
    assert "no se puede" in nota or "no se pueden" in nota
    assert "371" in f.nota and "1390" in f.nota
    assert "renderizar la pagina y leerla" not in nota
