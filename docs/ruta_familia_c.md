# Hoja de ruta de la Familia C — sección de marco a nivel de perfil

*Proyecto_alcantarillas — Vía de evitamiento, distrito de La Unión (Piura).*

*Objetivo: que un punto de Familia C (cruce de canal o dren, Sec. 2.3) recorra el mismo
pipeline que hoy recorren A y B y salga con **sección adoptada, control gobernante,
hidráulica, cotas y protección de salida** a `--alcance perfil`, **con cada paso del
procedimiento y cada valor de cálculo sostenidos por un numeral y visibles en la
memoria**, y con la verificación estructural del conducto y el cabezal diferidos al
expediente.*

**Alcance deliberadamente recortado.** Este documento NO cubre el diseño del pórtico por
AASHTO LRFD Sec. 5 / 12.11, ni el predimensionamiento del cabezal, ni la verificación
VC1 de no alteración de la rasante del canal. Los tres están en §13 como deuda
declarada, con el motivo.

---

## 0. Cómo usar este documento

| Parte | Qué es | Quién la lee |
|---|---|---|
| **I — Diagnóstico y diseño** (§1–§7) | Dónde se detiene hoy la Familia C, cómo debe quedar, y las reglas que impiden que arreglar una cosa rompa otra | Tú, y Claude Code cuando un prompt lo manda aquí |
| **II — Ejecución** (§8–§10) | Diez sesiones de Claude Code con su prompt, modelo y esfuerzo | Tú, al abrir cada sesión |
| **III — Cierre** (§11–§15) | Criterios de aceptación, antipatrones, deuda declarada, defectos abiertos | El revisor |

**Convivencia con lo que ya existe.** `CLAUDE.md` sigue siendo la constitución y manda
sobre este archivo. `docs/hoja_de_ruta_alcantarillas_v8.md` sigue siendo la fuente
normativa única; lo que este documento hace es declarar, punto por punto, **dónde la v8
no dice nada sobre el marco** y por qué eso obliga a abrir un criterio vacío en vez de
inventar un número. **La v8 no se edita desde aquí**: los defectos se acumulan en §15.

**Advertencia de nombre de archivo.** `M11_reporte.ruta_hoja_de_ruta()` busca en `docs/`
el patrón `hoja_de_ruta_alcantarillas_v*.md` y **falla si encuentra más de uno**. Este
archivo se llama `ruta_familia_c.md` y no colisiona. No lo renombres a
`hoja_de_ruta_alcantarillas_*`.

---

# PARTE I — DIAGNÓSTICO Y DISEÑO

## 1. Estado de partida, medido

### 1.1 Dónde se detiene hoy un punto de Familia C

Medido sobre `origin/main` con el fixture del repositorio:

```
python3 cli.py tests/ejemplo_puntos.csv --luz 2.75
→ C-01: [DatoFaltanteError] tirante en el receptor (TW, Sec. 1.3)
         Falta el dato 'S_cauce' en el punto C-01
```

Eso es un **síntoma**, no el bloqueo: `S_cauce` va vacía en Familia C a propósito
(`M0_carga._VACIAS_FAMILIA_C`) y `cli._resolver_tw` solo la exige cuando tiene que
calcular la cota de fondo de la salida. Declarando `Q_m3s`, `S_conducto` y `TW_m` por
`--datos-externos`, el punto llega al bloqueo real:

```
→ C-01: [DisenoNoFactibleError] material y diametro (bucle de MD)
         M2 (Sec. 3.4) no ofrece material candidato para la Familia C:
         Sec. 2.3 le asigna seccion de marco o multicelda, y el catalogo
         de Sec. 3.2 es de conductos circulares. El punto no es
         no-factible, es de otra forma de estructura.
```

### 1.2 Lo que ya funciona para C y no hay que tocar

- `M0_carga._familia` la valida contra el enum y `_VACIAS_FAMILIA_C` acepta la fila con
  `Q_m3s`, `area_ha` y `S_cauce` vacías.
- `M1_clasificacion.PERFILES[Familia.C]` está completo, incluida la nota «Sección: marco
  o multicelda». `periodo_retorno_de` devuelve `procede=False` con fundamento escrito.
  La Fase 2 de C-01 sale **verde** hoy.
- El TW de Sec. 1.3 entero (`M3.tw_seccion_1_3`, las cuatro vías, `SeccionReceptor`): es
  del receptor, no del barril.
- `M6_proteccion`: `laushey_d50(V)` es función solo de la velocidad.
- `M9_cabezal` entero: cadena sísmica, Mononobe-Okabe, estabilidad.
- `M11_reporte`, el registro de criterios, `PasoDeMemoria`, `Verificacion`, el gobierno
  de vacíos.
- `--alcance perfil` ya difiere completas la Fase 8 y la Fase 9, más V5 y V8, y lo deja
  escrito en el informe (`cli._cabezal_diferido`, `cli._fase8_diferida`).

### 1.3 El andamio que nadie usó todavía

- **`M3.area_trapecial` / `perimetro_trapecial` / `caudal_manning_trapecial` /
  `tirante_normal_trapecial` + `modelos.SeccionReceptor`.** El patrón «una sección que no
  es un círculo» ya existe, aunque solo del lado del receptor.
- **`criterios_adoptados['factores_carga_aashto']`** trae escrito: *«No es "Pórticos
  rígidos" (1.35/0.90): un pórtico es un marco con patas, y el catálogo de Sec. 3.2 es
  circular — la Familia C, de marco o multicelda, sale sin candidatos»*.
- **`constantes_normativas.alcantarilla_cajon_prefab_*`** (2.5 in / 2.0 in / 1.0 in) ya
  transcritos de la Tabla 5.10.1-1 de AASHTO y la 2.9.1.5.5.3-1 del Manual de Puentes.
- **Los subagentes `.claude/agents/verificador-normativo.md` y `auditor-adversarial.md`**,
  ambos con `model: opus` y `effort: high` ya fijados en su frontmatter. Ninguna sesión
  de este plan puede cerrarse sin haberlos usado.

---

## 2. El diagnóstico en una frase

**No existe el concepto de «sección» como abstracción: el diámetro está cableado en la
geometría del motor hidráulico**, y todo lo demás — el catálogo de M2, el bucle de MD,
las tablas transcritas, los criterios — deriva de esa única decisión.

| Símbolo | Qué supone |
|---|---|
| `M4_control.area_llena(D)` | `A = π·D²/4` |
| `M4_control.radio_hidraulico_lleno(D)` | `R = D/4` |
| `M4_control.caudal_adimensional(Q, D)` | deriva `A` de `D` internamente |
| `M4_control.tirante_critico(Q, D)` | brentq sobre θ con `_residuo_critico(D, θ, Q)` |
| `modelos.Geometria` | `(D, theta, A, P, R, y)`, parametrizada por ángulo mojado |

Y la consecuencia declarada: `M2_material.materiales_candidatos()` devuelve `()` para
`Familia.C`, con la razón escrita en el docstring del módulo bajo el epígrafe *«Familia C
queda sin candidatos — por DOS razones, y la normativa faltaba»*.

---

## 3. Principio rector

**Generalizar, no bifurcar, y no aplicar nada sin numeral.**

Tres corolarios operativos, y ninguno es opcional:

1. **El refactor de sección se hace sin cambiar ningún número.** Primero `SeccionCircular`
   con `casos_patron` en verde y todos los valores idénticos; después la rama rectangular.
   Un segundo motor de cálculo sin tests es exactamente lo que `SIS-A-07` cerró.
2. **Todo procedimiento aplicado al marco declara qué numeral lo sostiene.** Si el numeral
   habla de «alcantarilla» sin distinguir forma, se cita la frase. Si habla solo de
   tubería, es un vacío y va como `[N→]` con analogía declarada o como `[A]`. Si no hay
   numeral, el paso no se aplica «porque es lo que se hace»: se detiene.
3. **Todo vacío se declara, ninguno se rellena.** `Criterio(valor=None, ...)` con `nivel`,
   `sensibilidad` y `resolucion`, y el cálculo se detiene con `CriterioPendienteError`.
   El tesista los declara después. Eso no es una limitación del plan: es el contrato.

---

## 4. Arquitectura objetivo

### 4.1 El tipo `Seccion`

