# Reglas del proyecto

## Fuente de verdad
- Fuente normativa única: docs/hoja_de_ruta_alcantarillas_v8.md (o la version
  vigente que exista en docs/: M11 la localiza con el patron
  `hoja_de_ruta_alcantarillas_v*.md` y exige que haya exactamente una). Toda cita de
  numeral se verifica contra ese archivo. Nunca se inventa un numeral.
- Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta.
- **La única excepción a lo anterior: la fuente primaria.** Si la hoja de ruta
  discrepa del documento normativo original —el PDF del repositorio de
  normas enlazado por `NORMAS_DIR` (ver «Dónde están los PDF de normas»;
  hasta T-12 también estaba en `normas/` de este repositorio)— y la
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
  para la longitud de cuneta de la Fase 10, y desde T-9 la usa la Fase 1-bis
  para el caudal de un punto de Familia B —que es, por contrato, el de la
  cuneta que descarga en el alivio—, UNA vez: la Fase 10 lo reutiliza y no
  repite sus pasos). La GUI y la sesión todavía no conocen las dos entradas
  (ficha T1-04).
- **La Fase 10 verifica, y puede fallar (T-9).** `src/modulos/M10_espaciamiento.py`
  tiene dos verificaciones que entran a la aceptación de la Familia B
  (`PERFILES[Familia.B].verificaciones_aceptacion` = V1 + V2 + V4 + V5 + VB1 +
  VB2, que sigue siendo huella y no filtro): **VB2**, la condición literal del
  Manual (núm. 4.1.2.1 a), «Q manning > Q de aporte»), el caudal del punto
  contra la capacidad de la cuneta (`M10.verificar_aporte`), y **VB1**, el
  tramo de cuneta entre el alivio y el extremo de su lado de progresivas
  MENORES contra el espaciamiento máximo (`M10.verificar_tramo`). El extremo lo
  resuelve `M10.extremo_del_tramo` —el inicio declarado, que gana y no puede
  ser posterior a la obra, o la obra anterior en progresiva: de Familia B, o de
  Familia A por el criterio `obras_familia_a_extremo_de_cuneta`— con TODAS las
  obras a la vista, perezosamente y sólo para los alivios que pasan la Fase 2
  (`servicio.correr`); VB1 vive fuera del bucle de diámetros y ningún diámetro
  la cambia. Tres reglas: un VB1 que **no se evaluó** es un `Bloqueo` del punto
  que espera el dato que lo destraba (`TramoDeAlivio.falta`), nunca un aviso
  que deje el expediente cerrado; ningún texto de la Fase 10 supone el sentido
  del flujo en la cuneta; y con el tramo conocido el aporte por metro es Q / s
  (`M10.longitud_hidraulica_por_tramo`), sin mezclar el área tributaria con el
  ancho tributario —sin tramo, q · b con aviso de la longitud que el par
  implica—.
- **El cabezal es POR PUNTO desde T-7a, y su geometría la PROPONE una regla
  que el punto puede pisar.** `servicio._fase_9` (a expediente, detrás de la
  socavación de la Fase 6 y de la Fase 8) arma los dos cabezales de cada punto
  dimensionado con `M9.cabezal_del_punto`, y el proyecto solo guarda la suma
  (`InformeCabezal.por_punto`). Cada dimensión lleva su ORIGEN —«propuesta por
  regla», «declarada» (`cabezal_declarado` de `--datos-externos`) o «derivada
  de dimensiones declaradas»—, y una declarada se contrasta con los mínimos
  con número (CB1 a CB7). La embocadura es del punto y se resuelve ANTES de la
  Fase 4 (`M9.embocadura_del_punto`): en un marco, la carta y el ke declarados
  tienen que ser de la banda de ángulo del cabezal. El cabezal es normal al
  eje del conducto y, con esviaje, sus dos aleros miden distinto. Fichas
  T7A-01 a T7A-08.
