## RESUMEN (menos de 300 palabras)

**Veredicto: AJUSTADO.** Ningún hallazgo BLOQUEANTE; 2 ALTA, 5 MEDIA, 5 BAJA. No escribí `AUDITORIA_T-7c.md` (mis instrucciones me impiden crear archivos de informe): va ENTERO abajo. No toqué ningún worktree (`git status` limpio en `/home/user/wt/T-7c` y `/home/user/wt/main`).

**Los tres más graves**
1. **H1 (ALTA, fórmula)** — el momento de la pantalla y del alero sale de «resultante entera × (z − e_zapata)» (`M9.solicitaciones_por_elemento`, T-7b, ya en main). El docstring lo llama «del lado seguro» y para el momento no lo es: en el muro del dorado, −8.5 %. El dorado `CP_T7C_ARMADO` copia esa fórmula.
2. **H2 (ALTA, fórmula y cita)** — con `no_cedente_k0` y k_h reducido, el Evento Extremo se arma con k_h = 0.25 y solo avisa; AASHTO 11.6.5.4 dice «shall be increased to 1.0kh0». Con k_h0 la pantalla de salida pide 1798 mm²/m, no 1055, y A1 sale CUMPLE.
3. **H3 (MEDIA)** — fisuración 5.6.7 diferida mientras A4 sale CUMPLE; en la salida de A-01 aplica, y con Clase 2 pide s ≤ 60 mm frente a 100 propuestos.

**Diámetros movidos: ninguno** (comparador de E-B: 4/2/2/2 diferencias, 0 no comparables; bloques `diseno` idénticos).

**Cuña de T-7b: APROBADA.** Coincide con Coulomb en talud infinito y con Mononobe-Okabe en relleno horizontal a 1e-14; reproduce los oráculos (16.954 / 28.614; 30.578 / 50.854; 59.726 / 98.185); guardias presentes.

**Tests:** 566 passed en los seis archivos afectados; mutación dirigida propia, 24 de 26 muertos.

**Preguntas al dueño** (el informe trae ocho): 1 → (b), pasar 22.7.4 a [N→] en sesión aparte; 2 → (a), mantener 91.44 mm diciendo dónde no es el lado seguro; 3 → peso entero; 4 → (a), con fila INDICADOR; 5 → criterio [A] sin valor e implementar 5.6.7; 6 → mismo η_I que el conducto, decidido fuera del armado; 7 → (b), k_h0; 8 → tracciones nulas de archivo, y C2 decide siempre.

---

# AUDITORÍA ADVERSARIAL DE T-7c (FASE A) — cabezal: armado y alternativa ciclópea

