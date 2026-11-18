# Hidrología: casos reales publicados contra `MH_hidrologia.py`

Dossier de verificación independiente, 2026-11-18. No se modificó ningún repositorio ni se hizo commit.

- **Qué se verifica:** `/home/user/Proyecto_alcantarillas/src/modulos/MH_hidrologia.py` (Fase 1-bis).
- **Fuente normativa:** Manual de Hidrología, Hidráulica y Drenaje (MTC), `/home/user/Normas/normas/Hidrología, Hidráulica y Drenaje (Versión Libro).pdf`.
- **Casos:** `/home/user/Normas/ejemplos_resueltos/casos_reales/` (seis documentos).
- **Datos y cálculo:** `/tmp/claude-0/-home-user-Proyecto-alcantarillas/4ee726ed-9c15-53e3-939e-198cb9226506/scratchpad/verif/hidrologia_casos/`

Convención de páginas: «PDF n» es la página del archivo; «imp. m» la impresa.

---

## 0. Resumen ejecutivo

**El programa reproduce el cálculo a mano en todo lo comparado.** Sobre 6 casos, 10 series reales y 73 cuencas, la peor diferencia relativa entre `MH_hidrologia` y mi cálculo independiente es 9.7·10⁻¹⁶. Las 11 detenciones esperadas salieron con la excepción esperada. No encontré ningún defecto numérico en MH.

**Cuatro documentos sirven de oráculo numérico de terceros** para piezas concretas del módulo: el estadístico K-S de la ecuación (13), los tres estimadores (Normal, Log Normal 2P, Gumbel por momentos), Dick-Peschke y Témez. Ninguno sirve de oráculo del caudal: todos usan otro método, otra relación intensidad-duración o un coeficiente que la Tabla N.º 08 no puede dar.

| Caso | Clasificación | Qué valida con número de terceros | Qué NO valida | Tolerancia propuesta contra lo publicado |
|---|---|---|---|---|
| **INDECI Piura** (Miraflores 1971-2008) | **Oráculo numérico** + contraste del criterio FEN | P24(TR) Normal, LN y Gumbel por momentos, con y sin FEN (58 celdas); Δ de K-S (6 valores) | Caudal (no trae L ni S) | P24: ±0.1 %. Δ: ±0.0005 |
| **UNTumbes TU-107** (Cañaveral) | **Adversarial** (+ oráculo de estadística) | Media, s, parámetros LN; Δ de Normal, LN2 y Gumbel a 4 decimales; P24 LN2; Témez en 41 cuencas | Caudal (IDF propia); la serie misma es inverosímil | P24: ±0.05 %. Δ: ±0.00005. Tc: ±0.007 h |
| **UNSAAC Roquepata** (Colquepata) | **Oráculo numérico** (piezas) + contraste de método (caudal) | Gumbel por momentos (10 TR); Dick-Peschke (48 celdas); Témez (15 cuencas) | Caudal (tc promediado, IDF de regresión) | P24: ±0.01 %. I: ±0.02 mm/h. tc: ±0.005 min |
| **UPAO La Jalca** (Chachapoyas) | **Oráculo numérico** (estadística) + contraste de método (caudal) | Serie A: Δ y P24 de Normal, LN y Gumbel. Serie B: Gumbel por momentos | Caudal (IDF extrapolada bajo 1 h) | Δ: ±0.00005. P24: ±0.02 mm |
| **UPeU Colpahuayco** (Sicuani) | **Contraste de método** | K a 2 decimales; I de la ec. (34) dentro de ±1.6 % | P24 (elige Pearson III); C (sale de un CN no publicado); Q | K: ±0.006. I: no es oráculo |
| **ESPOL Intervalles** (4 series INAMHI) | **Descartable para caudal**; contraste de método de K-S | Dmax de Normal y Gumbel en 3 de 4 estaciones | Hidrología (norma ecuatoriana). El cajón con HY-8 no es de MH | Dmax: ±0.0001 (3 estaciones) |

**Tres cosas que conviene saber antes de leer el resto:**

1. **Los años «duplicados» de Tumbes no se pueden detectar con la entrada que el programa pide.** Son filas mensuales copiadas con otra etiqueta de año (2001 = 1996, 2002 = 1989). El programa recibe sólo el máximo anual, y dos máximos iguales son normales: ocurren en 8 de las 10 series reales que revisé. Recomiendo un aviso sin umbral, no una excepción ni una deduplicación (§3.4).
2. **El programa entrega caudal a partir de la serie de Tumbes.** Con `serie_completa` da P24(70) = 930 mm e intensidades de hasta 812 mm/h, sin detenerse. Avisa (consistencia sin umbral, años faltantes), pero no juzga. Es coherente con la regla de no inventar umbrales; lo dejo como hallazgo (§8, H3).
3. **El caudal de MH será del orden del doble que el de las tesis peruanas cuando tc < 1 h.** Tumbes y UPAO construyen su IDF con los coeficientes de la Tabla N.º 04 (válidos desde 1 h) y la extrapolan a minutos. MH usa Dick-Peschke, que es lo que el Manual manda bajo 1 h. No es un defecto de MH, y el criterio ya lo declara; es lo primero que verá un revisor (§8, H5).

---

## 1. Método de esta verificación

### 1.1 Orden de trabajo y congelado

1. Leí el docstring y las funciones públicas de MH, `docs/contrato_entradas.md` §2-bis y los fixtures sintéticos. Corrí `cli.py --help` y nada más.
2. Leí en el Manual las fórmulas que MH implementa y las transcribí yo (§1.2).
3. Escribí el cálculo a mano en `hidrologia_casos/_calculo/calculo_a_mano.py`. Sólo usa `math`, `statistics` y `scipy.stats` (cuantil normal y cuantil exacto de K-S). No importa `src/`.
4. Congelé el cálculo y las entradas con sha1 **antes** de correr el programa: `hidrologia_casos/_calculo/SHA1SUMS_congelado.txt`, sellado 2026-11-18T03:41:05Z.
5. Después corrí MH sobre los casos (`comparar_con_programa.py`) y comparé. Está en la §9, aparte.

sha1 del sello: `5278e20ca13469cfd3431fb7a00da1f8c60247e9`. Los principales:

| Archivo | sha1 |
|---|---|
| `_calculo/calculo_a_mano.py` | `361844c27679b4cc76312df4dfd6ac1c88d58b7c` |
| `_calculo/datos_publicados.py` | `671e87ba24a64b9fff8be3722fa0a6b173310536` |
| `_calculo/resultados_a_mano.txt` | `864190e8952dc6541d86174da93dc4bde609a4aa` |
| `_calculo/resultados_a_mano.json` | `06059a4c098a99ab466fb2532ffdf7e7890dc9cc` |

`comparar_con_programa.py` se escribió después del sello y no forma parte de él.

### 1.2 Las fórmulas, leídas en el Manual

| Pieza | Numeral y página impresa | Texto o fórmula literal |
|---|---|---|
| Gumbel por momentos | 3.7.1.7, imp. 29 | «α = 1.2825 / σ», «β = µ − 0.45σ», F(x) = e^(−e^(−α(x−β))) (9) |
| K-S | 3.7.2 b), imp. 32 | «D = máx / Fo(xm) – F(xm)/»; «Fo(xm) = 1- m / (n+1) (13)»; «m es el número de orden de dato xm en una lista de mayor a menor»; «Si D<d, se acepta la hipótesis nula» |
| Valores críticos | Tabla N.º 03, imp. 32-33 | α = 0.05: n = 5 → 0.56; 10 → 0.41; 15 → 0.34; 20 → 0.29; 25 → 0.26; 30 → 0.24; 35 → 0.22; 40 → 0.21 |
| Años FEN | 3.4, imp. 22 | «dicha información deberá incluir los años en que se han registrado los eventos del fenómeno “El Niño”» |
| Dick-Peschke | 3.8.1, imp. 37 | «Para el caso de duraciones de tormenta menores a 1 hora […] Pd = P24h (d/1440)^0.25 (16)», d en minutos |
| Tabla N.º 04 | 3.8.1, imp. 36-37 | Coeficientes de 1 h (0.25) a 48 h (1.32); «podrán usarse, con criterio y cautela» |
| Racional | 3.12.2, imp. 49 | «Q = 0,278 CIA (28)»; «Muy usado para cuencas, A<10 Km2» |
| Racional modificado | 3.12.2.1, imp. 50-52 | «áreas menores de 770 km2 y con tiempos de concentración (Tc) de entre 0.25 y 24 horas»; Q = 0,278 CIAK (29); Tc = 0.3(L/S^0.25)^0.76 (30); K (31); KA = 1 – (log10 A/15) (32); P = kA·Pd (33); I (34); C (35) |

