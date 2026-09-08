"""
tests/test_nivel_medido.py
==========================
`Criterio.nivel`, contrastado contra CORRIDAS REALES y en LAS DOS DIRECCIONES.

Por que existe, cuando ya habia un test de nivel
------------------------------------------------
`tests/test_cierre_perfil.py::test_todo_criterio_que_la_corrida_de_perfil_invoca_esta_clasificado`
comprueba UNA direccion: si la corrida de perfil lo invoca sin diferirlo,
tiene que ser de perfil. Esa mitad basta para lo que aquel test persigue --- el
criterio de salida del nivel de perfil --- y NO basta para lo que este campo
gobierna desde S21: el filtro de alcance de la pestana de criterios.

La razon es exacta. En una sola direccion, marcar un criterio como
`expediente` no lo comprueba NADIE: si la corrida de perfil no lo invoca, el
test calla, y da igual que la clasificacion sea cierta o que alguien la haya
escrito de mas para quitarse una fila de encima. Un filtro montado sobre eso
es otra vez una lista que alguien mantiene a mano --- solo que escrita campo a
campo en vez de en un archivo aparte, que es peor porque no se ve como lista.

Las dos direcciones, entonces:

    marcado PERFIL       ->  la corrida de perfil TIENE que invocarlo
    marcado EXPEDIENTE   ->  la corrida de perfil NO puede invocarlo

Y las tres corridas
-------------------
Son tres y no dos, y la tercera no es un lujo: un criterio `opcional=True` se
lee con `valor_si_declarado()`, que NO registra el uso mientras el criterio
siga vacio (ver su docstring). Los dos opcionales del archivo son por eso
invisibles a las dos corridas normales, y sin la tercera su nivel seria una
afirmacion sin medir. La tercera los declara en caliente con el valor que su
consumidor ya aplicaba por defecto --- no mueve ningun resultado --- y mide si
la corrida de perfil los invoca.

Lo que este test NO puede medir, dicho en vez de disimulado
-----------------------------------------------------------
Hay criterios que NINGUNA de las tres corridas invoca, y no por un descuido:
o no los consume ningun modulo (`sin_consumidor`), o su cadena se detiene
antes en un criterio pendiente --- la Fase 9 entera esta en ese caso ---. Para
esos, medir es imposible y decir "medido" seria mentir. Se comprueban por la
UNICA via que queda, que es el censo de `variables_entrada`: un criterio de
expediente no puede tener ningun consumidor que la corrida de perfil ejecute.
Es mas debil que una medicion, y por eso esta separado en su propio test y
dicho aqui.

Y queda un grupo al que NI SIQUIERA eso alcanza: los OCHO sin ningun
consumidor. De esos, el nivel es un argumento escrito junto al campo y no una
medida, y estan censados en `SIN_CONSUMIDOR_Y_SIN_MEDIDA` para que el grupo no
crezca en silencio. Ese limite no se dedujo leyendo el test: se midio POR
MUTACION --- cambiando el nivel de cinco de los trece de S21 y mirando cual
sobrevivia ---, y el superviviente fue justamente uno de esos ocho.
"""

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import cli                                                        # noqa: E402
import criterios_adoptados as ca                                  # noqa: E402
import variables_entrada as ve                                    # noqa: E402

CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"

# Los mismos datos externos que `test_cierre_perfil`: es el corredor con todo
# lo que el nivel de perfil SI tiene, y el unico CSV con el que la corrida
# llega hasta la Fase 5. Se repiten aqui en vez de importarse porque aquel
# modulo los usa dentro de una fixture que ademas guarda la foto del registro;
# lo que se comparte es el archivo, que es el dato.
EXTERNOS_GLOBALES = dict(luz_m=3.0, L_hidraulico_m=120.0, TW_m=None,
                         longitud_m=None, categoria_tr=None)
EXTERNOS_POR_PUNTO = {"C-01": {"Q_m3s": 0.65, "S_conducto": 0.004}}