- **Y desde T-7c cada cabezal se ARMA detrás de su estabilidad, con la misma
  geometría y sin iterarla** (`servicio._fase_9_armado`: una etapa por las
  solicitaciones, una por elemento y una por la tabla, para que lo que un
  elemento no pueda evaluar quede como `Bloqueo` y los demás sigan). Rige
  AASHTO LRFD Sección 5 sobre las solicitaciones FACTORADAS (filas A1 a A4,
  A6 la fisuración de 5.6.7 en Servicio I, A7 el f'c por durabilidad, A8 la
  altura de la zapata sobre su refuerzo de E.060 15.7); E.060 se calcula en
  paralelo como contraste [N→] (A5) y **los dos marcos no se cruzan**: cargas
  de un marco con φ del otro es un defecto. En los mínimos constructivos rige
  el más exigente de los dos. Con el muro que no cede
  (`regimen_resistencia_elementos_cabezal` = `no_cedente_k0`) los elementos
  se arman con el empuje en reposo y el Evento Extremo I con k_h = 1.0·k_h0,
  aunque la estabilidad externa —que sigue con el muro que cede— lo reduzca;
  la pantalla y el alero integran cada diagrama de empuje por encima del
  arranque (`M9.empujes_sobre_el_arranque`). El cabezal de gravedad no se
  arma: se verifica como concreto ciclópeo (C1 a C6). Fichas T7C-01 a
  T7C-13.
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
  EXT-5, 53 de las 70 claves (71 desde EXT-6, 73 desde EXT-7, 74 desde E-A, 75 desde PF-1, 76 desde PF-4, 77 desde el cierre de C10, 79 desde el de C05, 82 desde T-2, 88 desde T-4, 95 desde T-1, 97 desde T-6, 102 desde T-8, 109 desde T-5, 110 desde T-3, 114 desde T-9, 119 desde T-7a, 129 desde T-7b, 139 desde T-7c, 141 desde la verificación de fórmulas de T-7) aceptaban la cadena `'cero'` y la GUI no podía
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

