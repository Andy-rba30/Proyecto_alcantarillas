# INFORME FINAL — T-5 (estructural del conducto, Fase 8 real): correcciones de las dos auditorías + FASE B

Sesión de cierre, 2026-11-12. Worktree `/home/user/wt/T-5`, rama `tesis/T-5`.
Base de integración: `origin/main` = `df1b23c` (T-8). FASE A recibida: `ab7fc3a`
(respaldo intacto en `origin/tesis/T-5-faseA`).

**SHA en `origin/main`: `1522635aa35b2f14d605e6a53b5a28171ddc1f24`.**

---

## 1. IDs

| ID | Veredicto | Por qué |
|---|---|---|
| **INF-3.3.5** (lo que el prompt llama «INF-5.1.5 Fase 8 no verifica nada» e «INF-3.3 carga viva / clase / relleno máximo») | **Cerrado entero, con residuales declarados que dependen de entradas** | La carga de tierra y la HL-93 entran al conducto; clase por D-load (concreto), 12.7.2 con A796 de contraste (TMC), 12.12 (HDPE), demanda del marco, relleno máximo; la Fase 8 que decide la existencia corre también a perfil. Residuales: solo la Clase II de M 170M es legible; el HDPE no tiene veredicto sin el perfil del fabricante; costura empernada sin tabla; pórtico del marco diferido por la hoja de ruta. |
| INF-5.1.5 (canónico: mezcla de marcos, T-7b) | **No tocado** | No es de T-5. |
| INF-5.2.6, INF-0.5, INF-5.1.17 | **Nota añadida, estado sin cambio** | INF-5.2.6: falta un ejemplar legible de M 170M. INF-0.5: `clases_producto_por_relleno` deja de estar vacío (35 → 34 sin valor). INF-5.1.17: el residual de T4-08 queda cerrado. |

Única fila `INF-3.3.k` que T-0 asigna a T-5 en exclusiva: `INF-3.3.5` (comprobado en la hoja `Hallazgos`).

## 2. Tests y par de la suite

- **Nuevos (netos): 201.** `tests/test_t5_estructural_conducto.py` 105 (FASE A, reescritos donde las auditorías los desmintieron);
  `tests/test_t5_correcciones_auditoria.py` **74** (del cierre); 14 anclajes de fichas T5-01..14; 7 en `test_ext5_forma_gui`
  (siete criterios); +2 en `test_t4_materiales_durabilidad` (el caso G2 pasa de 1 test a 3); −1 en `test_criterios_adoptados`.
- **Par medido sobre `origin/main`** («PyMuPDF sí · Tk no», con `NORMAS_DIR`): **5161 passed / 16 skipped / 5177 collected** (sin `NORMAS_DIR`: 5143 / 34).
  Invariante `collected` = **5177** (4976 de `df1b23c` + 201).
- **Rojo de las correcciones** (no se escribieron antes del código; se declara): el archivo de correcciones, corrido sobre la
  FASE A rebasada (`1768b45`): **48 de 71 fallan**; los 23 que valen antes y después son 15 literales del PDF y 8 guardias.
  (El archivo ganó después 3 tests más, para los tres mutantes que quedaban vivos.)
- **Mutación dirigida**: 24 mutantes —los que las dos auditorías dejaron vivos y los de las correcciones—: **24/24 muertos**
  (`scratchpad/T-5/mutantes.py`, `mutantes.txt`). No se repitió la corrida entera del arnés sobre M8 (≈600 mutantes): no cabía en la sesión.
- Dorados a mano, en unidades inglesas y sin M8: `CP_FASE_8_CIERRE` en `tests/fixtures/casos_patron.py` (aritmética escrita;
  script independiente en `scratchpad/T-5/mano.py` y `mano2.py`).

## 3. Números de la línea base movidos, y por qué

Medido con el comparador de E-B (`cli.py --comparar`) contra `df1b23c`, `diff` y `cmp`:

| Archivo | Diferencias | Qué son |
|---|---|---|
| `informe_perfil_ancho.json` | 18 | `F8.CLASE` nueva en A-01 y A-02 (37.424 y 37.042 frente a 50.0 N/m/mm); bloque `estructural` (Clase II; relleno máximo **2.851 m**; contraste Tipo 4: 44.86 / 44.76 N/m/mm y **1.691 m**); texto del diferimiento de la Fase 8; 3 criterios usados; `criterios_sha1`; sin valor 35 → 34; verificación pendiente 27 → 28 |
| `informe_expediente.json`, `informe_rama_error.json` | 3 cada uno | huella y recuentos |
| `cli_perfil_ancho.txt`, tres memorias | — | la fila F8.CLASE, la línea «Fase 8 …», el diferimiento, huellas, recuento 102/35 → 109/34 |
| 2 CSV de resumen, `cli_perfil.txt`, `cli_expediente.txt`, `cli_rama_error.txt`, memoria del cajón | **0 bytes** | — |

