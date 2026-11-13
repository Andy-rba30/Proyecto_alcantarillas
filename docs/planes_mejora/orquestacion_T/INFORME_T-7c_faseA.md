# INFORME T-7c · FASE A — cabezal: armado o concreto ciclópeo (Fase 9)

- Rama: `tesis/T-7c`, creada desde `origin/main` = `451a10a`. **No fusionada ni empujada a `main`.**
- SHA de la rama al cerrar la FASE A: `f50edbe` (`f50edbe4abfacfa586d5bfd117e3192f13973909`) (empujada a `origin/tesis/T-7c`).
- Fecha: 2026-11-13. Worktree: `/home/user/wt/T-7c`.
- No se tocaron: el tracker `.xlsx`, la tabla de conteos de `CLAUDE.md`, `verificar_sesion.py`,
  `/home/user/Proyecto_alcantarillas`, `/home/user/wt/main`, `/home/user/wt/estado`.

## 1. IDs: entero / en parte / no

| ID | Veredicto | Con qué |
|---|---|---|
| `INF-4.6` (flexión y corte de pantalla y zapata, mínimos, recubrimientos, espaciamiento; o ciclópeo) | **Entero, con residuales declarados** | `M9.diseno_flexion_corte`, `M9.armar_elemento`, `M9.ensamblar_armado`, `M9.verificar_cabezal_ciclopeo`, cableados en `servicio._fase_9_armado`. Residuales con ficha: T7C-03 (cortante general y estribos), T7C-04 (zapata y secciones intermedias del alero), T7C-06 (fisuración 5.6.7, desarrollo, empalmes), T7C-09 (zapata del ciclópeo y su condición sísmica). |
| `INF-3.4.5` (fila «Armado» del §3.4, vinculada a INF-4.6) | **Entero**, mismos residuales | Lo mismo. No lo nombra el encargo; lo cierra el mismo código. |
| Ficha `EXT-7-01` (ec. 11-32 sin evaluar; los tres criterios de cortante alto vacíos) | **Cerrada** | `M9.cuantia_vertical_ec_11_32` (completa, con sus dos topes); los tres criterios tienen valor: `cortante_alto_muro_e060_art_11_10_10_2` = 0.0025 [N→], `cuantia_vertical_cortante_alto_e060_art_11_10_10_3` = 0.0025 [N→], `regimen_cortante_muro_e060_art_11_10_2` = perpendicular al plano [A]. |
| `NotImplementedError` de `M9.diseno_flexion_corte` | **Retirado** | Test `test_diseno_flexion_corte_ya_no_lanza_NotImplementedError`. |
| Pregunta de T-7a: rótulo por ámbito de E.060 22.7.4 | **En parte** | Todo lo de E.060 que T-7c **usa** entra como [N→] / «por analogía». La constante de T-7a `ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M` (0.30 m, [N]) **no se movió**: ficha T7C-10 y pregunta 1 de abajo. |
| `INF-0.5` (criterios vacíos) | Nota, no cierre | Los sin valor pasan de 22 a 19 (136 criterios; 129 en la base). |

## 2. Qué se hizo

**Marco que rige: AASHTO LRFD 9.ª ed., Sección 5**, sobre las solicitaciones factoradas de T-7b
(Resistencia I; Evento Extremo I con φ = 1.0 por 1.3.2.1). Flexión por 5.6.3.2 con el bloque de
5.6.2.2 y la sección controlada por tracción (5.6.2.1); mínimo de 5.6.3.3 (el menor de 1.33·M_u y
M_cr); cortante por 5.7.3.3 con el procedimiento **simplificado** de 5.7.3.4.1 (β = 2.0) donde la
fuente lo permite, y `MetodoNoEvaluableError` (rótulo `MOTIVO_METODO_NO_EVALUABLE_ARMADO`) fuera
de él; acero de retracción y temperatura de 5.10.6; espaciamientos de 5.10.3.2 y 5.10.6. Todo en
SI: las constantes de la fuente se convierten **en la constante** (`VC_COEFICIENTE_AASHTO_SI`,
`MODULO_ROTURA_AASHTO_SI`, `TEMPERATURA_COEFICIENTE_AASHTO_SI`, bloque `# --- T-7c ---` de
`constantes_normativas.py`). El MCFT general, transcrito en ksi y pulgadas, queda bajo una clave
rotulada «no ejecutable» del criterio `procedimiento_flexion_corte_aashto_sec5`.

