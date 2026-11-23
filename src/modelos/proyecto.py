"""
src/modelos/proyecto.py
=======================
Clasificacion y periodo de retorno, traza del diseno, modos de resolucion de las variables de entrada y barrido.

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

from src.modelos.errores import DatoFaltanteError
from src.modelos.base import ControlGobernante, Denominacion, RegimenBarril
from src.modelos.memoria import Verificacion

if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.base import CategoriaTR, Familia, PuntoCritico
    from src.modelos.conducto import Material, Seccion
    from src.modelos.hidraulica import ResultadoHidraulico
    from src.modelos.memoria import PasoDeMemoria

# ===========================================================================
# Clasificacion y periodo de retorno (Fase 2, salida de M1)
# ===========================================================================

@dataclass(frozen=True)
class PeriodoRetorno:
    """
    TR de diseno de un punto y la fila de la Tabla N 02 que lo sustenta
    (Sec. 2.2). El TR no se transporta como un numero suelto: sin la fila que
    lo origina, la memoria no puede defender por que son 71 anios y no 35.

    `anios` es el valor de la columna "TR de diseno" de la tabla DERIVADA de
    la Sec. 2.2 de la hoja de ruta -- la Tabla N 02 del Manual no trae esa
    columna: trae R y n, y el TR se calcula --, redondeado al anio; `exacto`
    conserva el resultado sin redondear.

    `procede` es False en dos situaciones, y en ambas `anios` es None:
      - Familia C: su caudal es el de diseno del canal (ANA / Junta), no un
        caudal hidrologico con periodo de retorno propio (Sec. 2.3).
      - Luz >= 6.0 m: el punto es un puente y esta fuera del alcance (Sec. 2.1).
    """

    procede: bool
    categoria: Optional[CategoriaTR]
    R: Optional[float]                    # riesgo admisible de falla
    n: Optional[int]                      # vida util, anios
    exacto: Optional[float]               # TR sin redondear
    anios: Optional[int]                  # TR de diseno, calculado de la fila
                                          # de la Tabla N 02 (tabla de la v8 §2.2)
    numeral: str
    fundamento: str                       # por que esta fila y no la otra
    id_punto: Optional[str] = None
    # El paso de memoria del TR (§4.4). `None` cuando `procede` es False: no
    # hay TR que fundar, y el motivo lo lleva `fundamento`.
    paso: Optional["PasoDeMemoria"] = None

    def exigir_anios(self) -> int:
        """
        Devuelve el TR o lanza: un TR ausente nunca se sustituye por uno
        plausible.

        HOY NO LA LLAMA NADIE, y esa es la decision (SIS-B-08): ver
        `docs/decisiones_diferidas.md`, ficha SIS-B-08. El docstring anterior
        decia «Unico acceso permitido cuando el modulo que llama NECESITA el
        numero», que es una condicion que no se cumple en ningun sitio --- la
        misma forma de prometer un consumidor que este archivo ya desterro al
        cerrar SIS-B-02 en `ControlEntrada`.

        Los CINCO accesos de produccion al TR --- `M11._tabla_clasificacion`,
        `M11.fila_resumen`, `M11._fila_resumen_csv`, `cli._clasificacion_json`
        y `cli._lineas_punto` --- leen `.anios` y tratan el `None`
        explicitamente: lo imprimen como ausente o lo propagan. Ninguno
        necesita el entero, porque el paso que si lo necesitaria --- «Tc.py +
        IDF con el TR de Fase 2», Sec. 1.1 --- ocurre fuera de este programa y
        Q entra por columna del CSV.

        Se conserva porque es la unica sentencia EJECUTABLE del invariante,
        y `anios` esta anotado `Optional[int]`: sin ella, el consumidor que
        llegue escribira `tr.anios or 35`, que es el default silencioso que
        CLAUDE.md llama el peor error posible.

        LIMITE CONOCIDO, declarado en vez de disimulado. Hay dos motivos por
        los que `anios` es None y esta guardia solo distingue bien uno:
        Familia C (el caudal es el de diseno del canal: falta el dato, y
        `DatoFaltanteError('Q_m3s')` es correcto) y punto fuera de alcance
        (es un puente: no falta nada, y lo que corresponde es
        `DisenoNoFactibleError`, como en `M1_clasificacion.exigir_alcance`).
        `PeriodoRetorno` no lleva hoy con que separarlos sin oler el texto de
        `fundamento`, y el orden que el propio M1 documenta en su bloque de
        Uso --- `exigir_alcance(...)` ANTES de leer el TR --- deja la segunda
        rama fuera del camino. Cerrarlo del todo pide un discriminante en el
        objeto, no una guardia mas: queda anotado en el registro.
        """
        if self.anios is None:
            raise DatoFaltanteError(
                "Q_m3s", id_punto=self.id_punto,
                detalle=f"este punto no tiene TR de la Tabla N 02: {self.fundamento}",
            )
        return self.anios


@dataclass(frozen=True)
class PerfilFamilia:
    """
    Lo que la familia de Sec. 2.3 implica para el resto del calculo: de donde
    sale su caudal, si la familia ya fija la fila de la Tabla N 02, que campos
    del CSV necesita y con que verificaciones se acepta.

    `verificaciones_aceptacion` es None cuando la hoja de ruta no declara un
    conjunto propio para esa familia. None significa "no declarado", no
    "ninguna": la tabla de la Fase 5 sigue aplicando punto por punto.

    NADIE DESPACHA SOBRE ESTE CAMPO, Y ES DELIBERADO (SIS-B-13)
    ----------------------------------------------------------
    Lo escribe solo `M1_clasificacion.PERFILES` y lo leen solo dos asserts de
    `tests/test_M1_clasificacion.py`. Cero lectores de produccion: `M5.verificar`
    y el cierre `verificar` de `cli.py` corren la Fase 5 ENTERA sobre todo
    punto, sin mirar la familia. La razon de que asi sea, dicha aqui porque es
    lo que faltaba escrito: si algun modulo despachara sobre esta tupla, la
    frase de la Sec. 2.3 se convertiria en un FILTRO y la Familia A se quedaria
    sin V3 (velocidad maxima), V6, V7 (flotacion), V8 y V9 --- que la tabla de
    la Fase 5 no exime por familia --- y las Familias B y C se quedarian sin
    conjunto ninguno. Es la lectura no conservadora que este campo existe para
    NO habilitar. Se conserva porque es la unica huella en el codigo de una
    frase de la fuente de verdad, y el `None` carga una distincion que se
    perderia al borrarlo.

    DEFECTO CONTRA LA HOJA DE RUTA, que es la que hay que corregir (regla 7).
    La Sec. 2.3 escribe «**A — Alcantarillas de paso.** Q hidrologico propio.
    TR 71 o 35 anios. Aceptacion: V1 + V2 + V4 + V5.» --- un conjunto SOLO
    para la Familia A y en una forma que se lee exhaustiva --- mientras la
    Fase 5 tabula sus verificaciones sin calificarlas por familia, y para B y
    C no declara nada. La hoja no dice si V1+V2+V4+V5 es «el minimo que A debe
    pasar» o «las unicas que a A se le exigen». La fuente primaria no puede
    dirimirlo: la taxonomia A/B/C y las etiquetas V1..V9 son de la hoja, no
    del MTC (`M1.NUMERAL_FAMILIA = "Sec. 2.3"`, «sin numeral MTC propio»).
    MIENTRAS NO SE CORRIJA, LA HOJA SIGUE MAL: quien la lea sin leer el codigo
    disenara una alcantarilla de Familia A creyendo que no se le exige V7
    (flotacion) ni V9 (disponibilidad de diametro). El codigo toma entretanto
    la lectura conservadora --- aplicarlas todas ---, que es la unica que no
    puede dejar un punto sin verificar.
    """

    familia: Familia
    nombre: str
    origen_del_caudal: str
    categoria_tr: Optional[CategoriaTR]        # None: la familia no la fija
    campos_requeridos: Tuple[str, ...]         # campos de PuntoCritico
    verificaciones_aceptacion: Optional[Tuple[str, ...]]
    notas: Tuple[str, ...]
    numeral: str


@dataclass(frozen=True)
class Clasificacion:
    """
    Salida de M1 para un punto: denominacion por luz (Sec. 2.1), perfil de
    familia (Sec. 2.3) y periodo de retorno (Sec. 2.2).

    `datos_pendientes` son los campos que la familia necesita y la fila trajo
    vacios por depender de un tablero externo. Como en M0, quien decide si el
    punto se puede calcular sin ellos es el modulo que los necesite.
    """

    punto: PuntoCritico
    luz_m: float
    denominacion: Denominacion
    verificacion_luz: Verificacion
    perfil: PerfilFamilia
    periodo_retorno: PeriodoRetorno
    datos_pendientes: Tuple[str, ...] = ()

    @property
    def en_alcance(self) -> bool:
        """False si la luz lo hace puente: Manual de Puentes, otro script."""
        return self.denominacion is Denominacion.ALCANTARILLA


@dataclass(frozen=True)
class GobiernoPorReceptor:
    """
    --- VE-3.13 (decision 8 del dueño) --- El diametro adoptado lo goberno
    el NIVEL DEL RECEPTOR, no el caudal de diseño: con
    'borde_libre_bajo_tw_ahogante' = «no_cumple», V1 descarto escalones que
    conservaban el borde libre con su tirante propio y que nada mas de la
    Fase 5 descartaba. No cambia ningun diametro; dice tres cosas:

      (a) que lo goberno el receptor (los escalones que descarto, en orden);
      (b) el diametro que bastaria por la hidraulica sola: el que la lectura
          «aviso» adoptaria, EVALUADO de verdad con esa lectura (MD vuelve a
          pasar la Fase 5 por los escalones descartados, sin publicar nada
          de esa pasada salvo cual cerro);
      (c) el descenso del TW --o la subida de la solera de salida-- con el
          que ese diametro cumpliria V1: TW - (y/D)max · D_h. Es una
          ALTERNATIVA que el proyectista evalua, no un remedio verificado:
          las demas fases no se vuelven a correr con esa cota (cambian la
          pendiente, la longitud, V4 y el cabezal).

    Lo emite MD (`MD._gobierno_por_receptor`), con su `PasoDeMemoria`; M11,
    la CLI, el JSON y la pestaña 3 solo lo imprimen (`aviso` es el texto del
    aviso del punto).
    """

    material_adoptado: str
    seccion_adoptada: "Seccion"
    material_hidraulico: str
    seccion_hidraulica: "Seccion"
    escalones_descartados: Tuple[str, ...]   # etiquetas, en orden
    tw_m: float                              # tirante del receptor sobre la solera de salida
    y_sobre_D_max: float                     # el umbral adoptado de V1
    tw_admisible_m: float                    # (y/D)max · D_h
    descenso_tw_m: float                     # tw_m - tw_admisible_m
    paso: "PasoDeMemoria"
    aviso: str


@dataclass(frozen=True)
class ResultadoPunto:
    """
    Resultado completo de un punto critico: la combinacion elegida y el
    expediente de verificaciones que la sostiene.

    `aceptado` y `punto` son los dos campos siempre presentes. Los demas solo
    existen para puntos que llegaron a dimensionarse:

        aceptado=True   material, D, resultado_hidraulico y verificaciones
                        estan completos. motivo_rechazo es None.
        aceptado=False  material, D, resultado_hidraulico y verificaciones
                        son None / tupla vacia. motivo_rechazo explica por
                        que no hubo solucion. M11 los lista aparte.

    Esta separacion permite a `disenar_lote` devolver la lista completa del
    expediente -- puntos resueltos y fallidos mezclados en el orden del CSV --
    sin perder ningun punto ni forzar un aborte.
    """

    punto: PuntoCritico
    aceptado: bool
    material: Optional[Material] = None
    # LA SECCION ADOPTADA, Y YA NO CONVIVE CON UN ESCALAR `D`.
    #
    # Hasta C7 este tipo llevaba ademas `D: Optional[float]`, "el diametro
    # adoptado", que en un marco valia la ALTURA. C7 añadio la seccion sin
    # tocarlo --- para que la Fase 7 pudiera ser ciega a la forma --- y dejo
    # escrito que retirarlo era de C8, "con sus consumidores delante". C8 lo
    # retira: eran once, y el peor era el titular de la memoria, que imprimia
    # «Diametro adoptado D = 0.900 m» sobre un marco de 1.20 x 0.90 m.
    #
    # POR QUE NO BASTABA CON LA INVARIANTE. C7 cerro la divergencia entre los
    # dos campos con un `__post_init__` de doble sentido, y era correcto
    # mientras convivieran. Pero un `D` coherente con la seccion sigue siendo
    # una PERDIDA DE INFORMACION: de «0.90» no se recupera si la luz eran
    # 1.20 o 2.00 m, y todo consumidor que imprima ese escalar esta publicando
    # media geometria bajo un nombre que en un cajon no significa nada.
    seccion: Optional[Seccion] = None
    resultado_hidraulico: Optional[ResultadoHidraulico] = None
    verificaciones: Tuple[Verificacion, ...] = ()
    motivo_rechazo: Optional[str] = None
    # --- VE-3.13 (decision 8 del dueño) --- Cuando el diametro adoptado lo
    # goberno el NIVEL DEL RECEPTOR y no el caudal (V1 descarto escalones
    # SOLO por el TW bajo «no_cumple»): el diametro que bastaria por la
    # hidraulica sola y la alternativa de cota. None en los demas puntos.
    gobierno_por_receptor: Optional["GobiernoPorReceptor"] = None

    @property
    def y_sobre_D(self) -> Optional[float]:
        """
        Relacion de llenado del punto dimensionado, `y_normal / altura`, o
        None si el punto no llego a dimensionarse.

        CONSERVA EL NOMBRE AUNQUE YA NO HAYA UN `D`, y se declara aqui por lo
        mismo que `Geometria.y_sobre_D` lo declara: "y/D" es como la Sec. 4.1
        y el HDS-5 nombran la relacion de llenado, y renombrarlo a
        `y_sobre_altura` obligaria a explicar en cada sitio que se trata del
        mismo numero de la fuente. La `D` del nombre es la de la FUENTE; el
        denominador es `seccion.altura`, que en una circular ES el diametro y
        en un marco es la H de la celda.

        Vive aqui, en el tipo que fluye entre modulos, y no en la capa de
        reporte: M11 la calculaba inline en dos sitios (la tabla del punto y
        la fila del cuadro resumen), contra su propio docstring de modulo
        ("sin calcular nada nuevo") y contra la regla de arquitectura. Es el
        mismo numero que V1 verifica en `M5_verificaciones.v1_borde_libre` y
        el mismo que `Geometria.y_sobre_D` define para la seccion; escrito
        una vez, no puede divergir entre la memoria y la verificacion.

        Y DESDE EXT-3 SIGUE EL REGIMEN DEL BARRIL, como V1: `y_normal /
        altura` solo bajo control de entrada; 1 a barril lleno; y bajo
        control de salida con el barril parcialmente lleno, DESDE E-A, el
        tirante maximo del perfil de la lamina (`perfil.y_max_m`), que es el
        que V1 compara. Hasta E-A salia None --celda vacia declarada-- porque
        V1 quedaba pendiente y publicar un y/D del flujo uniforme seria la
        divergencia memoria/pipeline de SIS-A-07 en otra celda; None sigue
        siendo la respuesta si el resultado no trae perfil.
        """
        if self.resultado_hidraulico is None or self.seccion is None:
            return None
        h = self.resultado_hidraulico
        altura = self.seccion.altura
        # EL MISMO TIRANTE QUE V1 COMPARA (EXT-3, auditoria adversarial; E-A):
        # el del REGIMEN del barril y no el normal a secas. A barril LLENO el
        # tirante es la altura entera; bajo control de SALIDA con el barril
        # parcialmente lleno es el maximo del perfil de la lamina; solo bajo
        # control de ENTRADA vale y_normal.
        # --- T-2 --- y sin tirante normal (barril horizontal, S = 0) el
        # tirante es el del perfil tambien cuando gobierna la entrada: es lo
        # que V1 compara ahi (`M5._regimen_de_v1_v2`).
        if h.regimen_barril is RegimenBarril.LLENO:
            y = altura
        elif (h.control_gobernante is ControlGobernante.SALIDA
              or h.sin_tirante_normal):
            if h.perfil is None:
                return None
            y = h.perfil.y_max_m
        else:
            y = h.y_normal
        return y / altura

    @property
    def verificaciones_incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las que M11 debe destacar en la memoria del punto."""
        return tuple(v for v in self.verificaciones if not v.cumple)

    @property
    def coherente(self) -> bool:
        """
        True si `aceptado` concuerda con las verificaciones y con el motivo de
        rechazo. Sirve de guarda en los tests de M5 y M7.
        """
        if self.aceptado:
            return not self.verificaciones_incumplidas and self.motivo_rechazo is None
        return bool(self.motivo_rechazo)