**Diámetros movidos: ninguno. Materiales movidos: ninguno.** A-01 y A-02 siguen en concreto reforzado Ø 0.90 m (Clase II);
B-01 sigue «no factible» por V2; C-01 sigue detenido en los criterios del cajón; a expediente los cuatro se detienen donde se detenían.

Fuera de la línea base (declarado, fichas T5-08, T5-02, T5-10): el caso G2 de T-4 deja de dimensionarse con la costura de archivo
(aprobado por el dueño); un tubo de concreto que pida más que la Clase II bloquea el punto; el HDPE no se adopta sin el perfil del fabricante.

Techos de `test_ext8` remedidos, **sin mover**: 70.3 KB y 20.3 páginas por punto a expediente (sobre `df1b23c`: 70.3 y 20.7);
la memoria de perfil, sin techo, pasa de 94.7 a 101.4 KB por punto.

## 4. Diferidos y pendientes (con símbolo)

| Qué | Símbolo | Lo que lo destraba |
|---|---|---|
| D-load de las Clases I, III, IV y V de M 170M | `M8.DIFERIDO_CLASES_M170M`, criterio `clases_producto_por_relleno`, ficha T5-02 | **Un ejemplar legible de AASHTO M 170M o ASTM C76M** (lista del dueño: `docs/contrato_entradas.md`) |
| Perfil del HDPE | criterio `perfil_hdpe_fabricante` (opcional, sin valor), `M8.cota_inferior_hdpe`, ficha T5-10 | Catálogo o certificación del fabricante |
| Costura empernada del TMC | `M8.DIFERIDO_COSTURA_EMPERNADA`, ficha T5-03 | Resistencia de costura del fabricante |
| Flexión combinada y pandeo local del HDPE | `M8.DIFERIDO_FLEXION_HDPE`, `M8.DIFERIDO_PANDEO_LOCAL_HDPE`, ficha T5-05 | Geometría idealizada del perfil / ensayo T 341 |
| Pórtico del marco y empuje lateral | `M8.DIFERIDO_MARCO`, `M8.DIFERIDO_EMPUJE_LATERAL_MARCO`, ficha T5-07 | Diseño por AASHTO Sec. 5 (fuera del alcance por la hoja de ruta) |
| La plancha elegida no vuelve a 7.A / V7 | `M8.verificar_tmc` (aviso), ficha T5-03 | Bucle nuevo sobre MD |
| Carga viva con relleno somero (< 2 ft / ≤ 1 ft) | `MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL`, ficha T5-06 | Implementar AASHTO 4.6.2.10 |
| Equivalencia Proctor Estándar / Modificado de la instalación del concreto | cita `AASHTO_LRFD_9.T12.10.2.1-1` (`Interpretacion`), ficha T5-12 | Tabla 27.5.2.2-3 de AASHTO LRFD Bridge Construction Specifications (no está en `normas/`) |

## 5. SHA y par sobre `origin/main`

- **`origin/main` = `1522635aa35b2f14d605e6a53b5a28171ddc1f24`** (`tesis(T-5): …`, UN commit sobre `df1b23c`, fast-forward con
  `git push origin HEAD:main`). Comprobado tras `git fetch origin main`: `origin/main == HEAD`. La rama `tesis/T-5` quedó empujada en
  ese mismo commit; `origin/tesis/T-5-faseA` sigue en `ab7fc3a`, sin tocar.
- **Par medido sobre ese árbol** (worktree limpio en `1522635`, «PyMuPDF sí · Tk no», `NORMAS_DIR` enlazado):
  **5161 passed, 16 skipped, collected 5177.** Sin `NORMAS_DIR`, medido sobre el mismo contenido antes del commit: 5143 passed, 34 skipped.
- Una medida adicional sobre una exportación `git archive` de `origin/main` dio 5160 passed + 1 failed
  (`test_ext11_mutacion::test_el_arnes_mata_de_verdad_un_mutante_conocido`): es un artefacto de la exportación —el arnés de mutación
  necesita `git ls-files` y la exportación no tiene `.git`—, no del árbol; sobre el checkout real pasa.