**E.060 en paralelo, de contraste [N→]**: fila A5 de cada sección, con las combinaciones de
E.060 9.2.5 y los φ de E.060 (0,90 y 0,85) sobre las mismas cargas sin factorar. Informa
(veredicto INDICADOR si no cumple) y no decide. **Los marcos no se cruzan**: lo fija
`test_las_resistencias_de_E060_solo_se_comparan_con_cargas_de_E060`. En los **mínimos
constructivos** rige el más exigente de los dos (`regla_minimos_constructivos_cabezal` [A], con
`solo_aashto` barrible).

**Empuje con que se arma: K0** (`regimen_resistencia_elementos_cabezal` [A] = `no_cedente_k0`,
`cedente` en la ventana). La estabilidad externa de T-7b no se tocó. Solo se escalan el empuje del
suelo (a (K0/K_A)·P_A, horizontal, con el factor 1.35 de la fila «En reposo») y el de la
sobrecarga; en cada sección rige la **mayor** de reposo y activo y las dos se imprimen, con aviso
por `avisos()` cuando la barra propuesta cambia. Bajo sismo no se inventa un K0 sísmico: se usa
el empuje del ensamble y, en pantalla y aleros, la mayor de su posición y la resultante a h/2
(C11.6.5.4); si la cadena sísmica redujo k_h, se avisa.

**Zapata**: presión de contacto **lineal** (AASHTO 10.6.5, que la exige para el diseño
estructural; la de T-7b es la uniforme de capacidad portante), con la subpresión en la punta, y
talón con el **peso entero** (11.6.1.2). **Aleros**: armados en su arranque, con aviso de lo que
no cubren. **Ciclópeo**: `M9.verificar_cabezal_ciclopeo` (C1 a C6), alcanzado por la puerta del
tipo declarado y probado de punta a punta por `servicio.correr`.

**Sin iterar dimensiones**: se arma la geometría que T-7a propone; si una sección no cumple, la
fila no cumple y lo dice. **Barras y espaciamientos** de un catálogo [A]
(`catalogo_barras_refuerzo_cabezal`). **Recubrimiento sin dato**: `categoria_refuerzo_aashto` y
`exposicion_quimica_ems` siguen sin valor; el peralte efectivo se calcula con la cota más exigente
(91.44 mm) y se avisa (ficha T7C-05).

**Tabla de armado**: `ArmadoDelCabezal.tabla` (`FilaDeArmado`), pasos de memoria `F9.ARM_*` y
`F9.CICLOPEO`, volcado en el JSON (`armado`) y en la CLI de texto. La maqueta en M11 es de T-10 y
no se tocó.

Siete criterios nuevos (todos de expediente, [A]): `regimen_resistencia_elementos_cabezal`,
`fc_cabezal_mpa` (21 MPa, ventana 17.5–35), `acero_refuerzo_cabezal`,
`catalogo_barras_refuerzo_cabezal`, `regla_minimos_constructivos_cabezal`,
`criterio_traccion_cabezal_ciclopeo`, `concreto_ciclopeo_cabezal`. Cuarenta citas nuevas
(AASHTO LRFD y E.060), todas con numeral, página impresa, página del PDF, texto literal y
carácter, verificadas por `tests/test_normativa_pdf.py`; diez fundamentos `F9.*`. El registro
queda en 494 citas.

## 3. Tests y par medido