# ===========================================================================
# Traza del diseno (bucle de MD; entregable 1 de la Fase 11)
# ===========================================================================

@dataclass(frozen=True)
class EscalonSinCabida:
    """
    --- T11-03 --- El escalon del catalogo cuya clave fisica NO CABE bajo la
    subrasante: la cota de clave queda a nivel de la subrasante o por encima
    y no hay relleno que pesar (V7) ni con que entrar a la norma de producto
    (Fase 8). Lo arma `MD.disenar_material` y viaja en `PasoDiseno.sin_cabida`.

    Existe porque ese hecho salia como `DatoInvalidoError` sobre
    'cota_subrasante' --un dato que nadie toco: lo que cambio fue la seccion
    que el bucle probaba-- y el punto como «no factible» sin su motivo
    (hallazgo H4 de la auditoria de T-11). Es GEOMETRIA: las dos cotas son el
    par culpable, y el motivo las nombra a las dos.

    `delta_rasante_m` es el del tamizado de Sec. 7.A para ESTE escalon
    (`M7.tamizado_rasante`), y solo se da cuando es geometria pura: el
    escalon cumple todo lo que la Fase 5 le evaluo y gobierna la condicion de
    recubrimiento, de modo que el numero no depende del HW. Es COTA INFERIOR
    para este escalon, no el remedio verificado del punto. `nota` dice la
    aritmetica cuando hay delta y por que no lo hay cuando es None.
    """

    cota_clave: float                     # msnm - cota entrada + altura + pared
    cota_subrasante: float                # msnm - la del CSV (Sec. 1.2)
    delta_rasante_m: Optional[float] = None
    nota: str = ""
    # --- VE-6 (item 34, H8 de los ensayos del conducto) --- True cuando la
    # clave SI cabe bajo la subrasante pero no deja la COBERTURA MINIMA bajo
    # la rasante (G1 de 7.A, evaluada dentro del bucle sobre el escalon que
    # cumple toda la Fase 5). El delta es entonces el de G1 para ese escalon.
    por_cobertura: bool = False

    @property
    def exceso_m(self) -> float:
        """Cuanto queda la clave POR ENCIMA de la subrasante, m (>= -tol)."""
        return self.cota_clave - self.cota_subrasante


