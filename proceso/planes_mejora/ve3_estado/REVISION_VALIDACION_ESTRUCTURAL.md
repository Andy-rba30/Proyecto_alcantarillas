# Revisión independiente de la validación estructural contra ejemplos publicados (VE-3.3 / VE3-03 y VE3-04)

- **Objeto:** `tests/apoyo/validacion_cabezal.py` → `docs/validacion_cabezal.md` (M9) y `tests/apoyo/validacion_conducto.py` → `docs/validacion_conducto.md` (M8), con `tests/test_validacion_cabezal.py` y `tests/test_validacion_conducto.py`.
- **Commit revisado:** `61a4dcc` (rama `claude/youthful-shannon-rjzmuc`), en un clon aparte (`/home/user/rev_validacion`); no se tocó el repositorio ni se hizo commit.
- **Fuentes leídas:** los PDF y las hojas de `/home/user/Normas/ejemplos_resueltos/` (texto con PyMuPDF; las páginas escaneadas del USACE y la ecuación del PPI, en imagen; la hoja de CDOT con openpyxl, fórmulas y valores) y AASHTO LRFD 9.ª ed. del repositorio de normas.
- **Qué NO se hizo:** no se corrió la suite completa (sólo los dos archivos de test, 116 verdes); no se buscó en internet un ejemplo resuelto con la edición 2013 o posterior.

## 0. Veredicto

**Fiable con correcciones.** La transcripción es buena (no encontré ninguna cifra mal copiada ni mal convertida), el motor reproduce las fuentes donde el método es el mismo y casi todas las erratas declaradas son reales. Pero la validación **demuestra menos de lo que su resumen dice** en tres puntos:

1. En M8, los diez contrastes «METODO» (toda la carga viva y toda la D-load) comparan el motor con **la lectura del mismo autor reescrita a mano**, no con una fuente. «0 defectos» ahí significa «M8 está bien programado según su lectura», no «la lectura está validada».
2. En M9, una de las cinco «erratas de la fuente» **no es errata** (acero de temperatura de CDOT), y al declararla así el contraste queda vacío: dos mutantes de la fórmula 5.10.6-1 sobreviven.
3. En M9, las filas «difiere por método» (n = Es/Ec) no fijan el valor del motor: un Ec un 5 a 10 % distinto sobrevive.

Ninguno de los tres esconde un defecto del motor que yo haya podido demostrar. Sobre **W_L sin longitud efectiva**: es la lectura literal de la 9.ª edición y la considero correcta, no un defecto (§3).

---

## 1. Hallazgos por severidad

### Bloqueantes
Ninguno.

### Alta

**A-1. Los contrastes «METODO» de M8 no pueden dar DEFECTO por una lectura equivocada de la norma.**
`tests/apoyo/validacion_conducto.py:149-155` (`Contraste.clase`): DEFECTO sólo si motor ≠ `referencia`, y `referencia` es el método de M8 reescrito en el arnés por el mismo autor (`_hl93_a_mano`, líneas 181-209; `_dload_aashto_a_mano`, 397-419). La diferencia con la fuente (+65 %, +104 %, −62 %) se clasifica siempre «METODO», sea cual sea su tamaño. El documento lo reconoce en §8, pero el §3 («0 defectos del motor») y la ficha VE3-04 («32 coinciden, 10 difieren… 0 defectos») se leen como una validación externa de la carga viva y de la D-load, y no lo son: **ninguna cifra de W_L ni de D-load de M8 está contrastada con una fuente**. Lo contrastado de verdad con la fuente en M8 son 32 filas: el IM (2), el VAF (4), el B_FE (20), un B_FLL, el empuje de flotación y las cuatro del USACE.
*Corrección sugerida:* separar en el resumen «contrastado contra la fuente» de «el motor reproduce su método» y no sumar los segundos como validación; y conseguir un ejemplo resuelto con AASHTO 2013 o posterior (ya pedido en VE3-04).