- **Archivo nuevo**: `tests/test_t7c_cabezal_armado.py`, **207 tests** (201 rápidos y 6 `lento`;
  21 con la marca `pdf`). Dorados a mano con la aritmética escrita en
  `tests/fixtures/casos_patron.py`: `CP_T7C_ARMADO`, `CP_T7C_EC_11_32`,
  `CP_T7C_TEMPERATURA_PUBLICADA` (los tres ejemplos que publica el comentario C5.10.6),
  `CP_T7C_CICLOPEO`, `CP_T7C_BASE_SERVICIO`.
- **Delta de la suite, medido por archivo** (`--collect-only` en la base y en la rama):
  +207 (archivo nuevo), +10 `test_decisiones_diferidas` (fichas T7C-01..10), +7
  `test_ext5_forma_gui` (siete criterios), −3 `test_criterios_adoptados` (tres criterios dejan de
  estar vacíos). **Neto +221.** (El desglose por archivo se midió con 203 en el archivo nuevo;
  después se añadieron cuatro tests más en él, y el total de la suite confirma los 221.)
- **Par medido de la rama** (UNA configuración: PyMuPDF sí · ventana Tk no · `NORMAS_DIR`
  enlazado), suite entera: **6200 passed, 23 skipped, collected 6223**. Base `451a10a`:
  5979 / 23 / 6002. Se midió sobre el árbol de `f10b5a8` más el párrafo de la ficha T7C-08;
  después de la medida solo cambiaron una cifra de ese párrafo y los sellos de los generados, y
  los tests de sincronía, de fichas, de línea base y las guardias se volvieron a correr (403
  passed). Las otras tres configuraciones y la corrida sin `NORMAS_DIR` **no se midieron**. Los
  tests `pdf` pasan de 124 a 145; los 21 nuevos abren AASHTO LRFD y E.060.
- **Rojo contra la base**: no se escribió con `xfail(strict=True)` antes del código (ficha
  T7C-08). Se midió copiando el archivo y el fixture a un árbol exportado de `451a10a`: el archivo
  entero falla en la recolección (`ImportError: cannot import name 'MARCO_E060'`). Es un rojo de
  recolección, no test a test.
- **Tests reescritos declarándolo**: `tests/test_M9_cabezal.py` (dos, que fijaban el
  `NotImplementedError` y los vacíos de cortante alto), `tests/test_ext7_cabezal.py` (cuatro),
  `tests/test_memoria_sustentada.py` (diez fundamentos que la corrida por defecto no alcanza),
  `tests/test_sin_literales.py` (censo de M9: 13 → 18 marcas).

### Mutación (arnés de EXT-11, `tests/apoyo/mutacion.py`)