La desviación estándar es la muestral (n − 1) en todo el cálculo.

### 1.3 Qué significa cada clasificación

- **Oráculo numérico:** un tercero publicó el número y sale del mismo método que MH implementa. Una discrepancia sería un defecto de MH o una errata demostrable del documento.
- **Contraste de método:** el documento usa otro método u otra edición. La diferencia se mide y se explica; no acusa a nadie.
- **Adversarial:** el valor del caso es comprobar qué hace el programa con una entrada defectuosa.
- **Descartable:** no aporta a MH.

### 1.4 Lo que ningún caso publica: los «vehículos»

El CSV de cuencas exige `cobertura`, `suelo` y `S_terreno`. **Ningún documento los publica.** Todos dan un C directo. Para poder cargar las cuencas puse una fila de la Tabla N.º 08 que lee el mismo C que el documento declara, y lo rotulé en cada archivo como «VEHÍCULO DEL VERIFICADOR, no dato del caso». Donde la Tabla no puede dar el C del documento (UPeU: 0.22 a 0.32) lo digo y el caudal no se compara.

Lo mismo con la columna `fen`: sólo INDECI nombra sus años FEN. En los demás «no» es declaración mía para que el archivo cargue, y está rotulada.

**No preparé CSV de puntos.** Sus columnas (cotas, CBR, SUCS, etc.) no están en ningún documento y habría que inventarlas. La hidrología se prueba llamando a `MH.cargar_entrada`, `MH.precipitacion_de_diseno(serie, TR)` y `MH.caudal_de_diseno(cuenca, serie, TR)`, que es lo que hace `comparar_con_programa.py`.

---

## 2. Caso 1 — INDECI-OEA, «Mapa de peligros de la ciudad de Piura» (2009)

Archivos: `indeci_piura/mapa_peligros_vol1.pdf` y `mapa_peligros_vol2_anexos.pdf`. En el Vol. I la página impresa es la del PDF menos 16. El Vol. II no lleva número de página impreso en los anexos; cito la del PDF.

**Clasificación: oráculo numérico.** Es el mejor caso del conjunto.

### 2.1 Qué publica

| Dato | Dónde | Valor |
|---|---|---|
| Serie P24 máx, Miraflores 1971-2008 (38 años) | Vol. I, Cuadro N.º 13, PDF 105 (imp. 89), columna ANUAL. Repetida en Vol. II, Anexo 07.2, PDF 346 | 1.6 a 173.6 mm |
| Fuente de la serie | Ídem, pie del cuadro | «División de Hidrometeorología – Proyecto Especial Chira-Piura» |
| Serie «sin FEN», 32 años | Vol. II, Anexo 07.1, PDF 338 | Quita 1972, 1973, 1983, 1987, 1992 y 1998 |
| Serie «sólo FEN», 5 datos | Vol. II, Anexo 07.3, PDF 354 | 1972, 1983, 1987, 1992, 1998 |
| Estadísticos sin FEN | Vol. II PDF 338 | μ = 18.6; σ = 21.66; log10: 1.037 y 0.467; n = 32 |
| Estadísticos con FEN | Vol. II PDF 346 | μ = 30.5; σ = 40.68; log10: 1.170 y 0.542; n = 38 |
| P24(TR), cinco distribuciones, TR 2 a 1000 | Vol. II PDF 338-339 y 346-347; Vol. I Cuadros 21 y 22, PDF 127-128 (imp. 111-112) | Ver §2.2 |
| Δc de K-S | Vol. I Cuadros 21 y 22 | Sin FEN (Δ tab 0.24): Normal 0.236, LN 0.080, LP3 0.223, Gumbel 0.220, Gumbel mod. 0.184. Con FEN (0.22): 0.245, 0.059, 0.102, 0.254, 0.222 |
| Decisión FEN | Vol. I PDF 133 (imp. 117) | «tomando un criterio conservador y márgenes de seguridad, se optará por considerar los resultados obtenidos, de la serie de precipitación 1971-2008 considerando los Fenómenos El Niño» |
| Intensidad | Vol. I Cuadro 27, PDF 134 (imp. 118) | P24 / 6 h: 131.82 / 6 = 21.97 mm/h |
| Subcuencas urbanas | Vol. I Cuadro 36, PDF 172-173 | A, CN, Pe, C, i = 22 mm/h fijo. **Sin L ni S** |

No publica tiempo de concentración ni cuencas con longitud y pendiente. El caso termina en la P24 de diseño.

### 2.2 Recálculo a mano

Con la serie completa (n = 38): media 30.4947, s = 40.6828; ln: Y = 2.6952, Sy = 1.2485 (log10: 1.1705 y 0.5422). Gumbel: α = 1.2825/40.6828 = 0.03152; β = 30.4947 − 0.45·40.6828 = 12.1875.

Ejemplo, LN a 25 años: z = 1.7507; P = exp(2.6952 + 1.7507·1.2485) = **131.76 mm** (impreso 131.82).

| Serie | Distribución | Mi P24(25) | Impreso | Dif. máx. en los 10 TR | Mi Δ (ec. 13) | Δc impreso |
|---|---|---|---|---|---|---|
| Con FEN | Normal | 101.72 | 101.73 | −0.02 % | 0.2447 | 0.245 |
| Con FEN | Log Normal | 131.76 | 131.82 | −0.05 % | 0.0591 | 0.059 |
| Con FEN | Gumbel momentos | 113.65 | 113.65 («Gumbel modificado») | +0.01 % | 0.2219 | 0.222 |
| Sin FEN | Normal | 56.55 | 56.56 | +0.02 % | 0.2361 | 0.236 |
| Sin FEN | Log Normal | 71.58 | 71.61 | −0.05 % | 0.0804 | 0.080 |
| Sin FEN | Gumbel momentos | 62.90 | 62.90 («Gumbel modificado») | +0.01 % | 0.1841 | 0.184 |

Los seis Δ coinciden a los tres decimales impresos. **El estudio calculó el K-S con la misma ecuación (13) del Manual.** Es el contraste más fuerte del dossier, porque el estadístico K-S es la pieza donde más varían los programas (§7).

El 0.05 % de la Log Normal sale de que el estudio usa z y los estadísticos en log10 a tres decimales.

Sólo FEN (5 datos): media 106.46, s = 57.76, log10 1.961 y 0.286. Coincide con lo impreso.

### 2.3 Contrastes de método (no de número)

1. **La columna «Gumbel» no es comparable.** Usa ȳN y σN de N = 20 (tabla A-8 de Ponce), aunque la serie tiene 32 o 38 años. Da 132.89 mm a 25 años frente a 113.65 por momentos (−14.5 %). La columna «Gumbel modificado» sí es la del Manual: su K_T (0.7195, 2.0439, 3.1368 para TR 5, 25, 100) es el de momentos (0.7195, 2.0440, 3.1369).
2. **Valor crítico.** El estudio usa 1.36/√n: 0.2404 (imprime 0.24) y 0.2206 (0.22). MH usa el cuantil exacto cuando n no es fila de la Tabla N.º 03: 0.2342 para n = 32 y 0.2154 para n = 38. Cambia un veredicto: la Normal sin FEN (0.2361) pasa con 0.24 y no pasa con 0.2342.
3. **Log Pearson III** no se compara: MH no la ajusta porque el Manual no imprime su estimador.

