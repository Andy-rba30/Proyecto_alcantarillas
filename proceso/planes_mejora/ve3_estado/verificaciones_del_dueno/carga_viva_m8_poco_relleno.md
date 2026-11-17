> Verificación independiente pedida por el dueño (decisión 4 del LEEME: primer filtro antes del ingeniero revisor), hecha con el modelo Fable desde otra sesión. La sesión que la envía comprobó por su cuenta la cita de AASHTO LRFD 9.ª 12.10.2.3 («uniform vertical distribution across the top of the pipe»). Ningún hallazgo bloqueante ni alto: la lectura literal se mantiene; los tres medios son para VE-3 (1 y 3) y para el dueño (2: adoptar L_e como [A] o sólo avisar).

# Revisión independiente: carga viva de M8 a través del relleno (VE3-04)

Rama revisada: `origin/claude/youthful-shannon-rjzmuc` (commit `ad8dd9f`). Fuente: AASHTO LRFD 9.ª ed. (2020), PDF de `/home/user/Normas/normas/`. Ecuaciones leídas en la imagen de la página. No se modificó ningún repositorio; el worktree temporal se eliminó.

## Veredicto

**«W_L sin L_e» es la lectura literal correcta de la 9.ª edición; no hay error de aplicación.** M8 transcribe las Eqs. 3.6.1.2.6b-1 a -7 sin desviación y mi cálculo a mano coincide con el programa al cuarto dígito (5 410.9 plf en el Ej. 1 de DD 1). El +65 % es real y del lado seguro, pero **no es «cambio de edición»**: +51 % es la longitud efectiva L_e de ACPA, que la 9.ª ed. no escribe en ningún numeral leído, y solo +10 % es la presión en la clave. Sí afecta al diseño: en tubos de 0.60–0.90 m con menos de ~1.0 m de relleno sube una o dos clases de M 170M respecto de la práctica ACPA.

## 1. Lo que dice la 9.ª edición (transcripción)

**3.6.1.2.5, pág. 3-25 (PDF 79).** «The tire contact area of a wheel consisting of one or two tires shall be assumed to be a single rectangle, whose width is 20.0 in. and whose length is 10.0 in.»

**3.6.1.2.6a, pág. 3-26 (PDF 80).**
- Permiso: «For single-span culverts, the effects of live load may be neglected where the depth of fill is more than 8.0 ft and exceeds the span length».
- Relleno somero: «Live load shall be distributed to concrete pipe culverts with less than 2.0 ft of cover in accordance with Eq. 4.6.2.10.2-1, regardless of the direction of travel. Round concrete culverts with 1.0 ft or more but less than 2.0 ft of cover shall be designed for a depth of 1.0 ft. Round culverts with less than 1.0 ft of fill shall be analyzed with more comprehensive methods.»
- Dominio del método: «Where the depth of fill over round, nonconcrete culverts is greater than 1.0 ft, or when the depth of fill over flat top three-sided, or long-span concrete arch culverts, or concrete pipe is 2.0 ft or greater the live load shall be distributed to the structure as wheel loads, uniformly distributed over a rectangular area with sides equal to the dimension of the tire contact area specified in Article 3.6.1.2.5 increased by the live load distribution factors (LLDF) specified in Table 3.6.1.2.6a-1, and the provisions of Articles 3.6.1.2.6b and 3.6.1.2.6c.»
- Carriles y vehículo: «For traffic parallel to the span, culverts shall be analyzed for a single loaded lane with the single lane multiple presence factor. […] Only the axle loads of the design truck or design tandem […] shall be applied as live load on culverts, regardless of traffic orientation.»

**Tabla 3.6.1.2.6a-1, pág. 3-27 (PDF 81).** «Concrete Pipe with fill depth 2.0 ft or greater: 1.15 for diameter 2.0 ft or less; 1.75 for diameters 8.0 ft or greater; Linearly interpolate for LLDF between these limits. All other culverts and buried structures: 1.15.» Y A_LL = l_w·w_w (3.6.1.2.6a-1).

