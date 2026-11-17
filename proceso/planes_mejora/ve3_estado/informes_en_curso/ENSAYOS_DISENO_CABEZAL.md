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
