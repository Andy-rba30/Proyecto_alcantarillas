# VERIFICACIÓN T-7b / T-7c (cierres `451a10a` y `2b13dc1`) — fórmulas contra norma y cálculo a mano

## RESUMEN

**Veredicto global: AJUSTADO.** De los 9 puntos, **6 CONFORMES** (1, 2, 4, 5, 6, 8) y **3 con DEFECTO** (3, 7, 9). No encontré ninguna fórmula mal transcrita: todos los controles del auditor y del corrector se reproducen a mano.

Defectos:
- **Punto 3 (MEDIA, lado inseguro, acotado).** `M4.hidraulica_a_presion` compara la aproximación de barril lleno sin la regla de E-A. Con control de salida y HW/D < 1.2, el evento extremo puede dar **menos carga que un caudal menor**: 0.957 m con 1.021 m³/s frente a 0.965 m con 0.987 m³/s. A-01 no lo toca, porque gobierna la entrada.
- **Punto 7 (BAJA).** La aritmética y la cita de A8 son correctas, pero A8 **nunca puede cumplir** con la zapata de la regla de T-7a. Con categoría B o C da 0.2937 m < 0.30 m, y el informe final dice que «cumpliría».
- **Punto 9 (MEDIA).** η = 1.00 implícito en el cabezal frente a η_I = 1.05 en el conducto. Está en la ficha T7C-11, pero la memoria del cabezal no lo dice.

La refutación del corrector sobre el recubrimiento de cota es correcta: 91.44 mm es la comprobación más exigente para 5.6.7 y para 15.7.

**Nada bloquea seguir con la cadena.** Antes de T-10 (memoria) conviene cerrar el punto 9, al menos con un aviso impreso, y el punto 3.

No escribí `VERIFICACION_T-7_fable.md`: mis instrucciones me impiden crear archivos de informe, así que va entero aquí. No edité ningún repositorio (`git status` de `/home/user/wt/main` limpio).

---

## Cómo se verificó