@dataclass(frozen=True)
class PasoDiseno:
    """
    Un escalon del bucle de MD: el par (material, D) que se probo y como
    termino.

    Existe porque la Fase 11 exige publicar las ITERACIONES del diseño
    (entregable 1) y `ResultadoPunto` solo conserva la combinacion ganadora:
    con ella sola la memoria muestra la seccion adoptada pero no puede
    defender por que se descarto la anterior, que es justamente lo que un
    revisor pregunta. No la produce ningun calculo nuevo -- es lo que MD ya
    evaluaba y descartaba en silencio.

    `verificaciones` viene vacia cuando el escalon ni siquiera transporto el
    caudal en flujo libre (M3 no hallo tirante normal): la Fase 5 no llego a
    correr y `motivo` lo dice. En el escalon aceptado, `motivo` es "".
    """

    material: str                         # Material.nombre
    # LA SECCION PROBADA, y no el escalar `D` que este campo tenia hasta C8.
    # Un escalon del catalogo del cajon es un par (B, H): con solo la altura,
    # la tabla de iteraciones imprimia «0.90» para tres marcos de luz
    # distinta y el revisor no podia saber cual se descarto. Ademas obligaba a
    # M11 a llamar «D» a lo que en un marco no es un diametro.
    seccion: "Seccion"
    aceptado: bool
    motivo: str                           # por que se descarto; "" si aceptado
    verificaciones: Tuple[Verificacion, ...] = ()
    # EL RESULTADO HIDRAULICO DEL ESCALON, con su traza (§4.4).
    #
    # Viaja aqui, y no solo en el `ResultadoPunto` ganador, por la MISMA razon
    # que existe `M11.bloque_umbrales`: en este expediente ningun punto llega
    # a dimensionarse --- V5 se detiene siempre en `ancho_derecho_via_m`, que
    # ningun tablero aporta todavia --- y `ResultadoPunto.resultado_hidraulico`
    # es None en los cuatro puntos. Sin este campo, el desarrollo hidraulico
    # que M3 y M4 SI calcularon no llegaria nunca al revisor, que es
    # literalmente la forma de NOR-MEM-01: cierto sobre el codigo y falso
    # sobre el producto.
    #
    # None cuando el escalon ni siquiera transporto el caudal en flujo libre
    # (M3 no hallo tirante normal) o cuando revento antes de resolver M4.
    resultado_hidraulico: Optional["ResultadoHidraulico"] = None
    # --- T11-03 --- Relleno solo en el escalon cuya clave no cabe bajo la
    # subrasante (`EscalonSinCabida`): con el termina la progresion del
    # material, descartado POR RASANTE. None en todos los demas.
    sin_cabida: Optional[EscalonSinCabida] = None

    @property
    def incumplidas(self) -> Tuple[Verificacion, ...]:
        """Las verificaciones que hicieron descartar este escalon."""
        return tuple(v for v in self.verificaciones if not v.cumple)


