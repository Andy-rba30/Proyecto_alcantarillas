# Inventario de criterios pendientes y constantes sin numeral

*Auditoría de estado, clasificada por **qué acción cierra cada vacío**.*
*Generada leyendo el código y corriendo el pipeline, no la documentación previa.*

---

## 0. Cómo se generó este inventario (reproducible)

Todo lo que sigue sale de tres comandos. Si el código cambia, se regenera con
los mismos tres — este documento no es una lista escrita a mano.

```bash
pip install -r requirements.txt

# 1. Estado de la suite
python -m pytest -q
# -> 654 passed, 1 skipped

# 2. Inventario de vacíos, directamente del módulo de gobierno
python -c "import sys; sys.path.insert(0,'src'); import criterios_adoptados as ca; \
print(len(ca.CRITERIOS), 'criterios'); print(ca.criterios_sin_valor())"

# 3. Qué bloquea de verdad, sobre el CSV de ejemplo
python cli.py tests/ejemplo_puntos.csv --luz 2.0
```

---

## 1. Resumen del estado

| Magnitud | Valor |
|---|---|
| Criterios declarados en `criterios_adoptados.py` | 46 |
| **Criterios sin valor (`valor=None`)** | **26** |
| Criterios cerrados | 20 |
| Datos de sitio en `datos_sitio.py` | 3, los tres con valor |
| Criterios marcados `provisional=True` | 0 — no hay residuo de pruebas |
| Suite de tests | 654 pasan, 1 se salta |
| Puntos del CSV de ejemplo que completan diseño | **0 de 4** |

Reparto por etiqueta de los 26 vacíos: **22 `[A]`** (adopción declarada) y
**4 `[C]`** (vacío normativo con fuente técnica identificada pero sin extraer).
Ningún vacío es `[N]` ni `[S]`, que es lo correcto: una exigencia normativa o
un dato de sitio no pueden estar "pendientes de elegir".

El programa no completa ningún punto **por diseño, no por defecto**. La
arquitectura de gobierno está haciendo exactamente lo que se construyó para
hacer: negarse a producir un número que no puede sostener.

---

## 2. Los 5 bloqueos de primera línea

De los 26 vacíos, solo **5** se manifiestan hoy al correr el pipeline. Los
otros 21 están **detrás** de estos: el cálculo se detiene antes de llegar a
invocarlos. Esto importa para priorizar: cerrar uno de estos cinco no solo
desbloquea su etapa, además **revela** qué viene después.

| # | Criterio | Detiene | Puntos afectados |
|---|---|---|---|
| 1 | `umbral_area_quebrada_importante_ha` | Fase 2 (M1) — clasificación y TR | A-01, A-02 |
| 2 | `TW_receptor` | Fases 3-5 (MD) — tirante en el receptor | B-01, C-01 |
| 3 | `talud_terraplen` | Fase 7 (M7) — longitud del conducto | B-01, C-01 |
| 4 | `phi_relleno_trasdos` | Fase 9 (M9) — K_AE de Mononobe-Okabe | proyecto |
| 5 | `predimensionamiento_cabezal` | Fase 9 (M9) — predimensionamiento E1-E5 | proyecto |

Los puntos A-01 y A-02 mueren en la Fase 2: ni siquiera llegan a tener caudal
de diseño. B-01 y C-01 pasan el umbral de luz y se detienen en el diseño
hidráulico.

> **Bloqueo adicional que no es un criterio:** B-01 arrastra un
> `DatoFaltanteError` por `L_hidraulico_m` (Fase 10). No es un vacío de
> `criterios_adoptados.py` sino un dato declarado que no se pasó por bandera.

---

## 3. Clasificación: los 7 grupos por acción de cierre

La clasificación útil no es por fase ni por etiqueta — es por **quién tiene
que hacer qué** para cerrar el vacío. Dos criterios de la misma fase pueden
necesitar cosas completamente distintas: uno un ensayo de laboratorio y otro
una firma en un plano.

