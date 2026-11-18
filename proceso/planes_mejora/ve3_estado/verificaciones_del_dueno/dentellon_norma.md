# Dentellón de corte bajo la zapata del cabezal: qué dicen las fuentes y qué modelo implementar

Revisión independiente, 2026-11-18. No se modificó ningún repositorio. Los números del caso
resuelto salen de una exportación de `HEAD` (`2b06ef2`) corrida con el juego titular de la
validación integral (`tests.apoyo.validacion_integral.juego_titular()`), no del árbol de trabajo,
que tiene cambios de otros agentes en `M9_cabezal.py`.

## Resumen

1. **AASHTO LRFD 9.ª no nombra el dentellón de corte de un muro en ningún artículo ni comentario** de
   las Secciones 3, 10 y 11. «Shear key» aparece sólo para superestructura, MSE y roca (10.6.1.5).
   No existen los textos de C10.6.3.4 o C11.6.3.5 sobre «la falla por la base del dentellón»: el
   encargo los suponía y no están. Todo el modelo del dentellón es **[A]** apoyado en dos ejemplos.
2. Lo que sí es de la fuente: R_R = φ_τ·R_τ + φ_ep·R_ep (10.6.3.4-1, pág. 10-84); φ_ep = 0.50 en
   Resistencia (Tabla 10.5.5.2.2-1, pág. 10-42); 1.0 en Evento Extremo (11.5.8, pág. 11-18); el
   pasivo sólo cuenta bajo la socavación máxima (11.6.3.5, pág. 11-24).
3. En sismo el pasivo **no se ignora ni se calcula con Mononobe-Okabe**: con empotramiento menor de
   5.0 ft (1.524 m) vale el método estático de la Sección 3; desde 5.0 ft exige espiral logarítmica
   con inercia (11.6.5.5, págs. 11-32 y 11-33). Ese límite es el único tope de profundidad que da la
   fuente.
4. K_p: figuras de espiral logarítmica o teoría de cuña con δ ≤ φ/2 (3.11.5.4, pág. 3-124). Las dos
   agencias leen la misma figura para φ = 34° y δ = 2/3·φ y obtienen 7.05 (Caltrans) y 7.6 (CDOT):
   la lectura gráfica no es reproducible. Propongo Coulomb cerrado con δ [A] en [0, φ/2], por
   defecto 0 (Rankine).
5. Los dos ejemplos (Caltrans BDP 11.2 y CDOT Ej. 11) ponen el dentellón hacia el talón, son
   someros (0.23 y 0.30 m) y modelan distinto la superficie de falla. Ninguno lo usa para cerrar el
   sismo: Caltrans calcula P_PE = 8.0 kip y lo ignora; resuelve el sismo por desplazamiento (Newmark).
6. El Manual de Puentes transcribe 11.6.3.5, 10.6.3.4 y 11.6.5.5 (págs. 250 a 252, 256 y 257) y no
   menciona dentellón. La E.050 tampoco; su Figura 22 (pág. 72) da E_ps = 0.85·K_p·R·γ·D_f²/2.
7. **Incoherencia de fondo:** k_h = k_h0 sin reducir supone un muro que no se desplaza; el pasivo
   pleno necesita Δ/H de 0.01 a 0.04 (Tabla C3.11.1-1, pág. 3-117). Con un desplazamiento de 1 a 2 in
   la propia fuente permite k_h = 0.5·k_h0 (11.6.5.2.2, pág. 11-28). Con «sin reducción», lo
   coherente es φ_ep = 0.5 también en sismo.
8. **Caso A-01 (PGA 0.50 g, φ_f = 32°, γ = 18):** la salida necesita d = 1.80 m (Rankine, φ_ep = 1.0)
   o 2.55 m (φ_ep = 0.5): no cierra dentro de 1.524 m. La entrada necesita 0.70 m (φ_ep = 1.0) o
   1.17 m (φ_ep = 0.5).
9. **La portante sísmica (E1) también falla** en los dos cabezales de A-01 al tope (salida: 100.6
   contra 0.59 kPa). Con la regla del dueño el punto sale «no factible» con o sin dentellón, salvo
   que cambie `factores_inclinacion_carga_portante`.
10. El dentellón no debe ayudar a la portante ni a la excentricidad (los dos ejemplos lo ignoran
    ahí). No debe contarse con hoya sin estimar, suelo blando o suelto, roca ni gradiente de
    filtración bajo la zapata.

---

## 1. AASHTO LRFD 9.ª edición (2020)

PDF: `/home/user/Normas/normas/AASHTO.LRFD.Bridge.Design.Specifications_9th.Edition.2020.pdf`.
«Pág.» es la página impresa.

### 1.1 Deslizamiento: 10.6.3.4 (págs. 10-84 y 10-85; pág. PDF 1373)

- «If passive resistance is included as part of the shear resistance required for resisting sliding,
  consideration shall also be given to possible future removal of the soil in front of the
  foundation.»
- «RR = ϕRn = ϕτ Rτ + ϕep Rep (10.6.3.4-1)».
- «Rep = nominal passive resistance of soil available throughout the design life of the structure
  (kips)».
- «Rτ = CV tan φf (10.6.3.4-2)», con «C = 1.0 for concrete cast against soil; = 0.8 for precast
  concrete footing».
- C10.6.3.4: «Sliding failure occurs if the force effects due to the horizontal component of loads
  exceed the more critical of either the factored shear resistance of the soils or the factored
  shear resistance at the interface between the soil and the foundation.»
- C10.6.3.4: «In most cases, the movement of the structure and its foundation will be small.
  Consequently, if passive resistance is included in the resistance, its magnitude is commonly
  taken as 50 percent of the maximum passive resistance. This is the basis for the resistance
  factor, ϕep, in Table 10.5.5.2.2-1.»

