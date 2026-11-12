# Reglas del proyecto

## Fuente de verdad
- Fuente normativa única: docs/hoja_de_ruta_alcantarillas_v8.md (o la version
  vigente que exista en docs/: M11 la localiza con el patron
  `hoja_de_ruta_alcantarillas_v*.md` y exige que haya exactamente una). Toda cita de
  numeral se verifica contra ese archivo. Nunca se inventa un numeral.
- Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta.
- **La única excepción a lo anterior: la fuente primaria.** Si la hoja de ruta
  discrepa del documento normativo original —el PDF en `normas/`, o en el
  repositorio de normas enlazado por `NORMAS_DIR` (ver «Dónde están los PDF
  de normas»)— y la
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
- **La hidrología es un módulo aparte que sólo conoce el servicio (T-1).**
  `src/modulos/MH_hidrologia.py` es la Fase 1-bis: calcula el caudal de un
  punto de Familia A o B a partir de `--cuencas` y `--estacion`
  (`servicio.cargar_hidrologia`, `servicio._fase_hidrologia`), y lo importa
  SÓLO `src/servicio.py` (fijado por AST). El caudal calculado entra al
  pipeline como `Q_m3s` del punto de cálculo, igual que el declarado, y
  ningún módulo de M1 a M11 sabe de cuál de los dos se trata salvo por
  `InformePunto.caudal` (un `CaudalDeDiseno` de `modelos.py`, con su origen,
  sus pasos y sus avisos). Tres reglas que no se negocian: un `Q_m3s` lleno
  GANA y no se recalcula ni se corrige; la serie, las cuencas y los años FEN
  son entradas del proyecto (`docs/contrato_entradas.md` §2-bis) y el
  repositorio no trae ninguna salvo las sintéticas de
  `tests/fixtures/hidrologia/`, rotuladas; y ninguna función pública del
  módulo entrega una lluvia o un caudal de diseño sin pasar por el criterio
  `homogeneidad_serie_fen` (`precipitacion_de_diseno`, `caudal_de_diseno` y
  `caudal_de_aporte_cuneta` son las tres puertas; esta última es el enlace
  para la longitud de cuneta de la Fase 10). La GUI y la sesión todavía no
  conocen las dos entradas (ficha T1-04).
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
  EXT-5, 53 de las 70 claves (71 desde EXT-6, 73 desde EXT-7, 74 desde E-A, 75 desde PF-1, 76 desde PF-4, 77 desde el cierre de C10, 79 desde el de C05, 82 desde T-2, 88 desde T-4, 95 desde T-1, 97 desde T-6, 102 desde T-8, 109 desde T-5) aceptaban la cadena `'cero'` y la GUI no podía
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
  deriva de ahí (EXT-G-03). Son ocho desde T-2, que sumó las dos que no son
  una magnitud: `seccion_receptor_medida` (un objeto: la sección levantada
  del receptor, que gana sobre el criterio `seccion_receptor`) y
  `acceso_mantenimiento_previsto` (un booleano por punto); las dos,
  opcionales y sin valor por defecto.
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

**Y desde S21 el nivel lo llevan los 69 (70 desde T1, 71 desde EXT-6, 73 desde EXT-7, 74 desde E-A, 75 desde PF-1, 76 desde PF-4, 77 desde el cierre de C10, 79 desde el de C05, 82 desde T-2, 88 desde T-4, 95 desde T-1, 97 desde T-6, 102 desde T-8, 109 desde T-5), no sólo los que no tienen valor.** La
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
  `demanda_sismica_licuefaccion`, que no tiene consumidor. De los **nueve** sin
  consumidor (diez hasta T-1, que le dio consumidor real a
  `homogeneidad_serie_fen` —`MH_hidrologia.precipitacion_de_diseno`— y lo
  sacó del censo; ocho hasta T1; T1 sumó `edicion_que_rige_el_expediente`, la
  decisión de marco normativo del expediente, que ningún módulo consume, y
  EXT-6 su mitad legal, `edicion_legal_que_rige_el_expediente`, partida de
  aquélla porque el Manual de Puentes está derogado por RD y las normas
  técnicas de EE.UU. no —EXT-N-01, PC-26—) el
  nivel es un argumento y no una medida, y están censados en
  `SIN_CONSUMIDOR_Y_SIN_MEDIDA` para que el grupo no crezca en silencio —el
  mismo recurso que fija el censo de los dos `inf` deliberados—.

**Para qué se completó, además de por completitud:** `nivel` gobierna el
filtro de alcance de la pestaña 2 (`criterios_adoptados.criterios_del_alcance`),
que a `--alcance perfil` pasa la tabla de 69 filas (70 desde T1, 71 desde EXT-6, 73 desde EXT-7, 74 desde E-A, 75 desde PF-1, 76 desde PF-4, 77 desde el cierre de C10, 79 desde el de C05, 82 desde T-2, 88 desde T-4, 95 desde T-1, 97 desde T-6, 102 desde T-8, 109 desde T-5) a 36 y los pendientes
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
  declarado su TR (`Q_evento_extremo_m3s`; la frase decía «este software no
  hace hidrología», y desde T-1 la hace: la Fase 1-bis calcula el caudal de
  DISEÑO con `--cuencas` y `--estacion`. El del evento extremo sigue siendo
  un dato que falta, porque V8 todavía no se lo pide —ficha T1-03—),
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
  conseguir. **Y desde T-5 la Fase 8 la levanta por tres datos de PRODUCTO**
  que el programa no puede elegir: la D-load de una clase de AASHTO M 170M
  que el ejemplar de `normas/` no deja leer (`clases_producto_por_relleno`),
  el perfil del tubo de HDPE que solo da su fabricante
  (`perfil_hdpe_fabricante`) y la resistencia de una costura empernada del
  TMC. Los tres detienen un escalón que CUMPLE toda la tabla de la Fase 5, y
  por eso `MD.disenar_punto` los relanza cuando ningún candidato cierra
  (`ATRIBUTO_ESCALON_CUMPLE_LO_DEMAS`): un punto al que solo le falta un
  dato no es «no factible» (ficha T5-10).
- DatoInvalidoError: el dato **está** pero no puede ser: no es del tipo
  esperado, cae fuera del rango físico de dominios.py, o contradice a otro
  dato de su misma fila (§1.5). Hermana de DatoFaltanteError y no la misma:
  "falta la columna cbr_subrasante" y "el CBR dice −3 %" son dos problemas
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
  `DisenoNoFactibleError`. Su `str()` empieza por
  `MOTIVO_METODO_NO_EVALUABLE` —el rótulo de los dos casos de HDS-5— o, desde
  T-1, por el que el constructor reciba en `rotulo=`: la Fase 1-bis levanta
  la MISMA excepción por los límites del Manual de Hidrología (el método
  racional desde 10 km², Témez fuera de 0.25–24 h, una distribución sin
  estimador impreso, un ajuste que no pasa K-S, `serie_sin_fen` con menos
  lluvia que la serie completa) y la encabeza con
  `MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA`, porque encabezarla con HDS-5 sería
  una cita falsa (ficha T1-06). Desde T-8 la levanta también M6 por los
  límites de HEC-14 —la Ec. (10.4) fuera de un conducto circular único, un
  conducto de más de 60 in = 1.524 m de alto (nota 8 de la Tabla 1.1; 1.50 m
  hasta las correcciones de T-8, que lo leen con la cifra en pulgadas para
  dejar evaluable el ejemplo resuelto de la propia fuente), un TW sobre el
  rango de la ecuación, un suelo cohesivo fuera del IP de las Ec. (5.2) y
  (5.3), la Tabla 5.2 agotada, varios barriles—, encabezada con
  `MOTIVO_METODO_NO_EVALUABLE_HEC14`; y dentro de la Fase 6 NO viaja como
  `Bloqueo`: la Fase 6 corre después del dimensionado, la captura y la
  convierte en el aviso del contraste que no se evaluó (rige el d50 de
  Laushey con lo adoptado, también bajo la envolvente de las correcciones de
  T-8: fichas T8-01 y T8-07). Y desde T-5 la levanta M8 cuando el relleno queda
  fuera del dominio del método de la carga viva a través del relleno de
  AASHTO LRFD 3.6.1.2.6a (menos de 2.0 ft sobre un tubo de concreto o un
  marco, 1.0 ft o menos sobre un flexible), encabezada con
  `MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL`: diferible a nivel de perfil,
  como V1/V2. Y desde EXT-3 `Bloqueo` vive en `modelos.py`
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
- **Enmienda (rediseño visual, bloque 3): la navegación es LATERAL y el
  Notebook se conserva por debajo.** «Notebook por pestañas» sigue siendo
  cierto como ESTRUCTURA y deja de serlo como CARA: la ventana principal
  tiene una columna de cuatro pasos numerados (`gui/componentes.py::
  NavegacionLateral`) que conmuta el `ttk.Notebook` de siempre, cuya tira de
  pestañas se retira por estilo (`Lateral.TNotebook`, layout vacío de su
  `Tab`). Lo que NO cambia, y es lo que la enmienda protege: `nb.select`,
  `nb.tabs`, `nb.index` y los cuatro `nb.add` siguen siendo la puerta única
  para cambiar de vista —la suite y los apoyos de ventana real la usan— y el
  paso activo tiene UNA fuente, el Notebook, que la columna lee por
  `<<NotebookTabChanged>>`; la columna nunca lleva el paso por su cuenta.
  Las ventanas emergentes (ayuda de entrada) siguen con sus pestañas a la
  vista. La decisión y su alternativa descartada —retirar el Notebook y
  apilar marcos a mano— están en la ficha REDISEÑO-3-01 de
  `docs/decisiones_diferidas.md`. El tema entero (paleta, tipografía,
  estilos con nombre, `Panel`, `Insignia`, `TituloDeVista`) vive en
  `gui/componentes.py` desde el bloque 1, y en Windows `gui.app.main`
  declara la conciencia de DPI por monitor antes del primer `Tk` (bloque
  1b): sin eso el contenido se veía borroso con la pantalla escalada.
- **Dónde están hoy esos componentes, que ya no es `legacy/Tc.py`.** La regla
  decía «leer esos archivos antes de escribir GUI», y mandaba a un programa
  que ya no se puede ni importar en este repositorio: `matplotlib` es import de
  nivel superior y no está en `requirements.txt`, y la `plantilla_memoria.html`
  que su encabezado anuncia no existe (SIS-B-10). La extracción ya se hizo:
  `Tooltip` y `MarcoScroll` son el MISMO código movido a `gui/componentes.py`;
  `CampoValidable` es su `_campo_validable` con la validación al escribir que
  exige la Sec. 4.3; y el patrón de plantilla `%%` vive en
  `M11_reporte.PlantillaHTML`. Se escribe GUI leyendo `gui/componentes.py`.
  `legacy/Tc.py` **se conserva** —la §1.2 de la hoja de ruta lo nombraba como
  origen del caudal de diseño Q— pero se lee como ANTECEDENTE, no como
  plantilla viva. **Desde T-1 ya no es el origen de nada**: el caudal de un
  punto de Familia A o B entra declarado por la columna `Q_m3s` o lo calcula
  `src/modulos/MH_hidrologia.py`, `PERFILES[...].origen_del_caudal` lo dice
  así, y el encabezado de `legacy/Tc.py` lleva la marca SUPERSEDED.
  Su estatus completo está en su propio encabezado y en
  `docs/decisiones_diferidas.md`.
- **Desde E-B la pestaña 2 declara por editores TIPADOS, y el literal sigue
  siendo la fuente.** `gui/editores.py` monta un editor por
  `Criterio.forma` (escalar, par, serie de pares, dict con campos, serie de
  claves; LITERAL para lo que la ficha no descompone, sin inventar campos),
  cada campo es un `CampoValidable` que valida al escribir con
  `src.editores.validar_campo`, y el contenido —campos, ventanas, filas de la
  tabla y la celda que cada fila propone— lo deriva `src/editores.py` de la
  ficha y del registro, sin Tk. Los editores COMPONEN el campo literal
  «Valor nuevo» (dos vistas, un valor) y «Aplicar» declara en UNA llamada por
  `src.editores.declarar`, que enruta a la puerta de `declaracion.py` del
  modo del criterio y registra la procedencia: elegir una fila obtiene el
  valor de la tabla; teclear la clave de una fila la nombra (y R4 rechaza
  la que no es elegible); un texto que nombra una fila DISTINTA de la
  elegida no entra, con o sin nota, y lo rechaza la puerta
  (`declaracion.declarar_desde_tabla`), de modo que vale también para la
  ventana emergente —la revisión de E-B lo midió después del cierre:
  «cajon_aletas_paralelas_escuadra» entraba «proveniente de la fila
  cajon_aletas_30_75_escuadra»—; un número nunca nombra una fila; un número que
  DIFIERE de la celda, o que no proviene de ninguna fila en un criterio de
  tabla, exige nota o no entra; un dict de tabla toma de la fila sus campos
  homónimos o exige nota; una categoría elige dentro de su conjunto cerrado
  sin fila; un dato de ensayo exige la nota, que es su trazabilidad. La
  pestaña 2 ya no llama a `establecer_valor_dinamico`
  ni olvida procedencias (fichas EB-01, EB-02). La ventana emergente
  conserva su campo único (EB-06). El comparador de dos `informe_json`
  (`src/comparador.py`, E14) vive en la pestaña 4 y en `cli.py --comparar`,
  nunca recalcula y es la MISMA comparación que la CLI hace con la corrida
  embebida en la sesión; responsable y evidencia de un pendiente
  (`src/responsable.py`, E13 reducido) se derivan de `resolucion` y
  `reemplazado_por` y se pintan en la pestaña 4, en el anticipo y en el JSON;
  la memoria lleva índice derivado de los `<h2 id>` de la plantilla y de los
  puntos (`M11.indice_de_la_memoria`, E21 acotado).