Sobre una copia en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7c/mut/`, las 34 funciones nuevas de M9 (**1007 mutantes**), con los
tests rápidos de `tests/test_t7c_cabezal_armado.py` como único objetivo:

- Primera medida: **748 muertos de 1007 (74.3 %)**, 259 vivos.
- Se escribió la sección 13 del archivo, «lo que la mutación enseñó» (20 tests: márgenes de las
  cinco filas, el contraste de E.060 que no cumple, fronteras de 16.0 in / 3·d_v / 18.0 in / la
  serie del catálogo, entradas inválidas, talón «más exacto» con y sin agua, fila de
  recubrimiento por cara, agua y freático a media altura en el ciclópeo, rige V_u/φ).
- Medida final: **843 muertos de 1007 (83.7 %)**, 164 vivos. Es la suma de una segunda medida
  entera (829) y una tercera parcial de las cuatro funciones cuyos tests cambiaron después
  (`solicitaciones_de_resistencia`, `diseno_flexion_corte`, `acciones_sobre_una_seccion`,
  `verificar_cabezal_ciclopeo`). No es una única corrida.

Los 164 vivos, clasificados por clase (con una heurística sobre el JSON del arnés, no uno a
uno, y sin censo fijado en un test):

| Clase | Vivos |
|---|---|
| Frontera de un umbral con tolerancia (`>=` por `>`, `± TOL_UMBRAL_NORMATIVO`): solo se distinguen en el valor exacto del umbral | 43 |
| Guardias de entrada (`_finito(x) and x > 0` y parecidas) en combinaciones que ningún dato válido distingue | 16 |
| Valores por omisión o de relleno que no se alcanzan (`.get(k, 0.0)`, `x if x is not None else 0.0`) | 37 |
| Texto de un aviso o de una procedencia | 3 |
| Otros | 65 |

De los 65 «otros», la mayoría son cifras de presentación de la memoria y fronteras donde las dos
ramas dan el mismo valor (por ejemplo `beta_1_e060` en 28 MPa, o la búsqueda de la solicitación
de la pantalla por combinación, que es equivalente porque las dos Resistencia I de T-7b dan a la
pantalla la misma solicitación). **Huecos reales que quedan vivos y no cerré:**

- el aviso de la punta sin presión de contacto evaluable (`solicitaciones_de_resistencia`);
- el umbral numérico del aviso de 0.5·φ·V_c en la pantalla (`diseno_flexion_corte`);
- la fila C6 del ciclópeo cuando **no** cumple, bajo cada criterio de tracción (el indicador
  `decide`), y el aviso del vuelo de su zapata (`verificar_cabezal_ciclopeo`);
- el empuje activo **inclinado** en las secciones del cuerpo del ciclópeo
  (`acciones_sobre_una_seccion`: en el dorado la inclinación es nula);
- el aviso de «ninguna barra del catálogo» y varias ramas de texto de `ensamblar_armado` y
  `_armado_con_el_otro_regimen`.

Los informes del arnés están en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7c/` (`mutacion_t7c_vuelta1.json`, `…_vuelta2.json`,
`…_vuelta3.json`, `mutacion_t7c_final.json`), fuera del repositorio.

## 4. Números movidos

**Diámetros, secciones, materiales y HW movidos: ninguno.**

Línea base de la Familia C regenerada y medida contra `451a10a` con el comparador de E-B
(`cli.py --comparar`): 4 diferencias en `informe_expediente.json` y 2 en cada uno de los otros
tres, 0 «no comparables». Son las huellas, el recuento de criterios («129 / 22» → «136 / 19») y
dos notas del bloque del cabezal. `cli_perfil.txt`, `cli_perfil_ancho.txt`, `cli_familia_c.txt`,
`cli_rama_error.txt`, `memoria_punto_cajon.html` y los dos CSV de resumen no cambian un byte. Ninguna
corrida de la línea base llega a armar: sin declarar nada, V5 sigue detenida en
`remanso_derecho_via` y ningún punto alcanza la Fase 9 a nivel de expediente (a perfil se difiere
entera), de modo que el armado no aparece en la línea base.

Con los datos de prueba rotulados de T-7b (A-01, no son del expediente) el armado corre entero:
entrada, pantalla M_u 31.36 kN·m/m (activo 23.37) → Ø 1/2" @ 0.20 m; salida, pantalla 75.68
(activo 52.96) → Ø 1/2" @ 0.10 m; el punto sigue en Ø 0.90 m.

## 5. Diferidos, con su símbolo

| Ficha | Qué | Símbolo |
|---|---|---|
| T7C-03 | Procedimiento general de cortante (5.7.3.4.2) y estribos; fuera del simplificado, método no evaluable | `M9.simplificado_permitido` |
| T7C-04 | Zapata y secciones intermedias del alero | `M9.armar_elemento` |
| T7C-05 | Recubrimiento del proyecto (faltan EMS y categoría del acero); se arma con la cota de 91.44 mm | `M9.recubrimiento_para_armar` |
| T7C-06 | Fisuración en servicio (AASHTO 5.6.7), desarrollo y empalmes | `M9.espaciamiento_maximo_del_armado` |
| T7C-07 | La interfaz de T-7b sigue entregando la zapata con presión uniforme (el armado no la usa) | `M9.solicitaciones_de_la_zapata` |
| T7C-09 | Ciclópeo: solo estático; su zapata no se verifica como voladizo de concreto simple | `M9.verificar_cabezal_ciclopeo` |
| T7C-10 | El 0.30 m de E.060 22.7.4 sigue como constante [N] | `constantes_normativas.ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M` |
| T7C-01, T7C-02 | Lo que queda abierto dentro de lo cerrado: η del cabezal, K0 de terreno horizontal, sismo sin K0 | `M9.diseno_flexion_corte`, criterio `regimen_resistencia_elementos_cabezal` |
| T7C-08 | Aceptación escrita después del código | `tests/test_t7c_cabezal_armado.py` |

