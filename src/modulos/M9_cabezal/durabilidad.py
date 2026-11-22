# -*- coding: utf-8 -*-
"""
M9_cabezal.durabilidad
======================
Submodulo de Fase 9 (`M9_cabezal`): bloque `durabilidad` (D1).
"""

from __future__ import annotations

from typing import Optional, Tuple

from src import criterios_adoptados as ca
from src.constantes_normativas import (
    AMBIENTE_CORROSIVO_AUMENTAR,
    AMBIENTE_CORROSIVO_TEXTO,
    CICLOPEO_DOS_MINIMOS,
    CICLOPEO_FC_MATRIZ_MIN_APLICABLE,
    CICLOPEO_FRACCION_PIEDRA_MAX,
    CLASE_DE_SITIO_COHERENCIA_INTERNA,
    CLASE_DE_SITIO_INDETERMINADA,
    CLASE_DE_SITIO_POR_QUE_DEJA_DE_DECIRSE,
    CLASE_DE_SITIO_QUE_LA_CIERRA,
    CLASE_SITIO_EF_NO_SUPUESTA_MP_TEXTO,
    CLASE_SITIO_EF_NO_SUPUESTA_TEXTO,
    CLASE_SITIO_INVESTIGACION_TEXTO,
    CUANTIA_MIN_MURO_E060_14_3_1,
    E030_AMBITO_LECTURA,
    E030_ART_7_3_TEXTO,
    E030_S5_LECTURA,
    E030_S5_TEXTO,
    ESPACIAMIENTO_MAX_ABSOLUTO,
    ESPACIAMIENTO_MAX_VECES_ESPESOR,
    ESPESOR_DOS_CAPAS_REFUERZO,
    ESPESOR_TEMPERATURA_DOS_CARAS,
    EXCENTRICIDAD_ERRATA_MANUAL,
    EXCEPCION_DOS_CAPAS_REFUERZO,
    EXCEPCION_REFUERZO_MIN_MURO_TEXTO,
    EXPOSICION_ESPECIAL,
    HIPOTESIS_EMPUJE_BAJO_NF,
    HOMONIMIA_CLASE_F,
    H_EQ_REPARTO_DE_TABLAS,
    KA_COULOMB_DECLARACION,
    K_AE_ERRATA_MANUAL,
    K_H0_ROCA_ERRATA,
    NUMERAL_AGUA_TRASDOS_AASHTO,
    NUMERAL_CICLOPEO,
    NUMERAL_CICLOPEO_APLICABLE,
    NUMERAL_CLASE_SITIO_AASHTO,
    NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA,
    NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA_MP,
    NUMERAL_CLASE_SITIO_INVESTIGACION,
    NUMERAL_CLASE_SITIO_MP,
    NUMERAL_COMBINACION_4_2_4_4,
    NUMERAL_CUANTIA_MIN,
    NUMERAL_DOS_CAPAS_REFUERZO,
    NUMERAL_E030_AMBITO,
    NUMERAL_E030_ESTRUCTURAS_NO_EDIFICACION,
    NUMERAL_E030_S5,
    NUMERAL_ESPACIAMIENTO,
    NUMERAL_EXCENTRICIDAD_ESTATICA,
    NUMERAL_EXCENTRICIDAD_SISMICA,
    NUMERAL_EXCENTRICIDAD_SISMICA_AASHTO,
    NUMERAL_EXCEPCION_REFUERZO_MIN_MURO,
    NUMERAL_EXPOSICION_ESPECIAL,
    NUMERAL_K_AE_AASHTO,
    NUMERAL_K_AE_MANUAL,
    NUMERAL_K_H0,
    NUMERAL_LICUEFACCION_AASHTO,
    NUMERAL_LICUEFACCION_ESPECTRO,
    NUMERAL_PRESION_CONTACTO,
    NUMERAL_PROTECCION_CORROSION,
    NUMERAL_P_IR,
    NUMERAL_RECUBRIMIENTO,
    NUMERAL_RECUBRIMIENTO_MP,
    NUMERAL_RESPUESTA_DE_SITIO_AASHTO,
    NUMERAL_RESPUESTA_DE_SITIO_MP,
    NUMERAL_SOBRECARGA_TRASDOS,
    NUMERAL_SOBRECARGA_TRASDOS_AASHTO,
    NUMERAL_SOBRECARGA_TRASDOS_ALTURA,
    NUMERAL_SOBRECARGA_TRASDOS_APLICA,
    NUMERAL_SULFATOS,
    NUMERAL_TEMPERATURA_DOS_CARAS,
    NUMERAL_ZAPATA_EN_TALUD,
    NUMERAL_ZAPATA_TALUD_E050,
    PROTECCION_CORROSION_TEXTO,
    RECUBRIMIENTO,
    RECUBRIMIENTO_AC_UMBRAL_ALTO,
    RECUBRIMIENTO_AC_UMBRAL_BAJO,
    RECUBRIMIENTO_MP_EQUIVALENCIA,
    RECUBRIMIENTO_MP_FACTOR_AC,
    RECUBRIMIENTO_MP_MM,
    RECUBRIMIENTO_MP_PISO_MM,
    REGIMENES_CORTANTE_MURO,
    REGIMEN_CORTANTE_PERPENDICULAR,
    SECCION_CABEZALES,
    SULFATOS,
    homonimia_como_texto,
)
from src.modelos import (
    CIFRAS_FACTOR,
    CriterioPendienteError,
    CuantiaRefuerzo,
    DatoInvalidoError,
    EleccionDeProyecto,
    Magnitud,
    RecubrimientoDiseno,
    RequisitosDurabilidad,
    TipoDeVeredicto,
    Umbral,
    Veredicto,
    Verificacion,
    paso,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

from src.modulos.M9_cabezal._criterios import (
    CATEGORIA_ACERO_SIN_RECUBRIR,
    CLAVES_ESCALAS_SULFATOS,
    CLAVE_FILAS_TABLA_4_2,
    CRITERIO_CATEGORIA_REFUERZO,
    CRITERIO_CORTANTE_ALTO,
    CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO,
    CRITERIO_EXPOSICION_QUIMICA,
    CRITERIO_FACTOR_BANDA_AC,
    CRITERIO_REGIMEN_CORTANTE,
    CRITERIO_SITUACION_RECUBRIMIENTO,
    CRITERIO_TABLA_RECUBRIMIENTO,
    NOMBRE_TABLA_4_2,
    NOMBRE_TABLA_4_4,
    NUMERAL_9_1,
    NUMERAL_CORTANTE_ALTO,
    NUMERAL_CORTANTE_ALTO_VERTICAL,
    NUMERAL_CORTANTE_PERPENDICULAR,
    NUMERAL_FLEXION_CORTE,
    NUMERAL_REGLA_RECUBRIMIENTO,
    NUMERAL_SUBPRESION,
    _finito,
)

# ===========================================================================
# 9.4 - REFUERZO Y DURABILIDAD
# ===========================================================================

def recubrimiento_e060_mm(*, condicion: str) -> float:
    """
    Recubrimiento minimo de E.060 Art. 7.7.1 (pag. 54), en mm. [N] por la
    excepcion declarada de durabilidad de Sec. 0.2: E.060 Cap. 4 y Art. 7.7
    si aplican, por ser especificacion de MATERIALES y estar calibrados con
    cementos peruanos.

    Condiciones: 'contra_suelo' (70), 'suelo_intemperie_ge_3_4' (50),
    'suelo_intemperie_le_5_8' (40).
    """
    if condicion not in RECUBRIMIENTO:
        raise DatoInvalidoError(
            campo="condicion", valor=condicion,
            motivo="no es una fila del Art. 7.7.1: " + ", ".join(sorted(RECUBRIMIENTO)),
        )
    return float(RECUBRIMIENTO[condicion])


def clase_exposicion_sulfatos(*, so4_suelo_pct: Optional[float],
                             so4_agua_ppm: Optional[float]) -> dict:
    """
    Fila de la Tabla 4.4 de E.060 (pag. impresa 38) que aplica al sitio.

    DOS ESCALAS PARALELAS, no una. La tabla clasifica por sulfato soluble en
    el SUELO (% en peso) o por sulfato en el AGUA (ppm), y son alternativas:
    el expediente puede traer una, la otra o las dos. Con las dos, gobierna la
    MAS exigente -- no promedian ni se eligen, y quedarse con la menor seria
    escoger el requisito mas bajo por omision.

    EL BORDE QUE LA TABLA IMPRESA DEJA ABIERTO -- SO4 = 2,0 % exacto no cae en
    ninguna fila -- lo cierra la hoja de ruta hacia la fila SEVERA, y cada fila
    de `SULFATOS` declara si su limite inferior es estricto en vez de dejar la
    respuesta escondida en un ">=" de este bucle. Ver
    `SULFATOS_BORDE_ABIERTO_TEXTO`.
    """
    if so4_suelo_pct is None and so4_agua_ppm is None:
        raise DatoInvalidoError(
            campo=CRITERIO_EXPOSICION_QUIMICA, valor=None,
            motivo="la Tabla 4.4 clasifica por sulfato en el suelo (% en "
                   "peso) o por sulfato en el agua (ppm), y el dato no trae "
                   "ninguna de las dos escalas",
        )
    indice = 0
    for posicion, fila in enumerate(SULFATOS):
        estricto = fila["limite_inferior_estricto"]
        alcanza = False
        for medida, clave in ((so4_suelo_pct, "so4_suelo_pct"),
                              (so4_agua_ppm, "so4_agua_ppm")):
            if medida is None:
                continue
            minimo = fila[clave][0]
            # El limite estricto NO se decide aqui: viaja en la fila, porque
            # es una lectura declarada y no una convencion del codigo.
            alcanza = alcanza or (medida > minimo if estricto
                                  else medida >= minimo)
        if alcanza:
            indice = max(indice, posicion)
    return SULFATOS[indice]


def _exposicion_quimica_validada() -> dict:
    """
    El dato de sitio 'exposicion_quimica_ems', comprobado ANTES de usarlo.

    POR QUE EXISTE ESTA FUNCION, y por que no basta con `.get()`. La version
    anterior leia `exposicion.get("cloruros_tabla_4_2")`: una clave AUSENTE
    daba None, None es falso, y el calculo seguia como si el EMS hubiera
    dicho "no hay cloruros". Con eso desaparecian en silencio la a/c <= 0.40
    y el f'c >= 35 MPa de esa fila -- que son justamente las exigencias que
    el expediente venia afirmando en prosa y que este cluster convirtio en
    dato. La ausencia de una lectura NO es una lectura negativa: es
    DatoInvalidoError, y el revisor tiene que anadir el analisis que falta.

    Lo segundo que comprueba es la FORMA. Este dato es el unico de todo el
    expediente que no es un numero ni un rotulo, sino un diccionario, y la
    unica via por la que hoy se puede declarar desde la ventana produce
    float o str. Sin esta comprobacion, declararlo mal no daba un problema
    del expediente sino un AttributeError -- un fallo del programa, que es
    precisamente la distincion que la taxonomia de excepciones existe para
    mantener.
    """
    exposicion = ca.valor(CRITERIO_EXPOSICION_QUIMICA)
    if not isinstance(exposicion, dict):
        raise DatoInvalidoError(
            campo=CRITERIO_EXPOSICION_QUIMICA, valor=exposicion,
            motivo="el analisis quimico del EMS se declara como un "
                   "diccionario con las claves "
                   + ", ".join(CLAVES_ESCALAS_SULFATOS)
                   + f" y {CLAVE_FILAS_TABLA_4_2}",
        )
    for clave in CLAVES_ESCALAS_SULFATOS:
        if clave not in exposicion:
            raise DatoInvalidoError(
                campo=CRITERIO_EXPOSICION_QUIMICA, valor=exposicion,
                motivo=f"falta la escala '{clave}' de la Tabla 4.4. Las dos "
                       f"escalas son alternativas y una puede venir en None, "
                       f"pero las dos claves tienen que estar declaradas: "
                       f"omitir una no es decir que no se midio",
            )
        medida = exposicion[clave]
        if medida is not None and (isinstance(medida, bool)
                                   or not isinstance(medida, (int, float))):
            raise DatoInvalidoError(
                campo=CRITERIO_EXPOSICION_QUIMICA, valor=medida,
                motivo=f"'{clave}' es una magnitud medida y tiene que ser un "
                       f"numero o None",
            )
    filas = exposicion.get(CLAVE_FILAS_TABLA_4_2)
    if not isinstance(filas, dict):
        raise DatoInvalidoError(
            campo=CRITERIO_EXPOSICION_QUIMICA, valor=filas,
            motivo=f"falta '{CLAVE_FILAS_TABLA_4_2}': las tres filas de la "
                   f"Tabla 4.2 se declaran como si/no en un diccionario",
        )
    for clave in EXPOSICION_ESPECIAL:
        if clave not in filas:
            raise DatoInvalidoError(
                campo=CRITERIO_EXPOSICION_QUIMICA, valor=filas,
                motivo=f"falta la fila '{clave}' de la Tabla 4.2. Se declaran "
                       f"LAS TRES porque la nota al pie manda tomar la menor "
                       f"relacion a/c APLICABLE, y aplicable no se puede "
                       f"evaluar sobre un conjunto incompleto",
            )
        if not isinstance(filas[clave], bool):
            raise DatoInvalidoError(
                campo=CRITERIO_EXPOSICION_QUIMICA, valor=filas[clave],
                motivo=f"la fila '{clave}' de la Tabla 4.2 aplica o no "
                       f"aplica: se declara True o False",
            )
    sobrantes = set(filas) - set(EXPOSICION_ESPECIAL)
    if sobrantes:
        raise DatoInvalidoError(
            campo=CRITERIO_EXPOSICION_QUIMICA, valor=sorted(sobrantes),
            motivo="la Tabla 4.2 tiene tres filas y no mas: "
                   + ", ".join(sorted(EXPOSICION_ESPECIAL)),
        )
    return exposicion


def _extremo_declarado(candidatos, funcion):
    """
    El extremo de una lista de (valor, fuente), con TODAS las fuentes que lo
    alcanzan, no solo una.

    Antes esto era `min(candidatos)` sobre tuplas, y con dos tablas empatadas
    en el valor el desempate lo decidia la comparacion alfabetica del nombre
    de la fuente. Ninguna de las dos tablas es "menor" que la otra: si las
    dos imponen el mismo limite, las dos gobiernan, y eso es lo que la
    memoria tiene que decir.
    """
    if not candidatos:
        return None, "-"
    extremo = funcion(valor for valor, _ in candidatos)
    fuentes = [fuente for valor, fuente in candidatos
               if abs(valor - extremo) <= TOL_UMBRAL_NORMATIVO]
    return extremo, " y ".join(fuentes)


def requisitos_durabilidad_concreto() -> RequisitosDurabilidad:
    """
    Relacion a/c maxima y f'c minimo del concreto, combinando las Tablas 4.2 y
    4.4 de E.060 con la nota al pie que las dos llevan:

        "Cuando se utilicen las Tablas 4.2 y 4.4 simultaneamente, se debe
        utilizar la MENOR relacion maxima agua-material cementante aplicable
        y el MAYOR f'c minimo"

    Es el eslabon que faltaba entero (NOR-E060-06): el expediente tenia las
    dos tablas transcritas y ninguna regla que las cruzara, de modo que en un
    sitio con sulfatos Y cloruros -- este -- no habia forma de decir que
    relacion a/c se especifica. Y de esa relacion a/c cuelga el recubrimiento,
    por el modificador del Art. 5.10.1 de AASHTO.

    QUE NUMERAL MANDA APLICAR LA TABLA 4.2, que la cadena habia perdido: el
    Art. 4.4.2 (pag. impresa 39), verificado contra el PDF. "Cuando el
    concreto con refuerzo vaya a estar expuesto a cloruros de quimicos
    descongelantes, sal, agua salobre, agua de mar o salpicaduras de las
    mismas, deben cumplirse los requisitos de la Tabla 4.2 para la maxima
    relacion agua-material cementante y valor minimo de f'c, Y LOS REQUISITOS
    DE RECUBRIMIENTO MINIMO DEL CONCRETO DE 7.7". Es el articulo que ata este
    cluster entero -- exposicion quimica, relacion a/c y recubrimiento en una
    sola frase --, y una version anterior de este cluster lo habia sacado de
    la cadena de numerales creyendo que citarlo era un error.

    LAS TRES FILAS DE LA TABLA 4.2 SE MIRAN, no solo la de cloruros. "La
    MENOR relacion a/c aplicable" es una comparacion, y una comparacion a la
    que le falta un candidato da el resultado equivocado sin avisar.

    Consume el dato de sitio 'exposicion_quimica_ems' ([S], pendiente de
    ensayo): sin el analisis quimico del EMS, `CriterioPendienteError` y el
    calculo se detiene. No hay lectura por defecto -- la afirmacion "corredor
    salino" viajaba en prosa por varias justificaciones y no era un dato.
    """
    exposicion = _exposicion_quimica_validada()
    fila = clase_exposicion_sulfatos(
        so4_suelo_pct=exposicion[CLAVES_ESCALAS_SULFATOS[0]],
        so4_agua_ppm=exposicion[CLAVES_ESCALAS_SULFATOS[1]])

    candidatos_ac = []
    candidatos_fc = []
    if fila["a_c_max"] is not None:
        candidatos_ac.append((fila["a_c_max"], NOMBRE_TABLA_4_4))
    if fila["fc_min_MPa"] is not None:
        candidatos_fc.append((fila["fc_min_MPa"], NOMBRE_TABLA_4_4))
    # LAS TRES FILAS DE LA TABLA 4.2, no solo la de cloruros. "La MENOR
    # relacion a/c APLICABLE" no se puede evaluar sobre un conjunto que el
    # dato deja a medias: si el concreto ademas debe ser de baja
    # permeabilidad, esa fila es aplicable y tiene que entrar a la
    # comparacion. El dato declara las tres, y aqui entran las que aplican.
    for clave, aplica in exposicion[CLAVE_FILAS_TABLA_4_2].items():
        if not aplica:
            continue
        requisito = EXPOSICION_ESPECIAL[clave]
        etiqueta = f"{NOMBRE_TABLA_4_2} ({clave})"
        candidatos_ac.append((requisito["a_c_max"], etiqueta))
        candidatos_fc.append((requisito["fc_min_MPa"], etiqueta))

    # La nota al pie, aplicada: MENOR a/c y MAYOR f'c de los aplicables.
    a_c_max, gobierna_a_c = _extremo_declarado(candidatos_ac, min)
    fc_min, gobierna_fc = _extremo_declarado(candidatos_fc, max)

    return RequisitosDurabilidad(
        a_c_max=a_c_max, fc_min_MPa=fc_min,
        clase_sulfatos=fila["exposicion"],
        gobierna_a_c=gobierna_a_c, gobierna_fc=gobierna_fc,
        cementos_admisibles=fila["cementos"],
        numeral=f"{NUMERAL_PROTECCION_CORROSION} / "
                f"{NUMERAL_EXPOSICION_ESPECIAL} / {NUMERAL_SULFATOS} / "
                f"{NUMERAL_COMBINACION_4_2_4_4}",
    )


def factor_recubrimiento_por_ac(*, a_c_max: Optional[float]) -> Tuple[float, str]:
    """
    Modificador del recubrimiento por relacion agua-cemento, con su origen.

        W/C <= 0.40  ->  0.8        W/C >= 0.50  ->  1.2

    El Art. 5.10.1 de AASHTO no deja la tabla de recubrimientos en bruto:
    "Cover ... shall not be less than that specified in Table 5.10.1-1 AND
    MODIFIED FOR W/CM RATIO". El Manual de Puentes trae los mismos factores en
    su num. 2.9.1.5.5.3. El criterio los ignoraba enteros, y son los que
    invierten la conclusion de la regla del mayor (NOR-AAS-05).

    QUE a/c ENTRA AQUI: la MAXIMA que la durabilidad permite, no la del diseno
    de mezcla. Es la eleccion conservadora de las dos -- una a/c mas alta da
    factor mas alto y por tanto MAS recubrimiento --, y ademas es la unica que
    el expediente conoce en fase de perfil.

    SIN LIMITE DE DURABILIDAD (`a_c_max=None`, exposicion insignificante y
    ninguna fila de la Tabla 4.2 aplicable) no hay a/c contra la que evaluar
    el modificador. No se inventa una: se aplica el factor MAS exigente de la
    tabla, 1.2, y la funcion lo declara en el origen que devuelve. Ese origen
    VIAJA hasta la memoria (`RecubrimientoDiseno.origen_factor`), porque del
    numero solo no se distingue esta situacion de un expediente cuya a/c
    maxima si es 0.50: son dos cosas distintas y la segunda es un dato,
    mientras la primera es una acotacion del calculo.

    LA BANDA INTERMEDIA no se resuelve aqui con un literal. El Manual de
    Puentes no imprime factor para 0.40 < a/c < 0.50 y AASHTO si; ese hueco
    es un [C] declarado ('factor_recubrimiento_banda_intermedia_ac'), no un
    1.0 escrito en este modulo por parecer neutro. Y la banda es alcanzable:
    con sulfatos severos y sin cloruros la a/c maxima resulta 0.45.
    """
    if a_c_max is None:
        return (max(RECUBRIMIENTO_MP_FACTOR_AC.values()),
                "conservador: ninguna de las dos tablas de E.060 limita la "
                "relacion a/c, y se aplica el factor mas exigente")
    if a_c_max <= RECUBRIMIENTO_AC_UMBRAL_BAJO + TOL_UMBRAL_NORMATIVO:
        return (RECUBRIMIENTO_MP_FACTOR_AC["a_c_menor_igual_0_40"],
                f"a/c maxima {a_c_max} <= 0.40")
    if a_c_max >= RECUBRIMIENTO_AC_UMBRAL_ALTO - TOL_UMBRAL_NORMATIVO:
        return (RECUBRIMIENTO_MP_FACTOR_AC["a_c_mayor_igual_0_50"],
                f"a/c maxima {a_c_max} >= 0.50")
    return (ca.valor(CRITERIO_FACTOR_BANDA_AC),
            f"a/c maxima {a_c_max} en la banda intermedia (0.40 < a/c < "
            f"0.50): el Manual de Puentes no imprime factor para esta banda "
            f"y el hueco lo cubre el criterio [C] "
            f"'{CRITERIO_FACTOR_BANDA_AC}' con el valor de AASHTO LRFD "
            f"Art. 5.10.1")


def recubrimiento_aashto_mm(*, condicion: str) -> float:
    """
    Lado AASHTO / Manual de Puentes de la regla del mayor, en mm, para la
    condicion de E.060 que se le pase. Ya NO es un valor declarado: se
    CALCULA, y por eso puede detenerse.

        tabulado      = max( tabla_aashto[situacion][categoria] ,
                             tabla_manual[fila equivalente] )   # solo cat. A
        recubrimiento = max( tabulado * factor_ac , piso de 1.0 in )

    Los tres eslabones y de donde sale cada uno:

      situacion   'situacion_recubrimiento_aashto' [A]: que fila de la tabla
                  se pone enfrente de cada condicion de E.060. Las dos tablas
                  no se indexan igual -- E.060 por diametro de barra, AASHTO
                  por severidad de exposicion -- y el emparejamiento no lo
                  dice ninguna de las dos normas.
      categoria   'categoria_refuerzo_aashto' [A], VACIO: la columna A/B/C.
                  Es la condicion de aplicacion que el expediente nunca
                  declaro (NOR-AAS-01) y la que puede invertir quien gobierna.
      factor_ac   modificador del Art. 5.10.1, via la durabilidad del
                  concreto, que a su vez cuelga del analisis quimico del EMS.

    DE QUE CORPUS SALE EL NUMERO, que la memoria tiene que declarar: con
    categoria A el valor es [N] peruano -- el Manual de Puentes transcribe esa
    columna en su Tabla 2.9.1.5.5.3-1, cuyo titulo dice "aceros no
    protegidas" -- y con B o C el corpus peruano no tabula nada para
    exposicion exterior y el hueco lo cubre AASHTO LRFD 9a ed. como [C], por
    la Via 1 de Sec. 0.2.
    """
    if condicion not in RECUBRIMIENTO:
        raise DatoInvalidoError(
            campo="condicion", valor=condicion,
            motivo="no es una fila del Art. 7.7.1: " + ", ".join(sorted(RECUBRIMIENTO)),
        )
    return _recubrimiento_aashto_detallado(condicion=condicion)[0]


def _recubrimiento_aashto_detallado(*, condicion: str) -> Tuple[float, dict]:
    """El valor y la cadena que lo produjo, para que la memoria la imprima."""
    situaciones = ca.valor(CRITERIO_SITUACION_RECUBRIMIENTO)
    if condicion not in situaciones:
        raise DatoInvalidoError(
            campo="condicion", valor=condicion,
            motivo=f"no tiene fila emparejada en "
                   f"'{CRITERIO_SITUACION_RECUBRIMIENTO}'",
        )
    situacion = situaciones[condicion]
    tabla = ca.valor(CRITERIO_TABLA_RECUBRIMIENTO)
    if situacion not in tabla:
        raise DatoInvalidoError(
            campo="situacion", valor=situacion,
            motivo=f"no es una fila de la Tabla 5.10.1-1 transcrita en "
                   f"'{CRITERIO_TABLA_RECUBRIMIENTO}'",
        )
    categoria = ca.valor(CRITERIO_CATEGORIA_REFUERZO)   # VACIO: detiene aqui
    if categoria not in tabla[situacion]:
        raise DatoInvalidoError(
            campo=CRITERIO_CATEGORIA_REFUERZO, valor=categoria,
            motivo="las categorias de la Tabla 5.10.1-1 son "
                   + ", ".join(sorted(tabla[situacion])),
        )

    tabulado = float(tabla[situacion][categoria])
    filas_mp = RECUBRIMIENTO_MP_EQUIVALENCIA.get(situacion)
    if filas_mp is None:
        # NO se sigue adelante saltandose el cruce. Una fila sin
        # correspondencia declarada significa que las dos transcripciones se
        # han desincronizado, y seguir seria calcular el recubrimiento con
        # una sola de las dos fuentes creyendo que se compararon.
        raise DatoInvalidoError(
            campo="situacion", valor=situacion,
            motivo="no tiene fila equivalente declarada en "
                   "RECUBRIMIENTO_MP_EQUIVALENCIA, y sin ella no se puede "
                   "cruzar la tabla de AASHTO con la del Manual de Puentes",
        )
    if categoria == CATEGORIA_ACERO_SIN_RECUBRIR:
        # El corpus peruano TABULA esta columna, asi que el valor sale de el y
        # no de AASHTO: es lo que pedia NOR-PUE-10, y no basta con nombrarlo en
        # la etiqueta. Se toma el mayor por la misma regla de conflicto de
        # Sec. 0.2 -- hoy coinciden en las 21 filas, y si alguna edicion las
        # separa, la regla ya esta escrita y no hay que decidir en caliente.
        #
        # EL CRUCE SE HACE POR MAPA Y NO POR NOMBRE DE CLAVE. Antes la guarda
        # era `situacion in RECUBRIMIENTO_MP_MM`, y en las 8 filas de la
        # familia de pilotes -- donde el Manual traduce "shafts" por "Pilares"
        # y ademas parte en dos la fila de ambiente corrosivo -- daba False:
        # el cruce se saltaba sin avisar y la red de seguridad cubria 14 filas
        # de 21 mientras el comentario afirmaba que las cubria todas.
        tabulado = max([tabulado]
                       + [float(RECUBRIMIENTO_MP_MM[fila])
                          for fila in filas_mp])
    requisitos = requisitos_durabilidad_concreto()
    factor, origen_factor = factor_recubrimiento_por_ac(
        a_c_max=requisitos.a_c_max)
    modificado = tabulado * factor
    # Piso absoluto sobre las barras principales: 1.0 in. Es lo que impide que
    # el 0.8 lleve el recubrimiento por debajo de la pulgada.
    piso_aplicado = modificado < RECUBRIMIENTO_MP_PISO_MM - TOL_UMBRAL_NORMATIVO
    valor = max(modificado, RECUBRIMIENTO_MP_PISO_MM)
    corpus = ("[N] Manual de Puentes Tabla 2.9.1.5.5.3-1 (aceros no "
              "protegidos), coincidente con AASHTO LRFD Tabla 5.10.1-1 "
              "columna A"
              if categoria == CATEGORIA_ACERO_SIN_RECUBRIR else
              "[C] AASHTO LRFD Tabla 5.10.1-1 columna " + str(categoria)
              + ": el Manual de Puentes no CALLA sobre el acero protegido "
                "-- su num. 2.9.1.5.5.4 lo trata --, pero solo autoriza usar "
                "la tabla con acero protegido 'Para exposicion interior'. "
                "Fuera de ella el corpus peruano no tabula, y el hueco lo "
                "cubre AASHTO por la Via 1 de Sec. 0.2. Es una lectura "
                "declarada, no neutra: la contraria mantendria la columna de "
                "aceros no protegidos y esta en la sensibilidad de "
                "'" + CRITERIO_CATEGORIA_REFUERZO + "'")
    detalle = {"situacion": situacion, "categoria": categoria,
               "tabulado_mm": tabulado, "factor_ac": factor,
               "origen_factor": origen_factor, "piso_aplicado": piso_aplicado,
               "corpus": corpus, "requisitos": requisitos,
               "filas_mp": filas_mp}
    return valor, detalle


def recubrimiento_de_diseno(*, condicion: str) -> RecubrimientoDiseno:
    """
    Regla de conflicto de Sec. 0.2: **rige el recubrimiento MAYOR entre AASHTO
    y E.060**. Devuelve los dos operandos, el adoptado, cual de las dos normas
    gobierna, y la cadena con que se produjo el lado AASHTO.

    Por que no basta con tomar el de E.060. Sec. 0.2 adopta la Via 1 (AASHTO
    LRFD de extremo a extremo) y declara la durabilidad como EXCEPCION: E.060
    entra, pero no desplaza a AASHTO, se compara con el. Una regla del maximo
    evaluada con un solo operando no es una regla -- por eso esta funcion
    exige los dos lados.

    QUE CAMBIO Y POR QUE (cluster C07; conflicto #3 del plan de correcciones).
    El lado AASHTO era un valor declarado, 75 mm en las tres condiciones, con
    la conclusion ya escrita: "AASHTO gobierna en los tres casos". Los 75 mm
    eran los 3.0 in de la columna A redondeados a la baja, sin el modificador
    por relacion a/c y sin decir que habia tres columnas. Con la cadena
    completa la conclusion deja de valer para las tres.

    EL RESULTADO, CONDICION POR CONDICION, para que nadie lo lea como una
    inversion general que no es. Con categoria A y el factor 0.8 de
    a/c <= 0.40, el lado AASHTO vale 76.2 x 0.8 = 61.0 mm en las tres:

        contra_suelo             E.060 70.0  AASHTO 61.0  ->  gobierna E.060
        suelo_intemperie_ge_3_4  E.060 50.0  AASHTO 61.0  ->  gobierna AASHTO
        suelo_intemperie_le_5_8  E.060 40.0  AASHTO 61.0  ->  gobierna AASHTO

    Es decir: la inversion ocurre en UNA de las tres condiciones -- la
    principal, la del concreto vaciado contra el suelo -- y en las otras dos
    AASHTO sigue gobernando, con 61.0 mm en vez de los 75 mm de antes.
    Corregir solo 75 -> 76.2, que era la correccion obvia que el conflicto #3
    prohibe, habria dejado la conclusion falsa con un numero mas exacto.

    EL EFECTO NETO, que conviene decir en voz alta: el recubrimiento adoptado
    BAJA en las tres condiciones respecto del expediente anterior (75 mm ->
    70.0 / 61.0 / 61.0). Es lo que la norma exige una vez aplicado el
    modificador que faltaba, y no es una holgura ganada: cuando la fila de
    cloruros de la Tabla 4.2 aplica, el Art. 4.4.2 remite al recubrimiento de
    7.7 y el Art. 7.7.5.1 manda AUMENTAR este minimo -- ver
    `aviso_ambiente_corrosivo`, que consume el mismo dato y lo dice sin
    condicional cuando el dato ya esta declarado.

    E.060 Art. 7.7.5.1 (ambiente corrosivo) manda AUMENTAR este resultado y no
    dice cuanto; ese aumento se declara aparte (`aviso_ambiente_corrosivo`).
    """
    e060 = recubrimiento_e060_mm(condicion=condicion)
    aashto, detalle = _recubrimiento_aashto_detallado(condicion=condicion)
    if aashto > e060 + TOL_UMBRAL_NORMATIVO:
        adoptado, origen = aashto, "AASHTO"
    else:
        adoptado, origen = e060, "E.060"
    return RecubrimientoDiseno(
        paso=_paso_recubrimiento(condicion=condicion, e060=e060, aashto=aashto,
                                 adoptado=adoptado, origen=origen,
                                 detalle=detalle),
        condicion=condicion, e060_mm=e060, aashto_mm=aashto,
        adoptado_mm=adoptado, origen=origen,
        criterio_aashto=CRITERIO_TABLA_RECUBRIMIENTO,
        numeral=f"{NUMERAL_RECUBRIMIENTO} / {NUMERAL_RECUBRIMIENTO_MP} / "
                f"{NUMERAL_REGLA_RECUBRIMIENTO}",
        situacion=detalle["situacion"], categoria=detalle["categoria"],
        tabulado_mm=detalle["tabulado_mm"], factor_ac=detalle["factor_ac"],
        piso_aplicado=detalle["piso_aplicado"], corpus_tabla=detalle["corpus"],
        origen_factor=detalle["origen_factor"],
        requisitos=detalle["requisitos"],
    )


def _paso_recubrimiento(*, condicion, e060, aashto, adoptado, origen,
                        detalle):
    """
    El paso de memoria del recubrimiento, con la regla del mayor a la vista.

    LA ELECCION QUE HAY QUE IMPRIMIR NO ES «cuanto recubrimiento»: es DE QUE
    CORPUS sale. Los dos regulan la misma pieza y ninguno deroga al otro, de
    modo que un revisor que vea «70 mm» sin ver el otro numero no puede saber
    si se cumplieron las dos normas o solo una. Es ademas la casilla donde el
    modificador por relacion a/c invierte la conclusion (NOR-AAS-05, conflicto
    vinculante n.3 del plan v12): sin el, AASHTO gobernaba las tres
    condiciones; con el, E.060 gana una.
    """
    return paso(
        "F8.RECUBRIMIENTO",
        codigo="8.R",
        que="Recubrimiento del refuerzo, por la regla del mayor",
        formula="recubrimiento = max(E.060 Art. 7.7.1, AASHTO 5.10.1 con su "
                "modificador por relacion a/c)",
        formula_cita_id="E060.7.7.1",
        citas_textuales=("E060.7.7.1", "AASHTO_LRFD_9.T5.10.1-1"),
        sustitucion=(
            Magnitud("E.060", e060, "mm",
                     f"Art. 7.7.1, condicion «{condicion}»",
                     cifras=CIFRAS_FACTOR),
            Magnitud("AASHTO", aashto, "mm",
                     f"{detalle['corpus']}, fila «{detalle['situacion']}», "
                     f"categoria {detalle['categoria']}: "
                     f"{detalle['tabulado_mm']} mm tabulados x factor "
                     f"{detalle['factor_ac']} por relacion a/c",
                     cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("recubrimiento adoptado", adoptado, "mm",
                           f"el mayor de los dos; gobierna {origen}",
                           cifras=CIFRAS_FACTOR),
        umbral=Umbral(
            descripcion="recubrimiento minimo del refuerzo",
            valor=adoptado, unidad="mm",
            cita_id="E060.7.7.1",
            caracter="EXIGENCIA en los dos corpus",
            aplicacion="REGLA DEL MAYOR (Sec. 0.2): cumplir el menor de los "
                       "dos dejaria el otro incumplido. Este numero es el "
                       "MINIMO ANTES del aumento por ambiente corrosivo que "
                       "el Art. 7.7.5.1 manda y no cuantifica; ese aumento se "
                       "declara aparte y no se calcula aqui.",
            criterio_aplicado=CRITERIO_TABLA_RECUBRIMIENTO),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.CUMPLE,
            margen=abs(aashto - e060), unidad="mm",
            explicacion=f"gobierna {origen}; la diferencia entre los dos "
                        f"corpus es la holgura con que se cumple el que no "
                        f"gobierna"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="corpus normativo que gobierna el recubrimiento",
            valor=f"{origen}, {adoptado} mm",
            entre=(f"E.060 Art. 7.7.1: {e060} mm",
                   f"AASHTO 5.10.1: {aashto} mm"),
            de_donde="la regla del mayor de la Sec. 0.2 del expediente",
            por_que=detalle["origen_factor"] or
                    "los dos corpus regulan la misma pieza y ninguno deroga "
                    "al otro",
            cita_id="AASHTO_LRFD_9.T5.10.1-1",
            clave_criterio=CRITERIO_TABLA_RECUBRIMIENTO),),
    )


def aviso_ambiente_corrosivo() -> str:
    """
    Aviso para la memoria: el recubrimiento de `recubrimiento_de_diseno` es el
    MINIMO antes del aumento por ambiente corrosivo. El aumento no se calcula
    aqui, se declara -- E.060 Art. 7.7.5.1 no fija cuanto.

    DOS CORRECCIONES DE CITA (NOR-E060-04). La primera, la forma verbal: el
    articulo imprime "debe aumentarse adecuadamente", no "aumentar
    adecuadamente", y entrecomillar lo segundo es citar mal aunque el fondo
    coincida. La segunda pesa mas: el articulo ofrece una ALTERNATIVA expresa
    -- "o debe disponerse de otro tipo de proteccion" -- que el aviso omitia,
    y que es un camino de cumplimiento distinto del que el expediente
    contempla. Con la alternativa a la vista, proteger el refuerzo (la
    categoria B o C de 'categoria_refuerzo_aashto') deja de ser solo una
    opcion de suministro y pasa a ser una forma de cumplir este articulo.
    Por eso el aviso transcribe el texto entero y no lo resume.

    Y EL AVISO EVALUA SU PROPIO ANTECEDENTE, que es lo que le faltaba. Decia
    "si el analisis quimico del EMS confirma la exposicion" -- un condicional
    cuyo antecedente el programa YA tiene resuelto en el mismo dato del que
    cuelga el factor por a/c. Dejarlo en potencial tenia una consecuencia
    concreta: en la misma corrida en que el modificador BAJA el recubrimiento
    adoptado, el aumento que la norma manda aplicar quedaba en prosa
    condicional. El Art. 4.4.2 cierra el circulo -- expuesto a cloruros ->
    Tabla 4.2 Y "los requisitos de recubrimiento minimo del concreto de 7.7"
    --, y el Art. 7.7.1 abre con la salvedad "excepto cuando se requieran
    recubrimientos mayores segun 7.7.5.1".
    """
    exposicion = _exposicion_quimica_validada()
    aplica = exposicion[CLAVE_FILAS_TABLA_4_2]["cloruros"]
    if aplica:
        cabecera = (
            "Recubrimiento: el valor adoptado es el MINIMO y HAY QUE "
            f"AUMENTARLO ({AMBIENTE_CORROSIVO_AUMENTAR}). No es un supuesto: "
            "el analisis quimico declarado en "
            f"'{CRITERIO_EXPOSICION_QUIMICA}' dice que el concreto queda "
            "expuesto a los cloruros de la Tabla 4.2, y con eso el "
            f"{NUMERAL_PROTECCION_CORROSION} manda cumplir tambien \""
            f"{PROTECCION_CORROSION_TEXTO}\". ")
    else:
        cabecera = (
            "Recubrimiento: el analisis quimico declarado en "
            f"'{CRITERIO_EXPOSICION_QUIMICA}' NO da por expuesto el concreto "
            "a los cloruros de la Tabla 4.2, de modo que el aumento de este "
            "articulo no se dispara por esa via. Queda anotado porque el "
            "ambiente corrosivo no se agota en los cloruros de esa fila. ")
    return (
        cabecera
        + f"Texto literal del articulo: \"{AMBIENTE_CORROSIVO_TEXTO}\". No "
        "fija cuanto, y ofrece la alternativa de disponer otro tipo de "
        "proteccion: las dos cosas se declaran en la memoria, no las calcula "
        "este modulo"
    )


# --- VE-6 (lote M9, item 29; ficha T7C-10) --- las cuantias minimas de muro
# de E.060 14.3.1 son el criterio [N→] 'cuantia_minima_muro_e060' (hasta
# VE-6, la constante [N] `CUANTIA_MIN_MURO`), y estas son sus dos claves.
CRITERIO_CUANTIA_MIN_MURO = "cuantia_minima_muro_e060"


DIRECCIONES_CUANTIA_MURO = ("horizontal", "vertical")


def cuantia_minima(*, direccion: str) -> float:
    """
    Cuantia minima de refuerzo de muro, E.060 Art. 14.3.1 (pag. 133):
    horizontal >= 0.0020, vertical >= 0.0015. Desde VE-6 la lee del
    criterio [N→] 'cuantia_minima_muro_e060': E.060 es norma de
    edificaciones y aplicarla al cabezal de una obra vial es una analogia
    (ficha T7C-10).

    Es un MINIMO OBLIGATORIO, no un dato informativo. Sec. 9.4 lo llama
    "REFERENCIA de cuantias minimas" y el matiz es real pero no significa lo
    que parece: por la Via 1 de Sec. 0.2 el DISENO estructural es de AASHTO
    LRFD Sec. 5, de modo que E.060 no dicta cuanto acero pide la flexion. Lo
    que si hace el Art. 14.3.1, dentro de E.060, es fijar un piso, gobierne
    quien gobierne el dimensionamiento. La consecuencia practica esta en
    `cuantia_de_diseno`: el minimo se aplica como rho_diseno =
    max(rho_calculado, rho_minimo), no se imprime al pie de la memoria.

    LO QUE ESTE DOCSTRING AFIRMABA DE MAS (NOR-E060-01). Decia que el 14.3.1
    fija "un piso por debajo del cual NINGUN muro se arma". Para un muro de
    CONTENCION -- que es lo que el cabezal es -- eso no es lo que dice E.060:
    el Art. 14.8.2 remite a 14.3 y acto seguido permite exceptuarlo, "cuando
    el Ingeniero Proyectista disponga juntas de contraccion y señale
    procedimientos constructivos que controlen los efectos de contraccion y
    temperatura". La excepcion es potestativa y exige las DOS cosas a la vez.
    Este proyecto NO la invoca -- no hay juntas de contraccion ni
    procedimientos constructivos declarados en el expediente -- y por eso el
    minimo se aplica entero. Lo que cambia es el argumento: se aplica porque
    nadie ejercio la excepcion, no porque la norma no la ofrezca. La
    diferencia importa el dia que el proyectista quiera ejercerla:
    `nota_excepcion_refuerzo_minimo` le dice que tiene que declarar para eso.

    Los pisos del regimen de cortante EN EL PLANO (11.10.10.2 horizontal,
    ec. 11-32 del 11.10.10.3 vertical) y la pregunta previa del plano
    (11.10.2 / 11.10.1): ver `cuantia_de_diseno` y los criterios
    'regimen_cortante_muro_e060_art_11_10_2',
    'cortante_alto_muro_e060_art_11_10_10_2' y
    'cuantia_vertical_cortante_alto_e060_art_11_10_10_3'. Este modulo NO
    calcula cortante, y por eso los tres quedan declarados como vacios y no
    resueltos en silencio.
    """
    if direccion not in DIRECCIONES_CUANTIA_MURO:
        raise DatoInvalidoError(
            campo="direccion", valor=direccion,
            motivo="las direcciones del Art. 14.3.1 son "
                   + ", ".join(sorted(DIRECCIONES_CUANTIA_MURO)),
        )
    tabla = ca.valor(CRITERIO_CUANTIA_MIN_MURO)
    rho = tabla.get(direccion) if hasattr(tabla, "get") else None
    if not (_finito(rho) and rho > 0):
        raise DatoInvalidoError(
            campo=CRITERIO_CUANTIA_MIN_MURO, valor=tabla,
            motivo="se espera un dict con 'horizontal' y 'vertical', cada "
                   "una una cuantia positiva")
    # --- dictamen Fable de VE-6 --- con etiqueta [N→] el criterio APLICA la
    # norma: un valor por debajo del de 14.3.1 la bajaria, y se rechaza
    # (bajar el minimo es ejercer 14.8.2, que se declara aparte).
    norma = CUANTIA_MIN_MURO_E060_14_3_1[direccion]
    if rho < norma - TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            campo=CRITERIO_CUANTIA_MIN_MURO, valor=tabla,
            motivo=f"la cuantia {direccion} ({rho:g}) baja del minimo de "
                   f"E.060 14.3.1 ({norma:g}) que el criterio [N→] aplica; "
                   "exceptuarlo es ejercer 14.8.2")
    return float(rho)