**Y desde S21 el nivel lo llevan los 69 (70 desde T1, 71 desde EXT-6, 73 desde EXT-7, 74 desde E-A, 75 desde PF-1, 76 desde PF-4, 77 desde el cierre de C10, 79 desde el de C05, 82 desde T-2, 88 desde T-4, 95 desde T-1, 97 desde T-6, 102 desde T-8, 109 desde T-5, 110 desde T-3, 114 desde T-9, 119 desde T-7a, 129 desde T-7b, 139 desde T-7c, 141 desde la verificación de fórmulas de T-7), no sólo los que no tienen valor.** La
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
  `demanda_sismica_licuefaccion`, que no tiene consumidor. De los **siete** sin
  consumidor —contados de nuevo por las correcciones de T-11 (H11), porque
  esta frase decía «ocho» desde T-7b, que le dio consumidor real a
  `c_phi_fundacion` (el ensamble de estabilidad de M9)— (ocho hasta T-7b;
  nueve hasta T-7a, que le dio consumidor real a `angulo_aletas`
  —`M9.embocadura_del_punto`, de perfil—; diez hasta T-1, que le dio consumidor real a
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
que a `--alcance perfil` pasa la tabla de 69 filas (70 desde T1, 71 desde EXT-6, 73 desde EXT-7, 74 desde E-A, 75 desde PF-1, 76 desde PF-4, 77 desde el cierre de C10, 79 desde el de C05, 82 desde T-2, 88 desde T-4, 95 desde T-1, 97 desde T-6, 102 desde T-8, 109 desde T-5, 110 desde T-3, 114 desde T-9, 119 desde T-7a, 129 desde T-7b, 139 desde T-7c, 141 desde la verificación de fórmulas de T-7) a 36 y los pendientes
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
  **Desde la corrección de T11-03 (cierre de T-11) el escalón que no cabe
  bajo la subrasante es un DESCARTE POR RASANTE, no un dato inválido**:
  `MD.disenar_material` lo reconoce por geometría (`MD._escalon_sin_cabida`:
  la excepción de `M5.altura_relleno_sobre_clave` sobre `cota_subrasante`
  y la clave sobre la subrasante con `TOL_UMBRAL_NORMATIVO`), lo anota con
  sus dos cotas (`PasoDiseno.sin_cabida`) y termina la progresión de ese
  material; el punto sale «NO FACTIBLE POR RASANTE» con el motivo del
  escalón anterior y `delta_rasante_m` = el delta de 7.A del escalón que no
  cabe (`M7.tamizado_rasante`), **sólo** cuando es geometría pura —el
  escalón cumple todo lo evaluado y gobierna el recubrimiento—, rotulado
  COTA INFERIOR para ese escalón y no remedio verificado del punto (ficha
  T11-03). Hasta T11-03 salía como dato inválido de una cota que nadie
  había tocado, el material «no evaluable» y sin delta.
- DatoFaltanteError: falta un dato de entrada. Falta la **columna** entera
  del CSV, o la celda obligatoria viene vacía. Lleva el nombre de la columna.
  **También cubre el dato que no es columna del CSV**: el que llega por
  `--datos-externos`, y el que un tablero externo tendría que aportar y
  todavía no aporta (`ancho_derecho_via_m` en V5 era el caso vivo; desde T-7b
  es clave de `--datos-externos`, como `cota_afectacion_aguas_arriba_msnm`, y
  sin ella, declarado el método de V5, sale este error). En esos
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
  **corregir** algo es Invalido. **Y desde la corrección de T11-03 MD no la
  degrada a «no factible»** cuando la levanta la Fase 5 sobre un dato DEL
  PUNTO (el caudal del evento extremo menor que el de diseño, que V8
  rechaza): `MD._exigir_datos_validos` relanza la primera, con su `campo`
  (bloqueo `DATO_INVALIDO`), si detuvo un escalón que cumplía todo lo que la
  Fase 5 le había evaluado o si detuvo a todos los candidatos —el mismo
  patrón que PC-28 y T-5 para el dato que falta—. Fuera, a propósito y en la
  ficha T11-03: el resultado aceptado cuando un candidato posterior cierra,
  y el `DatoInvalidoError` que M3 o M4 levantan antes de la Fase 5 (la rama
  de error de la línea base), que siguen como estaban.
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
  como V1/V2. Y desde T-7b la levantan, cada una con SU rótulo, V5 con el
  método `perfil_de_remanso_paso_a_paso` o sin pendiente de cauce
  (`MOTIVO_METODO_NO_EVALUABLE_REMANSO`), V8 con el umbral del desborde
  admitido (`MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO`) y el ensamble de
  estabilidad del cabezal (`MOTIVO_METODO_NO_EVALUABLE_CABEZAL`) con agua en
  el plano de empuje bajo sismo, con una cuña de tanteo sin máximo interior o
  con `regimen_cabezal` = `no_cedente`; la carga a presión del evento extremo
  fuera de las ecuaciones de M4 lleva la del HDS-5. Las del cabezal viajan como
  `Bloqueo` del punto, una por cabezal y condición (`servicio._fase_9`). Y desde
  T-7c la levanta `M9.diseno_flexion_corte` cuando una sección del cabezal queda
  fuera de las condiciones en que AASHTO 5.7.3.4.1 permite el cortante
  simplificado y no lleva estribos (el procedimiento general no se
  implementa), encabezada con `MOTIVO_METODO_NO_EVALUABLE_ARMADO`: viaja como
  `Bloqueo` de ESE elemento (`servicio._fase_9_armado`) y los demás se arman. Y desde EXT-3 `Bloqueo` vive en `modelos.py`
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
  porque necesita las corridas de referencia enteras —desde T-10 son DOS, que
  sí dimensionan, y desde T-11 TRES, con sus datos de PRUEBA en
  `tests/fixtures/corridas_de_referencia/` (`indice_formulas.CORRIDAS_DE_REFERENCIA`):
  la de la guía de perfil, la de expediente con cabezal y la de la
  hidrología calculada (el juego de la validación integral de T-11 con la
  variante `caudal_calculado`, que un test ata byte a byte al juego)—. Y
  desde T-11 hay cuatro documentos GENERADOS más, los de la validación
  integral (`docs/validacion_integral.md`, `validacion_hds5.md`,
  `validacion_hy8.md` y `validacion_sensibilidad.md`), cada uno con su test
  de sincronía y sin sello: los escribe `python -m
  tests.apoyo.validacion_integral --escribir`,
  `tests.apoyo.validacion_externa` y `tests.apoyo.sensibilidad`. El sello (fecha, commit
  de origen, alcance, par de la suite con su entorno) lo pone quien regenera
  y el test lo LEE del documento para comparar el cuerpo y no la fecha.

## Dónde están los PDF de normas: `NORMAS_DIR`, y sólo allí

**Decisión de T-0 de la cadena T (2026-11-11), opción (a): una variable de
entorno, no un submódulo ni un enlace simbólico; y desde T-12 (2026-11-13)
es la ÚNICA vía.** T-0 dejó dos carpetas —`NORMAS_DIR` y, mientras
existiera, `normas/` de este repositorio—; T-12 **retiró los dieciocho PDF
de `normas/`** después de comprobar, uno a uno y por sha1, que son idénticos
a los del repositorio de normas (el `git rm` no reescribe historia:
siguen en los commits anteriores), y con ellos la caída. Una sola puerta
conoce la carpeta (`src/normativa/fuentes.py`: `directorios_de_normas()`,
`ruta_pdf(fuente)`, `pdf_en_disco()`): la que nombre la variable
**`NORMAS_DIR`**, el clon del repositorio de normas (`Andy-rba30/Normas`);
vale la raíz del clon o su subcarpeta `normas/`, que es donde ese
repositorio guarda los PDF.

El comando, que es el que usa toda sesión que verifica:

    git clone https://github.com/Andy-rba30/Normas.git /ruta/a/Normas   # una vez
    export NORMAS_DIR=/ruta/a/Normas
    python3 -m pytest -q -p no:cacheprovider --no-header

Y para leer un PDF con la herramienta de siempre, que resuelve el fragmento
del nombre en la carpeta enlazada:

    NORMAS_DIR=/ruta/a/Normas python3 -m src.normativa.extraccion texto hec14 202

- **Por qué una variable.** El repositorio de normas lleva documentos con
  copyright (AASHTO, ASTM) y el README recomienda que sea privado. Un
  submódulo ataría cada clon de la app a una credencial sobre él y versionaría
  aquí su URL y su commit. La variable no versiona nada, vale con el
  repositorio público o privado, y un despliegue que sólo calcula no tiene
  que clonar 330 MB: **ningún módulo de cálculo abre un PDF**, sólo quien
  verifica (los tests `-m pdf`, `python3 -m src.normativa.extraccion`,
  `python3 -m proceso.verificar_sesion`). Fichas T0-01 y T12-01 de
  `docs/decisiones_diferidas.md`.
- **`Fuente.archivo_pdf` es un nombre lógico** («normas/hif12026.pdf»), no
  una ruta: dice cómo se llama el archivo dentro de la carpeta de normas, esté
  donde esté. Nadie compone `RAIZ / fuente.archivo_pdf`: se llama a
  `fuentes.ruta_pdf(fuente)`, que devuelve la ruta donde el archivo está, o
  donde se le esperaba si no está —sin enlace, `fuentes.RUTA_SIN_ENLACE`,
  `$NORMAS_DIR/normas/<archivo>`— y entonces quien llama decide si salta.
- **Este repositorio no versiona ningún PDF.** La guardia de PC-23
  (`tests/test_ext6_registro_normativo.py`) lo comprueba con `git ls-files` y
  mira el repositorio enlazado: todo PDF de allí es Fuente presente o está
  censado (`PRESENTES_SIN_REGISTRAR`), y toda fuente presente tiene allí su
  PDF. `SOLO_EN_EL_REPO_NORMAS` (el censo transitorio de T-0 para HEC-14 y
  el WSDOT) y `DIRECTORIO_NORMAS_DEL_REPOSITORIO` se retiraron con los PDF.
- **Sin `NORMAS_DIR` la suite queda verde y SALTA TODO TEST QUE ABRE UN PDF**:
  `conftest.py::pytest_runtest_setup` salta cualquier test con la marca `pdf`
  con un solo motivo (`MOTIVO_SIN_NORMAS_DIR`), y los pocos que leen un PDF
  sin la marca (la mitad de PC-23 que mira el repositorio enlazado, el sha1 de
  los dos PDF censados) se saltan diciéndolo. Es el tercer eje de entorno
  además de PyMuPDF y Tk, y desde T-12 abarca a todos los PDF, no sólo a los
  de HEC-14 y WSDOT: el número medido está en `proceso/bitacora_conteos_y_entorno.md`.
  `python3 -m proceso.verificar_sesion` lo dice en su paso 5 como AVISO.
  **Una sesión que verifica no cierra con esos saltos**: enlaza el
  repositorio y los corre.
- **Un `NORMAS_DIR` que apunta a una carpeta que no existe no se calla**:
  `FileNotFoundError`. Quien definió la variable quiso enlazar el repositorio,
  y seguir sin él le daría una suite verde que no verificó lo que creía.

## Material de proceso: `proceso/` (desde T-12)

Esta constitución lleva sólo las REGLAS TÉCNICAS del programa. El material
del proceso de desarrollo asistido por IA se movió en T-12 (2026-11-13,
INF-5.2.2) a `proceso/`, que **no es parte del entregable** (`git archive` lo
excluye por `.gitattributes`, y `python -m pytest` desde la raíz no lo
recoge: `testpaths = ["tests"]` en `pyproject.toml`). Nada se borró: todo se
movió con `git mv` y conserva su historia.

- `proceso/bitacora_conteos_y_entorno.md` — la sección «Cierre de tarea: la
  entrega es `origin/main`» que estaba aquí, entera: el ritual de cierre, el
  par de la suite sesión a sesión, la tabla de las cuatro configuraciones y
  los incidentes de entorno. **La tabla de conteos se actualiza allí.**
- `proceso/reglas_de_correccion_de_auditorias.md` — las secciones «Reglas de
  corrección de hallazgos de auditoría» y «Git (fase de corrección)», enteras.
  Una sesión que corrija hallazgos o integre un prompt de una cadena las lee
  ANTES de tocar nada.
- `proceso/auditorias/` (los tres informes, el tracker
  `matriz_cruzada_auditorias.xlsx` y los temarios), `proceso/planes_mejora/`
  (las cadenas de prompts, incluida la T, y los planes),
  `proceso/hoja_de_ruta_correcciones_v12.md` (el plan de correcciones de las
  auditorías), `proceso/auditoria_y_ruta_despliegue_v9.md`,
  `proceso/.claude/agents/` (los subagentes), `proceso/verificar_sesion.py`
  (`python3 -m proceso.verificar_sesion`) y `proceso/apoyo/tracker.py`.
- `proceso/tests/` — los tests de PROCESO (la gobernanza de la cadena T sobre
  el tracker, el cruce de los temarios, la copia de la cadena, la cobertura de
  la auditoría de sistema), con su propio `conftest.py`. Se corren aparte:
  `python -m pytest proceso/tests`. El par de la suite del ENTREGABLE es el
  de `python -m pytest` desde la raíz, y la suite del entregable tiene que
  pasar también sobre una EXPORTACIÓN (`git archive HEAD`: sin `proceso/` ni
  `.git`); lo que lee lo versionado o `proceso/` se salta allí diciéndolo.
- La carpeta de orquestación de la cadena T no está en `main`: vive en la rama
  `tesis/orquestacion-estado` (`docs/planes_mejora/orquestacion_T/`).
