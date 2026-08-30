# Hoja de ruta de correcciones y construcción · v12

**Documento único. Reemplaza a los borradores v10 y v11, que no deben subirse: todo su
contenido vivo está aquí.**

*Proyecto_alcantarillas — Vía de evitamiento, distrito de La Unión (Piura).*
*Objetivo: cerrar el diseño a nivel de perfil, dejar el expediente técnico preparado, y
convertir la norma en dato para que las variables de entrada se elijan desde tablas
referenciadas y la memoria de cálculo sea sustentada y defendible.*

---

## 0. Cómo usar este documento

Este archivo tiene tres partes y una regla de convivencia:

| Parte | Qué es | Quién la lee |
|---|---|---|
| **I — Diagnóstico y diseño** (§1–§7) | Qué está mal, cómo debe quedar, y las reglas que impiden que arreglar una cosa rompa otra | Tú, y Claude Code cuando un prompt lo manda aquí |
| **II — Ejecución** (§8–§12) | 21 sesiones de Claude Code con su prompt, modelo y esfuerzo | Tú, al abrir cada sesión |
| **III — Cierre** (§13–§15) | Criterios de aceptación, antipatrones, deuda declarada | El revisor |

**La regla de convivencia:** este documento es el **plan**;
`docs/auditorias/matriz_cruzada_auditorias.xlsx` es el **tracker**. El estado de cada uno de
los 234 hallazgos se marca en el Excel, en sus columnas `Estado` / `Responsable` /
`Commit`. Nunca se abre un tercer documento para registrar avance.

**Advertencia de nombre de archivo:** `M11_reporte.ruta_hoja_de_ruta()` busca en `docs/` el
patrón `hoja_de_ruta_alcantarillas_v*.md` y **falla si encuentra más de uno**. Este archivo
se llama `hoja_de_ruta_correcciones_v12.md` y no colisiona — pero no renombres nada a
`hoja_de_ruta_alcantarillas_*`.

---

# PARTE I — DIAGNÓSTICO Y DISEÑO

## 1. Estado de partida

### 1.1 Inventario, medido sobre el clon de `origin/main`

| | |
|---|---|
| Módulos de cálculo | 13 (`M0`–`M11` + `MD`) |
| Criterios declarados | **46** — 30 `[A]` · 13 `[C]` · 2 `[N→]` · 1 `[S]` |
| Criterios **sin valor** | **23** de 46 |
| Criterios con rango de sensibilidad numérico | 15 |
| Tablas normativas (dicts) en `constantes_normativas.py` | **18** |
| Escalares `[N]` en el mismo archivo | 26 |
| Datos de sitio de corredor (`datos_sitio.py`) | 17 |
| Columnas del CSV por punto | 17 |
| GUI | 4 pestañas, 958 líneas, **584 sentencias ejecutables, 0 tests** |
| Plantillas de memoria | 2, con 21 marcadores `%%` |
| Suite | 725 `passed` + 1 `skipped` (726 `collected`) |

### 1.2 Lo que dejaron las tres auditorías externas

| Auditoría | Hallazgos | Lo que más pesa |
|---|---|---|
| **Sistema** | 97 (1 bloqueante · 14 graves · 43 menores · 39 obs.) | `SIS-A-01`: un criterio declarado desde la GUI gobierna el cálculo y la memoria lo imprime como *«sin valor declarado»* |
| **Normativa** | 92 (11 críticas · 37 altas · 31 medias · 4 bajas) | Tablas transcritas incompletas, modificadores omitidos, y valores de **este** proyecto endurecidos como constante |
| **Matemática** | 240 ítems · 16 defectos · 8 contradicciones entre normas | 6 defectos **invierten el conservadurismo declarado**; 2 son citas normativas falsas |

**Ningún defecto matemático produce hoy un número equivocado en el flujo validado** — pero
seis rompen el conservadurismo y viven en ramas que se activan justo cuando cierres el
nivel de perfil. Por eso van primero.

### 1.3 Lo que ya está bien y sirve de andamio

No hay que reconstruir nada. Media arquitectura de lo que necesitas ya existe:

- La **taxonomía de cinco etiquetas** (`[N] [N→] [S] [C] [A]`) y la regla que separa *tabla*
  de *elección*: `F_PGA_TABLA` es `[N]`, `F_pga` es `[A]`. **Ese es exactamente el patrón de
  la ventana emergente**, ya inventado y ya defendido. Falta generalizarlo a las 18 tablas.
- El **gobierno de criterios**: `valor()` registra el uso, un `None` lanza
  `CriterioPendienteError` y detiene el cálculo, y los tres caminos de declaración pasan por
  la misma guardia (`_verificar_criterio`).
- La **declaración en caliente** (`establecer_valor_dinamico`), sobre la que se apoya la
  ventana emergente.
- El **bloqueo por alcance** (`diferido_por_alcance`), sobre el que se apoya
  «perfil cerrado / expediente preparado».
- El objeto **`Verificacion`** (nunca un bool desnudo) y el `Bloqueo` con fundamento.
- Las **174 verificaciones matemáticas correctas** contra la fuente primaria: hidráulica de
  barril, control de entrada/salida, tirante crítico, las tres cartas del HDS-5, los FS de
  E.050. **El motor de cálculo es el activo más valioso del repo.**

---

## 2. El diagnóstico en una frase

Hoy la norma vive en el repositorio como **prosa**: el numeral en un comentario, el título
de la tabla en un string, la página en un docstring. La prosa no se puede mostrar en una
ventana, no se puede validar con un test, y no se puede imprimir en la memoria con garantía
de que sea cierta.

**El paso que desbloquea las tres cosas que quieres —perfil cerrado, ventana con tablas
referenciadas, memoria sustentada— es el mismo: convertir la norma en dato.**

Esto no es preferencia de estilo. Es lo que las auditorías demostraron:

- `NOR-MAN-04` — de 296 referencias `archivo:línea` del manifiesto, **al menos 66 no llevan
  a lo que dicen llevar**, y el test que las vigila no las atrapa porque solo comprueba que
  la línea exista, no que diga algo.
- `NOR-PUE-01` / `MAT-D5` — el numeral que sostiene la sobrecarga de tráfico en el trasdós
  (`2.1.4.3.9`) es en realidad **«Aparatos de Apoyo»**, propagado a 6 puntos del repo.
- `NOR-HID-01` / `MAT-O7` — el `9.8` de Laushey se atribuye a un numeral que **no escribe
  ningún decimal**.
- `MAT-O17` — páginas corridas: 76→77, C.2→C.6, 2.14→2.10, 982→984.
- `NOR-MEM-01` — el matiz «recomienda, no prohíbe» que el manifiesto declara como *lo único
  que la memoria imprime de V2* **aparece 0 veces en la memoria generada**.

La hoja de ruta v8 lo dice mejor (§0.5): **un vacío se ve; una cita falsa se cree.**

Una ventana emergente que muestre una tabla es una **superficie de citación**: todo lo que
aparezca ahí lo vas a leer —y lo va a leer el revisor— como «esto lo dice la norma».
Montarla sobre el estado actual multiplicaría el daño de las citas rotas.

---

## 3. Principio rector

Cinco reglas. Toda decisión posterior se resuelve con estas cinco.

> **R1 — La tabla es `[N]`, la elección de fila es `[A]`.**
> Elegir una fila en una ventana **no convierte la elección en norma**. La ventana escribe
> un criterio `[A]` cuyo valor *proviene de* la fila X de la tabla T. La memoria debe poder
> decir: «se adoptó X, elegido entre X₁…Xₙ de la Tabla T (numeral N, pág. P)».

> **R2 — Ninguna cita vive en un comentario.**
> Numeral, página, título de tabla y texto literal son **campos de un objeto**. Un
> comentario puede explicar; no puede ser la fuente. Es lo único que hace la cita testeable
> contra el PDF.

> **R3 — Lo que la ventana muestra es lo que la memoria imprime.**
> Mismo objeto, misma fuente, un solo lugar donde equivocarse. Si leen de sitios distintos,
> van a divergir — es literalmente `SIS-A-01` y `NOR-MEM-01`.

> **R4 — Una condición de aplicación no declarada bloquea; no se asume.**
> Muchas tablas traen condiciones (carriles por sentido, categoría de acero, relación a/c,
> «solo si el barril fluye lleno»). Si el proyecto no puede evaluarla, la ventana
> **pregunta o bloquea**. Nunca elige por ti.

> **R5 — Primero los números, después la vitrina.**
> Corregir el conservadurismo invertido antes de construir la interfaz que lo va a exhibir.

---

## 4. Arquitectura objetivo

### 4.1 El registro normativo — `src/normativa/`

Paquete nuevo. Es el corazón de toda la reforma.

| Archivo | Qué guarda |
|---|---|
| `fuentes.py` | El catálogo de documentos: los 13 PDF de `normas/` como objetos |
| `citas.py` | Toda referencia a un numeral, como dato verificable |
| `tablas.py` | Las 18 tablas normativas, completas, con notas y condiciones |
| `rangos.py` | Los rangos normativos, con su semántica declarada |
| `fundamentos.py` | El «por qué se hace esto» de cada paso, atado a su fase |
| `extraccion/` | Utilidades de solo lectura para contrastar cita contra PDF (soporte de tests) |

**Campos de `Fuente`**

| Campo | Para qué |
|---|---|
| `id` | Clave corta y estable (`MC_HHD`, `MP`, `E060`, `HDS5_3ED`, `AASHTO_LRFD_9`) |
| `titulo` | Nombre completo, tal como se cita en una memoria |
| `emisor`, `edicion`, `anio`, `resolucion` | RD 20-2011-MTC/14, RM 183-2026-VIVIENDA… |
| `archivo_pdf` | Ruta dentro de `normas/` |
| `sha1` | Para que la memoria declare contra **qué archivo exacto** se verificó |
| `desfase_pagina` | Página impresa vs página del PDF — el repo ya sufre esta diferencia |
| `ausente` | `True` para lo que se cita y **no está** en `normas/` (ver §15) |

**Campos de `Cita`**

| Campo | Para qué |
|---|---|
| `fuente_id` | Apunta a `Fuente` |
| `numeral` | `"4.1.1.3.7 c)"`, `"Tabla N° 09"`, `"Ec. 3.4b"` |
| `titulo_numeral` | El título **literal** del numeral. Es lo que atrapa a `NOR-PUE-01`: si el título dice «Aparatos de Apoyo», la cita se cae sola |
| `pagina_impresa` / `pagina_pdf` | Las dos, siempre. Cierra `MAT-O17` y `NOR-EG-01` |
| `texto_literal` | Transcripción exacta de la frase que sostiene el valor |
| `caracter` | `exigencia` · `recomendacion` · `permiso` · `definicion`. **Cierra `NOR-MEM-01` y `MAT-O13`**: el 0.25 m/s se *recomienda*, el 0.75 se aplica duro, y hoy solo uno lleva el matiz |
| `condiciones` | Condiciones de aplicación declaradas por la fuente |
| `verificado` | Fecha + quién + contra qué SHA del PDF |