| Grupo | Qué lo cierra | N.º | Depende de |
|---|---|---|---|
| **G1** | Ensayo o estudio de campo | 5 | Laboratorio / EMS |
| **G2** | Transcribir una tabla o figura que ya existe | 5 | Acceso al documento |
| **G3** | Medir sobre planos del expediente vial | 5 | Proyectista vial |
| **G4** | Cálculo o estudio que este software no hace | 6 | Especialista |
| **G5** | Dato en poder de un tercero | 1 | Institución externa |
| **G6** | Decisión declarada del proyectista | 3 | Nadie más — se decide y se escribe |
| **G7** | Bloqueado por otro cálculo del propio expediente | 1 | Orden interno |

**El grupo G6 es el único que se cierra hoy, sin esperar a nadie.** Son tres
criterios cuya única barrera es que alguien escriba el número y lo defienda.

---

## 4. Tabla maestra — los 26 criterios

Ordenada por grupo. La columna "Módulo" dice quién lo invoca; `—` significa
que está declarado pero **ningún módulo lo consume todavía** (ver §6).

| # | Clave | Et. | Grupo | Fase / Módulo | Qué queda bloqueado |
|---|---|---|---|---|---|
| 1 | `phi_relleno_trasdos` | A | G1 | 9 / M9 | K_AE de Mononobe-Okabe |
| 2 | `c_phi_fundacion` | A | G1 | 9 / — | Resistencia del suelo de fundación |
| 3 | `capacidad_portante_adm` | A | G1 | 9 / — | Verificación de capacidad portante |
| 4 | `peso_especifico_relleno_kn_m3` | A | G1 | 5, 8, 9 / M5, M8, M9 | ΣW de V7 (flotación) |
| 5 | `Mw_licuefaccion` | A | G1 | 0-bis / — | Factor de escala de magnitud (MSF) |
| 6 | `h_relleno_min_concreto_tmc` | C | G2 | 3, 5, 7, 8 / M2, M5, M7, M8 | Cota de rasante en concreto y TMC |
| 7 | `clases_producto_por_relleno` | C | G2 | 8 / M8 | Clase/calibre por altura de relleno |
| 8 | `v_max_hdpe` | C | G2 | 3, 5 / M2, M5 | V3 en HDPE |
| 9 | `v_max_tmc` | C | G2 | 3, 5 / M2, M5 | V3 en TMC |
| 10 | `N_cq_N_gammaq_meyerhof` | A | G2 | 9 / M9 | Capacidad portante en talud |
| 11 | `talud_terraplen` | A | G3 | 7 / M7 | Longitud del conducto y cota de salida |
| 12 | `predimensionamiento_cabezal` | A | G3 | 9 / M9 | Todo el dimensionamiento del cabezal |
| 13 | `inclinacion_muro_beta` | A | G3 | 9 / M9 | K_AE (paramento del trasdós) |
| 14 | `pendiente_relleno_trasdos_i` | A | G3 | 9 / M9 | K_AE (superficie del relleno) |
| 15 | `angulo_aletas` | A | G3 | 9 / — | Geometría de aletas |
| 16 | `umbral_area_quebrada_importante_ha` | A | G4 | 2 / M1 | TR y caudal de toda la Familia A |
| 17 | `homogeneidad_serie_fen` | A | G4 | 1-bis / MD | Validez del Q de diseño |
| 18 | `remanso_derecho_via` | A | G4 | 5 / M5 | V5 (embalse en derecho de vía) |
| 19 | `TR_evento_extremo` | A | G4 | 5 / M5 | V8 (evento extremo) |
| 20 | `longitud_proteccion_salida` | A | G4 | 6 / M6 | Dimensión de la protección |
| 21 | `metodo_estabilidad_global` | A | G4 | 9 / M9 | FS de estabilidad global |
| 22 | `TW_receptor` | A | G5 | 4, 5 / MD, M4, M5 | Control de salida y HW |
| 23 | `v_max_concreto_eleccion` | A | G6 | 5 / — | V3 con un solo número |
| 24 | `friccion_muro_suelo_delta` | A | G6 | 9 / M9 | K_AE (δ) |
| 25 | `punto_aplicacion_incremento_sismico` | A | G6 | 9 / M9 | Volteo sísmico (brazo) |
| 26 | `cortante_alto_muro_e060_art_11_10_10_2` | A | G7 | 9 / M9 | Cuantía horizontal mínima |