El comentario no menciona dentellón ni superficie de falla por su base. La frase «the more critical
of either […] the soils or […] the interface» es el único apoyo de la fuente para comprobar un
plano suelo-suelo.

### 1.2 Factores de resistencia

- Tabla 10.5.5.2.2-1 (pág. 10-42), fila de deslizamiento: «Precast concrete placed on sand 0.90;
  Cast-in-Place Concrete on sand 0.80; Cast-in-Place or precast Concrete on Clay 0.85; Soil on soil
  0.90; ϕep Passive earth pressure component of sliding resistance 0.50».
- C10.5.5.2.2 (pág. 10-42): «The resistance factors for plate load tests and passive resistance were
  based on engineering judgment and past ASD practice.»
- Tabla 11.5.7-1 (pág. 11-17), bloque «Mechanically Stabilized Earth Walls, Gravity Walls, and
  Semigravity Walls»: «Sliding 1.0». **No tiene fila de pasivo** para estos muros; el φ_ep = 0.50
  viene de la Sección 10 (CDOT lo cita así).
- 11.5.8 (pág. 11-18): «Unless otherwise specified, all resistance factors shall be taken as 1.0
  when investigating the extreme event limit state. […] For bearing resistance, a resistance factor
  of 0.8 shall be used for gravity and semigravity walls».
- 10.5.5.3.3 (pág. 10-52): «Resistance factors for extreme limit state, including the design of
  foundations to resist earthquake, ice, vehicle or vessel impact loads, shall be taken as 1.0.»

### 1.3 Pasivo en muros: 11.6.3.5 y 11.6.3.6 (pág. 11-24; pág. PDF 1493)

- «Passive resistance shall be neglected in stability computations, unless the base of the wall
  extends below the depth of maximum scour, freeze–thaw, or other disturbances. In the latter case,
  only the embedment below the greater of these depths shall be considered effective.»
- «Where passive resistance is utilized to ensure adequate wall stability, the calculated passive
  resistance of soil in front of abutments and conventional walls shall be sufficient to prevent
  unacceptable forward movement of the wall.»
- «The passive resistance shall be neglected if the soil providing passive resistance is, or is
  likely to become soft, loose, or disturbed, or if the contact between the soil and wall is not
  tight.»
- C11.6.3.5: «Unacceptable deformations may occur before passive resistance is mobilized.
  Approximate deformations required to mobilize passive resistance are discussed in Article C3.11.1,
  where H in Table C3.11.1-1 is the effective depth of passive restraint.»
- 11.6.3.6: «The provisions of Article 10.6.3.4 shall apply.»

La fuente no da una profundidad fija que ignorar: es la mayor entre socavación máxima, helada y
«otras perturbaciones». Los «1 ft» y «2 ft» de los ejemplos son práctica de agencia.

### 1.4 Movimiento para movilizar el pasivo: C3.11.1 (pág. 3-117) y C3.11.5.4 (pág. 3-124)

- Tabla C3.11.1-1, «Values of Δ/H», columna «Passive»: «Dense sand 0.01; Medium dense sand 0.02;
  Loose sand 0.04; Compacted silt 0.02; Compacted lean clay 0.05; Compacted fat clay 0.05».
- C3.11.5.4: «The movement required to mobilize passive pressure is approximately 10.0 times as
  large as the movement needed to induce earth pressure to the active values. The movement required
  to mobilize full passive pressure in loose sand is approximately five percent of the height of
  the face on which the passive pressure acts.»

### 1.5 Coeficiente pasivo: 3.11.5.4 (págs. 3-124 a 3-127; figura en pág. PDF 180)

- «For noncohesive soils, values of the coefficient of passive lateral earth pressure may be taken
  from Figure 3.11.5.4-1 for the case of a sloping or vertical wall with a horizontal backfill or
  from Figure 3.11.5.4-2 […]. For conditions that deviate from those described in Figures 3.11.5.4-1
  and 3.11.5.4-2, the passive pressure may be calculated by using a trial procedure based on wedge
  theory, e.g., see Terzaghi et al. (1996). When wedge theory is used, the limiting value of the
  wall friction angle should not be taken larger than one-half the angle of internal friction, φf.»
- C3.11.5.4 (pág. 3-125): «Wedge solutions are inaccurate and unconservative for larger values of
  wall friction angle.»
- Suelos cohesivos: «pp = kp γs z + 2c √kp (3.11.5.4-1)».
- Figura 3.11.5.4-1 (pág. 3-126, U.S. Navy 1982a): espiral logarítmica, «NOTE: CURVES SHOWN ARE FOR
  δ/φf = −1», con la tabla «REDUCTION FACTOR (R) OF kp FOR VARIOUS RATIOS OF −δ/φf». Filas leídas de
  la imagen: φ = 30°: 0.878 (−0.7), 0.811 (−0.6), 0.746 (−0.5), 0.467 (0.0); φ = 35°: 0.836, 0.752,
  0.674, 0.362. La figura da «Pp = kp·γs·H²/2; PT = Pp SIN δ; PN = Pp COS δ».

No intenté digitalizar las curvas: no se leen con la precisión que un valor de proyecto pide.

### 1.6 Sismo: 11.6.5.1, 11.6.5.2.2, 11.6.5.5 y A11.4

- 11.6.5.1 (pág. 11-25): «The procedures specified in Article 11.6.3.7 for overall stability, Article
  11.6.3 for bearing stability, and Article 10.6.3.4 for sliding stability shall be used but
  including seismically induced earth pressure and inertial forces, using Extreme Event I limit
  state load and resistance factors as specified in Article 11.5.8.»
- 11.6.5.2.2 (pág. 11-28): «Where the wall is capable of displacements of 1.0 to 2.0 in. or more
  during the design seismic event, kh may be reduced to 0.5kh0 without conducting a deformation
  analysis using the Newmark method».
