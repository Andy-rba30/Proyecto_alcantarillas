# Reglas del proyecto

## Fuente de verdad
- Fuente normativa única: docs/hoja_de_ruta_alcantarillas_v8.md (o la version
  vigente que exista en docs/: M11 la localiza con el patron
  `hoja_de_ruta_alcantarillas_v*.md` y exige que haya exactamente una). Toda cita de
  numeral se verifica contra ese archivo. Nunca se inventa un numeral.
- Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta.
- **La única excepción a lo anterior: la fuente primaria.** Si la hoja de ruta
  discrepa del documento normativo original —el PDF en `normas/`— y la
  discrepancia se **verifica contra ese PDF**, gana la fuente primaria. Tu
  conocimiento previo no es fuente primaria: una verificación es citar numeral,
  página impresa y texto literal del documento. Cuando ganes por esta vía tienes
  que hacer las tres cosas, no una: (1) declarar la discrepancia **en el punto de
  uso**, con la cita que la sostiene; (2) reportar el defecto **contra la hoja de
  ruta**, que es la que hay que corregir; (3) dejar dicho que la hoja de ruta
  sigue mal mientras no se corrija, porque quien la lea sin leer el código
  diseñará con el valor equivocado. Esta regla estaba **aplicada y no escrita**
  (`constantes_normativas.py`, K_fricción SI: «aquí gana la fuente primaria
  HDS-5 por verificación externa»), y sin escribirla el proyecto tenía dos
  jerarquías incompatibles y un precedente sin norma (NOR-COH-02).
- **Si la hoja de ruta NO dice nada sobre algo que necesitas: NO lo inventes.**
  Crea una entrada en criterios_adoptados.py con valor=None, etiqueta [A] y
  justificación de por qué hace falta, y detén el cálculo con excepción.
  Rellenar un vacío en silencio es el peor error posible en este proyecto.

## Taxonomía de etiquetas (cinco, no cuatro)
Todo valor de proyecto lleva una de estas cinco. Se leen de más determinado a
más elegido, y ese es el orden en que M11 las imprime:

- **[N]** Exigencia normativa peruana vigente, numeral verificado. El mismo
  número en cualquier obra del país. Vive en constantes_normativas.py.
- **[N→]** Valor normativo aplicado POR ANALOGÍA. Requiere declaración expresa.
- **[S]** **Dato de sitio.** Obtenido mediante un procedimiento normativo real
  (mapa, ensayo, medición de campo) aplicado a las coordenadas o condiciones de
  ESTE proyecto. No es elección del proyectista ni analogía: es un hecho
  determinado, no portable a otro proyecto. **En vez de sensibilidad declara
  trazabilidad obligatoria**: el procedimiento exacto, la fuente, y si el dato
  aplica a todo el corredor o varía punto a punto.
- **[C]** Vacío normativo cubierto con fuente técnica reconocida (FHWA, AASHTO).
- **[A]** Sin norma ni fuente única. Adopción declarada + sensibilidad.

Regla para separar [N] de [S]: si el valor cambia al mover la obra de sitio
pero NO al cambiar de proyectista, es [S]. "La Unión está en Zona 4" cita
E.030 correctamente y aun así no es [N]. Regla para separar [S] de [A]: un [A]
se defiende con un rango de sensibilidad porque hubo elección; un [S] no tiene
rango que elegir y se defiende con la trazabilidad de la lectura.

Dónde vive cada [S]: si vale para todo el corredor, en datos_sitio.py; si
varía punto a punto, es columna del CSV (NF_profundidad_m, cbr_subrasante). Un
[S] pendiente de ensayo que además comparte tablero con los criterios puede
quedar en criterios_adoptados.py con el campo `trazabilidad`.