## 6. Filas del tracker a escribir en la FASE B (no se escribieron)

- `INF-4.6`: Cerrado — responsable «Claude Code (cadena T, T-7c)», commit `tesis(T-7c)`.
- `INF-3.4.5`: Cerrado, mismos datos (vínculo de INF-4.6).
- `INF-0.5`: nota (sin valor 22 → 19; tres de cortante alto con valor).
- `EXT-M-05` y `R95-031`: nota (los tres criterios que EXT-7 dejó vacíos tienen valor; la ec.
  11-32 se evalúa).
- `INF-4.3` (Cerrado parcial): nota (los aleros se arman en su arranque; siguen abiertos zapata y
  secciones intermedias).

Además, para la FASE B: fila de T-7c en `LO_QUE_ESCRIBIO_CADA_PROMPT`
(`tests/test_t0_gobernanza.py`), la tabla y el párrafo de `CLAUDE.md`, renumerar la «Parte LI
(rótulo provisional)» de `docs/decisiones_diferidas.md` según el orden de integración, y
**resellar** los cuatro documentos generados con el par de `origin/main`.

## 7. Preguntas para el dueño

1. **Rótulo de E.060 22.7.4 (0.30 m de zapata de concreto simple).** Opciones: (a) dejarlo [N]
   como hoy, por la «excepción de durabilidad» de la §0.2 de la hoja de ruta; (b) pasarlo a
   criterio [N→] (saca la constante de `constantes_normativas`, reescribe CB6 y dos tests de
   T-7a). **Recomiendo (b)**, en una sesión aparte, y decidir a la vez las cuantías de 14.3.1 y
   el recubrimiento de 7.7.1, que tienen la misma objeción.
2. **Recubrimiento sin dato.** El encargo pedía 70 mm; se usa la cota de 91.44 mm con aviso.
   Opciones: (a) mantener la cota; (b) 70 mm. **Recomiendo (a)**: 70 mm supone la categoría del
   acero y la agresividad del sitio.
3. **Talón.** Peso entero (11.6.1.2, regla por defecto) o método más exacto (del orden de 2.6
   veces menos momento en el muro de tanteo: 22.05 frente a 56.89 kN·m/m). **Recomiendo el peso
   entero**, con el exacto impreso, como está.
4. **Pantalla y AASHTO 5.7.2.3.** Se trata como losa (no se le pide refuerzo transversal por
   encima de 0.5·φ·V_c; se avisa). Opciones: (a) mantener; (b) exigir V_u ≤ 0.5·φ·V_c en la
   pantalla. **Recomiendo (a)** y revisar si algún cabezal real dispara el aviso.
5. **Clase de exposición para la fisuración (5.6.7).** No se evalúa. Hace falta que el
   Propietario la declare (γe 1.00 o 0.75) y decidir d_c. **Recomiendo** dejarla como entrada del
   contrato (ya está en `docs/contrato_entradas.md` §3.4).
6. **Modificador de carga η del cabezal.** T-7b no lo aplica (el conducto usa η_I = 1.05). El
   armado hereda sus solicitaciones. **Recomiendo** decidirlo en T-7b o T-11, no en el armado.
7. **k_h reducido con régimen no cedente.** Hoy solo se avisa. Opciones: (a) avisar; (b) armar el
   Evento Extremo con k_h = k_h0. **Recomiendo (b)** si el dueño confirma el régimen no cedente
   para el armado: es lo que dice 11.6.5.4 a la letra. No lo hice porque cambia el empuje sísmico
   de T-7b.
