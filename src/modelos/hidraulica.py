"""
src/modelos/hidraulica.py
=========================
Hidraulica del barril, TW (Sec. 1.3), resultados de la Fase 5, proteccion de salida y socavacion.

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple

from src.modelos.base import ControlGobernante, RegimenBarril

if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.base import RegimenEntrada, TipoDePerfil
    from src.modelos.conducto import ConstantesHDS5, Geometria
    from src.modelos.memoria import Magnitud, PasoDeMemoria

@dataclass(frozen=True)
class TiranteNormal:
    """
    Salida de M3 (Sec. 4.1): tirante normal resuelto por Manning + Brent con
    la regla de doble n, UN TIRANTE POR CADA EXTREMO del rango de n (VE-2).

    `geometria` es la solucion de Brent con n_max (rama de capacidad y
    tirante: V1 borde libre) -- el n mas conservador del lado de la
    inundacion fija el theta real de diseño --, y `geometria_erosion` la de
    n_min, sobre la misma ecuacion, la misma seccion y el mismo Q: un tirante
    MENOR. Cada velocidad es la de SU tirante, porque un umbral de velocidad
    no tiene un extremo conservador sino dos, y son opuestos:

        `V_erosion`        con n_min: Q / geometria_erosion.A, la estimacion
                           ALTA. Es la que hay que usar contra un TECHO -- V3
                           (velocidad maxima admisible) y el d50 de Laushey
                           (Fase 6) --, porque el riesgo esta en que la
                           velocidad real sea mayor que la calculada.
        `V_sedimentacion`  con n_max: la estimacion BAJA. Es la que hay que
                           usar contra un PISO -- V2 (velocidad minima de
                           autolimpieza) --, porque ahi el riesgo es el
                           contrario: que la velocidad real sea MENOR que la
                           calculada y el conducto sedimente.

    POR QUE HAY DOS Y NO UNA (MAT-D1). Este tipo llevaba un solo campo `V`,
    calculado con n_min, y V2 lo consumia: un piso verificado con la
    estimacion alta de velocidad, o sea el conservadurismo invertido. La
    Sec. 4.1 de la hoja de ruta asigna n minimo a "velocidad MAXIMA y
    socavacion" y no nombra a V2; el fixture CP-3 modela el umbral de V2 con
    n = 0.013, que es n_max. El repositorio se contradecia a si mismo, y la
    ventana permisiva era real: con D = 0.90 m, y/D = 0.75 y S = 5e-5, la
    velocidad de la rama n_max es 0.228 m/s -- por debajo del piso de
    0.25 m/s -- mientras que la de la rama n_min daba 0.297 m/s y el punto
    salia "cumple".

    LAS DOS CUMPLEN LA CONTINUIDAD, CADA UNA CON SU AREA (VE-2, decision (b)
    de la ficha VE1-02, aprobada el 2026-11-17):
    `V_erosion * geometria_erosion.A = Q` y `V_sedimentacion * geometria.A =
    Q`, hasta `tolerancias.TOL_REL_CONTINUIDAD_MANNING`. HASTA VE-2 ESTE
    DOCSTRING DECIA LO CONTRARIO, «V_erosion * geometria.A != Q en general»,
    y era cierto: `V_erosion` era la velocidad de n_min SOBRE LA GEOMETRIA DE
    n_max, V*A = Q*n_max/n_min (1.3*Q en el concreto), un caudal que no pasa
    por el conducto. Se corrigio porque ninguna fuente toma el tirante de un
    n y la velocidad de otro: HDS-5 num. 3.3.2 (pag. impresa 3.24) «The
    velocity at normal depth is assumed to be the outlet velocity» y HEC-14
    num. 3.2.2 (pag. impresa 3-7), cuyo ejemplo de la pag. 3-8 resuelve un
    tirante por cada n. Sobre la geometria de n_max, `V_erosion * A` sigue
    siendo mayor que Q (A(n_max) > A(n_min)), y eso es lo que se espera.

    Eso convierte a cada una en el extremo REAL de la velocidad sobre el
    rango de n de la Tabla N 09, no solo en "la de una geometria": con un n
    menor el tirante normal baja, el area baja y la velocidad media Q/A sube.
    La cadena vale mientras theta este en la RAMA CRECIENTE de la curva de
    capacidad de la seccion circular -- Q(theta) no es monotona: alcanza su
    maximo cerca de y/D = 0.94 y decae hasta la seccion llena --, y ahi esta
    siempre el diseño de este proyecto, porque V1 lo acota en y/D <= 0.75
    (num. 4.1.1.3.7 b). Se dice y no se da por supuesto: por encima de ese
    maximo la relacion theta(n) deja de ser creciente y el argumento no
    aplicaria.

    `geometria_erosion` viaja para que la memoria imprima el tirante con que
    se midio `V_erosion` (pasos 4.1 y 4.3b de M4). No es el tirante de
    registro: el que se publica como `y_normal`, el que V1 juzga y el que
    M4 da como tirante de salida bajo control de entrada es el de n_max.
    """

    geometria: Geometria          # con n_max  - tirante de capacidad (V1)
    V_erosion: float              # m/s, Q / geometria_erosion.A - ALTA (techos)
    V_sedimentacion: float        # m/s, con n_max  - estimacion BAJA (pisos)
    geometria_erosion: Geometria  # con n_min  - el tirante de V_erosion (VE-2)


@dataclass(frozen=True)
class SinTiranteNormal:
    """
    --- T-2 --- Lo que M3 devuelve cuando el barril es HORIZONTAL (S = 0): no
    hay tirante normal, y eso no es «el conducto no alcanza» (INF-5.1.6).

    TRES RESPUESTAS DISTINTAS DE `M3.resolver_manning`, y esta es la tercera:

        TiranteNormal      hay flujo uniforme que transporta Q.
        None               con esta S > 0 ningun tirante transporta Q en
                           lamina libre: el escalon no alcanza y MD pasa al
                           siguiente.
        SinTiranteNormal   S = 0: Manning no tiene solucion para NINGUN
                           caudal ni NINGUNA seccion, y subir de diametro no
                           lo cambia. No es un fallo del escalon: es otro
                           regimen. HDS-5 num. 3.3.4 (pag. impresa 3.25,
                           `HDS5_3ED.3.3.4#HORIZONTAL`) admite el barril
                           horizontal, y M4 lo resuelve con el control de
                           entrada (Ks·S = 0), el de salida (S·L = 0) y el
                           perfil de la lamina desde la salida (H2).

    Es un objeto y no un `None` con otro nombre para que quien lo reciba no
    pueda confundir las dos lecturas: `if normal is None` sigue significando
    lo de siempre. No lleva geometria ni velocidades porque no las hay; lleva
    la pendiente con que se pidio, para que el paso de memoria la imprima.
    """

    S: float = 0.0            # m/m - la pendiente del barril: nula


@dataclass(frozen=True)
class TiranteCritico:
    """
    Salida de la primera pieza de M4 (Sec. 4.2.1): tirante critico de la
    seccion, raiz de Q^2*T/(g*A^3) = 1.

    `cerrado` DICE POR CUAL DE LAS DOS VIAS SE RESOLVIO, y no es un detalle de
    implementacion: es lo que la memoria tiene que imprimir. En la circular la
    ecuacion es trascendente en theta y hace falta un segundo Brent; en un
    marco T = B es constante y se despeja, y_c = (q^2/g)^(1/3). Un revisor que
    lea "resuelta con Brent" sobre un numero que salio de una formula cerrada
    no puede rehacerlo, y al reves tampoco. Lo pone la seccion y no lo deduce
    el que imprime.

    `geometria` es la seccion en estado critico (de ella salen y_c, A_c y T_c);
    `V` = Q/A_c es la velocidad critica, y `H_c` = y_c + V^2/(2g) la energia
    especifica critica que exige la Forma 1 del control de entrada.

    Aqui V es Q/A y hay UNA sola: el tirante critico no depende de la
    rugosidad -- no interviene n en Q^2*T/(g*A^3) = 1 -- y por lo tanto la
    regla de doble n (Sec. 4.1) no le aplica: la ecuacion que la define no
    tiene rama de capacidad ni rama de erosion. (Decia que era «la unica
    velocidad del proyecto que se obtiene dividiendo Q entre A»; desde VE-2
    las dos de `TiranteNormal` tambien lo son, cada una con el area de su
    tirante, y desde EXT-3 lo eran las de salida y de barril lleno de M4.)
    """

    geometria: Geometria      # seccion en estado critico
    V: float                  # m/s - velocidad critica, Q/A_c
    H_c: float                # m  - energia especifica critica, y_c + V^2/(2g)
    cerrado: bool             # True si la seccion lo despejo; False si Brent

    @property
    def y_c(self) -> float:
        """Tirante critico, m."""
        return self.geometria.y


@dataclass(frozen=True)
class TransicionEntrada:
    """
    Los dos extremos de la recta de transicion del control de entrada
    (3.5 < q* < 4.0), con el caudal y el H_c con que se evaluo el inferior.

    EXISTE POR EXT-M-04. «La rama no sumergida en q* = 3.5» es la del CAUDAL
    que corresponde a q* = 3.5 -- `Q_lo` = 3.5 * A_llena * sqrt(D) / Ku -- y,
    bajo Forma 1, con el H_c de ESE caudal, `H_c_lo`. Hasta EXT-2 el extremo
    se evaluaba con el H_c del caudal real, de modo que se movia con q* y lo
    que la memoria imprimia como «recta» era una curva (v8 §4.2, enmendada
    en EXT-0). Los cuatro numeros viajan para que el paso F4.CONTROL los
    sustituya: un HW «por la recta» sin sus dos extremos no se puede rehacer.

    `H_c_lo` es `None` bajo Forma 2: la ec. (A.2) no lleva H_c, y publicar
    un H_c que no entra en el numero seria la clase de sustitucion falsa que
    C3 tuvo que corregir en ese mismo paso.
    """

    Q_lo: float                   # m3/s - el caudal de q* = 3.5
    H_c_lo: Optional[float]       # m    - H_c(Q_lo); None bajo Forma 2
    HW_lo: float                  # m    - rama no sumergida en q* = 3.5, * D
    HW_hi: float                  # m    - rama sumergida en q* = 4.0, * D
    peso: float                   # adimensional - (q* - 3.5) / (4.0 - 3.5)


@dataclass(frozen=True)
class ControlEntrada:
    """
    Salida del control de entrada HDS-5 (Sec. 4.2). Ademas del HW lleva el
    q* y la rama aplicada: son lo que hace revisable el numero en la memoria.

    `HW` es carga sobre el fondo de la entrada, en metros. `HW_sobre_D` es el
    HWi/D adimensional que devuelven las ecuaciones de la Tabla A.1, antes de
    multiplicar por D.

    `HW_sobre_D` NO LO LEE NINGUNA RUTA DE PRODUCCION, y este docstring ha
    dicho dos cosas falsas sobre el, las dos de la misma familia: predecir un
    consumidor que no existia.

    Primero decia que era "lo que compara V4b (HW/D <= 1.5)" (SIS-B-02,
    SIS-A-02), cuando M5 ni siquiera implementaba V4b. Corregido eso, decia
    que "sera el argumento del chequeo el dia que se cablee". El chequeo se
    cableo en S14 y el argumento NO es este campo: `M5.v4b_relacion_hw_d`
    divide entre D el HW del control GOBERNANTE, porque lo que la fuente
    acota es el embalse que la obra produce, y este campo es el HWi/D del
    control de ENTRADA, valido solo cuando ese control gobierna. Usarlo daria
    un numero menor que el embalse real siempre que gobierne el de salida,
    que es la direccion insegura.

    El campo se conserva por lo que SI es -- la salida literal de las
    ecuaciones de la Tabla A.1, la magnitud con la que HDS-5 razona, y
    multiplicarla por D para volver a dividirla despues seria perderla y
    recomponerla -- y lo que se dice de el es lo unico que se puede sostener:
    que hoy solo lo leen los tests. Sin consumidor y con la razon escrita, no
    sin consumidor y con un consumidor prometido.
    """

    HW: float                     # m  - HWi
    HW_sobre_D: float             # adimensional - HWi/D
    q_estrella: float             # adimensional - Ku*Q/(A_llena*D^0.5)
    regimen: RegimenEntrada
    critico: TiranteCritico
    constantes: ConstantesHDS5
    # LOS DOS EXTREMOS DE LA RECTA, cuando la rama es la de transicion
    # (EXT-M-04). `None` en las dos ramas puras: ahi no hay recta. Ver
    # `TransicionEntrada`.
    transicion: Optional["TransicionEntrada"] = None
    # EL PISO ADOPTADO cuando la correccion por pendiente dejo la ecuacion
    # fuera de rango (PF-1, PC-03). `None` siempre que la ecuacion entrego
    # carga por si sola, que es todo el corredor del repositorio. Ver
    # `PisoDeCargaEntrada`.
    piso: Optional["PisoDeCargaEntrada"] = None
    numeral: str = "HDS-5 Ap. A, Tabla A.1 (Sec. 4.2)"


@dataclass(frozen=True)
class PisoDeCargaEntrada:
    """
    Lo que M4 adopto en lugar del HWi/D que la ecuacion de control de
    entrada devolvio en cero o bajo cero (MAT-D10 / PC-03, cerrado en PF-1).

    La correccion por pendiente Ks*S de las ecs. (A.1) y (A.3) es una recta
    sin tope: con Ks = -0.5, un caudal chico y una pendiente grande la carga
    sale NEGATIVA, que es una lamina bajo el fondo del conducto. Hasta PF-1
    eso era un `DisenoNoFactibleError` definitivo y mudo --- el `Bloqueo`
    viajaba sin `criterio` y la pestaña 4 no lo mostraba ---. Desde PF-1 es
    un vacio DECLARABLE de perfil: el criterio [A] `hw_entrada_fuera_de_rango`
    decide si se adopta la energia especifica critica H_c como piso
    («energia_critica») o si el caso se descarta («descartar»); sin
    declarar, `CriterioPendienteError` con el par (Q, S) culpable y S*.

    `HW_sobre_D_formula` es lo que la ecuacion devolvio (<= 0), conservado
    para que la memoria lo imprima al lado del piso; `S_limite` es la
    pendiente S* a partir de la cual la ecuacion deja de entregar carga
    para ese Q y ese D (None si la rama no depende de S), y es lo que le
    dice al revisor cuanta pendiente sobra.
    """

    criterio: str
    adoptado: str
    HW_sobre_D_formula: float
    S_limite: Optional[float]


@dataclass(frozen=True)
class ControlSalida:
    """
    Salida del control de salida (Sec. 4.3): HW = H + h_o - S*L.

    Se guardan los tres sumandos por separado porque cada uno responde a una
    pregunta distinta del revisor: `H` es la perdida total en el barril
    (entrada + friccion + carga de velocidad), `h_o` es el nivel de agua a la
    salida que la manda aguas arriba, y `S*L` es la caida del conducto.

    `ahogado_por_TW` distingue las dos ramas de h_o = max(TW, (y_c + D)/2): si
    es True, el que gobierna el remanso es el nivel del cuerpo receptor y no
    la geometria del conducto. Es la situacion que Sec. 4.3 advierte
    expresamente para descargas a drenes con nivel propio.

    Y SE IMPRIME (SIS-B-18). La ficha lo señalaba como el unico de cinco
    campos escritos y nunca leidos que ademas no viajaba ni al JSON ni al
    HTML: una rama que el codigo distingue y el revisor no ve. Dejo de serlo
    en S18 sin que nadie lo buscara --- `M4._pasos_hidraulicos` lo lee para
    redactar la procedencia de h_o en su `PasoDeMemoria`, «(manda TW: la
    salida esta ahogada)» frente a «(manda la aproximacion geometrica)» ---,
    de modo que hoy la rama llega a la memoria como texto y con su razon.
    Lo fija `tests/test_M4_control.py`.

    Y AL JSON LLEGA DESDE EXT-3, con el bloque h_o ENTERO y no solo la
    etiqueta de la rama: `h_o`, `TW`, `ahogado_por_TW`, `HW_sobre_D` y los
    dos flags viajan a `ResultadoHidraulico` y de ahi a `cli._diseno_json` y
    a `cli.volcar` (SIS-B-18, mitad JSON). Hasta entonces no llegaba ninguna
    pieza del bloque, y la decision de S19 era que publicar la etiqueta sin
    los dos numeros que la producen seria menos revisable que no publicarla:
    por eso se abrio al bloque completo y no a un campo.

    `h_o_fuera_de_rango` y `h_o_requiere_cautela` son las DOS condiciones de
    uso que HDS-5 pone a esa aproximacion y que el proyecto puede evaluar
    (NOR-HDS-05, num. 3.3.3, pag. impresa 3.24): por debajo de HW/D = 0.75 la
    fuente dice que la aproximacion no debe usarse, y por debajo de 1.2 pide
    cautela porque el barril puede fluir parcialmente lleno. Son banderas y no
    excepciones a proposito: la fuente no prohibe calcular, dice que el numero
    no es de fiar, y quien decide que hacer con un punto asi es el revisor.
    Viajan a `ResultadoHidraulico` -- ya filtradas por si el control de salida
    gobierna, que es la condicion con que la fuente las escribe -- y de ahi a
    la memoria del punto.

    La tercera condicion de la fuente -- que el barril fluya lleno en la mayor
    parte de su longitud -- NO tiene bandera porque no se puede evaluar sin un
    perfil de la lamina de agua. Queda declarada en
    `constantes_normativas.H_O_CONDICION_APLICACION`.
    """

    HW: float                     # m  - carga sobre el fondo de la entrada
    H: float                      # m  - perdida total en el barril
    h_o: float                    # m  - max(TW, (y_c + D)/2)
    TW: float                     # m  - tirante en el cuerpo receptor
    caida: float                  # m  - S*L
    V: float                      # m/s - velocidad de referencia del barril
    R: float                      # m  - radio hidraulico de referencia
    ahogado_por_TW: bool
    critico: TiranteCritico
    HW_sobre_D: float = 0.0       # adimensional - HW/D, lo que acotan las dos
                                  # condiciones de uso de h_o
    h_o_fuera_de_rango: bool = False      # HW/D < 0.75 (num. 3.3.3)
    h_o_requiere_cautela: bool = False    # HW/D < 1.2  (num. 3.3.3)
    # EL ke CON QUE SE CALCULO H, y no es redundante con el criterio: quien
    # lea el criterio lee lo que el expediente DECLARO; este campo dice lo que
    # la ecuacion USO. Viaja desde C5 porque el marco lo declara como CLAVE DE
    # FILA de la Tabla C.2 y no como numero -- en el bloque del cajon el mismo
    # coeficiente aparece hasta en tres filas --, de modo que sin este campo
    # el paso de memoria tendria que volver a resolver la clave y habria dos
    # sitios donde el numero se decide. `ke_fila` y `ke_agrupacion` van con el
    # porque la fila suelta no identifica nada (ver 'ke_entrada_cajon'); en el
    # tubo salen vacios: alli el criterio es un numero declarado.
    ke: float = 0.0               # adimensional - coef. de perdida de entrada
    ke_criterio: str = ""         # clave en criterios_adoptados.py
    ke_fila: str = ""             # rotulo LITERAL de la fila de la Tabla C.2
    ke_agrupacion: str = ""       # rotulo de agrupacion de esa fila
    ke_bloque: str = ""           # familia de la tabla: «Box, Reinforced
                                  # Concrete», «Pipe, Concrete»... Viaja con
                                  # los otros dos porque la memoria lo IMPRIME,
                                  # y estuvo CABLEADO en el texto hasta que la
                                  # auditoria de C5 mostro que asi la
                                  # procedencia no se podia desmentir
    numeral: str = "Sec. 4.3"


@dataclass(frozen=True)
class PerfilLamina:
    """
    El perfil de la lamina de agua a lo largo del barril, resuelto por PASO
    DIRECTO desde la salida hacia la entrada (E-A; NOR-HDS-05 cerrada). Es
    el procedimiento de barril parcialmente lleno del Cap. III del HDS-5,
    tal como la pag. impresa 3.12 (PDF 94) lo escribe: el calculo «begin[s]
    at the water surface at the downstream end of the culvert and proceed[s]
    upstream to the entrance», la frontera aguas abajo es «critical depth at
    the culvert outlet or … the tailwater depth, whichever is higher», y
    donde la lamina toca la clave se empalma «a straight, full flow hydraulic
    grade line» con la pendiente de friccion de la Ec. 3.7. Lo resuelve
    `M4.perfil_lamina`; este tipo es lo que sale.

    ES UN TIPO PROPIO Y NO DIEZ CAMPOS SUELTOS EN `ResultadoHidraulico`, a
    proposito (prompt de E-A: «no ampliar ResultadoHidraulico a ciegas»):
    `ResultadoHidraulico.perfil` es UN campo, y quien necesite el perfil lo
    lee entero, con su tipo y su procedencia.

    Lo que entrega, y a quien:

        `fraccion_llena`, `longitud_llena_m`
            la PRIMERA SALIDA util: cuanto del barril va a seccion llena, que
            vuelve MEDIDA la primera condicion de uso de h_o («can only be
            used if the barrel flows full for most of its length», pag. 3.24)
            que hasta E-A solo se declaraba. La juzga el paso F4.PERFIL.
        `HW_remanso_m`, `y_entrada_m`, `V_entrada_m_s`
            la SEGUNDA: la carga a la entrada por remanso, HW = y_entrada +
            (1 + ke)·V_entrada²/2g (pag. 3.12: «The inlet losses and the
            velocity head are added to the elevation of the hydraulic grade
            line at the inlet»). `None` cuando el remanso NO alcanza la
            entrada (`alcanza_entrada=False`): la S1 corto y_c en
            `x_fin_remanso_m` < L, o tuvo longitud cero, y el control es de
            entrada (Section 3.5.1: la S1 se usa «if the S1 curve extends to
            the face of the culvert»). Para el HW esa lectura basta; el
            resalto lo situa por momentum, aparte, `M4.situar_resalto`
            (VE-5, ficha EA-02) y viaja en `ResultadoHidraulico.resalto`.
        `sustituye_aproximacion`
            True cuando HW_aproximado/D < 0.75, donde la fuente dice que la
            aproximacion h_o = max(TW, (y_c + D)/2) «should not be used» y
            que «backwater calculations are required» (pags. 3.24 y 3.12):
            ahi `ResultadoHidraulico.HW_salida` es `HW_remanso_m` y no
            `HW_aproximado_m`. Por encima de 0.75 la aproximacion sigue
            siendo el metodo --la pag. 3.12 la avala («adequate results are
            obtained down to a headwater of 0.75D»)-- y el remanso es la
            comprobacion que la pag. 3.24 pide («should be used to check the
            result from the approximate method»): en la banda de cautela
            (`cautela_aproximacion`, HW_aprox/D < 1.2) la comprobacion MANDA
            cuando pide mas carga (`comprobacion_manda`), y por encima de
            1.2 se imprime. Es la decision de la v8 §4.3 (EXT-0, nota de
            E-A), no una eleccion de esta pieza.
        `y_asintota_m`
            el tirante hacia el que tiende la lamina con la ley de friccion
            del perfil (la Ec. 3.7, donde Sf = S): un 0.05 % por encima del
            y_n de Manning de M3, porque K_FRICCION_SI/(2g) = 19.63/19.62.
            None cuando el perfil no tiene asintota bajo la clave (S1,
            crown, llena).
        `y_max_m`, `V_min_m_s`
            el tirante MAXIMO en lamina libre a lo largo del barril (D si hay
            tramo lleno) y la velocidad MINIMA, Q/A(y_max): lo que V1 y V2
            comparan bajo control de SALIDA con el barril parcialmente lleno,
            que hasta E-A quedaba pendiente por `MetodoNoEvaluableError`. Con
            n_max, como el resto del control de salida: mas tirante y menos
            velocidad, el lado conservador de las dos. Cuando la S1 no
            alcanza la entrada, el tramo supercritico aguas arriba del
            resalto se aproxima por el uniforme, como bajo control de entrada
            (EXT-3), y no mueve ninguno de los dos: en pendiente pronunciada
            y_n < y_c <= y_salida, de modo que el maximo esta en la salida.
        `estaciones`
            (x desde la salida, y) de cada rung de lamina libre que el paso
            directo resolvio, en orden aguas arriba. Sirven para rehacer el
            balance de energia estacion a estacion --E_arriba + S·Δx =
            E_abajo + Sf_medio·Δx-- que es la ecuacion del metodo; no van al
            JSON.

    `n` y `ke` son los que entraron: n_max (la regla de doble n manda el n
    mayor para una carga) y el ke con que `control_salida` formo H, para que
    el tramo lleno reproduzca la formula cerrada de la Sec. 4.3 exactamente.
    `rungs` es el numero de escalones de la escalera en el parametro propio
    de la seccion (`tolerancias.PASOS_PERFIL_LAMINA`): precision numerica,
    no un valor de proyecto.
    """

    tipo: TipoDePerfil
    y_salida_m: float                 # m  - frontera aguas abajo max(y_c, TW), acotada a D
    alcanza_entrada: bool             # False: la S1 corto y_c antes de la entrada
    x_fin_remanso_m: Optional[float]  # m  - donde termino el remanso si no alcanza
    y_entrada_m: Optional[float]      # m  - tirante (o carga de presion) en la entrada
    V_entrada_m_s: Optional[float]    # m/s
    HW_remanso_m: Optional[float]     # m  - y_entrada + (1 + ke) V^2/2g
    y_asintota_m: Optional[float]     # m  - donde la Ec. 3.7 da Sf = S (y_n'); None sin asintota
    longitud_llena_m: float           # m  - tramo a seccion llena
    fraccion_llena: float             # longitud_llena_m / L
    y_max_m: float                    # m  - tirante maximo (V1)
    V_min_m_s: float                  # m/s - velocidad minima, Q/A(y_max) (V2)
    n: float                          # n_max con que se resolvio
    ke: float                         # el ke de H
    HW_aproximado_m: float            # m  - el HW de la aproximacion (ControlSalida.HW)
    sustituye_aproximacion: bool      # HW_aproximado/D < 0.75: la aproximacion NO se usa
    cautela_aproximacion: bool        # HW_aproximado/D < 1.2: la banda de cautela
    rungs: int                        # escalones de la escalera
    estaciones: Tuple[Tuple[float, float], ...] = ()

    def __post_init__(self) -> None:
        # Guardias de coherencia interna, forma MAT-D13: en positivo y negadas.
        if not 0 <= self.fraccion_llena <= 1:
            raise ValueError(
                f"PerfilLamina: la fraccion llena ({self.fraccion_llena!r}) no "
                "esta en [0, 1]")
        if self.alcanza_entrada and self.HW_remanso_m is None:
            raise ValueError(
                "PerfilLamina: el remanso alcanza la entrada y no trae HW")
        if not self.alcanza_entrada and self.HW_remanso_m is not None:
            raise ValueError(
                "PerfilLamina: el remanso no alcanza la entrada y trae HW")
        if self.sustituye_aproximacion and not self.cautela_aproximacion:
            raise ValueError(
                "PerfilLamina: bajo 0.75 la aproximacion esta tambien bajo 1.2")

    @property
    def comprobacion_manda(self) -> bool:
        """
        True cuando, en la banda de cautela (0.75 <= HW_aprox/D < 1.2), el
        remanso alcanza la entrada y pide MAS carga que la aproximacion. La
        pag. 3.24 manda usar el remanso «to check the result from the
        approximate method», y una comprobacion que da mas carga no se puede
        descartar del lado de la inundacion: medido en E-A (auditoria
        adversarial), en 165 de 228 combinaciones de la banda el remanso
        superaba a la aproximacion, hasta +34 mm (+5 %). Por eso en la banda
        el HW efectivo es el MAYOR de los dos (v8 §4.3, nota de E-A).
        """
        return (self.cautela_aproximacion and not self.sustituye_aproximacion
                and self.HW_remanso_m is not None
                and self.HW_remanso_m > self.HW_aproximado_m)

    @property
    def HW_efectivo_m(self) -> Optional[float]:
        """
        La carga de control de SALIDA que el punto usa: el remanso donde
        sustituye a la aproximacion (HW_aprox/D < 0.75), el mayor de los dos
        en la banda de cautela (`comprobacion_manda`), la aproximacion en el
        resto; `None` si la aproximacion no se usa y el remanso no alcanza la
        entrada --el control de salida no impone carga alguna y gobierna la
        entrada--.
        """
        if self.sustituye_aproximacion:
            return self.HW_remanso_m
        if self.comprobacion_manda:
            return self.HW_remanso_m
        return self.HW_aproximado_m

    @property
    def salida_no_se_forma(self) -> bool:
        """
        --- T-12 (ficha T11-09) --- True cuando el control de SALIDA no
        impone carga: la aproximacion h_o se descarta (HW_aprox/D < 0.75,
        HDS-5 num. 3.3.3, pag. impresa 3.24: «should not be used») y el
        remanso que la sustituye no alcanza la entrada (`HW_remanso_m` None;
        Section 3.5.1). Es la condicion exacta en que `HW_efectivo_m` es
        None. La regla vive AQUI, en el dato, para que la CLI (JSON y linea
        «Control») y la memoria (fila «Control gobernante» de las dos vistas)
        la lean de un solo sitio; hasta T-12 vivia en `cli.salida_no_se_forma`
        y la memoria imprimia la aproximacion descartada como «salida».
        """
        return self.sustituye_aproximacion and self.HW_remanso_m is None


@dataclass(frozen=True)
class ResaltoHidraulico:
    """
    --- VE-5 (lote m45, item 17; fichas EA-02 y VE3-08) --- El resalto
    hidraulico resuelto por CANTIDAD DE MOVIMIENTO, HEC-14 num. 6.2, Ec.
    (6.1), pag. impresa 6-3 (PDF 66): «M = Q2/(gA) + AY … momentum is
    conserved through a hydraulic jump». Lo resuelve `M3.resalto_hidraulico`
    para cualquier forma del protocolo `Seccion`; cuando el conjugado no cabe
    bajo la clave la seccion 2 va llena y su «tirante» es la carga
    piezometrica sobre la solera, que es la Ec. (6.5) del circular (pag.
    impresa 6-8) escrita para cualquier forma (`lleno`).

    `x_desde_salida_m` lo pone M4 cuando SITUA el resalto dentro del barril
    (la S1 que sube desde el receptor contra la S2 que baja desde la
    entrada); `None` en el resalto suelto (los ejemplos resueltos de HEC-14).

    `V1`, `Fr1` son los de la seccion supercritica, con el Froude «computed
    using the maximum depth in the channel» (pag. impresa 6-9), y `V2` =
    Q / A2 es la velocidad tras el resalto del paso 3 de los ejemplos
    resueltos de HEC-14 (pags. impresas 6-6 y 6-11).
    """

    y1_m: float                       # m   - tirante supercritico (antes del resalto)
    A1_m2: float                      # m2
    V1_m_s: float                     # m/s
    Fr1: float                        # -   - V1 / sqrt(g y1), con el tirante maximo
    y2_m: float                       # m   - conjugado; carga piezometrica si `lleno`
    A2_m2: float                      # m2  - el area llena si `lleno`
    V2_m_s: float                     # m/s - Q / A2 (velocidad tras el resalto)
    lleno: bool                       # el conjugado no cabe bajo la clave (Ec. 6.5)
    x_desde_salida_m: Optional[float] = None   # m - donde lo situa M4

    @property
    def reduccion_de_velocidad(self) -> float:
        """(V1 - V2) / V1, como el paso 3 de los ejemplos de HEC-14."""
        return (self.V1_m_s - self.V2_m_s) / self.V1_m_s


# ===========================================================================
# Sec. 1.3 - TW: se calcula, no se mide
# ===========================================================================
# LOS DOS TIPOS DE LA SEC. 1.3, Y POR QUE SON DOS. `SeccionReceptor` es el
# DATO -- la geometria del dren o canal que recibe la descarga --, y
# `TWDeterminado` es el RESULTADO, con la via por la que se obtuvo. Separarlos
# permite que la memoria diga las dos cosas que un revisor pregunta delante de
# un TW: de que seccion salio, y si salio de un caudal documentado o de un
# escenario acotado.

@dataclass(frozen=True)
class SeccionReceptor:
    """
    Seccion transversal del cuerpo receptor, para el paso 2 de Sec. 1.3.

    TRAPECIAL, que cubre los tres casos del corredor: un dren de tierra
    (z > 0), un canal revestido rectangular (z = 0) y una cuneta triangular
    (b = 0). No se modela seccion irregular: eso es un levantamiento
    topografico del receptor, y el dia que exista el TW entra medido y esta
    seccion sobra.

    `altura_total_m` NO es el tirante: es la PROFUNDIDAD DE LA SECCION, del
    fondo a la corona del bordo. Existe para el paso 3 -- el escenario de
    "receptor a seccion llena" --, que sin ella no se puede acotar. Un
    escenario acotado por un numero que nadie declaro no es un escenario
    acotado.

    Ninguno de los cuatro numeros sale de una norma: los declara el
    proyectista en el criterio 'seccion_receptor' [A], con su trazabilidad.
    """

    b_m: float                 # m   - ancho de solera
    z_HV: float                # H:V - talud lateral, proyeccion horizontal por unidad de altura
    S: float                   # m/m - pendiente del receptor
    n: float                   # -   - Manning del receptor
    altura_total_m: float      # m   - profundidad de la seccion (fondo a corona)


# --- T-2 --- De donde salio la seccion del receptor con que se obtuvo el TW
# (vias 3 y 4 de Sec. 1.3). Son ROTULOS que la memoria imprime tal cual.
SECCION_RECEPTOR_MEDIDA = "seccion medida (levantamiento del receptor)"
SECCION_RECEPTOR_ADOPTADA = "seccion adoptada [A] por falta de levantamiento"
ORIGENES_SECCION_RECEPTOR = (SECCION_RECEPTOR_MEDIDA, SECCION_RECEPTOR_ADOPTADA)

# --- T-2 --- El aviso de un punto que declara que NO tiene previsto el acceso
# de mantenimiento (`acceso_mantenimiento_previsto = false` en
# --datos-externos). La EXIGENCIA es del Manual (num. 4.1.1.3.7 d), cita
# MC_HHD.4.1.1.3.7d); el texto de aqui es del proyecto y lo dice. Vive en
# este modulo porque lo imprimen el servicio (CLI y JSON) y la memoria (M11),
# y M11 no importa del servicio.
AVISO_SIN_ACCESO_DE_MANTENIMIENTO = (
    "Acceso de mantenimiento: el punto declara que NO esta previsto "
    "(acceso_mantenimiento_previsto = false). El Manual de Hidrologia, num. "
    "4.1.1.3.7 d) 'Mantenimiento y limpieza', exige que las dimensiones de "
    "la alcantarilla permitan el mantenimiento y la limpieza en su interior: "
    "hay que preverlo en los planos (criterio 'acceso_mantenimiento_v2b') o "
    "declarar la limitacion")



# --- T-10 --- EL ALCANCE DECLARADO DEL EXPEDIENTE: lo que el programa NO hace
# por DECISION DEL DUEÑO, dicho como alcance y no como omision (PRECISIONES
# de T-10). Una fuente y tres vistas: la CLI (`cli._lineas_alcance`), el
# JSON (`alcance.declarado`) y la memoria (`M11.bloque_alcance`). Vive aqui
# por la misma razon que el aviso de arriba: M11 no importa del servicio.
# Cada entrada nombra la ficha de `docs/decisiones_diferidas.md` donde esta
# el argumento y el simbolo del codigo donde vive lo que si se hace.
@dataclass(frozen=True)
class AlcanceDeclarado:
    clave: str
    texto: str
    ficha: str
    simbolo: str


ALCANCE_DECLARADO: Tuple[AlcanceDeclarado, ...] = (
    AlcanceDeclarado(
        clave="armado_seccion_marco",
        # --- VE-5 (m8) --- Hasta VE-5 decia que el armado de la seccion del
        # marco no se diseñaba. Desde VE-5 el portico se analiza y se arma
        # (`M8.disenar_portico`); lo que sigue fuera es lo de abajo.
        texto=("El portico del marco de concreto se analiza y se arma con UN "
               "canto, el de 'espesor_pared_cajon', en losas, paredes y "
               "tabiques, y no se itera: los cantos separados de losa y "
               "pared en la geometria del programa, el refuerzo de "
               "distribucion y las vigas de borde de la losa con menos de "
               "2.0 ft, el desarrollo y los empalmes y el agua exterior "
               "quedan para quien lo arme"),
        ficha="T5-07", simbolo="M8_estructural.disenar_portico"),
    AlcanceDeclarado(
        clave="cabezal_paralelo_a_la_via",
        # --- VE-6 --- El paralelo SIN aleros del marco ya se calcula (Carta
        # 11, ficha VE6-T7A03); lo que sigue fuera es lo que el texto dice.
        texto=("El cabezal PARALELO a la via solo se calcula en un marco y "
               "sin aleros, cuando 'embocadura_cajon' declara una fila de la "
               "Carta 11 del HDS-5; en los tubos, y con aleros (Carta 12, "
               "escala 3), el cabezal es normal al eje del conducto"),
        ficha="T7A-03", simbolo="M9_cabezal.predimensionar_aleros"),
    AlcanceDeclarado(
        clave="iteracion_ancho_zapata_cabezal",
        # --- VE-3.14 (H-10 de los ensayos de diseño del cabezal) --- Este
        # texto decia hasta VE-3.14 que el ancho «no se itera», y se itera
        # desde VE-3.5 (el peralte desde VE-3.9 y la pantalla desde
        # VE-3.14): la memoria declaraba fuera de alcance lo que hacia. Lo
        # que SIGUE fuera es lo que el texto dice ahora.
        texto=("El cabezal se dimensiona solo como zapata CORRIDA sobre la "
               "grilla de 'dimensionamiento_zapata_cabezal': el ancho por la "
               "estabilidad (VE-3.5, con la punta si el talon llega al "
               "tope), el peralte por el armado de la zapata (VE-3.9) y la "
               "pantalla por su armado (VE-3.14). Si ninguna zapata corrida "
               "cumple dentro del tope, el cabezal se declara NO FACTIBLE con "
               "estos criterios y no se proponen dentellon, llave de corte, "
               "mejoramiento del suelo ni pilotes; una dimension declarada "
               "(`cabezal_declarado`) no se itera y la estabilidad la juzga "
               "como llega; los parametros son los de prueba hasta el EMS"),
        ficha="T7B-09",
        simbolo="M9_cabezal.dimensionar_zapata_por_estabilidad"),
    AlcanceDeclarado(
        clave="aleros_como_muro",
        # --- VE-7 (ficha VE7-01, cierre de T7C-04; dictamen Fable) --- el
        # alero se verifica como muro en sus franjas, de voladizo o de
        # gravedad; lo que sigue fuera es lo que el texto dice.
        texto=("Los aleros se verifican como muro (E1 a E3, y el cuerpo "
               "ciclopeo en el de gravedad) en cinco franjas de su longitud "
               "(0, L/4, L/2, 3L/4 y L), no entre ellas; su zapata es una "
               "zapata CORRIDA de un solo ancho y un solo peralte por cabezal, "
               "y el cuerpo del alero de gravedad no se itera"),
        ficha="VE7-01", simbolo="M9_cabezal.estabilidad_del_alero"),
    # --- VE-5 (m8, item 26 del censo) --- 'flotacion_marco_sin_peso_propio'
    # SALIO: V7 pesa el concreto del marco (`M5.peso_propio_conducto_kn_m`,
    # con 'peso_especifico_concreto_kn_m3'); ficha T3-08 cerrada.
    # --- T8-08 (cerrada) --- Las Figuras 3.3 y 3.4 de HEC-14 estan
    # digitalizadas desde el cierre de la ficha; lo que queda declarado es
    # lo que las figuras no cubren. La entrada de T8-09 (la regla del maximo
    # en la banda de regimen de M4) salio con su cierre: M4 la aplica.
    AlcanceDeclarado(
        clave="tirante_de_borde_hec14",
        texto=("Donde las Figuras 3.3 y 3.4 de HEC-14 no dan el tirante de "
               "borde a la salida (una forma que no es circular ni "
               "rectangular, un caudal o un TW fuera de su familia de "
               "curvas, o una lectura que no queda bajo el tirante "
               "critico), la velocidad de salida bajo control de salida con "
               "el TW bajo el critico se toma al tirante critico: es una "
               "cota inferior y el contraste con la Tabla N 11 es un "
               "INDICADOR que no concluye"),
        ficha="T8-08", simbolo="M4_control.tirante_de_borde"),
    # --- T-11 --- El escalon de la regla de E-A en HW/D = 1.2 (medido por
    # la verificacion de T-7, no corregido), que el dueño dejo fuera
    # (PRECISIONES_T-11, punto 4 (ii)).
    AlcanceDeclarado(
        clave="escalon_regla_salida_hw_1_2_d",
        texto=("La regla de la carga de control de salida del HDS-5 num. "
               "3.3.3 (entre 0.75 D y 1.2 D compiten la aproximacion y el "
               "remanso; sobre 1.2 D rige la aproximacion) tiene un escalon "
               "donde la aproximacion cruza HW/D = 1.2: un caudal mayor "
               "puede dar unos milimetros menos de carga (11 mm medidos con "
               "el tubo de A-01 entre 1.276 y 1.290 m3/s). Es el umbral que "
               "la fuente escribe y no se suaviza; en V8 lo cubre la guardia "
               "de la carga del evento extremo"),
        ficha="T7V-01", simbolo="M4_control.resolver_control"),
)


class ViaDelTW(str, Enum):
    """
    Por cual de los cuatro caminos de Sec. 1.3 se obtuvo el TW de un punto.

    El orden es el de precedencia y no es arbitrario: va del dato mas
    determinado al escenario mas supuesto. Un TW medido no se sustituye por
    uno calculado, y uno calculado no se sustituye por un escenario.
    """

    DECLARADO = "declarado por el proyectista (--tw / TW_m)"
    COTA_TW = "columna `cota_TW` del CSV (paso 2 de Sec. 1.3, resuelto fuera)"
    MANNING_RECEPTOR = ("Manning en la seccion del receptor con su Q de "
                        "diseño (pasos 1 y 2 de Sec. 1.3)")
    ESCENARIOS_ACOTADOS = ("dos escenarios acotados, sin caudal documentado "
                           "(paso 3 de Sec. 1.3)")
    CRITERIO = "criterio 'TW_receptor' (Tablero 3.1)"


@dataclass(frozen=True)
class TWDeterminado:
    """
    El TW de un punto y de donde salio (Sec. 1.3).

    `valor` es un TIRANTE sobre el fondo de la SALIDA del conducto, en metros
    -- no una cota --, que es lo que consume el control de salida. La
    homonimia con `cota_TW` esta declarada en
    `constantes_normativas.HOMONIMIA_TW` y es exactamente la que este tipo
    existe para no volver a permitir: aqui el nombre del campo dice cual de
    las dos es, y `cota_TW_msnm` viaja aparte cuando se conoce.

    `escenarios` lleva los DOS del paso 3 cuando la via es
    `ESCENARIOS_ACOTADOS`: (TW de salida libre, TW de receptor a seccion
    llena). La hoja de ruta pide "cumplir en ambos" y el diseño corre con el
    GOBERNANTE, que es el mayor; por que eso equivale a cumplir en los dos
    esta demostrado en el docstring de `M3_hidraulica.tw_seccion_1_3`, y los
    dos numeros viajan hasta la memoria para que el revisor lo pueda
    comprobar en vez de creerlo.
    """

    valor: float                                   # m - tirante sobre el fondo de la salida
    via: "ViaDelTW"
    cota_TW_msnm: Optional[float] = None           # msnm - cuando se conoce
    escenarios: Tuple[Tuple[str, float], ...] = ()
    paso: Optional["PasoDeMemoria"] = None
    # --- T-2 --- (INF-3.2.8). CON QUE SECCION DEL RECEPTOR se obtuvo, cuando
    # la via la usa (3 y 4): la geometria, y de donde salio --MEDIDA por
    # levantamiento, o ADOPTADA por el criterio [A] 'seccion_receptor'--. Y
    # los AVISOS que la via dispara: el de la via 4 con seccion adoptada es
    # el que dice que el TW que decide el diametro es una adopcion. Viajan
    # aqui para que la CLI, el JSON y la memoria impriman el MISMO texto.
    seccion: Optional["SeccionReceptor"] = None
    origen_seccion: str = ""                       # uno de ORIGENES_SECCION_RECEPTOR, o ""
    avisos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class TiranteDeBorde:
    """
    --- T8-08 --- El tirante de BORDE a la salida (brink depth) que M4 lee de
    las Figuras 3.3 (marco) y 3.4 (tubo) de HEC-14, num. 3.1.3, bajo control
    de salida con el TW bajo el tirante critico, o por que no lo leyo.

        `figura`               "3.3", "3.4", o None si la forma no tiene
                               figura (la fuente acepta entonces el critico:
                               «not conservative, but is acceptable»).
        `caudal_adimensional`  KuQ/D^2.5 (tubo) o KuQ/(B·D^1.5) (marco), con
                               el caudal de UNA celda; None sin figura.
        `TW_sobre_D`           la abscisa de la figura.
        `y_o`                  m; None = no hay lectura, y `motivo` dice por
                               que (fuera de la familia de curvas, una curva
                               no dibujada, un borde leido que no queda bajo
                               el critico, la pendiente que no es suave u
                               horizontal con n maximo).

    Lo emite `M4.tirante_de_borde` y viaja en `ResultadoHidraulico.borde`;
    la memoria lo imprime en el paso 4.3b.
    """
    figura: Optional[str]
    caudal_adimensional: Optional[float]
    TW_sobre_D: Optional[float]
    y_o: Optional[float]
    motivo: str = ""


# ===========================================================================
# Resultados
# ===========================================================================

@dataclass(frozen=True)
class ResultadoHidraulico:
    """
    Salida de M3 + M4 para una combinacion punto / material / diametro.

    ATENCION a la regla de doble n (Sec. 4.1): `y_normal` se resuelve con
    n_max, y la velocidad viaja en DOS campos porque un umbral de velocidad
    tiene dos extremos conservadores opuestos (ver `TiranteNormal`):

        `V_erosion`        con n_min y SU tirante normal, estimacion ALTA.
                           Contra los TECHOS: V3 y el d50 de la Fase 6.
                           Cumple Q = V*A con el area de ESE tirante, no con
                           la de `y_normal` (VE-2; hasta VE-2 era la de n_min
                           sobre la geometria de n_max y V*A = 1.3*Q en el
                           concreto: ver `TiranteNormal`).
        `V_sedimentacion`  con n_max, estimacion BAJA. Contra el PISO: V2.

    NO HAY UN CAMPO `V` A SECAS, Y ES DELIBERADO. Lo habia, valia `V_erosion`
    y V2 lo consumia para verificar un piso con la estimacion alta (MAT-D1).
    Un nombre neutro deja que cada consumidor suponga que "la velocidad" es la
    suya; con dos nombres, elegir mal es visible en la linea que lo hace. Un
    modulo que obtenga la velocidad dividiendo Q entre A esta anulando la
    regla de doble n: siempre le dara `V_sedimentacion`, tambien cuando lo que
    necesita es el techo.

    HW_entrada y HW_salida son cargas sobre el fondo de la entrada, en metros.
    La conversion a cota (msnm) la hace M7 sumando la cota de entrada.

    `Q` y `S` son LOS DATOS CON QUE CORRIO EL DISENO, no los de la fila del
    CSV, y viajan aqui por el mismo motivo: ninguno de los dos sale siempre de
    su columna. Sec. 2.3 pone el caudal de la Familia B en el drenaje
    longitudinal y el de la C en el canal, y el punto cuya rasante no sigue el
    cauce declara su pendiente aparte ('S_conducto' de la CLI). Quien
    consuma este resultado -- la Fase 6, el tamizado de 7.A, la memoria --
    tiene que poder leer con QUE numeros se resolvio, sin volver a decidirlo.

    `S` entro en el tipo al cerrarse MAT-D9: la Fase 7 la re-resolvia por su
    cuenta contra `punto.S_cauce` y caia en la pendiente del cauce aunque el
    diseno hubiera corrido con otra, de modo que un mismo punto tenia dos
    pendientes -- una en el HW y otra en la cota de salida -- sin que nada lo
    dijera. No es un dato nuevo: es el mismo que M3 y M4 ya recibieron, hecho
    visible en su salida para que no se pueda elegir dos veces.

    `h_o_fuera_de_rango` / `h_o_requiere_cautela`: HDS-5 acota el uso de
    h_o = (dc + D)/2 con dos limites sobre HW/D, y los escribe condicionados a
    que el control de salida gobierne (num. 3.3.3, pag. impresa 3.24). Aqui
    llegan ya con esa condicion aplicada, de modo que True significa "este
    punto usa la aproximacion fuera del rango que su fuente declara" y no
    "podria pasarle a alguien". M11 lo imprime junto al HW del punto.

    `Q_celda_m3s` y `numero_celdas` (EXT-M-03): `Q` SIGUE SIENDO EL CAUDAL
    DEL PUNTO -- sus tres lectores (la memoria, el JSON de la CLI y la tabla
    de resumen) lo imprimen como tal, y cambiarle el significado los habria
    dejado imprimiendo un tercio del caudal como si fuera el del cruce --.
    Lo que M4 RESUELVE es `Q_celda_m3s` = Q / `numero_celdas`, el caudal de
    UN barril (regla vinculante #3 de ruta_familia_c.md §6; HDS-5 num.
    5.4.3, cita `HDS5_3ED.5.4.3#REPARTO`). Los dos llevan default para que
    los seis constructores de la suite y todo tubo circular -- una celda por
    construccion del catalogo -- sigan armandose igual: `numero_celdas = 1`
    y `Q_celda_m3s = Q`. Hasta EXT-2 el tipo no distinguia los dos caudales
    y M4 recibia el total con un tirante normal resuelto para Q/N: la
    memoria imprimia Q = 9.0 junto a un y_n que solo transporta 3.0.

    EL REGIMEN DEL BARRIL, Y POR QUE ESTA AQUI (EXT-3; EXT-M-01, PC-04,
    v8 §1.3 y §4.1 enmendadas en EXT-0). El parrafo de arriba sobre la doble
    n sigue valiendo para el flujo UNIFORME, y el flujo uniforme no es el
    unico regimen del barril: con TW >= D el barril fluye LLENO y el tirante
    y la velocidad con que V1 y V2 se comparan son D y Q_celda/A_llena, no
    los de Manning. Hasta EXT-3 la memoria imprimia «manda TW: la salida esta
    ahogada» junto a V1 [OK] con y/D = 0.135, cuando a seccion llena el borde
    libre no existe y la velocidad es 0.0786 m/s < 0.25.

        `regimen_barril`   LLENO si TW >= D; PARCIALMENTE_LLENO en otro caso.
        `V_llena_m_s`      Q_celda / A_llena: la velocidad del regimen LLENO.
                           No lleva n --a seccion llena no hay tirante que
                           resolver-- y por eso no rompe la regla de doble n:
                           es la UNICA velocidad del barril en ese regimen,
                           y V2 la compara tal cual.
        `V_salida`         la velocidad a la SALIDA por HDS-5 3.1.6 (pag.
                           impresa 3.18), como `Magnitud` con procedencia,
                           que es la que recibe M6 (PC-04). Bajo control de
                           SALIDA es Q_celda entre el area de la seccion al
                           tirante min(D, max(TW, y_c)) --tirante critico,
                           TW o seccion entera, segun el TW--: no depende de
                           n. Desde el cierre de T8-08 y T8-09, con el TW
                           bajo el critico el area es la del tirante de
                           BORDE de HEC-14 (Figuras 3.3 y 3.4) y la
                           velocidad la mayor de esa y `V_erosion` (ver
                           `borde`). Bajo control de ENTRADA es la del tirante
                           normal (pag. 3.24: «The velocity at normal depth
                           is assumed to be the outlet velocity»), y de sus
                           dos ramas la de n_min (`V_erosion`, con su propio
                           tirante desde VE-2): el techo conservador para un
                           d50 que crece con V^2. En pendiente suave con
                           salida libre la de salida a y_c SUPERA a la
                           normal (1.508 vs 1.184 m/s en el caso del
                           dictamen, medida con la formula anterior a VE-2;
                           hoy la normal es aun menor): M6 recibia una piedra
                           chica.
        `y_salida_m`       el TIRANTE a la salida. Bajo control de SALIDA y
                           con el barril horizontal, min(D, max(TW, y_c)):
                           el mismo con que se midio `V_salida` salvo con el
                           TW bajo el critico, donde la velocidad se mide al
                           borde (`borde`, T8-08) y este sigue siendo el
                           critico, el de registro del barril. Bajo
                           control de ENTRADA, el tirante normal de REGISTRO,
                           el de n_max (`y_normal`): la regla de doble n da
                           el tirante con n MAXIMO y la velocidad con n
                           MINIMO, y desde VE-2 esa velocidad se mide con su
                           propio tirante, mas bajo, que el paso 4.3b imprime
                           al lado (`y_n_min`). Lo leen como TIRANTE el
                           rotulo del regimen del Froude y la Ec. (10.5) de
                           HEC-14 (M6) y el nivel de agua contra el cabezal
                           de salida (M9); ver la ficha VE2-B.
        `h_o_m`, `TW_m`, `ahogado_por_TW`   el bloque h_o entero, que hasta
                           EXT-3 no salia del `ControlSalida` (SIS-B-18): el
                           JSON y `cli.volcar` lo imprimen junto a las dos
                           banderas y a `HW_sobre_D_salida`.

    Bajo control de SALIDA con el barril PARCIALMENTE LLENO el tirante y la
    velocidad «del barril» salen DESDE E-A del perfil de la lamina de agua
    (HDS-5 Section 3.5; `perfil`, un `PerfilLamina`): V1 compara
    `perfil.y_max_m` y V2 `perfil.V_min_m_s`. Hasta E-A no existia y V1/V2 lo
    decian con `MetodoNoEvaluableError`; hoy esa excepcion queda como el
    fallback de un resultado armado SIN perfil (`perfil is None`), que M4 no
    produce nunca.

    `perfil` (E-A) es UN campo y no diez, a proposito: el perfil se lee
    entero, con su tipo, su procedencia y sus dos salidas (la fraccion de
    longitud a seccion llena y el HW por remanso). Con el, `HW_salida` es el
    HW EFECTIVO del control de salida --el remanso donde sustituye a la
    aproximacion (HW_aprox/D < 0.75, pag. 3.24 y 3.12 del HDS-5) y la
    aproximacion en el resto-- y `HW_sobre_D_salida` es ese mismo efectivo
    entre D; `h_o_fuera_de_rango` significa lo que su docstring dice --«este
    punto USA la aproximacion fuera del rango que su fuente declara»-- y con
    perfil no puede ser True: donde la aproximacion esta fuera de rango, no
    se usa. Solo un resultado sin perfil puede llevarla en True, y es lo que
    la compuerta `servicio._compuerta_metodo_h_o` sigue guardando.
    """

    # --- T-2 --- LOS TRES DE MANNING SON `None` EN UN BARRIL HORIZONTAL
    # (S = 0, INF-5.1.6): no hay tirante normal ni velocidad uniforme, y un
    # numero puesto ahi seria inventado. `sin_tirante_normal` lo dice en una
    # palabra; V1 y V2 leen entonces el perfil de la lamina, V3 y la Fase 6
    # la velocidad de la seccion de salida (`V_salida`), y los lectores que
    # imprimen (CLI, JSON, memoria, ventana) escriben «no existe (S = 0)».
    y_normal: Optional[float]             # m  - con n_max (Sec. 4.1)
    y_critico: float                      # m  - Q^2*T/(g*A^3) = 1 (Sec. 4.2)
    V_erosion: Optional[float]            # m/s - con n_min (Sec. 4.1)
    V_sedimentacion: Optional[float]      # m/s - con n_max (Sec. 4.1)
    Q: float                              # m3/s - caudal de diseno del punto
    S: float                              # m/m - pendiente con que corrio el
                                          # diseno (la del cauce salvo que el
                                          # punto declare la suya): la MISMA
                                          # que usa 7.B (MAT-D9)
    HW_entrada: float                     # m  - control de entrada (Sec. 4.2)
    HW_salida: float                      # m  - control de salida (Sec. 4.3)
    control_gobernante: ControlGobernante
    # PF-1 (PC-03): el piso que `control_entrada` adopto en lugar de la
    # ecuacion, o None. Viaja aqui para que el JSON por punto y el comparador
    # lo vean; la memoria lo imprime desde el paso F4.CONTROL.
    piso_hw_entrada: Optional["PisoDeCargaEntrada"] = None
    # Las dos condiciones de uso de h_o que el proyecto evalua, ya filtradas
    # por si el control de salida gobierna (NOR-HDS-05). Ver `ControlSalida`.
    h_o_fuera_de_rango: bool = False
    h_o_requiere_cautela: bool = False
    # EL HW/D DEL CONTROL DE SALIDA, que es el que las dos banderas de arriba
    # acotan. Viaja como dato y no lo recompone el reporte: M11 imprimia
    # `hidraulica.HW / resultado.D` en el aviso de h_o, que es la segunda
    # mitad de SIS-A-07 --- la misma aritmetica sobre magnitudes, en el mismo
    # modulo, sobrevivida al test que la persigue porque su guardia excluia
    # `ast.Attribute` a la izquierda, y `hidraulica.HW` es un Attribute.
    # Aqui llega ya calculado por M4 (`ControlSalida.HW_sobre_D`), que es
    # quien tiene delante la seccion con que se dividio.
    HW_sobre_D_salida: float = 0.0
    # LA TRAZA HIDRAULICA (§4.4). Los pasos que M3 y M4 emitieron al resolver
    # esta combinacion, en el orden en que se calcularon: Manning, tirante
    # critico, control de entrada, control de salida y adopcion del
    # gobernante. M11 los formatea; no los reconstruye.
    pasos: Tuple["PasoDeMemoria", ...] = ()
    # EL CAUDAL CON QUE M3 Y M4 RESOLVIERON DE VERDAD, y cuantos barriles
    # lo reciben (EXT-M-03). Ver el docstring. `None` en el constructor
    # significa «no hay reparto»: se rellena con `Q` en `__post_init__`.
    Q_celda_m3s: Optional[float] = None   # m3/s - Q / numero_celdas
    numero_celdas: int = 1                # barriles hidraulicamente iguales
    # EL REGIMEN DEL BARRIL Y LO QUE DE EL DEPENDE (EXT-3; EXT-M-01, PC-04).
    # Ver el docstring. Todos con default para que los constructores de la
    # suite que no pasan por M4 sigan armandose; M4 los llena SIEMPRE, y
    # `servicio._fase_6` trata un `V_salida` vacio como fallo de programa.
    regimen_barril: RegimenBarril = RegimenBarril.PARCIALMENTE_LLENO
    V_llena_m_s: Optional[float] = None   # m/s - Q_celda / A_llena (regimen LLENO)
    V_salida: Optional["Magnitud"] = None # m/s - HDS-5 3.1.6, con procedencia
    y_salida_m: Optional[float] = None    # m  - tirante a la salida (ver arriba: bajo control de entrada, el de registro)
    h_o_m: Optional[float] = None         # m  - max(TW, (y_c + D)/2), Sec. 4.3
    TW_m: Optional[float] = None          # m  - tirante en el receptor
    ahogado_por_TW: bool = False          # manda TW en h_o, no la geometria
    # EL PERFIL DE LA LAMINA (E-A): un solo campo, ver el docstring. M4 lo
    # llena SIEMPRE; `None` solo en los constructores de la suite que no
    # pasan por M4, y ahi V1/V2 vuelven al fallback de EXT-3.
    perfil: Optional["PerfilLamina"] = None
    # --- T-8 --- LA VELOCIDAD CRITICA, Q_celda / A_c, que M4 ya resolvio en
    # el paso 4.2 y no salia del `TiranteCritico`. La lee la Fase 6 para la
    # proteccion de la ENTRADA: bajo control de entrada el flujo pasa por el
    # tirante critico justo aguas abajo de la boca (HDS-5 num. 3.1.3). `None`
    # solo en los constructores de la suite que no pasan por M4.
    V_critica_m_s: Optional[float] = None
    # --- VE-3.11 (H2) --- EL RESALTO DENTRO DEL BARRIL BAJO CONTROL DE
    # ENTRADA (HDS-5 3.1.3, pag. impresa 3.2). `y_conjugado_m` es el
    # conjugado del tirante normal supercritico (`M3.tirante_conjugado_barril`;
    # None si no aplica o no cabe en la seccion) y `resalto_en_el_barril`
    # dice si el TW lo alcanza. `receptor_en_el_barril` es lo que V1 lee: el
    # receptor fija el tirante maximo DENTRO del barril bajo control de
    # entrada --el resalto entra (barril supercritico) o el remanso M1 llega
    # a la salida (barril subcritico, TW > y_n)--. Los tres los llena M4.
    y_conjugado_m: Optional[float] = None
    resalto_en_el_barril: bool = False
    receptor_en_el_barril: bool = False
    # --- VE-5 (item 17, EA-02) --- EL RESALTO SITUADO POR MOMENTUM (HEC-14
    # num. 6.2, Ec. 6.1): donde la S1 que sube desde el receptor iguala el
    # conjugado de la S2 que baja desde la entrada. Lo llena M4 cuando el
    # resalto queda DENTRO del barril bajo control de entrada; V2 imprime su
    # velocidad tras el resalto (paso 3 de los ejemplos de HEC-14). None si
    # no hay resalto en el barril o si la S1 alcanza la cara de entrada (el
    # resalto se ahoga en la boca y todo el barril es subcritico).
    resalto: Optional[ResaltoHidraulico] = None
    # --- T8-08 / T8-09 --- LA VELOCIDAD DE SALIDA BAJO CONTROL DE SALIDA
    # CON EL TW BAJO EL CRITICO (primera viñeta de HDS-5 3.1.6). Desde el
    # cierre de T8-08 no se mide al tirante critico sino al de BORDE de las
    # Figuras 3.3 y 3.4 de HEC-14 (num. 3.1.3: «The flow goes through
    # critical depth upstream of the outlet»), y desde el de T8-09 es la
    # MAYOR de esa y `V_erosion` cuando con n minimo el tirante normal es
    # supercritico. `borde` es la lectura (o por que no la hubo), None fuera
    # de esa viñeta. `V_salida_cota_inferior` es True SOLO donde la figura
    # no dio lectura y la velocidad se quedo en la critica, que la fuente
    # dice mayor que el borde: es lo que la Fase 6 lee para no concluir el
    # contraste con la Tabla Nº 11. `y_salida_m` no cambia: sigue siendo el
    # critico, el tirante de REGISTRO del barril (subcritico) que el Froude,
    # la Ec. (10.5) de HEC-14 y el nivel del cabezal leen.
    borde: Optional[TiranteDeBorde] = None
    V_salida_cota_inferior: bool = False

    def __post_init__(self) -> None:
        if self.Q_celda_m3s is None:
            object.__setattr__(self, "Q_celda_m3s", self.Q)

    @property
    def sin_tirante_normal(self) -> bool:
        """
        --- T-2 --- True si el barril es horizontal (S = 0) y por tanto no
        hay flujo uniforme: `y_normal`, `V_erosion` y `V_sedimentacion` son
        `None` (HDS-5 num. 3.3.4; `SinTiranteNormal`). Es el predicado UNICO
        con que M5, la Fase 6 y los lectores eligen de donde sale el tirante
        y la velocidad del barril.
        """
        return self.y_normal is None

    @property
    def HW(self) -> float:
        """
        Carga a la entrada del control que gobierna. Es un selector sobre lo
        que M4 ya decidio, no una decision nueva.
        """
        if self.control_gobernante == ControlGobernante.ENTRADA:
            return self.HW_entrada
        return self.HW_salida

    @property
    def salida_no_se_forma(self) -> bool:
        """
        --- T-12 (ficha T11-09) --- True cuando el perfil de la lamina
        descarto la aproximacion del control de salida y su remanso no
        alcanza la entrada (`PerfilLamina.salida_no_se_forma`): entonces
        `HW_salida` es la aproximacion DESCARTADA, no una carga de salida, y
        ningun lector la publica como tal. False sin perfil.
        """
        return self.perfil is not None and self.perfil.salida_no_se_forma


@dataclass(frozen=True)
class ProteccionSalida:
    """
    Salida de M6 (Fase 6): d50 de Laushey y las dos piezas complementarias que
    la hoja de ruta deja como criterio adoptado (espesor y longitud).

    `d50` es la unica magnitud con formula normativa (num. 4.1.1.3.7 c). NO es
    un diseño de enrocado: la hoja de ruta (Sec. 6) dice expresamente que
    faltan la granulometria completa y el filtro, y que sin filtro el
    enrocado se socava por debajo y falla. `advertencias` transporta ese
    aviso para que ningun consumidor de este resultado lo omita.
    """

    # LOS TRES LLEVAN SIEMPRE NUMERO. T-8 los dejaba en `None` cuando la
    # velocidad de salida no superaba la admisible de la Tabla Nº 11 («sin
    # enrocado»); el dueño resolvio el 2026-11-12 que esa NUNCA es una
    # conclusion del programa: la proteccion se calcula y se mantiene
    # siempre, y la tabla informa (`requerida`). Siguen tipados `Optional`
    # porque los constructores y los lectores anteriores lo esperan.
    #
    # `d50` ES EL QUE RIGE, y desde esa misma decision no es siempre el de
    # Laushey: con la regla 'regla_espesor_longitud_proteccion_salida' en
    # «envolvente_hec14» (el archivo) es el MAYOR de Laushey y de la Ec.
    # (10.4) de HEC-14 cuando esta es evaluable; con «manual», el de Laushey.
    # El de Laushey se publica siempre aparte, en `d50_laushey`.
    d50: Optional[float]                  # m - el que rige (ver arriba)
    espesor: Optional[float]              # m - el que rige, segun la regla
    longitud: Optional[float]             # m - la que rige, segun la regla
    V: float                              # m/s - la velocidad de SALIDA de
                                          # HDS-5 3.1.6 con que se calculo
                                          # (`ResultadoHidraulico.V_salida`):
                                          # `V_erosion`, la rama de n minimo,
                                          # bajo control de entrada, y Q
                                          # entre el area al tirante de
                                          # salida bajo control de salida o
                                          # con el barril horizontal (EXT-3)
    criterio_espesor: str                 # clave en criterios_adoptados.py
    criterio_longitud: str                # clave en criterios_adoptados.py
    advertencias: Tuple[str, ...]
    numeral: str = "4.1.1.3.7 c)"
    paso: Optional["PasoDeMemoria"] = None
    # --- T-8 --- Lo que la Fase 6 añade AL LADO de Laushey. Todos con
    # default, para que los constructores anteriores sigan armandose.
    #   `requerida`   lo que INFORMA el contraste con la Tabla Nº 11: True
    #                 si la velocidad de salida supera la admisible del
    #                 terreno; False si no la supera (el terreno la
    #                 resistiria segun la tabla: la proteccion se mantiene
    #                 igual, y suprimirla queda sujeto a inspeccion de campo);
    #                 None si el punto no declaro el terreno o si el
    #                 contraste NO CONCLUYE porque la velocidad comparada es
    #                 una cota inferior (`velocidad_admisible.concluyente`).
    #   `pasos`       TODOS los pasos de la proteccion de salida, en su orden
    #                 de lectura; `paso` sigue siendo el de Laushey.
    #   `avisos`      lo que la corrida dice en voz alta: suben a
    #                 `InformePunto.avisos()` (CLI, JSON y memoria).
    requerida: Optional[bool] = None
    froude: Optional["FroudeSalida"] = None
    velocidad_admisible: Optional["VelocidadAdmisible"] = None
    apron: Optional["ApronHEC14"] = None
    filtro: Optional["RequisitoDeFiltro"] = None
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    # --- T-8, auditoria --- La clase de la Tabla 10.1 de HEC-14 que toca a
    # la piedra que el proyecto PONE (el d50 de Laushey), y la regla con que
    # se fijaron espesor y longitud: con «manual» (el archivo) son los
    # adoptados; con «envolvente_hec14», el mayor de lo adoptado y HEC-14.
    # `espesor_adoptado` y `longitud_adoptada` son siempre los del criterio,
    # antes de la regla.
    clase_de_la_piedra: Optional["ClaseHEC14"] = None
    regla_espesor_longitud: Optional[str] = None
    espesor_adoptado: Optional[float] = None
    longitud_adoptada: Optional[float] = None
    # --- T-8, segunda auditoria --- El d50 de LAUSHEY (Manual, num.
    # 4.1.1.3.7 c)), que se calcula y se imprime siempre, rija o no: con
    # «manual» es igual a `d50`; con la envolvente puede quedar por debajo.
    # `rige_la_envolvente` dice si la regla llego a formarla (False con
    # «manual» y cuando HEC-14 no es evaluable en el punto).
    d50_laushey: Optional[float] = None
    rige_la_envolvente: bool = False
    # --- VE-4g --- La poza de enrocado de HEC-14 Sec. 10.1, donde el apron
    # no llega (marco, conducto de mas de 60 in). None si el apron se evaluo
    # o si la poza tampoco es evaluable (varios barriles, Froude de 3 o mas).
    poza: Optional["PozaDeEnrocado"] = None
    # --- VE-5 (lote m6) --- Con el TW sobre 1.0·D de un tubo de hasta 60
    # in: la Figura 10.3 y la Ec. (10.6). None en otro caso.
    tw_alto: Optional["ProteccionTWAlto"] = None


# ---------------------------------------------------------------------------
# --- T-8 --- Proteccion de entrada y salida: las piezas nuevas de la Fase 6
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FroudeSalida:
    """
    Numero de Froude a la salida, con el tirante equivalente de HEC-14 (num.
    10.1.1): ye = yo en un marco, ye = (A/2)^0.5 en un tubo. `A` es el area
    que la continuidad asigna a la velocidad de salida, Q_celda / V.
    """

    Fr: float                             # Fr_e, con ye: parametro de HEC-14
    V: float                              # m/s - la V_salida de HDS-5 3.1.6
    A: float                              # m2  - Q_celda / V
    y_equivalente: float                  # m   - ye
    # El REGIMEN, del tirante de salida contra el critico
    # (`M6.flujo_supercritico`, la misma regla que el apron usa para la
    # Ec. 10.5); None si falta uno de los dos. NO es Fr_e > 1: el ye de
    # HEC-14 no clasifica el regimen (auditoria de T-8, hallazgo 2).
    supercritico: Optional[bool]
    seccion_llena: bool                   # la salida va a seccion llena
    paso: Optional["PasoDeMemoria"] = None


@dataclass(frozen=True)
class VelocidadAdmisible:
    """
    La velocidad del flujo contra la maxima admisible del terreno (Tabla
    Nº 11 del Manual). `supera` True es lo que dispara la proteccion.
    """

    donde: str                            # "salida" o "entrada"
    tipo_terreno: str                     # clave de fila de la Tabla Nº 11
    regimen_flujo: str                    # "intermitente" o "permanente"
    V: float                              # m/s
    V_admisible: float                    # m/s
    supera: bool
    paso: Optional["PasoDeMemoria"] = None
    # --- T-8, segunda auditoria (H2) --- False cuando la velocidad NO
    # supera la admisible pero es una COTA INFERIOR de la real (control de
    # salida con el TW bajo el critico: el tirante de borde es menor, HEC-14
    # num. 3.1.3): de esa comparacion no se concluye que el terreno resista.
    concluyente: bool = True


@dataclass(frozen=True)
class ApronHEC14:
    """
    Apron de enrocado de HEC-14 Sec. 10.2: el D50 de la Ec. (10.4) y, de la
    Tabla 10.1 (un EJEMPLO de estandar de proyecto), la clase, la longitud,
    la profundidad y el ancho. Los cuatro ultimos son `None` cuando el D50
    requerido supera la mayor clase de la tabla.
    """

    D50_requerido: float                  # m - Ec. (10.4)
    D: float                              # m - diametro del conducto
    D_de_calculo: float                   # m - D, o D' = (D + yn)/2 (Ec. 10.5)
    ajustado_por_supercritico: bool
    TW: float                             # m - el del punto
    TW_de_calculo: float                  # m - acotado a 0.4·D por abajo
    TW_acotado: bool
    clase: Optional[int] = None
    D50_clase: Optional[float] = None     # m
    longitud: Optional[float] = None      # m
    espesor: Optional[float] = None       # m
    ancho_final: Optional[float] = None   # m
    pasos: Tuple["PasoDeMemoria", ...] = ()
    # --- T-8, segunda auditoria (H15) --- False si no se pudo decidir el
    # regimen (falta el tirante de salida): la Ec. (10.5) no se aplico, y si
    # el flujo fuera supercritico el D50 seria mayor. Se avisa.
    regimen_determinado: bool = True


@dataclass(frozen=True)
class ClaseHEC14:
    """
    La clase de la Tabla 10.1 de HEC-14 que corresponde a una piedra dada
    (la de D50 mayor o igual) y la geometria que la tabla le da: longitud
    kL·D, profundidad ke·D50 de la clase, ancho final 3·D + (2/3)·L. Sin
    clase (piedra mayor que la ultima) los cuatro ultimos van en None.
    """

    d50_de_partida: float                 # m
    clase: Optional[int] = None
    D50_clase: Optional[float] = None     # m
    longitud: Optional[float] = None      # m
    espesor: Optional[float] = None       # m
    ancho_final: Optional[float] = None   # m
    paso: Optional["PasoDeMemoria"] = None


@dataclass(frozen=True)
class PozaDeEnrocado:
    """
    --- VE-4g --- La poza de enrocado (riprap basin) de HEC-14 Sec. 10.1:
    la hoya PRE-FORMADA y revestida que la Tabla 1.1 da donde el apron de la
    Sec. 10.2 no llega (marco, conducto de mas de 60 in). La dimensiona el
    procedimiento del num. 10.1.5 (`M6.poza_de_enrocado_hec14`).

    DOS PIEDRAS, y no se confunden: `D50_dimensionamiento` es con la que se
    resuelve la Ec. (10.1) y `D50_piedra` la que REVISTE la poza. Son la
    misma salvo que la piedra disponible de hs/D50 < 2: entonces la poza se
    dimensiona con la piedra de hs/D50 = 2 exacto y se reviste con la mayor
    («A basin sized for smaller riprap may be lined with larger riprap»,
    `dimensionada_con_menor`). Bajo D50/ye = 0.1, el limite de los ensayos,
    la piedra se sube a 0.1·ye (`piedra_subida`).
    """

    y_equivalente: float                  # m - ye (num. 10.1.1)
    Fr: float                             # Vo/(g·ye)^0.5
    TW: float                             # m
    Co: float                             # Ec. (10.2) o (10.3)
    relacion_co: str                      # 'envolvente' o 'mejor_ajuste'
    D50_minimo: float                     # m - 0.1·ye
    D50_piedra: float                     # m - la que reviste
    D50_dimensionamiento: float           # m - con la que se resuelve hs
    dimensionada_con_menor: bool
    piedra_subida: bool
    hs: float                             # m - profundidad de la poza
    Wo: float                             # m - ancho del conducto en la boca
    longitud_poza: float                  # m - Ls
    longitud_apron: float                 # m - LA = LB - Ls
    longitud_total: float                 # m - LB (extendida si hizo falta)
    longitud_sin_extender: float          # m - LB del paso 3
    ancho_final: float                    # m - WB = Wo + (2/3)·LB
    espesor: float                        # m - 2·D50 en piso y lados
    espesor_talud: float                  # m - 3·D50 en el talud de salida
    yc_salida: float                      # m - tirante critico en la salida
    V_salida_poza: float                  # m/s - Vc en la salida
    V_admisible: Optional[float] = None   # m/s - Vallow; None sin el dato
    extendida: bool = False               # el apron se alargo hasta Vallow
    # Paso 5: TW/yo > 0.75 pide proteccion aguas abajo (Figura 10.3); None
    # si falta el tirante de borde yo.
    proteccion_adicional: Optional[bool] = None
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    # --- VE-5 (lote m6) --- Con `proteccion_adicional` y la admisible, la
    # Figura 10.3: hasta donde llega la proteccion (m desde la boca) y la
    # piedra en la salida de la poza (Ec. 10.6). None si no aplica.
    proteccion_adicional_hasta: Optional[float] = None
    D50_proteccion_adicional: Optional[float] = None


@dataclass(frozen=True)
class ProteccionTWAlto:
    """
    --- VE-5 (lote m6) --- La proteccion de salida con el tirante del
    receptor sobre 1.0·D, donde la Ec. (10.4) no vale: la Sec. 10.2 de
    HEC-14 manda a la Figura 10.3 (atenuacion de la velocidad en el eje) y
    a la Ec. (10.6) de la Sec. 10.3 para la piedra. La dimensiona
    `M6.proteccion_tw_alto_hec14`.
    """

    De: float                             # m - diametro equivalente de borde
    Vo: float                             # m/s - velocidad de salida
    V_admisible: float                    # m/s
    D50: float                            # m - Ec. (10.6) con Vo, en la boca
    longitud: float                       # m - hasta VL = Vallow
    # m - max(2·D50 de HEC-14, lectura del proyecto; 0.30 m de HEC-11 Sec.
    # 4.3, [C] aplicado por analogia desde N3)
    espesor: float
    pasos: Tuple["PasoDeMemoria", ...] = ()
    # --- N3 --- el +50 % bajo agua de HEC-11 Sec. 4.3, que no se aplica.
    avisos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class EstructuraDeCaida:
    """
    --- VE-5 (lote m6) --- La estructura de caida recta de HEC-14 num.
    11.1.3 (estanque de bloques y umbral del St. Anthony Falls) para la
    salida que queda colgada sobre el lecho: cuando gobierna la pendiente
    maxima del conducto o cuando la caida supera la Tabla 5.2. La dimensiona
    `M6.caida_recta_hec14`.

    LAS COTAS VERTICALES SE MIDEN DESDE LA CRESTA y son NEGATIVAS hacia
    abajo, como las escribe la fuente: `h2` es el nivel del receptor y `ho`
    el piso del estanque. `depresion_piso` = -ho - h: cuanto baja el piso
    bajo el lecho del receptor (negativo si queda por encima).
    """

    Q: float                              # m3/s
    ancho_vertedero: float                # m - Wo
    q: float                              # m2/s - Q/Wo
    yc: float                             # m - Ec. (11.5)
    desnivel_h: float                     # m - cresta sobre el lecho
    tirante_aguas_abajo: float            # m - yo del receptor
    y3: float                             # m - Ec. (11.7)
    h2: float                             # m - Ec. (11.8), negativo
    ho: float                             # m - Ec. (11.9), negativo
    depresion_piso: float                 # m
    Lf: float                             # m - Ec. (11.12)
    Lt: float                             # m - Ec. (11.14)
    Ls: float                             # m - Ec. (11.13)
    L1: float                             # m - Ec. (11.11)
    L2: float                             # m - Ec. (11.15)
    L3: float                             # m - Ec. (11.16), el minimo
    longitud: float                       # m - LB, Ec. (11.10)
    altura_bloques: float                 # m
    ancho_bloques: float                  # m - ancho y separacion
    altura_umbral: float                  # m
    muro_sobre_tw: float                  # m
    longitud_aproximacion: float          # m - revestida aguas arriba
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class RelacionesDeFiltro:
    """
    --- N3 --- Las tres relaciones de la Ec. (14) de HEC-11 (Sec. 4.4.1) en
    UNA interfaz entre una capa gruesa y una fina:

        tubificacion   = D15 grueso / D85 fino   <= 5   («5 or less»)
        permeabilidad  = D15 grueso / D15 fino   >  5
        uniformidad    = D15 grueso / D15 fino   <  40

    Con una sola curva del grueso, permeabilidad y uniformidad son el mismo
    cociente. Con una BANDA del grueso (la Tabla 2 de HEC-11 alrededor del
    D50) cada una se forma con el extremo que la exige mas: tubificacion y
    uniformidad con el D15 grueso, permeabilidad con el fino
    (`Interpretacion` de la cita HEC11.4.2#T2).
    """

    D15_grueso_min: float                 # m
    D15_grueso_max: float                 # m
    D85_fino: float                       # m
    D15_fino: float                       # m
    tubificacion: float                   # -
    permeabilidad: float                  # -
    uniformidad: float                    # -
    cumple_tubificacion: bool
    cumple_permeabilidad: bool
    cumple_uniformidad: bool

    @property
    def cumple(self) -> bool:
        return (self.cumple_tubificacion and self.cumple_permeabilidad
                and self.cumple_uniformidad)


@dataclass(frozen=True)
class FiltroGranularHEC11:
    """
    --- N3 --- El filtro GRANULAR bajo el enrocado por HEC-11 Sec. 4.4.1,
    como REQUISITO de especificacion y no como un material elegido: la
    ventana de tamaños que tiene que cumplir una manta de UNA capa entre el
    suelo del lecho y la piedra, el pasante maximo del tamiz N.º 200 y el
    intervalo de espesor.

    Sin la granulometria del suelo (D85 y D15, dato del EMS) o sin la piedra
    los numeros quedan en `None` y `texto` dice que falta: no se supone un
    suelo. `una_capa_basta` es False cuando la ventana queda vacia --HEC-11
    pide entonces mas capas, que el programa no diseña--, y None sin datos o
    con un lecho COHESIVO, donde la Ec. (14) queda fuera del marco de la
    fuente y la ventana no se declara (los pasos salen como informacion).
    """

    D85_suelo: Optional[float]            # m - dato del EMS
    D15_suelo: Optional[float]            # m - dato del EMS
    d50_enrocado: Optional[float]         # m - la piedra que rige
    D15_enrocado_min: Optional[float]     # m - Tabla 2: 0.4·D50
    D15_enrocado_max: Optional[float]     # m - Tabla 2: 0.6·D50
    directo_sobre_el_suelo: Optional[RelacionesDeFiltro]
    D15_filtro_mayor_que: Optional[float]   # m - limite inferior, estricto
    D15_filtro_hasta: Optional[float]       # m - limite superior
    D85_filtro_desde: Optional[float]       # m - limite inferior, admitido
    una_capa_basta: Optional[bool]
    pasa_200_max_pct: float               # % del material del filtro
    espesor_una_capa_m: Tuple[float, float]
    espesor_varias_capas_m: Tuple[float, float]
    texto: str
    citas: Tuple[str, ...] = ()
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class RequisitoDeFiltro:
    """
    El filtro bajo el enrocado, como REQUISITO DECLARADO y no como diseño.
    Con el pasante del tamiz N.º 200 del suelo (dato del EMS) elige la
    columna de la Tabla 511-06 de EG-2013; sin el, los tres campos de la
    columna quedan en `None` y `texto` dice que dato falta.

    Desde N3 declara tambien la alternativa GRANULAR (`granular`, HEC-11
    Sec. 4.4.1), que la llamada desde la Fase 6 trae siempre; y, con una
    piedra de D50 mayor que 0.91 m, la cama de grava que HEC-11 Sec. 4.4.2
    pide bajo el enrocado cuando el filtro es geotextil
    (`cama_de_grava_bajo_geotextil`).
    """

    clase_geotextil: str
    pasa_200_pct: Optional[float]
    columna: Optional[str]                # rotulo de la columna de la tabla
    permitividad_min_s1: Optional[float]
    abertura_aparente_max_mm: Optional[float]
    texto: str
    citas: Tuple[str, ...] = ()
    paso: Optional["PasoDeMemoria"] = None
    avisos: Tuple[str, ...] = ()          # nota (5) a: suelo que pide diseño
    granular: Optional[FiltroGranularHEC11] = None
    cama_de_grava_bajo_geotextil: Optional[bool] = None


@dataclass(frozen=True)
class ProteccionEntrada:
    """
    Proteccion de la ENTRADA (INF-5.1.13): la velocidad en la boca, el
    revestimiento adoptado y lo que hay que proteger segun la embocadura.
    Ninguna fuente de normas/ da dimensiones para la entrada: la geometria
    del zampeado y del dentellon es del cabezal (T-7a).
    """

    tipo_embocadura: str
    V_entrada: Optional[float]            # m/s; None si M4 no la publica
    revestimiento: str                    # valor de 'tipo_proteccion_entrada'
    criterio_revestimiento: str
    elementos: Tuple[str, ...]            # lo que se protege, por embocadura
    requerida: Optional[bool] = None      # como en `ProteccionSalida`
    velocidad_admisible: Optional["VelocidadAdmisible"] = None
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()


TIPO_LECHO_NO_COHESIVO = "no_cohesivo"
TIPO_LECHO_COHESIVO = "cohesivo"
TIPOS_DE_LECHO = (TIPO_LECHO_NO_COHESIVO, TIPO_LECHO_COHESIVO)


@dataclass(frozen=True)
class MaterialLecho:
    """
    El dato externo `material_lecho_salida`, ya validado: el suelo del lecho
    a la salida, del EMS. Todos los campos son opcionales por separado
    --cada calculo dice cual le falta-- y ninguno tiene valor por defecto.

        tipo            "no_cohesivo" o "cohesivo": que ecuacion de HEC-14.
        D84_m, D16_m    granulometria del lecho (no cohesivo): σ = (D84/D16)^0.5.
        IP              indice de plasticidad (cohesivo).
        Sv_Pa           resistencia al corte saturada, N/m2 (cohesivo).
        pasa_200_pct    pasante del tamiz N.º 200, en %: elige la columna del
                        geotextil de filtro (EG-2013, Tabla 511-06).
        D85_m, D15_m    --- N3 --- granulometria del lecho para el FILTRO
                        GRANULAR (HEC-11 Ec. 14): van juntos, y no son D84 y
                        D16, que son los de la hoya (HEC-14 Ec. 5.1).
    """

    tipo: Optional[str] = None
    D84_m: Optional[float] = None
    D16_m: Optional[float] = None
    IP: Optional[float] = None
    Sv_Pa: Optional[float] = None
    pasa_200_pct: Optional[float] = None
    D85_m: Optional[float] = None
    D15_m: Optional[float] = None


@dataclass(frozen=True)
class HoyaDeSocavacion:
    """La hoya de socavacion local estimada por HEC-14 Cap. 5."""

    metodo: str                           # que ecuacion, con su numeral
    profundidad: float                    # m - hs
    ancho: float                          # m - Ws
    longitud: float                       # m - Ls
    distancia_al_maximo: float            # m - 0.4·Ls desde la salida
    duracion_min: float                   # minutos
    origen_duracion: str
    Cs: float                             # el de la profundidad
    Ch: float                             # el de la profundidad
    pasos: Tuple["PasoDeMemoria", ...] = ()
    # --- T-8, auditoria --- De donde salio t: `duracion_por_criterio` si
    # rigio el criterio 'duracion_caudal_pico_socavacion_min' por falta del
    # dato; `duracion_acotada` si el dato era menor de 30 min y se estimo con
    # 30 como cota superior. Con el criterio, la SENSIBILIDAD: la profundidad
    # que daria el otro extremo de su ventana (`duracion_alternativa_min`:
    # los 30 minutos que la fuente recomienda cuando rige el techo, 360).
    duracion_por_criterio: bool = False
    duracion_acotada: bool = False
    profundidad_alternativa: Optional[float] = None   # m
    duracion_alternativa_min: Optional[float] = None


ORIGEN_SOCAVACION_DECLARADA = "declarada (dato externo)"
ORIGEN_SOCAVACION_ESTIMADA = "estimada (HEC-14, Cap. 5)"
ORIGEN_SOCAVACION_SIN_DATO = "sin dato"


@dataclass(frozen=True)
class SocavacionSalida:
    """
    La profundidad de socavacion a la salida que la Fase 6 entrega al
    desplante del cabezal (T-7a): la DECLARADA si el punto la trae, y si no
    la ESTIMADA por HEC-14. `profundidad_para_desplante` es None cuando no
    hay ninguna de las dos, y `motivo_no_estimada` dice que dato falta.
    """

    profundidad_para_desplante: Optional[float]   # m
    origen: str
    estimada: Optional[HoyaDeSocavacion] = None
    declarada_m: Optional[float] = None
    motivo_no_estimada: str = ""
    pasos: Tuple["PasoDeMemoria", ...] = ()
    avisos: Tuple[str, ...] = ()
    # --- T-8, auditoria --- DESDE QUE COTA se mide la profundidad, que HEC-14
    # Cap. 5 no define: el valor del criterio 'referencia_profundidad_
    # socavacion', y la cota del fondo de la hoya que resulta (msnm) cuando
    # el punto trae las cotas. Es lo que T-7a toma para el desplante.
    referencia: Optional[str] = None
    cota_referencia: Optional[float] = None       # msnm
    cota_fondo_de_la_hoya: Optional[float] = None  # msnm
    # --- VE-5 (lote m6) --- La estructura de caida recta de HEC-14 Cap. 11
    # cuando la salida queda colgada (pendiente maxima del conducto, o caida
    # mas alla de la Tabla 5.2). None si no hace falta o no es evaluable
    # (lo dice un aviso).
    caida: Optional["EstructuraDeCaida"] = None


@dataclass(frozen=True)
class CamaApoyoRelleno:
    """
    Fila de la tabla 8.1 (EG-2013 Capitulo V) para un material: cama de
    apoyo y sujecion / relleno lateral, con su numeral. Es informacion para
    la memoria y los planos (Sec. 11, entregable 7), no una verificacion con
    umbral: el CSV no trae una columna de compactacion realmente lograda
    contra la que comparar.
    """
    cama_apoyo: str
    sujecion_relleno_lateral: str
    numeral: str
    # DE DONDE SALEN LOS PORCENTAJES DE COMPACTACION que la fila imprime, y
    # es un campo y no un comentario porque la memoria tiene que poder
    # decirlo. Al verificar las cuatro fichas contra el EG-2013 (NOR-EG-03)
    # aparecio que en tres de ellas el "95 % MDS" NO es literal de la
    # subseccion citada: llega por REMISION -- 506.07 y 507.08 remiten a la
    # Subseccion 205.12(c)(1), que es la que imprime Di > 0.95 De para la
    # corona y Di > 0.90 De para base y cuerpo --, y en la ficha del concreto
    # simple el 95 % de la pagina vecina es de OTRO elemento (el terreno base
    # de 505.06). El valor es correcto; lo que faltaba era decir por que via
    # llega, que es la diferencia entre una cita y una deduccion.
    # Vacio significa "todo lo que la fila imprime es literal de su
    # subseccion", que es el caso del HDPE.
    procedencia_de_los_porcentajes: str = ""


@dataclass(frozen=True)
class FactoresFlotacion:
    """
    Los tres factores de carga gamma con que V7 evalua la flotacion del
    conducto (Fase 8, item 3), leidos de 'factores_carga_aashto' (Tablas
    3.4.1-1 y 3.4.1-2 de AASHTO LRFD).

    Existe para que los tres viajen juntos con la clave del criterio de la
    que salieron: quien lea el resultado de V7 en la memoria tiene que poder
    ver CUAL gamma se aplico a cada carga, no solo el numero final. Un
    equilibrio de factores de carga en el que no se distingue el gamma del
    estabilizante del gamma del desestabilizante es indistinguible, en el
    papel, de un factor de seguridad global -- que es justo lo que V7 dejo
    de ser.

    `gamma_DC` y `gamma_EV` son los MINIMOS de la Tabla 2.4.5.3.1-2: en
    flotacion el peso propio y el peso del relleno estabilizan, y en LRFD lo
    que estabiliza se minora. `gamma_WA` es el de la subpresion, que
    desestabiliza y se mayora, y sale de la Tabla 2.4.5.3.1-1.

    `fila_gamma_EV` es la fila LITERAL de la Tabla 2.4.5.3.1-2 de la que sale
    `gamma_EV`, y viaja por la misma razon que el resto: esa tabla desglosa
    el empuje vertical de tierra POR TIPO DE ESTRUCTURA -- un muro de
    retencion y un conducto enterrado no llevan el mismo par -- y un gamma_EV
    suelto no dice de cual de las seis filas salio. El par {1.35, 0.90} que
    el proyecto uso durante un tiempo no era ninguna de ellas: mezclaba el
    maximo de una con el minimo de otra (MAT-D8, NOR-PUE-03).

    HASTA DONDE LLEGA HOY ESE CAMPO: hasta la memoria, y desde C7. Lo que
    esta clausula decia hasta entonces --- «llega a este objeto y ahi se
    queda... la memoria NO imprime hoy de que fila salio el gamma de V7» ---
    era cierto y ya no lo es. `M5.v7_flotacion` lo publica en el `valor` de su
    `EleccionDeProyecto`, junto al gamma que sale de esa fila y con las SIETE
    filas de EV de la tabla en `entre`.

    Y LA SALIDA QUE ESA CLAUSULA DABA POR NECESARIA NO LO ERA, que es lo que
    conviene no repetir: decia que llevar la fila a la memoria «pide un campo
    mas en `Verificacion` y su renderizado en M11». No pidio ninguno de los
    dos. La procedencia de un valor elegido ya tenia sitio --- la R1, que
    `EleccionDeProyecto` implementa y `M11._elecciones_del_paso` imprime ---
    y lo que faltaba era usarlo. Un campo nuevo en `Verificacion` habria sido
    un segundo canal para lo que ya tenia el suyo.
    """
    gamma_DC: float
    gamma_EV: float
    gamma_WA: float
    criterio: str
    fila_gamma_EV: str