### 2.4 Erratas internas del documento

| N.º | Dónde | Errata |
|---|---|---|
| 1 | Cuadro 13, fila «Prom. S/Niños», columna ANUAL | Imprime 42.5. La media sin Niños es 18.6 (su propio Anexo 07.1) |
| 2 | Cuadro 13, fila «MAX S/Niños», columna ANUAL | Imprime 107.1, que es 1992, año que el mismo estudio trata como FEN. Debería ser 103.5 (2002) |
| 3 | Anexos 07.1 y 07.3 | 1973 sale de «sin FEN» y no entra en «sólo FEN»: queda fuera de las dos poblaciones (el estudio escribe «72/73» como un evento) |
| 4 | Cuadro 22 | Normal (0.245), Gumbel (0.254) y Gumbel modificado (0.222) superan el Δ tabular 0.22 y el texto no lo comenta |
| 5 | Vol. I PDF 125 (imp. 109), ítem e) | Repite «sin considerar los fenómenos El Niño»; por el Anexo 07.5 es «considerando» |
| 6 | Figura 26, PDF 133 | Eje rotulado «Caudal m3/s» sobre curvas de precipitación |
| 7 | Cuadro 13, 1971 | Año parcial: sólo trae abril a diciembre (máximo 1.6 mm). Entra en las dos series |
| 8 | Serie «sin FEN» | Conserva 1997 (54.0 mm, en diciembre, inicio del FEN 97-98) y 2002 (103.5 mm) |

Ninguna afecta a los números que se usan de oráculo.

### 2.5 Entradas y salida esperada

- `hidrologia_casos/indeci_piura/estacion.csv`: 38 años, `fen = si` en los seis años que quita el Anexo 07.1. Es la declaración **del estudio**.
- `hidrologia_casos/indeci_piura/estacion_fen_5_sin_1973.csv`: variante con los cinco del Anexo 07.3.
- `hidrologia_casos/indeci_piura/salida_esperada.json`.

| Declaración | Esperado |
|---|---|
| `serie_completa`, `mejor_ajuste_ks` | `lognormal_2p`; Y = 2.6952, Sy = 1.2485; D = 0.0591; d = 0.2154. P24 = 131.76 (TR 25), 192.35 (50), 270.34 (100) |
| Ídem, TR 25 | Aviso: 131.8 mm queda bajo 151.4 mm (1983, T empírico 19.5 años). No detiene |
| `serie_sin_fen` | `MetodoNoEvaluableError`: 71.6 mm frente a 131.8 mm |
| `dos_poblaciones` | `MetodoNoEvaluableError` |
| Sin declarar `homogeneidad_serie_fen` | `CriterioPendienteError` |
| `serie_completa` + `normal` | `MetodoNoEvaluableError`: D = 0.2447 ≥ 0.2154 |
| `serie_completa` + `gumbel` | `MetodoNoEvaluableError`: D = 0.2219 ≥ 0.2154. Con α = 0.01 pasa (d = 0.2584) y da 113.65 mm |

**Tolerancias.** Programa contra cálculo a mano: 10⁻⁹ relativo (misma aritmética). Programa contra lo impreso: P24 ±0.1 % (el estudio redondea z y los logaritmos a 3 decimales; medido 0.05 %); Δ ±0.0005 (se imprime a 3 decimales).

### 2.6 El criterio `homogeneidad_serie_fen` contra un tercero

La regla de MH (detenerse si `serie_sin_fen` da menos lluvia) reproduce la decisión del estudio, que tomó la serie con FEN «por criterio conservador». La razón entre las dos lluvias es 1.84 a 25 años y 2.03 a 100.

La declaración de qué años son FEN mueve mucho la lluvia sin FEN, pero no la adoptada:

| Años marcados FEN | n sin FEN | LN P24(25) sin FEN | LN P24(100) sin FEN |
|---|---|---|---|
| Los 6 del estudio | 32 | 71.6 | 132.9 |
| Los 5 del Anexo 07.3 (1973 se queda) | 33 | 73.5 | 136.4 |
| Los 6 + 1997 | 31 | 65.3 | 119.6 |
| Los 6 + 1997 + 2002 | 30 | 53.1 | 93.1 |

En las cuatro, `serie_sin_fen` se detiene y `serie_completa` da los mismos 131.8 mm. Quitar 1971 (año parcial) baja la P24(25) de la serie completa a 130.5 mm (−1 %).

---

## 3. Caso 2 — UNTumbes, TU-107 Bocapán–Tamarindo (Ramos Estrada, 2025)

Archivo: `untumbes_tu107/tesis.pdf`. La página impresa coincide con la del PDF.

**Clasificación: adversarial.** Su estadística es además un oráculo numérico exacto.

### 3.1 Qué publica

| Dato | Dónde | Valor |
|---|---|---|
| Estación Cañaveral, 40 años (1983-87, 1989-2021, 2023-24) | Tabla 22, p. 60 | 133 msnm; «información que fue extraída del portal SENAMHI» |
| Máximos mensuales y anual | Tabla 23, p. 60 | 19.0 a 729.2 mm |
| Serie anual | Tabla 24, p. 61 | Suma 7546.90 |
| Estadísticos | Tabla 25, p. 62; Tablas 28 y 29, p. 66-67 | Media 188.673; s = 169.556; ln: 4.8750 y 0.8955 |
| Δ de K-S, 8 distribuciones | Tabla 36, p. 74 | Normal 0.1618; **LN2 0.0535 (elegida)**; Gumbel 0.1074; Δ tab 0.2150 = «1.36/√N» |
| P24(TR), LN2 con HidroEsta | Tabla 47, p. 80 | 278.23 (5), 628.29 (25), 930.62 (70), 1052.08 (100), 1724.28 (500); después × 1.13 |
| 41 cuencas: A, perímetro, L, cotas, S | Tabla 26, p. 64 | 0.10 a 102.71 km² |
| tc por Bransby-Williams, Témez y promedio | Tabla 27, p. 65 | 0.19 a 7.67 h |
| IDF | p. 87 | I = 408.8108·T^0.3910 / t^0.5375 |
| TR | Tabla 64, p. 89 | 35, 70 y 140 años |
| Q racional, 36 cuencas; C = 0.10, 0.15 o 0.20 | Tabla 66, p. 92 | «Q = C·I·A / 3.6» |
| Q por hidrograma triangular, 5 cuencas ≥ 10 km², con CN | Tabla 67, p. 93 | CN 62 o 70; Sapotal Q70 = 1827.93 m³/s |

### 3.2 Recálculo a mano

| Magnitud | Mi cálculo | Impreso |
|---|---|---|
| Media / s | 188.6725 / 169.5565 | 188.673 / 169.556 |
| Y / Sy (ln) | 4.8750 / 0.8955 | 4.8750 / 0.8955 |
| Δ Normal | 0.1618 | 0.1618 |
| Δ LN2 | 0.0535 | 0.0535 |
| Δ Gumbel (momentos) | 0.1074 | 0.1074 |
| LN2 P24(5) | 278.28 | 278.23 |
| LN2 P24(70) | 930.25 | 930.62 |
| LN2 P24(500) | 1723.75 | 1724.28 |

Los tres Δ coinciden a 4 decimales: la tesis usa la posición de Weibull, que es la ecuación (13). La P24 difiere 0.04 % como máximo (redondeo de z en HidroEsta).

**Témez en las 41 cuencas.** Con S = (cota máx − cota mín)/L el desvío máximo contra la columna TÉMEZ de la Tabla 27 es 0.007 h. Con la S de la Tabla 26, impresa a 2 decimales, no se reproduce (C-6: 7.034 h frente a 7.17 impreso; con las cotas, 7.176). Por eso el CSV lleva la pendiente derivada de las cotas a 4 decimales.