8. **Tracciones nulas en el ciclópeo.** Es criterio del proyecto y ninguna fuente lo exige; un
   muro esbelto con sobrecarga de tráfico no lo cumple y sí la tracción admisible de E.060.
   **Recomiendo** mantenerlo de archivo, con `traccion_admisible_e060` barrible, como está.

## 8. Lo que NO hice

- No escribí los tests en rojo antes del código; el rojo medido es de recolección.
- No medí las otras tres configuraciones de la suite ni la corrida sin `NORMAS_DIR`.
- No implementé el procedimiento general de cortante (5.7.3.4.2), ni estribos, ni fisuración
  (5.6.7), ni longitudes de desarrollo o empalme.
- No armé la zapata ni las secciones intermedias de los aleros.
- No verifiqué la zapata del cabezal ciclópeo ni sus secciones bajo sismo.
- No iteré dimensiones: si la geometría de T-7a no pasa, el armado lo dice y no la cambia.
- No toqué M11 (la maqueta de la tabla es de T-10), ni la GUI.
- No toqué el tracker, la tabla de `CLAUDE.md` ni `verificar_sesion.py`.
- No hice una segunda vuelta de mutación con otros archivos objetivo (línea base, CLI, T-7b);
  los 164 mutantes vivos están clasificados por clase, no uno a uno con un censo en un test, y
  quedan los huecos reales que la sección 3 nombra.
- No comprobé que la inclinación del empuje sea nula en el dorado del ciclópeo más que por el
  mutante que sobrevive: lo deduzco, no lo medí.
- Los sellos de los generados llevan el par de la rama, no el de `origin/main`.

## 9. Lo que el auditor debería mirar primero

1. **K0 y su envolvente** (`M9.cargas_en_reposo`, `M9.solicitaciones_de_resistencia`): K0 = 1 −
   sen φ es de terreno horizontal; se toma max(reposo, activo) por sección. Factor 1.35 de la
   fila «En reposo» frente a 1.50 del activo: si K0/K_A queda por debajo de 1.50/1.35 = 1.11 el
   activo factorado rige, y por eso es envolvente y no sustitución.
2. **Sismo a h/2** (`M9._momento_con_resultante_a_media_altura`): C11.6.5.4 dice «should be
   considered»; se aplica a la resultante total del suelo (estático más incremento).
3. **Lectura de 5.10.6** en `M9.espaciamiento_maximo_del_armado`: «3.0 times the component
   thickness but not less than 18.0 in» leído como piso del tope; en la práctica nunca rige,
   porque 5.10.3.2 ya limita a 18.0 in.
4. **Reparto por cara de la cuantía de E.060 14.3.1** (`M9.minimo_e060_por_cara`): la mitad por
   cara a partir de 200 mm; es del proyecto.
5. **Presión lineal y subpresión en la punta** (`M9.presion_de_contacto_lineal`,
   `M9.solicitaciones_de_la_zapata`): difiere de la interfaz de T-7b, a propósito.
6. **`M9.solicitaciones_por_elemento` ganó el parámetro `marco`** (LRFD por defecto): es el único
   cambio en código de T-7b.
7. **`EQ.PIR.muro`** incluye la inercia de la zapata en el ensamble de T-7b; el armado de la
   pantalla hereda esa solicitación sin descontarla (lado seguro).
8. **El recubrimiento de 91.44 mm** baja el peralte efectivo de una pantalla de 0.30 m a 0.202 m:
   pesa mucho en el acero. Con los datos declarados sería menor.
9. **Regla de propuesta de barra** (`M9.proponer_barra`): sube de diámetro solo si la barra
   mínima no alcanza con ningún espaciamiento de la serie; puede dar Ø 1/2" @ 0.10 m donde un
   proyectista pondría Ø 5/8" @ 0.15.
10. **El test de durabilidad nuevo** importa las declaraciones de prueba del `conftest` de la
    raíz (`import conftest`): si la suite cambia esa convención, es el primero en romperse.