**Concentración por fase:** la Fase 9 (cabezal) acumula **12 de los 26**. Es el
cuello de botella del expediente, y casi todo el bloque depende de una sola
cosa que aún no existe: la geometría del cabezal.

---

## 5. Cómo encontrar cada uno — vía de cierre por grupo

### G1 — Ensayo o estudio de campo (5)

No se cierran leyendo nada. Requieren que alguien vaya a campo o al laboratorio.

| Clave | Ensayo o estudio que lo cierra | Norma / referencia |
|---|---|---|
| `phi_relleno_trasdos` | Corte directo sobre el material de cantera propuesto | ASTM D3080 |
| `c_phi_fundacion` | Corte directo o SPT sobre el suelo de fundación | E.050 Art. 20 |
| `capacidad_portante_adm` | Derivado del anterior — sale del EMS | E.050 |
| `peso_especifico_relleno_kn_m3` | Peso específico del material de cantera | Ensayo estándar |
| `Mw_licuefaccion` | Desagregación del peligro sísmico | Estudio específico |

> **E.050 Art. 20 impone una restricción que no se puede saltar:** en suelos
> cohesivos se usa φ=0 y en friccionantes c=0. `c_phi_fundacion` debe entregar
> **uno de los dos**, nunca ambos. Declarar los dos es un error normativo, no
> un exceso de información.

**Vía práctica:** los tres primeros salen del **mismo EMS**. Si el EMS del
expediente vial ya existe, es un solo documento el que cierra tres criterios.
La pregunta a hacer es: *"¿el EMS incluye corte directo sobre la cantera
propuesta para el trasdós, o solo sobre el suelo de fundación?"* — es el hueco
habitual.

`peso_especifico_relleno_kn_m3` admite un cierre interino: un valor de práctica
corriente declarado con su fuente en la memoria, sustituible cuando llegue el
ensayo. Es el único de G1 que no obliga a esperar.

---

### G2 — Transcribir una tabla o figura que ya existe (5)

**Este es el grupo más barato de cerrar y el más fácil de postergar.** La
fuente está identificada en los cuatro casos: falta que alguien abra el
documento y copie los números.

| Clave | Documento exacto | Qué hay que extraer |
|---|---|---|
| `h_relleno_min_concreto_tmc` | AASHTO M-170M (concreto); ASTM A-807 / AASHTO M36 (TMC) | Altura mínima de relleno sobre la clave |
| `clases_producto_por_relleno` | Los mismos dos | Tabla completa: clase/calibre × diámetro × rango de altura |
| `v_max_hdpe` | Plastics Pipe Institute (PPI) *Handbook of PE Pipe*; FHWA | Velocidad máxima admisible |
| `v_max_tmc` | PPI / FHWA | Velocidad máxima admisible |
| `N_cq_N_gammaq_meyerhof` | Manual de Puentes, figs. 2.8.1.3.1.2c-1 y -2, págs. 272-273 | Lectura de ábaco (Meyerhof 1957) |

**Dos observaciones que cambian el orden de trabajo:**

1. `h_relleno_min_concreto_tmc` y `clases_producto_por_relleno` son **el mismo
   documento**. El primero es un escalar y el segundo la tabla completa. Extraer
   la tabla cierra los dos de una vez — y además cierra `D_MAX` de
   `constantes_normativas.py` (§7), que hoy lleva un comentario `VERIFICAR`.
   **Un solo acceso a AASHTO M-170M y AASHTO M36 cierra tres vacíos.**

2. `N_cq_N_gammaq_meyerhof` **no se puede cerrar antes que G3**. Los ábacos se
   leen para una geometría concreta: distancia de la zapata al borde del talud,
   altura del talud, inclinación. Sin `predimensionamiento_cabezal` no hay con
   qué entrar al ábaco. Está en G2 por su naturaleza (transcripción), pero su
   turno viene después.

---

### G3 — Medir sobre planos del expediente vial (5)

Todos se cierran con documentos que **el proyecto vial ya debería tener**. No
hay que producir información nueva: hay que ir a buscarla.