**Campos de `TablaNormativa`**

| Campo | Para qué |
|---|---|
| `cita` | Su `Cita` (numeral, página, título literal de la tabla) |
| `titulo_literal` | **Completo, con unidades.** `NOR-HID-06` existe porque el título de la Tabla N° 10 se cita omitiendo «(m/s)» |
| `columnas` | Nombre + unidad + si el código la usa o no |
| `filas` | Cada fila con su etiqueta, sus valores y **su condición de aplicación** |
| `notas_al_pie` | Las notas son normativas. `NOR-AAS-01` se produce por ignorar el pie que define las categorías A/B/C de acero |
| `modificadores` | Factores que la fuente aplica sobre la tabla (el 0.8/1.0/1.2 por relación a/c de AASHTO 5.10.1 — `NOR-AAS-05`) |
| `completitud` | `completa` o `parcial`, **con la razón**. Si el código usa 2 de 3 columnas, la ventana lo dice |

> **Regla dura: la tabla se transcribe COMPLETA, aunque el cálculo use una parte.**
> Tres hallazgos independientes son el mismo error: `NOR-HID-11` (la Tabla N° 09 tiene tres
> columnas, el código transcribe dos y elige una subfila sin declararlo), `NOR-AAS-01` (la
> Tabla 5.10.1-1 tiene tres columnas por categoría de acero, el código toma una),
> `NOR-E060-05` (la Tabla 4.4 tiene dos escalas y seis cementos, el código lleva una y
> tres). **Una ventana que muestre una tabla mutilada es peor que no tener ventana.**

**Campos de `RangoNormativo`**

| Campo | Para qué |
|---|---|
| `minimo`, `maximo`, `abierto_por` | Bordes y si son inclusivos |
| `semantica` | **El campo que evita el error más caro.** Ver §4.2 |
| `unidad` | Explícita siempre |
| `cita` | De dónde sale el rango |
| `que_pasa_fuera` | ¿Incumple la norma? ¿Sale del dominio físico? ¿Deja de ser defendible la adopción? |

### 4.2 Tres cosas distintas que hoy se llaman «rango»

Tu pedido —*«que de manera explícita diga entre qué números debe estar mi valor»*— toca tres
objetos diferentes que el repositorio maneja por separado pero **nombra igual**. Si la
ventana los muestra con la misma cara, le enseña al usuario una lectura falsa de la norma.

| Tipo | Qué es | Dónde vive hoy | Qué debe decir la ventana |
|---|---|---|---|
| **Dominio físico** | Valores que el dato puede tomar antes de dejar de ser ese dato (CBR ≤ 100 %, esviaje < 90°) | `dominios.py` | «Fuera de esto la celda está mal llenada» — **no es normativo** |
| **Rango normativo** | La norma acota (n de Manning entre n_mín y n_máx de la Tabla N° 09; HW/D entre 1.0 y 1.5) | `constantes_normativas.py` | «La Tabla N° 09 del Manual de Hidrología, pág. X, da para este material n ∈ [0.011, 0.013]» |
| **Rango de sensibilidad** | Cuánto se movió la adopción `[A]` para defenderla en la memoria | campo `sensibilidad` de `Criterio` (15 lo tienen) | «Adopción del proyectista; se defiende mostrando el resultado en los extremos» |

> **Caso testigo, ya registrado como hallazgo.** `NOR-HID-04`: los dos números de la fila del
> concreto de la Tabla N° 10 (3.0 y 6.0 m/s) **son ambos máximos**, no un piso y un techo. La
> explicación que el repo imprime junto a la cita —«el rango recorre la calidad del
> revestimiento»— **no aparece en el Manual**: es interpretación del proyectista y se imprime
> como si fuera norma. En cuanto eso vaya a una ventana rotulada «rango», el usuario leerá
> 3.0 como mínimo. Por eso `semantica` admite `par_de_maximos` como valor distinto de
> `intervalo_admisible`.

### 4.3 Modo de resolución de cada variable de entrada

Cada variable declara **cómo se resuelve**. Eso le dice a la GUI qué ventana abrir y a M11
qué imprimir.

| Modo | Qué hace la ventana | Qué escribe en la memoria | Ejemplos |
|---|---|---|---|
| `libre` | Campo numérico con su dominio físico | Valor y su procedencia | `Q_m3s`, `cota_terreno` |
| `de_tabla` | **Muestra la tabla completa**, con numeral, página, notas y condiciones; el usuario elige fila | Valor + fila elegida + alternativas + cita | `F_pga`, `factor_muro_eleccion`, `n_manning`, `resguardo(CBR)`, `k_e`, cartas HDS-5 |
| `en_rango` | Campo numérico + el rango con su cita y su semántica; valida al escribir | Valor + rango + cita + qué pasaría fuera | `n` dentro de la Tabla N° 09, `HW/D` ≤ 1.5, `y/D` ≤ 0.75 |
| `derivada` | No editable; muestra de qué se deriva | La fórmula con su numeral | `TR` desde (R, n), `k_h0` desde `A_s` |
| `de_ensayo` | Campo + **trazabilidad obligatoria** (quién, cuándo, qué ensayo) | Trazabilidad, nunca sensibilidad | `cbr_subrasante`, `NF_profundidad_m`, `clase_sitio` |
| `de_catalogo` | Igual que `de_tabla` pero **rotulado como catálogo de proveedor, no como norma** | Valor + catálogo + advertencia | `D_MAX`, `diametros_normalizados` |

> `de_catalogo` **no existe hoy y hace falta.** `NOR-PRO-01` y `NOR-PRO-02`: los topes
> `D_MAX` (2.70 / 2.10 / 1.50 m) están atribuidos a AASHTO M170 y ASTM A760, y **esas normas
> tabulan hasta 3600 mm**. No son topes normativos: son topes de catálogo, y hoy descartan
> materiales en silencio. Mostrarlos rotulados como «norma» sería crear una cita falsa nueva.

