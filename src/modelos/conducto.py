"""
src/modelos/conducto.py
=======================
Material y geometria del conducto: Material, Seccion (circular y rectangular), Geometria.

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional, Protocol, Tuple

from src.tolerancias import TOL_THETA_BORDE

from src.modelos.errores import DatoInvalidoError, LimiteNumericoError
from src.modelos.base import FormaSeccion
from src.modelos.memoria import (
    Magnitud, cifras_de_dimension, texto_de_dimension
)

if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.base import TipoMaterial
    from src.modelos.memoria import PasoDeMemoria

# ===========================================================================
# Material y geometria
# ===========================================================================

@dataclass(frozen=True)
class ConstantesHDS5:
    """
    Constantes de control de entrada de la Tabla A.1 de HDS-5 (Sec. 4.2).
    Los nombres de campo reproducen la notacion de la hoja de ruta.

    Ks NO figura en la Tabla A.1: proviene de la formulacion de las ecuaciones
    (-0.5 sin inglete, +0.7 con inglete). No omitirlo.

    `forma` SI figura en la Tabla A.1 -- es su columna «Equation Form» -- y
    hasta C2 no se transcribia. Vale 1 o 2, y no es un matiz de precision:

        Forma 1   HWi/D = H_c/D + K*(q*)^M + Ks*S     ec. (A.1)
        Forma 2   HWi/D = K*(q*)^M                     ec. (A.2)

    La Forma 2 NO LLEVA EL TERMINO Ks*S. Esta escrito asi arriba porque la
    primera redaccion de este docstring SI se lo puso -- «HWi/D = K*(q*)^M +
    Ks*S» -- y se contradecia con su propio parrafo de mas abajo, que ya decia
    que la Forma 2 no lo lleva. Verificado contra la fuente: `normas/
    hif12026.pdf`, pag. impresa A.2 (PDF 191), imprime la ec. (A.2) como
    HWi/D = K[Ku*Q/(A*D^0.5)]^M y nada mas. El contraste que lo cierra esta en
    la MISMA pagina: la ec. (A.3), sumergida, si lleva «+ Y + Ks*S».

    El error no era inocuo y por eso queda dicho: con Ks = -0.5 el termino
    RESTA, de modo que copiarlo a la Forma 2 daria un HW MENOR que el real
    -- del lado no conservador --. Medido sobre la Carta 9 escala 1
    (K = 0.510, M = 0.667) con un cajon de 2.00 x 2.00 m, Q = 8 m3/s y
    S = 0.03: 1.910 m contra 1.880 m, 30 mm de diferencia, y crece lineal con
    la pendiente. Es exactamente el fallo que `F4.FORMA_HDS5` describe, y
    estaba escrito en el sitio donde C3 lo iba a leer primero.

    Son DOS REGRESIONES DISTINTAS sobre dos conjuntos de ensayos, y sus K y M
    estan ajustadas cada una a SU ecuacion. Quien dice cual es cual es la
    COLUMNA «Equation Form» de la Tabla A.1, fila por fila.

    ESTE PARRAFO ATRIBUIA ESO AL NUM. A.3 -- «el HDS-5 lo dice con todas las
    letras» -- Y ERA FALSO. El num. A.3 prohibe cruzar coeficientes entre
    FORMAS GEOMETRICAS («rectangular (box) shapes» frente a «nonrectangular»),
    no entre formas de ecuacion. La Tabla A.1 lo zanja: forma y geometria son
    ORTOGONALES -- «Rect. Box Concrete» aparece con Forma 1 y con Forma 2, y
    «Circular» tambien --, de modo que una prohibicion sobre geometrias no
    puede ser la regla que separa las formas. Lo encontro la auditoria de C3,
    y es el mismo genero de defecto que este docstring ya cometio con la
    ecuacion: una afirmacion sobre la fuente que la fuente no sostiene.

    Las tres cartas circulares del catalogo son Forma 1. De las cinco del
    cajon que transcribio C2, la Carta 8 es Forma 1 y las Cartas 9 a 12 son
    Forma 2.

    LAS DOS FORMAS ESTAN IMPLEMENTADAS DESDE C3, en
    `M4_control._hw_sobre_D_no_sumergido`, que bifurca por este campo. Este
    parrafo decia «quien implemente la Forma 2 es C3; este campo solo la hace
    visible», y era cierto hasta que C3 la implemento: se corrige aqui porque
    una frase que describe un estado que dejo de ser cierto es el mismo
    defecto que este docstring ya cometio una vez, solo que en prosa en vez
    de en una ecuacion.

    Que el campo exista sigue siendo la guardia: sin el, las constantes de una
    carta de Forma 2 entrarian en la ecuacion de Forma 1 -- que lleva H_c/D y
    Ks*S, y la Forma 2 ninguno de los dos --, y el HW saldria MAYOR que el
    real (+91 % medido en I3 sobre el marco de la linea base: el H_c/D
    espurio domina por dos ordenes al Ks*S que resta) sin que ninguna guardia
    de signo lo detecte. Este parrafo decia «MENOR» hasta D9, mezclando ese
    error con la mutacion de 30 mm del parrafo anterior, que es otra: alli se
    suma solo Ks*S a la (A.2); aqui se copia la (A.1) entera. Lo que C3 añade es
    que ahora tambien hay TESTS que lo detectan: `CP5D_FORMA2_KS_ESPUREO` fija
    la diferencia de 30 mm, y tres tests de `test_M4_control` se ponen rojos
    si alguien vuelve a sumar Ks*S en la Forma 2 -- comprobado mutando el
    codigo, no supuesto --.
    """
    K: float
    M: float
    c: float
    Y: float
    Ks: float
    forma: int          # columna «Equation Form» de la Tabla A.1: 1 o 2

    @classmethod
    def desde_dict(cls, datos: Dict[str, float]) -> "ConstantesHDS5":
        """Construye desde una fila de `HDS5_INLET` o de un criterio adoptado."""
        # `forma` se exige, no se rellena: un KeyError aqui dice que la fila
        # o el criterio no declara su ecuacion, y ese es un dato que hay que
        # anadir, no adivinar. Un `datos.get("forma", 1)` seria el default
        # silencioso que CLAUDE.md llama el peor error posible.
        return cls(K=datos["K"], M=datos["M"], c=datos["c"],
                   Y=datos["Y"], Ks=datos["Ks"], forma=datos["forma"])


@dataclass(frozen=True)
class Material:
    """
    Material de conducto ya resuelto por M2: sus valores provienen de
    `constantes_normativas.py` y de `criterios_adoptados.py`. Este modulo solo
    declara la forma; no fija ningun numero.

    Regla de doble n (Sec. 4.1): n maximo para capacidad y tirante, n minimo
    para velocidad MAXIMA y socavacion. Se expone con TRES propiedades -- no
    dos -- para que ningun modulo tenga que recordar cual es cual: la
    velocidad tiene dos umbrales, un techo y un piso, y cada uno se calcula
    con el n del extremo contrario. `n_para_velocidad_minima` devuelve el
    mismo numero que `n_para_capacidad`, y tiene nombre propio porque el
    motivo es otro: alli n_max da mas tirante, aqui da menos velocidad.

    Dos campos que se leen mal si no se dice de que son:

    `D_max` NO es un tope normativo. Es el tope de CATALOGO que el proyecto
    adopta ('D_max_catalogo', [A]), y `D_max_de_catalogo` trae el rotulo con
    que hay que imprimirlo. `norma_producto` es la norma que rige el producto
    -- materiales, fabricacion, aceptacion -- y NO la que topa el diametro:
    A760 tabula hasta 3600 mm y M 170M tambien (NOR-PRO-01, NOR-PRO-02).

    `h_relleno_min_eg2013` es SOLO el minimo de EG-2013, que existe unicamente
    para HDPE (Subseccion 508.07, pag. 984). No es el recubrimiento minimo del
    material: ese lo calcula `M7_geometria.altura_recubrimiento` como el mayor
    entre este y la cobertura minima de AASHTO (Tabla 12.6.6.3-1), y depende
    del diametro exterior. Un None aqui significa "EG-2013 no lo fija para
    este material", no "falta el dato".
    """

    tipo: TipoMaterial
    nombre: str                             # etiqueta para el reporte
    n_min: float                            # Tabla N 09 (o criterio adoptado)
    n_max: float
    D_max: float                            # m - tope de CATALOGO adoptado (V9)
    D_max_de_catalogo: str                  # rotulo obligatorio de ese tope
    norma_producto: str                     # designacion METRICA de la norma
                                            # de producto: "AASHTO M 170M-04 /
                                            # ASTM C 76M-02 (metrica)",
                                            # "AASHTO M 36 / ASTM A760/A760M-10",
                                            # "AASHTO M 294-11 (en normas/:
                                            # traduccion no oficial)". Las imperiales
                                            # (C76, M170) nombran documentos
                                            # que este expediente no tiene y
                                            # cuyas tablas van en pulgadas
                                            # (NOR-PRO-05)
    hds5: ConstantesHDS5                    # carta adoptada en Sec. 4.2
    fila_manning: str                       # fila LITERAL de la Tabla N 09
    # Los dos techos de velocidad, separados porque son dos cosas distintas y
    # un solo campo las confundia (SIS-A-06): el campo anotado
    # `Optional[Tuple[float, float]]` transportaba el par de la Tabla N 10 para
    # el concreto y un ESCALAR para TMC y HDPE, de modo que el contrato que se
    # consulta aqui decia lo que el dato no era.
    v_max_tabla10: Optional[Tuple[float, ...]]   # m/s - fila de la Tabla N 10,
                                            # tal cual: dos valores para el
                                            # concreto, uno para la
                                            # mamposteria. None = el material
                                            # NO tiene fila en esa tabla
    v_max_adoptado: Optional[float]         # m/s - techo escalar de un criterio
                                            # [C] (TMC, HDPE). None = el techo
                                            # sale de la tabla, o falta declararlo
    h_relleno_min_eg2013: Optional[float]   # m sobre la clave; None = EG-2013 no lo fija
    espesor_pared: Optional[float]          # m - t; None = criterio sin declarar
    seccion_eg2013: str                     # 505 / 506 / 507 / 508 (Capitulo V)
    # EL QUE AÑADE C5: el catalogo dejo de ser solo circular y hay decisiones
    # que YA NO se pueden deducir del `tipo`. Un marco de concreto y un tubo
    # de concreto son el mismo `TipoMaterial`, y lo que los separa es de que
    # progresion sale su seccion, de que fila su n y de que carta de HDS-5 sus
    # constantes de control de entrada.
    forma: FormaSeccion                     # de que progresion sale la seccion
    # LA TRAZA DE FASE 3, y viaja con el material porque es donde se decide.
    # M2 la emite al resolver el catalogo -- que tipo de estructura, que
    # seccion, cuantas celdas, que fila de rugosidad -- y `M4._pasos_
    # hidraulicos` la antepone a la suya, de modo que llega a la memoria por
    # el MISMO canal que ya existe (`ResultadoHidraulico.pasos`, que M11
    # imprime bajo «Fases 3 y 4»). Sin este campo habria que abrir un canal
    # nuevo en el reporte, que es de otra sesion.
    #
    # VACIA EN EL TMC Y EN EL HDPE (VE-5, ficha VE2-A (3): decia «en la
    # circular», y el tubo de concreto la llena desde VE-2), y no por
    # olvido: esos tubos no eligen nada en Fase 3 que no este ya en el bloque
    # de criterios -- su fila de rugosidad y su carta de HDS-5 son lectura
    # directa, no adopcion --. EL TUBO DE
    # CONCRETO, desde VE-2 (a), si: la COLUMNA de su fila de la Tabla N 09 es el
    # criterio [A] 'columna_n_manning_concreto', y su eleccion viaja aqui
    # (paso F4.N_CONCRETO de `M2._pasos_del_tubo_de_concreto`). El marco si:
    # cuatro de sus cinco decisiones son criterios declarados por el
    # proyectista, y una memoria que no las desarrolle no las puede defender.
    pasos: Tuple["PasoDeMemoria", ...] = ()
    # --- T-4 --- DE QUE CRITERIO SALIO `D_max`. Desde T-4 el tope puede
    # venir de dos sitios: la SERIE de la norma de producto
    # ('D_max_norma_producto' [C], la regla) o la disponibilidad de mercado
    # que el proyectista declare por debajo ('D_max_catalogo' [A], opcional);
    # en el marco, de 'secciones_cajon_normalizadas'. V9 y el motivo de
    # descarte de MD lo leen de aqui en vez de suponer la clave: con la clave
    # cableada, un tope de norma se imprimia «de catalogo», que es la cita
    # falsa de NOR-PRO-01 leida al reves. Vacio = constructor que no pasa por
    # `M2.catalogo` (dobles de prueba): quien lo lea cae al rotulo.
    D_max_criterio: str = ""
    # --- VE-5 (m8), item 23 (ficha T5-03) --- LA PLANCHA DEL TMC con que se
    # arma la geometria: vacia = la adoptada ('corrugacion_y_espesor_tmc');
    # si no, la que la Fase 8 eligio y MD devolvio al material
    # (`M2.material_con_plancha_tmc`), y entonces `espesor_pared` ya la lleva.
    plancha_tmc: str = ""

    def __post_init__(self) -> None:
        # EL PAR ES UN PAR (PC-01): n_min <= n_max, o la regla de doble n se
        # invierte entera y cada verificacion usa el n del lado equivocado
        # sin que ninguna lo note. M2 lo exige al leer el criterio; esto es
        # la red de abajo para cualquier constructor que no pase por M2.
        # Escrito negado (`not n_min <= n_max`) para que un NaN no se cuele,
        # como en MAT-D13. Es DatoInvalidoError y no ValueError: el par lo
        # escribio el expediente (un criterio o una tabla), no el programa.
        # El None es el de «Campos que el catalogo puede dejar en None» (M2):
        # el criterio del HDPE vacio viaja como (None, None) y lo detiene el
        # consumidor, no este constructor. Sin esta salvedad el None salia de
        # aqui como TypeError (auditor adversarial de EXT-1).
        if self.n_min is None or self.n_max is None:
            return
        if not self.n_min <= self.n_max:
            raise DatoInvalidoError(
                "n_manning", valor=(self.n_min, self.n_max),
                motivo=f"el par de Manning de {self.nombre} esta invertido o "
                       f"no es comparable: n_min = {self.n_min!r} tiene que "
                       f"ser <= n_max = {self.n_max!r} (regla de doble n, "
                       "Sec. 4.1: n_max para capacidad, n_min para velocidad)")

    @property
    def n_para_capacidad(self) -> float:
        """n maximo: conservador del lado de la inundacion (Sec. 4.1)."""
        return self.n_max

    @property
    def n_para_velocidad_maxima(self) -> float:
        """
        n minimo: conservador del lado de la erosion (Sec. 4.1), o sea contra
        los TECHOS de velocidad -- V3 y el d50 de Laushey. Es la estimacion
        ALTA de velocidad.

        El nombre reproduce el de la hoja de ruta (Sec. 4.1: n minimo para
        "velocidad maxima y socavacion"). Se llamaba `n_para_velocidad`, sin
        el "maxima", y ese nombre era la mitad del defecto MAT-D1: leido desde
        V2 -- que es tambien una verificacion de velocidad -- parecia el n que
        le tocaba, y no lo es.
        """
        return self.n_min

    @property
    def n_para_velocidad_minima(self) -> float:
        """
        n maximo: el que da la estimacion BAJA de velocidad sobre la geometria
        de diseño, y por lo tanto el conservador contra un PISO de velocidad
        (V2, autolimpieza, Sec. 4.1.1.3.6).

        Devuelve el mismo numero que `n_para_capacidad` y existe aparte porque
        la razon es distinta: en capacidad n_max se usa porque exige mas area,
        y aqui porque entrega menos velocidad. Si algun dia el proyecto tomara
        el n de dos tablas distintas para las dos cosas, esta propiedad es la
        que cambiaria sin tocar la otra.
        """
        return self.n_max

    @property
    def v_max_definida(self) -> bool:
        """
        True si el material tiene un techo de velocidad aplicable: fila en la
        Tabla N 10, o techo escalar declarado en su criterio.

        HOY DEVUELVE True PARA LOS TRES, y el docstring anterior decia lo
        contrario -- "False para TMC y HDPE mientras el Tablero 1.3 siga
        abierto" (SIS-A-06). La frase no era falsa cuando se escribio: era
        condicional, y su condicion se cerro al declararse 'v_max_tmc' y
        'v_max_hdpe' con la fuente WSDOT. Vuelve a False para TMC o HDPE si
        alguien vacia esos criterios, que es justo lo que este campo tiene que
        poder decir.
        """
        return self.v_max_tabla10 is not None or self.v_max_adoptado is not None


class Seccion(Protocol):
    """
    La forma del barril, detras de una interfaz (Sec. 4.1 del plan de la
    Familia C). M3 y M4 dejan de saber si el conducto es un circulo.

    MODELA UNA CELDA. El numero de celdas vive fuera y se reparte el caudal:
    los coeficientes de HDS-5, el radio hidraulico y el control de entrada son
    POR BARRIL.

    DOS PARAMETRIZACIONES, Y NO ES REDUNDANCIA. La interfaz de arriba --
    `area(y)`, `perimetro(y)`, `ancho_superficial(y)` -- esta escrita sobre el
    TIRANTE, que es el lenguaje de la Sec. 4.1 y el que una seccion
    rectangular usa directamente. La de abajo -- `bracket_llenado()`,
    `geometria_en()`, `ancho_superficial_en_llenado()` -- esta escrita sobre
    el PARAMETRO PROPIO de la seccion, que en la circular es el angulo mojado
    theta y en una rectangular seria el propio tirante.

    Por que existen las dos: el solver de Manning y el del tirante critico
    recorren la seccion con Brent, y en la circular lo hacen SOBRE THETA. Si
    el solver pasara a recorrer el tirante, la raiz a la que converge cambia
    en los ultimos bits y con ella todos los numeros que cuelgan de ella. Eso
    no es un refactor, es un cambio de metodo numerico. La seccion expone su
    propio parametro para que el solver no tenga que elegir uno, y asi M3 y M4
    quedan ciegos a la forma SIN mover un digito.

    LAS DOS MITADES NO SON INTERCAMBIABLES, Y ESTE ES EL AVISO. La CANONICA
    es la del parametro propio -- es la que consumen M3 y M4 y sobre la que
    resuelve Brent --. La del tirante es de LECTURA, y desde C4 tiene DOS
    consumidores en produccion, los dos dentro de
    `SeccionRectangular.geometria_en`: el unico sitio donde no puede
    equivocarse, porque en esa forma el parametro propio ES el tirante y las
    dos vias coinciden bit a bit. Que sean dos y no mas lo vigila un censo del
    AST --`test_seccion_rectangular::test_la_via_por_tirante_no_gana_
    consumidores_sin_declararlos`--, y no un comentario: la auditoria de C4
    demostro que un comentario no basta. Esta escrito como regla vinculante
    #12 de docs/ruta_familia_c.md; aqui va lo imprescindible.

    En la circular, `area(y)` / `perimetro(y)` / `ancho_superficial(y)` pasan
    por `theta_desde_tirante(y)`, que es la inversa ALGEBRAICA de
    `_tirante_en_theta` pero no su inversa en punto flotante. El error del
    viaje de ida y vuelta NO ESTA ACOTADO POR UNA CONSTANTE: es un problema de
    CONDICIONAMIENTO concentrado en los dos extremos del llenado. Medido en C1
    sobre ocho diametros de 0.30 a 3.00 m:

        y/D en [0.10, 0.75] (la ventana que admite V1)
            A 9.7e-16   P 3.9e-16   T 4.0e-16      -- ultimos bits
        y/D en [0.01, 0.99]
            A 5.2e-15   P 1.5e-15   T 8.8e-15
        theta = 1e-6 rad
            P y T: 4.4e-5

    Y EN LOS EXTREMOS DEL BRACKET, con la correccion que midio C4. C1 escribio
    aqui "en los DOS extremos la via por tirante devuelve 0.0 EXACTO para P y
    para T", y eso vale ENTERO en uno solo de los dos. Medido sobre D = 0.90:

        theta = 1e-9 (extremo INFERIOR)
            canonica    P = T = 4.5e-10
            por tirante P = T = 0.0            <- 100 %, y cero EXACTO
        theta = 2*pi - 1e-9 (extremo SUPERIOR)
            canonica    T = 4.500001474513789e-10
            por tirante T = 1.1021821192326179e-16   <- ~100 % relativo, pero
                                                        NO es cero exacto
            canonica    P = 2.8274333877808138
            por tirante P = 2.827433388230814        <- 1.6e-10 relativo: el
                                                        perimetro NO se anula

    La consecuencia no cambia y sigue siendo peor que una deriva: `T` es el
    denominador de `A^3/T` en `M4_control._residuo_critico`, y el cero exacto
    esta justo en el extremo INFERIOR, que es de los primeros puntos donde
    Brent evalua. Quien reescriba el residuo sobre `ancho_superficial(y)` no
    mete un 1e-12: DIVIDE POR CERO, y reintroduce la clase de fallo que
    SIS-G-02 cerro. Lo unico que se corrige es el enunciado -- en el extremo
    superior el perimetro coincide en los ultimos bits --, y se corrige porque
    una regla vinculante que dice de mas se deja de creer entera.

    En el centro del rango las dos vias coinciden BIT A BIT (theta = pi:
    divergencia 0.0 exacta en las tres magnitudes), de modo que una
    comprobacion puntual las aprueba. Por eso el aviso esta aqui y no en un
    test: no se detecta mirando.

    En una seccion rectangular el parametro propio ES el tirante y las dos
    vias coinciden exactamente. Eso no autoriza a pasar M3 y M4 a la via por
    tirante: en la circular movería todos los numeros.

    Regla operativa: el valor que ya viene en un `Geometria` -- `g.A`, `g.P`,
    `g.T`, `g.R` -- NO se recalcula. La via por tirante solo se usa donde el
    llamador tenga un tirante y ningun `Geometria`, nunca dentro de un solver.
    """

    @property
    def altura(self) -> float:
        """m - altura interior del barril. Es el "D" de HDS-5."""
        ...

    @property
    def area_llena(self) -> float:
        """m2 - area de la seccion llena. La consumen q* y el control de salida."""
        ...

    @property
    def radio_hidraulico_lleno(self) -> float:
        """m - radio hidraulico de la seccion llena (Sec. 4.3)."""
        ...

    def ancho_exterior(self, espesor: float) -> float:
        """
        m - `Bc`: ancho exterior de la seccion en planta, con la pared.

        La nomenclatura es la del Art. 12.6.6.3 de AASHTO LRFD, que define
        `Bc` como *"outside diameter or width of the structure"*: es la
        dimension HORIZONTAL. Lo consume el peso del relleno de V7 -- el
        prisma de suelo tiene el ancho que el conducto ocupa de verdad en
        planta -- y es tambien el termino `Bc/8` de la cobertura minima.
        """
        ...

    def canto_exterior(self, espesor: float) -> float:
        """
        m - `B'c`: canto exterior de la seccion, con la pared.

        El mismo articulo lo define como *"out-to-out vertical rise of pipe"*:
        es la dimension VERTICAL, y por eso NO es intercambiable con
        `ancho_exterior`. En una circular las dos coinciden -- por eso el
        proyecto pudo vivir hasta C7 con un solo `D_exterior` --; en un marco
        no, y confundirlas es el error que la regla vinculante #9 estuvo a
        punto de introducir.
        """
        ...

    def area_exterior(self, espesor: float) -> float:
        """
        m2 - area que encierra la superficie EXTERIOR de la seccion.

        Es el volumen desplazado por metro lineal, o sea la subpresion de V7
        dividida por el peso especifico del agua (num. 2.4.3.8.2 del Manual de
        Puentes: la fuerza actua sobre "todos los componentes de la estructura
        que se encuentran debajo del nivel de agua de diseno").

        NO SE DERIVA DE LOS DOS ANTERIORES, y por eso es un miembro propio: en
        un rectangulo el area exterior SI es `Bc * B'c`, pero en una circular
        es `pi/4 * D_ext^2`, que no es el producto de sus dos dimensiones
        exteriores. Calcularla como producto le daria a la circular un 27 % de
        area de mas -- la del cuadrado circunscrito --, que es la direccion
        insegura al reves: mas subpresion de la real.
        """
        ...

    def etiqueta(self) -> str:
        """Como se nombra la seccion en la memoria."""
        ...

    def exigir_dimensiones_positivas(self) -> None:
        """
        Valida las dimensiones que definen la seccion y lanza
        `DatoInvalidoError` --con el NOMBRE del dato-- si alguna no la cumple.

        VIVE AQUI Y NO EN M3/M4 por dos razones. La primera es que el mensaje
        nombra el dato --`campo` y `motivo` se imprimen los dos, en la memoria
        y en el JSON-- y quien sabe como se llama el dato es la seccion. La
        segunda es que hasta C4 la MISMA pareja de cadenas estaba escrita dos
        veces, en `M3._validar_parametros` y en `M4._validar_Q_D`: dos copias
        que hay que editar juntas para siempre.

        Y EL NOMBRE NO ES EL "D" DE HDS-5, que es la distincion que C4 tuvo
        que decidir (anotacion A-4 de §16.4). Son dos vocabularios que
        coinciden en la circular y se separan en cuanto hay una forma que no
        es un circulo:

          * En las ECUACIONES DE HDS-5 --q*, HW/D, h_o-- "D" es correcto para
            cualquier forma: la fuente lo define como *"D - Interior height of
            culvert barrel"* (regla vinculante #4 de la Familia C). Esas
            formulas siguen escribiendo "D" y no se tocan.
          * En el DATO DE ENTRADA que el revisor tiene que corregir, "D"
            significa diametro. Una `SeccionRectangular` no tiene diametro:
            sus datos son el ancho B y la altura H. Los nombres de aqui son
            esos, y por eso los pone la seccion.
        """
        ...

    def magnitudes_de_forma(self) -> Tuple["Magnitud", ...]:
        """
        Las dimensiones que DEFINEN esta seccion, como `Magnitud` de memoria.

        Una circular se define con un numero y una rectangular con dos: la
        sustitucion de un paso no puede cablear cuantos son ni como se llaman.
        """
        ...

    def formula_geometria(self) -> str:
        """
        Como se calculan A, P y R en esta forma, para imprimirlo en la memoria.

        Es el hueco que el num. 4.1.1.3.6 deja abierto: prescribe Manning y
        define A, P y R --por su significado y su unidad, con R = A/P como
        unica relacion entre ellos-- y NO escribe ninguna geometria de
        seccion. Lo rellena la seccion, y por eso la frase sale de aqui.

        EL SUJETO ES EL NUMERAL Y NO EL MANUAL, y la precision importa: el
        Manual SI enumera formas y SI impone una, en el num. 4.1.1.3.4 a).
        El que no fija ninguna es este numeral.
        """
        ...

    def llenado_critico_cerrado(self, Q: float, g: float) -> Optional[float]:
        """
        El parametro propio en estado CRITICO, si esta forma lo despeja; si no,
        `None` y quien llama resuelve con Brent.

        `g` LLEGA COMO ARGUMENTO Y NO SE IMPORTA AQUI, a proposito: la seccion
        conoce el algebra de su forma, no cuanto vale la gravedad. Este modulo
        declara tipos y geometria; que g valga 9.81 lo dice
        `constantes_fisicas`, y quien lo consume es el modulo de calculo.
        """
        ...

    def area(self, y: float) -> float:
        """m2 - area hidraulica al tirante y."""
        ...

    def perimetro(self, y: float) -> float:
        """m - perimetro mojado al tirante y."""
        ...

    def ancho_superficial(self, y: float) -> float:
        """m - ancho de la lamina al tirante y. Es el T del tirante critico."""
        ...

    def bracket_llenado(self) -> Tuple[float, float]:
        """Extremos del intervalo que Brent recorre sobre el parametro propio."""
        ...

    def geometria_en(self, llenado: float) -> "Geometria":
        """`Geometria` completa para un valor del parametro propio."""
        ...

    def ancho_superficial_en_llenado(self, llenado: float) -> float:
        """m - el T, desde el parametro propio y no desde el tirante."""
        ...


@dataclass(frozen=True)
class SeccionCircular:
    """
    Seccion circular parcialmente llena (Sec. 4.1):

        A = (D^2/8)(theta - sen theta)      P = D*theta/2      R = A/P

    theta en radianes, sobre (0, 2*pi). Todas las longitudes en metros.

    Su parametro propio de llenado es THETA, el angulo mojado, y por eso el
    bracket de Brent sale de aqui: es la seccion la que sabe sobre que
    variable se la recorre.
    """

    D: float          # m - diametro interior

    @property
    def altura(self) -> float:
        """En un circulo la altura interior ES el diametro."""
        return self.D

    @property
    def area_llena(self) -> float:
        """A = pi*D^2/4. La usan q* (Sec. 4.2) y el control de salida (Sec. 4.3)."""
        return math.pi * self.D ** 2 / 4  # literal-ok: area del circulo, pi*D^2/4

    @property
    def radio_hidraulico_lleno(self) -> float:
        """R = A/P = (pi*D^2/4)/(pi*D) = D/4, seccion llena (Sec. 4.3)."""
        return self.D / 4  # literal-ok: R = A/P de la seccion llena, D/4

    # -- Geometria EXTERIOR: la que ve el agua y el relleno, no el caudal.
    #
    # EN UNA CIRCULAR LAS DOS DIMENSIONES EXTERIORES COINCIDEN, y esa
    # coincidencia es la que dejo pasar el error que la regla #9 estuvo a
    # punto de introducir: mientras el catalogo fue circular, `Bc` y `B'c`
    # eran el mismo numero y nadie tenia que distinguirlos. Se implementan
    # como dos miembros aunque aqui devuelvan lo mismo, porque el protocolo
    # los separa y un marco los separa de verdad.

    def ancho_exterior(self, espesor: float) -> float:
        """Bc = D + 2t: el diametro exterior."""
        return self.D + 2 * espesor

    def canto_exterior(self, espesor: float) -> float:
        """B'c = D + 2t. En un circulo el canto exterior ES el ancho."""
        return self.D + 2 * espesor

    def area_exterior(self, espesor: float) -> float:
        """
        pi/4 * (D + 2t)^2 -- el volumen desplazado por metro lineal.

        NO es `ancho_exterior * canto_exterior`: eso seria el cuadrado
        circunscrito, un 4/pi = 27 % mas de area, y en V7 mas area es mas
        subpresion, o sea el lado inseguro al reves. Es la razon por la que
        `area_exterior` es un miembro del protocolo y no una derivacion de
        los otros dos.
        """
        return math.pi * self.ancho_exterior(espesor) ** 2 / 4  # literal-ok: area del circulo

    def etiqueta(self) -> str:
        """
        Como la memoria nombra la seccion. Su consumidor llega con el reporte
        de la Familia C; hoy no lo invoca ningun modulo y se declara igual,
        porque es parte del contrato de `Seccion` y una implementacion que no
        lo cumpliera no seria sustituible por otra. Su ficha esta en
        `docs/decisiones_diferidas.md` (C1-02).

        El rotulo es el que fija la §4.1 del plan de la Familia C -- "Ø 0.90 m"
        frente al "marco 2.00 x 1.50 m" de la rectangular --. C1 lo escribio
        primero como "D 0.90 m", que no era el de la especificacion desde la
        que se escribio la clase; corregido al cierre. Los decimales son
        PRESENTACION, de la misma naturaleza que los `FMT_*` de M11: no dicen
        cuanto vale nada. Desde VE-1 (H1) los escribe `texto_de_dimension`:
        dos como minimo («Ø 0.90 m», como siempre) y los que el diametro
        declarado tenga («Ø 1.0668 m»). Con dos fijos, la serie de 6 in se
        rotulaba «Ø 1.07 m», el diametro que nadie declaro.
        """
        return f"Ø {texto_de_dimension(self.D)} m"

    def exigir_dimensiones_positivas(self) -> None:
        """
        EL TEXTO ES EL DE ANTES, LETRA POR LETRA, y eso es lo que hace que
        renombrar no fuera la respuesta a la anotacion A-4 de §16.4. Un tubo
        SI tiene diametro: "D" no era falso aqui, lo era en la otra forma. La
        correccion consiste en que el nombre lo ponga la seccion, no en
        cambiarselo a la que lo tenia bien.

        La condicion se escribe EN POSITIVO Y NEGADA (`not ... > 0`) con la
        plantilla de MAT-D13: `<= 0` deja pasar un NaN --es falso frente a los
        dos operadores-- y un diametro NaN llegaba hasta Brent, que revienta
        fuera de `ErrorProyecto`. Es la tercera anotacion que C1 dejo abierta.
        """
        if not self.D > 0:
            raise DatoInvalidoError(
                "D", valor=self.D, motivo="el diametro debe ser positivo")

    def magnitudes_de_forma(self) -> Tuple["Magnitud", ...]:
        """El diametro, que es la unica dimension que define un circulo."""
        return (Magnitud("D", self.D, "m",
                         "diametro interior del barril, que en un circulo es "
                         "tambien su altura interior: el «D» de HDS-5",
                         cifras=cifras_de_dimension(self.D)),)

    def formula_geometria(self) -> str:
        """Las tres de la Sec. 4.1, escritas sobre el angulo mojado."""
        return ("A = (D^2/8)(theta - sen theta), P = D*theta/2, R = A/P, "
                "con theta el angulo mojado")

    def llenado_critico_cerrado(self, Q: float, g: float) -> Optional[float]:
        """
        `None`: en la circular el critico NO se despeja.

        A^3/T = Q^2/g con A = (D^2/8)(theta - sen theta) y T = D*sen(theta/2)
        es trascendente en theta, y por eso M4 le pone su segundo Brent. Este
        `None` no es un hueco: es la respuesta, y es la que hace que el modulo
        de calculo no tenga que preguntar de que forma es la seccion.
        """
        return None

    # --- interfaz por TIRANTE (Sec. 4.1) -----------------------------------
    # Es la que una seccion rectangular usa directamente. En la circular pasa
    # por la inversion theta(y) = 2*arccos(1 - 2y/D), que es cerrada y exacta.
    # NINGUN SOLVER DE HOY ENTRA POR AQUI: los dos recorren theta.

    def theta_desde_tirante(self, y: float) -> float:
        """theta = 2*arccos(1 - 2y/D), inversa de y = (D/2)(1 - cos(theta/2))."""
        return 2 * math.acos(1 - 2 * y / self.D)

    def area(self, y: float) -> float:
        return self._area_en_theta(self.theta_desde_tirante(y))

    def perimetro(self, y: float) -> float:
        return self._perimetro_en_theta(self.theta_desde_tirante(y))

    def ancho_superficial(self, y: float) -> float:
        return self.ancho_superficial_en_llenado(self.theta_desde_tirante(y))

    # --- parametrizacion propia: theta -------------------------------------

    def bracket_llenado(self) -> Tuple[float, float]:
        """
        (theta_min, theta_max) sobre (0, 2*pi), separados del borde por
        `tolerancias.TOL_THETA_BORDE`: en theta = 0 y theta = 2*pi exactos el
        area y el perimetro se anulan y Brent no tiene residuo que morder.
        """
        return TOL_THETA_BORDE, 2 * math.pi - TOL_THETA_BORDE

    def _area_en_theta(self, theta: float) -> float:
        """A = (D^2/8)(theta - sen theta), Sec. 4.1."""
        return (self.D ** 2 / 8) * (theta - math.sin(theta))  # literal-ok: Sec. 4.1

    def _perimetro_en_theta(self, theta: float) -> float:
        """P = D*theta/2, Sec. 4.1."""
        return self.D * theta / 2

    def _tirante_en_theta(self, theta: float) -> float:
        """
        y = (D/2)(1 - cos(theta/2)): identidad geometrica de la seccion
        circular, no un valor normativo -- se deriva de la propia definicion
        de theta como angulo mojado.
        """
        return (self.D / 2) * (1 - math.cos(theta / 2))

    def ancho_superficial_en_llenado(self, llenado: float) -> float:
        """
        Ancho superficial, T = D*sen(theta/2), con theta = `llenado`.

        EL PARAMETRO SE LLAMA COMO EN EL PROTOCOLO y no `theta`, aunque aqui
        theta sea. Un `Protocol` con nombres distintos en cada implementacion
        no es sustituible por palabra clave --`seccion.geometria_en(llenado=x)`
        reventaria en una forma y no en la otra--, y la sustituibilidad es
        justamente la propiedad que hace que M3 y M4 puedan quedarse ciegos a
        la forma. Lo comprueba
        `test_seccion_rectangular::test_las_dos_secciones_implementan_el_protocolo_entero`.

        Identidad geometrica de la seccion circular, no un valor normativo:
        se deriva de y = (D/2)(1 - cos(theta/2)). La necesita M4 para el
        tirante critico, Q^2*T/(g*A^3) = 1 (Sec. 4.2).
        """
        return self.D * math.sin(llenado / 2)

    def geometria_en(self, llenado: float) -> "Geometria":
        """
        Arma la `Geometria` completa (A, P, R, y) para un theta dado.

        `llenado` es theta; se llama asi por el protocolo (ver
        `ancho_superficial_en_llenado`).
        """
        theta = llenado
        A = self._area_en_theta(theta)
        P = self._perimetro_en_theta(theta)
        return Geometria(seccion=self, llenado=theta, A=A, P=P, R=A / P,
                         y=self._tirante_en_theta(theta))


