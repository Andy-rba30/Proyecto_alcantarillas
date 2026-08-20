# Mapa de datos faltantes

Qué falta para que una corrida llegue de punta a punta con los 12 módulos
produciendo resultado y sin ningún bloqueo, y a quién hay que pedírselo.

**Método.** No es lectura estática. Se corrió el pipeline sobre
`tests/ejemplo_puntos.csv` y se fueron resolviendo los bloqueos en rondas
sucesivas — declarando en memoria lo que cada ronda reclamaba — hasta llegar a
punto fijo, para destapar también los bloqueos que solo aparecen cuando el
anterior se resuelve. Después se atravesaron los bloqueos que no tienen vía de
resolución (ver "Cuatro muros") para enumerar lo que hay detrás de ellos y que
hoy nadie alcanza. Ningún archivo del proyecto se modificó: las declaraciones
de prueba vivieron solo en memoria del proceso de diagnóstico.

**Fecha del diagnóstico:** 2026-08-20. **Estado:** 26 criterios sin valor,
0 datos de sitio sin valor, 4 puntos en el CSV, 0 dimensionados.

---

## Resumen ejecutivo

Tres cosas que conviene saber antes de leer la tabla.

**1. De los 26 criterios sin valor, solo 16 bloquean el pipeline.** Los otros
10 están declarados pero ningún módulo los invoca hoy: o no los llama nadie, o
los llaman funciones de M9 que la CLI no ensambla (las verificaciones E1–E5 de
estabilidad del cabezal, que `cli.NOTA_ESTABILIDAD_CABEZAL` declara fuera de
alcance a propósito). Conseguirlos no desbloquea nada hoy — pero harán falta
cuando se cierre la Fase 9 completa. Están en la tabla marcados como
`no bloquea hoy`, para que no se compren primero.

**2. Hay cuatro bloqueos que ningún dato resuelve.** No son vacíos de dato: son
procedimientos que el código no implementa. Se documentan abajo en "Cuatro
muros". Mientras sigan ahí, **ningún punto puede dimensionarse, tenga uno todos
los datos del mundo.** Esto es lo primero que cambia la respuesta a "qué salgo a
conseguir": tres de los cuatro son trabajo de código o de método, no de gestión.

**3. Con esos cuatro muros salvados y todo lo demás declarado, cierra
exactamente un punto: A-01** (concreto reforzado, D = 0.90 m, las nueve
verificaciones de Fase 5 cumpliendo). A-02 y B-01 chocan con un conflicto
geométrico real —la clave del conducto queda a nivel de la subrasante o por
encima, o sea no hay relleno sobre el tubo con el diámetro mínimo de 0.90 m— y
C-01 está fuera del catálogo por diseño. Ver "El camino más corto" al final.

---

## Los 26 criterios, los datos externos y las columnas del CSV

Agrupados por a quién se le pide. Los que dicen `no bloquea hoy` están
declarados pero el pipeline no los invoca todavía.

### A) Mi asesor y yo — adopción del proyectista ante un vacío ya confirmado

