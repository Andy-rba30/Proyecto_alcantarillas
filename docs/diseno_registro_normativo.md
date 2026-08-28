# Diseño del registro normativo — `src/normativa/`

**Sesión S11 de `docs/hoja_de_ruta_correcciones_v12.md`. Diseño, sin implementación.**
Lo implementa S12 (clusters C11, C12, C02); lo consumen S15 (modos de resolución),
S17 (la ventana) y S18 (la memoria sustentada).

> **Qué es este documento y qué no es.** Es el esquema que S12 tiene que poder
> implementar sin volver a decidir nada de fondo. **No** transcribe ninguna tabla
> nueva ni verifica ninguna cita contra ningún PDF: los dos ejemplos de la §11
> reproducen transcripciones que ya viven en `src/constantes_normativas.py` y llevan
> su campo `verificado` **vacío a propósito**, porque rellenarlo sin abrir el PDF
> sería cometer, dentro del diseño que existe para impedirlas, exactamente la falta
> que persigue.

---

## 0. El problema, dicho como restricción de diseño

La §2 del plan lo enuncia: hoy la norma vive en el repositorio como **prosa**. Pero
para diseñar hace falta la forma fuerte de esa frase, que es esta:

> **Una cita en prosa no tiene identidad.** El numeral `2.1.4.3.9` está hoy escrito en
> **seis archivos** —`constantes_normativas.py`, `M9_cabezal.py`, `test_M9_cabezal.py`,
> `manifiesto_citas.md` y las dos hojas de ruta— como seis cadenas independientes que
> casualmente coinciden. Cuando `NOR-PUE-01` descubrió que ese numeral es «Aparatos de
> Apoyo», no había *una* cosa que corregir: había seis, y nada que garantizara que se
> corrigieran las seis.

De ahí salen las tres propiedades que el registro tiene que dar, y que ordenan todo
lo demás:

| | Propiedad | Qué la hace posible |
|---|---|---|
| **P1** | **Identidad.** Cada cita es UN objeto con un id estable, referenciado desde donde haga falta | `Cita` internada en `citas.py`, nunca reescrita |
| **P2** | **Verificabilidad.** Un test puede decidir si la cita es cierta sin criterio humano | `texto_literal` verbatim + `pagina_pdf` + `sha1` de la fuente |
| **P3** | **Exhibibilidad.** La ventana puede pintarla entera sin saber nada de normas | Tabla completa, con notas, condiciones y modificadores, en el objeto |

Y una cuarta que no está en el plan y que las tres primeras hacen inevitable:

| | | |
|---|---|---|
| **P4** | **No representabilidad de la lectura falsa.** Lo que no se debe leer de la fuente no debe poder construirse | Familias cerradas de tipos, en vez de un campo `tipo: str` |

P4 es la diferencia entre un esquema que *documenta* el error de `NOR-HID-04` y uno que
lo **impide**. Un objeto con `minimo` y `maximo` y una etiqueta que dice «los dos son
máximos» se va a pintar en una ventana con una casilla «desde» y otra «hasta», porque
los campos existen y la ventana los va a encontrar. Un objeto que **no tiene** atributo
`minimo` no se puede pintar así.

---

## 1. Inventario medido, sobre `origin/main`

El prompt de S11 dice «18 tablas, 26 escalares». Medido con `ast` sobre
`src/constantes_normativas.py` (2 355 líneas):

| Clase de nombre a nivel de módulo | Cuenta |
|---|---|
| Escalares numéricos | **37** |
| Colecciones (`dict` / `list` / `tuple`) | **50** |
| Cadenas y otros (títulos, numerales, textos literales, notas, erratas) | **125** |
| Funciones | 1 (`fila_gamma_p_legible`) |
| **Total** | **213** |

De las 50 colecciones, **entre 18 y 23 son tablas normativas** según qué se cuente como
tabla: `FS` es un cuadro compuesto por cinco artículos distintos de E.050,
`CAMA_RELLENO_LATERAL` es una ficha por material y no una tabla impresa,
`EXCENTRICIDAD_ADMISIBLE_FRACCION_B` son dos puntos de una interpolación. **Que el
número no se pueda dar exacto sin decidir antes qué es una tabla es el primer hallazgo
del inventario**, y el registro tiene que zanjarlo: es `TablaNormativa` lo que la
fuente **imprime como tabla, con título propio**; lo demás son `RangoNormativo`,
`Escalar` o `Fundamento`, aunque en Python hoy sean todos `dict`.

Las 125 cadenas son títulos, numerales, notas al pie, textos literales, condiciones y
declaraciones de errata. **Ninguna entra en una fórmula.** Unas pocas viajan a la memoria
(los `NUMERAL_*`, y siete textos que `M9` invoca por `condicion_normativa_cabezal`); del
resto, el propio archivo dice: «no lo invoca nadie: es la parte de la transcripción que
existe para que la cita sea verificable contra el PDF. No es código muerto, es la cita».
Esas 125 son, literalmente, el registro normativo escrito sin esquema.

**El registro no inventa una capa nueva: le da forma a una que ya está escrita.**

---

## 2. Cinco decisiones que gobiernan el resto

Todo el esquema de la §3 se deduce de estas cinco. Se ponen delante para que S12 pueda
resolver por sí sola cualquier caso que la §3 no anticipe.

> **D1 — La cita es un objeto interno, no un texto.**
> Un `Cita` se define una vez en `citas.py` con un id estable y se referencia por id.
> Ningún módulo escribe un numeral, una página o un título de tabla como literal. Es la
> forma dura de la R2 del plan y lo único que hace que `NOR-PUE-01` sea *una* corrección
> y no seis.

> **D2 — La transcripción y la vista de cálculo son dos cosas, y la segunda se deriva de
> la primera.**
> No es una idea nueva: el repositorio ya lo hace en tres sitios
> (`MANNING` desde `TABLA_09_FILAS`, `V_MAX` desde `TABLA_10_FILAS`, `RIESGO_ADMISIBLE`
> desde `TABLA_02_FILAS`) y explica por qué — «si la transcripción se corrige, esta
> vista se corrige con ella y no quedan dos copias que puedan divergir». **El registro
> generaliza ese patrón a las 18-23 tablas, y ese es también el camino de migración**
> (§10).

> **D3 — Lo que la fuente dice y lo que el proyecto hace con ello son campos distintos,
> siempre.**
> Ya existe en `UMBRALES_DE_VERIFICACION` como `caracter` / `aplicacion`. El registro lo
> sube a invariante: `caracter` pertenece a la `Cita` (es un hecho del documento) y
> `aplicacion` pertenece al consumidor (es una decisión del proyecto). Un valor no puede
> viajar sin los dos.

> **D4 — Lo indeterminado bloquea; el que no bloquee es lo que hay que justificar.**
> R4 del plan, invertida. El campo por defecto de una condición no evaluable es
> `bloquea`. `advierte` existe, pero exige `justificacion_de_no_bloquear`. No hay
> «asumir».

> **D5 — Cuando una lectura falsa sea posible, se elimina el tipo que la permite.**
> P4. En la práctica: familias cerradas de tipos (`RangoNormativo`, `TextoDeFuente`,
> `CeldaSinValor`) y ninguna tabla de despacho de la ventana con caso por defecto. Una
> forma nueva de rango obliga a escribir su renderizador; no cae en el genérico.

---

## 3. El esquema

Los tipos viven en `src/normativa/esquema.py`. `src/modelos.py` los **reexporta**, para
que la regla de `CLAUDE.md` («los tipos que fluyen entre módulos están en `modelos.py`»)
siga cumpliéndose en el punto de importación sin partir en dos la definición.

Dirección de dependencias, que hay que respetar para no crear un ciclo:

```
normativa/  ←  constantes_normativas.py  ←  criterios_adoptados.py  ←  módulos M0..M11
    ↑
  (nadie de la izquierda importa nada de la derecha)
```

**Consecuencia:** el registro conoce la **clave** del criterio que resuelve una
condición, nunca el objeto `Criterio`. La resolución es tardía y la hace el consumidor.

### 3.1 `Fuente` — y `Catalogo`, que no es una `Fuente`

```python
@dataclass(frozen=True)
class Fuente:
    id: str                     # "MC_HHD", "MP", "E060", "HDS5_3ED", "AASHTO_LRFD_9"
    titulo: str                 # nombre completo, como se cita en una memoria
    emisor: str                 # "MTC", "SENCICO/VIVIENDA", "FHWA", "AASHTO"
    edicion: str                # "3a ed., abril 2012", "9th Edition, 2020"
    anio: int
    resolucion: str             # "RD 20-2011-MTC/14", "RM 183-2026-VIVIENDA"; "" si no tiene
    archivo_pdf: Optional[str]  # ruta relativa dentro de normas/; None si `ausente`
    sha1: Optional[str]         # del archivo exacto contra el que se verificó
    paginacion: Paginacion      # ver §3.2 -- NO es un entero
    ausente: bool = False       # se cita y NO está en normas/ (§8)
    ausencia: Optional[Ausencia] = None     # obligatorio si ausente
    reemplaza_a: Optional[str] = None       # edición anterior que este PDF sustituye
    convive_con: Tuple[str, ...] = ()       # otras ediciones del MISMO documento en normas/
```

`convive_con` no es adorno: en `normas/` hay **dos** HDS-5 que no dicen lo mismo
(`hif12026.pdf`, 3.ª ed. 2012, y `fhwa_culvert_hydraulics_hds5si.pdf`, ed. 1985 rotulada
«SI»), y leer la segunda «en SI» reproduce el error del 29 imperial (+9,6 %). Hoy eso
vive en un comentario de 15 líneas. En el registro son dos `Fuente` distintas, con
`convive_con` cruzado y una `Discrepancia` (§3.11) que declara cuál gobierna.

**`Catalogo` es un tipo aparte, y esa separación es el cierre estructural de
`NOR-PRO-01` / `NOR-PRO-02`:**

```python
@dataclass(frozen=True)
class Catalogo:
    id: str                     # "CAT_TUBERIA_LOCAL"
    titulo: str
    proveedor_o_ambito: str
    que_norma_NO_lo_sostiene: str   # obligatorio y no vacío
```

**Invariante:** un `Catalogo` **no puede** ser el `fuente_id` de una `Cita`. Un tope de
catálogo no tiene numeral, y el sistema de tipos no le deja fingir que lo tiene. Es lo
que impide que `D_MAX` (2.70 / 2.10 / 1.50 m) vuelva a imprimirse atribuido a AASHTO
M170 y ASTM A760 —normas que tabulan hasta 3 600 mm— y descarte materiales en silencio
con una cita que ninguna norma sostiene.

### 3.2 `Paginacion` — por qué `desfase_pagina` no puede ser un entero

El plan pide un campo `desfase_pagina`. **Un entero no alcanza**, y se comprueba con los
datos que el propio repositorio ya trae:

| Fuente | Páginas impresas ↔ PDF que el repo declara | Regla |
|---|---|---|
| Manual de Puentes | 123→124 · 140→141 · 143→144 · 248→249 · 250→251 · 252→253 · 254→255 · 586→587 | corrida, **+1** |
| E.030 | 7→7 · 8→8 · 9→9 · 11→11 | corrida, **0** |
| EG-2013 | 912→920 | corrida, **+8** |
| HDS-5 3.ª ed. | 3.10→92 · 3.24→106 · 3.25→107 · A.2→191 · DG3.3→296 | **por capítulo**: base cap. 3 = 82, base ap. A = 189 |
| AASHTO LRFD 9.ª | 3-17→71 · 3-18→72 · 3-100→154 · 3-118→172 · 11-25→1494 · 11-27→1496 · 11-145→1614 | **por capítulo**: base cap. 3 = 54, base cap. 11 = 1469 |

Las dos últimas no numeran con enteros: `"3.24"`, `"A.8"`, `"11-145"`, `"DG3.3"` son
**etiquetas**, no números. De ahí dos decisiones:

