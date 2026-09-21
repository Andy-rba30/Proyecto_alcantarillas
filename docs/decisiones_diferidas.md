# Decisiones diferidas — el registro único

Este documento existe por una razón concreta: el proyecto tiene **veintidós
objetos que la auditoría de sistema clasificó «deliberado sin documentar»**.
No son defectos. Son decisiones que alguien tomó a conciencia —conservar una
API sin llamador, excluir un directorio de un barrido, no implementar un
procedimiento todavía— y que **no estaban escritas en ningún sitio donde un
revisor las buscara**. La auditoría no las encontró mal hechas: las encontró
mudas.

El plan (`docs/hoja_de_ruta_correcciones_v12.md`, S14 punto 5 y S19 punto 1)
pide desde hace cinco sesiones «cada criterio sin consumidor, con su razón
escrita **en un solo lugar**». Este es ese lugar.

## Qué es y qué no es

- **Es** el índice de las decisiones. Cada ficha dice cuatro cosas y siempre
  las mismas: **qué se difirió**, **por qué**, **qué haría falta para
  cerrarlo**, y **dónde vive en el código**.
- **No es** una segunda copia de la razón. La razón vive donde vive el
  código —en el docstring del símbolo, en el comentario de la constante, en el
  test que la vigila— y aquí se **cita el símbolo**, no se transcribe el
  párrafo. Dos copias de la misma razón divergen sin que nada avise, y ese
  defecto ya lo tuvo el proyecto con las transcripciones normativas
  (NOR-MEM-01).
- **No es** el tracker, y los dos números no miden lo mismo. En el tracker
  (`docs/auditorias/matriz_cruzada_auditorias.xlsx`, hoja `Hallazgos`) **las 22
  figuran como `Cerrado`**, y con razón: lo que el tracker sigue es si el
  hallazgo está atendido, y todos lo están —la decisión se tomó y se escribió—.
  Aquí se mide otra cosa: **cuántas no esperan nada**. Son **quince**. Las otras
  **siete** están cerradas Y siguen esperando algo que no depende de esta
  decisión: SIS-A-04 (la cota levantada en campo), SIS-A-13 (el n del cauce
  natural, para el segundo indicador del num. 5.3.3), SIS-A-16 (que la Sec. 1.5
  recoja las dos filas), SIS-B-04 (el levantamiento de la sección del receptor),
  SIS-B-07, SIS-B-08 (un discriminante en `PeriodoRetorno`) y SIS-B-10 (que la
  §1.2 deje de nombrar `Tc.py`, o que su procedimiento entre al calculador).
  **Dos de las siete cambiaron de naturaleza en S20** y las fichas lo dicen:
  SIS-A-13 y SIS-B-04 pasaron de «difierido» a IMPLEMENTADO, y lo que esperan
  ya no es permiso para escribir el código sino un dato de campo que lo
  alimente mejor. Es la distinción que el epígrafe de arriba adelanta: cerrado
  no significa que el mundo no pueda cambiar.
- **Un hallazgo `Cerrado` con «qué haría falta» lleno no es una contradicción**,
  y conviene decirlo porque lo parece: cerrado significa que la decisión está
  tomada y escrita, no que el mundo ya no pueda cambiar. El día que llegue la
  cota levantada, SIS-A-04 no se reabre — se rehace la decisión con el dato.

## Cómo se mantiene

`tests/test_decisiones_diferidas.py` deriva la lista de los veintidós
**del propio informe de auditoría** —las fichas cuya línea `**Clasificacion**`
dice «deliberado sin documentar»— y comprueba que cada una tenga ficha aquí,
con sus cuatro campos, y que el símbolo que la ficha nombra **siga existiendo
en el repositorio**. Si alguien renombra el símbolo, este documento se pone en
rojo en vez de envejecer en silencio. Es la misma lección que dejó
`FACTOR_MURO_TABLA`: un documento que nadie verifica es una afirmación, no un
registro.

---

# Parte I — Los 22 «deliberado sin documentar»

## SIS-A-04 · `cota_entrada_supuesta` rellena un vacío de dato dentro de M5

- **Qué se difirió:** la cota de fondo de entrada no se mide: se adopta desde
  `cota_terreno` por una regla que el proyectista declara.
- **Por qué:** el dato es del levantamiento topográfico y el expediente no lo
  trae por punto. Adoptarlo en silencio era el defecto; adoptarlo **declarado**
  es la única alternativa que no inventa una medición.
- **Qué haría falta:** la cota de fondo levantada en campo, por punto, como
  columna del CSV.
- **Dónde vive:** `src/criterios_adoptados.py::origen_cota_fondo_entrada`

## SIS-A-13 · V2b (sedimentación / colmatación) — IMPLEMENTADA en S20

- **Qué se difirió:** ya nada, y conviene decir qué se difería y por qué dejó
  de estar bien difierido. La Fase 5 enuncia once verificaciones y el programa
  implementaba diez; V2b no existía en ninguna línea de código y en su lugar
  había una constancia: un párrafo que la memoria imprimía y que nadie tenía
  que contestar.
- **Por qué se cerró:** la premisa del diferimiento —«la colmatación no es un
  cálculo con umbral que este programa pueda evaluar»— era cierta **del Manual
  peruano** y falsa del cuerpo normativo que el proyecto ya aplica. El HDS-5
  3.ª ed., que vive en `normas/` y del que salen el control de salida y `h_o`,
  nombra los indicadores en su num. 5.3.3 «Sedimentation» (pág. impresa 5.11)
  y los nombra en términos de **dos números que el cálculo ya tiene**: la
  pendiente del barril frente a la del cauce natural, y la rugosidad de uno
  frente a la del otro. El primero se evalúa; el segundo exige el n del cauce,
  que no es columna, y queda declarado.
- **Qué haría falta:** dos cosas, y ninguna bloquea. (1) El **n de Manning del
  cauce natural** por punto, para evaluar el segundo indicador del mismo
  numeral. (2) Que la hoja de ruta recoja el 5.3.3: hoy su fila V2b atribuye
  la mitad [N] al «material sólido de arrastre», que es el asunto de V6, y
  afirma que «la norma no protege del riesgo real» sin acotar de qué norma
  habla. El defecto se reporta ahí, en su punto de uso.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v2b_sedimentacion` y
  `src/criterios_adoptados.py::acceso_mantenimiento_v2b`, que es la mitad [A]
  —el acceso de mantenimiento en planos— y que **detiene** la corrida mientras
  siga vacía: la obligación no se relajó al implementarse la otra mitad, se
  endureció.

## SIS-A-16 · Dos validaciones cruzadas de M0 que no son fila de la tabla de Sec. 1.5

- **Qué se difirió:** el diámetro implícito y la entrega por gravedad se
  validan aunque la tabla de Sec. 1.5 no las liste.
- **Por qué:** son contradicciones internas de la fila —el dato está y no puede
  ser— y dejarlas pasar sería aceptar un expediente incoherente por un
  tecnicismo de tabla. Se declaran como añadidos del proyecto, no como norma.
- **Qué haría falta:** que la Sec. 1.5 incorpore las dos filas, o que declare
  por qué no las quiere.
- **Dónde vive:** `src/modulos/M0_carga.py::_valida_cruzadas`

## SIS-A-17 · La GUI no exponía `--alcance`

- **Qué se difirió:** nada, ya. Estaba difierido de hecho y sin declarar: la
  ventana corría siempre «expediente» y `memoria_perfil.html` era inalcanzable.
- **Por qué:** se cerró en S17 exponiendo el selector, y la plantilla se elige
  con `cli.plantilla_por_alcance`, la misma función que usa `cli.main`.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `gui/app.py::_construir_tab_datos`

## SIS-A-18 · La sesión JSON no guardaba los criterios declarados

- **Qué se difirió:** nada, ya. Quien declaraba cinco criterios y volvía al día
  siguiente perdía las cinco decisiones sin aviso.
- **Por qué:** se cerró en S17. Se guardan valores **y procedencia**, y se
  reponen por la misma guardia que usan la ventana y la CLI, porque una sesión
  es un archivo que alguien pudo editar a mano.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/declaracion.py::restaurar_sesion`

## SIS-B-04 · «TW se calcula, no se mide» (Sec. 1.3) — IMPLEMENTADO en S20

- **Qué se difirió:** el procedimiento de tres pasos de Sec. 1.3 —Q del
  receptor → tirante normal del receptor → TW—. `Q_receptor_m3s` y `cota_TW`
  se validaban y no alimentaban nada: un CSV con las dos columnas llenas
  seguía exigiendo `--tw`.
- **Por qué se cerró:** el diferimiento se apoyaba en que faltaba un dato —el
  caudal del receptor— y en que el paso 2 necesita además la **sección
  transversal del receptor**, que no es columna. Lo segundo sigue siendo
  cierto y lo primero dejó de serlo: el dato es del Tablero 3.1 y el CSV lo
  admite. Lo que faltaba no era esperar: era **declarar la sección** como el
  vacío que es y escribir el procedimiento alrededor.
- **Qué haría falta:** el **levantamiento de la sección del receptor** en cada
  punto de descarga, que es una obra de terceros —el dren de la Junta de
  Usuarios— y que hoy entra como adopción de perfil con su ventana. Mientras
  no exista, la memoria dice que el nivel del receptor es una adopción; el día
  que llegue, el criterio deja de aplicarse. Falta además que la hoja de ruta
  lo recoja: su Sec. 1.3 pide correr Manning «en la sección del receptor» y ni
  la Sec. 1.1 ni la Sec. 1.2 la traen. El defecto se reporta ahí.
- **Dónde vive:** `src/modulos/M3_hidraulica.py::tw_seccion_1_3` (las cuatro
  vías, en orden de precedencia) y `src/criterios_adoptados.py::seccion_receptor`.
  `TW_receptor` sigue existiendo y sigue vacío a propósito: es la **última
  puerta**, la que detiene cuando el expediente no aporta ni el nivel, ni el
  caudal, ni la sección.

## SIS-B-05 · Entregable 5 (análisis de sensibilidad): su única API la consumían los tests

- **Qué se difirió:** nada, ya. `parametros_sensibilizables()` existía y solo
  la llamaban los tests; ningún bloque de alcance la declaraba diferida.
- **Por qué:** se cerró en S18 cableándola: la sensibilidad de cada criterio
  `[A]` llega hoy al documento.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/modulos/M11_reporte.py::_sensibilidad_declarada`

## SIS-B-06 · `--plantilla memoria_perfil.html` sobre corrida de expediente

- **Qué se difirió:** nada, ya. La combinación descartaba 13 647 caracteres de
  pendientes mientras el docstring afirmaba que las dos plantillas «comparten
  el contrato de marcadores».
- **Por qué:** se cerró en S18 en las dos direcciones. `substitute` ya reventaba
  cuando la plantilla pide un marcador que M11 no entrega; la dirección
  contraria —M11 calcula contenido y la plantilla no lo imprime— **no se
  quejaba de nada**, porque `substitute` ignora los valores sobrantes. Ésa era
  la que perdía los 13 647 caracteres, y no tenía guardia.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/modulos/M11_reporte.py::_exigir_que_la_plantilla_no_pierda_contenido`

## SIS-B-07 · `CriterioPendienteError.mensaje_gui` no tiene consumidor de producción

- **Qué se difirió:** conservar la propiedad sin cablearla.
- **Por qué:** es el único objeto ejecutable que fija la redacción que
  `CLAUDE.md` manda para esta excepción, y cablearla **degradaría** lo que la
  GUI muestra hoy: seis columnas (clave, etiqueta, concepto, fuente, fases,
  puntos) por la vía del `Bloqueo`, contra un solo dato. Además esa vía no es
  la más rica de dos: es la **única**. Lo comprobé vaciando el `valor` de los
  46 criterios y de todos los datos de sitio: `cli.correr` devuelve su informe
  sin levantar nada, con los bloqueos archivados. Ningún `CriterioPendienteError`
  alcanza el `except ErrorProyecto` de la ventana, porque los tres únicos sitios
  que lo levantan —`criterios_adoptados.valor`, `datos_sitio.valor` y
  `GeometriaCabezal.exigir_ancho_talon`— cuelgan todos de etapas envueltas por
  `_etapa`. (Sí corre otro código fuera de `_etapa` —`correr_cabezal` llama a
  `condicion_normativa_cabezal`, y varias fases piden `externos.valor`—: la
  conclusión se sostiene, pero decir «lo único que corre fuera de `_etapa` es
  `cargar_puntos`» era describir mal el archivo.)
- **Qué haría falta:** un consumidor que necesitara la frase corta y no el
  tablero. Hoy no existe y no se ve de dónde saldría.
- **Dónde vive:** `src/modelos.py::mensaje_gui`

> **Defecto contra `CLAUDE.md`, corregido en S19.** La cláusula
> `CriterioPendienteError` de la taxonomía decía «La GUI la muestra como
> "falta declarar: `<clave>`"», y la GUI muestra algo estrictamente más rico.
> Quien leyera la constitución sin leer el código creería que la ventana
> imprime una sola línea.

## SIS-B-08 · `PeriodoRetorno.exigir_anios` no tiene llamador

- **Qué se difirió:** conservar la guardia sin consumidor.
- **Por qué:** es la única sentencia ejecutable del invariante «un TR ausente
  no se sustituye». `anios` está anotado `Optional[int]`; sin la guardia, el
  consumidor que llegue escribirá `tr.anios or 35`, que es el default
  silencioso que `CLAUDE.md` llama el peor error posible. Los cinco accesos de
  producción tratan el `None` y ninguno necesita el entero, porque el paso que
  sí lo necesitaría —«Tc.py + IDF con el TR de Fase 2», Sec. 1.1— ocurre fuera
  de este programa.
- **Qué haría falta, y es dos cosas:** (1) un consumidor, que aparecerá el día
  que el cálculo hidrológico entre al programa; (2) **un discriminante en
  `PeriodoRetorno`**. La guardia distingue mal sus dos ramas: `anios` es `None`
  por Familia C (falta el dato: `DatoFaltanteError('Q_m3s')`, correcto) y por
  punto fuera de alcance (es un puente: correspondería
  `DisenoNoFactibleError`, como en `M1_clasificacion.exigir_alcance`). Hoy no
  hay con qué separarlos sin oler el texto de `fundamento`, y el orden que M1
  documenta —`exigir_alcance` antes de leer el TR— deja la segunda rama fuera
  del camino. **La decisión sobre `exigir_anios` está cerrada; este límite
  queda declarado y sin cerrar**, y no se puede cerrar sin tocar el modelo, que
  no es trabajo de esta fase.
- **Dónde vive:** `src/modelos.py::exigir_anios`

## SIS-B-09 · Constantes `NUMERAL_*` de módulo declaradas y nunca leídas

- **Qué se difirió:** nada, ya. Son ocho, no siete.
- **Por qué:** se cerró en S12 con un censo declarado y su razón.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/modelos.py::NUMERALES_DE_SECCION_SIN_LECTOR`

## SIS-B-10 · `legacy/Tc.py`: sin importadores, sin tests, sin barrido y sin estatus

- **Qué se difirió:** conservar un archivo de más de mil trescientas líneas y
  185 literales prohibidos que nadie importa, nadie prueba y ningún barrido
  recorre. (Eran 1320 antes de que esta sesión le añadiera su encabezado de
  estatus; los 185 literales sí siguen siendo 185, medidos con el detector del
  propio repositorio.)
- **Por qué, y no es nostalgia:** **no es código muerto, es otro programa.**
  La §1.2 de `docs/hoja_de_ruta_alcantarillas_v8.md` lo nombra por su nombre en
  la fila del caudal —«Caudal de diseño Q | m³/s | Tc.py + IDF con TR de Fase
  2»—, de modo que Q entra al calculador como columna del CSV y este archivo es
  la herramienta que la produce, aguas arriba y fuera de la corrida. Borrarlo
  dejaría al expediente sin la herramienta que produce una columna obligatoria.
  Sus literales están exentos **por directorio**, con la razón escrita y
  verificada por un test que barre el AST del repositorio buscando
  importadores: si alguien lo importa, la exención cae en rojo.
- **Qué haría falta, dicho entero porque no es inocuo:** tal como está
  commiteado **no corre aquí**. `matplotlib` es import de nivel superior y no
  está en `requirements.txt` (ni debe estarlo: no es dependencia del software
  calculado), y `plantilla_memoria.html`, que su encabezado anuncia «junto a
  este archivo», no existe en el repositorio. Para volver a ejecutarlo hacen
  falta las dos cosas. Para **borrarlo**: que la §1.2 deje de nombrarlo como
  origen de Q, o que su procedimiento entre al calculador.
- **Dónde vive:** `tests/test_sin_literales.py::DIRECTORIOS_FUERA_DEL_BARRIDO`

> **Defecto contra `CLAUDE.md`, corregido en S19.** La §GUI ordenaba «Leer esos
> archivos antes de escribir GUI», mandando a un programa que ya no se puede
> importar y cuyos ocho componentes están los ocho extraídos: `Tooltip` y
> `MarcoScroll` son el mismo código movido a `gui/componentes.py`,
> `CampoValidable` es su `_campo_validable` con la validación al escribir que
> pide la Sec. 4.3, y el patrón de plantilla `%%` vive en
> `M11_reporte.PlantillaHTML`.

## SIS-C-06 · `barrido()` solo recorría `src/`

- **Qué se difirió:** nada, ya. `cli.py` (8 literales) y `gui/app.py` (151)
  quedaban sin vigilancia.
- **Por qué:** se cerró en S16 metiéndolos al barrido con una regla estrecha y
  declarada para la capa de presentación.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `tests/test_sin_literales.py::CAPA_DE_PRESENTACION`

## SIS-C-11 · El barrido solo miraba `.py`

- **Qué se difirió:** nada, ya. Las dos plantillas bajo `src/` quedaban fuera.
- **Por qué:** se cerró en S16 con una regla propia para las plantillas.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `tests/test_sin_literales.py::PLANTILLAS`

## SIS-C-12 · El ejemplo de uso de M1 daba luces sin la salvedad que sí lleva el test

- **Qué se difirió:** nada, ya, **y el hallazgo se quedaba corto**. No era solo
  que el ejemplo diera las luces sin decir de dónde salen y con ids del fixture
  presentados como si fueran cruces reales: es que **no ejecutaba**. Llamaba a
  `clasificar_puntos` con dos de sus tres argumentos y abortaba en el primer
  punto con `CriterioPendienteError` sobre
  `umbral_area_quebrada_importante_ha`.
- **Por qué:** un ejemplo que no corre es peor que no tener ejemplo, porque el
  lector culpa a su entorno.
- **Qué haría falta:** nada para M1, y de paso se cerró más de lo que la ficha
  pedía. La primera versión de esta ficha decía que «los otros doce bloques
  `Uso` son fragmentos a propósito» — **y era falso**: los de `M0_carga` y
  `M10_espaciamiento` corren enteros. Era la misma especie de defecto que
  SIS-C-12 denuncia —una razón escrita que nadie ejecutó antes de escribirla—,
  cometida al cerrarlo. Hoy la suite **ejecuta los tres que se sostienen
  solos**, y un segundo test hace crecer la lista si alguien arregla otro. Los
  que quedan sí son fragmentos —parten de un `resultado` o un `material` que
  el llamante ya tiene—, medido ejecutándolos, no declarado.
- **Dónde vive:** `tests/test_M1_clasificacion.py::test_el_ejemplo_del_docstring_de_M1_ejecuta_y_da_los_TR_del_fixture`

## SIS-D-08 · `clase_sitio` es el único `[A]` con valor y sin sensibilidad

- **Qué se difirió:** nada, ya, **y el hallazgo se resolvió cambiando la
  pregunta.** El archivo estaba confesando el problema sin sacar la
  consecuencia: la razón escrita de por qué no declaraba sensibilidad era que
  «declarar un rango de clases alternativas sería fijar la respuesta antes de
  resolver la pregunta».
- **Por qué:** un valor que no puede declarar rango porque la pregunta no está
  resuelta **no es una elección: es un hecho que falta**. `clase_sitio` dejó de
  ser `[A]` y pasó a `[S]` sin valor, con `trazabilidad` en lugar de
  sensibilidad — que es exactamente la regla que separa las dos etiquetas en
  `CLAUDE.md`. Hoy: etiqueta `[S]`, `valor=None`, y la memoria declara que
  **no se ha ejecutado ninguna lectura**.
- **Qué haría falta:** el ensayo. La trazabilidad ya dice cómo se reproducirá
  la lectura cuando exista.
- **Dónde vive:** `src/criterios_adoptados.py::clase_sitio`

## SIS-D-09 · `datos_sitio.py` no tenía guardia al importar

- **Qué se difirió:** nada, ya. `DatoSitio(trazabilidad='', etiqueta='A')` se
  construía sin error mientras el homólogo de criterios lo rechazaba.
- **Por qué:** se cerró en S15 con la guardia simétrica.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/datos_sitio.py::_coherencia_de_datos_sitio`

## SIS-D-12 · `v_max_hdpe` y `v_max_tmc` sin ancla `vacio_verificado`