| Qué falta | Tipo | Módulo y fase que bloquea | A quién se le pide | Vía de entrega | Por punto / global |
|---|---|---|---|---|---|
| `umbral_area_quebrada_importante_ha` | criterio [A] | M1, Fase 2 — TR de toda la Familia A (A-01, A-02) | Asesor y yo. El Manual tarifa las dos categorías pero no da regla de asignación física: el vacío está confirmado contra el texto | `criterios_adoptados.py`, **o** esquivarlo con `--categoria-tr` punto por punto | Global si es umbral; por punto si se usa la bandera |
| `longitud_proteccion_salida` | criterio [A] | M6, Fase 6 — protección de salida | Asesor y yo, o HEC-14 como respaldo | `criterios_adoptados.py` | Global (admite por punto) |
| `predimensionamiento_cabezal` | criterio [A] | M9, Fase 9 — geometría del cabezal (H, B, D_f, espesores, beta) | Asesor y yo, o plano tipo de cabezal del expediente vial | `criterios_adoptados.py` | Global — es un cabezal, no cuatro |
| `inclinacion_muro_beta` | criterio [A] | M9, Fase 9 — K_AE de Mononobe-Okabe | Asesor y yo. Es parte del predimensionamiento: sale con él | `criterios_adoptados.py` | Global |
| `friccion_muro_suelo_delta` | criterio [A] | M9, Fase 9 — K_AE | Asesor y yo, declarándolo como **fracción de phi** con su fuente; alternativa cara: ensayo de interfase | `criterios_adoptados.py` | Global |
| `TR_evento_extremo` | criterio [A] | M5, Fase 5 (V8) — **MURO 1** | Asesor y yo: TR mayor que el de diseño + definición cuantitativa de "la vía no colapsa" | `criterios_adoptados.py` **+ código** (ver muros) | Global |
| `v_max_concreto_eleccion` | criterio [A] | `no bloquea hoy` — ningún módulo lo invoca; V3 verifica los dos extremos del rango [N] de la Tabla N 10 | Asesor y yo, al redactar la memoria | `criterios_adoptados.py` | Global |
| `punto_aplicacion_incremento_sismico` | criterio [A] | `no bloquea hoy` — M9, momento de volteo sísmico (E1–E5, no ensambladas) | Asesor y yo: convención declarada (Seed-Whitman 0.6H o AASHTO LRFD Sec. 11) | `criterios_adoptados.py` | Global |
| `metodo_estabilidad_global` | criterio [A] | `no bloquea hoy` — M9 (E4/E5). **MURO 4** si se activa | Asesor y yo, pero el análisis en sí es del EMS | `criterios_adoptados.py` **+ código** | Global |
| `angulo_aletas` | criterio [A] | `no bloquea hoy` — ningún módulo lo invoca | Asesor y yo | `criterios_adoptados.py` | Global |
| `Mw_licuefaccion` | criterio [A] | `no bloquea hoy` — ningún módulo lo invoca (Fase 0-bis fuera de alcance) | Asesor y yo, o desagregación del peligro sísmico | `criterios_adoptados.py` | Global |
| Subir la rasante de **A-02** y **B-01** | decisión de proyecto | M8, Fase 8 — con D = 0.90 m la clave queda a nivel de subrasante o encima: no hay relleno sobre el tubo | Asesor y yo, con el diseño geométrico vial | Rediseño de rasante, o aceptar que esos puntos no cierran | Por punto (A-02, B-01) |

### B) Un documento que tengo que conseguir

| Qué falta | Tipo | Módulo y fase que bloquea | A quién o a qué se le pide | Vía de entrega | Por punto / global |
|---|---|---|---|---|---|
| `v_max_hdpe` | criterio [C] | M5, Fase 5 (V3) — velocidad máxima en HDPE | **Plastics Pipe Institute (PPI) / FHWA.** La fuente está identificada; falta extraer el número | `criterios_adoptados.py` | Global |
| `v_max_tmc` | criterio [C] | M5, Fase 5 (V3) — velocidad máxima en TMC | **PPI / FHWA**, mismo documento | `criterios_adoptados.py` | Global |
| `h_relleno_min_concreto_tmc` | criterio [C] | M2 (catálogo) y M7, Fase 7.A — altura mínima de relleno sobre la clave | **AASHTO M-170M** (concreto, clases I–V) y **ASTM A-807 / AASHTO M36** (TMC) | `criterios_adoptados.py` | Global |
| `clases_producto_por_relleno` | criterio [C] | M8, Fase 8 — clase/calibre por altura de relleno. **MURO 3** | **AASHTO M-170M** y **ASTM A-807 / AASHTO M36**: la tabla completa (clase × diámetro × rango de altura) | `criterios_adoptados.py` **+ código** | Global |
| `talud_terraplen` | criterio [A] | M7, Fase 7.B — longitud del conducto (B-01, C-01, y A-01/A-02 si no se declara `--longitud`) | **DG-2018** + la sección típica del proyecto | `criterios_adoptados.py`, **o** esquivarlo con `--longitud` | Global (la sección típica es una); por punto si se usa la bandera |
| `pendiente_relleno_trasdos_i` | criterio [A] | M9, Fase 9 — K_AE. Es el parámetro más sensible de la Fase 9 | **DG-2018** / detalle de coronación del terraplén sobre el cabezal | `criterios_adoptados.py` | Global |
| `remanso_derecho_via` | criterio [A] | M5, Fase 5 (V5) — **MURO 2** | **DG-2018 + Ley 29338**, más un perfil de remanso (paso a paso o HEC-RAS) | `criterios_adoptados.py` **+ código y método** | Global (el método) |
| `ancho_derecho_via_m` | **dato sin vía de entrega** | M5, Fase 5 (V5) — **MURO 2**. Se exige pero **no se puede entregar**: no es columna, ni bandera, ni clave de `--datos-externos` | Expediente vial (ancho de derecho de vía legal, no el ancho de plataforma) | **Ninguna hoy** — requiere abrir la vía en el código | Por punto |
| `N_cq_N_gammaq_meyerhof` | criterio [A] | `no bloquea hoy` — M9 (capacidad portante con talud, E1–E5) | **Manual de Puentes**, figuras 2.8.1.3.1.2c-1 y -2, págs. 272-273 | `criterios_adoptados.py` | Global |
| `cortante_alto_muro_e060_art_11_10_10_2` | criterio [A] | `no bloquea hoy` — M9, cuantía horizontal del muro | **E.060 Art. 11.10.10.2** — verificar numeral y página contra el texto | `criterios_adoptados.py` | Global |

