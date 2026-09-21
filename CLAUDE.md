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

**Y desde EXT-10 hay una tercera casa, la de OTRA OBRA sobre el mismo
despliegue: un [S] declarado por sesión.** Hasta EXT-10 el repositorio ERA
un expediente: los [S] de corredor de La Unión están en datos_sitio.py y no es
hardcoding sino diseño (EXT-V-01, decidido en EXT-0). Lo que faltaba era un
requisito de producto —calcular un segundo corredor sin editar código—, y se
resuelve así: un [S] declarado por sesión vive en el bloque `sitio` de la
sesión JSON (`FORMATO_SESION = 3`, `src/sesion.py`) y entra al proceso por
`--datos-sitio sitio.json` en la CLI —hermano de `--datos-externos`— o por el
campo «JSON de datos de sitio» de la pestaña 1 de la GUI, SIEMPRE por
`datos_sitio.establecer_dato_dinamico(clave, valor, trazabilidad, fecha,
origen=…)`, que construye el dato por `dataclasses.replace` y lo somete a la
MISMA guardia que el archivo (`_verificar_dato`, que desde EXT-10 exige
también la FORMA y el signo: `DatoSitio.forma`, `opciones`, `positivo`,
`no_negativo`, porque un sitio.json es entrada de usuario y `"0.30"` o `True`
llegaban a M9), exige trazabilidad no vacía y fecha, y rechaza
un dato `Derivada` (`Z_E030` se deriva de la zona, no se declara). Cuatro
cosas que la casa nueva NO cambia: (1) el programa nunca escribe
datos_sitio.py —la sesión aporta el VALOR y su lectura; la ficha (concepto,
procedimiento, fuente, ámbito) sigue en el archivo—; (2) los valores del
archivo siguen siendo los de la obra del repositorio, y un proyecto nuevo se
crea cargando una sesión vacía, no vaciando el archivo; (3) la memoria y el
JSON imprimen DE QUÉ ARCHIVO salió cada [S] (datos_sitio.py o el sitio.json /
la sesión), leído del `ContextoCorrida` de la corrida y no del estado vivo, y
la memoria advierte cuando el `corredor_del_proyecto` efectivo gobierna
desde datos_sitio.py —los [S] son los de la obra del repositorio, con o sin
nombre de `--proyecto`; comparar dos rótulos por texto se probó y se refutó,
ficha EXT-10-03—; (4) la ventana normativa sigue sin declarar
[S] (regla R4: el camino es la sesión, no un campo de formulario). Y todo
`DatoSitio` lleva `nivel`, como los criterios: medido por corridas, la de
perfil no lee ningún [S] y la de expediente sólo `PGA_roca_B`
(`tests/test_ext10_multiobra.py`).

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
  Desde EXT-10 un [S] de otra obra puede pisar el del archivo SOLO por
  sesión (`establecer_dato_dinamico`, con trazabilidad y fecha, registrado
  como «declarado (sesión)» en la memoria con el valor del archivo al lado):
  datos_sitio.py sigue siendo el único archivo de [S] de corredor del
  repositorio, y ningún módulo de cálculo lee un [S] por otra vía que
  `datos_sitio.valor`.
  G_LAUSHEY = 9.8 SÍ vive en constantes_normativas.py, a pesar de ser
  numéricamente el mismo concepto físico: es el valor que la Sec. 4.1.1.3.7 c)
  de la hoja de ruta escribe explícitamente para su fórmula de d50, y separarlo
  de la gravedad genérica evita que una obra tenga dos valores distintos de "g"
  (9.8 en Laushey, 9.81 en todo lo demás) conviviendo sin que nadie lo declare.
- Un literal que es parte de una fórmula transcrita de la hoja de ruta —el 8 de
  A = (D²/8)(θ − sen θ), el exponente 2/3 de Manning— se deja en el módulo
  marcado con `# literal-ok: <razón>`. La marca lo declara y lo hace visible en
  revisión; sin marca, tests/test_sin_literales.py lo rechaza.
- **Quién consume una variable se AVERIGUA del código, y desde S21 se averigua
  siguiendo también las reexportaciones.** `variables_entrada._consumo_por_modulo`
  parsea el AST de cada módulo de cálculo. Hasta S21 sólo miraba las cadenas
  literales, y esa atribución se equivoca cuando el módulo que **escribe** la
  clave no es el que la **ejecuta**: `factores_carga_aashto` y
  `peso_especifico_relleno_kn_m3` figuraban como de «Fase 8 · Fase 9» y a las
  dos las invoca **V7, que es Fase 5** y corre en el alcance de perfil —M5
  importa de M8 la constante `CRITERIO_FACTORES_CARGA` y la función
  `peso_relleno_kn_m`—. Hoy se cierran las dos vías (constante reexportada y
  función reexportada, ésta con un punto fijo sobre el grafo de llamadas).
  Sigue siendo una **estimación** con falsos negativos posibles, y por eso no
  gobierna ningún filtro: dice a qué fase pertenece una variable y clasifica
  lo que ninguna corrida llega a invocar.
- **`src/` es un paquete real con UN solo nombre, y el servicio de cálculo
  vive en él (EXT-9, PC-08).** Hasta EXT-9 `src/` no era paquete: cinco
  archivos de producción (`cli.py`, `gui/app.py`, `gui/ayuda_entrada.py`,
  `gui/ventana_normativa.py`, `src/indice_formulas.py`) y `conftest.py` lo
  insertaban en `sys.path` e importaban por nombre plano, y con `src/` en el
  path `import src.criterios_adoptados` e `import criterios_adoptados` eran
  DOS módulos con dos `_OVERRIDES`, dos `_USADOS` y dos `CriterioPendienteError`
  que no se atrapan entre sí (demostrado en vivo por el dictamen: `catalogo(
  CONCRETO, RECTANGULAR)` por una vía exige los criterios del cajón y por la
  otra devuelve en silencio la norma del tubo). Desde EXT-9 hay un solo
  estilo en TODO el repositorio —`from src import criterios_adoptados as ca`,
  `from src.modulos import M4_control`, `from src.modulos.M3_hidraulica import
  geometria`—, ningún archivo toca `sys.path` (la raíz la pone quien ejecuta:
  `python cli.py`, `python -m gui.app`, `python -m src.indice_formulas`,
  `python -m src.normativa.manifiesto`, `python -m tests.apoyo.<script>`, o
  pytest por el `conftest.py` de la raíz), y `src/normativa/` conserva sus
  imports relativos, que no salen del subpaquete. Las rutas `src/modulos/X.py`
  de la documentación siguen siendo rutas de archivo. Y la orquestación
  —el alcance y lo que difiere, la carga de datos externos, las estructuras
  del informe, las fases, `correr`, `correr_punto` y `capturar_contexto`—
  está en `src/servicio.py`: `cli.py` es un ADAPTADOR (argparse, JSON,
  texto) que importa del servicio y REEXPORTA, como el mismo objeto, lo que
  `gui/app.py` y la suite leen de `cli` (ficha EXT-9-01). Importar y
  ejecutar el servicio no inicia la CLI ni la GUI; `anticipo`,
  `ayuda_entrada` e `indice_formulas` importan del servicio y ya no de la
  capa de arriba. `tests/test_ext9_paquete_servicio.py` fija las cuatro
  cosas: identidad (ningún archivo de `src/` bajo dos claves de
  `sys.modules`, medido en subproceso), estilo único y cero `sys.path` (por
  AST), servicio sin adaptadores (por AST y en proceso limpio) y equivalencia
  por las dos puertas (mismo JSON, mismos usos y misma huella del CSV, con y
  sin banderas y `--declarar`; la puerta `--sesion` la fija EXT-8 por el
  subproceso del PDF).
