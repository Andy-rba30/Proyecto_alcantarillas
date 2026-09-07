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

## 2-bis. Censo de acoplamiento al diámetro (C0)

La tabla de §2 nombra cinco símbolos como muestra. Éste es el barrido de `src/`,
`cli.py` y `gui/`, y es **lo que C1 tiene delante**. Todo va anclado por **nombre de
símbolo**, nunca por línea — regla 4 de `CLAUDE.md`, y aquí importa el doble porque C1
mueve cientos de líneas.

> **SU ALCANCE REAL, declarado por C4, porque decía «completo» y no lo era.** Este censo
> cubre el acoplamiento al diámetro del **motor hidráulico** — M3, M4, `modelos`, MD, M5 y
> la capa de presentación —, que es lo que C1 tenía que refactorizar. **No cubre
> `M8_estructural`**, que codifica geometría circular en producción por dos símbolos
> nombrados y verificados contra el árbol:
>
> - `M8_estructural.empuje_flotacion_kn_m` — `GAMMA_AGUA_KN_M3 * (math.pi / 4) * D_exterior ** 2`, o sea el área del **círculo**;
> - `M8_estructural.peso_relleno_kn_m` — `gamma_relleno * D_exterior * altura_relleno`, un prisma de ancho `D_ext`.
>
> Los dos son de la Fase 8 y el frente que los abre es **F4** (§5), no C1 ni C4. Lo que
> corrige C4 es la palabra: **«completo» era falso**, y quien ejecute F4 no puede leer este
> censo como exhaustivo. La anotación venía de la auditoría de C1 (§16.4) y se confirmó
> midiendo de nuevo los dos símbolos en esta sesión.

**Cómo leer la columna (d).** Marca los símbolos que hoy tienen al menos un localizador
`archivo:línea` en `docs/manifiesto_citas.md`. **No son los que más acoplan: son los que
van a romper `tests/test_manifiesto_citas.py` en cuanto C1 mueva una línea**, aunque el
número no cambie. Las cifras y el procedimiento están en §16.3.

**Lo primero que hay que saber, y no estaba escrito:** de las veinte funciones de M3 y M4
que tocan el diámetro, **una sola emite la traza de memoria de toda la hidráulica** —
`M4_control._pasos_hidraulicos`, que construye los tres pasos `F4.MANNING`, `F4.CONTROL` y
`F4.HO`—. La obligación de C1 de que «el `PasoDeMemoria` siga imprimiendo lo mismo» se
concentra ahí, no está repartida.

### (a) Geometría del barril — lo que C1 abstrae detrás de `Seccion`

| (b) símbolo | (c) paso que emite | (d) manifiesto |
|---|---|---|
| `M3_hidraulica.area(D, theta)` | — | |
| `M3_hidraulica.perimetro(D, theta)` | — | |
| `M3_hidraulica.tirante(D, theta)` | — | |
| `M3_hidraulica.geometria(D, theta)` | — | |
| `M3_hidraulica._caudal_manning(D, theta, n, S)` | — | |
| `M3_hidraulica._validar_parametros(D, Q, S, n)` | — | |
| `M3_hidraulica.tirante_normal(D, Q, S, n)` | — | |
| `M3_hidraulica.resolver_manning(D, Q, S, material)` | — | |
| `M4_control.area_llena(D)` | — | |
| `M4_control.radio_hidraulico_lleno(D)` | — | |
| `M4_control._residuo_critico(D, theta, Q)` | — | |
| `M4_control.tirante_critico(Q, D)` | — | |
| `M4_control._geometria_de_referencia(Q, D)` | — | |
| `M4_control._validar_Q_D(Q, D)` | — | |
| `modelos.Geometria` | — | |
| `modelos.Geometria.y_sobre_D` | — | **conserva el nombre** (§4.1) |
| `modelos.Geometria.T` | — | |
| `modelos.TiranteNormal` | — | |
| `modelos.TiranteCritico` | — | |

### (b) Consumidores de la geometría

| (b) símbolo | (c) paso que emite | (d) manifiesto |
|---|---|---|
| `M4_control.caudal_adimensional(Q, D)` | — | |
| `M4_control._hw_sobre_D_no_sumergido(q*, H_c, D, S, hds5)` | — | **SÍ** |
| `M4_control._exigir_hw_no_negativo(HW/D, S, D, q*, hds5)` | — | |
| `M4_control.control_entrada(Q, D, S, hds5, critico)` | — | **SÍ** |
| `M4_control.control_salida(Q, D, S, L, TW, n, ke, critico)` | — | |
| `M4_control._pasos_hidraulicos(...)` | **`F4.MANNING`, `F4.CONTROL`, `F4.HO`** | |
| `M4_control.resolver_control(D, Q, S, L, TW, material, normal)` | — | |
| `modelos.ControlEntrada` · `ControlSalida` · `ResultadoHidraulico` | — | |
| `M5_verificaciones.v1_borde_libre(D, resultado)` | `F5.V1` | |
| `M5_verificaciones.v2_velocidad_minima(resultado)` | `F5.V2` | **SÍ** |
| `M5_verificaciones._paso_v3(...)` | `F5.V3` | |
| `M5_verificaciones.cota_clave(punto, material, D)` | — | |
| `M5_verificaciones.altura_relleno_sobre_clave(punto, material, D)` | — | |
| `M5_verificaciones.v4b_relacion_hw_d(D, resultado)` | — | |
| `M5_verificaciones.v7_flotacion(punto, material, D, resultado)` | `F5.V7` | |
| `M5_verificaciones.v9_disponibilidad_diametro(D, material)` | — | |
| `M5_verificaciones.verificar(punto, material, D, resultado)` | — | |
| `M2_material.espesor_pared(material, D)` | — | |
| `M2_material.diametro_exterior(material, D)` | — | |
| `M2_material.siguiente_diametro(material, D)` | — | |
| `M2_material.catalogo(material)` | — | |
| `M7_geometria.cobertura_minima_aashto(material, D)` | — | |
| `M7_geometria.altura_recubrimiento(material, D)` | — | **SÍ** |
| `M7_geometria.criterio_recubrimiento(material)` | — | |
| `M7_geometria.tamizado_rasante(punto, material, D_supuesto, HW)` | — | **SÍ** |
| `M7_geometria.compatibilidad_geometrica(punto, material, D, resultado, longitud)` | — | |
| `modelos.TamizadoRasante` · `CompatibilidadGeometrica` · `Material.D_max` | — | |
| `MD.disenar_material(...)` — el bucle «para cada D» | — | |
| `MD._motivo_sin_flujo_libre(D, Q, S, material)` | — | |
| `MD._motivo_incumplimiento(D, verificaciones)` | — | |
| `MD._motivo_escalon_fallido(D, exc)` | — | |

### (c) Presentación — no calcula, formatea

| (b) símbolo | (c) paso que emite | (d) manifiesto |
|---|---|---|
| `M11_reporte._pasos_hidraulicos_del_punto(informe)` | — | |
| `M11_reporte.memoria_de_punto(informe)` | — | |
| `M11_reporte.memoria_html(informe, ...)` | — | |
| `M11_reporte._tabla_diseno(...)` — consume `y_sobre_D` | — | **SÍ** |

### Constantes y criterios que SON un diámetro

`constantes_normativas.DIAMETRO_MIN` (0.90 m) · `DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO`
(1.22 m) · `D_PASO` (0.15) · `D_INICIO` (0.90) · y los criterios
`diametros_normalizados`, `D_max_catalogo`, `espesor_pared_conducto` y
`cobertura_minima_aashto`, los cuatro indexados por diámetro o por material.

### Dos símbolos que NO acoplan al diámetro y aun así rompen

`M4_control.perdida_carga(V, R, n, L, ke)` recibe **R ya calculado**, no `D`; y
`modelos.PuntoCritico` es la fila del CSV. **Ninguno de los dos toca el diámetro** — pero
los dos viven en archivos que C1 reescribe y los dos tienen localizador en el manifiesto.
Están aquí para que C1 no los busque como acoplamiento y no se sorprenda cuando el test del
manifiesto los señale.

**Las 54 filas nombran 59 símbolos, y los 59 se comprobaron uno a uno contra el árbol:
los 59 existen.** Ninguno es inventado; el censo se midió, no se recordó.

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
conserva el nombre y cambia de definición a `y / seccion.altura`: **no se renombra**.

> **Corregido en C1 contra lo medido, porque el argumento estaba inflado y C4 y C8 lo van
> a citar.** Esta línea decía que `y_sobre_D` «lo consumen V1, `M11._tabla_diseno` y las
> dos plantillas HTML». De las tres, **la única exacta es la del medio**, y ni siquiera
> sobre esta propiedad:
>
> - **Las dos plantillas: 0 apariciones.** Medido sobre `src/plantillas/memoria_perfil.html`
>   y `src/plantillas/memoria_alcantarillas.html` — la cadena `y_sobre_D` no está en
>   ninguna de las dos.
> - **V1 no consume la propiedad: la recalcula.** `M5_verificaciones.v1_borde_libre`
>   escribe `y_sobre_D = resultado.y_normal / D` por su cuenta.
> - **`M11._tabla_diseno` y el CSV de resumen sí leen el número, pero de
>   `ResultadoPunto.y_sobre_D`**, que es una tercera expresión (`y_normal / self.D`), no
>   la de `Geometria`.
>
> Los consumidores reales de `Geometria.y_sobre_D` son **los tests del motor**
> (`test_modelos`, `test_M3_hidraulica`, `test_M5_verificaciones`).
>
> **La conclusión no cambia: no se renombra.** Se sostiene sobre dos hechos, y son
> suficientes — es el nombre bajo el que el número viaja al entregable
> (`M11_reporte.COLUMNAS_RESUMEN_CSV` lo lleva como columna `y_sobre_D`) y es el nombre
> que la suite pinea. Lo que se retira es el argumento de las plantillas, que era falso.
> Y queda anotado que **el mismo número está escrito tres veces** —`Geometria.y_sobre_D`,
> `ResultadoPunto.y_sobre_D` y el cálculo interno de V1—; unificarlas no es de C1 ni de
> C4, pero quien las toque tiene que saber que son tres.

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
Familia A. Todo lo que este plan añada tiene que aparecer por **los mismos siete vehículos
que el proyecto ya usa**, sin inventar uno nuevo:

| Qué se declara | Vehículo | Qué exige del código nuevo |
|---|---|---|
| **El procedimiento**, paso a paso | `PasoDeMemoria` emitido por la función de cálculo, impreso por `M11.bloque_paso` | qué, **por qué** (de un `Fundamento` de `normativa/fundamentos.py`, con `verbo` sostenido por el `caracter` de alguna de sus citas), fórmula con `cita_id`, sustitución con **procedencia de cada valor**, umbral con su **carácter en la fuente**, veredicto con margen |
| **Cada valor elegido** | `M11.bloque_criterios` (marcador `bloque_criterios`) | cada criterio nuevo con etiqueta, concepto, fuente, sensibilidad y `resolucion`; el valor **efectivo**, con marca si se declaró en caliente |
| **Lo adoptado donde la norma calla** | `M11.bloque_acotaciones` (marcador `bloque_acotaciones`) | el criterio nuevo debe llevar `vacio_verificado`, o **no aparece en este bloque**: `acotaciones_declaradas()` lo lee del catálogo, no de la plantilla. Y además **tener valor**: el filtro exige `valor is not None`, así que un criterio vacío no aparece aquí por mucho `vacio_verificado` que lleve |
| **El carácter de cada umbral** | `M11.bloque_umbrales` (marcador `bloque_umbrales`) | si el numeral *recomienda* y el proyecto lo aplica como umbral duro, tiene que decirlo — es lo que ya hacen V1 y V2 |
| **Lo que falta y a quién** | `M11.bloque_pendientes` + `criterios_bloqueantes` | cada vacío nuevo con concepto, fuente, qué lo resuelve, qué bloquea y en qué puntos |
| **Lo que la fuente dice / lee / hace** | tres clases CSS separadas: `fuente`, `interpretacion`, y lo que el proyecto hace | pegar las tres es `NOR-HID-04` |
| **Lo que el proyecto hace más estrecho que la norma** (la norma habla, y el proyecto cubre solo parte) | `M11.bloque_alcance` (marcador `bloque_alcance`, imprime con el expediente abierto) + `PasoDeMemoria.nota_del_proyecto` en el punto | el campo `nota_del_proyecto` se imprime bajo «Lo que pone el proyecto» con clase CSS `interpretacion`. **No es acotación**: acotaciones es «lo adoptado donde la norma calla», y aquí la norma habla. Y **no es `Cita.interpretacion`**, que existe como campo pero **no tiene impresor** en la memoria: su único consumidor en `M11_reporte` es `_interpretacion_tabla_10()`, cableado a `MC_HHD.T10` |

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

Estas doce sustituyen al criterio de quien ejecute la sesión. Si tu solución contradice
una, párate y explica por qué antes de seguir. (Eran diez cuando se escribió esta línea:
CP añadió la **#11** y C1 la **#12**, y el número de arriba se corrige con cada alta —
un encabezado que dice «diez» sobre doce reglas es la misma clase de símbolo colgado que
`CLAUDE.md` denuncia en su cláusula de taxonomía.)

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

**#5 — No se cruzan coeficientes entre GEOMETRÍAS. Y eso NO es lo mismo que «entre
formas de ecuación»: son dos ejes distintos y esta regla los confundía.**

Lo que el num. A.3 prohíbe, literal: *«coefficients for rectangular (box) shapes should not
be used for nonrectangular (circular, arch, pipe-arch, etc.) shapes and vice-versa»*. Habla
de **formas geométricas** —cajón frente a no-cajón—, y en esa lectura la regla es
vinculante y directa para la Familia C: **el cajón usa una carta de cajón**, no la circular
de concreto con otras constantes.

**Lo que el num. A.3 NO dice, y esta regla llegó a decir: no prohíbe nada sobre las dos
FORMAS DE ECUACIÓN** (la (A.1) y la (A.2) del num. A.2.1). Cuál de las dos aplica lo decide
la **columna «Equation Form» de la Tabla A.1, fila por fila**, y nada más.

**La prueba de que son ejes ortogonales está en la propia Tabla A.1**, medida sobre sus 36
filas en C3:

| `Shape and Material` | Formas en que aparece |
|---|---|
| **`Rect. Box Concrete`** | **1 y 2** — Carta 8 es Forma 1; Cartas 9 a 11 son Forma 2 |
| **`Circular`** | **1 y 2** — Carta 3 es Forma 1; Carta 55 es Forma 2 |
| `Circular Concrete`, `Circular CM` | 1 |
| `Rect. Box 3/4" chamf. Conc.`, `Rect. Box Top Bev. Conc.`, `Rectangular Concrete`, `Ellipital Face` | 2 |

La misma geometría vive en las dos formas, y la misma forma cubre geometrías distintas. Una
prohibición sobre geometrías **no puede** ser la regla que separa las formas.

> **Por qué se corrige aquí y no en una nota al pie.** La enunciación vieja la escribió esta
> hoja, la repitió el comentario de la cita `HDS5_3ED.A.3#FORMAS` en `normativa/citas.py`, y
> C3 la copió a tres sitios de código creyendo que verificaba —incluido un docstring que
> declaró «releído entero»—. Es una cita que **dice algo que la fuente no dice**, propagada
> por cuatro archivos: exactamente lo que `NOR-PUE-01` dejó por escrito sobre el numeral que
> vivía en seis sitios como seis cadenas independientes. C4 y C5 citan esta regla.

**#6 — La Tabla Nº 09 NO tiene fila de cajón, y el vacío es DE FILA, NO DE GRUPO.** El
grupo «A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO» ya cubre al marco por su
propio título: un cajón es un conducto cerrado. Lo que falta es la fila. De las siete
subfilas de «a. Concreto», seis dicen «tubo» y la séptima —`afinado`— no dice nada de
forma. **Esto hace la analogía más estrecha que la del HDPE**, que sí estaba fuera de la
tabla entera: aquí el conducto está dentro del grupo y solo falta su acabado. El n de
Manning del marco se cubre con un criterio `[N→]` cuya justificación tiene que declarar
las dos cosas — que el grupo aplica y que la fila no existe — y no puede copiar el
argumento de `n_manning_hdpe` tal cual.

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

**#11 — `ke_entrada` = 0.5 es de TUBO, y para el cajón el número puede coincidir pero la
cita no.** Su campo `fuente` lo ata explícitamente al bloque «Pipe, Concrete» de la Tabla
C.2, fila «Square-edge» **sangrada bajo el rótulo de agrupación «Headwall or headwall and
wingwalls»** — el propio criterio documenta que la fila suelta, sin su encabezado, pierde
la condición. El bloque «Box, Reinforced Concrete» tiene once filas propias, con cuatro
rótulos de aletas y siete valores.

**Y aquí está la trampa, que es peor que un valor equivocado.** Para la embocadura que el
proyecto adopta —cabezal a ras, sin aletas (Sec. 9.1 de la v8: «tubo a ras del muro (*square edge*)»)—
la fila del cajón es «Headwall parallel to embankment (no wingwalls) → Square-edged on 3
edges» y vale **0.5 también**. El número coincide; **lo que no coincide es la procedencia**,
porque `resolucion` apunta a `fila_id='concreto_headwall_square_edge'`, del bloque de tubo.
Es exactamente el precedente `NOR-HID-01`: *el número es defendible y la cita no lo era*.
**Y la coincidencia hace el defecto PEOR, no menor:** un valor que acierta por casualidad
no falla nunca de forma ruidosa, de modo que nadie lo comprueba, **mientras la cita sigue
siendo falsa**. Quien lea esta regla sin leer §15 tiene que salir sabiendo esto.

**Lo que lo hace peligroso es que no se detiene.** El criterio tiene `valor=0.5`,
`etiqueta="C"`, `nivel=NIVEL_PERFIL` y **`sensibilidad=None`**: con un cajón corre el
control de salida sin bloqueo, sin ventana y sin nada que lo señale en la memoria. Y en
cuanto `embocadura_cajon` declare **aletas** —que es lo que la Lámina Nº 03 dibuja— el
valor deja de coincidir: 0.4 con aletas a 30°–75°, 0.5 a 10°–25° y **0.7 con aletas
paralelas**. Con 0.5 → 0.7 y **V = 3 m/s**, `H` sube `0.2·V²/2g` = **0.092 m** de carga
que el cálculo no vería, contra V4 y contra el tamizado de 7.A.

**Y arrastra una premisa muerta.** `T_HDS5_C2.alcance` está `Acotada` con la razón «el
catálogo de conductos de la Sec. 3.2 **no ofrece sección cajón**» — exactamente la premisa
que C5 destruye. Un `Acotada` que describe un alcance que ya no es el suyo es el
antipatrón de §12.

C5 tiene que abrir `ke_entrada` por forma, emparejado con la fila que `embocadura_cajon`
declare. Las dos decisiones se mueven juntas con la embocadura de Sec. 9.1, igual que ya
lo hacen la carta de HDS-5 y el detalle del cabezal.

> **Dos cifras de esta regla las corrigió CP contra la fuente, y conviene saber cuáles.**
> El parche v2 escribía «once filas propias, **de 0.4 a 0.7** según aletas y borde»: leído
> sobre la pág. impresa C.6 (PDF 216), los siete valores del bloque van de **0.2 a 0.7**
> —0.4–0.7 es el rango de las variantes *square-edged at crown* solamente—. Y escribía los
> 0.09 m sin la velocidad: `0.2·V²/2g` no es un número hasta que se dice **V = 3 m/s**.
> Un umbral sin su condición es lo que esta misma regla denuncia.

**#12 — `Seccion` tiene DOS parametrizaciones y NO son intercambiables. La canónica es la
del parámetro propio.** La añadió C1 y la va a pisar C4.

`Seccion` expone la geometría por dos vías:

| Vía | Miembros | Estado |
|---|---|---|
| **Por parámetro propio — CANÓNICA** | `bracket_llenado()`, `geometria_en(llenado)`, `ancho_superficial_en_llenado(llenado)` | La que consumen M3 y M4. Es la que resuelve Brent |
| **Por tirante — de lectura** | `area(y)`, `perimetro(y)`, `ancho_superficial(y)` | **Cero consumidores en producción.** Es el vocabulario de la Sec. 4.1 |

**Por qué la canónica es la del parámetro propio, y no la del tirante** —que es la que
«se lee mejor» y por eso es la trampa—:

1. **Es la que conserva los números.** En la circular el parámetro propio es θ y Brent
   resuelve sobre θ. Pasar el solver al tirante mueve la raíz en los últimos bits y con
   ella todo lo que cuelga de ella: es un cambio de método numérico, no un refactor.
2. **`geometria_en()` devuelve A, P, R e y calculados de una vez y mutuamente
   consistentes.** La vía por tirante entrega piezas sueltas, y cada pieza vuelve a
   derivar θ desde y por su cuenta: tres viajes de ida y vuelta por una inversa mal
   condicionada donde antes había uno solo, directo.
3. **No es una vía «circular».** En la rectangular el parámetro propio **es** el tirante,
   de modo que `geometria_en(y)` es directa y las dos vías coinciden exactamente. Elegir
   la canónica no le cuesta nada al marco.