Tabla y elección se separan siempre: los valores de una tabla normativa son
[N] y viven en constantes_normativas.py (F_PGA_TABLA,
REDUCCION_KH_POR_DESPLAZAMIENTO); cuál fila aplica a esta obra es [A] y vive
en criterios_adoptados.py ('F_pga', 'factor_muro_eleccion'). El segundo
ejemplo decía FACTOR_MURO_TABLA hasta S16, y ese símbolo ya no existe: lo
retiró NOR-PUE-07 porque el numeral no presenta tabla alguna, y en su lugar
quedó el único valor normativo, REDUCCION_KH_POR_DESPLAZAMIENTO = 0.5. Se
corrige aquí porque un símbolo colgado en la constitución no es inocuo: un
test de la suite estaba VERDE SOBRE EL COMENTARIO que explica la retirada
—`"FACTOR_MURO_TABLA = {" in fuente` lo satisfacía— y así estuvo hasta que
S16 lo pasó al AST. El ejemplo sigue valiendo con el par que sí existe:
el 0.5 es [N] y cuál de las dos declaraciones aplica a esta obra es [A].

## Arquitectura
- Ningún módulo declara valores no normativos. Todo literal numérico fuera de
  constantes_normativas.py (solo [N]), criterios_adoptados.py ([N→],[C],[A] y
  los [S] pendientes de ensayo) o datos_sitio.py (solo [S] de corredor) es un
  defecto y se rechaza en revisión. Excepciones permitidas: 0, 1, 2,
  índices, y constantes matemáticas puras (pi). Tres archivos más quedan
  exentos por no contener valores de proyecto: tolerancias.py (precisión
  numérica: cambiarla no mueve ninguna magnitud física), dominios.py (rango
  físico posible de un dato de entrada: no entra en ninguna fórmula) y
  constantes_fisicas.py (constantes físicas universales -- hoy cinco nombres:
  G = 9.81 m/s², RHO_AGUA, N_POR_KN, GAMMA_AGUA y GAMMA_AGUA_KN_M3 (esta
  última derivada de las tres anteriores, no un literal independiente) --
  el mismo valor en cualquier obra del planeta; no responde a "qué exige la
  norma peruana" y por eso no es [N]). Regla
  para saber si un número va en uno de esos tres: si cambiarlo puede alterar un
  resultado del cálculo, no va ahí. datos_sitio.py está exento por la razón
  CONTRARIA: sus números sí son valores de proyecto, y de los más pesados —
  está aparte porque no son constantes universales, no porque no importen.
  G_LAUSHEY = 9.8 SÍ vive en constantes_normativas.py, a pesar de ser
  numéricamente el mismo concepto físico: es el valor que la Sec. 4.1.1.3.7 c)
  de la hoja de ruta escribe explícitamente para su fórmula de d50, y separarlo
  de la gravedad genérica evita que una obra tenga dos valores distintos de "g"
  (9.8 en Laushey, 9.81 en todo lo demás) conviviendo sin que nadie lo declare.
- Un literal que es parte de una fórmula transcrita de la hoja de ruta —el 8 de
  A = (D²/8)(θ − sen θ), el exponente 2/3 de Manning— se deja en el módulo
  marcado con `# literal-ok: <razón>`. La marca lo declara y lo hace visible en
  revisión; sin marca, tests/test_sin_literales.py lo rechaza.
- Los tipos que fluyen entre módulos están en modelos.py. Ningún módulo define
  sus propios dicts ad-hoc para lo que ya existe ahí.
- criterios_adoptados.valor(clave) y datos_sitio.valor(clave) con valor None
  lanzan CriterioPendienteError. Nunca se sustituye por un default silencioso.
- Cada invocación de un criterio o de un dato de sitio se registra, para que
  M11 imprima solo los usados.
- Cada verificación devuelve un objeto Verificacion(cumple, numeral, valor,
  criterio_aplicado), nunca un bool desnudo.
- **La memoria la EMITE el cálculo; M11 la formatea.** Cada función de cálculo
  devuelve, junto a su resultado, el `PasoDeMemoria` que lo explica: qué,
  **por qué**, fórmula con su cita, sustitución con la **procedencia** de cada
  valor, resultado, umbral con su **carácter en la fuente**, veredicto con
  margen, y las citas textuales. M11 elige etiquetas y CSS y no hace
  aritmética sobre magnitudes — un test barre su AST. La regla nace de
  SIS-A-07: el reporte declaraba «no calcula nada nuevo» mientras calculaba
  `y/D` en dos sitios, que es un segundo motor de cálculo sin tests.