def nota_excepcion_refuerzo_minimo() -> str:
    """
    La frase para la memoria: el minimo de E.060 Art. 14.3.1 se aplica entero
    porque el proyecto no ejercio la excepcion que el Art. 14.8.2 ofrece para
    muros de contencion, no porque la norma no la tenga.

    Sin esta nota, la memoria presentaba el minimo como inexcusable, que es
    afirmar de la norma algo que la norma no dice (NOR-E060-01). Con ella, el
    revisor ve las dos cosas: el numero que se aplico y la puerta que existia
    y no se uso.
    """
    return (
        "Cuantia minima de refuerzo del muro: se aplica integra la de "
        f"{NUMERAL_CUANTIA_MIN}. El {NUMERAL_EXCEPCION_REFUERZO_MIN_MURO} "
        f"permite exceptuarla en muros de contencion -- \"{EXCEPCION_REFUERZO_MIN_MURO_TEXTO}\" "
        "--, y este expediente NO ejerce esa excepcion: no declara juntas de "
        "contraccion ni procedimientos constructivos de control de "
        "contraccion y temperatura, que son las dos condiciones que el "
        "articulo exige a la vez. Ejercerla es una decision del proyectista y "
        "obliga a declarar las dos en el expediente"
    )


def _minimo_de_cuantia_aplicable(*, direccion: str,
                                 cortante_alto: bool) -> Tuple[float, str,
                                                              Optional[str],
                                                              Optional[str]]:
    """
    El minimo que rige en una direccion, y de donde sale: (minimo, numeral,
    clave del criterio que lo DECIDIO -- desde VE-6, sin cortante alto, el
    [N→] 'cuantia_minima_muro_e060'; hasta VE-6 era None, [N] puro --, regimen
    declarado o None si la ficha no se abrio). Con cortante perpendicular el
    numero es el del 14.3.1 y aun asi la clave es la del regimen: lo eligio
    una declaracion, no la norma sola. Es el unico sitio donde se contesta la
    pregunta, para que `verificar_cuantia` y `cuantia_de_diseno` no puedan
    contestarla distinto (EXT-M-05).

    Sin cortante alto: Art. 14.3.1, por analogia [N→]. Con cortante alto, en este
    orden y deteniendose en el primer vacio:

      1. EN QUE PLANO actua el cortante ('regimen_cortante_muro_e060_art_
         11_10_2'). E.060 11.10.2 restringe 11.10.3 a 11.10.10 al cortante
         EN EL PLANO del muro; 11.10.1 manda el perpendicular a las losas de
         11.12. Perpendicular: ni 11.10.10.2 ni .3 rigen, el minimo es el
         del 14.3.1 y el numeral lo dice.
      2. En el plano, el PISO de la direccion: horizontal, el 0.0025 del
         11.10.10.2 ('cortante_alto_muro_e060_art_11_10_10_2'); vertical, la
         ec. (11-32) del 11.10.10.3 ('cuantia_vertical_cortante_alto_e060_
         art_11_10_10_3'), que este software NO evalua -- faltan hm, lm y la
         rho_h requerida por 11.10.10.1 -- y por eso se declara.
    """
    minima = cuantia_minima(direccion=direccion)      # DatoInvalidoError si no es direccion
    if not cortante_alto:
        # --- VE-6 (ficha T7C-10) --- ya no es [N] puro: el minimo es el
        # criterio [N→] 'cuantia_minima_muro_e060', y se atribuye a el.
        return minima, NUMERAL_CUANTIA_MIN, CRITERIO_CUANTIA_MIN_MURO, None

    regimen = ca.valor(CRITERIO_REGIMEN_CORTANTE)     # CriterioPendienteError mientras falte
    if regimen not in REGIMENES_CORTANTE_MURO:
        # Segunda linea: la puerta (categoria) ya lo rechaza; aqui es un dato
        # del expediente que no puede ser (SIS-E-05 / ficha EXT-5-02).
        raise DatoInvalidoError(
            campo=CRITERIO_REGIMEN_CORTANTE, valor=regimen,
            motivo="las lecturas del plano del cortante son "
                   + ", ".join(REGIMENES_CORTANTE_MURO))
    if regimen == REGIMEN_CORTANTE_PERPENDICULAR:
        # El numero es el del 14.3.1, pero QUIEN LO DECIDIO fue la
        # declaracion [A] del regimen: se atribuye a ella, no a [N] puro
        # (auditoria adversarial de EXT-7).
        return (minima,
                f"{NUMERAL_CUANTIA_MIN} / {NUMERAL_CORTANTE_PERPENDICULAR}",
                CRITERIO_REGIMEN_CORTANTE, regimen)

    if direccion == "horizontal":
        clave, numeral = CRITERIO_CORTANTE_ALTO, NUMERAL_CORTANTE_ALTO
    else:
        clave, numeral = (CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO,
                          NUMERAL_CORTANTE_ALTO_VERTICAL)
    # CriterioPendienteError mientras el piso siga sin declarar. No hay rama
    # alternativa a proposito: sin el valor no se puede armar un muro en esta
    # condicion, y caer al 14.3.1 seria elegir el minimo menor en silencio.
    minima = float(ca.valor(clave))
    return minima, f"{NUMERAL_CUANTIA_MIN} / {numeral}", clave, regimen


