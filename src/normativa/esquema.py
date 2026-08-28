"""
El esquema del registro normativo.

Implementa docs/diseno_registro_normativo.md §3-§8. Aqui NO hay ni una sola
cita: hay tipos. Las citas viven en `citas.py`, las fuentes en `fuentes.py` y
las tablas en `tablas.py`.

LAS CINCO DECISIONES QUE GOBIERNAN TODO LO DEMAS (§2 del diseño), para que
quien tenga que resolver un caso que este archivo no anticipa lo resuelva
igual que se resolvio el resto:

  D1  La cita es un OBJETO con id estable, no un texto. Ningun modulo escribe
      un numeral, una pagina o un titulo de tabla como literal.
  D2  Transcripcion y vista de calculo son dos cosas, y la segunda se DERIVA
      de la primera. Nunca hay dos copias de un numero.
  D3  Lo que la fuente dice (`caracter`) y lo que el proyecto hace con ello
      (`aplicacion`) son campos distintos, siempre.
  D4  Lo indeterminado BLOQUEA. Lo que no bloquea es lo que hay que justificar.
  D5  Cuando una lectura falsa sea posible, se elimina el tipo que la permite.

Y de la ultima sale la forma de este archivo: familias CERRADAS de tipos en
vez de un campo `tipo: str`. Un `ConjuntoDeMaximos` no tiene atributo
`minimo`, de modo que una ventana no puede pintarlo con una casilla "desde".
Documentar el error no impide cometerlo; no poder representarlo, si.

POR QUE LOS INVARIANTES SE COMPRUEBAN EN `__post_init__` Y NO SOLO EN TESTS.
Los que dependen de un PDF (que el texto literal este de verdad en esa pagina)
son de test: hace falta abrir el archivo. Los que son puramente estructurales
--que un `Acotada` traiga su razon, que una condicion no bloqueante traiga su
justificacion-- se comprueban al construir, porque un objeto mal formado no
debe llegar a existir ni siquiera en memoria. La suite los vuelve a comprobar
sobre el registro entero (§9.1); esto es el cinturon y aquello los tirantes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple, Union


# ===========================================================================
# El centinela de lo aun no leido
# ===========================================================================
class _PorTranscribir:
    """
    UN valor admisible para el campo obligatorio que todavia no se ha leido
    del PDF -- y solo uno, para que no haya un segundo camino.

    Existe porque los dos extremos son peores. Un campo verbatim OPCIONAL se
    queda vacio y nadie lo nota. Un campo obligatorio que alguien rellena
    "provisionalmente" con algo plausible es la fabrica de citas falsas, que
    es la clase de defecto que la Sec. 0.5 de la hoja de ruta llama la mas
    grave: un vacio se ve, una cita falsa se cree.

    Sus dos reglas, que el test T22 vigila:
      - una `Cita` con cualquier campo en POR_TRANSCRIBIR no puede llevar
        `verificado`;
      - el total de POR_TRANSCRIBIR del registro solo puede DECRECER.

    Es la misma idea del `valor=None` de `criterios_adoptados`, aplicada a la
    cita.
    """

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def __repr__(self) -> str:
        return "POR_TRANSCRIBIR"

    def __bool__(self) -> bool:
        # Deliberadamente falsy: `if cita.titulo_numeral:` se lee como
        # "si ya se transcribio", que es lo que el consumidor quiere preguntar.
        return False


POR_TRANSCRIBIR = _PorTranscribir()

PorTranscribir = _PorTranscribir


def esta_por_transcribir(v: object) -> bool:
    return isinstance(v, _PorTranscribir)


class ErrorDeRegistro(ValueError):
    """
    Un objeto del registro mal formado. NO desciende de `ErrorProyecto`: no es
    un problema del expediente que la GUI deba mostrarle al proyectista, es un
    defecto del propio registro y lo tiene que ver quien lo escribe.
    """


# ===========================================================================
# §3.2 - Paginacion: por que `desfase_pagina` no puede ser un entero
# ===========================================================================
@dataclass(frozen=True)
class Corrida:
    """Numeracion continua: pdf = impresa + desfase."""
    desfase: int

    def pagina_pdf(self, impresa: str) -> Optional[int]:
        try:
            return int(impresa) + self.desfase
        except ValueError:
            return None


@dataclass(frozen=True)
class PorCapitulo:
    """
    Numeracion "3.24", "A.8", "11-145": el capitulo tiene su propia base y la
    etiqueta impresa NO es un numero. HDS-5 y AASHTO LRFD numeran asi, y por
    eso `pagina_impresa` es `str` en toda la casa: "3.24" no es 3,24.
    """
    base: Dict[str, int]
    separadores: Tuple[str, ...] = (".", "-")

    def _partir(self, impresa: str) -> Optional[Tuple[str, int]]:
        for sep in self.separadores:
            if sep in impresa:
                capitulo, _, numero = impresa.rpartition(sep)
                try:
                    return capitulo, int(numero)
                except ValueError:
                    return None
        return None

    def pagina_pdf(self, impresa: str) -> Optional[int]:
        partes = self._partir(impresa)
        if partes is None:
            return None
        capitulo, numero = partes
        if capitulo not in self.base:
            return None
        return self.base[capitulo] + numero


@dataclass(frozen=True)
class Irregular:
    """
    No hay regla: la correspondencia se declara pagina a pagina. `por_que` es
    obligatorio para que "irregular" no sea el cajon donde se tira lo que no
    se quiso medir.
    """
    tabla: Dict[str, int]
    por_que: str

    def __post_init__(self) -> None:
        if not self.por_que.strip():
            raise ErrorDeRegistro(
                "Irregular exige `por_que`: decir por que no hay regla es lo "
                "que separa una medicion de una rendicion")

    def pagina_pdf(self, impresa: str) -> Optional[int]:
        return self.tabla.get(impresa)


@dataclass(frozen=True)
class SinDeterminar:
    """
    El desfase NO se ha medido. No es un hueco del esquema: con un
    `desfase: int = 0` por defecto, una fuente sin medir se veria igual que
    una medida en cero, y eso es exactamente lo que hay que impedir.

    INVARIANTE: ninguna `Cita` a una `Fuente` con esta paginacion puede
    llevar `pagina_pdf` ni, por tanto, `verificado`.
    """
    por_que: str

    def __post_init__(self) -> None:
        if not self.por_que.strip():
            raise ErrorDeRegistro("SinDeterminar exige `por_que`")

    def pagina_pdf(self, impresa: str) -> Optional[int]:
        return None


Paginacion = Union[Corrida, PorCapitulo, Irregular, SinDeterminar]


# ===========================================================================
# §8 - Fuentes que se citan y NO estan en normas/
# ===========================================================================
class Esfuerzo(str, Enum):
    """Cuanto cuesta conseguir una fuente ausente. Convierte deuda en precio."""
    DESCARGA_PUBLICA = "facil, es descarga publica"
    COMPRA = "compra o suscripcion"
    GABINETE = "gabinete"
    CAMPO = "de campo"


@dataclass(frozen=True)
class Ausencia:
    por_que_se_cita: str
    que_desbloquearia: str
    esfuerzo: Esfuerzo
    sustituto_vigente: Optional[str] = None

    def __post_init__(self) -> None:
        for campo in ("por_que_se_cita", "que_desbloquearia"):
            if not getattr(self, campo).strip():
                raise ErrorDeRegistro(f"Ausencia exige `{campo}` no vacio")


@dataclass(frozen=True)
class Fuente:
    """
    Un documento normativo. §3.1 del diseño.

    `convive_con` no es adorno: en normas/ hay DOS HDS-5 que no dicen lo
    mismo, y leer la de 1985 "en SI" reproduce el error del 29 imperial
    (+9.6 %). Aqui son dos `Fuente` con `convive_con` cruzado y una
    `Discrepancia` que declara cual gobierna.
    """
    id: str
    titulo: str
    emisor: str
    edicion: str
    anio: int
    resolucion: str = ""
    archivo_pdf: Optional[str] = None
    sha1: Optional[str] = None
    paginas_pdf: Optional[int] = None
    paginacion: Paginacion = SinDeterminar(por_que="no medida")
    texto_extraible: bool = True
    ausente: bool = False
    ausencia: Optional[Ausencia] = None
    reemplaza_a: Optional[str] = None
    convive_con: Tuple[str, ...] = ()
    nota: str = ""

    def __post_init__(self) -> None:
        if self.ausente:
            if self.ausencia is None:
                raise ErrorDeRegistro(
                    f"Fuente {self.id}: `ausente=True` exige `ausencia`. Una "
                    "fuente que no esta se DECLARA; no se deja en blanco")
            if self.archivo_pdf is not None or self.sha1 is not None:
                raise ErrorDeRegistro(
                    f"Fuente {self.id}: una fuente ausente no tiene archivo "
                    "ni sha1. No hay contra que verificar y el registro no "
                    "finge que lo hay")
        else:
            if not self.archivo_pdf:
                raise ErrorDeRegistro(
                    f"Fuente {self.id}: una fuente presente declara su PDF")
            if not self.sha1:
                raise ErrorDeRegistro(
                    f"Fuente {self.id}: una fuente presente declara su sha1. "
                    "Es lo que ata cada `verificado` a UN archivo exacto")

    @property
    def verificable_por_pagina(self) -> bool:
        return not self.ausente and not isinstance(self.paginacion, SinDeterminar)


@dataclass(frozen=True)
class Catalogo:
    """
    NO es una `Fuente`, y esa separacion es el cierre estructural de
    NOR-PRO-01 / NOR-PRO-02.

    Un tope de catalogo no tiene numeral, y el sistema de tipos no le deja
    fingir que lo tiene: un `Catalogo` no puede ser el `fuente_id` de una
    `Cita` (test T1). Es lo que impide que los topes D_MAX vuelvan a
    imprimirse atribuidos a AASHTO M170 y ASTM A760 -- normas que tabulan
    hasta 3 600 mm -- descartando materiales en silencio con una cita que
    ninguna norma sostiene.
    """
    id: str
    titulo: str
    proveedor_o_ambito: str
    que_norma_NO_lo_sostiene: str

    def __post_init__(self) -> None:
        if not self.que_norma_NO_lo_sostiene.strip():
            raise ErrorDeRegistro(
                f"Catalogo {self.id}: `que_norma_NO_lo_sostiene` es "
                "obligatorio y no vacio. Es el campo entero del tipo")


# ===========================================================================
# §3.3 - TextoDeFuente: cuatro tipos, porque «literal» es una afirmacion
# ===========================================================================
class TextoDeFuente:
    """
    Base sellada. No se instancia.

    Existe porque el repositorio se tropezo DOS VECES con el mismo pie:
    NOR-HID-06 se cerro rotulando "Texto literal" dos composiciones que no lo
    eran, dentro del bloque construido para cerrarlo. Partir el campo en dos
    ayudo; con TIPOS, elegir mal es un error de construccion.
    """

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)


@dataclass(frozen=True)
class Verbatim(TextoDeFuente):
    """
    EXACTO, con las tildes, las mayusculas y las erratas de la fuente.

    Un literal de-acentuado no se puede encontrar en el PDF con el buscador de
    un lector, y entonces no es verificable por nadie salvo por quien ya sabe
    donde esta. La normalizacion sin diacriticos existe para BUSCAR, nunca
    para GUARDAR (test T21).
    """
    texto: str
    pagina_pdf: Union[int, PorTranscribir] = POR_TRANSCRIBIR

    def __post_init__(self) -> None:
        if not self.texto.strip():
            raise ErrorDeRegistro("Verbatim vacio: no es una cita")


@dataclass(frozen=True)
class Transcripcion(TextoDeFuente):
    """
    Datos de la fuente REORDENADOS por el proyecto. No se busca en el PDF
    porque no es una cita, y el rotulo lo dice.
    """
    texto: str
    de_donde: str

    def __post_init__(self) -> None:
        if not self.de_donde.strip():
            raise ErrorDeRegistro(
                "Transcripcion exige `de_donde`: que objeto del registro se "
                "reformateo. Sin eso no se distingue de un Verbatim")


@dataclass(frozen=True)
class Interpretacion(TextoDeFuente):
    """
    Lectura del PROYECTISTA. Lleva los hechos de la fuente que juegan en
    contra, no solo los que juegan a favor: es lo que permite a un revisor
    discutirla sin discutir la norma.

    INVARIANTE T7: nunca se serializa dentro de un campo de cita. El defecto
    de `76791d0` no fue de una constante suelta; fue del formato.
    """
    texto: str
    en_contra: Tuple[str, ...] = ()
    a_favor: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.en_contra:
            raise ErrorDeRegistro(
                "Interpretacion exige al menos un `en_contra`. Una lectura "
                "que no encuentra nada en contra no se ha buscado a si misma")


@dataclass(frozen=True)
class AfirmacionNegativa(TextoDeFuente):
    """
    "La Tabla N 09 no lista HDPE". Se verifica AL REVES: por ausencia sobre un
    ambito declarado.

    Hace falta como tipo propio porque una afirmacion negativa es lo que
    AUTORIZA saltar a un criterio [C] con fuente externa. Una mal hecha cubre
    con fuente ajena un vacio que no existe -- que es la forma exacta de
    NOR-VAC-01, donde el "vacio verificado" de la cobertura minima no era un
    vacio: AASHTO 12.6.6.3 lo tabulaba.
    """
    que_no_dice: str
    ambito_barrido: str
    cita_id: str = ""

    def __post_init__(self) -> None:
        if not self.ambito_barrido.strip():
            raise ErrorDeRegistro(
                "AfirmacionNegativa exige `ambito_barrido`: que se leyo "
                "entero para poder afirmarlo. Sin ambito no es una "
                "afirmacion, es una impresion")


# ===========================================================================
# §3.4 - Cita
# ===========================================================================
class Caracter(str, Enum):
    """
    Que hace la FUENTE con lo que dice. Cinco valores, no cuatro: `h_o` no es
    ninguno de los otros -- es una aproximacion con limite de validez expreso,
    y meterla en DEFINICION borra precisamente lo que NOR-HDS-05 obliga a
    conservar.
    """
    EXIGENCIA = "exigencia"
    RECOMENDACION = "recomendacion"
    PERMISO = "permiso"
    DEFINICION = "definicion"
    APROXIMACION = "aproximacion"


class MetodoDeVerificacion(str, Enum):
    """
    Con que se leyo. Existe porque tres hallazgos ya cerrados se decidieron
    sobre IMAGEN y no sobre texto: el `>` de la ultima columna de F_pga, el
    asterisco de la fila F y el `[1 -]` del denominador de K_AE. Una cita
    verificada por extraccion de texto donde hacia falta renderizar no esta
    verificada, y el campo obliga a decirlo.
    """
    TEXTO = "texto"
    IMAGEN = "imagen renderizada"
    AMBOS = "ambos"


@dataclass(frozen=True)
class Verificado:
    fecha: str
    por: str
    sha1_pdf: str
    metodo: MetodoDeVerificacion

    def __post_init__(self) -> None:
        if not self.sha1_pdf.strip():
            raise ErrorDeRegistro(
                "Verificado exige `sha1_pdf`: contra QUE archivo exacto. Sin "
                "el, el dia que el PDF cambie la firma seguira diciendo que "
                "si y nadie se enterara")


@dataclass(frozen=True)
class ReferenciaNormativa:
    """
    El PUENTE de la migracion (§10.2 d). `Verificacion.numeral` es hoy un
    `str` y decenas de tests hacen `numeral in memoria`. Una `Cita` no es un
    `str` -- es un objeto rico --, pero expone esto, que si lo es, y ademas
    mantiene separadas las dos mitades que el proyecto ya separaba.
    """
    seccion_hoja_ruta: str
    numeral_norma: str
    cita_id: str = ""

    def __str__(self) -> str:
        return self.numeral_norma


@dataclass(frozen=True)
class Cita:
    """
    UNA cita, con id estable, referenciada desde donde haga falta (D1).

    Es lo unico que hace que NOR-PUE-01 sea *una* correccion y no seis: el
    numeral 2.1.4.3.9 estaba escrito en seis archivos como seis cadenas
    independientes que casualmente coincidian.

    `titulo_numeral` es obligatorio y VERBATIM, y es el campo que hace que la
    cita se caiga sola: quien la rellene tiene que abrir la pagina y copiar el
    encabezado -- y entonces lee "Aparatos de Apoyo".
    """
    id: str
    fuente_id: str
    numeral: str
    titulo_numeral: Union[str, PorTranscribir]
    pagina_impresa: str
    pagina_pdf: Union[int, PorTranscribir]
    texto_literal: Union[Verbatim, PorTranscribir]
    caracter: Caracter
    # DONDE SE IMPRIME EL ENCABEZADO, que no siempre es donde se imprime el
    # valor: el num. 4.1.1.3.6 abre en la pag. impresa 74 y su Tabla Nº 10
    # esta en la 76. Sin este campo, T3 buscaria el titulo en la pagina del
    # valor y fallaria en toda cita cuyo numeral abarque mas de una pagina --
    # que son casi todas. Vacio significa «en la misma que el valor».
    pagina_pdf_titulo: Union[int, PorTranscribir, None] = None
    # LOS ENCABEZADOS DE LOS QUE CUELGA, literales y de fuera adentro. Es lo
    # mismo que `FilaDeTabla.jerarquia` y por la misma razon: la pagina imprime
    # «c)  Socavación local a la salida de la alcantarilla» y, tres renglones
    # mas arriba, «4.1.1.3.7  Consideraciones para el diseño». Unirlos en una
    # cadena produce una frase que no esta en el PDF y que un revisor no
    # encuentra; separarlos deja las dos buscables.
    jerarquia_numeral: Tuple[str, ...] = ()
    condiciones: Tuple["CondicionAplicacion", ...] = ()
    verificado: Optional[Verificado] = None
    interpretacion: Optional[Interpretacion] = None
    corresponde_en: Tuple[str, ...] = ()
    derivado_de: str = ""
    nota: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.caracter, Caracter):
            raise ErrorDeRegistro(
                f"Cita {self.id}: `caracter` es obligatorio y es un Caracter")
        if self.verificado is not None and self.tiene_pendientes:
            raise ErrorDeRegistro(
                f"Cita {self.id}: lleva POR_TRANSCRIBIR y `verificado` a la "
                "vez (T22). Lo pendiente de leer no puede firmarse como "
                "verificado")
        if isinstance(self.interpretacion, Interpretacion):
            texto = self.texto_literal
            if isinstance(texto, Verbatim) and \
                    self.interpretacion.texto in texto.texto:
                raise ErrorDeRegistro(
                    f"Cita {self.id}: la interpretacion esta serializada "
                    "dentro del texto literal (T7). Va en su campo, aparte")

    @property
    def tiene_pendientes(self) -> bool:
        return any(esta_por_transcribir(v) for v in
                   (self.titulo_numeral, self.pagina_pdf, self.texto_literal))

    @property
    def campos_pendientes(self) -> Tuple[str, ...]:
        nombres = ("titulo_numeral", "pagina_pdf", "texto_literal")
        return tuple(n for n in nombres
                     if esta_por_transcribir(getattr(self, n)))

    @property
    def pagina_del_titulo(self) -> Union[int, PorTranscribir]:
        """Donde buscar el `titulo_numeral`. Ver el campo homonimo."""
        return self.pagina_pdf if self.pagina_pdf_titulo is None \
            else self.pagina_pdf_titulo

    @property
    def referencia(self) -> ReferenciaNormativa:
        return ReferenciaNormativa(seccion_hoja_ruta="",
                                   numeral_norma=self.numeral,
                                   cita_id=self.id)

    def como_texto(self) -> str:
        """
        La cita en una linea, como la imprime una memoria. La compone ESTA
        funcion y no un campo: el " · " que une los trozos es del proyecto, y
        buscar la linea compuesta en el PDF no la encontraria.
        """
        trozos = [f"num. {self.numeral}"]
        if self.jerarquia_numeral:
            trozos.append(" > ".join(self.jerarquia_numeral))
        if not esta_por_transcribir(self.titulo_numeral):
            trozos.append(f"'{self.titulo_numeral}'")
        trozos.append(f"pag. impresa {self.pagina_impresa}")
        if not esta_por_transcribir(self.pagina_pdf):
            trozos.append(f"PDF {self.pagina_pdf}")
        if self.verificado is None:
            trozos.append("[cita NO verificada]")
        return " · ".join(trozos)


# ===========================================================================
# §3.5 - CondicionAplicacion
# ===========================================================================
@dataclass(frozen=True)
class PorExpresion:
    """La evalua el consumidor: "HW/D >= 1.2" son dos numeros que ya tiene."""
    expresion: str
    simbolos: Tuple[str, ...]


@dataclass(frozen=True)
class PorCriterio:
    """
    La CLAVE del criterio, nunca el objeto. El registro no importa
    `criterios_adoptados`: la resolucion es tardia y la hace el consumidor.
    Es lo que impide el ciclo de dependencias.
    """
    clave: str


@dataclass(frozen=True)
class PorDatoDeSitio:
    clave: str


@dataclass(frozen=True)
class NoEvaluable:
    """
    `que_lo_cerraria` es obligatorio: un "no se puede" sin salida declarada es
    una excusa; con salida, es una deuda con direccion.
    """
    por_que: str
    que_lo_cerraria: str

    def __post_init__(self) -> None:
        if not self.que_lo_cerraria.strip():
            raise ErrorDeRegistro(
                "NoEvaluable exige `que_lo_cerraria`: el procedimiento "
                "concreto que si la resolveria")


Resolucion = Union[PorExpresion, PorCriterio, PorDatoDeSitio, NoEvaluable]


class Efecto(str, Enum):
    BLOQUEA = "bloquea"
    ADVIERTE = "advierte"
    EXCLUYE = "excluye"


@dataclass(frozen=True)
class CondicionAplicacion:
    """
    D4 hecho valor por defecto: `efecto_si_indeterminada = BLOQUEA`, y
    desviarse EXIGE texto. No hay "asumir".

    Dentro de una misma cita puede haber condiciones de los dos tipos, y una
    `NoEvaluable` NO contagia a las otras: extender a la segunda condicion una
    imposibilidad que solo valia para la primera fue el defecto que la
    auditoria adversarial destapo en NOR-HDS-05.
    """
    id: str
    texto: Verbatim
    cita_id: str
    resuelve: Resolucion
    efecto_si_indeterminada: Efecto = Efecto.BLOQUEA
    justificacion_de_no_bloquear: str = ""

    def __post_init__(self) -> None:
        if self.efecto_si_indeterminada is not Efecto.BLOQUEA and \
                not self.justificacion_de_no_bloquear.strip():
            raise ErrorDeRegistro(
                f"Condicion {self.id}: efecto {self.efecto_si_indeterminada} "
                "sin `justificacion_de_no_bloquear` (T15). Advertir no puede "
                "ser la salida comoda")


# ===========================================================================
# §4 - Los tres ejes de «parcial»
# ===========================================================================
@dataclass(frozen=True)
class Integra:
    """
    La tabla impresa esta ENTERA en el registro. Es una afirmacion sobre el
    PDF, no una etiqueta: si apareciera una fila mas, lo que esta mal es la
    transcripcion y el campo pasa a `Acotada`.
    """


@dataclass(frozen=True)
class Acotada:
    razon: str
    que_queda_fuera: str
    donde_leerlo: str

    def __post_init__(self) -> None:
        for campo in ("razon", "que_queda_fuera", "donde_leerlo"):
            if not getattr(self, campo).strip():
                raise ErrorDeRegistro(
                    f"Acotada exige `{campo}` (T12): es lo que separa "
                    "«acotada» de «podada»")


Alcance = Union[Integra, Acotada]


@dataclass(frozen=True)
class Usada:
    por: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.por:
            raise ErrorDeRegistro("Usada exige al menos un consumidor")


@dataclass(frozen=True)
class NoUsada:
    """
    NO es un defecto, nunca. Es informacion, y `por_que_no` es lo que la
    ventana pinta en el sitio donde nace la duda: asi «completa pero de uso
    parcial» no se declara con una etiqueta, se declara CONTESTANDO la
    pregunta.
    """
    por_que_no: str

    def __post_init__(self) -> None:
        if not self.por_que_no.strip():
            raise ErrorDeRegistro(
                "NoUsada exige `por_que_no` (T12). Una columna sin razon "
                "declarada no compila el registro")


@dataclass(frozen=True)
class PendienteDeCondicion:
    """
    Distinto de `NoUsada`, y la distincion es el fondo de §4.1: alli la
    decision esta tomada y razonada; aqui FALTA UN DATO y el calculo se
    detiene. Confundirlas hace imposible declarar la primera sin parecer que
    se esconde la segunda.
    """
    condicion_id: str


UsoEnCalculo = Union[Usada, NoUsada, PendienteDeCondicion]


@dataclass(frozen=True)
class Laguna:
    """
    Lo que la FUENTE MISMA deja sin cubrir. Ni transcripcion incompleta (eje A)
    ni uso parcial (eje B): un hueco del texto impreso. La Tabla 4.4 de E.060
    imprime la fila severa como "< 2,0 %" y la muy severa como "2,0 % <": el
    2,0 % exacto no cae en ninguna.

    Sin este tercer eje, una laguna se disfraza de fila -- que es como un `>=`
    del codigo termina decidiendo en silencio lo que la norma calla.
    """
    que_no_cubre: str
    con_que_regla: str
    quien_lo_cierra: Optional[str] = None
    si_nadie_lo_cierra: Efecto = Efecto.BLOQUEA


# ===========================================================================
# §7 - Los tres «rangos». Familia cerrada; la semantica ES el tipo
# ===========================================================================
class QuePasaFuera(str, Enum):
    INCUMPLE_LA_NORMA = "incumple"
    SALE_DEL_DOMINIO = "dominio"
    DEJA_DE_SER_DEFENDIBLE = "indefendible"
    LA_FUENTE_NO_SE_PRONUNCIA = "no_cubierto"


@dataclass(frozen=True)
class IntervaloAdmisible:
    """Un piso Y un techo, los dos escritos por la fuente."""
    minimo: float
    maximo: float
    unidad: str
    cita_id: str
    que_pasa_fuera: QuePasaFuera
    rotulo_obligatorio: str = ("La fuente escribe un MINIMO y un MAXIMO para "
                               "esta fila.")


@dataclass(frozen=True)
class TechoUnico:
    maximo: float
    unidad: str
    cita_id: str
    que_pasa_fuera: QuePasaFuera
    rotulo_obligatorio: str = "La fuente escribe un MAXIMO admisible."


@dataclass(frozen=True)
class PisoUnico:
    minimo: float
    unidad: str
    cita_id: str
    que_pasa_fuera: QuePasaFuera
    rotulo_obligatorio: str = "La fuente escribe un MINIMO exigible."


@dataclass(frozen=True)
class ConjuntoDeMaximos:
    """
    n valores, y NINGUNO es un piso. NO TIENE atributo `minimo`: una ventana
    no tiene que enlazar a la casilla "desde", y por eso no puede pintar 3.0
    como minimo (NOR-HID-04).

    Una tupla de UN elemento es la forma normal, no un caso especial: la fila
    "Mamposteria de piedra y concreto" de la Tabla N 10 trae un solo numero, y
    escribirla (2.0, 2.0) inventaba un par que la fuente no escribe
    (NOR-HID-07).
    """
    valores: Tuple[float, ...]
    unidad: str
    cita_id: str
    que_pasa_fuera: QuePasaFuera
    rotulo_obligatorio: str = ("Todos los valores de esta fila son MAXIMOS "
                               "admisibles; ninguno es un piso.")

    def __post_init__(self) -> None:
        if not self.valores:
            raise ErrorDeRegistro("ConjuntoDeMaximos sin valores")


@dataclass(frozen=True)
class BandaDeInterpolacion:
    """
    Puntos entre los que la fuente MANDA interpolar. No es un intervalo
    admisible: los extremos no acotan un valor, lo definen por tramos.
    """
    puntos: Tuple[Tuple[float, float], ...]
    unidad_abscisa: str
    unidad: str
    cita_id: str
    que_pasa_fuera: QuePasaFuera
    rotulo_obligatorio: str = ("La fuente manda INTERPOLAR linealmente entre "
                               "estos puntos.")


RangoNormativo = Union[IntervaloAdmisible, TechoUnico, PisoUnico,
                       ConjuntoDeMaximos, BandaDeInterpolacion]

ROTULOS_DE_RANGO = {
    "normativo": "La tabla normativa acota este valor.",
    "dominio_fisico": ("Fuera de esto, la celda esta mal llenada. NO es "
                       "normativo."),
    "sensibilidad": ("Adopcion del proyectista; se defiende mostrando el "
                     "resultado en los extremos."),
}


# ===========================================================================
# §3.7 - Celdas
# ===========================================================================
class CeldaSinValor(str, Enum):
    """
    Unifica tres marcas que hoy son TRES tipos de Python distintos para la
    misma clase de cosa: `"*"` (str), `None` (NoneType) y `"--"` (str). Con
    `None` entre ellas, un consumidor descuidado escribe `valor or 0.0` y
    convierte «la fuente dice que aqui no hay factor» en un cero.
    """
    EXIGE_ESTUDIO = "*"
    NO_APLICA = "N/A"
    NO_PARTICIPA = "--"
    NO_IMPRESO = ""
    REMITE_A_OTRA_TABLA = "->"


Celda = Union[float, int, str, CeldaSinValor, RangoNormativo]


@dataclass(frozen=True)
class ColumnaDeTabla:
    id: str
    etiqueta_literal: str
    unidad: str
    uso: UsoEnCalculo


@dataclass(frozen=True)
class FilaDeTabla:
    """
    `jerarquia` SEPARADA de la celda, y con profundidad arbitraria. No es
    normalizacion por gusto: la celda del reposo dice "En reposo.", no
    "EH: Presion Horizontal de la tierra -- En reposo.", y unirlas convertiria
    una frase compuesta aqui en una transcripcion que un revisor no encuentra
    en el PDF.

    Sin profundidad arbitraria no alcanza: la fila `metal_corrugado_subdren`
    de la Tabla N 09 cuelga de TRES encabezados antes de llegar a su celda.
    """
    id: str
    etiqueta_literal: str
    valores: Dict[str, Celda]
    uso: UsoEnCalculo
    jerarquia: Tuple[str, ...] = ()
    condiciones: Tuple[CondicionAplicacion, ...] = ()
    llamadas_a_nota: Tuple[str, ...] = ()

    def legible(self, union: str = " -- ") -> str:
        """
        Grupo(s) y celda en una linea. La compone esta funcion, no el dato: el
        separador es del proyecto. Buscar la linea compuesta en el PDF no la
        encontraria; buscar cualquiera de sus trozos, si.
        """
        return union.join((*self.jerarquia, self.etiqueta_literal))


@dataclass(frozen=True)
class NotaAlPie:
    marca: str
    texto: Verbatim


# ===========================================================================
# §5 - Modificadores
# ===========================================================================
class OrdenDeAplicacion(str, Enum):
    """
    EL campo que puede invertir que norma gobierna, y por eso es obligatorio y
    no tiene valor por defecto.

        ANTES:   max(76.2 * 0.8, 70.0) = max(60.96, 70.0) = 70.0  -> gana E.060
        DESPUES: max(76.2, 70.0) * 0.8 = 76.2 * 0.8      = 60.96  -> gana AASHTO

    Los dos son "aplicar el 0,8", y difieren en 9 mm y en QUE NORMA queda
    citada en la memoria.
    """
    ANTES_DE_CRUZAR_FUENTES = "antes"
    DESPUES_DE_CRUZAR = "despues"


@dataclass(frozen=True)
class TramoDeModificador:
    condicion: CondicionAplicacion
    factor: float
    etiqueta_literal: str


@dataclass(frozen=True)
class Modificador:
    """
    Actua SOBRE celdas, no ES una celda: vive en `TablaNormativa.modificadores`
    y no en `filas`. Si fuera una fila mas, el usuario elegiria entre 0.8 y
    76.2 como si fueran alternativas.

    `piso` es del modificador y no una constante suelta: separarlos permitiria
    aplicar uno sin el otro.
    """
    id: str
    cita_id: str
    concepto: str
    texto: Verbatim
    sobre_que: str
    tramos: Tuple[TramoDeModificador, ...]
    orden: OrdenDeAplicacion
    piso: Optional[Tuple[float, str]] = None
    tope: Optional[Tuple[float, str]] = None
    lagunas: Tuple[Laguna, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.orden, OrdenDeAplicacion):
            raise ErrorDeRegistro(
                f"Modificador {self.id}: `orden` es obligatorio (T16)")
        if not self.tramos:
            raise ErrorDeRegistro(f"Modificador {self.id}: sin tramos")


# ===========================================================================
# §3.6 - TablaNormativa
# ===========================================================================
@dataclass(frozen=True)
class TablaNormativa:
    id: str
    cita_id: str
    titulo_literal: str
    columnas: Tuple[ColumnaDeTabla, ...]
    filas: Tuple[FilaDeTabla, ...]
    alcance: Alcance
    encabezados_superiores: Tuple[str, ...] = ()
    texto_previo: Optional[Verbatim] = None
    notas_al_pie: Tuple[NotaAlPie, ...] = ()
    modificadores: Tuple[Modificador, ...] = ()
    fuente_declarada_por_la_tabla: str = ""
    lagunas: Tuple[Laguna, ...] = ()
    erratas: Tuple[str, ...] = ()
    afirmaciones_negativas: Tuple[AfirmacionNegativa, ...] = ()
    interpretacion: Optional[Interpretacion] = None
    vistas_de_calculo: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        ids_columna = {c.id for c in self.columnas}
        for fila in self.filas:
            sobra = set(fila.valores) - ids_columna
            if sobra:
                raise ErrorDeRegistro(
                    f"Tabla {self.id}, fila {fila.id}: columnas que la tabla "
                    f"no declara: {sorted(sobra)}")

    # -- vistas derivadas (D2): la vista de calculo se DERIVA, no se copia --
    def columna(self, id_columna: str) -> ColumnaDeTabla:
        for c in self.columnas:
            if c.id == id_columna:
                return c
        raise KeyError(f"{self.id}: no hay columna «{id_columna}»")

    def fila(self, id_fila: str) -> FilaDeTabla:
        for f in self.filas:
            if f.id == id_fila or f.id.endswith("#" + id_fila):
                return f
        raise KeyError(f"{self.id}: no hay fila «{id_fila}»")

    def clave_corta(self, fila: FilaDeTabla) -> str:
        return fila.id.split("#")[-1]

    def pares(self, col_a: str, col_b: str) -> Dict[str, Tuple[Celda, Celda]]:
        self.columna(col_a), self.columna(col_b)
        return {self.clave_corta(f): (f.valores[col_a], f.valores[col_b])
                for f in self.filas
                if col_a in f.valores and col_b in f.valores}

    def columna_como_dict(self, id_columna: str) -> Dict[str, Celda]:
        self.columna(id_columna)
        return {self.clave_corta(f): f.valores[id_columna]
                for f in self.filas if id_columna in f.valores}

    def rotulo_de_completitud(self) -> str:
        """
        La frase que ve el revisor no puede contradecir a los campos porque ES
        los campos.
        """
        usadas_col = sum(1 for c in self.columnas if isinstance(c.uso, Usada))
        usadas_fil = sum(1 for f in self.filas if isinstance(f.uso, Usada))
        cabeza = ("Tabla completa" if isinstance(self.alcance, Integra)
                  else "Transcripcion acotada")
        return (f"{cabeza} · el calculo usa {usadas_col} de "
                f"{len(self.columnas)} columnas y {usadas_fil} de "
                f"{len(self.filas)} filas")


@dataclass(frozen=True)
class CorrespondenciaDeTablas:
    """
    Dos transcripciones del MISMO original que no se pueden cruzar por nombre.
    El Manual traduce "shafts" por "Pilares" donde AASHTO dice "pilote", y
    ademas parte en dos una fila.

    Ya costo un defecto real: el cruce se hacia con `situacion in
    RECUBRIMIENTO_MP_MM`, daba False para las 8 filas de la familia de pilotes
    y SE SALTABA SIN AVISAR. INVARIANTE T19: toda fila de `tabla_a` tiene
    entrada en `pares`; una fila sin correspondencia declarada es un ERROR, no
    un salto callado.
    """
    id: str
    tabla_a: str
    tabla_b: str
    pares: Dict[str, Tuple[str, ...]]
    regla_al_cruzar: str
    diferencias_declaradas: Tuple[str, ...] = ()


# ===========================================================================
# §3.10 - Fundamento
# ===========================================================================
class Verbo(str, Enum):
    OBLIGA = "obliga"
    RECOMIENDA = "recomienda"
    PERMITE = "permite"
    DEFINE = "define"


class EstadoFundamento(str, Enum):
    VIGENTE = "vigente"
    DIFERIDO = "diferido"
    ABIERTO = "abierto"


VERBO_COMPATIBLE_CON = {
    Verbo.OBLIGA: (Caracter.EXIGENCIA,),
    Verbo.RECOMIENDA: (Caracter.RECOMENDACION, Caracter.APROXIMACION),
    Verbo.PERMITE: (Caracter.PERMISO,),
    Verbo.DEFINE: (Caracter.DEFINICION, Caracter.APROXIMACION),
}


@dataclass(frozen=True)
class Fundamento:
    """
    INVARIANTE T11: `verbo` compatible con el `caracter` de sus citas.
    `OBLIGA` exige al menos una cita EXIGENCIA. Es lo que impide escribir
    «la norma obliga a…» sobre el parrafo que dice «recomendandose que la
    velocidad minima sea igual a 0.25 m/s».
    """
    id: str
    fase: str
    que_paso: str
    por_que: str
    verbo: Verbo
    citas: Tuple[str, ...]
    que_pasa_si_no_se_hace: str
    estado: EstadoFundamento = EstadoFundamento.VIGENTE

    def __post_init__(self) -> None:
        if not self.citas:
            raise ErrorDeRegistro(
                f"Fundamento {self.id}: al menos una cita")


# ===========================================================================
# §3.11 - Discrepancia
# ===========================================================================
class EstadoDiscrepancia(str, Enum):
    ABIERTA_CONTRA_HOJA_DE_RUTA = "abierta_contra_hoja_de_ruta"
    ABIERTA = "abierta"
    RESUELTA = "resuelta"
    ERRATA_DE_IMPRENTA = "errata_de_imprenta"


@dataclass(frozen=True)
class Parte:
    quien: str
    que_dice: str
    cita_id: str = ""


@dataclass(frozen=True)
class Discrepancia:
    """
    El objeto que `CLAUDE.md` ya exigia y no tenia donde vivir.

    La regla obliga, cuando la fuente primaria gana a la hoja de ruta, a hacer
    TRES cosas: declararlo en el punto de uso, reportar el defecto contra la
    hoja de ruta, y dejar dicho que la hoja de ruta SIGUE MAL mientras no se
    corrija. Hoy eso se cumple en prosa, en bloques de comentario, y por tanto
    no es enumerable ni imprimible ni testeable: la obligacion tercera no
    tiene donde vivir salvo en la memoria de quien la escribio.
    """
    id: str
    objeto: str
    partes: Tuple[Parte, ...]
    gana: str
    por_que: str
    efecto_si_se_sigue_la_otra: str
    estado: EstadoDiscrepancia

    def __post_init__(self) -> None:
        if len(self.partes) < 2:
            raise ErrorDeRegistro(
                f"Discrepancia {self.id}: hacen falta al menos dos partes")
        if self.gana not in {p.quien for p in self.partes}:
            raise ErrorDeRegistro(
                f"Discrepancia {self.id}: `gana` ({self.gana}) no es ninguna "
                f"de las partes declaradas")