# Los dos opcionales, con el valor que su consumidor YA aplica por defecto.
# No es una declaracion de proyecto: es el instrumento de medida, y esta
# elegido para no mover nada. `v_max_concreto_eleccion` = 6.0 es el maximo de
# la fila de concreto de la Tabla N 10, que es lo que rige sin declarar; el
# riesgo del Propietario repite los maximos recomendados de la Tabla N 02 para
# la fila que esta corrida usa.
OPCIONALES_PARA_MEDIR = {
    "v_max_concreto_eleccion": 6.0,
    "riesgo_admisible_propietario": {"quebrada_importante": {"R": 0.30, "n": 25}},
}


def _correr(alcance, opcionales=None):
    """
    Una corrida limpia, con la foto del registro de usos acotada a ella.

    `criterios_adoptados` acumula los usos en un registro global --- que es lo
    correcto para la memoria, que imprime lo que la corrida entera consumio ---
    y en una suite ese registro lleva ademas lo que invocaron los tests
    anteriores. Aqui se mide ESTA corrida, asi que se vacia, se corre, se lee y
    se devuelve la union para no dejar sin sus usos a lo que venga despues.
    """
    externos = cli.cargar_datos_externos(None, EXTERNOS_GLOBALES)
    for id_punto, datos in EXTERNOS_POR_PUNTO.items():
        externos.por_punto.setdefault(id_punto, {}).update(
            {clave: cli.DatoDeclarado(clave, valor, "datos del expediente")
             for clave, valor in datos.items()})
    previos = set(ca._USADOS)
    ca._USADOS.clear()
    try:
        for clave, valor in (opcionales or {}).items():
            ca.establecer_valor_dinamico(clave, valor)
        cli.correr(CSV_PERFIL, externos, alcance=alcance)
        return {c for c in ca._USADOS if c in ca.CRITERIOS}
    finally:
        for clave in (opcionales or {}):
            ca.quitar_valor_dinamico(clave)
        ca._USADOS.update(previos)


@pytest.fixture(scope="module")
def usados_perfil():
    return _correr(cli.ALCANCE_PERFIL)


@pytest.fixture(scope="module")
def usados_expediente():
    return _correr(cli.ALCANCE_EXPEDIENTE)


@pytest.fixture(scope="module")
def usados_perfil_con_opcionales():
    return _correr(cli.ALCANCE_PERFIL, OPCIONALES_PARA_MEDIR)


@pytest.fixture(scope="module")
def diferidos_perfil():
    """
    Los criterios cuya etapa la corrida de perfil DECLARO diferida.

    No se afirma cuales son: se leen de los bloqueos que la propia corrida
    marco `diferido_por_alcance`. Son V5 y V8, que a perfil se INTENTAN y cuyo
    fallo se difiere; sus criterios se invocan y no bloquean.
    """
    externos = cli.cargar_datos_externos(None, EXTERNOS_GLOBALES)
    for id_punto, datos in EXTERNOS_POR_PUNTO.items():
        externos.por_punto.setdefault(id_punto, {}).update(
            {clave: cli.DatoDeclarado(clave, valor, "datos del expediente")
             for clave, valor in datos.items()})
    informe = cli.correr(CSV_PERFIL, externos, alcance=cli.ALCANCE_PERFIL)
    return {b.criterio for _id, b in informe.diferidos() if b.criterio}


# ===========================================================================
# Las dos direcciones
# ===========================================================================

