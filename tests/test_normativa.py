"""
tests/test_normativa.py
=======================
La guardia ESTRUCTURAL del registro normativo: T1, T4, T7 y T10-T22 de la §9.1
de `docs/diseno_registro_normativo.md`.

No abre ningun PDF y corre en milisegundos. Los que SI abren PDF -- T0, T2,
T3, T5 y T6, los que hacen verdadera la palabra «verificado» -- viven en
`tests/test_normativa_pdf.py` y se saltan si PyMuPDF no esta instalado.

QUE VIGILA ESTA GUARDIA, dicho de una vez. Que una cita no pueda pudrirse en
silencio. El hallazgo que abrio el cluster C11 -- el numeral 2.1.4.3.9, que
resulto titularse «Aparatos de Apoyo», propagado a seis puntos del repositorio
como seis cadenas independientes -- no fue un descuido: fue la consecuencia de
que una cita en prosa NO TIENE IDENTIDAD. Estos tests existen para que la
siguiente no pueda comportarse asi.
"""

import pytest

from normativa import registro as _registro
from normativa.discrepancias import DISCREPANCIAS
from normativa.esquema import (
    Acotada,
    AfirmacionNegativa,
    Caracter,
    Catalogo,
    Cita,
    ConjuntoDeMaximos,
    Efecto,
    ErrorDeRegistro,
    Fuente,
    Integra,
    Interpretacion,
    IntervaloAdmisible,
    NoUsada,
    OrdenDeAplicacion,
    PendienteDeCondicion,
    PisoUnico,
    POR_TRANSCRIBIR,
    ROTULOS_DE_RANGO,
    QuePasaFuera,
    SinDeterminar,
    TechoUnico,
    Usada,
    VERBO_COMPATIBLE_CON,
    Verbatim,
    esta_por_transcribir,
)


@pytest.fixture(scope="module")
def reg():
    return _registro.construir()


# ===========================================================================
# T1 - un Catalogo no puede ser la fuente de una cita
# ===========================================================================

def test_T1_toda_cita_resuelve_a_una_fuente_y_ninguna_a_un_catalogo(reg):
    """
    Es el cierre estructural de `NOR-PRO-01` / `NOR-PRO-02`: los topes de
    diametro se imprimian atribuidos a AASHTO M170 y ASTM A760 -- normas que
    tabulan hasta 3600 mm -- y descartaban material en silencio con una cita
    que ninguna norma sostiene. Un tope de catalogo no tiene numeral, y el
    sistema de tipos ya no le deja fingir que lo tiene.
    """
    ids_fuente = set(reg.ids_de_fuente())
    for c in reg.citas:
        assert c.fuente_id in ids_fuente, f"{c.id}: fuente inexistente"
    for cat in reg.catalogos:
        with pytest.raises(KeyError, match="Catalogo"):
            reg.fuente(cat.id)


def test_T1_un_catalogo_declara_que_norma_NO_lo_sostiene():
    with pytest.raises(ErrorDeRegistro):
        Catalogo(id="X", titulo="x", proveedor_o_ambito="x",
                 que_norma_NO_lo_sostiene="")


# ===========================================================================
# T4 - integridad referencial
# ===========================================================================

def test_T4_todo_id_referenciado_existe(reg):
    """El id que apunta a nada: la version moderna de la referencia rota."""
    problemas = reg.problemas_de_integridad()
    assert not problemas, "\n  ".join(("integridad referencial rota:", *problemas))


def test_T4_ninguna_cita_queda_huerfana(reg):
    """
    Una cita que nadie referencia es una cita que nadie puede haber
    comprobado: o sostiene algo o sobra. Se admiten dos excepciones, y las dos
    llevan su razon escrita en el propio objeto:

      - las citas que DECLARAN un defecto (el numeral retirado de
        `MP.2.1.4.3.9`), que existen para que el error tenga donde estar dicho;
      - las que sostienen un valor de `constantes_normativas.py` sin pasar por
        una tabla (las que el archivo consume por `_reg.cita(...)`).

    Ambas se reconocen porque `constantes_normativas` las nombra.
    """
    import constantes_normativas as CN

    consumidas = {v for nombre in dir(CN) if nombre.startswith("NUMERAL")
                  for v in [getattr(CN, nombre)] if isinstance(v, str)}
    referenciadas = reg.citas_referenciadas()
    huerfanas = []
    for c in reg.citas:
        if c.id in referenciadas:
            continue
        if any(c.numeral in texto for texto in consumidas):
            continue
        huerfanas.append(c.id)
    assert not huerfanas, (
        "citas que no sostienen nada y que nadie referencia: "
        f"{huerfanas}. O tienen consumidor, o declaran un defecto y lo dicen "
        "en su `nota`, o sobran")


