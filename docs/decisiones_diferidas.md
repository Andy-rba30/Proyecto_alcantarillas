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
- **No es** una lista de deuda pendiente. Diecinueve de las veintidós están
  **cerradas**: la decisión se tomó y se escribió. Lo que sigue abierto lleva
  su fila en el tracker (`docs/auditorias/matriz_cruzada_auditorias.xlsx`,
  hoja `Hallazgos`), que es donde se sigue el estado. Aquí se registra la
  DECISIÓN; allí, el ESTADO.

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

## SIS-A-13 · V2b (sedimentación / colmatación) no existe en ninguna línea

- **Qué se difirió:** la Fase 5 de la hoja de ruta enuncia once verificaciones
  y el programa implementa las que puede; V2b no está.
- **Por qué:** la colmatación es contenido de planos y de mantenimiento, no un
  cálculo con umbral que este programa pueda evaluar. El alcance reducido no
  estaba escrito, y ese era el defecto: un lector contaba nueve y esperaba once.
- **Qué haría falta:** que la hoja de ruta fije el umbral cuantitativo de
  colmatación, que hoy no fija.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::verificaciones_no_evaluadas`

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

## SIS-B-04 · «TW se calcula, no se mide» (Sec. 1.3) no está implementado

- **Qué se difirió:** el procedimiento de tres pasos de Sec. 1.3 —Q del
  receptor → tirante normal del receptor → TW—. `Q_receptor_m3s` y `cota_TW`
  se validan y no alimentan nada.
- **Por qué:** el caudal del receptor lo fija el Tablero 3.1 (ANA / Junta de
  Usuarios) y el expediente no lo tiene. Sin ese dato el procedimiento no
  arranca, y calcular TW con un caudal inventado sería peor que pedirlo.
- **Qué haría falta, y es más que el caudal:** el paso 2 entero. El TW sale de
  correr Manning **en la sección transversal del receptor**, y esa sección no
  es columna del CSV ni la trae ningún tablero. Con el caudal solo no se
  arranca.
- **Dónde vive:** `src/criterios_adoptados.py::TW_receptor`

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
  la más rica de dos: es la **única**. Dentro de `cli.correr`, lo único que
  corre fuera de `_etapa` es `M0_carga.cargar_puntos`, que no toca criterios y
  solo levanta `DatoFaltanteError`/`DatoInvalidoError`; ningún
  `CriterioPendienteError` alcanza el `except ErrorProyecto` de la ventana.
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
  del camino. **Declarado, no cerrado.**
- **Dónde vive:** `src/modelos.py::exigir_anios`

## SIS-B-09 · Constantes `NUMERAL_*` de módulo declaradas y nunca leídas

- **Qué se difirió:** nada, ya. Son ocho, no siete.
- **Por qué:** se cerró en S12 con un censo declarado y su razón.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/modelos.py::NUMERALES_DE_SECCION_SIN_LECTOR`

## SIS-B-10 · `legacy/Tc.py`: sin importadores, sin tests, sin barrido y sin estatus

- **Qué se difirió:** conservar 1320 líneas y 185 literales prohibidos que
  nadie importa, nadie prueba y ningún barrido recorre.
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
> `M11_reporte.PlantillaMemoria`.

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
- **Qué haría falta:** nada para M1. Queda declarado que **los demás bloques
  `Uso` no se ejecutan en la suite**: los de los otros doce módulos son
  fragmentos a propósito (parten de un `resultado` que el llamante ya tiene) y
  ejecutarlos exigiría inventarles un contexto, que es justo lo que el test
  evita.
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
- **Dónde vive:** `src/constantes_normativas.py::H_O_CONDICION_APLICACION`

## NOR-PRO-04 · La norma a la que se difiere la verificación del TMC

- **Cerrado:** la **atribución**. `clases_producto_por_relleno` y el docstring
  de M8 difieren a ASTM A796/A796M (con A798/A798M para instalación) y ya no a
  ASTM A-807, que no aparece en M 170M, M 36 ni A760.
- **Abierto:** transcribir la relación luz/corrugación de la Tabla 1 de A760 y
  la Tabla 6 de M 36. El criterio sigue vacío (verificado hoy: `valor=None`).