- Las otras tres configuraciones de la tabla de CLAUDE.md (5174/3, 5071/106, 5058/119) son **derivadas, no medidas**.

## 6. Hallazgo → corregido / refutado (las dos auditorías, todas las severidades)

F = `AUDITORIA_T-5_fable.md`; O = `AUDITORIA_T-5_opus.md`.

| Hallazgo | Sev. | Resultado | Evidencia |
|---|---|---|---|
| **F-H1** vehículo por presión y no por efecto | ALTA | **Corregido** | `carga_viva_enterrada(efecto=…)`: cada consumidor pasa su medida (W_L; P_L·C_L·F_1; P_L en el marco, que es cota superior). Dorado a mano: concreto Ø 2.10, H_rel 0.47 → tándem, W_L 102.41 kN/m, **38.727 N/m/mm** (camión 30.747). `_hl93_a_mano` ya no elige. Test por AST: las 4 llamadas pasan `efecto=`. A-01/A-02: D-load **sin cambio** (B_c < l_w en los dos vehículos). |
| **F-H2 / O-H11** carga viva despreciada pasados 8 ft sin criterio | ALTA / BAJA | **Corregido** | AASHTO 3.6.1.2.6a, pág. 3-26 (PDF 80): «may be neglected where the depth of fill is more than 8.0 ft and exceeds the span length; for multiple span culverts … distance between inside faces of end walls». Criterio [A] `carga_viva_bajo_relleno_alto` = `conservar` (decisión 4), `despreciar_3_6_1_2_6a` barrible con aviso del punto. Dorado: 2.90 m → 50.587 (no alcanza) contra 46.043. Marco multicelda: `luz_del_permiso` = N·B + (N−1)·t. |
| **F-H3 / O-H1** HDPE excluido en todo el dominio, mínimos «not meaningful» | MEDIA / ALTA | **Corregido** (decisión 2) | C12.12.3.2, pág. 12-76 (PDF 1714): «have been minimum values and are not meaningful for design»; 12.12.3.2: «…or obtained from the pipe manufacturer». `perfil_hdpe_fabricante` opcional; sin él `DatoFaltanteError` con rótulo «no verificado con un producto real» y la cota inferior. Relleno: EG-2013 508.02 d), pág. 982 (PDF 990): «La cama de asiento y la sujeción lateral se construirán con material granular … Subsección 400.02 y la Sección 301» → `Si-95`. Test que fija que con `Cl-95` no cumple a ninguna altura (0.90/1.05/1.20 × 10 alturas). |
| **F-H4 / O-H3** `fabricacion_tmc` y el test G2 de T-4 | MEDIA / ALTA | **Corregido** (decisión 3) | Test de T-4 restaurado de `origin/main` y reescrito a la verdad nueva declarándolo; valor de archivo remachada simple; aviso fijo `AVISO_COSTURA_DE_OTRA_FABRICACION`; justificación corregida (EG-2013 507.02 a), pág. 969: «…y sus accesorios (pernos, tuercas) … perforado» = empernada, con `Interpretacion`). Tabla 5 de A796 **releída por imagen valor a valor** (PDF 8): 244/315, 266/435, 341/683, 357/715, 374/748 — coincide; Tabla 7 (PDF 9): 419, 521, 773, 929, 1032 — coincide. |
| **F-H5 / O-H7** clases sin diámetros; mensaje falso; `F8.CLASE` no podía ser `False` | MEDIA | **Corregido** | `DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM` (I: 1500; II–V: 300; leído por imagen, PDF 3, 4, 6, 8, 10); `clases_de_concreto_para`; con todas las superiores declaradas → `cumple=False` frente a la mayor; clave ajena → `DatoInvalidoError`. |
| **O-H2** «Tipo 3 el más desfavorable», `tipo_4` fuera de la ventana | ALTA | **Corregido** (decisión 1, con precisión contra la fuente) | `tipo_4` en la ventana; contraste impreso (`F8.TIPO4`, `F8.HMAX_TIPO4`); test renombrado. Ver §7.1. |
| **O-H4** pandeo del HDPE sin anclar en 12.12.3.3 | MEDIA | **Corregido** (decisión 7) | 12.12.3.3, pág. 12-76: «Investigation of general buckling shall be based on the value of modulus of elasticity that represents the design life of the project». `u_letra` (todo a largo plazo) y `u_duracion`; rige la mayor. Dorados: Cl-95 0.5134 / 0.4881; Si-95 0.1750 / 0.1945. |
| **O-H5** falta el FF del HDPE | MEDIA | **Corregido** | 12.12.3.6 (pág. 12-82, PDF 1720) y 12.5.6.3 (pág. 12-14, PDF 1652: «shall not exceed 95.0 in./kip»). `F8.FF` del HDPE, fundamento `F8.HDPE_FF`; diámetro exterior y módulo inicial. 36 in: 0.4224 ≤ 0.5425 mm/N. |
| **O-H6** docstring «subir de diámetro no lo resuelve» | MEDIA | **Corregido** | Docstring y ficha T5-02 reescritos; test con el contraejemplo (52.2 / 41.7 / 36.0). El bloqueo se sostiene por decisión 6. |
| **F-H6 / O-H8** huecos de mutación | MEDIA | **Corregido** | Tests con dorado para: deflexión admisible, rama elástica de 12.7.2.4-2 (105.238 MPa) y su umbral, H_max de TMC (área y costura) y HDPE, primer cruce con hundimiento estrecho, NF (ΔT 3.1751 kN/m; Δε 0.0059019), márgenes, marco con H ≠ 1, contraste ASD, relleno por plancha, `H_total_m`. 24/24 mutantes dirigidos muertos. |
| **F-H7** `caracter="EXIGENCIA"` a mano | MEDIA | **Corregido** | `_campos_f8` lee el carácter de la cita (`caracter_del_umbral`); `F8.DEFLEXION` → RECOMENDACION, cita C12.12.2.2. Test por AST. |
| **F-H8 / O-H13** nivel «medido» de 4 criterios | BAJA | **Corregido** | Corridas de perfil que llegan al TMC y al HDPE (concreto y TMC fuera por `D_max_catalogo`); comentario del bloque dice qué corrida midió cada uno. |
| **F-H9** fila «< 2.0 ft» de B_FLL muerta | BAJA | **Corregido** | Rama retirada; la constante queda como transcripción. |
| **F-H10** docstrings atrasados | BAJA | **Corregido** | `servicio.correr_punto`; `pesos_especificos_de_carga` («NO PUEDE GOBERNAR»); ficha T5-09. |
| **F-H11 / O-H9** diferido global | BAJA | **Corregido** | M11 y JSON imprimen `ResultadoEstructural.diferido`. |
| **F-H12** dorados que repiten la fórmula | BAJA | **Corregido** | Marco con dorado a mano en 1.00 y 1.50 m (56.32 y 51.39 kN·m/m); TMC Ø 2.10 con F_1 y cambio de vehículo a mano; `_hl93_a_mano` sin regla. |
| **F-H13** pie de los commits | BAJA | **Corregido** | Un solo commit con el pie de ORQUESTACION. |
| **F-H14 / O-H12** entradas raras | BAJA | **Corregido** | `conducto` fuera de `CONDUCTOS` → `DatoInvalidoError`; `incremento_dinamico_enterrado` con cubierta negativa/NaN → `DatoInvalidoError`; clases ajenas. |
| **F-H15** ASD con m = 1.20 | BAJA | **Corregido** | Nota del paso: «NO ES A796 PURO». |
| **O-H10** «más desfavorable» en la cabecera | BAJA | **Corregido** | Cabecera del bloque y `justificacion` de `parametros_diseno_hdpe`. |
| **O-H14** motivo engañoso y «sube de diámetro inútilmente» | BAJA | **Corregido en parte / refutado en parte** | Motivo: `ACLARACION_DESCARTE_POR_FASE_8` detrás del texto del Anexo B. **Refutado** cortar la progresión: la monotonía no vale en general (el propio O-H6 mide que la D-load baja con el diámetro en relleno somero). |
| Sospecha F: 12.7.2.2 sin K_γE | — | **Declarada** | Nota del paso `F8.T` («lectura de la menor demanda y la letra no la dice», con la razón 1.30 × 1.5 = 1.95). |
| Sospecha F: baterías de tubos | — | **Sin efecto con el valor de archivo** | El catálogo circular no ofrece multibarril (N = 1) y con `conservar` el permiso no se toma; el marco multicelda sí usa la distancia entre muros extremos. |
| Sospecha F: «VARIOS» | — | Sin cambio | Sigue rotulado «según el INFORME §1.1; páginas no verificadas». |
| Verificado por mí contra el PDF en esta sesión | — | — | 3.6.1.2.6a (80); 1.3.5 (22); 12.5.4 (1649); 12.5.6.3 (1652); Tabla 12.10.2.1-1 y su nota de Proctor (1688-1689); 12.12.3.2 / C12.12.3.2 / 12.12.3.3 (1713-1714); Tablas 12.12.3.5-1/-2 y 12.12.3.6 (1719-1720); EG-2013 205.02 y Tabla 205-01 (193-194), 205.12(c)(1) (201), Tabla 301-01 (246), 502 (903-907), 506 (967-969), 507 (977-978), 508 (989-992); Manual de Puentes 2.3.2.5 (100); A796 Tablas 5 y 7 (imagen); M 170M Tablas 1, 3, 4, 5 (imagen). |