**El caudal del documento se reproduce con su propio método.** C-1: I35 = 408.8108·35^0.391 / 26.81^0.5375 = 280.25 mm/h (impreso 280.28); Q = 0.15·280.28·0.25/3.6 = 2.92 m³/s (impreso 2.86: usa el área sin redondear, 0.245 km²).

### 3.3 Defectos de la serie

| N.º | Defecto | Evidencia |
|---|---|---|
| 1 | **Filas copiadas.** 2002 = 1989 en los 12 meses. 2001 = 1996 en 11 de 12 (mayo: 11.00 frente a 11.10) | Tabla 23, p. 60 |
| 2 | **Magnitudes inverosímiles para 24 h.** 14 celdas mensuales de 300 mm o más: 1983 (491, 337, 375), 1987 (360, 322), 1991 (717), 1992 (306.3), 1997 (502.3, 729.2, 447.6, 427.4), 2000, 2017, 2023 | Tabla 23. Como referencia, el máximo de Miraflores en 38 años es 173.6 mm, e INDECI cita 203 mm en Chulucanas como valor extremo de 1998 (Vol. I PDF 125, imp. 109) |
| 3 | **El evento de 1998 aparece en 1997.** «1997» trae 502 a 729 mm de enero a abril y «1998» sólo 150 mm. En Miraflores el máximo de 1997 es de diciembre (54.0 mm) y el de 1998 es de enero (173.6 mm) | Tabla 23 frente al Cuadro 13 de INDECI |
| 4 | **No menciona El Niño**, con 1983 y 1997-98 en la serie | Texto completo |
| 5 | Faltan 1988 y 2022 | Tabla 22 |
| 6 | Promedia Témez con Bransby-Williams y usa Témez con Tc bajo 0.25 h (C-20: 0.20 h; C-27: 0.25 h impreso, 0.246 h recalculado) | Tabla 27 |
| 7 | IDF ajustada a los coeficientes de la Tabla N.º 04 (1 a 24 h) y aplicada a duraciones de 11 a 60 min | Tabla 48, p. 80; Tabla 65, p. 90 |

Los defectos 2 y 3 son compatibles con que la columna contenga totales mensuales y con un corrimiento de año. **Es una hipótesis: el documento no permite demostrarla.** Lo que sí está demostrado es que el resultado es físicamente absurdo: I de 364 mm/h en la tesis y P24(100) de 1052 mm.

### 3.4 ¿Qué debe hacer un programa correcto con los años duplicados?

**Recomendación: avisar, sin umbral. No detenerse y no deduplicar.**

Hay que separar dos cosas que se llaman igual:

- **La misma etiqueta de año dos veces** (dos filas «2001»). El programa ya se detiene con `DatoInvalidoError` («el año esta dos veces en la serie […]: un maximo anual por año»). Lo comprobé. Es correcto: el dato está y contradice a otro, y el revisor tiene que corregir.
- **Dos años distintos con el mismo contenido** (el caso de Tumbes). Aquí no.

Razones para no detenerse:

1. **Con la entrada que el contrato pide, la copia no es demostrable.** El programa recibe `anio, p24_mm`. La prueba de la copia está en los 12 valores mensuales de la Tabla 23, que no entran. En la serie anual sólo se ve que 129.0 y 63.0 aparecen dos veces.
2. **Dos máximos anuales iguales son normales.** Los medí en las 10 series reales de este dossier:

| Serie | n | Valores repetidos |
|---|---|---|
| Miraflores | 38 | 3 (2.4, 13.0, 16.0) |
| Sicuani | 28 | 4 (30.4, 28.8, 25.8, 34.1) |
| Cañaveral | 40 | 2 (129.0 y 63.0: las copias) |
| Colquepata | 25 | 2 |
| La Argelia | 50 | 2 (uno, tres veces) |
| Gonzanamá | 48 | 1 |
| Malacatos | 49 | 3 |
| Catamayo | 29 | 2 |
| Chachapoyas A y B | 17 | 0 |

   Una excepción por valor repetido detendría 8 de 10 series reales, 7 de ellas sin defecto. Cañaveral no se distingue de las demás por este indicador.
3. **Ninguna excepción de la taxonomía encaja.** No falta nada (`DatoFaltanteError`), no hay criterio vacío, la aritmética cabe, y el método está definido. `DatoInvalidoError` es la única candidata y exige que el dato «contradiga a otro»: dos años con 129.0 mm no se contradicen.

Razones para no deduplicar:

4. **El módulo valida y no corrige** («La cuenca, la serie y los años FEN […] se validan y no se corrigen», docstring de MH). Quitar filas es corregir.
5. **No se sabe cuál es la copia**, y la elección mueve el resultado. Quitar 2001 y 2002 sube la LN2 un 5.1 % a 35 años, 5.6 % a 70 y 6.0 % a 140 (P70: 930.2 → 982.0 mm).

Lo que propongo:

- **Un renglón más en el aviso de consistencia sin umbral que ya existe** (paso 1b.3c, `_paso_consistencia`): la lista de máximos anuales repetidos con sus años («129.0 mm: 1989 y 2002; 63.0 mm: 1996 y 2001»), con el texto de que el programa no distingue una coincidencia de una copia y de que el proyectista debe contrastar esos años con el registro mensual o diario de origen. No lleva número de corte, así que no inventa nada.
- **Es comportamiento nuevo.** Por la regla de `CLAUDE.md` va como entrada a la hoja de ruta y no se rellena en silencio.
- Si algún día el contrato admitiera la serie mensual, una fila idéntica mes a mes a la de otro año sí sería `DatoInvalidoError`, con el par de años en el mensaje. Hoy no aplica.

### 3.5 Entradas y salida esperada

- `hidrologia_casos/untumbes_tu107/estacion_como_se_publica_fen_vacio.csv`: la columna `fen` vacía, que es lo que la tesis declara. **Esperado: `DatoFaltanteError('fen')` al cargar.** Es la primera guardia y es la que de verdad protege aquí: obliga a que alguien declare los años FEN antes de calcular.
- `hidrologia_casos/untumbes_tu107/estacion_fen_declarado_por_el_verificador.csv`: `fen = si` en 1983, 1987, 1992 y 1998, los años que INDECI nombra para Piura dentro del periodo. Es declaración mía, rotulada. Nótese que el máximo de la serie (729.2 mm) está en «1997», que queda como «no».
- `hidrologia_casos/untumbes_tu107/cuencas.csv`: las 41 cuencas, `metodo_tc = temez`, CN sólo en las cinco de 10 km² o más.
- `hidrologia_casos/untumbes_tu107/salida_esperada.json`.

| Entrada | Esperado |
|---|---|
| `fen` vacío | `DatoFaltanteError`, campo `fen` |
| Serie completa, `mejor_ajuste_ks` | `lognormal_2p`; D = 0.0535; d = 0.21 (Tabla N.º 03, n = 40). P24 = 719.34 (TR 35), 930.25 (70), 1174.80 (140) |
| C-1 (0.25 km², C = 0.15), TR 35 | tc = 27.67 min; I = 580.8 mm/h; Q = 6.21 m³/s (tesis: 280.28 mm/h y 2.86 m³/s) |
| C-20 y C-27 | `MetodoNoEvaluableError`: Témez da 0.204 y 0.246 h, bajo 0.25 h |
| C-6 Sapotal (102.71 km², CN 62), TR 70 | Racional modificado: Tc = 7.176 h; K = 1.4562; KA = 0.8659; I = 98.5 mm/h; C = 0.916; Q = 3752 m³/s (tesis, hidrograma triangular: 1827.93) |
| Otras cuatro de ≥ 10 km², TR 70 | C-7: 734.3; C-13: 835.1; C-16: 1131.0; C-17: 771.5 m³/s (tesis: 345.23, 372.98, 534.64, 345.99) |