- 11.6.5.5 (págs. 11-32 y 11-33): «For estimating seismic passive earth pressures, wall friction and
  the deformation required to mobilize the passive resistance shall be considered and a log spiral
  design methodology shall be used. The M–O Method shall not be used for estimating passive seismic
  earth pressure.»
- 11.6.5.5: «[…] and for wall embedment greater than or equal to 5.0 ft, the inertial forces in the
  passive pressure zone in front of the wall from the earthquake. For wall embedment depths less
  than 5.0 ft, passive pressure should be calculated using the static methods provided in Section
  3.»
- 11.6.5.5: «In the absence of any specific guidance or research results for seismic loading, a wall
  interface friction equal to two-thirds of the soil friction angle should be used when calculating
  seismic passive pressures.»
- C11.6.5.5 (pág. 11-33): «The deformation to mobilize the passive earth pressure during static
  loading is usually assumed to be large—typically 2 percent to 6 percent of the embedded wall
  height. Similar guidance is not available for seismic loading and therefore the normal approach
  […] is to assume that the displacement to mobilize the seismic passive earth pressure is the same
  as for static loading.»
- A11.4 (págs. 11-149 a 11-151): cartas de K_pe por espiral logarítmica, «The interface friction for
  these charts is 0.67φ». Figura A11.4-2, c/γH = 0, leída de la imagen: φ = 32.5° baja de ≈ 5.8
  (k_h = 0) a ≈ 3.6 (k_h = 0.5); φ = 35°, de ≈ 6.9 a ≈ 4.6. El pasivo sísmico se reduce en torno
  al 35–40 % con k_h = 0.5.

Lectura: el pasivo sísmico **cuenta**, con φ = 1.0, pero (a) nunca con M-O, (b) con método estático
sólo si el empotramiento es menor de 1.524 m, (c) considerando la deformación que lo moviliza.

### 1.7 Socavación

- 10.6.1.2 (pág. 10-52): «Where the potential for scour, erosion or undermining exists, spread
  footings shall be located to bear below the maximum anticipated depth of scour, erosion, or
  undermining as specified in Article 2.6.4.4.»
- 2.6.4.4.2 (pág. 2-21): «Spread footings on soil or erodible rock shall be located so that the
  bottom of footing is below scour depths determined for the check flood for scour.»
- 12.6.5 (pág. 12-19): «For structures placed over erodible deposits, a cut-off wall or scour
  curtain, extending below the maximum anticipated depth of scour or a paved invert, shall be used.
  The footings of structures shall be placed not less than 2.0 ft below the maximum anticipated
  depth of scour.»
- 11.6.3.4 (pág. 11-24), gradiente hidráulico: «For silts and cohesive soils: 0.20; For other
  cohesionless soils: 0.30. Where water seeps beneath a wall, the effects of uplift and seepage
  forces shall be considered.»

`margen_zapata_bajo_socavacion_m` vale hoy 0.0, de modo que la base de la zapata de salida coincide
con el fondo de la hoya. El «not less than 2.0 ft» de 12.6.5 queda sin cumplir a la letra; la
revisión de VE-3.15 ya lo señaló (H2) y no es materia de este informe, pero condiciona el pasivo:
con margen 0 sólo el dentellón queda bajo la socavación.

---

## 2. Ejemplos resueltos con dentellón

### 2.1 Caltrans, Bridge Design Practice 11.2 (octubre 2022), ejemplo 11.2.2

PDF: `/home/user/Normas/ejemplos_resueltos/cabezal_muros/caltrans_bdp_11_2.pdf`.

- Geometría (Figura 11.2.2-1, pág. 11.2-13): muro de 23 ft, zapata B = 19 ft de 2.5 ft de espesor,
  punta de 5.5 ft, 2 ft de terreno sobre la zapata, «24″ X 9″ deep shear key» con su eje a 5 ft del
  borde del talón. φ_f = 34°, γ = 120 pcf, c = 0, HPGA = 0.7 g, k_h = 0.28.
- Pasivo (pág. 11.2-19): «It is typically assumed that PPE is applied on the footing and shear key
  at the angle of 2/3 φf, δP = 2/3 φf = 22.67°». «PPE = ½ kPE γs (5.25² − 2²)»: la presión crece
  desde la superficie, pero sólo se integra entre 2 ft (cara superior de la zapata) y 5.25 ft (base
  del dentellón), sobre un plano vertical en la punta (Figura 11.2.2-7).
- K sísmico (pág. 11.2-19): «From AASHTO Figure A11.4-2, when kh = 0.28, kPE cos δP = 5.2»,
  k_PE = 5.64, P_PE = 8.0 kip.
- K estático (págs. 11.2-22 y 11.2-23): «From AASHTO Figure 3.11.5.4-1, with φf = 34° and
  δP = 22.67°, kP = 7.05», P_P = ½(7.05)(0.12)(5.25² − 2²) = 9.97 kip.
- Sismo (pág. 11.2-20): «The resistance factor of PPE is also 1.0. The contribution of PPE is again
  ignored.» El deslizamiento sísmico no se verifica por fuerzas: k_h = k_y = 0.28 = 0.4·HPGA y se
  comprueba el desplazamiento de Newmark, d = 5.4 in < 6 in (A11.5.2).
- Resistencia Ib (págs. 11.2-26 y 11.2-27): «ϕτ = 1.0 for friction resistance; ϕep = 0.5 for passive
  resistance»; Q_u = 25.94; φ_τ·V·tan φ_f = 1.0(53.16)tan 34° = 35.86 kip; φ_ep·P_P·cos δ_P =
  0.50(9.97)cos 22.67° = 4.60 kip; R_r = 40.5 kip > Q_u. Cumplía sin el pasivo.
- La fricción se toma con V entero y tan φ_f; el pasivo no entra en excentricidad ni portante
  («PP has little effect on bearing calculation and is ignored», pág. 11.2-24).