## 7. Decisiones del dueño (2026-11-12) aplicadas, con su antes / después

### 7.1 Instalación del tubo de concreto — Tipo 3 de archivo, `tipo_4` en la ventana, Tipo 4 impreso al lado
- **Antes (FASE A):** Tipo 3, ventana (1, 2, 3), justificado como «el más desfavorable que la norma peruana admite».
- **Después:** Tipo 3, ventana (1, 2, 3, **4**); pasos `F8.TIPO4` y `F8.HMAX_TIPO4`.
- **A-01 (concreto Ø 0.90):** Tipo 3: 37.42 N/m/mm, Clase II, relleno máximo **2.851 m**. Tipo 4: 44.86 N/m/mm, Clase II, **1.691 m**.
  (La FASE A imprimía 3.183 m, por la carga viva despreciada: 7.4.)
- **PRECISIÓN CONTRA LA FUENTE PRIMARIA (para el dueño):** la decisión justifica el Tipo 3 en «EG-2013 508.07 exige > 95 % del
  Proctor Modificado». **El 508.07 es de la tubería de polietileno.** Para el tubo de concreto rigen 506.07 y 506.10 (solado de
  subbase granular de 15 cm y sujeción hasta 1/6 del diámetro exterior, compactados como la corona: 95 % PM) y, por encima,
  506.11 → Sección 502 → 205.12(c)(1): materiales de terraplén (Tabla 205-01: A-1-a, A-1-b, A-2-4, A-2-6, A-3) al **90 %** PM.
  **La decisión (Tipo 3) se aplicó igual**, porque su sustancia se sostiene —el EG-2013 exige compactar todo el relleno, que es
  lo que el Tipo 4 no pide—, con la justificación corregida y **una condición declarada** en la `Interpretacion` de la cita
  `AASHTO_LRFD_9.T12.10.2.1-1`: la Tabla 12.10.2.1-1 gradúa en Proctor **Estándar** y remite la equivalencia a la Tabla
  27.5.2.2-3 de la especificación de construcción de AASHTO, **que no está en `normas/`**. Sin ella, el 90 % PM garantiza el
  Tipo 3 con relleno granular o limoso (pide 85 y 90 %), pero **no** con el A-2-6, para el que pide 95 %. Si el dueño prefiere
  la cota que no depende de esa equivalencia, es `tipo_4` (una declaración; no mueve la clase de A-01/A-02).