- **Qué se difirió:** nada, ya.
- **Por qué:** se cerró en S14 consolidando las afirmaciones negativas.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/criterios_adoptados.py::v_max_tmc`

## SIS-E-02 · M9 usaba `DatoInvalidoError` para validar argumentos internos

- **Qué se difirió:** nada, ya. Cuatro `DatoInvalidoError` validaban strings
  que produce el propio código: un fallo de programa presentado como problema
  del expediente.
- **Por qué:** se cerró en S16 separando las dos clases de fallo.
- **Qué haría falta:** nada. Cerrado. La razón vive en el bloque «POR QUÉ ESTE
  MÓDULO VALIDA ARGUMENTOS INTERNOS CON `DatoInvalidoError`», encima de las
  cuatro funciones que nombra.
- **Dónde vive:** `src/modulos/M9_cabezal.py::fs_requerido`

## SIS-E-04 · El único `raise` de la GUI valida un campo tecleado con `ValueError`

- **Qué se difirió:** conservar el `ValueError`, que **no** es de la taxonomía
  `ErrorProyecto`.
- **Por qué:** el campo lo teclea el usuario y el error se atrapa tres líneas
  más abajo, en sus dos llamadores, para pintarlo en el panel. Subirlo a la
  taxonomía lo haría viajar al informe como problema del expediente, que no lo
  es: es un renglón vacío en una caja de texto.
- **Qué haría falta:** nada. Es la decisión, y está fijada por un test que la
  rompería si alguien cambia el tipo sin tocar los dos llamadores.
- **Dónde vive:** `gui/app.py::_interpretar_valor_declarado`

## SIS-F-17 · Un test que no invocaba código de producción

- **Qué se difirió:** nada, ya. Reescribía la fórmula y se comparaba consigo
  mismo; contaba en el total y no protegía nada.
- **Por qué:** se cerró en S16 haciéndolo llamar a producción.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `tests/test_M3_hidraulica.py::test_pendiente_que_produce_v_objetivo_de_cp3`

## SIS-F-19 · El `ValueError` de `escribir_valor_en_archivo` y los criterios multilínea

- **Qué se difirió:** nada, ya. El patrón de la regex no alcanza a los dos
  criterios de valor multilínea, y ese `ValueError` era lo único que impedía
  escribirles un escalar encima.
- **Por qué:** se cerró en S16 ejercitando el patrón sobre los dos casos.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `tests/test_criterios_adoptados.py::test_la_escritura_permanente_se_niega_ante_un_valor_multilinea`

---

# Parte II — Lo que S19 encontró al escribir este registro

Tres cosas que ninguna de las tres auditorías nombra y que aparecieron al
verificar las veintidós fichas contra el código de hoy. Se anotan aquí porque
son de la misma especie —una decisión que el código toma y no dice— y porque
el sitio donde un revisor las buscaría es este.

## `M9_cabezal.combinaciones()` prometía un consumidor que no existe

- **Qué se difirió:** conservar la función sin llamador de producción.
- **Por qué:** las tres combinaciones (Resistencia I, Servicio I, Evento
  Extremo I) son `[N]` y esta función es su única forma ejecutable. Que la
  memoria las declare es una fase que no está escrita, no una llamada que
  falte.
- **Qué haría falta:** que M11 imprima las combinaciones vigentes, que hoy no
  imprime.
- **Matiz que hay que leer con esto**, o parece una contradicción: el registro
  normativo **sí la nombra** —las tres filas de `T_MP_COMBINACIONES` llevan
  `uso=Usada(por=(…, "M9.combinaciones"))`, y la ventana emergente se lo
  muestra al proyectista. No es una promesa incumplida: ese campo dice **qué
  símbolo lee la tabla**, no que una corrida pase por él, y esta función es en
  efecto la que lee la transcripción de esas etiquetas.
- **Dónde vive:** `src/modulos/M9_cabezal.py::combinaciones`

> Su docstring afirmaba «es la que M11 usa para declarar QUÉ combinaciones
> rigen», y `M11_reporte` no la referencia: sus únicos llamadores son cuatro
> tests. Es la misma forma de prometer un consumidor que el proyecto ya
> desterró en `ControlEntrada.HW_sobre_D` (SIS-B-02).

## La premisa de SIS-A-08 se había sustituido por otra premisa falsa

- **Qué se difirió:** nada. Es una corrección.
- **Por qué importa:** SIS-A-08 retiró de `MD.py` la frase «M5 todavía no
  existe en el repositorio» y la sustituyó por «la importación perezosa evita
  además un ciclo de importación en el arranque». **Eso también es falso:** M5
  importa `criterios_adoptados`, `constantes_normativas`, `modelos`, M2, M8 y
  `tolerancias`, y ninguno vuelve a MD. Sustituir una premisa falsa por otra no
  cierra el hallazgo: le cambia el hecho. La premisa original, además,
  sobrevivía **verbatim** en el docstring de `tests/test_MD.py`.
- **Qué haría falta:** nada. Cerrado en S19, con guardia.
- **Dónde vive:** `tests/test_MD.py::test_la_premisa_de_que_M5_no_existe_no_vuelve_como_afirmacion`

## Las referencias de prosa del manifiesto eran dos poblaciones, no una

- **Qué se difirió:** el cupo de referencias no verificables del manifiesto.
- **Por qué importa:** «de prosa» significaba «la fila no cita ningún símbolo
  **definido en el archivo de destino**», y eso mezclaba la fila que no nombra
  nada (hueco real) con la que nombra un símbolo que el archivo **usa** sin
  definir (verificable: basta exigir que el bloque de destino lo nombre). Al
  separarlas aparecieron dieciséis referencias desviadas que nadie buscaba,
  entre ellas dos nombres que el código ya no tiene.
- **Qué haría falta para llegar a cero:** que cada fila del manifiesto nazca de
  un objeto del registro normativo con id estable. Hoy el registro cubre C11,
  C12 y C02; el resto sigue en prosa. Quedan 32 filas sin identificador.
- **Dónde vive:** `tests/test_manifiesto_citas.py::test_toda_fila_que_cita_un_identificador_lo_nombra_en_su_destino`

---

# Parte III — Los seis parciales que la fase F5 heredó

`Plan_Fases` reclama a esta fase seis hallazgos que otras sesiones dejaron en
**Cerrado parcial**: cuatro normativos y dos de la suite. Ninguno se cierra
borrando código ni escribiendo prosa, y por eso conviene decir, uno por uno,
**qué falta exactamente y de qué clase de trabajo es**. Un «parcial» sin esa
frase se lee como pereza; con ella se lee como lo que es: una espera con
condición escrita.

## NOR-E060-02 · El acero en dos caras entre 200 y 250 mm

- **Cerrado:** la lógica. `ESPESOR_DOS_CAPAS_REFUERZO = 0.200` m (Art. 14.3.2)
  y `M9.requiere_refuerzo_dos_capas`: entre 200 y 250 mm el muro lleva dos
  capas aunque el acero por temperatura vaya en una cara, que es lo contrario
  de lo que la memoria imprimía.
- **Abierto:** la nota no tiene llamador de producción, porque su insumo es el
  espesor y el espesor sale de `predimensionamiento_cabezal`, que **sigue
  siendo un vacío declarado** (verificado hoy: `valor=None`, etiqueta `[A]`).
  Está censado en `M9_cabezal.FUNCIONES_SIN_CONSUMIDOR` junto a las otras
  siete funciones del num. 9.4, con la misma razón.
- **Qué haría falta:** que el proyectista declare el predimensionamiento del
  cabezal, y que `diseno_flexion_corte` deje de detenerse en
  `NotImplementedError`. Ninguna de las dos es trabajo documental.
- **Dónde vive:** `src/modulos/M9_cabezal.py::FUNCIONES_SIN_CONSUMIDOR`

## NOR-HDS-05 · Las tres condiciones de uso de h_o

- **Cerrado:** dos de las tres se **evalúan punto por punto** —los límites
  HW/D < 0.75 y HW/D < 1.2, como `H_O_HW_SOBRE_D_MIN` y
  `H_O_HW_SOBRE_D_CAUTELA`— y viajan a la memoria del punto junto a su HW.
- **Abierto:** la tercera —que el barril fluya lleno en la mayor parte de su
  longitud— no se puede evaluar sin un perfil de la lámina de agua. Está
  transcrita y **declarada como no evaluable** en
  `H_O_CONDICION_APLICACION`, y M4 lo dice en el punto de uso.
- **Qué haría falta:** el procedimiento de barril parcialmente lleno del
  Cap. III del HDS-5. Es implementar un método hidráulico, no redactar.
- **Evaluado en I1 (2026-09-12): el procedimiento SÍ es transcribible.** Se
  abrió el Cap. III de la 3.ª edición (fuente `HDS5_3ED`,
  `normas/hif12026.pdf`) y el paquete completo para la sesión que lo
  implemente —numeral y página de cada pieza (3.12/PDF 94 con la Ec. 3.7;
  3.24/PDF 106; Secc. 3.5), qué implementar en M4 y por qué M5 no cambia,
  y por qué los dorados no se fabrican— quedó ESCRITO en el bloque de
  comentario que precede a `H_O_CONDICION_APLICACION`, que es donde se va a
  pisar. La implementación es sesión propia con plan mode: toca
  `M4.control_salida`, que es motor validado.
- **Reabierta en EXT-0 (2026-09-20)** con argumento nuevo (`EXT-M-02`: el
  aviso convivía con un punto aceptado mientras el paso imprimía NO_CUMPLE,
  SIS-A-07; `EXT-M-01`: «M5 no cambia» era falso). La v8 §4.3 decidió
  «método no evaluable» por vía `Bloqueo`, diferible en perfil y no en
  expediente. **Cerrado parcial en EXT-3:** bloqueo, régimen y velocidad de
  salida (`modelos.MetodoNoEvaluableError`, `servicio._compuerta_metodo_h_o`,
  `ResultadoHidraulico.V_salida`); quedaba sólo el perfil (EXT-3b / E-A).
- **CERRADA en E-A (2026-09-21):** el perfil por paso directo existe
  (`M4.perfil_lamina`, `modelos.PerfilLamina`, pasos 4.3c/4.3d; siete citas
  nuevas de las págs. 3.12 y 3.36–3.38). Las tres condiciones se evalúan: la
  primera se mide (fracción llena contra `'fraccion_llena_mayor_parte'` [A]),
  bajo HW/D < 0.75 el HW es el del remanso o gobierna la entrada, y V1/V2
  salen del perfil. Lo que sigue sin hacer a propósito: Parte XXVIII (EA-01
  a EA-07).
- **Dónde vive:** `src/modulos/M4_control.py::perfil_lamina`

## NOR-PRO-04 · La norma a la que se difiere la verificación del TMC

- **Cerrado:** la **atribución**, y desde N1 **verificada**: ASTM A796/A796M-13
  está en `normas/` y en el registro (`fuentes.ASTM_A796`), y su num. 22.1
  nombra a A807/A807M como práctica de **instalación** (`ASTM_A796.22.1`).
  `DIS-HR-A807` quedó RESUELTA y la fila de la Fase 8 de la v8 corregida.
- **Cerrado también en I1 la mitad transcribible:** la relación
  diámetro/corrugación (`ASTM_A760.T1`, `AASHTO_M36.T6`, `CORR-TAMANOS-TMC`).
  El criterio sigue vacío a propósito: quién especifica el producto es el
  proyectista.
- **Cerrado en N1 lo que la fuente SÍ trae, y cambió de naturaleza lo que
  no:** la mitad (2) esperaba de A796 «la tabla de calibre por altura de
  cobertura», y **esa tabla no existe** (`SIN_TABLA_CALIBRE_POR_COBERTURA_A796`,
  con su ámbito): el espesor es la *salida* del procedimiento de los num. 7 a
  10 (`ASTM_A796.8.1.1.2#SELECCION`) y la cobertura mínima sale del num. 11.1
  (`ASTM_A796.11.1#PISOS`). Transcrito entero y verificado por imagen: las
  siete tablas SI de propiedades seccionales del catálogo (`ASTM_A796.T3` a
  `T17`), la carga viva por cobertura (`ASTM_A796.6.2.2.1`), los límites del
  factor de flexibilidad (`ASTM_A796.10.2`, `.10.3`) y las cargas por eje
  (`ASTM_A796.11.1`).
- **Abierto:** la mitad TMC sigue **sin valor**, ya no por fuente ausente sino
  porque cerrarla es **implementar el procedimiento** en M8
  (`seleccionar_clase_calibre`), con caso patrón y con los `[A]` que el
  procedimiento pide. La mitad concreto sigue esperando las Tablas 1 a 5 de
  M 170M. Y el hueco del generador hallado en I1b: `manifiesto.py` no emite
  las `CorrespondenciaDeTablas`.
- **Qué haría falta:** para el TMC, una sesión de cálculo que implemente los
  num. 6 a 11 de A796 sobre las tablas ya transcritas (dicho en el plan
  ANTES, con caso patrón y en commit propio); para el concreto, transcribir
  las Tablas 1 a 5 de M 170M por imagen.
- **Dónde vive:** `src/criterios_adoptados.py::clases_producto_por_relleno`

## NOR-ANA-03 · La analogía de embocadura del HDPE

- **Cerrado:** la comparación que la ficha reclama está **declarada**. La fila
  alternativa (`Circular CM / Headwall`) vive en `sensibilidad`, y
  `verificacion_pendiente` declara la comparación completa entre las dos filas.
- **Corregido en I1b, y contra la propia ficha:** hasta I1b la declaración
  copiaba de NOR-ANA-03 que la fila adoptada da un HW **menor** (dirección
  insegura). La verificación adversarial la **midió** con las constantes del
  propio criterio y los dominios de M4, y la dirección es la contraria en los
  tres regímenes vigentes: no sumergida manda K (0.0098 > 0.0078), sumergida
  la diferencia 0.0019·q*²−0.02 es positiva en todo su dominio (q* ≥ 4.0; el
  cruce en q* = 3.245 queda fuera, que es donde la ficha evaluó), y la
  transición es una recta entre dos extremos donde el concreto ya es mayor.
  La ficha además enumera «c y Y ambos menores» cuando 0.0398 > 0.0379. El
  defecto se reportó **contra la ficha NOR-ANA-03** en el tracker; la
  adopción resulta conservadora en dirección, pero se sigue sosteniendo en el
  argumento físico, no en ese margen.
- **Abierto:** no se cambia de fila, y es una decisión, no una omisión. La
  adopción se sostiene en el perfil de pared en la boca —argumento físico que
  la ficha no refuta—, no en un margen de seguridad; elegir la fila del metal
  por su resultado sería sustituir una analogía por otra.
- **Qué haría falta:** el detalle constructivo de la embocadura. Es contenido
  de planos.
- **Dónde vive:** `src/criterios_adoptados.py::hds5_embocadura_hdpe`

## SIS-F-01 · La GUI y sus tests de contrato

- **Cerrado en S19, y es la parte que faltaba dentro de la frontera:** las
  tres decisiones de `gui/app.py` que nadie ejercitaba —el estado con que se
  rotula cada criterio, la leyenda de etiquetas y de dónde saca la tabla el
  valor que muestra— tienen test, más las dos guardias de encabezado
  (pestañas y exportaciones contra el árbol; el campo validable).
- **Cerrado después, por etapas que conviene fechar:** S20 abrió el primer
  test de **ventana real** (la corrida de perfil de punta a punta, que
  construye `gui/app.py` entero), S21 dejó escrito cómo conseguir Tk en el
  contenedor, S22 sumó la ayuda de entrada y G1 la selección real de la
  pestaña 2. **I1 cerró el último archivo que faltaba:**
  `gui/ventana_normativa.py` no se construía nunca bajo Tk —los apoyos
  anteriores lo evitaban a propósito y lo decían—, y el smoke de
  `tests/apoyo/gui_smoke_normativa.py` construye la app, puebla las cuatro
  pestañas con el CSV de expediente y abre y cierra la emergente de un
  criterio `de_tabla` por el camino del ratón.
- **Abierto, en dos frentes que conviene no confundir.** (1) De **alcance**,
  medido en I1b: el smoke abre la emergente de UN criterio `de_tabla`, de
  modo que de las cuatro caras que `VentanaNormativa._construir` despacha
  solo la cara TABLA se construye bajo Tk; `_pintar_rango`,
  `_pintar_catalogo`, `_pintar_campo` y el camino de `_declarar` siguen sin
  construirse nunca en la suite — el mismo riesgo que el docstring del test
  describe, en las otras tres caras. (2) De **entorno**: los cuatro tests de
  ventana se **saltan** donde no hay Tk ni servidor X —la clase de saltos que
  CLAUDE.md censa—, de modo que una integración continua sin entorno gráfico
  sigue sin ejecutarlos.
- **Qué haría falta:** infraestructura de CI con entorno gráfico
  (instalar `python3-tk` + `xvfb`), no un test más.
- **Dónde vive:** `tests/test_gui_contrato.py::test_la_ventana_normativa_se_construye_y_se_cierra_de_verdad`
  (el smoke que lanza es `tests/apoyo/gui_smoke_normativa.py`; los cuatro
  tests de ventana comparten el `skipif` de `_interprete_con_ventana`).

## SIS-F-13 · Los módulos de cálculo sin caso patrón

- **Cerrado en S19 una de las tres razones:** `test_M5_verificaciones.py`
  consume ya CP-3 por la cadena de producción entera —catálogo de M2, Manning
  de M3, umbral de M5—, sin fabricar ningún dorado. Y la regla de `CLAUDE.md`
  «todo módulo de cálculo se contrasta contra `casos_patron`» **dejó de vivir
  solo en la constitución**: la ejecuta una guardia con la lista de exentos
  declarada, que además falla si un exento deja de serlo.
- **Cerrado también en C7 el de M8**, y conviene decirlo aquí porque esta
  ficha decía tres: la FLOTACIÓN no necesitaba ninguna de las fuentes
  ausentes y `CP10_FLOTACION_MARCO` le dio a M8 su caso patrón, así que M8
  **salió de la lista de exentos** (el comentario de la guardia conserva el
  motivo viejo y por qué dejó de cubrir al módulo entero;
  `seleccionar_clase_calibre` sigue sin dorado: por M 170M Tablas 1-5 sin
  transcribir y, desde N1, por el procedimiento de A796 sin implementar —la
  fuente ya está, la tabla que se esperaba de ella no existe—).
- **Cerrado también en N2 el de M2, en dos tercios y sin fabricar nada:**
  `CP11_SERIES_NOMINALES` es la serie de diámetros nominales TRANSCRITA de
  las normas de producto —la del TMC desde I1 (`ASTM_A760.T1`,
  `AASHTO_M36.T6`) y la del HDPE desde N2 (`AASHTO_M294_TRAD.T7.2.2`, leída
  de la **traducción no oficial** de M 294-11 que entró en `normas/`, sin
  firma)—, y `test_M2_material.py` contrasta `siguiente_diametro` contra
  esas tablas y no contra la fórmula (conflicto #7). M2 **salió de la lista
  de exentos**; el tercio que sigue sin dorado —la serie del concreto, porque
  AASHTO M 170M-04 Tablas 1 a 5 no están transcritas (OCR inutilizable; se
  leen por imagen en una sesión propia)— está censado en el propio fixture
  (`CP11_SERIES_NOMINALES['concreto_reforzado'] is None`, con test).
- **Abierto:** M10 sigue sin caso patrón, y M2 en su tercio del concreto.
  **No es pereza de la fase de tests:** fabricarles un dorado sería inventar
  el valor de referencia, que es exactamente lo que prohíbe el conflicto #7
  del plan. M11 no cuenta: es el módulo de reporte y no le corresponde dorado
  numérico.
- **Qué haría falta:** para el tercio de M2, transcribir por imagen la
  columna «Internal Designated Diameter, mm» de las Tablas 1 a 5 de M 170M-04
  y añadirla a CP11; para M10, no una norma sino el expediente vial. Están en
  la §15 del plan, y ahora también en la guardia, con su fuente concreta.
- **Dónde vive:** `tests/test_guardias_de_la_suite.py::SIN_CASO_PATRON`

---

# Parte IV — Un hallazgo nuevo que la suite no defendía

## MAT-D1 estaba corregido y no lo defendía ningún test

- **Qué se difirió:** nada — es lo contrario. MAT-D1 («V2 se evalúa con la
  rama `n_min`, que es la estimación alta: el conservadurismo queda
  invertido») se corrigió hace varias sesiones y **la corrección no la
  defendía ningún test**. Al escribir el caso patrón de M5 se mutó
  `v2_velocidad_minima` de vuelta a `resultado.V_erosion` y la suite entera
  quedó en verde: 1497 tests.
- **Por qué era invisible:** todos los tests de V2 usaban `_resultado(V=...)`,
  que fija **las dos ramas al mismo número**. Con las dos iguales, la rama que
  se lea da igual y la mutación no cambia nada.
- **Qué haría falta:** nada para MAT-D1 — el test nuevo separa las dos ramas a
  los dos lados del piso (la ventana que el propio docstring de la función
  describe, S entre 3.55e-5 y 6.01e-5) y mata la mutación. Lo que sí queda
  abierto es la pregunta general: **cuántas otras correcciones cerradas están
  sin defender**. Esta salió por casualidad, al escribir otra cosa; no hay
  barrido que las busque.
- **Dónde vive:** `tests/test_M5_verificaciones.py::test_v2_decide_con_la_rama_de_n_MAXIMO_y_no_con_la_de_erosion`

---

# Parte V — Los tres símbolos que C1 introdujo sin consumidor

La sesión **C1** (abstracción `Seccion`) creó tres cosas que hoy no llama
nadie. No son residuo: las tres existen por una razón y las tres tienen fecha
de consumidor —**C4**, la sesión que implementa `SeccionRectangular`—. Se
fichan aquí porque `CLAUDE.md` lo exige para *todo* objeto que se conserva sin
consumidor, y porque el precedente propio del repositorio es exactamente éste:
`M9_cabezal.combinaciones()` prometía un consumidor que no existía, y
`PeriodoRetorno.exigir_anios` lleva su ficha desde S19.

Las tres las descubrió la auditoría adversarial del cierre de C1, no la
sesión: C1 las escribió, documentó su razón en el código y **no abrió ficha**,
que es literalmente el defecto que este registro existe para impedir.

## C1-01 · La mitad por tirante de `Seccion` no tiene consumidor

- **Qué se difirió:** conservar `area(y)`, `perimetro(y)`,
  `ancho_superficial(y)` y el auxiliar `theta_desde_tirante(y)` sin llamador.
- **Por qué:** es el vocabulario de la Sec. 4.1 y la vía que
  `SeccionRectangular` usará directamente, porque en la rectangular el
  parámetro propio **es** el tirante. Retirarla ahora obligaría a C4 a
  reabrir el protocolo.
- **Qué haría falta:** que C4 la consuma desde `SeccionRectangular`. Y ojo:
  **no puede consumirla desde M3 ni M4**, que es la trampa que la regla
  vinculante **#12** de `docs/ruta_familia_c.md` §6 documenta con su
  medición — en la circular esta vía está mal condicionada y en los extremos
  de `bracket_llenado()` devuelve `0.0` exacto para P y para T.
- **Dónde vive:** `src/modelos.py::Seccion` (el docstring lleva la medición) y
  `src/modelos.py::SeccionCircular.theta_desde_tirante`

## C1-02 · `SeccionCircular.etiqueta()` no la invoca ningún módulo — **CERRADA en C8**

- **Qué se difirió:** conservar el método sin llamador.
- **Por qué:** es el miembro del protocolo con el que la memoria nombrará la
  sección cuando haya dos formas que distinguir. Con una sola forma, M11
  imprime `D` y no necesita preguntarle a la sección cómo se llama.
- **Qué haría falta:** nada ya. Hacía falta que M11 lo consumiera; era de **C8** (la memoria del
  marco), no de C4: hasta que la memoria tuviera que decir «marco 1.20 × 0.90 m»
  en vez de un diámetro, no había a quién preguntárselo.
- **Cómo se cerró (C8):** M11 lo invoca en **cinco** sitios —el titular de la
  combinación adoptada, la tabla de iteraciones, los dos textos de «último
  escalón evaluado» y la fila del cuadro resumen—, la CLI en **tres** (el
  volcado de texto y las dos claves del JSON), MD en **cinco** (los tres
  motivos de descarte y el mensaje del escalón sin verificaciones) y la GUI en
  **uno** (la columna del tablero de puntos). La ficha se conserva, marcada
  como cerrada, porque la razón que la abrió es lo que explica por qué el
  método existió tres sesiones sin llamador; borrarla dejaría el método sin
  historia.
- **Dónde vive:** `src/modelos.py::etiqueta`

## C1-03 · `Geometria.y_sobre_D` se quedó sin consumidor de producción

- **Qué se difirió:** conservar la propiedad, y **conservar su nombre**.
- **Por qué:** el número sí llega al entregable, pero **por otra expresión** —
  `ResultadoPunto.y_sobre_D`, que es `y_normal / self.D` —, y V1 calcula la
  suya por tercera vez dentro de `M5_verificaciones.v1_borde_libre`. Los
  consumidores de *esta* propiedad son los tests del motor. El nombre se
  conserva porque es el de la columna `y_sobre_D` del CSV entregable
  (`M11_reporte.COLUMNAS_RESUMEN_CSV`) y el que la suite pinea.
- **Qué haría falta:** unificar las **tres** expresiones del mismo número en
  una. No es de C1 (mover el número era exactamente lo prohibido) ni de C4;
  quien las toque tiene que saber que son tres y que hoy no hay nada que
  avise si divergen.
- **Dónde vive:** `src/modelos.py::y_sobre_D` — el de `Geometria`. Las otras
  dos expresiones del mismo número están en `ResultadoPunto.y_sobre_D` (mismo
  archivo) y en `src/modulos/M5_verificaciones.py::v1_borde_libre`

## C1-04 · `M3_hidraulica.tirante` se quedó huérfana

- **Qué se difirió:** conservar la función sin llamador.
- **Por qué:** la llamaba `M3.geometria` antes de C1; desde que `geometria`
  delega en `seccion.geometria_en()`, nadie la llama — ni producción ni la
  suite, que sí contrasta sus dos hermanas `area` y `perimetro`. Se conserva
  porque las tres nombran juntas, en el lenguaje de la Sec. 4.1, lo que la
  sección devuelve de una vez, y romper el trío por asimetría de llamadores
  deja peor la lectura del módulo.
- **Qué haría falta:** o un consumidor, o retirarla con sus dos hermanas
  cuando alguien decida que `geometria()` basta. **La primera redacción del
  comentario que la acompaña le inventó un consumidor** («la API pública que
  la suite contrasta»), que es el antipatrón de esta misma parte del
  registro; está corregido y medido en el propio comentario.
- **Dónde vive:** `src/modulos/M3_hidraulica.py::tirante`


---

# Parte VI — Lo que C5 dejó puesto y todavía sin consumidor

C5 abrió el catálogo del cajón (Familia C). Dos cosas quedan **escritas y sin
leer** hasta la sesión siguiente, y las dos por la misma razón: el frente que
las consumiría es de otra sesión, y adelantarlo habría metido en C5 cambios de
M8 y de M11 que su propio alcance excluye.

## C5-01 · La clave `"cajon"` de `factores_carga_aashto` no tiene consumidor

- **Qué se difirió:** dejar declarada la fila de γ_EV del marco —«Pórticos
  rígidos»— **sin cablear el consumidor que la leería**.
- **Por qué:** la fila la fija la regla vinculante #8 de
  `docs/ruta_familia_c.md` §6, no esta sesión, y el consumidor
  (`M8.factores_carga_flotacion`) indexa por `material.tipo.value`, que **no
  distingue un marco de un tubo de concreto**. Generalizar ese índice es el
  punto 2 del brief de C7. Mientras tanto un marco recibe la fila del tubo;
  el mínimo de las dos es 0.90, de modo que **el número de V7 no cambia** y lo
  que sale mal es la fila que la memoria imprime. Está escrito entero en el
  comentario de la clave y en el docstring de `M5.v7_flotacion`, que es quien
  consume la función.
- **Qué haría falta:** que `M8.factores_carga_flotacion` elija la clave por
  **forma** y no por material, como ya hace `M4.criterio_ke_de`. Es C7.
- **Dónde vive:** `src/criterios_adoptados.py::factores_carga_aashto`

## C5-02 · `ke_entrada` sigue declarando un número y `ke_entrada_cajon` una fila

- **Qué se difirió:** **no** migrar `ke_entrada` (el circular) al patrón de
  clave de fila que C5 estrenó para el marco.
- **Por qué:** en el bloque «Box, Reinforced Concrete» de la Tabla C.2 el
  coeficiente **no identifica la fila** —el 0.2 está en tres y el 0.5 en dos—,
  y por eso el criterio del marco declara la clave. En el bloque «Pipe,
  Concrete» esa presión no existe hoy, `ke_entrada` tiene valor y consumidor, y
  **cambiarle la forma por simetría es mover un dato de proyecto que nadie
  pidió mover**. La asimetría, con su medición, está escrita en el comentario
  de la vista derivada.
- **Qué haría falta:** migrar `ke_entrada` a una clave de `KE_HDS5_C2` y
  retirar la rama de `M4.ke_declarado` que devuelve los dos rótulos vacíos.
  ~~No tiene sesión asignada; es una limpieza, no un defecto.~~
- **Reabierta en EXT-0 (2026-09-20): pasa de limpieza a DEFECTO.** `EXT-V-02`
  midió que `ke_entrada` acepta −50 (y `'texto'`, `True`, `[1,2]`) con la
  procedencia «proviene de la fila» de la Tabla C.2: `--declarar
  ke_entrada=-50` produce `HW_salida_m = −7.668` con el punto dimensionado y
  cero incumplidas, y `PC-02`/`PC-34` añaden que sin ventana ni dominio la CLI
  declara la tupla `(0, 5)` por una coma. La forma por número es lo que hace
  posible que la procedencia mienta; la forma por clave de fila —la que ya usa
  `ke_entrada_cajon`— no puede. Sesión: EXT-1 si cabe, si no EXT-6.
- **EXT-1 (2026-09-20) cerró la mitad de VALIDACIÓN y difiere la MIGRACIÓN a
  EXT-6.** Lo que ya no puede pasar: `ke_entrada` lleva la ventana de la Tabla
  C.2 derivada de `KE_HDS5_C2` (0.2–0.9), `M4.perdida_carga` y `M4.ke_declarado`
  rechazan con `DatoInvalidoError` todo ke que no sea un real finito con
  `ke >= 0`, `declaracion.declarar_desde_tabla` guarda `valor_de_la_celda` y
  exige nota si el valor declarado difiere de la celda, y la memoria imprime
  «DIFIERE de la celda (0.5)» en vez de «proviene de esa fila». Lo que sigue
  abierto es la FORMA: `ke_entrada` declara un número y `ke_entrada_cajon` una
  clave de fila, y `M4.ke_declarado` conserva la rama que devuelve los tres
  rótulos vacíos. No cupo en EXT-1 porque migrar la forma mueve la memoria del
  corredor de referencia (la procedencia del ke de tubo pasaría a imprimir fila,
  agrupación y bloque) y ese cambio de salida pertenece a la sesión que rehace
  la forma de los criterios (EXT-6), no a la de guardias sin cambio de contrato.
- **Dónde vive:** `src/constantes_normativas.py::KE_HDS5_C2`


---

# Parte VII — Lo que C6 revisó y decidió NO cablear

## C6-01 · `sucs_fundacion` se carga, se valida y no la lee ningún módulo

- **Qué se difirió:** conectar la columna al num. 4.1.1.3.4 a), que recomienda
  el marco según la calidad del suelo de fundación. Es el **segundo**
  consumidor plausible; el declarado, `c_phi_fundacion`, es de expediente y lo
  consumen E1–E5 de la Sec. 9.3, que esta CLI no ensambla.