- Sección 11.2.1.3.6 (pág. 11.2-8): «Rankine theory may
  greatly underestimate lateral passive earth pressure. Coulomb theory is unconservative when the
  soil on wall friction angle δ, is more than one-third retained soil friction angle. […] for the
  strength limit state, only half of the full passive lateral earth pressure may be utilized as
  resistance.»

### 2.2 CDOT, Bridge Design Manual, Ejemplo 11

Archivo: `/home/user/Normas/ejemplos_resueltos/cabezal_muros/cdot_ex11.xlsx`, hoja «Ex.11». Es una
hoja de cálculo, sin páginas: cito celdas.

- Geometría (celdas Q52 a Q58 y figura): H = 15 ft, B = 10 ft, T_F = 1.25 ft, punta 2.75 ft, 2 ft
  de relleno sobre la punta. Dentellón d_Key = 1.0 ft, T_Key = 1.5 ft, eje a 3.5 ft del talón.
- A249: «Center line of the shear key is approximately B/3 from the heel edge of the footing; see
  BDM Section 11.5.1.»
- A250: «Passive soil pressure at the toe shall be neglected; only include passive pressure due to
  the inert block (c) (see AASHTO 11.6.3.5).»
- A252: «Depth of inert block is taken to be the sum of the key depth and the effective wedge depth.
  […] Conservatively, effective wedge depth can be ignored, allowing inert block to be equal to
  shear key depth.»
- A255: «Per BDM Section 11.5.1, the top 1 ft. of fill at the toe shall be ignored for all design
  cases.»
- A256: «The Designer may choose to add weight of the shear key for eccentricity and bearing
  analysis once shear key dimensions are confirmed. For this example, weight of the key is ignored.»
- A198 y A211: «When a shear key is required to prevent sliding, the passive resistance shall be
  ignored» (en excentricidad y en portante).
- Suelo: relleno φ = 34°, δ = 2/3·φ; subrasante φ_Sub = 20°, μ = tan φ_Sub = 0.36. K_p = 7.6
  («AASHTO Fig. 3.11.5.4-1», Q24), EFW(p) = 0.988 kcf. **Defecto del ejemplo:** K_p se lee con el φ
  del relleno (34°) y el pasivo se moviliza en la subrasante (20°).
- Factores (Q45 a Q48): φ_τ = 1.0 («AASHTO T.11.5.7-1»), suelo sobre suelo 1.0, φ_ep = 0.5
  («AASHTO T.10.5.5.2.2-1»), evento extremo 1.0 («AASHTO 11.5.8»).
- Modelo (fórmulas Q264, Q265, W298, AC298, U302): c = d_Key + X_Key·tan δ_sub = 1 + 5.75·tan 13.33°
  = 2.36 ft; y1 = H_TF + T_F − 1 = 2.25 ft; y2 = y1 + c = 4.61 ft; R_ep = 0.988·½(2.25 + 4.61)·2.36
  = 8.00 kip. La carga vertical se reparte uniforme: R1 = V·X_Key/B delante del dentellón (suelo
  sobre suelo, multiplicada por cos δ_sub) y R2 = V − R1 detrás (concreto sobre suelo).
- Resultado: sin dentellón R_R = 7.15 < ΣH = 8.63 kip/ft («Shear Key is Required»). Con dentellón,
  Resistencia Ia: 7.04 + 0.50(8.00) = 11.04 > 8.63. Evento Extremo IIa (colisión, no sismo):
  6.07 + 0.50(8.00) = 10.07 > 2.61. **CDOT mantiene φ_ep = 0.50 también en evento extremo.**
- Diseño del dentellón (A506): sección crítica en la unión con la zapata, flexión y corte con el
  pasivo del deslizamiento; M_u = 10.48 kip·ft/ft.

No pude ver la «Figure 2» del bloque inerte (es un EMF que no se renderiza aquí); el modelo está
reconstruido de las fórmulas.

### 2.3 Lo que los dos ejemplos enseñan

| | Caltrans BDP 11.2 | CDOT Ej. 11 |
|---|---|---|
| Dentellón (ancho × prof.) | 0.61 × 0.23 m | 0.46 × 0.30 m |
| Profundidad / altura del muro | ≈ 0.03 | ≈ 0.06 |
| Posición del eje | 5 ft del talón (B = 19 ft) | B/3 desde el talón |
| Suelo que se ignora delante | todo lo que está sobre la zapata (2 ft) | 1 ft superior |
| Cara que recibe pasivo | zapata + dentellón, plano en la punta | bloque inerte bajo la zapata |
| K_p (φ = 34°, δ = 2/3·φ) | 7.05 | 7.6 |
| Fricción | V·tan φ, sin cambio | repartida, parte delantera × cos δ |
| φ_ep Resistencia / Extremo | 0.5 / 1.0 (y lo ignora) | 0.5 / 0.5 |
| Dentellón en E1 y E2 | no | no |

---

## 3. Manual de Puentes (MTC) y E.050

### 3.1 Manual de Puentes

PDF: `/home/user/Normas/normas/Puentes (Versión Libro).pdf`.

- 2.8.1.1.12.5 «Resistencia Pasiva» (11.6.3.5 AASHTO), pág. 250: «Para los cálculos de estabilidad
  se deberá despreciar la resistencia pasiva, a menos que la base del muro se extienda por debajo
  de la profundidad de máxima socavación, regiones potencialmente afectadas por ciclos de
  congelamiento y deshielo u otras perturbaciones. En este último caso sólo se deberá considerar
  efectiva la longitud embebida debajo de la mayor de estas profundidades.» Y: «La resistencia
  pasiva se deberá despreciar si el suelo que proporciona resistencia pasiva es o potencialmente
  puede ser blando, suelto o alterado, o si el suelo y el muro no están en contacto firme.»
