# Validación de punta a punta contra ejemplos externos publicados

Programa: `/home/user/val_web`, commit `2d37c2c7298aabf1fec8602eddf745fa70994cc2` (árbol limpio: no se editó ni se escribió nada versionado; todas las entradas, scripts y salidas están en `/tmp/validacion_web/`).
Fecha: 2026-11-15. Entorno: Python 3.12.3, ttkbootstrap 2.2.1, weasyprint 69.0, numpy 2.2.3, scipy 1.15.2, `xvfb-run`, `NORMAS_DIR=/home/user/andy-rba30/normas`.

Todo se corrió por las puertas normales de la app: `python cli.py <csv> --alcance perfil --datos-externos … [--cuencas … --estacion …] [--datos-sitio …] --declarar … --json … --html …` (y `--prevuelo`), y la **ventana real** (`gui.app`) bajo xvfb para tres casos. No se llamó a ninguna función suelta del motor salvo en la reproducción mínima del defecto D1. Los comandos exactos están en `COMANDOS.md` (y en el `comandos.txt` de cada caso); la tabla completa de contraste (371 filas, con el recálculo a mano en la última columna) en `tabla_contraste.md`; todo en estructura en `resultados.json`.

## 1. Resumen

| Ejemplo (fuente) | Qué se comparó | Resultado | Fuera de tolerancia y por qué |
|---|---|---|---|
| **TDOT Ej. 2** (HY-8, 10 caudales) | HW de entrada, control, y_n, y_c, TW por Manning en el cauce, tirante y velocidad de salida | **Coincide**: control de entrada en 10/10; HW −1.5 % a +0.1 %; TW ±0.1 %; V (n=0.013) ±0.5 % | y_n e y_c a 2.5 cfs (+5.7 %, +4.6 %): **(b) fuente** (HY-8 no satisface Manning ni Q²/g=A³/T con sus propios datos). V_salida que usa la protección +30 %: **(c) método** (n_min, techo conservador declarado) |
| **TDOT Ej. 1** (a mano, nomogramas) | HW_i, d_c, h_o, H, HW_o, d_o, V, control | **Coincide** en todo (≤0.9 %) | ninguna |
| **TDOT Ej. 4** (HY-8, S=3 %) | HW a 69.2 cfs (inicio de rebose), TW, y_c, y_n, V | HW +0.5 %, TW ±0.2 %; la app descarta el 36 in (V3, V4b), como TDOT | y_c (−4.0 %): **(b) fuente** (HY-8 cerca de y_c/D→1). y_n (+5.8 %) y V (+4.5 %): **(c)** n=0.013 de la Tabla N° 09 frente a 0.012, y V al tirante normal (HDS-5 3.3.2) frente a curva S2 |
| **UPAO La Jalca** (Gumbel, Témez, Kirpich) | P24(T) Gumbel, Tc Témez, K, Tc Kirpich, I, C, Q | P24(50/100/500) ±0.003 %; Tc Témez +0.1 %; K +0.4 %; Kirpich +0.03 % y −0.3 % | X_T con 1.13 (−11.5 %), I de Tinas (−13.9 %), I de la cuneta (+52 %): **(c)**. Q de Tinas (55.9 km²): la app **se detiene** (racional < 10 km²) — **(c)** alcance declarado (ficha T1-08) |
| **UNC Cocahuayco** (Témez, C, alcantarilla 36 in) | Tc Témez (3 cuencas), C de la Tabla N° 08, y_c, HW | Tc −0.1 a −0.2 %; C = 0.45 exacto; y_c +2.6 % (lectura de gráfico); HW −3.8 % (French vs HDS-5) | I no comparable: **(b)** la tesis dice I15 = 120.01 mm/h y usa 39.61 |
| **UPAO alcantarillas** (Manning, 5 filas) | diámetro comercial | difiere en 5/5 | **(c) norma**: mínimo 0.90 m (núm. 4.1.1.3.4 a), V3 de la Tabla N° 10, pendiente acotada a 10 %; la S de la tesis (0.21–0.39) no trae unidad: **(b)** |
| **OBRA REAL WisDOT STH 32** (HY-8, 9 cruces, 18 caudales) | control, HW entrada, HW gobernante, y_c, y_n, TW, V | 12/18 con hidráulica: **control coincide 12/12; HW gobernante −0.2 a +0.6 %** (también bajo control de salida, por el remanso de la app); y_c ≤ +0.4 %; TW ≤ 0.6 % | y_n (+5 a +8 %): **(c)** n=0.013 vs 0.012 (a mano con 0.012 reproduce HY-8). V bajo control de entrada (+24 a +36 %): **(c)**. 6 escalones sin hidráulica: con n = 0.013 no existe tirante normal y la app descarta el escalón sin calcular HW: **(c)** |
| **OBRA REAL TU-107 Tumbes** (41 cuencas, serie de 40 años) | P24 LN2P, K-S, Tc Témez, C, I, Q, paradas | P24(35) 719.34 vs 719.39 (sin 1.13), K-S Δ = 0.0535 igual; Tc ±4.9 %; C 34/34 igual (fila inferida); 5 paradas por A ≥ 10 km² (la tesis también cambia de método) y 2 por Tc < 0.25 h | I y Q con Dick-Peschke ×1.48 a ×2.36; con la Tabla N° 04 (6 cuencas con Tc ≥ 1 h) −0.3 a −9.8 %: **(c)** método (IDF propia con 1.13). La app ajusta la serie sospechosa sin avisar de su magnitud (observación) |
| OBRA REAL Dale Blvd (ensayo de laboratorio) | HW | +16 % y +31 % | **(c)** configuración fuera de HDS-5 (dos diámetros en serie, entrada acampanada); además D > 2.70 m |
| OBRA REAL MnDOT, TU-107-05, Querari | — | no corridos | sin HW publicado / sin magnitud HDS-5 / fuente inconsistente (§6) |

**Ninguna diferencia fuera de tolerancia se clasificó como defecto del programa.** Las 116 filas fuera de tolerancia de `tabla_contraste.md` son 3 de la fuente (b) y 113 de método o norma (c), cada una con su recálculo independiente. Los dos **defectos candidatos** (§7) salieron de correr la app, no de una diferencia de resultado: **D1** (la progresión de diámetros declarada se redondea a 2 decimales y luego se rechaza a sí misma) y **D2** (V7 no lee el nivel freático aunque el contrato de entradas dice que sí).