- **Desde PF-2 el anticipo de la pestaña 1 tiene un cuarto bloque, los
  datos que faltan punto a punto**, y sigue siendo una ESTIMACIÓN que no
  gobierna ningún botón. `anticipo.datos_faltantes_por_punto(csv, externos,
  alcance)` lo deriva de lo que la corrida consulta —los vacíos admitidos
  de M0, los consumidores del censo menos los módulos que el alcance
  difiere, `servicio.CLAVES_EXTERNAS` con `familias_que_usan`, la columna
  que exige una sola familia (`servicio.FAMILIAS_QUE_EXIGEN_COLUMNA`) y el
  predicado del TW que `_resolver_tw` comparte (`tw_sin_via_de_sec_1_3`)—
  y dice de cada falta si DETIENE una etapa o ESPERA a un tablero, con la
  misma etapa y el mismo detalle que el `Bloqueo` llevará
  (`ETAPA_FALTA_*`, `DETALLE_FALTA_*`). Estima de MÁS a propósito, porque
  la corrida se detiene en la primera falta de cada punto y el pre-vuelo
  las dice todas; la unión de `tests/test_pf2_prevuelo.py` fija que
  ninguna falta real escapa y censa lo de más con su razón (ficha PF-2-01).
  La carga se comprueba PRIMERO: una celda que M0 no admite vacía en esa
  familia, una celda no numérica o una familia ilegible detienen la carga
  aunque el JSON «cubra» el dato (auditor adversarial de PF-2). La CLI lo
  expone con `--prevuelo` (imprime los cuatro bloques y termina sin correr:
  0 si nada detiene la carga ni una etapa, 1 si algo lo hace; «espera» no
  es una falta) y la ventana lo pinta en una tabla más del mismo panel,
  refrescada también al cambiar el JSON y las banderas; `gui/app.py` sólo
  pinta.
- **Desde PF-3 un [A] se puede BARRER sobre su ventana, y el barrido no
  recalcula ni deja rastro.** `src/barrido.py::barrer(csv, externos,
  alcance, clave, valores, fila=, nota=, declaraciones_base=, volcar=)`
  corre `servicio.correr` una vez por valor y devuelve un
  `ResultadoDeBarrido` de `modelos.py` con los volcados enteros dentro y
  una tabla por (valor, punto) leída del volcado. Tres reglas, fijadas en
  `tests/test_pf3_barrido.py`: (1) cada valor entra por LA MISMA puerta
  que la pestaña 2 (`editores.declarar`: forma, ventana, fila o nota para
  un criterio de tabla, trazabilidad de un dato de ensayo) y entra ANTES
  de la primera corrida, de modo que un valor fuera de la ventana no corre
  nada —un barrido fuera de la ventana no es sensibilidad, es otra
  adopción—; (2) cada corrida parte del estado de entrada y al salir,
  también con excepción, el proceso queda como estaba (fotografía de
  `declaracion.estado_de_sesion` y `restaurar_sesion(sustituir=True)`, la
  vía de «Cargar sesión», que repone también la procedencia); (3) la
  comparación de cada corrida con la del primer valor es la del comparador
  de E-B (`comparador.comparar`), «no comparable» incluido cuando cambia
  el método, y `src/barrido.py` no importa `src.modulos` ni `cli` (por
  AST): el volcador entra como argumento (`volcar=cli.informe_json`). La
  puerta es una función aparte, `barrido.verificar_valores`, que aplica
  también `declaraciones_base` —la elegibilidad de una fila (R4) depende
  de otros criterios— y que la CLI llama para TODOS sus barridos antes de
  correr el primero; un punto que deja de dimensionar dice qué
  verificaciones incumplió en su progresión
  (`FilaDelBarrido.incumplidas_en_la_progresion`, leído de
  `iteraciones[].incumplidas`), y una verificación que desaparece del
  volcado cuenta como cambio de veredicto (auditor adversarial de PF-3,
  que midió además cuatro mutantes vivos sobre las tres columnas de la
  tabla, hoy muertos). La
  CLI lo expone con `--barrido CLAVE=v1,v2,v3` (repetible, UNA clave a la
  vez, nunca el producto cartesiano; `--barrido-nota` y `--barrido-fila`
  valen para todos los de la invocación; la coma SEPARA valores, de modo
  que PC-34 no aplica y `3,5` son dos), imprime la tabla, avisa de las
  banderas que no aplica y escribe `{"barridos": [...]}` en `--json` o en
  `<csv>.barrido.json`; NO arma memoria, porque el barrido es un anexo
  de la tesis y no parte del expediente. El botón «Barrido…» de la
  pestaña 2 se difirió con símbolo (ficha PF-3-01).

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

## Dónde están los PDF de normas: `NORMAS_DIR`, con caída a `normas/`

**Decisión de T-0 de la cadena T (2026-11-11), opción (a): una variable de
entorno, no un submódulo ni un enlace simbólico.** Los PDF se buscan en dos
carpetas, en este orden, y una sola puerta las conoce
(`src/normativa/fuentes.py`: `directorios_de_normas()`, `ruta_pdf(fuente)`,
`pdf_en_disco()`):

1. la que nombre la variable **`NORMAS_DIR`**: el clon del repositorio de
   normas (`Andy-rba30/Normas`). Vale la raíz del clon o su subcarpeta
   `normas/`, que es donde ese repositorio guarda los PDF;
2. `normas/` de este repositorio, **mientras exista** (T-12 la retira).

El comando, que es el que usa toda sesión de la cadena T:

    git clone https://github.com/Andy-rba30/Normas.git /ruta/a/Normas   # una vez
    export NORMAS_DIR=/ruta/a/Normas
    python3 -m pytest -q -p no:cacheprovider --no-header

Y para leer un PDF con la herramienta de siempre, que resuelve el fragmento
del nombre en las dos carpetas:

    NORMAS_DIR=/ruta/a/Normas python3 -m src.normativa.extraccion texto hec14 202

- **Por qué una variable.** El repositorio de normas lleva documentos con
  copyright (AASHTO, ASTM) y T-12 recomendará hacerlo privado. Un submódulo
  ataría cada clon de la app a una credencial sobre él y versionaría aquí su
  URL y su commit; un enlace simbólico `normas → …` no convive con la carpeta
  `normas/` real que todavía no se ha retirado. La variable no versiona nada,
  vale con el repositorio público o privado, y un despliegue que sólo calcula
  no tiene que clonar 330 MB: **ningún módulo de cálculo abre un PDF**, sólo
  quien verifica (los tests `-m pdf`, `python3 -m src.normativa.extraccion`,
  `verificar_sesion.py`). Ficha T0-01 de `docs/decisiones_diferidas.md`.
- **`Fuente.archivo_pdf` es un nombre lógico** («normas/hif12026.pdf»), no
  una ruta: dice cómo se llama el archivo dentro de la carpeta de normas, esté
  donde esté. Nadie compone `RAIZ / fuente.archivo_pdf`: se llama a
  `fuentes.ruta_pdf(fuente)`, que devuelve la ruta donde el archivo está, o
  donde se le esperaba si no está (y entonces quien llama decide si salta).
- **`normas/` de la app NO gana PDF.** Las dos fuentes que T-0 dio de alta
  —HEC-14 (`hec14.pdf`, FHWA-NHI-06-086, 3.ª ed., julio de 2006) y el WSDOT
  Hydraulics Manual (`HydraulicsManual.pdf`, M 23-03.12, abril de 2026)—
  viven **sólo** en el repositorio de normas y están censadas en
  `fuentes.SOLO_EN_EL_REPO_NORMAS`. Copiarlas a `normas/` pone en rojo la
  guardia de PC-23 (`tests/test_ext6_registro_normativo.py`).
- **Sin `NORMAS_DIR` la suite queda verde y SALTA dieciocho tests** (siete
  hasta T-2; T-4 sumó los cinco de `tests/test_t4_materiales_durabilidad.py`
  que abren el WSDOT Hydraulics Manual, y T-1 los seis de
  `tests/test_t1_hidrologia.py` que abren su capítulo 2), que es un
  tercer eje de entorno además de PyMuPDF y Tk: los dos T0 de
  `test_normativa_pdf` (verifican las dieciséis fuentes que sí están y
  después saltan nombrando las dos que faltan), los cuatro de
  `tests/test_t0_gobernanza.py` que abren los dos PDF nuevos, y la mitad de
  la guardia de PC-23 que mira el repositorio enlazado. `verificar_sesion.py`
  lo dice en su paso 5 como AVISO. **Una sesión de la cadena T no cierra con
  esos dieciocho saltados**: enlaza el repositorio y los corre.
- **Un `NORMAS_DIR` que apunta a una carpeta que no existe no se calla**:
  `FileNotFoundError`. Quien definió la variable quiso enlazar el repositorio,
  y caer en silencio a `normas/` le daría una suite verde que no verificó lo
  que creía.

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
segundo eje. Lo invariante es `collected = passed + skipped`, hoy **5246**; lo
que se mueve es el reparto, y **ningún salto de los de abajo es una
regresión**. (Desde T-0 hay un TERCER eje, el repositorio de normas enlazado
o no por `NORMAS_DIR`: son dieciocho saltos más sin él (siete hasta T-2, doce hasta T-4), descritos en «Dónde
están los PDF de normas».) Son de **dos** clases desde EXT-11, y hasta entonces eran tres
(la primera viñeta de abajo explica la que desapareció):

- `tests/test_MD.py` YA NO SALTA. Hasta EXT-11 tenía el `skipped`
  **permanente** por condición imposible —un `skipif` que guardaba que
  `M5_verificaciones` no existiera, y ya no podía darse—, que era un test que
  nunca corría (PC-22). EXT-11 lo sustituyó por la simulación de la ausencia
  REAL: un subproceso sobre una copia del árbol sin el archivo de M5, donde
  `import_module` falla de verdad. Por eso la columna «sí · sí» pasa de 4 a
  3 saltos.
- `tests/test_gui_contrato.py` y `tests/test_ext5_forma_gui.py` — los tests
  de **ventana real**, que hoy son **once** en `test_gui_contrato` y `test_ext5_forma_gui` (S20 abrió el
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
  cuando no—; EXT-10 el de las dos obras; el cierre de C09 el de las tres
  caras restantes de la ventana normativa, `tests/apoyo/gui_caras_normativa.py`,
  que declara por el camino del botón en RANGO, CATALOGO y CAMPO—). Se saltan
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
  que S12 documentó. Con los marcados `pdf` de otros archivos eran 35 en
  total hasta T-0, **39** desde T-0, que sumó cuatro en
  `tests/test_t0_gobernanza.py` (la portada, las páginas y la paginación de
  HEC-14 y del WSDOT Hydraulics Manual), **40** desde T-2, que sumó
  el de las cifras del ejemplo publicado de HDS-5 contra su página
  (`tests/test_t2_hidraulica.py`), y son **55** desde T-4, que sumó los
  quince de `tests/test_t4_materiales_durabilidad.py` que fijan en su página
  los números que el cálculo toma de WSDOT, AASHTO LRFD, HDS-5, EG-2013,
  ASTM A796 y la E.050. T-1 sumó **veinte** en `tests/test_t1_hidrologia.py`
  (catorce hechos del capítulo III del Manual de Hidrología y seis del
  capítulo 2 de WSDOT). Contados con `--collect-only -m pdf` son **76**
  sobre el árbol de T-1 y eran 56 sobre `7fb7926`, uno más que el 55 de la
  frase anterior: la diferencia es de antes de T-1 y no se rastreó. T-5 sumó
  **veintiocho** (trece en `tests/test_t5_estructural_conducto.py` y quince
  en `tests/test_t5_correcciones_auditoria.py`, que fijan en su página los
  números y las frases de AASHTO LRFD, el Manual de Puentes y el EG-2013 en
  que se apoya la Fase 8): son **104** sobre el árbol de T-5. Ninguno abre
  HEC-14 ni WSDOT, de modo que el eje de `NORMAS_DIR` no se mueve. Las
  correcciones de T-8 sumaron **uno** en `tests/test_t8_correcciones.py` (las
  llamadas de las Tablas 511-02 y 511-06 del EG-2013, que está en `normas/`
  de la app): son **105**, contados con `--collect-only -m pdf` sobre su
  árbol.

**No basta con que el intérprete de la suite tenga tkinter**, y conviene
decirlo porque invita al error contrario: el test de ventana sondea primero
`sys.executable` y después los intérpretes del sistema, de modo que un
`1949 passed` **no** demuestra que la suite corra sobre un Python con tkinter
—solo que alguno lo tenía—. Es exactamente lo que pasa hoy en el contenedor de
desarrollo, donde el intérprete de la suite no tiene tkinter y el test corre
igual, en un subproceso, sobre `python3.12`.