# ===========================================================================
# Modo de resolucion de una variable de entrada (Sec. 4.3 del plan v12)
# ===========================================================================
# Cada variable de entrada declara COMO SE RESUELVE. Eso es lo que le dice a
# la GUI que ventana abrir y a M11 que imprimir, y es informacion que hoy no
# existe en ninguna parte: el usuario ve una sola cosa -- "un dato que hay que
# llenar" -- donde el repositorio tiene cuatro poblaciones separadas (las
# columnas del CSV, los datos externos del JSON, los datos de sitio de
# corredor y los criterios adoptados)
# y seis maneras distintas de llegar al numero.
#
# LA SEMANTICA ES EL TIPO, igual que en `normativa/esquema.py` §7. No hay un
# campo `modo: str` que alguien pueda escribir mal: el modo se LEE del tipo
# del objeto `resolucion` (`modo_de()`), de forma que declarar una resolucion
# y declarar un modo son el mismo acto y no pueden divergir.
#
# COMO SE ELIGE EL MODO. La escalera se recorre de arriba abajo y se para en
# el primer peldaño que aplica; esta escrita aqui para que la clasificacion
# de las 83 variables sea reproducible y no dependa del gusto de quien la
# hizo:
#
#   1. El valor es una fila, una columna o una regla de lectura de una tabla
#      normativa TRANSCRITA EN EL REGISTRO   ->  DeTabla
#   2. Es un numero que una fuente acota con un piso, un techo o un
#      intervalo escritos por ella                ->  EnRango
#   3. El programa lo calcula desde otras variables ya declaradas y el
#      usuario no puede editarlo                  ->  Derivada
#   4. Sale de un catalogo o de la disponibilidad del mercado, y NO de una
#      norma                                      ->  DeCatalogo
#   5. Lo DETERMINA un procedimiento real aplicado a este sitio -- ensayo,
#      medicion de campo, lectura de mapa o de plano, estudio de un tercero
#      -- y por eso se defiende con trazabilidad y no con un rango de
#      sensibilidad                               ->  DeEnsayo
#   6. En cualquier otro caso                     ->  Libre
#
# ELEGIR (peldaño 6) Y DETERMINAR (peldaño 5) NO SON LO MISMO, y es lo que
# separa `Libre` de `DeEnsayo`: un metodo de analisis lo elige el
# proyectista aunque salga del mismo EMS del que sale la capacidad portante.
# Por eso `metodo_estabilidad_global` es `Libre` y `capacidad_portante_adm`
# es `DeEnsayo`.
#
# `DeEnsayo` cubre TODA determinacion por procedimiento, no solo el ensayo de
# laboratorio: es la misma extension que CLAUDE.md le da a la etiqueta [S]
# ("mapa, ensayo, medicion de campo"). Se llama asi porque asi lo nombra la
# Sec. 4.3 del plan, y la ventana que abre es la misma en los tres casos:
# campo mas TRAZABILIDAD OBLIGATORIA.