**La medición que lo sostiene, hecha en C1 y con su grilla declarada.** En la circular,
`area(y)` / `perimetro(y)` / `ancho_superficial(y)` pasan por `theta_desde_tirante(y)`,
que es la inversa **algebraica** de `_tirante_en_theta` pero **no** su inversa en punto
flotante. El error del viaje de ida y vuelta **no está acotado por una constante**: es un
problema de **condicionamiento** que se concentra en los dos extremos del llenado.

| Dónde | Divergencia relativa máxima entre las dos vías |
|---|---|
| `y/D` ∈ [0.10, 0.75] — la ventana de diseño, la que V1 admite | **A 9.7e-16 · P 3.9e-16 · T 4.0e-16** (últimos bits) |
| `y/D` ∈ [0.05, 0.95] | A 1.2e-15 · P 4.6e-16 · T 1.9e-15 |
| `y/D` ∈ [0.01, 0.99] | A 5.2e-15 · P 1.5e-15 · T 8.8e-15 |
| θ = 1e-5 rad (`y/D` ≈ 6e-12) | **P y T: 4.1e-8** |
| θ = 1e-6 rad | **P y T: 4.4e-5** |
| **Extremo INFERIOR de `bracket_llenado()`** (θ = 1e-9) | **100 %: la vía por tirante devuelve `0.0` exacto para P y para T** (canónica: 4.5e-10) |
| **Extremo SUPERIOR** (θ = 2π − 1e-9) | **T: ~100 % relativo pero NO cero exacto** — 1.1021821192326179e-16 frente a 4.500001474513789e-10. **P: 1.6e-10 relativo**, no se anula |

> **La última fila la corrigió C4, y la enunciación vieja decía de más.** Esta tabla
> decía «en los **dos** extremos … devuelve `0.0` exacto para P y para T», y medido
> sobre D = 0.90 eso vale **entero en uno solo**: en el inferior, donde `y ≈ 0` y
> `theta_desde_tirante` devuelve 0 exacto. En el superior `y = D` exactamente, la
> inversa devuelve 2π y **el perímetro coincide en los últimos bits** (2.8274333877808138
> frente a 2.827433388230814); sólo `T` cae siete órdenes, y tampoco a cero.
>
> **La consecuencia no cambia ni un ápice** —el cero exacto está en el extremo
> **inferior**, que es de los primeros puntos donde Brent evalúa, y `T` es el
> denominador de `A³/T`—, pero el enunciado sí, y se corrige por la misma razón por la
> que se corrigió la #5 en C3.5: una regla vinculante que dice de más se deja de creer
> entera, y ésta la citan C4 y C5. La medición está fijada en
> `tests/test_seccion_rectangular.py::test_que_coincidan_en_el_marco_no_las_hace_intercambiables`
> y en el docstring de `modelos.Seccion`.

Grilla: 8 diámetros de 0.30 a 3.00 m; las filas de rango, sobre 20 000 ángulos repartidos
en `bracket_llenado()` (73 896 a 139 592 puntos según la ventana); las tres últimas, sobre
el punto exacto. **La cota depende de la grilla y por eso se da por tramos y no como un
número suelto**: una malla más fina encuentra siempre un punto peor cerca de los extremos.

**Lo que esto significa en la práctica, y es peor que una deriva.** El último renglón no
es un error pequeño: es la vía por tirante devolviendo **cero** donde la vía por θ devuelve
un positivo. Y `T` es exactamente el denominador de `A^3/T` en
`M4_control._residuo_critico`. Quien reescriba el residuo sobre `seccion.ancho_superficial(y)`
no introduce un 1e-12: **divide por cero en el extremo inferior del bracket**, que es de los
primeros puntos donde Brent evalúa — reintroduciendo la clase de fallo que `SIS-G-02`
cerró y que el propio módulo documenta haber esquivado.

**La regla, en dos líneas:**

- El valor que ya viene en un `Geometria` —`g.A`, `g.P`, `g.T`, `g.R`— **no se recalcula**.
  Sustituir `g.A` por `seccion.area(g.y)` es el error que esta regla existe para impedir.
- La vía por tirante solo puede usarse donde el llamador tenga **un tirante y ningún
  `Geometria`**, y nunca dentro de un solver ni cerca de los extremos del llenado.

En el centro del rango las dos vías **coinciden bit a bit** (θ = π: divergencia 0.0
exacta en A, P y T), de modo que **una comprobación puntual las aprueba**. Ése es el
motivo de que esto sea una regla vinculante y no un comentario: no se detecta mirando.

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

1. **El contenedor de sesión arranca sin dependencias.** CN tuvo que instalarlas para
   poder correr la suite. Deja resuelto, o instruye en el prompt, `numpy`, `scipy`,
   `pytest` y **`pymupdf`**. Sin PyMuPDF los 32 tests de `test_normativa_pdf.py` se
   saltan y las transcripciones de C2 pasarían sin verificar.
2. Guardar la salida de `python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance
   perfil` y el par `passed / skipped` leído de `origin/main`. Es la línea base contra la
   que C1 se mide con un diff.
3. **CN va primero.** Es la sesión que contesta qué numeral sostiene cada paso del
   procedimiento cuando la sección es un marco. Sin ella, C5 escribe criterios cuya
   justificación habría que rehacer.
4. **La configuración de referencia de este plan es «PyMuPDF sí / ventana Tk no»**, que
   da `1536 passed / 2 skipped` (collected 1538). Es la que midió CN. Cualquier sesión
   que reporte otro par tiene que decir con qué configuración corrió, no solo el número.

**Convención de commit:** `familiaC(Cn): resumen — símbolos tocados`. Una tarea no está
terminada hasta que su trabajo está en `origin/main`; el conteo de tests se lee de ahí.

---

## 9. Tabla maestra de sesiones

| Sesión | Trabajo | Frente | Modelo | Esfuerzo | Plan mode | Estado |
|---|---|---|---|---|---|---|
| **CN** | Procedimiento normativo del marco | F0 | Opus 5 *(corrida real; el plan proponía Fable 5.1)* | max | sí | **Cerrada** — `e2da067`, PR #2 |
| **C0** | Censo de acoplamiento y línea base | — | Sonnet 5 | high | no | |
| **C1** | Refactor de sección, sin cambiar ningún número | F1 | Opus 5 | **ultracode** | sí | |
| **C2** | Registro normativo del cajón (Tabla A.1 y C.2) | F2 | Opus 5 | **xhigh** | sí | |
| **C3** | HDS-5 Forma 2 en M4 | F1+F2 | Opus 5 | high | sí | |
| **C4** | `SeccionRectangular`: hidráulica del marco | F1 | Opus 5 | xhigh | sí | |
| **C5** | Catálogo, criterios y verificaciones del cajón | F3 | Opus 5 | xhigh | sí | |
| **C6** | Entradas: CSV, CLI, variables, dominios | F5 | Sonnet 5 | high | no | |
| **C7** | Camino a perfil: M7, M8 y V7 | F4 | Opus 5 | high | sí | |
| **C8** | Reporte, GUI, corrida completa y cierre | F5 | Opus 5 | ultracode | no | |

> **Nota de calibración, medida y no supuesta.** CN corrió con Opus 5 a `max` en lugar de
> Fable 5.1 a `high`, y salió bien: cuatro `verificador-normativo` en paralelo, cuatro
> autocorrecciones antes de cerrar y una refutación propia retirada (R-5). Para las
> sesiones de volumen (C2, C8) **no repitas `max`**: cuesta sin dar más que `xhigh`, que
> es lo que `ultracode` ya envía.

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
Lee CLAUDE.md y docs/ruta_familia_c.md (§2, §2-bis, §4.1, §4.5, §5-F1, §7 y §16.3).
§2-bis es el censo que C0 midió: los 59 símbolos que tocan el diámetro, con
cuáles emiten PasoDeMemoria y cuáles tienen localizador en el manifiesto.

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
       control_entrada, control_salida
   NO toques M3.area_trapecial / perimetro_trapecial / caudal_manning_trapecial /
   tirante_normal_trapecial ni SeccionReceptor: son del receptor, no del barril.
   Y NO toques M4.perdida_carga: figuraba en esta lista y NO recibe ningún
   diámetro — le llega la R ya calculada, como el censo de §2-bis ya había
   medido. No hay nada que migrar ahí. (Corregido en C1: la lista estaba
   desactualizada respecto del propio censo que C0 dejó.)

4. Los PasoDeMemoria que estas funciones emiten tienen que seguir imprimiendo lo
   MISMO: misma fórmula, misma cita, misma sustitución con la misma procedencia,
   mismo umbral con el mismo carácter. Si una sustitución nombraba "D" y ahora la
   magnitud viene de la sección, el rótulo impreso no cambia.
   ATAJO QUE C0 MIDIÓ: toda la traza hidráulica sale de UNA función,
   `M4_control._pasos_hidraulicos`, que construye los tres pasos F4.MANNING,
   F4.CONTROL y F4.HO. No está repartida por el módulo; comprobala ahí.

5. EL MANIFIESTO VA EN COMMIT APARTE DEL REFACTOR. `docs/manifiesto_citas.md`
   ancla por archivo:línea y vos vas a mover cientos de líneas: 12 localizadores
   viven en los tres archivos que reescribís y 23 más en los consumidores que
   arrastrás (§16.3). Regeneralo con
       python3 -m src.normativa.manifiesto --escribir
   y ponelo en su PROPIO commit, después del refactor.
   POR QUÉ, y no es orden por gusto: si van juntos, un rojo de
   test_manifiesto_citas.py NO SE PUEDE ATRIBUIR — puede ser el anclaje corrido
   o puede ser un número que se movió, y tu criterio de salida entero depende de
   poder separar esas dos cosas. CP lo topó con TRES ediciones de docstring:
   rompió cuatro tests y hubo que regenerar 12 localizadores.
   No arregles el anclaje por línea: es un defecto conocido del manifiesto y su
   corrección no es de esta sesión.