**A-2. La «referencia a mano» no es del todo independiente del motor, y el contraste DD1 no ejercita la línea de W_L de M8.**
- `validacion_conducto.py:261`: el arnés pasa a `M8.carga_viva_enterrada` **su propia** fórmula `efecto=lambda P_L, l_w: P_L * min(l_w, Do)`. En DD1-EJ1 y DD1-EJ4 el W_L «del motor» lo calcula el arnés; de M8 sólo se prueban P_L y l_w.
- La línea real (`src/modulos/M8_estructural.py:1541-1543` y `W_L = cv.P_L_kPa * min(cv.l_w_m, B_c)`) sólo entra por CPDM-4-7, y allí l_w (3.13 ft) > B_c (2.5 ft): la rama l_w < B_c no se ejercita en ningún contraste.
- **Mutante mío M8-A** (`min(l_w, B_c)` → `B_c` en `verificar_concreto`): **sobrevive, 116 verdes**. Es justo la fórmula que la observación principal discute.
- `validacion_conducto.py:311, 321, 323, 409, 411`: la referencia usa `M8._interpolar` (función del motor) y, para el B_FE «de la 9.ª ed.», la tabla del CPDM (`CPDM_BFE`), pese a que el docstring (línea 25 y 399-403) dice «sin llamar a M8» y «las tablas de la 9.ª ed. transcritas aquí a mano». (Comprobé que la tabla de AASHTO 12.10.4.3.2a-1 es idéntica a la del CPDM, así que el número es correcto; lo que falla es la independencia declarada.)
*Corrección sugerida:* en DD1 obtener W_L por la ruta de `verificar_concreto`; añadir un caso con l_w < B_c (p. ej. Ø 72 in con 2 ft: l_w = 3.23 ft frente a B_c = 7.17 ft); interpolar a mano en el arnés; y usar como contraste real el B_fe = 3.93 que el CPDM 4-2 publica para 48 in (hoy sólo se contrastan los nodos de la tabla).

**A-3. «Errata de la fuente» falsa: el acero de temperatura de CDOT (la hoja SÍ aplica el piso).**
`validacion_cabezal.py:474-487` y `docs/validacion_cabezal.md` §3 dicen que «la hoja aplica la ec. 5.10.6-1 sin el piso de la 5.10.6-2». La hoja calcula la 5.10.6-1 en `Y455` (0.083) **y comprueba el piso y el techo en la fila siguiente**: `AD456 = IF(AND(T454>=0.11, T454<=0.6),"OK","Fails")`. No hay errata: son dos comprobaciones separadas, como en AASHTO. El arnés compara 0.083 (ec. sin acotar) con un «recalculado» que no es la fórmula de la celda (`temperatura_us`, línea 230, acota a 0.11).
Consecuencia: el motor devuelve 0.11 por el piso y la ecuación 5.10.6-1 de M9 **no se contrasta**. Mutantes míos: coeficiente 1.30 → 1.00 **sobrevive**; `2(b+h)` → `4(b+h)` **sobrevive** (sólo muere el que duplica el resultado y supera el piso).
*Corrección sugerida:* retirar la errata del censo (`ERRATAS_ESPERADAS`, `test_validacion_cabezal.py:63-71`), contrastar 0.083 con la ecuación sin acotar (hace falta exponerla en M9 o elegir un caso que supere 0.11) y contrastar aparte el piso con `AD456`.

### Media