- **Por qué:** **el vacío es del Manual, no del proyecto.** La fuente
  recomienda el marco según esa calidad y **no define «mala calidad»** — sin
  umbral, sin lista de grupos SUCS, sin remisión a otra norma —, de modo que el
  mapeo SUCS → «mala calidad» habría que **inventarlo**, que es el peor error
  posible de este repositorio. La medición, con el literal verificado y su
  página, está en `COND-MARCO-SUELO-MALA-CALIDAD`, que por eso lo resuelve como
  `NoEvaluable` y no como un dato pendiente. Dos razones más, medidas en §15.5:
  el párrafo es **recomendación atenuada** y no soporta una regla dura (un
  `Fundamento` con `verbo=OBLIGA` lo rechazaría T11); y **no cambiaría ningún
  resultado**, porque en la Familia C el tipo ya lo fija la Sec. 2.3.
- **Qué haría falta:** una fuente que respalde el mapeo — la candidata peruana
  es la **E.050**; la tabla de calidad por CBR del Manual de Suelos num. 4.5.4
  **no sirve**, clasifica la *subrasante* y no el suelo de *fundación* — y,
  con ella, el cambio de esquema de `_Columna.criterio_destino`, que hoy admite
  **un solo** destino. **Abrir el criterio «para declarar el vacío» no vale**:
  un `Criterio(valor=None)` entraría en `criterios_sin_valor()` como vacío
  bloqueante que nadie tiene obligación de contestar, y `opcional=True` está
  definido para el criterio que refina un valor que la norma ya fija — aquí no
  hay valor normativo por defecto.
- **Dónde vive:** `src/variables_entrada.py::sucs_fundacion`

## C6-02 · `_Columna.criterio_destino` admite un solo destino

- **Qué se difirió:** decidir si el campo pasa a tupla.
- **Por qué:** es **cambio de esquema**. Hoy `sucs_fundacion` apunta a
  `c_phi_fundacion` y no hay un segundo consumidor cableado (ver C6-01), de
  modo que **nada lo fuerza todavía**: cambiarlo ahora sería mover el contrato
  que la memoria y la GUI leen para explicar dónde aterriza cada columna, sin
  un caso que lo pida. C6 lo midió y lo deja **propuesto**, que es lo que su
  brief pide: proponer y parar.
- **Qué haría falta:** el primer segundo consumidor real. Cuando llegue, hay
  que decidir entre tupla (una columna alimenta varios criterios) o cambio de
  destino (la columna cambia de dueño), y arrastrar `test_variables_entrada.py`.
- **Dónde vive:** `src/variables_entrada.py::criterio_destino`

# Parte VIII — Lo que C8 dejó puesto, cerró o retiró

C8 abrió el canal de las discrepancias a la memoria y retiró `ResultadoPunto.D`.
Las tres fichas de abajo son lo que ese trabajo dejó **sin consumidor de
producción o sin cerrar del todo**, más la única retirada. La cuarta cosa que
C8 tocó de este registro está arriba: **C1-02 quedó CERRADA** — el
`Seccion.etiqueta()` que llevaba tres sesiones sin llamador tiene ahora
catorce, y su ficha lo dice sin borrarse.

## C8-01 · Nueve de 38 `Parte.cita_id` anuncian una cita que nadie transcribió

- **Qué se difirió:** transcribir las nueve citas, y con ellas hacer que el
  registro EXIJA que toda `Parte.cita_id` exista.
- **Por qué:** transcribir una cita es leer el PDF y verificar numeral, página
  impresa y texto literal (regla 8 de `CLAUDE.md`), y son nueve repartidas en
  cinco documentos. Inventarlas para poner el barrido en verde sería
  exactamente el defecto que este proyecto persigue. **Lo que sí se hizo es
  darles el primer consumidor y hacerlas visibles**: la memoria imprime «cita
  anunciada y NO transcrita al registro» en vez de un ancla rota, y el censo
  queda con trinquete decreciente.
- **Por qué no lo vio nadie antes:** la validación del registro mete estos ids
  en el conjunto de `referenciadas` —para que una cita no cuente como
  huérfana— y **nunca comprobó que existieran**. Un id que solo sirve para
  excusar a otro de estar huérfano no se comprueba jamás. Se destapó al
  darles el primer consumidor de verdad.
- **Qué haría falta:** las nueve transcripciones, con su test de página. Al
  llegar a cero, la rama del aviso en `M11._ancla_de_parte` sobra y el
  registro puede pasar a rechazar la parte sin cita.
- **Dónde vive:** `src/normativa/registro.py::partes_sin_cita_transcrita`

## C8-02 · `Registro.discrepancias_abiertas` sigue sin consumidor de producción

- **Qué se difirió:** cablearla, o retirarla.
- **Por qué:** es el **censo completo** de lo abierto, y la memoria no consume
  censos: consume lo que ESTA corrida toca (`discrepancias_que_tocan`). Son dos
  destinatarios distintos —el manifiesto es para quien audita el código, la
  memoria para quien sustenta— y fundirlos volcaría las diez abiertas en la
  memoria de un perfil que difiere seis de ellas. Su consumidor legítimo es el
  test T20 y un futuro informe de estado del expediente, no la memoria.
- **Cuidado con leer su docstring viejo:** decía «M11 las imprime» y era falso
  —M11 no importaba el módulo—. C8 lo corrigió en el sitio. Es el caso de
  manual de la primera lección de §4.5: **una declaración en un docstring no
  imprime nada**.
- **Qué haría falta:** un informe de estado del expediente, distinto de la
  memoria de cálculo, que enumere lo abierto con independencia de la corrida.
- **Dónde vive:** `src/normativa/registro.py::discrepancias_abiertas`

## C8-03 · `Registro.discrepancias_de_cita` solo lo usa el propio registro

- **Qué se difirió:** nada; se declara para que no se lea como código muerto.
- **Por qué:** es el índice inverso `cita_id → discrepancias`, y hoy su único
  llamador es `discrepancias_que_tocan`, en el mismo archivo. Se conserva
  **separado y público** porque es la operación que un revisor querrá hacer a
  mano —«¿qué discrepancias hay sobre este numeral?»— y porque tenerla aparte
  es lo que deja el filtro (`viva` + `tocada`) legible en una sola expresión.
  Es la ventana normativa, y no la memoria, su segundo consumidor plausible.
- **Qué haría falta:** que `gui/ventana_normativa.py` la consulte al pintar una
  cita, que es lo que hoy hace solo con las erratas atadas a una tabla
  (`_texto_de_errata` publica cinco de las veintitrés).
- **Dónde vive:** `src/normativa/registro.py::discrepancias_de_cita`

## C8-04 · `M2.diametro_exterior` — se RETIRÓ, y por qué no se difirió

- **Qué se difirió:** nada. Se anota la **no** deferencia, porque la pregunta
  «¿por qué esto no está en este registro?» tiene respuesta y conviene que
  esté escrita donde se buscaría.
- **Por qué:** `diametro_exterior(*, material, D)` devolvía `D + 2t` y **no
  tenía ninguna llamada** —medido sobre el AST de M7, M5, M8, MD, la CLI y su
  propio módulo, y tampoco en tests—, pese a seguir importado en dos módulos y
  citado en cinco docstrings, que es como un símbolo muerto sobrevive a la
  revisión: se lee como si alguien lo usara. Aquí viven los objetos que se
  CONSERVAN sin consumidor **por una razón**, y éste no tiene ninguna: en un
  marco no hay «un diámetro exterior» —hay `Bc = B + 2t` y `B'c = H + 2t`, que
  son números distintos— y una función que recibe un escalar solo puede
  devolver uno de los dos. C5 la usó para el `Bc` de la cobertura mínima y le
  entregó el **canto** donde iba el **ancho**, que es la regla vinculante #9
  arrastrada dos veces. Lo que la sustituye son los tres miembros del
  protocolo `Seccion` que C7 añadió.
- **Qué haría falta:** nada. Retirada en C8, con la razón completa en el
  bloque de comentario que quedó en su lugar.
- **Dónde vive:** `src/modulos/M2_material.py::siguiente_diametro` (el
  comentario que la sustituye está justo encima de ese símbolo)

# Parte IX — Lo que VC1 cerró, y la mitad que dejó abierta

## VC1-01 · La deuda de §13 se cierra por MITADES, y la otra mitad sigue diferida

- **Cerrado:** la mitad del requisito de la Sec. 2.3 que habla del **borde
  libre del canal**. `M5.vc1_borde_libre_canal` compara `cota_entrada + HW`
  contra `cota_coronacion_canal − borde_libre_canal` y emite `Verificacion`
  con veredicto y margen en metros. Corre en la posición de V5 —que en esta
  familia no aplica— y es OBLIGATORIA también a `--alcance perfil`: sin la
  columna o sin el criterio se detiene, no devuelve «no evaluable».
- **Abierto:** la mitad que habla de la **rasante hidráulica**. VC1 acota el
  NIVEL que el agua alcanza; no mide en cuánto la obra levanta el pelo de agua
  del canal respecto del que tendría sin ella. Un punto puede cumplir VC1 con
  holgura y haber elevado la rasante hidráulica en una fracción apreciable del
  calado. Y VC1 mide **en la sección del cruce**: no acota cuánto se extiende
  el remanso aguas arriba, donde el canal puede tener la coronación más baja.
- **Qué haría falta:** dos datos que hoy no son columna de la Sec. 1.2. (1) La
  **geometría trapecial del canal** en cada cruce —ancho de solera y talud— y
  su **n de Manning**, con los que se calcula su tirante normal y, restándolo,
  la alteración. El levantamiento ya midió la sección trapecial, de modo que
  lo que falta de verdad es transcribirla a columnas y conseguir el n. (2) Un
  **perfil de remanso** aguas arriba, que es el mismo dato que V5 pide en las
  otras familias y que ninguna de las dos tiene. Y, aparte de las dos, el
  **borde libre que el propio canal adoptó en SU proyecto** (ANA / Junta de
  Usuarios del Bajo Piura), que sustituiría a la analogía con el badén: si
  fuera mayor que 0.50 m, esta verificación es menos exigente que el proyecto
  del canal.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::NOTA_VC1_LO_QUE_NO_MIDE`
  (la advertencia pegada al veredicto) y `cli.py::DECLARACION_ALCANCE_FAMILIA_C`
  (la declaración entera, una vez por punto)

## VC1-02 · V5 no se difiere en la Familia C: NO APLICA, y VC1 ocupa su hueco

- **Qué se difirió:** nada, y ése es el cambio. Hasta aquí V5 quedaba
  «pendiente para siempre» en la Familia C: se intentaba, fallaba por falta de
  `ancho_derecho_via_m`, y el fallo se anotaba como diferido al expediente. La
  deuda no era diferible porque el dato que la cerraría no habría cerrado
  nada: el umbral de V5 es un ANCHO.
- **Por qué:** V5 verifica que el embalse quede dentro del derecho de vía, y
  esa formulación presupone agua que se **extiende lateralmente** sobre la
  plataforma al remansarse contra el terraplén. En un paso de canal el agua
  sube **confinada** entre las dos coronaciones: su avance no es lateral sino
  vertical contra el labio del canal, y un ancho de derecho de vía no acota
  nada ahí. La preocupación —los terceros— no desaparece: cambia de dirección,
  y es exactamente la que mide VC1. Por eso V5 no se declara «no aplicable» a
  secas sino **sustituida**, con su sustituta corriendo en la misma posición
  de la tabla y con veredicto real.
- **Qué haría falta:** nada para cerrar esto; sí para lo que la sustitución no
  cubre, que es la extensión aguas arriba del remanso (ficha VC1-01). V5
  tampoco la cubría —su umbral era un ancho, no una longitud—, de modo que la
  sustitución no pierde alcance, pero decir que cierra el hueco entero sería
  falso.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::pieza_del_hueco_de_V5`
  (la regla de familia, en un solo sitio y consultada por los dos llamadores)

---

# Parte X — La historia que R2a retiró de las justificaciones del lote de perfil

R2a (plan R, `docs/planes_mejora/02_PLAN_REDACCION_CRITERIOS.md` §R2)
reescribió la redacción de los criterios de nivel de perfil: la narración de
bitácora salió de `justificacion` porque la historia vive en git y aquí.
Estas fichas conservan la parte de esa narración que un revisor futuro
necesita y que no queda escrita en ningún otro registro.

## R2a-01 · `factores_carga_aashto`: el par único descartado, y la dirección que la ficha NOR-PUE-03 invierte

- **Qué se difirió:** nada nuevo; se conserva la razón del cambio de forma
  que la justificación ya no narra. El criterio transcribía un único par EV
  {max 1.35, min 0.90} con etiqueta [C]; ese par no es ninguna fila de la
  Tabla 2.4.5.3.1-2 —mezclaba el máximo del muro con el mínimo de la
  estructura enterrada— y ningún par único podía servir a la vez a V7 y al
  cabezal. La corrección fue el desglose por estructura (cluster C03: MAT-D8,
  MAT-D15, NOR-PUE-03, NOR-PUE-04, NOR-AAS-04).
- **Por qué se escribe aquí:** dos afirmaciones de aquellas fichas no hay que
  repetirlas. NOR-PUE-03 sostiene que usar 0.90 en E2/E3/V7 es la dirección
  insegura, y es al revés: rebajar lo que estabiliza es la dirección
  conservadora (AASHTO LRFD C3.4.1) y el desglose corrige conformidad, no
  seguridad. Y la afirmación «EH en reposo 1.35, sin mínimo declarado» era un
  corrimiento de fila: el N/A es de las paredes ancladas; el reposo lleva
  1.35 / 0.90.
- **Qué haría falta:** nada — cerrado; la lectura vinculante quedó en la
  justificación del criterio, en presente y sin narración.
- **Dónde vive:** `src/criterios_adoptados.py::factores_carga_aashto`

## R2a-02 · `HW_D_max`: V4b estuvo declarado y sin cablear a propósito

- **Qué se difirió:** ya nada; se conserva el porqué de un hueco que en el
  historial se leería como olvido. El chequeo V4b (HW/D máximo) estuvo
  declarado y sin consumidor hasta S14: el conflicto #1 de la matriz de
  auditorías (NOR-HDS-02 frente a MAT-D2 / SIS-A-02 / SIS-B-02) prohibía
  implementarlo mientras la etiqueta del criterio siguiera abierta, porque un
  umbral que rechaza diámetros apoyado en una cita mal leída es peor que un
  umbral que no se evalúa.
- **Por qué se cerró:** primero se cerró la procedencia —el num. 2.2.5 d) del
  HDS-5 describe práctica de agencias y no prescribe HW/D; etiqueta [A]— y el
  cableado a `M5.v4b_relacion_hw_d` vino después, en S14.
- **Qué haría falta:** nada — cerrado.
- **Dónde vive:** `src/criterios_adoptados.py::HW_D_max`

## R2a-03 · `espesor_pared_conducto`: la cifra del código (−33.1 %) no es la de la ficha MAT-D3 (−31.6 %)

- **Qué se difirió:** nada; se fija una divergencia numérica que invita a
  «corregirla» mal. La subestimación del empuje de flotación al usar el D
  interior es −33.1 % bajo la convención del código (D_ext = D + 2·t, con
  t = 0.100 m y D = 0.90 m); la ficha MAT-D3 publica −31.6 % porque supone
  OD = 1.088 m.
- **Por qué:** las dos cifras son coherentes cada una con su convención; la
  que vale en el código es la de su propia convención, y la justificación del
  criterio ya solo lleva esa.
- **Qué haría falta:** nada para esta ficha; el día que la Fase 8 especifique
  el producto, la cifra se recalcula con su espesor real.
- **Dónde vive:** `src/criterios_adoptados.py::espesor_pared_conducto`

---

# Parte XI — La historia que R2b retiró de las justificaciones del lote de expediente

R2b (plan R, `docs/planes_mejora/02_PLAN_REDACCION_CRITERIOS.md` §R2) cerró
la reescritura de estilo con el lote de nivel expediente. Como en la Parte X:
la narración de bitácora salió de `justificacion` porque la historia vive en
git y aquí, y estas fichas conservan la parte que un revisor futuro necesita
y que no queda escrita en ningún otro registro.

## R2b-01 · `clase_sitio`: la dispensa inventada y el [A] que confesaba no ser una elección

- **Qué se difirió:** nada; se conserva la historia que la justificación ya
  no narra. Dos piezas. (1) La redacción histórica del criterio y la §0.5 de
  la hoja de ruta v7 atribuían a AASHTO una dispensa por periodo fundamental
  corto (T ≤ 0.5 s) que permitía clasificar el sitio como si el suelo no
  licuara. El barrido de verificación dio cero coincidencias en las 1905
  páginas de AASHTO LRFD 9.ª ed. (2020): no fue un vacío relleno en
  silencio, fue una autorización normativa inventada — que es peor, porque
  un vacío se ve y una cita falsa se cree. La v8 ya retiró la regla en su
  §0.5. (2) Mientras el criterio tuvo valor fue el único [A] con valor que
  no declaraba sensibilidad (SIS-D-08), con la razón escrita de que declarar
  un rango de clases alternativas sería fijar la respuesta antes de resolver
  la pregunta; esa confesión es la que llevó a reetiquetarlo [S] sin valor.
- **Por qué se escribe aquí:** la justificación conserva íntegro el
  argumento presente (las prohibiciones de suponer E o F, el salto
  S5→Clase F que ninguna de las dos fuentes escribe, y la verificación de
  que la dispensa no existe), pero ya no cuenta de dónde venía cada error;
  sin esta ficha, la lección «una cita falsa se cree» quedaba solo en git.
- **Qué haría falta:** nada — cerrado; el pendiente vivo del criterio es la
  medición (Vs30/N/su), declarada en su `resolucion`.
- **Dónde vive:** `src/criterios_adoptados.py::clase_sitio`

## R2b-02 · `cortante_alto_muro_e060_art_11_10_10_2`: el umbral 0.5·φ·Vc era una atribución inventada

- **Qué se difirió:** nada; se conserva la corrección que la justificación
  ya no narra (NOR-E060-03). El criterio decía que el Art. 11.10.10.2 de
  E.060 define un umbral de entrada «del orden de Vu > 0.5·φ·Vc». Verificado
  contra el PDF, el artículo entero es una sola frase y no define umbral
  alguno; el 0.5·φ·Vc existe en E.060 pero en el Art. 11.5.6.1 (pág. 91) y
  para elementos sometidos a flexión, no para muros. Era una atribución
  inventada del mismo tipo que la de NOR-PUE-01.
- **Por qué se escribe aquí:** la justificación conserva los umbrales que sí
  escalonan el régimen de un muro (11.10.10.1 y 11.10.7/11.10.8) en
  presente; la procedencia del error y su ficha correctora son historia y
  viven aquí y en el tracker.
- **Qué haría falta:** nada — cerrado; el pendiente vivo del criterio es la
  demanda Vu, que espera a `procedimiento_flexion_corte_aashto_sec5`.
- **Dónde vive:** `src/criterios_adoptados.py::cortante_alto_muro_e060_art_11_10_10_2`

## R2b-03 · `k_v`: la sensibilidad numérica (0.0, 0.5) retirada, y las tres formas del rango

- **Qué se difirió:** nada; se conserva por qué la `sensibilidad` de `k_v`
  declara dos regímenes y no un rango numérico. El criterio llevó una
  sensibilidad (0.0, 0.5) que se retiró por tres razones encadenadas:
  sugería una libertad que el num. 2.8.1.1.14.2.1 no concede (el cero es
  prescrito, no elegido); su propio comentario no coincidía con su extremo —
  hablaba de 0.5·k_h como escenario alterno, que con la cadena de este
  proyecto vale 0.25 y no 0.5 —; y la hoja de ruta escribe (0, 0.5·k_h),
  que es una tercera forma distinta de las otras dos.
- **Por qué se escribe aquí:** quien vea la tupla declarativa actual podría
  «completarla» con un rango numérico plausible; esta ficha deja dicho que
  ese rango ya existió y por qué se retiró.
- **Qué haría falta:** nada — cerrado; si algún caso reservado del numeral
  se diera en esta obra, el número sería del proyectista y entraría como
  valor del criterio, no como sensibilidad.
- **Dónde vive:** `src/criterios_adoptados.py::k_v`
# Parte XII — Lo que S24 anotó sin abrir

## S24-01 · Las claves externas sin techo, y el punto de decisión de `longitud_m`