- Código de `/home/user/wt/main` en `2b13dc1`, llamado directamente con los datos de prueba de `tests/test_t7c_cabezal_armado.py::_correr_de_prueba` (A-01, Ø 0.90 m) y el muro de tanteo T-00.
- PDF leídos con PyMuPDF: HDS-5 (PDF 71, 72, 190, 191), AASHTO LRFD 9.ª ed. (PDF 18, 21, 22, 205, 379, 414, 415, 424, 1501), E.060 (PDF 138, 191, 192, 193).
- Tests rápidos de `test_t7b_cabezal_estabilidad.py` y `test_t7c_cabezal_armado.py`: 495 passed. `test_sin_literales.py`: 58 passed. No corrí la suite entera.
- Scripts en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/verif-T7/` (`corrida.py`, `p123.py`, `p3b.py`, `p3c.py`, `p456.py`, `p4b.py`, `p8.py`, `pag.py`).

Los cinco controles de mi encargo:
1. **Conflictos (§6 del plan).** Los tres que tocan el cabezal se respetan: #2 (EV de muro 1.35 / 1.00, leído de `factores_de_carga`), #3 (el recubrimiento no se corrige: cota con aviso mientras falte la categoría) y #4 (h_eq = 0.6096 m por orientación [S]).
2. **Consumidores.** Ninguno roto: el nombre viejo `_momento_con_resultante_a_media_altura` no queda en `src/`, `cli.py`, `gui/` ni `tests/`; la puerta `k_h` es solo de palabra clave.
3. **Literales.** `test_sin_literales` verde.
4. **Vacíos en silencio.** Uno: η del cabezal (punto 9).
5. **Dirección del conservadurismo.** Recomputada en cada punto; falla en el punto 3.

---

## T-7b

### 1. Cota del nivel freático — CONFORME

Símbolos: `M9.datos_del_cabezal_del_punto` (`cota_freatico = punto.cota_terreno − NF`, la misma para los dos cabezales), `M9.cargas_del_cabezal` (`h_w_natural = clamp(cota_NF − cota_desplante, 0, h)`), `M9._empotramiento_delante` (`D_w = max(terreno_delante − cota_NF, 0)`).

Caso: salida de A-01, NF 1.40, drenado, γ_sat 20 de prueba. Agua a 42.10 − 1.40 = 40.70 msnm; h_w = 40.70 − 40.50 = 0.20 m. Con h = 3.32546, K_A = 0.30440, γ = 17, δ = 22.78°, B = 2.05575:

| Magnitud | A mano | Código |
|---|---|---|
| Triángulo seco 0.3044·17·3.12546²/2 | 25.275 | — |
| Rectángulo 0.3044·17·3.12546·0.20 | 3.235 | — |
| Triángulo sumergido 0.3044·(20 − 9.81)·0.20²/2 | 0.062 | — |
| P_A | 28.572 kN/m | 28.5722 |
| z_A | 1.1100 m | 1.1100 |
| EH.h = P_A·cos δ | 26.343 | 26.3435 |
| WA.h = 9.81·0.20²/2, a 0.0667 m | 0.1962 | 0.1962 |
| Subpresión 9.81·0.20·B | 4.033 kN/m | 4.0334 |
| D_w = 41.30 − 40.70 | 0.60 m | 0.60 |
| E3-LRFD: H_u = 1.5·26.3435 + 1.75·10.4905 + 0.1962 | 58.07 | 58.07 |
| E3-LRFD: resistencia 0.8·94.214·tan 32° | 47.10 | 47.097 |

- **Sin doble cuenta.** El suelo empuja con peso sumergido solo bajo el agua; la hidrostática entra una vez; el relleno sobre el talón queda seco (h_w < e_z) y la subpresión entra una sola vez en N (N mínimo = 32.456 + 49.196 + 16.595 − 4.033 = 94.214).
- **Sísmica de salida:** `MetodoNoEvaluableError` (agua en el plano de empuje, h_w = 0.200 m), como predijo el auditor.
- Las doce filas LRFD del informe final de T-7b se reproducen idénticas sobre `2b13dc1`.

### 2. V5 `cota_de_afectacion` — CONFORME (un matiz de redacción)

- `M5._v5_cota_de_afectacion` usa `resultado.HW`, que es el del control que gobierna, y `cota_de_entrada(punto)`, que devuelve la medida si existe y si no la regla declarada.
- A-01: 42.10 + 1.0420 = 43.142 ≤ 44.00 msnm. A mano: q* = 1.811·1.167/(0.63617·0.9^0.5) = 3.502, borde de la transición; la rama sumergida da HW/D = 0.0398·3.502² + 0.67 − 0.003 = 1.155, HW ≈ 1.040 m. El código da 1.042 m.
- **Citas, literales en su página:**
  - PDF 71 (pág. 2.9): «The design headwater should not exceed the allowable headwater.» Carácter RECOMENDACIÓN: correcto («should»).
  - PDF 72 (pág. 2.10): «Another criteria might be the flood damage elevation of an upstream building or another upstream road crossing.» Carácter PERMISO: correcto («might be»).
  - La fuente no nombra el derecho de vía; el código lo dice («umbral del proyecto», [A]).
- **`embalse_a_nivel`:** el docstring, el supuesto (5) del paso y la ficha del criterio dicen ya que d incluye el tramo natural, que es cota superior de lo que añade la obra y que con anchos de 16 a 40 m solo cumple en pendiente fuerte.
- **Matiz (BAJA, texto):** la nota dice que compara «el nivel más alto del embalse (en la boca)». Eso vale solo para el embalse a nivel; con remanso M1 la superficie sube aguas arriba hasta S·x (0.12 m a 20 m con S = 0.006). El docstring sí dice que no mide la curva de remanso.

### 3. V8 con el barril a presión — DEFECTO MEDIA

**Lo que está bien.** A-01, Q_ext = 1.75 m³/s, TW 0.5, n = 0.013, ke = 0.5, L = 18.869 m, S = 0.006, Carta 1 escala 1:

| Pieza | A mano | Código |
|---|---|---|
| q* = 1.811·1.75/(0.63617·0.94868) | 5.251 | 5.251 |
| Entrada, ec. (A.3): 0.0398·5.251² + 0.67 − 0.5·0.006 = 1.7645 → HW | 1.588 m | 1.5880 |
| V = 1.75/0.63617; V²/2g | 2.751 m/s; 0.3857 m | — |
| Fricción 19.63·0.013²·18.869/0.225^(4/3) | 0.4574 | — |
| H = (1 + 0.5 + 0.4574)·0.3857 | 0.7549 m | — |
| d_c (resuelto: A³/T = 0.3124 ≈ Q²/g = 0.3122) | 0.772 m | — |
| h_o = max(0.5; (0.772 + 0.90)/2) | 0.836 m | — |
| Salida: 0.7549 + 0.836 − 0.006·18.869 | 1.478 m | 1.4779 |

Gobierna el mayor (entrada): cota 42.10 + 1.588 = 43.69 < 44.20 msnm. La ec. (A.3) «applies above about Q/AD^0.5 = 4.0 (2.21 SI)» y no tiene tope escrito (PDF 191). En Q_lleno = 1.402 m³/s el paso de lámina libre a presión es continuo en A-01: 1.2325 m (Q = 1.40) y 1.2415 m (Q = 1.41).

**El defecto.** `M4.hidraulica_a_presion` llama a `hw_gobernante(entrada, salida)` sin perfil. Sin perfil, esa función compara la aproximación de la Sec. 4.3 tal cual, sin las dos reglas de E-A que el propio M4 aplica en lámina libre: la competencia con el remanso en la banda 0.75–1.2 y el retiro de la aproximación bajo 0.75 («should not be used», HDS-5 pág. 3.24).

Caso numérico que lo rompe (mismo tubo de A-01, S = 0.003, L = 60 m, TW = 0; Q_lleno = 0.9915 m³/s):

| Q (m³/s) | Vía | HW (m) | HW/D |
|---|---|---|---|
| 0.9866 | lámina libre, salida con perfil | 0.9654 | 1.073 |
| 0.9965 | «a presión» | 0.9347 | 1.039 |
| 1.0213 | «a presión» | 0.9570 | 1.063 |

- Con Q de diseño 0.987 y Q_ext 1.021 (×1.035), **V8 juzga el evento extremo con menos carga que la de diseño**. No hay guardia `HW_ext ≥ resultado.HW`.
- Mismo patrón con S = 0.004, L = 100 m: 1.0547 → 1.0315.
- Tamaño medido: 2 a 3.5 % (2 a 3 cm). Solo ocurre con control de salida, HW/D < 1.2 y Q_ext apenas por encima de Q_lleno.
- Segunda mitad: con S = 0.0002, L = 20 m, Q = 0.257 da HW/D = 0.676 con control de salida, rotulado «barril a presión». Es una cifra bajo 0.75, fuera del dominio de la aproximación, sin aviso. Queda del lado seguro: 0.608 m frente a 0.456 m del perfil.

**Corrección (por símbolo):**
- En `M4.hidraulica_a_presion`, cuando gobierne la salida: con `salida.HW_sobre_D` < 1.2 (`cautela_aproximacion`), avisar y no entregar menos que la carga de lámina libre; bajo `H_O_HW_SOBRE_D_MIN` (0.75), `MetodoNoEvaluableError` o aviso expreso.
- En `M5.v8_evento_extremo`: guardia `HW_ext ≥ resultado.HW − tolerancia`, con aviso si se acota.
- Valor de control: en el caso de arriba, HW_ext(1.0213) ≥ 0.9654 m. A-01 no cambia (1.588 m; 43.69 msnm).

---

## T-7c

### 4. Momento y cortante de pantalla y alero — CONFORME

T-00 (φ 30°, γ 18, δ 20.1°, K_A = 0.29726, K0 = 0.5, h = 2.40, e_z = 0.40, h_eq = 0.6096), sobre el arranque (altura 2.00 m):

| | A mano | Código |
|---|---|---|
| Activo, EH: 0.29726·18·2²/2·cos 20.1° | 10.0495 kN/m, M = 6.6997 | 10.0496 / 6.6997 |
| Activo, LS: 0.29726·18·0.6096·2 | 6.5235, M = 6.5235 | 6.5235 / 6.5235 |
| Activo, V_u = 1.5·10.0495 + 1.75·6.5235 | **26.490** | 26.4906 |
| Activo, M_u | **21.466** | 21.4658 |
| Reposo, V_u = 1.35·18.0 + 1.75·10.9728 | **43.502** | 43.5024 |
| Reposo, M_u = 1.35·12.0 + 1.75·10.9728 | **35.402** | 35.4024 |

- **Cortante:** integrado también sobre el arranque (el 26.491 del auditor ya lo era), tomado en la cara y no a d_v. Es estática y coincide con la nota del paso. La resultante a h/2 se trata como diagrama uniforme y mueve también el cortante.
- **Tramo sumergido** (salida con agua a 41.50, h_w = 1.0): a mano EH 20.458 / 20.449 y WA 1.9468 / 0.4088; el código da lo mismo.
- **Inercia:** solo k_h·W_pantalla.
- **A-01 en reposo:** entrada 33.541 y salida 78.441 kN·m/m, iguales a la columna del auditor.
- **Estabilidad externa idéntica.** El diff por función entre `451a10a` y `2b13dc1` solo cambia la puerta `k_h` en `cargas_del_cabezal`; `combinaciones_de_estabilidad`, `_verificaciones_lrfd`, `_casos_sismicos`, `ensamble_estabilidad`, `cuna_de_tanteo` y `resistencia_portante_nominal` no cambian un byte.

### 5. k_h = k_h0 en el armado del muro que no cede — CONFORME

- **Solo el armado usa la puerta:** la única llamada con `k_h=` es la de `solicitaciones_de_resistencia`; `ensamble_estabilidad` y el ciclópeo llaman sin ella.
- **K_AE de la cuña con k_h0 = 0.5:** 1.14464 (entrada, P_AE = 59.726) y 1.04454 (salida, P_AE = 98.185), los oráculos del auditor. La inercia también va con k_h0 (13.509 = 0.5·27.017).
- **Cita:** PDF 1501, pág. 11-32, literal «shall be increased to 1.0kh0». El comentario dice que h/2 «may be warranted … and should be considered for design»; el código toma el mayor de «en su posición» y h/2, que es la lectura correcta de un «should».

Controles reproducidos a mano (Evento Extremo I, 100 % P_AE + 50 % P_IR, γ_EQ = 0.5):

| Término | Entrada (h 2.4776, alto 2.1076) | Salida (h 3.3255, alto 2.9555) |
|---|---|---|
| EH sobre el arranque | 11.312 kN/m → M 7.947 | 20.838 → M 20.528 |
| Incremento (trapecio, f = 0.6) | 36.553 → M 44.534 | → M 104.84 |
| LS × 0.5 | 3.549 → M 3.739 | 4.662 → M 6.889 |
| Inercia de pantalla × 0.5 | 3.322 → M 3.123 | 4.536 → M 5.821 |
| **M_u a mano** | **59.343** | **138.08** |
| M_u del código | 59.342 | 138.078 |
| V_u a mano / código | 54.735 / 54.734 | — / 90.849 |

- Con la resultante a h/2 sale 56.23 (entrada) y 131.60 (salida): no rige.
- Flexión de la entrada: A_s = 729.7 mm²/m; φM_n = 59.92 con Ø 1/2" @ 0.175 (a mano e igual en el código).
- **Observación, no defecto:** con k_h0 la punta se arma con un triángulo de contacto de 3105 kPa (entrada) y 5833 kPa (salida). La resultante está en el borde de la base; el armado no itera y lo avisa.

### 6. Fisuración AASHTO 5.6.7 — CONFORME

- **Literal (PDF 414–415):** condición «tension in the cross section exceeds 80 percent of the modulus of rupture»; s ≤ 700·γ_e/(β_s·f_ss) − 2·d_c; β_s = 1 + d_c/[0.7(h − d_c)]; γ_e 1.00 y 0.75; f_ss «not to exceed 0.60 fy».
- **Conversión:** 700 ksi·in = 700·6.894757·0.0254 = 122.589 MPa·m (`FISURACION_COEFICIENTE_AASHTO_SI`).
- **E_c:** ec. C5.4.2.4-1 (PDF 379), 2500·f'c^0.33 ksi = 9114.8·f'c^0.33 MPa; con 21 MPa, 24 893 MPa y n = 8.032.
- **f_r:** 0.24·√f'c ksi = 2.888 MPa; 0.8·f_r = 2.310 MPa.
- **Servicio I:** todas las cargas con 1.00; con `no_cedente_k0` toma el mayor de activo y reposo, y en la pantalla rige K0.

Pantalla de salida de A-01:

| Magnitud | A mano | Código |
|---|---|---|
| M_s = 32.241 + 19.951 (reposo) | 52.19 kN·m/m | 52.193 |
| f_t = 52.19/0.015 | 3.48 MPa > 2.31: aplica | aplica |
| f_ss con Ø 5/8" @ 0.10 (1990 mm²/m, d = 200.61 mm, k = 0.3274, j = 0.8909) | 146.75 MPa | 146.754 |
| d_c; β_s | 99.39 mm; 1.7078 | 1.70777 |
| s máx. Clase 1 = 122.589/(1.7078·146.75) − 0.1988 | 0.2905 m | 0.29036 |
| s máx. Clase 2 | 0.1682 m | 0.16807 |

- En ksi y pulgadas: 700/(1.7078·21.28) − 2·3.913 = 11.44 in = 0.2905 m.
- **Control del auditor** (A_s 1290, M_s 50.2): f_ss 211.71 MPa, β_s 1.69087, s ≤ 0.14687 / 0.06126 m; el código lo reproduce exacto.
- **A6 «pasa» con las dos clases** (s = 0.10 ≤ 0.168 m) porque el acero subió a Ø 5/8" @ 0.10 por el k_h0 del punto 5. Es coherente; no es un cambio de criterio.
- **Disputa del recubrimiento: tiene razón el corrector.** Con el mismo M_s y A_s:

| Recubrimiento (mm) | s máx. Clase 1 (m) | s máx. Clase 2 (m) |
|---|---|---|
| 91.44 | 0.290 | 0.168 |
| 76.2 | 0.411 | 0.266 |
| 70 | 0.463 | 0.308 |
| 50.8 | 0.634 | 0.446 |

  s máx. baja de forma monótona con d_c, de modo que la cota es la comprobación más exigente: si pasa con 91.44 mm, pasa con cualquier recubrimiento menor. Lo mismo en 15.7 (altura = e_z − rec − d_b/2). La frase del auditor describía que más recubrimiento endurece esas dos comprobaciones, que es justo por qué la cota es la hipótesis segura.
- **Observación:** el talón de salida queda al 96 % del umbral (f_t = 2.209 frente a 2.310 MPa: «no aplica»). Si aplicara, f_ss = 268 MPa superaría 0.60·f_y = 252 MPa. Es correcto por la letra, pero muy sensible.

### 7. d_v acotado y A8 — d_v CONFORME; A8 con DEFECTO BAJA

**d_v.** Literal de 5.7.2.8 (PDF 424): «need not be taken to be less than the greater of 0.9de or 0.72h».
- Pantalla de entrada: d − a/2 = 0.1935, 0.9·d = 0.1820, 0.72·h = 0.216; la letra da 0.216 y el código acota a d = 0.2022 m.
- V_c = 0.082975·2·√21·202.21 = 153.77 kN/m (código 153.776; la letra daría 164.3).
- Es interpretación declarada y avisada, del lado seguro frente a la letra.

**A8, aritmética y cita.** 0.370 − (0.09144 + 0.00635) = **0.2722 m** < 0.30: NO CUMPLE. El código da 0.27221. Cita en E.060 pág. 138 (PDF 138), literal: «La altura de las zapatas, medida sobre el refuerzo inferior no debe ser menor de 300 mm para zapatas apoyadas sobre el suelo».

**Defecto.**
- La regla de T-7a fija e_z = 0.30 + 0.070 = 0.37 m, y A8 mide hasta el eje de la barra con un recubrimiento que nunca baja de 70 mm (regla del mayor).
- Con categoría B o C (ejecutado): recubrimiento 70 mm → 0.370 − 0.070 − 0.00635 = **0.2937 m < 0.30**.
- Por tanto A8 no cumple en ningún cabezal de regla, con o sin EMS. El §7.3 (b) del informe final («con 50.8 mm de las categorías B/C cumpliría») es falso con la lectura implementada, y la nota de A8 ofrece «bajar el recubrimiento con el dato de exposición», que no alcanza.
- El paso imprime «hasta la cara de la barra» = e_z − rec, que es la cara inferior, la lectura menos exigente. La de la cara superior (0.2659 m), que es la habitual de «above bottom reinforcement», no se imprime.

**Corrección:** en `M9.peralte_minimo_zapata` (T-7a), espesor ≥ 0.30 + recubrimiento de diseño + d_b/2. Controles: 0.38 m con 70 mm y Ø 1/2" (0.38 − 0.07635 = 0.3037 ≥ 0.30); 0.40 m con la cota (0.40 − 0.09779 = 0.3022). Como mínimo, corregir la nota de A8 en `M9._fila_de_peralte_de_zapata` y el texto del informe. Mueve la geometría de T-7a: es decisión del dueño (ficha T7B-09).

### 8. Ciclópeo — CONFORME

- **Citas:** E.060 22.4.7 (pág. 191), literal: «La tracción no debe transmitirse a través de los bordes exteriores, juntas de construcción, juntas de contracción, o juntas de aislamiento de un elemento individual de concreto simple.» 22.6.3 (pág. 192): «…pero no menor de 0,10 h».
- **C2 decide siempre:** `decide = nulas or en_la_junta`. Ejecutado con las dos opciones de `criterio_traccion_cabezal_ciclopeo`: C2 queda NO_CUMPLE en ambas, mientras C1 y C3 pasan a INDICADOR con `traccion_admisible_e060`.
- **A mano** (cuerpo H 1.3, 0.30/0.50, γ_c 23.56, K0 0.5, γ 18):
  - W = 23.56·0.4·1.3 = 12.2512 kN/m; x_W = 0.2042 m.
  - M_H = 7.605·1.3/3 + 7.1323·0.65 = 7.9315 kN·m/m.
  - e de servicio = (7.9315 − 12.2512·0.04583)/12.2512 = 0.6016 m.
  - e amplificada = (1.7·7.9315 − 0.9·12.2512·0.04583)/(0.9·12.2512) = 1.1770 m.
  - Límite t/6 = 0.0833 m. El código da 0.60157 y 1.17705.

### 9. η de AASHTO 1.3.2.1 — DEFECTO MEDIA

**Lo que manda la fuente (PDF 18, 21, 22):**
- «Each component and connection shall satisfy Eq. 1.3.2.1-1 for each limit state»: Σ η_i·γ_i·Q_i ≤ φ·R_n.
- η_i = η_D·η_R·η_I ≥ 0.95 con γ máximo; η_i = 1/(η_D·η_R·η_I) ≤ 1.0 con γ mínimo.
- En resistencia: η_D 1.05 / 1.00 / 0.95; η_R ≥ 1.05 para «nonredundant members», 1.00 convencional; η_I ≥ 1.05 para puentes críticos o esenciales, 1.00 típicos. «For all other limit states» (Evento Extremo incluido), 1.00.
- La descripción del corrector en la ficha T7C-11 es fiel.

**Dictamen.**
- η = 1.00 es un valor legítimo de la fuente, así que no hay fórmula mal aplicada.
- Lo que no es defendible es que sea implícito. El conducto del mismo cruce lleva η_I = 1.05 como [A] declarado (`eta_importancia_operativa_conducto`), y el cabezal usa 1.00 sin criterio, sin paso y sin aviso: `M9_cabezal.py` no menciona η en ninguna salida. Solo lo dice la ficha.
- Es un vacío relleno con el valor menos exigente, del lado inseguro frente a la adopción del propio proyecto (5 % en Resistencia I), e incoherente dentro del mismo expediente.
- Efecto: el talón de salida pasa de 71.72 a 71.72·1.05 = 75.31 kN·m/m, que supera φM_n = 73.43 (Ø 1/2" @ 0.175 → @ 0.15). Las cifras de estabilidad con η (E3 de entrada 39.95 > 28.47, etc.) son las que midió el corrector; no las recalculé. Ningún veredicto de A-01 cambia.

**Diferirlo es defendible solo como decisión declarada en la memoria.** Corrección en dos escalones:
1. **Ya, sin tocar dorados:** aviso por `InformePunto.avisos()` en `M9.integrar_estabilidad` y `M9.ensamblar_armado` («Resistencia I del cabezal con η = 1.00; el conducto usa η_I = 1.05; sensibilidad +5 %»).
2. **Sesión dedicada, antes de T-10:** criterio [A] propio del cabezal (η_I, y η_R por 1.3.4, que es del Propietario) aplicado en `M9.combinaciones_de_estabilidad` y `M9._combinaciones_en_reposo` (1.05 en γ máximo, 1/1.05 en γ mínimo, 1.00 en Evento Extremo y Servicio). Control: talón de salida 75.31 kN·m/m, Ø 1/2" @ 0.15. Rehace 22 dorados de T-7b y T-7c.

---

## Lo que no hice

- No corrí la suite entera ni mutación.
- No leí por imagen las ecuaciones 5.6.7-1 y -2: la capa de texto del PDF 415 las trae legibles.
- No verifiqué los puntos A-02 ni C-01.
- No abrí la hoja `Conflictos` del `.xlsx`; usé la §6 de `/home/user/wt/main/docs/hoja_de_ruta_correcciones_v12.md`, que el plan da como equivalente.
- No recalculé las cifras de estabilidad con η de la ficha T7C-11; solo el talón de salida.
- La magnitud del defecto del punto 3 sale de cuatro combinaciones (S, L, TW) sobre Ø 0.90 m; no barrí otras secciones ni el marco.