Criterio de salida, y es duro:
- tests/fixtures/casos_patron.py en verde SIN tocar un solo valor esperado
- el par passed/skipped idéntico al de C0
- `sh tests/linea_base_familia_c/regenerar.sh` y después
  `git diff --stat tests/linea_base_familia_c/` : VACÍO, los dos archivos.
  La línea base está NORMALIZADA — C0 le quitó los tres campos volátiles, uno de
  ellos un mtime que cambia por clon —, de modo que aquí no se admite "salvo
  marcas de tiempo": el diff es vacío o el refactor movió algo

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
   Dejá anotado en el reporte de la sesión que el consumidor de esta tabla es el
   criterio `ke_entrada`, que hoy tiene valor 0.5 tomado del bloque «Pipe,
   Concrete», y que C5 tendrá que abrirlo por forma (regla vinculante #11). NO lo
   toques en esta sesión: aquí solo se transcribe.

3. LAS SEIS CITAS DEL MANUAL MTC QUE §15.7 ENUMERA, Y QUE HOY NO EXISTEN. Sin
   ellas, TRES de los ocho Fundamento de §15.7 no se pueden construir y C5 se
   detiene: está medido en §15.7. Sus páginas están en §15.3 y §15.4.
   - `MC_HHD.4.1.1.3.4a#TIPOS` (impresa 71 / PDF 74), DEFINICION
   - `MC_HHD.4.1.1.3.4a#NIVELES` (impresa 72 / PDF 75), PERMISO
   - `MC_HHD.4.1.1.3.4a#MARCO` (impresa 72 / PDF 75), RECOMENDACION
     Ojo: son DOS citas y no una. El párrafo tiene dos caracteres —«pueden
     ubicarse» y «Generalmente, se recomienda»— y `Cita.caracter` es escalar.
   - `MC_HHD.4.1.1.3.4a#MULTIPLES` (impresa 72 / PDF 75), RECOMENDACION
   - `MC_HHD.4.1.1.3.7d` (impresa 80 / PDF 83), EXIGENCIA. Es la única exigencia
     sin número que acota la sección del cajón una vez levantado el piso de 0.90 m.
   - `MC_HHD.LAMINA_03` (impresa 209 / PDF 212), DEFINICION, `metodo=IMAGEN`.
     Es un plano: leerlo por extracción de texto es lo que MetodoDeVerificacion
     existe para obligar a declarar. Cuelga de ella una `AfirmacionNegativa`: la
     lámina NO acota ninguna dimensión —el único token numérico de la página es el
     folio y el número de lámina—, de modo que sostiene el TIPO y ninguna magnitud.
   Y una `Discrepancia` de estado ABIERTA: el cuerpo del Manual describe mal su
   propia Lámina Nº 03 —dice «secciones típicas de alcantarillas tipo marco de
   concreto» (impresa 73) y la primera de sus TRES figuras es tubería metálica
   corrugada—. Es contradicción interna de la fuente primaria, no contra la v8.

4. Tabla Nº 09, dos cosas que faltan y son de esta sesión:
   - transcribí la fila `afinado` del ítem «a. Concreto» del grupo A. Es la única
     del ítem cuyo rótulo no dice «tubo», y por eso es candidata a la analogía del
     cajón (regla #6). C5 elige y declara cuál toma; vos solo la ponés disponible.
   - `constantes_normativas.TABLA_09_FILAS` no remite a
     `DIS-MCHHD-T09-A2-DESPLAZADA`, que sí está declarada en `normativa/tablas.py`.
     Sus valores de A.2 son la lectura CORREGIDA del corrimiento, y quien lea solo
     `constantes_normativas` y abra la página encuentra otros tres números. Una
     línea de remisión; la discrepancia ya existe y NO hay que volver a demostrarla.

5. En modelos.ConstantesHDS5 añadí el campo `forma: int` (1 o 2) y actualizá
   `desde_dict`. Poné Forma 1 en las tres filas circulares existentes: es lo que
   hoy hacen, y así el cambio no mueve ningún número.

6. En constantes_normativas.HDS5_INLET añadí las filas del cajón con la misma
   convención de clave que las circulares ("cajon_concreto_<borde>"), DERIVADAS de
   la transcripción del punto 1, nunca escritas a mano. Es el mismo patrón que
   MANNING deriva de TABLA_09_FILAS.

7. Actualizá docs/manifiesto_citas.md y comprobá test_manifiesto_citas.py.

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
vinculantes #3, #4 y #12 de §6). La #12 es de C1 y es la que más caro sale
en esta sesión: leela antes de escribir la primera línea.

0. LA VÍA CANÓNICA ES LA DEL PARÁMETRO PROPIO, NO LA DEL TIRANTE (regla #12).
   `Seccion` expone la geometría por dos caminos y NO son intercambiables:
     - CANÓNICA, la que consumen M3 y M4 y sobre la que resuelve Brent:
       `bracket_llenado()`, `geometria_en(llenado)`,
       `ancho_superficial_en_llenado(llenado)`
     - DE LECTURA, hoy con CERO consumidores en producción:
       `area(y)`, `perimetro(y)`, `ancho_superficial(y)`
   `SeccionRectangular` implementa LAS DOS. Su parámetro propio ES el tirante,
   así que para el marco las dos coinciden exactamente y no hay nada que elegir.
   PRECISAMENTE POR ESO ES LA TRAMPA: vas a ver que en la rectangular
   `geometria_en(y)` y `area(y)` dan lo mismo, y la conclusión natural —
   "entonces M3 y M4 pueden llamar a la vía por tirante y queda más legible" —
   ES FALSA PARA LA CIRCULAR y mueve todos sus números. En la circular esa vía
   pasa por `theta_desde_tirante`, que está MAL CONDICIONADA en los extremos: en
   los dos extremos de `bracket_llenado()` devuelve 0.0 exacto para P y para T, y
   T es el denominador de A^3/T en `M4_control._residuo_critico`. No es una
   deriva de 1e-12: es una división por cero donde Brent evalúa primero.
   Lo que NO podés hacer en esta sesión, aunque parezca una simplificación:
     - reescribir M3 o M4 sobre `area(y)` / `perimetro(y)` / `ancho_superficial(y)`
     - recalcular con esos métodos un valor que un `Geometria` YA trae
       (`g.A`, `g.P`, `g.T`, `g.R`)
     - pasar el solver de la circular de theta al tirante
   Si creés que alguna de las tres hace falta, PARÁ y explicá por qué antes de
   tocarla: el criterio de salida de esta sesión incluye "todo lo circular
   intacto", y `sh tests/linea_base_familia_c/regenerar.sh` lo comprueba.

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

Criterio de salida: todo lo circular intacto —y eso se mide, no se declara:
`sh tests/linea_base_familia_c/regenerar.sh` tiene que dejar el diff VACÍO,
igual que en C1—; la rectangular con al menos un caso patrón por función
pública nueva; y `tests/test_memoria_sustentada.py` en verde sobre los pasos
nuevos.

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
   Y por lo mismo, en el MISMO barrido: el comentario de
   criterios_adoptados['factores_carga_aashto'] justifica la fila del tubo diciendo
   «No es "Pórticos rígidos" ... la Familia C, de marco o multicelda, sale sin
   candidatos». Esa premisa la destruye esta sesión. Reescribilo y añadí la clave
   del cajón; QUÉ fila le toca lo fija la regla vinculante #8 y lo aplica C7.

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
     OJO CON EL ANCLA DE V6: la fila V6 de la Fase 5 de la v8 lleva etiqueta «[N]»
     y NINGÚN numeral, y su enunciado —«con palizada: sección única mayor»— sale de
     una frase que RECOMIENDA («recomendándose utilizar obras con mayor sección
     transversal libre, sin subdivisiones», num. 4.1.1.3.4 a, impresa 72 / PDF 75).
     No escribas un Fundamento con verbo=OBLIGA sobre ella. El que corresponde es
     `F3.CELDAS` con verbo=RECOMIENDA, que funda el paso que ADOPTA el número de
     celdas; `F5.V6` se queda en SIN_FUNDAMENTO, porque V6 no es un cálculo. Está
     redactado en §15.7 y el defecto contra la v8 es D-3 de §15.8.

5. Implementá la declaración que CN redactó en §15 punto 4, por el vehículo que CN
   determinó: `bloque_alcance` más `PasoDeMemoria.nota_del_proyecto` en el punto.
   Lo que se declara: Sec. 2.3 NO le da a la Familia C un conjunto de
   verificaciones de aceptación —`PERFILES[Familia.C].verificaciones_aceptacion`
   es None, y el comentario del propio código lo dice—, de modo que a nivel de
   perfil el marco se acepta con V1/V4/V4b, que es el conjunto de una alcantarilla
   de paso. Eso LLENA UN HUECO, no sustituye a un criterio declarado, y el
   requisito de Sec. 2.3 que sí existe (no alterar la rasante hidráulica ni el
   borde libre del canal) queda diferido como VC1 (§13).
   Esto NO puede quedar en un docstring.

6. `ke_entrada` (regla vinculante #11). Hoy vale 0.5 con etiqueta [C],
   NIVEL_PERFIL y sensibilidad None, y su `fuente` lo ata al bloque «Pipe,
   Concrete» de la Tabla C.2, fila «Square-edge» bajo el rótulo de agrupación
   «Headwall or headwall and wingwalls». OJO: para el cabezal a ras sin aletas
   que adopta la Sec. 9.1 de la v8, la fila del cajón vale 0.5 TAMBIÉN — el número coincide y la
   PROCEDENCIA no, que es el precedente NOR-HID-01. Y en cuanto la embocadura
   declare aletas deja de coincidir (0.4 / 0.5 / 0.7 según el ángulo). Con un
   cajón NADA lo detiene: no hay bloqueo, no hay ventana, no hay marca en la
   memoria.
   Abrilo por forma: el ke del marco sale del bloque «Box, Reinforced Concrete»
   que C2 transcribió, emparejado con la fila que `embocadura_cajon` declare. Las
   dos decisiones se mueven juntas.
   Comprobá que el ke elegido sale en la memoria con SU FILA Y SU RÓTULO DE
   AGRUPACIÓN: el propio criterio ya documenta que la fila suelta pierde la
   condición.
   Y comprobá que `T_HDS5_C2.alcance` dejó de decir «el catálogo de Sec. 3.2 no
   ofrece sección cajón»: esa premisa la destruye esta misma sesión, y un
   `Acotada` que describe un alcance que ya no es el suyo es el antipatrón de §12.

7. Actualizá los tests que pinnean el contrato viejo, y decí en el reporte cuál
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

5. `sucs_fundacion` NO SE CABLEA EN ESTA SESIÓN, y este punto existe para que no
   la cablees. Vas a encontrarte una columna OBLIGATORIA que se carga, se valida y
   NO LA LEE NINGÚN MÓDULO, con `criterio_destino="c_phi_fundacion"`, que es de
   EXPEDIENTE. Es tentador conectarla, porque el num. 4.1.1.3.4 a) recomienda el
   marco «cuando se tiene la presencia de suelos de fundación de mala calidad» y
   la Sec. 3.1 de la v8 lo recoge. NO LO HAGAS, por tres razones medidas en §15.5:
   - LA NORMA NO DEFINE «MALA CALIDAD». No da umbral, ni lista de símbolos SUCS,
     ni CBR. El mapeo SUCS -> «mala calidad» habría que INVENTARLO, que es el peor
     error posible de este proyecto. Y la tabla de calidad por CBR del Manual de
     Suelos num. 4.5.4 NO sirve: clasifica la SUBRASANTE, no el suelo de
     FUNDACIÓN, y confundirlas es el género de NOR-PUE-01.
   - EL CARÁCTER NO SOPORTA UNA REGLA DURA. El párrafo es recomendación atenuada
     («Generalmente, se recomienda»). Autoriza a ORIENTAR, no a imponer ni a
     descartar. Un Fundamento con verbo=OBLIGA sobre él lo rechaza T11.
   - NO CAMBIARÍA NINGÚN RESULTADO. En la Familia C el tipo ya lo fija Sec. 2.3.
   Y NO ABRAS el criterio de mapeo «para declarar el vacío»: `Criterio(valor=None)`
   detiene el cálculo si alguien lo invoca, y si no lo invoca nadie entra en
   `criterios_sin_valor()` y la memoria y la GUI lo anuncian como vacío bloqueante
   que nadie tiene obligación de contestar. `opcional=True` tampoco vale: el
   catálogo lo define para el criterio que «refina un valor que la norma ya fija»,
   y aquí no hay valor normativo por defecto.
   LO QUE SÍ HACÉS: comprobar y REPORTAR que `variables_entrada._Columna.
   criterio_destino` es `Optional[str]` —un solo destino—, de modo que un segundo
   consumidor exige decidir si el campo pasa a tupla. Es CAMBIO DE ESQUEMA, toca
   `variables_entrada` y su test, y no se decide de paso: proponelo y pará.

6. Añadí al fixture tests/ejemplo_puntos.csv lo que haga falta para que C-01
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
6. El **hueco de aceptación de la Familia C** está declarado y visible: que Sec. 2.3 no
   le da conjunto propio, que a perfil se acepta con V1/V4/V4b, y que el requisito de
   Sec. 2.3 queda diferido como VC1. Por `bloque_alcance` + `nota_del_proyecto`, no
   implícito y no en un docstring.
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
- **No dejar `ke_entrada` en 0.5 cuando la sección es un cajón.** Tiene valor y no tiene
  sensibilidad: no se detiene solo. Regla #11.
- **No llamar «sustitución» al conjunto de aceptación de la Familia C.** Sec. 2.3 nunca
  declaró uno; V1/V4/V4b llena un hueco.

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

*Las cerró **C0**. Se escriben aquí para que las sesiones siguientes las LEAN en vez de
volver a decidirlas — y para que quien quiera reabrirlas tenga contra qué argumentar.*

### 14.1 El marco es VACIADO IN SITU, no prefabricado

**Decisión: vaciado in situ.** Y el argumento no es constructivo, es de trazabilidad.

**Lo que decide, medido sobre `normas/`:** el directorio tiene trece documentos, y **ninguno
es una norma de producto de cajón prefabricado**. No están AASHTO M 259 ni M 273, ni ASTM
C1433 ni C1577. Lo que sí está es **AASHTO LRFD 9.ª ed. (2020)**, que es una norma de
**diseño**, no de producto.

Elegir prefabricado sin su norma de producto obligaría a que **cada dimensión del cajón
—ancho, altura, espesores, clases por altura de relleno— fuera un `[A]` sin fuente
verificable**. Es exactamente lo que este proyecto persigue: `NOR-PRO-01` y `NOR-PRO-02`
retiraron ya la atribución de los topes de diámetro a AASHTO M170 y ASTM A760 *porque esas
normas tabulan otra cosa*. Repetirlo con un catálogo de cajón que ni siquiera está en
`normas/` sería el mismo defecto, cometido a sabiendas.

**Tres cosas más apuntan al mismo lado, y ninguna es opinión:**

1. La **Fase 8 de la v8** ya lo dice para este cruce: *«Para el **marco de concreto** del
   canal de 2.75 m no aplica la simplificación: diseño completo por AASHTO LRFD Sección
   5»*. Un elemento que se diseña por Sección 5 es un elemento **diseñado**, no elegido de
   un catálogo.
2. El **num. 4.1.1.3.4 a)** manda, en cruces de canal de riego, adoptar *«secciones de
   acuerdo a cada diseño particular»* (regla vinculante **#1**). Ése es el lenguaje de una
   estructura que se proyecta, no de un producto que se pide.
3. La **Lámina Nº 03** dibuja el marco en cruce de canal de riego con **todas sus cotas
   como `VARIABLE`** y ninguna dimensión numérica (§15.4). Un producto de catálogo no se
   dibuja así.

**Qué se sigue de la decisión, y es lo que las sesiones necesitan:**

- `secciones_cajon_normalizadas` es un **`[A]` honesto**: una progresión B×H **adoptada por
  el proyectista**, no una serie de catálogo. Su `sensibilidad` es la ventana de esa
  adopción y su `resolucion` no es `DeCatalogo`.
- **`espesor_pared_conducto` no aplica al marco**, y no hay que buscarle una fila: el
  espesor de un cajón vaciado in situ es **salida del diseño estructural**, no entrada. La
  Fase 8 lo produce, y `--alcance perfil` la difiere entera. `M2.espesor_pared` ya levanta
  `DatoFaltanteError` para un material sin fila (§15.2.2), que es el comportamiento
  correcto: pide un dato que hay que conseguir, no inventa uno.
- **`V9` no aplica al marco tal como está escrita.** Verifica `D ≤ D_max` contra un tope de
  catálogo, y un cajón vaciado in situ no tiene tope de catálogo. C5 la reescribe como
  disponibilidad de **sección**; lo que la acota no es un producto sino el propio diseño.

**Qué habría costado prefabricado, para que la decisión sea auditable.** Traer M 259 / M 273
o C1433 / C1577 a `normas/`, transcribir sus tablas de clases por altura de relleno con
verificación contra PDF —trabajo de **C2**, del mismo orden que la Tabla A.1 entera—, y
volver a abrir `espesor_pared_conducto` y `V9` por forma en **C5**. No se descarta por caro:
se descarta porque **hoy no hay fuente**, y sin fuente el trabajo no se puede hacer bien.

### 14.2 Una sola celda, `N = 1` por criterio declarado

**Decisión: `n_celdas_cajon` se declara y se fija en 1 para este alcance. La multicelda
queda diferida, no descartada.**

**Lo que lo decide es la propia fuente.** El num. 4.1.1.3.4 a), impresa 72 / PDF 75, ante
capacidad de arrastre del curso *«recomienda utilizar obras con mayor sección transversal
libre, **sin subdivisiones**»*. La Sec. 2.3 dice «marco o multicelda», de modo que **la
elección es del proyecto y la norma ya tomó partido sobre cuál prefiere**. Eso es
exactamente lo que `F3.CELDAS` funda, con `verbo=RECOMIENDA` (§15.7): la multicelda no está
prohibida, pero **quien la adopte tiene que decir por qué**, y no al revés.

**Y hay una razón de alcance que pesa igual.** La regla vinculante **#10** lo deja escrito:
mientras `N = 1` esté fijado **por criterio declarado**, `V6` sigue valiendo — pero *«hay
que decirlo en el criterio, no darlo por hecho»*. Hoy V6 es trivialmente verdadera **por una
propiedad del programa** (MD no sabe hacer multibarril), no por una decisión de diseño. Fijar
N = 1 en un criterio convierte esa casualidad en una declaración, que es lo que la regla #10
pide y lo que hace que V6 no se vuelva falsa en silencio el día que MD aprenda.

**Qué costaría abrir multicelda, sesión por sesión.** Se escribe aunque la decisión sea no
abrirla, porque una deuda sin precio no se puede planificar:

| Sesión | Trabajo adicional que añade la multicelda |
|---|---|
| **C4** | El reparto `Q/N` y su `PasoDeMemoria`: qué caudal entra en cada barril y por qué. La `Seccion` **no** cambia — regla **#3**: modela UNA celda, y el número de celdas vive fuera |
| **C5** | `n_celdas_cajon` deja de ser un valor fijo y pasa a ser una **elección con ventana**; y `V6` deja de ser una constancia y pasa a ser una **verificación real** contra la recomendación de sección única, con umbral y veredicto que hoy **no tienen método escrito** |
| **C7** | La separación entre barriles entra en la geometría. El num. 4.1.1.3.4 a) trae una regla de separación **escrita para tuberías** y **no dice nada del marco**: sería otro `[N→]` con analogía declarada, o un `[A]`. *C0 NO verificó sus valores y por eso no los transcribe aquí — es alcance de C2, con `verificador-normativo`* |
| **C8** | El reporte deja de tener «una sección adoptada» y pasa a tener N; `M11._tabla_diseno`, el CSV resumen y las dos plantillas cambian de forma |

**El precio de diferirla es bajo y el de abrirla no**: la regla #3 ya garantiza que el motor
hidráulico no cambia —se diseña **una celda** con `Q/N`—, de modo que abrirla más tarde no
invalida nada de C1 a C4. Es una decisión reversible, y por eso se difiere.

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
una TABLA cuyas FILAS están enumeradas por un objeto que el marco no es.** Son **cuatro** en
todo el procedimiento —CN escribió «tres» y la auditoría adversarial encontró la cuarta; ver
§15.10—:

- **Tabla Nº 09** (Manning): sus filas de concreto dicen «tubo». → `n_manning_cajon` **[N→]**.
- **Tabla A.1 del HDS-5** (control de entrada): sus cartas son por forma y material. → **hay
  cartas de cajón** (Cartas 8–12), de modo que **no es un vacío**: es una fila distinta de la
  misma tabla. **[C]**, la misma etiqueta que hoy. *Este dato no lo verificó CN —su fuente es
  `normas/hif12026.pdf`, no el Manual MTC—: se toma de la regla vinculante **#2** de §6, y
  **C3 lo re-verifica** contra las ecs. (A.1) y (A.2) antes de escribir la bifurcación.*
- **Tabla C.2 del HDS-5** (`k_e`, pérdida de entrada, control de salida): tiene una familia
  **«Box, Reinforced Concrete»** aparte de la de **«Pipe, Concrete»** de la que el proyecto toma
  hoy su 0.5. → como la Tabla A.1, **no es un vacío**: es otra familia de la misma tabla. **[C]**,
  pero con un valor y una elección nuevos. **Ésta es la que CN no vio** (§15.10, punto 1).
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
| **n de Manning del cajón** (criterio nuevo `n_manning_cajon`) | **Tabla Nº 09**, 75 / 78 — **grupo A**: *«A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO»* | **El grupo es neutro** («conducto cerrado»): el marco cae dentro. **Las FILAS de «a. Concreto» no**: seis de siete dicen «tubo» | **ANALOGÍA declarable, DENTRO del grupo que ya lo cubre** | **[N→]** — ver §15.3.2, que es el hallazgo que corrige la regla #6 |
| **Tirante crítico** (`M4.tirante_critico`) | *ninguno del Manual* — HDS-5 | — | **FUERA DEL MANUAL**; la solución cerrada rectangular es álgebra, no norma | **[C]** (como hoy) |
| **Control de entrada** (`M4.control_entrada`) | **HDS-5** num. A.2/A.2.1, Tabla A.1 (A.8) | Cartas **por forma y material**; hay cartas de cajón (regla #2 de §6, **no verificada por CN**: su fuente es `hif12026.pdf`) | **DIRECTO a otra fila de la misma tabla** — **no** es analogía | **[C]** |
| **Control de salida** (`M4.control_salida`, `F4.HO`) | **HDS-5** 3.1.4 y 3.3.3 · **Tabla C.2** (`k_e`), pág. impresa C.6 / PDF 216 | La fricción y `h_o` son neutros. **`k_e` NO lo es**: la Tabla C.2 lo tabula por **familia de conducto**, y el 0.5 del proyecto sale de la fila `Square-edge` del bloque **«Pipe, Concrete»** | **DIRECTO** salvo `k_e`, que **cambia de familia de tabla**: hay un bloque «Box, Reinforced Concrete» con once filas por configuración de aletas | **[C]**, y **`ke_entrada` deja de ser un valor fijo**: para el cajón depende de la embocadura, o sea queda acoplado a `embocadura_cajon` |
| **HW gobernante** (`M4.hw_gobernante`, `F4.CONTROL`) | **HDS-5** | Neutro | **DIRECTO** | **[C]** |

> **DOS pasos de la Fase 4 cambian, no uno, y el segundo lo encontró la auditoría (§15.10).**
> El **n de Manning** cambia de **etiqueta** —pasa a `[N→]`—; y **`ke_entrada` cambia de fila y de
> valor** sin cambiar de etiqueta, que es la forma más peligrosa de las dos porque nada se
> detiene: hoy vale `0.5` fijo, con `sensibilidad=None`, leído de `DeTabla(fila_id=
> "concreto_headwall_square_edge")` — una fila de **tubo**. En la familia «Box, Reinforced
> Concrete» de la misma Tabla C.2 el coeficiente va de **0.4 a 0.7** según las aletas, y el 0.7
> sube `H = (1 + k_e + 19.63·n²L/R^(4/3))·V²/2g` en `0.2·V²/2g`, o sea del orden de una décima de
> metro **menos** de HW que el real — contra V4 y contra el tamizado de 7.A. Todo lo demás de la
> Fase 4 conserva lo que ya tiene para el circular.
>
> **Y el repositorio ya lo había anticipado, con la premisa que este plan destruye.**
> `normativa/tablas.py::T_HDS5_C2.alcance` es `Acotada` con esta razón, literal: *«la tabla trae
> ademas la familia "Box, Reinforced Concrete" con sus once filas de aletas y bordes, y **el
> catalogo de conductos de la Sec. 3.2 no ofrece seccion cajon**: ninguna de esas filas puede
> aplicarse a un punto de este corredor»*. En cuanto C5 haga que M2 devuelva un candidato de
> marco, esa razón deja de ser cierta. Es exactamente el antipatrón que §12 enumera —**«No dejar
> un `Acotada` describiendo un alcance que ya no es el suyo»**— y **C5 tiene que ampliar la
> `Acotada` y transcribir las filas de cajón**, o el punto de Familia C tomará el `k_e` de un
> tubo sin que nada se detenga.

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

**Del Manual MTC, un solo paso de los 42 cambia de etiqueta**, y es el **n de Manning**. Ése es
el resultado de esta sesión y conviene decirlo así de crudo: **el procedimiento del Manual
peruano es casi enteramente neutro respecto de la forma de la sección**, y lo poco que no lo
es, no lo es por descuido sino porque copia sus filas de Ven Te Chow.

**Pero un segundo paso cambia de FILA sin cambiar de etiqueta, y CN no lo vio.** Es
`ke_entrada`, del control de salida, y su fuente no es el Manual MTC sino el HDS-5: la
auditoría adversarial lo encontró y está en §15.10, punto 1. Que la etiqueta no cambie es
justamente lo que lo hace peligroso — **nada se detiene** —, y la lección general es la que
conviene llevarse de esta sección: *no basta con preguntar qué numeral sostiene un paso; hay
que preguntar además si la TABLA de la que sale su valor enumera sus filas por algo que el
marco no es.* Con esa segunda pregunta, `ke_entrada` salta a la primera lectura.

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

> **POR QUÉ SON DOS IDS Y NO UNO, y es la corrección que la auditoría obligó (§15.10, punto 5).**
> `Cita.caracter` es un campo **escalar**: un id lleva un solo carácter. El párrafo de la pág.
> impresa 72 tiene **dos**, permiso y recomendación, en dos oraciones. Meterlos en un id obliga
> a elegir uno, y entonces la fila «Libertad de cota de emplazamiento — carácter PERMISO» de
> §15.2.2 quedaría apoyada sobre una cita cuyo carácter es RECOMENDACION: **el mismo defecto que
> el párrafo de abajo denuncia**, cometido dos páginas después de denunciarlo. Son dos ids, y
> `F3.TIPO_MARCO` cita los dos. Es la misma partición que el registro ya hizo con
> `MC_HHD.4.1.1.3.6#VMIN_INICIO` / `#VMIN`, por la misma razón exacta.

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
*«A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO»* (así, **sin espacio tras el punto**, que es como el PDF lo imprime) — «conducto cerrado», no
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

> **Aviso a C5, y no es menor: `afinado` NO es «más conservador» sin más.** Y el mecanismo hay
> que decirlo bien, porque CN lo escribió mal en su primera redacción (§15.10, punto 8): **las
> dos ramas se mueven en el MISMO sentido** —con n mayor, los dos tirantes suben y las dos
> velocidades bajan, porque `V = Q/A` es monótona decreciente en n—. Lo que cambia de signo es
> **el sentido de la exigencia de cada verificación**. Recomputado a mano sobre un marco
> B = 2.00 m, H = 1.50 m, S = 0.001, Q = 2.0 m³/s:
>
> | | y/H (rama n_máx) | V de sedimentación (n_máx) | V de erosión (n_mín) | d₅₀ |
> |---|---|---|---|---|
> | `tubo recto` (0.010, 0.013) | 0.4870 | 1.3689 m/s | 1.6509 m/s | 0.0897 m |
> | `afinado` (0.011, 0.014) | **0.5139** | **1.2973 m/s** | **1.5430 m/s** | **0.0784 m** |
>
> O sea: `afinado` **aprieta** V1 (y/H sube un 5.5 %, se acerca al techo de 0.75) y **aprieta
> V2** (la velocidad de la rama n_máx, que es la que evalúa el piso de autolimpieza, baja un
> 5.2 %); y **afloja** V3 (la velocidad de erosión baja un 6.5 %, pasa con más holgura) y
> **afloja el d₅₀ de Laushey** (cae un **12.6 %**, o sea piedra más chica). **Son cuatro
> verificaciones afectadas, dos en cada sentido.** La dirección **no es uniforme** y el criterio
> tiene que decirlo, igual que `DIAMETRO_MIN_AMBITO` lo dice del piso de 0.90 m.

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
| **La declaración entera**, una vez por punto de Familia C | **`bloque_alcance`**, vía un `Bloqueo(fase="Fase 5 - Verificaciones", etapa="VC1 - no alteración de la rasante hidráulica ni del borde libre del canal", tipo="DiferidoPorAlcance", diferido_por_alcance=True, mensaje=<el texto de §15.6.2>)` emitido por `cli` | Es el bloque que **imprime SIEMPRE** —su propio docstring dice que en alcance de expediente tampoco desaparece— y **no depende de que ningún criterio tenga valor**. Es **por punto**, de modo que nombra los puntos afectados. Y ya existen los precedentes exactos: `cli._cabezal_diferido` (cli.py) y `cli._diferir_fase_8` — **ese es el nombre; CN escribió `_fase8_diferida`, que no existe (§15.10, punto 4)**. `diferido_por_alcance=True` es lo que impide que además cuente como defecto del expediente en `Informe.cerrado` |
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

**Cómo se le da forma al mensaje, porque el vehículo tiene una restricción que hay que
respetar.** `bloque_alcance` pinta el fundamento con `_esc(b.mensaje)`: **escapa el HTML y lo
mete en UNA celda de tabla**. El texto de §15.6.2 son siete párrafos con negritas; volcado tal
cual saldría con los asteriscos literales y en un solo bloque ilegible. **C5 tiene dos salidas
y ninguna es reescribir `_esc`:** o el `mensaje` se redacta en prosa corrida sin marcas —
perdiendo la jerarquía visual pero conservando entero el argumento —, o `bloque_alcance` gana
una rama para el diferimiento de una verificación, como ya tiene una para el diferimiento por
criterio (`if b.criterio: … else: …`). **La segunda es la que conserva el texto**, y es un
cambio de M11 que C8 puede absorber; la primera cabe en C5 sola. Que se elija una u otra,
pero que **no se deje el texto entrando por `_esc` con las negritas puestas**.

**Comprobación que C5 debe dejar en verde** (criterio de aceptación #6 de §11), y son **dos**,
porque la auditoría mostró que una sola verifica media declaración (§15.10, punto 4):

1. **El primer vehículo.** Repetir la corrida de arriba y comprobar que la cadena «no evalúa ese
   requisito» aparece en el HTML **antes** de que ningún criterio nuevo tenga valor. Si sólo
   aparece con los criterios declarados, el vehículo elegido está mal.
2. **El segundo vehículo, que hoy NO se puede ejercitar con el fixture tal como está.** C-01
   trae `Q_m3s` vacío a propósito (`M0_carga._VACIAS_FAMILIA_C`) y **se detiene antes de llegar a
   V1 y a V4b**, de modo que su `nota_del_proyecto` no se emite nunca. Hace falta un caso —fila
   nueva del fixture o `--datos-externos` en el test— que **llegue a las verificaciones**, y
   comprobar allí que la nota sale junto al número. Sin ese segundo caso, la mitad del diseño de
   §15.6.3 queda sin prueba.

### 15.7 (b) Los `Fundamento` que C3, C4 y C5 necesitan

**Regla que gobierna los ocho, y es T11:** `Registro.problemas_de_integridad` exige que
**al menos una** de las citas de un `Fundamento` tenga un `caracter` compatible con su
`verbo` (`VERBO_COMPATIBLE_CON`; verificado en `registro.py`: la condición es
`any(...)`, no `all(...)`, precisamente para que V2 pueda colgar de su exigencia y de su
recomendación a la vez). Por eso **cada bloque de abajo lleva el carácter de cada cita
anotado**: es lo que hay que comprobar antes de escribirlo, no después.

**Ocho citas no existen todavía.** Van marcadas `⛔ POR TRANSCRIBIR (C2)` y **ningún
fundamento que dependa de ellas se puede construir hasta que C2 las transcriba y
`test_normativa_pdf.py` las verifique** — cuáles quedan bloqueados y cuáles no está medido más
abajo. Sus páginas están en §15.3 y §15.4:

| Id propuesto | Qué transcribe | Impresa / PDF | `caracter` |
|---|---|---|---|
| `MC_HHD.4.1.1.3.4a#TIPOS` | *«Los tipos de alcantarillas comúnmente utilizadas … son; marco de concreto, …»* | 71 / 74 | `DEFINICION` |
| `MC_HHD.4.1.1.3.4a#NIVELES` | *«Las alcantarillas tipo marco de concreto de sección rectangular o cuadrada **pueden** ubicarse a niveles que se requiera…»* | 72 / 75 | `PERMISO` |
| `MC_HHD.4.1.1.3.4a#MARCO` | *«Generalmente, **se recomienda** emplear este tipo de alcantarillas cuando se tiene la presencia de suelos de fundación de mala calidad.»* | 72 / 75 | `RECOMENDACION` |
| `MC_HHD.4.1.1.3.4a#MULTIPLES` | *«…recomendándose utilizar obras con mayor sección transversal libre, sin subdivisiones.»* | 72 / 75 | `RECOMENDACION` |
| `MC_HHD.4.1.1.3.7d` | *«Las dimensiones de las alcantarillas deben permitir efectuar trabajos de mantenimiento y limpieza en su interior de manera factible.»* | 80 / 83 | `EXIGENCIA` |
| `MC_HHD.LAMINA_03` | rótulo de la 3.ª figura, `metodo=IMAGEN` | 209 / 212 | `DEFINICION` |
| `HDS5_3ED.A.3#FORMAS` | *«coefficients for rectangular (box) shapes should not be used for nonrectangular … shapes and vice-versa»* | A.3 | `EXIGENCIA` |
| `HDS5_3ED.TC2#cajon_*` | **las once filas de la familia «Box, Reinforced Concrete»** de la Tabla C.2, con sus configuraciones de aletas (0.4 – 0.7). Obliga además a **ampliar el `Acotada` de `T_HDS5_C2`**, cuya razón deja de ser cierta | C.6 / 216 | `DEFINICION` |

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

**Y un patrón del archivo que los ocho tienen que respetar, medido sobre los diecisiete
vigentes:** ninguno de sus `por_qué` entrecomilla texto de la fuente — `F5.V1` dice *«El Manual
lo escribe como el 25 % de la altura de la estructura»*, que es **paráfrasis sin comillas**. El
`por_qué` se imprime en la memoria, de modo que una frase entrecomillada ahí sería una **segunda
transcripción** fuera de `Registro.textos_literales()`. Los bloques de abajo llevan ya la
corrección; la denuncia y su origen están en §15.10, punto 5.

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
        "entre las mas usuales, PERMITE expresamente ubicarlo a la cota que "
        "se requiera -- que es justo lo que un cruce a nivel de canal "
        "necesita -- y RECOMIENDA emplearlo con suelos de fundacion de mala "
        "calidad. Ademas lo DIBUJA para este caso exacto: la Lamina N 03 "
        "trae una figura de marco de concreto en cruce de canal de riego. La "
        "asignacion del tipo a la Familia C la hace la Sec. 2.3 de la hoja "
        "de ruta; lo que estas citas aportan es que esa asignacion tiene "
        "respaldo en la fuente primaria y no solo en la hoja."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.4a#TIPOS",     # DEFINICION    ⛔ POR TRANSCRIBIR (C2)
           "MC_HHD.4.1.1.3.4a#NIVELES",   # PERMISO       ⛔ POR TRANSCRIBIR (C2)
           "MC_HHD.4.1.1.3.4a#MARCO",     # RECOMENDACION -> sostiene RECOMIENDA
           "MC_HHD.LAMINA_03"),           # DEFINICION    ⛔ POR TRANSCRIBIR (C2)
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
        "riego, y ordena adoptar alli la seccion segun cada diseno "
        "particular. La Familia C ES ese conjunto de cruces. Lo que el "
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
        "La Tabla N 09 SI cubre al cajon por el TITULO DE SU GRUPO, que "
        "habla de conducto cerrado con escurrimiento parcialmente lleno y no "
        "de tuberia: es el unico grupo de la tabla que describe una "
        "alcantarilla. Lo que no tiene es una FILA que nombre la seccion "
        "rectangular. El vacio es de fila y no de grupo, y por eso la "
        "analogia se declara DENTRO del grupo que ya cubre la estructura "
        "-- entre filas separadas por un atributo que no es la forma -- y es "
        "mas estrecha que la de 'n_manning_hdpe', que cruza material. El "
        "rango se toma completo, minimo y maximo: la regla de doble n pide "
        "los dos extremos, porque n_max es conservador para capacidad y "
        "n_min para velocidad y socavacion."),
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
`normativa/discrepancias.py` se revisaron una a una. *(C3 añadió D-10 y C4 añade D-11 y
D-12; los doce siguen sin duplicar ninguna `DIS-HR-*`.)*

| Id | Dónde | Qué dice la v8 | Qué dice la fuente primaria | Dónde se ve en el código |
|---|---|---|---|---|
| **D-1** | **Sec. 3.1**, «Reglas duras **[N]**» · y **Sec. 3.2** | *«**Diámetro mínimo 0.90 m (36")** — num. 4.1.1.3.4 a), pág. 72»*, sin condición; y *«desde 0.90 m (mínimo normativo MTC)»* | La misma oración lo condiciona **dos veces**: *«En carreteras de alto volumen de tránsito…»* y *«**salvo en cruces de canales de riego**…»*. Impresa 72 / PDF 75 | `constantes_normativas.DIAMETRO_MIN_AMBITO` y las dos `CondicionAplicacion` de `MC_HHD.4.1.1.3.4a` ya llevan las dos condiciones. **La v8 no.** Un lector de la v8 aplicaría el piso a la Familia C |
| **D-2** | **Sec. 3.1**, bajo «Reglas duras **[N]**» | *«Suelo de fundación deficiente → orientar a marco de concreto»* | *«**Generalmente, se recomienda** emplear este tipo de alcantarillas cuando se tiene la presencia de suelos de fundación de mala calidad.»* — **recomendación atenuada**, impresa 72 / PDF 75. Y la fuente **no define «mala calidad»** | El párrafo **no está transcrito en el repositorio**: `MC_HHD.4.1.1.3.4a` sólo transcribe el del 0.90 m. Es `NOR-MEM-01` en su forma exacta: una regla dura escrita encima de un «se recomienda» |
| **D-3** | **Sec. 3.1** y **fila V6 de la Fase 5** | *«Con palizada: sección única mayor, no múltiple»* como regla dura, y la fila V6 con ancla **«[N]» y NINGÚN numeral** | La frase que más se le parece dice *«…**recomendándose** utilizar obras con mayor sección transversal libre, sin subdivisiones»* (impresa 72 / PDF 75): **recomendación, no exigencia**. Y el requisito lo sostienen **dos** párrafos de **dos** numerales distintos — ése, y el de 4.1.1.3.7 a) que habla de *«alcantarillas de mayor sección hidráulica»* (impresa 78 / PDF 81) | Un `[N]` sin numeral es lo que `CLAUDE.md` prohíbe de entrada. **La v8 no nombra ninguno de los dos.** Lo que falta transcribir es el de la 72, que es el único que habla de **subdivisiones**, o sea de multicelda |
| **D-4** | **Sec. 3.4**, «Matriz de decisión de material» | *«Concreto reforzado · Vacíos normativos: **Ninguno.** n y velocidad máxima en Tablas Nº 09 y Nº 10…»* | Cierto para la sección **circular** y **falso para el marco**: la Tabla Nº 09 no tiene fila de sección rectangular (§15.3.2). La velocidad de la Tabla Nº 10 sí sirve, porque clasifica por revestimiento | El criterio nuevo `n_manning_cajon` **[N→]** es la prueba: si el concreto no tuviera vacíos, no haría falta |
| **D-5** | **Fase 4, §4.1**, tabla «Tabla Nº 09 — Manning» | Lista cuatro filas y ninguna nota sobre el ámbito de la tabla | El grupo que gobierna se titula *«A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO»* y **cubre al marco**; lo que falta es la **fila**. La v8 no distingue una cosa de la otra | `constantes_normativas.TABLA_09_GRUPO` ya declara que el grupo A es *«el único grupo de la tabla que describe una alcantarilla»*. La v8 no lo recoge |
| **D-6** | **todo el documento** | La **Lámina Nº 03 no se menciona ni una vez** en la v8, ni en su Fase 3, ni en su Fase 6, ni en su Anexo B | El Manual trae, impresa 209 / PDF 212, una figura titulada **«ALCANTARILLA TIPO MARCO DE CONCRETO EN CRUCE DE CANAL DE RIEGO»**: el respaldo gráfico normativo del tipo de estructura de la Familia C | Hoy no está citada **en ninguna parte del repositorio**. Ver §15.4 para la forma en que entra |
| **D-7** | **Sec. 2.3**, Familia C | Enuncia el requisito *«No puede alterar la rasante hidráulica ni el borde libre del canal»* **sin etiqueta, sin numeral y sin verificación asignada**, mientras que a la Familia A sí le da conjunto de aceptación (V1+V2+V4+V5) | El requisito no sale de ningún numeral del Manual: se apoyaría en la Ley 29338 y la DG-2018, **fuentes ausentes** del registro | `M1_clasificacion.PERFILES[Familia.C].verificaciones_aceptacion = None`, con el comentario *«Sec. 2.3 no declara conjunto propio»*. Es el hueco que §13 llama **VC1** y lo que obliga a la declaración de §15.6 |
| **D-8** | **Fila V7 de la Fase 5** | Enumera cuatro filas de la Tabla 2.4.5.3.1-2 —«Estructura rígida enterrada» 1.30/0.90, «Alcantarillas termoplásticas» 1.30/0.90, flexibles «Entre otros» 1.95/0.90 y «Muros y estribos de retención» 1.35/1.00— y **omite «Pórticos rígidos» (1.35/0.90)** | Es la fila que la regla vinculante **#8** asigna al cajón: la v8 desglosa la tabla por tipo de estructura y deja fuera precisamente el tipo de la Familia C | `constantes_normativas.TABLA_GAMMA_P_FILAS` **sí la tiene** (`EV_porticos_rigidos`, 1.35/0.90). El que no la contempla es el desglose de la v8 |

| **D-9** *(C2, redacción corregida por C3)* | **Fase 4, §4.2**, control de entrada | Escribe **una** ecuación de control de entrada no sumergido —la que lleva `Ks·S`— y presenta las constantes `K, M, c, Y` de la Tabla A.1 como si una sola ecuación las consumiera. **C2 escribió que «no menciona que HDS-5 tiene DOS formas», y eso es inexacto: la v8 rotula su ecuación «Forma 1».** Medido sobre el documento entero: la palabra «Forma» aparece **tres veces** y las tres son «Forma 1»; **«Forma 2» no aparece nunca**. La omisión no es más leve por eso, es **más aguda**: rotula una forma y jamás dice que exista otra, de modo que el lector no tiene por dónde enterarse. Y en la línea del `MAT-D10` usa «las dos formas» para nombrar las dos **ramas** (no sumergida y sumergida), que **colisiona con el término del propio HDS-5** | La Tabla A.1 tiene una columna **«Equation Form»** con valores 1 y 2, y el num. A.3 (pág. impresa **A.2** / PDF 191) prohíbe cruzarlas: *«coefficients for rectangular (box) shapes should not be used for nonrectangular … shapes and vice-versa»*. Para el cajón la cosa es inmediata: **la Carta 8 es Forma 1 y las Cartas 9, 10, 11 y 12 son Forma 2**, y la Forma 2 **no lleva `Ks·S`** | `modelos.ConstantesHDS5.forma` y la columna `equation_form` de `T_HDS5_A1`, ambos añadidos por C2. Con la v8 en la mano, quien implemente el cajón copiará la Forma 1 y le cambiará las constantes: con `Ks = -0.5` el término **resta** carga y el HW sale **menor que el real**, del lado no conservador, sin que ninguna guardia de signo lo detecte |

| **D-10** *(C3)* | **Fase 4, §4.2**, encabezado «Fuente a citar», y el bloque de código de la §12 | Cita la Tabla A.1 como *«Apéndice A, Tabla A.1, **pág. A.8**»*, en **dos** sitios | **Esa página no lleva folio impreso.** La numeración del Apéndice A termina en **A.7**; las cuatro hojas apaisadas de tablas (PDF 197–200) van **sin numerar** y el Apéndice B reinicia en B.1. Verificado dos veces y de dos formas independientes: en C2 por render del pie, y en C3 midiendo el rango vertical de todo el texto de la página —no hay una sola palabra en la banda del pie— | El repositorio ya lo declara en la `nota` de `citas.HDS5_TA1` y en el `donde_leerlo` de `T_HDS5_A1`: «A.8» es una **inferencia por secuencia**, correcta y predicha por la regla de paginación, pero **no una lectura**. La v8 la escribe como si lo fuera, y es la única referencia que le da al lector para encontrar la tabla |

| **D-11** *(C4)* | **«Notas críticas de programación»** (la lista que un programador lee como checklist) | Enuncia **sin condición** dos propiedades que sólo valen para la sección circular: *«**Q(y/D) no es monótona** cerca de sección llena (máximo en y/D ≈ 0.938)»* y *«**M4 necesita tirante crítico:** Q²T/(gA³) = 1, **segundo Brent sobre θ**»* | Las dos son **falsas para el marco**, medido: barrido de 400 tirantes entre 0 y H sobre 2.00 × 1.50 → **Q(y) es estrictamente creciente, sin pico**; y el crítico **se despeja**, `y_c = (q²/g)^(1/3)`, sin segundo solver y sin θ. **La v8 se contradice a sí misma**: su §4.2.1 lo condiciona bien —*«El tirante crítico **en sección circular** no tiene solución cerrada»*—, pero la versión sin condición es la que está en el checklist | `SeccionRectangular.llenado_critico_cerrado` y `M4.tirante_critico`, que bifurca por lo que la sección responde. **La consecuencia no es cosmética:** quien implemente desde el checklist pone un Brent donde hay fórmula cerrada, y con él **reintroduce la clase de fallo de `SIS-G-02`** que la forma cerrada retira |
| **D-12** *(C4)* | **Fase 4, §4.3**, ecuación de pérdida de carga | Escribe `H = (1 + k_e + 19.63·n²·L/R^(4/3))·V²/(2g)` **sin decir qué `R`**, y la única R que la v8 define es la de §4.1, `R = A/P` de la sección circular parcialmente llena | Para un marco hay **dos R distintas y las dos son correctas**, cada una en su régimen: la de **lámina libre** (`P = B + 2y`, sin la losa superior) y la de **sección llena a presión** (`P = 2(B+H)`, con ella). Medido sobre 2.00 × 1.50 m: en `y = H` valen **0.600 m** y **0.4286 m** — un **40 %** —. En la circular **convergen** (en θ = 2π el ancho de la lámina se anula y el perímetro de lámina libre ya es πD), y por eso la ambigüedad de la v8 no se nota | `SeccionRectangular.radio_hidraulico_lleno` frente a `geometria_en(y).R`, con la distinción escrita en el docstring de la clase y fijada en `CP2R_GEOMETRIA_MANNING_RECTANGULAR`. El proyecto **sí** la resuelve, por el criterio `geometria_control_salida = "seccion_llena"`; lo que no la resuelve es la v8, y quien generalice su `R = A/P` al marco se equivoca en un 40 % en el término de fricción |

**Recordatorio, no defecto nuevo:** `DIS-HR-G-LAUSHEY` sigue en estado
`ABIERTA_CONTRA_HOJA_DE_RUTA` y esta sesión la **reconfirmó por segunda vía independiente**
(§15.3.4): el num. 4.1.1.3.7 c) define `g` sin número. **La v8 sigue mal ahí.**

