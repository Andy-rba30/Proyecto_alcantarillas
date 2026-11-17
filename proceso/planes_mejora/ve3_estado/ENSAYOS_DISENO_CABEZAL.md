# Ensayos de diseño del cabezal — revisión estructural independiente

**Revisor:** ingeniero estructural independiente (adversarial), sesión del 2026-11-17.
**Objeto:** el cabezal por punto de la app de alcantarillas (`src/modulos/M9_cabezal.py`,
Fase 9: muro de cabecera en voladizo con punta, talón y aleros), en el commit
`d78f2c4` de la rama `claude/youthful-shannon-rjzmuc` (clon de trabajo
`/home/user/ensayos_cabezal`; el repositorio original no se tocó).
**Pregunta:** ¿la app produce un BUEN diseño de cabezal? Se contrasta su geometría y su
armado con un diseño propio hecho a mano **antes** de mirar el resultado de la app.

> Estado del documento: se escribe por etapas. §1–§3 se escribieron y se congelaron
> ANTES de correr la app a expediente (sello en §3.4).

---

## 1. Método del ensayo

1. **Entradas por la puerta real.** Cada escenario es un punto de Familia A (paso de
   quebrada bajo terraplén) en un CSV de una fila, con `--datos-externos`,
   `--datos-sitio` y `--declarar`, partiendo del juego de la validación integral (T-11).
   Todo está en `/home/user/ensayos_cabezal_casos/<escenario>/` (CSV, JSON, lista de
   declaraciones, comando y salidas). Generador: `herramientas/matriz.py` y
   `herramientas/escenarios.py`.
2. **El conducto es una entrada del cabezal.** La app se corrió primero a `--alcance
   perfil` (la Fase 9 está diferida a ese alcance: no imprime nada del cabezal) para fijar
   el tubo, las cotas, el HW, el TW y la hoya de socavación. Esos datos —y solo esos— se
   extrajeron a `diseno_mano/entradas_geometricas.json` (`herramientas/extraer_entradas.py`).
3. **Diseño a mano** con `diseno_mano/diseno_mano.py`, que **no importa `src/` ni llama a
   la CLI**. Resultado congelado en `diseno_mano/diseno_mano_CONGELADO_antes_de_la_app.json`
   (sha1 en §3.4).
4. Después, la app a `--alcance expediente` (`salida_expediente.json` de cada escenario) y
   la comparación (§4 en adelante).

### 1.1 Qué tomé igual que la app (decisiones de proyecto, no de método)

Para comparar el **método de diseño** y no los datos, uso las mismas decisiones de
proyecto que la app trae de archivo o que el juego declara: f'c = 21 MPa, fy = 420 MPa
(A615 Gr 60, γ3 = 0.67), γc = 23.56 kN/m³, relleno γ = 17 kN/m³ (γsat 20), talud 2:1,
δ = 0.67·φ en el plano virtual (C3.11.5.3, PDF 175: «long-term practice has been to use
δ = 0.67φ ... soil against concrete as well as soil against soil»), h_eq = 2.0 ft
(Tabla 3.11.6.4-2, muro paralelo, ≥ 1 ft del borde), η = 1.05 en Resistencia I (η_I del
cruce), γ_EQ = 0.5 sobre LS, recubrimiento de 91.44 mm en todas las caras (el que la app
arma: 3.0 in «coastal» × 1.2 por a/c), clase 2 de exposición en 5.6.7, y la **geometría
que fijan las cotas**: coronación = clave exterior + 0.30 + 0.15 (o el agua), desplante
0.80 m en la entrada y bajo la hoya de socavación + 0.61 m en la salida, relleno retenido
hasta la coronación − 0.15 m y talud que sube hasta el borde de la plataforma.

### 1.2 Qué decidí YO como diseñador (y que la app puede decidir distinto)

| Tema | Mi diseño | Fuente (verificada en el PDF) |
|---|---|---|
| Factores de resistencia de estabilidad | **φb = 0.55, φτ = 1.0** (Tabla 11.5.7-1, muros de gravedad y semigravedad); sismo φb = 0.80, φτ = 1.0 | AASHTO LRFD 9.ª 11.5.7 (pág. impresa 11-15, PDF 1484: «the resistance factors provided in Table 11.5.7-1 **shall be used for wall design**»); Tabla 11.5.7-1 (pág. 11-17, PDF 1486); 11.5.8 (pág. 11-18, PDF 1487) |
| Empuje estático | Cuña de tanteo (Culmann) sobre el plano vertical del extremo del talón, superficie real (talud que sube y plataforma); contraste con Coulomb y pendiente equivalente | 3.11.5.3 (PDF 175) y C3.11.5.3 |
| Empuje sísmico | Cuña pseudoestática con k_h, k_v = 0; **P_AE con la distribución del estático (resultante a h/3)** | 11.6.5.3 (pág. 11-30, PDF 1499: «should be distributed using the same distribution as the static earth pressure ... but no less than H/3») |
| Inercia | P_IR = k_h(W_w + W_s), W_s incluye el suelo sobre el talón; casos 100 % P_AE + 50 % P_IR y max(50 % P_AE, P_A) + 100 % P_IR | 11.6.5.1 (pág. 11-26, PDF 1495) |
| k_h | 0.5·k_h0 cuando el escenario admite el desplazamiento; k_h0 = F_pga·PGA | 11.6.5.2.2 (PDF 1497) |
| Portante | σ = V/(B − 2e) ≤ φ·q_n, q_n de 10.6.3.1.2a con B', factores de inclinación (cargas sin factorar), C_wq, C_wγ; d_q = 1 | 11.6.3.2 (PDF 1490); 10.6.3.1.2a (PDF 1360) |
| Excentricidad | e ≤ B/3 (estático, suelo); sismo e ≤ (1/3 + γEQ·(0.4 − 1/3))·B | 11.6.3.3 (PDF 1493); 11.6.5.1 (PDF 1494) |
| Deslizamiento | R = V·tan φ_f (vaciado contra el suelo); arcilla min(c, σ/2)·B'; pasivo despreciado | 10.6.3.4; 11.6.3.5 (PDF 1493) |
| Ajuste | Menor B en malla de 0.05 m con **la punta libre** (0.20 B a 0.50 B); pantalla y zapata crecen de 0.05 en 0.05 hasta que su armado cumple | procedimiento clásico |
| Pantalla | Empuje **activo** (voladizo que cede), γ_EH = 1.50; el reposo K0 (γ 1.35) se imprime al lado | C3.11.5.2 (muro en voladizo > 5 ft desarrolla la condición activa) |
| Zapata, presión de contacto | Lineal (triangular o trapezoidal) con cargas factoradas | C10.6.5 (pág. 10-86, PDF 1375: «a triangular or trapezoidal contact stress distribution based on factored loads **shall** be used») |
| Talón | **Método más exacto**: cargas hacia abajo menos la reacción del suelo; el de «peso entero» se imprime como contraste | 11.6.1.2 (pág. 11-20, PDF 1489: «loaded with the full weight of the superimposed material, **unless a more exact method is used**»); Caltrans BDP 11.2 lo hace así (ejemplo resuelto) |
| Cortante | 5.7.3.3; β = 2 donde 5.7.3.4.1 lo permite; **donde no, el procedimiento general 5.7.3.4.2 (ec. -2, sin estribos)**; sección crítica: punta a d_v de la cara, talón en la cara | 5.7.3.4.1–2 (pág. 5-70, PDF 429); C5.12.8.6.1 (pág. 5-251, PDF 610) |
| Mínimos | 5.6.3.3 (Mr ≥ min(Mcr, 1.33 Mu)), 5.10.3.2 (s ≤ 1.5 t y 18 in), 5.6.7 (clase 2), 5.10.6 | Sec. 5 |

---

## 2. Matriz de escenarios (escrita antes de diseñar)

Todos son un tubo de concreto bajo terraplén (Familia A), con freático a 3.0 m bajo el
terreno del cruce (39.10 msnm), PGA 0.50 g en roca (costa, zona 4) salvo E9, filas de
sitio C-D-E (F_pga = 1.0 a PGA 0.50) salvo E9, y lecho de grava gruesa (la hoya de HEC-14
baja el desplante de salida). Cada escenario da **dos cabezales** (entrada y salida).

| Esc. | Qué varía | Conducto (perfil) | Terraplén | Esviaje | Fundación | Relleno trasdós | Sismo |
|---|---|---|---|---|---|---|---|
| **E1** referencia | — | Ø0.90 m (Q 1.167) | 2.1 m | 15° | arena φf 32°, γ 18 | φ 34°, drenado | k_h0 0.50, **con** reducción (k_h 0.25) |
| **E2** alto | altura | Ø1.20 m (Q 2.6) | 4.0 m | 15° | como E1 | como E1 | como E1 |
| **E3** muy alto | altura | Ø1.50 m (Q 4.5, S 0.010) | 4.0 m | 0° | como E1 | como E1 | como E1 |
| **E4** arena suelta | fundación | como E1 | 2.1 m | 15° | arena limosa φf 27°, γ 17 | como E1 | como E1 |
| **E5** arcilla | fundación | como E1 | 2.1 m | 15° | arcilla c_u 40 kPa (φ 0), γ 18 | como E1 | como E1 |
| **E6** grava densa alto | fundación + altura | como E2 | 4.0 m | 15° | grava φf 38°, γ 20 | como E1 | como E1 |
| **E7** sin drenaje | relleno | como E1 | 2.1 m | 15° | como E1 | **φ 30°, sin drenaje** (agua hasta el relleno) | como E1 |
| **E8** sismo severo | sismo | como E1 | 2.1 m | 15° | como E1 | como E1 | k_h0 0.50, **sin** reducción (k_h 0.50: valor de archivo) |
| **E9** sismo bajo | sismo | como E1 | 2.1 m | 15° | como E1 | como E1 | PGA 0.15, clase C (F_pga 1.2): k_h0 0.18, k_h 0.09 |
| **E10** esviaje | esviaje | como E1 | 2.1 m | **45°** (aleros 30°) | como E1 | como E1 | como E1 |