- Los tipos que fluyen entre módulos están en modelos.py. Ningún módulo define
  sus propios dicts ad-hoc para lo que ya existe ahí.
- criterios_adoptados.valor(clave) y datos_sitio.valor(clave) con valor None
  lanzan CriterioPendienteError. Nunca se sustituye por un default silencioso.
- Cada invocación de un criterio o de un dato de sitio se registra, para que
  M11 imprima solo los usados.
- Cada verificación devuelve un objeto Verificacion(cumple, numeral, valor,
  criterio_aplicado), nunca un bool desnudo.
- **Todo criterio declara la FORMA de su valor, y la puerta la exige (EXT-5).**
  `Criterio.forma` es una de las ocho de `criterios_adoptados.FORMAS` (`int`,
  `float`, `str`, `par_ordenado`, `serie_de_pares`, `dict_con_campos`,
  `categoria`, `serie_de_claves`) o la unión de varias como tupla (`k_v`), y
  `_verificar_criterio` la comprueba en los tres caminos —archivo, declaración
  en caliente, escritura permanente—, también cuando la sensibilidad no es
  numérica. Es lo que M2/M4 iban a exigir de todos modos, dicho en la ficha
  para que se rechace en la puerta con `ValueError` (SIS-E-05) y no en el
  consumidor con un `TypeError` fuera de `ErrorProyecto`: medido antes de
  EXT-5, 53 de las 70 claves (71 desde EXT-6, 73 desde EXT-7) aceptaban la cadena `'cero'` y la GUI no podía
  declarar el entero de `n_celdas_cajon` (PC-13, PC-14). Una `categoria`
  valida contra la tupla de textos de `sensibilidad`, que es donde vive el
  conjunto cerrado de un criterio; las guardias de los consumidores se
  quedan como segunda línea (ficha EXT-5-02). Y lo que el proyectista teclea
  lo lee UN solo parser para las dos ventanas,
  `gui/componentes.py::interpretar_texto_declarado` —entero, real con coma o
  punto decimal, literal estructurado, o texto; rechaza el separador de
  miles—, distinto a propósito del de la CLI (`ast.literal_eval` del texto
  entero), divergencia fijada por test. Las seis claves de
  `servicio.CLAVES_EXTERNAS` (en `cli` hasta EXT-9) que no son columna del CSV son desde EXT-5 la cuarta
  población del censo, `Poblacion.DATO_EXTERNO`, y la ayuda del JSON se
  deriva de ahí (EXT-G-03).
- **El estado con que corrió el expediente viaja en el informe, no se lee
  del proceso al exportar (EXT-4).** Los tres archivos de valores llevan
  estado de proceso —el registro de usos, las declaraciones en caliente, el
  libro de procedencias— y hasta EXT-4 los cuatro exportadores lo leían AL
  EXPORTAR, en 39 sitios: correr dos veces en la GUI, declarar después de
  correr o editar el CSV antes de exportar movían la memoria de una corrida
  que ya había pasado (EXT-A-01, PC-07, PC-09). `servicio.correr` (`cli.correr` hasta EXT-9) vacía los usos al
  entrar (`reiniciar_usos`) y fotografía al salir `Informe.contexto`, un
  `ContextoCorrida` congelado de `modelos.py` con usos, valores efectivos
  copiados en profundidad, procedencias, declarados y pisados en caliente y
  las dos huellas (`csv_sha1` de los MISMOS bytes que M0 leyó,
  `criterios_sha1`). De los catálogos, la capa de reporte sólo hace lecturas
  ESTÁTICAS —lo que dice el archivo—, y un test barre el AST de M11 para que
  siga siendo así. Un `Informe` sin contexto no se exporta: no hay caída al
  estado vivo (ficha EXT-4-03). Y la sesión de la GUI SUSTITUYE al abrirse
  (`restaurar_sesion(sustituir=True)`, con el candidato validado en seco) e
  importa aparte, porque abrir la obra B no puede heredar las decisiones de
  la obra A (EXT-A-02, SIS-B-22).
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

**Y desde S21 el nivel lo llevan los 69 (70 desde T1, 71 desde EXT-6, 73 desde EXT-7), no sólo los que no tienen valor.** La
guardia sólo lo exigía a los criterios SIN VALOR, de modo que trece con valor
—once de Fase 9 y licuefacción, dos opcionales— se habían quedado sin
clasificar. Se rellenaron **midiendo**, no opinando, y esa distinción tiene
consecuencias que conviene leer antes de tocar el campo:

- **La medida son corridas, y son tres.** `tests/test_nivel_medido.py` corre
  el pipeline a `--alcance perfil`, a `--alcance expediente`, y una tercera
  vez con los criterios `opcional=True` declarados en caliente —sin ella son
  invisibles, porque `valor_si_declarado()` no registra el uso mientras el
  criterio siga vacío—.
- **Se comprueba en LAS DOS DIRECCIONES**, y la segunda es la que faltaba: un
  criterio marcado `expediente` que la corrida de perfil invoque sin diferir
  es un fallo. Con una sola dirección, marcar `expediente` no lo comprobaba
  nadie, y el campo volvía a ser una lista mantenida a mano —escrita criterio
  a criterio en vez de en un archivo aparte, que es peor porque no se ve como
  lista—.