> **Implementado en S15, y cuatro de los ejemplos de esta tabla no sobrevivieron al
> contraste.** El censo vive en `src/variables_entrada.py` (83 variables: 17 columnas + 7
> datos de sitio + 59 criterios) y el modo es el **tipo** del objeto `resolucion`, que
> `Criterio` y `DatoSitio` llevan ahora como campo. Las desviaciones están declaradas una a
> una, con su razón, en `variables_entrada.DESVIACIONES_DEL_PLAN`, y un test comprueba que
> siguen siendo desviaciones. Las cuatro se apartan **hacia el modo que promete menos**:
>
> - **`HW_D_max`** no es `en_rango` sino `libre`. El num. 2.2.5 d) del HDS-5 *describe* lo
>   que imponen las agencias de EE.UU. y no prescribe HW/D alguno (`NOR-HDS-02`, y el
>   conflicto vinculante **#1** de la §6 de este mismo plan). Un rango con cita normativa
>   devolvería la cita que ese hallazgo retiró.
> - **`factor_muro_eleccion`** no es `de_tabla` sino `libre`: el num. 2.8.1.1.14.2.2 **no
>   tabula nada**, autoriza una reducción, y el 1.0 adoptado es la *ausencia* de reducción.
> - **`resguardo(CBR)`** no es `de_tabla` todavía: su tabla existe y es `[N]`, pero vive como
>   escalares en `constantes_normativas.py` y no está transcrita al registro, y el criterio de
>   salida de esta misma §4.3 prohíbe un `de_tabla` sin tabla en el registro. Queda `libre`
>   con la tabla **nombrada** como pendiente.
> - **`diametros_normalizados`** no es `de_catalogo`: el ejemplo apunta al `max` que ese
>   criterio tenía cuando se escribió este plan, y **S4 lo mudó a `D_max_catalogo`** al cerrar
>   `NOR-PRO-01`/`NOR-PRO-02`. Lo que queda es la serie verificada contra ASTM A760 Tabla 1.
>
> **Defecto de la §1.1 de este plan, para corregir:** la fila «Datos de sitio de corredor
> (`datos_sitio.py`) | 17» es errónea. En el commit sobre el que se midió el inventario
> (`b8d70e5`) el archivo declaraba **3** datos; hoy son **7**. El 17 es el de la fila
> siguiente —las columnas del CSV— repetido. Mientras no se corrija, quien lea el plan sin
> abrir el archivo dimensionará esa población por seis.

### 4.4 La memoria: `PasoDeMemoria`

El cambio de fondo: hoy M11 **reconstruye** la memoria leyendo resultados —y declara en su
docstring que «no calcula nada nuevo» mientras calcula `y/D` en dos sitios (`SIS-A-07`)—.
Debe pasar a **formatear una traza que el cálculo emitió**.

| Campo | Contenido |
|---|---|
| `que` | Qué se está calculando |
| `por_que` | **El fundamento**: por qué la norma obliga o recomienda este paso. Sale de `fundamentos.py` |
| `formula` | La expresión tal como la transcribe la fuente, con su cita |
| `sustitucion` | Los valores entrando, con unidades y con la **procedencia** de cada uno |
| `resultado` | El número, con unidad y cifras significativas declaradas |
| `umbral` | Contra qué se compara, con su cita y su **carácter** (exigencia/recomendación) |
| `veredicto` | Cumple / no cumple / diferido, con el margen |
| `citas_textuales` | Las transcripciones literales que sostienen el paso |

---

## 5. Los 14 clusters — el mapa de «qué se rompe si toco esto»

Los 234 hallazgos están reagrupados **por causa raíz** en la hoja `Clusters` del `.xlsx`.
Un cluster es la unidad real de trabajo: sus hallazgos comparten archivo, fuente normativa o
error de fondo, y **se corrigen juntos, en un solo cambio de diseño y un solo commit**.

Solo 224 de los 234 caen en alguno de los 14 clusters. Los otros 10 —última fila de la tabla—
llevan `—` en la columna Cluster porque la auditoría los revisó y los cerró como correctos,
sin corrección que hacer: los nueve `NOR-OK-*` y `NOR-AAS-07`, retirado. **No son trabajo
pendiente**, y por eso no entran en ninguna fase ni consumen sesión.

| Cluster | Título | Hallazgos | Auditorías |
|---|---|---|---|
| C01 | Geometría física del conducto (pared, D exterior, topes de catálogo) | 12 | MAT+NOR |
| C02 | Sobrecarga de tráfico en el trasdós (h_eq) | 6 | MAT+NOR+SIS |
| C03 | Factores de carga AASHTO (Tabla 3.4.1-2) | 5 | MAT+NOR |
| C04 | Cadena sísmica y estabilidad del cabezal | 26 | MAT+NOR+SIS |
| C05 | Manning, doble n, V1/V2/V3 | 13 | MAT+NOR+SIS |
| C06 | Control de entrada/salida HDS-5 (V4b, K_fricción, h_o) | 10 | MAT+NOR+SIS |
| C07 | Recubrimiento y durabilidad (E.060 vs AASHTO) | 15 | MAT+NOR |
| C08 | Vacíos, criterios y su declaración en la memoria | 32 | MAT+NOR+SIS |
| C09 | Casos patrón, tests y guardianes | 34 | MAT+NOR+SIS |
| C10 | Bordes, validación, taxonomía de excepciones | 14 | MAT+SIS |
| C11 | Citas, numerales y páginas (documental) | 29 | MAT+NOR+SIS |
| C12 | Suelos: calicatas, resguardo, compactación | 8 | MAT+NOR |
| C13 | Rasante, longitud, geometría (M7 / 7.A-7.B) | 4 | MAT+SIS |
| C14 | GUI, CLI, código muerto, deuda de producto | 16 | SIS |
| — | Verificado correcto / retirado (9 OK + `AAS-07`) | 10 | — |

**Uso práctico:** antes de escribir una línea sobre un archivo, busca su cluster aquí. Si
tocas `M9_cabezal.py` o los factores de carga, estás en C03+C04 — 31 hallazgos combinados,
no se tocan por separado.

---

## 6. Los 8 conflictos — reglas vinculantes

Esto es lo que hace integral al plan: **cada fila es un caso donde la corrección obvia de un
hallazgo es la corrección equivocada**, porque otra auditoría ya descubrió por qué. Fuente
autoritativa: hoja `Conflictos` del `.xlsx`.

| # | Objeto | La corrección ingenua sería… | …pero | Resolución vinculante |
|---|---|---|---|---|
| **1** | V4b (HW/D ≤ 1.5) | Implementar el chequeo: la fórmula existe (`MAT-D2`) y dos docstrings dicen que ya corre (`SIS-A-02`) | El rango 1.0–1.5 del HDS-5 **es una encuesta de práctica de agencias de EE.UU., no un criterio del manual**, y está en otra página de la que se cita (`NOR-HDS-02`) | **No implementar todavía.** Primero reetiquetar de `[C]` a lo que corresponda y declarar de dónde sale el 1.5 |
| **2** | γ_EV mínimo | Corregir el par `{1.35, 0.90}` a otro par único | Hoy **no hay daño**: V7 consume solo el mínimo (0.90, correcto para conducto enterrado) y M9 solo el máximo (1.35, correcto para muro). Un fix ingenuo rompe uno de los dos | **Desglosar por tipo de estructura**: conducto enterrado 1.30/0.90, muro-estribo 1.35/**1.00** |
| **3** | Recubrimiento AASHTO 75 mm | Corregir 75 → 76.2 mm (3.0 in exactos) | 76.2 mm es la **Categoría A** (acero sin recubrir). Con galvanizado o epóxico AASHTO daría 50.8 mm y **la regla del mayor la ganaría E.060**, invirtiendo la conclusión. Falta además el modificador por a/c | **No corregir el número todavía.** Primero declarar categoría de refuerzo y factor a/c |
| **4** | h_eq de sobrecarga (0.60 m) | Subir a 1.12 m (fila de AASHTO para un cabezal de 2.0 m) | Para muro **paralelo** al tráfico con borde ≥0.3 m, la misma tabla da 0.61 m para toda altura | **No es contradicción, es dato faltante**: la orientación del muro. Declararla como dato de sitio y hacer h_eq función de (altura, orientación) |
| **5** | Relleno mínimo 0.30 m | Sumar el espesor de pared a la cota de clave (`MAT-D3`/`D4`) | Aunque sumes el espesor, **AASHTO 12.6.6.3 exige Bc/8 ≈ 0.36 m** para un tubo de 2.40 m; 0.30 m queda 5 mm bajo el piso de 12 in (`NOR-VAC-01`) | Los dos defectos **se acumulan sobre el mismo número**: está mal Y se mide desde el punto equivocado. Paquete único, con `SIS-A-03` |
| **6** | K_fricción SI (19.63 vs 19.62) | — | Sin conflicto: las tres auditorías coinciden en que el código (19.63) tiene razón | Hoja de ruta v8 a 19.63 en sus 4 menciones, actualizar líneas citadas en el comentario, retirar la frase de «coincidencia numérica» (K = 2g/φ² exacto) |
| **7** | Dorados de CP-1 | Corregir el fixture (70.63→70.59302, 35.29→35.32272) | Los dorados de CP-7 están **duplicados como literales** en `test_M9_cabezal.py`: corregir el fixture no llega ahí (`SIS-F-14`); y el claim «todos verificados con brentq» es falso (`MAT-O20`) | Corregir fixture + estrechar tolerancia + tests de M9 **leen del fixture** + retirar el claim. Va en F1, no en la fase de tests |
| **8** | Clase de Sitio F | Cablear `clase_sitio` a `criterios_usados()` (`SIS-B-01`) | La **premisa** —que el sitio es Clase F por licuefacción— no la sostiene ninguna de las dos tablas (`NOR-AAS-02`), y «Clase F» significa dos cosas incompatibles en el mismo expediente (`NOR-VOC-04`) | **No cablear todavía.** Resolver primero la premisa; cablear después. Al revés, la memoria declararía formalmente algo que la fuente no respalda |

---

## 7. Las cinco trampas que la reforma va a destapar

Aparecen **exactamente cuando construyas la ventana**. Si te toman por sorpresa, las
resolverás mal por prisa.

1. **Las tablas están transcritas incompletas.** `NOR-HID-11`, `NOR-AAS-01`, `NOR-E060-05` —
   mismo patrón, tres veces. La ventana las va a exhibir. Transcribir completo es más
   trabajo del que parece, y **es el trabajo**.
2. **Los modificadores están omitidos, y uno invierte una conclusión.** `NOR-AAS-05`: el
   factor por relación a/c de AASHTO 5.10.1 llevaría el recubrimiento de 76.2 a 61 mm, por
   debajo de los 70 mm de E.060.
3. **Tres cosas distintas se llaman «rango»** (§4.2), y una —el par de máximos de la Tabla
   N° 10— se explica hoy en la memoria con una interpretación que no está en el Manual.
4. **Hay condiciones de aplicación que el proyecto no puede evaluar todavía.** Carriles por
   sentido (`NOR-SUE-01`), categoría de acero (`NOR-AAS-01`), «solo si el barril fluye
   lleno» (`NOR-HDS-05`), «solo con refuerzo transversal mínimo» (`NOR-AAS-06`).
5. **Hay valores que parecen norma y son catálogo.** `D_MAX` es el caso claro.

Y una sexta, entre las normas y no del código: **8 contradicciones cruzadas** entre los
documentos de `normas/`. El proyecto ya resolvió bien varias, pero **sin dejarlo escrito** —
que es cómo nace `MAT-O2` (la errata de imprenta de `K_AE`).

---

# PARTE II — EJECUCIÓN CON CLAUDE CODE

## 8. Preparación, antes de la primera sesión

### 8.1 Unificar la constitución — hazlo primero

El repo tiene **dos archivos que difieren solo en mayúsculas, ambos rastreados en git**:

```
CLAUDE.md     2 202 bytes   (un puntero de 5 líneas)
Claude.md    10 838 bytes   (la constitución real)
```

En Linux conviven; en Windows y macOS el sistema de archivos es *case-insensitive* y **uno
pisa al otro al clonar**. Si trabajas en Windows, hay probabilidad real de que Claude Code
esté leyendo el puntero y creyendo que esa es toda la constitución.

**Prompt (Sonnet 5, esfuerzo `medium`):**

```
Fusiona el contenido completo de Claude.md dentro de CLAUDE.md, conservando el
texto íntegro y el orden actual de secciones. Elimina Claude.md del repositorio
(git rm) y retira de CLAUDE.md el párrafo puntero que pide leer el otro archivo,
que deja de tener sentido.

Busca en todo el repo (docs/, src/, tests/, gui/, cli.py) toda referencia textual
a "Claude.md" con esa grafía y actualízala a CLAUDE.md. Reporta cuántas
encontraste.

Razón, escríbela en el commit: los dos nombres difieren solo en mayúsculas y
colisionan en sistemas de archivos case-insensitive (Windows, macOS), donde uno
puede pisar al otro al clonar.

No cambies ninguna regla del contenido. Es una fusión, no una revisión.
```

### 8.2 Añadir a `CLAUDE.md` el bloque de reglas de corrección

`CLAUDE.md` es lo que Claude Code lee en **cada** sesión sin que se lo pidas. Las reglas que
impiden romper un hallazgo al arreglar otro tienen que vivir ahí. Pega esto al final:

```markdown
## Reglas de corrección de hallazgos de auditoría

Este repositorio tiene 234 hallazgos de tres auditorías externas, ya cruzados en
`docs/auditorias/matriz_cruzada_auditorias.xlsx` (14 clusters por causa raíz, 8
conflictos resueltos). Ese archivo es el TRACKER: el estado de cada hallazgo se
marca ahí, en las columnas Estado / Responsable / Commit. El PLAN es
`docs/hoja_de_ruta_correcciones_v12.md`.

1. Antes de tocar un archivo, busca su cluster en la hoja `Clusters`. Un cluster
   se corrige entero, en un solo cambio de diseño y un solo commit. Nunca
   hallazgo por hallazgo. Solo 224 de los 234 caen en alguno de los 14
   clusters: los otros 10 llevan `—` en la columna Cluster (los nueve
   `NOR-OK-*` y `NOR-AAS-07`, retirado) porque la auditoría los cerró como
   correctos, sin corrección que hacer. No son trabajo pendiente.
2. Antes de aplicar cualquier corrección, consulta la hoja `Conflictos` (o la §6
   del plan). Ocho objetos del repositorio tienen una corrección "obvia" que es
   la EQUIVOCADA porque otra auditoría descubrió por qué. Si el objeto que vas a
   tocar está ahí, la resolución de esa fila es vinculante y sustituye a tu
   criterio.
3. Ancla todo por NOMBRE DE SÍMBOLO (función, constante, clave de criterio),
   nunca por número de línea. Al menos 66 de 296 referencias archivo:línea del
   manifiesto no llevan a lo que dicen llevar, y las auditorías corren sobre dos
   commits distintos (71b134fb y 2e1708ab).
4. Cita los IDs siempre con prefijo MAT- / SIS- / NOR-. `F-01` y `F-02`
   significan hallazgos DISTINTOS en la auditoría Normativa y en la de Sistema.
5. No escribas tests contra el comportamiento actual antes de cerrar las fases
   de corrección: congelarías los defectos. Los tests van en su fase, después.
6. Cuando el código y la hoja de ruta discrepan, el defecto se reporta contra la
   hoja de ruta primero y la fuente primaria (el PDF en normas/) decide.
```

### 8.3 Crear los tres subagentes del proyecto

Son **archivos de texto** en `.claude/agents/`. Es lo que hace seguro usar `ultracode` más
adelante: cuando Claude Code reparte trabajo, lo reparte entre **estos** especialistas, que
conocen las reglas, y no entre agentes genéricos.

Se cargan **al arrancar la sesión**: créalos y **reinicia Claude Code**.

**`.claude/agents/verificador-normativo.md`**

```markdown
---
name: verificador-normativo
description: Verifica una cita normativa (numeral, título, página, texto literal) contra el PDF en normas/. Solo lectura. Úsalo PROACTIVAMENTE antes de aceptar cualquier valor [N] o [N->].
tools: Read, Grep, Glob, Bash
model: opus
effort: high
---
Verificas citas contra la fuente primaria. Nunca corriges código.

Para cada cita que se te pase, devuelve:
1. Si el numeral EXISTE en el documento y cuál es su TÍTULO LITERAL impreso.
2. La página impresa y la página del PDF (no son la misma; declara ambas).
3. Si el texto literal que el repo atribuye aparece de verdad en esa página.
4. Si el valor numérico está en la fuente o es una interpretación.
5. Veredicto: CONFIRMA / CONTRADICE / NO VERIFICABLE con lo adjunto.

Regla dura: si un numeral existe pero su título no corresponde al contenido que
el repo le atribuye, eso es CONTRADICE, no un detalle. Es el defecto que el
expediente declara el más grave (NOR-PUE-01: el numeral que sostenía la
sobrecarga de tráfico resultó ser "Aparatos de Apoyo").

Nunca inventes una página. Si no la puedes leer, di NO VERIFICABLE.
```

**`.claude/agents/auditor-adversarial.md`**

```markdown
---
name: auditor-adversarial
description: Intenta refutar una corrección que otro agente acaba de hacer. Solo lectura. Úsalo antes de cerrar cualquier cluster.
tools: Read, Grep, Glob, Bash
model: opus
effort: high
---
Tu trabajo es intentar demostrar que la corrección que se te presenta está mal.
No la escribiste tú y no tienes que defenderla.

Comprueba, en este orden:
1. ¿La corrección toca un objeto de la hoja `Conflictos` de
   docs/auditorias/matriz_cruzada_auditorias.xlsx (o la §6 del plan)? Si sí,
   ¿respeta la resolución vinculante, o aplicó la "corrección obvia" prohibida?
2. ¿Rompe algún consumidor existente? Búscalos por nombre de símbolo, con grep,
   en src/, cli.py, gui/app.py y tests/.
3. ¿Introduce un literal numérico fuera de constantes_normativas.py,
   criterios_adoptados.py o datos_sitio.py, sin marca `# literal-ok`?
4. ¿Rellena algún vacío en silencio? Es la regla nuclear del proyecto.
5. ¿El conservadurismo va en la dirección que el docstring declara? Recomputa a
   mano con un caso numérico concreto; no confíes en la afirmación del código.

Devuelve: REFUTADO (con el caso numérico que lo rompe), AJUSTADO (qué matiz
falta) o CONFIRMADO. Si no encuentras nada, dilo, pero solo después de haber
intentado los cinco puntos.
```

**`.claude/agents/explorador.md`**

```markdown
---
name: explorador
description: Mapeo de solo lectura del repositorio. Encuentra consumidores, definiciones y referencias cruzadas. Devuelve un resumen corto.
tools: Read, Grep, Glob
model: haiku
---
Exploras y reportas. Nunca modificas archivos.

Devuelve rutas y nombres de símbolo, nunca números de línea como única
referencia. Sé breve: el que te llamó tiene su ventana de contexto ocupada.
```

**Cómo crearlos:** pídeselo a Claude Code (*«Lee la §8.3 de
docs/hoja_de_ruta_correcciones_v12.md y crea la carpeta .claude/agents/ con los tres
archivos, con el contenido exacto que aparece ahí; no los reescribas ni cambies el modelo o
el esfuerzo declarados»*) o créalos a mano. Después **reinicia**, y verifica con: *«lista
los subagentes disponibles y dime el modelo y esfuerzo de cada uno»*.

---

## 9. Cómo elegir modelo y esfuerzo

**Modelo** es lo que sabe; **esfuerzo** es cuánto se esfuerza. Se configuran por separado,
con `/model` y `/effort`.

| | |
|---|---|
| **Modelo** | Fable 5 (el especialista) · Opus 5 (el experto) · Sonnet 5 (el generalista muy bueno) · Haiku 4.5 (barato, explorar) |
| **Esfuerzo** | `low` · `medium` · `high` · `xhigh` · `max` · **`ultracode`** |

### Sobre `ultracode`

Ultracode no es un nivel más alto de razonamiento: es un ajuste de Claude Code que envía
`xhigh` al modelo **y además hace que Claude orqueste flujos de trabajo dinámicos** para
tareas sustanciales. Es decir, reparte la tarea entre subagentes y encarga la verificación a
un agente que no escribió la respuesta que juzga.

**La advertencia que importa para este proyecto.** El reparto automático es justo lo que
quieres en trabajo ancho e independiente (62 citas contra 13 PDFs), y **justo lo que NO
quieres donde hay conflictos cruzados**. Ejemplo, el conflicto #5:

> Un agente recibe `MAT-D3/D4` y suma el espesor de pared a la cota de clave. Otro recibe
> `NOR-VAC-01` y ve que AASHTO exige Bc/8 ≈ 0.36 m. Cada uno «cierra» su hallazgo. Ninguno
> ve que **los dos defectos se acumulan sobre el mismo número**. La matriz existe
> precisamente para impedir eso, y el fan-out la evade.

**Regla de este proyecto:** `ultracode` donde el trabajo es **ancho e independiente**;
esfuerzo `high` en sesión única y secuencial donde el trabajo es **estrecho y acoplado**. Y
si usas `ultracode`, que sea con los subagentes de §8.3 ya cargados.

### Sobre Fable 5

Cuesta el doble que Opus 5 por token y, en planes Max, consume hasta el 50 % del límite
semanal — puede agotarse mientras Opus todavía tiene margen. Resérvalo para las **dos
decisiones donde el problema es genuinamente raro**: el diseño del registro normativo (S11)
y la premisa de Clase de Sitio F (S13). Para todo lo demás, Opus 5 es el caballo de batalla
y en suscripción no cuesta extra.

---

## 10. Tabla maestra de sesiones

| Sesión | Trabajo | Clusters | Hallazgos | Modelo | Esfuerzo | Plan mode |
|---|---|---|---|---|---|---|
| **S0** | Preparación (§8) | — | — | Sonnet 5 | medium | no |
| **S1** | Reconciliar línea base | — | 0 | Sonnet 5 | high | no |
| **S2–S10** | Corrección de fondo | C08, C09, C01, C05, C06, C13, C03, C04, C07 | 16 | **Opus 5** | **high** | **sí** |
| **S11** | Diseño del registro normativo | — | — | **Fable 5** | high | sí |
| **S12** | Citas y transcripciones | C11, C12, C02 | 62 | Opus 5 | **ultracode** | no |
| **S13** | Premisa Clase de Sitio F | (C04) | — | **Fable 5** | high | sí |
| **S14** | Vacíos y cableado | C01, C04, C06, C08, C11 | 40 | Opus 5 | high | sí |
| **S15** | Modo de resolución de variables | — | — | Opus 5 | high | sí |
| **S16** | Tests y guardianes | C09, C10 | 33 | Opus 5 | **ultracode** | no |
| **S17** | Ventana emergente | (C14) | — | Opus 5 | high | sí |
| **S18** | Memoria sustentada | — | — | Opus 5 | high | sí |
| **S19** | Deuda y GUI | C14 + resto | 73 | Opus 5 | ultracode | no |
| **S20** | Cierre del nivel de perfil | — | — | Opus 5 | high | sí |
| **S21** | Contrato de expediente | — | — | Opus 5 | high | sí |

**Las nueve sesiones S2–S10 son una por cluster, a propósito.** Es la etapa con los
conflictos acoplados; una sesión por cluster mantiene la ventana de contexto limpia y el
commit atómico. Orden: **C08** (el bloqueante) → **C09** (los dorados de CP-1, porque
validan todo lo demás) → C01 → C05 → C06 → C13 → C03 → C04 → C07.

**Por qué S2–S10 dice 16 y no 20.** La columna `Hallazgos` de esta tabla es el conteo de
filas de la hoja `Hallazgos` por fase, no el de filas que la sesión tocó. Las nueve
sesiones sí trabajaron veinte: cuatro —`MAT-D2`, `SIS-A-02` (S6) y `SIS-B-01`, `SIS-D-01`
(S9)— quedaron en «Cerrado parcial» porque los conflictos #1 y #8 prohíben cablearlos
antes de cerrar su premisa, y lo que les queda abierto es el cableado, que es S14. Por eso
se reasignaron a F3 y por eso S14 pasa de 36 a 40: son las mismas cuatro filas, contadas
donde se van a cerrar. Estaban en F1 con F1 ya consumida, o sea que ninguna sesión que
filtre por fase las habría vuelto a mirar.

---

## 11. Los prompts

### S1 · Reconciliar la línea base

**Sonnet 5 · `high` · sin plan mode.** Trabajo mecánico de amplitud; no necesita juicio
profundo, sí necesita no saltarse archivos.

```
Lee CLAUDE.md, docs/hoja_de_ruta_correcciones_v12.md (§1 y §5) y la hoja `Léeme`
de docs/auditorias/matriz_cruzada_auditorias.xlsx.

Objetivo: dejar la línea base reconciliada antes de tocar una línea de cálculo.
No corrijas ningún hallazgo en esta sesión.

1. Determina el SHA actual de origin/main. Genera el diff entre 71b134fb
   (auditorías Matemática y Normativa), 2e1708ab (auditoría de Sistema) y el
   HEAD actual. Reporta qué archivos cambiaron entre esos tres puntos.

2. Para cada hallazgo de la hoja `Hallazgos` cuya columna de ubicación traiga un
   archivo:línea, verifica si esa línea sigue apuntando a lo que el hallazgo
   describe. Donde no, reancla al NOMBRE DEL SÍMBOLO y anota el reanclaje. Usa el
   subagente `explorador` para las búsquedas.

3. Corre la suite sobre origin/main, no sobre el clon local ni sobre una rama.
   Reporta passed y collected por separado (hoy hay 1 skipped permanente, así
   que collected = passed + 1).

4. Arregla estas cuatro deudas de línea base, cada una en su commit:
   - CLAUDE.md dice que constantes_fisicas.py tiene "hoy solo la gravedad" y son
     cinco nombres (SIS-A-15).
   - La lista de dependencias de CLAUDE.md incluye jinja2 y pandas (cero usos, no
     instalados) y omite weasyprint, que sí está pineado (SIS-B-03).
   - docs/auditoria_y_ruta_despliegue_v9.md sigue citando "12 módulos, 595 tests"
     (SIS-F-18).
   - tests/ejemplo_puntos.informe.json es salida de corrida versionada que
     cualquier ejecución de la CLI pisa, y .gitignore no la cubre (SIS-C-10).

Entregable: docs/linea_base.md con el diff resumido, la tabla de reanclajes y el
conteo de tests leído de origin/main.

Criterio de salida: no queda ninguna referencia de la matriz anclada solo a un
número de línea.
```

---

### S2 · Cluster C08 — el bloqueante

**Opus 5 · `high` · plan mode SÍ.** Es el único hallazgo que hoy produce una memoria
equivocada, y toca la frontera entre GUI, criterios y reporte.

```
Cluster C08 de la matriz. Lee CLAUDE.md, la §6 de
docs/hoja_de_ruta_correcciones_v12.md (los 8 conflictos) y la fila C08 de la
hoja `Clusters` antes de proponer nada.

El hallazgo central es SIS-A-01, el ÚNICO BLOQUEANTE de las tres auditorías:
M11_reporte.bloque_criterios lee ca.criterio(clave).valor —el valor del archivo—
y nunca consulta _OVERRIDES. Consecuencia: un criterio declarado desde la GUI
"solo para esta corrida" gobierna el cálculo y la memoria lo imprime como "sin
valor declarado". El bloque de vacíos tampoco lo lista.

Prioridad absoluta porque toda la ventana emergente que se construirá en S17
declara valores por esa vía: sin este arreglo, cada valor elegido en una ventana
saldría en la memoria como no declarado.

Trabajo:
1. Hacer que la memoria imprima el valor EFECTIVO de todo criterio, distinguiendo
   visiblemente el declarado en caliente del transcrito en el archivo. Un
   override no es un valor [N]: la memoria debe decir de dónde vino.
2. Cerrar SIS-A-04: `cota_entrada_supuesta` adopta cota_terreno como cota de
   fondo y gobierna V4, V7 y la rasante de M7/M8, sin entrada en
   criterios_adoptados.py, sin Anexo A, y M11 imprime el número sin marcarlo como
   supuesto. Es la regla nuclear del proyecto incumplida.
3. El resto de los 32 hallazgos de C08 según la hoja `Hallazgos` filtrada por
   Cluster = C08.

Restricciones:
- No toques ninguna fórmula de cálculo. C08 es declaración y reporte.
- El camino de declaración sigue siendo establecer_valor_dinamico(), que ya pasa
  por _verificar_criterio(). No inventes un segundo camino.
- Ningún literal numérico nuevo fuera de los tres archivos permitidos.

Antes de cerrar: lanza el subagente `auditor-adversarial` sobre tu propio cambio.
Si te refuta, corrige y vuelve a lanzarlo.

Criterio de salida (verificable): correr la CLI declarando un criterio en
caliente y comprobar en el HTML generado que ese criterio aparece con su valor
efectivo Y con la marca de que fue declarado para la corrida. Suite verde en
origin/main. Columna Estado actualizada para los 32 hallazgos de C08.
```

---

### S3 · Cluster C09 (parte) — los dorados de CP-1

**Opus 5 · `high` · sin plan mode.** Acotado y quirúrgico, pero con una trampa: el fixture
no es la única copia.

```
Cluster C09, PARTE DE CASOS PATRÓN ÚNICAMENTE. NO escribas tests nuevos en esta
sesión: eso es S16, y hacerlo ahora congelaría los defectos aún sin corregir.

Lee el conflicto #7 de la §6 del plan. En resumen:

MAT-D7 y SIS-F-03 coinciden dígito a dígito: los valores dorados de CP-1 en
tests/fixtures/casos_patron.py (TR = 70.63 y 35.29) NO salen de la fórmula que el
propio fixture declara. Los correctos son 70.59302 y 35.32272. Con la tolerancia
de 0.05, la ventana queda centrada en un número falso y la implementación
CORRECTA pasa con margen de solo 0.013.

Trabajo:
1. Corregir los dorados a 70.59302 y 35.32272.
2. Estrechar la tolerancia: 0.05 es lo que dejaba pasar el error.
3. SIS-F-14: los dorados de CP-7 están DUPLICADOS como literales en
   tests/test_M9_cabezal.py. Corregir el fixture no llega ahí. Hacer que esos
   tests lean del fixture.
4. MAT-O20: el claim "todos los valores verificados con brentq" es falso — el
   bloque __main__ solo autoverifica CP-2 y CP-8. Retirarlo o hacerlo cierto.

Los redondeos publicados (71 y 35 años) no cambian. Verifica que
M1_clasificacion siga imprimiendo lo mismo.

Criterio de salida: recomputar TR a mano en doble precisión y que coincida con el
fixture; los tests de M9 sin literales dorados; suite verde.
```

---

### S4–S10 · Clusters restantes de corrección

**Opus 5 · `high` · plan mode SÍ en C01, C04 y C07.**

**Plantilla** — sustituye `<CXX>`:

```
Cluster <CXX> de docs/auditorias/matriz_cruzada_auditorias.xlsx.

Antes de proponer nada:
1. Lee CLAUDE.md.
2. Lee la fila <CXX> de la hoja `Clusters`: causa raíz y línea de ataque.
3. Lee la §6 ENTERA de docs/hoja_de_ruta_correcciones_v12.md (los 8 conflictos).
   Si algún objeto de este cluster aparece ahí, la resolución de esa fila es
   VINCULANTE y sustituye a tu criterio, aunque la corrección obvia parezca otra.
4. Filtra la hoja `Hallazgos` por Cluster = <CXX> y lista los hallazgos.

Trabajo: corregir el cluster ENTERO en un solo cambio de diseño y un solo commit.
No hallazgo por hallazgo.

Restricciones invariables:
- Ancla por nombre de símbolo, nunca por número de línea.
- Ningún literal numérico fuera de constantes_normativas.py (solo [N] con numeral
  verificado), criterios_adoptados.py o datos_sitio.py.
- Un vacío jamás se rellena en silencio: valor=None, etiqueta [A], justificación,
  y el cálculo se detiene con la excepción de la taxonomía.
- No escribas tests nuevos: eso es S16.
- Si la hoja de ruta v8 y el código discrepan, el defecto se reporta contra la
  hoja de ruta primero y el PDF de normas/ decide.

Antes de cerrar: subagente `auditor-adversarial` sobre tu propio cambio, con un
caso numérico concreto recomputado a mano. Si te refuta, corrige.

Criterio de salida: <el del cluster> + suite verde en origin/main + columna Estado
actualizada en el .xlsx.
```

**Contexto específico por cluster** (pégalo debajo de la plantilla):

> **S4 · C01 — Geometría física del conducto.** *Plan mode obligatorio. Conflicto #5:*
> `MAT-D3`, `MAT-D4` y `NOR-VAC-01` **se acumulan sobre el mismo número**. El valor de
> relleno mínimo está mal (AASHTO 12.6.6.3 tabula Bc/8 ≈ 0.36 m para un tubo de 2.40 m;
> 0.30 m queda 5 mm bajo el piso de 12 in) **Y** se mide desde el punto equivocado (la cota
> de clave usa el diámetro interior, sin espesor de pared). Corregir uno solo deja el número
> corto igual. Además `SIS-A-03`: ocho docstrings lo declaran pendiente cuando ya tiene
> valor. Y `NOR-PRO-01/02`: los topes `D_MAX` no salen de las normas que se les atribuyen —
> son topes de catálogo; reetiquetarlos como tales (ver `de_catalogo` en §4.3).

> **S5 · C05 — Manning y velocidades.** `MAT-D1`: V2 (piso de velocidad ≥ 0.25 m/s) se
> evalúa con la rama `n_min`, que es la estimación **alta**. Para un piso, el extremo
> conservador es `n_max`. El fixture CP-3 ya modela el umbral con `n_max`: el repo se
> contradice a sí mismo. Además completar las transcripciones de las Tablas 02, 09 y 10 — la
> 09 tiene tres columnas y el código lleva dos.

> **S6 · C06 — Control HDS-5.** *Conflicto #1, vinculante:* **NO implementes V4b todavía.**
> El rango HW/D 1.0–1.5 es una encuesta de práctica de agencias de EE.UU., no un criterio
> del HDS-5. Primero reetiquetar el criterio y declarar de dónde sale el 1.5. Sí va aquí:
> acotar `HW ≥ 0` (`MAT-D10`: hoy da HW negativo con S grande y Q chico) y la hoja de ruta a
> 19.63 en sus cuatro menciones (conflicto #6).

> **S7 · C13 — Rasante y geometría.** `MAT-D9`: `_fase_7` llama a
> `compatibilidad_geometrica()` sin S, así que cae al default `S_cauce` aunque el punto
> declare `S_conducto`. Dos pendientes distintas conviven en el mismo punto. Y
> `MAT-O5`/`O6`: la hoja de ruta escribe V4 y 7.A mezclando carga (m sobre el fondo) con
> cota (msnm), sin datum — el código lo corrige, la hoja no.

> **S8 · C03 — Factores de carga.** *Conflicto #2, vinculante:* no corrijas el par
> `{1.35, 0.90}` a otro par único. **Desglosa por tipo de estructura**: conducto enterrado
> 1.30/0.90, muro-estribo 1.35/**1.00**. Hoy V7 consume solo el mínimo y M9 solo el máximo,
> así que un fix ingenuo rompe uno de los dos.

> **S9 · C04 — Cadena sísmica.** *Plan mode obligatorio. 26 hallazgos, el cluster más
> grande. Conflicto #8, vinculante:* **no cablees `clase_sitio` en esta sesión** — eso se
> resuelve en S13. Lo que sí va aquí: `MAT-O2` — el Manual de Puentes imprime `K_AE` con
> «1 − √(…)», que es **errata de imprenta**; el código sigue bien a AASHTO y la discrepancia
> **no está documentada**. Documentarla es el trabajo; NO «corregir» el código contra el
> literal del Manual.

> **S10 · C07 — Recubrimiento.** *Plan mode obligatorio. Conflicto #3, vinculante:* **no
> corrijas 75 → 76.2 mm.** Parece la corrección obvia y es la equivocada. Los 3.0 in son la
> Categoría A (acero sin recubrir); con galvanizado o epóxico AASHTO daría 50.8 mm y la
> regla del mayor la ganaría E.060, invirtiendo la conclusión. Falta además el modificador
> por relación a/c (0.8 con a/c ≤ 0.40, que es el que el proyecto adopta). **Primero declarar
> categoría de refuerzo y factor a/c**; el valor queda determinado después.

---

### S11 · Diseño del registro normativo

**Fable 5 · `high` · plan mode SÍ.** De esta decisión cuelgan la ventana, la memoria y 62
correcciones de citas. Equivocar el esquema cuesta rehacer dos etapas. **Una sola sesión.**

```
Diseña —sin implementar todavía— el registro normativo de la §4.1 de
docs/hoja_de_ruta_correcciones_v12.md.

Contexto: hoy la norma vive en este repositorio como PROSA. El numeral en un
comentario, el título de la tabla en un string, la página en un docstring. Eso
hace imposibles las tres cosas que el proyecto necesita: mostrar una tabla en una
ventana emergente, validar una cita con un test, e imprimir una cita en la
memoria con garantía de que sea cierta.

Lee antes:
- src/constantes_normativas.py entero (18 tablas, 26 escalares).
- docs/manifiesto_citas.md.
- Las §2, §4.1, §4.2, §4.3 y §7 del plan.
- Las hojas `Clusters` (C11, C12, C02) y `Conflictos` de la matriz.

Entregable: docs/diseno_registro_normativo.md, que resuelva y justifique:

1. El esquema exacto de Fuente, Cita, TablaNormativa, RangoNormativo, FilaDeTabla
   y Fundamento. Campos, tipos, invariantes.
2. Cómo se representa una tabla que el cálculo usa PARCIALMENTE. La Tabla N° 09
   tiene tres columnas y el código lleva dos; la Tabla 5.10.1-1 tiene tres
   categorías de acero y el código lleva una. La ventana las va a exhibir. ¿Cómo
   se declara "completa pero uso parcial" sin que parezca error?
3. Cómo se representan los MODIFICADORES que la fuente aplica sobre una tabla —
   el factor 0.8/1.0/1.2 por relación a/c de AASHTO 5.10.1, que puede invertir
   qué norma gobierna.
4. Cómo se representa una CONDICIÓN DE APLICACIÓN que el proyecto todavía no
   puede evaluar (carriles por sentido, categoría de acero, "solo si el barril
   fluye lleno"). Debe poder bloquear, no asumir.
5. Las tres cosas que hoy se llaman "rango" (§4.2) y el caso NOR-HID-04: los dos
   números de la Tabla N° 10 son AMBOS máximos, y la explicación que el repo
   imprime junto a la cita no está en el Manual. ¿Cómo evita el esquema que la
   ventana enseñe una lectura falsa?
6. Cómo se marcan las fuentes que se citan y NO están en normas/ (§15 del plan).
7. Qué tests hacen falta para que una cita no pueda volver a pudrirse, y cuál de
   ellos habría atrapado NOR-MAN-04 (66 de 296 referencias rotas) y NOR-PUE-01
   (el numeral que resultó ser "Aparatos de Apoyo").
8. La ruta de migración: constantes_normativas.py NO puede romperse de golpe.
   ¿Cómo convive el registro con él mientras se migra?

No escribas código de implementación. Entrega el diseño con ejemplos concretos de
dos tablas reales del repo (una completa, una parcial) escritos como datos.
```

---

### S12 · Citas y transcripciones

**Opus 5 · `ultracode`.** ← *La sesión donde ultracode gana claramente:* 62 hallazgos, cada
cita verificable contra su PDF de forma independiente, y la verificación separable de la
corrección.

```
Clusters C11 (29 hallazgos), C12 (8) y C02 (6). Implementa el registro normativo
según docs/diseno_registro_normativo.md.

Esta es la clase de defecto que el propio expediente declara la más grave
(hoja_de_ruta_v8 §0.5): "un vacío se ve; una cita falsa se cree".

Trabajo, en orden:
1. Construir src/normativa/ según el diseño aprobado.
2. Cargar las 13 fuentes de normas/ con SHA y desfase de página impresa vs PDF.
   Declarar las fuentes ausentes (§15 del plan).
3. Migrar las 18 tablas de constantes_normativas.py, COMPLETAS: todas las
   columnas, todas las filas, todas las notas al pie, todos los modificadores.
   Marcar cuáles usa el cálculo parcialmente y por qué.
4. Reconstruir cada cita: numeral + TÍTULO LITERAL DEL NUMERAL + página impresa +
   página PDF + texto literal + carácter (exigencia / recomendación / permiso /
   definición).
5. Escribir la guardia: los tests del punto 7 del diseño.
6. Generar el manifiesto de citas DESDE el registro, en vez de mantenerlo a mano.

Para cada cita usa el subagente `verificador-normativo`. No aceptes ninguna cita
que no haya pasado por él. Si devuelve NO VERIFICABLE, la cita se marca como tal:
no se inventa una página.

Verifica uno por uno los hallazgos de Cluster IN (C11, C12, C02). Los de mayor
consecuencia:
- NOR-PUE-01 / MAT-D5: el numeral 2.1.4.3.9 que sostiene la sobrecarga de tráfico
  en el trasdós es "Aparatos de Apoyo". El texto real está en 2.4.2.2. El numeral
  falso está propagado a 6 puntos del repo.
- NOR-HID-01 / MAT-O7: el 9.8 de Laushey se atribuye a un numeral que no escribe
  ningún decimal.
- NOR-MAN-04: al menos 66 de 296 referencias del manifiesto no resuelven.
- MAT-O17: páginas corridas (76→77, C.2→C.6, 2.14→2.10, 982→984).
- NOR-SUE-01 / MAT-D11: el Cuadro 4.1 SÍ condiciona 4 vs 6 calicatas (por
  carriles por sentido) y el código afirma que no lo dice.
- Conflicto #4 (h_eq, cluster C02): NO subas h_eq a 1.12 m sin más. No es
  contradicción, es DATO FALTANTE: la orientación del muro respecto al tráfico.
  Para muro paralelo con borde ≥ 0.3 m la misma tabla da 0.61 m. Declarar la
  orientación como dato de sitio y hacer h_eq función de (altura, orientación).
- Conflicto #6: hoja de ruta a 19.63 en sus cuatro menciones (436, 440, 797,
  908), actualizar las líneas citadas en el comentario de constantes_normativas,
  retirar la frase de "coincidencia numérica" (K = 2g/φ² exactamente).

Criterio de salida: cero numerales inexistentes; toda página verificada contra el
PDF; hoja de ruta a 19.63; manifiesto resincronizado; un test que falle si una
cita no resuelve. Y el criterio que habilita la ventana: TODA TABLA TRANSCRITA
COMPLETA, con notas y modificadores.
```

---

### S13 · La premisa de Clase de Sitio F

**Fable 5 · `high` · plan mode SÍ.** Dos esquemas normativos que **discrepan justo en el
rasgo que motiva la clasificación**. Razonamiento normativo fino sobre fuentes que se
contradicen. **No lo mezcles con otro trabajo.**

```
Resuelve el conflicto #8 de la §6 del plan. Sesión de análisis y decisión: no
cablees nada todavía.

El problema:
- SIS-B-01: `clase_sitio` no se invoca desde producción, no entra en
  criterios_usados(), y la memoria nunca declara la adopción de Clase de Sitio F
  que la hoja de ruta §0.5 obliga a escribir "con esas palabras". El mismo
  documento llama a su versión mal etiquetada "el error más grave que ha tenido
  este expediente".
- NOR-AAS-02: la premisa de toda la §0.5 —que el sitio es Clase F por
  licuefacción— NO la sostiene ninguna de las dos tablas.
- NOR-VOC-04: "Clase F" significa dos cosas incompatibles dentro del mismo
  expediente: clase de sitio sísmica (E.030 / Manual de Puentes) y clase de
  resistencia del tubo de concreto (ASTM C76 / M 170M).
- NOR-E030-02: el perfil S5 se declara "referencia muerta" y trae una prohibición
  expresa de construir salvo estudio específico.
- NOR-MEM-03: la memoria justifica F_pga = 1.0 con una convergencia entre clases
  C, D y E que NO incluye la clase F que el propio expediente se atribuye — y la
  fila que le correspondería no da factor, exige un estudio.

Lee las fuentes primarias en normas/: E.030 Art. 14.6 y su Tabla N° 2; el Manual
de Puentes Tabla 2.4.3.11.2.1.2-1 con su Nota 2; AASHTO LRFD Art. 3.10.3.1 y su
comentario. Usa el subagente `verificador-normativo`.

Responde, con cita de página en cada respuesta:
1. ¿E.030 y AASHTO clasifican los suelos licuables en la misma categoría? Si no,
   ¿en qué discrepan exactamente?
2. ¿Puede el expediente trasladar la clasificación de un esquema al otro? ¿Bajo
   qué declaración expresa?
3. Si el sitio es Clase F para AASHTO, ¿existe factor de sitio tabulado, o la
   norma exige análisis de respuesta dinámica?
4. ¿Qué debe decir exactamente la memoria, para ser defendible, sobre la clase de
   sitio adoptada y sobre F_pga = 1.0?
5. ¿Es `clase_sitio` un criterio [A] con valor, o un vacío [A] sin valor que
   bloquea hasta el SPT? Justifica contra la taxonomía de CLAUDE.md.

Entregable: docs/resolucion_clase_sitio.md con la decisión, su fundamento y el
texto exacto que la memoria debe imprimir. El cableado se hace en S14 — hacerlo
antes haría que la memoria declare formalmente algo que la fuente no sostiene.
```

---

### S14 · Vacíos y cableado

**Opus 5 · `high` · plan mode SÍ.** 40 hallazgos con juicio de por medio (decidir qué es
vacío real y qué es vacío inventado). Ultracode repartiría esa decisión y perderías
coherencia.

```
Clusters C01, C04, C06, C08, C11. 40 hallazgos.

Con las citas ya firmes (S12) se puede decidir qué es vacío real y qué es vacío
inventado. Esa es toda la sesión.

Trabajo:
1. Aplicar la decisión de docs/resolucion_clase_sitio.md: cablear (o no)
   clase_sitio según lo resuelto, y hacer que la memoria imprima lo que ese
   documento dice que debe imprimir. No reabras la decisión.
2. Retirar los vacíos declarados sobre fuentes que SÍ traen el dato:
   - NOR-PUE-04: el vacío de factores_carga_aashto se declara sobre las páginas
     que CONTIENEN las tablas (143-144), y el código ya no está vacío.
   - NOR-PUE-05: "vacío absoluto sobre conductos enterrados" — el Manual los trata
     en al menos cinco lugares.
   - NOR-PUE-06: la "evidencia de índice" que sostiene ese vacío es falsa: 2.11 no
     es "Muros de Contención y Estribos", es "Diseño de Barreras de Sonido".
   - NOR-VAC-01: el vacío de altura mínima de relleno no está cerrado; AASHTO
     Sec. 12 la tabula.
3. MAT-D6: ensamblar P_IR = k_h·(W_w + W_s), o declararlo como bloqueo explícito
   con criterio pendiente. Hoy no existe ninguna línea de inercia del muro en el
   repo, y la MISMA sección de la que la hoja toma k_h0 exige combinar
   100% P_AE + 50% P_IR y 50% P_AE + 100% P_IR. Es omisión NO conservadora.
   Decide con fundamento: si va a expediente y no a perfil, se declara como tal.
4. Conflicto #1: ahora sí, con la etiqueta de V4b cerrada en S6, cablear (o no)
   HW/D ≤ 1.5 a verificar() y corregir los dos docstrings que afirman que M5 ya
   lo ejecuta.
5. Cada criterio sin consumidor, con su razón escrita en UN SOLO lugar (los 22
   hallazgos "deliberado sin documentar").

Criterio de salida: clase_sitio resuelto según S13; P_IR ensamblado o declarado
como bloqueo explícito; ningún vacío declarado sobre una fuente que sí trae el
dato; cada criterio sin consumidor con su razón escrita.
```

---

### S15 · Modo de resolución de las variables

**Opus 5 · `high` · plan mode SÍ.**

```
Implementa la §4.3 de docs/hoja_de_ruta_correcciones_v12.md: el modo de
resolución de cada variable de entrada. Es el paso que le dice a la GUI qué
ventana abrir y a M11 qué imprimir.

Trabajo:
1. Definir el objeto VariableDeEntrada: clave, concepto, unidad, modo, dominio
   físico, tabla o rango asociado, criterio [A] que recibe la elección, fase que
   la consume.
2. Los seis modos: libre, de_tabla, en_rango, derivada, de_ensayo, de_catalogo.
   `de_catalogo` es nuevo y hace falta: D_MAX y diametros_normalizados NO son
   normativos (NOR-PRO-01/02: las normas tabulan hasta 3600 mm) y mostrarlos en
   una ventana rotulada "norma" crearía una cita falsa nueva.
3. Censar y clasificar las TRES poblaciones que hoy están separadas y que el
   usuario ve como una sola cosa: las 17 columnas del CSV, los 17 datos de sitio
   de corredor, y los 46 criterios adoptados.
4. Añadir a Criterio el campo `resolucion`, que apunta a la tabla o rango del que
   salió el valor. Es el vínculo que permite que la memoria diga: "el valor X vino
   de la fila R de la tabla T" (regla R1 del plan).
5. Cerrar la asimetría de guardias: SIS-D-09 (datos_sitio.py no tiene guardia al
   importar y el homólogo de criterios sí), SIS-D-07, SIS-D-08, SIS-D-12.

Criterio de salida: ninguna variable de entrada sin modo; ningún modo=de_tabla
sin tabla existente en el registro; ningún modo=en_rango sin rango con semántica
declarada.
```

---

### S16 · Tests y guardianes

**Opus 5 · `ultracode`.** 33 hallazgos independientes, muy paralelizables, y ahora es
seguro porque el comportamiento ya está corregido. Ultracode además entrega la verificación
a un agente que no escribió el test que juzga.

```
Clusters C09 (tests y casos patrón) y C10 (bordes y taxonomía de excepciones).
33 hallazgos.

Se hace AHORA y no antes: escribir tests contra el comportamiento anterior habría
congelado los defectos de S2-S14.

Objetivo declarado: que la suite HABRÍA DETECTADO los hallazgos de las tres
auditorías.

Trabajo:
1. Matar los mutantes que sobreviven. Los ocho documentados: SIS-F-04
   (Mononobe-Okabe, siete mutantes de signo), SIS-F-05
   (empuje_activo_sismico_total, 4/4 y el único assert es tautológico), SIS-F-06
   (FS de E3: `FS = R*A` y la guarda invertida pasan la suite), SIS-F-07
   (empuje_horizontal_total y momento_volcante sobreviven a * -> / y + -> -),
   SIS-F-08 (Sec. 7.B, tres mutantes).
2. Endurecer el barrido de literales. Hoy se evade por seis vías: comillas
   simples (SIS-C-01), substring en docstring (SIS-C-03), todo entero dentro de un
   Subscript (SIS-C-04), nombre de archivo a cualquier profundidad (SIS-C-05),
   marca en línea propia (SIS-C-07), conversión desde string (SIS-C-09). Y no
   recorre cli.py (8 literales) ni gui/app.py (151) — SIS-C-06.
3. SIS-F-16: 15 asserts comparan floats con ==, prohibido por CLAUDE.md.
4. C10 entero: exigir finitud en M0 (MAT-D14: Q_m3s='inf' pasa todos los rangos y
   produce un diagnóstico falso), cerrar el borde de TR (MAT-D13:
   ZeroDivisionError fuera de la taxonomía), estrechar las capturas de la GUI
   (SIS-E-01: un ValueError del pipeline se muestra como "no se pudo leer la
   entrada").

Criterio de salida: los mutantes de M7/M9/modelos mueren; el barrido cubre cli.py
y gui/app.py y no se evade por ninguna de las seis vías; ningún assert de float
con ==; ningún dato no finito entra al pipeline como diagnóstico falso.
```

---

### S17 · La ventana emergente

**Opus 5 · `high` · plan mode SÍ.** Un artefacto coherente, no un conjunto de tareas
paralelas. Ultracode lo fragmentaría y tendrías cuatro ventanas con criterios distintos.

```
Construye la ventana emergente de las §4.2 y §4.3 de
docs/hoja_de_ruta_correcciones_v12.md.

Lee antes legacy/Tc.py: CLAUDE.md obliga a reutilizar sus componentes
(MarcoScroll, Tooltip, campo validable, sesión JSON). No reinventes.

Un solo componente con cuatro caras, que LEE DEL REGISTRO NORMATIVO y no sabe
nada de normas por su cuenta.

Ventana de tabla, en este orden visual:
  - Título literal de la tabla, CON unidades (NOR-HID-06: el título de la Tabla
    N° 10 se cita hoy sin "(m/s)").
  - Numeral · nombre completo de la norma · edición · página impresa.
  - La tabla COMPLETA. Las columnas que el cálculo no usa: visibles, atenuadas.
  - La condición de aplicación de cada fila, si la tiene.
  - Las notas al pie, íntegras.
  - Los modificadores que la fuente aplica sobre la tabla, con su cita.
  - La cita textual del párrafo que sostiene la tabla.
  - Al elegir: registra fila, valor, alternativas descartadas, cita y fecha.

Ventana de rango: campo numérico + rango explícito ("debe estar entre X e Y") +
LA SEMÁNTICA (§4.2: dominio físico / rango normativo / rango de sensibilidad no
son lo mismo) + cita + unidad + qué significa salirse. Valida al escribir, no al
calcular.

Reglas duras:
- R1 del plan: la tabla es [N], la elección de fila es [A]. Elegir una fila NO
  convierte la elección en norma. La ventana escribe un criterio [A] cuyo valor
  PROVIENE DE la fila X de la tabla T.
- Se declara por establecer_valor_dinamico(), que ya pasa por
  _verificar_criterio(). No inventes un segundo camino. Escribir el archivo de
  criterios es una acción aparte y explícita.
- R4 del plan: cuando una fila depende de un dato que el proyecto no tiene, la
  ventana PIDE o BLOQUEA. Nunca elige. Casos identificados: carriles por sentido
  (NOR-SUE-01), categoría de acero (NOR-AAS-01, que invierte qué norma gobierna),
  relación a/c (NOR-AAS-05), "solo si el barril fluye lleno" (NOR-HDS-05), "solo
  con refuerzo transversal mínimo" (NOR-AAS-06).
- Todo lo que construyas entra con test. La GUI hoy tiene 584 sentencias y cero
  (SIS-F-01).

Además, en esta sesión:
- SIS-A-17: la GUI no expone --alcance, así que siempre corre "expediente" y
  memoria_perfil.html es INALCANZABLE desde la interfaz. Arreglarlo: es cómo vas
  a usar el nivel de perfil.
- SIS-A-18: la sesión JSON no guarda ni restaura los criterios declarados para la
  corrida.

Criterio de salida: toda variable de_tabla se declara desde su ventana con
procedencia registrada; toda variable en_rango muestra su rango con cita y
semántica; la sesión guarda y restaura; un valor declarado desde la ventana
APARECE EN LA MEMORIA COMO DECLARADO (comprueba de punta a punta el cierre de
SIS-A-01, arreglado en S2).
```

---

### S18 · La memoria sustentada

**Opus 5 · `high` · plan mode SÍ.**

```
Construye la memoria sustentada según la §4.4 de
docs/hoja_de_ruta_correcciones_v12.md.

El cambio de fondo: hoy M11 RECONSTRUYE la memoria leyendo resultados —y declara
en su propio docstring que "no calcula nada nuevo" mientras calcula y/D en dos
sitios (SIS-A-07). Debe pasar a FORMATEAR una traza que el cálculo emitió.

1. Definir PasoDeMemoria con los ocho campos de la §4.4, emitido por cada función
   de cálculo.

2. Escribir los fundamentos ("por qué se hace esto"), uno por fase. Buena parte
   ya está redactada en la hoja de ruta v8 y en los docstrings: muévela al
   registro para que M11 la imprima, en vez de que viva donde solo la lee un
   programador.

3. Citas textuales: la frase que fija cada umbral de aceptación, y toda aquella
   donde el matiz cambia la lectura. Empieza por la que hoy NO llega
   (NOR-MEM-01): el 0.25 m/s de V2 se RECOMIENDA, y la memoria debe decir que el
   proyecto lo aplica como umbral duro por decisión conservadora propia. Hoy
   "recomend" aparece 0 veces en la memoria generada. Mismo tratamiento para V1
   (MAT-O13: el 0.75 tiene el mismo carácter y solo V2 lleva el matiz).

4. Separar tipográficamente lo que dice la fuente de lo que el proyecto
   interpreta. Caso testigo, NOR-HID-04: "el rango recorre la calidad del
   revestimiento" es interpretación del proyectista y hoy se imprime pegada a la
   cita, como si fuera norma.

5. Imprimir la procedencia de cada elección (R1): "se adoptó X, elegido entre
   X1...Xn de la Tabla T (numeral N, pág. P), por la razón R". Es lo que hace
   defendible una memoria, y lo que da sentido al análisis de sensibilidad, que
   hoy existe y solo lo consumen los tests (SIS-B-05).

6. Cerrar SIS-B-06 (--plantilla memoria_perfil.html sobre corrida de expediente
   descarta 13 647 caracteres de pendientes) y SIS-D-05.

Criterio de salida: la memoria de un punto se lee de arriba abajo y se entiende
sin abrir el código; cada número tiene de dónde salió, contra qué se comparó y la
frase de la norma; cada elección tiene qué se eligió, entre qué y por qué. Test:
ningún PasoDeMemoria sin por_qué; ningún umbral sin cita; ninguna cita textual
que no esté en el registro.
```

---

### S19 · Deuda: GUI, código muerto, documentación

**Opus 5 · `ultracode`.** 73 hallazgos, casi todos mecánicos o de redacción. Nada de aquí
cambia un número. Perfil ideal para el reparto.

```
Cluster C14 y el resto de la deuda. 73 hallazgos. Nada de aquí cambia un número
hoy.

Buena parte se cierra ESCRIBIENDO LA DECISIÓN donde un revisor la busque, no
borrando código. Los 22 hallazgos clasificados "deliberado sin documentar" son
intencionales; lo que falta es que estén escritos.

Trabajo:
1. Los 22 "deliberado sin documentar" con su decisión escrita, en un solo lugar.
2. Tests de contrato para la GUI (lo que quede después de S17).
3. legacy/Tc.py: 1320 líneas, 185 literales prohibidos, sin importadores, sin
   tests, sin barrido y sin estatus declarado (SIS-B-10). Decide: se conserva con
   su razón escrita, o se borra. No queda como está.
4. Docstrings que contradicen al código: SIS-A-08 (el docstring de MD abre con
   "M5 todavía no existe en el repositorio" y apoya en esa premisa la
   justificación del Protocol), SIS-A-10 (lista tres pestañas, la app tiene
   cuatro), SIS-A-11, SIS-A-12.
5. El resto de C14 según la hoja `Hallazgos`.

Criterio de salida: los 22 hallazgos "deliberado sin documentar" tienen su
decisión escrita; la GUI tiene tests de contrato; ningún dato no finito entra al
pipeline como diagnóstico falso.
```

---

### S20 · Cierre del nivel de perfil

**Opus 5 · `high` · plan mode SÍ.**

```
Cerrar el nivel de perfil.

1. Correr el pipeline COMPLETO de perfil sobre un CSV real con todos los datos
   externos presentes. Advertencia de la auditoría normativa (limitación
   R48-041): su revisión de la memoria se hizo sobre una corrida que SE DETIENE
   EN LA FASE 2 por falta de luz_m — "lo que solo se imprime en Fase 5 no está
   cubierto por esta auditoría". Cerrar eso exige un CSV completo. Prepáralo.
2. De los 23 criterios sin valor, separar los de perfil de los de expediente.
   Declarar los de perfil con su ventana y su sensibilidad.
3. Implementar el procedimiento de Sec. 1.3 ("TW se calcula, no se mide"), que
   hoy está escrito y no existe en src/ (SIS-B-04): Q_receptor_m3s y cota_TW se
   validan y no alimentan nada.
4. Resolver V2b (sedimentación/colmatación), que desapareció en silencio
   (SIS-A-13, MAT-O15): o se implementa, o se difiere con detención ruidosa y
   texto de diferimiento. Silencio no.
5. Generar los 5 entregables y contrastar la memoria contra un caso resuelto a
   mano.

Criterio de salida: --alcance perfil corre de punta a punta DESDE LA GUI y
produce memoria completa; todo lo diferido aparece listado con fundamento en el
bloque de alcance; ningún [A] de perfil sin valor, sin sensibilidad y sin
procedencia.

Recomendación aparte, fuera de esta sesión: contrastar el dimensionamiento
hidráulico contra HY-8 (FHWA, gratuito) en 3-4 puntos. Es la comprobación más
barata de que el motor no se desvió.
```

---

### S21 · Contrato de expediente

**Opus 5 · `high` · plan mode SÍ.**

```
Dejar el expediente PREPARADO, no escrito.

Principio: una función en blanco es deuda invisible; una función declarada es
deuda con dirección. El mecanismo ya existe (CriterioPendienteError, Bloqueo,
diferido_por_alcance). Falta aplicarlo de forma uniforme.

1. Para cada etapa de expediente hoy vacía o a medias, escribir el contrato: qué
   recibe, qué devuelve, qué criterios consume, qué numerales la sustentan, qué
   falta para cerrarla. SIN escribir el cálculo.
2. Detención ruidosa uniforme: toda etapa no implementada falla con la excepción
   de la taxonomía y aparece en el bloque de pendientes. Cerrar SIS-E-02 (cuatro
   DatoInvalidoError que validan strings que produce el propio código: un fallo de
   programa disfrazado de problema del expediente).
3. Dejar registrado en el contrato lo que las auditorías YA saben que falta, para
   que quien lo implemente no repita el hallazgo:
   - MAT-O1 / conflicto #4: h_eq por orientación del muro (resuelto en S12 como
     dato faltante; el contrato debe consumirlo).
   - MAT-D8 / MAT-D15 / conflicto #2: las filas desglosadas de la Tabla 3.4.1-2.
   - MAT-O2: la errata de imprenta de K_AE en el Manual de Puentes, DOCUMENTADA.
   - MAT-O3: empuje con gamma total bajo el NF — el agua se cuenta dos veces;
     conservador, pero sin declarar.
   - MAT-O9: el MCFT transcrito en ksi-pulgadas con claves rotuladas en SI.
     Trampa de unidades latente.
   - MAT-O16: la capacidad portante exige un q_actuante que no existe en el repo
     NI COMO CRITERIO PENDIENTE DECLARADO. Único eslabón de la cadena de
     estabilidad sin declaración.
   - NOR-PRO-04: la verificación pendiente del TMC se difiere a ASTM A-807, que
     aparece CERO veces en las tres normas de producto. Lo que hace falta está en
     A796 (diseño estructural) y A798 (instalación). Y la relación luz/corrugación
     YA ESTÁ en la Tabla 6 de M 36 y la Tabla 1 de A760, ambas en el repo: PARTE
     DE ESE PENDIENTE SE PUEDE CERRAR HOY.

Entregable: docs/contrato_expediente.md, seguible por un desarrollador que no
haya leído las auditorías.

Criterio de salida: ninguna función en blanco; test que falla si aparece una
etapa sin contrato.
```

---

## 12. Higiene de sesión

| Regla | Por qué |
|---|---|
| **Una sesión = un cluster o una pieza** | La ventana de contexto se ensucia rápido; el commit queda atómico y el `.xlsx` se actualiza limpio |
| **No cambies el esfuerzo a mitad de sesión** | El esfuerzo es parte de la clave de caché: cambiarlo fuerza una relectura completa, a precio lleno, de toda la conversación en el turno siguiente |
| **Plan mode antes de tocar código donde está marcado** | En C01, C04 y C07 el plan es donde detectas que aplicó la corrección «obvia» que un conflicto prohíbe — **antes** de que la escriba |
| **Un commit por cluster, con el ID en el mensaje** | `fix(C01): geometría física del conducto — MAT-D3, MAT-D4, NOR-VAC-01, …` |
| **Actualiza el `.xlsx` al cerrar cada cluster** | Es el tracker real. Si no se marca, el siguiente agente no sabe qué se cerró |
| **Cierra siempre contra `origin/main`** | Regla de `CLAUDE.md`: una rama empujada no es una entrega. El conteo de tests se lee del remoto, distinguiendo `passed` de `collected` |
| **Si Claude se equivoca, revisa el contexto antes de subir el esfuerzo** | Cuando falla en una tarea que no debería necesitar más esfuerzo, el arreglo suele estar arriba: en el prompt, en `CLAUDE.md`, o en cómo está acotada la tarea |
| **Los subagentes se cargan al arrancar** | Si editas `.claude/agents/`, reinicia la sesión |

---

# PARTE III — CIERRE

## 13. Criterios de aceptación del conjunto

Cuando todo esté hecho, estas afirmaciones deben ser verificables con un comando:

| # | Afirmación |
|---|---|
| 1 | Ningún numeral, página o título de tabla vive en un comentario o docstring como fuente |
| 2 | Toda cita del registro se verifica contra el texto del PDF en la página declarada |
| 3 | Toda variable de entrada declara su modo de resolución |
| 4 | Toda variable `de_tabla` se puede declarar desde su ventana, y la ventana muestra la tabla **completa** con numeral, norma, página, notas y condiciones |
| 5 | Toda variable `en_rango` muestra sus bordes, su unidad, su cita y su semántica |
| 6 | Un valor declarado desde la GUI aparece en la memoria como declarado, con su procedencia |
| 7 | Cada paso de la memoria lleva qué, por qué, fórmula con numeral, sustitución con unidades, resultado, umbral con cita y veredicto |
| 8 | Cada umbral de aceptación lleva su cita textual y su carácter (exigencia / recomendación) |
| 9 | Lo que es interpretación del proyectista está marcado como tal, separado de la cita |
| 10 | `--alcance perfil` corre de punta a punta desde la GUI y produce memoria completa |
| 11 | Ninguna etapa de expediente está en blanco: o implementada, o con contrato y detención ruidosa |
| 12 | Todo lo diferido aparece en la memoria con fundamento |
| 13 | El barrido de literales cubre `src/`, `cli.py` y `gui/app.py`, sin las evasiones conocidas |
| 14 | La GUI tiene cobertura de tests |

---

## 14. Lo que conviene NO hacer

- **No construir la ventana antes del registro.** Es la tentación fuerte, porque la ventana
  se ve y el registro no. Una ventana que lea de `constantes_normativas.py` tal como está
  hoy hay que rehacerla entera.
- **No «arreglar» la fórmula de `K_AE` contra el literal del Manual de Puentes.** El Manual
  tiene una errata de imprenta («1 −» donde AASHTO pone «1 +»); el código está bien. Lo que
  falta es **documentar la discrepancia**. Es la trampa más fácil de pisar de todo el
  expediente.
- **No cerrar criterios `[A]` de expediente para «desbloquear» el pipeline.** El campo
  `provisional=True` existe precisamente para que un valor de prueba no pueda pasar
  inadvertido; usarlo y olvidarlo es peor que el bloqueo.
- **No convertir `datos_sitio.py` en constantes** al migrar. Está exento del barrido por la
  razón contraria: sus números **sí** son valores de proyecto, y de los más pesados.
- **No dejar que la ventana escriba directamente en `criterios_adoptados.py`.** El camino
  correcto es la declaración en caliente, que ya pasa por la guardia. Escribir el archivo es
  una acción aparte y explícita (y su rama hoy no tiene ningún test — `SIS-F-02`).
- **No tocar el motor hidráulico validado sin un test que falle antes.** Son 174
  verificaciones correctas contra la fuente primaria.
- **No usar `ultracode` en las sesiones marcadas `high`.** El fan-out evade la matriz de
  conflictos (§9).

---

## 15. Deuda declarada, fuera de alcance

Para que esto no se lea como una promesa de completitud:

- **Las fuentes que se citan y no están en `normas/`:** WSDOT Hydraulics Manual, AASHTO
  M294, ASTM A796/A798/C76/A-807, DG-2018, HEC-14, Ley 29338 y su reglamento, series
  SENAMHI/ANA, Meyerhof (1957) original, el Apéndice A3 de mapas del Manual de Puentes, y el
  estudio geotécnico del expediente. El registro las declara como ausentes; conseguirlas es
  trabajo de gabinete. **Dos son fáciles y desbloquean cosas concretas: A796** cierra la
  mitad TMC de `clases_producto_por_relleno`, y **M294** cierra `D_MAX["hdpe"]`.
- **La lectura de los ábacos raster** (Meyerhof `N_cq`/`N_γq`, la isolínea de PGA sobre
  Piura). Existen y están correctamente numerados; los valores no son legibles por texto.
- **La validación contra HY-8**, recomendada pero externa.
- **El cálculo de expediente propiamente dicho.** Este plan lo *prepara*; no lo escribe.
- **La portabilidad a otra carretera.** El §8 de la auditoría normativa (el corredor de
  ~5 km, `PGA_roca_B`, `clase_sitio`, `D_MAX`, `v_max_*` endurecidos como constante). No
  bloquea nada de lo anterior, y cada sesión previa lo abarata. Se aborda después de S21.