- **El `por_qué` no se escribe en el módulo que calcula.** Sale de un
  `Fundamento` de `src/normativa/fundamentos.py`, que lleva `verbo` y citas, y
  el registro comprueba que el verbo esté sostenido por el `caracter` de
  alguna de sus citas. Es lo que impide escribir «la norma obliga a…» encima
  del párrafo que dice «recomendándose que la velocidad mínima sea igual a
  0.25 m/s» (NOR-MEM-01, MAT-O13). Un paso sin `por_qué` no se construye, y un
  umbral sin `cita_id` tampoco.
- **Ningún texto literal se transcribe dos veces.** Toda frase que la memoria
  entrecomille como cita sale de `Registro.textos_literales()` — el `Verbatim`
  de una cita, o el título, el texto previo o una nota al pie de una tabla —,
  verificada contra su página. Las segundas transcripciones a mano no son un
  duplicado inocuo: divergen sin que nada avise, y dos de las seis que había
  ya divergían (el título de la Tabla N° 10, y la tercera condición de `h_o`,
  con una **elisión sin marcar** bajo el rótulo «texto literal»).
- **Tres cosas se imprimen separadas, y no es estilo:** lo que la fuente
  **dice** (cita, `class="fuente"`), lo que el proyecto **lee** en ella
  (`Interpretacion`, `class="interpretacion"`) y lo que el proyecto **hace**.
  Pegadas, las tres se leen como norma: es NOR-HID-04.

## Nivel de entrega: perfil o expediente

La taxonomía de cinco etiquetas dice **cuánto se eligió** un valor. No dice a
**qué entrega pertenece**, y son dos preguntas distintas: un [A] que gobierna
el diámetro de una alcantarilla y un [A] que gobierna la cuantía del cabezal
son igual de elegidos y no se cierran en la misma etapa del proyecto. Todo
criterio lleva por eso un segundo campo, `Criterio.nivel`, con dos valores:
`NIVEL_PERFIL` y `NIVEL_EXPEDIENTE`.

- **El nivel de un criterio es el nivel de la etapa que lo consume**, y no es
  una opinión: si una corrida `--alcance perfil` lo invoca sin que su etapa
  quede diferida, es de perfil. `tests/test_cierre_perfil.py` lo comprueba
  corriendo el pipeline y contrastando lo que invoca contra el campo, de modo
  que la clasificación no puede quedar desincronizada del código — que es
  exactamente como se desincronizan las clasificaciones escritas a mano.
- **Todo criterio SIN VALOR tiene que declarar nivel.** Un vacío que no dice a
  qué entrega pertenece no se puede planificar: no se sabe si frena el perfil o
  si el alcance lo difiere.
- **Todo criterio de PERFIL con etiqueta [A] lleva `sensibilidad` y
  `resolucion`**, tenga valor o no. La ventana es parte de la FICHA y no del
  valor: dice dentro de qué se va a poder elegir, y eso se sabe antes de
  elegir. Sin ese matiz, un [A] de perfil sin declarar se quedaba sin ventana y
  entonces la GUI y la CLI no lo podían declarar en caliente — el valor
  aparecía y la ventana seguía sin estar.

Las tres reglas están en `criterios_adoptados._verificar_nivel`, no en un
documento. La tercera es el criterio de salida del nivel de perfil escrito como
invariante: **ningún [A] de perfil sin valor, sin sensibilidad y sin
procedencia**.

Qué NO es el nivel, porque las tres cosas se confunden: no es la **fase** del
cálculo (eso es `variables_entrada`), no es la **etiqueta** (eso es la
taxonomía de arriba) y no es el **alcance de una corrida** (eso es la bandera
`--alcance`, que decide qué etapas se ejecutan). El nivel es una propiedad del
criterio; el alcance, de la corrida. Coinciden porque el alcance de perfil
difiere justamente las etapas cuyos criterios son de expediente, y esa
coincidencia es lo que el test comprueba en vez de darla por hecha.

## Unidades
- **Todo el código opera en SI: metros, m³/s, m/s, Pa, kN.** Ninguna función
  acepta ni devuelve pulgadas, pies ni kg/cm².