| Clave | Documento del expediente | Pregunta concreta que responde |
|---|---|---|
| `talud_terraplen` | Sección típica (DG-2018) | ¿Cuál es el H:V del talud del terraplén? |
| `predimensionamiento_cabezal` | Plano tipo de cabezal, acotado | H, B, D_f, espesores de pantalla y zapata |
| `inclinacion_muro_beta` | El mismo plano | ¿El paramento es vertical o tiene talud? |
| `pendiente_relleno_trasdos_i` | Sección típica sobre el cabezal | ¿El relleno corona horizontal o sigue el talud? |
| `angulo_aletas` | Detalle de aletas + esviaje del punto | Ángulo, ajustado al esviaje |

> **`pendiente_relleno_trasdos_i` es el criterio con la sensibilidad más
> violenta de todo el expediente.** En Mononobe-Okabe, *i* entra en
> sen(φ − ψ − i); con ψ = 26.6° (k_h = 0.50), el radicando **se anula** cuando
> φ − i se acerca a ψ. Unos pocos grados de relleno inclinado pueden llevar el
> empuje sísmico al infinito. Adoptar *i = 0* "porque parece inocuo" es el
> error más caro de la lista.

**Vía práctica:** `predimensionamiento_cabezal` e `inclinacion_muro_beta` son
**el mismo plano** — β es literalmente una cota de ese dibujo. Y ese plano es
el que desbloquea la Fase 9 entera, incluido el turno de
`N_cq_N_gammaq_meyerhof`. Es el documento de mayor rendimiento del inventario.

Advertencia registrada en el propio criterio: la geometría tiene que ser
**compatible** con el diámetro adoptado en la Fase 4 y con la altura de
terraplén de la Fase 7. Un cabezal dimensionado aparte del conducto que remata
es una incoherencia de expediente, no un detalle.

---

### G4 — Cálculo o estudio que este software no hace (6)

Aquí no falta un número: falta **un procedimiento** que produzca el número.

| Clave | Estudio que lo cierra | Herramienta típica |
|---|---|---|
| `umbral_area_quebrada_importante_ha` | Clasificación del cauce, punto por punto | Criterio hidrológico documentado |
| `homogeneidad_serie_fen` | Análisis de homogeneidad de la serie SENAMHI | Ajuste con y sin 1983/1998/2017 |
| `remanso_derecho_via` | Perfil de remanso aguas arriba + ancho de derecho de vía | HEC-RAS o paso a paso |
| `TR_evento_extremo` | Definir TR mayor y umbral cuantitativo de colapso | Declaración en memoria |
| `longitud_proteccion_salida` | Diseño de disipador o transición | HEC-14 |
| `metodo_estabilidad_global` | Análisis de estabilidad de taludes | Bishop / Spencer / Morgenstern-Price |

**`umbral_area_quebrada_importante_ha` tiene una salida que no exige estudio, y
conviene conocerla.** El Manual de Hidrología (Tabla N.º 02, num. 3.6) tarifa
las dos categorías de cauce pero **no las define**: no hay umbral de área, ni
de caudal, ni de longitud, ni de orden de cauce. El vacío está en la norma. La
alternativa que M1 ya soporta es **pasar la categoría explícita punto por
punto** (`categoria_tr`, bandera de `cli.py`), documentando la clasificación de
cada cauce en la memoria en vez de inventar una regla general. Es la vía
defendible, y **está disponible hoy sin esperar a nadie**.

Entre una categoría y la otra el TR se duplica (71 vs. 35 años), y con él sube
la intensidad de la IDF y el Q de diseño de todos los puntos de paso. No es un
matiz de clasificación: es el caudal.

**`homogeneidad_serie_fen` es previo a la Fase 4, no paralelo.** Si la serie de
Piura contiene 1983, 1998 y 2017, el ajuste K-S puede estar dominado por dos o
tres outliers. Si **no** los contiene, el Q de diseño está gravemente
subestimado. Cerrar la hidráulica antes de contestar esto es construir sobre un
caudal que puede cambiar entero.

---

### G5 — Dato en poder de un tercero (1)

| Clave | Quién lo tiene | Qué pedir |
|---|---|---|
| `TW_receptor` | ANA / Junta de Usuarios del Bajo Piura | Caudal de diseño documentado del dren o canal receptor |