- **Qué se difirió:** decidir si las claves de `--datos-externos` que quedan
  fuera de `cli.py::_DOMINIO_DE_CLAVE` necesitan cota, y con ella el **punto de
  decisión de `longitud_m`**. El diagnóstico **está hecho y escrito**; lo que
  se difiere es actuar sobre él. El conjunto no se transcribe aquí ni allí: se
  **calcula** (`set(CLAVES_EXTERNAS) - set(_DOMINIO_DE_CLAVE)`), porque un
  conteo a mano al lado de la colección que cuenta ya envejeció tres veces en
  este mismo bloque.
- **Por qué:** porque de las que quedan fuera **ninguna es una deuda abierta**,
  y eso hubo que establecerlo antes de poder no hacer nada con tranquilidad.
  `categoria_tr` está fuera por construcción (es de `CLAVES_TEXTO`); `Q_m3s`
  está fuera por decisión ya tomada y escrita —techo ausente, guardia en la
  salida de la aritmética—; `luz_m` tiene umbral normativo que **no debe**
  copiarse aquí, porque `LUZ_MAX_ALCANTARILLA` clasifica y no invalida, y
  copiarlo cambiaría el veredicto «es puente, fuera de alcance» por un
  `DatoInvalidoError`; `TW_m` y `L_hidraulico_m` no tienen cota que heredar ni
  que derivar, e inventarla está prohibido.
  `longitud_m` es la excepción y es una **elección**, no un olvido: su cota
  existe, no es constante —es la fórmula de Sec. 7.B— y la puerta que la
  aplica es la que la declaración existe **para no usar**.
- **Qué haría falta:** decidir si `longitud_m` declarada se contrasta contra la
  geometría de su propia fila (validación cruzada de Sec. 1.5, con
  `DatoInvalidoError`) o si se deja como está, por el precedente de `Q_m3s`.
  Lo que **no** haría falta es una guardia de finitud o de signo: las dos
  puertas ya las tienen, y está medido que no es ahí donde pasa. Está medido
  también qué pasa hoy: sobre A-01 de `tests/ejemplo_puntos.csv`, con
  `ancho_plataforma` de 9.60 m, un `longitud_m` declarado de 0.5 m llega a la
  Sec. 7.B y sale `factible`.
- **Dónde vive:** `src/servicio.py::_DOMINIO_DE_CLAVE` (en `cli.py` hasta EXT-9) (el diagnóstico completo, clave
  por clave, en su comentario) y `cli.py::_resolver_longitud` (las dos puertas)

---

# Parte XIII — Lo que N1 dejó sin usuario al resolver la última discrepancia contra la v8

## N1-01 · La vía 3 del canal de discrepancias (`Criterio.discrepancias`) se quedó sin usuario de producción

- **Qué se difirió:** darle a la vía 3 un caso real de producción. `DIS-HR-A807`
  era el único criterio-portador desde I2 (`clases_producto_por_relleno`), y
  N1 la resolvió: con ASTM A796/A796M-13 en `normas/` sus partes llevan cita,
  la fila de la v8 está corregida y una resuelta no se declara (la guardia
  `_verificar_discrepancias` lo impide). Ningún criterio declara hoy una
  discrepancia.
- **Por qué:** porque inventarle una discrepancia a un criterio para que la
  vía tenga usuario es fabricar el defecto que este registro persigue. Es la
  misma decisión que I2 tomó con la vía 2 cuando resolvió `DIS-HR-G-LAUSHEY`,
  y que I3 cerró cuando apareció el caso real (`DIS-HR-FORMAS-HDS5` en el
  paso `de_forma`). La mecánica sigue probada en las dos direcciones con el
  registro, y el censo «ningún criterio declara ninguna» es una aserción
  medida que falla el día que uno la declare.
- **Qué haría falta:** una discrepancia viva cuyo canal natural sea un
  criterio y no un paso ni una cita — y entonces reescribir el test con ese
  caso, no al revés.
- **Dónde vive:** `tests/test_canal_discrepancias.py::test_la_via_del_criterio_existe_porque_V9_no_emite_paso`

## N2-01 · La traducción no oficial de M 294-11 entra como Fuente propia, sin firma en sus citas, y el original sigue ausente

- **Qué se difirió:** firmar (`Verificado`) las citas de AASHTO M 294-11 y
  retirar al original del censo de ausentes. Lo que llegó a `normas/` es una
  **traducción al español no oficial**, sin folio en sus 17 hojas: Fuente
  PRESENTE con la naturaleza en título y nota (`AASHTO_M294_TRAD`, como la
  traducción de ASTM A760), `convive_con` cruzado con el original, que
  **sigue en `FUENTES_AUSENTES`** con `que_desbloquearia` redefinido —citar a
  AASHTO y no a un traductor—, y las cuatro citas SIN FIRMA, censadas en
  `CITAS_SIN_FIRMA_A_PROPOSITO` con el precedente de `HDS5_SI_1985.EC4B#K`.
- **Por qué:** UNA razón, no dos —la primera redacción sumaba «y además es
  traducción», y el auditor adversarial de N2 mostró que choca con el
  precedente—. Sin folio, la paginación es `SinDeterminar` y T6 prohíbe
  firmar una página PDF de una fuente sin paginación medida; un tipo nuevo
  de `Paginacion` («sin número impreso») se descartó porque no habría nada
  que predecir. Ser traducción NO impide firmar: la firma acredita el
  ARCHIVO (`Verificado.sha1_pdf`), no a AASHTO, y la de ASTM A760 va firmada
  por eso; la reserva viaja en la nota, y la exige
  `test_toda_cita_de_la_traduccion_de_M294_lo_dice`. Lo que vigila el
  contenido, en cada corrida con PyMuPDF: T0, T2 y T3, porque el texto SÍ es
  extraíble.
- **Qué haría falta:** el original en inglés. Reverificar 1.1.1, 1.4, 7.2.1
  y la tabla de 7.2.2 contra él, citarlo (con firma si imprime folio), sacar
  las cuatro del censo y cerrar la Ausencia. Ni entonces el tope pasaría a
  `[N]`: es norma de producto extranjera. De leer el numeral salió además
  `DIS-HR-M294-PASO` (la v8 decía «150 mm por encima de 600 mm»; la serie
  tiene el 675), corregida en la v8 y resuelta.
- **Dónde vive:** `src/normativa/fuentes.py::AASHTO_M294_TRAD`

## T1-01 · La vigencia de las ediciones es una marca en la nota, no un campo del esquema

- **Qué se difirió:** el campo `Fuente.vigencia`. Lo que T1 (2026-09-14)
  verificó contra cada emisor —siete ediciones confirmadas, ocho con edición
  posterior publicada, ninguna indeterminable— vive en la `nota` de cada
  Fuente presente detrás de una de las tres marcas de `MARCAS_DE_VIGENCIA`,
  que `estado_de_vigencia` lee, `fuentes_con_eleccion_de_edicion_pendiente`
  deriva y `tests/test_vigencia_fuentes.py` exige en las quince. La elección
  de qué edición rige el expediente es del proyectista y está declarada
  vacía en `criterios_adoptados['edicion_que_rige_el_expediente']`.
- **Por qué:** el esquema no modela «el emisor publica hoy una edición
  posterior a la citada»: `reemplaza_a` mira hacia atrás (lo que ESTA fuente
  sustituye) y `convive_con` exige que la otra Fuente exista en el registro.
  `Discrepancia` sí tiene precedente de cuestión abierta con `gana`
  provisional (`EstadoDiscrepancia.ABIERTA`), y se descartó igual, por dos
  razones: una discrepancia dice qué AFIRMAN dos fuentes sobre un objeto, y
  la vigencia no es una afirmación de la fuente; y un `gana` provisional a
  favor de la citada sería exactamente el default que el prompt prohíbe
  decidir por el proyectista. Es la fila 6 de la tabla de decisiones
  abiertas de `docs/diseno_registro_normativo.md` («cómo se versiona el
  registro cuando salga una edición nueva»): T1 cierra la mitad de registrar
  la vigencia y deja abierta la política de migración de citas. El prompt de
  T1 pedía proponer el campo en el cierre en vez de forzar el esquema, y eso
  es lo que se hizo: la marca es el mínimo que convierte la prosa en algo
  enumerable mientras el campo no exista.
- **Qué haría falta:** una sesión de esquema que añada a `Fuente` un
  `Vigencia(estado, fecha, como, edicion_posterior, resolucion_posterior,
  pendiente_gabinete)`, mueva las marcas a ese campo, haga que
  `estado_de_vigencia` y el manifiesto lean de él y retire la marca de las
  notas. Y, aparte, lo que T1 dejó para gabinete porque ninguna página del
  emisor fue legible desde su entorno: leer la RD 22-2013-MTC/14 (la
  actualización del EG-2013, que probablemente es la que este ejemplar
  imprime como «Revisada y Corregida a Junio 2013»), la RM 217-2026-VIVIENDA
  (la transitoria de la E.030) y el listado de manuales del portal del MTC.
- **CERRADA en EXT-6 (2026-09-20):** `esquema.Vigencia` existe, con
  `acto_aprobatorio` y `derogado_por` (EXT-N-01); la marca salió de las notas.
- **Dónde vive:** `src/normativa/fuentes.py::estado_de_vigencia`

---

# Parte XIV — Lo que I4 midió y dejó sin corregir

## I4-01 · El chequeo dimensional piloto (M3–M5) midió cuatro inconsistencias de presentación y ninguna de valor; PD las cerró sin mover un número, y la extensión del barrido a M6–M10 sigue diferida

- **Cerrado (PD):** las cuatro que I4 midió, sin cambiar un solo número de
  cálculo —la línea base de la Familia C se regeneró y su diff es sólo texto
  de la memoria—: (1) el coeficiente de unidades de Manning es
  `constantes_normativas.K_MANNING_SI = 1.0 m^(1/3)/s`, con el molde de
  `KU_SI` (imperial 1.486 al lado, nombrado y no usado; etiqueta [N]
  declarada), sostenido por la ec. (47) del num. 4.1.1.3.6, que el Manual
  imprime en forma SI sin coeficiente —verificado contra el PDF—; M3
  multiplica por él en vez de esconderlo en `(1/n)` y `F4.MANNING` lo trae
  como `k_n`; (2) el paso 4.2 trae el `D` con que HW/D pasa a HW_entrada;
  (3) el paso 4.3 imprime `D` y `HW/D` (`salida.HW_sobre_D`, el cociente que
  ya juzgaba) sin cambiar qué se compara ni el veredicto, declarado en
  `UMBRAL_JUZGA`; (4) el comentario de `K_FRICCION_SI` dice la derivación que
  cierra (2·32.2/1.486² = 29.164 → 19.63) y no la del «29» redondeado. Los
  dos censos quedaron en cero y se conservan como guardia.
- **Abierto:** (a) `K_FRICCION_SI` sigue sin nombrarla ningún paso: H llega
  al 4.3 como número, y transcribir su fórmula es un paso nuevo con relación
  propia, que PD no abrió (`la_nombra_algun_paso=False` lo mide). (b) El
  barrido NO se extiende a M6–M10 (M6–M9 en el encargo; M10 también emite
  un paso), y el argumento es medido, no el del plan: la corrida de
  referencia emite 119 pasos, todos de M1, M3, M4 y M5, y ninguno de M6–M10
  —los cuatro puntos se detienen en Fases 3-5 (A-01, A-02 y B-01 por
  `CriterioPendienteError`, C-01 por `DatoFaltanteError`), B-01 además en
  Fase 10 por `DatoFaltanteError`, C-01 difiere VC1 por alcance y la Fase 9
  se bloquea en seis pendientes—, de modo que `RELACIONES` para esos módulos
  no tendría nada que medir; y M8 no emite ningún `paso()`. Extenderlo hoy
  sería censar en el vacío.
- **Qué haría falta:** para (a), un paso propio para H en M4 con
  `K_FRICCION_SI` en su sustitución y `la_nombra_algun_paso=True` en el mismo
  commit; para (b), que la corrida de referencia alcance M6–M10 —declarar los
  pendientes de perfil— y entonces escribir sus `RELACIONES` con las dos
  direcciones que ya rigen M3–M5.
- **Dónde vive:** `tests/test_dimensional_piloto.py::INHOMOGENEIDADES_CENSADAS`

---

# Parte XV — Lo que D9 dejó sin usuario al resolver la última discrepancia contra la v8

## D9-01 · La vía 2 del canal de discrepancias (`PasoDeMemoria.discrepancias`) volvió a quedarse sin usuario de producción

- **Qué se difirió:** darle a la vía 2 un caso real de producción. `DIS-HR-FORMAS-HDS5`
  fue el único paso-portador de I3 a D9 (el paso `de_forma` de M4, que habla del
  NÚMERO que sustituye: la forma de la ecuación de control de entrada), y D9 la
  resolvió: la v8 escribe ya la Forma 2, ec. (A.2), con la regla de selección por
  la columna «Equation Form» de la Tabla A.1 (los cinco puntos de §16.19 de
  `docs/ruta_familia_c.md`), y una resuelta no se declara (la guardia de `paso()`
  lo impide). Ningún paso de producción declara hoy una discrepancia.
- **Por qué:** porque el único candidato honesto se midió y no aporta. La otra
  viva, `DIS-AASHTO-GAMMA-EV-12.6.1`, habla de γ_EV en la flotación, y el paso V7
  —que sí se emite en la corrida de referencia— ya la recibe por la vía 1: sus
  `citas_textuales` llevan a propósito las citas de las DOS partes. Declararla
  además por la vía 2 imprimiría el mismo objeto del registro por segunda puerta;
  inventarle a otro paso una discrepancia para conservar el test sería fabricar
  el defecto que este registro persigue. Es la misma decisión que I2 tomó al
  resolver `DIS-HR-G-LAUSHEY` y que N1 tomó con la vía 3 (N1-01). La mecánica
  sigue probada sobre la corrida real en las dos direcciones, y el censo «ningún
  paso declara ninguna» es una aserción medida que falla el día que uno la declare.
- **Qué haría falta:** una discrepancia viva que hable del NÚMERO que un paso
  sustituye y a la que el cruce por cita no alcance —por ejemplo, una que las
  citas del `Fundamento` de ese paso no toquen—, y entonces reescribir el test
  con ese caso, no al revés.
- **Dónde vive:** `tests/test_canal_discrepancias.py::test_la_via_del_paso_quedo_sin_usuario_al_resolver_FORMAS`


---

# Parte XVI — Lo que EXT-0 reabrió y decidió tras el dictamen de la auditoría externa

Fuente: `docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md` y la
cadena `07_CADENA_PROMPTS_EXT.md`. Los IDs `EXT-*` y `PC-*` están de alta en el
tracker desde EXT-0. Las dos fichas anteriores que EXT-0 reabrió con argumento
nuevo —`NOR-HDS-05` y `C5-02`— llevan la reapertura escrita dentro de su propia
ficha, arriba, para no duplicar el símbolo.

## SIS-B-22 · `limpiar_valores_dinamicos` sí tiene caso de uso: abrir una sesión

- **Qué se difirió:** en S16.5 se cerró SIS-B-22 escribiendo en el docstring de
  `limpiar_valores_dinamicos` que **no tiene llamador a propósito**: «una corrida
  de la CLI es un proceso de un solo uso y no necesita borrar todo; la GUI retira
  UNA clave; el consumidor real es conftest.py». Se difirió, sin decirlo, decidir
  qué pasa con los valores dinámicos de una obra cuando se abre la sesión de otra.
- **Por qué se reabre (EXT-0, 2026-09-20):** la premisa era de S16.5 y S17 la
  dejó atrás al crear la sesión JSON (SIS-A-18). `EXT-A-02` midió que
  `restaurar_sesion` es **aditiva**: abrir la sesión B tras declarar en A deja
  las claves de A vivas, `estado_de_sesion()` de B las **persiste**, y una clave
  de B sin procedencia **hereda la de A** — la memoria afirma algo falso sobre
  otra obra. Abrir sesión **es** el caso de uso de vaciar todo, y la ficha no es
  vinculante (no está entre los ocho conflictos).
- **Qué haría falta:** `restaurar_sesion(estado, *, sustituir=True)` que valide
  el candidato en seco, vacíe con `limpiar_valores_dinamicos()` y las
  procedencias, y vuelque sólo lo aceptado; `sustituir=False` como «importar
  decisiones». Sesión EXT-4, junto con el contexto de corrida (`EXT-A-01`).
- **CERRADA en EXT-4 (2026-09-20):** exactamente eso. `restaurar_sesion` valida
  el candidato entero con `criterios_adoptados.verificar_declaracion` —la
  guardia de `establecer_valor_dinamico` en seco, sin escribir—, después
  vacía con `limpiar_valores_dinamicos()` y el libro de procedencias, vuelca
  sólo lo aceptado por el único camino y devuelve `retirados`. «Cargar
  sesión» de la GUI la llama con `sustituir=True`; «Importar decisiones» es un
  botón aparte con `sustituir=False`. El docstring de
  `limpiar_valores_dinamicos` dice ahora que SÍ tiene llamador de producción
  y cuál; `tests/test_ext4_contexto_corrida.py` (casos d, d2, d3, d4) fija que
  abrir la sesión B vacía deja `valores_dinamicos() == {}` y
  `procedencias() == {}`, y que una clave de B sin procedencia no hereda la de A.
- **Dónde vive:** `src/criterios_adoptados.py::limpiar_valores_dinamicos`

## NOR-HID-02 · La cuneta está en la pág. 179 y la memoria sigue imprimiendo 178

- **Qué se difirió:** nada a propósito: `NOR-HID-02` figura «Cerrado» desde S12
  porque el registro (`MC_HHD_CUNETA`) lleva la 179 y el carácter por valor. Lo
  que quedó sin tocar, sin que nadie lo decidiera, fue **lo que la memoria
  imprime**: `NUMERAL_FASE_10`, `Espaciamiento.numeral`, la ficha de
  `long_max_cuneta` y la v8 seguían en 178 (`PC-30`, `EXT-G-03`).
- **Por qué se reabre (EXT-0, 2026-09-20):** un cierre que corrige el registro y
  deja el texto que llega al entregable es un cierre incompleto, y el tracker lo
  daba por entero. La v8 se corrigió en EXT-0 (verificado sobre el PDF: la 178
  es la Tabla Nº 34; el apartado d) con 250 m y 200 m está en la 179).
- **Qué haría falta:** los tres textos del código a 179 y un test que los
  compare con `MC_HHD_CUNETA.pagina_impresa` en vez de repetir el número.
  Sesión EXT-6.
- **CERRADA en EXT-6 (2026-09-20).** `NUMERAL_FASE_10` lee la página de la
  cita (`MC_HHD_CUNETA.pagina_impresa`); `Espaciamiento.numeral` y la ficha
  de `long_max_cuneta` dicen 179 y
  `tests/test_ext6_registro_normativo.py::test_la_pagina_de_la_cuneta_que_imprime_la_memoria_es_la_del_registro`
  los compara con la cita en vez de repetir el número.
- **Dónde vive:** `src/modulos/M10_espaciamiento.py::NUMERAL_FASE_10`

## EXT-V-01 · Un expediente por repositorio; multi-obra es requisito de producto

- **Qué se difirió:** el mecanismo multi-obra: que un mismo despliegue calcule
  dos corredores con sus propios datos de sitio sin editar archivos de código.
- **Por qué:** el hallazgo V-01 de la auditoría externa leía los [S] de La Unión
  en `datos_sitio.py` como «hardcoding indebido». No lo es: es el **diseño
  constitucional** (v8 §0.7 «se declara una sola vez», taxonomía [S] de
  CLAUDE.md, `auditoria_y_ruta_despliegue_v9.md` A.0): el repositorio **es** el
  expediente de una obra, y un [S] con trazabilidad en un archivo versionado es
  más revisable que un campo de formulario. Lo que falta para «herramienta
  general» es un **requisito de producto**, no la corrección de un defecto, y se
  hace en ese orden: primero la enmienda constitucional (CLAUDE.md y v8 §0.7:
  dónde vive un [S] declarado por sesión), después el mecanismo. Radio medido
  por el dictamen: la corrida de perfil no lee ningún [S]; la de expediente sólo
  `PGA_roca_B`; ponerlos a `None` sin enmendar la constitución mata 18 tests en
  5 archivos y no gana nada. **Lo que no hay que hacer:** un objeto `Proyecto`
  que duplique `DatoSitio`/`Criterio`/`Procedencia`, ni vaciar los archivos.
- **Qué haría falta:** `DatoSitio.nivel`, `datos_sitio.establecer_dato_dinamico`
  con trazabilidad obligatoria, `--datos-sitio sitio.json`, sesión formato 3 como
  único lugar del «proyecto actual», y la advertencia cuando `--proyecto` no
  coincide con `corredor_del_proyecto`. Sesión EXT-10, sólo después de EXT-4 y
  EXT-9.
- **CERRADA en EXT-10 (2026-09-21).** Enmienda constitucional primero
  (CLAUDE.md, taxonomía [S]; v8 §0.7) y mecanismo después: `DatoSitio.nivel`
  medido en las dos direcciones (`tests/test_ext10_multiobra.py`),
  `datos_sitio.establecer_dato_dinamico` (replace + `_verificar_dato`,
  trazabilidad y fecha obligatorias, `Derivada` rechazada), `--datos-sitio`
  (`servicio.cargar_datos_sitio`, rechazo entero y en seco), sesión formato
  3 (`src/sesion.py`) como único lugar del «proyecto actual»,
  `ContextoCorrida.datos_efectivos` con origen, y la memoria con «Origen» y
  la advertencia de corredor. Los valores de La Unión siguen en los
  archivos; un proyecto nuevo es `sesion_vacia()`. Parte XXVI.
- **Dónde vive:** `src/datos_sitio.py::establecer_dato_dinamico`

## EXT-G-03 · Las seis fichas de ayuda de claves externas: se llenan, pero sólo por derivación

- **Qué se difirió:** el contenido de `concepto`, `unidad` y `de_donde_sale` para
  las seis claves de `cli.CLAVES_EXTERNAS` que no son columna del CSV, ni dato de
  sitio, ni criterio, y que por eso no están en `variables_entrada.VARIABLES`.
  El docstring de `FichaDeClaveExterna` lo decidió: «prefiere un hueco declarado
  a una frase inventada o sacada de un docstring que puede reformatearse mañana».
- **Por qué (decisión EXT-0, 2026-09-20):** el hueco declarado es honesto, pero
  quien lo mira es justamente la persona que tiene que rellenar el JSON y no sabe
  qué unidad lleva `luz_m` ni de dónde sale `Q_m3s`. La objeción del docstring
  vale contra la prosa a mano, no contra la **derivación**: la fase y el módulo
  que consumen cada clave los mide `variables_entrada._consumo_por_modulo`, y la
  unidad y el origen están en el contrato que `cli` ya exige (`_numero_externo`,
  los `DatoFaltanteError` que dicen de dónde tendría que venir el dato). **Se
  llenan por derivación**: las seis entran a `VARIABLES` como variables de origen
  «dato externo», con concepto y unidad **leídos del código** y la fase medida; lo
  que no se pueda derivar sigue vacío y la ventana lo sigue diciendo. Nunca una
  frase escrita para la ficha.
- **Qué haría falta:** las seis variables en `variables_entrada`, la ficha
  derivándose de ahí y un test que compruebe que ninguna ficha lleva texto que no
  esté en su variable. Sesión EXT-5.
- **CERRADA en EXT-5 (2026-09-20).** Las seis entraron a `variables_entrada`
  como la cuarta población, `Poblacion.DATO_EXTERNO` (`_EXTERNOS`), con la
  fase medida por `_consumidores` donde hay consumidor (`luz_m`, `S_conducto`,
  `categoria_tr`) y declarada donde no lo hay (`TW_m`, `longitud_m`,
  `L_hidraulico_m`, que entran a MD ya resueltas o las lee `cli._fase_10`),
  el dominio de `S_conducto` nombrado contra `dominios.S_CAUCE_MAX` —el mismo
  que `cli._DOMINIO_DE_CLAVE` aplica— y las opciones de `categoria_tr` leídas
  de `modelos.CategoriaTR`. `fichas_de_datos_externos` ya no tiene rama vacía:
  las ocho fichas salen del censo, `tests/test_ext5_forma_gui.py` comprueba
  que dicen letra por letra lo que dice su variable, y la GUI de ayuda retiró
  la etiqueta «sin ficha». El docstring de `cli.py` sigue sin parsearse.