- 2.8.1.1.12.6 «Deslizamiento» (11.6.3.6 AASHTO), págs. 250 y 251: «Si se incluye la resistencia
  pasiva como parte de la resistencia al corte requerido para resistir el deslizamiento, también
  se deberá considerar la posible eliminación futura del suelo delante de la fundación.»
  «R_R = φR_n = φ_τ R_τ + φ_ep R_ep 2.8.1.1.12.6-1». «R_ep = resistencia nominal pasiva del suelo
  disponible durante la totalidad de la vida de diseño de la estructura».
- Tabla 2.8.1.1.12.6-1, pág. 252: «Concreto llenado en sitio sobre arena. 0.80 […] Suelo sobre
  suelo. 0.90; Componente de la presión pasiva de la tierra de resistencia al deslizamiento. 0.50».
- 2.8.1.1.14.5 «Cálculo de la Presión Sísmica Pasiva del Suelo» (11.6.5.5 AASHTO), págs. 256 y 257:
  «El método de Mononobe-Okabe (M-O) no será utilizado para la estimación de la presión sísmica
  pasiva del suelo.» «Para muros empotrados a una profundidad menor que 5.0 ft, la presión pasiva
  se calculará usando el método estático (3.11 AASHTO).» «[…] tomando la fricción de contacto del
  muro igual dos-tercios (2/3) del ángulo de fricción del suelo.»
- El Manual no contiene «dentellón», «uña» ni «llave de corte» para muros. «Llave de corte»
  aparece sólo en tableros prefabricados.
- Dos diferencias con AASHTO 9.ª: escribe «se puede tomar» donde el original dice «shall be taken»,
  y R_τ = V·tan δ (forma de 2014) en vez de C·V·tan φ_f. No cambian el modelo.

### 3.2 E.050

PDF: `/home/user/Normas/normas/Norma E.050 Suelos y cimentaciones.pdf`.

- No contiene «dentellón» ni «llave». No da regla para cuándo contar el pasivo.
- Figura 21 (pág. 72), «Diagrama de cargas a considerar para el diseño de muros de contención
  (volteo y deslizamiento)»: dibuja «E pasivo» sobre la altura enterrada delante y «Fricción» en la
  base.
- Figura 22 (pág. 72): «Eps = 0.85·Kp·R·γ·Df²/2», aplicado a D_f/3. El texto no explica el 0.85.
- 16.2.9 (pág. 29 por conteo de pies de página; conviene confirmarla): el EMS debe entregar «f)
  Coeficiente Pasivo Estático Kp; g) Factor de Reducción del Empuje Pasivo R; […] j) Coeficiente
  Pasivo Dinámico Kps; k) Coeficiente de Fricción bajo la cimentación Tan δ».
- 39.13.6 (pág. 72): FS mínimo «Condición Estático 1.50 (por volteo y por deslizamiento)»,
  «Condición Pseudo - dinámico: 1.25».

Para el marco ASD (por analogía, [N→]) la E.050 sí admite el pasivo y da la fórmula; K_p, R y K_ps
son datos del EMS, es decir [S].

### 3.3 Hoja de ruta v8

No dice nada del dentellón de corte ni del pasivo delante del cabezal (sólo que la traducción del
Manual «se corta en el empuje pasivo k_p», línea 1171). Por `CLAUDE.md`, cada número que el modelo
necesite y la fuente no dé es un criterio [A] nuevo.

---

## 4. Modelo propuesto

Nombres de criterio sugeridos; ninguno existe hoy. El dentellón de corte es un elemento distinto
del «dentellón de la losa de entrega» que el programa ya tiene (`dentellon_losa_entrega`, 0.40 ×
0.80 m), que es una pantalla anti-socavación y no debe confundirse en memoria ni en claves.

### 4.1 Lo que tiene número en la fuente

| Magnitud | Valor | Etiqueta | Cita |
|---|---|---|---|
| Forma de la resistencia | R_R = φ_τ·R_τ + φ_ep·R_ep | [N→] / [C] | MdP 2.8.1.1.12.6-1, pág. 251; AASHTO 10.6.3.4-1, pág. 10-84 |
| φ_ep, Resistencia | 0.50 | [N→] / [C] | MdP Tabla 2.8.1.1.12.6-1, pág. 252; AASHTO Tabla 10.5.5.2.2-1, pág. 10-42 |
| φ suelo sobre suelo, fila de Sección 10 | 0.90 | [N→] / [C] | mismas tablas |
| φ deslizamiento, fila de muros | 1.0 | [C] | AASHTO Tabla 11.5.7-1, pág. 11-17 |
| φ en Evento Extremo | 1.0 | [C] | AASHTO 11.5.8, pág. 11-18 |
| Suelo efectivo para el pasivo | sólo bajo la mayor de socavación, helada u otra perturbación | [N→] / [C] | MdP 2.8.1.1.12.5, pág. 250; AASHTO 11.6.3.5, pág. 11-24 |
| Límite del método estático en sismo | empotramiento < 5.0 ft = 1.524 m | [N→] / [C] | MdP 2.8.1.1.14.5, pág. 257; AASHTO 11.6.5.5, pág. 11-33 |
| Prohibición de M-O para el pasivo | — | [N→] / [C] | mismas |
| Tope de δ con teoría de cuña | φ_f/2 | [C] | AASHTO 3.11.5.4, pág. 3-124 |
| Δ/H para movilizar el pasivo | 0.01, 0.02, 0.04, 0.02, 0.05, 0.05 | [C] | AASHTO Tabla C3.11.1-1, pág. 3-117 |
| Presión pasiva con cohesión | p_p = k_p·γ·z + 2c·√k_p | [C] | AASHTO 3.11.5.4-1, pág. 3-125 |
| Gradiente hidráulico máximo | 0.20 / 0.30 | [C] | AASHTO 11.6.3.4, pág. 11-24 |