TW no se mide: se calcula con Manning en el receptor usando **su propio caudal
de diseño**. Lo que falta es ese caudal, y lo tiene la institución que
administra el dren.

**Cierre interino disponible:** el propio criterio contempla adoptar **dos
escenarios acotados** — salida libre y sección llena — y correr el diseño con
ambos. No cierra el expediente, pero produce un rango defendible y desbloquea
B-01 y C-01 para ver qué hay detrás. Es la vía recomendada mientras llega el
dato: **acota en vez de inventar**.

---

### G6 — Decisión declarada del proyectista (3)

**Estos tres no esperan a nadie.** No hay ensayo, ni plano, ni institución: hay
que elegir un número, escribir por qué, y defenderlo en la memoria.

| Clave | Rango o convención | Fuente a citar al declararlo |
|---|---|---|
| `v_max_concreto_eleccion` | 3.0 – 6.0 m/s | Manual MTC, Tabla N.º 10 (num. 4.1.1.3.6) |
| `friccion_muro_suelo_delta` | φ/2 a 2φ/3 | Práctica de concreto contra suelo granular |
| `punto_aplicacion_incremento_sismico` | ~0.6H | Seed-Whitman, o AASHTO LRFD Sec. 11 |

Notas de cierre que el propio código exige:

- **`v_max_concreto_eleccion`:** la lectura conservadora es el extremo inferior
  (3.0 m/s). Hoy M5 verifica **los dos extremos del rango**, que es un rodeo
  correcto pero deja la memoria sin un número único.
- **`friccion_muro_suelo_delta`:** declararlo como **fracción de φ**, no como
  ángulo suelto — si no, al ajustar `phi_relleno_trasdos` los dos quedan
  incoherentes. Ojo: δ alto reduce K_AE (favorable) pero inclina la resultante
  y cambia el reparto entre deslizamiento y volteo. No es conservador por un
  lado solo.
- **`punto_aplicacion_incremento_sismico`:** sin él no hay brazo, y sin brazo
  no hay momento de volteo sísmico. La fila "volteo / sísmico" de la tabla de
  Sec. 9.3 simplemente no se puede evaluar.

---

### G7 — Bloqueado por otro cálculo del expediente (1)

| Clave | Depende de | Por qué no se puede contestar hoy |
|---|---|---|
| `cortante_alto_muro_e060_art_11_10_10_2` | Vu del cabezal | M9 no calcula cortante todavía |

E.060 no tiene un mínimo de cuantía horizontal de muro: tiene **dos**. El
Art. 14.3.1 fija 0.0020 y el Art. 11.10.10.2 lo sube a 0.0025 bajo demanda de
cortante alta (del orden de Vu > 0.5·φ·Vc). Aplicar solo el 0.0020 sin
comprobar el otro es quedarse con el mínimo más bajo **por omisión**.

El disparador es una demanda de cortante, y el diseño por flexión y corte está
en `procedimiento_flexion_corte_aashto_sec5` (que **sí** tiene valor). Este
criterio se cierra **después** de que M9 produzca Vu — no antes.

---

## 6. Cinco criterios declarados que ningún módulo consume

Están correctamente declarados, pero **hoy no bloquean nada** porque nadie los
invoca. No son un defecto: son declaración anticipada del vacío. Conviene
saberlo para no gastar esfuerzo cerrando algo que no desbloquea nada todavía.

| Clave | Estado | Por qué no se invoca |
|---|---|---|
| `v_max_concreto_eleccion` | Declarado | M5 verifica los dos extremos del rango [N] en su lugar |
| `c_phi_fundacion` | Declarado | La verificación geotécnica del cabezal aún no llega ahí |
| `capacidad_portante_adm` | Declarado | Ídem |
| `Mw_licuefaccion` | Declarado | La Fase 0-bis (licuefacción) no está implementada |
| `angulo_aletas` | Declarado | M9 no dimensiona aletas todavía |

Consecuencia práctica: darles valor **no cambia ninguna corrida hoy**. Su
cierre es de expediente, no de desbloqueo.

---

## 7. Problema distinto: constantes `[N]` sin numeral

`constantes_normativas.py` admite en su docstring **solo `[N]` con numeral
verificado**. Estas entradas tienen valor pero les falta o les cojea la cita.
No bloquean el cálculo — bloquean la **defensa** del cálculo ante un revisor.