- **Dónde vive:** `src/ayuda_entrada.py::FichaDeClaveExterna`


---

# Parte XVII — Lo que EXT-1 dejó escrito al cerrar las guardias locales

Fuente: prompt EXT-1 de `docs/planes_mejora/07_CADENA_PROMPTS_EXT.md` y el
paso 1 del dictamen. Los tests de aceptación están en
`tests/test_ext1_entradas.py`, uno por ID. Las dos fichas de abajo son las dos
decisiones que la sesión tomó **distintas de lo que el prompt pedía a la
letra**, y por eso se escriben aquí y no sólo en el docstring.

## PC-32 · El umbral de `factor_esviaje` es una tolerancia numérica, no una cota de esviaje

- **Qué se difirió:** cortar el esviaje de **89.9 grados** (factor 573,
  longitud de 10 313 m sobre A-01), que es el caso que el dictamen usa para
  motivar PC-32. La guardia de salida **existe** desde EXT-1 y lanza
  `LimiteNumericoError` con umbral nombrado, pero su umbral es
  `tolerancias.COS_ESVIAJE_MIN` ≈ 3.5e-7 —cos(θ) por debajo del cual el
  redondeo del ángulo en doble precisión mueve el factor más que
  `TOL_UMBRAL_NORMATIVO` en relativo—, o sea θ > 89.99998°. El 89.9 pasa.
- **Por qué:** porque cualquier umbral que atrape 89.9° es un **valor de
  proyecto**, no una tolerancia: no hay norma en `normas/` que fije un esviaje
  máximo constructivo (ni Sec. 7.B ni EG-2013), y el docstring de
  `factor_esviaje` (MAT-O18) ya había decidido que si el proyecto quiere esa
  cota, «el camino es declararla como criterio [A] con su sensibilidad, no
  escribirla aquí». Escribirla en `tolerancias.py` con nombre de tolerancia
  sería la misma cota disfrazada. Lo que sí es numérico —y se derivó, no se
  eligió: `(π/2)·ε/TOL_UMBRAL_NORMATIVO`— es dónde 1/cos deja de estar
  determinado por el dato, y eso es lo que la guardia mide. El caso del
  dictamen sigue **visible**: la longitud absurda llega a la memoria y G2 la
  contrasta contra la cota del receptor, como MAT-O18 escribió.
- **Qué haría falta:** un criterio `[A]` de nivel perfil con el esviaje máximo
  que el proyecto acepta construir, su ventana y su fuente técnica ([C] si
  alguna guía lo fija), leído por `factor_esviaje` con `valor_si_declarado` para
  no mover la línea base mientras nadie lo declare. Es una decisión del
  proyectista, no de esta sesión.
- **Dónde vive:** `src/tolerancias.py::COS_ESVIAJE_MIN`

## EXT-V-02 · La celda que la procedencia cita se infiere cuando la fila tiene una sola

- **Qué se difirió:** exigir que la GUI y `declarar_desde_tabla` nombren
  siempre la **columna** además de la fila. El prompt pedía guardar
  `valor_de_la_celda` «cuando se nombra una fila y una columna con celda
  escalar»; la ventana de la Tabla C.2 deja elegir sólo la fila (la tabla tiene
  una columna de coeficientes), de modo que con la letra del prompt la
  procedencia veraz no se habría activado nunca en el flujo real.
- **Por qué:** `declaracion._celda_escalar` resuelve la celda también cuando se
  nombra una sola fila que tiene **una sola** celda numérica; con varias celdas
  numéricas (los tres n de la Tabla N.º 09), varias filas o una celda no
  escalar devuelve `None` y la procedencia dice «fila» como hasta ahora. No es
  una inferencia sobre el dato —la celda es la que la tabla imprime— sino sobre
  cuál celda se está citando, y sólo cuando no hay ambigüedad posible. **Y la
  celda sólo se cita cuando lo declarado es un número**: los criterios que
  declaran la CLAVE de la fila (`ke_entrada_cajon`, `embocadura_cajon`) no
  «difieren» de ninguna celda. Lo encontró el auditor adversarial de EXT-1: la
  primera versión comparaba la clave con el coeficiente y rechazaba la
  declaración legítima que hace la ventana de la GUI; hay test de regresión en
  `tests/test_ext1_entradas.py`.
- **Qué haría falta:** nada mientras la ventana siga ofreciendo fila y columna
  por separado; si algún día exige la columna, la rama de una sola celda
  numérica se vuelve redundante y se retira.
- **Dónde vive:** `src/declaracion.py::_celda_escalar`

---

# Parte XVIII — Lo que EXT-2 dejó escrito al cerrar el cluster hidráulico A

EXT-2 cerró EXT-M-03, EXT-M-04, PC-06 y PC-19 (el reparto Q/N dentro de M4, la
recta de transición con `H_c(Q_lo)` y el techo `Q_lleno` del tirante normal).
Dos cosas quedaron sin cambiar a propósito, y las dos se dejan aquí con su
argumento para que nadie las lea como olvido.

## EXT-2-01 · V6 sigue rechazando N > 1 aunque el multicelda ya se resuelve bien

- **Qué se difirió:** cambiar `v6_material_solido_arrastre` (`cumple = celdas == 1`)
  para que un marco de N > 1 celdas pueda **aceptarse**. El prompt de EXT-2 lo
  ataba a que existiera un test multicelda de punta a punta y a que el cambio
  fuera en el mismo commit que el contrato de `Q_celda_m3s`; el test existe
  desde EXT-2 (`tests/test_ext2_multicelda_transicion.py::test_el_multicelda_se_dimensiona_con_Q_sobre_N_y_publica_los_dos_caudales`,
  con verificador inyectado) y el contrato también, y aun así V6 no se toca.
- **Por qué:** V6 no es una propiedad del programa sino una **lectura de la
  fuente**: el num. 4.1.1.3.4 a) del Manual RECOMIENDA sección única sin
  subdivisiones **ante capacidad de arrastre del curso** (`MC_HHD.4.1.1.3.4a#MULTIPLES`,
  fundamento `F3.CELDAS`). Aceptar N > 1 exige saber si ESTE cauce arrastra
  palizada, y ese dato —un [S] por punto, o al menos por corredor— no existe
  en el CSV ni en `datos_sitio.py`. Sin él, la única V6 que no inventa nada es
  la que hoy está: N > 1 no cumple, y quien declare multicelda lo ve como
  incumplimiento con su criterio citado, no como un silencio. Cambiarla a
  «cumple siempre» sería rellenar un vacío; cambiarla a «cumple si no hay
  arrastre» exige el dato. El reparto Q/N (regla vinculante #3) queda
  correcto y visible en la memoria con V6 tal cual: el defecto EXT-M-03 vivía
  en la traza y en el motivo de rechazo, no en el veredicto.
- **Qué haría falta:** una entrada [S] `arrastre_de_solidos` (o equivalente)
  por punto, con su trazabilidad (observación de campo, registro de la Junta
  de Usuarios), y una V6 que la lea: N > 1 cumple sólo sin arrastre
  declarado. Con ese dato, `test_V6_sigue_rechazando_el_multicelda` se
  reescribe en la misma sesión.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v6_material_solido_arrastre`

## EXT-2-02 · El JSON de la CLI no lleva `Q_celda_m3s` ni `numero_celdas` todavía

- **Qué se difirió:** publicar los dos campos nuevos de `ResultadoHidraulico`
  en `cli._diseno_json` (y por tanto en la GUI, que lee el mismo `Informe`).
  Hoy viajan en la memoria HTML —el paso del reparto los imprime— y en el
  objeto, pero el JSON sólo imprime `Q_m3s`, que sigue siendo el del punto.
- **Por qué:** EXT-3 tiene asignada la mitad JSON de SIS-B-18 (`ahogado_por_TW`
  y las banderas de h_o que tampoco llegan al JSON ni a la GUI), y meter aquí
  dos claves nuevas al esquema sería tocar el mismo objeto en dos commits
  consecutivos, que es lo que la regla «un cluster entero por commit» existe
  para evitar. Ningún número publicado está mal: `Q_m3s` es el caudal del
  punto, que es lo que su clave dice.
- **Qué haría falta:** en EXT-3, sumar `Q_celda_m3s` y `numero_celdas` a
  `_diseno_json` junto a las banderas de SIS-B-18, y regenerar la línea base
  declarando que las tres corridas de la CLI ganan dos claves por punto.
- **Dónde vive:** `src/modelos.py::ResultadoHidraulico`
- **Cerrado en EXT-3 (2026-09-20):** `cli._diseno_json` publica `Q_celda_m3s`
  y `numero_celdas` junto al bloque h_o entero y al régimen del barril (trece
  claves nuevas por punto dimensionado); la línea base lo declara archivo por
  archivo en el README de `tests/linea_base_familia_c/` (entrada EXT-3).

# Parte XIX — Lo que EXT-3 dejó escrito al cerrar el régimen del barril y el dominio del método

EXT-3 cerró EXT-M-01, EXT-M-02 y PC-04, la mitad compuerta de PC-27 y la mitad
JSON de SIS-B-18 (régimen del barril, velocidad de salida de HDS-5 3.1.6, la
sexta excepción `MetodoNoEvaluableError` y `Bloqueo` en `modelos.py` con
`tipo` Enum). Tres cosas quedaron sin hacer a propósito, y una de ellas la v8
decía que EXT-3 la haría: se dejan aquí con su argumento y su sesión.

## EXT-3-01 · El 0.75 de V1 y el 0.25 m/s de V2 siguen rotulados [N] aunque la v8 ya dice que el umbral duro es [A]

- **Qué se difirió:** reetiquetar `Y_SOBRE_D_MAX` y `V_MIN` —que
  `constantes_normativas.py` lleva como [N]— a la forma que la v8 §4.1
  enmendada en EXT-0 fija para V1 y V2: **[N] el deber de verificar** (el
  Manual manda «verificar que la velocidad mínima… no produzca sedimentación»
  y tomar en cuenta el borde libre) y **[A] el valor aplicado como umbral
  duro**, porque las dos cifras llegan con «se recomienda» (págs. 77 y 79) y
  aplicar una recomendación como rechazo es una adopción del proyectista, con
  sensibilidad. La nota de §4.1 decía «lo cambia EXT-3».
- **Por qué:** son 56 usos en 13 archivos, y el cambio no es un renombre:
  exige dos criterios nuevos en `criterios_adoptados.py` con ventana,
  `nivel` y `resolucion` (ambos de perfil), mueve la tabla de criterios que
  `test_nivel_medido` contrasta contra las corridas, el bloque
  `UMBRALES_DE_VERIFICACION` que M11 imprime siempre, los manifiestos y las
  fichas de los dos criterios. EXT-3 ya era «la sesión más delicada de la
  cadena» por el régimen del barril, y meter el reetiquetado en el mismo
  commit habría mezclado dos clusters. La memoria SÍ imprime hoy el matiz
  («recomienda, no prohíbe», NOR-HID-10 / NOR-MEM-01): lo que falta es la
  etiqueta, no la honestidad del texto. La v8 §4.1 quedó corregida en EXT-3
  para no prometer lo que el código no hizo.
- **Qué haría falta:** una sesión propia (EXT-3c) que cree los dos criterios
  [A] de perfil —o un solo criterio por verificación con el valor de la
  fuente como default declarado—, mueva las lecturas de M5, deje las cifras
  de la fuente donde están como constantes de tabla (el 25 % y el 0.25 m/s
  SÍ los escribe el Manual: el patrón `F_PGA_TABLA` / `'F_pga'`) y regenere
  los manifiestos.
- **Dónde vive:** `src/constantes_normativas.py::Y_SOBRE_D_MAX`

## EXT-3-02 · V1 y V2 se evalúan con el escenario de TW gobernante, no con los dos

- **Qué se difirió:** la frase que la v8 §1.3 añadió en EXT-0 —«para V1/V2 el
  escenario de TW mayor es el gobernante sólo si el barril llena en los dos;
  si llena en uno solo, se evalúan los dos»— cuando el TW sale de la vía 4 de
  Sec. 1.3 (dos escenarios acotados: salida libre y receptor a sección llena).
  La corrida sigue resolviendo M4 y la Fase 5 UNA vez, con el TW gobernante
  (el mayor), y por tanto con UN régimen del barril.
- **Por qué:** bajo «cumplir en ambos» evaluar el segundo escenario no cambia
  la aceptación. Si con el TW mayor el barril llena, V1 no cumple (y/D = 1) y
  el escalón se rechaza igual; si con el TW mayor no llena, con el menor
  tampoco, y de los dos el mayor es el que puede llevar el control de salida
  a gobernar y dejar V1/V2 pendientes, que ya impide cerrar. Lo que se pierde
  es sólo la impresión del segundo escenario en la memoria, y resolverlo
  exige correr M4 dos veces por escalón y decidir cómo se publican dos trazas
  hidráulicas del mismo punto, que es un cambio de forma de `ResultadoPunto`
  y de M11 y no de EXT-3. **Con una salvedad que la auditoría de EXT-3
  señaló y que no es de aceptación sino de la Fase 6:** la velocidad de
  salida que recibe M6 es la del escenario de TW mayor, y con
  y_c ≤ TW < D esa es la MENOR de las dos (Q/A(TW) < Q/A(y_c)): el d50 sale
  del lado no conservador respecto del escenario de salida libre. Hoy ningún
  punto dimensionado de la línea base cae ahí (los de vía 4 con TW ≥ D no
  dimensionan), y es una razón más para evaluar los dos escenarios en EXT-3b.
- **Qué haría falta:** un `ResultadoHidraulico` por escenario (o la pareja
  dentro de `TWDeterminado`), la Fase 5 evaluada sobre los dos y la memoria
  imprimiendo ambos regímenes; conviene hacerlo junto al perfil por paso
  directo (EXT-3b), que es el que cambia la respuesta bajo control de salida.
- **Dónde vive:** `src/modulos/M4_control.py::regimen_del_barril`

## EXT-3-03 · El bloqueo «método no evaluable» no aparece en el tablero de criterios de la GUI

- **Qué se difirió:** que `M11.criterios_bloqueantes` —el bloque «Criterios
  pendientes que bloquearon una etapa» de la memoria y el tablero de seis
  columnas de la pestaña 4 de la GUI— liste los `Bloqueo` de tipo
  `METODO_NO_EVALUABLE`. Hoy los salta, porque llevan `criterio=None` y ese
  agregador está construido por clave de criterio.
- **Por qué:** es exactamente el hueco que PC-03 describe para el
  `DisenoNoFactibleError` de MAT-D10, y PC-03 no está asignado a EXT-3 ni a
  ninguna sesión de la cadena: cerrarlo aquí sería decidir la forma del
  tablero para dos tipos de bloqueo a la vez sin su sesión. El bloqueo SÍ es
  visible en todo lo demás que lee el `Informe`: `cli.volcar` (bloque
  «Bloqueos» y bloque de alcance), `informe_json` (`bloqueos` del punto y
  `alcance.diferidos`), la tabla «Etapas bloqueadas» y el bloque de alcance de
  la memoria HTML, y el conteo de bloqueos de la pestaña de puntos de la GUI.
  Lo que no ve el proyectista es una FILA en el tablero de criterios, que es
  un tablero de criterios y no de bloqueos.
- **Qué haría falta:** la sesión que recoja PC-03: un tablero de bloqueos sin
  criterio (o una columna «qué hace falta» que admita «otro método» además de
  «declarar»), con la GUI leyendo el mismo agregador que la memoria.
- **Dónde vive:** `src/modulos/M11_reporte.py::criterios_bloqueantes`

---

# Parte XX — Lo que EXT-4 dejó escrito al cerrar el contexto de corrida y las sesiones

EXT-4 cerró EXT-A-01, EXT-A-02, EXT-G-02, PC-07, PC-09, PC-15, PC-16 y
SIS-B-22 (reabierta en EXT-0), y retiró los 27 accesos a `_USADOS` de la
suite: `cli.correr` vacía los registros de uso al entrar y fotografía al
salir un `ContextoCorrida` congelado en `Informe.contexto`, del que leen los
cuatro exportadores; `restaurar_sesion(sustituir=True)` valida en seco,
vacía y vuelca; la GUI invalida el informe en los cuatro gestos que cambian
el estado y valida la sesión entera antes de tocar un campo. Tres cosas
quedaron sin hacer a propósito, con su argumento y su sesión.

## EXT-4-01 · La sesión sigue en formato v2: sin identidad, sin huella del CSV y sin corridas

- **Qué se difirió:** un formato de sesión v3 con migración explícita v2→v3,
  el `csv_sha1` de la corrida, el `informe_json` embebido por corrida y
  escritura temporal + `os.replace`, que es lo que el dictamen pide para E04
  («persistencia con revisiones»). EXT-4 dejó `FORMATO_SESION = 2` y cerró
  PC-16 por la vía estrecha: el esquema v2 se valida ENTERO
  (`gui.app.errores_de_sesion`, tipo por clave) antes de escribir en ningún
  `StringVar`, y los externos ausentes se reponen a vacío.
- **Por qué:** subir la versión del formato en la misma sesión que cambia la
  semántica de «cargar» (de aditiva a sustitutiva) habría mezclado dos
  decisiones que se revisan por separado, y E04 exige además decidir qué es
  una «revisión» de expediente —un objeto que EXT-4 no crea a propósito: el
  prompt dice «no crees un objeto Proyecto»—. El `ContextoCorrida` ya lleva
  las dos huellas (`csv_sha1`, `criterios_sha1`) y `informe_json` las
  publica, de modo que E04 no tiene que inventar dónde guardarlas.
- **Qué haría falta:** la sesión E04 del plan de evolución: formato 3 con
  migración, corridas embebidas (cada una con su `contexto`), escritura
  atómica; y decidir si «Importar decisiones» —que hoy suma sin vaciar y sin
  preguntar— pide confirmación clave a clave cuando pisa.
- **CERRADA en EXT-10 (2026-09-21), salvo la pregunta de «Importar
  decisiones», que queda como ficha EXT-10-02.** `FORMATO_SESION = 3`,
  `sesion.migrar_a_actual` (explícita, por escalones, `ValueError` para lo
  que no se puede migrar), `id`, `csv_sha1`, `corridas` con `informe_json`
  (`sesion.corrida_para_sesion`; la CLI dice si su corrida REPRODUCE o
  DIFIERE de la embebida), y `sesion.escribir_json_atomico` (temporal +
  `os.replace`) en las cuatro escrituras. `ResultadoDeRestauracion` no
  cambió de contrato: `restaurar_datos_de_sitio` lo reutiliza.
- **Dónde vive:** `src/sesion.py::migrar_a_actual`

## EXT-4-02 · El contexto vive en registros de módulo, no en `contextvars`: la GUI sigue corriendo en su hilo

- **Qué se difirió:** pasar los cuatro registros (`_OVERRIDES`, los dos
  `_USADOS`, `_PROCEDENCIAS`) a `contextvars` para que dos corridas
  concurrentes —una GUI en hilo, o un servicio— no compartan la foto. Hoy
  `cli.correr` vacía y fotografía sobre estado de PROCESO, y eso es correcto
  porque la GUI corre el pipeline en el hilo de Tk, de forma síncrona.
- **Por qué:** el dictamen lo dice en su propuesta 1: «si un día la GUI corre
  en hilo, el mismo almacén pasa a `contextvars` sin tocar M2–M10», porque
  los 79 escritores de uso pasan por tres funciones (`ca.valor`,
  `ca.valor_si_declarado`, `ds.valor`). Hacerlo antes de que exista un hilo
  sería resolver una carrera que no se puede medir, y EXT-8 (rendimiento y
  GUI no bloqueante) es donde se decide si la corrida sale a hilo o a
  subproceso —la propuesta 2 del dictamen prefiere el subproceso, con el que
  el aislamiento es gratis y esta ficha se cierra sola—.
- **Qué haría falta:** que EXT-8 decida hilo o subproceso; si hilo,
  `contextvars.ContextVar` por registro con `reiniciar_usos`/`capturar_contexto`
  sobre la variable de contexto, y un test con dos corridas concurrentes
  cuyos `contexto.criterios_usados` no se mezclen.
- **Dónde vive:** `src/servicio.py::capturar_contexto` (en `cli.py` hasta EXT-9)

## EXT-4-03 · Un `Informe` sin contexto no se exporta: no hay caída al estado vivo

- **Qué se difirió:** nada a favor del código viejo, y conviene decirlo
  porque la alternativa existía y se descartó: `Informe.contexto` es
  `Optional` y `None` en un informe armado a mano, y `ContextoCorrida.de`
  levanta `ValueError` en vez de fotografiar el estado del proceso en ese
  momento. El único `Informe` de la suite armado a mano
  (`test_M11_reporte.py::test_un_informe_sin_bloqueos_no_inventa_bloqueantes`)
  no se exporta; los tests que prueban un bloque de M11 suelto arman su foto
  con `cli.capturar_contexto` y se la pasan.
- **Por qué:** una caída silenciosa al estado vivo sería EXACTAMENTE el
  defecto que EXT-A-01 cierra, escondido en el caso raro. Que un informe sin
  corrida no se pueda exportar es lo que la constitución pide de todo vacío:
  detener, no rellenar. Y el registro de usos ya no se puede leer desde M11
  (la guardia AST de `tests/test_ext4_contexto_corrida.py` lo prohíbe), de
  modo que el fallback no tendría siquiera de dónde leer sin abrir la puerta.
- **Qué haría falta:** nada; queda escrito para que nadie lo lea como un
  hueco. Si algún consumidor futuro necesita exportar un `Informe`
  construido fuera de `cli.correr`, tiene que construirlo CON su
  `ContextoCorrida`, no pedir que la capa de reporte lo adivine.
- **Dónde vive:** `src/modelos.py::ContextoCorrida`

---

# Parte XXI — Lo que EXT-5 dejó escrito al cerrar la forma por criterio y el parser GUI–GUI

EXT-5 cerró EXT-G-01, PC-13, PC-14, la mitad de FORMA de EXT-V-02, EXT-V-05
y EXT-V-06 que EXT-1 había dejado abierta, la mitad de pestaña 2 de EXT-V-04
y EXT-G-03: `Criterio.forma` exigida a las 70 claves por `_verificar_criterio`,
un solo parser `gui/componentes.py::interpretar_texto_declarado` para la
pestaña 2 y la emergente, `validar_contra_rango` en forma MAT-D13, la cara de
solo lectura de un `Derivada` en la pestaña 2 y la cuarta población del censo.
Tres decisiones se apartaron de la letra del prompt o merecen quedar escritas.

## EXT-5-01 · Ocho formas, no siete: `serie_de_claves` y la unión de formas

- **Qué se difirió:** ceñir `Criterio.forma` a las siete formas que el prompt
  enumera (`int | float | str | par_ordenado | serie_de_pares |
  dict_con_campos | categoria`). Se añadió una octava, `serie_de_claves`, y
  la posibilidad de declarar la UNIÓN de formas como tupla.
- **Por qué:** `F_pga` declara la tupla de filas de la tabla de factores de
  sitio sobre las que M9 lee la envolvente (`('C', 'D', 'E')`), y eso no es un
  texto, ni una serie de pares, ni una categoría: forzarla en `categoria`
  escondía la estructura que `M9.factor_sitio_desde_tabla` exige (tupla no
  vacía de filas existentes). Y `k_v` admite, por contrato de
  `M9.k_v_declarado`, la cadena del régimen prescrito O el número del caso
  reservado: una forma única habría estrechado un contrato que el consumidor
  ya tiene, y estrechar en la puerta lo que el consumidor acepta es una
  regresión, no una guardia. Las dos ampliaciones son las mínimas que las 70
  claves pidieron; ninguna otra clave las usa.
- **Qué haría falta:** nada; queda escrito para que la familia no crezca sin
  argumento. Si una novena forma aparece, entra con su clave, su consumidor y
  su rama en `_cumple_la_forma`, no como excepción en un test.
- **Dónde vive:** `src/criterios_adoptados.py::FORMA_SERIE_DE_CLAVES`

## EXT-5-02 · La forma va última, y las guardias de los consumidores se quedan

- **Qué se difirió:** retirar de M2, M4, M5, M7 y M9 las guardias de tipo que
  la puerta de declaración ahora hace redundantes (`numero_de_celdas`,
  `progresion_de_cajon`, `_espesor_valido`, `k_v_declarado`,
  `_exposicion_quimica_validada`, las de `condicion_pavimento` y
  `geometria_control_salida`), y colocar `_verificar_forma` en cabeza de
  `_verificar_criterio`.
- **Por qué:** dos líneas de defensa no son duplicación cuando la segunda
  tiene un lector distinto: la puerta protege a quien DECLARA (ValueError,
  contrato SIS-E-05, rótulo rojo en la ventana); la guardia del consumidor
  protege al CÁLCULO de lo que no entró por la puerta —`con_valor` en los
  tests, un `CRITERIOS[...]` pisado a mano, una versión vieja de una sesión— y
  sale como `DatoInvalidoError` con el nombre del criterio. Retirarlas habría
  dejado los tests de consumidor sin objeto y el cálculo confiando en una
  puerta que no es la única vía a `CRITERIOS`. Y la forma se comprueba al
  FINAL porque las guardias anteriores dicen cosas más precisas cuando
  aplican —la ventana de sensibilidad, el par ordenado, el bool—; la forma es
  la última palabra sobre lo que ninguna de ellas mira. Consecuencia medida:
  los tests que probaban una guardia de consumidor con un valor que la puerta
  ya rechaza pasaron a `tests/apoyo/criterios.py::con_valor`, que exige decir
  por qué se esquiva la puerta.
- **Qué haría falta:** nada por diseño. Si algún día `CRITERIOS` deja de ser
  escribible fuera de la puerta, las guardias de consumidor pasan a ser
  aserciones de invariante y pueden simplificarse. Y un hueco MEDIDO que la
  forma no cubre porque es dominio y no estructura: `TW_receptor = -1.0`
  pasa la puerta y `cli.resolver` lo entrega literal a `M3.tw_seccion_1_3`,
  sin segunda línea (auditoría adversarial de EXT-5). Es preexistente y no
  se cierra aquí: pide una ventana numérica en la ficha o una guardia
  MAT-D13 en el consumidor, y decidir cuál es de la sesión que toque V4.
- **Dónde vive:** `src/criterios_adoptados.py::_verificar_forma`

## EXT-5-03 · Once criterios de texto cuyo conjunto cerrado vive en el consumidor, no en `sensibilidad`

- **Qué se difirió:** promover a `categoria` los criterios de valor textual
  cuya ventana de sensibilidad es PROSA y no una tupla de opciones
  (`homogeneidad_serie_fen`, `h_eq_bajo_altura_tabulada`,
  `h_eq_banda_intermedia_borde`, `categoria_refuerzo_aashto`,
  `edicion_que_rige_el_expediente`, `metodo_estabilidad_global`,
  `metodo_transicion_hds5`, `geometria_control_salida`,
  `resguardo_HW_subrasante`, `embocadura_cajon`, `n_manning_cajon`,
  `ke_entrada_cajon`, `PERFIL_SUELO_PRESUNTO`, `clase_sitio`). Llevan
  `forma=str`. (`cortante_alto_muro_e060_art_11_10_10_2` estuvo en esta
  lista hasta que el auditor adversarial de EXT-5 midió que M9 hace
  `float()` sobre su valor: es la CUANTÍA que rige, no un sí/no, y su forma
  es `float`; la ficha decía `dominio="declaracion si/no"` y se corrigió.)
- **Por qué:** `categoria` valida contra `sensibilidad`, que es donde
  CLAUDE.md dice que vive el conjunto cerrado de un criterio, y sólo cinco
  claves lo tienen escrito como tupla de textos (`condicion_pavimento`,
  `origen_cota_fondo_entrada`, `acceso_mantenimiento_v2b`,
  `factor_muro_eleccion`, `F_pga_lectura_columna_extrema`). En las demás el
  conjunto admisible está en constantes del consumidor (`CARTAS_CAJON_TA1`,
  `FILAS_MANNING_CONCRETO`, `H_EQ_BAJO_TABLA_*`, las filas de la Tabla
  5.10.1-1) o no está enumerado en ningún sitio (un método de estabilidad
  global, una edición). Copiar esas listas a `sensibilidad` crearía dos
  fuentes de verdad; inventar la lista donde no existe sería rellenar un
  vacío. Con `str` la puerta rechaza lo que NO es texto ('cero' entra como
  texto y lo rechaza el consumidor con `DatoInvalidoError`, que es un
  problema del expediente y no un fallo de programa), y por eso el conjunto
  de claves que aceptan 'cero' bajó de 53 a las de forma textual, medido en
  `tests/test_ext5_forma_gui.py`.
- **Qué haría falta:** que cada consumidor exponga su conjunto cerrado como
  dato reutilizable y que `sensibilidad` lo referencie sin copiarlo (o que la
  ventana de esas claves pase a `DeTabla` con la fila como clave, como ya
  hacen `embocadura_cajon` y `ke_entrada_cajon`); entonces pasan a
  `categoria` una a una.
- **Dónde vive:** `src/criterios_adoptados.py::FORMA_CATEGORIA`

---

# Parte XXII — Lo que EXT-6 dejó escrito al cerrar el registro normativo

EXT-6 cerró EXT-N-01, EXT-N-02, EXT-N-03, EXT-N-04, PC-23, PC-26, PC-30 y
el resto de EXT-G-03: el DG-2018 entró como `Fuente` presente con sha1,
285 páginas y desfase +1 medidos (284 de 285 páginas) y sus citas del
304.07 y la Tabla 304.09; la guardia «todo PDF de `normas/` es Fuente
presente o está censado» existe y censa dos PDF con motivo; las tres normas
de producto tienen su cláusula de alcance y el marco ya no lleva la norma de
un tubo; la elección de edición se partió en legal y técnica y la vigencia es
un campo; y los textos que la memoria imprime dicen 179, «una geometría y dos
velocidades», la tabla de la v8 §2.2 y las dos bases de la fricción. Tres
decisiones se apartaron de la letra del prompt o merecen quedar escritas, y
una queda diferida a sabiendas.

## EXT-6-01 · El RNGIV no vuelve a `normas/`: lo que se borró no era el decreto

- **Qué se difirió:** restaurar el archivo «Reglamento Nacional de Gestion de
  Infraestructura Vial.pdf» que el dueño borró en `5196dd2` y al que el
  DG-2018 §304.07.01 remite (DS 034-2008-MTC).
- **Por qué:** se recuperó del historial para decidir, y **no era ese
  decreto**: son 12 páginas de El Peruano fechadas el 10 de febrero de 2006,
  dos años anteriores al DS 034-2008-MTC y con otra numeración de artículos
  (su artículo 4 son las definiciones; el DG-2018 cita el artículo 4 como el
  de las autoridades competentes). Restaurarlo habría puesto en `normas/` un
  texto que no es el que la remisión nombra; registrarlo habría firmado
  citas contra un documento equivocado. Lo que falta se censa como falta:
  `RNGIV` entra en `FUENTES_AUSENTES` con lo que desbloquearía (la definición
  jurídica del derecho de vía y quién lo aprueba; ningún número: los anchos
  están en la Tabla 304.09, que sí está).
- **Qué haría falta:** el DS 034-2008-MTC con sus modificatorias, en
  `normas/`, medido como toda Fuente; entonces `DG2018.304.07.01` gana una
  `corresponde_en` y la remisión deja de ser el sustituto.
- **Dónde vive:** `src/normativa/fuentes.py::RNGIV`

## EXT-6-02 · El piso [N] del ancho del derecho de vía está en el registro y no tiene consumidor

- **Qué se difirió:** cablear la Tabla 304.09 y el incremento de 5.00 m del
  304.07.02 a V5. Están transcritos (`DG2018.T304.09`,
  `ANCHO_MIN_DERECHO_VIA_M`, `INCREMENTO_DERECHO_VIA_OBRAS_DRENAJE_M`) y las
  cinco filas dicen `NoUsada` con su razón; las dos constantes están en
  `CONSTANTES_DE_REFERENCIA`.
- **Por qué:** V5 se detiene antes, en dos vacíos que el piso no cierra: el
  método de perfil de remanso es [A] (`remanso_derecho_via`, vacío) y el ancho
  de ESTE corredor es un dato de sitio que no llega por ninguna vía
  (`ancho_derecho_via_m`); y elegir fila exige `clase_de_via`, vacía hasta que
  el estudio de demanda cierre el IMDA. Cablear el piso sin los tres habría
  sido una verificación que compara contra nada. Y el 304.07 no enuncia
  condición hidráulica alguna: F5.V5 sigue en `SIN_FUNDAMENTO` con la razón
  reescrita, porque un `Fundamento` con las citas del DG-2018 convertiría un
  piso de ancho en una verificación hidráulica que la fuente no escribe.
- **Qué haría falta:** el dato `ancho_derecho_via_m` (columna del CSV o
  tablero externo), `clase_de_via` declarada y el método de remanso; con los
  tres, V5 compara el ancho declarado contra el de su fila con el incremento
  de 5.00 m compuesto como diga la `Interpretacion` registrada en
  `DG2018.304.07.02#INCREMENTO` (la norma escribe el incremento y el caso,
  no la composición; el auditor adversarial de EXT-6 encontró la lectura
  «fila + 5» escrita como hecho y se retiró), y su fundamento cuelga de
  `DG2018.304.07.02`.