class ModoDeResolucion(str, Enum):
    """Los seis modos de la Sec. 4.3. Familia cerrada."""
    LIBRE = "libre"
    DE_TABLA = "de_tabla"
    EN_RANGO = "en_rango"
    DERIVADA = "derivada"
    DE_ENSAYO = "de_ensayo"
    DE_CATALOGO = "de_catalogo"


@dataclass(frozen=True)
class Libre:
    """
    Campo con su dominio fisico. Ninguna tabla, ningun rango de fuente y
    ninguna medicion lo determinan: el numero lo pone quien firma.

    `opciones` es para el conjunto cerrado de valores admisibles cuando la
    variable no es numerica (la Familia de un punto). En un criterio NO se
    usa: alli el conjunto ya vive en `Criterio.sensibilidad`, y repetirlo
    aqui crearia dos listas que pueden divergir.

    `tabla_pendiente` es la lista de trabajo que este censo produce: nombra
    la tabla de la fuente que convertiria esta variable en `DeTabla` el dia
    que se transcriba al registro. No es una excusa, es un pendiente con
    nombre.
    """
    que_lo_fija: str
    dominio: str = ""
    opciones: Tuple[str, ...] = ()
    tabla_pendiente: str = ""


@dataclass(frozen=True)
class DeTabla:
    """
    El valor es una fila, una columna, o la regla con que se lee una tabla
    del registro. La ventana MUESTRA LA TABLA ENTERA -- con su numeral, su
    pagina, sus notas y sus condiciones -- y el usuario elige sobre ella.

    `tablas` es una tupla porque hay elecciones que se hacen mirando dos: la
    de estribos y la de muros de AASHTO 3.11.6.4 se leen juntas o no se
    entiende ninguna de las dos.

    `laguna` se llena cuando lo que se elige NO es una fila sino una REGLA DE
    LECTURA que la tabla no resuelve. Es la diferencia entre "elegi la fila
    de 10 ft" y "elegi que hacer con un muro de 4 ft, que la tabla no
    tabula": la memoria tiene que poder decir cual de las dos cosas paso.

    `elegido_por` dice que OTRA variable elige la fila cuando esta transcribe
    la tabla completa en vez de elegir dentro de ella.
    """
    tablas: Tuple[str, ...]
    que_elige: str
    fila_id: Optional[str] = None
    columna_id: Optional[str] = None
    elegido_por: Optional[str] = None
    laguna: str = ""