```python
Paginacion = Union[Corrida, PorCapitulo, Irregular, SinDeterminar]

@dataclass(frozen=True)
class Corrida:
    desfase: int                        # pdf = impresa + desfase

@dataclass(frozen=True)
class PorCapitulo:
    base: Dict[str, int]                # {"3": 82, "A": 189, "DG": 293}
    patron: str                         # regex que parte "3.24" en ("3", 24)

@dataclass(frozen=True)
class Irregular:
    tabla: Dict[str, int]               # etiqueta impresa -> página PDF, una a una
    por_que: str                        # obligatorio: por qué no hay regla

@dataclass(frozen=True)
class SinDeterminar:
    por_que: str                        # "ninguna cita del repo declara su página PDF"
    # invariante: ninguna Cita a esta Fuente puede llevar `verificado`
```

`SinDeterminar` no es un hueco del esquema: es el estado real de **la fuente con más
citas del proyecto**. El Manual de Hidrología aparece en el repositorio con páginas
impresas (25, 72, 75, 76, 77, 79, 178) y **ni una sola página PDF**, de modo que hoy
ninguna de sus citas es verificable por la vía barata. Declararlo hace que se vea; con
un `desfase: int = 0` por defecto, no se vería.

- **`pagina_impresa` es `str`, no `int`.** `"3.24"` no es 3,24.
- **`pagina_pdf` es `int`, y sin ella no hay verificación posible.** Es la única que un
  test puede abrir. Mientras no se haya leído lleva `POR_TRANSCRIBIR` (§3.4), nunca un
  valor calculado a ojo desde el desfase.

Y con esto el desfase deja de ser documentación y pasa a ser **predicción testeable**:
dada la `Paginacion`, la `pagina_pdf` declarada tiene que ser la que la regla calcula.
Es el test T6 de la §9, y es el que cierra `MAT-O17` (páginas corridas 76→77, C.2→C.6,
2.14→2.10, 982→984) por construcción y no una por una.

### 3.3 `TextoDeFuente` — cuatro tipos, porque «literal» es una afirmación

Este es el punto donde el repositorio ya se tropezó **dos veces con el mismo pie**, y la
segunda es la que obliga a resolverlo con tipos y no con disciplina:

> `NOR-HID-06` se cerró en `00da460` (el título de la Tabla N° 10 recupera «(m/s)»).
> Y se **reabrió** en `76791d0`: el bloque `UMBRALES_DE_VERIFICACION`, construido para
> cerrarlo, rotulaba «Texto literal» dos composiciones que no lo eran —prosa del proyecto
> en `TR`, la tabla reformateada en `V3`—. *La corrección reintrodujo el defecto que
> cerraba.* Lo arregló partir el campo en `texto` (tupla de verbatim) y `transcripcion`.

Eso es la solución correcta, a medias: sigue dependiendo de que quien escriba elija bien
el campo. Con tipos, elegir mal es un error de construcción:

```python
class TextoDeFuente:  ...            # base sellada; no se instancia

@dataclass(frozen=True)
class Verbatim(TextoDeFuente):
    texto: str                       # EXACTO, con las erratas de la fuente
    pagina_pdf: int                  # dónde se leyó ESTA frase
    # invariante T2: `texto` normalizado tiene que aparecer en esa página

@dataclass(frozen=True)
class Transcripcion(TextoDeFuente):
    texto: str                       # datos de la fuente, reordenados por el proyecto
    de_donde: str                    # qué objeto del registro se reformateó
    # NO se busca en el PDF: no es una cita, y el rótulo lo dice

@dataclass(frozen=True)
class Interpretacion(TextoDeFuente):
    texto: str                       # lectura del proyectista
    en_contra: Tuple[str, ...]       # hechos de la fuente que juegan en contra
    a_favor: Tuple[str, ...]
    # invariante T7: nunca se serializa dentro de un campo de cita

@dataclass(frozen=True)
class AfirmacionNegativa(TextoDeFuente):
    que_no_dice: str                 # "la Tabla N° 09 no lista HDPE"
    ambito_barrido: str              # qué se leyó entero para poder afirmarlo
    # se verifica al revés: por ausencia sobre un ámbito declarado
```

`AfirmacionNegativa` no está en el plan y hace falta: el manifiesto ya registra cuatro
(«TMC y HDPE NO están listados en la Tabla N° 10», «HDPE no está en la Tabla N° 09»…) y
**son las que autorizan a saltar a un `[C]`**. Una afirmación negativa mal hecha abre la
puerta a cubrir con fuente externa un vacío que no existe —que es la forma exacta de
`NOR-VAC-01`, donde el «vacío verificado» de la cobertura mínima no era un vacío: AASHTO
12.6.6.3 lo tabulaba—. Necesita campo propio y método de verificación propio.

### 3.4 `Cita`

```python
@dataclass(frozen=True)
class Cita:
    id: str                         # "MP.2.4.2.2", "MC_HHD.T10", "HDS5.A.2.1.Ku"
    fuente_id: str
    numeral: str                    # "4.1.1.3.7 c)", "Tabla N° 09", "Ec. 3.4b", "Art. 22.10"
    titulo_numeral: Union[str, PorTranscribir]   # LITERAL del encabezado.
                                    # Es la trampa de NOR-PUE-01
    pagina_impresa: str             # "76", "3.24", "11-145"
    pagina_pdf: Union[int, PorTranscribir]
    texto_literal: Verbatim         # la frase que sostiene el valor
    caracter: Caracter              # enum; ver abajo
    condiciones: Tuple[CondicionAplicacion, ...] = ()
    verificado: Optional[Verificado] = None
    interpretacion: Optional[Interpretacion] = None
    corresponde_en: Tuple[str, ...] = ()   # ids de citas equivalentes en otra fuente

class Caracter(str, Enum):
    EXIGENCIA     = "exigencia"
    RECOMENDACION = "recomendacion"
    PERMISO       = "permiso"          # "puede ser reducido a 0.5 kh0"
    DEFINICION    = "definicion"
    APROXIMACION  = "aproximacion"     # h_o: fórmula con condición de uso expresa

@dataclass(frozen=True)
class Verificado:
    fecha: str                      # ISO
    por: str                        # "fase1/S12 · verificador-normativo"
    sha1_pdf: str                   # contra QUÉ archivo exacto
    metodo: str                     # "texto" | "imagen renderizada" | "ambos"
```

Cuatro decisiones dentro de este bloque:

1. **`titulo_numeral` es obligatorio y verbatim.** Es el campo que hace que
   `NOR-PUE-01` se caiga sola: quien rellene la cita de `h_eq` tiene que abrir la
   pág. 91 y copiar el encabezado, y lee «Aparatos de Apoyo».
2. **`caracter` tiene cinco valores, no cuatro.** El plan lista cuatro; `h_o` no es
   ninguno de ellos —es una aproximación con límite de validez expreso, y meterla en
   `definicion` borra precisamente lo que `NOR-HDS-05` obliga a conservar—.
3. **`metodo` existe porque tres hallazgos se decidieron sobre imagen y no sobre texto**:
   el signo `>` de la última columna de `F_pga`, el asterisco de la fila F, el `[1 −]`
   de `K_AE`. Una cita verificada por extracción de texto plano donde hacía falta
   renderizar no está verificada, y el campo obliga a decirlo.
4. **`verificado = None` es un estado legítimo y ruidoso**, no un hueco. La ventana lo
   pinta como «cita **no verificada**» y `M11` lo imprime igual.

**El sentinel `POR_TRANSCRIBIR`.** Los campos verbatim son obligatorios, y sin embargo la
transcripción de una fuente entera no cabe en una sesión. Un campo obligatorio que
alguien rellena «provisionalmente» con algo plausible es la fábrica de citas falsas. De
modo que hay **un** valor admisible para lo aún no leído —`POR_TRANSCRIBIR`, un centinela
único, no una cadena vacía ni un texto verosímil— con dos reglas:

- Una `Cita` con cualquier campo en `POR_TRANSCRIBIR` **no puede** llevar `verificado`, y
  la ventana la pinta como incompleta (T22).
- El número de `POR_TRANSCRIBIR` del registro **solo puede decrecer** (trinquete, T22).

Es la misma idea que el `valor=None` de `criterios_adoptados`, aplicada a la cita: *un
vacío se ve; una cita falsa se cree*.

### 3.5 `CondicionAplicacion`

```python
@dataclass(frozen=True)
class CondicionAplicacion:
    id: str
    texto: Verbatim                     # cómo la escribe la fuente
    cita_id: str                        # dónde la escribe
    resuelve: Resolucion                # familia cerrada; ver abajo
    efecto_si_indeterminada: Efecto = Efecto.BLOQUEA      # D4: por defecto, bloquea
    justificacion_de_no_bloquear: str = ""                # obligatorio si != BLOQUEA

Resolucion = Union[PorExpresion, PorCriterio, PorDatoDeSitio, NoEvaluable]

@dataclass(frozen=True)
class PorExpresion:
    expresion: str                      # "HW/D >= 1.2"; el consumidor la evalúa
    simbolos: Tuple[str, ...]           # magnitudes que necesita

@dataclass(frozen=True)
class PorCriterio:
    clave: str                          # "categoria_refuerzo_aashto"  (clave, no objeto)

@dataclass(frozen=True)
class PorDatoDeSitio:
    clave: str                          # "orientacion_muro_respecto_al_trafico"

@dataclass(frozen=True)
class NoEvaluable:
    por_que: str                        # qué haría falta y este programa no calcula
    que_lo_cerraria: str                # el procedimiento concreto que la resolvería

class Efecto(str, Enum):
    BLOQUEA  = "bloquea"     # CriterioPendienteError, por la vía que ya existe
    ADVIERTE = "advierte"    # se calcula, y la memoria del punto lo dice
    EXCLUYE  = "excluye"     # la fila/columna no aplica a esta obra
```

### 3.6 `TablaNormativa`

```python
@dataclass(frozen=True)
class TablaNormativa:
    id: str                             # "MC_HHD.T09"
    cita_id: str
    titulo_literal: str                 # COMPLETO, con unidades (NOR-HID-06)
    columnas: Tuple[ColumnaDeTabla, ...]
    filas: Tuple[FilaDeTabla, ...]
    alcance: Alcance                            # §4, eje A -- obligatorio, sin defecto
    encabezados_superiores: Tuple[str, ...] = ()   # F_pga tiene encabezado de dos niveles
    texto_previo: Optional[Verbatim] = None
    notas_al_pie: Tuple[NotaAlPie, ...] = ()
    modificadores: Tuple[Modificador, ...] = ()
    fuente_declarada_por_la_tabla: str = ""     # "Ven Te Chow, 1983"; "HCANALES"
    lagunas: Tuple[Laguna, ...] = ()            # §4, eje C
    erratas: Tuple[str, ...] = ()               # ids de Discrepancia (§3.11)
    vistas_de_calculo: Tuple[str, ...] = ()     # nombres derivados: "MANNING", "V_MAX"
```

`fuente_declarada_por_la_tabla` no es decorativo: la Tabla N° 09 y la N° 10 del Manual
del MTC **no son del MTC** (son de Ven Te Chow y de HCANALES). Una ventana que rotule
«Manual de Hidrología» sobre la tabla y calle su procedencia hace una atribución que la
página no hace.

### 3.7 `ColumnaDeTabla`, `FilaDeTabla`, `CeldaSinValor`

```python
@dataclass(frozen=True)
class ColumnaDeTabla:
    id: str
    etiqueta_literal: str               # "MÍNIMO", "PGA > 0.50", "Mínimo" (sic)
    unidad: str                         # "" si adimensional; explícita siempre
    uso: UsoEnCalculo                   # §4, eje B

@dataclass(frozen=True)
class FilaDeTabla:
    id: str                             # "MC_HHD.T09#concreto_tubo_recto"
    etiqueta_literal: str               # texto EXACTO de la celda, y solo de la celda
    valores: Dict[str, Celda]           # por id de columna; ver `Celda` abajo
    uso: UsoEnCalculo                   # obligatorio: §4, eje B
    jerarquia: Tuple[str, ...] = ()     # encabezados de los que cuelga, literales,
                                        # de fuera adentro. Profundidad arbitraria
    condiciones: Tuple[CondicionAplicacion, ...] = ()
    llamadas_a_nota: Tuple[str, ...] = ()      # "(*)", "(**)", "1", "2"

Celda = Union[float, str, CeldaSinValor, RangoNormativo]

class CeldaSinValor(str, Enum):
    EXIGE_ESTUDIO  = "*"       # el asterisco de la fila F de F_pga -> Nota 2
    NO_APLICA      = "N/A"     # la fuente dice que esa fila no tiene ese extremo
    NO_PARTICIPA   = "--"      # la carga no entra en esa combinación
    NO_IMPRESO     = ""        # la celda está en blanco en el original
```