Alturas de cabezal resultantes (de las cotas, iguales en la app y en mi diseño): entrada
2.25 m (E1, E4, E5, E7–E10), 2.575 m (E2, E6), 2.90 m (E3); salida 3.83 m (E1, E4, E5,
E7–E9), 3.785 m (E10), 4.51 m (E2, E6), 5.10 m (E3). La salida es más alta porque el
desplante baja hasta la hoya de socavación de HEC-14 menos 0.61 m.

Pares de **monotonía** que la matriz permite leer: altura E1 → E2 → E3; fundación E6 (φ
38) ↔ E2 (φ 32), E1 (φ 32) → E4 (φ 27); sismo E9 (k_h 0.09) → E1 (0.25) → E8 (0.50);
relleno E1 → E7.

---

## 3. Mi diseño (congelado antes de correr la app)

### 3.1 Geometría

| Esc. | Extremo | H_c (m) | **B** (m) | punta (m) | talón (m) | pantalla (m) | **zapata** (m) | B/H_c | punta/B | uso máx. | gobierna (uso ≥ 0.95) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | entrada | 2.250 | **1.55** | 0.35 | 0.90 | 0.30 | **0.40** | 0.69 | 0.23 | 0.997 | E3-LRFD est 0.997 |
| E1 | salida | 3.827 | **2.85** | 0.65 | 1.90 | 0.30 | **0.40** | 0.74 | 0.23 | 0.953 | E1-LRFD sis 0.953 |
| E2 | entrada | 2.575 | **2.60** | 0.55 | 1.75 | 0.30 | **0.40** | 1.01 | 0.21 | 0.975 | E3-LRFD est 0.960; E3-LRFD sis 0.975 |
| E2 | salida | 4.510 | **4.55** | 1.15 | 3.05 | 0.35 | **0.50** | 1.01 | 0.25 | 0.973 | E1-LRFD sis 0.973 |
| E3 | entrada | 2.900 | **2.65** | 0.55 | 1.80 | 0.30 | **0.40** | 0.91 | 0.21 | 0.999 | E1-LRFD sis 0.999 |
| E3 | salida | 5.100 | **5.05** | 1.25 | 3.40 | 0.40 | **0.55** | 0.99 | 0.25 | 0.990 | E1-LRFD sis 0.990 |
| E4 | entrada | 2.250 | **1.95** | 0.40 | 1.25 | 0.30 | **0.40** | 0.87 | 0.20 | 0.970 | E3-LRFD est 0.970 |
| E4 | salida | 3.827 | **3.70** | 0.90 | 2.50 | 0.30 | **0.40** | 0.97 | 0.24 | 0.991 | E1-LRFD est 0.991; E1-LRFD sis 0.990 |
| E5 | entrada | 2.250 | **1.95** | 0.40 | 1.25 | 0.30 | **0.40** | 0.87 | 0.20 | 0.988 | E3-LRFD est 0.988 |
| E5 | salida | 3.827 | **3.00** | 0.90 | 1.80 | 0.30 | **0.40** | 0.78 | 0.30 | 0.992 | E1-LRFD est 0.984; E3-LRFD sis 0.992 |
| E6 | entrada | 2.575 | **2.05** | 0.45 | 1.30 | 0.30 | **0.40** | 0.80 | 0.22 | 0.959 | E1-LRFD sis 0.959 |
| E6 | salida | 4.510 | **3.55** | 0.75 | 2.45 | 0.35 | **0.50** | 0.79 | 0.21 | 0.952 | E1-LRFD sis 0.952 |
| E7 | entrada | 2.250 | **3.15** | 0.65 | 2.20 | 0.30 | **0.40** | 1.40 | 0.21 | 0.990 | E3-LRFD est 0.990 (sismo no evaluable: relleno saturado) |
| E7 | salida | 3.827 | **4.70** | 0.95 | 3.40 | 0.35 | **0.45** | 1.23 | 0.20 | 0.998 | E3-LRFD est 0.998 (sismo no evaluable: relleno saturado) |
| E8 | entrada | 2.250 | **4.60** | 0.95 | 3.35 | 0.30 | **0.40** | 2.04 | 0.21 | 1.000 | E3-LRFD sis 1.000 |
| E8 | salida | 3.827 | **6.95** | 1.40 | 5.25 | 0.30 | **0.45** | 1.82 | 0.20 | 0.999 | E3-LRFD sis 0.999 |
| E9 | entrada | 2.250 | **1.55** | 0.35 | 0.90 | 0.30 | **0.40** | 0.69 | 0.23 | 0.997 | E3-LRFD est 0.997 |
| E9 | salida | 3.827 | **2.45** | 0.70 | 1.45 | 0.30 | **0.40** | 0.64 | 0.29 | 0.929 | — |
| E10 | entrada | 2.250 | **1.55** | 0.35 | 0.90 | 0.30 | **0.40** | 0.69 | 0.23 | 0.997 | E3-LRFD est 0.997 |
| E10 | salida | 3.785 | **2.85** | 0.65 | 1.90 | 0.30 | **0.40** | 0.75 | 0.23 | 0.956 | E1-LRFD sis 0.956 |

### 3.2 Armado (barra principal por metro)

| Esc. | Extremo | Pantalla: Mu (kN·m/m) activo / K0 | Pantalla: barra | Punta: Mu | Punta: barra | Talón neto: Mu (máx. Res/EE) | Talón: barra | Talón «peso entero»: Mu | cortante de la zapata |
|---|---|---|---|---|---|---|---|---|---|
| E1 | entrada | 18.1 / 20.8 | Ø1/2" @ 0.300 | 5.5 | Ø1/2" @ 0.300 | 23.7 | Ø1/2" @ 0.300 | 41.3 | β = 2 |
| E1 | salida | 85.9 / 107.3 | Ø3/4" @ 0.150 | 22.5 | Ø1/2" @ 0.300 | 115.1 | Ø5/8" @ 0.200 | 276.5 | β = 2 |
| E2 | entrada | 29.4 / 31.9 | Ø1/2" @ 0.200 | 12.3 | Ø1/2" @ 0.300 | 75.3 | Ø5/8" @ 0.250 | 182.0 | β = 2 |
| E2 | salida | 151.0 / 164.3 | Ø3/4" @ 0.100 | 65.8 | Ø1/2" @ 0.200 | 315.5 | Ø3/4" @ 0.125 | no cabe en la zapata | general 5.7.3.4.2 (talón β = 1.88) |
| E3 | entrada | 42.6 / 46.2 | Ø1/2" @ 0.200 | 14.6 | Ø1/2" @ 0.300 | 91.1 | Ø1/2" @ 0.150 | 210.5 | β = 2 |
| E3 | salida | 208.9 / 232.1 | Ø3/4" @ 0.100 | 85.3 | Ø1/2" @ 0.175 | 411.3 | Ø3/4" @ 0.100 | no cabe en la zapata | general 5.7.3.4.2 (talón β = 1.93) |
| E4 | entrada | 18.1 / 20.8 | Ø1/2" @ 0.300 | 5.4 | Ø1/2" @ 0.300 | 29.2 | Ø1/2" @ 0.300 | 77.3 | β = 2 |
| E4 | salida | 85.9 / 107.3 | Ø3/4" @ 0.150 | 30.5 | Ø1/2" @ 0.300 | 122.4 | Ø1/2" @ 0.125 | no cabe en la zapata | β = 2 |
| E5 | entrada | 18.1 / 20.8 | Ø1/2" @ 0.300 | 5.4 | Ø1/2" @ 0.300 | 29.2 | Ø1/2" @ 0.300 | 77.3 | β = 2 |
| E5 | salida | 85.9 / 107.3 | Ø3/4" @ 0.150 | 33.7 | Ø1/2" @ 0.300 | 101.0 | Ø1/2" @ 0.150 | 249.8 | β = 2 |
| E6 | entrada | 29.4 / 31.9 | Ø1/2" @ 0.200 | 10.8 | Ø1/2" @ 0.300 | 60.7 | Ø1/2" @ 0.175 | 101.6 | β = 2 |
| E6 | salida | 151.0 / 164.3 | Ø3/4" @ 0.100 | 43.6 | Ø1/2" @ 0.300 | 294.4 | Ø5/8" @ 0.100 | 576.1 | general 5.7.3.4.2 (talón β = 1.78) |
| E7 | entrada | 26.7 / 28.1 | Ø1/2" @ 0.250 | 10.2 | Ø1/2" @ 0.300 | 45.1 | Ø1/2" @ 0.200 | 246.4 | β = 2 |
| E7 | salida | 133.4 / 147.7 | Ø3/4" @ 0.100 | 39.2 | Ø1/2" @ 0.300 | 175.2 | Ø1" @ 0.125 | no cabe en la zapata | general 5.7.3.4.2 (talón β = 3.01) |
| E8 | entrada | 18.1 / 20.8 | Ø1/2" @ 0.300 | 18.0 | Ø1/2" @ 0.300 | 94.9 | Ø5/8" @ 0.250 | no cabe en la zapata | β = 2 |
| E8 | salida | 82.7 / 103.2 | Ø3/4" @ 0.150 | 72.3 | Ø5/8" @ 0.250 | 408.1 | Ø1" @ 0.150 | no cabe en la zapata | general 5.7.3.4.2 (talón β = 3.36) |
| E9 | entrada | 18.1 / 20.8 | Ø1/2" @ 0.300 | 5.5 | Ø1/2" @ 0.300 | 23.7 | Ø1/2" @ 0.300 | 41.3 | β = 2 |
| E9 | salida | 85.9 / 107.3 | Ø3/4" @ 0.150 | 29.3 | Ø1/2" @ 0.300 | 91.1 | Ø1/2" @ 0.150 | 166.8 | β = 2 |
| E10 | entrada | 18.1 / 20.8 | Ø1/2" @ 0.300 | 5.5 | Ø1/2" @ 0.300 | 23.7 | Ø1/2" @ 0.300 | 41.3 | β = 2 |
| E10 | salida | 84.0 / 103.9 | Ø3/4" @ 0.150 | 22.3 | Ø1/2" @ 0.300 | 114.7 | Ø5/8" @ 0.200 | 275.1 | β = 2 |