def test_todo_criterio_marcado_de_perfil_lo_invoca_la_corrida_de_perfil(
        usados_perfil, usados_expediente, usados_perfil_con_opcionales):
    """
    Primera direccion: si dice perfil, la corrida de perfil lo tiene que tocar.

    EL UNIVERSO ES LO QUE ALGUNA CORRIDA INVOCA, y esa acotacion es la unica
    honesta: de un criterio que ninguna corrida alcanza no se puede afirmar
    nada por esta via, y se comprueba en el test de mas abajo. Lo que este
    cierra es el hueco que dejaba la comprobacion en una sola direccion: un
    criterio invocado a expediente y marcado de perfil pasaria inadvertido,
    y con el la promesa del filtro --- "estos son los que este alcance puede
    necesitar" --- seria falsa por exceso.
    """
    alcanzados = usados_perfil | usados_expediente | usados_perfil_con_opcionales
    de_perfil = [c for c in alcanzados
                 if ca.CRITERIOS[c].nivel == ca.NIVEL_PERFIL]
    assert de_perfil, "sin criterios de perfil invocados no se mide nada"
    for clave in sorted(de_perfil):
        assert clave in usados_perfil or clave in usados_perfil_con_opcionales, (
            f"'{clave}' esta clasificado como de PERFIL y ninguna corrida de "
            "perfil lo invoca. O es de expediente, o su etapa dejo de correr "
            "al alcance de perfil")


def test_ningun_criterio_marcado_de_expediente_lo_invoca_la_corrida_de_perfil(
        usados_perfil, usados_perfil_con_opcionales, diferidos_perfil):
    """
    Segunda direccion, y es la que sostiene el filtro: si dice expediente, la
    corrida de perfil NO lo puede invocar.

    La excepcion no se afirma, se lee: V5 y V8 se intentan a perfil y su fallo
    se difiere, de modo que sus criterios SI se invocan sin ser de perfil. Los
    que la corrida marco `diferido_por_alcance` quedan fuera del reproche ---
    y esa marca la pone la corrida, no este test.
    """
    for clave in sorted(usados_perfil | usados_perfil_con_opcionales):
        if ca.CRITERIOS[clave].nivel != ca.NIVEL_EXPEDIENTE:
            continue
        assert clave in diferidos_perfil, (
            f"'{clave}' esta clasificado como de EXPEDIENTE y la corrida de "
            "perfil lo invoca sin que su etapa quede diferida. El filtro de "
            "alcance lo estaria escondiendo de quien tiene que declararlo")


# ===========================================================================
# Lo que ninguna corrida alcanza
# ===========================================================================

def test_lo_que_ninguna_corrida_invoca_se_clasifica_por_su_consumidor(
        usados_perfil, usados_expediente, usados_perfil_con_opcionales):
    """
    La via debil, y esta separada para que se vea que lo es.

    Un criterio que ninguna corrida invoca no se puede medir. Lo unico que
    queda es el censo: si esta marcado de EXPEDIENTE, ninguno de sus
    consumidores puede ser un modulo que la corrida de perfil ejecute. La
    lista de modulos que el alcance no ejecuta sale de
    `cli.MODULOS_DIFERIDOS_POR_ALCANCE`, que es la MISMA que consultan los dos
    saltos de `correr_punto` y `correr`.
    """
    alcanzados = usados_perfil | usados_expediente | usados_perfil_con_opcionales
    diferidos = set(cli.MODULOS_DIFERIDOS_POR_ALCANCE[cli.ALCANCE_PERFIL])
    sin_medir = [c for c in sorted(ca.CRITERIOS) if c not in alcanzados]
    assert sin_medir, "si todo se mide, este test sobra y hay que retirarlo"
    for clave in sin_medir:
        consumidores = set(ve.variable(clave).consumido_por)
        corren_a_perfil = consumidores - diferidos
        if ca.CRITERIOS[clave].nivel == ca.NIVEL_EXPEDIENTE:
            assert not corren_a_perfil, (
                f"'{clave}' esta clasificado como de EXPEDIENTE y el censo le "
                f"encuentra consumidores que la corrida de perfil SI ejecuta: "
                f"{sorted(corren_a_perfil)}")
        else:
            # SIN NINGUN CONSUMIDOR NO HAY CONTRADICCION QUE DENUNCIAR, y esta
            # rama lo tuvo que aprender de un caso vivo:
            # 'homogeneidad_serie_fen' es un vacio de perfil declarado --- la
            # serie de caudales por FEN no ha llegado --- cuya fase (1-bis,
            # hidrologia) todavia no esta ensamblada, de modo que no lo invoca
            # nadie y aun asi frena el perfil. `variables_sin_consumidor()`
            # existe justamente para distinguir "se olvido cablearlo" de "su
            # fase no existe todavia", y su `fase_declarada` dice cual es.
            # Lo que SI es una contradiccion --- y es lo que queda comprobado
            # --- es declararlo de perfil cuando TIENE consumidores y todos
            # son modulos que el alcance de perfil no ejecuta.
            assert corren_a_perfil or not consumidores, (
                f"'{clave}' esta clasificado como de PERFIL y todos sus "
                f"consumidores ({sorted(consumidores)}) son modulos que la "
                "corrida de perfil no ejecuta: la clasificacion contradice al "
                "censo")