Son **cuatro** configuraciones y no dos, porque PyMuPDF y tkinter son
independientes. **Las correcciones de T-8 (2026-11-12, integradas detrás de
T-5) sumaron SESENTA Y NUEVE tests**, uno con la marca `pdf` (abre el EG-2013,
que está en `normas/` de la app) y ninguno dependiente de Tk ni del
repositorio de normas: los 63 de `tests/test_t8_correcciones.py` —la
aceptación de la SEGUNDA auditoría adversarial de T-8 (H1 a H15) y de las seis
decisiones que el dueño del proyecto tomó sobre ella el mismo día (D1 a D6)—
y los seis anclajes de `test_decisiones_diferidas` para las fichas T8-07 a
T8-12, que cierran la Parte XLV antes de la de T-5. **Seis cosas cambian, y
conviene leerlas porque el párrafo de T-8 de abajo decía otra cosa y se
corrigió en su sitio:** (1) `regla_espesor_longitud_proteccion_salida` vale
`envolvente_hec14` y la envolvente alcanza a la PIEDRA: el d50 que rige es el
mayor del de Laushey —que se sigue calculando e imprimiendo,
`ProteccionSalida.d50_laushey`; `ProteccionSalida.d50` es desde aquí «el que
rige»— y del D50 de la Ec. (10.4), y el espesor y la longitud los mayores de
lo adoptado y de los de la Tabla 10.1 para esa piedra; donde HEC-14 no es
evaluable rige Laushey con lo adoptado y se avisa, y fuera de la Tabla 10.1 se
imprimen cotas inferiores (2.0·d50 y 8D) con el aviso de que hace falta un
disipador (ficha T8-07); `manual` queda barrible y reproduce exactamente los
números anteriores; (2) «sin enrocado» nunca es conclusión: la protección se
calcula y se mantiene SIEMPRE, el contraste con la Tabla Nº 11 informa si el
terreno la resistiría y suprimirla queda sujeto a inspección de campo (HDS-5
núm. 5.3.2), y con la velocidad tomada al tirante crítico —cota inferior de la
de borde: las Figuras 3.3 y 3.4 de HEC-14 no están digitalizadas, ficha
T8-08— el contraste NO concluye (veredicto INDICADOR,
`VelocidadAdmisible.concluyente`, que llega a `InformePunto.avisos()`);
(3) `duracion_caudal_pico_socavacion_min` pasa de [C] 30 min a [A] 360 min,
ventana 30–360 con 30 barrible y la cita literal de HEC-14 («2/3 to 3/4 of
the maximum scour depth», `HEC14.5.1.2#DOS_TERCIOS`): la fuente sostiene el
piso y la razón para no quedarse en él, y **el techo de 360 min es elección
del proyecto, no de HEC-14**, que no da duración máxima (la hoya de
`HoyaDeSocavacion` llama ahora `profundidad_alternativa` a la de la otra
punta de la ventana); (4) la nota (5) b de la Tabla 511-06 del EG-2013 vale
sólo en la columna «>50»: es la lectura que no relaja, declarada como
`Interpretacion` (`citas.INTERPRETACION_NOTA_5_T511_06`) y sostenida por la
Tabla 511-02 de la misma Sección, que numera las dos notas por separado, hasta
conseguir AASHTO M 288 (ficha T8-10); (5) el límite del apron es 60 in =
1.524 m (`HEC14_APRON_ALTURA_MAX_M`), la lectura que deja evaluable el ejemplo
resuelto de la propia fuente, y el CU vuelve a su escala real; (6) lo demás de
la auditoría: el Froude de HEC-14 no clasifica el régimen
(`fundamentos.FROUDE_SALIDA` y otros cuatro `F6.*` reescritos), tres
`Interpretacion` nuevas colgadas de HEC-14 10.2, del núm. 4.1.1.3.7 c) y de la
Tabla 511-06 que los pasos leen del registro, guardias de tipo en las entradas
de texto de M6 (H7), «recomienda» donde decía «manda» (H8), la cita de hs de
HEC-14 10.1 (H9), los mensajes y comentarios que decían lo contrario que el
código (H10), las tablas transcritas fijadas celda a celda (H13) y la banda de
régimen de M4 avisada desde M6 sin tocar M4 (ficha T8-09). Lo que la auditoría
pidió y no se hizo —techos físicos para los datos de la Fase 6— está refutado
con su razón en la ficha T8-11. **El rojo se escribió primero** con
`xfail(strict=True)`, y porque las decisiones del dueño llegaron a media
pasada y reescribieron H1, H2, H11 y D3 se REMIDIÓ con el archivo final sobre
`df1b23c`: 43 rojos y 20 verdes, que son guardias (ficha T8-12); la mutación
de M6 con el arnés de EXT-11 mata 536 de 574 (93.4 %), sumando una medida
entera y una parcial. Ningún archivo restó tests: `test_t8_proteccion` se
reescribió a la verdad nueva y sigue en 96 (declarado en su cabecera), y
`test_guardias_de_la_suite` gana una entrada en `TEXTUAL_CON_RAZON`. Ningún
censo cambia: 109 criterios, 34 sin valor, `CLAVES_EXTERNAS` dieciocho,
ninguna marca `literal-ok` nueva; las citas del registro pasan de 375 a
378. El tracker no cambia ningún estado: INF-3.3.7, INF-5.1.13 y MAT-X6
ganan una NOTA. **La línea base de la Familia C se regeneró sobre el árbol
fusionado y se midió contra `1522635` con el comparador de E-B, y es la
primera regeneración de la cadena T que mueve un número de la Fase 6, con la
aprobación del dueño**: 15 diferencias en el JSON ancho y 0 no comparables —el
espesor de A-01 y A-02 pasa de 0.592 y 0.479 m a 0.770 m (clase 4 de la Tabla
10.1: 2.2·0.35) y la longitud de 5.00 a 5.40 m (6·0.90); el d50 que rige NO se
mueve (0.338 y 0.274 m: rige Laushey, porque la Ec. 10.4 pide 0.252 y
0.104 m); las claves nuevas `d50_laushey_m` y `rige_la_envolvente`, la regla,
la tercera advertencia, el criterio entre los usados y la huella—, y sólo la
huella en los otros dos; las dos celdas de espesor y longitud del CSV ancho;
`cli_perfil.txt`, `cli_expediente.txt`, `cli_rama_error.txt`, el CSV de
expediente y la memoria del cajón no cambian un byte. El delta es el MISMO que
la rama midió contra `df1b23c` (comparado `diff` contra `diff`), y **ningún
diámetro ni material se movió**: A-01 y A-02 siguen en concreto de 0.90 m, y
la fila `F8.CLASE` de T-5 sigue en 37.42 y 37.04 N/m/mm. Los techos de
`test_ext8` se remidieron y no se mueven (70.3 KB y 20.3 páginas por punto a
expediente, iguales sobre `1522635`); la memoria de perfil, sin techo, pasa
de 101.4 a 102.6 KB por punto (el párrafo de la envolvente, el paso 6.6c y los
avisos). De las cuatro configuraciones se MIDIÓ UNA, «sí · no», con el
repositorio de normas enlazado: 5230 passed, 16 skipped, collected
5246 (y sin `NORMAS_DIR`, sobre el mismo árbol: 5212 passed, 34
skipped). **Las otras tres se dicen como derivadas, no como medidas**, por lo
mismo que en T-0: la derivación suma 69 a las de T-5 y pasa uno de ellos a
`skipped` en las dos columnas sin PyMuPDF.
**T-5 de la cadena T (2026-11-12, integrado detrás de T-8: el
primero del segundo lote) sumó DOSCIENTOS UN tests netos**, veintiocho con la
marca `pdf` y ninguno dependiente de Tk ni del repositorio de normas: los 105
de `tests/test_t5_estructural_conducto.py` y los 74 de
`tests/test_t5_correcciones_auditoria.py` —**la Fase 8 REAL del conducto**
(`src/modulos/M8_estructural.py`, INF-3.3.5): la carga de tierra sobre la
altura real de relleno más el paquete estructural y la carga viva HL-93 del
Manual de Puentes distribuida a través del relleno por AASHTO LRFD 3.6.1.2.6
[C], con el IM de componentes enterrados (`M8.carga_viva_enterrada`: GOBIERNA
EL VEHÍCULO DE MAYOR EFECTO sobre el conducto, que cada consumidor pasa en
`efecto=`, no el de mayor presión; fuera del dominio del método,
`MetodoNoEvaluableError` con `MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL`); el
tubo de concreto por el método indirecto de 12.10.4.3 contra la D-load de
0.3 mm de la clase de M 170M (`M8.verificar_concreto`); el TMC por 12.7.2
—empuje, área con pandeo, costura y factor de flexibilidad— con progresión
de plancha dentro de la corrugación adoptada y el mínimo de la Tabla 507-01
del EG-2013, y ASTM A796 solo como contraste por tensiones admisibles que no
rige (`M8.verificar_tmc`); el HDPE por 12.12 —empuje, pandeo general,
deflexión y factor de flexibilidad— (`M8.verificar_hdpe`); la demanda de la
losa superior del marco con el pórtico diferido (`M8.demanda_marco`); y el
relleno máximo de lo elegido, por el primer cruce del margen. **Lo que
decide si la combinación material / diámetro / plancha / clase EXISTE corre
también a nivel de perfil**, como filas `F8.*` de la tabla de la Fase 5
(`M5.fase_8_estructural`), detrás de V9 y solo si todo lo anterior cumple; a
perfil se difieren la cama de apoyo y la demanda del marco (ficha T5-01). La
mina `AssertionError` de `M8.seleccionar_clase_calibre` quedó retirada. **La
FASE A la auditaron dos auditores adversariales independientes (AJUSTADO los
dos) y el dueño del proyecto decidió el 2026-11-12 las siete preguntas que
dejaban abiertas; el cierre las aplicó, y conviene leerlas porque cuatro
contradicen lo que la FASE A había escrito:** (1) la instalación del tubo de
concreto es el Tipo 3 de archivo con `tipo_4` DENTRO de la ventana y el Tipo
4 impreso al lado como contraste (pasos `F8.TIPO4` y `F8.HMAX_TIPO4`); la
correspondencia del EG-2013 con el Tipo 3 es lectura del proyecto y tiene una
condición, dicha en la `Interpretacion` de la cita —los numerales del tubo de
concreto son 506.07, 506.10 y 506.11 → 502 → 205.12(c)(1), 95 % del Proctor
Modificado en el solado y la sujeción y 90 % en el relleno; el 508.07 que la
decisión citaba es del polietileno— (ficha T5-12); (2) las propiedades de
sección del HDPE son DATO DEL FABRICANTE (`perfil_hdpe_fabricante`, [A]
opcional sin valor por defecto): sin ellas el HDPE queda «no verificado con
un producto real» —`DatoFaltanteError` con la cota inferior del perfil mínimo
de la Tabla A12-11 en el mensaje, que AASHTO C12.12.3.2 declara «not
meaningful for design»— y NO se adopta; el relleno de archivo es `Si-95`, la
columna menos favorable de las que corresponden al material granular que el
EG-2013 508.02 d) exige, y no `Cl-95`, con el que el perfil mínimo no cumple
a ninguna altura (fichas T5-05 y T5-10); (3) `fabricacion_tmc` es la
remachada simple, la costura más débil TABULADA, y el resultado avisa siempre
que el EG-2013 507.02 a) describe tubería empernada; el caso G2 de la
auditoría de T-4 (TMC de 1.95 m con ~8.5 m de relleno) deja de dimensionarse
y su test se reescribió DECLARÁNDOLO, no en silencio como en la FASE A (ficha
T5-08); (4) la carga viva pasados 8.0 ft de relleno se CONSERVA: despreciarla
es el permiso de 3.6.1.2.6a y lo declara `carga_viva_bajo_relleno_alto` [A]
(ficha T5-11); (5) η_I = 1.05 no lo prescribe ninguna fuente para una
estructura enterrada: es la clasificación de importancia del Propietario, [A]
con la ventana del Manual de Puentes 2.3.2.5, y η_R = 1.00 por 12.5.4; (6) un
tubo de concreto que pide más que la Clase II —la única D-load legible del
ejemplar de M 170M— BLOQUEA el punto con el mensaje que nombra las clases que
faltan para ese diámetro, y el ejemplar legible va a la lista de entradas del
dueño (`docs/contrato_entradas.md`); la clase no se ofrece por debajo del
primer diámetro que la norma le tabula (ficha T5-02); (7) el pandeo general
del HDPE va con el módulo de la vida de diseño, como manda la letra de
12.12.3.3, con la suma por duración al lado y rigiendo la mayor (ficha
T5-13). **Y una regla de MD que sale de ahí:** un punto al que solo le falta
un dato no es «no factible» —cuando la Fase 8 detiene por dato faltante un
escalón que cumple toda la tabla, `MD.disenar_punto` relanza ese
`DatoFaltanteError`—; el HDPE es el último candidato de M2, de modo que su
dato no bloquea a ningún otro (regla T4-10). Los dorados
(`CP_FASE_8_ESTRUCTURAL` y `CP_FASE_8_CIERRE`) están calculados a mano en
unidades inglesas, con la aritmética escrita. **Ni los tests de la FASE A ni
los de las correcciones se escribieron en rojo primero**: los de las
correcciones se midieron contra la FASE A rebasada (`1768b45`) y 48 de 71
fallan allí —los 23 que valen antes y después son quince literales del PDF y
ocho guardias—; y veinticuatro mutantes dirigidos, los que las dos auditorías
habían dejado vivos, mueren todos (ficha T5-14). Los otros 22 netos: los
catorce anclajes de `test_decisiones_diferidas` para las fichas de la Parte
XLVI (T5-01..14); los siete que crecen solos en `test_ext5_forma_gui` con los
siete criterios nuevos (109 donde T-8 dejó 102; los sin valor bajan de 35 a
34, porque `clases_producto_por_relleno` deja de estar vacío y
`perfil_hdpe_fabricante` es opcional y no cuenta: los opcionales vuelven a
ser cuatro); dos en `test_t4_materiales_durabilidad` (el caso G2, que pasa de
un test a tres); y uno MENOS en `test_criterios_adoptados` (el caso de
`clases_producto_por_relleno` en el parametrizado de vacíos). Se reescribieron
al contrato nuevo `test_M8_estructural`, `test_cli`, `test_cierre_perfil` (la
fila `F8.CLASE` detrás de V9), `test_memoria_sustentada` (doce fundamentos
`F8.*` que la corrida por defecto no alcanza), `test_sin_literales`
(`src/modulos/M8_estructural.py`: 29), `test_normativa`,
`test_guardias_de_la_suite` y `test_t0_gobernanza`, que ganó la fila de T-5.
Cierra INF-3.3.5, con residuales declarados que dependen de entradas (las
clases ilegibles de M 170M, el perfil del fabricante del HDPE, la costura
empernada del TMC y el pórtico del marco). **La línea base de la Familia C se
regeneró sobre el árbol fusionado y se midió contra `df1b23c` con el
comparador de E-B**: 18 diferencias en el JSON ancho, todas de T-5 —la fila
`F8.CLASE` de A-01 y A-02 (37.42 y 37.04 frente a 50.0 N/m/mm), su bloque
`estructural` (Clase II, relleno máximo 2.851 m; 1.691 m con el Tipo 4), el
texto del diferimiento de la Fase 8, tres criterios usados, las huellas y los
recuentos— y 3 de huella y recuento en los otros dos; los dos CSV de resumen,
tres de los cuatro `cli_*.txt` y la memoria del cajón no cambian un byte, y
**ningún diámetro ni material se movió** (A-01 y A-02 siguen en concreto de
0.90 m). Los techos de `test_ext8` se remidieron y no se mueven (70.3 KB y
20.3 páginas por punto a expediente). De las cuatro configuraciones se MIDIÓ
UNA, «sí · no», con el repositorio de normas enlazado: 5161 passed, 16
skipped, collected 5177 (y sin `NORMAS_DIR`, sobre el mismo árbol: 5143
passed, 34 skipped). **Las otras tres se dicen como derivadas, no como
medidas**, por lo mismo que en T-0: la derivación suma 201 a las de T-8 y
pasa 28 de ellos a `skipped` en las dos columnas sin PyMuPDF.
**T-8 de la cadena T (2026-11-12, integrado detrás de T-6)
sumó CIENTO DIEZ tests**, ninguno con la marca `pdf` ni dependiente de Tk ni
del repositorio de normas: los 96 de `tests/test_t8_proteccion.py` —la Fase 6
de entrada y salida, con el d50 de Laushey del Manual (núm. 4.1.1.3.7 c)),
que T-8 dejó rigiendo sin moverse y que **desde sus correcciones rige dentro
de la ENVOLVENTE con HEC-14** (párrafo de arriba; lo que este párrafo dice
de T-8 y las correcciones cambiaron va corregido en su sitio):
`M6.proteccion_salida` lo contrasta con la velocidad máxima admisible del
terreno (Tabla Nº 11 del Manual, por `tipo_terreno_receptor` y
`regimen_flujo_descarga`) y dice si el terreno la resistiría —en T-8, si la
protección era «requerida»; desde las correcciones el contraste INFORMA, la
protección se mantiene siempre y «sin enrocado» no es conclusión—, y calcula
AL LADO el apron de HEC-14 Cap. 10 (`M6.apron_hec14`: Ec.
10.4 con el D' de la Ec. 10.5 y el TW acotado a 0.4D–1.0D, clase de la Tabla
10.1, ancho 3D + (2/3)L) y la clase de la piedra adoptada (paso 6.6b), con
aviso cuando lo adoptado queda corto y SIEMPRE que el espesor 1.75·d50 quede
bajo el piso de 2.0·D50 de HEC-14 —la decisión quedó preparada en
`regla_espesor_longitud_proteccion_salida` [A]; T-8 la dejó en `manual` con
`envolvente_hec14` barrible, y desde las correcciones es AL REVÉS:
`envolvente_hec14` de archivo, alcanzando también a la piedra, y `manual`
barrible—; el Froude de HEC-14 (`Fr_e` con `ye =
(A/2)^0.5`) es un parámetro de diseño y no un indicador de régimen, que sale
del tirante contra el crítico por UNA regla (`M6.flujo_supercritico`); el
filtro es un requisito declarado (Lámina Nº 05, HEC-14 núm. 10.2, EG-2013
núm. 511.08 con la Tabla 511-06 leída por fila y su nota (5) a; la (5) b, que
T-8 aplicaba a la fila, vale desde las correcciones sólo en la columna «>50»,
declarada como `Interpretacion`), no un dimensionado; la entrada (`M6.proteccion_entrada`, INF-5.1.13) publica la
velocidad en la boca de lo que M4 ya resolvió, la contrasta con la Tabla Nº
11 si se declara `tipo_terreno_entrada` y declara el revestimiento de
`tipo_proteccion_entrada` [A] y lo que se protege según la embocadura, sin
dimensiones porque ninguna fuente de `normas/` se las da (ficha T8-03); y la
socavación a la salida para el desplante (`M6.socavacion_salida`) es HEC-14
**Cap. 5** —no el 3, errata de la cadena—, Ec. 5.1 en no cohesivos y 5.2 a
5.4 en cohesivos con sus Tablas 5.1 a 5.4, la duración del pico declarada o
`duracion_caudal_pico_socavacion_min` —[C] de 30 min en T-8, el valor que la
fuente recomienda cuando no se conoce; desde las correcciones, [A] de 360 min
con ventana 30–360 y 30 barrible: a 30 min sólo se alcanza de 2/3 a 3/4 de
la socavación máxima, y el techo de 360 es elección del proyecto, no de
HEC-14—; una duración menor de 30 min se acota a 30 como cota superior,
porque los exponentes no valen por debajo; la lectura entre filas por
`lectura_coeficientes_socavacion_hec14` [A], la referencia de la profundidad
por `referencia_profundidad_socavacion` [A] y la cota del fondo de la hoya;
seis datos externos nuevos y opcionales entran por `--datos-externos`
(`servicio.CLAVES_EXTERNAS` tiene dieciocho), y sin ellos la fase lo avisa.
Los oráculos son los ejemplos resueltos de HEC-14 (el de las págs. 10-18 y
10-19, y el CU, que T-8 escaló a λ = 0.9 para caber en un límite de 1.50 m y
que desde las correcciones corre a su escala real con el de 60 in = 1.524 m)
y la aritmética escrita—; los seis anclajes de `test_decisiones_diferidas` para
las fichas de la Parte XLV (T8-01..06); los cinco que crecen solos en
`test_ext5_forma_gui` con los cinco criterios nuevos (102 donde T-6 dejó 97;
los sin valor siguen siendo 35); y los tres de `test_dimensional_piloto` con
`HEC14_TAU_C_ALFA_U_SI` en su censo. **No se escribieron en rojo primero**:
el prompt se retomó a medias con el código escrito, y el rojo se midió contra
`ad5cb97` (ficha T8-06); la mutación de M6 con el arnés de EXT-11, sobre el
módulo final, mata 472 de 514 mutantes (91.8 %) y los 42 vivos están
clasificados en esa ficha. El auditor adversarial dejó diez correcciones, entre
ellas el aviso de la duración adoptada por criterio con su sensibilidad, una
sola regla de régimen, un IP fuera de 5–16 que avisa y no bloquea, la salida
sin enrocado avisada con el literal de HDS-5 núm. 5.3.2 («…is typically a
standard practice unless…») y
su `Interpretacion` en vez de un verbo de obligación (desde las correcciones
el mismo literal acompaña al aviso de que la protección se MANTIENE y
suprimirla queda sujeto a inspección de campo), el límite de la nota 8 de la
Tabla 1.1 (1.50 m en T-8; 1.524 m desde las correcciones), el tirante de borde (HEC-14 núm. 3.1.3), el terreno
declarado contra el lecho y el rótulo `MOTIVO_METODO_NO_EVALUABLE_HEC14`.
Ningún archivo restó tests; se reescribieron `test_t0_gobernanza` (HEC-14
pasa de «sin citas» a citada y firmada por T-8, y la fila de T-8 en
`LO_QUE_ESCRIBIO_CADA_PROMPT`), `test_t2_hidraulica` (los avisos sin los de
geometría ni los de la Fase 6), `test_ayuda_entrada` (catorce externos que no
son columna), `test_memoria_sustentada` (las tres piezas de la Fase 6 y nueve
fundamentos `F6.*` que la corrida por defecto no alcanza), `test_normativa`
(el prefijo `HEC`) y `test_sin_literales` (`src/dominios.py`: 11, por
`PORCENTAJE_POR_UNIDAD`). Cierra INF-3.3.7 e INF-5.1.13, y deja una nota en
MAT-X6: su premisa, «HEC-14 no está en normas/», ya no se sostiene, y con
HEC-14 la contradicción numérica sí se ve (en A-01, 0.592 m de espesor contra
0.770 m de profundidad del apron de clase 4; las correcciones la resuelven
por la envolvente). **La línea base de la Familia C
se regeneró por FORMATO** sobre el árbol fusionado y se midió contra
`7e74065` con el comparador de E-B: los bloques nuevos de la Fase 6, los
textos de dos advertencias, los avisos de la fase, los criterios usados, las
huellas y el recuento «97 / 35» → «102 / 35»; el bloque `diseno` de los
cuatro puntos es idéntico, los cuatro `cli_*.txt` salvo el ancho, los dos CSV
de resumen y la memoria del cajón no cambian un byte, **ningún diámetro se
movió** y en T-8 los números de Laushey tampoco (d50 0.338 y 0.274 m, espesor
0.592 y 0.479 m, longitud 5.00 m); las correcciones movieron el espesor a
0.770 m y la longitud a 5.40 m en los dos puntos, con el d50 sin mover. De las cuatro configuraciones se MIDIÓ UNA,
«sí · no», con el repositorio de normas enlazado: 4960 passed, 16 skipped,
collected 4976 (y sin `NORMAS_DIR`, sobre el mismo árbol: 4942 passed, 34 skipped). **Las
otras tres se dicen como derivadas, no como medidas**, por lo mismo que en
T-0: la derivación suma 110 a las de T-6, y ninguno pasa a `skipped`.
**T-6 de la cadena T (2026-11-11, integrado el 12 detrás de
T-2, T-4 y T-1: el último del primer lote) sumó CIENTO TREINTA Y OCHO
tests**, ninguno con la marca `pdf` ni dependiente de Tk: los 131 de
`tests/test_t6_geometria.py` —la geometría de la Sec. 7.B, por los cinco
puntos de su prompt: (1) `cota_fondo_entrada` medida gana, y cuando falta
la adopción deja de ser muda: `CotaDeEntrada.aviso` («fondo de entrada
adoptado igual al terreno de plataforma: medir en el cauce») y
`TamizadoRasante.provisional`, que marca el delta de rasante de 7.A; (2) la
longitud **por extremo** —criterio [A] `metodo_longitud_conducto`, con
`terraplen_simetrico`, la fórmula anterior, conservada como caso
particular—: `L = [ancho + talud·(H_e + H_s0)] / [cos θ − talud·S]`, con la
salida `S·L` más baja y `bombeo` o `peralte` como datos externos opcionales
y **excluyentes** (DG-2018 núm. 304.05 y 304.06), cuya ausencia se avisa con
su sensibilidad; el HDS-5 (núm. 2.2.4 b. y Figura 2.4, pág. impresa 2.8)
sostiene la superposición aproximada del barril, y medir al **fondo** es
elección del proyecto —cota superior de la longitud, no el lado seguro por
construcción—, de modo que la longitud entre cabezales a la clave se imprime
como encaje (núm. 3.3.5) sin sustituir a la del diseño; y 7.B deja de ser
una frase: pasos 7.B.1 a 7.B.5 con fórmula sustituida, más los de G2 y G3;
(3) G2 con `desnivel_minimo_entrega_m` [A] (0.0 m, ventana 0.0–0.30:
ninguna fuente da la cifra, y el umbral lo dice); (4) `esviaje_max_grados`
con valor (45°, ventana 45–60, por analogía con el esviaje de embocadura
del HDS-5 núm. 5.4.2) y como **aviso** —la verificación G3, con veredicto
INDICADOR— en vez del `DatoInvalidoError` del cierre de C10; (5)
`M7.pendiente_adoptada`, que resuelve la pendiente UNA vez antes de la Fase
4 y la deja con su origen (`OrigenPendiente`: cauce, declarada, mínima o
máxima). El dorado `CP_T6_LONGITUD_POR_EXTREMO` está calculado a mano—; los
cinco anclajes de `test_decisiones_diferidas` para las fichas de la Parte
XLIV (T6-01..05); y los dos que crecen solos en `test_ext5_forma_gui` con
los dos criterios nuevos (97 donde T-1 dejó 95; los «todavía sin valor»
que la memoria cuenta siguen siendo 35, porque `esviaje_max_grados` era
opcional y no contaba entre ellos: recibe valor y los opcionales quedan en
tres). **La aceptación se midió
en rojo contra `87d1ce7`** antes de darla por tal (y los diez ítems del
cierre, contra los commits `wip(T-6)`), y el auditor adversarial
dejó nueve correcciones (bombeo y peralte excluyentes, la atribución a la
fuente de lo que es elección del proyecto, «cota superior» donde decía
inferior, el sesgo del eje con el fondo adoptado, la guardia del esviaje
negativo, el dorado a mano, el umbral de G2 citando la Lámina Nº 01). **Cuatro
cosas de la integración, que es donde T-6 toca a los otros tres:** (a) **el
reparto con V10** —`M7.pendiente_adoptada` lee la banda con la lectura
única de T-2, `M5.limites_de_pendiente()`, y acota sólo la pendiente del
**cauce**; V10 juzga la que quedó y sólo se incumple con una pendiente
**declarada**. Acotar no resuelve la obra y se avisa
(`M7.aviso_de_pendiente`): con la máxima, el desnivel `(S_cauce − S)·L`
pide una estructura de caída o de disipación que el programa no dimensiona
y V2b lo juzga según `regimen_v2b` (con `indicador_con_aviso` el punto
dimensiona con el indicador; con `umbral_duro` no dimensiona y el motivo
nombra V2b); con la mínima, la salida queda bajo el cauce natural y la
juzga G2. Una pendiente de cauce no finita o no positiva no se sustituye
por un extremo: es `DatoInvalidoError` (un NaN es falso frente a `>=` y
salía con origen «mínima»)—; (b) **los avisos de 7.B salen por
`InformePunto.avisos()`, una vez** (`avisos_de_geometria`: fondo adoptado,
pendiente en un extremo, plataforma horizontal, transversal descartada), y
los lleva también el punto que no dimensiona, porque su longitud ya entró
al diseño de cada escalón; G3 no va en esa lista: es un INDICADOR y sale
por `con_aviso` como V2b, de modo que cuenta en `ResumenDeCorrida.con_aviso`;
(c) `servicio.CLAVES_EXTERNAS` tiene doce claves, `CLAVES_QUE_ADMITEN_CERO`
suma `bombeo` y `peralte` y `CLAVES_CON_SIGNO` nombra la única con signo;
(d) lo que dejó el cierre de la integración: la banda vacía de
`M5.limites_de_pendiente`, que `M7.pendiente_adoptada` lee FUERA de
`_etapa`, salía de `correr_punto` y tumbaba la corrida —es un bloqueo del
punto en `servicio.ETAPA_PENDIENTE`, como cuando la levantaba V10 dentro
de MD—; el aviso de fondo adoptado del punto que no dimensiona sale de la
cota de entrada (`InformePunto.cota_entrada`) y no de la longitud, que con
el método simétrico o la longitud declarada no lo llevaba; G3 tiene segunda
línea sobre su máximo; y las fichas de `pendiente_minima_conducto` y
`pendiente_maxima_conducto` dicen el reparto con M7 (decían «la aplica
V10»).
Ningún archivo restó tests; se reescribieron `test_M7_geometria`,
`test_cierre_c10` (PC-32 pasa de bloqueo a aviso), `test_cierre_perfil`
(la longitud de A-01 a mano, 18.869 m; `G3` en la lista de códigos),
`test_criterios_adoptados`, `test_nivel_medido`, `test_ayuda_entrada`,
`test_memoria_sustentada` (siete fundamentos `F7.*`), `test_pf2_prevuelo`,
`test_t2_hidraulica` (los dos tests que fijaban la tupla entera de avisos
la fijan sin los de geometría), `test_pf1_hw_fuera_de_rango` (el caso patrón de
0.40 m/m declara su pendiente: la del cauce ya no llega al diseño fuera de
la banda), `test_ext8` (techos remedidos: 70.3 KB y 20.7 páginas por punto
donde `5bca7c6` medía 63.7 y 18.7; quedan pegados a la medida, 71 y 21, y
los reconcilia T-10) y `test_t0_gobernanza`, que ganó la fila de T-6 y le
pasó INF-3.2.7. Cierra INF-5.1.18, INF-3.3.3 e INF-3.2.7 (que T-2 había
dejado en parte), y enmienda PC-32 / C10-03. **La línea base de la Familia C
se regeneró y T-6 SÍ mueve números, todos declarados en su README**: la
longitud de los cuatro puntos (A-01 18.6350 → 18.8694 m; A-02 18.2695 →
18.5677; B-01 18.4000 → 18.7755; C-01 21.2465 → 21.4446) y lo que cuelga de
ella —caída, cota de salida y HW de **salida** de A-01 y A-02 (0.9929 →
0.9925 y 0.5618 → 0.5596 m; el HW que gobierna, de entrada, no cambia), y
el TW de la vía 4 en la corrida estrecha—; el bloqueo de C-01 en esa
corrida cambia de etapa («longitud del conducto (7.B)» en vez del TW) con
la misma causa. Medido contra `5bca7c6` con el comparador de E-B en los
tres JSON y en los doce pares punto × corrida: material, sección, control,
veredicto y admisible de cada verificación, iteraciones y tipo de cada
bloqueo son idénticos, y **ningún diámetro se movió** (A-01 y A-02 siguen
en Ø 0.90 m). De las cuatro configuraciones se MIDIÓ UNA, «sí · no», con el
repositorio de normas enlazado: 4850 passed, 16 skipped, collected 4866 (y
sin `NORMAS_DIR`, sobre el mismo árbol: 4832 passed, 34 skipped). **Las
otras tres se dicen como derivadas, no como medidas**, por lo mismo que en
T-0: la derivación suma 138 a las de T-1, y ninguno pasa a `skipped`.
**T-1 de la cadena T (2026-11-11, integrado el 12 detrás de T-2 y T-4) sumó
CIENTO NOVENTA Y UN tests**, veinte con la marca `pdf` y ninguno dependiente
de Tk: los 113 de `tests/test_t1_hidrologia.py` y los 59 de
`tests/test_MH_hidrologia.py` —la hidrología DENTRO del programa: el módulo
nuevo `src/modulos/MH_hidrologia.py` (Fase 1-bis, importado sólo por
`servicio.py`, con un test que lo fija por AST) calcula el caudal de un punto
de Familia A o B por el método racional (`Q = 0.278·C·I·A`, Manual de
Hidrología núm. 3.12.2, ec. 28, con «A<10 Km2» estricto) a partir de dos
entradas opcionales que van juntas, `--cuencas` y `--estacion`, y deja
**nueve pasos de memoria** con su cita (1b.1 a 1b.8 y 1b.3b); la precedencia
no cambia —`Q_m3s` en `--datos-externos`, la columna `Q_m3s` llena, y sólo
con la celda vacía el cálculo— y un caudal declarado se imprime como «Q
declarado por el estudio hidrológico» con su contraste Q/A (paso 1b.8, sin
umbral: el núm. 3.13 no pone uno); el tiempo de concentración lo declara cada
fila del CSV de cuencas entre CUATRO filas de la Tabla Nº 05 (Kirpich,
California, FAA y retardo SCS; la tabla está entera en el registro e Izzard
y onda cinemática quedan diferidas) y Témez, que **no es fila de esa tabla**
sino la ec. (30) del núm. 3.12.2.1; la lluvia de diseño sale del ajuste de la
serie P24 con las tres distribuciones de las que el Manual imprime el
estimador (Normal, Log Normal 2P, Gumbel) y Kolmogorov–Smirnov, y la
intensidad de Dick y Peschke o de la Tabla Nº 04;
`homogeneidad_serie_fen` tiene **consumidor real** y es una categoría de
tres tratamientos sin valor de archivo: sin declararlo el caudal calculado
se detiene, y un caudal declarado nunca recibe `tratamiento_fen`. La
auditoría adversarial dejó trece correcciones (H1 a H13), entre ellas: la
lluvia de diseño que queda por debajo de un año ya registrado se contrasta
con la probabilidad observada de la ec. (13) y se avisa (paso 1b.2; cita
`MC_HHD.3.12.5#PIURA`); una celda `fen` vacía no es un «no»; `S_terreno` es
columna obligatoria y la Tabla Nº 08 no se lee nunca con la pendiente del
cauce; la población de la que salió cada fórmula de tc es DESCRIPCIÓN de la
tabla y lo que se hace fuera lo decide `tc_fuera_de_la_poblacion_del_metodo`
[A], con el mismo trato para Kirpich y California; la duración de la lluvia
no baja de `duracion_minima_lluvia_min` [C] (5 min, WSDOT núm. 2-6.3); con
Témez el caudal lleva el coeficiente de uniformidad K por
`coeficiente_uniformidad_temez` [A] (uso híbrido declarado); una superficie
de la plataforma vial toma su C de `coeficiente_escorrentia_superficie_vial`
[C] (WSDOT Table 2-2), nunca de una fila de la Tabla Nº 08 puesta por
omisión; `area_ha` y `area_km2` de la misma cuenca tienen que decir lo
mismo; y **la regla de la hoja de ruta se restauró y es dura** —«reportar el
ajuste con y sin ellos, adoptar el más conservador»: `serie_sin_fen` con
menos lluvia que la serie completa DETIENE el cálculo hidrológico del punto,
por decisión del dueño (ficha T1-09)—. Los dorados (`CP13_HIDROLOGIA`) están
calculados a mano, porque el Manual no trae ejemplo numérico, y los datos de
`tests/fixtures/hidrologia/` son sintéticos y lo dicen en su primera línea—;
los nueve anclajes de `test_decisiones_diferidas` para las fichas de la Parte
XLIII (T1-01..09); los siete que crecen solos en `test_ext5_forma_gui` con
los siete criterios nuevos (95 donde T-4 dejó 88, y los sin valor siguen
siendo 35); y los tres de `test_dimensional_piloto` con
`RACIONAL_COEFICIENTE_SI` en su censo. **No se escribieron en rojo
primero**: el archivo de aceptación lo dice y midió el rojo sobre `87d1ce7`
(105 xfailed y 14 XPASS de 119). Ningún archivo restó tests; se reescribieron
`test_t2_hidraulica` (dos tests que decían «sin avisos» dicen «sin más aviso
que el del caudal declarado»), `test_cierre_perfil`, `test_nivel_medido`
(`homogeneidad_serie_fen` sale de `SIN_CONSUMIDOR_Y_SIN_MEDIDA`),
`test_memoria_sustentada` (ocho fundamentos `FH.*` que sólo se emiten con el
caudal calculado), `test_sin_literales` (`src/dominios.py`: 10),
`test_normativa`, `test_traza_punto` y `test_t0_gobernanza`, que ganó la
fila de T-1 en `LO_QUE_ESCRIBIO_CADA_PROMPT`. Tres cosas de la integración
con T-2: los avisos de la Fase 1-bis salen por `InformePunto.avisos()` con
los demás del punto, una sola vez; todo punto de Familia A o B con el caudal
declarado lleva ahí un aviso PERMANENTE (el criterio FEN no lo alcanza); y un
paso de la Fase 1-bis con veredicto INDICADOR cuenta en
`ResumenDeCorrida.con_aviso` junto a las verificaciones
(`InformePunto.indicadores_de_hidrologia`). Cierra INF-3.1.2, INF-3.1.3,
INF-3.1.5, INF-3.1.6, INF-5.2.5 e INF-5.1.3, y en parte INF-3.1.1 (la
delimitación de la cuenca es una entrada) e INF-3.1.4 (quién fija R y n
sigue siendo del Propietario). La línea base de la Familia C se regeneró
sobre el árbol fusionado y se midió contra `7fb7926` en los doce pares punto
× corrida: material, sección, código, estado, veredicto, valor obtenido y
admisible de cada verificación, tipo de cada bloqueo, iteraciones,
durabilidad y periodo de retorno son idénticos; cambian la línea «Fase 1b Q
declarado…», el aviso permanente, la clave `caudal`, el origen del caudal en
la clasificación, tres entradas de `verificacion_pendiente`, las huellas y
el recuento de criterios; los dos CSV de resumen y la memoria del cajón no
cambian un byte, y **ningún diámetro se movió**. De las cuatro
configuraciones se MIDIÓ UNA, «sí · no», con el repositorio de normas
enlazado: 4712 passed, 16 skipped, collected 4728 (y sin `NORMAS_DIR`, sobre
el mismo árbol: 4694 passed, 34 skipped). **Las otras tres se dicen como
derivadas, no como medidas**, por lo mismo que en T-0: la derivación suma
191 a las de T-4 y pasa 20 de ellos a `skipped` en las dos columnas sin
PyMuPDF. **T-4 de la cadena T (2026-11-11, integrado el 12 detrás de
T-2) sumó CIENTO TREINTA Y UN tests netos**, quince con la marca `pdf` y
ninguno dependiente de Tk: los 115 de
`tests/test_t4_materiales_durabilidad.py` —la aceptación de material,
durabilidad y topes: el espesor de pared del TMC derivado de la corrugación
y la plancha adoptadas (`corrugacion_y_espesor_tmc` [A]: 13 + 2.01 mm, M 36
Table 1 y núm. 8.1.1) y el del HDPE del diámetro exterior máximo de AASHTO
LRFD Table A12-11, con 7.A y V7 recalculados a mano sobre A-01 y B-01; el
tope de diámetro por norma de producto (`D_max_norma_producto` [C]: 2.70 /
3.60 / 1.50 m, y en concreto el último DISEÑO ESTÁNDAR de M 170M, no la
última fila de su serie), la corrugación como tope del TMC y
`D_max_catalogo` [A] opcional que sólo baja; `v_max_tmc` [A] con ventana
(3.048, 4.572) y `v_max_hdpe` [C] citado del §8-3.3 de WSDOT; el n del HDPE
[C] de HDS-5 Table B.1; la matriz de durabilidad como filtro real de
`M2.materiales_candidatos` con seis ensayos opcionales que entran por
`--datos-externos` (`servicio.CLAVES_DE_DURABILIDAD`, fuera de
`CLAVES_EXTERNAS` para que el pre-vuelo no los anuncie como faltas) y que
sin ensayos imprime «durabilidad: sin ensayos, matriz no aplicada»; el aviso
de marco leído de `sucs_fundacion` contra `sucs_fundacion_deficiente` [A]; y
las correcciones del auditor adversarial (H1 a H11), entre ellas que
`MD.disenar_punto` no acepta un candidato si uno ANTERIOR quedó sin evaluar
por un dato que falta —lo que invierte el «caso mixto» que EXT-1 había
dejado sin cambio en PC-28, ficha T4-10—, los criterios electroquímicos de
AASHTO LRFD para acero galvanizado enterrado aplicados por analogía
(`suelo_agresivo_acero_lrfd` [C]) con efecto declarado
(`suelo_agresivo_lrfd_sobre_tmc` [A] = `aviso` | `excluye`), EG-2013 507.10
aplicada entera y el aviso fijo del Manual para la TMC candidata—; los diez
anclajes de `test_decisiones_diferidas` para las fichas de la Parte XLII
(T4-01..10); y los seis que crecen solos en `test_ext5_forma_gui` con los
seis criterios nuevos (88 donde T-2 dejó 82). No se
escribieron en rojo primero: el registro y las fichas fueron antes, y el
archivo lo dice. Ningún archivo restó tests; se reescribieron al contrato
nuevo `test_M2_material`, `test_M3_hidraulica`, `test_M5_verificaciones`,
`test_MD`, `test_criterios_adoptados`, `test_declaracion`,
`test_ext11_propiedades`, `test_pf3_barrido`, `test_cierre_c05`,
`test_guardias_de_la_suite`, `test_memoria_sustentada`, `test_sin_literales`
(`src/dominios.py`: 8), `test_normativa` y `test_ext1_entradas` (el caso
mixto de PC-28), y `test_t0_gobernanza` ganó la fila de T-4 en
`LO_QUE_ESCRIBIO_CADA_PROMPT`. Cierra INF-5.1.17, INF-3.3.4, INF-3.3.1,
INF-3.2.4, INF-5.1.9 e INF-5.1.16, y en parte INF-3.2.1 (sólo el HDPE). La
línea base de la Familia C se regeneró sobre el árbol fusionado y se midió
contra `ad5cb97` en los doce pares punto × corrida: material, sección,
código, estado, veredicto, valor obtenido y admisible de cada verificación y
tipo de cada bloqueo son idénticos; cambian la lista de materiales EVALUADOS
(B-01 de la corrida ancha pasa de 10 a 21 escalones), el texto de los
motivos, el criterio que V9 cita, las líneas y el bloque de durabilidad, los
criterios usados y las huellas; los dos CSV de resumen y la memoria del
cajón no cambian un byte, y **ningún diámetro se movió**. De las cuatro
configuraciones se MIDIÓ UNA, «sí · no», con el repositorio de normas
enlazado: 4521 passed, 16 skipped, collected 4537 (y sin `NORMAS_DIR`, sobre
el mismo árbol: 4509 passed, 28 skipped). **Las otras tres se dicen como
derivadas, no como medidas**, por lo mismo que en T-0: el contenedor no
tiene `tkinter` y desinstalar PyMuPDF apagaría la verificación normativa de
la sesión; la derivación suma 131 a las de T-2 y pasa 15 de ellos a
`skipped` en las dos columnas sin PyMuPDF. **T-2 de la cadena T (2026-11-11) sumó CIENTO SETENTA Y UN
tests netos** (173 nuevos y dos casos parametrizados que desaparecen), y
uno solo lleva la marca `pdf`; ninguno depende de Tk: los 160 de
`tests/test_t2_hidraulica.py` —la aceptación de los cierres de método de la
hidráulica: el barril horizontal (`S = 0` en M3 y M4, HDS-5 num. 3.3.4;
`modelos.SinTiranteNormal`, perfil `H2`, V1/V2 sobre el perfil y V3/d50
sobre la velocidad de salida, también con el control de entrada
gobernando), la banda de pendiente y V10 (`M5.v10_pendiente_conducto`,
evaluada detrás de V4b para que V5 y V8 no la tapen en el alcance de
expediente), el borde libre cuando lo toma el nivel del receptor
(`borde_libre_bajo_tw_ahogante`, con la monotonía de la lectura «aviso» a
lo largo del TW medida con seis TW y dos diámetros), la sección medida del
receptor con su validación de forma y de dominio, las 26 filas de la Tabla
A.1 valor a valor, el ejemplo publicado de HDS-5 (`CP_HDS5_DG1`: tolerancia
de lectura del 3 %, cinco casillas fuera censadas con su causa, las dos
filas de metal corrugado por intervalo con el n acotado por la Tabla B.1, y
ninguna fila en la transición), los indicadores que suben a los avisos y al
RESUMEN, el receptor seco y los diámetros de la línea base leídos del
archivo comprometido—; los siete anclajes de `test_decisiones_diferidas`
para las fichas de la Parte XLI (T2-01..07); los tres que crecen solos en
`test_ext5_forma_gui` con los tres criterios nuevos (79 → 82); uno en
`test_M3_hidraulica` y uno en `test_M4_control` (la pendiente NaN junto a la
negativa); y uno en `test_pf4_regimen_v2b` (C-01 sin declarar el régimen).
Los dos que desaparecen: el caso de `hw_entrada_fuera_de_rango` en el
parametrizado de vacíos de `test_criterios_adoptados` y su ejemplo de
`--declarar` en `test_guia_perfil`, porque el criterio ya tiene valor de
archivo. **Estos tests no se escribieron en rojo antes del código**: se
midieron después contra un árbol exportado de `87d1ce7` —126 rojos y 34
verdes, que son guardias que valen antes y después— y la mutación de lo
tocado se midió con el arnés de EXT-11 (283 mutantes, 28 vivos, censados
uno a uno en `MUTANTES_VIVOS_DE_T2`; ficha T2-07). Se reescribieron al contrato nuevo, sin
sumar ni restar, `test_M5_verificaciones` (doce filas y doce funciones;
V10 entre V4b y el hueco de V5), `test_cierre_perfil`, `test_cli`,
`test_ayuda_entrada`, `test_ea_perfil_lamina` (el perfil `H2`),
`test_ext11_mutacion` (dos claves del censo cambian de texto),
`test_ext11_propiedades` (el receptor seco), `test_memoria_sustentada` (dos
fundamentos que la corrida por defecto no alcanza), `test_dimensional_piloto`
(la relación de V10, que la corrida de referencia ya alcanza), `test_ext8`
(el techo de tamaño por punto, remedido: 60.8 KB), `test_sin_literales` (la
marca nueva de `dominios.py`), `test_pf1_hw_fuera_de_
rango` y `test_pf4_regimen_v2b` (los dos criterios con valor de archivo; el
caso patrón de PF-1, con S = 0.40, abre el techo de V10 para seguir midiendo
el piso), `test_seccion_rectangular` (quince cartas de cajón de Forma 2,
con el mínimo y el máximo sin mover) y `test_t0_gobernanza`, cuya tabla de
lo que cada prompt escribe en el tracker deja de fijar «cerrados == los de
T-0» y crece con cada integración. Cierra INF-5.1.6 e INF-5.1.7; en parte
INF-3.2.2, INF-3.2.6, INF-3.2.7 e INF-3.2.8; INF-3.2.5 por verificación
contra el PDF, sin tocar V4; e INF-3.2.9 queda diferido con ficha. Dos
valores de archivo cambian —`regimen_v2b` a `indicador_con_aviso` y
`hw_entrada_fuera_de_rango` a `energia_critica`— y los dos siguen siendo
[A]; `borde_libre_bajo_tw_ahogante` queda en `no_cumple` por decisión del
dueño, con «aviso» como alternativa barrible. La línea base de la Familia C
se regeneró por FORMATO, clasificado diferencia a diferencia con el
comparador de E-B (README de la línea base): la fila V10, los avisos, la
línea «Verificaciones con aviso» del RESUMEN, las huellas y los recuentos;
los dos CSV de resumen no cambian un byte y **ningún diámetro se movió**
(diez corridas medidas antes y después). De las cuatro configuraciones se
MIDIÓ UNA, «sí · no», sobre `origin/main` en el commit `tesis(T-2)`, con el
repositorio de normas enlazado: 4390 passed, 16 skipped, collected 4406 (y
sin `NORMAS_DIR`, sobre el mismo árbol: 4383 passed, 23 skipped). Las otras
tres se dicen como **derivadas**, por la misma razón que en T-0 —el
contenedor no tiene `tkinter` y no se puede instalar—: de los 171, uno
lleva la marca `pdf` (40 saltos sin PyMuPDF donde eran 39) y ninguno
depende de Tk (siguen siendo 13).
**T-0 de la cadena T (2026-11-11) sumó CINCUENTA Y SIETE
tests netos** (58 nuevos y uno retirado de un censo), sobre un árbol que ya
llevaba TRES que esta tabla no contaba: el orquestador de la cadena midió
`c2262a2` en «sí · no» y dio 4162 passed, 16 skipped, collected **4178**,
contra los 4175 que aquí se leían. El clon tiene un solo commit y los tres
no se pueden atribuir por historial; `c2262a2` es el cuarto bloque del
rediseño visual de la GUI, que sumó al menos el anclaje de la ficha
REDISEÑO-3-01 en `test_decisiones_diferidas`, y ninguno de los tres depende
de PyMuPDF ni de Tk (los 16 saltos de «sí · no» son los mismos). Los 58 de
T-0: los 53 de `tests/test_t0_gobernanza.py` —la aceptación de la
gobernanza de la cadena T, escrita primero en rojo con `xfail(strict=True)`
de módulo (medidos 50 xfailed y 3 XPASS antes de tocar nada; los tres valen
antes y después) y liberada al corregir: las 64 filas `INF-` del tracker con
el número del INFORME como ID canónico y cada alias de la cadena llevando a
una sola fila; la hoja de ruta v8 titulada v8, con el encabezado del CSV de
`M0_carga.COLUMNAS` y las claves de Manning y las dos gravedades del Anexo B
comparadas por AST con el código; los docstrings de M1, M4, M5, MD y M11 que
dejaron de afirmar lo que el código no hace (`_lo_que_afirma` descuenta lo
que el docstring cita entre «»: la casa no borra la frase que corrige); el
código de paso `F4.YC` con `F4.YC_RECT` como alias y las dos citas nuevas de
HDS-5; el contrato de entradas, que nombra cada columna, cada dato externo y
cada [S]; `NORMAS_DIR` con su caída y su error; HEC-14 y WSDOT como fuente
presente con la paginación que predice sus páginas; y la huella de la copia
de la cadena—, el de `test_ext6_registro_normativo` que mira el repositorio
de normas enlazado (la mitad de PC-23 que T-0 abre) y los cuatro anclajes de
`test_decisiones_diferidas` para las fichas de la Parte XL (T0-01..04). El
retirado: `M11_reporte.bloque_umbrales` sale del censo
`PUBLICAS_SIN_REFERENCIA_EN_TESTS`, porque un test ya la nombra. Ningún
archivo más sumó ni restó: `test_seccion_rectangular`, `test_M4_control`,
`test_ext2`, `test_dimensional_piloto` y `test_indice_formulas` cambian el
literal `F4.YC_RECT` por `F4.YC`; `test_normativa_pdf` y `test_ext6` buscan
los PDF por `fuentes.ruta_pdf`; `test_vigencia_fuentes` y `test_ext6`
admiten la tercera fecha de verificación; `test_ext11_cruce_temarios` espera
367 filas. Cierra INF-5.1.1, INF-5.1.2, INF-5.1.4, INF-5.1.10, INF-5.1.11 e
INF-5.1.14. La línea base de la Familia C se regeneró por FORMATO,
clasificado diferencia a diferencia (README de la línea base): las dos
huellas, «(v7)» → «(v8)», el código de paso y su ancla, las dos
procedencias de fórmula, las dos citas nuevas en el anexo y los textos de
`v_max_tmc` / `v_max_hdpe`; los cuatro `cli_*.txt` y los dos CSV de resumen
no cambian un byte, los tres JSON sólo en `criterios_sha1`, y **ningún
diámetro se movió**. De las cuatro configuraciones se MIDIÓ UNA, «sí · no»,
sobre `origin/main` en el commit `tesis(T-0)`, con el repositorio de normas
enlazado: 4219 passed, 16 skipped, collected 4235 (y sin `NORMAS_DIR`, sobre
el mismo árbol: 4212 passed, 23 skipped). **Las otras tres NO se pudieron
medir en el contenedor de T-0 y se dicen como derivadas, no como medidas**:
no tiene `tkinter` en ninguno de sus cuatro intérpretes (medido:
`python3`, 3.11, 3.12 y 3.13 dan `ModuleNotFoundError`) y `apt-get install
python3-tk` devuelve 503 según lo midió la sesión orquestadora de la cadena
(el espejo de paquetes no responde desde esa red), de modo que las dos
columnas «Ventana Tk = sí» no se pueden levantar; y las dos
«PyMuPDF = no» exigen desinstalarlo, que en un contenedor que no puede
reinstalar con garantía es apagar la mitad de la verificación normativa de
la sesión. La derivación: de los 58, cuatro llevan la marca `pdf` (39 saltos
sin PyMuPDF donde eran 35) y ninguno depende de Tk (siguen siendo 13).
**El cierre de los hallazgos abiertos (2026-09-22: C10,
C05, C09, C11 y C14, cinco commits `cierre(...)` de `67d5810` a `19bcf5a`)
sumó SESENTA tests netos**, y sólo uno depende de Tk: los 16 de
`tests/test_cierre_c10.py` —C5-02 (la fila del ke recuperada por
`M4._fila_del_ke_numerico`, rótulos sólo si el número es la celda, una fila
«Box» rechazada para el tubo), PC-27 (`modelos.EstadoDeVerificacion` como
fuente única con `cumple` y el veredicto del paso como vistas comprobadas,
NO_APLICA con productor real en V5 de la Familia C, la marca en M11, la
traza y la CLI de texto) y PC-32 (`esviaje_max_grados`, [A] opcional de
perfil leído por `M7.factor_esviaje`), escritos en rojo con `xfail(strict=True)`
—12 xfailed, 2 XPASS invariantes— y liberados, más los que dejó el auditor
adversarial (el hueco censado impreso encima de la fila «no aplica», la CLI
que decía `[OK]`, el mutante de la frontera del esviaje)—; los 17 de
`tests/test_cierre_c05.py` —PC-24 (`borde_libre_y_sobre_d_max` y
`velocidad_minima_autolimpieza_m_s`, [A] de perfil con el valor recomendado
por defecto, sólo endurecibles: `_umbral_adoptado_v1/_v2`, V1 con ventana
numérica (0, 0.75), y `MD.disenar_punto` relanzando el `DatoInvalidoError`
de un criterio en vez de tragarlo como «material no evaluable») y R48-030
(la v8 nombra WSDOT M 23-03.12 Tabla 8-4 en los seis sitios que decían «por
extraer»), 14 en rojo y liberados, más los tres del auditor (la memoria bajo
endurecimiento, la puerta de V1, el bloqueo del criterio)—; los 12 de
`tests/test_cierre_varios.py` —R48-001 (cinco citas nuevas verificadas: el
glosario y la Fig. 1.10-a del Manual de Puentes, AASHTO 1.2, HDS-5 §1.2 en
sus dos páginas; `DIS-LUZ-DENOMINACION` con el desacuerdo real, por vano
contra ancho total y 6.0 contra 6.096 m; la vía 2 del canal con usuario otra
vez), PC-31 (`registro.construir` con `lru_cache`, una instancia) y SIS-F-13
(la Tabla 5 de M 170M, PDF 10, el único escaneo real del ejemplar, transcrita
por imagen en `AASHTO_M170M.T5`: CP11 con dorado para los tres materiales)—;
el DUODÉCIMO test de ventana real de `test_gui_contrato`
(`tests/apoyo/gui_caras_normativa.py`: RANGO, CATALOGO y CAMPO construidas y
declaradas por `boton.invoke()`, SIS-F-01); dos parametrizados más en
`test_M2_material` (el concreto en CP11); tres que crecen solos en
`test_ext5_forma_gui` (76 → 79 criterios); y los nueve anclajes de
`test_decisiones_diferidas` para las fichas de las Partes XXXVI a XXXVIII
(C10-01..03, C05-01..02, C11-01, C14-01, C09-01..02). Ningún archivo restó
tests: `test_M5`, `test_cli`, `test_canal_discrepancias` y
`test_ext11_mutacion` reescribieron aserciones al contrato nuevo (V5 como
fila «no aplica», `criterio_aplicado` en V1/V2, la discrepancia declarada
por el paso 2.1, los operandos nuevos del censo de mutantes). Dos auditores
adversariales por cluster; el segundo refutó dos cierres —«las tres fuentes
coinciden» y «la PDF 10 está en blanco»— y los dos se rehicieron con las
fuentes que faltaban (`19bcf5a`). La línea base de la Familia C se regeneró
por FORMATO en cada cluster (clave `estado` del JSON, textos del ke y de
V1/V2, criterios usados, citas del paso 2.1 y su discrepancia; ningún número
de cálculo se movió). Aviso de entorno: durante la sesión `/dev/null` del
contenedor quedó sustituido por un archivo regular (un `cli.py --json
/dev/null` del auditor: `exportar` reemplaza el destino de forma atómica) y
los tests del subproceso del PDF fallaron hasta restaurarlo con `mknod` en
otra ruta y `mv`. Las cuatro configuraciones se MIDIERON sobre un checkout
limpio (`git worktree`) de `origin/main` en `19bcf5a`, en serie y sin otra
suite en marcha: las dos sin Tk sin `DISPLAY` y con un `xvfb-run` que falla,
las dos sin PyMuPDF desinstalándolo y reinstalándolo; `collected = 4175` en
las cuatro. Se midieron ANTES de sellar los documentos generados —los 13
tests de sincronía de `manifiesto_citas`, `trazabilidad.csv`,
`indice_formulas` y la convención de `test_ext9` fallaban en las cuatro por
el mismo motivo, ninguno depende de PyMuPDF ni de Tk— y la tabla suma esos
13 a cada `passed`; «sí · sí» se remidió sobre el commit de cierre con los
sellos puestos, y es el par que llevan los sellos. **PF-6 (2026-09-21) sumó DIECISIETE tests netos** (18
nuevos y un caso parametrizado retirado), y uno depende de Tk: los 15 de `tests/test_pf6_cabos.py` —los tres cabos, escritos primero
en rojo con `xfail(strict=True)` por test (medidos 12 xfailed y 0 XPASS antes
de tocar código) y liberados al corregir: (a) R48-007, el techo
`CBR_MAX_FISICO = 100.0` retirado contra la fuente primaria (verificador
normativo sobre el Manual de Suelos: S5 «CBR ≥ 30%» abierta, Cuadro 4.11
pág. 37; «Mínimo 100%» de la base granular, Cuadro Nº 10.2 pág. 108; «Base
Granular CBR 100%», Cuadro 12.13 pág. 129; y ningún techo en 281 páginas) y
sustituido por `CBR_MIN_FISICO`, con un CBR de 250 % que se carga y el piso
que sigue; (b) el editor escalar que suelta la fila cuando el texto deja de
ser su clave, medido en la ventana de verdad (`tests/apoyo/gui_eb_real.py`,
bloque 3b: el único de los 15 que depende de Tk); (c) `CAMPOS_OMITIDOS`
contrastado ruta a ruta contra el comportamiento del comparador, los
diferidos por contenido y un bool que nunca es igual a un número— y los tres
anclajes de `test_decisiones_diferidas` para las fichas de la Parte XXXV
(PF-6-01..03). Ningún archivo restó tests: `test_M0_carga` retira el caso
«250» de su parametrizado (ya no es inválido), `test_M5_verificaciones`
barre desde el piso y por encima de la tabla en vez de hasta el techo, y
`test_sin_literales` baja el censo de marcas de `dominios.py` de 5 a 4 (el
`0.0` del piso es literal exento). Cierra R48-007 entero. La línea base no
se movió: ningún número de cálculo cambia. Las cuatro configuraciones:
«sí · sí» MEDIDA sobre el árbol de PF-6 con `python3-tk` para `python3.12`
y PyMuPDF: 4112 passed, 3 skipped, collected 4115; las otras tres se
derivan de las de PF-5 sumando 17 `passed` con Tk, y 16 `passed` y 1
`skipped` sin Tk. **PF-5 (2026-09-21) sumó TREINTA Y CUATRO tests**, y ninguno
depende de PyMuPDF ni de Tk: los 32 de `tests/test_guia_perfil.py`, la
guardia de `docs/guia_perfil.md` —la guía de corrida de perfil para un
tesista, que NO se escribe a mano dos veces—: los ocho bloques de comandos
de la guía se ejecutan en subproceso, en el orden en que la guía los
presenta, con los archivos que la guía muestra (las cercas `archivo=` se
escriben tal cual y el CSV de trabajo se deriva de `tests/ejemplo_puntos.csv`
rellenando la sola celda que la guía dice), y se afirma lo que la guía
promete: el código de salida de cada comando, las líneas del RESUMEN que la
guía imprime contra la salida real, los cuatro puntos dimensionados con los
siete del cajón declarados y `S_conducto ≥ S_cauce`, la advertencia de
corredor sin `--datos-sitio` y su ausencia con él, la sesión mínima válida
que `--sesion` reproduce, `--comparar` y `--barrido`; las siete tablas
generadas se comparan texto a texto con `tests/apoyo/guia_perfil.py`, que
las deriva de sus símbolos (`M0_carga.COLUMNAS`, `VACIOS_ADMITIDOS`,
`servicio.CLAVES_EXTERNAS` con la bandera leída del parser real,
`datos_sitio.DATOS_SITIO`, `ca.criterios_de_perfil_sin_valor()` con
`Criterio.forma` y su ventana, `M11.COLUMNAS_RESUMEN_CSV`,
`sesion.sesion_vacia`) y se regeneran con `python -m tests.apoyo.guia_perfil`;
los diez ejemplos de `--declarar` (uno por criterio de perfil sin valor, en su
orden, con todas las formas) pasan la puerta real, y el README enlaza la
guía. El único `lento` es el del PDF por la sesión, que acepta los dos
finales declarados de `--pdf`. Los otros dos son los anclajes parametrizados
de `test_decisiones_diferidas` para las dos fichas de la Parte XXXIV
(PF-5-01, PF-5-02). No cierra IDs; las dos fichas registran lo que el prompt suponía y el árbol no
sostiene: DIEZ [A] de perfil sin valor desde PF-1 y no nueve, el `si` de
«Expediente cerrado» a perfil cuando nada bloquea al alcance declarado, la
copia del CSV con la coronación de C-01, y la sesión que la CLI no escribe.
La línea base no se movió: PF-5 no toca `src/`. Las cuatro configuraciones:
«sí · sí» MEDIDA sobre el árbol de PF-5 con `python3-tk` instalado para
`python3.12` (el intérprete de la suite es 3.11 sin tkinter; la sonda lo
encuentra sola) y PyMuPDF presente: 4095 passed, 3 skipped, collected 4098;
las otras tres se derivan sumando 34 a las de PF-4, porque ninguno de los
34 depende de PyMuPDF ni de Tk. **PF-4 (2026-09-21) sumó TREINTA tests**, y ninguno depende
de PyMuPDF ni de Tk: los 27 de `tests/test_pf4_regimen_v2b.py` —la
aceptación de PF-4: el régimen con que V2b aplica el indicador de HDS-5
§5.3.3 deja de estar cableado como «decisión conservadora del proyecto» y
pasa al criterio [A] de perfil `regimen_v2b` (categoría, valor de archivo
`umbral_duro`, ventana `umbral_duro` / `indicador_con_aviso`); 19 escritos
primero en rojo con `xfail(strict=True)` por test (medidos 19 xfailed, 0
XPASS, 2 passed y un teardown que fallaba en el árbol viejo por no existir
la clave) y liberados al corregir: la ficha, la guardia de forma sobre seis
valores malos y los dos buenos, `TipoDeVeredicto.INDICADOR` y su exigencia
de umbral, M11 pintándolo como aviso, V2b bajo los dos regímenes con la
elección y su fundamento en el paso, el consumidor que rechaza un régimen
que burla la puerta, la línea base sin mover un número medida con el
comparador de E-B, C-01 por la CLI real en las dos direcciones, y el editor
de categoría de la pestaña 2; más los que dejó la auditoría adversarial que
la sesión ejecutó al caerse el subagente (el literal buscado DENTRO del
bloque de C-01 y la clase de la fila, porque el literal ya se imprimía en
A-01 y A-02 y un `in html` a secas pasaba vacuo; y el barrido de PF-3, que
leía el veredicto sólo de `.cumple` y se habría callado un CUMPLE →
INDICADOR)—, los dos anclajes de `test_decisiones_diferidas` para las fichas
de la Parte XXXIII (PF-4-01, PF-4-02) y el que crece solo en
`test_ext5_forma_gui` con el criterio nuevo (75 → 76 criterios). Ningún
archivo restó tests. Cinco mutantes medidos y los cinco muertos: `cumple or
aviso` → `cumple`, INDICADOR → CUMPLE, `not cumple` → `cumple`, el paso sin
la elección del régimen, y el `nivel` del criterio a expediente. La línea
base de la Familia C se regeneró por FORMATO, clasificado diferencia a
diferencia con el propio comparador contra `a96bbec`: la huella
`criterios_sha1`, la clave nueva `veredicto` de cada verificación (26 en el
JSON ancho, 4 en los otros dos), el texto de `NUMERAL_V2B`, el criterio
nuevo entre los usados, `verificacion_pendiente` 21 → 22, y en las memorias
el CSS del aviso, la huella de la hoja de ruta y el recuento «75 / 36» →
«76 / 36»; ningún número de cálculo se movió y el CSV resumen, los tres
`cli_*.txt` salvo el numeral y la memoria del cajón quedaron intactos. Las
cuatro configuraciones: «sí · sí» MEDIDA sobre un checkout limpio
(`git worktree`) del commit `ext(PF-4)`, sin otra suite en marcha: 4061 passed,
3 skipped, collected 4064; las otras tres se derivan sumando 30 a
las de PF-3, porque ninguno de los 30 depende de PyMuPDF ni de Tk.
independientes. **PF-3 (2026-09-21) sumó TRECE tests**, y ninguno depende de
PyMuPDF ni de Tk: los 12 de `tests/test_pf3_barrido.py` —la aceptación del
barrido de sensibilidad: los siete del prompt escritos primero en rojo con
`xfail(strict=True)` por test (medidos 7 xfailed y 0 XPASS antes de tocar
código) y liberados al corregir (tres corridas sobre el mismo árbol con
`criterios_sha1` y `csv_sha1` idénticos, cada una con SU valor declarado y
su procedencia; la tabla leída del volcado y la primera corrida IGUAL a sí
misma; el valor fuera de la ventana que no corre nada, medido con
`servicio.correr` interceptado; el criterio de tabla que exige fila o nota
por la misma puerta; el estado del proceso repuesto con la MISMA
procedencia; la guardia por AST; y la CLI con dos barridos, el JSON y la
memoria que no se escribe), más los cinco que dejó el auditor adversarial
en la parte 2 (la comparación con la PRIMERA corrida y el «no comparable»
cuando A-01 pasa de control de entrada a salida en ke = 0.9; `_filas_de`
sobre una comparación sintética; el punto que deja de dimensionar y dice
V3; la base aplicada en la puerta como en la pestaña 2; y la CLI que
cierra la puerta de todos los barridos antes de correr, avisa de las
banderas que no aplica y nombra la clave inexistente y el valor vacío)— y
el anclaje de la ficha PF-3-01 en `test_decisiones_diferidas`. Ningún
archivo restó tests ni se reescribió. La línea base no se movió: el
comparador cambió tres literales por constantes con el mismo texto. Las
cuatro configuraciones: «sí · sí» MEDIDA sobre un checkout limpio
(`git worktree`) de `d4a4488` (el segundo commit `ext(PF-3)`, con los
ajustes del auditor), sin otra suite en marcha: 4031 passed, 3 skipped,
collected 4034; las otras tres se derivan sumando 13 a las de PF-2, porque
ninguno de los 13 depende de PyMuPDF ni de Tk. **PF-2 (2026-09-21) sumó QUINCE tests**, y ninguno depende de
PyMuPDF ni de Tk: los 14 de `tests/test_pf2_prevuelo.py` —la aceptación
del cuarto bloque del anticipo, escrita primero en rojo con
`xfail(strict=True)` por test (medidos 10 xfailed y 0 XPASS antes de tocar
código) y liberada al corregir: la luz en los cuatro puntos y lo de cada
familia (la coronación sólo en C-01, la longitud hidráulica sólo en B-01,
el caudal y la pendiente del canal en C-01 con S_conducto nombrado en la
misma entrada); con el JSON ampliado y la luz sólo queda la coronación; lo
que espera a un tablero no se confunde con lo que detiene; el TW sin vía
cae en el criterio con el mismo predicado del resolvedor; la UNIÓN contra
tres corridas reales con lo de más censado y medido; la guardia por AST de
que ni el bloque ni `cli._prevuelo` corren el pipeline; la CLI que sale con
1 y con 0; y las líneas del bloque; más los cuatro que dejó el auditor
adversarial en la parte 2: la celda obligatoria vacía que el JSON no
sustituye, la celda no numérica y la familia ilegible como faltas de
carga, la partición exacta de las claves externas sin columna, y la CLI
que sale con 1 cuando la cabecera detiene la carga— y el anclaje de la
ficha PF-2-01 en `test_decisiones_diferidas`. Ningún archivo restó tests:
`test_gui_contrato` fija las dos llamadas nuevas del panel,
`test_sin_literales` censa las cinco marcas de columna de la tabla nueva
de `gui/app.py` (45 → 50) y `test_ext9` retira ahora la marca de tiempo
REAL del JSON (`expediente.generado_utc`; retiraba una clave inexistente y
sólo pasaba con las dos corridas en el mismo segundo, que el aislamiento
de PF-2 destapó). La línea base no se movió. Las cuatro configuraciones:
«sí · sí» MEDIDA sobre un checkout limpio (`git worktree`) de `654ca60` (el
segundo commit `ext(PF-2)`, con los ajustes del auditor), sin otra suite en
marcha: 4018 passed, 3 skipped, collected 4021; las otras tres se derivan
sumando 15 a las de PF-1, porque ninguno de los 15 depende de PyMuPDF ni
de Tk. **PF-1 (2026-09-21) sumó CIENTO DOCE tests**, y ninguno
depende de PyMuPDF ni de Tk: los 13 de
`tests/test_pf1_hw_fuera_de_rango.py` —la aceptación de PC-03, escrita
primero en rojo con `xfail(strict=True)` por test (medidos 17 xfailed y 0
XPASS antes de tocar código sobre `863aac8`: los 11 ítems más 6 teardowns
del fixture `_limpio`, que en el árbol viejo fallaban al no existir la
clave) y liberada al corregir: la
carta fuera de rango es un vacío declarable (`CriterioPendienteError` sobre
`hw_entrada_fuera_de_rango`) con el par (Q, S) y S* en el mensaje; el
límite de signo analítico que `M4.pendiente_limite_de_signo` publica;
«energia_critica» adopta H_c y lo publica en `ControlEntrada.piso`;
«descartar» es la conducta anterior; la ficha es de perfil, categórica y
con ventana; el bloqueo viaja con criterio y la pestaña 4 y el JSON lo
pintan; declarado en caliente el punto dimensiona y la memoria lo
declara; S* no crece con D bajo Forma 1; y los dos que dejó el auditor
adversarial: el piso acota el SIGNO y por debajo de S* manda la ecuación
aunque dé menos que H_c, y bajo Forma 2 S* no es monótono y no alcanza el
dominio del dato—, los 96 de la propiedad P9 en
`tests/test_ext11_propiedades.py` (bajo S* la carta entrega carga sobre la
malla Q × D × fracción, en las tres ramas; S* no crece con D), el anclaje
de la ficha PF-1-01
en `test_decisiones_diferidas` y los dos que crecen solos con el criterio
nuevo (`test_ext5_forma_gui`, `test_criterios_adoptados`). Ningún archivo
restó tests: el parametrizado de MAT-D10 de `test_M4_control` mide ahora
los dos caminos (sin declarar y «descartar») y `test_cierre_perfil` cuenta
DIEZ vacíos de perfil, tres no invocados por el corredor. La línea base de
la Familia C se regeneró por FORMATO, medido con `diff`: `criterios_sha1`,
`hoja_ruta_sha1` (la nota «Corregido (PF-1)» de la v8 §4.2), la clave
nueva en la lista de criterios sin valor, el recuento «74 / 35» → «75 /
36» y las tres claves `hw_entrada_*` del JSON en `null`; ningún número de
cálculo se movió (README de la línea base). El auditor adversarial dejó
además la enmienda de la v8 con su declaración en el punto de uso, la
`justificacion` que promete sólo lo que el código hace, la monotonía
acotada a la Forma 1 y el piso viajando en `ResultadoHidraulico` y en el
JSON por punto. Las cuatro configuraciones: «sí · sí» MEDIDA sobre un
checkout limpio (`git worktree`) de `3d478d3` (el tercer commit
`ext(PF-1)`, tras el auditor y las dos guardias de la suite), sin otra
suite en marcha: 4003 passed, 3 skipped, collected 4006; las otras tres se
derivan sumando 112 a las del cierre de E-B, porque ninguno de los 112
depende de PyMuPDF ni de Tk.
**El cierre de E-B (2026-09-21, tras la revisión) sumó UN
test**, sin dependencia de PyMuPDF ni de Tk: el de
`tests/test_eb_editores_comparador.py` que cierra el hueco del texto que
nombra otra fila (escrito en rojo con `xfail(strict=True)`, medido 1
xfailed y 0 XPASS, y comprobado rojo otra vez sin la guardia antes de
liberarlo). Con él el archivo tiene 63. Se midió «sí · sí» sobre un
checkout limpio de `fbc57e6` (3891/3, collected 3894) y las otras tres
se derivan sumando 1, como en EXT-1 y EXT-2, porque el test no depende
de PyMuPDF ni de Tk. **E-B (2026-09-21) sumó SESENTA Y
NUEVE tests netos**, y ninguno depende de PyMuPDF; uno depende de Tk: los
62 de `tests/test_eb_editores_comparador.py` —la aceptación de E10, E14,
E13 reducido y E21 acotado: 53 en la parte 1 (51 funciones más un
parametrizado de tres casos), escrita primero en rojo con
`xfail(strict=True)` por test (medidos 52 xfailed, 1 passed y 0 XPASS
antes de tocar código; 49 XPASS al escribirlo, y liberados), más los
NUEVE que dejó el auditor adversarial en la parte 2 —y no ocho, que es lo
que decía el mensaje de `5a35ed3` («61 (+8)») y lo que sumaba el desglose
anterior de este párrafo: se contaron por nombre de función en el diff—
(el `descomponer_valor` que recortaba un triple y declaraba el recorte en
verde; el `repr` que ponía comillas a un texto; la pestaña 2 que no
declara desde un editor que no refleja el literal; la fila no elegible
que entraba con nota por otra puerta; la serie de claves que declara desde
la tabla; el dato de ensayo que exige su trazabilidad; el dict de tabla
que nombraba una fila cuyas celdas no eran el valor; el comparador con
falsos IGUALES en bloqueos, iteraciones y listas de estado; el NaN y el
infinito que caían del lado de «igual». La fila que un número «adivinaba»
y la categoría de tabla que proponía una clave que la guardia rechazaba
fueron REESCRITURAS de tests existentes, no altas) y el UNDÉCIMO test de ventana
real (`tests/apoyo/gui_eb_real.py`: la serie de pares par a par, el dict
con un campo fuera de ventana que no declara nada, la fila de la Tabla C.2
que pone 0.5 y el 0.55 que exige nota, las dos columnas nuevas y la
comparación de la corrida con su propio volcado)—, el de `test_linea_base`
con el comparador como segundo consumidor de la línea base, los seis
anclajes de `test_decisiones_diferidas` para las fichas de la Parte XXIX
(EB-01..06) y el parametrizado de `test_gui_contrato` que crece con
`gui/editores.py` en `ARBOLES_DE_LA_GUI`; menos UNO: el censo
`PUBLICAS_SIN_REFERENCIA_EN_TESTS` retira `M11_reporte.ancla_de_criterio`,
que la suite ya nombra. Ningún archivo restó tests: `test_cierre_perfil`
corta la memoria por el ancla y no por el título (el índice lo repite como
enlace), `test_ext4` conoce el quinto botón de la pestaña 4,
`test_sin_literales` censa `gui/editores.py` y las dos marcas de columna de
`gui/app.py` (43 → 45). La línea base de la Familia C se regeneró por
FORMATO, medido con `diff`: las claves `responsable` y `evidencia` en
`criterios.bloquearon` de los dos JSON con bloqueantes, y el índice, sus
tres reglas de estilo y el `id` de cada bloque de punto en las tres
memorias de la CLI; ningún número de cálculo se movió (README de la línea
base). Las cuatro configuraciones se MIDIERON sobre `origin/main` en
`5a35ed3` (el segundo commit `ext(E-B)`, con las correcciones del auditor,
fusionado por fast-forward), en serie, sobre un checkout limpio
(`git worktree`) y sin otra suite en marcha: las dos sin Tk sin `DISPLAY` y
con un `xvfb-run` que falla, las dos sin PyMuPDF desinstalándolo y
reinstalándolo; `collected = 3893` en las cuatro. **E-A (2026-09-21) sumó CUARENTA Y CINCO tests**, y
ninguno depende de PyMuPDF ni de Tk: los 36 de
`tests/test_ea_perfil_lamina.py` —la aceptación de NOR-HDS-05 entera, el
perfil de la lámina de agua por paso directo (HDS-5 pág. 3.12 / PDF 94
con la Ec. 3.7; umbrales de la pág. 3.24; Section 3.5.1): los 26 primeros
escritos en rojo con `xfail(strict=True)` de módulo —medidos 26 xfailed y
0 XPASS antes de tocar código— y liberados al corregir (los tipos
`PerfilLamina`/`TipoDePerfil`, los DOS dorados de LÍMITE que el conflicto
#7 admite sin corrida externa —flujo lleno de punta a punta, que reproduce
la fórmula cerrada de `control_salida` a 1e-9, y flujo uniforme en su
propia asíntota—, el balance de energía por estación y la monotonía de
M1/M2/S1, la convergencia N frente a 2N, la fracción analítica de longitud
llena, el caso (b) del dictamen que pasa a ENTRADA porque la S1 no alcanza
la entrada, el caso (c) con HW por remanso, V1/V2 sobre el perfil, la
corrida sin bloqueos «no evaluables», la regla vinculante #12 por AST y
las siete citas verificadas); los diez restantes los dejaron el auditor
adversarial (la asíntota y_n' de la Ec. 3.7 frente al y_n de Manning, la
banda 0.75–1.2 donde manda la comprobación si pide más carga, el TW a
1e-9 de la clave, el punto fijo sobre la asíntota) y el arnés de mutación
(`V_entrada_m_s` del retorno UNIFORME, los escalones mínimos)—, el de
`test_cli` (B-01 ahogado no cierra por V2 en ningún D), los siete
anclajes parametrizados de `test_decisiones_diferidas` para las fichas de
la Parte XXVIII (EA-01..07) y el que crece solo en `test_ext5_forma_gui`
con el criterio nuevo `fraccion_llena_mayor_parte` (73 → 74 criterios).
Ningún archivo restó tests: el bloque (b) de `test_ext3_regimen_barril`
se reescribió a la verdad nueva con el mismo número, `test_cierre_perfil`
(B-01 con V1/V2 evaluadas), `test_dimensional_piloto` (F4.PERFIL@4.3c/4.3d;
`K_FRICCION_SI` ya la nombra el paso 4.3c), `test_ext2` (HW multicelda
contra `perfil.HW_aproximado_m`), `test_ext11_mutacion` (censo remedido:
62 supervivientes con razón, 20 nuevos del perfil, un hueco real cerrado),
`test_ext8` (techos remedidos: 51.4 KB y 16.0 páginas por punto),
`test_sin_literales` (ocho marcas en M4) y `test_MD` (el y/D del punto
CP-2 con TW = 0 es el máximo del perfil M2, 0.7484, y no el uniforme) se
reescribieron sin sumar ni restar. La línea base de la Familia C se
regeneró y lo que se mueve está declarado en su README y en el commit:
B-01 (TW = 1.00 m) YA NO SE DIMENSIONA —la S1 desde el TW deja V_min =
Q/A(TW) entre 0.06 y 0.11 m/s < 0.25 en todo D: `DisenoNoFactibleError`
con motivo V2 donde antes salía 1.05 m con V1/V2 diferidas—; A-01 y A-02
no cambian de diámetro; el bloqueo «método no evaluable» desaparece de la
corrida; entran las doce claves `perfil_*` del JSON y los pasos 4.3c/4.3d;
cambian `criterios_sha1` y `hoja_ruta_sha1`. La mutación se remidió con el
arnés sobre las once funciones tocadas (242 mutantes: 212 muertos en la
primera vuelta, 87.6 %, 5 más en la segunda, 25 vivos, uno cerrado con
una aserción y 24 censados, ficha EA-06). Las cuatro configuraciones se
MIDIERON sobre `origin/main` en `b7d8def` (el commit `ext(E-A)`, fusionado
por fast-forward), en serie, sobre un checkout limpio (`git worktree`) y
sin otra suite en marcha: las dos sin Tk sin `DISPLAY` y con un `xvfb-run`
que falla, las dos sin PyMuPDF desinstalándolo y reinstalándolo;
`collected = 3824` en las cuatro. **EXT-11 (2026-09-21) sumó MIL CIENTO SESENTA Y DOS tests**,
y ninguno depende de PyMuPDF ni de Tk: los 981 de
`tests/test_ext11_propiedades.py` —las siete propiedades del motor por
mallas (Q = V_sedimentación·A en circular y rectangular; Q_total = N·Q_celda
a través de MD→M4; V_erosion ≥ V_sedimentación; continuidad y linealidad de
la transición en las dos formas; monotonía de HW(Q) bajo Forma 1;
tirante_normal = None para Q ≥ Q_lleno; HW(N=3) ≠ HW(N=1) y HW(N, N·Q) =
HW(1, Q)) más las dos tandas de «lo que la mutación enseñó» (V3 juzga la
rama alta y su paso lo publica; los umbrales de M5 son inclusivos; las
guardias del receptor trapecial, el par de Manning, el ke, la progresión
que se repite, la cota del TW, el motivo de descarte del marco)—, los 119
de `tests/test_ext11_cruce_temarios.py` (PC-29: 71 ítems ALTA/CRÍTICA de
los temarios cruzados con la hoja `Hallazgos`, leída con
`tests/apoyo/tracker.py` sin openpyxl), los 9 de
`tests/test_ext11_mutacion.py` (el arnés `tests/apoyo/mutacion.py`
probándose a sí mismo y el censo de 43 supervivientes con razón), los 47
netos de `test_guardias_de_la_suite` (la guardia PC-21
`afirmaciones_textuales_sobre_codigo` con taint, sus 16 autopruebas y el
censo `TEXTUAL_CON_RAZON`; el censo `PUBLICAS_SIN_REFERENCIA_EN_TESTS` de 29
públicas por tokens NAME con su llamador comprobado por AST, parametrizado),
los 5 anclajes de `test_decisiones_diferidas` para las fichas de la Parte
XXVII (EXT-11-01..05) y el test nuevo de test_cli (la Fase 8 llamada sobre
el concreto real de perfil). Ningún archivo restó tests: el skip permanente
de `test_MD` pasó a ser un test que corre (la ausencia real de M5 en
subproceso), y por eso «sí · sí» salta 3 y no 4; test_anticipo,
test_gui_contrato, test_ext8, test_ext10, test_ayuda_entrada, test_M5,
test_dimensional_piloto se reescribieron al AST sin sumar ni restar. La
mutación medida con el arnés (679 mutantes sobre M3–M5/MD, `_par_de_manning`
y las tres propiedades del par de n): 568 muertos en la primera vuelta
(83.6 %) contra diez archivos objetivo, 65 de los 111 restantes en la
segunda (línea base, cierre de perfil, CLI), 46 vivos, 43 tras la segunda
tanda; sin `hypothesis` ni `mutmut` (consulta sin respuesta, ficha
EXT-11-01). Las cuatro configuraciones se MIDIERON sobre `origin/main` en
`e734c23` (el commit `ext(EXT-11)`, fusionado por fast-forward), en serie,
sobre un checkout limpio (`git worktree`) y sin otra suite en marcha: las
dos sin Tk sin `DISPLAY` y con un `xvfb-run` que falla, las dos sin PyMuPDF
desinstalándolo y reinstalándolo; `collected = 3779` en las cuatro, y los
cuatro pares suben 1163 `passed` y bajan 1 `skipped` respecto de EXT-10,
porque ninguno de los 1162 depende de PyMuPDF ni de Tk y el salto
permanente de `test_MD` desapareció. **EXT-10 (2026-09-21) sumó OCHENTA Y CINCO tests**: los 78
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
2367; EXT-6: 2417; EXT-7: 2475; EXT-8: 2515; EXT-9: 2532; EXT-10: 2617;
EXT-11: 3779; E-A: 3824; E-B: 3893; cierre de E-B: 3894; PF-1: 4006; PF-2: 4021;
PF-3: 4034; PF-4: 4064; PF-5: 4098; PF-6: 4115; cierre C10/C05/C09/C11/C14:
4175; rediseño visual de la GUI (cuatro bloques, sin fila en esta tabla):
4178; T-0 de la cadena T: 4235; T-2: 4406; T-4: 4537; T-1: 4728; T-6:
4866; T-8: 4976; T-5: 5177; correcciones de T-8: 5246. La
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
| sí | sí | 5243 (**derivado** en las correcciones de T-8, no medido: el contenedor no tiene tkinter) | 3 |
| sí | no | 5230 (**MEDIDO** en las correcciones de T-8 sobre el árbol fusionado, con `NORMAS_DIR`) | 16 |
| no | sí | 5139 (**derivado**, no medido) | 107 |
| no | no | 5126 (**derivado**, no medido) | 120 |