- Las constantes empíricas dependientes de unidades llevan sufijo _SI en su
  nombre y un comentario con el valor imperial equivalente y por qué NO se usa.
- La conversión a unidades de presentación (pulgadas, kg/cm²) ocurre solo en
  la capa de reporte, nunca en el cálculo.

## Excepciones (taxonomía)
Todas descienden de ErrorProyecto, definidas en modelos.py, para que la GUI
distinga un problema del expediente de un fallo del programa con un solo except.
- CriterioPendienteError: criterio [A] sin valor. La GUI la muestra como un
  pendiente declarable, no como error del programa. **Y no la muestra con esa
  sola línea**, que es lo que esta cláusula decía: llega por la vía del
  `Bloqueo` — `cli._etapa` → `cli._bloqueo` → `M11.criterios_bloqueantes` →
  `gui/app.py::_llenar_resumen` — y pinta seis columnas: clave, etiqueta,
  concepto, fuente, fases y puntos. `CriterioPendienteError.mensaje_gui`
  conserva la redacción mínima («falta declarar: <clave>») y **no tiene
  consumidor de producción a propósito**: cablearla cambiaría ese tablero por
  un solo dato. Se corrige aquí en S19 porque quien leyera la constitución sin
  leer el código diseñaría la ventana con la línea equivocada (SIS-B-07); la
  decisión entera está en `docs/decisiones_diferidas.md`.
- DisenoNoFactibleError: ninguna combinación material/diámetro cumple.
  Debe llevar el motivo y, si aplica, el delta de rasante requerido.
- DatoFaltanteError: falta un dato de entrada. Falta la **columna** entera
  del CSV, o la celda obligatoria viene vacía. Lleva el nombre de la columna.
  **También cubre el dato que no es columna del CSV**: el que llega por
  `--datos-externos`, y el que un tablero externo tendría que aportar y
  todavía no aporta (`ancho_derecho_via_m` en V5 es el caso vivo). En esos
  casos el campo `campo` nombra el DATO, no una columna, y el mensaje dice de
  dónde tendría que venir. **En S20 se le sumaron tres casos vivos más, y los
  tres son la misma forma:** el caudal del evento extremo que V8 pide una vez
  declarado su TR (`Q_evento_extremo_m3s`; este software no hace hidrología),
  y las dos entradas que `espesor_pared_conducto` puede no traer — el material
  cuya norma de producto no está en `normas/`, y la fila de diámetro que nadie
  transcribió—. Los tres eran `AssertionError` desnudos: **una excepción que no
  desciende de `ErrorProyecto` tumba la corrida entera** porque `cli._etapa` no
  la captura, y la GUI no la puede distinguir de un fallo del programa. La
  regla que los separa sigue siendo la misma: si el revisor tiene que AÑADIR
  algo es Faltante. Se amplió aquí en S16 (SIS-E-06): `modelos.py`
  llevaba tiempo declarando el contrato ancho — "del CSV (Sec. 1.2) o de un
  tablero externo" — y el código lo usaba así, de modo que la constitución
  describía una excepción más estrecha que la que el proyecto tiene. La
  alternativa —estrechar el código— habría obligado a inventar una excepción
  nueva para el mismo problema del revisor: falta un dato que hay que
  conseguir.
- DatoInvalidoError: el dato **está** pero no puede ser: no es del tipo
  esperado, cae fuera del rango físico de dominios.py, o contradice a otro
  dato de su misma fila (§1.5). Hermana de DatoFaltanteError y no la misma:
  "falta la columna cbr_subrasante" y "el CBR dice 250 %" son dos problemas
  distintos del expediente y se corrigen de forma distinta. La regla para
  elegir: si el revisor tiene que **añadir** algo es Faltante, si tiene que
  **corregir** algo es Invalido.