@dataclass(frozen=True)
class SeccionRectangular:
    """
    Marco rectangular parcialmente lleno (Sec. 4.1 del plan de la Familia C):

        A = B*y        P = B + 2y        R = A/P        T = B

    MODELA UNA CELDA, Y ESO NO ES UN DETALLE DE IMPLEMENTACION. Es la regla
    vinculante #3: los coeficientes de HDS-5, el radio hidraulico y el control
    de entrada son POR BARRIL. Con N celdas se diseña UNA celda con Q/N y se
    declara N; el numero de celdas no entra aqui ni multiplica nada de esta
    clase. Meterlo dentro seria construir una seccion de area N*B*H cuyo
    perimetro mojado no es el de ningun barril real, y con ella un R que no
    corresponde a ninguna celda: el q* saldria de una abertura que no existe.
    Donde vive N es en la Fase 3 (criterio de celdas, C5), fuera de la
    geometria.

    SU PARAMETRO PROPIO ES EL TIRANTE, y por eso las dos parametrizaciones de
    `Seccion` COINCIDEN EXACTAMENTE aqui: `geometria_en(y)` y `area(y)` dan el
    mismo numero, bit a bit, porque no hay ninguna inversion por medio. ESO NO
    AUTORIZA A CAMBIAR DE VIA EN M3 NI EN M4 (regla vinculante #12): en la
    circular la via por tirante pasa por `theta_desde_tirante`, que esta mal
    condicionada. En el extremo INFERIOR del bracket devuelve 0.0 EXACTO para
    P y para T --y T es el denominador de A^3/T en `M4._residuo_critico`, o
    sea una division por cero en uno de los primeros puntos donde Brent
    evalua--. En el SUPERIOR no: alli el perimetro coincide en los ultimos
    bits (1.6e-10 relativo) y solo T cae, sin llegar a cero. La coincidencia
    de las dos vias es una propiedad de ESTA forma, no del protocolo.

    LAS DOS "R" DE UN MARCO NO SON LA MISMA, y conviene verlo antes de
    compararlas. `geometria_en(y).R` es de LAMINA LIBRE: su perimetro mojado
    es B + 2y y NO incluye la losa superior, porque a esa altura el agua no la
    toca. `radio_hidraulico_lleno` es de SECCION LLENA A PRESION: su perimetro
    es 2(B+H), con la losa dentro. En y = H las dos existen y NO coinciden --
    con B = 2.00 m y H = 1.50 m dan 0.600 m y 0.4286 m, un 40 % de diferencia
    --, y no es un error de ninguna de las dos: son dos regimenes distintos, y
    cada consumidor usa el suyo (Manning, el de lamina libre; el control de
    salida de la Sec. 4.3, el lleno). En la CIRCULAR esta distincion no se ve
    porque las dos convergen: en theta = 2*pi el ancho de la lamina se anula y
    el perimetro de lamina libre YA es el perimetro completo, pi*D. En un
    marco el ancho de la lamina vale B hasta el final y nunca convergen.
    """

    B: float          # m - ancho interior de UNA celda
    H: float          # m - altura interior del barril

    @property
    def altura(self) -> float:
        """La altura interior es H. Es el "D" de HDS-5 (regla #4)."""
        return self.H

    # -- Geometria EXTERIOR: aqui las dos dimensiones SI se separan, y es la
    # razon por la que el protocolo tiene dos miembros y no uno.

    def ancho_exterior(self, espesor: float) -> float:
        """Bc = B + 2t: el ancho exterior en planta."""
        return self.B + 2 * espesor

    def ancho_exterior_de_celdas(self, espesor: float, celdas: int) -> float:
        """
        --- T-3 --- El ancho exterior del marco de N celdas MONOLITICO:

            N*B + (N - 1)*t + 2*t

        Las celdas comparten tabique, del mismo espesor que las paredes
        (un solo criterio, 'espesor_pared_cajon'): es la geometria de un marco
        vaciado in situ (§14.1 de docs/ruta_familia_c.md). Con N = 1 es
        `ancho_exterior`. Vive aqui y no en M5 ni en M7 porque lo leen los
        dos -- V6 con N > 1 y la geometria del marco de 7.B -- y dos copias de
        la misma cuenta son como divergen los numeros.
        """
        return celdas * self.B + (celdas - 1) * espesor + 2 * espesor

    def canto_exterior(self, espesor: float) -> float:
        """
        B'c = H + 2t: el canto exterior.

        DISTINTO DE `ancho_exterior`, y esa es toda la diferencia con la
        circular. Un marco de 2.00 x 1.50 m con t = 0.15 tiene Bc = 2.30 m y
        B'c = 1.80 m: intercambiarlos cambia la subpresion y el peso de
        relleno en sentidos opuestos.
        """
        return self.H + 2 * espesor

    def area_exterior(self, espesor: float) -> float:
        """
        (B + 2t)*(H + 2t) -- el volumen desplazado por metro lineal.

        En un prisma el area exterior SI es el producto de sus dos
        dimensiones exteriores. Es mas simple que en la circular, no mas
        dificil: el rectangulo exterior no tiene nada que descontar.
        """
        return self.ancho_exterior(espesor) * self.canto_exterior(espesor)

    @property
    def area_llena(self) -> float:
        """A = B*H. La usan q* (Sec. 4.2) y el control de salida (Sec. 4.3)."""
        return self.B * self.H

    @property
    def radio_hidraulico_lleno(self) -> float:
        """
        R = A/P = B*H / (2(B+H)), seccion llena (Sec. 4.3).

        El perimetro lleva la losa superior: a seccion llena el agua moja los
        cuatro lados. Es el de PRESION, no el de lamina libre; ver el
        docstring de la clase.
        """
        return self.B * self.H / (2 * (self.B + self.H))

    def etiqueta(self) -> str:
        """
        El rotulo que fija la §4.1 del plan: "marco 2.00 × 1.50 m", con las
        dimensiones declaradas sin redondear (`texto_de_dimension`, VE-1 H1).
        """
        return (f"marco {texto_de_dimension(self.B)} × "
                f"{texto_de_dimension(self.H)} m")

    def exigir_dimensiones_positivas(self) -> None:
        """
        Las DOS dimensiones, y en el orden en que se declaran. Un marco se
        define con dos numeros: validar solo la altura dejaria pasar un ancho
        nulo, y con B = 0 el caudal por unidad de ancho q = Q/B no existe.

        Y LOS NOMBRES SON "B" Y "H", no "D": un marco no tiene diametro. Es la
        mitad de la anotacion A-4 de §16.4 que solo esta sesion podia decidir,
        porque es la primera que ve las dos formas a la vez.

        Condicion en positivo y negada, plantilla de MAT-D13.
        """
        if not self.B > 0:
            raise DatoInvalidoError(
                "B", valor=self.B,
                motivo="el ancho interior del marco debe ser positivo")
        if not self.H > 0:
            raise DatoInvalidoError(
                "H", valor=self.H,
                motivo="la altura interior del marco debe ser positiva")

    def magnitudes_de_forma(self) -> Tuple["Magnitud", ...]:
        """
        LAS DOS, y en este orden. Una circular se define con un numero y un
        marco con dos: es la razon por la que la sustitucion de un paso pide
        esta tupla a la seccion en vez de escribir "D".
        """
        return (
            Magnitud("B", self.B, "m",
                     "ancho interior de UNA celda; con N celdas se diseña una "
                     "celda con Q/N (regla #3: el control de entrada y el "
                     "radio hidraulico son POR BARRIL)",
                     cifras=cifras_de_dimension(self.B)),
            Magnitud("H", self.H, "m",
                     "altura interior del barril: el «D» de HDS-5, que la "
                     "fuente define como *interior height of culvert barrel*",
                     cifras=cifras_de_dimension(self.H)),
        )

    def formula_geometria(self) -> str:
        """Las tres, escritas sobre el tirante, que es el parametro propio."""
        return "A = B*y, P = B + 2y, R = A/P, con y el tirante"

    # --- interfaz por TIRANTE (Sec. 4.1) -----------------------------------
    # AQUI ES LA MISMA QUE LA DE ABAJO: el parametro propio de un marco es el
    # tirante. Las dos vias no se unifican porque en la circular no coinciden
    # (regla vinculante #12) y el protocolo es uno solo para las dos.

    def area(self, y: float) -> float:
        return self.B * y

    def perimetro(self, y: float) -> float:
        """
        P = B + 2y: fondo y dos hastiales. NO lleva la losa superior, ni
        siquiera en y = H, porque este es el perimetro de LAMINA LIBRE.
        """
        return self.B + 2 * y

    def ancho_superficial(self, y: float) -> float:
        """T = B, constante. Es lo que cierra el tirante critico."""
        return self.B

    # --- parametrizacion propia: el propio tirante --------------------------

    def bracket_llenado(self) -> Tuple[float, float]:
        """
        (0, H): el intervalo entero, SIN margen de borde.

        La circular necesita `TOL_THETA_BORDE` porque en theta = 0 y en
        theta = 2*pi el area y el perimetro se anulan los dos y R = 0/0 queda
        indeterminado. Aqui no pasa: en y = 0 el area vale 0 pero el perimetro
        vale B > 0, de modo que R = 0/B = 0 esta definido y el residuo de
        Manning vale -Q, que es el signo que Brent necesita. Copiarle el
        margen a la circular seria arrastrar una defensa contra una
        singularidad que esta forma no tiene.
        """
        return 0.0, self.H

    def ancho_superficial_en_llenado(self, llenado: float) -> float:
        """El mismo B: el parametro propio ES el tirante."""
        return self.B

    def geometria_en(self, llenado: float) -> "Geometria":
        """
        `Geometria` completa (A, P, R, y) para un tirante dado.

        `llenado` y `y` valen lo mismo, y eso es correcto: el parametro propio
        de esta forma es el tirante. No se "aprovecha" para nada -- quien
        consuma un `Geometria` sigue leyendo `g.y` y `g.llenado` por su nombre.
        """
        y = llenado
        A = self.area(y)
        P = self.perimetro(y)
        return Geometria(seccion=self, llenado=y, A=A, P=P, R=A / P, y=y)

    def llenado_critico_cerrado(self, Q: float, g: float) -> Optional[float]:
        """
        y_c = (q^2/g)^(1/3), con q = Q/B. EXACTA: aqui no hay Brent.

        Sale de la condicion de energia minima Q^2*T/(g*A^3) = 1 con T = B
        constante y A = B*y: Q^2*B/(g*B^3*y^3) = 1, de donde y^3 = q^2/g. No
        es una aproximacion ni una linealizacion; es la misma ecuacion que la
        circular resuelve con Brent, despejada.

        Y NO ES SOLO ELEGANCIA: retira la clase entera de fallos de
        convergencia que `LimiteNumericoError` cubre en la circular (SIS-G-02,
        donde un Q diminuto lleva el resolutor a un theta en que el area se
        cancela). Lo que NO retira es la aritmetica, y por eso hay tres
        guardias A LA SALIDA, con la forma de MAT-D13 -- umbral MEDIDO,
        condicion en positivo y negada, mensaje que nombra al PAR culpable --.
        Las tres se midieron sobre este mismo codigo:

          1. `q ** 2` desborda para q >= 1.3407807929942597e+154 (con
             B = 2.00 m eso es Q >= 2.6815615859885194e+154). `float.__pow__`
             lanza OverflowError donde `q*q` daria `inf`.
          2. `Q/B` puede dar `inf` SIN excepcion --Q = 1e308 con B = 1e-5--, y
             entonces y_c sale `inf`: un tirante que no es un numero, y con el
             un informe entero de diagnosticos sobre algo que no lo es
             (SIS-G-01).
          3. `q^2/g` se cancela a 0.0 exacto para q <= 4.715183354107886e-162
             (el primer q que deja y_c > 0 es 4.715183354107887e-162, y da
             y_c = 1.7031839360032837e-108). Con y_c = 0 no hay velocidad
             critica que calcular.

        La cuarta --que y_c salga positivo y aun asi A = B*y_c se anule-- NO
        se guarda aqui: la atrapa la guardia de area de `M4.tirante_critico`,
        que es comun a las dos formas. Es alcanzable, y medido: con
        B = Q = 5e-324 (el denormal mas pequeño) y_c vale 0.4671363512679737 y
        A vale 0.0 exacto.

        Y HAY UNA QUINTA COSA QUE NO ES ARITMETICA, y por eso no esta en esa
        lista: el TECHO. La forma cerrada retiro, sin que nadie lo notara, el
        limite que en la circular ponia la geometria del bracket. Lo repone la
        ultima linea, y la razon la escribe la fuente, no el proyecto: ver el
        comentario junto a ella.
        """
        q = Q / self.B
        try:
            q_al_cuadrado = q ** 2  # literal-ok: el cuadrado de q en y_c = (q^2/g)^(1/3)
        except OverflowError:
            raise LimiteNumericoError(
                "Q", valor=Q, motivo=(
                    f"el par (Q = {Q!r} m3/s, B = {self.B!r} m) da un caudal "
                    f"por unidad de ancho q = Q/B = {q!r} m2/s cuyo cuadrado "
                    f"no cabe en doble precision, y sin q^2 no hay tirante "
                    f"critico que despejar. No es un caudal fuera de rango "
                    f"--'Q_m3s' solo exige ser positivo, y ponerle un techo "
                    f"seria inventar un valor de proyecto--: es un caudal "
                    f"cuyo cuadrado por unidad de ancho no es representable. "
                    f"Revisa si la celda perdio el separador decimal, si el "
                    f"caudal vino en otra unidad, o si el ancho de celda es "
                    f"el de una celda y no el del conjunto")
            ) from None
        y_c = (q_al_cuadrado / g) ** (1 / 3)  # literal-ok: exponente de la raiz cubica de (q^2/g)
        if not y_c < math.inf:
            raise LimiteNumericoError(
                "Q", valor=Q, motivo=(
                    f"el par (Q = {Q!r} m3/s, B = {self.B!r} m) desborda al "
                    f"despejar el tirante critico: q = Q/B = {q!r} m2/s y "
                    f"y_c = (q^2/g)^(1/3) = {y_c!r} m, que no es un numero "
                    f"finito. Cada dato cumple su rango por separado --el "
                    f"ancho es positivo y el caudal tambien--; lo que no cabe "
                    f"es la operacion que los combina")
            )
        if not y_c > 0:
            raise LimiteNumericoError(
                "Q", valor=Q, motivo=(
                    f"el par (Q = {Q!r} m3/s, B = {self.B!r} m) degenera: el "
                    f"caudal por unidad de ancho q = Q/B = {q!r} m2/s es tan "
                    f"pequeño que q^2/g se cancela entero en doble precision "
                    f"(ocurre desde q <= 4.715183354107886e-162) y el tirante "
                    f"critico sale {y_c!r} m. Sin tirante no hay area y sin "
                    f"area no hay velocidad critica. No es un caudal fuera de "
                    f"rango: revisa si la celda perdio digitos o si el caudal "
                    f"vino en otra unidad")
            )
        # EL TECHO, QUE LA FORMA CERRADA RETIRO SIN QUERER Y LA FUENTE SI PONE.
        # VA DESPUES DE LAS DOS GUARDIAS Y NO ANTES, y el orden importa: con
        # q = inf el `min` se tragaria el infinito --min(inf, H) = H-- y la
        # guardia de finitud no llegaria a verlo nunca. Medido al escribirlo:
        # puesto arriba, el par (Q = 1e308, B = 1e-5) devolvia 1.5 m tan
        # tranquilo en vez de lanzar `LimiteNumericoError`.
        # La circular lo tenia por geometria: su bracket es (0, 2*pi) y
        # y = (D/2)(1 - cos(theta/2)) no puede pasar de D, de modo que un Q
        # desmedido solo acerca y_c a D. Medido: `SeccionCircular(0.90)` da
        # y_c = 0.8999649945 con Q = 15 y 0.8999999823 con Q = 100. El despeje
        # no tiene ese limite: con el marco 2.00 x 1.50, Q = 15 m3/s y
        # S = 0.05 m/m -- un punto VIABLE, y_n = 0.805 m, y/H = 0.54, dentro
        # del 0.75 que admite V1 -- daba y_c = 1.7899 m, o sea un area critica
        # de 3.58 m2 sobre un barril cuya area llena es 3.00 m2. El informe
        # imprimia una seccion critica mas grande que el conducto entero, sin
        # decir nada, porque el numero era positivo y finito.
        #
        # Y NO ES UNA DECISION DEL PROYECTO: lo escribe la fuente. HDS-5 3a
        # ed., num. 3.3.3 «Outlet Control», pag. impresa 3.24 (PDF 106), en la
        # misma lista de vinetas que la condicion de h_o, dice que el tirante
        # critico no puede exceder D -- la altura interior del barril --. Las
        # cartas del Apendice C lo acotan igual. La frase no se transcribe
        # aqui: el registro no tiene todavia su `Verbatim`, y una segunda
        # transcripcion a mano es lo que CLAUDE.md prohibe. Queda anotado
        # como C4-5 en §16.8.
        y_c = min(y_c, self.H)
        return y_c