En `modelos.py`, un protocolo con dos implementaciones. **Modela UNA celda**; el número
de celdas vive fuera y se reparte el caudal (regla vinculante #3 de §6).

```
Seccion (Protocol)
    altura           float   m — el "D" de HDS-5: altura interior del barril
    area(y)          float   m²
    perimetro(y)     float   m
    ancho_superficial(y)     m   — el T que necesita el tirante crítico
    area_llena       float   m²
    radio_hidraulico_lleno   m
    etiqueta()       str     — "Ø 0.90 m" | "marco 2.00 × 1.50 m"

SeccionCircular(D)
    altura = D
    area(y), perimetro(y), ancho_superficial(y) por θ, como hoy
    area_llena = π·D²/4        radio_hidraulico_lleno = D/4

SeccionRectangular(B, H)
    altura = H
    area(y) = B·y              perimetro(y) = B + 2y
    ancho_superficial(y) = B   (constante — el tirante crítico se cierra)
    area_llena = B·H           radio_hidraulico_lleno = B·H / (2(B+H))
```

`Geometria` pasa a llevar la `Seccion` en vez de `D` + `theta`. La propiedad `y_sobre_D`
conserva el nombre y cambia de definición a `y / seccion.altura`: **no se renombra**,
porque la consumen V1, `M11._tabla_diseno` y las dos plantillas HTML.

### 4.2 El tirante crítico rectangular es cerrado

`y_c = (q²/g)^(1/3)` con `q = Q/B`. Exacto, sin brentq. Elimina la clase de fallos que
`LimiteNumericoError` cubre en `M4.tirante_critico` (`SIS-G-02`). La guardia de finitud
va a la **salida**, con la forma que fijó `MAT-D13`: umbral medido, condición escrita en
positivo y negada, mensaje que nombra al par culpable.

### 4.3 HDS-5 gana una forma de ecuación

`modelos.ConstantesHDS5` tiene hoy `K, M, c, Y, Ks` y **ningún campo de forma**. Gana
`forma: int` (1 o 2).

- La **Forma 1** es la de hoy: `HWi/D = Hc/D + K·(q*)^M + Ks·S`.
- La **Forma 2** es `HWi/D = K·(q*)^M`, **sin el término `Ks·S`** (num. A.2.1, ec. A.2,
  pág. impresa A.1). Regla vinculante #2.
- `_hw_sobre_D_sumergido` (ec. A.3) no cambia: es común a las dos formas y sí lleva `Ks·S`.
- `caudal_adimensional` pasa a recibir la `Seccion`: `q* = Ku·Q / (A_llena · √altura)`.

### 4.4 El catálogo de M2 gana forma

Las claves de `constantes_normativas.HDS5_INLET` ya codifican la forma
(`"circular_concreto_square_edge_headwall"`); se extienden con `"cajon_concreto_*"` por
carta y escala de la Tabla A.1. `Material.D_max` conserva el nombre (lo consumen V9 y el
reporte) y su semántica pasa a ser *dimensión máxima de catálogo*.

### 4.5 Contrato de memoria — qué tiene que salir en el reporte

**Esta sección es tan vinculante como §6.** El entregable de la tesis no es que el número
salga: es que el revisor pueda reconstruir de dónde salió, igual que ya ocurre con la
Familia A. Todo lo que este plan añada tiene que aparecer por **los mismos seis vehículos
que el proyecto ya usa**, sin inventar uno nuevo:

| Qué se declara | Vehículo | Qué exige del código nuevo |
|---|---|---|
| **El procedimiento**, paso a paso | `PasoDeMemoria` emitido por la función de cálculo, impreso por `M11.bloque_paso` | qué, **por qué** (de un `Fundamento` de `normativa/fundamentos.py`, con `verbo` sostenido por el `caracter` de alguna de sus citas), fórmula con `cita_id`, sustitución con **procedencia de cada valor**, umbral con su **carácter en la fuente**, veredicto con margen |
| **Cada valor elegido** | `M11.bloque_criterios` (marcador `bloque_criterios`) | cada criterio nuevo con etiqueta, concepto, fuente, sensibilidad y `resolucion`; el valor **efectivo**, con marca si se declaró en caliente |
| **Lo adoptado donde la norma calla** | `M11.bloque_acotaciones` (marcador `bloque_acotaciones`) | el criterio nuevo debe llevar `vacio_verificado`, o **no aparece en este bloque**: `acotaciones_declaradas()` lo lee del catálogo, no de la plantilla |
| **El carácter de cada umbral** | `M11.bloque_umbrales` (marcador `bloque_umbrales`) | si el numeral *recomienda* y el proyecto lo aplica como umbral duro, tiene que decirlo — es lo que ya hacen V1 y V2 |
| **Lo que falta y a quién** | `M11.bloque_pendientes` + `criterios_bloqueantes` | cada vacío nuevo con concepto, fuente, qué lo resuelve, qué bloquea y en qué puntos |
| **Lo que la fuente dice / lee / hace** | tres clases CSS separadas: `fuente`, `interpretacion`, y lo que el proyecto hace | pegar las tres es `NOR-HID-04` |

Dos reglas que se rompen sin querer:

- **Ningún texto literal se transcribe dos veces.** Toda frase entrecomillada sale de
  `Registro.textos_literales()`, verificada contra su página. Copiarla a un docstring
  crea una segunda transcripción que diverge sin que nada avise.
- **M11 no hace aritmética sobre magnitudes.** Un test barre su AST. Si un valor nuevo
  hay que calcularlo, lo calcula el módulo y lo emite en su paso.

---

## 5. Los cinco frentes y qué se rompe si tocas cada uno

| Frente | Símbolos que toca | Qué se rompe |
|---|---|---|
| **F0 · Procedimiento normativo** | `docs/ruta_familia_c.md` §15, `normativa/fundamentos.py`, `normativa/citas.py` | nada de código; es la sesión CN |
| **F1 · Abstracción de sección** | `modelos.Geometria`, `M3.area/perimetro/tirante/geometria/_caudal_manning/tirante_normal/resolver_manning`, `M4.area_llena/radio_hidraulico_lleno/caudal_adimensional/_residuo_critico/tirante_critico/_geometria_de_referencia/control_entrada/control_salida/perdida_carga` | el motor completo bajo `casos_patron`. Es el frente de riesgo |
| **F2 · Registro normativo del cajón** | `normativa/tablas.py` (los `Acotada` de Tabla A.1 y C.2), `constantes_normativas.HDS5_INLET`, `modelos.ConstantesHDS5` | `test_normativa_pdf.py` (32 tests), `test_manifiesto_citas.py`, `docs/manifiesto_citas.md` |
| **F3 · Catálogo y criterios** | `M2.materiales_candidatos/catalogo`, `criterios_adoptados` (4 criterios nuevos), `M5.v1/v6/v9`, `MD._motivo_sin_candidatos` | `test_M2_material.py:283`, `test_MD.py:719/743/747`, `test_M1_clasificacion.py:394`, `test_criterios_adoptados.py`, `test_cierre_perfil.py` |
| **F4 · Camino a perfil** | `M7.cobertura_minima_aashto/altura_recubrimiento/compatibilidad_geometrica`, `M8.empuje_flotacion_kn_m/peso_relleno_kn_m/factores_carga_flotacion`, `M5.v7_flotacion` | `test_M7_geometria.py`, `test_M5_verificaciones.py`. **V7 SÍ corre a perfil** |
| **F5 · Entradas y reporte** | `variables_entrada`, `dominios`, `cli.CLAVES_EXTERNAS`, `M11.fila_resumen/_tabla_diseno/_fila_resumen_csv/bloque_criterios/bloque_acotaciones/bloque_umbrales`, las dos plantillas, `gui/app.py` | `test_variables_entrada.py`, `test_cli.py`, `test_M11_reporte.py`, `test_gui_contrato.py`, `test_memoria_sustentada.py` |

---

## 6. Reglas vinculantes — donde la corrección «obvia» es la equivocada

Estas diez sustituyen al criterio de quien ejecute la sesión. Si tu solución contradice
una, párate y explica por qué antes de seguir.

**#1 — El cajón NO hereda el piso de 0.90 m.** El num. 4.1.1.3.4 a) lo escribe así: *«…se
adoptará una sección mínima circular de 0.90 m (36") de diámetro o su equivalente de otra
sección, **salvo en cruces de canales de riego donde se adoptarán secciones de acuerdo a
cada diseño particular**»*. La Familia C **es** el conjunto de cruces de canal. El literal
y su ámbito ya viven en `constantes_normativas.DIAMETRO_MIN_TEXTO` y `DIAMETRO_MIN_AMBITO`.

**#2 — La Forma 2 de HDS-5 no lleva el término `Ks·S`.** Verificado contra
`normas/hif12026.pdf`, num. A.2.1, ecuaciones (A.1) y (A.2), pág. impresa A.1–A.2. De las
cinco cartas de cajón de la Tabla A.1, **solo la Carta 8 usa Forma 1**; las Cartas 9, 10,
11 y 12 usan Forma 2.

**#3 — Multicelda se resuelve por barril, no por conjunto.** Los coeficientes de HDS-5, el
radio hidráulico y el control de entrada son **por barril**. Con N celdas se diseña una
celda con `Q/N` y se declara N.

**#4 — `D` en `q* = Ku·Q/(A·√D)` es la ALTURA interior, y `A` es el área LLENA del
barril.** No hay «diámetro equivalente». HDS-5: *«D — Interior height of culvert barrel»*,
*«A — Full cross sectional area of culvert barrel»*.

**#5 — No se cruzan coeficientes entre formas.** HDS-5 num. A.3: *«coefficients for
rectangular (box) shapes should not be used for nonrectangular (circular, arch, pipe-arch,
etc.) shapes and vice-versa»*.

**#6 — La Tabla Nº 09 NO tiene fila de cajón.** El subgrupo «a. Concreto» del grupo A trae
solo filas de **tubo**. El n de Manning de un marco es un **vacío del Manual** y se cubre
con un criterio `[N→]` con la analogía declarada, con la forma de `n_manning_hdpe`.

**#7 — La Tabla Nº 10 SÍ sirve tal cual, y no se le crea criterio.** Clasifica por **tipo
de revestimiento** («Concreto 3.0 – 6.0 m/s»), no por forma. V3 no se toca y **no** se
abre un `v_max_cajon`: sería inventar un vacío que no existe.

**#8 — La fila de γ_EV del cajón es «Pórticos rígidos» (1.35/0.90).** El comentario de
`criterios_adoptados['factores_carga_aashto']` ya lo anticipa por escrito.

**#9 — En `cobertura_minima_aashto` vuelve el segundo término `B'c/8`.** El criterio omite
hoy el `whichever is greater` de la Tabla 12.6.6.3-1 porque en un conducto circular
`B'c = Bc` por geometría. Para un cajón deja de valer. Está anotado en su campo
`verificacion_pendiente`.

**#10 — `MD._motivo_sin_candidatos` no se borra: se estrecha.** Y
`M5.v6_material_solido_arrastre` deja de ser trivial en cuanto exista multibarril: su
docstring ya lo avisa. Mientras N esté fijado en 1 por criterio declarado, V6 sigue
valiendo y **hay que decirlo en el criterio**, no darlo por hecho.

---

## 7. Las cinco trampas que este trabajo va a destapar

1. **El refactor bajo 1538 tests.** `collected = passed + skipped` y hay cuatro
   configuraciones de entorno (PyMuPDF × ventana Tk). El número que se reporta es un
   **par**, leído de `origin/main`, con el entorno declarado.
2. **`tests/test_sin_literales.py` rechaza cualquier literal nuevo** fuera de
   `constantes_normativas.py`, `criterios_adoptados.py` y `datos_sitio.py`. Los literales
   de fórmula transcrita van marcados `# literal-ok: <razón>`. El barrido corre sobre el
   **AST**: un símbolo en un comentario no lo satisface.
3. **La memoria la emite el cálculo.** Ver §4.5. Un paso sin `por_qué` no se construye, y
   un umbral sin `cita_id` tampoco.
4. **Ningún texto literal se transcribe dos veces.** Sale de `Registro.textos_literales()`.
5. **`test_cierre_perfil.py` corre el pipeline y contrasta lo invocado contra
   `Criterio.nivel`.** Un criterio que una corrida `--alcance perfil` invoque y esté
   marcado `NIVEL_EXPEDIENTE` rompe la suite. Todo `[A]` de perfil necesita `sensibilidad`
   y `resolucion`, tenga valor o no.

---

# PARTE II — EJECUCIÓN CON CLAUDE CODE

## 8. Preparación, antes de la primera sesión

1. `pip install pymupdf --break-system-packages` en el entorno de la suite. Sin él, los 32
   tests de `test_normativa_pdf.py` se saltan y las transcripciones de C2 pasarían sin
   verificar.
2. Guardar la salida de `python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance
   perfil` y el par `passed / skipped` leído de `origin/main`. Es la línea base contra la
   que C1 se mide con un diff.
3. **CN va primero.** Es la sesión que contesta qué numeral sostiene cada paso del
   procedimiento cuando la sección es un marco. Sin ella, C5 escribe criterios cuya
   justificación habría que rehacer.

**Convención de commit:** `familiaC(Cn): resumen — símbolos tocados`. Una tarea no está
terminada hasta que su trabajo está en `origin/main`; el conteo de tests se lee de ahí.

---

## 9. Tabla maestra de sesiones

| Sesión | Trabajo | Frente | Modelo | Esfuerzo | Plan mode |
|---|---|---|---|---|---|
| **CN** | Procedimiento normativo del marco | F0 | **Fable 5.1** | high | sí |
| **C0** | Censo de acoplamiento y línea base | — | Sonnet 5 | high | no |
| **C1** | Refactor de sección, sin cambiar ningún número | F1 | Opus 5 | **ultracode** | sí |
| **C2** | Registro normativo del cajón (Tabla A.1 y C.2) | F2 | Opus 5 | **xhigh** | sí |
| **C3** | HDS-5 Forma 2 en M4 | F1+F2 | Opus 5 | high | sí |
| **C4** | `SeccionRectangular`: hidráulica del marco | F1 | Opus 5 | xhigh | sí |
| **C5** | Catálogo, criterios y verificaciones del cajón | F3 | Opus 5 | xhigh | sí |
| **C6** | Entradas: CSV, CLI, variables, dominios | F5 | Sonnet 5 | high | no |
| **C7** | Camino a perfil: M7, M8 y V7 | F4 | Opus 5 | high | sí |
| **C8** | Reporte, GUI, corrida completa y cierre | F5 | Opus 5 | ultracode | no |

**Por qué este reparto.** El modelo es aproximadamente *cuán capaz* y el esfuerzo
aproximadamente *cuán exhaustivo*: el esfuerzo no controla solo el tiempo de pensamiento,
sino cuánto trabajo hace Claude en total — cuántos archivos lee, cuántas herramientas usa
y cuánto verifica antes de volver a ti. En Opus 5 y Fable 5.1 el default es `high` y se
ajusta desde ahí. `ultracode` no es un nivel del modelo sino un ajuste de Claude Code:
envía `xhigh` y además orquesta flujos dinámicos, que es lo que quieres en C1 y C8, las
dos sesiones de amplitud multiarchivo.

Fable se reserva para **CN** y solo para CN: es la única sesión cuyo valor está en
reconocer qué numeral sostiene qué, no en ser exhaustiva. C2, que parece el candidato
obvio por ser normativa, es en realidad volumen de transcripción con verificación contra
PDF: eso es exhaustividad, y se resuelve con Opus a `xhigh` más el subagente
`verificador-normativo`.

**Cómo corregir sobre la marcha.** Si Claude tenía el contexto, se esforzó y aun así se
equivocó, sube de modelo. Si falló por saltarse un archivo, no correr los tests o no
verificar su trabajo, sube el esfuerzo.

**Los subagentes ignoran el nivel de la sesión.** `effort` en el frontmatter de un
subagente sobrescribe el de la sesión, así que `verificador-normativo` y
`auditor-adversarial` corren a `opus` / `high` aunque tú bajes la sesión a Sonnet. Por eso
C0 y C6 pueden ir con Sonnet sin perder rigor normativo.

---

## 9-bis. Cláusula normativa común

**Pégala al final de los prompts de C1 a C8.** CN ya la contiene desarrollada.

```
CLÁUSULA NORMATIVA (aplica a toda esta sesión):

1. Antes de aceptar cualquier valor [N] o [N->] que toques o crees, invocá el
   subagente `verificador-normativo` sobre su cita. No es opcional: su
   frontmatter existe para esto.

2. Todo procedimiento que apliques al marco tiene que decir QUÉ NUMERAL lo
   sostiene, y la respuesta sale de §15 de docs/ruta_familia_c.md, que cerró la
   sesión CN. Si lo que necesitás no está ahí, PARÁ y decilo: no lo apliques
   "porque es lo que se hace para el circular".

3. CONTRATO DE MEMORIA (§4.5 de docs/ruta_familia_c.md). Nada de lo que agregues
   puede quedar invisible en el reporte:
   - toda función de cálculo nueva emite su PasoDeMemoria con por_qué de un
     Fundamento, fórmula con cita_id, sustitución con procedencia de cada valor,
     umbral con su carácter en la fuente y veredicto con margen
   - todo criterio nuevo aparece en bloque_criterios con etiqueta, concepto,
     fuente, sensibilidad y resolución
   - todo criterio que cubra un vacío normativo verificado lleva
     `vacio_verificado`, o NO SALDRÁ en bloque_acotaciones
   - todo umbral que el numeral RECOMIENDA y el proyecto endurece lo declara,
     para que salga en bloque_umbrales
   - toda frase entrecomillada sale de Registro.textos_literales(), nunca
     copiada a un docstring
   - lo que la fuente DICE, lo que el proyecto LEE y lo que el proyecto HACE van
     separados (NOR-HID-04)

4. Al cerrar, reportá el DEFECTO CONTRA docs/hoja_de_ruta_alcantarillas_v8.md:
   qué tendría que decir la v8 sobre el marco y no dice. NO la edites — es la
   fuente normativa única y M11 la localiza por patrón de nombre. Acumulá los
   defectos en §15 de docs/ruta_familia_c.md, con el símbolo del código donde la
   discrepancia se ve.

5. Antes de cerrar, invocá el subagente `auditor-adversarial` sobre tu propio
   trabajo y reportá qué encontró, lo cierre o no.
```

---

## 10. Los prompts

### CN · Procedimiento normativo del marco

**Fable 5.1 · `high` · plan mode SÍ.** Ninguna otra sesión decide tanto con tan poco
código. Va primero.

```
Lee CLAUDE.md, docs/ruta_familia_c.md (§3, §4.5 y §6) y los num. 4.1.1.3.1 a
4.1.1.3.7 de normas/Hidrología, Hidráulica y Drenaje (Versión Libro).pdf.

No escribas código de cálculo. Esta sesión decide si el procedimiento de diseño
que el proyecto aplica hoy a un conducto circular está sostenido por la norma
cuando la sección es un marco de concreto.

1. Fase por fase (2, 3, 4, 5, 6, 7), y paso por paso dentro de cada una, decí:
   - qué numeral lo sostiene
   - si ese numeral habla de "alcantarilla" en general, de "tubería", o de
     "marco / sección rectangular"
   - si aplica al cajón DIRECTAMENTE, POR ANALOGÍA declarable, o NO APLICA
   - qué etiqueta le corresponde en consecuencia: [N], [N->] o [A]
   Usá `verificador-normativo` para cada cita. Anotá página impresa y página PDF,
   que no son la misma.

   Presta atención especial a estos cuatro, que son los que deciden:
   - 4.1.1.3.4 a) elección de tipo y sección: nombra el marco de concreto como
     tipo común, dice que las secciones usuales son "circulares, rectangulares y
     cuadradas", recomienda el marco con suelos de fundación de mala calidad, y
     EXCEPTÚA los cruces de canal de riego del piso de 0.90 m
   - 4.1.1.3.6 Manning y velocidades: comprobá si la Tabla Nº 09 tiene fila de
     cajón (yo sostengo que NO: el subgrupo "a. Concreto" trae solo filas de
     "tubo") y si la Tabla Nº 10 clasifica por revestimiento y no por forma
   - 4.1.1.3.7 b) borde libre: comprobá si dice "altura, diámetro o flecha"
   - 4.1.1.3.7 c) protección de salida (d50 de Laushey): si es función solo de V

2. Lámina Nº 03 de los Anexos. Una de sus figuras se titula "ALCANTARILLA TIPO
   MARCO DE CONCRETO EN CRUCE DE CANAL DE RIEGO". Verificá que existe y en qué
   página, y evaluá si debe entrar al registro normativo como respaldo del tipo
   de estructura de la Familia C. Hoy no está citada en ninguna parte del repo.

3. Sec. 3.1 de la hoja de ruta dice "suelo de fundación deficiente -> orientar a
   marco de concreto", y el num. 4.1.1.3.4 a) lo respalda. La columna
   `sucs_fundacion` del CSV se carga, se valida y NO LA LEE NINGÚN MÓDULO.
   Evaluá si ese numeral es su primer consumidor y qué haría falta para cablearlo.
   No lo cablees en esta sesión.

4. LA PREGUNTA QUE MÁS IMPORTA. Sec. 2.3 dice que la Familia C "no puede alterar
   la rasante hidráulica ni el borde libre del canal". Difiriendo VC1 (§13), el
   marco se dimensionará por V1/V4/V4b, que es el criterio de una alcantarilla de
   paso, NO el de un cruce de canal. Eso es admisible a nivel de perfil solo si se
   DECLARA. Proponé el texto exacto de esa declaración y por qué vehículo del §4.5
   sale en la memoria — mi lectura es que es una `Interpretacion` más una entrada
   de acotaciones, pero decidilo vos y justificalo.

5. Redactá los `Fundamento` de normativa/fundamentos.py que las sesiones C3, C4 y
   C5 van a necesitar para el `por_qué` de sus pasos. Recordá que el `verbo` de un
   Fundamento tiene que estar sostenido por el `caracter` de alguna de sus citas:
   no se escribe "la norma obliga a" encima de un párrafo que dice "se recomienda".

Entregable: §15 de docs/ruta_familia_c.md, con (a) la tabla numeral-por-paso, (b)
los Fundamento redactados, (c) la declaración del punto 4, y (d) la lista de
defectos abiertos contra docs/hoja_de_ruta_alcantarillas_v8.md.

Criterio de salida: ningún paso del procedimiento queda como "se aplica igual" sin
numeral o sin analogía declarada. Invocá `auditor-adversarial` sobre tu propio
resultado antes de cerrar.
```

---

### C0 · Censo de acoplamiento y línea base

**Sonnet 5 · `high` · sin plan mode.** Amplitud mecánica; el esfuerzo alto es lo que hace
que no se salte archivos.

```
Lee CLAUDE.md, docs/ruta_familia_c.md (§1, §2, §6 y §15) y la Sec. 2.3 y la Fase 8
de docs/hoja_de_ruta_alcantarillas_v8.md.

No escribas código de cálculo en esta sesión.

1. Reproduce y documenta el estado de partida de la Familia C:
   - corre `python3 cli.py tests/ejemplo_puntos.csv --luz 2.75` y anota dónde se
     detiene C-01 y con qué excepción
   - corre lo mismo declarando Q_m3s, S_conducto y TW_m para C-01 por
     --datos-externos, y anota el bloqueo real
   Cita el símbolo que produce cada uno.

2. GUARDA LA LÍNEA BASE que C1 va a usar como diff: la salida completa de
   `python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance perfil`, en un
   archivo versionado bajo tests/ o docs/, y el par passed/skipped leído de
   origin/main con el entorno declarado (PyMuPDF sí/no, ventana Tk sí/no).

3. Censo de acoplamiento al diámetro. Barre src/ y lista TODA función y todo
   dataclass que reciba, devuelva o derive un diámetro de conducto. Ancla por
   NOMBRE DE SÍMBOLO, nunca por línea. Usá el subagente `explorador`. Separa en:
   (a) geometría del barril, (b) consumidores de la geometría, (c) presentación.
   Añadí una cuarta columna: si el símbolo emite PasoDeMemoria, cuál.

4. Deja escritas en docs/ruta_familia_c.md, en §14, las dos decisiones de alcance
   con su argumento, para que las sesiones siguientes las lean en vez de volver a
   decidirlas:
   - marco VACIADO IN SITU o PREFABRICADO. normas/ tiene AASHTO LRFD 9a ed. y NO
     tiene ninguna norma de producto de cajón prefabricado (M 259, M 273, ASTM
     C1433/C1577), y la Fase 8 de la hoja de ruta ya dice "diseño completo por
     AASHTO LRFD Sección 5" para el marco.
   - número de celdas: si se fija N = 1 por criterio declarado, o si se abre
     multicelda. Lee la regla vinculante #10 de §6 antes de proponer.
   Si eliges prefabricado o multicelda, di qué trabajo adicional añade a cada
   sesión posterior.

Criterio de salida: ninguna entrada del censo anclada solo a un número de línea, y
la línea base del punto 2 guardada y reproducible.
```

---

### C1 · Refactor de sección, sin cambiar ningún número

**Opus 5 · `ultracode` · plan mode SÍ.** El frente de riesgo. El criterio de éxito es que
**ningún valor cambie**.

```
Lee CLAUDE.md y docs/ruta_familia_c.md (§2, §4.1, §4.5, §5-F1 y §7).

Objetivo: introducir la abstracción `Seccion` y hacer que M3 y M4 dejen de saber
qué forma tiene el barril. En esta sesión NO se añade la sección rectangular.
El comportamiento del cálculo tiene que quedar IDÉNTICO, valor por valor.

1. En modelos.py, define el protocolo `Seccion` con la forma de §4.1, y
   `SeccionCircular(D)` como su única implementación. Los literales de fórmula
   transcrita (el 8 de A=(D²/8)(θ−senθ), el 4 de R=D/4, el π del área llena) van
   marcados `# literal-ok: <razón>`.

2. `modelos.Geometria` pasa a llevar la `Seccion` en vez de D + theta sueltos.
   `y_sobre_D` CONSERVA EL NOMBRE y pasa a definirse como y / seccion.altura: lo
   consumen M5.v1_borde_libre, M11._tabla_diseno y las dos plantillas de
   src/plantillas/. Renombrarlo rompe la memoria.

3. Reescribe para que consuman `Seccion` en vez de D:
   M3: area, perimetro, tirante, geometria, _caudal_manning, tirante_normal,
       resolver_manning
   M4: area_llena, radio_hidraulico_lleno, caudal_adimensional,
       _residuo_critico, tirante_critico, _geometria_de_referencia,
       control_entrada, control_salida, perdida_carga
   NO toques M3.area_trapecial / perimetro_trapecial / caudal_manning_trapecial /
   tirante_normal_trapecial ni SeccionReceptor: son del receptor, no del barril.

4. Los PasoDeMemoria que estas funciones emiten tienen que seguir imprimiendo lo
   MISMO: misma fórmula, misma cita, misma sustitución con la misma procedencia,
   mismo umbral con el mismo carácter. Si una sustitución nombraba "D" y ahora la
   magnitud viene de la sección, el rótulo impreso no cambia.

Criterio de salida, y es duro:
- tests/fixtures/casos_patron.py en verde SIN tocar un solo valor esperado
- el par passed/skipped idéntico al de C0
- diff de la salida de `cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance
  perfil` contra la línea base guardada en C0: VACÍO, salvo lo no numérico
- la memoria HTML generada: diff vacío salvo marcas de tiempo y SHA

Si algún caso patrón exige cambiar un número esperado, PARATE y explicá por qué
antes de tocarlo. Un valor que se mueve en un refactor puro es un defecto
introducido, no un ajuste.

[pegar aquí la CLÁUSULA NORMATIVA COMÚN de §9-bis]
```

---

### C2 · Registro normativo del cajón

**Opus 5 · `xhigh` · plan mode SÍ.** Volumen de transcripción con verificación contra PDF.
Ningún cálculo.

```
Lee CLAUDE.md, docs/diseno_registro_normativo.md, docs/manifiesto_citas.md y
docs/ruta_familia_c.md (§4.3, §4.5, §5-F2, §15 y las reglas vinculantes #2, #5 y
#6 de §6).

Requisito de entorno: PyMuPDF instalado. Si tests/test_normativa_pdf.py se está
saltando, PARÁ y decilo: sin él las transcripciones de esta sesión no se verifican
y pasarían en falso.

No toques ningún módulo de cálculo en esta sesión.

1. Tabla A.1 de HDS-5 (normas/hif12026.pdf, pág. impresa A.8, PDF 197). Su objeto
   en src/normativa/tablas.py está declarado `Acotada` con que_queda_fuera = "las
   cartas de secciones cajón, elíptica, pipe-arch, arco y long span". Ensanchá ese
   alcance SOLO al cajón rectangular de concreto y transcribí las filas de las
   Cartas 8, 9, 10, 11 y 12 con sus escalas, sus constantes K, M, c, Y y su
   COLUMNA DE FORMA DE ECUACIÓN. La elíptica, el pipe-arch, el arco y el long span
   SIGUEN FUERA: reescribí `razon` y `que_queda_fuera` para que digan la verdad
   nueva. Un `Acotada` que describe un alcance que ya no es el suyo es un defecto.

2. Tabla C.2 de HDS-5 (coeficientes ke, pág. impresa C.6, PDF 216). Su `Acotada`
   nombra hoy como fuera «Box, Reinforced Concrete» con sus once filas de aletas y
   bordes. Transcribilas y ensanchá el alcance igual que en el punto 1. Ojo con la
   precisión que la propia transcripción ya documenta: el valor 0.5 aparece siete
   veces en esa tabla, en siete filas distintas. Cada fila queda identificada por
   su BORDE, no por su valor.

3. En modelos.ConstantesHDS5 añadí el campo `forma: int` (1 o 2) y actualizá
   `desde_dict`. Poné Forma 1 en las tres filas circulares existentes: es lo que
   hoy hacen, y así el cambio no mueve ningún número.

4. En constantes_normativas.HDS5_INLET añadí las filas del cajón con la misma
   convención de clave que las circulares ("cajon_concreto_<borde>"), DERIVADAS de
   la transcripción del punto 1, nunca escritas a mano. Es el mismo patrón que
   MANNING deriva de TABLA_09_FILAS.

5. Actualizá docs/manifiesto_citas.md y comprobá test_manifiesto_citas.py.

Criterio de salida:
- test_normativa_pdf.py corre COMPLETO (no saltado) y en verde
- cada fila nueva tiene numeral, página impresa y página PDF verificadas
- el par passed/skipped sube solo por tests nuevos, ninguno rojo
- ningún módulo de cálculo tocado, y ningún número de cálculo movido

[pegar aquí la CLÁUSULA NORMATIVA COMÚN de §9-bis]
```

---

### C3 · HDS-5 Forma 2 en M4

**Opus 5 · `high` · plan mode SÍ.** Corta, y es donde está el error fácil.

```
Lee CLAUDE.md, docs/ruta_familia_c.md (§4.3, §4.5, §15 y la regla vinculante #2 de
§6) y el num. A.2.1 de normas/hif12026.pdf, ecs. (A.1) y (A.2), pág. impresa
A.1-A.2.

1. Bifurcá M4._hw_sobre_D_no_sumergido por `hds5.forma`:
   Forma 1 (la de hoy): HWi/D = Hc/D + K·(q*)^M + Ks·S
   Forma 2:             HWi/D = K·(q*)^M
   LA FORMA 2 NO LLEVA EL TÉRMINO Ks·S. Verificalo vos contra la ec. (A.2) antes
   de escribir la línea, y dejá la cita en el docstring. Copiar la Forma 1 y
   cambiarle las constantes es el defecto que esta sesión existe para evitar.

2. _hw_sobre_D_sumergido (ec. A.3) NO cambia: es común a las dos formas y sí lleva
   Ks·S.

3. La zona de transición entre 3.5 y 4.0 (Q_LIM_NO_SUMERGIDO / Q_LIM_SUMERGIDO,
   escala inglesa a propósito) interpola entre las dos ramas. Comprobá que la
   interpolación sigue siendo correcta cuando la rama no sumergida es la Forma 2.

4. El PasoDeMemoria del control de entrada tiene que IMPRIMIR QUÉ FORMA SE USÓ Y
   POR QUÉ, con su cita. Un lector de la memoria no puede tener que deducirlo. El
   por_qué sale de un Fundamento de normativa/fundamentos.py — de los que CN dejó
   redactados en §15 —, no se escribe en el módulo.

5. Añadí casos patrón para la Forma 2 en tests/fixtures/casos_patron.py,
   calculados A MANO desde la ecuación, nunca desde la salida del código.

Criterio de salida: los casos patrón circulares existentes intactos; al menos un
caso patrón nuevo por rama (Forma 2 no sumergida, transición, sumergida); y la
memoria de un punto que use Forma 2 imprime la forma, su cita y su por_qué.

[pegar aquí la CLÁUSULA NORMATIVA COMÚN de §9-bis]
```

---

### C4 · `SeccionRectangular`: la hidráulica del marco

**Opus 5 · `xhigh` · plan mode SÍ.**

```
Lee CLAUDE.md y docs/ruta_familia_c.md (§4.1, §4.2, §4.5, §15 y las reglas
vinculantes #3 y #4 de §6).

1. Implementá `SeccionRectangular(B, H)` según §4.1. MODELA UNA CELDA: los
   coeficientes de HDS-5, el radio hidráulico y el control de entrada son POR
   BARRIL. El número de celdas no entra en la sección; se reparte el caudal fuera.
   Dejá esa razón escrita en el docstring de la clase.

2. Tirante crítico cerrado: y_c = (q²/g)^(1/3) con q = Q/B. No uses brentq: para
   la rectangular la solución es exacta. El exponente 1/3 y el 2 del cuadrado van
   marcados `# literal-ok`.
   La guardia de finitud va a la SALIDA del cálculo, con la forma que fijó
   MAT-D13: umbral MEDIDO (nunca un != 0 genérico), condición escrita en positivo
   y negada (un NaN es falso frente a <= igual que frente a >), y mensaje que
   nombra al PAR culpable. Si desborda, LimiteNumericoError.

3. Comprobá que M3.tirante_normal converge para la rectangular. Manning es
   monótono en y para esta sección; si el resolutor por Brent que usa la circular
   no encaja, decilo y proponé el cambio en vez de forzarlo.

4. caudal_adimensional con la sección: q* = Ku·Q / (A_llena · √altura), donde
   `altura` es la altura INTERIOR del barril (el "D" de HDS-5) y A_llena es el
   área llena del barril. No hay diámetro equivalente.

5. CADA FUNCIÓN PÚBLICA NUEVA EMITE SU PasoDeMemoria: qué, por_qué (de un
   Fundamento de normativa/fundamentos.py, con verbo sostenido por el `caracter`
   de alguna de sus citas — usá los que CN dejó redactados en §15), fórmula con
   cita_id, sustitución con la PROCEDENCIA de cada valor, umbral con su carácter
   en la fuente, y veredicto con margen. Un paso sin por_qué no se construye; un
   umbral sin cita_id tampoco. Esto no es opcional ni se difiere a C8.

6. Casos patrón nuevos para la rectangular: tirante normal, tirante crítico,
   control de entrada por las dos formas, control de salida. Calculados a mano.

Criterio de salida: todo lo circular intacto; la rectangular con al menos un caso
patrón por función pública nueva; y `tests/test_memoria_sustentada.py` en verde
sobre los pasos nuevos.

[pegar aquí la CLÁUSULA NORMATIVA COMÚN de §9-bis]
```

---

### C5 · Catálogo, criterios y verificaciones del cajón

**Opus 5 · `xhigh` · plan mode SÍ.** Cuatro criterios nuevos y **ninguno se rellena**.

```
Lee CLAUDE.md (la taxonomía de cinco etiquetas y el bloque "Nivel de entrega"),
docs/ruta_familia_c.md (§4.5, §5-F3, §15 y las reglas vinculantes #1, #6, #7 y #10
de §6) y el docstring de M2_material.py bajo "Familia C queda sin candidatos".

REGLA QUE MANDA EN TODA LA SESIÓN: donde la hoja de ruta v8 no habla del marco, se
abre un Criterio(valor=None) con nivel, sensibilidad, resolución y justificación,
y el cálculo se detiene con CriterioPendienteError. NO elijas vos ningún valor.
El tesista los declara después, y la memoria imprime de dónde vino cada uno.

1. Criterios nuevos en criterios_adoptados.py, los cuatro NIVEL_PERFIL, los cuatro
   SIN VALOR, y los cuatro con `sensibilidad` y `resolucion` (lo exige
   _verificar_nivel para todo [A] de perfil). Los que cubran un vacío normativo
   verificado llevan `vacio_verificado`, o no saldrán en bloque_acotaciones:

   - `secciones_cajon_normalizadas` [A]. La progresión B×H. Justificación
     OBLIGATORIA: el num. 4.1.1.3.4 a) EXCEPTÚA los cruces de canal de riego del
     piso de 0.90 m ("se adoptarán secciones de acuerdo a cada diseño
     particular"). El literal ya está en constantes_normativas.DIAMETRO_MIN_TEXTO
     y DIAMETRO_MIN_AMBITO: CITALO, no lo transcribas de nuevo. Este criterio NO
     hereda el piso circular.
   - `n_manning_cajon` [N->]. La Tabla Nº 09 NO TIENE FILA DE CAJÓN: §15 lo
     verificó en CN. Declará de qué fila se toma la analogía y por qué, con la
     forma exacta de `n_manning_hdpe`, y dejá la divergencia visible en la memoria.
   - `embocadura_cajon` [A]. Qué carta y escala de la Tabla A.1 aplica (aletas,
     chaflán, bisel, esviaje). Acoplado a Sec. 9.1 igual que la circular: cambiar
     el detalle obliga a cambiar las constantes, y las dos decisiones se mueven
     juntas. Dejalo escrito en el criterio.
   - `n_celdas_cajon` [A]. Con la razón de Sec. 3.1 ("con palizada: sección única
     mayor, no múltiple") y lo que implica para V6.

   NO abras `v_max_cajon`. La Tabla Nº 10 clasifica por REVESTIMIENTO, no por
   forma, y "Concreto 3.0 – 6.0" sirve tal cual. Abrirlo sería inventar un vacío.

2. M2_material: `materiales_candidatos` deja de devolver () para Familia.C y
   devuelve el candidato de marco de concreto. `catalogo` gana la forma. REESCRIBÍ
   el epígrafe "Familia C queda sin candidatos" del docstring del módulo: describe
   un estado que deja de ser cierto, y dejarlo es peor que no haberlo escrito.

3. MD._motivo_sin_candidatos: NO lo borres. Se estrecha — sigue siendo el camino
   correcto para una familia futura sin candidatos — y su rama de Familia C sale.

4. M5_verificaciones:
   - v1_borde_libre: el 25 % es "de la altura, diámetro o flecha de la estructura"
     (num. 4.1.1.3.7 b). Para el cajón la magnitud es la altura interior. §15 lo
     verificó. Comprobá que el umbral, su cita Y SU CARÁCTER (el numeral
     RECOMIENDA y el proyecto lo endurece) siguen saliendo en bloque_umbrales.
   - v9_disponibilidad_diametro: pasa a ser disponibilidad de SECCIÓN. Si le
     cambiás el nombre, arrastrá los marcadores de las plantillas.
   - v6_material_solido_arrastre: mientras `n_celdas_cajon` fije 1, V6 sigue
     valiendo trivialmente, PERO su docstring tiene que decir que ahora depende de
     un criterio declarado y no de que MD no sepa hacer multibarril.

5. Implementá la declaración que CN redactó en §15 punto 4: que la memoria diga,
   donde corresponda, que a nivel de perfil el marco se dimensiona por V1/V4/V4b y
   no por el criterio de Sec. 2.3 (no alterar la rasante hidráulica ni el borde
   libre del canal), que queda diferido. Esto NO puede quedar en un docstring.

6. Actualizá los tests que pinnean el contrato viejo, y decí en el reporte cuál
   cambiaste y por qué: test_M2_material.py:283, test_MD.py:719/743/747,
   test_M1_clasificacion.py:394.

Criterio de salida: `cli.py tests/ejemplo_puntos.csv --luz 2.75` sobre C-01 ya NO
dice "no ofrece material candidato". Dice que faltan declarar los criterios
nuevos, con su concepto, su fuente y qué los resuelve, en el bloque de pendientes.

[pegar aquí la CLÁUSULA NORMATIVA COMÚN de §9-bis]
```

---

### C6 · Entradas: CSV, CLI, variables y dominios

**Sonnet 5 · `high` · sin plan mode.**

```
Lee CLAUDE.md y docs/ruta_familia_c.md (§4.5 y §5-F5).

1. cli.CLAVES_EXTERNAS es hoy ("luz_m","TW_m","longitud_m","Q_m3s","S_conducto",
   "L_hidraulico_m") + CLAVES_TEXTO. Añadí las claves que el marco necesita y que
   Sec. 1.2 no trae como columna. Cada clave nueva se documenta en el docstring
   del módulo, en el bloque "Datos que NO están en el CSV", con la misma forma que
   las cinco de hoy: unidad, de dónde sale, y qué se detiene sin ella. Ninguna
   lleva valor por defecto.

2. variables_entrada.py: una entrada _Columna por dato nuevo, con concepto, unidad
   y `resolucion` (qué lo fija y su dominio). Ese archivo es lo que la memoria y la
   GUI leen para explicar de dónde sale cada dato: una entrada pobre aquí es un
   hueco en el reporte, no un detalle interno.

3. dominios.py: rango FÍSICO posible de cada dato nuevo. Ojo con la regla: ese
   archivo acota lo que un dato PUEDE SER, no lo que la aritmética puede llevar.
   No le pongas techos para evitar desbordes; eso es LimiteNumericoError a la
   salida del cálculo.

4. M0_carga._VACIAS_FAMILIA_C: revisá si sigue siendo la lista correcta ahora que
   la Familia C se dimensiona. Si una columna deja de poder ir vacía, decilo.

5. Añadí al fixture tests/ejemplo_puntos.csv lo que haga falta para que C-01
   corra, SIN inventar valores de proyecto: si un dato es del expediente, va vacío
   y el informe lo reclama.

Criterio de salida: una clave mal escrita en --datos-externos sigue siendo
DatoInvalidoError y no un aviso; test_variables_entrada.py y test_cli.py en verde;
y cada dato nuevo aparece en la memoria con su procedencia, no como un número
suelto.

[pegar aquí la CLÁUSULA NORMATIVA COMÚN de §9-bis]
```

---

### C7 · Camino a perfil: M7, M8 y V7

**Opus 5 · `high` · plan mode SÍ.** Lo que todo el mundo asume diferido y no lo está.

```
Lee CLAUDE.md y docs/ruta_familia_c.md (§4.5, §5-F4, §15 y las reglas vinculantes
#8 y #9 de §6).

CONTEXTO QUE IMPORTA: `--alcance perfil` difiere la Fase 8 COMPLETA y la Fase 9
COMPLETA, pero V7 (flotación) SÍ SE EVALÚA a perfil — se comprueba corriendo
`cli.py ... --alcance perfil` sobre A-01. O sea que M8.empuje_flotacion_kn_m y
M8.peso_relleno_kn_m están en el camino de perfil y no son diferibles.

1. M8.empuje_flotacion_kn_m y M8.peso_relleno_kn_m reciben hoy `D_exterior` y
   suponen un cilindro. Generalizalos a la sección exterior. Para un prisma
   rectangular es más simple, no más difícil: no lo compliques.

2. M8.factores_carga_flotacion: la fila de γ_EV del cajón es «Pórticos rígidos»
   (1.35/0.90), NO «Estructura rígida enterrada». El comentario de
   criterios_adoptados['factores_carga_aashto'] ya lo anticipa por escrito —
   citalo al abrir la rama. Verificá el par de valores contra el Manual de
   Puentes, Tablas 2.4.5.3.1-1/-2, pág. impresa 143, con
   `verificador-normativo`. Y comprobá que la elección de fila sale en la memoria
   como elección del proyecto, no como si la tabla la impusiera.

3. M7.cobertura_minima_aashto: el criterio omite hoy el "whichever is greater" de
   la Tabla 12.6.6.3-1 porque en un conducto circular B'c = Bc por geometría. Para
   un cajón deja de valer. Traé el segundo término B'c/8 y cerrá lo que el propio
   criterio dejó anotado en `verificacion_pendiente`. Comprobá además qué fila de
   esa tabla aplica a un cajón de concreto y si está transcrita; si no lo está, es
   transcripción nueva con página verificada.

4. M7.altura_recubrimiento y M7.compatibilidad_geometrica: generalizalos a la
   sección. La regla del mayor entre EG-2013 y AASHTO no cambia, y su PasoDeMemoria
   tiene que seguir diciendo CUÁL de los dos gobernó.

5. constantes_normativas.SECCION_EG2013 mapea material -> sección 505/506/507/508,
   todas de tubería. Un marco vaciado in situ se paga por Sec. 503 (concreto
   estructural) + 504 (acero) y no tiene sección de tubería. Abrí la rama con la
   cita; si la decisión de C0 fue prefabricado, declaralo como vacío: EG-2013 no
   tiene sección de cajón prefabricado.

6. M5.v7_flotacion: que consuma lo anterior sin suponer forma.

Criterio de salida: C-01 llega a Fase 6 y Fase 7 con cotas y protección de salida,
y V7 se evalúa con un veredicto real (cumple o no), no con un bloqueo.

[pegar aquí la CLÁUSULA NORMATIVA COMÚN de §9-bis]
```

---

### C8 · Reporte, GUI, corrida completa y cierre

**Opus 5 · `ultracode` · sin plan mode.** Amplitud multiarchivo con corrida de cierre.

```
Lee CLAUDE.md (los bloques "La memoria la EMITE el cálculo" y "Tres cosas se
imprimen separadas") y docs/ruta_familia_c.md (§4.5, §5-F5, §7, §11 y §15).

1. M11_reporte: fila_resumen, _fila_resumen_csv y _tabla_diseno imprimen hoy un
   diámetro. Tienen que imprimir la sección adoptada con su etiqueta ("marco
   2.00 × 1.50 m", "Ø 0.90 m") sin que M11 haga aritmética sobre magnitudes: el
   test que barre su AST sigue vigente. La columna "Tipo" de las dos plantillas de
   src/plantillas/ y los marcadores de MARCADORES acompañan el cambio.

2. AUDITORÍA DEL CONTRATO DE MEMORIA (§4.5), bloque por bloque, sobre un punto de
   Familia C ya dimensionado. Comprobá y reportá, con la evidencia pegada:
   - bloque_criterios: los cuatro criterios nuevos, con etiqueta, concepto,
     fuente, sensibilidad, resolución y valor EFECTIVO con marca de procedencia
   - bloque_acotaciones: aparecen los que llevan `vacio_verificado`. Si alguno
     falta, el criterio no lo declaró: arreglalo en el criterio, no en el bloque
   - bloque_umbrales: el carácter de cada umbral nuevo (recomendación endurecida
     por el proyecto vs exigencia)
   - bloque_pendientes: qué falta, quién lo resuelve, qué bloquea, en qué puntos
   - los pasos del punto: cada uno con su por_qué, su fórmula citada y la
     procedencia de cada valor sustituido
   - la declaración de §15 punto 4 (que a perfil el marco se dimensiona por
     V1/V4/V4b y no por el criterio de Sec. 2.3) sale visible
   - fuente / interpretacion / lo que el proyecto hace, separados (NOR-HID-04)

3. Comprobá que toda frase entrecomillada nueva sale de
   Registro.textos_literales() y no de una transcripción a mano en un docstring.

4. gui/app.py y gui/componentes.py: que la Familia C aparezca en el tablero de
   resumen y que sus criterios nuevos sean declarables en caliente por la ventana
   emergente, como cualquier otro [A] de perfil. test_gui_contrato.py manda.

5. CORRIDA DE CIERRE. Con los criterios de C5 declarados con valores de tanteo
   pasados por --datos-externos o por la GUI (NO escritos en
   criterios_adoptados.py), corré:
       python3 cli.py tests/ejemplo_puntos.csv --datos-externos <json> --alcance perfil
   y comprobá que C-01 sale con: sección adoptada, control gobernante, hidráulica,
   longitud y cotas, protección de salida, y las verificaciones de perfil con
   veredicto. Generá también la memoria HTML y pegá el bloque del punto C-01.

6. Actualizá docs/ruta_familia_c.md §11 con lo cerrado, §13 con lo abierto y §15
   con los defectos contra la v8 que acumularon las sesiones, y
   docs/decisiones_diferidas.md con cada objeto que se conserve sin consumidor. No
   transcribas la razón: citá el símbolo donde ya está escrita, como exige
   test_decisiones_diferidas.py.

Criterio de salida: el par passed/skipped leído de origin/main con el entorno
declarado, la corrida del punto 5 pegada entera, y la auditoría del punto 2 con
las siete comprobaciones respondidas una por una.

[pegar aquí la CLÁUSULA NORMATIVA COMÚN de §9-bis]
```

---

# PARTE III — CIERRE

## 11. Criterios de aceptación del conjunto

Sobre `origin/main`:

1. Un punto de Familia C con sus criterios declarados sale de `cli.py --alcance perfil`
   con **sección adoptada, control gobernante, hidráulica, longitud, cotas de entrada y
   salida, y protección de salida**.
2. Las verificaciones de perfil (V1, V2, V2b, V3, V4, V4b, V6, V7, V9, G1, G2) dan
   veredicto real para ese punto, no bloqueo.
3. La Fase 8 y la Fase 9 salen marcadas como **diferidas por alcance**, con motivo escrito.
4. **Cada paso del procedimiento aplicado al marco tiene numeral en §15**, y ese numeral
   sale impreso en el `por_qué` del paso correspondiente de la memoria.
5. **Cada valor de cálculo sale en la memoria con su procedencia**: los cuatro criterios
   nuevos en `bloque_criterios`, los que cubren vacío en `bloque_acotaciones`, y los
   umbrales con su carácter en `bloque_umbrales`.
6. La sustitución del criterio de dimensionamiento de la Familia C (V1/V4/V4b en lugar de
   Sec. 2.3) está **declarada y visible**, no implícita.
7. Ningún criterio nuevo tiene valor escrito en `criterios_adoptados.py`.
8. `test_normativa_pdf.py` corre completo, no saltado, y en verde.
9. El par `passed / skipped` se reporta leído de `origin/main`, con el entorno declarado,
   y `collected = passed + skipped` se mantiene.
10. `casos_patron.py` cubre la sección rectangular en cada función pública nueva.

## 12. Lo que conviene NO hacer

- **No escribir un `M3_hidraulica_cajon.py` paralelo.** Es `SIS-A-07`.
- **No aplicar un paso del procedimiento sin numeral** «porque es lo que se hace para el
  circular». Es el defecto que CN existe para impedir.
- **No editar `docs/hoja_de_ruta_alcantarillas_v8.md`.** Los defectos van a §15.
- **No heredar el piso de 0.90 m para el cajón.** Regla #1.
- **No copiar la Forma 1 de HDS-5 con constantes de cajón.** Regla #2.
- **No abrir un `v_max_cajon`.** Regla #7.
- **No inventar el n de Manning del marco.** Regla #6.
- **No renombrar `Geometria.y_sobre_D`.** Lo consumen V1, M11 y las dos plantillas.
- **No poner techos en `dominios.py` para evitar desbordes.**
- **No escribir valores en `criterios_adoptados.py`.** Los declara el tesista.
- **No dejar un `Acotada` describiendo un alcance que ya no es el suyo.**

## 13. Deuda declarada, fuera de este alcance

**VC1 — no alteración de la rasante hidráulica ni del borde libre del canal.** Sec. 2.3
fija el requisito y ninguna verificación lo implementa; **no es V5**, que es el remanso
dentro del derecho de vía. VC1 necesita el nivel de agua de diseño y el borde libre del
canal, y su cierre exige además reescribir `remanso_derecho_via`, que hoy solo habla de
DG-2018 y no de la faja marginal ni de la Ley 29338. **Es la verificación que de verdad
gobierna a la Familia C**, y es lo primero que hay que abrir después de este alcance.
Mientras tanto, su sustitución por V1/V4/V4b se declara (CN punto 4, C5 punto 5).

**Diseño estructural del pórtico.** AASHTO LRFD Sec. 5 y 12.11: factor de interacción
suelo-estructura, distribución de carga viva a través del relleno (3.6.1.2.6), momentos y
cortantes del marco. La Fase 8 de la v8 ya dice *«Para el marco de concreto del canal de
2.75 m no aplica la simplificación: diseño completo por AASHTO LRFD Sección 5»*.
`--alcance perfil` lo difiere entero, y la 9.ª ed. está en `normas/`.

**Predimensionamiento del cabezal.** El programa **no dimensiona cabezales de ninguna
familia**: `M9.geometria_adoptada()` lee el criterio `predimensionamiento_cabezal`, cuya
ficha dice *«Lo resuelve: Plano de encofrado del cabezal, acotado»*. M9 verifica la
estabilidad de una geometría que el proyectista propone. Para el perfil, el cabezal se
predimensiona por plano tipo o regla de práctica y se declara como criterio `[A]` con su
sensibilidad y su procedencia; la memoria lo imprime como valor adoptado y trazado.
Convertirlo en salida del cálculo sería un módulo nuevo cuyas reglas serían todas `[A]` o
`[C]`, porque ni el Manual de Hidrología ni el de Puentes tabulan un predimensionamiento.

**Elección de tipo a partir del suelo de fundación.** El num. 4.1.1.3.4 a) recomienda el marco
*«cuando se tiene la presencia de suelos de fundación de mala calidad»* y la columna
`sucs_fundacion` del CSV se carga, se valida y no la lee nadie. Ese numeral es su **primer
consumidor plausible con numeral**, pero entre los dos falta un mapeo SUCS → «mala calidad»
que la fuente **no da**, y cablearlo obliga además a cambiar el esquema de
`variables_entrada._Columna.criterio_destino`, que hoy admite un solo destino. **No se abre en
este alcance**: en la Familia C el tipo ya lo fija la Sec. 2.3, de modo que el criterio no
cambiaría ningún resultado y sí frenaría el pipeline. El análisis completo, con las tres cosas
que faltan, está en **§15.5**.

## 14. Decisiones de alcance

*(La rellena C0. Dos decisiones: vaciado in situ o prefabricado; una celda o multicelda.)*

## 15. Numeral por paso, y defectos abiertos contra la hoja de ruta v8

*Abierta por la sesión **CN**. Cuatro apartados: **(a)** la tabla numeral-por-paso (§15.2),
**(b)** los `Fundamento` redactados (§15.7), **(c)** la declaración de la sustitución del
criterio de dimensionamiento de la Familia C (§15.6), y **(d)** los defectos abiertos contra
la v8 (§15.8). Las sesiones C1–C8 la alimentan; **ninguna la contradice sin pararse antes**.*

> **Cómo se citan aquí los textos literales.** Este documento es un documento de trabajo y
> entrecomilla la frase que sostiene cada lectura, porque sin ella la tabla no se puede
> revisar. **En el código no se transcribe ninguna otra vez**: toda frase que la memoria
> imprima entre comillas sale de `Registro.textos_literales()`, verificada contra su página
> (§4.5, y la regla de `CLAUDE.md`). Cuando abajo aparece una cita **que todavía no está en
> el registro**, va marcada `POR TRANSCRIBIR (C2)` y **no se puede usar hasta que C2 la
> transcriba y `test_normativa_pdf.py` la verifique**.

### 15.0 Con qué se leyó, y qué se verificó

| | |
|---|---|
| Fuente primaria | `normas/Hidrología, Hidráulica y Drenaje (Versión Libro).pdf` |
| SHA-1 | `a31e853b8171b931863d7afa4379bbbc57cacb0d` — 225 páginas |
| Desfase de paginación | **página PDF = página impresa + 3**, medido leyendo el folio impreso en ocho páginas del tramo (PDF 73→70, 74→71, 75→72, 76→73, 77→74, 78→75, 79→76, 80→77) y en la lámina (PDF 212→209). **No supuesto.** |
| Tramo barrido | num. 4.1.1.3 completo: impresas **70–83** = PDF **73–86**; más Anexos, Lámina Nº 03: impresa **209** = PDF **212** |
| Método | cuatro corridas de `verificador-normativo`, cada una con el extractor del repositorio (`python3 -m src.normativa.extraccion`). **Las tablas y la lámina se leyeron sobre la página RENDERIZADA**, y la Tabla Nº 09 además contra las coordenadas de línea base de cada palabra: la extracción lineal pierde la alineación fila↔valor, que es justo lo que aquí se discute. |
| Contraprueba de las citas | Las **23 frases** que §15 entrecomilla se buscaron una a una, normalizadas, **en la página que cada una declara**, con `extraccion.aparece_en_pagina`: **23 de 23 aparecen**. Ninguna cita de esta sección manda al revisor a una página donde no está lo que promete — que es el género de defecto de `NOR-HID-05` y `DIS-HR-G-LAUSHEY`. |

**Resultado global del barrido, y es el que ordena toda la tabla:** en los numerales
**4.1.1.3.1, .2, .3, .5, .6 y .7 completos** —impresas 70 a 83— las palabras **«marco»,
«cajón», «rectangular» y «cuadrada» aparecen CERO veces**. Aparecen concentradas en un solo
sitio, el **4.1.1.3.4 a) «Tipo y sección»** (impresas 71–73), que es precisamente el numeral
que **autoriza y recomienda** el marco. Y en los numerales .1, .2, .3 y .5 tampoco aparecen
«tubería», «tubo» ni «sección»: el término que usan es «**estructura**» y, una vez,
«**conducto**».

### 15.1 La regla de lectura, y por qué no es «se aplica igual»

El principio rector de §3 dice *«no aplicar nada sin numeral»*. Aplicado a la forma de la
sección, se concreta en una regla con tres tramos, y el orden importa:

**1. El marco ES una alcantarilla para este Manual, y eso no es analogía.** El num. 4.1.1.3.1
define la alcantarilla por **luz y función**, sin forma ni material: *«Se define como
alcantarilla a la estructura cuya luz sea menor a 6.0 m…»*. Y el 4.1.1.3.4 a) nombra el
**marco de concreto en primer lugar** entre los tipos comúnmente utilizados, y las secciones
**«rectangulares y cuadradas»** entre las usuales. Un cruce de canal de 2.75 m de luz
resuelto con un marco cae dentro de la definición por su propio texto.

**2. Por tanto, un numeral de 4.1.1.3 que dice «alcantarilla» y no se restringe a una forma
aplica al marco DIRECTAMENTE, y su etiqueta es [N] — la misma que para el circular.**
Declarar una analogía donde no hace falta es **un defecto simétrico al de omitirla**:
degradaría a `[N→]` algo que el Manual ya dice, y una memoria que declara analogías de más se
vuelve indistinguible de una que las declara de menos.

**3. El vacío se abre en un solo sitio, y siempre con la misma forma: donde el valor sale de
una TABLA cuyas FILAS están enumeradas por un objeto que el marco no es.** Son tres, y solo
tres, en todo el procedimiento:

- **Tabla Nº 09** (Manning): sus filas de concreto dicen «tubo». → `n_manning_cajon` **[N→]**.
- **Tabla A.1 del HDS-5** (control de entrada): sus cartas son por forma y material. → **hay
  cartas de cajón** (Cartas 8–12), de modo que **no es un vacío**: es una fila distinta de la
  misma tabla. **[C]**, la misma etiqueta que hoy. *Este dato no lo verificó CN —su fuente es
  `normas/hif12026.pdf`, no el Manual MTC—: se toma de la regla vinculante **#2** de §6, y
  **C3 lo re-verifica** contra las ecs. (A.1) y (A.2) antes de escribir la bifurcación.*
- **Normas de producto** (AASHTO M170 = *pipe*): no tabulan un marco vaciado in situ. →
  `V9` y `espesor_pared_conducto` quedan **fuera de su alcance declarado**, no en analogía.

Todo lo demás del Manual —borde libre, velocidades, Laushey, mantenimiento, pendiente,
ubicación, palizada— es **neutro respecto de la forma**, verificado por ausencia sobre las
páginas declaradas arriba.

### 15.2 (a) Numeral por paso — Fases 2 a 7

Convenciones de las columnas: **«De qué habla»** es lo que el numeral **nombra**, no lo que
se le puede aplicar. **«Al cajón»** es `DIRECTO` (el numeral no distingue forma),
`ANALOGÍA` (hay que declararla), `NO APLICA` (la fuente lo excluye o queda fuera de su
alcance) o `FUERA DEL MANUAL` (lo sostiene otra fuente). Las páginas son **impresa / PDF**.

#### 15.2.1 Fase 2 — Clasificación y periodo de retorno

| Paso (símbolo) | Numeral, pág. impresa / PDF | De qué habla | Al cajón | Etiq. |
|---|---|---|---|---|
| Denominación por luz (`M1.PERFILES`, `F2.LUZ`) | **4.1.1.3.1** «Aspectos generales», 70 / 73 · **4.1.1.5.1**, 87 / 90 | «**alcantarilla**» / «**estructura**». Cero ocurrencias de forma o material | **DIRECTO** | **[N]** |
| Perfil de familia y sus notas (`M1.perfil_de`, `PERFILES[Familia.C]`) | **Sec. 2.3 de la v8** — *no hay numeral del Manual* | La v8 asigna a C «marco o multicelda» y el requisito de no alterar el canal | **DIRECTO**, pero de la **hoja de ruta**, no del Manual | **[A]** (decisión de la v8) |
| «Sección: marco o multicelda» respaldado por norma | **4.1.1.3.4 a)**, 71 / 74 y 72 / 75 · **Lámina Nº 03**, 209 / 212 | Nombra el marco como tipo, y lo dibuja **en cruce de canal de riego** | **DIRECTO** | **[N]** |
| Periodo de retorno (`M1.periodo_retorno_de`, `F2.TR`) | **3.6**, Tabla Nº 02, 25 / 28 | Riesgo admisible y vida útil. No distingue forma | **DIRECTO**… y **no procede** en C: su caudal es el del canal, no hidrológico | **[N]** |

> **Ninguno de los cuatro cambia por la forma de la sección.** La Fase 2 de un punto de
> Familia C ya sale verde hoy (§1.2) y **este trabajo no la toca**.

#### 15.2.2 Fase 3 — Tipo, material y durabilidad

| Paso (símbolo) | Numeral, pág. impresa / PDF | De qué habla | Al cajón | Etiq. |
|---|---|---|---|---|
| **Elección del tipo de estructura** (`M2.materiales_candidatos`, criterio nuevo) | **4.1.1.3.4 a)**, 71 / 74: *«Los tipos de alcantarillas comúnmente utilizadas … son; marco de concreto, tuberías metálicas corrugadas, tuberías de concreto y tuberías de polietileno de alta densidad.»* | Enumera el **marco de concreto** como primer tipo | **DIRECTO** | **[N]** |
| **Orientación a marco por suelo de fundación** (hoy sin consumidor — §15.5) | **4.1.1.3.4 a)**, 72 / 75: *«Generalmente, se recomienda emplear este tipo de alcantarillas cuando se tiene la presencia de suelos de fundación de mala calidad.»* | El marco, por nombre | **DIRECTO**, pero es **RECOMENDACIÓN atenuada** («Generalmente,») | **[N]** el enunciado; **[A]** el umbral de «mala calidad», que la fuente **no define** |
| **Libertad de cota de emplazamiento** | **4.1.1.3.4 a)**, 72 / 75: *«pueden ubicarse a niveles que se requiera, como colocarse de tal manera que el nivel de la rasante coincida con el nivel superior de la losa o debajo del terraplén»* | El marco, por nombre. Verbo **«pueden»** | **DIRECTO** — carácter **PERMISO** | **[N]** |
| **Sección mínima: el piso de 0.90 m** (`constantes_normativas.DIAMETRO_MIN`, `F3.D_MIN`) | **4.1.1.3.4 a)**, 72 / 75 | *«…sección mínima circular de 0.90 m (36”) de diámetro o su equivalente de otra sección, **salvo en cruces de canales de riego** donde se adoptarán secciones de acuerdo a cada diseño particular.»* | **NO APLICA** a la Familia C. La excepción es **expresa** y la Familia C **es** el conjunto de cruces de canal | — (queda **excluida**, no pendiente: `COND-DMIN-CANAL-RIEGO`, `Efecto.EXCLUYE`) |
| **Sección mínima: lo que SÍ la acota igualmente** | **4.1.1.3.7 d)** «Mantenimiento y limpieza», 80 / 83: *«Las dimensiones de las alcantarillas **deben permitir** efectuar trabajos de mantenimiento y limpieza en su interior de manera factible.»* | «alcantarillas», «dimensiones». **Cero** forma | **DIRECTO**, y es **EXIGENCIA sin número** | **[N]** la exigencia; **[A]** el valor → `secciones_cajon_normalizadas` |
| **Progresión de secciones normalizadas** (`M2.catalogo`, criterio nuevo) | *ninguno* — el 4.1.1.3.4 a) remite a «cada diseño particular» | — | **NO APLICA** ningún catálogo normativo | **[A]** con `vacio_verificado` |
| **Materiales** (`M2.catalogo`) | **4.1.1.3.4 b)**, 73 / 76: *«…no es posible dar una regla general para la elección del tipo de material…»* | Material, no forma | **DIRECTO** | **[N]** (y lo que fija es que **no hay regla**) |
| **Durabilidad** (`M2`, sulfatos/cloruros) | **E.060** Cap. 4, Tabla 4.4 | Concreto, no forma | **DIRECTO** | **[N]** |
| **Espesor de pared** (`M2.espesor_pared`) | **AASHTO M170 / ASTM C76** | ***pipe*** | **NO APLICA** a marco vaciado in situ | *fuera de alcance declarado* — `DatoFaltanteError`, ya previsto en `espesor_pared_conducto` |

#### 15.2.3 Fase 4 — Dimensionamiento hidráulico

| Paso (símbolo) | Numeral, pág. impresa / PDF | De qué habla | Al cajón | Etiq. |
|---|---|---|---|---|
| **Manning** (`M3.resolver_manning`, `F4.MANNING`) | **4.1.1.3.6**, 74 / 77: *«El cálculo hidráulico considerado para establecer las dimensiones mínimas de la sección para **las alcantarillas a proyectarse**, es lo establecido por la fórmula de Robert Manning\* **para canales abiertos y tuberías**…»* | El numeral **declara su propio ámbito**: «las alcantarillas a proyectarse». Cero adjetivos de forma en sus cuatro páginas | **DIRECTO por el ámbito que el numeral se da a sí mismo**, no por analogía: el marco es una alcantarilla (4.1.1.3.1 y 4.1.1.3.4 a). *Refuerzo, y va marcado como lectura del proyecto: un marco con `y < H` escurre como canal abierto, una de las dos clases que la oración nombra.* | **[N]** |
| **Área, perímetro y radio hidráulico** (`Seccion.area/perimetro`, `R = A/P`) | **4.1.1.3.6**, 74 / 77: *«A : Área de la sección hidráulica (m2)»*, *«P : Perímetro mojado (m)»*, *«R : Radio hidráulico (m)»*, `R = A/P` | Define las variables **sin geometría**: no dice cómo se calcula A ni P | **DIRECTO** — y por eso la abstracción `Seccion` de §4.1 **no inventa nada**: rellena lo que el numeral deja al cálculo | **[N]** las definiciones; las fórmulas de A y P del rectángulo son geometría elemental, `# literal-ok` |
| **n de Manning del cajón** (criterio nuevo `n_manning_cajon`) | **Tabla Nº 09**, 75 / 78 — **grupo A**: *«A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO»* | **El grupo es neutro** («conducto cerrado»): el marco cae dentro. **Las FILAS de «a. Concreto» no**: seis de siete dicen «tubo» | **ANALOGÍA declarable, DENTRO del grupo que ya lo cubre** | **[N→]** — ver §15.3.2, que es el hallazgo que corrige la regla #6 |
| **Tirante crítico** (`M4.tirante_critico`) | *ninguno del Manual* — HDS-5 | — | **FUERA DEL MANUAL**; la solución cerrada rectangular es álgebra, no norma | **[C]** (como hoy) |
| **Control de entrada** (`M4.control_entrada`) | **HDS-5** num. A.2/A.2.1, Tabla A.1 (A.8) | Cartas **por forma y material**; hay cartas de cajón (regla #2 de §6, **no verificada por CN**: su fuente es `hif12026.pdf`) | **DIRECTO a otra fila de la misma tabla** — **no** es analogía | **[C]** |
| **Control de salida** (`M4.control_salida`, `F4.HO`) | **HDS-5** 3.1.4 y 3.3.3 | `k_e`, fricción, `h_o`. Neutro respecto de forma | **DIRECTO** | **[C]** |
| **HW gobernante** (`M4.hw_gobernante`, `F4.CONTROL`) | **HDS-5** | Neutro | **DIRECTO** | **[C]** |

> **Lo único que cambia de etiqueta en toda la Fase 4 es el n de Manning.** Todo lo demás
> conserva la que ya tiene para el circular.

#### 15.2.4 Fase 5 — Verificaciones

| V | Numeral, pág. impresa / PDF | De qué habla | Al cajón | Etiq. |
|---|---|---|---|---|
| **V1** Borde libre (`M5.v1_borde_libre`, `F5.V1`) | **4.1.1.3.7 b)**, 79 / 82: *«Se recomienda que el diseño hidráulico considere como mínimo el 25 % de **la altura, diámetro o flecha** de la estructura.»* | **Nombra las tres magnitudes**, una por familia de forma. **Cero** mención de forma en el apartado | **DIRECTO — y el numeral es MÁS general que el código.** Para el marco la magnitud es **«altura»**, que es la primera que la fuente escribe | **[N]** (RECOMENDACIÓN endurecida por el proyecto) |
| **V2** Velocidad mínima (`M5.v2_velocidad_minima`, `F5.V2`) | **4.1.1.3.6**, 76 / 79 + 77 / 80 | *«Se deberá verificar…»* (EXIGENCIA) + *«recomendándose que la velocidad mínima sea igual a 0.25 m/s.»* (RECOMENDACIÓN). Habla del «conducto» | **DIRECTO** | **[N]** |
| **V2b** Sedimentación (`M5.v2b_sedimentacion`) | **HDS-5** 5.3.3, 5.11 | Pendiente y rugosidad del barril frente al cauce. Neutro | **DIRECTO** | **[C]** |
| **V3** Velocidad máxima (`M5.v3_velocidad_maxima`) | **Tabla Nº 10**, 76 / 79. Columna: **`TIPO DE REVESTIMIENTO`**. Fila **«Concreto 3.0 – 6.0»** | **Clasifica por revestimiento, NO por forma** — confirmado sobre la página renderizada | **DIRECTO, sin criterio nuevo** | **[N]** |
| **V4** Carga a la entrada (`M5.v4_carga_entrada`, `F5.V4`) | **Manual de Suelos** 4.5.4, 42 | Separación subrasante–napa freática. Ni forma ni conducto | **DIRECTO**, con la analogía que **ya** está declarada (napa → HW). La forma **no añade** una segunda analogía | **[N→]**, sin cambio |
| **V4b** Relación HW/altura (`M5.v4b_relacion_hw_d`) | *ninguno* — HDS-5 2.2.5 d) **describe**, no prescribe | — | **NO APLICA** ningún numeral; adopción del proyectista | **[A]**, sin cambio |
| **V5** Remanso en el derecho de vía | DG-2018 + Ley 29338 — **fuentes ausentes** del registro | — | **DIFERIDA** por alcance de perfil | — |
| **V6** Material sólido de arrastre (`M5.v6_material_solido_arrastre`) | **4.1.1.3.4 a)**, 72 / 75: *«…recomendándose utilizar obras con mayor sección transversal libre, sin subdivisiones.»* | «obras», «sección transversal libre». **Neutro respecto de forma** — y es exactamente el numeral que gobierna **multicelda** | **DIRECTO** | **[N]** el enunciado; **[A]** el `n_celdas_cajon` que lo hace evaluable |
| **V7** Flotación (`M5.v7_flotacion`) | Manual de Puentes, Tablas 2.4.5.3.1-1/-2, 143 | La tabla desglosa por **tipo de estructura**, no por forma de sección | **DIRECTO, pero CAMBIA DE FILA**: por la regla vinculante **#8**, la del cajón es **«Pórticos rígidos»** y no «Estructura rígida enterrada», que es la del tubo | **[N]** los γ; **[A]** la fila (`factores_carga_aashto`) |
| **V8** Evento extremo | *ninguno* | — | **DIFERIDA** | **[A]** |
| **V9** Disponibilidad de sección (`M5.v9_disponibilidad_diametro`) | **Catálogo**, no norma (`NOR-PRO-01`/`-02`) | — | **NO APLICA** a marco vaciado in situ | **[A]** de catálogo |

> **La fila de V7, con los dos números medidos, porque la regla #8 conviene entenderla bien.**
> `EV_estructura_rigida_enterrada` es **1.30 / 0.90** y `EV_porticos_rigidos` es **1.35 / 0.90**
> (`constantes_normativas.TABLA_GAMMA_P_FILAS`; las dos filas **ya están transcritas**, C5 sólo
> añade la clave del cajón a `factores_carga_aashto`). **V7 lee el MÍNIMO**, y el mínimo es
> **0.90 en las dos**: por tanto **el número de V7 no cambia** al pasar al cajón. Lo que cambia
> es el **máximo**, 1.35 frente a 1.30, y ése gobierna la **Fase 8**, que `--alcance perfil`
> difiere. Cambiar la fila igualmente **no es cosmético**: dejarla mal la haría entrar mal el día
> que la Fase 8 se ejecute, y el comentario que hoy justifica la fila del tubo —*«No es "Pórticos
> rígidos" … la Familia C, de marco o multicelda, sale sin candidatos»*— **describe un estado que
> C5 deja de ser cierto** y hay que reescribirlo, igual que el epígrafe de `M2_material`.

#### 15.2.5 Fase 6 — Protección de entrada y salida

| Paso (símbolo) | Numeral, pág. impresa / PDF | De qué habla | Al cajón | Etiq. |
|---|---|---|---|---|
| **d₅₀ de Laushey** (`M6.laushey_d50`, `F6.LAUSHEY`) | **4.1.1.3.7 c)**, ec. (49), 80 / 83 | **Variables: solo `d50`, `V` y `g`.** Ninguna dimensión de la estructura entra en la fórmula. El único «diámetro» del apartado es el de **la piedra** | **DIRECTO, sin matiz alguno.** `M6.laushey_d50(*, V)` ya es función de **una sola** variable: **el módulo no se toca** | **[N]** |
| **g de Laushey** (`G_LAUSHEY = 9.8`) | **3.12.5**, 63 / 66 y **4.1.1.5.4 b.2.4)**, 111 / 114 — **NO** el 4.1.1.3.7 c) | — | **DIRECTO** | **[N]**, con `DIS-HR-G-LAUSHEY` abierta contra la v8 |
| **Espesor y longitud del enrocado** | *ninguno* | — | **NO APLICA** | **[A]**, sin cambio |
| **Protección de entrada y salida, y solado** | **Lámina Nº 03**, 209 / 212 (fig. 3) | **Dibuja** el solado y la protección del cruce de canal. **Cero cotas numéricas** | **DIRECTO** como respaldo **tipológico**; **NO** sostiene ninguna magnitud | **[N]** el tipo; nada más |

> **La Fase 6 es la que menos trabajo da y conviene que quede dicho:** el paso que más se
> parecía a «esto seguro depende del diámetro» resulta ser el único del procedimiento cuya
> fórmula **no lleva ninguna dimensión de la obra**.

#### 15.2.6 Fase 7 — Compatibilidad geométrica

| Paso (símbolo) | Numeral, pág. impresa / PDF | De qué habla | Al cajón | Etiq. |
|---|---|---|---|---|
| **Pendiente longitudinal** (`ResultadoHidraulico.S`) | **4.1.1.3.3**, 71 / 74: *«La pendiente longitudinal de la alcantarilla **debe ser tal que** no altere desmesuradamente los procesos geomorfológicos…»* | «alcantarilla». Cero forma, cero tubería. **Y cero valores numéricos** | **DIRECTO** | **[N]** el enunciado; **ningún número** sale de aquí |
| **Ubicación en planta y esviaje** (`M7.factor_esviaje`) | **4.1.1.3.2**, 71 / 74 (numeral íntegro, un párrafo) | Dirección de la corriente. Cero forma | **DIRECTO** | **[N]** |
| **Longitud del conducto** (`M7.longitud_conducto`) | *sin numeral*: ancho de plataforma + taludes | — | **DIRECTO** (geometría) | — |
| **Cobertura mínima sobre la clave** (`M7.cobertura_minima_aashto`, `F7.RELLENO`) | **AASHTO LRFD** Tabla 12.6.6.3-1 | Conductos enterrados, por tipo | **DIRECTO, y no hay analogía que declarar** — pero **vuelve el segundo término `B'c/8`** del *whichever is greater*, que hoy se omite legítimamente porque en un círculo `B'c = Bc` y para un cajón deja de valer (regla **#9**; ya anotado en `verificacion_pendiente` del criterio) | **[C]**, con `vacio_verificado` |
| **Tamizado de rasante 7.A** (`M7.tamizado_rasante`) | composición de V4 + cobertura | Neutro | **DIRECTO** | mezcla, ya declarada |
| **Cotas de entrada y salida** (`M5.cota_entrada_supuesta`, `M7.cota_salida`) | **4.1.1.3.3** + criterio `origen_cota_fondo_entrada` | Neutro | **DIRECTO** | **[A]** el origen de la cota |
| **G1 / G2** (`M7.g1_rasante_congelada`, `g2_cota_salida`) | reglas de la v8, sin numeral | — | **DIRECTO** | — |

**Criterio de salida de §15.2, contado fila por fila.** La tabla tiene **42 pasos** y
**ninguno** queda como «se aplica igual» sin numeral ni analogía declarada. Se reparten así:

| | Pasos | Cuáles |
|---|---|---|
| **DIRECTO**, con numeral del Manual MTC verificado contra el PDF | **19** | luz, tipo, TR, orientación por suelo, cota de emplazamiento, mantenimiento, materiales, Manning, A/P/R, V1, V2, V3, V6, Laushey, g, Lámina 03, pendiente, ubicación, respaldo del tipo |
| **ANALOGÍA declarable** | **1** | `n_manning_cajon` — y **dentro** del grupo de la Tabla Nº 09 que ya cubre al marco (§15.3.2) |
| **NO APLICA**, con la exclusión citada | **6** | piso de 0.90 m, progresión de secciones, espesor de pared, V4b, V9, espesor/longitud del enrocado |
| **FUERA DEL MANUAL**, con su fuente propia y su etiqueta ya vigente | **9** | E.060 durabilidad, tirante crítico, controles de entrada y salida, HW gobernante, V2b, V4, V7, cobertura AASHTO |
| **DIFERIDOS por alcance**, con su constancia | **2** | V5, V8 |
| **Sin numeral por naturaleza** (geometría elemental o regla de la propia v8) | **5** | perfil de familia, longitud, tamizado 7.A, cotas, G1/G2 |

**Un solo paso de los 42 cambia de etiqueta al pasar del circular al marco**, y es el n de
Manning. Ése es el resultado de esta sesión y conviene decirlo así de crudo: **el
procedimiento del Manual peruano es casi enteramente neutro respecto de la forma de la
sección**, y lo poco que no lo es, no lo es por descuido sino porque copia sus filas de
Ven Te Chow.

### 15.3 Los cuatro numerales que deciden — resultado literal

#### 15.3.1 · 4.1.1.3.4 a) «Tipo y sección» — impresas 71–73 / PDF 74–76

Las cuatro afirmaciones que §6 y §10-CN dan por buenas **se confirman las cuatro**, y el
apartado resulta ser **el numeral más favorable a la Familia C de todo el Manual**. Pero no
es un bloque homogéneo: **tiene tres caracteres normativos distintos en tres párrafos
consecutivos**, y colapsarlos en uno es la forma exacta de `NOR-MEM-01`.

| Párrafo, pág. | Texto | Carácter | Qué autoriza |
|---|---|---|---|
| impresa 71 / PDF 74 | *«Los tipos de alcantarillas comúnmente utilizadas en proyectos de carreteras en nuestro país son; marco de concreto, tuberías metálicas corrugadas, …»* | **DEFINICIÓN / enumeración** | Que el marco de concreto es un tipo del catálogo del Manual, no una importación |
| impresa 72 / PDF 75 | *«Las secciones mas usuales son circulares, rectangulares y cuadradas.»* | **DEFINICIÓN** | Que la sección rectangular y la cuadrada son usuales, no excepcionales |
| impresa 72 / PDF 75 | *«…se adoptará una sección mínima circular de 0.90 m (36”) de diámetro o su equivalente de otra sección, salvo en cruces de canales de riego donde se adoptarán secciones de acuerdo a cada diseño particular.»* | **EXIGENCIA condicionada** | Que en un cruce de canal de riego **el piso no rige** y la sección se adopta caso por caso |
| impresa 72 / PDF 75 | *«Las alcantarillas tipo marco de concreto de sección rectangular o cuadrada **pueden** ubicarse a niveles que se requiera…»* | **PERMISO** | Libertad de cota de emplazamiento — que es justo lo que un cruce de canal necesita |
| impresa 72 / PDF 75 | *«Generalmente, **se recomienda** emplear este tipo de alcantarillas cuando se tiene la presencia de suelos de fundación de mala calidad.»* | **RECOMENDACIÓN atenuada** | La orientación a marco por suelo — ver §15.5 |

**Cuatro precisiones de transcripción**, porque son exactamente donde una segunda copia
diverge. El original escribe **«son;» con punto y coma**; **«mas» sin tilde** (errata del
Manual: reproducirla es la transcripción fiel, corregirla en silencio es alterar la fuente);
el **`36”` con comilla tipográfica U+201D**, no con comilla recta; y **«Nº» con o volada
(U+00BA)**.

> **CONSECUENCIA VINCULANTE PARA C5, y es nueva.** La cita
> `MC_HHD.4.1.1.3.4a` del registro **transcribe hoy sólo el tercer párrafo** —el del 0.90 m—
> y declara `caracter=EXIGENCIA`. Los párrafos de **PERMISO** y de **RECOMENDACIÓN**, que son
> los que sostienen el tipo de estructura de la Familia C, **no están transcritos en ninguna
> parte del repositorio**. Un `Fundamento` para «el tipo es marco de concreto» que cuelgue
> hoy de `MC_HHD.4.1.1.3.4a` **estaría apoyando un permiso sobre una exigencia**, y T11 lo
> dejaría pasar porque el carácter que lee es el de la cita, no el del párrafo. **C2 tiene que
> transcribir dos citas nuevas** antes de que C5 escriba su fundamento — ver §15.7.

#### 15.3.2 · 4.1.1.3.6, Tablas Nº 09 y Nº 10 — impresas 74–77 / PDF 77–80

**La Tabla Nº 10 sirve tal cual: CONFIRMADO, y la regla #7 queda en pie sin matices.** Su
título es *«TABLA Nº 10: Velocidades máximas admisibles (m/s) en conductos revestidos»* y el
encabezado de su primera columna es literalmente **`TIPO DE REVESTIMIENTO`**. Sus tres filas
son «Concreto 3.0 – 6.0», «Ladrillo con concreto 2.5 – 3.5» y «Mampostería de piedra y
concreto 2.0» (un solo valor). **Nada en ella nombra una forma.** No se abre `v_max_cajon`.
Confirmado también que la Tabla Nº 11 clasifica por **`TIPO DE TERRENO`** y su título dice
«en canales **no revestidos**»: no trata del conducto en absoluto.

**La Tabla Nº 09 NO tiene fila de cajón: CONFIRMADO. Pero la razón que la regla #6 escribe
es inexacta, y hay que corregirla antes de que llegue a la memoria.**

El barrido sobre las dos páginas que ocupa la tabla (impresas 75–76 / PDF 78–79) devuelve
**cero ocurrencias** de `marco`, `cajon`, `rectangul`, `cuadrad` y `box`. Hasta ahí, la regla
#6 acierta. Lo que no acierta es en el porqué. Leídas por coordenadas de línea base sobre la
página renderizada, **las siete filas hoja del ítem «a. Concreto» del grupo A son**:

| Fila (rótulo literal) | ¿Dice «tubo»? |
|---|---|
| `tubo recto y libre de basuras` | sí |
| `tubo con curvas, conexiones` | sí |
| **`afinado`** | **NO** |
| `tubo de alcantarillado con cámaras, entradas.` | sí |
| `Tubo con moldaje de acero.` | sí |
| `Tubo de moldaje madera cepillada` | sí |
| `Tubo con moldaje madera en bruto` | sí |

**Seis de siete dicen «tubo». La séptima, `afinado`, no dice nada de forma** — verificado por
coordenadas: en su línea hay **una sola palabra** en la columna de rótulos, y es `afinado`.

Y hay un segundo hecho que la regla #6 no recoge y que es el que de verdad decide: **el
GRUPO que contiene esas filas ya cubre al marco por su propio título**. Se llama
*«A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO»* — «conducto cerrado», no
«tubería» —, y `constantes_normativas.TABLA_09_GRUPO` ya lo tiene declarado como *«el único
grupo de la tabla que describe una alcantarilla»*.

**Reformulación de la regla #6, que C5 debe usar en vez de la actual:**

> El vacío de la Tabla Nº 09 **no es de grupo, es de fila**. El grupo A cubre al marco por su
> propio título («conducto cerrado con escurrimiento parcialmente lleno»); lo que la tabla no
> tiene es una fila que nombre la sección rectangular. Seis de sus siete filas de concreto
> están enumeradas por **tubo**; la séptima, `afinado`, está enumerada por **acabado** y no
> menciona forma alguna. Por eso `n_manning_cajon` es **[N→]**: una analogía **dentro del
> grupo que ya lo cubre**, entre filas enumeradas por un atributo que no es la forma. Es una
> analogía **más estrecha** que la de `n_manning_hdpe`, que cruza material.

**Las dos filas candidatas, con sus valores, para que C5 declare cuál toma y por qué** —y no
las elige esta sesión, porque elegir es lo que el tesista declara:

| Fila candidata | (n_mín, n_máx) | Argumento a favor | Argumento en contra |
|---|---|---|---|
| `tubo recto y libre de basuras` | **(0.010, 0.013)** | Es la que el proyecto **ya usa** para el concreto (`MANNING["concreto_tubo_recto"]`) y la que `n_manning_hdpe` toma por analogía: una obra con dos n distintos para el mismo concreto es peor que una analogía discutible | Su rótulo dice **tubo**, que es exactamente lo que el marco no es |
| **`afinado`** | **(0.011, 0.014)** | Es la **única fila del ítem sin forma en el rótulo**, y describe el acabado que un marco vaciado in situ tiene | El repositorio **no la transcribe todavía** (`TABLA_09_FILAS` sólo trae cuatro filas): exige transcripción y verificación en C2 |

> **Aviso a C5, y no es menor: `afinado` NO es «más conservador» sin más.** Sus dos valores
> son mayores, y por la regla de doble n eso mueve las dos ramas **en sentidos opuestos**: un
> `n_máx` mayor (0.014 frente a 0.013) es **más conservador** para capacidad y tirante, y un
> `n_mín` mayor (0.011 frente a 0.010) da **menos velocidad**, o sea es **menos conservador**
> para V3 y para el d₅₀ de Laushey. La dirección **no es uniforme** y el criterio tiene que
> decirlo, igual que `DIAMETRO_MIN_AMBITO` lo dice del piso de 0.90 m.

**Dónde NO se puede ir a buscar el n, y conviene dejarlo escrito antes de que a alguien se le
ocurra:** el grupo **B. CANALES REVESTIDOS** tiene un ítem «b. Concreto» con la fila
`afinado con plana`, que suena a la fila ideal para un marco de concreto. **No lo es**: el
grupo B describe **el cauce revestido**, no el conducto, y `TABLA_09_GRUPO` ya lo declara.
Tomar de B lo que se dimensiona con A sería cambiar de objeto a mitad de tabla.

**Advertencia de lectura que arrastra cualquier valor de A.2, y ya está declarada.** La
columna de valores del bloque A.2 está impresa **un renglón más arriba** que sus rótulos, de
modo que los números que se leen en la línea de `afinado` (0.013/0.015/0.017) **no son los
suyos**: los suyos, corrigiendo el corrimiento, son **0.011/0.012/0.014**. Esto **no es un
hallazgo nuevo**: el repositorio lo tiene declarado como `DIS-MCHHD-T09-A2-DESPLAZADA`
(`ERRATA_DE_IMPRENTA`), con las cuatro pruebas y con la correspondencia fila a fila contra
Ven Te Chow 1983 — donde `finished` es exactamente 0.011/0.012/0.014. C5 **cita esa
discrepancia**; no la vuelve a demostrar.

#### 15.3.3 · 4.1.1.3.7 b) «Borde libre» — impresa 79 / PDF 82

**Dice «altura, diámetro o flecha»: CONFIRMADO, literal y exacto.**

> *«El borde libre en alcantarillas es un parámetro muy importante a tomar en cuenta durante
> su diseño hidráulico, por ello, las alcantarillas **no deben** ser diseñadas para trabajar a
> sección llena, ya que esto incrementa su riesgo de obstrucción, afectando su capacidad
> hidráulica.*
> *Se recomienda que el diseño hidráulico considere como mínimo el 25 % de la altura,
> diámetro o flecha de la estructura.»*

Tres cosas que este apartado resuelve de un golpe:

1. **V1 no necesita ninguna analogía para el marco.** La fuente enumera **tres** magnitudes,
   una por familia de forma, y **«altura» es la primera que escribe**. Para el marco la
   magnitud es la altura interior, **por texto expreso**, no por extensión.
2. **El numeral es MÁS general que el código, no menos.** `Geometria.y_sobre_D` conserva su
   nombre (§4.1) y pasa a `y / seccion.altura`. Lo que el nombre `y/D` sugiere —que el
   Manual habla de un diámetro— **nunca fue cierto**: la nota de `MC_HHD.4.1.1.3.7b` ya
   declara que la fuente no escribe «y/D» y que el 0.75 es derivación del 25 %.
3. **Dos caracteres en dos oraciones.** La primera **prohíbe** («no deben ser diseñadas para
   trabajar a sección llena»); la segunda **recomienda** el 25 %. El proyecto endurece la
   segunda y eso ya sale en `bloque_umbrales`. **No cambia con la forma.**

#### 15.3.4 · 4.1.1.3.7 c) «Socavación local a la salida» — impresa 80 / PDF 83

**d₅₀ es función sólo de V (y de g): CONFIRMADO sobre la página renderizada.**

La ec. (49) es `d50 = V² / (3.1 · g)` y su lista de variables completa es:

> *«d₅₀ : Diámetro medio de los elementos de protección (m) · V : Velocidad media del flujo a
> la salida de la alcantarilla (m/s) · g : Aceleración de la gravedad (m/s2)»*

**Ninguna dimensión de la estructura entra en la fórmula.** El único «diámetro» del apartado
es el de la **piedra**, no el del conducto. `M6_proteccion.laushey_d50(*, V)` ya tiene esa
firma exacta: **la Fase 6 no se toca en todo este plan**, y eso es un resultado, no una
omisión.

Se confirma además, por segunda vía independiente, que **este numeral define `g` sin
número** — sólo con su unidad —, que es el objeto de la discrepancia `DIS-HR-G-LAUSHEY`, hoy
`ABIERTA_CONTRA_HOJA_DE_RUTA`. **La v8 sigue mal en ese punto mientras no se corrija**: quien
la lea sin leer el código creerá que el 9.8 es cita de la pág. impresa 80, y no lo es.

### 15.4 Lámina Nº 03 — existe, y hay que decir con precisión qué sostiene y qué no

**Existe. Página impresa 209 / página PDF 212**, en el Capítulo V — ANEXOS (portada del
capítulo: impresa 204 / PDF 207). Leída sobre la página renderizada a escala 4, y el cajetín
a escala 8.

**El cajetín tiene tres celdas** y su título general, literal, es:

> **«SECCIONES TÍPICAS DE ALCANTARILLAS CON PROTECCIÓN A LA ENTRADA Y SALIDA»**

**Trae TRES figuras, no dos**, apiladas verticalmente, cada una con su título centrado
debajo:

1. **ALCANTARILLA TIPO TUBERÍA METÁLICA CORRUGADA**
2. **ALCANTARILLA TIPO MARCO DE CONCRETO**
3. **ALCANTARILLA TIPO MARCO DE CONCRETO EN CRUCE DE CANAL DE RIEGO**

**El título de la tercera aparece exacto, carácter por carácter.** Es la sección típica del
caso exacto de la Familia C, dibujada en la norma peruana vigente, y hoy **no está citada en
ninguna parte del repositorio**.

Rótulos legibles en esa tercera figura, leídos sobre recorte a escala 9: `BORDE DE CANAL`
(dos veces, a izquierda y derecha), `EJE`, `ENTRADA`, `SALIDA`, `S%`, `SOLADO`, `a`, y
`VARIABLE` cuatro veces. **No** aparecen en ella `CALZADA`, `EMBOQUILLADO LONGITUDINAL` ni
`CAMA DE APOYO`: ésos pertenecen a las figuras 1 y 2 y el volcado de texto plano de la página
los mezcla, que es el error fácil aquí.

#### ¿Debe entrar al registro normativo? **Sí, y como `Cita` de tipología, con su alcance acotado por escrito.**

**Lo que sostiene:** que el Manual **reconoce, nombra y dibuja** la alcantarilla tipo marco de
concreto **en cruce de canal de riego** como sección típica, con solado y con protección de
entrada y salida. Es el respaldo normativo directo del **tipo de estructura de la Familia C**,
y hoy ese tipo se apoya sólo en la Sec. 2.3 de la hoja de ruta, que **no es fuente primaria**.
Con la lámina citada, «la Familia C es de marco» deja de ser una decisión del proyecto y pasa
a ser una lectura del Manual.

**Lo que NO sostiene, y hay que escribirlo en el propio objeto:** **ninguna magnitud**. Barrido
con expresión regular sobre todo token con dígito de la página PDF 212, el resultado completo
es `['209', '03']` — el folio y el número de lámina. **Cero cotas numéricas en las tres
figuras.** Toda dimensión está acotada como `VARIABLE` o con literal alfabético `a`, `b`, `c`
sin tabla de valores. El contraste que fija el punto y demuestra que la ausencia es deliberada
y no un fallo del extractor: **la Lámina Nº 04 sí acota** (`0.15m`, `0.20m`, `0.30m`, `0.40m`,
`0.60m`, `0.80 min.`, `1.00m`).

**Forma en que entra (para C2):**

- Una **`Cita`** `MC_HHD.LAMINA_03`, `pagina_impresa="209"`, `pagina_pdf=212`,
  `titulo_numeral` = el cajetín, `texto_literal` = `Verbatim` del rótulo de la tercera figura,
  `caracter=Caracter.DEFINICION`, **`metodo=IMAGEN`** — es un plano; leerla por extracción de
  texto es exactamente lo que `MetodoDeVerificacion` existe para obligar a declarar.
- Una **`AfirmacionNegativa`** colgada de ella: `que_no_dice="la Lámina Nº 03 no acota ninguna
  dimensión"`, `ambito_barrido="las tres figuras de la página impresa 209 (PDF 212), leídas
  sobre la página renderizada; el único token numérico de la página es el folio y el número de
  lámina, frente a la Lámina Nº 04 que sí acota siete cotas"`. Sin ella, la cita se leerá
  antes o después como si respaldara una geometría.
- Una **`Discrepancia`** interna del Manual — ver §15.8, defecto **D-6**.

> **Y la contrapartida honesta, porque esta cita es tentadora:** con la lámina en el registro,
> `secciones_cajon_normalizadas` **sigue siendo `[A]` sin valor**. La lámina respalda el
> **tipo**, no el **tamaño**. Cualquier constante `[N]` que se apoye en la Lámina Nº 03 para un
> ancho, una altura, un espesor o una longitud de solado tendría la etiqueta equivocada.

### 15.5 `sucs_fundacion` — el numeral es su primer consumidor PLAUSIBLE, y todavía no basta

**El planteo de §10-CN punto 3 es correcto en su premisa y hay que matizarlo en su
conclusión.** La premisa: la Sec. 3.1 de la v8 dice «suelo de fundación deficiente → orientar
a marco de concreto», y el num. 4.1.1.3.4 a) **sí lo respalda**, literal e impreso (impresa 72
/ PDF 75). Confirmado.

**Estado medido de la columna hoy:**

- `variables_entrada.py::_Columna["sucs_fundacion"]` la declara con `criterio_destino=
  "c_phi_fundacion"` y `DeEnsayo(...)`, y su `trazabilidad_exigida` ya dice literalmente que
  *«es obligatoria en el encabezado de Sec. 1.2 aunque hoy ningún módulo la lea: su consumidor
  previsto es `c_phi_fundacion`, todavía vacío»*.
- `c_phi_fundacion` es `NIVEL_EXPEDIENTE` y `sin_consumidor` declarado: lo consumen E1–E5 de
  la Sec. 9.3, que esta CLI no ensambla.
- `modelos.py` ya declara por escrito que la obligatoriedad y la ausencia de lector **son las
  dos correctas a la vez**.

**Lo que falta para cablearlo, y son tres cosas, no una.** Ninguna la hace esta sesión:

1. **El numeral no define «mala calidad».** Dice *«suelos de fundación de mala calidad»* y no
   da ni un umbral, ni una lista de símbolos SUCS, ni un CBR. **El mapeo SUCS → «mala calidad»
   no está en el Manual**, y ponerlo sin declararlo es rellenar un vacío en silencio. Hace
   falta un criterio nuevo — llamémoslo `sucs_fundacion_deficiente` — con la lista de símbolos
   que el proyecto considera deficientes, **`[A]` o `[C]` según la fuente que lo respalde**, y
   **sin valor** hasta que el tesista lo declare. El candidato de fuente peruana es la **E.050**;
   la tabla de calidad por CBR del **Manual de Suelos num. 4.5.4** *no* sirve: clasifica la
   **subrasante**, no el suelo de **fundación**, y confundirlas sería el mismo género de error
   que `NOR-PUE-01`.
2. **El carácter no soporta una regla dura.** El párrafo es **RECOMENDACIÓN atenuada**
   («**Generalmente**, se recomienda»). No autoriza a **descartar** un tipo de estructura ni a
   **imponer** el marco: autoriza a **orientar**, y la memoria tiene que decir «orienta», no
   «obliga». Un `Fundamento` con `verbo=OBLIGA` sobre este párrafo **quedaría sin sostén y T11
   lo rechazaría** — que es exactamente lo que T11 existe para hacer.
3. **`_Columna.criterio_destino` es `Optional[str]`, uno solo.** Cablear un segundo consumidor
   obliga a decidir si el campo pasa a tupla o si el destino cambia. **Es cambio de esquema**,
   toca `variables_entrada` y su test, y **no cabe en C5**: pertenece a **C6** (frente F5,
   entradas), que es donde `variables_entrada` y `dominios` se tocan.

> **Veredicto de §15.5.** El num. 4.1.1.3.4 a) es hoy el **primer consumidor plausible y el
> único candidato con numeral** de `sucs_fundacion` — hasta ahora su único destino declarado
> era `c_phi_fundacion`, de **expediente**, de modo que la columna no tenía ningún consumidor
> de **perfil**. Pero **no es todavía un consumidor**: entre el numeral y la columna falta un
> criterio de mapeo que la norma no da.
>
> **Y lo correcto en este alcance es NO crear ese criterio todavía**, que es la conclusión
> contraria a la que se llega por inercia. Un `Criterio(valor=None)` **detiene el cálculo**
> (`CriterioPendienteError`), y la única salida a esa regla —`opcional=True`— **no encaja
> aquí**: el catálogo la define para el criterio que *«refina un valor que la norma ya fija»*,
> de modo que sin declarar *«el consumidor aplica el valor normativo por defecto y el cálculo
> sigue»*. Aquí **no hay valor normativo por defecto**: el Manual no define «mala calidad».
> Crearlo como bloqueante deja las dos salidas malas: si algún módulo lo invocara, **detendría
> la corrida** por una elección de tipo que en la Familia C **ya está tomada** por la Sec. 2.3;
> y si no lo invoca ninguno —que es lo que pasaría hoy—, entraría en `criterios_sin_valor()` y
> la memoria y la GUI lo anunciarían como **vacío bloqueante que nadie tiene obligación de
> contestar**, que es literalmente el defecto que la bandera `opcional` se creó para retirar.
> Y marcarlo `opcional=True` sería usar la bandera para lo que no es, que es exactamente la
> confusión que su propio docstring llama *«grave»* en los dos sentidos.
>
> **Por tanto: la columna queda sin cablear, y el hueco queda registrado** —numeral, mapeo
> ausente y cambio de esquema de `criterio_destino`— como deuda de §13, para abrirla el día
> que una sesión implemente de verdad la elección de tipo a partir del suelo. **Cablearla en
> C5 sería inventar el mapeo; declarar el criterio ahora sería frenar el pipeline entero por
> una decisión ya tomada.**

### 15.6 (c) La declaración de la sustitución del criterio de dimensionamiento de la Familia C

Ésta es la pregunta que más importa de §10-CN, y la respuesta tiene dos mitades: **el texto**
y **el vehículo**. El vehículo se decidió **midiendo el código**, no por estilo.

#### 15.6.1 El hecho que hay que declarar, dicho con precisión

Conviene enunciarlo mejor de como lo enuncia el prompt, porque la formulación exacta cambia
lo que se declara. **No es que el criterio de la Sec. 2.3 se sustituya por el de la Familia A.**
Medido sobre `M1_clasificacion.PERFILES`:

- `PERFILES[Familia.A].verificaciones_aceptacion = ("V1", "V2", "V4", "V5")`
- `PERFILES[Familia.C].verificaciones_aceptacion = **None**`, con el comentario ya escrito
  *«Sec. 2.3 no declara conjunto propio»*

Es decir: **la Sec. 2.3 nunca le dio a la Familia C un conjunto de aceptación.** Le dio **un
requisito** —*«No puede alterar la rasante hidráulica ni el borde libre del canal»*— y ninguna
verificación lo implementa. Lo que hace este alcance no es cambiar un conjunto por otro: es
**correr la batería general de la Fase 5 sobre un punto cuyo único requisito propio queda sin
evaluar**. Dicho así, la declaración se puede escribir sin exagerar ni suavizar.

#### 15.6.2 El texto exacto de la declaración

> **SUSTITUCIÓN DEL CRITERIO DE DIMENSIONAMIENTO — FAMILIA C (cruces de canal y dren).**
>
> La Sec. 2.3 de la hoja de ruta enuncia, para la Familia C, un requisito que ninguna otra
> familia tiene: la obra **no puede alterar la rasante hidráulica ni el borde libre del
> canal**. **Esta corrida no evalúa ese requisito.** La verificación que lo evaluaría —VC1—
> necesita el nivel de agua de diseño del canal y su borde libre, que no son columna de la
> Sec. 1.2 ni los aporta ningún tablero, y queda **diferida al expediente**.
>
> Lo que esta corrida evalúa en su lugar es la batería general de la Fase 5, cuyos numerales
> son neutros respecto de la forma de la sección: **V1** acota el tirante dentro del barril al
> 75 % de su altura interior (num. 4.1.1.3.7 b); **V4** acota la carga a la entrada bajo la
> subrasante de la **vía** (Manual de Suelos num. 4.5.4, por la analogía ya declarada); y
> **V4b** acota la relación entre esa carga y la altura del barril contra un tope adoptado por
> el proyectista. Los tres son el criterio de aceptación de una **alcantarilla de paso**.
>
> **La sustitución no es conservadora, y por eso se declara en vez de suponerse.** Los tres
> protegen la carretera y el conducto; **ninguno protege el canal**. Y no lo hacen porque
> **miden contra otra cota**: V1 compara el tirante contra la altura del propio barril, y V4
> compara la carga a la entrada contra la subrasante de la **vía**. El nivel que el requisito de
> la Sec. 2.3 protege —la rasante hidráulica del canal más su borde libre— **es un dato que este
> cálculo no tiene**, y ningún umbral puede acotar un nivel que no conoce. Por tanto no hay
> relación de orden garantizada entre los tres umbrales evaluados y el que no se evalúa: un
> punto puede cumplir V1, V4 y V4b **y aun así** elevar el nivel de agua aguas arriba por encima
> del borde del canal, sin que nada en esta memoria lo señale.
>
> **Por tanto, y mientras VC1 no exista: un veredicto «cumple» en un punto de Familia C
> significa que la obra es admisible como alcantarilla de paso. NO significa que sea admisible
> como cruce de canal.**
>
> **Qué cierra esta declaración:** el nivel de agua de diseño y el borde libre del canal (ANA
> o Junta de Usuarios del Bajo Piura), y la implementación de VC1 (§13).

#### 15.6.3 El vehículo: `bloque_alcance`, y por qué no los dos que el prompt proponía

**Mi lectura difiere de la del prompt en la primera mitad y coincide en el fondo de la
segunda.** Las tres razones son medidas, no de criterio:

**(1) `bloque_acotaciones` NO puede llevarla, por dos motivos y cada uno basta.**

- *Mecánico, medido corriendo el código:* `M11.acotaciones_declaradas()` filtra
  `c.vacio_verificado and criterio_efectivo(k).valor is not None`. Ejecutado sobre el catálogo
  actual devuelve **`['cobertura_minima_aashto']`**, y **no existe hoy ningún criterio con
  `vacio_verificado` y `valor=None`**. Los cuatro criterios que C5 crea son **todos sin valor
  por mandato**. Una acotación sería, por tanto, **invisible exactamente durante todo el nivel
  de perfil** —que es cuando la advertencia hace falta— y aparecería sólo después, cuando el
  tesista declare los valores.
- *Categórico, y es el que manda:* `bloque_acotaciones` es *«lo que el proyectista adoptó donde
  la norma no dice nada»*. Aquí **la fuente no calla**: la Sec. 2.3 habla, dice qué hay que
  cumplir, y el proyecto **no lo cumple todavía**. Eso no es una adopción sobre un vacío, es un
  **diferimiento de una exigencia declarada**. Meterlo en acotaciones sería reetiquetar una
  deuda como una decisión.

**(2) `esquema.Interpretacion` no tiene dónde colgarse ni dónde imprimirse.** Medido:
`Interpretacion` sólo es campo de `Cita` y de `TablaNormativa`; y en `M11_reporte` hay **un
solo** consumidor, `_interpretacion_tabla_10()`, **cableado a `MC_HHD.T10`**. Un
`Cita.interpretacion` llega hoy a `ventana_normativa` y al manifiesto, **no a la memoria**.
Y además **no hay `Cita` de la que colgarla**: la Sec. 2.3 es la hoja de ruta, no un documento
de `normas/`; el requisito de no alterar el canal se apoyaría en la Ley 29338 y la DG-2018,
que son **fuentes ausentes** del registro — el mismo motivo por el que `F5.V5` está en
`SIN_FUNDAMENTO`.

**(3) `bloque_umbrales` tampoco, y por una razón concreta que conviene dejar escrita.** Sus
funciones toleran `citas=()` (`caracter_del_umbral` devuelve `"SIN CITA"`), pero
**`fundamento_del_umbral` es incondicional**: llama a `_reg.fundamento(umbral["fundamento"])`,
y un `Fundamento` **exige al menos una cita del registro**. VC1 no tiene ninguna. Una entrada
de VC1 en `UMBRALES_DE_VERIFICACION` **rompería la construcción del bloque**.

**Lo que SÍ la lleva, y es el vehículo del §4.5 «Lo que falta y a quién» en su variante de
alcance:**

| Pieza de la declaración | Vehículo | Por qué ése |
|---|---|---|
| **La declaración entera**, una vez por punto de Familia C | **`bloque_alcance`**, vía un `Bloqueo(fase="Fase 5 - Verificaciones", etapa="VC1 - no alteración de la rasante hidráulica ni del borde libre del canal", tipo="DiferidoPorAlcance", diferido_por_alcance=True, mensaje=<el texto de §15.6.2>)` emitido por `cli` | Es el bloque que **imprime SIEMPRE** —su propio docstring dice que en alcance de expediente tampoco desaparece— y **no depende de que ningún criterio tenga valor**. Es **por punto**, de modo que nombra los puntos afectados. Y ya existe el precedente exacto: `cli._cabezal_diferido` y `cli._fase8_diferida`. `diferido_por_alcance=True` es lo que impide que además cuente como defecto del expediente en `Informe.cerrado` |
| **La advertencia junto al número**, en el desarrollo de V1 y de V4b del punto | **`PasoDeMemoria.nota_del_proyecto`**, que M11 imprime bajo `<dt class="interpretacion">Lo que pone el proyecto</dt>` (`M11_reporte`, ~1076) | **Aquí el prompt tenía razón: es una interpretación.** Sólo que el objeto que lleva una interpretación **por punto** a la memoria no es `esquema.Interpretacion` sino este campo, que M4 y M5 ya usan. Y es la lección de `NOR-HDS-05`: *un aviso que no señala el punto afectado es el «nadie se entera»* |
| **La deuda, para que no se pierda de vista** | **§13 de este documento** (ya está) + la actualización del tracker | El registro de deuda no es la memoria |

> **Regla NOR-HID-04 en este caso.** Las tres tipografías son «lo que la fuente **dice**», «lo
> que el proyecto **lee**» y «lo que el proyecto **hace**». Aquí **la primera no aplica**: no
> hay cita de `normas/` que entrecomillar, porque el requisito es de la hoja de ruta. Por eso
> la declaración puede viajar en un solo `mensaje` sin pegarse a ninguna cita — y por eso
> mismo **no puede** presentarse como si fuera norma: el texto de §15.6.2 nombra su fuente
> («la Sec. 2.3 de la hoja de ruta») en su primera línea, deliberadamente.

**La premisa del vehículo está MEDIDA, no supuesta.** Corriendo hoy
`python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance perfil --html …` sobre el fixture
—una corrida que termina con *«El expediente NO cierra»* porque quedan criterios sin valor— el
HTML generado **sí trae** el bloque de alcance, con su encabezado «Alcance declarado de la
corrida» y el conteo «Etapas diferidas al expediente: **8**». Es decir: **el bloque imprime
con el expediente abierto**, que es exactamente la condición en la que la declaración tiene que
verse y en la que una acotación no se vería.

**Comprobación que C5 debe dejar en verde** (criterio de aceptación #6 de §11): repetir esa
misma corrida y comprobar que la cadena «no evalúa ese requisito» aparece en el HTML **antes**
de que ningún criterio nuevo tenga valor. Si sólo aparece con los criterios declarados, el
vehículo elegido está mal y hay que volver a esta sección.

### 15.7 (b) Los `Fundamento` que C3, C4 y C5 necesitan

**Regla que gobierna los ocho, y es T11:** `Registro.problemas_de_integridad` exige que
**al menos una** de las citas de un `Fundamento` tenga un `caracter` compatible con su
`verbo` (`VERBO_COMPATIBLE_CON`; verificado en `registro.py`: la condición es
`any(...)`, no `all(...)`, precisamente para que V2 pueda colgar de su exigencia y de su
recomendación a la vez). Por eso **cada bloque de abajo lleva el carácter de cada cita
anotado**: es lo que hay que comprobar antes de escribirlo, no después.

**Seis citas no existen todavía.** Van marcadas `⛔ POR TRANSCRIBIR (C2)` y **ningún
fundamento que dependa de ellas se puede construir hasta que C2 las transcriba y
`test_normativa_pdf.py` las verifique** — cuáles quedan bloqueados y cuáles no está medido más
abajo. Sus páginas están en §15.3 y §15.4:

| Id propuesto | Qué transcribe | Impresa / PDF | `caracter` |
|---|---|---|---|
| `MC_HHD.4.1.1.3.4a#TIPOS` | *«Los tipos de alcantarillas comúnmente utilizadas … son; marco de concreto, …»* | 71 / 74 | `DEFINICION` |
| `MC_HHD.4.1.1.3.4a#MARCO` | *«Las alcantarillas tipo marco de concreto de sección rectangular o cuadrada pueden ubicarse… Generalmente, se recomienda emplear este tipo… suelos de fundación de mala calidad.»* | 72 / 75 | **dos citas**: `PERMISO` la 1.ª oración, `RECOMENDACION` la 2.ª |
| `MC_HHD.4.1.1.3.4a#MULTIPLES` | *«…recomendándose utilizar obras con mayor sección transversal libre, sin subdivisiones.»* | 72 / 75 | `RECOMENDACION` |
| `MC_HHD.4.1.1.3.7d` | *«Las dimensiones de las alcantarillas deben permitir efectuar trabajos de mantenimiento y limpieza en su interior de manera factible.»* | 80 / 83 | `EXIGENCIA` |
| `MC_HHD.LAMINA_03` | rótulo de la 3.ª figura, `metodo=IMAGEN` | 209 / 212 | `DEFINICION` |
| `HDS5_3ED.A.3#FORMAS` | *«coefficients for rectangular (box) shapes should not be used for nonrectangular … shapes and vice-versa»* | A.3 | `EXIGENCIA` |

**Comprobación ejecutada de los ocho, contra el registro construido** (no a ojo): los **ocho ids
están libres** —ninguno colisiona con los diecisiete de `fundamentos.py`— y las seis citas que
§15.7 da por **existentes** existen con el `caracter` que se les atribuye: `HDS5_3ED.A.2`
`definicion`, `HDS5_3ED.TA.1` `definicion`, `HDS5_3ED.3.3.3#HO` **`aproximacion`** (que
`VERBO_COMPATIBLE_CON` admite para `DEFINE`, junto con `definicion`), `MC_HHD.4.1.1.3.6`
`definicion`, `MC_HHD.4.1.1.3.6#T09` `definicion` y `MC_HHD.4.1.1.3.4a` `exigencia`.

**Y el reparto de dependencias, que es lo que ordena a C2 y C5:** cinco de los ocho
—`F4.FORMA_HDS5`, `F4.SECCION`, `F4.YC_RECT`, `F3.SECCION_CANAL` y `F4.N_CAJON`— **ya se pueden
construir hoy**, porque al menos una cita existente sostiene su verbo. Los otros **tres**
—`F3.TIPO_MARCO`, `F3.MANTENIMIENTO` y `F3.CELDAS`— tienen **todas** sus citas por transcribir y
**están completamente bloqueados por C2**. Son justamente los tres que sostienen el tipo de
estructura, el mínimo de mantenimiento y el número de celdas: **C2 no es opcional antes de C5.**

---

#### Para C3 — HDS-5 Forma 2

```python
FORMA_HDS5 = _fundamento(
    id="F4.FORMA_HDS5",
    fase=F4,
    que_paso=("Forma de la ecuacion de control de entrada del HDS-5 que "
              "aplica a esta seccion, y por que"),
    por_que=(
        "El HDS-5 no tiene UNA ecuacion de control de entrada no sumergido: "
        "tiene DOS formas, y cual se usa no lo elige el proyectista, lo fija "
        "la carta de la Tabla A.1 a la que pertenece la seccion. La Forma 1 "
        "arranca del tirante critico y corrige por pendiente; la Forma 2 es "
        "un ajuste directo sobre el caudal adimensional y NO lleva el termino "
        "Ks*S. La diferencia no es de precision: son dos regresiones "
        "distintas sobre dos conjuntos de ensayos, y sus constantes K y M "
        "estan ajustadas cada una a SU forma. Por eso la memoria imprime que "
        "forma se uso: un lector que vea K y M sin saber en que ecuacion "
        "entraron no puede rehacer el numero."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.A.2",          # DEFINICION -> sostiene DEFINE
           "HDS5_3ED.TA.1",         # DEFINICION
           "HDS5_3ED.A.3#FORMAS"),  # EXIGENCIA  # ⛔ POR TRANSCRIBIR (C2)
    que_pasa_si_no_se_hace=(
        "Es el error que la sesion C3 existe para evitar: copiar la Forma 1 y "
        "cambiarle las constantes. El termino Ks*S sobreviviria en una "
        "ecuacion que no lo tiene, y con Ks = -0.5 RESTA carga: el HW saldria "
        "menor que el real y V4, V4b y el tamizado de 7.A se evaluarian del "
        "lado no conservador, sin que nada avise -- exactamente la forma de "
        "MAT-D10, pero por una via que ninguna guardia de signo detecta, "
        "porque el resultado sigue siendo positivo."),
)
```

> **Cuidado con el `verbo` aquí.** Es `DEFINE` y no `OBLIGA` aunque la cita `#FORMAS` sea una
> exigencia: lo que el paso hace es **elegir una ecuación**, y el HDS-5 la **define**. La
> exigencia (`no cruzar coeficientes entre formas`) es la **restricción** sobre esa elección,
> no el motivo del paso. Escribir `OBLIGA` pasaría T11 y diría algo falso.

---

#### Para C4 — `SeccionRectangular`

```python
SECCION = _fundamento(
    id="F4.SECCION",
    fase=F4,
    que_paso=("Area, perimetro mojado y radio hidraulico de la seccion, para "
              "el tirante de trabajo"),
    por_que=(
        "El num. 4.1.1.3.6 prescribe Manning y define sus variables -- A "
        "'area de la seccion hidraulica', P 'perimetro mojado', R = A/P -- "
        "pero NO dice como se calcula A ni como se calcula P: eso depende de "
        "la forma, y el Manual no fija ninguna. Ahi es donde entra la "
        "seccion como abstraccion: no es una generalizacion que el proyecto "
        "se inventa para que le quepan dos formas, es el hueco que el propio "
        "numeral deja al calculo. Un circulo lo llena por el angulo mojado y "
        "un rectangulo por B*y; el numeral es el mismo para los dos, y por "
        "eso el procedimiento tambien."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.6",),    # DEFINICION -> sostiene DEFINE
    que_pasa_si_no_se_hace=(
        "Se escribe un segundo motor de calculo para la otra forma. Es "
        "SIS-A-07 y es el antipatron numero uno de la §12: dos motores, uno "
        "con casos patron y otro sin ellos, que empiezan iguales y divergen "
        "en la primera correccion que solo se aplique a uno."),
)

YC_RECT = _fundamento(
    id="F4.YC_RECT",
    fase=F4,
    que_paso="Tirante critico de la seccion, y la energia critica H_c",
    por_que=(
        "El tirante critico no se calcula porque interese por si mismo: se "
        "calcula porque DOS pasos posteriores lo consumen. La Forma 1 del "
        "control de entrada arranca de H_c/D, y el control de salida necesita "
        "h_o = max(TW, (d_c + D)/2). En la seccion circular no hay solucion "
        "cerrada y hace falta un segundo Brent; en la rectangular el ancho "
        "superficial es constante y la condicion de energia minima se "
        "despeja: y_c = (q^2/g)^(1/3) con q = Q/B. Que sea exacta no es un "
        "lujo de elegancia -- retira la clase entera de fallos de "
        "convergencia que LimiteNumericoError cubre en la circular "
        "(SIS-G-02), donde un Q diminuto lleva el resolutor a un angulo "
        "donde el area se cancela."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.3.3.3#HO",     # sostiene DEFINE (definicion/aproximacion)
           "HDS5_3ED.A.2"),         # DEFINICION
    que_pasa_si_no_se_hace=(
        "El control de salida se queda sin h_o y la Forma 1 sin H_c: los dos "
        "pasos que producen el HW gobernante. Y si en vez de la solucion "
        "cerrada se reusa el Brent de la circular, se arrastra a la "
        "rectangular una fragilidad numerica que en ella NO existe."),
)
```

> **Qué NO lleva un `Fundamento` en C4, y es la mitad del trabajo.** `y_c = (q²/g)^(1/3)` es
> **álgebra**, no norma: sale de la condición de energía mínima, no de un numeral. El
> `Fundamento` funda **por qué el paso existe** (dos pasos posteriores lo consumen); la fórmula
> viaja en `PasoDeMemoria.formula` y su `formula_cita_id` apunta al numeral que **la exige**,
> no a uno que la imprima. Inventarle una cita a la fórmula sería la clase de defecto que
> `SIN_FUNDAMENTO` existe para no cometer.

---

#### Para C5 — catálogo, criterios y verificaciones del cajón

```python
TIPO_MARCO = _fundamento(
    id="F3.TIPO_MARCO",
    fase=F3,
    que_paso=("Tipo de estructura del cruce: alcantarilla tipo marco de "
              "concreto de seccion rectangular"),
    por_que=(
        "El marco de concreto no es una importacion ni una excepcion en este "
        "Manual: lo nombra el PRIMERO entre los tipos comunmente utilizados "
        "en carreteras del pais, cuenta la seccion rectangular y la cuadrada "
        "entre las 'mas usuales', PERMITE expresamente ubicarlo a la cota "
        "que se requiera -- que es justo lo que un cruce a nivel de canal "
        "necesita -- y RECOMIENDA emplearlo con suelos de fundacion de mala "
        "calidad. Ademas lo DIBUJA para este caso exacto: la Lamina N 03 "
        "trae una figura titulada 'ALCANTARILLA TIPO MARCO DE CONCRETO EN "
        "CRUCE DE CANAL DE RIEGO'. La asignacion del tipo a la Familia C la "
        "hace la Sec. 2.3 de la hoja de ruta; lo que estas citas aportan es "
        "que esa asignacion tiene respaldo en la fuente primaria y no solo "
        "en la hoja."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.4a#TIPOS",    # DEFINICION   ⛔ POR TRANSCRIBIR (C2)
           "MC_HHD.4.1.1.3.4a#MARCO",    # RECOMENDACION -> sostiene RECOMIENDA
           "MC_HHD.LAMINA_03"),          # DEFINICION   ⛔ POR TRANSCRIBIR (C2)
    que_pasa_si_no_se_hace=(
        "El tipo de estructura de la Familia C se apoya solo en la Sec. 2.3 "
        "de la hoja de ruta, que no es fuente primaria, y la memoria no "
        "puede citar ningun numeral para la decision que gobierna todo lo "
        "demas del punto."),
)

SECCION_CANAL = _fundamento(
    id="F3.SECCION_CANAL",
    fase=F3,
    que_paso=("Adopcion de la seccion del cajon en un cruce de canal de "
              "riego, fuera del piso de 0.90 m"),
    por_que=(
        "El piso de 0.90 m del num. 4.1.1.3.4 a) NO se aplica aqui, y no "
        "porque el proyecto decida saltarselo: el mismo numeral que lo fija "
        "lo EXCEPTUA, en la misma oracion, para los cruces de canales de "
        "riego, y ordena adoptar alli secciones 'de acuerdo a cada diseno "
        "particular'. La Familia C ES ese conjunto de cruces. Lo que el "
        "numeral hace no es liberar la seccion: la traslada del catalogo al "
        "diseno, y por eso la progresion B*H de este proyecto es una "
        "adopcion declarada y no una lectura de la norma."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.1.3.4a",),   # EXIGENCIA -> sostiene OBLIGA
    que_pasa_si_no_se_hace=(
        "Se hereda al cajon un piso que su propio numeral le levanta, o -- al "
        "reves -- se lee 'de acuerdo a cada diseno particular' como si fuera "
        "un valor. Las dos contradicen la fuente, por lados opuestos."),
)

MANTENIMIENTO = _fundamento(
    id="F3.MANTENIMIENTO",
    fase=F3,
    que_paso=("Cota inferior de la progresion de secciones: dimension "
              "interior que permite mantener y limpiar el conducto"),
    por_que=(
        "Levantado el piso de 0.90 m, la seccion del cajon NO queda sin cota "
        "inferior normativa. El num. 4.1.1.3.7 d) exige, sin distinguir "
        "forma alguna, que las dimensiones permitan efectuar el "
        "mantenimiento y la limpieza EN SU INTERIOR de manera factible. Es "
        "una exigencia SIN NUMERO: obliga a que exista un minimo y deja al "
        "proyecto decir cual. Esa es exactamente la forma de un vacio "
        "declarable -- la norma pide el requisito y no da la cifra --, y por "
        "eso 'secciones_cajon_normalizadas' es [A] con vacio verificado y no "
        "una eleccion libre."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.1.3.7d",),   # EXIGENCIA  ⛔ POR TRANSCRIBIR (C2)
    que_pasa_si_no_se_hace=(
        "La progresion de secciones del cajon se lee como una decision "
        "puramente economica o hidraulica, y el minimo se fija por el caudal. "
        "Es como se llega a un cruce que pasa el agua y no se puede limpiar, "
        "que es el mismo fallo que el piso de 0.90 m evita en las Familias A "
        "y B por otra via."),
)

N_CAJON = _fundamento(
    id="F4.N_CAJON",
    fase=F4,
    que_paso=("Coeficiente de rugosidad de Manning del cajon de concreto, "
              "por analogia declarada dentro del grupo A de la Tabla N 09"),
    por_que=(
        "La Tabla N 09 SI cubre al cajon por el titulo de su grupo -- 'A. "
        "CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO' --, que es "
        "el unico grupo de la tabla que describe una alcantarilla. Lo que no "
        "tiene es una FILA que nombre la seccion rectangular: seis de las "
        "siete filas de su item 'a. Concreto' estan enumeradas por 'tubo' y "
        "la septima, 'afinado', por el acabado. El vacio es de fila y no de "
        "grupo, y por eso la analogia se declara DENTRO del grupo que ya "
        "cubre la estructura -- entre filas separadas por un atributo que no "
        "es la forma -- y es mas estrecha que la de 'n_manning_hdpe', que "
        "cruza material. El rango se toma completo, minimo y maximo: la "
        "regla de doble n pide los dos extremos, porque n_max es "
        "conservador para capacidad y n_min para velocidad y socavacion."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.6",          # DEFINICION -> sostiene DEFINE
           "MC_HHD.4.1.1.3.6#T09"),     # DEFINICION
    que_pasa_si_no_se_hace=(
        "Se toma el n del concreto 'porque el cajon es de concreto', que es "
        "una analogia igual de real pero SIN DECLARAR: la memoria imprimiria "
        "un valor [N] apoyado en una fila cuyo rotulo dice 'tubo', y un "
        "revisor que abra la pag. impresa 75 no encontraria el cajon por "
        "ninguna parte."),
)

CELDAS = _fundamento(
    id="F3.CELDAS",
    fase=F3,
    que_paso="Numero de celdas del cajon: una sola, o multicelda",
    por_que=(
        "El Manual toma partido y hay que citarlo donde se decide: ante "
        "capacidad de arrastre del curso -- palizada, troncos, material de "
        "cauce -- RECOMIENDA usar obras con mayor seccion transversal libre, "
        "SIN SUBDIVISIONES, porque cada tabique es un punto donde la palizada "
        "se traba. La multicelda no esta prohibida; lo que el numeral hace es "
        "invertir la carga de la prueba: quien la adopte tiene que decir por "
        "que, y no al reves. Por eso el numero de celdas es un criterio "
        "declarado y no un supuesto del codigo."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.4a#MULTIPLES",),  # RECOMENDACION  ⛔ POR TRANSCRIBIR (C2)
    que_pasa_si_no_se_hace=(
        "V6 sigue siendo trivialmente verdadera porque MD no sabe hacer "
        "multibarril -- que es una propiedad del PROGRAMA, no del diseno --, "
        "y el dia que sepa, la verificacion se vuelve falsa en silencio. Es "
        "la trampa que la regla vinculante #10 anticipa."),
)
```

#### Lo que C5 **no** tiene que escribir, y conviene que quede dicho

**`F5.V1` no necesita ningún cambio para el marco, y ésa es la comprobación más útil de esta
sesión.** Su `por_que` ya está escrito en términos de **altura de la estructura**, no de
diámetro, y el numeral que lo sostiene enumera las tres magnitudes. **La única mejora es de
paráfrasis:** hoy dice *«El Manual lo escribe como el 25 % de la altura de la estructura»* y
el Manual escribe *«de la altura, diámetro o flecha»*. Es paráfrasis, no cita entrecomillada,
de modo que no viola la regla de la doble transcripción — pero elide justo las dos palabras
que hacen general al numeral. **Completar las tres es una línea, y C5 debería hacerlo.**

**`F5.V6` sigue en `SIN_FUNDAMENTO` y no sale de ahí.** Su razón censada —*«lo que el proyecto
ejecuta no es un cálculo: es una constatación declarativa sin magnitud ni umbral»*— **sigue
siendo cierta** después de C5: `n_celdas_cajon` no convierte a V6 en un cálculo, le da una
procedencia. Lo que C5 añade es `F3.CELDAS`, que funda **el paso que adopta el número de
celdas**, no la verificación. Confundirlos metería un `Fundamento` en un paso que no existe.

> **Defecto menor que se ve al hacer esto, y va a §15.8 (D-7):** la ficha de `F5.V6` en
> `SIN_FUNDAMENTO` remite al num. **4.1.1.3.7 a)**, que es el de la recomendación de TMC Ø48"
> en selva alta. La frase que sostiene lo que la fila V6 de la v8 realmente enuncia —«con
> palizada: sección única mayor»— está en el num. **4.1.1.3.4 a), pág. impresa 72 / PDF 75**,
> que es otro numeral y hoy **no está transcrito**.

### 15.8 (d) Defectos abiertos contra `docs/hoja_de_ruta_alcantarillas_v8.md`

**La v8 no se edita desde aquí** (§0). Se acumulan, con el símbolo del código donde cada
discrepancia se ve, para que quien la corrija sepa contra qué contrastarla. Ninguno de los
ocho duplica una `Discrepancia` ya registrada: las nueve `DIS-HR-*` de
`normativa/discrepancias.py` se revisaron una a una.

| Id | Dónde | Qué dice la v8 | Qué dice la fuente primaria | Dónde se ve en el código |
|---|---|---|---|---|
| **D-1** | **Sec. 3.1**, «Reglas duras **[N]**» · y **Sec. 3.2** | *«**Diámetro mínimo 0.90 m (36")** — num. 4.1.1.3.4 a), pág. 72»*, sin condición; y *«desde 0.90 m (mínimo normativo MTC)»* | La misma oración lo condiciona **dos veces**: *«En carreteras de alto volumen de tránsito…»* y *«**salvo en cruces de canales de riego**…»*. Impresa 72 / PDF 75 | `constantes_normativas.DIAMETRO_MIN_AMBITO` y las dos `CondicionAplicacion` de `MC_HHD.4.1.1.3.4a` ya llevan las dos condiciones. **La v8 no.** Un lector de la v8 aplicaría el piso a la Familia C |
| **D-2** | **Sec. 3.1**, bajo «Reglas duras **[N]**» | *«Suelo de fundación deficiente → orientar a marco de concreto»* | *«**Generalmente, se recomienda** emplear este tipo de alcantarillas cuando se tiene la presencia de suelos de fundación de mala calidad.»* — **recomendación atenuada**, impresa 72 / PDF 75. Y la fuente **no define «mala calidad»** | El párrafo **no está transcrito en el repositorio**: `MC_HHD.4.1.1.3.4a` sólo transcribe el del 0.90 m. Es `NOR-MEM-01` en su forma exacta: una regla dura escrita encima de un «se recomienda» |
| **D-3** | **Sec. 3.1** y **fila V6 de la Fase 5** | *«Con palizada: sección única mayor, no múltiple»* como regla dura, y la fila V6 con ancla **«[N]» y NINGÚN numeral** | *«…**recomendándose** utilizar obras con mayor sección transversal libre, sin subdivisiones.»* — **recomendación**, impresa 72 / PDF 75 | Un `[N]` sin numeral es lo que `CLAUDE.md` prohíbe de entrada. Y `fundamentos.SIN_FUNDAMENTO["F5.V6"]` remite al num. **4.1.1.3.7 a)**, que es la recomendación de TMC Ø48" en selva alta: **otro numeral** |
| **D-4** | **Sec. 3.4**, «Matriz de decisión de material» | *«Concreto reforzado · Vacíos normativos: **Ninguno.** n y velocidad máxima en Tablas Nº 09 y Nº 10…»* | Cierto para la sección **circular** y **falso para el marco**: la Tabla Nº 09 no tiene fila de sección rectangular (§15.3.2). La velocidad de la Tabla Nº 10 sí sirve, porque clasifica por revestimiento | El criterio nuevo `n_manning_cajon` **[N→]** es la prueba: si el concreto no tuviera vacíos, no haría falta |
| **D-5** | **Fase 4, §4.1**, tabla «Tabla Nº 09 — Manning» | Lista cuatro filas y ninguna nota sobre el ámbito de la tabla | El grupo que gobierna se titula *«A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO»* y **cubre al marco**; lo que falta es la **fila**. La v8 no distingue una cosa de la otra | `constantes_normativas.TABLA_09_GRUPO` ya declara que el grupo A es *«el único grupo de la tabla que describe una alcantarilla»*. La v8 no lo recoge |
| **D-6** | **todo el documento** | La **Lámina Nº 03 no se menciona ni una vez** en la v8, ni en su Fase 3, ni en su Fase 6, ni en su Anexo B | El Manual trae, impresa 209 / PDF 212, una figura titulada **«ALCANTARILLA TIPO MARCO DE CONCRETO EN CRUCE DE CANAL DE RIEGO»**: el respaldo gráfico normativo del tipo de estructura de la Familia C | Hoy no está citada **en ninguna parte del repositorio**. Ver §15.4 para la forma en que entra |
| **D-7** | **Sec. 2.3**, Familia C | Enuncia el requisito *«No puede alterar la rasante hidráulica ni el borde libre del canal»* **sin etiqueta, sin numeral y sin verificación asignada**, mientras que a la Familia A sí le da conjunto de aceptación (V1+V2+V4+V5) | El requisito no sale de ningún numeral del Manual: se apoyaría en la Ley 29338 y la DG-2018, **fuentes ausentes** del registro | `M1_clasificacion.PERFILES[Familia.C].verificaciones_aceptacion = None`, con el comentario *«Sec. 2.3 no declara conjunto propio»*. Es el hueco que §13 llama **VC1** y lo que obliga a la declaración de §15.6 |
| **D-8** | **Fila V7 de la Fase 5** | Enumera cuatro filas de la Tabla 2.4.5.3.1-2 —«Estructura rígida enterrada» 1.30/0.90, «Alcantarillas termoplásticas» 1.30/0.90, flexibles «Entre otros» 1.95/0.90 y «Muros y estribos de retención» 1.35/1.00— y **omite «Pórticos rígidos» (1.35/0.90)** | Es la fila que la regla vinculante **#8** asigna al cajón: la v8 desglosa la tabla por tipo de estructura y deja fuera precisamente el tipo de la Familia C | `constantes_normativas.TABLA_GAMMA_P_FILAS` **sí la tiene** (`EV_porticos_rigidos`, 1.35/0.90). El que no la contempla es el desglose de la v8 |

**Recordatorio, no defecto nuevo:** `DIS-HR-G-LAUSHEY` sigue en estado
`ABIERTA_CONTRA_HOJA_DE_RUTA` y esta sesión la **reconfirmó por segunda vía independiente**
(§15.3.4): el num. 4.1.1.3.7 c) define `g` sin número. **La v8 sigue mal ahí.**

