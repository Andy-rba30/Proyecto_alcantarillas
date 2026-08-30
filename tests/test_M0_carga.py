"""
tests/test_M0_carga.py
======================
M0 contra los dos fixtures de la Parte 1 y contra casos sinteticos escritos en
tmp_path (los fixtures del repositorio no se tocan).

Que es cada fixture
-------------------
    ejemplo_puntos.csv           4 filas validas: A-01, A-02, B-01 y C-01.
                                 Las 16 columnas de Sec. 1.2. C-01 es de
                                 Familia C y trae vacias Q_m3s, area_ha y
                                 S_cauce (Tablero 3.1); cota_TW y
                                 Q_receptor_m3s vienen vacias en las cuatro.

    ejemplo_puntos_invalido.csv  Le falta UNA columna del encabezado:
                                 'cota_subrasante', la cota contra la que se
                                 chequea V4. NO le falta 'cbr_subrasante',
                                 que si viene y con valor. El caso de la celda
                                 de CBR vacia se cubre sinteticamente en
                                 test_una_celda_de_cbr_vacia_falla_...

La linea que separa este modulo del resto: M0 rechaza lo que es imposible y
carga lo que solo esta incompleto por culpa de un tercero. Los tests que mas
importan son los dos que fijan ese limite -- la fila C-01 se carga marcada, y
la misma celda vacia en una familia A si es un error.
"""

import csv
from pathlib import Path

import pytest

from modelos import (DatoFaltanteError, DatoInvalidoError, Familia,
                     PuntoCritico)
from modulos.M0_carga import COLUMNAS, cargar_puntos
from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING

DIRECTORIO_TESTS = Path(__file__).resolve().parent
CSV_VALIDO = DIRECTORIO_TESTS / "ejemplo_puntos.csv"
CSV_INVALIDO = DIRECTORIO_TESTS / "ejemplo_puntos_invalido.csv"


def _filas_del_ejemplo():
    with CSV_VALIDO.open(encoding="utf-8-sig", newline="") as archivo:
        return [dict(fila) for fila in csv.DictReader(archivo)]


def _escribe(tmp_path, filas, nombre="caso.csv"):
    ruta = tmp_path / nombre
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(COLUMNAS))
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta


def _con(tmp_path, **cambios):
    """CSV de una sola fila, la A-01 del ejemplo, con las celdas cambiadas."""
    fila = _filas_del_ejemplo()[0]
    fila.update(cambios)
    return _escribe(tmp_path, [fila])


# ---------------------------------------------------------------------------
# El CSV de ejemplo completo
# ---------------------------------------------------------------------------

def test_carga_los_cuatro_puntos_del_ejemplo():
    puntos = cargar_puntos(CSV_VALIDO)
    assert len(puntos) == 4
    assert [p.id for p in puntos] == ["A-01", "A-02", "B-01", "C-01"]
    assert all(isinstance(p, PuntoCritico) for p in puntos)


def test_acepta_la_ruta_como_texto():
    assert len(cargar_puntos(str(CSV_VALIDO))) == 4


def test_los_tipos_y_unidades_son_los_de_la_seccion_1_1():
    punto = cargar_puntos(CSV_VALIDO)[0]
    assert punto.familia is Familia.A
    assert isinstance(punto.sucs_fundacion, str) and punto.sucs_fundacion == "SM"
    for campo in ("progresiva_km", "Q_m3s", "area_ha", "S_cauce", "cota_terreno",
                  "cota_rasante", "cota_subrasante", "cbr_subrasante",
                  "esviaje_grados", "ancho_plataforma", "cota_fondo_receptor"):
        assert isinstance(getattr(punto, campo), float), campo


def test_el_caudal_de_A01_es_el_del_caso_patron_CP2():
    """A-01 es el punto con el que se armo CP-2 (D=0.90, y/D=0.75, S=0.005)."""
    punto = cargar_puntos(CSV_VALIDO)[0]
    assert punto.Q_m3s == pytest.approx(
        CP2_GEOMETRIA_MANNING["Q_con_n_max_esperado"],
        abs=CP2_GEOMETRIA_MANNING["tolerancia_hidraulica"])