**Tolerancias.** Programa contra cálculo a mano: 10⁻⁹. Contra lo impreso: P24 LN2 ±0.05 %; Δ ±0.00005; Tc de Témez ±0.007 h. **El caudal no se compara con la tesis**: es otro método y la serie no es creíble.

---

## 4. Caso 3 — UNSAAC, camino vecinal Emp. CU112–Roquepata (2019)

Archivo: `unsaac_42tmc/tesis.pdf`. La página impresa es la del PDF menos 12.

**Clasificación: oráculo numérico** de tres piezas (Gumbel por momentos, Dick-Peschke, Témez) y **contraste de método** del caudal. Tiene un subcaso adversarial: Témez bajo 0.25 h.

### 4.1 Qué publica

| Dato | Dónde | Valor |
|---|---|---|
| Serie Colquepata 1990-2014 (25 años), SENAMHI | Tabla 6.6, PDF 101-102 (imp. 89-90) | Promedio 23.43; desv. estándar 13.11 |
| Gumbel por factor de frecuencia | Tabla 6.7, PDF 104 (imp. 92) | K y Pmax para 10 TR; TR 35: 2.3108 y 53.7268; TR 70: 2.8569 y 60.8874 |
| Dick-Peschke, I para d = 5 a 40 min | Tabla 6.8, PDF 106 (imp. 94) | TR 70, 20 min: 62.71 mm/h |
| 15 microcuencas: A, L, S (Taylor-Schwarz) | Tablas 6.4 y 6.5, PDF 98-100 (imp. 86-88) | 0.09 a 1.37 km²; S de 19 a 42 % |
| tc por Témez, Bransby-Williams y promedio | Tabla 6.5 | A1: 24.18, 20.85 y 22.51 min |
| IDF de regresión | Figura 6.6, PDF 107 (imp. 95) | I = 328.6439·T^0.0976 / D^0.75 |
| Q racional, C = 0.5 único | Tabla 6.13, PDF 111 (imp. 99) | A1: 5.12, 5.20 y 5.56 m³/s |

### 4.2 Recálculo a mano

**Gumbel por momentos.** Media 23.4280; s = 13.1119 (la impresa, 13.11, es la muestral; la poblacional sería 12.847). α = 0.09781; β = 17.5276. En los 10 TR la diferencia máxima con la Tabla 6.7 es 0.004 %. A 35 años: K = 2.3109, P = 53.729 mm.

**Dick-Peschke.** Recalculé las 48 celdas de la Tabla 6.8 con I = P24·(d/1440)^0.25/(d/60) y la P24 impresa a 2 decimales. Desvío máximo: 0.013 mm/h. Ejemplo: 60.89·(20/1440)^0.25/(20/60) = 62.71 mm/h.

**Témez.** Las 15 microcuencas coinciden a los 2 decimales impresos. A1: 0.3·(1.147/0.3663^0.25)^0.76 = 0.4030 h = 24.18 min.

**El caudal del documento** se reproduce con su método: A1, I35 = 328.6439·35^0.0976/22.51^0.75 = 44.99 mm/h; Q = 0.5·44.99·83.20/360 = 5.20 m³/s.

### 4.3 Contraste de método

| Punto | Documento | MH según el Manual |
|---|---|---|
| Distribución | «Gumbel» por HidroEsta (anexo no publicado) | Con la ec. (13): Normal D = 0.1721, Gumbel 0.2419, LN 0.2696. `mejor_ajuste_ks` elige **Normal** (48.37 mm a 35 años). La LN no pasa (d = 0.26) |
| tc | Promedio de Témez y Bransby-Williams | Témez solo |
| Rango de Témez | Lo usa en las 15 | **7 de 15 quedan bajo 0.25 h** (A8 a A13 y A15: 7.8 a 13.6 min): `MetodoNoEvaluableError` |
| Intensidad | IDF de regresión sobre Dick-Peschke | Dick-Peschke directo en tc |
| K | No | Sí, con Témez (`coeficiente_uniformidad_temez = aplicar`) |

Con `gumbel` declarado y C = 0.5, MH da en las 8 cuencas evaluables entre +6.0 % y +10.5 % sobre la tesis (A1: 5.68 frente a 5.20 m³/s a 35 años). La diferencia se reparte entre el tc más corto, el K (1.3 a 2.2 %) y el ajuste de la regresión.

Kirpich tampoco es salida por omisión: las 15 pendientes (19 a 42 %) están fuera de la población de 3 a 10 %.

### 4.4 Erratas internas

| N.º | Dónde | Errata |
|---|---|---|
| 1 | Tabla 6.7, título | Dice «distribución normal»; el contenido es Gumbel |
| 2 | Tabla 6.13, encabezado | «T= 35 AÑOS» dos veces; la tercera columna es 70 años (corresponde a I70) |
| 3 | PDF 100-101 | Dice 28 registros de 1990 a 2017; la serie de P24 llega a 2014 (25 años) |
| 4 | Serie | **Inhomogénea.** 1990-1997: 4.4 a 9.3 mm (media 6.54). 1998-2014: 20.1 a 48.2 mm (media 31.38). Un quiebre de ese tamaño apunta a un cambio de instrumento o de unidad, no al clima |
| 5 | PDF 103 | Afirma que el mejor ajuste es Gumbel; con el K-S del Manual es la Normal y el anexo no se publicó |

El defecto 4 importa: sólo con 1998-2014 (17 años) la Gumbel a 35 años baja de 53.73 a 47.19 mm. El aviso de consistencia de MH lo deja a la vista (mínimo 4.4, máximo 48.2) sin juzgarlo.

### 4.5 Entradas y salida esperada

- `hidrologia_casos/unsaac_42tmc/estacion.csv` y `cuencas.csv` (15 microcuencas; C = 0.50 por la fila vehículo pastos/semipermeable con S_terreno 0.30).
- `hidrologia_casos/unsaac_42tmc/salida_esperada.json`.

| Declaración | Esperado |
|---|---|
| `mejor_ajuste_ks` | `normal`; D = 0.1721; d = 0.26 (Tabla N.º 03, n = 25); P24(35) = 48.37; P24(70) = 52.13 |
| `gumbel` | P24(35) = 53.729; P24(70) = 60.890 |
| `lognormal_2p` | `MetodoNoEvaluableError`: D = 0.2696 ≥ 0.26 |
| `gumbel`, A1, TR 35 | tc = 24.178 min; I = 47.996 mm/h; K = 1.022; Q = 5.675 m³/s |
| A8, A9, A10, A11, A12, A13, A15 | `MetodoNoEvaluableError` (Témez bajo 0.25 h) |

**Tolerancias contra lo impreso.** Gumbel P24: ±0.01 %. Dick-Peschke: ±0.02 mm/h (la P24 de la tabla está a 2 decimales). Témez: ±0.005 min. Caudal: no se compara.

---

## 5. Caso 4 — UPAO, La Jalca–Nueva Esperanza (2016)

Archivo: `upao_la_jalca/tesis.pdf`. La página impresa es la del PDF menos 20.

**Clasificación: oráculo numérico** de la estadística y **contraste de método** del caudal. Subcaso adversarial: Kirpich fuera de su población.

### 5.1 Qué publica

Dos series de la misma estación, discordantes:

| Serie | Dónde | Años | Para qué la usa |
|---|---|---|---|
| A | Cuadro N.º 18, PDF 91-92 (imp. 71-72) | 1964-73 y 1995-2001 (17) | Cuadros 19 y 20: K-S y P24 |
| B | Tabla mensual y tabla Gumbel, PDF 113-114 (imp. 93-94) | 1965-73 y 2004-11 (17) | Curvas IDF y caudales |