### 4.2 Lo que es elección [A]

**a) Profundidad del dentellón, d.** Crece con el paso que ya existe
(`dimensionamiento_zapata_cabezal.paso_m`, 0.10 m) desde un mínimo hasta un tope.
- Tope con respaldo de fuente: el empotramiento efectivo (desde el terreno que cuenta hasta la base
  del dentellón) no llega a 1.524 m mientras exista la condición sísmica. Al alcanzarlo, el pasivo
  sísmico deja de ser calculable con el método estático: `MetodoNoEvaluableError` con
  `MOTIVO_METODO_NO_EVALUABLE_CABEZAL` (haría falta la espiral logarítmica con inercia de A11.4).
- Tope elegido por el proyectista, dentro del anterior: [A] `profundidad_max_dentellon_corte_m`.
  Ventana que las fuentes sostienen: de 0.23 m (Caltrans) y 0.30 m (CDOT) a 1.524 m. Ningún ejemplo
  de los disponibles pasa de 0.30 m; un dentellón de más de 1 m no tiene precedente en `normas/`.
- Mínimo: [A]. Los ejemplos dan 0.23 y 0.30 m; propongo el paso (0.10 m) como arranque de la grilla
  y que el mínimo constructivo lo declare el proyectista.

**b) Ancho del dentellón.** Ninguna fuente lo fija. Los ejemplos dan 0.61 m (ancho/profundidad
2.7) y 0.46 m (1.5). [A] `ancho_dentellon_corte_m`, ventana 0.40 a 0.60 m; lo que decide de verdad
es su armado (ménsula con el pasivo factorado, sección crítica en la unión con la zapata, como CDOT
A506 y con las filas A1 a A4 que ya existen). El ancho no entra en E3.

**c) Posición.** [A] `posicion_dentellon_corte`, con opciones `tercio_desde_el_talon` (CDOT A249),
`bajo_la_pantalla` y `en_el_talon`. Los dos ejemplos lo ponen hacia el talón. Con el modelo (f.1)
de abajo la posición no cambia E3; con (f.2) sí.

**d) Suelo que se ignora delante.** [A] `terreno_efectivo_del_pasivo`, por extremo:
- Salida: el terreno efectivo es el fondo de la hoya de la Fase 6 (el mismo `min(cota_fondo_hoya,
  cota_pie)` que ya usa `M9._empotramiento_delante`). Con el margen 0 de archivo, la zapata no
  aporta pasivo y sólo cuenta la cara del dentellón.
- Entrada: no hay hoya calculada y delante está la losa de entrega. Ventana: ignorar los 0.30 m
  superiores (CDOT, 1 ft), ignorar todo lo que está sobre la cara superior de la zapata (Caltrans),
  o contar sólo bajo la base de la zapata (lado seguro; lo que recomiendo). En los tres casos el
  suelo ignorado como cara resistente sí pesa como sobrecarga: R_ep = ½·K_p·γ·(z2² − z1²).
- Bajo el freático delante, γ sumergido (el programa ya calcula D_w ahí).

**e) K_p.** [C] para el método, [A] para δ.
- Método: Coulomb cerrado con trasdós vertical y terreno horizontal,
  K_p = cos²φ / {cos δ·[1 − √(sen(φ + δ)·sen φ / cos δ)]²}, componente horizontal K_p·cos δ. Es la
  «wedge theory» que 3.11.5.4 admite.
- δ: [A] `friccion_dentellon_suelo_delta_pasivo`, ventana [0, φ_f/2] (tope de 3.11.5.4). Por
  defecto 0, que da Rankine, K_p = tan²(45° + φ/2).
- Contraste que la memoria debe imprimir: las lecturas de la Figura 3.11.5.4-1 con δ = 2/3·φ rondan
  el doble de Rankine (7.05 y 7.6 contra 3.54 para 34°). Rankine es conservador; no propongo
  digitalizar la figura.
- Si el EMS trae K_p y R (E.050 16.2.9), ganan como [S], igual que `q_n_kpa` gana sobre la ecuación.
- El φ es el del suelo de fundación delante del dentellón, no el del relleno (el error de CDOT).
- Suelo cohesivo: ec. 3.11.5.4-1 con la regla de c y φ de E.050 Art. 20 que el módulo ya aplica; y
  la guardia de 10.6.3.4 por la grieta de retracción (el pasivo en arcilla exige contacto firme).

**f) Superficie de deslizamiento.** La fuente calla; hay dos modelos publicados. [A]
`modelo_deslizamiento_con_dentellon`:
- (f.1) `plano_horizontal_por_la_base` (Caltrans): R_τ = C·V·tan φ_f sin cambio y R_ep sobre el
  plano vertical delante, hasta la base del dentellón. Es el que recomiendo por simple. No se suma
  el peso del prisma de suelo bajo la zapata ni su inercia: las dos omisiones juntas quedan del
  lado seguro si tan φ_f > k_h (0.625 > 0.50 en A-01) y hay que decirlo en la memoria.
- (f.2) `bloque_inerte_cdot`: reparto de V, tramo delantero suelo-suelo con cos δ_sub, pasivo sobre
  c = d + X·tan δ_sub. Depende de la posición y cuenta más profundidad que la del dentellón.
- Con zapata vaciada contra suelo granular, C = 1.0 y tan δ = tan φ_f: pasar el plano a suelo-suelo
  no cambia el coeficiente. Sí cambia la fila de φ si rige la de la Sección 10 (0.80 concreto
  vaciado en sitio contra 0.90 suelo sobre suelo); con `muros_tabla_11_5_7`, que es el valor de
  archivo, es 1.0 en los dos casos.

**g) φ_ep en sismo.** [A] `phi_ep_evento_extremo`, opciones 1.0 y 0.5.
- 1.0 es la letra de 11.5.8 y lo que escribe Caltrans.
- 0.5 es lo que hace CDOT en evento extremo y lo que C10.6.3.4 explica: el 0.5 no mide
  incertidumbre sino movilización parcial con movimientos pequeños.