def test_la_progresiva_se_parte_en_numero_y_notacion_vial():
    puntos = {p.id: p for p in cargar_puntos(CSV_VALIDO)}
    assert puntos["A-01"].progresiva_display == "0+380"
    assert puntos["A-01"].progresiva_km == pytest.approx(0.380)
    assert puntos["A-02"].progresiva_display == "1+920"
    assert puntos["A-02"].progresiva_km == pytest.approx(1.920)
    progresivas = [p.progresiva_km for p in cargar_puntos(CSV_VALIDO)]
    assert all(anterior <= siguiente
               for anterior, siguiente in zip(progresivas, progresivas[1:])), (
        "los puntos se cargan en el orden de progresiva del CSV")


def test_la_progresiva_numerica_se_convierte_a_notacion_vial(tmp_path):
    punto = cargar_puntos(_con(tmp_path, progresiva_km="2.5"))[0]
    assert punto.progresiva_km == pytest.approx(2.5)
    assert punto.progresiva_display == "2+500.00"


# ---------------------------------------------------------------------------
# El limite: incompleto por terceros no es invalido
# ---------------------------------------------------------------------------

def test_la_fila_de_familia_C_se_carga_marcada_y_no_se_rechaza():
    """
    Tablero 3.1: el caudal de C-01 lo fija el canal (ANA / Junta). Sin ese
    dato la fila se carga igual, con los campos en None y anotados.
    """
    c01 = {p.id: p for p in cargar_puntos(CSV_VALIDO)}["C-01"]
    assert c01.familia is Familia.C
    assert c01.Q_m3s is None
    assert c01.area_ha is None
    assert c01.S_cauce is None
    assert c01.pendiente_dato_externo
    assert set(c01.pendientes_externos) == {
        "Q_m3s", "area_ha", "S_cauce", "Q_receptor_m3s", "cota_TW",
        "NF_profundidad_m"}
    # Lo que si trajo la fila esta cargado y validado.
    assert c01.cbr_subrasante == pytest.approx(6.5)
    assert c01.cota_subrasante == pytest.approx(38.95)


def test_el_TW_esta_pendiente_en_todas_las_familias():
    """Tablero 3.1 bloquea el TW de todas las alcantarillas, no solo la C."""
    for punto in cargar_puntos(CSV_VALIDO):
        assert punto.cota_TW is None
        assert punto.Q_receptor_m3s is None
        assert "cota_TW" in punto.pendientes_externos


def test_el_NF_esta_pendiente_en_todas_las_familias(tmp_path):
    """
    El NF de cada cruce lo da el estudio geotecnico, no la hoja de ruta ni el
    proyectista: la columna se carga vacia en las cuatro filas y se marca. No
    se hereda el 1.4 m de la caracterizacion general de la llanura -- ese
    numero describe una zona, no cuatro mediciones.
    """
    for punto in cargar_puntos(CSV_VALIDO):
        assert punto.NF_profundidad_m is None
        assert "NF_profundidad_m" in punto.pendientes_externos
        with pytest.raises(DatoFaltanteError) as exc:
            punto.exigir("NF_profundidad_m")
        assert exc.value.campo == "NF_profundidad_m"


def test_el_NF_declarado_se_carga_como_dato_del_punto(tmp_path):
    """Cuando el estudio lo da, es un dato mas de la fila, no un criterio."""
    punto = cargar_puntos(_con(tmp_path, NF_profundidad_m="1.4"))[0]
    assert punto.NF_profundidad_m == pytest.approx(1.4)
    assert "NF_profundidad_m" not in punto.pendientes_externos


@pytest.mark.parametrize("valor", ["0", "-1.4"])
def test_un_NF_no_positivo_es_dato_invalido(tmp_path, valor):
    """
    El NF es una PROFUNDIDAD bajo el terreno: el signo cambiado es el error de
    transcripcion tipico de esta columna, y es dato invalido (hay que
    corregirlo), no faltante (no hay nada que anadir).
    """
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, NF_profundidad_m=valor))
    assert exc.value.campo == "NF_profundidad_m"