**Ventana real** (§5): tres casos (TDOT Ej. 2, cadena hidrológica UPAO/UNC y un grupo de cruces de WisDOT) cargados por «Examinar…», declarados por la pestaña 2, ejecutados, leídos en la pestaña 3 y exportados por «Exportar JSON»: el JSON de la ventana es **idéntico** al de la CLI salvo la hora (0 diferencias, rutas incluidas), y la sesión guardada por la ventana, repuesta con `cli.py --sesion`, «REPRODUCE» la corrida.

## 2. Método

**Conversiones** (exactas): 1 ft = 0.3048 m; 1 ft³/s = 0.028316846592 m³/s (= 0.3048³); 1 in = 0.0254 m. Ej.: 341.25 ft = 104.013 m; 340.70 ft = 103.84536 m; 110 ft = 33.528 m; 36 in = 0.9144 m; 25 cfs = 0.707921 m³/s; 1.8 ft = 0.54864 m. Las cotas se escribieron con 6 decimales (con 4, la salida quedaba 0.04 mm bajo el receptor y G2 fallaba: era redondeo mío, no de la app; queda en `casos/TDOT_EX2/_primer_intento_salida`).

**Cómo se fijó lo que el ejemplo fija** (todo por `--declarar`, la puerta de la pestaña 2): el diámetro, con `diametros_normalizados = {"inicio": D, "paso": …}`; el espesor de pared de un diámetro que la tabla de AASHTO M 170M no tiene (914, 762, 686, 610 mm), con `espesor_pared_conducto` (pared B de ASTM C76, **dato de prueba**: no entra en la hidráulica); TR = 50/100/500, con `riesgo_admisible_propietario` (R despejado de R = 1−(1−1/T)ⁿ); distribución, tratamiento FEN y K de Témez con sus criterios. **No se pudo fijar** el n del concreto: es [N] de la Tabla N° 09 (0.010–0.013) y no es declarable; la app usa n_max = 0.013 para tirante y capacidad. Cuando hizo falta leer la hidráulica de un escalón que la app **descarta** (TDOT Ej. 4, WisDOT, Dale), se dejó al concreto como único candidato con dos ensayos de durabilidad de prueba (resistividad 500 Ω·cm excluye TMC; abrasión severa excluye HDPE) y una serie de un solo diámetro (el siguiente supera el tope de 2.70 m); la hidráulica del escalón descartado se lee de la memoria HTML (`scripts/memoria_txt.py`) y del motivo del descarte en el JSON.

**Datos de prueba e invariancia** (`invariancia.json`): cada caso se corrió en dos variantes, `base` y `alt`, que mueven **solo** los datos de prueba (área, terreno, rasante, subrasante, CBR, SUCS, luz, ancho de plataforma, altura del canal, espesor de pared, columna FEN, cobertura no publicada, área de diagnóstico). Las magnitudes comparadas no se mueven: diferencia máxima 3·10⁻¹¹ m (TDOT Ej. 2), 0 en TDOT Ej. 1, UNC y WisDOT, motivos de descarte idénticos en Ej. 4, P24/Tc/K/I/C/Q idénticos en las cadenas hidrológicas. Lo que sí se mueve se declara y no se compara: el C de Tinas y de la cuneta (cobertura de prueba) y el h_o de UPAO-Manning (TW de prueba; el diámetro comparado no cambia).

**Rasante de TDOT**: la publicada (hombro, 345.32 ft) se probó tal cual (`casos/TDOT_EX2/publicada`): la app **rechaza** el 36 in por V7 (flotación) en los 10 caudales y por V4 (resguardo MTC según CBR, con subrasante y CBR de prueba) desde 7.5 cfs —criterios peruanos que TDOT no aplica, (c)— y el punto termina detenido por el defecto D1. Para leer la hidráulica del 36 in se subió la rasante como dato de prueba (+1.25 m / +2.25 m).

**Tolerancias**: HY-8 y ecuaciones ±3 % (HY-8 ajusta polinomios a los nomogramas para el control de entrada); nomograma ±5 %; tablas de tesis según su redondeo (±0.5–1 % para fórmulas exactas, ±5 % para Tc con S publicada a 2 decimales, ±10 % para métodos distintos como French o el ensayo de Dale).

**Recálculo independiente**: `scripts/recalculo_mano.py`, `scripts/hds5_mano.py` (Manning, crítico exacto, HDS-5 Apéndice A con la transición lineal entre q* = 3.5 y 4.0, en unidades inglesas, sin importar nada de la app), `scripts/compara_wisdot.py`, `scripts/compara_tu107.py`. El resultado de cada fila está en la columna «a mano» de `tabla_contraste.md`.

## 3. Ejemplos de manual y de tesis

### 3.1 TDOT Ejemplo 2 (HY-8), 36 in de concreto, S = 0.005, L = 110 ft

Entradas: `casos/TDOT_EX2/{base,alt,publicada}` (generadas por `scripts/arma_tdot_ex2.py`) y `declaraciones_base.txt`. El TW **no se declaró**: la app lo calculó por Manning en el cauce publicado (rectangular-trapecial b = 3 ft, z = 3, S = 0.005, n = 0.065) con `seccion_receptor_medida` y `Q_receptor_m3s` = Q. Corridas: 10/10 puntos dimensionados (concreto Ø 0.9144 m), perfil cerrado (código 0). Valores en ft y ft/s (publicado / app (dif. %)):

