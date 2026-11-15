# Resolución del conflicto #8 — la clase de sitio

**Sesión S13 de `docs/hoja_de_ruta_correcciones_v12.md`. Análisis y decisión, sin cableado.**
Lo aplica S14 (§5 de este documento). Hallazgos: `NOR-AAS-02`, `NOR-VOC-04`,
`NOR-E030-02`, `NOR-MEM-03`, `SIS-B-01`, `SIS-D-01`.

> **Qué es este documento.** La decisión sobre una premisa que el expediente tenía
> abierta, tomada contra las fuentes primarias y no contra la hoja de ruta. **No cablea
> nada**: cablear `clase_sitio` antes de resolver la premisa haría que la memoria
> declarase formalmente una clasificación que la fuente no sostiene, que es peor que no
> declararla (conflicto #8, vinculante). Las doce citas en que se apoya están en
> `src/normativa/citas.py`, verificadas contra su PDF por el subagente
> `verificador-normativo` y comprobadas por los tests T2/T3/T6.

---

## 0. La decisión, en una página

**El expediente deja de atribuirse la Clase de Sitio F.** No porque la fuente diga que el
sitio no lo es, sino por algo más fuerte y que nadie había leído: **las dos fuentes
prohíben expresamente *suponer* la clase E o F sin dato geotécnico o determinación de la
autoridad competente**, y este expediente no tiene ninguna de las dos.

| | |
|---|---|
| **`clase_sitio`** | pasa de `[A]` con valor `"F_con_factores_tabulados_por_adopcion"` a **`[S]` sin valor**. Es un dato de sitio pendiente de ensayo, no una elección del proyectista |
| **Lo que el proyecto hace mientras tanto** | ya está declarado, ya es correcto y ya se imprime: `F_pga = ("C", "D", "E")`, envolvente 1.0. **No cambia** |
| **Lo que la memoria declara** | el vacío (por `criterios_sin_valor()`) y la nota normativa de §4. **No** una clase de sitio |
| **Lo que NO se hace** | no se invoca `clase_sitio` desde la cadena sísmica. Un `valor=None` invocado detendría todo el cálculo del cabezal, y no hay norma que lo exija: la cadena consume `F_pga`, no `clase_sitio` |

El valor que se retira glutinaba **dos cosas distintas** en una sola cadena: una
clasificación que la fuente no sostiene (`F`) y una decisión de procedimiento que sí es
del proyectista (`con_factores_tabulados_por_adopcion`). La segunda ya vive, bien
etiquetada y con su rango, en `F_pga`. Separarlas es toda la corrección.

**Consecuencia sobre `SIS-B-01`:** la memoria pasa a declarar `clase_sitio` **sin
cablear ninguna invocación**. Un criterio con `valor=None` entra por `criterios_sin_valor()`,
que es una de las puertas de M11 que hoy no lo recogía porque el criterio *tenía* valor.
El defecto era el valor, no la falta de cableado.

---

## 1. Qué se verificó, contra qué, y con qué método

Tres subagentes `verificador-normativo` independientes, uno por documento, cada uno con
el desfase de paginación **medido por él y no asumido**:

| Documento | Desfase verificado | Alcance del barrido |
|---|---|---|
| E.030 (RM 183-2026-VIVIENDA) | impresa = PDF (68 pág., 0 discrepancias) | Art. 4, 7.3, 11.1, 14.6, 17, 22.4; Tablas Nº 1 a Nº 5; Anexo III |
| Manual de Puentes (MTC) | impresa = PDF − 1 (650 pág. con marcador, 0 discrepancias) | 673 páginas; `licuef*`, «clase de sitio», «factor de sitio», «dispensa*» |
| AASHTO LRFD 9.ª ed. (2020) | Sec. 3 → PDF = impresa + 54; Sec. 10 → + 1289 | 1905 páginas; `liquef*`, `Site Class F`, `response analysis is not required` |

Las doce citas resultantes están internadas en `src/normativa/citas.py` con firma
`fase1/S13 · verificador-normativo` y sha1 del PDF. El registro pasa de **78 a 90 citas
verificadas**; los tests T2 (el texto literal está en su página), T3 (el título del
numeral está donde se dice) y T6 (la página PDF es la que predice la regla de paginación)
las cubren.

> **Un artefacto de extracción que hubo que resolver primero.** E.030 no tenía ni una
> cita en el registro, y la razón no era descuido: su PDF emite la ligadura `U+FB01`
> seguida de un espacio —`clasiﬁ cación`, `perﬁ les`, `especíﬁ co`—, de modo que ninguna
> frase entera de la norma se encontraba en su propia página. La prohibición de la fila
> S5 cruza tres ligaduras rotas. Se añadió a `extraccion.pdf.normalizar` una regla tan
> estrecha como la que ya existía para el guion de fin de línea: espacio pegado a un
> codepoint de ligadura (`U+FB00`–`U+FB06`), aplicada **antes** de la descomposición NFKD
> para que no pueda tocar una «fi» corriente. Sin ella, las citas de E.030 habrían tenido
> que recortarse justo donde importan.

> **Una afirmación de subagente que NO se acepta.** El verificador del Manual de Puentes
> concluyó que el Manual «omite el primer bullet de la Tabla 3.10.3.1-1 de AASHTO (el de
> *soils vulnerable to potential failure or collapse under seismic loading such as
> liquefiable soils*)». **Es falso, y no leyó AASHTO para decirlo.** El verificador que sí
> lo leyó confirma que la fila F de AASHTO tiene **tres** categorías, las mismas tres que
> el Manual, y que `liquef` no aparece en la página PDF 156 entera. Ese primer bullet es
> de **ASCE 7**, no de AASHTO LRFD. Queda anotado porque es exactamente el mecanismo que
> produjo el defecto original: recordar una regla de otra norma y atribuírsela a la que se
> está citando.

---

## 2. Las cinco preguntas

### 2.1 ¿E.030 y AASHTO clasifican los suelos licuables en la misma categoría? Si no, ¿en qué discrepan exactamente?

**No.** Discrepan en tres planos, y conviene no confundirlos porque solo uno decide.

**(a) Son dos taxonomías con variables distintas.** E.030 clasifica *perfiles de suelo*
S0–S5 (Art. 14.6, «Los tipos de perfiles de suelo son:», pág. impresa 10) y su Tabla Nº 2
«Tipos de perfiles de suelo» tiene tres columnas —`Perfil`, `Nombre`, `Descripción`—: es
**prosa**, no umbrales. AASHTO clasifica *Site Class* A–F por rigidez **medida**: «Sites
shall be classified by their stiffness as determined by the shear wave velocity in the
upper 100 ft» (Art. 3.10.3.1, pág. impresa 3-101 / PDF 155). No son dos nombres de la
misma escala, y no hay tabla de equivalencia en ninguno de los dos documentos.

**(b) E.030 nombra los suelos licuables; AASHTO y el Manual no.** La fila S5 «Suelos
excepcionales» de E.030 tiene diez viñetas y **la primera es «Suelos potencialmente
licuables»** (pág. impresa 11). La fila F de AASHTO dice, entera:

> «Soils requiring site-specific evaluations, such as: • Peats or highly organic clays
> (H > 10.0 ft…) • Very high plasticity clays (H > 25.0 ft with PI > 75) • Very thick
> soft/medium stiff clays (H >120 ft)»
> — Tabla 3.10.3.1-1, pág. impresa **3-102** (PDF 156)

`liquef` **no aparece en esa página entera**, y en las 1905 páginas del documento los
conjuntos {páginas con `liquef`} y {páginas con «Site Class F»} son **disjuntos**. El
Manual de Puentes traduce las mismas tres categorías, con el mismo «tales como», en su
Tabla 2.4.3.11.2.1.1-1 (pág. impresa **122** / PDF 123), y tampoco la nombra.

**(c) AASHTO trata la licuefacción por otra vía.** Art. 10.5.4.2 «Liquefaction Design
Requirements», pág. impresa **10-34** (PDF 1323), Sección 10 *Foundations*. Su disparador
es *zona sísmica 3 o 4* **más** *napa freática en los 50 ft superiores* **más**
*características de suelo* (`(N1)60`, `q_ciN`, `V_s1` o unidad geológica con antecedente):
**ninguna de las tres condiciones es la clase de sitio**, y «Site Class F» no aparece en
ninguna página de la Sección 10. El Manual hace lo mismo: once apariciones de `licuef*` en
ocho páginas, todas en exploración del subsuelo, pilotes, *downdrag* y el Apéndice A11;
ninguna en el numeral de clases de sitio. **No existe en el Manual un numeral titulado
«Licuefacción».**

**La formulación exacta, y por qué importa la precisión.** No es que AASHTO *excluya* los
suelos licuables de la Clase F: la fila se abre con «**such as**», lista abierta, de modo
que del silencio no se sigue la exclusión. Esta es la acotación que la refutación
adversarial `R95-073` ya le había hecho a la primera versión de `NOR-AAS-02`, con razón.
Lo defendible es la afirmación **negativa**: *el salto «suelo licuable → Clase F» no lo
escribe ninguno de los dos documentos que el criterio invoca.*

Hay además una tensión dentro del propio AASHTO, declarada en
`DIS-AASHTO-F-LISTA-ABIERTA`: el articulado dice «such as» y el comentario —Tabla
C3.10.3.1-1 «Steps for Site Classification», pág. impresa **3-103** (PDF 157)— la llama
«**the three categories** of Site Class F». Gana el articulado por jerarquía. **Pero la
decisión no depende de cómo se resuelva:** si la lista es cerrada, la premisa es *falsa*;
si es abierta, la premisa es *no sostenida*. Por las dos lecturas el salto sigue sin estar
escrito.

Y hay algo que el debate «abierta o cerrada» tapaba: el paso 1 del comentario no es
retórica, es un **procedimiento**. Manda comprobar esas tres categorías y, si el sitio no
cae en ninguna, seguir al paso 2 (capa blanda → Clase E) y al paso 3 (calcular `v̄s`, `N̄`
o `s̄u` sobre los 100 ft superiores → Clase A a E). **En ninguno de los tres pasos hay una
ruta que lleve de «suelo licuable» a la Clase F.**

**Dónde sí convergen, que es lo que faltaba mirar.** Los dos esquemas discrepan en el
**criterio** y coinciden en la **consecuencia**: ninguno tabula un factor para su categoría
excepcional.

| | Categoría excepcional | ¿Factor tabulado? |
|---|---|---|
| E.030 | S5 «Suelos excepcionales» (Tabla Nº 2, pág. 11) | **No.** S5 no tiene fila en la Tabla Nº 3 ni columna en la Nº 4 «Factor de suelo S» ni en la Nº 5. En la Zona 4, ya la columna S4 dice «Requiere un análisis de respuesta de sitio» (pág. impresa 13) |
| AASHTO / Manual | Site Class F | **No.** Cinco asteriscos en las cinco columnas, en las tres tablas de AASHTO y en las cinco del Manual |

E.030 no tiene `F_pga`, `Fa` ni `Fv`: su aparato es `S`, `T_P`, `T_L`. Emparejar «S5» con
«Clase F» —como hace la hoja de ruta con una barra— sugiere una equivalencia que **ninguna
de las dos fuentes imprime**.

### 2.2 ¿Puede el expediente trasladar la clasificación de un esquema al otro? ¿Bajo qué declaración expresa?

**No puede, y no hay declaración que lo habilite.** Ésta es la respuesta que cambia el
resultado de la sesión, y sale de un texto que está en el **articulado** y que el
expediente no había leído. Al pie de la Tabla 3.10.3.1-1, pág. impresa **3-102** (PDF 156):

> «Where the soil properties are not known in sufficient detail to determine the site
> class, a site investigation **shall** be undertaken sufficient to determine the site
> class. **Site classes E or F should not be assumed** unless the authority having
> jurisdiction determines that site classes E or F could be present at the site or in the
> event that site classes E or F are established by geotechnical data.»

El Manual de Puentes lo **endurece** al traducirlo (pág. impresa **122** / PDF 123):

> «Las clases de Sitio E o F **no serán supuestas** a no ser que la Entidaddetermine la
> clase de sitio E o F o estas sean establecidas por datos geotécnicos.»

*(«Entidaddetermine», sin espacio, es errata del impreso y se transcribe tal cual.)*

De modo que el expediente no necesitaba una autorización para suponer la Clase F: **tenía
una prohibición expresa de suponerla**, con dos puertas de salida y ninguna abierta —no
hay determinación de la Entidad en el expediente, y el SPT está pendiente—. Suponerla no
es una adopción declarable del proyectista: es lo que la norma veda. Y como el Manual
endurece a AASHTO, el resultado **no depende de qué Vía de Sec. 0.2 se elija**.

La misma cláusula trae la otra mitad, que es un **deber positivo**: no dice «no supongas y
sigue», dice **investiga**. Ése es el trabajo que el expediente tiene pendiente, y ahora
tiene numeral.

**Y el traslado, además, no compraría nada.** Si se trasladase S5 → Clase F, la fila de
destino no tiene factor: son cinco asteriscos y una nota que exige un estudio. La premisa
no aporta un número al cálculo y sí le aporta al expediente una afirmación refutable de un
vistazo.

**Lo que sí se puede declarar** —y es lo que la memoria hará— son tres hechos, cada uno con
su cita, sin traslado entre ellos:
1. E.030 clasifica el sitio como perfil **S5**, por su primera viñeta, y esa clasificación
   trae una prohibición condicionada de construir (`E030.T2#S5`).
2. La clase de sitio de AASHTO / Manual de Puentes está **indeterminada**, y las dos
   fuentes prohíben suponerla E o F (`AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES`,
   `MP.2.4.3.11.2.1.1#EXCEPCIONES`).
3. Mientras esté indeterminada, el factor de sitio se lee sobre las filas C, D y E y se
   adopta la envolvente (`F_pga`, ya declarado).

### 2.3 Si el sitio es Clase F para AASHTO, ¿existe factor de sitio tabulado, o la norma exige análisis de respuesta dinámica?

**No existe factor tabulado en ninguna tabla de ninguno de los dos documentos, y el
análisis se exige con `shall`.** Ocho tablas barridas, ocho veces la misma respuesta:

| Documento | Tabla | Fila F |
|---|---|---|
| AASHTO | 3.10.3.2-1 `F_pga` (pág. impresa 3-105) | `F²` + cinco asteriscos |
| AASHTO | 3.10.3.2-2 `Fa` (3-105) · 3.10.3.2-3 `Fv` (3-106) | ídem |
| Manual | 2.4.3.11.2.1.2-1 `F_pga` · -2 `Fa` · -3 `Fv` (pág. impresa 123) | `F²` + cinco asteriscos |
| Manual | Apéndice A3, Tablas 1 y 2 (pág. impresa 548) | celda fusionada: «Se deben considerar investigaciones geotécnicas y análisis dinámicos específicos para la zona de estudio.» |

**No hay dispensa por periodo corto.** Verificado exhaustivamente: `response analysis is
not required` da **0 coincidencias en las 1905 páginas** de AASHTO; `Site Class F` aparece
en exactamente 5 páginas (PDF 125, 154, 157, 159, 160) y en ninguna hay condicionamiento
por periodo fundamental. En el Manual, «sitio clase F» aparece 4 veces y ninguna es una
salvedad. La afirmación de `Sec. 0.5` —que la dispensa **no existe**— queda **confirmada
por la fuente primaria**.

> **Corrección de anclaje, y el expediente citaba el texto más débil de los tres.** La
> exigencia con `shall` está en el **Art. 3.10.2 «Seismic Hazard»**, pág. impresa **3-71**
> (PDF 125): «A Site-Specific Procedure **shall** be used if any one of the following
> conditions exist: … The site is classified as Site Class F (Article 3.10.3.1),». Y se
> repite en el Art. 3.10.2.2 (pág. impresa 3-100). La **Nota 2** de las tablas de factores
> —que es lo que `Sec. 0.5` y el criterio venían citando— dice **`should`**. El Manual
> tiene su propio articulado: num. **2.4.3.11.2 «Peligro Sísmico»**, pág. impresa **121**
> (PDF 122), «El procedimiento especificado de sitio **será usado** si existen las
> siguientes condiciones: … Si el sitio está clasificado como sitio clase F».
> La afirmación del expediente era **cierta**; el anclaje se apoyaba en una recomendación
> para sostener una exigencia. No es discrepancia entre fuentes: es cita corta, y se
> corrige citando el `shall`.

**Y el argumento que cierra la cuestión por lo positivo.** El propio Art. 10.5.4.2 manda
analizar un sitio licuable en dos configuraciones y dice: «**The design spectrum should be
the same as that used in the nonliquefied configuration**» (pág. impresa 10-34), y acota el
espectro específico de sitio a no menos de dos tercios del general «**modified by the site
factors in Article 3.10.3.2**» (pág. impresa 10-35). Es decir: **AASHTO espera que a un
sitio licuable le aplique un factor de sitio tabulado de 3.10.3.2.** Eso es incompatible
con que la licuefacción lo hiciera Clase F por sí sola —la fila F no tiene factor con que
empezar—. Las dos reglas solo son coherentes si un suelo licuable puede clasificar A–E y
evaluarse aparte, **que es exactamente el reparto que este expediente ya hace con su SPT de
15 m**.

Esto convierte `NOR-AAS-02` de argumento por silencio —que `R95-073` había acotado— en
argumento por **coherencia interna de la fuente**. Es la razón por la que la resolución no
depende ya de cómo se lea el «such as».

### 2.4 ¿Qué debe decir exactamente la memoria?

El texto exacto está en la **§4**. Su forma, en tres reglas:

1. **No declara clase de sitio.** Declara que está indeterminada, que las fuentes prohíben
   suponerla E o F, y qué ensayo la cierra.
2. **Separa las tres afirmaciones** de §2.2 sin traslado entre ellas, cada una con su cita.
3. **`F_pga = 1.0` se defiende sin mencionar la Clase F como clase del sitio**, y diciendo
   por qué la fila F no está entre las leídas: no porque el sitio no sea F, sino porque esa
   fila **no da factor** y porque suponerla está vedado.

Esto completa `NOR-MEM-03`, que ya estaba cerrado a medias: la convergencia C/D/E dejaba
fuera la fila que el propio expediente reclamaba. Ahora el expediente no reclama ninguna, y
la ausencia de F queda explicada por la fuente en vez de por omisión.

### 2.5 ¿Es `clase_sitio` un criterio `[A]` con valor, o un vacío `[A]` sin valor que bloquea hasta el SPT?

**Ninguna de las dos: es un `[S]` sin valor.** Contra la taxonomía de `CLAUDE.md`, punto
por punto.

**Por qué no es `[A]`.** La regla que separa `[S]` de `[A]` es: «un `[A]` se defiende con
un rango de sensibilidad porque hubo elección; un `[S]` no tiene rango que elegir y se
defiende con la trazabilidad de la lectura». La clase de sitio **no es una elección**: el
Art. 3.10.3.1 dice que se determina «by their stiffness as determined by the shear wave
velocity in the upper 100 ft», y el paso 3 del comentario da el procedimiento de cálculo.
Es una **medición**. Y la regla que separa `[N]` de `[S]` la coloca sola: el valor cambia
al mover la obra de sitio y **no** al cambiar de proyectista.

El propio archivo ya lo estaba confesando sin sacar la consecuencia. `clase_sitio` es hoy
**el único `[A]` con valor que no declara sensibilidad**, y su campo
`verificacion_pendiente` explica por qué: «declarar un rango de clases alternativas sería
fijar la respuesta antes de resolver la pregunta». Eso no es un `[A]` bien defendido: es la
taxonomía avisando de que la etiqueta está mal. Un valor que no puede declarar rango porque
la pregunta no está resuelta no es una elección; es **un hecho que falta**.

**Por qué no es un vacío `[A]`.** La regla de `CLAUDE.md` para los vacíos —«si la hoja de
ruta NO dice nada sobre algo que necesitas… `valor=None`, etiqueta `[A]`»— gobierna el
**vacío normativo**: la norma no fija el valor y hay que adoptarlo. Aquí no hay vacío
normativo. La norma **sí** dice cómo se determina la clase, con qué variables y sobre qué
profundidad; incluso dice qué hacer mientras no se sepa (investigar, y no suponer E ni F).
Lo que falta no es la regla: falta **la medición**. Eso es un dato de sitio pendiente de
ensayo, y el proyecto ya tiene la vía para eso —`[S]` en `criterios_adoptados.py` con el
campo `trazabilidad`, exactamente como está previsto para «un `[S]` pendiente de ensayo que
además comparte tablero con los criterios»—.

**Y el `[A]` que sí existe no desaparece: ya estaba en otro sitio, bien puesto.** Lo que
el proyecto elige es **sobre qué filas lee la tabla mientras el hecho falta**, y eso es
`F_pga = ("C", "D", "E")`, `[A]`, con su sensibilidad declarada 0.9–1.0. Es el mismo
reparto R1 que el proyecto ya aplicó dos veces —la tabla es `[N]`, la fila es `[A]`— y
está bien resuelto. La corrección de esta sesión **no lo toca**.

Dicho de una vez: el valor `"F_con_factores_tabulados_por_adopcion"` era **dos cosas
pegadas** —una clasificación (`F`) y un procedimiento (`con factores tabulados por
adopción`)—, y por eso no se podía ni etiquetar ni sensibilizar. Separadas, cada mitad cae
donde le toca y las dos quedan defendibles.

**¿Bloquea hasta el SPT?** Bloquea **si se invoca**, como todo `valor=None`. Y no se debe
invocar, por una razón normativa y no de comodidad: **la cadena sísmica no consume la clase
de sitio, consume el factor**, y el factor está declarado por `F_pga` con su fundamento
propio. Invocar `clase_sitio` desde `cadena_sismica()` detendría el dimensionamiento entero
del cabezal sin que ninguna norma lo exija —y contra el hecho de que el proyecto **puede**
dimensionar hoy, bajo adopción declarada—. El vacío se **declara**, no se interpone.

> **Diferencia con `PERFIL_SUELO_PRESUNTO`, que conserva su valor `"S5"` y su etiqueta
> `[S]`.** No es incoherencia: la asimetría es de las fuentes. El perfil S5 se alcanza por
> **descripción** —la Tabla Nº 2 tiene columna «Descripción» y su fila S5 es una lista de
> condiciones cualitativas, la primera «Suelos potencialmente licuables»—, y la
> caracterización disponible del corredor (arenas saturadas, NF a 1.4 m, llanura del Bajo
> Piura) la satisface a la vista. La clase A–E de AASHTO se alcanza por **números** que
> nadie ha medido, y la F por una evaluación específica que nadie ha hecho. Una se puede
> presumir declarándolo; la otra la norma **prohíbe** presumirla. Por eso una conserva
> valor con `reemplazado_por = SPT` y la otra no puede conservarlo.

---

## 3. Los cuatro defectos que se reportan contra la hoja de ruta

`CLAUDE.md` obliga, cuando la fuente primaria gana, a tres cosas: declararlo en el punto de
uso, reportar el defecto contra la hoja de ruta, y **dejar dicho que la hoja de ruta sigue
mal mientras no se corrija**. Las tres quedan cumplidas en objetos, no en prosa: cuatro
`Discrepancia` en `src/normativa/discrepancias.py`, que el test T20 enumera.

| id | Objeto | Estado |
|---|---|---|
| `DIS-HR-CLASE-DE-SITIO-F` | la premisa de Sec. 0.5 | **abierta contra la hoja de ruta** |
| `DIS-HR-VIA-DE-LA-LICUEFACCION` | Sec. 0.5 hace de la licuefacción la *causa* de la clase de sitio; AASHTO la evalúa en 10.5.4.2 y espera factor tabulado | **abierta contra la hoja de ruta** |
| `DIS-HR-30M-VS-100FT` | «30 m» atribuido al Art. 3.10.3.1, que imprime «the upper 100 ft» | **abierta contra la hoja de ruta** |
| `DIS-AASHTO-F-LISTA-ABIERTA` | articulado «such as» vs. comentario «the three categories» | resuelta (gana el articulado) |

**La hoja de ruta v8 sigue mal en estos cuatro puntos mientras no se corrija**, y quien la
lea sin leer el código diseñará con la premisa equivocada. Además, y son defectos de
literalidad de cita en un pasaje que la hoja presenta entrecomillado (Fase 0-bis):

1. Empalma como texto contiguo la **viñeta 1** («Suelos potencialmente licuables») y la
   **viñeta 10** (la prohibición) de la celda S5, con ocho viñetas elididas y sin marca.
2. Escribe «no están cubiertos en la clasificación de la Tabla Nº 2»; la fuente imprime
   «no están cubiertos en la clasificación **establecida en** la Tabla Nº2 **de la presente
   Norma Técnica**».
3. Escribe «salvo que se efectúe»; la fuente imprime «salvo que**,** se efectúe», con coma.
4. Escribe «la condición **S5 / Clase F**» (Fase 0-bis, punto 2). La barra asimila dos
   taxonomías que ninguna de las dos fuentes empareja. Es el defecto de fondo, dicho en un
   signo de puntuación.

`constantes_normativas.E030_S5_TEXTO` **sí** transcribe el pasaje exacto: el defecto es de
la hoja de ruta, no del código.

**Un hallazgo colateral, ajeno a este conflicto y que no se resuelve aquí.** Los rótulos de
columna de la tabla de `F_pga` difieren **dentro del propio Manual**: el cuerpo normativo
(pág. impresa 123) usa estrictos «PGA < 0.10 … PGA > 0.50» y la Tabla 1 del Apéndice A3
(pág. impresa 548) usa «PGA≤ 0.10 … PGA≥ 0.50». Con `PGA = 0.50` **exacto** —el de este
proyecto— la diferencia decide si el dato cae dentro de la columna o en la frontera sujeta
a interpolación. Agrava `NOR-PUE-11`: no es solo que el repositorio lea `≥` donde hay `>`,
es que **la fuente se contradice a sí misma justo donde este proyecto se apoya**. Se
recomienda resolverlo citando el cuerpo normativo, que prevalece sobre un apéndice
metodológico. *(Y ojo con ese apéndice: su «Fpga = 1.00» es específico de **Lima
Metropolitana sobre roca Clase B**, no una regla general. Ninguna cita del proyecto debe
apoyarse ahí.)*

---

## 4. El texto exacto que la memoria debe imprimir

Va en `M9.condicion_normativa_cabezal()`, que es el vehículo que ya lleva a las dos
plantillas la nota del perfil S5 y las tres erratas del Manual. **Se escribe sin tildes**,
como el resto de ese módulo y como lo imprime M11 hoy; los textos normativos
entrecomillados salen del registro y **sí** conservan las suyas (invariante T21).

### 4.1 La clase de sitio — reemplaza a cualquier declaración de Clase F

```
Clase de sitio sismica: INDETERMINADA. Este expediente NO se atribuye la
Clase de Sitio F, y no puede: el articulado que la define prohibe suponerla.
AASHTO LRFD 9a ed., Art. 3.10.3.1, al pie de la Tabla 3.10.3.1-1 (pag.
impresa 3-102): "Site classes E or F should not be assumed unless the
authority having jurisdiction determines that site classes E or F could be
present at the site or in the event that site classes E or F are established
by geotechnical data." El Manual de Puentes lo endurece en su num.
2.4.3.11.2.1.1 (pag. impresa 122): "Las clases de Sitio E o F no seran
supuestas a no ser que la Entidaddetermine la clase de sitio E o F o estas
sean establecidas por datos geotecnicos." Este expediente no tiene
determinacion de la Entidad ni datos geotecnicos: el SPT esta pendiente. La
misma clausula fija el deber positivo que queda abierto: "a site
investigation shall be undertaken sufficient to determine the site class".
```

```
Por que el expediente decia Clase F, y por que deja de decirlo: el salto de
"suelo potencialmente licuable" a "Clase de Sitio F" NO lo escribe ninguno de
los dos documentos que la cadena sismica invoca. La fila F de la Tabla
3.10.3.1-1 enumera turbas o arcillas altamente organicas, arcillas de muy
alta plasticidad y estratos potentes de arcilla blanda, y ninguna es
licuefaccion; en las 1905 paginas de AASHTO no hay una sola donde coincidan
"liquefaction" y "Site Class F". La licuefaccion la trata el Art. 10.5.4.2
"Liquefaction Design Requirements" (pag. impresa 10-34), por via de
cimentaciones y disparada por zona sismica, napa freatica y caracteristicas
de suelo, nunca por la clase de sitio. Quien SI clasifica los suelos
licuables en su categoria excepcional es E.030, en el perfil S5, que es de
donde el expediente sacaba la letra: son dos esquemas distintos y discrepan
justo en el rasgo que motivaba la clasificacion de este sitio.
```

```
Y no es solo que la norma calle: el Art. 10.5.4.2 manda analizar el sitio
licuable en configuracion no licuada y licuada "with the design spectrum the
same as that used in the nonliquefied configuration", y acota el espectro
especifico de sitio a no menos de dos tercios del general "modified by the
site factors in Article 3.10.3.2". AASHTO ESPERA que a un sitio licuable le
aplique un factor de sitio tabulado, cosa imposible si la licuefaccion lo
hiciera Clase F, porque la fila F no tiene factor. El reparto coherente es el
que este expediente ya hace: clasificar por rigidez medida y evaluar la
licuefaccion aparte, con el SPT de 15 m del Art. 38 de E.050.
```

```
Lo que cierra este vacio, y son DOS ensayos de profundidades distintas que
conviene pedir juntos: (1) la caracterizacion de los 100 ft superiores
(30.48 m) -- Vs30 o N_barra --, que es la profundidad que el Art. 3.10.3.1
escribe y con la que se lee la clase; y (2) si esa caracterizacion diera
Clase F, el analisis de respuesta dinamica de sitio, que el Art. 3.10.2 exige
con "shall" y el num. 2.4.3.11.2 del Manual con "sera usado". NO lo cierra el
SPT de licuefaccion de 15 m de E.050 Art. 38: ese ensayo responde a otra
pregunta y se detiene a mitad de la columna que esta clase necesita.
```

### 4.2 El factor de sitio `F_pga = 1.0` — sustituye la justificación actual

```
Factor de sitio F_pga = 1.0, adoptado como ENVOLVENTE de las filas C, D y E
de la Tabla 2.4.3.11.2.1.2-1 al PGA de este proyecto (1.0, 1.0 y 0.9): la
tabla es [N] y la eleccion de filas es [A]. Se declaran esas tres, y no una,
porque la clase de sitio esta indeterminada. A y B quedan fuera por ser las
filas de roca, y esa exclusion no es cosmetica: el num. 2.8.1.1.14.2.1 da a
las cimentaciones en Clase A o B una expresion distinta de k_h0.
```

```
Por que la fila F no esta entre las leidas, dicho con precision para que no
se lea al reves: NO porque se haya descartado que el sitio sea Clase F -- eso
lo decide la campana geotecnica --, sino por dos razones que valen hoy. La
primera, que esa fila NO DA FACTOR: la tabla le pone asterisco en las cinco
columnas y su Nota 2 remite a "investigaciones geotecnicas especificas del
sitio y analisis de respuesta dinamica de sitio, para todos los sitios en
sitio clase F". Elegirla no seria leer un valor, seria leer una exigencia de
estudio. La segunda, que suponerla esta expresamente vedado mientras no haya
dato geotecnico. Si la campana devolviera Clase F, no queda fila con factor:
queda el estudio, y esta memoria no podria cerrarse sin el.
```

```
Alcance de "conservador", sin coartada: los factores tabulados permiten
DIMENSIONAR el elemento estructural dentro del marco tabulado. No constituyen
una evaluacion del riesgo de licuefaccion, que sigue siendo el condicionante
tecnico no resuelto del proyecto, y los efectos de la licuefaccion --
perdida de resistencia, asentamiento, desplazamiento lateral -- quedan fuera
del alcance de este calculo y remitidos al estudio geotecnico del expediente.
Un analisis de respuesta especifica de sitio puede arrojar valores MAYORES
que los tabulados: la adopcion no es conservadora por construccion, y por eso
la eleccion de filas es [A] y no [N->].
```

### 4.3 La desambiguación de «Clase F» — `NOR-VOC-04`

Toda aparición de «Clase F» en la memoria lleva su calificador, **siempre**, porque son
taxonomías sin relación y las dos llegan al mismo documento:

```
"Clase de Sitio F" (sismica, AASHTO LRFD Tabla 3.10.3.1-1 / Manual de
Puentes Tabla 2.4.3.11.2.1.1-1: suelos que requieren evaluaciones
especificas de sitio)
```
```
"Concreto Clase F" (resistencia, EG-2013 Tabla 503-07, pag. 912: concreto
simple, f'c = 14 MPa)
```

Y una nota, porque el corpus tiene una **tercera** homonimia que hasta ahora nadie había
localizado y que conviene tener anotada antes de que aparezca:

```
"Clase F" designa TRES cosas sin relacion en las normas de este expediente:
la clase de sitio sismica (AASHTO / Manual de Puentes), la clase de
resistencia del concreto (EG-2013 Tabla 503-07) y la clase del acero ASTM
A668 que el propio Manual de Puentes tabula en su pag. impresa 289. Las dos
primeras llegan a esta memoria y van siempre calificadas; la tercera se
anota para que nadie la cruce con las otras dos.
```

---

## 5. Qué hace S14 con esto — y una trampa que le va a saltar

**No reabrir la decisión** (instrucción expresa del plan). Aplicarla:

1. **`criterios_adoptados.CRITERIOS["clase_sitio"]`**: `valor=None`, `etiqueta="S"`,
   `trazabilidad=…` (obligatoria para `[S]`), **sin** `sensibilidad` (la guardia la rechaza
   en un `[S]`), `reemplazado_por` = los dos ensayos de §4.1, y `sin_consumidor` con la
   razón de §2.5 —el vacío se declara, no se interpone—.
2. **No** añadir `ca.valor("clase_sitio")` a `cadena_sismica()` ni a ningún módulo de
   producción. El criterio entra en la memoria por `criterios_sin_valor()`, que es la
   puerta de M11 que le corresponde a un vacío declarado. Con eso `SIS-B-01` queda cerrado.
3. **`F_pga`**: reescribir solo la justificación con el texto de §4.2. El **valor
   `("C","D","E")` no cambia**.
4. **`M9.condicion_normativa_cabezal()`**: añadir los bloques de §4.1 y la nota de §4.3.
5. **Hoja de ruta v8, §0.5 y Fase 0-bis**: corregir los cuatro defectos de §3. Mientras no
   se corrijan, las tres `Discrepancia` abiertas los mantienen declarados.
6. **`clase_sitio.reemplazado_por`**: «100 ft (30.48 m)», no «30 m» (`DIS-HR-30M-VS-100FT`).
7. **Reanclar la exigencia** al Art. 3.10.2 / num. 2.4.3.11.2, no a la Nota 2 de la tabla.

> ### La trampa, y no es menor
>
> `tests/test_criterios_adoptados.py` tiene una guardia que prohíbe la subcadena **`excep`**
> en todos los campos de los ocho criterios sísmicos
> (`test_la_memoria_no_presenta_ninguna_excepcion_en_la_seccion_sismica`). Nació de un
> defecto real: el expediente llegó a afirmar que AASHTO concedía una **excepción** para
> la Clase F, y un revisor que lea «excepción» busca el numeral que la concede.
>
> Pero el texto que **resuelve** el conflicto está en un bloque que las dos fuentes titulan
> literalmente «**Exceptions**» / «**Excepciones**», y la fila de E.030 se llama «Suelos
> **excep**cionales». La guardia, tal como está, rechazaría la cita más fuerte del archivo.
>
> **S14 no debe borrar la palabra: debe estrechar la guardia** para que persiga la
> *afirmación* («excepción que autoriza saltarse el estudio») y no la *subcadena*. Borrar
> la palabra para pasar el test dejaría la decisión sin su cita, que es el modo exacto en
> que este expediente perdió la premisa la primera vez.
>
> Los otros dos tests a actualizar en la misma pasada:
> `test_la_clase_de_sitio_es_adopcion_declarada_y_no_dispensa_normativa` (afirma
> `etiqueta == "A"` y el valor retirado) y el bloque `CRITERIOS_SISMICOS`. Lo que esos
> tests deben seguir vigilando, con otra redacción, es lo que sigue siendo cierto y es el
> núcleo: **la dispensa por periodo corto no existe**, verificado ahora contra la fuente
> primaria con 0 coincidencias en 1905 páginas.

---

## 6. Contraste con la evidencia de cada ficha

Según la regla 3 de `CLAUDE.md`, cierre por cierre:

| ID | Qué pedía la ficha | Estado tras esta sesión |
|---|---|---|
| **`NOR-AAS-02`** | la premisa de Sec. 0.5 no la sostiene ninguna de las dos tablas | **Cierra el fondo; sigue `Cerrado parcial`.** La premisa queda **resuelta**, no ya «abierta»: verificada contra las dos fuentes, con el argumento reforzado (prohibición expresa + coherencia interna de 10.5.4.2) y con la acotación de `R95-073` incorporada en vez de ignorada. Lo que impide cerrarla: **el valor `"F_con_factores_tabulados_por_adopcion"` sigue en `criterios_adoptados.py`**, y retirarlo es cableado — S14. Mientras esté, el repositorio sigue conteniendo la premisa. Fase reasignada F2 → **F3** |
| **`SIS-B-01`** | `clase_sitio` no entra en `criterios_usados()` y la memoria nunca lo declara | **Sigue `Cerrado parcial`, y ahora tiene solución definida:** no se cierra cableando una invocación —lo que el conflicto #8 prohíbe y §2.5 desaconseja por norma— sino retirando el valor, con lo que el criterio entra por `criterios_sin_valor()`. S14 |
| **`SIS-D-01`** | `F_pga` y `clase_sitio` se defendían con premisas contradictorias | **Sigue `Cerrado parcial`.** La incoherencia ya estaba cerrada en S9; con la premisa retirada desaparece su causa. Falta el texto de §4.2 en el archivo. S14 |
| **`NOR-MEM-03`** | la convergencia C/D/E omitía la fila que el expediente reclamaba | **Cerrado, y ahora completo.** El expediente deja de reclamar la fila F; §4.2 explica su ausencia por la fuente. Sin cambio de estado |
| **`NOR-E030-02`** | S5 se declaraba «referencia muerta» y trae prohibición expresa | **Cerrado, y reforzado.** Se añade la primera cita verificada de E.030 al registro (`E030.T2#S5`), con el pasaje literal completo, y se precisa su estatuto: fila **nominal** de la Tabla Nº 2, **laguna** en las Tablas Nº 3, Nº 4 y Nº 5. Sin cambio de estado |
| **`NOR-VOC-04`** | «Clase F» significa dos cosas incompatibles | **Sigue `Pendiente`** (cluster C11, fase F3 = S14). §4.3 le da el texto exacto, y añade la tercera homonimia (acero ASTM A668 Clase F, Manual pág. impresa 289) que la ficha no había localizado |

**Nada de lo verificado contradice ninguna ficha.** La única corrección de fondo va contra
la *primera formulación* de `NOR-AAS-02` («las **tres** categorías… y ninguna es suelos
licuables»), y no la hace esta sesión: la hizo la refutación adversarial `R95-073`, y la
propia ficha ya la había incorporado. Lo que esta sesión aporta es que **el núcleo ya no
depende de ese argumento**: se apoya en la prohibición de suponer —articulado, sin lectura
doble— y en la coherencia interna del Art. 10.5.4.2.

---

## 7. Lo que esta sesión deliberadamente NO hace

- **No cablea nada.** El conflicto #8 es vinculante en los dos sentidos: no cablear antes
  de resolver, y no dar por cableado lo resuelto.
- **No toca `F_pga`.** Su valor y su etiqueta son correctos; solo su justificación se
  reescribe, y eso es S14.
- **No toca `PERFIL_SUELO_PRESUNTO`.** Conserva `"S5"` y `[S]` por la razón de §2.5.
- **No escribe tests.** Regla 6 de `CLAUDE.md`: los tests van en su fase. Lo que sí queda
  escrito es **qué tres tests hay que rehacer y por qué**, en la advertencia de §5.
- **No resuelve `NOR-PUE-11`** (el borde `PGA = 0.50` exacto), aunque esta sesión le haya
  encontrado un agravante nuevo: la contradicción de rótulos dentro del propio Manual.
  Queda escrito en §3 para quien lo tome.
- **No cita ASCE 7.** El verificador de AASHTO apunta —sin darlo por verificado— que la
  dispensa por `T ≤ 0.5 s` que «suena familiar» es de **ASCE 7 §20.3.1** y allí es
  específica de suelos licuables. Es la explicación más plausible del origen de la cita
  inventada, y por eso se anota; pero **ASCE 7 no está en `normas/`** y esta sesión no la
  ha abierto. No se usa como fundamento de nada.
