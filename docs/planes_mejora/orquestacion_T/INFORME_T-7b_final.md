# Informe final de T-7b (cabezal: ensamble de estabilidad en dos marcos; V5 y V8 con método declarable) — correcciones de la auditoría + integración

Worktree `/home/user/wt/T-7b`, rama `tesis/T-7b`. Base y `origin/main` previo: `250c972`.
SHA en `origin/main`: **`451a10a` (fast-forward desde `250c972`; `tesis/T-7b` empujada en el mismo commit)** (un commit `tesis(T-7b): …`, aplastado sobre `250c972`).

## 1. Hallazgos de la auditoría (H1–H10)

| Hallazgo | Estado | Qué se hizo (símbolos) |
|---|---|---|
| H1 (ALTA) datum del freático | **cerrado** | `EntornoDelCabezal.cota_freatico` (+ `origen_freatico`) = `punto.cota_terreno − NF_profundidad_m`, armado en `M9.datos_del_cabezal_del_punto`; `M9.cargas_del_cabezal` deriva `h_w_natural = clamp(cota_NF − cota_desplante, 0, h)` y `M9._empotramiento_delante` `D_w = max(terreno_delante − cota_NF, 0)`. Docstring corregido. El test que congelaba el defecto se reescribió declarándolo; dorado a mano con pie ≠ terreno: salida de A-01, agua a 40.70 msnm, 0.20 m sobre la base (40.50), subpresión 1.962·B. |
| H2 (ALTA) V5 | **cerrado** | (a) método nuevo `cota_de_afectacion` (`M5._v5_cota_de_afectacion`): cota de entrada + HW de M4 ≤ `cota_afectacion_aguas_arriba_msnm` (dato externo por punto, A y B, opcional, sin valor por defecto, admite cero y signo; `CLAVES_EXTERNAS` 24 → 25; pre-vuelo pide el dato de SU método; `variables_entrada`; contrato). Citas nuevas verificadas: HDS-5 2.2.5 «The design headwater should not exceed the allowable headwater» (pág. 2.9, PDF 71, RECOMENDACIÓN) y 2.2.5 a. «…flood damage elevation of an upstream building or another upstream road crossing» (pág. 2.10, PDF 72, PERMISO). (b) `embalse_a_nivel` se conserva y el paso, el criterio, la ficha T7B-01 y la v8 dicen que d incluye el tramo natural (cota superior de lo atribuible a la obra) y que solo cumple con pendiente fuerte; restar el tirante natural, diferido. Criterio sin valor de archivo. Test de punta a punta con cota de prueba 44.00 msnm. |
| H3 (ALTA) V8 | **cerrado** | (1) `M4.hidraulica_a_presion` (sin ecuaciones nuevas: `control_entrada` + `control_salida` a barril lleno + `hw_gobernante`; dice cuál gobierna); `EventoExtremoDelPunto.resolver` la usa cuando M3 no da tirante normal; `modelos.HidraulicaDelEventoExtremo`. (2) `M5.verificar` evalúa V8 solo si todo lo anterior cumple; mensaje «sección candidata». (3) Barrido en A-01 (test): ×1.11, ×1.20 lámina libre, cumple Ø 0.90; ×1.29, ×1.50 a presión (gobierna la entrada, q* 4.50 y 5.25), cumple Ø 0.90 (43.43, 43.69 msnm < 44.20); ×1.97 Ø 0.90 desborda (44.41 > 44.20), MD adopta Ø 1.05 (43.72). |
| H4 (MEDIA) cuña | **cerrado** | `M9.cuna_de_tanteo`, `M9.empuje_de_una_cuna` (Culmann, superficie real, estática y pseudoestática k_h/k_v); regla de archivo `regla_pendiente_relleno_trasdos` = `cuna_de_tanteo` (2H y talud entero barribles, sesgo dicho); K_A = 2P/(γh²) repartido como Coulomb; Coulomb/M-O cerrados como contraste (`K_A_contraste`, `K_AE_contraste`). Citas verificadas: 3.11.5.3 «…Culmann method» (3-121/175, PERMISO), 3.11.5.8.1 «…Coulomb trial wedge analysis should be used» (3-137/191, RECOMENDACIÓN, analogía MSE), C11.6.5.3 «…trial wedge method… may also be used…» (11-30/1499, PERMISO). Dorados `CP_T7B_CUNA`: Coulomb (13.65665 kN/m) y M-O (15.15792) a mano, cuatro cuñas escritas sobre superficie quebrada (14.60404, 14.80006, 14.20376, 6.15783; sísmica 22.62889). Oráculos del auditor reproducidos (16.95/28.61; 30.58/50.85; 59.73/98.19). MAT-D13: cuña sin máximo → `MetodoNoEvaluableError`; no finito → `LimiteNumericoError`. `factor_muro_eleccion` sin cambio. |
| H5 (MEDIA) fila φ / «no pasa» | **cerrado** | `fila_phi_estabilidad_cabezal` sigue `zapatas_seccion_10`, justificada como la más exigente y la transcrita por el Manual (la letra de 11.5.7 da 0.55/1.0). `M9._avisos_de_sensibilidad`: aviso por `avisos()` cuando una fila cambia de veredicto con la otra fila de φ o con los factores de inclinación, con las dos cifras. Ficha T7B-09 y memoria reescritas. Ancho de zapata NO iterado (diferido). |
| H6 (MEDIA) agua | **cerrado** | `sin_drenaje` de archivo; tope `h_w = max(min(z_rel, h), h_w_natural)` (relleno retenido, nunca sobre el muro); redacción unificada con `HIPOTESIS_EMPUJE_BAJO_NF` y la `Interpretacion` de 11.6.6. Con `drenado`: `M9._aviso_desembalse_rapido` (en A-01 entrada, 16.6 kN/m contra 15.6 kN/m de EH.h). Ficha T7B-03/05. |
| H7 (MEDIA) muro no cedente | **cerrado** | `regimen_cabezal` [A] (`cedente` archivo, `no_cedente` detiene con `MetodoNoEvaluableError`); citas C11.6.5.4 #CEDENTE y #K0, 3.11.5.2 #K0 (verificadas). `SolicitacionDeElemento` lleva `regimen`, `coeficiente_de_empuje`, `K_empuje`, `K0`, `K0_sobre_K_A`. En A-01 con la cuña: K0 0.441 frente a K_A 0.325 (entrada, +36 %) y 0.304 (salida, +45 %); con el K_A 2H (0.290) era el +52 % del auditor. Ficha T7B-14. |
| H8 (BAJA) | **cerrado** | nota de `AASHTO_LRFD_9.10.6.3.4#RESISTENCIA`; docstring de `servicio._fase_9`; `gamma_saturado_kn_m3` retirado del suelo de fundación (rechazado como desconocido); aviso del cabezal con una sola condición evaluada (`integrar_estabilidad`, y M11 lo pinta). El «0 → 1» del pre-vuelo corregido en T7B-12 (ya salía con 1; cambia de «espera» a «DETIENE»). |
| H9 (BAJA) aleros | **cerrado** | aviso cuando el alero largo supera la longitud entre cabezales (`M9.cabezal_del_punto`; magnitud existente, sin umbral nuevo). Test con esviaje 58°. |
| H10 (BAJA) tautología | **cerrado** | la aserción k_h·(DC+EV) = EQ se reescribió como lo que es (reconstrucción), declarándolo. |