Las cuatro filas son **con el repositorio de normas enlazado**
(`NORMAS_DIR`). Sin él, las dos con PyMuPDF pasan DIECIOCHO menos y saltan
dieciocho más desde T-1 (medido en «sí · no» sobre el árbol de las
correcciones de T-8: 5212 passed, 34 skipped; sobre el de T-5, 5143 y 34;
sobre el de T-8, 4942 y 34; ni T-6, ni T-8, ni T-5, ni las correcciones de
T-8 sumaron ninguno que abra el repositorio de normas; eran
siete hasta T-2 y doce hasta T-4: T-4 sumó los cinco de
`tests/test_t4_materiales_durabilidad.py` que abren el WSDOT Hydraulics
Manual y T-1 los seis de `tests/test_t1_hidrologia.py` que abren su capítulo
2); las dos sin PyMuPDF, uno menos y uno más, porque los otros diecisiete ya
iban saltados por la marca `pdf`. Tras T-5 la tabla decía 5174 / 5161 / 5071
/ 5058, medida sólo la segunda. Tras T-8 la tabla decía 4973 / 4960 / 4898
/ 4885, medida sólo la segunda. Tras T-6 la tabla decía 4863 / 4850 / 4788
/ 4775, medida sólo la segunda. Tras T-1 la tabla decía 4725 / 4712 / 4650
/ 4637, medida sólo la segunda. Tras T-4 la tabla decía 4534 / 4521 / 4479
/ 4466, medida sólo la segunda. Tras T-2 la
tabla decía 4403 / 4390 / 4363 / 4350, medida sólo la segunda. Hasta T-0 la tabla decía 4172 / 4159 / 4137 / 4124, medidos
los cuatro en el cierre del 2026-09-22 sobre `19bcf5a`; tras T-0, 4232 /
4219 / 4193 / 4180, medida sólo la segunda.

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
conflictos resueltos; desde T-0, cinco clusters más, C15 a C19, para los
hallazgos `INF-`). Ese archivo es el TRACKER: el estado de cada hallazgo se
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
NOR-HID-02 y SIS-B-22. **Y desde T-0 (2026-11-11) tiene 367 filas**: entraron
los 64 hallazgos del `INFORME_evaluacion_app_alcantarillas_vs_PDF.md`
(repositorio `Cotas-esviaje-alcantarillas`) con prefijo `INF-`, y cinco
clusters nuevos, C15 a C19, para las causas raíz que las tres auditorías no
tenían (hidrología, Fase 8, cabezal por punto, protección y espaciamiento,
criterios vacíos). Su plan es la cadena T,
`docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md` (serie de commits
`tesis(T-n)`). **El ID de un `INF-` es el número del INFORME, no el que
escribe el prompt**: la cadena cita seis hallazgos del §5.1 con un número
que no es el de su ítem, y la tabla de equivalencias está al principio de
ese documento y en «Vínculos cruzados» de cada fila (ficha T0-04). Quien
cierre uno escribe el canónico. Las entradas de diseño que la cadena no
rellena —y quién debe cada una— están en `docs/contrato_entradas.md`.

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
