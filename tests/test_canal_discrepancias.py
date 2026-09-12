"""
El CANAL de las discrepancias a la memoria (C8, punto 1).

POR QUE EXISTE ESTE ARCHIVO. El registro de discrepancias llevaba desde S13
enumerando lo que `CLAUDE.md` obliga a declarar cuando dos fuentes dicen cosas
distintas, y `Registro.discrepancias_abiertas` afirmaba en su docstring que
«M11 las imprime». No las imprimia: M11 no importaba el modulo por ninguna
parte. Medido antes de C8, de las 23 declaradas llegaban DOS a la memoria, y
las dos por accidente --- porque alguien habia escrito el id a mano dentro de
la justificacion de un criterio o de la nota de una cita, y M11 imprime esos
campos tal cual. O sea: un id suelto dentro de un parrafo, sin partes, sin
quien gana y sin efecto.

Las dos lecciones que este archivo fija, y las dos costaron auditorias:

    una declaracion en un docstring no imprime nada;
    una discrepancia registrada donde nadie la lee esta tan registrada como
    no registrada.

QUE SE VIGILA. No que "lleguen todas" --- eso seria volcar el registro, y el
manifiesto es para quien audita el codigo mientras la memoria es para quien
sustenta ---, sino las dos mitades del filtro: que llegue lo VIVO que la
corrida TOCA, y que no llegue lo demas.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import criterios_adoptados as ca                                   # noqa: E402
from cli import cargar_datos_externos, correr                      # noqa: E402
from modelos import Magnitud, paso                                 # noqa: E402
from modulos import M11_reporte as M11                             # noqa: E402
from normativa.esquema import EstadoDiscrepancia                   # noqa: E402
from normativa.registro import construir                           # noqa: E402

CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"

# El censo de C8, medido: nueve `Parte.cita_id` anunciaban una cita que nadie
# transcribio. Es TRINQUETE --- solo puede decrecer ---, igual que
# `cuenta_por_transcribir` (T22) y que las anclas por mencion de R-17.
# T2 lo dejo en CERO: siete de las nueve se transcribieron (cuatro del Manual
# de Puentes, AASHTO 11.6.3.3, AASHTO M 170M Tablas 1-5, y la ec. 4b de la
# copia HDS-5 de 1985 --- esta ultima SIN firma, por el invariante T6; su
# comentario en citas.py dice por que ---) y dos se RE-ANCLARON a la cita que
# ya sostenia la afirmacion bajo otro id (`ASTM_A760.T1` y
# `AASHTO_LRFD_9.3.11.6.4`): duplicarlas habria violado la regla de la
# transcripcion unica.
PARTES_SIN_CITA_TRANSCRITA = 0


@pytest.fixture(scope="module")
def reg():
    return construir()


# Los criterios del cajon que la corrida del entregable declara. Son los
# mismos que `--declarar` pasa por la CLI, y sin ellos C-01 no dimensiona: el
# canal se comprobaria sobre una memoria en la que ningun punto llego a la
# Fase 5, que es justamente donde viven las discrepancias que mas importan.
DECLARACIONES_DEL_CAJON = {
    "embocadura_cajon": "cajon_concreto_aletas_30_75",
    "n_manning_cajon": "concreto_afinado",
    "secciones_cajon_normalizadas": [[1.20, 0.90], [1.50, 1.20], [2.00, 1.50]],
    "n_celdas_cajon": 1,
    "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
    "espesor_pared_cajon": 0.20,
    "cobertura_minima_cajon": 0.3048,
}


@pytest.fixture(scope="module")
def informe():
    """
    LA CORRIDA DEL ENTREGABLE DE C8, en perfil y con C-01 dimensionado.

    No vale el CSV pelado: en el, ningun punto pasa de V5 --- falta
    `ancho_derecho_via_m` --- y ni V7 ni la cobertura minima llegan a emitir
    paso, de modo que las discrepancias que tocan un valor de la Fase 5 y de
    la 7 no tendrian por donde aparecer. Comprobar el canal sobre esa corrida
    daria un verde que no dice nada.
    """
    # EL REGISTRO DE USOS ES DE PROCESO, y en una suite eso significa que
    # llega contaminado por las corridas de otros modulos de test: `F_pga` lo
    # marca usado cualquier corrida de expediente, y con el entraria
    # `DIS-HR-30M-VS-100FT` en un bloque de PERFIL, que es justo lo que el
    # filtro tiene que impedir. En produccion no pasa --- una corrida por
    # proceso --- pero aqui hay que partir de cero o el test comprueba la
    # suma de todas las corridas de la sesion, no la suya.
    ca._USADOS.clear()
    for clave, valor in DECLARACIONES_DEL_CAJON.items():
        ca.establecer_valor_dinamico(clave, valor)
    try:
        externos = cargar_datos_externos(
            None, {"luz_m": 2.75, "TW_m": 0.3, "longitud_m": None,
                   "L_hidraulico_m": None, "categoria_tr": None,
                   "Q_m3s": 0.85, "S_cauce": 0.006})
        yield correr(CSV_EJEMPLO, externos, alcance="perfil")
    finally:
        for clave in DECLARACIONES_DEL_CAJON:
            ca.quitar_valor_dinamico(clave)


@pytest.fixture(scope="module")
def memoria(informe):
    return M11.memoria_html(informe, proyecto="prueba del canal")


# ===========================================================================
# El filtro: que llega y que no
# ===========================================================================

def test_lo_resuelto_no_llega_a_la_memoria(reg):
    """
    La mitad menos obvia del filtro, y la que hace trabajo de verdad.

    `DIS-CN-EG-508-07` esta RESUELTA --- el repositorio cito la pagina impresa
    982 y despues la 984, y se quedo con la verificada --- y su cita
    `EG2013.508.07#RELLENO_MIN` SI se imprime en la memoria de todos los
    puntos: es la del relleno minimo del HDPE. Por el indice de citas llegaria
    sola. No llega, y es correcto: quien abra hoy esa pagina encuentra lo que
    la memoria dice, de modo que no hay nada que defender en una sustentacion.
    Eso es del manifiesto, que es para quien audita el codigo.
    """
    resuelta = reg.discrepancia("DIS-CN-EG-508-07")
    assert resuelta.estado is EstadoDiscrepancia.RESUELTA
    assert not resuelta.viva

    tocadas = reg.discrepancias_que_tocan({"EG2013.508.07#RELLENO_MIN"})
    assert resuelta not in tocadas, (
        "una discrepancia resuelta llego a la memoria: el filtro de "
        "`EstadoDiscrepancia.viva` dejo de aplicarse")


def test_una_errata_de_imprenta_SI_llega(reg):
    """
    La otra mitad menos obvia, en el sentido contrario. Una errata de
    imprenta no esta "resuelta": el PDF sigue imprimiendo lo que imprime.

    `DIS-MCHHD-T09-A2-DESPLAZADA` es el caso que lo prueba con un numero: el
    revisor que abra la pag. impresa 75 y lea la Tabla N 09 al pie de la letra
    obtiene `n = (0.011, 0.014)` donde la memoria uso `(0.010, 0.013)` --- un
    +10 % en el n que gobierna V3 y la socavacion. Si la memoria no lo declara
    antes, el revisor lo descubre solo, leyendo el PDF, y concluye que el
    calculo esta mal.
    """
    errata = reg.discrepancia("DIS-MCHHD-T09-A2-DESPLAZADA")
    assert errata.estado is EstadoDiscrepancia.ERRATA_DE_IMPRENTA
    assert errata.viva
    assert errata in reg.discrepancias_que_tocan({"MC_HHD.4.1.1.3.6#T09"})


def test_lo_que_la_corrida_no_toca_no_se_vuelca(reg, informe, memoria):
    """
    NO SE VUELCA EL REGISTRO. De las diez discrepancias abiertas, seis son del
    cabezal --- clase de sitio, licuefaccion, h_eq, ciclopeo --- y una corrida
    de perfil difiere el cabezal entero: su memoria no afirma nada sobre
    ellas, y publicarlas seria pedirle al lector que sostenga lo que este
    documento no dice.
    """
    abiertas = {d.id for d in reg.discrepancias_abiertas()}
    assert len(abiertas) >= 10, "cambio el censo de abiertas: revisa el test"

    del_cabezal = {"DIS-HR-CLASE-DE-SITIO-F", "DIS-HR-30M-VS-100FT",
                   "DIS-HR-VIA-DE-LA-LICUEFACCION", "DIS-HR-H-EQ",
                   "DIS-HR-CICLOPEO"}
    assert informe.alcance == "perfil"
    assert del_cabezal <= abiertas
    bloque = M11.bloque_discrepancias(informe)
    for id_ in del_cabezal:
        assert id_ not in bloque, (
            f"{id_} es del cabezal y el cabezal esta diferido en esta corrida")


# ===========================================================================
# Las tres vias de llegada
# ===========================================================================

def test_la_via_de_la_cita_no_necesita_que_nadie_la_cablee(reg):
    """
    VIA 1, y es la que no se puede desincronizar: el indice inverso sale de
    las `Parte.cita_id` que la discrepancia YA declara. Nadie mantiene una
    segunda lista.
    """
    d = reg.discrepancia("DIS-HR-H-RELLENO-MIN")
    assert "AASHTO_LRFD_9.12.6.6.3#COBERTURA" in d.citas
    assert d in reg.discrepancias_de_cita("AASHTO_LRFD_9.12.6.6.3#COBERTURA")
    assert d in reg.discrepancias_que_tocan(
        {"AASHTO_LRFD_9.12.6.6.3#COBERTURA"})


def test_la_via_del_paso_existe_porque_la_cita_falla_por_un_sufijo(reg):
    """
    VIA 2, con el caso exacto que la obliga a existir.

    `DIS-HR-G-LAUSHEY` habla de `MC_HHD.4.1.1.3.7c#G` --- el ancla del SIMBOLO
    g dentro del numeral --- y el paso de Laushey cita `MC_HHD.4.1.1.3.7c`, el
    numeral. Es el mismo sitio del documento con dos ids: por la via de la
    cita, la discrepancia pasa de largo por un sufijo. Por eso el paso la
    nombra.
    """
    d = reg.discrepancia("DIS-HR-G-LAUSHEY")
    assert d.citas == ("MC_HHD.4.1.1.3.7c#G",)
    assert d not in reg.discrepancias_que_tocan({"MC_HHD.4.1.1.3.7c"}), (
        "si el cruce por cita empezara a alcanzarla, esta via sobra y hay que "
        "retirarla en vez de dejar dos caminos al mismo sitio")
    assert d in reg.discrepancias_que_tocan((), {"DIS-HR-G-LAUSHEY"})


def test_la_via_del_criterio_existe_porque_V9_no_emite_paso(reg):
    """
    VIA 3, tambien con su caso.

    `DIS-HR-D-MAX` dice que los topes de 2.70 / 2.10 / 1.50 m no son
    normativos sino de catalogo. Quien los lleva es `criterios_adoptados`, y
    quien los consume es V9 --- que devuelve una `Verificacion` sin paso ---.
    Sin esta via, el hallazgo no tiene por donde llegar.
    """
    assert ca.CRITERIOS["D_max_catalogo"].discrepancias == ("DIS-HR-D-MAX",)
    d = reg.discrepancia("DIS-HR-D-MAX")
    assert d in reg.discrepancias_que_tocan((), {"DIS-HR-D-MAX"})


def test_las_tres_llegan_al_HTML(memoria):
    """
    Sobre el PRODUCTO y no sobre los objetos, que es la unica forma de
    comprobar lo que este archivo dice. Las tres que el brief de C8 nombra por
    tocar un valor que la corrida usa, mas la que la auditoria de C7 abrio.
    """
    for id_ in ("DIS-HR-D-MAX", "DIS-HR-H-RELLENO-MIN", "DIS-HR-G-LAUSHEY",
                "DIS-AASHTO-GAMMA-EV-12.6.1"):
        assert id_ in memoria, f"{id_} no llega a la memoria generada"


def test_la_memoria_publica_los_cuatro_campos_y_no_solo_el_id(memoria, reg):
    """
    El defecto que se cierra no era solo "no llegan": era que las dos que
    llegaban lo hacian como un codigo dentro de un parrafo. Una discrepancia
    sin sus partes, sin quien gana y sin el efecto de seguir a la otra no se
    puede sustentar --- es una sigla.
    """
    d = reg.discrepancia("DIS-AASHTO-GAMMA-EV-12.6.1")
    assert d.objeto[:40] in memoria
    assert "Cual gana, y por que" in memoria
    assert "Que pasaria siguiendo a la otra" in memoria
    # El efecto medido de esta, que es lo que la hace importar: seguir la otra
    # parte ABLANDA la verificacion, que es la direccion insegura.
    assert "34.884" in memoria


def test_la_discrepancia_va_como_interpretacion_y_no_como_fuente(memoria):
    """
    NOR-HID-04. Una discrepancia es lo que el proyecto LEE cuando dos fuentes
    dicen cosas distintas: presentarla con `class="fuente"` seria dar por
    norma una eleccion entre normas.
    """
    for marca in ('<h4><code>DIS-', 'class="acotacion interpretacion"'):
        assert marca in memoria
    inicio = memoria.index("DIS-AASHTO-GAMMA-EV-12.6.1")
    bloque = memoria[inicio - 400:inicio + 400]
    assert 'class="fuente"' not in bloque


# ===========================================================================
# Las guardias del canal
# ===========================================================================

def test_un_paso_no_puede_declarar_una_discrepancia_inexistente():
    with pytest.raises(KeyError):
        paso("F6.LAUSHEY", que="x", formula="f", sustitucion=(),
             resultado=Magnitud("a", 1.0, "m", "de algun sitio"),
             discrepancias=("DIS-QUE-NO-EXISTE",))


def test_un_paso_no_puede_declarar_una_discrepancia_resuelta():
    """
    La guardia que impide reabrir por la puerta de atras lo que el filtro
    cierra por delante: si una discrepancia se resuelve, el paso que la
    nombraba tiene que enterarse en el acto y no seguir publicandola.
    """
    with pytest.raises(ValueError) as exc:
        paso("F6.LAUSHEY", que="x", formula="f", sustitucion=(),
             resultado=Magnitud("a", 1.0, "m", "de algun sitio"),
             discrepancias=("DIS-CN-EG-508-07",))
    assert "manifiesto" in str(exc.value)


def test_un_criterio_no_puede_declarar_una_discrepancia_inexistente():
    import dataclasses
    from criterios_adoptados import _verificar_criterio

    c = dataclasses.replace(ca.CRITERIOS["D_max_catalogo"],
                            discrepancias=("DIS-QUE-NO-EXISTE",))
    with pytest.raises(ValueError) as exc:
        _verificar_criterio("D_max_catalogo", c)
    assert "no esta en el registro" in str(exc.value)


# ===========================================================================
# El censo de anclas rotas que abrir el canal destapo
# ===========================================================================

def test_el_censo_de_partes_sin_cita_transcrita_solo_decrece(reg):
    """
    NUEVE de las 38 `Parte.cita_id` del registro anuncian una cita que nadie
    transcribio. El campo se documenta como «ancla al registro» y en nueve
    casos no ancla en nada.

    POR QUE NADIE LO NOTO: la validacion del registro mete estos ids en el
    conjunto de «referenciadas» --- para que una cita no cuente como huerfana
    --- y nunca comprobo que existieran. Un id que solo sirve para excusar a
    otro de estar huerfano no se comprueba jamas. Se destapo al darles el
    primer consumidor de verdad.

    NO SE CIERRA INVENTANDO NUEVE CITAS (regla 8 de `CLAUDE.md`): transcribir
    una es leer el PDF y verificar numeral, pagina impresa y texto literal.
    Queda como trinquete, que es lo que este proyecto hace con toda migracion
    a medias: visible y decreciente.
    """
    faltan = reg.partes_sin_cita_transcrita()
    assert len(faltan) <= PARTES_SIN_CITA_TRANSCRITA, (
        f"el censo crecio a {len(faltan)}: una discrepancia nueva anuncia una "
        f"cita que no esta transcrita. {faltan}")
    if len(faltan) < PARTES_SIN_CITA_TRANSCRITA:
        pytest.fail(
            f"bajo a {len(faltan)}: baja la constante "
            "PARTES_SIN_CITA_TRANSCRITA en el mismo commit, o el trinquete "
            "deja de apretar")


def test_la_memoria_ya_no_avisa_de_partes_sin_cita_transcrita(memoria):
    """
    El censo llego a cero en T2 y el aviso desaparece CON el: mientras hubo
    partes sin transcribir, la memoria decia en el sitio el id anunciado y
    que la transcripcion faltaba (imprimir el id pelado mandaria al revisor a
    buscar en el registro algo que no esta). El mecanismo de M11 sigue vivo
    para la proxima parte que se declare sin cita; lo que este test fija es
    que hoy no queda ninguna que lo dispare, y que el ancla re-anclada de
    DIS-HR-D-MAX imprime la cita real en su lugar.
    """
    assert "cita anunciada y NO transcrita al registro" not in memoria
    assert "ASTM_A760.T1#DIAMETROS" not in memoria


def test_la_discrepancia_llega_por_la_cita_del_FUNDAMENTO(informe, memoria, reg):
    """
    LO QUE LA AUDITORIA ADVERSARIAL REFUTO, fijado para que no vuelva.

    Un `PasoDeMemoria` carga numerales por CUATRO puertas y el canal leia una
    --- `citas_textuales` ---. La memoria de C-01 nombra la **Tabla A.1 del
    HDS-5 cinco veces**: es de donde salen K, M, c, Y y Ks del control de
    entrada, que producen el UNICO HW que C-01 publica (0.589 m, el
    gobernante). Y la discrepancia sobre el TITULO de esa tabla ---
    `DIS-HDS5-APENDICE-G`, que remite a un «Appendix G» que la 3.a edicion no
    tiene --- no llegaba: la cita entra al paso por el `Fundamento`
    `F4.FORMA_HDS5`, no por sus comillas.

    El criterio, dicho de una vez: llega la discrepancia sobre un numeral en
    el que la memoria APOYA algo, no solo sobre el que ENTRECOMILLA.
    """
    d = reg.discrepancia("DIS-HDS5-APENDICE-G")
    assert d.viva
    assert "HDS5_3ED.TA.1" in d.citas

    pasos = M11.pasos_del_informe(informe)
    por_comillas = {c for p in pasos for c in p.citas_textuales}
    por_las_cuatro = set().union(*(M11.citas_en_que_descansa(p) for p in pasos))
    assert "HDS5_3ED.TA.1" not in por_comillas, (
        "si la Tabla A.1 pasara a entrecomillarse, este test deja de probar "
        "lo que dice: revisar el supuesto antes de tocarlo")
    assert "HDS5_3ED.TA.1" in por_las_cuatro
    assert "DIS-HDS5-APENDICE-G" in memoria

    # Y el hueco no se cierra de mas: leer las cuatro puertas anade ESA y
    # ninguna de las etapas que `--alcance perfil` difiere.
    solo_comillas = {x.id for x in reg.discrepancias_que_tocan(por_comillas)}
    las_cuatro = {x.id for x in reg.discrepancias_que_tocan(por_las_cuatro)}
    assert las_cuatro - solo_comillas == {"DIS-HDS5-APENDICE-G"}


def test_ningun_id_de_discrepancia_queda_suelto_en_la_memoria(memoria):
    """
    EL DEFECTO QUE C8 DIJO CERRAR, SOBREVIVIENDO POR UN CAMPO DE TEXTO.

    La memoria imprimia el id `DIS-HR-30M-VS-100FT` dentro de la prosa del
    campo `resolucion` de 'clase_sitio' --- que el bloque de criterios sin
    valor publica tal cual ---, y el filtro excluia la discrepancia CON RAZON,
    porque esta corrida no invoca ese criterio. Resultado: una sigla que el
    lector no puede resolver en el documento, que es exactamente «un id suelto
    dentro de un parrafo».

    La regla que fija este test: si un id aparece en la memoria, tiene que
    tener su bloque. Un id se escribe en el campo `discrepancias`, nunca en
    prosa.
    """
    import re

    todos = set(re.findall(r"DIS-[A-Z0-9.\-]+", memoria))
    con_bloque = set(re.findall(r"<code>(DIS-[A-Z0-9.\-]+)</code>", memoria))
    sueltos = todos - con_bloque
    assert not sueltos, (
        f"ids de discrepancia sin bloque que los resuelva: {sorted(sueltos)}. "
        "Un id en prosa no es un canal: se declara en `Criterio.discrepancias` "
        "o en `PasoDeMemoria.discrepancias`")


def test_lo_que_el_bloque_entrecomilla_sale_del_registro(memoria, reg):
    """
    LA REGLA DE LAS SEGUNDAS TRANSCRIPCIONES, aplicada al canal nuevo.

    `Parte.que_dice` es PROSA A MANO, y varias partes citan dentro de ella la
    frase de su fuente. Eso es exactamente lo que la §4.5 llama una segunda
    transcripcion: dos copias del mismo texto que divergen sin que nada avise
    --- de las seis que habia, dos ya divergian ---. Al abrir el canal, esa
    prosa pasa a imprimirse en la memoria, de modo que la regla ahora la
    alcanza.

    Se comprueba sobre ESTA corrida y no solo sobre la del CSV pelado: son
    memorias con discrepancias distintas, y el hueco estaria justo en las que
    una no toca.
    """
    import html as _html
    import re

    normalizados = {" ".join(t.split()) for t in reg.textos_literales()}
    fuera = []
    for bruto in re.findall(r"&laquo;(.+?)&raquo;", memoria, re.S):
        texto = " ".join(re.sub(r"<[^>]+>", "", _html.unescape(bruto)).split())
        if texto in normalizados:
            continue
        # Recortada por el ancho, o dentro de un parrafo mayor: la inclusion
        # en los dos sentidos sigue atando el texto a un original verificado.
        if any(texto in t or t in texto for t in normalizados):
            continue
        fuera.append(texto[:160])
    assert not fuera, (
        "la memoria del entregable entrecomilla como literal texto que el "
        "registro no sostiene:\n  " + "\n  ".join(fuera))


# ===========================================================================
# El recorrido de pasos, que ahora tiene dos copias
# ===========================================================================

def test_los_dos_recorridos_de_pasos_ven_lo_mismo(informe):
    """
    `M11.pasos_del_informe` y `test_memoria_sustentada._pasos_de` hacen el
    mismo recorrido, y el segundo NO se borro a cambio del primero: un test
    que consuma la funcion que audita deja de auditarla. Lo que hay es este
    test, que los compara --- si uno se olvida de una rama nueva del informe,
    el otro lo dice.
    """
    from test_memoria_sustentada import _pasos_de

    de_M11 = M11.pasos_del_informe(informe)
    del_test = _pasos_de(informe)
    assert len(de_M11) == len(del_test)
    assert {id(p) for p in de_M11} == {id(p) for p in del_test}