#### Huecos del repositorio que esta sesión destapó (no son de la v8)

| Id | Símbolo | Qué falta | Quién lo cierra |
|---|---|---|---|
| **R-1** | `citas.MC_HHD_4_1_1_3_4a` | Transcribe **sólo** el párrafo del 0.90 m, con `caracter=EXIGENCIA`. Los párrafos de **PERMISO** y **RECOMENDACIÓN** que sostienen el tipo de la Familia C no están | **C2** — `#TIPOS`, `#MARCO`, `#MULTIPLES` (§15.7) |
| **R-2** | `citas` / `tablas` | **No existe cita del num. 4.1.1.3.7 d)**, que es la única exigencia sin número que acota la sección del cajón tras levantarse el piso de 0.90 m | **C2** — `MC_HHD.4.1.1.3.7d` |
| **R-3** | `constantes_normativas.TABLA_09_FILAS` | Transcribe cuatro filas del grupo A. **`afinado` no está**, y es la única fila del ítem sin forma en el rótulo: la candidata a la analogía del cajón | **C2**, y **C5** elige y declara cuál toma (§15.3.2) |
| **R-4** | `constantes_normativas.TABLA_09_FILAS` | Sus valores de A.2 son la lectura **corregida** del corrimiento y el bloque **no remite a `DIS-MCHHD-T09-A2-DESPLAZADA`**, que está declarada en `normativa/tablas.py`. Quien lea sólo `constantes_normativas` y vaya a la página encuentra otros tres números | **C2** — una línea de remisión; la discrepancia ya existe y **no hay que volver a demostrarla** |
| **R-5** | `fundamentos.SIN_FUNDAMENTO["F5.V6"]` | Remite al numeral equivocado (ver **D-3**) | **C5** |
| **R-6** | `variables_entrada._Columna.criterio_destino` | Es `Optional[str]`, un solo destino. Un segundo consumidor de `sucs_fundacion` obliga a decidir tupla o cambio de destino: **es cambio de esquema** | **C6**, no C5 (§15.5) |
| **R-7** | `normativa/discrepancias.py` | El cuerpo del Manual describe **mal su propia Lámina Nº 03**: dice *«se aprecia secciones típicas de alcantarillas tipo marco de concreto»* (impresa 73) y la **primera de sus tres figuras es tubería metálica corrugada** (impresa 209). Contradicción **interna de la fuente primaria**, no contra la v8 | **C2** — una `Discrepancia` de estado `ABIERTA`, para que un revisor que cuente las figuras no crea que la cita está mal puesta |
| **R-8** | `criterios_adoptados['factores_carga_aashto']` | Su comentario justifica la fila del tubo diciendo *«No es "Pórticos rígidos" … la Familia C, de marco o multicelda, sale sin candidatos»*: **describe un estado que C5 deja de ser cierto**. Falta además la clave del cajón | **C5** — junto con el epígrafe «Familia C queda sin candidatos» de `M2_material`, que tiene el mismo problema y ya está en el prompt de C5 |