**M-1. Las filas «difiere por método» de M9 no fijan el valor del motor.**
`validacion_cabezal.py:134-139`: con `metodo` declarado, cualquier valor del motor fuera del 1 % es «difiere por método». No hay una `referencia` propia como en M8. Mutantes míos sobre `EC_COEFICIENTE_AASHTO_SI`: ×0.90, ×0.93, ×0.95 y ×1.04 **sobreviven**; `ES_REFUERZO_AASHTO_MPA` ×0.95 **sobrevive**. (×0.85 y ×1.06 mueren sólo de rebote, por s_max o porque la fila k cambia de clase.)
*Corrección:* añadir la referencia de M9 escrita a mano (n = 29 000 / (2 500·f'c^0.33): 7.341 en Caltrans, 7.062 en CDOT) y exigir motor = referencia.

**M-2. La regla de juicio de M9 deja pasar una errata declarada sin comprobar que lo sea.**
Misma función: con `errata` no vacía y el motor igual a lo recalculado el juicio es «errata» aunque lo publicado coincida con lo recalculado (pasa en q sísmica: 7.87 frente a 7.88, 0.13 %; en dv de CDOT, 0.47 %; en Vc de CDOT, 0.45 %). No es incorrecto —las tres son reales—, pero el censo no distingue «la fuente imprime un número equivocado» de «la fuente escribe mal un intermedio y el número está bien». Sólo dos de las cinco mueven el número publicado más allá de la tolerancia (e de servicio y k de CDOT); la de temperatura es falsa (A-3).

**M-3. El §8 de `validacion_conducto.md` no cuantifica las causas y atribuye a «lectura» lo que es texto de la norma.**
Descompuse a mano las dos cifras:

| Contraste | Presión M8 / ACPA | Efecto de no repartir con L_e | Total |
|---|---|---|---|
| DD1-EJ1 (2 ft) | 1.757 / 1.603 ksf = +9.6 % | 12.01 / 7.97 = +50.7 % | +65 % |
| DD1-EJ4 (6 ft) | 0.359 / 0.367 ksf = −2.1 % | 16.61 / 12.57 = +32.1 % | +29 % |

Casi todo es la desaparición de L_e; la «edición» (m = 1.20, 0.06·D_i, LLDF) pesa +10 % a 2 ft y es *favorable* a 6 ft. La explicación repetida en §4 («son dos ediciones del método») y la de §8 no lo dicen. Además §8 presenta la ausencia de L_e como «LECTURA» del proyecto; es lo que la 9.ª ed. escribe (§3 de este informe).
Menor, en el mismo sitio: el «R_o» de DD 1 es la **altura exterior** del tubo (3.08 ft = D_o en un circular; la Fig. 7 de la propia DD 1 escribe 3/4·B_c), no el radio. El arnés lo usa bien (línea 257), pero el documento lo escribe «3/4 R_o» sin aclararlo.

**M-4. Comentario erróneo sobre la fila kh·4 de Caltrans.**
`validacion_cabezal.py:512-513`: «su signo contradice al de las demás inercias». No contradice: la parte 4 es la llave de corte (0.15·0.75·2.0 = 0.22 kip, p. 11.2-55), que queda **por debajo** del punto O, y su fuerza de inercia da momento de signo contrario. El arnés la suma bien (+0.02), así que no cambia ningún número; sólo es una lectura equivocada escrita en el código.

**M-5. La observación O-1 se puede cerrar con la norma, y a favor de M9.**
AASHTO 5.4.2.4 (pág. 5-20, PDF 379) da la ec. 5.4.2.4-1 con w_c y, en C5.4.2.4, «For normal weight concrete with wc = 0.145 kcf, Ec may be taken as 2,500 f'c^0.33 (C5.4.2.4-1)». La Tabla 3.5.1-1 da 0.145 kcf al concreto de peso normal con f'c ≤ 5.0 ksi, y C3.5.1 (pág. 3-21, PDF 75) dice que los 0.005 kcf de más son del concreto *armado*, para cargas muertas. CDOT mete 0.150 kcf (el del armado) en la ecuación de Ec; Caltrans usa 57 000√f'c, que no es de AASHTO 8.ª/9.ª. M9 es el que sigue la letra. No hace falta decisión del dueño salvo que quiera otro w_c.

### Baja

- **B-1. Ramas sin ejemplo (mutantes que sobreviven, cobertura y no error):** `dv` piso 0.72·h (0.72 → 0.80); e admisible sísmica con γEQ = 1 (0.4·B → 0.45·B); tope V_n = 0.25·f'c; límite f_ss ≤ 0.6·fy; en M8, pandeo elástico 12E/(kS/r)² (12 → 6), el `min(f_y, f_c)` de `area_requerida_asd_a796`, y B_FLL de menos de 2 ft (inalcanzable hoy). El documento no las lista en «lo que no se contrasta».
- **B-2. Varios contrastes de M9 son triviales o hacen media cuenta en el arnés:** el arnés calcula `V·B/2 − M` antes de llamar a `presion_contacto_base` (`validacion_cabezal.py:257-262`) y toma cos δ / sen δ fuera de `empuje_activo_estatico` (línea 320-335). Válidos, pero de los 61 contrastes unos 24 son la misma cuenta e = M/N, B' = B − 2e, q = N/B'.
- **B-3. Inconsistencias de Caltrans no declaradas que el margen propagado absorbe:** la Tabla 11.2.2-2 imprime la parte 6 = 394.66 y la parte 8 = 66.06, mientras la 11.2.2-5 imprime 394.730 y 65.99 para las mismas fuerzas y brazos (las dos parejas suman 460.72). El margen |F|δb + |b|δF + δM (0.22 y 0.10) las deja pasar como redondeo; son más bien erratas compensadas. Sin efecto en ΣM.
- **B-4. Erratas menores de las fuentes no anotadas (no usadas):** CPDM 4-5 escribe «48-inch diameter pipe» en la nota de un tubo de 24 in y cita «Equation 3» por la 4; DD 22 Ej. 2 escribe «= 123(1 − 1/2.66) + 77» por «= 77»; Caltrans p. 11.2-27 da Q_u en «ksf» por kip.
- **B-5. Tolerancia del 1 % en cifras de dos dígitos:** e de CDOT Strength IV se publica «0.08» (resolución ±6 %) y pasa con 0.0798. No tapa nada —la sensibilidad va en la dirección correcta, porque e es diferencia de números grandes—, pero el contraste de esa fila vale poco.

---

## 2. Erratas declaradas: confirmadas y no confirmadas

| Fuente | Errata declarada | Recalculado por mí | Dictamen |
|---|---|---|---|
| Caltrans p. 11.2-23 | e = 19/2 − 8.79 = 0.70 | 9.5 − 8.79 = 0.71; con x = 465.8/52.98 = 8.792, e = 0.708 | **Confirmada**, de última cifra. No existe lectura sin redondear que dé a la vez x → 8.79, e → 0.70 y B' → 17.59 |
| Caltrans p. 11.2-22 | q sísmica con 55.35 | 55.35/7.03 = 7.873; 55.36/7.03 = 7.875 → 7.87 también; sin redondear 55.36/7.025 = 7.880 | **Confirmada** como errata del numerador escrito; el 7.87 publicado no cambia. También confirmado q_n: 0.8·33.22 = 26.58, luego «32.22» es el errado |
| Caltrans Tabla 11.2.2-3, parte 6 | 394.47 | 29.37 × 13.44 = 394.73 (la Tabla 11.2.2-5 imprime 394.730) | **Confirmada** |
| Caltrans Tabla 11.2.2-3, brazo 10.65 | debe ser 10.15 | 17.29 × 10.15 = 175.49 = momento impreso; h = 10.15 ft en p. 11.2-22 y en la Fig. 11.2.2-6 | **Confirmada** |
| CDOT `S411` | dv con c/2 | fórmula `MAX(AA355 − AA360/2, …)` con AA360 = c = 0.982; rótulo «de − Cb/2». AASHTO 5.7.2.8 (PDF 423): d − a/2. 18.199 frente a 18.285 | **Confirmada** |
| CDOT `Q444`/`AA444` | texto «(2)» con β = 1.81 | el texto usa `TEXT(S440,0)`; el valor, S440 = 1.81: 0.0316·1.81·√4.5·12·18.2 = 26.50 | **Confirmada**, sólo de formato del texto; el número publicado es correcto |
| CDOT `Q397` | k con ρ redondeado | X395 muestra 0.003 y la hoja calcula «as displayed»: k = 0.1794; con ρ = 0.002764, k = 0.1729 | **Confirmada** |
| CDOT `Y455` | temperatura sin el piso | la hoja comprueba 0.11 ≤ As ≤ 0.60 en `AD456` | **NO confirmada: no es errata** (A-3) |
| CPDM Ej. 4-7 | 597.3 frente a 563.2 | (952/3 + 1780/2.2)/2 = 563.2 | **Confirmada**; «H = 10» también (680 lb/ft sale de H = 2) |
| DD 22 Ej. 1 | «4267» | 68·[0.1073·7.17² + 8·7.17] = 4 275.6; 4276/1.25 = 3421; 3421 − 708 = 2713 | **Confirmada** |
| USACE p. B-9 | 1 220 psf; LL 38 200 | 3 m × 18 850 = 56 550 N/m² (bien en SI; 10 ft × 120 pcf = 1 200); 56 550 + 38 300 = 94 850, y 38 300 es la fila de 0.6 m de su tabla | **Confirmadas las dos**, leídas en la imagen |
| USACE p. B-11 (no usado) | I = 39 198 mm⁴/mm | 2.392 in⁴/ft = 3 266 mm⁴/mm; 2.392 × 16 387 = 39 198 | **Confirmada** |
| PPI (no usado) | «27.98 + 2.92» | 0.76 − 0.71·(6.81/10.90) = 0.316 → 0.32 | **Confirmada**, leída en la imagen |

Erratas no declaradas en números que la validación da por buenos: **ninguna que cambie un contraste**. Las que encontré están en B-3 y B-4.

---

## 3. «Difiere por método»: comprobación contra AASHTO LRFD 9.ª ed.

| Diferencia | Lo que dice la 9.ª ed. | Dictamen |
|---|---|---|
| Ec de C5.4.2.4-1 (M9) frente a 5.4.2.4-1 con 0.150 (CDOT) y 57 000√f'c (Caltrans) | 5.4.2.4 y C5.4.2.4, pág. 5-20 (PDF 379); Tabla 3.5.1-1 y C3.5.1, pág. 3-21 (PDF 75) | M9 sigue la norma (M-5) |
| Carga viva: HL-93, m = 1.20, LLDF por diámetro, 0.06·D_i | 3.6.1.2.6a, pág. 3-26 (PDF 80): «single loaded lane with the single lane multiple presence factor»; Tabla 3.6.1.2.6a-1 y Ecs. 3.6.1.2.6b-1 a -7, págs. 3-27 y 3-28 (PDF 81-82) | M8 y la referencia a mano coinciden con el texto. Recalculé 5 417, 1 108 y 4 676 lb/ft |
| W_E sin riñones | Ec. 12.10.2.1-1, W_E = F_e·w·B_c·H (PDF ~1690) | Correcto |
| W_F sumada a la tierra y 1.10 en Tipo 1 | 12.10.2.2 y Ec. 12.10.4.3.1-1, pág. 12-64 (PDF 1702): «For Type 1 installations, D loads… multiplying by an installation factor of 1.10» | Correcto. Recalculé D = 1 147 lb/ft/ft en CPDM-4-7 |
| B_FLL 2.4 para Ø ≤ 24 in con ≥ 2 ft; sin la regla «usar B_fe si es menor» | Tabla 12.10.4.3.2c-1, pág. 12-66 (PDF 1704); la regla del CPDM existe (texto del cap. 4) y no está en la 9.ª | Correcto |
| VAF y B_FE | Tablas 12.10.2.1-3 y 12.10.4.3.2a-1 | Idénticas a las del CPDM |
| DD 22 con relleno sobre riñones; flotación ASD | M8 toma el prisma B_c·H y γ_EV = 0.90, γ_WA = 1.00 | Diferencia real y del lado seguro; sólo coincide el veredicto, no un número |
| Simplificado de cortante, e admisible sísmica, h_eq | 5.7.3.4.1 (PDF 429); 11.6.5.1 (PDF 1494), «middle two-thirds… for γEQ = 0.0»; Tabla 3.11.6.4-2 (PDF 205) | M9 coincide con el texto |

### Juicio sobre W_L = P_L·min(l_w, B_c) sin longitud efectiva

**Es una lectura defendible; a mi juicio es la literal de la 9.ª edición y no un defecto.** Razones, todas leídas en el PDF:

1. **12.10.2.3** (pág. 12-54, PDF 1692): «Live loads shall be as specified in Article 3.6 and shall be distributed through the earth cover as specified in Article 3.6.1.2.6. For standard installations, the live load on the pipe shall be assumed to have a uniform vertical distribution across the top of the pipe». No hay L_e ni remisión a ella.
2. **12.10.4.3.1** define W_L como «total unfactored live load on unit length pipe specified in Article 12.10.2.3».
3. **C12.10.4.3.2c** (pág. 12-66, PDF 1704): «The relatively large bending stiffness in the longitudinal direction of concrete pipe results in the distribution of the live load force along the length of the pipe… The bedding factor has been adjusted in Table 12.10.4.3.2c-1 to account for this higher distribution length». La norma dice dónde metió el reparto longitudinal: en B_FLL (2.4 y 3.2 para tubos pequeños), en el LLDF creciente con el diámetro (1.15 a 1.75) y en el término 0.06·D_i de w_w. Aplicar además la L_e de ACPA lo contaría dos veces.
4. La dirección es la correcta: con tráfico paralelo a la luz, l_w va en el sentido de la marcha (a través del tubo) y w_w a lo largo del eje; carga por unidad de longitud de tubo = P_L × ancho cargado a través = P_L·min(l_w, B_c). El `min` es el mismo criterio que el S_L de DD 1.

Reservas, que no cambian el juicio:
- **No lo confirma ningún ejemplo resuelto** con la edición 2013 o posterior; ni lo hay en `ejemplos_resueltos/` ni lo busqué fuera. Mi dictamen sale del texto de la norma, no de un número de terceros.
- Para Ø ≥ 30 in el B_FLL no cambió (2.2) y la única compensación por perder L_e es el LLDF y el 0.06·D_i: el +65 % en 30 in es, por tanto, lo que la 9.ª ed. pide de más respecto de ACPA 2009, no un artefacto de M8. Conviene que el dueño lo sepa como consecuencia de la edición.
- La rama l_w < B_c no está cubierta por ningún contraste (A-2).

---

## 4. ¿Comparan el motor con la fuente, o consigo mismo?

- **M9:** el «recalculado» está escrito aparte en unidades de EE. UU. (`flexion_us`, `fisuracion_us`, `vc_us`, `ka_coulomb_aashto`, etc.) y no llama a M9. Es comparación real en 53 filas. Excepciones: temperatura (A-3) y las filas de método (M-1).
- **M8:** real en 32 filas (tablas, IM, empuje, USACE). En las 10 de método el motor se compara con el arnés (A-1), y en dos de ellas parte de la fórmula la pone el propio arnés (A-2).
- **Tolerancias:** 1 % en M9 y 0.5 % en M8 frente a cifras impresas están justificadas por el redondeo de las fuentes (la hoja de CDOT calcula «as displayed»); las diferencias mayores que vi dentro de tolerancia son 0.67 % (s_max de CDOT) y 0.47 % (dv). No encontré ninguna diferencia de método escondida dentro de la tolerancia. `TOL_REL_MOTOR` = 1e-9 es adecuada.

---

## 5. Tests y mutantes

- `tests/test_validacion_cabezal.py` + `tests/test_validacion_conducto.py`: **116 passed**.
- **Mutantes declarados, los cuatro mueren:** `MODULO_ROTURA_AASHTO_SI` ×1.05; `NUCLEO_CENTRAL_DIVISOR` ×5/6; VAF Tipo 1 → 1.40; B_FE Tipo 4 (24 in) → 1.8.
- **Mutantes míos que mueren:** M9: 700 → 600 de fisuración; β_s 0.7 → 0.8; 0.0316 ×1.05; piso de temperatura 0.11 → 0.09; 0.9·d_e → 0.95; 16 in → 22 in; 3·d_v → 6·d_v; B/3 → B/6 con γEQ = 0; γ1 1.6 → 1.2; reducción de β1 ×2; talud y signo del trasdós en Coulomb; j = 1 − k/2; d − a en vez de d − a/2; raíz de k sin el 2; temperatura con (b+h) en vez de 2(b+h). M8: pendiente del IM; m = 1.00; LLDF máx. 1.50; factor del Tipo 1; B_FLL de 24 in; eje del tándem; 0.06 → 0.6·D_i; l_w sin s_a; D sin W_F; W_L sobre B_FE; empuje con el diámetro interior; 48E → 40E; interpolación rota.
- **Mutantes míos que SOBREVIVEN y la validación debería matar:**
  - **M8-A**, `W_L = P_L·B_c` sin `min(l_w, B_c)` en `verificar_concreto` (A-2).
  - **M9**, temperatura 5.10.6-1: coeficiente 1.30 → 1.00 y `2(b+h)` → `4(b+h)` (A-3).
  - **M9**, Ec ×0.90 a ×1.04 y Es ×0.95 (M-1).
- Sobreviven por falta de ejemplo (B-1): piso 0.72·h, γEQ = 1, tope de V_n, límite de f_ss, pandeo elástico, `min(f_y, f_c)` del ASD, B_FLL < 2 ft.

Nota de método: mis primeros mutantes por edición de archivo dieron un falso «muere» por bytecode en caché (misma longitud y mismo segundo); los repetí con `PYTHONDONTWRITEBYTECODE=1` y sin `__pycache__`. Los resultados de arriba son los repetidos. El clon quedó limpio (`git status` vacío).

---

## 6. Lo verificado que está bien

- **Transcripción, M9 (más de 60 cifras contra página o celda):** tablas 11.2.2-1, -2 y -3 de Caltrans enteras (fuerzas, brazos, momentos, sumas 194.46 y 465.8, que rehice); V y ΣM de Resistencia Ia (70.68, 600.48) y Ib (53.16, 395.62), que también suman; a, c, d_e, Mn, ε_t, Mcr (78.0 y 86.4), n, β_s, x, I_cr, f_ss, s_max, d_v, V_c, β = 1.57, A_s = 3.0, vuelo del talón 11.125 ft; q del trapecio y del triángulo. De CDOT: todas las entradas (Q20, Q25, Q36, Q52-Q56, AM19-AM22, T316-T325) y las 33 publicadas, con sus fórmulas; las seis combinaciones H188-Z193.
- **Transcripción, M8:** DD 1 Ej. 1 y 4 (P, áreas, IM, w, L_e, W_L); DD 22 Ej. 1 (1811, 2519, 68, 4276, 3421, 2713); CPDM: VAF, Ilustración 4.19 entera, fila de 2.0 ft de la 4.21, Ej. 4-2, 4-5 y 4-7; USACE B-7, B-9 y B-10 en imagen (T, A, f_y, f_u, E, k, r, s, f_c; clases 40/50/65/100/140).
- **Conversión de unidades:** factores exactos de `constantes_fisicas`; no encontré ninguna mal hecha (33 000 psi = 227.53 MPa, D-load lb/ft/ft ↔ N/m/mm, in²/ft ↔ mm²/m).
- **Fila equivocada:** ninguna. Las páginas citadas son las correctas (pág. impresa = pág. del PDF en Caltrans; CPDM impresa 38/52/55/60-73 = PDF 12/26/29/34-47).
- **Recuentos de las fichas** VE3-03 (61 = 53 + 5 + 3) y VE3-04 (42 = 32 + 10; 2 erratas) coinciden con los documentos. Con A-3, VE3-03 pasa a 4 erratas reales.
- La cautela d_v ≤ d de M9 y el uso de e ≤ B/3 con γEQ = 0 (frente a la errata del Manual de Puentes) coinciden con AASHTO.

---

## 7. Correcciones sugeridas, en orden

1. Retirar la errata de temperatura de CDOT y rehacer ese contraste para que vea la ec. 5.10.6-1 (A-3).
2. Añadir a M9 una referencia propia de n y exigir motor = referencia en las filas de método (M-1).
3. En M8: W_L de los DD1 por la ruta real, un caso con l_w < B_c, interpolación a mano y B_fe = 3.93 de CPDM 4-2 como contraste (A-2).
4. Reescribir el resumen de `validacion_conducto.md` y la ficha VE3-04 separando «contrastado con la fuente» (32) de «reproduce su método» (10); cuantificar en §8 cuánto es L_e y cuánto edición, y citar 12.10.2.3 y C12.10.4.3.2c como texto de norma (A-1, M-3).
5. Cerrar O-1 con C5.4.2.4 y la Tabla 3.5.1-1 (M-5); corregir el comentario de kh·4 (M-4).
6. Listar en «lo que no se contrasta» las ramas de B-1.
7. Sigue pendiente, y es lo único que cerraría W_L con un número externo: un ejemplo resuelto de tubo de concreto con AASHTO LRFD 2013 o posterior.