- **Cada uno de los trece dice QUÉ CORRIDA lo midió**, en el comentario que
  acompaña al campo. Ocho se midieron; cinco no se pueden medir —su cadena se
  detiene antes en un pendiente, o no los consume ningún módulo— y lo dicen
  con esas palabras, apoyados en `variables_entrada.consumido_por`.
- **El límite se conoce por MUTACIÓN, no por lectura.** Cambiando el nivel de
  cinco de los trece murieron cuatro tests y sobrevivió uno:
  `demanda_sismica_licuefaccion`, que no tiene consumidor. De los **diez** sin
  consumidor (ocho hasta T1; T1 sumó `edicion_que_rige_el_expediente`, la
  decisión de marco normativo del expediente, que ningún módulo consume, y
  EXT-6 su mitad legal, `edicion_legal_que_rige_el_expediente`, partida de
  aquélla porque el Manual de Puentes está derogado por RD y las normas
  técnicas de EE.UU. no —EXT-N-01, PC-26—) el
  nivel es un argumento y no una medida, y están censados en
  `SIN_CONSUMIDOR_Y_SIN_MEDIDA` para que el grupo no crezca en silencio —el
  mismo recurso que fija el censo de los dos `inf` deliberados—.

**Para qué se completó, además de por completitud:** `nivel` gobierna el
filtro de alcance de la pestaña 2 (`criterios_adoptados.criterios_del_alcance`),
que a `--alcance perfil` pasa la tabla de 69 filas (70 desde T1, 71 desde EXT-6, 73 desde EXT-7) a 36 y los pendientes
visibles de 33 a 11. El filtro **no oculta**: el recuento sigue contando los 33
sobre el archivo entero y dice además cuántas filas esconde. Y **no se apoya en
la derivación estática** de `variables_entrada` —que es una ESTIMACIÓN y tuvo
dos falsos negativos medidos, ver abajo—, sino en el campo que las corridas
comprueban.

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
  `Bloqueo` — `servicio._etapa` → `servicio._bloqueo` → `M11.criterios_bloqueantes` →
  `gui/app.py::_llenar_resumen` (los dos primeros vivían en `cli` hasta
  EXT-9, que los reexporta) — y pinta seis columnas: clave, etiqueta,
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
  desciende de `ErrorProyecto` tumba la corrida entera** porque `servicio._etapa` no
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
- **MetodoNoEvaluableError: el dato está y es válido, el criterio está
  declarado, y lo que falta es un PROCEDIMIENTO que el software no
  implementa.** Sexta de la taxonomía, añadida en EXT-3 (EXT-M-01, EXT-M-02,
  PC-27). La regla que la separa de las otras cinco, en el orden en que se
  pregunta: si el revisor tiene que **añadir** es Faltante, si tiene que
  **corregir** es Invalido, si tiene que **declarar** es CriterioPendiente, si
  la aritmética no cabe es LimiteNumerico, y si no hay nada que añadir,
  corregir ni declarar —hace falta OTRO MÉTODO— es MetodoNoEvaluable. Los dos
  casos vivos están bajo control de salida con el barril parcialmente lleno:
  la carga HW cuando HW/D < 0.75 («should not be used», HDS-5 pág. 3.24) y
  V1/V2, cuyo tirante y velocidad exigen el perfil de la lámina de agua
  (Section 3.5). **No es un incumplimiento** —subir de diámetro sólo baja
  HW/D— ni un aviso: viaja por la vía `Bloqueo` con
  `TipoDeBloqueo.METODO_NO_EVALUABLE`, **diferible a nivel de perfil y no de
  expediente** (v8 §4.3), y `MD.disenar_punto` la acumula como a los criterios
  pendientes en vez de descartar el material o degradarla a
  `DisenoNoFactibleError`. Su `str()` empieza siempre por
  `MOTIVO_METODO_NO_EVALUABLE`. Y desde EXT-3 `Bloqueo` vive en `modelos.py`
  con `tipo: TipoDeBloqueo` (str Enum cuyos valores son los textos que la
  línea base ya imprimía): la vía `servicio._etapa` → `servicio._bloqueo` descrita
  arriba no cambia, `cli` lo reexporta.
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
- **Tres documentos de `docs/` se GENERAN y no se editan a mano**, cada uno
  con su test de sincronía que regenera a memoria y compara:
  `manifiesto_citas.md` (resincronizado por símbolo) y
  `manifiesto_registro_normativo.md` (índice del registro, anclado por id)
  salen de `python3 -m src.normativa.manifiesto --escribir --suite "..."`,
  y desde T3 también `trazabilidad.csv` —la vista filtrable del registro,
  una fila por `Cita`— sale del mismo comando, que por eso exige el par de
  la suite: es parte del sello de la primera línea. El cuarto generado,
  `indice_formulas.md`, tiene su propio comando (`python3 -m src.indice_formulas`;
  hasta EXT-9 se lanzaba como script, y como script ya no encuentra el paquete)
  porque necesita la corrida de referencia entera. El sello (fecha, commit
  de origen, alcance, par de la suite con su entorno) lo pone quien regenera
  y el test lo LEE del documento para comparar el cuerpo y no la fecha.

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
segundo eje. Lo invariante es `collected = passed + skipped`, hoy **2617**; lo
que se mueve es el reparto, y **ningún salto de los de abajo es una
regresión**. Son de **tres** clases y no de dos, y la tercera llegó en S21:

- `tests/test_MD.py` — el `skipped` **permanente** por condición imposible:
  su `skipif` guarda que `M5_verificaciones` no exista, y ya no puede darse.
- `tests/test_gui_contrato.py` y `tests/test_ext5_forma_gui.py` — los tests
  de **ventana real**, que hoy son **nueve** en siete corridas (S20 abrió el
  primero, la corrida de perfil; S22 el de la ayuda de entrada; G1 el de la
  selección real de la pestaña 2, que sobrevive al filtro; I1 el smoke que
  construye la app con las cuatro pestañas pobladas y abre y cierra
  `gui/ventana_normativa.py`, que hasta entonces no se construía nunca bajo
  Tk; EXT-4 el del contexto de corrida, que lee el texto real de «Etapas
  bloqueadas» y el estado real de los exportadores tras declarar, quitar,
  cargar sesión y fallar; EXT-5 los tres de `tests/apoyo/gui_ext5_real.py`
  sobre UNA corrida —el bloqueo real de C-01 tras declarar los siete del
  cajón por el ratón, la cara de solo lectura del `Derivada` en la pestaña 2
  y el veredicto de 'nan' al escribir y al declarar—; EXT-8 el de
  `tests/apoyo/gui_ext8_real.py`, que mide el rótulo visible del motivo, la
  rueda de X11, Escape, Control-Return y la exportación del PDF —por el
  SUBPROCESO, con el botón apagado, el estado terminal y la cancelación,
  cuando el intérprete de la ventana tiene weasyprint; por el navegador
  cuando no—). Se saltan
  cuando ningún intérprete disponible puede levantar un `Tk`: falta `tkinter`,
  falta `ttkbootstrap` o falta entorno gráfico.