# ===========================================================================
# T7 - una Interpretacion no se serializa dentro de una cita
# ===========================================================================

def test_T7_ninguna_interpretacion_viaja_dentro_de_un_campo_de_cita(reg):
    """
    LA REINCIDENCIA QUE ESTE TEST IMPIDE. `NOR-HID-06` se cerro una vez y se
    reabrio: el bloque construido para cerrarlo rotulaba «Texto literal» dos
    composiciones que no lo eran. El defecto no fue de una constante suelta,
    fue DEL FORMATO -- y por eso la solucion tiene que ser del formato.
    """
    for c in reg.citas:
        if c.interpretacion is None:
            continue
        assert isinstance(c.interpretacion, Interpretacion)
        texto = c.texto_literal
        if isinstance(texto, Verbatim):
            assert c.interpretacion.texto not in texto.texto, (
                f"{c.id}: la interpretacion esta dentro del texto literal")


def test_T7_una_interpretacion_exige_hechos_en_contra():
    """
    Una lectura que no encuentra nada en contra no se ha buscado a si misma.
    Es lo que permite a un revisor discutir la interpretacion sin discutir la
    norma.
    """
    with pytest.raises(ErrorDeRegistro):
        Interpretacion(texto="x", en_contra=(), a_favor=("y",))


# ===========================================================================
# T11 - caracter obligatorio; verbo compatible
# ===========================================================================

def test_T11_toda_cita_declara_su_caracter(reg):
    for c in reg.citas:
        assert isinstance(c.caracter, Caracter), f"{c.id} sin caracter"


def test_T11_el_verbo_de_un_fundamento_es_compatible_con_sus_citas(reg):
    """
    Lo que impide escribir «la norma obliga a…» sobre el parrafo que dice
    «recomendandose que la velocidad minima sea igual a 0.25 m/s»
    (`NOR-MEM-01`, `MAT-O13`).
    """
    for f in reg.fundamentos:
        caracteres = {reg.cita(cid).caracter for cid in f.citas}
        admitidos = set(VERBO_COMPATIBLE_CON[f.verbo])
        assert caracteres & admitidos, (
            f"fundamento {f.id}: verbo {f.verbo.value} sobre citas "
            f"{[c.value for c in caracteres]}")


# ===========================================================================
# T12 - los tres ejes de «parcial» llevan su razon
# ===========================================================================

def test_T12_una_transcripcion_acotada_dice_por_que_y_donde_leer_el_resto(reg):
    for t in reg.tablas:
        if isinstance(t.alcance, Acotada):
            assert t.alcance.razon.strip()
            assert t.alcance.que_queda_fuera.strip()
            assert t.alcance.donde_leerlo.strip()


def test_T12_una_columna_o_fila_no_usada_dice_por_que(reg):
    """
    NO es un defecto que el calculo use una parte: es informacion, y
    `por_que_no` es lo que la ventana pinta en el sitio donde nace la duda.
    Una columna sin razon declarada no compila el registro.
    """
    for t in reg.tablas:
        for e in (*t.columnas, *t.filas):
            if isinstance(e.uso, NoUsada):
                assert e.uso.por_que_no.strip(), f"{t.id}: {e.id} sin razon"


def test_T12_acotada_sin_razon_no_se_puede_construir():
    with pytest.raises(ErrorDeRegistro):
        Acotada(razon="", que_queda_fuera="x", donde_leerlo="y")
    with pytest.raises(ErrorDeRegistro):
        NoUsada(por_que_no="   ")


def test_T12_pendiente_no_es_lo_mismo_que_no_usada(reg):
    """
    LA DISTINCION QUE HACE POSIBLE DECLARAR «completa de uso parcial» SIN QUE
    PAREZCA QUE SE ESCONDE ALGO. En `NoUsada` la decision esta tomada y
    razonada -- la columna NORMAL de la Tabla Nº 09 --; en
    `PendienteDeCondicion` FALTA UN DATO y el calculo se detiene -- las dos
    filas multicarril del Cuadro 4.1 --. Confundirlas es lo que hacia
    imposible declarar la primera.
    """
    pendientes = reg.elecciones_pendientes()
    assert pendientes, (
        "el registro no declara ninguna eleccion pendiente; el Cuadro 4.1 "
        "tiene dos filas que dependen de `carriles_por_sentido`")
    for donde, condicion_id in pendientes:
        assert reg.condicion(condicion_id) is not None, (
            f"{donde} apunta a la condicion «{condicion_id}», que no existe")