Preguntas 4 y 6: se mantienen `terreno_delante_del_cabezal = horizontal` y V8 «sin desborde».

## 2. IDs
- `INF-4.4`, `INF-4.5`, `INF-5.1.5`: **entero**.
- `INF-4.2`: **entero, con la salvedad escrita** (la ruta real exige declarar el método de V5 y su dato, TR/Q/TW del evento extremo y el EMS).
- `INF-4.1`: **entero** (suelo de fundación y NF por punto; PGA y clase de sitio son [S] de corredor por diseño; γ_EQ [A]).
- `INF-4.3`: **en parte** (queda T7A-03, cabezal paralelo a la vía para el marco).
- `EXT-7-02`, `EXT-7-04`: cerrados (fichas). `EXT-7-01`: no (es de T-7c). Notas en `INF-0.5`, `EXT-N-04`, `SIS-F-15`; T1-03 sigue en parte (ficha).

## 3. Tests y par
Par **MEDIDO** «PyMuPDF sí · Tk no», sobre `451a10a` = `origin/main`, con `NORMAS_DIR`: **5979 passed / 23 skipped / 6002 collected**. Sin `NORMAS_DIR` (sobre el árbol de cierre, mismo contenido salvo el resello de los generados y CLAUDE.md): **5961 / 41**. Base `250c972`: 5690 / 19 / 5709 → **+293 netos** (FASE A +222; cierre +71). Derivados (no medidos): sí·sí 5992/10; no·sí 5869/133; no·no 5856/146. `-m pdf`: 112 → 124.

Tests por archivo (netos contra `250c972`): `tests/test_t7b_cabezal_estabilidad.py` 0 → 272 (FASE A 207 + 65 del cierre; 61 de ellos son la aceptación de H1–H10, todos rojos contra `fc792d9`: 51 rápidos —43 F, 8 E— y 10 lentos; el archivo entero, 157 rojos y 115 verdes contra la FASE A); `test_decisiones_diferidas` +14 (T7B-01..14); `test_ext5_forma_gui` +10; `test_familias_del_csv` +6 (4 saltos de diseño); `test_nivel_medido` +1; `test_M9_cabezal` −7; `test_criterios_adoptados` −3. Reescritos declarándolo en el cierre: `test_ayuda_entrada`, `test_ext5_forma_gui`, `test_familias_del_csv`, `test_ext6_registro_normativo` (por_que de F5.V5), `test_t0_gobernanza` (fila de T-7b; T-7a pierde las tres filas que T-7b reescribe), y dentro del archivo de T-7b los que fijaban el datum (H1), el tope del agua (H6), la regla 2H (H4) y la tautología (H10). Generados re-sellados con el par medido; tracker escrito (openpyxl) sobre el de `origin/main`.