### C) Un ensayo de laboratorio o de campo (EMS)

| Qué falta | Tipo | Módulo y fase que bloquea | Qué ensayo exactamente | Vía de entrega | Por punto / global |
|---|---|---|---|---|---|
| `peso_especifico_relleno_kn_m3` | criterio [A] | M5 (V7, flotación) y M8, Fase 8 — término EV | **Peso específico del material de cantera** propuesto. Es de los más baratos del EMS | `criterios_adoptados.py` | Global (una cantera) |
| `phi_relleno_trasdos` | criterio [A] | M9, Fase 9 — K_AE y Ka de Coulomb | **Corte directo** sobre el material de cantera del trasdós | `criterios_adoptados.py` | Global |
| `c_phi_fundacion` | criterio [A] | `no bloquea hoy` — M9 (E1–E5) | **Corte directo o SPT.** E.050 Art. 20: solo uno de los dos (phi=0 en cohesivos, c=0 en friccionantes) | `criterios_adoptados.py` | Global, salvo que varíe por calicata |
| `capacidad_portante_adm` | criterio [A] | `no bloquea hoy` — M9 (E1) | **EMS conforme a E.050.** Se deriva de `c_phi_fundacion` | `criterios_adoptados.py` | Global, salvo que varíe por calicata |
| `NF_profundidad_m` (vacía en las 4 filas) | columna CSV | **No bloquea hoy.** V7 asume el NF en su cota más alta, que es conservador; los empujes y la subpresión de M9 que sí lo usan pertenecen a E1–E5, no ensambladas | **Estudio geotécnico**, medido en cada cruce | Columna del CSV | **Por punto** (4 lecturas) |

### D) Una entidad (ANA, Junta de Usuarios, SENAMHI)