def verificar_cuantia(*, cuantia_provista: float, direccion: str,
                      cortante_alto: bool) -> Verificacion:
    """
    R1 (horizontal) / R2 (vertical): contraste de la cuantia PROVISTA en el
    plano contra el minimo que rige en esa direccion: el de E.060 Art. 14.3.1
    o, con cortante alto EN EL PLANO del muro, el piso del regimen de
    11.10.10 (11.10.10.2 horizontal, ec. 11-32 del 11.10.10.3 vertical).

    `cortante_alto` NO tiene valor por defecto, por la misma razon que en
    `cuantia_de_diseno`: la pregunta se contesta una sola vez por muro y no
    la contesta esta funcion. Hasta EXT-7 este contraste ignoraba el
    argumento y comparaba siempre contra el 14.3.1, de modo que un armado
    vertical de 0.0020 «cumplia» bajo un regimen que le pide 0.0025.

    Es la comprobacion a posteriori, y no sustituye a `cuantia_de_diseno`:
    esta funcion detecta que un armado ya dibujado incumple el minimo, y
    aquella impide que el minimo se pierda al producir el armado. Las dos
    hacen falta -- la cuantia que llega aqui puede venir de un plano que
    nadie paso por `cuantia_de_diseno` -- y por eso las dos leen el minimo
    del mismo sitio, `_minimo_de_cuantia_aplicable`.
    """
    minima, numeral, criterio, _regimen = _minimo_de_cuantia_aplicable(
        direccion=direccion, cortante_alto=cortante_alto)
    codigo = "R1" if direccion == "horizontal" else "R2"
    return Verificacion(
        cumple=cuantia_provista >= minima - TOL_UMBRAL_NORMATIVO,
        numeral=numeral,
        valor_obtenido=cuantia_provista,
        valor_admisible=minima,
        criterio_aplicado=criterio,      # [N→] del 14.3.1, o el [A] que decidio
        codigo=codigo,
    )