- **LimiteNumericoError: cada dato cumple su rango y es la ARITMÉTICA la que
  no cabe.** Quinta de la taxonomía, añadida en S16.5. La regla que la separa
  de DatoInvalidoError: si el dato, por sí solo, viola un límite de
  dominios.py es Invalido; si **todos** los datos pasan **todas** las
  validaciones y aun así la operación que los combina desborda a ±inf o anula
  el denominador de una división, es LimiteNumerico. Ejemplos medidos:
  `cota_rasante = 1e308` (finita, y ninguna cota tiene techo — ponérselo sería
  inventar un valor de proyecto) hace que `M7.proyeccion_taludes` devuelva
  `inf` y el informe imprima un diagnóstico entero sobre un número que no lo
  es (SIS-G-01); un `Q_m3s` diminuto lleva a brentq a un θ donde el área se
  cancela y `M4.tirante_critico` dividía por cero (SIS-G-02).
  **No se corrige poniendo techos en dominios.py**: ese archivo acota lo que
  un dato *puede ser*, no lo que la aritmética *puede llevar*. La guardia va
  siempre a la **salida** del cálculo.
  Precedente que conviene conocer antes de leer esto como una incoherencia:
  **MAT-D13** (`M1_clasificacion.tr_desde_riesgo`) cerró un caso idéntico bajo
  DatoInvalidoError **antes de que esta clase existiera**, y no se migró
  porque es código verde. La clase nueva no llegó porque DatoInvalidoError
  fuera la equivocada por definición: llegó a **nombrar algo que el proyecto
  ya venía haciendo sin nombre**.
  De MAT-D13 se hereda además la **forma** de la guardia: umbral **medido**
  (nunca un `!= 0` genérico), condición escrita **en positivo y negada**
  (`not A > 0`, porque un NaN es falso frente a `<=` igual que frente a `>`),
  y mensaje que nombra al **par culpable**, no a un solo dato.
  Contrapeso obligatorio: hay **dos** `inf` deliberados en el repositorio
  (`M9.verificar_volteo` y `M9.verificar_deslizamiento`, donde un FS infinito
  es la ausencia de la solicitación). Ninguna guardia de finitud puede
  atraparlos; por eso no hay barrido global y el censo está fijado en un test.
No usar Exception genérica en lógica de negocio. Un fallo de E/S (archivo
inexistente) no es del expediente y sale como FileNotFoundError, fuera de
ErrorProyecto.

## Estilo
- Python 3.11+. Dependencias: numpy, scipy (brentq), pytest, ttkbootstrap,
  weasyprint. Cualquier dependencia adicional se consulta antes.
- No comparar floats con ==. Tolerancias explícitas y nombradas.
- Identificadores en español (coherente con Tc.py), docstrings en español.
- Cada función de cálculo lleva en su docstring el numeral que la sustenta.

## GUI
- Reutilizar el patrón de legacy/Tc.py:
  Tkinter + ttkbootstrap, Notebook por pestañas, MarcoScroll, Tooltip, campo
  validable, plantilla con marcadores %%, sesión en JSON, export HTML/PDF/CSV.
  No reinventar los componentes.
- **Dónde están hoy esos componentes, que ya no es `legacy/Tc.py`.** La regla
  decía «leer esos archivos antes de escribir GUI», y mandaba a un programa
  que ya no se puede ni importar en este repositorio: `matplotlib` es import de
  nivel superior y no está en `requirements.txt`, y la `plantilla_memoria.html`
  que su encabezado anuncia no existe (SIS-B-10). La extracción ya se hizo:
  `Tooltip` y `MarcoScroll` son el MISMO código movido a `gui/componentes.py`;
  `CampoValidable` es su `_campo_validable` con la validación al escribir que
  exige la Sec. 4.3; y el patrón de plantilla `%%` vive en
  `M11_reporte.PlantillaHTML`. Se escribe GUI leyendo `gui/componentes.py`.
  `legacy/Tc.py` **se conserva** —no es código muerto: la §1.2 de la hoja de
  ruta lo nombra como origen del caudal de diseño Q, que entra al calculador
  como columna del CSV— pero se lee como ANTECEDENTE, no como plantilla viva.
  Su estatus completo está en su propio encabezado y en
  `docs/decisiones_diferidas.md`.

## Tests
- pytest en tests/. Mínimo un test por módulo.
- Todo módulo de cálculo se contrasta contra tests/fixtures/casos_patron.py.
- Al cerrar cada módulo: commit con el nombre del módulo en el mensaje.