- **Dónde vive:** `src/normativa/tablas.py::DG2018_T304_09`

## EXT-6-03 · PC-24 no se cierra en EXT-6: su resto es EXT-3-01

- **Qué se difirió:** el prompt de EXT-6 pedía cerrar PC-24. Lo que de PC-24
  quedaba abierto tras EXT-0 —reetiquetar `Y_SOBRE_D_MAX` y `V_MIN` de [N] a
  «[N] el deber de verificar, [A] el valor como umbral duro»— es exactamente
  la ficha EXT-3-01: 56 usos en 13 archivos, dos criterios nuevos de perfil
  con ventana y `resolucion`, la tabla de `test_nivel_medido`, el bloque
  `UMBRALES_DE_VERIFICACION` de M11 y los manifiestos.
- **Por qué:** meterlo en el commit del registro normativo habría mezclado
  dos clusters (el mismo argumento con que EXT-3 lo dejó fuera), y EXT-6 no
  lo puede cerrar «de paso» sin escribir la sesión entera. Se dice aquí para
  que el tracker no lo dé por cerrado con un ID que no lo está.
- **Qué haría falta:** la sesión EXT-3c que EXT-3-01 describe.
- **Dónde vive:** `src/constantes_normativas.py::Y_SOBRE_D_MAX`

## EXT-6-04 · La cláusula de alcance no crea un `Fundamento`: el rótulo del marco es texto del registro, no un paso

- **Qué se difirió:** un `PasoDeMemoria` de Fase 3 que imprima la norma de
  producto con su alcance. El rótulo por (material, forma) lo produce
  `M2.norma_producto_de`, su alcance sale del registro por
  `constantes_normativas.ALCANCE_NORMA_PRODUCTO` (`como_texto` de las citas
  1.1 de M 170M, M 36, A760 y M 294, y de LRFD 12.4.2.4 y 12.11.1 para el
  marco) y viaja al JSON como `alcance_norma_producto`; pero ningún paso lo
  emite y por eso las citas de alcance no cuelgan de un `Fundamento`.
- **Por qué:** un `Fundamento` sin paso que lo imprima es exactamente lo que
  `test_memoria_sustentada` prohíbe (F9.CABEZAL está censado por eso), y M2
  no emite paso al elegir material: elige catálogo, no verifica nada. Las
  citas no quedan huérfanas —T4 las reconoce por el numeral en los textos de
  `constantes_normativas`— y el JSON, el resumen y los tres sitios de M11
  imprimen el rótulo correcto; lo que falta es que la memoria diga, como paso,
  «este material se compra contra esta norma, que cubre esto».
- **Qué haría falta:** un paso de Fase 3 en `M2.catalogo` (o en
  `_pasos_del_marco`) con un `Fundamento` F3.NORMA_PRODUCTO de verbo
  `DEFINE` sobre las citas de alcance; entonces salen de la lista de
  `test_memoria_sustentada` y `consumidores_de_cita` las ve.
- **Dónde vive:** `src/modulos/M2_material.py::norma_producto_de`

# Parte XXIII — Lo que EXT-7 dejó escrito al cerrar el cabezal (cluster C07)

EXT-7 cerró EXT-M-05 (y R95-031, que es el mismo defecto con otra fila),
EXT-M-06 y EXT-M-07: la rama vertical de `cuantia_de_diseno` con cortante
alto ya no devuelve 0.0015 —se detiene en dos criterios [A] de expediente,
el plano del cortante (E.060 11.10.2 / 11.10.1) y el piso de la ec. (11-32)—,
`verificar_cuantia` pregunta lo mismo con el mismo argumento; el empuje
estático y la sobrecarga van con el Ka de Coulomb del Manual de Puentes
(num. 2.4.4.1.5.3, cita nueva, discrepancia `DIS-HR-KA-COULOMB` resuelta) y
CP-9 tiene un bloque C con ángulos no nulos; y `EstabilidadCabezal` lleva
`exigidas`, `pendientes` y un `estable` que sólo es cierto con las cinco
filas presentes y cumplidas. Nada se cableó a la CLI. Tres decisiones quedan
escritas porque se apartan de lo que un lector esperaría.

## EXT-7-01 · La ec. (11-32) del Art. 11.10.10.3 no se implementa: se declara evaluada fuera

- **Qué se difirió:** evaluar en M9 la cuantía vertical mínima bajo el
  régimen de cortante en el plano, ρv = 0.0025 + 0.5·(2.5 − hm/ℓm)·(ρh −
  0.0025) ≥ 0.0025, con tope en la ρh requerida por 11.10.10.1 (E.060
  11.10.10.3, pág. 104; cita `E060.11.10.10.3`).
- **Por qué:** de sus tres entradas el software no tiene ninguna: hm y ℓm
  son geometría que `GeometriaCabezal` no lleva (no tiene longitud), y la
  ρh requerida sale de una demanda Vu que `diseno_flexion_corte` no produce
  (`NotImplementedError`, bloqueado en
  `procedimiento_flexion_corte_aashto_sec5`). Evaluarla con un hm/ℓm
  supuesto sería inventar una dimensión del cabezal. Lo que sí se cierra es
  el defecto: la rama vertical con cortante alto **se detiene** en
  `cuantia_vertical_cortante_alto_e060_art_11_10_10_3` (forma `float`, como
  su hermano horizontal: lo que M9 lee es la cuantía que rige, evaluada por
  el proyectista con hm, ℓm y ρh delante) en vez de devolver el 0.0015 del
  14.3.1, y el docstring ya no afirma lo contrario de la norma.
- **Qué haría falta:** la longitud del cabezal en `GeometriaCabezal` (o en
  `predimensionamiento_cabezal`), y el diseño por corte de AASHTO LRFD Sec.
  5 que produzca Vu y con él la ρh requerida; entonces la ecuación se
  transcribe como fórmula con su cita y el criterio pasa a `Derivada`.
- **Dónde vive:** `src/modulos/M9_cabezal.py::cuantia_de_diseno`

## EXT-7-02 · E6 (excentricidad sísmica) no entra en las `exigidas` por defecto

- **Qué se difirió:** exigir la fila E6 —`verificar_excentricidad_sismica`,
  la ubicación de la resultante bajo sismo del Manual de Puentes— dentro de
  `EstabilidadCabezal.exigidas`, junto a E1..E5.
- **Por qué:** `exigidas` se deriva de las claves de
  `constantes_normativas.FS` (`FS_CODIGO`), que es la tabla de Sec. 9.3 de la
  hoja de ruta, y E6 no es fila de esa tabla: E.050 no la escribe, la trae el
  Manual (num. 2.4.3.11 de la excentricidad, con `gamma_EQ` vacío) y su
  umbral cambia con la condición —sólo existe en la sísmica—. Meterla en la
  tupla por defecto habría hecho que **ningún** expediente estático pudiera
  ser `estable`, y habría escrito en la constitución del tipo una fila que
  la tabla que lo gobierna no tiene. La vía queda abierta y probada:
  `verificar_estabilidad(..., exigidas=EXIGIDAS_SEC_9_3 + ("E6",))` la
  registra como pendiente hasta que alguien la resuelva.
- **Qué haría falta:** decidir, con `gamma_EQ` declarado, si E6 se exige
  sólo en la condición sísmica (entonces `exigidas` deja de ser una tupla
  única y pasa a depender de `CondicionAnalisis`) y cablear
  `presion_contacto_base` → `verificar_excentricidad_sismica` en el
  ensamble, que hoy no existe (`FUNCIONES_SIN_CONSUMIDOR`).
- **Dónde vive:** `src/modulos/M9_cabezal.py::EXIGIDAS_SEC_9_3`

## EXT-7-03 · El Ka de Coulomb se adopta entero, no la «guardia mínima»

- **Qué se difirió:** la alternativa mínima que el prompt ofrecía —dejar
  Rankine en el estático y detener en condición sísmica cuando
  |K_A_rankine − K_A_coulomb| supere una tolerancia nombrada—.
- **Por qué:** habría conservado la base mixta que EXT-M-06 denuncia y la
  habría vuelto **condicional**: con i = β = δ = 0 nada la dispara, y en
  cuanto un ángulo se declara el cálculo se detiene en vez de calcular con el
  coeficiente correcto. La fuente primaria del marco (MP 2.4.4.1.5.3, PERMISO
  verificado) escribe Coulomb y la v8 ya está enmendada (EXT-0), de modo que
  no había nada que proteger con una guardia: había que usar el coeficiente.
  Consecuencia declarada en `empujes_trasdos`: los cuatro ángulos de Sec. 9.2
  son entrada también en condición **estática** y un vacío la detiene, donde
  antes sólo φ lo era. `ka_rankine` se conserva como patrón del caso límite y
  como la forma reducida que la hoja escribía.
- **Qué haría falta:** nada para cerrarla; se registra para que nadie vuelva
  a proponer la guardia como si fuera equivalente.
- **Dónde vive:** `src/modulos/M9_cabezal.py::empujes_trasdos`

## EXT-7-04 · La resultante de Coulomb se toma entera como horizontal: la descomposición queda diferida

- **Qué se difirió:** descomponer el empuje activo de Coulomb (y la
  sobrecarga, que va con el mismo Ka, y el incremento sísmico, que ya estaba
  inclinado) en su componente horizontal P·cos(δ + β) y vertical
  P·sen(δ + β), y llevar la vertical al modelo de cargas de la base.
- **Por qué:** `EmpujesTrasdos` no tiene modelo de cargas verticales del
  trasdós —el único vertical que lleva es la subpresión— y el ensamble de
  estabilidad que las consumiría no existe (`verificar_estabilidad` recibe
  las demandas ya calculadas; `FUNCIONES_SIN_CONSUMIDOR`). Inventarlo en
  EXT-7 habría sido ensanchar el cluster. Lo que sí se hace es **declararlo**
  con su dirección, que no es una: tomar la resultante entera como
  horizontal es conservador para el volteo y el deslizamiento y no lo es para
  la capacidad portante en la parte de la componente vertical que deja de
  cargar sobre la base. Medido en el bloque C de CP-9 (δ + β = 22°): la
  horizontal se sobreestima +7.9 %, y hasta +18.8 % en el extremo de ventana
  (δ = 22.7°, β = 10°). Lo encontró el auditor adversarial de EXT-7: la frase
  «+9.7 % sobre Rankine» era cierta para el coeficiente y engañosa para la
  fuerza horizontal (+1.7 %).
- **Qué haría falta:** un campo de carga vertical del trasdós en
  `EmpujesTrasdos` (con su brazo, porque también resiste el volteo) y el
  ensamble de la normal en la base que lo sume antes de E1 y E3; entonces
  `E_activo` pasa a ser la componente horizontal y el dorado del bloque C
  gana `C_E_h_esperado` y `C_E_v_esperado`.
- **Dónde vive:** `src/modelos.py::EmpujesTrasdos`

# Parte XXIV — Lo que EXT-8 dejó escrito al cerrar el rendimiento y la GUI no bloqueante

EXT-8 cerró PC-10, PC-11, PC-12 y PC-17: `import cli` pasó de 870–930 ms a
125–150 ms (weasyprint, scipy y el censo de `variables_entrada` perezosos);
el PDF sale de la ventana en un SUBPROCESO (`cli.py --sesion … --pdf
--progreso`) con progreso, cancelación, botón apagado con motivo visible y
estado terminal; la memoria dejó de renderizar dos veces el paso 2.1, los
punteros son enlaces y hay un anexo único de fundamentos, citas y umbrales
al que cada punto enlaza, construido por streaming; y la ventana tiene
rueda en X11/macOS, rótulo visible del motivo, Escape y Control-Return.
Cuatro decisiones quedan escritas porque se apartan de lo que un lector
esperaría o porque dejan algo abierto.

## EXT-8-01 · El anexo se decide contra el «de arriba abajo» de la §4.4, y el objetivo de tamaño no se alcanzó

- **Qué se difirió:** el objetivo del dictamen —«< 15 KB y < 10 páginas
  por punto»— y, con él, cualquier recorte adicional de lo que la memoria
  de un punto imprime.
- **Por qué:** la §4.4 de `hoja_de_ruta_correcciones_v12.md` pide que «la
  memoria de un punto se lea de arriba abajo y se entienda sin abrir el
  código». El anexo lo tensiona a sabiendas y se decide así: lo que es DEL
  PUNTO (qué se calcula, con qué valores y su procedencia, el resultado,
  contra qué valor se compara y el veredicto) se queda en el punto; lo que
  es DEL REGISTRO (el argumento del fundamento, la frase literal de cada
  cita, el carácter y la aplicación de cada umbral) se imprime una vez y
  el punto lo enlaza con su numeral en la línea. «Sin abrir el código» se
  conserva —todo está en el mismo documento—; «de arriba abajo» pasa a
  «con una remisión al anexo», que es cómo cita una memoria impresa.
  MEDIDO en el árbol de EXT-8, coste marginal por punto a alcance
  expediente (cuatro puntos contra uno): 54.0 KB y ~20 páginas antes;
  44.6 KB y 14.0 páginas después; la repetición de texto cayó del 44 % al
  7 % de los bytes. Lo que queda no es repetición: la sustitución con la
  procedencia de cada valor (8 KB), las tablas de datos, iteraciones y
  verificaciones (15 KB), los resultados y veredictos. Bajar de 15 KB
  exigiría quitar del punto contenido que la §4.4 pone en el punto, y eso
  no es una decisión de formato. Los techos de
  `tests/test_ext8_rendimiento_gui.py` (`KB_POR_PUNTO_MAX`,
  `PAGINAS_POR_PUNTO_MAX`) se fijaron sobre la MEDIDA, con holgura, no
  sobre el objetivo.
- **Qué haría falta:** una decisión de contenido sobre la memoria del
  punto (por ejemplo, la sustitución sin la procedencia larga, con la
  procedencia en el anexo también), tomada contra la §4.4 y no por debajo
  de ella; y medir el PDF de 40 y 200 puntos después.
- **Dónde vive:** `src/modulos/M11_reporte.py::anexo_referencias`

## EXT-8-02 · El hijo recalcula: la equivalencia se afirma sobre la sesión serializada, no sobre el objeto `Informe`

- **Qué se difirió:** serializar el `Informe` de la ventana y pasárselo al
  proceso hijo para que sólo formatee.
- **Por qué:** el cálculo cuesta 2 ms por punto y el `Informe` no tiene
  forma serializable de ida y vuelta (`informe_json` es un volcado de
  salida, no un formato de carga). El hijo corre la CLI con la MISMA
  sesión que «Guardar sesión» escribe —`ExpedienteApp._datos_de_sesion`,
  una sola definición— y la CLI la repone por `declaracion.restaurar_sesion`,
  el mismo camino con guardia que la ventana. Lo que se afirma y se mide
  (`test_pc11_el_pdf_del_subproceso_describe_la_misma_corrida`) es «misma
  sesión serializada → misma corrida, salvo la marca de tiempo»
  (`gui.exportacion_pdf.sin_marca_de_tiempo`).
- **Qué haría falta:** un formato de sesión con la corrida embebida
  (`informe_json` por corrida, `FORMATO_SESION = 3`): es EXT-10 / E04.
- **Cerrada EN PARTE en EXT-10 (2026-09-21).** La sesión embebe la corrida
  y la CLI compara la suya con la embebida (`cli._comparar_con_la_corrida_
  embebida`); el hijo del PDF SIGUE RECALCULANDO, porque `Informe` sigue
  sin forma de ida y vuelta. Lo que queda es la ficha EXT-10-04.
- **Dónde vive:** `gui/exportacion_pdf.py::ProcesoPdf`