| Q (cfs) | HW entrada | y_n | y_c | TW | y salida | V (n=0.013) | V_salida que usa la protección (n_min) | control |
|---|---|---|---|---|---|---|---|---|
| 2.5 | 0.659 / 0.655 (−0.6) | 0.444 / 0.469 (+5.7) | 0.470 / 0.492 (+4.6) | 0.584 / 0.585 (+0.1) | 0.460 / 0.469 (+2.0) | 3.534 / 3.538 (+0.1) | 3.534 / 4.599 (+30.1) | entrada = |
| 5 | 0.952 / 0.945 (−0.8) | 0.651 / 0.660 (+1.3) | 0.688 / 0.700 (+1.8) | 0.833 / 0.833 | 0.657 / 0.660 | 4.335 / 4.340 | 4.335 / 5.642 (+30.1) | entrada = |
| 7.5 | 1.180 / 1.175 (−0.4) | 0.797 / 0.809 (+1.5) | 0.856 / 0.862 (+0.7) | 1.017 / 1.018 | 0.805 / 0.809 | 4.877 / 4.880 | 4.877 / 6.344 (+30.1) | entrada = |
| 10 | 1.376 / 1.377 (+0.1) | 0.934 / 0.938 (+0.4) | 0.992 / 1.000 (+0.8) | 1.170 / 1.170 | 0.941 / 0.938 | 5.294 / 5.296 | 5.294 / 6.885 (+30.1) | entrada = |
| 12.5 | 1.561 / 1.562 (+0.1) | 1.046 / 1.054 (+0.8) | 1.116 / 1.123 (+0.6) | 1.301 / 1.301 | 1.055 / 1.054 | 5.617 / 5.637 (+0.3) | 5.617 / 7.328 (+30.5) | entrada = |
| 15 | 1.753 / 1.736 (−1.0) | 1.158 / 1.163 (+0.4) | 1.232 / 1.235 (+0.2) | 1.417 / 1.417 | 1.161 / 1.163 | 5.933 / 5.926 | 5.933 / 7.703 (+29.8) | entrada = |
| 17.5 | 1.930 / 1.902 (−1.4) | 1.261 / 1.265 (+0.3) | 1.331 / 1.338 (+0.6) | 1.521 / 1.522 | 1.270 / 1.265 | 6.144 / 6.176 (+0.5) | 6.144 / 8.029 (+30.7) | entrada = |
| 20 | 2.095 / 2.063 (−1.5) | 1.359 / 1.364 (+0.4) | 1.430 / 1.435 (+0.4) | 1.619 / 1.618 | 1.360 / 1.364 | 6.417 / 6.397 | 6.417 / 8.316 (+29.6) | entrada = |
| 22.5 | 2.252 / 2.220 (−1.4) | 1.456 / 1.459 (+0.2) | 1.524 / 1.526 (+0.2) | 1.708 / 1.708 | 1.463 / 1.459 | 6.570 / 6.594 (+0.4) | 6.570 / 8.572 (+30.5) | entrada = |
| 25 | 2.402 / 2.375 (−1.1) | 1.551 / 1.553 (+0.1) | 1.607 / 1.613 (+0.4) | 1.791 / 1.791 | 1.556 / 1.553 | 6.755 / 6.769 (+0.2) | 6.755 / 8.800 (+30.3) | entrada = |

Recálculo a mano de lo que queda fuera de ±3 %:

- **y_n a 2.5 cfs (+5.7 %) → (b) fuente.** Manning con D = 3 ft, n = 0.013, S = 0.005: y_n = **0.469 ft** (= app). El 0.444 ft de HY-8, metido en Manning con esos mismos datos, transporta **2.23 cfs**, no 2.5: el número publicado no cuadra con sus propias entradas.
- **y_c a 2.5 cfs (+4.6 %) → (b) fuente.** Crítico exacto Q²/g = A³/T: **0.492 ft** (= app). El 0.470 ft de HY-8 corresponde a Q = **2.29 cfs**. A partir de 5 cfs la discrepancia baja a ≤1.8 %.
- **V_salida (+30 %) → (c) método declarado.** La app entrega a la protección (Fase 6) la velocidad con n_min = 0.010 sobre la geometría de n_max (regla de doble n, `modelos.TiranteNormal`; procedencia «HDS-5 núm. 3.3.2 y 3.1.6 … se toma la de n MINIMO … techo conservador»). Cociente medido 1.30 = 0.013/0.010. Con n = 0.013 (V_sedimentación) coincide con HY-8 a ±0.5 %.
- HW de entrada: HDS-5 Forma 1 a mano a 25 cfs = **2.376 ft** (= app 2.375); HY-8 2.402 (−1.1 %) usa polinomios de los nomogramas. Dentro de tolerancia en los 10.

### 3.2 TDOT Ejemplo 1 (a mano, nomogramas), mismo sitio, Q = 25 cfs, TW = 1.8 ft declarado

`casos/TDOT_EX1`. Dimensionado, control de entrada (TDOT: entrada, 343.62 > 343.45).

| Magnitud | TDOT | App | Dif. % | A mano |
|---|---|---|---|---|
| HW entrada (ft) | 2.37 (HW/D 0.79 leído) | 2.375 | +0.2 | 2.376 |
| d_c (ft) | 1.61 | 1.613 | +0.2 | 1.613 |
| h_o (ft) | 2.3 | 2.306 | +0.3 | 2.307 |
| H, pérdidas (ft) | 0.45 (nomograma, L ajustada por n) | 0.446 | −0.9 | 0.445 (n = 0.013, L = 110 ft) |
| HW salida, aproximación H + h_o − S·L (ft) | 2.20 | 2.203 | +0.1 | 2.202 |
| d_o (ft) | 1.55 | 1.553 | +0.2 | 1.553 |
| V salida (ft/s) | 6.78 | 6.769 (n = 0.013) | −0.2 | 6.769 |

Diferencia de método sin efecto en el resultado: con HW_aprox/D = 0.734 < 0.75 la app no usa la aproximación de control de salida (HDS-5 3a ed. núm. 3.3.3, «should not be used») y la sustituye por el remanso, que no alcanza la entrada; TDOT usa la aproximación. Los dos concluyen control de entrada con el mismo HW.

### 3.3 TDOT Ejemplo 4 (HY-8), S = 3 %, entrada cuadrada con muro

`casos/TDOT_EX4/{base,alt}` (solo concreto, un escalón de 36 in) y `diseno_libre` (la progresión de la app). La app descarta el 36 in en 69.2, 72 y 90 cfs (V3: V(n_min) = 6.77 > 6.0 m/s; V4b: HW/D = 1.93 > 1.5); TDOT también lo descarta (HW 347.25 ft sobre la calzada). Con su progresión, la app elige **TMC Ø 1.20 m** (el concreto falla V3 en todos sus diámetros a 3 %); TDOT eligió 36 in con entrada mejorada (fuera del alcance de la app).