# LOS OCHO QUE ESTE ARCHIVO NO PUEDE COMPROBAR, censados en vez de omitidos.
#
# Se llego a esta lista POR MUTACION, que es la unica forma de saber que
# comprueba de verdad un test: se le cambio el nivel a uno de los trece que S21
# midio y se miro si la suite moria. Murieron cuatro de cinco mutantes; el que
# sobrevivio fue 'demanda_sismica_licuefaccion' de expediente a perfil, y
# sobrevivio por una razon estructural y no por un descuido del test --- no lo
# consume NINGUN modulo, asi que ninguna corrida lo puede invocar y el censo no
# tiene consumidor que contradiga. De un criterio asi, el nivel es un argumento
# y no una medida.
#
# El censo se fija aqui por lo mismo que CLAUDE.md fija el de los dos `inf`
# deliberados: lo que no se puede comprobar se declara, para que no crezca en
# silencio. Si aparece un noveno, este test falla y obliga a decidir --- o se
# cablea su consumidor, o se admite que su nivel es una declaracion.
SIN_CONSUMIDOR_Y_SIN_MEDIDA = (
    "Mw_licuefaccion",
    "PERFIL_SUELO_PRESUNTO",
    "angulo_aletas",
    "c_phi_fundacion",
    "capacidad_portante_adm",
    "clase_sitio",
    "demanda_sismica_licuefaccion",
    "homogeneidad_serie_fen",
)


def test_el_censo_de_lo_que_no_se_puede_medir_no_crece_en_silencio():
    """
    El limite de este archivo, escrito como dato.

    Los ocho no tienen consumidor: ninguna corrida los invoca y el censo de
    `variables_entrada` no puede contradecir su nivel. Su clasificacion se
    defiende con el argumento que cada uno escribe junto a `nivel`, y esa es
    la unica defensa que tienen. Lo que se comprueba aqui es que sean estos
    ocho y no nueve.
    """
    sin_consumidor = tuple(sorted(c for c in ca.CRITERIOS
                                  if not ve.variable(c).consumido_por))
    assert sin_consumidor == tuple(sorted(SIN_CONSUMIDOR_Y_SIN_MEDIDA))


def test_lo_que_no_se_puede_medir_dice_al_menos_por_que_no_lo_invoca_nadie():
    """
    Un criterio sin consumidor tiene dos lecturas opuestas --- se olvido
    cablearlo, o su fase no existe todavia --- y desde fuera no se distinguen.
    El que no llene `sin_consumidor` tiene que decirlo en su fase declarada,
    que es la otra via que el censo ofrece.
    """
    for clave in SIN_CONSUMIDOR_Y_SIN_MEDIDA:
        razon = ca.CRITERIOS[clave].sin_consumidor or ve.variable(clave).fase
        assert razon.strip(), (
            f"'{clave}' no lo invoca nadie y no dice por que: su nivel queda "
            "sin nada que lo sostenga")


def test_ningun_criterio_se_queda_sin_nivel():
    """
    Los trece que quedaban se midieron en S21. La guardia
    `_verificar_nivel` solo lo exige a los criterios SIN VALOR, de modo que
    uno nuevo con valor puede volver a nacer sin clasificar: aqui se ve.

    No es una regla nueva sobre el archivo --- el filtro MUESTRA lo que no
    sabe clasificar, que es la direccion segura ---, es la constancia de que
    hoy no queda ninguno.
    """
    sin_nivel = sorted(c for c in ca.CRITERIOS if not ca.CRITERIOS[c].nivel)
    assert not sin_nivel, (
        "criterios sin nivel declarado: " + ", ".join(sin_nivel))