**3.6.1.2.6b, págs. 3-27 y 3-28 (PDF 81-82).** Unidades: H, s_w, s_a, l_w, w_w en ft; w_t, l_t, D_i en in.
- (b-1) H_int-t = (s_w − w_t/12 − 0.06·D_i/12) / LLDF
- (b-2) H < H_int-t: w_w = w_t/12 + LLDF·H + 0.06·D_i/12
- (b-3) H ≥ H_int-t: w_w = w_t/12 + s_w + LLDF·H + 0.06·D_i/12
- (b-4) H_int-p = (s_a − l_t/12) / LLDF
- (b-5) H < H_int-p: l_w = l_t/12 + LLDF·H
- (b-6) H ≥ H_int-p: l_w = l_t/12 + s_a + LLDF·H
- (b-7) P_L = P·(1 + IM/100)·m / A_LL, con «P = live load applied at surface on all interacting wheels (kip)», «s_w = wheel spacing, 6.0 ft», «D_i = inside diameter or clear span of the culvert (in.)».
- w_w es la dimensión «transverse to culvert spans», es decir, **a lo largo del eje del tubo**. El único término de reparto longitudinal por la estructura es 0.06·D_i.
- C3.6.1.2.6b: «The case where traffic is parallel to the culvert span applies to the vast majority of highway culverts.»

**3.6.1.2.6c, pág. 3-28.** Tráfico perpendicular: se intercambian (w_t, s_w) por (l_t, s_a).

**3.6.2.2, pág. 3-34 (PDF 88).** IM = 33(1.0 − 0.125·D_E) ≥ 0 % (3.6.2.2-1), «D_E = the minimum depth of earth cover above the structure (ft)».

**12.10.2.3, pág. 12-54 (PDF 1692).** «Live loads shall be as specified in Article 3.6 and shall be distributed through the earth cover as specified in Article 3.6.1.2.6. For standard installations, the live load on the pipe shall be assumed to have a uniform vertical distribution across the top of the pipe and the same distribution across the bottom of the pipe as given in Figure 12.10.2.1-1.» No hay L_e.

**12.10.4.3.1, pág. 12-64 (PDF 1702).** D = (12/S_i)·[(W_E + W_F)/B_FE + W_L/B_FLL]; «W_L = total unfactored live load on unit length pipe specified in Article 12.10.2.3 (kip/ft)»; «For Type 1 installations, D loads […] shall be modified by multiplying by an installation factor of 1.10.»

**12.10.4.3.2c y Tabla -1, pág. 12-66 (PDF 1704).** B_FLL: 12, 18 y 24 in → 3.2 (< 2.0 ft) y 2.4 (≥ 2.0 ft); «30 and larger» → 2.2 y 2.2. Comentario: «The relatively large bending stiffness in the longitudinal direction of concrete pipe results in the distribution of the live load force along the length of the pipe. This ratio of distribution length to pipe diameter is higher in small diameter pipes designed by the Indirect Design Method. The bedding factor has been adjusted in Table 12.10.4.3.2c-1 to account for this higher distribution length.»

No verificado por imagen: el valor m = 1.20 de la Tabla 3.6.1.1.2-1 (localicé la tabla en el PDF 77, no releí la celda).

## 2. Lo que aplica M8 (`src/modulos/M8_estructural.py`, rama VE-3)

`_presion_de_un_vehiculo` (líneas 1039-1063) y `carga_viva_enterrada` (1080-1261):

1. LLDF: `_lldf`, 1.15 salvo tubo de concreto, que interpola 1.15→1.75 entre D_i = 2 ft y 8 ft. Coincide con la tabla.
2. IM = 33(1 − 0.125·D_E) ≥ 0, con D_E = relleno sin el paquete del pavimento. Coincide; la elección de D_E da el IM mayor.
3. m = 1.20, un carril, tráfico paralelo al vano. Coincide con 3.6.1.2.6a.
4. H_int-t, w_w, H_int-p, l_w y P_L: idénticos a (b-1) a (b-7), en SI. P se dobla al interactuar ruedas y otra vez al interactuar ejes.
5. Se evalúan camión (32 kip, s_a = 14 ft) y tándem (25 kip, s_a = 4 ft) y gobierna el de mayor efecto.
6. Dominio: concreto y cajón H ≥ 2.0 ft, flexible H > 1.0 ft; fuera, `MetodoNoEvaluableError`.

Consumo por material:
- **Tubo de concreto** (`verificar_concreto`, 1478+): W_L = P_L·min(l_w, B_c); D = [(W_E+W_F)/B_FE + W_L/B_FLL]/S_i, ×1.10 en Tipo 1; B_FLL de la fila «≥ 2.0 ft».
- **TMC** (`verificar_tmc`, 1874+): C_L = min(l_w, S), F_1 = max(0.75·S/l_w, F_min), T_L = P_FD·S/2 + P_FL·C_L·F_1/2.
- **HDPE** (`verificar_hdpe`, 2352+): C_L = min(l_w/D_o, 1), F_1 = max(0.75·D_o/l_w, F_min), con F_2.