- Auditado: `/home/user/wt/T-7c`, rama `tesis/T-7c`, HEAD `f50edbe`, contra `451a10a`.
- Solo lectura. Temporales en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7c-aud/` (scripts `a01.py`, `a01b.py`, `kh0.py`, `grav.py`, `cuna_aud.py`, `mutar.py`, `pag.py`; copia para mutantes en `mut/`).
- PDF leídos por capa de texto con PyMuPDF: AASHTO LRFD 9.ª ed., E.060, EG-2013.
- No corrí la suite entera.

## 0. Veredicto

**AJUSTADO.** El bloque está bien construido: las fórmulas de sección reproducen mi cálculo a mano, las citas están en su página, los marcos no se cruzan y la línea base no se mueve. Lo que hay que corregir antes de integrar son dos defectos de demanda (H1, H2) y cinco huecos de verificación o de atribución (H3 a H7).

| Severidad | Hallazgos |
|---|---|
| BLOQUEANTE | ninguno |
| ALTA | H1, H2 |
| MEDIA | H3, H4, H5, H6, H7 |
| BAJA | H8, H9, H10, H11, H12 |

## 1. Caso a mano: A-01 con los datos de prueba (cabezal de entrada)

Datos leídos de la corrida real (`servicio.correr` a expediente, `a01b.py`): H = 1.88 m, B = 1.575 m, e_z = 0.37 m, pantalla 0.30 m, punta 0.520 m, talón 0.755 m, longitud 1.70 m; h = 2.4776 m en el plano del talón; γ = 17 kN/m³, δ = 22.78°, K_A = 0.32493 (cuña), K0 = 0.44081, h_eq = 0.6096 m.

**Cargas sin factorar**
- P_A = ½·0.32493·17·2.4776² = 16.954 kN/m; EH.h = 16.954·cos 22.78° = 15.632 a z = 0.826 m.
- LS.h = 0.32493·17·0.6096·2.4776 = 8.343 a z = 1.239 m.

**Pantalla, Resistencia I**
- Activo: V = 1.5·15.632 + 1.75·8.343 = 38.05; M = 23.448·0.456 + 14.600·0.869 = 23.37. Coincide con el código.
- Reposo: K0/K_A = 1.3566; EH0 = 23.00 (horizontal), LS0 = 11.318; V = 1.35·23.00 + 1.75·11.318 = 50.86; M = 31.051·0.456 + 19.807·0.869 = 31.36. Coincide.
- Qué se escala: solo EH.h y LS.h; EH.v pasa a 0; DC, EV, LS.v y WA no cambian. Factor 1.35 de la fila «En reposo». Correcto.

**Pantalla, Evento Extremo I (k_h = 0.25)**
- V = 15.632 + 12.561 + 0.5·8.343 + 0.5·6.754 = 35.74.
- M en su posición = 7.126 + 14.026 + 3.624 + 1.244 = 26.02.
- M con la resultante a h/2 = 26.02 − 21.152 + 28.193·0.869 = 29.36. Coincide.

**Flexión (5.6.3.2)**
- d = 300 − 91.44 − 6.35 = 202.2 mm.
- R = 2·31.364/(0.9·0.85·21000·0.2022²) = 0.0955; A_s = 0.0425·(1 − √0.9045)·202 200 = 420.6 mm²/m.
- M_cr = 0.67·1.6·2.888·15.0 = 46.44; 1.33·M_u = 41.71 (el menor) → 564.3 mm²/m.
- Ø 1/2" @ 0.20 = 645 mm²/m; a = 15.18 mm; φM_n = 47.45 kN·m/m; ε_t = 0.031. Coincide.

**Cortante (5.7.3.3)**
- d_v = max(194.6, 182.0, 216.0) = 216 mm; V_c = 0.08297·2·√21·216 = 164.26; φV_c = 147.84 kN/m. Coincide.

**Punta, Resistencia I máximos**
- Activo: N = 90.574, e = 0.1324 < B/6; σ = 57.507·(1 ± 0.5044) = 86.51 / 28.50 kPa; σ en la cara = 67.37; V = 39.989 − 10.897·0.520 = 34.33; M = 9.099 + 1.724 − 1.472 = 9.35. Coincide.
- Reposo: e = 0.4023 > B/6 → triángulo de 1.1556 m, σ = 139.7 kPa; V = 50.62; M = 14.57. Coincide.

**Talón con el peso entero**
- V = 1.35·24.636 + 1.75·7.827 + 1.5·6.565 + 10.897·0.755 = 65.03.
- M = 12.973 + 5.173 + 7.437 + 3.108 = 28.69. Coincide (el «exacto», 17.92).

**Conversiones (punto 10 del encargo), todas correctas**
- 0.24·√6.894757 = 0.6302.
- 0.0316·√6.894757 = 0.08297.
- 1.30 kip/(in·ft) = 0.7469 N/mm².
- 0.11 y 0.60 in²/ft = 232.8 y 1270 mm²/m.
- 16 in = 0.4064 m; 18 in = 0.4572 m; 12 in = 0.3048 m.
- β1: 0.05 por ksi sobre 4 ksi, piso 0.65.

## 2. Hallazgos refutados con evidencia

### H1 — ALTA · toca FÓRMULA: sí · el momento de la pantalla y del alero se subestima

**Dónde.** `M9.solicitaciones_por_elemento` (T-7b, ya en `origin/main`), rama `pantalla`: `M_p = Σ γ·H·max(z − e_z, 0)` con la resultante ENTERA de cada empuje. T-7c la consume en `solicitaciones_de_resistencia`, la escala a K0 con los mismos brazos (`cargas_en_reposo`: «el diagrama conserva su forma») y la repite en `_momento_con_resultante_a_media_altura` (`h/2 − e_z`).

**Qué dice y qué pasa.** El docstring afirma «Aproximación DECLARADA y del lado seguro». Para el cortante es cierto. Para el momento no: el tramo del diagrama bajo el arranque entra con brazo negativo.
- Empuje triangular: Kγh²/2·(h/3 − e_z) frente a Kγ(h − e_z)³/6. Con x = e_z/h, la fórmula da (1 − 3x) donde corresponde (1 − x)³.
- Sobrecarga: (1 − 2x) donde corresponde (1 − x)².
- Con h ≤ 3·e_z el momento del empuje sale **cero**.

**Evidencia (aritmética, y `python3` sobre los datos del volcado).**

| Caso | M_u reposo, código | M_u con el diagrama sobre el arranque | Diferencia |
|---|---|---|---|
| Muro del dorado T-00 (relleno horizontal, h = 2.40, e_z = 0.40) | 32.431 | 35.402 | −8.4 % |
| Mismo muro, activo | 19.642 | 21.466 | −8.5 % |
| A-01 entrada | 31.364 | 33.541 | −6.5 % |
| A-01 salida | 75.676 | 78.441 | −3.5 % |
| Muro bajo ilustrativo (h = 1.50, e_z = 0.37), activo | 4.13 | 5.17 | −20 % |

En T-00 el relleno es horizontal y no hay ambigüedad de modelo: el dorado `CP_T7C_ARMADO["pantalla"]` («brazos sobre la zapata: 0.40 y 0.80 m») es la fórmula del código, no un cálculo independiente.

Matiz: en A-01 el relleno sube sobre el talón. Frente a la presión sobre la cara de la pantalla con su propia altura retenida (1.73 m), el código queda por encima. La subestimación de A-01 es frente al diagrama del plano del talón truncado en el arranque, que es el que la propia rama usa en `acciones_sobre_una_seccion`.

**Efecto en A-01.** Las barras propuestas no cambian: entrada gobierna el mínimo; salida 1055 → 1096 mm²/m, sigue Ø 1/2" @ 0.10.

**Corrección.** En `solicitaciones_por_elemento`, integrar cada diagrama POR ENCIMA del arranque:
- suelo: H = K·γ·(h − e_z)²/2·cos(δ+β), M = H·(h − e_z)/3, con el tramo sumergido como en `acciones_sobre_una_seccion(z_seccion=e_z)`;
- sobrecarga: H = K·γ·h_eq·(h − e_z), M = H·(h − e_z)/2;
- inercia: solo la de la pantalla, k_h·W_pant·(z_pant − e_z);
- corregir el docstring y rehacer el dorado.

**Dorado de control (T-00, a mano).**
- Activo: V_u = 1.5·10.0496 + 1.75·6.5236 = **26.491 kN/m**; M_u = 1.5·6.6997 + 1.75·6.5236 = **21.466 kN·m/m**.
- Reposo: V_u = 1.35·18.0 + 1.75·10.9728 = **43.502**; M_u = 16.2 + 19.2024 = **35.402**.
- Con M_u = 35.402: A_s de resistencia = **476 mm²/m**; mínimo de flexión con M_cr = 46.437 (ahora el menor, porque 1.33·35.402 = 47.08) = **630.7 mm²/m**; sigue Ø 1/2" @ 0.20.

### H2 — ALTA · toca FÓRMULA y CITA: sí · k_h reducido con el régimen que no cede

**Dónde.** `M9.solicitaciones_de_resistencia`, bloque «Evento Extremo I»: usa `cargas_del_cabezal(entorno, sis)` con el k_h de la cadena. Si `cadena.k_h < cadena.k_h0`, añade un aviso y A1 sigue saliendo CUMPLE.

**Fuente.** AASHTO 11.6.5.4, pág. impresa 11-32 (PDF 1501): «For abutment walls and other walls that are considered nonyielding, the value of kh used to calculate seismic earth pressure **shall be increased to 1.0kh0** … In this case, kh should not be corrected for wall displacement». Comentario, misma página: «if the lack of ability of the wall to yield requires that the wall be designed for K0 conditions for the strength limit state, then a kh of 1.0kh0 should be used for seismic design».

**Contradicción interna.** El `por_que` de `F9.ARM_REGIMEN` dice que la fuente «manda no reducir el coeficiente sísmico» y el cálculo lo reduce. PRECISIONES decía «si no da método, avísalo»; la fuente sí da método, y gana la fuente.

**Evidencia** (`kh0.py`: misma corrida de prueba sin declarar `factor_muro_eleccion`, de modo que k_h = k_h0 = 0.50, el valor de archivo):

| Pantalla | Con k_h = 0.25 (lo que hace) | Con k_h0 = 0.50 (lo que 11.6.5.4 pide) |
|---|---|---|
| Entrada, M_u que rige | 31.36 kN·m/m (Resistencia I) | **57.27** (Evento Extremo, φ = 1.0) |
| Entrada, acero y barra | 564 mm²/m, Ø 1/2" @ 0.20 | **703 mm²/m, Ø 1/2" @ 0.175** |
| Salida, M_u que rige | 75.68 | **135.51** |
| Salida, acero y barra | 1055 mm²/m, Ø 1/2" @ 0.10 | **1798 mm²/m, Ø 5/8" @ 0.10** |
| Punta de salida | 444 mm²/m | 755 mm²/m, Ø 1/2" @ 0.15 |

Con los valores de archivo (`sin_reduccion`) no hay incoherencia. Aparece al declarar la reducción, que es lo que hacen los datos de prueba y lo que hará quien quiera que la estabilidad pase.

**Corrección** (opción (b) de la pregunta 7): con `regimen_resistencia_elementos_cabezal = no_cedente_k0`, las cargas sísmicas DEL ARMADO se calculan con k_h = `cadena.k_h0`. Hace falta un parámetro de sobrescritura de k_h en `cargas_del_cabezal`; la estabilidad externa no se toca. Si no se aplica, A1 y A2 de las combinaciones sísmicas no pueden salir CUMPLE: INDICADOR como mínimo. Dorados de control: los de la columna derecha.

### H3 — MEDIA · toca FÓRMULA: no (verificación omitida) · fisuración 5.6.7 diferida con A4 en CUMPLE

**Fuente.** AASHTO 5.6.7, pág. impresa 5-55 (PDF 414): «the provisions specified herein **shall apply** to the reinforcement of all concrete components in which tension in the cross section exceeds 80 percent of the modulus of rupture … at applicable service limit state». Ec. 5.6.7-1: s ≤ 700·γe/(βs·f_ss) − 2·d_c.

**Evidencia (a mano, pantalla de salida de A-01, Servicio I con reposo).**
- M_s = 41.43·0.7385 + 15.19·1.2927 = 50.2 kN·m/m.
- Tracción bruta = 50.2/0.015 = 3.35 MPa > 0.8·f_r = 2.31 MPa: aplica.
- Con A_s = 1290 mm²/m: f_ss ≈ 213 MPa (30.9 ksi); d_c = 91.44 + 6.35 = 97.8 mm (3.85 in); βs = 1.691.
- s ≤ **145 mm** con Clase 1; s ≤ **60 mm** con Clase 2. Propuesto: 100 mm.
- En la entrada no aplica (1.35 MPa).

**Dos consecuencias.**
- A4 (`decide=True`) dice CUMPLE con una nota de que 5.6.7 «puede pedir un espaciamiento menor». En la salida, con Clase 2, lo pide.
- El recubrimiento de 91.44 mm es el lado seguro del acero por flexión y el lado INSEGURO de la fisuración (d_c mayor, s menor). El aviso de `recubrimiento_para_armar` no lo dice.

**Corrección.** Criterio [A] sin valor para la clase de exposición (γe), e implementar 5.6.7 en `diseno_flexion_corte` con la combinación de servicio de las mismas cargas. Mientras tanto, A4 como INDICADOR cuando la tracción de servicio supere 0.8·f_r.

### H4 — MEDIA · toca CITA: sí · E.060 15.7 no se comprueba con el recubrimiento con que se arma

**Fuente.** E.060 15.7, pág. 138: «La altura de las zapatas, medida sobre el refuerzo inferior no debe ser menor de 300 mm».

**Qué pasa.** T-7a fijó la zapata en 0.37 m = 0.30 + 0.070 y dejó escrito en `M9.peralte_minimo_zapata`: «El peralte de diseño — con el recubrimiento mayor entre AASHTO y E.060 y el diámetro de la barra — es de T-7c». T-7c no lo comprueba: en el bloque nuevo de M9 no hay ninguna referencia a 15.7 ni a `peralte_minimo_zapata` (grep sobre el bloque).

**Evidencia.**
- Con la cota de 91.44 mm: 0.37 − 0.0914 = **0.279 m** < 0.30.
- Con 76.2 mm (fila «Cast against earth», categoría A, factor 1.0): **0.294 m** < 0.30.
- Solo con B o C (50.8 mm) gobernaría el 70 mm de E.060 y cumpliría.

PRECISIONES pedía que en los mínimos, incluidos los espesores, rigiera el más exigente.

**Corrección.** Fila de armado (o aviso por `avisos()`) en `ensamblar_armado`: altura sobre el refuerzo inferior = e_z − recubrimiento de la cara inferior frente a `peralte_min_zapata_armada_m`. No iterar; decirlo.

### H5 — MEDIA · toca CITA: sí · ciclópeo: «ninguna fuente exige tracciones nulas» es falso en el arranque

**Fuente.** E.060 22.4.7, pág. 191: «La tracción no debe transmitirse a través de los bordes exteriores, **juntas de construcción**, juntas de contracción, o juntas de aislamiento de un elemento individual de concreto simple». El encuentro del cuerpo con la zapata es una junta de construcción.

**Qué dice la rama.** Ficha T7C-09 y criterio `criterio_traccion_cabezal_ciclopeo`: las tracciones nulas «no las exige ninguna fuente de normas/». Con `traccion_admisible_e060`, C2 pasa a INDICADOR y decide C6, que admite tracción en esa junta.

**Otros dos puntos del mismo capítulo.**
- 22.6.3 (pág. 192) pide una excentricidad no menor de 0,10·h; C6 no la aplica.
- C1 a C3 llevan como umbral la cita `E060.22.6.3#TERCIO` con carácter EXIGENCIA. Esa frase habla de cargas amplificadas y del espesor del muro; no exige e ≤ B/6 con cargas de servicio. La `aplicacion` lo aclara, pero el carácter impreso es el de una exigencia.