| Magnitud | HY-8 | App | Dif. % | Clasificación / a mano |
|---|---|---|---|---|
| HW a 69.2 cfs (rebose: 347.00 − 341.25) | 5.75 ft | 5.778 ft (HW/D 1.926, sumergido) | +0.5 | a mano HDS-5 sumergida: 5.779 ft |
| TW a 72 cfs / 90 cfs | 1.81 / 2.005 ft | 1.807 / 2.005 ft | −0.2 / 0.0 | — |
| y_c a 90 cfs | 2.967 ft | 2.848 ft | −4.0 | **(b) fuente**: crítico exacto 2.846 ft; HY-8 se desvía cuando y_c/D → 1 |
| y_n a 90 cfs | 1.883 ft (n = 0.012) | 1.991 ft (n = 0.013) | +5.8 | **(c) norma**: Manning a mano n = 0.012 → 1.883 (= HY-8); n = 0.013 → 1.991 (= app) |
| V salida a 90 cfs | 17.29 ft/s | 18.07 ft/s (n = 0.013) | +4.5 | **(c) método**: V al tirante normal (HDS-5 pág. 3.24, «assumed») frente a la curva S2 de HY-8 (tirante 2.072 ft en 110 ft); a mano V(2.072 ft) = 17.28 |

(Los valores de barril a 90 cfs de HY-8 vienen de la corrida con entrada mejorada; el barril es el mismo.)

### 3.4 Cadena hidrológica UPAO La Jalca + UNC Cocahuayco

`casos/HIDRO_UPAO_UNC/{base,alt}`, dos corridas por variante (TR 100/50 y 500/100). Serie: los 17 años publicados de Chachapoyas (la tesis omite 1974–2003; la app lo avisa); columna `fen` de prueba (con `serie_completa` no entra al ajuste: idéntico con 1972-73 marcados). Distribución declarada `gumbel`.

| Magnitud | Publicado | App | Dif. % | Clasificación / a mano |
|---|---|---|---|---|
| X'_T(50) | 57.2041 mm | 57.2053 | 0.00 | a mano 57.2053 |
| X'_T(100) | 61.4878 mm | 61.4892 | 0.00 | 61.4892 |
| X'_T(500) | 71.3868 mm | 71.3886 | 0.00 | 71.3886 |
| X_T(100) con ×1.13 | 69.48 mm | 61.49 | −11.5 | **(c)**: la app no aplica el factor de intervalo fijo 1.13; el Manual de Hidrología del MTC no lo trae (buscado en el PDF: ninguna ocurrencia de «1.13» ni «intervalo fijo»). 61.489 × 1.13 = 69.48 |
| Tc Témez, Tinas | 3.95 h | 3.954 h | +0.1 | 3.9540 h |
| K uniformidad, Tinas | 1.28 | 1.2848 | +0.4 | 1.2848 |
| Tc Kirpich, Tinas | 93.07 min | 93.10 | +0.03 | 93.099 |
| I de diseño, Tinas | 11.51 mm/h | 9.908 | −13.9 | **(c)**: la tesis aplica el racional modificado completo del Manual (ec. 32–34: K_A = 0.8835, P = 61.39 mm, I con el 11 de Témez) sobre P24 × 1.13 → a mano **11.512** (la fuente cuadra). La app usa Dick-Peschke sobre P24 sin 1.13 ni K_A (uso híbrido declarado, ficha T1-08) → a mano **9.908** (= app) |
| C, Tinas | 0.32 (ec. 35 con CN = 72) | no se compara | — | a mano ec. 35: 0.3220; la app toma C de la Tabla N° 08 y la tesis no publica la cobertura |
| Q, Tinas (55.911 km²) | 74.03 m³/s | **detenida** | — | **(c)**: `MetodoNoEvaluableError` «el Manual sitúa el método racional en cuencas de área menor de 10 km² (núm. 3.12.2) y la cuenca tiene 55.911 km²». El racional modificado (núm. 3.12.2.1, hasta 770 km²) no está implementado (ficha T1-08) |
| Tc Kirpich, cuneta 1 | 1.05 min | 1.047 | −0.3 | 1.0468 |
| I, cuneta 1 | 109.84 mm/h (TR 10, IDF propia, t = 1.05 min) | 166.6 (TR 50, 5 min) | +52 | **(c) norma/método**: TR 10 no se puede (la Tabla N° 02 da TR ≥ 35 en cunetas y la app solo deja endurecer); duración mínima 5 min [C]; Dick-Peschke en vez de la IDF de la tesis |
| Tc Témez UNC Cajahuache / A1 / A2 | 97.75 / 38.23 / 34.35 min | 97.66 / 38.20 / 34.28 | −0.1 / −0.1 / −0.2 | 97.66 / 38.20 / 34.28 |
| C UNC (pastos, semipermeable, media) | 0.45 | 0.45 (con S_terreno 0.10 y 0.15) | 0 | — |
| I UNC A1 | 39.61 mm/h | no comparable | — | **(b)**: la tesis da I₁₅ = 120.01 mm/h en el texto y usa 39.61 en la Tabla 15, la misma para t = 38 y 34 min; su aritmética Q = 0.45·39.61·1.191/3.6 = 5.897 sí cuadra |

Variante de diagnóstico (rotulada en los archivos): para leer Tc, K, P24 e I de Tinas —que no dependen del área— se repitió la cuenca con **área de prueba** 9.5 km² (y 9.0 en `alt`); su C y su Q no se comparan. Otras inconsistencias de la fuente, sin efecto en lo comparado: UPAO trae un Cuadro 19 de Chachapoyas con otra serie (P100 = 88.15 mm) incompatible con la tabla Gumbel; UNC da 7.76 km² (Tabla 13) y 9.863 km² para Cajahuache.

### 3.5 UNC: alcantarilla de 36 in (método de French)

`casos/UNC_ALC36`. Para que la app evalúe el TMC (el concreto va primero en su orden) se declaró `v_max_concreto_eleccion = 3.0` (mínimo de su ventana): el concreto cae por V3 y la app dimensiona TMC Ø 0.90 m, control de entrada. y_c a 0.79 m³/s: tesis 0.51 m (gráfico), app **0.523** (exacto) (+2.6 %, dentro de ±5 %). HW a 0.80 m³/s: tesis Y1 = 0.80 m (French, C_d = 0.89, flujo tipo 1), app **0.770 m** (HDS-5, carta CMP con muro) (−3.8 %, (c) método; los dos dan control de entrada / flujo tipo 1).

### 3.6 UPAO: diseño por Manning (5 de 46 filas)