**Diferencias con lo transcrito en 1: ninguna en las ecuaciones de 3.6.1.2.6.** Dos matices, ambos fuera de la fórmula:
- min(l_w, B_c) no está escrito como ecuación en la norma; es la lectura de «uniform vertical distribution across the top of the pipe». Es la misma S_L que usa ACPA.
- Entre 1.0 y 2.0 ft sobre tubo de concreto la norma da un camino (Eq. 4.6.2.10.2-1) y el programa se detiene. Ver hallazgo 3.

No revisé contra el PDF las ecuaciones 12.7.2.2 (TMC) ni 12.12.3.5 (HDPE); solo cómo consumen P_L y l_w.

## 3. Tres casos

Scripts: `manual.py` (a mano, solo `math`), `prog.py` (llama a `M8.carga_viva_enterrada`) y `dload.py`, en la misma carpeta que este informe.

| Caso | A mano (9.ª ed.) | Programa | Publicado | Diferencia y causa |
|---|---|---|---|---|
| (a) ACPA DD 1 Ej. 1: concreto Ø30″, B_c = 3.08 ft, H = 2 ft | LLDF 1.20, IM 24.75 %, w_w = 4.217 ft, l_w = 3.233 ft, P_L = 1 756.8 psf, **W_L = 5 410.9 plf** (camión; tándem 4 227) | P_L = 84.116 kPa = 1 756.8 psf, W_L = 78.967 kN/m = **5 410.9 plf** | 3 272 plf | +65.4 %. Programa = mano. Causa abajo. |
| (b) PPI Ej. 2: HDPE Ø48″, H = 2 ft | Con la rueda del ejemplo (45 kip, 18×18 in, IM = 0, m = 1): l_d = 45.6 in, w_d = 48.48 in, **P_L = 20.36 psi** | No reproducible: HL-93 fijo. Con la misma geometría y HL-93: l_w = 37.6 in, w_w = 50.48 in, P_L = 12.62 psi (= mano) | 20.3 psi | La fórmula es la misma (LLDF 1.15, 0.06·D_i). La diferencia de número es solo el vehículo: el ejemplo usa un equipo de obra, no HL-93. |
| (c) Ø 0.60 m, H = 0.60 m, HL-93 | Flexible: IM 24.88 %, l_w = 0.944 m, w_w = 1.234 m, P_L = 91.56 kPa. Concreto (B_c = 0.75 m supuesto): W_L = 68.7 kN/m | Flexible: 91.557 kPa (= mano). Concreto: **`MetodoNoEvaluableError`**, H = 0.600 < 0.6096 m. Con H = 0.61 m: P_L = 89.52 kPa, W_L = 67.14 kN/m (= mano) | — | Sin diferencia numérica. El tubo de concreto con 0.60 m exactos queda fuera del método por 9.6 mm. |

**Descomposición del +65 % del caso (a)** (factores multiplicativos sobre el recálculo de ACPA, 3 267.5 plf):

| Paso | Factor |
|---|---|
| Una rueda de 16 kip con m = 1.20, en vez de dos ruedas de camiones en paso (32 kip, m = 1.0, ancho + 4 ft) | ×1.205 |
| LLDF 1.15 → 1.20 | ×0.945 |
| Término 0.06·D_i en w_w | ×0.964 |
| IM (24.75 % en ambos) | ×1.000 |
| S_L = B_c en ambos | ×1.000 |
| Subtotal: presión en la clave | **×1.099** |
| Sin L_e (ACPA: L_e = 7.97 + 1.75·0.75·3.08 = 12.01 ft frente a L = 7.97 ft) | **×1.507** |
| Total | ×1.656 |

Confirma la tabla del §8 de `docs/validacion_conducto.md` (+9.6 % y +50.7 %).

## 4. Dictamen

- **¿Lectura literal?** Sí. 12.10.2.3 remite a 3.6.1.2.6 y no menciona longitud efectiva. El reparto a lo largo del tubo que la norma reconoce está en dos sitios y el programa aplica ambos: el 0.06·D_i de w_w y el B_FLL de la Tabla 12.10.4.3.2c-1. Añadir además la L_e de ACPA contaría el reparto dos veces en Ø ≤ 24″.
- **¿Legítimo o defecto?** No es defecto de programación ni de aplicación. Tampoco es propiamente «cambio de edición»: es norma literal frente a un método de la industria (ACPA) que añade L_e. No pude comprobar si alguna edición de LRFD anterior a 2013 traía L_e; no está en el repositorio de normas.
- **¿Lado seguro y cuánto?** Sí. Frente a ACPA, W_L sale de +30 % (H = 6 ft) a +65 % (H = 2 ft) en los dos ejemplos de DD 1.
- **¿Afecta al diseño?** Sí, con poco relleno. Estimación mía a mano (Tipo 2, γ = 19 kN/m³, pared B, L_e de ACPA aplicada sobre la distribución de la 9.ª ed.; orden de magnitud, no una corrida del programa):