## EXT-8-03 · Las claves enteras de un criterio declarado no sobreviven al JSON de la sesión

- **Qué se difirió:** corregir que un criterio `dict_con_campos` declarado
  con claves ENTERAS (el espesor de pared por diámetro, que `conftest`
  declara como `{"concreto_reforzado": {900: 0.1, …}}`) vuelva de una
  sesión guardada con claves de TEXTO (`"900"`), de modo que el consumidor
  no encuentra la fila y se detiene con «Falta el dato
  `espesor_pared_conducto[concreto_reforzado][900]`».
- **Por qué:** lo encontró EXT-8 al medir la equivalencia del subproceso
  —la corrida propia y la del hijo diferían en ese bloqueo— y NO es del
  subproceso: «Guardar sesión» y «Cargar sesión» ya lo hacían antes.
  Convertir claves de texto a enteros al restaurar sería adivinar (una
  clave `"900"` puede ser un texto legítimo en otro criterio), y cambiar
  la forma de guardar es cambiar el formato de sesión, que es EXT-10. El
  test de equivalencia repone la sesión con su forma serializada por las
  dos puertas, para que la afirmación sea la que se puede sostener.
- **Qué haría falta:** en el formato 3 de la sesión, guardar los valores
  de los criterios en una forma que conserve el tipo de las claves (un
  literal de Python, o el par tipo/valor), con migración explícita v2→v3.
- **Dónde vive:** `src/declaracion.py::restaurar_sesion`

## EXT-8-04 · El progreso del hijo se lee de un archivo, no de un pipe, y no hay hilo

- **Qué se difirió:** leer stdout del subproceso por un pipe sin bloquear.
- **Por qué:** un pipe sin bloqueo no existe igual en Windows y en POSIX,
  y la alternativa portable —un hilo lector— es lo que E06/E07 proponían
  y el dictamen descartó: el estado de módulo de los tres archivos de
  valores no es seguro entre hilos. stdout y stderr del hijo van a un
  archivo de trabajo y `ProcesoPdf.sondear()` lee lo que haya llegado
  desde el `after` de Tk; las líneas de progreso llevan
  `cli.PREFIJO_PROGRESO` para separarlas del volcado. `gui/app.py` no
  importa `threading`, y un test lo fija.
- **Qué haría falta:** nada para cerrarla; se registra para que nadie
  proponga el hilo como equivalente.
- **Dónde vive:** `gui/exportacion_pdf.py::ProcesoPdf`

## EXT-8-05 · Un paso renderizado suelto lleva enlaces sin destino

- **Qué se difirió:** que `bloque_paso` / `bloque_pasos` / `memoria_de_punto`,
  usados FUERA de `memoria_html_por_partes`, impriman los enlaces al anexo
  con destino. `tests/linea_base_familia_c/memoria_punto_cajon.html` (el
  driver `punto_cajon.py` imprime sólo `bloque_pasos`) tiene hoy 35 `href`
  y 0 `id`.
- **Por qué:** ningún consumidor de producción muestra un punto suelto como
  HTML —la traza de la GUI es texto por `traza_punto`— y el anexo es del
  DOCUMENTO: se construye con los pasos de todos los puntos y las citas de
  sus fundamentos. Darle a cada fragmento su propio anexo sería la segunda
  transcripción que la §4.5 prohíbe, y ponerlo al pie del fragmento
  cambiaría el oráculo de la línea base por un formato que nadie lee. En
  las siete memorias completas (las generadas y las de línea base) el cruce
  `href`↔`id` da cero huérfanos (`test_pc12_todo_enlace_interno_de_la_
  memoria_tiene_destino`). Lo encontró el auditor adversarial de EXT-8.
- **Qué haría falta:** si algún día un fragmento se entrega solo, una
  función `fragmento_con_anexo(pasos)` que lo cierre con su propio anexo.
- **Dónde vive:** `src/modulos/M11_reporte.py::bloque_paso`


# Parte XXV — Lo que EXT-9 dejó escrito al convertir `src/` en paquete y separar el servicio de cálculo

## EXT-9-01 · `cli` conserva reexportaciones del servicio hasta que la suite migre

- **Qué se difirió:** retirar de `cli.py` el bloque `from src.servicio import
  (...)  # noqa: F401` que reexporta lo que `gui/app.py` lee como `cli.X` y
  lo que la suite lee de `cli` (por atributo y por `from cli import`), y
  con él esas lecturas.
- **Por qué:** E01 pedía mover la orquestación sin cambiar el contrato de
  quien la consume («se retiran solo cuando los archivos de tests migren»).
  Lo que SÍ se fija ya es que la reexportación es el MISMO objeto, con el
  censo derivado del AST de la GUI y de la suite por las dos vías
  (`test_e03_cli_reexporta_el_mismo_objeto_que_el_servicio`); los tres
  `monkeypatch` sobre lo que el servicio LLAMA migraron a `servicio`. El
  auditor adversarial midió que sólo cinco privados se leen como código y
  que seis (`_etapa`, `_fase_*`, `_dato_externo`, `_avisar_ids_desconocidos`)
  se conservan porque el prompt los nombra; y que los lectores son 17
  archivos por atributo más 6 por `from cli import`, no once. La lista y la
  razón viven en el bloque de imports de `cli.py`.
- **Qué haría falta:** cambiar `cli.X` y `from cli import` por `servicio` en
  `gui/app.py` y en esos archivos, retirar el bloque y dejar que el censo del
  test —que sale del código— se apague solo.
- **Dónde vive:** `cli.py::main`

## EXT-9-02 · La CLI se queda en la raíz: no hay `python -m src.cli`

- **Qué se difirió:** mover `cli.py` dentro del paquete para que
  `python -m src.cli` y `python -m src.normativa.manifiesto` compartan
  literalmente la misma escritura, que es como el prompt de EXT-9 enuncia
  la convención (`python -m <paquete>.cli`).
- **Por qué:** la convención que se comparte es la que importa —todo se
  lanza desde la raíz, con `-m` o como script de la raíz, y nada inserta
  rutas en `sys.path`—, y `cli.py` en la raíz ya la cumple: `python cli.py`
  y `python -m cli` resuelven `src` porque la raíz es `sys.path[0]`. Moverlo
  habría tocado el contrato de EXT-8 (el subproceso del PDF lanza
  `python cli.py --sesion ...`, `gui/exportacion_pdf.py::comando_exportar_pdf`),
  el README, la línea base de la Familia C (`regenerar.sh` lo invoca cuatro
  veces) y una docena de tests que lo ejecutan por ruta, sin cerrar ningún
  hallazgo: PC-08 se cierra con un solo nombre importable para `src/`, no
  con la ubicación del adaptador. Lo que sí cambió de escritura es lo que
  no tenía otra salida: `src/indice_formulas.py` se lanza como
  `python -m src.indice_formulas` —como script, `sys.path[0]` es `src/` y el
  paquete no se ve—, igual que `tests/linea_base_familia_c/punto_cajon.py`
  (`python -m tests.linea_base_familia_c.punto_cajon` en `regenerar.sh`).
  Por la misma razón `python gui/app.py` dejó de funcionar —`sys.path[0]`
  sería `gui/`— y la escritura vigente es la del README, `python -m gui.app`;
  la forma vieja sobrevive en documentos históricos
  (`docs/auditoria_y_ruta_despliegue_v9.md`, `prompt_PD_piloto_dimensional.md`
  con `python3 src/indice_formulas.py`), que no se reescriben.
- **Qué haría falta:** si algún día el adaptador entra al paquete, un
  `src/cli.py` con el `main` actual y un `cli.py` de raíz que sólo lo
  invoque, actualizando a la vez el comando del hijo del PDF, el README y
  `regenerar.sh`; y decidir qué pasa con `import cli` en la GUI y en la
  suite, que volvería a ser un segundo nombre para el mismo módulo.
- **Dónde vive:** `gui/exportacion_pdf.py::comando_exportar_pdf`

## EXT-9-03 · El índice de fórmulas no se regeneró en EXT-9, y su sello sigue siendo el de EXT-8

- **Qué se difirió:** regenerar `docs/indice_formulas.md` con un sello de
  EXT-9.