**Evidencia de ruta real** (`grav.py`, A-01 con `tipo: gravedad_ciclopeo`). La «gravedad» de T-7a es un muro de 0.375 m de espesor constante.
- C2: e = 1.318 m frente a t/6 = 0.062.
- C6: aprovechamiento 3.23.
- Con las dos opciones del criterio el punto queda incumplido; la verificación detecta bien que eso no es un muro de gravedad.

**Corrección.** Citar 22.4.7; C2 decide SIEMPRE, salvo vaciado monolítico declarado; corregir la ficha y la justificación; el umbral de C1 a C3 con `Interpretacion` o con el criterio como origen.

### H6 — MEDIA · toca FÓRMULA: no · el armado calla el vano del conducto, la losa y el dentellón

**Evidencia.** `GeometriaCabezal.longitud` de A-01 = 1.70 m, con un tubo de Ø 0.90 m interior (≈ 1.1 m exterior). La «sección llena junto al conducto» de la hipótesis de T-7b son unos 0.30 m a cada lado. La tabla propone «Ø 1/2" @ 0.20 vertical» para una pantalla que en más de la mitad de su longitud es hueco.

**Qué falta.**
- `grep vano|abertura` en el bloque de T-7c no devuelve nada: los avisos de `ensamblar_armado` no nombran el vano ni el refuerzo de borde. E.060 22.6.6.5 (pág. 193) pide dos barras de 5/8" alrededor de las aberturas en muros de concreto simple; vale por analogía para el ciclópeo.
- Tampoco nombran la losa de entrega ni el dentellón, que `GeometriaCabezal.losa` sí trae y no se arman.