| D_i (m) | H (m) | D-load M8 (N/m/mm) | Clase | D-load con L_e | Clase |
|---|---|---|---|---|---|
| 0.60 | 0.61 | 55.0 | III | 34.4 | I |
| 0.60 | 0.80 | 42.0 | II | 29.3 | I |
| 0.90 | 0.61 | 49.9 | II | 28.7 | I |
| 0.90 | 0.80 | 41.1 | II | 26.8 | I |
| 0.60–1.50 | ≥ 1.00 | 31–36 | I | 25–35 | I |

  A partir de ~1.0 m de relleno la clase no cambia; con 1.5 m la diferencia en D-load baja a ~+10 %. No evalué el efecto en TMC ni HDPE: ahí no hay L_e en juego y el caso (b) muestra la misma fórmula que el PPI.

## 5. Hallazgos

1. **(Medio) La documentación atribuye la diferencia a la edición.** La ficha VE3-04 y la línea 83 de `docs/validacion_conducto.md` abren con «DD 1 (2009) aplica la distribución ANTERIOR a 2013», aunque el §8 ya dice que casi todo es L_e. Ante un jurado, «cambio de edición» no sostiene un +65 %. Corrección: decir en los dos sitios que la causa dominante (×1.51) es que la 9.ª ed. no escribe L_e y que la norma compensa con 0.06·D_i y B_FLL; la edición explica solo ×1.10.

2. **(Medio) Sobrecosto no declarado en el punto de uso.** El paso F8.CLASE de la memoria no advierte que la clase puede salir una o dos por encima de la práctica ACPA en tubos ≤ 0.90 m con H < 1.0 m. Corrección: un aviso en ese paso con el rango, o un contraste [C] que no rija (W_L con L_e), como ya se hace con la instalación Tipo 4. Añadir L_e al cálculo que rige sería una adopción [A] y necesita decisión del dueño, no una corrección.

3. **(Medio) Tubo de concreto con 1.0 ≤ H < 2.0 ft: el programa se detiene y la norma da camino.** 3.6.1.2.6a manda la Eq. 4.6.2.10.2-1 y «designed for a depth of 1.0 ft»; además la Tabla 12.10.4.3.2c-1 tiene la fila «< 2.0 ft» (B_FLL = 3.2) que hoy no se usa. Reproducible: `carga_viva_enterrada(H=0.60, D_i=0.60, conducto="tubo_concreto")` → `MetodoNoEvaluableError`. Un relleno total de 0.60 m, redondo en métrico, cae 9.6 mm por debajo del umbral. Detenerse es seguro, pero conviene confirmar cuántos puntos reales caen ahí (H es hasta la rasante, con pavimento). Corrección: implementar 4.6.2.10.2-1 para ese tramo, o dejarlo y decir en la memoria que el umbral es 0.6096 m.

4. **(Bajo) Ningún ejemplo de terceros cierra W_L de concreto con la edición vigente.** El PPI confirma la forma de l_w y w_w (20.36 psi a mano frente a 20.3 publicado), pero para HDPE y con otro vehículo. La reserva del §8 sigue en pie.

5. **(Bajo) min(l_w, B_c) es lectura del proyecto**, razonable e igual a la S_L de ACPA; ya está declarada como tal en el paso. Sin acción.

Sin hallazgos bloqueantes ni altos.

## 6. Para el ingeniero revisor

- Decidir si la tesis mantiene la lectura literal (conservadora, defendible con 12.10.2.3 y C12.10.4.3.2c) o adopta L_e como criterio [A] con fuente ACPA. Es una decisión de criterio, no de cálculo.
- Conseguir un ejemplo de tubo de concreto resuelto con LRFD 2013 o posterior (ACPA DD 1 revisado, PipePac, o un manual de un DOT) para cerrar W_L con un número de terceros.
- Confirmar si LRFD anterior a 2013 traía L_e en su texto o si siempre fue práctica ACPA / Standard Specifications.
- Releer la celda m = 1.20 de la Tabla 3.6.1.1.2-1 y las ecuaciones 12.7.2.2 y 12.12.3.5, que no verifiqué por imagen.
- Juzgar el hallazgo 3: si en el corredor hay tubos de concreto con menos de 0.61 m hasta la rasante.