def test_las_familias_A_y_B_no_heredan_la_excepcion_de_la_C(tmp_path):
    """La misma celda vacia que en C-01 es correcta, en una A es un error."""
    with pytest.raises(DatoFaltanteError) as exc:
        cargar_puntos(_con(tmp_path, Q_m3s=""))
    assert exc.value.campo == "Q_m3s"
    assert "Q_m3s" in str(exc.value)
    assert exc.value.id_punto == "A-01"


def test_una_familia_C_completa_no_queda_marcada_por_su_hidrologia(tmp_path):
    """La marca es por dato ausente, no por familia."""
    ruta = _con(tmp_path, familia="C")
    punto = cargar_puntos(ruta)[0]
    assert punto.familia is Familia.C
    assert "Q_m3s" not in punto.pendientes_externos
    assert punto.pendiente_dato_externo          # le siguen faltando TW y Q receptor


# ---------------------------------------------------------------------------
# Estructura del archivo
# ---------------------------------------------------------------------------

def test_el_csv_invalido_falla_nombrando_la_columna_ausente():
    """
    El fixture invalido omite 'cota_subrasante' (la cota contra la que se
    chequea V4), no 'cbr_subrasante', que si viene en su encabezado. Este test
    fija esa identidad: si alguien regenera el fixture cambiando la columna
    omitida, falla aqui y no en un sitio raro tres modulos mas adelante.
    """
    with CSV_INVALIDO.open(encoding="utf-8-sig", newline="") as archivo:
        encabezado = next(csv.reader(archivo))
    assert "cbr_subrasante" in encabezado
    assert "cota_subrasante" not in encabezado

    with pytest.raises(DatoFaltanteError) as exc:
        cargar_puntos(CSV_INVALIDO)
    assert exc.value.campo == "cota_subrasante"
    assert "cota_subrasante" in str(exc.value)


def test_el_error_nombra_toda_columna_que_falte_del_encabezado():
    """Formulado contra el archivo, para que siga valiendo si el fixture cambia."""
    with CSV_INVALIDO.open(encoding="utf-8-sig", newline="") as archivo:
        encabezado = next(csv.reader(archivo))
    faltantes = [c for c in COLUMNAS if c not in encabezado]
    assert faltantes, "el fixture invalido deberia omitir alguna columna"

    with pytest.raises(DatoFaltanteError) as exc:
        cargar_puntos(CSV_INVALIDO)
    for columna in faltantes:
        assert columna in str(exc.value)


@pytest.mark.parametrize("columna", ["id", "progresiva_km", "familia",
                                     "sucs_fundacion"])
def test_una_celda_de_texto_vacia_falla_nombrando_su_columna(tmp_path, columna):
    """
    SIS-F-12. `_texto` tiene dos ramas: la columna que falta del encabezado
    (DatoFaltanteError, cubierta) y la CELDA VACIA, que es la otra mitad de la
    definicion de DatoFaltanteError en CLAUDE.md ("falta la columna entera, o
    la celda obligatoria viene vacia") y que la suite no ejecutaba nunca.

    Es Faltante y no Invalido porque el revisor tiene que AÑADIR el dato, no
    corregirlo: la celda no dice nada equivocado, no dice nada.
    """
    with pytest.raises(DatoFaltanteError) as exc:
        cargar_puntos(_con(tmp_path, **{columna: ""}))
    assert exc.value.campo == columna
    assert "vacia" in str(exc.value)


def test_una_celda_de_texto_con_solo_espacios_es_una_celda_vacia(tmp_path):
    """`_celda` recorta antes de mirar: '   ' no es un id, es una celda vacia."""
    with pytest.raises(DatoFaltanteError) as exc:
        cargar_puntos(_con(tmp_path, id="   "))
    assert exc.value.campo == "id"


def test_una_celda_de_cbr_vacia_falla_nombrando_cbr_subrasante(tmp_path):
    """El CBR define el resguardo de V4 (Sec. 5.1): no admite vacio."""
    with pytest.raises(DatoFaltanteError) as exc:
        cargar_puntos(_con(tmp_path, cbr_subrasante=""))
    assert exc.value.campo == "cbr_subrasante"
    assert "cbr_subrasante" in str(exc.value)