**Corrección.** Añadirlos al aviso de «lo que el armado NO cubre» y a la ficha T7C-04. Sin dimensionar: decirlo.

### H7 — MEDIA · toca FÓRMULA: no · textos que afirman lo que el código no hace

- `fc_cabezal_mpa`, justificación: «el armado lo dice como incumplimiento (verificación A6)». No existe A6. `ensamblar_armado` solo añade un AVISO si f'c queda bajo el mínimo por durabilidad, y nada detiene el punto.
- `AASHTO_LRFD_9.5.5.4.2#FLEXION`, nota: «sale como incumplida (verificación A5)». Es A1; A5 es el contraste de E.060.
- `concreto_ciclopeo_cabezal`, justificación: «las verificaciones R4 y R5». Son C4 y C5.
- Informe §9.7: «EQ.PIR.muro … lado seguro». Para el cortante sí; para el momento no: (W_p + W_z)·(z_muro − e_z) = W_p·(z_p − e_z) − W_z·e_z/2. Efecto pequeño, del orden de 0.3 a 0.6 kN·m/m en A-01. Se corrige con H1.

**Corrección.** Para A6, convertir el contraste de f'c en fila que decide cuando el dato existe, o corregir la justificación.

## 3. Sospechas (no refutadas)

### H8 — BAJA/MEDIA · d_v = 0.72·h mayor que el peralte efectivo