- `tests/test_familias_del_csv.py` — **tres** saltos de DISEÑO, no de entorno,
  y por eso valen lo mismo en las cuatro configuraciones. El test está
  parametrizado por (dato declarado × familia) y mide sólo las familias que
  NO usan el dato; las tres combinaciones que sí lo usan se saltan diciéndolo.
  Es el primer salto del repositorio que no depende de qué haya instalado.
- Y aparte, en bloque, los **33** de `tests/test_normativa_pdf.py` (32 hasta
  T1, que sumó el de la resolución impresa del Manual de Puentes), que se
  saltan sin PyMuPDF —dependencia de TEST, no de producción—. Ése es el eje
  que S12 documentó.

**No basta con que el intérprete de la suite tenga tkinter**, y conviene
decirlo porque invita al error contrario: el test de ventana sondea primero
`sys.executable` y después los intérpretes del sistema, de modo que un
`1949 passed` **no** demuestra que la suite corra sobre un Python con tkinter
—solo que alguno lo tenía—. Es exactamente lo que pasa hoy en el contenedor de
desarrollo, donde el intérprete de la suite no tiene tkinter y el test corre
igual, en un subproceso, sobre `python3.12`.

Son **cuatro** configuraciones y no dos, porque PyMuPDF y tkinter son
independientes. **EXT-10 (2026-09-21) sumó OCHENTA Y CINCO tests**: los 78
de `tests/test_ext10_multiobra.py` —la aceptación de EXT-V-01 y de la fase
E04: 63 escritos primero en rojo con `xfail(strict=True)` por test —medidos
63 xfailed y 0 XPASS antes de tocar código; dos guardias no lo llevaron
porque valen antes y después, y se midió con un XPASS— y liberados al
corregir; los quince restantes los dejó el auditor adversarial (la forma y
el signo de un [S] declarado por sesión: `"0.30"`, `True`, `-0.3`, `[0.3]`,
una orientación fuera de las dos tabuladas, `"dos"` carriles; el origen por
entrada; el volcado que lee «SIN LEER» de la foto; la advertencia por
origen; la precedencia ruta/bloque)—, el DÉCIMO test de ventana real de
`test_gui_contrato` (`tests/apoyo/gui_ext10_real.py`: dos obras por el campo
de la pestaña 1, «Guardar sesion» en formato 3, «Nuevo proyecto», abrir B
tras A, borrar el campo, y un sitio.json malo que no corre) y los seis
anclajes parametrizados de `test_decisiones_diferidas` para las fichas de
la Parte XXVI (EXT-10-01..06). Ningún archivo restó tests: `test_M11_reporte`
admite un [S] entre los bloqueantes, `test_datos_sitio` enumera los campos
nuevos, `test_M9_cabezal` fuerza el valor por `object.__setattr__` para
seguir probando la guardia del consumidor, `test_ext4` lista dos lecturas
estáticas más y `test_sin_literales` censa la marca de `FORMATO_SESION`.
La línea base de la Familia C se regeneró por cambios de FORMATO medidos
con `diff`: `hoja_ruta_sha1` (la v8 enmendada), `criterios_sha1` (los
imports de `NIVEL_*`), el bloque `corredor_del_proyecto` y los campos
`origen`/`fecha`/`declarado_en_caliente` del JSON, la línea «Corredor» y la
fila «Origen» del HTML, y la advertencia de corredor de la obra del
repositorio en las memorias y los volcados; ningún número de cálculo se
movió. Las cuatro configuraciones se MIDIERON sobre `eb926e6` (el segundo
commit `ext(EXT-10)`, con los ajustes del auditor), en serie, sobre un
checkout limpio (`git worktree`) y sin otra suite en marcha: las dos sin
Tk sin `DISPLAY` y con un `xvfb-run` que falla, las dos sin PyMuPDF
desinstalándolo y reinstalándolo. De los 85, ninguno depende de PyMuPDF y
sólo el de ventana real depende de Tk: la columna «Ventana Tk = no» salta
ahora 14 y no 13, y la «PyMuPDF = no» sigue saltando 35 más que la de al
lado. **EXT-9 (2026-09-21) sumó DIECISIETE tests**: los 14 de
`tests/test_ext9_paquete_servicio.py` —la aceptación de PC-08 y de las fases
E01, E02, E03, E03a, E03b y E03c del plan de evolución: diez escritos primero
en rojo con `xfail(strict=True)` —medidos 4 passed, 10 xfailed y 0 XPASS
antes de tocar código— y liberados al convertir `src/` en paquete y mover la
orquestación a `src/servicio.py`; los cuatro que valen antes y después son la
guardia de identidad en subproceso (ningún archivo de `src/` bajo dos claves
de `sys.modules`), el rechazo por AST de `import src.X`, los imports
relativos confinados a `src/normativa/` y el mutante del detector— y los
tres anclajes parametrizados de `test_decisiones_diferidas` para las fichas
de la Parte XXV (EXT-9-01..03). Ningún otro archivo sumó ni restó tests: los tres `monkeypatch` de `test_cli` sobre
lo que el servicio LLAMA pasaron a `servicio`, los barridos de consumidores
de `test_criterios_adoptados` y `test_ext7_cabezal` incluyen ahora
`src/servicio.py`, y las guardias por AST que comparaban la primera parte
del nombre del módulo (`test_ext4`, `test_gui_contrato`, `test_MD`) miran
todas las partes para no quedar vacuas con el prefijo del paquete. La línea
base de la Familia C se regeneró por UNA sola razón medida con `diff`: la
huella `criterios_sha1`, porque `criterios_adoptados.py` cambió sus líneas
de import; ningún número de cálculo ni ningún otro byte se movió. Ninguno de
los diecisiete depende de PyMuPDF ni de Tk, de modo que los cuatro pares
suben 17 exactos. Las cuatro configuraciones se MIDIERON sobre `origin/main`
en `dda328e` (el commit `ext(EXT-9)`, fusionado por fast-forward), en serie,
sobre un checkout limpio (`git worktree`) y sin otra suite en marcha: las
dos sin Tk sin `DISPLAY` y con un `xvfb-run` que falla, las dos sin PyMuPDF
desinstalándolo y reinstalándolo. El commit de cierre que sigue a `dda328e`
lleva los ajustes del auditor adversarial (la guardia del anticipo en
`test_gui_contrato`, que buscaba `cli.X` en el `unparse` y quedó verde
sobre el docstring cuando `anticipo.py` pasó a leer `servicio.X`; el censo
de `from cli import` y la segunda corrida con banderas y `--declarar` en
`test_ext9`) sin sumar ni restar tests, y «sí · sí» se remidió sobre él. **EXT-8 (2026-09-20) sumó CUARENTA tests**: los 33 de
`tests/test_ext8_rendimiento_gui.py` —la aceptación del cluster «rendimiento
y GUI no bloqueante» (PC-10, PC-11, PC-12, PC-17), escrita primero en rojo
con `xfail(strict=True)` de módulo —medidos 28 xfailed y 0 XPASS antes de
tocar código, con `src/sesion.py` y `gui/exportacion_pdf.py` todavía
inexistentes— y liberada al corregir: el presupuesto de `import cli` en
subproceso con `-X importtime`, los tres perezosos comprobados en un
proceso limpio, la sonda de weasyprint con sus dos diagnósticos, la sesión
serializada de la CLI con procedencias, el progreso por stdout, el
subproceso real (PDF, equivalencia del JSON, cancelación, fallo), el anexo
con anclas y el cruce `href`↔`id`, el streaming, los techos de tamaño
MEDIDOS (44.6 KB y 14.0 páginas por punto: el objetivo del dictamen no se
alcanzó, ficha EXT-8-01) y la accesibilidad; los cinco últimos los dejó el
auditor adversarial (la sesión del hijo desde la corrida y no desde los
campos vivos, el hijo que no arranca, la bandera escrita que gana, el HTML
no truncado y el enlace roto del anexo)—, el noveno test de ventana real
en `test_gui_contrato` (`tests/apoyo/gui_ext8_real.py`) más el
parametrizado que crece con `gui/exportacion_pdf.py` en `ARBOLES_DE_LA_GUI`,
y los cinco anclajes de `test_decisiones_diferidas` para las fichas de la
Parte XXIV (EXT-8-01..05). Ningún archivo restó tests: `test_seccion_
rectangular` intercepta ahora `scipy.optimize.brentq` (de donde M4 lo toma
en el punto de uso), los dos de `test_M11_reporte` sondean antes de parchear
`WeasyHTML`, y `test_gui_contrato` lee la sesión de `_datos_de_sesion` y la
versión de `src/sesion.py`. La línea base de la Familia C se regeneró
(cambia el formato de la memoria: enlaces, anexo, el paso 2.1 una sola vez;
ningún número de cálculo se mueve: JSON, CSV y volcados intactos). Las
cuatro configuraciones se MIDIERON sobre `origin/main` en `8c1ac25` (el
commit `ext(EXT-8)`, fusionado por fast-forward), en serie, sobre un
checkout limpio: las dos sin Tk sin `DISPLAY` y con un `xvfb-run` que
falla, las dos sin PyMuPDF desinstalándolo y reinstalándolo. De los 40,
uno depende de PyMuPDF (`test_pc12_las_paginas_por_punto_caben_en_el_
techo_medido`, marcado `pdf`) y uno de Tk (el de ventana real): la columna
«PyMuPDF = no» salta ahora 39 y la «Ventana Tk = no» 13. **EXT-7 (2026-09-20) sumó CINCUENTA Y OCHO tests**: los 50
de `tests/test_ext7_cabezal.py` —la aceptación del cluster «cabezal» C07
(EXT-M-05, EXT-M-06, EXT-M-07 y R95-031), escrita primero en rojo con un
`xfail(strict=True)` de módulo —medidos 44 xfailed y 6 XPASS antes de tocar
código: los cinco del caso límite de Rankine y la guardia de que nada se
cablea a la CLI ya se cumplían— y liberada al corregir: la rama vertical con
cortante alto que se detiene en el plano del cortante (11.10.2 / 11.10.1 →
11.12) y en el piso de la ec. (11-32), `verificar_cuantia` con el mismo
argumento, el docstring comprobado por AST, el Ka de Coulomb del Manual
(`MP.2.4.4.1.5.3`, `DIS-HR-KA-COULOMB`) en el estático y la sobrecarga con
el bloque C de CP-9 recomputado con la escritura del Manual, y
`EstabilidadCabezal` con `exigidas`, `pendientes` y un `estable` estricto;
más los tres ajustes que dejó el auditor adversarial (el [A] del régimen
atribuido en la rama perpendicular, la resultante inclinada δ + β tomada
entera como horizontal y declarada, y el rango «−6.25 % a +7.23 %» de la v8
que era falso: medido −11.1 % a +44.4 %)—, los cuatro anclajes
parametrizados de `test_decisiones_diferidas` para las fichas de la Parte
XXIII (EXT-7-01..04), y los cuatro que crecen solos con los dos criterios
nuevos (dos en `test_ext5_forma_gui`, dos en `test_criterios_adoptados`).
Ningún archivo restó tests: los dos de `test_M9_cabezal` que pineaban
`estable` con tres ítems se reescribieron y uno de `test_ext5_forma_gui`
declara además el plano del cortante. La línea base de la Familia C se
regeneró (cambian la declaración del Ka en la nota de la memoria, el
recuento 71 → 73 criterios / 33 → 35 sin valor y la huella de criterios;
ningún número de cálculo se mueve). Las cuatro configuraciones se MIDIERON
sobre `origin/main` en `42a1cb1` (el commit `ext(EXT-7)`, fusionado por
fast-forward), en serie y sin otra suite en marcha —una primera medición se
descartó porque dos instancias del mismo script se solaparon y una
desinstaló PyMuPDF a mitad de la otra—: las dos sin Tk sin `DISPLAY` y con
un `xvfb-run` que falla, las dos sin PyMuPDF desinstalándolo y
reinstalándolo. Los cuatro pares suben 58 exactos, porque ninguno de los 58
depende de PyMuPDF ni de Tk: la cita nueva entra en los barridos de
`test_normativa_pdf` sin sumar un test. **EXT-6 (2026-09-20) sumó CINCUENTA tests**: los 35
de `tests/test_ext6_registro_normativo.py` —la aceptación del cluster
«registro normativo» (EXT-N-01..04, PC-23, PC-26, PC-30, resto de
EXT-G-03), escritos primero en rojo con `xfail(strict=True)` y liberados
al corregir: DG-2018 presente y medida, la guardia «todo PDF de `normas/`
es Fuente presente o está censado», el RNGIV que no vuelve, las citas
nuevas verificadas contra sus páginas, `norma_producto` por (material,
forma), la elección de edición partida en legal y técnica con
`Fuente.vigencia`, los textos 179 / Manning / TR / fricción, y los dos que
dejó el auditor adversarial (la puerta del criterio legal, que con forma
`str` aceptaba la opción «citada» sin fecha ni acto, y el contrato del JSON
leído del AST en vez de un `AssertionError` en la ruta de exportación)—, los nueve
netos de `tests/test_vigencia_fuentes.py` reescrito para el campo y los
dos criterios (25 frente a 16), y los seis que crecen solos con el
criterio nuevo y las cuatro fichas de la Parte XXII (`test_ext5_forma_gui`,
`test_criterios_adoptados`, `test_decisiones_diferidas`). Las cuatro
configuraciones se MIDIERON sobre el árbol de EXT-6 antes del commit (las
dos sin Tk sin `DISPLAY` y con un `xvfb-run` que falla; las dos sin
PyMuPDF desinstalándolo y reinstalándolo): los dos pares con PyMuPDF suben
50 y los dos sin él suben 49 `passed` y 1 `skipped`, porque el T5 nuevo
—el «5.00 m» de `DG2018.304.07.02#INCREMENTO` en
`VALORES_QUE_LA_CITA_SOSTIENE`— abre el PDF y la columna «PyMuPDF = no»
salta ahora 38 y no 37; ninguno de los 50 depende de Tk, y `sha1_de` es
`hashlib`. `origin/main` quedó en `363091b` por fast-forward y «sí · sí» se
remidió sobre un checkout limpio de ese commit: 2413 passed, 4 skipped. **EXT-5 (2026-09-20) sumó DOSCIENTOS SIETE tests**: los 204
de `tests/test_ext5_forma_gui.py` —la aceptación del cluster GUI (EXT-G-01,
PC-13, PC-14, la mitad de FORMA de EXT-V-02/05/06, la de pestaña 2 de
EXT-V-04 y EXT-G-03): los cuatro casos del prompt escritos primero en rojo
con `xfail(strict=True)` —130 fallos y 31 errores medidos antes de tocar
código— y liberados al corregir; la guardia de forma en las 70 claves (70
parametrizados sobre 'cero', uno por clave); el parser único medido por
casos y por AST en las dos ventanas; `validar_contra_rango` en forma MAT-D13
por comportamiento sobre los cinco tipos de rango y por AST; el censo de las
seis externas; y los tres de ventana real sobre `tests/apoyo/gui_ext5_real.py`,
más los dos que dejó el auditor adversarial (la forma `float` de
`cortante_alto_muro_e060_art_11_10_10_2`, que M9 lee con `float()`, y el
parser sólo con cifras ASCII)— y los tres anclajes parametrizados de
`test_decisiones_diferidas` para las fichas de la Parte XXI (EXT-5-01,
EXT-5-02, EXT-5-03). Ningún archivo restó tests: el test de ventana real de
perfil de `test_gui_contrato` se reescribió (dejó de ser ciego a PC-13) y los
de guardias de consumidor pasaron a `con_valor`. Las cuatro configuraciones se
MIDIERON sobre el árbol de EXT-5 antes del commit (las dos sin Tk sin
`DISPLAY` y con un `xvfb-run` que falla; las dos sin PyMuPDF desinstalándolo
y reinstalándolo), y los cuatro pares coinciden con la derivación: ninguno
de los 207 depende de PyMuPDF, y sólo los tres de ventana real dependen de
Tk (la columna «Ventana Tk = no» salta ahora 12 y no 9). **EXT-4
(2026-09-20) sumó TREINTA Y TRES tests**: los
veintinueve de `tests/test_ext4_contexto_corrida.py` —la aceptación del
cluster «estado» (EXT-A-01, EXT-A-02, EXT-G-02, PC-07, PC-09, PC-15, PC-16,
SIS-B-22 y los 27 accesos a `_USADOS` de la suite): los seis casos del
prompt escritos primero en rojo con `xfail(strict=True)` y liberados al
corregir (dos corridas en el mismo proceso, declarar tras correr, el
`csv_sha1` de la corrida, la sesión B vacía, la GUI que invalida el informe,
«Etapas bloqueadas» como una sola cuenta), más las tres guardias que dejan
la corrección probada: el AST de M11 sin lecturas de estado, el barrido de
la suite sin privados y el contexto congelado—, el de ventana real de
`test_gui_contrato` (`tests/apoyo/gui_contexto_real.py`: el texto real de la
etiqueta y el estado real de los cuatro exportadores tras declarar, quitar,
cargar sesión y fallar; es el QUINTO test de ventana real, y por eso la
columna «Ventana Tk = no» salta ahora 9 y no 8) y los tres anclajes
parametrizados de `test_decisiones_diferidas` para las fichas de la Parte XX
(EXT-4-01, EXT-4-02, EXT-4-03). Ningún archivo restó tests: los nueve que
vaciaban `_USADOS` a mano pasaron a las funciones públicas
(`reiniciar_usos`) o al contexto del informe. Las cuatro configuraciones se
MIDIERON sobre el árbol de `main` en `ec55253` (el commit `ext(EXT-4)`,
fusionado por fast-forward): las dos sin Tk con el `xvfb-run` que falla y
sin `DISPLAY`, las dos sin PyMuPDF desinstalándolo y reinstalándolo; los
cuatro pares coinciden con la derivación (ninguno de los treinta y tres
depende de PyMuPDF, y sólo el de ventana real depende de Tk). El push se
rechazó con 403 durante casi toda la sesión —la app de Claude sin acceso de
escritura al repositorio, como en D9 y PD— y el commit de cierre `d7ffa7a`
lo dejó dicho con su SHA; el acceso se restauró en la misma sesión, `main`
entró por fast-forward y `origin/main` quedó en `d7ffa7a`, sobre el que se
remidió «sí · sí»: 2156 passed, 4 skipped.
**EXT-3 (2026-09-20) sumó TREINTA tests**: los veintiséis de
`tests/test_ext3_regimen_barril.py` —la aceptación del cluster C06 (EXT-M-01,
EXT-M-02, PC-04, PC-27 mitad compuerta, SIS-B-18 mitad JSON): los cuatro
casos del prompt escritos primero en rojo con `xfail(strict=True)` y
liberados al corregir, los tipos nuevos (`RegimenBarril`,
`MetodoNoEvaluableError`, `Bloqueo` en `modelos.py` con `TipoDeBloqueo`), el
dorado CP-12 del régimen lleno, y los tres que dejó el auditor adversarial
(la compuerta llamada en los dos alcances, que una mutación «siempre
diferida» sobrevivía a 277 tests; la celda y/D del resumen siguiendo al
régimen)—, el de B-01 «dimensionado con HW no evaluable/diferido» en
`test_cierre_perfil`, y los tres anclajes parametrizados de
`test_decisiones_diferidas` para las fichas de la Parte XIX (EXT-3-01,
EXT-3-02, EXT-3-03). Las cuatro configuraciones se MIDIERON sobre
`origin/main` en 43b2531 (el contenedor arrancó sin `python3-tk`, se
instaló como manda el bloque de abajo, y las cuatro se midieron: las dos
sin PyMuPDF desinstalándolo y reinstalándolo; las dos sin Tk con el
`xvfb-run` que falla y sin `DISPLAY`). Las cinco citas nuevas entran en los
barridos de `test_normativa_pdf` sin sumar un test, y por eso la columna
«PyMuPDF = no» sigue saltando 33. **EXT-2 (2026-09-20) sumó DIECINUEVE tests**: los diecisiete de
`tests/test_ext2_multicelda_transicion.py` —la aceptación del cluster
hidráulico A del dictamen (EXT-M-03, EXT-M-04, PC-06, PC-19), catorce escritos
primero en rojo con `xfail(strict=True)` y liberados al corregir, dos que
fijan lo que NO cambia (la continuidad en q\* = 3.5 y 4.0, y V6 con N > 1) y
el que dejó el auditor adversarial (la fila «Hidráulica» de la tabla de M11
dice N y Q_celda)— y
los dos anclajes parametrizados de `test_decisiones_diferidas` para las fichas
nuevas de la Parte XVIII (EXT-2-01, EXT-2-02); ningún otro archivo sumó ni
restó tests (el test de la recta de `test_M4_control` se reescribió, no se
duplicó). Se midió «sí · no» sobre el árbol final (2089/8); las otras tres se
derivan sumando 19, porque ninguno de los diecinueve depende de PyMuPDF ni de
Tk: la cita nueva `HDS5_3ED.5.4.3#REPARTO`
entra en los barridos de `test_normativa_pdf` sin sumar un test. **EXT-1
(2026-09-20) había sumado NOVENTA Y DOS tests**: los 89 de
`tests/test_ext1_entradas.py` —la aceptación del cluster «entradas» del
dictamen, escrita primero en rojo con `xfail(strict=True)` y liberada al
corregir, un bloque por ID (EXT-A-03, EXT-V-02..06, PC-01, PC-02, PC-05,
PC-28, PC-32..35), más los dos de regresión que dejó el auditor adversarial
(la clave de fila que no «difiere» de ninguna celda y el par de Manning sin
declarar)—, el del «mismo rasero» para los criterios `Derivada` en
`test_criterios_adoptados`, y los dos anclajes parametrizados de
`test_decisiones_diferidas` para las fichas nuevas de la Parte XVII (PC-32 y
EXT-V-02). Se midió «sí · no» sobre el árbol final (2070/8); «no · no» se
midió antes de los dos tests del auditor (2035/41) y se deriva sumando 2,
porque ninguno de los dos depende de PyMuPDF; las dos con Tk se derivan
sumando 4, como en EXT-0: el contenedor no tenía `python3-tk`. **EXT-0 (2026-09-20)
había sumado CUATRO tests sin tocar un test**:
son los anclajes parametrizados de
`test_decisiones_diferidas.py::test_el_simbolo_que_cada_ficha_ancla_sigue_existiendo`
para las cuatro fichas nuevas de `docs/decisiones_diferidas.md` (SIS-B-22,
NOR-HID-02, EXT-V-01, EXT-G-03), de modo que el parametrizado crece con el
registro. Se midieron las dos configuraciones sin Tk sobre el árbol de EXT-0
(sí · no: 1978/8; no · no: ver la tabla) y las dos con Tk se derivan sumando
4, porque ese test no depende ni de PyMuPDF ni de Tk: el contenedor de EXT-0
no tenía `python3-tk` y no se instaló. **Las cuatro medidas anteriores, sobre
el mismo árbol en PD**
(`aefbdcd`, la rama de trabajo; el push se rechazó con 403 —la app de
Claude volvió a no tener acceso de escritura al repositorio, como en D9— y
las cuatro se midieron sobre ese árbol; el acceso se restauró en la misma
sesión, la rama entró en `main` por fast-forward y `origin/main` quedó en
`0c71854`, que sólo añade los sellos y esta tabla; la configuración
«sí · sí» se remidió sobre él: 1978 passed, 4 skipped, y los sellos de
`indice_formulas.md` y `trazabilidad.csv` llevan ese SHA), que sumó SIETE
tests, todos en
`tests/test_dimensional_piloto.py`: `K_MANNING_SI` en los tres
parametrizados del censo de constantes `_SI`, la afirmación positiva de
Manning con `k_n`, los dos censos en cero, el umbral del paso 4.3 juzgado
sobre una magnitud de su sustitución (`UMBRAL_JUZGA`), y la guardia sobre
el AST de M3 que pidió el auditor adversarial (sin ella, revertir
`_caudal_manning` a `(1/n)` dejaba la suite verde). D9 las había medido
sobre el árbol anterior (`749311c`, el `main` fusionado por fast-forward;
el push se rechazó primero con 403 —la app de Claude no tenía acceso de escritura al
repositorio— y entró horas después, una vez restaurado el acceso, sin
cambios: `origin/main` quedó en `80f2bc9`, que sólo añade los sellos y esta
tabla, y la configuración «sí · sí» se remidió sobre él: 1971 passed, 4
skipped), que sumó UN test neto: la ficha D9-01
en el parametrizado de `test_decisiones_diferidas` (la vía 2 del canal
censada sin usuario al resolver `DIS-HR-FORMAS-HDS5`; el test de la vía 2
se reescribió uno por uno). T3 las había medido sobre el árbol anterior
(`1aed003`), que sumó veintiún tests,
todos en `tests/test_trazabilidad_csv.py`: la sincronía de
`docs/trazabilidad.csv` con el registro, su sello de cuatro partes, las
catorce columnas, el orden determinista y los dos índices inversos
derivados. El sello de `docs/trazabilidad.csv` lleva ese mismo par —firmado
en el commit de cierre, porque el par se mide sobre `origin/main` y no
puede conocerse antes de la fusión—, y `test_trazabilidad_csv` exige que
sea un par. I4 las había medido sobre el árbol anterior
(`c4aca04`), que sumó treinta y nueve
tests: los diecinueve de `tests/test_indice_formulas.py` (la sincronía del
índice de fórmulas generado, su sello y sus huecos), los diecinueve de
`tests/test_dimensional_piloto.py` (el chequeo dimensional de M3–M5 con su
censo de lo que no cierra, y las dos constantes `_SI`) y la ficha `I4-01`
parametrizada en `test_decisiones_diferidas`; el sello de
`docs/indice_formulas.md` sigue llevando el par de I4, que es el del árbol
sobre el que se generó. T1 las había medido sobre el árbol anterior
(`c09c459`), que sumó diecinueve tests:
los dieciséis de `tests/test_vigencia_fuentes.py`, el de la resolución
impresa del Manual de Puentes en `test_normativa_pdf` (por eso la columna
«PyMuPDF = no» salta ahora 33 y no 32), la ficha `T1-01` parametrizada en
`test_decisiones_diferidas` y el criterio nuevo en el parametrizado de
pendientes de `test_criterios_adoptados`. N2 las había medido sobre el árbol
anterior (`dbba580`), que sumó once tests: la
guardia de la traducción no oficial de M 294-11
(`test_toda_cita_de_la_traduccion_de_M294_lo_dice`), los ocho de `CP11` en
`test_M2_material`, el del motivo de descarte del HDPE en `test_MD` y la
ficha `N2-01` parametrizada en `test_decisiones_diferidas`. Post-N1 las
había medido sobre el árbol anterior (su +1 fue el censo de las citas sin
firma deliberada, `CITAS_SIN_FIRMA_A_PROPOSITO`), N1 sobre el previo (su
ficha `N1-01`) y pre-N1 sobre el anterior a ése. Conviene
decir cómo llegó la tabla hasta ahí,
porque es el defecto que este párrafo persigue: I1b la dejó en 1830 y después
**seis sesiones** (G3, I3, R3, R3b, G2, G5) sumaron 51 tests sin volver a
medirla; pre-N1 la encontró en 1881 y fusionó además la rama de S24, que
llevaba desde el 2026-09-09 sin entrar en `main` y cuya ficha `S24-01` trae su
propio caso parametrizado en `test_decisiones_diferidas`: 1882; N1: 1883;
post-N1: 1884; N2: 1895; T1: 1914; I4: 1953; T3: 1974; D9: 1975; PD: 1982;
EXT-0: 1986; EXT-1: 2078; EXT-2: 2097; EXT-3: 2127; EXT-4: 2160; EXT-5:
2367; EXT-6: 2417; EXT-7: 2475; EXT-8: 2515; EXT-9: 2532; EXT-10: 2617. La
«Ventana Tk = no» de las medidas de pre-N1 se consiguió simulando la ausencia
de entorno gráfico (sin `DISPLAY` y con un `xvfb-run` que falla), que es una
de las tres condiciones legítimas del salto; en N1, corriendo la suite ANTES
de instalar `python3-tk` (el contenedor arranca sin él) y otra vez después;
post-N1, N2, T1, I4, T3, D9 y PD repitieron el procedimiento de pre-N1 (N2,
T1, I4, T3, D9 y PD instalaron antes `python3-tk` y las dependencias de
`python3.12`, como manda el bloque de abajo). La «PyMuPDF = no», en todas
esas sesiones, desinstalándolo para la medida y reinstalándolo después:

| PyMuPDF | Ventana Tk | `passed` | `skipped` |
|---|---|---|---|
| sí | sí | 2613 (medido en EXT-10) | 4 |
| sí | no | 2603 (medido en EXT-10) | 14 |
| no | sí | 2578 (medido en EXT-10) | 39 |
| no | no | 2568 (medido en EXT-10) | 49 |

**Cómo se consigue la columna «Ventana Tk = sí», que S21 dio por imposible.**
S21 escribió que el contenedor no tiene `tkinter` en ninguno de sus intérpretes
y dejó dos celdas vacías. Era cierto y no era el final: `apt-get install
python3-tk` se lo da a `python3.12`, y con `xvfb-run` —que ya estaba— los
cuatro tests de ventana corren. La sonda de `test_gui_contrato._interprete_con_ventana`
los encuentra sola, sin tocar nada. Queda escrito porque una celda vacía se lee
como «no se puede» cuando lo cierto era «no estaba instalado»:

    apt-get install -y python3-tk
    python3.12 -m pip install numpy scipy ttkbootstrap weasyprint --break-system-packages

`weasyprint` entró en esa línea en EXT-8: sin él, el noveno test de ventana
real pasa igual —mide la vía del navegador— pero NO ejercita el subproceso
del PDF, que es lo que EXT-8 cerró; con él, lo ejercita de punta a punta
(botón apagado con motivo, progreso, estado terminal, cancelación). Medido
en EXT-8 sobre este contenedor en las dos condiciones.

**Y el número saltó de 1538 a 1794 en dos sesiones, no en una.** La tabla se
quedó en el árbol de S20 mientras la suite crecía: al abrir S21 el conteo ya
era `1651 passed, 35 skipped` (1686). Conviene decirlo porque la deriva de esta
tabla es el defecto que la propia sección persigue.

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
`docs/hoja_de_ruta_correcciones_v12.md`. **Desde EXT-0 (2026-09-20) la hoja
`Hallazgos` tiene 303 filas, no 237**: entraron los 23 hallazgos de la
auditoría externa del 2026-09-19 con prefijo `EXT-` (nunca los prefijos
desnudos `A-`/`M-`/`V-`/`G-`, que colisionan con la de Sistema), los 35 puntos
ciegos `PC-` de su dictamen (`docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md`),
siete ítems `R95-`/`R48-` de los temarios de refutación que no tenían fila de
estado, y `C5-02`. Su plan es la cadena `docs/planes_mejora/07_CADENA_PROMPTS_EXT.md`
(serie de commits `ext(EXT-n)`), y un hallazgo puede volver de «Cerrado» a
«Reabierto (EXT-0)» cuando llega un argumento nuevo: le pasó a NOR-HDS-05,
NOR-HID-02 y SIS-B-22.

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
