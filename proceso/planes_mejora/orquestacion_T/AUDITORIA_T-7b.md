## RESUMEN (menos de 300 palabras)

**Veredicto: AJUSTADO.** Hallazgos: 0 BLOQUEANTE, 3 ALTA, 4 MEDIA, 3 BAJA. La aritmética del ensamble es correcta contra AASHTO: reproduje A-01 a mano y las citas y tablas coinciden con el PDF. Los defectos están en tres supuestos de modelo y en lo que se declara cerrado.

**Los tres más graves:**
1. **H1 (ALTA, fórmula):** el freático se mide desde el pie de cada cabezal; el resto del repositorio lo mide desde `cota_terreno`. En la salida de A-01 queda 0.80 m más bajo: el cabezal sale seco cuando tiene 0.20 m de agua sobre la base. Corregido, la estática pide el peso saturado y la sísmica no es evaluable. Un test fija el defecto.
2. **H2 (ALTA, fórmula):** V5 «embalse a nivel» mide HW/S_cauce, que incluye el tramo natural del cauce. Una obra sin remanso alguno también falla. Con los anchos del DG-2018 (16–40 m) no puede cumplir; el test pasa con 400 m.
3. **H3 (ALTA):** V8 deja A-01 bloqueado en cuanto Q_ext ≥ 1.29·Q de diseño. La ruta real a la Fase 9 sólo existe con datos de prueba benignos; `INF-4.2` «Cerrado» está sobredeclarado.

**Diámetros movidos: ninguno** (comparador de E-B: 31 / 27 / 27 / 3 diferencias, todas de texto, huella y recuento).

**Las seis preguntas:**
1. Drenaje: mantener `sin_drenaje`.
2. Cabezal que no pasa: no iterar B todavía; con la fila de muros y sin factores de inclinación las doce filas LRFD cumplen.
3. Reducción de k_h: no declararla de archivo; implementar la cuña de tanteo.
4. Terreno delante horizontal: mantener.
5. Fila de φ: la letra de AASHTO 11.5.7 da 0.55 / 1.0; si se mantiene la de zapatas, justificarla como «la más exigente».
6. V8: vale como única lectura, pero necesita flujo a presión para ser utilizable.

---

# AUDITORÍA ADVERSARIAL DE T-7b — FASE A

