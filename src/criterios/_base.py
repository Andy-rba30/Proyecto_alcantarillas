"""
Definicion de Criterio, niveles, formas y tablas derivadas base.
Submodulo de `src.criterios` extraido de `src/criterios_adoptados.py` (D2).
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from src.constantes_fisicas import PULGADA_EN_MM
from src.constantes_normativas import (
    DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM,
    D_INICIO,
    KE_HDS5_C2,
    K_CD_DESBORDE_SI,
    SIMBOLOS_SUCS,
    TMC_PLANCHA_CORRUGADA,
)
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import (
    NIVELES as _NIVELES,
    NIVEL_EXPEDIENTE as _NIVEL_EXPEDIENTE,
    NIVEL_PERFIL as _NIVEL_PERFIL,
    Resolucion,
)


# ---------------------------------------------------------------------------
# Estructura
# ---------------------------------------------------------------------------

# LOS DOS NIVELES DE ENTREGA. No son etiquetas de la taxonomia de CLAUDE.md
# (esas son [N], [N->], [S], [C], [A]) ni fases del calculo: dicen a que
# ENTREGA pertenece el criterio. Un estudio de PERFIL cierra con los primeros
# declarados; los segundos son del expediente tecnico, y `--alcance perfil`
# difiere sus etapas con su fundamento en el bloque de alcance.
#
# Desde EXT-10 los tres nombres se DEFINEN en `modelos.py` --- los lleva
# tambien `DatoSitio.nivel`, y `datos_sitio` no puede importar este modulo
# --- y aqui se reexportan con los mismos nombres, que son los que leen la
# GUI, `variables_entrada` y la suite (`ca.NIVEL_PERFIL`).
NIVEL_PERFIL = _NIVEL_PERFIL
NIVEL_EXPEDIENTE = _NIVEL_EXPEDIENTE
NIVELES = _NIVELES

# La etiqueta que exige ventana, y es UNA. CLAUDE.md lo escribe en la propia
# definicion de la taxonomia: «[A] Sin norma ni fuente unica. Adopcion
# declarada + sensibilidad». Las otras cuatro quedan fuera y cada una por su
# razon: [N] y [N->] no se eligieron, se leyeron -- darles rango seria decir
# que la norma admite otro numero --; [C] esta cubierto por una fuente tecnica
# reconocida, que es su procedencia y su defensa; y [S] se defiende con
# `trazabilidad`, no con rango, que es la regla que separa [S] de [A].
ETIQUETAS_DE_ELECCION = ("A",)

# LA FORMA DEL VALOR: la familia cerrada de estructuras que un criterio puede
# declarar (EXT-5; cierra EXT-G-01, PC-13, PC-14 y la mitad de FORMA de
# EXT-V-02, EXT-V-05 y EXT-V-06). Es lo que el CONSUMIDOR va a exigir, dicho
# en la ficha para que la puerta de declaracion lo exija ANTES: hasta EXT-5
# la guardia validaba etiqueta, nivel, finitud y la ventana de sensibilidad,
# pero no la ESTRUCTURA del valor, de modo que 53 de las 70 claves aceptaban
# la cadena 'cero' y la aritmetica reventaba despues con un `TypeError` fuera
# de `ErrorProyecto` (PC-14), y la GUI no podia declarar un ENTERO para
# `n_celdas_cajon` porque nada le decia que hacia falta uno (PC-13).
#
# Ocho formas, no siete: el prompt de EXT-5 enumera siete y `F_pga` no cabe
# en ninguna --- declara la TUPLA de filas de la tabla sobre las que se lee
# el factor ('C', 'D', 'E'), que no es un texto ni una serie de pares ---, y
# meterla a la fuerza en `categoria` escondia la estructura que M9 exige.
# `serie_de_claves` la nombra. Esta escrito en decisiones_diferidas.md.
#
# Un criterio puede llevar la UNION de dos formas, como tupla: `k_v` admite
# la cadena del regimen prescrito O el numero del caso reservado (asi lo
# consume `M9.k_v_declarado`), y una forma unica habria estrechado el
# contrato que el consumidor ya tiene.
FORMA_INT = "int"                       # entero de Python; `bool` queda fuera
FORMA_FLOAT = "float"                   # real (un `int` vale); `bool` queda fuera
FORMA_STR = "str"                       # texto no vacio: la CLAVE de una fila, un metodo
FORMA_PAR_ORDENADO = "par_ordenado"     # (minimo, maximo) de reales, en orden
FORMA_SERIE_DE_PARES = "serie_de_pares" # [(B, H), ...] de reales, sin repetidos
FORMA_DICT_CON_CAMPOS = "dict_con_campos"  # dict no vacio con claves de texto
FORMA_CATEGORIA = "categoria"           # texto de un conjunto cerrado: `sensibilidad`
FORMA_SERIE_DE_CLAVES = "serie_de_claves"  # (clave, ...) de textos, sin repetidos
FORMAS = (FORMA_INT, FORMA_FLOAT, FORMA_STR, FORMA_PAR_ORDENADO,
          FORMA_SERIE_DE_PARES, FORMA_DICT_CON_CAMPOS, FORMA_CATEGORIA,
          FORMA_SERIE_DE_CLAVES)


@dataclass(frozen=True)
class Criterio:
    valor: Any
    etiqueta: str                              # "N", "N->", "S", "C", "A"
    concepto: str                              # que es
    justificacion: str                         # por que este valor
    fuente: str                                # de donde sale
    forma: Any = ""                            # una de FORMAS, o una tupla de ellas; obligatoria
    reemplazado_por: Optional[str] = None      # ensayo/dato que lo sustituye
    sensibilidad: Optional[Tuple] = None       # rango declarado -- [A] y [C]; nunca [S]
    trazabilidad: Optional[str] = None         # como reproducir la lectura -- SOLO [S]
    verificacion_pendiente: Optional[str] = None   # lo que falta confirmar
    provisional: bool = False                  # valor de PRUEBA, no verificado
    opcional: bool = False                     # valor=None NO bloquea: hay defecto normativo
    vacio_verificado: str = ""                 # ancla al vacio registrado que este valor cubre
    sin_consumidor: str = ""                   # por que NINGUN modulo lo invoca
    de_catalogo: str = ""                      # rotulo: el valor es de CATALOGO, no de norma
    resolucion: Optional[Resolucion] = None    # COMO se resuelve (Sec. 4.3): tabla, rango, ensayo...
    campos_obligatorios: Tuple[str, ...] = ()  # solo con `dict_con_campos`: los campos que la puerta exige (EXT-6)
    # EL SIGNO, exigido en la puerta (revision de VE-2, M4). El mismo campo
    # que `datos_sitio.DatoSitio.no_negativo`, y por la misma razon: un
    # `float` cuya ventana es SIMBOLICA (dos frases, no un par de numeros)
    # no tiene rango numerico que rechace un negativo, y sin esto el negativo
    # entraba por los tres caminos y solo lo atrapaba el consumidor. No es
    # un tope: no dice cuanto puede valer, solo que no puede ser menor que
    # cero. Solo en `int` o `float` (`_verificar_signo`).
    no_negativo: bool = False
    # Y EL ESTRICTO (verificacion de las correcciones de VE-2, N2): el mismo
    # campo que `datos_sitio.DatoSitio.positivo`. Un peso especifico cero o
    # negativo no es un dato que se pueda leer de un ensayo; sin esto la
    # puerta lo aceptaba y solo lo rechazaba el consumidor.
    positivo: bool = False
    nivel: str = ""
    # LAS DISCREPANCIAS DECLARADAS QUE ESTE CRITERIO TOCA, por su id.
    #
    # Tercera via del canal de C8, y la que faltaba: hay discrepancias que no
    # hablan de un TEXTO (esas llegan solas, cruzando las citas que los pasos
    # imprimen) ni de un valor que un PASO sustituye (esas las declara el
    # paso), sino del valor de un CRITERIO. `DIS-HR-D-MAX` es el caso vivo:
    # dice que los topes de 2.70 / 2.10 / 1.50 m no son normativos sino de
    # catalogo, y quien los lleva es este archivo. V9 los consulta y ni
    # siquiera emite paso.
    #
    # VIAJA EL ID Y NUNCA EL TEXTO. Antes de C8 estos ids se escribian a mano
    # DENTRO de la `justificacion` --- prosa, invisible al registro, imposible
    # de enumerar y libre de divergir de la discrepancia que nombra. Aqui el
    # registro comprueba que el id exista y que siga viva, y M11 imprime la
    # discrepancia entera desde el registro.
    discrepancias: Tuple[str, ...] = ()                            # NIVEL_PERFIL / NIVEL_EXPEDIENTE / "" sin clasificar

    # `nivel` responde a UNA pregunta y no a dos: si este criterio hay que
    # tenerlo declarado para cerrar el nivel de PERFIL, o si su etapa la
    # difiere el alcance de perfil al expediente. No es la fase (eso es
    # `variables_entrada`) ni la etiqueta (eso es la taxonomia de CLAUDE.md):
    # es a que ENTREGA pertenece.
    #
    # La regla que lo decide, y es empirica, no de opinion: el nivel de un
    # criterio es el nivel de la etapa que lo consume. Si una corrida
    # `--alcance perfil` lo invoca sin que su etapa quede diferida, es de
    # perfil. `tests/test_criterios_adoptados.py` lo comprueba corriendo el
    # pipeline y contrastando `criterios_usados()` contra este campo, de modo
    # que la clasificacion no puede quedar desincronizada del codigo -- que
    # es exactamente como se desincronizan las clasificaciones escritas a
    # mano en un documento.

    # `resolucion` es el vinculo que faltaba: dice DE DONDE SALIO el valor --
    # de que tabla y de que fila, de que rango, de que ensayo, de que catalogo
    # -- y con el la memoria puede escribir "el valor X vino de la fila R de la
    # tabla T" en vez de dejar al revisor cruzando a mano la prosa de `fuente`
    # con el registro normativo (regla R1 del plan v12).
    #
    # No es un `str` con el nombre del modo: es un objeto de la familia cerrada
    # de `modelos.py` (Libre / DeTabla / EnRango / Derivada / DeEnsayo /
    # DeCatalogo) y EL MODO ES SU TIPO. Un criterio no puede quedarse sin modo
    # ni declarar uno que no corresponda a como se resuelve, porque no hay dos
    # campos que puedan contradecirse: hay uno.
    #
    # Es `Optional` solo por la firma; la guardia lo exige a toda entrada del
    # archivo. El default existe para que `replace()` -- los dos caminos
    # dinamicos -- no tenga que repetirlo.

    # `de_catalogo` marca el valor que se PARECE a una exigencia normativa y
    # no lo es: un tope de proveedor, una disponibilidad de mercado. Lleva el
    # rotulo con que hay que imprimirlo -- de que catalogo sale y que norma de
    # producto NO lo sostiene -- para que la memoria no le invente una cita.
    #
    # Nace de NOR-PRO-01 y NOR-PRO-02: los topes D_MAX (2.70 / 2.10 / 1.50 m)
    # vivian en constantes_normativas.py atribuidos a AASHTO M170 y ASTM A760,
    # y esas normas tabulan hasta 3600 mm. Un tope de catalogo impreso como
    # tope normativo es una cita falsa que ademas descarta materiales en
    # silencio. El campo existe para que la distincion viaje con el dato y no
    # dependa de que alguien lea la justificacion entera.

    # `sin_consumidor` es la razon escrita de que ninguna etapa de produccion
    # llame a este criterio. Existe porque un criterio sin consumidor tiene
    # dos lecturas opuestas -- se olvido cablearlo, o su consumidor esta
    # declarado fuera de alcance -- y desde fuera del archivo no se
    # distinguen: `criterios_usados()` devuelve lo mismo en los dos casos.
    #
    # Sin el campo, un criterio CON valor y sin invocacion no cae en ninguno
    # de los tres bloques de M11 (no esta usado, no esta vacio, no es
    # opcional) y desaparece de la memoria sin dejar rastro. Con el, M11 lo
    # imprime en su propio bloque con la razon delante.

    # `vacio_verificado` distingue dos cosas que se parecen y no son iguales:
    # un valor que cubre un hueco que NADIE busco, y uno que cubre un hueco
    # que alguien AGOTO -- fuente por fuente, con cita -- y dejo registrado.
    # Solo lo segundo se puede defender en una memoria, y solo lo segundo
    # entra en el bloque de acotaciones que M11 imprime.
    #
    # No es un booleano a proposito: lleva el ANCLA al registro
    # ("manifiesto_citas.md Sec. 14.a"), de modo que la memoria puede decirle
    # al revisor donde ir a leer la busqueda completa en vez de pedirle que
    # confie. `_verificar_criterio` comprueba al importar que esa seccion
    # existe de verdad: un ancla rota falla, no pasa en silencio.

    # `opcional=True` cambia el significado de `valor=None`, que sin el
    # significa una sola cosa: vacio que detiene el calculo. Un criterio
    # opcional REFINA un valor que la norma ya fija, en vez de cubrir un
    # vacio que la norma deje abierto; sin declarar, el consumidor aplica el
    # valor normativo por defecto y el calculo sigue. Se lee con
    # `valor_si_declarado()`, nunca con `valor()`.
    #
    # La distincion vivia solo en que funcion usaba el llamador, mas prosa en
    # la justificacion. Eso dejaba a `criterios_sin_valor()` -- y con el, al
    # bloque "VACIOS SIN VALOR" de la memoria y al aviso de la GUI --
    # anunciando como vacio bloqueante lo que es un refinamiento que nadie
    # tiene obligacion de declarar. Ahora la distincion esta en el dato.

    # `provisional=True` marca un valor cargado para una corrida de prueba
    # integral: destraba el pipeline para ver que puntos completan diseno,
    # pero NO esta verificado contra norma ni ensayo y no puede ir a una
    # memoria de calculo. Existe para que ese valor NUNCA pueda pasar
    # inadvertido: reporte_criterios() y M11 lo imprimen con marca visible.
    # Ningun criterio del expediente lo lleva puesto -- si alguno aparece
    # con provisional=True en una revision, es que quedo residuo de una
    # prueba sin limpiar.

    # sensibilidad y trazabilidad no son dos nombres para lo mismo y no se
    # mezclan: un [A] se defiende mostrando cuanto cambiaria el resultado con
    # el otro extremo del rango, y un [S] no tiene rango que elegir -- se
    # defiende diciendo donde se leyo, para que el revisor repita la lectura.
    # `_verificar_criterio()` lo verifica al importar el modulo.




# ---------------------------------------------------------------------------
# La Tabla 5.10.1-1 de AASHTO, DERIVADA DEL REGISTRO y no copiada a mano
# ---------------------------------------------------------------------------
# Este dict era 63 numeros escritos aqui, y la transcripcion completa de la
# misma tabla vive ahora en el registro normativo, con el rotulo literal en
# ingles de cada fila, la pulgada IMPRESA al lado del milimetro convertido, la
# nota de las tres categorias y la correspondencia declarada con la tabla del
# Manual de Puentes. Mantener dos copias a mano de la misma tabla es
# exactamente el defecto que este cluster existe para eliminar: la que el
# revisor lee y la que el programa calcula tienen que ser LA MISMA.
#
# LA CONVERSION NO SE REHACE AQUI. La tabla del registro trae las columnas en
# pulgadas -- lo impreso -- y en milimetros -- la conversion del proyecto,
# exacta --, y esta funcion solo las reagrupa por (situacion, categoria), que
# es la forma en que `M9._recubrimiento_aashto_detallado` las consulta.
def _tabla_recubrimiento_aashto_mm() -> Dict[str, Dict[str, float]]:
    from src.normativa import registro as _rn
    tabla = _rn.construir().tabla("AASHTO_LRFD_9.T5.10.1-1")
    return {
        tabla.clave_corta(fila): {
            "A": float(fila.valores["cat_a_mm"]),
            "B": float(fila.valores["cat_b_mm"]),
            "C": float(fila.valores["cat_c_mm"]),
        }
        for fila in tabla.filas
    }


_TABLA_RECUBRIMIENTO_AASHTO_MM = _tabla_recubrimiento_aashto_mm()


# --- T-4 --- La doble n del HDPE, DERIVADA de la fila transcrita de la Table
# B.1 del HDS-5 (`HDS5_3ED.TB.1`) y no escrita a mano: es el valor y la
# ventana de 'n_manning_hdpe'. Mismo patron que la tabla de arriba.
def _n_manning_hdpe_hds5() -> Tuple[float, float]:
    from src.normativa import registro as _rn
    fila = _rn.construir().tabla("HDS5_3ED.TB.1").fila(
        "polietileno_corrugado_liso")
    return (float(fila.valores["n_min"]), float(fila.valores["n_max"]))


_N_MANNING_HDPE_HDS5 = _n_manning_hdpe_hds5()


# --- VE-2 (a) --- El n UNICO que el HDS-5 da como tipico de diseño para un
# conducto de PARED LISA (num. 3.1.4, pag. impresa 3.8, cita
# HDS5_3ED.3.1.4#N_TIPICO: «Typical Manning's n values used for designing
# culverts are n = 0.012 for smooth walled culverts»). Es [C] y por eso vive
# aqui y no en `constantes_normativas`: no es una exigencia peruana, es la
# alternativa 'n_unico_hds5' del criterio [A] 'columna_n_manning_concreto'.
# No es una fila de tabla que se pueda leer del registro --es una frase--, y
# `tests/test_ve2_materiales.py` comprueba que el numero ES el de la frase.
N_MANNING_PARED_LISA_HDS5 = 0.012


# --- T-4 --- El espesor del HDPE, DERIVADO de la Table A12-11 de AASHTO LRFD
# (`AASHTO_LRFD_9.TA12-11`): el t que lleva el diametro DESIGNADO del catalogo
# hasta el diametro exterior MAXIMO del producto, t = (Max. OD - D) / 2. El
# designado en mm de cada tamaño en pulgadas se lee de la serie de la propia
# norma de producto (`AASHTO_M294_TRAD.T7.2.2`: «900 (36)», «1050 (42)»,
# «1200 (48)»), no se calcula. Solo los tamaños del catalogo (de 0.90 m en
# adelante) y solo los que la tabla de AASHTO trae: tres filas.
def _espesor_hdpe_de_aashto() -> Dict[int, float]:
    from src.normativa import registro as _rn
    reg = _rn.construir()
    designado_mm = {f.valores["dn_in"]: f.valores["dn_mm"]
                    for f in reg.tabla("AASHTO_M294_TRAD.T7.2.2").filas}
    piso_mm = round(D_INICIO * MILIMETROS_POR_METRO)
    espesores = {}
    for fila in reg.tabla("AASHTO_LRFD_9.TA12-11").filas:
        dn_mm = designado_mm[fila.valores["nominal_in"]]
        if dn_mm < piso_mm:
            continue
        od_max_m = fila.valores["od_max_in"] * PULGADA_EN_MM / MILIMETROS_POR_METRO
        espesores[dn_mm] = round((od_max_m - dn_mm / MILIMETROS_POR_METRO) / 2,
                                 _DECIMALES_DE_ESPESOR)
    return espesores


# Diezmilesima de metro: la tabla da el diametro exterior a la decima de
# pulgada (2.5 mm), de modo que mas cifras no son informacion.
_DECIMALES_DE_ESPESOR = 5
_ESPESOR_HDPE_AASHTO = _espesor_hdpe_de_aashto()


# --- T-4 --- El tope de la SERIE de cada norma de producto, DERIVADO de la
# ultima fila de las tres tablas del registro, en metros.
def _topes_de_la_norma_de_producto() -> Dict[str, float]:
    from src.normativa import registro as _rn
    reg = _rn.construir()
    topes = {
        material: max(f.valores["dn_mm"] for f in reg.tabla(tabla).filas)
        / MILIMETROS_POR_METRO
        for material, tabla in (
            ("tmc", "AASHTO_M36.T6"),
            ("hdpe", "AASHTO_M294_TRAD.T7.2.2"))
    }
    # EL CONCRETO NO TOMA LA ULTIMA FILA DE SU SERIE (auditoria de T-4, H2):
    # M 170M lista diametros hasta 3600 mm, pero por encima de 2700 mm no
    # tabula pared ni acero -- son los diseños especiales de su Seccion 7.2 --.
    # El tope es el mayor diametro con diseño estandar.
    return {"concreto_reforzado":
            DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM / MILIMETROS_POR_METRO,
            **topes}


_TOPES_DE_LA_NORMA_DE_PRODUCTO = _topes_de_la_norma_de_producto()

# --- T-4 --- Los dos conjuntos cerrados que se derivan de una vista de
# `constantes_normativas`: las planchas del TMC y los simbolos SUCS.
_CLAVES_DE_PLANCHA_TMC = tuple(TMC_PLANCHA_CORRUGADA)
_SIMBOLOS_SUCS_E050 = SIMBOLOS_SUCS
# --- T-1 --- Las cuatro superficies de la plataforma vial que la Tabla N 08
# del Manual de Hidrologia no tiene, leidas de la Table 2-2 del WSDOT
# Hydraulics Manual tal como esta en el registro (no copiadas a mano). Las
# cuatro filas valen lo mismo en las tres columnas de pendiente de esa tabla,
# y el helper lo EXIGE: si una transcripcion futura las separase, habria que
# elegir columna y esto dejaria de ser un numero por superficie.
SUPERFICIES_VIALES_WSDOT = ("pavimento", "berma_de_tierra", "talud_de_tierra",
                            "talud_con_cesped")


def _coeficientes_de_superficies_viales() -> Dict[str, float]:
    from src.normativa import registro as _rn
    tabla = _rn.construir().tabla("WSDOT_HM.T2-2")
    salida: Dict[str, float] = {}
    for clave in SUPERFICIES_VIALES_WSDOT:
        celdas = set(tabla.fila(clave).valores.values())
        if len(celdas) != 1:
            raise ValueError(
                f"WSDOT_HM.T2-2#{clave}: la fila ya no vale lo mismo en sus "
                f"tres columnas ({sorted(celdas)}); hay que elegir columna")
        salida[clave] = float(celdas.pop())
    return salida


_COEFICIENTES_VIALES_WSDOT = _coeficientes_de_superficies_viales()


# El recorrido de los coeficientes de la Tabla C.2 del HDS-5, DERIVADO de la
# transcripcion del registro (`constantes_normativas.KE_HDS5_C2`) y no
# escrito a mano: es la ventana de 'ke_entrada' (PC-02). Si la transcripcion
# gana filas, la ventana las sigue.
_VENTANA_KE_C2 = (min(f["ke"] for f in KE_HDS5_C2.values()),
                  max(f["ke"] for f in KE_HDS5_C2.values()))

# --- T-9 --- Los revestimientos de cuneta que el criterio
# 'revestimiento_cuneta' admite: cada clave UNE una fila de la Tabla Nº 32
# del Manual de Hidrologia (K de Strickler, el n de Manning) con una de su
# Tabla Nº 33 (velocidad limite admisible). Solo «concreto» une dos filas
# que nombran el mismo material; las demas uniones son LECTURA DEL PROYECTO
# --la fuente no relaciona las dos tablas-- y la memoria lo imprime. Son
# claves de fila, no numeros: los valores viven en el registro.
REVESTIMIENTOS_CUNETA: Dict[str, Tuple[str, str]] = {
    "concreto": ("de_concreto", "concreto"),
    "roca_dura": ("en_roca", "mamposteria_rocas_duras"),
    "roca_blanda": ("en_roca", "conglomerado_pizarras_duras_rocas_blandas"),
    "terreno_hierba": ("excavada_en_terreno", "hierba"),
    "terreno_arcilla_grava": (
        "excavada_en_terreno",
        "arcilla_grava_pizarras_blandas_con_cubierta_vegetal"),
    "terreno_con_vegetacion": (
        "excavada_en_terreno", "terreno_parcialmente_cubierto_de_vegetacion"),
    "terreno_arena_arcillosa": (
        "excavada_en_terreno", "arena_arcillosa_dura_margas_duras"),
    "terreno_arena_fina_o_limo": ("excavada_en_terreno", "arena_fina_o_limo"),
}


# --- VE-5 fixve4 --- LA FIGURA 3.11 DEL HDS-5 COMO SE LEYO (curvas de C_r
# en las unidades de la figura, ft^0.5/s; el panel B ya con la abscisa en m).
# Es la TRANSCRIPCION de la lectura de VE-4d (ver el comentario del criterio
# 'coeficientes_desborde_plataforma', que dice como se leyo); el imperial no
# entra en ninguna formula: el criterio guarda estas curvas CONVERTIDAS a SI
# con K_CD_DESBORDE_SI (revision de la fusion de VE-4, hallazgo 3), y el test
# marcado `pdf` de tests/test_ve4d_v8_desborde.py contrasta esta transcripcion
# con la imagen. Ordenada imperial: C_r(SI) = 0.552 · C_r(figura).
_FIGURA_3_11_C_R_LEIDA = {
    # Panel A: abscisa HW_r/L_r (el eje esta rotulado «HWr», y su
    # rango 0.15-0.32 es el de la relacion: interpretacion
    # declarada en la cita HDS5_3ED.F3.11).
    "Cr_profundo": {
        "pavimentada": ((0.15, 3.052), (0.16, 3.058), (0.18, 3.067),
                        (0.20, 3.076), (0.22, 3.081), (0.24, 3.085),
                        (0.26, 3.088), (0.28, 3.091), (0.30, 3.093),
                        (0.32, 3.093)),
        "grava": ((0.15, 2.951), (0.16, 2.958), (0.18, 2.979),
                  (0.20, 3.001), (0.22, 3.021), (0.24, 3.043),
                  (0.26, 3.060), (0.28, 3.079), (0.30, 3.090),
                  (0.32, 3.094)),
    },
    # Panel B: abscisa HW_r en METROS. La figura la da en pies (0 a
    # 4.0 ft): se leyo en 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0,
    # 1.25 (grava), 1.5, 1.75 (grava), 2.0, 2.5, 3.0, 3.5 y 4.0 ft y
    # se convirtio con 0.3048 m/ft exactos. El valor en 0 se toma en
    # la primera columna del trazo (0.02 ft) extrapolado al eje.
    "Cr_somero_m": {
        "pavimentada": ((0.0, 2.897), (0.03048, 2.933),
                        (0.06096, 2.969), (0.09144, 2.990),
                        (0.12192, 3.006), (0.1524, 3.019),
                        (0.18288, 3.026), (0.24384, 3.032),
                        (0.3048, 3.034), (0.4572, 3.034),
                        (0.6096, 3.037), (0.762, 3.037),
                        (0.9144, 3.043), (1.0668, 3.040),
                        (1.2192, 3.040)),
        "grava": ((0.0, 2.513), (0.03048, 2.550), (0.06096, 2.591),
                  (0.09144, 2.629), (0.12192, 2.674), (0.1524, 2.701),
                  (0.18288, 2.729), (0.24384, 2.778), (0.3048, 2.827),
                  (0.381, 2.875), (0.4572, 2.919), (0.5334, 2.953),
                  (0.6096, 2.978), (0.762, 3.012), (0.9144, 3.034),
                  (1.0668, 3.039), (1.2192, 3.039)),
    },
}
_FIGURA_3_11_C_R_EN_SI = {
    curva: {superficie: tuple((abscisa, K_CD_DESBORDE_SI * ordenada)
                              for abscisa, ordenada in serie)
            for superficie, serie in por_superficie.items()}
    for curva, por_superficie in _FIGURA_3_11_C_R_LEIDA.items()}