def cuantia_de_diseno(*, cuantia_calculada: float, direccion: str,
                      cortante_alto: bool) -> CuantiaRefuerzo:
    """
    Cuantia de refuerzo ADOPTADA para una direccion del muro:

        rho_diseno = max(rho_calculado, rho_minimo)

    El minimo de E.060 Art. 14.3.1 (pag. 133) es un piso obligatorio y aqui
    es donde se aplica. Antes de esta funcion el modulo tenia el minimo
    transcrito y `verificar_cuantia` para contrastarlo, pero nada que lo
    levantara: un rho calculado por debajo del minimo salia del modulo tal
    cual, y el minimo aparecia en la memoria como una linea al pie. Una
    exigencia que solo se imprime no es una exigencia aplicada.

    `cortante_alto` NO tiene valor por defecto, y es deliberado. E.060 tiene
    dos regimenes de minimos -- el general del Art. 14.3.1 (0.0020 / 0.0015)
    y el de cortante en el plano de 11.10.10 -- y elegir el mas bajo porque
    es el unico que la hoja de ruta transcribia seria quedarse con el minimo
    menor por omision. Este modulo NO calcula cortante: el diseno por flexion
    y corte esta bloqueado entero en 'procedimiento_flexion_corte_aashto_sec5'
    (AASHTO LRFD Sec. 5, Via 1 de Sec. 0.2), asi que no hay Vu con que
    contestar la pregunta del 11.10.10.1. Se traslada a quien llama, que es
    quien tiene el diseno estructural delante:

        cortante_alto=False  el muro NO esta en la condicion de 11.10.10.1
                             (Vu > phi*Vc), y quien lo afirma lo justifica
                             en la memoria. Rige el 0.0020 / 0.0015 del
                             Art. 14.3.1.
        cortante_alto=True   se abre la cadena de abajo, que se DETIENE con
                             `CriterioPendienteError` en el primer vacio.

    LA CADENA CON CORTANTE ALTO, en el orden en que se pregunta (EXT-M-05,
    R95-031; v8 §9.4 enmendada en EXT-0):

      1. En que plano actua el cortante. E.060 11.10.2 aplica 11.10.3 a
         11.10.10 a las fuerzas cortantes EN EL PLANO del muro, y 11.10.1
         manda las PERPENDICULARES al plano a las disposiciones para losas
         de 11.12 (pag. 103). Un cabezal en voladizo bajo empuje de tierras
         trabaja perpendicular a su plano: si ese es el cortante, ni el
         11.10.10.2 ni el 11.10.10.3 rigen y el minimo es el del 14.3.1 en
         las DOS direcciones. Lo declara 'regimen_cortante_muro_e060_art_
         11_10_2', vacio: ninguna de las dos respuestas se da por defecto.
      2. En el plano, HORIZONTAL: el piso 0.0025 del 11.10.10.2, declarado
         en 'cortante_alto_muro_e060_art_11_10_10_2' (vacio).
      3. En el plano, VERTICAL: la ec. (11-32) del 11.10.10.3, rho_v =
         0.0025 + 0.5*(2.5 - hm/lm)*(rho_h - 0.0025) >= 0.0025, que no
         necesita superar la rho_h requerida por 11.10.10.1. Hasta EXT-7
         esta rama devolvia el 0.0015 del 14.3.1 -- 1.67 veces menos acero
         que el piso -- y este docstring afirmaba que el cortante alto no
         cambiaba el minimo vertical, que es lo contrario de lo que la norma
         dice (R95-031). La ecuacion NO se evalua aqui: faltan hm, lm (la
         geometria del cabezal no lleva longitud) y la rho_h requerida (sale
         de un Vu que no existe). Se declara evaluada fuera en
         'cuantia_vertical_cortante_alto_e060_art_11_10_10_3', vacio.

    `direccion` es 'horizontal' o 'vertical'. El resultado lleva el regimen
    declarado y la clave del criterio que fijo el minimo, para que la
    memoria diga en que plano actua el cortante y de donde salio el numero.
    """
    minima, numeral, criterio, regimen = _minimo_de_cuantia_aplicable(
        direccion=direccion, cortante_alto=cortante_alto)

    if cuantia_calculada >= minima - TOL_UMBRAL_NORMATIVO:
        adoptada, gobierna = cuantia_calculada, "calculo"
    else:
        adoptada, gobierna = minima, "minimo_normativo"

    return CuantiaRefuerzo(
        direccion=direccion,
        cuantia_calculada=cuantia_calculada,
        cuantia_minima=minima,
        cuantia_adoptada=adoptada,
        gobierna=gobierna,
        numeral=numeral,
        # Solo la clave del piso que SE LEYO; vacia si el minimo es el del
        # 14.3.1 (sin cortante alto, o con cortante perpendicular).
        criterio_cortante_alto=(
            criterio if criterio in (CRITERIO_CORTANTE_ALTO,
                                     CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO)
            else ""),
        regimen_cortante=regimen,
        criterio_regimen_cortante=(CRITERIO_REGIMEN_CORTANTE
                                   if cortante_alto else ""),
    )


