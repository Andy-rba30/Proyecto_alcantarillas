"""
M1_clasificacion.py
===================
Fase 2 de la hoja de ruta: umbral binario de luz (Sec. 2.1), periodo de retorno
por la formula de la Tabla N 02 (Sec. 2.2) y perfil de familia A/B/C (Sec. 2.3).

Las tres cosas que decide M1
----------------------------
1. DENOMINACION (Sec. 2.1). Luz < 6.0 m -> alcantarilla, y el punto sigue en
   este script. Luz >= 6.0 m -> puente, Manual de Puentes, fuera de alcance.
   El binario no tiene tercera casilla: "ponton" no existe en la normativa MTC.

2. PERIODO DE RETORNO (Sec. 2.2). No se toma de una lista de TR "de costumbre":
   se despeja de la formula del riesgo admisible con el R y el n de la fila que
   corresponda de la Tabla N 02. No hay TR minimo obligatorio independiente y
   por eso el modulo no adopta 50 anios ni ningun otro piso.

3. PERFIL DE FAMILIA (Sec. 2.3). La familia viene declarada en el CSV
   (Sec. 1.1 la lista como dato de entrada "de Fase 2"); lo que M1 resuelve es
   lo que esa familia IMPLICA: de donde sale el caudal, que fila de la
   Tabla N 02 le toca, que campos necesita y con que verificaciones se acepta.

De donde sale la luz
--------------------
`luz_m` NO es columna del encabezado de Sec. 1.2 y por eso no es campo de
PuntoCritico: es la luz que exige el cruce -- el ancho del canal o de la
quebrada que se atraviesa -- y sale de la topografia o del QGIS, como en los
dos ejemplos de Sec. 2.1 (canal de 12 m -> puente; canal de 2.75 m ->
alcantarilla). No es el diametro: el diametro lo fija la Fase 4 y, topado por
Sec. 3.2 en 2.70 m, nunca alcanzaria por si solo el umbral de 6.0 m. Como el
dato no esta en el CSV, se pasa explicitamente; si no se pasa, el modulo lanza
DatoFaltanteError en vez de suponer que el cruce es estrecho.

El vacio que M1 no rellena
--------------------------
La Tabla N 02 trae dos filas y Sec. 2.3 dice que la Familia A lleva "TR 71 o 35
anios", sin regla para decidir cual. M1 no elige por su cuenta: o el que llama
declara la categoria del cauce, o se lee el criterio
`umbral_area_quebrada_importante_ha`, hoy sin valor, que detiene el calculo con
CriterioPendienteError. La Familia B si tiene fila fija (descarga de cunetas ->
quebrada menor, TR 35) y la Familia C no tiene TR: su caudal es el del canal.

Excepciones
-----------
    DatoFaltanteError        falta la luz del cruce, o un campo que la familia
                             necesita y la fila trajo vacio.
    DatoInvalidoError        la luz esta pero no puede ser (nula o negativa), o
                             la categoria de TR no es una fila de la Tabla N 02.
    CriterioPendienteError   Familia A sin categoria declarada: el umbral que
                             separa quebrada importante de menor sigue vacio.
    DisenoNoFactibleError    solo desde `exigir_alcance()`: el punto es puente.

Uso
---
    from modulos.M0_carga import cargar_puntos
    from modulos.M1_clasificacion import clasificar_puntos, exigir_alcance

    puntos = cargar_puntos("tests/ejemplo_puntos.csv")
    luces = {"A-01": 2.75, "A-02": 1.80, "B-01": 1.20, "C-01": 2.75}
    for clasificacion in clasificar_puntos(puntos, luces):
        exigir_alcance(clasificacion)              # detiene los puentes
        TR = clasificacion.periodo_retorno.anios
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Tuple, Union

from constantes_normativas import (LUZ_MAX_ALCANTARILLA, RIESGO_ADMISIBLE,
                                   TABLA_02_FILAS, UMBRALES_POR_CODIGO,
                                   caracter_del_umbral)
from criterios_adoptados import valor, valor_si_declarado
from modelos import (CIFRAS_FACTOR, CIFRAS_MAGNITUD, CategoriaTR,
                     Clasificacion, DatoFaltanteError,
                     DatoInvalidoError, Denominacion, DisenoNoFactibleError,
                     EleccionDeProyecto, Familia, Magnitud, PerfilFamilia,
                     PeriodoRetorno, PuntoCritico, TipoDeVeredicto, Umbral,
                     Veredicto, Verificacion, paso)
from tolerancias import TOL_UMBRAL_NORMATIVO

# Numerales que sustentan cada decision de la fase.
NUMERAL_LUZ = "4.1.1.3.1 / 4.1.1.5.1"     # Manual MTC, pags. 70 y 88 (Sec. 2.1)
# El numeral se escribe largo por lo mismo que los de M5: es lo que la memoria
# imprime, y sin el CARACTER de la tabla el revisor lee como exigencia lo que
# la fuente escribe como techo recomendado (NOR-HID-08). El titulo literal es
# "VALORES MAXIMOS RECOMENDADOS de riesgo admisible de obras de drenaje", el
# texto que la introduce dice "se recomienda utilizar como maximo", y la nota
# al pie cierra: "El Propietario de una Obra es el que define el riesgo
# admisible de falla y la vida util de las obras". El proyecto adopta los
# maximos recomendados, que en esta tabla -- al reves que en V1 y V2 -- es el
# extremo MENOS conservador del margen concedido: mas riesgo admisible da
# menos TR y menos caudal de diseno.
NUMERAL_TR = ('MC-HHD (RD 20-2011-MTC/14), num. 3.6, Tabla N 02 "VALORES '
              'MAXIMOS RECOMENDADOS de riesgo admisible de obras de drenaje", '
              'pag. impresa 25. La tabla RECOMIENDA estos valores "como '
              'maximo" y su nota al pie asigna la decision al Propietario de '
              'la obra; el proyecto adopta los maximos recomendados mientras '
              'el Propietario no declare otros')  # (Sec. 2.2)
NUMERAL_FAMILIA = "Sec. 2.3"              # la hoja de ruta, sin numeral MTC propio

CRITERIO_CATEGORIA_A = "umbral_area_quebrada_importante_ha"
# La decision que la nota al pie de la Tabla N 02 le asigna al Propietario:
# que R y que n adopta para una fila ya elegida. OPCIONAL -- se lee con
# `valor_si_declarado`, no con `valor` --: sin declarar rigen los maximos
# recomendados de la tabla y el calculo no se detiene.
CRITERIO_RIESGO_PROPIETARIO = "riesgo_admisible_propietario"

CategoriaLike = Union[CategoriaTR, str]


# ---------------------------------------------------------------------------
# Sec. 2.1 - Umbral binario de luz
# ---------------------------------------------------------------------------

def denominacion_por_luz(luz_m: Optional[float],
                         id_punto: Optional[str] = None) -> Denominacion:
    """
    Alcantarilla o puente, segun el umbral de 6.0 m (num. 4.1.1.3.1 y
    4.1.1.5.1). Binario: no existe una tercera denominacion intermedia.

    La tolerancia se aplica del lado exigente. Una luz que el punto flotante
    deja en 5.999999999 es una luz de 6.0 m mal representada, y 6.0 m es
    puente: sumarla al lado de la alcantarilla convertiria un puente en
    alcantarilla por ruido de aritmetica.
    """
    luz = _luz_valida(luz_m, id_punto)
    if luz <= LUZ_MAX_ALCANTARILLA - TOL_UMBRAL_NORMATIVO:
        return Denominacion.ALCANTARILLA
    return Denominacion.PUENTE


def verificar_luz(luz_m: Optional[float],
                  id_punto: Optional[str] = None) -> Verificacion:
    """
    Umbral de luz como verificacion, no como bool desnudo: la memoria necesita
    el numeral que lo sustenta (Sec. 2.1).

    `cumple` significa "esta dentro del alcance de este script", es decir, que
    la denominacion es alcantarilla.
    """
    denominacion = denominacion_por_luz(luz_m, id_punto)
    es_alcantarilla = denominacion is Denominacion.ALCANTARILLA
    return Verificacion(
        cumple=es_alcantarilla,
        numeral=NUMERAL_LUZ,
        valor_obtenido=float(luz_m),
        valor_admisible=LUZ_MAX_ALCANTARILLA,
        criterio_aplicado=None,           # umbral [N] puro, sin criterio adoptado
        paso=paso(
            "F2.LUZ",
            codigo="2.1",
            que="Denominacion de la obra: alcantarilla o puente",
            formula="luz < 6.0 m -> alcantarilla; luz >= 6.0 m -> puente",
            formula_cita_id="MC_HHD.4.1.1.3.1",
            citas_textuales=("MC_HHD.4.1.1.3.1", "MC_HHD.4.1.1.5.1"),
            sustitucion=(
                Magnitud("luz", float(luz_m), "m",
                         "luz del cruce, declarada con --luz o por "
                         "--datos-externos: NO es columna del CSV",
                         cifras=CIFRAS_FACTOR),),
            resultado=Magnitud("denominacion", denominacion.value, "",
                               "lectura del umbral de los dos numerales"),
            umbral=Umbral(
                descripcion="luz maxima de una alcantarilla",
                valor=LUZ_MAX_ALCANTARILLA, unidad="m",
                cita_id="MC_HHD.4.1.1.3.1",
                caracter="DEFINICION",
                aplicacion="La tolerancia se aplica del lado exigente: una "
                           "luz que el punto flotante deja en 5.999999999 es "
                           "6.0 m mal representada, y 6.0 m es puente. "
                           "Sumarla al lado de la alcantarilla convertiria un "
                           "puente en alcantarilla por ruido de aritmetica."),
            veredicto=Veredicto(
                tipo=(TipoDeVeredicto.CUMPLE if es_alcantarilla
                      else TipoDeVeredicto.NO_CUMPLE),
                margen=LUZ_MAX_ALCANTARILLA - float(luz_m), unidad="m",
                explicacion=(
                    "dentro del alcance de este script"
                    if es_alcantarilla else
                    "la obra es un PUENTE: la gobierna el Manual de Puentes, "
                    "con otro tren de cargas y otro procedimiento sismico. "
                    "El pipeline se detiene en vez de emitir una memoria que "
                    "cite numerales de un manual que no la gobierna")),
        ),
    )


def exigir_alcance(clasificacion: Clasificacion) -> Clasificacion:
    """
    Detiene el pipeline cuando el punto resulta puente (Sec. 2.1 y regla dura
    de Sec. 3.1: luz >= 6.0 m -> fuera de alcance).

    Se devuelve la misma clasificacion para poder encadenar. La excepcion es
    DisenoNoFactibleError y no otra porque el punto es del expediente y la GUI
    tiene que mostrarlo como tal: no hay conducto alguno que resuelva un cruce
    de 6 m o mas, y el motivo dice a que manual se remite.
    """
    if clasificacion.en_alcance:
        return clasificacion
    raise DisenoNoFactibleError(
        motivo=f"la luz del cruce ({clasificacion.luz_m} m) alcanza el umbral de "
               f"{LUZ_MAX_ALCANTARILLA} m del num. {NUMERAL_LUZ}: la estructura es "
               "un PUENTE y se disena con el Manual de Puentes, fuera del alcance "
               "de este script. No existe la categoria intermedia 'ponton'",
        id_punto=clasificacion.punto.id,
    )


def _luz_valida(luz_m: Optional[float], id_punto: Optional[str]) -> float:
    """
    La luz no es columna de Sec. 1.2: llega por argumento y aqui se comprueba
    que llego y que es un numero posible.
    """
    if luz_m is None:
        raise DatoFaltanteError(
            "luz_m", id_punto=id_punto,
            detalle="la luz del cruce no es columna del encabezado de Sec. 1.2 y "
                    "se pasa a M1 explicitamente. Sale de la topografia o del "
                    "QGIS (ancho del canal o de la quebrada que se atraviesa), no "
                    "del diametro, que lo fija la Fase 4. Sin ella no se puede "
                    "aplicar el umbral binario de Sec. 2.1",
        )
    try:
        luz = float(luz_m)
    except (TypeError, ValueError):
        raise DatoInvalidoError(
            "luz_m", valor=luz_m, id_punto=id_punto,
            motivo="no es un numero (metros, SI)",
        ) from None
    if luz <= 0:
        raise DatoInvalidoError(
            "luz_m", valor=luz_m, id_punto=id_punto,
            motivo="la luz del cruce es una longitud positiva en metros",
        )
    return luz


# ---------------------------------------------------------------------------
# Sec. 2.2 - Periodo de retorno
# ---------------------------------------------------------------------------

def tr_desde_riesgo(R: float, n: int) -> float:
    """
    TR despejado del riesgo admisible de falla (num. 3.6, Sec. 2.2):

        R = 1 - (1 - 1/T)^n     =>     T = 1 / (1 - (1-R)^(1/n))

    R es probabilidad (0 < R < 1) y n la vida util en anios. Devuelve el TR sin
    redondear; el redondeo al anio lo hace `tr_de_categoria`.
    """
    if not 0 < R < 1:
        raise DatoInvalidoError(
            "R", valor=R, motivo="el riesgo admisible de falla es una "
                                 "probabilidad entre 0 y 1, no un porcentaje")
    if not n > 0:
        # EN POSITIVO, por la misma razon que la guarda del denominador mas
        # abajo: `n <= 0` es FALSO para un NaN, de modo que un `n = nan`
        # atravesaba esta comprobacion y llegaba a la formula. La condicion
        # escrita en positivo y negada si lo atrapa.
        raise DatoInvalidoError(
            "n", valor=n, motivo="la vida util son anios y es un numero "
                                 "positivo")
    # BORDE R -> 0 (MAT-D13). Con un riesgo suficientemente pequeño,
    # (1-R)^(1/n) redondea a 1.0 en doble precision y el denominador se anula.
    # El limite esta en R ~ n * eps/4 -- medido: 1.3877787807814459e-15 para
    # n = 25 --, y es el CUARTO y no la mitad porque los floats inmediatamente
    # por debajo de 1.0 estan espaciados eps/2, de modo que 1 - R/n redondea a
    # 1.0 en cuanto R/n cae por debajo de eps/4. Sin esta guarda el resultado
    # era un ZeroDivisionError: un fallo de PROGRAMA, fuera de la taxonomia
    # ErrorProyecto que CLAUDE.md exige para todo problema del expediente.
    #
    # Se comprueba el DENOMINADOR y no se compara la potencia con 1.0: no hay
    # umbral que declarar (seria un literal de precision disfrazado de valor
    # normativo) y no se comparan floats con igualdad. Cuando el denominador
    # es cero el TR no es "muy grande": no existe, porque la formula se
    # degenero antes de calcularlo.
    #
    # La condicion se escribe EN POSITIVO y negada -- `not denominador > 0` y
    # no `denominador <= 0` -- porque un NaN es falso frente a `<=` igual que
    # frente a `>`: con n = nan las tres guardas de esta funcion se
    # atravesaban y el TR salia nan, que es el mismo agujero que la guarda
    # existe para cerrar.
    denominador = 1 - (1 - R) ** (1 / n)
    if not denominador > 0:
        # EL MENSAJE NOMBRA EL PAR, no solo R. La degeneracion no es de un
        # dato sino de la combinacion: (1-R)^(1/n) redondea a 1 cuando R es
        # diminuto PARA ESA n, y una n grande la provoca con una R que seria
        # perfectamente sana con otra vida util. La primera version acusaba
        # siempre a 'R' y mandaba al revisor a corregir el dato equivocado la
        # mitad de las veces; escribir un discriminante que reparta la culpa
        # entre los dos seria falsa precision --- no hay un umbral que separe
        # "culpa de R" de "culpa de n" ---, de modo que se dicen los DOS
        # valores y se deja la eleccion a quien tiene el expediente delante.
        #
        # El `campo` sigue siendo 'R' porque es el que el Propietario declara
        # y el que MAT-D13 describe; el motivo dice que n es la otra mitad.
        raise DatoInvalidoError(
            "R", valor=R,
            motivo=f"el par (R = {R!r}, n = {n!r}) degenera: (1-R)^(1/n) no "
                   "se distingue de 1 en doble precision y el periodo de "
                   "retorno resultaria de una division por cero. No es un TR "
                   "grande, es una division por cero. Puede corregirse por "
                   "cualquiera de los dos lados --- un R mayor o una vida "
                   "util menor ---, y NINGUNO sale de una celda del CSV: o "
                   "son los de la Tabla N 02, o los declaro el Propietario "
                   f"en '{CRITERIO_RIESGO_PROPIETARIO}'. Revisa ahi si R "
                   "vino en porcentaje o si perdio digitos",
        )
    return 1 / denominador


def _riesgo_del_propietario(cat: CategoriaTR, R: float, n: int):
    """
    (R, n, declarado) tras aplicar la declaracion del Propietario, si la hay.

    La nota al pie de la Tabla N 02 dice que "El Propietario de una Obra es el
    que define el riesgo admisible de falla y la vida util de las obras", y el
    titulo de la tabla la presenta como VALORES MAXIMOS RECOMENDADOS. Los
    numeros de `RIESGO_ADMISIBLE` son, por lo tanto, un techo recomendado que
    el proyecto adopta por defecto, no una exigencia; esta funcion es la via
    por la que el Propietario ejerce su decision (NOR-HID-08).

    Se lee con `valor_si_declarado`, no con `valor`: sin declaracion el
    calculo NO se detiene y rigen los maximos de la tabla. La declaracion se
    escribe por fila:

        {"quebrada_importante": {"R": 0.20, "n": 25}}

    Solo puede ENDURECER lo que la tabla concede. Un R por encima del maximo
    recomendado de su fila, o un n por debajo de la vida util que la nota al
    pie le asigna, es `DatoInvalidoError`: la tabla dice "como maximo", de modo
    que declarar mas riesgo del recomendado no es una decision del Propietario
    sino salirse del techo normativo. Bajar R o subir n sube el TR y con el el
    caudal de diseno, que es la direccion segura.
    """
    declarado = valor_si_declarado(CRITERIO_RIESGO_PROPIETARIO)
    if not declarado or cat.value not in declarado:
        return R, n, False

    fila = declarado[cat.value]
    R_declarado = fila.get("R", R)
    n_declarado = fila.get("n", n)
    if R_declarado > R + TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            CRITERIO_RIESGO_PROPIETARIO, valor=R_declarado,
            motivo=f"la Tabla N 02 recomienda R = {R} COMO MAXIMO para la "
                   f"fila '{cat.value}'. El Propietario puede adoptar un "
                   f"riesgo menor -- que sube el TR y el caudal de diseno -- "
                   f"pero no uno mayor: eso seria salirse del techo que la "
                   f"tabla concede, no ejercer la decision que su nota al pie "
                   f"le asigna",
        )
    if n_declarado < n - TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            CRITERIO_RIESGO_PROPIETARIO, valor=n_declarado,
            motivo=f"la nota al pie de la Tabla N 02 asigna n = {n} anios de "
                   f"vida util a la fila '{cat.value}'. Una vida util menor "
                   f"baja el TR y el caudal de diseno: es la direccion "
                   f"insegura, y no es lo que la nota concede",
        )
    return R_declarado, n_declarado, True


def _paso_tr(*, cat, R, n, exacto, del_propietario: bool):
    """
    El paso de memoria del periodo de retorno.

    ES EL CASO MAS CLARO DE LA REGLA R1 ("se adopto X, elegido entre X1...Xn
    de la Tabla T, por la razon R"): la Tabla Nº 02 tiene SEIS filas, el
    calculo usa dos, y de esas dos el TR sale de la que describe a este punto.
    Sin las alternativas, «TR = 71 años» es un numero que el revisor tiene que
    creer; con ellas, es una decision que puede discutir.

    Y HAY UNA SEGUNDA ELECCION, que es la que la memoria callaba: adoptar los
    MAXIMOS recomendados de la tabla es el extremo MENOS conservador del
    margen que la tabla concede -- mas riesgo admisible da menos TR y menos
    caudal de diseño --, al reves que en V1 y V2, donde la lectura dura es la
    conservadora. La nota al pie deja esa decision al Propietario y el
    proyecto tiene una via declarada para que la ejerza.
    """
    filas = tuple(
        f"«{datos['fila']}» (R = {RIESGO_ADMISIBLE[clave]['R']}, "
        f"n = {RIESGO_ADMISIBLE[clave]['n']} anios)"
        for clave, datos in TABLA_02_FILAS.items()
        if clave in RIESGO_ADMISIBLE)
    elecciones = [EleccionDeProyecto(
        que_se_adopto="fila de la Tabla Nº 02 que describe a este cruce",
        valor=f"«{TABLA_02_FILAS[cat.value]['fila']}»",
        entre=filas,
        de_donde="la Tabla Nº 02 del num. 3.6, pag. impresa 25",
        por_que="es la fila que corresponde a la familia y al area tributaria "
                "del punto (Sec. 2.2 y 2.3). LA TABLA ES NORMATIVA; QUE FILA "
                "DESCRIBE A ESTE CRUCE NO LO ES",
        cita_id="MC_HHD.3.6")]
    if del_propietario:
        elecciones.append(EleccionDeProyecto(
            que_se_adopto="riesgo admisible y vida util",
            valor=f"R = {R}, n = {n} anios",
            entre=(f"R = {RIESGO_ADMISIBLE[cat.value]['R']}, "
                   f"n = {RIESGO_ADMISIBLE[cat.value]['n']} anios "
                   "(maximos recomendados por la tabla)",),
            de_donde=f"el criterio '{CRITERIO_RIESGO_PROPIETARIO}'",
            por_que="el Propietario ejercio la decision que la nota al pie de "
                    "la tabla le asigna, por debajo de los maximos "
                    "recomendados. La via solo admite ENDURECER el techo",
            cita_id="MC_HHD.3.6",
            clave_criterio=CRITERIO_RIESGO_PROPIETARIO))
    else:
        elecciones.append(EleccionDeProyecto(
            que_se_adopto="riesgo admisible y vida util",
            valor=f"R = {R}, n = {n} anios",
            entre=("cualquier R menor, que daria un TR mayor y un caudal de "
                   "diseño mayor",),
            de_donde="los MAXIMOS RECOMENDADOS de la propia tabla",
            por_que="el Propietario no ha declarado otros por la via que "
                    f"tiene para hacerlo ('{CRITERIO_RIESGO_PROPIETARIO}'). "
                    "ADVERTENCIA: adoptar el maximo recomendado es el extremo "
                    "MENOS conservador del margen que la tabla concede, al "
                    "reves que en V1 y V2",
            cita_id="MC_HHD.3.6",
            clave_criterio=CRITERIO_RIESGO_PROPIETARIO))
    u = UMBRALES_POR_CODIGO["TR"]
    return paso(
        "F2.TR",
        codigo="2.2",
        que="Periodo de retorno del caudal de diseño",
        formula="R = 1 - (1 - 1/T)^n, despejada en T: "
                "T = 1 / (1 - (1 - R)^(1/n))",
        formula_cita_id="MC_HHD.3.6",
        citas_textuales=("MC_HHD.3.6",),
        sustitucion=(
            Magnitud("R", R, "",
                     f"riesgo admisible de falla de la fila "
                     f"«{TABLA_02_FILAS[cat.value]['fila']}»",
                     cifras=CIFRAS_FACTOR),
            Magnitud("n", n, "anios",
                     "vida util de la misma fila, que la tabla escribe en su "
                     "nota al pie (**)")),
        resultado=Magnitud("TR", round(exacto), "anios",
                           f"redondeo al anio de {exacto:.2f}, que es el "
                           f"valor que la columna «TR de diseño» de la tabla "
                           f"publica", cifras=None),
        umbral=Umbral(
            descripcion="riesgo admisible maximo recomendado para esta fila",
            valor=RIESGO_ADMISIBLE[cat.value]["R"], unidad="",
            cita_id="MC_HHD.3.6",
            caracter=caracter_del_umbral(u),
            aplicacion=u["aplicacion"]),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.CUMPLE,
            margen=RIESGO_ADMISIBLE[cat.value]["R"] - R, unidad="",
            explicacion="el riesgo adoptado no excede el maximo recomendado "
                        "de la tabla"),
        elecciones=tuple(elecciones),
    )


def tr_de_categoria(categoria: CategoriaLike,
                    id_punto: Optional[str] = None,
                    fundamento: str = "") -> PeriodoRetorno:
    """
    TR de una fila de la Tabla N 02, calculado, no copiado (Sec. 2.2).

    El redondeo al anio es el de la propia tabla: la columna "TR de diseno"
    publica 71 y 35, que son 70.59 y 35.32 redondeados. Se conserva el valor
    exacto en `exacto` para que el redondeo sea visible y no un dato perdido.

    QUE CLASE DE VALORES SON R Y n (NOR-HID-08). Maximos RECOMENDADOS, no
    exigencias: el titulo de la Tabla N 02 lo dice, el texto que la introduce
    dice "se recomienda utilizar como maximo" y la nota al pie remata que "El
    Propietario de una Obra es el que define el riesgo admisible de falla y la
    vida util de las obras". Adoptarlos tal cual es una decision del proyecto,
    y es la MENOS conservadora que la tabla admite: mas riesgo admisible da
    menos TR y menos caudal de diseno. `fundamento` lo lleva escrito para que
    la memoria no presente como umbral normativo lo que es un techo
    recomendado adoptado.
    """
    cat = _categoria(categoria, id_punto)
    fila = RIESGO_ADMISIBLE[cat.value]
    R, n = fila["R"], fila["n"]
    R, n, adoptado_por_propietario = _riesgo_del_propietario(cat, R, n)
    exacto = tr_desde_riesgo(R, n)
    return PeriodoRetorno(
        paso=_paso_tr(cat=cat, R=R, n=n, exacto=exacto,
                      del_propietario=adoptado_por_propietario),
        procede=True,
        categoria=cat,
        R=R,
        n=n,
        exacto=exacto,
        anios=round(exacto),
        numeral=NUMERAL_TR,
        fundamento=fundamento or (
            f"fila \"{TABLA_02_FILAS[cat.value]['fila']}\" de la Tabla N 02 "
            f"(R = {R}, n = {n} anios). " + (
                f"Valores DECLARADOS POR EL PROPIETARIO en el criterio "
                f"'{CRITERIO_RIESGO_PROPIETARIO}', por debajo de los maximos "
                f"recomendados de la tabla, que son R = "
                f"{RIESGO_ADMISIBLE[cat.value]['R']} y n = "
                f"{RIESGO_ADMISIBLE[cat.value]['n']} anios"
                if adoptado_por_propietario else
                "Son los valores MAXIMOS RECOMENDADOS de la tabla, adoptados "
                "por el proyecto: la nota al pie deja la decision al "
                "Propietario de la obra, que no ha declarado otros por la via "
                f"que tiene para hacerlo (criterio "
                f"'{CRITERIO_RIESGO_PROPIETARIO}')")),
        id_punto=id_punto,
    )


def periodo_retorno_de(punto: PuntoCritico,
                       categoria: Optional[CategoriaLike] = None) -> PeriodoRetorno:
    """
    TR del punto segun su familia (Sec. 2.2 + Sec. 2.3).

        Familia A  la hoja de ruta admite 71 o 35 y no dice cual. Se usa la
                   categoria declarada por el que llama; si no la hay, se lee
                   el criterio pendiente y el calculo se detiene.
        Familia B  fila fija: alcantarilla de alivio = descarga de cunetas ->
                   quebrada menor -> TR 35 anios (Sec. 2.3, explicito).
        Familia C  no tiene TR: su caudal es el de diseno del canal, que fija
                   la ANA o la Junta de Usuarios (Tablero 3.1).
    """
    perfil = perfil_de(punto.familia)

    if punto.familia is Familia.C:
        return PeriodoRetorno(
            procede=False, categoria=None, R=None, n=None, exacto=None,
            anios=None, numeral=NUMERAL_TR,
            fundamento="Familia C: el caudal es el de diseno del canal o dren "
                       "(ANA / Junta de Usuarios, Tablero 3.1), no un caudal "
                       "hidrologico con periodo de retorno propio (Sec. 2.3)",
            id_punto=punto.id,
        )

    if categoria is not None:
        cat = _categoria(categoria, punto.id)
        if perfil.categoria_tr is not None and cat is not perfil.categoria_tr:
            raise DatoInvalidoError(
                "familia", valor=cat.value, id_punto=punto.id,
                motivo=f"la Familia {punto.familia.value} tiene fila fija en la "
                       f"Tabla N 02 ('{perfil.categoria_tr.value}', Sec. 2.3) y "
                       "no admite otra categoria")
        return tr_de_categoria(
            cat, punto.id,
            fundamento=f"categoria '{cat.value}' declarada para el cauce del "
                       f"punto; fila de la Tabla N 02 con R = "
                       f"{RIESGO_ADMISIBLE[cat.value]['R']} y n = "
                       f"{RIESGO_ADMISIBLE[cat.value]['n']} anios")

    if perfil.categoria_tr is not None:
        return tr_de_categoria(
            perfil.categoria_tr, punto.id,
            fundamento=f"Familia {punto.familia.value} ({perfil.nombre}): "
                       f"{perfil.origen_del_caudal}, que es la fila "
                       f"'{perfil.categoria_tr.value}' de la Tabla N 02 (Sec. 2.3)")

    return tr_de_categoria(
        _categoria_por_area(punto), punto.id,
        fundamento=f"categoria derivada del area de cuenca "
                   f"({punto.area_ha} ha) con el criterio "
                   f"'{CRITERIO_CATEGORIA_A}'")


def _categoria_por_area(punto: PuntoCritico) -> CategoriaTR:
    """
    Unica via automatica para la Familia A, y esta bloqueada a proposito: el
    criterio no tiene valor y `valor()` lanza CriterioPendienteError antes de
    mirar el area. Si algun dia se le pone umbral, el area de cuenca -- el dato
    que Sec. 1.1 llama "solo clasificador" -- decide la fila.

    La tolerancia va del lado conservador: en el empate exacto gana quebrada
    importante, que es la fila de TR mayor y por tanto de mayor caudal.
    """
    umbral = valor(CRITERIO_CATEGORIA_A)
    area = punto.exigir("area_ha")
    if area >= umbral - TOL_UMBRAL_NORMATIVO:
        return CategoriaTR.QUEBRADA_IMPORTANTE
    return CategoriaTR.QUEBRADA_MENOR


def _categoria(categoria: CategoriaLike,
               id_punto: Optional[str] = None) -> CategoriaTR:
    try:
        cat = CategoriaTR(categoria)
    except ValueError:
        raise DatoInvalidoError(
            "categoria_tr", valor=categoria, id_punto=id_punto,
            motivo="las filas de la Tabla N 02 (Sec. 2.2) son "
                   f"{', '.join(c.value for c in CategoriaTR)}",
        ) from None
    if cat.value not in RIESGO_ADMISIBLE:
        raise DatoInvalidoError(
            "categoria_tr", valor=categoria, id_punto=id_punto,
            motivo=f"'{cat.value}' no tiene fila en RIESGO_ADMISIBLE "
                   "(Anexo B, Tabla N 02)")
    return cat


# ---------------------------------------------------------------------------
# Sec. 2.3 - Familias
# ---------------------------------------------------------------------------
# La familia llega declarada en el CSV (Sec. 1.1: dato de entrada "de Fase 2")
# y M0 ya la valido contra el enum. Lo que se declara aqui es lo que cada
# familia implica para el resto del calculo. Texto, no numeros: el unico umbral
# numerico que menciona Sec. 2.3 -- los 1.5 m de terraplen que separan el
# tratamiento sin bordillo del tratamiento con bordillo y bajantes -- pertenece
# al drenaje longitudinal y lo resuelve M10 (Fase 10), que ademas necesita un
# dato que Sec. 1.2 no trae: si el punto cae en curva peraltada.

PERFILES: Dict[Familia, PerfilFamilia] = {

    Familia.A: PerfilFamilia(
        familia=Familia.A,
        nombre="Alcantarillas de paso",
        origen_del_caudal="Q hidrologico propio de la cuenca (Tc.py + IDF con "
                          "el TR de la Fase 2)",
        categoria_tr=None,          # "TR 71 o 35 anios": la hoja no fija cual
        campos_requeridos=("Q_m3s", "area_ha", "S_cauce"),
        verificaciones_aceptacion=("V1", "V2", "V4", "V5"),
        notas=(
            "La fila de la Tabla N 02 no esta fijada por la familia: se declara "
            f"por punto o se resuelve con el criterio '{CRITERIO_CATEGORIA_A}'.",
        ),
        numeral=NUMERAL_FAMILIA,
    ),

    Familia.B: PerfilFamilia(
        familia=Familia.B,
        nombre="Alcantarillas de alivio",
        origen_del_caudal="Q del drenaje longitudinal (cuneta)",
        categoria_tr=CategoriaTR.QUEBRADA_MENOR,   # "descarga de cunetas" -> TR 35
        campos_requeridos=("Q_m3s",),
        verificaciones_aceptacion=None,            # Sec. 2.3 no declara conjunto propio
        notas=(
            "El espaciamiento lo fija la Fase 10 (M10) a partir de la longitud "
            "maxima de cuneta, criterio 'long_max_cuneta'.",
            "Tratamiento del terraplen segun su altura -- sin bordillo con "
            "geomalla, o con bordillo y bajantes a ambos lados, a un solo lado "
            "en curvas peraltadas -- es regla de Sec. 2.3 que resuelve M10: "
            "depende de la altura de terraplen y de si el punto cae en curva "
            "peraltada, y ninguno de los dos es columna de Sec. 1.2.",
        ),
        numeral=NUMERAL_FAMILIA,
    ),

    Familia.C: PerfilFamilia(
        familia=Familia.C,
        nombre="Cruces de canales y drenes",
        origen_del_caudal="Q de diseno del canal (ANA / Junta de Usuarios del "
                          "Bajo Piura)",
        categoria_tr=None,          # no hay TR: el caudal no es hidrologico propio
        campos_requeridos=("Q_m3s",),
        verificaciones_aceptacion=None,            # Sec. 2.3 no declara conjunto propio
        notas=(
            "No puede alterar la rasante hidraulica ni el borde libre del canal.",
            "Requiere autorizacion de obras en fuente natural / faja marginal.",
            "Seccion: marco o multicelda.",
            "Bloqueada por falta del dato de la ANA (Tablero 3.1): el Q propio "
            "del canal es el que fija el diseno.",
        ),
        numeral=NUMERAL_FAMILIA,
    ),
}


def perfil_de(familia: Union[Familia, str]) -> PerfilFamilia:
    """Lo que implica la familia declarada en el CSV (Sec. 2.3)."""
    try:
        clave = Familia(familia)
    except ValueError:
        raise DatoInvalidoError(
            "familia", valor=familia,
            motivo="las familias de Sec. 2.3 son "
                   f"{', '.join(f.value for f in Familia)}",
        ) from None
    return PERFILES[clave]


def datos_pendientes(punto: PuntoCritico) -> Tuple[str, ...]:
    """
    Campos que la familia del punto necesita y la fila trajo vacios. No lanza:
    marca, como hace M0. Quien decide si el punto se puede calcular sin ellos
    es el modulo que los necesite.
    """
    perfil = perfil_de(punto.familia)
    return tuple(campo for campo in perfil.campos_requeridos
                 if getattr(punto, campo) is None)


# ---------------------------------------------------------------------------
# Clasificacion completa de un punto
# ---------------------------------------------------------------------------

def clasificar(punto: PuntoCritico,
               luz_m: Optional[float],
               categoria_tr: Optional[CategoriaLike] = None) -> Clasificacion:
    """
    Fase 2 completa para un punto: denominacion (Sec. 2.1), perfil de familia
    (Sec. 2.3) y periodo de retorno (Sec. 2.2).

    Si la luz lo hace puente, el TR no se resuelve: se devuelve con
    procede=False y el motivo. Es deliberado -- intentar el TR de un punto
    fuera de alcance puede disparar el criterio pendiente de la Familia A y la
    GUI mostraria "falta declarar: umbral..." cuando el problema real es que el
    cruce es un puente.
    """
    verificacion = verificar_luz(luz_m, punto.id)
    denominacion = (Denominacion.ALCANTARILLA if verificacion.cumple
                    else Denominacion.PUENTE)
    perfil = perfil_de(punto.familia)

    if denominacion is Denominacion.PUENTE:
        tr = PeriodoRetorno(
            procede=False, categoria=None, R=None, n=None, exacto=None,
            anios=None, numeral=NUMERAL_TR,
            fundamento=f"punto fuera de alcance: con luz {float(luz_m)} m la "
                       f"estructura es un puente (num. {NUMERAL_LUZ}) y su "
                       "periodo de retorno lo fija el Manual de Puentes",
            id_punto=punto.id,
        )
    else:
        tr = periodo_retorno_de(punto, categoria_tr)

    return Clasificacion(
        punto=punto,
        luz_m=float(luz_m),
        denominacion=denominacion,
        verificacion_luz=verificacion,
        perfil=perfil,
        periodo_retorno=tr,
        datos_pendientes=datos_pendientes(punto),
    )


def clasificar_puntos(puntos: List[PuntoCritico],
                      luces: Mapping[str, float],
                      categorias: Optional[Mapping[str, CategoriaLike]] = None
                      ) -> List[Clasificacion]:
    """
    Clasifica una tanda de puntos. `luces` y `categorias` van por id de punto:
    la luz porque no es columna de Sec. 1.2, y la categoria porque la fila de
    la Tabla N 02 de la Familia A se declara cauce por cauce.
    """
    categorias = categorias or {}
    return [clasificar(punto, luces.get(punto.id), categorias.get(punto.id))
            for punto in puntos]