- Recomendación: atar la opción al régimen sísmico que el proyecto ya declara. Con
  `factor_muro_eleccion` = `sin_reduccion` (muro que no se desplaza) rige 0.5; con la reducción a
  0.5·k_h0 (muro que admite 1 a 2 in) puede regir 1.0. Contar el pasivo pleno y a la vez negar el
  desplazamiento que lo moviliza es incoherente, y además es más favorable que cualquiera de los
  dos ejemplos.

**h) Portante y excentricidad.** El dentellón no entra en E1 ni en E2: ni su peso ni el pasivo
(Caltrans pág. 11.2-24; CDOT A198, A211 y A256). No es [A]: es la práctica de las dos fuentes y el
lado seguro. Consecuencia que conviene escribir: el factor de inclinación de la portante sigue
viendo H entero, de modo que el dentellón no mejora E1.

**i) Orden del dimensionamiento.** Zapata hasta el tope; si sólo falla E3 (estática o sísmica), se
añade el dentellón y crece d hasta cumplir o hasta su tope; si a tope de zapata falla E1 o E2, «no
factible» sin probar dentellón (decisión del dueño). Origen nuevo de dimensión: «dimensionada por
deslizamiento». El marco ASD (E3-ASD, indicador) puede usar E_ps de la Figura 22 de E.050 sólo con
K_p y R del EMS; sin ellos, el mismo K_p que el LRFD y sin el 0.85, declarándolo.

### 4.3 Verificación que la fuente exige y hoy no existe

11.6.3.5 obliga a que el pasivo sea suficiente «to prevent unacceptable forward movement». Como
mínimo, el paso de memoria debe imprimir el movimiento que moviliza el pasivo pleno,
Δ = (Δ/H)·d con la fila de la Tabla C3.11.1-1 que corresponda al suelo (dato del EMS: la compacidad
no la conoce el programa; sin ella, el rango 0.01 a 0.04). Para d = 1.5 m son 15 a 60 mm.

---

## 5. Riesgos: cuándo no contar el dentellón y qué avisar

| Situación | Qué hacer | Sustento |
|---|---|---|
| Salida sin hoya estimada (lecho sin declarar, Fase 6 no evaluable) | No contar pasivo; `Bloqueo` que pide el dato. No suponer socavación cero | 11.6.3.5; 10.6.3.4 («future removal of the soil») |
| Base del dentellón sobre el fondo de la hoya | Pasivo = 0 | 11.6.3.5 |
| Hoya que alcanza la base de la zapata (margen 0) | Sólo la cara del dentellón; avisar que 12.6.5 pide 2.0 ft bajo la socavación | 11.6.3.5; 12.6.5 |
| Suelo delante blando, suelto o alterado; relleno de la excavación sin compactar contra el dentellón | No contar. Exigir en planos que el dentellón se vacíe contra terreno natural sin encofrar | 11.6.3.5, tercer párrafo |
| Arcilla | Considerar la grieta de retracción; pasivo con la ec. 3.11.5.4-1 o no contar | 10.6.3.4 |
| Roca (filas de sitio de roca en `F_pga`) | El pasivo de suelo no aplica. `MetodoNoEvaluableError`: en roca son anclajes, pernos o llaves (10.6.1.5) | 10.6.1.5, pág. 10-54 |
| Empotramiento efectivo ≥ 1.524 m con sismo | `MetodoNoEvaluableError` (espiral logarítmica sísmica con inercia) | 11.6.5.5 |
| Trasdós sin drenaje (valor de archivo) | Hay carga hidráulica entre trasdós y pie: flujo ascendente delante del dentellón que reduce el peso efectivo. Avisar y comprobar el gradiente | 11.6.3.4 |
| Terreno que desciende delante (`TERRENO_TALUD`) | Las fórmulas de terreno horizontal no valen. No contar o no evaluable | 3.11.5.4 (Figura 3.11.5.4-2, no implementada) |
| Agua en el cauce delante | γ sumergido en el pasivo | 3.11.3 (no releído aquí) |
| k_h sin reducir y φ_ep = 1.0 | Aviso de incoherencia entre el régimen y la movilización | 11.6.5.2.2; C10.6.3.4; Tabla C3.11.1-1 |

Texto mínimo del aviso cuando el dentellón entra: que la resistencia cuenta el empuje pasivo sobre
d metros bajo el fondo de la hoya; que depende de que ese suelo exista durante toda la vida de la
obra y no se remueva; el movimiento que lo moviliza; y que el veredicto de E3 cambia dentro de las
ventanas de δ y de φ_ep (con el mismo mecanismo de `M9._avisos_de_sensibilidad`).

---

## 6. Caso numérico para el test dorado

Datos: A-01 del juego titular (`drenaje_trasdos` = `sin_drenaje`, `factor_muro_eleccion` =
`sin_reduccion`, γ_sat = 20), `HEAD` `2b06ef2`. PGA 0.50, k_h = k_h0 = 0.50, k_v = 0. Fundación de
prueba: no cohesiva, φ_f = 32°, γ = 18 kN/m³. Fila φ de muros: φ_τ = 1.0. Combinación que rige E3:
«Evento Extremo I, 50% P_AE + 100% P_IR», para excentricidad y deslizamiento.

Constantes: tan 32° = 0.624869; K_p Rankine = tan² 61° = 3.254588; ½·K_p·γ = 29.29129 kN/m³.
Coulomb con δ = 16°: K_p = 5.774832, componente horizontal 5.551125.

### 6.1 Salida (zapata al tope, B = 4.852 m, D_f = 1.078 m, base en el fondo de la hoya)