# ===========================================================================
# T13 / T14 - lo que el calculo consume esta transcrito, y coincide
# ===========================================================================

def test_T13_toda_vista_de_calculo_declarada_existe_de_verdad(reg):
    """
    Si una tabla declara que de ella se deriva `MANNING`, ese nombre tiene que
    existir en `constantes_normativas`. Es la mitad barata de T14.
    """
    import constantes_normativas as CN
    for t in reg.tablas:
        for vista in t.vistas_de_calculo:
            assert hasattr(CN, vista), (
                f"{t.id} declara la vista `{vista}`, que no existe en "
                "constantes_normativas")


def test_T14_las_vistas_derivadas_coinciden_con_su_transcripcion(reg):
    """
    D2: la vista de calculo se DERIVA de la transcripcion, no se copia. Este
    test lo comprueba sobre las que el codigo ya deriva, para que si alguien
    vuelve a escribir el numero a mano, las dos copias diverjan y se vea.
    """
    import constantes_normativas as CN

    t09 = reg.tabla("MC_HHD.T09")
    assert CN.MANNING == {t09.clave_corta(f): (f.valores["minimo"],
                                               f.valores["maximo"])
                          for f in t09.filas}
    t10 = reg.tabla("MC_HHD.T10")
    assert CN.V_MAX == {t10.clave_corta(f): f.valores["velocidad"].valores
                        for f in t10.filas}
    c41 = reg.tabla("MS.C41")
    assert CN.CALICATAS_POR_SENTIDO == {c41.clave_corta(f): f.valores["por_sentido"]
                                        for f in c41.filas}


# ===========================================================================
# T15 - advertir no puede ser la salida comoda
# ===========================================================================

def test_T15_una_condicion_que_no_bloquea_lleva_su_justificacion(reg):
    """
    D4 invertida: lo indeterminado bloquea, y lo que NO bloquea es lo que hay
    que justificar. `NOR-HDS-05` es la prueba de que un esquema que solo
    bloquee es inservible -- la condicion «que el barril fluya lleno» no la
    puede evaluar este programa --, y tambien de que `ADVIERTE` no puede ser
    comodo.
    """
    for donde, cond in reg.condiciones():
        if cond.efecto_si_indeterminada is not Efecto.BLOQUEA:
            assert cond.justificacion_de_no_bloquear.strip(), (
                f"{donde}: la condicion {cond.id} no bloquea y no dice por que")


def test_T15_por_defecto_una_condicion_bloquea():
    """El valor por defecto ES la regla; desviarse exige texto."""
    from normativa.esquema import CondicionAplicacion, PorDatoDeSitio
    c = CondicionAplicacion(
        id="X", texto=Verbatim(texto="x", pagina_pdf=1), cita_id="Y",
        resuelve=PorDatoDeSitio(clave="z"))
    assert c.efecto_si_indeterminada is Efecto.BLOQUEA


# ===========================================================================
# T16 - todo modificador declara su orden de aplicacion
# ===========================================================================

def test_T16_todo_modificador_declara_orden_y_tiene_tramos(reg):
    """
    `orden` es el campo que puede INVERTIR QUE NORMA GOBIERNA: aplicar el 0.8
    antes o despues de cruzar fuentes da 70.0 o 60.96 mm, y con ello E.060 o
    AASHTO en la memoria. Es obligatorio y no tiene valor por defecto.
    """
    for m in reg.modificadores():
        assert isinstance(m.orden, OrdenDeAplicacion), f"{m.id} sin orden"
        assert m.tramos, f"{m.id} sin tramos"


# ===========================================================================
# T17 - una fuente ausente no sostiene un [N]
# ===========================================================================

def test_T17_una_fuente_ausente_no_tiene_archivo_ni_sha1(reg):
    for f in reg.fuentes_ausentes:
        assert f.ausente and f.ausencia is not None
        assert f.archivo_pdf is None and f.sha1 is None, (
            f"{f.id}: no hay contra que verificar y el registro no finge "
            "que lo hay")