`casos/UPAO_MANNING`. Tesis: TMC 24 in (N° 1, 13, 46) y 36 in (N° 40, 44), n = 0.024, y/D ≈ 0.75. App: N° 1 concreto Ø 0.90 m; N° 46 concreto Ø 1.35 m (sube para bajar V de 6.28 a < 6.0 m/s); N° 13, 40 y 44 **no factibles** (V3 en los tres materiales). **(c) norma**: mínimo de 0.90 m del Manual núm. 4.1.1.3.4 a) (la app lo adopta sin condición, declarado en `diametros_normalizados`), V3 de la Tabla N° 10 con n_min, pendiente del conducto acotada a 10 % [A]. **(b) fuente**: las S publicadas (0.21–0.44) no traen unidad; la tabla es consistente con m/m (N° 40: Manning con D = 0.894, y = 0.67, n = 0.024, S = 0.21 da 4.02 m³/s frente a 4.042), pendientes irreales para un barril.

## 4. Obras reales

### 4.1 WisDOT STH 32 (Oconto County, proyecto 9190-26(27)-00), reporte HY-8 — el caso hidráulico más fuerte

`casos/OBRA_WISDOT/{base,alt}/D{2.0,2.25,2.5,3.0}ft` (una corrida por diámetro; `scripts/arma_wisdot.py`), 18 puntos (Q de diseño y máximo de los 9 cruces). Entradas publicadas: Q, D, inverts (S = Δinvert/L declarada), L, canal de salida rectangular (b = 8 ft, S = 0.33, n = 0.029, invert) para el TW por Manning, cota de calzada. Consistencia de la fuente comprobada por el buscador y aquí (HW = invert + profundidad gobernante; y_c y la entrada HDS-5 reproducidos a mano). Valores en ft y ft/s (HY-8 / app):

| Punto | Q | D | S | HY-8 control (tipo) | app | HW entrada HY-8 / app / a mano | HW gobernante (dif. %) | y_c | y_n HY-8 (0.012) / app (0.013) / a mano 0.012 | TW* | V |
|---|---|---|---|---|---|---|---|---|---|---|---|
| WI-C1-Qd | 14 | 2.0 | 0.0030 | salida (7-M2c) | sin hidráulica | 2.139 / — / 2.140 | 2.221 / — | 1.344 / — | 1.761 / — / 1.746 | 0.187 / 0.187 | 6.235 / — |
| WI-C1-Qm | 17 | 2.0 | 0.0030 | salida (7-M2c) | sin hidráulica | 2.508 / — / 2.509 | 2.551 / — | 1.484 / — | 2.000 / — / — | 0.211 / 0.210 | 6.799 / — |
| WI-C2-Qd | 20 | 2.25 | 0.0174 | entrada (5-S2n) | entrada | 2.508 / 2.507 / 2.507 | 2.508 / 2.507 (−0.1) | 1.560 / 1.565 | 1.059 / 1.112 / 1.061 | 0.633 / 0.633 | 9.796 / 13.287 |
| WI-C2-Qm | 26 | 2.25 | 0.0174 | entrada (5-S2n) | entrada | 3.183 / 3.189 / 3.190 | 3.183 / 3.189 (+0.2) | 1.778 / 1.781 | 1.238 / 1.302 / 1.240 | 0.674 / 0.673 | 10.448 / 14.154 |
| WI-C3-Qd | 15 | 2.5 | 0.0030 | salida (2-M2c) | salida | 1.938 / 1.913 / 1.913 | 2.055 / 2.051 (−0.2) | 1.304 / 1.306 | 1.413 / 1.490 / 1.414 | 0.195 / 0.197 | 5.790 / 5.781 |
| WI-C3-Qm | 19 | 2.5 | 0.0030 | salida (2-M2c) | salida | 2.246 / 2.234 / 2.236 | 2.363 / 2.362 (−0.0) | 1.474 / 1.476 | 1.655 / 1.755 / 1.655 | 0.226 / 0.226 | 6.311 / 6.289 |
| WI-C4-Qd | 21 | 2.5 | 0.0030 | salida (7-M2c) | salida | 2.399 / 2.395 / 2.396 | 2.513 / 2.523 (+0.4) | 1.554 / 1.558 | 1.786 / 1.909 / 1.787 | 0.240 / 0.240 | 6.546 / 6.532 |
| WI-C4-Qm | 26 | 2.5 | 0.0030 | salida (7-M2c) | sin hidráulica | 2.802 / — / 2.801 | 2.894 / — | 1.733 / — | 2.249 / — / 2.244 | 0.274 / 0.272 | 7.161 / — |
| WI-C5-Qd | 42 | 3.0 | 0.0081 | entrada (5-S2n) | entrada | 3.420 / 3.415 / 3.415 | 3.420 / 3.415 (−0.1) | 2.109 / 2.110 | 1.756 / 1.850 / 1.757 | 0.368 / 0.367 | 9.346 / 11.923 |
| WI-C5-Qm | 52 | 3.0 | 0.0081 | entrada (5-S2n) | entrada | 4.146 / 4.150 / 4.152 | 4.146 / 4.150 (+0.1) | 2.342 / 2.346 | 2.033 / 2.162 / 2.032 | 0.421 / 0.420 | 9.894 / 12.405 |
| WI-C6-Qd | 25 | 2.0 | 0.0151 | entrada (5-S2n) | entrada | 3.823 / 3.845 / 3.845 | 3.823 / 3.845 (+0.6) | 1.761 / 1.762 | 1.392 / 1.483 / 1.391 | 0.267 / 0.266 | 10.477 / 13.015 |
| WI-C6-Qm | 31 | 2.0 | 0.0151 | entrada (5-S2n) | sin hidráulica | 5.187 / — / 5.200 | 5.187 / — | 1.875 / — | 1.710 / — / 1.698 | 0.305 / 0.305 | 10.841 / — |
| WI-C7-Qd | 25 | 2.0 | 0.0298 | entrada (5-S2n) | entrada | 3.808 / 3.829 / 3.831 | 3.808 / 3.829 (+0.5) | 1.761 / 1.762 | 1.105 / 1.165 / 1.106 | 0.267 / 0.266 | 13.213 / 17.139 |
| WI-C7-Qm | 31 | 2.0 | 0.0298 | entrada (5-S2n) | entrada | 5.173 / 5.184 / 5.186 | 5.173 / 5.184 (+0.2) | 1.875 / 1.877 | 1.270 / 1.345 / 1.272 | 0.305 / 0.305 | 13.818 / 17.923 |
| WI-C8-Qd | 25 | 2.0 | 0.0100 | entrada (5-S2n) | sin hidráulica | 3.828 / — / 3.850 | 3.828 / — | 1.761 / — | 1.686 / — / 1.678 | 0.267 / 0.266 | 8.866 / — |
| WI-C8-Qm | 31 | 2.0 | 0.0100 | entrada (7-M2c) | sin hidráulica | 5.193 / — / 5.205 | 5.193 / — | 1.875 / — | 2.000 / — / — | 0.305 / 0.305 | 10.130 / — |
| WI-C9-Qd | 17 | 2.5 | 0.0029 | salida (2-M2c) | salida | 2.093 / 2.073 / 2.075 | 2.209 / 2.211 (+0.1) | 1.389 / 1.394 | 1.559 / 1.650 / 1.560 | 0.211 / 0.210 | 6.069 / 6.040 |
| WI-C9-Qm | 22 | 2.5 | 0.0029 | salida (7-M2c) | salida | 2.477 / 2.477 / 2.477 | 2.588 / 2.595 (+0.3) | 1.592 / 1.594 | 1.898 / 2.047 / 1.894 | 0.247 / 0.246 | 6.670 / 6.654 |

