# INFORME T-9 · CORRECCIONES DE LA AUDITORÍA (PARTE 1)

Rama `tesis/T-9`, worktree `/home/user/wt/T-9`, base `df1b23c`. **HEAD = `9880688`**, empujado a
`origin/tesis/T-9` (commits `wip(T-9)`: `27fbd14`, `9ec08a2`, `0d5df4b`, `9880688`).
**No se fusionó ni se empujó nada a `main`.** No se tocó el `.xlsx`, la tabla de conteos de `CLAUDE.md`
ni `verificar_sesion.py`. PARTE 2 (rebase sobre `origin/main` con T-3) pendiente de «integra».

## 1. Hallazgo por hallazgo

| ID | Veredicto | Qué se hizo (anclas) |
|---|---|---|
| **H1** (ALTA) | **Cerrado** | **VB2** (`M10.verificar_aporte`, código `VB2`, fundamento `F10.APORTE_CAPACIDAD` OBLIGA, cita nueva `MC_HHD.4.1.2.1a#CONDICION`, pág. 177 / PDF 180, EXIGENCIA, verificada): Q del punto ≤ `Q_admisible`; puede fallar; llega a `verificaciones()/incumplidas()`, RESUMEN, CLI, JSON (`aporte_alivio`), memoria, comparador. Entra a la aceptación: `PERFILES[B]` = V1+V2+V4+V5+VB1+VB2. Aporte por metro: con tramo conocido y Q declarado `M10.longitud_hidraulica_por_tramo` (q' = Q/s, L = Q_adm·s/Q); sin tramo, `longitud_hidraulica` conserva q·b y publica `s_implicita_m` = A·10⁶/b con aviso si supera `long_max_cuneta`; caudal calculado: camino q·b. L declarado gana; sin `S_cuneta` y con L declarado VB2 «no se evaluó» por `avisos()` (sin exigir datos). Caso del auditor: Q_adm = 0.052215 m³/s → VB2 NO CUMPLE; B-02 en 2+650: L = 109.93 m → VB1 NO CUMPLE (en FASE A: 8 244 m y CUMPLE). Test «duplicar `area_ha` duplica L» reescrito declarándolo. |
| **INF-5.1.8** | **En parte** | `area_ha` en B tiene dos consumidores reales (contraste Q/A de T-1; reparto q·b sin tramo con aviso de s_impl), pero con tramo conocido ya no entra a L y nada comprueba que sea el área del tramo (ficha T9-07). |
| **H2** | **Cerrado** | VB1 sin evaluar ⇒ `TramoDeAlivio.falta` y `Bloqueo` `DatoFaltanteError` del punto en `ETAPA_TRAMO_ALIVIO` (`inicio_tramo_cuneta_km` sin extremo; `L_hidraulico_m` con máximo desconocido): cuenta en «Etapas bloqueadas» y `cerrado`. Vía elegida: la de «espera a un tablero» en la corrida (DatoFaltante). Pre-vuelo: regla propia (`anticipo` + `servicio.extremos_de_los_tramos`); `inicio_tramo_cuneta_km` sale de `EXTERNOS_CON_VIA_ALTERNA`. Guía lo dice. |
| **H3** | **Cerrado** | `M10.extremo_del_tramo`: avisos de hueco (obra anterior → inicio declarado; lado de progresivas mayores cuando la siguiente obra no es alivio o no hay); inicio posterior ⇒ `DatoInvalidoError` campo `inicio_tramo_cuneta_km / progresiva_km` (bloqueo, sin tumbar la corrida); textos sin «aguas arriba/abajo» (test por AST). |
| **H4 + D** | **Cerrado** | Sin «TR = 35» en M10 (test AST). `servicio._texto_periodo_retorno`: TR del punto (R, n, con el del Propietario: R 0.20 n 15 → 67.7 años); con Q declarado dice que el programa no conoce el TR del estudio. Tabla Nº 02 verificada (pág. 25/PDF 28): R 35 % / 40 %, n 15 → T = 35.32 / 29.87 años; envolvente como `Interpretacion` de `MC_HHD.4.1.2a` (`INTERPRETACION_TR_CUNETA_ENVOLVENTE`). |
| **H5 + A** | **Cerrado** | `seccion_cuneta` = {0.40, 1.20, Z2 1.0, bl 0}; ventana d 0.40–0.60, a 1.20–2.40 (techo = adopción, corregida la atribución a la Tabla 304.12), Z2 0.10–2.0 (Tabla 304.10, H:V, verificada pág. 204/PDF 205), bl 0–0.10. Tabla 304.12 verificada en imagen (pág. 173/PDF 176), cita `MC_HHD.4.1.2.1#T304_12`, `CN.CUNETA_Z1_MIN_T304_12`; `M10.aviso_de_talud_interior`: Z1 < 2 DatoInvalido, 2–3 y 3–4 avisos. Región pluvial sin trazabilidad y >3000 mm/año trapezoidal no implementada: justificación + ficha T9-01 + contrato de entradas. Sensibilidad Z2 0.467–0.871 m³/s verificada. Ejemplo `--declarar seccion_cuneta` retirado de la guía. |
| **B** | **Cerrado** | v8: «con borde libre» retirado de la línea del punto 2 con nota de corrección (literal pág. 174); campo [A] 0–0.10 con valor 0 (0.10 adopción). |
| **C** | **Cerrado** | Criterio `obras_familia_a_extremo_de_cuneta` [A] categoría «si»/«no», valor «si», perfil. Cita `DG2018.304.11#DESAGUE` (pág. 208/PDF 209, verificada) con `INTERPRETACION_OBRA_A_EXTREMO`; `MC_HHD.4.1.2.1d#ALIVIO` (PDF 182) como lo que juega en contra. Inicio declarado gana. Obras C no son extremo. |
| **H6** | **Cerrado** | Justificación de `revestimiento_cuneta`: concreto es el extremo menos conservador para L; nota «*» desde el registro. |
| **H7** | **Cerrado** | Tests: dorado Z2 ≠ 1 (`CP_T9_CUNETA['velocidad_Z2']`), criterio de VB1 con hidráulico calculado = `seccion_cuneta`, frontera s = 200 m con máximo desconocido, progresiva 0, Q declarado con cuenca no recalculado. Mutación NO re-medida con el arnés. |
| **H8** | **Cerrado** | `CP_T9_CUNETA` (a mano) en `casos_patron.py`, consumido por `test_M10_espaciamiento`; M10 sale de `SIN_CASO_PATRON`. |
| **H9** | **Cerrado** | `FAMILIAS_QUE_EXIGEN_COLUMNA['area_ha'] = (A, B)` con comentario. |
| **H10** | **Cerrado** | `INTERPRETACION_UNION_T32_T33` (cita T33), TR como Interpretación, nota de `MC_HHD.4.1.2a` factual, `F10.TRAMO` separa EXIGE 250 / RECOMIENDA 200 / adopta. |
| **H11** | **Cerrado** | Fase 1-bis usa `MH.caudal_de_aporte_cuneta` para B (una vez); Fase 10 reutiliza `informe.caudal` sin repetir pasos FH.* . |
| Dudosos 1–4 | Resueltos como manda el encargo | 1: `INTERPRETACION_CUNETA_DEL_TRAMO` (cita `#UBICACION`); 2: elección Tabla 32 vs 09 en el paso (cita `#T09`); 3: nota «*» del registro con concreto/mampostería; 4: ficha. |

Decisión de diseño propia (declarar): VB1 sólo se evalúa para alivios que **pasan la Fase 2**
(`InformePunto.fase_2_cerrada`; extremo resuelto perezosamente); los demás ya tienen su bloqueo. Y la CLI,
sin etapas bloqueadas pero con incumplidas, ya no dice «mientras un criterio siga sin valor».

## 2. Tests y par
- Nuevo `tests/test_t9_correcciones.py`: **66** (3 `pdf`). Rojo medido contra árbol exportado de `304cea6`: **62 rojos, 4 verdes** (guardias: Z2 de la ficha, dorado Z2≠1, progresiva 0, Tabla 02/304.12 en su página). +3 en `test_M10_espaciamiento` (caso patrón), +4 anclajes de fichas (T9-07..10), −1 ejemplo `seccion_cuneta` de la guía. **Total +72 collected.**
- Reescritos declarándolo: `test_t9_espaciamiento` (sección de prueba por sustitución, C=«no» en el fixture de dos alivios, H2, H1.4, H11, VB2 en la aceptación), `test_guia_perfil` (perfil/sesión/pdf salen con 1; única incumplida VB1 de B-01), `test_cli::test_perfil_cerrado…` (declara `inicio_tramo_cuneta_km`), `test_t2_hidraulica`, `test_t6_geometria`, `test_M1`, `test_t0_gobernanza`, `test_pf2_prevuelo` (partición), `test_cierre_perfil`, `test_criterios_adoptados`, `test_memoria_sustentada`, `test_guardias_de_la_suite`, `test_ext8` (techos remedidos: 70.47→74.55 KB y 20.67→21.0 pág. por punto; nuevos 75.0 / 21.4).
- **Par de la rama (HEAD 9880688, PyMuPDF sí · Tk no · `NORMAS_DIR`): 5131 passed / 19 skipped / 5150 collected.** Sin `NORMAS_DIR`: no medido.

## 3. Lo que se mueve en el fixture
- **VB1 de B-01: «no se evaluó» → NO CUMPLE** (A-02 cierra el tramo, 530 m > 200 m) en las 4 corridas de la línea base: «Verificaciones incumplidas» 0 → 1. En la guía: 530 m > 120 m (`L_hidraulico_m`), perfil y sesión ya no cierran (rc 1); la guía lo muestra y explica cómo se resuelve sin inventar progresiva.
- Línea base regenerada (README con antes/después): `tramo_alivio`, VB1, `aporte_alivio`, texto del bloqueo (sólo `S_cuneta`), criterios usados (+`long_max_cuneta`, +`obras_familia_a…`), sin valor 36→35, huellas, avisos. CSV de resumen y cajón sin cambio.
- **Diámetros movidos: ninguno** (bloques `diseno` idénticos en los 3 JSON; guía antes/después: A-01, A-02, B-01 Ø 0.90 concreto, C-01 marco 1.20×0.90).

## 4. Preguntas para el dueño
1. VB2 sin `S_cuneta` con L declarado: hoy sólo aviso (encargo). ¿Debe bloquear? Recomiendo dejar aviso.
2. Fixture/guía terminan con VB1 de B-01 NO CUMPLE hasta que el proyecto de drenaje dé el inicio del tramo o un alivio. ¿Aceptado como estado de la guía? Recomiendo sí.
3. Región pluvial en año FEN y V.D./IMDA de la vía: entradas sin trazabilidad (contrato de entradas).

## 5. No hecho
Par sin `NORMAS_DIR`; mutación con el arnés; tracker, CLAUDE.md y renumeración de la Parte (PARTE 2).