## Cierre de tarea: la entrega es `origin/main`

**Una tarea no está terminada hasta que su trabajo está en `origin/main`.**
El último paso de cualquier tarea, siempre, son estos dos:

1. **Fusionar a `main` y empujar.** Una rama de trabajo empujada al remoto no
   es una entrega: es un borrador que nadie lee. Un commit que no está en
   `main` no cuenta como entregado.
2. **Confirmar el conteo de tests leyéndolo de `origin/main`**, no del clon
   local ni de la rama de trabajo. Traer el remoto primero (`git fetch origin
   main`) y correr la suite sobre ese árbol. El número que se reporta es ese.

Por qué está escrito aquí: esto falló dos veces. La primera se arregló a mano
en el "PASO 0" y no se dejó regla, así que volvió a pasar — siete commits y 36
tests quedaron en una rama sin fusionar mientras se reportaba `main` como si
los tuviera, y una auditoría posterior los dio por perdidos.

Al reportar el conteo, distinguir **`passed` de `collected`** y saber que **el
conteo es un PAR, no un número**. Es la misma lección que el paso 2 de
`verificar_sesion.py` dejó escrita en S12 para PyMuPDF, aplicada ahora a un
segundo eje. Lo invariante es `collected = passed + skipped`, hoy **1538**; lo
que se mueve es el reparto, porque **dos** tests se saltan según el entorno y
**ninguno de los dos saltos es una regresión**:

- `tests/test_MD.py:362` — el `skipped` **permanente**, y el único que lo es:
  su `skipif` guarda una condición (que `M5_verificaciones` no exista) que ya
  no puede darse.
- `tests/test_gui_contrato.py:1027` — el test de **ventana real** que añadió
  S20. Se salta cuando ningún intérprete disponible puede levantar un `Tk`:
  falta `tkinter`, falta `ttkbootstrap` o falta entorno gráfico.
- Y aparte, en bloque, los **32** de `tests/test_normativa_pdf.py`, que se
  saltan sin PyMuPDF —dependencia de TEST, no de producción—. Ése es el eje
  que S12 documentó.

**No basta con que el intérprete de la suite tenga tkinter**, y conviene
decirlo porque invita al error contrario: el test de ventana sondea primero
`sys.executable` y después los intérpretes del sistema, de modo que un
`1537 passed` **no** demuestra que la suite corra sobre un Python con tkinter
—solo que alguno lo tenía—. Es exactamente lo que pasa hoy en el contenedor de
desarrollo, donde el intérprete de la suite no tiene tkinter y el test corre
igual, en un subproceso, sobre `python3.12`.

Son **cuatro** configuraciones y no dos, porque PyMuPDF y tkinter son
independientes. Las cuatro medidas sobre el mismo árbol, no supuestas:

| PyMuPDF | Ventana Tk | `passed` | `skipped` |
|---|---|---|---|
| sí | sí | 1537 | 1 |
| sí | no | 1536 | 2 |
| no | sí | 1505 | 33 |
| no | no | 1504 | 34 |

Decir cuál de los dos números se está citando **y con qué entorno**; la mayor
parte de la confusión histórica de números sale de mezclarlos. La regla que no
depende del entorno es la suma: si `passed + skipped` deja de dar `collected`,
hay un fallo o un error de recolección —no una dependencia ausente—, y eso sí
es una regresión.

Si la fusión no se puede hacer (permisos, política de egress, conflicto), eso
**no** convierte la tarea en terminada: se reporta explícitamente qué quedó sin
fusionar, en qué rama y con qué SHA, para que nadie lo lea como entregado.

## Reglas de corrección de hallazgos de auditoría

Este repositorio tiene 234 hallazgos de tres auditorías externas
(`docs/auditorias/auditoria_matematica.md`, `auditoria_sistema.md`,
`auditoria_normativa.md`), ya cruzados en
`docs/auditorias/matriz_cruzada_auditorias.xlsx` (14 clusters por causa raíz, 8
conflictos resueltos). Ese archivo es el TRACKER: el estado de cada hallazgo se
marca ahí, en las columnas Estado / Responsable / Commit. El PLAN es
`docs/hoja_de_ruta_correcciones_v12.md`.