\* TW referido al invert de SALIDA. En C2 el canal está 0.40 ft sobre la salida: HY-8 publica la profundidad en el canal (0.233 / 0.274) y la app la cota de agua menos el fondo de la salida (0.233 + 0.40 = 0.633): es la misma lámina.

Lectura: donde hay hidráulica, **el control coincide en 12/12 y el HW gobernante queda entre −0.2 % y +0.6 % de HY-8**, también en los 5 puntos de control de salida (M2c), donde la app usa su remanso (HW/D < 1.2, HDS-5 3.3.3) y no la aproximación. Recálculo de lo que queda fuera de ±3 %:

- **y_n +5 a +8 % → (c) norma.** Manning a mano con n = 0.012 reproduce HY-8 (p. ej. C9-Qm 1.894 frente a 1.898); la app usa n = 0.013 (n_max de la Tabla N° 09, [N], no declarable).
- **V bajo control de entrada +24 a +36 % → (c) método**, el mismo de §3.1 (n_min y tirante normal, frente al tirante de la curva S2 de HY-8). Bajo control de salida los dos usan Q/A(y_c): −0.3 a −0.5 %.
- **6 escalones «sin hidráulica» → (c) norma/método.** La app los descarta con «el conducto no transporta Q en flujo libre con n = 0.013 (Sec. 4.1)» y no calcula HW. A mano: con n = 0.013 el caudal supera el pico de la sección parcial (p. ej. C6-Qm: Q_lleno = 27.8 cfs, Q_pico ≈ 29.9 < 31), de modo que no hay tirante normal; con n = 0.012 sí (1.698 ft). Es el diseño con borde libre obligatorio de la app (V1, núm. 4.1.1.3.7 b), documentado en `modelos.PasoDiseno`; HY-8 sí calcula el HW (en C1-Qm y C8-Qm publica y_n = D). Limitación para **verificar** tubos existentes, no un error de cálculo.

Además, con las cotas de prueba solo C9 pasa todas las verificaciones de la app (C2–C5 por V4, C6–C7 por V4b, C4 también por V7): consecuencia de los criterios MTC (resguardo según CBR, HW/D ≤ 1.5) y de cotas que no son las del proyecto; no se comparan.

### 4.2 TU-107 Bocapán–Tamarindo (Tumbes): hidrología de 41 cuencas

`casos/OBRA_TU107/{base,alt}` (`scripts/arma_tu107.py`, `scripts/compara_tu107.py` → `contraste.json`). Serie publicada **tal cual** (40 años, con 729.2 mm en 1997, 717 mm en 1991 y filas repetidas 1996/2001 y 1989/2002). Cobertura y suelo **inferidos** (rotulados): «bosques, densa vegetación, permeable» con la pendiente del cauce, la única fila de la Tabla N° 08 que reproduce las 36 C publicadas (0.10/0.15/0.20); por eso C no es un contraste independiente. Declarado: `lognormal_2p`, `serie_completa`, `coeficiente_uniformidad_temez = no_aplicar` (la tesis usa Q = C·I·A/3.6 sin K); dos variantes de relación I–d: `dick_peschke` (valor de archivo) y `tabla_04_coeficientes_de_duracion`.

| Magnitud | Tesis | App | Dif. | Clasificación / a mano |
|---|---|---|---|---|
| P24(T=35), LN2P sin 1.13 | 719.39 (media/desv log10 publicadas 2.117/0.389) | 719.34 | −0.01 % | de la serie: 719.34 |
| P24 con 1.13 | 813 | 719.34 | −11.5 % | (c), §3.4 |
| K-S Δ de la LN2P / Δ crítico | 0.0535 / 0.2150 | 0.0535 / 0.21 | igual | Tabla N° 03, n = 40 |
| TR quebrada importante | 70 (trunca 70.59) | 71 (redondea) | +1 año | (c) convención de redondeo |
| Tc Témez (34 cuencas) | 2a columna de la Tabla 27 | ±4.9 % máx. | dentro de ±5 % | a mano con la S publicada (2 decimales) = app; con S = (cota máx − cota mín)/L ±1.6 %: la tesis calculó con la S sin redondear |
| C (34 cuencas) | 0.10–0.20 | igual 34/34 | — | fila inferida |
| I y Q con Dick-Peschke | p. ej. C-1: I = 280.28, Q = 2.86 | I = 579.2, Q = 6.04 | Q × 1.48 a × 2.36 | **(c)**, abajo |
| I y Q con la Tabla N° 04 (6 cuencas con Tc ≥ 1 h) | C-2: 178.98 / 4.66; C-35: 142.41 / 32.02 | 178.44 / 4.66; 128.49 / 28.93 | Q +0.1 % a −9.6 % | **(c)**, abajo |
| C-6, C-7, C-13, C-16, C-17 (A = 12–103 km²) | hidrograma unitario | **detenida** (racional < 10 km²) | — | coherente: la tesis también cambia de método |
| C-20, C-27 (Tc Témez 0.203 y 0.245 h) | racional con Tc 0.19 y 0.22 h | **detenida** (Témez acotado a 0.25–24 h, núm. 3.12.2.1) | — | **(c)**: la tesis aplica Témez fuera de su rango |