| Dato | Dónde | Valor |
|---|---|---|
| Serie A: Δc y P24 por distribución | Cuadro N.º 19, PDF 93 (imp. 73) | Normal 0.1591; LN 0.1149; LP3 0.0932 (elegida); Gumbel 0.1032; Δt = 0.3298 |
| Serie B: Gumbel por momentos | PDF 114-115 (imp. 94-95) | x̄ = 36.81; s = 7.87; α = 6.14; u = 33.26; XT' de 2 a 500 años; después × 1.13 |
| IDF | PDF 124 (imp. 104) | I = 84.6176·T^0.1240 / t^0.54001 |
| Alcantarilla 19 | PDF 138-140 (imp. 118-120) | A = 1.25 km²; L = 2415.58 m; S = 0.211; tc = 14.27 min; I = 32.72327 mm/h; C = 0.35; TR 50; Q = 3.99 m³/s |

De las 46 alcantarillas sólo la 19 trae L y S.

### 5.2 Recálculo a mano

**Serie A.** Media 40.0765; s = 15.3262.

| Distribución | Mi Δ | Δc impreso | Mi P24 (10 / 50 / 100 / 175 / 500) | Impreso |
|---|---|---|---|---|
| Normal | 0.1591 | 0.1591 | 59.72 / 71.55 / 75.73 / 78.84 / 84.19 | 59.72 / 71.56 / 75.74 / 78.85 / 84.19 |
| Log Normal | 0.1149 | 0.1149 | 56.89 / 72.51 / 78.99 / 84.18 / 93.93 | 56.90 / 72.52 / 79.00 / 84.20 / 93.94 |
| Gumbel momentos | 0.1032 | 0.1032 | 60.07 / 79.81 / 88.15 / 94.87 / 107.43 | 60.07 / 79.81 / 88.15 / 94.86 / 107.43 |

Los tres Δ coinciden a 4 decimales y las 15 lluvias dentro de 0.02 mm. Es un segundo oráculo completo de estimadores y K-S, independiente del de Piura.

**Serie B.** Suma 625.7; suma de cuadrados 990.7; media 36.81; s = 7.87; 1/α = 6.136; β = 33.265. Las siete XT' coinciden dentro de 0.003 % (TR 50: 57.2053 frente a 57.2041).

### 5.3 Contraste de método

- **Elige Log Pearson III**, que MH no ajusta. Con `mejor_ajuste_ks` MH elige Gumbel en las dos series.
- **Valor crítico:** 1.36/√17 = 0.3298; el exacto es 0.3180.
- **Factor 1.13:** lo aplica; MH lo tiene como criterio `factor_intervalo_fijo_p24`, con 1.00 de archivo.
- **Intensidad.** La tesis ajusta su IDF a los coeficientes de la Tabla N.º 04 (1 a 24 h) y la evalúa en 14.27 min: 32.72 mm/h. Dick-Peschke en esa duración, con la misma serie y sin el 1.13, da 75.89 mm/h. **Razón: 2.3.** El Manual manda Dick-Peschke «para el caso de duraciones de tormenta menores a 1 hora» (núm. 3.8.1, imp. 37).

### 5.4 Erratas internas

| N.º | Dónde | Errata |
|---|---|---|
| 1 | Series A y B, 1973 | 25.5 mm en la A y 27.0 en la B. En la tabla mensual, 25.50 es junio y 27.00 es abril: el máximo es 27.0 |
| 2 | PDF 139 (imp. 119) | Escribe Kirpich con L^0.76. Con 0.76 da 13.20 min; los 14.27 impresos salen con 0.77, que es el exponente del Manual |
| 3 | PDF 115 (imp. 95), lluvia de 18 h, TR 25 | 47.21 mm; debería ser 0.90·59.76 = 53.79. Contamina la regresión de TR 25 (constante 140.18 con exponente −0.555, fuera de la secuencia) |
| 4 | PDF 90 (imp. 70) | Anuncia «tres estaciones» y registros «entre el año 1964 y 2003»; hay una estación y la serie acaba en 2001 |
| 5 | Alcantarilla 19 | Kirpich con S = 21.1 %, fuera de la población de 3 a 10 % |

### 5.5 Entradas y salida esperada

- `hidrologia_casos/upao_la_jalca/estacion.csv` (dos estaciones: «Chachapoyas-A» y «Chachapoyas-B»), `cuencas.csv` (ALC-19) y `salida_esperada.json`.

| Declaración | Esperado |
|---|---|
| Chachapoyas-A, `mejor_ajuste_ks` | `gumbel`; D = 0.1032; d = 0.3180; P24(50) = 79.809; P24(100) = 88.153 |
| Chachapoyas-B, `mejor_ajuste_ks` | `gumbel`; D = 0.1253; P24(50) = 57.205 |
| ALC-19, por omisión | `MetodoNoEvaluableError` (Kirpich fuera de 3-10 %) |
| ALC-19, con `tc_fuera_de_la_poblacion_del_metodo = indicador_con_aviso`, TR 50 | tc = 14.271 min; I = 75.886 mm/h; C = 0.35; Q = 9.230 m³/s (tesis: 3.99) |

**Tolerancias contra lo impreso.** Δ: ±0.00005. P24 de la serie A: ±0.02 mm. XT' de la serie B: ±0.005 %. Caudal: no se compara.

---

## 6. Caso 5 — UPeU, Colpahuayco–Langui (Huamán Guerra y Marrujo Carpio, 2023)

Archivo: `upeu_colpahuayco/doc.pdf`. La página impresa coincide con la del PDF.

**Clasificación: contraste de método.** Es el único que aplica el racional modificado de Témez con sus pasos, pero no sirve de oráculo: la P24 sale de Pearson III y el C de un CN que no imprime.

### 6.1 Qué publica

| Dato | Dónde | Valor |
|---|---|---|
| Serie Sicuani 1993-2020 (28 años), SENAMHI | Tabla 2, p. 13 | 20.0 a 44.4 mm |
| K-S | p. 19 | Pearson III, Δ = 0.0537 frente a 0.2570 |
| P24 Pearson III | Tabla 7, p. 19 | 34.83 (5), 40.59 (20), 42.62 (35), 43.85 (50), 44.98 (70), 46.15 (100) |
| 14 microcuencas: A, L, cotas, S de cuenca y s de cauce | Tabla 6, p. 18 | 0.09 a 29.94 km² |
| Racional modificado, TR 70: K, I, A (ha), C, Q | Tabla 8, p. 20 | 12 microcuencas |
| HEC-HMS en las microcuencas 7 y 14 | Tabla 8 | 15.10 y 8.00 m³/s |

No publica los parámetros del ajuste ni el CN.

### 6.2 Recálculo a mano

**Serie.** Media 30.2571; s = 5.7334. Normal D = 0.0831; LN 0.0546; Gumbel 0.0769. Las tres pasan. La LN queda a −0.5 % y −0.6 % de la Pearson III impresa a 35 y 70 años (42.40 y 44.73 frente a 42.62 y 44.98); la Gumbel, a +2.1 % y +3.7 %.

**Racional modificado con Pd = 44.98 mm.** Microcuenca 1: Tc = 0.3·(2.01/0.33^0.25)^0.76 = 0.630 h; K = 1.039 (impreso 1.04); KA = 1.0009; I = 27.14 mm/h (impreso 27.10).

El K impreso a 2 decimales coincide en 10 de las 12 filas con la pendiente del cauce (fallan la 8: 1.090 frente a 1.08, y la 9: 1.058 frente a 1.05) y en 11 de 12 con la de la microcuenca (falla la 13 por 0.0002: 1.0252 frente a 1.02).

La intensidad no cierra con la pendiente del cauce:

| Pendiente usada en Témez | Diferencia de I con lo impreso, 12 filas |
|---|---|
| s, del cauce principal (la que manda la ec. 30) | de −7.4 % a +1.4 % |
| S, de la microcuenca | de −1.6 % a +1.0 % |