@dataclass(frozen=True)
class EnRango:
    """
    El valor tiene que caer dentro de un rango que una fuente escribe.

    NO COPIA EL RANGO: lo referencia por (tabla, fila, columna) del registro,
    donde vive como `IntervaloAdmisible`, `TechoUnico`, `PisoUnico`,
    `ConjuntoDeMaximos` o `BandaDeInterpolacion`. Copiarlo aqui pondria los
    numeros de la norma fuera de su unico sitio y, peor, dejaria que la
    ventana pintara como "minimo" el primero de dos maximos (NOR-HID-04),
    que es exactamente el error que el tipo del registro existe para impedir.
    """
    tabla_id: str
    fila_id: str
    columna_id: str
    que_acota: str


@dataclass(frozen=True)
class Derivada:
    """
    No editable: la calcula el programa desde otras variables ya declaradas.
    La ventana muestra DE QUE se deriva y la memoria escribe la regla con su
    numeral.
    """
    de: Tuple[str, ...]
    regla: str


@dataclass(frozen=True)
class DeEnsayo:
    """
    La determina un procedimiento real aplicado a este sitio. La ventana pide
    el valor Y LA TRAZABILIDAD, y la memoria escribe la trazabilidad -- nunca
    una sensibilidad: no hay rango que elegir, hay una lectura que reproducir.
    """
    ensayo: str
    trazabilidad_exigida: str


@dataclass(frozen=True)
class DeCatalogo:
    """
    Igual que `DeTabla` pero ROTULADO COMO CATALOGO, no como norma.

    Existe por `NOR-PRO-01` y `NOR-PRO-02`: los topes de diametro estaban
    atribuidos a AASHTO M170 y ASTM A760, que tabulan hasta 3600 mm.
    Mostrarlos en una ventana rotulada "norma" seria crear una cita falsa
    nueva, y por eso `advertencia` es obligatoria y dice que norma NO lo
    sostiene.
    """
    catalogo_id: str
    que_elige: str
    advertencia: str