### 3.3 Lectura de mi diseño

* **B/H_c de 0.64 a 1.01** en los escenarios «normales» (E1–E6, E9, E10), dentro de la
  práctica (0.5–0.7 H para relleno horizontal; más con relleno en talud o sismo). Con el
  relleno saturado (E7) sube a 1.23–1.40 y con k_h = k_h0 = 0.50 (E8) a **1.82–2.04**: con
  k_h = 0.5 cada kN de suelo sobre el talón suma 0.5 kN de inercia contra 0.625 kN de
  resistencia (tan 32°), y la zapata sin dentellón se vuelve irracional; un diseñador
  pondría un dentellón de corte o admitiría el desplazamiento (11.6.5.2.2).
* **La punta queda en 0.20–0.30 B**: el deslizamiento o el portante sísmico gobiernan, y
  lo que más rinde es el talón (peso del relleno); la punta se acorta por debajo del B/3
  de la regla.
* **Pantalla de 0.30 m** hasta 3.8 m de altura; 0.35 m para 4.5 m y 0.40 m para 5.1 m (con
  0.30 m no cumple la flexión/fisuración). **Zapata de 0.40 m** hasta 3.8 m, 0.45–0.55 m en
  los altos o los de talón muy largo.
* **El talón con el «peso entero» de 11.6.1.2 da 2 a 3 veces el momento del método
  exacto** (E1 salida: 276 contra 115 kN·m/m) y en los muros altos no cabe en la zapata
  que la estabilidad y el método exacto piden: es la regla que hace crecer el peralte.
* E3 salida tiene 0.26 m de agua sobre la base (freático 39.10, desplante 38.84): evalué
  el sismo con la cuña seca sobre toda la altura y el agua aparte; **el sismo gobierna**
  y lleva B de 3.95 m (solo estático) a 5.05 m.

### 3.4 Sello

`diseno_mano/diseno_mano.py` sha1 `9ded2c631092e0d1b0531f6068cb1768265aac19`;
`diseno_mano/diseno_mano_CONGELADO_antes_de_la_app.json` sha1
`1a80f5849dd2c97e46247e327d350a96667c4a01`; entradas `73b5a7d13a8149d00d64c6f34e2352304e2801aa`;
congelado el 2026-11-17T21:17Z, **antes** de la primera corrida a expediente
(ninguna `salida_expediente*.json` existía).

Comprobaciones del motor propio (antes de usarlo): la cuña reproduce Coulomb (3.11.5.3-1)
y Mononobe-Okabe (A11.3.1) a 1e-8 con relleno horizontal y con talud infinito 2:1, y la
cadena E1/E2/E3 de E1-entrada se rehízo a mano (N = 61.86 kN/m, R = 38.65 contra
H = 38.52 kN/m; e = 0.397 m; q_n = 218.7 kPa).

---

## 4. Lo que la app produjo (corrida a expediente, después del sello)

Comando por escenario en `<escenario>/comando_expediente.txt`; salida de la CLI en
`salida_expediente.json` y `stdout_expediente.txt`. La traza de intentos
(`intentos_de_zapata`, `intentos_de_peralte`) **no está en el JSON** de la CLI (solo en
la memoria HTML, pasos 9.3.d/9.3.p): la extraje del `InformePunto` corriendo el servicio
en proceso por las mismas puertas que la CLI (`herramientas/extraer_app.py` →
`app_resumen.json`; la geometría coincide con el JSON de la CLI en los 20 cabezales).
Memoria HTML de E1 en `E1_referencia/memoria_expediente.html`.

Trazas de dimensionamiento más representativas (B en m; «A2-NV» = «A2: fuera de
5.7.3.4.1, sin verificar»):

* **E1 salida** — ancho: 2.679 (E3 est, E1 sís) → 2.779 → 2.879 (E1 sís) → 2.979 → **3.079
  cumple**; peralte: 0.404 (A1, A2 talón) → 0.504 A2-NV → 0.604 A2-NV → 0.704 A2-NV →
  **0.804 cumple**.
* **E2 entrada** — ancho 1.802 → … 16 intentos … → **3.303**; peralte 0.404 (A1, A2 talón)
  → 0.504 … 0.904 (cinco A2-NV) → **1.004**.
* **E5 salida (arcilla)** — ancho 2.679 → … → 5.579 → **5.679 (tope 1.5·H_c) y 14
  intentos más idénticos en el tope**, siempre E1-LRFD.est.s; peralte 0.404 → 0.504 …
  1.604 (doce A2-NV, con el ancho «re-dimensionado» en el tope en cada vuelta) →
  **1.704**. Resultado final: B 5.68 m × zapata 1.70 m y **E1 sigue sin cumplir**
  (135.8 > 98.4 kPa).
* **E3 salida** — 0.257 m de agua sobre la base: la condición sísmica es «método no
  evaluable» (`Bloqueo`) y **el ancho se dimensiona solo con la estática**: 3.570 → … →
  4.570.

Resultados completos: Tablas G, C, A, Z y M (§5).

---

## 5. Comparación

### Tabla G — geometría: mi diseño frente a la app

| Esc. | Ext. | H_c | B mano | B app | ΔB | punta mano / app | talón mano / app | pantalla mano / app | zapata mano / app | B/H_c app | e_z/H_c app | concreto m³/m mano / app | Δ concreto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | ent | 2.25 | 1.55 | 2.08 | +34 % | 0.35 / 0.52 | 0.90 / 1.26 | 0.30 / 0.30 | 0.40 / **0.40** | 0.92 | 0.18 | 1.18 / 1.39 | +18 % |
| E1 | sal | 3.83 | 2.85 | 3.08 | +8 % | 0.65 / 0.88 | 1.90 / 1.89 | 0.30 / 0.30 | 0.40 / **0.80** | 0.80 | 0.21 | 2.17 / 3.38 | +56 % |
| E2 | ent | 2.58 | 2.60 | 3.30 | +27 % | 0.55 / 0.59 | 1.75 / 2.41 | 0.30 / 0.30 | 0.40 / **1.00** | 1.28 | 0.39 | 1.69 / 3.79 | +124 % |
| E2 | sal | 4.51 | 4.55 | 4.86 | +7 % | 1.15 / 1.04 | 3.05 / 3.52 | 0.35 / 0.30 | 0.50 / **1.35** | 1.08 | 0.30 | 3.68 / 7.51 | +104 % |
| E3 | ent | 2.90 | 2.65 | 3.33 | +26 % | 0.55 / 0.67 | 1.80 / 2.36 | 0.30 / 0.30 | 0.40 / **1.00** | 1.15 | 0.35 | 1.81 / 3.91 | +116 % |
| E3 | sal | 5.10 | 5.05 | 4.57 | -10 % | 1.25 / 1.18 | 3.40 / 3.09 | 0.40 / 0.30 | 0.55 / **1.21** | 0.90 | 0.24 | 4.60 / 6.70 | +46 % |
| E4 | ent | 2.25 | 1.95 | 2.48 | +27 % | 0.40 / 0.52 | 1.25 / 1.66 | 0.30 / 0.30 | 0.40 / **0.40** | 1.10 | 0.18 | 1.33 / 1.55 | +16 % |
| E4 | sal | 3.83 | 3.70 | 4.78 | +29 % | 0.90 / 0.88 | 2.50 / 3.59 | 0.30 / 0.30 | 0.40 / **1.40** | 1.25 | 0.37 | 2.51 / 7.44 | +196 % |
| E5 | ent | 2.25 | 1.95 | 2.38 | +22 % | 0.40 / 0.52 | 1.25 / 1.56 | 0.30 / 0.30 | 0.40 / **0.40** | 1.06 | 0.18 | 1.33 / 1.51 | +13 % |
| E5 | sal | 3.83 | 3.00 | 5.68 | +89 % | 0.90 / 0.88 | 1.80 / 4.49 | 0.30 / 0.30 | 0.40 / **1.70** | 1.48 | 0.45 | 2.23 / 10.31 | +363 % |
| E6 | ent | 2.58 | 2.05 | 2.50 | +22 % | 0.45 / 0.59 | 1.30 / 1.61 | 0.30 / 0.30 | 0.40 / **0.40** | 0.97 | 0.16 | 1.47 / 1.66 | +13 % |
| E6 | sal | 4.51 | 3.55 | 3.86 | +9 % | 0.75 / 1.04 | 2.45 / 2.52 | 0.35 / 0.30 | 0.50 / **1.05** | 0.86 | 0.23 | 3.18 / 5.09 | +60 % |
| E7 | ent | 2.25 | 3.15 | 3.38 | +7 % | 0.65 / 0.52 | 2.20 / 2.56 | 0.30 / 0.30 | 0.40 / **1.00** | 1.50 | 0.45 | 1.81 / 3.76 | +107 % |
| E7 | sal | 3.83 | 4.70 | 5.58 | +19 % | 0.95 / 0.88 | 3.40 / 4.39 | 0.35 / 0.30 | 0.45 / **1.70** | 1.46 | 0.45 | 3.30 / 10.14 | +208 % |
| E8 | ent | 2.25 | 4.60 | 3.38 | -27 % | 0.95 / 0.52 | 3.35 / 2.56 | 0.30 / 0.30 | 0.40 / **1.00** | 1.50 | 0.45 | 2.40 / 3.76 | +57 % |
| E8 | sal | 3.83 | 6.95 | 5.68 | -18 % | 1.40 / 0.88 | 5.25 / 4.49 | 0.30 / 0.30 | 0.45 / **1.70** | 1.48 | 0.45 | 4.14 / 10.31 | +149 % |
| E9 | ent | 2.25 | 1.55 | 2.08 | +34 % | 0.35 / 0.52 | 0.90 / 1.26 | 0.30 / 0.30 | 0.40 / **0.40** | 0.92 | 0.18 | 1.18 / 1.39 | +18 % |
| E9 | sal | 3.83 | 2.45 | 2.88 | +17 % | 0.70 / 0.88 | 1.45 / 1.69 | 0.30 / 0.30 | 0.40 / **0.70** | 0.75 | 0.18 | 2.01 / 2.96 | +48 % |
| E10 | ent | 2.25 | 1.55 | 2.08 | +34 % | 0.35 / 0.52 | 0.90 / 1.26 | 0.30 / 0.30 | 0.40 / **0.40** | 0.92 | 0.18 | 1.18 / 1.39 | +18 % |
| E10 | sal | 3.79 | 2.85 | 3.05 | +7 % | 0.65 / 0.87 | 1.90 / 1.88 | 0.30 / 0.30 | 0.40 / **0.80** | 0.81 | 0.21 | 2.16 / 3.35 | +55 % |