**Dónde vive una decisión DIFERIDA**, que no es lo mismo que su estado:
`docs/decisiones_diferidas.md`. Un objeto que se conserva sin consumidor, un
barrido con un directorio exento, un procedimiento que no se implementa
todavía — cada uno con **qué se difirió, por qué, qué haría falta para
cerrarlo y dónde vive el símbolo**. El tracker dice en qué estado está un
hallazgo; ese registro dice qué se decidió y con qué argumento. No se
transcribe la razón: se cita el símbolo donde ya está escrita, y
`tests/test_decisiones_diferidas.py` comprueba que el símbolo siga existiendo.
Nació de los 22 hallazgos que la auditoría de sistema clasificó «deliberado
sin documentar», que eran decisiones correctas y mudas.

1. Antes de tocar un archivo, busca su cluster en la hoja `Clusters` y abre la
   ficha de cada ID citado (MAT-, SIS-, NOR-) para leer su evidencia completa.
   Un cluster se corrige entero, en un solo cambio de diseño y un solo commit.
   Nunca hallazgo por hallazgo. Solo 224 de los 234 caen en alguno de los 14
   clusters: los otros 10 llevan `—` en la columna Cluster (los nueve
   `NOR-OK-*` y `NOR-AAS-07`, retirado) porque la auditoría los revisó y los
   cerró como correctos, sin corrección que hacer. No son trabajo pendiente.
2. Antes de aplicar cualquier corrección, consulta la hoja `Conflictos` (o la §6
   del plan). Ocho objetos del repositorio tienen una corrección "obvia" que es
   la EQUIVOCADA porque otra auditoría descubrió por qué. Si el objeto que vas a
   tocar está ahí, la resolución de esa fila es vinculante y sustituye a tu
   criterio.
3. Después de implementar, contrasta tu solución contra la evidencia de cada
   ficha y decime explícitamente si la cierra, la cierra en parte, o no la
   cierra. Si tu solución contradice lo que dice la ficha, parate y explicá por
   qué antes de seguir.
4. Ancla todo por NOMBRE DE SÍMBOLO (función, constante, clave de criterio),
   nunca por número de línea. Al menos 66 de 296 referencias archivo:línea del
   manifiesto no llevan a lo que dicen llevar, y las auditorías corren sobre dos
   commits distintos (71b134fb y 2e1708ab).
5. Cita los IDs siempre con prefijo MAT- / SIS- / NOR-. `F-01` y `F-02`
   significan hallazgos DISTINTOS en la auditoría Normativa y en la de Sistema.
6. No escribas tests contra el comportamiento actual antes de cerrar las fases
   de corrección: congelarías los defectos. Los tests van en su fase, después.
7. Cuando el código y la hoja de ruta discrepan, el defecto se reporta contra la
   hoja de ruta primero y la fuente primaria (el PDF en normas/) decide.
8. No inventes valores normativos ni citas: numeral, artículo y página salen del
   PDF, no de memoria. Si un dato lo tiene que decidir el proyectista, no lo
   elijas vos: dejalo como vacío declarado, por la vía que el proyecto ya usa
   para V5 y V8.
9. Actualiza la columna Estado/Responsable/Commit de la hoja `Hallazgos` del
   `.xlsx` para cada ID que cierres en la sesión. `openpyxl` está PREAUTORIZADO
   para esto (`pip install openpyxl --break-system-packages`): es herramienta de
   mantenimiento del tracker, no dependencia del software calculado — no va en
   requirements.txt ni necesita consulta previa.

### Git (fase de corrección)
- El trabajo puede pasar por ramas auxiliares, pero ninguna queda abierta: al
  cerrar cada sesión, todo tiene que estar fusionado en `main`.
- Un commit por sesión (ver `docs/hoja_de_ruta_correcciones_v12.md`), con
  mensaje `fase1(Sn): resumen — IDs cerrados`, donde `Sn` es el número de
  sesión (S1, S2...).
- No hagas commit si la suite no está en verde.