def test_T17_ninguna_cita_se_apoya_en_una_fuente_ausente(reg):
    """
    Es la definicion misma de `[N]` en CLAUDE.md: numeral VERIFICADO. Lo que
    impide, estructuralmente, una cita como «WSDOT Hydraulics Manual (M
    23-03.12, abril 2026)» con pagina y frase que nadie abrio.
    """
    ausentes = {f.id for f in reg.fuentes_ausentes}
    for c in reg.citas:
        assert c.fuente_id not in ausentes, (
            f"{c.id} cita la fuente ausente {c.fuente_id}: se cita EL "
            "DOCUMENTO, no una pagina suya")


def test_T17_toda_ausencia_dice_que_desbloquearia_y_cuanto_cuesta(reg):
    """`que_desbloquearia` convierte la deuda en trabajo con precio."""
    for f in reg.fuentes_ausentes:
        assert f.ausencia.que_desbloquearia.strip()
        assert f.ausencia.por_que_se_cita.strip()
        assert f.ausencia.esfuerzo is not None


# ===========================================================================
# T18 - los tres «rangos» no se pueden confundir
# ===========================================================================

def test_T18_los_tres_rotulos_de_rango_son_textualmente_distintos():
    """
    §4.2 del plan: dominio fisico, rango normativo y rango de sensibilidad son
    TRES cosas que el repositorio llamaba igual. Si compartieran rotulo
    compartirian renderizador, y la ventana los enseñaria con la misma cara.
    """
    valores = list(ROTULOS_DE_RANGO.values())
    assert len(set(valores)) == len(valores)
    assert "NO es normativo" in ROTULOS_DE_RANGO["dominio_fisico"]
    assert "proyectista" in ROTULOS_DE_RANGO["sensibilidad"]


