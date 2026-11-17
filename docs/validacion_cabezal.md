# Validación externa de M9: el cabezal contra ejemplos resueltos (VE-3.3)

> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe `python -m tests.apoyo.validacion_cabezal --escribir` y `tests/test_validacion_cabezal.py` lo regenera y lo compara. Las cifras de las fuentes están transcritas con su página o su celda en `tests/apoyo/validacion_cabezal.py`; la cuenta es la de las funciones de M9. Las fuentes no están en el repositorio.

## 1. Fuentes, tolerancia y regla de juicio

- **Caltrans BDP 11.2.2.** Caltrans, *Bridge Design Practice*, Cap. 11.2, oct. 2022, §11.2.2 «Reinforced Concrete Retaining Wall Design Example» (AASHTO-CA BDS-8). Citas: «p. 11.2-xx» es la pagina impresa; la del PDF del capitulo es la misma cifra xx.
- **CDOT Ex. 11.** Colorado DOT, *Bridge Design Manual*, Example 11 «Cast-in-Place Concrete Cantilever Retaining Wall», hoja de calculo feb. 2023, hoja «Ex.11». Citas: celda de esa hoja. La hoja calcula «as displayed» (celda AF1).

- **Tolerancia: 1%**, la de un ejemplo impreso (`TOLERANCIA_EJEMPLO_IMPRESO` de `tests/apoyo/validacion_externa.py`): las fuentes imprimen tres o cuatro cifras y redondean los intermedios.
- Por cada cifra: **publicado** (la fuente), **recalculado** (la fórmula de la propia fuente, en sus unidades, sin M9) y **motor** (M9 en SI, devuelto a las unidades de la fuente). El motor se juzga contra lo recalculado; si la fuente no cuadra con su propia cuenta es una **errata de la fuente**, declarada con su causa.
- Juicios: «coincide», «errata de la fuente; el motor coincide con lo recalculado», «difiere por método (declarado)» y «DEFECTO DEL MOTOR». La suite exige cero defectos.

## 2. Caltrans BDP 11.2.2