### Tabla C — ¿la geometría final de la app cumple SUS verificaciones?

| Esc. | Ext. | Estabilidad E1–E3 (LRFD, decide) | Armado de la zapata (punta y talón, A1–A6) | Pantalla y alero (A1–A6) | Bloqueos |
|---|---|---|---|---|---|
| E1 | ent | cumple | cumple | cumple | — |
| E1 | sal | cumple | cumple | NO: A1 | — |
| E2 | ent | cumple | cumple | cumple | — |
| E2 | sal | cumple | cumple | NO: A1, A2, A3, A4, A6 | — |
| E3 | ent | cumple | cumple | NO: A1 | — |
| E3 | sal | cumple | cumple | NO: A1, A2, A3, A4, A6 | sísmica no evaluable |
| E4 | ent | cumple | cumple | cumple | — |
| E4 | sal | cumple | cumple | cumple | — |
| E5 | ent | cumple | cumple | cumple | — |
| E5 | sal | NO: E1-LRFD.est.s | cumple | cumple | — |
| E6 | ent | cumple | cumple | NO: A1 | — |
| E6 | sal | cumple | cumple | NO: A1, A2, A3, A4, A6 | — |
| E7 | ent | NO: E3-LRFD.est.e | cumple | cumple | sísmica no evaluable |
| E7 | sal | cumple | cumple | cumple | sísmica no evaluable |
| E8 | ent | NO: E3-LRFD.sis.e | cumple | cumple | — |
| E8 | sal | NO: E1-LRFD.sis.s, E3-LRFD.sis.s | cumple | cumple | — |
| E9 | ent | cumple | cumple | cumple | — |
| E9 | sal | cumple | cumple | NO: A1 | — |
| E10 | ent | cumple | cumple | cumple | — |
| E10 | sal | cumple | cumple | NO: A1 | — |

### Tabla A — de dónde sale la diferencia de B (paso 0.10 de la app salvo indicación)

| Esc. | Ext. | B app | B reproducido (criterios y procedimiento de la app, e_z final) | con φ de la Tabla 11.5.7-1 | con el incremento sísmico a h/3 | mis criterios, solo talón, paso 0.10 | mis criterios, punta libre, paso 0.05 (e_z de la app) | B mano (congelado) |
|---|---|---|---|---|---|---|---|---|
| E1 | ent | 2.08 | 2.08 | 1.77 | 2.08 | 1.77 | 1.55 | 1.55 |
| E1 | sal | 3.08 | 3.08 | 3.08 | 2.88 | 2.88 | 2.83 | 2.85 |
| E2 | ent | 3.30 | 3.00 | 2.70 | 3.00 | 2.50 | 2.48 | 2.60 |
| E2 | sal | 4.86 | 4.76 | 4.76 | 4.56 | 4.56 | 4.50 | 4.55 |
| E3 | ent | 3.33 | 3.03 | 2.83 | 3.03 | 2.63 | 2.61 | 2.65 |
| E3 | sal | 4.57 | 5.37 | 5.37 | 5.07 | 5.07 | 5.04 | 5.05 |
| E4 | ent | 2.48 | 2.48 | 2.08 | 2.48 | 2.08 | 1.90 | 1.95 |
| E4 | sal | 4.78 | 4.68 | 4.08 | 4.68 | 4.08 | 3.68 | 3.70 |
| E5 | ent | 2.38 | 2.38 | 2.08 | 2.38 | 2.08 | 1.95 | 1.95 |
| E5 | sal | 5.68 | — | — | — | — | 3.13 | 3.00 |
| E6 | ent | 2.50 | 2.50 | 2.30 | 2.50 | 2.10 | 2.08 | 2.05 |
| E6 | sal | 3.86 | 3.86 | 3.86 | 3.56 | 3.56 | 3.50 | 3.55 |
| E7 | ent | 3.38 | — | 2.88 | 3.48 | 2.88 | 2.90 | 3.15 |
| E7 | sal | 5.58 | 5.18 | 4.28 | 5.18 | 4.28 | 4.18 | 4.70 |
| E8 | ent | 3.38 | — | 3.88 | 3.88 | 3.88 | 4.05 | 4.60 |
| E8 | sal | 5.68 | — | 7.48 | 7.28 | 7.28 | 6.53 | 6.95 |
| E9 | ent | 2.08 | 2.08 | 1.77 | 2.08 | 1.77 | 1.55 | 1.55 |
| E9 | sal | 2.88 | 2.78 | 2.68 | 2.78 | 2.68 | 2.43 | 2.45 |
| E10 | ent | 2.08 | 2.08 | 1.77 | 2.08 | 1.77 | 1.55 | 1.55 |
| E10 | sal | 3.05 | 3.05 | 3.05 | 2.85 | 2.85 | 2.81 | 2.85 |

Notas: «—» en la columna 4 = ningún B ≤ 1.5·H_c (el tope de la app) cumple; las columnas
5 a 8 buscan hasta 3·H_c, de modo que un valor mayor que 1.5·H_c (E7-ent, E8) también
significa «no cabe en el tope». Las columnas 4 a 8 usan el peralte FINAL de la app; la 9
es mi diseño congelado, con mi peralte (0.40–0.55 m), por eso puede diferir de la 8.
Columnas 4→5: efecto de la fila de φ (H-7); 4→6: efecto de la altura del incremento
sísmico (H-9); 7→8: efecto de la punta fija y de la malla (H-5); 3→4: efecto de que el
ancho no baje cuando el peralte crece (H-12).

### Tabla Z — espesor de zapata NECESARIO para la planta de la app (mi motor, cortante general 5.7.3.4.2 donde el simplificado no aplica)

| Esc. | Ext. | e_z app | talón con PESO ENTERO + cortante general | talón con método más exacto + cortante general | M talón peso entero / exacto (kN·m/m) |
|---|---|---|---|---|---|
| E1 | ent | 0.40 | 0.40 | 0.40 | 78 / 27 |
| E1 | sal | 0.80 | 0.45 | 0.40 | 276 / 96 |
| E2 | ent | 1.00 | 0.50 | 0.40 | 350 / 95 |
| E2 | sal | 1.35 | 1.35 | 0.45 | 1205 / 319 |
| E3 | ent | 1.00 | 0.50 | 0.45 | 363 / 105 |
| E3 | sal | 1.21 | 1.20 | 0.45 | 1022 / 348 |
| E4 | ent | 0.40 | 0.40 | 0.40 | 134 / 31 |
| E4 | sal | 1.40 | 1.15 | 0.40 | 960 / 113 |
| E5 | ent | 0.40 | 0.40 | 0.40 | 119 / 30 |
| E5 | sal | 1.70 | 1.65 | 0.45 | 1510 / 115 |
| E6 | ent | 0.40 | 0.40 | 0.40 | 154 / 66 |
| E6 | sal | 1.05 | 0.85 | 0.40 | 613 / 254 |
| E7 | ent | 1.00 | 0.50 | 0.40 | 332 / 49 |
| E7 | sal | 1.70 | 1.60 | 0.50 | 1500 / 188 |
| E8 | ent | 1.00 | 0.45 | 0.40 | 314 / 34 |
| E8 | sal | 1.70 | 1.65 | 0.50 | 1510 / 115 |
| E9 | ent | 0.40 | 0.40 | 0.40 | 78 / 27 |
| E9 | sal | 0.70 | 0.45 | 0.40 | 224 / 92 |
| E10 | ent | 0.40 | 0.40 | 0.40 | 78 / 27 |
| E10 | sal | 0.80 | 0.45 | 0.40 | 269 / 96 |

La columna 4 es la regla de la app (peso entero) con el cortante general en vez del salto
«A2-NV»: la diferencia con la 3 es lo que cuesta no implementar 5.7.3.4.2; la diferencia
entre la 4 y la 5 es lo que cuesta el peso entero. Los momentos de peso entero de mi motor
reproducen los de la app (E2-sal 1 205.1 = 1 205.1; E5-sal 1 510 contra 1 514 kN·m/m).