### 7.2 HDPE — perfil del fabricante, «no verificado con un producto real», relleno granular
- **Antes:** verificado con el perfil mínimo de la Tabla A12-11 y `Cl-95` → «no cumple» a cualquier altura (medido: 0.90/1.05/1.20 m × 0.35–10 m).
- **Después:** `perfil_hdpe_fabricante` [A] opcional sin valor. Sin él: `DatoFaltanteError` con el rótulo y la cota inferior;
  el HDPE **no se adopta**. Relleno de archivo `Si-95` (EG-2013 508.02 d) + Sección 301 → A-1 / A-2-4 → Sn o Si, la menos favorable).
- **Cota inferior con `Si-95`, 0.90 m en A-01:** ε = 0.0356 ≤ 0.041; pandeo 0.194 ≤ 0.70; deflexión 0.0317 ≤ 0.045 m; FF 0.422 ≤ 0.542 mm/N; relleno máximo ≈ 1.48 m.
- **No choca con el fixture:** el HDPE es el último candidato; A-01 y A-02 cierran en concreto antes; B-01 falla V2 antes de la Fase 8.
- **Regla derivada, aplicada (decisiones 2 y 6):** cuando la Fase 8 detiene por dato faltante un escalón que cumple toda la tabla de
  la Fase 5 y ningún candidato cierra, el punto sale **`DatoFaltanteError`** (con el campo), no «no factible» (`MD.ATRIBUTO_ESCALON_CUMPLE_LO_DEMAS`).
  La otra mitad de T4-10 no cambia. **Si el dueño prefiere el «no factible» de antes para ese caso, es una línea de MD.**