Recálculo de I y Q (todas las filas en `tabla_contraste.md`):

- La fuente **cuadra consigo misma**: su IDF I = 408.8108·T^0.3910 / t^0.5375 (Tablas 61–62) con t = promedio de Témez y Bransby-Williams reproduce sus 34 intensidades a ±0.02 % (C-1: 408.81·35^0.391/26.81^0.5375 = 280.2), y Q = C·I·A/3.6 sus caudales a ±2.8 % (área redondeada).
- La app con Dick-Peschke, a mano: C-1, P24 = 719.34, d = 27.77 min → Pd = 719.34·(27.77/1440)^0.25 = 268.1 mm → I = 579.2 mm/h → Q = 0.278·0.15·579.2·0.25 = 6.04 m³/s (= app). Dick-Peschke da a 1 h Pd = 0.452·P24, y la Tabla N° 04 da 0.25·P24: **las dos relaciones del Manual difieren en ~80 % en duraciones cortas**, y la tesis usó la segunda (más el 1.13 y una regresión extrapolada bajo 1 h).
- La app con la Tabla N° 04, a mano: C-35, P24(71) = 934.90, d = 2.521 h → coef. = 0.31 + 0.07·0.521 = 0.3465 → I = 128.5 (= app). La tesis, Tabla N° 04 × 1.13 a 2.607 h: 0.3525·930.25·1.13/2.607 = 142.1 ≈ su 142.41. La diferencia (−9.8 %) es el 1.13 (−11.5 %) compensado en parte por TR 71 y la duración.

La app **no avisa** de la magnitud de la serie (729 mm en 24 h) ni de las filas repetidas: avisa que no hay años FEN declarados y que faltan 1988 y 2022, y ajusta. No hay umbral normativo de plausibilidad; si la serie mezcla totales mensuales (alerta del buscador, coherente con las filas duplicadas: 1996 y 2001 con máximo 63.0, 1989 y 2002 con 129.0), es un problema **(b)** de la fuente que la app no puede detectar. Nota de extracción: en `obras.json` las columnas `tc_temez_h` y `tc_bransby_h` están **invertidas** respecto del PDF (Tabla 27, pág. 65: primera columna Bransby-Williams, segunda Témez; ver `casos/OBRA_TU107/fuente/pdf65.png`); se usó la del PDF.

### 4.3 Dale Boulevard (FHWA-RD-01-095) — solo cualitativo

`casos/OBRA_DALE`. Dos tubos en serie con entrada acampanada a 45°: fuera de HDS-5 y de la app. Modelado como un solo tubo de 9.5 ft (2.896 m) con borde cuadrado: la app lo descarta (D > 2.70 m, tope de AASHTO M 170M, V9; y V3). HW de entrada del escalón: 14.21 ft a 1000 cfs y 24.11 ft a 1500 cfs, frente a 12.23 y 18.40 ft medidos en el modelo (+16 %, +31 %): **(c)** configuración (la entrada acampanada es más eficiente que el borde cuadrado). TW por `cota_TW`: 7.88 ft, igual al publicado.

## 5. Ventana real (gui.app bajo xvfb)

Conductor: `scripts/gui_validacion.py` (imita `tests/apoyo/gui_ui4_recorrido_real.py`). Por caso: «Examinar…» de la pestaña 1 para CSV, datos externos, datos de sitio, CSV de cuencas y CSV de la estación; alcance perfil; los criterios tecleados en la pestaña 2 y «Aplicar solo a esta corrida» (ninguno pidió nota); EJECUTAR; lectura de la pestaña 3 (filas y detalle de puntos); «Exportar JSON» y «Guardar sesion». Salidas en `gui/<caso>/`.

| Caso | Puntos | JSON ventana = JSON CLI (sin la hora) | Diferencias | Detalle de la pestaña 3 | `cli.py --sesion <sesión de la ventana>` |
|---|---|---|---|---|---|
| TDOT Ej. 2 (base) | 10 | sí | 0 | contiene todas las líneas de la CLI (Q25p0cfs, Q02p5cfs; espacios normalizados, sin las reglas «----») | REPRODUCE |
| Hidrología UPAO/UNC (TR 100/50) | 7 | sí | 0 | ídem (TINAS detenida, TINAS-T-DIAG, UNC-A1) | REPRODUCE |
| WisDOT D = 2.5 ft (C3, C4, C9) | 6 | sí | 0 | ídem (WI-C9-Qd, WI-C3-Qd) | (no corrido) |

La comparación es directa sobre el diccionario completo (rutas incluidas), y además con `src/comparador.py`: «IGUALES». Diálogos: solo los de información («JSON exportado», «Sesion guardada»); ningún error.

## 6. Lo que la app no pudo correr, y por qué (todo correcto según su norma)

- **Tinas (UPAO), 55.9 km²**, y **5 cuencas de TU-107** de 12 a 103 km²: `MetodoNoEvaluableError`, racional solo para A < 10 km² (núm. 3.12.2); el racional modificado no está implementado (ficha T1-08).
- **C-20 y C-27 de TU-107**: Témez fuera de 0.25–24 h → `MetodoNoEvaluableError` que sugiere otro método de Tc o el caudal declarado.
- **TDOT con la rasante publicada**: el 36 in no pasa V7 (10/10) ni V4 (8/10) (criterios MTC); después la corrida se detiene pidiendo la fila de espesor de 1070 mm, efecto de D1.
- **6 escalones de WisDOT**: sin tirante normal con n = 0.013 → descartados sin HW.
- **TDOT Ej. 4 y UPAO-Manning**: no factibles por V3 (velocidad máxima de la Tabla N° 10 con n_min) — el diseño de la app elige otro material o se declara no factible.
- **No corridos**: MnDOT 2021-29 (cajones multicelda sin HW, cotas ni TW publicados), TU-107-05 (solo capacidad a sección llena, sin HW/ke/L/TW; además el buscador halló que las capacidades de los marcos no salen de su propio Manning), Querari (puente con Mac-Math; serie de 45–185 mm frente a P24(T=2) = 36 mm: fuente inconsistente).

## 7. Defectos candidatos (clasificación (a))