### Tabla M — barridos de monotonía (variantes de E1 con UNA entrada cambiada; B y e_z de la app)

**(a) Altura de la salida por la socavación declarada (`profundidad_socavacion_estimada_m`)**

| socavación (m) | H_c sal | B sal | e_z sal | E no cumple | A no cumple | bloqueos |
|---|---|---|---|---|---|---|
| 0.0 | 2.939 | 2.457 | 0.404 | — | — | — |
| 0.3 | 3.049 | 2.534 | 0.404 | — | A1.alero, A1.pantalla | — |
| 0.6 | 3.349 | 2.644 | 0.404 | — | A1.alero, A1.pantalla | — |
| 0.9 | 3.649 | 2.854 | 0.704 | — | A1.alero, A1.pantalla | — |
| 1.2 | 3.949 | 3.164 | 0.804 | — | A1.alero, A1.pantalla | — |
| 1.5 | 4.249 | 3.374 | 0.825 | — | A1.alero, A1.pantalla, A3.alero, A3.pantalla, A4.alero, A4.pantalla, A6.alero, A6.pantalla | — |
| **1.8** | **4.549** | **3.284 ↓** | 0.855 | — | A1.alero, A1.pantalla, A2.alero, A2.pantalla, A6.alero, A6.pantalla | sísmica salida no evaluable |
| 2.1 | 4.849 | 3.594 | 0.885 | — | A1.alero, A1.pantalla, A2.alero, A2.pantalla, A3.alero, A3.pantalla, A4.alero, A4.pantalla, A6.alero, A6.pantalla | sísmica salida no evaluable |
| 2.4 | 5.149 | 4.104 | 1.015 | — | A1.alero, A1.pantalla, A2.alero, A2.pantalla, A3.alero, A3.pantalla, A4.alero, A4.pantalla, A6.alero, A6.pantalla | sísmica salida no evaluable |

**(b) φ de la fundación (arena, γ 18)**

| φ_f (°) | B ent | e_z ent | B sal | e_z sal | E no cumple | A no cumple | bloqueos |
|---|---|---|---|---|---|---|---|
| 26 | 2.475 | 0.404 | 5.179 | 1.504 | — | — | — |
| 28 | 2.375 | 0.404 | 3.779 | 1.004 | — | A1.alero, A1.pantalla | — |
| 30 | 2.175 | 0.404 | 3.279 | 0.904 | — | A1.alero, A1.pantalla | — |
| 32 | 2.075 | 0.404 | 3.079 | 0.804 | — | A1.alero, A1.pantalla | — |
| 34 | 1.975 | 0.404 | 2.879 | 0.704 | — | A1.alero, A1.pantalla | — |
| 36 | 1.875 | 0.404 | 2.679 | 0.704 | — | A1.alero, A1.pantalla | — |
| 38 | 1.775 | 0.404 | 2.679 | 0.704 | — | A1.alero, A1.pantalla | — |

**(c) PGA (clase C, con reducción)**

| PGA (g) | B ent | B sal | e_z sal | E no cumple | A no cumple | bloqueos |
|---|---|---|---|---|---|---|
| 0.1 | 2.075 | 2.879 | 0.704 | — | A1.alero, A1.pantalla | — |
| 0.2 | 2.075 | 2.879 | 0.704 | — | A1.alero, A1.pantalla | — |
| 0.3 | 2.075 | 2.879 | 0.704 | — | A1.alero, A1.pantalla | — |
| 0.4 | 2.075 | 2.879 | 0.704 | — | A1.alero, A1.pantalla | — |
| 0.45 | 2.075 | 2.879 | 0.704 | — | A1.alero, A1.pantalla | — |
| 0.5 | 2.075 | 3.079 | 0.804 | — | A1.alero, A1.pantalla | — |

**(d) φ del relleno (drenado)**

| φ_r (°) | B ent | B sal | e_z sal | E no cumple | A no cumple | bloqueos |
|---|---|---|---|---|---|---|
| 30 | 2.375 | 3.379 | 0.904 | — | A1.alero, A1.pantalla | — |
| 32 | 2.175 | 3.179 | 0.804 | — | A1.alero, A1.pantalla | — |
| 34 | 2.075 | 3.079 | 0.804 | — | A1.alero, A1.pantalla | — |
| 36 | 1.975 | 2.879 | 0.704 | — | A1.alero, A1.pantalla | — |
| 38 | 1.775 | 2.779 | 0.704 | — | A1.alero, A1.pantalla | — |

**(e) Cohesión de la fundación (arcilla, φ = 0)**

| c_u (kPa) | B ent | B sal | e_z sal | E no cumple | A no cumple | bloqueos |
|---|---|---|---|---|---|---|
| 30 | 2.375 | 5.679 | 1.704 | E1-LRFD.est.s, E1-LRFD.sis.s, E3-LRFD.sis.s | — | — |
| 40 | 2.375 | 5.679 | 1.704 | E1-LRFD.est.s | — | — |
| 50 | 2.375 | 3.279 | 0.904 | — | A1.alero, A1.pantalla | — |
| 60 | 2.375 | 3.279 | 0.904 | — | A1.alero, A1.pantalla | — |
| 80 | 2.375 | 3.279 | 0.904 | — | A1.alero, A1.pantalla | — |
| 100 | 2.375 | 3.279 | 0.904 | — | A1.alero, A1.pantalla | — |

**(f) Profundidad del freático bajo el terreno del cruce (`NF_profundidad_m`)**

| NF (m) | B sal | e_z sal | E no cumple | A no cumple | bloqueos |
|---|---|---|---|---|---|
| 5.0 | 2.879 | 0.704 | — | A1.alero, A1.pantalla | — |
| 4.0 | 2.979 | 0.804 | — | A1.alero, A1.pantalla | — |
| 3.5 | 2.979 | 0.804 | — | A1.alero, A1.pantalla | — |
| 3.0 | 3.079 | 0.804 | — | A1.alero, A1.pantalla | — |
| 2.8 | 3.079 | 0.804 | — | A1.alero, A1.pantalla | — |
| 2.6 | 3.079 | 0.804 | — | A1.alero, A1.pantalla | — |
| **2.4** | **2.979 ↓** | 0.804 | — | A1.alero, A1.pantalla | sísmica salida no evaluable |
| 2.2 | 2.979 | 0.804 | — | A1.alero, A1.pantalla | sísmica salida no evaluable |
| 2.0 | 3.179 | 0.804 | — | A1.alero, A1.pantalla | sísmica salida no evaluable |
| 1.5 | 3.379 | 0.904 | — | A1.alero, A1.pantalla | sísmica salida no evaluable |
| 1.0 | 3.779 | 1.004 | — | A1.alero, A1.pantalla | sísmica salida no evaluable |


### Tabla P — demanda de la pantalla: la regla de la app contra una cuña sobre la pantalla

Con la planta y el peralte de la app, Resistencia I, empuje activo (kN·m/m). La columna (b)
reproduce exactamente lo que la app imprime con el régimen «cedente» cuando rige
Resistencia I (E1-ent, E3-sal, E9): es su regla de T7C-12. Script:
`diseno_mano/pantalla_plano_truncado.py`.