Con la cota de recubrimiento, d_e = 0.202 m y `cortante_del_concreto` toma d_v = 0.216 m > d_e. La letra de 5.7.2.8 lo ampara («need not be taken to be less than the greater of 0.9de or 0.72h»), pero el piso está pensado para d ≈ 0.8·h.

Consecuencia: el «lado seguro» del recubrimiento no llega al cortante. V_c = 164.3 kN/m frente a 138.4 con 0.9·d_e (−16 %). Con 0.9·d_e, 0.5·φ·V_c baja a 62.3 kN/m. Ningún veredicto de A-01 cambia.

Sugerencia: avisar cuando 0.72·h > d_e, o acotar d_v ≤ d_e.

### H9 — BAJA · el reposo de «mínimos» se descarta sin aviso

En los dos cabezales de A-01, la combinación «Resistencia I (mínimos), empuje en reposo» deja la resultante fuera de la base (entrada: e = 0.841 > B/2 = 0.787). `presion_de_contacto_lineal` devuelve None y la punta se arma con el activo. `sin_presion` solo se llena cuando falta el activo.

Sugerencia: avisarlo; con K0 factorado el muro vuelca.

### H10 — BAJA · K0 de terreno horizontal

La «envolvente» max(reposo, activo) no cubre el reposo con relleno en talud. Con la corrección usual K0·(1 + sen i), la entrada daría 0.523 (+19 %). La ficha lo declara como cota inferior; AASHTO no da fórmula. Sin acción, salvo imprimir la sensibilidad.