### D1 — La progresión de diámetros declarada se redondea a 2 decimales y después se rechaza a sí misma (severidad media)

- **Dónde**: `/home/user/val_web/src/modulos/M2_material.py:973` — `siguiente = round(inicio + (n + 1) * paso, 2)` —, y la guardia de las líneas 964–970, que rechaza el escalón siguiente por no pertenecer a la progresión.
- **Qué pasa**: `diametros_normalizados = {"inicio": 0.9144, "paso": 0.1524}` (la serie de 6 in que la propia ficha del criterio cita como la serie real) pasa la puerta del criterio; el 2.º escalón sale **1.07 m** y no 1.0668 m, y pide la fila de espesor **1070** mm aunque la declarada sea 1067; el 3.º levanta `DatoInvalidoError: no pertenece a la progresion de 0.9144 m + 0.1524 m … (valor leido: 1.07)`, los tres materiales salen «no evaluable» y el punto termina en `DisenoNoFactibleError` aunque un diámetro mayor cumpliría. Con la progresión de archivo (0.90/0.15) no se dispara.
- **Reproducción mínima** (`defectos/D1_progresion_redondeo/`):
  - CLI: un punto con Q = 2.0 m³/s y S = 0.005 (`puntos.csv`, `externos.json`, `decl.txt`) → iteraciones Ø 0.91 m, Ø 1.07 m y luego `DisenoNoFactibleError … material no evaluable: DatoInvalidoError: Dato invalido en 'D' …`.
  - En proceso (`repro_minima.py`, desde `/home/user/val_web`): `D1 = 0.9144  D2 = 1.07 (esperado 1.0668)` y `D3 -> DatoInvalidoError`.
  - Se ve también en la corrida real de TDOT con la rasante publicada (`casos/TDOT_EX2/publicada`): el 914 no pasa V7 y el siguiente escalón se detiene pidiendo la fila 1070.

### D2 — V7 (flotación) no lee `NF_profundidad_m`, y el contrato de entradas dice que sí (severidad baja; del lado seguro)

- **Dónde**: `/home/user/val_web/docs/contrato_entradas.md:71` («La lee V7 (flotación)… Puede ir vacía; V7 queda pendiente de ese dato») frente a `src/modulos/M5_verificaciones.py:3058` (`U = empuje_flotacion_kn_m(seccion=seccion, espesor=t)`, sin NF) y `src/modulos/M8_estructural.py:304` (conducto totalmente sumergido, «NF en su cota más alta»). El texto de ayuda del pre-vuelo dice lo mismo que el contrato («para la flotación (V7)»), aunque el propio pre-vuelo reconoce que ningún módulo de perfil consume el dato.
- **Qué pasa**: sin NF, V7 no queda pendiente: se evalúa con el conducto sumergido y puede descartar diámetros; con un NF medido profundo, el resultado no cambia.
- **Reproducción mínima** (`defectos/O2_NF_y_V7/`): el mismo punto de TDOT (36 in, rasante publicada) sin NF y con `NF_profundidad_m = 10.0` da el mismo V7: «obtenido 1.2745 frente a 9.6235» (U = 9.623 kN/m) y el mismo descarte.
- El cálculo es conservador y está declarado en el código; lo que no cuadra es la documentación con el código. Cualquiera de las dos se puede corregir, pero hoy dicen cosas distintas.

## 8. Observaciones (no son defectos)

1. **El n del concreto no es declarable** (es [N]: 0.010–0.013 de la Tabla N° 09). Frente a fuentes con n = 0.012, el tirante normal sale 5–8 % mayor y algunos escalones quedan sin tirante normal (WisDOT). Es la norma que la app sigue.
2. **La velocidad de salida que la app publica y entrega a la protección** es la de n_min sobre la geometría de n_max (×1.30 respecto de n = 0.013), emparejada en la línea «V_salida = … (y_salida = …)» con el tirante de n_max. Está documentado (`modelos.TiranteNormal`: «V_erosion · A ≠ Q en general») y la Fase 6 usa A = Q/V, coherente con V; quien compare con HY-8 debe leer V_sedimentación.
3. **Las dos relaciones intensidad–duración del Manual** (Dick-Peschke y Tabla N° 04) dan intensidades muy distintas en duraciones cortas (×1.5 a ×2.4 en TU-107). La elección es el criterio `relacion_intensidad_duracion`; la Tabla N° 04 no se evalúa bajo 1 h.
4. **El factor 1.13** de intervalo fijo, que usan las dos tesis peruanas, no está en el Manual del MTC y la app no lo aplica (−11.5 % en P24).
5. **Sin control de plausibilidad de la serie**: la app ajusta 729 mm/24 h y filas repetidas sin avisar (no hay umbral normativo).
6. Errores en el material de entrada de esta validación, no en la app: en `obras.json`, columnas de Tc de TU-107 invertidas (§4.2); en `ejemplos.json`, el HW de TDOT Ej. 2 viene en cota y en profundidad (se usó la profundidad, «HW inlet control depth»).

## 9. Archivos

- `INFORME.md` (este), `resultados.json` (meta, casos, 371 filas de contraste, invariancia, ventana real, defectos), `tabla_contraste.md` (las 371 filas con el recálculo a mano), `tabla_ex2.md`, `tabla_wisdot.md`, `COMANDOS.md`, `recalculo_mano.json`, `invariancia.json`, `resultados_filas.json`.
- `casos/<caso>/{base,alt,…}/`: entradas rotuladas (`puntos.csv`, `externos.json`, `sitio.json`, `cuencas.csv`, `estacion.csv`, `declaraciones*.txt`) y `salida/` (texto de la CLI, `*.informe.json`, `memoria*.html`, `prevuelo.txt`); `casos/OBRA_WISDOT/contraste.json`, `casos/OBRA_TU107/contraste.json`.
- `gui/<caso>/`: `recorrido_ventana.json`, `ventana.informe.json`, `ventana.sesion.json`, y la corrida `--sesion`.
- `defectos/D1_progresion_redondeo/`, `defectos/O2_NF_y_V7/`: reproducciones mínimas.
- `scripts/`: constructores de entradas (`arma_*.py`), `correr.py` (deja el comando exacto en `comandos.txt`), recálculo a mano (`recalculo_mano.py`, `hds5_mano.py`), comparadores, conductor de la ventana y generadores de tablas.