Con S la fila 4 sale exacta (22.49) y la 8 pasa de −7.4 % a +1.0 %. **El documento calculó Témez con la pendiente de la microcuenca**, no con la del cauce mayor. La fila «Tc» de su Tabla 6 lo confirma: es Kirpich con S (microcuenca 7: 37.97 min con S frente a 38.02 impreso; con s daría 55.06).

### 6.3 Erratas internas

| N.º | Dónde | Errata |
|---|---|---|
| 1 | Tablas 6 y 8 | Las áreas no coinciden: 0.97 km² frente a 113.89 ha; 0.20 frente a 25.57; 3.70 frente a 403.16 |
| 2 | Tabla 8, columna Q | **El K no entra en el caudal impreso.** 0.278·C·I·A con el área de la Tabla 8 y sin K da 2.40, 3.86, 0.87, 0.89 y 0.36 para las filas 1, 9, 10, 11 y 13 (impreso 2.41, 3.86, 0.87, 0.89, 0.36). Con K la fila 8 sería 6.64 y se imprime 6.09 |
| 3 | Témez | Usa la pendiente de la microcuenca (§6.2) |
| 4 | Ec. (1), p. 13 | «R = 1 − (1 − T)^n»; es 1 − (1 − 1/T)^n |
| 5 | p. 15 | «P0 = [(500/CN) – 50]»; el Manual escribe 5000/CN (ec. 35) |
| 6 | Tabla 4, p. 14 | «Tc=3.98*L^(0.77)*S^(-0.385)» con unidad «h»; ese coeficiente da minutos |
| 7 | Tabla 8 | C a 2 decimales (±1.7 %), lo que impide separar la fila 2 (0.72 sin K, 0.74 con K; impreso 0.74) |

### 6.4 Contraste de método con MH

Bajo 10 km², MH usa el racional (ec. 28) con tc de Témez, intensidad de Dick-Peschke y K. El documento usa el modificado completo (ec. 34). Con la misma P24 = 44.98 mm, la intensidad de Dick-Peschke es de 0.99 a 1.13 veces la de la ecuación (34) en las 12 microcuencas. La diferencia mayor está en las de tc más corto (10 y 11: 21 a 24 min).

El coeficiente no se puede contrastar. El documento da C de 0.22 a 0.32; el CN que los produce con la ecuación (35) sería de 74.2 a 79.8 (derivado por mí, no publicado). La Tabla N.º 08 sólo da múltiplos de 0.05.

En las microcuencas 7 y 14 MH aplicaría el modificado completo, pero falta el CN. Informativo, con Pd = 44.98 mm:

| Microcuenca | Tc (h) | K | KA | I (mm/h) | Q con CN 70 / 75 / 80 | HEC-HMS impreso | CN que lo iguala |
|---|---|---|---|---|---|---|---|
| 7 (29.94 km²) | 2.485 | 1.1823 | 0.9016 | 10.43 | 16.50 / 23.87 / 33.28 | 15.10 | 68.9 |
| 14 (10.60 km²) | 2.098 | 1.1528 | 0.9316 | 12.05 | 6.58 / 9.52 / 13.27 | 8.00 | 72.6 |

Los dos métodos son del mismo orden para CN en torno a 70, pero el CN del documento no se conoce: no es un contraste cerrado.

### 6.5 Entradas y salida esperada

- `hidrologia_casos/upeu_colpahuayco/estacion.csv`, `cuencas.csv` (14 microcuencas; `S_cauce_cuenca` = s, `S_terreno` = S; CN vacío en MC-07 y MC-14) y `salida_esperada.json`.

| Entrada | Esperado |
|---|---|
| Sicuani, `mejor_ajuste_ks` | `lognormal_2p`; D = 0.0546; d = 0.2499; P24(35) = 42.397; P24(70) = 44.726 |
| MC-01, TR 70 (C vehículo 0.30) | tc = 37.773 min; I = 28.591 mm/h; Q = 2.402 m³/s |
| MC-07 y MC-14 | `DatoFaltanteError`, campo `CN` |

**Tolerancias.** Contra el cálculo a mano: 10⁻⁹. Contra lo impreso sólo vale el K (±0.006), y no en todas las filas (§6.2). Ni la P24 ni el caudal son oráculo.

---

## 7. Caso 6 — ESPOL, vía Intervalles (Luna Chalán, 2023)

Archivo: `espol_intervalles/tesis.pdf`. La página impresa es la del PDF menos 5.

**Clasificación: descartable para el caudal; contraste de método del K-S.**

- La hidrología es ecuatoriana: IDF del INAMHI para la zona 17 y fórmula del MTOP. Q25 = 0.613 m³/s (Tabla 3.9, PDF 58, imp. 53) entraría **declarado**.
- La cuenca (9.27 ha, PDF 51) no trae L ni S.
- El cajón de 1.10 × 1.10 m con HY-8 es hidráulica (M3/M4). No es de MH y no lo traté.

Lo que sí aporta: cuatro series reales (Anexo 2, PDF 94-96) con el Dmax de K-S de Hydrognomon (Anexos 3 a 6, PDF 96-98). Verifiqué por imagen la alineación de los años y de las tres celdas vacías (Gonzanamá 1974 y 1987; Malacatos 1999). Los cuatro n coinciden (50, 48, 49, 29).

| Estación | Distribución | Mi D (ec. 13) | Hydrognomon | K-S de escalón |
|---|---|---|---|---|
| La Argelia | Normal | 0.1021 | 0.10209 | 0.1119 |
| La Argelia | Gumbel | 0.0896 | 0.0896 | 0.0967 |
| Gonzanamá | Normal | 0.0937 | 0.09365 | 0.1124 |
| Gonzanamá | Gumbel | 0.0686 | 0.06861 | 0.0873 |
| Catamayo | Normal | 0.2360 | 0.23595 | 0.2601 |
| Catamayo | Gumbel | 0.1676 | 0.16758 | 0.1918 |
| Malacatos | Normal | 0.0895 | 0.08111 | 0.1001 |
| Malacatos | Gumbel | 0.0787 | 0.08131 | 0.0901 |

En tres estaciones, Normal y Gumbel coinciden a 4 decimales: Hydrognomon usa la posición de Weibull y momentos, como el Manual. El «K-S de escalón» (el de los paquetes estadísticos generales) no coincide con ninguno: sirve para saber que un contraste hecho con `scipy.stats.kstest` daría otro número.

Lo que no coincide:

- **Log Normal** en las cuatro (La Argelia 0.0689 frente a 0.07205): Hydrognomon estima la LN de otra forma. Contraste de método.
- **Malacatos** en las tres distribuciones. Con las otras tres estaciones cuadrando, lo más probable es que la serie impresa no sea exactamente la que entró a Hydrognomon. No es oráculo.

Entradas: `hidrologia_casos/espol_intervalles/estacion.csv` y `salida_esperada.json`. Tolerancia para Normal y Gumbel en La Argelia, Gonzanamá y Catamayo: ±0.0001.

---

## 8. Hallazgos sobre `MH_hidrologia`

Ninguno es un error numérico. Van de más a menos consecuencia.

**H1. No detecta filas copiadas entre años, y no puede con el contrato actual.** Evidencia y recomendación en la §3.4: aviso sin umbral con los máximos repetidos, como entrada a la hoja de ruta.

**H2. La guardia que de verdad protege en Tumbes es la celda `fen` obligatoria.** La serie como se publica no carga (`DatoFaltanteError`). Funciona como está pensada. Pero una vez que alguien escribe «no» en toda la columna, lo único que queda es un aviso («no declara ningún año FEN»).

**H3. El programa entrega caudal con la serie de Tumbes.** Con `serie_completa` y los valores de archivo: P24(35) = 719 mm, P24(70) = 930 mm; C-39, I = 812 mm/h; Sapotal, Q70 = 3752 m³/s. Emite el aviso de años faltantes (1988, 2022) y el de consistencia («19.0 mm (1986) a 729.2 mm (1997), con mediana 134.7 mm y un cociente máximo / mediana de 5.4»), sin juzgar. Es coherente con la regla de no inventar umbrales, y el cociente 5.4 no delata nada: el de Miraflores, una serie creíble, es 10.9. La defensa real es que el proyectista lea la memoria. Lo dejo dicho porque un revisor externo esperará una detención.