### 15.9 Correcciones a ESTE documento

Las tres salen de la verificación y **se corrigen aquí porque §6 y §13 son vinculantes**: una
regla vinculante mal fundada se cita literal en una memoria y ahí ya es una cita falsa.

1. **Regla vinculante #6 de §6 — el porqué, no la conclusión.** Dice *«El subgrupo "a.
   Concreto" del grupo A trae solo filas de **tubo**»*. **Seis de sus siete filas dicen «tubo»;
   la séptima, `afinado`, no dice nada de forma.** La conclusión de la regla —no hay fila de
   cajón, y el n del marco es un vacío que se cubre con `[N→]`— **se sostiene entera**; lo que
   se sustituye es su justificación, por la reformulación de §15.3.2, que además es más
   fuerte: **el vacío es de fila, no de grupo.**
2. **§15 (encabezado anterior) y §10-CN punto 2 — «una de sus dos figuras».** La Lámina Nº 03
   trae **TRES** figuras (§15.4). La tercera es la del cruce de canal de riego y su título es
   exacto; la primera es de **tubería metálica corrugada**, que es lo que hace que el Manual se
   describa mal a sí mismo (**R-7**).
3. **§10-CN punto 4 y §13 — «el marco se dimensionará por V1/V4/V4b, que es el criterio de una
   alcantarilla de paso, NO el de un cruce de canal».** El fondo es correcto; la forma sugiere
   una **sustitución** de un conjunto por otro, y medido sobre `M1_clasificacion.PERFILES` **la
   Sec. 2.3 nunca le dio a la Familia C un conjunto de aceptación**. Lo que ocurre es que se
   corre la batería general sobre un punto cuyo **único requisito propio queda sin evaluar**.
   La declaración de §15.6.2 está redactada sobre esta lectura, no sobre la del prompt.

**Reglas que la verificación CONFIRMA sin matices, y conviene decirlo tan explícitamente como
las correcciones:** la **#1** (el cajón no hereda el piso de 0.90 m: la excepción es expresa y
está en la misma oración) y la **#7** (la Tabla Nº 10 clasifica por `TIPO DE REVESTIMIENTO`;
**no** se abre `v_max_cajon`).