### H11 — BAJA · huecos de test

Mutación dirigida propia (`mutar.py`, 26 mutantes semánticos, tests rápidos de `tests/test_t7c_cabezal_armado.py`): 24 muertos, 2 vivos.
- **M10:** `decide=not nulas` → `decide=nulas` en C6. Ningún test tiene a C6 incumpliendo bajo `traccion_admisible_e060`. Es el hueco que el informe nombra, y sí importa: es la única fila que decide con esa opción.
- **M23:** `ancho=max(ancho, espesor)` → `ancho=espesor` en el acero de temperatura del ensamble. El piso de 0.11 in²/ft lo tapa en todos los muros probados.

Los demás huecos del informe (avisos de texto, umbral de 0.5·φ·V_c) no cambian ninguna cifra.

### H12 — BAJA · nombres y literales

- `BARRA_GRUESA_DESDE = "3/4"` vive en M9. Es el umbral de la fila de E.060 7.7.1 b) codificado como texto.
- `BETA_1_REDUCCION_POR_MPA`, `PERALTE_MAX_SIMPLIFICADO_M` y `TEMPERATURA_AS_*_MM2_M` son conversiones de constantes empíricas sin el sufijo `_SI` que pide «Unidades»; llevan la unidad en el nombre y el valor imperial en el comentario.

## 4. Comprobado y no refutado