def test_T18_un_conjunto_de_maximos_no_tiene_minimo():
    """
    `NOR-HID-04`, hecho imposible de representar. Los dos numeros de la fila
    del concreto de la Tabla Nº 10 son AMBOS maximos. En cuanto eso vaya a una
    ventana rotulada «rango», el usuario leera 3.0 como minimo -- salvo que el
    objeto NO TENGA a que enlazar la casilla «desde».
    """
    fila = ConjuntoDeMaximos(valores=(3.0, 6.0), unidad="m/s", cita_id="x",
                             que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    assert not hasattr(fila, "minimo")
    assert "MAXIMOS" in fila.rotulo_obligatorio
    # Y una tupla de UN elemento es la forma normal, no un caso especial
    # (`NOR-HID-07`): la mamposteria trae un solo valor y escribirla (2.0, 2.0)
    # inventaba un par que la fuente no escribe.
    assert ConjuntoDeMaximos(valores=(2.0,), unidad="m/s", cita_id="x",
                             que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)


def test_T18_que_pasa_fuera_distingue_incumplir_de_no_estar_cubierto():
    """
    Sin el cuarto valor, un valor fuera de la tabla se acaba leyendo como
    incumplimiento -- que es lo contrario de lo que la fuente hace: callar.
    """
    assert QuePasaFuera.LA_FUENTE_NO_SE_PRONUNCIA != QuePasaFuera.INCUMPLE_LA_NORMA
    assert len(set(QuePasaFuera)) == 4   # literal-ok: son cuatro y solo cuatro


def test_T18_la_familia_de_rangos_no_comparte_atributos(reg):
    """
    La semantica ES el tipo: `TechoUnico` no tiene minimo, `PisoUnico` no
    tiene maximo, y solo `IntervaloAdmisible` tiene los dos. Un renderizador
    generico de «rango» es justamente la pieza que no debe existir.
    """
    techo = TechoUnico(maximo=1.0, unidad="m", cita_id="x",
                       que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    piso = PisoUnico(minimo=1.0, unidad="m", cita_id="x",
                     que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    intervalo = IntervaloAdmisible(minimo=1.0, maximo=2.0, unidad="m",
                                   cita_id="x",
                                   que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    assert not hasattr(techo, "minimo") and not hasattr(piso, "maximo")
    assert hasattr(intervalo, "minimo") and hasattr(intervalo, "maximo")
    assert len({techo.rotulo_obligatorio, piso.rotulo_obligatorio,
                intervalo.rotulo_obligatorio}) == 3


# ===========================================================================
# T19 - una correspondencia de tablas no se salta filas en silencio
# ===========================================================================

def test_T19_toda_fila_de_la_tabla_a_tiene_par_declarado(reg):
    """
    El defecto real que este invariante impide: el cruce de las dos
    transcripciones del recubrimiento se hacia con `situacion in
    RECUBRIMIENTO_MP_MM`, daba False para las 8 filas de la familia de pilotes
    y SE SALTABA SIN AVISAR, mientras el comentario afirmaba que cubria todas.
    """
    for corr in reg.correspondencias:
        a = reg.tabla(corr.tabla_a)
        for fila in a.filas:
            clave = a.clave_corta(fila)
            assert clave in corr.pares or fila.id in corr.pares, (
                f"{corr.id}: la fila «{clave}» de {corr.tabla_a} no tiene "
                "correspondencia declarada. Una fila sin par es un ERROR, no "
                "un salto callado")


# ===========================================================================
# T20 - las discrepancias abiertas estan listadas
# ===========================================================================

def test_T20_las_discrepancias_abiertas_contra_la_hoja_de_ruta_se_enumeran(reg):
    """
    LA TERCERA OBLIGACION DE `CLAUDE.md`, que hasta ahora no tenia donde
    vivir: «dejar dicho que la hoja de ruta SIGUE MAL mientras no se corrija».
    En prosa dependia de que alguien se acordara; aqui es enumerable.
    """
    abiertas = reg.discrepancias_abiertas()
    assert abiertas, (
        "ninguna discrepancia abierta: o se corrigieron todas -- y entonces "
        "hay que decirlo en la hoja de ruta -- o alguien las borro")
    for d in abiertas:
        assert d.efecto_si_se_sigue_la_otra.strip(), (
            f"{d.id}: no dice que pasa si se sigue la otra parte")


def test_T20_toda_discrepancia_tiene_dos_partes_y_una_gana(reg):
    for d in reg.discrepancias:
        assert len(d.partes) >= 2
        assert d.gana in {p.quien for p in d.partes}


def test_T20_las_erratas_que_una_tabla_declara_son_discrepancias(reg):
    for t in reg.tablas:
        for e in t.erratas:
            assert e in DISCREPANCIAS, (
                f"{t.id} declara la errata «{e}», que no es una Discrepancia")


# ===========================================================================
# T21 - un Verbatim conserva tildes, mayusculas y erratas
# ===========================================================================

def test_T21_los_verbatim_del_registro_conservan_sus_diacriticos(reg):
    """
    UN LITERAL DE-ACENTUADO NO SE PUEDE ENCONTRAR EN EL PDF, y entonces no es
    verificable por nadie salvo por quien ya sabe donde esta. La normalizacion
    sin diacriticos existe para BUSCAR, nunca para GUARDAR.

    Se comprueba de la unica forma barata que no da falsos positivos: los
    textos del corpus peruano son largos y en español, y un texto largo en
    español sin una sola tilde ha sido de-acentuado.
    """
    minimo_para_sospechar = 120   # literal-ok: longitud a partir de la cual un
                                  # texto en español sin tildes es sospechoso
    tildes = set("áéíóúÁÉÍÓÚñÑüÜ")
    sospechosos = []
    for c in reg.citas:
        if reg.fuente(c.fuente_id).id.startswith(("AASHTO", "ASTM", "HDS")):
            continue        # el corpus en ingles no lleva tildes, y es correcto
        t = c.texto_literal
        if not isinstance(t, Verbatim):
            continue
        if len(t.texto) > minimo_para_sospechar and not (set(t.texto) & tildes):
            sospechosos.append(c.id)
    assert not sospechosos, (
        "textos literales largos del corpus peruano sin una sola tilde: "
        f"{sospechosos}. Un Verbatim de-acentuado no se puede volver a "
        "encontrar en el PDF")


def test_T21_la_normalizacion_es_para_buscar_y_no_altera_lo_guardado():
    from normativa.extraccion import normalizar
    original = "Velocidades máximas admisibles (m/s), 2,0 %"
    plano = normalizar(original)
    assert plano == "velocidades maximas admisibles (m/s), 2.0 %"
    # La coma decimal ENTRE DIGITOS es un punto; la de una enumeracion, no.
    assert normalizar("DC, DD, DW") == "dc, dd, dw"
    # Y lo guardado sigue siendo lo guardado.
    assert "máximas" in original


# ===========================================================================
# T22 - POR_TRANSCRIBIR: no se firma, y su total solo decrece
# ===========================================================================

# EL TRINQUETE. Este numero solo puede BAJAR. La migracion a medias es un
# estado legitimo; la migracion a medias INVISIBLE, no. Si sube, es que se
# añadieron campos sin leer el PDF -- y eso es lo que este cluster persigue.
MAX_POR_TRANSCRIBIR = 0


def test_T22_ninguna_cita_pendiente_lleva_firma_de_verificacion(reg):
    for c in reg.citas:
        if c.tiene_pendientes:
            assert c.verificado is None, (
                f"{c.id}: lleva {c.campos_pendientes} sin transcribir y una "
                "firma de verificacion. Lo pendiente de leer no se firma")


def test_T22_el_total_de_por_transcribir_solo_decrece(reg):
    total = reg.cuenta_por_transcribir()
    assert total <= MAX_POR_TRANSCRIBIR, (
        f"el registro tiene {total} campos POR_TRANSCRIBIR y el trinquete "
        f"esta en {MAX_POR_TRANSCRIBIR}. Si el aumento es deliberado, baja el "
        "trinquete en el MISMO commit y di por que")


def test_T22_el_centinela_es_unico_y_falsy():
    """
    UN solo valor admisible para lo aun no leido, y falsy para que
    `if cita.titulo_numeral:` se lea como «si ya se transcribio».
    """
    from normativa.esquema import _PorTranscribir
    assert POR_TRANSCRIBIR is _PorTranscribir()
    assert not POR_TRANSCRIBIR
    assert esta_por_transcribir(POR_TRANSCRIBIR)
    assert not esta_por_transcribir("")


def test_T22_una_cita_con_pendientes_y_firma_no_se_puede_construir():
    from normativa.esquema import MetodoDeVerificacion, Verificado
    with pytest.raises(ErrorDeRegistro):
        Cita(id="X", fuente_id="MC_HHD", numeral="1", titulo_numeral="t",
             pagina_impresa="1", pagina_pdf=POR_TRANSCRIBIR,
             texto_literal=Verbatim(texto="x", pagina_pdf=1),
             caracter=Caracter.DEFINICION,
             verificado=Verificado(fecha="2026-01-01", por="x", sha1_pdf="y",
                                   metodo=MetodoDeVerificacion.TEXTO))


# ===========================================================================
# Invariantes del esquema que no llevan numero pero sostienen a los que si
# ===========================================================================

def test_una_fuente_ausente_exige_su_Ausencia():
    with pytest.raises(ErrorDeRegistro):
        Fuente(id="X", titulo="x", emisor="y", edicion="z", anio=2020,
               ausente=True)


def test_una_fuente_presente_exige_archivo_y_sha1():
    with pytest.raises(ErrorDeRegistro):
        Fuente(id="X", titulo="x", emisor="y", edicion="z", anio=2020)


def test_una_afirmacion_negativa_exige_su_ambito_barrido():
    """
    Una afirmacion negativa es lo que AUTORIZA saltar a un `[C]` con fuente
    externa. Mal hecha, cubre con fuente ajena un vacio que no existe -- que
    es la forma exacta de `NOR-VAC-01`, donde el «vacio verificado» de la
    cobertura minima no era un vacio: AASHTO 12.6.6.3 lo tabulaba.
    """
    with pytest.raises(ErrorDeRegistro):
        AfirmacionNegativa(que_no_dice="la tabla no lista X", ambito_barrido="")


def test_una_tabla_no_admite_celdas_en_columnas_que_no_declara():
    from normativa.esquema import ColumnaDeTabla, FilaDeTabla, TablaNormativa
    with pytest.raises(ErrorDeRegistro):
        TablaNormativa(
            id="T", cita_id="C", titulo_literal="t",
            columnas=(ColumnaDeTabla(id="a", etiqueta_literal="A", unidad="",
                                     uso=Usada(por=("x",))),),
            filas=(FilaDeTabla(id="T#1", etiqueta_literal="f",
                               valores={"b": 1.0}, uso=Usada(por=("x",))),),
            alcance=Integra())


def test_el_rotulo_de_completitud_lo_deriva_la_tabla_de_sus_campos(reg):
    """
    La frase que ve el revisor no puede contradecir a los campos porque ES los
    campos. Nadie la escribe a mano.
    """
    t09 = reg.tabla("MC_HHD.T09")
    rotulo = t09.rotulo_de_completitud()
    assert rotulo.startswith("Transcripcion acotada")
    # Tres de sus cuatro columnas se consumen -- TIPO DE CANAL para elegir la
    # fila, MINIMO y MAXIMO para el doble n --; la que no es NORMAL, y su
    # razon esta escrita en el propio objeto. El ejemplo del diseño escribe
    # «2 de 4» porque no cuenta la columna de rotulo como consumida; aqui se
    # cuenta, porque M2 la lee de verdad para elegir la fila. Lo que importa
    # del invariante es que el numero salga de los campos y no de una frase.
    assert "3 de 4 columnas" in rotulo
    assert "2 de 4 filas" in rotulo
    t10 = reg.tabla("MC_HHD.T10")
    assert t10.rotulo_de_completitud().startswith("Tabla completa")


def test_la_fila_legible_la_compone_una_funcion_y_no_el_dato(reg):
    """
    El separador que une los niveles es DEL PROYECTO: buscar la linea
    compuesta en el PDF no la encontraria, buscar cualquiera de sus trozos si.
    Por eso la composicion vive en un metodo y no dentro de la transcripcion.
    """
    fila = reg.tabla("MC_HHD.T09").fila("concreto_tubo_recto")
    assert fila.etiqueta_literal == "tubo recto y libre de basuras"
    assert len(fila.jerarquia) == 3
    assert " -- " in fila.legible()
    assert " -- " not in fila.etiqueta_literal


def test_la_paginacion_predice_la_pagina_pdf_desde_la_impresa(reg):
    """
    El desfase deja de ser documentacion y pasa a ser PREDICCION. Y una
    `SinDeterminar` no predice nada, que es exactamente lo que hay que poder
    decir de una fuente que no se ha medido.
    """
    assert reg.fuente("MC_HHD").paginacion.pagina_pdf("75") == 78
    assert reg.fuente("EG2013").paginacion.pagina_pdf("984") == 992
    assert reg.fuente("HDS5_3ED").paginacion.pagina_pdf("3.24") == 106
    assert reg.fuente("HDS5_3ED").paginacion.pagina_pdf("C.6") == 216
    assert reg.fuente("AASHTO_LRFD_9").paginacion.pagina_pdf("3-151") == 205
    assert reg.fuente("AASHTO_LRFD_9").paginacion.pagina_pdf("11-145") == 1614
    assert isinstance(reg.fuente("HDS5_SI_1985").paginacion, SinDeterminar)
    assert reg.fuente("HDS5_SI_1985").paginacion.pagina_pdf("1") is None


def test_las_fuentes_sin_texto_extraible_estan_declaradas(reg):
    """
    Es una propiedad DE LA FUENTE, no un percance de quien la lee: tres de las
    trece no entregan texto utilizable y sus citas se verifican por imagen o
    no se verifican.
    """
    sin_texto = {f.id for f in reg.fuentes if not f.texto_extraible}
    assert sin_texto == {"AASHTO_M36", "AASHTO_M170M", "ASTM_A760"}


def test_la_cita_falsa_de_NOR_PUE_01_sigue_declarada(reg):
    """
    El numeral retirado NO se borra: se nombra. Un revisor que venga con la
    cita vieja en la mano tiene que encontrar aqui por que no vale, y este
    test tiene contra que fallar si alguien la reactiva.
    """
    falsa = reg.cita("MP.2.1.4.3.9")
    assert falsa.titulo_numeral == "Aparatos de Apoyo"
    assert "0.60" not in falsa.texto_literal.texto
    buena = reg.cita("MP.2.4.2.2#SOBRECARGA")
    assert buena.titulo_numeral == "Cargas de Suelo: EH, ES, y DD"
    assert "0.60 m de altura de relleno" in buena.texto_literal.texto


def test_el_numeral_de_laushey_no_escribe_ningun_valor_de_g(reg):
    """
    `NOR-HID-01` / `MAT-O7`: el numero es defendible y la cita no lo era.
    """
    laushey = reg.cita("MC_HHD.4.1.1.3.7c#G")
    assert "9.8" not in laushey.texto_literal.texto
    assert laushey.titulo_numeral.endswith("Socavación local a la salida de la "
                                           "alcantarilla")
    # Y los dos numerales que SI lo escriben estan en el registro.
    assert "9.8" in reg.cita("MC_HHD.3.12.5#G").texto_literal.texto
    assert "9.8" in reg.cita("MC_HHD.4.1.1.5.4b24#G").texto_literal.texto