- **Qué haría falta, y son dos cosas de dificultad distinta:** la mitad del
  **concreto y la corrugación** se puede hacer —A760 y M 36 **están** en
  `normas/`, y S14 dejó comprobado que la Tabla 1 de A760 es legible
  renderizando su pág. PDF 3 a escala 2.0—, pero es **transcripción de tabla**,
  que es trabajo de la fase de citas y no de ésta. La mitad del **calibre del
  TMC por altura de cobertura** no se puede hacer en absoluto: **ASTM
  A796/A796M no está en `normas/`** (comprobado: las trece fuentes del
  directorio no la incluyen) y figura en la §15 del plan como una de las dos
  ausencias «fáciles» que desbloquean cosas concretas.
- **Dónde vive:** `src/criterios_adoptados.py::clases_producto_por_relleno`

## NOR-ANA-03 · La analogía de embocadura del HDPE

- **Cerrado:** la comparación que la ficha reclama está **declarada**. La fila
  alternativa (`Circular CM / Headwall`) vive en `sensibilidad`, y
  `verificacion_pendiente` dice con todas las letras que la fila adoptada da
  un HW **menor** y que ésa es la dirección insegura para V1, V4 y el
  resguardo.
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
- **Abierto, y la frontera no se ha movido:** el código que **construye
  widgets** sigue sin ejecutarse en la suite, tanto el viejo de `gui/app.py`
  como el nuevo de `gui/ventana_normativa.py`. No es descuido: probarlo con el
  doble de tkinter sería un espejismo —lo que se vería correr no es lo que
  corre en pantalla—, y la verificación real se hizo a mano bajo Xvfb sin que
  quedara en la suite.
- **Qué haría falta:** una suite con Tk real bajo servidor X virtual en la
  integración continua. Es infraestructura, no un test más.
- **Dónde vive:** `tests/test_gui_contrato.py::test_la_leyenda_nombra_exactamente_las_etiquetas_que_el_archivo_puede_tener`

## SIS-F-13 · Los módulos de cálculo sin caso patrón

- **Cerrado en S19 una de las tres razones:** `test_M5_verificaciones.py`
  consume ya CP-3 por la cadena de producción entera —catálogo de M2, Manning
  de M3, umbral de M5—, sin fabricar ningún dorado. Y la regla de `CLAUDE.md`
  «todo módulo de cálculo se contrasta contra `casos_patron`» **dejó de vivir
  solo en la constitución**: la ejecuta una guardia con la lista de exentos
  declarada, que además falla si un exento deja de serlo.
- **Abierto:** M2, M8 y M10 siguen sin caso patrón. **No es pereza de la fase
  de tests:** fabricarles un dorado sería inventar el valor de referencia, que
  es exactamente lo que prohíbe el conflicto #7 del plan. M11 no cuenta: es el
  módulo de reporte y no le corresponde dorado numérico.
- **Qué haría falta:** para M2, la serie de diámetros nominales tabulada de
  las normas de producto; para M8, AASHTO M 170M-04 Tablas 1 a 5 y ASTM
  A796/A796M; para M10, no una norma sino el expediente vial. Están en la §15
  del plan, y ahora también en la guardia, con su fuente concreta.
- **Dónde vive:** `tests/test_guardias_de_la_suite.py::SIN_CASO_PATRON`

---

# Parte IV — Un hallazgo nuevo que la suite no defendía

## MAT-D1 estaba corregido y no lo defendía ningún test

- **Qué pasó:** MAT-D1 —«V2 se evalúa con la rama `n_min`, que es la
  estimación alta: el conservadurismo queda invertido»— se corrigió hace
  varias sesiones. Al escribir el caso patrón de M5 se mutó
  `v2_velocidad_minima` de vuelta a `resultado.V_erosion` y **la suite entera
  quedó en verde**: 1497 tests.
- **Por qué era invisible:** todos los tests de V2 usaban `_resultado(V=...)`,
  que fija **las dos ramas al mismo número**. Con las dos iguales, la rama que
  se lea da igual y la mutación no cambia nada.
- **Qué se hizo:** un test que las separa a los dos lados del piso —la ventana
  que el propio docstring de la función describe, S entre 3.55e-5 y 6.01e-5—,
  de modo que solo hay una respuesta correcta. Verificado: mata la mutación.
- **Dónde vive:** `tests/test_M5_verificaciones.py::test_v2_decide_con_la_rama_de_n_MAXIMO_y_no_con_la_de_erosion`