@dataclass(frozen=True)
class Geometria:
    """
    La seccion resuelta a un llenado concreto: A, P, R y el tirante.

    LLEVA LA `Seccion`, NO EL DIAMETRO. Hasta C1 llevaba `D` y `theta`
    sueltos, y con ellos la forma circular cableada en el tipo que atraviesa
    todo el motor hidraulico. `llenado` es el parametro propio de la seccion
    -- theta en la circular -- y las magnitudes derivadas se le piden a ella.

    `y_sobre_D` CONSERVA EL NOMBRE aunque ya no haya un diametro: lo consumen
    los tests del motor y es el nombre con que el numero viaja al reporte.
    """

    seccion: Seccion  # la forma del barril
    llenado: float    # parametro propio de la seccion (theta en la circular)
    A: float          # m2 - area hidraulica
    P: float          # m  - perimetro mojado
    R: float          # m  - radio hidraulico
    y: float          # m  - tirante

    @property
    def y_sobre_D(self) -> float:
        """Relacion de llenado. V1 exige y/D <= el maximo adoptado (0.75 por defecto)."""
        return self.y / self.seccion.altura

    @property
    def T(self) -> float:
        """Ancho superficial. Lo calcula la seccion desde su propio parametro."""
        return self.seccion.ancho_superficial_en_llenado(self.llenado)