1. **Solicitaciones.** Combinaciones y factores correctos (Resistencia I máximos y mínimos; Evento Extremo I con γ_EQ = 0.5). El escalado a K0 toca solo EH.h y LS.h, con EH.v = 0 y factor 1.35. Cortante en la cara, sin reducir a d_v: lado seguro. Momento en la cara (5.12.8.4; C5.12.8.6.1 para el talón).
2. **Flexión.** Bloque, β1, ε_t ≥ 0.005 exigido sin interpolar φ (lado seguro), φ = 0.90 y 1.0. Mínimo de 5.6.3.3 con 1.33·M_u solo de Resistencia I. Acero de temperatura contra los tres ejemplos de C5.10.6 (0.126, 0.260, 0.520 in²/ft). b = altura del muro es la lectura del ejemplo publicado («30.0 ft high × 1.0 ft thick wall»).
3. **Espaciamiento.** 5.10.3.2 y la letra de 5.10.6 («but not less than 18.0 in», pág. 5-175), que no llega a regir; E.060 14.3.3.
4. **Cortante.** Constante, d_v, tope 0.25·f'c. Condiciones de 5.7.3.4.1 leídas en la pág. 5-70: una pantalla de 0.30 m entra, y una de 0.4064 m o más se detiene con `MetodoNoEvaluableError` y su rótulo. Probado por ruta real con 0.45 m.
5. **Recubrimiento.** 91.44 mm = 3.0 in («Cast against earth», categoría A, Tabla 5.10.1-1, pág. 5-169) × 1.2 (W/CM ≥ 0.50, pág. 5-167). Es el máximo que puede dar la regla del mayor, etiquetado como cota con aviso y con los dos criterios sin valor. Defendible, con las salvedades de H3, H4 y H8.
6. **E.060.** 9.2.5, φ 0,90 y 0,85, 11.3.1.1, 10.5.4, 14.3.1 a 14.3.3, 11.10.1, 11.10.2, 22.5.3, 22.5.4, 22.10.1, 22.10.2.3 y 22.4.8: en su página. Los tres criterios de cortante alto: [N→] 0.0025, [A] «perpendicular», [N→] 0.0025; ec. (11-32) con sus dos topes.
7. **No cruce de marcos.** El mutante que pone φ = 0.90 en el contraste muere. En los mínimos rige el más exigente y se imprime cuál: en A-01, E.060 10.5.4 en la zapata y 14.3.3 en el espaciamiento.
8. **Zapata.** Presión lineal de 10.6.5 (pág. 10-86, PDF 1375) con la subpresión; talón con el peso entero. 11.6.1.2 está en la pág. 11-20 (PDF 1489) y es «shall … unless a more exact method is used».
9. **Aleros.** Arranque, con su espesor y la solicitación de la pantalla; su altura inicial (1.45 m) es menor que la de la pantalla: lado seguro. La zapata del cabezal SÍ se arma (punta y talón); la del alero y sus secciones intermedias, no.
10. **INF-4.6.** «Entero con residuales» es defendible si la nota del tracker nombra 5.6.7 y H2.
11. **Barras.** Diámetros y áreas nominales correctos (9.5/71, 12.7/129, 15.9/199, 19.1/284, 25.4/510). La propuesta cubre por construcción el adoptado y el s máximo.
12. **EG-2013, Tabla 503-07** (pág. 912, PDF 920): 35, 32, 28, 21, 17,5 y 14 MPa; Clase G con 30 %.
13. **Arquitectura.** Excepciones por `_etapa` como `Bloqueo`; avisos en `InformePunto.avisos()`; M11 sin tocar; `diseno_flexion_corte` sin `NotImplementedError`; test de ruta real que arma A-01 (`test_A01_sale_de_la_Fase_9_con_sus_dos_cabezales_armados`). MCFT como cadena de texto bajo una clave no ejecutable.
14. **Tests afectados.** 566 passed en 58 s con `NORMAS_DIR`: `test_t7c_cabezal_armado`, `test_normativa_pdf`, `test_M9_cabezal`, `test_ext7_cabezal`, `test_sin_literales`, `test_linea_base`.

## 5. PARADA (c)

`cli.py --comparar` de cada JSON de `tests/linea_base_familia_c/` contra el de `/home/user/wt/main`:

| Archivo | Diferencias | No comparables |
|---|---|---|
| `informe_expediente` | 4 (huella, dos notas del cabezal, sin valor 22 → 19) | 0 |
| `informe_familia_c` | 2 | 0 |
| `informe_perfil_ancho` | 2 | 0 |
| `informe_rama_error` | 2 | 0 |

Bloques `diseno` idénticos punto a punto: A-01 y A-02 en concreto Ø 0.90 m; C-01 en marco 1.20 × 0.90 m donde dimensiona. **Diámetros, secciones, materiales y HW movidos: ninguno.**

## 6. Cuña de tanteo de T-7b: APROBADA

`M9.cuna_de_tanteo` y `M9.empuje_de_una_cuna` de `/home/user/wt/main`; T-7c no las toca.

- **Coulomb, talud infinito** (`subida = inf`), tres casos: diferencia ≤ 1e-14 con la ec. 3.11.5.3-1.
- **Mononobe-Okabe, relleno horizontal**, cinco casos (k_h 0.2 a 0.5, uno con k_v = 0.1): diferencia ≤ 1.4e-14. También con talud infinito y sismo.
- **Oráculos de A-01:** 16.954 / 28.614; 30.578 / 50.854; 59.726 / 98.185 kN/m. Coincide con `ORQ/aud_T-7b_scripts/cuna.py`.
- **Fórmula.** P = W·(1 − k_v)·sen(ρ − φ + ψ)/[cos ψ·cos(ρ − φ − δ)] es el triángulo de fuerzas correcto. K_AE = 2P/[h²(1 − k_v)] es coherente con `empuje_activo_sismico_total`. EH.h y EH.v = P·cos δ y P·sen δ en el plano vertical del talón; β > 0 se rechaza.
- **Guardias.**
  - Sin máximo (talud más empinado que φ − ψ; k_h grande) → `MetodoNoEvaluableError`.
  - Dominio (h = 0, δ > φ, k_v = 1, NaN, subida negativa) → `DatoInvalidoError`.
  - No finito → `LimiteNumericoError`.