def test_el_error_de_encabezado_avisa_de_las_columnas_no_reconocidas(tmp_path):
    ruta = tmp_path / "mal_escrito.csv"
    encabezado = [c if c != "cbr_subrasante" else "cbr_subrsante" for c in COLUMNAS]
    ruta.write_text(",".join(encabezado) + "\n", encoding="utf-8")

    with pytest.raises(DatoFaltanteError) as exc:
        cargar_puntos(ruta)
    assert "cbr_subrasante" in str(exc.value)
    assert "cbr_subrsante" in str(exc.value)          # la mal escrita, como pista


def test_una_fila_truncada_falla_en_la_primera_columna_que_falta(tmp_path):
    ruta = tmp_path / "truncado.csv"
    ruta.write_text(",".join(COLUMNAS) + "\nA-01,0+380,A\n", encoding="utf-8")
    with pytest.raises(DatoFaltanteError) as exc:
        cargar_puntos(ruta)
    assert exc.value.campo == "Q_m3s"


def test_una_fila_con_celdas_de_mas_no_pasa_en_silencio(tmp_path):
    fila = _filas_del_ejemplo()[0]
    ruta = tmp_path / "sobrante.csv"
    ruta.write_text(
        ",".join(COLUMNAS) + "\n" +
        ",".join(fila[c] for c in COLUMNAS) + ",sobra\n",
        encoding="utf-8")
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(ruta)
    assert "sobra" in str(exc.value)


def test_un_csv_sin_filas_de_datos_falla(tmp_path):
    ruta = tmp_path / "solo_encabezado.csv"
    ruta.write_text(",".join(COLUMNAS) + "\n", encoding="utf-8")
    with pytest.raises(DatoFaltanteError):
        cargar_puntos(ruta)


def test_un_csv_vacio_falla(tmp_path):
    ruta = tmp_path / "vacio.csv"
    ruta.write_text("", encoding="utf-8")
    with pytest.raises(DatoFaltanteError):
        cargar_puntos(ruta)


def test_un_archivo_que_no_existe_no_es_un_error_del_expediente(tmp_path):
    with pytest.raises(FileNotFoundError):
        cargar_puntos(tmp_path / "no_existe.csv")


def test_dos_puntos_no_pueden_llamarse_igual(tmp_path):
    filas = _filas_del_ejemplo()[:2]
    filas[1]["id"] = filas[0]["id"]
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_escribe(tmp_path, filas))
    assert exc.value.campo == "id"


# ---------------------------------------------------------------------------
# Tipos y rangos por columna
# ---------------------------------------------------------------------------

def test_un_valor_no_numerico_falla_nombrando_su_columna(tmp_path):
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, cota_rasante="cuarenta y cuatro"))
    assert exc.value.campo == "cota_rasante"
    assert "cuarenta y cuatro" in str(exc.value)


@pytest.mark.parametrize("columna, valor", [
    ("cbr_subrasante", "0"),        # una proporcion nula no es un suelo
    ("cbr_subrasante", "-3"),
    ("cbr_subrasante", "250"),      # fuera de la escala del CBR
    ("Q_m3s", "0"),
    ("Q_m3s", "-1.2"),
    ("area_ha", "-850"),
    ("S_cauce", "0"),
    ("S_cauce", "6"),               # llego en porcentaje, no en m/m
    ("esviaje_grados", "-5"),
    ("esviaje_grados", "90"),       # el conducto seria paralelo a la via
    ("ancho_plataforma", "0"),
    ("progresiva_km", "0+1200"),    # los metros no llegan a 1000
    ("progresiva_km", "0+380+2"),
])
def test_los_valores_fuera_del_rango_fisico_se_rechazan(tmp_path, columna, valor):
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, **{columna: valor}))
    assert exc.value.campo == columna