def requiere_temperatura_dos_caras(*, espesor: float) -> bool:
    """
    True si hace falta acero por temperatura en AMBAS caras: espesor >= 0.250
    m (250 mm), E.060 Art. 14.8.3. Umbral INCLUSIVO ("mayor o igual a").
    `espesor` en metros.

    Este es el umbral del acero POR TEMPERATURA Y CONTRACCION, y solo de el.
    El del refuerzo en dos capas es otro y esta 50 mm mas abajo: ver
    `requiere_refuerzo_dos_capas`.
    """
    return espesor >= ESPESOR_TEMPERATURA_DOS_CARAS - TOL_UMBRAL_NORMATIVO


def requiere_refuerzo_dos_capas(*, espesor: float) -> bool:
    """
    True si el refuerzo va en DOS CAPAS en cada direccion: espesor > 0.200 m
    (200 mm), E.060 Art. 14.3.2. Umbral ESTRICTO ("mayor que"), a diferencia
    del de temperatura. `espesor` en metros.

    POR QUE EXISTE ESTA FUNCION (NOR-E060-02). El modulo decidia el acero en
    dos caras con un solo umbral, el de 250 mm del Art. 14.8.3, y la memoria
    imprimia "Acero por temperatura en UNA cara" para todo espesor menor. Pero
    E.060 tiene DOS umbrales sobre cosas distintas: el 14.3.2 exige el
    refuerzo "en cada direccion colocado en dos capas paralelas a las caras
    del muro" a partir de 200 mm -- con una sola excepcion, los muros de
    sotanos, que un cabezal no es --, y el 14.8.2 remite expresamente a todo
    14.3, de modo que un muro de contencion lo hereda. Entre 200 y 250 mm el
    muro lleva dos capas por 14.3.2 aunque el acero por temperatura vaya en
    una cara por 14.8.3, y la memoria decia lo contrario.
    """
    return espesor > ESPESOR_DOS_CAPAS_REFUERZO + TOL_UMBRAL_NORMATIVO