Resolucion = Union[Libre, DeTabla, EnRango, Derivada, DeEnsayo, DeCatalogo]

_MODO_DE_TIPO: Dict[type, ModoDeResolucion] = {
    Libre: ModoDeResolucion.LIBRE,
    DeTabla: ModoDeResolucion.DE_TABLA,
    EnRango: ModoDeResolucion.EN_RANGO,
    Derivada: ModoDeResolucion.DERIVADA,
    DeEnsayo: ModoDeResolucion.DE_ENSAYO,
    DeCatalogo: ModoDeResolucion.DE_CATALOGO,
}


def modo_de(resolucion: Resolucion) -> ModoDeResolucion:
    """
    El modo de una resolucion. Es una lectura del TIPO, no de un campo: una
    variable no puede quedarse sin modo ni declarar uno que no corresponda a
    como se resuelve.
    """
    try:
        return _MODO_DE_TIPO[type(resolucion)]
    except KeyError:
        raise TypeError(
            f"{resolucion!r} no es una resolucion de la familia cerrada de "
            f"la Sec. 4.3: {tuple(t.__name__ for t in _MODO_DE_TIPO)}"
        ) from None


class Poblacion(str, Enum):
    """
    Las CINCO poblaciones (cuatro hasta VE-5) que el repositorio mantiene
    separadas y que el usuario ve como una sola cosa -- "los datos que hay que llenar".

    Estan separadas por buenas razones (una es del CSV y varia punto a punto,
    otra es del corredor, la tercera es lo que el proyectista decidio donde la
    norma calla, la cuarta entra por bandera o por el JSON de
    `--datos-externos` sin ser columna) y esas razones no se tocan. Lo que
    faltaba era la vista unica: sin ella, la GUI tiene pestañas que no se
    pueden comparar y la memoria bloques que no suman.

    `DATO_EXTERNO` llego en EXT-5 (EXT-G-03): las seis claves de
    `servicio.CLAVES_EXTERNAS` que no son columna, ni dato de sitio, ni criterio
    no estaban en ningun censo, y la ayuda de la GUI las mostraba como «sin
    ficha». Se censan como poblacion propia y no como columnas porque no lo
    son: no viven en el CSV y no varian necesariamente punto a punto.

    `DATO_EXTERNO_OPCIONAL` llego en VE-5 (ficha T4-09) y es la QUINTA: los
    seis ensayos de durabilidad que entran por el mismo JSON
    (`servicio.CLAVES_DE_DURABILIDAD`) y que NO son de `CLAVES_EXTERNAS`
    porque ninguna etapa los exige --- sin ellos la matriz no actua y la
    memoria lo dice ---. Censados como `DATO_EXTERNO`, el pre-vuelo los habria
    leido como datos que faltan; fuera del censo, la ayuda del JSON no los
    nombraba. Poblacion propia: estan en el censo y nadie los cuenta como
    falta.
    """
    COLUMNA_CSV = "columna_csv"
    DATO_SITIO = "dato_sitio"
    CRITERIO = "criterio"
    DATO_EXTERNO = "dato_externo"
    DATO_EXTERNO_OPCIONAL = "dato_externo_opcional"


@dataclass(frozen=True)
class VariableDeEntrada:
    """
    Una variable que el expediente tiene que traer, con todo lo que la GUI
    necesita para pintarla y M11 para imprimirla.

    `criterio_destino` es el criterio [A] que RECIBE la eleccion cuando la
    variable la alimenta sin ser ella misma un criterio: el CBR de la fila
    entra en `resguardo_HW_subrasante`, la cota TW en `TW_receptor`. Para una
    variable que ES un criterio, es su propia clave.

    `dominio` nombra el limite de `dominios.py` que acota la celda, POR
    NOMBRE y no por valor: el dominio fisico no es normativo -- fuera de el
    la celda esta mal llenada -- y la ventana tiene que rotularlo asi
    (§4.2 del plan).
    """
    clave: str
    concepto: str
    unidad: str
    poblacion: Poblacion
    resolucion: Resolucion
    fase: str
    consumido_por: Tuple[str, ...] = ()
    criterio_destino: Optional[str] = None
    dominio: Optional[str] = None
    nota: str = ""

    @property
    def modo(self) -> ModoDeResolucion:
        """El modo de la Sec. 4.3, leido del tipo de `resolucion`."""
        return modo_de(self.resolucion)