`jerarquia` **separada de la celda** no es un capricho de normalización: la celda del
reposo dice `"En reposo."`, no `"EH: Presión Horizontal de la tierra — En reposo."`.
Unirlas convertiría una frase compuesta aquí en una transcripción, y un revisor que la
busque en el PDF no la encuentra. El repositorio ya lo resolvió así en
`TABLA_GAMMA_P_FILAS` (`grupo` / `subgrupo` / `fila`) + `fila_gamma_p_legible()`; el
registro lo hace regla y le quita el tope de dos niveles, porque **hay tablas con más**:
la fila de la Tabla N° 09 que el código llama `metal_corrugado_subdren` cuelga de tres
encabezados —`A. CONDUCTO CERRADO…` → `A.1 METÁLICOS` → `c. Metal corrugado`— antes de
llegar a la celda `sub-dren`. Con `grupo`/`subgrupo` habría que aplastar dos de los tres,
y hoy están los cuatro aplastados en una sola cadena.

La línea compuesta que la memoria imprime la produce `fila_legible()`, no el dato: el
`" — "` que une los niveles es del proyecto, y por eso vive en una función y no dentro de
una transcripción. Buscar la frase compuesta en el PDF no la encontraría; buscar
cualquiera de sus trozos, sí.

`CeldaSinValor` unifica tres marcas que hoy son **tres tipos de Python distintos** para
la misma clase de cosa: `F_PGA_EXIGE_ESTUDIO_DE_SITIO = "*"` (str),
`GAMMA_P_NO_APLICA = None` (NoneType) y `COMBINACION_NO_PARTICIPA = "--"` (str). Con
`None` entre ellas, un consumidor descuidado escribe `valor or 0.0` y convierte «la
fuente dice que aquí no hay factor» en un cero. El enum cierra esa puerta y obliga a un
`match` exhaustivo.

### 3.8 `Modificador` — ver §5

```python
@dataclass(frozen=True)
class Modificador:
    id: str
    cita_id: str
    concepto: str                       # "factor por relación agua-cemento"
    texto: Verbatim
    sobre_que: str                      # qué celdas multiplica, en palabras de la fuente
    tramos: Tuple[TramoDeModificador, ...]
    orden: OrdenDeAplicacion            # ← el campo que puede invertir qué norma gobierna
    piso: Optional[Tuple[float, str]] = None   # (valor, cita_id) que acota el resultado
    tope: Optional[Tuple[float, str]] = None
    lagunas: Tuple[Laguna, ...] = ()

@dataclass(frozen=True)
class TramoDeModificador:
    condicion: CondicionAplicacion
    factor: float
    etiqueta_literal: str               # "Para W/C <= 0.40 ... 0.8"

class OrdenDeAplicacion(str, Enum):
    ANTES_DE_CRUZAR_FUENTES  = "antes"   # se aplica sobre el valor de SU fuente
    DESPUES_DE_CRUZAR        = "despues"
```

### 3.9 `RangoNormativo` — familia cerrada, ver §7

```python
RangoNormativo = Union[IntervaloAdmisible, TechoUnico, PisoUnico,
                       ConjuntoDeMaximos, BandaDeInterpolacion]
```

Todos comparten `unidad`, `cita_id`, `que_pasa_fuera: QuePasaFuera` y
`rotulo_obligatorio: str`. **Ninguno tiene una base común instanciable ni un campo
`semantica: str`**: la semántica *es* el tipo.

### 3.10 `Fundamento`

```python
@dataclass(frozen=True)
class Fundamento:
    id: str
    fase: str                           # "Fase 5 / V2", "Fase 9.2"
    que_paso: str                       # qué se está haciendo
    por_que: str                        # por qué la norma lo obliga o lo recomienda
    verbo: Verbo                        # OBLIGA | RECOMIENDA | PERMITE | DEFINE
    citas: Tuple[str, ...]              # ids; al menos una
    que_pasa_si_no_se_hace: str
    estado: EstadoFundamento            # VIGENTE | DIFERIDO | ABIERTO
```

**Invariante fuerte, y es la que cierra la familia de `NOR-MEM-01`:** `verbo` tiene que
ser compatible con el `caracter` de sus citas. `OBLIGA` exige al menos una cita
`EXIGENCIA`; `RECOMIENDA` no puede sostenerse sobre una cita `EXIGENCIA` sin declararlo.
Es lo que impide escribir «la norma obliga a…» sobre el párrafo que dice
«recomendándose que la velocidad mínima sea igual a 0.25 m/s».

### 3.11 `Discrepancia` — el objeto que el plan no lista y `CLAUDE.md` ya exige

`CLAUDE.md` obliga, cuando la fuente primaria gana a la hoja de ruta, a hacer **tres**
cosas: declararlo en el punto de uso, reportar el defecto contra la hoja de ruta, y dejar
dicho que la hoja de ruta sigue mal mientras no se corrija. Hoy eso se cumple **en
prosa**, en tres bloques de comentario (`K_FRICCION_SI`, `H_RELLENO_MIN`,
`CICLOPEO_DISCREPANCIA_HOJA_RUTA`), y por tanto no es enumerable ni imprimible ni
testeable. Sin objeto, la obligación tercera —«sigue mal mientras no se corrija»— no
tiene dónde vivir salvo en la memoria de quien la escribió.

```python
@dataclass(frozen=True)
class Discrepancia:
    id: str
    objeto: str                         # qué está en disputa
    partes: Tuple[Parte, ...]           # cada una: (fuente_id | "hoja_de_ruta", qué dice, cita_id)
    gana: str                           # cuál de las partes, y por qué regla
    por_que: str
    efecto_si_se_sigue_la_otra: str     # cuantificado cuando se pueda
    estado: EstadoDiscrepancia          # ABIERTA_CONTRA_HOJA_DE_RUTA | RESUELTA | ERRATA_DE_IMPRENTA
```

Cubre de una vez: las **tres erratas de imprenta** de la cadena sísmica del Manual
(`K_AE`, el `1.2 k_h0` de roca, «tercio central» por *two-thirds*), las **dos ediciones
de HDS-5**, la **regla del mayor** entre E.060 y AASHTO, y las **discrepancias abiertas
contra la hoja de ruta v8** (los topes `D_MAX`, el `f'c` del ciclópeo, las remisiones a
A-807). Un test lista las `ABIERTA_CONTRA_HOJA_DE_RUTA` y M11 las imprime: la
obligación tercera de `CLAUDE.md` deja de depender de que alguien se acuerde.

### 3.12 Invariantes, en una tabla

| # | Invariante | Lo verifica |
|---|---|---|
| I1 | Todo `fuente_id` de una `Cita` resuelve a una `Fuente`; nunca a un `Catalogo` | T1 |
| I2 | `texto_literal` normalizado aparece en `pagina_pdf` del PDF con el `sha1` declarado | T2 |
| I3 | `titulo_numeral` aparece en esa misma página, junto al `numeral` | T3 |
| I4 | El valor que la cita sostiene aparece en `texto_literal`, o hay `derivado_de` declarado | T5 |
| I5 | `pagina_pdf` es la que predice la `Paginacion` a partir de `pagina_impresa` | T6 |
| I6 | Toda `Cita` declara `caracter`; todo `Fundamento` usa un `verbo` compatible | T11 |
| I7 | `alcance = Acotada` exige `razon` y `que_queda_fuera`; `uso = NoUsada` exige `por_que_no` | T12 |
| I8 | Toda columna/fila que una vista de cálculo consume está transcrita | T13 |
| I9 | Toda vista de cálculo coincide con la transcripción de la que se deriva | T14 |
| I10 | Condición con `efecto != BLOQUEA` exige `justificacion_de_no_bloquear` no vacía | T15 |
| I11 | Todo `Modificador` declara `orden`; sus `tramos` cubren el dominio o hay `Laguna` | T16 |
| I12 | Una `Fuente` con `ausente=True` no sostiene ningún `[N]` ni tiene `texto_literal` | T17 |
| I13 | Ninguna `Interpretacion` se serializa dentro de un campo de cita | T7 |
| I14 | Ningún numeral, página o título de tabla aparece como literal fuera de `normativa/` | T10 |
| I15 | Todo id referenciado existe; ninguna `Cita` queda huérfana | T4 |
| I16 | Un `Verbatim` conserva tildes, mayúsculas y erratas; la normalización es solo para buscar | T21 |
| I17 | Una `Cita` con `POR_TRANSCRIBIR` no lleva `verificado`; el total de `POR_TRANSCRIBIR` solo decrece | T22 |

---

## 4. Tabla completa con uso parcial — sin que parezca error

**Pregunta 2 del encargo.** La respuesta corta: hoy «parcial» nombra tres cosas
distintas, y por eso no se puede declarar ninguna sin que parezca defecto. El esquema
las separa en **tres ejes ortogonales**, cada uno con su campo, su razón obligatoria y su
tratamiento propio en la ventana.

| Eje | Pregunta que responde | Campo | ¿Es un defecto? |
|---|---|---|---|
| **A · Alcance de la transcripción** | ¿Qué parte de la tabla *impresa* está en el registro? | `TablaNormativa.alcance` | **Sí**, si la razón falta |
| **B · Uso del cálculo** | ¿Qué parte de lo transcrito *consume* el cálculo? | `Columna.uso` / `Fila.uso` | **No**, nunca. Es información |
| **C · Lagunas de la fuente** | ¿Qué parte del dominio *la fuente misma* deja sin cubrir? | `TablaNormativa.lagunas` | **No**. Es un hecho del documento |

```python
Alcance = Union[Integra, Acotada]

@dataclass(frozen=True)
class Integra:
    """La tabla impresa está entera en el registro."""

@dataclass(frozen=True)
class Acotada:
    razon: str                  # obligatorio
    que_queda_fuera: str        # obligatorio: qué NO está, en palabras de la fuente
    donde_leerlo: str           # numeral y página de lo que no se transcribe

UsoEnCalculo = Union[Usada, NoUsada, PendienteDeCondicion]

@dataclass(frozen=True)
class Usada:
    por: Tuple[str, ...]        # "M3.resolver_manning", "M5.v3_velocidad_maxima"

@dataclass(frozen=True)
class NoUsada:
    por_que_no: str             # obligatorio
    # NO bloquea. La ventana la pinta atenuada, con la razón en el tooltip

@dataclass(frozen=True)
class PendienteDeCondicion:
    condicion_id: str           # la fila/columna se elegiría si esto se declarase
    # SÍ bloquea, por D4. La ventana la pinta como elección pendiente
```

### 4.1 Las dos tablas del encargo son casos **distintos**, y ahí está el fondo

El encargo las pone juntas —«la Tabla N° 09 tiene tres columnas y el código lleva dos;
la Tabla 5.10.1-1 tiene tres categorías de acero y el código lleva una»—, y en la
superficie son idénticas: *la fuente tiene n, el código usa menos de n*. **Son dos cosas
opuestas, y confundirlas es lo que hace imposible declarar la primera sin parecer que se
esconde la segunda.**