# ===========================================================================
# El filtro que se apoya en todo lo anterior
# ===========================================================================

def test_el_filtro_de_alcance_no_esconde_nada_que_la_corrida_invoque(
        usados_perfil, usados_perfil_con_opcionales, diferidos_perfil):
    """
    El contrato del filtro, dicho sobre el filtro y no sobre el campo.

    `criterios_del_alcance` lee `nivel`, de modo que este test es consecuencia
    de los dos de arriba --- y se escribe igual, porque lo que la GUI llama es
    esta funcion y es su promesa la que hay que poder citar.
    """
    visibles = set(ca.criterios_del_alcance(cli.ALCANCE_PERFIL))
    for clave in sorted(usados_perfil | usados_perfil_con_opcionales):
        if clave in diferidos_perfil:
            continue
        assert clave in visibles, (
            f"el filtro de alcance perfil esconde '{clave}', que la corrida de "
            "perfil invoca sin diferirlo")


def test_el_filtro_de_expediente_no_esconde_nada():
    """
    El alcance de expediente no difiere ninguna etapa, asi que no puede
    esconder ninguna fila. Es lo que hace del filtro una consecuencia del
    alcance y no una preferencia de quien mira.
    """
    assert set(ca.criterios_del_alcance(cli.ALCANCE_EXPEDIENTE)) == set(ca.CRITERIOS)
    assert cli.MODULOS_DIFERIDOS_POR_ALCANCE[cli.ALCANCE_EXPEDIENTE] == ()


def test_el_alcance_desconocido_no_devuelve_una_lista_vacia():
    """
    Un alcance mal escrito tiene que fallar, no filtrar a cero: una tabla
    vacia se lee como "no queda nada por declarar", que es la lectura mas
    peligrosa que esta pestana puede dar.
    """
    with pytest.raises(ValueError, match="alcance desconocido"):
        ca.criterios_del_alcance("perfíl")


# ===========================================================================
# La declaracion de modulos diferidos, contra lo que la corrida declara
# ===========================================================================

def test_los_modulos_diferidos_coinciden_con_lo_que_la_corrida_difiere():
    """
    `MODULOS_DIFERIDOS_POR_ALCANCE` no puede quedarse describiendo un salto que
    el codigo ya no hace. Los dos `if` de `correr_punto` y `correr` lo
    consultan, asi que lo que queda por comprobar es lo otro: que la corrida
    de perfil deje constancia de haber diferido las dos fases que ese
    diccionario nombra, y ninguna mas.
    """
    externos = cli.cargar_datos_externos(None, EXTERNOS_GLOBALES)
    for id_punto, datos in EXTERNOS_POR_PUNTO.items():
        externos.por_punto.setdefault(id_punto, {}).update(
            {clave: cli.DatoDeclarado(clave, valor, "datos del expediente")
             for clave, valor in datos.items()})
    informe = cli.correr(CSV_PERFIL, externos, alcance=cli.ALCANCE_PERFIL)
    fases = {b.fase for _id, b in informe.diferidos()
             if b.tipo == "DiferidoPorAlcance"}
    assert cli.FASE_ESTRUCTURAL in fases
    assert cli.FASE_CABEZAL in fases
    # El modulo que nombra cada fase diferida sale del rotulo, que es donde
    # `cli` lo escribe: "Fase 8 - Estructural del conducto (M8)".
    for modulo in cli.MODULOS_DIFERIDOS_POR_ALCANCE[cli.ALCANCE_PERFIL]:
        sigla = modulo.split("_")[0]
        assert any(f"({sigla})" in fase for fase in fases), (
            f"'{modulo}' figura como diferido a perfil y ninguna fase diferida "
            "de la corrida lo nombra")