#### Huecos del repositorio que esta sesión destapó (no son de la v8)

| Id | Símbolo | Qué falta | Quién lo cierra |
|---|---|---|---|
| ~~**R-1**~~ **cerrado en C2** | `citas.MC_HHD_4_1_1_3_4a` | Transcribe **sólo** el párrafo del 0.90 m, con `caracter=EXIGENCIA`. Los párrafos de **PERMISO** y **RECOMENDACIÓN** que sostienen el tipo de la Familia C no están | **C2** — `#TIPOS`, `#MARCO`, `#MULTIPLES` (§15.7) |
| ~~**R-2**~~ **cerrado en C2** | `citas` / `tablas` | **No existe cita del num. 4.1.1.3.7 d)**, que es la única exigencia sin número que acota la sección del cajón tras levantarse el piso de 0.90 m | **C2** — `MC_HHD.4.1.1.3.7d` |
| ~~**R-3**~~ **cerrado en C2** | `constantes_normativas.TABLA_09_FILAS` | Transcribe cuatro filas del grupo A. **`afinado` no está**, y es la única fila del ítem sin forma en el rótulo: la candidata a la analogía del cajón | **C2**, y **C5** elige y declara cuál toma (§15.3.2) |
| ~~**R-4**~~ **cerrado en C2** | `constantes_normativas.TABLA_09_FILAS` | Sus valores de A.2 son la lectura **corregida** del corrimiento y el bloque **no remite a `DIS-MCHHD-T09-A2-DESPLAZADA`**, que está declarada en `normativa/tablas.py`. Quien lea sólo `constantes_normativas` y vaya a la página encuentra otros tres números | **C2** — una línea de remisión; la discrepancia ya existe y **no hay que volver a demostrarla** |
| ~~**R-5**~~ | ~~`SIN_FUNDAMENTO` de `F5.V6`~~ | **RETIRADO por la auditoría adversarial (§15.10, punto 7).** CN afirmó que la ficha remitía al numeral equivocado, y es falso por partida doble: el num. **4.1.1.3.7 a) se titula literalmente «Material sólido de arrastre»** —el mismo nombre que V6— y contiene *«alcantarillas de mayor sección hidráulica»*; y la cláusula prospectiva de la ficha apunta al Ø48" **para lo que esa cláusula dice**, que es un diámetro mínimo por zona. **La ficha está bien y no se toca.** *(De paso: `SIN_FUNDAMENTO` es una `Tuple[Tuple[str,str,str], ...]`, no un dict — la notación con corchetes que CN usó sería un `TypeError`.)* | — |
| **R-9** | `M6_proteccion.proteccion_salida` (docstring) | Afirma que `longitud_proteccion_salida` está *«hoy sin valor — la llamada se detiene con `CriterioPendienteError`»*. **Medido: vale `5.0` con `sensibilidad=(3.0, 8.0)`.** Docstring que describe un estado que dejó de ser cierto | fuera del alcance de este plan; se registra aquí porque salió al comprobar que la Fase 6 no se toca |
| ~~**R-10**~~ **cerrado en C2** en su mitad de transcripción; el acoplamiento de `ke_entrada` sigue en C5 | `normativa/tablas.py::T_HDS5_C2.alcance` | Es `Acotada` con la razón *«…el catálogo de conductos de la Sec. 3.2 **no ofrece sección cajón**: ninguna de esas filas puede aplicarse a un punto de este corredor»*. **C5 destruye esa premisa** en cuanto M2 devuelva un candidato de marco. Es el antipatrón que §12 enumera: *«No dejar un `Acotada` describiendo un alcance que ya no es el suyo»* | **C2** transcribe las once filas de «Box, Reinforced Concrete»; **C5** amplía la `Acotada` y acopla `ke_entrada` a `embocadura_cajon` |
| **R-11** | `normativa/citas.py::HDS5_TA1`, campo `pagina_impresa` | Dice `"A.8"`, y **esa página no imprime folio**. C2 lo anotó en la `nota` de la cita; C3 lo reconfirmó por una vía distinta (rango vertical del texto de la página) y **sigue sin corregirse**: el campo afirma un número que el documento no imprime. Lo que sí es sólido e inequívoco es **PDF 197** más el título literal de la tabla | fuera del alcance de C3 (punto 9): tocar `pagina_impresa` mueve un campo que **T6** usa para predecir la página desde la regla de paginación, y esa interacción hay que resolverla, no esquivarla |
| **R-12** | `normativa/citas.py::HDS5_3ED.3.1.3#TRANSICION` | Su `Verbatim` termina en *«…connecting them with a line tangent to both curves»* y **la fuente continúa** *«, as shown in Figure 3.4.»*. Es una **elisión final sin marcar** bajo el rótulo «texto literal»: el mismo patrón que `CLAUDE.md` denuncia en la tercera condición de `h_o` y que C2 ya corrigió en `#MULTIPLES`. Las palabras citadas son exactas; lo que falta es la marca de corte. Verificado contra PDF 86 | **anotado y no corregido en C3** (punto 9). Es una línea, y va con quien cierre la familia de elisiones: arreglarla mezclada con la bifurcación de forma la volvería invisible, que es lo que C1 y C2 dejaron por escrito |
| **R-13** *(C4)* | `M3_hidraulica`, línea de import | Importa `SeccionCircular` y **no la usa**: las tres apariciones restantes del nombre en el archivo son comentarios, y un comentario no sostiene un import. Es **anterior a C4** —medido sobre `05d8a5e`, el `origin/main` con que arrancó la sesión— y es de C1, que mudó la geometría a `modelos` y dejó el import detrás | anotado y no corregido (punto 11 del prompt de C4: un defecto ajeno se anota y se sigue). Es una línea, y va con quien toque los imports de M3 — probablemente **C6**, que reescribe las entradas |
| **R-6** | `variables_entrada._Columna.criterio_destino` | Es `Optional[str]`, un solo destino. Un segundo consumidor de `sucs_fundacion` obliga a decidir tupla o cambio de destino: **es cambio de esquema** | **C6**, no C5 (§15.5) |
| ~~**R-7**~~ **cerrado en C2** (`DIS-MCHHD-LAMINA-03-TMC`) | `normativa/discrepancias.py` | El cuerpo del Manual describe **mal su propia Lámina Nº 03**: dice *«se aprecia secciones típicas de alcantarillas tipo marco de concreto»* (impresa 73) y la **primera de sus tres figuras es tubería metálica corrugada** (impresa 209). Contradicción **interna de la fuente primaria**, no contra la v8 | **C2** — una `Discrepancia` de estado `ABIERTA`, para que un revisor que cuente las figuras no crea que la cita está mal puesta |
| **R-8** | `criterios_adoptados['factores_carga_aashto']` | Su comentario justifica la fila del tubo diciendo *«No es "Pórticos rígidos" … la Familia C, de marco o multicelda, sale sin candidatos»*: **describe un estado que C5 deja de ser cierto**. Falta además la clave del cajón | **C5** — junto con el epígrafe «Familia C queda sin candidatos» de `M2_material`, que tiene el mismo problema y ya está en el prompt de C5 |