| | **Tabla N° 09 · columna NORMAL** | **Tabla 5.10.1-1 · categorías B y C** |
|---|---|---|
| Por qué el cálculo no la usa | Porque **el método del proyecto no la pide**: la regla de doble *n* (Sec. 4.1) exige los dos extremos, no el valor corriente. El NORMAL entraría en un cálculo de un solo *n*, que es lo que la regla prohíbe | Porque **el proyecto no sabe cuál aplica**: la categoría de refuerzo (acero sin recubrir / galvanizado / epóxico) no está declarada |
| ¿Falta un dato? | No. La decisión está tomada y razonada | **Sí.** `categoria_refuerzo_aashto` está vacío |
| ¿Bloquea? | **Nunca** | **Sí**, y debe: con acero protegido AASHTO baja de 76,2 a 50,8 mm y **la regla del mayor la gana E.060** — se invierte qué norma gobierna |
| Campo | `uso = NoUsada(por_que_no=...)` | `uso = PendienteDeCondicion(condicion_id=...)` |
| Ventana | Columna **visible y atenuada**, con la razón | Columna **visible y marcada como elección pendiente**; el cálculo se detiene |
| Hallazgo | `NOR-HID-11` (cerrado, S5) | `NOR-AAS-01` (cerrado, S10) |

**El mecanismo que lo hace robusto:** `NoUsada` exige `por_que_no`, y ese texto es lo que
la ventana pinta. Una columna sin razón declarada no compila el registro. De modo que
«completa pero de uso parcial» no se declara con una etiqueta —se declara **contestando
la pregunta**, y la ventana muestra la respuesta en el sitio donde nace la duda.

Y el rótulo que la ventana imprime **no lo escribe nadie a mano**: lo deriva la tabla.

```python
def rotulo_de_completitud(t: TablaNormativa) -> str:
    # "Tabla completa · el cálculo usa 2 de 4 columnas"
    # "Transcripción acotada al grupo A · el cálculo usa 2 de 4 columnas"
```

Así la frase que ve el revisor no puede contradecir a los campos: **es** los campos.

### 4.2 Un caso que ninguno de los dos ejes cubre, y por eso hace falta el tercero

La Tabla 4.4 de E.060 imprime la fila severa como `< 2,0 %` y la muy severa como
`2,0 % <`: **el valor 2,0 % exacto no cae en ninguna de las dos.** No es transcripción
incompleta (eje A) ni uso parcial (eje B): es un hueco **del texto impreso**. Igual que
la banda `0.40 < a/c < 0.50` que el Manual de Puentes deja sin factor.

```python
@dataclass(frozen=True)
class Laguna:
    que_no_cubre: str               # "el punto SO4 = 2,0 % exacto"
    quien_lo_cierra: Optional[str]  # "hoja_de_ruta §3.3" | clave de criterio [C] | None
    con_que_regla: str
    si_nadie_lo_cierra: Efecto = Efecto.BLOQUEA
```

La ventana la pinta en **su propia banda**, separada de las filas, con el rótulo «la
fuente no cubre este caso». Sin ese tercer eje, una laguna se acaba disfrazando de fila
—que es cómo un `>=` en el código termina decidiendo en silencio lo que la norma calla—.

### 4.3 Dos transcripciones del mismo original: `CorrespondenciaDeTablas`

La Tabla 5.10.1-1 de AASHTO y la Tabla 2.9.1.5.5.3-1 del Manual **son la misma tabla**,
y sus filas **no se pueden cruzar por nombre**: el Manual traduce *shafts* por «Pilares»
donde la transcripción de AASHTO dice «pilote», y además parte en dos la fila de pilares
in situ en ambiente corrosivo.

Esto ya costó un defecto real: el cruce se hacía con `situacion in RECUBRIMIENTO_MP_MM`,
que daba `False` para las 8 filas de la familia de pilotes y **se saltaba sin avisar** —
la red de seguridad estaba escrita para 14 filas de 21 mientras el comentario afirmaba
que cubría todas.

```python
@dataclass(frozen=True)
class CorrespondenciaDeTablas:
    id: str
    tabla_a: str                            # "AASHTO_LRFD_9.T5.10.1-1"
    tabla_b: str                            # "MP.T2.9.1.5.5.3-1"
    pares: Dict[str, Tuple[str, ...]]       # fila de A -> filas de B (1..n)
    regla_al_cruzar: str                    # "el mayor (Sec. 0.2)"
    diferencias_declaradas: Tuple[str, ...]
```

**Invariante:** toda fila de `tabla_a` tiene entrada en `pares`; una fila sin
correspondencia declarada es un **error**, no un salto callado.

---

## 5. Modificadores

**Pregunta 3 del encargo.** El factor 0,8 / 1,0 / 1,2 por relación a/c del Art. 5.10.1
de AASHTO no es un dato más de la tabla: **puede invertir qué norma gobierna**
(`NOR-AAS-05`). Con `a/c ≤ 0.40`, el lado AASHTO cae de 76,2 a 60,96 mm y la regla del
mayor de la Sec. 0.2 la pasa a ganar E.060 con sus 70 mm.

Un modificador tiene cuatro propiedades que una tabla no tiene, y las cuatro son campos:

**(a) Actúa *sobre* celdas, no *es* una celda.** Vive en `TablaNormativa.modificadores`,
no en `filas`. La ventana lo pinta en su propia banda, bajo la tabla y sobre las notas,
con su cita. Si fuera una fila más, el usuario elegiría entre `0.8` y `76.2` como si
fueran alternativas.

**(b) Tiene orden de aplicación, y ese es el campo que decide el resultado.**

```
         orden = ANTES_DE_CRUZAR_FUENTES        (correcto)
         max( 76.2 × 0.8 , 70.0 )  =  max( 60.96 , 70.0 )  =  70.0  → gobierna E.060

         orden = DESPUES_DE_CRUZAR              (incorrecto, y da otro número)
         max( 76.2 , 70.0 ) × 0.8  =  76.2 × 0.8            =  60.96 → gobierna AASHTO
```

Los dos son «aplicar el 0,8», y difieren en 9 mm y en **qué norma queda citada en la
memoria**. Sin el campo, el orden lo fija quien escriba el código, en silencio y sin que
la ventana pueda mostrarlo. `orden` es obligatorio y no tiene valor por defecto.

**(c) Está acotado por un piso normativo con cita propia.** El Manual escribe
«el recubrimiento mínimo sobre las barras principales […] deberá ser de 1.0 in (25 mm)».
Es lo que impide que un factor de 0,8 arrastre el recubrimiento a cualquier cosa. Va en
`Modificador.piso = (25.4, cita_id)`, **no** como constante suelta: el piso es del
modificador, y separarlo permitiría aplicar uno sin el otro.

**(d) Puede tener laguna, y la laguna no se rellena con la otra fuente.** El Manual
imprime **dos** viñetas y AASHTO **tres**: la banda `0.40 < a/c < 0.50` no está en el
corpus peruano. Se declara como `Laguna` y se cierra por criterio `[C]`
(`factor_recubrimiento_banda_intermedia_ac`), no copiando el 1,0 de la otra fuente hacia
adentro de la transcripción peruana. La banda **es alcanzable** en este expediente —con
sulfatos severos y sin cloruros la a/c máxima resulta 0,45—, de modo que no es un caso
teórico.

**Invariante T16:** los `tramos` de un modificador cubren su dominio, o cada hueco tiene
su `Laguna`. Un modificador que no cubre un valor y no declara la laguna **bloquea**; no
devuelve 1,0 en silencio. Un modificador que se olvida no deja rastro; uno que bloquea,
sí — y esa asimetría es la que `NOR-AAS-05` documenta («el criterio lo ignoraba entero»).

---

## 6. Condiciones de aplicación que el proyecto todavía no puede evaluar

**Pregunta 4 del encargo.** R4 del plan: *no declarada, bloquea; no se asume.* El
esquema lo consigue con **el valor por defecto**, no con disciplina:
`efecto_si_indeterminada = BLOQUEA`, y desviarse exige texto.

Los cuatro casos que el plan identifica, resueltos:

| Caso | Hallazgo | `resuelve` | `efecto` | Por qué |
|---|---|---|---|---|
| Carriles por sentido (4 vs 6 calicatas) | `NOR-SUE-01` | `PorDatoDeSitio("carriles_por_sentido")` | **BLOQUEA** | El Cuadro 4.1 **sí** lo condiciona; el código afirmaba que no. El dato existe en el mundo: falta traerlo |
| Categoría de acero AASHTO | `NOR-AAS-01` | `PorCriterio("categoria_refuerzo_aashto")` | **BLOQUEA** | Cambia qué norma gobierna. Ya implementado así en S10: el criterio vale `None` y detiene los tres recubrimientos |
| Relación a/c | `NOR-AAS-05` | `PorCriterio` sobre la durabilidad | **BLOQUEA** | Su insumo (`exposicion_quimica_ems`) es un `[S]` pendiente de ensayo |
| «Solo si el barril fluye lleno» | `NOR-HDS-05` | `NoEvaluable(...)` | **ADVIERTE** | Exige un perfil de la lámina de agua que este script no calcula. Único caso de la lista |
| Refuerzo transversal mínimo (β) | `NOR-AAS-06` | `PorCriterio` | **BLOQUEA** | Habilita una de las dos expresiones de β; AASHTO lo escribe como potestativo |

### 6.1 Por qué `ADVIERTE` existe, y por qué no puede ser cómodo

`NOR-HDS-05` es la prueba de que un esquema que **solo** bloquee es inservible: la
condición «que el barril fluya lleno en la mayor parte de su longitud» no la puede
evaluar este programa, y bloquear por ella detendría todo cálculo de control de salida
del expediente. El proyecto calcula `h_o` igualmente y **declara**. Eso es legítimo, y es
distinto de asumir.

La diferencia la sostienen tres exigencias, no una:

1. `justificacion_de_no_bloquear` es **obligatoria y no vacía** (T15).
2. `NoEvaluable.que_lo_cerraria` obliga a nombrar el procedimiento concreto que sí la
   resolvería —aquí, el de barril parcialmente lleno del Cap. III de HDS-5—. Un «no se
   puede» sin salida declarada es una excusa; con salida, es una deuda con dirección.
3. El aviso viaja **al punto**, no al preámbulo. La auditoría adversarial refutó
   exactamente la primera versión de este cierre: declaraba las condiciones sin
   evaluarlas *pudiendo*, y «un aviso general que no señala el punto afectado no le sirve
   al revisor». Por eso la condición evaluable se modela `PorExpresion` y se evalúa:
   `HW/D < 1.2` («cautela») y `HW/D < 0.75` («no debe usarse») son comparaciones entre
   dos números que el módulo ya tiene.

**Regla que se deduce, y conviene escribirla:** dentro de una misma cita puede haber
condiciones de los dos tipos. `NoEvaluable` en una **no** contagia a las otras. Extender
a la segunda condición una imposibilidad que solo vale para la primera fue el defecto que
la auditoría adversarial destapó, y el esquema lo impide porque cada `CondicionAplicacion`
lleva su propio `resuelve` y su propio `efecto`.

### 6.2 No se inventa una excepción nueva

Una condición con `efecto = BLOQUEA` cuyo `resuelve` es `PorCriterio(clave)` **se
resuelve llamando a `criterios_adoptados.valor(clave)`**, que ya lanza
`CriterioPendienteError` y ya está en la taxonomía de `ErrorProyecto` que la GUI
distingue con un solo `except`. `PorDatoDeSitio` hace lo propio con `datos_sitio.valor`.

El registro **no** añade una excepción, un camino de declaración ni un segundo `except`.
Es la misma regla que el plan pone para la ventana —«se declara por
`establecer_valor_dinamico()`, que ya pasa por `_verificar_criterio()`. No inventes un
segundo camino»— aplicada un nivel más abajo.

---

## 7. Los tres «rangos», y por qué la Tabla N° 10 no puede pintarse mal

**Pregunta 5 del encargo.**

### 7.1 Los tres siguen viviendo en tres sitios, y eso es la solución

La §4.2 del plan describe tres objetos que el repositorio **maneja por separado y nombra
igual**. La tentación de diseño es unificarlos en un `Rango(tipo=...)`. **Sería el error
exacto que el plan advierte:** si comparten tipo, comparten renderizador, y la ventana
los enseña con la misma cara.

| | Dominio físico | Rango normativo | Rango de sensibilidad |
|---|---|---|---|
| Vive en | `dominios.py` | `normativa/rangos.py` | `Criterio.sensibilidad` |
| Qué es | Qué valores puede tomar el dato antes de dejar de ser ese dato | Qué acota la norma | Cuánto se movió la adopción `[A]` para defenderla |
| Rótulo obligatorio | «Fuera de esto, la celda está mal llenada. **No es normativo**» | «La Tabla N° X, pág. Y, da para este material…» | «Adopción del proyectista; se defiende mostrando el resultado en los extremos» |
| Lo escribe | El programa | La norma | El proyectista |