def nota_temperatura_dos_caras(*, espesor: float) -> str:
    """
    La frase para la memoria y el plano: en que cara o caras va el refuerzo,
    con su numeral. No es una verificacion con umbral contra un dato del
    proyecto -- son dos reglas de detalle que se disparan con el espesor -- y
    por eso sale como texto y no como `Verificacion`.

    Los dos umbrales van juntos en la misma frase a proposito: separarlos era
    lo que permitia leer "en UNA cara" y creer que el muro entero lleva una
    sola parrilla.
    """
    if requiere_temperatura_dos_caras(espesor=espesor):
        temperatura = (
            f"Acero por temperatura en AMBAS caras: espesor {espesor:.3f} m "
            f">= {ESPESOR_TEMPERATURA_DOS_CARAS:.3f} m "
            f"({NUMERAL_TEMPERATURA_DOS_CARAS})"
        )
    else:
        temperatura = (
            f"Acero por temperatura en UNA cara: espesor {espesor:.3f} m < "
            f"{ESPESOR_TEMPERATURA_DOS_CARAS:.3f} m "
            f"({NUMERAL_TEMPERATURA_DOS_CARAS})"
        )
    if requiere_refuerzo_dos_capas(espesor=espesor):
        capas = (
            f"; refuerzo en cada direccion en DOS CAPAS paralelas a las caras: "
            f"espesor {espesor:.3f} m > {ESPESOR_DOS_CAPAS_REFUERZO:.3f} m "
            f"({NUMERAL_DOS_CAPAS_REFUERZO}, {EXCEPCION_DOS_CAPAS_REFUERZO})"
        )
    else:
        capas = (
            f"; refuerzo en una capa por direccion: espesor {espesor:.3f} m "
            f"<= {ESPESOR_DOS_CAPAS_REFUERZO:.3f} m "
            f"({NUMERAL_DOS_CAPAS_REFUERZO})"
        )
    return temperatura + capas


def espaciamiento_maximo(*, espesor: float) -> float:
    """
    Espaciamiento maximo del refuerzo, en m: min(3h, 0.400 m), E.060
    Art. 14.3.3. `espesor` (h) en metros.
    """
    return min(ESPACIAMIENTO_MAX_VECES_ESPESOR * espesor,
               ESPACIAMIENTO_MAX_ABSOLUTO)


def verificar_espaciamiento(*, espaciamiento: float,
                            espesor: float) -> Verificacion:
    """
    R3: espaciamiento <= min(3h, 400 mm), E.060 Art. 14.3.3. Ambos argumentos
    en metros.
    """
    maximo = espaciamiento_maximo(espesor=espesor)
    return Verificacion(
        cumple=espaciamiento <= maximo + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_ESPACIAMIENTO,
        valor_obtenido=espaciamiento,
        valor_admisible=maximo,
        criterio_aplicado=None,          # [N] puro, Art. 14.3.3
        codigo="R3",
    )


def verificar_ciclopeo(*, fc_matriz: float,
                       fraccion_piedra: float) -> Tuple[Verificacion, ...]:
    """
    R4 / R5: alternativa en concreto ciclopeo. Piedra desplazadora <= 30 % del
    volumen total de concreto ciclopeo (E.060 Art. 22.10, pags. 194-195) y
    f'c de la matriz >= el MAYOR de los dos minimos que rigen sobre el mismo
    material. Admitido para muros de gravedad; Sec. 9.4 la llama "opcion
    realista para cabezales pequenos".

    DOS MINIMOS, Y EL EXPEDIENTE DECLARABA EL MENOR (NOR-E060-07). E.060
    Art. 22.10 pide 10 MPa para la matriz. La Tabla 503-07 del EG-2013 -- cuya
    Seccion 503 es la que este proyecto cita para cabezales, y que es
    especificacion vial del MTC -- clasifica el concreto ciclopeo como Clase G
    y le pide 14 MPa. Los dos rigen sobre una obra vial peruana y ninguno
    deroga al otro, asi que se aplica el mayor: la misma regla del maximo que
    Sec. 0.2 usa para el recubrimiento y `M7.altura_recubrimiento` para la
    cobertura. Citar solo el 10 MPa era quedarse con el requisito mas bajo de
    los dos disponibles, y de los dos el que NO es de una norma vial.

    `fc_matriz` en MPa, `fraccion_piedra` en tanto por uno (0.30, no 30).
    """
    # El numeral llevo pegado, entre corchetes, el rotulo "[DISCREPA DE LA
    # HOJA DE RUTA: ...]" mientras DIS-HR-CICLOPEO estuvo abierta: era la
    # declaracion en el punto de uso que CLAUDE.md exige. I2 corrigio la
    # Sec. 9.4 de la v8 (escribe los dos minimos y el mayor) y la
    # discrepancia quedo RESUELTA, de modo que el rotulo pasaba a afirmar
    # algo falso. La regla de los dos minimos -- que sigue siendo la que
    # esta verificacion aplica -- queda dicha en CICLOPEO_DOS_MINIMOS.
    return (
        Verificacion(
            cumple=fc_matriz >= CICLOPEO_FC_MATRIZ_MIN_APLICABLE - TOL_UMBRAL_NORMATIVO,
            numeral=f"{NUMERAL_CICLOPEO_APLICABLE} "
                    f"[{CICLOPEO_DOS_MINIMOS}]",
            valor_obtenido=fc_matriz,
            valor_admisible=CICLOPEO_FC_MATRIZ_MIN_APLICABLE,
            criterio_aplicado=None,
            codigo="R4",
        ),
        Verificacion(
            cumple=fraccion_piedra <= CICLOPEO_FRACCION_PIEDRA_MAX + TOL_UMBRAL_NORMATIVO,
            numeral=NUMERAL_CICLOPEO,
            valor_obtenido=fraccion_piedra,
            valor_admisible=CICLOPEO_FRACCION_PIEDRA_MAX,
            criterio_aplicado=None,
            codigo="R5",
        ),
    )


# --- T-7c --- `diseno_flexion_corte` YA NO ESTA AQUI. Hasta T-7c esta era la
# funcion que se detenia con `NotImplementedError` («el ensamble del diseño
# por flexion y corte todavia no esta implementado»). El diseño existe: esta
# al final del modulo, en el bloque «9.4 · EL ARMADO DE CADA CABEZAL», con el
# mismo nombre, y arma una seccion por AASHTO LRFD 5.6 y 5.7 con el
# procedimiento simplificado de cortante.