### 15.9 Correcciones a ESTE documento

Las cinco primeras salen de la verificación de CN y **se corrigen aquí porque §6 y §13 son
vinculantes**: una regla vinculante mal fundada se cita literal en una memoria y ahí ya es una
cita falsa. **La sexta la añadió C4** y es de la misma familia, con el agravante de que el
texto corregido **se imprime**.

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

4. **§6 necesita una regla vinculante más, y la trae la auditoría (§15.10, punto 1).** Ninguna
   de las diez reglas cubre `k_e`. Propuesta de **#11**, con la forma de las otras: *«El `k_e` de
   la Tabla C.2 del HDS-5 tiene familia propia para el cajón. El 0.5 que el proyecto usa sale de
   la fila `Square-edge` del bloque «Pipe, Concrete»; el bloque «Box, Reinforced Concrete» tiene
   once filas y va de 0.4 a 0.7 según las aletas. `ke_entrada` deja de ser un valor fijo y queda
   acoplado a `embocadura_cajon`, y el `Acotada` de `T_HDS5_C2` — cuya razón es que el catálogo
   no ofrece sección cajón — hay que ampliarlo.»*
5. **§10-CN punto 1 pedía «fase por fase, paso por paso, qué numeral lo sostiene», y esa pregunta
   sola no basta.** `ke_entrada` tiene numeral, tiene fuente y tiene etiqueta correcta, y aun así
   cambia con la forma. La pregunta que hay que añadir, y que §15.1 ahora lleva, es: **¿la TABLA
   de la que sale el valor enumera sus filas por algo que el marco no es?** Con la primera
   pregunta sola, `ke_entrada` pasa desapercibido; con la segunda, salta a la primera lectura.

**Reglas que la verificación CONFIRMA sin matices, y conviene decirlo tan explícitamente como
las correcciones:** la **#1** (el cajón no hereda el piso de 0.90 m: la excepción es expresa y
está en la misma oración) y la **#7** (la Tabla Nº 10 clasifica por `TIPO DE REVESTIMIENTO`;
**no** se abre `v_max_cajon`).

6. **§15.7, `F4.SECCION` — el sujeto de la frase, corregido contra la fuente primaria (C4).**
   La redacción decía *«eso depende de la forma, y **el Manual** no fija ninguna»*, y ese texto
   **se imprime en la memoria**: es el `por_qué` de un paso. Verificado contra el PDF, num.
   **4.1.1.3.6**, pág. impresa **74** / PDF **77**: el numeral prescribe Manning, define A, P y
   R **por su significado y su unidad** —*«A : Área de la sección hidráulica (m2)»*, *«P :
   Perímetro mojado (m)»*, *«R : Radio hidráulico (m)»*—, escribe `R = A/P` como única relación
   entre ellos y **no escribe ninguna geometría de sección** (comprobado además sobre las cuatro
   páginas del numeral y sobre las 225 del PDF: los aciertos de `θ` están todos en la prueba de
   bondad de ajuste del Cap. III y en el capítulo de socavación). Hasta ahí la frase es exacta.
   **Lo que no lo es es el sujeto:** el Manual **sí** enumera formas y **sí** impone una, en el
   num. **4.1.1.3.4 a)**, pág. impresa 72 — *«Las secciones mas usuales son circulares,
   rectangulares y cuadradas…»* y la sección mínima de 0.90 m —, que este mismo repositorio cita
   en otro sitio. El que no fija ninguna es **este numeral**, y así queda escrito en
   `normativa/fundamentos.py` y en `modelos.SeccionRectangular.formula_geometria`. Es una
   palabra, y es la diferencia entre una afirmación verificada y una sobreafirmación impresa
   bajo el rótulo «por qué se hace».

### 15.10 Lo que la auditoría adversarial encontró

`auditor-adversarial` corrió sobre esta misma sección con el encargo de refutarla en ocho
frentes. **Encontró una refutación y cuatro ajustes**, y los cinco están ya incorporados
arriba. Se deja el registro entero —incluido lo que confirmó y lo que le refuté a él— porque
un informe de auditoría del que sólo se conserva lo cómodo no es una auditoría.

| # | Frente | Veredicto |
|---|---|---|
| 1 | La regla de lectura de §15.1 | **REFUTADO** |
| 2 | Las cuatro afirmaciones sobre la Tabla Nº 09 | CONFIRMADO, con una salvedad de transcripción |
| 3 | La prohibición de tomar el n del grupo B | CONFIRMADO |
| 4 | Las tres mediciones que deciden el vehículo | CONFIRMADO en las tres; **AJUSTADO** en tres detalles |
| 5 | Los ocho `Fundamento` | verbos e ids correctos; **AJUSTADO** en tres |
| 6 | «La Fase 6 no se toca» | CONFIRMADO |
| 7 | Los defectos D-1…D-8 | seis confirmados; **una mitad REFUTADA** |
| 8 | La dirección del conservadurismo de `afinado` | conclusión confirmada; **mecanismo AJUSTADO** |

#### 1 · La refutación, y es la que valía la sesión entera

**CN escribió que el vacío se abre en «tres, y sólo tres» tablas. Son cuatro.** La que faltaba
es la **Tabla C.2 del HDS-5**, de donde sale `k_e`, y el caso es idéntico al de la Tabla A.1
que CN sí resolvió: la tabla tiene una familia **«Box, Reinforced Concrete»** aparte de la
**«Pipe, Concrete»** de la que el proyecto toma su 0.5.

Lo que hace grave el descuido no es la omisión, es la **asimetría**: CN razonó correctamente
sobre la Tabla A.1 —«hay cartas de cajón, no es un vacío, es otra fila de la misma tabla»— y
**no aplicó el mismo razonamiento a la Tabla C.2**, que tiene `alcance=Acotada` por exactamente
la misma razón y la consume la misma función, `M4.control_salida`.

Comprobado sobre el registro construido, no sobre el PDF:

- `criterios_adoptados['ke_entrada']` → `valor=0.5`, **`sensibilidad=None`**, `etiqueta="C"`,
  `resolucion=DeTabla(tablas=('HDS5_3ED.TC2',), fila_id='concreto_headwall_square_edge')`.
- `registro.tabla("HDS5_3ED.TC2").filas` → **quince filas, todas de `Pipe, Concrete` o de
  `Pipe. or Pipe-Arch. Corrugated Metal`**. Ninguna de cajón.
- `…TC2.alcance.que_queda_fuera` → *«"Box, Reinforced Concrete": Headwall parallel to
  embankment (no wingwalls), Wingwalls at 30° to 75° to barrel, Wingwall at 10° to 25° to
  barrel y Wingwalls parallel (extension of sides), con sus sub-bordes»*.

**Por qué importa el número.** `H = (1 + k_e + 19.63·n²L/R^(4/3))·V²/2g`. Pasar de 0.5 a 0.7
—la fila de aletas paralelas— sube `H` en `0.2·V²/2g`: con V = 3 m/s son **0.092 m** de HW que
el cálculo no vería, contra V4 y contra el tamizado de 7.A. Es el mismo género y el mismo orden
de magnitud que el 0.18 m que `F4.FORMA_HDS5` invoca como *«exactamente la forma de MAT-D10»*.
Y con `sensibilidad=None` y etiqueta `[C]`, **nada se detiene**: un punto de Familia C tomaría
el `k_e` de un tubo en silencio, que es la regla nuclear del proyecto.

**Qué cambió arriba:** §15.1 punto 3 pasa a enumerar cuatro tablas; §15.2.3 gana la fila
corregida del control de salida y la nota de `T_HDS5_C2`; el recuento de §15.2 dice «un paso
del Manual MTC cambia de etiqueta, **y un segundo cambia de fila sin cambiarla**»; §15.8 gana
**R-10**; y §15.9 propone la **regla vinculante #11** para §6.

#### 2, 3 y 6 · Lo que confirmó

- **Tabla Nº 09**: las cuatro afirmaciones, leídas por coordenadas de línea base. Siete filas
  hoja, `afinado` es una sola palabra en la columna de rótulos, el grupo A cubre al marco por su
  título, y la lectura corregida de `afinado` es 0.011 / 0.012 / 0.014. Corroboró además por una
  vía interna que CN no usó: `T09.alcance.que_queda_fuera` dice «las **seis** subfilas restantes
  de "a. Concreto"», y 6 + la transcrita = 7. **Salvedad aceptada:** el PDF imprime
  `A.CONDUCTO` **sin espacio** tras el punto; corregido en las tres ocurrencias.
- **Grupo B**: la prohibición no la inventa §15, ya está en `TABLA_09_GRUPO` y en
  `T09.alcance.razon`.
- **Fase 6**: leyó el módulo entero y confirmó que sus dos funciones toman sólo `V`. Añadió un
  matiz correcto —«es cierto del código, no del resultado»: `V` sale de la rama n_mín y cambia
  con la sección— y, de paso, encontró **R-9**.

#### 4 y 5 · Los ajustes, todos aceptados

| Ajuste | Qué se corrigió |
|---|---|
| `cli._fase8_diferida` **no existe**; es `cli._diferir_fase_8` | §15.6.3. Es la regla 4 de `CLAUDE.md`: anclar por nombre de símbolo |
| El `mensaje` del `Bloqueo` entra por `_esc()` **a una celda de tabla** | §15.6.3 gana el párrafo de cómo se le da forma, con las dos salidas posibles |
| La comprobación de aceptación **no ejercita el segundo vehículo**: C-01 se detiene antes de V1 y V4b | §15.6.3 pasa a tener **dos** comprobaciones |
| «Cinco citas no existen» y la tabla tenía seis | corregido — y con las de la Tabla C.2 y la partición de `#MARCO` son **ocho** |
| `MC_HHD.4.1.1.3.4a#MARCO` llevaba **dos caracteres en un `Cita.caracter` escalar** | partido en `#NIVELES` (`PERMISO`) y `#MARCO` (`RECOMENDACION`). Era el defecto que §15.3.1 denuncia, cometido dos páginas después |
| Tres `por_qué` **transcribían texto literal a mano**, y ninguno de los 17 vigentes lo hace | reescritos en paráfrasis. Es la regla de `CLAUDE.md` que §15 se autoimpone en su propio encabezado |

#### 7 · Lo que le refuté al auditor, y lo que él me refutó a mí

**Me refutó, y tiene razón: la segunda mitad de D-3 y el hallazgo R-5 eran falsos.** CN escribió
que la ficha de `F5.V6` remitía al numeral equivocado. No es así: el num. **4.1.1.3.7 a) se
titula «Material sólido de arrastre»** —el mismo nombre que la fila V6; título en la pág.
impresa 77 / PDF 80— y su pág. impresa **78 / PDF 81** dice *«…mediante la construcción de
alcantarillas de mayor sección hidráulica acorde al estudio puntualizado de la cuenca de
aporte»*. La ficha del
repositorio está bien y **R-5 queda retirado**; D-3 se reescribe para decir lo que sí es cierto:
que la v8 pone `[N]` **sin numeral ninguno**, y que el requisito lo sostienen **dos** párrafos de
dos numerales, de los cuales el único que habla de **subdivisiones** —el de la impresa 72— no
está transcrito.

**Y una corrección menor suya que también acepto:** `SIN_FUNDAMENTO` es una
`Tuple[Tuple[str, str, str], ...]`, no un dict; la notación `SIN_FUNDAMENTO["F5.V6"]` que CN usó
sería un `TypeError`.

**Lo que NO acepto, y queda dicho para que nadie lo reabra:** el auditor apunta que §15 escribe
«Cartas 8–12» y que serían 8–13. **CN no verificó ese dato y lo declara así en dos sitios**: su
fuente es `normas/hif12026.pdf`, no el Manual MTC, y §15 lo toma de la regla vinculante #2 de §6
marcándolo como no verificado por esta sesión. **La numeración de cartas la cierra C3**, contra
las ecs. (A.1) y (A.2), que es donde el plan la puso.

#### 8 · El conservadurismo: conclusión confirmada, mecanismo mal explicado

El auditor recomputó a mano y obtuvo los mismos números que CN. **La conclusión se sostiene**:
`afinado` es más exigente para el tirante y más laxo para la velocidad y el d₅₀.

Pero encontró dos defectos en cómo estaba explicado, y los dos son de los que llevan a un lector
de la memoria a la conclusión contraria:

1. CN escribió que la regla de doble n *«mueve las dos ramas en sentidos opuestos»*. **Falso:
   las dos ramas se mueven en el mismo sentido** —con n mayor los dos tirantes suben y las dos
   velocidades bajan—. Lo que cambia de signo es **el sentido de la exigencia de cada
   verificación**.
2. CN enumeró tres verificaciones afectadas y **son cuatro**: faltaba **V2**, que sale de la rama
   n_máx (`MANNING`: *«El piso de velocidad (V2) NO sale de n_min: sale de n_max»*) y con
   `afinado` también se aprieta.

El aviso de §15.3.2 está reescrito con la tabla de los cuatro números y las cuatro
verificaciones.

---