@dataclass(frozen=True)
class VacioAdmitido:
    """
    Un grupo de columnas del CSV que pueden ir VACIAS, con quien debe el dato.

    Existe porque «celda vacia» tiene dos lecturas opuestas que desde fuera no
    se distinguen: falta un dato que el proyectista tenia que poner, o espera
    a un tablero que todavia no respondio. M0 lo sabia --- lo declaraba en
    cinco tuplas privadas, cada una con su razon escrita al lado --- y nadie
    mas lo podia leer, de modo que el proyectista veia una columna vacia en su
    CSV y creia que le faltaba un dato.

    `familias` vacia significa TODA FAMILIA. Cuando lleva familias, el vacio
    solo se admite en esas: `Q_m3s` va vacia en un cruce de canal y es
    obligatoria en una alcantarilla de paso, y esa es la distincion que la
    ayuda de la ventana tiene que poder decir.

    `marca_pendiente` separa el vacio que ESPERA A ALGUIEN del que no: una
    `cota_fondo_entrada` vacia no espera a nadie porque el proyecto tiene una
    regla declarada para ese caso, y meterla entre los pendientes pintaria un
    pendiente que no existe. Es el mismo matiz que `pendientes_externos`.
    """

    columnas: Tuple[str, ...]
    quien_lo_debe: str
    familias: Tuple[Familia, ...] = ()
    marca_pendiente: bool = True

    def alcanza_a(self, familia: Optional[Familia]) -> bool:
        """
        Si este vacio se admite para esa familia.

        `familia=None` pregunta por el grupo entero, sin fijar una: es lo que
        necesita una ayuda que se abre ANTES de que haya CSV cargado.
        """
        if not self.familias:
            return True
        return familia is None or familia in self.familias


@dataclass(frozen=True)
class CabeceraCSV:
    """
    Lo que se puede saber de un CSV leyendo SOLO su cabecera y contando las
    celdas vacias: lo que el anticipo de la pestana 1 necesita ANTES de
    correr (G3). La produce `M0_carga.leer_cabecera` y la consume
    `anticipo.contraste_de_cabecera`; vive aqui porque fluye entre modulos.

    NO VALIDA NADA -- ni tipos, ni rangos, ni cruzadas: eso es
    `M0_carga.cargar_puntos`, y esta lectura existe justamente para no
    ejecutarla --. Una cabecera incompleta o una celda imposible no son aqui
    un error sino el CONTENIDO que el anticipo tiene que mostrar.

    `columnas` conserva el orden del archivo (las de nombre vacio se
    descartan); `vacias_por_columna` cuenta las celdas vacias de cada columna
    --- una fila mas corta que la cabecera cuenta como vacias las celdas que
    no alcanza a traer ---; `filas` son las filas de datos con algun
    contenido.
    """

    columnas: Tuple[str, ...]
    vacias_por_columna: Dict[str, int]
    filas: int


# ===========================================================================
# El barrido de sensibilidad de un criterio (PF-3)
# ===========================================================================

@dataclass(frozen=True)
class CorridaDelBarrido:
    """
    Una corrida del barrido: el valor que el criterio tomo en ella, la
    procedencia con que se declaro (el texto del libro de `declaracion`),
    el volcado ENTERO de `cli.informe_json` y lo que el comparador de E-B
    dijo al contrastarla con la corrida del primer valor (`lineas()`, la
    primera empieza por IGUALES o DIFIEREN). `comparable` es False cuando
    el comparador encontro algun «no comparable»: metodo distinto en algun
    punto, alcance distinto, o un punto con diseño en una corrida y sin el
    en la otra. La produce `barrido.barrer`; ningun modulo de calculo la
    lee.
    """
    valor: Any
    procedencia: str
    informe_json: Dict[str, Any]
    comparacion_con_la_primera: Tuple[str, ...]
    comparable: bool


@dataclass(frozen=True)
class FilaDelBarrido:
    """
    Una fila de la tabla del barrido: un punto en una corrida. Todo lo que
    lleva se LEE del volcado de esa corrida (`puntos[].diseno`), y las dos
    ultimas columnas se leen de la comparacion con la corrida del primer
    valor: los codigos de las verificaciones cuyo veredicto `cumple` cambio,
    y si el punto se pudo comparar (`motivo` dice por que no). Cuando el
    punto no dimensiono, material, seccion, carga y control van en None y
    `incumplidas_en_la_progresion` dice que verificaciones incumplio a lo
    largo de su progresion (leido de `iteraciones[].incumplidas`); cuando
    dimensiono va vacia.
    """
    valor: Any
    id_punto: str
    dimensionado: bool
    material: Optional[str]
    seccion: Optional[str]
    HW_gobernante_m: Optional[float]
    control_gobernante: Optional[str]
    verificaciones_que_cambian: Tuple[str, ...]
    comparable: bool
    motivo: str = ""
    incumplidas_en_la_progresion: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ResultadoDeBarrido:
    """
    El barrido entero de UNA clave sobre una lista de valores de su
    ventana (PF-3): las corridas en el orden de los valores y la tabla por
    punto, una fila por (valor, punto). Los volcados enteros viajan dentro
    de cada corrida para que quien lea el barrido pueda comparar cualquier
    par con el comparador sin volver a correr nada.
    """
    clave: str
    corridas: Tuple[CorridaDelBarrido, ...]
    filas: Tuple[FilaDelBarrido, ...]