**No se unifican.** Lo único que se les impone es un contrato de la ventana: la tabla de
renderizadores es **total y sin caso por defecto**, un tipo nuevo obliga a escribir su
renderizador, y **los tres rótulos son textualmente distintos** (test T18). Un renderizador
genérico de «rango» es justamente la pieza que no debe existir.

### 7.2 `NOR-HID-04`: los dos números son ambos máximos

La fila del concreto de la Tabla N° 10 trae `3.0` y `6.0`, y **los dos son máximos**. El
título lo dice —«Velocidades máximas admisibles **(m/s)** en conductos revestidos»— y lo
confirma el rótulo de su única columna de valores, «VELOCIDAD (M/S)». El piso de
velocidad está **aparte**, en el párrafo siguiente, y vale 0,25 m/s para todos los
materiales por igual.

En cuanto eso vaya a una ventana rotulada «rango», el usuario leerá 3,0 como mínimo. Tres
mecanismos lo impiden, en orden de fuerza:

**(1) El tipo no tiene `minimo`.** La fila no es un `IntervaloAdmisible`:

```python
@dataclass(frozen=True)
class ConjuntoDeMaximos:
    valores: Tuple[float, ...]          # 1..n; ninguno es un piso
    unidad: str
    cita_id: str
    que_pasa_fuera: QuePasaFuera
    rotulo_obligatorio: str = "Todos los valores de esta fila son MÁXIMOS admisibles."
    # NO existe .minimo. La ventana no tiene qué enlazar a la casilla "desde".
```

**(2) La fila de un solo valor deja de ser un caso especial.** «Mampostería de piedra y
concreto» trae **un** número. Hoy escribirla `(2.0, 2.0)` inventaba un par que la fuente
no escribe (`NOR-HID-07`). Con `ConjuntoDeMaximos`, una tupla de un elemento es la forma
normal: no hay nada que rellenar y nada que inventar.

**(3) La explicación del proyectista sale del campo de cita.** «El rango recorre la
calidad del revestimiento; el inferior es el máximo del acabado más pobre» **no aparece
en el Manual**. Es `Interpretacion`, con sus dos `en_contra` transcritos —la frase que
introduce la tabla habla de «un rango, cuyos límites se describen a continuación», y la
fila de mampostería trae un solo valor— y su `a_favor` —el título, que es lo único que
decide que ninguno de los dos números sea un piso—.

Y el invariante T7 es el que impide la reincidencia de `76791d0`: **una `Interpretacion`
no puede serializarse dentro de un campo de `Cita`.** El defecto no fue de una constante
suelta; fue del formato. Por eso la solución tiene que ser del formato.

### 7.3 `QuePasaFuera` también es familia cerrada

```python
class QuePasaFuera(str, Enum):
    INCUMPLE_LA_NORMA      = "incumple"       # y la memoria lo marca NO CUMPLE
    SALE_DEL_DOMINIO       = "dominio"        # la celda está mal llenada
    DEJA_DE_SER_DEFENDIBLE = "indefendible"   # la adopción [A] pierde su sustento
    LA_FUENTE_NO_SE_PRONUNCIA = "no_cubierto" # → Laguna; ver §4.2
```

Sin el cuarto valor, un valor fuera de la tabla se acaba leyendo como incumplimiento —que
es lo contrario de lo que la fuente hace: callar—.

---

## 8. Fuentes que se citan y no están en `normas/`

**Pregunta 6 del encargo.** La §15 del plan las lista: WSDOT Hydraulics Manual, AASHTO
M294, ASTM A796/A798/C76/A-807, DG-2018, HEC-14, Ley 29338 y su reglamento, series
SENAMHI/ANA, Meyerhof (1957), el Apéndice A3 de mapas del Manual de Puentes, y el estudio
geotécnico del expediente.

```python
@dataclass(frozen=True)
class Ausencia:
    por_que_se_cita: str            # qué valor del proyecto se apoya en ella
    que_desbloquearia: str          # qué se cierra si se consigue
    esfuerzo: str                   # "fácil, es descarga pública" | "gabinete" | "de campo"
    sustituto_vigente: Optional[str]    # qué se usa mientras tanto, y con qué etiqueta
```

Cuatro consecuencias, todas invariantes:

1. **`archivo_pdf = None` y `sha1 = None`.** No hay contra qué verificar, y el registro no
   finge que lo hay.
2. **Ninguna `Cita` a una fuente ausente lleva `texto_literal` ni `pagina_pdf`.** Se cita
   *el documento*, no una página suya. Esto es lo que estructuralmente impide una cita
   como «WSDOT Hydraulics Manual (M 23-03.12, abril 2026)» con página y frase que nadie
   abrió (hoy `v_max_hdpe` y `v_max_tmc` figuran con «cita cerrada» en el manifiesto y sin
   PDF en `normas/`).
3. **Una fuente ausente no puede sostener un `[N]`** (T17). Es la definición misma de
   `[N]` en `CLAUDE.md`: *numeral verificado*. Un valor apoyado en una fuente ausente es
   `[C]` como máximo, y la ventana lo rotula «fuente no disponible en el expediente».
4. **`que_desbloquearia` convierte la deuda en trabajo con precio.** El plan ya identifica
   las dos baratas: **A796** cierra la mitad TMC de `clases_producto_por_relleno` y
   **M294** cierra `D_max["hdpe"]`. Un test lista las ausentes ordenadas por esfuerzo, de
   modo que la deuda se vea sin leer la §15.

**Caso aparte, y conviene no mezclarlo:** el Apéndice A3 de mapas del Manual de Puentes y
los ábacos de Meyerhof **sí están** en `normas/` — lo que no se puede es *leerlos por
texto*, porque son ráster. No son `Fuente(ausente=True)`: son `Fuente` presentes con
`Cita.verificado.metodo = "imagen renderizada"` y un valor que el proyecto no puede
extraer. Confundir «no está» con «está y no se puede leer por texto» produce dos
diagnósticos distintos y dos remedios distintos: conseguir el documento, o leerlo a ojo y
declarar la lectura como `[S]`.

---

## 9. Los tests que impiden que una cita vuelva a pudrirse

**Pregunta 7 del encargo.** Van en `tests/test_normativa_*.py`. Los que abren PDF se
marcan `@pytest.mark.pdf` y corren en la suite completa, no en el bucle rápido.

### 9.1 Guardia estructural — no abre ningún PDF, corre en milisegundos

| # | Test | Qué impide |
|---|---|---|
| **T1** | Todo `fuente_id` resuelve a una `Fuente`; ningún `Catalogo` aparece como fuente de cita | Que un tope de catálogo vuelva a citarse como norma (`NOR-PRO-01/02`) |
| **T4** | Integridad referencial: todo `cita_id`, `tabla_id`, `condicion_id` y `fuente_id` referenciado existe, y ninguna `Cita` del registro queda huérfana | El id que apunta a nada — la versión moderna de la referencia `archivo:línea` rota |
| **T8** | El manifiesto regenerado desde el registro coincide con el del repositorio | Que el índice y el código se separen otra vez |
| **T9** | `MAX_REFERENCIAS_DE_PROSA == 0`: toda fila del manifiesto se ancla a un id del registro | **`NOR-MAN-04`**. Ver §9.3 |
| **T7** | Ninguna `Interpretacion` aparece serializada dentro de un campo de `Cita` | La reincidencia de `76791d0` (`NOR-HID-04`, `NOR-HID-06`) |
| **T10** | Ningún numeral, página o título de tabla aparece como literal fuera de `src/normativa/` | Criterio de aceptación #1 del plan. Es el `test_sin_literales` de las citas |
| **T11** | Toda `Cita` declara `caracter`; el `verbo` de cada `Fundamento` es compatible con el `caracter` de sus citas | «La norma obliga a…» sobre un párrafo que recomienda (`NOR-MEM-01`, `MAT-O13`) |
| **T12** | `Acotada` sin `razon`/`que_queda_fuera`; `NoUsada` sin `por_que_no` | Tabla podada que se ve igual que tabla completa (§4) |
| **T13** | Toda columna/fila que consume una vista de cálculo está transcrita | `NOR-HID-11`, `NOR-AAS-01`, `NOR-E060-05` |
| **T14** | Cada vista de cálculo coincide con la transcripción de la que se deriva | Las dos copias que divergen |
| **T15** | `efecto != BLOQUEA` sin `justificacion_de_no_bloquear` | Que «advertir» se vuelva la salida cómoda (`NOR-HDS-05`) |
| **T16** | Todo `Modificador` declara `orden`; sus tramos cubren el dominio o hay `Laguna` | `NOR-AAS-05`, y el modificador que devuelve 1,0 en silencio |
| **T17** | Ninguna `Fuente(ausente=True)` sostiene un `[N]`, ni sus citas llevan página o texto literal | §15 del plan; `v_max_hdpe` / `v_max_tmc` / `D_max["hdpe"]` |
| **T18** | Los rótulos obligatorios de los tres «rangos» son textualmente distintos, y la tabla de renderizadores de la ventana es total y sin caso por defecto | §4.2 del plan: que la ventana enseñe una lectura falsa |
| **T19** | Toda fila de `tabla_a` de una `CorrespondenciaDeTablas` tiene par declarado | El cruce que se saltaba 8 de 21 filas sin avisar |
| **T20** | Las `Discrepancia` en estado `ABIERTA_CONTRA_HOJA_DE_RUTA` están listadas y M11 las imprime | La tercera obligación de `CLAUDE.md`, hoy solo en prosa |
| **T21** | Todo `Verbatim` conserva tildes, mayúsculas y erratas de la fuente | Un literal de-acentuado no se puede encontrar en el PDF. Ver §11.3 |
| **T22** | Ninguna `Cita` con campos `POR_TRANSCRIBIR` lleva `verificado`, y su total solo decrece | Que «pendiente de leer» se disfrace de transcrito |

### 9.2 Guardia contra el PDF — la que hace verdadera la palabra «verificado»

| # | Test | Qué impide |
|---|---|---|
| **T0** | El `sha1` de cada PDF de `normas/` coincide con el declarado en su `Fuente` | Que se cambie el archivo y todos los `verificado` queden mintiendo. **Si falla, no falla «un test»: caducan todas las citas de esa fuente**, y el mensaje las lista |
| **T2** | El `texto_literal` normalizado aparece en la `pagina_pdf` declarada | La cita que dice lo que la página no dice |
| **T3** | El `titulo_numeral` aparece en esa página, junto al `numeral` | **`NOR-PUE-01`** |
| **T5** | El valor que la cita sostiene aparece en su `texto_literal`, o la cita declara `derivado_de` con la conversión | **`NOR-PUE-01` y `NOR-HID-01`**. Es el test de la causa raíz de C11: «atribuciones de valores a numerales que no los escriben» |
| **T6** | La `pagina_pdf` es la que predice la `Paginacion` desde la `pagina_impresa` | **`MAT-O17`** (76→77, C.2→C.6, 2.14→2.10, 982→984) y `NOR-EG-01` |

Normalización de T2/T3/T5: minúsculas, colapso de espacios, `NFKD` sin diacríticos,
comillas y guiones unificados, y **coma decimal ≡ punto decimal** (E.060 imprime «2,0 %»
y el código escribe `2.00`). Sin esa última equivalencia, T5 daría falsos negativos en
todo el corpus peruano.

### 9.3 Cuál habría atrapado cada uno de los dos casos que el encargo nombra

**`NOR-PUE-01` — el numeral que resultó ser «Aparatos de Apoyo».**

`SOBRECARGA_TRASDOS_H_EQ = 0.60` se apoya en el numeral `2.1.4.3.9` del Manual de
Puentes. Según `NOR-PUE-01` —y así lo recoge el prompt de S12— ese numeral se titula
«Aparatos de Apoyo», y el texto que de verdad sostiene la sobrecarga está en `2.4.2.2`. Lo atrapan
dos tests, y conviene ver que son dos porque atacan cosas distintas:

- **T5 es el que lo atrapa solo, sin criterio humano.** El `texto_literal` del numeral
  2.1.4.3.9 habla de aparatos de apoyo y **no contiene ningún `0.60` de relleno
  equivalente**. El test compara el valor con el texto que lo sostiene y falla. No hace
  falta que nadie se dé cuenta de nada: el número no está en la frase.
- **T3 lo atrapa en el momento de transcribir**, que es antes. `titulo_numeral` es
  obligatorio y verbatim: quien rellene la cita tiene que abrir la pág. 91 y copiar el
  encabezado. Es lo que la §4.1 del plan describe como «la cita se cae sola».

Y hay un tercer efecto, que no es un test sino una propiedad: por **D1**, el numeral está
propagado a seis puntos del repositorio como **una** `Cita` referenciada seis veces.
Corregirla es un cambio en un sitio. Hoy son seis cadenas independientes y nada garantiza
que se corrijan las seis — que es la mitad del daño de este hallazgo.

**`NOR-MAN-04` — 66 de 296 referencias `archivo:línea` que no llevan a lo que dicen.**

Aquí hay que ser exacto, porque la respuesta fácil es falsa. El test que hoy vigila el
manifiesto **no** «solo comprueba que la línea exista»: verifica que cada referencia caiga
dentro del **bloque del símbolo** que su fila cita, y eso funciona. El problema es su
excepción declarada: las **referencias de prosa** —filas sin identificador entre
backticks— solo se comprueban contra «que la línea no esté vacía», y la auditoría
encontró que **el 100 % de los defectos está ahí dentro**.

Medido hoy sobre `origin/main`, con el propio código del test:

```
referencias totales:                   326
verificables por símbolo:              240
de prosa (el hueco declarado):          86      ← aquí caen los 66 rotos
cupo actual MAX_REFERENCIAS_DE_PROSA:   90
```

De modo que la respuesta es doble:

- **El test que lo habría atrapado es T9: `MAX_REFERENCIAS_DE_PROSA == 0`.** Con el cupo
  en cero, las 86 referencias sin ancla —los 66 defectos entre ellas— fallan el día que
  entran. Marca un superjuego de los rotos, que es el comportamiento correcto de una
  guardia: no distingue «rota» de «no verificable», y **ninguna de las dos debe existir**.
- **Pero bajar el cupo hoy sería imposible de cumplir**, porque una fila del manifiesto
  que no cita ningún símbolo no tiene a qué anclarse. Lo que lo hace cumplible es **T8: el
  manifiesto se genera desde el registro** (punto 6 de S12) — cada fila nace de un objeto
  con id estable, y el ancla deja de ser `archivo:línea` para pasar a ser el id. T8 se
  implementa regenerando a un temporal y comparando: si difieren, el manifiesto está
  desincronizado.

**El fondo, y por eso este hallazgo es de diseño y no de mantenimiento:** el número de
línea es un ancla que se rompe sola. Cualquier inserción en un archivo citado desplaza
todos los enlaces de abajo, en silencio. La regla 4 de `CLAUDE.md` ya lo dice —«ancla
todo por NOMBRE DE SÍMBOLO […] nunca por número de línea»— y el manifiesto es el
documento del repositorio que más la incumple: 326 veces. **T9 es la guardia; T8 es la
cura.**

---

## 10. Ruta de migración: `constantes_normativas.py` no se rompe

**Pregunta 8 del encargo.** El archivo tiene 213 nombres a nivel de módulo y **lo
importan 22 archivos**: ocho de los once módulos de cálculo (M1, M2, M4, M5, M6, M8, M9,
M11), `criterios_adoptados.py`, `cli.py` y doce archivos de `tests/`. Cambiarlo de golpe
no es una opción.

**La migración no inventa un patrón: usa el que el archivo ya tiene.** Hoy `MANNING` no
es una tabla: es una **vista derivada** de `TABLA_09_FILAS`, y el comentario que la
acompaña explica exactamente por qué («si la transcripción se corrige, esta vista se
corrige con ella y no quedan dos copias que puedan divergir»). Lo mismo `V_MAX` desde
`TABLA_10_FILAS` y `RIESGO_ADMISIBLE` desde `TABLA_02_FILAS`.

**La migración es mover la mitad *transcripción* al registro y dejar la mitad *vista* donde
está.** Los consumidores siguen leyendo el mismo nombre.

```python
# ANTES — src/constantes_normativas.py
TABLA_09_FILAS = { "concreto_tubo_recto": {"fila": "...", "min": 0.010, ...}, ... }
MANNING = {c: (f["min"], f["max"]) for c, f in TABLA_09_FILAS.items()}

# DESPUÉS — la transcripción vive en normativa/tablas.py; aquí queda la vista
from normativa import registro
TABLA_09 = registro.tabla("MC_HHD.T09")
TABLA_09_FILAS = TABLA_09.como_dict_legacy()          # forma antigua, mismo contenido
MANNING = TABLA_09.pares("minimo", "maximo")          # misma vista, misma firma
```

### 10.1 Las cinco etapas

| Etapa | Qué pasa | Qué se rompe |
|---|---|---|
| **M0 · Fotografía** | Antes de tocar nada: volcar los 213 nombres y sus valores a `tests/fixtures/snapshot_pre_registro.json` | Nada |
| **M1 · Paquete vacío** | `src/normativa/` existe, con esquema y tests propios. **Nadie lo importa** salvo sus tests | Nada |
| **M2 · Poblado** | Se cargan fuentes y tablas, una a una. `constantes_normativas.py` **sigue intacto** | Nada. Las dos transcripciones conviven y **T14 compara**: si difieren, una de las dos está mal, y saberlo es el objetivo |
| **M3 · Inversión, tabla a tabla** | Cada nombre público pasa a derivarse del registro. Un commit por tabla | Nada, si el snapshot de M0 sigue verde |
| **M4 · Vaciado** | `constantes_normativas.py` queda reducido a vistas de cálculo + su bloque de doble definición | Nada. El archivo **no desaparece**: es la fachada estable |

### 10.2 Los cuatro seguros

**(a) El snapshot de M0 hace la migración demostrablemente conservadora.** Un test
compara cada nombre público contra su valor fotografiado. Migrar **no puede** cambiar un
número: si el registro devuelve otra cosa, o la transcripción nueva está mal, o la vieja
lo estaba — y en ambos casos el test lo dice antes de que llegue a un cálculo. Cualquier
cambio intencional edita el snapshot **en el mismo commit**, con su razón: pasa de ser un
efecto lateral invisible a un renglón de diff.

**(b) La exención del barrido de literales se estrecha, no se ensancha.**
`tests/test_sin_literales.py` exime hoy a `constantes_normativas.py`,
`criterios_adoptados.py` y `datos_sitio.py`. `src/normativa/` entra en la lista **con una
condición que las otras tres no tienen**: todo literal numérico suyo debe estar dentro de
un `FilaDeTabla`, un `TramoDeModificador` o un `RangoNormativo` — nunca como constante de
módulo suelta. Sin esa condición, el paquete nuevo sería el mejor escondite del
repositorio.

**(c) El trinquete.** `normativa/PENDIENTE_DE_MIGRAR` enumera lo que falta. Un test exige
que la lista **solo decrezca**. La migración a medias es un estado legítimo; la migración
a medias *invisible*, no.

**(d) `ReferenciaNormativa` es el puente, y ya existe.** `Verificacion.numeral` es hoy un
`str`, y decenas de tests hacen `numeral in memoria`. `Cita` **no** es un `str` —es un
objeto rico—, pero expone `Cita.referencia -> ReferenciaNormativa`, que sí lo es y ya
mantiene separadas las dos mitades (`seccion_hoja_ruta` / `numeral_norma`). Durante la
migración `Verificacion.numeral` admite las dos formas; al final lleva la que produce la
cita. **Ningún test de memoria se reescribe.**

### 10.3 Orden de migración, y por qué no es el orden del archivo

Se migra **por cluster**, no por orden de aparición, porque el cluster es la unidad de
trabajo del repositorio y porque el registro se puebla como efecto del barrido de citas:

1. **C11** (29 hallazgos) puebla `fuentes.py` y `citas.py`: es el barrido de citas contra
   los PDF. Todo lo demás cuelga de aquí.
2. **C05** (Manning, V1/V2/V3): las Tablas 09 y 10 son las dos de la §11 y las más
   pequeñas; son el banco de pruebas del esquema.
3. **C12** (calicatas): el Cuadro 4.1 es el primer caso real de `CondicionAplicacion` que
   bloquea sobre un dato de sitio.