| Paso | Unidad | Publicado | Recalculado | Motor | Motor − rec. | Juicio | Cita | Función de M9 |
|---|---|---|---|---|---|---|---|---|
| e = B/2 − ΣM_O/V, sismo (Evento Extremo) | ft | 5.98 | 5.987 | 5.987 | 0.00% | coincide | p. 11.2-21 | `M9.presion_contacto_base (rama de suelo)` |
| B' = B − 2e, sismo (Evento Extremo) | ft | 7.03 | 7.025 | 7.025 | 0.00% | coincide | p. 11.2-22 | `M9.presion_contacto_base (rama de suelo)` |
| q = V/B', sismo (Evento Extremo) | ksf | 7.87 | 7.88 | 7.88 | 0.00% | errata de la fuente; el motor coincide con lo recalculado | p. 11.2-22 | `M9.presion_contacto_base (rama de suelo)` |
| e = B/2 − ΣM_O/V, servicio | ft | 0.7 | 0.708 | 0.708 | 0.00% | errata de la fuente; el motor coincide con lo recalculado | p. 11.2-23 | `M9.presion_contacto_base (rama de suelo)` |
| B' = B − 2e, servicio | ft | 17.59 | 17.58 | 17.58 | 0.00% | coincide | p. 11.2-23 | `M9.presion_contacto_base (rama de suelo)` |
| q = V/B', servicio | ksf | 3.01 | 3.013 | 3.013 | 0.00% | coincide | p. 11.2-24 | `M9.presion_contacto_base (rama de suelo)` |
| e = B/2 − ΣM_O/V, Resistencia Ia | ft | 1 | 1.004 | 1.004 | 0.00% | coincide | p. 11.2-40 | `M9.presion_contacto_base (rama de suelo)` |
| B' = B − 2e, Resistencia Ia | ft | 17 | 16.99 | 16.99 | 0.00% | coincide | p. 11.2-25 | `M9.presion_contacto_base (rama de suelo)` |
| q = V/B', Resistencia Ia | ksf | 4.16 | 4.16 | 4.16 | 0.00% | coincide | p. 11.2-25 | `M9.presion_contacto_base (rama de suelo)` |
| e = B/2 − ΣM_O/V, Resistencia Ib | ft | 2.06 | 2.058 | 2.058 | 0.00% | coincide | p. 11.2-27 | `M9.presion_contacto_base (rama de suelo)` |
| e admisible bajo sismo con γEQ = 0 (11.6.5.1) | ft | 6.33 | 6.333 | 6.333 | 0.00% | coincide | p. 11.2-22 | `M9.excentricidad_admisible_sismica` |
| q en la punta, trapecio (Resistencia Ia) | ksf | 4.895 | 4.9 | 4.9 | 0.00% | coincide | p. 11.2-41 | `M9.presion_de_contacto_lineal (AASHTO 10.6.5)` |
| q en el talon, trapecio (Resistencia Ia) | ksf | 2.545 | 2.54 | 2.54 | 0.00% | coincide | p. 11.2-41 | `M9.presion_de_contacto_lineal (AASHTO 10.6.5)` |
| q máx., triángulo desde la punta (sismo) | ksf | 10.48 | 10.51 | 10.51 | 0.00% | coincide | p. 11.2-43 | `M9.presion_de_contacto_lineal (AASHTO 10.6.5)` |
| a del alzado | in | 2.2 | 2.206 | 2.206 | 0.00% | coincide | p. 11.2-35 | `M9.resistencia_a_flexion` |
| c del alzado | in | 2.59 | 2.595 | 2.595 | 0.00% | coincide | p. 11.2-35 | `M9.resistencia_a_flexion` |
| Mn del alzado | kip-ft/ft | 186.3 | 186.2 | 186.2 | 0.00% | coincide | p. 11.2-35 | `M9.resistencia_a_flexion` |
| ε_t del acero | — | 0.027 | 0.02698 | 0.02698 | 0.00% | coincide | p. 11.2-35 | `M9.resistencia_a_flexion` |
| As para φMn = 167.7 kip-ft (inversa) | in²/ft | 1.5 | 1.501 | 1.501 | 0.00% | coincide | p. 11.2-35 | `M9.acero_por_flexion` |
| Mcr del alzado (γ3 = 0.75, A706) | kip-ft/ft | 78 | 77.98 | 77.98 | 0.00% | coincide | p. 11.2-30 | `M9.momento_de_agrietamiento` |
| Mcr de la punta (γ3 = 0.75, A706) | kip-ft/ft | 86.4 | 86.4 | 86.4 | 0.00% | coincide | p. 11.2-42 | `M9.momento_de_agrietamiento` |
| n = Es/Ec | — | 8 | 8.044 | 7.341 | -8.74% | difiere por método (declarado) | p. 11.2-36 | `M9.fisuracion_aashto` |
| β_s | — | 1.14 | 1.141 | 1.141 | 0.00% | coincide | p. 11.2-36 | `M9.fisuracion_aashto` |
| f_ss (seccion fisurada) | ksi | 27 | 26.97 | 26.89 | -0.32% | coincide | p. 11.2-37 | `M9.fisuracion_aashto` |
| s_max (γe = 1.0, clase 1) | in | 17.6 | 17.61 | 17.68 | +0.41% | coincide | p. 11.2-37 | `M9.fisuracion_aashto` |
| dv del talon (5.7.2.8) | in | 24.2 | 24.09 | 24.09 | 0.00% | coincide | p. 11.2-56 («calculation is not shown here») | `M9.cortante_del_concreto` |
| Vc del talon con β = 1.57 (β del Apendice B5, dato de la fuente) | kip/ft | 28.8 | 28.68 | 28.68 | 0.00% | coincide | p. 11.2-56 | `M9.cortante_del_concreto` |
| ¿Procedimiento simplificado permitido en el talon (vuelo 11.125 ft frente a 3·dv)? | sí/no | no | no | no | — | coincide | p. 11.2-56 (usa el procedimiento general, Apendice B5) | `M9.simplificado_permitido` |