Rama `tesis/T-7b`, HEAD `fc792d9`, base `250c972`. Sólo lectura: no edité el repositorio, y `git status` del worktree queda limpio. No escribí `AUDITORIA_T-7b.md` porque mis instrucciones me impiden crear archivos de informe; va entero aquí. Los temporales y scripts están en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7b-aud/`.

## 1. Caso a mano de A-01 (entrada, estático), independiente del código

Datos de la corrida real por `servicio.correr`: H = 1.88, B = 1.575, e_z = 0.37, pantalla 0.30, talón 0.7553, punta 0.5198, talud 2, bordillo 0.15. De ahí z_rel = 2.10, subida = 0.80 y h = 2.10 + 0.7553/2 = 2.4776 m.

Atención: el relleno entra con γ = 17 kN/m³ (`peso_especifico_relleno_kn_m3` de archivo) y γ_c = 23.56. Los 18 kN/m³ del encargo son del suelo de fundación.

- **Pendiente:** i = atan(0.8/4.2) = 10.784°. δ = 0.67·34 = 22.78°.
- **K_A** (ec. 3.11.5.3-1, θ = 90°): Γ = [1 + √(sen 56.78·sen 23.216 / (cos 22.78·cos 10.784))]² = 2.5710; K_A = cos²34 / (2.5710·cos 22.78) = 0.28994. Código: 0.28995.
- **Empuje:** P_A = ½·0.28995·17·2.4776² = 15.129; EH.h = 13.949; EH.v = 5.858.
- **Pesos:** DC = 13.288 + 13.730; EV = 17·(0.7553·1.73 + 0.1426) = 24.636; LS.h = 0.28995·17·0.6096·2.4776 = 7.445.
- **Resistencia I mínimos:** N = 0.9·27.018 + 24.636 + 1.5·5.858 = 57.739; H_u = 1.5·13.949 + 1.75·7.445 = 33.952.
- **E3-LRFD:** φ_τ·R_τ = 0.80·57.739·tan 32° = 28.863. 33.95 > 28.86: **el hallazgo 1 del implementador se reproduce exacto.**
- **E2:** e = 0.7875 − (61.385 − 33.421)/57.739 = 0.3032 ≤ B/3 = 0.525.
- **E1 estático:** σ_v = 89.514/(1.575 − 2·0.0983) = 64.94; q_n = 18·0.8·23.2·0.4524 + ½·18·1.3784·30.2·0.3043·0.6451 = 224.7; ×0.45 = 101.1.
- **Sísmico (k_h 0.25):** K_AE = 0.57055 (ec. A11.3.1-1 a mano); P_AE = 29.771; límite de excentricidad 0.3667·B; q_n = 58.28 + 11.85 = 70.13, ×0.8 = 56.10 < 79.28.

Todo coincide con el código.

## 2. Hallazgos

### H1 — ALTA · toca FÓRMULA: sí · REFUTADO con evidencia
**El nivel freático usa otro datum que el resto del repositorio, del lado inseguro.**

- `M9.datos_del_cabezal_del_punto` pasa `punto.NF_profundidad_m` tal cual. `M9.cargas_del_cabezal` lo resta de `D_f = cota_pie − cota_desplante`, y `M9._empotramiento_delante` lo mide desde `cota_pie`. Es decir, «profundidad bajo el pie de cada cabezal», como dice el docstring de `modelos.EntornoDelCabezal`.
- En `origin/main`, `M8_estructural` usa `(punto.cota_terreno - nf)` en dos sitios. El censo (`variables_entrada`, columna `NF_profundidad_m`) y el pre-vuelo dicen «bajo el terreno natural en el cruce», y `docs/contrato_entradas.md` dice «en el cruce».
- Caso A-01 salida: cota_terreno 42.10, pie 41.30, desplante 40.50, NF 1.40. Según M8 el agua está a 40.70 msnm, 0.20 m sobre la base. Según M9 está a 39.90, bajo la zapata.
- Recalculé el cabezal de salida con el datum coherente (NF 0.60 bajo su pie; script `nf.py`):
  - estático: `CriterioPendienteError('peso_especifico_saturado_relleno_kn_m3')`;
  - con γ_sat = 20 de prueba: E3-LRFD 54.21 > 46.54 y E1-LRFD 77.1 / 90.9 (antes 79.0 / 111.9);
  - sísmico: `MetodoNoEvaluableError` (agua en el plano de empuje, h_w = 0.200 m).
- Consecuencia: «A-01 sale con E1–E3 de los dos cabezales» sólo se sostiene por el datum. Ocurrirá igual en la entrada cuando `cota_fondo_entrada` venga medida por debajo del terreno.
- Un test lo fija: `test_el_entorno_de_cada_cabezal_sale_de_lo_que_las_fases_ya_resolvieron` exige `NF_profundidad_m == 1.4` en los dos entornos. Mi mutante sobre el datum sólo muere ahí.

**Corrección:** pasar al entorno la cota del agua (`punto.cota_terreno − NF`, la convención de M8) y derivar de ella `h_w_natural` y `D_w` en `cargas_del_cabezal` y `_empotramiento_delante`. Corregir el docstring de `EntornoDelCabezal`, reescribir el test declarándolo y añadir un dorado con pie ≠ terreno. Conviene hacerlo antes de integrar.

### H2 — ALTA · toca FÓRMULA: sí · REFUTADO con caso límite
**`M5.v5_remanso` («embalse_a_nivel») mide el tramo natural del cauce, no el remanso que la obra produce.**

- x = HW/S_cauce es donde el plano horizontal corta el **fondo**. Una obra que no eleva el nivel (HW = y_n) da d = (L_boca + y_n/S)·cos θ > 0 y «no cumple». Ilustración con una sección supuesta (trapecio b = 2 m, z = 1.5, n = 0.035, Q = 1.167, S = 0.006): y_n ≈ 0.43 m, d ≈ 78 m. Eso es fallar en falso.
- El embalse a nivel atribuible a la obra es (HW − y_n)/S, que exige la sección del cauce de aproximación, y el programa no la tiene.
- Con los anchos de la Tabla 304.09 que el propio código transcribe (16–40 m), V5 exige d ≤ 8–20 m. En A-01 d = 176.75 m, y sólo L_boca·cos θ ya son 9.0 m. Haría falta S ≥ 9 %.
- Corrida real con ancho 40 m (`v5.py`): V5 incumple en todos los escalones (176.7 → 123.0 m contra 20 m) y el punto no dimensiona. El test de punta a punta pasa con 400 m, un derecho de vía que no existe.
- Lo que la fuente sostiene (HDS-5 núm. 2.2.5, págs. impresas 2.9–2.10, PDF 71–72, leído) es un criterio de **cota**: «the flood damage elevation of an upstream building», y en el inciso b. un **aumento** admisible del nivel («the allowable water surface elevation increase varies from 0 to 1 ft»). No hay ninguna longitud.
- Lo que sí está bien: la proyección cos(esviaje), L_boca (semilongitud de entrada de 7.B sobre el eje), la faja simétrica como `Interpretacion`, las guardias (S ≤ 0, NaN, ancho inválido) y las excepciones dentro de `ErrorProyecto`. Sin declarar el criterio, nada cambia.

**Corrección** (decisión del dueño; el método lo pidió el encargo), una de dos:
- (a) añadir el método que la fuente sí sostiene: cota del embalse ≤ cota de afectación aguas arriba, como dato externo por punto; o
- (b) restar el tirante natural, con la sección del cauce como dato y `MetodoNoEvaluableError` sin ella.

Como mínimo, el paso y la ficha T7B-01 deben decir que d incluye el tramo natural y que con anchos normativos sólo cumple en cauces de más del 5–10 %.

### H3 — ALTA · toca FÓRMULA: no · REFUTADO con corrida
**V8 sólo es evaluable con un evento extremo de prueba; la ruta real a la Fase 9 no es robusta.**

- Barrido de `Q_evento_extremo_m3s` en A-01 (`v8.py`):

| Q_ext | relación con Q de diseño | resultado |
|---|---|---|
| 1.30 | ×1.11 | cumple |
| 1.40 | ×1.20 | cumple |
| 1.50 | ×1.29 | no dimensiona |
| 1.75 | ×1.50 | no dimensiona |
| 2.30 | ×1.97 | no dimensiona |

- Desde ×1.29 el punto no dimensiona: `Bloqueo` METODO_NO_EVALUABLE («no conduce el caudal en lámina libre»). Cualquier periodo de retorno «mayor» realista cae ahí.
- Con H2, eso deja `INF-4.2` e `INF-4.3` cerrados sólo bajo datos de prueba elegidos para pasar (faja de 400 m, Q_ext = 1.11·Q). Propongo «Cerrado en parte» o cerrado con esa salvedad escrita.
- El control de entrada sumergido no necesita tirante normal: `EventoExtremoDelPunto.resolver` (en `servicio._datos_de_expediente`) devuelve `None` antes de llamar a M4. Es prudente, pero es la causa.
- El `MetodoNoEvaluableError` de V8 salta también en candidatos que ya incumplen V1 o V5 y enmascara el motivo real (hallazgo 7 del implementador, confirmado). Además el mensaje dice «la sección adoptada (Ø 0.90 m)» de un candidato que no está adoptado.
- V8 no inventa nada: es coherente con la fila V8 de la hoja de ruta, y la cota de comparación la sostiene HDS-5 2.2.5 a.

**Corrección:** flujo a presión en `resolver` (M4 ya tiene el barril lleno) o, al menos, evaluar V8 sólo sobre el candidato que cumple lo demás (`M5.verificar` / `MD.disenar_punto`), y corregir el texto del mensaje.

### H4 — MEDIA · toca FÓRMULA: sí · REFUTADO con cálculo independiente
**La «pendiente equivalente 2H» no es el lado seguro frente a la cuña que la fuente pide.**

- AASHTO 3.11.5.3 («For conditions that deviate… Culmann method») y 3.11.5.8.1 («a GLE… or a Coulomb trial wedge analysis should be used») piden cuña. El comentario C3.11.5.8.1 permite la simplificación para muros de suelo reforzado.
- Programé una cuña de Culmann sobre el plano del talón con la superficie real (`cuna.py`). Está validada contra Coulomb con talud infinito y contra Mononobe-Okabe con relleno horizontal, a 1e-8.

| Cabezal | P_A del código | P_A de la cuña | diferencia |
|---|---|---|---|
| entrada | 15.13 kN/m | 16.95 kN/m | −10.8 % |
| salida | 26.71 kN/m | 28.61 kN/m | −6.7 % |

- En sismo con k_h 0.25 coinciden: 29.77 contra 30.58 y 51.38 contra 50.85.
- El código mezcla, además, dos alturas: mide i desde la coronación con 2·z_rel, pero aplica la presión sobre h hasta el terreno real. Con la figura al pie de la letra (h hasta la recta β′) saldría 12.41 kN/m, −27 %.
- El criterio no afirma que sea conservador y es [A] «por analogía», pero el paso no dice hacia dónde sesga.

**Corrección:** implementar la cuña en `M9.cargas_del_cabezal` como tercera opción de `regla_pendiente_relleno_trasdos`, o decir en el paso y en el criterio que subestima del orden del 7–11 % en A-01.

### H5 — MEDIA · toca CITA: sí · REFUTADO en parte
**El «cabezal de T-7a no pasa» depende de dos elecciones [A] tomadas en su extremo más exigente.**

Corridas reales, un proceso por caso (`sens1.py`):

| Declaración | E3-LRFD estático (entrada / salida) | E1-LRFD sísmico |
|---|---|---|
| de archivo | 33.95 > 28.86 / 54.07 > 48.57 (no cumple) | 79.3 > 56.1 (no cumple) |
| `fila_phi_estabilidad_cabezal` = `muros_tabla_11_5_7` | 33.95 ≤ 36.08 / 54.07 ≤ 60.71 (cumple) | sin cambio |
| `factores_inclinacion_carga_portante` = `omitir` | sin cambio | 79.3 ≤ 397 (cumple) |

- Con las dos, las doce filas LRFD cumplen con la zapata de la regla.
- AASHTO 11.5.7 (pág. impresa 11-15, PDF 1484): «the resistance factors provided in Table 11.5.7-1 **shall** be used for wall design», y remite a la Sección 10 sólo «unless specifically identified». La tabla (PDF 1486) identifica expresamente portante 0.55 y deslizamiento 1.0 para muros de gravedad y semigravedad.
- La ficha del criterio lo cuenta bien, como «tensión». El informe §8.5 no: dice que la tabla «remite a la Sección 10», y es inexacto.
- La inclinación sí es un permiso del comentario C10.6.3.1.2a, verificado en la pág. 10-71.

**Corrección:** el informe, la ficha T7B-09 y la memoria deben presentar el incumplimiento como sensible a esas dos elecciones, no como hecho del cabezal. Conviene un aviso cuando el veredicto cambia entre opciones de la ventana.

### H6 — MEDIA · toca FÓRMULA: sí (modelo) · en parte refutado, en parte sospecha
**Agua.**

- **Refutado:** con `sin_drenaje`, `h_w = h` lleva el agua hasta el terreno sobre el talón. En A-01 entrada eso es 43.78 msnm, 0.23 m por encima de la coronación del muro (43.55), lo que es físicamente imposible. Los textos dicen «superficie del relleno retenido» (`HIPOTESIS_EMPUJE_BAJO_NF`, ficha T7B-05) y el código usa h. Con γ_sat 20 da E2-LRFD 1.05 > B/2 y FS de deslizamiento 0.55. **Corrección:** acotar a `cota_relleno` o a la coronación y unificar la redacción.
- **Sospecha:** `drenado` toma sólo el freático natural. Un cabezal está en un cauce que en la avenida de diseño moja el relleno hasta HW (entrada: 1.84 m sobre la base, de h = 2.48). El desembalse rápido con cauce vacío añadiría ½·9.81·1.84² ≈ 16.6 kN/m, más que EH.h = 13.9. C11.6.6 advierte que los lloraderos no aseguran el drenaje. No está declarado ni en el paso ni en T7B-03. **Corrección:** aviso y ficha.
- **No refutado:** no hay doble cuenta (suelo sumergido + agua aparte + peso saturado en EV + subpresión; mis mutantes mueren). Con nivel igual a ambos lados, contar la hidrostática sólo detrás es conservador y está declarado. La subpresión se mantiene.

### H7 — MEDIA · toca CITA: sí · sospecha fundada
**Muro no cedente.**

- `fundamentos.F9.SISMO` dice que el cabezal «se parece» al muro que no puede ceder (11.6.5.4). Sus ejemplos incluyen «abutment walls with structural wing walls», y manda k_h = 1.0·k_h0.
- El comentario de ese mismo artículo dice que entonces las presiones pueden superar las de Mononobe-Okabe, que la resultante puede subir a h/2 y que el diseño de resistencia va con K0.
- El ensamble calcula con K_A y Mononobe-Okabe, que son de muro cedente. Para la estabilidad externa es defendible.
- `M9.solicitaciones_por_elemento` entrega a T-7c momentos con K_A. Con K0 = 1 − sen 34° = 0.441 contra 0.290 serían +52 %.

**Corrección:** declarar el régimen como [A] y marcarlo en la interfaz antes de T-7c.

### H8 — BAJA · textos que dicen lo contrario que el código
- La nota de la cita `AASHTO_LRFD_9.10.6.3.4#RESISTENCIA` dice que el suelo cohesivo «NO está implementado (… método no evaluable)»; `M9._resistencia_al_deslizamiento` sí lo calcula.
- El docstring de `servicio._fase_9` dice «la estabilidad y el armado NO están aquí».
- `gamma_saturado_kn_m3` del suelo de fundación se valida y nadie lo consume.
- `M11._bloque_cabezal` no avisa cuando sólo se evaluó una de las dos condiciones.
- El informe §4.3 dice que `--prevuelo` a expediente pasa de 0 a 1. Con `tests/ejemplo_puntos.csv` ya salía con 1 en `250c972`; lo que cambia es que el freático pasa de «espera» a «DETIENE».