- N = 258.483 kN/m; H_u = 256.811 kN/m.
- R_τ = 1.0·258.483·0.624869 = 161.518 kN/m (coincide con el programa: 161.51828).
- Déficit: 256.811 − 161.518 = 95.293 kN/m.
- Terreno efectivo = base de la zapata (z1 = 0). R_ep = 29.29129·d².

| d (m) | R_ep (kN/m) | R_R con φ_ep = 1.0 | R_R / H_u | R_R con φ_ep = 0.5 | R_R / H_u |
|---|---|---|---|---|---|
| 0.80 | 18.746 | 180.265 | 0.702 | 170.891 | 0.665 |
| 1.00 | 29.291 | 190.810 | 0.743 | 176.164 | 0.686 |
| 1.50 | 65.905 | 227.424 | 0.886 | 194.471 | 0.757 |

- d necesario: 1.804 m (φ_ep = 1.0) y 2.551 m (φ_ep = 0.5). Los dos pasan de 1.524 m.
- Con Coulomb δ = φ/2: 1.381 m (φ_ep = 1.0; con d = 1.50 m, R_ep = 112.410 y R_R = 273.929, cumple
  con 1.067) y 1.953 m (φ_ep = 0.5).
- **Dorado:** con Rankine, d = 1.50 m y φ_ep = 1.0, E3-LRFD.sis.s da 256.811 > 227.424: no cumple.
  El dentellón llega a su tope y el punto queda sin cerrar.
- Además E1-LRFD.sis.s: 100.63 kPa contra 0.59 kPa admisibles (con `factores_inclinacion…` =
  `aplicar`; con `omitir` serían 360.61). Por la regla del dueño, este cabezal es «no factible»
  antes de probar el dentellón.
- Movimiento para movilizar el pasivo con d = 1.50 m: 15 a 60 mm.

### 6.2 Entrada (zapata al tope, B = 3.375 m, D_f = 0.80 m, sin hoya)

- N = 130.284 kN/m; H_u = 128.625 kN/m.
- R_τ = 130.284·0.624869 = 81.411 kN/m (programa: 81.41057).
- Déficit: 47.215 kN/m.
- Terreno efectivo = terreno del pie, contando pasivo sólo bajo la base (z1 = 0.80 m):
  R_ep = 29.29129·[(0.80 + d)² − 0.64].

| d (m) | R_ep (kN/m) | R_R con φ_ep = 1.0 | R_R / H_u | R_R con φ_ep = 0.5 | R_R / H_u |
|---|---|---|---|---|---|
| 0.60 | 38.665 | 120.075 | 0.934 | 100.743 | 0.783 |
| 0.70 | 47.159 | 128.570 | 0.9996 | 104.990 | 0.816 |
| 0.80 | 56.239 | 137.650 | 1.070 | 109.530 | 0.852 |

- d necesario: 0.701 m (φ_ep = 1.0), que en la grilla de 0.10 m es 0.80 m; empotramiento 1.60 m,
  **mayor que 1.524 m**: la fuente ya pide el método sísmico. Con d = 0.70 m (empotramiento 1.50 m)
  falta 0.06 kN/m.
- Con φ_ep = 0.5: 1.166 m (empotramiento 1.97 m). Con Coulomb δ = φ/2: 0.459 m (φ_ep = 1.0) y
  0.791 m (φ_ep = 0.5).
- Si el terreno sobre la base no se cuenta ni como sobrecarga (z1 = 0): d = 0.80 m da R_ep = 18.746
  y R_R = 100.157 (0.779).
- **Dorados:** (i) d = 0.60 m, φ_ep = 1.0: 128.625 > 120.075, no cumple; (ii) d = 0.80 m,
  φ_ep = 1.0: 128.625 ≤ 137.650, cumple en fuerzas, pero el empotramiento de 1.60 m debe levantar
  el «no evaluable» de 11.6.5.5; (iii) d = 0.80 m, φ_ep = 0.5: 128.625 > 109.530, no cumple. No
  usar d = 0.70 m como dorado: el margen es de 0.04 %.
- E1-LRFD.sis.e tampoco cumple en este cabezal (72.78 contra 7.84 kPa; 621.33 con `omitir`).

### 6.3 Dorado externo independiente del programa

CDOT Ej. 11, Resistencia Ia: ΣV = 19.86, ΣH = 8.63 kip/ft, μ = 0.36, B = 10, X_Key = 5.75,
δ_sub = 13.33°, EFW(p) = 0.988 kcf, d_Key = 1.0 ft.
- R1 = 19.86·5.75/10 = 11.42; R2 = 8.44; φR_τ = 11.42·0.36·cos 13.33° + 8.44·0.36 = 7.04 kip/ft.
- c = 1 + 5.75·tan 13.33° = 2.36 ft; R_ep = 0.988·½(2.25 + 4.61)·2.36 = 8.00 kip/ft.
- R_R = 7.04 + 0.50·8.00 = 11.04 > 8.63.

Sirve para el modelo (f.2). Para (f.1) el contraste es Caltrans, Resistencia Ib:
35.86 + 0.50·9.97·cos 22.67° = 40.46 kip (el documento redondea a 40.5), con P_P =
½(7.05)(0.12)(5.25² − 2²) = 9.97 kip.

---

## 7. Lo que no pude verificar

- No digitalicé la Figura 3.11.5.4-1 ni la A11.4-2; los valores de A11.4-2 son lecturas a ojo.
- La «Figure 2» de CDOT (bloque inerte) no se pudo renderizar.
- La página impresa de E.050 16.2.9 (29) sale de contar pies de página en el volcado, no de ver la
  página.
- No leí AASHTO 3.11.3 (agua) ni la BDM 11.5.1 de CDOT, que el ejemplo cita y no está en la carpeta.
- Los números de la sección 6 son de `HEAD`; el árbol de trabajo tiene `M9_cabezal.py` modificado y
  puede dar otros.