@pytest.mark.parametrize("columna", [
    "Q_m3s", "area_ha", "cbr_subrasante", "ancho_plataforma",
    "cota_rasante", "cota_terreno", "cota_subrasante", "cota_fondo_receptor",
])
@pytest.mark.parametrize("texto", ["inf", "Infinity", "-inf", "nan", "NaN"])
def test_ningun_dato_no_finito_entra_al_pipeline(tmp_path, columna, texto):
    """
    MAT-D14. `float()` acepta 'inf' y 'nan' como literales, y ninguna
    validacion de rango los atrapa: `inf > 0` es cierto, y `nan` es falso
    frente a `<=` y frente a `>=` a la vez, de modo que pasa tanto una
    validacion escrita como "esta dentro" como una escrita como "no esta
    fuera". El dato recorria el pipeline entero y salia por el otro extremo
    como una memoria con numeros que no son numeros.

    Es DatoInvalidoError y no DatoFaltanteError: la celda ESTA, y el revisor
    tiene que CORREGIRLA, no añadirla.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, **{columna: texto}))
    assert exc.value.campo == columna
    assert "finito" in str(exc.value)


def test_el_infinito_pasaba_todas_las_cotas_inferiores(tmp_path):
    """
    El caso concreto de la ficha: Q_m3s = 'inf' pasa `Q_m3s > 0` y produce un
    diagnostico falso. Este test fija que la guarda de finitud corre ANTES de
    la de rango, y que el mensaje no habla de un caudal negativo.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, Q_m3s="inf"))
    assert exc.value.campo == "Q_m3s"
    assert "finito" in str(exc.value)
    assert "positivo" not in str(exc.value), (
        "la guarda que atrapa a inf tiene que ser la de finitud, no la de rango")


def test_la_progresiva_no_finita_tambien_se_rechaza(tmp_path):
    """La progresiva pasa por el mismo conversor, en sus dos formas."""
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, progresiva_km="inf"))
    assert exc.value.campo == "progresiva_km"


def test_el_esviaje_perpendicular_es_valido(tmp_path):
    """B-01 cruza a 0 grados: el limite inferior del rango es admisible."""
    punto = cargar_puntos(_con(tmp_path, esviaje_grados="0"))[0]
    assert punto.esviaje_grados == pytest.approx(0.0)


def test_una_familia_desconocida_se_rechaza(tmp_path):
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, familia="D"))
    assert exc.value.campo == "familia"
    assert "A, B, C" in str(exc.value)


# ---------------------------------------------------------------------------
# Validaciones cruzadas (Sec. 1.5)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cota_subrasante", ["44.20", "44.55"])
def test_la_subrasante_no_puede_alcanzar_la_rasante(tmp_path, cota_subrasante):
    """Sec. 1.5: subrasante = rasante - espesor del paquete estructural."""
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, cota_subrasante=cota_subrasante))
    assert exc.value.campo == "cota_subrasante"
    assert "paquete estructural" in str(exc.value)


def test_sin_altura_de_terraplen_el_diametro_implicito_es_imposible(tmp_path):
    """La subrasante bajo el terreno natural no deja sitio para el conducto."""
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, cota_terreno="44.10"))
    assert "diametro implicito" in str(exc.value)


def test_un_terraplen_bajo_pero_posible_lo_decide_M7_y_no_M0(tmp_path):
    """
    0.40 m entre terreno y subrasante no alcanzan para el diametro minimo de
    0.90 m, pero eso lo resuelve el tamizado de 7.A con su delta de rasante.
    M0 solo rechaza lo imposible, no lo ajustado.
    """
    punto = cargar_puntos(_con(tmp_path, cota_terreno="43.65"))[0]
    assert punto.cota_subrasante - punto.cota_terreno == pytest.approx(0.40)


def test_el_receptor_no_puede_estar_sobre_el_terreno_del_cruce(tmp_path):
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, cota_fondo_receptor="42.50"))
    assert exc.value.campo == "cota_fondo_receptor"
    assert "gravedad" in str(exc.value)


def test_el_TW_no_puede_quedar_bajo_el_fondo_del_receptor(tmp_path):
    """Sec. 1.5: el TW es el nivel EN EL RECEPTOR durante la avenida."""
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, cota_TW="41.00"))   # fondo receptor: 41.30
    assert exc.value.campo == "cota_TW"


def test_un_TW_por_encima_del_fondo_se_carga_y_deja_de_estar_pendiente(tmp_path):
    punto = cargar_puntos(_con(tmp_path, cota_TW="41.80"))[0]
    assert punto.cota_TW == pytest.approx(41.80)
    assert "cota_TW" not in punto.pendientes_externos
    assert punto.exigir("cota_TW") == pytest.approx(41.80)