**Estado de §15 tras la auditoría:** una refutación cerrada con una regla vinculante nueva
propuesta y dos entradas de tracker (`R-10`, y la #11 de §6), cuatro ajustes aplicados, un
hallazgo propio retirado por falso, y ninguna afirmación pendiente de resolver. **El criterio
de salida de §10-CN —que ningún paso quede como «se aplica igual» sin numeral o sin analogía
declarada— se cumple sobre los 42 pasos**, y la lección que la auditoría añade es que ese
criterio, solo, no basta: hay que preguntar además de qué tabla sale cada valor.

---

## 16. Bitácora de sesiones

Una fila por sesión cerrada. El estado de detalle vive en §15 (normativa) y en
`docs/decisiones_diferidas.md` (lo conservado sin consumidor); esta tabla es solo el índice
de qué se corrió, con qué y con qué resultado medido.

| Sesión | SHA | Suite (config) | Qué dejó | Qué queda abierto |
|---|---|---|---|---|
| **CN** | `e2da067` · PR #2, fusionado en `d469409` | 1536 p / 2 s, «PyMuPDF sí / Tk no» | §15: tabla numeral-por-paso, ocho `Fundamento`, la declaración del hueco de aceptación, 8 defectos contra la v8 y 10 huecos del repo (`R-5` retirado por la auditoría: 9 vivos) | nada de CN: lo que dejó propuesto lo aplicó CP |
| **CP** | `53e431a` (consolidación) · `bb8cdfa` (docstrings) · `a6d6543` (prompts) · PR #3 y #4 | 1536 p / 2 s, «PyMuPDF sí / Tk no» | Consolidación en §4.5, §6, §8, §9, §10, §11 y §12; los cuatro puntos de prompt de §16.2; y las tres correcciones de código de `R-9` | los 8 defectos contra la v8 (`D-1`…`D-8`): son de una **v9** |
| **C0** | medida sobre `origin/main` **`4f6cf69`** | 1536 p / 2 s, «PyMuPDF sí / Tk no» | §2-bis (censo de 59 símbolos), §14 (las dos decisiones de alcance), la línea base de `tests/linea_base_familia_c/`, el punto 5 de C1 y §16.3 | el anclaje por línea del manifiesto: **se mide, no se arregla** (§16.3) |
| **C1** | `56677a4` · `b535176` · `a25ce7a` · `f99764a` · `d46256f` · `C1f` · `C1g` · PR #6 | **refactor: 1536 p / 2 s** (collected 1538, el par de C0). **Cierre: 1540 p / 2 s** (collected **1542**), «PyMuPDF sí / Tk no» | La abstracción `Seccion` y su única implementación `SeccionCircular`; `Geometria` lleva la sección y el `llenado` en vez de `D` y `theta`; M3 y M4 dejan de saber la forma del barril; manifiesto regenerado dos veces (11 + 1 ocurrencias); **regla vinculante #12**; punto 0 nuevo en el prompt de C4; **Parte V** de `decisiones_diferidas.md` | ensanchar `regenerar.sh` (tira el JSON, no corre expediente, dimensiona 1 punto de 4) → **C4**. `M8_estructural` fuera del censo de §2-bis → **F4**. `_validar_parametros` sin la forma `not A > 0` de MAT-D13 |
| **C2** | `c8404ad` · `f7526be` · `1874d80` · `ebc114d` · `2018403` · `C2f` · `C2g` · PR #7 | **1540 p / 2 s** (collected 1542), «PyMuPDF sí / Tk no» — **y `test_normativa_pdf.py` corrió COMPLETO, 32 passed, ninguno saltado** | Tabla A.1: las 15 filas del cajón (Cartas 8–12) con su columna de **forma de ecuación**. Tabla C.2: el bloque Box, **7 filas con valor bajo 4 rótulos**. Las **7 citas** de §15.7, la fila `afinado` de la Tabla Nº 09, **4 `Fundamento`** (F3.TIPO_MARCO, F3.MANTENIMIENTO, F3.CELDAS, F4.FORMA_HDS5), `ConstantesHDS5.forma`, `HDS5_INLET` **derivado** de la transcripción, `DIS-MCHHD-LAMINA-03-TMC` y `SIN_COTAS_LAMINA_03`. Cierra R-1, R-2, R-3, R-4, R-7 y la mitad de R-10 | **D-9** nuevo contra la v8 (las dos formas de ecuación de HDS-5). `ke_entrada` sigue en 0.5 de tubo → **C5** (regla #11). La «pág. impresa A.8» de la Tabla A.1 es **inferida, no leída** — esa página no lleva folio |


> **Los dos pares de C1, y por qué son dos.** El refactor cierra con **el par de C0 sin mover**: `1536 passed / 2 skipped`, `collected 1538`, medido sobre los cuatro commits del refactor. Las correcciones de la auditoría añaden **cuatro tests y ni uno más**: las cuatro fichas nuevas de `docs/decisiones_diferidas.md` (`C1-01`…`C1-04`), de las que `tests/test_decisiones_diferidas.py` deriva una comprobación de existencia de símbolo por ficha — 34 fichas antes, 38 ahora. De ahí `collected 1542`. **Ningún test nuevo pinea comportamiento de cálculo**, que es lo que el criterio de salida protegía; los dos asserts de `motivo` que se añadieron caen dentro de casos parametrizados que ya existían y no cambian el conteo.

**No hay archivo de parche.** El parche v2 se aplicó y se retiró del repositorio, con el
precedente que `docs/hoja_de_ruta_correcciones_v12.md` fija en su primera línea para los
borradores v10 y v11 — *«no deben subirse: todo su contenido vivo está aquí»*. Un parche ya
aplicado es una **segunda copia** de lo que vive en §6 y §10, y puede divergir sin que nada
avise. Lo consolidado está en el commit **`53e431a`**; ahí se lee qué se cambió y contra qué.

### 16.1 Qué se cerró y qué sigue abierto

**Cerrado por CP en este documento.** Las diez ediciones del parche v2 —regla #6 reescrita,
regla #11 nueva, séptimo vehículo de memoria en §4.5, C5 punto 6, C2 punto 2 ampliado, §8,
§9, §11 y §12— más **cuatro puntos de prompt** decididos sobre los defectos y huecos de
§15.8, que §16.2 enumera. Y dos cifras del parche corregidas contra la fuente dentro de la
propia regla #11.

**Cerrado por CP en el código**, en su propio commit (`bb8cdfa`): las **tres** frases
«hoy sin valor» que describían un bloqueo inexistente. `R-9` de §15.8 nombraba una
—`M6_proteccion.proteccion_salida`—; el barrido encontró dos más, en el docstring de módulo
de `M1_clasificacion` (`umbral_area_quebrada_importante_ha`, que vale 100.0 con ventana
50–200) y en el epígrafe de V7 de `M8_estructural` (`espesor_pared_conducto`, que trae la
serie de concreto reforzado y se contradecía con el «ya está declarado» de su misma línea).
Las tres se cierran juntas porque son **un solo defecto de diseño**, no tres hallazgos.

**Abierto, y no se cierra desde aquí: los ocho defectos contra la v8** (`D-1`…`D-8`). La v8
es la fuente normativa única y `M11.ruta_hoja_de_ruta()` la localiza por patrón de nombre;
su corrección es una **v9**. Hasta que exista, cada defecto vive en §15.8 con el símbolo del
código donde se ve, y las reglas de §6 son lo que impide que una sesión los herede: **#1**
cubre `D-1`, **#6** cubre `D-4` y `D-5`, **#8** cubre `D-8`, y `D-3` y `D-7` viajan dentro
de los prompts de C5.

### 16.1-bis La línea base de la Familia C, y por qué está normalizada

Vive en **`tests/linea_base_familia_c/`**, medida sobre `origin/main` **`4f6cf69`** con la
configuración de referencia («PyMuPDF sí / ventana Tk no», `1536 passed / 2 skipped`,
collected 1538). Tres archivos:

| Archivo | Qué es |
|---|---|
| `cli_perfil.txt` | salida completa de `cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance perfil` |
| `memoria_perfil.html` | la memoria HTML de **esa misma** corrida |
| `regenerar.sh` | el comando exacto **y la normalización**. Se corre desde la raíz |

**Está normalizada, y no es cosmética.** Corrida cruda, la salida **no es reproducible**:
C0 la generó dos veces seguidas y difería. Tres campos, medidos:

1. `generado (UTC): <iso>` en la salida de la CLI.
2. `corrida UTC: <iso>` y la misma fecha en formato local, en el HTML.
3. **`Fecha de criterios_adoptados.py`** en el HTML, que `M11_reporte` saca de
   `ruta.stat().st_mtime`. **Éste es el que importa:** no cambia por corrida sino por
   **CLON** — en un checkout nuevo es la hora del clon —, de modo que el diff de C1 daría
   rojo en otra máquina con el código idéntico. Sin retirarlo, la línea base no sirve para
   lo único para lo que existe.

Los patrones de la normalización son específicos a propósito: un barrido de fechas genérico
pisaría texto normativo. Medido: en el HTML hay **tres** fechas y las tres son volátiles.

Con eso, el criterio de salida de C1 deja de ser «diff vacío salvo marcas de tiempo» y pasa
a ser **diff vacío**, que es comprobable.

### 16.2 Los cuatro puntos de prompt que CP añadió

| Punto | Sesión | Qué cubre de §15.8 | Por qué hacía falta |
|---|---|---|---|
| **P-1** | **C2**, puntos 3 y 4 nuevos | `D-6`, `R-1`, `R-2`, `R-3`, `R-4`, `R-7` | **Era bloqueante y está medido.** El prompt de C2 nombraba solo las Tablas A.1 y C.2, y **ninguna** de las seis citas que §15.7 exige. Sin ellas, `F3.TIPO_MARCO`, `F3.MANTENIMIENTO` y `F3.CELDAS` no se construyen y **C5 se detiene** |
| **P-2** | **C6**, punto 5 nuevo | `D-2`, `R-6` | El riesgo es el **inverso** del habitual: un C6 diligente ve una columna obligatoria sin lector y la conecta, **inventando** el mapeo SUCS → «mala calidad» que la norma no da. El punto existe para decir que NO se cablea, y por qué |
| **P-3** | **C5**, punto 2 | `R-8` | C7 ya resuelve *qué fila* de γ_EV toca al cajón (regla #8); nadie resolvía el **comentario rancio** de `factores_carga_aashto` ni la clave que falta |
| **D-3** | **C5**, punto 4 | `D-3` | La fila V6 de la v8 lleva «[N]» **sin numeral**, sobre una frase que recomienda. Sin el aviso, un `Fundamento` con `verbo=OBLIGA` sobre ella es el error natural |

### 16.3 El manifiesto ancla por línea, y C1 va a mover cientos

`docs/manifiesto_citas.md` referencia el código por **`archivo:línea`**. Es lo contrario de
la regla 4 de `CLAUDE.md` —*anclar por NOMBRE DE SÍMBOLO, nunca por número de línea*— y es
un defecto conocido del propio manifiesto, que **C0 mide y no arregla**: corregir el
esquema de anclaje no es de esta sesión ni de C1.

**Medido sobre `origin/main` `4f6cf69`:**

| | Localizadores |
|---|---|
| **Total en `docs/manifiesto_citas.md`** | **326**, en 19 archivos, que caen dentro de **38 símbolos** |
| En los **tres archivos que C1 reescribe** | **12** — `M4_control` 9, `M3_hidraulica` 2, `modelos` 1 |
| En los **consumidores que C1 arrastra** | **23** — `M5_verificaciones` 13, `M2_material` 4, `M7_geometria` 4, `MD` 1, `M11_reporte` 1 |
| Símbolos **del censo de §2-bis** que llevan uno | **6** — marcados «SÍ» en su columna (d) |

**Regeneración:** `python3 -m src.normativa.manifiesto --escribir`. Vuelve a calcular los
326 localizadores desde el árbol; el contenido del manifiesto no cambia, solo los números.

**Y va en COMMIT APARTE del refactor** (punto 5 de C1). No es orden por gusto: juntos, un
rojo de `test_manifiesto_citas.py` no se puede atribuir — puede ser el anclaje corrido o
puede ser un número que se movió, y el criterio de salida de C1 depende entero de poder
separar esas dos cosas. **CP lo topó con tres ediciones de docstring**: rompió cuatro tests
y hubo que regenerar 12 localizadores.
### 16.4 C1 — lo que se midió, lo que se decidió y lo que quedó anotado

**El criterio de salida se cumplió, y no de vista.** Diff contra la línea base normalizada
de C0, por su propio `regenerar.sh`: **vacío**, en la salida de la CLI y en el HTML de la
memoria. `tests/fixtures/casos_patron.py` verde **sin tocar un solo valor esperado**. Par
de la suite `1536 passed / 2 skipped`, `collected 1538`, configuración «PyMuPDF sí /
ventana Tk no» — el par de C0, sin mover.

**La traza de memoria se comparó campo por campo, no de vista** (punto 6 del prompt).
Sonda propia: los cinco `PasoDeMemoria` que emite `M4_control._pasos_hidraulicos` sobre
una malla de 5 diámetros × 4 caudales × 3 pendientes × 3 TW = **180 combinaciones**,
volcando de cada paso `codigo`, `fase`, `que`, `por_que`, `formula`, `formula_cita_id`,
`fundamento_id`, `nota_del_proyecto`, el `Umbral` entero con su `cita_id` y su `caracter`,
y **cada `Magnitud` con su valor en hexadecimal exacto** (`float.hex`), contra un
*worktree* de `8d5e54b`. Resultado: **12 564 líneas idénticas, `cmp` limpio**.

De las 180, **144 producen los cinco pasos (720 en total) y 36 no llegan a producirlos**:
son las ramas `None` de `resolver_manning` y las excepciones de diseño. El volcado las
registra con su causa y **también entraron en la comparación**, así que la cobertura no
las pierde — pero la primera redacción de esta sección escribió «144 combinaciones» donde
la malla tiene 180, sin decir que 36 caían ni por qué. Corregido. De los 720 pasos, 144
llevan `Umbral` real —el de `h_o`, `HDS5_3ED.3.3.3#HO_1_2D`— y también coincide. El
hexadecimal importa: `pytest.approx` habría aprobado una deriva de 1e-12, que es
exactamente la que este refactor podía introducir.

**Por qué no se movió nada — con la salvedad que la auditoría encontró.** La regla general
es que cada sustitución es un renombre con el mismo árbol de expresión:
`SeccionCircular.altura` es `return self.D`, y `_area_en_theta`, `_perimetro_en_theta`,
`_tirante_en_theta`, `area_llena`, `radio_hidraulico_lleno`, `ancho_superficial_en_llenado`
y `bracket_llenado` conservan operandos, paréntesis y orden. Brent recibe la misma `f` y el
mismo bracket, luego la misma sucesión de iterados y la misma raíz.

**Pero «renombre con el mismo árbol» es falso para tres funciones, y conviene decirlo
porque se escribió aquí como si fuera universal.** `M3.area`, `M3.perimetro` y `M3.tirante`
ya no evalúan su fórmula: devuelven un campo de `seccion.geometria_en(llenado)`, que
construye la `Geometria` entera y con ella el `R = A/P`. Donde antes había una
multiplicación ahora hay una **división**, y en `llenado = 0` eso es `ZeroDivisionError`
donde antes salía `0.0`. **No es alcanzable desde producción** —el bracket arranca en
`TOL_THETA_BORDE` y `M3.geometria` ya dividía igual antes de C1—, y ningún número se
movió; pero `ZeroDivisionError` no desciende de `ErrorProyecto`, de modo que es un modo de
fallo nuevo de esas tres funciones. **Queda anotado y no corregido**: evitarlo pide tres
miembros nuevos en el protocolo `Seccion`, y reestructurar el protocolo al cierre de la
sesión de mayor riesgo del plan arriesga más de lo que arregla. La nota completa está en
el comentario de las tres funciones en `M3_hidraulica`.

#### Las cuatro anotaciones (punto 9: se anota y se sigue)

| # | Qué | Dónde se ve | Por qué no se corrige aquí |
|---|---|---|---|
| **A-1** | `M4_control.perdida_carga` está en la lista de migración del punto 3 del prompt y **no recibe ningún diámetro**: le llega la `R` ya calculada. No se migró | `M4_control.perdida_carga(V, R, n, L, ke)` | No hay nada que migrar. La lista del prompt quedó **desactualizada respecto del propio §2-bis de C0**, que ya lo había medido |
| **A-2** | §4.1 y el punto 2 del prompt dicen que `y_sobre_D` «lo consumen `M5.v1_borde_libre`, `M11._tabla_diseno` y **las dos plantillas de `src/plantillas/`**». Medido: **0 apariciones** en las dos plantillas, y `M5.v1_borde_libre` **no consume la propiedad** — recalcula `resultado.y_normal / D` por su cuenta | `src/plantillas/memoria_perfil.html`, `src/plantillas/memoria_alcantarillas.html`, `M5_verificaciones.v1_borde_libre:447` | El nombre **se conservó igual**, que era la instrucción; lo inexacto es la razón, no la orden. Los consumidores reales de `Geometria.y_sobre_D` son **los tests del motor**; al reporte el número viaja por `ResultadoPunto.y_sobre_D`, que es otra expresión |
| **A-3** | El mismo `h_o` geométrico está escrito **dos veces**: `control_salida` lo calcula en `h_o_geometrico` y `_pasos_hidraulicos` lo vuelve a calcular para su `Magnitud("(y_c + D)/2", ...)`. `ControlSalida` no lo expone, y por eso el emisor lo repite | `M4_control.control_salida` (`h_o_geometrico`) y `M4_control._pasos_hidraulicos` (`Magnitud("(y_c + D)/2", ...)`) | **Es anterior a C1** —ya estaba escrito dos veces con `D` suelto— y arreglarlo movería la traza. Es la regla «M11 no hace aritmética sobre magnitudes» incumplida **del lado del emisor**: dos expresiones que hay que editar juntas para siempre, y solo una bajo los tests numéricos |
| **A-4** | `DatoInvalidoError.campo` **se imprime** —M11 lo pinta en la memoria y la CLI lo publica en el JSON—, de modo que renombrarlo a `"altura"` habría sido mover salida. C1b lo había renombrado en M3; **C1c lo devolvió a `"D"`** | Los dos sitios que lo levantan: `M3_hidraulica._validar_parametros` y `M4_control._validar_Q_D` (que llama a `_validar_positivo`). Los dos tests que lo pinean: `test_M3_hidraulica.test_parametros_invalidos_lanzan_dato_invalido` y `test_M4_control.test_tirante_critico_valida_sus_parametros`. Los dos impresores: `M11_reporte` (memoria) y `cli.py` (JSON) | Renombrarlo es una **corrección de vocabulario**, y C1 no corrige. **Queda para C4**, que es la primera sesión en que `"D"` es falso —una `SeccionRectangular` no tiene diámetro— y la única que puede elegir el nombre viendo las dos formas a la vez. Si C4 lo renombra, mueve salida: tiene que decirlo y no puede escudarse en el diff vacío de la línea base, que **no cubre las ramas de error** |

#### El arma cargada que C1 deja: **regla vinculante #12** de §6

`Seccion` expone **dos parametrizaciones** y no son intercambiables. Está desarrollado en
la **regla #12**, que es donde lo va a leer C4; aquí queda solo lo que C1 midió y la
corrección de una cifra propia.

**Primero la corrección, porque la cifra que esta sección publicó era falsa.** El primer
cierre de C1 escribió «divergencia relativa máxima A 5.4e-12, P 4.7e-12, T 9.3e-11 sobre
15 992 puntos» y **eso no es una cota**: es un artefacto de la grilla. Al afinarla, el
máximo **crece** —2.0e-8 en A y 5.3e-8 en P sobre 800 016 puntos—, porque no se trata de
una deriva de últimos bits sino de un **problema de condicionamiento** que se concentra en
los dos extremos del llenado. La pista estaba a la vista y no se leyó: un mapa previo del
refactor había medido A 2.1e-11 sobre otra grilla, y **dos grillas que dan máximos
distintos son la definición de que no hay cota**. Publicar un número suelto como si la
hubiera es exactamente el defecto que la regla #11 denuncia — una cifra sin su condición.

**Lo que sí se sostiene, por tramos** (8 diámetros de 0.30 a 3.00 m; las filas de rango
sobre 20 000 ángulos repartidos en `bracket_llenado()`):

| Dónde | Divergencia relativa máxima |
|---|---|
| `y/D` ∈ [0.10, 0.75] — la ventana que V1 admite | A 9.7e-16 · P 3.9e-16 · T 4.0e-16 |
| `y/D` ∈ [0.01, 0.99] | A 5.2e-15 · P 1.5e-15 · T 8.8e-15 |
| θ = 1e-6 rad | P y T: 4.4e-5 |
| **Extremo INFERIOR de `bracket_llenado()`** | **100 %: la vía por tirante devuelve `0.0` exacto para P y T** |
| **Extremo SUPERIOR** *(medido por C4)* | T ~100 % relativo y **no** cero exacto; **P: 1.6e-10** — no se anula. Ver la corrección en §6 #12 |

**Y la consecuencia es peor que una deriva.** `T` es el denominador de `A^3/T` en
`M4_control._residuo_critico`. Quien reescriba el residuo sobre
`seccion.ancho_superficial(y)` no mete un 1e-12: **divide por cero en el extremo inferior
del bracket**, que es de los primeros puntos donde Brent evalúa, reintroduciendo la clase
de fallo que `SIS-G-02` cerró.

En el centro del rango las dos vías **coinciden bit a bit** (θ = π: divergencia 0.0 exacta
en las tres magnitudes). Por eso es regla vinculante y no comentario: **no se detecta
mirando, y una comprobación puntual la aprueba**. El aviso, con la medición, está también
en el docstring de `modelos.Seccion`, que es donde lo lee quien esté a punto de hacerlo.

#### La auditoría adversarial del cierre, y lo que le encontró a C1

Se invocó `auditor-adversarial` sobre los cinco commits, con el encargo de refutar ocho
afirmaciones concretas de esta misma sección. **De las ocho, una salió limpia (el censo de
literales), dos quedaron refutadas y cinco ajustadas.** Todo lo de arriba ya está
corregido con lo que encontró. Lo que importa registrar:

**La refutación que valía la sesión entera: C1 movió salida impresa y no se dio cuenta.**
El revert de A-4 devolvió a `"D"` el **campo** de `DatoInvalidoError` y **dejó renombrado
el motivo** —de «el diametro debe ser positivo» a «la altura interior de la seccion debe
ser positiva»—. Los dos viajan juntos dentro de `str(exc)`, que `cli._bloqueo` guarda como
`mensaje`, `cli._bloqueo_json` publica y `M11._tabla_bloqueos` pinta: exactamente los tres
sitios que el propio argumento de A-4 invocaba para el campo. Es alcanzable con **un solo
argumento de CLI** —`--declarar 'diametros_normalizados={"inicio": -0.90, "paso": 0.15}'`—
y da **12 apariciones en el JSON y una en el HTML**. Y el resultado era peor que cualquiera
de las dos opciones puras: `campo: D` pegado a una frase que habla de «la altura interior
de la sección», dos vocabularios para el mismo dato en la misma línea. **Corregido**: la
rama de error ahora es idéntica a `8d5e54b`, verificada con `diff` de las dos corridas.

**Por qué la suite no lo vio, que es la lección reutilizable.** El test que cubre esa rama
comprobaba `exc.value.campo` **y no `exc.value.motivo`**. Un test que pinea la mitad de una
cadena impresa no defiende la cadena. Los dos tests
(`test_M3_hidraulica.test_parametros_invalidos_lanzan_dato_invalido` y
`test_M4_control.test_tirante_critico_valida_sus_parametros`) ahora comprueban las dos
mitades, con la razón escrita encima.

**Y por qué la línea base tampoco lo vio.** `regenerar.sh` genera el `--json` en un
temporal y **lo tira**; no genera el `--csv-resumen`; no corre `--alcance expediente`; y de
los 4 puntos de `tests/ejemplo_puntos.csv` **solo 1 llega a dimensionarse**. El diff vacío
es real, pero la ventana por la que mira es más estrecha de lo que esta sección daba a
entender, y **la rama de error no entra en ella en absoluto**: hace falta un `--declarar`
para llegar. La auditoría cerró esos huecos por su cuenta —los 3 CSV de `tests/`, × los dos
alcances, × `cli.txt` + `informe.json` + `memoria.html` + `resumen.csv`, contra un worktree
de la base— y **no encontró más movimiento**; y barrió además el régimen de transición
(`3.5 < q* < 4.0`), el sumergido, `h_o_fuera_de_rango`, `DisenoNoFactibleError` y
`LimiteNumericoError`, todos idénticos. **Ensanchar la línea base es trabajo de C4**, que
la va a usar con el mismo criterio de salida y con una forma más que verificar.

**Las demás, corregidas en el sitio que les toca:**

| Qué | Dónde quedó |
|---|---|
| Tres símbolos nuevos sin consumidor y sin ficha —la mitad por tirante de `Seccion`, `SeccionCircular.etiqueta` y `Geometria.y_sobre_D`—, más `M3.tirante`, que se quedó huérfana | **Parte V nueva de `docs/decisiones_diferidas.md`** (`C1-01` a `C1-04`). Lo exige `CLAUDE.md` para todo objeto conservado sin consumidor, y `tests/test_decisiones_diferidas.py` ya las vigila |
| El comentario de `M3.area/perimetro/tirante` decía que las tres son «la API pública que la suite contrasta contra `geometria()`». La suite contrasta **dos**; `tirante` no la llama nadie | Corregido y medido en el propio comentario. Es el antipatrón de «predecir un consumidor que no existe», que el repositorio ya tiene fichado |
| Dos referencias cruzadas que C1 dejó rancias: `M7_geometria` y `M2_material` mandaban a `modelos.Geometria` por cosas que se mudaron a `SeccionCircular` | Reapuntadas. Es el patrón `FACTOR_MURO_TABLA`: prosa que ningún barrido vigila |
| `SeccionCircular.etiqueta()` devolvía `"D 0.90 m"`; la §4.1 especifica `"Ø 0.90 m"` | Corregido. Era código nuevo que no cumplía la especificación desde la que se escribió |
| El mensaje del commit `f99764a` dice «10 localizadores en 3 archivos». El recuento real —conjunto de localizadores antes y después, no líneas del diff— es **11 ocurrencias en 4 archivos**: `M4_control` 7, `M3_hidraulica` 2, `MD` 1 y **`modelos.py` 1, que el mensaje omitía** | Corregido aquí. El commit está empujado y no se reescribe: el número bueno es éste |
| `M8_estructural` codifica geometría circular en producción (`(math.pi/4)·D_ext²` de la flotación, y el prisma de relleno de ancho `D_ext`) y **no figura en el censo de 59 símbolos de §2-bis**, que se presenta como el barrido completo de `src/`, `cli.py` y `gui/` | **Anotado, no corregido.** Es defecto del censo de C0, y §5 ya asigna esos símbolos al frente **F4**. Quien ejecute F4 no puede fiarse de que §2-bis sea exhaustivo |
| `_validar_parametros` conserva `if seccion.altura <= 0` en vez de la forma `not A > 0` que `CLAUDE.md` fija desde MAT-D13 (un `nan` la atraviesa) | **Anotado, no corregido**: es anterior a C1 y cambiarlo mueve el comportamiento de una rama de error |

#### Sobre la cláusula normativa de §9-bis

C1 **no tocó ni creó ningún valor `[N]` ni `[N→]`**, no aplicó ningún procedimiento al
marco, no añadió ninguna función de cálculo y no declaró ningún criterio nuevo: es un
refactor de tipos cuyo criterio de éxito es que la salida no se mueva, y no se movió. Por
eso no hubo cita que pasar por `verificador-normativo`, y por eso **no hay defecto nuevo
contra la v8 que sumar a §15.8**: los ocho (`D-1`…`D-8`) siguen siendo los de CN, sin
alta ni baja.
| **C3** | `df2edac` · `396a9b7` · `17d36ba` · `a9e9028` · `C3d` · `C3e` · PR #8 | **1554 p / 2 s**, «PyMuPDF sí / Tk no» | La **Forma 2** de HDS-5 implementada: `M4._hw_sobre_D_no_sumergido` bifurca por `hds5.forma`; el paso de memoria que dice **qué forma se usó y por qué**, con `F4.FORMA_HDS5`; casos patrón `CP5D_*` calculados a mano; y la **línea base ensanchada a 12 archivos** (JSON, CSV, expediente, rama de error, 3 de 4 puntos dimensionados) | La transición bajo Forma 2 **decrece con el caudal** para S > 0.2365 — declarada, no corregida: corregirla es sustituir el criterio `metodo_transicion_hds5`. **D-10** nuevo y **D-9** corregido contra la v8. `R-11` (pág. A.8 inferida) y `R-12` (elisión sin marcar) anotados |


| **C3.5** | `3050af8` · `e6e408c` · merge `7507991` | **1558 p / 2 s** (collected 1560), «PyMuPDF sí / Tk no» — **leído de `origin/main` en checkout limpio**, no del clon local | Dos correcciones de raíz pedidas al cerrar C3: la **regla vinculante #5** reenunciada con la medición de la Tabla A.1, y su origen corregido en `citas.py`; y **`tests/test_linea_base.py`**, que hace que la ventana deje de depender de que alguien corra el script | El límite de la ventana, **declarado y medido**: no ve cablear `forma = 1` porque ningún punto del fixture usa Forma 2 todavía. Lo cazan los tests unitarios; se vuelve visible aquí cuando C4 meta un cajón |
### 16.5 C2 — lo que se transcribió, lo que se corrigió y lo que se anotó

**El gate de entorno se comprobó antes de transcribir nada, y no es formalismo.** PyMuPDF
1.28.2 presente y `tests/test_normativa_pdf.py` corriendo **completo: 32 passed, ninguno
saltado**. Sin él, T2, T3, T5 y T6 se saltan en bloque y las 22 filas y 7 citas de esta
sesión habrían entrado **sin que nada las contrastara contra el PDF** — que es exactamente
la clase de defecto que el registro normativo existe para impedir.

#### Lo que la fuente primaria corrigió del repositorio y del propio plan

Cinco cosas, todas verificadas contra el PDF por `verificador-normativo` antes de
escribirlas:

| Qué decía | Qué dice la fuente | Dónde estaba |
|---|---|---|
| La Tabla A.1 «cubre todas las cartas del Apéndice C — cajón, **elíptica, arco, pipe-arch, long span**» y esas quedan fuera | Censadas sus **36 filas de datos**, la Tabla A.1 **no tiene ni una fila** de pipe-arch, arco ni long span —viven en las Tablas A.2 y A.4—, y **sí tiene 23 de cajón rectangular de concreto**. Las dos mitades de la frase estaban al revés | `T_HDS5_A1.alcance` |
| El bloque «Box, Reinforced Concrete» tiene **once filas** | **Siete** con coeficiente, bajo **cuatro rótulos de agrupación**. Once es el número de *líneas* | `T_HDS5_C2.alcance` |
| §15.7 sitúa `HDS5_3ED.A.3#FORMAS` en la página **«A.3»** | **A.3 es el numeral**; la página impresa es **A.2** (PDF 191), porque el numeral abre al pie de la anterior. Es la confusión numeral/folio que `NOR-HDS-01` ya cerró una vez | §15.7, tabla de citas |
| §15.7 propone citar `#MULTIPLES` como *«…recomendándose utilizar obras con mayor sección transversal libre, sin subdivisiones.»* | Es una **elisión sin marcar** bajo el rótulo «texto literal» — el defecto que `CLAUDE.md` nombra a propósito de la tercera condición de `h_o` — y además el recorte se lee como preferencia **general** por la celda única, cuando la recomendación está **condicionada** al supuesto de multicelda en cauce con arrastre. Se cita la oración entera | §15.7, y ahora `citas.CAJON_MULTIPLES` |
| La Tabla A.1 está en la **pág. impresa A.8** | **Esa página no lleva folio impreso**: las cuatro páginas apaisadas de tablas del apéndice (PDF 197–200) van sin numerar. «A.8» es una **inferencia por secuencia**, correcta y predicha por la regla de paginación, pero no una lectura. **Anotado, no corregido**: `pagina_impresa` es un campo que T6 usa | `citas.HDS5_TA1.nota` |

**Y una errata de la fuente que explica la primera fila de esa tabla**: el num. A.3.1 del
propio HDS-5 dice *«From Table A.1, Chart 34, Scale 3»*, y la carta 34 —*Pipe Arch CM*—
está en la **Tabla A.2** en esta 3.ª edición. Es una remisión no actualizada al reorganizar
el apéndice, hermana de `DIS-HDS5-APENDICE-G`. Queda **anotada en la nota de la cita y sin
ID propio**: abrir una `Discrepancia` nueva no era trabajo de C2.

#### Dos tests corregidos porque afirmaban algo falso, no para que pasaran

- **T21** (`test_T21_los_verbatim_del_registro_conservan_sus_diacriticos`) se declaraba a sí
  mismo *«la única forma barata que no da falsos positivos»*. Da uno: la frase del
  num. 4.1.1.3.7 d) tiene **133 caracteres y ni una sola tilde en la fuente**. Queda exenta
  **con su verificación escrita en el propio código**, no con una etiqueta. La guardia no se
  afloja: T2 sigue comprobando que el texto aparezca en su página, y lo que T21 añade —que
  la comparación de T2 normaliza sin diacríticos y por tanto aceptaría un verbatim
  de-acentuado— sigue en pie para todas las demás.
- El **rótulo de completitud** de la Tabla Nº 09 pasa de «2 de 4 filas» a «2 de 5». El
  rótulo lo **deriva la tabla de sus campos**; el número del test era la copia vieja.

#### Los ocho `Fundamento` de §15.7: construibles, y medido

Comprobado sobre el registro construido, cita por cita y verbo por verbo (no de vista):
**los ocho tienen todas sus citas en el registro y todos los verbos quedan sostenidos** por
el `caracter` de al menos una, que es lo que T11 exige.

| Escritos por C2 | Pendientes, y de quién |
|---|---|
| `F3.TIPO_MARCO`, `F3.MANTENIMIENTO`, `F3.CELDAS`, `F4.FORMA_HDS5` | `F4.SECCION`, `F4.YC_RECT` (**C4**) · `F3.SECCION_CANAL`, `F4.N_CAJON` (**C5**) |

**Por qué C2 escribió cuatro y no cero, que era lo que el alcance sugería:** `T4` del
registro rechaza una cita que nadie referencia. Transcribir `MC_HHD.4.1.1.3.7d`,
`MC_HHD.LAMINA_03` y `HDS5_3ED.A.3#FORMAS` **sin su consumidor deja el registro en rojo**.
Los otros cuatro no se escriben porque sus citas ya existían y no crean ninguna huérfana:
su sitio es la sesión que escribe el paso que los emite.

**Y quedan declarados como inalcanzables**, en `tests/test_memoria_sustentada.py`, con una
razón distinta de la de los que ya estaban ahí: aquéllos no se alcanzan porque al expediente
le falta un dato; **éstos porque el paso que los emitiría todavía no existe**. Salen de esa
lista en cuanto C4 y C5 escriban los pasos; **si en esas sesiones siguen ahí, es que el paso
se escribió sin su fundamento**.

#### Qué se movió en la salida, y por qué está bien

La línea base de la Familia C cambia en **dos líneas, y ninguna es un número de cálculo**:
el SHA-1 de `criterios_adoptados.py` —que cambió— y el criterio `hds5_embocadura_hdpe`, que
pasa a imprimir **`forma = 1`** junto a sus K, M, c, Y y Ks. Lo segundo **es el efecto
buscado**: el contrato de memoria de §4.5 exige que nada de lo que se añade quede invisible
en el reporte, y la forma de ecuación es justamente lo que un revisor necesita para poder
rehacer el número. HW, tirantes y velocidades no se mueven.

#### Anotado y no corregido (punto 8 del prompt)

- **`ke_entrada` sigue valiendo 0.5, tomado del bloque «Pipe, Concrete»**, fila
  «Square-edge» bajo el rótulo «Headwall or headwall and wingwalls». Con un cajón ese valor
  no corresponde, y lo que lo hace peligroso es que el bloque Box **tiene una fila que
  coincide en valor** —«Square-edged on 3 edges», también 0.5—: el número saldría igual y la
  cita sería falsa. **Abrirlo por forma es de C5** (regla vinculante #11). C2 solo transcribe,
  y lo deja escrito en el propio objeto.
- **La «pág. impresa A.8»** de la Tabla A.1 es inferida y no leída (arriba).
- **La remisión rancia del num. A.3.1** del propio HDS-5 (arriba).

#### Lo que la auditoría adversarial refutó, y estaba todo en pie

Se invocó `auditor-adversarial` sobre los commits de C2 con el encargo de refutar nueve
afirmaciones. **Cinco confirmadas, cuatro ajustadas, y cuatro refutaciones concretas — las
cuatro reales**, verificadas contra el PDF antes de corregir nada.

**La que podía mover un número, y es la lección de la sesión.** El docstring de
`ConstantesHDS5` escribía la Forma 2 como `HWi/D = K·(q*)^M + Ks·S` **y se contradecía a sí
mismo once líneas más abajo**, donde ya decía que la Forma 2 no lleva ese término. La ec.
(A.2), pág. impresa A.2 / PDF 191, es `HWi/D = K[Ku·Q/(A·D^0.5)]^M` y nada más; el contraste
está en la misma página, porque la ec. (A.3) sumergida **sí** extrae `+ Y + Ks·S`. Medido el
daño sobre la Carta 9 escala 1, cajón 2.00 × 2.00 m, `Q = 8 m³/s`, `S = 0.03`: **1.910 m
contra 1.880 m — 30 mm menos de carga, del lado no conservador**, creciendo lineal con la
pendiente. Es **exactamente el fallo que `F4.FORMA_HDS5` describe**, escrito por error en el
archivo que C3 abre primero. El campo `forma` se justificó como «la guardia», y la guardia
traía la fórmula mal transcrita dentro.

**La segunda decía una cosa y el programa hacía otra.** `#MARCO` declaraba `ADVIERTE` y en
ejecución **bloqueaba**: resolvía por `PorDatoDeSitio(clave="sucs_fundacion")` con el
comentario «la clave existe y hoy no tiene valor», y **las dos mitades eran falsas** —
`sucs_fundacion` no está en `datos_sitio`, es **columna del CSV**, porque varía punto a
punto—. `disponibilidad_de` corta por la rama «la clave no está en datos_sitio» **antes** de
mirar el efecto, de modo que la `justificacion_de_no_bloquear` que T15 obliga a escribir era
texto muerto y la ventana mandaba al revisor al archivo equivocado. Pasa a `NoEvaluable`,
que es lo que la condición dice de verdad: **el Manual no define «mala calidad»**.

**Las otras dos eran de explicación, no de valor.** El comentario de `afinado` aplicaba el
corrimiento de la errata **al revés** —la lectura literal a la altura de ese rótulo es
0.013/0.015/0.017, no lo que decía—, y el valor transcrito seguía siendo el correcto; y
`LAMINA_03` prometía que la segunda mitad del cajetín «viaja como `texto_previo`», campo que
`Cita` **no tiene**. La razón verdadera del recorte es otra y ahora está escrita: T3 busca
`titulo_numeral` en la capa de texto, que entrega los dos renglones como corridas
independientes y en orden inverso. **Es una limitación de la maquinaria, no una decisión de
lectura**, y §15.4 tiene razón al dar el título entero.

Y tres apuntes menores, corregidos: la `razon` del `Acotada` de la Tabla A.1 describía una
correspondencia fila↔material que no existe (el HDPE no tiene fila); la afirmación sobre la
**codificación** del grado era imprecisa —lo que es cero volado es el glifo *impreso*; la
capa de texto entrega un `0` ASCII—; y las siete filas de la Tabla C.2 colgaban de una
condición cuya evidencia era un `Verbatim` **de otra tabla y otra página**. Ahora tienen la
suya, anclada a la cita de la C.2.

#### Sobre la cláusula normativa de §9-bis

Los valores `[N]` que C2 crea son las 22 filas nuevas de las Tablas A.1 y C.2 más la fila
`afinado`. **Los tres lotes pasaron por `verificador-normativo` antes de aceptarse**, columna
por columna, y su informe corrigió cinco cosas —las de la tabla de arriba—. Ningún
procedimiento se aplicó al marco en esta sesión: C2 transcribe, y quien aplique tiene que
citar el numeral que §15 le asigna. Toda cita nueva entra por `Registro.textos_literales()`;
ninguna se copió a mano a un docstring.

### 16.6 C3 — la Forma 2, y lo que la auditoría encontró en ella

**El punto 0 fue primero y en su propio commit**, que era la instrucción y también la
lección de C1 y C2: la ventana con que se comprueba «no se movió nada» tiene que ser ancha
**antes** del cambio, o no prueba nada. Pasó de mirar una corrida a mirar **12 archivos** —
JSON, CSV de resumen, alcance expediente, rama de error, y de **1 a 3** puntos
dimensionados, con C-01 llegando a su bloqueo real—. Los dos archivos de C0 se conservan y
**se reprodujeron byte a byte** antes de tocar M4.

**La ecuación se verificó en la fuente, no en lo que dijo C2** — y con razón, porque C2 la
había escrito mal. La (A.2) es `HWi/D = K[Ku·Q/(A·D^0.5)]^M` y ahí termina; la sumergida
(A.3) es una sola, común a las dos formas.

#### Lo que la auditoría refutó, y era todo cierto

**La grave: el defecto de esta sesión se había mudado del docstring al reporte.** Bajo
Forma 2, el paso del control de entrada **imprimía la ec. (A.1) entera** —con su `H_c/D` y
su `Ks·S`— y metía `Ks` en la sustitución, para explicar un número salido de la (A.2). Y el
paso nuevo, dos líneas antes, **prometía por escrito que eso no pasaba**. Corregido: la
fórmula y la sustitución dependen ahora de la rama.

**El paso nuevo era el único bloque de la sesión sin cobertura.** Quitarlo del `return`
rompía un test, pero **cablear `forma = 1` dentro de él dejaba la suite en verde**, igual
que invertir la etiqueta de ecuación, igual que escribir «La Forma 2 SÍ lleva `Ks·S`» en su
nota. El paso que existe para que el defecto no vuelva sin auditor era, él mismo, invisible
a la suite. Cuatro tests nuevos matan las tres mutaciones.

**El num. A.3 no prohíbe cruzar coeficientes entre formas de ecuación, y yo lo escribí en
tres sitios.** Prohíbe cruzarlos entre **formas geométricas**. Y la Tabla A.1 lo zanja sola:
medido sobre sus 36 filas, **forma y geometría son ortogonales** — «Rect. Box Concrete»
aparece con Forma 1 y con Forma 2, y «Circular» también—. Una prohibición sobre geometrías
no puede ser la regla que separa las formas, porque la misma geometría vive en las dos.
Quien lo dice es la **columna «Equation Form»**, fila por fila. Uno de los tres sitios era
el docstring que yo había declarado «releído entero».

**Y el eje que motivaba el ensanche era el único que no ensanché**: C3a invoca que «la rama
de error necesita un `--declarar`», y las tres corridas nuevas usaban `--datos-externos`.
Añadida una cuarta con el comando exacto de la regresión de C1: la cadena
`Dato invalido en 'D': el diametro debe ser positivo` aparece ahora **3 veces en el CLI y
12 en el JSON**.

#### La propiedad que se declara y no se corrige

**Bajo Forma 2, la transición decrece con el caudal para `S > 0.236495 m/m`.** Con Forma 1
los dos extremos de la recta llevan `Ks·S` y el término se cancela en la diferencia; con
Forma 2 el extremo inferior lo pierde. Con `D = 0.90` y `S = 0.30`, un `q*` de 3.50 da
1.0585 m y uno de 4.00 da 1.0300 m: **28.6 mm menos de carga con 14 % más de caudal**, del
lado no conservador, y **ninguna guardia lo atrapa** porque el número es positivo.

No se corrige: sale de combinar la (A.2), la (A.3) y la recta del criterio `[C]`
`metodo_transicion_hds5`, y sustituir ese método no es de esta sesión. Se **declara**, con
caso patrón y test que fijan las dos mitades del umbral.

#### Lo que queda anotado y no corregido

- **La ventana sigue sin mirar** el código de salida (los cuatro comandos llevan `|| true`),
  `--pdf`, `--criterios`, y **ningún test la consume**: solo «mira» si alguien corre el
  script a mano. La auditoría lo demostró — una mutación que cambiaba la etiqueta de
  ecuación impresa en las tres memorias dejaba la suite verde.
- **La memoria generada no lleva la advertencia de fixture**: quien abra
  `memoria_perfil_ancha.html` suelto ve una memoria completa con TW = 0.300 m y nada que
  diga que es una sonda.
- **`R-11`** (la pág. impresa A.8, que no está impresa) y **`R-12`** (la elisión final sin
  marcar en el `Verbatim` de la zona de transición), en §15.8.
- La confusión «num. A.3 separa las formas» **nace antes de C3**: está en la `nota` de la
  cita `HDS5_3ED.A.3#FORMAS` que escribió C2 y en la **regla vinculante #5** de §6. C3
  corrigió sus tres sitios; **los dos anteriores siguen mal** y hay que corregirlos donde
  viven.

#### Sobre la cláusula normativa de §9-bis

Los valores `[N]` que C3 toca son las dos ecuaciones y los dos límites de rama.
**Pasaron por `verificador-normativo` antes de aceptarse**, punto por punto, y su informe
confirmó los ocho: numeral, título, páginas impresa y PDF, y el texto de cada ecuación. De
paso corrigió el defecto **D-9** que C2 había registrado contra la v8.

### 16.7 C3.5 — las dos correcciones de raíz

**Entregada en `origin/main` = `7507991`**, con los tres punteros coincidiendo: `main` y
`origin/main` en `7507991`, y la rama en `e6e408c`, **contenida en `main`** (cero commits
fuera), de modo que no queda PR abierto ni haría falta: uno de C3.5 tendría el diff vacío.

**El par, leído de un checkout limpio de `origin/main` y no del clon local:** `1558 passed /
2 skipped`, `collected 1560`, configuración «PyMuPDF sí / ventana Tk no» —
`test_normativa_pdf.py` corrió completo, 32 passed—. Sube 4 respecto de C3 por los cuatro
tests nuevos de `test_linea_base.py`, que **pasan desde el checkout limpio**: era lo que
había que comprobar, porque el test ejecuta el script y podía depender del árbol local.

> **El push falló primero, y conviene que quede escrito.** Al cerrar C3.5 el remoto devolvió
> **403** —«Claude doesn't have GitHub access… for your organization»— y se reintentó cuatro
> veces con espera creciente. No es transitorio: es un permiso. Durante ese rato el trabajo
> estuvo **commiteado y sin entregar**, y se reportó así, con rama y SHA, en vez de darlo por
> cerrado. Es exactamente el caso que la regla de cierre de `CLAUDE.md` anticipa —«si la
> fusión no se puede hacer, eso **no** convierte la tarea en terminada»— y la segunda vez que
> el proyecto lo ejerce.

**La regla vinculante #5 estaba mal enunciada, y es la que C4 y C5 citan.** Decía «no se
cruzan coeficientes entre formas» apoyándose en el num. A.3, y ese numeral prohíbe cruzarlos
entre **formas geométricas**, no entre formas de ecuación. La prueba está en la Tabla A.1,
medida sobre sus 36 filas: **`Rect. Box Concrete` aparece con Forma 1 y con Forma 2, y
`Circular` también**. La misma geometría vive en las dos formas y la misma forma cubre
geometrías distintas; una prohibición sobre geometrías no puede ser la regla que separa las
formas.

La regla reescrita conserva **lo que sí es vinculante y directo para la Familia C** —el
cajón usa una carta *de cajón*, no la circular con otras constantes— y separa los dos ejes
con la tabla de la medición. Corregido también el sitio donde nació: el **comentario** de la
cita `HDS5_3ED.A.3#FORMAS` (no su campo `nota`, que está vacío — al cerrar C3 lo dije mal).
De ahí lo copió C3 a otros tres archivos creyendo que lo verificaba. **Es `NOR-PUE-01` otra
vez**: una cita que dice algo que la fuente no dice, propagada por cuatro archivos.

**La línea base ya no depende de que alguien se acuerde.** `tests/test_linea_base.py` corre
el script contra un destino temporal y compara byte a byte. Para eso `regenerar.sh` admite
ahora un **argumento de destino**: sin él, el test tendría que repetir los cuatro comandos y
habría **dos** definiciones de la línea base que podrían divergir — el defecto que este
repositorio persigue en todas partes—. Con él hay una, y el test la ejecuta.

Cuatro comprobaciones: que la salida comprometida es la que produce el código; que no hay
salidas sin comprometer **ni** comprometidas que ya no se generen; que la corrida es
determinista —sin eso el primero sería intermitente y acabaría desactivado—; y que la
ventana **cubre los ejes que el README dice que cubre**, para que estrecharla rompa un test
en vez de pasar inadvertido, que es como llegó a estar estrecha.

**Y su límite, declarado en vez de tapado.** Medido con tres mutaciones: ve invertir la
etiqueta de ecuación y ve renombrar el `motivo` de un `DatoInvalidoError` —la regresión de
C1—, y **no** ve cablear `forma = 1`, porque hoy ningún punto del fixture usa Forma 2. A ésa
la caza un test unitario. Las dos capas son complementarias y ninguna sustituye a la otra;
**cuando C4 meta un cajón en el fixture, esa mutación se vuelve visible aquí también**.

---

### 16.8 C4 — `SeccionRectangular`, y las tres cosas que la medición corrigió

**Qué se implementó.** `modelos.SeccionRectangular(B, H)` con las dos parametrizaciones del
protocolo, el **tirante crítico cerrado** `y_c = (q²/g)^(1/3)`, y **cuatro** miembros nuevos
en `Seccion` que retiran del motor lo que quedaba de forma cableada. M3 y M4 no ganaron ni
un `isinstance`: la sección responde, el módulo pregunta.

| Miembro nuevo de `Seccion` | Qué retira del módulo |
|---|---|
| `exigir_dimensiones_positivas()` | **dos copias** de la pareja `("D", "el diametro debe ser positivo")`, una en `M3._validar_parametros` y otra en `M4._validar_Q_D`; y con ellas el `"D"` cableado en la validación |
| `magnitudes_de_forma()` | que la memoria supiera que una sección se define con **un** número |
| `formula_geometria()` | la frase «A, P y R son los de la sección circular parcialmente llena», que con un marco además sería falsa |
| `llenado_critico_cerrado(Q, g)` | que M4 tuviera que preguntar de qué forma es la sección para elegir método |

`g` llega **como argumento** y no se importa en `modelos.py`: la sección conoce el álgebra
de su forma, no cuánto vale la gravedad. Es la misma separación que `constantes_fisicas`
declara.

> **Eran cinco, y el quinto se retiró antes de cerrar.** El primer diseño añadía además
> `simbolo_altura` —`"D"` en la circular, `"H"` en el marco—, y al buscarle consumidores
> **no tenía ninguno**: ni en producción, ni en la suite. Lo habían dejado sin trabajo sus
> dos vecinos, `exigir_dimensiones_positivas()` (que ya emite el nombre dentro del mensaje)
> y `magnitudes_de_forma()` (que ya publica los símbolos para la memoria). Un miembro de
> protocolo sin consumidor es exactamente el símbolo colgado que `CLAUDE.md` denuncia en su
> cláusula de taxonomía, y **predecirle un consumidor futuro es el antipatrón que este
> repositorio ya tiene fichado**. Se retiró y su explicación —la distinción entre el `"D"`
> de las ecuaciones de HDS-5, que vale para cualquier forma, y el `"D"` del dato de
> entrada, que significa diámetro— se mudó al docstring de
> `Seccion.exigir_dimensiones_positivas`, que es el miembro que sí lo usa.

#### La trampa de la regla #12, y por qué la medición la corrigió a ella también

La regla se respetó: **M3 y M4 siguen entrando por el parámetro propio**, ningún valor que
un `Geometria` ya trae se recalcula, y el solver de la circular sigue recorriendo θ. Los
tests lo fijan (`test_que_coincidan_en_el_marco_no_las_hace_intercambiables`).

Pero al escribir ese test hubo que medir el enunciado, y **decía de más**: la tabla afirmaba
que «en los **dos** extremos de `bracket_llenado()` la vía por tirante devuelve `0.0` exacto
para P y para T», y eso vale entero **en uno solo**. En el superior `y = D` exactamente, la
inversa devuelve 2π y el **perímetro coincide en los últimos bits**. La consecuencia no
cambia —el cero exacto está en el extremo **inferior**, que es donde Brent evalúa primero, y
`T` es el denominador de `A³/T`—, pero el enunciado sí, y **una regla vinculante que dice de
más se deja de creer entera**. Corregida en §6 #12, en §16.4 y en el docstring de
`modelos.Seccion`, las tres con la medición.

#### El diff de la línea base, línea por línea

Se movieron **tres archivos** —las tres memorias HTML— y **ninguno de los otros nueve**: ni
las cuatro salidas de CLI, ni los tres JSON, ni los dos CSV. Contado sobre bloques `<div
class="paso">` y no sobre líneas, porque el HTML mete un punto entero por línea:

| Qué se movió | Cuántas veces | Por qué |
|---|---|---|
| **Bloque `4.1 — Área, perímetro mojado y radio hidráulico` NUEVO** | 3 por memoria (una por punto dimensionado) | el paso `de_seccion`, que emite `F4.SECCION` |
| Fórmula de `4.1 — Tirante normal` | 3 | decía «resuelta en theta … sección circular parcialmente llena»; ahora el paso de geometría lo dice y éste no lo repite |
| Procedencia de la magnitud `D` en `4.1` y en `4.2.1` | 3 + 3 | la pone la sección (`magnitudes_de_forma`) y ya no dice «diámetro probado por el bucle de diseño» |
| «Por qué se hace» de `4.2.1` | 3 | el paso dejó de tomar prestado `F4.CONTROL` |
| Fórmula de `4.2.1` | 3 | «resuelta en theta» → «sobre el parámetro de llenado de la sección» |
| Nota de `4.2.1` | 3 | se le añadió por qué vía se resolvió |

**Y no se movió ningún número, y eso se midió, no se declaró.** Multiconjunto de todos los
números impresos, antes y después, en las tres memorias: **«sólo en la base: {}»** en las
tres — ninguno desapareció ni cambió de valor —. Lo que aparece son **12 apariciones nuevas
por memoria**, y son exactamente `y`, `A`, `P` y `R` de los tres puntos dimensionados:
números que el cálculo ya tenía y que la memoria no imprimía.

#### El punto de cajón en el fixture, y la mutación que ahora muere

C3.5 dejó el límite escrito: la línea base **no veía** cablear `forma = 1`. C4 añade la
**quinta corrida**, `tests/linea_base_familia_c/punto_cajon.py`, y la ceguera se cierra.

**No pasa por la CLI, y hay que decir por qué:** `MD.disenar_material` construye
`SeccionCircular(D)` sobre la progresión de diámetros de M2, y abrir ese catálogo es **C5**
(punto 11 del prompt). El driver llama a M3 y a M4 con la sección que C4 sí trae. Es un
**fixture** —lleva la advertencia escrita, como `entradas_ampliadas.json`— y toma prestadas
tres decisiones de C5 sólo para poder correr: la fila `concreto_afinado` de la Tabla Nº 09,
la carta `cajon_concreto_aleta_45_d043` y el `ke_entrada` del bloque de tubo (regla #11).

Vueltas a medir las mutaciones sobre este mismo árbol:

| Mutación | Antes de C4 | Ahora |
|---|---|---|
| `forma = FORMA_1` en `_pasos_hidraulicos` (**la etiqueta**) | no movía un byte | **mueve `memoria_punto_cajon.html`** |
| la Forma 2 deja de bifurcar en el **cálculo** | no movía un byte | **HW de entrada 1.576717 m → 3.031241 m** |

El punto: marco 2.00 × 1.50 m, Q = 6.00 m³/s, S = 0.004 m/m, L = 20 m, TW = 0.30 m. Cae
donde se quiere mirar y se dice cuál es cada cosa: **y/H = 0.694** (dentro del 0.75 de V1),
régimen **subcrítico** (y_n = 1.040 m frente a y_c = 0.972 m) y **q\* = 2.957**, o sea la
rama no sumergida — la única en que la ec. (A.2) se aplica pura, sin interpolar —.

#### Lo que se contestó midiendo, y no opinando

**Manning converge en el marco sin tocar el solver** (punto 3). Brent resuelve sobre el
parámetro propio, que aquí es el propio tirante, y devuelve el tirante del caso patrón.
Barrido de 400 tirantes entre 0 y H: **Q(y) es estrictamente creciente, sin pico**. Es una
diferencia con la circular y no un detalle — allí la curva tiene un máximo en y/D = 0.938 y
después baja (MAT-O18) —: en el marco el `None` de `tirante_normal` significa, literalmente,
«no hay tirante que transporte ese caudal en lámina libre».

**Dos cosas que conviene saber del bracket.** No lleva margen de borde —en y = 0 el área
vale 0 pero el perímetro vale B > 0, de modo que R = 0/B está definido, a diferencia de la
circular, donde R = 0/0—; y `TOL_BRENT = 1e-10` se lee aquí **directamente en metros**,
porque el parámetro propio es el tirante (en la circular son radianes, ~1e-11 m sobre un
tubo de 0.90 m).

**Las dos «R» de un marco no son la misma, y en la circular la distinción no se ve.**
`geometria_en(y).R` es de **lámina libre** (P = B + 2y, sin la losa superior);
`radio_hidraulico_lleno` es de **presión** (P = 2(B+H), con ella). En y = H las dos existen
y **no coinciden**: con 2.00 × 1.50 dan **0.600 m y 0.4286 m, un 40 %**. En la circular
convergen —en θ = 2π el ancho de la lámina se anula y el perímetro de lámina libre ya es
πD—, y por eso nadie las había tenido que separar. Cada consumidor usa la suya: Manning la
primera, el control de salida de la Sec. 4.3 la segunda.

**La transición no monótona, sobre las cartas que de verdad son de cajón** (punto 8).
Barridas las **12 cartas de cajón con Forma 2** de la Tabla A.1:

    S* = (c·4² + Y − K·3.5^M) / |Ks|
    mínimo  0.215192 m/m   (cajon_concreto_aleta_18_337_d083)
    máximo  0.493306 m/m   (cajon_concreto_chaflan_aletas_184)

Las **3** cartas de cajón con Forma 1 no tienen umbral: con Forma 1 los dos extremos de la
recta llevan `Ks·S` y el término se cancela en la diferencia. **No muerde en este proyecto**:
la pendiente más alta del expediente de prueba es **0.010 m/m** y la de C-01, 0.004 — el
umbral más bajo está **21 veces** por encima. **Pero no está excluida por ninguna guardia**:
`dominios.S_CAUCE_MAX` vale 1.0, de modo que un CSV válido puede traer una pendiente por
encima del umbral y el cálculo la aceptaría sin decir nada, porque el número sigue siendo
positivo. Queda fijada como caso patrón (`CP5DR_TRANSICION_CAJON`) en vez de darse por
descartada de vista.

**Los CP5D_\* se repiten sobre la rectangular sin cambiar un número** (punto 7), y se
comprobó en vez de suponerse: para cada rama se despeja el B que produce **exactamente** el
q\* del caso y se contrasta el HW/D contra el mismo dorado que C3 calculó a mano. Las tres
ramas coinciden. Y la pareja carta/sección pasa a ser además la correcta: en C3 la Carta 9
—de cajón— se evaluaba sobre una circular como **sonda de la ecuación**, que el num. A.3 no
admitiría como diseño.

#### La anotación A-4, cerrada, y la respuesta no era renombrar

C1 dejó `DatoInvalidoError.campo = "D"` para C4, «la primera sesión en que "D" es falso».
Vistas las dos formas a la vez: **"D" no era falso en la circular**. Un tubo tiene diámetro y
el dato que un revisor corregiría se llama así. Lo falso era **suponer que hay un solo
nombre**. El nombre del dato es una propiedad de la forma, y por eso la validación entera
—campo y motivo— se le pide a la sección: `SeccionCircular` sigue diciendo `"D"` y `"el
diametro debe ser positivo"` **letra por letra** (por eso la rama de error de la línea base
no se movió) y `SeccionRectangular` dice `"B"` y `"H"` con sus propios motivos. De paso
retira una copia: la pareja estaba escrita **dos veces**.

Y con ella se cerró la **tercera anotación de C1**: la condición pasa a estar escrita en
positivo y negada (`not self.D > 0`), plantilla de MAT-D13. Con `<= 0` un NaN se colaba —es
falso frente a los dos operadores— y llegaba hasta Brent, que revienta fuera de
`ErrorProyecto`.

#### Las cuatro guardias del crítico cerrado, con su par medido

La solución cerrada retira la clase de fallos de **convergencia** (SIS-G-02); no retira la
aritmética. Cada guardia lleva umbral **medido**, condición en positivo y negada, y mensaje
que nombra al **par**:

| Qué falla | Par que lo dispara | Dónde está la guardia |
|---|---|---|
| `q ** 2` desborda | q ≥ 1.3407807929942597e+154 (con B = 2.00, Q ≥ 2.68e+154) | `SeccionRectangular.llenado_critico_cerrado` |
| `Q/B` da `inf` **sin excepción** y y_c sale `inf` | Q = 1e308 con B = 1e-5 | ídem |
| `q²/g` se cancela a `0.0` | q ≤ 4.715183354107886e-162 (el primero que deja y_c > 0 es …887e-162, y da y_c = 1.703e-108) | ídem |
| y_c positivo y **A = B·y_c nulo** | B = Q = 5e-324 → y_c = 0.4671363512679737 m, A = 0.0 | `M4._critico_cerrado` — la sección no puede guardarla sola |

#### Los `Fundamento`, y una lista que no era de C4

El prompt daba por hecho que alguno de los cuatro `Fundamento` que C2 dejó en `sin_alcanzar`
era de esta sesión. **Medido: ninguno.** `F4.FORMA_HDS5` salió en C3 y los tres que quedan
—`F3.TIPO_MARCO`, `F3.MANTENIMIENTO`, `F3.CELDAS`— son de **C5**, y sus propios comentarios
lo dicen. Los de C4 son `F4.SECCION` y `F4.YC_RECT`, que **no existían**: C2 los dejó sin
escribir a propósito («su sitio es la sesión que escribe el paso que los emite»). C4 los
escribe con el texto de §15.7 y los emite en **toda** corrida que dimensione un punto, sea
la sección circular o rectangular — que es lo que impide que entren en `sin_alcanzar` por la
puerta de atrás —.

`F4.YC_RECT` pasa a fundar el paso del crítico **también en la circular**, y eso movió la
memoria. No es cosmético: `F4.CONTROL` dice literalmente «Carga a la entrada HW por los dos
controles del HDS-5, entrada y salida, y adopción del mayor» — describe **otro paso**, y el
crítico lo tomaba prestado porque no había uno propio. Queda **anotado** que su `id` es hoy
más estrecho que su uso: se conserva el de §15.7 verbatim en vez de renombrarlo, porque C5
lo cita.

#### Lo que la verificación normativa encontró, y estaba en el texto que se IMPRIME

Se invocó `verificador-normativo` sobre las citas de los dos `Fundamento` nuevos. Las citas
—numeral, título, página impresa, página PDF y `caracter`— **salieron confirmadas las tres**
(`MC_HHD.4.1.1.3.6`, `HDS5_3ED.A.2`, `HDS5_3ED.3.3.3#HO`), y el `verbo` `DEFINE` está bien
elegido y sostenido por el `caracter`. **Lo que no salió limpio es la PROSA**, que es
justamente lo que T11 no gobierna: el invariante comprueba que el verbo declarado sea
compatible con el carácter de las citas, y no comprueba que las frases del `por_qué`
respeten ese carácter. Cuatro correcciones, todas verificadas de nuevo contra el PDF por
esta sesión antes de aplicarlas:

1. **El `Verbatim` de `HDS5_3ED.3.3.3#HO` estaba TRUNCADO, y la truncadura se llevaba la
   condición.** Terminaba en *«…can only be used if the barrel flows full for»* — que es
   donde el PDF parte la línea — y la oración de la fuente sigue: *«…**most of its
   length**.»* Leído bajo el rótulo «texto literal», publicaba un requisito **más laxo** que
   el de la fuente: «que el barril fluya lleno» en vez de «que fluya lleno **en la mayor
   parte de su longitud**». Es la elisión sin marcar que `CLAUDE.md` persigue, y
   `test_normativa_pdf` no la veía **porque verifica por subcadena y una truncadura siempre
   lo es**. Corregido contra la PDF 106.
2. **«h_o = max(TW, (d_c + D)/2)» no es la ecuación que escribe el num. 3.3.3.** Esa página
   escribe *«Approximate hydraulic gradeline ho = (dc + D)/2 can only be used if…»* — el
   símbolo atado **sólo a la semisuma** — y el máximo lo dice en **prosa**, en el párrafo
   siguiente y **sin nombrar `ho`**: *«the greater of tailwater or (dc + D)/2»*. Con forma de
   ecuación, el máximo está en **otros** numerales (impresas 3.12, 3.32 y 3.43). La v8 ya lo
   declaraba en su §4.3; el `Fundamento` lo había perdido. Reescrito: la fuente **aproxima**,
   y el máximo **lo toma el proyecto**.
3. **«DOS pasos posteriores lo consumen» es cierto de ESTE pipeline y falso del HDS-5**, que
   le da un tercer uso —el área para la velocidad de salida bajo control de salida, num.
   3.1.6, impresa 3.18 / PDF 100—. Acotado el sujeto.
4. **«La Forma 1 arranca de H_c/D» se imprimía igual bajo Forma 2**, donde la ec. (A.2) no
   usa `H_c`. Es el defecto que C3 corrigió en la **nota** del paso y que volvía por la
   puerta del **fundamento**, que es texto fijo. Condicionado.

Las cuatro mueven texto impreso y **ningún número**: multiconjunto vuelto a medir sobre las
cuatro memorias, «sólo en la base: {}» en las cuatro.

#### Dos cosas que encontró la propia sesión al auditarse, antes del auditor

- **`simbolo_altura` no tenía consumidor** — retirado; la razón completa está arriba.
- **Las dos implementaciones no eran sustituibles por palabra clave.** El `Protocol` nombra
  su parámetro `llenado`, `SeccionCircular` lo nombraba `theta` y la rectangular `y`: un
  `seccion.geometria_en(llenado=x)` habría reventado en una forma y no en la otra. Y nada lo
  comprobaba — `Seccion` no lleva `@runtime_checkable`, y aunque lo llevara, `isinstance`
  contra un `Protocol` mira los **nombres** y no las firmas —. Alineados los tres, y añadido
  `test_las_dos_secciones_implementan_el_protocolo_entero`, que compara miembro por miembro
  **y firma por firma**, y además que una propiedad sea propiedad en las dos. Sin él,
  «M3 y M4 quedan ciegos a la forma» es una intención y no una propiedad.

#### Anotado y no corregido

| # | Qué | Por qué no aquí |
|---|---|---|
| **C4-1** | `de_critico` **no lleva `formula_cita_id`**, y §4.5 pide fórmula con cita. La cita correcta depende de la forma de ecuación: bajo Forma 1 la exige la (A.2) por `H_c`, bajo Forma 2 sólo `h_o` (`HDS5_3ED.3.3.3#HO`) | elegir entre dos citas según la forma es una decisión de reporte que toca los dos pasos; C4 ya mueve la memoria por otras cinco razones y mezclarlo la haría ilegible |
| **C4-2** | El `id` `F4.YC_RECT` nombra sólo a la rectangular y funda el paso de **las dos** formas | renombrar un `id` del registro a mitad del plan mueve las referencias de C5 |
| **C4-4** | El paso `de_salida` de `M4._pasos_hidraulicos` escribe la fórmula *«HW = H + h_o − S·L, con h_o = max(TW, (y_c + D)/2)»* con `formula_cita_id = "HDS5_3ED.3.3.3#HO"`, y **ese numeral no escribe el máximo como ecuación** (verificado en C4: lo dice en prosa y sin nombrar `ho`; con forma de ecuación está en las impresas 3.12, 3.32 y 3.43) | es **anterior a C4** y la v8 **ya lo declara** en su §4.3 —*«La forma con el máximo … la 3.ª ed. no la numera: la escribe en prosa»*—, de modo que no es una atribución oculta. Corregirlo es elegir entre citar el numeral que aproxima y citar el que imprime la igualdad, y esa decisión toca los tres pasos de salida a la vez |
| **C4-3** | `M8_estructural` sigue codificando geometría circular en producción (`(π/4)·D_ext²`, prisma de ancho `D_ext`) | es del frente **F4**. Lo que sí corrigió C4 es la palabra «completo» de §2-bis, que declaraba un alcance que el censo no tiene |