**H4. El valor crítico exacto es más estricto que el 1.36/√n que usan los cuatro documentos peruanos.** n = 17: 0.3180 frente a 0.3298. n = 28: 0.2499 frente a 0.2570. n = 32: 0.2342 frente a 0.2404. n = 38: 0.2154 frente a 0.2206. Cambia un veredicto de los revisados (Normal sin FEN de Piura). En las filas tabuladas MH usa la Tabla N.º 03 (n = 25: 0.26; n = 40: 0.21), así que es fiel al Manual. Conviene que la memoria diga que el crítico no es 1.36/√n, porque es lo que el revisor recalculará.

**H5. Dick-Peschke frente a la IDF de la práctica local.** Para tc < 1 h MH da una intensidad del orden del doble que las tesis que extrapolan la Tabla N.º 04: 2.3 veces en UPAO (75.9 frente a 32.7 mm/h) y 2.07 en Tumbes C-1 (580.8 frente a 280.3, y eso que la tesis lleva el 1.13). MH aplica lo que el Manual escribe, y el criterio `relacion_intensidad_duracion` ya declara un 81 % a 1 hora. Estos dos casos lo confirman con números de terceros. Donde la tesis usa Dick-Peschke (UNSAAC), MH queda a +6 a +10 %.

**H6. Las microcuencas pequeñas y empinadas no tienen, por omisión, fórmula de tc evaluable.** En UNSAAC, 7 de 15 dan Témez bajo 0.25 h y las 15 están fuera de la población de Kirpich (19 a 42 % de pendiente). En Tumbes, 2 de 41. El programa se detiene con `MetodoNoEvaluableError` y ofrece la salida (otra fórmula, `indicador_con_aviso`, o el caudal declarado). Es correcto por la letra del Manual; es una limitación práctica en sierra que conviene anticipar en la guía de uso.

**H7. `serie_sin_fen` no es adoptable en costa norte.** En Piura se detiene con cualquiera de las cuatro declaraciones de años FEN que probé (§2.6). Es la regla de la ficha T1-09 funcionando, y coincide con la decisión de INDECI. Efecto práctico: en una estación con FEN extraordinario el criterio tiene un solo valor utilizable.

**H8. `mejor_ajuste_ks` puede elegir la Normal en una serie con quiebre.** Colquepata: Normal D = 0.1721, y P24(35) = 48.37 mm queda apenas sobre el máximo registrado (48.2 mm, T empírico 26 años). El defecto es de la serie (§4.4), no de la regla.

**H9. El contrato no tiene forma de marcar un año incompleto.** 1971 en Miraflores trae nueve meses y entra como máximo anual de 1.6 mm. Efecto medido: −1 % en la P24(25). Menor.

**Coincidencia, no hallazgo:** la lectura de MH de la ecuación (13), del estimador de la Log Normal (logaritmos, n − 1) y de Gumbel por momentos es la misma que usaron INDECI, UNTumbes, UPAO, UNSAAC y, para Normal y Gumbel, Hydrognomon.

---

## 9. Después del sello: el programa sobre los casos

Corrido el 2026-11-18, después de `SHA1SUMS_congelado.txt`, con `/home/user/venv312/bin/python -B hidrologia_casos/_calculo/comparar_con_programa.py` y el directorio del proyecto como cwd. Salida en `hidrologia_casos/_calculo/comparacion_con_programa.txt`. Commit del proyecto: `6b08e4b`.

| Caso | Comparado | Resultado |
|---|---|---|
| Piura | 12 (distribución, TR); 5 declaraciones adversariales | Coincide. Normal y Gumbel se detienen por K-S; `serie_sin_fen` y `dos_poblaciones`, `MetodoNoEvaluableError`; sin declarar, `CriterioPendienteError`; aviso de 151.4 mm emitido |
| UPeU | 8 de estación; 24 (cuenca, TR) | Coincide. MC-07 y MC-14: `DatoFaltanteError('CN')` |
| Tumbes | 12 de estación; 78 (cuenca, TR) | Coincide. `fen` vacío: `DatoFaltanteError`. C-20 y C-27: `MetodoNoEvaluableError` |
| UNSAAC | 8 de estación; 16 (cuenca, TR) | Coincide. LN se detiene por K-S; 7 cuencas, `MetodoNoEvaluableError` |
| UPAO | 48 de estación; ALC-19 | Coincide. Por omisión, `MetodoNoEvaluableError`; con `indicador_con_aviso`, Q = 9.2297 m³/s |
| ESPOL | 48 de estación | Coincide |

- **Peor diferencia relativa en P24, D, d crítico, tc, I, C y Q: 9.7·10⁻¹⁶.**
- **Discrepancias: 0.** Excepciones esperadas que salieron: 11 de cuencas, más las de estación.
- Dos filas con la misma etiqueta de año: `DatoInvalidoError`, como dice el docstring.

Lo que esto prueba y lo que no: que MH implementa las fórmulas del Manual tal como yo las leí, y que cuatro terceros llegaron a los mismos números en estimadores y K-S. No prueba el caudal contra ningún tercero, porque ninguno lo calcula con el método de MH de punta a punta.

---

## 10. Archivos

Todo bajo `/tmp/claude-0/-home-user-Proyecto-alcantarillas/4ee726ed-9c15-53e3-939e-198cb9226506/scratchpad/verif/hidrologia_casos/`.

| Ruta | Contenido |
|---|---|
| `_calculo/datos_publicados.py` | Transcripción de los datos de los seis documentos, con página |
| `_calculo/calculo_a_mano.py` | El cálculo independiente; genera las entradas y las salidas esperadas |
| `_calculo/resultados_a_mano.txt` y `.json` | Resultados del cálculo a mano |
| `_calculo/SHA1SUMS_congelado.txt` | El sello, anterior a correr el programa |
| `_calculo/comparar_con_programa.py` y `comparacion_con_programa.txt` | La comparación posterior |
| `indeci_piura/` | `estacion.csv`, `estacion_fen_5_sin_1973.csv`, `salida_esperada.json` |
| `upeu_colpahuayco/` | `estacion.csv`, `cuencas.csv`, `salida_esperada.json` |
| `untumbes_tu107/` | `estacion_como_se_publica_fen_vacio.csv`, `estacion_fen_declarado_por_el_verificador.csv`, `cuencas.csv`, `salida_esperada.json` |
| `unsaac_42tmc/` | `estacion.csv`, `cuencas.csv`, `salida_esperada.json` |
| `upao_la_jalca/` | `estacion.csv`, `cuencas.csv`, `salida_esperada.json` |
| `espol_intervalles/` | `estacion.csv`, `salida_esperada.json` |
| `_txt/` | Texto de los PDF (`pdftotext -layout`) e imágenes de comprobación |

Para rehacer el cálculo a mano: `/home/user/venv312/bin/python -I _calculo/calculo_a_mano.py`.

**Limitaciones de este trabajo.**

- Las tablas se leyeron de la capa de texto de los PDF. Verifiqué por imagen sólo el Anexo 2 de ESPOL; las demás se validan por sus sumas y por coincidir con los estadísticos impresos.
- Los CSV de cuencas llevan `cobertura`, `suelo` y `S_terreno` como vehículo, no como dato publicado (§1.4).
- No corrí el pipeline completo por la CLI: no hay CSV de puntos publicable sin inventar columnas.
- `/home/user/Proyecto_alcantarillas/docs/validacion_integral.md` aparece modificado en el árbol de trabajo (mtime 03:42:06Z). No es de esta sesión, que sólo importó MH en lectura; hay otros agentes activos.