| Qué falta | Tipo | Módulo y fase que bloquea | A quién se le pide | Vía de entrega | Por punto / global |
|---|---|---|---|---|---|
| `TW_receptor` | criterio [A] | MD, Fases 3-5 — tirante en el receptor. Bloquea todo punto sin `--tw` | **ANA / Junta de Usuarios del Bajo Piura**: caudal de diseño documentado del dren o canal receptor | `criterios_adoptados.py`, **o** esquivarlo con `--tw` | Global si es un escenario; por punto si se mide receptor por receptor |
| `Q_m3s` de **C-01** (celda vacía) | columna CSV | MD, Fases 3-5 — `DatoFaltanteError`. Sec. 2.3: el caudal de la Familia C es el del canal | **ANA / Junta de Usuarios** (Tablero 3.1) | Columna del CSV, **o** `--datos-externos` por punto | **Por punto** (solo C-01) |
| `S_cauce` de **C-01** (celda vacía) | columna CSV | MD — se destapa **solo después** de resolver `Q_m3s`: es un bloqueo de segunda capa | **ANA / Junta de Usuarios**, con la rasante del canal | Columna del CSV, **o** `--datos-externos` (`S_conducto`) | **Por punto** (solo C-01) |
| `homogeneidad_serie_fen` | criterio [A] | `no bloquea hoy` — ningún módulo lo invoca (la CLI no recalcula el Q; lo lee del CSV) | **SENAMHI**: serie de precipitación máxima anual con longitud de registro, estación y años faltantes | `criterios_adoptados.py` | Global |
| `area_ha` de **C-01** (celda vacía) | columna CSV | **No bloquea.** Sec. 1.1 la marca "solo clasificador" y solo se usa para el umbral de la Familia A; C-01 es Familia C | — | — | Por punto |
| `cota_TW` y `Q_receptor_m3s` (vacías en las 4 filas) | columnas CSV | **No bloquean.** M0 las admite vacías para toda familia por el Tablero 3.1 | ANA / Junta de Usuarios, cuando lleguen | Columnas del CSV | Por punto |

### E) Datos externos que declaro yo (topografía, QGIS, expediente vial)

Ninguno es criterio ni columna: entran por bandera o por `--datos-externos`.

| Qué falta | Tipo | Módulo y fase que bloquea | A quién se le pide | Vía de entrega | Por punto / global |
|---|---|---|---|---|---|
| `luz_m` | dato externo | M1, Fase 2 — **sin él ningún punto se clasifica siquiera.** Es el primer bloqueo de todos | Topografía / QGIS. Umbral binario de Sec. 2.1: ≥ 6 m es PUENTE y sale de alcance | `--luz` o `--datos-externos` | **Por punto** (varía cruce a cruce) |
| `L_hidraulico_m` | dato externo | M10, Fase 10 — solo **Familia B (B-01)**. Sec. 10 da el procedimiento pero no la sección de la cuneta | Yo, del diseño de drenaje longitudinal | `--l-hidraulico` o `--datos-externos` | **Por punto** (solo B-01) |
| `longitud_m` | dato externo | **Opcional.** Si no se declara, la calcula M7 (7.B) y entonces hace falta `talud_terraplen` | Expediente vial / topografía | `--longitud` o `--datos-externos` | Por punto |
| `TW_m` | dato externo | **Opcional.** Sustituye a `TW_receptor`. TW = 0 es legítimo (salida libre) | Yo, adoptando escenario acotado, mientras ANA no responda | `--tw` o `--datos-externos` | Por punto |
| `categoria_tr` | dato externo | **Opcional.** Sustituye a `umbral_area_...` en Familia A: se clasifica el cauce a mano | Asesor y yo, cauce por cauce | `--categoria-tr` o `--datos-externos` | Por punto (A-01, A-02) |
| `Q_m3s` / `S_conducto` | dato externo | Familias B y C, cuando el caudal no es el de la columna (Sec. 2.3) | ANA / Junta, o diseño de cuneta | `--datos-externos` por punto | Por punto |

---

## Cuatro muros: bloqueos que ningún dato resuelve

Estos no se compran ni se gestionan. El código llama al criterio y, si el
criterio **tiene** valor, levanta `AssertionError` o pide un dato que no tiene
puerta de entrada. Verificado corriendo el pipeline con cada criterio declarado.