- **Salvedades**, heredadas y declaradas: resultante a h/3 con superficie quebrada; sobrecarga con el K_A equivalente sobre toda la h.

## 7. Riesgos de integración

- **Censos** a recalcular sobre el árbol fusionado: criterios 129 → 136, sin valor 22 → 19, marcas `literal-ok` de M9 13 → 18, citas 494, Parte LI provisional de `decisiones_diferidas.md`, fila de T-7c en `test_t0_gobernanza`.
- **`FUNCIONES_SIN_CONSUMIDOR`** cambia (ocho → seis): choca con cualquier rama que la toque.
- **`solicitaciones_por_elemento`.** Ganó el parámetro `marco`, y H1 la corrige: los 272 tests de T-7b que fijan la pantalla y los aleros habrá que reescribirlos DECLARÁNDOLO.
- **H2** necesita una puerta de k_h en `cargas_del_cabezal` (código de T-7b).
- **Par de la suite.** La rama midió una sola configuración.
- Los sellos de los generados llevan el par de la rama.

## 8. Recomendaciones para las preguntas del §7 del informe

1. **Rótulo de E.060 22.7.4 → (b), [N→], en sesión aparte.** La excepción de la §0.2 de la hoja de ruta cubre solo durabilidad (Cap. 4 y Art. 7.7); 22.7.4 es un mínimo estructural de una norma de edificaciones, y T-7a ya trató así a 15.7. El recubrimiento de 7.7.1 queda [N] por la excepción declarada; 14.3.1 pasa a [N→].
2. **Recubrimiento sin dato → (a), mantener 91.44 mm.** Con acero sin recubrir, AASHTO ya da 76.2 mm o más contra el suelo; 70 mm sería suponer categoría B o C. El aviso tiene que decir que NO es el lado seguro para 5.6.7 (H3), para E.060 15.7 (H4) ni para el cortante (H8).
3. **Talón → peso entero.** 11.6.1.2 es «shall … unless a more exact method is used»; el exacto impreso al lado, como está.
4. **Pantalla y 5.7.2.3 → (a).** La práctica de pantalla como losa y E.060 11.10.1 lo sostienen. El aviso SÍ se dispara en la salida de A-01 (82.5 > 73.9 kN/m): mejor fila INDICADOR en A2 que solo un texto.
5. **Fisuración → criterio [A] sin valor para la clase de exposición, e implementar 5.6.7.** Es «shall», decide el espaciamiento y aplica en A-01 (H3).
6. **η → fuera del armado (T-7b o T-11), con el mismo η_I del conducto (1.05, T-5) en Resistencia I.** No es inocuo: en el talón de salida el margen es 2.4 % (71.72 frente a 73.43 kN·m/m), y con 1.05 la barra pasa de @ 0.175 a @ 0.15. No lo comprobé contra AASHTO 1.3.
7. **k_h con régimen no cedente → (b), k_h = k_h0 para el armado.** Es H2.
8. **Tracciones nulas → mantenerlas de archivo.** Además, C2 decide siempre por 22.4.7 (H5).

## 9. Lo que NO hice

- No corrí la suite entera ni el arnés de mutación de EXT-11: 26 mutantes dirigidos propios.
- No leí por imagen las ecuaciones de 5.6.7 ni la Tabla 5.10.1-1 entera; me bastó la capa de texto.
- No abrí AASHTO 3.11.6.4 (la búsqueda por texto no dio con la página). Que la sobrecarga se escale con K0 es mi lectura de la práctica, no una cita verificada.
- No verifiqué una a una las 40 citas nuevas: leí unas 25 páginas y me apoyé en `test_normativa_pdf` para el resto.
- No revisé `modelos.py`, `variables_entrada.py`, `contrato_entradas.md` ni los cuatro documentos generados.
- No medí H1 sobre el punto A-02 ni sobre el marco C-01.