Erratas de la fuente y diferencias de método:

- *q = V/B', sismo (Evento Extremo)* — **errata:** la fuente divide 55.35 (no 55.36) por 7.03; la diferencia es de la cuarta cifra. En la misma pagina escribe q_n = 32.22 ksf y luego 0.8·(33.22) = 26.58: una de las dos cifras de q_n esta mal (no la usa el motor).
- *e = B/2 − ΣM_O/V, servicio* — **errata:** la fuente escribe e = 19/2 − 8.79 = 0.70, y esa resta da 0.71; con x = 465.8/52.98 = 8.792 e = 0.708 (y B' = 17.584, que la fuente imprime 17.59).
- *n = Es/Ec* — **método:** Ec: Caltrans usa 57 000·√f'c (psi), la expresion de ACI 318 (3605 ksi, n = 8.04, redondeado a 8); M9 la del comentario C5.4.2.4-1 de AASHTO (3950 ksi, n = 7.34). Ver O-1.
- *f_ss (seccion fisurada)* — **método:** n distinto (O-1); f_ss casi no depende de n

## 3. CDOT Ex. 11

| Paso | Unidad | Publicado | Recalculado | Motor | Motor − rec. | Juicio | Cita | Función de M9 |
|---|---|---|---|---|---|---|---|---|
| Ka de Coulomb (φ = 34°, δ = 22.67°, θ = 89° de la hoja, que en M9 es β = 90° − θ = 1°; relleno horizontal) | — | 0.261 | 0.2614 | 0.2614 | 0.00% | coincide | AQ19 (= Q23) | `M9.k_a_coulomb` |
| EHH de estabilidad, ½·EFW·(H+TF)²·cos δ | kip/ft | 4.39 | 4.386 | 4.386 | 0.00% | coincide | T138 | `M9.empuje_activo_estatico (la componente horizontal, cos δ, la toma aqui el arnes)` |
| EHH del alzado, ½·EFW·H²·cos δ | kip/ft | 3.74 | 3.737 | 3.737 | 0.00% | coincide | K331 | `M9.empuje_activo_estatico (la componente horizontal, cos δ, la toma aqui el arnes)` |
| EHV, ½·EFW·(H+TF)²·sen δ | kip/ft | 1.83 | 1.832 | 1.832 | 0.00% | coincide | T133 | `M9.empuje_activo_estatico (sen δ en el arnes)` |
| LSH, EFW·h_eq·(H+TF) con h_eq de la Tabla 3.11.6.4-2 (paralelo, ≥ 1.0 ft) | kip/ft | 1.17 | 1.17 | 1.17 | 0.00% | coincide | T139 | `M9.empuje_sobrecarga_trasdos (h_eq de M9.h_eq_sobrecarga_trasdos)` |
| LSH, EFW·h_eq·H con h_eq de la Tabla 3.11.6.4-2 (paralelo, ≥ 1.0 ft) | kip/ft | 1.08 | 1.08 | 1.08 | 0.00% | coincide | K332 | `M9.empuje_sobrecarga_trasdos (h_eq de M9.h_eq_sobrecarga_trasdos)` |
| e, Strength Ia | ft | 1.14 | 1.142 | 1.142 | 0.00% | coincide | N204 (ΣV, ΣMV, ΣMH de H188-Z193) | `M9.presion_contacto_base (rama de suelo)` |
| σV = ΣV/(B − 2e), Strength Ia | ksf | 2.57 | 2.574 | 2.574 | 0.00% | coincide | T298 | `M9.presion_contacto_base (rama de suelo)` |
| e, Extreme IIa | ft | 1.96 | 1.956 | 1.956 | 0.00% | coincide | N207 (ΣV, ΣMV, ΣMH de H188-Z193) | `M9.presion_contacto_base (rama de suelo)` |
| σV = ΣV/(B − 2e), Extreme IIa | ksf | 2.82 | 2.812 | 2.812 | 0.00% | coincide | T299 | `M9.presion_contacto_base (rama de suelo)` |
| e, Strength Ib | ft | 0.43 | 0.4305 | 0.4305 | 0.00% | coincide | W220 (ΣV, ΣMV, ΣMH de H188-Z193) | `M9.presion_contacto_base (rama de suelo)` |
| σV = ΣV/(B − 2e), Strength Ib | ksf | 3.04 | 3.04 | 3.04 | 0.00% | coincide | W221 | `M9.presion_contacto_base (rama de suelo)` |
| e, Strength IV | ft | 0.08 | 0.0798 | 0.0798 | 0.00% | coincide | W225 (ΣV, ΣMV, ΣMH de H188-Z193) | `M9.presion_contacto_base (rama de suelo)` |
| σV = ΣV/(B − 2e), Strength IV | ksf | 2.8 | 2.802 | 2.802 | 0.00% | coincide | W226 | `M9.presion_contacto_base (rama de suelo)` |
| e, Extreme IIb | ft | 1.21 | 1.205 | 1.205 | 0.00% | coincide | W230 (ΣV, ΣMV, ΣMH de H188-Z193) | `M9.presion_contacto_base (rama de suelo)` |
| σV = ΣV/(B − 2e), Extreme IIb | ksf | 3.08 | 3.073 | 3.073 | 0.00% | coincide | W231 | `M9.presion_contacto_base (rama de suelo)` |
| e, Service I | ft | 0.28 | 0.2811 | 0.2811 | 0.00% | coincide | R495 (ΣV, ΣMV, ΣMH de H188-Z193) | `M9.presion_contacto_base (rama de suelo)` |
| σV = ΣV/(B − 2e), Service I | ksf | 2.17 | 2.175 | 2.175 | 0.00% | coincide | R496 | `M9.presion_contacto_base (rama de suelo)` |
| β1 (5.6.2.2, f'c = 4.5 ksi) | — | 0.825 | 0.825 | 0.825 | 0.00% | coincide | T322 | `M9.beta_1_aashto` |
| c, eje neutro | in | 0.982 | 0.9824 | 0.9824 | 0.00% | coincide | AA360 | `M9.resistencia_a_flexion` |
| a = β1·c | in | 0.81 | 0.8105 | 0.8105 | 0.00% | coincide | AA361 | `M9.resistencia_a_flexion` |
| Mn | kip-ft/ft | 56.68 | 56.68 | 56.68 | 0.00% | coincide | AA362 | `M9.resistencia_a_flexion` |
| As para φMn = 51.01 kip-ft (inversa) | in²/ft | 0.62 | 0.6199 | 0.6199 | 0.00% | coincide | AA359 y AA363 | `M9.acero_por_flexion` |
| Mcr (γ3 = 0.67, A615 G60) | kip-ft/ft | 40.11 | 40.11 | 40.11 | 0.00% | coincide | Q386 | `M9.momento_de_agrietamiento` |
| n = Es/Ec | — | 6.54 | 6.538 | 7.062 | +8.00% | difiere por método (declarado) | T321 (Ec en T320) | `M9.fisuracion_aashto` |
| k de la seccion fisurada | — | 0.179 | 0.1729 | 0.179 | +3.54% | difiere por método (declarado) | Q397 | `M9.fisuracion_aashto` |
| f_ss = Ms/(As·j·d) | ksi | 29.52 | 29.45 | 29.51 | +0.22% | coincide | AA400 | `M9.fisuracion_aashto` |
| β_s | — | 1.18 | 1.177 | 1.177 | 0.00% | coincide | AA401 | `M9.fisuracion_aashto` |
| s_max (γe = 0.75, clase 2) | in | 10.45 | 10.52 | 10.49 | -0.31% | coincide | AA402 | `M9.fisuracion_aashto` |
| dv (5.7.2.8) | in | 18.2 | 18.28 | 18.28 | 0.00% | errata de la fuente; el motor coincide con lo recalculado | S411 | `M9.cortante_del_concreto` |
| Vc con β = 1.81 (β del procedimiento general, dato de la fuente) | kip/ft | 26.5 | 26.62 | 26.62 | 0.00% | errata de la fuente; el motor coincide con lo recalculado | AA444 (β en S440) | `M9.cortante_del_concreto` |
| ¿Procedimiento simplificado de 5.7.3.4.1 permitido en el alzado sin estribos (h = 21 in)? | sí/no | no | no | no | — | coincide | A413 («does not qualify for simplified procedure») | `M9.simplificado_permitido` |
| As de temperatura por cara con b = 12 in, h = 21 in | in²/ft | 0.083 | 0.11 | 0.11 | 0.00% | errata de la fuente; el motor coincide con lo recalculado | Y455 | `M9.acero_de_temperatura_aashto` |

Erratas de la fuente y diferencias de método:

- *n = Es/Ec* — **método:** Ec: CDOT usa la ec. 5.4.2.4-1, 120 000·K1·wc²·f'c^0.33 con wc = 0.150 kcf (4435 ksi); M9 usa la del comentario C5.4.2.4-1, 2500·f'c^0.33, que es la misma con wc = 0.145 kcf (4107 ksi). Ver la observacion O-1.
- *k de la seccion fisurada* — **errata:** la hoja calcula k con ρ = 0.003, el valor MOSTRADO de 0.620/(12·18.69) = 0.002764 («as displayed», celda AF1): con ρ exacto y su n = 6.54, k = 0.1729.
- *k de la seccion fisurada* — **método:** el k depende de n (O-1): con el n de M9 sale 0.1790
- *f_ss = Ms/(As·j·d)* — **método:** n distinto (O-1); f_ss casi no depende de n
- *dv (5.7.2.8)* — **errata:** la celda escribe dv = max(de − c/2, …) con c = 0.982 in (AA360), y AASHTO 5.7.2.8 resta a/2 (a = 0.81 in): 18.199 frente a 18.285 in; dentro del 1 %.
- *Vc con β = 1.81 (β del procedimiento general, dato de la fuente)* — **errata:** el texto de la celda escribe «0.0316 (2)(1) …» y el valor usa β = 1.81 de S440: con β = 2 saldria 29.3 kip; el numero publicado es el de β = 1.81 con el dv de S411.
- *As de temperatura por cara con b = 12 in, h = 21 in* — **errata:** la hoja aplica la ec. 5.10.6-1 (0.0827 in²/ft) sin el piso de la ec. 5.10.6-2 (0.11 ≤ As ≤ 0.60; cita AASHTO_LRFD_9.5.10.6#TEMPERATURA); el #4 @ 12 provisto (0.20 in²/ft) cumple igual. Ademas toma b = 12 in, la franja de calculo, donde AASHTO dice «least width of component section»: M9 pasa el ancho real del elemento (O-2).

## 4. La aritmética de la propia fuente (Caltrans, tablas de momentos)

Sin motor: cada momento impreso contra su fuerza por su brazo, con el redondeo propagado de las tres cifras impresas como margen (|F|·δb + |b|·δF + δM, δ = medio último dígito), y cada suma contra la suma de las filas impresas.

| Tabla | Fila | Impreso | Recalculado | Margen | ¿Cuadra? | Nota |
|---|---|---|---|---|---|---|
| 11.2.2-2 (sismo, p. 11.2-21) | parte 1: F·brazo | 19.28 | 19.283 | 0.051 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte 2: F·brazo | 17.15 | 17.162 | 0.052 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte 3: F·brazo | 67.69 | 67.640 | 0.088 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte 4: F·brazo | 3.15 | 3.080 | 0.076 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte 5: F·brazo | 13.50 | 13.504 | 0.051 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte 6: F·brazo | 394.66 | 394.733 | 0.219 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte 7: F·brazo | 3.63 | 3.630 | 0.025 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte 8: F·brazo | 66.06 | 65.993 | 0.101 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte PAE·sen δA: F·brazo | 101.46 | 101.460 | 0.367 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte PAE·cos δA: F·brazo | -315.77 | -315.767 | 0.211 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte kh·1: F·brazo | -12.66 | -12.740 | 0.121 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte kh·2: F·brazo | -7.06 | -7.017 | 0.059 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte kh·3: F·brazo | -2.49 | -2.500 | 0.021 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte kh·5: F·brazo | -8.75 | -8.757 | 0.093 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte kh·6: F·brazo | -111.02 | -110.970 | 0.484 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte kh·7: F·brazo | -1.29 | -1.295 | 0.041 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | parte kh·8: F·brazo | -33.10 | -33.100 | 0.144 | sí | — |
| 11.2.2-2 (sismo, p. 11.2-21) | ΣM_O | 194.46 | 194.460 | 0.005 | sí | suma de los momentos IMPRESOS de la tabla |
| 11.2.2-3 (servicio, p. 11.2-23) | parte 1: F·brazo | 19.28 | 19.283 | 0.051 | sí | — |
| 11.2.2-3 (servicio, p. 11.2-23) | parte 2: F·brazo | 17.15 | 17.162 | 0.052 | sí | — |
| 11.2.2-3 (servicio, p. 11.2-23) | parte 3: F·brazo | 67.69 | 67.640 | 0.088 | sí | — |
| 11.2.2-3 (servicio, p. 11.2-23) | parte 4: F·brazo | 3.15 | 3.080 | 0.076 | sí | — |
| 11.2.2-3 (servicio, p. 11.2-23) | parte 5: F·brazo | 13.50 | 13.504 | 0.051 | sí | — |
| 11.2.2-3 (servicio, p. 11.2-23) | parte 6: F·brazo | 394.47 | 394.733 | 0.219 | **NO** | 29.37 × 13.44 = 394.73; la misma fila de la tabla sismica imprime 394.66, y ninguna fuerza que se imprima 29.37 da 394.47 |
| 11.2.2-3 (servicio, p. 11.2-23) | parte 7: F·brazo | 3.63 | 3.630 | 0.025 | sí | — |
| 11.2.2-3 (servicio, p. 11.2-23) | parte 8: F·brazo | 65.99 | 65.993 | 0.101 | sí | — |
| 11.2.2-3 (servicio, p. 11.2-23) | parte PA·sen δA: F·brazo | 56.43 | 56.430 | 0.249 | sí | — |
| 11.2.2-3 (servicio, p. 11.2-23) | parte PA·cos δA: F·brazo | -175.49 | -184.138 | 0.145 | **NO** | el brazo impreso «10.65» es errata de 10.15: −17.29 × 10.15 = −175.49, que es el momento impreso (y el brazo de la tabla sismica y de la Tabla 11.2.2-4) |
| 11.2.2-3 (servicio, p. 11.2-23) | ΣM_O | 465.80 | 465.800 | 0.050 | sí | suma de los momentos IMPRESOS de la tabla |
| 11.2.2-1 (p. 11.2-18) y p. 11.2-21 | ΣW | 50.02 | 50.010 | 0.040 | sí | la p. 11.2-21 escribe V = 50.02 + 5.34 y la Tabla 11.2.2-1 suma 50.01: dentro del redondeo de sus ocho partes |

Las filas que no cuadran son erratas de la fuente. La de la parte 6 de servicio deja la suma 0.26 kip-ft corta (0.06 %, sin efecto en x ni en e a dos cifras); la del brazo de PA·cos δA es solo de la cifra del brazo, porque el momento impreso es el correcto. Los contrastes de las secciones 2 y 3 usan las sumas IMPRESAS.

## 5. Lo que no se contrasta, y por qué

| Fuente | Qué | Por qué |
|---|---|---|
| Caltrans BDP 11.2.2 | P_A y P_AE por cuña de tanteo (17.54 y 31.56 kip) | la superficie del relleno (talud y tramo horizontal) solo esta en la Fig. 11.2.2-1, sin cotas suficientes para reconstruir AB = 30.44 ft; contrastar `M9.cuna_de_tanteo` exige esa geometria |
| Caltrans BDP 11.2.2 | k_PE y k_P de las cartas de AASHTO (Fig. A11.4-2 y 3.11.5.4-1) | M9 no calcula el empuje pasivo de espiral logaritmica; el cabezal no cuenta con el pasivo frente a la punta |
| Caltrans BDP 11.2.2 | Desplazamiento sismico de Anderson (A11.5.2, 5.4 in) | M9 no implementa Newmark ni sus correlaciones |
| Caltrans BDP 11.2.2 | q_n de las Fig. 11.2.2-3 y -4 | son lecturas de graficas del sitio del ejemplo |
| Caltrans BDP 11.2.2 | Cortante de interfaz (5.7.4) y corte de barras (5.10.8) | M9 no los verifica |
| Caltrans BDP 11.2.2 | θ y β por el procedimiento general (Apendice B5) | M9 no implementa el procedimiento general: fuera del simplificado levanta `MetodoNoEvaluableError` (T-7c). Se contrasta Vc con el β de la fuente y la decision de no usar el simplificado |
| Caltrans BDP 11.2.2 | Acero de temperatura 0.0018·b·h (C5.10.6) | la fuente usa la regla del comentario; M9 la ec. 5.10.6-1 con el ancho real del elemento (en un muro largo las dos dan ~0.31 in²/ft por cara en 28.5 in, pero el ejemplo no da la longitud del muro) |
| CDOT Ex. 11 | Llave de corte por bloque inerte (BDM 11.5.1, R1, R2, Rep) | regla de la agencia; el cabezal de M9 no lleva llave |
| CDOT Ex. 11 | Carga de colision CT y combinaciones Extreme II | el cabezal de una alcantarilla no recibe la baranda del ejemplo |
| CDOT Ex. 11 | EFW minimo de 36 pcf (BDM 11.5) | regla de la agencia: se contrasta el empuje con el EFW que la hoja usa, no se valida el minimo |
| CDOT Ex. 11 | Example 8 (aleta en voladizo de un estribo integral) | la aleta del ejemplo vuela HORIZONTALMENTE desde el estribo, con la presion trapezoidal de una ayuda de diseño de Caltrans; el alero de M9 es un voladizo vertical sobre su zapata. Lo unico comun, K0 = 1 − sen φ = 0.4408 (celda E78), M9 lo calcula dentro de `cargas_del_cabezal`, sin funcion publica que llamar |
| ambas | Contraste E.060 (fila A5 del armado) | las dos fuentes son AASHTO; no hay ejemplo E.060 que contrastar |

## 6. Observaciones para el dueño (no son defectos)

- **O-1.** El modulo de elasticidad del concreto. M9 toma n con la expresion del comentario C5.4.2.4-1 (2500·f'c^0.33 ksi, la de wc = 0.145 kcf); la ec. 5.4.2.4-1 con un peso unitario mayor (CDOT usa 0.150 kcf) da un Ec mayor y un n menor (6.54 frente a 7.06). En f_ss la diferencia es menor del 0.5 % en los dos ejemplos, porque j casi no depende de n. Se deja al dueño si M9 debe usar la ec. 5.4.2.4-1 con el peso unitario del concreto del proyecto (no se midio aqui cual es).
- **O-2.** El «b» del acero de temperatura. CDOT toma b = 12 in (la franja de calculo); M9 pasa el ancho real del elemento, que es lo que AASHTO 5.10.6 llama «least width of component section». Con el ancho real el minimo es mayor en un muro largo; ninguno de los dos ejemplos baja del piso de 0.11 in²/ft.

## 7. Resumen

- **Caltrans BDP 11.2.2:** 28 contrastes — 25 «coincide»; 2 «errata de la fuente; el motor coincide con lo recalculado»; 1 «difiere por método (declarado)»; 0 «DEFECTO DEL MOTOR».
- **CDOT Ex. 11:** 33 contrastes — 28 «coincide»; 3 «errata de la fuente; el motor coincide con lo recalculado»; 2 «difiere por método (declarado)»; 0 «DEFECTO DEL MOTOR».
- **Aritmética de Caltrans:** 2 filas que no cuadran, de 30.
- **Defectos del motor: 0.**