## 4. Las doce filas LRFD de A-01 con el modelo corregido
Datos de prueba de la FASE A (φ relleno 34°, fundación φ 32° γ 18, NF 1.40 bajo el terreno del cruce, drenado, k_h 0.25 por la reducción declarada) + γ_sat 20 de prueba:
- entrada est.: E1 67.52 ≤ 81.09 kPa; E2 0.35 ≤ 0.52 m; **E3 38.05 > 29.39 kN/m**
- entrada sís.: **E1 80.26 > 50.28** (cumpliría sin inclinación: 396.76); E2 0.39 ≤ 0.58; E3 38.82 ≤ 39.68
- salida est.: E1 72.53 ≤ 75.25; E2 0.38 ≤ 0.69; **E3 58.07 > 47.10** (cumpliría con la fila de muros: 58.87)
- salida sís.: **no evaluable** (0.20 m de agua en el plano por H1)
Con k_h 0.50 de archivo la entrada sísmica da cifra (cuña): E2 0.83 > 0.58, E3 72.15 > 46.73, E1 sin presión (resultante fuera). Con NF 2.0 y k_h 0.25 las 12 se evalúan (incumplen E3 est. e/s y E1 sís. e/s); con zapata declarada de 3.00 m las 12 cumplen.

## 5. Movidos
**Diámetros, secciones, materiales y HW movidos: ninguno.** Línea base regenerada; contra `250c972` con el comparador: 27/27/31/3 diferencias (textos, huellas, recuentos, el bloqueo «K_AE (9.2)» del proyecto que desaparece), 0 no comparables; bloques de cálculo idénticos; CSV de resumen, `cli_rama_error.txt`, `memoria_punto_cajon.html` idénticos. Respecto de la FASE A solo huellas, «128 → 129 criterios» y la nota del empuje bajo el freático.

## 6. Diferidos (símbolo)
T7B-01 `M5.v5_remanso` (perfil de remanso; restar tirante natural) · T7B-02 `M5.v8_evento_extremo` (desborde admitido) · T7B-03 `M9.ensamble_estabilidad` (vano, aleros, agua del cauce, desembalse rápido) · T7B-04 `M9.resistencia_portante_nominal` · T7B-06 `M9.cargas_del_cabezal` (GLE) · T7B-07 `M9.PENDIENTES_E4_E5` · T7B-08 `M9.solicitaciones_por_elemento` · T7B-09 `M9.predimensionar_cabezal` (iteración del ancho) · T7B-14 `criterios_adoptados::regimen_cabezal` (muro no cedente).

## 7. Interfaz para T-7c
`EstabilidadDelCabezal` (por cabezal y condición): `cargas` (`CargaDeCabezal`: codigo, tipo DC/EV/EH/LS/WA/EQ, V y H en kN/m sin factorar, brazos x desde la punta y z desde la base, `sobre` pantalla/zapata), `combinaciones` (`CombinacionDeEstabilidad`: marco LRFD/ASD, nombre —Resistencia I máx/mín; Evento Extremo I, dos casos del 11.6.5.1, con y sin peso de LS—, factores por carga, N, H, M_e, M_v, B), `solicitaciones` (`SolicitacionDeElemento` solo del marco LRFD: elemento pantalla/zapata/aleros, sección —arranque de pantalla; punta y talón en la cara de la pantalla; arranque del alero—, combinación, V_u kN/m, M_u kN·m/m, nota, **regimen**, **coeficiente_de_empuje** 'K_A'/'K_AE', **K_empuje**, **K0**, **K0_sobre_K_A**), `K_A`, `K_AE`, `metodo_empuje`, `regimen`, `K0`. Régimen `cedente` de archivo: si T-7c juzga que la pantalla no cede, la resistencia va con K0 (C11.6.5.4) y sus empujes crecen en K0/K_A.

## 8. Preguntas para el dueño
1. ¿Se itera el ancho de la zapata (pregunta 2, diferida) o se mantiene «el proyectista declara»? Recomiendo esperar al EMS real: el «no pasa» es sensible a dos [A] y a datos de prueba.
2. ¿`regimen_cabezal` de la pantalla en T-7c: cedente o no cedente? Recomiendo que T-7c arme con K0 (lado seguro) para la pantalla, manteniendo la estabilidad externa con K_A.

## 9. Lo que NO hice
No implementé GLE, el perfil de remanso, restar el tirante natural, el desborde admitido, la iteración del ancho, el muro no cedente, ni las tablas de talud de 10.6.3.1.2c. Los tests del cierre no se escribieron en rojo con xfail: el rojo es contra la FASE A, donde los símbolos nuevos no existen. No medí las configuraciones con Tk ni sin PyMuPDF (derivadas). No corrí mutación nueva sobre el código del cierre.