### H9 — BAJA · T-7a (`M9.predimensionar_aleros`)
- La fórmula es correcta: avance (h0 − H_f)·talud en la dirección de bajada, dividido por el coseno del ángulo de cada alero con ella. Probé esviajes de 0 a 75°.
- La guardia dispara con α + θ ≥ 90° (θ = 60° con α = 30°).
- Sólo cubre la singularidad exacta. A θ = 50° da 12.1 m y cerca de 59° decenas de metros, sin aviso.

### H10 — BAJA · tests
- Los dorados (`CP_T7B_ESTABILIDAD`, `CP_T7B_MURO_2`) son aritmética escrita, no copian la fórmula.
- Mutación dirigida sobre una copia del árbol: 18 de 19 muertos. Probé factores mínimos, piso del caso 2, φ sísmico, agua dos veces, subpresión, cargas factoradas en la inclinación, h, D_w, brazo, V5 y V8. El único vivo es el datum de H1, que sólo muere en el test lento que lo congela.
- El contraste con «VARIOS» está rotulado honestamente, pero es en parte circular: φ, γ, H y k_h se reconstruyen del propio ejemplo y la última aserción es tautológica. No ajusta el código al ejemplo.

## 3. Comprobado y no refutado

- **Plano de empuje y δ:** plano vertical del talón y δ = 0.67·φ suelo–suelo (C3.11.5.3, PDF 175–176); Figura C3.11.5.3-1b, leída por imagen, da φ/3 a 2φ/3.
- **Figuras C11.5.6-1/-2/-4** (por imagen): 1.25 / 0.90 DC; suelo sobre el talón 1.35 / 1.00 (rotulado «EH» por errata en -1 y -2; «1.00 EV» en la -4); 1.50 EH en las **dos** componentes, también cuando la vertical estabiliza. La lectura del implementador es la de la figura.
- **Combinaciones:** LS 1.75 sin su peso en deslizamiento y excentricidad (Figura C11.5.6-3); WA 1.00; Evento Extremo I todo 1.00 con LS = γ_EQ. El conflicto #2 (EV 1.35 / 1.00 de muro) está respetado.
- **Sobrecarga viva:** Tablas 3.11.6.4-1/-2 idénticas al PDF 205; altura sobre la superficie de empuje; orientación como [S] (conflicto #4 respetado); «siempre aplica» es conservador.
- **Sismo:** h de 11.6.5.2.2; condición φ ≥ i + arctan(k_h/(1 − k_v)); P_IR = k_h(W_w + W_s); los dos casos con el piso estático; el 0.6 aplicado al incremento deja la resultante total en 0.46·h, dentro del 0.4–0.5 h del comentario; φ de 11.5.8 (0.8 / 1.0); límite de excentricidad con γ_EQ; γ_EQ = 0.50 «is reasonable» (C3.4.1, PDF 64).
- **Portante:** Tabla 10.6.3.1.2a-1 comparada celda a celda por programa (46 filas, 0 diferencias); C_w; i_q e i_γ con cargas sin factorar y n = 2. El 10.6.3.1.2c trae coeficientes de reducción RC_BC, no N_cq / N_γq: confirmado en PDF 1363.
- **Marco ASD:** E.050 Art. 17.1, 21, 39.13.6 y 39.13.8 (con su errata «39.14.6») leídos; factores 1; no hay cruce; es [N→].
- **Citas:** los 38 tests `-m pdf` de `test_normativa_pdf` y de T-7b pasan.
- **Tests afectados** (T-7b, M9, EXT-7, sin_literales, memoria_sustentada, linea_base, T-7a): verdes.
- **M11:** sólo formato. Excepciones dentro de `ErrorProyecto` y como `Bloqueo`.
- **Ruta real:** A-01 llega a la Fase 9 por `servicio.correr` con los datos de prueba, que están rotulados.
- **Lo que cambia sin declarar nada:** retirar la etapa «K_AE (9.2)» del proyecto es legítimo (K_AE es por cabezal), y `phi_relleno_trasdos` sigue en el pre-vuelo.
- **Hallazgos 2 y 3 del implementador:** con k_h 0.50 Mononobe-Okabe no es evaluable y con `sin_drenaje` nada se evalúa; los dos reproducidos.
- **PARADA (c):** ningún diámetro, sección, material ni HW se mueve; los dos CSV de resumen, `cli_rama_error.txt` y `memoria_punto_cajon.html` son idénticos byte a byte.

## 4. Riesgos de integración

- H1 cambia el comportamiento del cabezal de salida: su test de punta a punta habrá que reescribirlo.
- No cerrar `INF-4.2` e `INF-4.3` sin la salvedad de H2 y H3.
- T-7c heredará K_A por la interfaz (H7).
- La línea base sólo cambia en textos, huella y recuentos (128 criterios, 22 sin valor): recalcular los censos al rebasar.

## 5. Recomendación para las seis preguntas al dueño

1. **Drenaje de archivo → mantener `sin_drenaje`.** AASHTO 11.6.6: «shall be drained or, if drainage cannot be provided… full hydrostatic pressure». Sin detalle declarado no hay drenaje que suponer, y `drenado` compromete planos. Corregir el tope del agua y avisar del nivel de avenida (H6).
2. **Cabezal que no pasa → no iterar B todavía.** El incumplimiento se invierte con la tabla de muros y sin factores de inclinación (H5), los datos son de prueba, y H1 y H4 mueven los números. Dejarlo como incumplimiento que se cierra con `cabezal_declarado`.
3. **Reducción de k_h → no declararla de archivo.** El 11.6.5.2.2 exige muro libre de moverse 1–2 in y aceptación del Propietario, y el 11.6.5.4 pone al muro con aleros estructurales como no cedente. Implementar la cuña de tanteo que C11.6.5.3 admite: con k_h = 0.50 da una cifra finita (59.7 y 98.2 kN/m en A-01), porque el talud se quiebra en la plataforma.
4. **Terreno delante horizontal → mantener.** El 10.6.3.1.2c es para zapatas «on or adjacent to slopes» y aquí el talud sube detrás. Se cuenta sólo el empotramiento bajo la hoya.
5. **Fila de φ.** Por la letra de AASHTO 9.ª ed. corresponde la Tabla 11.5.7-1 (0.55 / 1.0). Mantener `zapatas_seccion_10` es defendible sólo como «la más exigente, y la que el Manual de Puentes 2016 transcribe»; hay que corregir esa justificación e imprimir la sensibilidad.
6. **V8 → sí como única lectura por ahora.** No inventa nada y HDS-5 2.2.5 a. sostiene la cota. Pero sin flujo a presión deja el punto bloqueado con cualquier Q_ext ≥ 1.3·Q (H3).