| # | Dónde | Qué pasa hoy si el criterio está vacío | Qué pasa si le doy valor | Qué falta de verdad |
|---|---|---|---|---|
| 1 | **V8**, `M5_verificaciones.py:447` | `CriterioPendienteError` en `TR_evento_extremo`: bloqueo limpio | **La corrida entera aborta** con `AssertionError: inalcanzable mientras 'TR_evento_extremo' este vacio`. `AssertionError` no desciende de `ErrorProyecto`, así que `cli._etapa` no lo captura | Implementar V8: correr M3/M4 con el TR extremo y comparar el HW contra el umbral de colapso |
| 2 | **V5**, `M5_verificaciones.py:322` | `CriterioPendienteError` en `remanso_derecho_via` | `DatoFaltanteError("ancho_derecho_via_m")` — **y ese dato no se puede entregar por ninguna vía**: aparece una sola vez en todo el repo, en el `raise` que lo pide | Un perfil de remanso (método) **y** abrir la vía de entrada para el ancho de derecho de vía por punto |
| 3 | **Fase 8**, `M8_estructural.py:187` | `CriterioPendienteError` en `clases_producto_por_relleno` | `AssertionError: inalcanzable...`, aborta la corrida. Además se llama para todo material, aunque su propio docstring diga que HDPE está exento | Transcribir la tabla de norma de producto **y** ramificar por material |
| 4 | **E4/E5**, `M9_cabezal.py:979` y `:995` | No se alcanza: la CLI no ensambla E1–E5 | `AssertionError: inalcanzable...` si se activaran | Implementar la estabilidad global, o dejar el análisis en el EMS como hoy |

Mismo patrón, sin ser muro, en `M9_cabezal.py:1086` (`N_cq_N_gammaq_meyerhof`).

**Consecuencia práctica:** los muros 1 y 2 están en la ruta de dimensionamiento
de **todo** punto (V5 y V8 se evalúan para cada diámetro candidato). Mientras
sigan ahí, `dimensionados` será 0 aunque lleguen todos los datos de la tabla.
El muro 3 impide cerrar la Fase 8 aunque el punto ya esté dimensionado.

### Un hallazgo aparte: la declaración en caliente de la GUI no llega a M2

`M2_material._valor_si_declarado` decide si un criterio está vacío leyendo
`ca.criterio(clave).valor`, que **no** refleja `_OVERRIDES`. Un criterio
declarado desde la GUI con `establecer_valor_dinamico` (`h_relleno_min_concreto_tmc`,
`v_max_hdpe`, `v_max_tmc`, `n_manning_hdpe`) le sigue pareciendo vacío a M2: el
catálogo sale con el campo en `None` y M7 cae en el `AssertionError` del muro,
en vez de usar el valor que el usuario acaba de declarar. Editar el archivo sí
funciona; la GUI no. Lo dejo anotado, no lo toqué.

---

## Bloqueos en cascada: en qué orden aparecen

Corrida real sobre `tests/ejemplo_puntos.csv`, empezando solo con `--luz 2.0` y
resolviendo cada ronda. Cada capa solo se ve cuando la anterior está resuelta.

| Ronda | Aparece | Puntos |
|---|---|---|
| 1 | `umbral_area_quebrada_importante_ha` | A-01, A-02 |
| 1 | `talud_terraplen` | B-01, C-01 |
| 1 | `TW_receptor` | B-01, C-01 |
| 1 | `phi_relleno_trasdos`, `predimensionamiento_cabezal` | proyecto (Fase 9) |
| 1 | `L_hidraulico_m` | B-01 |
| 2 | `remanso_derecho_via` — antes ni se alcanzaba | A-01, A-02, B-01 |
| 2 | `Q_m3s` | C-01 |
| 2 | `pendiente_relleno_trasdos_i` | proyecto |
| 3 | **`ancho_derecho_via_m`** — segunda capa de V5, sin vía de entrega | A-01, A-02, B-01 |
| 3 | `S_cauce` — segunda capa de C-01, solo tras resolver `Q_m3s` | C-01 |
| 3 | `inclinacion_muro_beta` | proyecto |
| 4 | `friccion_muro_suelo_delta` | proyecto |
| 5 | **punto fijo**: quedan `ancho_derecho_via_m` y `S_cauce`, y el primero no tiene puerta | — |

Detrás del muro de V5 (salvándolo en el diagnóstico) aparecen todavía
`TR_evento_extremo` (V8), `longitud_proteccion_salida` (Fase 6),
`h_relleno_min_concreto_tmc` (Fase 7) y `clases_producto_por_relleno` (Fase 8).

---

## El camino más corto: cerrar UN punto

**El punto más barato es A-01.** No por tener menos datos pendientes, sino
porque es **el único de los cuatro que llega a cerrar**:

- **A-02 y B-01** se dimensionan hidráulicamente, pero mueren en Fase 8: con el
  diámetro mínimo de la progresión (0.90 m) la clave del conducto queda a nivel
  de la subrasante o por encima — no queda relleno sobre el tubo. Eso no se
  arregla con un dato: hay que subir la rasante, que es rediseño vial.
- **C-01** no puede cerrar nunca por esta vía: `DisenoNoFactibleError` — Sec. 2.3
  le asigna sección de marco o multicelda y el catálogo de Sec. 3.2 es de
  conductos circulares. No es falta de datos: *"el punto no es no-factible, es de
  otra forma de estructura"*. Pedirle el caudal a ANA para C-01 no lo cierra.
- **A-01** cierra: concreto reforzado, D = 0.90 m, las nueve verificaciones de
  Fase 5 cumpliendo y las Fases 6, 7, 8 y 9 sin bloqueos.

Además A-01 es Familia A, así que **no** necesita `L_hidraulico_m` (eso es de
Familia B, o sea de B-01, que de todos modos no cierra).

### Lista de compra mínima para A-01

**Paso 0 — trabajo de código, no de gestión (sin esto no hay paso 1):**
salvar los muros 1, 2 y 3. Son V8, V5 (+ abrir la entrada de
`ancho_derecho_via_m`) y la tabla de clase/calibre de Fase 8.

**Paso 1 — cuatro datos del punto, todos por bandera (los consigo yo):**

| Dato | Bandera | De dónde sale |
|---|---|---|
| `luz_m` | `--luz` | Topografía / QGIS |
| `categoria_tr` | `--categoria-tr` | Asesor y yo, clasificando ese cauce — evita `umbral_area_...` |
| `TW_m` | `--tw` | Escenario acotado adoptado — evita `TW_receptor` y no espera a ANA |
| `longitud_m` | `--longitud` | Expediente vial — evita `talud_terraplen` |

Las tres últimas banderas esquivan tres criterios enteros. Es la palanca más
barata que tiene el proyecto hoy: **cambian una gestión larga por un dato que
ya está en el expediente.**

**Paso 2 — tres criterios que sí hay que declarar (globales, valen para los
cuatro puntos):**

| Criterio | A quién | Por qué es barato |
|---|---|---|
| `peso_especifico_relleno_kn_m3` | Ensayo de cantera | Es el ensayo más barato del EMS, y una cantera sirve para todo el corredor |
| `longitud_proteccion_salida` | Asesor y yo | Decisión, no ensayo ni documento |
| `h_relleno_min_concreto_tmc` | AASHTO M-170M | Un número de un documento que ya está identificado |

**Paso 3 — cinco criterios de la Fase 9, globales del proyecto** (no son del
punto: el cabezal es uno solo): `predimensionamiento_cabezal`,
`inclinacion_muro_beta`, `phi_relleno_trasdos`, `pendiente_relleno_trasdos_i`,
`friccion_muro_suelo_delta`. Cuatro de los cinco los cierra el asesor con el
predimensionamiento y la sección típica; solo `phi_relleno_trasdos` necesita un
corte directo.

**Total: 4 banderas + 8 criterios globales + 3 arreglos de código.** Los 14
criterios restantes de los 26 no hacen falta para cerrar A-01.

### Si además quiero cerrar A-02 y B-01

Ningún dato más de la tabla: los dos necesitan **subir la rasante** para que
quepa el relleno sobre la clave, más `L_hidraulico_m` en el caso de B-01. Es una
conversación de diseño geométrico con el asesor, no una gestión de datos.

### Qué NO comprar todavía

Los 10 criterios marcados `no bloquea hoy` (`Mw_licuefaccion`, `angulo_aletas`,
`c_phi_fundacion`, `capacidad_portante_adm`, `v_max_concreto_eleccion`,
`homogeneidad_serie_fen`, `metodo_estabilidad_global`,
`N_cq_N_gammaq_meyerhof`, `punto_aplicacion_incremento_sismico`,
`cortante_alto_muro_e060_art_11_10_10_2`) y la columna `NF_profundidad_m`. Nada
de eso mueve una sola corrida hoy. Hará falta cuando se ensamblen las
verificaciones E1–E5 del cabezal, que es otro frente.