4. **C02** (h_eq): es el caso de `CondicionAplicacion` sobre una tabla **de dos
   entradas** (altura × orientación), y su conflicto vinculante (#4) dice que no es
   contradicción sino dato faltante.
5. **C07, C03, C04**: las tablas grandes (recubrimiento, γ_p, combinaciones, F_pga), ya
   con el esquema rodado.

### 10.4 Lo que la migración **no** toca

- **`datos_sitio.py`**, por la razón contraria a las otras exenciones: sus números **sí**
  son valores de proyecto. No se convierte en constantes (§14 del plan).
- **`dominios.py`**, **`tolerancias.py`**, **`constantes_fisicas.py`**: ninguno contiene
  valores de proyecto. El dominio físico **no** entra en el registro normativo — es
  justamente el primero de los tres «rangos» y confundirlo sería el error de la §7.1.
- **El motor hidráulico.** Son 174 verificaciones correctas contra la fuente primaria, y
  el snapshot de M0 es lo que garantiza que la migración no las toque.

### 10.5 Una dependencia nueva, y hay que consultarla

Los tests T0/T2/T3/T5/T6 abren PDF, y `normativa/extraccion/` es exactamente eso. **No
hay hoy ninguna librería de PDF en `requirements.txt`** (numpy, scipy, pytest,
ttkbootstrap, weasyprint), y `CLAUDE.md` exige consultar antes de añadir una.

- Es una dependencia **de test**, no del software calculado: va en un
  `requirements-dev.txt`, no en `requirements.txt`.
- Necesita **extracción de texto por página** y, para tres hallazgos ya conocidos
  (el `>` de la última columna de `F_pga`, el asterisco de la fila F, el `[1 −]` de
  `K_AE`), **renderizado a imagen**. `PyMuPDF` hace las dos; `pdfminer.six` solo la
  primera.
- Si no se autoriza, el diseño **no se cae**: T0, T1, T7 y T10-T20 son estructurales y
  corren sin PDF. Lo que se pierde es la verificación automática (T2/T3/T5/T6), que
  pasaría a ser manual vía el subagente `verificador-normativo`. **Es la decisión del
  usuario, y queda abierta** (§12).

---

## 11. Dos tablas reales del repositorio, escritas como datos

Las dos son del Manual de Hidrología y del **mismo numeral**, `4.1.1.3.6`. Se eligen por
eso: comparten fuente, numeral y página aproximada, y aun así **una es íntegra y la otra
acotada**, de modo que la diferencia que se ve entre las dos es la del esquema y no la de
dos documentos distintos.

> **Procedencia de estos datos.** Reproducen la transcripción que hoy vive en
> `src/constantes_normativas.py` tras el cierre de `NOR-HID-04`, `NOR-HID-06`, `NOR-HID-07`
> y `NOR-HID-11` en S5 (commit `00da460`). **Ninguna cita se verifica aquí**: los campos
> que el repositorio no tiene aparecen como `POR_TRANSCRIBIR` y `verificado` va en `None`.
> Rellenarlos es el trabajo de S12, con el subagente `verificador-normativo`.

### 11.0 La fuente, común a las dos

```python
MC_HHD = Fuente(
    id="MC_HHD",
    titulo="Manual de Hidrología, Hidráulica y Drenaje",
    emisor="MTC — Dirección General de Caminos y Ferrocarriles",
    edicion="Versión Libro",
    anio=2011,
    resolucion="RD 20-2011-MTC/14",
    archivo_pdf="normas/Hidrología, Hidráulica y Drenaje (Versión Libro).pdf",
    sha1="a31e853b8171b931863d7afa4379bbbc57cacb0d",
    paginacion=SinDeterminar(
        por_que="ninguna de las citas del repositorio a este documento declara página "
                "PDF: solo página impresa (25, 72, 75, 76, 77, 79, 178). El desfase "
                "no se puede inferir de lo escrito y hay que medirlo abriendo el PDF"),
    ausente=False,
)
```

**Esto ya es un resultado.** La fuente con más citas del proyecto —la que gobierna las
Fases 2 a 6— **no tiene hoy ni una sola cita verificable por página**, y hasta escribirla
como dato eso no se veía: en prosa, «pág. impresa 76» parece una cita completa.

### 11.1 Tabla ÍNTEGRA — Tabla N° 10, velocidades máximas admisibles

```python
CITA_T10 = Cita(
    id="MC_HHD.4.1.1.3.6#T10",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6, Tabla Nº 10",
    titulo_numeral=POR_TRANSCRIBIR,     # el encabezado del 4.1.1.3.6, literal
    pagina_impresa="76",
    pagina_pdf=POR_TRANSCRIBIR,
    texto_literal=Verbatim(
        texto="TABLA Nº 10: Velocidades maximas admisibles (m/s) en conductos "
              "revestidos",
        pagina_pdf=POR_TRANSCRIBIR),
    caracter=Caracter.EXIGENCIA,        # tabla de valores admisibles
    condiciones=(),
    verificado=None,                    # T22: con POR_TRANSCRIBIR dentro, no puede ir
    interpretacion=INTERPRETACION_T10,  # ver abajo — NO viaja dentro de esta cita
)

TABLA_10 = TablaNormativa(
    id="MC_HHD.T10",
    cita_id="MC_HHD.4.1.1.3.6#T10",
    titulo_literal="TABLA Nº 10: Velocidades maximas admisibles (m/s) en conductos "
                   "revestidos",
    texto_previo=Verbatim(
        texto="Se debe tener en cuenta la velocidad, parametro que es necesario "
              "verificar de tal manera que se encuentre dentro de un rango, cuyos "
              "limites se describen a continuacion.",
        pagina_pdf=POR_TRANSCRIBIR),
    columnas=(
        ColumnaDeTabla(id="revestimiento", etiqueta_literal="TIPO DE REVESTIMIENTO",
                       unidad="", uso=Usada(por=("M2.material",))),
        ColumnaDeTabla(id="velocidad", etiqueta_literal="VELOCIDAD (M/S)",
                       unidad="m/s", uso=Usada(por=("M5.v3_velocidad_maxima",))),
    ),
    filas=(
        FilaDeTabla(
            id="MC_HHD.T10#concreto",
            etiqueta_literal="Concreto",
            valores={"velocidad": ConjuntoDeMaximos(
                valores=(3.0, 6.0), unidad="m/s", cita_id="MC_HHD.4.1.1.3.6#T10",
                que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)},
            uso=Usada(por=("M5.v3_velocidad_maxima",))),
        FilaDeTabla(
            id="MC_HHD.T10#ladrillo_c_concreto",
            etiqueta_literal="Ladrillo con concreto",
            valores={"velocidad": ConjuntoDeMaximos(
                valores=(2.5, 3.5), unidad="m/s", cita_id="MC_HHD.4.1.1.3.6#T10",
                que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)},
            uso=NoUsada(por_que_no="el catálogo de conductos de la Sec. 3.2 no ofrece "
                                   "ladrillo con concreto")),
        FilaDeTabla(
            id="MC_HHD.T10#mamposteria_piedra",
            etiqueta_literal="Mamposteria de piedra y concreto",
            # UN solo valor. No es media fila ni un par al que le falte el otro número:
            # es lo que la tabla imprime (NOR-HID-07). La tupla de un elemento es la
            # forma normal, no un caso especial.
            valores={"velocidad": ConjuntoDeMaximos(
                valores=(2.0,), unidad="m/s", cita_id="MC_HHD.4.1.1.3.6#T10",
                que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)},
            uso=NoUsada(por_que_no="ídem")),
    ),
    notas_al_pie=(),                    # la tabla no imprime notas
    modificadores=(),
    fuente_declarada_por_la_tabla="HCANALES, Maximo Villon B.",
    alcance=Integra(),      # ver la nota de abajo: es una afirmación sobre la página
    lagunas=(),
    vistas_de_calculo=("V_MAX",),
)

# `Integra()` AFIRMA que la tabla impresa tiene esas tres filas y ninguna más. Se
# escribe así porque es lo que la transcripción vigente sostiene — incluidas sus dos
# afirmaciones negativas sobre TMC y HDPE —, pero **es una afirmación sobre el PDF** y
# S12 la confirma al verificar. Si apareciera una cuarta fila, lo que está mal es la
# transcripción, no el esquema: `alcance` pasaría a `Acotada` y el defecto quedaría
# declarado en vez de invisible. Ese es justamente el trabajo del campo.

# La interpretación del proyectista, FUERA de la cita (NOR-HID-04). La ventana la pinta
# en su propia banda, con estas dos listas visibles: es lo que permite al revisor
# discutirla sin discutir la norma.
INTERPRETACION_T10 = Interpretacion(
    texto="Que los dos números de una fila recorran la calidad del revestimiento — el "
          "superior para el acabado de mejor calidad y el inferior para el más pobre — "
          "es una lectura que este proyecto adopta para poder elegir un techo más "
          "conservador dentro de la fila ('v_max_concreto_eleccion'). El Manual NO la "
          "escribe.",
    en_contra=("la frase que introduce la tabla habla de 'un rango, cuyos límites se "
               "describen a continuación'",
               "la fila de mampostería trae un solo valor, que no encaja con una "
               "lectura de acabados"),
    a_favor=("el título dice 'Velocidades máximas admisibles', que es lo único que "
             "decide que ninguno de los dos números sea un piso",),
)

# Afirmación negativa: es lo que AUTORIZA el salto a un criterio [C] con fuente WSDOT
# para el techo de TMC y HDPE. Sin ella, ese [C] cubriría un vacío no demostrado.
SIN_FILA_T10 = AfirmacionNegativa(
    que_no_dice="la Tabla Nº 10 no lista TMC ni HDPE",
    ambito_barrido="las tres filas de la tabla, leídas íntegras en la pág. impresa 76")

# Vista de cálculo, DERIVADA. Reemplaza al actual `V_MAX` sin cambiarle la forma.
V_MAX = {f.id.split("#")[1]: f.valores["velocidad"].valores for f in TABLA_10.filas}
```

**Qué demuestra este ejemplo, punto por punto:**

| Lo que el esquema hace | Hallazgo que cierra |
|---|---|
| `titulo_literal` con `(m/s)` | `NOR-HID-06` |
| `ConjuntoDeMaximos` sin atributo `minimo` — la ventana no tiene qué atar a «desde» | `NOR-HID-04` |
| Fila de un solo valor como tupla de uno, sin par inventado | `NOR-HID-07` |
| `Interpretacion` en campo aparte, con `en_contra` y `a_favor` | `NOR-HID-04`, y la reincidencia de `76791d0` |
| `fuente_declarada_por_la_tabla` = HCANALES, no el MTC | atribución que la página no hace |
| `AfirmacionNegativa` con `ambito_barrido` | lo que sostiene el `[C]` de `v_max_tmc` / `v_max_hdpe` |
| `alcance=Integra()` **y** dos filas `NoUsada` con razón | «completa, con uso parcial», sin parecer error |

Nótese lo último: **esta tabla es íntegra y su uso es parcial** —el cálculo consume una
de las tres filas—, y no hay en el objeto nada que se parezca a un defecto. La ventana
imprimirá «Tabla completa · el cálculo usa 1 de 3 filas», con la razón a mano.

### 11.2 Tabla ACOTADA — Tabla N° 09, coeficiente de rugosidad de Manning

```python
CITA_T09 = Cita(
    id="MC_HHD.4.1.1.3.6#T09",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6, Tabla Nº 09",
    titulo_numeral=POR_TRANSCRIBIR,
    pagina_impresa="75",
    pagina_pdf=POR_TRANSCRIBIR,
    texto_literal=Verbatim(
        texto="TABLA Nº 09: Valores del Coeficiente de Rugosidad de Manning (n)",
        pagina_pdf=POR_TRANSCRIBIR),
    caracter=Caracter.DEFINICION,       # tabula un coeficiente; no exige ni recomienda
    verificado=None,
)

TABLA_09 = TablaNormativa(
    id="MC_HHD.T09",
    cita_id="MC_HHD.4.1.1.3.6#T09",
    titulo_literal="TABLA Nº 09: Valores del Coeficiente de Rugosidad de Manning (n)",
    columnas=(
        ColumnaDeTabla("tipo_de_canal", "TIPO DE CANAL", "",
                       Usada(por=("M2.material",))),
        ColumnaDeTabla("minimo", "MINIMO", "",
                       Usada(por=("M3.resolver_manning",))),
        # LA COLUMNA DEL CENTRO. Transcrita, no consumida, y con la razón obligatoria.
        # NO es PendienteDeCondicion: no falta ningún dato. El método del proyecto no
        # la pide, y eso es una decisión tomada, no una pendiente.
        ColumnaDeTabla("normal", "NORMAL", "",
                       NoUsada(por_que_no=
                           "la regla de doble n (Sec. 4.1 de la hoja de ruta) no pide "
                           "el valor corriente sino los dos EXTREMOS — n máximo para "
                           "capacidad y tirante, n mínimo para velocidad máxima y "
                           "socavación —, de modo que cada verificación se resuelve con "
                           "el extremo que la deja del lado seguro. El valor NORMAL "
                           "entraría en un cálculo de un solo n, que es justo lo que la "
                           "regla prohíbe")),
        ColumnaDeTabla("maximo", "MAXIMO", "",
                       Usada(por=("M3.resolver_manning",))),
    ),
    filas=(
        FilaDeTabla(
            id="MC_HHD.T09#metal_corrugado_subdren",
            jerarquia=("A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.1 METALICOS", "c. Metal corrugado"),
            etiqueta_literal="sub - dren",
            valores={"minimo": 0.017, "normal": 0.019, "maximo": 0.021},
            uso=NoUsada(por_que_no="una alcantarilla es dren para aguas lluvias, no "
                                   "sub-dren (M2._MANNING_CLAVE)")),
        FilaDeTabla(
            id="MC_HHD.T09#metal_corrugado_dren_aguas_lluvias",
            jerarquia=("A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.1 METALICOS", "c. Metal corrugado"),
            etiqueta_literal="dren para aguas lluvias",
            valores={"minimo": 0.021, "normal": 0.024, "maximo": 0.030},
            uso=Usada(por=("M2._MANNING_CLAVE['tmc']",))),
        FilaDeTabla(
            id="MC_HHD.T09#concreto_tubo_recto",
            jerarquia=("A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.2 NO METALICOS", "a. Concreto"),
            etiqueta_literal="tubo recto y libre de basuras",
            valores={"minimo": 0.010, "normal": 0.011, "maximo": 0.013},
            uso=Usada(por=("M2._MANNING_CLAVE['concreto']",
                           "criterios_adoptados['n_manning_hdpe']  # [N->] por analogía"))),
        FilaDeTabla(
            id="MC_HHD.T09#madera_duelas",
            jerarquia=("A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.2 NO METALICOS", "b. Madera"),
            etiqueta_literal="duelas",
            valores={"minimo": 0.010, "normal": 0.012, "maximo": 0.014},
            uso=NoUsada(por_que_no="el catálogo de la Sec. 3.2 no ofrece madera")),
    ),
    fuente_declarada_por_la_tabla="Hidraulica de Canales Abiertos, Ven Te Chow, 1983",

    # EL EJE A. La tabla impresa tiene cuatro grupos y aquí está uno. Se declara con su
    # razón y con dónde leer lo que falta: es lo que separa "acotada" de "podada".
    alcance=Acotada(
        razon="el grupo A es el único de la tabla que describe una alcantarilla; los "
              "grupos B (canales revestidos), C (excavado) y D (corrientes naturales) "
              "describen el cauce, no el conducto, y ningún módulo dimensiona un cauce",
        que_queda_fuera="B. CANALES REVESTIDOS O DESARMABLES; C. EXCAVADO O DRAGADO; "
                        "D. CORRIENTES NATURALES",
        donde_leerlo="MC_HHD, num. 4.1.1.3.6, Tabla Nº 09, pág. impresa 75 y ss."),
    lagunas=(),
    vistas_de_calculo=("MANNING",),
)

SIN_FILA_T09 = AfirmacionNegativa(
    que_no_dice="la Tabla Nº 09 no lista HDPE",
    ambito_barrido="las siete subfilas de concreto y las demás del grupo A, pág. 75")

# Vista de cálculo DERIVADA, idéntica en forma a la actual: (n_min, n_max) por fila.
MANNING = TABLA_09.pares("minimo", "maximo")
```

**La ventana pinta esta tabla así, y todo sale de los campos:**

```
TABLA Nº 09: Valores del Coeficiente de Rugosidad de Manning (n)
MC-HHD · RD 20-2011-MTC/14 · num. 4.1.1.3.6 · pág. impresa 75      [cita no verificada]
Fuente de la tabla: Hidráulica de Canales Abiertos, Ven Te Chow, 1983

  TIPO DE CANAL                             MINIMO   ·NORMAL·   MAXIMO
  A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO
    A.1 METALICOS
      c. Metal corrugado — sub - dren        0.017    ·0.019·    0.021   (atenuada)
      c. Metal corrugado — dren aguas lluvias 0.021   ·0.024·    0.030   ← TMC
    A.2 NO METALICOS
      a. Concreto — tubo recto y libre…      0.010    ·0.011·    0.013   ← concreto
      b. Madera — duelas                     0.010    ·0.012·    0.014   (atenuada)

  Transcripción acotada al grupo A · el cálculo usa 2 de 4 columnas
  ▸ Por qué no se usa NORMAL: la regla de doble n pide los dos extremos, no el valor
    corriente…
  ▸ Qué queda fuera: grupos B, C y D — describen el cauce, no el conducto…
  ▸ La tabla no lista HDPE (barrido: el grupo A entero, pág. 75)
```

Ninguna de esas cuatro líneas del pie la escribe la ventana: las **deriva** de `alcance`,
de `uso`, de `AfirmacionNegativa` y de `verificado`. Es la R3 del plan —lo que la ventana
muestra es lo que la memoria imprime— hecha imposible de incumplir, porque hay un solo
sitio de donde leer.

### 11.3 Lo que escribir estas dos tablas como datos hizo aparecer

Tres cosas que en prosa no se veían. **Son observaciones sobre el repositorio, no citas
verificadas**: las tres se comprueban leyendo el propio código, sin abrir ningún PDF.

1. **`SinDeterminar` en el Manual de Hidrología.** La fuente con más citas del proyecto
   no tiene ninguna página PDF declarada. Trabajo de S12, y no estaba enumerado.

2. **Hay `Verbatim` de-acentuados, y no se pueden encontrar en el PDF.** `TABLA_10_TITULO`
   escribe «Velocidades **maximas** admisibles» y `TABLA_10_TEXTO_PREVIO` escribe
   «**parametro**», «**limites**», «**continuacion**». La transcripción de la Tabla γ_p
   hace lo contrario y **dice por qué**: «van con sus tildes y con sus letras griegas, al
   revés que la mayoría de este archivo: son texto citado, y un revisor tiene que poder
   buscarlo en el PDF y encontrarlo». Las dos reglas conviven hoy en el mismo archivo.
   La correcta es la segunda, y es **exactamente la misma clase de defecto que
   `NOR-HID-06`**: un título entrecomillado al que le falta un trozo de lo que la página
   imprime. La normalización sin diacríticos es para **buscar**, nunca para **guardar**
   → T21.

3. **Los cuatro niveles de la fila de la Tabla N° 09.** Hoy `"A.1 METALICOS - c. Metal
   corrugado - sub - dren"` es una sola cadena, con los guiones puestos por el proyecto
   mezclados con el texto de la fuente. Buscar esa cadena en el PDF no la encuentra;
   buscar `"Metal corrugado"` sí. `jerarquia` + `etiqueta_literal` + `fila_legible()`
   separa lo citado de lo compuesto, que es la regla que el repositorio ya aplica a γ_p.

---

## 12. Lo que este diseño deja abierto

Se listan para que no se lean como resueltas. Ninguna bloquea el arranque de S12.

| # | Decisión abierta | Quién la cierra |
|---|---|---|
| **1** | **La librería de PDF** para `normativa/extraccion/` (§10.5). `PyMuPDF` cubre texto e imagen; `pdfminer.six` solo texto. Dependencia **de test**. `CLAUDE.md` exige consultarla | **El usuario**, antes de S12 |
| **2** | Si `Fuente` guarda además el **número total de páginas** del PDF, para que T6 detecte una `pagina_pdf` fuera de rango sin abrir el archivo. Barato y probablemente sí | S12 |
| **3** | Dónde vive el **`caracter`** cuando una misma frase sostiene una exigencia para un material y una recomendación para otro. No hay caso hoy; lo habrá con las tablas de AASHTO | S12, si aparece |
| **4** | Si `Fundamento` se puebla en S12 o se difiere a S18. El esquema está; la carga es trabajo aparte y **no bloquea la ventana** | S12 / S18 |
| **5** | El formato exacto del **manifiesto generado** (§9.3, T8): mismo Markdown por bloques, o tabla por fuente. Afecta a la revisión humana, no al esquema | S12 |
| **6** | Cómo se **versiona** el registro cuando salga una edición nueva de una norma (E.030 ya cambió a RM 183-2026). `Fuente.reemplaza_a` está previsto; la política de migración de citas, no | Después de S21 |

Y una que **no** es de este diseño y conviene no confundir: la §15 del plan deja fuera de
alcance conseguir las fuentes ausentes. El registro las **declara**; traerlas es trabajo
de gabinete.

---

## 13. Trazabilidad: qué pieza cierra qué

| Pieza del esquema | Hallazgos / reglas que cierra o habilita |
|---|---|
| `Cita` internada con id (**D1**) | `NOR-PUE-01` (propagado a 6 puntos), R2 del plan, criterio de aceptación #1 |
| `Cita.titulo_numeral` | `NOR-PUE-01` |
| `Cita.pagina_impresa` + `pagina_pdf` + `Paginacion` | `MAT-O17`, `NOR-EG-01`, `NOR-HDS-01` |
| `Cita.texto_literal` verbatim + T5 | `NOR-HID-01` / `MAT-O7` (el 9.8 de Laushey), causa raíz de C11 |
| `Cita.caracter` (cinco valores) | `NOR-MEM-01`, `MAT-O13`, `NOR-HID-10` |
| `Verbatim` / `Transcripcion` / `Interpretacion` como **tipos** | `NOR-HID-04`, `NOR-HID-06` y su reincidencia en `76791d0` |
| `AfirmacionNegativa` | `NOR-VAC-01` (el vacío que no era un vacío) |
| `alcance` + `uso` + `Laguna` (§4) | `NOR-HID-11`, `NOR-AAS-01`, `NOR-E060-05`, trampa 1 del plan |
| `PendienteDeCondicion` ≠ `NoUsada` | `NOR-AAS-01` — y la distinción que el encargo pedía |
| `Modificador.orden` | `NOR-AAS-05`, trampa 2 del plan, **conflicto vinculante #3** |
| `Modificador.piso` + `Laguna` | `NOR-AAS-05`, `RECUBRIMIENTO_MP_FACTOR_AC_LAGUNA` |
| `CondicionAplicacion` con `BLOQUEA` por defecto | R4 del plan, `NOR-SUE-01`, `NOR-AAS-06`, trampa 4 |
| `Efecto.ADVIERTE` + `justificacion_de_no_bloquear` | `NOR-HDS-05` (cerrado parcial) |
| Familia cerrada `RangoNormativo` | §4.2 del plan, `NOR-HID-04`, `NOR-HID-07`, trampa 3 |
| `Catalogo` ≠ `Fuente` | `NOR-PRO-01`, `NOR-PRO-02`, modo `de_catalogo` de §4.3, trampa 5 |
| `Fuente.ausente` + `Ausencia` | §15 del plan; `v_max_hdpe`, `v_max_tmc`, `D_max["hdpe"]` |
| `Fuente.convive_con` | `MAT-X5`, `MAT-O12` (las dos ediciones de HDS-5) |
| `CorrespondenciaDeTablas` | `NOR-PUE-10`, `NOR-AAS-01`; el cruce que se saltaba 8 de 21 filas |
| `Discrepancia` | `MAT-O2`, `MAT-X2`, las tres erratas del Manual, y la obligación tercera de `CLAUDE.md` |
| `CeldaSinValor` (enum) | `NOR-PUE-09`, `MAT-D15` / `NOR-AAS-04`, `NOR-PUE-11` |
| `Fundamento.verbo` ↔ `caracter` | `NOR-MEM-01`, criterios de aceptación #7 y #8 |
| Snapshot de M0 + trinquete (§10.2) | Que la migración no mueva ningún número |
| T8 + T9 | **`NOR-MAN-04`**, `NOR-MAN-02`, `SIS-A-20`, `NOR-COH-03` |
| T0 (`sha1`) | Que «verificado» siga siendo cierto mañana |

### Los tres conflictos vinculantes que este diseño toca

Comprobado contra la hoja `Conflictos` de `matriz_cruzada_auditorias.xlsx`, como manda la
regla 2 de `CLAUDE.md`. **Ninguno se resuelve aquí; los tres se respetan:**

- **#3 · Recubrimiento AASHTO 75 mm.** «Corregir a 76,2 sería resolver el síntoma:
  primero declarar la categoría de refuerzo y el factor por a/c.» El esquema **no fija
  ningún número**: pone la categoría como `CondicionAplicacion` que bloquea (§6) y el
  factor como `Modificador` con `orden` (§5). Es la resolución, hecha estructura.
- **#4 · h_eq.** «No hay contradicción sino un dato faltante: la orientación del muro.»
  El esquema lo modela `PorDatoDeSitio("orientacion_muro_respecto_al_trafico")` con
  `BLOQUEA` — y **no** escribe ni 0,60 ni 1,12.
- **#8 · Clase de Sitio F.** «No cablear todavía: resolver primero la premisa.» El
  registro le da sitio a la premisa como `Discrepancia` entre E.030 (perfil S5) y AASHTO
  / Manual de Puentes (Clase F), en estado `ABIERTA`, sin decidirla. S13 la decide.

---

## 14. Resumen operativo para S12

1. Crear `src/normativa/` con `esquema.py`, `fuentes.py`, `citas.py`, `tablas.py`,
   `rangos.py`, `fundamentos.py`, `extraccion/`. Reexportar los tipos desde `modelos.py`.
2. **Fotografiar antes de tocar**: `tests/fixtures/snapshot_pre_registro.json` con los
   213 nombres públicos de `constantes_normativas.py` y sus valores (§10.1, M0).
3. Cargar las 13 fuentes con `sha1` (ya calculados, §11.0 trae el del Manual de
   Hidrología) y **medir la `Paginacion` de cada una**. Las de AASHTO y HDS-5 son
   `PorCapitulo` y sus bases están medidas en la §3.2; las demás hay que determinarlas.
4. Declarar las fuentes ausentes con su `Ausencia` (§8).
5. Migrar tabla a tabla en el orden de la §10.3, un commit por tabla, con el snapshot en
   verde en cada uno.
6. Escribir la guardia: T0–T22 (§9). Empezar por las estructurales, que no necesitan la
   decisión abierta #1.
7. Generar el manifiesto desde el registro y bajar `MAX_REFERENCIAS_DE_PROSA` a 0.

**Criterio de salida del diseño, que S12 puede comprobar:** ningún numeral, página ni
título de tabla vive fuera de `src/normativa/`; ninguna cita verificada lleva
`POR_TRANSCRIBIR`; y las dos tablas de la §11 están en el registro con todos sus campos
rellenos y `verificado` firmado por el subagente `verificador-normativo`.