- **Por qué:** EXT-9 es un refactor de imports y de ubicación: la corrida de
  referencia emite los MISMOS `PasoDeMemoria` —el test de sincronía lo
  comprueba regenerando a memoria y comparando el cuerpo sin la fecha—, de
  modo que no hay nada que resincronizar, y el sello exige el par de la suite
  medido sobre `origin/main`, que no se conoce antes de fusionar. El
  dictamen ya lo había dicho de E03c («no puede "regenerar el índice con
  sello" dentro de la sesión») y el prompt de EXT-9 lo repite. El
  encabezado del documento nombra `src/indice_formulas.py` como ruta de
  archivo, que sigue siendo cierta; el comando de regeneración, que sí
  cambió, vive en el docstring del módulo y en los mensajes de
  `tests/test_indice_formulas.py`, no en el documento generado.
- **Qué haría falta:** nada para cerrarla; la próxima sesión que toque
  citas, criterios, memoria o pasos regenera los cuatro documentos con su
  sello, como manda el ritual de cierre.
- **Dónde vive:** `src/indice_formulas.py::corrida_de_referencia`


---

# Parte XXVI — Lo que EXT-10 dejó escrito al hacer del despliegue una herramienta multi-obra

EXT-10 cerró EXT-V-01 y la fase E04 del plan de evolución: la enmienda
constitucional primero (CLAUDE.md, v8 §0.7) y después el mecanismo —
`DatoSitio.nivel`, `datos_sitio.establecer_dato_dinamico`, `--datos-sitio`,
la sesión formato 3 como único lugar del «proyecto actual», el origen de
cada [S] en la memoria y la advertencia de corredor—. Seis cosas quedaron
decididas DISTINTAS de la lectura más directa del prompt, o sin hacer a
propósito, y cada una lleva su argumento y su símbolo.

## EXT-10-01 · La ventana normativa sigue sin declarar datos de sitio

- **Qué se difirió:** que la pestaña 2 / la ventana emergente declaren un
  [S] como declaran un criterio.
- **Por qué:** la regla R4 («cuando una fila depende de un dato que el
  proyecto no tiene, la ventana pide o bloquea; nunca elige») vale para la
  variable entera: un [S] no se elige en un formulario, se LEE con un
  procedimiento y se defiende con la trazabilidad de esa lectura. La casa
  nueva de EXT-10 es la sesión —un archivo con valor, trazabilidad y fecha
  por clave, revisable y versionable—, y por eso el campo de la pestaña 1 y
  `--datos-sitio` son la puerta, no un cuadro de texto por dato. El texto de
  `_POR_QUE_NO_DECLARABLE[DATO_SITIO]` dice ahora dónde sí se declara.
- **Qué haría falta:** decidir si un editor por dato en la GUI (valor +
  trazabilidad + fecha, sobre `verificar_declaracion_de_sitio`) es un
  requisito de producto; es la misma pregunta que E10 para los criterios.
- **Dónde vive:** `src/ventana_normativa.py::_POBLACION_DECLARABLE`

## EXT-10-02 · «Importar decisiones» importa criterios y no datos de sitio

- **Qué se difirió:** que «Importar decisiones» (sustituir=False) sume
  también el bloque `sitio` de otra sesión, y la confirmación clave a clave
  cuando pisa (pregunta abierta desde EXT-4-01).
- **Por qué:** importar decisiones de otra sesión tiene sentido para lo que
  se ELIGE —un criterio elegido en la obra A puede valer en la B—; un [S] es
  un hecho de UN sitio y sumar los de otra obra es exactamente el error que
  la etiqueta existe para impedir. Abrir sustituye, importar suma sólo
  criterios, y `_aplicar_bloques_de_sesion` es la única función que toca los
  [S] de la sesión. La confirmación clave a clave sigue sin decidirse: no
  cabe en un cluster de estado de datos de sitio.
- **Qué haría falta:** un caso de uso real en que dos obras compartan un
  [S] (no se conoce ninguno), y para la confirmación, la sesión E10 de
  editores tipados.
- **Dónde vive:** `gui/app.py::importar_decisiones`

## EXT-10-03 · La advertencia de corredor es por origen, no por texto; no bloquea y no va al JSON

- **Qué se difirió:** comparar el nombre de `--proyecto` con
  `corredor_del_proyecto` («advierte si no coinciden», letra del prompt),
  un bloqueo cuando no coinciden, y meter la advertencia en `informe_json`.
- **Por qué:** la primera versión comparaba los dos textos por contención
  normalizada y el auditor adversarial la refutó en las dos direcciones: el
  corredor del archivo es una descripción («terraplen de ~5 km de la Fase
  0-bis…») que ningún nombre de obra contiene, así que la propia obra del
  repositorio recibía el aviso siempre; y un proyecto de nombre corto («A»,
  «km») o sin nombre no lo recibía nunca. Dos rótulos escritos por personas
  no se pueden comparar con provecho. Lo que sí se sabe con certeza es el
  ORIGEN del corredor efectivo: si gobierna desde `datos_sitio.py`, los [S]
  son los de la obra del repositorio y el aviso lo dice, con o sin nombre
  de proyecto; si otra obra los declaró por sesión, la sesión es el
  proyecto y no hay nada que advertir. Sigue siendo puro, sólo avisa, y no
  va al JSON porque `Informe` no lleva `proyecto`. El [S]
  `corredor_del_proyecto` de La Unión no se reescribió para callar el
  aviso, y por eso la memoria de la obra del repositorio lo lleva: es
  cierto que sus [S] gobiernan desde el archivo.
- **Qué haría falta:** una cabecera de obra con progresivas en el CSV o en
  el sitio.json (lo que `reemplazado_por` de `corredor_del_proyecto` ya
  pide) y entonces una comparación por dato y no por texto.
- **Dónde vive:** `src/datos_sitio.py::advertencia_de_corredor`

## EXT-10-04 · La sesión embebe la corrida; el hijo del PDF sigue recalculando

- **Qué se difirió:** que el subproceso del PDF (EXT-8) lea el `informe_json`
  embebido en la sesión y sólo formatee, en vez de repetir el cálculo.
- **Por qué:** `informe_json` es un volcado de salida, no un formato de
  carga: `Informe` no tiene ida y vuelta y M11 formatea objetos, no dicts.
  Lo que E04 sí da es la equivalencia MEDIDA sobre la sesión: la CLI, al
  abrir una sesión con corrida embebida del mismo CSV y alcance, dice si su
  corrida la REPRODUCE (mismo JSON salvo la marca de tiempo) o DIFIERE, y
  eso es lo que un revisor necesita para saber si la memoria sigue vigente.
- **Qué haría falta:** un cargador de `Informe` desde su JSON, con los
  `PasoDeMemoria` incluidos; es la sesión E14 (comparador) la que lo
  necesitará primero.
- **Dónde vive:** `cli.py::_comparar_con_la_corrida_embebida`

## EXT-10-05 · El nivel de seis datos de sitio es un argumento, no una medida

- **Qué se difirió:** medir por corridas el `nivel` de `ZONA_SISMICA_LA_UNION`,
  `Z_E030`, `corredor_del_proyecto`, `carriles_por_sentido`, `clase_de_via` y
  `existe_informacion_secundaria_tramo`.
- **Por qué:** ningún módulo de cálculo los invoca por `valor()` (la zona y
  el Z son sólo referencia, Sec. 0.4; el corredor lo imprime M11 desde el
  contexto; los tres de calicatas los pide el Manual de Suelos y ningún
  módulo los consume todavía), de modo que ninguna corrida puede medirlos.
  Se clasifican por argumento, escrito junto al campo, y están censados en
  `DATOS_SIN_CONSUMIDOR_Y_SIN_MEDIDA` para que el grupo no crezca en
  silencio, con la misma técnica que `test_nivel_medido`. Los otros tres se
  midieron: `PGA_roca_B` lo invoca sólo la corrida de expediente, y los dos
  de M9 se detienen antes en otros pendientes.
- **Qué haría falta:** un consumidor real de los tres de calicatas (el
  programa de exploración del expediente), que los haría medibles.
- **Dónde vive:** `tests/test_ext10_multiobra.py::DATOS_SIN_CONSUMIDOR_Y_SIN_MEDIDA`

## EXT-10-06 · El `id` de una sesión migrada sólo es estable desde que se guarda

- **Qué se difirió:** una identidad de sesión derivada del contenido (una
  huella) en vez de un `uuid4` asignado al migrar.
- **Por qué:** una sesión v1 o v2 no tiene identidad, y una huella del
  contenido cambiaría con cada campo editado, que es lo contrario de una
  identidad. `migrar_a_actual` asigna un `uuid4` nuevo a cada apertura de
  una sesión sin `id` y LO DICE en el aviso («solo sera estable cuando la
  guarde»); la ventana lo conserva en `sesion_id` y «Guardar sesion» lo
  escribe, y desde entonces abrir y guardar conservan el mismo. Los
  archivos de `tests/apoyo/` que escriben `FORMATO_SESION` sin `id` entran
  por la misma regla.
- **Qué haría falta:** nada para cerrarla; es el comportamiento elegido.
- **Dónde vive:** `src/sesion.py::_migrar_v2_a_v3`

# Parte XXVII — Lo que EXT-11 dejó escrito al medir la suite con propiedades y mutación

EXT-11 cerró PC-18 (residuo), PC-20, PC-21, PC-22 y PC-29: siete propiedades
del motor hidráulico por mallas, un arnés de mutación propio medido sobre
M3–M5/MD y el par (n_min, n_max), y la higiene de suite que el dictamen
enumeró (dos tests textuales al AST con su guardia, la corrida real en
concreto de test_cli, la ausencia real de M5, la marca `lento`, el censo de
públicas sin referencia y el cruce de los temarios como test). Cinco cosas
quedaron decididas DISTINTAS de la lectura más directa del prompt, o sin
hacer a propósito, y cada una lleva su argumento y su símbolo.

## EXT-11-01 · Sin `hypothesis` ni `mutmut`: mallas y un arnés propio, hasta que se apruebe la dependencia

- **Qué se difirió:** sumar `hypothesis` y `mutmut` a `requirements-dev.txt`
  como dependencias de TEST, con la misma justificación que PyMuPDF.
- **Por qué:** el prompt de EXT-11 manda CONSULTAR antes (regla de
  dependencias de CLAUDE.md) y da el camino por defecto si no se aprueban:
  `pytest.parametrize` sobre mallas. La consulta no obtuvo respuesta en la
  sesión, y sin respuesta la regla es que no se suma nada. Las siete
  propiedades se escribieron sobre mallas deterministas (10 secciones × 3
  materiales o el marco × 4 pendientes × 6 fracciones de Q_lleno; 58 pasos
  de q\* para la monotonía), y la mutación se midió con
  `tests/apoyo/mutacion.py`, un arnés por AST de un archivo que genera los
  ocho operadores —seis sintácticos y dos del dominio, el par de n y las dos
  velocidades— y corre los tests objetivo en subproceso. Lo que se pierde
  frente a `hypothesis` es la búsqueda aleatoria de contraejemplos y el
  encogimiento; frente a `mutmut`, la caché incremental y el catálogo
  completo de operadores. Lo que se gana es que la malla se lee entera y
  que la mutación corre en minutos sin dependencia nueva.
- **Qué haría falta:** la aprobación de las dos dependencias. Con ella, las
  mallas se conservan (son la documentación de cada propiedad) y se añade
  por encima una estrategia de `hypothesis` por propiedad; el arnés propio
  se retira si `mutmut` reproduce su censo de supervivientes.
- **Dónde vive:** `tests/apoyo/mutacion.py::MODULOS_DE_EXT11`

## EXT-11-03 · El cruce de los temarios lleva un censo manual porque el auditor y el informe numeran distinto

- **Qué se difirió:** un cruce puramente automático entre
  `temario_refutar_*.json` y la hoja `Hallazgos`, sin lista mantenida a mano.
- **Por qué:** los ítems de los temarios remiten a la numeración ORIGINAL
  del auditor (`H-13`, `E-06`, `G-06`, `H-MC-19`) y las filas del tracker a
  la del informe consolidado (`NOR-E060-03`, `NOR-HID-05`), y ningún
  documento del repositorio enlaza las dos: `auditoria_normativa.md` §13
  lista los ítems por `R95-nnn`/`hallazgo_id` sin decir a qué ficha NOR
  corresponden. EXT-0 cruzó los 71 ítems ALTA/CRÍTICA a mano y dejó huella
  sólo de los 7 con fila propia y de los 8 grupos PARCIAL anotados en
  «Vínculos cruzados»; los 45 restantes están cubiertos por una fila NOR y
  nadie lo había escrito. `CUBIERTOS_POR_FILA_NOR` es ese resto, ítem por
  ítem con la fila que lo cubre, y el test lo exige en las dos
  direcciones: un ítem sin fila, sin mención y sin censo falla, y una
  entrada del censo que el tracker ya absorbió también. Los otros 26 se
  cubren solos por (a) y (b).
- **Qué haría falta:** una columna «ID auditor» en las filas NOR del
  tracker (o en las fichas de §11 del informe) que enlace `H-nn` ↔ `NOR-*`;
  con ella el censo se deriva y desaparece.
- **Dónde vive:** `tests/test_ext11_cruce_temarios.py::CUBIERTOS_POR_FILA_NOR`

## EXT-11-04 · La Fase 8 se prueba llamándola sobre el resultado real de perfil, porque el expediente no dimensiona

- **Qué se difirió:** una corrida de EXPEDIENTE que dimensione un punto
  sin ayuda, para que las Fases 6, 7 y 8 se prueben de punta a punta por la
  puerta del expediente.
- **Por qué:** a nivel de expediente V5 y V8 son obligatorias y están
  vacías (`remanso_derecho_via`, `TR_evento_extremo`), y con ellas
  declaradas piden datos que ninguna puerta aporta todavía
  (`ancho_derecho_via_m`, `Q_evento_extremo_m3s`): el bucle de MD se
  detiene ANTES de dimensionar, por diseño. La corrida de perfil sí
  dimensiona A-01, A-02 y B-01 en concreto reforzado con las Fases 6 y 7
  reales, V5 y V8 diferidas con fundamento y el contexto completo, y ESA
  corrida es `informe_dimensionado`: salida del producto sin parche. La
  Fase 8, diferida en perfil también por diseño, se ejercita llamando
  `servicio._fase_8` sobre una copia del punto real, y llega a la cama de
  apoyo del concreto y al bloqueo de la clase de producto. Se descartó la
  alternativa que la sesión escribió primero —una corrida de expediente con
  `disenar_punto` devolviendo el resultado de perfil— porque el auditor
  adversarial midió que no era «el producto»: perdía los usos de criterios
  de la Fase 4 (`correr` reinicia el registro al entrar) y mostraba tres
  puntos dimensionados a nivel de expediente con V5 y V8 ni verificadas,
  ni bloqueadas, ni diferidas. El stub de HDPE D = 0.60 m que el producto
  no podía producir (PC-20) se retiró; queda un solo doble, de la capa de
  reporte (`informe_con_criterio_desconocido`), sobre una copia.
- **Qué haría falta:** cerrar V5 y V8 en el expediente (los datos de
  remanso y del evento extremo por una puerta real); entonces la Fase 8 se
  prueba por la corrida de expediente y la llamada explícita sobra.
- **Dónde vive:** `tests/test_cli.py::informe_dimensionado`

## EXT-11-05 · El determinismo de la línea base se demuestra con los archivos comprometidos, no con una segunda corrida

- **Qué se difirió:** la segunda corrida de `regenerar.sh` que
  `test_la_corrida_es_determinista` lanzaba siempre (6 s medidos en
  5196dd2) para comparar dos corridas del mismo árbol.
- **Por qué:** los archivos comprometidos SON una corrida anterior del
  mismo árbol, hecha en otro clon y a otra hora, que es exactamente el eje
  por el que el mtime de `criterios_adoptados.py` variaba (C0). Si la
  corrida de la fixture coincide con ellos byte a byte, el determinismo
  queda demostrado con una prueba más fuerte que dos corridas seguidas en
  la misma máquina, y sin correr nada más. La segunda corrida se conserva
  para el caso rojo, donde separa los dos diagnósticos que la discrepancia
  mezcla: un campo volátil sin normalizar (dos corridas seguidas también
  difieren) o un cambio del código (dos corridas seguidas coinciden y es el
  test de la línea base el que tiene que fallar). Es la mitad «compartir la
  corrida entre sus dos tests» de PC-22; la fixture de módulo ya la
  compartía entre los otros tres desde antes del dictamen. Queda dicho lo
  que el auditor adversarial señaló: en verde, este test afirma la MISMA
  comparación que el de la línea base, con otro sentido; lo que añade es el
  diagnóstico del caso rojo, y en el clon que regeneró la línea base el
  eje del mtime no lo ejercita ninguna de las dos pruebas.
- **Qué haría falta:** nada para cerrarla; es el comportamiento elegido.
- **Dónde vive:** `tests/test_linea_base.py::test_la_corrida_es_determinista`

## EXT-11-02 · Cuarenta y tres mutantes sobreviven a toda la suite, y cada uno tiene su razón escrita

- **Qué se difirió:** matar los 43 mutantes de M3–M5/MD que sobreviven a
  los diez archivos objetivo del arnés y a la segunda vuelta (línea base,
  cierre de perfil y CLI), medidos el 2026-09-21 sobre el árbol de EXT-11:
  568 de 679 muertos en la primera vuelta (83.6 %), 65 de los 111
  supervivientes muertos en la segunda, 46 vivos; tres más murieron con la
  segunda tanda de tests que la propia lista motivó (el motivo de descarte
  del marco, la identidad de anchos en `_mismo_escalon`, la procedencia del
  ke) y quedan 43.
- **Por qué:** ninguno de los 43 es un hueco real, y la clase de cada uno
  está escrita en `SUPERVIVIENTES_CON_RAZON`: 34 son equivalentes (una
  `<=` frente a `<` cuando la banda `TOL_UMBRAL_NORMATIVO` ya cubre la
  igualdad exacta, de medida nula; las guardias del corchete de
  `tirante_normal`, inalcanzables tras la de `Q_lleno`; un `return None`
  donde sólo se lee la falsedad; un argumento por defecto que nadie usa; el
  `cota_agua` sin efecto de la vía de escenarios; el techo de la tabla del
  CBR, que el orden descendente de la tabla vuelve redundante); 6 son de
  banda (el signo de la tolerancia en V4, V4b, VC1, V7, `hw_gobernante` y
  la altura del barril, donde fijar el umbral exacto exige cotas o pesos al
  pelo); 2 son de borde
  (HW/D exactamente 0.75 y 1.2 de HDS-5 pág. 3.24, de medida nula) y 1
  está fuera del alcance de la suite (`M5.verificar` entera, porque V5
  vacía detiene el expediente antes de su último `return`; ficha
  EXT-11-04). Los huecos reales que la mutación encontró —V3 juzgando la
  rama baja, los umbrales inclusivos, las guardias del receptor, el par de
  Manning, el ke, la progresión que se repite, la cota del TW— se cerraron
  con tests y se remidieron con el arnés función por función; ninguno se
  censó. La lista se ancla por (módulo, función, operador, fragmento,
  ordinal) y `test_cada_superviviente_del_censo_sigue_siendo_un_mutante_
  del_codigo` la contrasta con lo que el arnés genera hoy.
- **Qué haría falta:** para los de banda y borde, casos construidos al pelo
  (invertir el control de salida para HW/D = 0.75 exacto, cotas que dejen
  V4 a menos de 1e-9 del admisible), que fijarían una lectura de la fuente
  que hoy es de medida nula; para el de `M5.verificar`, cerrar V5 en el
  expediente.
- **Dónde vive:** `tests/test_ext11_mutacion.py::SUPERVIVIENTES_CON_RAZON`

# Parte XXVIII — Lo que E-A dejó escrito al calcular el perfil de la lámina

E-A cerró NOR-HDS-05 entera: el perfil de la lámina de agua por paso directo
(HDS-5 pág. 3.12 y Sección 3.5), con sus dos salidas —la fracción de longitud
a sección llena, que vuelve medida la primera condición de h_o, y el HW por
remanso bajo HW/D < 0.75, que deshace la circularidad de la aproximación— y
con V1/V2 evaluadas sobre él. Siete cosas quedaron decididas DISTINTAS de la
lectura más directa de la fuente o del prompt, o sin hacer a propósito, y
cada una lleva su argumento y su símbolo.

## EA-01 · Los dorados del perfil son límites de la propia fórmula, no una corrida HY-8

- **Qué se difirió:** un caso patrón de perfil con números externos
  (HY-8 u otra corrida citable) en `tests/fixtures/casos_patron.py`.
- **Por qué:** el conflicto #7 de la matriz de auditorías prohíbe fabricar
  dorados, y el paquete I1 lo dijo para el perfil: «un caso patrón de perfil
  necesita una corrida de referencia externa citable». No la hay. Lo que sí
  se puede fijar sin inventar son los LÍMITES de la propia fórmula —con la
  línea de energía llena de punta a punta el perfil reproduce
  HW = H + h_o − S·L de `control_salida` (identidad algebraica); con TW = y_n
  el perfil es plano y HW = y_n + (1 + ke)·V_n²/2g— y el BALANCE DE ENERGÍA
  estación a estación, que es la ecuación que el método resuelve. Los números
  del prototipo (0.489, 0.391, 1.130, 0.5518, 0.501) se contrastan a la cifra
  impresa, como los del dictamen en EXT-3: lectura, no dorado.
- **Qué haría falta:** una corrida HY-8 (o equivalente) aportada por el dueño
  del expediente sobre uno de los casos del dictamen, con su archivo de
  entrada; con ella el caso entra en `casos_patron.py` con su cita.
- **Dónde vive:** `tests/test_ea_perfil_lamina.py::REL_DORADO_LIMITE`

## EA-02 · El resalto no se sitúa por momentum: la S1 que no llega a la entrada se lee como control de entrada

- **Qué se difirió:** situar el resalto hidráulico dentro del barril (HY-8
  7.3 lo hace por momentum, Sección 3.5.1) y computar la S2 desde la
  entrada aguas arriba de él.
- **Por qué:** para el HW basta lo que la Sección 3.5.1 escribe del tipo 1:
  la S1 se usa «if the S1 curve extends to the face of the culvert»; si
  corta el tirante crítico antes, el control es de entrada y el HW es el de
  la pieza 4.2, exista o no un resalto aguas abajo. Dónde queda el resalto
  cambia el tirante y la velocidad del tramo intermedio, y ahí el proyecto
  aproxima el tramo supercrítico por el uniforme —la misma decisión de EXT-3
  para el control de entrada— y toma como tirante máximo el mayor entre la S1
  medida y y_n (`PerfilLamina.y_max_m`), que es conservador para V1 y para
  V2. Situar el resalto exigiría la ecuación de cantidad de movimiento en la
  sección circular, que ninguna de las dos fuentes transcribe.
- **Qué haría falta:** transcribir la condición de profundidades secuentes
  para la sección circular y el marco (Chow o HY-8) con su cita, y una
  corrida de referencia que la valide.
- **Dónde vive:** `src/modulos/M4_control.py::perfil_lamina`

## EA-03 · En la banda 0.75 ≤ HW/D < 1.2 la aproximación es el método y la comprobación manda sólo si pide más carga; el paso 4.3c puede decir NO CUMPLE sin rechazar el punto

- **Qué se difirió:** sustituir la aproximación por el remanso siempre que
  exista el perfil (la lectura de HY-8, Sección 3.5), o siempre que el barril
  no vaya lleno en la mayor parte de su longitud.
- **Por qué:** la v8 §4.3 (EXT-0) decidió que en la banda 0.75–1.2 «el método
  sí se usa, con cautela, y el remanso es la comprobación que la fuente
  pide», y el prompt de E-A pide el remanso «bajo HW/D < 0.75». La fuente
  sostiene esa lectura (pág. 3.12: «adequate results … down to a headwater of
  0.75D»). Lo que la auditoría adversarial de E-A midió es que una
  comprobación sin consecuencia no comprueba nada: en 165 de 228
  combinaciones de la banda el remanso pedía MÁS carga que la aproximación
  (hasta +34 mm, +5 %), y publicar la menor teniendo la mayor no es
  conservador. Por eso en la banda manda el mayor de los dos
  (`PerfilLamina.comprobacion_manda`) y por encima de 1.2 la aproximación, con
  el remanso impreso. La viñeta de la pág. 3.24 («can only be used if the
  barrel flows full for most of its length») es más estricta que su propia
  prosa y el proyecto la MIDE en vez de aplicarla: cuando la aproximación se
  usa y el barril no va lleno en la mayor parte, el paso 4.3c imprime NO
  CUMPLE sobre esa condición, con la cita de la 3.12 que ampara el HW. No es
  la divergencia de SIS-A-07 (`TipoDeVeredicto` lo dice): lo que no se cumple
  es la condición ideal de un método cuya validez la propia fuente extiende,
  y `verificaciones_incumplidas` lee las `Verificacion`, no los pasos. V3
  tampoco cambia: sigue comparando `V_erosion` del uniforme (EXT-3).
- **Qué haría falta:** que la v8 §4.3 decida que el remanso gobierna siempre
  que exista; con ella `HW_efectivo_m` devuelve siempre el remanso y el paso
  4.3 se vuelve informativo.
- **Dónde vive:** `src/modelos.py::PerfilLamina`

## EA-04 · La compuerta de h_o queda como guardia sin alcance en producción

- **Qué se difirió:** retirar `servicio._compuerta_metodo_h_o`, los dos casos
  de `MetodoNoEvaluableError` bajo control de salida y el texto
  `M5.PROCEDIMIENTO_PERFIL_LAMINA`.
- **Por qué:** con el perfil que M4 emite siempre, la aproximación fuera de
  rango no se usa y `ResultadoHidraulico.h_o_fuera_de_rango` no puede ser
  True; V1/V2 tampoco llegan al `MetodoNoEvaluableError`. Pero el tipo sigue
  admitiendo un resultado SIN perfil —los constructores de la suite que no
  pasan por M4—, y ahí la guardia es la respuesta honesta: no se inventa un
  llenado. Retirarla convertiría ese estado en un `AttributeError` fuera de
  `ErrorProyecto`. Los dos tests que la llaman directamente
  (`test_ext3_regimen_barril`, `test_ea_perfil_lamina`) fijan que dispara sin
  perfil y calla con él.
- **Qué haría falta:** que `ResultadoHidraulico.perfil` deje de admitir
  `None` —lo que exige reescribir los constructores de la suite— y entonces
  la compuerta y los dos casos se retiran juntos.
- **Dónde vive:** `src/servicio.py::_compuerta_metodo_h_o`

## EA-05 · «Most of its length» es un [A] con ventana, y su lectura vive en el registro

- **Qué se difirió:** un número [N] para «most of its length», o la
  cuantificación por la fuente.
- **Por qué:** «most» es una palabra de la fuente, no un número. La primera
  redacción de E-A lo escribió como 1/2 en `constantes_normativas.py` («el
  significado de la palabra»), y la auditoría adversarial lo refutó con la
  propia `Interpretacion` registrada: admite «casi toda», o sea que hay
  alternativas, y una lectura con alternativas es una elección con ventana,
  [A] por la taxonomía de CLAUDE.md. Es `'fraccion_llena_mayor_parte'`
  (0.5, sensibilidad 0.5–0.9, nivel perfil, forma float) y la lectura
  sigue en `citas.INTERPRETACION_MAYOR_PARTE`, con lo que juega en contra.
  Sólo mueve el rótulo del veredicto del paso 4.3c: la consecuencia de fallar
  la condición la fija la pág. 3.12 (EA-03).
- **Qué haría falta:** que la fuente cuantifique «most»; entonces el número
  pasa a [N] y la `Interpretacion` se retira.
- **Dónde vive:** `src/criterios_adoptados.py::fraccion_llena_mayor_parte`

## EA-06 · Veinticuatro mutantes del perfil sobreviven a toda la suite, y cada uno tiene su razón escrita

- **Qué se difirió:** matar los 24 mutantes de `M4.perfil_lamina` y sus
  auxiliares que sobreviven a los once archivos objetivo del arnés
  (`tests/test_ea_perfil_lamina.py` sumado a los diez de EXT-11) y a la
  segunda vuelta (línea base, cierre de perfil, CLI), medidos el 2026-09-21
  con `--funcion` sobre las once funciones tocadas por E-A: 242 mutantes,
  212 muertos en la primera vuelta (87.6 %), 5 más en la segunda, 25 vivos.
  Uno era un hueco real —`V_entrada_m_s` del retorno UNIFORME, que ningún
  test leía (Q/A → Q·A sobrevivía)— y se cerró con una aserción en el dorado
  de flujo uniforme; una primera medición, antes de la auditoría adversarial,
  había dejado 37 vivos y motivó cinco tests más y la retirada de dos
  términos muertos (`max(y_max, y_n)`, `min(V_min, Q/A_n)`).
- **Por qué:** ninguno de los 24 es un hueco, y la clase de cada uno está en
  `SUPERVIVIENTES_CON_RAZON`: 4 ya estaban censados desde EXT-11
  (`hw_gobernante` ×2, V1, V2: banda); de los 20 nuevos, 13 son de borde
  (una igualdad exacta en punto flotante: la raíz de Sf = S en un extremo del
  corchete, Sf exactamente S en la frontera o en la línea llena, HW/D
  exactamente 0.75 o 1.2, el corte de la clave o un escalón que termina
  exactamente en la entrada, dx exactamente cero, una frontera a
  exactamente 1e-9 m de y_c, de la clave o de la asíntota), 5 son
  equivalentes (el signo del cociente frente al del producto; TW == D;
  TW == y_c; `longitud_llena` = 0 en los dos retornos donde el mutante lo
  multiplica) y 2 son de banda (la frontera a menos de 2·TOL de y_c, y el
  freno de la escalera en 1e-12·S frente a 1e-12/S, entre los que ninguna
  estación cae porque acercarse tanto a la asíntota exige del orden de 1e9
  escalones). Los de borde y banda son los de siempre: fijarlos pediría
  casos al pelo sobre tolerancias numéricas que no mueven ninguna magnitud.
- **Qué haría falta:** casos construidos exactamente sobre cada borde
  (un TW igual a y_c a la ulp, un Sf_llena igual a S), que fijarían lecturas
  de medida nula; nada para los equivalentes.
- **Dónde vive:** `tests/test_ext11_mutacion.py::SUPERVIVIENTES_CON_RAZON`

## EA-07 · La asíntota del perfil no es el tirante normal de M3, y la diferencia queda impresa

- **Qué se difirió:** unificar la ley de fricción del perfil (Ec. 3.7 con
  `K_FRICCION_SI` = 19.63) con la de Manning en M3 (`K_MANNING_SI` = 1), o
  clasificar el perfil contra `y_normal`.
- **Por qué:** la auditoría adversarial de E-A midió que 19.63/(2·9.81) =
  1.00051, de modo que en el y_n de Manning la pendiente de fricción del
  perfil vale 1.00051·S y la lámina tiende a un y_n' un 0.05 % más alto
  (0.07 mm en D = 0.90, Q = 0.3, S = 0.001). Clasificar contra y_n dejaba una
  banda de TW entre y_n y y_n' en la que la escalera iba contra su propio
  perfil y lanzaba `LimiteNumericoError`. La corrección es clasificar e
  integrar contra la raíz de Sf = S con la MISMA ley
  (`M4._llenado_donde_Sf_iguala_S`), publicar y_n' junto a y_n en el paso
  4.3c y no tocar la ley: 19.63 es el número que la fuente escribe para la
  fricción del control de salida (v8 §4.3, conflicto #6) y M3 sigue siendo
  Manning con k = 1 como manda la Sec. 4.1; el 0.05 % es el mismo que separa
  19.63 de 2g y está declarado desde PD.
- **Qué haría falta:** que la v8 decida una sola g para la fricción (2g o
  19.63), lo que movería el término de fricción de H en un 0.05 % y con él la
  línea base; hasta entonces las dos asíntotas conviven, dichas.
- **Dónde vive:** `src/modulos/M4_control.py::_llenado_donde_Sf_iguala_S`

# Parte XXIX — Lo que E-B dejó escrito al construir los editores tipados, el comparador y el índice

E-B ejecutó las cuatro piezas del último prompt de la cadena (E10, E14, E13
reducido, E21 acotado) sobre lo que EXT-4, EXT-5 y EXT-10 ya habían dejado:
la forma de cada criterio, el contexto de corrida y la sesión con corridas
embebidas. Seis cosas quedaron decididas DISTINTAS de la lectura más directa
del prompt, o sin hacer a propósito, y cada una lleva su argumento y su
símbolo.

## EB-01 · El literal sigue existiendo: el editor lo compone y es la fuente al aplicar; un dict que la ficha no descompone no recibe campos inventados

- **Qué se difirió:** sustituir el campo literal «Valor nuevo» de la pestaña 2
  por los editores tipados, y dar campos a TODOS los `dict_con_campos`.
- **Por qué:** el literal es el único camino de declaración desde EXT-5 y
  los cuatro apoyos de ventana real de la suite declaran por él; los
  editores lo COMPONEN (dos vistas, un valor) en vez de abrir un segundo
  camino con su propia guardia. Al aplicar, la fuente es el editor cuando
  tiene campos y el literal cuando no (`_valor_a_declarar`): medido en la
  ventana real, un campo que no arma (n = 0.05 fuera de su ventana) dejaba
  el literal en el valor ANTERIOR y «Aplicar» declaraba un número que el
  proyectista no veía. Y un dict cuyos campos no salen de la ficha —un dict
  de dicts como `cobertura_minima_aashto`, o uno vacío sin ventana ni
  campos obligatorios como `N_cq_N_gammaq_meyerhof`— cae al editor LITERAL:
  darle campos sería escribir en el editor lo que la ficha no declara,
  que es el error que el proyecto persigue en todas partes.
- **Qué haría falta:** que las fichas de esos dicts declaren sus campos
  (`campos_obligatorios`, o una ventana por campo) y entonces el editor
  los deriva solo; no hay nada que cambiar en `gui/editores.py`.
- **Dónde vive:** `src/editores.py::_campos_del_dict`

## EB-02 · Una categoría no exige fila, y un número nunca nombra una fila

- **Qué se difirió:** exigir la fila de la tabla a TODO criterio `de_tabla`
  al declararlo desde la pestaña 2, y resolver por el número tecleado la
  fila de la que «proviene».
- **Por qué:** en una `categoria` la selección normativa ES el conjunto
  cerrado que la ficha deriva de la tabla (`sensibilidad`): las filas de
  `condicion_pavimento` son materiales de conducto y sus claves no son los
  tres textos que el criterio admite, de modo que exigir fila la habría
  vuelto indeclarable, y por eso sus filas se ofrecen como contexto y no
  proponen valor (la primera versión proponía la clave de la fila y la
  guardia la rechazaba en las catorce: R8 de la auditoría adversarial). Y
  un número no nombra ninguna fila, ni cuando coincide con una sola celda:
  la primera versión infería la única coincidencia y la auditoría midió que
  0.9 atribuía `ke_entrada` a «Corrugated metal, projecting» sin que nadie
  la eligiera (R3); adivinar la fila es inventar la procedencia (EXT-V-02
  al revés). El rechazo DICE con qué filas coincide el número, para que se
  elija. Teclear la CLAVE de una fila sí la nombra —es el camino del ratón
  de EXT-5, que sigue valiendo—, y vale para toda fila, elegible o no: la
  que no lo es la rechaza R4 en `declaracion`, como desde la ventana
  emergente (R4 de la auditoría: con nota entraba por `declarar_valor`).
  Un dato `de_ensayo` exige la nota, que es su trazabilidad (A1, Conflicto
  #8).
- **Qué haría falta:** nada para el producto; una tabla con una fila por
  categoría permitiría emparejar `categoria` con fila, y entonces
  `exige_fila` podría incluirla.
- **Dónde vive:** `src/editores.py::fila_implicita`

## EB-03 · El comparador compara volcados, no informes; «método» son tres campos

- **Qué se difirió:** un cargador de `Informe` desde su JSON (la ficha
  EXT-10-04 lo pedía «para el comparador») y una definición más ancha de
  «método distinto».
- **Por qué:** el comparador trabaja sobre dos `dict` y no necesita
  reconstruir objetos: comparar volcados es lo que la línea base hace byte
  a byte y lo que la CLI hacía con `==` sobre la corrida embebida; ahora hay
  UNA definición de «la misma corrida» y las dos la llaman. Cargar un
  `Informe` desde JSON seguiría siendo un segundo motor sin tests, y
  EXT-10-04 queda como estaba. «Método distinto» son el control gobernante,
  el régimen del barril y el tipo de perfil de la lámina: los tres deciden
  de qué fórmula salió cada número del diseño; el material o la sección no
  son método sino RESULTADO, y su cambio se reporta como diferencia.
- **Qué haría falta:** un consumidor que necesite el objeto —el hijo del
  PDF leyendo la corrida embebida— y entonces el cargador, con los
  `PasoDeMemoria` incluidos.
- **Dónde vive:** `src/comparador.py::CAMPOS_DE_METODO`

## EB-04 · Responsable y evidencia son una derivación de la ficha, no una matriz; van al JSON y no a la memoria

- **Qué se difirió:** la «matriz requisito-aplicabilidad-responsable-
  evidencia» del plan original, y una columna de responsable en la memoria
  HTML.
- **Por qué:** el dictamen la descartó por no tener forma en el esquema del
  registro; lo que E13 reducido pide cabe en dos lecturas de objetos que ya
  existen —`resolucion` dice quién fija el valor y `reemplazado_por` (o la
  trazabilidad exigida por el ensayo, o la fuente de un vacío) qué lo
  sostiene— y por eso vive en un módulo sin estado que leen el anticipo y
  M11. Van al JSON `criterios.bloquearon` porque es el otro reporte de la
  corrida y dejarlo sin la columna que la pestaña 4 muestra repetiría
  SIS-A-13; no van a la memoria porque el bloque de pendientes ya imprime
  «Qué lo resuelve» desde `reemplazado_por` y una segunda columna diría lo
  mismo con otras palabras.
- **Qué haría falta:** un caso en que responsable y evidencia no se lean de
  la ficha (una asignación de obra, un plazo), que sería un campo nuevo de
  `Criterio` y una decisión de producto.
- **Dónde vive:** `src/responsable.py::evidencia_de`

## EB-05 · El índice se deriva de la plantilla y de los puntos; el «histórico» no ganó una vista

- **Qué se difirió:** un índice escrito en la plantilla, un índice de pasos
  dentro de cada punto, y una vista del histórico de corridas (el «e
  histórico» del título del prompt).
- **Por qué:** el índice sale de los `<h2 id>` del texto que se va a
  imprimir y de los `InformePunto`, de modo que no puede divergir de las
  secciones ni de los puntos («nada que no exista como objeto»); un índice
  de pasos por punto duplicaría los `<h5>` que el anexo ya enlaza (EXT-8) y
  engordaría la memoria que EXT-8 adelgazó. El histórico ya existe como
  objeto desde EXT-10 —las corridas embebidas en la sesión, con su
  `informe_json`— y la CLI ya dice si una corrida reproduce la guardada; la
  pieza que faltaba para leerlo es el comparador de E14, y una vista de
  lista de corridas no añade ningún objeto nuevo. Consecuencia que conviene
  saber: una `--plantilla` propia sin `%%indice` cae en la guardia de
  contenido (SIS-B-06), porque el índice nunca está vacío; es el mismo
  precedente que el anexo de EXT-8, y la plantilla se corrige añadiendo el
  marcador.
- **Qué haría falta:** una pestaña o un volcado que liste las corridas de la
  sesión y compare dos cualesquiera por el comparador; es presentación
  sobre objetos que ya existen.
- **Dónde vive:** `src/modulos/M11_reporte.py::indice_de_la_memoria`

## EB-06 · La ventana emergente conserva su campo único; las dos ventanas no se unifican

- **Qué se difirió:** montar los editores tipados también en la ventana
  normativa emergente (`gui/ventana_normativa.py`), que declara con UN
  `CampoValidable` y el mismo parser.
- **Por qué:** la emergente existe para LEER la norma —la tabla completa con
  sus notas, el rango con su semántica— y su campo declara lo que esa
  lectura decide; los editores tipados existen para COMPONER un valor
  estructurado, que es la pregunta de la pestaña 2. Las dos comparten el
  parser (EXT-5) y la puerta de declaración, que es lo que impide que
  diverjan; duplicar los editores en la emergente habría sido un segundo
  sitio donde mantener la misma composición.
- **Qué haría falta:** decidir si la emergente absorbe la pestaña 2 (una
  sola ventana de declaración), que es una decisión de producto y no de
  este cluster.
- **Dónde vive:** `gui/ventana_normativa.py::_pie`