# ===========================================================================
# 9.x - QUE FUNCIONES DE ESTE MODULO NO TIENEN LLAMADOR DE PRODUCCION, Y POR
#       QUE. Una sola escritura, como ya se hace con los criterios
#       (`criterios_adoptados.criterios_sin_consumidor`).
# ===========================================================================
# La razon de cada una vivia repartida entre la auditoria, el manifiesto, el
# docstring del modulo y la nota que la CLI imprime, y ninguno de los cuatro
# era la fuente: los tres hallazgos "deliberado documentado" de este cluster
# (SIS-B-17, SIS-B-20, SIS-B-21) son el mismo defecto de reparto. Aqui la
# razon se escribe una vez, y la CLI y la memoria la leen de aqui.
#
# "Sin llamador de produccion" NO es codigo muerto: son formulas utilizables
# hoy pasandoles sus argumentos, y lo que falta es el INSUMO -- un vacio
# declarado -- o el llamador que lo ensamble. Si alguna se cablea, sale de
# esta lista en el mismo commit.
#
# LA LISTA SE MANTIENE A MANO Y NO HAY GUARDIA QUE LA ATE al estado real del
# modulo. Es la misma deuda que `criterios_sin_consumidor` cerro con un test
# (`test_lo_que_declara_sin_consumidor_de_verdad_no_tiene_consumidor`), y aqui
# esta abierta: el test que la ate va en la fase de tests, no antes. Mientras
# tanto, la comprobacion es de revision: si una funcion de este modulo no
# aparece llamada desde cli.py, gui/app.py ni otro modulo de src/modulos/,
# tiene que estar aqui. La primera version de esta lista ya nacio incompleta
# -- le faltaban siete entradas, dos de ellas de funciones creadas en el mismo
# commit -- y eso es exactamente lo que el test tendra que impedir.
FUNCIONES_SIN_CONSUMIDOR = {
    # --- T-7b --- LA LISTA SE ACORTA: el ensamble de estabilidad
    # (`ensamble_estabilidad`, que el servicio llama por cabezal y por
    # condicion) consume ahora la cadena sismica, Coulomb, Mononobe-Okabe,
    # h_eq, la presion de contacto, gamma_EQ, el limite de excentricidad
    # sismico, la regla de E.050 Art. 20 y los factores de seguridad. Lo que
    # queda aqui es lo que el ensamble NO usa, con su razon.
    "empujes_trasdos": (
        "El ensamble de EXT-7, que tomaba la resultante de Coulomb entera "
        "como horizontal y dejaba el plano de empuje al llamador. T-7b lo "
        "sustituye por `cargas_del_cabezal`, que la descompone sobre el "
        "plano vertical del talon (AASHTO C3.11.5.3) y usa el peso sumergido "
        "bajo el agua. Se conserva como la forma anterior, con sus tests, "
        "para quien tantee con un plano de empuje distinto; ninguna corrida "
        "la llama"),
    "peso_suelo_sobre_talon": (
        "El peso del relleno sobre el talon, de altura uniforme. "
        "`cargas_del_cabezal` lo calcula con la cuña que el talud deja sobre "
        "el talon y con el peso saturado bajo el agua, que esta no conoce. "
        "Se conserva como la pieza revisable del caso mas simple"),
    "fuerza_inercia_muro / peso_propio_cabezal / demanda_sismica_cabezal": (
        "Las formulas sueltas de la inercia del muro y de los dos casos del "
        "num. 2.8.1.1.14.1. `cargas_del_cabezal` calcula esas mismas cargas "
        "con su brazo (necesita el centro de gravedad de cada peso, que "
        "estas no dan) y `combinaciones_de_estabilidad` arma los dos casos "
        "con los mismos factores (`P_SEIS_COMBINACIONES`). Se conservan "
        "como piezas revisables una a una"),
    "verificar_estabilidad / verificar_capacidad_portante / verificar_volteo "
    "/ verificar_deslizamiento / verificar_excentricidad_sismica": (
        "Las cinco verificaciones sueltas de antes de T-7b, que comparan con "
        "los factores de seguridad de E.050 lo que el llamador les pase. El "
        "ensamble no las usa: emite sus propias verificaciones, una por fila "
        "y por marco, con el paso de memoria que dice que cargas recibio "
        "cada una -- que es justo lo que a estas les faltaba (INF-5.1.5). "
        "Se conservan con sus tests; ninguna corrida las llama"),
    "aplica_sobrecarga_trasdos": (
        "Comprueba la regla de la distancia H/2 para el trafico. No la llama "
        "nadie a proposito: Sec. 9.2 cierra el punto diciendo que en un "
        "cabezal bajo terraplen vial la sobrecarga SIEMPRE aplica, y el "
        "ensamble la aplica siempre; esta queda para quien tenga la "
        "distancia medida y quiera comprobarlo"),
    "sobrecarga_trasdos_siempre_aplica": (
        "Declaracion para la memoria; el paso de la sobrecarga del ensamble "
        "(F9.SOBRECARGA) dice lo mismo en su nota"),
    "verificar_estabilidad_global / verificar_talud": (
        "E4 y E5. El ensamble NO las llama: las imprime como diferidas al "
        "expediente con el EMS (`PENDIENTES_E4_E5`). Llamadas a mano se "
        "detienen en 'metodo_estabilidad_global' y, declarado este, con "
        "«metodo no evaluable»: el analisis de superficies de falla no esta "
        "en este programa (hasta T-7b terminaban en un AssertionError)"),
    # --- T-7c --- EL ARMADO TIENE LLAMADOR: `armar_elemento`,
    # `ensamblar_armado` y `verificar_cabezal_ciclopeo` los llama el servicio
    # por cabezal, y consumen `_minimo_de_cuantia_aplicable`,
    # `requiere_refuerzo_dos_capas` y `espaciamiento_maximo`. Lo que queda
    # aqui son las seis piezas sueltas que el armado NO usa.
    "piezas sueltas del num. 9.4 (seis funciones)": (
        "`cuantia_de_diseno`, `verificar_cuantia`, `requiere_temperatura_"
        "dos_caras`, `nota_temperatura_dos_caras`, `verificar_espaciamiento` "
        "y `verificar_ciclopeo` comparan con los minimos de E.060 lo que el "
        "llamador les pase y devuelven una verificacion SIN paso de memoria. "
        "El armado de T-7c no las usa: emite sus propias filas (A3 el acero "
        "minimo, A4 el espaciamiento, C4 y C5 el material del ciclopeo) con "
        "el paso que dice que minimo gobierna y de que norma sale, y en el "
        "minimo junta a E.060 con AASHTO 5.10.6, que estas no conocen. Se "
        "conservan con sus tests como piezas revisables una a una; ninguna "
        "corrida las llama"),
    "clase_exposicion_sulfatos / factor_recubrimiento_por_ac": (
        "No tienen llamador de PRODUCCION directo y no son deuda: las llama "
        "`requisitos_durabilidad_concreto` y "
        "`_recubrimiento_aashto_detallado`, que si estan en el camino de la "
        "CLI. Se declaran aparte porque son las dos piezas que un revisor va "
        "a querer ejecutar sueltas para reproducir la clasificacion de la "
        "Tabla 4.4 y el factor por a/c sin montar el recubrimiento entero"),
    "n_q_zapata_en_talud / n_s_zapata_en_talud": (
        "`capacidad_portante_zapata_en_talud` solo se alcanza con "
        "'terreno_delante_del_cabezal' = 'talud_descendente', que no es el "
        "valor de archivo, y entonces pide la geometria del talud "
        "('talud_delante_del_cabezal' [S]); desde VE-5 la reduccion es la "
        "RC_BC de AASHTO 10.6.3.1.2c, cuyas tablas leen N_s "
        "(`coeficiente_rcbc`). Ninguna corrida con el valor de archivo las "
        "llama (SIS-B-21)"),
}


def funciones_sin_consumidor() -> Tuple[str, ...]:
    """
    Las familias de funciones de M9 que ningun modulo de produccion invoca,
    cada una con su razon, para que la CLI y la memoria la impriman desde un
    solo sitio en vez de repetirla.
    """
    return tuple(f"{nombre}: {razon}"
                 for nombre, razon in FUNCIONES_SIN_CONSUMIDOR.items())


# ===========================================================================
# 9.1 - Condicion normativa (declarativo, para M11)
# ===========================================================================