| Esc. | Ext. | e_z app | altura de la pantalla | suelo contra la pantalla (z_rel − e_z) | altura del diagrama de la app (h − e_z) | (a) cuña sobre la pantalla, Res I | (b) plano truncado, Res I | (c) app 'cedente', la que rige |
|---|---|---|---|---|---|---|---|---|
| E1 | ent | 0.404 | 1.85 | 1.70 | 2.32 | 18.0 | 27.6 | 27.6 (Resistencia I (maximos) |
| E1 | sal | 0.804 | 3.02 | 2.87 | 3.69 | 62.7 | 85.4 | 104.6 (Evento Extremo I, 100%) |
| E2 | ent | 1.004 | 1.57 | 1.42 | 2.62 | 12.5 | 50.3 | 65.2 (Evento Extremo I, 100%) |
| E2 | sal | 1.351 | 3.16 | 3.01 | 4.77 | 79.6 | 201.1 | 273.8 (Evento Extremo I, 100%) |
| E3 | ent | 1.004 | 1.90 | 1.75 | 2.93 | 20.5 | 61.5 | 77.6 (Evento Extremo I, 100%) |
| E3 | sal | 1.210 | 3.89 | 3.74 | 5.29 | 138.4 | 262.5 | 262.5 (Resistencia I (maximos) |
| E6 | ent | 0.404 | 2.17 | 2.02 | 2.82 | 29.3 | 65.1 | 82.4 (Evento Extremo I, 100%) |
| E6 | sal | 1.051 | 3.46 | 3.31 | 4.57 | 101.7 | 199.0 | 270.2 (Evento Extremo I, 100%) |
| E9 | ent | 0.404 | 1.85 | 1.70 | 2.32 | 18.0 | 27.6 | 27.6 (Resistencia I (maximos) |
| E9 | sal | 0.704 | 3.12 | 2.97 | 3.79 | 68.0 | 91.5 | 91.5 (Resistencia I (maximos) |

En E2-ent el diagrama con que la app carga la pantalla mide 2.62 m sobre una pantalla de
1.57 m: 1.05 m de presión actúan por encima de la corona del muro.

### Tabla V — el motor de estabilidad de la app, contra el mío

Con la geometría final de la app y **sus** criterios cargados en mi motor
(`diseno_mano/verificar_app.py`, copia parametrizada del motor congelado: φ 0.45/0.80 en
arena y 0.50/0.85 en arcilla, incremento sísmico a 0.6 h), las 111 filas E1/E2/E3
evaluables de los 20 cabezales coinciden con las de la app: **estáticas, diferencia
máxima de uso 0.009 (media 0.0006); sísmicas, 0.041 (media 0.005)**, siempre con mi motor
del lado más exigente y solo en la portante sísmica (E6 entrada 0.545 contra 0.586). Y
reimplementando el procedimiento de la app (crece solo el talón desde 0.7·H_c, paso 0.10,
punta 0.33·B_regla, peralte final) **reproduzco su B exacto en 9 de los 20 cabezales y
coincido en otros 4 en que ningún B ≤ 1.5·H_c cumple** (E5-sal, E7-ent, E8-ent, E8-sal);
en 6 la app da 0.10–0.40 m MÁS porque dimensionó el ancho con la zapata de 0.404 m y,
cuando después el peralte creció, el ancho ya no baja (Tabla A, columna 4), y en E3-sal
da 0.80 m MENOS porque omitió el sismo (H-3).
Conclusión: **no hay error aritmético en empujes, combinaciones ni E1–E3**; las
diferencias con mi diseño son de criterio y de procedimiento.

### Tabla R — resumen por cabezal

«Cumple»: la geometría final cumple TODAS las verificaciones de la app (estabilidad, zapata,
pantalla y alero). «Razonable»: B/H_c y e_z/H_c dentro de lo que pide un diseño correcto
(mi diseño + 0.15 m en B; e_z ≤ max(0.55 m, H_c/8)). «Monótono»: el par de la matriz o el
barrido no invierte el sentido. «Coincide»: |ΔB| ≤ 0.15 m y |Δe_z| ≤ 0.10 m.

| Esc. | Ext. | Cumple (app) | Razonable | Monótono | Coincide con mi diseño | Causa principal de la diferencia |
|---|---|---|---|---|---|---|
| E1 | ent | sí | B no (+0.53) | sí | no (B +34 %) | φ de la Tabla 10.5.5.2.2-1 (+0.30) y punta fija/paso 0.10 (+0.22) |
| E1 | sal | **no** (A1 pantalla) | **no** (e_z 0.80) | sí | no (e_z ×2) | peralte A2-NV (0.80 contra 0.45 con el cortante general) |
| E2 | ent | sí | **no** (e_z 1.00) | sí | no | e_z: A2-NV + talón con peso entero; B: φ y monotonía |
| E2 | sal | **no** (A1–A6 pantalla) | **no** (e_z 1.35) | sí | no | talón con peso entero (1205 contra 319 kN·m/m) |
| E3 | ent | **no** (A1 pantalla) | **no** (e_z 1.00) | sí | no | A2-NV + peso entero |
| E3 | sal | **no** (A1–A6 pantalla; sismo sin evaluar) | **no**: B corto para el sismo, e_z 1.21 | **no** (agua) | no (B −10 %) | sismo saltado por 0.26 m de agua: con él, B 5.05–5.37 |
| E4 | ent | sí | B no (+0.53) | sí | no (+27 %) | φ (+0.40) y punta fija |
| E4 | sal | sí (gracias a e_z 1.40) | **no** (e_z 1.40) | sí | no | peso entero (960 contra 113 kN·m/m) |
| E5 | ent | sí | B no (+0.43) | sí | no (+22 %) | φ y punta fija |
| E5 | sal | **no** (E1 est en el tope) | **no** (5.68 × 1.70) | sí (falla en el tope) | no (+89 %) | crece solo el talón en arcilla + A2-NV en el tope |
| E6 | ent | **no** (A1 pantalla) | B no (+0.45) | sí | no (+22 %) | φ y punta fija |
| E6 | sal | **no** (A1–A6 pantalla) | **no** (e_z 1.05) | sí | no | e_z peso entero; B incremento a 0.6 h |
| E7 | ent | **no** (E3 est en el tope; sismo sin evaluar) | **no** (e_z 1.00) | sí | no (B +0.23; e_z ×2.5) | φ: con la Tabla 11.5.7-1 cumple con 2.88 m (aviso propio de la app) |
| E7 | sal | sí en estática (sismo sin evaluar) | **no** (e_z 1.70) | sí | no (+19 %) | peso entero + φ |
| E8 | ent | **no** (E3 sís en el tope) | — (hace falta B ≈ 2 H) | sí | — (los dos > 1.5 H) | k_h = 0.50: sin dentellón no hay zapata racional |
| E8 | sal | **no** (E1, E3 sís en el tope) | — | sí | — | ídem |
| E9 | ent | sí | B no (+0.53) | sí | no (+34 %) | φ y punta fija |
| E9 | sal | **no** (A1 pantalla) | e_z no (0.70) | sí | no | A2-NV |
| E10 | ent | sí | B no (+0.53) | sí | no (+34 %) | φ y punta fija |
| E10 | sal | **no** (A1 pantalla) | **no** (e_z 0.80; alero largo 13.1 m sin diseñar) | sí | no | A2-NV; aleros fuera de alcance |

Recuento: la geometría final de la app cumple todas sus verificaciones en **7 de 20
cabezales** (E1-ent, E2-ent, E4-ent, E4-sal, E5-ent, E9-ent, E10-ent); la estabilidad
LRFD falla en 4 (E5-sal, E7-ent, E8-ent, E8-sal: los cuatro en el tope de 1.5·H_c) y
queda sin evaluar en sísmica en 3 (E3-sal, E7-ent, E7-sal), de modo que cumple con las
dos condiciones evaluadas en 14; el armado de la zapata cumple en los 20 (por
construcción del bucle del peralte) y la pantalla/alero en 12. **En ningún cabezal la geometría de la app coincide
con la mía**; en todos los «normales» es mayor.

---

## 6. Hallazgos, por severidad

Clasificación de cada uno: **D** = defecto del software (el programa hace algo que la
fuente o la estática no sostienen, o no hace lo que dice); **C** = criterio declarado (una
elección documentada, defendible, que este ensayo solo cuantifica); **R** = error o límite
mío. Entradas reproducibles en `/home/user/ensayos_cabezal_casos/` (§8).

### ALTA

**H-1 (D; VE3-05 abierto 2). La pantalla y el alero no se dimensionan: la app entrega
cabezales que no cumplen su propio armado en 8 de 20 casos.** La pantalla queda en 0.30 m
(regla `espesor_pantalla_voladizo_m`) para cualquier altura, y el bucle solo hace crecer
B y e_z. Resultado: A1 de la pantalla y del alero no cumple en E1-sal, E3-ent, E6-ent,
E9-sal, E10-sal, y A1–A6 no cumplen en E2-sal, E3-sal y E6-sal (Tabla C). Evidencia:
E1-sal, `A1.pantalla.s`: M_u = 232.1 kN·m/m (Evento Extremo I, 100 % P_AE + 50 % P_IR con
k_h = k_h0 = 0.50), A_s = 3 599 mm²/m, M_r = 253.4 ≥ M_u pero ε_t = 0.0022 < 0.005 (la app
exige sección controlada por tracción, y con 0.30 m no se puede); E2-sal, `A1.pantalla.s`: M_u =
630.5 contra M_r = 51.6 kN·m/m, «la sección no alcanza» (`E*/app_resumen.json`, clave
`armado`). En el barrido de altura (Tabla M-a) la pantalla de 0.30 m falla desde
**H_c ≥ 3.05 m**, es decir, en casi todo cabezal de salida. Con las cargas de la propia app
la pantalla necesitaría ≈ 0.40 m (E1-sal), 0.45 m (E3-sal), 0.50 m (E6-sal) y 0.55 m (E2-sal) (mi función de sección con el M_u de la app); con las mías (activo, k_h
reducido), 0.30–0.40 m (Tabla 3.1). Y hay un efecto perverso: en E4-sal, E5-sal, E7-sal y
E8-sal la pantalla «cumple» **solo porque la zapata engordó a 1.40–1.70 m y la pantalla
quedó más corta**; con el cortante verificable (corrida `*_wi_cortante`, zapata 0.90–1.20 m)
las cuatro vuelven a no cumplir A1. La app lo avisa (el expediente no cierra) pero no
propone el espesor: no es un diseño terminado.

**H-2 (D + C; VE3-05 abierto 1). El peralte de la zapata sale hasta 4.3 veces mayor que el
necesario: 0.70–1.70 m (e_z/H_c hasta 0.45) frente a 0.40–0.55 m.** Dos causas que se
multiplican:
* **(D) El salto «A2-NV».** En cuanto la zapata pasa de 0.404 m (< 16 in) a 0.504 m, el
  simplificado de 5.7.3.4.1 deja de aplicar salvo que el vuelo sea < 3·d_v, y como el
  general de 5.7.3.4.2 no está implementado, **cada peralte intermedio se rechaza sin que
  ninguna resistencia falle**; el bucle sigue hasta que 3·d_v supera el talón (E1-sal:
  0.504 → 0.604 → 0.704 «sin verificar» → 0.804). Con el procedimiento general (que mi
  motor sí aplica: β de la ec. 5.7.3.4.2-2 con ε_s de la ec. 5.7.3.4.2-4 y s_xe con a_g = 3/4 in), las
  mismas cargas y la misma planta de la app piden **0.45–0.50 m donde la app da 0.70–1.00
  m** (E1-sal, E2-ent, E3-ent, E7-ent, E8-ent, E9-sal, E10-sal; Tabla Z). AASHTO
  5.7.3.4.1 (pág. 5-70, PDF 429) da el β = 2 como un «may be used» y 5.7.3.4.2 es el
  procedimiento general: no verificar no es lo mismo que no cumplir.
* **(C) El talón con el «peso entero» de 11.6.1.2.** Rige siempre el talón cargado con
  todo lo que tiene encima sin descontar la reacción (`M9._talon_con_el_peso_entero`; el
  método exacto se imprime y no rige, y no hay criterio para elegirlo). AASHTO lo permite
  «unless a more exact method is used» (pág. 11-20, PDF 1489), pero con el talón que el
  propio bucle alarga para la estabilidad (2.5–4.5 m) el momento de peso entero es **2.4 a
  13 veces el exacto** (E5-sal 1 510 contra 115 kN·m/m; E4-sal 960 contra 113; E2-sal 1 205
  contra 319) y obliga a 0.85–1.65 m donde el método exacto pide 0.40–0.50 m (Tabla Z).
  Caltrans BDP 11.2 (ejemplo resuelto en `Normas/ejemplos_resueltos/cabezal_muros/`)
  diseña el talón con la reacción del terreno.

  Consecuencia: concreto +13 % a +363 % por metro de muro (Tabla G); la zapata gruesa
  esconde fallas de pantalla (H-1) y empeora el portante en arcilla (H-5). No es inseguro,
  pero no es un buen diseño. **Quién tiene razón:** en el salto A2-NV, mi diseño (5.7.3.4.2
  es el procedimiento de la fuente para esas secciones); en el peso entero, las dos
  lecturas caben en la letra de 11.6.1.2, pero la de la app deja de ser razonable con los
  talones largos que su propio bucle genera.

### MEDIA

**H-3 (D). Con cualquier lámina de agua en el plano de empuje, la condición sísmica se
salta y el ancho se dimensiona solo con la estática; el resultado deja de ser monótono.**
`M9.cargas_del_cabezal` levanta «método no evaluable» si h_w > TOL (relleno drenado,
freático natural sobre la base). En E3-sal hay **0.257 m de agua bajo 6.0 m de plano**: la
app da B = 4.57 m, y con esa geometría mi motor (con SUS criterios) da un uso sísmico de
portante de **1.76** (1.36 con los míos); el B necesario es 5.37 m con sus criterios y 5.05
m con los míos (Tabla A). El tratamiento del agua que pide C11.6.5.3 (PDF 1500: peso total
del suelo saturado, o la presión hidrodinámica) es despreciable a esa escala (Westergaard
≈ 7/12·k_h·γ_w·h_w² ≈ 0.1 kN/m). Monotonía rota: al bajar la socavación de 1.5 a 1.8 m
(H_c 4.25 → 4.55 m) B **baja** de 3.374 a 3.284 m, y al subir el freático de 2.6 a 2.4 m B
baja de 3.079 a 2.979 m (Tablas M-a y M-f). La app lo declara como `Bloqueo` y el
expediente no cierra, pero el ancho sale rotulado «dimensionada por estabilidad». Además,
el mensaje del bloqueo recomienda declarar `drenaje_trasdos = 'drenado'`, que ya está
declarado (texto engañoso).

**H-4 (D/C; T7C-12 lo llama «cota superior»). La pantalla se carga con el diagrama del
plano virtual del talón truncado en la zapata, no con el empuje sobre su propia cara.** El
diagrama integra presión sobre una altura h − e_z que incluye lo que el talud sube por
encima del relleno retenido junto a la pantalla (h − z_rel, que crece con el talón). Con
la geometría de la app y el mismo régimen activo, la pantalla recibe **1.5 a 4 veces** el
momento de una cuña de tanteo sobre la pantalla (E1-ent 27.6 contra 18.0; E2-ent 50.3
contra 12.5; E2-sal 201 contra 80; E3-sal 262 contra 138 kN·m/m: reproduje los valores de la
app con su regla en E1, E3 y E9, script
`diseno_mano/pantalla_plano_truncado.py`, Tabla P). La presión por encima de la corona del relleno actúa sobre el plano
virtual, no sobre el concreto; y acopla la demanda de la pantalla al largo del talón que
el dimensionamiento hace crecer. Sumado a K0 + k_h0 (H-8), explica la mayoría de los A1 de
H-1. **Quién tiene razón:** la cuña sobre la pantalla, que es la presión que actúa sobre el
concreto y lo que hace el ejemplo resuelto de Caltrans BDP 11.2 (pág. 11.2-27/28, PDF
27-28: «Soil pressure is obtained by performing a trial wedge analysis along AB», la cara
de la pantalla, con P_A a 1/3 de AB); la regla de la app es una cota superior que no hace
falta y que penaliza a los muros altos.

**H-5 (D). Solo crece el talón (la punta queda en 0.33·B_regla): en arcilla el bucle no
encuentra solución aunque exista, y en los demás casos el ancho sale 0.2–0.4 m mayor.**
En suelo cohesivo el portante no crece con B (no hay término N_γ) y alargar el talón suma
carga: en E5-sal ningún B ≤ 1.5·H_c cumple E1 estático. Con la Tabla 11.5.7-1 (φb 0.55) y
la punta libre la zapata de 3.00 m × 0.40 m cumple (mi diseño, punta 0.90 m); con los
criterios de la app (φb 0.50) no hay zapata corrida que cumpla, y lo correcto sería
decirlo, no entregar 5.68 × 1.70 m (H-6). En arena, la punta libre ahorra hasta 0.40 m de B (0.18–0.40 m en E1/E4/E9/E10-ent y
E4/E9-sal; Tabla A, columnas 7 y 8, parte por la malla de 0.05 m).

**H-6 (D). En el tope de 1.5·H_c el bucle sigue: el peralte crece por «A2-NV», el ancho se
«re-dimensiona» en el tope en cada vuelta y la geometría final es absurda y sigue sin
cumplir.** E5-sal: 14 intentos idénticos en 5.679 m, peralte 0.404 → 1.704 m, E1 sigue en
135.8 > 98.4 kPa (y la zapata gruesa la empeora: con la misma planta y 0.40 m de
peralte el uso sería 1.30 en vez de 1.38). E7-ent y
E8-ent terminan en 3.375 × 1.004 m sin cumplir. El aviso del tope es correcto, pero la
geometría entregada no es un diseño: debería detenerse en la última geometría con sentido
y declarar «zapata corrida no factible con estos criterios».

**H-7 (C). Factores de resistencia de zapatas (Tabla 10.5.5.2.2-1: 0.45/0.80) en vez de
los de muros (Tabla 11.5.7-1: 0.55/1.0).** 11.5.7 (pág. 11-15, PDF 1484): «the resistance
factors provided in Table 11.5.7-1 **shall be used for wall design**»; la Tabla 11.5.7-1
(pág. 11-17, PDF 1486) da 0.55 y 1.0 a «gravity and semigravity walls», y el Manual de
Puentes (PDF 511, 2.11.8.5) remite a ella para muros permanentes. La app lo sabe y lo elige
a propósito (`fila_phi_estabilidad_cabezal` [A], ficha T7B-09) y avisa la sensibilidad
(E7-ent: «con 'muros_tabla_11_5_7' 61.37 contra 76.40, cumple»). Efecto medido: −0.10 a
−0.90 m de B (típicamente −0.30 m) en los casos que gobierna el deslizamiento estático
(Tabla A, col. 5 contra col. 4). Es
conservador; recomiendo que el valor de archivo sea el de la letra para muros. **Quién
tiene razón:** la letra de 11.5.7 está de mi lado; la app es más exigente y lo declara.

### BAJA

**H-8 (C). Régimen incoherente entre estabilidad y armado.** La estabilidad admite el
desplazamiento (k_h = 0.5·k_h0, muro que cede) y la pantalla se arma como muro que no cede
(K0 en Resistencia I; k_h = 1.0·k_h0 y resultante a h/2 o incremento a 0.6 h en Evento
Extremo, `regimen_resistencia_elementos_cabezal = no_cedente_k0`, T7C-02). Los dos son
lecturas defendibles de 11.6.5.2.2 y C11.6.5.4 (PDF 1497 y 1501: «abutment walls with
structural wing walls» pueden no ceder), pero no a la vez sobre el mismo muro. Con
`cedente` la pantalla de 0.30 m pasa en E1, E9 y E10 (corrida `*_wi_cedente`).

**H-9 (C). Incremento sísmico a 0.6·h.** `punto_aplicacion_incremento_sismico` [C] = 0.6
(práctica de Seed y Whitman); la 9.ª ed. pide distribuir P_AE «using the same
distribution as the static earth pressure ... but no less than H/3» (11.6.5.3, pág.
11-30, PDF 1499) y su comentario sugiere a lo sumo 0.4–0.5 h para el total. Efecto: +0.20 a
+0.30 m de B en los cabezales que gobierna la portante sísmica (E1, E2, E3, E6, E10
salida; Tabla A, col. 6). **Quién tiene razón:** la especificación (h/3) está de mi lado;
el comentario admite subir el total a 0.4–0.5 h, y la app queda en ese rango o por encima.

**H-10 (D). El «alcance declarado» dice que el ancho NO se itera, y desde VE-3.5 se
itera.** `src/modelos.py:2520-2526` (`ALCANCE_DECLARADO`, clave
`iteracion_ancho_zapata_cabezal`): «El ancho de la zapata del cabezal no se itera: ... la
iteración espera los parámetros reales del EMS (ficha T7B-09)». Se imprime en la CLI, en
`alcance.declarado` del JSON y en la memoria (verificado en E1), a la vez que la misma
memoria muestra el paso 9.3.d «dimensionada por estabilidad»; `tests/test_t10_memoria.py:435`
fija la clave, de modo que la suite mantiene el texto falso. También el docstring de
`servicio._fase_9_armado` («no se itera ninguna dimensión»).

**H-11 (D). La traza del dimensionamiento no está en el JSON.** `intentos_de_zapata`,
`intentos_de_peralte` y los pasos F9.DIMENSIONADO / F9.DIMENSIONADO_PERALTE solo salen en
la memoria HTML; el JSON trae el origen «dimensionada por estabilidad/armado» sin los
intentos. Quien audite por el JSON no ve por qué la zapata creció. Y el RESUMEN de la CLI
atribuye el bloqueo sísmico a «un criterio sin valor» cuando es un «método no evaluable».

**H-12 (D). El ancho no baja cuando el peralte crece.** El bucle es monótono por diseño
(«el ancho solo crece»), pero el ancho se dimensionó con la zapata de 0.404 m: con la
zapata final (más pesada) bastaba 0.10–0.40 m menos (E2-ent 3.30 → 3.00; E3-ent 3.33 →
3.03; E7-sal 5.58 → 5.18; Tabla A, col. 4).

**H-13 (C, fuera de alcance declarado). Aleros sin diseñar, y con esviaje alto miden
13 m.** Con esviaje 45° (E10) el alero largo mide 8.11 m en la entrada y **13.12 m** en la
salida (normal al eje, α = 30°), se arma con la sección de la pantalla en su arranque y
hereda la zapata del cabezal; su estabilidad no se calcula (T7C-04, T7A-03). Es el elemento
más grande del cabezal y queda sin diseño.

**H-14 (C). La salida se funda bajo la hoya de socavación sin proteger + 0.61 m, y además
lleva el enrocado de la Fase 6.** Eso lleva el cabezal de salida de 2.25 a 3.83 m (E1) y a
5.10 m (E3) y es lo que lo pone en la zona donde fallan la pantalla (H-1) y el peralte
(H-2). Es un criterio [C] con ventana (`margen_zapata_bajo_socavacion_m`, 0–0.61 m, y la
hoya es la de HEC-14 sin protección); con el delantal de enrocado diseñado, fundar bajo la
hoya no protegida es doble protección. Lo anoto sin severidad de defecto.

### Lo que NO es defecto (y conviene decirlo)

* **El motor de estabilidad es correcto** (Tabla V): empujes por cuña de tanteo,
  combinaciones de 11.6.5.1 con P_IR del suelo sobre el talón, η = 1.05 en Resistencia I,
  E1 con B' y factores de inclinación, E2 y E3, coinciden con mi motor independiente a
  0.009 en estática y 0.041 en sísmica.
* **Es monótono** frente a φ de fundación, φ del relleno, cohesión y PGA (Tablas M-b a M-e)
  y frente a la altura mientras no entra agua al plano (M-a hasta 1.5 m de socavación).
* **No da falsos «cumple»**: en el tope (E5, E7, E8) dice que no cumple y por qué; en E8
  (k_h = 0.50) mi diseño confirma que hacen falta B ≈ 1.8–2.0·H_c, irracional sin
  dentellón.
* **Mis propios límites (R):** no diseñé los aleros ni la estabilidad global (E4/E5), como
  la app; mi pantalla es la de un muro que cede: si el Propietario la declara «no cedente»
  (C11.6.5.4) mi pantalla de E1-sal (Ø3/4" @ 0.15, M_r ≈ 126 kN·m/m) cubre el reposo
  estático (107 kN·m/m) pero quedaría justa con k_h0 en Evento Extremo. No encontré un
  error mío que cambie una conclusión; la única corrección que hice a mi motor (antes del
  sello) fue evaluar el sismo con agua residual en E3-sal.

---

## 7. Veredicto

Las cuatro preguntas del encargo:

* **(a) ¿La geometría final cumple sus verificaciones de estabilidad y de armado de la
  zapata?** La zapata, sí en los 20 (punta y talón A1–A6, por construcción). La
  estabilidad LRFD, en 16 de 20 en lo que evalúa (falla en el tope en E5-sal, E7-ent,
  E8-ent y E8-sal, y lo dice) y queda sin evaluar en sismo en 3. El cabezal COMPLETO
  cumple solo en 7 de 20: la pantalla y el alero fallan en 8.
* **(b) ¿Es razonable o está sobredimensionada?** El ancho es razonable a algo holgado
  (B/H_c 0.75–1.3; +7 a +34 % sobre el mío, explicado por criterios declarados y por el
  talón como única variable). El peralte está muy sobredimensionado: 0.70–1.70 m (e_z/H_c
  0.18–0.45) contra 0.40–0.55 m (≈ H/10 o el mínimo de E.060 15.7); concreto +13 % a +363 %.
  La punta (0.33·B_regla) es mayor de lo que hace falta y no se ajusta.
* **(c) ¿Es monótona?** Sí frente a φ, cohesión, PGA y altura sin agua; **no** cuando el
  freático entra al plano de empuje (el sismo se omite y B baja: Tablas M-a y M-f).
* **(d) ¿Coincide con mi diseño?** No en ningún cabezal: el motor de estabilidad sí
  coincide (Tabla V), pero B difiere entre −27 % y +89 % y e_z entre ×1 y ×4.3; las
  causas, una por una, en la Tabla A, la Tabla Z y la Tabla P.

**No: hoy la app no produce buenos diseños de cabezal, aunque sí produce diseños
estables y del lado seguro en lo que evalúa.** Su núcleo de estabilidad es correcto y su
ancho de zapata es razonable en el orden de magnitud (B/H_c 0.75–1.3 en los casos
normales, 7–34 % mayor que el mío salvo E5-sal, +89 %, y E3-sal, −10 % por el sismo
omitido; casi todo por dos criterios conservadores declarados:
los φ de zapatas en vez de los de muros y el incremento sísmico a 0.6 h, más el talón como
única variable). Pero el producto final no es un diseño entregable: (1) la pantalla y el
alero no se dimensionan y fallan su armado en 8 de 20 cabezales —en todos los de salida
de H_c ≳ 3 m salvo donde la zapata engordó tanto que acortó la pantalla—, en parte porque
la pantalla se carga con presiones que actúan por encima de su corona; (2) el peralte de la zapata sale de 0.70 a 1.70 m —hasta el 45 % de la
altura del muro y 2–4 veces lo necesario— porque los peraltes que el programa no sabe
verificar se tratan como si no cumplieran y porque el talón alargado se carga con el peso
entero; (3) con agua mínima en la base se omite el sismo y el ancho sale corto y no
monótono; (4) en arcilla o en el tope el bucle entrega geometrías absurdas que siguen sin
cumplir. Para que lo sea bastan cuatro cambios: implementar 5.7.3.4.2 (o dejar de
rechazar lo no verificado), usar el método exacto del talón, dimensionar la pantalla con
una cuña sobre su propia cara, y tratar el agua residual en el sismo; y revisar los dos
valores de archivo (φ de la Tabla 11.5.7-1 y P_AE a h/3) con el dueño.

---

## 8. Reproducibilidad

Entorno: `export PATH=/home/user/venv312/bin:$PATH NORMAS_DIR=/home/user/Normas`; clon
`/home/user/ensayos_cabezal` en `d78f2c4`. Desde `/home/user/ensayos_cabezal_casos/`:

| Paso | Comando | Produce |
|---|---|---|
| Escenarios y conducto (perfil) | `python herramientas/correr_perfil.py` | `<E>/puntos.csv`, `externos.json`, `sitio.json`, `declaraciones.json`, `salida_perfil.json` |
| Entradas del cabezal | `python herramientas/extraer_entradas.py` | `diseno_mano/entradas_geometricas.json` |
| Mi diseño (sin `src/`) | `python3 diseno_mano/diseno_mano.py` | `diseno_mano/diseno_mano.json` (congelado: `..._CONGELADO_antes_de_la_app.json`) |
| App a expediente (CLI) | `python herramientas/correr_expediente.py` | `<E>/salida_expediente.json`, `stdout_expediente.txt`, `comando_expediente.txt` |
| Traza y armado de la app | `python herramientas/extraer_app.py E1_referencia ...` | `<E>/app_resumen.json` |
| Contraste de motores y atribución | `cd diseno_mano && python3 verificar_app.py` | `verificacion_geometria_app.json` |
| Peralte necesario | `cd diseno_mano && python3 espesor_necesario.py` | `espesor_necesario_geometria_app.json` |
| Demanda de la pantalla | `cd diseno_mano && python3 pantalla_plano_truncado.py` | `tabla_pantalla.md` |
| ¿Qué pasaría si? (sin tocar `src/`) | `python herramientas/que_pasaria.py E1_referencia ... --cortante-simplificado --sufijo _wi_cortante`; `... --declarar "regimen_resistencia_elementos_cabezal='cedente'" --sufijo _wi_cedente` | `<E>/app_resumen_wi_*.json` |
| Monotonía | `python herramientas/barridos.py`; `python herramientas/barrido_nf.py` | `barridos/*.json` |
| Memoria HTML (E1) | `python herramientas/correr_html.py E1_referencia` | `E1_referencia/memoria_expediente.html` |

Normas leídas (texto extraído de los PDF de `NORMAS_DIR` con `normas_txt/extraer.py <pdf>
<salida.txt>`; los volcados se borraron al terminar por ser texto de normas con derechos): AASHTO LRFD 9.ª
11.5.7 y Tabla 11.5.7-1 (PDF 1484, 1486), 11.5.8 (1487), 11.6.1.2 (1489), 11.6.3.2–11.6.3.6
(1490–1493), 11.6.5.1–11.6.5.4 (1494–1501), 10.6.1.3 y C10.6.5 (1342, 1375), 10.6.3.1.2a
(1360), C3.11.5.3 (175), 5.7.3.4.1–2 (429), C5.12.8.6.1 (610); Manual de Puentes 2.11.8.5
(PDF 511); Caltrans BDP 11.2 (ejemplo resuelto).