### 7.1 Abiertas

| Constante | Valor | Qué falta | Gravedad |
|---|---|---|---|
| `SPT_ESPACIAMIENTO` | 1.0 m | Ningún numeral. **Además ningún módulo lo usa** | Baja |
| `K_FRICCION_SI` | 19.63 | Discrepancia con la fuente de verdad (ver 7.2) | **Alta** |
| `Ks` (en `HDS5_INLET`) | −0.5 / +0.7 | Declarado como "no figura en la Tabla A.1"; falta la ecuación y página que lo fija | Media |
| `D_INICIO` / `D_PASO` / `D_MAX` | 0.90 / 0.15 / dict | Comentario `VERIFICAR`; norma de producto sin numeral extraído | Media |

**`SPT_ESPACIAMIENTO`** admite la solución más simple del inventario: como no lo
usa nadie, o se le encuentra el numeral en E.050 o **se retira**. Una constante
sin numeral y sin consumidor solo puede hacer daño.

**`D_INICIO`/`D_PASO`/`D_MAX`** se cierran con el mismo acceso documental de G2
(`clases_producto_por_relleno`). No es un frente aparte.

### 7.2 La discrepancia de `K_FRICCION_SI` — la más seria de esta sección

El código usa **19.63** y la hoja de ruta escribe **19.62** en cuatro lugares
(verificado: líneas 436, 440, 794 y 905 de `hoja_de_ruta_alcantarillas_v8.md`).

`constantes_normativas.py` documenta la decisión: gana HDS-5 como fuente
primaria y **la hoja de ruta debe corregirse**. Pero la hoja de ruta es la
fuente de verdad declarada del proyecto, y hoy el código la contradice sin que
ella lo registre.

La diferencia numérica es despreciable (0.05 %). El problema no es aritmético:
es que un revisor que compare los dos documentos encuentra una contradicción
sin resolver en el archivo que el proyecto declara inapelable.

**Cierre:** verificar el valor contra el HDS-5 con página exacta y **corregir la
hoja de ruta**, no el código. Es una edición de cuatro líneas en un `.md`.

### 7.3 Ya resueltas — no volver a abrirlas

Auditorías anteriores listaron estas como pendientes. **Ya están cerradas en el
código**, verificado en esta revisión:

| Constante | Cómo se resolvió |
|---|---|
| `G` | Movida a `constantes_fisicas.py`; `G_LAUSHEY = 9.8` queda con numeral 4.1.1.3.7 c) |
| `COMPACTACION_CORONA` / `_CUERPO` | Numeral cerrado: Manual de Suelos 3.2.1, 3.2.2, 3.3 y 9.1(1) |
| `CALICATAS_POR_KM` / `ESPACIAMIENTO_PERFIL_KM` | Numeral cerrado: num. 4.2, Cuadro 4.1 |
| `h_o` | Ya no es constante: la fórmula vive en M4 y la geometría en `geometria_control_salida` |
| `Q_LIM_NO_SUMERGIDO` / `_SUMERGIDO` | Respaldadas por §4.2 de la hoja de ruta (HDS-5, Tabla A.1, pág. A.8) |
| `NF_profundidad_m` | Reclasificado: hoy es **columna del CSV**, no constante `[N]` |
| `ZONA_SISMICA_LA_UNION` / `Z_E030` | Reclasificados a `[S]` en `datos_sitio.py` |

---

## 8. Ruta de cierre sugerida, por rendimiento

Ordenada por **cuánto desbloquea cada acción**, no por facilidad.