def exigir_seccion_coherente(material: "Material", seccion: "Seccion") -> None:
    """
    Que la `Seccion` que llega sea de la FORMA que el material declara.

    LA ABRIO LA AUDITORIA ADVERSARIAL DE C7, y su medicion es la razon de que
    esto exista:

        cobertura_minima_aashto(material=catalogo(CONCRETO_REFORZADO),
                                seccion=SeccionRectangular(B=3.00, H=1.50))
        -> 0.4125     # Bc/8 de la fila «Reinforced Concrete PIPE», sobre un
                      # RECTANGULO

    O sea el defecto que C7 declara no cometer -- aplicar una fila rotulada
    «Pipe» a algo que no lo es --, alcanzable en tres lineas. Ocurre porque
    `M7.cobertura_minima_aashto` y `M8._elemento_de` bifurcan por
    `material.forma` mientras la geometria la pone la `Seccion`, y nada ataba
    las dos cosas. En produccion el par siempre es coherente --la seccion sale
    del catalogo del material-- de modo que ningun numero publicado estaba
    mal; lo que estaba mal era la palabra «POR CONSTRUCCION» con que los
    docstrings de C7 describian esa correccion. Con esta guardia lo es.

    Va aqui y no en el `Protocol`: la forma no es una propiedad que la seccion
    necesite conocer de si misma -- todo el diseño de `Seccion` consiste en
    que el calculo NO pregunte de que forma es --, y anadirsela para poder
    compararla desharia justamente eso. Lo que hace falta es cruzar los dos
    objetos en la puerta por la que entran juntos, que es esto.
    """
    rectangular = isinstance(seccion, SeccionRectangular)
    if (material.forma is FormaSeccion.RECTANGULAR) is not rectangular:
        raise DatoInvalidoError(
            campo="seccion",
            valor=type(seccion).__name__,
            motivo=(f"el material declara forma {material.forma.value} y la "
                    f"seccion recibida es {type(seccion).__name__}: el par no "
                    "es coherente. La forma decide que fila de tabla aplica, "
                    "de modo que con el par cruzado se le aplicaria a esta "
                    "seccion la fila de la otra"),
        )