### 7.3 `fabricacion_tmc` = remachada simple; el caso G2 de T-4 cambia
- **Antes (`df1b23c`):** G2 (Q = 6 m³/s, ~8.5 m de relleno) → TMC Ø 1.95 m adoptado sin verificación estructural.
- **Después:** no se dimensiona: `F8.COSTURA` 320.7 kN/m > 0.67 × 374 = 250.6 kN/m con la plancha de 4.27 mm (la última de la tabla; la progresión sube hasta ella).
  Con `anular_remachada_doble` o `helicoidal` declaradas: TMC Ø 1.95 m, plancha 68×13/4.27. El veredicto dice qué otra fabricación lo desarrollaría.
- El test de T-4 se restauró de `origin/main` y se reescribió declarándolo (qué pasaba, qué pasa, por qué).
- **Para el dueño:** el EG-2013 507.02 a) describe tubería **empernada**, sin resistencia tabulada. Hoy `anular_empernada` detiene la Fase 8 pidiéndola.
  Alternativa no aplicada: tratar la costura empernada como dato diferible a nivel de perfil (TMC dimensionado con aviso «costura sin verificar»).

### 7.4 Carga viva sobre 8 ft — conservar
- **Antes:** despreciada siempre. Relleno máximo de A-01/A-02 con Clase II: 3.183 m; a 2.90 m «cumplía» (46.04).
- **Después:** conservada. Relleno máximo **2.851 m**; a 2.90 m, 50.59 > 50.0. `despreciar_3_6_1_2_6a` barrible (reproduce 3.18 m).

### 7.5 η_I = 1.05 — se mantiene, como clasificación del Propietario
- La fuente **no lo prescribe**: 12.5.4 (pág. 12-11) fija la redundancia («shall be considered redundant» → η_R = 1.00) y dice que la
  clasificación operativa se determina por la continuidad de función o la seguridad de la vía; 1.3.5 (pág. 1-7): «The Owner may declare…».
  Sigue [A], ventana (0.95, 1.05) del Manual de Puentes 2.3.2.5. Sin cambio numérico.

### 7.6 Concreto que pide más que la Clase II — bloquear
- `DatoFaltanteError` sobre `clases_producto_por_relleno`, con las clases que faltan **para ese diámetro** y lo que lo destraba.
- **Entrada para el dueño** (`docs/contrato_entradas.md`): **un ejemplar legible de AASHTO M 170M (vigente) o ASTM C76M**.
  Con solo la Clase II y el Tipo 3: ~2.85 m de relleno sobre un tubo de 0.90 m.

### 7.7 Pandeo del HDPE — letra de 12.12.3.3
- **Antes:** suma por duración. **Después:** `u_letra` (todo con el módulo de la vida de diseño) y `u_duracion`, rige **la mayor**.
  Con `Cl-95` gobierna la letra (0.513 > 0.488); con `Si-95`/`Sn-95`, la suma por duración (0.194 > 0.175).
  **Si el dueño quiere la letra a secas (sin el máximo), es menos conservador con relleno granular.**

## 8. Lo que NO hice, sin adornos

- No repetí la corrida completa del arnés de mutación de EXT-11 sobre M8 (≈600 mutantes): solo 24 mutantes dirigidos.
- No medí las tres configuraciones con Tk o sin PyMuPDF (el contenedor no tiene tkinter): se dicen **derivadas**.
- No transcribí el último diámetro con diseño estándar de cada clase de M 170M (solo se lee con seguridad en I, II y V): se
  implementó el **primer** diámetro tabulado, que es lo que cierra el defecto auditado.
- El área efectiva del HDPE sigue saliendo del mínimo de M 294 núm. 7.7 aunque el perfil esté declarado (falta 12.12.3.10.1b).
- El motivo de MD de un escalón rechazado por `F8.COSTURA` no incluye la «pista» de la otra fabricación: está en el paso de la memoria.
- No toqué `verificar_sesion.py` (no lleva conteos).