def condicion_normativa_cabezal() -> Tuple[str, ...]:
    """
    Lo que Sec. 9.1 obliga a escribir en la memoria sobre el cabezal, incluida
    la precision que la propia hoja de ruta hace contra si misma.
    """
    return (
        f"Cabezales y aletas: concreto estructural EG-2013 Seccion "
        f"{SECCION_CABEZALES} (+504 para el acero). NO tienen partida con "
        f"numeral propio: se pagan bajo el volumen de concreto y el acero. "
        f"Que aparezcan nominados en 503.01 confirma que son elemento "
        f"estandar de terminacion, pero el argumento es mas debil que "
        f"'existe una partida especifica' ({NUMERAL_9_1})",
        "Embocadura: tubo a ras del muro (square edge), coherente con las "
        "constantes HDS-5 adoptadas en Sec. 4.2. Ambas decisiones se mueven "
        "juntas: cambiar el detalle obliga a cambiar las constantes "
        "(Sec. 9.1 y Tablero 2.3). Desde T-7a la embocadura es del PUNTO "
        "('embocadura_cabezal' y 'angulo_aletas', [A]): con tubo la Tabla C.2 "
        "agrupa el cabezal con y sin aleros en una fila y nada se mueve; con "
        "marco, su carta y su fila de ke tienen que ser de la banda de angulo "
        "del cabezal",
        f"Empuje hidrostatico y subpresion: con NF a 1.4 m NO son opcionales "
        f"({NUMERAL_SUBPRESION})",
        # El Ka estatico es el de Coulomb del Manual, no el tan^2 de la hoja
        # de ruta: declarado en el punto de uso (`empujes_trasdos`) y aqui,
        # para el revisor que lea la v8 antigua (EXT-M-06).
        KA_COULOMB_DECLARACION,
        # --- T-7b --- REESCRITA. La hoja de ruta afirmaba que el cabezal
        # «se apoya en el borde del terraplen, no en terreno horizontal» y
        # exigia siempre la zapata en talud; con la geometria que T-7a
        # propone no es asi, y lo declara 'terreno_delante_del_cabezal'.
        f"Terreno delante de la zapata: el cabezal se desplanta bajo el "
        f"terreno del pie del muro, que es el fondo del cauce, y el talud "
        f"del terraplen SUBE detras de el. La capacidad portante es por eso "
        f"la de terreno horizontal (AASHTO LRFD 10.6.3.1.2a), con el "
        f"empotramiento que quede bajo la socavacion "
        f"('terreno_delante_del_cabezal' [A] = horizontal). La zapata en "
        f"talud ({NUMERAL_ZAPATA_TALUD_E050} y {NUMERAL_ZAPATA_EN_TALUD}) "
        f"queda para el cabezal que si tenga un terreno que desciende "
        f"delante; la hoja de ruta la exigia para todos y se corrigio",
        f"Diseno por flexion y corte: {NUMERAL_FLEXION_CORTE}. E.060 no "
        f"gobierna el diseno estructural (Sec. 0.2, Via 1); si gobierna la "
        f"durabilidad y los recubrimientos, con la regla del mayor",
        # Las erratas de imprenta del Manual en la cadena sismica -- son TRES
        # y la tercera esta mas abajo, con la excentricidad. Van a
        # la memoria y no solo a un docstring porque quien las va a encontrar
        # es el revisor que compare el codigo con la norma impresa, y sin
        # esta nota concluira que el codigo esta mal (MAT-O2, MAT-X2).
        f"Mononobe-Okabe, signo del denominador: {K_AE_ERRATA_MANUAL} "
        f"({NUMERAL_K_AE_MANUAL}; {NUMERAL_K_AE_AASHTO})",
        f"k_h0 en cimentacion sobre roca: {K_H0_ROCA_ERRATA} "
        f"({NUMERAL_K_H0})",
        # LA SOBRECARGA VIVA DEL TRASDOS, con sus DOS fuentes. La memoria
        # imprimia solo el numeral peruano, que fija un PISO de 0.60 m, para
        # un h_eq que la tabla de AASHTO puede llevar a 1.12 m: el lector veia
        # el numero grande citado contra la fuente del numero pequeño
        # (NOR-PUE-01, NOR-PUE-02, MAT-O1, MAT-X1).
        f"Sobrecarga viva en el trasdos: h_eq = max(piso del Manual, tabla de "
        f"AASHTO por altura y orientacion). {NUMERAL_SOBRECARGA_TRASDOS} fija "
        f"el piso -- «no menor que» -- y no tabula nada; el valor sale de "
        f"{NUMERAL_SOBRECARGA_TRASDOS_AASHTO}. La altura de entrada es la del "
        f"muro CON zapata: {NUMERAL_SOBRECARGA_TRASDOS_ALTURA}",
        f"Cual de las dos tablas de AASHTO aplica: {H_EQ_REPARTO_DE_TABLAS}",
        f"Cuando la sobrecarga se aplica: {NUMERAL_SOBRECARGA_TRASDOS_APLICA}",
        # La hipotesis del agua en el trasdos: desviacion conservadora de un
        # `shall` de AASHTO, declarada (MAT-O3, MAT-X3).
        f"Empuje bajo el nivel freatico: {HIPOTESIS_EMPUJE_BAJO_NF} "
        f"({NUMERAL_AGUA_TRASDOS_AASHTO})",
        # Inercia del muro: el termino que faltaba, y el aviso de que la
        # combinacion no es una suma (MAT-D6, MAT-X7).
        f"Demanda sismica del cabezal: no basta el empuje. El num. {NUMERAL_P_IR} "
        f"exige combinar P_AE con la inercia de la masa del muro "
        f"P_IR = k_h*(W_w + W_s), en dos casos que se investigan por separado "
        f"porque sus efectos NO son simultaneos -- 100 % P_AE + 50 % P_IR, y "
        f"50 % P_AE (no menor que el empuje activo estatico) + 100 % P_IR --, "
        f"rigiendo el mas desfavorable. La Sec. 9.2 de la hoja de ruta "
        f"desagrega la cadena sismica y NO menciona P_IR: el defecto se "
        f"reporta contra ella. Desde T-7b el ensamble de cada cabezal la "
        f"arma entera, con sus dos casos",
        # El limite de excentricidad: no es "el tercio central" a secas
        # (MAT-O16).
        f"Ubicacion de la resultante en la base bajo sismo: el "
        f"num. {NUMERAL_EXCENTRICIDAD_SISMICA} la acota a los dos tercios "
        f"centrales (e <= B/3) con gamma_EQ = 0.0 y a las ocho decimas "
        f"centrales (e <= 0.4*B) con gamma_EQ = 1.0, interpolando en medio. "
        f"Es una verificacion que la tabla de FS de Sec. 9.3 no trae, porque "
        f"E.050 no la escribe: desde T-7b es la fila E2 del marco LRFD en "
        f"condicion sismica, y depende de 'gamma_EQ' [A] (0.50 de archivo)",
        # La tercera errata, que mueve un numero y por eso pesa mas que las
        # otras dos.
        f"Excentricidad sismica, 'tercio central': {EXCENTRICIDAD_ERRATA_MANUAL} "
        f"({NUMERAL_EXCENTRICIDAD_SISMICA}; {NUMERAL_EXCENTRICIDAD_SISMICA_AASHTO}; "
        f"el limite estatico que sirve de ancla, en {NUMERAL_EXCENTRICIDAD_ESTATICA})",
        # La presion de contacto tiene dos ramas y el proyecto usa la de suelo.
        f"Presion de contacto en la base: el num. {NUMERAL_PRESION_CONTACTO} "
        f"la reparte por terreno de fundacion -- uniforme sobre el ancho "
        f"efectivo B - 2e en SUELO, lineal sobre B en ROCA -- y no la "
        f"escribe el numeral sismico. La rama que aplica a este cabezal es la "
        f"de suelo, coherente con las filas de sitio declaradas en 'F_pga'",
        # Por que E.030 no gobierna este cabezal. El descarte se defendia solo
        # por periodo de retorno, que es la via discutible (NOR-E030-03).
        f"E.030 no gobierna el diseno sismico de este cabezal, y el argumento "
        f"es de AMBITO antes que de periodo de retorno: {E030_AMBITO_LECTURA} "
        f"({NUMERAL_E030_AMBITO}; {NUMERAL_E030_ESTRUCTURAS_NO_EDIFICACION})",
        f"Texto literal del Art. 7.3 de E.030, que es el que cede el paso: "
        f"\"{E030_ART_7_3_TEXTO}\" ({NUMERAL_E030_ESTRUCTURAS_NO_EDIFICACION})",
        # LA CLASE DE SITIO, y por que este expediente no se atribuye
        # ninguna. Es la correccion de S13/S14 (conflicto #8): el expediente
        # afirmaba la Clase de Sitio F y ninguna de las dos fuentes la
        # sostiene -- pero lo que decide no es el silencio, es que las dos
        # PROHIBEN suponer la clase E o F sin dato geotecnico. El texto va a
        # la memoria entero, con las dos citas literales, porque un revisor
        # que solo lea "indeterminada" no sabra que ya se busco
        # (NOR-AAS-02, SIS-B-01, SIS-D-01, NOR-MEM-03).
        f"{CLASE_DE_SITIO_INDETERMINADA} ({NUMERAL_CLASE_SITIO_AASHTO})",
        f"Texto literal de la prohibicion, en el articulado y no en un "
        f"comentario: \"{CLASE_SITIO_EF_NO_SUPUESTA_TEXTO}\" "
        f"({NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA}). El Manual de Puentes lo "
        f"endurece a un futuro imperativo: "
        f"\"{CLASE_SITIO_EF_NO_SUPUESTA_MP_TEXTO}\" "
        f"({NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA_MP})",
        f"El deber positivo que abre la misma clausula, y que es lo que "
        f"convierte a la clase de sitio en un dato pendiente de ensayo y no "
        f"en un valor que el proyectista adopte: "
        f"\"{CLASE_SITIO_INVESTIGACION_TEXTO}\" "
        f"({NUMERAL_CLASE_SITIO_INVESTIGACION})",
        f"{CLASE_DE_SITIO_POR_QUE_DEJA_DE_DECIRSE} "
        f"({NUMERAL_CLASE_SITIO_MP}; {NUMERAL_LICUEFACCION_AASHTO}; "
        f"{NUMERAL_E030_S5})",
        f"{CLASE_DE_SITIO_COHERENCIA_INTERNA} "
        f"({NUMERAL_LICUEFACCION_ESPECTRO})",
        f"{CLASE_DE_SITIO_QUE_LA_CIERRA} "
        f"({NUMERAL_RESPUESTA_DE_SITIO_AASHTO}; "
        f"{NUMERAL_RESPUESTA_DE_SITIO_MP})",
        # La homonimia, que llega a la memoria por dos caminos distintos y
        # sin relacion entre si (NOR-VOC-04). Se imprime aqui, pegada a la
        # cadena sismica, porque es donde el lector se encuentra el termino;
        # el glosario completo de las cuatro homonimias del expediente lo
        # imprime M11 (`bloque_homonimias`), leyendo esta MISMA declaracion.
        homonimia_como_texto(HOMONIMIA_CLASE_F),
        # Lo que E.030 SI dice sobre este sitio, y que el expediente tenia
        # archivado como referencia muerta (NOR-E030-02).
        f"Perfil de suelo S5 de E.030: aunque la norma no gobierne el diseno "
        f"del cabezal, su clasificacion del sitio trae una consecuencia que "
        f"el expediente tiene que atender. Texto literal: \"{E030_S5_TEXTO}\" "
        f"({NUMERAL_E030_S5}). {E030_S5_LECTURA}",
        # Las funciones de este modulo que ningun llamador de produccion
        # alcanza, con su razon, desde un solo sitio (SIS-B-17/20/21).
        *(f"Sin llamador de produccion -- {linea}"
          for linea in funciones_sin_consumidor()),
    )


# ---------------------------------------------------------------------------
# Recubrimiento con que se arma
# ---------------------------------------------------------------------------

def recubrimiento_para_armar(*, condicion: str) -> Tuple[float, str,
                                                         Optional[str]]:
    """
    El recubrimiento, en mm, con que se calcula el peralte efectivo de una
    cara, su origen y, si hace falta, el aviso.

    CON LOS DOS DATOS DECLARADOS ('categoria_refuerzo_aashto' [A] y
    'exposicion_quimica_ems' [S]) es el de la regla del mayor de la Sec. 0.2
    (`recubrimiento_de_diseno`).

    SIN ALGUNO DE LOS DOS NO SE RELLENA EL DATO: el encargo de la cadena T
    pedia tomar entonces los 70 mm de E.060 7.7.1, y eso seria suponer la
    categoria del acero y la agresividad del sitio. Se arma con la COTA MAS
    EXIGENTE que la regla puede dar para esa cara -- el mayor de E.060 y de
    la fila de AASHTO en su columna de mas recubrimiento, con el factor por
    relacion agua-cemento mas alto --, que es el lado seguro del peralte
    efectivo (mas recubrimiento, menos brazo, mas acero), y se AVISA: el dato
    sigue faltando y el recubrimiento del plano sale de la regla completa.

    DONDE ESA COTA NO ES EL LADO SEGURO, dicho en el aviso (pregunta 2 del
    cierre de T-7c): es la mas exigente de la regla ANTES del aumento por
    ambiente corrosivo de E.060 7.7.5.1, que la regla no cuantifica; si el
    EMS declara un ambiente corrosivo, el recubrimiento real puede pasarla y
    entonces la flexion, la fisuracion de 5.6.7 (d_c) y la altura de la
    zapata sobre su refuerzo (E.060 15.7) quedan del lado inseguro hasta
    rearmar. Y en el cortante el piso 0.72·h de 5.7.2.8 no depende del
    recubrimiento: por eso d_v se acota al peralte efectivo (H8).
    """
    try:
        r = recubrimiento_de_diseno(condicion=condicion)
        return (float(r.adoptado_mm),
                f"regla del mayor ({r.origen}: E.060 {r.e060_mm:.1f} mm, "
                f"AASHTO {r.aashto_mm:.1f} mm)", None)
    except CriterioPendienteError as falta:
        if falta.clave not in (CRITERIO_CATEGORIA_REFUERZO,
                               CRITERIO_EXPOSICION_QUIMICA):
            raise
        clave = falta.clave
    e060 = recubrimiento_e060_mm(condicion=condicion)
    situaciones = ca.valor(CRITERIO_SITUACION_RECUBRIMIENTO)
    tabla = ca.valor(CRITERIO_TABLA_RECUBRIMIENTO)
    situacion = situaciones.get(condicion)
    if situacion not in tabla:
        raise DatoInvalidoError(
            "situacion", valor=situacion,
            motivo=f"la condicion '{condicion}' no tiene fila emparejada en "
                   f"'{CRITERIO_SITUACION_RECUBRIMIENTO}'")
    tabulado = max(float(x) for x in tabla[situacion].values())
    factor = max(RECUBRIMIENTO_MP_FACTOR_AC.values())
    cota = max(e060, tabulado * factor, RECUBRIMIENTO_MP_PISO_MM)
    return (cota,
            f"cota mas exigente por falta de dato: max(E.060 {e060:.1f} mm, "
            f"AASHTO {tabulado:.1f} mm x {factor:g})",
            f"el recubrimiento con que se arma ({cota:.1f} mm, condicion "
            f"'{condicion}') es la COTA MAS EXIGENTE de la regla del mayor y "
            f"no el recubrimiento del proyecto: falta declarar '{clave}' "
            f"(tambien hacen falta '{CRITERIO_CATEGORIA_REFUERZO}' y "
            f"'{CRITERIO_EXPOSICION_QUIMICA}', del expediente y del analisis "
            "quimico del EMS). Sin ambiente corrosivo, con ellos el "
            "recubrimiento baja, el peralte efectivo sube y el acero "
            "requerido no aumenta; el espaciamiento de fisuracion de AASHTO "
            "5.6.7 y la altura de la zapata sobre su refuerzo (E.060 15.7) "
            "se relajan. NO es el lado seguro si el EMS declara un ambiente "
            "corrosivo: E.060 7.7.5.1 manda entonces AUMENTAR el "
            "recubrimiento sin decir cuanto, puede pasar esta cota y la "
            "flexion, la fisuracion y la altura de 15.7 hay que rehacerlas. "
            "En el cortante el piso 0.72·h de AASHTO 5.7.2.8 no depende del "
            "recubrimiento: por eso d_v se acota al peralte efectivo")