| Orden | Acción | Cierra | Desbloquea |
|---|---|---|---|
| 1 | **Plano de cabezal acotado** (G3) | `predimensionamiento_cabezal`, `inclinacion_muro_beta` | La Fase 9 entera; habilita el turno de `N_cq_N_gammaq_meyerhof` |
| 2 | **Sección típica del terraplén** (G3) | `talud_terraplen`, `pendiente_relleno_trasdos_i` | Fase 7 en B-01 y C-01; el parámetro más sensible de la Fase 9 |
| 3 | **Extraer AASHTO M-170M y M36** (G2) | `h_relleno_min_concreto_tmc`, `clases_producto_por_relleno`, `D_MAX` | Fases 7 y 8 en concreto y TMC |
| 4 | **Clasificar los cauces punto por punto** (G4) | `umbral_area_quebrada_importante_ha` | A-01 y A-02, hoy muertos en la Fase 2 |
| 5 | **Escenarios acotados de TW** (G5, interino) | `TW_receptor` provisionalmente | B-01 y C-01 en Fases 4-5 |
| 6 | **Declarar los tres de G6** | 3 criterios | V3 con número único; K_AE completo; volteo sísmico |
| 7 | **Pedir el EMS con corte directo sobre cantera** (G1) | 4 criterios | Verificaciones geotécnicas del cabezal |
| 8 | **Análisis de homogeneidad SENAMHI** (G4) | `homogeneidad_serie_fen` | Valida — o invalida — todo el Q de diseño |

> **Sobre el orden 8.** Está al final por dependencia de terceros, no por
> importancia. Si la serie resulta no homogénea, el Q de diseño cambia y **con
> él todo lo dimensionado antes**. Conviene lanzar la consulta a SENAMHI el
> primer día aunque su resultado se procese el último.

---

## 9. Cómo cargar un valor cuando llegue

### 9.1 Cierre definitivo

Una línea en `src/criterios_adoptados.py`. El criterio ya existe con su
concepto, justificación y fuente: solo cambia `valor=None` por el valor real, y
se actualiza `fuente` para que deje de decir `PENDIENTE`.

```python
"talud_terraplen": Criterio(
    valor=1.5,                       # <- antes None
    etiqueta="A",
    concepto="Inclinacion del talud del terraplen ...",
    justificacion="...",
    fuente="Seccion tipica del expediente vial, lamina ST-01",   # <- ya no PENDIENTE
    sensibilidad=(1.5, 2.0),         # obligatorio en [A]
),
```

Dos cosas distintas gobiernan ese campo, y conviene no confundirlas:

- **Regla del proyecto** (`Claude.md`): todo `[A]` se defiende con un rango de
  sensibilidad. **No está automatizada** — se verifica en revisión. Hoy hay una
  excepción legítima: `clase_sitio` es `[A]` con valor categórico, y un valor
  categórico no tiene rango que declarar.
- **Invariante automático** (`_coherencia_de_etiquetas()`, al importar el
  módulo): todo `[S]` **debe** declarar `trazabilidad` y **no puede** declarar
  `sensibilidad`; ningún criterio que no sea `[S]` puede declarar
  `trazabilidad`. Esto sí falla al arrancar, no en la memoria.

### 9.2 Corrida exploratoria sin tocar el archivo

Para ver **qué hay detrás** de un bloqueo sin comprometer un valor:

```python
import criterios_adoptados as ca
ca.establecer_valor_dinamico("talud_terraplen", 1.5)   # solo esta corrida
```

`tests/fixtures/datos_referenciales_prueba.md` ya trae un juego completo de
valores de destrabe para exactamente esto. **No son valores verificados y no
pueden ir a una memoria de cálculo** — el propio fixture lo advierte en
mayúsculas. Sirven para responder "si cierro esto, ¿qué aparece después?", que
es la pregunta que ordena el trabajo.

### 9.3 La red que impide el atajo

Tres mecanismos hacen que rellenar un vacío en silencio no pase inadvertido:

- `criterios_sin_valor()` — inventario en vivo, sin provocar la excepción.
- `provisional=True` — marca un valor de prueba; M11 y `reporte_criterios()` lo
  imprimen con marca visible. **Hoy no hay ninguno**, lo que confirma que no
  quedó residuo de la prueba integral.
- `tests/test_sin_literales.py` — rechaza cualquier literal numérico fuera de
  los tres archivos de valores, salvo con marca `# literal-ok: <razón>`.

---

*Verificado contra el código en la rama `claude/repo-contents-tkywpc`.*
*Suite: 654 pasan, 1 se salta. Corrida de referencia:*
*`python cli.py tests/ejemplo_puntos.csv --luz 2.0` — 0 de 4 puntos dimensionados,*
*9 etapas bloqueadas.*
